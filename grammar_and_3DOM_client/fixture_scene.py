"""fixture_scene.py -- the heuristic 3D fixture scene, and the resolver that turns
a selector IR object into a SET OF SCENE-NODE NAMES.

WHY THIS IS A SEPARATE MODULE
    Of the five task families, selector-resolution is the ONLY one whose ground
    truth lives outside the string (TERMINOLOGY.md S4). op-selection,
    arg-extraction, labeling and multi-op are graded from the IR alone. Keeping
    the scene here makes that asymmetry structural instead of a comment: tasks.py
    imports a resolver, and nothing else in the grader can accidentally reach into
    a scene.

    Nothing here parses 3DOM source. The parser builds an AST; the IR builder
    lowers it; THIS file resolves the lowered selector against geometry. Those
    three jobs never touch.

The dumptruck fixture mirrors SETUP_DUMPTRUCK in docs/editor/js/ai/editEval.js
node-for-node, so the Python matrix and the browser matrix score the same truth.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

GRAMMAR_VERSION = "3dom-grammar/1.1.0"

# Type-selector keywords: 4, INVARIANT (METRICS.md).
TYPE_KEYWORDS = frozenset({"mesh", "group", "light", "camera"})
# Pseudo-selectors: 2, INVARIANT.
PSEUDO_KEYWORDS = frozenset({"selected", "lasso"})


# -- SCENE NODES ---------------------------------------------------------------

@dataclass(frozen=True)
class SceneNode:
    """One node in the SCENE GRAPH (semantics) -- never an AST node (syntax).

    `name` is the stable identity the RCN truth sets are written against
    ('Object_20'), `label` is the human name Stage-4 labeling produced, and
    `classes` is what classDerive() harvested from material names and geometric
    descriptors. Frozen because a scorer must not be able to mutate the fixture
    mid-run: a scene that drifts between cases produces confident-but-wrong rows.
    """

    name: str
    label: str
    node_type: str = "mesh"
    classes: frozenset[str] = frozenset()
    parent: str | None = None
    separable: bool = True

    @property
    def ident(self) -> str:
        """The '#id' handle: the node name, case-folded."""
        return self.name.lower()


@dataclass
class FixtureScene:
    """A scene graph plus the two pieces of editor state pseudo-selectors read."""

    nodes: dict[str, SceneNode]
    selected: frozenset[str] = frozenset()
    lassoed: frozenset[str] = frozenset()
    _children: dict[str | None, list[str]] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        # Build the parent -> children index once. Resolution walks it per step,
        # so paying for it here keeps the resolver linear in scene size.
        for name, node in self.nodes.items():
            self._children.setdefault(node.parent, []).append(name)

    # -- graph walks -----------------------------------------------------------

    def children_of(self, name: str) -> list[str]:
        """One level down the SPATIAL tree. This is what the `>` terminal MEANS."""
        return list(self._children.get(name, ()))

    def descendants_of(self, name: str) -> list[str]:
        out: list[str] = []
        stack = self.children_of(name)
        while stack:
            current = stack.pop()
            out.append(current)
            stack.extend(self.children_of(current))
        return out

    def roots(self) -> list[str]:
        return list(self._children.get(None, ()))


# -- SELECTOR PARSING ----------------------------------------------------------
# A model very often emits `selector: {"raw": ".wheel"}` with no `steps`, or even
# a bare string. The resolver must not care: it re-parses `raw` and grades the
# same selector either way. Refusing to resolve a structurally-valid selector
# because the builder omitted an optional field would score the BUILDER, not the
# model -- exactly the false-negative class SCORING_POLICY.md S1 warns about.

_SELECTOR_TOKEN = re.compile(
    r"""
      (?P<child>\s*>\s*)               # child combinator -- a LEAF terminal
    | (?P<descendant>\s+)              # significant whitespace
    | (?P<klass>\.[A-Za-z0-9_-]+)      # .class
    | (?P<ident>\#[A-Za-z0-9_-]+)      # #id
    | (?P<pseudo>:[A-Za-z0-9_-]+)      # :selected / :lasso
    | (?P<wildcard>\*)                 # universal
    | (?P<word>[A-Za-z][A-Za-z0-9_-]*) # bare word -> type keyword, else label
    """,
    re.VERBOSE,
)


def parse_selector(raw: str) -> list[dict[str, Any]]:
    """'.car > .wheel' -> [{combinator, matchers}, ...]  (the schema's `steps`)."""
    steps: list[dict[str, Any]] = []
    pending_combinator: str | None = None

    for token in _SELECTOR_TOKEN.finditer(raw or ""):
        kind = token.lastgroup
        text = token.group()

        if kind == "child":
            pending_combinator = "child"
            continue
        if kind == "descendant":
            # Whitespace only separates steps if a step already exists; leading
            # and trailing space is noise, not a descendant combinator.
            if steps:
                pending_combinator = "descendant"
            continue

        if kind == "klass":
            matcher = {"kind": "class", "name": text[1:]}
        elif kind == "ident":
            matcher = {"kind": "id", "name": text[1:]}
        elif kind == "pseudo":
            matcher = {"kind": "pseudo", "name": text[1:]}
        elif kind == "wildcard":
            matcher = {"kind": "wildcard"}
        else:
            lowered = text.lower()
            matcher = (
                {"kind": "type", "name": lowered}
                if lowered in TYPE_KEYWORDS
                else {"kind": "label", "name": text}
            )

        if pending_combinator is not None or not steps:
            steps.append({"combinator": pending_combinator, "matchers": [matcher]})
            pending_combinator = None
        else:
            # No combinator since the last matcher => COMPOUND step: '.front.wheel'
            # is one step with two ANDed matchers, not two steps.
            steps[-1]["matchers"].append(matcher)

    return steps


def selector_steps(selector: Any) -> list[dict[str, Any]]:
    """Coerce whatever landed in `op["selector"]` into a list of steps.

    Accepts the schema object, a bare raw string, or a malformed near-miss.
    Returns [] for anything unusable -- an unresolvable selector resolves to no
    nodes, which fails RCN honestly rather than raising.
    """
    if isinstance(selector, str):
        return parse_selector(selector)
    if not isinstance(selector, Mapping):
        return []

    steps = selector.get("steps")
    if isinstance(steps, list) and steps:
        return [s for s in steps if isinstance(s, Mapping) and s.get("matchers")]
    return parse_selector(str(selector.get("raw") or ""))


# -- RESOLUTION ----------------------------------------------------------------

def _matches(scene: FixtureScene, node: SceneNode, matcher: Mapping[str, Any]) -> bool:
    kind = str(matcher.get("kind") or "").lower()
    name = str(matcher.get("name") or "")

    if kind == "wildcard":
        return True
    if kind == "class":
        return name.lower() in node.classes
    if kind == "id":
        return node.ident == name.lower()
    if kind == "type":
        return node.node_type == name.lower()
    if kind == "pseudo":
        pseudo = name.lower()
        if pseudo == "selected":
            return node.name in scene.selected
        if pseudo == "lasso":
            return node.name in scene.lassoed
        return False
    if kind == "label":
        return _slug(node.label) == _slug(name)
    return False


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")


def _step_matches(scene: FixtureScene, name: str, matchers: Iterable[Mapping[str, Any]]) -> bool:
    node = scene.nodes[name]
    return all(_matches(scene, node, m) for m in matchers)


def resolve(selector: Any, scene: FixtureScene) -> frozenset[str]:
    """Selector IR + scene -> the SET OF SCENE-NODE NAMES it hits.

    This is the 1:N fan-out: ONE selector_call resolves to N scene nodes
    (TERMINOLOGY.md S2). The return type is a set on purpose -- order is not part
    of the truth, membership is.
    """
    steps = selector_steps(selector)
    if not steps:
        return frozenset()

    # Step 0 is unanchored: it searches the whole scene.
    current = {n for n in scene.nodes if _step_matches(scene, n, steps[0]["matchers"])}

    for step in steps[1:]:
        if not current:
            break
        combinator = step.get("combinator") or "descendant"
        reachable: set[str] = set()
        for anchor in current:
            candidates = (
                scene.children_of(anchor)
                if combinator == "child"
                else scene.descendants_of(anchor)
            )
            reachable.update(candidates)
        current = {n for n in reachable if _step_matches(scene, n, step["matchers"])}

    return frozenset(current)


def resolve_all(ops: Sequence[Mapping[str, Any]], scene: FixtureScene) -> list[frozenset[str]]:
    """One resolved set per emitted op, positionally aligned with `ops`."""
    return [resolve(op.get("selector") if isinstance(op, Mapping) else None, scene) for op in ops]


# -- THE FIXTURES --------------------------------------------------------------
# Node-for-node mirrors of SETUP_DUMPTRUCK / SETUP_MERGED_BED in editEval.js.
# The classes are what classDerive() produces on the real asset: material names
# (Rims -> .rims, Grille -> .grille) and geometric descriptors (.front, .left).

def _truck_part(name: str, label: str, classes: Sequence[str]) -> SceneNode:
    return SceneNode(name=name, label=label, node_type="mesh",
                     classes=frozenset(classes), parent="DumpTruck")


def dumptruck_scene() -> FixtureScene:
    nodes = [
        SceneNode("DumpTruck", "DumpTruck", "group", frozenset({"truck", "vehicle"}), None),
        _truck_part("Object_03", "Cab", ["cab", "grille", "front", "top"]),
        _truck_part("Object_07", "Dump Bed", ["bed", "dump-bed", "center", "largest"]),
        _truck_part("Object_12", "Tail Light (left)", ["tail-light", "light", "back", "left", "pair-left"]),
        _truck_part("Object_13", "Tail Light (right)", ["tail-light", "light", "back", "right", "pair-right"]),
        _truck_part("Object_20", "Front Left Wheel", ["wheel", "rims", "front", "left", "pair-left"]),
        _truck_part("Object_21", "Front Right Wheel", ["wheel", "rims", "front", "right", "pair-right"]),
        _truck_part("Object_22", "Rear Left Wheel", ["wheel", "rims", "back", "left", "pair-left"]),
        _truck_part("Object_23", "Rear Right Wheel", ["wheel", "rims", "back", "right", "pair-right"]),
    ]
    return FixtureScene(nodes={n.name: n for n in nodes})


def merged_bed_scene() -> FixtureScene:
    """The graceful-fail fixture: ONE unsplittable mesh with no addressable parts.

    A part selector ('.sheets') must resolve to NOTHING here. A resolver that
    falls back to the whole merged mesh turns 'recolour the sheets' into
    'recolour the entire bed' -- the co-location false-pass the eval gate exists
    to catch.
    """
    node = SceneNode("GothicBed", "Gothic Bed", "mesh",
                     frozenset({"bed", "furniture"}), None, separable=False)
    return FixtureScene(nodes={node.name: node})


ASSET_SCENES = {
    "dumptruck": dumptruck_scene,
    "merged-bed": merged_bed_scene,
}


def scene_for(asset: str) -> FixtureScene:
    """Build a FRESH scene per case. Never share one: a mutated fixture silently
    changes the ground truth of every case after it."""
    try:
        return ASSET_SCENES[asset]()
    except KeyError:
        raise KeyError(f"unknown fixture asset {asset!r}; have {sorted(ASSET_SCENES)}") from None
