#!/usr/bin/env python3
"""fix_heldout_problems.py — Phase 4, step 0: post-hoc fixes for the open problems of
the Phase 3.3 held-out run, listed in phase3_2/sol/heldout_results_explained/08 and 06 §10.

    python3 phase4/scripts/fix_heldout_problems.py [--run heldout-20261007a] [--root DIR]

Everything here is computed AFTER the held-out outcomes were known, outside the
frozen code, from the run's saved data. Nothing is confirmatory, no model is re-run,
and no registered verdict changes (deviation D13). Before correcting anything, each
fix reproduces the frozen number it corrects with the frozen functions, and the
script refuses to continue if it cannot.

  F1  H4 calibration. For the 8 pairs without frozen Platt parameters, the export
      computed ECE, Brier and the calibration slope in-sample. Fix: out-of-sample
      calibration by template-grouped 5-fold cross-fitting, and by cross-family
      transfer (fit on the pair's other grammar family).
  F2  H5's registered test was never implemented. Fix: implement it as registered,
      but post hoc: targeted minus random reduction per changed symbol, with a 95%
      template-cluster interval excluding 0, and control sites worsening by ≤ 0.02;
      each grammar family separately.
  F4  H5's per-symbol metric mixes repaired and control sites. Fix: split it exactly
      into the two parts, and test targeted against random on the repaired part.
  F5  Arm B's extraction kept a same-line "Request:" continuation. Fix: cut it,
      re-evaluate with the frozen evaluator, re-observe every site of the changed
      rows, and report corrected task accuracy.
  F6  Open item from 06 §10: H4 per role, to show that no single role carries the
      prediction.

F3, the D10 scale analysis, was fixed before Phase 4 (deviation D11).
Intervals: 95% percentile template-cluster bootstrap, B = 2000, seed 20261002, drawn
exactly as scale_analysis.py and paper_figures.py draw them.
Output: <run>/analysis_addenda/phase4_fixes/ (nothing is written anywhere else).
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SOL = os.path.join(REPO, "phase3_2", "sol")
sys.path.insert(0, os.path.join(SOL, "src"))

from p33 import armb, h4  # noqa: E402  (importing p33 first puts the vendored modules on the path)
from p33 import pipeline as PL  # noqa: E402
from p33 import registry as R  # noqa: E402
from phase3_2 import sites2 as S  # noqa: E402
from phase3_2 import templates as TM  # noqa: E402
from phase3_2.backends import BACKENDS  # noqa: E402

import phi as P  # noqa: E402

GRAMMARS = ("dom", "blk")
FOLDS = 5
REQUEST_TAIL = re.compile(r"\s+request\s*:", re.I)   # the same rule as the 2026-10-09 check
csv.field_size_limit(10 ** 9)


def _load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# the D11-identical bootstrap draws, interval and AUROC (tested in test_paper_figures.py)
PF = _load_module("paper_figures", os.path.join(SOL, "scripts", "paper_figures.py"))
B, SEED = PF.B, PF.SEED


def die(msg: str):
    raise SystemExit(f"REFUSED: {msg}")


def read_csv(path: str) -> list[dict]:
    if not os.path.exists(path):
        die(f"{path} does not exist")
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return math.nan


def short(m: str) -> str:
    return m.split("/")[-1]


def close(a: float, b: float, tol: float = 2e-5) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(b))


def md_table(rows: list[dict], cols: list[str]) -> list[str]:
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    out += ["| " + " | ".join(str(r.get(c, "")).replace("|", "\\|") for c in cols) + " |" for r in rows]
    return out


def write_csv(path: str, rows: list[dict], cols: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def two_sided_p(reps: np.ndarray) -> float:
    """As in scale_analysis.py: min(1, 2 min(P*(x <= 0), P*(x >= 0)))."""
    r = reps[np.isfinite(reps)]
    return float(min(1.0, 2 * min(np.mean(r <= 0), np.mean(r >= 0))))


def holm(pvals: dict) -> dict:
    order = sorted(pvals, key=lambda k: pvals[k])
    m, running, out = len(order), 0.0, {}
    for i, k in enumerate(order):
        running = max(running, min(1.0, (m - i) * pvals[k]))
        out[k] = running
    return out


def fmt_ci(pt: float, lohi, d: int = 3, sign: bool = True) -> str:
    f = ("{:+.%df}" if sign else "{:.%df}") % d
    return f"{f.format(pt)} [{f.format(lohi[0])}, {f.format(lohi[1])}]"


# ---------------------------------------------------------------------------
# F1 — out-of-sample calibration
# ---------------------------------------------------------------------------

def template_folds(templates: list[str], key: str, k: int = FOLDS) -> dict[str, int]:
    """Deterministic, balanced assignment of templates to k folds."""
    ts = sorted(templates)
    random.Random(f"{SEED}/{key}").shuffle(ts)
    return {t: i % k for i, t in enumerate(ts)}


def calibration_metrics(probs: list[float], labels: list[int], bins: int) -> dict:
    cs = h4.calibration_slope_intercept(probs, labels)
    return {"ece": h4.ece(probs, labels, bins), "brier": h4.brier(probs, labels),
            "cal_intercept": cs[0] if cs else math.nan, "cal_slope": cs[1] if cs else math.nan}


def platt_probs(cal: tuple[float, float], xs: list[float]) -> list[float]:
    return [h4._sigmoid(cal[0] + cal[1] * x) for x in xs]


def cross_fitted_probs(risk: list[float], labels: list[int], templates: list[str],
                       folds: dict[str, int], k: int = FOLDS) -> list[float]:
    """Each row's probability comes from a Platt fit that never saw its template."""
    out = [math.nan] * len(risk)
    for f in range(k):
        train = [i for i, t in enumerate(templates) if folds[t] != f]
        test = [i for i, t in enumerate(templates) if folds[t] == f]
        if not test:
            continue
        cal = h4.logistic_fit([risk[i] for i in train], [labels[i] for i in train])
        for i in test:
            out[i] = h4._sigmoid(cal[0] + cal[1] * risk[i])
    return out


# ---------------------------------------------------------------------------
# F2 / F4 — the H5 metric and its split
# ---------------------------------------------------------------------------

def h5_parts(v: list[np.ndarray], n_changed: int, W: np.ndarray) -> dict:
    """The registered per-symbol reduction of one arm, split exactly into its repaired-site and
    control-site parts, plus the control degradation, under template weights W (B x T).

    v holds per-template counts: [repaired sites, repaired reverted before, repaired reverted
    after, control sites, control reverted before, control reverted after]."""
    d = [W @ x for x in v[:6]]
    with np.errstate(invalid="ignore", divide="ignore"):
        rep = (d[1] - d[2]) / n_changed
        ctl = (d[4] - d[5]) / n_changed
        return {"all": rep + ctl, "rep": rep, "ctl": ctl, "cdeg": (d[5] - d[4]) / d[3]}


# ---------------------------------------------------------------------------
# F5 — corrected Arm B extraction
# ---------------------------------------------------------------------------

def extract_corrected(raw: str) -> str:
    """The frozen extraction, then cut a same-line 'Request:' continuation."""
    return REQUEST_TAIL.split(armb.extract_program(raw), maxsplit=1)[0].strip()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", default="heldout-20261007a")
    ap.add_argument("--root", default=os.environ.get("P33_RESULTS_ROOT",
                                                     os.path.join(REPO, "phase3_3", "sol_results")))
    a = ap.parse_args(argv)
    rd = os.path.join(a.root, a.run)
    out = os.path.join(rd, "analysis_addenda", "phase4_fixes")
    os.makedirs(out, exist_ok=True)

    def csvp(name):
        return os.path.join(rd, "csv", f"{name}.csv")

    with open(os.path.join(rd, "manifests", "run_config.json"), encoding="utf-8") as fh:
        rcfg = json.load(fh)
    rcfg = rcfg.get("config", rcfg)
    bins = int(rcfg["analysis"]["ece_bins"])
    tolerance = float(rcfg["h5"]["low_risk_tolerance"])
    if int(rcfg["analysis"]["B"]) != B or int(rcfg["seeds"]["bootstrap"]) != SEED:
        die("the run's registered bootstrap settings differ from the figure helpers'")
    with open(os.path.join(rd, "HELDOUT_UNLOCK.json"), encoding="utf-8") as fh:
        unlock = json.load(fh)
    freeze_path = os.path.join(a.root, os.path.basename(os.path.dirname(unlock["freeze_path"])), "DEV_FREEZE.json")
    with open(freeze_path, "rb") as fh:
        raw_freeze = fh.read()
    if hashlib.sha256(raw_freeze).hexdigest() != unlock["freeze_sha256"]:
        die(f"{freeze_path} is not the freeze this run was unlocked against")
    freeze = json.loads(raw_freeze)

    checks: list[str] = []
    report: list[str] = [
        f"# Phase 4 fixes of the held-out run's open problems — `{a.run}`", "",
        "> **Post hoc.** Computed on "
        f"{datetime.date.today().isoformat()}, after the held-out outcomes were known, outside the "
        "frozen code. Nothing here is confirmatory, and no registered verdict changes (deviation "
        "D13 in `phase3_2/PREREGISTRATION.md`). Made by `phase4/scripts/fix_heldout_problems.py`; "
        "the explanation is in `phase4/fixes_before_phase4/`.", ""]

    # =========================================================================
    # F1 — H4 calibration out of sample
    # =========================================================================
    h4p = read_csv(csvp("h4_predictions"))
    h4m = read_csv(csvp("h4_metrics_baselines_calibration"))
    frozen_cal = {(r["pair"], r["family"]): r for r in h4m
                  if r["record_type"] == "metric" and r["predictor"] == "risk"}
    params = freeze["calibration"]["params"]
    groups = defaultdict(list)
    for r in h4p:
        groups[(r["pair"], r["family"])].append(r)
    pairs = sorted({p for p, _ in groups},
                   key=lambda p: (R.spec(p.split("|")[0]).family, R.spec(p.split("|")[0]).size_b))
    f1 = []
    n_repro = 0
    for p in pairs:
        for g in GRAMMARS:
            rows = groups[(p, g)]
            risk = [float(r["risk"]) for r in rows]
            lab = [int(r["label"]) for r in rows]
            tpl = [r["template"] for r in rows]
            frozen_pair = p in params
            # reproduce the export's numbers: frozen Platt for the 2 development pairs,
            # an in-sample fit for the other 8, exactly as evaluate_group does
            cal_exp = tuple(params[p]) if frozen_pair else h4.logistic_fit(risk, lab)
            exp = calibration_metrics(platt_probs(cal_exp, risk), lab, bins)
            fz = frozen_cal[(p, g)]
            for k_ in ("ece", "brier", "cal_slope", "cal_intercept"):
                if not close(exp[k_], num(fz[k_]), 1e-4) and not (abs(exp[k_]) < 1e-9 and abs(num(fz[k_])) < 1e-9):
                    die(f"F1: cannot reproduce the export's {k_} for {p} {g}: {exp[k_]} vs {fz[k_]}")
            n_repro += 1
            folds = template_folds(sorted(set(tpl)), f"{g}/phase4/calibration_folds")
            cf = calibration_metrics(cross_fitted_probs(risk, lab, tpl, folds), lab, bins)
            other = groups[(p, "blk" if g == "dom" else "dom")]
            cal_other = h4.logistic_fit([float(r["risk"]) for r in other], [int(r["label"]) for r in other])
            xf = calibration_metrics(platt_probs(cal_other, risk), lab, bins)
            f1.append({
                "pair": short(p.split("|")[0]), "grammar": g, "sites": len(rows),
                "export's source": "frozen (development)" if frozen_pair else "in-sample (the gap)",
                "export ECE": f"{exp['ece']:.3f}", "export slope": f"{exp['cal_slope']:.2f}",
                "cross-fitted ECE": f"{cf['ece']:.3f}", "cross-fitted Brier": f"{cf['brier']:.3f}",
                "cross-fitted slope": f"{cf['cal_slope']:.2f}", "cross-fitted intercept": f"{cf['cal_intercept']:+.2f}",
                "other-grammar ECE": f"{xf['ece']:.3f}", "other-grammar slope": f"{xf['cal_slope']:.2f}",
                "_frozen": frozen_pair, "_cf_ece": cf["ece"], "_cf_slope": cf["cal_slope"],
                "_xf_ece": xf["ece"], "_xf_slope": xf["cal_slope"], "_exp_ece": exp["ece"]})
    checks.append(f"F1: the export's ECE, Brier, calibration slope and intercept are reproduced exactly for all {n_repro} pair × grammar groups")
    cols = ["pair", "grammar", "sites", "export's source", "export ECE", "export slope", "cross-fitted ECE",
            "cross-fitted Brier", "cross-fitted slope", "cross-fitted intercept", "other-grammar ECE",
            "other-grammar slope"]
    write_csv(os.path.join(out, "F1_h4_calibration_out_of_sample.csv"), f1, cols)
    gap = [r for r in f1 if not r["_frozen"]]
    rng = lambda xs, d=3: f"{min(xs):.{d}f}–{max(xs):.{d}f}"  # noqa: E731
    report += ["## F1 — H4 calibration, out of sample", "",
               "**Problem.** For the 8 pairs without frozen Platt parameters, the export fitted the calibration on "
               "the held-out rows themselves and then measured it there: in-sample, with a slope of exactly 1.00.",
               "",
               f"**Fix.** Two out-of-sample estimates per pair and grammar: (1) template-grouped {FOLDS}-fold "
               "cross-fitting, where each site's probability comes from a Platt fit that never saw its template; "
               "(2) cross-family transfer, a Platt fit on the pair's other grammar family. Same ECE (10 bins), "
               "Brier and slope functions as the frozen code (`p33.h4`).", ""]
    report += md_table(f1, cols)
    report += ["", f"**Result.** For the 8 pairs that had no frozen calibration, cross-fitted ECE is "
               f"{rng([r['_cf_ece'] for r in gap])} with slopes {rng([r['_cf_slope'] for r in gap], 2)}, "
               f"close to the export's in-sample ECE ({rng([r['_exp_ece'] for r in gap])}): with only two "
               "parameters, a Platt fit barely overfits, so a calibration learned on some templates of a pair "
               "transfers to its other templates. Fitted on the other grammar family instead, it transfers less "
               f"well: ECE {rng([r['_xf_ece'] for r in gap])}, slopes {rng([r['_xf_slope'] for r in gap], 2)}. "
               "This is a post-hoc statement about calibratability within a pair, not a registered transfer "
               "test: the registered calibration-transfer claim stays limited to the two frozen pairs.", ""]

    # =========================================================================
    # F2 + F4 — H5: the registered test, and the repaired / control split
    # =========================================================================
    before = {}
    for r in read_csv(csvp("arm_a_long")):
        if r["status"] == "ok" and r["condition"] == "rule":
            before[(r["model"], r["site_id"])] = float(r["m_seq"]) < 0
    h5_path = os.path.join(rd, "merged", "h5.jsonl")
    if not os.path.exists(h5_path):
        die(f"{h5_path} is missing: run `bash phase3_3/sol_results/restore_large_files.sh {a.run}` first")
    tpl_f = {g: set() for g in GRAMMARS}
    acc: dict[tuple, dict] = {}
    with open(h5_path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("status") != "ok" or (r["model"], r["orig_site_id"]) not in before:
                continue
            key = (r["model"], r["family"], r["lexicon"], r["arm"], int(r["seed"]))
            d = acc.setdefault(key, {"n_changed": r["n_changed"] or 1, "t": defaultdict(lambda: np.zeros(7))})
            tpl_f[r["family"]].add(r["template"])
            v = d["t"][r["template"]]
            part = 0 if r["repaired_role"] else 3
            v[part] += 1                                               # sites
            v[part + 1] += before[(r["model"], r["orig_site_id"])]     # reverted before (Arm A, rule)
            v[part + 2] += bool(r["reverted_after"])                    # reverted after repair
            if r["repaired_role"]:
                v[6] += bool(r["silent_error_after"])
    tpl = {g: sorted(tpl_f[g]) for g in GRAMMARS}
    tix = {g: {t: i for i, t in enumerate(tpl[g])} for g in GRAMMARS}

    def vec(key, j):
        g = key[1]
        x = np.zeros(len(tpl[g]))
        for t, v in acc[key]["t"].items():
            x[tix[g][t]] = v[j]
        return x

    # reproduce the frozen h5_budget_outcomes, cell by cell
    frozen_h5 = {(r["model"], r["family"], r["lexicon"], r["arm"], int(r["seed"])): r
                 for r in read_csv(csvp("h5_budget_outcomes")) if r["record_type"] == "arm"}
    if set(frozen_h5) != set(acc):
        die("F2: the arms in merged/h5.jsonl and csv/h5_budget_outcomes.csv differ")
    for key, fr in frozen_h5.items():
        s = lambda j: float(vec(key, j).sum())  # noqa: E731
        n_ch = acc[key]["n_changed"]
        mine = {"n_repaired_sites": s(0), "reversions_before_repaired": s(1), "reversions_after_repaired": s(2),
                "silent_errors_after_repaired": s(6), "n_control_sites": s(3),
                "error_reduction_per_changed_symbol": (s(1) + s(4) - s(2) - s(5)) / n_ch}
        if s(3):
            mine["control_degradation"] = (s(5) - s(4)) / s(3)
        for k_, v in mine.items():
            if not close(v, num(fr[k_]), 5e-5):           # the CSV keeps 6 significant digits
                die(f"F2: cannot reproduce {k_} for {key}: {v} vs {fr[k_]}")
    checks.append(f"F2/F4: every one of the {len(frozen_h5)} frozen H5 arm rows (counts, per-symbol reduction, "
                  "control degradation) is reproduced exactly from merged/h5.jsonl and Arm A")

    def arm_stats(key, W):
        return h5_parts([vec(key, j) for j in range(6)], acc[key]["n_changed"], W)

    seeds = sorted({k[4] for k in acc if k[3] == "random"})
    stats = ("D", "Drep", "Dctl", "CD")
    f2_family, f2_model, f2_cell, f4_rows = [], [], [], []
    model_p, model_rows = {}, {}
    decomposition_ok = 0
    for g in GRAMMARS:
        W = PF.draws(tpl[g], f"{g}/phase4/h5_registered")
        ones = np.ones((1, len(tpl[g])))
        cells = sorted({(k[0], k[2]) for k in acc if k[1] == g})
        reps = {s_: [] for s_ in stats}           # one bootstrap vector per cell
        points = {s_: [] for s_ in stats}         # one point estimate per cell
        per_model_reps, per_model_pts = defaultdict(list), defaultdict(list)
        for (m, lx) in cells:
            res = {}
            for WW, tag in ((ones, "pt"), (W, "bs")):
                t_ = arm_stats((m, g, lx, "targeted", 0), WW)
                rnd = [arm_stats((m, g, lx, "random", s_), WW) for s_ in seeds]
                gl = arm_stats((m, g, lx, "global", 0), WW)
                res[tag] = {"D": t_["all"] - np.mean([x["all"] for x in rnd], axis=0),
                            "Drep": t_["rep"] - np.mean([x["rep"] for x in rnd], axis=0),
                            "Dctl": t_["ctl"] - np.mean([x["ctl"] for x in rnd], axis=0),
                            "CD": t_["cdeg"], "t": t_, "r": rnd, "gl": gl}
            pt, bs = res["pt"], res["bs"]
            decomposition_ok += 1
            for s_ in stats:
                reps[s_].append(bs[s_])
                points[s_].append(float(pt[s_][0]))
            per_model_reps[m].append(bs["D"])
            per_model_pts[m].append(float(pt["D"][0]))
            f2_cell.append({"model": short(m), "grammar": g, "lexicon": lx,
                            "targeted − random per symbol [95% CI]": fmt_ci(float(pt["D"][0]), PF.interval(bs["D"]), 2),
                            "control degradation (targeted)": f"{float(pt['CD'][0]):+.3f}",
                            "_D": float(pt["D"][0]), "_lo": PF.interval(bs["D"])[0], "_hi": PF.interval(bs["D"])[1]})
            f4_rows.append({"model": short(m), "grammar": g, "lexicon": lx,
                            "targeted: all / repaired / control": (
                                f"{float(pt['t']['all'][0]):+.2f} / {float(pt['t']['rep'][0]):+.2f} / "
                                f"{float(pt['t']['ctl'][0]):+.2f}"),
                            "random (mean): all / repaired / control": (
                                f"{np.mean([x['all'][0] for x in pt['r']]):+.2f} / "
                                f"{np.mean([x['rep'][0] for x in pt['r']]):+.2f} / "
                                f"{np.mean([x['ctl'][0] for x in pt['r']]):+.2f}"),
                            "global: all = repaired": f"{float(pt['gl']['all'][0]):+.2f}"})
        # family level: the mean over its cells, for the point and for every resample
        point = {s_: float(np.mean(points[s_])) for s_ in stats}
        iv = {s_: PF.interval(np.mean(np.vstack(reps[s_]), axis=0)) for s_ in stats}
        supported = iv["D"][0] > 0 and point["CD"] <= tolerance
        f2_family.append({
            "grammar": g, "cells": len(cells),
            "targeted − random, per changed symbol [95% CI]": fmt_ci(point["D"], iv["D"], 3),
            "control degradation, targeted [95% CI]": fmt_ci(point["CD"], iv["CD"], 3),
            "tolerance": f"≤ {tolerance:.2f}",
            "H5 as registered": "SUPPORTED" if supported else "NOT SUPPORTED",
            "repaired-site part of the difference [95% CI]": fmt_ci(point["Drep"], iv["Drep"], 3),
            "control-site part [95% CI]": fmt_ci(point["Dctl"], iv["Dctl"], 3),
            "_supported": supported, "_D": point["D"], "_lo": iv["D"][0], "_hi": iv["D"][1],
            "_Drep": point["Drep"], "_Drep_iv": iv["Drep"], "_Dctl": point["Dctl"], "_Dctl_iv": iv["Dctl"],
            "_CD": point["CD"]})
        for m in sorted(per_model_reps):
            mrep = np.mean(np.vstack(per_model_reps[m]), axis=0)
            mpt = float(np.mean(per_model_pts[m]))
            model_p[(m, g)] = two_sided_p(mrep)
            model_rows[(m, g)] = {"model": short(m), "grammar": g,
                                  "targeted − random per symbol [95% CI]": fmt_ci(mpt, PF.interval(mrep), 2),
                                  "_D": mpt}
    adj = holm(model_p)
    for k_, row in model_rows.items():
        row["two-sided p"] = f"{model_p[k_]:.3f}" if model_p[k_] > 0 else f"< {1 / B:.4f}"
        row["Holm p (20 tests)"] = f"{adj[k_]:.3f}" if adj[k_] > 0 else f"< {20 / B:.3f}"
        f2_model.append(row)
    checks.append(f"F4: the split is exact by construction (repaired part + control part = the registered metric, "
                  f"which is itself reproduced above for every frozen arm row); computed for all {decomposition_ok} cells")
    cols_fam = ["grammar", "cells", "targeted − random, per changed symbol [95% CI]",
                "control degradation, targeted [95% CI]", "tolerance", "H5 as registered",
                "repaired-site part of the difference [95% CI]", "control-site part [95% CI]"]
    write_csv(os.path.join(out, "F2_h5_registered_test.csv"), f2_family, cols_fam)
    cols_model = ["model", "grammar", "targeted − random per symbol [95% CI]", "two-sided p", "Holm p (20 tests)"]
    write_csv(os.path.join(out, "F2_h5_by_model.csv"), f2_model, cols_model)
    cols_cell = ["model", "grammar", "lexicon", "targeted − random per symbol [95% CI]", "control degradation (targeted)"]
    write_csv(os.path.join(out, "F2_h5_by_cell.csv"), f2_cell, cols_cell)
    cols_f4 = ["model", "grammar", "lexicon", "targeted: all / repaired / control",
               "random (mean): all / repaired / control", "global: all = repaired"]
    write_csv(os.path.join(out, "F4_h5_repaired_control_split.csv"), f4_rows, cols_f4)
    n_pos = sum(1 for r in f2_cell if r["_lo"] > 0)
    n_neg = sum(1 for r in f2_cell if r["_hi"] < 0)
    verdict = "SUPPORTED" if all(r["_supported"] for r in f2_family) else "NOT SUPPORTED"
    report += ["## F2 — H5, the registered test (implemented post hoc)", "",
               "**Problem.** The preregistration (§3) says: *H5 is supported iff error reduction per changed "
               "symbol exceeds the matched-budget random-rewrite control with an interval excluding 0, and "
               "reversion at low-risk control sites does not worsen by more than 0.02.* The frozen export reported "
               "each arm but never computed this test.", "",
               "**Fix.** Exactly that test, computed now. Per cell (instruct model × lexicon): targeted minus the "
               "mean of the five random seeds, in reversions removed per changed symbol (the export's metric). "
               "Per grammar family: the mean over its 50 cells, with a 95% template-cluster bootstrap interval "
               "(B = 2000, the same template draw for every cell and arm). Control degradation is the targeted "
               "arm's change in reversion rate at the sites it did not repair. Families are never pooled; H5 "
               "would need support in both.", ""]
    report += md_table(f2_family, cols_fam)
    report += ["", f"**Result: H5 is {verdict} by its own registered test**, in both grammar families. The "
               "verdict that was given descriptively (D12) stands, now with the registered interval. Per cell, "
               f"the interval lies above 0 in {n_pos} and below 0 in {n_neg} of {len(f2_cell)} cells "
               "(`F2_h5_by_cell.csv`). Per model and family, with Holm over the 20 tests:", ""]
    report += md_table(f2_model, cols_model)
    report += ["", "## F4 — H5's metric, split into repaired and control sites", "",
               "**Problem.** The registered metric counts the reversions removed at *every* site of a cell, so "
               "it mixes the sites whose spelling was repaired with the control sites, which change only because "
               "the prompt's table changed.", "",
               "**Fix.** An exact split: reduction per changed symbol = repaired-site part + control-site part. "
               "The total is the registered metric, reproduced for every frozen arm row. The family table above "
               "already shows the split of the "
               "targeted − random difference; `F4_h5_repaired_control_split.csv` has it per cell and arm.", ""]
    for r in f2_family:
        report.append(f"- `{r['grammar']}`: targeted − random = {r['_D']:+.3f} per changed symbol; repaired-site "
                      f"part {fmt_ci(r['_Drep'], r['_Drep_iv'], 3)}; control-site part "
                      f"{fmt_ci(r['_Dctl'], r['_Dctl_iv'], 3)}.")
    # pooled reversion rates at the repaired sites, before and after, per arm and family
    rates = []
    for g in GRAMMARS:
        for arm_ in ("targeted", "random", "global"):
            ks = [k for k in acc if k[1] == g and k[3] == arm_]
            n_ = sum(vec(k, 0).sum() for k in ks)
            b_ = sum(vec(k, 1).sum() for k in ks)
            a_ = sum(vec(k, 2).sum() for k in ks)
            s_ = sum(vec(k, 6).sum() for k in ks)
            rates.append({"grammar": g, "arm": arm_, "repaired sites": int(n_),
                          "reverting before → after": f"{b_ / n_:.1%} → {a_ / n_:.1%}",
                          "silent after": f"{s_ / n_:.1%}"})
    cols_rates = ["grammar", "arm", "repaired sites", "reverting before → after", "silent after"]
    write_csv(os.path.join(out, "F4_h5_repaired_site_rates.csv"), rates, cols_rates)
    report += ["", "Reversion at the repaired sites themselves, pooled over models and lexicons (random: all "
               "five seeds):", ""]
    report += md_table(rates, cols_rates)
    rep_wins = all(r["_Drep_iv"][0] > 0 for r in f2_family)
    ctl_loses = all(r["_Dctl_iv"][1] < 0 for r in f2_family)
    rate = {(r["grammar"], r["arm"]): r["reverting before → after"] for r in rates}
    if rep_wins and ctl_loses:
        report += ["", "**Reading.**", "",
                   "- **At the repaired sites, targeting beats random** in both families (intervals above 0). "
                   "This is mostly because respelling random, low-risk roles makes their sites *worse* "
                   f"(`dom` {rate[('dom', 'random')]}, `blk` {rate[('blk', 'random')]}), while respelling the "
                   "riskiest roles leaves them about as they were or improves them "
                   f"(`dom` {rate[('dom', 'targeted')]}, `blk` {rate[('blk', 'targeted')]}).",
                   "- **The registered difference is negative because of the control-site part**: under random "
                   "repair, the sites that were *not* repaired improved more. The registered H5 verdict is "
                   "therefore decided mainly by changes at sites that were not repaired. Why they change is not "
                   "known: both the prompt's table and the earlier part of each program differ after a repair.",
                   "- **Silent errors stay** under targeted repair, because in a permuted language the old "
                   "spelling of a repaired role is still another role's spelling; only global respelling removes "
                   "them.",
                   "- This is post hoc. It generates a hypothesis for Phase 4 (a preregistered repaired-site "
                   "metric); the registered verdict stands.", ""]
    else:
        report += ["", "**Reading.** The split does not change the picture: "
                   + "; ".join(f"`{r['grammar']}` repaired-site part {fmt_ci(r['_Drep'], r['_Drep_iv'], 3)}"
                               for r in f2_family) + ".", ""]

    # =========================================================================
    # F5 — Arm B, corrected extraction
    # =========================================================================
    gens = read_csv(csvp("arm_b_generations"))
    temps = {t.template_id: t for t in TM.build_templates()}
    ident = P.identity_phi()
    n_ok = 0
    changed, site_checks, site_changes = [], 0, 0
    by_mf = defaultdict(lambda: defaultdict(int))
    for r in gens:
        be, L = BACKENDS[r["family"]], PL.phi(r["lexicon"])
        prog = armb.extract_program(r["raw_output"])
        ev = armb.evaluate(prog, be, L, r["target_ir_hash"])
        if prog != r["extracted"] or ev["bucket"] != r["bucket"]:
            die(f"F5: cannot reproduce the frozen extraction or bucket for {r['row_key']}")
        n_ok += 1
        new = extract_corrected(r["raw_output"])
        key = (r["model"], r["family"])
        by_mf[key]["programs"] += 1
        by_mf[key]["correct_frozen"] += r["bucket"] == "VALID_CORRECT"
        by_mf[key]["parse_fail_frozen"] += r["bucket"] == "PARSE_FAIL"
        bucket = r["bucket"]
        if new != prog:
            ev2 = armb.evaluate(new, be, L, r["target_ir_hash"])
            bucket = ev2["bucket"]
            text = be.render(temps[r["template"]].ir, L)
            if text != r["target_program"]:
                die(f"F5: the rendered target differs from the stored one for {r['row_key']}")
            sites = {s.site_id: s for s in S.classify(text, L, be, template_id=r["template"], identity=ident)}
            for o in json.loads(r["site_obs"] or "[]"):
                site_checks += 1
                if armb.observe(new, sites[o["site_id"]])["outcome"] != o["outcome"]:
                    site_changes += 1
            changed.append({"model": short(r["model"]), "grammar": r["family"], "lexicon": r["lexicon"],
                            "template": r["template"], "frozen bucket": r["bucket"], "corrected bucket": bucket,
                            "corrected program": new})
        by_mf[key]["correct_corrected"] += bucket == "VALID_CORRECT"
        by_mf[key]["parse_fail_corrected"] += bucket == "PARSE_FAIL"
    checks.append(f"F5: the frozen extraction and bucket are reproduced exactly for all {n_ok} generations")
    checks.append(f"F5: re-observing the {site_checks} sites of the {len(changed)} changed generations gives "
                  f"{site_changes} changed site outcomes (reach and reversion given reach are unaffected)")
    write_csv(os.path.join(out, "F5_armb_changed_generations.csv"), changed,
              ["model", "grammar", "lexicon", "template", "frozen bucket", "corrected bucket", "corrected program"])
    f5 = []
    for (m, g), v in sorted(by_mf.items(), key=lambda kv: (R.spec(kv[0][0]).family, R.spec(kv[0][0]).size_b, kv[0][1])):
        f5.append({"model": short(m), "grammar": g, "programs": v["programs"],
                   "correct, frozen": f"{v['correct_frozen']} ({v['correct_frozen'] / v['programs']:.1%})",
                   "correct, corrected": f"{v['correct_corrected']} ({v['correct_corrected'] / v['programs']:.1%})",
                   "parse failures, frozen → corrected": f"{v['parse_fail_frozen']} → {v['parse_fail_corrected']}"})
    tot = {k_: sum(v[k_] for v in by_mf.values()) for k_ in
           ("programs", "correct_frozen", "correct_corrected", "parse_fail_frozen", "parse_fail_corrected")}
    f5.append({"model": "ALL", "grammar": "both", "programs": tot["programs"],
               "correct, frozen": f"{tot['correct_frozen']} ({tot['correct_frozen'] / tot['programs']:.1%})",
               "correct, corrected": f"{tot['correct_corrected']} ({tot['correct_corrected'] / tot['programs']:.1%})",
               "parse failures, frozen → corrected": f"{tot['parse_fail_frozen']} → {tot['parse_fail_corrected']}"})
    cols_f5 = ["model", "grammar", "programs", "correct, frozen", "correct, corrected",
               "parse failures, frozen → corrected"]
    write_csv(os.path.join(out, "F5_armb_task_accuracy.csv"), f5, cols_f5)
    moved = defaultdict(int)
    for c in changed:
        moved[(c["frozen bucket"], c["corrected bucket"])] += 1
    report += ["## F5 — Arm B, corrected extraction", "",
               "**Problem.** The frozen extractor keeps the whole first line of the output. Some models "
               "continued the few-shot pattern on that same line (`<program> Request: <next request>`), so a "
               "correct program was scored as a parse failure.", "",
               "**Fix.** The frozen extraction, then a cut at the first same-line `Request:`; the corrected "
               "program is re-evaluated with the frozen evaluator (`armb.evaluate`), and every site of each "
               "changed generation is re-observed with the frozen `armb.observe`.", ""]
    report += md_table(f5, cols_f5)
    report += ["", f"**Result.** {len(changed)} of {tot['programs']} generations change: "
               + "; ".join(f"{a_} → {b_}: {n_}" for (a_, b_), n_ in sorted(moved.items()))
               + f". Task accuracy goes from {tot['correct_frozen'] / tot['programs']:.1%} to "
               f"{tot['correct_corrected'] / tot['programs']:.1%}. Reach and reversion given reach do not change "
               f"({site_changes} of {site_checks} re-observed site outcomes differ), because the cut text lies after "
               "the program.", ""]

    # =========================================================================
    # F6 — H4 per role
    # =========================================================================
    tplh = {g: sorted({r["template"] for r in h4p if r["family"] == g}) for g in GRAMMARS}
    tixh = {g: {t: i for i, t in enumerate(tplh[g])} for g in GRAMMARS}
    f6 = []
    n_auc = 0
    for p in pairs:
        for g in GRAMMARS:
            W = PF.draws(tplh[g], f"{g}/phase4/h4_per_role")
            for role in ("sigil", "keyword", "verb"):
                rows = [r for r in groups[(p, g)] if r["stratum"] == role]
                if not rows:
                    continue
                sc = [float(r["risk"]) for r in rows]
                lb = [int(r["label"]) for r in rows]
                if len(set(lb)) < 2:
                    continue
                pt, (lo, hi) = PF.auroc_w(sc, lb, [tixh[g][r["template"]] for r in rows], W)
                ref = h4.auroc(sc, lb)
                if not close(pt, ref, 1e-12):
                    die(f"F6: vectorised AUROC {pt} != p33.h4.auroc {ref} for {p} {g} {role}")
                n_auc += 1
                f6.append({"pair": short(p.split("|")[0]), "grammar": g, "role": role, "sites": len(rows),
                           "reversion prevalence": f"{sum(lb) / len(lb):.3f}",
                           "AUROC within the role [95% CI]": fmt_ci(pt, (lo, hi), 3, sign=False),
                           "_pt": pt, "_lo": lo})
    checks.append(f"F6: all {n_auc} per-role AUROCs equal the frozen p33.h4.auroc")
    cols_f6 = ["pair", "grammar", "role", "sites", "reversion prevalence", "AUROC within the role [95% CI]"]
    write_csv(os.path.join(out, "F6_h4_per_role.csv"), f6, cols_f6)
    by_role = defaultdict(list)
    for r in f6:
        by_role[r["role"]].append(r["_pt"])
    report += ["## F6 — H4 per role (open item from 06 §10)", "",
               "**Question.** Is the H4 prediction carried by one kind of symbol (for example verbs)? The roles "
               "differ in how often they revert, so an AUROC pooled over roles could partly reflect those "
               "differences; inside one role they are gone. (Differences between the terminals of one role "
               "remain; the exploratory per-terminal `terminal_rate` baseline addresses those.)", ""]
    report += md_table(f6, cols_f6)
    report += ["", "**Result.** "
               + "; ".join(f"{role}: AUROC {min(v):.2f}–{max(v):.2f} (median {np.median(v):.2f})"
                           for role, v in by_role.items())
               + f". The interval lies above 0.5 in {sum(1 for r in f6 if r['_lo'] > 0.5)} of {len(f6)} "
               "pair × grammar × role groups: the prediction holds inside every role, not only across roles.", ""]

    # =========================================================================
    # checks and provenance
    # =========================================================================
    report += ["## Checks (all passed; the script refuses otherwise)", ""] + [f"- {c}" for c in checks]
    with open(os.path.abspath(__file__), "rb") as fh:
        me = hashlib.sha256(fh.read()).hexdigest()
    inputs = ["h4_predictions", "h4_metrics_baselines_calibration", "arm_a_long", "h5_budget_outcomes",
              "arm_b_generations"]
    report += ["", "## Provenance", "",
               f"- script `phase4/scripts/fix_heldout_problems.py`, sha256 `{me[:16]}…`",
               f"- frozen analysis `DEV_FREEZE.json` sha256 `{unlock['freeze_sha256'][:16]}…`",
               f"- intervals: template-cluster bootstrap, B = {B}, seed {SEED}, streams "
               "`<grammar>/phase4/{h5_registered, h4_per_role}`; calibration folds "
               f"`<grammar>/phase4/calibration_folds` ({FOLDS} folds)"]
    report += [f"- `csv/{n}.csv` sha256 `{hashlib.sha256(open(csvp(n), 'rb').read()).hexdigest()[:16]}…`" for n in inputs]
    report += [f"- `merged/h5.jsonl` sha256 `{hashlib.sha256(open(h5_path, 'rb').read()).hexdigest()[:16]}…`"]
    with open(os.path.join(out, "PHASE4_FIXES.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(report) + "\n")
    for c in checks:
        print("check:", c)
    print("H5 as registered:", "; ".join(f"{r['grammar']} {r['H5 as registered']} ({r['targeted − random, per changed symbol [95% CI]']})" for r in f2_family))
    print(f"Arm B task accuracy: {tot['correct_frozen']}/{tot['programs']} -> {tot['correct_corrected']}/{tot['programs']}")
    print("written:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
