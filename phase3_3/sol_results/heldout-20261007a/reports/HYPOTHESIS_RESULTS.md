# Hypothesis results — `heldout-20261007a`

> **Run** `heldout-20261007a` · **stage** HELD-OUT · **status** COMPLETE
>
> Held-out evaluation under DEV_FREEZE; see criteria below. blk results are a WEAKER family test (deviation D1), never a held-out-grammar confirmation.

| hypothesis | status in this run |
|---|---|
| H1 familiar beats unfamiliar | established in prior literature; not a contribution and not retested |
| H2 prior × context | **NOT TESTABLE** — no calibrated prior-strength (T) or local-context (A) levels exist; deriving them from outcome margins would be circular (review section 6.3) |
| H4 exact-site prediction | see criteria below  |
| H5 targeted repair | see arms below |
| Arm B generation | see hurdle below |

## H4 criteria

| pair | family | split | criterion | status | delta | ci_lo | ci_hi | p_holm | detail |
|---|---|---|---|---|---|---|---|---|---|
| Qwen/Qwen2.5-72B/Qwen/Qwen2.5-72B-Instruct | blk | HELDOUT-WEAK-FAMILY | C1_delta_vs_identity | MET | 0.365736 | 0.338153 | 0.392882 | 0.0009995 |  |
| Qwen/Qwen2.5-72B/Qwen/Qwen2.5-72B-Instruct | blk | HELDOUT-WEAK-FAMILY | C2_delta_vs_length | MET | 0.425418 | 0.376073 | 0.472975 | 0.0009995 |  |
| Qwen/Qwen2.5-72B/Qwen/Qwen2.5-72B-Instruct | blk | HELDOUT-WEAK-FAMILY | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-72B/Qwen/Qwen2.5-72B-Instruct | dom | HELDOUT | C1_delta_vs_identity | MET | 0.353616 | 0.321749 | 0.38354 | 0.0009995 |  |
| Qwen/Qwen2.5-72B/Qwen/Qwen2.5-72B-Instruct | dom | HELDOUT | C2_delta_vs_length | MET | 0.366132 | 0.320499 | 0.41133 | 0.0009995 |  |
| Qwen/Qwen2.5-72B/Qwen/Qwen2.5-72B-Instruct | dom | HELDOUT | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | blk | HELDOUT-WEAK-FAMILY | C1_delta_vs_identity | MET | 0.336469 | 0.299342 | 0.36904 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | blk | HELDOUT-WEAK-FAMILY | C2_delta_vs_length | MET | 0.266623 | 0.206752 | 0.323358 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | blk | HELDOUT-WEAK-FAMILY | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | dom | HELDOUT | C1_delta_vs_identity | MET | 0.388212 | 0.360668 | 0.412497 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | dom | HELDOUT | C2_delta_vs_length | MET | 0.297132 | 0.250401 | 0.339515 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | dom | HELDOUT | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | blk | HELDOUT-WEAK-FAMILY | C1_delta_vs_identity | MET | 0.419857 | 0.399668 | 0.437745 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | blk | HELDOUT-WEAK-FAMILY | C2_delta_vs_length | MET | 0.426145 | 0.382686 | 0.468441 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | blk | HELDOUT-WEAK-FAMILY | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | dom | HELDOUT | C1_delta_vs_identity | MET | 0.462619 | 0.447366 | 0.474561 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | dom | HELDOUT | C2_delta_vs_length | MET | 0.493124 | 0.455919 | 0.533898 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | dom | HELDOUT | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-14B/Qwen/Qwen2.5-Coder-14B-Instruct | blk | HELDOUT-WEAK-FAMILY | C1_delta_vs_identity | MET | 0.374775 | 0.344058 | 0.403476 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-14B/Qwen/Qwen2.5-Coder-14B-Instruct | blk | HELDOUT-WEAK-FAMILY | C2_delta_vs_length | MET | 0.387287 | 0.3395 | 0.435099 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-14B/Qwen/Qwen2.5-Coder-14B-Instruct | blk | HELDOUT-WEAK-FAMILY | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-14B/Qwen/Qwen2.5-Coder-14B-Instruct | dom | HELDOUT | C1_delta_vs_identity | MET | 0.352269 | 0.320278 | 0.383435 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-14B/Qwen/Qwen2.5-Coder-14B-Instruct | dom | HELDOUT | C2_delta_vs_length | MET | 0.369333 | 0.319007 | 0.419564 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-14B/Qwen/Qwen2.5-Coder-14B-Instruct | dom | HELDOUT | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-32B/Qwen/Qwen2.5-Coder-32B-Instruct | blk | HELDOUT-WEAK-FAMILY | C1_delta_vs_identity | MET | 0.304999 | 0.259323 | 0.346792 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-32B/Qwen/Qwen2.5-Coder-32B-Instruct | blk | HELDOUT-WEAK-FAMILY | C2_delta_vs_length | MET | 0.408617 | 0.344834 | 0.467694 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-32B/Qwen/Qwen2.5-Coder-32B-Instruct | blk | HELDOUT-WEAK-FAMILY | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-32B/Qwen/Qwen2.5-Coder-32B-Instruct | dom | HELDOUT | C1_delta_vs_identity | MET | 0.286128 | 0.242815 | 0.324613 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-32B/Qwen/Qwen2.5-Coder-32B-Instruct | dom | HELDOUT | C2_delta_vs_length | MET | 0.331232 | 0.272231 | 0.39377 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-32B/Qwen/Qwen2.5-Coder-32B-Instruct | dom | HELDOUT | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-3B/Qwen/Qwen2.5-Coder-3B-Instruct | blk | HELDOUT-WEAK-FAMILY | C1_delta_vs_identity | MET | 0.439479 | 0.421478 | 0.455834 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-3B/Qwen/Qwen2.5-Coder-3B-Instruct | blk | HELDOUT-WEAK-FAMILY | C2_delta_vs_length | MET | 0.405904 | 0.359309 | 0.454015 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-3B/Qwen/Qwen2.5-Coder-3B-Instruct | blk | HELDOUT-WEAK-FAMILY | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-3B/Qwen/Qwen2.5-Coder-3B-Instruct | dom | HELDOUT-WEAKENED | C1_delta_vs_identity | MET | 0.448877 | 0.431868 | 0.464001 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-3B/Qwen/Qwen2.5-Coder-3B-Instruct | dom | HELDOUT-WEAKENED | C2_delta_vs_length | MET | 0.413293 | 0.368243 | 0.459196 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-3B/Qwen/Qwen2.5-Coder-3B-Instruct | dom | HELDOUT-WEAKENED | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-7B/Qwen/Qwen2.5-Coder-7B-Instruct | blk | HELDOUT-WEAK-FAMILY | C1_delta_vs_identity | MET | 0.258763 | 0.213172 | 0.302926 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-7B/Qwen/Qwen2.5-Coder-7B-Instruct | blk | HELDOUT-WEAK-FAMILY | C2_delta_vs_length | MET | 0.266755 | 0.206938 | 0.324752 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-7B/Qwen/Qwen2.5-Coder-7B-Instruct | blk | HELDOUT-WEAK-FAMILY | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-7B/Qwen/Qwen2.5-Coder-7B-Instruct | dom | HELDOUT | C1_delta_vs_identity | MET | 0.260118 | 0.218165 | 0.300576 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-7B/Qwen/Qwen2.5-Coder-7B-Instruct | dom | HELDOUT | C2_delta_vs_length | MET | 0.293465 | 0.23627 | 0.346973 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-7B/Qwen/Qwen2.5-Coder-7B-Instruct | dom | HELDOUT | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| deepseek-ai/deepseek-coder-1.3b-base/deepseek-ai/deepseek-coder-1.3b-instruct | blk | HELDOUT-WEAK-FAMILY | C1_delta_vs_identity | MET | 0.28779 | 0.246082 | 0.331305 | 0.0009995 |  |
| deepseek-ai/deepseek-coder-1.3b-base/deepseek-ai/deepseek-coder-1.3b-instruct | blk | HELDOUT-WEAK-FAMILY | C2_delta_vs_length | MET | 0.136337 | 0.092372 | 0.186678 | 0.0009995 |  |
| deepseek-ai/deepseek-coder-1.3b-base/deepseek-ai/deepseek-coder-1.3b-instruct | blk | HELDOUT-WEAK-FAMILY | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| deepseek-ai/deepseek-coder-1.3b-base/deepseek-ai/deepseek-coder-1.3b-instruct | dom | HELDOUT | C1_delta_vs_identity | MET | 0.34122 | 0.310335 | 0.369946 | 0.0009995 |  |
| deepseek-ai/deepseek-coder-1.3b-base/deepseek-ai/deepseek-coder-1.3b-instruct | dom | HELDOUT | C2_delta_vs_length | MET | 0.302864 | 0.257224 | 0.348355 | 0.0009995 |  |
| deepseek-ai/deepseek-coder-1.3b-base/deepseek-ai/deepseek-coder-1.3b-instruct | dom | HELDOUT | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| deepseek-ai/deepseek-coder-33b-base/deepseek-ai/deepseek-coder-33b-instruct | blk | HELDOUT-WEAK-FAMILY | C1_delta_vs_identity | MET | 0.446179 | 0.431846 | 0.459687 | 0.0009995 |  |
| deepseek-ai/deepseek-coder-33b-base/deepseek-ai/deepseek-coder-33b-instruct | blk | HELDOUT-WEAK-FAMILY | C2_delta_vs_length | MET | 0.368912 | 0.326474 | 0.411313 | 0.0009995 |  |
| deepseek-ai/deepseek-coder-33b-base/deepseek-ai/deepseek-coder-33b-instruct | blk | HELDOUT-WEAK-FAMILY | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| deepseek-ai/deepseek-coder-33b-base/deepseek-ai/deepseek-coder-33b-instruct | dom | HELDOUT | C1_delta_vs_identity | MET | 0.42587 | 0.402642 | 0.447842 | 0.0009995 |  |
| deepseek-ai/deepseek-coder-33b-base/deepseek-ai/deepseek-coder-33b-instruct | dom | HELDOUT | C2_delta_vs_length | MET | 0.41249 | 0.370921 | 0.456024 | 0.0009995 |  |
| deepseek-ai/deepseek-coder-33b-base/deepseek-ai/deepseek-coder-33b-instruct | dom | HELDOUT | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| meta-llama/Llama-3.2-1B/meta-llama/Llama-3.2-1B-Instruct | blk | HELDOUT-WEAK-FAMILY | C1_delta_vs_identity | MET | 0.339507 | 0.310313 | 0.366075 | 0.0009995 |  |
| meta-llama/Llama-3.2-1B/meta-llama/Llama-3.2-1B-Instruct | blk | HELDOUT-WEAK-FAMILY | C2_delta_vs_length | MET | 0.304122 | 0.252936 | 0.350977 | 0.0009995 |  |
| meta-llama/Llama-3.2-1B/meta-llama/Llama-3.2-1B-Instruct | blk | HELDOUT-WEAK-FAMILY | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| meta-llama/Llama-3.2-1B/meta-llama/Llama-3.2-1B-Instruct | dom | HELDOUT | C1_delta_vs_identity | MET | 0.39266 | 0.364143 | 0.416633 | 0.0009995 |  |
| meta-llama/Llama-3.2-1B/meta-llama/Llama-3.2-1B-Instruct | dom | HELDOUT | C2_delta_vs_length | MET | 0.414268 | 0.376569 | 0.450258 | 0.0009995 |  |
| meta-llama/Llama-3.2-1B/meta-llama/Llama-3.2-1B-Instruct | dom | HELDOUT | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |

Criterion 1's identity baseline is CONSTANT on the SEMANTIC-only eligible set (AUROC exactly 0.5), so C1 is equivalent to AUROC ≥ 0.60 with an interval above 0.5 (deviation D6). The exploratory `terminal_rate` baseline is the stronger 'language-identity' competitor.

## H5 arms

| family | lexicon | model | arm | seed | n_changed | per_symbol | ctrl | control_within_tolerance |
|---|---|---|---|---|---|---|---|---|
| blk | d25s3 | Qwen/Qwen2.5-72B-Instruct | global | 0 | 9 | 9.000 | — |  |
| blk | d25s3 | Qwen/Qwen2.5-72B-Instruct | random | 1 | 3 | 15.000 | -0.293 | True |
| blk | d25s3 | Qwen/Qwen2.5-72B-Instruct | random | 2 | 3 | 20.667 | -0.121 | True |
| blk | d25s3 | Qwen/Qwen2.5-72B-Instruct | random | 3 | 3 | 1.000 | 0.031 | False |
| blk | d25s3 | Qwen/Qwen2.5-72B-Instruct | random | 4 | 3 | 10.667 | -0.198 | True |
| blk | d25s3 | Qwen/Qwen2.5-72B-Instruct | random | 5 | 3 | 8.333 | -0.021 | True |
| blk | d25s3 | Qwen/Qwen2.5-72B-Instruct | targeted | 0 | 3 | 14.000 | -0.213 | True |
| blk | d50s3 | Qwen/Qwen2.5-72B-Instruct | global | 0 | 13 | 8.077 | — |  |
| blk | d50s3 | Qwen/Qwen2.5-72B-Instruct | random | 1 | 3 | 14.333 | -0.238 | True |
| blk | d50s3 | Qwen/Qwen2.5-72B-Instruct | random | 2 | 3 | 18.667 | 0.046 | False |
| blk | d50s3 | Qwen/Qwen2.5-72B-Instruct | random | 3 | 3 | 3.667 | -0.041 | True |
| blk | d50s3 | Qwen/Qwen2.5-72B-Instruct | random | 4 | 3 | 10.667 | -0.174 | True |
| blk | d50s3 | Qwen/Qwen2.5-72B-Instruct | random | 5 | 3 | 1.667 | -0.114 | True |
| blk | d50s3 | Qwen/Qwen2.5-72B-Instruct | targeted | 0 | 3 | 13.667 | -0.144 | True |
| blk | d75s1a | Qwen/Qwen2.5-72B-Instruct | global | 0 | 22 | 5.909 | — |  |
| blk | d75s1a | Qwen/Qwen2.5-72B-Instruct | random | 1 | 3 | 2.667 | -0.028 | True |
| blk | d75s1a | Qwen/Qwen2.5-72B-Instruct | random | 2 | 3 | 11.000 | -0.122 | True |
| blk | d75s1a | Qwen/Qwen2.5-72B-Instruct | random | 3 | 3 | 2.667 | 0.007 | True |
| blk | d75s1a | Qwen/Qwen2.5-72B-Instruct | random | 4 | 3 | -0.667 | 0.007 | True |
| blk | d75s1a | Qwen/Qwen2.5-72B-Instruct | random | 5 | 3 | 4.333 | -0.016 | True |
| blk | d75s1a | Qwen/Qwen2.5-72B-Instruct | targeted | 0 | 3 | 1.000 | 0.018 | True |
| blk | d75s2a | Qwen/Qwen2.5-72B-Instruct | global | 0 | 22 | 6.500 | — |  |
| blk | d75s2a | Qwen/Qwen2.5-72B-Instruct | random | 1 | 3 | 8.000 | -0.063 | True |
| blk | d75s2a | Qwen/Qwen2.5-72B-Instruct | random | 2 | 3 | 17.667 | -0.179 | True |
| blk | d75s2a | Qwen/Qwen2.5-72B-Instruct | random | 3 | 3 | 9.000 | -0.077 | True |
| blk | d75s2a | Qwen/Qwen2.5-72B-Instruct | random | 4 | 3 | 11.333 | -0.078 | True |
| blk | d75s2a | Qwen/Qwen2.5-72B-Instruct | random | 5 | 3 | 7.667 | -0.048 | True |
| blk | d75s2a | Qwen/Qwen2.5-72B-Instruct | targeted | 0 | 3 | 1.667 | -0.010 | True |
| blk | d75s3a | Qwen/Qwen2.5-72B-Instruct | global | 0 | 22 | 6.636 | — |  |
| blk | d75s3a | Qwen/Qwen2.5-72B-Instruct | random | 1 | 3 | 4.333 | -0.056 | True |
| blk | d75s3a | Qwen/Qwen2.5-72B-Instruct | random | 2 | 3 | 15.333 | -0.168 | True |
| blk | d75s3a | Qwen/Qwen2.5-72B-Instruct | random | 3 | 3 | 5.667 | -0.053 | True |
| blk | d75s3a | Qwen/Qwen2.5-72B-Instruct | random | 4 | 3 | 5.667 | -0.052 | True |
| blk | d75s3a | Qwen/Qwen2.5-72B-Instruct | random | 5 | 3 | 7.000 | -0.054 | True |
| blk | d75s3a | Qwen/Qwen2.5-72B-Instruct | targeted | 0 | 3 | 6.333 | -0.062 | True |
| dom | d25s3 | Qwen/Qwen2.5-72B-Instruct | global | 0 | 9 | 9.222 | — |  |
| dom | d25s3 | Qwen/Qwen2.5-72B-Instruct | random | 1 | 3 | 12.000 | -0.280 | True |
| dom | d25s3 | Qwen/Qwen2.5-72B-Instruct | random | 2 | 3 | 19.000 | 0.052 | False |
| dom | d25s3 | Qwen/Qwen2.5-72B-Instruct | random | 3 | 3 | 1.000 | 0.041 | False |
| dom | d25s3 | Qwen/Qwen2.5-72B-Instruct | random | 4 | 3 | 10.000 | -0.177 | True |
| dom | d25s3 | Qwen/Qwen2.5-72B-Instruct | random | 5 | 3 | 4.333 | -0.005 | True |
| dom | d25s3 | Qwen/Qwen2.5-72B-Instruct | targeted | 0 | 3 | 13.667 | -0.310 | True |
| dom | d50s3 | Qwen/Qwen2.5-72B-Instruct | global | 0 | 13 | 8.462 | — |  |
| dom | d50s3 | Qwen/Qwen2.5-72B-Instruct | random | 1 | 3 | 14.333 | -0.271 | True |
| dom | d50s3 | Qwen/Qwen2.5-72B-Instruct | random | 2 | 3 | 19.000 | 0.046 | False |
| dom | d50s3 | Qwen/Qwen2.5-72B-Instruct | random | 3 | 3 | 2.333 | -0.049 | True |
| dom | d50s3 | Qwen/Qwen2.5-72B-Instruct | random | 4 | 3 | 9.333 | -0.207 | True |
| dom | d50s3 | Qwen/Qwen2.5-72B-Instruct | random | 5 | 3 | 2.000 | -0.105 | True |
| dom | d50s3 | Qwen/Qwen2.5-72B-Instruct | targeted | 0 | 3 | 11.333 | -0.201 | True |
| dom | d75s1a | Qwen/Qwen2.5-72B-Instruct | global | 0 | 22 | 6.545 | — |  |
| dom | d75s1a | Qwen/Qwen2.5-72B-Instruct | random | 1 | 3 | 2.000 | -0.031 | True |
| dom | d75s1a | Qwen/Qwen2.5-72B-Instruct | random | 2 | 3 | 17.667 | -0.201 | True |
| dom | d75s1a | Qwen/Qwen2.5-72B-Instruct | random | 3 | 3 | 7.000 | -0.037 | True |
| dom | d75s1a | Qwen/Qwen2.5-72B-Instruct | random | 4 | 3 | -0.667 | 0.000 | True |
| dom | d75s1a | Qwen/Qwen2.5-72B-Instruct | random | 5 | 3 | 5.000 | 0.003 | True |
| dom | d75s1a | Qwen/Qwen2.5-72B-Instruct | targeted | 0 | 3 | 0.000 | 0.016 | True |
| dom | d75s2a | Qwen/Qwen2.5-72B-Instruct | global | 0 | 22 | 7.909 | — |  |
| dom | d75s2a | Qwen/Qwen2.5-72B-Instruct | random | 1 | 3 | 5.000 | -0.050 | True |
| dom | d75s2a | Qwen/Qwen2.5-72B-Instruct | random | 2 | 3 | 21.667 | -0.244 | True |
| dom | d75s2a | Qwen/Qwen2.5-72B-Instruct | random | 3 | 3 | 15.000 | -0.127 | True |
| dom | d75s2a | Qwen/Qwen2.5-72B-Instruct | random | 4 | 3 | 13.000 | -0.111 | True |
| dom | d75s2a | Qwen/Qwen2.5-72B-Instruct | random | 5 | 3 | 8.667 | -0.035 | True |
| dom | d75s2a | Qwen/Qwen2.5-72B-Instruct | targeted | 0 | 3 | 8.000 | -0.049 | True |
| dom | d75s3a | Qwen/Qwen2.5-72B-Instruct | global | 0 | 22 | 6.909 | — |  |
| dom | d75s3a | Qwen/Qwen2.5-72B-Instruct | random | 1 | 3 | 1.333 | -0.034 | True |
| dom | d75s3a | Qwen/Qwen2.5-72B-Instruct | random | 2 | 3 | 24.667 | -0.254 | True |
| dom | d75s3a | Qwen/Qwen2.5-72B-Instruct | random | 3 | 3 | 6.000 | -0.040 | True |
| dom | d75s3a | Qwen/Qwen2.5-72B-Instruct | random | 4 | 3 | 5.333 | -0.052 | True |
| dom | d75s3a | Qwen/Qwen2.5-72B-Instruct | random | 5 | 3 | 12.000 | -0.067 | True |
| dom | d75s3a | Qwen/Qwen2.5-72B-Instruct | targeted | 0 | 3 | 3.000 | -0.018 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | global | 0 | 9 | 2.778 | — |  |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 1 | 3 | 4.000 | -0.197 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 2 | 3 | 8.000 | -0.138 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 3 | 3 | -3.333 | -0.005 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 4 | 3 | 3.667 | -0.333 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 5 | 3 | 1.667 | -0.021 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | targeted | 0 | 3 | 6.333 | -0.148 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | global | 0 | 13 | 1.231 | — |  |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 1 | 3 | -0.667 | -0.081 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 2 | 3 | 1.333 | 0.037 | False |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 3 | 3 | -0.333 | 0.012 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 4 | 3 | 3.667 | -0.103 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 5 | 3 | -3.333 | 0.004 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | targeted | 0 | 3 | 5.000 | -0.037 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | global | 0 | 22 | 2.682 | — |  |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 1 | 3 | -6.667 | 0.016 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 2 | 3 | 4.333 | -0.097 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 3 | 3 | -6.667 | -0.010 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 4 | 3 | -0.667 | -0.016 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 5 | 3 | 5.333 | -0.061 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | targeted | 0 | 3 | 0.667 | 0.003 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | global | 0 | 22 | 2.364 | — |  |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 1 | 3 | -4.333 | -0.022 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 2 | 3 | 2.333 | -0.072 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 3 | 3 | -1.667 | -0.080 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 4 | 3 | -1.000 | -0.039 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 5 | 3 | 4.333 | -0.093 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | targeted | 0 | 3 | 1.000 | 0.010 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | global | 0 | 22 | 2.227 | — |  |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 1 | 3 | -6.333 | 0.006 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 2 | 3 | 0.000 | -0.047 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 3 | 3 | -4.667 | -0.017 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 4 | 3 | -1.333 | -0.023 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 5 | 3 | 0.333 | -0.006 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | targeted | 0 | 3 | -0.667 | 0.029 | False |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | global | 0 | 9 | 2.111 | — |  |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 1 | 3 | -0.667 | -0.089 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 2 | 3 | 1.667 | -0.017 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 3 | 3 | -4.000 | 0.005 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 4 | 3 | -0.333 | -0.333 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 5 | 3 | 0.333 | 0.000 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | targeted | 0 | 3 | 2.667 | -0.097 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | global | 0 | 13 | 2.000 | — |  |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 1 | 3 | -0.667 | -0.057 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 2 | 3 | 1.000 | -0.009 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 3 | 3 | -1.333 | 0.000 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 4 | 3 | 1.667 | -0.070 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 5 | 3 | -2.000 | -0.021 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | targeted | 0 | 3 | 2.333 | -0.053 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | global | 0 | 22 | 2.773 | — |  |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 1 | 3 | -3.667 | -0.009 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 2 | 3 | 4.333 | -0.086 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 3 | 3 | -4.667 | 0.000 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 4 | 3 | -3.333 | 0.003 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 5 | 3 | 7.000 | -0.051 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | targeted | 0 | 3 | -1.667 | 0.013 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | global | 0 | 22 | 2.636 | — |  |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 1 | 3 | -0.667 | -0.060 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 2 | 3 | 4.333 | -0.068 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 3 | 3 | -1.333 | -0.080 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 4 | 3 | -0.667 | -0.046 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 5 | 3 | 7.000 | -0.077 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | targeted | 0 | 3 | -1.333 | 0.013 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | global | 0 | 22 | 1.955 | — |  |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 1 | 3 | -5.000 | -0.009 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 2 | 3 | 2.667 | -0.065 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 3 | 3 | -7.000 | 0.010 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 4 | 3 | -5.333 | 0.007 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | random | 5 | 3 | -1.333 | 0.013 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | targeted | 0 | 3 | -2.667 | 0.038 | False |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | global | 0 | 9 | 8.111 | — |  |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 1 | 3 | 14.667 | -0.331 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 2 | 3 | 26.333 | -0.121 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 3 | 3 | 1.333 | -0.052 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 4 | 3 | 15.333 | -0.417 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 5 | 3 | 3.667 | -0.048 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | targeted | 0 | 3 | 12.333 | -0.282 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | global | 0 | 13 | 7.615 | — |  |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 1 | 3 | 8.667 | -0.210 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 2 | 3 | 21.667 | 0.028 | False |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 3 | 3 | 1.667 | -0.066 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 4 | 3 | 10.000 | -0.207 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 5 | 3 | -2.000 | -0.034 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | targeted | 0 | 3 | 12.667 | -0.145 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | global | 0 | 22 | 6.818 | — |  |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 1 | 3 | 0.000 | 0.000 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 2 | 3 | 10.667 | -0.158 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 3 | 3 | 2.667 | -0.010 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 4 | 3 | 1.333 | -0.042 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 5 | 3 | 3.667 | -0.048 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | targeted | 0 | 3 | 2.667 | -0.013 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | global | 0 | 22 | 6.545 | — |  |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 1 | 3 | -0.667 | -0.016 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 2 | 3 | 12.000 | -0.190 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 3 | 3 | 4.000 | -0.093 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 4 | 3 | 2.333 | -0.056 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 5 | 3 | 1.000 | -0.045 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | targeted | 0 | 3 | -2.000 | 0.030 | False |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | global | 0 | 22 | 6.455 | — |  |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 1 | 3 | -4.000 | 0.009 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 2 | 3 | 12.000 | -0.186 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 3 | 3 | 0.667 | -0.020 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 4 | 3 | 1.000 | -0.033 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 5 | 3 | -2.667 | -0.013 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | targeted | 0 | 3 | 3.667 | -0.025 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | global | 0 | 9 | 5.444 | — |  |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 1 | 3 | 7.333 | -0.146 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 2 | 3 | 19.333 | -0.172 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 3 | 3 | -2.333 | -0.010 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 4 | 3 | 8.333 | -0.365 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 5 | 3 | 2.333 | -0.021 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | targeted | 0 | 3 | 6.667 | -0.141 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | global | 0 | 13 | 6.000 | — |  |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 1 | 3 | 3.667 | -0.100 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 2 | 3 | 15.000 | 0.000 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 3 | 3 | -2.667 | -0.016 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 4 | 3 | 5.667 | -0.108 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 5 | 3 | -1.333 | -0.034 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | targeted | 0 | 3 | 6.667 | -0.073 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | global | 0 | 22 | 5.727 | — |  |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 1 | 3 | 1.000 | -0.013 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 2 | 3 | 7.333 | -0.097 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 3 | 3 | 6.000 | -0.063 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 4 | 3 | 0.333 | -0.020 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 5 | 3 | 7.000 | -0.064 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | targeted | 0 | 3 | 0.000 | 0.006 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | global | 0 | 22 | 4.818 | — |  |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 1 | 3 | -2.333 | 0.000 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 2 | 3 | 7.667 | -0.115 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 3 | 3 | 4.000 | -0.057 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 4 | 3 | -1.000 | -0.023 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 5 | 3 | 2.333 | -0.026 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | targeted | 0 | 3 | -5.667 | 0.023 | False |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | global | 0 | 22 | 4.455 | — |  |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 1 | 3 | -2.667 | 0.003 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 2 | 3 | 4.667 | -0.072 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 3 | 3 | -1.667 | -0.013 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 4 | 3 | -4.333 | 0.007 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | random | 5 | 3 | -2.000 | 0.003 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | targeted | 0 | 3 | -1.667 | 0.022 | False |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | global | 0 | 9 | 8.667 | — |  |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 1 | 3 | 8.667 | -0.344 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 2 | 3 | 13.667 | -0.224 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 3 | 3 | 3.000 | -0.026 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 4 | 3 | 11.000 | -0.198 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 5 | 3 | 6.667 | -0.016 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | targeted | 0 | 3 | 5.333 | -0.250 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | global | 0 | 13 | 7.308 | — |  |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 1 | 3 | 0.333 | -0.152 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 2 | 3 | 3.000 | 0.009 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 3 | 3 | 1.333 | -0.021 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 4 | 3 | -0.667 | -0.103 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 5 | 3 | 0.000 | -0.059 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | targeted | 0 | 3 | 0.667 | -0.012 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | global | 0 | 22 | 5.500 | — |  |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 1 | 3 | 1.333 | -0.025 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 2 | 3 | 3.000 | -0.147 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 3 | 3 | 1.333 | 0.017 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 4 | 3 | 1.333 | -0.013 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 5 | 3 | 3.333 | -0.022 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | targeted | 0 | 3 | -1.000 | 0.010 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | global | 0 | 22 | 6.545 | — |  |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 1 | 3 | 4.333 | -0.063 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 2 | 3 | 3.000 | -0.147 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 3 | 3 | 13.667 | -0.097 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 4 | 3 | 11.333 | -0.101 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 5 | 3 | 2.000 | -0.038 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | targeted | 0 | 3 | 5.333 | -0.050 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | global | 0 | 22 | 5.227 | — |  |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 1 | 3 | 1.000 | -0.022 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 2 | 3 | -1.667 | -0.108 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 3 | 3 | 3.333 | -0.007 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 4 | 3 | 1.667 | -0.003 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 5 | 3 | 0.667 | -0.038 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | targeted | 0 | 3 | 2.333 | -0.019 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | global | 0 | 9 | 7.778 | — |  |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 1 | 3 | 6.667 | -0.331 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 2 | 3 | 16.333 | -0.224 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 3 | 3 | 2.333 | -0.010 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 4 | 3 | 11.333 | -0.115 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 5 | 3 | 7.000 | 0.000 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | targeted | 0 | 3 | 5.333 | -0.237 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | global | 0 | 13 | 7.692 | — |  |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 1 | 3 | 4.667 | -0.210 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 2 | 3 | 15.000 | -0.046 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 3 | 3 | 2.333 | -0.004 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 4 | 3 | 1.667 | -0.141 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | random | 5 | 3 | 2.333 | -0.093 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | targeted | 0 | 3 | 4.333 | -0.037 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | global | 0 | 22 | 5.500 | — |  |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 1 | 3 | 2.333 | -0.041 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 2 | 3 | 5.333 | -0.161 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 3 | 3 | 3.333 | 0.003 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 4 | 3 | 4.000 | -0.023 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 5 | 3 | 3.667 | -0.022 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | targeted | 0 | 3 | 2.333 | -0.022 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | global | 0 | 22 | 6.091 | — |  |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 1 | 3 | 3.667 | -0.038 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 2 | 3 | 2.333 | -0.122 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 3 | 3 | 11.667 | -0.097 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 4 | 3 | 10.000 | -0.092 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 5 | 3 | 9.000 | -0.029 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | targeted | 0 | 3 | 2.667 | -0.041 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | global | 0 | 22 | 5.273 | — |  |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 1 | 3 | 0.667 | -0.022 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 2 | 3 | 4.667 | -0.158 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 3 | 3 | 7.333 | -0.033 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 4 | 3 | 3.667 | -0.016 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | random | 5 | 3 | 4.000 | -0.045 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | targeted | 0 | 3 | 4.000 | -0.016 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | global | 0 | 9 | 11.222 | — |  |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 1 | 3 | 18.667 | -0.344 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 2 | 3 | 27.667 | -0.103 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 3 | 3 | 4.000 | -0.067 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 4 | 3 | 18.667 | -0.198 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 5 | 3 | 6.333 | -0.016 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | targeted | 0 | 3 | 19.333 | -0.349 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | global | 0 | 13 | 8.923 | — |  |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 1 | 3 | 10.667 | -0.229 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 2 | 3 | 25.667 | -0.194 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 3 | 3 | 4.000 | -0.041 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 4 | 3 | 13.667 | -0.239 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 5 | 3 | 1.000 | -0.076 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | targeted | 0 | 3 | 15.000 | -0.221 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | global | 0 | 22 | 6.591 | — |  |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 1 | 3 | 1.667 | -0.034 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 2 | 3 | 13.000 | -0.172 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 3 | 3 | 2.333 | -0.053 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 4 | 3 | 3.000 | -0.049 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 5 | 3 | -0.333 | -0.006 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | targeted | 0 | 3 | 1.333 | -0.023 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | global | 0 | 22 | 6.409 | — |  |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 1 | 3 | 3.333 | -0.056 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 2 | 3 | 10.000 | -0.186 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 3 | 3 | 5.333 | -0.027 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 4 | 3 | 10.333 | -0.075 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 5 | 3 | 1.667 | -0.038 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | targeted | 0 | 3 | 2.667 | -0.033 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | global | 0 | 22 | 6.091 | — |  |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 1 | 3 | 0.000 | -0.006 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 2 | 3 | 11.000 | -0.179 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 3 | 3 | -3.000 | 0.030 | False |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 4 | 3 | 1.000 | -0.010 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 5 | 3 | 1.667 | -0.042 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | targeted | 0 | 3 | 0.333 | 0.006 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | global | 0 | 9 | 9.000 | — |  |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 1 | 3 | 7.000 | -0.248 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 2 | 3 | 21.000 | -0.138 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 3 | 3 | 3.000 | -0.021 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 4 | 3 | 10.667 | -0.240 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 5 | 3 | 5.667 | 0.005 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | targeted | 0 | 3 | 8.000 | -0.224 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | global | 0 | 13 | 7.462 | — |  |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 1 | 3 | 3.667 | -0.143 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 2 | 3 | 20.333 | -0.102 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 3 | 3 | 6.000 | -0.053 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 4 | 3 | 6.000 | -0.164 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | random | 5 | 3 | 1.000 | -0.055 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | targeted | 0 | 3 | 7.333 | -0.157 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | global | 0 | 22 | 5.636 | — |  |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 1 | 3 | -0.667 | -0.016 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 2 | 3 | 2.000 | -0.097 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 3 | 3 | -3.333 | 0.023 | False |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 4 | 3 | -1.000 | 0.000 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 5 | 3 | 5.000 | -0.051 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | targeted | 0 | 3 | 0.000 | 0.018 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | global | 0 | 22 | 5.500 | — |  |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 1 | 3 | -1.667 | -0.006 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 2 | 3 | -3.000 | -0.072 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 3 | 3 | 3.667 | -0.040 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 4 | 3 | 9.000 | -0.082 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 5 | 3 | -2.667 | 0.010 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | targeted | 0 | 3 | -2.333 | -0.034 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | global | 0 | 22 | 5.273 | — |  |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 1 | 3 | -0.667 | -0.022 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 2 | 3 | 3.000 | -0.097 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 3 | 3 | -0.667 | -0.007 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 4 | 3 | 3.333 | -0.020 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | random | 5 | 3 | 1.333 | -0.013 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | targeted | 0 | 3 | 2.000 | 0.000 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | global | 0 | 9 | 5.222 | — |  |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 1 | 3 | 8.000 | -0.274 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 2 | 3 | 11.667 | -0.207 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 3 | 3 | -4.000 | -0.005 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 4 | 3 | 7.333 | -0.260 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 5 | 3 | 4.333 | -0.011 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | targeted | 0 | 3 | 5.333 | -0.068 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | global | 0 | 13 | 5.615 | — |  |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 1 | 3 | 10.667 | -0.186 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 2 | 3 | 8.667 | 0.037 | False |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 3 | 3 | -0.667 | -0.012 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 4 | 3 | 11.333 | -0.207 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 5 | 3 | 3.000 | -0.055 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | targeted | 0 | 3 | 11.000 | -0.119 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | global | 0 | 22 | 4.727 | — |  |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 1 | 3 | 0.000 | -0.006 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 2 | 3 | 12.333 | -0.147 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 3 | 3 | 1.000 | -0.057 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 4 | 3 | -0.667 | -0.049 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 5 | 3 | 8.333 | -0.073 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | targeted | 0 | 3 | -4.333 | 0.035 | False |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | global | 0 | 22 | 4.500 | — |  |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 1 | 3 | -4.333 | 0.009 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 2 | 3 | 9.333 | -0.161 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 3 | 3 | 0.667 | -0.040 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 4 | 3 | -1.333 | -0.007 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 5 | 3 | 5.333 | -0.073 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | targeted | 0 | 3 | -4.333 | 0.047 | False |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | global | 0 | 22 | 4.818 | — |  |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 1 | 3 | 1.667 | -0.025 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 2 | 3 | 14.667 | -0.168 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 3 | 3 | 2.667 | -0.063 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 4 | 3 | -0.333 | -0.036 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 5 | 3 | 7.000 | -0.064 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | targeted | 0 | 3 | -1.667 | 0.022 | False |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | global | 0 | 9 | 7.444 | — |  |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 1 | 3 | 11.000 | -0.280 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 2 | 3 | 17.333 | -0.155 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 3 | 3 | -2.667 | -0.005 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 4 | 3 | 9.667 | -0.302 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 5 | 3 | 4.000 | -0.005 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | targeted | 0 | 3 | 7.333 | -0.109 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | global | 0 | 13 | 6.615 | — |  |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 1 | 3 | 8.333 | -0.152 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 2 | 3 | 12.333 | -0.037 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 3 | 3 | -0.667 | -0.012 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 4 | 3 | 7.333 | -0.164 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | random | 5 | 3 | 0.333 | -0.025 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | targeted | 0 | 3 | 6.667 | -0.082 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | global | 0 | 22 | 4.864 | — |  |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 1 | 3 | 0.667 | -0.009 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 2 | 3 | 9.667 | -0.125 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 3 | 3 | 4.667 | -0.087 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 4 | 3 | 0.000 | -0.039 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 5 | 3 | 4.000 | -0.035 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | targeted | 0 | 3 | -2.000 | 0.019 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | global | 0 | 22 | 4.682 | — |  |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 1 | 3 | -3.667 | 0.000 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 2 | 3 | 10.000 | -0.140 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 3 | 3 | 1.000 | -0.043 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 4 | 3 | -0.667 | -0.023 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 5 | 3 | 0.667 | -0.035 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | targeted | 0 | 3 | -1.000 | 0.025 | False |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | global | 0 | 22 | 4.591 | — |  |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 1 | 3 | -2.667 | -0.003 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 2 | 3 | 12.667 | -0.158 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 3 | 3 | 2.333 | -0.063 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 4 | 3 | 2.000 | -0.049 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | random | 5 | 3 | 2.000 | -0.016 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | targeted | 0 | 3 | -1.667 | 0.016 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | global | 0 | 9 | 4.667 | — |  |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 1 | 3 | 2.667 | -0.229 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 2 | 3 | 11.000 | -0.086 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 3 | 3 | 1.000 | 0.005 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 4 | 3 | 8.667 | -0.104 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 5 | 3 | 5.667 | -0.027 | True |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | targeted | 0 | 3 | 1.333 | 0.021 | False |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | global | 0 | 13 | 7.154 | — |  |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 1 | 3 | 1.000 | -0.148 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 2 | 3 | 6.333 | 0.019 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 3 | 3 | 4.333 | -0.037 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 4 | 3 | -0.333 | -0.127 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 5 | 3 | 3.333 | -0.101 | True |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | targeted | 0 | 3 | 2.667 | 0.000 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | global | 0 | 22 | 6.182 | — |  |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 1 | 3 | 1.667 | -0.028 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 2 | 3 | 3.000 | -0.118 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 3 | 3 | 4.000 | -0.043 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 4 | 3 | 4.667 | -0.052 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 5 | 3 | 9.333 | -0.061 | True |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | targeted | 0 | 3 | 1.667 | 0.003 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | global | 0 | 22 | 5.227 | — |  |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 1 | 3 | 3.667 | -0.056 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 2 | 3 | 5.667 | -0.158 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 3 | 3 | 2.667 | -0.060 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 4 | 3 | 5.667 | -0.065 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 5 | 3 | 3.000 | -0.016 | True |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | targeted | 0 | 3 | -0.333 | 0.010 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | global | 0 | 22 | 5.455 | — |  |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 1 | 3 | 1.333 | -0.044 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 2 | 3 | 3.333 | -0.136 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 3 | 3 | 5.000 | -0.070 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 4 | 3 | 5.667 | -0.062 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 5 | 3 | 8.000 | -0.073 | True |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | targeted | 0 | 3 | 3.333 | 0.006 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | global | 0 | 9 | 6.111 | — |  |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 1 | 3 | 4.333 | -0.236 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 2 | 3 | 12.000 | -0.224 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 3 | 3 | 2.333 | 0.005 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 4 | 3 | 8.667 | -0.146 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 5 | 3 | 7.667 | -0.027 | True |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | targeted | 0 | 3 | 3.333 | -0.203 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | global | 0 | 13 | 7.000 | — |  |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 1 | 3 | 7.333 | -0.167 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 2 | 3 | 10.667 | -0.037 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 3 | 3 | 8.000 | -0.041 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 4 | 3 | 3.000 | -0.108 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | random | 5 | 3 | 4.000 | -0.105 | True |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | targeted | 0 | 3 | 8.000 | -0.154 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | global | 0 | 22 | 5.727 | — |  |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 1 | 3 | 4.333 | -0.056 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 2 | 3 | 9.667 | -0.161 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 3 | 3 | 8.000 | -0.090 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 4 | 3 | 9.000 | -0.088 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 5 | 3 | 2.333 | 0.003 | True |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | targeted | 0 | 3 | 7.667 | -0.069 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | global | 0 | 22 | 5.773 | — |  |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 1 | 3 | 5.667 | -0.072 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 2 | 3 | 8.333 | -0.168 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 3 | 3 | 6.667 | -0.087 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 4 | 3 | 8.333 | -0.088 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 5 | 3 | 10.667 | -0.073 | True |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | targeted | 0 | 3 | 3.667 | -0.029 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | global | 0 | 22 | 5.545 | — |  |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 1 | 3 | 3.667 | -0.044 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 2 | 3 | 7.667 | -0.154 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 3 | 3 | 8.667 | -0.090 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 4 | 3 | 4.000 | -0.042 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | random | 5 | 3 | 6.333 | -0.058 | True |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | targeted | 0 | 3 | 11.000 | -0.058 | True |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | global | 0 | 9 | 4.444 | — |  |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 1 | 3 | 8.667 | -0.287 | True |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 2 | 3 | 9.667 | -0.034 | True |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 3 | 3 | -0.333 | 0.005 | True |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 4 | 3 | 4.333 | -0.219 | True |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 5 | 3 | 5.000 | -0.059 | True |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | targeted | 0 | 3 | 8.667 | -0.100 | True |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | global | 0 | 13 | 5.923 | — |  |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 1 | 3 | 2.333 | -0.186 | True |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 2 | 3 | 10.000 | 0.000 | True |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 3 | 3 | 2.667 | -0.066 | True |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 4 | 3 | 5.000 | -0.197 | True |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 5 | 3 | 0.000 | -0.025 | True |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | targeted | 0 | 3 | 8.333 | -0.066 | True |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | global | 0 | 22 | 5.045 | — |  |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 1 | 3 | 0.000 | -0.031 | True |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 2 | 3 | 11.000 | -0.215 | True |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 3 | 3 | 4.000 | -0.023 | True |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 4 | 3 | 3.667 | -0.036 | True |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 5 | 3 | 8.000 | -0.058 | True |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | targeted | 0 | 3 | 1.667 | -0.013 | True |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | global | 0 | 22 | 4.182 | — |  |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 1 | 3 | -5.000 | 0.003 | True |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 2 | 3 | 8.333 | -0.151 | True |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 3 | 3 | 4.000 | -0.060 | True |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 4 | 3 | 0.000 | -0.029 | True |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 5 | 3 | 11.667 | -0.083 | True |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | targeted | 0 | 3 | 1.667 | -0.003 | True |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | global | 0 | 22 | 4.591 | — |  |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 1 | 3 | -3.000 | -0.025 | True |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 2 | 3 | 8.667 | -0.172 | True |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 3 | 3 | 1.333 | -0.020 | True |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 4 | 3 | 2.333 | -0.036 | True |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 5 | 3 | 4.000 | -0.026 | True |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | targeted | 0 | 3 | 6.000 | -0.025 | True |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | global | 0 | 9 | 5.000 | — |  |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 1 | 3 | 0.000 | -0.102 | True |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 2 | 3 | 8.333 | 0.000 | True |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 3 | 3 | -1.667 | 0.015 | True |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 4 | 3 | 5.667 | -0.271 | True |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 5 | 3 | 3.667 | -0.016 | True |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | targeted | 0 | 3 | 0.667 | 0.000 | True |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | global | 0 | 13 | 6.385 | — |  |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 1 | 3 | 0.667 | -0.143 | True |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 2 | 3 | 14.333 | -0.009 | True |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 3 | 3 | -3.667 | 0.021 | False |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 4 | 3 | 5.667 | -0.192 | True |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | random | 5 | 3 | -2.333 | -0.034 | True |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | targeted | 0 | 3 | 8.000 | -0.091 | True |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | global | 0 | 22 | 4.182 | — |  |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 1 | 3 | -3.667 | -0.003 | True |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 2 | 3 | 5.333 | -0.118 | True |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 3 | 3 | 5.333 | -0.023 | True |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 4 | 3 | -1.667 | 0.010 | True |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 5 | 3 | 6.000 | -0.032 | True |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | targeted | 0 | 3 | -5.333 | 0.051 | False |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | global | 0 | 22 | 3.727 | — |  |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 1 | 3 | -5.333 | -0.009 | True |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 2 | 3 | 4.333 | -0.125 | True |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 3 | 3 | 1.667 | -0.067 | True |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 4 | 3 | 1.333 | -0.039 | True |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 5 | 3 | 6.667 | -0.029 | True |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | targeted | 0 | 3 | -0.667 | 0.010 | True |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | global | 0 | 22 | 3.591 | — |  |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 1 | 3 | -4.667 | -0.019 | True |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 2 | 3 | 2.667 | -0.097 | True |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 3 | 3 | 2.667 | -0.030 | True |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 4 | 3 | -1.333 | 0.000 | True |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | random | 5 | 3 | 0.667 | -0.016 | True |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | targeted | 0 | 3 | -1.333 | 0.022 | False |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | global | 0 | 9 | 7.556 | — |  |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 1 | 3 | 10.333 | -0.280 | True |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 2 | 3 | 17.667 | -0.034 | True |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 3 | 3 | -1.000 | -0.010 | True |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 4 | 3 | 5.000 | -0.292 | True |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 5 | 3 | 5.333 | -0.032 | True |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | targeted | 0 | 3 | 5.333 | 0.175 | False |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | global | 0 | 13 | 7.846 | — |  |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 1 | 3 | 5.667 | -0.152 | True |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 2 | 3 | 11.000 | 0.046 | False |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 3 | 3 | 1.667 | -0.021 | True |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 4 | 3 | 4.667 | -0.136 | True |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 5 | 3 | 7.333 | -0.080 | True |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | targeted | 0 | 3 | 6.333 | -0.073 | True |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | global | 0 | 22 | 6.182 | — |  |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | random | 1 | 3 | -1.667 | -0.009 | True |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | random | 2 | 3 | 8.000 | -0.147 | True |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | random | 3 | 3 | 0.000 | -0.017 | True |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | random | 4 | 3 | -4.667 | 0.000 | True |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | random | 5 | 3 | 1.667 | -0.032 | True |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | targeted | 0 | 3 | 2.333 | -0.019 | True |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | global | 0 | 22 | 6.091 | — |  |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | random | 1 | 3 | -0.667 | -0.031 | True |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | random | 2 | 3 | 10.333 | -0.172 | True |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | random | 3 | 3 | 3.333 | -0.057 | True |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | random | 4 | 3 | -5.333 | 0.016 | True |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | random | 5 | 3 | 4.333 | -0.038 | True |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | targeted | 0 | 3 | 1.000 | -0.013 | True |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | global | 0 | 22 | 5.909 | — |  |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | random | 1 | 3 | -2.667 | -0.006 | True |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | random | 2 | 3 | 6.000 | -0.140 | True |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | random | 3 | 3 | 2.000 | -0.047 | True |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | random | 4 | 3 | -1.000 | -0.042 | True |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | random | 5 | 3 | -5.000 | 0.016 | True |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | targeted | 0 | 3 | 4.667 | -0.009 | True |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | global | 0 | 9 | 12.333 | — |  |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 1 | 3 | 16.000 | -0.369 | True |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 2 | 3 | 28.333 | -0.138 | True |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 3 | 3 | 0.000 | 0.010 | True |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 4 | 3 | 7.667 | -0.240 | True |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 5 | 3 | 5.667 | 0.000 | True |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | targeted | 0 | 3 | 18.333 | -0.198 | True |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | global | 0 | 13 | 10.615 | — |  |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 1 | 3 | 12.667 | -0.267 | True |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 2 | 3 | 26.333 | 0.037 | False |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 3 | 3 | 4.000 | -0.008 | True |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 4 | 3 | 10.667 | -0.221 | True |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | random | 5 | 3 | 6.667 | -0.072 | True |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | targeted | 0 | 3 | 17.333 | -0.173 | True |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | global | 0 | 22 | 7.591 | — |  |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | random | 1 | 3 | 1.667 | -0.041 | True |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | random | 2 | 3 | 13.333 | -0.211 | True |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | random | 3 | 3 | 3.667 | -0.033 | True |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | random | 4 | 3 | -0.667 | -0.052 | True |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | random | 5 | 3 | 2.667 | -0.029 | True |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | targeted | 0 | 3 | 1.000 | -0.009 | True |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | global | 0 | 22 | 7.182 | — |  |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | random | 1 | 3 | 0.000 | -0.028 | True |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | random | 2 | 3 | 13.667 | -0.215 | True |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | random | 3 | 3 | 3.333 | -0.047 | True |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | random | 4 | 3 | -3.667 | -0.010 | True |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | random | 5 | 3 | 4.333 | -0.029 | True |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | targeted | 0 | 3 | 2.000 | 0.003 | True |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | global | 0 | 22 | 7.727 | — |  |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | random | 1 | 3 | 0.000 | -0.031 | True |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | random | 2 | 3 | 17.000 | -0.251 | True |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | random | 3 | 3 | 6.000 | -0.067 | True |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | random | 4 | 3 | -1.000 | -0.036 | True |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | random | 5 | 3 | 1.000 | -0.029 | True |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | targeted | 0 | 3 | 6.000 | -0.016 | True |
| blk | d25s3 | meta-llama/Llama-3.2-1B-Instruct | global | 0 | 9 | 4.889 | — |  |
| blk | d25s3 | meta-llama/Llama-3.2-1B-Instruct | random | 1 | 3 | 11.333 | -0.268 | True |
| blk | d25s3 | meta-llama/Llama-3.2-1B-Instruct | random | 2 | 3 | 7.667 | -0.052 | True |
| blk | d25s3 | meta-llama/Llama-3.2-1B-Instruct | random | 3 | 3 | -1.667 | -0.021 | True |
| blk | d25s3 | meta-llama/Llama-3.2-1B-Instruct | random | 4 | 3 | 7.000 | -0.260 | True |
| blk | d25s3 | meta-llama/Llama-3.2-1B-Instruct | random | 5 | 3 | 4.667 | -0.053 | True |
| blk | d25s3 | meta-llama/Llama-3.2-1B-Instruct | targeted | 0 | 3 | 13.000 | -0.290 | True |
| blk | d50s3 | meta-llama/Llama-3.2-1B-Instruct | global | 0 | 13 | 3.231 | — |  |
| blk | d50s3 | meta-llama/Llama-3.2-1B-Instruct | random | 1 | 3 | 8.000 | -0.186 | True |
| blk | d50s3 | meta-llama/Llama-3.2-1B-Instruct | random | 2 | 3 | 7.000 | -0.046 | True |
| blk | d50s3 | meta-llama/Llama-3.2-1B-Instruct | random | 3 | 3 | 0.000 | -0.021 | True |
| blk | d50s3 | meta-llama/Llama-3.2-1B-Instruct | random | 4 | 3 | 6.000 | -0.146 | True |
| blk | d50s3 | meta-llama/Llama-3.2-1B-Instruct | random | 5 | 3 | -2.333 | -0.042 | True |
| blk | d50s3 | meta-llama/Llama-3.2-1B-Instruct | targeted | 0 | 3 | 13.333 | -0.222 | True |
| blk | d75s1a | meta-llama/Llama-3.2-1B-Instruct | global | 0 | 22 | 4.136 | — |  |
| blk | d75s1a | meta-llama/Llama-3.2-1B-Instruct | random | 1 | 3 | -2.333 | -0.016 | True |
| blk | d75s1a | meta-llama/Llama-3.2-1B-Instruct | random | 2 | 3 | 9.000 | -0.143 | True |
| blk | d75s1a | meta-llama/Llama-3.2-1B-Instruct | random | 3 | 3 | -4.333 | 0.020 | False |
| blk | d75s1a | meta-llama/Llama-3.2-1B-Instruct | random | 4 | 3 | -5.667 | 0.013 | True |
| blk | d75s1a | meta-llama/Llama-3.2-1B-Instruct | random | 5 | 3 | 4.667 | -0.042 | True |
| blk | d75s1a | meta-llama/Llama-3.2-1B-Instruct | targeted | 0 | 3 | -1.667 | 0.013 | True |
| blk | d75s2a | meta-llama/Llama-3.2-1B-Instruct | global | 0 | 22 | 4.273 | — |  |
| blk | d75s2a | meta-llama/Llama-3.2-1B-Instruct | random | 1 | 3 | -5.667 | -0.003 | True |
| blk | d75s2a | meta-llama/Llama-3.2-1B-Instruct | random | 2 | 3 | 7.333 | -0.129 | True |
| blk | d75s2a | meta-llama/Llama-3.2-1B-Instruct | random | 3 | 3 | 1.333 | -0.057 | True |
| blk | d75s2a | meta-llama/Llama-3.2-1B-Instruct | random | 4 | 3 | -1.667 | -0.016 | True |
| blk | d75s2a | meta-llama/Llama-3.2-1B-Instruct | random | 5 | 3 | 2.667 | -0.070 | True |
| blk | d75s2a | meta-llama/Llama-3.2-1B-Instruct | targeted | 0 | 3 | 3.000 | -0.026 | True |
| blk | d75s3a | meta-llama/Llama-3.2-1B-Instruct | global | 0 | 22 | 4.318 | — |  |
| blk | d75s3a | meta-llama/Llama-3.2-1B-Instruct | random | 1 | 3 | -6.667 | 0.006 | True |
| blk | d75s3a | meta-llama/Llama-3.2-1B-Instruct | random | 2 | 3 | 8.667 | -0.161 | True |
| blk | d75s3a | meta-llama/Llama-3.2-1B-Instruct | random | 3 | 3 | -4.667 | 0.010 | True |
| blk | d75s3a | meta-llama/Llama-3.2-1B-Instruct | random | 4 | 3 | -9.333 | 0.052 | False |
| blk | d75s3a | meta-llama/Llama-3.2-1B-Instruct | random | 5 | 3 | 1.000 | -0.010 | True |
| blk | d75s3a | meta-llama/Llama-3.2-1B-Instruct | targeted | 0 | 3 | 1.000 | -0.003 | True |
| dom | d25s3 | meta-llama/Llama-3.2-1B-Instruct | global | 0 | 9 | 6.222 | — |  |
| dom | d25s3 | meta-llama/Llama-3.2-1B-Instruct | random | 1 | 3 | 12.667 | -0.204 | True |
| dom | d25s3 | meta-llama/Llama-3.2-1B-Instruct | random | 2 | 3 | 12.333 | -0.069 | True |
| dom | d25s3 | meta-llama/Llama-3.2-1B-Instruct | random | 3 | 3 | -2.333 | -0.015 | True |
| dom | d25s3 | meta-llama/Llama-3.2-1B-Instruct | random | 4 | 3 | 5.667 | -0.292 | True |
| dom | d25s3 | meta-llama/Llama-3.2-1B-Instruct | random | 5 | 3 | 2.667 | 0.011 | True |
| dom | d25s3 | meta-llama/Llama-3.2-1B-Instruct | targeted | 0 | 3 | 10.333 | -0.174 | True |
| dom | d50s3 | meta-llama/Llama-3.2-1B-Instruct | global | 0 | 13 | 3.385 | — |  |
| dom | d50s3 | meta-llama/Llama-3.2-1B-Instruct | random | 1 | 3 | 7.667 | -0.148 | True |
| dom | d50s3 | meta-llama/Llama-3.2-1B-Instruct | random | 2 | 3 | 8.000 | -0.056 | True |
| dom | d50s3 | meta-llama/Llama-3.2-1B-Instruct | random | 3 | 3 | -2.667 | 0.012 | True |
| dom | d50s3 | meta-llama/Llama-3.2-1B-Instruct | random | 4 | 3 | 6.000 | -0.113 | True |
| dom | d50s3 | meta-llama/Llama-3.2-1B-Instruct | random | 5 | 3 | -1.000 | -0.063 | True |
| dom | d50s3 | meta-llama/Llama-3.2-1B-Instruct | targeted | 0 | 3 | 9.000 | -0.111 | True |
| dom | d75s1a | meta-llama/Llama-3.2-1B-Instruct | global | 0 | 22 | 3.864 | — |  |
| dom | d75s1a | meta-llama/Llama-3.2-1B-Instruct | random | 1 | 3 | -1.667 | -0.016 | True |
| dom | d75s1a | meta-llama/Llama-3.2-1B-Instruct | random | 2 | 3 | 9.000 | -0.122 | True |
| dom | d75s1a | meta-llama/Llama-3.2-1B-Instruct | random | 3 | 3 | -5.000 | 0.010 | True |
| dom | d75s1a | meta-llama/Llama-3.2-1B-Instruct | random | 4 | 3 | -7.000 | 0.049 | False |
| dom | d75s1a | meta-llama/Llama-3.2-1B-Instruct | random | 5 | 3 | 6.333 | -0.054 | True |
| dom | d75s1a | meta-llama/Llama-3.2-1B-Instruct | targeted | 0 | 3 | 0.667 | -0.003 | True |
| dom | d75s2a | meta-llama/Llama-3.2-1B-Instruct | global | 0 | 22 | 3.545 | — |  |
| dom | d75s2a | meta-llama/Llama-3.2-1B-Instruct | random | 1 | 3 | -4.000 | -0.009 | True |
| dom | d75s2a | meta-llama/Llama-3.2-1B-Instruct | random | 2 | 3 | 7.667 | -0.090 | True |
| dom | d75s2a | meta-llama/Llama-3.2-1B-Instruct | random | 3 | 3 | -1.667 | -0.027 | True |
| dom | d75s2a | meta-llama/Llama-3.2-1B-Instruct | random | 4 | 3 | -3.333 | -0.010 | True |
| dom | d75s2a | meta-llama/Llama-3.2-1B-Instruct | random | 5 | 3 | 3.000 | -0.051 | True |
| dom | d75s2a | meta-llama/Llama-3.2-1B-Instruct | targeted | 0 | 3 | -0.667 | 0.003 | True |
| dom | d75s3a | meta-llama/Llama-3.2-1B-Instruct | global | 0 | 22 | 3.955 | — |  |
| dom | d75s3a | meta-llama/Llama-3.2-1B-Instruct | random | 1 | 3 | -5.000 | -0.009 | True |
| dom | d75s3a | meta-llama/Llama-3.2-1B-Instruct | random | 2 | 3 | 10.000 | -0.129 | True |
| dom | d75s3a | meta-llama/Llama-3.2-1B-Instruct | random | 3 | 3 | -5.000 | 0.013 | True |
| dom | d75s3a | meta-llama/Llama-3.2-1B-Instruct | random | 4 | 3 | -4.667 | 0.007 | True |
| dom | d75s3a | meta-llama/Llama-3.2-1B-Instruct | random | 5 | 3 | 4.333 | -0.042 | True |
| dom | d75s3a | meta-llama/Llama-3.2-1B-Instruct | targeted | 0 | 3 | 0.667 | -0.006 | True |

## Arm B hurdle

| family | lexicon | model | reach | rev | valid | acc | n_sites |
|---|---|---|---|---|---|---|---|
| blk | d25s3 | Qwen/Qwen2.5-72B-Instruct | 0.323 | 0.169 | 0.338 | 0.162 | 220 |
| blk | d50s3 | Qwen/Qwen2.5-72B-Instruct | 0.640 | 0.052 | 0.750 | 0.408 | 272 |
| blk | d75s1a | Qwen/Qwen2.5-72B-Instruct | 0.191 | 0.246 | 0.550 | 0.113 | 341 |
| blk | d75s2a | Qwen/Qwen2.5-72B-Instruct | 0.173 | 0.237 | 0.750 | 0.138 | 341 |
| blk | d75s3a | Qwen/Qwen2.5-72B-Instruct | 0.150 | 0.392 | 0.338 | 0.025 | 341 |
| dom | d25s3 | Qwen/Qwen2.5-72B-Instruct | 0.586 | 0.047 | 0.973 | 0.459 | 220 |
| dom | d50s3 | Qwen/Qwen2.5-72B-Instruct | 0.287 | 0.244 | 0.947 | 0.250 | 272 |
| dom | d75s1a | Qwen/Qwen2.5-72B-Instruct | 0.270 | 0.141 | 0.588 | 0.275 | 341 |
| dom | d75s2a | Qwen/Qwen2.5-72B-Instruct | 0.270 | 0.272 | 0.875 | 0.138 | 341 |
| dom | d75s3a | Qwen/Qwen2.5-72B-Instruct | 0.311 | 0.104 | 0.975 | 0.263 | 341 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.055 | 0.083 | 0.203 | 0.041 | 220 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.066 | 0.056 | 0.368 | 0.053 | 272 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.018 | 0.333 | 0.237 | 0.013 | 341 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.018 | 0.167 | 0.338 | 0.025 | 341 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.012 | 0.750 | 0.350 | 0.000 | 341 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.064 | 0.143 | 0.378 | 0.054 | 220 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.022 | 0.167 | 0.329 | 0.000 | 272 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.023 | 0.250 | 0.412 | 0.013 | 341 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.023 | 0.375 | 0.625 | 0.000 | 341 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.023 | 0.250 | 0.575 | 0.025 | 341 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.159 | 0.171 | 0.446 | 0.081 | 220 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.136 | 0.135 | 0.395 | 0.105 | 272 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.026 | 0.333 | 0.512 | 0.037 | 341 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.067 | 0.261 | 0.625 | 0.013 | 341 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.023 | 0.500 | 0.212 | 0.013 | 341 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.168 | 0.270 | 0.568 | 0.095 | 220 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.070 | 0.211 | 0.711 | 0.013 | 272 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.038 | 0.308 | 0.400 | 0.037 | 341 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.053 | 0.278 | 0.300 | 0.013 | 341 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.032 | 0.273 | 0.312 | 0.025 | 341 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | 0.305 | 0.239 | 0.649 | 0.270 | 220 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | 0.423 | 0.113 | 0.974 | 0.342 | 272 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | 0.097 | 0.424 | 0.713 | 0.050 | 341 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | 0.164 | 0.143 | 0.787 | 0.125 | 341 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | 0.067 | 0.391 | 0.412 | 0.025 | 341 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | 0.377 | 0.217 | 0.973 | 0.230 | 220 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | 0.176 | 0.229 | 0.934 | 0.079 | 272 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | 0.167 | 0.140 | 0.575 | 0.150 | 341 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | 0.164 | 0.321 | 0.950 | 0.087 | 341 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | 0.196 | 0.164 | 0.963 | 0.188 | 341 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | 0.255 | 0.304 | 0.622 | 0.203 | 220 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | 0.327 | 0.101 | 0.987 | 0.289 | 272 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | 0.109 | 0.324 | 0.662 | 0.100 | 341 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | 0.173 | 0.186 | 0.675 | 0.138 | 341 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | 0.065 | 0.409 | 0.312 | 0.025 | 341 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | 0.391 | 0.186 | 0.851 | 0.216 | 220 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | 0.265 | 0.194 | 0.974 | 0.092 | 272 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | 0.232 | 0.139 | 0.438 | 0.200 | 341 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | 0.135 | 0.304 | 0.725 | 0.075 | 341 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | 0.211 | 0.194 | 0.925 | 0.188 | 341 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | 0.155 | 0.235 | 0.459 | 0.162 | 220 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | 0.287 | 0.128 | 0.789 | 0.184 | 272 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | 0.059 | 0.300 | 0.613 | 0.025 | 341 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | 0.129 | 0.318 | 0.762 | 0.050 | 341 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | 0.041 | 0.500 | 0.312 | 0.025 | 341 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | 0.241 | 0.208 | 0.676 | 0.149 | 220 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | 0.151 | 0.220 | 0.855 | 0.092 | 272 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | 0.164 | 0.125 | 0.475 | 0.125 | 341 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | 0.117 | 0.325 | 0.588 | 0.025 | 341 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | 0.082 | 0.214 | 0.688 | 0.075 | 341 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | 0.209 | 0.239 | 0.608 | 0.149 | 220 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | 0.246 | 0.104 | 0.961 | 0.211 | 272 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | 0.053 | 0.389 | 0.675 | 0.000 | 341 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | 0.106 | 0.250 | 0.850 | 0.062 | 341 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | 0.050 | 0.412 | 0.512 | 0.037 | 341 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | 0.268 | 0.153 | 0.662 | 0.189 | 220 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | 0.143 | 0.231 | 0.868 | 0.053 | 272 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | 0.135 | 0.196 | 0.463 | 0.087 | 341 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | 0.097 | 0.242 | 0.800 | 0.062 | 341 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | 0.129 | 0.159 | 0.900 | 0.087 | 341 |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | 0.141 | 0.032 | 0.378 | 0.149 | 220 |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | 0.074 | 0.150 | 0.711 | 0.053 | 272 |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | 0.029 | 0.300 | 0.425 | 0.013 | 341 |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | 0.026 | 0.111 | 0.688 | 0.037 | 341 |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | 0.041 | 0.429 | 0.325 | 0.000 | 341 |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | 0.150 | 0.212 | 0.568 | 0.122 | 220 |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | 0.048 | 0.231 | 0.539 | 0.026 | 272 |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | 0.041 | 0.214 | 0.512 | 0.037 | 341 |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | 0.070 | 0.333 | 0.600 | 0.025 | 341 |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | 0.079 | 0.222 | 0.800 | 0.050 | 341 |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | 0.245 | 0.185 | 0.716 | 0.203 | 220 |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | 0.390 | 0.132 | 0.895 | 0.276 | 272 |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | 0.065 | 0.364 | 0.650 | 0.025 | 341 |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | 0.132 | 0.311 | 0.875 | 0.062 | 341 |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | 0.067 | 0.391 | 0.438 | 0.025 | 341 |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | 0.309 | 0.132 | 0.919 | 0.243 | 220 |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | 0.143 | 0.256 | 0.947 | 0.053 | 272 |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | 0.176 | 0.083 | 0.662 | 0.175 | 341 |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | 0.185 | 0.222 | 0.775 | 0.062 | 341 |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | 0.111 | 0.184 | 0.875 | 0.100 | 341 |
| blk | d25s3 | meta-llama/Llama-3.2-1B-Instruct | 0.068 | 0.400 | 0.392 | 0.014 | 220 |
| blk | d50s3 | meta-llama/Llama-3.2-1B-Instruct | 0.121 | 0.121 | 0.276 | 0.026 | 272 |
| blk | d75s1a | meta-llama/Llama-3.2-1B-Instruct | 0.023 | 0.250 | 0.237 | 0.000 | 341 |
| blk | d75s2a | meta-llama/Llama-3.2-1B-Instruct | 0.029 | 0.100 | 0.362 | 0.025 | 341 |
| blk | d75s3a | meta-llama/Llama-3.2-1B-Instruct | 0.012 | 0.500 | 0.188 | 0.000 | 341 |
| dom | d25s3 | meta-llama/Llama-3.2-1B-Instruct | 0.082 | 0.222 | 0.392 | 0.054 | 220 |
| dom | d50s3 | meta-llama/Llama-3.2-1B-Instruct | 0.040 | 0.364 | 0.526 | 0.000 | 272 |
| dom | d75s1a | meta-llama/Llama-3.2-1B-Instruct | 0.038 | 0.231 | 0.550 | 0.013 | 341 |
| dom | d75s2a | meta-llama/Llama-3.2-1B-Instruct | 0.047 | 0.188 | 0.662 | 0.013 | 341 |
| dom | d75s3a | meta-llama/Llama-3.2-1B-Instruct | 0.029 | 0.200 | 0.662 | 0.025 | 341 |
