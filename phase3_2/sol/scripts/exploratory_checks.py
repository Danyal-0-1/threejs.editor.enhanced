#!/usr/bin/env python3
"""exploratory_checks.py — post hoc, EXPLORATORY checks on a held-out run.

    python3 scripts/exploratory_checks.py --run heldout-20261007a [--root DIR]

Written on 2026-10-09, AFTER the held-out results were seen, to decide how
strongly the paper may word its claims. Nothing here is preregistered or
confirmatory, and nothing changes a registered verdict. Read-only: it reads
the exported CSVs and writes only <run>/analysis_addenda/exploratory/.

  1. cross_family_h4   Is an instruct model's failure pattern INHERITED from its
                       own base model, or does any base model predict it as well
                       (shared site difficulty)? AUROC of -M(base, rule) for
                       M(instruct, rule) < 0 for every base x instruct
                       combination, per grammar family, and the own-base minus
                       other-lineage difference with template-cluster intervals.
  2. roles_by_rung     Share of sites with M < 0 by role, for the instruct
                       models, with 0 and with 4 worked examples, next to Arm B's
                       reversion given reach (generation with 4 examples).
  3. adaptation_cuts   KM median examples to switch by remap density, role and
                       model kind (first computed on 2026-10-09 with a scratch
                       script; now reproducible from the repository).

Intervals: 95% template-cluster bootstrap, B = 2000, seed 20261002, drawn as
scale_analysis.py draws them, with streams named "<grammar>/exploratory/...".
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

from p33 import config as CFG  # noqa: E402
from p33 import kstar  # noqa: E402
from p33 import registry as R  # noqa: E402

B, SEED = 2000, 20261002
GRAMMARS = ("dom", "blk")
STRATA = ("sigil", "keyword", "verb")
# lineages: families that share an organisation, tokenizer and much of their pretraining data
LINEAGE = {"qwen2.5-coder": "Qwen", "qwen2.5": "Qwen", "deepseek-coder": "DeepSeek",
           "llama-3.2": "Llama", "starcoder2": "StarCoder2", "olmo-2": "OLMo"}
csv.field_size_limit(10 ** 9)


def die(msg):
    raise SystemExit(f"REFUSED: {msg}")


def read_csv(path):
    if not os.path.exists(path):
        die(f"{path} does not exist")
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def short(m):
    return m.split("/")[-1]


def draws(T, key):
    """B x T template multiplicities, drawn as scale_analysis.py draws them."""
    rng = random.Random(f"{SEED}/{key}")
    W = np.zeros((B, T))
    for b in range(B):
        for _ in range(T):
            W[b, rng.randrange(T)] += 1
    return W


def interval(v):
    v = np.sort(np.asarray(v, float))
    v = v[np.isfinite(v)]
    n = v.size
    return (float(v[int(0.025 * (n - 1))]), float(v[int(math.ceil(0.975 * (n - 1)))])) if n else (math.nan, math.nan)


def auroc_reps(scores, labels, tix, W=None):
    """Mann-Whitney AUROC (ties 1/2): the point, and one value per template resample."""
    s, y, t = np.asarray(scores, float), np.asarray(labels, float), np.asarray(tix, int)
    o = np.argsort(s, kind="mergesort")
    s, y, t = s[o], y[o], t[o]
    starts = np.r_[0, np.flatnonzero(np.diff(s)) + 1]

    def auc(w):
        wp, wn = w * y, w * (1 - y)
        gp, gn = np.add.reduceat(wp, starts, axis=1), np.add.reduceat(wn, starts, axis=1)
        below = np.cumsum(gn, axis=1) - gn
        with np.errstate(invalid="ignore", divide="ignore"):
            return (gp * (below + 0.5 * gn)).sum(1) / (wp.sum(1) * wn.sum(1))

    point = float(auc(np.ones((1, s.size)))[0])
    return point, (auc(W[:, t]) if W is not None else None)


def md_table(rows, cols):
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    out += ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
    return out


def write_csv(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--root", default=None)
    a = ap.parse_args(argv)
    rd = os.path.join(a.root or CFG.results_root(), a.run)
    out = os.path.join(rd, "analysis_addenda", "exploratory")
    os.makedirs(out, exist_ok=True)
    report = [f"# Exploratory checks — `{a.run}`", "",
              "> **EXPLORATORY, post hoc.** Run on 2026-10-09 after the held-out results were seen, to "
              "decide how strongly the paper may word its claims. Not preregistered; no registered verdict "
              "changes. Made by `phase3_2/sol/scripts/exploratory_checks.py`.", ""]

    # =========================================================================
    # 1. cross-family H4
    # =========================================================================
    arm = [r for r in read_csv(os.path.join(rd, "csv", "arm_a_long.csv"))
           if r["status"] == "ok" and r["condition"] == "rule"]
    M = {}
    tpl_of = {}
    for r in arm:
        M[(r["model"], r["family"], r["site_id"])] = float(r["m_seq"])
        tpl_of[(r["family"], r["site_id"])] = r["template"]
    models = sorted({r["model"] for r in arm})
    bases = [m for m in models if R.spec(m).kind == "base"]
    insts = [m for m in models if R.spec(m).kind == "instruct"]
    frozen = {(r["pair"], r["family"]): float(r["auroc"])
              for r in read_csv(os.path.join(rd, "csv", "h4_metrics_baselines_calibration.csv"))
              if r["record_type"] == "metric" and r["predictor"] == "risk"}

    def lineage(m):
        return LINEAGE[R.spec(m).family]

    cross_rows, summary = [], []
    for g in GRAMMARS:
        sites = sorted({s for (_m, gg, s) in M if gg == g})
        templates = sorted({tpl_of[(g, s)] for s in sites})
        ti = {t: i for i, t in enumerate(templates)}
        tix = [ti[tpl_of[(g, s)]] for s in sites]
        W = draws(len(templates), f"{g}/exploratory/cross_family_h4")
        for inst in sorted(insts, key=lambda m: (lineage(m), R.spec(m).size_b)):
            own = R.spec(inst).pair
            labels = [int(M[(inst, g, s)] < 0) for s in sites]
            auc = {}
            for b in bases:
                auc[b] = auroc_reps([-M[(b, g, s)] for s in sites], labels, tix)[0]
                cross_rows.append({"grammar": g, "instruct": short(inst), "base": short(b),
                                   "relation": ("own" if b == own else "same lineage" if lineage(b) == lineage(inst)
                                                else "other lineage"), "auroc": f"{auc[b]:.4f}"})
            ref = frozen.get((f"{own}|{inst}", g))
            if ref is None or abs(auc[own] - ref) > 1e-5:
                die(f"own-base AUROC {inst} {g}: {auc[own]:.6f} != frozen H4 {ref}")
            other = [b for b in bases if lineage(b) != lineage(inst)]
            same = [b for b in bases if lineage(b) == lineage(inst) and b != own]
            # consensus of the other lineages: the mean margin of their base models at each site
            cons = [-float(np.mean([M[(b, g, s)] for b in other])) for s in sites]
            p_own, r_own = auroc_reps([-M[(own, g, s)] for s in sites], labels, tix, W)
            p_con, r_con = auroc_reps(cons, labels, tix, W)
            diff = r_own - r_con
            lo, hi = interval(diff)
            summary.append({
                "grammar": g, "instruct model": short(inst), "own base": f"{p_own:.3f}",
                "same lineage, other sizes (mean)": f"{np.mean([auc[b] for b in same]):.3f}" if same else "—",
                "other lineages (mean)": f"{np.mean([auc[b] for b in other]):.3f}",
                "other lineages (best)": f"{max(auc[b] for b in other):.3f} ({short(max(other, key=auc.get))})",
                "other-lineage consensus": f"{p_con:.3f}",
                "own − consensus [95% CI]": f"{p_own - p_con:+.3f} [{lo:+.3f}, {hi:+.3f}]",
                "share of own signal reached by consensus": f"{(p_con - 0.5) / (p_own - 0.5):.0%}",
                "_diff": p_own - p_con, "_lo": lo, "_share": (p_con - 0.5) / (p_own - 0.5)})
    write_csv(os.path.join(out, "cross_family_h4.csv"), cross_rows,
              ["grammar", "instruct", "base", "relation", "auroc"])
    cols = ["grammar", "instruct model", "own base", "same lineage, other sizes (mean)", "other lineages (mean)",
            "other lineages (best)", "other-lineage consensus", "own − consensus [95% CI]",
            "share of own signal reached by consensus"]
    write_csv(os.path.join(out, "cross_family_h4_summary.csv"), summary, cols)
    n_pos = sum(1 for r in summary if r["_lo"] > 0)
    shares = [r["_share"] for r in summary]
    report += ["## 1. Is the failure pattern inherited from the model's own base?", "",
               "AUROC of the base-model risk −M(base, rule) for the instruct model's reversions (M < 0), on the "
               "same held-out sites as H4. *Own base* is the registered H4 pair (it reproduces the frozen H4 "
               "AUROC exactly). *Other lineages* are base models from other organisations (Qwen2.5 and "
               "Qwen2.5-Coder count as one lineage). *Consensus* averages the margins of every other-lineage base "
               "at each site: a pure \"site difficulty\" predictor that knows nothing about the instruct model's "
               "own history. The last column is (consensus − 0.5) / (own − 0.5).", ""]
    report += md_table(summary, cols)
    report += ["", f"**Reading.** The own base beats the other-lineage consensus with an interval above zero in "
               f"{n_pos} of {len(summary)} instruct × grammar groups. The consensus reaches "
               f"{min(shares):.0%}–{max(shares):.0%} (median {np.median(shares):.0%}) of the own base's signal "
               "above chance. So a large part of *where* models revert is shared site difficulty, which any base "
               "model reveals, and the remainder is specific to the model's own lineage.", ""]

    # =========================================================================
    # 2. role ordering: margins at 0 and 4 examples vs Arm B (4 examples)
    # =========================================================================
    ext = [r for r in read_csv(os.path.join(rd, "csv", "extinction_rung_long.csv"))
           if r["status"] == "ok" and r["kind"] == "ladder" and r["model"] in set(insts)]
    gens = read_csv(os.path.join(rd, "csv", "arm_b_generations.csv"))
    role_rows = []
    for g in GRAMMARS:
        templates = sorted({r["template"] for r in ext if r["family"] == g} |
                           {r["template"] for r in gens if r["family"] == g})
        ti = {t: i for i, t in enumerate(templates)}
        W = draws(len(templates), f"{g}/exploratory/roles_by_rung")
        for s_ in STRATA:
            rec = {"grammar": g, "role": s_}
            for rung in ("0", "4"):
                n, k = np.zeros(len(templates)), np.zeros(len(templates))
                for r in ext:
                    if r["family"] == g and r["stratum"] == s_ and r["rung"] == rung:
                        n[ti[r["template"]]] += 1
                        k[ti[r["template"]]] += float(r["m_seq"]) < 0
                with np.errstate(invalid="ignore", divide="ignore"):
                    lo, hi = interval((W @ k) / (W @ n))
                rec[f"margins, {rung} examples: M < 0"] = (f"{k.sum() / n.sum():.3f} [{lo:.3f}, {hi:.3f}] "
                                                           f"(n={int(n.sum())})")
                rec[f"_m{rung}"] = k.sum() / n.sum()
            n, k = np.zeros(len(templates)), np.zeros(len(templates))
            for r in gens:
                if r["family"] != g:
                    continue
                for o in json.loads(r["site_obs"] or "[]"):
                    if o["stratum"] == s_ and o["reached"]:
                        n[ti[r["template"]]] += 1
                        k[ti[r["template"]]] += o["outcome"] == "reverted"
            with np.errstate(invalid="ignore", divide="ignore"):
                lo, hi = interval((W @ k) / (W @ n))
            rec["Arm B, 4 examples: old spelling given reached"] = (f"{k.sum() / n.sum():.3f} [{lo:.3f}, {hi:.3f}] "
                                                                     f"(n={int(n.sum())})")
            rec["_b"] = k.sum() / n.sum()
            role_rows.append(rec)
    cols = ["grammar", "role", "margins, 0 examples: M < 0", "margins, 4 examples: M < 0",
            "Arm B, 4 examples: old spelling given reached"]
    write_csv(os.path.join(out, "roles_by_rung.csv"), role_rows, cols)

    def order(g, key):
        rs = sorted([r for r in role_rows if r["grammar"] == g], key=lambda r: -r[key])
        return " > ".join(r["role"] for r in rs)

    report += ["## 2. Does the role ordering in generation match the margins?", "",
               "Instruct models only (the Arm B models), on the extinction subset of sites. *Margins* = share of "
               "sites where the correct spelling loses (M < 0) with the token table and k leak-free worked "
               "examples. *Arm B* = share of reached sites where the generated program uses the old spelling, "
               "with the table and 4 worked examples.", ""]
    report += md_table(role_rows, cols)
    report += ["", "**Orderings (most reversion first):**", ""]
    for g in GRAMMARS:
        report += [f"- `{g}`: margins at 0 examples {order(g, '_m0')}; margins at 4 examples {order(g, '_m4')}; "
                   f"Arm B {order(g, '_b')}."]
    report += ["", "**Reading.** Compare the orderings at the *same* number of examples. A mismatch between 0 and "
               "4 examples means a role is often wrong at first but quickly fixed by examples (or the reverse).", ""]

    # =========================================================================
    # 3. adaptation cuts (KM median examples to switch)
    # =========================================================================
    ks = [r for r in read_csv(os.path.join(rd, "csv", "kstar_survival.csv"))
          if r["record_type"] == "site" and r["status"] == "ok" and r["already_correct"] == "False"]

    def km_cut(key):
        groups = defaultdict(list)
        for r in ks:
            groups[key(r)].append(r)
        rows = []
        for k_, rs in sorted(groups.items()):
            times = [float(r["top_rung"]) if r["censored"] == "True" else float(r["k_star"]) for r in rs]
            km = kstar.kaplan_meier(times, [r["censored"] == "False" for r in rs], population="INITIALLY_WRONG")
            rows.append({"grammar": k_[0], "cut": k_[1], "initially wrong sites": km.n,
                         "KM median examples": "> 32" if km.median is None else f"{km.median:.2f}",
                         "never switched": f"{km.censoring_rate:.0%}"})
        return rows

    cuts = (km_cut(lambda r: (r["family"], "density " + r["lexicon"][:3]))
            + km_cut(lambda r: (r["family"], "role " + r["stratum"]))
            + km_cut(lambda r: (r["family"], R.spec(r["model"]).kind)))
    cols = ["grammar", "cut", "initially wrong sites", "KM median examples", "never switched"]
    write_csv(os.path.join(out, "adaptation_cuts.csv"), cuts, cols)
    report += ["## 3. Adaptation by remap density, role and model kind", "",
               "Kaplan–Meier median number of worked examples before the first switch, pooled over models "
               "(sites wrong at 0 examples). Density has one lexicon each at 25% and 50%, so lexicon and "
               "density are confounded.", ""]
    report += md_table(cuts, cols)

    # =========================================================================
    # 4. how big are the wobbles?
    # =========================================================================
    # The frozen `nonmonotone` flag is true for ANY decrease between consecutive rungs, however
    # small. Here: decreases of a given size, and how far a switched site falls back.
    allsites = [r for r in read_csv(os.path.join(rd, "csv", "kstar_survival.csv"))
                if r["record_type"] == "site" and r["status"] == "ok"]
    wob = []
    for g in GRAMMARS + ("pooled",):
        rs = [r for r in allsites if g == "pooled" or r["family"] == g]
        drops = [max([a - b for a, b in zip(m, m[1:])] + [0.0]) for m in (json.loads(r["margins"]) for r in rs)]
        wrong = [r for r in rs if r["already_correct"] == "False"]
        switched = [r for r in wrong if r["censored"] == "False"]
        fell = [r for r in switched if r["recrossed_down"] == "True"]
        depth = []
        for r in fell:
            m = json.loads(r["margins"])
            first = next(i for i in range(1, len(m)) if m[i - 1] < 0 <= m[i])
            depth.append(min(m[first:]))
        q = np.percentile(depth, [25, 50, 75]) if depth else [math.nan] * 3
        wob.append({
            "grammar": g, "sites": len(rs),
            "any decrease (frozen flag)": f"{np.mean([r['nonmonotone'] == 'True' for r in rs]):.1%}",
            "a decrease > 0.5 nats": f"{np.mean([d > 0.5 for d in drops]):.1%}",
            "a decrease > 1 nat": f"{np.mean([d > 1.0 for d in drops]):.1%}",
            "switched sites that fall back below 0": f"{len(fell)}/{len(switched)} ({len(fell) / len(switched):.1%})",
            "how far they fall: median [IQR], nats": f"{q[1]:+.2f} [{q[0]:+.2f}, {q[2]:+.2f}]",
            "fall below −0.5 nats": f"{np.mean([d < -0.5 for d in depth]):.1%}"})
    cols = ["grammar", "sites", "any decrease (frozen flag)", "a decrease > 0.5 nats", "a decrease > 1 nat",
            "switched sites that fall back below 0", "how far they fall: median [IQR], nats", "fall below −0.5 nats"]
    write_csv(os.path.join(out, "wobble_size.csv"), wob, cols)
    report += ["", "## 4. How big are the wobbles?", "",
               "The frozen `nonmonotone` flag counts *any* decrease between consecutive rungs, however small, "
               "so on its own it overstates instability. Here: the share of curves (all sites, all models) with a "
               "decrease of more than 0.5 or 1 nat between consecutive rungs (1 nat = an odds factor of 2.7), "
               "and, for initially wrong sites that switched, how many fall back below zero later and how far "
               "(the lowest margin after the first switch).", ""]
    report += md_table(wob, cols)
    with open(os.path.join(out, "EXPLORATORY_CHECKS.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(report) + "\n")
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
