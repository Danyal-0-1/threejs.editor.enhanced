# Development results — `dev-20261006a`

> **Run** `dev-20261006a` · **stage** DEVELOPMENT · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

## Headline numbers (from the CSVs; see stage banner)

**Reversion with the token table present** (`rule_effect.csv`, record_type=reversion)

| family | lexicon | model | rate | ci | n_rows | n_templates |
|---|---|---|---|---|---|---|
| dom | d25s1 | Qwen/Qwen2.5-Coder-0.5B | 0.423 | [0.364, 0.481] | 220 | 74 |
| dom | d25s2 | Qwen/Qwen2.5-Coder-0.5B | 0.432 | [0.326, 0.540] | 88 | 55 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-0.5B | 0.412 | [0.367, 0.455] | 272 | 76 |
| dom | d50s2 | Qwen/Qwen2.5-Coder-0.5B | 0.430 | [0.384, 0.479] | 272 | 76 |
| dom | d25s1 | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.395 | [0.345, 0.451] | 220 | 74 |
| dom | d25s2 | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.386 | [0.309, 0.469] | 88 | 55 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.441 | [0.398, 0.484] | 272 | 76 |
| dom | d50s2 | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.390 | [0.346, 0.434] | 272 | 76 |
| dom | d25s1 | Qwen/Qwen2.5-Coder-1.5B | 0.500 | [0.430, 0.567] | 220 | 74 |
| dom | d25s2 | Qwen/Qwen2.5-Coder-1.5B | 0.580 | [0.468, 0.695] | 88 | 55 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-1.5B | 0.537 | [0.471, 0.598] | 272 | 76 |
| dom | d50s2 | Qwen/Qwen2.5-Coder-1.5B | 0.537 | [0.481, 0.590] | 272 | 76 |
| dom | d25s1 | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.445 | [0.392, 0.500] | 220 | 74 |
| dom | d25s2 | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.511 | [0.408, 0.616] | 88 | 55 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.456 | [0.394, 0.514] | 272 | 76 |
| dom | d50s2 | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.485 | [0.430, 0.539] | 272 | 76 |

**Rule effect** — `M_seq(rule) − M_seq(control)` (`rule_effect.csv`)

| family | lexicon | model | control | mean | ci | ci_excludes_zero | helped |
|---|---|---|---|---|---|---|---|
| dom | d25s1 | Qwen/Qwen2.5-Coder-0.5B | norule | 0.094 | [-0.133, 0.329] | False | 0.441 |
| dom | d25s1 | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.164 | [-0.064, 0.404] | False | 0.482 |
| dom | d25s2 | Qwen/Qwen2.5-Coder-0.5B | norule | 0.152 | [-0.372, 0.683] | False | 0.466 |
| dom | d25s2 | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.154 | [-0.378, 0.700] | False | 0.466 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-0.5B | norule | 0.185 | [-0.004, 0.388] | False | 0.544 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.226 | [0.036, 0.425] | True | 0.562 |
| dom | d50s2 | Qwen/Qwen2.5-Coder-0.5B | norule | 0.143 | [-0.034, 0.327] | False | 0.496 |
| dom | d50s2 | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.179 | [-0.002, 0.369] | False | 0.518 |
| dom | d25s1 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.142 | [-0.161, 0.478] | False | 0.477 |
| dom | d25s1 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.128 | [-0.157, 0.444] | False | 0.495 |
| dom | d25s2 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.285 | [-0.262, 0.871] | False | 0.545 |
| dom | d25s2 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.265 | [-0.238, 0.801] | False | 0.534 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.209 | [-0.045, 0.487] | False | 0.540 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.186 | [-0.060, 0.458] | False | 0.526 |
| dom | d50s2 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.157 | [-0.092, 0.443] | False | 0.562 |
| dom | d50s2 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.148 | [-0.088, 0.415] | False | 0.544 |
| dom | d25s1 | Qwen/Qwen2.5-Coder-1.5B | norule | 0.149 | [-0.137, 0.450] | False | 0.486 |
| dom | d25s1 | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.151 | [-0.123, 0.441] | False | 0.491 |
| dom | d25s2 | Qwen/Qwen2.5-Coder-1.5B | norule | 0.148 | [-0.286, 0.607] | False | 0.523 |
| dom | d25s2 | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.169 | [-0.275, 0.632] | False | 0.534 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-1.5B | norule | 0.107 | [-0.116, 0.358] | False | 0.471 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.122 | [-0.093, 0.362] | False | 0.478 |
| dom | d50s2 | Qwen/Qwen2.5-Coder-1.5B | norule | 0.085 | [-0.140, 0.338] | False | 0.504 |
| dom | d50s2 | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.098 | [-0.122, 0.343] | False | 0.507 |
| dom | d25s1 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.197 | [-0.168, 0.616] | False | 0.518 |
| dom | d25s1 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.194 | [-0.173, 0.603] | False | 0.518 |
| dom | d25s2 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.330 | [-0.323, 1.028] | False | 0.489 |
| dom | d25s2 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.360 | [-0.321, 1.068] | False | 0.500 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.208 | [-0.113, 0.568] | False | 0.518 |
| dom | d50s1 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.206 | [-0.110, 0.560] | False | 0.515 |
| dom | d50s2 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.193 | [-0.114, 0.519] | False | 0.522 |
| dom | d50s2 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.198 | [-0.104, 0.522] | False | 0.515 |

**Extinction** — Kaplan–Meier median shots (`kstar_survival.csv`)

| family | model | population | median | ci | n | cens |
|---|---|---|---|---|---|---|
| dom | Qwen/Qwen2.5-Coder-0.5B | ALL_SITES | 0 | [0.000, 0.002] | 400 | 0.055 |
| dom | Qwen/Qwen2.5-Coder-0.5B | INITIALLY_WRONG | 6.22992 | [2.350, 7.799] | 169 | 0.130 |
| dom | Qwen/Qwen2.5-Coder-0.5B-Instruct | ALL_SITES | 0 | [0.000, 0.000] | 400 | 0.077 |
| dom | Qwen/Qwen2.5-Coder-0.5B-Instruct | INITIALLY_WRONG | 5.88692 | [2.629, 11.511] | 175 | 0.177 |
| dom | Qwen/Qwen2.5-Coder-1.5B | ALL_SITES | 0.131184 | [0.000, 0.592] | 400 | 0.113 |
| dom | Qwen/Qwen2.5-Coder-1.5B | INITIALLY_WRONG | 5.67693 | [3.127, 10.053] | 207 | 0.217 |
| dom | Qwen/Qwen2.5-Coder-1.5B-Instruct | ALL_SITES | 0 | [0.000, 0.188] | 400 | 0.090 |
| dom | Qwen/Qwen2.5-Coder-1.5B-Instruct | INITIALLY_WRONG | 3.58495 | [2.303, 6.734] | 181 | 0.199 |

## H4 on development data (calibration fitted here — becomes the frozen calibration)

| pair | family | predictor | role | auroc | auprc | prev | p@10 | p@50 | n_rows |
|---|---|---|---|---|---|---|---|---|---|
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | dom | risk | score | 0.869 | 0.819 | 0.407 | 1.000 | 0.920 | 852 |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | dom | identity | baseline | 0.500 | 0.407 | 0.407 | 0.407 | 0.407 | 852 |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | dom | length | baseline | 0.544 | 0.433 | 0.407 | 0.146 | 0.241 | 852 |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | dom | program_nll | baseline | 0.538 | 0.446 | 0.407 | 0.300 | 0.580 | 852 |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | dom | token_count | baseline | 0.522 | 0.416 | 0.407 | 0.435 | 0.435 | 852 |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | dom | terminal_rate | exploratory_baseline | 0.797 | 0.813 | 0.407 | 1.000 | 0.973 | 852 |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | dom | risk | score | 0.935 | 0.924 | 0.468 | 1.000 | 1.000 | 852 |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | dom | identity | baseline | 0.500 | 0.468 | 0.468 | 0.468 | 0.468 | 852 |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | dom | length | baseline | 0.486 | 0.457 | 0.468 | 0.171 | 0.242 | 852 |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | dom | program_nll | baseline | 0.492 | 0.460 | 0.468 | 0.400 | 0.380 | 852 |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | dom | token_count | baseline | 0.505 | 0.472 | 0.468 | 0.491 | 0.491 | 852 |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | dom | terminal_rate | exploratory_baseline | 0.790 | 0.811 | 0.468 | 0.900 | 0.860 | 852 |

*Tied scores.* AP (`auprc`) is step-wise average precision with every tied score admitted as ONE threshold; precision@k is the expected precision when the top-k boundary falls inside a tie and places are filled uniformly from that tie. Both are therefore independent of row order, and a constant score (the identity baseline) scores exactly the prevalence. Corrected 2026-10-07 (deviation D9).
