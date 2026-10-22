# 01 — Phase 4, step 0: the fixes made on 2026-10-21

> **What and why.** The held-out analysis of Phase 3.3 left five known problems
> ([`heldout_results_explained/08`](../../phase3_3/heldout_results_explained/08_issues_and_superseded_numbers.md)
> §1) and one open analysis item ([06 §10](../../phase3_3/heldout_results_explained/06_publishability_and_paper.md)).
> All of them were fixed before any new Phase 4 work began.
>
> **The rules every fix followed:**
>
> 1. **Post hoc, and labelled so.** The fixes come after the held-out outcomes were known, so
>    none is confirmatory. They are recorded as deviation **D13**, appended to
>    `phase3_2/PREREGISTRATION.md`. The frozen text above "Deviations" is byte-identical, which
>    `test_frozen_preregistration_text_is_byte_identical` checks.
> 2. **Outside the frozen code.** Nothing in `phase3_2/sol/src/` changed, and no frozen output
>    (`csv/`, `plots/`, `reports/`) was rewritten. The fixes live in
>    `phase4/scripts/fix_heldout_problems.py`, and their outputs in
>    `heldout-20261007a/analysis_addenda/phase4_fixes/`.
> 3. **Reproduce before correcting.** Each fix first recomputes the frozen numbers it is about to
>    correct, using the frozen functions. The script refuses to continue if any of them differs.
> 4. **Same statistics as the registered analysis:** 95% template-cluster bootstrap, B = 2000,
>    seed 20261002, drawn exactly as the D11 script draws it. Each grammar family is analysed
>    separately.

---

## The checks that ran first (all passed)

| check | what it proves |
|---|---|
| ECE, Brier, slope and intercept of all **20** pair × grammar groups equal the export's | F1 starts from the same rows and functions as the frozen analysis |
| all **700** frozen H5 arm rows are reproduced from `merged/h5.jsonl` and Arm A: counts, per-symbol reduction, control degradation | F2 and F4 compute the registered metric exactly as the export did |
| the frozen extraction and bucket are reproduced for all **7,800** Arm B generations | F5's re-evaluation uses the same evaluator, lexicons and targets |
| re-observing the **205** sites of the 63 changed generations gives **0** changed outcomes | the extraction fix cannot touch reach or reversion given reach |
| all **60** per-role AUROCs equal the frozen `p33.h4.auroc` | F6's vectorised AUROC is exact |
| **6** unit tests in `phase4/tests/`, plus the **147** Phase 3.3 tests | the new functions do what they claim; nothing old broke |

---

## F1 — H4 calibration: from in-sample to out-of-sample

**The problem.**

- **The freeze held Platt calibration only for the two development pairs** (Qwen2.5-Coder 0.5B
  and 1.5B).
- **The export mislabelled the other 8 pairs.** It wrote `calibrated_p = σ(risk)` labelled
  `DEV_FREEZE`. Then `evaluate_group` fitted a calibration on the held-out rows themselves and
  measured it on the same rows.
- **So their ECE, Brier and calibration slope were in-sample.** The slope was exactly 1.00,
  because a logistic fit is perfectly calibrated on its own training data.

**Why it matters.** An in-sample calibration says nothing about whether the risk score can be
turned into honest probabilities for new sites.

**What was done.** Two out-of-sample estimates per pair and grammar:

1. **Template-grouped 5-fold cross-fitting.**
   - The 80 templates are split into 5 folds, deterministically (seed 20261002) and balanced
     (16 templates each).
   - Each site's probability comes from a Platt fit, `p = σ(a + b·risk)`, made on the other four
     folds only.
   - So no site is predicted by a fit that saw its own template.
2. **Cross-family transfer.** A Platt fit on the same pair's *other* grammar family, applied here.

The ECE (10 bins), Brier and slope functions are the frozen ones (`p33.h4.ece`, `brier`,
`calibration_slope_intercept`).

**Code.**

- [`template_folds`](../../../phase4/scripts/fix_heldout_problems.py#L147-L151) and
  [`cross_fitted_probs`](../../../phase4/scripts/fix_heldout_problems.py#L164-L176).
- The F1 block of `main`, [lines 247–316](../../../phase4/scripts/fix_heldout_problems.py#L247-L316). It first
  reproduces the export: the frozen Platt parameters for the two development pairs, and an
  in-sample fit for the other eight, exactly as the frozen `p33.h4.evaluate_group` does.
- **Tests:**
  - `test_template_folds_are_deterministic_and_balanced`;
  - `test_cross_fitted_probabilities_never_see_their_own_template`, which flips one template's
    labels and checks that its own probabilities do not move;
  - `test_in_sample_slope_is_one_and_cross_fitted_is_not_exactly_one`.

**Result** (`F1_h4_calibration_out_of_sample.csv`):

| | ECE | calibration slope |
|---|---|---|
| export, 8 pairs (in-sample, the gap) | 0.017–0.111 | exactly 1.00 |
| **cross-fitted, 8 pairs** | **0.016–0.105** | **0.97–0.99** |
| other-grammar transfer, 8 pairs | 0.026–0.137 | 0.75–1.33 |
| frozen transfer, the 2 development pairs (registered) | 0.036–0.052 | 0.83–1.18 |

**What it means.**

- **Within a pair, calibration carries over to new templates.** With only two parameters, a Platt
  fit hardly overfits, so the cross-fitted values are close to the in-sample ones.
- **Across grammar families it carries over less well:** slopes as far from 1 as 0.75 and 1.33.
- **The claim does not grow.** Calibration *transfer* is still claimed only for the two frozen
  pairs. The new values support a weaker statement: each pair *can* be calibrated with a small
  calibration set.

---

## F2 — H5: the registered test, finally run

**The problem.** The preregistration (§3) states the H5 criterion:

> H5 is supported iff error reduction per changed symbol exceeds the matched-budget
> random-rewrite control with an interval excluding 0, and reversion at low-risk control sites
> does not worsen by more than 0.02.

The frozen export reported each arm's per-symbol reduction, but never computed this test. The
H5 verdict ("not supported") rested on descriptive numbers: targeted beat the random mean in
43 of 100 cells, with a mean difference of −0.41.

**What was done.** The test, exactly as stated:

- **Per cell** (instruct model × lexicon): D = targeted − the mean of the 5 random seeds, in
  reversions removed per changed symbol, which is the export's own metric.
- **Per grammar family:** the mean of D over its 50 cells, with a 95% template-cluster bootstrap
  interval. The same template draw is used for every cell and arm.
- **Control criterion:** the targeted arm's change in reversion rate at the sites it did not
  repair must be ≤ 0.02.
- **Never pooled across families:** H5 would need support in both.

**Code.**

- The F2 + F4 block of `main`, [lines 317–530](../../../phase4/scripts/fix_heldout_problems.py#L317-L530).
  - It rebuilds each arm's per-template counts from `merged/h5.jsonl`. "Before" comes from
    Arm A: the rule condition, M < 0.
  - It checks the counts against all 700 arm rows of `csv/h5_budget_outcomes.csv`.
  - It computes D with [`h5_parts`](../../../phase4/scripts/fix_heldout_problems.py#L183-L193), under the
    bootstrap weights of `paper_figures.draws`.
- p-values come from [`two_sided_p`](../../../phase4/scripts/fix_heldout_problems.py#L123-L126) and
  [`holm`](../../../phase4/scripts/fix_heldout_problems.py#L129-L135).
- **Test:** `test_two_sided_p_and_holm`.

**Result** (`F2_h5_registered_test.csv`):

| family | targeted − random per changed symbol [95% CI] | control degradation | H5 as registered |
|---|---|---|---|
| `dom` | −0.77 [−1.96, +0.40] | −0.06 (an improvement) | **NOT SUPPORTED** |
| `blk` | −0.04 [−1.19, +1.12] | −0.05 | **NOT SUPPORTED** |

**Detail:**

- **Per cell,** the interval lies above 0 in 20 cells and below 0 in 18, out of 100.
- **Per model and family, with Holm over the 20 tests,** two survive, in opposite directions:
  - Qwen2.5-Coder-3B-Instruct `blk`: −3.47 [−5.68, −1.45];
  - Llama-3.2-1B-Instruct `blk`: +4.05 [+2.19, +5.88].
- The control criterion is met; criterion 1 is not.

**What it means.** The verdict is unchanged, but it now rests on the registered test instead of
on description. The two family means average −0.41, exactly the descriptive figure.

---

## F3 — the D10 scale analysis (fixed before Phase 4)

The frozen code never computed the scale analysis that D10 pre-specified.

- **Fixed on 2026-10-08 by D11.** The analysis was specified, implemented in
  [`phase3_2/sol/scripts/scale_analysis.py`](../../../phase3_2/sol/scripts/scale_analysis.py) and
  approved by the investigator, all before any held-out outcome was examined.
- **Nothing more to do;** it is listed here because it was item 3 of the open list.

---

## F4 — H5's metric, split into the sites it repaired and the rest

**The problem.**

- **The metric mixes two kinds of site.** It counts reversions removed at *every* site of a
  cell: those whose spelling was repaired, and "control" sites, which change only because the
  prompt's token table (and the earlier part of each program) changed.
- **The worked cell showed how big the mix can be.** In 02 §6, the repaired sites got worse
  (29 → 36) while the control sites improved (61 → 13).

**What was done.** An exact split of the registered metric:

  R = (b_rep − a_rep)/n + (b_ctl − a_ctl)/n = repaired-site part + control-site part

where b and a are reversions before and after, and n is the number of changed roles. The total is
the registered metric, reproduced for all 700 arm rows. The same bootstrap as F2 gives intervals
for each part of the targeted − random difference.

**Code.**

- [`h5_parts`](../../../phase4/scripts/fix_heldout_problems.py#L183-L193) returns the two parts, their sum and
  the control degradation, under any template weights.
- It runs in the same loop as F2.
- **Test:** `test_h5_parts_split_exactly_and_weights_count_templates`.

**Result** (`F4_h5_repaired_control_split.csv`, `F4_h5_repaired_site_rates.csv`):

| family | targeted − random | repaired-site part | control-site part |
|---|---|---|---|
| `dom` | −0.77 | **+0.79 [+0.06, +1.53]** | −1.57 [−2.51, −0.65] |
| `blk` | −0.04 | **+2.21 [+1.39, +3.02]** | −2.25 [−3.34, −1.23] |

Reversion at the repaired sites themselves (pooled):

| family | targeted | random (5 seeds) | global |
|---|---|---|---|
| `dom` | 70.9% → 70.5% | 50.5% → 54.6% | 47.4% → 15.3% |
| `blk` | 74.2% → 66.5% | 49.5% → 56.3% | 48.1% → 15.7% |

**What it means.** This is the most important new observation of step 0.

- **Where the repair acts, targeting beats random.** The interval is above 0 in both families.
  This is mostly because respelling random, low-risk roles makes their own sites *worse*,
  while respelling the riskiest roles leaves them about as they were (`dom`) or improves them
  (`blk`).
- **The registered result is negative because of the control sites.** Under random repair, the
  sites that were not repaired improved more. The H5 verdict is decided mainly by sites the
  repair never touched.
- **Silent errors stay** under any partial repair. In a permuted language, a repaired role's old
  spelling is still another role's spelling. Only global respelling removes them.
- **It is post hoc,** so it is a hypothesis, not a finding. It becomes Phase 4 candidate
  study 1: H5 with a preregistered repaired-site metric.

---

## F5 — Arm B: the extraction fix

**The problem.**

- **The frozen extractor keeps the whole first line** of a model's output (`armb.extract_program`).
- **Some models ran on.** They continued the few-shot pattern on that same line:
  `$S 'mesh' { duplicate 1, 2, 3; } Request: First, set the visibility …`.
- **Valid programs failed.** The parser failed on "Request:", so a possibly correct program
  counted as a parse failure.

**What was done.**

1. Apply the frozen extraction, then cut at the first same-line `Request:` (case-insensitive,
   preceded by whitespace). It is the same rule as the exploratory check that found the
   problem (08 §1, item 5: 58 of the 63 then parse, and 27 equal the target).
2. Re-evaluate the corrected program with the frozen `armb.evaluate`.
3. Rebuild the sites of each changed generation with the frozen `sites2.classify`, and re-observe
   them with the frozen `armb.observe`.

**Code.**

- [`extract_corrected`](../../../phase4/scripts/fix_heldout_problems.py#L200-L202).
- The F5 block of `main`, [lines 531–606](../../../phase4/scripts/fix_heldout_problems.py#L531-L606). It also
  checks that each re-rendered target program equals the stored one.
- **Test:** `test_corrected_extraction_cuts_only_a_same_line_request`. It checks three things:
  - the cut ignores case (`request : next` is cut);
  - a selector such as `'requests'` inside a program is left alone;
  - an output without a continuation is extracted exactly as the frozen extractor does it.

**Result** (`F5_armb_task_accuracy.csv`, `F5_armb_changed_generations.csv`):

| | frozen | corrected |
|---|---|---|
| correct programs | 747 / 7,800 (9.6%) | **774 / 7,800 (9.9%)** |
| parse failures | 3,006 | 2,948 |
| changed generations | — | 63: 27 become correct, 31 valid but wrong, 5 still fail |
| site outcomes changed (reach, reversion) | — | **0 of 205** |

**Most of the change is in one model:**

- **Qwen2.5-72B-Instruct `blk`:** 65 → 87 correct (16.7% → 22.3%);
- **Qwen2.5-72B-Instruct `dom`:** 107 → 110;
- **Qwen2.5-Coder-32B-Instruct `dom`:** 60 → 62.

**What it means.**

- **Task accuracy was slightly understated, mostly for the largest model.**
- **Reach and reversion given reach are untouched.** Both depend only on the program text up to
  each site, and the cut text lies after the program.
- **In the paper,** report the corrected accuracy *beside* the frozen value.

---

## F6 — H4 per role (an open analysis item)

**The question.** 06 §10 listed it as "should do": is the H4 prediction carried by one kind of
symbol, for example verbs?

**Why this test answers it.**

- **The roles differ in how often they revert.** Reversion prevalence ranges from 0.38 to 0.61
  for sigils and from 0.35 to 0.53 for verbs, so an AUROC pooled over roles could partly reflect
  those differences.
- **Inside one role, those differences are gone.** A high AUROC there cannot come from them.
- **One difference remains:** the terminals within one role (14 verbs, 6 keywords, 2 sigils)
  still differ from one another. The exploratory per-terminal baseline `terminal_rate` covers
  those (Δ role in 00 §3).

**What was done.** For each pair, family and role (sigil, keyword, verb), the AUROC of the base
model's risk for the instruct model's reversions, with a template-cluster interval
(`F6_h4_per_role.csv`).

**Code.**

- The F6 block of `main`, [lines 607–651](../../../phase4/scripts/fix_heldout_problems.py#L607-L651).
- The intervals come from `paper_figures.auroc_w`.
- Each point estimate is checked against the frozen `p33.h4.auroc`.

**Result:**

| role | AUROC range | median | intervals above 0.5 |
|---|---|---|---|
| sigil | 0.63–0.98 | 0.86 | 20 / 20 |
| keyword | 0.66–0.98 | 0.88 | 20 / 20 |
| verb | 0.80–0.97 | 0.88 | 20 / 20 |

The weakest groups are Qwen2.5-Coder-7B sigils (0.635 `dom`, 0.636 `blk`) and
Qwen2.5-Coder-32B keywords (0.661 and 0.697). Even these intervals stay above 0.5.

**What it means.**

- **The prediction holds inside every role,** so it is not carried by the differences between
  roles.
- **It adds to the exploratory Δ role result,** in which the score beats the per-terminal
  `terminal_rate` baseline: by point estimate in 20 of 20 groups, with the interval above 0 in
  16 of them.
- **Both are exploratory.** The confirmatory H4 criteria are C1 and C2.

---

## The documentation fixes (same day)

The audit of `heldout_results_explained/` found these errors and stale statements:

| doc | problem | fix |
|---|---|---|
| 00 | said "Two gaps in the frozen analysis" while §13 listed three | three, plus their Phase 4 status |
| 00 | "Holm p = 0.001" | "≤ 0.001 (the bootstrap floor, 0.0009995)": it is a floor, not a measurement |
| 00 | "3 random seeds' worth of random choices" for H5 | **5 seeds** of 3 roles each (`seeds.h5_random = [1, 2, 3, 4, 5]` in the run config) |
| 00 §13 | titled "disclosed, not corrected post hoc" | now "disclosed, then corrected post hoc in Phase 4", with a table of each gap and its correction |
| 01 §6 | "92.8–99.5% of curves wobble", without the size | now gives the size: 31% of switches fall back, median −0.76 nats; 59% of curves drop > 1 nat |
| 01 §6, closing paragraph | "flips after about 2 examples … unstable until about 8", without "among sites that switch" | qualified |
| 07 Q14 | "`k*` (median ≈ 2)" without "among …" | qualified, and asks why |
| 00, 01, 02, 05, 06, 09, 10 | the calibration, H5 and Arm B statements predated the fixes | the Phase 4 results were added, each labelled post hoc |
| 06 §10 | the checklist still listed the H5 test and the per-role H4 table as to-do | ticked, with pointers; the frequency-aware H5 item moved to the Phase 4 plan |
| 03, 04, 08, sol `README.md` | no mention of Phase 4 | §13 in 03, a retype note in 04, §5 in 08, a status line in the README |

The exact before and after text of every change is in
[`03_doc_changes_before_after.md`](03_doc_changes_before_after.md).

---

## What did *not* change

- **Every frozen number**, in `csv/`, `plots/` and `reports/`.
- **Every registered verdict:**
  - H4 is met in 20 of 20 groups; C3 is not testable;
  - H5 is not supported;
  - the `k*` endpoint is unchanged.
- **The frozen code** (`phase3_2/sol/src/`) and the frozen preregistration text.
- **The paper figures and tables** of `paper_figures.py`. They restate frozen numbers. Where
  the paper gives Arm B task accuracy, the corrected 9.9% goes beside the frozen 9.6%, never in
  place of it.
