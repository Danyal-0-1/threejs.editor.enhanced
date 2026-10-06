"""h2.py — the prior x local-context interaction. EXPLORATORY, and NOT TESTABLE now.

H2 needs two calibrated factors: competitor prior strength T (neutral /
medium / strong) and local-context activation A (low / medium / high), built
from MATCHED context variants that share the AST and IR up to the decision.
Neither calibration exists in Phase 3.2 or 3.3. Inventing T and A levels from
outcome data would be circular (the review's §6.3: an activation score derived
from the same margin it is used to explain leaks the outcome).

So the honest output is NOT TESTABLE, with the reason. The machinery below is
real and tested on synthetic cells, so H2 can be run the day T/A calibration
exists:

    three preregistered scales      margin, logit P(revert), P(revert)
    expected directions             margin DiD < 0, logit/probability DiD > 0
    sign_agrees                     the DiD is interpretable only if all three
                                    point the same way (an ordinal interaction
                                    on one scale can vanish or flip on another)
"""

from __future__ import annotations

NOT_TESTABLE_REASON = ("no calibrated prior-strength (T) or local-context (A) "
                       "levels exist; deriving them from outcome margins would be "
                       "circular (review section 6.3)")

EXPECTED = {"did_margin": "negative", "did_logit": "positive", "did_prob": "positive"}


def evaluate(cells: dict | None) -> dict:
    """cells: {(T_level, A_level): [MarginRecord-like with .m_seq]} or None."""
    if not cells:
        return {"status": "NOT TESTABLE", "reason": NOT_TESTABLE_REASON,
                "expected_directions": EXPECTED}
    from phase3.scoring import interaction_did
    res = interaction_did(cells)
    return {"status": "EXPLORATORY",
            "did_margin": res.did_margin, "did_logit": res.did_logit,
            "did_prob": res.did_prob, "sign_agrees": res.sign_agrees,
            "verdict": res.verdict(), "n": res.n,
            "directions_as_expected": (res.did_margin < 0 and res.did_logit > 0
                                       and res.did_prob > 0),
            "expected_directions": EXPECTED}
