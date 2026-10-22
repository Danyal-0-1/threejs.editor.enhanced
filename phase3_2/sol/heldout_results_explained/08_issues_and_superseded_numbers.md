# 08 — Issues found at the results stage, and superseded numbers

> Everything here was found **after** the held-out results existed. None of it changes a
> registered verdict. All of it was disclosed (deviation D12 records items 1–3).
>
> **On 2026-10-21 (Phase 4, step 0) every open item was corrected post hoc**, outside the frozen
> code and without changing a frozen number (deviation D13). See §5, and
> [`phase4/fixes_before_phase4/`](../../../phase4/fixes_before_phase4/README.md) for the detail.

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
| "examples to switch" | ~6 (Phase 3.3 headline, withdrawn: leaked demonstrations) | KM median 1.4–4.6 (`dom`), 3.3–11.6 (`blk`); among sites that switch, first switch ≈ 2 and lasting switch ≈ 8 | leak-free ladder, censoring, held-out mappings |
| development `k*` medians | 3.6–6.2 (4 models, `dom`) | see above | different mappings (incl. `d75`) and more models |
| rule effect | +0.08…+0.36; 1/32 intervals > 0 (development) | +0.16…+0.62; 263/420 intervals > 0 | larger cells, `d75` lexicons; development power (0.25 pooled) was conservative |
| H4 AUROC, 0.5B / 1.5B pairs | 0.869 / 0.935 (development) | 0.888 / 0.963 (`dom`), 0.836 / 0.920 (`blk`) | replicated on new mappings |
| projected compute | ~100 A100 GPU-hours | **40.8** | large models faster than the pessimistic scaling |
| preview (2026-10-08, frozen code on a scratch copy) | Arm A, extinction, H4, D11 | **identical** in the final export | same inputs, same code |
| D11 `dom` AUROC p | "Holm p < 0.001" (chat, 2026-10-08) | **p < 0.0005, Holm p < 0.003** | the bootstrap's resolution is 1/2000; the script now prints "< 1/B" |
| Arm B task accuracy | 747 / 7,800 = 9.6% (frozen extraction) | **774 / 7,800 = 9.9%** beside the frozen value (post hoc) | a same-line "Request:" continuation was cut (§5, F5) |
| basis of the H5 verdict | descriptive (43/100 cells; mean −0.41) | **the registered test**, run post hoc: `dom` −0.77 [−1.96, +0.40], `blk` −0.04 [−1.19, +1.12] | §5, F2 |
| calibration of the 8 pairs without frozen parameters | in-sample ECE 0.017–0.111, slope exactly 1.00 | **cross-fitted ECE 0.016–0.105, slopes 0.97–0.99** (post hoc) | §5, F1 |
| random arms of H5 (00 §9) | "3 random seeds' worth of random choices" | **5 seeds** of 3 random roles each | a wording error in 00 (the run config has seeds 1–5) |
| figures for the paper | `plots/` (frozen diagnostics: up to 42 overlapping series, a stamp on each, two figures tens of thousands of pixels tall) | `analysis_addenda/paper_figures/`: 10 figures, 16 tables, draft captions | `plots/` stays as registered output; the new figures restate the frozen numbers and are checked against them |
| "examples to switch" wording | "the median site switches after about two examples" (06, abstract draft) | "**among sites that switch**, about two; a lasting switch, about eight" | 2.06 and 8 are medians among crossers and holders; the KM medians are the endpoint |
| role-ordering wording | "the role ordering matches the margins" (06, objections) | "matches the margins **at the same number of worked examples** (4); at 0 examples the roles are about equal" | exploratory check, [09 §3.2](09_conclusions_claim_strength_and_venues.md) |
| "wobble" wording | "~97% of curves wobble" (06, 05) | "**31% of switched sites fall back later, by a median of −0.76 nats**; 59% of curves drop by > 1 nat at some step" | the frozen `nonmonotone` flag counts any decrease, however small ([09 §3.3](09_conclusions_claim_strength_and_venues.md)) |

---

## 4. What is *not* an issue (checked)

- **Measurement:** 0 exact-zero margins, 0 ties, 0 exclusions in Arm A; 0 failed cells
  anywhere.
- **Leakage:** demonstration leakage is impossible by construction (`demos.audit` raises).
- **Repair proofs:** all 35 IR proofs passed, each over 284 programs.
- **Local vs Sol:** byte-identical on the merged data, the H4 table and the hypothesis report.
  The D11 slopes, recomputed locally, are identical.
- **Paper figures:** `scripts/paper_figures.py` recomputes what it draws from the CSVs and
  refuses unless it equals the frozen export: the 420 per-lexicon rule effects, the 840
  per-lexicon, per-role reversion counts, the 60 AUROCs, the 42 KM medians, the Arm B counts,
  the frozen calibration, and the 36 D11 ladder values with their intervals, digit for digit.

---

## 5. Fixed in Phase 4 (2026-10-21, post hoc, deviation D13)

These were made by `phase4/scripts/fix_heldout_problems.py`; the output is in
`analysis_addenda/phase4_fixes/`. Each fix first reproduces the frozen numbers it corrects, and
the script refuses otherwise.

| # | item (§1) | what was done | result |
|---|---|---|---|
| F1 | 1. calibration of 8 pairs | template-grouped 5-fold cross-fitting, and transfer from the other grammar family | cross-fitted ECE 0.016–0.105, slopes 0.97–0.99; other-grammar ECE 0.026–0.137, slopes 0.75–1.33 |
| F2 | 2. H5's registered test | implemented as §3 states it, each family separately | `dom` −0.77 [−1.96, +0.40], `blk` −0.04 [−1.19, +1.12]: **not supported** |
| F3 | 3. D10 scale analysis | — | fixed before Phase 4 by D11 |
| F4 | 4. H5 metric mixes sites | exact repaired/control split | at repaired sites targeted beats random: `dom` +0.79 [+0.06, +1.53], `blk` +2.21 [+1.39, +3.02]; the control sites decide the sign |
| F5 | 5. Arm B extraction | cut the same-line "Request:", re-evaluate with the frozen evaluator, re-observe sites | 63 generations change; accuracy 9.6% → 9.9%; 0 of 205 site outcomes change |
| F6 | open item (06 §10): H4 per role | AUROC within each role | 0.63–0.98; interval above 0.5 in 60/60 groups |

**Documentation fixes in this folder, made the same day:**

- 00 said "two gaps" while listing three; now three, plus the Phase 4 status.
- 00 gave "Holm p = 0.001"; now "≤ 0.001", because 0.0009995 is a floor.
- 00 said the random H5 arm used 3 seeds; it used 5.
- 01 gave the unqualified "92.8–99.5% of curves wobble" and an unqualified "2 → 8"; both now
  carry their sizes and "among sites that switch".
- 07 Q14 now carries "among …".
- 02, 05, 06, 09 and 10 now include the Phase 4 results.

Every change is listed with its before and after text in `phase4/fixes_before_phase4/`.

