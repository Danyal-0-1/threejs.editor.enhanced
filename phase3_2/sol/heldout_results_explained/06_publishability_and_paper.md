# 06 — Is it publishable, and how to structure the paper

> This is an honest assessment for planning the paper. Every number comes from
> [00](00_complete_results.md).
>
> Venue names and related-work entries are **starting points to verify**. They were not
> checked from this environment.

---

## 1. Short answer

**Yes.**

- **The confirmatory core is clean.** H4 was preregistered, frozen, tested once and met in
  every group.
- **It is rare in LLM evaluation.** Few studies have a design this rigorous.
- **It has a story.** The descriptive results add a clear one: scale doesn't fix the habit,
  adaptation is fast but fragile, and only complete respelling removes silent errors.
- **The weak points are known, bounded and already disclosed:** one domain, no valid held-out
  grammar, a negative H5, and three gaps in the frozen analysis.

---

## 2. The contributions, strongest first

| # | contribution | evidence type | key number |
|---|---|---|---|
| 1 | **The base model's margin predicts where its instruct twin reverts**, beyond symbol difficulty | **confirmatory** (H4) | AUROC 0.76–0.96; C1 and C2 met for 10/10 pairs × 2 families; Δ vs role-level baseline > 0 in 20/20 (CI > 0 in 16) |
| 2 | **Prior reliance does not shrink with scale** | registered (D10/D11) + descriptive | reversion 40–56% at every size, 0.5B–72B; no D11 slope survives Holm |
| 3 | **Rules help, but too little** | descriptive, length-controlled | +0.16…+0.62 nats; reversion falls only ~5–6 points |
| 4 | **In-context adaptation is fast but fragile** | primary endpoint (KM) | KM median to the first switch 1.4–4.6 (`dom`) and 3.3–11.6 (`blk`) examples; among sites that switch, ~2 to the first switch and ~8 to one that lasts; 18% never switch within 32; 31% of switches fall back later, by a median of −0.76 nats ([09 §3.3](09_conclusions_claim_strength_and_venues.md)) |
| 5 | **Behavioural confirmation in generation** | descriptive (Arm B) | 1 in 5 reached sites revert; verbs most (29–43%) |
| 6 | **Targeted repair fails, and why** | preregistered H5, not supported, with a mechanism | targeted beats random in 43/100 cells; global respelling → 0 silent errors |
| 7 | **A reusable rigorous protocol** | methods | code-hash-enforced freeze/unlock, leak-free demonstrations, cluster bootstrap, KM with censoring |

**Exploratory, for the discussion section and a follow-up study:**

- verbs ≫ keywords > sigils;
- a partly changed language is harder to adopt than a mostly changed one;
- instruct models adapt more slowly than their base.

---

## 3. How a reviewer will see it

**Strengths they will credit:**

- preregistration with real enforcement: the freeze, a code-hash drift check, and a typed
  unlock;
- held-out mappings *and* held-out models, with a size ladder at a fixed tokenizer;
- exact-site measurement, with a length-matched control;
- correct clustering: templates as the unit, not sites;
- censoring handled with Kaplan–Meier;
- negative results reported, and analysis gaps disclosed.

**Likely objections, and your answers:**

| objection | answer |
|---|---|
| "One synthetic DSL; does this generalize?" | Two grammar families and five unseen lexicons; models from four families. Generalization to other DSLs is the stated limitation and the next study. |
| "Isn't H4 trivial: the instruct model is fine-tuned from the base?" | That *is* the hypothesis: the prior survives tuning. Non-trivial because the score beats a role-level baseline in 20/20 groups and holds within lexicons. *Exploratory:* the model's own base also beats a consensus of other-lineage bases in 20/20 groups (+0.12 to +0.35 AUROC), so the prediction is inherited, not just shared site difficulty ([09 §3.1](09_conclusions_claim_strength_and_venues.md)). |
| "Log-prob margins aren't behaviour." | Arm B: in real generation, about 20% of reached sites revert. The role ordering (verb > keyword > sigil) matches the margins at the same number of worked examples (4) in both grammars; levels differ, because reached sites are a selected subset ([09 §3.2](09_conclusions_claim_strength_and_venues.md)). |
| "Why should we care about permuted spellings?" | They produce *silent* wrong programs: the code runs but does the wrong thing. That is the dangerous failure mode in DSL deployment. |
| "H5 failed, so is the repair story weak?" | The failure has a mechanism (permutations keep old spellings meaningful) and a positive counterpart: global respelling eliminates silent errors. |
| "Calibration claims?" | Only for the two pairs with frozen parameters (ECE 0.036–0.052). The other eight are disclosed as in-sample (D12). |
| "Was anything tuned on test data?" | No. Frozen code hashes were re-verified on every held-out job. D11 was approved before outcomes were seen, with a git timestamp. |

---

## 4. Claims you can and cannot make

| ✅ you can claim | ❌ do not claim |
|---|---|
| base-model margins predict instruct reversions on held-out mappings (confirmatory) | generalization to new *grammars* (C3 not testable) |
| reversion is substantial (40–56%) at every tested size, 0.5B–72B | that size *causes* anything (sizes are not randomized) |
| the token table shifts preferences consistently but modestly | that models "ignore" the rules (they don't; the shift is real) |
| KM median to the first switch 1.4–4.6 (`dom`), 3.3–11.6 (`blk`); among switchers ≈ 2 to the first switch and ≈ 8 to a lasting one; 18% never within 32 | a single "number of examples" without censoring and wobble; "≈ 2" or "≈ 8" without "among the sites that switch" |
| about 1 in 5 reached sites revert in generation | an overall generation "error rate" from multiplying the hurdle |
| targeted repair ≤ random; global respelling removes silent errors | that targeting by risk can never work (only this rule, with this metric) |
| *(exploratory)* verbs are stickiest; partial remaps are harder | the exploratory patterns as findings without a "exploratory" label |
| calibration transfers for the two frozen pairs | calibration for the other eight pairs |

---

## 5. Title options

1. **Familiar Spellings Win: Code Language Models Revert to Pretrained Syntax Under Redefined DSLs — and Their Base Models Predict Where**
2. **Do Code LLMs Follow Redefined Syntax? A Preregistered Study of Prior Reliance from 0.5B to 72B**
3. **Silent Reversions: Predicting and Repairing Where Code Models Ignore a Redefined Language**

---

## 6. Abstract (draft; every number from this run)

> Code language models are increasingly asked to write domain-specific languages whose
> surface conventions differ from those seen in pretraining. We ask whether they follow
> redefined syntax or revert to familiar spellings.
>
> Using 3DOM, a 3D-scene DSL rendered in two grammar families under lexicons that permute
> 25–75% of its symbols, we measure at each decision site the log-probability margin between
> the redefined and the familiar spelling. The study was preregistered: designed on four
> development checkpoints, frozen with code-hash enforcement, and tested once on held-out
> mappings and 21 checkpoints from 0.5B to 72B parameters.
>
> Models revert at 40–56% of sites even when given the full token table, with no detectable
> trend across a six-size model ladder. The table shifts preferences consistently
> (+0.16 to +0.62 nats) but rarely enough to change decisions. With leak-free worked examples,
> sites that switch do so after a median of about two examples, but a switch that lasts takes
> about eight, and 18% of initially wrong sites never switch within 32.
>
> A base model's margin predicts which sites its instruction-tuned twin gets wrong (AUROC
> 0.76–0.96), meeting both preregistered criteria for all ten model pairs in both grammar
> families and exceeding a role-level difficulty baseline. In free generation, one in five
> reached sites reverts, verbs most often. Respelling the predicted-riskiest symbols is no
> better than random, whereas respelling all reassigned symbols eliminates silent errors:
> in a permuted language every familiar spelling remains meaningful.

---

## 7. Paper structure

Each section gives its content and the source files behind it.

### 1. Introduction (~1 page)

- DSLs, silent wrong programs, and the question "rules or priors?".
- The three findings: prediction (confirmatory), scale invariance, fragile adaptation.
- The contributions list (§2 above).

### 2. Related work (~0.75 page)

- Prior reliance in code LLMs (PLSemanticsBench, "LLMs lean on priors").
- Semantic overriding in in-context learning (flipped labels).
- Robustness of code models to renaming.
- Scaling, and inverse scaling.
- Preregistration in ML.

### 3. The 3DOM testbed (~1 page)

- The language and the two grammar families.
- Lexicons (φ-maps), with permutation density 25/50/75%.
- **Sites and semantic collisions:** why reversions are silent.
- **Figure 1:** one program in standard and remapped spellings, with a decision site marked.
- **Source:** [`EXPERIMENT_IN_ONE_FILE.md §1, §3`](../sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md).

### 4. Measurement (~0.75 page)

- The first-divergent-token margin.
- The fp32 output head.
- Refusals instead of zeros.
- The `rule`, `norule` and length-matched conditions.
- The extinction ladder: leak-free, nested demonstrations.
- **Source:** [02](02_mathematics_and_statistics.md) and the earlier `02` doc.

### 5. Design and preregistration (~1 page)

- **The split:** development vs held-out cells, models and mappings.
- **Enforcement:** the freeze, the unlock and the code-hash drift check.
- **Hypotheses and criteria:** H4 C1 to C3; H5; `k*`; D10/D11.
- **Deviations D1–D12,** summarized in a box.
- **Models:** 21 checkpoints. **Compute:** 40.8 A100 GPU-hours.
- **Table 1:** models × roles in the design.

### 6. Results (~3 pages)

Every figure and table named here is already made, in
`phase3_3/sol_results/heldout-20261007a/analysis_addenda/paper_figures/` (**P/** below), with a
draft caption for each in `P/CAPTIONS.md` (§8).

- **6.1 Predicting reversions (H4, confirmatory).**
  - **Table 2:** `P/tables/T2_h4`: AUROC with intervals, AUPRC, within-lexicon AUROC, ΔC1,
    ΔC2, Δ-role and the criteria, for 10 pairs × 2 families.
  - **Figure 2:** `P/fig2_h4`: AUROC per pair against the role-level and length baselines,
    one panel per family. It replaces the 20 overlapping ROC curves.
- **6.2 Reversion and the rule effect.**
  - **Figure 3:** `P/fig3_reversion`: reversion per checkpoint, with and without the table,
    and the length-matched control.
  - Tables C1 and C2 (appendix): the rates, and the rule effect in nats, with intervals.
- **6.3 Scale.**
  - **Figure 4:** `P/fig4_scale`: reversion and H4 AUROC against log size. The ladder
    intervals equal the D11 intervals exactly. Table C4 gives the six slopes.
- **6.4 Adaptation.**
  - **Figure 5:** `P/fig5_adaptation`: Kaplan–Meier curves, the KM median per checkpoint,
    and the first switch against a switch that lasts.
  - **Table 3:** `P/tables/T3_adaptation` (KM medians with censoring) and `T3b` (first
    against lasting switch).
  - The KM medians are the endpoint. "About 2 against about 8" holds **among the sites that
    switch, or hold**, and must be worded so.
- **6.5 Generation (Arm B).**
  - **Figure 6:** `P/fig6_generation`: reach and reversion given reach, with template
    intervals; reversion given reach by role.
  - Tables C3 and C3b.
- **6.6 Repair (H5).**
  - **Table 4:** `P/tables/T4_repair` (targeted, random and global per-symbol reductions) and
    `T4b_repaired_sites` (silent errors after repair).
  - **Figure 7:** `P/fig7_repair`: the registered metric per model, and what happens at the
    repaired sites.
  - The worked cell as an inset, showing that the control sites drive the per-symbol metric.

### 7. Exploratory analyses (~0.5 page, clearly labelled)

- Roles (Arm B and extinction agree).
- Remap density, with the confound noted.
- Instruct vs base adaptation.

### 8. Discussion (~0.75 page)

- **For DSL designers:** avoid permutations of familiar spellings. If they can't be avoided,
  respell *completely* into an unfamiliar alphabet.
- **For deployment:** base-model margins work as a cheap risk screen.
- **For in-context learning research:** among sites that switch, the flip at ~2 examples and
  the lasting switch at ~8 show that preference flips are not learning curves.

### 9. Limitations (~0.5 page)

- One domain; synthetic lexicons.
- No valid held-out grammar (D1).
- Sizes not randomized.
- Calibration transfer only for 2 pairs.
- The H5 interval test was not implemented, and its metric counts all sites.
- Arm B's reach is strict; a minor extraction artifact (08).
- Exploratory density confound.

### 10. Conclusion (~0.25 page)

### Appendices

- A: the full preregistration and deviations D1–D12.
- B: all lexicons, prompts and the token table.
- C: per-model tables (`P/tables/C1`–`C4`; all of [00](00_complete_results.md)), and the
  appendix figures `P/figA1`–`figA4` with tables `A1`–`A5`.
- D: reproducibility (code, hashes, commands, compute, the frozen commit `78b2bcd`).
- E: datasheet for the benchmark.

---

## 8. The figures for the paper

**Use `analysis_addenda/paper_figures/` (P/), not `plots/`.** The 12 figures in `plots/` are the
frozen pipeline's diagnostics. They show every model, family and lexicon at once, carry a
provenance stamp, and two are tens of thousands of pixels tall. They stay unchanged, because
they are registered outputs of the frozen code. The paper figures are drawn by
[`scripts/paper_figures.py`](../scripts/paper_figures.py), which sits outside the frozen source
set, like the D11 script.

**How they are made:**

- **Text.** One message per figure, with panel letters and no stamps or numbers inside. The
  captions are in `P/CAPTIONS.md` and every number is in `P/tables/` (CSV + Markdown).
- **Format.** PDF (vector, fonts embedded, for LaTeX), SVG and 300-dpi PNG, 6.5 in wide, with
  7–8 pt type. Okabe–Ito colours, safe for colour-blind readers; dom in black, blk in grey.
  `P/ALL_FIGURES.pdf` has all ten on one page each, for a quick review.
- **Intervals.** 95% template-cluster bootstrap, B = 2000, seed 20261002, drawn exactly as the
  D11 script draws them.
- **Checks.** Before drawing, the script compares everything it recomputes with the frozen
  export, and refuses on any mismatch. There are eight checks, listed in `P/PROVENANCE.md`.

| paper | file in P/ | replaces in `plots/` |
|---|---|---|
| Figure 2 | `fig2_h4` | `h4_roc_pr_calibration` (ROC and PR curves) |
| Figure 3 | `fig3_reversion` | `rule_effect_forest` |
| Figure 4 | `fig4_scale` | `model_size_tokenizer` (linear axis, no intervals) |
| Figure 5 | `fig5_adaptation` | `extinction_trajectories_km` |
| Figure 6 | `fig6_generation` | `armb_hurdle_outcomes` |
| Figure 7 (or Table 4 alone) | `fig7_repair` | `h5_benefit_per_symbol` (now with the silent-error panel) |
| Appendix A1 | `figA1_calibration` | the calibration panel, now for the two frozen pairs only |
| Appendix A2 | `figA2_paraphrase` | `paraphrase_sensitivity` |
| Appendix A3 | `figA3_roles` | `family_mapping_model_stratum` |
| Appendix A4 | `figA4_margins` | `margin_reversion_distributions` |
| Table A5 | `tables/A5_tokenization` | `fertility_tokenization`: a null check, so a table |
| — | — | `h2_three_scale` and `power_curves`: omitted. H2 is not testable, and power was development planning |

**Tables.** `T1_models` (with revisions and tokenizers), `T2_h4`, `T3_adaptation`,
`T3b_first_vs_lasting_switch`, `T4_repair` and `T4b_repaired_sites` are for the main text;
`C1`–`C4` and `A1`–`A5` are for the appendix.

---

## 9. Threats to validity

| kind | threat | mitigation already in place | remaining |
|---|---|---|---|
| internal | analysis tuned to results | freeze + drift check; D11 pre-approved | 3 disclosed gaps (D12) |
| internal | demonstration leakage | `demos.audit` raises on any leak | — |
| construct | margin ≠ behaviour | Arm B generation agrees | Arm B reach is strict and small for small models |
| construct | "verbs" confounded with length and frequency | — | exploratory only |
| statistical | clustering | template-cluster bootstrap | lexicon-level clustering not modelled |
| statistical | multiplicity | Holm within the registered families | many descriptive comparisons, unadjusted |
| external | one DSL, synthetic permutations | 2 grammars, 5 unseen lexicons, 4 model families | other DSLs, natural respellings |

---

## 10. Before submitting: a prioritized checklist

**Must:**

- [ ] Report calibration only for the 0.5B and 1.5B pairs; footnote the in-sample values (08, D12).
      The figure is ready: `P/figA1_calibration`.
- [ ] State that H5's registered interval test was not implemented; give the descriptive result.
- [x] Redraw the scale figure from the D11 output (log axis, intervals): `P/fig4_scale`.
- [x] Redraw every figure for publication, with the numbers in tables: `P/` (§8).
- [ ] Release the benchmark (templates, lexicons, prompts), the frozen code (`78b2bcd`) and the
      analysis scripts, with the commands from [03 §11](03_code_and_pipeline.md).

**Should:**

- [ ] An exploratory, frequency-aware H5 re-analysis (rank roles by risk × site count), labelled
      post hoc.
- [ ] An exploratory per-role H4 table, to show the prediction is not driven by verbs alone.
- [x] Confidence intervals on the Arm B rates, with a template bootstrap: `P/tables/C3_generation`.

**Could:**

- [ ] A second DSL, or natural (non-permuted) respellings, preregistered as a follow-up.
- [ ] A preregistered test of the density effect, with several lexicons per density.
- [ ] Mechanism work: does attention to the token table predict the margin shift?

---

## 11. Venues

**Superseded by [09 §6](09_conclusions_claim_strength_and_venues.md).** That section has the
venue list, with dates checked on 2026-10-09, fit, realistic chances, and a recommended plan:
ACL 2027 through the January 2027 ARR cycle, with COLM 2027 or TMLR as alternatives.

---

## 12. Related-work starting points (check each before citing; two verified on 2026-10-09)

- *LLMs Lean on Priors, Not Programming Language Semantics* (PLSemanticsBench), from your
  literature review: the closest prior work.
- **Verified:** Miceli-Barone, Barez, Konstas & Cohen, *The Larger They Are, the Harder They
  Fail: Language Models do not Recognize Identifier Swaps in Python*, Findings of ACL 2023.
  This is the inverse-scaling paper cited in D10.
- **Verified:** Wu et al., *Reasoning or Reciting? Exploring the Capabilities and Limitations
  of Language Models Through Counterfactual Tasks*, NAACL 2024. Its counterfactual task
  variants include programming.
- Human parallels (Stroop, capture errors, extinction, first-language transfer):
  [10](10_humans_and_the_brain.md).
- In-context learning with flipped or semantically unrelated labels: larger models overriding
  semantic priors (Wei et al., 2023). Verify the title and venue.
- Robustness of code generation to renaming and perturbation (e.g. ReCode). Verify.
- Preregistration in NLP/ML (e.g. van Miltenburg et al.). Verify.
