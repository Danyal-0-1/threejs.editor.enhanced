"""h4.py — exact-site prediction: risk score, mandatory baselines, metrics.

H4 (preregistered, confirmatory): a BASE checkpoint's preference at an exact
decision site predicts which sites the matched INSTRUCT checkpoint gets wrong.

    risk   = -M_seq(base model, rule condition)          frozen formula id
             "neg_mseq_base_rule" (positive = the base model prefers the
             familiar competitor even with the table in context)
    label  = 1 if M_seq(instruct model, rule condition) < 0   (reversion)

Both come from Arm A rows scored by the ONE canonical first-divergent-token
scorer. `phase3.linter.score_site` is not used: it reaches the old
prefix-tail path, which now raises instead of returning 0.0 (P32-001).

MANDATORY BASELINES (preregistered §3 and review §10.2)
    identity       1 if the lexicon remaps this role. NOTE: every eligible
                   site is SEMANTIC (remapped) by exclusion rule 1, so this
                   baseline is CONSTANT on the eligible set and its AUROC is
                   exactly 0.5. Criterion 1 therefore reduces to
                   "AUROC >= 0.60 with the difference's interval above 0".
                   Reported, not hidden (deviation D6).
    length         |q| - |c| in UTF-8 bytes
    program_nll    base model's whole-program NLL per character
    token_count    n_tok_correct + n_tok_competitor under the base tokenizer
EXPLORATORY (not preregistered, labelled so)
    terminal_rate  the dev-estimated reversion rate of the site's TERMINAL
                   (role). This is the real "language-identity detector": if
                   knowing only WHICH ROLE predicts as well as the site score,
                   the score carries nothing site-specific. Cross-fitted by
                   template within a run so it is not scored on its own data.

All metrics are pure Python so CPU tests need nothing beyond the stdlib.
"""

from __future__ import annotations

import math
import operator
import statistics as st
from collections import defaultdict
from typing import Sequence

RISK_FORMULA = "neg_mseq_base_rule"
BASELINES = ("identity", "length", "program_nll", "token_count")
EXPLORATORY_BASELINES = ("terminal_rate",)


# ---------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------

def auroc(scores: Sequence[float], labels: Sequence[int]) -> float | None:
    """Mann-Whitney AUROC with average ranks for ties. None if one class absent."""
    n1 = sum(labels)
    n0 = len(labels) - n1
    if n1 == 0 or n0 == 0:
        return None
    order = sorted(range(len(scores)), key=lambda i: scores[i])
    ranks = [0.0] * len(scores)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for t in range(i, j + 1):
            ranks[order[t]] = avg
        i = j + 1
    r1 = sum(r for r, y in zip(ranks, labels) if y == 1)
    return (r1 - n1 * (n1 + 1) / 2) / (n1 * n0)


def threshold_groups(scores: Sequence[float], labels: Sequence[int]
                     ) -> list[tuple[float, int, int]]:
    """(score, n, positives) for every DISTINCT score, highest first.

    Every metric that thresholds a score is computed on these groups, never on
    individual observations: no threshold can separate observations with equal
    scores, so no metric may depend on the order in which they were listed.
    Raises on a NaN score (it has no place in an ordering; callers drop
    missing predictions first) and on labels other than 0/1.
    """
    if len(scores) != len(labels):
        raise ValueError(f"{len(scores)} scores but {len(labels)} labels")
    groups: dict[float, list[int]] = defaultdict(lambda: [0, 0])
    for s, y in zip(scores, labels):
        s = float(s)
        if math.isnan(s):
            raise ValueError("NaN score: drop missing predictions before thresholding")
        if y not in (0, 1):
            raise ValueError(f"labels must be 0 or 1, got {y!r}")
        g = groups[s]
        g[0] += 1
        g[1] += int(y)
    return [(s, n, p) for s, (n, p) in sorted(groups.items(), key=lambda kv: -kv[0])]


def auprc(scores: Sequence[float], labels: Sequence[int]) -> float | None:
    """Average precision, step-wise, with TIED SCORES GROUPED into one threshold.

        AP = sum_j (R_j - R_(j-1)) * P_j

    over the distinct scores j, highest first; R_j and P_j are the recall and
    precision after admitting EVERY observation that scores >= the j-th
    distinct score. Since R_j - R_(j-1) = p_j / P, this is computed as
    sum_j p_j * P_j / P. It is the step-wise "average precision" estimator,
    not the trapezoidal area under the PR curve (which interpolates linearly
    between points and is optimistic for PR curves).

      * permutation-invariant: a tied group enters as a whole. The previous
        version ranked tied rows by input position, so scores [1, 1] gave
        AP = 1.0 for labels [1, 0] and 0.5 for [0, 1]; both are 0.5 now.
      * a constant score gives exactly the positive prevalence;
      * distinct scores give bit-for-bit the previous value (each group is
        one observation, summed in the same order);
      * no positive observation (including empty input) -> None, the existing
        convention: AP is undefined without a positive class.
    Report it WITH the prevalence, which is its chance level.
    """
    groups = threshold_groups(scores, labels)
    P = sum(p for _s, _n, p in groups)
    if P == 0:
        return None
    acc = 0.0
    tp = seen = 0
    for _s, n, p in groups:
        tp += p
        seen += n
        if p:
            acc += p * (tp / seen)
    return acc / P


def precision_at_k(scores: Sequence[float], labels: Sequence[int], k: int) -> float | None:
    """Expected precision of the top k under UNIFORM selection inside the boundary tie.

    With K = min(k, n): every observation scoring strictly above the boundary
    score is selected (a of them, with pos_above positives); the remaining
    K - a places are filled uniformly at random from the boundary tie group
    (g observations, p positives), which contributes (K - a) * p / g expected
    positives:

        P@K = (pos_above + (K - a) * p / g) / K

      * permutation-invariant. The previous version broke the boundary tie
        by input position: on the development data the identity baseline's
        P@10 moved from 0.4 to 0.6 when the rows were reversed;
      * identical to plain top-k precision when the boundary is not tied;
      * a constant score gives the prevalence for every valid k;
      * k larger than the sample: K = n, i.e. the prevalence of the whole set;
      * empty input -> None; k < 1 or a non-integer k -> ValueError.
    """
    if isinstance(k, bool):
        raise ValueError(f"k must be an integer >= 1, got {k!r}")
    try:
        k = operator.index(k)
    except TypeError:
        raise ValueError(f"k must be an integer >= 1, got {k!r}") from None
    if k < 1:
        raise ValueError(f"k must be an integer >= 1, got {k!r}")
    groups = threshold_groups(scores, labels)
    n = sum(g for _s, g, _p in groups)
    if n == 0:
        return None
    K = min(k, n)
    taken, positives = 0, 0.0
    for _s, g, p in groups:
        if taken + g <= K:
            taken += g
            positives += p
            if taken == K:
                break
        else:
            positives += (K - taken) * p / g
            break
    return positives / K


def pr_curve(scores: Sequence[float], labels: Sequence[int]) -> list[tuple[float, float]]:
    """(recall, precision) after each distinct-score threshold, highest first.

    These are exactly the points whose step-wise sum `auprc` reports; figures
    draw them, so a plot and its table cannot disagree.
    """
    groups = threshold_groups(scores, labels)
    P = sum(p for _s, _n, p in groups)
    out, tp, seen = [], 0, 0
    for _s, n, p in groups:
        tp += p
        seen += n
        out.append((tp / P if P else 0.0, tp / seen))
    return out


def roc_curve(scores: Sequence[float], labels: Sequence[int]) -> list[tuple[float, float]]:
    """(FPR, TPR) from (0, 0) through each distinct-score threshold.

    A tied group moves diagonally, so the trapezoidal area under these points
    equals the average-rank AUROC that `auroc` reports.
    """
    groups = threshold_groups(scores, labels)
    P = sum(p for _s, _n, p in groups)
    N = sum(n - p for _s, n, p in groups)
    out, tp, fp = [(0.0, 0.0)], 0, 0
    for _s, n, p in groups:
        tp += p
        fp += n - p
        out.append((fp / N if N else 0.0, tp / P if P else 0.0))
    return out


def brier(probs: Sequence[float], labels: Sequence[int]) -> float:
    return sum((p - y) ** 2 for p, y in zip(probs, labels)) / len(labels)


def ece(probs: Sequence[float], labels: Sequence[int], bins: int = 10) -> float:
    n = len(probs)
    total = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        idx = [i for i, p in enumerate(probs) if (lo <= p < hi) or (b == bins - 1 and p == 1.0)]
        if idx:
            conf = sum(probs[i] for i in idx) / len(idx)
            acc = sum(labels[i] for i in idx) / len(idx)
            total += len(idx) / n * abs(acc - conf)
    return total


def _sigmoid(z: float) -> float:
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    e = math.exp(z)
    return e / (1 + e)


def logistic_fit(x: Sequence[float], y: Sequence[int], *, iters: int = 50,
                 ridge: float = 1e-6) -> tuple[float, float]:
    """Newton-Raphson for p = sigmoid(a + b x). Tiny ridge for separability."""
    a = b = 0.0
    for _ in range(iters):
        ga = gb = haa = hab = hbb = 0.0
        for xi, yi in zip(x, y):
            p = _sigmoid(a + b * xi)
            w = p * (1 - p)
            ga += yi - p
            gb += (yi - p) * xi
            haa += w
            hab += w * xi
            hbb += w * xi * xi
        haa += ridge
        hbb += ridge
        det = haa * hbb - hab * hab
        if det <= 0:
            break
        da = (hbb * ga - hab * gb) / det
        db = (haa * gb - hab * ga) / det
        a, b = a + da, b + db
        if abs(da) + abs(db) < 1e-10:
            break
    return a, b


def calibration_slope_intercept(probs: Sequence[float], labels: Sequence[int]
                                ) -> tuple[float, float] | None:
    """Regress y on logit(p): perfect calibration gives intercept 0, slope 1."""
    eps = 1e-6
    z = [math.log(min(max(p, eps), 1 - eps) / (1 - min(max(p, eps), 1 - eps))) for p in probs]
    if len(set(labels)) < 2:
        return None
    a, b = logistic_fit(z, labels)
    return a, b


def youden_threshold(probs: Sequence[float], labels: Sequence[int]) -> float:
    best_t, best_j = 0.5, -1.0
    P = sum(labels)
    N = len(labels) - P
    for t in sorted(set(probs)):
        tp = sum(1 for p, y in zip(probs, labels) if p >= t and y)
        fp = sum(1 for p, y in zip(probs, labels) if p >= t and not y)
        j = (tp / P if P else 0) - (fp / N if N else 0)
        if j > best_j:
            best_t, best_j = t, j
    return best_t


# ---------------------------------------------------------------------------
# the H4 table: one row per (pair, site)
# ---------------------------------------------------------------------------

def pairs_present(rows: Sequence[dict]) -> list[tuple[str, str]]:
    from p33 import registry as R
    models = {r["model"] for r in rows}
    out = []
    for m in sorted(models):
        s = R.REGISTRY.get(m)
        if s and s.kind == "base" and s.pair in models:
            out.append((m, s.pair))
    return out


def build_table(arm_a_rows: Sequence[dict]) -> list[dict]:
    """Join base and instruct rule-condition rows on site_id."""
    rule = [r for r in arm_a_rows if r["condition"] == "rule" and r["status"] == "ok"]
    by = defaultdict(dict)
    for r in rule:
        by[r["model"]][r["site_id"]] = r
    out = []
    for base, inst in pairs_present(rule):
        for sid, b in sorted(by[base].items()):
            i = by[inst].get(sid)
            if i is None:
                continue
            out.append({
                "pair": f"{base}|{inst}", "base_model": base, "instruct_model": inst,
                "model": f"{base}|{inst}",
                "model_revision": f"{b['model_revision']}|{i['model_revision']}",
                "base_revision": b["model_revision"], "instruct_revision": i["model_revision"],
                "tokenizer_id": b["tokenizer_id"],
                "site_id": sid, "family": b["family"], "lexicon": b["lexicon"],
                "template": b["template"], "terminal": b["terminal"],
                "stratum": b["stratum"], "split": i["split"],
                "risk": -b["m_seq"],
                "label": int(i["m_seq"] < 0),
                "identity": 1.0 if b["correct"] != b["competitor"] else 0.0,
                "length": float(len(b["competitor"].encode()) - len(b["correct"].encode())),
                "program_nll": b.get("program_nll_per_char") or float("nan"),
                "token_count": float((b["n_tok_correct"] or 0) + (b["n_tok_competitor"] or 0)),
            })
    _crossfit_terminal_rate(out)
    return out


def _crossfit_terminal_rate(table: list[dict]) -> None:
    """Exploratory baseline, leave-one-template-out within each pair."""
    by_pair = defaultdict(list)
    for r in table:
        by_pair[r["pair"]].append(r)
    for rows in by_pair.values():
        tot = defaultdict(lambda: [0, 0])
        per_t = defaultdict(lambda: defaultdict(lambda: [0, 0]))
        for r in rows:
            tot[r["terminal"]][0] += r["label"]
            tot[r["terminal"]][1] += 1
            per_t[r["template"]][r["terminal"]][0] += r["label"]
            per_t[r["template"]][r["terminal"]][1] += 1
        prior = sum(r["label"] for r in rows) / len(rows) if rows else 0.5
        for r in rows:
            s, n = tot[r["terminal"]]
            ds, dn = per_t[r["template"]][r["terminal"]]
            s, n = s - ds, n - dn
            r["terminal_rate"] = (s + prior) / (n + 1)        # shrink toward prior


# ---------------------------------------------------------------------------
# evaluation
# ---------------------------------------------------------------------------

def _finite(rows, col):
    return [r for r in rows if not (isinstance(r[col], float) and math.isnan(r[col]))]


def evaluate_group(rows: Sequence[dict], *, calibration: tuple[float, float] | None,
                   threshold: float | None, ks: Sequence[int], bins: int,
                   B: int, seed: int, min_clusters: int) -> list[dict]:
    """Metrics for the score and every baseline in one group of rows."""
    from phase3_2 import analysis as AN
    out = []
    labels = [r["label"] for r in rows]
    prev = sum(labels) / len(labels) if labels else float("nan")
    cal = calibration or logistic_fit([r["risk"] for r in rows], labels)
    for col in ("risk",) + BASELINES + EXPLORATORY_BASELINES:
        sub = _finite(rows, col)
        sc = [r[col] for r in sub]
        lb = [r["label"] for r in sub]
        rec = {"predictor": col,
               "role": ("score" if col == "risk" else
                        "exploratory_baseline" if col in EXPLORATORY_BASELINES else "baseline"),
               "n_rows": len(sub), "n_templates": len({r["template"] for r in sub}),
               "n_mappings": len({r["lexicon"] for r in sub}), "prevalence": prev,
               "auroc": auroc(sc, lb), "auprc": auprc(sc, lb)}
        for k in ks:
            rec[f"p_at_{k}"] = precision_at_k(sc, lb, k)
        if col == "risk" and sub:
            probs = [_sigmoid(cal[0] + cal[1] * x) for x in sc]
            rec.update({"brier": brier(probs, lb), "ece": ece(probs, lb, bins),
                        "cal_a": cal[0], "cal_b": cal[1],
                        "threshold": threshold})
            cs = calibration_slope_intercept(probs, lb)
            rec.update({"cal_intercept": cs[0] if cs else None,
                        "cal_slope": cs[1] if cs else None})
            within = []
            for lx in sorted({r["lexicon"] for r in sub}):
                g = [r for r in sub if r["lexicon"] == lx]
                a = auroc([r["risk"] for r in g], [r["label"] for r in g])
                if a is not None:
                    within.append(a)
            rec["within_lexicon_auroc_mean"] = st.mean(within) if within else None
        out.append(rec)

    # template-cluster bootstrap of AUROC differences: score - baseline
    if len(set(labels)) < 2:
        for base in BASELINES + EXPLORATORY_BASELINES:
            out.append({"predictor": f"delta_vs_{base}", "role": "difference",
                        "n_rows": len(rows),
                        "ci_status": f"NOT ESTIMABLE: every label is {labels[0] if labels else '?'} "
                                     f"(AUROC undefined with one class)"})
        return out
    for base in BASELINES + EXPLORATORY_BASELINES:
        sub = [r for r in _finite(rows, base)]

        def stat(rs, base=base):
            a = auroc([r["risk"] for r in rs], [r["label"] for r in rs])
            c = auroc([r[base] for r in rs], [r["label"] for r in rs])
            if a is None or c is None:
                raise ValueError("degenerate resample")
            return a - c
        res = AN.cluster_bootstrap(sub, stat, unit="template", B=B, seed=seed,
                                   min_clusters=min_clusters, return_draws=True)
        if res is None:
            n_t = len({r["template"] for r in sub})
            out.append({"predictor": f"delta_vs_{base}", "role": "difference",
                        "n_rows": len(sub),
                        "ci_status": (f"NO INTERVAL ({n_t} template clusters < {min_clusters})"
                                      if n_t < min_clusters else
                                      "NO INTERVAL (statistic undefined on too many resamples)")})
            continue
        iv, draws = res
        out.append({"predictor": f"delta_vs_{base}", "role": "difference",
                    "n_rows": len(sub), "delta_auroc": iv.point,
                    "ci_lo": iv.lo, "ci_hi": iv.hi, "n_templates": iv.n_clusters,
                    "p_one_sided": AN.bootstrap_pvalue_greater(draws, 0.0),
                    "ci_unit": "template", "ci_reps": B, "ci_seed": seed})
    return out


def criteria(metrics: Sequence[dict], *, grammar_valid: bool) -> list[dict]:
    """The frozen H4 criteria, with Holm over the two confirmatory differences."""
    from phase3_2 import analysis as AN
    get = {m["predictor"]: m for m in metrics}
    rows = []
    pv = {}
    for name, base, thr in (("C1_delta_vs_identity", "identity", 0.10),
                            ("C2_delta_vs_length", "length", 0.05)):
        d = get.get(f"delta_vs_{base}", {})
        if "delta_auroc" not in d:
            rows.append({"criterion": name, "status": "NOT TESTABLE",
                         "detail": d.get("ci_status", "no difference computed")})
            continue
        pv[name] = d["p_one_sided"]
        rows.append({"criterion": name, "threshold": thr, "delta": d["delta_auroc"],
                     "ci_lo": d["ci_lo"], "ci_hi": d["ci_hi"],
                     "met_point": d["delta_auroc"] >= thr, "met_ci": d["ci_lo"] > 0})
    adj = AN.holm(pv) if pv else {}
    for r in rows:
        if r["criterion"] in adj:
            r["p_holm"] = adj[r["criterion"]]
            r["status"] = "MET" if (r["met_point"] and r["met_ci"] and r["p_holm"] < 0.05) else "NOT MET"
    score = get.get("risk", {})
    if grammar_valid:
        a = score.get("auroc")
        rows.append({"criterion": "C3_auroc_heldout_grammar", "threshold": 0.65,
                     "value": a, "status": "MET" if a is not None and a >= 0.65 else "NOT MET"})
    else:
        rows.append({"criterion": "C3_auroc_heldout_grammar", "status": "NOT TESTABLE",
                     "detail": "no valid held-out grammar family exists: blk was "
                               "scored before the freeze (deviation D1)"})
    return rows
