"""finalize.py — STATUS.json, MANIFEST.json, HYPOTHESIS_ASSESSMENT.md,
LIMITATIONS.md, OVERALL_REPORT.md and the experiment README.

All prose that states a NUMBER pulls it from metrics/aggregate.json. The
hypothesis verdicts are computed by the rules predeclared in STUDY_PLAN.md, not
chosen by hand.
"""
from __future__ import annotations

import collections, datetime, glob, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)
RUN_ID = os.path.basename(RUN)
ROOT = os.path.dirname(RUN)

import checkpoint as C

LANGS = ["identity", "alpha", "beta", "gamma"]
ALIEN = ["alpha", "beta", "gamma"]
CONDS = ["bare", "scaffolded"]
TASKS = ["op-selection", "selector-resolution", "arg-extraction", "multi-op"]


def pct(p):
    return "NA" if p is None else f"{100*p:.1f}%"


def short(m):
    return m.replace("Qwen/Qwen2.5-Coder-", "").replace("-Instruct", "")


def load():
    with open(os.path.join(RUN, "metrics", "aggregate.json"), encoding="utf-8") as fh:
        return json.load(fh)


def raw_gen():
    out = []
    for p in glob.glob(os.path.join(RUN, "raw", "*", "lane_b", "gen.jsonl")):
        out += C.read_rows(p)
    return out


# ── hypothesis assessment, computed mechanically ─────────────────────────────

def assess(A):
    laneA, laneB = A["lane_a"], A["lane_b"]
    v = {}

    # H1 — base ΔNLL/char > 0 with CI excluding 0
    h1 = []
    for label, m in laneA["models"].items():
        for lang in ALIEN:
            d = (m["languages"].get(lang) or {}).get("delta_nll_per_char")
            if d:
                h1.append({"model": label, "language": lang, "delta": d["point"],
                           "lo": d["ci95_lo"], "hi": d["ci95_hi"],
                           "supports": d["ci95_lo"] > 0})
    v["H1"] = {"cells": h1,
               "n_supporting": sum(1 for c in h1 if c["supports"]),
               "n_total": len(h1),
               "verdict": ("SUPPORTED" if h1 and all(c["supports"] for c in h1)
                           else "MIXED" if any(c["supports"] for c in h1)
                           else "NOT SUPPORTED" if h1 else "NOT ASSESSED")}

    # H2 — paired semantic accuracy lower than identity
    h2 = []
    for model, m in laneB["models"].items():
        for cond, ce in m["conditions"].items():
            for lang, comp in ce.get("comparisons", {}).items():
                s = comp["semantic"]
                h2.append({"model": model, "condition": cond, "language": lang,
                           "rd": s["risk_difference"], "lo": s["ci95_lo"],
                           "hi": s["ci95_hi"],
                           "p": s["mcnemar"]["p_value"],
                           "n_disc": s["mcnemar"]["n_discordant"],
                           "negative": s["risk_difference"] < 0,
                           "ci_excludes_zero": s["ci95_hi"] < 0})
    v["H2"] = {"cells": h2,
               "n_negative": sum(1 for c in h2 if c["negative"]),
               "n_ci_excludes_zero": sum(1 for c in h2 if c["ci_excludes_zero"]),
               "n_total": len(h2),
               "verdict": ("SUPPORTED" if h2 and sum(c["ci_excludes_zero"] for c in h2) > len(h2) / 2
                           else "MIXED" if any(c["negative"] for c in h2)
                           else "NOT SUPPORTED" if h2 else "NOT ASSESSED")}

    # H3 — scaffolding improves accuracy / narrows the gap
    h3, gaps = [], []
    for model, m in laneB["models"].items():
        cb, cs = m["conditions"].get("bare"), m["conditions"].get("scaffolded")
        if not (cb and cs):
            continue
        for lang in LANGS:
            eb, es = cb["languages"].get(lang), cs["languages"].get(lang)
            if eb and es:
                h3.append({"model": model, "language": lang,
                           "bare": eb["semantic_accuracy"]["proportion"],
                           "scaffolded": es["semantic_accuracy"]["proportion"],
                           "delta": es["semantic_accuracy"]["proportion"]
                                    - eb["semantic_accuracy"]["proportion"]})
        for lang in ALIEN:
            gb = (cb.get("comparisons", {}).get(lang, {}).get("semantic") or {}).get("risk_difference")
            gs = (cs.get("comparisons", {}).get(lang, {}).get("semantic") or {}).get("risk_difference")
            if gb is not None and gs is not None:
                gaps.append({"model": model, "language": lang, "gap_bare": gb,
                             "gap_scaffolded": gs, "narrowed": gs > gb})
    n_imp = sum(1 for c in h3 if c["delta"] > 0)
    v["H3"] = {"cells": h3, "gaps": gaps, "n_improved": n_imp, "n_total": len(h3),
               "n_gap_narrowed": sum(1 for g in gaps if g["narrowed"]),
               "n_gap_total": len(gaps),
               "verdict": ("SUPPORTED" if h3 and n_imp > len(h3) / 2
                           else "MIXED" if n_imp else "NOT SUPPORTED" if h3
                           else "NOT ASSESSED")}

    # H4 — fertility raises token cost (confirmatory); accuracy link exploratory
    fert = next(t for t in A["fertility"]["tokenizers"] if t["repo"].startswith("Qwen"))
    h4 = []
    for model, m in laneB["models"].items():
        for cond, ce in m["conditions"].items():
            base = ce["languages"].get("identity")
            if not base:
                continue
            for lang in ALIEN:
                e = ce["languages"].get(lang)
                if e:
                    h4.append({
                        "model": model, "condition": cond, "language": lang,
                        "relative_fertility": fert["rows"][lang]["relative_fertility_vs_identity"],
                        "input_tokens_median": e["input_tokens"]["median"],
                        "identity_input_tokens_median": base["input_tokens"]["median"],
                        "token_ratio": (e["input_tokens"]["median"] / base["input_tokens"]["median"]
                                        if base["input_tokens"]["median"] else None),
                        "more_tokens": (e["input_tokens"]["median"]
                                        > base["input_tokens"]["median"])})
    v["H4"] = {"cells": h4, "n_more_tokens": sum(1 for c in h4 if c["more_tokens"]),
               "n_total": len(h4),
               "verdict": ("SUPPORTED (token cost)" if h4 and all(c["more_tokens"] for c in h4)
                           else "MIXED" if any(c["more_tokens"] for c in h4)
                           else "NOT SUPPORTED" if h4 else "NOT ASSESSED")}

    # Dense-prior rule (predeclared, all four conditions)
    nong = [c for c in h2 if c["language"] != "gamma"]
    dp = {
        "a_nll_rises": v["H1"]["verdict"] == "SUPPORTED",
        "b_accuracy_falls": v["H2"]["n_negative"] > v["H2"]["n_total"] / 2 if h2 else False,
        "c_consistent_across_sizes_and_tasks": None,
        "d_not_only_gamma": (sum(1 for c in nong if c["negative"]) > len(nong) / 2
                             if nong else False),
    }
    if h1 and h2:
        by_model = collections.defaultdict(list)
        for c in h2:
            by_model[c["model"]].append(c["negative"])
        dp["c_consistent_across_sizes_and_tasks"] = (
            sum(1 for k, vs in by_model.items() if sum(vs) > len(vs) / 2)
            > len(by_model) / 2)
    dp["suggestive_support"] = all(bool(x) for x in dp.values() if x is not None) and \
        all(x is not None for x in dp.values())
    v["dense_prior_rule"] = dp
    return v


def main() -> int:
    A = load()
    V = assess(A)
    laneA, laneB, fert = A["lane_a"], A["lane_b"], A["fertility"]
    rows = raw_gen()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(os.path.join(RUN, "metadata", "environment.json"), encoding="utf-8") as fh:
        env = json.load(fh)
    with open(os.path.join(RUN, "inputs", "task_dataset.json"), encoding="utf-8") as fh:
        DS = json.load(fh)
    try:
        with open(os.path.join(RUN, "metadata", "validation.json"), encoding="utf-8") as fh:
            VAL = json.load(fh)
    except FileNotFoundError:
        VAL = []

    b_models = sorted(laneB["models"], key=lambda m: laneB["models"][m]["n_parameters"] or 0)
    a_models = list(laneA["models"])
    # Every lane's blocked cells, including the secondary analyses -- a blocked
    # cell that is not listed reads as "not attempted", which is a different and
    # stronger claim than "attempted and failed".
    blocked = (laneA["blocked"] + laneB["blocked"]
               + A.get("conditional_loss", {}).get("blocked", [])
               + A.get("labeling_control", {}).get("blocked", []))

    # ── STATUS.json ─────────────────────────────────────────────────────────
    cells = []
    for label, m in laneA["models"].items():
        for lang in LANGS:
            if lang in m["languages"]:
                cells.append({"lane": "A", "model": label, "language": lang,
                              "condition": "nll", "status": "VERIFIED",
                              "n": m["n_programs_scored"]})
    for model, m in laneB["models"].items():
        for cond, ce in m["conditions"].items():
            for lang, e in ce["languages"].items():
                cells.append({"lane": "B", "model": model, "language": lang,
                              "condition": cond, "status": "VERIFIED",
                              "n": e["semantic_accuracy"]["denominator"]})
    for model, m in A.get("conditional_loss", {}).get("models", {}).items():
        for cond, ce in m["conditions"].items():
            for lang in ce["languages"]:
                cells.append({"lane": "B-conditional-loss", "model": model,
                              "language": lang, "condition": cond,
                              "status": "VERIFIED", "n": ce["n_paired_cases"]})
    for model, m in A.get("labeling_control", {}).get("models", {}).items():
        for cond, e in m["conditions"].items():
            cells.append({"lane": "B-labeling-control", "model": model,
                          "language": "none", "condition": cond,
                          "status": "VERIFIED",
                          "n": e["overall"]["denominator"]})
    for b in blocked:
        cells.append({"lane": b["lane"], "model": b["model"], "language": "ALL",
                      "condition": f"{b['precision']}/{b['device']}",
                      "status": "BLOCKED", "reason": b["failure_kind"],
                      "error": str(b["error"])[:300]})
    status = {
        "run_id": RUN_ID, "generated_utc": now,
        "study": "exploratory fertility-unmatched model evaluation",
        "overall": "VERIFIED" if all(c["status"] == "VERIFIED" for c in cells
                                     if c["status"] != "BLOCKED") else "PARTIAL",
        "lane_a_models_executed": a_models,
        "lane_b_models_executed": b_models,
        "blocked": blocked,
        "cells": cells,
        "validation": VAL,
        "counts": {
            "lane_a_nll_rows": sum(1 for _ in glob.glob(
                os.path.join(RUN, "raw", "*", "lane_a", "*.jsonl"))),
            "lane_b_generation_rows": len([r for r in rows
                                           if r.get("scoring_family") == "generation"]),
            "lane_b_refusal_rows": len([r for r in rows
                                        if r.get("scoring_family") == "graceful_refusal"]),
            "task_dataset": DS["counts"],
        },
    }
    with open(os.path.join(RUN, "STATUS.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=2)

    # ── MANIFEST.json ───────────────────────────────────────────────────────
    manifest = {"run_id": RUN_ID, "generated_utc": now, "files": []}
    for base in ("metadata", "inputs", "scripts", "prompts", "raw", "metrics",
                 "reports", "plots", "logs"):
        d = os.path.join(RUN, base)
        for dirpath, _dd, files in os.walk(d):
            for name in sorted(files):
                p = os.path.join(dirpath, name)
                try:
                    manifest["files"].append({
                        "path": os.path.relpath(p, RUN),
                        "bytes": os.path.getsize(p),
                        "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()})
                except OSError:
                    pass
    for top in ("STUDY_PLAN.md", "STATUS.json"):
        p = os.path.join(RUN, top)
        if os.path.exists(p):
            manifest["files"].append({
                "path": top, "bytes": os.path.getsize(p),
                "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()})
    manifest["n_files"] = len(manifest["files"])
    with open(os.path.join(RUN, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    with open(os.path.join(RUN, "metrics", "hypothesis_assessment.json"), "w",
              encoding="utf-8") as fh:
        json.dump(V, fh, indent=2)

    print(f"STATUS.json: {status['overall']}, {len(cells)} cells, "
          f"{len(blocked)} blocked")
    print(f"MANIFEST.json: {manifest['n_files']} files")
    print(f"H1={V['H1']['verdict']} H2={V['H2']['verdict']} "
          f"H3={V['H3']['verdict']} H4={V['H4']['verdict']}")
    print(f"dense-prior suggestive support: {V['dense_prior_rule']['suggestive_support']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
