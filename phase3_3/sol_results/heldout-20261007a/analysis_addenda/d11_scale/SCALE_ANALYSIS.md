# Scale analysis (D10, specified by D11) — `heldout-20261007a`

- computed 2026-10-09T18:20:43+00:00 from the frozen export's CSVs (no re-scoring)
- ladder: Qwen2.5-Coder 0.5B, 1.5B, 3B, 7B, 14B, 32B; x = log10(parameters, billions)
- two-sided, no predicted direction; templates resampled within each family; Holm over every slope below
- size is not randomized: the ladder holds the tokenizer and training recipe fixed, but sizes may differ in other ways, so a trend is an association
- `blk` cells are HELDOUT-WEAK-FAMILY (D1); the 3B pair is HELDOUT-WEAKENED (D2)

| family | outcome | models | slope per 10x size | 95% CI | p (two-sided) | p (Holm) |
|---|---|---|---:|---|---:|---:|
| blk | reversion | base | +0.0325 | [+0.0046, +0.0600] | 0.0180 | 0.0720 |
| blk | reversion | instruct | -0.0130 | [-0.0444, +0.0167] | 0.3910 | 1.0000 |
| blk | h4_auroc | pair | -0.0365 | [-0.0657, -0.0089] | 0.0110 | 0.0550 |
| dom | reversion | base | -0.0011 | [-0.0256, +0.0232] | 0.9620 | 1.0000 |
| dom | reversion | instruct | -0.0135 | [-0.0441, +0.0165] | 0.3610 | 1.0000 |
| dom | h4_auroc | pair | -0.0814 | [-0.1106, -0.0499] | < 0.0005 | < 0.0030 |

## Per size

| family | outcome | models | 0.5B | 1.5B | 3B | 7B | 14B | 32B |
|---|---|---|---|---|---|---|---|---|
| blk | reversion | base | 0.438 [0.398, 0.478] | 0.509 [0.461, 0.556] | 0.508 [0.459, 0.559] | 0.546 [0.501, 0.590] | 0.492 [0.453, 0.531] | 0.514 [0.463, 0.567] |
| blk | reversion | instruct | 0.441 [0.405, 0.479] | 0.521 [0.469, 0.572] | 0.490 [0.439, 0.539] | 0.481 [0.433, 0.530] | 0.436 [0.385, 0.485] | 0.454 [0.403, 0.503] |
| blk | h4_auroc | pair | 0.836 [0.800, 0.869] | 0.920 [0.899, 0.939] | 0.939 [0.920, 0.956] | 0.759 [0.714, 0.803] | 0.875 [0.844, 0.902] | 0.805 [0.759, 0.844] |
| dom | reversion | base | 0.455 [0.415, 0.495] | 0.498 [0.453, 0.545] | 0.481 [0.437, 0.521] | 0.508 [0.467, 0.549] | 0.465 [0.427, 0.507] | 0.462 [0.425, 0.499] |
| dom | reversion | instruct | 0.445 [0.412, 0.478] | 0.462 [0.417, 0.508] | 0.475 [0.427, 0.523] | 0.519 [0.473, 0.567] | 0.459 [0.420, 0.498] | 0.400 [0.353, 0.444] |
| dom | h4_auroc | pair | 0.888 [0.861, 0.911] | 0.963 [0.948, 0.975] | 0.949 [0.933, 0.964] | 0.760 [0.719, 0.801] | 0.852 [0.822, 0.883] | 0.786 [0.743, 0.824] |

Inputs and their hashes: `inputs.json`.
