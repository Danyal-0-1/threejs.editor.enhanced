"""prefetch_models.py — download weights on a login node and pin revisions.

Sol compute nodes are typically offline, so weights must be staged first.
This also writes the resolved revision sha for every model, which is what
makes a result traceable to the exact weights that produced it.

    export HF_HOME=/scratch/$USER/hf
    python sol/prefetch_models.py --tier small
"""
from __future__ import annotations
import argparse, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

TIERS = {
    "small": ["Qwen/Qwen2.5-Coder-0.5B", "Qwen/Qwen2.5-Coder-0.5B-Instruct",
              "Qwen/Qwen2.5-Coder-1.5B", "Qwen/Qwen2.5-Coder-1.5B-Instruct"],
    "mid": ["Qwen/Qwen2.5-Coder-3B", "Qwen/Qwen2.5-Coder-3B-Instruct",
            "Qwen/Qwen2.5-Coder-7B", "Qwen/Qwen2.5-Coder-7B-Instruct",
            "deepseek-ai/deepseek-coder-1.3b-base",
            "deepseek-ai/deepseek-coder-6.7b-base",
            "bigcode/starcoder2-3b", "bigcode/starcoder2-7b",
            "meta-llama/Llama-3.2-1B", "meta-llama/Llama-3.2-3B",
            "allenai/OLMo-2-1124-7B"],
    "large": ["Qwen/Qwen2.5-Coder-14B", "Qwen/Qwen2.5-Coder-32B",
              "bigcode/starcoder2-15b", "allenai/OLMo-2-1124-13B"],
}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="small", choices=[*TIERS, "all"])
    ap.add_argument("--out", default="outputs/model_pins.json")
    a = ap.parse_args(argv)
    ids = sum(TIERS.values(), []) if a.tier == "all" else TIERS[a.tier]

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from phase3_2 import runmeta

    ok, failed = [], {}
    for mid in ids:
        try:
            AutoTokenizer.from_pretrained(mid)
            AutoModelForCausalLM.from_pretrained(mid)      # cache only
            ok.append(mid)
            print(f"  cached  {mid}")
        except Exception as exc:
            failed[mid] = f"{type(exc).__name__}: {str(exc)[:120]}"
            print(f"  FAILED  {mid}: {failed[mid]}")

    pins = runmeta.pin(ok)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump({"pins": pins, "failed": failed}, open(a.out, "w"), indent=1)
    print(f"\n{len(ok)} cached, {len(failed)} failed -> {a.out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
