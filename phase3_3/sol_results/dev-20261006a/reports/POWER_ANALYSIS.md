# Power analysis — `dev-20261006a`

> **Run** `dev-20261006a` · **stage** DEVELOPMENT · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

## What this is — and what it is not

- **Planning estimates from the development pilot only.** `power.pilot_from_rows` refuses any non-DEVELOPMENT row; no held-out result was used, and nothing here changed the registered design or sample size.
- **H4:** the power of **criterion 1 only** (AUROC ≥ 0.60 with its lower bound above 0.5). It says nothing about criterion 2, about criterion 3 (NOT TESTABLE, deviation D1), or about any other hypothesis.
- **Rule effect:** a one-sample, template-clustered test of the POOLED mean rule effect M(rule) − M(norule) > 0. The registered `rule_effect.csv` tests are per (model, lexicon), with far fewer rows per template than this pooled pilot, so each of those has less power than shown here.
- **Approximate.** Normal approximations; a binormal score model for H4; one ICC standing in for a nested design (sites within templates, models and lexicons within sites).
- **Templates are the independent unit.** Scoring the same templates under more models or lexicons, or repeating sites, adds rows *within* templates; it does not add templates. Template counts above the corpus (marked *) are hypothetical projections, not data already collected.

## Clustering, in plain language

Rows from one template are siblings: they share a program, so they tend to agree. The **ICC** (intra-class correlation) is the share of all variation that lies *between* templates; 0 means sibling rows are as different as strangers, 1 means they are copies. With m rows per template:

    design effect          DE    = 1 + (m − 1) · ICC
    effective sample size  n_eff = T · m / DE

- **rule effect** — m = 44.84 rows per template (pooled over 4 model(s) x 4 lexicon(s); rows of one template from other models or lexicons are NOT extra templates); pilot ICC = 0.252, so DE = 12.05 and at T = 80 the 3587 rows are worth about **298** independent observations.
- **H4 criterion 1** — m = 22.42 rows per template (pooled over 2 pair(s) x 4 lexicon(s); rows of one template from other pairs or lexicons are NOT extra templates); pilot ICC = 0.073, so DE = 2.56 and at T = 80 the 1794 rows are worth about **700** independent observations.

## Rule effect — power for a positive pooled mean

Pilot mean 0.164 nats, SD 2.193. Every ICC scenario is shown; the pilot estimate is in bold.

| ICC | ICC source | T=20 | T=40 | T=80 | T=160* | T=320* |
|---|---|---|---|---|---|---|
| 0.000 | sensitivity | 0.610 | 0.886 | 0.994 | 1.000 | 1.000 |
| 0.050 | sensitivity | 0.240 | 0.425 | 0.707 | 0.943 | 0.999 |
| 0.100 | sensitivity | 0.160 | 0.276 | 0.488 | 0.779 | 0.971 |
| 0.200 | sensitivity | 0.107 | 0.172 | 0.299 | 0.526 | 0.817 |
| 0.252 | **pilot estimate** | 0.094 | 0.147 | 0.251 | 0.446 | 0.732 |

\* hypothetical: more templates than the 80-template corpus, i.e. new materials would have to be written; not an observed sample.

**Reading it.** At the pilot ICC the power at 80 templates is **0.251**; 80% power is **not reached** anywhere on this grid (best: 0.732 at 320 templates, HYPOTHETICAL: exceeds the 80-template corpus (needs new templates)).
The ICC = 0 column (0.994 at 80 templates) assumes rows within a template are independent; the pilot says they are not, so ICC = 0 is the most optimistic row, not the expected one.

## H4 criterion 1 — smallest true AUROC detected with 80% power

One row per (ICC scenario, template count); each computed with the ICC in its own row. 'not reached' = no AUROC on the 0.51–0.99 grid reaches 80% power.

| ICC | ICC source | T=20 | T=40 | T=80 | T=160* | T=320* |
|---|---|---|---|---|---|---|
| 0.000 | sensitivity | 0.63 | 0.62 | 0.62 | 0.61 | 0.61 |
| 0.050 | sensitivity | 0.64 | 0.63 | 0.62 | 0.62 | 0.61 |
| 0.073 | **pilot estimate** | 0.64 | 0.63 | 0.62 | 0.62 | 0.61 |
| 0.100 | sensitivity | 0.64 | 0.63 | 0.62 | 0.62 | 0.62 |
| 0.200 | sensitivity | 0.67 | 0.64 | 0.63 | 0.62 | 0.62 |

\* hypothetical: more templates than the 80-template corpus, i.e. new materials would have to be written; not an observed sample.

**Reading it.** At the pilot ICC and 80 templates, criterion 1 has 80% power for a true AUROC of 0.62 or more; the pooled development AUROC was 0.899. That is planning information about criterion 1 only — it is not evidence that the held-out AUROC will be similar.

### H4 power at the pilot ICC, by true AUROC

| true AUROC | T=20 | T=40 | T=80 | T=160* | T=320* |
|---|---|---|---|---|---|
| 0.55 | 0.128 | 0.054 | 0.011 | 0.001 | 0.000 |
| 0.60 | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 |
| 0.65 | 0.882 | 0.954 | 0.991 | 1.000 | 1.000 |
| 0.70 | 0.993 | 1.000 | 1.000 | 1.000 | 1.000 |
| 0.75 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 0.80 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 0.85 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

## Simulation check of the analytic curve

| n_templates | true_auroc | icc | power_analytic | power_simulated | source |
|---|---|---|---|---|---|
| 76 | 0.899 | 0.073 | 1 | 1 | template-clustered binormal simulation, R=200 (integer sites per template; the analytic value uses the mean) |

## KM median precision by template count (pilot resampling)

| n_templates | median_of_medians | lo | hi | share_median_unreached |
|---|---|---|---|---|
| 40 | 5.00932 | 2.86242 | 7.92466 | 0 |
| 80 | 5.00932 | 3.35055 | 6.7703 | 0 |
| 160 | 5.14902 | 3.66372 | 6.19691 | 0 |
| 320 | 5.1932 | 4.31637 | 6.04463 | 0 |

## Not computed

| analysis | status | reason |
|---|---|---|
| armb_conditional_precision | NOT RUN | no development Arm B hurdle estimates |

**Assumptions.** Binormal score model (H4); template random intercept; two-sided 95%; the identity baseline is constant on the eligible set (D6), so criterion 1 is AUROC ≥ 0.60 with an interval above 0.5. Held-out results were never used to tune any sample size.
