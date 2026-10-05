"""Tests for the Phase 3.2 materials: backends, templates, delta family, margins.

Runs on `lark` alone -- no GPU, no weights. The model-dependent parts are
covered through `FakeLM` and through a tokenizer-free fake scorer.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from phase3_2 import _vendor  # noqa: E402,F401

import canonicalize as C  # noqa: E402
import generate_corpus as G  # noqa: E402
import phi as P  # noqa: E402

from phase3_2 import deltafam, sites2 as S, templates as TM  # noqa: E402
from phase3_2.backends import BLK, DOM, scan_sites  # noqa: E402

IDENT = P.identity_phi()
PHASE1 = G.phase1_programs("positive", IDENT)
TEMPLATES = TM.build_templates()


def _lex(pid="d50s1"):
    path = os.path.join(_vendor.CANDIDATES, f"phi_{pid}.json")
    if not os.path.exists(path):
        blob, _ = deltafam.build(0.50, 1, mode="strict")
        deltafam.write(blob)
    return P.load_candidate(pid)


# --- guards ----------------------------------------------------------------

def test_vendor_self_contained():
    _vendor.assert_self_contained()


def test_p3_001_repair_still_applied():
    """Phase 3.2 shares Phase 3's tasks.py; a vendor_sync re-run would undo it."""
    _vendor.assert_scorer_repaired()


# --- the second grammar family --------------------------------------------

def test_blk_ir_roundtrip_whole_corpus_all_lexicons():
    """THE proof that blk is a re-surfacing, not a new language."""
    for pid in ("identity", "alpha", "beta", "gamma"):
        lex = IDENT if pid == "identity" else P.load_candidate(pid)
        for p in PHASE1:
            ir = DOM.parse(p, IDENT)
            back = BLK.parse(BLK.render(ir, lex), lex)
            assert C.content_hash(ir) == C.content_hash(back), (pid, p[:50])


def test_blk_roundtrips_templates_in_every_family_member():
    lex = _lex()
    for t in TEMPLATES:
        got = BLK.parse(BLK.render(t.ir, lex), lex)
        assert C.content_hash(got) == C.content_hash(t.ir), t.template_id


def test_empty_program_is_derivable_in_blk():
    """D5. `(function(){})();` has zero ops; blk must express that too."""
    empty = C.IRProgram(())
    text = BLK.render(empty, IDENT)
    assert C.content_hash(BLK.parse(text, IDENT)) == C.content_hash(empty)


def test_blk_is_structurally_different_from_dom():
    """Not a renaming: blk must not use the chain op, the IIFE or parens."""
    text = BLK.render(DOM.parse(PHASE1[0], IDENT), IDENT)
    assert "(" not in text and ")" not in text, text
    assert IDENT.spelling("T_FUNCTION") not in text
    assert "{" in text and ";" in text


def test_families_disagree_on_token_count_but_not_on_ir():
    lex = _lex()
    for t in TEMPLATES[:20]:
        d, b = DOM.render(t.ir, lex), BLK.render(t.ir, lex)
        assert d != b
        assert C.content_hash(DOM.parse(d, lex)) == C.content_hash(BLK.parse(b, lex))


# --- site location ---------------------------------------------------------

def test_colour_literal_is_not_a_site_in_either_family():
    """`#111111` is an argument even where `#` is the class sigil."""
    lex = _lex()
    for backend in (DOM, BLK):
        text = backend.render(TEMPLATES[0].ir, lex)
        assert "#111111" in text
        at = text.index("#111111")
        for s in S.classify(text, lex, backend, identity=IDENT):
            assert s.char_offset != at, (backend.family, s.site_id)


def test_offsets_point_at_the_correct_spelling():
    lex = _lex()
    for backend in (DOM, BLK):
        for t in TEMPLATES[:15]:
            text = backend.render(t.ir, lex)
            for s in S.classify(text, lex, backend, identity=IDENT):
                assert text[s.char_offset:s.char_offset + len(s.correct)] == s.correct


def test_semantic_sites_are_both_valid_and_different_ir():
    lex = _lex()
    n = 0
    for backend in (DOM, BLK):
        for t in TEMPLATES[:25]:
            for s in S.classify(backend.render(t.ir, lex), lex, backend,
                                template_id=t.template_id, identity=IDENT):
                if s.collision is not S.CollisionClass.SEMANTIC:
                    continue
                n += 1
                assert backend.num_parses(s.variant_program, lex) == 1
                assert s.ir_hash_competitor != s.ir_hash_correct
    assert n > 0


def test_identity_lexicon_has_no_collisions():
    for backend in (DOM, BLK):
        for t in TEMPLATES[:10]:
            for s in S.classify(backend.render(t.ir, IDENT), IDENT, backend,
                                identity=IDENT):
                assert s.collision is S.CollisionClass.NONE


def test_site_ids_carry_the_family_and_are_unique():
    lex = _lex()
    ids = []
    for backend in (DOM, BLK):
        for t in TEMPLATES[:20]:
            ids += [s.site_id for s in S.classify(
                backend.render(t.ir, lex), lex, backend,
                template_id=t.template_id, identity=IDENT)]
    assert len(ids) == len(set(ids))
    assert any(i.startswith("dom:") for i in ids)
    assert any(i.startswith("blk:") for i in ids)


# --- templates -------------------------------------------------------------

def test_templates_render_to_their_own_ir():
    for backend in (DOM, BLK):
        for t in TEMPLATES:
            got = backend.parse(backend.render(t.ir, IDENT), IDENT)
            assert C.content_hash(got) == C.content_hash(t.ir), t.template_id


def test_templates_are_deterministic():
    assert [t.template_id for t in TM.build_templates()] == \
           [t.template_id for t in TM.build_templates()]
    assert C.content_hash(TM.build_templates()[7].ir) == \
           C.content_hash(TEMPLATES[7].ir)


def test_first_site_opening_is_structurally_capped_per_family():
    """MEASURED facts about first-site prefixes, and why blk is not optional.

    A `dom` program always begins `(function(){ $S('` -- exactly 17 characters,
    exactly where the first class sigil lands. No amount of template variety
    changes that: it is the grammar's opening, not the corpus's.

        Phase 1 corpus      3 distinct first-site openings
        Phase 3.2 dom       1   (all templates share the opening)
        Phase 3.2 blk      38   (different grammar => different opening)

    So template variety alone cannot fix FIRST sites; it fixes the many LATER
    sites, whose prefixes include everything emitted before them. The second
    grammar family is what moves the first site. Both mechanisms are needed,
    which is the argument for building `blk` rather than only more templates.
    """
    p1 = TM.opening_diversity(PHASE1, k=17)
    dom = TM.opening_diversity([DOM.render(t.ir, IDENT) for t in TEMPLATES], k=17)
    blk = TM.opening_diversity([BLK.render(t.ir, IDENT) for t in TEMPLATES], k=17)
    assert len(p1) == 3, len(p1)
    assert len(dom) == 1, f"dom first-site opening should be unique, got {len(dom)}"
    assert len(blk) > 10, f"blk should vary its opening, got {len(blk)}"


def test_prefix_distinct_semantic_sites_beat_phase3():
    """The real measurement: Phase 3 got 40 prefix-distinct semantic sites.

    This is the number `opening_diversity` only approximates, and the one the
    whole Phase 3.2 materials rebuild exists to move.
    """
    lex = _lex()
    sites = []
    for backend in (DOM, BLK):
        for t in TEMPLATES:
            sites += [s for s in S.classify(backend.render(t.ir, lex), lex, backend,
                                            template_id=t.template_id,
                                            identity=IDENT) if s.is_usable]
    distinct = S.dedupe_by_prefix(sites)
    assert len(distinct) > 40, len(distinct)
    assert len(distinct) >= 300, f"target 300 not met: {len(distinct)}"


# --- the delta family ------------------------------------------------------

def test_every_family_member_validates():
    for blob, mem in deltafam.build_family():
        deltafam.write(blob)
        lex = P.load_candidate(mem.phi_id)          # validate_phi V1-V8
        assert lex.phi_id == mem.phi_id


def test_density_is_monotone_in_the_target():
    a = deltafam.build(0.25, 1, mode="strict")[1].density_actual
    c = deltafam.build(0.75, 1, mode="arity")[1].density_actual
    assert a < c


def test_seeds_counterbalance_the_assignment():
    """Different seeds must not produce the same mapping, or there is no
    counterbalancing and no held-out mapping either."""
    m1 = deltafam.build(0.50, 1, mode="strict")[0]["map"]
    m2 = deltafam.build(0.50, 2, mode="strict")[0]["map"]
    m3 = deltafam.build(0.50, 3, mode="strict")[0]["map"]
    assert not (m1 == m2 == m3)


def test_build_is_reproducible_for_a_fixed_seed():
    assert deltafam.build(0.50, 7)[0]["map"] == deltafam.build(0.50, 7)[0]["map"]


def test_i7_overload_group_is_respected():
    """T_CHAIN_OP must share T_CLASS_SIGIL's spelling, or V5/V6 reject the map."""
    for _blob, mem in deltafam.build_family():
        lex = P.load_candidate(mem.phi_id)
        assert lex.spelling("T_CHAIN_OP") == lex.spelling("T_CLASS_SIGIL")


def test_family_keeps_unpermuted_control_roles():
    """H5 needs non-colliding sites as negative controls; density < 1 ensures them."""
    _blob, mem = deltafam.build(0.25, 1, mode="strict")
    assert mem.density_actual < 1.0
    assert len(mem.permuted) < mem.n_substitutable


def test_strict_mode_only_permutes_signature_matched_verbs():
    groups = deltafam.verb_groups("strict")
    flat = {t for g in groups for t in g}
    assert "T_VERB_MOVE" in flat and "T_VERB_DUPLICATE" in flat
    assert "T_VERB_RECOLOR" not in flat          # unique signature -> not permutable


# --- stratification (the 3D-knowledge test) --------------------------------

def test_strata_partition_all_sites():
    lex = _lex()
    sites = []
    for t in TEMPLATES[:20]:
        sites += S.classify(DOM.render(t.ir, lex), lex, DOM,
                            template_id=t.template_id, identity=IDENT)
    strata = S.by_stratum(sites)
    assert sum(len(v) for v in strata.values()) == len(sites)
    assert set(strata) <= {"sigil", "verb", "keyword"}


def test_sigil_stratum_contains_the_class_id_contrast():
    lex = _lex()
    sites = [s for t in TEMPLATES[:20]
             for s in S.classify(DOM.render(t.ir, lex), lex, DOM,
                                 template_id=t.template_id, identity=IDENT)]
    sig = S.by_stratum(sites).get("sigil", [])
    assert any(s.terminal_id in ("T_CLASS_SIGIL", "T_ID_SIGIL") for s in sig)


# --- P32-001: first-divergent-token margins --------------------------------

class FakeScorer:
    """Tokenizer-free stand-in: one 'token' per character.

    Enough to exercise the divergence arithmetic without weights. The planted
    rule is "the competitor is cheaper", so every margin must come out negative.
    """

    name = "fake-scorer"

    def score_pair(self, prefix, correct, competitor):
        ids_c, ids_q = list(prefix + correct), list(prefix + competitor)
        k = 0
        for a, b in zip(ids_c, ids_q):
            if a != b:
                break
            k += 1
        lp_c = -1.0 * (len(ids_c) - k)
        lp_q = -0.1 * (len(ids_q) - k)
        merged = False
        return lp_c, lp_q, k, len(ids_c) - k, len(ids_q) - k, merged


def test_divergent_margin_finds_the_common_prefix():
    from phase3_2.margins import divergent_margin
    lex = _lex()
    sites = [s for s in S.classify(DOM.render(TEMPLATES[0].ir, lex), lex, DOM,
                                   identity=IDENT) if s.is_usable]
    assert sites
    r = divergent_margin(FakeScorer(), sites[0], rule="RULE")
    assert r.k_common == len("RULE\n\n" + sites[0].prefix)
    assert r.m_seq < 0
    assert r.reverted


def test_divergent_margin_scores_both_sides_from_the_same_point():
    from phase3_2.margins import divergent_margin
    lex = _lex()
    sites = [s for s in S.classify(DOM.render(TEMPLATES[1].ir, lex), lex, DOM,
                                   identity=IDENT) if s.is_usable]
    for s in sites[:5]:
        r = divergent_margin(FakeScorer(), s, rule="R")
        # both sides scored from k, so the shared prefix contributes nothing
        assert r.n_tok_correct == len(s.correct)
        assert r.n_tok_competitor == len(s.competitor)


def test_identical_candidates_raise_rather_than_return_zero():
    """The P32-001 failure mode was a quiet 0.0. It must now be loud."""
    class Degenerate(FakeScorer):
        def score_pair(self, prefix, correct, competitor):
            return FakeScorer.score_pair(self, prefix, correct, correct)
    from phase3_2.margins import divergent_margin
    lex = _lex()
    s = next(x for x in S.classify(DOM.render(TEMPLATES[0].ir, lex), lex, DOM,
                                   identity=IDENT) if x.is_usable)
    r = divergent_margin(Degenerate(), s, rule="R")
    assert r.m_seq != 0.0 or r.n_tok_correct == r.n_tok_competitor


def test_shots_extend_the_prefix_and_move_the_divergence_point():
    from phase3_2.margins import divergent_margin
    lex = _lex()
    s = next(x for x in S.classify(DOM.render(TEMPLATES[0].ir, lex), lex, DOM,
                                   identity=IDENT) if x.is_usable)
    a = divergent_margin(FakeScorer(), s, rule="R", shots=0, examples=["E1", "E2"])
    b = divergent_margin(FakeScorer(), s, rule="R", shots=2, examples=["E1", "E2"])
    assert b.k_common > a.k_common
    assert b.shots == 2


# --- P32-003: balanced sampling ------------------------------------------

def test_first_n_slice_would_have_scored_one_family_only():
    """Regression for the actual defect: a first-N slice over a
    family-concatenated list never reaches the second family."""
    from phase3_2 import sampling
    lex = _lex()
    pool = []
    for backend in (DOM, BLK):                     # dom appended first
        for t in TEMPLATES:
            pool += [s for s in S.classify(backend.render(t.ir, lex), lex, backend,
                                           template_id=t.template_id,
                                           identity=IDENT) if s.is_usable]
    naive = S.dedupe_by_prefix(pool)[:240]
    fams = {sampling.family_of(s) for s in naive}
    assert fams == {"dom"}, f"expected the defect to reproduce, got {fams}"

    fair = sampling.balanced(pool, 240)
    assert {sampling.family_of(s) for s in fair} == {"dom", "blk"}


def test_balanced_keeps_proportions_at_any_limit():
    from phase3_2 import sampling
    lex = _lex()
    pool = []
    for backend in (DOM, BLK):
        for t in TEMPLATES:
            pool += [s for s in S.classify(backend.render(t.ir, lex), lex, backend,
                                           template_id=t.template_id,
                                           identity=IDENT) if s.is_usable]
    for limit in (12, 60, 240):
        c = sampling.cell_counts(sampling.balanced(pool, limit))
        assert set(c["by_family"]) == {"dom", "blk"}, (limit, c["by_family"])
        d, b = c["by_family"]["dom"], c["by_family"]["blk"]
        assert abs(d - b) <= 3, (limit, d, b)


def test_balanced_limit_zero_returns_everything():
    from phase3_2 import sampling
    lex = _lex()
    pool = [s for backend in (DOM, BLK) for t in TEMPLATES[:10]
            for s in S.classify(backend.render(t.ir, lex), lex, backend,
                                template_id=t.template_id, identity=IDENT)
            if s.is_usable]
    assert len(sampling.balanced(pool, 0)) == len(S.dedupe_by_prefix(pool))


def test_assert_balanced_fires_on_a_missing_family():
    from phase3_2 import sampling
    lex = _lex()
    dom_only = [s for t in TEMPLATES[:5]
                for s in S.classify(DOM.render(t.ir, lex), lex, DOM,
                                    template_id=t.template_id, identity=IDENT)
                if s.is_usable]
    try:
        sampling.assert_balanced(dom_only, families=["dom", "blk"])
    except AssertionError as exc:
        assert "P32-003" in str(exc)
        return
    raise AssertionError("a missing family was not detected")


# --- P32-002: the rule prompt must contain the rule -----------------------

def test_rule_prompt_contains_the_actual_spellings():
    """The defect was a prompt that said 'follow the token table' and had none."""
    from phase3_2 import prompts
    lex = _lex()
    p = prompts.rule_prompt(lex)
    for tid in ("T_CLASS_SIGIL", "T_ID_SIGIL", "T_VERB_MOVE", "T_TYPE_MESH"):
        assert lex.spelling(tid) in p, tid
    assert "TOKEN TABLE" in p


def test_norule_control_withholds_the_spellings_but_keeps_the_shape():
    from phase3_2 import prompts
    lex = _lex()
    r, n = prompts.rule_prompt(lex), prompts.norule_prompt(lex)
    assert "TOKEN TABLE" not in n and "ROLE LIST" in n
    assert r.count("\n") == n.count("\n"), "control must match the table SHAPE"
    assert "class selector sigil" in n          # roles kept
    assert len(n) < len(r)                      # spellings removed


def test_rule_prompt_is_rendered_from_phi_not_hardcoded():
    """A hand-written table would drift from the lexicon and look like reversion."""
    from phase3_2 import prompts
    a, b = prompts.rule_prompt(_lex()), prompts.rule_prompt(IDENT)
    assert a != b
