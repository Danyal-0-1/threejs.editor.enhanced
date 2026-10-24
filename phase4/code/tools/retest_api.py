#!/usr/bin/env python3
"""retest_api.py — score a sample of a run's Arm A sites again, through the API, and compare.

    python3 tools/retest_api.py --run dev-20261023a [--n 300] [--seed 20261023] [--root DIR]

WHY. A served model is not a fixed file of weights on our own GPU. The same request, sent twice to
the same deployment, can come back with slightly different log-probabilities, because the server
batches it with other users' requests and the arithmetic order changes with the batch. The probe
of 2026-10-22 asked short questions, one at a time, on a quiet server, and got bit-identical
answers. During the run of 2026-10-23, one site re-scored by hand differed by 0.04 nats. This
tool measures that variation on a fixed random sample: how far margins move, and how often a
margin changes sign, which is what reversion counts.

WHAT. For each served model of the run: `--n` sites of the `rule` condition, drawn with a fixed
seed from the run's merged Arm A rows, rebuilt exactly as the pipeline builds them (the same plan,
prompt and prefix), and scored again by the same pinned deployment (the scorer refuses another
one). Nothing in the run is changed.

OUTPUT: <run>/analysis_addenda/retest/retest_<UTC date>.csv (one row per site) and
SUMMARY.md (per model: median and 95th-percentile |change|, exact repeats, sign changes).
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime
import json
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from p4.experiments import pipeline as PL  # noqa: E402
from p4.governance import registry as R  # noqa: E402
from p4.prompts import prompts  # noqa: E402
from p4.runtime import config as CFG  # noqa: E402
from p4.scoring.api import APIScorer  # noqa: E402
from p4.scoring.margins import ScoringError, build_prefix  # noqa: E402


def quantile(v, q):
    v = sorted(v)
    if not v:
        return float("nan")
    i = q * (len(v) - 1)
    lo, hi = int(i), min(int(i) + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--n", type=int, default=300, help="sites per model")
    ap.add_argument("--seed", type=int, default=20261023)
    ap.add_argument("--root", default=None)
    a = ap.parse_args(argv)
    root = a.root or CFG.results_root()
    rd = os.path.join(root, a.run)
    cfg = CFG.RunConfig.from_dict(json.load(open(os.path.join(rd, "manifests", "run_config.json")))["config"])
    pins = json.load(open(os.path.join(root, "model_pins.json")))["pins"]
    rows = defaultdict(list)
    with open(os.path.join(rd, "merged", "arm_a.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["status"] == "ok" and r["condition"] == "rule" and R.is_api(r["model"]):
                rows[r["model"]].append(r)
    plan = PL.build_plan(cfg, site_limit=cfg.site_limit)
    sites = {s.site_id: s for s in plan.all_sites()}
    out_dir = os.path.join(rd, "analysis_addenda", "retest")
    os.makedirs(out_dir, exist_ok=True)
    day = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    def one_model(m):
        out = []
        pool = sorted(rows[m], key=lambda r: r["row_key"])
        sample = random.Random(f"{a.seed}/{m}").sample(pool, min(a.n, len(pool)))
        sc = APIScorer.for_model(m, pin=pins.get(m))
        started = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        for r in sample:
            s = sites[r["site_id"]]
            pb = prompts.bundle("rule", PL.phi(s.phi_id))
            try:
                ps = sc.score_pair_detailed(build_prefix(s, rule=pb.text), s.correct, s.competitor)
                new, why = ps.m_seq, ""
            except ScoringError as exc:
                new, why = float("nan"), f"{type(exc).__name__}"
            old = float(r["m_seq"])
            out.append({"model": m, "family": r["family"], "lexicon": r["lexicon"], "site_id": r["site_id"],
                        "m_run": repr(old), "m_retest": repr(new), "change": repr(new - old),
                        "same_bits": str(new == old), "reverted_run": str(old < 0),
                        "reverted_retest": str(new < 0), "sign_changed": str((old < 0) != (new < 0)),
                        "retest_started_utc": started, "revision": sc.revision, "note": why})
        sc.release()
        print(f"{m}: {len(sample)} sites re-scored", flush=True)
        return out

    models = [x for x in cfg.models if R.is_api(x)]
    with cf.ThreadPoolExecutor(max_workers=len(models)) as ex:      # models side by side, sites in order
        out = [r for part in ex.map(one_model, models) for r in part]
    path = os.path.join(out_dir, f"retest_{day}.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    lines = [f"# Re-scoring a sample of {a.run}'s Arm A sites ({day})", "",
             f"{a.n} sites of the `rule` condition per served model, drawn with seed {a.seed} "
             "(`random.Random(f'{seed}/{model}')`), rebuilt by the pipeline and scored again by the same "
             f"pinned deployment. Rows: `{os.path.basename(path)}`.", "",
             "| model | sites | same to the bit | median abs. change | 95th pct | max | sign changed | of those within 0.1 nat |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    by = defaultdict(list)
    for r in out:
        by[r["model"]].append(r)
    for m, rs in by.items():
        ch = [abs(float(r["change"])) for r in rs if r["note"] == ""]
        flips = [r for r in rs if r["sign_changed"] == "True"]
        near = sum(1 for r in flips if abs(float(r["m_run"])) < 0.1)
        lines.append(f"| {m} | {len(rs)} | {sum(r['same_bits'] == 'True' for r in rs)} | {quantile(ch, 0.5):.4f} | "
                     f"{quantile(ch, 0.95):.4f} | {max(ch):.4f} | {len(flips)} | {near} |")
    with open(os.path.join(out_dir, "SUMMARY.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
