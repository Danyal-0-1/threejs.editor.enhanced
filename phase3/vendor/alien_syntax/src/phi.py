"""phi.py — load, VALIDATE, apply and INVERT a φ-map.

A φ-map is the ONLY thing that differs between 3DOM and an alien language. The
non-terminal set N and the shape of P are frozen (I1–I4); φ renames terminal
SPELLINGS, keyed on the stable terminal IDs in Phase 1's `terminals.json`.

This module is deliberately dependency-free (no lark, no transformers) so that
validation runs anywhere, including in CI on a machine with no models.

FAIL LOUDLY is the contract. Every check below raises `PhiValidationError`.
Nothing here warns.

The validator enforces, mechanically:

  V1  the map targets the frozen grammar version
  V2  every substitutable terminal appears exactly once; no extras
  V3  no non-substitutable terminal is substituted        (I8 quotes, I9 T_WS)
  V4  each entry's `from` matches terminals.json byte-for-byte
  V5  overload_groups receive one identical spelling      (I7)
  V6  φ preserves the SPELLING PARTITION of the terminal set — i.e. two IDs
      share an alien spelling iff they share a 3DOM spelling. This is the
      precise sense in which φ is a bijection (I7 + I10) and is what makes
      φ⁻¹ derivable rather than hand-maintained.
  V7  the declared `frozen` list covers every non-substitutable ID, and names
      T_WS explicitly (I9) and both quote terminals (I8)
  V8  lexability: no alien spelling may start with a character that the
      two-level lexer already claims (quote, structural delimiter, numeric
      sign, digit) — otherwise the alien lexer is not well-defined and the
      "same lookahead k" claim (I6) is meaningless.

On `terminals.json`'s collision note
------------------------------------
The Phase 1 collisions block says T_CHAIN_OP and T_CLASS_SIGIL "get INDEPENDENT
alien spellings". The hazard it describes is a φ-map keyed on the CHARACTER "."
renaming one role and silently breaking the other. This module removes that
hazard by keying on the terminal ID: the two roles carry two INDEPENDENT map
ENTRIES. Invariant I7 additionally requires those two entries to carry the SAME
VALUE, because de-overloading "." would make the alien language strictly easier
to lex than 3DOM — an unmatched complexity change. If the stronger reading of
the Phase 1 note is intended instead (two DIFFERENT spellings), set
`overload_groups: []` in the φ-map and V5/V6 relax accordingly; that is the
whole cost of the change.
"""

from __future__ import annotations

import functools
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

GRAMMAR_VERSION = "3dom-grammar/1.1.0"

# Characters the two-level lexer claims before it ever consults φ (V8).
RESERVED_LEAD_CHARS = frozenset("'\"(){};,+-0123456789 \t\r\n")

# The identifier character class. FROZEN: identifier VALUES are copied verbatim
# into the shared IR, so they cannot be renamed (terminals.json, T_IDENT).
IDENT_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
)


class PhiValidationError(Exception):
    """Raised on ANY φ-map defect. There is no warning path."""


# ─────────────────────────────────────────────────────────────────────────────
# Phase 1 artifacts
# ─────────────────────────────────────────────────────────────────────────────

def phase1_dir() -> str:
    """Locate the Phase 1 artifact directory (overridable with $PHASE1_DIR)."""
    env = os.environ.get("PHASE1_DIR")
    if env:
        return os.path.abspath(env)
    here = os.path.dirname(os.path.abspath(__file__))          # …/alien_syntax/src
    repo = os.path.dirname(os.path.dirname(here))              # …/<repo root>
    return os.path.join(repo, "grammar_and_3DOM_client")


def alien_dir() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass(frozen=True)
class Terminal:
    id: str
    spelling: str
    role: str
    productions: tuple[str, ...]
    substitutable: bool
    note: str

    @property
    def is_word_class(self) -> bool:
        """True iff the spelling is drawn entirely from the identifier charset.

        This is the lexical class that forces the lexer to do maximal munch and
        then a keyword-membership test. Preserving it is what keeps the alien
        lexer exactly as hard as 3DOM's (see measure/collisions.py check (g)).
        """
        return bool(self.spelling) and all(c in IDENT_CHARS for c in self.spelling)


@dataclass(frozen=True)
class TerminalTable:
    grammar_version: str
    terminals: tuple[Terminal, ...]

    @functools.cached_property
    def by_id(self) -> dict[str, Terminal]:
        """id -> Terminal, built once.

        This was a plain @property, which rebuilt a 43-entry dict on EVERY
        lookup — and `PhiMap.spelling` calls it once per terminal, inside the
        lexer's hot path and inside every collision check's cross product. The
        table is frozen for the life of the process, so the rebuild bought
        nothing. `cached_property` writes through `instance.__dict__` directly,
        which is why it works on a frozen dataclass: it never calls the blocked
        `__setattr__`.
        """
        return {t.id: t for t in self.terminals}

    @property
    def substitutable_ids(self) -> tuple[str, ...]:
        return tuple(t.id for t in self.terminals if t.substitutable)

    @property
    def non_substitutable_ids(self) -> tuple[str, ...]:
        return tuple(t.id for t in self.terminals if not t.substitutable)

    def spelling_partition(self) -> frozenset[frozenset[str]]:
        """{ {ids sharing a 3DOM spelling}, … } over SUBSTITUTABLE terminals.

        For 3DOM this is 28 singletons plus {T_CHAIN_OP, T_CLASS_SIGIL}.
        """
        groups: dict[str, set[str]] = {}
        for t in self.terminals:
            if t.substitutable:
                groups.setdefault(t.spelling, set()).add(t.id)
        return frozenset(frozenset(v) for v in groups.values())

    def terminals_of_production(self, production: str) -> tuple[Terminal, ...]:
        return tuple(t for t in self.terminals if production in t.productions)


def load_terminals(path: str | None = None) -> TerminalTable:
    path = path or os.path.join(phase1_dir(), "terminals.json")
    with open(path, encoding="utf-8") as fh:
        blob = json.load(fh)
    version = blob["grammar_version"]
    if version != GRAMMAR_VERSION:
        raise PhiValidationError(
            f"terminals.json targets {version!r}, this phase is pinned to "
            f"{GRAMMAR_VERSION!r}"
        )
    terms = tuple(
        Terminal(
            id=t["id"],
            spelling=t["spelling"],
            role=t["role"],
            productions=tuple(t["productions"]),
            substitutable=bool(t["substitutable"]),
            note=t.get("note", ""),
        )
        for t in blob["terminals"]
    )
    return TerminalTable(grammar_version=version, terminals=terms)


# ─────────────────────────────────────────────────────────────────────────────
# The φ-map
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PhiMap:
    phi_id: str
    targets_grammar: str
    generated: str
    notes: str
    substitutions: dict[str, str]                 # terminal id -> alien spelling
    declared_from: dict[str, str]                 # terminal id -> declared 3DOM spelling
    overload_groups: tuple[frozenset[str], ...]
    frozen: frozenset[str]
    table: TerminalTable

    # ── application ─────────────────────────────────────────────────────────
    def spelling(self, terminal_id: str) -> str:
        """φ(terminal_id) — the spelling this language uses for that role."""
        if terminal_id in self.substitutions:
            return self.substitutions[terminal_id]
        term = self.table.by_id.get(terminal_id)
        if term is None:
            raise PhiValidationError(f"unknown terminal id {terminal_id!r}")
        return term.spelling                       # frozen: identity

    def source_spelling(self, terminal_id: str) -> str:
        """φ⁻¹ at the ID level: the 3DOM spelling for that role."""
        term = self.table.by_id.get(terminal_id)
        if term is None:
            raise PhiValidationError(f"unknown terminal id {terminal_id!r}")
        return term.spelling

    def is_identity(self) -> bool:
        return all(self.spelling(i) == self.source_spelling(i)
                   for i in self.table.by_id)

    # ── inversion ───────────────────────────────────────────────────────────
    def invert(self) -> dict[str, frozenset[str]]:
        """φ⁻¹ as DERIVED data: alien spelling -> the ID set it denotes.

        Never hand-maintained. V6 guarantees this is well defined and that its
        partition is identical to 3DOM's, so inverting an alien token stream is
        exactly as context-dependent as lexing a 3DOM one — no more, no less.
        """
        out: dict[str, set[str]] = {}
        for tid in self.table.by_id:
            out.setdefault(self.spelling(tid), set()).add(tid)
        return {k: frozenset(v) for k, v in out.items()}

    def inverse_map(self) -> "PhiMap":
        """The φ-map that carries this language back to 3DOM."""
        return PhiMap(
            phi_id=f"{self.phi_id}^-1",
            targets_grammar=self.targets_grammar,
            generated=self.generated,
            notes=f"derived inverse of {self.phi_id}",
            substitutions={t: self.source_spelling(t) for t in self.substitutions},
            declared_from={t: self.spelling(t) for t in self.substitutions},
            overload_groups=self.overload_groups,
            frozen=self.frozen,
            table=self.table,
        )

    # ── convenience views used by the lexer / renderer ──────────────────────
    def verbs(self) -> dict[str, str]:
        """alien verb spelling -> canonical 3DOM verb (the IR's op name)."""
        return {
            self.spelling(t.id): t.spelling
            for t in self.table.terminals
            if t.role == "operation verb"
        }

    def types(self) -> dict[str, str]:
        return {
            self.spelling(t.id): t.spelling
            for t in self.table.terminals
            if t.role == "type selector keyword"
        }

    def pseudos(self) -> dict[str, str]:
        return {
            self.spelling(t.id): t.spelling
            for t in self.table.terminals
            if t.role == "pseudo-selector keyword"
        }


def _as_group_sets(groups: Iterable[Sequence[str]]) -> tuple[frozenset[str], ...]:
    return tuple(frozenset(g) for g in groups)


def validate_phi(blob: Mapping[str, Any], table: TerminalTable) -> PhiMap:
    """Validate a raw φ-map dict against terminals.json. Raises on any defect."""
    errors: list[str] = []
    phi_id = str(blob.get("phi_id", "<unnamed>"))

    def bad(code: str, msg: str) -> None:
        errors.append(f"[{code}] {msg}")

    # V1 — version pin
    targets = blob.get("targets_grammar")
    if targets != GRAMMAR_VERSION:
        bad("V1", f"targets_grammar={targets!r}, expected {GRAMMAR_VERSION!r}")

    raw_map = blob.get("map")
    if not isinstance(raw_map, dict):
        raise PhiValidationError(f"φ-map {phi_id!r}: 'map' must be an object")

    by_id = table.by_id
    substitutable = set(table.substitutable_ids)
    non_sub = set(table.non_substitutable_ids)

    subs: dict[str, str] = {}
    froms: dict[str, str] = {}
    for tid, entry in raw_map.items():
        if tid not in by_id:
            bad("V2", f"{tid!r} is not a terminal id in terminals.json")
            continue
        if not isinstance(entry, dict) or "from" not in entry or "to" not in entry:
            bad("V2", f"{tid!r} entry must be an object with 'from' and 'to'")
            continue
        # V3 — frozen terminals must not be substituted at all (I8, I9)
        if tid in non_sub:
            bad("V3", f"{tid!r} is substitutable:false in terminals.json "
                      f"(role: {by_id[tid].role}) and MUST NOT be substituted")
            continue
        # V4 — the declared source spelling must match Phase 1 byte-for-byte
        if entry["from"] != by_id[tid].spelling:
            bad("V4", f"{tid!r} declares from={entry['from']!r} but "
                      f"terminals.json says {by_id[tid].spelling!r}")
        subs[tid] = str(entry["to"])
        froms[tid] = str(entry["from"])

    # V2 — exact cover of the substitutable set
    missing = sorted(substitutable - set(subs))
    if missing:
        bad("V2", f"{len(missing)} substitutable terminal(s) absent from the map: "
                  f"{', '.join(missing)}")

    # V5 — overload groups share one spelling (I7)
    groups = _as_group_sets(blob.get("overload_groups", []))
    for group in groups:
        unknown = sorted(g for g in group if g not in by_id)
        if unknown:
            bad("V5", f"overload group names unknown id(s): {', '.join(unknown)}")
            continue
        spellings = {subs.get(g) for g in group}
        if len(spellings) != 1 or None in spellings:
            bad("V5", f"overload group {sorted(group)} must receive ONE identical "
                      f"spelling (I7); got {sorted(str(s) for s in spellings)}")

    # V6 — φ preserves the spelling partition (bijectivity, I7 + I10)
    if not missing:
        alien_partition: dict[str, set[str]] = {}
        for tid, spell in subs.items():
            alien_partition.setdefault(spell, set()).add(tid)
        alien = frozenset(frozenset(v) for v in alien_partition.values())
        source = table.spelling_partition()
        if alien != source:
            only_alien = sorted(tuple(sorted(g)) for g in (alien - source))
            only_src = sorted(tuple(sorted(g)) for g in (source - alien))
            bad("V6", "φ does not preserve the spelling partition — it is not a "
                      "bijection modulo overloads. "
                      f"groups only in alien: {only_alien}; "
                      f"groups only in 3DOM: {only_src}")

    # V7 — the frozen declaration must be honest and complete (I8, I9)
    declared_frozen = frozenset(blob.get("frozen", []))
    unknown_frozen = sorted(f for f in declared_frozen if f not in by_id)
    if unknown_frozen:
        bad("V7", f"frozen names unknown id(s): {', '.join(unknown_frozen)}")
    frozen_missing = sorted(non_sub - declared_frozen)
    if frozen_missing:
        bad("V7", f"frozen must list every substitutable:false terminal; "
                  f"absent: {', '.join(frozen_missing)}")
    if "T_WS" not in declared_frozen:
        bad("V7/I9", "T_WS (the descendant combinator) must be declared frozen — "
                     "replacing significant whitespace with a visible glyph would "
                     "delete the two-level parsing requirement")
    for qid in ("T_QUOTE_S", "T_QUOTE_D"):
        if qid not in declared_frozen:
            bad("V7/I8", f"{qid} must be declared frozen — symmetric string "
                         f"delimiters carry the quote-agreement constraint (D2)")

    # V8 — the alien spellings must be lexable
    for tid, spell in sorted(subs.items()):
        if not spell:
            bad("V8", f"{tid!r} maps to the empty string")
            continue
        if spell[0] in RESERVED_LEAD_CHARS:
            bad("V8", f"{tid!r} maps to {spell!r}, which starts with the reserved "
                      f"lexer character {spell[0]!r} (quote / delimiter / sign / "
                      f"digit / layout)")
        if any(c in RESERVED_LEAD_CHARS for c in spell[1:]):
            offending = sorted({c for c in spell[1:] if c in RESERVED_LEAD_CHARS})
            bad("V8", f"{tid!r} maps to {spell!r}, which contains reserved lexer "
                      f"character(s) {offending}")

    if errors:
        raise PhiValidationError(
            f"φ-map {phi_id!r} is invalid ({len(errors)} defect(s)):\n  "
            + "\n  ".join(errors)
        )

    return PhiMap(
        phi_id=phi_id,
        targets_grammar=str(targets),
        generated=str(blob.get("generated", "")),
        notes=str(blob.get("notes", "")),
        substitutions=subs,
        declared_from=froms,
        overload_groups=groups,
        frozen=declared_frozen,
        table=table,
    )


def load_phi(path: str, table: TerminalTable | None = None) -> PhiMap:
    table = table or load_terminals()
    with open(path, encoding="utf-8") as fh:
        blob = json.load(fh)
    return validate_phi(blob, table)


def identity_phi(table: TerminalTable | None = None) -> PhiMap:
    """3DOM itself, expressed as the φ = id instance of the alien machinery.

    Everything downstream (lexer, parser, IR builder, emitter, corpus generator)
    is parameterised by a φ-map; 3DOM is simply the identity member of that
    family. That is what makes `ir(parse_alien(φ(x))) == ir(parse_3dom(x))` a
    statement about one code path rather than two.
    """
    table = table or load_terminals()
    blob = {
        "phi_id": "identity",
        "targets_grammar": GRAMMAR_VERSION,
        "generated": "",
        "map": {
            t.id: {"from": t.spelling, "to": t.spelling}
            for t in table.terminals if t.substitutable
        },
        "overload_groups": [["T_CHAIN_OP", "T_CLASS_SIGIL"]],
        "frozen": list(table.non_substitutable_ids),
        "notes": "3DOM as the identity member of the φ family.",
    }
    return validate_phi(blob, table)


SLOT_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def render_slots(text: str, phi: PhiMap) -> str:
    """template + φ -> concrete artifact.

    A slot is `{{T_TERMINAL_ID}}`. Every slot must name a SUBSTITUTABLE terminal
    (a slot for a frozen terminal would mean the template lets φ touch something
    I8/I9 forbid), and every substitutable terminal must appear in at least one
    slot of the grammar templates — that second check lives in render_grammar.py,
    which knows which templates are grammars.
    """
    unknown: set[str] = set()
    frozen_slots: set[str] = set()

    def sub(match: "re.Match[str]") -> str:
        tid = match.group(1)
        term = phi.table.by_id.get(tid)
        if term is None:
            unknown.add(tid)
            return match.group(0)
        if not term.substitutable:
            frozen_slots.add(tid)
            return match.group(0)
        return phi.spelling(tid)

    out = SLOT_RE.sub(sub, text)
    problems: list[str] = []
    if unknown:
        problems.append(f"template names unknown terminal id(s): "
                        f"{', '.join(sorted(unknown))}")
    if frozen_slots:
        problems.append(f"template opens a slot for substitutable:false "
                        f"terminal(s) {', '.join(sorted(frozen_slots))} — a frozen "
                        f"terminal must be written literally, never rendered (I8/I9)")
    if problems:
        raise PhiValidationError("; ".join(problems))
    return out


def slots_in(text: str) -> set[str]:
    return set(SLOT_RE.findall(text))


def candidates_dir() -> str:
    return os.path.join(alien_dir(), "candidates")


def load_candidate(phi_id: str) -> PhiMap:
    if phi_id in ("identity", "3dom"):
        return identity_phi()
    return load_phi(os.path.join(candidates_dir(), f"phi_{phi_id}.json"))


if __name__ == "__main__":
    import sys
    table = load_terminals()
    print(f"terminals.json  {table.grammar_version}")
    print(f"  {len(table.terminals)} terminals, "
          f"{len(table.substitutable_ids)} substitutable, "
          f"{len(table.non_substitutable_ids)} frozen")
    print(f"  spelling partition: {len(table.spelling_partition())} distinct "
          f"substitutable spellings")
    for name in sys.argv[1:] or ["identity"]:
        phi = load_candidate(name)
        print(f"OK  φ={phi.phi_id!r}  "
              f"{len(phi.substitutions)} substitutions, "
              f"{len(phi.overload_groups)} overload group(s)")
