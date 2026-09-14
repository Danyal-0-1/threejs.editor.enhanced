"""lane_a.py — LANE A: base-model prior strength / language-model surprise.

Teacher-forced causal-LM scoring of the 62-item paired positive corpus in each
of the four languages. NO TRAINING OCCURS. There is no training-loss curve and
no loss over epochs.

What the model sees: the PROGRAM STRING ONLY. No editing request, no
instruction prompt, NEUTRAL_PREFIX = "" for every language (BOS + program).

Alignment: logits[t] predicts ids[t+1], so the first token is never scored --
there is nothing to condition it on. That costs one token per program
IDENTICALLY in every lexicon, so the paired delta is unaffected.

Per-item rows are written so that every aggregate is reproducible from raw
evidence. Aggregation and bootstrap live in aggregate.py, not here.

These numbers are LANGUAGE-MODEL SURPRISE. They are never task accuracy,
hallucination rate, instruction following, or training loss.
"""
from __future__ import annotations

import argparse, gc, json, os, sys, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "alien_syntax", "src"))

import checkpoint as C
from phi import identity_phi, load_candidate                           # noqa: E402
import generate_corpus as G                                            # noqa: E402

LANGUAGES = ("identity", "alpha", "beta", "gamma")
SEED = 20260910
NEUTRAL_PREFIX = ""


def parallel_corpora() -> dict[str, list[str]]:
    """Index i is the SAME semantic program in every language."""
    out = {"identity": G.phase1_programs("positive", identity_phi())}
    for name in LANGUAGES[1:]:
        out[name] = G.generate(load_candidate(name), write=False)["positive"]
    lengths = {k: len(v) for k, v in out.items()}
    if len(set(lengths.values())) != 1:
        raise SystemExit(f"corpora are not matched: {lengths}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--precision", default="fp32", choices=["fp32", "fp16", "bf16"])
    ap.add_argument("--device", default="cuda")
    args = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    dtype = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}[args.precision]

    corpora = parallel_corpora()
    done = C.load_done(args.out)
    print(f"[resume] {len(done)} rows complete", flush=True)

    meta = {"model": args.model, "lane": "A", "precision": args.precision,
            "device": args.device, "seed": SEED, "prefix": NEUTRAL_PREFIX,
            "n_programs": len(corpora["identity"])}

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

    # warm-up, EXCLUDED from scoring time
    t0 = time.perf_counter()
    with torch.inference_mode():
        model(tok("warm up", return_tensors="pt").input_ids.to(args.device))
    if args.device.startswith("cuda"):
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
    meta["warmup_seconds"] = round(time.perf_counter() - t0, 4)
    print(f"[load] {args.model} load={meta['model_load_seconds']}s "
          f"params={meta['n_parameters']:,}", flush=True)

    n_new = 0
    for language in LANGUAGES:
        programs = corpora[language]
        t_lang = time.perf_counter()
        for idx, text in enumerate(programs):
            key = C.result_key(model=args.model, revision=meta["revision"],
                               tokenizer_revision=meta["tokenizer_revision"],
                               lane="A", language=language, condition="nll",
                               case_id=f"prog{idx:03d}", seed=SEED,
                               precision=args.precision, device=args.device,
                               prompt_hash=C.text_hash(text))
            if key in done:
                continue
            row = {"result_key": key, "model": args.model,
                   "revision": meta["revision"], "lane": "A",
                   "language": language, "program_index": idx,
                   "precision": args.precision, "device": args.device,
                   "program": text, "chars": len(text),
                   "utf8_bytes": len(text.encode("utf-8"))}
            try:
                if args.device.startswith("cuda"):
                    torch.cuda.synchronize()
                t = time.perf_counter()
                ids = tok(text, return_tensors="pt",
                          add_special_tokens=True).input_ids.to(args.device)
                with torch.inference_mode():
                    logits = model(ids).logits
                logprobs = torch.log_softmax(logits[0, :-1].float(), dim=-1)
                picked = logprobs.gather(-1, ids[0, 1:].unsqueeze(-1)).squeeze(-1)
                if args.device.startswith("cuda"):
                    torch.cuda.synchronize()
                row["nll_seconds"] = round(time.perf_counter() - t, 6)
                row["total_nll_nats"] = float(-picked.sum().item())
                row["scored_tokens"] = int(picked.numel())
                row["total_tokens_with_special"] = int(ids.shape[1])
                # fertility uses add_special_tokens=False: BOS/EOS belong to the
                # harness, not the lexicon, and would dilute the ratio.
                row["tokens_no_special"] = len(
                    tok(text, add_special_tokens=False).input_ids)
                row["outcome"] = "VERIFIED"
            except torch.cuda.OutOfMemoryError as exc:
                row.update(outcome="OOM", error_category=f"OOM: {exc}"[:300])
                torch.cuda.empty_cache()
            except Exception as exc:
                row.update(outcome="HARNESS_ERROR",
                           error_category=f"{type(exc).__name__}: {exc}"[:300])
            C.append_row(args.out, row)
            n_new += 1
        print(f"  {language:<9} {len(programs)} programs "
              f"in {time.perf_counter()-t_lang:.2f}s", flush=True)

    meta["status"] = "VERIFIED"
    meta["rows_new"] = n_new
    if args.device.startswith("cuda"):
        meta["peak_vram_allocated_bytes"] = int(torch.cuda.max_memory_allocated())
        meta["peak_vram_reserved_bytes"] = int(torch.cuda.max_memory_reserved())
    import resource
    meta["peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    C.append_row(args.out.replace(".jsonl", ".meta.jsonl"), meta)
    del model
    gc.collect()
    if args.device.startswith("cuda"):
        torch.cuda.empty_cache()
    print(f"[done] {args.model}: {n_new} rows", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
