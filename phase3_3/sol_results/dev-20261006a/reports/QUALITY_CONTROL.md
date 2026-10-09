# Quality control — `dev-20261006a`

> **Run** `dev-20261006a` · **stage** DEVELOPMENT · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

## Arm A measurement health

| rows | ok | excluded | exact_zero_margins | ties | merged_share |
|---|---|---|---|---|---|
| 10224 | 10224 | 0 | 0 | 0 | 0.417 |

## Split and exclusion audit

| record_type | count |
|---|---|
| cell_class | 16 |
| dropped_site | 443 |
| structural_grid | 1 |

**Structurally empty cells** (the lexicon cannot test this stratum):

| family | lexicon | stratum | status |
|---|---|---|---|
| dom | d25s2 | sigil | STRUCTURALLY_EMPTY |

## Failed cells

_none_

## Demonstration leakage

Enforced, not merely checked: `score_primary_cell` raises if `demos.audit` finds any leak, so a completed ladder row is leak-free by construction.

## Extinction curve shape

| family | model | share_nonmonotone | share_recrossed_down | share_already_correct |
|---|---|---|---|---|
| dom | Qwen/Qwen2.5-Coder-0.5B | 0.985 | 0.4375 | 0.5775 |
| dom | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.985 | 0.3725 | 0.5625 |
| dom | Qwen/Qwen2.5-Coder-1.5B | 0.9725 | 0.305 | 0.4825 |
| dom | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.9825 | 0.3875 | 0.5475 |
