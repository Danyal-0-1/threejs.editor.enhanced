# 04 — Retyping and reading plan (the Sol pipeline)

---

## 1. Inventory

Computed with `wc -l` and the Python AST on the final code, not estimated.

| Category | Files | Lines |
|---|---:|---:|
| **New: `src/p33/` package** | 24 | **5,023** |
| **New: `scripts/p33.py` (CLI)** | 1 | **412** |
| **New: `tests/`** (6 test modules + runner + helpers) | 8 | **1,630** |
| **New Python, total** | 33 | **7,065** |
| Shared modules rewritten in full for this phase (`margins`, `sampling`, `analysis`) | 3 | 775 |
| Shared modules extended (`prompts`, `deltafam`) | 2 | 514 |
| Legacy runners turned into guarded wrappers (`run_arm_a`, `run_primary`) | 2 | 150 |
| `phase3/src/phase3/models.py` (one branch made loud) | 1 | 229 |
| Shell: 11 jobs + `submit.sh` + `make_env.sh` + `activate.sh` + `sol.env` | 15 | 342 |
| Configs | 4 | — |

| `p33` module | Lines | | `p33` module | Lines |
|---|---:|---|---|---:|
| `pipeline.py` | 448 | | `power.py` | 262 |
| `plots.py` | 429 | | `shards.py` | 262 |
| `export.py` | 414 | | `h5.py` | 249 |
| `h4.py` | 350 | | `fakes.py` | 194 |
| `splits.py` | 334 | | `prefetch.py` | 184 |
| `reports.py` | 329 | | `kstar.py` | 166 |
| `armb.py` | 289 | | `preflight.py` | 158 |
| `config.py` | 274 | | `provenance.py` | 154 |
| `demos.py` | 111 | | `freeze.py` | 109 |
| `registry.py` | 83 | | `fertility.py` | 80 |
| `scorers.py` | 66 | | `h2.py` | 43 |
| `_paths.py` | 24 | | `__init__.py` | 11 |

**Denominator for the percentages below:** 7,065 new lines + 775 lines of
fully rewritten shared modules = **7,840**. Two retyped functions,
`prompts.assert_prompt_matches` (21 lines) and `deltafam.write` (23 lines),
sit in *extended* files that are not in the denominator. That overstates the
percentage by about 0.6 points; it is stated here rather than hidden.

---

## 2. Triage

**Rule:** LOAD-BEARING means a subtle mistake could invalidate a conclusion
*while the program still runs*. A crash is not the danger; a plausible wrong
number is.

### LOAD-BEARING

| File | Why |
|---|---|
| `splits.py` | The only thing standing between development and held-out data. A missing check does not crash; it silently turns a confirmatory result into an exploratory one. |
| `pipeline.py` | Decides *what* is scored: which sites, which prompt, which demonstrations, which model per array task. Defect P33-012 lived here: a resubmitted task scored nothing, and it looked like success. |
| `demos.py` | **P33-008 lived here.** A leaking demonstration produces a beautiful, wrong extinction curve. |
| `kstar.py` | **P33-007 lived here.** A threshold that depends on bookkeeping, not on the model. |
| `phase3_2/analysis.py` | **P33-005 lived here.** Intervals too narrow, with no visible symptom. |
| `phase3_2/margins.py` | The measurement itself: P33-001 (one-sided zero) and P33-002 (bf16 rounding decides the sign). |
| `phase3_2/sampling.py` | **P33-003/004 lived here**: order-dependent selection, and a missing cell that passed. |
| `phase3_2/prompts.py` | **P33-006 lived here**: one lexicon's table shown for every site. |
| `shards.py` | Decides what "done" means. A wrong answer here loses cells or double-counts them. |
| `h4.py` | The headline hypothesis: the risk sign, the label, the pairing, the baselines, the frozen criteria. |
| `h5.py` | A repair that changes meaning would fake a benefit. The IR proof is the guard. |
| `armb.py` | Collapsing the hurdle hides "never reached" inside "never reverted". |

### PLUMBING

Here a mistake is loud, or cannot change a number.

| File | Why |
|---|---|
| `config.py` | Paths, defaults and hashing. `atomic_write_text` is load-bearing in practice (P33-014), but loud. |
| `provenance.py` | Records; changes nothing that is computed. |
| `preflight.py` | Refuses jobs; it cannot change a result. Read its docstring. |
| `prefetch.py`, `scorers.py` | Fail loudly on a missing or wrong revision (`test_wrong_revision_is_refused`). |
| `export.py`, `plots.py`, `reports.py` | Read-only consumers of merged rows. Check the stage banners, then trust the tests. |
| `fertility.py`, `power.py` | Descriptive and sizing. Power matters before held-out sizing; read §8 of `02`. |
| `freeze.py` | Assembles the payload; the immutability lives in `splits.py`. |
| `registry.py` | A data table. |
| `fakes.py` | Test support only; `sol.env` guarantees it is never active in a real job. |
| `h2.py` | Returns NOT TESTABLE. |
| `scripts/p33.py` | Argument parsing. Two functions with teeth: `task_args` (P33-012) and `load_cfg` (stage separation). |
| `jobs/*.slurm`, `submit.sh` | Read them once; they are thin. |

---

## 3. The short list

Seven files:

| File | Lines |
|---|---:|
| `splits.py` | 334 |
| `pipeline.py` | 448 |
| `demos.py` | 111 |
| `kstar.py` | 166 |
| `h4.py` | 350 |
| `phase3_2/analysis.py` | 263 |
| `phase3_2/margins.py` | 323 |
| **total** | **1,995** (25.4% of 7,840) |

**How to judge what they give you.** The 11 rows of
[`01 §17`](01_theory_and_research_design.md) map each construct to its code.

- **6 of the 11 rows** are implemented entirely in these seven files: no peeking,
  the extinction threshold, the clean dose, evidence-level uncertainty, sign
  precision, and site-level predictability.
- **The other 5** are each one self-contained module that can be read later:
  - the length control (`prompts`);
  - reproducibility (`shards`, `provenance`);
  - H5;
  - Arm B;
  - power.

This is a count of rows, not a percentage of understanding. No
"you will understand 85%" figure is claimed.

---

## 4. Data structures first

Read the definitions in [`03 §2`](03_code_and_pipeline.md), in this order.
Each one is the input of the next.

```
RunConfig ──► CellClass ──► Plan ──► Cell ──► (shard + done marker) ──► MergeResult
                                       │
                         PairScore ◄───┤ (per site)      DemoSet ◄─ (per ladder rung)
                                       ▼
                                  row ──► KStar ──► KMSummary
JobManifest wraps every job; DEV_FREEZE / HELDOUT_UNLOCK wrap every held-out access.
```

The relationship to hold onto:

```
same config + same model revision + same sites   ⇒  same cell key  ⇒  "already done", skip it
a different config hash under the same run id     ⇒  refused before any work
```

---

## 5. One end-to-end path — the path to retype

| # | File | Function(s) |
|---:|---|---|
| 1 | `scripts/p33.py` | `main` → `cmd_run` → `task_args` (array task *i* → model *i*) |
| 2 | `pipeline.py` | `run`: `install_signal_handlers`, `shards.assert_compatible` |
| 3 | `pipeline.py` → `splits.py` | `build_plan` → `enforce_config` → `check_access` → `classify` (+ `load_unlock` → `frozen_drift` when held-out) |
| 4 | `phase3_2/sites2.py` → `sampling.py` | `classify` → `dedupe_within_cells` → `balanced` → `assert_balanced` |
| 5 | `pipeline.py` → `config.py` | `write_plan_artifacts` → `atomic_write_text` |
| 6 | `pipeline.py` | `assigned_models`, `models_for`, `primary_cells` → `primary_site_source` |
| 7 | `shards.py` | `ShardStore.status` (done / failed / corrupt / missing), `quarantine` |
| 8 | `scorers.py` | `load_scorer` (revision must equal the pin) |
| 9 | `pipeline.py` → `demos.py` | `score_primary_cell` → `pool_order` → `for_site` → `audit` |
| 10 | `prompts.py` | `bundle` → `assert_prompt_matches` |
| 11 | `pipeline.py` → `margins.py` | `_score_into` → `TokenScorer.score_pair_detailed` → `check_pair` → `_logprobs_rows` |
| 12 | `shards.py` | `ShardStore.write` (shard, then marker) |
| 13 | `pipeline.py` → `shards.py` | `merge` → `ShardStore.merge` → `write_merged` |
| 14 | `export.py` → `kstar.py`, `analysis.py` | `compute`, `km_from_kstars` → `kaplan_meier`; `cluster_bootstrap` → `_draw_rows` → `paired_rule_effect` |
| 15 | `freeze.py` → `splits.py` | `build_payload` → `write_freeze`; later `write_unlock` → `frozen_drift` |

---

## 6. What to retype

### Core — 827 lines, **10.5%** of 7,840

| Function | File:lines | Lines | Why | In → out | Invariant | Test after |
|---|---|---:|---|---|---|---|
| `classify` | splits 84–117 | 34 | the registered split | (family, lexicon, model) → `CellClass` | `blk` never HELDOUT; > 3B FORBIDDEN; DEVELOPMENT only for registered cells | `test_registered_split_classification` · `test_blk_is_never_labelled_a_heldout_grammar` · `test_no_model_above_3b_in_any_stage` |
| `check_access` | splits 128–156 | 29 | the gate | (stage, cell, run_dir) → class or `SplitViolation` | held-out needs `load_unlock`; dev refuses held-out | `test_dev_stage_refuses_a_heldout_mapping` · `test_heldout_stage_refuses_without_unlock` |
| `write_freeze` | splits 188–207 | 20 | immutability | (path, payload) → sha | refuse if it exists; mode 444 + sidecar | `test_freeze_cannot_be_written_twice` |
| `load_freeze` | splits 210–224 | 15 | tamper detection | path → payload | sidecar sha must match | `test_tampered_freeze_is_detected` |
| `write_unlock` | splits 235–263 | 29 | the human act | (run_dir, freeze, phrase) → record | exact phrase; zero drift | `test_unlock_needs_the_exact_phrase` · `test_unlock_refuses_if_source_changed_since_freeze` |
| `frozen_drift` | splits 274–297 | 24 | what "frozen" means | freeze → drifted items | source, materials and model pins all compared | `test_a_model_repinned_after_the_freeze_is_refused` |
| `load_unlock` | splits 303–334 | 32 | re-verification on every access | run_dir → record | freeze unchanged; no drift (once per process) | `test_heldout_access_refuses_if_source_changes_after_unlock` |
| `ShardStore.status` | shards 98–126 | 29 | what "done" means | key → `CellStatus` | done ⇔ shard sha == marker sha | `test_corrupt_shard_detected_quarantined_and_rewritable` · `test_marker_without_shard_is_corrupt` |
| `ShardStore.write` | shards 132–148 | 17 | atomic completion | (key, fields, rows) → path | shard before marker; marker carries the sha | `test_atomic_write_then_done` |
| `ShardStore.merge` | shards 196–226 | 31 | determinism | expected keys → `MergeResult` | identical duplicates dropped, conflicting refused; sorted | `test_merge_is_byte_deterministic` · `test_identical_duplicates_dropped_conflicting_refused` |
| `compute` | kstar 74–103 | 30 | the threshold | (ladder, margins) → `KStar` | M(0) ≥ 0 ⇒ 0; first upward crossing; crossed-then-dropped not censored | the six `test_kstar_*` / `test_crossed_then_dropped_is_not_censored` / `test_nonmonotone_*` tests |
| `kaplan_meier` | kstar 124–149 | 26 | survival | (times, events) → `KMSummary` | censored sites stay at risk until their time | `test_kaplan_meier_hand_example` |
| `is_leak` | demos 74–83 | 10 | the leak definition | (site, demo) → reason or None | the fixed opening is exempt | `test_replayed_decision_prefix_is_a_leak_but_the_fixed_opening_is_not` |
| `for_site` | demos 86–105 | 20 | the dose | (site, pool, order, n) → `DemoSet` | first n clean, in fixed order; raises if short | `test_demonstrations_never_contain_the_target` · `test_ladder_is_nested_and_hashed` |
| `build_plan` | pipeline 103–132 | 30 | refuse first, then enumerate | cfg → `Plan` | `enforce_config` before any `classify` | `test_plan_refuses_before_enumerating_any_heldout_site` |
| `_score_into` | pipeline 250–272 | 23 | measurement → row | (row, scorer, prefix, site) → row | refusal → `status` + reason, never 0.0 | `test_canonical_scorer_has_no_silent_zero_branch` |
| `score_arm_a_cell` | pipeline 275–297 | 23 | Arm A | cell → rows | the prompt comes from the site's own lexicon | `test_every_site_gets_its_own_lexicons_table_in_a_two_lexicon_run` |
| `score_primary_cell` | pipeline 300–334 | 35 | the ladder | cell → rows | demonstration audit empty; nested | e2e `test_no_demonstration_leaks_in_any_ladder_row` |
| `run` | pipeline 362–435 | 74 | orchestration with teeth | (cfg, run_dir, exp) → status | task *i* → model *i*; revision check; skip done; failures recorded; signal → INTERRUPTED | `test_resumed_output_equals_uninterrupted_output` · `test_array_task_i_scores_model_i_even_when_resubmitted_alone` · `test_signal_interruption_leaves_finished_cells_and_resumes` |
| `build_table` | h4 184–213 | 30 | the H4 data | Arm A rows → table | risk = −M(base); label = M(inst) < 0; paired on `site_id` | `test_build_table_pairs_base_with_instruct_on_site` |
| `criteria` | h4 319–350 | 32 | the frozen decision | metrics → C1/C2/C3 | Holm over C1, C2; C3 NOT TESTABLE | `test_criteria_c3_not_testable_without_a_valid_grammar` |
| `ir_proof` | h5 92–110 | 19 | repair safety | (L, L2) → proof | every program × family keeps its IR | `test_every_arm_preserves_ir_over_the_whole_corpus` · `test_ir_proof_can_fail` |
| `observe` | armb 179–191 | 13 | reach | (text, site) → observation | longest candidate matched first | `test_reach_and_conditional_reversion_are_separate` |
| `hurdle` | armb 194–201 | 8 | two numbers, never one | observations → table | P(reach) and P(revert \| reach) separate | same |
| `_draw_rows` | analysis 87–100 | 14 | multiplicity | (clusters, ids, draw) → rows | every copy tagged `_draw` | `test_bootstrap_keeps_duplicate_cluster_weight_hand_example` |
| `cluster_bootstrap` | analysis 103–145 | 43 | every interval | (rows, stat) → `Interval` or None | ≥ 8 clusters; None if the point is undefined | `test_no_interval_below_eight_clusters` |
| `paired_rule_effect` | analysis 176–189 | 14 | the rule effect | rows → mean | keyed on (`_draw`, `site_id`) | `test_old_dict_pairing_collapsed_the_duplicate` |
| `check_pair` | margins 137–153 | 17 | refusals | (ids_c, ids_q) → k | raise on identical, zero-length, no context | `test_check_pair_refuses_every_degenerate_case` |
| `score_pair_detailed` | margins 223–248 | 26 | the measurement | (prefix, c, q) → `PairScore` | both sides scored from the same k; fp32 head | `test_merged_candidate_is_measured_not_zeroed` |
| `dedupe_within_cells` | sampling 82–96 | 15 | the de-duplication unit | sites → (kept, dropped) | within (family, lexicon); canonical tie-break | `test_dedup_unit_is_family_lexicon_and_records_drops` |
| `balanced` | sampling 121–147 | 27 | selection | (sites, limit) → sites | proportions per cell; order-independent | `test_selection_is_identical_under_every_lexicon_order` |
| `assert_balanced` | sampling 173–189 | 17 | the missing-cell check | (sites, expected) → raises | every materially available cell present | `test_missing_cell_is_refused` · `test_structurally_empty_cell_is_reported_not_failed` |
| `assert_prompt_matches` | prompts 271–291 | 21 | per-site table check | (site, phi, prompt) → raises | the table belongs to the site's own lexicon | `test_old_behaviour_first_lexicon_table_is_rejected` |

### Optional — +203 lines, total 1,030 = **13.1%**

| Function | File:lines | Lines | What it teaches |
|---|---|---:|---|
| `atomic_write_text` | config 198–219 | 22 | why `.tmp.<pid>` is not unique on a cluster (P33-014) |
| `assigned_models` | pipeline 139–143 | 5 | array index → model (P33-012) |
| `primary_site_source` | pipeline 184–197 | 14 | the balanced primary subset |
| `auroc` | h4 51–69 | 19 | Mann–Whitney with average ranks: why a constant score gives exactly 0.5 |
| `ece` | h4 98–108 | 11 | equal-width calibration bins |
| `logistic_fit` | h4 118–142 | 25 | Newton–Raphson behind Platt scaling |
| `_crossfit_terminal_rate` | h4 216–234 | 19 | leave-one-template-out cross-fitting |
| `pool_order`, `common_opening` | demos 59–71 | 11 | seeded nesting; the fixed-opening exemption |
| `holm` | analysis 154–164 | 11 | step-down adjustment |
| `TokenScorer._logprobs_rows` | margins 205–220 | 16 | the fp32 head itself |
| `hanley_mcneil_var`, `h4_power`, `rule_power` | power 71–84, 125–129 | 17 | the design effect in three lines |
| `define_arms` | h5 113–122 | 10 | targeted vs random vs global |
| `write` | deltafam 184–206 | 23 | idempotent + atomic materials (P33-011) |

---

## 7. What to ignore for now

- `plots.py`, `reports.py`, and most of `export.py`. They consume CSVs; read one
  report and one figure instead.
- `fakes.py`: read only enough to know it plants a *site-level habit* and
  shares the real `check_pair`.
- `prefetch.py`, `preflight.py`, `provenance.py`, `scorers.py`: read the
  docstrings.
- `registry.py`, `h2.py`, `_paths.py`, `__init__.py`.
- `scripts/run_arm_a.py`, `scripts/run_primary.py`: deprecated wrappers that
  refuse held-out and contaminated cells.
- `legacy_superseded/`: kept only so the record of what would *not* have run
  survives.
- All of `phase3/vendor/` and the unchanged Phase 3 / 3.2 modules (`sites2`,
  `backends`, `templates`). They are covered by those phases' 54 + 36 tests.

---

## 8. The things you are most likely to get wrong

None of these is hypothetical. Each happened in this project, and each was
silent.

### (1) Showing the answer and calling it a dose

- **Where:** `demos.for_site` vs any `templates[:32]`.
- **Misunderstanding:** that "the first 32 templates" is a neutral
  demonstration pool.
- **Reality:**
  - 82 of the 120 Phase 3.3 extinction sites came from those templates.
  - On today's development plan the same rule would leak for **177 of 400**
    sites.
- **Symptom:** a clean-looking, fast extinction curve. The withdrawn
  "≈ 5–7 shots" headline was exactly that.
- **Detector:** `demos.audit` inside `score_primary_cell` (it raises), and
  `test_old_first_32_pool_leaked_the_target`.

### (2) Treating "already correct", "never" and "missing" as the same thing

- **Where:** `kstar.compute`.
- **Reality:** the old code had three errors:
  - 84 of 125 already-correct curves got `None`;
  - 41 got a later re-crossing;
  - 16 were both crossed and censored.
- **Symptom:** a threshold that moves when you change the bookkeeping.
- **Detector:** the six k\* tests. Read
  `test_crossed_then_dropped_is_not_censored` first.

### (3) Counting a twice-drawn family once

- **Where:** any paired statistic inside a cluster bootstrap.
- **Reality:** tA, tA, tB should give 5/3; pairing by `site_id` gives 2.0.
- **Symptom:** intervals too narrow. One Phase 3.3 interval excluded zero and
  should not have.
- **Detector:** `test_old_dict_pairing_collapsed_the_duplicate`.

### (4) A rule table from the wrong lexicon

- **Where:** `prompts.bundle` vs `load_candidate(args.lexicons[0])`.
- **Reality:** the old runners showed the first lexicon's table to every site in
  a multi-lexicon run.
- **Symptom:** "rule-following" measured against the wrong rules.
- **Detector:** `assert_prompt_matches`, and
  `test_old_behaviour_caught_even_when_the_table_line_coincides`.

### (5) Letting rounding decide a sign

- **Where:** reading logits in bf16.
- **Reality:** a margin of +0.6250 is exactly 10/16. Any site within ~0.06 nats of
  zero can flip sign.
- **Detector:** the `fp32_head` column; ties counted in QC (0 in the smoke).

### (6) Writes that are atomic for one writer but not for two

- **Where:** any `path + ".tmp"`, and `clean_temp`.
- **Reality:**
  - Array tasks start together, on different nodes, and can share a pid.
  - The old scheme failed **5 of 5** trials of the concurrency test.
  - The test suite also rewrote 9 tracked lexicon files every run, changing their
    hashes (P33-011).
- **Symptom:** a corrupt plan file followed by every resume refusing, or
  "materials changed" in the middle of a run.
- **Detector:** `test_concurrent_writers_never_share_a_temp_file`,
  `test_materials_writer_is_idempotent_and_atomic`.

### (7) A "read-only" command with a side effect

- **Where:** `p33.py status` vs `validate`.
- **Reality:** `status` constructed a `ShardStore` for every experiment, which
  creates its directory. A directory is what makes an experiment count as
  "started", so after one `status` the never-run Arm B was started and EMPTY.
- **Symptom:** following the README, `dev_freeze` refused a complete
  development run with `INCOMPLETE: {'armb': 'EMPTY'}` (P33-017). The unit tests
  passed; only rehearsing the README's exact commands found it.
- **Detector:** `test_status_is_read_only_so_validate_still_passes`, which
  drives the real CLI.

### (8) Checking the guard only at the door

- **Where:** `write_unlock` vs `load_unlock`.
- **Reality:** the source used to be compared with the freeze only at unlock time.
  Code edited after the unlock, or a model re-pinned, still scored held-out cells.
- **Detector:** `test_heldout_access_refuses_if_source_changes_after_unlock`,
  `test_a_model_repinned_after_the_freeze_is_refused`.

---

## 9. AI-generated-code audit

Honest provenance labels. "Apparently arbitrary" is used freely: it is the
truthful label for most constants.

| Value | Where | Role | Provenance |
|---|---|---|---|
| `B = 2000` | `analysis.cluster_bootstrap`, config | bootstrap replicates | **Conventional** for percentile intervals. The exact value is **apparently arbitrary**. The smoke used 200, which is labelled in every CSV row. |
| seeds 20261002 / 20261005 / 20261006; H5 1–5 | config | reproducibility | **Apparently arbitrary** (they are dates). Only the fixing matters. |
| `min_clusters = 8` | `analysis` | no interval below | **Judgment call, apparently arbitrary.** Percentile bootstraps over very few clusters are unreliable; 8 is not derived. |
| ladder `0,1,2,4,8,16,32` | config | dose | Doubling is a **design choice**. The top rung 32 is **checked**: every development site can fill 32 clean rungs. |
| paraphrases `p0–p2` | `prompts` | robustness | Three is **apparently arbitrary**. `p0` *is* the rule prompt (same sha `9668e9c3…`). |
| `primary.site_limit = 400` | config | sample | **Compute-constrained / apparently arbitrary.** Not from a power analysis, which can only run after the development run. |
| `chunk_size = 64` | config | restart granularity | **Engineering trade-off, apparently arbitrary.** |
| `max_new_tokens = 192` | `armb` | generation cap | **Checked with headroom:** the longest rendered target is 73 Qwen tokens (`d25s1`/`blk`/`t075`), so 2.6×. Other tokenizers were not measured. |
| `n_demos = 4` (Arm B) | `armb` | prompt | **Apparently arbitrary.** |
| H5 `budget = 3`, `low_risk_tolerance = 0.02` | config | repair size, control | **Preregistered, apparently arbitrary.** |
| precision@{10, 50}, ECE 10 bins | config | metrics | **Conventional, apparently arbitrary.** |
| C1 0.10, C2 0.05, C3 0.65 | freeze | decision rules | **Preregistered judgment calls.** C1 reduces to AUROC ≥ 0.60 (D6). |
| `MAX_SIZE_B = 3.0` | `splits` | scale gate | **Derived** from the preregistered gate (no scaling past 3B without valid held-out-grammar evidence, which cannot exist yet). |
| Platt calibration + Youden threshold | `freeze` | calibration | **Standard.** Youden is one of several defensible threshold rules; the choice is **apparently arbitrary**. |
| `terminal_rate` pseudo-count 1 | `h4` | shrinkage | **Apparently arbitrary.** |
| `NEUTRAL_FILLER` text | `prompts` | length control | **Apparently arbitrary content.** Its neutrality is assumed, not measured. |
| `clean_temp` min age 900 s | `shards` | safety | **Engineering judgment:** a write lasts milliseconds; 15 min is generous. |
| `--signal=USR1@300` | jobs | grace period | **Derived with headroom:** the stop flag is checked between *sites*, and one site takes seconds. |
| prefetch retries 3; preflight thresholds (GPU > 2 GiB, results ≥ 2 GB, HF cache ≥ 5 GB) | `prefetch`, `preflight` | robustness | **Apparently arbitrary** rough lower bounds. |
| time limits | `submit.sh` | Slurm | From the README §14 estimates with ≥ 2.5× headroom. The estimates are **extrapolations** from a laptop smoke. |
| `m = 3.0`, `icc = 0.1` | `power.analyse` → `armb_precision` | Arm B precision | **Hard-coded, apparently arbitrary.** Unlike the rule and H4 analyses, these are not estimated from the pilot. A known inconsistency. |

### Cross-file inconsistencies and declared deviations

1. **`armb_precision` is not pilot-driven** (the last row above). The rule and
   H4 power analyses estimate `m` and sweep the ICC; Arm B's does not.
2. **`deltafam.write` still writes into `phase3/vendor/…/candidates/`.** This was
   inherited from Phase 3.2 and declared there. It is now idempotent and atomic,
   so tests no longer rewrite the nine tracked files.
3. **The `dev` command group accepts smoke runs.** This is deliberate
   (`load_cfg`): a smoke run holds only development cells.
4. **Pins taken after the freeze are not drift-checked.** `frozen_drift` compares
   pins only for models pinned *at freeze time*. A model first pinned after the
   freeze passes, but its revision is on every row. The README orders prefetch
   before the smoke, so every study model is pinned before any freeze.
   Re-running prefetch keeps existing pins (P33-018); only `--repin` moves them.
5. **The smoke's stored config still contains `primary.demo_pool: 48`.** The
   field was never read and has now been removed from the code and every shipped
   config. The smoke's `run_config.json` and its hash `190fbc72…` are kept as
   recorded.
6. **The smoke's preflight file predates the WARN/PASS split.** Two
   informational checks read PASS there; today's code prints WARN.
7. **Source hashes cover** `p33`, `phase3_2/src`, `phase3/src` and the CLI. They
   do not cover the job scripts or configs. Configs are frozen through the
   config hash and materials through materials hashes; the job scripts are not
   frozen at all.
8. **Arm B requests carry verb cues** ("recolor …"). That is a known
   limitation of rendering requests from the IR.

### Data assumptions that differ across files

- **The cluster unit `template` is shared across lexicons.** t000 in `d25s1` and
  in `d50s1` is the same cluster. The bootstrap treats them as one family;
  `sampling` treats them as different cells. Both are intended, but they are easy
  to conflate.
- **A site's identity is `family:lexicon:template:terminal:occurrence`.** Its
  prefix is *not* an identity: 443 development sites duplicate another site's
  prefix within their cell and were dropped.
- **`os.replace` is assumed to be atomic** on Sol's filesystems. This is standard
  POSIX, but untested on Sol from here.
- **H4 pairs base and instruct by `site_id`.** Nothing requires the two to share a
  tokenizer; each row carries its own `tokenizer_id`.
