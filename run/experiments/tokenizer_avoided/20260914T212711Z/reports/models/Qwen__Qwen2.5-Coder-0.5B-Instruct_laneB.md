# `Qwen/Qwen2.5-Coder-0.5B-Instruct` — model report

_Run `20260914T212711Z` · Lane B_

## Identity

- **Checkpoint type:** Instruct
- **Resolved revision:** `ea3f2471cf1b1f0db85067f1ef93848e38e88c25`
- **Parameters:** NA
- **Tokenizer:** Qwen2 BPE (shared across the Qwen2.5-Coder family)
- **Device / precision:** `cuda` / `fp16`
- **Cold model-load time:** None s
- **Warm-up time (excluded from per-case latency):** None s
- **Peak VRAM allocated:** None bytes
- **Peak process RSS:** None bytes

## Completed cells

- 65 rows total · 65 generation · 0 graceful-refusal · 0 error/OOM

## Lane B results

### bare

| language | semantic accuracy | parse validity | op-selection | selector-resolution | arg-extraction | multi-op | e2e s (med) | out tok (med) |
|---|---|---|---|---|---|---|---|---|
| `identity` | 12.5% (1/8, 95% CI 2.2%–47.1%) | 100.0% | 75.0% | 37.5% | 50.0% | 62.5% | 0.451 | 20 |
| `alpha` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 87.5% | 12.5% | 25.0% | 25.0% | 12.5% | 0.488 | 21 |
| `beta` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 100.0% | 62.5% | 12.5% | 37.5% | 62.5% | 0.568 | 24 |
| `gamma` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 100.0% | 12.5% | 12.5% | 12.5% | 12.5% | 0.516 | 22 |

### scaffolded

| language | semantic accuracy | parse validity | op-selection | selector-resolution | arg-extraction | multi-op | e2e s (med) | out tok (med) |
|---|---|---|---|---|---|---|---|---|
| `identity` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 100.0% | 50.0% | 12.5% | 37.5% | 37.5% | 0.590 | 25 |
| `alpha` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.606 | 26 |
| `beta` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 11.710 | 512 |
| `gamma` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 75.0% | 12.5% | 12.5% | 12.5% | 12.5% | 0.649 | 28 |

## Failures

- None. No OOM, timeout or harness error was recorded for this model under the configuration reported above.

## Scaling interpretation

See `plots/overall/09_model_size_scaling` for accuracy against parameter count and `plots/overall/06_nll_per_char` for surprise against size. With three or four sizes these are trends, not fitted scaling laws.
