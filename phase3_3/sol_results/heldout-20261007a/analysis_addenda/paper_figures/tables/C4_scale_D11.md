# Table C4. Scale (D10, specified by D11): OLS slopes across the Qwen2.5-Coder ladder, 0.5B–32B

From analysis_addenda/d11_scale/. Template-cluster bootstrap, B = 2000; a p of 0 is reported as < 1/B. Holm over the six slopes. Sizes are not randomized: associations.

| grammar | outcome | models | slope per 10x parameters | 95% CI | p (two-sided) | Holm p |
|---|---|---|---|---|---|---|
| dom | reversion rate | base | -0.0011 | [-0.0256, +0.0232] | 0.962 | 1.000 |
| dom | reversion rate | instruct | -0.0135 | [-0.0441, +0.0165] | 0.361 | 1.000 |
| dom | H4 AUROC | pair | -0.0814 | [-0.1106, -0.0499] | < 0.0005 | < 0.003 |
| blk | reversion rate | base | +0.0325 | [+0.0046, +0.0600] | 0.018 | 0.072 |
| blk | reversion rate | instruct | -0.0130 | [-0.0444, +0.0167] | 0.391 | 1.000 |
| blk | H4 AUROC | pair | -0.0365 | [-0.0657, -0.0089] | 0.011 | 0.055 |
