"""canonicalize.py — THE FROZEN CANONICAL IR FORM.

Nothing round-trips until this file exists, because "did text -> IR -> text come
back the same?" is meaningless without a canonical form to come back to, and
"is ir(alien) == ir(3dom)?" is meaningless without a canonical serialisation to
compare. Every decision below is frozen here, with its one-line rationale, and
is referenced by reports/METRICS_PARITY.md.

The IR objects produced here validate against Phase 1's `ir_schema.json`
(`3dom-grammar/1.1.0`), which is `additionalProperties: false` — so nothing may
be bolted onto an IR object, including a marker for which language produced it.

  C0  grammar_version. Every IR object carries "3dom-grammar/1.1.0", the
      GRAMMAR's version, in both languages. RATIONALE: 3DOM and its alien twin
      are two spellings of ONE grammar; the shared IR is the shared ground truth
      (SCORING_POLICY.md S6) and must be byte-identical, so the lexicon id lives
      in the harness row, never in the IR.

  C1  Number formatting. Leading "+" dropped; a value equal to an integer is
      emitted as an int ("1.50" -> 1.5, "2.0" -> 2, "-0" -> 0); otherwise the
      shortest round-tripping float repr. RATIONALE: one syntactic form per
      numeric VALUE, so IR equality is value equality and not spelling equality.

  C2  Canonical quote character is "'" (single). A body containing "'" is
      emitted with '"' instead; a body containing BOTH raises. RATIONALE: the
      grammar defines sq_char as [^'] with NO escape mechanism (D2/D3), so
      canonicalisation must pick a delimiter, never invent an escape. The
      raise is deliberate: such a string is not in the language, and silently
      mangling it would hide a corpus defect.

  C3  Compound-selector matchers are SORTED, key = (kind_rank, name), with
      kind_rank = type < id < class < pseudo < label < wildcard. RATIONALE:
      matchers inside one compound are ANDed and therefore order-INDEPENDENT;
      leaving them unsorted would make ".wheel.front" and ".front.wheel" — the
      same query — produce different IR, and the isomorphism equality test would
      be wrong rather than strict.

  C4  Operation order is PRESERVED, and so is step order inside a selector.
      RATIONALE: operations are order-DEPENDENT (scale-then-move != move-then-
      scale) and combinators are positional. Sorting either would destroy
      meaning; C3 applies only where semantics is genuinely commutative.

  C5  selector.raw is re-emitted from `steps` in the 3DOM REFERENCE SPELLING,
      never copied from the surface text. RATIONALE: `raw` is required by
      ir_schema.json, so if it held the surface substring the alien IR could
      never equal the 3DOM IR. Rendering it from the canonical steps makes it
      language-neutral AND consistent with C3.

  C6  Canonical JSON: sort_keys=True, separators=(",", ":"), ensure_ascii=False,
      UTF-8. RATIONALE: deterministic bytes are a precondition for hashing.

  C7  Content hash = SHA-256 over the C6 bytes of {grammar_version, ops}, with
      `source` EXCLUDED. RATIONALE: ir_schema.json states scorers MUST NOT read
      `source`; including it in the identity would let the surface string leak
      into an equality test that is supposed to be surface-blind.

  C8  Arguments are named by the per-verb signature table below and emitted
      positionally from it. An operation carrying MORE arguments than its
      signature stores all of them under "_positional" (the escape hatch
      tasks.py's arg_bag already understands). RATIONALE: value TYPING lives in
      the IR builder's per-verb table, not the grammar (D3); this is that table.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

GRAMMAR_VERSION = "3dom-grammar/1.1.0"                                  # C0

VERBS: tuple[str, ...] = (
    "recolor", "scale", "move", "rotate", "delete", "spin", "duplicate",
    "setMaterial", "setOpacity", "setVisible", "wireframe",
    "metalness", "roughness", "castShadow", "receiveShadow",
)
assert len(VERBS) == 15 == len(set(VERBS)), "closed verb set is an INVARIANT"

# C8 — the per-verb argument signature table.
# The first seven rows are copied from Phase 1's tasks.py `_SIGNATURES` and are
# asserted against it at import time; the remaining eight complete the closed
# set of 15 and are new here (Phase 1 never needed them because its scorers only
# read args for those seven task families).
SIGNATURES: dict[str, tuple[str, ...]] = {
    "recolor": ("color",),
    "scale": ("factor", "axis"),
    "move": ("dx", "dy", "dz"),
    "rotate": ("axis", "degrees"),
    "delete": (),
    "spin": ("axis", "turns", "duration"),
    "duplicate": ("dx", "dy", "dz"),
    "setMaterial": ("material",),
    "setOpacity": ("opacity",),
    "setVisible": ("visible",),
    "wireframe": ("enabled",),
    "metalness": ("metalness",),
    "roughness": ("roughness",),
    "castShadow": ("enabled",),
    "receiveShadow": ("enabled",),
}
assert set(SIGNATURES) == set(VERBS), "signature table must cover the closed set"

MATCHER_KIND_RANK: dict[str, int] = {                                   # C3
    "type": 0, "id": 1, "class": 2, "pseudo": 3, "label": 4, "wildcard": 5,
}

# 3DOM reference sigils used to render selector.raw (C5). These are the ONLY
# place a spelling is hard-coded, and they are the 3DOM ones on purpose: `raw`
# is the language-neutral reference rendering.
_REF_SIGIL = {"id": "#", "class": ".", "pseudo": ":"}


class CanonicalisationError(Exception):
    pass


def _check_against_phase1() -> None:
    """Fail loudly if Phase 1's partial signature table has drifted from ours."""
    import os
    import sys
    from phi import phase1_dir
    p1 = phase1_dir()
    if p1 not in sys.path:
        sys.path.insert(0, p1)
    try:
        import tasks                                   # type: ignore
    except Exception:                                  # pragma: no cover
        return                                         # Phase 1 not importable
    theirs = getattr(tasks, "_SIGNATURES", {})
    for verb, sig in theirs.items():
        if verb in SIGNATURES and tuple(sig) != SIGNATURES[verb]:
            raise CanonicalisationError(
                f"signature drift for {verb!r}: tasks.py says {tuple(sig)}, "
                f"canonicalize.py says {SIGNATURES[verb]}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# C1 — numbers
# ─────────────────────────────────────────────────────────────────────────────

def canonical_number(text: str) -> int | float:
    """'+3' -> 3 ; '1.50' -> 1.5 ; '-0' -> 0 ; '2.0' -> 2."""
    body = text[1:] if text[:1] == "+" else text
    value = float(body)
    if value == int(value):
        return int(value) + 0                          # normalises -0 to 0
    return value


def format_number(value: int | float) -> str:
    if isinstance(value, bool):                        # guard: bool is an int
        raise CanonicalisationError("booleans are not 3DOM numbers")
    if isinstance(value, int) or float(value) == int(float(value)):
        return str(int(value) + 0)
    return repr(float(value))


# ─────────────────────────────────────────────────────────────────────────────
# C2 — strings
# ─────────────────────────────────────────────────────────────────────────────

def quote_string(body: str) -> str:
    if "'" not in body:
        return f"'{body}'"
    if '"' not in body:
        return f'"{body}"'
    raise CanonicalisationError(
        f"string {body!r} contains both quote characters; the grammar has no "
        f"escape mechanism (D2), so it is not in the language"
    )


# ─────────────────────────────────────────────────────────────────────────────
# IR node types
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, order=False)
class Matcher:
    kind: str                       # class | id | type | pseudo | wildcard | label
    name: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in MATCHER_KIND_RANK:
            raise CanonicalisationError(f"unknown matcher kind {self.kind!r}")
        if self.kind == "wildcard" and self.name is not None:
            raise CanonicalisationError("wildcard matcher must carry no name")
        if self.kind != "wildcard" and not self.name:
            raise CanonicalisationError(f"{self.kind} matcher requires a name")

    @property
    def sort_key(self) -> tuple[int, str]:                              # C3
        return (MATCHER_KIND_RANK[self.kind], self.name or "")

    def render_reference(self) -> str:                                  # C5
        if self.kind == "wildcard":
            return "*"
        if self.kind == "type":
            return self.name or ""
        return _REF_SIGIL.get(self.kind, "") + (self.name or "")

    def to_json(self) -> dict[str, Any]:
        out: dict[str, Any] = {"kind": self.kind}
        if self.name is not None:
            out["name"] = self.name
        return out


@dataclass(frozen=True)
class Step:
    combinator: str | None          # None | 'descendant' | 'child'
    matchers: tuple[Matcher, ...]

    def __post_init__(self) -> None:
        if self.combinator not in (None, "descendant", "child"):
            raise CanonicalisationError(f"bad combinator {self.combinator!r}")
        if not self.matchers:
            raise CanonicalisationError("a step needs at least one matcher")

    def canonical(self) -> "Step":                                      # C3
        return Step(self.combinator, tuple(sorted(self.matchers,
                                                  key=lambda m: m.sort_key)))

    def to_json(self) -> dict[str, Any]:
        return {"combinator": self.combinator,
                "matchers": [m.to_json() for m in self.matchers]}


@dataclass(frozen=True)
class Selector:
    steps: tuple[Step, ...]

    def canonical(self) -> "Selector":
        return Selector(tuple(s.canonical() for s in self.steps))       # C4 order kept

    @property
    def raw(self) -> str:                                               # C5
        out: list[str] = []
        for step in self.steps:
            if step.combinator == "descendant":
                out.append(" ")
            elif step.combinator == "child":
                out.append(">")
            out.append("".join(m.render_reference() for m in step.matchers))
        return "".join(out)

    def to_json(self) -> dict[str, Any]:
        return {"raw": self.raw, "steps": [s.to_json() for s in self.steps]}


@dataclass(frozen=True)
class Operation:
    op: str
    selector: Selector
    args: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.op not in SIGNATURES:
            raise CanonicalisationError(f"{self.op!r} is not in the closed verb set")

    def canonical(self) -> "Operation":
        return Operation(self.op, self.selector.canonical(), dict(self.args))

    def to_json(self) -> dict[str, Any]:
        out: dict[str, Any] = {"op": self.op, "selector": self.selector.to_json()}
        if self.args:
            out["args"] = dict(self.args)
        return out


@dataclass(frozen=True)
class IRProgram:
    ops: tuple[Operation, ...]
    source: str | None = None
    grammar_version: str = GRAMMAR_VERSION                              # C0

    def canonical(self) -> "IRProgram":
        return IRProgram(tuple(o.canonical() for o in self.ops),        # C4
                         source=self.source,
                         grammar_version=self.grammar_version)

    def to_json(self, *, include_source: bool = False) -> dict[str, Any]:
        out: dict[str, Any] = {"grammar_version": self.grammar_version}
        if include_source and self.source is not None:
            out["source"] = self.source
        out["ops"] = [o.to_json() for o in self.ops]
        return out


# ─────────────────────────────────────────────────────────────────────────────
# C6 / C7 — canonical serialisation and content hash
# ─────────────────────────────────────────────────────────────────────────────

def canonical_json(ir: IRProgram) -> str:                               # C6
    return json.dumps(ir.canonical().to_json(include_source=False),     # C7 excludes source
                      sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_hash(ir: IRProgram) -> str:                                 # C7
    return hashlib.sha256(canonical_json(ir).encode("utf-8")).hexdigest()


def build_args(verb: str, values: Sequence[Any]) -> dict[str, Any]:     # C8
    names = SIGNATURES[verb]
    if len(values) > len(names):
        return {"_positional": list(values)}
    return {name: value for name, value in zip(names, values)}


def args_in_order(verb: str, args: Mapping[str, Any]) -> list[Any]:     # C8, inverse
    if "_positional" in args:
        return list(args["_positional"])
    out: list[Any] = []
    for name in SIGNATURES[verb]:
        if name not in args:
            break
        out.append(args[name])
    if len(out) != len(args):
        raise CanonicalisationError(
            f"args {dict(args)!r} for {verb!r} are not a prefix of its signature "
            f"{SIGNATURES[verb]}; cannot be emitted positionally"
        )
    return out


_check_against_phase1()


if __name__ == "__main__":
    sel = Selector((Step(None, (Matcher("class", "wheel"),
                                Matcher("class", "front"))),))
    ir = IRProgram((Operation("recolor", sel, {"color": "#111111"}),))
    print(canonical_json(ir))
    print("raw       :", ir.canonical().ops[0].selector.raw)
    print("hash      :", content_hash(ir)[:16])
    print("numbers   :", [format_number(canonical_number(t))
                          for t in ("+3", "1.50", "-0", "2.0", "0.5", "-15")])
