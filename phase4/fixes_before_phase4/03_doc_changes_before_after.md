# 03 — Every documentation change of 2026-10-21, before and after

> **What this is.** The exact text of every change made to the explained docs, the Sol
> README and the preregistration on 2026-10-21, as a diff against commit
> `1750947b` (the last commit before Phase 4). In each block, `-` lines are the text before
> and `+` lines the text after. The reasons are in [`01`](01_phase4_step0_fixes.md) (F1–F6
> and "The documentation fixes").
>
> **To regenerate the raw diff:** `git diff 1750947b -- phase3_2/sol/heldout_results_explained/ phase3_2/sol/README.md phase3_2/PREREGISTRATION.md`. Run it before these changes are
> committed, or against the commit that holds them.

**What kind of change:**

- **doc error:** a statement that was wrong, now fixed;
- **doc precision:** a statement that was true but easy to misread, now qualified;
- **F1–F6:** a result of the Phase 4 fixes, added and labelled post hoc;
- **status, pipeline, checklist, governance:** pointers that keep the docs current.

**In total:** 42 changes in 13 files, 311 lines added and 59 removed. No
frozen number was edited in any doc; every number that was added comes from
`analysis_addenda/phase4_fixes/`.

| file | changes | lines |
|---|---|---|
| [`00_complete_results.md`](#00_complete_resultsmd) | 10 | +54 / −27 |
| [`01_theory.md`](#01_theorymd) | 6 | +22 / −7 |
| [`02_mathematics_and_statistics.md`](#02_mathematics_and_statisticsmd) | 2 | +55 / −0 |
| [`03_code_and_pipeline.md`](#03_code_and_pipelinemd) | 2 | +13 / −0 |
| [`04_retyping_plan.md`](#04_retyping_planmd) | 1 | +12 / −0 |
| [`05_mental_image.md`](#05_mental_imagemd) | 1 | +12 / −0 |
| [`06_publishability_and_paper.md`](#06_publishability_and_papermd) | 6 | +17 / −11 |
| [`07_knowledge_check.md`](#07_knowledge_checkmd) | 2 | +18 / −2 |
| [`08_issues_and_superseded_numbers.md`](#08_issues_and_superseded_numbersmd) | 3 | +39 / −2 |
| [`09_conclusions_claim_strength_and_venues.md`](#09_conclusions_claim_strength_and_venuesmd) | 5 | +8 / −6 |
| [`10_humans_and_the_brain.md`](#10_humans_and_the_brainmd) | 2 | +8 / −4 |
| [`README.md`](#readmemd) | 1 | +9 / −0 |
| [`PREREGISTRATION.md`](#preregistrationmd) | 1 | +44 / −0 |

---

## 00_complete_results.md

[`phase3_2/sol/heldout_results_explained/00_complete_results.md`](../../phase3_2/sol/heldout_results_explained/00_complete_results.md): 10 changes, 54 lines added, 27 removed.

**Why:**

- **doc error:** the header said "Two gaps" while §13 listed three
- **doc error:** "Holm p = 0.001" is the bootstrap floor (0.0009995), so it is now "≤ 0.001"
- **doc error:** the H5 random arm used **5** seeds (`seeds.h5_random = [1, 2, 3, 4, 5]`), not 3
- **F2:** the H5 row now gives the registered test
- **F1:** an out-of-sample calibration bullet; "Their ECE" becomes "Their exported ECE"
- **F5:** an Arm B extraction-correction bullet
- **F4:** the repaired-site split under "H5 fails"
- **status:** §13 is rewritten from "disclosed, not corrected" to a table of each gap and its Phase 4 correction; §14 gains a row for `phase4_fixes/`

**1. § 00 — Complete results of the held-out run** (new line 20; changed)

```diff
-> - Two gaps in the frozen analysis are disclosed in §13.
+> - Three gaps in the frozen analysis are disclosed in §13. On 2026-10-21 they, and two further
+>   problems, were corrected **post hoc** in Phase 4 (deviation D13). No registered verdict
+>   changed (§13 and [`phase4/`](../../../phase4/README.md)).
```

**2. § 2. The verdicts in one table** (new line 112; changed)

```diff
-| **H4**: does the base model's margin predict where the instruct model reverts? | C1: AUROC − identity ≥ 0.10, CI > 0; C2: AUROC − length ≥ 0.05, CI > 0; Holm; each family separately | AUROC 0.76–0.96; C1 deltas +0.26…+0.46; C2 deltas +0.14…+0.49; all CIs > 0; Holm p = 0.001 | **MET in 20/20** (10 pairs × 2 families) |
+| **H4**: does the base model's margin predict where the instruct model reverts? | C1: AUROC − identity ≥ 0.10, CI > 0; C2: AUROC − length ≥ 0.05, CI > 0; Holm; each family separately | AUROC 0.76–0.96; C1 deltas +0.26…+0.46; C2 deltas +0.14…+0.49; all CIs > 0; Holm p ≤ 0.001 (the bootstrap floor, 0.0009995) | **MET in 20/20** (10 pairs × 2 families) |
```

**3. § 2. The verdicts in one table** (new line 116; changed)

```diff
-| **H5**: targeted repair beats random per changed symbol | interval excluding 0; control sites worsen ≤ 0.02 | targeted beats the mean of random in **43/100** cells; mean difference **−0.41** per symbol | **NOT SUPPORTED** (descriptive; the interval test was never implemented, §13) |
+| **H5**: targeted repair beats random per changed symbol | interval excluding 0; control sites worsen ≤ 0.02 | targeted beats the mean of random in **43/100** cells; mean difference **−0.41** per symbol | **NOT SUPPORTED**. The frozen export gave this descriptively. The registered interval test, run post hoc in Phase 4, gives `dom` −0.77 [−1.96, +0.40] and `blk` −0.04 [−1.19, +1.12] (§13) |
```

**4. § 3. H4: the base model predicts where its instruct twin reverts** (new line 182; changed)

```diff
-- **The other 8 pairs have no frozen calibration.** Their ECE (0.017–0.111) and Brier
+- **The other 8 pairs have no frozen calibration.** Their exported ECE (0.017–0.111) and Brier
```

**5. § 3. H4: the base model predicts where its instruct twin reverts** (new line 184; added)

```diff
+- **Out of sample (Phase 4, post hoc).** Template-grouped cross-fitting gives ECE 0.016–0.105,
+  with slopes 0.97–0.99, for those 8 pairs. Fitting on the other grammar family instead gives ECE
+  0.026–0.137, with slopes 0.75–1.33. Within a pair, the calibration carries over to new templates;
+  across grammars, less well. The registered transfer claim stays limited to the two frozen
+  pairs.
```

**6. § 8. Arm B: real code generation (instruct models; table + 4 examples in the prompt)** (new line 368; added)

```diff
+- **Extraction correction (Phase 4, post hoc).** In 63 generations, the frozen extractor
+  kept a same-line "Request:" continuation, so they counted as parse failures. Cutting it makes
+  27 correct and 31 valid but wrong. Task accuracy rises from 747 to **774 / 7,800 (9.9%)**. The
+  change is mostly in Qwen2.5-72B-I `blk`, which goes from 65 to 87 correct programs. Reach and
+  reversion given reach are unchanged.
```

**7. § 9. H5: repairing risky spellings** (new line 378; changed)

```diff
-- **The arms.** Each cell is one instruct model × family × lexicon; there are 100. In each, 3
-  roles were respelled using the targeted choice (the highest base-model risk), 3 random
-  seeds' worth of random choices, or all remapped roles (global).
+- **The arms.** Each cell is one instruct model × family × lexicon; there are 100. In each, the
+  repair respelled one of:
+  - **targeted:** the 3 roles with the highest base-model risk;
+  - **random:** 3 roles chosen at random, repeated with 5 seeds;
+  - **global:** all remapped roles.
```

**8. § 9. H5: repairing risky spellings** (new line 396; changed)

```diff
-- **H5 fails.** Choosing the riskiest roles does not beat random choice.
+- **H5 fails.** Choosing the riskiest roles does not beat random choice on the registered
+  metric. The registered interval test, run post hoc in Phase 4, confirms it in both families
+  (§2).
+- **But at the repaired sites themselves, targeting beats random** (Phase 4, post hoc):
+  `dom` +0.79 [+0.06, +1.53] and `blk` +2.21 [+1.39, +3.02] per changed symbol.
+  - This is mostly because respelling random, low-risk roles makes their own sites *worse*
+    (50.5% → 54.6% in `dom`, 49.5% → 56.3% in `blk`).
+  - The registered difference is negative because the *unrepaired* sites improved more under
+    random repair.
+  - This is a hypothesis for a preregistered follow-up, not a finding.
```

**9. § 13. Gaps in the frozen analysis: disclosed, then corrected post hoc in Phase 4** (new line 468; changed)

```diff
-## 13. Gaps in the frozen analysis (disclosed, not corrected post hoc)
-
-1. **H4 calibration labels.** For the 8 pairs without frozen Platt parameters (everything
-   but 0.5B and 1.5B), the frozen export does two things wrong:
-   - **The probability.** It writes `calibrated_p = σ(risk)`, i.e. uncalibrated, but labels
-     it `DEV_FREEZE`.
-   - **The calibration metrics.** It computes ECE, Brier and the calibration slope after
-     fitting a calibration on the held-out rows themselves, so the slope is exactly 1.00.
-   - **Unaffected:** AUROC, AP, the C1/C2 criteria and every other rank-based number.
-   - **The only genuine calibration-transfer claims are for the 0.5B and 1.5B pairs.**
-2. **The H5 interval test was never implemented.** The frozen export lists each arm's
-   per-symbol reduction but not the registered test (targeted − random with an interval). The
-   descriptive result (43/100 cells; mean −0.41) already contradicts H5. No post-hoc test is
-   offered as confirmatory.
-3. **The D10 scale analysis** was likewise missing from the frozen code. It was specified
-   (D11) and approved before outcomes were examined, and was run after the export.
-
-All three are recorded in [08](08_issues_and_superseded_numbers.md) and in deviation D12 of
-`phase3_2/PREREGISTRATION.md`.
+## 13. Gaps in the frozen analysis: disclosed, then corrected post hoc in Phase 4
+
+The frozen numbers above stay as they are. On 2026-10-21, the gaps below were corrected **after**
+the outcomes were known, outside the frozen code (deviation D13). The correcting script first
+reproduces each frozen number it corrects, and refuses otherwise. The full report is
+`analysis_addenda/phase4_fixes/PHASE4_FIXES.md`, and the explanation is in
+[`phase4/fixes_before_phase4/`](../../../phase4/fixes_before_phase4/README.md).
+
+| # | gap in the frozen export | Phase 4 correction (post hoc) | effect on a registered verdict |
+|---|---|---|---|
+| 1 | **H4 calibration** for the 8 pairs without frozen Platt parameters: `calibrated_p = σ(risk)` labelled `DEV_FREEZE`, and ECE, Brier and slope computed in-sample (slope exactly 1.00) | template-grouped 5-fold cross-fitting: ECE 0.016–0.105, slopes 0.97–0.99; other-grammar transfer: ECE 0.026–0.137, slopes 0.75–1.33 | none: the criteria are rank-based. The transfer claim stays limited to the 0.5B and 1.5B pairs |
+| 2 | **H5's registered interval test was never implemented** | the test as registered: `dom` −0.77 [−1.96, +0.40], `blk` −0.04 [−1.19, +1.12] per changed symbol; control sites within tolerance | none: H5 stays **not supported**, now by its own test |
+| 3 | **the D10 scale analysis** was not in the frozen code | fixed before Phase 4 by D11, specified and approved before outcomes were seen | — |
+| 4 | **H5's per-symbol metric mixes** repaired and control sites | exact split: at the repaired sites, targeted beats random (`dom` +0.79, `blk` +2.21; intervals above 0). The control sites decide the sign | none. It is a hypothesis for a preregistered follow-up |
+| 5 | **Arm B extraction** kept a same-line "Request:" continuation | cut and re-evaluated with the frozen evaluator: 63 generations change; task accuracy 9.6% → 9.9%; reach unchanged | none (Arm B is descriptive) |
+
+Also done in Phase 4: H4 **per role**, an open item from [06 §10](06_publishability_and_paper.md).
+The AUROC within each role is 0.63–0.98, with the interval above 0.5 in all 60 groups, so the
+prediction does not depend on one role.
+
+These items are recorded in [08](08_issues_and_superseded_numbers.md) and in deviations D12 and
+D13 of `phase3_2/PREREGISTRATION.md`.
```

**10. § 14. Where every number lives** (new line 511; added)

```diff
+| **Phase 4 post-hoc fixes** | `analysis_addenda/phase4_fixes/` (`PHASE4_FIXES.md`, F1–F6 CSVs) |
```

---

## 01_theory.md

[`phase3_2/sol/heldout_results_explained/01_theory.md`](../../phase3_2/sol/heldout_results_explained/01_theory.md): 6 changes, 22 lines added, 7 removed.

**Why:**

- **doc precision:** "92.8–99.5% of curves wobble" now gives the size of the dips, because the frozen `nonmonotone` flag counts any decrease
- **doc precision:** the "2 and 8 examples" are medians *among the sites that switch*
- **F2, F4:** the H5 concept gains the registered test and the split
- **F1:** the calibration concept gains the out-of-sample values; item 10 now limits the claim to calibration *transfer*

**1. § 6. In-context extinction: first switch vs a switch that holds** (new line 169; changed)

```diff
-   - 92.8–99.5% of curves wobble.
+   - 92.8–99.5% of curves dip at least once, but that frozen flag counts any decrease, however
+     small. The dips that matter: 31% of the sites that switch later fall back below zero, by a
+     median of −0.76 nats, and 59% of curves drop by more than 1 nat at some step
+     ([09 §3.3](09_conclusions_claim_strength_and_venues.md)).
```

**2. § 6. In-context extinction: first switch vs a switch that holds** (new line 188; changed)

```diff
-    back. That is a finding about in-context learning, not just about DSLs, and the gap
-    between 2 and 8 examples is a crisp, quotable number.
+    back. That is a finding about in-context learning, not just about DSLs. The gap between
+    about 2 and about 8 examples is a crisp, quotable number, as long as it is stated as
+    medians *among the sites that switch* (and among those whose switch lasts).
```

**3. § 11. Repair: silent vs loud errors (H5)** (new line 319; added)

```diff
+   - **The registered test** was run post hoc in Phase 4. Targeted − random per changed symbol
+     is `dom` −0.77 [−1.96, +0.40] and `blk` −0.04 [−1.19, +1.12]: not supported.
+   - **Split into repaired and control sites** (Phase 4, post hoc): at the repaired sites
+     targeted beats random (`dom` +0.79, `blk` +2.21, intervals above 0). The control sites
+     decide the negative sign.
```

**4. § 13. Calibration transfer, and the disclosed gap** (new line 381; added)

```diff
+   - **Out of sample** (Phase 4, post hoc): template-grouped cross-fitting gives ECE
+     0.016–0.105 with slopes 0.97–0.99 for those 8 pairs. Fitting on the other grammar gives
+     ECE 0.026–0.137 with slopes 0.75–1.33.
```

**5. § 13. Calibration transfer, and the disclosed gap** (new line 392; changed)

```diff
-10. **Why it matters.** Report calibration only for the 0.5B and 1.5B pairs. AUROC and the
-    criteria are rank-based and unaffected. See [08](08_issues_and_superseded_numbers.md).
+10. **Why it matters.** Claim calibration *transfer* only for the 0.5B and 1.5B pairs. The
+    post-hoc cross-fitted values show that each pair *can* be calibrated, which is a weaker
+    statement. AUROC and the criteria are rank-based and unaffected. See
+    [08](08_issues_and_superseded_numbers.md).
```

**6. § What the results say about the theory, in one paragraph** (new line 405; changed)

```diff
-- Showing them examples flips most preferences after about 2 examples, but the flip is
-  unstable until about 8, and 1 in 5 hard sites never flips within 32.
+- Showing them examples flips most preferences. Among sites that flip, the first flip comes
+  after about 2 examples, but a flip that lasts takes about 8, and 1 in 5 hard sites never flips
+  within 32.
```

---

## 02_mathematics_and_statistics.md

[`phase3_2/sol/heldout_results_explained/02_mathematics_and_statistics.md`](../../phase3_2/sol/heldout_results_explained/02_mathematics_and_statistics.md): 2 changes, 55 lines added, 0 removed.

**Why:**

- **F2, F4:** a new §6b with the registered test's formula, the exact split, the worked cell and the family tables
- **F1:** the cross-fitted calibration formula and values

**1. § 6b. The registered test and the repaired/control split (Phase 4, post hoc, 2026-10-21)** (new line 226; added)

```diff
+### 6b. The registered test and the repaired/control split (Phase 4, post hoc, 2026-10-21)
+
+**The registered test.** For each cell c, the difference compares the targeted arm with the
+mean of the 5 random seeds:
+
+$$
+D_c = R_{\text{targeted},c} - \tfrac{1}{5}\textstyle\sum_s R_{\text{random},s,c},
+\qquad R = \frac{\text{reversions before} - \text{reversions after}}{\text{changed roles}}
+$$
+
+For each grammar family, the statistic is the mean of D over its 50 cells. Its 95% interval
+comes from resampling the 80 templates 2,000 times, with the same draw for every cell and arm.
+H5 needs the interval above 0 in *both* families, and control degradation ≤ 0.02.
+
+| family | mean D [95% CI] | control degradation (targeted) | H5 as registered |
+|---|---|---|---|
+| `dom` | −0.77 [−1.96, +0.40] | −0.06 | not supported |
+| `blk` | −0.04 [−1.19, +1.12] | −0.05 | not supported |
+
+**The split.** R is the sum of a repaired-site part and a control-site part, exactly:
+
+$$
+R = \underbrace{\frac{b_{\text{rep}} - a_{\text{rep}}}{n}}_{\text{repaired sites}}
+  + \underbrace{\frac{b_{\text{ctl}} - a_{\text{ctl}}}{n}}_{\text{control sites}}
+$$
+
+Here b and a are the reversions before and after, and n is the number of changed roles.
+
+**The worked cell.** For the targeted arm, 13.67 = (29 − 36)/3 + (61 − 13)/3 = −2.33 + 16.00.
+The random mean is 9.27 = +5.87 + 3.40. So D = +4.40 [+1.27, +7.67], made of −8.20 at the
+repaired sites and +12.60 at the control sites. **This cell is atypical:** targeted wins here only
+through its control sites.
+
+**Over each family it is the other way round:**
+
+| family | repaired-site part of mean D | control-site part |
+|---|---|---|
+| `dom` | +0.79 [+0.06, +1.53] | −1.57 [−2.51, −0.65] |
+| `blk` | +2.21 [+1.39, +3.02] | −2.25 [−3.34, −1.23] |
+
+**Reading.** At the sites a repair touches, targeting beats random. That is mostly because
+respelling random, low-risk roles makes their own sites worse (50.5% → 54.6% reverting in `dom`).
+The registered sum is negative because of the control sites. All of this is post hoc
+(deviation D13), and the registered verdict stands.
+
```

**2. § 7. Calibration: what the frozen parameters do, and the gap** (new line 309; added)

```diff
+**The out-of-sample replacement (Phase 4, post hoc).** For each pair and family, the templates
+are split into 5 folds. Each site's probability comes from a Platt fit on the *other* four folds,
+p̂ᵢ = σ(â₋f + b̂₋f · riskᵢ), and ECE, Brier and the slope are computed on those predictions.
+
+- **The 8 pairs:** ECE 0.016–0.105, slopes 0.97–0.99.
+- **Fitted on the other grammar family instead:** ECE 0.026–0.137, slopes 0.75–1.33.
+
+With 2 parameters, the in-sample fit hardly overfits, which is why the cross-fitted ECE is close
+to the in-sample one.
+
```

---

## 03_code_and_pipeline.md

[`phase3_2/sol/heldout_results_explained/03_code_and_pipeline.md`](../../phase3_2/sol/heldout_results_explained/03_code_and_pipeline.md): 2 changes, 13 lines added, 0 removed.

**Why:**

- **pipeline:** the Phase 4 script's command line, and a new §13 with its input, transformation, output and validation

**1. § 11. Reproducing any number** (new line 276; added)

```diff
+$PY ../../phase4/scripts/fix_heldout_problems.py           # Phase 4 post-hoc fixes (D13): works locally (§13)
```

**2. § 13. Phase 4 fixes (local, CPU, 2026-10-21)** (new line 326; added)

```diff
+
+---
+
+## 13. Phase 4 fixes (local, CPU, 2026-10-21)
+
+| | |
+|---|---|
+| **Input** | 5 frozen CSVs, `merged/h5.jsonl` (restore it first with `restore_large_files.sh` after a clone), the run config, and the development freeze (its sha256 is checked against the unlock) |
+| **Transformation** | [`phase4/scripts/fix_heldout_problems.py`](../../../phase4/scripts/fix_heldout_problems.py), about 40 s. It reuses the frozen functions (`p33.h4`, `p33.armb`, `phase3_2.sites2`) and the D11-identical bootstrap |
+| **Output** | `analysis_addenda/phase4_fixes/`: `PHASE4_FIXES.md` and the F1–F6 CSVs. **Nothing written inside** `csv/`, `plots/` or `reports/` |
+| **Validation** | Before correcting anything, it reproduces the frozen numbers it corrects: 20 calibration groups, 700 H5 arm rows, 7,800 Arm B extractions and buckets, 60 per-role AUROCs. 205 sites are re-observed after the Arm B cut, with 0 changes. There are 6 tests in `phase4/tests/` |
+
```

---

## 04_retyping_plan.md

[`phase3_2/sol/heldout_results_explained/04_retyping_plan.md`](../../phase3_2/sol/heldout_results_explained/04_retyping_plan.md): 1 change, 12 lines added, 0 removed.

**Why:**

- **retype plan:** the four short functions of the Phase 4 script to read and retype, with line links

**1. § 10. Addendum (2026-10-09): the paper-figure script** (new line 245; added)

```diff
+**The Phase 4 fix script** ([`phase4/scripts/fix_heldout_problems.py`](../../../phase4/scripts/fix_heldout_problems.py),
+679 lines) corrects the open gaps post hoc (D13). Read four short functions:
+
+- `template_folds` ([147–151](../../../phase4/scripts/fix_heldout_problems.py#L147)) and
+  `cross_fitted_probs` ([164–176](../../../phase4/scripts/fix_heldout_problems.py#L164)). Their
+  invariant is that a site's probability never sees its own template; it is tested by flipping
+  that template's labels.
+- `h5_parts` ([183–193](../../../phase4/scripts/fix_heldout_problems.py#L183)). The registered
+  metric is the sum of its repaired and control parts, under any template weights.
+- `extract_corrected` ([200–202](../../../phase4/scripts/fix_heldout_problems.py#L200)). It is the
+  frozen extraction plus one cut.
+
```

---

## 05_mental_image.md

[`phase3_2/sol/heldout_results_explained/05_mental_image.md`](../../phase3_2/sol/heldout_results_explained/05_mental_image.md): 1 change, 12 lines added, 0 removed.

**Why:**

- **F4, F2:** Picture 7 gains the "repainted corners" view, with the repaired-site rates and the registered test

**1. § 🧠 Picture 7 — Repainting signs (H5, not supported)** (new line 149; added)

```diff
+**Looking only at the repainted corners** *(Phase 4, post hoc)*:
+
+- Repainting the 3 most dangerous signs does **better** than repainting 3 random ones.
+- That is mostly because repainting random, safe signs makes *those* corners worse.
+- The registered score still says "no better", because random repainting helped more at the
+  corners nobody repainted.
+
+```
+   at the repainted corners (dom):  "most dangerous" 70.9% → 70.5% wrong   random 50.5% → 54.6% wrong
+   registered test (post hoc):   dom −0.77 [−1.96, +0.40]   blk −0.04 [−1.19, +1.12]   → not supported
+```
+
```

---

## 06_publishability_and_paper.md

[`phase3_2/sol/heldout_results_explained/06_publishability_and_paper.md`](../../phase3_2/sol/heldout_results_explained/06_publishability_and_paper.md): 6 changes, 17 lines added, 11 removed.

**Why:**

- **F2, F4:** contribution 6, the H5 objection, the claims row and the abstract now separate the registered metric from the repaired sites
- **checklist:** the calibration item is revised (F1); the H5 test (F2), the per-role H4 table (F6) and the Arm B footnote (F5) are ticked; the frequency-aware H5 moves to the Phase 4 plan, because it needs new GPU scoring

**1. § 2. The contributions, strongest first** (new line 34; changed)

```diff
-| 6 | **Targeted repair fails, and why** | preregistered H5, not supported, with a mechanism | targeted beats random in 43/100 cells; global respelling → 0 silent errors |
+| 6 | **Targeted repair fails on the registered metric, and why** | preregistered H5, not supported, now by its own registered test (run post hoc) | targeted beats random in 43/100 cells; registered test `dom` −0.77 [−1.96, +0.40], `blk` −0.04 [−1.19, +1.12]; at the repaired sites alone targeted wins (post hoc); global respelling → 0 silent errors |
```

**2. § 3. How a reviewer will see it** (new line 65; changed)

```diff
-| "H5 failed, so is the repair story weak?" | The failure has a mechanism (permutations keep old spellings meaningful) and a positive counterpart: global respelling eliminates silent errors. |
+| "H5 failed, so is the repair story weak?" | The failure has a mechanism (permutations keep old spellings meaningful) and a positive counterpart: global respelling eliminates silent errors. Splitting the metric (post hoc) shows that targeting *does* win at the sites it repairs; the registered sum is decided by unrepaired sites, which is a precise hypothesis for a follow-up. |
```

**3. § 4. Claims you can and cannot make** (new line 80; changed)

```diff
-| targeted repair ≤ random; global respelling removes silent errors | that targeting by risk can never work (only this rule, with this metric) |
+| targeted repair ≤ random on the registered metric; global respelling removes silent errors | that targeting by risk can never work (only this rule, with this metric; at the repaired sites it won, post hoc) |
```

**4. § 6. Abstract (draft; every number from this run)** (new line 115; changed)

```diff
-> reached sites reverts, verbs most often. Respelling the predicted-riskiest symbols is no
-> better than random, whereas respelling all reassigned symbols eliminates silent errors:
-> in a permuted language every familiar spelling remains meaningful.
+> reached sites reverts, verbs most often. On the registered measure, respelling the
+> predicted-riskiest symbols is no better than random, whereas respelling all reassigned symbols
+> eliminates silent errors: in a permuted language every familiar spelling remains meaningful.
```

**5. § 10. Before submitting: a prioritized checklist** (new line 298; changed)

```diff
-- [ ] Report calibration only for the 0.5B and 1.5B pairs; footnote the in-sample values (08, D12).
-      The figure is ready: `P/figA1_calibration`.
-- [ ] State that H5's registered interval test was not implemented; give the descriptive result.
+- [ ] Report calibration *transfer* only for the 0.5B and 1.5B pairs; the figure is ready
+      (`P/figA1_calibration`). For the other 8, report the out-of-sample (cross-fitted) values from
+      Phase 4 and label them post hoc (D13).
+- [x] H5's registered interval test: run post hoc in Phase 4 (`dom` −0.77 [−1.96, +0.40],
+      `blk` −0.04 [−1.19, +1.12]). State that it was implemented after the outcomes were known.
```

**6. § 10. Before submitting: a prioritized checklist** (new line 311; changed)

```diff
-      post hoc.
-- [ ] An exploratory per-role H4 table, to show the prediction is not driven by verbs alone.
+      post hoc. It needs new GPU scoring, so it moves to the Phase 4 plan, together with a
+      preregistered repaired-site H5 metric.
+- [x] An exploratory per-role H4 table: done in Phase 4 (`analysis_addenda/phase4_fixes/F6_h4_per_role.csv`);
+      AUROC 0.63–0.98 within each role.
+- [x] Footnote the Arm B extraction effect with the corrected numbers: task accuracy 9.6% → 9.9%
+      (Phase 4, F5).
```

---

## 07_knowledge_check.md

[`phase3_2/sol/heldout_results_explained/07_knowledge_check.md`](../../phase3_2/sol/heldout_results_explained/07_knowledge_check.md): 2 changes, 18 lines added, 2 removed.

**Why:**

- **doc precision:** Q14 gives both medians with "among …" and asks why
- **new section K** (Q41–45) on the Phase 4 fixes

**1. § D. Adaptation (`00 §6`, `02 §3`, `01 §6–7`)** (new line 48; changed)

```diff
-14. Explain the difference between `k*` (median ≈ 2) and `sustained_k` (median ≈ 8) to someone
-    who has never seen an extinction curve.
+14. Explain the difference between `k*` (median ≈ 2 among the sites that switch) and
+    `sustained_k` (median ≈ 8 among the sites whose switch lasts) to someone who has never seen
+    an extinction curve. Why must both medians carry "among …"?
```

**2. § K. The Phase 4 fixes (`08 §5`, `phase4/fixes_before_phase4/`)** (new line 116; added)

```diff
+## K. The Phase 4 fixes (`08 §5`, `phase4/fixes_before_phase4/`)
+
+41. ✎ For one cell, the targeted arm removes 13.67 reversions per changed symbol: −2.33 at the
+    repaired sites and +16.00 at the control sites. Why can a repair remove reversions at sites
+    it did not touch?
+42. The registered H5 test is negative in both families, yet at the repaired sites targeting
+    beats random. Write the two sentences you would put in the paper, and say which one is
+    confirmatory.
+43. Why is cross-fitted calibration (ECE 0.016–0.105 for the 8 pairs) still *not* evidence of
+    calibration transfer, while the 0.5B and 1.5B values are?
+44. ⌨ In `analysis_addenda/phase4_fixes/F5_armb_changed_generations.csv`, find one generation
+    that became VALID_WRONG after the cut. What did the model get wrong?
+45. Every Phase 4 fix first reproduces the frozen number it corrects. Why does that matter more
+    for a post-hoc fix than for the original analysis?
+
```

---

## 08_issues_and_superseded_numbers.md

[`phase3_2/sol/heldout_results_explained/08_issues_and_superseded_numbers.md`](../../phase3_2/sol/heldout_results_explained/08_issues_and_superseded_numbers.md): 3 changes, 39 lines added, 2 removed.

**Why:**

- **status:** the header says what Phase 4 corrected
- **superseded numbers:** four rows (Arm B accuracy, the basis of the H5 verdict, the calibration of the 8 pairs, the random-seed wording)
- **new §5:** the F1–F6 table and the list of same-day doc fixes

**1. § 08 — Issues found at the results stage, and superseded numbers** (new line 4; changed)

```diff
-> registered verdict. All of it is disclosed, not patched. Deviation D12 in
-> `phase3_2/PREREGISTRATION.md` records items 1–3.
+> registered verdict. All of it was disclosed (deviation D12 records items 1–3).
+>
+> **On 2026-10-21 (Phase 4, step 0) every open item was corrected post hoc**, outside the frozen
+> code and without changing a frozen number (deviation D13). See §5, and
+> [`phase4/fixes_before_phase4/`](../../../phase4/fixes_before_phase4/README.md) for the detail.
```

**2. § 3. Superseded numbers** (new line 54; added)

```diff
+| Arm B task accuracy | 747 / 7,800 = 9.6% (frozen extraction) | **774 / 7,800 = 9.9%** beside the frozen value (post hoc) | a same-line "Request:" continuation was cut (§5, F5) |
+| basis of the H5 verdict | descriptive (43/100 cells; mean −0.41) | **the registered test**, run post hoc: `dom` −0.77 [−1.96, +0.40], `blk` −0.04 [−1.19, +1.12] | §5, F2 |
+| calibration of the 8 pairs without frozen parameters | in-sample ECE 0.017–0.111, slope exactly 1.00 | **cross-fitted ECE 0.016–0.105, slopes 0.97–0.99** (post hoc) | §5, F1 |
+| random arms of H5 (00 §9) | "3 random seeds' worth of random choices" | **5 seeds** of 3 random roles each | a wording error in 00 (the run config has seeds 1–5) |
```

**3. § 5. Fixed in Phase 4 (2026-10-21, post hoc, deviation D13)** (new line 77; added)

```diff
+
+---
+
+## 5. Fixed in Phase 4 (2026-10-21, post hoc, deviation D13)
+
+These were made by `phase4/scripts/fix_heldout_problems.py`; the output is in
+`analysis_addenda/phase4_fixes/`. Each fix first reproduces the frozen numbers it corrects, and
+the script refuses otherwise.
+
+| # | item (§1) | what was done | result |
+|---|---|---|---|
+| F1 | 1. calibration of 8 pairs | template-grouped 5-fold cross-fitting, and transfer from the other grammar family | cross-fitted ECE 0.016–0.105, slopes 0.97–0.99; other-grammar ECE 0.026–0.137, slopes 0.75–1.33 |
+| F2 | 2. H5's registered test | implemented as §3 states it, each family separately | `dom` −0.77 [−1.96, +0.40], `blk` −0.04 [−1.19, +1.12]: **not supported** |
+| F3 | 3. D10 scale analysis | — | fixed before Phase 4 by D11 |
+| F4 | 4. H5 metric mixes sites | exact repaired/control split | at repaired sites targeted beats random: `dom` +0.79 [+0.06, +1.53], `blk` +2.21 [+1.39, +3.02]; the control sites decide the sign |
+| F5 | 5. Arm B extraction | cut the same-line "Request:", re-evaluate with the frozen evaluator, re-observe sites | 63 generations change; accuracy 9.6% → 9.9%; 0 of 205 site outcomes change |
+| F6 | open item (06 §10): H4 per role | AUROC within each role | 0.63–0.98; interval above 0.5 in 60/60 groups |
+
+**Documentation fixes in this folder, made the same day:**
+
+- 00 said "two gaps" while listing three; now three, plus the Phase 4 status.
+- 00 gave "Holm p = 0.001"; now "≤ 0.001", because 0.0009995 is a floor.
+- 00 said the random H5 arm used 3 seeds; it used 5.
+- 01 gave the unqualified "92.8–99.5% of curves wobble" and an unqualified "2 → 8"; both now
+  carry their sizes and "among sites that switch".
+- 07 Q14 now carries "among …".
+- 02, 05, 06, 09 and 10 now include the Phase 4 results.
+
+Every change is listed with its before and after text in `phase4/fixes_before_phase4/`.
+
```

---

## 09_conclusions_claim_strength_and_venues.md

[`phase3_2/sol/heldout_results_explained/09_conclusions_claim_strength_and_venues.md`](../../phase3_2/sol/heldout_results_explained/09_conclusions_claim_strength_and_venues.md): 5 changes, 8 lines added, 6 removed.

**Why:**

- **F2, F4:** the conclusion paragraph and claim G now say "on the registered measure", with the registered test and the split
- **F6:** claim A gains the per-role evidence
- **F1:** claim I gains the cross-fitted values
- **§5:** row 2b, "fix the frozen analysis's open gaps", is marked done

**1. § 1. The conclusion paragraph (abstract-ready, conservative)** (new line 53; changed)

```diff
-> in five reached sites reverted. Respelling only the predicted-riskiest symbols was no
-> better than respelling random ones. Respelling every reassigned symbol into an unfamiliar
-> alphabet cut reversion at the repaired sites from 48% to 16% and left no silent errors.
+> in five reached sites reverted. On the registered measure, respelling only the
+> predicted-riskiest symbols was no better than respelling random ones. Respelling every
+> reassigned symbol into an unfamiliar alphabet cut reversion at the repaired sites from 48% to
+> 16% and left no silent errors.
```

**2. § 2. Claim by claim: how strong, the main attack, the defence** (new line 75; changed)

```diff
-| A | An instruct model's reversions are predictable, site by site, from its base model | preregistered H4: C1 and C2 met in 20/20; AUROC 0.76–0.96; within-lexicon AUROC 0.76–0.96; Δ vs role-level > 0 in 20/20 (CI > 0 in 16) | **Strong** | "Trivial: it is fine-tuned from the base" | It holds *with the rules in context*, where tuning should help most. And see A′ |
+| A | An instruct model's reversions are predictable, site by site, from its base model | preregistered H4: C1 and C2 met in 20/20; AUROC 0.76–0.96; within-lexicon AUROC 0.76–0.96; Δ vs role-level > 0 in 20/20 (CI > 0 in 16); *post hoc (Phase 4):* within each single role, AUROC 0.63–0.98, interval above 0.5 in 60/60 | **Strong** | "Trivial: it is fine-tuned from the base" | It holds *with the rules in context*, where tuning should help most. And see A′ |
```

**3. § 2. Claim by claim: how strong, the main attack, the defence** (new line 83; changed)

```diff
-| G | Targeting the riskiest symbols does not beat random repair | H5 not supported: targeted > random in 43/100 cells | **Not supported** (honest negative) | "The interval test was not run, and the metric counts all sites" | Disclosed (D12, [08](08_issues_and_superseded_numbers.md)); report it as descriptive |
+| G | Targeting the riskiest symbols does not beat random repair (registered metric) | targeted > random in 43/100 cells. The registered test, run post hoc in Phase 4: `dom` −0.77 [−1.96, +0.40], `blk` −0.04 [−1.19, +1.12] | **Not supported** (honest negative, now by its own test) | "The metric counts all sites" | Split (Phase 4, post hoc): at the repaired sites targeted *beats* random (`dom` +0.79, `blk` +2.21; intervals above 0), and the control sites decide the sign. Report it as a hypothesis for a preregistered follow-up |
```

**4. § 2. Claim by claim: how strong, the main attack, the defence** (new line 86; changed)

```diff
-| I | Calibration transfers | only the 2 development pairs: ECE 0.036–0.052 | **Weak–moderate** | "Two pairs" | Claim it for those two only (D12) |
+| I | Calibration transfers | only the 2 development pairs: ECE 0.036–0.052. The other 8, cross-fitted (Phase 4, post hoc): ECE 0.016–0.105, slopes 0.97–0.99 | **Weak–moderate** | "Two pairs" | Claim *transfer* for those two only (D12); the cross-fitted values show each pair can be calibrated |
```

**5. § 5. What would make the paper stronger (in priority order)** (new line 216; added)

```diff
+| 2b | Fix the frozen analysis's open gaps: calibration, H5's registered test, the H5 split, Arm B extraction, H4 per role | **done** (Phase 4 step 0, post hoc, D13; `phase4/`) | answers "the analysis has holes": each one is closed and disclosed |
```

---

## 10_humans_and_the_brain.md

[`phase3_2/sol/heldout_results_explained/10_humans_and_the_brain.md`](../../phase3_2/sol/heldout_results_explained/10_humans_and_the_brain.md): 2 changes, 8 lines added, 4 removed.

**Why:**

- **F4:** the sticker analogy in Moment 9, and its model bullets, now separate the registered score from the repaired stalks

**1. § Moment 9 — Fixing the car (H5)** (new line 197; changed)

```diff
-- **Alex, option 1:** stickers on the three stalks Alex confuses most. It helps little: the
-  other swapped controls still trap Alex.
+- **Alex, option 1:** stickers on the three stalks Alex confuses most. They help with *those*
+  stalks more than stickers on three random stalks would. But the registered score counts
+  every control in the car, and random stickers happened to help more with the stalks they were
+  *not* on. By that score, the three stickers do no better.
```

**2. § Moment 9 — Fixing the car (H5)** (new line 205; changed)

```diff
-  - respelling the 3 riskiest roles is no better than respelling 3 at random (43 of 100
-    cells);
+  - on the registered measure, respelling the 3 riskiest roles is no better than respelling
+    3 at random (43 of 100 cells; the registered test, run post hoc, agrees);
+  - at the repaired sites themselves, targeting does better than random (post hoc), mostly
+    because respelling random, low-risk roles makes those sites worse;
```

---

## README.md

[`phase3_2/sol/README.md`](../../phase3_2/sol/README.md): 1 change, 9 lines added, 0 removed.

**Why:**

- **status:** a line saying that Phase 4 started, and what its first step corrected

**1. § Phase 3.3 on ASU Sol — runbook** (new line 35; added)

```diff
+> - **Phase 4 started on 2026-10-21** ([`../../phase4/`](../../phase4/README.md)). Its first step
+>   corrected every open gap of the held-out analysis post hoc (deviation D13):
+>   - out-of-sample calibration;
+>   - H5's registered test, which is not supported in either family;
+>   - the H5 repaired/control split;
+>   - the Arm B extraction, with task accuracy 9.6% → 9.9%;
+>   - H4 per role.
+>
+>   No registered verdict changed.
```

---

## PREREGISTRATION.md

[`phase3_2/PREREGISTRATION.md`](../../phase3_2/PREREGISTRATION.md): 1 change, 44 lines added, 0 removed.

**Why:**

- **governance:** deviation D13 appended. The frozen text above "Deviations" is untouched; `test_frozen_preregistration_text_is_byte_identical` checks its sha256 (`a0146494…`)

**1. § D13 — 2026-10-21 — post-hoc corrections of the held-out gaps (Phase 4, step 0)** (new line 361; added)

```diff
+
+### D13 — 2026-10-21 — post-hoc corrections of the held-out gaps (Phase 4, step 0)
+
+**What happened.** The gaps disclosed in D12, and two further problems listed in
+`sol/heldout_results_explained/08`, were corrected after the held-out outcomes were known. The
+corrections were made by `phase4/scripts/fix_heldout_problems.py`, outside the frozen code, from
+the run's saved data, with no model re-run. Before correcting anything, each fix reproduces the
+frozen numbers it corrects with the frozen functions, and the script refuses if it cannot. The
+output is in `heldout-20261007a/analysis_addenda/phase4_fixes/`.
+
+**Change.**
+
+1. **H4 calibration (D12 item 1).** Out-of-sample estimates for all ten pairs:
+   template-grouped 5-fold cross-fitting and cross-family transfer.
+   - The eight pairs without frozen parameters, cross-fitted: ECE 0.016–0.105, slopes 0.97–0.99.
+   - Transfer from the other grammar family: ECE 0.026–0.137, slopes 0.75–1.33.
+2. **H5's registered test (D12 item 2).** Implemented exactly as §3 states it: targeted minus
+   random per changed symbol, with a 95% template-cluster interval (B = 2000), and control
+   degradation ≤ 0.02, for each family separately.
+   - `dom` −0.77 [−1.96, +0.40] and `blk` −0.04 [−1.19, +1.12] per changed symbol.
+   - Control degradation −0.06 and −0.05 (within the tolerance).
+3. **The H5 metric's mixing (D12 item 2, second sentence).** The metric was split exactly into
+   repaired-site and control-site parts.
+   - At the repaired sites, targeted beats random: `dom` +0.79 [+0.06, +1.53], `blk` +2.21
+     [+1.39, +3.02].
+   - The registered difference is negative because unrepaired sites improved more under random
+     repair: `dom` −1.57, `blk` −2.25.
+4. **Arm B extraction.** A same-line "Request:" continuation was cut, and the result
+   re-evaluated with the frozen evaluator.
+   - 63 of 7,800 generations change.
+   - Task accuracy goes from 9.6% to 9.9%.
+   - No site's reach or reversion changes (205 sites re-observed).
+5. **H4 per role (an open item).** The AUROC within each role is 0.63–0.98, and its interval lies
+   above 0.5 in all 60 pair × grammar × role groups.
+
+**Scientific consequence.** No registered verdict changes.
+
+- H4's criteria are rank-based and untouched. The calibration-transfer claim stays limited to
+  the two frozen pairs; the cross-fitted values are a post-hoc statement about calibratability.
+- **H5 is not supported by its own registered test**, in either family. That confirms the
+  descriptive verdict of D12, now with the registered interval.
+- The repaired-site advantage of targeting is post hoc. It is a hypothesis for a preregistered
+  follow-up with a repaired-site metric, not a finding.
+- The corrected Arm B accuracy is reported beside the frozen 9.6%, never instead of it.
```
