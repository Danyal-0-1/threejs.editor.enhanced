# Quality control — `dev-20261023a`

> **Run** `dev-20261023a` · **stage** DEVELOPMENT · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

## Arm A measurement health

| rows | ok | excluded | exact_zero_margins | ties | merged_share |
|---|---|---|---|---|---|
| 81810 | 81810 | 0 | 778 | 778 | 0.460 |

## Split and exclusion audit

| record_type | count |
|---|---|
| cell_class | 90 |
| dropped_site | 1670 |

## Failed cells

_none_

## Demonstration leakage

Enforced, not merely checked: `score_primary_cell` raises if `demos.audit` finds any leak, so a completed ladder row is leak-free by construction.

## Extinction curve shape

| family | model | share_nonmonotone | share_recrossed_down | share_already_correct |
|---|---|---|---|---|
| blk | asu-rc/deepseek-v4-1-flash | 0.985366 | 0.404878 | 0.531707 |
| dom | asu-rc/deepseek-v4-1-flash | 0.979487 | 0.425641 | 0.54359 |
| blk | asu-rc/gemma4-31b-it | 0.985366 | 0.463415 | 0.492683 |
| dom | asu-rc/gemma4-31b-it | 0.984615 | 0.441026 | 0.441026 |
| blk | asu-rc/olmo3-32b-instruct | 0.980488 | 0.37561 | 0.507317 |
| dom | asu-rc/olmo3-32b-instruct | 1 | 0.476923 | 0.564103 |
| blk | asu-rc/olmo3-32b-think | 0.985366 | 0.331707 | 0.526829 |
| dom | asu-rc/olmo3-32b-think | 0.989744 | 0.4 | 0.523077 |
| blk | asu-rc/olmo3-7b-instruct | 0.995122 | 0.42439 | 0.502439 |
| dom | asu-rc/olmo3-7b-instruct | 0.994872 | 0.302564 | 0.538462 |
| blk | asu-rc/qwen3-coder-30b-a3b-instruct | 0.980488 | 0.429268 | 0.55122 |
| dom | asu-rc/qwen3-coder-30b-a3b-instruct | 0.964103 | 0.435897 | 0.492308 |
| blk | asu-rc/qwen35-122b-a10b | 0.985366 | 0.404878 | 0.570732 |
| dom | asu-rc/qwen35-122b-a10b | 0.964103 | 0.379487 | 0.615385 |
| blk | asu-rc/qwen35-27b | 0.980488 | 0.487805 | 0.595122 |
| dom | asu-rc/qwen35-27b | 0.969231 | 0.528205 | 0.630769 |
| blk | asu-rc/qwen35-397b-a17b | 0.980488 | 0.409756 | 0.57561 |
| dom | asu-rc/qwen35-397b-a17b | 0.964103 | 0.446154 | 0.6 |
