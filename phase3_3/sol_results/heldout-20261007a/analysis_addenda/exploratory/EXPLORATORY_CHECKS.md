# Exploratory checks — `heldout-20261007a`

> **EXPLORATORY, post hoc.** Run on 2026-10-09 after the held-out results were seen, to decide how strongly the paper may word its claims. Not preregistered; no registered verdict changes. Made by `phase3_2/sol/scripts/exploratory_checks.py`.

## 1. Is the failure pattern inherited from the model's own base?

AUROC of the base-model risk −M(base, rule) for the instruct model's reversions (M < 0), on the same held-out sites as H4. *Own base* is the registered H4 pair (it reproduces the frozen H4 AUROC exactly). *Other lineages* are base models from other organisations (Qwen2.5 and Qwen2.5-Coder count as one lineage). *Consensus* averages the margins of every other-lineage base at each site: a pure "site difficulty" predictor that knows nothing about the instruct model's own history. The last column is (consensus − 0.5) / (own − 0.5).

| grammar | instruct model | own base | same lineage, other sizes (mean) | other lineages (mean) | other lineages (best) | other-lineage consensus | own − consensus [95% CI] | share of own signal reached by consensus |
|---|---|---|---|---|---|---|---|---|
| dom | deepseek-coder-1.3b-instruct | 0.841 | 0.733 | 0.620 | 0.689 (starcoder2-3b) | 0.665 | +0.177 [+0.134, +0.220] | 48% |
| dom | deepseek-coder-33b-instruct | 0.926 | 0.632 | 0.572 | 0.744 (starcoder2-3b) | 0.585 | +0.341 [+0.289, +0.393] | 20% |
| dom | Llama-3.2-1B-Instruct | 0.893 | — | 0.685 | 0.838 (Qwen2.5-Coder-0.5B) | 0.772 | +0.121 [+0.093, +0.152] | 69% |
| dom | Qwen2.5-Coder-0.5B-Instruct | 0.888 | 0.717 | 0.679 | 0.879 (Llama-3.2-1B) | 0.757 | +0.131 [+0.095, +0.170] | 66% |
| dom | Qwen2.5-Coder-1.5B-Instruct | 0.963 | 0.810 | 0.709 | 0.785 (Llama-3.2-1B) | 0.763 | +0.200 [+0.148, +0.251] | 57% |
| dom | Qwen2.5-Coder-3B-Instruct | 0.949 | 0.773 | 0.722 | 0.806 (starcoder2-3b) | 0.778 | +0.171 [+0.133, +0.210] | 62% |
| dom | Qwen2.5-Coder-7B-Instruct | 0.760 | 0.661 | 0.592 | 0.730 (starcoder2-3b) | 0.616 | +0.144 [+0.090, +0.200] | 45% |
| dom | Qwen2.5-Coder-14B-Instruct | 0.852 | 0.684 | 0.625 | 0.786 (starcoder2-3b) | 0.664 | +0.188 [+0.139, +0.238] | 47% |
| dom | Qwen2.5-Coder-32B-Instruct | 0.786 | 0.689 | 0.569 | 0.705 (starcoder2-3b) | 0.561 | +0.225 [+0.175, +0.275] | 21% |
| dom | Qwen2.5-72B-Instruct | 0.854 | 0.628 | 0.612 | 0.639 (starcoder2-3b) | 0.645 | +0.209 [+0.168, +0.253] | 41% |
| blk | deepseek-coder-1.3b-instruct | 0.788 | 0.675 | 0.543 | 0.646 (starcoder2-3b) | 0.563 | +0.225 [+0.179, +0.274] | 22% |
| blk | deepseek-coder-33b-instruct | 0.946 | 0.665 | 0.605 | 0.729 (starcoder2-3b) | 0.635 | +0.311 [+0.259, +0.361] | 30% |
| blk | Llama-3.2-1B-Instruct | 0.840 | — | 0.640 | 0.746 (Qwen2.5-Coder-0.5B) | 0.722 | +0.118 [+0.082, +0.159] | 65% |
| blk | Qwen2.5-Coder-0.5B-Instruct | 0.836 | 0.667 | 0.646 | 0.829 (Llama-3.2-1B) | 0.717 | +0.119 [+0.084, +0.154] | 65% |
| blk | Qwen2.5-Coder-1.5B-Instruct | 0.920 | 0.733 | 0.655 | 0.689 (starcoder2-3b) | 0.697 | +0.223 [+0.174, +0.275] | 47% |
| blk | Qwen2.5-Coder-3B-Instruct | 0.939 | 0.734 | 0.663 | 0.713 (starcoder2-3b) | 0.708 | +0.232 [+0.200, +0.267] | 47% |
| blk | Qwen2.5-Coder-7B-Instruct | 0.759 | 0.663 | 0.538 | 0.629 (starcoder2-3b) | 0.544 | +0.214 [+0.158, +0.270] | 17% |
| blk | Qwen2.5-Coder-14B-Instruct | 0.875 | 0.669 | 0.563 | 0.602 (deepseek-coder-33b-base) | 0.601 | +0.274 [+0.219, +0.329] | 27% |
| blk | Qwen2.5-Coder-32B-Instruct | 0.805 | 0.623 | 0.475 | 0.581 (starcoder2-3b) | 0.451 | +0.354 [+0.305, +0.400] | -16% |
| blk | Qwen2.5-72B-Instruct | 0.866 | 0.633 | 0.558 | 0.590 (deepseek-coder-33b-base) | 0.590 | +0.276 [+0.212, +0.341] | 24% |

**Reading.** The own base beats the other-lineage consensus with an interval above zero in 20 of 20 instruct × grammar groups. The consensus reaches -16%–69% (median 46%) of the own base's signal above chance. So a large part of *where* models revert is shared site difficulty, which any base model reveals, and the remainder is specific to the model's own lineage.

## 2. Does the role ordering in generation match the margins?

Instruct models only (the Arm B models), on the extinction subset of sites. *Margins* = share of sites where the correct spelling loses (M < 0) with the token table and k leak-free worked examples. *Arm B* = share of reached sites where the generated program uses the old spelling, with the table and 4 worked examples.

| grammar | role | margins, 0 examples: M < 0 | margins, 4 examples: M < 0 | Arm B, 4 examples: old spelling given reached |
|---|---|---|---|---|
| dom | sigil | 0.514 [0.382, 0.655] (n=650) | 0.328 [0.188, 0.471] (n=650) | 0.113 [0.085, 0.143] (n=1083) |
| dom | keyword | 0.497 [0.425, 0.576] (n=650) | 0.395 [0.305, 0.487] (n=650) | 0.232 [0.182, 0.289] (n=427) |
| dom | verb | 0.495 [0.392, 0.598] (n=650) | 0.483 [0.394, 0.573] (n=650) | 0.294 [0.222, 0.366] (n=681) |
| blk | sigil | 0.486 [0.332, 0.644] (n=690) | 0.423 [0.293, 0.531] (n=690) | 0.090 [0.058, 0.129] (n=984) |
| blk | keyword | 0.496 [0.429, 0.566] (n=680) | 0.440 [0.356, 0.525] (n=680) | 0.176 [0.123, 0.236] (n=380) |
| blk | verb | 0.506 [0.410, 0.598] (n=680) | 0.493 [0.404, 0.582] (n=680) | 0.428 [0.345, 0.506] (n=549) |

**Orderings (most reversion first):**

- `dom`: margins at 0 examples sigil > keyword > verb; margins at 4 examples verb > keyword > sigil; Arm B verb > keyword > sigil.
- `blk`: margins at 0 examples verb > keyword > sigil; margins at 4 examples verb > keyword > sigil; Arm B verb > keyword > sigil.

**Reading.** Compare the orderings at the *same* number of examples. A mismatch between 0 and 4 examples means a role is often wrong at first but quickly fixed by examples (or the reverse).

## 3. Adaptation by remap density, role and model kind

Kaplan–Meier median number of worked examples before the first switch, pooled over models (sites wrong at 0 examples). Density has one lexicon each at 25% and 50%, so lexicon and density are confounded.

| grammar | cut | initially wrong sites | KM median examples | never switched |
|---|---|---|---|---|
| blk | density d25 | 437 | 10.19 | 27% |
| blk | density d50 | 434 | 5.80 | 19% |
| blk | density d75 | 1307 | 6.19 | 19% |
| dom | density d25 | 429 | 5.40 | 18% |
| dom | density d50 | 402 | 1.57 | 12% |
| dom | density d75 | 1244 | 2.15 | 17% |
| blk | role keyword | 709 | 9.02 | 17% |
| blk | role sigil | 736 | 3.21 | 10% |
| blk | role verb | 733 | 11.36 | 35% |
| dom | role keyword | 659 | 2.85 | 13% |
| dom | role sigil | 719 | 1.28 | 2% |
| dom | role verb | 697 | 6.57 | 34% |
| blk | base | 1162 | 5.78 | 20% |
| blk | instruct | 1016 | 7.23 | 21% |
| dom | base | 1096 | 2.37 | 16% |
| dom | instruct | 979 | 3.04 | 16% |

## 4. How big are the wobbles?

The frozen `nonmonotone` flag counts *any* decrease between consecutive rungs, however small, so on its own it overstates instability. Here: the share of curves (all sites, all models) with a decrease of more than 0.5 or 1 nat between consecutive rungs (1 nat = an odds factor of 2.7), and, for initially wrong sites that switched, how many fall back below zero later and how far (the lowest margin after the first switch).

| grammar | sites | any decrease (frozen flag) | a decrease > 0.5 nats | a decrease > 1 nat | switched sites that fall back below 0 | how far they fall: median [IQR], nats | fall below −0.5 nats |
|---|---|---|---|---|---|---|---|
| dom | 4095 | 96.8% | 81.0% | 57.6% | 552/1740 (31.7%) | -0.71 [-1.44, -0.34] | 64.3% |
| blk | 4305 | 97.1% | 82.2% | 60.0% | 537/1729 (31.1%) | -0.83 [-1.49, -0.38] | 68.0% |
| pooled | 8400 | 96.9% | 81.6% | 58.8% | 1089/3469 (31.4%) | -0.76 [-1.46, -0.36] | 66.1% |
