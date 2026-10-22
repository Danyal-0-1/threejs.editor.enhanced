# Fixes made before Phase 4

Everything that was found wrong in Phase 3.3, and fixed, before Phase 4's new work begins.

- **Phase 4's own step 0** (2026-10-21) corrected the open problems of the held-out analysis.
- **The history before it** runs from the audit of the inherited pipeline (2026-10-05) to the
  held-out results (2026-10-09).

| file | what it explains |
|---|---|
| [`01_phase4_step0_fixes.md`](01_phase4_step0_fixes.md) | **the six fixes of 2026-10-21** (F1–F6): each problem, its evidence, the method with code links, the checks, the results and what they mean; plus that day's documentation fixes |
| [`02_fixes_during_phase3_3.md`](02_fixes_during_phase3_3.md) | **every fix from 2026-10-05 to 2026-10-09**: the audit's defects (P33-001 to P33-018), the development-run corrections (R1–R8), deviations D1–D12, errata E1–E4, corrected doc claims, the paper figures, and git ↔ Sol consistency |
| [`03_doc_changes_before_after.md`](03_doc_changes_before_after.md) | **the exact before and after text** of all 42 documentation changes of 2026-10-21, file by file, with the reason for each file |

**The rules every fix followed:**

- **Before the freeze:** a fix may change the analysis, if it is recorded as a dated deviation.
- **After the freeze:** a fix is post hoc. It runs outside the frozen code, it first reproduces the
  frozen numbers it corrects, and it is labelled post hoc.
- **Always:**
  - no frozen number is overwritten;
  - the preregistration's frozen text stays byte-identical (sha256 `a0146494…`, checked by
    `tests/test_prereg_env.py`).

---

## Every fix, in one index

### 2026-10-21 — Phase 4, step 0 (post hoc, deviation D13) → [01](01_phase4_step0_fixes.md)

| ID | problem | fix | result |
|---|---|---|---|
| F1 | H4 calibration of the 8 pairs without frozen parameters was computed in-sample (slope exactly 1.00) | template-grouped 5-fold cross-fitting, and transfer from the other grammar family | cross-fitted ECE 0.016–0.105, slopes 0.97–0.99; other-grammar ECE 0.026–0.137, slopes 0.75–1.33 |
| F2 | H5's registered interval test was never run | the test exactly as §3 registers it, each family separately | `dom` −0.77 [−1.96, +0.40], `blk` −0.04 [−1.19, +1.12]: **H5 not supported**, now by its own test |
| F3 | the D10 scale analysis was missing from the frozen code | — | fixed on 2026-10-08 by D11 |
| F4 | H5's per-symbol metric mixes repaired and control sites | an exact split of the metric | at the repaired sites, targeted beats random (`dom` +0.79, `blk` +2.21; intervals above 0); the control sites decide the sign. A hypothesis for Phase 4 |
| F5 | Arm B's extractor kept a same-line "Request:" continuation | the cut, then the frozen evaluator; sites re-observed | 63 generations change; task accuracy 9.6% → 9.9%; 0 of 205 site outcomes change |
| F6 | open item: does one role carry the H4 prediction? | AUROC within each role, with intervals | 0.63–0.98; interval above 0.5 in 60 of 60 groups |
| D13 | the corrections above need a record | appended to the preregistration, dated, with their scientific consequence | no registered verdict changes |
| docs | 6 errors and stale statements in `heldout_results_explained/` ("two gaps" listing three; "Holm p = 0.001"; "3 random seeds", really 5; unqualified wobble, "2 → 8" and Q14) | fixed; every doc gained the Phase 4 results, labelled post hoc | [03](03_doc_changes_before_after.md): 42 changes in 13 files |

### 2026-10-09 — the held-out results stage → [02 §4](02_fixes_during_phase3_3.md#4-2026-10-09--the-held-out-results-stage)

| ID | problem | fix |
|---|---|---|
| D12 | three gaps in the frozen analysis: in-sample calibration, the missing H5 test, the missing D10 analysis | disclosed, not patched; corrected later by F1–F3 |
| 08 §1 #4–5 | the H5 metric mixes sites; the Arm B extraction artifact | disclosed; corrected later by F4 and F5 |
| ops | `final_export` held by Slurm; `git pull` on Sol refused a `.pyc` | `scontrol release`; Sol left on the frozen commit |
| doc claims | 13 numbers or claims in the docs and figure captions failed a recheck, two of them already on 2026-10-07 (for example "78 templates × 5", a Brier range, "small car ~46%", the Q8 question stated backwards, the margin wording) | each corrected; the before and after are in 02 §4.3 |
| figures | the frozen `plots/` were not publishable (up to 42 overlapping series, stamps, giant images) | `scripts/paper_figures.py`: 10 figures and 16 tables, checked 8 ways against the frozen export; the rule-effect estimand aligned with the docs |
| wording | three statements were stronger than the data (first switch "≈ 2"; the role ordering; "~97% wobble") | qualified after the exploratory checks |
| sync | the laptop, git and Sol differed (27 dev-run files, Sol-only folders, 4 files over 100 MB, a fused `.gitignore` line) | made identical, file by file with checksums; large files gzipped with a restore script; the fake `_quarantine/` run excluded |

### 2026-10-08 — the held-out chain running → [02 §3](02_fixes_during_phase3_3.md#3-2026-10-08--the-scale-analysis-d11-and-a-reporting-fix)

| ID | problem | fix |
|---|---|---|
| D11 | D10 pre-specified a scale analysis, but no statistic and no code | specified, implemented outside the frozen code (`scripts/scale_analysis.py`), approved before any held-out outcome was examined |
| p-floor | a bootstrap p of 0 printed as "0.0000" | printed as "< 1/B" (and Holm as "< m/B") |
| wobble range | "93–100%" of `dom` curves | 93–99% |
| SSH | a dropped connection led to an unannounced Duo push | pollers stop instead of reconnecting; logins are announced |

### 2026-10-07 — the development run's analysis and model scale → [02 §2](02_fixes_during_phase3_3.md#2-2026-10-07--the-development-runs-analysis-d9-and-model-scale-d10)

| ID | problem | fix |
|---|---|---|
| R1 | AP ranked tied scores by input row | tie-correct AP (D9) |
| R2 | precision@k broke boundary ties by input row | expected precision within the tie (D9) |
| R3 | the power rows all used the pilot ICC | one row per (T, ICC) scenario (D9) |
| R4 | the power report showed only ICC = 0 for the rule effect | every scenario shown; the real power is 0.251, not 0.994 (D9) |
| R5 | `RUN_SUMMARY` counted reports before writing them | counted against an artifact registry, written last |
| R6 | plot footers paired models and revisions wrongly | `model@revision` per model, with a test |
| R7 | `REPRODUCTION.md` named commands that do not exist | the real commands |
| R8 | the test runner could write into the real results root, and on Sol it did | always a temporary root; the fake run quarantined |
| D9 | the corrections above, re-derived from the saved measurements | 652 inputs byte-identical; in the H4 table only baseline AP and P@k change |
| D10 | a 3B cap that D1 made impossible to lift | models up to 72B: 10 held-out checkpoints, two-GPU loading |
| exec | the chain, `accelerate`, the Llama status | one job at a time, H5 gated on `afterok`; `accelerate` added; docs and D10 corrected |

### 2026-10-05 — the audit, before any Sol job → [02 §1](02_fixes_during_phase3_3.md#1-2026-10-05--the-audit-before-any-sol-job)

| ID | problem | fix |
|---|---|---|
| P33-001 | a scorer path returned 0.0, including for one side of a prefix pair | explicit errors; the old scorer raises |
| P33-002 | bf16 margins quantised, and the outcome is a sign | an fp32 output head (D7) |
| P33-003 | site selection depended on the lexicon order | de-duplication within (family, lexicon) (D5) |
| P33-004 | the balance check ignored cells | expected cells come from the materials |
| P33-005 | the bootstrap dropped a twice-drawn cluster's weight | tagged draws (D4) |
| P33-006 | every site saw the first lexicon's table | a per-site prompt bundle, checked |
| P33-007 | `k*` and censoring were wrong | the exact definition, and Kaplan–Meier (D3) |
| P33-008 | 82/120 sites saw their own target among the demonstrations | a leak-free ladder; a leak raises |
| P33-009 | fertility came from one model | per tokenizer |
| P33-010 | no provenance; one JSON at job end | job manifests, atomic shards |
| P33-011 | the tests rewrote 9 tracked lexicon files | an idempotent, atomic writer |
| P33-012 | a single-index resubmission scored no model | task *i* → model *i* |
| P33-013 | one blocked test stopped the CPU-test job | exit codes 0/1/5; all suites run |
| P33-014 | temp-file names collided across tasks | mkstemp + fsync + replace |
| P33-015 | drift was checked only at unlock | checked on every held-out access |
| P33-016 | the fake scorer could leak into a real job | `P33_FAKE` unset in real jobs |
| P33-017 | the read-only `status` made a complete run look incomplete | `status` is read-only |
| P33-018 | prefetch re-pinned models | pins kept unless `--repin` |
| D1–D8 | `blk` inspected; 3B observed; `k*`; the bootstrap; de-duplication; the constant identity baseline; fp32 and the length-matched control; instruct twins | appended to the preregistration, each with its consequence |
| E1–E4 | the first Phase 3.3 run's `k*` ≈ 5–7, its rule-effect intervals, `blk` as held-out, its Sol scripts | withdrawn or corrected in `phase3_3/ERRATA.md` |
| build | bugs caught by the new tests and the rehearsal (a too-strict leak rule, a bootstrap crash on one class, a resume that differed by a byte, and more) | fixed before any real run (02 §1.6) |

---

## How to check the Phase 4 fixes yourself

```bash
# from the repository root, with the project venv
bash phase3_3/sol_results/restore_large_files.sh heldout-20261007a   # after a fresh clone
run/.venv/bin/python phase4/scripts/fix_heldout_problems.py         # about 40 s; refuses on any mismatch
run/.venv/bin/python phase4/tests/run_tests.py -v                   # 6 tests
run/.venv/bin/python phase3_2/sol/tests/run_tests.py                # the Phase 3.3 suite (147)
```

The script prints its six checks: 20 calibration groups, 700 H5 arm rows, 7,800 Arm B
generations, 205 re-observed sites, 60 per-role AUROCs, and the split. It writes only to
`phase3_3/sol_results/heldout-20261007a/analysis_addenda/phase4_fixes/`.
