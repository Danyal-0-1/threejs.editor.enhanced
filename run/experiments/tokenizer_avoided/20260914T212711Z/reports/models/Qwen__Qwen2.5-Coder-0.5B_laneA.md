# `Qwen/Qwen2.5-Coder-0.5B` — model report

_Run `20260914T212711Z` · Lane A_

## Identity

- **Checkpoint type:** Base
- **Resolved revision:** `8123ea2e9354afb7ffcc6c8641d1b2f5ecf18301`
- **Parameters:** 494,032,768
- **Tokenizer:** Qwen2 BPE (shared across the Qwen2.5-Coder family)
- **Device / precision:** `cuda` / `fp32`
- **Cold model-load time:** 1.9222 s
- **Warm-up time (excluded from per-case latency):** 0.5688 s
- **Peak VRAM allocated:** 2092569600 bytes
- **Peak process RSS:** 3805642752 bytes

## Completed cells

- 62 paired programs × 4 languages = 248 NLL scorings

## Lane A results

| language | NLL/char | NLL/token | perplexity | tokens/program | ΔNLL/char | 95% CI |
|---|---:|---:|---:|---:|---:|---|
| `identity` | 1.3314 | 3.9978 | 54.48 | 19.435 | — | — |
| `alpha` | 1.8839 | 5.2834 | 197.04 | 20.306 | +0.5525 | [+0.5059, +0.6005] |
| `beta` | 3.0549 | 6.4481 | 631.49 | 27.226 | +1.7235 | [+1.6256, +1.8126] |
| `gamma` | 4.1503 | 6.3363 | 564.69 | 26.968 | +2.8189 | [+2.6293, +2.9919] |

These are base-model likelihoods on teacher-forced programs. **No training occurred**; there is no training-loss curve.

## Failures

- None. No OOM, timeout or harness error was recorded for this model under the configuration reported above.

## Scaling interpretation

See `plots/overall/09_model_size_scaling` for accuracy against parameter count and `plots/overall/06_nll_per_char` for surprise against size. With three or four sizes these are trends, not fitted scaling laws.
