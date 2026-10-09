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

## Validation on Sol (2026-10-07)

- Code: branch `sol-d9-d10` at commit `78b2bcd`, the same commit that was verified locally:
  139 tests passed in the project venv, and the CPU-test job (`setup-20261007b`) ran on Sol before
  this re-derivation.
- `p33 validate` on this run, with Sol's real `model_pins.json`, between the snapshot and the
  export: VALID. The merge it performs is byte-deterministic, so every recorded input stayed
  identical; `record` re-checks all of them.
- The same correction was first applied to a local copy of this run. Its record has the same
  analysis-source digest when the code is identical. With the ORIGINAL code, that local copy
  reproduced 18 of these 19 CSVs byte for byte. The nineteenth differed only in
  `cal_intercept`, floating-point noise on a value that is zero by construction.

## Figures and reports

- Every figure was regenerated. Figures with unchanged data differ only in their footers
  (`model@revision`) and embedded metadata. The H4 figure draws tie-grouped curves, and the
  power figure has the rule-effect panel.
- `DEVELOPMENT_RESULTS`, `DEVIATIONS` (D9 and D10 appended), `POWER_ANALYSIS`, `REPRODUCTION`
  and `RUN_SUMMARY` change. The other five reports are expected to stay byte-identical.

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

No GPU, no model loading, no re-scoring. No held-out cell was touched before this record. The
development freeze and the held-out unlock follow this record, at the investigator's direction.
