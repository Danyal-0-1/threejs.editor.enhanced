# Development results — `smoke-local-20261005`

> **Run** `smoke-local-20261005` · **stage** SMOKE (development cell) · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

## Headline numbers (from the CSVs; see stage banner)

**Reversion with the token table present** (`rule_effect.csv`, record_type=reversion)

| family | lexicon | model | rate | ci | n_rows | n_templates |
|---|---|---|---|---|---|---|
| dom | d50s1 | Qwen/Qwen2.5-Coder-0.5B | 0.583 | [0.333, 0.833] | 12 | 11 |

**Rule effect** — `M_seq(rule) − M_seq(control)` (`rule_effect.csv`)

| family | lexicon | model | control | mean | ci | ci_excludes_zero | helped |
|---|---|---|---|---|---|---|---|
| dom | d50s1 | Qwen/Qwen2.5-Coder-0.5B | norule | 0.182 | [-0.433, 0.911] | False | 0.583 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.291 | [-0.368, 1.131] | False | 0.583 |

**Extinction** — Kaplan–Meier median shots (`kstar_survival.csv`)

| family | model | population | median | ci | n | cens |
|---|---|---|---|---|---|---|
| dom | Qwen/Qwen2.5-Coder-0.5B | ALL_SITES | 0 | [—, —] | 6 | 0.167 |
| dom | Qwen/Qwen2.5-Coder-0.5B | INITIALLY_WRONG | 6.78877 | [—, —] | 3 | 0.333 |

## H4 on development data (calibration fitted here — becomes the frozen calibration)

_NOT RUN_
