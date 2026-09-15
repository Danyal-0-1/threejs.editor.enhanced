"""labeling.py — TASK 4: the labeling probe, run as a NEGATIVE CONTROL.

Labeling is language-independent: the model is shown a descriptor row harvested
from an asset and asked for a human part name. No DSL is involved, so there is
no identity/alpha/beta/gamma dimension here and none is invented.

WHY IT IS RUN AT ALL
    It establishes that a model which scores poorly on alien-syntax generation
    is not simply incompetent at the surrounding domain. If labeling holds up
    while DSL accuracy falls, the DSL effect is specific rather than general.

WHY IT IS NOT EVIDENCE OF A SYNTAX EFFECT
    Per the work order: repeated labeling scores must NOT be used as evidence of
    a syntax effect. It is reported in its own section and never pooled with
    generation accuracy.

Two probes, mirroring the production/eval split in editMatrix.js:
    bare        the descriptor row alone
    scaffolded  the row plus the asset context and an explanation of the row
                schema (what production's labelPass actually supplies)
"""
from __future__ import annotations

import argparse, gc, json, os, sys, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "grammar_and_3DOM_client"))

import checkpoint as C
import tasks as T

SEED = 20260910

SYSTEM_BARE = (
    "You name parts of 3D models. Given a short descriptor of one part, reply "
    "with ONLY the common human name for that part. No explanation, no "
    "punctuation, just the name.")

SYSTEM_SCAFFOLDED = (
    "You name parts of 3D models. You are given one row from a part table.\n"
    "The row lists, in order: the graph ROLE ('leaf' means a single mesh), then "
    "shape and position descriptors, then optionally the MATERIAL name, which is "
    "a STRONG hint about what the part is.\n"
    "Reply with ONLY the common human name for that part. No explanation, no "
    "punctuation, just the name.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--precision", default="fp16")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--max-new-tokens", type=int, default=24)
    args = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    dtype = {"fp16": torch.float16, "fp32": torch.float32,
             "bf16": torch.bfloat16}[args.precision]

    with open(os.path.join(RUN, "inputs", "task_dataset.json"), encoding="utf-8") as fh:
        cases = json.load(fh)["labeling_cases"]

    meta = {"model": args.model, "lane": "B-labeling-control",
            "precision": args.precision, "device": args.device, "seed": SEED,
            "n_cases": len(cases)}
    try:
        tok = AutoTokenizer.from_pretrained(args.model)
        model = AutoModelForCausalLM.from_pretrained(args.model, dtype=dtype)
        model.to(args.device).eval()
    except Exception as exc:
        meta.update(status="BLOCKED", stage="load",
                    error=f"{type(exc).__name__}: {exc}"[:600],
                    failure_kind=("OOM" if "out of memory" in str(exc).lower() else "load"),
                    traceback=traceback.format_exc()[-1500:])
        C.append_row(args.out.replace(".jsonl", ".meta.jsonl"), meta)
        print(f"BLOCKED {args.model}: {exc}", flush=True)
        return 4
    meta["revision"] = getattr(model.config, "_commit_hash", None) or "unresolved"

    done = C.load_done(args.out)
    n = 0
    for idx, case in enumerate(cases):
        for condition in ("bare", "scaffolded"):
            system = SYSTEM_BARE if condition == "bare" else SYSTEM_SCAFFOLDED
            user = (f"Descriptor row: {case['desc']}"
                    + (f"\nThis part belongs to a {case['asset']}."
                       if condition == "scaffolded" else ""))
            messages = [{"role": "system", "content": system},
                        {"role": "user", "content": user}]
            text = tok.apply_chat_template(messages, tokenize=False,
                                           add_generation_prompt=True)
            key = C.result_key(model=args.model, revision=meta["revision"],
                               tokenizer_revision=meta["revision"],
                               lane="Blabel", language="none",
                               condition=condition, case_id=f"label{idx:02d}",
                               seed=SEED, precision=args.precision,
                               device=args.device, prompt_hash=C.text_hash(text))
            if key in done:
                continue
            row = {"result_key": key, "model": args.model,
                   "revision": meta["revision"], "lane": "B-labeling-control",
                   "language": "none", "condition": condition,
                   "case_id": f"label{idx:02d}", "kind": case["kind"],
                   "descriptor": case["desc"], "gold": case["gold"],
                   "precision": args.precision, "device": args.device}
            try:
                enc = tok(text, return_tensors="pt").to(args.device)
                if args.device.startswith("cuda"):
                    torch.cuda.synchronize()
                t0 = time.perf_counter()
                with torch.inference_mode():
                    out = model.generate(**enc, max_new_tokens=args.max_new_tokens,
                                         do_sample=False,
                                         pad_token_id=tok.pad_token_id or tok.eos_token_id)
                if args.device.startswith("cuda"):
                    torch.cuda.synchronize()
                row["seconds"] = round(time.perf_counter() - t0, 6)
                gen_ids = out[0][enc.input_ids.shape[1]:]
                resp = tok.decode(gen_ids, skip_special_tokens=True)
                row["raw_response"] = resp
                row["output_tokens"] = int(gen_ids.shape[0])
                ok, why = T.score_labeling_report(resp, case["gold"])
                row["labeling_correct"] = int(ok == 1.0)
                row["scorer_explanation"] = "; ".join(why)[:300]
                row["outcome"] = "VERIFIED"
            except torch.cuda.OutOfMemoryError as exc:
                row.update(outcome="OOM", error_category=f"OOM: {exc}"[:200])
                torch.cuda.empty_cache()
            except Exception as exc:
                row.update(outcome="HARNESS_ERROR",
                           error_category=f"{type(exc).__name__}: {exc}"[:200])
            C.append_row(args.out, row)
            n += 1
    meta["status"] = "VERIFIED"
    meta["rows_new"] = n
    C.append_row(args.out.replace(".jsonl", ".meta.jsonl"), meta)
    del model
    gc.collect()
    if args.device.startswith("cuda"):
        torch.cuda.empty_cache()
    print(f"[done] {args.model}: {n} labeling rows", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
