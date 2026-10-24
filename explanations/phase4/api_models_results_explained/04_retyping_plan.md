# 04 — Retyping plan: the code behind the served-model results

> **Scope.** The analysis code (export, Kaplan–Meier, bootstrap) is Phase 3.3's, and its retype
> plan is [`../../phase3_3/heldout_results_explained/04_retyping_plan.md`](../../phase3_3/heldout_results_explained/04_retyping_plan.md).
> This plan covers the code Phase 4 added to measure **served** models: the client, the scorer,
> the side-by-side runner, the probe, and the figures.
>
> **Line numbers** are those of `phase4/code/` in the commit that adds this document (2026-10-23).

---

## 1. Inventory

| file | lines | what it is |
|---|---:|---|
| [`p4/runtime/asu_api.py`](../../../phase4/code/p4/runtime/asu_api.py) | 134 | the address, the key, and one request with the gateway's retry rules |
| [`p4/scoring/api.py`](../../../phase4/code/p4/scoring/api.py) | 204 | `APIScorer`: the margin from the served tokens; the deployment pin |
| [`p4/experiments/pipeline.py`](../../../phase4/code/p4/experiments/pipeline.py), 406–410 and 443–476 | 39 | cells side by side for a served model |
| [`p4/governance/registry.py`](../../../phase4/code/p4/governance/registry.py), 83–133 and 148–157 | 61 | the 36 served models; `is_api`; `tier_models` |
| [`p4/governance/splits.py`](../../../phase4/code/p4/governance/splits.py), the Phase 4 block and `MAX_SIZE_B` | 15 | the nine development models; the 600B ceiling |
| [`p4/runtime/prefetch.py`](../../../phase4/code/p4/runtime/prefetch.py), `pin_served` and its call | 30 | pinning the deployment that answers |
| [`p4/runtime/preflight.py`](../../../phase4/code/p4/runtime/preflight.py), the served branches | 20 | no GPU check; the deployment against the pin |
| [`p4/scoring/fertility.py`](../../../phase4/code/p4/scoring/fertility.py), [`run.py`](../../../phase4/code/run.py) | 16 | routing served models |
| [`tools/voyager_models.py`](../../../phase4/code/tools/voyager_models.py) | 435 | the model list and the probe |
| [`tools/run_api_local.sh`](../../../phase4/code/tools/run_api_local.sh) | 53 | one process per model, on this machine |
| [`tools/retest_api.py`](../../../phase4/code/tools/retest_api.py) | 131 | re-scoring a sample |
| [`tools/paper_figures_api.py`](../../../phase4/code/tools/paper_figures_api.py) | 1,039 | the figures and tables, beside Phase 3.3 |
| **total** | **2,177** | |

---

## 2. Triage

| priority | code | why |
|---|---|---|
| **must** | `APIScorer._tokens`, `score_pair_detailed` | the measurement itself |
| **must** | `asu_api.request` | what happens when the network or the server misbehaves |
| **must** | `APIScorer.__init__`, `_post` | the deployment pin: what makes two answers comparable |
| should | `_score_cells_side_by_side` | concurrency that must not change a row |
| should | the probe's `_margin`, `resolution` | how rounding was detected |
| should | the figure script's bootstrap and Arm A block | how every interval in the figures is made |
| later | `registry`, `prefetch`, `preflight`, `run_api_local.sh` | plumbing |
| later | the figure script's drawing code | layout |

---

## 3. The short list: read these first

1. `p4/scoring/api.py` 120–146 (`_tokens`): what one request returns, and every way it is refused.
2. `p4/scoring/api.py` 165–180 (`score_pair_detailed`): the margin, in 16 lines.
3. `p4/runtime/asu_api.py` 90–134 (`request`): the retry rules.

---

## 4. Data structures, in the order they flow

| structure | where | holds |
|---|---|---|
| pin | `results/model_pins.json` | `revision` = `"<served name>@<system_fingerprint>"`, `tokenizer_id`, `quantization`, `pinned_utc` |
| request body | `api.py` `_tokens` | `prompt`, `max_tokens: 1`, `temperature: 0`, `return_token_ids`, `add_special_tokens: false`, `prompt_logprobs: 0` |
| answer | the server | `model`, `system_fingerprint`, `choices[0].prompt_token_ids`, `choices[0].prompt_logprobs` (one dict per position, keyed by token id) |
| `{"ids", "lps"}` | `api.py` `_tokens` | the token ids and their log-probabilities (`None` for position 0) |
| `PairScore` | `margins.py` | `logp_correct`, `logp_competitor`, `k_common`, `merged`, … `fp32_head=False` |
| row | `pipeline._score_into` | the 46 columns of `arm_a_long.csv`, with `model_revision`, `dtype` (= served precision) |
| per-template counts | `paper_figures_api.py` `acc` | arrays over templates: sites, reversions, ties, near-zero, rule-effect sums |

---

## 5. One end-to-end path to retype

**One site's margin, from the server to the figure.** `score_pair_detailed` sends three
`_tokens` requests → `check_pair(a, b)` gives `k` → the two sums give M → `_score_into` writes the
row → the merge and export write `arm_a_long.csv` → `paper_figures_api.py` counts M < 0 per
template → `ratio` and `draws` give the rate and its interval → Figure 1. The worked numbers are
in [03 §10](03_code_and_pipeline.md#10-one-site-through-the-api) and [02](02_mathematics_and_statistics.md).

---

## 6. What to retype: 295 lines, **13.6%** of 2,177

| # | file | lines | what | invariant | test after |
|---|---|---|---|---|---|
| 1 | `p4/runtime/asu_api.py` | 68–134 | `_connection`, `_drop`, `request` | one connection per thread; 429 waits 60 s; 500/502–504, timeouts and dropped connections back off and retry on a fresh connection; the key never in a result | `test_the_real_client_scrubs_the_key_from_an_error`, `test_the_real_client_retries_a_server_error_and_a_stall_on_a_fresh_connection` |
| 2 | `p4/scoring/api.py` | 69–96 | `__init__` | the first answer binds the deployment; a different pin raises | `test_an_answer_from_another_deployment_is_refused` |
| 3 | `p4/scoring/api.py` | 107–146 | `_post`, `_tokens` | every answer from the bound deployment; ids and log-probabilities aligned; special tokens off | `test_special_tokens_stay_off_even_where_the_server_would_add_them` |
| 4 | `p4/scoring/api.py` | 165–180 | `score_pair_detailed` | M = Σ lp_a[k:] − Σ lp_b[k:], `k` from `check_pair`; `merged` = a candidate's tokens do not outnumber the prefix's | `test_the_margin_is_margins_py_algorithm_on_the_served_tokens`, `test_merged_is_flagged_when_the_candidate_joins_the_prefix_token` |
| 5 | `p4/experiments/pipeline.py` | 406–410, 443–476 | `_score_cells_side_by_side` | rows written from one thread; identical to the serial loop | `test_a_served_model_runs_through_arm_a_and_arm_b` |
| 6 | `tools/voyager_models.py` | 239–265 | `_margin`, `resolution` | the coarsest 2^−j dividing every margin, tolerance 10⁻⁵ | `test_margin_resolution_tells_rounded_logits_from_full_precision` |
| 7 | `tools/paper_figures_api.py` | 188–214 | `draws`, `interval`, `ratio` | the same resamples as Phase 3.3's figure script, for the same stream key | the script's own export checks |
| 8 | `tools/paper_figures_api.py` | 393–443 | the Arm A accumulation | per-template sums; a tie (M = 0) is not a reversion | the script refuses on any mismatch with the export |

---

## 7. What to ignore for now

- The drawing code of `paper_figures_api.py` (layout, legends).
- `tools/run_api_local.sh` and the `_api` profiles of `sol/submit.sh` (process plumbing).
- `voyager_models.py`'s `list`, tables and chat checks (they decide nothing in the run).

---

## 8. The things you are most likely to get wrong

### (1) Counting a tie as a reversion
`m_seq < 0` is a reversion; `m_seq == 0` is a tie. Phase 3.3 never had a tie. With rounded
scores, ties happen (Table A1). `M ≤ 0` would raise every served model's rate.

### (2) Starting the sum at `k − 1`
The log-probability at position `j` is the probability of token `j` given tokens `0 … j−1`. The
first token that differs is at `k`, so the sums start at `k`. Position 0 has no log-probability
(`None`); `k ≥ 1` is guaranteed by `check_pair` (`NoContext`).

### (3) Leaving special tokens on
`add_special_tokens` defaults to true in vLLM. Five served models then add a beginning-of-text
token, and every `k` shifts by one.

### (4) Reading a served margin as exact
Rounding and batching both move margins near zero ([01 §4–5](01_theory.md)). Rates are robust;
single sites near zero are not.

### (5) Reading the development numbers as confirmatory
Every row says `DEVELOPMENT` ([01 §1](01_theory.md#1-development-evidence)).

### (6) Reading OLMo 3's Arm B as "cannot write 3DOM"
It ended its turn at once ([01 §10](01_theory.md#10-ending-the-turn-empty-generations)).

---

## 9. AI-code audit: the constants behind these results

| constant | value | where | status |
|---|---|---|---|
| request timeout | 150 s | `api.py` (`$P4_API_TIMEOUT`) | **apparently arbitrary**: long enough for a slow answer, short enough to escape a stalled connection |
| tries per request | 8 | `api.py` | **apparently arbitrary** |
| backoff | 5 s doubling, at most 120 s; 60 s on 429 | `asu_api.py` | 60 s and "back off" follow the gateway's documentation; 5 s and 120 s are **apparently arbitrary** |
| requests per pair | 3, at once | `api.py` (`workers`) | needed: prefix + two candidates |
| cells side by side | 1 (DeepSeek 2) | `$P4_API_CELL_WORKERS` | chosen after the stall; 2 stays within the gateway's advice of 4–8 requests per model |
| token-id cache | 4,096 texts | `api.py` | **apparently arbitrary**; only the prompt texts repeat |
| reference text | code, sigils, Unicode, layout | `api.py` `REFERENCE` | **apparently arbitrary**; it only fingerprints the tokenizer |
| near zero | 1/8 nat | `paper_figures_api.py` | the coarsest step seen in the probe (bf16 near 16–32) |
| the grid | 1/32 nat | `paper_figures_api.py` | the finest common step seen in the probe; descriptive only |
| `MAX_SIZE_B` | 600 | `splits.py` | chosen to admit DeepSeek (about 550B): **set to fit this choice of models**, recorded as such |
| probe timeout, tries | 60 s, 2 | `voyager_models.py` | **apparently arbitrary** |
| re-test sample | 300 sites per model, seed 20261023 | `retest_api.py` | **apparently arbitrary**; the seed is the date |
| bootstrap | B = 2000, seed 20261002 | `paper_figures_api.py` | registered in Phase 3.2's preregistration; reused |

---

## After retyping

You should be able to say, without the code open:

- which three numbers come back from one request, and which one the margin needs;
- why the sums start at `k`, and why a tie is not a reversion;
- what makes two answers comparable, and what happens when they are not;
- what the client does when the network stalls.
