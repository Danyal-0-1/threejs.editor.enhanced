# Quality control — `smoke-20261006a`

> **Run** `smoke-20261006a` · **stage** SMOKE (development cell) · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

## Arm A measurement health

| rows | ok | excluded | exact_zero_margins | ties | merged_share |
|---|---|---|---|---|---|
| 36 | 36 | 0 | 0 | 0 | 0.167 |

## Split and exclusion audit

| record_type | count |
|---|---|
| cell_class | 1 |
| dropped_site | 144 |

## Failed cells

_none_

## Demonstration leakage

Enforced, not merely checked: `score_primary_cell` raises if `demos.audit` finds any leak, so a completed ladder row is leak-free by construction.

## Extinction curve shape

| family | model | share_nonmonotone | share_recrossed_down | share_already_correct |
|---|---|---|---|---|
| dom | Qwen/Qwen2.5-Coder-0.5B | 0.833333 | 0.333333 | 0.5 |
