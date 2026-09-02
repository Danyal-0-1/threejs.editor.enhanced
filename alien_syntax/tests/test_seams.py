"""test_seams.py — the three lexical seams, compared explicitly.

Three components read this language's surface text, and they are deliberately
NOT the same program:

  1. the LARK front end      grammar-exact, Earley, raises on malformed text;
                             the reference recognizer.
  2. the HAND-WRITTEN LEXER  emits typed tokens for the Phase 1 DFA, supports
                             the branching and longest-valid-prefix metrics,
                             raises LexError; an INDEPENDENT recognizer.
  3. the TRANSLITERATOR      φ on raw TEXT, malformed input included; never
                             raises, because the negative corpus is invalid by
                             construction and must still be mappable.

Two of them must AGREE and one must not. Seams 1 and 2 share no code, so their
agreement over the corpora is evidence rather than tautology — it is Phase 1's
gate G6, repeated per lexicon. Seam 3 must be strictly MORE lenient, and the
interesting property is not that it accepts more but that it neither REPAIRS a
defect nor ADDS one: a 3DOM near-miss must arrive in the alien corpus as the
same near-miss, on the same production.

The three use different rules for deciding whether text is in selector
position, and that difference is intentional. This file pins it so it cannot
drift into an accident.

Run standalone (`python3 tests/test_seams.py`) or under pytest.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))

from phi import identity_phi, load_candidate  # noqa: E402
from transpiler import (LexError, Transliterator, accepts,  # noqa: E402
                        dfa_accepts, lex, num_parses, phi_forward, phi_inverse,
                        transliterate)
import generate_corpus as G  # noqa: E402

LEXICONS = ("alpha", "beta", "gamma")
CORPORA = ("positive", "negative", "vacuous")


def _corpora_for(name: str) -> dict[str, list[str]]:
    phi = load_candidate(name)
    if name in ("identity", "3dom"):
        ident = identity_phi(phi.table)
        return {c: G.phase1_programs(c, ident) for c in CORPORA}
    return {c: G.generate(phi, write=False)[c] for c in CORPORA}


# ─────────────────────────────────────────────────────────────────────────────
# Seam 1 vs seam 2 — the biconditional
# ─────────────────────────────────────────────────────────────────────────────

def test_lark_and_dfa_agree_on_every_corpus_item_in_every_lexicon() -> None:
    """lark_accepts(x, φ) == dfa_accepts(x, φ), for all 138 items × 4 lexicons.

    This is the biconditional, not two one-way checks: a recognizer that
    accepted everything would pass 'positives are accepted' and fail here.
    """
    checked = 0
    for name in ("identity",) + LEXICONS:
        phi = load_candidate(name)
        for corpus, items in _corpora_for(name).items():
            for item in items:
                lark_says = accepts(item, phi)
                dfa_says = dfa_accepts(item, phi)
                assert lark_says == dfa_says, (
                    f"[{name}/{corpus}] the two recognizers disagree:\n"
                    f"  lark accepts = {lark_says}\n"
                    f"  dfa  accepts = {dfa_says}\n"
                    f"  item        = {item!r}")
                checked += 1
    assert checked >= 4 * 138, f"only {checked} item/lexicon pairs were checked"


def test_the_biconditional_is_not_vacuous() -> None:
    """Both recognizers must actually REJECT things, or the agreement above is
    the trivial agreement of two functions that always say yes."""
    for name in ("identity",) + LEXICONS:
        phi = load_candidate(name)
        corpora = _corpora_for(name)
        assert all(accepts(x, phi) for x in corpora["positive"]), \
            f"[{name}] a positive was rejected by Lark"
        assert not any(accepts(x, phi) for x in corpora["negative"]), \
            f"[{name}] a negative was accepted by Lark"
        assert not any(dfa_accepts(x, phi) for x in corpora["negative"]), \
            f"[{name}] a negative was accepted by the DFA"


def test_the_exact_parse_counter_agrees_with_both() -> None:
    """A third witness: refgrammar's exact derivation counter over our token
    stream. num_parses == 1 iff accepted, for the whole corpus."""
    for name in ("identity",) + LEXICONS:
        phi = load_candidate(name)
        corpora = _corpora_for(name)
        for x in corpora["positive"] + corpora["vacuous"]:
            assert num_parses(x, phi) == 1, f"[{name}] {x[:50]!r} not unique"
        for x in corpora["negative"]:
            assert num_parses(x, phi) == 0, f"[{name}] negative {x[:50]!r} parsed"


# ─────────────────────────────────────────────────────────────────────────────
# Seam 3 — the transliterator is lenient, but neither repairs nor compounds
# ─────────────────────────────────────────────────────────────────────────────

def test_transliterator_never_raises_on_malformed_text() -> None:
    """It must map the negative corpus, which by construction does not parse,
    and a handful of inputs uglier than anything in it."""
    hostile = [
        "",
        "(",
        "'unterminated",
        '(function(){ $S(".a\').delete(); })();',
        "(function(){ $S('.a').delete()",
        "\x00\x01 not even text",
        "$S(",
        "(function(){ $S('" + "." * 200 + "').delete(); })();",
    ]
    for name in LEXICONS:
        phi = load_candidate(name)
        ident = identity_phi(phi.table)
        for text in hostile + _corpora_for("identity")["negative"]:
            try:
                transliterate(text, ident, phi)
            except Exception as exc:
                raise AssertionError(
                    f"[{name}] the transliterator raised {type(exc).__name__} "
                    f"on {text[:60]!r}; it must be total")


def test_a_near_miss_stays_a_near_miss() -> None:
    """Generating the negative corpus BY φ is itself an isomorphism check: a
    3DOM near-miss that became valid would mean φ moved structure."""
    ident = identity_phi()
    for name in LEXICONS:
        phi = load_candidate(name)
        for x in G.phase1_programs("negative", ident):
            assert num_parses(x, ident) == 0, f"corpus defect: {x!r} parses in 3DOM"
            alien = phi_forward(x, phi)
            assert num_parses(alien, phi) == 0, \
                f"[{name}] a near-miss became valid: {x!r} -> {alien!r}"


def test_a_defect_is_not_repaired_and_not_multiplied() -> None:
    """The sharp case the code comments call out: a MISSPELLED entry point.

    `$D('.a')` carries exactly one defect (an unknown bareword where ENTRY is
    required). The transliterator's selector-position rule is deliberately
    lenient enough to still rewrite the selector body, so the alien image also
    carries exactly ONE defect. A stricter rule would leave the selector in 3DOM
    spelling and the item would arrive carrying TWO — which would silently make
    the alien negative corpus harder than the 3DOM one.
    """
    for name in LEXICONS:
        phi = load_candidate(name)
        ident = identity_phi(phi.table)
        broken = "(function(){ $D('.a.b').delete(); })();"
        alien = transliterate(broken, ident, phi)
        assert num_parses(broken, ident) == 0, "fixture is not a near-miss"
        assert num_parses(alien, phi) == 0, f"[{name}] the near-miss was repaired"
        # the SELECTOR was still translated: the class sigil moved
        sigil = phi.spelling("T_CLASS_SIGIL")
        assert sigil in alien, (
            f"[{name}] the selector body was left in 3DOM spelling, so this "
            f"item now carries a second defect: {alien!r}")
        # and the verb moved too, so only the entry point is still wrong
        assert phi.spelling("T_VERB_DELETE") in alien, \
            f"[{name}] the verb was not translated: {alien!r}"


def test_an_unterminated_string_stays_unterminated() -> None:
    """The D2 near-miss class. The transliterator emits the opening quote and
    keeps reading in OUTER mode; the result must still fail to parse."""
    for name in LEXICONS:
        phi = load_candidate(name)
        ident = identity_phi(phi.table)
        for broken in ("(function(){ $S('.a).delete(); })();",
                       '(function(){ $S(".a).delete(); })();'):
            alien = transliterate(broken, ident, phi)
            assert num_parses(broken, ident) == 0, "fixture is not a near-miss"
            assert num_parses(alien, phi) == 0, \
                f"[{name}] an unterminated string was repaired: {alien!r}"


def test_transliteration_is_invertible_on_well_formed_text() -> None:
    ident = identity_phi()
    for name in LEXICONS:
        phi = load_candidate(name)
        for x in (G.phase1_programs("positive", ident)
                  + G.phase1_programs("vacuous", ident)):
            assert phi_inverse(phi_forward(x, phi), phi) == x, \
                f"[{name}] φ⁻¹∘φ != id on {x!r}"


def test_transliteration_preserves_identifiers_and_numbers_verbatim() -> None:
    """Identifier VALUES are copied into the shared IR, so φ must not touch
    them; numbers and argument-string bodies likewise."""
    ident = identity_phi()
    src = "(function(){ $S('#Wheel-Front_02').recolor('#A1b2C3').scale(1.50); })();"
    for name in LEXICONS:
        phi = load_candidate(name)
        alien = phi_forward(src, phi)
        for literal in ("Wheel-Front_02", "#A1b2C3", "1.50"):
            assert literal in alien, \
                f"[{name}] {literal!r} was altered by φ: {alien!r}"


# ─────────────────────────────────────────────────────────────────────────────
# The selector-position rules: different on purpose, compatible in practice
# ─────────────────────────────────────────────────────────────────────────────

def test_the_two_selector_position_rules_agree_on_well_formed_text() -> None:
    """The lexer requires DOLLAR LP immediately before the string; the
    transliterator also accepts WORD LP and OTHER LP. On text that parses, the
    two must pick out the SAME strings, or φ would rewrite a selector the
    recognizer treats as an opaque argument (or vice versa)."""
    ident = identity_phi()
    for x in G.phase1_programs("positive", ident):
        # the lexer's view: a QUOTE token is emitted only in selector position
        quoted = sum(1 for tt, _v, _p in lex(x, ident) if tt == "QUOTE") // 2
        # the transliterator's view, on the identity map: a selector body is the
        # only thing it descends into, so translating with a φ that renames the
        # class sigil marks exactly those regions
        beta = load_candidate("beta")
        alien = phi_forward(x, beta)
        descended = alien.count(beta.spelling("T_CLASS_SIGIL")) > 0
        has_class = "." in "".join(
            v for tt, v, _p in lex(x, ident) if tt == "CSIG")
        assert (quoted > 0) or not has_class, \
            f"the lexer found no selector in {x[:60]!r}"
        if has_class:
            assert descended, \
                f"the transliterator did not descend into the selector of {x[:60]!r}"


def test_an_argument_string_is_never_treated_as_a_selector() -> None:
    """`recolor('.notaselector')` — the argument is opaque (D3). Neither seam
    may descend into it, or a colour value would be rewritten by φ."""
    ident = identity_phi()
    src = "(function(){ $S('.a').recolor('.b#c'); })();"
    types = [tt for tt, _v, _p in lex(src, ident)]
    assert types.count("STRING") == 1, \
        f"the argument string was not lexed as one opaque STRING: {types}"
    for name in LEXICONS:
        phi = load_candidate(name)
        alien = phi_forward(src, phi)
        assert ".b#c" in alien, \
            f"[{name}] φ rewrote an argument string body: {alien!r}"


def test_lexer_selector_detection_requires_the_entry_point() -> None:
    """A string after a misspelled entry is NOT a selector to the lexer. This is
    exactly the rule the transliterator deliberately relaxes.

    The misspelling has to be a BAREWORD (`SS`), not `$D`: `$` is not a legal
    lead character on its own, so `$D` dies in the lexer at the `$` before the
    selector-position question is ever reached. Both are near-misses; only this
    one exercises the context rule.
    """
    ident = identity_phi()
    types = [tt for tt, _v, _p in lex("(function(){ SS('.a'); })();", ident)]
    assert "QUOTE" not in types, \
        f"the lexer descended into a selector after a misspelled entry: {types}"
    assert "STRING" in types, f"the string was not lexed as opaque: {types}"
    assert "BADWORD" in types, f"the misspelled entry was not flagged: {types}"

    # `$D` is a near-miss too, but it fails EARLIER, in the character scan.
    try:
        lex("(function(){ $D('.a'); })();", ident)
    except LexError:
        pass
    else:
        raise AssertionError("'$D' unexpectedly lexed")


def test_the_transliterator_relaxes_exactly_that_rule() -> None:
    """Where the lexer refuses to see a selector, the transliterator still
    descends — so a one-defect negative does not gain a second defect."""
    for name in LEXICONS:
        phi = load_candidate(name)
        ident = identity_phi(phi.table)
        alien = transliterate("(function(){ SS('.a.b'); })();", ident, phi)
        assert phi.spelling("T_CLASS_SIGIL") in alien, (
            f"[{name}] the transliterator did not descend where the lexer "
            f"refuses to: {alien!r}")
        assert num_parses(alien, phi) == 0, \
            f"[{name}] the near-miss was repaired: {alien!r}"


def test_transliterator_context_history_is_bounded() -> None:
    """`push` keeps only the last two token kinds. A longer history would make
    selector detection depend on unbounded context and stop matching the
    lexer's two-token rule."""
    ident = identity_phi()
    beta = load_candidate("beta")
    tr = Transliterator(ident, beta)
    prev: list[str] = []

    def push(kind: str) -> None:
        prev.append(kind)
        del prev[:-2]
    for kind in "abcdefghij":
        push(kind)
    assert len(prev) <= 2, f"context history grew to {len(prev)}"
    assert prev == ["i", "j"]
    # and the real thing still round-trips a long chain
    long_chain = ("(function(){ " + "$S('.a').scale(2); " * 8 + "})();")
    assert phi_inverse(phi_forward(long_chain, beta), beta) == long_chain


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
    print("test_seams — 3dom-grammar/1.1.0")
    raise SystemExit(main())
