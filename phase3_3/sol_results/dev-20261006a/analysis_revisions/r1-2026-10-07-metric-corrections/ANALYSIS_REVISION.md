# Analysis revision `r1-2026-10-07-metric-corrections` — run `dev-20261006a`

- recorded 2026-10-08T05:24:02+00:00 (snapshot 2026-10-08T00:24:00+00:00)
- reason: Correct tie handling in AUPRC and precision@k, the per-ICC smallest-detectable-AUROC rows, the power report's hidden ICC scenarios and the run summary's artifact counts; re-derive every table, plot and report from the saved GPU measurements (no re-scoring).
- command: `P33_RESULTS_ROOT=<repo>/phase3_3/sol_results run/.venv/bin/python phase3_2/sol/scripts/p33.py export --run dev-20261006a`
- git: `8650df525242` (dirty: True)
- Derived tables, plots and reports were regenerated from the run's saved merged measurements by CPU code. No model was loaded, no site was re-scored, and every measurement input is byte-identical to the snapshot.
- analysis code: 44 source files, digest of their hashes `3c3e772c66ecf51e` (the same digest means the same analysis code)
- environment: python 3.12.3, numpy 2.5.2, matplotlib 3.11.2, transformers 5.16.1, lark 1.3.1

## What was corrected (deviation D9 in `phase3_2/PREREGISTRATION.md`)

| Defect | Where | Correction |
|---|---|---|
| AP ordered tied scores by input row | `p33/h4.py` `auprc` | step-wise average precision over DISTINCT scores (each tie group is one threshold): AP = Σ_j (R_j − R_(j−1))·P_j |
| precision@k broke a boundary tie by input row | `p33/h4.py` `precision_at_k` | expected precision under uniform selection inside the boundary tie: (pos above + (K − a)·p/g)/K, K = min(k, n); empty → None; k < 1 or non-integer → error |
| 25 smallest-detectable-AUROC rows, 5 distinct, all computed with the pilot ICC | `p33/power.py` `analyse` | one row per (template count, ICC) scenario, computed with the ICC it reports; the pilot flagged; counts above the 80-template corpus marked HYPOTHETICAL; design effect and effective n per row |
| the power report showed only ICC = 0 for the rule effect, and filtered rows by truthiness | `p33/reports.py` `power_report` | every scenario in a T × ICC table, the pilot in bold, zero power kept, scope and the DE / n_eff formulas stated |
| RUN_SUMMARY counted `reports/` before writing it (0 files on Sol) | `p33/reports.py` `run_summary`, `make_all`; new `p33/artifacts.py` | counts the pipeline's registered artifacts after everything else is written; unregistered files never counted |
| the power figure omitted the rule-effect sensitivity; figure footers named one model of a "base|instruct" pair | `p33/plots.py` | a third panel with every ICC (pilot highlighted, hypothetical T shaded); footers list every model, each with its own revision (`model@revision`) |
| the reproduction report named commands that do not exist (`dev arm-a`) and a missing `env/README.md` | `p33/reports.py` `reproduction`; `env/README.md` | the real commands; the file written |

## Validation (before and after the export)

- `p33 status` on the run itself (read-only, temporary validation pins from the job manifests):
  Arm A 192/192 done, primary 112/112 done, before AND after.
- `p33 validate` on a scratch copy of the run: VALID; the re-merged 10,224 + 16,000 rows were
  byte-identical to the stored merged files.
- With the ORIGINAL code, a local re-export reproduced 18 of Sol's 19 CSVs byte for byte; the
  nineteenth differed only in `cal_intercept` (−8.53e-17 on Sol, −7.93e-17 here): floating-point
  noise on a value that is zero by construction. So every difference below comes from the
  corrections, not from the environment.

## Figures and reports

- Every figure file changed bytes. Figures with unchanged data differ only in embedded metadata:
  a creation date (SVG) and the matplotlib version (3.10.7 on Sol, 3.11.2 here); their plotted
  values come from CSVs that are byte-identical. The H4 figure now draws tie-grouped curves
  with AUROC and AP in its legend; the power figure has the new rule-effect panel.
- Reports changed: DEVELOPMENT_RESULTS (corrected AP, new P@k columns, tie note), DEVIATIONS
  (D9, D10 appended), POWER_ANALYSIS, REPRODUCTION, RUN_SUMMARY. Unchanged byte for byte:
  METHODS_AND_PROVENANCE, QUALITY_CONTROL, HELDOUT_RESULTS, HYPOTHESIS_RESULTS,
  PLAIN_LANGUAGE_RESULTS.

## What the corrected power analysis says, in plain words

The rule effect (pooled mean 0.164 nats, SD 2.19) looked well powered because the report
showed only the ICC = 0 row (0.994 at 80 templates). Rows from one template are strongly alike
(pilot ICC 0.252), so the 3,587 rows of an 80-template design are worth about 298 independent
observations, and power at the pilot ICC is 0.251 at 80 templates; 80% is not reached even at
320 templates (0.732), and anything above 80 templates would need new materials. H4 criterion
1 is in a different situation: at the pilot ICC (0.073) and 80 templates it has 80% power for a
true AUROC of 0.62 or more, while the pooled development AUROC was 0.899. These are planning
estimates from development data; the registered design was not changed in response.

## Not done here

No GPU, no model loading, no re-scoring, no freeze, no unlock, no submission. Held-out cells
were not touched. The gated Llama-3.2-1B pair was approved and downloaded on Sol on
2026-10-07; it remains in the design.

## Checks

| check | passed | detail |
|---|---|---|
| site_inventory.csv unchanged | yes | byte-identical |
| split_exclusion_audit.csv unchanged | yes | byte-identical |
| run_completeness.csv unchanged | yes | byte-identical |
| failed_cells.csv unchanged | yes | byte-identical |
| job_provenance.csv unchanged | yes | byte-identical |
| fertility.csv unchanged | yes | byte-identical |
| arm_a_long.csv unchanged | yes | byte-identical |
| rule_effect.csv unchanged | yes | byte-identical |
| paraphrase.csv unchanged | yes | byte-identical |
| extinction_rung_long.csv unchanged | yes | byte-identical |
| kstar_survival.csv unchanged | yes | byte-identical |
| h4_predictions.csv unchanged | yes | byte-identical |
| arm_b_generations.csv unchanged | yes | byte-identical |
| arm_b_hurdle.csv unchanged | yes | byte-identical |
| h5_budget_outcomes.csv unchanged | yes | byte-identical |
| h5_ir_proof.csv unchanged | yes | byte-identical |
| h2_did.csv unchanged | yes | byte-identical |
| H4: only AP and precision@k columns changed | yes | 23 expected cell changes; 0 unexpected |
| power: h4_criterion1 values unchanged on every shared scenario | yes | 175 shared scenarios; duplicates after: [] |
| power: rule_effect values unchanged on every shared scenario | yes | 25 shared scenarios; duplicates after: [] |

## CSV files

| file | bytes identical | rows before | rows after |
|---|---|---:|---:|
| site_inventory | yes | 852 | 852 |
| split_exclusion_audit | yes | 460 | 460 |
| run_completeness | yes | 4 | 4 |
| failed_cells | yes | 1 | 1 |
| job_provenance | yes | 8 | 8 |
| fertility | yes | 5 | 5 |
| arm_a_long | yes | 10224 | 10224 |
| rule_effect | yes | 180 | 180 |
| paraphrase | yes | 16 | 16 |
| extinction_rung_long | yes | 11200 | 11200 |
| kstar_survival | yes | 1616 | 1616 |
| h4_predictions | yes | 1704 | 1704 |
| h4_metrics_baselines_calibration | no | 28 | 28 |
| arm_b_generations | yes | 1 | 1 |
| arm_b_hurdle | yes | 1 | 1 |
| h5_budget_outcomes | yes | 1 | 1 |
| h5_ir_proof | yes | 1 | 1 |
| h2_did | yes | 1 | 1 |
| power | no | 231 | 231 |

## H4 metric cells that changed (expected: AP and precision@k only)

| pair | predictor | column | before | after |
|---|---|---|---|---|
| Qwen2.5-Coder-0.5B | identity | auprc | 0.40998 | 0.407277 |
| Qwen2.5-Coder-0.5B | identity | p_at_10 | 0.3 | 0.407277 |
| Qwen2.5-Coder-0.5B | identity | p_at_50 | 0.44 | 0.407277 |
| Qwen2.5-Coder-0.5B | length | auprc | 0.434397 | 0.433374 |
| Qwen2.5-Coder-0.5B | length | p_at_10 | 0.2 | 0.146341 |
| Qwen2.5-Coder-0.5B | length | p_at_50 | 0.22 | 0.240896 |
| Qwen2.5-Coder-0.5B | program_nll | auprc | 0.445085 | 0.445784 |
| Qwen2.5-Coder-0.5B | terminal_rate | auprc | 0.807714 | 0.81268 |
| Qwen2.5-Coder-0.5B | terminal_rate | p_at_50 | 0.96 | 0.973333 |
| Qwen2.5-Coder-0.5B | token_count | auprc | 0.431463 | 0.416017 |
| Qwen2.5-Coder-0.5B | token_count | p_at_10 | 0.5 | 0.435185 |
| Qwen2.5-Coder-0.5B | token_count | p_at_50 | 0.48 | 0.435185 |
| Qwen2.5-Coder-1.5B | identity | auprc | 0.452324 | 0.46831 |
| Qwen2.5-Coder-1.5B | identity | p_at_10 | 0.4 | 0.46831 |
| Qwen2.5-Coder-1.5B | identity | p_at_50 | 0.44 | 0.46831 |
| Qwen2.5-Coder-1.5B | length | auprc | 0.436575 | 0.456774 |
| Qwen2.5-Coder-1.5B | length | p_at_10 | 0.1 | 0.170732 |
| Qwen2.5-Coder-1.5B | length | p_at_50 | 0.22 | 0.24209 |
| Qwen2.5-Coder-1.5B | program_nll | auprc | 0.459467 | 0.460181 |
| Qwen2.5-Coder-1.5B | terminal_rate | auprc | 0.800325 | 0.811029 |
| Qwen2.5-Coder-1.5B | token_count | auprc | 0.468459 | 0.472068 |
| Qwen2.5-Coder-1.5B | token_count | p_at_10 | 0.4 | 0.490741 |
| Qwen2.5-Coder-1.5B | token_count | p_at_50 | 0.46 | 0.490741 |

## Power: smallest detectable AUROC

Before: 25 rows, 5 distinct, every one computed with the pilot ICC whatever ICC its loop iteration stood for. After: 25 rows, one per (template count, ICC) scenario.

| templates | ICC | ICC source | smallest detectable AUROC | status | templates vs corpus |
|---:|---:|---|---|---|---|
| 20 | 0 | sensitivity | 0.63 | reached | subset of the corpus |
| 20 | 0.05 | sensitivity | 0.64 | reached | subset of the corpus |
| 20 | 0.073 | pilot estimate | 0.64 | reached | subset of the corpus |
| 20 | 0.1 | sensitivity | 0.64 | reached | subset of the corpus |
| 20 | 0.2 | sensitivity | 0.67 | reached | subset of the corpus |
| 40 | 0 | sensitivity | 0.62 | reached | subset of the corpus |
| 40 | 0.05 | sensitivity | 0.63 | reached | subset of the corpus |
| 40 | 0.073 | pilot estimate | 0.63 | reached | subset of the corpus |
| 40 | 0.1 | sensitivity | 0.63 | reached | subset of the corpus |
| 40 | 0.2 | sensitivity | 0.64 | reached | subset of the corpus |
| 80 | 0 | sensitivity | 0.62 | reached | the whole corpus |
| 80 | 0.05 | sensitivity | 0.62 | reached | the whole corpus |
| 80 | 0.073 | pilot estimate | 0.62 | reached | the whole corpus |
| 80 | 0.1 | sensitivity | 0.62 | reached | the whole corpus |
| 80 | 0.2 | sensitivity | 0.63 | reached | the whole corpus |
| 160 | 0 | sensitivity | 0.61 | reached | HYPOTHETICAL: exceeds the 80-template corpus (needs new templates) |
| 160 | 0.05 | sensitivity | 0.62 | reached | HYPOTHETICAL: exceeds the 80-template corpus (needs new templates) |
| 160 | 0.073 | pilot estimate | 0.62 | reached | HYPOTHETICAL: exceeds the 80-template corpus (needs new templates) |
| 160 | 0.1 | sensitivity | 0.62 | reached | HYPOTHETICAL: exceeds the 80-template corpus (needs new templates) |
| 160 | 0.2 | sensitivity | 0.62 | reached | HYPOTHETICAL: exceeds the 80-template corpus (needs new templates) |
| 320 | 0 | sensitivity | 0.61 | reached | HYPOTHETICAL: exceeds the 80-template corpus (needs new templates) |
| 320 | 0.05 | sensitivity | 0.61 | reached | HYPOTHETICAL: exceeds the 80-template corpus (needs new templates) |
| 320 | 0.073 | pilot estimate | 0.61 | reached | HYPOTHETICAL: exceeds the 80-template corpus (needs new templates) |
| 320 | 0.1 | sensitivity | 0.62 | reached | HYPOTHETICAL: exceeds the 80-template corpus (needs new templates) |
| 320 | 0.2 | sensitivity | 0.62 | reached | HYPOTHETICAL: exceeds the 80-template corpus (needs new templates) |

## RUN_SUMMARY artifact lines

Before:

    - **csv/** — 19 files
    - **plots/** — 24 files
    - **reports/** — 0 files

After:

    - **csv/** — 19 of 19 registered files present (tables)
    - **plots/** — 24 of 24 registered files present (12 figures x PNG/SVG)
    - **reports/** — 10 of 10 registered files present (Markdown reports)

Measurement inputs verified byte-identical: **652 files** (raw shards, checkpoints, merged JSONL and status, job and other manifests, logs). Hashes are in `analysis_revision.json`; the previous derived outputs are in `before/`.
