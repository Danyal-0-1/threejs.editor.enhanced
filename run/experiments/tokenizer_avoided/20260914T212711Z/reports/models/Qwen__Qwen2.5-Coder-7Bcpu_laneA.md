# `Qwen/Qwen2.5-Coder-7B [cpu]` — model report

_Run `20260914T212711Z` · Lane A_

## Identity

- **Checkpoint type:** Base
- **Resolved revision:** `0396a76181e127dfc13e5c5ec48a8cee09938b02`
- **Parameters:** 7,615,616,512
- **Tokenizer:** Qwen2 BPE (shared across the Qwen2.5-Coder family)
- **Device / precision:** `cpu` / `fp32`
- **Cold model-load time:** 2.8284 s
- **Warm-up time (excluded from per-case latency):** 0.822 s
- **Peak VRAM allocated:** None bytes
- **Peak process RSS:** 46536339456 bytes

## Completed cells

- 62 paired programs × 4 languages = 248 NLL scorings

## Lane A results

| language | NLL/char | NLL/token | perplexity | tokens/program | ΔNLL/char | 95% CI |
|---|---:|---:|---:|---:|---:|---|
| `identity` | 1.2675 | 3.8058 | 44.96 | 19.435 | — | — |
| `alpha` | 1.8546 | 5.2011 | 181.48 | 20.306 | +0.5871 | [+0.5409, +0.6355] |
| `beta` | 2.8585 | 6.0335 | 417.16 | 27.226 | +1.5910 | [+1.5094, +1.6659] |
| `gamma` | 4.0497 | 6.1828 | 484.32 | 26.968 | +2.7822 | [+2.5852, +2.9682] |

These are base-model likelihoods on teacher-forced programs. **No training occurred**; there is no training-loss curve.

## Failures

- **OOM** in Lane A (fp32/cuda)
  - attempted: `lane_a.py --model Qwen/Qwen2.5-Coder-7B --precision fp32 --device cuda`
  - error: `OutOfMemoryError: CUDA out of memory. Tried to allocate 260.00 MiB. GPU 0 has a total capacity of 15.61 GiB of which 114.12 MiB is free. Including non-PyTorch memory, this process has 15.15 GiB memory in use. Of the allocated memory 14.87 GiB is allocated by PyTorch, and 91.35 MiB is reserved by PyTorch but unallocated. If reserved but unallocated memory is large try setting PYTORCH_CUDA_ALLOC_CON`

## Scaling interpretation

See `plots/overall/09_model_size_scaling` for accuracy against parameter count and `plots/overall/06_nll_per_char` for surprise against size. With three or four sizes these are trends, not fitted scaling laws.
