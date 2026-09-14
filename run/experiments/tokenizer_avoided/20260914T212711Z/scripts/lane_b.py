"""lane_b.py — LANE B: instruction-model behavioural accuracy.

One model, every language x condition x case, greedy and deterministic, scored
through the target language's PhiMap into the shared canonical IR.

NOT Lane A. These are INSTRUCT checkpoints answering an editing request. Their
numbers are task accuracy and must never be reported as base-model NLL.

Timing discipline
    - model load and warm-up are timed but EXCLUDED from per-case latency
    - torch.cuda.synchronize() brackets every GPU timing region
    - prefill and decode are timed separately (prefill = a 1-token generate)
    - `--reps` repetitions per case; median and IQR reported. Greedy decoding is
      deterministic, so repetitions measure TIMING ONLY and the harness asserts
      the text is identical across them (recorded as `deterministic`).
"""
from __future__ import annotations

import argparse, gc, json, os, statistics, sys, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)

import prompts as P
import score as S
import checkpoint as C
import extract as E

LANGUAGES = list(P.LANGUAGES)
CONDITIONS = list(P.SUPPORT_CONDITIONS)
SEED = 20260910


def latin_square_order(case_index: int) -> list[str]:
    """Rotate language order by case index so warm-cache and thermal drift are
    not assigned consistently to one language."""
    k = case_index % len(LANGUAGES)
    return LANGUAGES[k:] + LANGUAGES[:k]


def peak_rss_bytes() -> int:
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompts-dir", default=os.path.join(RUN, "prompts", "rendered"))
    ap.add_argument("--dataset", default=os.path.join(RUN, "inputs", "task_dataset.json"))
    ap.add_argument("--max-new-tokens", type=int, default=512)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--precision", default="fp16", choices=["fp16", "fp32", "bf16"])
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--limit-cases", type=int, default=0, help="smoke test: first N cases")
    ap.add_argument("--languages", nargs="*", default=None)
    ap.add_argument("--conditions", nargs="*", default=None)
    ap.add_argument("--cases", nargs="*", default=None,
                    help="restrict to these case IDs (sensitivity conditions)")
    ap.add_argument("--condition-suffix", default="",
                    help="tag appended to `condition` so a sensitivity run is a "
                         "SEPARATELY LABELLED condition and can never be pooled "
                         "with the primary matrix")
    args = ap.parse_args()

    langs = args.languages or LANGUAGES
    conds = args.conditions or CONDITIONS

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dtype = {"fp16": torch.float16, "fp32": torch.float32, "bf16": torch.bfloat16}[args.precision]
    with open(args.dataset, encoding="utf-8") as fh:
        ds = json.load(fh)
    cases = ds["cases"]
    if args.cases:
        want = set(args.cases)
        cases = [c for c in cases if c["id"] in want]
    if args.limit_cases:
        cases = cases[:args.limit_cases]

    done = C.load_done(args.out)
    print(f"[resume] {len(done)} rows already complete in {args.out}", flush=True)

    meta = {"model": args.model, "lane": "B", "precision": args.precision,
            "device": args.device, "max_new_tokens": args.max_new_tokens,
            "reps": args.reps, "seed": SEED}

    # ── load (timed, EXCLUDED from per-case latency) ────────────────────────
    t0 = time.perf_counter()
    try:
        tok = AutoTokenizer.from_pretrained(args.model)
        model = AutoModelForCausalLM.from_pretrained(args.model, dtype=dtype)
        model.to(args.device).eval()
    except Exception as exc:
        meta.update(status="BLOCKED", error=f"{type(exc).__name__}: {exc}"[:800],
                    traceback=traceback.format_exc()[-2000:],
                    failure_kind=("OOM" if "out of memory" in str(exc).lower() else "load"))
        C.append_row(args.out.replace(".jsonl", ".meta.jsonl"), meta)
        print(f"BLOCKED {args.model}: {exc}", flush=True)
        return 4
    if args.device.startswith("cuda"):
        torch.cuda.synchronize()
    meta["model_load_seconds"] = round(time.perf_counter() - t0, 4)
    meta["revision"] = getattr(model.config, "_commit_hash", None) or "unresolved"
    meta["tokenizer_revision"] = getattr(tok, "_commit_hash", None) or meta["revision"]
    meta["n_parameters"] = sum(p.numel() for p in model.parameters())
    meta["vocab_size"] = len(tok)

    # ── warm-up (EXCLUDED) ─────────────────────────────────────────────────
    t0 = time.perf_counter()
    with torch.inference_mode():
        warm = tok("warm up", return_tensors="pt").to(args.device)
        model.generate(**warm, max_new_tokens=8, do_sample=False,
                       pad_token_id=tok.pad_token_id or tok.eos_token_id)
    if args.device.startswith("cuda"):
        torch.cuda.synchronize()
    meta["warmup_seconds"] = round(time.perf_counter() - t0, 4)
    if args.device.startswith("cuda"):
        torch.cuda.reset_peak_memory_stats()
    print(f"[load] {args.model} load={meta['model_load_seconds']}s "
          f"warmup={meta['warmup_seconds']}s params={meta['n_parameters']:,}", flush=True)

    n_done = n_new = 0
    for ci, case in enumerate(cases):
        for language in latin_square_order(ci):
            if language not in langs:
                continue
            for condition in conds:
                messages = P.render_messages(case, language, condition)
                try:
                    text = tok.apply_chat_template(messages, tokenize=False,
                                                   add_generation_prompt=True)
                except Exception as exc:
                    text = (messages[0]["content"] + "\n\n" + messages[1]["content"])
                    meta.setdefault("chat_template_warning",
                                    f"{type(exc).__name__}: {exc}"[:200])
                prompt_hash = C.text_hash(text)
                cond_label = condition + args.condition_suffix
                key = C.result_key(model=args.model, revision=meta["revision"],
                                   tokenizer_revision=meta["tokenizer_revision"],
                                   lane="B", language=language, condition=cond_label,
                                   case_id=case["id"], seed=SEED,
                                   precision=args.precision, device=args.device,
                                   prompt_hash=prompt_hash)
                if key in done:
                    n_done += 1
                    continue

                # persist the EXACT model input
                pdir = os.path.join(args.prompts_dir, args.model.replace("/", "__"),
                                    language, condition)
                os.makedirs(pdir, exist_ok=True)
                with open(os.path.join(pdir, f"{case['id']}.txt"), "w", encoding="utf-8") as fh:
                    fh.write(text)

                row = {"result_key": key, "model": args.model,
                       "revision": meta["revision"],
                       "tokenizer_revision": meta["tokenizer_revision"],
                       "lane": "B", "language": language, "condition": cond_label,
                       "case_id": case["id"], "seed": SEED,
                       "precision": args.precision, "device": args.device,
                       "prompt_hash": prompt_hash,
                       "max_new_tokens": args.max_new_tokens}
                try:
                    t = time.perf_counter()
                    enc = tok(text, return_tensors="pt").to(args.device)
                    if args.device.startswith("cuda"):
                        torch.cuda.synchronize()
                    row["tokenize_seconds"] = round(time.perf_counter() - t, 6)
                    row["input_tokens"] = int(enc.input_ids.shape[1])
                    row["prompt_chars"] = len(text)

                    e2e, prefill, decode, outs = [], [], [], []
                    for _rep in range(args.reps):
                        if args.device.startswith("cuda"):
                            torch.cuda.synchronize()
                        t = time.perf_counter()
                        with torch.inference_mode():
                            out = model.generate(
                                **enc, max_new_tokens=args.max_new_tokens,
                                do_sample=False, num_beams=1,
                                pad_token_id=tok.pad_token_id or tok.eos_token_id)
                        if args.device.startswith("cuda"):
                            torch.cuda.synchronize()
                        e2e.append(time.perf_counter() - t)
                        outs.append(out)

                        # prefill measured as a 1-new-token generate
                        if args.device.startswith("cuda"):
                            torch.cuda.synchronize()
                        t = time.perf_counter()
                        with torch.inference_mode():
                            model.generate(**enc, max_new_tokens=1, do_sample=False,
                                           pad_token_id=tok.pad_token_id or tok.eos_token_id)
                        if args.device.startswith("cuda"):
                            torch.cuda.synchronize()
                        prefill.append(time.perf_counter() - t)
                        decode.append(e2e[-1] - prefill[-1])

                    out = outs[0]
                    gen_ids = out[0][enc.input_ids.shape[1]:]
                    response = tok.decode(gen_ids, skip_special_tokens=True)
                    texts = [tok.decode(o[0][enc.input_ids.shape[1]:],
                                        skip_special_tokens=True) for o in outs]
                    row["deterministic"] = int(len(set(texts)) == 1)
                    row["output_tokens"] = int(gen_ids.shape[0])
                    row["truncated"] = int(gen_ids.shape[0] >= args.max_new_tokens)
                    row["timeout"] = 0
                    row["oom"] = 0
                    row["e2e_seconds_median"] = round(statistics.median(e2e), 6)
                    row["e2e_seconds_all"] = [round(x, 6) for x in e2e]
                    row["e2e_iqr"] = (round(statistics.quantiles(e2e, n=4)[2]
                                            - statistics.quantiles(e2e, n=4)[0], 6)
                                      if len(e2e) >= 4 else None)
                    row["prefill_seconds_median"] = round(statistics.median(prefill), 6)
                    row["decode_seconds_median"] = round(statistics.median(decode), 6)
                    row["output_tokens_per_second"] = (
                        round(row["output_tokens"] / row["decode_seconds_median"], 4)
                        if row["decode_seconds_median"] > 0 else None)
                    row["raw_response"] = response
                    if args.device.startswith("cuda"):
                        row["peak_vram_allocated_bytes"] = int(torch.cuda.max_memory_allocated())
                        row["peak_vram_reserved_bytes"] = int(torch.cuda.max_memory_reserved())
                    row["peak_rss_bytes"] = peak_rss_bytes()

                    row.update(S.score_response(response, case, language))

                except torch.cuda.OutOfMemoryError as exc:
                    row.update(outcome=E.OOM, oom=1, error_category=f"OOM: {exc}"[:300],
                               raw_response=None)
                    torch.cuda.empty_cache()
                except Exception as exc:
                    row.update(outcome=E.HARNESS_ERROR,
                               error_category=f"{type(exc).__name__}: {exc}"[:300],
                               traceback=traceback.format_exc()[-1200:],
                               raw_response=None)

                C.append_row(args.out, row)
                n_new += 1
                print(f"  {case['id']:<20} {language:<9} {condition:<11} "
                      f"{row.get('outcome'):<14} out={row.get('output_tokens')} "
                      f"t={row.get('e2e_seconds_median')}s", flush=True)

    meta["status"] = "VERIFIED"
    meta["rows_new"] = n_new
    meta["rows_skipped_resume"] = n_done
    if args.device.startswith("cuda"):
        meta["peak_vram_allocated_bytes"] = int(torch.cuda.max_memory_allocated())
        meta["peak_vram_reserved_bytes"] = int(torch.cuda.max_memory_reserved())
    meta["peak_rss_bytes"] = peak_rss_bytes()
    C.append_row(args.out.replace(".jsonl", ".meta.jsonl"), meta)

    del model
    gc.collect()
    if args.device.startswith("cuda"):
        torch.cuda.empty_cache()
    print(f"[done] {args.model}: {n_new} new, {n_done} resumed", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
