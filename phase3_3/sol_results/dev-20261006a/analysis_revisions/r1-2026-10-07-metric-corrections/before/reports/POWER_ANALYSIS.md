# Power analysis — `dev-20261006a`

> **Run** `dev-20261006a` · **stage** DEVELOPMENT · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

Development pilot estimates only (`power.pilot_from_rows` refuses any non-DEVELOPMENT row). Clustering by template is modelled through the design effect 1 + (m − 1)·ICC, with the ICC estimated from the pilot AND swept for sensitivity.

## H4 criterion 1 — smallest AUROC detectable with 80% power

| n_templates | icc | value |
|---|---|---|
| 20 | 0.0730113 | 0.64 |
| 20 | 0.0730113 | 0.64 |
| 20 | 0.0730113 | 0.64 |
| 20 | 0.0730113 | 0.64 |
| 20 | 0.0730113 | 0.64 |
| 40 | 0.0730113 | 0.63 |
| 40 | 0.0730113 | 0.63 |
| 40 | 0.0730113 | 0.63 |
| 40 | 0.0730113 | 0.63 |
| 40 | 0.0730113 | 0.63 |
| 80 | 0.0730113 | 0.62 |
| 80 | 0.0730113 | 0.62 |
| 80 | 0.0730113 | 0.62 |
| 80 | 0.0730113 | 0.62 |
| 80 | 0.0730113 | 0.62 |
| 160 | 0.0730113 | 0.62 |
| 160 | 0.0730113 | 0.62 |
| 160 | 0.0730113 | 0.62 |
| 160 | 0.0730113 | 0.62 |
| 160 | 0.0730113 | 0.62 |
| 320 | 0.0730113 | 0.61 |
| 320 | 0.0730113 | 0.61 |
| 320 | 0.0730113 | 0.61 |
| 320 | 0.0730113 | 0.61 |
| 320 | 0.0730113 | 0.61 |

## Simulation check of the analytic curve

| n_templates | true_auroc | icc | power_analytic | power_simulated | source |
|---|---|---|---|---|---|
| 76 | 0.899 | 0.073 | 1 | 1 | template-clustered binormal simulation, R=200 |

## Rule effect

| n_templates | icc | pilot_mean | pilot_sd | power |
|---|---|---|---|---|
| 20 | 0 | 0.163897 | 2.1926 | 0.610 |
| 40 | 0 | 0.163897 | 2.1926 | 0.886 |
| 80 | 0 | 0.163897 | 2.1926 | 0.994 |
| 160 | 0 | 0.163897 | 2.1926 | 1.000 |
| 320 | 0 | 0.163897 | 2.1926 | 1.000 |

## Not computed

| analysis | status | reason |
|---|---|---|
| armb_conditional_precision | NOT RUN | no development Arm B hurdle estimates |

## KM median precision by template count (pilot resampling)

| n_templates | median_of_medians | lo | hi | share_median_unreached |
|---|---|---|---|---|
| 40 | 5.00932 | 2.86242 | 7.92466 | 0 |
| 80 | 5.00932 | 3.35055 | 6.7703 | 0 |
| 160 | 5.14902 | 3.66372 | 6.19691 | 0 |
| 320 | 5.1932 | 4.31637 | 6.04463 | 0 |

**Assumptions.** Binormal score model; template random intercept; two-sided 95%; the identity baseline is constant on the eligible set (D6), so criterion 1 is AUROC ≥ 0.60 with an interval above 0.5. Held-out results were never used to tune any sample size.
