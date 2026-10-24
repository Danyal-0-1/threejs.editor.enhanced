# Phase 4

Phase 3.3 ended with a complete, validated held-out run on ASU Sol (`heldout-20261007a`: 21
models, 0 failed cells). Its results and its open problems are explained in
[`explanations/phase3_3/heldout_results_explained/`](../explanations/phase3_3/heldout_results_explained/00_complete_results.md).

Phase 4 starts by closing every open problem that can be closed with the data already in hand.
Only then does it take on new questions.

| step | status | what |
|---|---|---|
| **0. Fix what Phase 3.3 left open** | **done, 2026-10-21** | five post-hoc corrections of the held-out analysis and one open analysis item, with every doc fixed and every change explained ([`explanations/phase4/fixes_before_phase4/`](../explanations/phase4/fixes_before_phase4/README.md)) |
| **0b. Give the Phase 4 pipeline its own settings** | **done, 2026-10-22** | `code/` uses its own experiment folder and `P4_*` names, its own preregistration and split, and the `p4/1` label (see [`code/README.md`](code/README.md)) |
| 1. Plan and preregister Phase 4 | **in progress** | [`PREREGISTRATION.md`](PREREGISTRATION.md) is a draft. The freeze refuses until it is registered |
| 2. Add the ASU RC API models | **done, 2026-10-22** | 52 listed, 42 probed; 36 serve Arm A and Arm B by Phase 3.3's protocol and are in the registry, with a scorer. Their role is decided in the preregistration: [`code/VOYAGER.md`](code/VOYAGER.md) |
| 3. First development run with nine of them | **done, 2026-10-23** (exploratory) | `dev-20261023a`: on exactly Phase 3.3's held-out cells; results and figures in [`results/`](results/README.md), explained in [`explanations/phase4/api_models_results_explained/`](../explanations/phase4/api_models_results_explained/00_complete_results.md) |

---

## Layout

| path | what |
|---|---|
| [`code/`](code/README.md) | **the pipeline for the next experiment:** a verified copy of the Phase 3.3 pipeline, organized by stage, with the language files, configs, Sol jobs and tests. Phase 4's changes go here |
| [`scripts/fix_heldout_problems.py`](scripts/fix_heldout_problems.py) | step 0's analysis: the post-hoc corrections F1–F6 (CPU only, about 40 s). It imports the frozen Phase 3.3 code on purpose |
| [`tests/`](tests/) | 6 tests for it, run by the Phase 3.3 test runner |

**Explanations** are kept with every other phase's, in
[`explanations/phase4/fixes_before_phase4/`](../explanations/phase4/fixes_before_phase4/README.md): every fix made
before Phase 4 proper, explained in detail (step 0 of Phase 4, and the full history of fixes during
Phase 3.3). It was moved there from `phase4/fixes_before_phase4/` on 2026-10-22 ([`MOVES.md`](../MOVES.md)).

**Outputs** go next to the run they analyse:
`phase3_3/sol_results/heldout-20261007a/analysis_addenda/phase4_fixes/` (`PHASE4_FIXES.md`
and one CSV per fix).

```bash
# from the repository root, with the project venv
run/.venv/bin/python phase4/scripts/fix_heldout_problems.py     # writes analysis_addenda/phase4_fixes/
run/.venv/bin/python phase4/tests/run_tests.py -v               # 6 tests
# after a fresh clone, restore the four gzipped files first:
bash phase3_3/sol_results/restore_large_files.sh heldout-20261007a
```

---

## Step 0 in one table

All six fixes are **post hoc**: made after the held-out outcomes were known, outside the frozen
code, and recorded as deviation D13 in `phase3_2/PREREGISTRATION.md`. **No registered verdict
changed.**

| fix | problem | result |
|---|---|---|
| F1 | H4 calibration of 8 pairs was computed in-sample | out of sample: cross-fitted ECE 0.016–0.105, slopes 0.97–0.99 |
| F2 | H5's registered test was never run | `dom` −0.77 [−1.96, +0.40], `blk` −0.04 [−1.19, +1.12]: **H5 not supported**, now by its own test |
| F3 | the D10 scale analysis was missing | fixed earlier, by D11 |
| F4 | H5's metric mixes repaired and control sites | at the repaired sites, targeted beats random (`dom` +0.79, `blk` +2.21); the control sites decide the sign. A new hypothesis |
| F5 | Arm B's extractor kept a same-line "Request:" | 63 generations change; task accuracy 9.6% → 9.9%; reach unchanged |
| F6 | open item: does one role carry H4? | no: AUROC 0.63–0.98 within each role, 60/60 intervals above 0.5 |

The details, with every number, check and changed sentence, are in
[`explanations/phase4/fixes_before_phase4/01_phase4_step0_fixes.md`](../explanations/phase4/fixes_before_phase4/01_phase4_step0_fixes.md).

---

## Candidate Phase 4 studies (a plan to discuss, not yet registered)

Each needs new model runs on Sol, so each needs its own preregistration first, as in Phase 3.3.

| # | study | the question it answers | where it comes from |
|---|---|---|---|
| 1 | **H5 again, with a repaired-site metric and frequency-aware targeting** | Does targeting the riskiest roles beat random where the repair acts? F4 suggests yes; only a preregistered test can say | F4; 06 §10 |
| 2 | **A second DSL, or natural respellings** | Do the findings hold beyond one permuted 3D-scene language? This is the biggest gap a reviewer will name | 09 §5 #4 |
| 3 | **Models served by the ASU RC API ("Voyager")** | Do many more models revert at reached sites (Arm B), and do their margins agree (Arm A)? 36 models can do both, up to 1T parameters. None is a base model, so no H4 or H5; 33 of 36 round their logits | 09 §5 #3; [`code/VOYAGER.md`](code/VOYAGER.md) |
| 4 | **The spelling-risk linter** | Turn H4 into a tool: score a DSL's planned spellings with an open base model, and flag the risky ones before release | H4; the standing "platform first" recommendation |
| 5 | **A small human comparison** | Do programmers slip at the same collision sites? It makes a CogSci paper possible | 09 §5 #5; [10](../explanations/phase3_3/heldout_results_explained/10_humans_and_the_brain.md) |
| 6 | **Mechanism** | Does attention to the token table predict the margin shift? | 09 §5 #6 |

**Before any of these:** write up Phase 3.3. The paper plan is in
[`06`](../explanations/phase3_3/heldout_results_explained/06_publishability_and_paper.md) and
[`09`](../explanations/phase3_3/heldout_results_explained/09_conclusions_claim_strength_and_venues.md).
The main target is ACL 2027, through the January 2027 ARR cycle.
