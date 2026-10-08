# AUDIT.md — the Phase 3.3 Sol pipeline

The audit was done on 2026-10-05, before any change. Every defect claim in the brief was
**verified by computation or by reading the code**, not taken on trust.

- Where the brief was wrong or incomplete: [`PROMPT_REVIEW.md`](PROMPT_REVIEW.md).
- The plain explanation of every defect: [`sol_experiment_explained/08`](sol_experiment_explained/08_changes_defects_and_superseded_numbers.md).

---

## 1. Starting state

| Item | Value |
|---|---|
| `git status --short` | empty (clean) at the start of this work, checked in the session record; last commit `699dfdb phase3/3_2/3_3` |
| Phase 3 tests | 54 passed, 0 failed |
| Phase 3.2 tests | 36 passed, 0 failed |
| local project venv | lark 1.3.1, numpy 2.5.2, matplotlib 3.11.2, torch 2.14.0+cu130, transformers 5.16.1, huggingface_hub 1.29.0. **No scipy, pandas or statsmodels** |
| system python3 | lark only |
| output schema | one JSON per run, with aggregates and `rows` (Arm A) or `paraphrase` + `extinction` (primary); no per-row provenance beyond the model id |

## 2. Defects

### 2.1 The brief's ten stop-ship claims (all verified true)

| # | Claim | Verification | Verdict |
|---|---|---|---|
| 1 | runners reuse the first lexicon's rule table and examples | `run_arm_a.py:140 lex0 = P.load_candidate(args.lexicons[0])`; `run_primary.py:93` the same | **TRUE** (P33-006) |
| 2a | `assert_balanced` checks only families; `empty_cells` always empty | `sampling.py:94 "empty_cells": []` is hard-coded | **TRUE** (P33-004) |
| 2b | de-duplication depends on CLI order | reversing the 4 development lexicons moved retained sites: `d25s1` 220 → 150, `d50s1` 204 → 174, `d50s2` 172 → 272 | **TRUE** (P33-003) |
| 2c | the pool can omit `dom/d25s2/sigil` and still pass | true, but that cell is **structurally empty** (`d25s2` never remaps a sigil). Expected cells must come from the materials, not a full grid | **TRUE, needs correction** |
| 3 | 82/120 extinction sites had their target in the demonstration pool | pool = t000–t031; 82 of the 120 sampled sites come from those templates | **TRUE, exactly 82/120** (P33-008) |
| 4 | `k*` and censoring are wrong | 84 of 125 already-correct sites got `k* = None`; 41 got a later re-crossing; 16 curves had **both** a `k*` and `censored = True`. Also **237/240 curves non-monotone** (not in the brief) | **TRUE, and worse** (P33-007) |
| 5 | the bootstrap loses a duplicate cluster's weight | hand example: tA drawn twice + tB once returned **2.000**; the correct answer is **5/3** | **TRUE** (P33-005) |
| 6 | fertility computed only from `args.models[0]` | `run_arm_a.py:124` | **TRUE** (P33-009) |
| 7 | `phase3.linter.score_site` reaches the old zero-returning scorer | `linter.py:91` → `HFModel.sequence_logprob` → `models.py:193 return 0.0` | **TRUE** (P33-001) |
| 8 | `runmeta` not wired into the runners | `grep runmeta scripts/*.py` → no runner imports it | **TRUE** (P33-010) |
| 9 | one big JSON written at job end | `run_arm_a.py:237`, `run_primary.py:168` | **TRUE** (P33-010) |
| 10 | `blk` already inspected | `blk × d50s1` was scored in Phase 3.2's balanced run (272 sites) and Phase 3.3's primary run (60 sites). PREREGISTRATION §8 itself reports `blk ≈ dom` | **TRUE** (deviation D1) |

### 2.2 Found during the audit (not in the brief)

| ID | Defect | Evidence |
|---|---|---|
| P33-001 (part) | the first P32-001 fix still returned `0.0` for ONE side when one candidate's tokens are a strict prefix of the other's | `margins._score_from: if k >= len(ids): return 0.0` |
| P33-002 | bf16 logits are quantised, and the margin's SIGN is the outcome | native bf16 margins `+0.6250` (10/16) and `−4.4375` (−71/16); fp32-head `+0.6473` and `−4.4436` |
| — | Qwen2.5-Coder-3B observed before the freeze | `arm_a_sizes.json` (dom only, no-table prompt) → D2 |
| — | `snapshot_download(local_files_only=True)` rejects a transformers-populated cache as "incomplete" without `allow_patterns` | verified on the local 0.5B cache |
| — | `TRANSFORMERS_CACHE` is ignored by transformers 5.x | 0 references in the installed 5.16.1 |
| — | the identity baseline is constant on the SEMANTIC-only eligible set, so its AUROC is exactly 0.5 | by construction → D6 |
| — | the pre-freeze rule-effect intervals were too narrow | recomputed: **all four** now include zero; one had excluded it → ERRATA E2, D4 |

### 2.3 Found in the final verification pass

These were found by re-reading the operational path and **rehearsing the runbook**
end to end (§6). The unit tests did not find them.

| ID | Defect | How it was confirmed | Guard |
|---|---|---|---|
| P33-011 | the Phase 3.2 tests rewrote 9 tracked lexicon files with a fresh `generated` timestamp on every run, changing their sha256. A mid-run `cpu_tests` would have failed every later GPU job's materials check | the `git diff` of the 9 files was timestamp-only; traced to `test_phase3_2.py:33,210` → `deltafam.write` | `test_materials_writer_is_idempotent_and_atomic`; the 9 files stayed byte-identical through every later suite and the simulated `cpu_tests` job |
| P33-012 | the array stride came from `SLURM_ARRAY_TASK_COUNT`, so a single-index resubmission selected no model. Arm B / H5 also indexed the filtered list | read and reproduced in a test | `test_array_task_i_scores_model_i_even_when_resubmitted_alone`; rehearsal: a single-index resume after a real SIGUSR1 → COMPLETE |
| P33-013 | a hardware-BLOCKED test made the runner exit non-zero, so `set -e` stopped `cpu_tests` after the first of three suites. The exit status was a count, which wraps at 256 | CPU-node simulation | the `cpu_tests.slurm` simulation: all three suites run, job exit 0 |
| P33-014 | fixed `.tmp` / `.tmp.<pid>` names; `clean_temp` deleted any temp file, including another task's write in flight | the old scheme failed **5 of 5** threaded trials (`FileNotFoundError`) | `test_concurrent_writers_never_share_a_temp_file`, `test_abandoned_temp_file_is_not_a_shard` |
| P33-015 | source compared with the freeze only at unlock; materials and model pins never compared | read | `test_heldout_access_refuses_if_source_changes_after_unlock`, `test_a_model_repinned_after_the_freeze_is_refused` |
| P33-016 | `--export=ALL` could carry `P33_FAKE=1` into a real job | read | `test_test_mode_cannot_leak_into_a_real_job`; the `submit.sh` simulation showed `P33_FAKE` unset |
| P33-017 | `status` created `raw/shards/armb`, so `validate` and `dev_freeze` refused a complete development run | **reproduced** on a copy of the rehearsal's development run: VALID → `status` → `INCOMPLETE: {'armb': 'EMPTY'}`, exit 3 | `test_status_is_read_only_so_validate_still_passes` (real CLI); the final rehearsal calls `status` where the README does |
| P33-018 | prefetch re-pinned every model to the Hub's current commit | read | `test_prefetch_keeps_existing_pins_unless_repin` (fake Hub API) |

**Smaller fixes from the same pass:**

- reversion rows labelled `condition = rule`;
- the stage-group refusal now exits 2, not 1;
- the smoke computes real-tokenizer fertility;
- `prefetch --config` is the default (the `mid`/`large` tiers hold forbidden 7B+ models);
- the H5 job runs preflight;
- smoke runs map to the `dev` group in the H5 and final-export jobs;
- the dead `primary.demo_pool` field is removed;
- the appended deviation note cited a non-existent test file.

---

## 3. Requirement → implementation → tests → artifacts

| Requirement | Implementation | Tests | Artifact |
|---|---|---|---|
| per-lexicon prompts, verified per site | `phase3_2/prompts.py` `bundle`, `assert_prompt_matches` | `test_old_behaviour_first_lexicon_table_is_rejected`, `…_coincides`, `…_two_lexicon_run` | `prompt_sha` per row; prompt hashes per job manifest |
| expected-cell validation | `sampling.available_cells`, `structural_grid`, `assert_balanced(expected=)` | `test_missing_cell_is_refused`, `test_structurally_empty_cell_is_reported_not_failed` | `split_exclusion_audit.csv` |
| order-independent selection | `sampling.dedupe_within_cells`, `canonical_key`, `balanced` | `test_selection_is_identical_under_every_lexicon_order`, `test_old_global_dedup_was_order_dependent` | `site_inventory.csv`; drops in the audit CSV |
| leakage-free demonstrations, recorded | `p33/demos.py` | `test_demonstrations_never_contain_the_target`, `test_old_first_32_pool_leaked_the_target`, `test_ladder_is_nested_and_hashed`, e2e leak test | `demo_ids`, `demo_set_sha`, `demo_order_sha`, `demo_seed` per rung |
| corrected k* + KM | `p33/kstar.py` | 8 k* tests | `kstar_survival.csv`, `extinction_trajectories_km.*` |
| bootstrap multiplicity, Holm, ≥ 8 clusters | `phase3_2/analysis.py` | hand example 5/3, old-behaviour regression, `<8` refusal, Holm hand example | every CI column |
| tokenizer-specific fertility | `p33/fertility.py` | `test_fertility_is_computed_per_distinct_tokenizer` | `fertility.csv` |
| one canonical scorer, no silent zero | `phase3_2/margins.py`; `phase3/models.py` raises | 4 scorer tests; fp32 head validated on real weights (§5) | `merged`, `k_common`, `first_div_*`, `tie`, `fp32_head` per row |
| provenance bound to every runner and shard | `p33/provenance.py`, shard markers | `test_provenance_is_bound_to_every_job_and_shard`, `test_every_row_carries_its_split_revision_and_prompt` | `manifests/job_*.json`, `job_provenance.csv` |
| crash safety + resume | `p33/shards.py`, `pipeline.run`, `config.atomic_write_text` | shard/resume tests incl. **resumed == uninterrupted byte-for-byte**, concurrency, single-index resume, read-only status | `checkpoints/`, `failed_cells.csv`, `run_completeness.csv` |
| development / held-out isolation, freeze, unlock | `p33/splits.py`, `p33/freeze.py`, CLI stage groups | 20 split/freeze tests incl. drift after unlock and re-pinned models; e2e freeze → refused → unlock → held-out | `DEV_FREEZE.json(+.sha256)`, `HELDOUT_UNLOCK.json` |
| Arm A | `pipeline.score_arm_a_cell` | e2e | `arm_a_long.csv`, `rule_effect.csv` |
| primary / extinction / paraphrase | `pipeline.score_primary_cell` | e2e | `extinction_rung_long.csv`, `kstar_survival.csv`, `paraphrase.csv` |
| H4 | `p33/h4.py` | metric hand values, calibration identity, C3 NOT TESTABLE, single-class handling, pairing | `h4_predictions.csv`, `h4_metrics_baselines_calibration.csv` |
| Arm B | `p33/armb.py` | NL rendering, extraction, 5 buckets, reach vs conditional | `arm_b_generations.csv`, `arm_b_hurdle.csv` |
| H5 | `p33/h5.py` | whole-corpus IR proof for every arm, a proof that can fail, I7, arm selection | `h5_budget_outcomes.csv`, `h5_ir_proof.csv` |
| H2 | `p33/h2.py` | NOT TESTABLE; machinery checked on synthetic cells | `h2_did.csv` |
| power | `p33/power.py` | held-out pilot refused, monotonicity, ICC hand example | `power.csv`, `POWER_ANALYSIS.md` |
| 19 CSVs / 12 plots / 10 reports | `p33/export.py`, `plots.py`, `reports.py` | e2e generation + metadata tests | `csv/`, `plots/` (PNG+SVG), `reports/` |
| preflight | `p33/preflight.py` | A100 check on a real GPU (hardware-BLOCKED on CPU nodes), scheduler mismatch | `manifests/preflight_*.json` |
| download-only prefetch, pins | `p33/prefetch.py`, `scorers.resolve_snapshot` | AST check (no model instantiated), `.bin` fallback, pins kept unless `--repin` | `model_pins.json` |
| environment + lock | `env/make_env.sh`, `requirements.in`, `activate.sh` | `bash -n` on every script | `requirements.lock.sol.txt` (written on Sol), `requirements.lock.laptop.txt` |
| 11 jobs + submit wrapper | `jobs/*.slurm`, `submit.sh` | `bash -n`; no `partition=general`; no `P33_FAKE` outside `cpu_tests`; `submit.sh` against a stand-in `sbatch`; `cpu_tests.slurm` against a stand-in `srun` | `results/<run>/logs/` |

## 4. Test results (exact; the 2026-10-05 code; for 2026-10-07 see §7.5)

| Suite | Interpreter / setting | Result |
|---|---|---|
| `phase3_2/sol/tests` | project venv, GPU visible | **112 passed, 0 failed, 0 blocked** (exit 0) |
| `phase3_2/sol/tests` | bare python3 (lark only) | **110 passed, 0 failed, 2 blocked** (matplotlib, torch absent): exit 5, reported and not counted as passes |
| `jobs/cpu_tests.slurm` | run as Slurm would on a CPU node: stand-in `srun`, `CUDA_VISIBLE_DEVICES=""`, `P33_FAKE` set by the job | Sol **111 passed + 1 blocked** (the A100 test, for want of a GPU); Phase 3.2 **36**; Phase 3 **54**; **job exit 0** |
| `phase3_2/tests` | python3 | **36 passed, 0 failed** |
| `phase3/tests` | python3 | **54 passed, 0 failed** |
| `submit.sh` × 11 jobs | stand-in `sbatch` | correct flags; arrays `0-3` / `0-10`; `P33_ARRAY=2` → `--array=2`; extra flags pass through; log directories created; `P33_FAKE` not exported |

The 9 tracked lexicon files are byte-identical before and after every suite (sha256 compared).

## 5. The one real-model run

Exactly one development smoke, on the laptop GPU (Sol is not reachable from here):

| | |
|---|---|
| model | Qwen2.5-Coder-0.5B @ `8123ea2e…`, offline |
| cell | `dom × d50s1`, 12 sites |
| A100 check | **waived and recorded** |
| preflight | every check passed |
| Arm A | 36/36 rows, 9/9 cells |
| primary | 48/48 rows, 8/8 cells |
| measurement health | 0 exact-zero margins, 0 ties, 6/36 merged-token sites |
| outputs | 19 CSVs, 24 plot files, 10 reports |

**After the smoke, on the same run,** with no model loaded and nothing re-scored (logged in
`logs/post_smoke_fertility_export.out`):

- tokenizer-only fertility was computed. Identity `dom` gives 0.366917 tokens/char, reproducing
  Phase 3.2; `d50s1` gives 0.394997;
- the export was regenerated twice from the saved rows with the final code.

The run's stored `run_config.json` still contains the since-removed, never-read
`demo_pool` field, and its preflight file predates the WARN/PASS split. Both are kept
as recorded.

**Scorer validation.** On three development sites of the same cell, the fp32 head
was compared with the model's native logits:

| | Values |
|---|---|
| per-candidate log P, absolute difference | 0.0051, 0.0243, 0.0422 |
| margin sign | identical at all three |
| margins, fp32 | +0.6473, −4.4436, −5.4815 |
| margins, native | +0.6250, −4.4375, −5.4763 |

This is reported as a correctness check, not a result.

**Other model-free uses of the cached tokenizer:**

- `prefetch --verify-only` (pins);
- the length of the longest rendered target program (73 tokens), used to check
  `max_new_tokens`.

**No held-out cell was enumerated, loaded or scored with a real model, and no
full sweep was submitted.** The only held-out scoring in this work used the
deterministic fake scorer, in the test suite and in the rehearsal.

## 6. The runbook rehearsal

The `p33.py` commands of README §5–§12 were run **in order**, as Slurm would run
them: `SLURM_ARRAY_TASK_ID` / `SLURM_ARRAY_TASK_COUNT` were set per emulated array task.
The setup used:

- the fake scorer, in a scratch results root;
- `configs/dev.json` and `configs/heldout.json` with small limits;
- all 4 development models and all 11 held-out models.

Final code, 22:25–23:29, **0 tracebacks**.

### Development run

| Step | Result |
|---|---|
| `dev init` → Arm A, tasks 0–3 | 288 rows, 48/48 cells |
| `status` (README §6) | `primary`, `armb`, `h5` → `not started`; nothing created |
| primary, tasks 0–3 (task 2 also resubmitted alone with `SLURM_ARRAY_TASK_COUNT=1`) | 480 rows, 64/64 cells |
| `status` (README §7) → `dev fertility` → `dev analyze` → `validate` | **VALID** |
| `validate` → `dev freeze` | **FROZEN** |
| second `dev freeze` | `REFUSED … a freeze is immutable` (exit 2) |

### Held-out run

| Step | Result |
|---|---|
| `heldout init` | done |
| `heldout run` before the unlock | `REFUSED: held-out cells are locked` (exit 2) |
| a `dev` command on the held-out run | `REFUSED … physically separated` (exit 2) |
| `heldout unlock --confirm "yes"` | `REFUSED: unlock requires the exact phrase` (exit 2) |
| `heldout unlock` with the phrase | **UNLOCKED** (source, materials and pins re-checked) |
| held-out Arm A + primary, tasks 0–10 | 1,320 rows (330/330) and 3,520 rows (440/440) |
| `status` | Arm B and H5 `not started` |
| Arm B, tasks 0–10 (base-model tasks are no-ops) | 100 rows (50/50) |
| H5, tasks 0–10 (each merges Arm A first, as `jobs/h5.slurm` does) | 1,400 rows (350/350) |
| `heldout fertility` → `heldout analyze` → `validate` | 19 CSVs, 24 plot files, 10 reports, **VALID** |

### Interruption, with real signals

**In the final rehearsal the targeted task finished in about 2 s, before its 12 s
signal arrived ("No such process"), so the interrupt was not exercised there.**
It was confirmed separately on the final code, with the signal sent only once 7
cells had been written:

| | Result |
|---|---|
| SIGUSR1 | exit **4**; manifest `INTERRUPTED \| signal 10` |
| the other tasks, then task 2 resubmitted alone | `COMPLETE` |
| merged output | **960 rows, byte-identical** to an uninterrupted run of the same configuration |

Earlier in the session:

- the previous full rehearsal (18:09–19:13) exercised the same path: exit 4, then a
  single-index resume → COMPLETE;
- a real SIGTERM sent to a running job recorded `INTERRUPTED | signal 15`.

### What the rehearsal did not cover

- Slurm itself; `submit.sh` was checked against a stand-in `sbatch` (§4);
- the network download in `prefetch`;
- any real model beyond the one development smoke;
- Sol's filesystems.

---

## 7. 2026-10-07 — analysis corrections on the real development run, and model scale

### 7.1 The run

`dev-20261006a` was downloaded to `phase3_3/sol_results/`.

**Contents:**

| | |
|---|---|
| Arm A | 192/192 cells, 10,224 rows |
| primary | 112/112 cells, 16,000 rows |
| models | 4 |
| hardware | A100-SXM4-80GB, bf16, fp32 head |

**What its job manifests record:**

- commit `8650df5`;
- source hashes identical to the local tree (0 differing files);
- materials identical;
- revisions `8123ea2e…` / `ea3f2471…` / `df3ce67c…` / `2e1fd397…`, all with tokenizer `cc349caf…`.

There is no `DEV_FREEZE.json` and no unlock.

### 7.2 Confirmed before changing anything

Every claim in the brief was reproduced from the saved files or measurements:

| Claim | Verified |
|---|---|
| risk AP 0.81887449 / 0.92397474 with 852 distinct scores | yes; invariant to row order |
| 1.5B identity AP 0.45232430, reversed 0.49245557, prevalence 0.46830986 | yes |
| P@10 identity 1.5B 0.4 → 0.6 reversed; token_count 0.5B 0.5 → 0.1 | yes |
| power.csv: 25 smallest-detectable rows, 5 distinct, all with the pilot ICC | yes |
| power report shows only ICC = 0 for the rule effect | yes (`x["icc"] in (rule[0]["icc"],)`) |
| RUN_SUMMARY says 0 report files | yes on Sol; a repeated export counted 10, and would count stale files too |

**Also found:**

- Tied scores also made the `length`, `program_nll` and exploratory `terminal_rate` baselines
  order-dependent.
- The plot footer showed one model and one revision for "base|instruct" rows. The first fix
  listed the models and the revisions as two separately sorted lists, which pairs them wrongly
  by position: 3 of the 4 development models. Footers now print each model with its own
  revision (`model@revision`), and `test_figure_footer_pairs_each_model_with_its_own_revision`
  guards it.
- `REPRODUCTION.md` named non-existent commands (`dev arm-a`) and a missing `env/README.md`.
- The test runner used `setdefault` for its results root, so under `sol.env` a CPU-test job
  writes `dev-status-readonly/` into the real results root and briefly swaps the real
  `model_pins.json` (then restores it). It did happen on Sol: `results/dev-status-readonly/`
  (fake 0.5B pair, `d50s1`, 24 sites) dates from 2026-10-06. It was moved to
  `results/_quarantine/` on 2026-10-07, and the pins file's development revisions match the
  job manifests.

**Baseline reproduction:** re-exporting with the ORIGINAL code locally reproduced 18 of Sol's 19
CSVs byte for byte. The nineteenth differed only in `cal_intercept`: −8.5e-17 against −7.9e-17,
floating-point noise.

### 7.3 Corrections and their evidence

The record is in `dev-20261006a/analysis_revisions/r1-2026-10-07-metric-corrections/`
(`ANALYSIS_REVISION.md`, `analysis_revision.json`, `before/`).

**Inputs.** All 652 measurement inputs are byte-identical before and after: raw shards,
checkpoints, merged JSONL and status files, manifests and logs.

**Validation:**

- `p33 status` reports 192/192 and 112/112 done, before and after.
- `p33 validate` on a scratch copy reports VALID, with the re-merge byte-identical.

**Outputs:**

- **17 of 19 CSVs are byte-identical.**
- **H4 table:** 23 cells changed, all baseline AP or P@k; 0 unexpected changes.
- **Power:** all 200 shared scenarios have unchanged values. The 25 smallest-detectable rows are
  now one per (T, ICC) scenario.
- **Figures:** they differ in metadata (date, matplotlib version) and, for the H4 and power
  figures, in content.

**Corrected values** (old → new):

| Pair | Predictor | AP | P@10 |
|---|---|---|---|
| 1.5B | identity | 0.452 → **0.468** (= prevalence) | 0.4 → 0.468 |
| 0.5B | identity | 0.410 → **0.407** (= prevalence) | 0.3 → 0.407 |
| 0.5B | token_count | 0.431 → 0.416 | 0.5 → 0.435 |
| 1.5B | token_count | 0.468 → 0.472 | 0.4 → 0.491 |
| 0.5B / 1.5B | risk | **unchanged** (0.818874 / 0.923975) | unchanged (1.0 / 1.0) |

AUROC, the C1/C2 deltas, their bootstrap intervals, the Holm p-values and the calibration are
all unchanged.

**Power, corrected:** at the pilot ICC the rule-effect power is 0.094 / 0.147 / **0.251** /
0.446 / 0.732 at 20 / 40 / 80 / 160* / 320* templates (* hypothetical). The ICC = 0 row
shows 0.994 at 80 templates and is the most optimistic one. For H4 criterion 1, the smallest
detectable AUROC at the pilot ICC is 0.62 at 80 templates.

### 7.4 Model scale (deviation D10)

| Change | Where |
|---|---|
| ceiling 3B → 72B | `splits.MAX_SIZE_B` |
| DeepSeek-Coder-33B and Qwen2.5-72B pairs | registry |
| `gpus` per checkpoint | registry |
| 10 checkpoints appended to `configs/heldout.json` | indices 0–10 unchanged |
| sharded 2-GPU loading | `TokenScorer._load_sharded`; the 1-GPU path is unchanged |
| per-task preflight with GPU count and memory checks | `preflight.py` |
| `p33.py array-indices` and the `*_2gpu` job profiles | `scripts/p33.py`, `submit.sh` |

**Tested without a GPU:**

- `submit.sh` against a stand-in `sbatch`;
- the array split (0–18 / 19,20);
- per-task preflight.

**Not tested:** the 2-GPU load itself, which needs two GPUs.

### 7.5 Tests

| Suite | Result |
|---|---|
| Sol-pipeline suite, local project venv | 139 passed |
| Sol-pipeline suite, local bare python | 135 passed + 4 blocked (dependencies) |
| Phase 3.2 | 36 |
| Phase 3 | 54 |
| simulated `cpu_tests.slurm` | Sol 138 + 1 hardware-blocked, 36, 54; exit 0; 0 files in the stand-in results root |

**New test modules:**

- `test_metric_and_report_corrections.py` (20);
- `test_model_scale.py` (6);
- plus a test that the runner never uses the real results root.

### 7.6 Execution on Sol (2026-10-07)

| Step | Evidence |
|---|---|
| pushed and pulled | commit `78b2bcd` on branch `sol-d9-d10`; Sol's checkout on that commit (only tracked `__pycache__` files and the untracked Sol lock file differ) |
| test artifact quarantined | `results/dev-status-readonly/` (fake rows, 2026-10-06) moved to `results/_quarantine/` |
| CPU tests (job 64939805) | Sol 138 passed + 1 hardware-blocked; Phase 3.2 36; Phase 3 54; exit 0; the results root untouched |
| D9 re-analysis on Sol | `r1-2026-10-07-metric-corrections`: 652 inputs byte-identical, all checks passed, digest `3c3e772c66ecf51e`. Against the local record, 18/19 CSVs are byte-identical; the 19th differs in one `cal_intercept` cell by 6e-18 |
| prefetch (job 64939806) | the 10 D10 checkpoints, 600.6 GiB, every file sha256-verified, 36 min; `model_pins.json`: 21 pins, no failures |
| freeze (job 64942745) | `DEV_FREEZE.json` sha256 `b319c3fc…`; 44 source hashes; 21 model pins; drift `[]` |
| unlock | `heldout-20261007a`, phrase entered at the investigator's direction (`UNLOCK_NOTE.md`) |
| held-out chain | jobs 64943130–64943136, one at a time (`logs/submission_chain.env`); first task's preflight OK (one informational WARN: materials recorded by the first job), 210 cells permitted |
