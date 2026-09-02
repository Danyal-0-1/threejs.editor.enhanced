"""test_grammar_whitespace.py — the L2 selector layer, case by case.

Selector whitespace is the one place in this language where layout is MEANING
(I9): U+0020 is the descendant combinator. The outer level elides layout; the
inner level has no `%ignore` at all. Every claim that separation makes is tested
here, in every lexicon, because φ must not move it.

A note on where the normalisation lives. `.a  .b` (two spaces) and `.a > .b`
(padded child) both reach ONE canonical form, but NOT via canonicalize.py: the
collapse happens in the GRAMMAR, because `WS : / +/` is one token for a run of
spaces and `child_combinator : WS? CHILD WS?` absorbs its own padding. That is a
real canonicalisation step and it was unregistered in the C0–C8 table, so it is
named C9 here and in canonicalize.py's docstring. It is deliberately NOT moved
into Python: a working grammar-level normalisation rewritten as a post-pass
would be strictly more code and strictly more opportunity to disagree with the
parser.

Run standalone (`python3 tests/test_grammar_whitespace.py`) or under pytest.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))

from canonicalize import content_hash  # noqa: E402
from phi import identity_phi, load_candidate  # noqa: E402
from transpiler import (AmbiguityError, LexError, ParseError,  # noqa: E402
                        canon_text, dfa_accepts, lex, num_parses, parse,
                        phi_forward)

LEXICONS = ("identity", "alpha", "beta", "gamma")


def _wrap(selector: str) -> str:
    """A minimal program carrying `selector` verbatim, with no φ applied."""
    return "(function(){ $S('" + selector + "').delete(); })();"


def _in(lexicon: str, selector: str) -> tuple[str, object]:
    """(program text, φ) for `selector` rendered into `lexicon`."""
    phi = load_candidate(lexicon)
    return phi_forward(_wrap(selector), phi), phi


def _accepts(lexicon: str, selector: str) -> bool:
    src, phi = _in(lexicon, selector)
    return num_parses(src, phi) == 1


def _steps(lexicon: str, selector: str):
    src, phi = _in(lexicon, selector)
    return parse(src, phi).ops[0].selector.steps


def _hash(lexicon: str, selector: str) -> str:
    src, phi = _in(lexicon, selector)
    return content_hash(parse(src, phi))


# ── the descendant combinator ────────────────────────────────────────────────
def test_single_space_is_the_descendant_combinator() -> None:
    for lex_name in LEXICONS:
        steps = _steps(lex_name, ".a .b")
        assert [s.combinator for s in steps] == [None, "descendant"], \
            f"[{lex_name}] '.a .b' gave {[s.combinator for s in steps]}"


def test_no_space_is_a_compound_AND_not_two_steps() -> None:
    for lex_name in LEXICONS:
        steps = _steps(lex_name, ".a.b")
        assert len(steps) == 1, f"[{lex_name}] '.a.b' produced {len(steps)} steps"
        assert len(steps[0].matchers) == 2, \
            f"[{lex_name}] '.a.b' is not a two-matcher compound"


def test_the_whitespace_differential_survives_phi() -> None:
    """The Phase 1 G5 check, per lexicon: these are DIFFERENT queries."""
    for lex_name in LEXICONS:
        assert _hash(lex_name, ".a .b") != _hash(lex_name, ".a.b"), \
            f"[{lex_name}] descendant and compound collapsed to one IR"


# ── C9: grammar-level whitespace normalisation ───────────────────────────────
def test_C9_multiple_internal_spaces_normalise() -> None:
    """`WS : / +/` matches a RUN of spaces as one token, so '.a  .b' and
    '.a .b' are the same derivation, not two."""
    for lex_name in LEXICONS:
        one, two = _hash(lex_name, ".a .b"), _hash(lex_name, ".a  .b")
        assert one == two, f"[{lex_name}] one space and two spaces differ"
        assert _hash(lex_name, ".a   .b") == one, \
            f"[{lex_name}] three spaces differ from one"


def test_C9_padding_around_the_child_combinator_normalises() -> None:
    """`child_combinator : WS? CHILD WS?` absorbs its own padding."""
    for lex_name in LEXICONS:
        forms = [".a>.b", ".a >.b", ".a> .b", ".a > .b", ".a  >  .b"]
        hashes = {f: _hash(lex_name, f) for f in forms}
        assert len(set(hashes.values())) == 1, \
            f"[{lex_name}] child-combinator padding is not normalised: {hashes}"


def test_C9_normalisation_is_visible_in_the_canonical_text() -> None:
    """One canonical rendering per meaning, in every lexicon."""
    for lex_name in LEXICONS:
        phi = load_candidate(lex_name)
        texts = {canon_text(phi_forward(_wrap(f), phi), phi)
                 for f in (".a>.b", ".a > .b", ".a  >  .b")}
        assert len(texts) == 1, f"[{lex_name}] canonical text differs: {texts}"


def test_C9_does_not_erase_the_descendant_distinction() -> None:
    """Over-normalisation check: padding collapses, but ' ' vs '>' must not."""
    for lex_name in LEXICONS:
        assert _hash(lex_name, ".a .b") != _hash(lex_name, ".a > .b"), \
            f"[{lex_name}] descendant and child combinators collapsed"


# ── rejections ───────────────────────────────────────────────────────────────
def test_leading_selector_space_rejects() -> None:
    """`complex_selector` starts with a compound, so a leading WS is not
    derivable. This is the frozen grammar contract, not an accident."""
    for lex_name in LEXICONS:
        assert not _accepts(lex_name, " .a"), \
            f"[{lex_name}] a leading selector space was accepted"


def test_trailing_selector_space_rejects() -> None:
    for lex_name in LEXICONS:
        assert not _accepts(lex_name, ".a "), \
            f"[{lex_name}] a trailing selector space was accepted"
        assert not _accepts(lex_name, ".a .b "), \
            f"[{lex_name}] a trailing space after a descendant was accepted"


def test_tab_inside_a_selector_rejects_at_the_lexer() -> None:
    """Only U+0020 is the combinator. A tab is neither layout (there is no
    %ignore at L2) nor a combinator, so it must not lex."""
    for lex_name in LEXICONS:
        src, phi = _in(lex_name, ".a\t.b")
        try:
            lex(src, phi)
        except LexError:
            pass
        else:
            raise AssertionError(f"[{lex_name}] a tab lexed inside a selector")
        assert num_parses(src, phi) == 0, \
            f"[{lex_name}] a tab inside a selector parsed"
        assert not dfa_accepts(src, phi)


def test_empty_selector_rejects_at_the_L3_seam() -> None:
    """`$S('')` parses at the OUTER level (STRING matches '') and fails when the
    transformer descends into level 2 — which is what the L3 seam is."""
    for lex_name in LEXICONS:
        src, phi = _in(lex_name, "")
        try:
            parse(src, phi)
        except (ParseError, AmbiguityError):
            continue
        raise AssertionError(f"[{lex_name}] the empty selector was accepted")


def test_a_selector_of_only_spaces_rejects() -> None:
    for lex_name in LEXICONS:
        assert not _accepts(lex_name, " "), \
            f"[{lex_name}] a whitespace-only selector was accepted"


def test_bare_unknown_word_rejects() -> None:
    """A bare run that is not a type or pseudo keyword lexes to IDENT, which no
    production can consume in that position."""
    for lex_name in LEXICONS:
        assert not _accepts(lex_name, "notatype"), \
            f"[{lex_name}] a bare unknown word was accepted as a selector"


# ── quote symmetry (D2 / I8) ─────────────────────────────────────────────────
def test_matching_quotes_are_accepted_in_both_forms() -> None:
    for lex_name in LEXICONS:
        phi = load_candidate(lex_name)
        for quote in ("'", '"'):
            src = phi_forward("(function(){ $S(" + quote + ".a" + quote +
                              ").delete(); })();", phi)
            assert num_parses(src, phi) == 1, \
                f"[{lex_name}] a {quote}-quoted selector did not parse"


def test_mismatched_quotes_reject() -> None:
    """STRING binds its opening and closing quote in ONE alternative, so a
    mismatched pair is not derivable (repair D2)."""
    for lex_name in LEXICONS:
        phi = load_candidate(lex_name)
        for opening, closing in (("'", '"'), ('"', "'")):
            src = phi_forward("(function(){ $S(" + opening + ".a" + closing +
                              ").delete(); })();", phi)
            assert num_parses(src, phi) == 0, \
                f"[{lex_name}] {opening}.a{closing} parsed despite mismatched quotes"


def test_quote_characters_are_never_substituted() -> None:
    for lex_name in LEXICONS:
        phi = load_candidate(lex_name)
        assert phi.spelling("T_QUOTE_S") == "'"
        assert phi.spelling("T_QUOTE_D") == '"'


# ── the outer level, by contrast, DOES elide layout ──────────────────────────
def test_outer_layout_is_insignificant() -> None:
    """L1: the same program, differently laid out, is one IR."""
    for lex_name in LEXICONS:
        phi = load_candidate(lex_name)
        compact = phi_forward("(function(){ $S('.a').scale(2); })();", phi)
        spaced = phi_forward(
            "(function () {\n   $S( '.a' ) . scale( 2 ) ;\n})();", phi)
        assert content_hash(parse(compact, phi)) == content_hash(parse(spaced, phi)), \
            f"[{lex_name}] outer layout changed the IR"


def test_outer_layout_cannot_be_smuggled_into_a_selector() -> None:
    """The elision stops at the quote. A space INSIDE the selector is meaning,
    a space outside it is not — and the two must not be confused."""
    for lex_name in LEXICONS:
        phi = load_candidate(lex_name)
        inside = phi_forward(_wrap(".a .b"), phi)
        outside = phi_forward("(function(){ $S ( '.a.b' ) .delete(); })();", phi)
        assert content_hash(parse(inside, phi)) != content_hash(parse(outside, phi)), \
            f"[{lex_name}] selector-internal and external space were conflated"


# ── ambiguity is counted BEFORE transformation ───────────────────────────────
def test_every_whitespace_form_is_unambiguous() -> None:
    """I10 over exactly the forms this file exercises. `parse` raises
    AmbiguityError before any transformer method runs, so a second derivation
    can never reach the IR."""
    forms = [".a", ".a.b", ".a .b", ".a  .b", ".a>.b", ".a > .b", ".a  >  .b",
             ".a .b .c", ".a > .b > .c", ".a .b > .c", "*", "#x", "mesh",
             ":selected", ".a mesh", "mesh > .b"]
    for lex_name in LEXICONS:
        phi = load_candidate(lex_name)
        for form in forms:
            src = phi_forward(_wrap(form), phi)
            count = num_parses(src, phi)
            assert count == 1, \
                f"[{lex_name}] {form!r} has {count} derivations, expected 1"
            parse(src, phi)          # must not raise AmbiguityError


def test_ambiguity_is_reported_not_silently_resolved() -> None:
    """A synthetic ambiguous grammar, to prove the detector actually fires.
    Without this, 'zero ambiguities' could mean the check is broken."""
    from lark import Lark
    ambiguous = Lark("start: a | b\na: X\nb: X\nX: \"x\"",
                     start="start", parser="earley", ambiguity="explicit",
                     lexer="dynamic")
    from transpiler import _count_ambiguities
    assert _count_ambiguities(ambiguous.parse("x")) > 0, \
        "the ambiguity detector reported none on a provably ambiguous grammar"


def test_parser_cache_cannot_serve_the_wrong_lexicon() -> None:
    """Parsers are cached on a key derived from φ's CONTENT. If the key were the
    φ id alone, an edited candidate would silently reuse a stale parser."""
    from transpiler import _phi_key
    keys = {n: _phi_key(load_candidate(n)) for n in LEXICONS}
    assert len(set(keys.values())) == len(keys), f"φ keys collide: {keys}"
    beta = load_candidate("beta")
    mutated = load_candidate("beta")
    mutated.substitutions["T_VERB_SCALE"] = "CHANGED"
    assert _phi_key(beta) != _phi_key(mutated), \
        "the cache key ignores the substitution table, so an edited φ-map " \
        "would reuse the parser built from the old one"


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
            failures += 1
            print(f"  ERROR {name}\n        {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    print("test_grammar_whitespace — 3dom-grammar/1.1.0")
    raise SystemExit(main())
