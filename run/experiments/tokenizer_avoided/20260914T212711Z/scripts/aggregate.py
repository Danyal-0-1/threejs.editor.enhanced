"""aggregate.py — raw JSONL rows -> every reported metric.

EVERY aggregate here is computed from the raw rows on disk. Nothing is copied
from a log, and no missing cell is replaced by zero: a cell with no raw evidence
is emitted as null / NA and is labelled with WHY (BLOCKED, OOM, ...).
"""
from __future__ import annotations

import collections, csv, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)

import stats as ST
import checkpoint as C

LANGUAGES = ["identity", "alpha", "beta", "gamma"]
ALIEN = ["alpha", "beta", "gamma"]
CONDITIONS = ["bare", "scaffolded"]
TASKS = ["op-selection", "selector-resolution", "arg-extraction", "multi-op"]
TASK_COL = {"op-selection": "op_correct", "selector-resolution": "selector_correct",
            "arg-extraction": "args_correct", "multi-op": "multi_op_correct"}
RAW = os.path.join(RUN, "raw")


def find(pattern: str) -> list[str]:
    out = []
    for dirpath, _dirs, files in os.walk(RAW):
        if "/smoke" in dirpath or dirpath.endswith("smoke"):
            continue
        for f in files:
            if f == pattern:
                out.append(os.path.join(dirpath, f))
    return sorted(out)


# ── LANE A ───────────────────────────────────────────────────────────────────

def lane_a() -> dict:
    out = {"models": {}, "blocked": []}
    for meta_path in find("nll.meta.jsonl") + find("nll_cpu.meta.jsonl"):
        for m in C.read_rows(meta_path):
            if m.get("status") == "BLOCKED":
                out["blocked"].append({
                    "model": m["model"], "lane": "A", "device": m.get("device"),
                    "precision": m.get("precision"),
                    "failure_kind": m.get("failure_kind"),
                    "error": m.get("error"),
                    "attempted_command":
                        f"lane_a.py --model {m['model']} --precision "
                        f"{m.get('precision')} --device {m.get('device')}"})

    for path in find("nll.jsonl") + find("nll_cpu.jsonl"):
        rows = [r for r in C.read_rows(path) if r.get("outcome") == "VERIFIED"]
        if not rows:
            continue
        model = rows[0]["model"]
        device = rows[0].get("device", "?")
        label = model if device == "cuda" else f"{model} [{device}]"
        meta_rows = C.read_rows(path.replace(".jsonl", ".meta.jsonl"))
        meta = meta_rows[-1] if meta_rows else {}

        by = collections.defaultdict(dict)
        for r in rows:
            by[r["language"]][r["program_index"]] = r
        common = set.intersection(*(set(v) for v in by.values())) if by else set()
        idx = sorted(common)

        entry = {"model": model, "device": device, "precision": rows[0].get("precision"),
                 "revision": rows[0].get("revision"),
                 "n_parameters": meta.get("n_parameters"),
                 "model_load_seconds": meta.get("model_load_seconds"),
                 "warmup_seconds": meta.get("warmup_seconds"),
                 "peak_vram_allocated_bytes": meta.get("peak_vram_allocated_bytes"),
                 "peak_rss_bytes": meta.get("peak_rss_bytes"),
                 "n_programs_scored": len(idx), "languages": {}}

        def series(lang, num, den):
            return [(by[lang][i][num], by[lang][i][den]) for i in idx]

        for lang in LANGUAGES:
            if lang not in by:
                continue
            nll = sum(by[lang][i]["total_nll_nats"] for i in idx)
            tok = sum(by[lang][i]["scored_tokens"] for i in idx)
            ch = sum(by[lang][i]["chars"] for i in idx)
            byt = sum(by[lang][i]["utf8_bytes"] for i in idx)
            tns = sum(by[lang][i]["tokens_no_special"] for i in idx)
            secs = [by[lang][i]["nll_seconds"] for i in idx]
            e = {"total_nll_nats": nll, "nll_per_token": nll / tok,
                 "nll_per_char": nll / ch, "nll_per_utf8_byte": nll / byt,
                 "token_perplexity": math.exp(nll / tok),
                 "model_tokens_per_program": tns / len(idx),
                 "chars_per_program": ch / len(idx),
                 "utf8_bytes_per_program": byt / len(idx),
                 "fertility_tok_per_char": tns / ch,
                 "nll_scoring_seconds_total": sum(secs),
                 "nll_scoring_seconds_median": ST.median_iqr_p95(secs)["median"]}
            if lang != "identity":
                e["delta_nll_per_char"] = ST.paired_bootstrap_ratio(
                    series(lang, "total_nll_nats", "chars"),
                    series("identity", "total_nll_nats", "chars"))
                e["delta_nll_per_token"] = ST.paired_bootstrap_ratio(
                    series(lang, "total_nll_nats", "scored_tokens"),
                    series("identity", "total_nll_nats", "scored_tokens"))
            entry["languages"][lang] = e
        out["models"][label] = entry
    return out


# ── LANE B ───────────────────────────────────────────────────────────────────

def lane_b() -> dict:
    out = {"models": {}, "blocked": [], "paired_items": []}
    for meta_path in find("gen.meta.jsonl"):
        for m in C.read_rows(meta_path):
            if m.get("status") == "BLOCKED":
                out["blocked"].append({
                    "model": m["model"], "lane": "B", "device": m.get("device"),
                    "precision": m.get("precision"),
                    "failure_kind": m.get("failure_kind"), "error": m.get("error"),
                    "attempted_command":
                        f"lane_b.py --model {m['model']} --precision "
                        f"{m.get('precision')} --device {m.get('device')} --reps 3"})

    for path in find("gen.jsonl"):
        rows = C.read_rows(path)
        if not rows:
            continue
        model = rows[0]["model"]
        meta_rows = C.read_rows(path.replace(".jsonl", ".meta.jsonl"))
        meta = meta_rows[-1] if meta_rows else {}
        entry = {"model": model, "revision": rows[0].get("revision"),
                 "precision": rows[0].get("precision"), "device": rows[0].get("device"),
                 "n_parameters": meta.get("n_parameters"),
                 "model_load_seconds": meta.get("model_load_seconds"),
                 "warmup_seconds": meta.get("warmup_seconds"),
                 "peak_vram_allocated_bytes": meta.get("peak_vram_allocated_bytes"),
                 "peak_vram_reserved_bytes": meta.get("peak_vram_reserved_bytes"),
                 "peak_rss_bytes": meta.get("peak_rss_bytes"),
                 "n_rows": len(rows), "conditions": {}}

        gen = [r for r in rows if r.get("scoring_family") == "generation"]
        refusal = [r for r in rows if r.get("scoring_family") == "graceful_refusal"]
        errs = [r for r in rows if r.get("outcome") in ("OOM", "HARNESS_ERROR")]
        entry["n_generation_rows"] = len(gen)
        entry["n_refusal_rows"] = len(refusal)
        entry["n_error_rows"] = len(errs)

        for cond in CONDITIONS:
            cg = [r for r in gen if r["condition"] == cond]
            if not cg:
                continue
            ce = {"languages": {}, "comparisons": {}}
            by_lang = collections.defaultdict(dict)
            for r in cg:
                by_lang[r["language"]][r["case_id"]] = r
            common = (set.intersection(*(set(v) for v in by_lang.values()))
                      if by_lang else set())
            cases = sorted(common)
            ce["n_paired_cases"] = len(cases)

            for lang in LANGUAGES:
                if lang not in by_lang:
                    continue
                rs = [by_lang[lang][c] for c in cases]
                n = len(rs)
                def prop(col):
                    return ST.proportion(sum(int(r.get(col) or 0) for r in rs), n)
                e = {
                    "semantic_accuracy": prop("semantic_correct"),
                    "ir_exact_match": prop("ir_exact_match"),
                    "parse_validity": prop("parse_valid"),
                    "lex_validity": prop("lex_valid"),
                    "language_compliance": prop("requested_language_compliance"),
                    "vacuous_rate": prop("vacuous"),
                    "truncation_rate": prop("truncated"),
                    "per_task": {t: prop(TASK_COL[t]) for t in TASKS},
                    "outcomes": dict(collections.Counter(r["outcome"] for r in rs)),
                    "hallucinations": dict(collections.Counter(
                        h for r in rs for h in (r.get("hallucinations") or []))),
                    "nlvp": ST.median_iqr_p95([r.get("nlvp") for r in rs]),
                    "nlvp_invalid_only": ST.median_iqr_p95(
                        [r.get("nlvp") for r in rs
                         if r["outcome"] in ("LEX_FAIL", "PARSE_FAIL")]),
                    "input_tokens": ST.median_iqr_p95([r.get("input_tokens") for r in rs]),
                    "output_tokens": ST.median_iqr_p95([r.get("output_tokens") for r in rs]),
                    "e2e_seconds": ST.median_iqr_p95([r.get("e2e_seconds_median") for r in rs]),
                    "prefill_seconds": ST.median_iqr_p95([r.get("prefill_seconds_median") for r in rs]),
                    "decode_seconds": ST.median_iqr_p95([r.get("decode_seconds_median") for r in rs]),
                    "output_tokens_per_second": ST.median_iqr_p95(
                        [r.get("output_tokens_per_second") for r in rs]),
                    "deterministic_rate": prop("deterministic"),
                }
                ce["languages"][lang] = e

            # paired comparisons vs identity
            if "identity" in by_lang:
                pvals = {}
                for lang in ALIEN:
                    if lang not in by_lang:
                        continue
                    a = [int(by_lang[lang][c].get("semantic_correct") or 0) for c in cases]
                    b = [int(by_lang["identity"][c].get("semantic_correct") or 0) for c in cases]
                    comp = {"semantic": {**ST.paired_risk_difference(a, b),
                                         **{"mcnemar": ST.mcnemar_exact(a, b)}}}
                    for t in TASKS:
                        col = TASK_COL[t]
                        ta = [int(by_lang[lang][c].get(col) or 0) for c in cases]
                        tb = [int(by_lang["identity"][c].get(col) or 0) for c in cases]
                        mc = ST.mcnemar_exact(ta, tb)
                        comp[t] = {**ST.paired_risk_difference(ta, tb), "mcnemar": mc}
                        pvals[f"{lang}:{t}"] = mc["p_value"]
                    pvals[f"{lang}:semantic"] = comp["semantic"]["mcnemar"]["p_value"]
                    ce["comparisons"][lang] = comp
                ce["holm_within_model_condition_family"] = ST.holm(pvals)

                for c in cases:
                    rec = {"model": model, "condition": cond, "case_id": c}
                    for lang in LANGUAGES:
                        if lang in by_lang:
                            r = by_lang[lang][c]
                            rec[lang] = {k: r.get(k) for k in (
                                "semantic_correct", "parse_valid", "op_correct",
                                "selector_correct", "args_correct", "multi_op_correct",
                                "outcome", "output_tokens", "input_tokens",
                                "e2e_seconds_median", "requested_language_compliance")}
                    out["paired_items"].append(rec)
            entry["conditions"][cond] = ce

        # refusal family, kept separate
        if refusal:
            entry["graceful_refusal"] = {}
            for cond in CONDITIONS:
                for lang in LANGUAGES:
                    rs = [r for r in refusal
                          if r["condition"] == cond and r["language"] == lang]
                    if rs:
                        entry["graceful_refusal"][f"{lang}/{cond}"] = ST.proportion(
                            sum(int(r.get("refusal_correct") or 0) for r in rs), len(rs))
        out["models"][model] = entry
    return out


def write_csv(path: str, rows: list[dict], fields: list[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    A, B = lane_a(), lane_b()
    with open(os.path.join(RUN, "metrics", "fertility.json"), encoding="utf-8") as fh:
        fert = json.load(fh)

    payload = {"lane_a": A, "lane_b": B, "fertility": fert,
               "languages": LANGUAGES, "conditions": CONDITIONS, "tasks": TASKS}
    with open(os.path.join(RUN, "metrics", "aggregate.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    with open(os.path.join(RUN, "metrics", "paired-item-results.jsonl"), "w",
              encoding="utf-8") as fh:
        for rec in B["paired_items"]:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # flat aggregate.csv — one row per (lane, model, language, condition)
    flat = []
    for label, m in A["models"].items():
        for lang, e in m["languages"].items():
            d = e.get("delta_nll_per_char") or {}
            flat.append({
                "lane": "A", "model": label, "n_parameters": m["n_parameters"],
                "device": m["device"], "precision": m["precision"],
                "language": lang, "condition": "nll", "n": m["n_programs_scored"],
                "nll_per_char": e["nll_per_char"], "nll_per_token": e["nll_per_token"],
                "nll_per_utf8_byte": e["nll_per_utf8_byte"],
                "token_perplexity": e["token_perplexity"],
                "model_tokens_per_program": e["model_tokens_per_program"],
                "fertility_tok_per_char": e["fertility_tok_per_char"],
                "delta_nll_per_char": d.get("point"),
                "delta_nll_per_char_lo": d.get("ci95_lo"),
                "delta_nll_per_char_hi": d.get("ci95_hi"),
                "delta_nll_per_token": (e.get("delta_nll_per_token") or {}).get("point"),
                "nll_seconds_total": e["nll_scoring_seconds_total"],
            })
    for model, m in B["models"].items():
        for cond, ce in m["conditions"].items():
            for lang, e in ce["languages"].items():
                comp = ce["comparisons"].get(lang, {}).get("semantic", {})
                flat.append({
                    "lane": "B", "model": model, "n_parameters": m["n_parameters"],
                    "device": m["device"], "precision": m["precision"],
                    "language": lang, "condition": cond,
                    "n": e["semantic_accuracy"]["denominator"],
                    "semantic_correct_k": e["semantic_accuracy"]["numerator"],
                    "semantic_accuracy": e["semantic_accuracy"]["proportion"],
                    "semantic_wilson_lo": e["semantic_accuracy"]["wilson95_lo"],
                    "semantic_wilson_hi": e["semantic_accuracy"]["wilson95_hi"],
                    "parse_validity": e["parse_validity"]["proportion"],
                    "language_compliance": e["language_compliance"]["proportion"],
                    "vacuous_rate": e["vacuous_rate"]["proportion"],
                    "op_selection": e["per_task"]["op-selection"]["proportion"],
                    "selector_resolution": e["per_task"]["selector-resolution"]["proportion"],
                    "arg_extraction": e["per_task"]["arg-extraction"]["proportion"],
                    "multi_op": e["per_task"]["multi-op"]["proportion"],
                    "risk_difference_vs_identity": comp.get("risk_difference"),
                    "rd_ci95_lo": comp.get("ci95_lo"), "rd_ci95_hi": comp.get("ci95_hi"),
                    "mcnemar_p": (comp.get("mcnemar") or {}).get("p_value"),
                    "input_tokens_median": e["input_tokens"]["median"],
                    "output_tokens_median": e["output_tokens"]["median"],
                    "e2e_seconds_median": e["e2e_seconds"]["median"],
                    "e2e_seconds_p95": e["e2e_seconds"]["p95"],
                    "decode_seconds_median": e["decode_seconds"]["median"],
                    "prefill_seconds_median": e["prefill_seconds"]["median"],
                    "output_tok_per_s_median": e["output_tokens_per_second"]["median"],
                    "peak_vram_allocated_bytes": m["peak_vram_allocated_bytes"],
                    "peak_rss_bytes": m["peak_rss_bytes"],
                })
    fields = sorted({k for r in flat for k in r})
    fields = (["lane", "model", "language", "condition", "n"]
              + [f for f in fields if f not in ("lane", "model", "language", "condition", "n")])
    write_csv(os.path.join(RUN, "metrics", "aggregate.csv"), flat, fields)

    # per-language and per-model slices
    for lang in LANGUAGES:
        write_csv(os.path.join(RUN, "metrics", "by_language", lang, "rows.csv"),
                  [r for r in flat if r["language"] == lang], fields)
    for model in {r["model"] for r in flat}:
        safe = model.replace("/", "__").replace(" ", "_").replace("[", "").replace("]", "")
        write_csv(os.path.join(RUN, "metrics", "by_model", f"{safe}.csv"),
                  [r for r in flat if r["model"] == model], fields)

    print(f"lane A models: {list(A['models'])}")
    print(f"lane B models: {list(B['models'])}")
    print(f"blocked: {[b['model']+' ('+str(b.get('failure_kind'))+')' for b in A['blocked']+B['blocked']]}")
    print(f"aggregate.csv rows: {len(flat)}")
    print(f"paired items: {len(B['paired_items'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
