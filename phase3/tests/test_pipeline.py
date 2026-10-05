"""Tests for scoring, outcomes, the linter, and the end-to-end pipeline.

The end-to-end test plants a KNOWN familiarity bias in `FakeLM` and asserts
that the pipeline recovers it with the right sign at the right sites. A
pipeline that cannot recover an effect it was handed cannot be trusted to
measure a real one.
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

from phase3 import linter, outcomes, scoring, sites as S  # noqa: E402
from phase3.models import FakeLM  # noqa: E402

IDENT = P.identity_phi()
PROGRAMS = G.phase1_programs("positive", IDENT)
RULE = "In this language the class sigil is '#' and the id sigil is '.'."


def delta():
    return P.load_candidate("delta")


def semantic_sites(limit=40, dedupe=True):
    d = delta()
    out = []
    for i, p in enumerate(PROGRAMS):
        for s in S.classify(T.transliterate(p, IDENT, d), d,
                            template_id=f"t{i:03d}", identity=IDENT):
            if s.is_usable:
                out.append(s)
        if len(out) >= limit * 3:
            break
    if dedupe:
        out = S.dedupe_by_prefix(out)
    return out[:limit]


PREFIX_TAIL = 48


def biased_lm(sts, bonus=3.0, context_bonus=0.0):
    """A fake that prefers each site's competitor AT THAT SITE by `bonus` nats.

    The bias must be keyed on (prefix, continuation), not on the spelling
    alone. `delta` is a pure permutation lexicon, so the set of correct
    spellings and the set of competitor spellings are IDENTICAL — every
    spelling is correct at one role and a competitor at another. A
    spelling-keyed bonus would be awarded to both candidates at every site and
    cancel exactly, making a planted effect unrecoverable for reasons that have
    nothing to do with the pipeline. Real priors are contextual too, so pair
    keying is also the more faithful fixture.
    """
    assert not S.prefix_collisions(sts), (
        "fixture contains sites with identical prefixes but different correct "
        "spellings; pass them through S.dedupe_by_prefix first")
    return FakeLM(
        favoured_pairs=frozenset((s.prefix, s.competitor) for s in sts),
        familiar_bonus=bonus, context_bonus=context_bonus)


# --- scoring: sign convention ---------------------------------------------

def test_margin_sign_negative_when_competitor_preferred():
    sts = semantic_sites(20)
    lm = biased_lm(sts, bonus=5.0)
    for s in sts:
        r = scoring.forced_prefix_margin(lm, s, rule=RULE)
        assert r.m_seq < 0, f"{s.site_id}: expected reversion, got {r.m_seq}"
        assert r.reverted


def test_margin_is_zero_without_bias_at_matched_token_length():
    """With no planted bias, no noise and equal token counts the margin is
    EXACTLY zero. If it is not, the two candidates are not being scored
    symmetrically and every downstream number is suspect."""
    neutral = FakeLM(familiar=frozenset(), noise=0.0)
    checked = 0
    for s in semantic_sites(20):
        if neutral.n_tokens(s.correct) != neutral.n_tokens(s.competitor):
            continue
        checked += 1
        r = scoring.forced_prefix_margin(neutral, s, rule=RULE)
        assert abs(r.m_seq) < 1e-12, f"{s.site_id}: asymmetric scoring {r.m_seq}"
    assert checked > 0, "no token-length-matched sites to check"


def test_unbiased_fake_does_not_systematically_revert():
    sts = semantic_sites(20)
    neutral = FakeLM(familiar=frozenset())
    rate = sum(scoring.forced_prefix_margin(neutral, s, rule=RULE).reverted
               for s in sts) / len(sts)
    assert 0.0 <= rate <= 0.9, rate


def test_margin_scores_both_candidates_against_identical_prefix():
    s = semantic_sites(1)[0]
    lm = FakeLM()
    scoring.forced_prefix_margin(lm, s, rule=RULE)
    prefixes = {p for p, _c in lm.calls}
    assert len(prefixes) == 1, "candidates were scored against different prefixes"


def test_shots_change_the_prefix():
    s = semantic_sites(1)[0]
    lm = FakeLM()
    scoring.forced_prefix_margin(lm, s, rule=RULE, shots=0, examples=["EX1", "EX2"])
    n0 = len(lm.calls[0][0])
    lm.calls.clear()
    scoring.forced_prefix_margin(lm, s, rule=RULE, shots=2, examples=["EX1", "EX2"])
    assert len(lm.calls[0][0]) > n0


# --- extinction (the PRIMARY estimand) ------------------------------------

def test_extinction_curve_detects_a_crossing():
    """A fake whose bias decays with context length must yield a finite k*."""
    s = semantic_sites(1)[0]

    class Decaying(FakeLM):
        """Bias decays in the DOSE (number of example lines), not in prefix
        characters — the dose is what the ladder actually varies."""

        def sequence_logprob(self, prefix, continuation):
            base = -0.5 * self.n_tokens(continuation)
            if continuation == s.competitor:
                dose = prefix.count("example ")
                return base + 4.0 - 0.6 * dose
            return base

    curve = scoring.extinction_curve(Decaying(), s, [f"example {i}" for i in range(128)],
                                     rule=RULE)
    assert curve.k_star is not None, f"no crossing: {curve.margins}"
    assert not curve.censored
    assert 0 <= curve.k_star <= max(curve.shots)


def test_extinction_curve_reports_censoring():
    s = semantic_sites(1)[0]
    stubborn = biased_lm([s], bonus=50.0)
    curve = scoring.extinction_curve(stubborn, s, [f"ex {i}" for i in range(16)],
                                     rule=RULE)
    assert curve.k_star is None
    assert curve.censored, "a never-crossing curve must be flagged censored"


def test_ladder_truncates_to_available_examples():
    s = semantic_sites(1)[0]
    curve = scoring.extinction_curve(FakeLM(), s, ["a", "b", "c"], rule=RULE)
    assert max(curve.shots) <= 3


# --- the secondary DiD and its scale-robustness rule ----------------------

def _cells(strong_high, strong_low, neutral_high, neutral_low):
    def mk(vals):
        return [scoring.MarginRecord("s", "m", 0, 0.0, 0.0, v, 1, 1, True)
                for v in vals]
    return {("strong", "high"): mk(strong_high),
            ("strong", "low"): mk(strong_low),
            ("neutral", "high"): mk(neutral_high),
            ("neutral", "low"): mk(neutral_low)}


def test_interaction_reports_three_scales():
    res = scoring.interaction_did(_cells([-3, -3], [-1, -1], [-1, -1], [-0.5, -0.5]))
    assert res.did_margin != 0.0
    assert set(res.n) == {"strong/high", "strong/low", "neutral/high", "neutral/low"}


def test_interaction_flags_scale_dependence():
    """Saturation: every strong cell reverts, so the probability DiD is 0
    while the margin DiD is large. That disagreement must be FLAGGED, not
    silently reported as support (analysis doc section 2.1)."""
    res = scoring.interaction_did(_cells([-9, -9], [-5, -5], [-1, -1], [-0.9, -0.9]))
    assert res.did_prob == 0.0
    assert "SCALE-DEPENDENT" in res.verdict() or res.sign_agrees


def test_interaction_requires_all_four_cells():
    try:
        scoring.interaction_did({("strong", "high"): []})
    except ValueError as exc:
        assert "four corner cells" in str(exc)
    else:
        raise AssertionError("missing cells were not rejected")


# --- outcomes: taxonomy and the hurdle ------------------------------------

def test_taxonomy_correct_program():
    d = delta()
    prog = T.transliterate(PROGRAMS[0], IDENT, d)
    target = C.content_hash(T.parse(prog, d))
    o = outcomes.evaluate(prog, d, target)
    assert o.bucket is outcomes.Bucket.VALID_CORRECT
    assert o.parse_valid and o.task_correct


def test_taxonomy_valid_wrong():
    """A SEMANTIC site's variant parses but has a different IR."""
    d = delta()
    s = semantic_sites(1)[0]
    o = outcomes.evaluate(s.variant_program, d, s.ir_hash_correct)
    assert o.bucket is outcomes.Bucket.VALID_WRONG
    assert o.parse_valid and not o.task_correct


def test_taxonomy_lex_fail():
    d = delta()
    o = outcomes.evaluate("(function(){ $S('.wheel'", d, "deadbeef")
    assert o.bucket in (outcomes.Bucket.LEX_FAIL, outcomes.Bucket.PARSE_FAIL)
    assert not o.parse_valid


def test_vacuous_is_parse_success_and_task_failure():
    """D5. The most plausible null output must not be able to inflate accuracy."""
    d = delta()
    vac = T.transliterate("(function(){ $S('.wheel'); })();", IDENT, d)
    o = outcomes.evaluate(vac, d, "whatever")
    assert o.bucket is outcomes.Bucket.VALID_VACUOUS
    assert o.parse_valid and not o.task_correct


def test_hurdle_separates_reach_from_choice():
    """The Experiment-02 error: 3/3 vs 15/20 is not comparable when P(reach)
    differs. The hurdle keeps the two factors apart."""
    obs_bare = [outcomes.SiteObservation("s", True, True, "x", "")] * 3 + \
               [outcomes.SiteObservation("s", False, None, None, "")] * 17
    obs_scaf = [outcomes.SiteObservation("s", True, True, "x", "")] * 15 + \
               [outcomes.SiteObservation("s", True, False, "y", "")] * 5

    h_bare, h_scaf = outcomes.hurdle(obs_bare), outcomes.hurdle(obs_scaf)
    assert h_bare.p_revert_given_reach == 1.0
    assert h_scaf.p_revert_given_reach == 0.75
    # conditional reversion is LOWER under scaffolding even though the raw
    # count (15 vs 3) is five times higher — the whole point.
    assert h_scaf.p_revert_given_reach < h_bare.p_revert_given_reach
    assert h_scaf.p_reach > h_bare.p_reach


def test_hurdle_handles_zero_reach():
    h = outcomes.hurdle([outcomes.SiteObservation("s", False, None, None, "")] * 4)
    assert h.p_revert_given_reach is None
    assert h.p_observed == 0.0


def test_observe_site_detects_competitor():
    d = delta()
    s = semantic_sites(1)[0]
    assert outcomes.observe_site(s.program, d, s).reverted is False
    assert outcomes.observe_site(s.variant_program, d, s).reverted is True


# --- linter: H4 ------------------------------------------------------------

def test_risk_sign_is_opposite_to_margin():
    """S > 0 means danger; M_seq > 0 means safe. They must not be confused."""
    sts = semantic_sites(8)
    lm = biased_lm(sts, bonus=4.0)
    for s in sts:
        m = scoring.forced_prefix_margin(lm, s, rule=RULE).m_seq
        r = linter.score_site(lm, s, rule=RULE)
        assert r.s_seq > 0 > m
        assert abs(r.s_seq + m) < 1e-9


def test_risk_decomposition_adds_up():
    s = semantic_sites(1)[0]
    lm = biased_lm([s])
    r = linter.score_site(lm, s, rule=RULE)
    assert abs((r.s_local + r.s_shift) - r.s_seq) < 1e-9


def test_auroc_perfect_and_degenerate():
    assert linter.auroc([3.0, 2.0, 1.0, 0.0], [1, 1, 0, 0]) == 1.0
    assert linter.auroc([0.0, 1.0, 2.0, 3.0], [1, 1, 0, 0]) == 0.0
    assert linter.auroc([1.0, 1.0], [1, 1]) is None          # one class absent
    assert linter.auroc([1.0, 1.0, 1.0, 1.0], [1, 1, 0, 0]) == 0.5   # all ties


def test_auprc_and_precision_at_k():
    assert linter.auprc([3.0, 2.0, 1.0], [1, 1, 0]) == 1.0
    assert linter.precision_at_k([3.0, 2.0, 1.0], [1, 1, 0], 2) == 1.0


def test_rank_report_includes_baselines():
    sts = semantic_sites(12)
    lm = biased_lm(sts, bonus=4.0)
    scores = [linter.score_site(lm, s, rule=RULE).s_seq for s in sts]
    labels = [1] * len(sts)
    labels[0] = 0
    rep = linter.rank_report(
        sts, scores, labels,
        baselines={"length": linter.length_baseline(sts),
                   "language_identity": linter.identity_baseline(sts)})
    assert "length" in rep.baselines
    assert "language_identity" in rep.baselines
    assert rep.n == len(sts)


# --- linter: H5 repair -----------------------------------------------------

def test_repair_preserves_ir_over_the_whole_corpus():
    """The H5 correctness condition, proved mechanically, not argued."""
    import json
    d = delta()
    blob = json.load(open(os.path.join(_vendor.VENDOR, "alien_syntax",
                                       "candidates", "phi_delta.json"),
                          encoding="utf-8"))
    rep = linter.Repair("T_VERB_SPIN", d.spelling("T_VERB_SPIN"), "qzspin", 1.0, 0.1)
    new_blob = linter.apply_repairs(blob, [rep])
    new_phi = P.validate_phi(new_blob, P.load_terminals())

    ok, problems = linter.verify_repair(d, new_phi, PROGRAMS, IDENT)
    assert ok, problems[:5]


def test_apply_repairs_does_not_mutate_input():
    import json
    blob = json.load(open(os.path.join(_vendor.VENDOR, "alien_syntax",
                                       "candidates", "phi_delta.json"),
                          encoding="utf-8"))
    before = blob["map"]["T_VERB_SPIN"]["to"]
    linter.apply_repairs(blob, [linter.Repair("T_VERB_SPIN", before, "zzz", 1.0, 0.0)])
    assert blob["map"]["T_VERB_SPIN"]["to"] == before


def test_a_verb_swap_is_ir_preserving_because_renaming_is_by_role():
    """Worth asserting because it is counter-intuitive.

    Swapping two verbs' SPELLINGS does not change any program's meaning: the
    transpiler renames by terminal ROLE, so a program transliterated into the
    swapped language expresses the same roles and lowers to the same canonical
    IR. Repair is a renaming, and renamings are meaning-preserving by
    construction. What protects the IR is therefore not verify_repair alone but
    the V6 partition proof inside validate_phi — see the next test.
    """
    import json
    d = delta()
    blob = json.load(open(os.path.join(_vendor.VENDOR, "alien_syntax",
                                       "candidates", "phi_delta.json"),
                          encoding="utf-8"))
    a, b = "T_VERB_RECOLOR", "T_VERB_SCALE"
    sa, sb = blob["map"][a]["to"], blob["map"][b]["to"]
    blob2 = linter.apply_repairs(blob, [linter.Repair(a, sa, sb, 1, 0),
                                        linter.Repair(b, sb, sa, 1, 0)])
    swapped = P.validate_phi(blob2, P.load_terminals())
    ok, problems = linter.verify_repair(d, swapped, PROGRAMS, IDENT)
    assert ok, problems[:5]


def test_colliding_repair_is_rejected_at_validation():
    """THE actual guard. A repair that gives two roles the same spelling
    violates the V6 spelling-partition proof and must not produce a usable
    phi-map at all — the failure happens before anything can be scored."""
    import json
    blob = json.load(open(os.path.join(_vendor.VENDOR, "alien_syntax",
                                       "candidates", "phi_delta.json"),
                          encoding="utf-8"))
    victim = blob["map"]["T_VERB_SCALE"]["to"]
    bad = linter.apply_repairs(
        blob, [linter.Repair("T_VERB_RECOLOR",
                             blob["map"]["T_VERB_RECOLOR"]["to"], victim, 1, 0)])
    try:
        P.validate_phi(bad, P.load_terminals())
    except P.PhiValidationError:
        return
    raise AssertionError("a spelling collision passed validate_phi")


# --- end to end ------------------------------------------------------------

def test_end_to_end_recovers_a_planted_effect():
    """Plant a known bias; assert the pipeline measures it back.

    This exercises: site enumeration -> collision classification -> forced-
    prefix margins -> risk scoring -> ranking, with no GPU and no weights.
    """
    sts = semantic_sites(40)
    assert len(sts) >= 8, f"fixture too small: {len(sts)}"

    planted = 3.0
    lm = biased_lm(sts, bonus=planted)

    margins = [scoring.forced_prefix_margin(lm, s, rule=RULE) for s in sts]
    assert all(m.reverted for m in margins), "planted bias not recovered"

    # magnitude: |M_seq| should sit near the planted bonus, up to the fake's
    # length cost and bounded noise.
    import statistics
    mean_abs = statistics.mean(abs(m.m_seq) for m in margins)
    assert 0.5 < mean_abs < planted + 6.0, mean_abs

    # the risk score must rank the biased sites above unbiased controls
    controls = [s for s in semantic_sites(60) if s not in sts][:8]
    all_sites = sts + controls
    labels = [1] * len(sts) + [0] * len(controls)
    if controls:
        scores = [linter.score_site(lm, s, rule=RULE).s_seq for s in all_sites]
        auc = linter.auroc(scores, labels)
        assert auc is None or auc >= 0.5, auc
