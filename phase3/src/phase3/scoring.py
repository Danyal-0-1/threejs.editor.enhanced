"""scoring.py — forced-prefix margins (Arm A) and the extinction ladder.

SIGN CONVENTION, fixed here and used everywhere in Phase 3:

    M_seq = log P(c | r, x) - log P(q | r, x)

    M_seq > 0   the model prefers the SPECIFIED DSL token      (good)
    M_seq < 0   the model prefers the FAMILIAR competitor      (reversion)

`c` is the correct spelling at the site, `q` the familiar competitor, `r` the
remote specification (the prompt text that defines the mapping) and `x` the
exact program prefix immediately before the decision.

Two distinct quantities must never be conflated, so they never share a name:

    M_seq   full-sequence log-probability margin  (this module; behavioural)
    G_tok   single-next-token LOGIT margin        (mechanistic phase only)

They coincide only when both candidates are exactly one token. `castShadow`
vs `receiveShadow` are not, so Phase 3's behavioural endpoint is M_seq.

----------------------------------------------------------------------------
THE PRIMARY ESTIMAND IS THE EXTINCTION THRESHOLD, NOT A DIFFERENCE OF
DIFFERENCES
----------------------------------------------------------------------------
`hypothesis_strength_and_compute_analysis.md` §2.1 argues that an ordinal
interaction measured on a log-probability margin is partly an artifact of the
scale: two factors that both push the same way generically produce
"super-additivity" under a compressive nonlinearity, with no mechanism behind
it. A difference-in-differences cannot distinguish the two.

Phase 3's primary estimand is therefore the EXTINCTION THRESHOLD

    k*(site) = the smallest number of in-context examples at which
               M_seq crosses from negative to positive

read off the dose-response curve by `extinction_curve`. A threshold on the
x-axis is far more robust to monotone rescaling of the y-axis than a contrast
between two gaps on it. The A x T difference-in-differences is retained as a
SECONDARY contrast (`interaction_did`) and is reported on three scales, with
the preregistered rule that its sign must agree on all of them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Sequence

from phase3.models import LM
from phase3.sites import Site

# ---------------------------------------------------------------------------
# Arm A — forced-prefix margin
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MarginRecord:
    site_id: str
    model: str
    shots: int
    logp_correct: float
    logp_competitor: float
    m_seq: float                     # logp_correct - logp_competitor
    n_tok_correct: int
    n_tok_competitor: int
    rule_present: bool

    @property
    def reverted(self) -> bool:
        """Teacher-forced reversion: the competitor is preferred at this site."""
        return self.m_seq < 0.0

    # --- sensitivity analyses; NEVER the primary -------------------------
    @property
    def m_per_token(self) -> float:
        return (self.logp_correct / max(self.n_tok_correct, 1)
                - self.logp_competitor / max(self.n_tok_competitor, 1))


def forced_prefix_margin(model: LM, site: Site, *, rule: str = "",
                         shots: int = 0, examples: Sequence[str] = ()) -> MarginRecord:
    """Score both candidates against the IDENTICAL prefix and return M_seq.

    The prefix handed to the model is

        rule  +  k examples  +  site.prefix

    and the two candidates are scored against exactly that same string. Any
    asymmetry between the two scoring calls would be a confound, so the prefix
    is built once and reused rather than reconstructed per candidate.
    """
    shown = list(examples[:shots])
    ctx = ""
    if rule:
        ctx += rule.rstrip() + "\n\n"
    for ex in shown:
        ctx += ex.rstrip() + "\n"
    if shown:
        ctx += "\n"
    prefix = ctx + site.prefix

    lp_c = model.sequence_logprob(prefix, site.correct)
    lp_q = model.sequence_logprob(prefix, site.competitor)
    return MarginRecord(
        site_id=site.site_id, model=model.name, shots=len(shown),
        logp_correct=lp_c, logp_competitor=lp_q, m_seq=lp_c - lp_q,
        n_tok_correct=model.n_tokens(site.correct),
        n_tok_competitor=model.n_tokens(site.competitor),
        rule_present=bool(rule),
    )


# ---------------------------------------------------------------------------
# the PRIMARY estimand: extinction / dose-response
# ---------------------------------------------------------------------------

DEFAULT_LADDER: tuple[int, ...] = (0, 1, 2, 4, 8, 16, 32, 64, 128)


@dataclass
class ExtinctionCurve:
    site_id: str
    model: str
    shots: tuple[int, ...]
    margins: tuple[float, ...]
    k_star: float | None             # interpolated crossing; None = never crosses
    censored: bool                   # True => still negative at the last rung

    def as_row(self) -> dict:
        return {"site_id": self.site_id, "model": self.model,
                "shots": list(self.shots), "margins": list(self.margins),
                "k_star": self.k_star, "censored": self.censored}


def _interpolate_crossing(xs: Sequence[int], ys: Sequence[float]) -> float | None:
    """First upward zero crossing of y(x), linearly interpolated in x.

    Interpolated, not snapped to a rung, because the rungs are geometric
    (0,1,2,4,…): snapping would quantise k* into buckets whose width grows with
    k and manufacture ties between sites that are far apart. Returns None when
    the curve never crosses, and the caller must treat that as CENSORED rather
    than as a large k* — dropping censored sites would bias k* downward exactly
    where the prior is strongest.
    """
    for i in range(1, len(xs)):
        y0, y1 = ys[i - 1], ys[i]
        if y0 < 0.0 <= y1:
            if y1 == y0:
                return float(xs[i])
            t = (0.0 - y0) / (y1 - y0)
            return float(xs[i - 1]) + t * (float(xs[i]) - float(xs[i - 1]))
    return None


def extinction_curve(model: LM, site: Site, examples: Sequence[str], *,
                     rule: str = "", ladder: Sequence[int] = DEFAULT_LADDER
                     ) -> ExtinctionCurve:
    """M_seq as a function of the number of in-context examples.

    `examples` must be long enough for the top rung; rungs beyond
    `len(examples)` are not scored, so a short example pool silently truncates
    the ladder rather than repeating examples (repetition would change the
    estimand from "more evidence" to "more repetition").
    """
    rungs = tuple(k for k in ladder if k <= len(examples))
    ys = tuple(forced_prefix_margin(model, site, rule=rule, shots=k,
                                    examples=examples).m_seq for k in rungs)
    k_star = _interpolate_crossing(rungs, ys)
    return ExtinctionCurve(site_id=site.site_id, model=model.name, shots=rungs,
                           margins=ys, k_star=k_star,
                           censored=bool(ys) and ys[-1] < 0.0)


# ---------------------------------------------------------------------------
# SECONDARY: the A x T difference-in-differences, on three scales
# ---------------------------------------------------------------------------

def _logit(p: float, eps: float = 1e-6) -> float:
    p = min(max(p, eps), 1.0 - eps)
    return math.log(p / (1.0 - p))


@dataclass(frozen=True)
class InteractionResult:
    did_margin: float            # on M_seq (unbounded)
    did_logit: float             # on logit P(revert)
    did_prob: float              # on P(revert) itself
    n: dict[str, int]
    sign_agrees: bool            # the preregistered robustness rule

    def verdict(self) -> str:
        if not self.sign_agrees:
            return ("SCALE-DEPENDENT: the interaction changes sign across "
                    "scales, so it is not interpretable as a mechanism "
                    "(analysis doc section 2.1).")
        return "sign agrees on all three scales"


def interaction_did(cells: dict[tuple[str, str], Sequence[MarginRecord]]
                    ) -> InteractionResult:
    """Difference-in-differences over the four corner cells of the T x A design.

    `cells` is keyed (T_level, A_level) with levels drawn from
    {"strong","neutral"} x {"high","low"}.

    Reported on three scales deliberately. The preregistered rule from the
    analysis doc section 2.1 is that the DiD counts as support ONLY if its sign
    agrees on all three; a sign that flips under reparameterisation is a
    property of the scale, not of the model.
    """
    need = [("strong", "high"), ("strong", "low"),
            ("neutral", "high"), ("neutral", "low")]
    missing = [k for k in need if not cells.get(k)]
    if missing:
        raise ValueError(f"interaction_did needs all four corner cells; "
                         f"missing {missing}")

    def mean_margin(k) -> float:
        rs = cells[k]
        return sum(r.m_seq for r in rs) / len(rs)

    def p_revert(k) -> float:
        rs = cells[k]
        return sum(1 for r in rs if r.reverted) / len(rs)

    dm = ((mean_margin(need[0]) - mean_margin(need[1]))
          - (mean_margin(need[2]) - mean_margin(need[3])))
    dl = ((_logit(p_revert(need[0])) - _logit(p_revert(need[1])))
          - (_logit(p_revert(need[2])) - _logit(p_revert(need[3]))))
    dp = ((p_revert(need[0]) - p_revert(need[1]))
          - (p_revert(need[2]) - p_revert(need[3])))

    # M_seq is "correct minus competitor", so MORE interference is a NEGATIVE
    # margin DiD but a POSITIVE reversion-probability DiD. Flip the margin sign
    # before comparing, so "agreement" means agreement about interference.
    signs = {math.copysign(1, -dm), math.copysign(1, dl), math.copysign(1, dp)}
    nonzero = {s for s, v in ((math.copysign(1, -dm), dm),
                              (math.copysign(1, dl), dl),
                              (math.copysign(1, dp), dp)) if v != 0.0}

    return InteractionResult(
        did_margin=dm, did_logit=dl, did_prob=dp,
        n={f"{t}/{a}": len(cells[(t, a)]) for t, a in need},
        sign_agrees=len(nonzero) <= 1,
    )
