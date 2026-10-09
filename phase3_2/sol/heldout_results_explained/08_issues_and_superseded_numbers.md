# 08 — Issues found at the results stage, and superseded numbers

> Everything here was found **after** the held-out results existed. None of it changes a
> registered verdict. All of it is disclosed, not patched. Deviation D12 in
> `phase3_2/PREREGISTRATION.md` records items 1–3.

---

## 1. Gaps in the frozen analysis

| # | gap | evidence | affects | does **not** affect |
|---|---|---|---|---|
| 1 | **H4 calibration for pairs without frozen parameters.** The freeze fitted Platt calibration only for the two development pairs. For the other 8, `export.py` (310–340) writes `calibrated_p = σ(risk)` labelled `DEV_FREEZE`, and `evaluate_group` refits calibration on the held-out rows before computing ECE, Brier and the slope | calibration slope exactly 1.00 for those 8 pairs (`test_calibration_of_a_fitted_model_is_identity` explains why) | `calibrated_p`, ECE, Brier, slope and intercept for 8 pairs | AUROC, AP, P@k, deltas, C1/C2/C3, within-lexicon AUROC; calibration of the 0.5B and 1.5B pairs |
| 2 | **H5's registered interval test was not implemented.** The export lists per-arm results but not "targeted − random, with an interval excluding 0" | `reports/HYPOTHESIS_RESULTS.md` has per-arm rows and no verdict | the formal H5 decision | the descriptive outcome: targeted > random in 43/100 cells, mean −0.41. That already contradicts H5, so no post-hoc test is presented as confirmatory |
| 3 | **The D10 scale analysis was not in the frozen code** | no slope computation in `export.py` | — | closed by D11 (specified and approved before outcomes were seen) and run after the export |
| 4 | **The H5 per-symbol metric counts all sites in the cell**, not only the repaired ones | worked cell: repaired 29 → 36, control 61 → 13 ([02 §6](02_mathematics_and_statistics.md)) | the interpretation of "per changed symbol" | the counts themselves |
| 5 | **Arm B extraction keeps a same-line "Request:" continuation** | 63 of 3,006 PARSE_FAILs. Cut before "Request:" (exploratory), 58 parse and 27 equal the target | task accuracy is understated by at most 27 / 7,800 (9.6% → ≤ 9.9%) | reach and reversion given reach (prefix-based) |

**What to say in the paper.**

- Report calibration for the two frozen pairs only.
- State that H5 is not supported descriptively, and that its registered interval test was not
  implemented.
- Describe D11 as specified after the freeze but before outcomes were seen.
- Footnote the Arm B extraction effect.

---

## 2. Operational incidents (no effect on any number)

| when | what | resolution |
|---|---|---|
| 2026-10-06 | the old test runner wrote a fake run (`dev-status-readonly/`) into the real results root | moved to `results/_quarantine/`; runner fixed (always a temporary root) |
| 2026-10-08, twice | the SSH master connection dropped | pollers stopped instead of reconnecting, so no surprise Duo pushes |
| 2026-10-09 10:16 | `final_export` was cancelled before its script ran (`user_env_retrieval_failed_requeued_held`) | `scontrol release`; ran 10:23–11:20, VALID |
| 2026-10-09 | `git pull` on Sol refused to overwrite a regenerated `.pyc` that a later commit contains | Sol left on the frozen `78b2bcd`; nothing needed newer files there |

---

## 3. Superseded numbers

| quantity | earlier | now (held-out) | why it changed |
|---|---|---|---|
| "examples to switch" | ~6 (Phase 3.3 headline, withdrawn: leaked demonstrations) | KM median 1.4–4.6 (`dom`), 3.3–11.6 (`blk`); first switch ≈ 2, stable ≈ 8 | leak-free ladder, censoring, held-out mappings |
| development `k*` medians | 3.6–6.2 (4 models, `dom`) | see above | different mappings (incl. `d75`) and more models |
| rule effect | +0.08…+0.36; 1/32 intervals > 0 (development) | +0.16…+0.62; 263/420 intervals > 0 | larger cells, `d75` lexicons; development power (0.25 pooled) was conservative |
| H4 AUROC, 0.5B / 1.5B pairs | 0.869 / 0.935 (development) | 0.888 / 0.963 (`dom`), 0.836 / 0.920 (`blk`) | replicated on new mappings |
| projected compute | ~100 A100 GPU-hours | **40.8** | large models faster than the pessimistic scaling |
| preview (2026-10-08, frozen code on a scratch copy) | Arm A, extinction, H4, D11 | **identical** in the final export | same inputs, same code |
| D11 `dom` AUROC p | "Holm p < 0.001" (chat, 2026-10-08) | **p < 0.0005, Holm p < 0.003** | the bootstrap's resolution is 1/2000; the script now prints "< 1/B" |

---

## 4. What is *not* an issue (checked)

- **Measurement:** 0 exact-zero margins, 0 ties, 0 exclusions in Arm A; 0 failed cells
  anywhere.
- **Leakage:** demonstration leakage is impossible by construction (`demos.audit` raises).
- **Repair proofs:** all 35 IR proofs passed, each over 284 programs.
- **Local vs Sol:** byte-identical on the merged data, the H4 table and the hypothesis report.
  The D11 slopes, recomputed locally, are identical.
