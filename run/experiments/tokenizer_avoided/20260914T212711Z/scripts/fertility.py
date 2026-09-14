"""fertility.py — tokenizer fertility per language, per tokenizer.

The Experiment 01 eligibility GATE is waived in this study, but fertility is
still measured, reported and treated as a CONFOUNDING VARIABLE. It directly
demonstrates increased token cost; whether accuracy degrades is a SEPARATE
measurement and must not be inferred from these numbers.

Definitions (identical to alien_syntax/measure/fertility.py, so the numbers are
comparable to the Experiment 01 archive):
    fertility (tok/char) = total tokens / total Unicode code points
    add_special_tokens=False -- BOS/EOS belong to the harness, not the lexicon
    corpus totals, never a mean of per-program ratios
    relative fertility = candidate fertility / identity fertility

DeepSeek-V3 appears here as a TOKENIZER ONLY. Its full weights (671B) are not
runnable on this machine; it is never behaviourally tested in this study.
"""
from __future__ import annotations

import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "alien_syntax", "src"))

import lane_a                                                          # noqa: E402

TOKENIZERS = [
    ("Qwen/Qwen2.5-Coder-0.5B", "behavioural+tokenizer"),
    ("Qwen/Qwen2.5-Coder-1.5B", "behavioural+tokenizer"),
    ("Qwen/Qwen2.5-Coder-3B", "behavioural+tokenizer"),
    ("Qwen/Qwen2.5-Coder-7B", "behavioural+tokenizer"),
    ("deepseek-ai/DeepSeek-V3", "TOKENIZER-ONLY (weights not runnable here)"),
]


def main() -> int:
    from transformers import AutoTokenizer
    corpora = lane_a.parallel_corpora()
    out = {"corpus_programs_per_language": {k: len(v) for k, v in corpora.items()},
           "tokenizers": [], "skipped": []}

    for repo, role in TOKENIZERS:
        try:
            tok = AutoTokenizer.from_pretrained(repo, trust_remote_code=False)
        except Exception as exc:
            out["skipped"].append({"repo": repo, "role": role,
                                   "status": "BLOCKED",
                                   "error": f"{type(exc).__name__}: {exc}"[:300]})
            print(f"BLOCKED {repo}: {type(exc).__name__}", flush=True)
            continue
        rows = {}
        for lang, programs in corpora.items():
            total = frag = 0
            per_prog = []
            for p in programs:
                ids = tok(p, add_special_tokens=False).input_ids
                total += len(ids)
                frag += sum(1 for i in ids if "�" in tok.decode([i]))
                per_prog.append(len(ids))
            chars = sum(len(p) for p in programs)
            utf8 = sum(len(p.encode("utf-8")) for p in programs)
            rows[lang] = {
                "total_tokens": total, "total_chars": chars, "total_utf8_bytes": utf8,
                "tokens_per_program": total / len(programs),
                "chars_per_program": chars / len(programs),
                "utf8_bytes_per_program": utf8 / len(programs),
                "fertility_tok_per_char": total / chars,
                "fertility_tok_per_utf8_byte": total / utf8,
                "fragmented_percent": 100.0 * frag / total,
                "tokens_per_program_list": per_prog,
            }
        base = rows["identity"]["fertility_tok_per_char"]
        for lang in rows:
            rows[lang]["relative_fertility_vs_identity"] = \
                rows[lang]["fertility_tok_per_char"] / base
        out["tokenizers"].append({
            "repo": repo, "role": role,
            "tokenizer_class": type(tok).__name__,
            "vocab_size": getattr(tok, "vocab_size", None),
            "tokenizer_length": len(tok),
            "is_fast": getattr(tok, "is_fast", None),
            "rows": rows,
        })
        print(f"{repo}: " + "  ".join(
            f"{l}={rows[l]['relative_fertility_vs_identity']:.3f}"
            for l in ("identity", "alpha", "beta", "gamma")), flush=True)

    dest = sys.argv[1]
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"wrote {dest}", flush=True)
    return 0 if out["tokenizers"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
