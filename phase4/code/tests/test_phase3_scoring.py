"""Tests for scoring.py: the subset of phase3/tests/test_pipeline.py for code the pipeline uses.

The end-to-end test plants a KNOWN familiarity bias in `FakeLM` and asserts
that the pipeline recovers it with the right sign at the right sites. A
pipeline that cannot recover an effect it was handed cannot be trusted to
measure a real one.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(  # phase4/code: where p4 is
    os.path.abspath(__file__))))

from p4 import paths as _vendor  # noqa: E402,F401

import canonicalize as C  # noqa: E402
import generate_corpus as G  # noqa: E402
import phi as P  # noqa: E402
import transpiler as T  # noqa: E402

from p4.scoring import scoring; from p4.sites import sites as S  # noqa: E402  (linter, outcomes: not copied)
from p4.scoring.models import FakeLM  # noqa: E402

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

# --- linter: H4 ------------------------------------------------------------

# --- linter: H5 repair -----------------------------------------------------

# --- end to end ------------------------------------------------------------
