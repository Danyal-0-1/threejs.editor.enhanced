# `Qwen/Qwen2.5-Coder-0.5B-Instruct` — model report

_Run `20260914T212711Z` · Lane B_

## Identity

- **Checkpoint type:** Instruct
- **Resolved revision:** `ea3f2471cf1b1f0db85067f1ef93848e38e88c25`
- **Parameters:** 494,032,768
- **Tokenizer:** Qwen2 BPE (shared across the Qwen2.5-Coder family)
- **Device / precision:** `cuda` / `fp16`
- **Cold model-load time:** 2.4692 s
- **Warm-up time (excluded from per-case latency):** 0.9172 s
- **Peak VRAM allocated:** 1068145664 bytes
- **Peak process RSS:** 2818985984 bytes

## Completed cells

- 176 rows total · 168 generation · 8 graceful-refusal · 0 error/OOM

## Lane B results

### bare

| language | semantic accuracy | parse validity | op-selection | selector-resolution | arg-extraction | multi-op | e2e s (med) | out tok (med) |
|---|---|---|---|---|---|---|---|---|
| `identity` | 14.3% (3/21, 95% CI 5.0%–34.6%) | 95.2% | 66.7% | 28.6% | 76.2% | 52.4% | 0.483 | 21 |
| `alpha` | 0.0% (0/21, 95% CI 0.0%–15.5%) | 61.9% | 9.5% | 19.0% | 38.1% | 9.5% | 0.518 | 23 |
| `beta` | 4.8% (1/21, 95% CI 0.8%–22.7%) | 95.2% | 66.7% | 9.5% | 71.4% | 57.1% | 0.626 | 27 |
| `gamma` | 0.0% (0/21, 95% CI 0.0%–15.5%) | 95.2% | 4.8% | 9.5% | 61.9% | 4.8% | 0.548 | 24 |

### scaffolded

| language | semantic accuracy | parse validity | op-selection | selector-resolution | arg-extraction | multi-op | e2e s (med) | out tok (med) |
|---|---|---|---|---|---|---|---|---|
| `identity` | 4.8% (1/21, 95% CI 0.8%–22.7%) | 90.5% | 28.6% | 9.5% | 66.7% | 23.8% | 0.835 | 35 |
| `alpha` | 0.0% (0/21, 95% CI 0.0%–15.5%) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 1.835 | 80 |
| `beta` | 0.0% (0/21, 95% CI 0.0%–15.5%) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 11.691 | 512 |
| `gamma` | 0.0% (0/21, 95% CI 0.0%–15.5%) | 52.4% | 4.8% | 4.8% | 28.6% | 4.8% | 0.697 | 29 |

### Graceful refusal (`merged-sheets`, scored separately)

| language/condition | correct |
|---|---|
| alpha/bare | 1/1 |
| alpha/scaffolded | 0/1 |
| beta/bare | 1/1 |
| beta/scaffolded | 0/1 |
| gamma/bare | 1/1 |
| gamma/scaffolded | 0/1 |
| identity/bare | 1/1 |
| identity/scaffolded | 0/1 |

## Failures

- None. No OOM, timeout or harness error was recorded for this model under the configuration reported above.

## Scaling interpretation

See `plots/overall/09_model_size_scaling` for accuracy against parameter count and `plots/overall/06_nll_per_char` for surprise against size. With three or four sizes these are trends, not fitted scaling laws.
