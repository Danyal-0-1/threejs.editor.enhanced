# Run summary — `smoke-20261006a`

> **Run** `smoke-20261006a` · **stage** SMOKE (development cell) · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

## Completeness (`run_completeness.csv`)

| experiment | status | n_expected_cells | done | missing | failed | corrupt | duplicates_dropped |
|---|---|---|---|---|---|---|---|
| arm_a | COMPLETE | 9 | 9 | 0 | 0 | 0 | 0 |
| primary | COMPLETE | 8 | 8 | 0 | 0 | 0 | 0 |
| armb | NOT RUN |  |  |  |  |  |  |
| h5 | NOT RUN |  |  |  |  |  |  |

## Headline numbers (from the CSVs; see stage banner)

**Reversion with the token table present** (`rule_effect.csv`, record_type=reversion)

| family | lexicon | model | rate | ci | n_rows | n_templates |
|---|---|---|---|---|---|---|
| dom | d50s1 | Qwen/Qwen2.5-Coder-0.5B | 0.583 | [0.333, 0.833] | 12 | 11 |

**Rule effect** — `M_seq(rule) − M_seq(control)` (`rule_effect.csv`)

| family | lexicon | model | control | mean | ci | ci_excludes_zero | helped |
|---|---|---|---|---|---|---|---|
| dom | d50s1 | Qwen/Qwen2.5-Coder-0.5B | norule | 0.215 | [-0.423, 0.967] | False | 0.667 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.284 | [-0.365, 1.146] | False | 0.583 |

**Extinction** — Kaplan–Meier median shots (`kstar_survival.csv`)

| family | model | population | median | ci | n | cens |
|---|---|---|---|---|---|---|
| dom | Qwen/Qwen2.5-Coder-0.5B | ALL_SITES | 0 | [—, —] | 6 | 0.167 |
| dom | Qwen/Qwen2.5-Coder-0.5B | INITIALLY_WRONG | 6.81651 | [—, —] | 3 | 0.333 |

## Artifacts

- **csv/** — 19 files
- **plots/** — 24 files
- **reports/** — 0 files
