#!/usr/bin/env python3
"""scale_analysis.py — the scale analysis pre-specified by deviation D10, as specified by D11.

    python3 scripts/scale_analysis.py --run heldout-20261007a

D10 registered a two-sided analysis with no predicted direction: the reversion
rate and the H4 AUROC as functions of log(parameters) within the Qwen2.5-Coder
ladder, on held-out mappings, per grammar family and never pooled across
families. The frozen pipeline exports the per-model inputs but not this
analysis, so it runs here, AFTER the frozen export, on its CSVs only:

  ladder     registry family "qwen2.5-coder": 0.5, 1.5, 3, 7, 14, 32 (registry size_b)
  rows       Arm A, status ok, the rule condition, every lexicon of the held-out run
  reversion  per model: share of rows with m_seq < 0 (base and instruct separately)
  H4 AUROC   per base/instruct pair: AUROC of `risk` for `label` (p33.h4.auroc)
  statistic  OLS slope of the outcome on log10(size), one point per size
  interval   95% percentile template-cluster bootstrap within the family: templates
             resampled with replacement (multiplicity kept), the same draw for every
             size; B = 2000, seed 20261002 (the registered bootstrap settings)
  p value    two-sided bootstrap p = min(1, 2 min(P*(b <= 0), P*(b >= 0)))
  Holm       over all slopes reported (reversion: base, instruct x dom, blk; AUROC: dom, blk)

It never re-scores, never writes inside csv/, plots/ or reports/, and refuses if
a ladder model or input file is missing. Output: <run>/analysis_addenda/d11_scale/.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import math
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SOL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SOL, "src"))

from p33 import config as CFG  # noqa: E402
from p33 import h4, registry  # noqa: E402

LADDER_FAMILY = "qwen2.5-coder"
B_DEFAULT = 2000
SEED_DEFAULT = 20261002


def ladder() -> list[tuple[float, str, str]]:
    """(size_b, base id, instruct id) for the Qwen2.5-Coder ladder, smallest first."""
    out = []
    for s in registry.REGISTRY.values():
        if s.family == LADDER_FAMILY and s.kind == "base":
            out.append((s.size_b, s.id, s.pair))
    return sorted(out)


def slope(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return None if sxx == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def holm(pvals: dict[str, float]) -> dict[str, float]:
    order = sorted(pvals, key=lambda k: pvals[k])
    m, running, out = len(order), 0.0, {}
    for i, k in enumerate(order):
        running = max(running, min(1.0, (m - i) * pvals[k]))
        out[k] = running
    return out


def _read(path: str) -> list[dict]:
    if not os.path.exists(path):
        raise SystemExit(f"REFUSED: {path} does not exist; run the frozen export first")
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def reversion_inputs(rows: list[dict], fam: str, models: list[str]) -> dict:
    """Per model and template: (rows, reversions), rule condition, status ok."""
    agg = {m: defaultdict(lambda: [0, 0]) for m in models}
    for r in rows:
        if r["family"] != fam or r["condition"] != "rule" or r["status"] != "ok" or r["model"] not in agg:
            continue
        a = agg[r["model"]][r["template"]]
        a[0] += 1
        a[1] += float(r["m_seq"]) < 0
    return agg


def auroc_inputs(rows: list[dict], fam: str, pairs: list[str]) -> dict:
    """Per pair and template: the (risk, label) rows of that template."""
    agg = {p: defaultdict(list) for p in pairs}
    for r in rows:
        if r["family"] != fam or r["pair"] not in agg:
            continue
        agg[r["pair"]][r["template"]].append((float(r["risk"]), int(r["label"])))
    return agg


def rate(per_t: dict, weights: dict) -> float | None:
    n = sum(per_t[t][0] * w for t, w in weights.items() if t in per_t)
    k = sum(per_t[t][1] * w for t, w in weights.items() if t in per_t)
    return k / n if n else None


def auroc_w(per_t: dict, weights: dict) -> float | None:
    sc, lb = [], []
    for t, w in weights.items():
        for s, y in per_t.get(t, ()):
            sc.extend([s] * w)
            lb.extend([y] * w)
    return h4.auroc(sc, lb) if sc else None


def analyse(arm_rows, h4_rows, *, B: int = B_DEFAULT, seed: int = SEED_DEFAULT) -> dict:
    lad = ladder()
    sizes = [s for s, _b, _i in lad]
    xs = [math.log10(s) for s in sizes]
    present = {r["model"] for r in arm_rows}
    missing = [m for _s, b, i in lad for m in (b, i) if m not in present]
    if missing:
        raise SystemExit(f"REFUSED: ladder models missing from Arm A: {missing}")
    fams = sorted({r["family"] for r in arm_rows})
    results, pvals = [], {}
    for fam in fams:
        series = {
            ("reversion", "base"): ("rate", reversion_inputs(arm_rows, fam, [b for _s, b, _i in lad]),
                                    [b for _s, b, _i in lad]),
            ("reversion", "instruct"): ("rate", reversion_inputs(arm_rows, fam, [i for _s, _b, i in lad]),
                                        [i for _s, _b, i in lad]),
            ("h4_auroc", "pair"): ("auroc", auroc_inputs(h4_rows, fam, [f"{b}|{i}" for _s, b, i in lad]),
                                   [f"{b}|{i}" for _s, b, i in lad]),
        }
        templates = sorted({r["template"] for r in arm_rows if r["family"] == fam})
        for (outcome, kind), (fn, agg, keys) in series.items():
            f = rate if fn == "rate" else auroc_w
            ones = {t: 1 for t in templates}
            point = [f(agg[k], ones) for k in keys]
            if any(v is None for v in point):
                results.append({"family": fam, "outcome": outcome, "kind": kind, "status": "NOT ESTIMABLE",
                                "detail": f"undefined at sizes {[s for s, v in zip(sizes, point) if v is None]}"})
                continue
            b0 = slope(xs, point)
            rng = random.Random(f"{seed}/{fam}/{outcome}/{kind}")
            boots, dropped = [], 0
            per_size = [[] for _ in keys]
            for _ in range(B):
                draw = defaultdict(int)
                for _j in range(len(templates)):
                    draw[templates[rng.randrange(len(templates))]] += 1
                vals = [f(agg[k], draw) for k in keys]
                if any(v is None for v in vals):
                    dropped += 1
                    continue
                boots.append(slope(xs, vals))
                for j, v in enumerate(vals):
                    per_size[j].append(v)
            boots.sort()
            n = len(boots)
            lo, hi = boots[int(0.025 * (n - 1))], boots[int(math.ceil(0.975 * (n - 1)))]
            p = min(1.0, 2 * min(sum(b <= 0 for b in boots) / n, sum(b >= 0 for b in boots) / n))
            key = f"{outcome}/{kind}/{fam}"
            pvals[key] = p
            rec = {"family": fam, "outcome": outcome, "kind": kind, "status": "ESTIMATED",
                   "slope_per_log10_size": b0, "ci_lo": lo, "ci_hi": hi, "p_two_sided": p,
                   "n_templates": len(templates), "B": B, "seed": seed, "replicates_used": n,
                   "replicates_dropped": dropped}
            for j, (s, v) in enumerate(zip(sizes, point)):
                ps = sorted(per_size[j])
                rec[f"value_{s:g}B"] = v
                rec[f"ci_{s:g}B"] = [ps[int(0.025 * (len(ps) - 1))], ps[int(math.ceil(0.975 * (len(ps) - 1)))]]
            results.append(rec)
    adj = holm(pvals)
    for r in results:
        k = f"{r['outcome']}/{r['kind']}/{r['family']}"
        if k in adj:
            r["p_holm"] = adj[k]
    return {"ladder_sizes_b": sizes, "results": results}


def _md(out: dict, meta: dict) -> str:
    s = [f"# Scale analysis (D10, specified by D11) — `{meta['run']}`", "",
         f"- computed {meta['utc']} from the frozen export's CSVs (no re-scoring)",
         f"- ladder: Qwen2.5-Coder {', '.join(f'{x:g}B' for x in out['ladder_sizes_b'])}; "
         "x = log10(parameters, billions)",
         "- two-sided, no predicted direction; templates resampled within each family; Holm over every slope below",
         "- size is not randomized: the ladder holds the tokenizer and training recipe fixed, "
         "but sizes may differ in other ways, so a trend is an association",
         "- `blk` cells are HELDOUT-WEAK-FAMILY (D1); the 3B pair is HELDOUT-WEAKENED (D2)", "",
         "| family | outcome | models | slope per 10x size | 95% CI | p (two-sided) | p (Holm) |",
         "|---|---|---|---:|---|---:|---:|"]
    for r in out["results"]:
        if r["status"] != "ESTIMATED":
            s.append(f"| {r['family']} | {r['outcome']} | {r['kind']} | {r['status']} | {r['detail']} | | |")
            continue
        s.append(f"| {r['family']} | {r['outcome']} | {r['kind']} | {r['slope_per_log10_size']:+.4f} | "
                 f"[{r['ci_lo']:+.4f}, {r['ci_hi']:+.4f}] | {r['p_two_sided']:.4f} | {r['p_holm']:.4f} |")
    s += ["", "## Per size", "", "| family | outcome | models | " +
          " | ".join(f"{x:g}B" for x in out["ladder_sizes_b"]) + " |",
          "|---|---|---|" + "---|" * len(out["ladder_sizes_b"])]
    for r in out["results"]:
        if r["status"] == "ESTIMATED":
            cells = [f"{r[f'value_{x:g}B']:.3f} [{r[f'ci_{x:g}B'][0]:.3f}, {r[f'ci_{x:g}B'][1]:.3f}]"
                     for x in out["ladder_sizes_b"]]
            s.append(f"| {r['family']} | {r['outcome']} | {r['kind']} | " + " | ".join(cells) + " |")
    s += ["", "Inputs and their hashes: `inputs.json`.", ""]
    return "\n".join(s)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--B", type=int, default=B_DEFAULT)
    a = ap.parse_args(argv)
    rd = os.path.join(CFG.results_root(), a.run)
    paths = {n: os.path.join(rd, "csv", f"{n}.csv") for n in ("arm_a_long", "h4_predictions")}
    arm, h4p = _read(paths["arm_a_long"]), _read(paths["h4_predictions"])
    stages = {r.get("stage") for r in arm}
    if stages != {"heldout"}:
        raise SystemExit(f"REFUSED: D11 is defined on the held-out run; stages here: {sorted(stages)}")
    out = analyse(arm, h4p, B=a.B)
    od = os.path.join(rd, "analysis_addenda", "d11_scale")
    os.makedirs(od, exist_ok=True)
    meta = {"run": a.run, "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "inputs": {n: {"path": os.path.relpath(p, rd), "sha256": CFG.sha256_file(p)} for n, p in paths.items()},
            "script_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest()}
    with open(os.path.join(od, "inputs.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1)
    flat = [{k: (json.dumps(v) if isinstance(v, list) else v) for k, v in r.items()} for r in out["results"]]
    cols = sorted({k for r in flat for k in r})
    with open(os.path.join(od, "scale_analysis.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(flat)
    with open(os.path.join(od, "SCALE_ANALYSIS.md"), "w", encoding="utf-8") as fh:
        fh.write(_md(out, meta))
    print(f"scale analysis: {len(out['results'])} slopes -> {od}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
