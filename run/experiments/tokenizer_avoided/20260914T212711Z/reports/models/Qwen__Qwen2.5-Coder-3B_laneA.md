# `Qwen/Qwen2.5-Coder-3B` — model report

_Run `20260914T212711Z` · Lane A_

## Identity

- **Checkpoint type:** Base
- **Resolved revision:** `09d9bc5d376b0cfa0100a0694ea7de7232525803`
- **Parameters:** 3,085,938,688
- **Tokenizer:** Qwen2 BPE (shared across the Qwen2.5-Coder family)
- **Device / precision:** `cuda` / `fp32`
- **Cold model-load time:** 5.0417 s
- **Warm-up time (excluded from per-case latency):** 0.5925 s
- **Peak VRAM allocated:** 12463155200 bytes
- **Peak process RSS:** 19359514624 bytes

## Completed cells

- 62 paired programs × 4 languages = 248 NLL scorings

## Lane A results

| language | NLL/char | NLL/token | perplexity | tokens/program | ΔNLL/char | 95% CI |
|---|---:|---:|---:|---:|---:|---|
| `identity` | 1.2491 | 3.7505 | 42.54 | 19.435 | — | — |
| `alpha` | 1.9021 | 5.3344 | 207.35 | 20.306 | +0.6530 | [+0.6089, +0.6991] |
| `beta` | 2.9121 | 6.1466 | 467.14 | 27.226 | +1.6631 | [+1.5701, +1.7472] |
| `gamma` | 3.9138 | 5.9752 | 393.54 | 26.968 | +2.6647 | [+2.4849, +2.8321] |

These are base-model likelihoods on teacher-forced programs. **No training occurred**; there is no training-loss curve.

## Failures

- None. No OOM, timeout or harness error was recorded for this model under the configuration reported above.

## Scaling interpretation

See `plots/overall/09_model_size_scaling` for accuracy against parameter count and `plots/overall/06_nll_per_char` for surprise against size. With three or four sizes these are trends, not fitted scaling laws.
