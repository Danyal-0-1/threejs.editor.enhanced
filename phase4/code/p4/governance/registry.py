"""registry.py — every model the programme may touch, with its pairing.

Selection axes that matter more than size (Phase 3.2 decision):
  * matched base/instruct PAIRS -- H4 predicts an instruct checkpoint's
    reversion from its base checkpoint, so an unpaired model cannot enter H4;
  * TOKENIZER diversity -- P32-001's merge behaviour is a property of the
    tokenizer, so `k_common` differs per family. That is the point.

Repo ids are as known on 2026-10-05 and are VERIFIED, not assumed, by
`prefetch --dry-run` on Sol, which lists any that do not resolve.

SCALE (deviation D10, 2026-10-07). The registered 3B ceiling is replaced by
72B. The Qwen2.5-Coder ladder 0.5B -> 32B holds the tokenizer and training
recipe fixed, so it is the one clean scale contrast; DeepSeek-Coder-33B adds a
second code family at the large end; Qwen2.5-72B (general, same tokenizer
family) extends the curve and is the only model that needs two GPUs. All of
them run in bf16 with the fp32 output head -- never quantized, because the
outcome is the SIGN of a margin. `gpus` is the number of A100-80GB GPUs one
checkpoint needs for scoring.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    id: str
    family: str
    size_b: float
    kind: str                 # base | instruct
    pair: str | None          # the counterpart checkpoint
    tier: str                 # small | mid | large | xlarge
    gated: bool = False       # needs an HF token (never stored by this code)
    gpus: int = 1             # A100-80GB GPUs needed to score it in bf16 + fp32 head


def _pair(fam, size, base, inst, tier, gated=False, gpus=1):
    return [ModelSpec(base, fam, size, "base", inst, tier, gated, gpus),
            ModelSpec(inst, fam, size, "instruct", base, tier, gated, gpus)]


_SPECS: list[ModelSpec] = [
    *_pair("qwen2.5-coder", 0.5, "Qwen/Qwen2.5-Coder-0.5B", "Qwen/Qwen2.5-Coder-0.5B-Instruct", "small"),
    *_pair("qwen2.5-coder", 1.5, "Qwen/Qwen2.5-Coder-1.5B", "Qwen/Qwen2.5-Coder-1.5B-Instruct", "small"),
    *_pair("qwen2.5-coder", 3.0, "Qwen/Qwen2.5-Coder-3B", "Qwen/Qwen2.5-Coder-3B-Instruct", "mid"),
    *_pair("qwen2.5-coder", 7.0, "Qwen/Qwen2.5-Coder-7B", "Qwen/Qwen2.5-Coder-7B-Instruct", "mid"),
    *_pair("qwen2.5-coder", 14.0, "Qwen/Qwen2.5-Coder-14B", "Qwen/Qwen2.5-Coder-14B-Instruct", "large"),
    *_pair("qwen2.5-coder", 32.0, "Qwen/Qwen2.5-Coder-32B", "Qwen/Qwen2.5-Coder-32B-Instruct", "large"),
    *_pair("deepseek-coder", 1.3, "deepseek-ai/deepseek-coder-1.3b-base", "deepseek-ai/deepseek-coder-1.3b-instruct", "small"),
    *_pair("deepseek-coder", 6.7, "deepseek-ai/deepseek-coder-6.7b-base", "deepseek-ai/deepseek-coder-6.7b-instruct", "mid"),
    *_pair("deepseek-coder", 33.0, "deepseek-ai/deepseek-coder-33b-base", "deepseek-ai/deepseek-coder-33b-instruct", "large"),
    # ~145 GB of bf16 weights + a 5 GB fp32 head: sharded over two A100-80GB
    *_pair("qwen2.5", 72.0, "Qwen/Qwen2.5-72B", "Qwen/Qwen2.5-72B-Instruct", "xlarge", gpus=2),
    *_pair("llama-3.2", 1.0, "meta-llama/Llama-3.2-1B", "meta-llama/Llama-3.2-1B-Instruct", "small", gated=True),
    *_pair("llama-3.2", 3.0, "meta-llama/Llama-3.2-3B", "meta-llama/Llama-3.2-3B-Instruct", "mid", gated=True),
    *_pair("olmo-2", 7.0, "allenai/OLMo-2-1124-7B", "allenai/OLMo-2-1124-7B-Instruct", "mid"),
    *_pair("olmo-2", 13.0, "allenai/OLMo-2-1124-13B", "allenai/OLMo-2-1124-13B-Instruct", "large"),
    # StarCoder2 base checkpoints have no matched instruct twin at 3B/7B, so
    # they can enter Arm A and fertility but never H4.
    ModelSpec("bigcode/starcoder2-3b", "starcoder2", 3.0, "base", None, "mid"),
    ModelSpec("bigcode/starcoder2-7b", "starcoder2", 7.0, "base", None, "mid"),
]

REGISTRY: dict[str, ModelSpec] = {m.id: m for m in _SPECS}
TIERS = ("small", "mid", "large", "xlarge")


def gpus_needed(model_id: str) -> int:
    return spec(model_id).gpus


def spec(model_id: str) -> ModelSpec:
    if model_id not in REGISTRY:
        raise KeyError(f"{model_id!r} is not in the model registry; add it "
                       f"deliberately rather than scoring an unregistered model")
    return REGISTRY[model_id]


def tier_models(tier: str) -> list[str]:
    if tier == "all":
        return sorted(REGISTRY)
    return sorted(m.id for m in _SPECS if m.tier == tier)


def validate_pairs(ids: list[str]) -> list[str]:
    """Problems with base/instruct pairing in a requested set (empty = fine)."""
    problems = []
    have = set(ids)
    for mid in ids:
        s = spec(mid)
        if s.pair and s.pair not in have:
            problems.append(f"{mid} requested without its {('instruct' if s.kind == 'base' else 'base')} "
                            f"pair {s.pair} -- it cannot enter H4")
        if s.pair:
            t = spec(s.pair)
            if (t.family, t.size_b) != (s.family, s.size_b) or t.kind == s.kind:
                problems.append(f"registry pairing inconsistent for {mid} <-> {s.pair}")
    return problems
