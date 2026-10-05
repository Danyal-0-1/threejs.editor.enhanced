"""templates.py — varied-opening AST templates, built as IR and rendered.

----------------------------------------------------------------------------
THE PROBLEM THIS SOLVES
----------------------------------------------------------------------------
Phase 3 measured that 61% of its semantic sites were unusable for a
prefix-conditioned predictor: 3 prefix groups held 63 of 103 sites, leaving
only 40 prefix-distinct sites. The cause is structural, not accidental --
every Phase 1 program opens with the same 17 characters:

    (function(){ $S('
                     ^ the first class sigil lands here, every single time

A site's prefix is everything before it, so the FIRST site of every program
has a byte-identical prefix. No model can tell those sites apart, and they are
not independent observations.

----------------------------------------------------------------------------
HOW VARIATION IS CREATED
----------------------------------------------------------------------------
Three mechanisms, in rough order of how much prefix diversity they buy:

1. MULTIPLE STATEMENTS. The second and third statements sit behind everything
   the first emitted, so their sites have long, highly distinctive prefixes.
2. RICHER SELECTORS. `.a > .b c` puts several sigils in one selector; each one
   after the first has a different prefix.
3. VERB AND ARGUMENT VARIETY. Changes the text between sites, so downstream
   prefixes diverge.

What this CANNOT fix: the very first site of a single-statement program in a
given family always has the same prefix. That is a property of the grammar's
opening, not of the corpus. The `blk` family has a different opening
(`$S '`), which is one more reason a second family matters.

----------------------------------------------------------------------------
BUILT AS IR, NOT AS TEXT
----------------------------------------------------------------------------
Templates are constructed as `IRProgram` objects and then RENDERED by a
backend. Three consequences, all of them the point:

  * validity by construction -- there is no hand-written text to typo, and a
    template that cannot be rendered fails loudly at build time;
  * the SAME template set is expressible in both grammar families, so a
    cross-family comparison holds the abstract program fixed and varies only
    the concrete syntax -- which is the whole claim;
  * the target IR is known exactly, so Arm B scoring needs no oracle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Sequence

from phase3_2 import _vendor  # noqa: F401

import canonicalize as C  # noqa: E402

# ---------------------------------------------------------------------------
# selector shapes — deliberately spanning every production in the inner grammar
# ---------------------------------------------------------------------------
# Names are descriptive so a failing site can be traced to the shape that
# produced it. The pool is ordered from shallow to deep; deeper shapes put more
# sigils behind more text, which is where prefix diversity comes from.

NAMES = ("wheel", "door", "bus", "roof", "lamp", "axle", "hood", "seat",
         "panel", "frame", "glass", "tyre")


def _m(kind: str, name: str | None = None) -> C.Matcher:
    return C.Matcher(kind, name)


def _sel(*steps: C.Step) -> C.Selector:
    return C.Selector(tuple(steps))


def selector_shapes() -> list[tuple[str, C.Selector]]:
    """A spread of selector shapes, each exercising different inner productions."""
    n = NAMES
    out: list[tuple[str, C.Selector]] = [
        ("class", _sel(C.Step(None, (_m("class", n[0]),)))),
        ("id", _sel(C.Step(None, (_m("id", n[1]),)))),
        ("type", _sel(C.Step(None, (_m("type", "mesh"),)))),
        ("wildcard", _sel(C.Step(None, (_m("wildcard"),)))),
        ("pseudo", _sel(C.Step(None, (_m("pseudo", "selected"),)))),
        # compound: several matchers in ONE step (no combinator between them)
        ("compound_tc", _sel(C.Step(None, (_m("type", "group"), _m("class", n[2]))))),
        ("compound_ci", _sel(C.Step(None, (_m("class", n[3]), _m("id", n[4]))))),
        # descendant / child combinators: two steps
        ("descendant", _sel(C.Step(None, (_m("class", n[2]),)),
                            C.Step("descendant", (_m("class", n[1]),)))),
        ("child", _sel(C.Step(None, (_m("class", n[2]),)),
                       C.Step("child", (_m("class", n[1]),)))),
        ("id_child_class", _sel(C.Step(None, (_m("id", n[5]),)),
                                C.Step("child", (_m("class", n[6]),)))),
        # three steps: the deepest shapes, richest prefixes
        ("deep_desc", _sel(C.Step(None, (_m("class", n[2]),)),
                           C.Step("descendant", (_m("type", "group"),)),
                           C.Step("descendant", (_m("class", n[7]),)))),
        ("deep_child", _sel(C.Step(None, (_m("id", n[8]),)),
                            C.Step("child", (_m("class", n[9]),)),
                            C.Step("child", (_m("type", "mesh"),)))),
        ("mixed", _sel(C.Step(None, (_m("type", "light"),)),
                       C.Step("descendant", (_m("class", n[10]),)),
                       C.Step("child", (_m("id", n[11]),)))),
        # --- second tier: more openings, different leading matcher kinds ----
        ("type_camera", _sel(C.Step(None, (_m("type", "camera"),)))),
        ("pseudo_lasso", _sel(C.Step(None, (_m("pseudo", "lasso"),)))),
        ("wild_child", _sel(C.Step(None, (_m("wildcard"),)),
                            C.Step("child", (_m("class", n[0]),)))),
        ("type_desc_id", _sel(C.Step(None, (_m("type", "mesh"),)),
                              C.Step("descendant", (_m("id", n[3]),)))),
        ("compound3", _sel(C.Step(None, (_m("type", "mesh"), _m("class", n[5]),
                                         _m("id", n[7]))))),
        ("id_desc_wild", _sel(C.Step(None, (_m("id", n[9]),)),
                              C.Step("descendant", (_m("wildcard"),)))),
        ("class_child_compound", _sel(C.Step(None, (_m("class", n[4]),)),
                                      C.Step("child", (_m("type", "group"),
                                                       _m("class", n[8]))))),
    ]
    return out


# ---------------------------------------------------------------------------
# operations — one well-typed argument tuple per verb
# ---------------------------------------------------------------------------
# Values are chosen to be type-appropriate for the C8 signature so a rendered
# program is not merely parseable but sensible. `build_args` maps positionally.

VERB_VALUES: dict[str, list] = {
    "recolor": ["#111111"],
    "scale": [2, "x"],
    "move": [1, 2, 3],
    "rotate": ["y", 90],
    "delete": [],
    "spin": ["y", 2, 4],
    "duplicate": [1, 0, 0],
    "setMaterial": ["matte"],
    "setOpacity": [0.5],
    "setVisible": [1],
    "wireframe": [1],
    "metalness": [0.8],
    "roughness": [0.3],
    "castShadow": [1],
    "receiveShadow": [0],
}

VERBS = tuple(VERB_VALUES)


@dataclass(frozen=True)
class Template:
    template_id: str
    shape: str              # selector-shape name(s) used
    n_statements: int
    ir: C.IRProgram

    @property
    def n_ops(self) -> int:
        return len(self.ir.ops)


def build_templates(*, max_statements: int = 4,
                    target: int = 96) -> list[Template]:
    """Deterministically enumerate templates, shallow first.

    Deterministic, not random: the same call always yields the same list in the
    same order, so a template id in a result file always means the same
    program. Randomising here would make a run un-reproducible without also
    serialising the corpus.
    """
    shapes = selector_shapes()
    out: list[Template] = []
    vi = 0

    for n_stmt in range(1, max_statements + 1):
        for si, (sname, sel) in enumerate(shapes):
            # rotate a second/third selector in so multi-statement programs do
            # not simply repeat one selector
            sels = [shapes[(si + k) % len(shapes)] for k in range(n_stmt)]
            ops: list[C.Operation] = []
            names: list[str] = []
            for (nm, s) in sels:
                verb = VERBS[vi % len(VERBS)]
                vi += 1
                ops.append(C.Operation(verb, s, C.build_args(verb, VERB_VALUES[verb])))
                names.append(nm)
            out.append(Template(
                template_id=f"t{len(out):03d}",
                shape="+".join(names),
                n_statements=n_stmt,
                ir=C.IRProgram(tuple(ops)).canonical()))
            if len(out) >= target:
                return out
    return out


def render(templates: Sequence[Template], backend, phi) -> list[tuple[Template, str]]:
    """(template, concrete text) pairs for one family and one lexicon."""
    return [(t, backend.render(t.ir, phi)) for t in templates]


def opening_diversity(texts: Sequence[str], k: int = 17) -> dict[str, int]:
    """How many DISTINCT first-k-character openings the corpus has.

    k defaults to 17, the offset of the FIRST class sigil in a `dom` program
    (`(function(){ $S('` is exactly 17 characters). That is the number that
    matters, and choosing k carelessly hides the problem: measured at k=24 the
    Phase 1 corpus looks diverse (33 distinct openings) because 24 characters
    reach into the selector NAME, which varies. But the first site sits at
    offset 17, so its prefix is the same for every program regardless.

    This is a WEAK proxy, kept only because it is model-free and instant. The
    real measurement is `sites2.prefix_collisions` /
    `sites2.dedupe_by_prefix`, which compare the actual site prefixes rather
    than a fixed-width window. Trust those; use this to sanity-check a corpus
    before classifying it.
    """
    counts: dict[str, int] = {}
    for t in texts:
        counts[t[:k]] = counts.get(t[:k], 0) + 1
    return counts
