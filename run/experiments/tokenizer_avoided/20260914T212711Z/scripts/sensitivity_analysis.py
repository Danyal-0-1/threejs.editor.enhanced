"""sensitivity_analysis.py — the D2 truncation sensitivity result.

Compares the primary matrix (max_new_tokens = 512) against the separately
labelled `@maxnew1536` condition, on the same model, the same cases and ALL
FOUR languages. Never pools the two.
"""
from __future__ import annotations

import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)

import checkpoint as C

LANGS = ["identity", "alpha", "beta", "gamma"]


def main() -> int:
    out = {"condition": "maxnew1536", "primary_max_new_tokens": 512,
           "sensitivity_max_new_tokens": 1536, "cells": [], "models": []}
    for path in sorted(glob.glob(os.path.join(RUN, "raw", "*", "lane_b",
                                              "gen_maxnew1536.jsonl"))):
        S = [r for r in C.read_rows(path) if r.get("scoring_family") == "generation"]
        if not S:
            continue
        model = S[0]["model"]
        out["models"].append(model)
        P = [r for r in C.read_rows(path.replace("gen_maxnew1536", "gen"))
             if r.get("scoring_family") == "generation"]
        pk = {(r["case_id"], r["language"], r["condition"]): r for r in P}
        rescued = still = n_trunc = 0
        for cond in ("bare", "scaffolded"):
            for lang in LANGS:
                rs = [r for r in S if r["condition"] == f"{cond}@maxnew1536"
                      and r["language"] == lang]
                if not rs:
                    continue
                base = [pk[(r["case_id"], lang, cond)] for r in rs
                        if (r["case_id"], lang, cond) in pk]
                out["cells"].append({
                    "model": model, "condition": cond, "language": lang,
                    "n": len(rs),
                    "truncated_512": sum(b.get("truncated", 0) for b in base),
                    "truncated_1536": sum(r.get("truncated", 0) for r in rs),
                    "correct_512": sum(b.get("semantic_correct", 0) for b in base),
                    "correct_1536": sum(r.get("semantic_correct", 0) for r in rs),
                    "parse_valid_512": sum(b.get("parse_valid", 0) for b in base),
                    "parse_valid_1536": sum(r.get("parse_valid", 0) for r in rs)})
        for r in S:
            k = (r["case_id"], r["language"],
                 r["condition"].replace("@maxnew1536", ""))
            b = pk.get(k)
            if b and b.get("truncated"):
                n_trunc += 1
                if r.get("semantic_correct"):
                    rescued += 1
                else:
                    still += 1
        out.setdefault("verdict", {})[model] = {
            "cases_truncated_at_512": n_trunc,
            "became_correct_at_1536": rescued,
            "still_failed_at_1536": still,
            "limit_was_binding": rescued > 0,
            "conclusion": (
                "The 512-token limit WAS binding; the primary matrix must be "
                "re-run at a larger common limit for every language arm."
                if rescued > 0 else
                "The 512-token limit was NOT the binding constraint: no case that "
                "truncated at 512 became correct at 1536. The primary matrix "
                "stands, and truncation is reported as a failure mode in its own "
                "right.")}

    dest = os.path.join(RUN, "metrics", "sensitivity_maxnew.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    for m, v in out.get("verdict", {}).items():
        print(f"{m}: truncated@512={v['cases_truncated_at_512']} "
              f"rescued@1536={v['became_correct_at_1536']} -> "
              f"binding={v['limit_was_binding']}")
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
