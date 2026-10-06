"""power.py — template-clustered power and precision, from DEVELOPMENT data only.

The preregistration (§7) admitted there was no power analysis, so a null from
the confirmatory run would be uninterpretable. This module supplies one.

RULES
  * Pilot estimates come ONLY from development rows. `pilot_from_rows`
    refuses any row whose split label is not DEVELOPMENT (or SMOKE-tagged
    development cells), so held-out results can never tune a sample size.
  * Clustering is modelled, not ignored: sites are nested in templates, so
    every variance is inflated by the design effect 1 + (m - 1) * ICC, with
    the ICC both ESTIMATED from the pilot and SWEPT for sensitivity.

ANALYSES
  h4        P(criterion 1 met) = P(AUROC_hat >= 0.60 AND its lower bound > 0.5)
            -- criterion 1 reduces to this because the identity baseline is
            constant on the SEMANTIC-only eligible set (deviation D6).
            Hanley-McNeil variance x design effect; checked against a
            template-clustered binormal SIMULATION at the pilot point.
  rule      power for a positive mean rule effect, clustered.
  armb      precision of P(revert | reached) as a function of P(reach):
            the hurdle shrinks the effective n to n x P(O).
  kstar     projected precision of the KM median by resampling pilot
            TEMPLATES (censoring structure carried along, never re-imputed).
"""

from __future__ import annotations

import math
import random
import statistics as st
from collections import defaultdict
from statistics import NormalDist
from typing import Sequence

Z = NormalDist()


class HeldoutLeak(PermissionError):
    pass


def pilot_from_rows(rows: Sequence[dict]) -> list[dict]:
    bad = [r for r in rows if r.get("split") not in ("DEVELOPMENT",)]
    if bad:
        raise HeldoutLeak(f"{len(bad)} non-development rows offered as pilot data "
                          f"(e.g. split={bad[0].get('split')!r}); power may only "
                          f"use development estimates")
    return list(rows)


def icc_binary(rows: Sequence[dict], *, value: str, unit: str = "template") -> float:
    """One-way ANOVA ICC estimator, truncated at 0."""
    groups = defaultdict(list)
    for r in rows:
        groups[r[unit]].append(float(r[value]))
    gs = [g for g in groups.values() if g]
    k = len(gs)
    N = sum(len(g) for g in gs)
    if k < 2 or N <= k:
        return 0.0
    grand = sum(sum(g) for g in gs) / N
    ssb = sum(len(g) * (st.mean(g) - grand) ** 2 for g in gs)
    ssw = sum(sum((x - st.mean(g)) ** 2 for x in g) for g in gs)
    msb, msw = ssb / (k - 1), ssw / (N - k)
    n0 = (N - sum(len(g) ** 2 for g in gs) / N) / (k - 1)
    denom = msb + (n0 - 1) * msw
    return max(0.0, (msb - msw) / denom) if denom > 0 else 0.0


def hanley_mcneil_var(A: float, n1: int, n0: int) -> float:
    q1, q2 = A / (2 - A), 2 * A * A / (1 + A)
    return (A * (1 - A) + (n1 - 1) * (q1 - A * A) + (n0 - 1) * (q2 - A * A)) / (n1 * n0)


def h4_power(A: float, *, n_templates: int, m: float, prevalence: float,
             icc: float, threshold: float = 0.60, alpha: float = 0.05) -> float:
    n = max(int(round(n_templates * m)), 2)
    n1 = max(int(round(n * prevalence)), 1)
    n0 = max(n - n1, 1)
    deff = 1 + (m - 1) * icc
    se = math.sqrt(hanley_mcneil_var(A, n1, n0) * deff)
    cut = max(threshold, 0.5 + Z.inv_cdf(1 - alpha / 2) * se)
    return 1 - Z.cdf((cut - A) / se)


def h4_power_simulated(A: float, *, n_templates: int, m: int, prevalence: float,
                       icc: float, R: int = 300, seed: int = 20261006) -> float:
    """Template-clustered binormal simulation of criterion 1 (no bootstrap
    inside, Hanley-McNeil x deff for the interval) -- a check on the analytic
    curve's shape and level, not a replacement for it."""
    from p33.h4 import auroc
    rng = random.Random(seed)
    mu = math.sqrt(2) * Z.inv_cdf(A)
    hits = 0
    sd_t = math.sqrt(icc) if icc > 0 else 0.0
    base_logit = math.log(prevalence / (1 - prevalence))
    for _ in range(R):
        scores, labels = [], []
        for _t in range(n_templates):
            u = rng.gauss(0, sd_t * 1.8)
            for _s in range(m):
                p = 1 / (1 + math.exp(-(base_logit + u)))
                y = 1 if rng.random() < p else 0
                scores.append(rng.gauss(mu * y, 1.0))
                labels.append(y)
        a = auroc(scores, labels)
        if a is None:
            continue
        n1 = sum(labels)
        se = math.sqrt(hanley_mcneil_var(a, max(n1, 1), max(len(labels) - n1, 1))
                       * (1 + (m - 1) * icc))
        if a >= 0.60 and a - 1.96 * se > 0.5:
            hits += 1
    return hits / R


def smallest_detectable(power_fn, grid: Sequence[float], target: float = 0.80) -> float | None:
    for x in grid:
        if power_fn(x) >= target:
            return x
    return None


def rule_power(d: float, sd: float, *, n_templates: int, m: float, icc: float,
               alpha: float = 0.05) -> float:
    n_eff = n_templates * m / (1 + (m - 1) * icc)
    se = sd / math.sqrt(max(n_eff, 1.0))
    return 1 - Z.cdf(Z.inv_cdf(1 - alpha / 2) - d / se) if se > 0 else float("nan")


def armb_precision(p_cond: float, *, n_sites: int, p_reach: float, m: float,
                   icc: float) -> float:
    """95% CI half-width for P(revert | reached)."""
    n_eff = n_sites * p_reach / (1 + (m - 1) * icc)
    if n_eff < 1:
        return float("inf")
    return 1.96 * math.sqrt(p_cond * (1 - p_cond) / n_eff)


def kstar_projection(curves: Sequence[dict], *, target_templates: int,
                     R: int = 200, seed: int = 20261006) -> dict:
    """Resample pilot TEMPLATES to `target_templates`; spread of the KM median."""
    from p33.kstar import kaplan_meier
    by_t = defaultdict(list)
    for c in curves:
        by_t[c["template"]].append(c)
    keys = sorted(by_t)
    if len(keys) < 2:
        return {"status": "NOT ESTIMABLE", "reason": "fewer than 2 pilot templates"}
    rng = random.Random(seed)
    meds = []
    for _ in range(R):
        pick = [c for _ in range(target_templates) for c in by_t[keys[rng.randrange(len(keys))]]]
        wrong = [c for c in pick if not c["already_correct"]]
        if not wrong:
            continue
        km = kaplan_meier([c["top_rung"] if c["censored"] else c["k_star"] for c in wrong],
                          [not c["censored"] for c in wrong], population="INITIALLY_WRONG")
        meds.append(km.median if km.median is not None else float("inf"))
    finite = sorted(x for x in meds if math.isfinite(x))
    if not finite:
        return {"status": "NOT ESTIMABLE", "reason": "median never reached in resamples"}
    lo = finite[int(0.025 * (len(finite) - 1))]
    hi = finite[int(0.975 * (len(finite) - 1))]
    return {"status": "OK", "median_of_medians": st.median(finite), "lo": lo, "hi": hi,
            "share_median_unreached": 1 - len(finite) / len(meds) if meds else None}


def analyse(h4_table: Sequence[dict], arm_a_rows: Sequence[dict],
            curves: Sequence[dict], armb_hurdles: Sequence[dict]) -> list[dict]:
    """All power/precision rows for power.csv. Development data only."""
    out = []
    grid_A = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
    grid_T = [20, 40, 80, 160, 320]
    grid_icc = [0.0, 0.05, 0.10, 0.20]

    if h4_table:
        pilot_from_rows(h4_table)
        prev = sum(r["label"] for r in h4_table) / len(h4_table)
        m = len(h4_table) / max(len({r["template"] for r in h4_table}), 1)
        icc = icc_binary(h4_table, value="label")
        from p33.h4 import auroc
        A_pilot = auroc([r["risk"] for r in h4_table], [r["label"] for r in h4_table])
        pilot_models = "|".join(sorted({r["model"] for r in h4_table}))
        pilot_revs = "|".join(sorted({r["model_revision"] for r in h4_table}))
        for T in grid_T:
            for ic in sorted(set(grid_icc + [round(icc, 3)])):
                for A in grid_A:
                    out.append({"analysis": "h4_criterion1", "n_templates": T,
                                "sites_per_template": round(m, 2), "prevalence": round(prev, 3),
                                "icc": ic, "true_auroc": A,
                                "power": h4_power(A, n_templates=T, m=m, prevalence=max(min(prev, .99), .01), icc=ic),
                                "pilot_auroc": A_pilot, "pilot_icc": icc,
                                "model": pilot_models, "model_revision": pilot_revs,
                                "split": "DEVELOPMENT",
                                "source": "analytic (Hanley-McNeil x design effect)"})
                sde = smallest_detectable(lambda a: h4_power(a, n_templates=T, m=m,
                                          prevalence=max(min(prev, .99), .01), icc=icc),
                                          [x / 100 for x in range(51, 100)])
                out.append({"analysis": "h4_smallest_detectable_auroc", "n_templates": T,
                            "icc": icc, "value": sde, "power_target": 0.8})
        if A_pilot and 0.5 < A_pilot < 1 and 0 < prev < 1:
            T0 = len({r["template"] for r in h4_table})
            out.append({"analysis": "h4_simulation_check", "n_templates": T0,
                        "true_auroc": round(A_pilot, 3), "icc": round(icc, 3),
                        "power_simulated": h4_power_simulated(
                            A_pilot, n_templates=T0, m=max(int(round(m)), 1),
                            prevalence=prev, icc=icc, R=200),
                        "power_analytic": h4_power(A_pilot, n_templates=T0, m=m,
                                                   prevalence=prev, icc=icc),
                        "source": "template-clustered binormal simulation, R=200"})
    else:
        out.append({"analysis": "h4_criterion1", "status": "NOT RUN",
                    "reason": "no development H4 table (needs base AND instruct Arm A rows)"})

    idx = defaultdict(dict)
    for r in arm_a_rows:
        if r.get("status") == "ok" and r["condition"] in ("rule", "norule"):
            idx[(r["model"], r["site_id"])][r["condition"]] = r
    diffs = [{"template": v["rule"]["template"], "d": v["rule"]["m_seq"] - v["norule"]["m_seq"],
              "split": v["rule"]["split"]} for v in idx.values() if len(v) == 2]
    if len(diffs) > 2:
        pilot_from_rows(diffs)
        d = st.mean(x["d"] for x in diffs)
        sd = st.pstdev(x["d"] for x in diffs) or 1e-9
        m = len(diffs) / max(len({x["template"] for x in diffs}), 1)
        icc = icc_binary(diffs, value="d")
        for T in grid_T:
            for ic in sorted(set(grid_icc + [round(icc, 3)])):
                out.append({"analysis": "rule_effect", "n_templates": T, "icc": ic,
                            "pilot_mean": d, "pilot_sd": sd, "sites_per_template": round(m, 2),
                            "power": rule_power(d, sd, n_templates=T, m=m, icc=ic)})
    else:
        out.append({"analysis": "rule_effect", "status": "NOT RUN",
                    "reason": "no paired rule/no-rule development rows"})

    if armb_hurdles:
        for h in armb_hurdles:
            pc = h.get("p_revert_given_reach")
            if pc is None:
                continue
            for pr in (0.1, 0.25, 0.5, 0.75, 1.0):
                for ns in (200, 800, 3200):
                    out.append({"analysis": "armb_conditional_precision", "p_reach": pr,
                                "n_sites": ns, "pilot_p_cond": pc, "icc": 0.1,
                                "ci_halfwidth": armb_precision(pc, n_sites=ns, p_reach=pr,
                                                               m=3.0, icc=0.1)})
            break
    else:
        out.append({"analysis": "armb_conditional_precision", "status": "NOT RUN",
                    "reason": "no development Arm B hurdle estimates"})

    if curves:
        pilot_from_rows(curves)
        for T in (40, 80, 160, 320):
            proj = kstar_projection(curves, target_templates=T)
            out.append({"analysis": "kstar_km_median_precision", "n_templates": T, **proj})
    else:
        out.append({"analysis": "kstar_km_median_precision", "status": "NOT RUN",
                    "reason": "no development extinction curves"})
    return out
