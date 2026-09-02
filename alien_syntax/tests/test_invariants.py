"""test_invariants.py — one test per HARD INVARIANT I1–I10.

Each failure message names the invariant it belongs to, so a red test says which
part of the isomorphism contract broke rather than merely that something did.

The grammar-shape invariants (I1, I2, I3) are checked against the GENERATED
.ebnf files using Phase 1's own `grammar_metrics.parse_ebnf`, so the alien
grammar is measured with the identical instrument that produced METRICS.md.
"""

from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))
sys.path.insert(0, os.path.join(ALIEN, "measure"))

from phi import identity_phi, load_candidate, phase1_dir, render_slots  # noqa: E402
from transpiler import (AmbiguityError, ParseError, lex, num_parses,  # noqa: E402
                        parse, phi_forward)
import collisions as C  # noqa: E402
import generate_corpus as G  # noqa: E402
import refgrammar as R  # noqa: E402

sys.path.insert(0, phase1_dir())
import grammar_metrics as GM  # noqa: E402

CANDIDATES = ("alpha", "beta", "gamma")
GENERATED = os.path.join(ALIEN, "grammar", "generated")


def _metrics(path: str, notation: str):
    return GM.parse_ebnf(path, notation)


def _pairs():
    """[(name, notation, phase1_path, alien_path)] for both notations."""
    out = []
    for name in CANDIDATES:
        for notation, p1 in (("w3c", "3dom_grammar.w3c.ebnf"),
                             ("iso", "3dom_grammar.iso.ebnf")):
            out.append((name, notation,
                        os.path.join(phase1_dir(), p1),
                        os.path.join(GENERATED, f"alien.{name}.{notation}.ebnf")))
    return out


# ── I1 ───────────────────────────────────────────────────────────────────────
def test_I1_same_nonterminal_set() -> None:
    for name, notation, p1, alien in _pairs():
        a, b = _metrics(p1, notation), _metrics(alien, notation)
        na, nb = set(a["nonterminals"]), set(b["nonterminals"])
        assert na == nb, (
            f"I1 [{name}/{notation}] non-terminal set is not one-to-one: "
            f"3DOM-only={sorted(na - nb)} alien-only={sorted(nb - na)}")
        assert a["N"] == b["N"] == 31, \
            f"I1 [{name}/{notation}] |N| = {b['N']}, expected 31"


# ── I2 ───────────────────────────────────────────────────────────────────────
def test_I2_same_production_and_alternation_counts() -> None:
    for name, notation, p1, alien in _pairs():
        a, b = _metrics(p1, notation), _metrics(alien, notation)
        assert a["P"] == b["P"], (
            f"I2 [{name}/{notation}] |P| differs: 3DOM {a['P']} vs alien {b['P']}")
        for rule in a["nonterminals"]:
            alts_a = len(re.sub(r"'[^']*'|\"[^\"]*\"", " L ",
                                a_rhs(p1, notation, rule)).split("|"))
            alts_b = len(re.sub(r"'[^']*'|\"[^\"]*\"", " L ",
                                a_rhs(alien, notation, rule)).split("|"))
            assert alts_a == alts_b, (
                f"I2 [{name}/{notation}] rule {rule!r} has {alts_b} alternatives, "
                f"3DOM has {alts_a}")


def a_rhs(path: str, notation: str, rule: str) -> str:
    raw = open(path, encoding="utf-8").read()
    body = GM.strip_comments(raw, notation)
    if notation == "w3c":
        parts = re.split(r"\n(?=[A-Za-z_][A-Za-z0-9_]*\s*::=)", body)
        rx = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*::=(.*)$", re.S)
    else:
        parts = body.split(";")
        rx = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$", re.S)
    for part in parts:
        m = rx.match(part)
        if m and m.group(1) == rule:
            return m.group(2)
    return ""


# ── I3 ───────────────────────────────────────────────────────────────────────
def test_I3_same_operator_skeleton() -> None:
    for name, notation, p1, alien in _pairs():
        a, b = _metrics(p1, notation), _metrics(alien, notation)
        assert a["ops"] == b["ops"], (
            f"I3 [{name}/{notation}] operator counts differ: "
            f"3DOM {a['ops']} vs alien {b['ops']}")


def test_I3_chain_stays_infix_and_left_to_right() -> None:
    """No prefix, postfix or stack-based form. The selector comes first and the
    operations appear in IR order, in every lexicon."""
    src = "(function(){ $S('.wheel').scale(2).move(1,0,0); })();"
    for name in CANDIDATES:
        phi = load_candidate(name)
        alien = phi_forward(src, phi)
        entry = phi.spelling("T_SELECTOR_ENTRY")
        first = phi.spelling("T_VERB_SCALE")
        second = phi.spelling("T_VERB_MOVE")
        i_entry, i_1, i_2 = (alien.index(entry), alien.index(first),
                             alien.index(second))
        assert i_entry < i_1 < i_2, (
            f"I3 [{name}] chain is not infix/left-to-right: {alien!r}")
        ir = parse(alien, phi)
        assert [op.op for op in ir.ops] == ["scale", "move"], \
            f"I3 [{name}] operation order was not preserved"
        # a postfix rendering must NOT be in the language
        postfix = alien.replace(f"{entry}(", "@@(", 1)
        assert num_parses(postfix, phi) == 0, \
            f"I3 [{name}] a non-infix form parsed"


# ── I4 ───────────────────────────────────────────────────────────────────────
def test_I4_regular_non_self_embedding() -> None:
    """A DFA over the DSL token alphabet exists and accepts the whole positive
    corpus — a finite automaton exists IFF the language is regular."""
    from transpiler import dfa_accepts
    d = R.dfa()
    assert d["nstates"] == 52, f"I4 DFA has {d['nstates']} states, expected 52"
    for name in CANDIDATES:
        phi = load_candidate(name)
        for p in G.generate(phi, write=False)["positive"]:
            assert dfa_accepts(p, phi), \
                f"I4 [{name}] DFA rejected a positive item: {p[:60]!r}"


def test_I4_no_nesting_introduced() -> None:
    """A nested selector call must be rejected in every lexicon: nesting is the
    structural manipulation this phase explicitly does not make."""
    for name in CANDIDATES:
        phi = load_candidate(name)
        entry = phi.spelling("T_SELECTOR_ENTRY")
        nested = phi_forward(
            "(function(){ $S('.a').scale(2); })();", phi).replace(
            "2", f"{entry}('.b')", 1)
        assert num_parses(nested, phi) == 0, \
            f"I4 [{name}] a nested selector call parsed: {nested!r}"


# ── I5 ───────────────────────────────────────────────────────────────────────
def test_I5_closed_set_cardinalities() -> None:
    for name in CANDIDATES:
        phi = load_candidate(name)
        roles = {}
        for t in phi.table.terminals:
            roles.setdefault(t.role, []).append(t.id)
        counts = {
            "verbs": len(roles["operation verb"]),
            "types": len(roles["type selector keyword"]),
            "pseudos": len(roles["pseudo-selector keyword"]),
        }
        assert counts == {"verbs": 15, "types": 4, "pseudos": 2}, \
            f"I5 [{name}] closed-set cardinalities are {counts}"
        spellings = {phi.spelling(i) for r in
                     ("operation verb", "type selector keyword",
                      "pseudo-selector keyword") for i in roles[r]}
        assert len(spellings) == 21, \
            f"I5 [{name}] the 21 closed-set spellings are not distinct"
        # two argument kinds: number | quoted_string (hex folded into the IR, D3)
        rhs = a_rhs(os.path.join(GENERATED, f"alien.{name}.w3c.ebnf"),
                    "w3c", "argument")
        assert len(rhs.split("|")) == 2, \
            f"I5 [{name}] argument has {len(rhs.split('|'))} kinds, expected 2"


# ── I6 ───────────────────────────────────────────────────────────────────────
def test_I6_lookahead_is_still_two() -> None:
    """The k=2 decision point survives φ: after a selector-internal WS the
    automaton still has BOTH a child continuation and a descendant continuation,
    so one token of lookahead cannot decide."""
    d = R.dfa()
    for name in CANDIDATES:
        phi = load_candidate(name)
        prefix = phi_forward("(function(){ $S('.a .b').delete(); })();", phi)
        tokens = [t[0] for t in lex(prefix, phi)]
        ws_at = tokens.index("WS")
        st = d["start"]
        for tt in tokens[:ws_at + 1]:
            st = d["trans"][st][tt]
        nxt = set(d["trans"].get(st, {}))
        assert "GT" in nxt, f"I6 [{name}] no child continuation after WS"
        assert nxt - {"GT"}, f"I6 [{name}] no descendant continuation after WS"
        # and both witnesses really are in the language
        for sel in (".a .b", ".a > .b"):
            p = phi_forward(f"(function(){{ $S('{sel}').delete(); }})();", phi)
            assert num_parses(p, phi) == 1, f"I6 [{name}] {sel!r} did not parse"


# ── I7 ───────────────────────────────────────────────────────────────────────
def test_I7_overload_preserved() -> None:
    for name in CANDIDATES:
        phi = load_candidate(name)
        chain = phi.spelling("T_CHAIN_OP")
        cls = phi.spelling("T_CLASS_SIGIL")
        assert chain == cls, (
            f"I7 [{name}] the '.' overload was split: chain={chain!r} "
            f"class={cls!r}; de-overloading makes the alien language strictly "
            f"easier to lex than 3DOM")
        assert not C.check_c_overload(phi, identity_phi(phi.table)), \
            f"I7 [{name}] the spelling partition is not preserved"


# ── I8 ───────────────────────────────────────────────────────────────────────
def test_I8_delimiter_symmetry_preserved() -> None:
    for name in CANDIDATES:
        phi = load_candidate(name)
        ident = identity_phi(phi.table)
        assert phi.spelling("T_QUOTE_S") == "'" and phi.spelling("T_QUOTE_D") == '"', \
            f"I8 [{name}] a string delimiter was substituted"
        findings = C.check_e_delimiters(phi, ident)
        assert not findings, f"I8 [{name}] {findings[0]}"
        # the quote-agreement constraint still bites
        bad = phi_forward("(function(){ $S('.a\").delete(); })();", phi)
        assert num_parses(bad, phi) == 0, \
            f"I8 [{name}] a mismatched-quote program parsed"


# ── I9 ───────────────────────────────────────────────────────────────────────
def test_I9_whitespace_significance_preserved() -> None:
    for name in CANDIDATES:
        phi = load_candidate(name)
        assert "T_WS" not in phi.substitutions, \
            f"I9 [{name}] T_WS was substituted"
        assert "T_WS" in phi.frozen, f"I9 [{name}] T_WS is not declared frozen"
        descendant = phi_forward("(function(){ $S('.car .wheel').delete(); })();", phi)
        toks = [t[0] for t in lex(descendant, phi)]
        assert "WS" in toks, \
            f"I9 [{name}] the descendant combinator is no longer whitespace"


def test_I9_whitespace_differential() -> None:
    """The Phase 1 L2 check, per lexicon: the alien renderings of '.car .wheel'
    and '.car.wheel' must parse to DIFFERENT structures."""
    for name in CANDIDATES:
        phi = load_candidate(name)
        a = phi_forward("(function(){ $S('.car .wheel').delete(); })();", phi)
        b = phi_forward("(function(){ $S('.car.wheel').delete(); })();", phi)
        fa, _ = R.derive(lex(a, phi))
        fb, _ = R.derive(lex(b, phi))
        assert ("combinator", 0) in fa, f"I9 [{name}] descendant branch unused"
        assert ("matchers", 1) in fb, f"I9 [{name}] compound-AND branch unused"
        assert fa != fb, \
            f"I9 [{name}] descendant and compound collapsed to one structure"


# ── I10 ──────────────────────────────────────────────────────────────────────
def test_I10_zero_ambiguity_over_positive_corpus() -> None:
    """Two independent witnesses: Earley's explicit-ambiguity mode (the Lark
    front end) and the exact derivation counter (Phase 1's parse_counts)."""
    for name in CANDIDATES:
        phi = load_candidate(name)
        for p in G.generate(phi, write=False)["positive"]:
            count = num_parses(p, phi)
            assert count == 1, \
                f"I10 [{name}] {count} derivations for {p[:60]!r}"
            try:
                parse(p, phi)
            except AmbiguityError as exc:
                raise AssertionError(f"I10 [{name}] Earley reported ambiguity "
                                     f"on {p[:60]!r}: {exc}")
            except ParseError as exc:
                raise AssertionError(f"I10 [{name}] failed to parse {p[:60]!r}: "
                                     f"{exc}")


# ── the templates really are the Phase 1 grammar ─────────────────────────────
def test_templates_render_to_phase1_under_identity() -> None:
    ident = identity_phi()
    banner = "version: 3dom-grammar/1.1.0  —  TEMPLATE (slots: {{ TERMINAL_ID }})"
    for template, p1 in (("grammar.iso.template.ebnf", "3dom_grammar.iso.ebnf"),
                         ("grammar.w3c.template.ebnf", "3dom_grammar.w3c.ebnf")):
        with open(os.path.join(ALIEN, "grammar", "templates", template),
                  encoding="utf-8") as fh:
            rendered = render_slots(fh.read(), ident).replace(
                banner, "version: 3dom-grammar/1.1.0")
        with open(os.path.join(phase1_dir(), p1), encoding="utf-8") as fh:
            assert rendered == fh.read(), (
                f"the identity render of {template} is not byte-identical to "
                f"Phase 1 — the template is a retyping, not a derivation")


def main() -> int:
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as exc:
            failures += 1
            print(f"  FAIL  {name}\n        {exc}")
        except Exception as exc:
            # An ERROR is not a pass. See the note in test_isomorphism.main.
            failures += 1
            print(f"  ERROR {name}\n        {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    print("test_invariants — 3dom-grammar/1.1.0")
    raise SystemExit(main())
