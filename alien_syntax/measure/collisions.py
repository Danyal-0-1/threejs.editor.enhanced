"""collisions.py — lexical hazard checks on each candidate lexicon.

    python3 measure/collisions.py               # all candidates
    python3 measure/collisions.py beta --md     # one candidate, markdown table

Every check is a FAILURE, not a warning. A candidate with any failure violates
CONSTRAINT 2 of the pre-committed selection rule in reports/CANDIDATE_SELECTION.md.

Checks (a)–(f) are the ones the Phase 2 brief specifies. Check (g) is a PROPOSED
ADDITION, reported separately and flagged as such, so the pre-committed decision
never turns on a criterion that was added after the fact:

  (a) PREFIX HAZARD. A terminal that is a proper prefix of another terminal at
      the same lexical level, where maximal munch would mis-lex. 3DOM has zero
      such pairs; any alien pair is an unmatched increase in lexer difficulty.

  (b) BARE-IDENTIFIER HAZARD. An identifier-charset terminal that becomes
      ambiguous with an identifier where no sigil disambiguates — the bare
      type_selector position. Checked against the identifiers that actually
      occur in the corpora, not hypothetically.

  (c) OVERLOAD VIOLATION (I7). Roles that share a spelling in 3DOM must share a
      spelling in the alien language.

  (d) FROZEN SUBSTITUTION (I9). A substitutable:false terminal was substituted.

  (e) ASYMMETRIC DELIMITERS (I8). The quote terminals must be untouched, and no
      terminal may be drawn from a paired/asymmetric delimiter set — either
      would delete the quote-agreement constraint that repair D2 installed.

  (f) D3 REGRESSION. `argument ::= number | quoted_string` is unambiguous only
      because FIRST(number) = [+-0-9] and FIRST(quoted_string) = ['"] are
      disjoint. Recomputed here from the ACTUAL alien lexer, not assumed.

  (g) [PROPOSED] LEXICAL-CLASS AND REACHABILITY PARITY. Two parts:
        g1  a terminal spelled from the identifier charset in 3DOM must be
            spelled from it in the alien language, and vice versa;
        g2  for every ordered pair of word-class terminals X, Y at one level,
            concatenating their spellings must lex to the same number of tokens
            in both languages.
      g2 is the sharp one. In 3DOM, `mesh` + `mesh` lexes as the SINGLE token
      IDENT("meshmesh"), so the token sequence TYPE TYPE — although the grammar
      derives it — is UNREACHABLE from any 3DOM string. A lexicon whose type
      keywords are single glyphs makes it reachable, and then
      L(alien) is a strict SUPERSET of φ(L(3DOM)): the two languages are not
      isomorphic, whatever the production counts say. The identifier charset is
      frozen ASCII (identifier VALUES are copied verbatim into the shared IR), so
      any non-ASCII word-class spelling fails g1 and, in general, g2. That is a
      theorem about glyph lexicons, not a defect in one of them.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))

from phi import IDENT_CHARS, PhiMap, identity_phi, load_candidate  # noqa: E402
from transpiler import Lexer, lex  # noqa: E402
import generate_corpus as G  # noqa: E402

# Paired / asymmetric delimiter characters, and the open/close pairs they form.
# Substituting one of these for a terminal invites exactly the structural
# simplification I8 forbids: a reader (or a model) reads `‹ … ›` as a bracketed
# region, which is what removes the quote-AGREEMENT constraint repair D2
# installed. Characters 3DOM itself already uses are exempt — the check must not
# fail the reference language, and 3DOM spells its child combinator '>'.
ASYMMETRIC_PAIRS = (("‹", "›"), ("«", "»"), ("⟨", "⟩"), ("⟦", "⟧"), ("⟪", "⟫"),
                    ("「", "」"), ("『", "』"), ("【", "】"), ("〈", "〉"),
                    ("（", "）"), ("［", "］"), ("｛", "｝"), ("“", "”"),
                    ("‘", "’"), ("<", ">"), ("[", "]"))
ASYMMETRIC = {c for pair in ASYMMETRIC_PAIRS for c in pair}

Level = str        # "outer" | "inner"


def _levels(phi: PhiMap) -> dict[Level, dict[str, str]]:
    """{level: {terminal_id: spelling}} — the spellings each level must lex."""
    table = phi.table
    outer = ["T_SELECTOR_ENTRY", "T_FUNCTION", "T_CHAIN_OP"]
    outer += [t.id for t in table.terminals if t.role == "operation verb"]
    inner = ["T_ID_SIGIL", "T_CLASS_SIGIL", "T_PSEUDO_SIGIL", "T_CHILD",
             "T_WILDCARD"]
    inner += [t.id for t in table.terminals
              if t.role in ("type selector keyword", "pseudo-selector keyword")]
    return {"outer": {t: phi.spelling(t) for t in outer},
            "inner": {t: phi.spelling(t) for t in inner}}


def _is_word(spelling: str) -> bool:
    return bool(spelling) and all(c in IDENT_CHARS for c in spelling)


def _corpus_identifiers(phi: PhiMap) -> set[str]:
    """Every IDENT value that occurs in this lexicon's three corpora."""
    idents: set[str] = set()
    for name in G.CORPORA:
        for program in G.generate(phi, write=False)[name]:
            try:
                for tt, value, _pos in lex(program, phi):
                    if tt == "IDENT":
                        idents.add(value)
            except Exception:
                continue                    # negatives may not lex; that is fine
    return idents


# ─────────────────────────────────────────────────────────────────────────────
# The checks
# ─────────────────────────────────────────────────────────────────────────────

def check_a_prefix(phi: PhiMap, ident: PhiMap) -> list[str]:
    out: list[str] = []
    for level, spellings in _levels(phi).items():
        base = _levels(ident)[level]
        alien_pairs = _prefix_pairs(spellings)
        base_pairs = _prefix_pairs(base)
        for a, b in sorted(alien_pairs - base_pairs):
            out.append(f"({level}) {a!r} is a proper prefix of {b!r}; 3DOM has no "
                       f"such pair at this level, so maximal munch is harder here")
    return out


def _prefix_pairs(spellings: dict[str, str]) -> set[tuple[str, str]]:
    values = sorted(set(spellings.values()))
    return {(a, b) for a in values for b in values
            if a != b and b.startswith(a)}


def check_b_bare_identifier(phi: PhiMap, ident: PhiMap) -> list[str]:
    out: list[str] = []
    table = phi.table
    bare_ids = [t.id for t in table.terminals
                if t.role in ("type selector keyword", "pseudo-selector keyword")]
    idents = _corpus_identifiers(phi)
    for tid in bare_ids:
        spelling = phi.spelling(tid)
        if not _is_word(spelling):
            continue
        if spelling in idents:
            out.append(f"{tid} is spelled {spelling!r}, which also occurs as an "
                       f"IDENTIFIER in the corpus; in the bare type_selector "
                       f"position no sigil disambiguates them")
    return out


def check_c_overload(phi: PhiMap, ident: PhiMap) -> list[str]:
    out: list[str] = []
    source = ident.table.spelling_partition()
    alien: dict[str, set[str]] = {}
    for tid in phi.table.substitutable_ids:
        alien.setdefault(phi.spelling(tid), set()).add(tid)
    alien_p = frozenset(frozenset(v) for v in alien.values())
    for group in sorted(source - alien_p, key=lambda g: sorted(g)):
        if len(group) > 1:
            out.append(f"3DOM shares one spelling across {sorted(group)}; the "
                       f"alien lexicon splits them, which makes it strictly "
                       f"EASIER to lex (I7)")
    for group in sorted(alien_p - source, key=lambda g: sorted(g)):
        if len(group) > 1:
            out.append(f"the alien lexicon merges {sorted(group)}, an overload "
                       f"3DOM does not have (I7)")
    return out


def check_d_frozen(phi: PhiMap, ident: PhiMap) -> list[str]:
    return [f"{tid} is substitutable:false but appears in the map (I9)"
            for tid in phi.table.non_substitutable_ids
            if tid in phi.substitutions]


def check_e_delimiters(phi: PhiMap, ident: PhiMap) -> list[str]:
    out: list[str] = []
    # e1 — the string delimiters themselves are untouched.
    for qid in ("T_QUOTE_S", "T_QUOTE_D"):
        if phi.spelling(qid) != ident.spelling(qid):
            out.append(f"{qid} was substituted; string delimiters must stay "
                       f"symmetric (I8, repair D2)")
    # e2 — no NEW bracket character is introduced. 3DOM's own inventory is
    # exempt: it already spells the child combinator '>', and a check that fails
    # the reference language is a broken check, not a finding.
    baseline_chars = {c for tid in ident.table.substitutable_ids
                      for c in ident.spelling(tid)}
    for tid in sorted(phi.table.substitutable_ids):
        spelling = phi.spelling(tid)
        hits = sorted((set(spelling) & ASYMMETRIC) - baseline_chars)
        if hits:
            out.append(f"{tid} is spelled {spelling!r}, introducing paired/"
                       f"asymmetric delimiter character(s) {hits} that 3DOM does "
                       f"not use (I8)")
    # e3 — no alien lexicon may contain BOTH halves of a pair, which would let a
    # reader treat the two terminals as an open/close delimiter around a region.
    used = {phi.spelling(tid) for tid in phi.table.substitutable_ids}
    for open_c, close_c in ASYMMETRIC_PAIRS:
        if any(open_c in s for s in used) and any(close_c in s for s in used):
            if not ({open_c, close_c} <= baseline_chars):
                out.append(f"the lexicon uses both halves of the delimiter pair "
                           f"{open_c!r}…{close_c!r}, which reads as an asymmetric "
                           f"paired delimiter (I8)")
    return out


def check_f_d3(phi: PhiMap, ident: PhiMap) -> list[str]:
    """FIRST(number) and FIRST(quoted_string) must stay disjoint, and no
    substituted terminal may intrude on either."""
    out: list[str] = []
    first_number = set("+-0123456789")
    first_string = {phi.spelling("T_QUOTE_S"), phi.spelling("T_QUOTE_D")}
    if first_number & first_string:
        out.append("FIRST(number) and FIRST(quoted_string) overlap — repair D3's "
                   "argument unambiguity is lost")
    for tid in phi.table.substitutable_ids:
        lead = phi.spelling(tid)[:1]
        if lead in first_number or lead in first_string:
            out.append(f"{tid} is spelled {phi.spelling(tid)!r}, which starts in "
                       f"FIRST(argument); this re-opens the D3 ambiguity")
    return out


def check_g_parity(phi: PhiMap, ident: PhiMap) -> list[str]:
    """[PROPOSED] lexical-class (g1) and reachability (g2) parity."""
    out: list[str] = []
    alien_lexer, base_lexer = Lexer(phi), Lexer(ident)
    levels, base_levels = _levels(phi), _levels(ident)

    # g1 — class parity, reported for every terminal at every level.
    for level, spellings in levels.items():
        base = base_levels[level]
        for tid, spelling in sorted(spellings.items()):
            if _is_word(base[tid]) != _is_word(spelling):
                was = "identifier-charset word" if _is_word(base[tid]) else "symbol"
                now = "identifier-charset word" if _is_word(spelling) else "symbol"
                out.append(f"g1 ({level}) {tid}: 3DOM spells it as a {was} "
                           f"({base[tid]!r}), the alien lexicon as a {now} "
                           f"({spelling!r}); the keyword-vs-identifier "
                           f"discrimination is not matched")

    # g2 — reachability parity. ONE witness per level is a proof, so we stop at
    # the first at each level rather than enumerating the whole cross product.
    for level, spellings in levels.items():
        base = base_levels[level]
        word_ids = [t for t in spellings if _is_word(base[t])]
        found = False
        for x in word_ids:
            if found:
                break
            for y in word_ids:
                n_base = _token_count(base_lexer, level, base[x] + base[y])
                n_alien = _token_count(alien_lexer, level,
                                       spellings[x] + spellings[y])
                if n_base != n_alien:
                    out.append(
                        f"g2 ({level}) {base[x]}+{base[y]} lexes to {n_base} "
                        f"token(s) in 3DOM but {spellings[x]}+{spellings[y]} lexes "
                        f"to {n_alien} in the alien lexicon — the alien language "
                        f"makes a token sequence reachable that no 3DOM string can "
                        f"produce, so L(alien) is a strict superset of phi(L(3DOM))")
                    found = True
                    break
    return out


def _token_count(lexer: Lexer, level: Level, text: str) -> int:
    try:
        if level == "inner":
            return len(lexer.lex_selector_body(text, 0))
        return len(lexer.lex(text))
    except Exception:
        return -1


CHECKS = (
    ("a", "prefix hazard", check_a_prefix),
    ("b", "bare-identifier hazard", check_b_bare_identifier),
    ("c", "overload preservation (I7)", check_c_overload),
    ("d", "frozen terminals (I9)", check_d_frozen),
    ("e", "delimiter symmetry (I8)", check_e_delimiters),
    ("f", "D3 argument unambiguity", check_f_d3),
)
PROPOSED = (("g", "[proposed] lexical-class + reachability parity", check_g_parity),)


def run(phi: PhiMap) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    ident = identity_phi(phi.table)
    specified = {key: fn(phi, ident) for key, _label, fn in CHECKS}
    proposed = {key: fn(phi, ident) for key, _label, fn in PROPOSED}
    return specified, proposed


def main(argv: list[str]) -> int:
    names = [a for a in argv[1:] if not a.startswith("-")] or \
        ["identity", "alpha", "beta", "gamma"]
    as_md = "--md" in argv
    labels = {k: v for k, v, _ in CHECKS + PROPOSED}
    status = 0
    rows: list[tuple[str, str, str, str]] = []
    for name in names:
        phi = load_candidate(name)
        specified, proposed = run(phi)
        n_spec = sum(len(v) for v in specified.values())
        n_prop = sum(len(v) for v in proposed.values())
        if not as_md:
            print(f"\nφ = {phi.phi_id}")
            print(f"  checks (a)-(f), the pre-committed CONSTRAINT 2: "
                  f"{'PASS — 0 violations' if not n_spec else f'FAIL — {n_spec} violation(s)'}")
            for key, _label, _fn in CHECKS:
                for msg in specified[key]:
                    print(f"    ({key}) {msg}")
            print(f"  check (g), PROPOSED, reported separately: "
                  f"{'PASS' if not n_prop else f'FAIL — {n_prop} finding(s)'}")
            for key, _label, _fn in PROPOSED:
                for msg in proposed[key][:4]:
                    print(f"    ({key}) {msg}")
                if len(proposed[key]) > 4:
                    print(f"    ({key}) … and {len(proposed[key]) - 4} more")
        for key, _label, _fn in CHECKS + PROPOSED:
            findings = specified.get(key, proposed.get(key, []))
            rows.append((phi.phi_id, key, labels[key],
                         "PASS" if not findings else f"FAIL ({len(findings)})"))
        if n_spec:
            status = 1
    if as_md:
        print("| lexicon | check | what it tests | result |")
        print("|---|---|---|---|")
        for lexicon, key, label, result in rows:
            print(f"| `{lexicon}` | ({key}) | {label} | **{result}** |")
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
