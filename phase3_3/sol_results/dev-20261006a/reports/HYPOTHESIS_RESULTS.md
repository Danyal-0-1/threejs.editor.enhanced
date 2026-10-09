# Hypothesis results — `dev-20261006a`

> **Run** `dev-20261006a` · **stage** DEVELOPMENT · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

| hypothesis | status in this run |
|---|---|
| H1 familiar beats unfamiliar | established in prior literature; not a contribution and not retested |
| H2 prior × context | **NOT TESTABLE** — no calibrated prior-strength (T) or local-context (A) levels exist; deriving them from outcome margins would be circular (review section 6.3) |
| H4 exact-site prediction | see criteria below (DEVELOPMENT — not confirmatory) |
| H5 targeted repair | NOT RUN |
| Arm B generation | NOT RUN |

## H4 criteria

| pair | family | split | criterion | status | delta | ci_lo | ci_hi | p_holm | detail |
|---|---|---|---|---|---|---|---|---|---|
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | dom | DEVELOPMENT | C1_delta_vs_identity | MET | 0.368765 | 0.333741 | 0.403106 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | dom | DEVELOPMENT | C2_delta_vs_length | MET | 0.324527 | 0.247298 | 0.396503 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-0.5B/Qwen/Qwen2.5-Coder-0.5B-Instruct | dom | DEVELOPMENT | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | dom | DEVELOPMENT | C1_delta_vs_identity | MET | 0.434909 | 0.412761 | 0.455431 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | dom | DEVELOPMENT | C2_delta_vs_length | MET | 0.44884 | 0.390527 | 0.513277 | 0.0009995 |  |
| Qwen/Qwen2.5-Coder-1.5B/Qwen/Qwen2.5-Coder-1.5B-Instruct | dom | DEVELOPMENT | C3_auroc_heldout_grammar | NOT TESTABLE |  |  |  |  | no valid held-out grammar family exists: blk was scored before the freeze (deviation D1) |

Criterion 1's identity baseline is CONSTANT on the SEMANTIC-only eligible set (AUROC exactly 0.5), so C1 is equivalent to AUROC ≥ 0.60 with an interval above 0.5 (deviation D6). The exploratory `terminal_rate` baseline is the stronger 'language-identity' competitor.
