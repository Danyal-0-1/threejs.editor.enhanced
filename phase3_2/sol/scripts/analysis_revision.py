#!/usr/bin/env python3
"""analysis_revision.py — re-derive a run's tables, plots and reports from its
saved measurements, and prove that the measurements were not touched.

    python3 scripts/analysis_revision.py snapshot --run RUN --rev REV --reason "..."
    python3 scripts/p33.py export --run RUN
    python3 scripts/analysis_revision.py record   --run RUN --rev REV --command "..."

snapshot  refuses if `analysis_revisions/REV/` already exists. Hashes every
          measurement input (raw shards, checkpoints, merged JSONL and status,
          manifests, logs) and COPIES the current derived outputs (csv/,
          plots/, reports/) to `analysis_revisions/REV/before/`, so the
          previous analysis stays recoverable.
record    re-hashes the inputs and refuses (exit 2) unless every one is
          byte-identical to the snapshot; hashes the regenerated outputs;
          compares every CSV with its saved copy; writes
          `analysis_revision.json` and `ANALYSIS_REVISION.md` with the
          analysis source hashes, git state, package versions, the command,
          the before/after values of every changed cell, and the checks that
          the quantities expected to stay unchanged did.

Nothing outside `analysis_revisions/REV/` is ever written. No model, GPU or
model pin is needed: this is CPU analysis of saved GPU measurements.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import glob
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

import p33  # noqa: E402,F401
from p33 import config as CFG  # noqa: E402

INPUT_GLOBS = ("raw/shards/**/*", "checkpoints/**/*", "merged/*", "manifests/*", "logs/*")
OUTPUT_DIRS = ("csv", "plots", "reports")

# Tables whose every byte must survive a re-derivation that only corrects
# AP / precision@k / power / report code. A difference here is investigated,
# not explained away.
BYTE_IDENTICAL = ("site_inventory", "split_exclusion_audit", "run_completeness",
                  "failed_cells", "job_provenance", "fertility", "arm_a_long",
                  "rule_effect", "paraphrase", "extinction_rung_long",
                  "kstar_survival", "h4_predictions", "arm_b_generations",
                  "arm_b_hurdle", "h5_budget_outcomes", "h5_ir_proof", "h2_did")
H4_EXPECTED_TO_CHANGE = ("auprc", "p_at_10", "p_at_50")
FLOAT_TOL = 1e-9          # cross-platform noise, e.g. a fitted intercept of 8e-17


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_tree(run_dir: str, patterns) -> dict[str, str]:
    out = {}
    for pat in patterns:
        for p in glob.glob(os.path.join(run_dir, pat), recursive=True):
            if os.path.isfile(p) and "/analysis_revisions/" not in p:
                out[os.path.relpath(p, run_dir)] = _sha(p)
    return dict(sorted(out.items()))


def _git() -> dict:
    def run(*a):
        try:
            return subprocess.run(["git", "-C", HERE, *a], capture_output=True,
                                  text=True, timeout=20).stdout.strip()
        except Exception:
            return "UNAVAILABLE"
    status = run("status", "--porcelain")
    return {"commit": run("rev-parse", "HEAD"),
            "dirty": bool(status) and status != "UNAVAILABLE",
            "changed_paths": [l[3:] for l in status.splitlines()][:200]}


def _packages() -> dict:
    from p33 import provenance
    out = provenance.package_versions()
    out["python_executable"] = sys.executable
    out["platform"] = platform.platform()
    return out


def _rev_dir(run: str, rev: str) -> tuple[str, str]:
    rd = CFG.run_dir(run)
    if not os.path.isdir(rd):
        sys.exit(f"no run directory {rd} (is P33_RESULTS_ROOT set?)")
    return rd, os.path.join(rd, "analysis_revisions", rev)


# ---------------------------------------------------------------------------
# snapshot
# ---------------------------------------------------------------------------

def snapshot(a) -> int:
    rd, out = _rev_dir(a.run, a.rev)
    if os.path.exists(out):
        print(f"REFUSED: {out} exists; an analysis revision is written once")
        return 2
    os.makedirs(os.path.join(out, "before"))
    for sub in OUTPUT_DIRS:
        src = os.path.join(rd, sub)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(out, "before", sub), copy_function=shutil.copy2)
    blob = {"run_id": a.run, "revision": a.rev, "snapshot_utc": _now(), "reason": a.reason,
            "freeze_present": os.path.exists(os.path.join(rd, "DEV_FREEZE.json")),
            "inputs": _hash_tree(rd, INPUT_GLOBS),
            "outputs_before": _hash_tree(rd, [f"{s}/*" for s in OUTPUT_DIRS]),
            "analysis_source_hashes_before": CFG.source_hashes(), "git_before": _git()}
    with open(os.path.join(out, "snapshot.json"), "w", encoding="utf-8") as fh:
        json.dump(blob, fh, indent=1, sort_keys=True)
    print(f"snapshot: {len(blob['inputs'])} input files hashed; "
          f"{len(blob['outputs_before'])} derived files copied to {out}/before/")
    return 0


# ---------------------------------------------------------------------------
# record
# ---------------------------------------------------------------------------

def _rows(path: str) -> list[dict]:
    return list(csv.DictReader(open(path, encoding="utf-8"))) if os.path.exists(path) else []


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _same(x, y) -> bool:
    if x == y:
        return True
    fx, fy = _num(x), _num(y)
    return fx is not None and fy is not None and abs(fx - fy) <= FLOAT_TOL * max(1.0, abs(fx))


def _h4_compare(before: list[dict], after: list[dict]) -> dict:
    key = lambda r: (r.get("record_type"), r.get("pair"), r.get("predictor"), r.get("criterion"))  # noqa: E731
    bi, ai = {key(r): r for r in before}, {key(r): r for r in after}
    changed, unexpected = [], []
    for k in sorted(set(bi) | set(ai), key=str):
        b, x = bi.get(k), ai.get(k)
        if b is None or x is None:
            unexpected.append({"key": list(map(str, k)), "problem": "row missing on one side"})
            continue
        for col in sorted(set(b) | set(x)):
            if not _same(b.get(col, ""), x.get(col, "")):
                rec = {"pair": k[1], "predictor": k[2], "criterion": k[3], "column": col,
                       "before": b.get(col, ""), "after": x.get(col, "")}
                (changed if col in H4_EXPECTED_TO_CHANGE else unexpected).append(rec)
    return {"changed_expected": changed, "changed_unexpected": unexpected}


def _power_compare(before: list[dict], after: list[dict]) -> dict:
    def tab(rows, analysis, cols):
        out = {}
        for r in rows:
            if r.get("analysis") == analysis and r.get("status") not in ("NOT RUN",):
                out.setdefault(tuple(r.get(c, "") for c in cols), []).append(r)
        return out
    res = {}
    for analysis, cols, val in (("h4_criterion1", ("n_templates", "icc", "true_auroc"), "power"),
                                ("rule_effect", ("n_templates", "icc"), "power")):
        b, x = tab(before, analysis, cols), tab(after, analysis, cols)
        common = sorted(set(b) & set(x), key=str)
        res[analysis] = {
            "scenarios_before": len(b), "scenarios_after": len(x),
            "duplicate_keys_after": sorted(str(k) for k, v in x.items() if len(v) > 1),
            "values_equal_on_common_scenarios": all(_same(b[k][0].get(val), x[k][0].get(val)) for k in common),
            "n_common": len(common)}
    sb = [r for r in before if r.get("analysis") == "h4_smallest_detectable_auroc"]
    sa = [r for r in after if r.get("analysis") == "h4_smallest_detectable_auroc"]
    res["h4_smallest_detectable_auroc"] = {
        "rows_before": len(sb), "distinct_rows_before": len({tuple(sorted(r.items())) for r in sb}),
        "rows_after": len(sa),
        "before": sorted({(r["n_templates"], r["icc"], r.get("value", "")) for r in sb}, key=lambda t: (float(t[0]), float(t[1]))),
        "after": [{k: r.get(k, "") for k in ("n_templates", "icc", "icc_source", "value", "value_status", "t_status")} for r in sa]}
    return res


def _summary_lines(path: str) -> list[str]:
    if not os.path.exists(path):
        return []
    return [l.strip() for l in open(path, encoding="utf-8") if l.strip().startswith("- **") and "/**" in l]


def record(a) -> int:
    rd, out = _rev_dir(a.run, a.rev)
    snap_p = os.path.join(out, "snapshot.json")
    if not os.path.exists(snap_p):
        print(f"REFUSED: no snapshot at {snap_p}; run `snapshot` before regenerating")
        return 2
    snap = json.load(open(snap_p, encoding="utf-8"))
    inputs_now = _hash_tree(rd, INPUT_GLOBS)
    drift = sorted(k for k in set(snap["inputs"]) | set(inputs_now)
                   if snap["inputs"].get(k) != inputs_now.get(k))
    if drift:
        print(f"REFUSED: {len(drift)} measurement input(s) changed since the snapshot, "
              f"e.g. {drift[:5]}")
        return 2
    outputs_after = _hash_tree(rd, [f"{s}/*" for s in OUTPUT_DIRS])
    before_csv = os.path.join(out, "before", "csv")
    from p33.export import CSV_NAMES
    files = {}
    for name in CSV_NAMES:
        b, x = os.path.join(before_csv, f"{name}.csv"), os.path.join(rd, "csv", f"{name}.csv")
        same_bytes = os.path.exists(b) and os.path.exists(x) and _sha(b) == _sha(x)
        files[name] = {"identical_bytes": same_bytes,
                       "rows_before": len(_rows(b)), "rows_after": len(_rows(x))}
    checks = []
    for name in BYTE_IDENTICAL:
        ok = files[name]["identical_bytes"]
        if not ok:   # equal within float noise counts, but is reported as such
            rb, rx = _rows(os.path.join(before_csv, f"{name}.csv")), _rows(os.path.join(rd, "csv", f"{name}.csv"))
            ok = len(rb) == len(rx) and all(_same(u.get(c, ""), v.get(c, "")) for u, v in zip(rb, rx)
                                            for c in set(u) | set(v))
            checks.append({"check": f"{name}.csv unchanged", "passed": ok,
                           "detail": "equal within float tolerance, bytes differ" if ok else "VALUES DIFFER"})
        else:
            checks.append({"check": f"{name}.csv unchanged", "passed": True, "detail": "byte-identical"})
    h4 = _h4_compare(_rows(os.path.join(before_csv, "h4_metrics_baselines_calibration.csv")),
                     _rows(os.path.join(rd, "csv", "h4_metrics_baselines_calibration.csv")))
    checks.append({"check": "H4: only AP and precision@k columns changed",
                   "passed": not h4["changed_unexpected"],
                   "detail": f"{len(h4['changed_expected'])} expected cell changes; "
                             f"{len(h4['changed_unexpected'])} unexpected"})
    pw = _power_compare(_rows(os.path.join(before_csv, "power.csv")),
                        _rows(os.path.join(rd, "csv", "power.csv")))
    for an in ("h4_criterion1", "rule_effect"):
        checks.append({"check": f"power: {an} values unchanged on every shared scenario",
                       "passed": pw[an]["values_equal_on_common_scenarios"] and not pw[an]["duplicate_keys_after"],
                       "detail": f"{pw[an]['n_common']} shared scenarios; duplicates after: {pw[an]['duplicate_keys_after']}"})
    blob = {
        "run_id": a.run, "revision": a.rev, "record_utc": _now(), "snapshot_utc": snap["snapshot_utc"],
        "reason": snap.get("reason"), "command": a.command,
        "gpu_measurements_reused": True,
        "statement": ("Derived tables, plots and reports were regenerated from the run's saved "
                      "merged measurements by CPU code. No model was loaded, no site was "
                      "re-scored, and every measurement input is byte-identical to the snapshot."),
        "inputs_verified_identical": len(inputs_now), "input_hashes": inputs_now,
        "outputs_before": snap["outputs_before"], "outputs_after": outputs_after,
        "analysis_source_hashes": CFG.source_hashes(),
        "analysis_source_digest": hashlib.sha256(json.dumps(CFG.source_hashes(), sort_keys=True)
                                                 .encode()).hexdigest(),
        "git": _git(), "packages": _packages(),
        "csv_files": files, "h4_metric_changes": h4, "power": pw, "checks": checks,
        "run_summary_artifacts": {"before": _summary_lines(os.path.join(out, "before", "reports", "RUN_SUMMARY.md")),
                                  "after": _summary_lines(os.path.join(rd, "reports", "RUN_SUMMARY.md"))},
        "all_checks_passed": all(c["passed"] for c in checks)}
    with open(os.path.join(out, "analysis_revision.json"), "w", encoding="utf-8") as fh:
        json.dump(blob, fh, indent=1, sort_keys=True)
    with open(os.path.join(out, "ANALYSIS_REVISION.md"), "w", encoding="utf-8") as fh:
        fh.write(_markdown(blob, a.notes))
    print(f"record: inputs byte-identical ({len(inputs_now)} files); "
          f"{sum(1 for f in files.values() if not f['identical_bytes'])} CSV(s) changed; "
          f"checks {'ALL PASSED' if blob['all_checks_passed'] else 'FAILED'} -> {out}")
    return 0 if blob["all_checks_passed"] else 3


def _markdown(b: dict, notes_path: str | None) -> str:
    s = [f"# Analysis revision `{b['revision']}` — run `{b['run_id']}`", "",
         f"- recorded {b['record_utc']} (snapshot {b['snapshot_utc']})",
         f"- reason: {b['reason']}", f"- command: `{b['command']}`",
         f"- git: `{b['git']['commit'][:12]}` (dirty: {b['git']['dirty']})",
         f"- {b['statement']}",
         f"- analysis code: {len(b['analysis_source_hashes'])} source files, digest of their hashes "
         f"`{b['analysis_source_digest'][:16]}` (the same digest means the same analysis code)",
         "- environment: " + ", ".join(f"{k} {b['packages'].get(k)}" for k in
                                       ("python", "numpy", "matplotlib", "transformers", "lark")),
         ""]
    if notes_path and os.path.exists(notes_path):
        s += [open(notes_path, encoding="utf-8").read().rstrip(), ""]
    s += ["## Checks", "", "| check | passed | detail |", "|---|---|---|"]
    s += [f"| {c['check']} | {'yes' if c['passed'] else '**NO**'} | {c['detail']} |" for c in b["checks"]]
    s += ["", "## CSV files", "", "| file | bytes identical | rows before | rows after |", "|---|---|---:|---:|"]
    s += [f"| {n} | {'yes' if f['identical_bytes'] else 'no'} | {f['rows_before']} | {f['rows_after']} |"
          for n, f in b["csv_files"].items()]
    s += ["", "## H4 metric cells that changed (expected: AP and precision@k only)", "",
          "| pair | predictor | column | before | after |", "|---|---|---|---|---|"]
    s += [f"| {c['pair'].split('|')[0].split('/')[-1]} | {c['predictor']} | {c['column']} | {c['before']} | {c['after']} |"
          for c in b["h4_metric_changes"]["changed_expected"]]
    if b["h4_metric_changes"]["changed_unexpected"]:
        s += ["", "**Unexpected H4 changes:**", "```", json.dumps(b["h4_metric_changes"]["changed_unexpected"], indent=1), "```"]
    p = b["power"]["h4_smallest_detectable_auroc"]
    s += ["", "## Power: smallest detectable AUROC", "",
          f"Before: {p['rows_before']} rows, {p['distinct_rows_before']} distinct, every one computed with the pilot ICC "
          f"whatever ICC its loop iteration stood for. After: {p['rows_after']} rows, one per (template count, ICC) scenario.", "",
          "| templates | ICC | ICC source | smallest detectable AUROC | status | templates vs corpus |", "|---:|---:|---|---|---|---|"]
    s += [f"| {r['n_templates']} | {r['icc']} | {r['icc_source']} | {r['value'] or '—'} | {r['value_status']} | {r['t_status']} |"
          for r in p["after"]]
    s += ["", "## RUN_SUMMARY artifact lines", "", "Before:", ""] + [f"    {l}" for l in b["run_summary_artifacts"]["before"]]
    s += ["", "After:", ""] + [f"    {l}" for l in b["run_summary_artifacts"]["after"]]
    s += ["", f"Measurement inputs verified byte-identical: **{b['inputs_verified_identical']} files** "
              "(raw shards, checkpoints, merged JSONL and status, job and other manifests, logs). "
              "Hashes are in `analysis_revision.json`; the previous derived outputs are in `before/`.", ""]
    return "\n".join(s)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot")
    s.add_argument("--run", required=True)
    s.add_argument("--rev", required=True)
    s.add_argument("--reason", required=True)
    r = sub.add_parser("record")
    r.add_argument("--run", required=True)
    r.add_argument("--rev", required=True)
    r.add_argument("--command", required=True)
    r.add_argument("--notes", default=None, help="Markdown file appended to the record")
    a = ap.parse_args(argv)
    return snapshot(a) if a.cmd == "snapshot" else record(a)


if __name__ == "__main__":
    raise SystemExit(main())
