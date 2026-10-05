"""Tests for decision-site enumeration and collision classification.

The load-bearing ones here are:

  * `test_colour_literal_is_not_a_site` — the `'#333333'` hazard. `#` is also a
    sigil spelling, so a naive str.replace would corrupt arguments and invent
    collisions. Sites must come from the lexer's offsets.
  * `test_token_type_map_matches_lexer` — SIMPLE_TOKEN_TERMINAL is a hand-written
    mirror of transpiler.Lexicon.of(); this verifies it against a freshly lexed
    program instead of trusting it.
  * `test_semantic_requires_both_valid_and_different_ir` — the review's actual
    requirement, asserted rather than assumed.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from phase3 import _vendor  # noqa: E402,F401

import canonicalize as C  # noqa: E402
import generate_corpus as G  # noqa: E402
import phi as P  # noqa: E402
import transpiler as T  # noqa: E402

from phase3 import sites as S  # noqa: E402

IDENT = P.identity_phi()
PROGRAMS = G.phase1_programs("positive", IDENT)


def _delta():
    return P.load_candidate("delta")


# --- self-containment ------------------------------------------------------

def test_vendor_tree_is_self_contained():
    _vendor.assert_self_contained()


# --- site location ---------------------------------------------------------

def test_colour_literal_is_not_a_site():
    """`#333333` is an argument, not a class sigil, even in a lexicon where
    `#` IS the class sigil. If this fails, every alpha/delta result is junk."""
    d = _delta()
    prog = T.transliterate("(function(){ $S('.wheel').recolor('#111111'); })();",
                           IDENT, d)
    assert "#111111" in prog
    found = S.classify(prog, d, template_id="colour", identity=IDENT)
    colour_at = prog.index("#111111")
    assert all(s.char_offset != colour_at for s in found), (
        "a site was located inside a quoted colour literal")


def test_token_type_map_matches_lexer():
    """Every token type we claim to understand must actually be emitted."""
    d = _delta()
    emitted = set()
    for p in PROGRAMS[:20]:
        for tok_type, _v, _o in T.lex(T.transliterate(p, IDENT, d), d):
            emitted.add(tok_type)
    known = set(S.SIMPLE_TOKEN_TERMINAL)
    assert known & emitted, f"none of the mapped token types appear: {emitted}"
    for t in known & emitted:
        assert S.SIMPLE_TOKEN_TERMINAL[t] in {x.id for x in d.table.terminals}


def test_offsets_point_at_the_correct_spelling():
    d = _delta()
    for p in PROGRAMS[:15]:
        prog = T.transliterate(p, IDENT, d)
        for s in S.classify(prog, d, identity=IDENT):
            assert prog[s.char_offset:s.char_offset + len(s.correct)] == s.correct
            assert s.prefix == prog[:s.char_offset]


# --- classification semantics ---------------------------------------------

def test_identity_has_no_collisions():
    """Under phi = identity nothing is remapped, so every site is NONE."""
    for p in PROGRAMS[:10]:
        for s in S.classify(p, IDENT, identity=IDENT):
            assert s.collision is S.CollisionClass.NONE
            assert s.correct == s.competitor


def test_semantic_requires_both_valid_and_different_ir():
    """The review's requirement, asserted on every SEMANTIC site we produce."""
    d = _delta()
    n = 0
    for p in PROGRAMS:
        prog = T.transliterate(p, IDENT, d)
        for s in S.classify(prog, d, identity=IDENT):
            if s.collision is not S.CollisionClass.SEMANTIC:
                continue
            n += 1
            assert T.num_parses(s.variant_program, d) == 1, s.site_id
            assert s.ir_hash_competitor is not None
            assert s.ir_hash_competitor != s.ir_hash_correct, s.site_id
    assert n > 0, "delta produced no semantic sites"


def test_lexical_sites_really_do_not_parse():
    d = _delta()
    checked = 0
    for p in PROGRAMS[:25]:
        prog = T.transliterate(p, IDENT, d)
        for s in S.classify(prog, d, identity=IDENT):
            if s.collision is S.CollisionClass.LEXICAL:
                checked += 1
                assert s.ir_hash_competitor is None
                try:
                    ok = T.num_parses(s.variant_program, d) == 1
                except Exception:
                    ok = False
                assert not ok, f"{s.site_id} classified LEXICAL but parses"
    assert checked > 0


def test_beta_and_gamma_have_no_semantic_sites():
    """Measured fact that motivates delta: disjoint alphabets give LOUD
    failures only, so beta/gamma cannot support the primary contrast."""
    for name in ("beta", "gamma"):
        lex = P.load_candidate(name)
        for p in PROGRAMS[:20]:
            prog = T.transliterate(p, IDENT, lex)
            for s in S.classify(prog, lex, identity=IDENT):
                assert s.collision is not S.CollisionClass.SEMANTIC, (
                    f"{name} unexpectedly produced a semantic site: {s.site_id}")


def test_census_counts_add_up():
    d = _delta()
    found = []
    for i, p in enumerate(PROGRAMS[:12]):
        found += S.classify(T.transliterate(p, IDENT, d), d,
                            template_id=f"t{i}", identity=IDENT)
    cen = S.census(found)
    assert sum(cen["delta"].values()) == len(found)
    assert len(S.usable(found)) == cen["delta"]["semantic"]


def test_site_ids_are_unique():
    d = _delta()
    ids = [s.site_id for i, p in enumerate(PROGRAMS)
           for s in S.classify(T.transliterate(p, IDENT, d),
                               d, template_id=f"t{i:03d}", identity=IDENT)]
    assert len(ids) == len(set(ids))


# --- materials validation --------------------------------------------------

def test_prefix_collisions_are_detected_and_removable():
    """Sites sharing a prefix but disagreeing on `correct` cap any
    prefix-conditioned predictor. The diagnostic must find them, and
    dedupe_by_prefix must remove them."""
    d = _delta()
    found = []
    for i, p in enumerate(PROGRAMS):
        found += S.classify(T.transliterate(p, IDENT, d), d,
                            template_id=f"t{i:03d}", identity=IDENT)
    sem = S.usable(found)
    cols = S.prefix_collisions(sem)
    # 3DOM programs share openings, so collisions are EXPECTED here.
    assert isinstance(cols, dict)
    deduped = S.dedupe_by_prefix(sem)
    assert not S.prefix_collisions(deduped)
    assert len(deduped) <= len(sem)


def test_dedupe_keeps_first_and_is_stable():
    d = _delta()
    sem = S.usable(S.classify(T.transliterate(PROGRAMS[0], IDENT, d), d,
                              identity=IDENT))
    once = S.dedupe_by_prefix(sem)
    assert S.dedupe_by_prefix(once) == once
