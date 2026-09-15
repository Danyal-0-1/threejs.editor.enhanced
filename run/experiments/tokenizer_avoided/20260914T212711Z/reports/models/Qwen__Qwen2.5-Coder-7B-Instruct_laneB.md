# `Qwen/Qwen2.5-Coder-7B-Instruct` — model report

_Run `20260914T212711Z` · Lane B_

## Identity

- **Checkpoint type:** Instruct
- **Resolved revision:** `c03e6d358207e414f1eca0bb1891e29f1db0e242`
- **Parameters:** 7,615,616,512
- **Tokenizer:** Qwen2 BPE (shared across the Qwen2.5-Coder family)
- **Device / precision:** `cuda` / `fp16`
- **Cold model-load time:** 5.2669 s
- **Warm-up time (excluded from per-case latency):** 1.0459 s
- **Peak VRAM allocated:** 15557297152 bytes
- **Peak process RSS:** 31305658368 bytes

## Completed cells

- 176 rows total · 168 generation · 8 graceful-refusal · 0 error/OOM

## Lane B results

### bare

| language | semantic accuracy | parse validity | op-selection | selector-resolution | arg-extraction | multi-op | e2e s (med) | out tok (med) |
|---|---|---|---|---|---|---|---|---|
| `identity` | 71.4% (15/21, 95% CI 50.0%–86.2%) | 90.5% | 90.5% | 76.2% | 90.5% | 85.7% | 1.174 | 24 |
| `alpha` | 0.0% (0/21, 95% CI 0.0%–15.5%) | 9.5% | 4.8% | 0.0% | 4.8% | 4.8% | 1.216 | 24 |
| `beta` | 19.0% (4/21, 95% CI 7.7%–40.0%) | 100.0% | 81.0% | 38.1% | 90.5% | 81.0% | 1.477 | 31 |
| `gamma` | 33.3% (7/21, 95% CI 17.2%–54.6%) | 42.9% | 42.9% | 33.3% | 42.9% | 42.9% | 1.453 | 29 |

### scaffolded

| language | semantic accuracy | parse validity | op-selection | selector-resolution | arg-extraction | multi-op | e2e s (med) | out tok (med) |
|---|---|---|---|---|---|---|---|---|
| `identity` | 90.5% (19/21, 95% CI 71.1%–97.3%) | 95.2% | 95.2% | 90.5% | 95.2% | 95.2% | 1.442 | 23 |
| `alpha` | 4.8% (1/21, 95% CI 0.8%–22.7%) | 9.5% | 4.8% | 9.5% | 9.5% | 4.8% | 1.488 | 25 |
| `beta` | 52.4% (11/21, 95% CI 32.4%–71.7%) | 66.7% | 52.4% | 66.7% | 61.9% | 52.4% | 1.601 | 30 |
| `gamma` | 38.1% (8/21, 95% CI 20.8%–59.1%) | 38.1% | 38.1% | 38.1% | 38.1% | 38.1% | 1.684 | 30 |

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
