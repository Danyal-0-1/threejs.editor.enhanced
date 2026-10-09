# 02 — Mathematics: how each held-out number is computed, with worked examples

> Every number below was recomputed from the local copy of `heldout-20261007a`, and each
> matches the frozen export.
>
> The general formulas (margin, `k*` interpolation, Kaplan–Meier, AUROC, cluster bootstrap)
> are derived in [`../sol_experiment_explained/02_mathematics_and_statistics.md`](../sol_experiment_explained/02_mathematics_and_statistics.md)
> and in [`EXPERIMENT_IN_ONE_FILE.md`](../sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md).
> Here they are applied to the real held-out data.

---

## 1. H4 for one pair: Qwen2.5-Coder-32B, `dom`

**The data.** 1,515 sites. Each has:

- **risk** = −M(32B base, rule);
- **label** = 1 if M(32B-Instruct, rule) < 0.

606 sites have label 1 (n₁) and 909 have label 0 (n₀), so the prevalence is 0.400.

**AUROC by ranks (Mann–Whitney).** Rank all 1,515 risks from lowest (1) to highest, giving
ties their average rank. Sum the ranks of the label-1 sites: R₁ = 616,963. Then

$$
\text{AUROC} = \frac{R_1 - n_1(n_1+1)/2}{n_1 n_0}
= \frac{616{,}963 - 606\cdot607/2}{606\cdot909}
= \frac{616{,}963 - 183{,}921}{550{,}854} = \mathbf{0.7861}
$$

**In words:** pick a random reverting site and a random correct site. The base model ranks
the reverting one as riskier 78.6% of the time. A coin flip would give 50%.

**The differences (criteria C1 and C2):**

| baseline | AUROC of baseline | Δ = 0.7861 − baseline | 95% template-bootstrap interval |
|---|---:|---:|---|
| identity (constant) | 0.5000 | **+0.2861** | [+0.243, +0.325] |
| length | 0.4549 | **+0.3312** | [+0.272, +0.394] |
| role-level `terminal_rate` | 0.6022 | +0.1839 | [+0.122, +0.245] |

**The bootstrap interval**
([`analysis.cluster_bootstrap`](../../src/phase3_2/analysis.py#L103)):

- Draw the 80 templates with replacement, 2,000 times (seed 20261002). Each drawn template
  brings all its sites, so a template drawn twice counts twice.
- Recompute both AUROCs and their difference each time.
- The 2.5th and 97.5th percentiles of the 2,000 differences form the interval.

**The p-value and Holm** ([`bootstrap_pvalue_greater`](../../src/phase3_2/analysis.py#L148),
[`holm`](../../src/phase3_2/analysis.py#L154)):

$$
p = \frac{\#\{\text{draws} \le 0\} + 1}{B + 1} = \frac{0 + 1}{2001} = 0.0005
\qquad
p_{\text{Holm}} = \min(1,\, 2 \times 0.0005) = \mathbf{0.0010}
$$

Both C1 and C2 had no draw at or below zero, so both adjusted values are 0.0010. That is the
`0.0009995` you see in every row of `HYPOTHESIS_RESULTS.md`. It is the smallest p a
2,000-draw bootstrap can report, not an exact value.

**The decision** ([`h4.criteria`](../src/p33/h4.py#L437)):

- C1 is met because Δ = 0.286 ≥ 0.10, the interval lower bound is above 0, and the Holm p is
  below 0.05.
- C2 is met because 0.331 ≥ 0.05, likewise.

**Within-lexicon check.** The same AUROC computed inside each of the 5 lexicons and averaged
gives 0.787 ≈ 0.786. The score ranks *sites*, not just lexicons.

---

## 2. Reversion and the rule effect for one cell

**Cell:** Qwen2.5-Coder-32B, `dom`, `d75s1a`, compared with `norule`. 341 paired sites in 80
templates.

| | value |
|---|---|
| mean of M(rule) − M(norule) | **+0.168 nats** |
| median | +0.091 |
| 95% template-bootstrap interval | [−0.057, +0.422], which **includes 0** |
| share of sites the table helped (Δ > 0) | 52.8% |

**In odds:** e^0.168 = 1.18. The table makes the new spelling 18% more likely relative to the
old one, on average. At this cell, that is not distinguishable from zero.

**Across all cells:**

- 263 of 420 model × lexicon × control intervals are above zero, and none below.
- The per-model means range from +0.16 to +0.62 nats (table in [00 §5](00_complete_results.md)).

**Why reversion barely moves.** Take a site at M = −1, a typical reverting site. A shift of
+0.35 nats leaves it at −0.65: still reverting. Only sites already within about 0.35 of zero
flip. So the reversion rate drops by only 5–6 points, from 0.534 to 0.482 in `dom`.

---

## 3. Kaplan–Meier for one model: Qwen2.5-Coder-32B, `dom`, initially wrong

**The data.** 95 sites were wrong with 0 examples. 83 crossed somewhere on the ladder; 12
never did and are censored at 32. Sorted by `k*`:

| t (examples) | at risk nⱼ | switches dⱼ | S(t) = S(t⁻)·(1 − dⱼ/nⱼ) |
|---:|---:|---:|---:|
| 0.026 | 95 | 1 | 0.9895 |
| 0.042 | 94 | 1 | 0.9789 |
| 0.068 | 93 | 1 | 0.9684 |
| 0.118 | 92 | 1 | 0.9579 |
| … | … | … | … |
| 1.360 | 48 | 1 | 0.5052 → **0.4947** |

S first drops to 0.5 or below at t = 1.360, so the **median is 1.36 examples**. The 95%
template-bootstrap interval is [1.04, 2.66].

**Why `k*` can be below 1.** It is interpolated. A site at M = −0.1 with 0 examples and +2.0
with 1 example crosses at 0 + 1 × 0.1 / 2.1 = 0.05. Sub-1 values mean "the first example is
enough".

**Why censoring matters.** Drop the 12 censored sites and the median falls, because the
hardest sites disappear. KM keeps them at risk until 32. Across all models, 784 of 4,253
initially-wrong ladders (18.4%) are censored.

**Sustained switching.** `sustained_k` is the first rung after which M ≥ 0 up to 32. Its median
over the 2,912 sites that eventually hold is **8**, against a median first switch of 2.06. The
gap is the "wobble" ([01 §6](01_theory.md)).

---

## 4. The D11 scale slope, by hand: H4 AUROC in `dom`

| size (B) | 0.5 | 1.5 | 3 | 7 | 14 | 32 |
|---|---:|---:|---:|---:|---:|---:|
| x = log₁₀(size) | −0.301 | 0.176 | 0.477 | 0.845 | 1.146 | 1.505 |
| y = AUROC | 0.888 | 0.963 | 0.949 | 0.760 | 0.852 | 0.786 |

$$
\bar x = 0.6414,\quad \bar y = 0.8663,\quad
S_{xx} = \sum (x-\bar x)^2 = 2.1740,\quad
S_{xy} = \sum (x-\bar x)(y-\bar y) = -0.1773
$$

$$
\text{slope} = S_{xy}/S_{xx} = -0.0815 \text{ per 10× parameters}
$$

The official value is −0.0814; the rounding of y explains the last digit.

**Inference.**

- Resample templates 2,000 times, using the *same* draw for all six sizes. Recompute the six
  AUROCs and the slope each time.
- The interval is [−0.111, −0.050]. No draw was at or above 0, so p < 1/2000 = 0.0005.
- Holm over the 6 D11 slopes multiplies the smallest p by 6, giving p < 0.003.

**How to read it.** The fit goes through two high points (1.5B, 3B) and two low ones (7B,
32B). Six non-monotone points support "lower at the large end", not a smooth law. Its
reversion siblings are flat: the largest is +0.033 per 10×, Holm p 0.072.

---

## 5. Arm B, the generation hurdle: Qwen2.5-72B-Instruct, `dom`

**Pooled over the 5 lexicons.** The model wrote 390 programs, one per template per lexicon
(74 + 76 + 80 + 80 + 80 templates), which together offered 1,515 sites.

| quantity | formula | value |
|---|---|---|
| reach | sites whose generated program matches the target up to the site ÷ sites | 497 / 1,515 = **0.328** |
| reversion given reach | reached sites where the old spelling followed ÷ reached | 74 / 497 = **0.149** |
| product (reported alongside only) | reverted ÷ all sites | 74 / 1,515 = 0.049 |
| task accuracy | programs whose IR equals the target's ÷ programs | 107 / 390 = **0.274** |
| parse failures | | 51 / 390 = 0.131 |

**Why the product is not the headline.** Compare the smallest model: reach 0.029 and
reversion 0.227, a product of 0.007. It *looks* safer than 72B (0.049) only because it almost
never writes the program at all. The two-number hurdle keeps that visible
([`armb.hurdle`](../src/p33/armb.py#L194)).

**All models pooled:**

- reach 4,104 / 30,300 = 0.135;
- reversion given reach 812 / 4,104 = 0.198;
- correct programs 747 / 7,800 = 0.096.

---

## 6. H5 for one cell: Qwen2.5-72B-Instruct, `dom`, `d25s3`

The cell has 220 sites. With the original lexicon, 90 of them revert.

**Targeted arm.** The 3 roles with the highest base-model risk were respelled.

| | sites | reversions before | reversions after |
|---|---:|---:|---:|
| repaired roles' sites | 65 | 29 | **36** (all 36 still silent) |
| control sites (other roles) | 155 | 61 (rate 0.394) | 13 (rate 0.084) |
| all | 220 | 90 | 49 |

$$
\text{per-symbol reduction} = \frac{90 - 49}{3} = \mathbf{13.67}
$$

**Random arms** (3 roles each, seeds 1–5): 12.00, 19.00, 1.00, 10.00, 4.33, a mean of 9.27.
Here targeted − random = +4.40.

**Global arm** (all 9 reassigned roles respelled): reversions 90 → **7**, silent afterwards **0**.

$$
\text{per-symbol} = \frac{90 - 7}{9} = 9.22
$$

**What the arithmetic shows.**

1. **The gain did not come from the repaired sites.** In the targeted arm they got slightly
   worse (29 → 36, all silent). The gain came from the *other* sites (61 → 13): changing 3
   rows of the token table changed the whole prompt, and the model read it differently.
2. **Partial repairs leave errors silent.** These lexicons permute familiar spellings, so the
   old spelling of a repaired role still names another role.
3. **Only the global arm reaches zero silent errors,** because no familiar spelling keeps any
   meaning.
4. **Over 100 cells,** targeted beat the random mean in only 43; the mean difference is −0.41.
   H5 is not supported.

---

## 7. Calibration: what the frozen parameters do, and the gap

**Platt scaling, frozen on development** (0.5B pair: a = −0.2984, b = 0.9014):

$$
p = \sigma(a + b\cdot\text{risk}) = \frac{1}{1 + e^{-(a + b\,\text{risk})}}
$$

For risk = 2.476: p = σ(1.934) = 0.874.

**ECE (10 equal-width bins):**

$$
\text{ECE} = \sum_{b=1}^{10} \frac{n_b}{N}\,\lvert \bar y_b - \bar p_b \rvert
$$

This is the gap between the predicted and observed reversion rate, averaged over bins.

**Results for the frozen pairs on held-out data:**

| pair | family | ECE | calibration slope |
|---|---|---:|---:|
| 0.5B | `dom` | 0.047 | 1.08 |
| 0.5B | `blk` | 0.051 | 0.84 |
| 1.5B | `dom` | 0.036 | 1.18 |
| 1.5B | `blk` | 0.052 | 0.83 |

A slope of 1 is perfect. Below 1, the probabilities are over-confident; above 1,
under-confident.

**Why the other 8 pairs show a slope of exactly 1.00.** With no frozen parameters, the
export fits the logistic calibration *on the same held-out rows*. Logistic regression's score
equations force the calibration intercept to 0 and the slope to 1 on its own training data
(`test_calibration_of_a_fitted_model_is_identity`). Their ECE and Brier are therefore
in-sample. They are not evidence of transfer ([08](08_issues_and_superseded_numbers.md)).

---

## 8. Paraphrase robustness

For each model × family, compute reversion under three framings of the rule prompt
(`p0` = the rule prompt, `p1`, `p2`):

$$
\text{range} = \max_v \text{reversion}_v - \min_v \text{reversion}_v
$$

Over 42 groups: 0.010–0.132, median 0.046, and 5 above 0.08. The preregistration said the
headline would become the *range* if the variants disagreed in sign. None reversed the
picture.

---

## 9. Formulas at a glance

| quantity | formula | held-out value example |
|---|---|---|
| margin | $\log P(c) - \log P(q)$, first divergent token on | — |
| reversion rate | $\frac1n\sum \mathbf 1[M<0]$ | 0.462 (32B, `dom`, rule) |
| rule effect | $\overline{M_\text{rule} - M_\text{ctrl}}$ | +0.168 (32B, `dom`, `d75s1a`) |
| AUROC | $\frac{R_1 - n_1(n_1+1)/2}{n_1 n_0}$ | 0.786 |
| bootstrap p | $\frac{\#\{d \le 0\} + 1}{B+1}$ | 0.0005 |
| Holm | $\min(1, (m-i+1)\,p_{(i)})$, made monotone | 0.0010 |
| KM | $S(t) = \prod_{t_j \le t}(1 - d_j/n_j)$ | median 1.36 |
| scale slope | $S_{xy}/S_{xx}$ on $\log_{10}$ size | −0.081 |
| hurdle | reach = reached/sites; revert∣reach = reverted/reached | 0.328, 0.149 |
| H5 per-symbol | (before − after over all sites) ÷ changed roles | 13.67 |
| ECE | $\sum \frac{n_b}{N}\lvert \bar y_b - \bar p_b\rvert$ | 0.036–0.052 (frozen pairs) |
