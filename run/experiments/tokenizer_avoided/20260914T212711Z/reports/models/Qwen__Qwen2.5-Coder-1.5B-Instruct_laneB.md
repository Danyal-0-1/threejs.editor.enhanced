# `Qwen/Qwen2.5-Coder-1.5B-Instruct` — model report

_Run `20260914T212711Z` · Lane B_

## Identity

- **Checkpoint type:** Instruct
- **Resolved revision:** `2e1fd397ee46e1388853d2af2c993145b0f1098a`
- **Parameters:** 1,543,714,304
- **Tokenizer:** Qwen2 BPE (shared across the Qwen2.5-Coder family)
- **Device / precision:** `cuda` / `fp16`
- **Cold model-load time:** 2.8392 s
- **Warm-up time (excluded from per-case latency):** 1.0389 s
- **Peak VRAM allocated:** 3219994112 bytes
- **Peak process RSS:** 7017725952 bytes

## Completed cells

- 176 rows total · 168 generation · 8 graceful-refusal · 0 error/OOM

## Lane B results

### bare

| language | semantic accuracy | parse validity | op-selection | selector-resolution | arg-extraction | multi-op | e2e s (med) | out tok (med) |
|---|---|---|---|---|---|---|---|---|
| `identity` | 42.9% (9/21, 95% CI 24.5%–63.5%) | 85.7% | 81.0% | 47.6% | 85.7% | 81.0% | 0.713 | 24 |
| `alpha` | 14.3% (3/21, 95% CI 5.0%–34.6%) | 71.4% | 47.6% | 38.1% | 52.4% | 38.1% | 0.664 | 24 |
| `beta` | 19.0% (4/21, 95% CI 7.7%–40.0%) | 90.5% | 42.9% | 38.1% | 66.7% | 42.9% | 0.864 | 29 |
| `gamma` | 19.0% (4/21, 95% CI 7.7%–40.0%) | 66.7% | 38.1% | 38.1% | 57.1% | 33.3% | 0.874 | 30 |

### scaffolded

| language | semantic accuracy | parse validity | op-selection | selector-resolution | arg-extraction | multi-op | e2e s (med) | out tok (med) |
|---|---|---|---|---|---|---|---|---|
| `identity` | 57.1% (12/21, 95% CI 36.5%–75.5%) | 100.0% | 85.7% | 76.2% | 95.2% | 95.2% | 0.745 | 25 |
| `alpha` | 38.1% (8/21, 95% CI 20.8%–59.1%) | 81.0% | 57.1% | 57.1% | 66.7% | 57.1% | 0.745 | 23 |
| `beta` | 28.6% (6/21, 95% CI 13.8%–50.0%) | 95.2% | 52.4% | 66.7% | 81.0% | 52.4% | 0.901 | 29 |
| `gamma` | 38.1% (8/21, 95% CI 20.8%–59.1%) | 95.2% | 57.1% | 66.7% | 85.7% | 52.4% | 0.915 | 29 |

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
