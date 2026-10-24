# 03 — Code and pipeline: how the served-model run was executed

> **Scope.** The pipeline itself (plan → score → shard → merge → export) is Phase 3.3's,
> explained in
> [`../../phase3_3/sol_experiment_explained/03_code_and_pipeline.md`](../../phase3_3/sol_experiment_explained/03_code_and_pipeline.md).
> This file covers what is new in Phase 4: **a model on someone else's server instead of
> weights on our GPU**, from the probe of the API to the figures.
>
> **Format.** Each stage is INPUT → TRANSFORMATION → OUTPUT → VALIDATION, with real dumps.
>
> **Times** are the laptop's local time (MST, UTC−7). Everything ran on the laptop: the API
> needs the network, not a GPU.

```
 2026-10-22                           2026-10-23
 list ─► probe ─► registry ─► pins ─► smoke ─► init ─► preflight ─► run (stall ─► fix ─► run) ─► DeepSeek ─► merge/export ─► re-score ─► figures
 52      42       36 served   9       2 min    90 cells  9 PASS      12:12        12:25        → 18:08        18:08–18:27    2,700 sites  18:38
```

---

## 0. The decision this run rests on

| | |
|---|---|
| **Input** | the short list of 2026-10-23: OLMo 3 7B Instruct, OLMo 3 32B Instruct and Think, Qwen3-Coder 30B-A3B, Gemma 4 31B; and, above the old 72B ceiling, DeepSeek-V4.1-Flash and Qwen3.5 at 27B, 122B and 397B |
| **Transformation** | the nine join `DEV_MODELS` in [`p4/governance/splits.py`](../../../phase4/code/p4/governance/splits.py); `MAX_SIZE_B` goes from Phase 3.3's 72 to 600 (total parameters), so DeepSeek (about 550B) is allowed |
| **Output** | a split under which the nine are **development** models |
| **Validation** | `test_every_model_phase3_3_scored_is_development_and_an_unseen_model_is_not`: `DEV_MODELS` is exactly Phase 3.3's 21 plus these 9, and every other model is held out or above the ceiling |

**What this costs.** A development model can never be Phase 4's held-out model. A confirmatory
test with these nine needs held-out *material* instead (new lexicons or a new grammar family);
see [06](06_publishability_and_paper.md).

---

## 1. The model list and the probe (2026-10-22)

| | |
|---|---|
| **Input** | the key in `~/.config/asu-rc/llm_api_key` (mode 600); `GET /v1/models` |
| **Transformation** | [`tools/voyager_models.py`](../../../phase4/code/tools/voyager_models.py) `list`, then `probe`: about 14 small requests per text model, with neutral prompts only (a sentence about a river; `def add(a, b):`) |
| **Output** | [`configs/voyager/models_2026-10-22.md`](../../../phase4/code/configs/voyager/models_2026-10-22.md) and [`probe_2026-10-22.md`](../../../phase4/code/configs/voyager/probe_2026-10-22.md), with their JSON |
| **Validation** | 52 models listed, 39 text models; 42 probed (families split into instruct and thinking members); **37 serve Arm A, 38 serve Arm B**; the key is in no output file (a test checks it) |

**What the probe found** (all of it on the river sentence, sent one request at a time to a quiet
server):

- the API returns every prompt token's id and log-probability with special tokens off: the exact
  input of Phase 3.3's scorer;
- the same request twice gave the same margin, bit for bit;
- 33 of the 36 models later registered gave margins that were whole multiples of 1/8, 1/16 or
  1/32 nat: rounded (bf16) scores. beam-1-0, deepseek-v4-1-flash and muse-spark-open did not round.

The run showed that the second point holds only on a quiet server (§11).

---

## 2. Registry, scorer and plumbing

| | |
|---|---|
| **Input** | the probe's tables |
| **Transformation** | 36 models registered as `asu-rc/<name>` (`serving="api"`, `gpus=0`, `pair=None`); [`p4/scoring/api.py`](../../../phase4/code/p4/scoring/api.py) (`APIScorer`, `TokenScorer`'s interface); [`p4/runtime/asu_api.py`](../../../phase4/code/p4/runtime/asu_api.py) (the key and one request); `prefetch` pins served models; `preflight` checks them; `run.py` routes them; `h5._is_instruct` leaves out instruct models without a base twin |
| **Output** | commit `5fe5d05a` (2026-10-22) and later commits (§13) |
| **Validation** | the test suite: 240 passed, 0 failed, 0 blocked (after the run, with every change below); `tools/compare_with_phase3_3.py --real-dev`: both pipelines still give identical CSVs (36 of 36 on the fake-scorer experiment, 19 of 19 on Phase 3.3's real development run); `tools/verify_copy.py`: 0 problems |

---

## 3. The configuration

| | |
|---|---|
| **Input** | Phase 3.3's held-out config, [`configs/phase3_3/heldout.json`](../../../phase4/code/configs/phase3_3/heldout.json) |
| **Transformation** | the same file with the nine served models in place of the 21 local ones |
| **Output** | [`configs/dev_api.json`](../../../phase4/code/configs/dev_api.json): `dom` and `blk` × `d25s3`, `d50s3`, `d75s1a`, `d75s2a`, `d75s3a`; every site (`site_limit` 0); the ladder 0–32 on 400 sites; three paraphrases; Arm B on every template; B = 2000; the same seeds |
| **Validation** | config hash `c786cd79962f…`; `test_phase4s_configs_only_touch_cells_their_stage_allows` |

**Why these cells.** They are exactly the cells of Phase 3.3's held-out run. So every served
model meets the same 3,030 sites, with the same prompts, as Phase 3.3's 21 models. The only
thing that changes is the model: the comparison is cell for cell.

---

## 4. Pins: which deployment answered

| | |
|---|---|
| **Input** | `run.py prefetch --config configs/dev_api.json` |
| **Transformation** | `prefetch.pin_served`: one request per model (a reference text), recording the model the gateway ran and its `system_fingerprint`. Nothing is downloaded |
| **Output** | `phase4/results/model_pins.json` |
| **Validation** | `failed: {}`; the key is not in the file |

```
asu-rc/olmo3-7b-instruct            olmo3-7b-instruct@vllm-0.26.0-9c8d2749                                 api-4d65007203f3c81b
asu-rc/olmo3-32b-instruct           olmo3-32b-instruct@vllm-0.26.0-e58ad632                                api-4d65007203f3c81b
asu-rc/olmo3-32b-think              olmo3-32b-think@vllm-0.26.0-c1dad0c2                                   api-4d65007203f3c81b
asu-rc/qwen3-coder-30b-a3b-instruct qwen3-coder-30b-a3b-instruct@vllm-0.26.0-9d422224                      api-40c4f55acb581b43
asu-rc/gemma4-31b-it                gemma4-31b-it@vllm-0.26.0-tp4-0e321782                                 api-8d6e58ef2e8bdb6c
asu-rc/deepseek-v4-1-flash          deepseek-v4-1-flash@vllm-0.28.1rc1.dev944+gced6857af-tp8-ep-d26393b7   api-1f62b89657270241
asu-rc/qwen35-27b                   qwen35-27b-fp8@vllm-0.26.0-5c5b7be4                                    api-2bef010c1e74ec28
asu-rc/qwen35-122b-a10b             qwen35-122b-a10b-fp8@vllm-0.26.0-tp4-ep-39012ab1                       api-2bef010c1e74ec28
asu-rc/qwen35-397b-a17b             qwen35-397b-a17b-fp8@vllm-0.28.1rc1.dev944+gced6857af-tp8-ep-448245c1  api-2bef010c1e74ec28
```

Read a line as: *the registry name*, *the deployment that answered* (served name @ server
build and hash), *the fingerprint of its tokenizer*. Three facts are visible here:

- the Qwen3.5 models are served as their `-fp8` variants;
- the three OLMo 3 models share one tokenizer, as do the three Qwen3.5 models: five tokenizers
  for nine models;
- two deployments run a newer server build (vLLM 0.28.1rc1) than the rest (0.26.0).

---

## 5. Smoke test (`smoke-20261023a`, 1 min 57 s)

| | |
|---|---|
| **Input** | [`configs/smoke_api.json`](../../../phase4/code/configs/smoke_api.json): OLMo 3 7B Instruct on `dom` × `d50s1`, 12 Arm A sites, 6 ladder sites |
| **Transformation** | `run.py smoke`: preflight, Arm A, the ladder, merge, fertility, export |
| **Output** | `phase4/results/smoke-20261023a/`: 36 Arm A rows (12 per condition), 48 ladder rows, 19 CSVs, 24 plot files, 10 reports |
| **Validation** | every row `status: ok`, `fp32_head: false`, `model_revision: olmo3-7b-instruct@vllm-0.26.0-9c8d2749`, `schema_version: p4/1`, `split: DEVELOPMENT` |

---

## 6. Init and preflight

| | |
|---|---|
| **Input** | `run.py dev init --config configs/dev_api.json --run dev-20261023a` |
| **Transformation** | the split checks every cell before anything is listed; preflight checks each served model's deployment against its pin (one request each) and skips the GPU checks |
| **Output** | `phase4/results/dev-20261023a/manifests/` (run config, preflight report) |
| **Validation** | `split_permission: 90 cells allowed for stage dev: ['DEVELOPMENT']`; nine `[PASS] model:` lines, `served … pinned …` identical |

---

## 7. The first launch, and why it stalled (12:12–12:20)

| | |
|---|---|
| **Input** | [`tools/run_api_local.sh`](../../../phase4/code/tools/run_api_local.sh): one process per model, each running Arm A → ladder → Arm B; fertility alongside |
| **Transformation** | two cells at a time per model, three requests per pair: **54 requests in flight**, each on a new TLS connection |
| **Output** | after 5 minutes, finished cells for one model only (Qwen3-Coder) |
| **Validation** | failed: 8 of 9 processes read **0 bytes in 20 s** (`/proc/<pid>/io`) |

**The evidence.** A stuck process had 26 threads waiting on locks and 3 waiting on sockets. One of
those sockets, to the API's address (a private campus address, port 443):

```
ESTAB 0 2171 … timer:(on,10sec,10) rto:120000 backoff:10 cwnd:1 bytes_sent:6894 bytes_retrans:4206
      bytes_acked:518 lastrcv:357653 unacked:3 retrans:1/11 lost:3 pmtu:1390 mss:1268
```

The request's packets were lost and resent 11 times, with the wait doubling each time up to two
minutes, and no answer for 357 seconds. A single test request sent at the same moment answered
in 0.23 s. So the service was fine, but the laptop's path to it was dropping packets under 54
concurrent new connections. (The API's address is private: it is reached through the campus
network or the VPN.)

**Stopped** at about 12:20: SIGTERM, then SIGKILL after 20 s for the processes stuck in a network
wait. Two driver loops went on to their next experiment and were stopped at 12:22. Finished cells
are atomic files, so nothing was lost or half-written. Kept: 15 Arm A cells (Qwen3-Coder 8,
OLMo 3 7B 3, Qwen3.5 27B 2, Qwen3.5 122B 2) and 6 ladder cells (Qwen3.5 27B 3, Gemma 4 3, from
those two loops). One failure marker (DeepSeek, `HTTP 500: Internal server error`) was left to
be redone.

---

## 8. The fix, and the relaunch (12:25:41)

| | |
|---|---|
| **Input** | the stall of §7 |
| **Transformation** | [`asu_api.py`](../../../phase4/code/p4/runtime/asu_api.py): each thread keeps **one connection and reuses it**; a request gives up after 150 s (`$P4_API_TIMEOUT`) and is retried on a fresh connection; 500 and 502–504 are retried with backoff (5, 10, 20 … s, at most 120); 429 waits 60 s; each retry is noted on stderr, never with the key. `APIScorer.cell_workers` default 1: **27 requests in flight** for nine models |
| **Output** | `logs/local_driver_2.log`; preflight PASS again for all nine |
| **Validation** | two minutes later every process was reading 0.8–9.7 MiB per 30 s; `test_the_real_client_retries_a_server_error_and_a_stall_on_a_fresh_connection` |

**Retries over the whole run**, counted in the logs (`logs/local_*.log`, from the relaunch on):

| the request got | retries | DeepSeek's | what it means |
|---|---:|---:|---|
| no answer (`RemoteDisconnected`) | 1,100 | 981 | a reused connection that the server had already closed |
| `HTTP 503` | 147 | 140 | the deployment was busy |
| `HTTP 500` | 46 | 45 | a server error |
| no answer (`TimeoutError`) | 1 | 1 | nothing within 150 s |
| **all** | **1,294** | **1,167** | |

They were 1,294 retries of 1,156 requests: 1,156 needed a second attempt, 69 a third and a
fourth, none a fifth (8 are allowed). So every retried request succeeded, and no cell failed
after the fix. The other eight models had 10–44 retries each, 117 of their 121 `RemoteDisconnected`
(each costs a 5-second wait and nothing else). DeepSeek-V4.1-Flash had
1,167, and 185 of its retries were the server's own errors (503, 500): its deployment was the
busiest. `local_driver_2.log` ends `driver exit=1` because the processes stopped for §9's changes
returned non-zero; their work was finished by the restarted processes.

---

## 9. The slow ones: DeepSeek and Arm B

| | |
|---|---|
| **Input** | the rates after the relaunch: DeepSeek-V4.1-Flash made 2 Arm A cells in 7 minutes (12:26–12:33), one cell at a time; Arm B makes one generation at a time per cell, and Qwen3.5 122B made 2 Arm B cells per 10 minutes |
| **Transformation** | • 12:33: DeepSeek's process alone restarted with `P4_API_CELL_WORKERS=2` (6 requests in flight, within the gateway's advice of 4–8 per model); log `local_task_5b.log`.<br>• 14:27: Qwen3.5 122B's Arm B restarted with 4 cells side by side (`local_task_7_cont.log`); Qwen3.5 397B's Arm B queued with 4 (`local_task_8_cont.log`); DeepSeek's ladder queued with 2 and its Arm B with 4 (`local_task_5_cont.log`).<br>• 15:28: DeepSeek's ladder restarted with 3 cells (9 requests in flight). |
| **Output** | DeepSeek's Arm A at 10 cells per 10 minutes (the others: 16–80); the last cell of the run at 18:08:22 |
| **Validation** | the rows of two cells side by side equal the rows of one at a time (`test_a_served_model_runs_through_arm_a_and_arm_b`); every restart resumed from the finished cells (0 missing and 0 duplicates at the merge, §13) |

**Time per model**, from the job manifests: the job that completed each experiment, in minutes
(162 Arm A cells, 40 ladder cells and 20 Arm B cells per model; a few were finished by an earlier
job that was stopped: the first launch, §7, or one of the restarts above).

| model | Arm A | ladder | Arm B | last cell |
|---|---:|---:|---:|---|
| OLMo 3 7B Instruct | 19.9 | 16.9 | 6.5 | 13:10 |
| OLMo 3 32B Instruct | 32.5 | 22.6 | 25.9 | 13:48 |
| OLMo 3 32B Think | 46.5 | 28.9 | 54.7 | 14:37 |
| Qwen3-Coder 30B-A3B Instruct | 43.8 | 60.5 | 36.6 | 14:48 |
| Qwen3.5 27B | 38.5 | 24.6 | 54.5 | 14:25 |
| Qwen3.5 122B-A10B | 62.4 | 33.6 | 30.8 (4 cells; 23.7 before, with 1) | 14:58 |
| Qwen3.5 397B-A17B | 99.0 | 51.3 | 41.5 (4 cells) | 15:39 |
| Gemma 4 31B | 36.0 | 29.5 | 62.4 | 14:35 |
| DeepSeek-V4.1-Flash | 160.5 (2 cells; 6.7 before, with 1) | 131.3 (3 cells; 13.1 before, with 2) | 27.7 (4 cells) | 18:08 |

From the relaunch, a model took 45 minutes (OLMo 3 7B Instruct) to 5 h 43 min
(DeepSeek-V4.1-Flash). The other eight were finished by 15:39.

---

## 10. One site through the API

The first Arm A site of OLMo 3 7B Instruct: `blk:d25s3:t000:T_CLASS_SIGIL:0`, correct `#`,
familiar `.`, with the token table. The prompt is 1,532 characters and ends `… above.\n\n$S '`.
`score_pair_detailed` sends three requests at once (the prompt is shown by its end):

```
{"prompt": "<1532 chars, ends \"above.\n\n$S '\">", "max_tokens": 1, "temperature": 0,
 "return_token_ids": true, "add_special_tokens": false}                          -> 301 token ids
{"prompt": "<1533 chars, ends \"bove.\n\n$S '#\">", …, "prompt_logprobs": 0}       -> 301 ids;
   last two: [50 "S", -0.1035], [5999 " '#", -17.0033]
{"prompt": "<1533 chars, ends \"bove.\n\n$S '.\">", …, "prompt_logprobs": 0}       -> 301 ids;
   last two: [50 "S", -0.1035], [6389 " '.", -15.5814]
```

| step | value |
|---|---|
| the two token lists first differ at | index 300 (`k_common` = 300) |
| the correct side, scored from there | one token, `" '#"`, log-probability −17.0033 |
| the familiar side | one token, `" '."`, −15.5814 |
| margin M = −17.0033 − (−15.5814) | **−1.4219**: the familiar spelling wins, a reversion |
| `merged` | true: the prefix alone is also 301 tokens, so the candidate joined the token `" '"` |

This is defect P32-001's merge, `('` + `#` → one token, measured from the first divergent
token exactly as Phase 3.3 measures it.

**The same site in the run's data** (its cell was written at 12:19:21, during the first launch, under the heaviest load): log-probabilities −17.0430
and −15.5814, M = −1.4616. The correct side's log-probability moved by 0.04 between the two
requests, on the same pinned deployment. §11 measures how often that happens.

---

## 11. Re-scoring a sample

| | |
|---|---|
| **Input** | the merged Arm A rows; 300 sites of the `rule` condition per model (2,700 in all), drawn with seed 20261023 (`random.Random("20261023/<model>")`) |
| **Transformation** | [`tools/retest_api.py`](../../../phase4/code/tools/retest_api.py): each site rebuilt by the pipeline and scored again by the same pinned deployment; the nine models side by side, 18:29:47–18:38:34, five to six hours after the run scored the same sites |
| **Output** | `analysis_addenda/retest/retest_2026-10-24.csv` (named by the UTC date), `SUMMARY.md` |
| **Validation** | 2,700 rows, none refused; the `revision` column equals the pin in all 2,700; the figure script checks that each row's run margin is the run's exported margin |

`SUMMARY.md`:

```
| model                               | sites | same to the bit | median abs. change | 95th pct | max     | sign changed | of those within 0.1 nat |
| asu-rc/olmo3-7b-instruct            | 300   | 150             | 0.0000             | 0.3745   | 0.8125  | 1            | 1 |
| asu-rc/olmo3-32b-instruct           | 300   | 293             | 0.0000             | 0.0000   | 0.4484  | 0            | 0 |
| asu-rc/olmo3-32b-think              | 300   | 299             | 0.0000             | 0.0000   | 0.0166  | 0            | 0 |
| asu-rc/qwen3-coder-30b-a3b-instruct | 300   | 300             | 0.0000             | 0.0000   | 0.0000  | 0            | 0 |
| asu-rc/gemma4-31b-it                | 300   | 140             | 0.1145             | 3.7544   | 10.6886 | 14           | 0 |
| asu-rc/deepseek-v4-1-flash          | 300   | 264             | 0.0000             | 0.1982   | 0.6848  | 4            | 1 |
| asu-rc/qwen35-27b                   | 300   | 288             | 0.0000             | 0.0000   | 0.6250  | 0            | 0 |
| asu-rc/qwen35-122b-a10b             | 300   | 27              | 0.2028             | 0.7387   | 1.2445  | 20           | 7 |
| asu-rc/qwen35-397b-a17b             | 300   | 300             | 0.0000             | 0.0000   | 0.0000  | 0            | 0 |
```

What it means is in [00 §8](00_complete_results.md#8-precision-rounding-and-batching) and
[02 §5](02_mathematics_and_statistics.md#5-the-re-test-batching-noise-in-numbers).

---

## 12. Fertility (finished 12:59)

| | |
|---|---|
| **Input** | the nine pinned deployments |
| **Transformation** | `run.py dev fertility`: the 80 templates in every lexicon, counted by each distinct served tokenizer (one request per text) |
| **Output** | `manifests/fertility.json`: 60 rows, **5 tokenizers** |
| **Validation** | the tokenizer groups match the pins: OLMo 3 ×3, Qwen3.5 ×3, Qwen3-Coder, Gemma 4, DeepSeek |

---

## 13. Merge, export and validate

| | |
|---|---|
| **Input** | 1,998 cell files in `raw/shards/`, each with a done-file (row count and SHA-256) in `checkpoints/` |
| **Transformation** | the plain-language report's rule-effect sentence corrected first ([08 §3](08_issues_and_superseded_numbers.md#3-fixed-in-the-code-during-this-work)); then `run.py dev analyze` (merge each experiment, export the 19 CSVs, the plots and the reports) and `run.py validate`; 18:08:42–18:27:45 |
| **Output** | `merged/arm_a.jsonl` (81,810 rows), `primary.jsonl` (36,000), `armb.jsonl` (7,020); `csv/` (19 files), `plots/` (24), `reports/` (10) |
| **Validation** | below: every cell present, every hash right, no duplicate |

```
merge arm_a    COMPLETE  rows= 81810 done=1458/1458 missing=0 failed=0 corrupt=0 dup_dropped=0
merge primary  COMPLETE  rows= 36000 done=360/360 missing=0 failed=0 corrupt=0 dup_dropped=0
merge armb     COMPLETE  rows=  7020 done=180/180 missing=0 failed=0 corrupt=0 dup_dropped=0
VALID: every expected cell is done and verified
```

Every row of the three merged files has `status: ok`, `split: DEVELOPMENT` and `schema_version:
p4/1`; Arm A and ladder rows have `fp32_head: false`.

**Which code scored the run.** The job manifests record commit `c173cf4a` with `git_dirty: true`:
the client fix (§8) and the side-by-side runner (§9) were committed only with these documents.
The manifests' `source_hashes` (57 files) equal the committed files, in the first scoring job
after the relaunch and in the last, except `p4/reporting/reports.py`, which was corrected after
the last scoring job (18:08:22) and before the export (18:08:42). The manifests' `dtype:
bfloat16`, `lm_head_fp32: true` and `gpu` fields describe the config and the laptop, not the
served models: the rows' `dtype` (the served precision, or `served` where the listing gives none)
and `fp32_head: false`, with `model_pins.json`, are the record of what was measured.

**Stored gzipped.** `merged/arm_a.jsonl` (105.9 MiB) is over GitHub's 100 MB limit, so the
repository holds `arm_a.jsonl.gz`, with both files' SHA-256 in `LARGE_FILES.sha256`;
`phase4/results/restore_large_files.sh dev-20261023a` restores and checks it, as for Phase 3.3.

---

## 14. The figures

| | |
|---|---|
| **Input** | Phase 4's `csv/` and the re-test rows; Phase 3.3's held-out `csv/` ([`phase3_3/sol_results/heldout-20261007a`](../../../phase3_3/sol_results/heldout-20261007a/)), its ten instruct models |
| **Transformation** | [`tools/paper_figures_api.py`](../../../phase4/code/tools/paper_figures_api.py): every plotted number recomputed from the site rows, with Phase 3.3's bootstrap streams (B = 2000, seed 20261002), then checked against both runs' exports; it refuses on any mismatch |
| **Output** | `analysis_addenda/paper_figures/`: 7 figures (PDF, SVG and 300-dpi PNG, 6.5 in wide), `ALL_FIGURES.pdf`, 8 tables (CSV and Markdown) in `tables/`, `CAPTIONS.md`, `PROVENANCE.md`; 17 s (18:38:34–18:38:51) |
| **Validation** | the checks, from the log: |

```
check: both runs scored the same 1515 dom and 1515 blk sites, on 80 and 80 templates and the lexicons d25s3, d50s3, d75s1a, d75s2a, d75s3a
check: Phase 3.3: the per-lexicon mean rule effect equals the export in all 200 model x grammar x lexicon x control cells, and the reversion counts and rates in all 400 model x grammar x lexicon x role cells
check: Phase 4: the per-lexicon mean rule effect equals the export in all 180 model x grammar x lexicon x control cells, and the reversion counts and rates in all 360 model x grammar x lexicon x role cells
check: Kaplan-Meier medians recomputed from the site rows equal each run's export in all 38 model x grammar groups
check: Arm B site, reach, reversion, correct-program and parse-failure counts equal each run's hurdle table for all 38 model x grammar groups
check: every one of the 2700 re-scored sites' 'run' margins is the run's exported margin
```

Every PNG was looked at before the run's figures were accepted. That caught overlapping axis
labels, a legend cut off, a dashed line that read as a marker, and a re-scoring axis too short
for Gemma 4's largest change (10.7 nats); each was fixed in the script and the figures drawn
again (the last time after the run, with the same checks passing).

---

## 15. Reproducing any number

```bash
cd ~/Desktop/projects/Lab/threejs.editor/threejs.editor.enhanced
export P4_RESULTS_ROOT=$PWD/phase4/results
run/.venv/bin/python phase4/code/run.py validate --run dev-20261023a        # every cell done and verified
run/.venv/bin/python phase4/code/run.py export --run dev-20261023a          # the 19 CSVs, plots, reports again
run/.venv/bin/python phase4/code/tools/paper_figures_api.py --run dev-20261023a
```

Re-scoring needs the key and the same deployments: a deployment that has changed is refused
(`ServedModelChanged`), by design.
