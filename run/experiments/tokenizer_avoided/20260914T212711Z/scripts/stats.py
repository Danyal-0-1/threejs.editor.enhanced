"""stats.py — the statistics the study predeclared. Pure numpy/stdlib.

Everything here is deterministic given the recorded seed, and every function
returns its numerator and denominator alongside the estimate so a reader can
recompute it by hand.
"""
from __future__ import annotations

import math
import random
from typing import Sequence

SEED = 20260910
BOOTSTRAP = 10_000


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson 95% interval for a proportion. n == 0 -> (nan, nan), never 0."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def proportion(k: int, n: int) -> dict:
    lo, hi = wilson(k, n)
    return {"numerator": k, "denominator": n,
            "proportion": (k / n) if n else None,
            "percent": (100.0 * k / n) if n else None,
            "wilson95_lo": lo, "wilson95_hi": hi}


def paired_risk_difference(alien: Sequence[int], base: Sequence[int], *,
                           rounds: int = BOOTSTRAP, seed: int = SEED) -> dict:
    """Paired risk difference (alien - identity) on MATCHED items, with a
    paired item-level bootstrap interval. Resamples ITEM INDICES once and
    applies them to both arms -- that is what makes it paired."""
    n = len(alien)
    if n != len(base):
        raise ValueError(f"unpaired: {n} vs {len(base)}")
    if n == 0:
        return {"n_pairs": 0, "risk_difference": None,
                "ci95_lo": None, "ci95_hi": None}
    point = (sum(alien) - sum(base)) / n
    rng = random.Random(seed)
    deltas = []
    for _ in range(rounds):
        idx = [rng.randrange(n) for _ in range(n)]
        deltas.append(sum(alien[i] - base[i] for i in idx) / n)
    deltas.sort()
    return {"n_pairs": n, "risk_difference": point,
            "ci95_lo": deltas[max(0, int(0.025 * rounds) - 1)],
            "ci95_hi": deltas[min(rounds - 1, int(0.975 * rounds) - 1)],
            "bootstrap_rounds": rounds, "seed": seed}


def mcnemar_exact(alien: Sequence[int], base: Sequence[int]) -> dict:
    """Exact McNemar: a two-sided binomial test on the DISCORDANT pairs.

    b = identity correct, alien wrong.   c = alien correct, identity wrong.
    With b + c == 0 there is no discordant evidence and p is reported as 1.0
    with n_discordant = 0, so the emptiness is visible rather than hidden.
    """
    b = sum(1 for a, d in zip(alien, base) if d == 1 and a == 0)
    c = sum(1 for a, d in zip(alien, base) if d == 0 and a == 1)
    n = b + c
    if n == 0:
        return {"b_identity_only": 0, "c_alien_only": 0,
                "n_discordant": 0, "p_value": 1.0}
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return {"b_identity_only": b, "c_alien_only": c, "n_discordant": n,
            "p_value": min(1.0, 2.0 * tail)}


def holm(pvalues: dict[str, float]) -> dict[str, dict]:
    """Holm-Bonferroni within one declared family."""
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(items)
    out, running = {}, 0.0
    for i, (name, p) in enumerate(items):
        adj = min(1.0, (m - i) * p)
        running = max(running, adj)            # enforce monotonicity
        out[name] = {"p_raw": p, "p_holm": running,
                     "reject_at_0.05": running < 0.05}
    return out


def ratio_of_totals(rows: Sequence[tuple[float, int]]) -> float:
    """Sum(numerator) / Sum(denominator). NOT a mean of per-item ratios: a short
    program contributes fewer nats AND fewer tokens, and averaging per-item
    ratios would weight it like a long one and change the estimand."""
    den = sum(r[1] for r in rows)
    if den == 0:
        raise ZeroDivisionError("empty denominator")
    return sum(r[0] for r in rows) / den


def paired_bootstrap_ratio(alien: Sequence[tuple[float, int]],
                           base: Sequence[tuple[float, int]], *,
                           rounds: int = BOOTSTRAP, seed: int = SEED) -> dict:
    """95% CI for a DIFFERENCE OF RATIOS OF TOTALS, recomputing the same
    estimand the point estimate uses (see prior_strength.paired_bootstrap)."""
    n = len(alien)
    if n != len(base):
        raise ValueError(f"unpaired: {n} vs {len(base)}")
    point = ratio_of_totals(alien) - ratio_of_totals(base)
    if n < 2:
        return {"point": point, "ci95_lo": point, "ci95_hi": point,
                "degenerate": True, "n_pairs": n}
    rng = random.Random(seed)
    deltas = []
    for _ in range(rounds):
        idx = [rng.randrange(n) for _ in range(n)]
        deltas.append(ratio_of_totals([alien[i] for i in idx])
                      - ratio_of_totals([base[i] for i in idx]))
    deltas.sort()
    return {"point": point,
            "ci95_lo": deltas[max(0, int(0.025 * rounds) - 1)],
            "ci95_hi": deltas[min(rounds - 1, int(0.975 * rounds) - 1)],
            "n_pairs": n, "bootstrap_rounds": rounds, "seed": seed}


def median_iqr_p95(xs: Sequence[float]) -> dict:
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return {"n": 0, "median": None, "iqr": None, "p95": None}
    n = len(xs)
    def q(p):
        if n == 1:
            return xs[0]
        pos = p * (n - 1)
        lo = int(math.floor(pos)); hi = min(lo + 1, n - 1)
        return xs[lo] + (pos - lo) * (xs[hi] - xs[lo])
    return {"n": n, "median": q(0.5), "q1": q(0.25), "q3": q(0.75),
            "iqr": q(0.75) - q(0.25), "p95": q(0.95),
            "min": xs[0], "max": xs[-1]}
