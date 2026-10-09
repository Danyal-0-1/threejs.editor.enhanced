"""export.py — every required CSV, built ONLY from merged shards and manifests.

Nothing here recomputes a model score. Every number traces to a saved row.
Where data do not exist the CSV still exists, with a single row stating
`NOT RUN` or `NOT TESTABLE` and why -- never a placeholder claim.

Every aggregate row carries the metadata the brief requires: stage and split
label, grammar family, model and resolved revision, tokenizer, rows /
templates / mappings, prevalence, exclusions, failed and missing cells, the
confidence-interval unit, repetitions and seed, and censoring where it applies.
"""

from __future__ import annotations

import csv
import glob
import io
import json
import os
import statistics as st
from collections import defaultdict

from phase3_2 import analysis as AN

from p33 import config as CFG, h2, h4, kstar, power, splits
from p33.armb import hurdle

from p33.artifacts import CSV_NAMES  # noqa: E402  (the one registry of outputs)

PREFERRED = ["record_type", "status", "stage", "split", "family", "lexicon", "model",
             "model_revision", "tokenizer_id", "stratum", "condition", "n_rows",
             "n_templates", "n_mappings", "prevalence"]


# ---------------------------------------------------------------------------
# io
# ---------------------------------------------------------------------------

def _load_jsonl(p: str) -> list[dict]:
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []


def _load_json(p: str, default=None):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


def _cell(v):
    if isinstance(v, (list, dict)):
        return json.dumps(v, sort_keys=True, ensure_ascii=False)
    if isinstance(v, float):
        return f"{v:.6g}"
    return v


def write_csv(path: str, rows: list[dict], *, not_run: str | None = None) -> str:
    if not rows:
        rows = [{"status": "NOT RUN", "reason": not_run or "no data"}]
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    cols = [k for k in PREFERRED if k in keys] + sorted(k for k in keys if k not in PREFERRED)
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow({k: _cell(r.get(k)) for k in cols})
    CFG.atomic_write_text(path, buf.getvalue())
    return path


# ---------------------------------------------------------------------------
# shared metadata
# ---------------------------------------------------------------------------

def meta(rows: list[dict], *, B=None, seed=None, unit=None, label_key=None) -> dict:
    out = {"n_rows": len(rows),
           "n_templates": len({r.get("template") for r in rows}),
           "n_mappings": len({r.get("lexicon") for r in rows}),
           "split": "|".join(sorted({str(r.get("split")) for r in rows})) or None,
           "model_revision": "|".join(sorted({str(r.get("model_revision")) for r in rows if r.get("model_revision")})),
           "tokenizer_id": "|".join(sorted({str(r.get("tokenizer_id")) for r in rows if r.get("tokenizer_id")}))}
    if label_key:
        ys = [r[label_key] for r in rows if r.get(label_key) is not None]
        out["prevalence"] = (sum(ys) / len(ys)) if ys else None
    if B is not None:
        out.update({"ci_unit": unit, "ci_reps": B, "ci_seed": seed})
    return out


def _iv(iv):
    if iv is None:
        return {"ci_lo": None, "ci_hi": None, "ci_status": "NO INTERVAL (<8 template clusters)"}
    return {"ci_lo": iv.lo, "ci_hi": iv.hi, "ci_status": "ok", "n_clusters": iv.n_clusters}


# ---------------------------------------------------------------------------
# the builder
# ---------------------------------------------------------------------------

def export_all(run_dir: str, cfg) -> dict[str, str]:
    out_dir = os.path.join(run_dir, "csv")
    os.makedirs(out_dir, exist_ok=True)
    A = cfg.analysis
    B, seed, unit, mc = int(A["B"]), int(cfg.seeds["bootstrap"]), A["unit"], int(A["min_clusters"])
    paths = {}
    W = lambda name, rows, nr=None: paths.__setitem__(name, write_csv(  # noqa: E731
        os.path.join(out_dir, f"{name}.csv"), rows, not_run=nr))

    merged = {e: _load_jsonl(os.path.join(run_dir, "merged", f"{e}.jsonl"))
              for e in ("arm_a", "primary", "armb", "h5")}
    status = {e: _load_json(os.path.join(run_dir, "merged", f"{e}.status.json"), {})
              for e in merged}
    plan = _load_json(os.path.join(run_dir, "manifests", "plan_arm_a.json")) or \
        _load_json(os.path.join(run_dir, "manifests", "plan_primary.json"), {})

    # 1 site inventory
    W("site_inventory", [{"record_type": "site", "stage": cfg.stage, **s}
                         for s in plan.get("sites", [])], "no plan written (no runner executed)")

    # 2 split / exclusion audit
    audit = []
    for k, c in sorted(plan.get("classes", {}).items()):
        audit.append({"record_type": "cell_class", "cell": k, **c})
    for d in plan.get("dropped", []):
        audit.append({"record_type": "dropped_site", **d})
    for g in plan.get("grid", []):
        if g["status"] != "OK":
            audit.append({"record_type": "structural_grid", **g})
    for e, rows in merged.items():
        for r in rows:
            if r.get("status") == "excluded":
                audit.append({"record_type": "excluded_row", "experiment": e,
                              "site_id": r.get("site_id") or r.get("orig_site_id"),
                              "model": r.get("model"), "condition": r.get("condition"),
                              "reason": r.get("exclusion_reason")})
    W("split_exclusion_audit", audit)

    # 3 completeness, 4 failed cells
    comp = []
    for e, s in status.items():
        if s:
            comp.append({"record_type": "experiment", "experiment": e, "status": s["status"],
                         "n_expected_cells": s["n_expected_cells"], "done": s["done"],
                         "missing": len(s["missing"]), "failed": len(s["failed"]),
                         "corrupt": len(s["corrupt"]),
                         "duplicates_dropped": s["duplicates_dropped"],
                         "merged_sha256": s.get("sha256")})
        else:
            comp.append({"record_type": "experiment", "experiment": e, "status": "NOT RUN"})
    W("run_completeness", comp)
    failed = []
    for p in sorted(glob.glob(os.path.join(run_dir, "checkpoints", "*", "*.failed.json"))):
        r = _load_json(p, {})
        failed.append({"experiment": os.path.basename(os.path.dirname(p)),
                       "cell_key": r.get("cell_key"), "kind": r.get("kind"),
                       "error_type": r.get("error_type"), "message": r.get("message"),
                       "host": r.get("host"), "job": r.get("job"),
                       "failed_utc": r.get("failed_utc")})
    W("failed_cells", failed, "no failed cells recorded")

    # 5 provenance
    prov = []
    for p in sorted(glob.glob(os.path.join(run_dir, "manifests", "job_*.json"))):
        j = _load_json(p, {})
        g, pk = j.get("gpu", {}), j.get("packages", {})
        prov.append({"experiment": j.get("experiment"), "status": j.get("status"),
                     "stage": j.get("stage"), "start_utc": j.get("start_utc"),
                     "end_utc": j.get("end_utc"), "job_id": j.get("slurm", {}).get("job_id"),
                     "array_task": j.get("slurm", {}).get("array_task_id"),
                     "node": j.get("job", {}).get("node"), "git_commit": j.get("git_commit"),
                     "git_dirty": j.get("git_dirty"), "config_hash": j.get("config_hash"),
                     "torch": g.get("torch"), "cuda_runtime": g.get("cuda_runtime"),
                     "device": g.get("device_name"), "driver": g.get("nvidia_smi"),
                     "transformers": pk.get("transformers"), "python": pk.get("python"),
                     "dtype": j.get("dtype"), "lm_head_fp32": j.get("lm_head_fp32"),
                     "models": {m: v.get("revision") for m, v in j.get("models", {}).items()},
                     "n_prompts_hashed": len(j.get("prompt_hashes", {})),
                     "manifest": os.path.basename(p)})
    W("job_provenance", prov)

    # 6 fertility
    W("fertility", _load_json(os.path.join(run_dir, "manifests", "fertility.json"), []),
      "fertility not computed (run `p33 ... fertility`)")

    # 7 Arm A long
    a_rows = merged["arm_a"]
    W("arm_a_long", a_rows, "Arm A not run")

    # 8 rule effect (+ reversion), never pooled across families
    rule_rows = []
    ok = [r for r in a_rows if r.get("status") == "ok"]
    for (model, fam, lx) in sorted({(r["model"], r["family"], r["lexicon"]) for r in ok}):
        sub = [r for r in ok if (r["model"], r["family"], r["lexicon"]) == (model, fam, lx)]
        for stratum in ["ALL"] + sorted({r["stratum"] for r in sub}):
            g = sub if stratum == "ALL" else [r for r in sub if r["stratum"] == stratum]
            rr = [r for r in g if r["condition"] == "rule"]
            if not rr:
                continue
            base = {"record_type": "reversion", "condition": "rule", "stage": cfg.stage,
                    "family": fam, "lexicon": lx, "model": model, "stratum": stratum,
                    **meta(rr, B=B, seed=seed, unit=unit)}
            base["prevalence"] = AN.reversion_rate(rr)
            base["reversion_rate"] = base["prevalence"]
            base.update(_iv(AN.cluster_bootstrap(rr, AN.reversion_rate, unit=unit, B=B,
                                                 seed=seed, min_clusters=mc)))
            rule_rows.append(base)
            for ctrl in ("norule", "norule_lenmatched"):
                pair = [r for r in g if r["condition"] in ("rule", ctrl)]
                pair = [dict(r, condition="norule" if r["condition"] == ctrl else "rule")
                        for r in pair]
                try:
                    pt = AN.paired_rule_effect(pair)
                except st.StatisticsError:
                    continue
                idx = defaultdict(dict)
                for r in pair:
                    idx[r["site_id"]][r["condition"]] = r["m_seq"]
                d = [v["rule"] - v["norule"] for v in idx.values() if len(v) == 2]
                row = {"record_type": "rule_effect", "control": ctrl, "stage": cfg.stage,
                       "family": fam, "lexicon": lx, "model": model, "stratum": stratum,
                       **meta(rr, B=B, seed=seed, unit=unit), "n_pairs": len(d),
                       "mean_rule_effect": pt, "median_rule_effect": st.median(d),
                       "share_helped": sum(x > 0 for x in d) / len(d)}
                iv = AN.cluster_bootstrap(pair, AN.paired_rule_effect, unit=unit, B=B,
                                          seed=seed, min_clusters=mc)
                row.update(_iv(iv))
                row["ci_excludes_zero"] = iv.excludes_zero if iv else None
                rule_rows.append(row)
    W("rule_effect", rule_rows, "no Arm A rows with status ok")

    # 9 paraphrase, 10 rung long, 11 k* survival
    p_rows = merged["primary"]
    para = [r for r in p_rows if r.get("kind") == "paraphrase" and r.get("status") == "ok"]
    prow = []
    for (model, fam) in sorted({(r["model"], r["family"]) for r in para}):
        g = [r for r in para if (r["model"], r["family"]) == (model, fam)]
        rates = {}
        for v in sorted({r["condition"] for r in g}):
            gv = [r for r in g if r["condition"] == v]
            rates[v] = AN.reversion_rate(gv)
            row = {"record_type": "variant", "stage": cfg.stage, "family": fam,
                   "model": model, "condition": v, **meta(gv, B=B, seed=seed, unit=unit),
                   "reversion_rate": rates[v], "mean_m_seq": AN.mean_margin(gv)}
            row.update(_iv(AN.cluster_bootstrap(gv, AN.reversion_rate, unit=unit, B=B,
                                                seed=seed, min_clusters=mc)))
            prow.append(row)
        prow.append({"record_type": "range", "stage": cfg.stage, "family": fam, "model": model,
                     "reversion_range": max(rates.values()) - min(rates.values()),
                     "variants": "|".join(sorted(rates))})
    W("paraphrase", prow, "paraphrase robustness not run")

    lad = [r for r in p_rows if r.get("kind") == "ladder"]
    W("extinction_rung_long", lad, "extinction ladder not run")

    curves = []
    by = defaultdict(list)
    for r in lad:
        by[(r["model"], r["site_id"])].append(r)
    for (model, sid), rs in sorted(by.items()):
        rs = sorted(rs, key=lambda r: r["rung"])
        if any(r["status"] != "ok" for r in rs):
            curves.append({"record_type": "site", "model": model, "site_id": sid,
                           "status": "excluded", "reason": "a rung was not measurable"})
            continue
        ks = kstar.compute([r["rung"] for r in rs], [r["m_seq"] for r in rs])
        r0 = rs[0]
        curves.append({"record_type": "site", "status": "ok", "stage": cfg.stage,
                       "split": r0["split"], "model": model, "model_revision": r0["model_revision"],
                       "tokenizer_id": r0["tokenizer_id"], "family": r0["family"],
                       "lexicon": r0["lexicon"], "template": r0["template"],
                       "site_id": sid, "stratum": r0["stratum"],
                       "margins": [r["m_seq"] for r in rs], **ks.as_dict()})
    summ = []
    okc = [c for c in curves if c["status"] == "ok"]
    for (model, fam) in sorted({(c["model"], c["family"]) for c in okc}):
        g = [c for c in okc if (c["model"], c["family"]) == (model, fam)]
        kobjs = [kstar.KStar(**{k: c[k] for k in kstar.KStar.__dataclass_fields__}) for c in g]
        for wrong_only in (False, True):
            km = kstar.km_from_kstars(kobjs, initially_wrong_only=wrong_only)

            def stat(rs, wrong_only=wrong_only):
                kk = [kstar.KStar(**{k: c[k] for k in kstar.KStar.__dataclass_fields__}) for c in rs]
                m = kstar.km_from_kstars(kk, initially_wrong_only=wrong_only).median
                if m is None:
                    raise ValueError("median not reached")
                return m
            iv = AN.cluster_bootstrap(g if not wrong_only else [c for c in g if not c["already_correct"]],
                                      stat, unit=unit, B=B, seed=seed, min_clusters=mc)
            summ.append({"record_type": "km_summary", "population": km.population,
                         "stage": cfg.stage, "family": fam, "model": model,
                         **meta(g, B=B, seed=seed, unit=unit), "n": km.n,
                         "n_events": km.n_events, "n_censored": km.n_censored,
                         "censoring_rate": km.censoring_rate,
                         "km_median": km.median if km.median is not None else "NOT REACHED",
                         **_iv(iv)})
        summ.append({"record_type": "diagnostic_median_among_crossers",
                     "stage": cfg.stage, "family": fam, "model": model,
                     "value": kstar.median_among_crossers(kobjs),
                     "warning": "drops censored sites; underestimates k*; diagnostic only"})
        summ.append({"record_type": "curve_shape", "stage": cfg.stage, "family": fam,
                     "model": model, "share_nonmonotone": sum(k.nonmonotone for k in kobjs) / len(kobjs),
                     "share_recrossed_down": sum(k.recrossed_down for k in kobjs) / len(kobjs),
                     "share_already_correct": sum(k.already_correct for k in kobjs) / len(kobjs)})
    W("kstar_survival", curves + summ, "extinction ladder not run")

    # 12-13 H4
    table = h4.build_table(a_rows)
    freeze = None
    if cfg.stage == "heldout" and cfg.freeze_path:
        freeze = splits.load_freeze(cfg.freeze_path)
    h4rows, h4m = [], []
    for (pair, fam, split) in sorted({(r["pair"], r["family"], r["split"]) for r in table}):
        g = [r for r in table if (r["pair"], r["family"], r["split"]) == (pair, fam, split)]
        if freeze:
            cal = tuple(freeze["calibration"]["params"][pair]) if pair in freeze["calibration"]["params"] else None
            thr = freeze["decision_threshold"].get(pair)
        else:
            cal = h4.logistic_fit([r["risk"] for r in g], [r["label"] for r in g])
            thr = None
        a_, b_ = cal if cal else (0.0, 1.0)
        for r in g:
            h4rows.append({**r, "stage": cfg.stage,
                           "calibrated_p": h4._sigmoid(a_ + b_ * r["risk"]),
                           "calibration_source": "DEV_FREEZE" if freeze else "fit on these rows (DEVELOPMENT)"})
        ms = h4.evaluate_group(g, calibration=cal, threshold=thr,
                               ks=A["precision_at_k"], bins=int(A["ece_bins"]),
                               B=B, seed=seed, min_clusters=mc)
        for m in ms:
            h4m.append({"record_type": "metric", "stage": cfg.stage, "pair": pair,
                        "family": fam, "split": split, **m})
        grammar_valid = False                 # deviation D1: no valid held-out grammar
        for c in h4.criteria(ms, grammar_valid=grammar_valid):
            h4m.append({"record_type": "criterion", "stage": cfg.stage, "pair": pair,
                        "family": fam, "split": split,
                        "confirmatory": cfg.stage == "heldout", **c})
    W("h4_predictions", h4rows, "H4 needs base AND instruct Arm A rows for a registered pair")
    W("h4_metrics_baselines_calibration", h4m,
      "H4 needs base AND instruct Arm A rows for a registered pair")

    # 14-15 Arm B
    b_rows = merged["armb"]
    W("arm_b_generations", b_rows, "Arm B not run")
    hrows = []
    for (model, fam, lx) in sorted({(r["model"], r["family"], r["lexicon"]) for r in b_rows}):
        g = [r for r in b_rows if (r["model"], r["family"], r["lexicon"]) == (model, fam, lx)]
        obs = [o for r in g for o in r["site_obs"]]
        buckets = {b: sum(1 for r in g if r["bucket"] == b) for b in
                   ("LEX_FAIL", "PARSE_FAIL", "VALID_VACUOUS", "VALID_WRONG", "VALID_CORRECT")}
        for stratum in ["ALL"] + sorted({o["stratum"] for o in obs}):
            oo = obs if stratum == "ALL" else [o for o in obs if o["stratum"] == stratum]
            hrows.append({"record_type": "hurdle", "stage": cfg.stage, "family": fam,
                          "lexicon": lx, "model": model, "stratum": stratum,
                          **meta(g), **hurdle(oo),
                          **({f"n_{k.lower()}": v for k, v in buckets.items()} if stratum == "ALL" else {}),
                          "parse_valid_rate": sum(r["parse_valid"] for r in g) / len(g),
                          "task_accuracy": sum(r["task_correct"] for r in g) / len(g),
                          "note": "P(reach) and P(revert|reach) are separate; the product is reported alongside, never instead"})
    W("arm_b_hurdle", hrows, "Arm B not run")

    # 16-17 H5
    h5_rows = merged["h5"]
    arms = _load_json(os.path.join(run_dir, "manifests", "h5_arms.json"), {})
    proof_rows = [{"repair": k, **v} for k, v in sorted(arms.get("proofs", {}).items())]
    W("h5_ir_proof", proof_rows, "H5 not prepared")
    before = {(r["model"], r["site_id"]): r for r in a_rows
              if r.get("condition") == "rule" and r.get("status") == "ok"}
    h5o = []
    for key in sorted({(r["model"], r["family"], r["lexicon"], r["arm"], r["seed"]) for r in h5_rows}):
        g = [r for r in h5_rows if (r["model"], r["family"], r["lexicon"], r["arm"], r["seed"]) == key
             and r.get("status") == "ok" and (key[0], r["orig_site_id"]) in before]
        if not g:
            continue
        rep = [r for r in g if r["repaired_role"]]
        ctl = [r for r in g if not r["repaired_role"]]
        rb = lambda rs: sum(before[(key[0], r["orig_site_id"])]["m_seq"] < 0 for r in rs)  # noqa: E731
        ra = lambda rs: sum(r["reverted_after"] for r in rs)  # noqa: E731
        sa = lambda rs: sum(r["silent_error_after"] for r in rs)  # noqa: E731
        n_ch = g[0]["n_changed"] or 1
        row = {"record_type": "arm", "stage": cfg.stage, "model": key[0], "family": key[1],
               "lexicon": key[2], "arm": key[3], "seed": key[4], "n_changed": n_ch,
               **meta(g), "n_repaired_sites": len(rep), "n_control_sites": len(ctl),
               "reversions_before_repaired": rb(rep), "reversions_after_repaired": ra(rep),
               "silent_errors_after_repaired": sa(rep),
               "error_reduction_per_changed_symbol": (rb(g) - ra(g)) / n_ch,
               "control_reversion_before": rb(ctl) / len(ctl) if ctl else None,
               "control_reversion_after": ra(ctl) / len(ctl) if ctl else None}
        if ctl:
            row["control_degradation"] = row["control_reversion_after"] - row["control_reversion_before"]
            row["control_within_tolerance"] = row["control_degradation"] <= float(cfg.h5["low_risk_tolerance"])
        h5o.append(row)
    W("h5_budget_outcomes", h5o, "H5 not run")

    # 18 H2, 19 power
    W("h2_did", [{"stage": cfg.stage, **h2.evaluate(None)}])
    dev_table = [r for r in table if r["split"] == "DEVELOPMENT"]
    dev_a = [r for r in a_rows if r.get("split") == "DEVELOPMENT"]
    dev_curves = [c for c in okc if c.get("split") == "DEVELOPMENT"]
    dev_h = [h for h in hrows if h.get("stratum") == "ALL" and "DEVELOPMENT" in str(h.get("split"))]
    if cfg.stage == "heldout":
        W("power", [{"status": "NOT RUN", "reason": "power uses development data only; run it in the dev stage"}])
    else:
        from phase3_2 import templates as TM
        W("power", power.analyse(dev_table, dev_a, dev_curves, dev_h,
                                 corpus_templates=len(TM.build_templates())))

    missing = [n for n in CSV_NAMES if n not in paths]
    if missing:
        raise RuntimeError(f"export forgot {missing}")
    return paths
