# Development results — `smoke-20261023a`

> **Run** `smoke-20261023a` · **stage** SMOKE (development cell) · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

## Headline numbers (from the CSVs; see stage banner)

**Reversion with the token table present** (`rule_effect.csv`, record_type=reversion)

| family | lexicon | model | rate | ci | n_rows | n_templates |
|---|---|---|---|---|---|---|
| dom | d50s1 | asu-rc/olmo3-7b-instruct | 0.333 | [0.091, 0.636] | 12 | 11 |

**Rule effect** — `M_seq(rule) − M_seq(control)` (`rule_effect.csv`)

| family | lexicon | model | control | mean | ci | ci_excludes_zero | helped |
|---|---|---|---|---|---|---|---|
| dom | d50s1 | asu-rc/olmo3-7b-instruct | norule | 2.064 | [0.829, 3.377] | True | 0.833 |
| dom | d50s1 | asu-rc/olmo3-7b-instruct | norule_lenmatched | 1.911 | [0.774, 3.086] | True | 0.833 |

**Extinction** — Kaplan–Meier median shots (`kstar_survival.csv`)

| family | model | population | median | ci | n | cens |
|---|---|---|---|---|---|---|
| dom | asu-rc/olmo3-7b-instruct | ALL_SITES | 0 | [—, —] | 6 | 0.333 |
| dom | asu-rc/olmo3-7b-instruct | INITIALLY_WRONG | NOT REACHED | [—, —] | 3 | 0.667 |

## H4 on development data (calibration fitted here — becomes the frozen calibration)

_NOT RUN_
