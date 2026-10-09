# Quality control — `heldout-20261007a`

> **Run** `heldout-20261007a` · **stage** HELD-OUT · **status** COMPLETE
>
> Held-out evaluation under DEV_FREEZE; see criteria below. blk results are a WEAKER family test (deviation D1), never a held-out-grammar confirmation.

## Arm A measurement health

| rows | ok | excluded | exact_zero_margins | ties | merged_share |
|---|---|---|---|---|---|
| 190890 | 190890 | 0 | 0 | 0 | 0.437 |

## Split and exclusion audit

| record_type | count |
|---|---|
| cell_class | 210 |
| dropped_site | 1670 |

## Failed cells

_none_

## Demonstration leakage

Enforced, not merely checked: `score_primary_cell` raises if `demos.audit` finds any leak, so a completed ladder row is leak-free by construction.

## Extinction curve shape

| family | model | share_nonmonotone | share_recrossed_down | share_already_correct |
|---|---|---|---|---|
| blk | Qwen/Qwen2.5-72B | 0.97561 | 0.395122 | 0.546341 |
| dom | Qwen/Qwen2.5-72B | 0.979487 | 0.441026 | 0.574359 |
| blk | Qwen/Qwen2.5-72B-Instruct | 0.985366 | 0.395122 | 0.526829 |
| dom | Qwen/Qwen2.5-72B-Instruct | 0.953846 | 0.410256 | 0.54359 |
| blk | Qwen/Qwen2.5-Coder-0.5B | 0.970732 | 0.331707 | 0.443902 |
| dom | Qwen/Qwen2.5-Coder-0.5B | 0.958974 | 0.338462 | 0.466667 |
| blk | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.980488 | 0.321951 | 0.502439 |
| dom | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.984615 | 0.348718 | 0.548718 |
| blk | Qwen/Qwen2.5-Coder-1.5B | 0.936585 | 0.341463 | 0.463415 |
| dom | Qwen/Qwen2.5-Coder-1.5B | 0.938462 | 0.317949 | 0.487179 |
| blk | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.960976 | 0.321951 | 0.497561 |
| dom | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.94359 | 0.420513 | 0.553846 |
| blk | Qwen/Qwen2.5-Coder-14B | 0.980488 | 0.439024 | 0.507317 |
| dom | Qwen/Qwen2.5-Coder-14B | 0.984615 | 0.533333 | 0.533333 |
| blk | Qwen/Qwen2.5-Coder-14B-Instruct | 0.995122 | 0.468293 | 0.502439 |
| dom | Qwen/Qwen2.5-Coder-14B-Instruct | 0.974359 | 0.405128 | 0.430769 |
| blk | Qwen/Qwen2.5-Coder-32B | 0.97561 | 0.443902 | 0.478049 |
| dom | Qwen/Qwen2.5-Coder-32B | 0.964103 | 0.441026 | 0.512821 |
| blk | Qwen/Qwen2.5-Coder-32B-Instruct | 0.980488 | 0.458537 | 0.580488 |
| dom | Qwen/Qwen2.5-Coder-32B-Instruct | 0.979487 | 0.435897 | 0.558974 |
| blk | Qwen/Qwen2.5-Coder-3B | 0.956098 | 0.341463 | 0.478049 |
| dom | Qwen/Qwen2.5-Coder-3B | 0.974359 | 0.364103 | 0.492308 |
| blk | Qwen/Qwen2.5-Coder-3B-Instruct | 0.941463 | 0.346341 | 0.453659 |
| dom | Qwen/Qwen2.5-Coder-3B-Instruct | 0.958974 | 0.369231 | 0.492308 |
| blk | Qwen/Qwen2.5-Coder-7B | 0.965854 | 0.317073 | 0.492683 |
| dom | Qwen/Qwen2.5-Coder-7B | 0.984615 | 0.358974 | 0.471795 |
| blk | Qwen/Qwen2.5-Coder-7B-Instruct | 0.946341 | 0.312195 | 0.487805 |
| dom | Qwen/Qwen2.5-Coder-7B-Instruct | 0.928205 | 0.353846 | 0.410256 |
| blk | bigcode/starcoder2-3b | 0.990244 | 0.380488 | 0.468293 |
| dom | bigcode/starcoder2-3b | 0.989744 | 0.369231 | 0.441026 |
| blk | deepseek-ai/deepseek-coder-1.3b-base | 0.980488 | 0.44878 | 0.517073 |
| dom | deepseek-ai/deepseek-coder-1.3b-base | 0.969231 | 0.4 | 0.45641 |
| blk | deepseek-ai/deepseek-coder-1.3b-instruct | 0.970732 | 0.443902 | 0.468293 |
| dom | deepseek-ai/deepseek-coder-1.3b-instruct | 0.969231 | 0.405128 | 0.466667 |
| blk | deepseek-ai/deepseek-coder-33b-base | 0.97561 | 0.453659 | 0.55122 |
| dom | deepseek-ai/deepseek-coder-33b-base | 0.979487 | 0.528205 | 0.528205 |
| blk | deepseek-ai/deepseek-coder-33b-instruct | 0.970732 | 0.497561 | 0.521951 |
| dom | deepseek-ai/deepseek-coder-33b-instruct | 0.974359 | 0.482051 | 0.497436 |
| blk | meta-llama/Llama-3.2-1B | 0.97561 | 0.287805 | 0.385366 |
| dom | meta-llama/Llama-3.2-1B | 0.953846 | 0.333333 | 0.415385 |
| blk | meta-llama/Llama-3.2-1B-Instruct | 0.980488 | 0.419512 | 0.502439 |
| dom | meta-llama/Llama-3.2-1B-Instruct | 0.974359 | 0.384615 | 0.476923 |
