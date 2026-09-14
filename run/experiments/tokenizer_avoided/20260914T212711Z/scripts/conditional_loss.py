"""conditional_loss.py — SECONDARY: conditional task loss on Instruct models.

Condition on the EXACT chat prompt, teacher-force the frozen canonical gold
completion for that language, mask the prompt tokens, and compute loss over the
target-completion tokens only.

Reported SEPARATELY from Lane A: it answers a different question (how surprising
is the correct answer, given the instruction) and it depends on the chosen
reference serialisation -- the gold program string. A different but equally
correct serialisation would give different numbers.
"""
from __future__ import annotations

import argparse, gc, json, os, sys, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)

import prompts as P
import checkpoint as C

SEED = 20260910


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--precision", default="fp16")
    ap.add_argument("--device", default="cuda")
    args = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    dtype = {"fp16": torch.float16, "fp32": torch.float32,
             "bf16": torch.bfloat16}[args.precision]

    with open(os.path.join(RUN, "inputs", "task_dataset.json"), encoding="utf-8") as fh:
        cases = [c for c in json.load(fh)["cases"] if c.get("gold_renderings")]

    meta = {"model": args.model, "lane": "B-conditional-loss",
            "precision": args.precision, "device": args.device, "seed": SEED}
    try:
        tok = AutoTokenizer.from_pretrained(args.model)
        model = AutoModelForCausalLM.from_pretrained(args.model, dtype=dtype)
        model.to(args.device).eval()
    except Exception as exc:
        meta.update(status="BLOCKED", error=f"{type(exc).__name__}: {exc}"[:600],
                    failure_kind=("OOM" if "out of memory" in str(exc).lower() else "load"),
                    traceback=traceback.format_exc()[-1500:])
        C.append_row(args.out.replace(".jsonl", ".meta.jsonl"), meta)
        print(f"BLOCKED {args.model}: {exc}", flush=True)
        return 4
    meta["revision"] = getattr(model.config, "_commit_hash", None) or "unresolved"
    done = C.load_done(args.out)
    n = 0
    for case in cases:
        for language in P.LANGUAGES:
            for condition in P.SUPPORT_CONDITIONS:
                gold = case["gold_renderings"][language]
                messages = P.render_messages(case, language, condition)
                prompt = tok.apply_chat_template(messages, tokenize=False,
                                                 add_generation_prompt=True)
                target = f"```\n{gold}\n```"
                key = C.result_key(model=args.model, revision=meta["revision"],
                                   tokenizer_revision=meta["revision"],
                                   lane="Bcond", language=language,
                                   condition=condition, case_id=case["id"],
                                   seed=SEED, precision=args.precision,
                                   device=args.device,
                                   prompt_hash=C.text_hash(prompt + target))
                if key in done:
                    continue
                row = {"result_key": key, "model": args.model,
                       "revision": meta["revision"], "lane": "B-conditional-loss",
                       "language": language, "condition": condition,
                       "case_id": case["id"], "precision": args.precision,
                       "device": args.device, "target_text": target,
                       "target_chars": len(target)}
                try:
                    p_ids = tok(prompt, return_tensors="pt").input_ids
                    full = tok(prompt + target, return_tensors="pt").input_ids.to(args.device)
                    n_prompt = p_ids.shape[1]
                    if full.shape[1] <= n_prompt:
                        raise ValueError("target contributed no tokens")
                    t0 = time.perf_counter()
                    with torch.inference_mode():
                        logits = model(full).logits
                    lp = torch.log_softmax(logits[0, :-1].float(), dim=-1)
                    picked = lp.gather(-1, full[0, 1:].unsqueeze(-1)).squeeze(-1)
                    # mask the prompt: score ONLY the completion tokens
                    picked = picked[n_prompt - 1:]
                    if args.device.startswith("cuda"):
                        torch.cuda.synchronize()
                    row.update(
                        total_nll_nats=float(-picked.sum().item()),
                        target_tokens=int(picked.numel()),
                        nll_per_target_token=float(-picked.mean().item()),
                        nll_per_target_char=float(-picked.sum().item()) / len(target),
                        prompt_tokens=int(n_prompt),
                        seconds=round(time.perf_counter() - t0, 6),
                        outcome="VERIFIED")
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
    print(f"[done] {args.model}: {n} rows", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
