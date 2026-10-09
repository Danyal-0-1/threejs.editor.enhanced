# 04 — Retyping plan: the analysis code behind the held-out results

> **Scope.** The pipeline core (split, freeze, shards, scoring, `k*`, KM, H4 table,
> bootstrap) has its own retype plan:
> [`../sol_experiment_explained/04_retyping_and_reading_plan.md`](../sol_experiment_explained/04_retyping_and_reading_plan.md).
>
> This plan covers **only the code that turns merged rows into the results you now read**.
> Functions already on the previous list are linked, not repeated.
>
> **Line numbers** are for commit `78b2bcd`, the frozen code; `scale_analysis.py` is at `efee629`.

---

## 1. Inventory

Computed with `wc -l` and the Python AST, not estimated.

| module | lines | role in the results |
|---|---:|---|
| `src/p33/h4.py` | 468 | every H4 number: AUROC, AP, P@k, deltas, calibration, criteria |
| `src/p33/export.py` | 411 | assembles all 19 CSVs; aggregates Arm B and H5 |
| `src/p33/armb.py` | 289 | generation, buckets, reach and outcome |
| `../src/phase3_2/analysis.py` | 263 | cluster bootstrap, bootstrap p, Holm, rule effect |
| `scripts/scale_analysis.py` | 255 | D11 |
| `src/p33/h5.py` | 249 | repair arms, IR proof, re-scoring |
| `src/p33/kstar.py` | 166 | `k*`, KM, summaries |
| **total (the denominator)** | **2,101** | |

---

## 2. Triage

**LOAD-BEARING** for the results: a subtle mistake here changes a number without crashing.

| file | why |
|---|---|
| `h4.py` | The confirmatory verdict lives here. `evaluate_group` decides which rows enter each AUROC and how the deltas are bootstrapped. The calibration path is where the labelling gap is (08). |
| `analysis.py` | Every interval and every p. Multiplicity handling (P33-005) and the +1 smoothing of p values. |
| `export.py`, H5 and Arm B sections | The H5 metric's definition, which counts *all* sites, and the hurdle's pooling are decided here, not in `h5.py` or `armb.py`. |
| `h5.py: score_h5_cell` | Decides whether an error after repair is silent: `silent_error_after`. |
| `scale_analysis.py` | D11: the same template draw for all sizes; Holm over 6. |

**PLUMBING:** `armb.describe_*` (renders the natural-language requests), `export.write_csv`
and `meta`, `h4.pr_curve` and `roc_curve` (figures only).

---

## 3. The short list: read these first

| order | what | lines |
|---:|---|---|
| 1 | `h4.evaluate_group` | [h4.py:363–434](../src/p33/h4.py#L363) |
| 2 | `export.export_all`, H4 section | [export.py:310–340](../src/p33/export.py#L310) |
| 3 | `export.export_all`, H5 aggregation | [export.py:362–393](../src/p33/export.py#L362) |
| 4 | `h5.score_h5_cell` | [h5.py:200–246](../src/p33/h5.py#L200) |
| 5 | `scale_analysis.analyse` | [scale_analysis.py:122–185](../scripts/scale_analysis.py#L122) |

These five decide the four headline results: H4, H5, Arm B pooling and D11.

---

## 4. Data structures, in the order they flow

```
merged/arm_a.jsonl row  ── h4.build_table ──►  H4 table row {pair, site_id, template, risk, label, identity, length, …}
                                                    │  grouped by (pair, family, split)
                                                    ▼
                                    h4.evaluate_group ──► metric dicts {predictor, auroc, auprc, p_at_k, ece, …}
                                                          + difference dicts {delta_vs_<base>, ci_lo, ci_hi, p_one_sided}
                                                    ▼
                                    h4.criteria ──► {criterion, delta, ci, p_holm, status MET / NOT MET / NOT TESTABLE}

merged/primary.jsonl ladder rows ── kstar.compute ──► KStar(k_star, censored, nonmonotone, sustained_k, …)
                                                    ── kstar.km_from_kstars ──► KMSummary(median, n, n_events, curve)

merged/armb.jsonl  {bucket, site_obs[]}  ── export (345–360) ──► hurdle rows {p_reach, p_revert_given_reach, n_*}
merged/h5.jsonl    {arm, seed, repaired_role, reverted_after, silent_error_after}
                                         ── export (362–393) ──► arm rows {error_reduction_per_changed_symbol, control_degradation}

csv/arm_a_long.csv + csv/h4_predictions.csv ── scale_analysis.analyse ──► 6 slopes {slope, ci, p, p_holm}
```

---

## 5. One end-to-end path to retype

1. `export.export_all`: the H4 section. Freeze → `cal` and `thr` per pair (the gap).
2. `h4.evaluate_group`: the metrics, then the bootstrap of `auroc(risk) − auroc(baseline)`.
3. `analysis.cluster_bootstrap` *(previous plan)* → `analysis.bootstrap_pvalue_greater`.
4. `h4.criteria` *(previous plan)* → `analysis.holm` *(previous plan)* → the MET rows.
5. `h5.score_h5_cell` → `export.export_all`'s H5 section → the per-symbol metric.
6. `scale_analysis.analyse` → `slope`, `holm`.

---

## 6. What to retype: 312 lines, **14.9%** of 2,101

| function | file:lines | lines | why | in → out | invariant | test after |
|---|---|---:|---|---|---|---|
| `evaluate_group` | h4 363–434 | 72 | the confirmatory metrics | rows → metric and difference dicts | the same rows feed the score and the baseline; ties are threshold groups; a single class gives NOT ESTIMABLE | `test_h4_metrics_against_hand_values` · `test_single_class_labels_are_not_estimable_not_a_crash` · `test_h4_evaluation_is_invariant_to_row_order` |
| `bootstrap_pvalue_greater` | analysis 148–151 | 4 | every confirmatory p | draws → p | (#≤0 + 1)/(B + 1); never 0 | `test_holm_hand_example` (with Holm) |
| `calibration_slope_intercept` | h4 263–271 | 9 | why 8 pairs show exactly 1.00 | probs, labels → (a, b) | a fitted logistic model calibrates to (0, 1) on its own data | `test_calibration_of_a_fitted_model_is_identity` |
| `km_from_kstars` | kstar 152–157 | 6 | KStars → KM | list → KMSummary | censored items enter at the top rung | `test_kaplan_meier_hand_example` |
| `median_among_crossers` | kstar 160–166 | 7 | the diagnostic that must not be the headline | KStars → median | drops censored items, so it is labelled diagnostic | `test_median_among_crossers_is_labelled_diagnostic_and_drops_censored` |
| `extract_program` | armb 132–140 | 9 | what counts as "the program" in a generation | text → program | first fenced or complete program; deterministic | `test_extraction_and_layout_normalisation` |
| `evaluate` | armb 159–176 | 18 | the five buckets | text → bucket | exactly one parse, or PARSE_FAIL; zero operations means VACUOUS | `test_five_bucket_evaluation` |
| `score_h5_cell` | h5 200–246 | 47 | silent vs loud after repair | cell → rows | `silent_error_after` requires a SEMANTIC collision after repair; "no contrast" means excluded | `test_every_arm_preserves_ir_over_the_whole_corpus` |
| `export_all`, H4 section | export 310–340 | 31 | frozen vs refit calibration; where criteria rows are made | table → CSV rows | `cal = None` for unfrozen pairs, which is **the gap** | (no test of the label; see 08) |
| `export_all`, H5 section | export 362–393 | 32 | the per-symbol metric | h5 rows → arm rows | the numerator counts all ok sites in the cell, repaired and control | (none; the confound is in 08) |
| `slope` | scale_analysis 61–66 | 6 | OLS | xs, ys → b | `None` if Sxx = 0 | `test_slope_recovers_a_known_trend_and_a_flat_one` |
| `holm` | scale_analysis 69–75 | 7 | Holm over the D11 slopes | p dict → adjusted | monotone, capped at 1 | `test_bootstrap_is_deterministic_and_holm_is_applied` |
| `analyse` | scale_analysis 122–185 | 64 | D11 | rows → slopes | one template draw for every size; refuses a missing ladder model | `test_missing_ladder_model_is_refused` |

**Optional, +85 lines, for a total of 397 lines = 18.9%:**

| function | file:lines | lines | what it teaches |
|---|---|---:|---|
| `export_all`, Arm B section | export 345–360 | 16 | pooling and the "product alongside, never instead" note |
| `h5.prepare` | h5 125–173 | 49 | how the targeted arm ranks roles by *mean* base risk, ignoring how often each role occurs |
| `normalize_layout` | armb 143–156 | 14 | why "reach" is a strict text match |
| `youden_threshold` | h4 274–284 | 11 | the frozen decision threshold (only for the two development pairs) |

---

## 7. What to ignore for now

- `armb.describe_*` and `build_prompt`: the natural-language request rendering. Read one
  generated row in `csv/arm_b_generations.csv` instead.
- `h4.pr_curve`, `roc_curve`, `ece` and `brier`: covered by the previous plan or trivial.
- `export.write_csv` and `meta`.
- The figure code in `plots.py`.

---

## 8. The things you are most likely to get wrong when *reading* these results

### (1) Reading H5's per-symbol number as "what the repair did at the repaired sites"

- **Where:** `export.py` 362–393.
- **Reality:** the numerator is reversions before minus after over **all** sites in the cell.
  In the worked cell, the repaired sites got worse (29 → 36) and the control sites improved
  (61 → 13).
- **Check:** compare `reversions_after_repaired` with `control_reversion_after` in
  `h5_budget_outcomes.csv`.

### (2) Multiplying the hurdle

- **Where:** `arm_b_hurdle.csv`.
- **Reality:** a 0.5B model "reverts" in 0.7% of sites only because it reaches 2.9% of them.
- **Check:** always quote reach and reversion-given-reach together.

### (3) Trusting the `calibration_source` label

- **Reality:** `DEV_FREEZE` on all 10 pairs, but only 2 had frozen parameters.
- **Check:** a calibration slope of exactly 1.00 means in-sample.

### (4) Treating `p_holm = 0.0009995` as an exact p

- **Reality:** it is the floor of a 2,000-draw bootstrap with +1 smoothing, doubled by Holm.
  Report it as "p ≤ 0.001".

### (5) Pooling the two grammar families

- **Reality:** the criteria are per family, by registration. `blk` is a weak family (D1) and
  never a held-out-grammar confirmation.

### (6) Using the median among crossers as the adaptation number

- **Reality:** it drops the 18% of sites that never switch. The KM median is the endpoint.

### (7) Over-reading the D11 AUROC slope

- **Reality:** the six points are non-monotone (0.89, 0.96, 0.95, 0.76, 0.85, 0.79). The 7B
  dip and the 32B point carry the slope.

### (8) Treating the density pattern (25% harder than 50–75%) as established

- **Reality:** it is exploratory, with one lexicon each for 25% and 50%.

---

## 9. AI-code audit: the constants behind these results

"Apparently arbitrary" is used freely: it is the truthful label for most of them.

| value | where | role | provenance |
|---|---|---|---|
| `B = 2000`, seed 20261002 | config, every bootstrap | intervals and p | **Conventional**; the exact values are **apparently arbitrary** |
| +1 smoothing in the bootstrap p | `analysis.bootstrap_pvalue_greater` | p never 0 | **Standard practice** (Davison and Hinkley style); no alternative was considered |
| `min_clusters = 8` | `analysis` | no interval below | **Judgment call, apparently arbitrary**; never binding here (80 templates) |
| 10 ECE bins | config | calibration | **Conventional, apparently arbitrary** |
| H5 `budget = 3` | config | roles per targeted or random arm | **Preregistered, apparently arbitrary** |
| H5 random seeds 1–5 | config | random arms | **Apparently arbitrary**; 5 seeds is a small reference distribution |
| H5 `low_risk_tolerance = 0.02` | config | control degradation | **Preregistered judgment call** |
| targeted ranking by **mean** base risk | `h5.define_arms` | which roles to repair | **Design choice**; ignores frequency, which the results suggest matters |
| repair alphabet `beta` | `h5.REPAIR_SOURCE` | new spellings | **Design choice**: disjoint from CSS |
| Arm B `n_demos = 4` | config | examples in the generation prompt | **Apparently arbitrary** |
| Arm B `max_new_tokens = 192` | config | generation cap | **Checked with headroom** at design (2.6× the longest target); small models hit it |
| greedy decoding | `armb._decoding` | determinism | **Design choice** for reproducibility |
| exact-prefix "reach" | `armb.observe` | when a site counts | **Design choice**: strict, so a reach is unambiguous |
| ladder 0, 1, 2, 4, 8, 16, 32 | config | dose | **Design choice** (doubling); the top rung is checked |
| D11: OLS on log₁₀ of *nominal* size | `scale_analysis` | slope | **Specified in D11**; nominal rather than exact parameter counts is **apparently arbitrary** |
| D11: Holm over 6 | `scale_analysis` | multiplicity | **Specified in D11**, following the registered convention |
| Platt + Youden, development pairs only | `freeze.build_payload` | calibration | **Standard**; covering only 2 of 10 held-out pairs is a **gap**, not a choice |

---

## 10. Addendum (2026-10-09): the paper-figure script

[`scripts/paper_figures.py`](../scripts/paper_figures.py) has 1,432 lines and draws every paper
figure (06 §8). It is **not added to the 2,101-line denominator**. It restates frozen numbers and
refuses to run unless they agree, so a mistake in it shows up as a refusal, not as a wrong
result. Most of it is layout. About 100 lines carry statistics, and those are worth retyping:

| function | lines | count | why | invariant | test after |
|---|---|---:|---|---|---|
| `draws` | [170–183](../scripts/paper_figures.py#L170) | 14 | the template resample as a B × T count matrix | the same `random.Random` calls, in the same order, as `scale_analysis.analyse` | `test_figure_intervals_are_the_d11_intervals` |
| `interval` | [186–193](../scripts/paper_figures.py#L186) | 8 | the 95% percentile interval | D11's order statistics: `int(0.025(n−1))` and `ceil(0.975(n−1))` | same |
| `ratio` | [196–200](../scripts/paper_figures.py#L196) | 5 | every rate: reversion, reach, reversion given reach | one matrix product per numerator and denominator | same |
| `auroc_w` | [203–219](../scripts/paper_figures.py#L203) | 17 | AUROC for 2,000 resamples at once | weight w = the template drawn w times; ties count ½ | `test_weighted_auroc_equals_auroc_on_replicated_rows` |
| `lexicon_mean` | [425–436](../scripts/paper_figures.py#L425) | 12 | the rule effect averaged over lexicons, as 00 §5 reports it | each lexicon weighs the same; one resample applies to all five | check 2 (420 cells) |
| the D11 check | [500–519](../scripts/paper_figures.py#L500) | 20 | ties the figure intervals to D11 | 36 values and intervals, to 1e-9 | check 5 |
| first against lasting switch | [741–763](../scripts/paper_figures.py#L741) | 23 | Figure 5c and Table 3b | the denominator is **every** initially wrong site; the dashed curve stops at 16 | none (compare with 00 §6) |

**Optional, +61 lines:** the rule-effect and reversion checks
([442–469](../scripts/paper_figures.py#L442)), the Arm B check
([818–836](../scripts/paper_figures.py#L818)) and the H5 per-model aggregation
([904–917](../scripts/paper_figures.py#L904)).

**Ignore:** `rows_layout`, `style_rows`, `dodge`, the `fig.legend` calls, captions and table
formatting.

**The exploratory companion.** [`scripts/exploratory_checks.py`](../scripts/exploratory_checks.py)
(346 lines) makes the three post hoc checks in [09 §3](09_conclusions_claim_strength_and_venues.md).
Two parts are worth reading:

- the cross-family block, [134–210](../scripts/exploratory_checks.py#L134). Its invariant: the
  own-base AUROC must equal the frozen H4 AUROC, or it refuses.
- the wobble block, [302–338](../scripts/exploratory_checks.py#L302). It makes the size of a
  dip explicit, where the frozen `nonmonotone` flag counts any decrease.

`auroc_reps` repeats `paper_figures.auroc_w`, but returns every resample, so that differences
between two scores can be bootstrapped on the same draws.

**AI-code audit, figure choices:**

| value | where | role | provenance |
|---|---|---|---|
| the D11 random streams, reused for the figure intervals | `W_rev`, `draws` | ladder intervals equal D11's | **Design choice**, so that one number never has two intervals |
| stream `<grammar>/figure/arm_b` | Arm B intervals | a new stream | **Apparently arbitrary** name; any fixed key works |
| rule effect averaged over lexicons, reversion pooled over sites | `lexicon_mean`, `ratio` | Figure 3, Tables C1 and C2 | **Chosen to match the results documents** (00 §4–5) and D11 |
| the "holds" curve stops at rung 16 | Figure 5c | a switch first seen at 32 cannot be checked | **Design choice**, stated in the caption |
| dodge: models within 0.08 dex share a cluster, 0.045 dex apart | `dodge` | Figure 4 | **Apparently arbitrary**, visual only |
| reliability bins with fewer than 10 sites hidden | Figure A1 | calibration | **Judgment call**, apparently arbitrary |
| 6.5 in wide, 7–8 pt type, Okabe–Ito colours | `rcParams` | every figure | **Conventional** for two-column papers |

---

## After retyping

Re-derive three numbers by hand from the CSVs and compare with [02](02_mathematics_and_statistics.md):

1. the 32B `dom` AUROC (0.7861);
2. the 72B-Instruct `dom` reach (497 / 1,515);
3. the targeted per-symbol value of the worked H5 cell (13.67).
