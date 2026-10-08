# 08 — Changes, defects, and superseded numbers

This is the ledger. Every defect is listed with the evidence that it was real,
what fixed it, and the test that keeps it fixed. Every number that changed is
listed with its old and new value. Where the evidence was gathered is in
[`../AUDIT.md`](../AUDIT.md). What the brief got right, wrong or missed is in
[`../PROMPT_REVIEW.md`](../PROMPT_REVIEW.md).

---

## 1. Defects

### The brief's ten stop-ship defects (all verified, all fixed)

| ID | Defect | Evidence it was real | Fix | Guard |
|---|---|---|---|---|
| P33-006 | runners showed `--lexicons[0]`'s rule table and examples to **every** site | `run_arm_a.py:140`, `run_primary.py:93` | per-site `prompts.bundle` + `assert_prompt_matches` | `test_old_behaviour_first_lexicon_table_is_rejected`, `…_two_lexicon_run` |
| P33-003 | de-duplication depended on CLI lexicon order | retained sites `d25s1` 220 → 150, `d50s1` 204 → 174, `d50s2` 172 → 272 when reversed | de-duplicate **within** (family, lexicon), canonical tie-break, every drop logged | `test_selection_is_identical_under_every_lexicon_order`, `test_old_global_dedup_was_order_dependent` |
| P33-004 | `assert_balanced` checked families only; `empty_cells` hard-coded `[]` | `sampling.py:94` | expected cells from the classified materials; STRUCTURALLY_EMPTY reported | `test_missing_cell_is_refused`, `test_structurally_empty_cell_is_reported_not_failed` |
| P33-008 | demonstrations = templates t000–t031 for every site | **82 of 120** Phase 3.3 extinction sites saw their own target | leak-free nested ladder (`demos.py`); a leak raises | `test_old_first_32_pool_leaked_the_target`, e2e leak test |
| P33-007 | `k*`: already-correct → None; later re-crossings; crossed + censored | 84 / 41 / 16 of 240 curves | exact definition, KM for two populations | 8 k\* tests |
| P33-005 | bootstrap lost a twice-drawn cluster's weight | hand example 2.000 vs 5/3 | `_draw` tags, pairs keyed on (`_draw`, `site_id`) | `test_bootstrap_keeps_duplicate_cluster_weight_hand_example` |
| P33-009 | fertility from `--models[0]` reported for every model | `run_arm_a.py:124` | per distinct tokenizer | `test_fertility_is_computed_per_distinct_tokenizer` |
| P33-001 | `phase3.linter.score_site` reached a scorer that returned 0.0; and the first P32-001 fix still returned 0.0 for **one side** | `models.py:193`, `margins._score_from` | `ZeroLengthSpan` / `IdenticalCandidates` / `NoContext`; `HFModel` raises | `test_check_pair_refuses_every_degenerate_case`, `test_old_phase3_scorer_now_raises_instead_of_returning_zero` |
| P33-010 | provenance never wired into runners; one JSON written at job end | no runner imported `runmeta`; `run_arm_a.py:237` | `JobManifest` + atomic shards + markers | `test_provenance_is_bound_to_every_job_and_shard`, `test_every_row_carries_its_split_revision_and_prompt` |
| (D1) | `blk` was inspected before the freeze | 272 + 60 sites scored; PREREGISTRATION §8 itself reports `blk ≈ dom` | relabelled EXPLORATORY / HELDOUT-WEAK-FAMILY; C3 NOT TESTABLE | `test_blk_is_never_labelled_a_heldout_grammar` |

### Found during the audit (not in the brief)

| ID | Defect | Evidence | Fix |
|---|---|---|---|
| P33-002 | bf16 margins are quantised; the outcome is a **sign** | native +0.6250 = 10/16, −4.4375 = −71/16 | fp32 output head, validated against native logits (same sign, 0.005–0.042 nats) |
| — | 237 of 240 curves non-monotone | Phase 3.3 primary output | `nonmonotone`, crossing counts, `sustained_k` |
| — | no-rule control about a third shorter than the rule prompt | 1,014 vs 1,527 characters | `norule_lenmatched` |
| — | Qwen 3B observed before the freeze | `arm_a_sizes.json` | HELDOUT-WEAKENED (D2) |
| — | identity baseline constant on the eligible set | by construction | stated as D6; exploratory `terminal_rate` baseline added |
| — | `TRANSFORMERS_CACHE` ignored by transformers 5.x; offline resolution needs the same `allow_patterns` | 0 references in 5.16.1; `IncompleteSnapshotError` | `HF_HUB_CACHE` + pinned patterns |

### Found in the final verification pass (after the code was "done")

These were found by re-reading the operational path and **rehearsing the
runbook**, not by the unit tests. That is why a rehearsal was worth an hour.
P33-017 was found only on the *second* rehearsal pass, by running the exact
commands the README tells you to run, including the harmless-looking `status`.

| ID | Defect | How it would have shown up on Sol | Fix | Guard |
|---|---|---|---|---|
| **P33-011** | the Phase 3.2 tests rewrote 9 tracked lexicon files with a fresh timestamp on every run, changing their sha256 | rerun `cpu_tests` mid-run, and every later GPU job fails preflight with "materials CHANGED". A scoring job reading a lexicon mid-rewrite could see a truncated file | `deltafam.write` idempotent (unchanged member left untouched) and atomic | `test_materials_writer_is_idempotent_and_atomic`; the 9 files stayed byte-identical through every suite |
| **P33-012** | the array stride came from `SLURM_ARRAY_TASK_COUNT`; resubmitting one index (`--array=2`) gave count 1, and `i % 1 == 2` selected **no model**. Arm B / H5 also indexed the *filtered* model list, contradicting the job comments | a "successful" resubmission that scored nothing | task *i* → model *i* of the full config; inapplicable models are no-ops; `P33_ARRAY` in `submit.sh` | `test_array_task_i_scores_model_i_even_when_resubmitted_alone`; rehearsed with a real single-index resume |
| **P33-013** | on a Sol CPU node the A100 test is BLOCKED → the runner exited non-zero → `set -e` aborted `cpu_tests` after the **first** suite. The exit status was also a count, which wraps to 0 at 256 | the Phase 3.2 and Phase 3 suites would never run on Sol | exit codes 0 / 1 / 5; `--cpu-node` lists hardware-only blocks without failing; the job runs all three suites and aggregates | CPU-node simulation: 1 hardware block → exit 0; a missing dependency → exit 5 |
| **P33-014** | fixed `.tmp` / `.tmp.<pid>` names; array tasks start together on different nodes that can share a pid. `clean_temp` deleted **any** temp file, including another task's write in flight | an interleaved plan or arms file; every later resume refused; spurious failed cells | `config.atomic_write_text` (mkstemp, fsync, replace) for every writer; `clean_temp` only removes temp files older than 15 min | `test_concurrent_writers_never_share_a_temp_file` (the old scheme failed **5 of 5** trials); `test_abandoned_temp_file_is_not_a_shard` |
| **P33-015** | source compared with the freeze **only at unlock**; materials and model pins never compared | held-out cells scored by code edited after the unlock, or by a re-pinned model, with no refusal | `frozen_drift` (source + materials + model pins), checked at unlock **and** on every held-out access | `test_heldout_access_refuses_if_source_changes_after_unlock`, `test_a_model_repinned_after_the_freeze_is_refused` |
| **P33-016** | `submit.sh` exports the caller's environment; a leftover `P33_FAKE=1` would make a GPU job score with the **fake** scorer under a real label (and the smoke skips preflight in fake mode) | fabricated numbers labelled as real | `sol.env` unsets `P33_FAKE`; only `cpu_tests` sets it, afterwards | `test_test_mode_cannot_leak_into_a_real_job` |
| **P33-017** | `p33 status`, a read-only command, built a `ShardStore` for every experiment, which **created** `raw/shards/armb`. "Started" is defined by that directory, so a never-run Arm B became a started, EMPTY experiment | following the README (`status` in §6–§7), `validate` reported `INCOMPLETE: {'armb': 'EMPTY'}` and `dev_freeze` exited 3 **without freezing**. Reproduced on a copy of the rehearsal's development run | `status` is read-only and prints `not started` | `test_status_is_read_only_so_validate_still_passes` drives the real CLI; the final rehearsal calls `status` where the README does |
| **P33-018** | `prefetch` resolved every model to the Hub's **current** commit and overwrote existing pins | re-running prefetch after the freeze (e.g. to add the Llama pair once access is granted) would re-pin any model the Hub had updated, and every held-out command would refuse on pin drift | already-pinned models keep their revision; `--repin` is explicit | `test_prefetch_keeps_existing_pins_unless_repin` (fake Hub API, no network) |

Smaller fixes from the same pass:

| Was | Now |
|---|---|
| reversion rows in `rule_effect.csv` had no `condition` column | labelled `rule` |
| a `dev` command on a held-out run exited 1 (crash code) | exits 2 (the documented refusal code) |
| the smoke never exercised the real tokenizer path of fertility | it computes fertility. For the laptop smoke this was run afterwards on the same run, tokenizer only |
| the default prefetch was the `small` tier | the 11 models the shipped configs use. The `mid` and `large` tiers contain 7B–32B models no stage may score |
| `h5.slurm` had no preflight; `h5` and `final_export` called a non-existent `smoke` group for smoke runs | preflight added; smoke maps to `dev` |
| the dead `primary.demo_pool: 48` | removed from the code and every config |
| the appended deviation note cited `sol/tests/test_prereg.py` | `test_prereg_env.py`. The frozen hash `a0146494…` is unchanged |

---

## 2. Superseded numbers

| Quantity | Was | Now | Status / where |
|---|---|---|---|
| extinction threshold `k*` | 4.96–6.94 shots, 8–18% censored | **withdrawn**; no valid estimate exists | ERRATA E1, D3 |
| rule effect, 0.5B base `dom` | +0.171 [+0.029, +0.326] | +0.171 **[−0.012, +0.370]** | ERRATA E2, D4 |
| rule effect, 0.5B base `blk` | +0.156 [−0.020, +0.344] | +0.156 [−0.068, +0.402] | E2 |
| rule effect, 0.5B instruct `dom` | +0.199 [−0.003, +0.414] | +0.199 [−0.054, +0.477] | E2 |
| rule effect, 0.5B instruct `blk` | +0.222 [−0.004, +0.465] | +0.222 [−0.064, +0.530] | E2 |
| "3 of 4 intervals include zero" | — | **all 4 include zero** | E2 |
| `blk` | "the held-out grammar family" | EXPLORATORY / HELDOUT-WEAK-FAMILY | E3, D1 |
| H4 criterion C3 | testable on `blk` | **NOT TESTABLE** | D1 |
| identity baseline | a competitor | constant: AUROC = 0.5; C1 means AUROC ≥ 0.60 | D6 |
| Qwen 3B | held-out model | HELDOUT-WEAKENED | D2 |
| development sites kept (CLI order) | `d25s1` 220, `d25s2` 86, `d50s1` 204, `d50s2` 172 (order-dependent) | 220, 88, 272, 272 = **852**, order-independent | P33-003 |
| leaking ladder sites | 82 / 120 (Phase 3.3) | 0 of 2,800 demonstration sets on the development plan (the old rule: 177 / 400) | P33-008 |
| Sol scripts | `arm_a.slurm`, `primary.slurm`, `prefetch_models.py` | superseded: `--partition=general` is rejected; the prefetcher instantiated models | E4, `legacy_superseded/WHY_SUPERSEDED.md` |
| Sol test suite | 104 / 102 (before the final pass) | **112** passed (venv), **110 + 2 blocked** (bare python) | `AUDIT.md` §4 |

**What still stands from Phase 3.3:**

- reversion ≈ 0.41–0.46 with the token table present (one lexicon, one model family);
- `blk ≈ dom` (exploratory);
- paraphrase stability of the reversion rate;
- the withdrawal of the 3D-knowledge conclusion.

---

## 3. Files

| Change | Files |
|---|---|
| **New** | `phase3_2/sol/`: `README.md`, `AUDIT.md`, `PROMPT_REVIEW.md`, `sol.env`, `submit.sh`, `.gitignore` (caches and weights, this folder only), `configs/` (4), `env/` (`make_env.sh`, `activate.sh`, `requirements.in`, laptop lock), `jobs/` (11), `scripts/p33.py`, `src/p33/` (24), `tests/` (8), `local_smoke/`, `legacy_superseded/WHY_SUPERSEDED.md`, `sol_experiment_explained/` (this folder); `phase3_3/ERRATA.md` |
| **Rewritten** | `phase3_2/src/phase3_2/{margins, sampling, analysis}.py`; `phase3_2/scripts/{run_arm_a, run_primary}.py` (guarded deprecated wrappers) |
| **Extended** | `phase3_2/src/phase3_2/prompts.py` (bundles, length-matched control, per-site check); `deltafam.py` (idempotent atomic writer); `phase3/src/phase3/models.py` (zero-length raises) |
| **Appended only** | `phase3_2/PREREGISTRATION.md` (D1–D8, dated 2026-10-05; frozen hash unchanged) |
| **Banner added** | `phase3_3/{README, 00, 01, 02, 04}.md` (erratum pointers; original text untouched) |
| **Moved** (`git mv`, staged, not committed) | `phase3_2/sol/{README.md, arm_a.slurm, primary.slurm, prefetch_models.py}` → `legacy_superseded/` |
| **Side effects, not edits** | tracked `__pycache__/*.pyc` (rewritten by running the tests); `phase3/vendor/alien_syntax/candidates/phi_d*.json` (9 files, **timestamp-only**, rewritten by the pre-fix Phase 3.2 tests before P33-011; the smoke's recorded materials hashes refer to these bytes) |

Nothing was committed or pushed.

---

## 4. Deviations D1–D8 (appended to the preregistration, 2026-10-05)

| # | Deviation | Consequence |
|---|---|---|
| D1 | `blk` is not a clean held-out grammar | C3 NOT TESTABLE; H4 can be supported on mappings and models only |
| D2 | Qwen 3B observed before the freeze | HELDOUT-WEAKENED; never the sole basis of a held-out-model claim |
| D3 | `k*` definition clarified; pre-freeze `k*` withdrawn | no valid `k*` yet |
| D4 | rule-effect intervals recomputed | all include zero |
| D5 | the de-duplication unit is (family, lexicon) | order-independent selection |
| D6 | the identity baseline is constant | C1 ≡ AUROC ≥ 0.60; exploratory `terminal_rate` added |
| D7 | fp32 head; length-matched control | measurement and control changes, both declared |
| D8 | development models include the instruct twins | H4 can be developed and calibrated before the freeze |

---

## 5. 2026-10-07 — corrections to the real development analysis (D9) and model scale (D10)

### Defects found in the analysis of `dev-20261006a`

Every claim was reproduced from the saved files before anything changed.

| ID | Defect | Evidence (saved data) | Fix | Guard |
|---|---|---|---|---|
| R1 | AP ranked tied scores by input row | 1.5B identity baseline: AP 0.452 forward, 0.492 reversed (correct: prevalence 0.468); `length`, `program_nll`, `terminal_rate` also order-dependent | step-wise AP over distinct scores, tie groups as one threshold | 5 AP tests + the whole H4 path under shuffling |
| R2 | precision@k broke a boundary tie by input row | identity 1.5B P@10 0.4 → 0.6 reversed; token_count 0.5B 0.5 → 0.1 | expected precision under uniform selection in the boundary tie | 5 P@k tests |
| R3 | smallest-detectable-AUROC rows: 25 rows, 5 distinct, all with the pilot ICC | `power.csv` | one row per (T, ICC), computed with its own ICC; pilot flagged; T > 80 marked hypothetical | `test_power_scenarios_are_unique_and_each_uses_its_own_icc` |
| R4 | the power report showed only ICC = 0 for the rule effect (and filtered rows on truthiness) | `reports.py`: `x["icc"] in (rule[0]["icc"],)` | every scenario, the pilot in bold, DE and n_eff explained, zero power kept | report ↔ CSV agreement test; zero-power test |
| R5 | RUN_SUMMARY counted `reports/` before writing it | Sol's file: "reports/ — 0 files" | counted against a registry (`p33/artifacts.py`) after everything else is written | first-and-repeated-export test |
| R6 | the power figure lacked the rule-effect sensitivity; footers named one model of a "base\|instruct" pair | figures | a third panel; footers print each model with its own revision (`model@revision`); two sorted lists, the first fix, would have paired 3 of 4 wrongly | figure-series ↔ CSV test; `test_figure_footer_pairs_each_model_with_its_own_revision` |
| R7 | `REPRODUCTION.md` named commands that do not exist and a missing `env/README.md` | report text | the real commands; the file written | `test_reproduction_report_names_commands_that_exist` |
| R8 | the test runner used `setdefault` for its results root, so under `sol.env` a CPU-test job writes `dev-status-readonly/` into the REAL results root and briefly swaps the real `model_pins.json` (then restores it). It happened on Sol: `dev-status-readonly/` dates from 2026-10-06, moved to `results/_quarantine/` on 2026-10-07 | the committed tests and `sol.env`; reproduced against a stand-in root; found on Sol | always a fresh temporary root | `test_tests_never_use_the_real_results_root`; a simulated CPU-test job wrote 0 files into a stand-in root |

### Numbers that changed (development, exploratory)

| Quantity | Was | Now |
|---|---|---|
| identity baseline AP / P@10 (0.5B pair) | 0.410 / 0.3 | **0.407 / 0.407**, the prevalence |
| identity baseline AP / P@10 (1.5B pair) | 0.452 / 0.4 | **0.468 / 0.468**, the prevalence |
| token_count AP (0.5B / 1.5B) | 0.431 / 0.468 | 0.416 / 0.472 |
| length AP (0.5B / 1.5B) | 0.434 / 0.437 | 0.433 / 0.457 |
| risk-score AP and P@k | 0.819 / 0.924 | **unchanged**: 852 distinct risk values per pair at full precision (the CSV's 6-digit rounding merges two of the 1.5B values) |
| AUROC, C1/C2 deltas, bootstrap intervals, Holm p, calibration | — | **unchanged** |
| rule-effect power shown in the report at 80 templates | 0.994 (ICC = 0 only) | **0.251 at the pilot ICC 0.252**, every scenario shown |
| smallest detectable AUROC (T = 80) | 0.62, the same five times | 0.62 at the pilot ICC; 0.62–0.63 across scenarios |
| RUN_SUMMARY reports count | 0 | 10 of 10 |

Unchanged byte for byte: 17 of 19 CSVs. These include Arm A, the rule effect, extinction,
k\* survival, H4 predictions and fertility.

### Model scale (D10)

- **Ceiling:** 3B → 72B.
- **10 held-out checkpoints appended**, all base + instruct pairs:
  - Qwen2.5-Coder 7B, 14B and 32B;
  - DeepSeek-Coder-33B;
  - Qwen2.5-72B, on 2 GPUs.
- **New code:** sharded 2-GPU loading (the 1-GPU path is unchanged); per-task preflight with GPU
  count and memory checks; `array-indices` and the `*_2gpu` job profiles.
- **Unchanged:** the development set and the completed run.
- **Not tested here:** the 2-GPU load itself, which needs two GPUs.

### Files (2026-10-07)

| Change | Files |
|---|---|
| corrected | `p33/h4.py`, `p33/power.py`, `p33/reports.py`, `p33/plots.py`, `p33/export.py`, `p33/preflight.py`, `p33/registry.py`, `p33/splits.py`, `p33/scorers.py`, `phase3_2/src/phase3_2/margins.py` (2-GPU branch only), `scripts/p33.py`, `submit.sh`, `configs/heldout.json`, `tests/run_tests.py` |
| new | `p33/artifacts.py`, `scripts/analysis_revision.py`, `env/README.md`, `tests/test_metric_and_report_corrections.py`, `tests/test_model_scale.py` |
| appended | `phase3_2/PREREGISTRATION.md` (D9, D10; frozen hash unchanged) |
| regenerated (not hand-edited) | `phase3_3/sol_results/dev-20261006a/{csv,plots,reports}`; the previous versions are in `analysis_revisions/r1-2026-10-07-metric-corrections/before/` |
