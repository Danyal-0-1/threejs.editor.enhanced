# 02 — Every fix made during Phase 3.3, before Phase 4

> **What this is.** This is the complete list of what was found wrong and fixed, from the audit
> of the inherited pipeline (2026-10-05) to the end of the held-out results stage (2026-10-09).
> Phase 4's own fixes (2026-10-21) are in [`01`](01_phase4_step0_fixes.md).
>
> **How to read it.** Each item gives the problem, the evidence, the fix and its guard, where
> there is one. It summarises the primary records below and links to them. Where this file and a
> record disagree, the record wins.

| record | what it holds |
|---|---|
| [`phase3_2/sol/AUDIT.md`](../../phase3_2/sol/AUDIT.md) | the 2026-10-05 audit and the 2026-10-07 corrections, with their evidence |
| [`sol_experiment_explained/08`](../../phase3_2/sol/sol_experiment_explained/08_changes_defects_and_superseded_numbers.md) | each pre-run defect explained, with its fix and its guard test |
| [`phase3_2/PREREGISTRATION.md`](../../phase3_2/PREREGISTRATION.md) | deviations D1–D12 (D13 belongs to Phase 4) |
| [`phase3_3/ERRATA.md`](../../phase3_3/ERRATA.md) | E1–E4: the withdrawn and corrected claims of the first Phase 3.3 run |
| [`phase3_2/sol/PROMPT_REVIEW.md`](../../phase3_2/sol/PROMPT_REVIEW.md) | where the two briefs were right, wrong or incomplete |
| [`heldout_results_explained/08`](../../phase3_2/sol/heldout_results_explained/08_issues_and_superseded_numbers.md) | issues found at the results stage, and superseded numbers |
| [`dev-20261006a/SOL_SYNC_2026-10-09.md`](../../phase3_3/sol_results/dev-20261006a/SOL_SYNC_2026-10-09.md) | the laptop ↔ Sol file comparison |
| git history, `699dfdb..1750947b` | the commit messages quoted below |
| the session record | small bugs found while building and testing, not recorded elsewhere; marked *(session record)* |

---

## The timeline

| date | stage | what was fixed | section |
|---|---|---|---|
| 2026-10-05 | audit of the inherited Phase 3.3 pipeline, before any Sol job | the brief's 10 stop-ship defects (all true), more found in the audit, and P33-011 to P33-018 in a final verification pass; deviations D1–D8; errata E1–E4 | [§1](#1-2026-10-05--the-audit-before-any-sol-job) |
| 2026-10-05 to 06 | building and rehearsing the new pipeline | bugs caught by the tests and the runbook rehearsal | [§1.6](#16-bugs-caught-while-building-and-rehearsing-session-record) |
| 2026-10-07 | the real development run `dev-20261006a`, analysed | D9: tied scores in AP and P@k, power per ICC, report fixes (R1–R8); D10: models up to 72B | [§2](#2-2026-10-07--the-development-runs-analysis-d9-and-model-scale-d10) |
| 2026-10-07 | execution on Sol | a test artifact quarantined; the freeze; the unlock; the chain run one job at a time | [§2.5](#25-execution-on-sol-2026-10-07) |
| 2026-10-08 | the held-out chain running | D11: the scale analysis specified and approved; a bootstrap p of 0 shown as "< 1/B" | [§3](#3-2026-10-08--the-scale-analysis-d11-and-a-reporting-fix) |
| 2026-10-09 | the held-out results | a Slurm hold released; gaps disclosed (D12); doc claims corrected; paper figures; exploratory checks and three wording corrections; git ↔ Sol consistency | [§4](#4-2026-10-09--the-held-out-results-stage) |

**What these fixes did not do:**

- **None changed a frozen held-out number.**
- **Every fix to the measurement or to the frozen analysis came before the freeze** (2026-10-07).
- **D11 is the one analysis specified after the freeze.** It was approved on 2026-10-08 (commit
  `efee629`, 12:03) before any held-out outcome was examined. The first held-out outcomes were
  read later that day, in a preview with the frozen code on a scratch copy (08 §3).
- **Everything after that is reporting or post hoc,** outside the frozen code and labelled so:
  - the "< 1/B" fix;
  - the doc corrections;
  - the paper figures;
  - the exploratory checks.

---

## 1. 2026-10-05 — the audit, before any Sol job

The audit read and ran the inherited code before changing anything. It checked every claim in
the brief by computation or by reading the code.

### 1.1 The brief's ten stop-ship defects (all verified, all fixed)

| ID | defect | evidence | fix | guard |
|---|---|---|---|---|
| P33-006 | the runners showed the first lexicon's rule table and examples to **every** site | `run_arm_a.py:140`, `run_primary.py:93` | a per-site prompt bundle (`prompts.bundle`) with `assert_prompt_matches` | `test_old_behaviour_first_lexicon_table_is_rejected`, `…_two_lexicon_run` |
| P33-003 | de-duplication depended on the order of the lexicons on the command line | reversing the order moved retained sites: `d25s1` 220 → 150, `d50s1` 204 → 174, `d50s2` 172 → 272 | de-duplicate **within** (family, lexicon), with a canonical tie-break; every drop logged (D5) | `test_selection_is_identical_under_every_lexicon_order`, `test_old_global_dedup_was_order_dependent` |
| P33-004 | `assert_balanced` checked families only; `empty_cells` was hard-coded `[]` | `sampling.py:94` | expected cells come from the classified materials; a structurally empty cell (such as `dom/d25s2/sigil`, which never remaps a sigil) is reported, not failed | `test_missing_cell_is_refused`, `test_structurally_empty_cell_is_reported_not_failed` |
| P33-008 | the demonstrations were templates t000–t031 for every site | **82 of 120** extinction sites saw their own target program | a leak-free nested ladder (`p33/demos.py`); a leak raises | `test_old_first_32_pool_leaked_the_target`, an end-to-end leak test |
| P33-007 | `k*` was wrong: already-correct sites got None, later re-crossings were used, and curves were marked crossed *and* censored | 84, 41 and 16 of 240 curves | the exact definition, and Kaplan–Meier for two populations (D3) | 8 `k*` tests |
| P33-005 | the bootstrap lost the weight of a cluster drawn twice | hand example: 2.000 returned, 5/3 correct | `_draw` tags; pairs keyed on (`_draw`, `site_id`) (D4) | `test_bootstrap_keeps_duplicate_cluster_weight_hand_example` |
| P33-009 | fertility was computed from the first model and reported for every model | `run_arm_a.py:124` | computed per distinct tokenizer | `test_fertility_is_computed_per_distinct_tokenizer` |
| P33-001 | `phase3.linter.score_site` reached a scorer that returned 0.0; and the first P32-001 fix still returned 0.0 for **one side** when one candidate's tokens are a prefix of the other's | `models.py:193`, `margins._score_from` | explicit errors (`ZeroLengthSpan`, `IdenticalCandidates`, `NoContext`); `HFModel` raises | `test_check_pair_refuses_every_degenerate_case`, `test_old_phase3_scorer_now_raises_instead_of_returning_zero` |
| P33-010 | provenance was never wired into the runners, and one big JSON was written at the end of the job | no runner imported `runmeta`; `run_arm_a.py:237` | a `JobManifest`, atomic shards and markers | `test_provenance_is_bound_to_every_job_and_shard`, `test_every_row_carries_its_split_revision_and_prompt` |
| (D1) | `blk` was inspected before the freeze | 272 + 60 sites scored; the preregistration's §8 itself reports `blk ≈ dom` | relabelled EXPLORATORY / HELDOUT-WEAK-FAMILY; H4's C3 is NOT TESTABLE | `test_blk_is_never_labelled_a_heldout_grammar` |

### 1.2 Found during the audit (not in the brief)

| ID | defect | evidence | fix |
|---|---|---|---|
| P33-002 | bf16 logits are quantised, and the outcome is a margin's **sign** | native margins +0.6250 = 10/16 and −4.4375 = −71/16 | an fp32 output head, validated against the native logits: same sign, 0.005–0.042 nats apart (D7) |
| — | 237 of 240 extinction curves were non-monotone | the first Phase 3.3 primary output | `nonmonotone`, crossing counts, `sustained_k` |
| — | the no-rule control was about a third shorter than the rule prompt | 1,014 vs 1,527 characters | a `norule_lenmatched` control, padded to the rule prompt's token count (D7) |
| — | Qwen2.5-Coder-3B was observed before the freeze | `arm_a_sizes.json` | every 3B row labelled HELDOUT-WEAKENED (D2) |
| — | the identity baseline is constant on the eligible set, so its AUROC is exactly 0.5 | by construction | stated as D6; an exploratory `terminal_rate` baseline added |
| — | `TRANSFORMERS_CACHE` is ignored by transformers 5.x, and offline resolution needs the same `allow_patterns` | 0 references in 5.16.1; `IncompleteSnapshotError` | `HF_HUB_CACHE` plus pinned patterns |
| — | the pre-freeze rule-effect intervals were too narrow | recomputed: **all four** include zero, where one had excluded it | erratum E2, D4 |

### 1.3 Found in the final verification pass

These were found by re-reading the operational path and **rehearsing the runbook** end to end,
not by the unit tests.

| ID | defect | how it would have shown up on Sol | fix | guard |
|---|---|---|---|---|
| P33-011 | the Phase 3.2 tests rewrote 9 tracked lexicon files with a fresh timestamp on every run, changing their sha256 | a `cpu_tests` run mid-sweep, and every later GPU job fails preflight with "materials CHANGED" | `deltafam.write` is idempotent and atomic | `test_materials_writer_is_idempotent_and_atomic`; the 9 files stayed byte-identical through every suite |
| P33-012 | the array stride came from `SLURM_ARRAY_TASK_COUNT`, so resubmitting one index selected **no model**; Arm B and H5 indexed the filtered model list | a "successful" resubmission that scored nothing | task *i* → model *i* of the full config; `P33_ARRAY` in `submit.sh` | `test_array_task_i_scores_model_i_even_when_resubmitted_alone`; a real single-index resume |
| P33-013 | a hardware-BLOCKED test made the runner exit non-zero, so `set -e` stopped `cpu_tests` after its first suite; the exit status was a count, which wraps at 256 | the Phase 3.2 and Phase 3 suites never run on Sol | exit codes 0 / 1 / 5; `--cpu-node` | a CPU-node simulation: all three suites run, exit 0 |
| P33-014 | fixed `.tmp` names, and `clean_temp` deleted any temp file, including another task's write in flight | interleaved files; refused resumes; spurious failed cells | `config.atomic_write_text` (mkstemp, fsync, replace); only stale temp files are cleaned | `test_concurrent_writers_never_share_a_temp_file` (the old scheme failed 5 of 5 trials) |
| P33-015 | the source was compared with the freeze only at unlock; materials and model pins never | held-out cells scored by code edited after the unlock, with no refusal | `frozen_drift` (source, materials, pins) at unlock **and** on every held-out access | `test_heldout_access_refuses_if_source_changes_after_unlock`, `test_a_model_repinned_after_the_freeze_is_refused` |
| P33-016 | `submit.sh` exported the caller's environment, so a leftover `P33_FAKE=1` could make a GPU job use the fake scorer under a real label | fabricated numbers labelled as real | `sol.env` unsets it; only `cpu_tests` sets it | `test_test_mode_cannot_leak_into_a_real_job` |
| P33-017 | the read-only `p33 status` created `raw/shards/armb`, so a never-run Arm B became a started, EMPTY experiment | following the README, `validate` reported INCOMPLETE and `dev_freeze` exited 3 without freezing | `status` is read-only | `test_status_is_read_only_so_validate_still_passes` (the real CLI) |
| P33-018 | `prefetch` re-pinned every model to the Hub's current commit | a re-run after the freeze, and every held-out command refuses on pin drift | existing pins are kept; `--repin` is explicit | `test_prefetch_keeps_existing_pins_unless_repin` |

**Smaller fixes from the same pass:**

- reversion rows in `rule_effect.csv` are labelled `condition = rule`;
- a `dev` command on a held-out run exits 2 (the refusal code), not 1;
- the smoke run computes real-tokenizer fertility;
- the default prefetch is the 11 models the shipped configs use, not a tier that holds forbidden
  7B+ models;
- `h5.slurm` runs preflight, and smoke runs map to the `dev` group in the H5 and final-export
  jobs;
- the dead `primary.demo_pool` field is removed;
- the deviation note cited a non-existent test file; it now names `test_prereg_env.py`.

### 1.4 Deviations D1–D8 (appended to the preregistration on 2026-10-05)

| # | deviation | consequence |
|---|---|---|
| D1 | `blk` is not a clean held-out grammar family | H4's C3 is NOT TESTABLE; H4 can be supported on held-out mappings and models only |
| D2 | Qwen2.5-Coder-3B was observed before the freeze | HELDOUT-WEAKENED; never the sole basis of a held-out-model claim |
| D3 | `k*` defined exactly; the pre-freeze `k*` values withdrawn | the earlier "≈ 5–7 examples" is not evidence |
| D4 | the bootstrap fixed; pre-freeze rule-effect intervals withdrawn | all four include zero |
| D5 | the de-duplication unit is (family, lexicon) | site selection no longer depends on argument order |
| D6 | the identity baseline is constant on the eligible set | C1 is equivalent to AUROC ≥ 0.60; the exploratory `terminal_rate` baseline added |
| D7 | the fp32 output head and the length-matched control | measurement and control changes, both declared before any confirmatory run |
| D8 | the development models include the instruct twins of 0.5B and 1.5B | H4 can be developed and calibrated before the freeze |

### 1.5 Errata for the first Phase 3.3 run (`phase3_3/ERRATA.md`)

| # | erratum |
|---|---|
| E1 | **"`k*` ≈ 5–7 examples" is withdrawn.** Three verified defects: leaked demonstrations (82/120), mishandled already-correct sites (84 + 41 of 125), and mis-defined censoring (16) |
| E2 | **Rule-effect intervals corrected.** The bootstrap counted a twice-drawn template once. "3 of 4 intervals include zero" becomes "all 4" |
| E3 | **`blk` is not a held-out grammar family**, since `blk × d50s1` was scored before the freeze |
| E4 | **The old Sol scripts would not have run:** `--partition=general` is rejected, and the prefetcher instantiated full models. They were replaced by `phase3_2/sol/` |

The original Phase 3.3 documents were left in place, each with a banner pointing to the errata.

### 1.6 Bugs caught while building and rehearsing *(session record)*

These were bugs in the new code, found by its own tests or by the rehearsal before any real
run.

- **The demonstration-leak rule was too strict.** The first site's prefix equals the family's
  fixed opening, so every demonstration was flagged as a leak. A `common_opening` exemption
  fixed it. Then 0 leaking sets were found, and every site could be filled to 32 demonstrations.
- **H4 with single-class labels crashed the bootstrap.** `cluster_bootstrap` now returns None when
  the point statistic fails, and `evaluate_group` reports NOT ESTIMABLE.
- **The H4 plot stamp showed `model=n/a`.** Model and revision were added to the H4 rows, and
  model, revision and split to the power rows.
- **The CLI imported matplotlib at the top level.** The plot and report imports are now lazy, so
  scoring runs on a bare Python.
- **Arm B and H5 failed every cell with `KeyError: 'condition'`.** After the fix, the resume
  retried exactly the failed cells, and both completed. That validated failure recording and
  resume.
- **A resumed run differed from an uninterrupted one** in `program_nll`, because the fake
  tokenizer gave ids in order of first use. Content-derived ids fixed it, and resumed output is
  now byte-identical.
- **Preflight showed WARN checks as PASS.** Fixed in `_check`.
- **Test bugs:**
  - source-text checks matched comments, so they now strip comments or use the AST;
  - a fake-vocabulary token swallowed a `(`;
  - a hand value was wrong (1.25, correct 1.0);
  - the `Blocked` class differed between `__main__` and an imported runner.
- **Found while making the D9 and D10 changes (2026-10-07):**
  - a test's prevalence was 3/7 where the labels give 2/7;
  - an old split test still asserted that 7B is forbidden;
  - the power figure's ticks and legend overlapped;
  - `power_series` could mix template counts;
  - the README listed wrong names for the directories the old test runner created.

---

## 2. 2026-10-07 — the development run's analysis (D9) and model scale (D10)

`dev-20261006a` ran on Sol's A100s: 4 Qwen2.5-Coder checkpoints, 10,224 Arm A rows and
16,000 primary rows. Every claim of the second brief was reproduced from the saved files before
anything changed (AUDIT §7.2).

### 2.1 Defects in the analysis (deviation D9, before the freeze)

| ID | defect | evidence (saved data) | fix | guard |
|---|---|---|---|---|
| R1 | AP ranked tied scores by input row | the constant identity baseline's AP was 0.452 forward and 0.492 reversed (correct: the prevalence, 0.468); `length`, `program_nll` and `terminal_rate` were order-dependent too | step-wise AP over distinct scores, each tie group one threshold | 5 AP tests, plus the whole H4 path under shuffling |
| R2 | precision@k broke a tie at the boundary by input row | identity 1.5B P@10 0.4 → 0.6 reversed; token_count 0.5B 0.5 → 0.1 | the expected precision when the boundary falls inside a tie | 5 P@k tests |
| R3 | the 25 smallest-detectable-AUROC power rows held 5 distinct values, all computed with the pilot ICC | `power.csv` | one row per (template count, ICC), each with its own ICC; the pilot flagged; counts above 80 marked hypothetical | `test_power_scenarios_are_unique_and_each_uses_its_own_icc` |
| R4 | the power report showed only the ICC = 0 rows for the rule effect | `reports.py`: `x["icc"] in (rule[0]["icc"],)` | every scenario, with the design effect and effective sample size | report ↔ CSV agreement test |
| R5 | `RUN_SUMMARY` counted `reports/` before writing it | Sol's file: "reports/ — 0 files" | counted against an artifact registry (`p33/artifacts.py`), written last | a first-and-repeated-export test |
| R6 | the plot footer named one model of a "base\|instruct" pair; the first fix sorted models and revisions separately, which would have paired 3 of 4 wrongly | the figures | each model printed with its own revision (`model@revision`) | `test_figure_footer_pairs_each_model_with_its_own_revision` |
| R7 | `REPRODUCTION.md` named commands that do not exist (`dev arm-a`) and a missing `env/README.md` | the report text | the real commands; the file written | `test_reproduction_report_names_commands_that_exist` |
| R8 | the test runner used `setdefault` for its results root, so a CPU-test job under `sol.env` wrote into the **real** results root | it happened: `results/dev-status-readonly/` (fake 0.5B pair, 24 sites), dated 2026-10-06 | always a fresh temporary root | `test_tests_never_use_the_real_results_root`; a simulated CPU-test job wrote 0 files |

**How it was re-derived.** Everything was recomputed from the saved GPU measurements, without
re-scoring, as analysis revision `r1-2026-10-07-metric-corrections` (`scripts/analysis_revision.py`).

- **Inputs:** all 652 measurement inputs are byte-identical before and after.
- **Outputs:** 17 of 19 CSVs are byte-identical; 23 cells of the H4 table changed, all baseline
  AP or P@k.

### 2.2 Numbers that changed (development, exploratory)

| quantity | was | now |
|---|---|---|
| identity baseline AP / P@10 (1.5B pair) | 0.452 / 0.4 | **0.468 / 0.468**, the prevalence |
| identity baseline AP / P@10 (0.5B pair) | 0.410 / 0.3 | **0.407 / 0.407**, the prevalence |
| token_count AP (0.5B / 1.5B) | 0.431 / 0.468 | 0.416 / 0.472 |
| length AP (0.5B / 1.5B) | 0.434 / 0.437 | 0.433 / 0.457 |
| risk-score AP and P@k | 0.819 / 0.924 | **unchanged**: 852 distinct risk values per pair at full precision |
| rule-effect power at 80 templates, as reported | 0.994 (ICC = 0 only) | **0.251 at the pilot ICC (0.252)**, with every scenario shown |
| `RUN_SUMMARY` report count | 0 | 10 of 10 |

**Unchanged:** AUROC, the C1 and C2 deltas, their intervals, the Holm p-values and the
calibration. No registered criterion changed, because C1 and C2 compare AUROCs, and the
average-rank AUROC was already tie-correct.

### 2.3 Model scale (deviation D10)

**Why.** The registered gate "do not scale beyond 3B until the effect is present in `blk`" could
never be met, because of D1. A study capped at 3B cannot say whether its effect survives scale.

**What changed.** Decided after the development run, before any freeze or held-out access:

- **The size ceiling** went from 3B to 72B.
- **Ten held-out checkpoints were appended**, each a base/instruct pair:
  - Qwen2.5-Coder 7B, 14B and 32B, which with 0.5B, 1.5B and 3B make a six-size ladder;
  - DeepSeek-Coder-33B;
  - Qwen2.5-72B, on two GPUs.
- **The code gained** sharded two-GPU loading, per-task preflight with GPU-count and memory
  checks, `p33.py array-indices` and the `*_2gpu` job profiles.
- **Pre-specified analysis:** two-sided, within the ladder, per family. Its statistic was missing,
  and came later as D11 (§3).

### 2.4 Tests (2026-10-07)

- **139 passed** in the project venv.
- 135 + 4 dependency-blocked on bare Python.
- The simulated `cpu_tests.slurm`: Sol suite 138 + 1 hardware-blocked, then 36 and 54, exit 0,
  0 files in the stand-in results root.

### 2.5 Execution on Sol (2026-10-07)

| fix | why |
|---|---|
| `results/dev-status-readonly/` moved to `results/_quarantine/` | it is the fake run written by the old test runner (R8). The pins file's development revisions were checked against the job manifests |
| `env/requirements.in` lists `accelerate` | needed for two-GPU loading |
| `submit_chain.sh` runs the held-out stage one job at a time (`%1`); H5 runs only after both evaluation jobs succeed (`afterok`); Arm B and H5 get 12 h and 10 h per task | H5 derives its arms from the merged held-out Arm A, so it must not start on a partial merge |
| the Llama-3.2-1B status corrected in the docs and in D10 | access was granted on 2026-10-07, and both checkpoints were downloaded and pinned (prefetch job 64914503) |

Then the D9 re-analysis was repeated on Sol: 652 inputs identical, digest `3c3e772c66ecf51e`. The
freeze followed (job 64942745, `DEV_FREEZE.json` sha256 `b319c3fc…`), then the unlock of
`heldout-20261007a` and the held-out chain.

---

## 3. 2026-10-08 — the scale analysis (D11) and a reporting fix

| fix | detail | record |
|---|---|---|
| **D11: the D10 analysis specified and implemented** | the frozen pipeline exported only its inputs. Specified with the held-out chain running and before any outcome was examined: the Qwen2.5-Coder ladder, x = log10(size); reversion (rule condition, base and instruct separately) and the H4 AUROC; each family separately; the OLS slope with a template-cluster interval (B = 2000, seed 20261002); Holm over six slopes. It lives in `scripts/scale_analysis.py`, outside the frozen code, with 4 tests (143 in the suite) | D11; commit `8d0dcf6` |
| **D11 approved** | by the investigator, unchanged, before any held-out outcome was examined | commit `efee629` |
| **a bootstrap p of 0 reported as "< 1/B"** | "p = 0.0000" with "Holm p < 0.001" overstated the resolution: 2,000 resamples cannot resolve below 1/2000. Now "p < 0.0005, Holm p < 0.003" for the `dom` AUROC slope. Reporting only; the statistic is unchanged | commit `164ed31` |
| **"curves that wobble" in `EXPERIMENT_IN_ONE_FILE.md`** | `dom` 93–100% → **93–99%** | commit `164ed31` |
| **SSH monitoring** | the master connection dropped twice, and one command opened a fresh login that sent an unannounced Duo push. Pollers now stop instead of reconnecting, and every new login is announced first | 08 §2 |

---

## 4. 2026-10-09 — the held-out results stage

### 4.1 Operational incidents (no effect on any number)

| what | resolution |
|---|---|
| `final_export` was cancelled before its script ran (`user_env_retrieval_failed_requeued_held`) | `scontrol release 64943136`; it ran 10:23–11:20, and `validate` reported VALID |
| `git pull` on Sol refused to overwrite a regenerated `.pyc` that a later commit contains | Sol was left on the frozen commit `78b2bcd`; nothing there needed newer files |

### 4.2 Gaps in the frozen analysis, disclosed (D12)

D12 disclosed three gaps. Doc 08 §1 added two more problems found the same day.

| # | gap | how it was handled on 2026-10-09 | fixed in Phase 4 |
|---|---|---|---|
| 1 | H4 calibration of the 8 pairs without frozen parameters was in-sample | calibration claimed for the two frozen pairs only | F1 |
| 2 | H5's registered interval test was not implemented | H5 reported as not supported on the descriptive evidence (43/100 cells, mean −0.41) | F2 |
| 3 | the D10 scale analysis was not in the frozen code | closed by D11 (§3) | F3 = D11 |
| 4 | the H5 per-symbol metric counts all sites in a cell | disclosed, with the worked cell (repaired 29 → 36, control 61 → 13) | F4 |
| 5 | Arm B's extraction kept a same-line "Request:" | disclosed as a bound: accuracy 9.6% → at most 9.9% | F5 |

### 4.3 Claims in the explained docs corrected after checking them against the data

Each stated number was recomputed from the run's files before it was trusted. These are the
claims that failed the check.

- **When:** mostly while the held-out docs were being written (2026-10-09). The two dated
  2026-10-07 were in the pre-run guides.
- **What changed:** only the docs. No measured or exported number changed.

| when, where | was | now | why |
|---|---|---|---|
| 2026-10-07, D9 and the pre-run guides | "852 distinct values per pair" | 852 distinct **at full precision**; the CSV's 6-digit rounding merges two of the 1.5B values | the CSV shows 851 for 1.5B; full precision confirmed 852 |
| 2026-10-07, pre-run guides 00 and 07 | "138 tests pass in Sol's environment" | "pass **locally** (not yet re-run on Sol since the 2026-10-07 changes)"; later 139 | they had been run locally only |
| 2026-10-09, held-out 00 | "43.7% of sites have a multi-token first divergence ("merged")" | "at 43.7% of sites the candidate's first characters merge into the prompt's last token when tokenized ("merged"). Scoring from the first divergent token handles this" | "merged" is a tokenization event at the prompt boundary, not a long divergence |
| 2026-10-09, held-out 00 | Brier of the 8 in-sample pairs "0.074–0.194" | **0.089–0.194** | 0.074 is the Qwen2.5-Coder-1.5B `dom` development pair |
| 2026-10-09, held-out 02 (Arm B worked example) | "390 programs (78 templates × 5 lexicons)" | "390 programs, one per template per lexicon (74 + 76 + 80 + 80 + 80 templates)" | the lexicons offer different numbers of templates |
| 2026-10-09, held-out 02 | code links `../sol/src/...` | `../src/...` | one level too deep; the link checker then found 0 broken links |
| 2026-10-09, held-out 03 §11 | a local re-export of the held-out run works | every number can be recomputed locally from the exported CSVs (the D11 script reproduces Sol's slope tables exactly), but the pipeline's held-out commands refuse locally by design | tested: `p33.py status` raised `SplitViolation`, because `HELDOUT_UNLOCK.json` binds the unlock to the freeze at its Sol path |
| 2026-10-09, held-out 05 | "small car ~46% wrong turns" | **~44%** | recomputed for the 0.5B models |
| 2026-10-09, held-out 05 | "the wrong turns rise from ~48% to ~54%" without the dictionary | **~49% to ~55%** "(the average over all drivers)" | recomputed |
| 2026-10-09, held-out 07 Q8 | "The role-level baseline beats nothing in 4 of 20 groups" | "In 4 of the 20 groups, the site-level score does *not* significantly beat the role-level baseline (the interval includes 0)" | the question stated the result backwards |
| 2026-10-09, paper-figure captions | "the first-divergent-token margin" | "the log-probability of the correct spelling minus that of the familiar one, scored from the first token where they differ" | the old phrase reads as one token; the margin sums the candidate's tokens from the first divergence |
| 2026-10-09, paper-figure caption A4 | "Reversions are mostly confident, not near-ties" | "Margins are spread widely on both sides of zero" | the title now states what the figure shows |

**Also corrected, with no record of the exact text:** the phrasing about the 0.5B pair and the
role-level baseline. The current statement (00 §3) is "It beats even the role-level one in
20/20 point estimates and 16/20 intervals; the exceptions are 0.5B and 7B."

### 4.4 The paper figures (replacing the messy frozen plots for the paper)

**Problem.** The frozen `plots/` are diagnostic dumps of the frozen code:

- up to 42 overlapping series in one figure;
- a provenance stamp on each figure;
- two figures tens of thousands of pixels tall.

They are registered outputs, so they could not be edited.

**Fix.** `phase3_2/sol/scripts/paper_figures.py` (outside the frozen code) draws 10 figures and
16 tables into `analysis_addenda/paper_figures/`.

- **The figures:** one message per figure, the numbers in tables instead of on the plot,
  colour-blind-safe colours, and the grammar families never pooled.
- **Eight checks before drawing.** The script refuses to draw unless what it recomputes equals
  the frozen export:
  - the freeze;
  - 420 rule effects;
  - 840 reversion counts;
  - 20 AUROC groups;
  - 36 D11 values with their intervals;
  - 42 KM medians;
  - the Arm B hurdle counts;
  - the frozen calibration.

**Two fixes inside it:**

- **The rule-effect estimand.** The first version pooled the rule effect over all sites. The
  results docs average the per-lexicon means, each lexicon weighing the same. The figure now does
  the same, with one template resample applied to every lexicon at once. It is checked against
  the export's per-lexicon means in all 420 cells.
- **Markdown tables.** A table header containing "|" ("old spelling | reached") broke the
  Markdown tables. It was renamed and escaped.

### 4.5 Exploratory checks, and the three wording corrections they forced

`scripts/exploratory_checks.py` (post hoc, written on 2026-10-09) ran four checks:

- inheritance against shared site difficulty;
- the role ordering at matched examples;
- adaptation by remap density and role;
- the size of the wobbles.

They made three statements in the docs more precise:

| statement | was | now | evidence |
|---|---|---|---|
| examples to switch | "the median site switches after about two examples" | "**among sites that switch**, about two; a lasting switch, about eight" | 2.06 and 8 are medians among crossers and holders; the KM medians are the endpoint |
| role ordering | "the role ordering matches the margins" | "matches the margins **at the same number of worked examples** (4); at 0 examples the roles are about equal" | `roles_by_rung.csv` |
| wobble | "~97% of curves wobble" | "**31% of switched sites fall back later, by a median of −0.76 nats**; 59% of curves drop by more than 1 nat at some step" | `wobble_size.csv`: the frozen `nonmonotone` flag counts any decrease, however small |

### 4.6 Git, the laptop and Sol made consistent

The goal was for the repository to hold exactly what Sol holds, checked file by file with
checksums. The commits are `1e52d1d` and `1750947`.

| problem | fix |
|---|---|
| 27 files of the development run's export differed between laptop and Sol (Sol's later export carries the corrected Llama status; the CSV differed by floating-point noise) | Sol's copies taken; the laptop's are kept in history at `c007c3d`, and each copy matches its own revision record (`SOL_SYNC_2026-10-09.md`) |
| the setup, prefetch and smoke folders, the post-processing scripts and Sol's environment lock existed only on Sol | copied into `phase3_3/sol_results/`, `phase3_3/sol_experiment_root/` and `env/requirements.lock.sol.txt` |
| four held-out files exceed GitHub's 100 MB limit | committed gzipped (`gzip -9 -n`), the originals ignored, both hashes in `LARGE_FILES.sha256`; `restore_large_files.sh` restores and verifies them |
| `.gitignore` had a fused line (`.DS_Storeprogress_summare/`) | split into its two entries |
| `results/_quarantine/` (the fake run) | deliberately **not** copied, and documented as such |

---

## 5. The test suite over time

| date | Phase 3.3 suite | what was added |
|---|---|---|
| 2026-10-05 | 112 | the new pipeline |
| 2026-10-07 | 139 | D9 corrections (20), model scale (6), the results-root guard |
| 2026-10-08 | 143 | D11 (4) |
| 2026-10-09 | 147 | the paper figures (4) |
| 2026-10-21 | 147 + 6 | Phase 4 step 0, in `phase4/tests/` |
