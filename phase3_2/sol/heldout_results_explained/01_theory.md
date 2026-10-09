# 01 — Theory: what the held-out results mean

> The design concepts (site, collision, margin, freeze, ladder, cluster bootstrap) are
> defined in [`../sol_experiment_explained/01_theory_and_research_design.md`](../sol_experiment_explained/01_theory_and_research_design.md)
> and not repeated here.
>
> This file covers the concepts you need to **read the results**. Each gets 10 points:
>
> 1. technical;
> 2. simple;
> 3. real example from this run;
> 4. inputs → outputs;
> 5. assumptions;
> 6. silent failure;
> 7. symptom;
> 8. test;
> 9. where in code;
> 10. why it matters.

---

## 1. Confirmatory evidence

1. **Technical.** A result is confirmatory when the hypothesis, the statistic, the
   threshold and the analysis code were fixed **before** the data that test them existed, and
   the test was run once. Here the code hashes, calibration, prompts and model revisions were
   frozen in `DEV_FREEZE.json`. Every held-out job re-checked them.
2. **Simple.** You wrote the grading rules in ink before seeing the exam.
3. **Example.** The held-out H4 test ran on 21 models and 5 new mappings, and C1/C2 were met
   20/20. No choice could have been tuned to these numbers.
4. **In → out.** A frozen plan plus new data gives one verdict per registered criterion.
5. **Assumptions.**
   - The frozen code is the code that ran: 44 source hashes, drift `[]` at every access.
   - Nothing about held-out outcomes leaked back into the design.
6. **Silent failure.** Editing the analysis after seeing results, then reporting it as if
   planned.
7. **Symptom.** A "confirmatory" number whose computation changed after the unlock.
8. **Test.**
   - `test_heldout_access_refuses_if_source_changes_after_unlock`
   - `test_unlock_needs_the_exact_phrase`
   - `test_tampered_freeze_is_detected`
9. **Where.** `p33/splits.py`: `write_freeze`, `write_unlock`, `frozen_drift`, `load_unlock`.
10. **Why it matters.** It is the difference between "we found" and "we predicted and it
    held". Reviewers weigh the two very differently. The analysis gaps found afterwards (§13)
    are *disclosed*, not patched, for the same reason.

---

## 2. Prior reliance (reversion)

1. **Technical.** At a site, reversion means M = log P(new spelling) − log P(old spelling) < 0.
   The reversion rate is the share of sites with M < 0.
2. **Simple.** The model writes the word it learned in training instead of the word the new
   language uses.
3. **Example.**
   - With the token table: every model, 0.5B to 72B, reverts on **40–56%** of sites.
   - Without the table: 46–66%.
4. **In → out.** One margin per site gives the share below zero, per model and family.
5. **Assumptions.**
   - The first-divergent-token margin reflects what the model would write.
   - Arm B checks this assumption in real generation: about 1 in 5 reached sites revert.
6. **Silent failure.** Counting a degenerate tokenization (identical candidates) as a
   preference. The code refuses those pairs.
7. **Symptom.** Margins of exactly 0 (there are none: 0 of 190,890).
8. **Test.** `test_check_pair_refuses_every_degenerate_case`,
   `test_merged_candidate_is_measured_not_zeroed`.
9. **Where.** `phase3_2/margins.py`: `TokenScorer.score_pair_detailed`.
10. **Why it matters.** It is the core phenomenon. That it does **not** shrink with scale
    (D11: no slope survives Holm) is the paper's strongest descriptive finding: bigger models
    lean on their priors just as much.

---

## 3. Rule following: information, not length

1. **Technical.**
   - The rule effect is M(rule) − M(control), paired by site.
   - There are two controls: the same prompt without spellings (`norule`), and that prompt
     padded to the rule prompt's token count (`norule_lenmatched`).
2. **Simple.** Does showing the dictionary help, and is it the dictionary or just a longer
   prompt?
3. **Example.**
   - The mean effect is +0.16 to +0.62 nats for every model.
   - The interval is above zero in 263 of 420 model × lexicon × control tests, and never
     below.
   - The length control gives the same answer (+0.353 vs +0.340 in `dom`).
4. **In → out.** Paired margins give a mean difference with a template-bootstrap interval.
5. **Assumptions.** The neutral filler carries no information. Its neutrality is assumed,
   not measured.
6. **Silent failure.** Comparing against `norule` only, and crediting the table with a pure
   length effect.
7. **Symptom.** The effect vanishes against the length-matched control. It does not here.
8. **Test.** `test_norule_lenmatched_reaches_rule_token_count`,
   `test_old_dict_pairing_collapsed_the_duplicate`.
9. **Where.** `phase3_2/prompts.py: norule_lenmatched`; `phase3_2/analysis.py: paired_rule_effect`.
10. **Why it matters.** Models *do* read the table: the margin moves. But e^0.35 ≈ 1.4× is
    too small a shift to flip most decisions, so reversion falls only about 5 points.
    "Telling the model the rules" is necessary but far from sufficient.

---

## 4. Site-level predictability (H4)

1. **Technical.**
   - risk = −M(base, rule).
   - label = 1[M(instruct, rule) < 0].
   - The test is the AUROC of risk for label, against constant (identity) and length
     baselines, with template-bootstrap intervals on the differences and Holm correction.
2. **Simple.** Where the base model hesitates, its instruction-tuned twin fails.
3. **Example.**
   - AUROC is 0.76–0.96 across 10 pairs and 2 grammars. C1 and C2 are met 20/20.
   - At the top-risk 32B site (`castShadow`, risk 5.4), the instruct model indeed reverted.
4. **In → out.** One base margin per site gives a ranking of sites, scored by AUROC against
   the instruct outcomes.
5. **Assumptions.**
   - Base and instruct share a tokenizer and pretraining, which is the hypothesis itself.
   - Sites are clustered by template, and the bootstrap respects that.
6. **Silent failure.** A score that only separates *lexicons* (some mappings are harder)
   would look predictive.
7. **Symptom.** A high overall AUROC but a low within-lexicon AUROC. Here the within-lexicon
   AUROC (0.758–0.963) equals the overall one.
8. **Test.**
   - `test_build_table_pairs_base_with_instruct_on_site`
   - `test_h4_metrics_against_hand_values`
   - `test_h4_evaluation_is_invariant_to_row_order`
9. **Where.** `p33/h4.py`: `build_table`, `auroc`, `evaluate_group`, `criteria`.
10. **Why it matters.** It is the preregistered confirmatory claim, and it held everywhere.
    Practically, a cheap forward pass of the *base* model flags where a deployed assistant
    will silently write the wrong program.

---

## 5. Site-level vs role-level prediction

1. **Technical.**
   - `terminal_rate` is the instruct model's reversion rate for the same *terminal* in
     *other* templates, cross-fitted leave-one-template-out.
   - Δ role is AUROC(risk) − AUROC(terminal_rate).
2. **Simple.** Knowing "verbs are hard" is not the same as knowing "this verb, here, is
   hard".
3. **Example.**
   - Δ role is positive in 20/20 groups, with the interval above zero in 16.
   - The exceptions: Qwen2.5-Coder-0.5B (+0.03, +0.05) and 7B (+0.05, +0.05).
   - The role baseline alone reaches AUROC 0.60–0.86.
4. **In → out.** Two scores per site give the difference of AUROCs with an interval.
5. **Assumptions.** Cross-fitting prevents the baseline from seeing its own site's outcome.
6. **Silent failure.** Fitting `terminal_rate` on all templates, the site's own included,
   inflates the baseline.
7. **Symptom.** The baseline looks as good as the site score.
8. **Test.** No dedicated test; the cross-fit is in code review (`_crossfit_terminal_rate`).
   This is an honest gap.
9. **Where.** `p33/h4.py: _crossfit_terminal_rate`.
10. **Why it matters.** It answers the reviewer question "isn't this just symbol
    difficulty?": mostly no. The 0.5B and 7B exceptions are worth a sentence in the paper.

---

## 6. In-context extinction: first switch vs a switch that holds

1. **Technical.**
   - `k*` is the first upward zero-crossing of M(k) over k ∈ {0, 1, 2, 4, 8, 16, 32}
     examples, linearly interpolated.
   - `sustained_k` is the first rung after which M stays ≥ 0 up to 32.
2. **Simple.** How many examples until the model writes the new word, and how many until it
   *keeps* writing it?
3. **Example.**
   - The median first switch is **2.06** examples (3,469 crossers).
   - The median rung where the switch starts holding is **8** (2,912 sites).
   - 92.8–99.5% of curves wobble.
4. **In → out.** 7 margins per site give `k*`, `sustained_k` and non-monotone flags.
5. **Assumptions.**
   - Demonstrations are leak-free and nested, so rung 4 contains rung 2.
   - Interpolation is linear between rungs.
6. **Silent failure.**
   - Demonstrations that contain the answer (the old "~6" headline).
   - Treating a crossed-then-dropped curve as censored.
7. **Symptom.** Suspiciously fast, smooth curves.
8. **Test.**
   - `test_kstar_first_crossing_interpolated`
   - `test_crossed_then_dropped_is_not_censored`
   - `test_nonmonotone_flag_and_sustained_crossing`
   - `test_no_demonstration_leaks_in_any_ladder_row`
9. **Where.** `p33/kstar.py: compute`; `p33/demos.py: for_site, audit`.
10. **Why it matters.** Adaptation is **fast but fragile**: models flip early and then slip
    back. That is a finding about in-context learning, not just about DSLs, and the gap
    between 2 and 8 examples is a crisp, quotable number.

---

## 7. Censoring and Kaplan–Meier

1. **Technical.**
   - A site that never crosses by 32 examples is right-censored at 32.
   - The KM estimator is S(t) = ∏(1 − dⱼ/nⱼ), and the median is the first t with S ≤ 0.5.
2. **Simple.** "More than 32" is an answer, not a blank. Throwing it away makes the habit look
   easier to break.
3. **Example.**
   - 784 of 4,253 initially-wrong site-ladders (18.4%) never switched.
   - Per model and family, censoring is 6–29%.
4. **In → out.** (time, event) pairs give a survival curve, a median and a bootstrap interval
   over templates.
5. **Assumptions.**
   - Censoring is non-informative.
   - This is debatable: hard sites are exactly the censored ones, so medians are
     conditional summaries.
6. **Silent failure.** Taking the median among crossers only. It is reported, labelled
   "diagnostic".
7. **Symptom.** Medians that drop sharply when censored sites are removed.
8. **Test.** `test_kaplan_meier_hand_example`,
   `test_median_among_crossers_is_labelled_diagnostic_and_drops_censored`.
9. **Where.** `p33/kstar.py: kaplan_meier`.
10. **Why it matters.** It is the honest form of the primary endpoint, and you will need this
    sentence when a reviewer asks why you didn't just average `k*`.

---

## 8. Grammar familiarity and the "familiarity trap" (exploratory)

1. **Technical.**
   - The same IR is written in `dom` (JS-like) and `blk` (block grammar).
   - Lexicons respell 25%, 50% or 75% of roles.
2. **Simple.** A language that looks *almost* like one you know is harder to switch into than
   one that looks clearly different.
3. **Example.**
   - Median examples to switch in `dom`: 25% respelled 5.40, 50% 1.57, 75% 2.15.
   - In `blk`: 10.19, 5.80 and 6.19.
   - `blk` takes 2–4× more examples than `dom`.
4. **In → out.** KM per family × density.
5. **Assumptions.**
   - Densities are represented by 1 / 1 / 3 lexicons, so density and lexicon are confounded.
   - Not preregistered.
6. **Silent failure.** Reading a one-lexicon contrast as a law.
7. **Symptom.** The pattern reverses with a second `d25` lexicon. Untested.
8. **Test.** None. This is exploratory analysis of exported tables.
9. **Where.** `analysis_addenda/exploratory/adaptation_by_role_density.txt`, written by
   `explore_density.py`.
10. **Why it matters.** It is a striking, testable hypothesis for a follow-up preregistration.
    It must be labelled exploratory in the paper.

---

## 9. Symbol class: sigils, keywords, verbs (exploratory)

1. **Technical.** The stratum is the role of the respelled symbol: a punctuation sigil
   (`#`, `.`), a keyword (`mesh`, `lasso`) or a verb (`metalness`, `duplicate`).
2. **Simple.** Punctuation is easy to re-learn. Words carry meaning the model won't let go
   of.
3. **Example.**
   - Median examples to switch: sigils 1.28 and keywords 2.85 in `dom`; verbs 6.57 (`dom`)
     and 11.36 (`blk`).
   - Verbs never switch at 34–35% of sites.
   - Arm B shows the same ordering in real generation: reversion given reach is 9–11%
     (sigils), 18–23% (keywords) and 29–43% (verbs).
4. **In → out.** KM per stratum; hurdle per stratum.
5. **Assumptions.** Strata differ in length and frequency too (preregistration §8: sigil and
   verb token-length signatures barely overlap). The contrast is descriptive.
6. **Silent failure.** Attributing the verb effect to "meaning" when it could be token length
   or frequency.
7. **Symptom.** The effect disappears in length-matched strata. Not run.
8. **Test.** None for the contrast. The stratum label itself comes from `sites2`.
9. **Where.** `site_inventory.csv` and `kstar_survival.csv` (`stratum` column);
   `arm_b_hurdle.csv` (stratum rows).
10. **Why it matters.** Two independent methods, margins and generation, agree on the
    ordering. That is the most interesting exploratory result for the discussion section.

---

## 10. The generation hurdle (Arm B)

1. **Technical.**
   - From a natural-language request plus the table and 4 examples, an instruct model
     generates a program.
   - **Reach**: the normalized program reproduces the target up to the site.
   - **Revert given reach**: the next token is the old spelling.
   - Both are reported separately; the product is "alongside, never instead".
2. **Simple.** First, did the model even write the same program up to the tricky spot? Only
   then: did it write the old word there?
3. **Example.**
   - Reach is 13.5% overall: 2.9% for the 0.5B model, 32.8% for 72B-Instruct on `dom`.
   - Reversion given reach is 19.8%.
   - 9.6% of programs are fully correct; 38.5% do not parse.
4. **In → out.** A generated text gives a bucket (lex fail, parse fail, vacuous, wrong,
   correct) plus per-site reach and outcome.
5. **Assumptions.**
   - Exact-prefix matching after layout normalization.
   - A semantically equivalent program written differently does not "reach".
6. **Silent failure.** Multiplying reach × reversion into one number hides that small models
   rarely get there at all.
7. **Symptom.** A tiny model looks "safe" because it reverts rarely, while it almost never
   writes the program.
8. **Test.** `test_reach_and_conditional_reversion_are_separate`,
   `test_five_bucket_evaluation`, `test_extraction_and_layout_normalisation`.
9. **Where.** `p33/armb.py`: `evaluate`, `observe`, `hurdle`.
10. **Why it matters.** It ties the margin measurements to behaviour. When models do write
    the code, they revert at about 1 in 5 sites, more for verbs.

---

## 11. Repair: silent vs loud errors (H5)

1. **Technical.**
   - Repaired roles are respelled from the `beta` alphabet, which is disjoint from CSS.
   - The arms: targeted (the 3 highest base-model risk roles), random (3 roles × 5 seeds) and
     global (all reassigned roles).
   - Each repair is IR-proven over 284 programs.
   - The metric is (reversions before − after) over *all* sites in the cell, divided by the
     number of changed roles.
2. **Simple.** Rename the dangerous words to something unfamiliar so that mistakes become
   obvious errors, not silent wrong programs.
3. **Example.**
   - Targeted beats random in only 43 of 100 cells (mean −0.41).
   - Global repair cut reversions at repaired sites from 14,459 to 4,696 and silent errors to
     **0**.
   - Partial repairs left most errors silent: 2,672 of 2,804 for targeted.
4. **In → out.** A repaired lexicon re-scores every site; counts by arm.
5. **Assumptions.**
   - Role risk transfers from the base model, which is H4.
   - The metric credits the changed symbols with effects on *all* sites.
6. **Silent failure.** These lexicons **permute** familiar spellings, so a repaired role's old
   spelling usually still means *another* role. A partial repair cannot make the error loud.
7. **Symptom.** In the worked cell, reversions at repaired sites rose (29 → 36, all silent)
   while control sites improved (39% → 8%). That shows the effect comes from changing the
   prompt, not from the repair.
8. **Test.** `test_every_arm_preserves_ir_over_the_whole_corpus`,
   `test_targeted_arm_ranks_by_base_risk_and_random_is_seeded`, `test_ir_proof_can_fail`.
9. **Where.** `p33/h5.py`: `define_arms`, `repaired_phi`, `ir_proof`, `score_h5_cell`;
   aggregation in `p33/export.py`.
10. **Why it matters.** A negative result with a mechanism. In permutation-style DSLs, only a
    global respelling eliminates silent errors. That is a design lesson for DSL authors, and
    worth reporting even though H5 failed.

---

## 12. Scale as an association (D11)

1. **Technical.**
   - OLS slope of each outcome on log₁₀(parameters) across Qwen2.5-Coder 0.5–32B, which share
     a tokenizer and training recipe.
   - Template-bootstrap intervals; Holm over 6 slopes.
2. **Simple.** Does making the same model family bigger change anything?
3. **Example.**
   - Reversion: no slope survives Holm. The largest is +0.033 per 10×, Holm p 0.072.
   - H4 AUROC in `dom`: −0.081 per 10×, Holm p < 0.003.
4. **In → out.** 6 points per outcome and family give a slope with an interval.
5. **Assumptions.**
   - Size is not randomized, and larger checkpoints differ in data and training as well.
   - Six points; a linear fit on the log scale.
6. **Silent failure.** Reading the AUROC slope as "big models are less predictable". The
   per-size values are not monotone (0.89, 0.96, 0.95, 0.76, 0.85, 0.79): the 7B dip and the
   lower 32B drive the slope.
7. **Symptom.** A significant slope that a single point can carry.
8. **Test.** `test_slope_recovers_a_known_trend_and_a_flat_one`,
   `test_ladder_is_the_six_registered_qwen_coder_sizes`.
9. **Where.** `scripts/scale_analysis.py`.
10. **Why it matters.** "Scale doesn't fix prior reliance" is a clean, preregistered (D10/D11)
    result that connects to the "LLMs lean on priors" literature.

---

## 13. Calibration transfer, and the disclosed gap

1. **Technical.**
   - Platt: p = σ(a + b·risk), with a and b fitted on development pairs only (0.5B, 1.5B) and
     frozen.
   - Metrics: ECE (10 bins), Brier and the calibration slope.
2. **Simple.** Does "80% risk" still mean an 80% chance on new mappings?
3. **Example.**
   - For the frozen pairs, ECE was 0.036–0.052, with slopes 0.83–1.18: calibration
     transferred.
   - The 8 other pairs had **no** frozen parameters. The export fitted calibration on held-out
     rows (in-sample, slope exactly 1.00) and labelled it `DEV_FREEZE`.
4. **In → out.** A risk gives a probability, and binned agreement with outcomes.
5. **Assumptions.** Transfer is only claimable where parameters were frozen.
6. **Silent failure.** Mislabelled in-sample calibration presented as frozen transfer. This
   one happened.
7. **Symptom.** A calibration slope of exactly 1.00. That is how it was found.
8. **Test.** `test_calibration_of_a_fitted_model_is_identity` (which explains the 1.00).
   There is no test that the label matches the source, which is the gap.
9. **Where.** `p33/export.py`, the H4 section, around the `calibration_source` assignment.
10. **Why it matters.** Report calibration only for the 0.5B and 1.5B pairs. AUROC and the
    criteria are rank-based and unaffected. See [08](08_issues_and_superseded_numbers.md).

---

## What the results say about the theory, in one paragraph

**Pretrained priors dominate.**

- Code models follow a redefined language only partially, at every scale from 0.5B to 72B.
- Telling them the rules shifts their preferences reliably, but by too little.
- Showing them examples flips most preferences after about 2 examples, but the flip is
  unstable until about 8, and 1 in 5 hard sites never flips within 32.

**Where they fail is predictable.**

- The base model's own hesitation predicts its instruct twin's failures (AUROC 0.76–0.96),
  beyond what symbol difficulty alone explains.
- Semantic words resist more than punctuation, in both scoring and generation.
- Because a permuted language keeps every familiar spelling meaningful, only a complete
  respelling removes silent errors.
