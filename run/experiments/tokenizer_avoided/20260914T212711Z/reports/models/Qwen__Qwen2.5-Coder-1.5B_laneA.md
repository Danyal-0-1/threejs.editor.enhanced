# `Qwen/Qwen2.5-Coder-1.5B` — model report

_Run `20260914T212711Z` · Lane A_

## Identity

- **Checkpoint type:** Base
- **Resolved revision:** `df3ce67c0e24480f20468b6ef2894622d69eb73b`
- **Parameters:** 1,543,714,304
- **Tokenizer:** Qwen2 BPE (shared across the Qwen2.5-Coder family)
- **Device / precision:** `cuda` / `fp32`
- **Cold model-load time:** 3.2166 s
- **Warm-up time (excluded from per-case latency):** 0.6731 s
- **Peak VRAM allocated:** 6293092352 bytes
- **Peak process RSS:** 10104541184 bytes

## Completed cells

- 62 paired programs × 4 languages = 248 NLL scorings

## Lane A results

| language | NLL/char | NLL/token | perplexity | tokens/program | ΔNLL/char | 95% CI |
|---|---:|---:|---:|---:|---:|---|
| `identity` | 1.2723 | 3.8202 | 45.61 | 19.435 | — | — |
| `alpha` | 1.9034 | 5.3381 | 208.12 | 20.306 | +0.6311 | [+0.5867, +0.6778] |
| `beta` | 2.9802 | 6.2903 | 539.32 | 27.226 | +1.7079 | [+1.6159, +1.7901] |
| `gamma` | 4.3941 | 6.7086 | 819.38 | 26.968 | +3.1218 | [+2.9225, +3.3056] |

These are base-model likelihoods on teacher-forced programs. **No training occurred**; there is no training-loss curve.

## Failures

- None. No OOM, timeout or harness error was recorded for this model under the configuration reported above.

## Scaling interpretation

See `plots/overall/09_model_size_scaling` for accuracy against parameter count and `plots/overall/06_nll_per_char` for surprise against size. With three or four sizes these are trends, not fitted scaling laws.
