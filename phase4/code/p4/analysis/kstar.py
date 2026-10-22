"""kstar.py — the extinction threshold, defined correctly, plus survival summaries.

----------------------------------------------------------------------------
DEFECT P33-007: THE PHASE 3.3 k* WAS WRONG IN THREE WAYS
----------------------------------------------------------------------------
Measured on `phase3_2/outputs/primary.json` (240 curves):

  * 84 of 125 sites already correct at 0 shots got k* = None -- treated as
    missing instead of "no examples needed";
  * the other 41 already-correct sites got a k* from a LATER re-crossing;
  * 16 curves had BOTH a k* and censored=True, because censoring was defined
    as "negative at the last rung" rather than "never crossed".

On top of that, 82 of the 120 sites had their own target program in the
demonstration pool (see `demos.py`), so those curves are contaminated anyway.

----------------------------------------------------------------------------
THE DEFINITION (as specified, and implemented exactly)
----------------------------------------------------------------------------
    M(0) >= 0          k* = 0,     already_correct = True,  censored = False
    else               first UPWARD crossing (M_{j-1} < 0 <= M_j),
                       linearly interpolated between those two rungs
    no crossing        k* = None,  censored = True

A curve that crosses and later drops is NOT censored -- the event happened.
Every rung is preserved; the crossing counts and a non-monotonicity flag are
recorded, because 237 of the 240 audited curves were non-monotone, which makes
a first-crossing threshold sensitive to noise.

`sustained_k` is an ADDITIONAL, clearly labelled diagnostic: the first rung
after which the margin never returns below zero. It answers "when does the
habit stay broken?", which first-crossing does not.

----------------------------------------------------------------------------
SURVIVAL SUMMARIES
----------------------------------------------------------------------------
The event is "the margin first becomes non-negative"; time is the shot count;
curves that never cross are right-censored at the top rung. Kaplan-Meier is
the valid estimator. Two populations, always labelled:

  ALL SITES            events at t=0 for already-correct sites. With ~half the
                       sites already correct, the KM median here is often 0 --
                       that is a TRUE statement about the population, not a bug.
  INITIALLY WRONG      conditional on M(0) < 0: "how many examples does it take,
                       for sites that start wrong?" -- the actionable number.

The median among crossers only is kept as a DIAGNOSTIC and labelled so. It
discards censored sites, which are exactly the strongest priors, and therefore
underestimates k*.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence


@dataclass(frozen=True)
class KStar:
    k_star: float | None
    already_correct: bool
    censored: bool
    n_up_crossings: int
    n_down_crossings: int
    nonmonotone: bool          # any decrease between consecutive rungs
    recrossed_down: bool       # dropped below zero again after the first crossing
    sustained_k: float | None  # first rung after which M never returns below 0
    top_rung: int

    def as_dict(self) -> dict:
        return asdict(self)


def compute(ladder: Sequence[int], margins: Sequence[float]) -> KStar:
    if len(ladder) != len(margins) or not ladder:
        raise ValueError("ladder and margins must be equal, non-empty")
    if list(ladder) != sorted(ladder) or ladder[0] != 0:
        raise ValueError("ladder must be increasing and start at 0")

    ups = sum(1 for a, b in zip(margins, margins[1:]) if a < 0 <= b)
    downs = sum(1 for a, b in zip(margins, margins[1:]) if a >= 0 > b)
    nonmono = any(b < a for a, b in zip(margins, margins[1:]))

    sustained = None
    for i in range(len(margins)):
        if all(m >= 0 for m in margins[i:]):
            sustained = float(ladder[i])
            break

    if margins[0] >= 0:
        return KStar(0.0, True, False, ups, downs, nonmono,
                     downs > 0, sustained, ladder[-1])

    for i in range(1, len(margins)):
        y0, y1 = margins[i - 1], margins[i]
        if y0 < 0 <= y1:
            t = (0.0 - y0) / (y1 - y0)
            k = float(ladder[i - 1]) + t * (ladder[i] - ladder[i - 1])
            after = margins[i:]
            return KStar(k, False, False, ups, downs, nonmono,
                         any(m < 0 for m in after), sustained, ladder[-1])

    return KStar(None, False, True, ups, downs, nonmono, False, None, ladder[-1])


# ---------------------------------------------------------------------------
# Kaplan-Meier
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class KMSummary:
    population: str
    n: int
    n_events: int
    n_censored: int
    median: float | None       # None = survival never fell to 0.5 (> top rung)
    curve: list[tuple[float, float]]

    @property
    def censoring_rate(self) -> float:
        return self.n_censored / self.n if self.n else float("nan")


def kaplan_meier(times: Sequence[float], events: Sequence[bool],
                 *, population: str) -> KMSummary:
    """Product-limit estimator. `times` for censored items = censoring time."""
    data = sorted(zip(times, events), key=lambda te: (te[0], not te[1]))
    n_at_risk = len(data)
    s = 1.0
    curve: list[tuple[float, float]] = [(0.0, 1.0)]
    median = None
    i = 0
    while i < len(data):
        t = data[i][0]
        d = c = 0
        while i < len(data) and data[i][0] == t:
            if data[i][1]:
                d += 1
            else:
                c += 1
            i += 1
        if d:
            s *= (1 - d / n_at_risk)
            curve.append((t, s))
            if median is None and s <= 0.5:
                median = t
        n_at_risk -= d + c
    n_ev = sum(1 for e in events if e)
    return KMSummary(population, len(times), n_ev, len(times) - n_ev, median, curve)


def km_from_kstars(ks: Sequence[KStar], *, initially_wrong_only: bool) -> KMSummary:
    pop = "INITIALLY_WRONG" if initially_wrong_only else "ALL_SITES"
    use = [k for k in ks if not (initially_wrong_only and k.already_correct)]
    times = [k.top_rung if k.censored else k.k_star for k in use]
    events = [not k.censored for k in use]
    return kaplan_meier(times, events, population=pop)


def median_among_crossers(ks: Sequence[KStar]) -> float | None:
    """DIAGNOSTIC ONLY -- drops censored sites and so underestimates k*."""
    xs = sorted(k.k_star for k in ks if k.k_star is not None and not k.already_correct)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2
