# Phase 4 fixes of the held-out run's open problems — `heldout-20261007a`

> **Post hoc.** Computed on 2026-10-22, after the held-out outcomes were known, outside the frozen code. Nothing here is confirmatory, and no registered verdict changes (deviation D13 in `phase3_2/PREREGISTRATION.md`). Made by `phase4/scripts/fix_heldout_problems.py`; the explanation is in `explanations/phase4/fixes_before_phase4/`.

## F1 — H4 calibration, out of sample

**Problem.** For the 8 pairs without frozen Platt parameters, the export fitted the calibration on the held-out rows themselves and then measured it there: in-sample, with a slope of exactly 1.00.

**Fix.** Two out-of-sample estimates per pair and grammar: (1) template-grouped 5-fold cross-fitting, where each site's probability comes from a Platt fit that never saw its template; (2) cross-family transfer, a Platt fit on the pair's other grammar family. Same ECE (10 bins), Brier and slope functions as the frozen code (`p33.h4`).

| pair | grammar | sites | export's source | export ECE | export slope | cross-fitted ECE | cross-fitted Brier | cross-fitted slope | cross-fitted intercept | other-grammar ECE | other-grammar slope |
|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek-coder-1.3b-base | dom | 1515 | in-sample (the gap) | 0.054 | 1.00 | 0.053 | 0.165 | 0.99 | +0.01 | 0.062 | 1.27 |
| deepseek-coder-1.3b-base | blk | 1515 | in-sample (the gap) | 0.074 | 1.00 | 0.070 | 0.187 | 0.98 | +0.01 | 0.083 | 0.78 |
| deepseek-coder-33b-base | dom | 1515 | in-sample (the gap) | 0.040 | 1.00 | 0.040 | 0.112 | 0.98 | +0.03 | 0.046 | 0.83 |
| deepseek-coder-33b-base | blk | 1515 | in-sample (the gap) | 0.022 | 1.00 | 0.017 | 0.094 | 0.99 | +0.00 | 0.034 | 1.20 |
| Llama-3.2-1B | dom | 1515 | in-sample (the gap) | 0.040 | 1.00 | 0.041 | 0.133 | 0.99 | +0.00 | 0.067 | 1.33 |
| Llama-3.2-1B | blk | 1515 | in-sample (the gap) | 0.033 | 1.00 | 0.035 | 0.165 | 0.98 | +0.01 | 0.066 | 0.75 |
| Qwen2.5-72B | dom | 1515 | in-sample (the gap) | 0.036 | 1.00 | 0.041 | 0.157 | 0.98 | +0.00 | 0.051 | 0.84 |
| Qwen2.5-72B | blk | 1515 | in-sample (the gap) | 0.017 | 1.00 | 0.016 | 0.150 | 0.98 | -0.00 | 0.036 | 1.19 |
| Qwen2.5-Coder-0.5B | dom | 1515 | frozen (development) | 0.047 | 1.08 | 0.046 | 0.135 | 0.98 | -0.00 | 0.043 | 1.29 |
| Qwen2.5-Coder-0.5B | blk | 1515 | frozen (development) | 0.051 | 0.84 | 0.040 | 0.165 | 0.99 | +0.00 | 0.055 | 0.77 |
| Qwen2.5-Coder-1.5B | dom | 1515 | frozen (development) | 0.036 | 1.18 | 0.030 | 0.074 | 0.98 | +0.01 | 0.059 | 1.43 |
| Qwen2.5-Coder-1.5B | blk | 1515 | frozen (development) | 0.052 | 0.83 | 0.024 | 0.114 | 0.98 | +0.01 | 0.052 | 0.70 |
| Qwen2.5-Coder-3B | dom | 1515 | in-sample (the gap) | 0.031 | 1.00 | 0.031 | 0.090 | 0.98 | +0.01 | 0.031 | 1.05 |
| Qwen2.5-Coder-3B | blk | 1515 | in-sample (the gap) | 0.026 | 1.00 | 0.030 | 0.101 | 0.99 | +0.01 | 0.026 | 0.95 |
| Qwen2.5-Coder-7B | dom | 1515 | in-sample (the gap) | 0.111 | 1.00 | 0.105 | 0.194 | 0.97 | +0.01 | 0.137 | 0.96 |
| Qwen2.5-Coder-7B | blk | 1515 | in-sample (the gap) | 0.095 | 1.00 | 0.089 | 0.195 | 0.99 | -0.00 | 0.105 | 1.04 |
| Qwen2.5-Coder-14B | dom | 1515 | in-sample (the gap) | 0.056 | 1.00 | 0.054 | 0.158 | 0.99 | +0.00 | 0.071 | 0.85 |
| Qwen2.5-Coder-14B | blk | 1515 | in-sample (the gap) | 0.038 | 1.00 | 0.036 | 0.145 | 0.99 | +0.00 | 0.058 | 1.18 |
| Qwen2.5-Coder-32B | dom | 1515 | in-sample (the gap) | 0.067 | 1.00 | 0.069 | 0.183 | 0.99 | +0.00 | 0.068 | 0.79 |
| Qwen2.5-Coder-32B | blk | 1515 | in-sample (the gap) | 0.038 | 1.00 | 0.033 | 0.179 | 0.99 | -0.00 | 0.063 | 1.27 |

**Result.** For the 8 pairs that had no frozen calibration, cross-fitted ECE is 0.016–0.105 with slopes 0.97–0.99, close to the export's in-sample ECE (0.017–0.111): with only two parameters, a Platt fit barely overfits, so a calibration learned on some templates of a pair transfers to its other templates. Fitted on the other grammar family instead, it transfers less well: ECE 0.026–0.137, slopes 0.75–1.33. This is a post-hoc statement about calibratability within a pair, not a registered transfer test: the registered calibration-transfer claim stays limited to the two frozen pairs.

## F2 — H5, the registered test (implemented post hoc)

**Problem.** The preregistration (§3) says: *H5 is supported iff error reduction per changed symbol exceeds the matched-budget random-rewrite control with an interval excluding 0, and reversion at low-risk control sites does not worsen by more than 0.02.* The frozen export reported each arm but never computed this test.

**Fix.** Exactly that test, computed now. Per cell (instruct model × lexicon): targeted minus the mean of the five random seeds, in reversions removed per changed symbol (the export's metric). Per grammar family: the mean over its 50 cells, with a 95% template-cluster bootstrap interval (B = 2000, the same template draw for every cell and arm). Control degradation is the targeted arm's change in reversion rate at the sites it did not repair. Families are never pooled; H5 would need support in both.

| grammar | cells | targeted − random, per changed symbol [95% CI] | control degradation, targeted [95% CI] | tolerance | H5 as registered | repaired-site part of the difference [95% CI] | control-site part [95% CI] |
|---|---|---|---|---|---|---|---|
| dom | 50 | -0.772 [-1.963, +0.401] | -0.058 [-0.072, -0.043] | ≤ 0.02 | NOT SUPPORTED | +0.793 [+0.061, +1.532] | -1.565 [-2.512, -0.649] |
| blk | 50 | -0.041 [-1.191, +1.117] | -0.053 [-0.071, -0.034] | ≤ 0.02 | NOT SUPPORTED | +2.205 [+1.388, +3.024] | -2.247 [-3.340, -1.228] |

**Result: H5 is NOT SUPPORTED by its own registered test**, in both grammar families. The verdict that was given descriptively (D12) stands, now with the registered interval. Per cell, the interval lies above 0 in 20 and below 0 in 18 of 100 cells (`F2_h5_by_cell.csv`). Per model and family, with Holm over the 20 tests:

| model | grammar | targeted − random per symbol [95% CI] | two-sided p | Holm p (20 tests) |
|---|---|---|---|---|
| Qwen2.5-72B-Instruct | dom | -2.28 [-4.47, -0.32] | 0.027 | 0.338 |
| Qwen2.5-Coder-0.5B-Instruct | dom | +0.35 [-1.25, +1.96] | 0.722 | 1.000 |
| Qwen2.5-Coder-1.5B-Instruct | dom | -2.07 [-3.61, -0.45] | 0.009 | 0.153 |
| Qwen2.5-Coder-14B-Instruct | dom | -2.08 [-3.87, -0.23] | 0.026 | 0.338 |
| Qwen2.5-Coder-32B-Instruct | dom | -0.92 [-3.23, +1.33] | 0.415 | 1.000 |
| Qwen2.5-Coder-3B-Instruct | dom | -2.52 [-4.52, -0.52] | 0.009 | 0.153 |
| Qwen2.5-Coder-7B-Instruct | dom | -0.12 [-2.15, +2.11] | 0.868 | 1.000 |
| deepseek-coder-1.3b-instruct | dom | -1.76 [-3.44, -0.03] | 0.047 | 0.517 |
| deepseek-coder-33b-instruct | dom | +1.76 [-0.16, +3.77] | 0.078 | 0.780 |
| Llama-3.2-1B-Instruct | dom | +1.92 [+0.48, +3.40] | 0.016 | 0.224 |
| Qwen2.5-72B-Instruct | blk | -1.32 [-3.21, +0.51] | 0.154 | 1.000 |
| Qwen2.5-Coder-0.5B-Instruct | blk | +2.55 [+0.52, +4.59] | 0.012 | 0.180 |
| Qwen2.5-Coder-1.5B-Instruct | blk | +0.05 [-1.69, +1.77] | 0.968 | 1.000 |
| Qwen2.5-Coder-14B-Instruct | blk | -1.33 [-3.89, +1.04] | 0.304 | 1.000 |
| Qwen2.5-Coder-32B-Instruct | blk | +0.08 [-2.15, +2.35] | 0.961 | 1.000 |
| Qwen2.5-Coder-3B-Instruct | blk | -3.47 [-5.68, -1.45] | < 0.0005 | < 0.010 |
| Qwen2.5-Coder-7B-Instruct | blk | -2.68 [-4.57, -0.79] | 0.004 | 0.072 |
| deepseek-coder-1.3b-instruct | blk | +1.01 [-0.44, +2.53] | 0.178 | 1.000 |
| deepseek-coder-33b-instruct | blk | +0.64 [-1.29, +2.68] | 0.501 | 1.000 |
| Llama-3.2-1B-Instruct | blk | +4.05 [+2.19, +5.88] | < 0.0005 | < 0.010 |

## F4 — H5's metric, split into repaired and control sites

**Problem.** The registered metric counts the reversions removed at *every* site of a cell, so it mixes the sites whose spelling was repaired with the control sites, which change only because the prompt's table changed.

**Fix.** An exact split: reduction per changed symbol = repaired-site part + control-site part. The total is the registered metric, reproduced for every frozen arm row. The family table above already shows the split of the targeted − random difference; `F4_h5_repaired_control_split.csv` has it per cell and arm.

- `dom`: targeted − random = -0.772 per changed symbol; repaired-site part +0.793 [+0.061, +1.532]; control-site part -1.565 [-2.512, -0.649].
- `blk`: targeted − random = -0.041 per changed symbol; repaired-site part +2.205 [+1.388, +3.024]; control-site part -2.247 [-3.340, -1.228].

Reversion at the repaired sites themselves, pooled over models and lexicons (random: all five seeds):

| grammar | arm | repaired sites | reverting before → after | silent after |
|---|---|---|---|---|
| dom | targeted | 2133 | 70.9% → 70.5% | 67.7% |
| dom | random | 13200 | 50.5% → 54.6% | 49.4% |
| dom | global | 15150 | 47.4% → 15.3% | 0.0% |
| blk | targeted | 1955 | 74.2% → 66.5% | 62.8% |
| blk | random | 13200 | 49.5% → 56.3% | 50.2% |
| blk | global | 15150 | 48.1% → 15.7% | 0.0% |

**Reading.**

- **At the repaired sites, targeting beats random** in both families (intervals above 0). This is mostly because respelling random, low-risk roles makes their sites *worse* (`dom` 50.5% → 54.6%, `blk` 49.5% → 56.3%), while respelling the riskiest roles leaves them about as they were or improves them (`dom` 70.9% → 70.5%, `blk` 74.2% → 66.5%).
- **The registered difference is negative because of the control-site part**: under random repair, the sites that were *not* repaired improved more. The registered H5 verdict is therefore decided mainly by changes at sites that were not repaired. Why they change is not known: both the prompt's table and the earlier part of each program differ after a repair.
- **Silent errors stay** under targeted repair, because in a permuted language the old spelling of a repaired role is still another role's spelling; only global respelling removes them.
- This is post hoc. It generates a hypothesis for Phase 4 (a preregistered repaired-site metric); the registered verdict stands.

## F5 — Arm B, corrected extraction

**Problem.** The frozen extractor keeps the whole first line of the output. Some models continued the few-shot pattern on that same line (`<program> Request: <next request>`), so a correct program was scored as a parse failure.

**Fix.** The frozen extraction, then a cut at the first same-line `Request:`; the corrected program is re-evaluated with the frozen evaluator (`armb.evaluate`), and every site of each changed generation is re-observed with the frozen `armb.observe`.

| model | grammar | programs | correct, frozen | correct, corrected | parse failures, frozen → corrected |
|---|---|---|---|---|---|
| deepseek-coder-1.3b-instruct | blk | 390 | 19 (4.9%) | 19 (4.9%) | 193 → 193 |
| deepseek-coder-1.3b-instruct | dom | 390 | 20 (5.1%) | 20 (5.1%) | 154 → 154 |
| deepseek-coder-33b-instruct | blk | 390 | 45 (11.5%) | 45 (11.5%) | 112 → 112 |
| deepseek-coder-33b-instruct | dom | 390 | 49 (12.6%) | 49 (12.6%) | 65 → 65 |
| Llama-3.2-1B-Instruct | blk | 390 | 5 (1.3%) | 5 (1.3%) | 277 → 277 |
| Llama-3.2-1B-Instruct | dom | 390 | 8 (2.1%) | 8 (2.1%) | 171 → 171 |
| Qwen2.5-72B-Instruct | blk | 390 | 65 (16.7%) | 87 (22.3%) | 177 → 129 |
| Qwen2.5-72B-Instruct | dom | 390 | 107 (27.4%) | 110 (28.2%) | 51 → 47 |
| Qwen2.5-Coder-0.5B-Instruct | blk | 390 | 10 (2.6%) | 10 (2.6%) | 273 → 273 |
| Qwen2.5-Coder-0.5B-Instruct | dom | 390 | 7 (1.8%) | 7 (1.8%) | 208 → 208 |
| Qwen2.5-Coder-1.5B-Instruct | blk | 390 | 19 (4.9%) | 19 (4.9%) | 219 → 219 |
| Qwen2.5-Coder-1.5B-Instruct | dom | 390 | 14 (3.6%) | 14 (3.6%) | 213 → 213 |
| Qwen2.5-Coder-3B-Instruct | blk | 390 | 34 (8.7%) | 34 (8.7%) | 161 → 161 |
| Qwen2.5-Coder-3B-Instruct | dom | 390 | 36 (9.2%) | 36 (9.2%) | 135 → 135 |
| Qwen2.5-Coder-7B-Instruct | blk | 390 | 35 (9.0%) | 35 (9.0%) | 109 → 109 |
| Qwen2.5-Coder-7B-Instruct | dom | 390 | 37 (9.5%) | 37 (9.5%) | 102 → 102 |
| Qwen2.5-Coder-14B-Instruct | blk | 390 | 62 (15.9%) | 62 (15.9%) | 115 → 115 |
| Qwen2.5-Coder-14B-Instruct | dom | 390 | 57 (14.6%) | 57 (14.6%) | 48 → 48 |
| Qwen2.5-Coder-32B-Instruct | blk | 390 | 58 (14.9%) | 58 (14.9%) | 137 → 137 |
| Qwen2.5-Coder-32B-Instruct | dom | 390 | 60 (15.4%) | 62 (15.9%) | 86 → 80 |
| ALL | both | 7800 | 747 (9.6%) | 774 (9.9%) | 3006 → 2948 |

**Result.** 63 of 7800 generations change: PARSE_FAIL → PARSE_FAIL: 5; PARSE_FAIL → VALID_CORRECT: 27; PARSE_FAIL → VALID_WRONG: 31. Task accuracy goes from 9.6% to 9.9%. Reach and reversion given reach do not change (0 of 205 re-observed site outcomes differ), because the cut text lies after the program.

## F6 — H4 per role (open item from 06 §10)

**Question.** Is the H4 prediction carried by one kind of symbol (for example verbs)? The roles differ in how often they revert, so an AUROC pooled over roles could partly reflect those differences; inside one role they are gone. (Differences between the terminals of one role remain; the exploratory per-terminal `terminal_rate` baseline addresses those.)

| pair | grammar | role | sites | reversion prevalence | AUROC within the role [95% CI] |
|---|---|---|---|---|---|
| deepseek-coder-1.3b-base | dom | sigil | 755 | 0.596 | 0.813 [0.751, 0.874] |
| deepseek-coder-1.3b-base | dom | keyword | 273 | 0.421 | 0.876 [0.814, 0.929] |
| deepseek-coder-1.3b-base | dom | verb | 487 | 0.388 | 0.848 [0.813, 0.883] |
| deepseek-coder-1.3b-base | blk | sigil | 755 | 0.567 | 0.715 [0.642, 0.792] |
| deepseek-coder-1.3b-base | blk | keyword | 273 | 0.495 | 0.758 [0.673, 0.830] |
| deepseek-coder-1.3b-base | blk | verb | 487 | 0.489 | 0.866 [0.829, 0.899] |
| deepseek-coder-33b-base | dom | sigil | 755 | 0.611 | 0.882 [0.835, 0.928] |
| deepseek-coder-33b-base | dom | keyword | 273 | 0.447 | 0.935 [0.897, 0.966] |
| deepseek-coder-33b-base | dom | verb | 487 | 0.429 | 0.966 [0.950, 0.980] |
| deepseek-coder-33b-base | blk | sigil | 755 | 0.584 | 0.940 [0.912, 0.964] |
| deepseek-coder-33b-base | blk | keyword | 273 | 0.451 | 0.947 [0.918, 0.971] |
| deepseek-coder-33b-base | blk | verb | 487 | 0.415 | 0.953 [0.938, 0.967] |
| Llama-3.2-1B | dom | sigil | 755 | 0.468 | 0.984 [0.971, 0.994] |
| Llama-3.2-1B | dom | keyword | 273 | 0.535 | 0.741 [0.638, 0.828] |
| Llama-3.2-1B | dom | verb | 487 | 0.470 | 0.846 [0.800, 0.887] |
| Llama-3.2-1B | blk | sigil | 755 | 0.491 | 0.889 [0.848, 0.927] |
| Llama-3.2-1B | blk | keyword | 273 | 0.476 | 0.721 [0.622, 0.810] |
| Llama-3.2-1B | blk | verb | 487 | 0.526 | 0.835 [0.791, 0.879] |
| Qwen2.5-72B | dom | sigil | 755 | 0.485 | 0.839 [0.782, 0.889] |
| Qwen2.5-72B | dom | keyword | 273 | 0.564 | 0.895 [0.829, 0.954] |
| Qwen2.5-72B | dom | verb | 487 | 0.417 | 0.875 [0.847, 0.903] |
| Qwen2.5-72B | blk | sigil | 755 | 0.400 | 0.811 [0.755, 0.862] |
| Qwen2.5-72B | blk | keyword | 273 | 0.571 | 0.873 [0.802, 0.931] |
| Qwen2.5-72B | blk | verb | 487 | 0.454 | 0.940 [0.912, 0.965] |
| Qwen2.5-Coder-0.5B | dom | sigil | 755 | 0.377 | 0.939 [0.895, 0.971] |
| Qwen2.5-Coder-0.5B | dom | keyword | 273 | 0.535 | 0.730 [0.645, 0.803] |
| Qwen2.5-Coder-0.5B | dom | verb | 487 | 0.499 | 0.901 [0.869, 0.930] |
| Qwen2.5-Coder-0.5B | blk | sigil | 755 | 0.384 | 0.865 [0.803, 0.913] |
| Qwen2.5-Coder-0.5B | blk | keyword | 273 | 0.531 | 0.738 [0.648, 0.812] |
| Qwen2.5-Coder-0.5B | blk | verb | 487 | 0.478 | 0.856 [0.820, 0.890] |
| Qwen2.5-Coder-1.5B | dom | sigil | 755 | 0.481 | 0.981 [0.962, 0.992] |
| Qwen2.5-Coder-1.5B | dom | keyword | 273 | 0.520 | 0.975 [0.948, 0.991] |
| Qwen2.5-Coder-1.5B | dom | verb | 487 | 0.400 | 0.931 [0.905, 0.957] |
| Qwen2.5-Coder-1.5B | blk | sigil | 755 | 0.566 | 0.917 [0.878, 0.949] |
| Qwen2.5-Coder-1.5B | blk | keyword | 273 | 0.502 | 0.953 [0.908, 0.982] |
| Qwen2.5-Coder-1.5B | blk | verb | 487 | 0.464 | 0.915 [0.888, 0.939] |
| Qwen2.5-Coder-3B | dom | sigil | 755 | 0.518 | 0.945 [0.916, 0.968] |
| Qwen2.5-Coder-3B | dom | keyword | 273 | 0.454 | 0.969 [0.936, 0.989] |
| Qwen2.5-Coder-3B | dom | verb | 487 | 0.419 | 0.944 [0.919, 0.966] |
| Qwen2.5-Coder-3B | blk | sigil | 755 | 0.543 | 0.934 [0.900, 0.962] |
| Qwen2.5-Coder-3B | blk | keyword | 273 | 0.436 | 0.964 [0.932, 0.984] |
| Qwen2.5-Coder-3B | blk | verb | 487 | 0.437 | 0.933 [0.906, 0.957] |
| Qwen2.5-Coder-7B | dom | sigil | 755 | 0.523 | 0.635 [0.559, 0.707] |
| Qwen2.5-Coder-7B | dom | keyword | 273 | 0.630 | 0.847 [0.755, 0.925] |
| Qwen2.5-Coder-7B | dom | verb | 487 | 0.452 | 0.882 [0.853, 0.909] |
| Qwen2.5-Coder-7B | blk | sigil | 755 | 0.499 | 0.636 [0.550, 0.716] |
| Qwen2.5-Coder-7B | blk | keyword | 273 | 0.604 | 0.908 [0.852, 0.953] |
| Qwen2.5-Coder-7B | blk | verb | 487 | 0.384 | 0.830 [0.787, 0.870] |
| Qwen2.5-Coder-14B | dom | sigil | 755 | 0.485 | 0.840 [0.781, 0.893] |
| Qwen2.5-Coder-14B | dom | keyword | 273 | 0.509 | 0.878 [0.815, 0.940] |
| Qwen2.5-Coder-14B | dom | verb | 487 | 0.390 | 0.876 [0.841, 0.911] |
| Qwen2.5-Coder-14B | blk | sigil | 755 | 0.441 | 0.862 [0.803, 0.913] |
| Qwen2.5-Coder-14B | blk | keyword | 273 | 0.484 | 0.894 [0.836, 0.943] |
| Qwen2.5-Coder-14B | blk | verb | 487 | 0.402 | 0.889 [0.858, 0.918] |
| Qwen2.5-Coder-32B | dom | sigil | 755 | 0.417 | 0.809 [0.745, 0.870] |
| Qwen2.5-Coder-32B | dom | keyword | 273 | 0.440 | 0.661 [0.530, 0.778] |
| Qwen2.5-Coder-32B | dom | verb | 487 | 0.351 | 0.801 [0.755, 0.847] |
| Qwen2.5-Coder-32B | blk | sigil | 755 | 0.490 | 0.828 [0.743, 0.897] |
| Qwen2.5-Coder-32B | blk | keyword | 273 | 0.469 | 0.697 [0.582, 0.799] |
| Qwen2.5-Coder-32B | blk | verb | 487 | 0.390 | 0.805 [0.755, 0.851] |

**Result.** sigil: AUROC 0.63–0.98 (median 0.86); keyword: AUROC 0.66–0.98 (median 0.88); verb: AUROC 0.80–0.97 (median 0.88). The interval lies above 0.5 in 60 of 60 pair × grammar × role groups: the prediction holds inside every role, not only across roles.

## Checks (all passed; the script refuses otherwise)

- F1: the export's ECE, Brier, calibration slope and intercept are reproduced exactly for all 20 pair × grammar groups
- F2/F4: every one of the 700 frozen H5 arm rows (counts, per-symbol reduction, control degradation) is reproduced exactly from merged/h5.jsonl and Arm A
- F4: the split is exact by construction (repaired part + control part = the registered metric, which is itself reproduced above for every frozen arm row); computed for all 100 cells
- F5: the frozen extraction and bucket are reproduced exactly for all 7800 generations
- F5: re-observing the 205 sites of the 63 changed generations gives 0 changed site outcomes (reach and reversion given reach are unaffected)
- F6: all 60 per-role AUROCs equal the frozen p33.h4.auroc

## Provenance

- script `phase4/scripts/fix_heldout_problems.py`, sha256 `4b249d0a9d2a6687…`
- frozen analysis `DEV_FREEZE.json` sha256 `b319c3fcba3dd325…`
- intervals: template-cluster bootstrap, B = 2000, seed 20261002, streams `<grammar>/phase4/{h5_registered, h4_per_role}`; calibration folds `<grammar>/phase4/calibration_folds` (5 folds)
- `csv/h4_predictions.csv` sha256 `acbd8d0c6b207ffc…`
- `csv/h4_metrics_baselines_calibration.csv` sha256 `5c3b0c8cf7af8302…`
- `csv/arm_a_long.csv` sha256 `2d1ef380b2384dee…`
- `csv/h5_budget_outcomes.csv` sha256 `c0fc7031697d60f4…`
- `csv/arm_b_generations.csv` sha256 `ad697518d561db06…`
- `merged/h5.jsonl` sha256 `6bcf7583f922fbb1…`
