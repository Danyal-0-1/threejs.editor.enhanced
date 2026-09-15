# `Qwen/Qwen2.5-Coder-3B-Instruct` — model report

_Run `20260914T212711Z` · Lane B_

## Identity

- **Checkpoint type:** Instruct
- **Resolved revision:** `488639f1ff808d1d3d0ba301aef8c11461451ec5`
- **Parameters:** 3,085,938,688
- **Tokenizer:** Qwen2 BPE (shared across the Qwen2.5-Coder family)
- **Device / precision:** `cuda` / `fp16`
- **Cold model-load time:** 4.5286 s
- **Warm-up time (excluded from per-case latency):** 1.0394 s
- **Peak VRAM allocated:** 6452672512 bytes
- **Peak process RSS:** 13187829760 bytes

## Completed cells

- 176 rows total · 168 generation · 8 graceful-refusal · 0 error/OOM

## Lane B results

### bare

| language | semantic accuracy | parse validity | op-selection | selector-resolution | arg-extraction | multi-op | e2e s (med) | out tok (med) |
|---|---|---|---|---|---|---|---|---|
| `identity` | 57.1% (12/21, 95% CI 36.5%–75.5%) | 95.2% | 90.5% | 61.9% | 95.2% | 90.5% | 0.912 | 22 |
| `alpha` | 19.0% (4/21, 95% CI 7.7%–40.0%) | 61.9% | 33.3% | 42.9% | 47.6% | 33.3% | 0.921 | 22 |
| `beta` | 66.7% (14/21, 95% CI 45.4%–82.8%) | 100.0% | 95.2% | 66.7% | 100.0% | 95.2% | 1.178 | 28 |
| `gamma` | 38.1% (8/21, 95% CI 20.8%–59.1%) | 81.0% | 66.7% | 47.6% | 76.2% | 66.7% | 1.142 | 28 |

### scaffolded

| language | semantic accuracy | parse validity | op-selection | selector-resolution | arg-extraction | multi-op | e2e s (med) | out tok (med) |
|---|---|---|---|---|---|---|---|---|
| `identity` | 81.0% (17/21, 95% CI 60.0%–92.3%) | 100.0% | 95.2% | 85.7% | 100.0% | 95.2% | 0.997 | 22 |
| `alpha` | 42.9% (9/21, 95% CI 24.5%–63.5%) | 95.2% | 61.9% | 71.4% | 81.0% | 57.1% | 1.058 | 23 |
| `beta` | 85.7% (18/21, 95% CI 65.4%–95.0%) | 95.2% | 90.5% | 90.5% | 95.2% | 90.5% | 1.263 | 28 |
| `gamma` | 61.9% (13/21, 95% CI 40.9%–79.2%) | 85.7% | 71.4% | 76.2% | 81.0% | 71.4% | 1.234 | 29 |

### Graceful refusal (`merged-sheets`, scored separately)

| language/condition | correct |
|---|---|
| alpha/bare | 0/1 |
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
