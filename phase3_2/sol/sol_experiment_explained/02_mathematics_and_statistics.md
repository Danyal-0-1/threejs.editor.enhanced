# 02 — Mathematics and statistics (the Sol pipeline)

Every number here was computed by running the code: on the development smoke
(`local_smoke/smoke-local-20261005`, Qwen2.5-Coder-0.5B @ `8123ea2e`,
`dom × d50s1`, 12 sites), on the real development plan, or on the tests' hand
examples. The smoke is far too small to estimate anything, so its numbers
illustrate the arithmetic, not the science.

The first-divergent-token margin was introduced in
[`phase3_2_explained/02 §1`](../../phase3_2_explained/02_mathematics_and_statistics.md).
§1 below restates it only as far as the new refusals and the fp32 head require.

---

## 1. The canonical margin, and when it refuses

For a site with context `x` (prompt plus program prefix), correct spelling `c`
and competitor `q`, tokenise the **full strings** `x+c` and `x+q`:

```
T(x+c) = t_1 … t_n          T(x+q) = u_1 … u_m
k      = first index where they differ            (k_common = k − 1 shared tokens)
```

$$
\log P(c\mid x) = \sum_{i=k}^{n} \log p(t_i \mid t_{<i}), \qquad
\log P(q\mid x) = \sum_{i=k}^{m} \log p(u_i \mid u_{<i}), \qquad
M_{\text{seq}} = \log P(c\mid x) - \log P(q\mid x).
$$

**Positive M means the model prefers the rule.** `M < 0` is reversion.

**The scorer refuses rather than invents.** These cases raise:

| Case | Condition | Exception |
|---|---|---|
| the two tokenisations are identical | `T(x+c) == T(x+q)` | `IdenticalCandidates` |
| one side has nothing left after the divergence | `k > n` or `k > m` (one tokenisation is a strict prefix of the other) | `ZeroLengthSpan` |
| no context for the first divergent token | divergence at the very first token | `NoContext` |

The second case is defect **P33-001**. The first P32-001 fix still returned
`0.0` for that one side, and 0.0 is a plausible-looking margin. The old
`phase3` scorer now raises too (`test_old_phase3_scorer_now_raises_instead_of_returning_zero`).

### Worked example 1 — `t000`: a merged token

The rendered program under `d50s1` (the chain operator follows the class sigil, by rule I7):

```
identity : (function(){ $S('.wheel').recolor('#111111'); })();
d50s1    : (function(){ $S('#wheel')#recolor('#111111'); })();
                           ▲ site: prefix "(function(){ $S('"  c = "#"  q = "."
```

Real values (rule condition):

| Field | Value |
|---|---|
| prompt + prefix tokens | 303 |
| `k_common` | **302** |
| `merged` | **true** |
| first divergent tokens | `('#` vs `('.` |
| tokens per candidate | 1 and 1 |
| log P(c) | **−4.4885** |
| log P(q) | **−5.1358** |
| **M** | **+0.6473** |

The tokenizer fuses `('` with the sigil into one token. So the last prefix
token is "un-merged", and the divergence starts one token **earlier** than the
prefix ends (302 < 303). A scorer that assumed the prefix boundary was a token
boundary would score the wrong tokens.

### Worked example 2 — `t004`: unequal lengths

| Field | Value |
|---|---|
| `c` | `lasso`, 2 tokens (`lass` + `o`) |
| `q` | `selected`, 1 token |
| `merged` | false |
| log P(c) | −7.1938 (a sum of 2 terms) |
| log P(q) | −1.7124 |
| **M** | **−5.4815** |

A two-token candidate pays two log-probabilities. That is a structural
disadvantage, unrelated to rule-following, and it is why H4 must beat a
`token_count` baseline (§7).

---

## 2. Why bf16 margins are quantised, and the fp32 head

When both candidates diverge at a **single** token in the **same** context,
they share the normaliser:

$$
\log p(c) = z_c - \operatorname{LSE}(z), \quad \log p(q) = z_q - \operatorname{LSE}(z)
\;\Rightarrow\; M = z_c - z_q .
$$

`LSE(z)` is the log of the sum of `exp` over every logit.

So M is a difference of **two logits**. bf16 keeps 8 significant bits (7
stored and 1 implicit). Between $2^e$ and $2^{e+1}$, representable numbers are
$2^{e-7}$ apart. Logits in [8, 16) therefore sit on a grid of **1/16**, and so does their
difference:

| Site | native bf16 M | Multiple of 1/16? | fp32-head M | \|Δ log P(c)\| |
|---|---:|---|---:|---:|
| t000 | +0.6250 | yes, 10/16 | +0.6473 | 0.0051 |
| t002 | −4.4375 | yes, −71/16 | −4.4436 | 0.0243 |
| t004 | −5.4763 | no (multi-token: normalisers differ per position) | −5.4815 | 0.0422 |

The fp32 head recomputes `z = W·h` in fp32. `h` is the decoder's last hidden
state, upcast; `W` is an fp32 copy of the output matrix. The grid becomes
about $10^{-6}$ relative.

The outcome is `sign(M)`, so a 1/16-nat grid decides the outcome for any site
within ~0.06 of zero. The head is disabled automatically for models with
logit soft-capping or scaling, where `W·h` is not the final logit.

---

## 3. `k*` — the threshold, exactly

Ladder rungs $k_0 = 0 < k_1 < \dots$ (0, 1, 2, 4, 8, 16, 32 on Sol; 0, 1, 2, 4, 8 in the smoke), margins $M_j$:

$$
k^* = \begin{cases}
0 & M_0 \ge 0 \quad(\text{already correct, not censored})\\[2pt]
k_{j-1} + \dfrac{0 - M_{j-1}}{M_j - M_{j-1}}\,(k_j - k_{j-1}) & \text{first } j \text{ with } M_{j-1} < 0 \le M_j\\[8pt]
\text{censored at } k_{\max} & \text{no upward crossing}
\end{cases}
$$

A curve that crosses and later drops below zero is **not** censored. It is
flagged (`recrossed_down`), and `sustained_k` records when it last crossed for good.

**Real curves (smoke, rule condition):**

| Site | Stratum | M at 0, 1, 2, 4, 8 shots | `k*` | Notes |
|---|---|---|---:|---|
| t000 | sigil | +0.647, −1.396, −0.931, +0.510, +0.216 | **0** | already correct; drops, recovers; `sustained_k = 4` |
| t005 | sigil | +0.691, +2.848, +1.765, +1.899, +5.701 | **0** | non-monotone but never negative |
| t006 | verb | +4.143, +2.715, +1.772, +2.440, +0.537 | **0** | drifts down from +4.1 to +0.5 but stays positive: examples *weaken* a correct preference |
| t011 | keyword | −2.565, −1.699, +0.706, +0.411, −1.022 | **1.706** | crosses, then falls back; `sustained_k = None` |
| t004 | keyword | −5.481, −6.299, −6.184, −5.824, +2.530 | **6.788** | crosses only at the last step |
| t002 | verb | −4.444, −3.955, −2.805, −2.263, −1.654 | censored | rising, but never reaches 0 |

**The interpolation, by hand:**

- **t004:**
  $k^* = 4 + \frac{5.824}{2.530 + 5.824}\cdot 4 = 4 + 0.6972\cdot 4 = 6.7888$. The
  code gives 6.788767.
- **t011:**
  $k^* = 1 + \frac{1.699}{0.706 + 1.699}\cdot 1 = 1.7065$.

**Non-monotonicity:** 5 of the 6 curves (0.833) are non-monotone, and 2 of 6 (0.333)
re-cross downward. The Phase 3.3 audit found 237 of 240 non-monotone.

---

## 4. Kaplan–Meier, and the two populations

With distinct event times $t_i$, $d_i$ events and $n_i$ sites still at risk:

$$\hat S(t) = \prod_{t_i \le t}\Bigl(1 - \frac{d_i}{n_i}\Bigr), \qquad
\text{median} = \min\{t : \hat S(t) \le 0.5\}.$$

**ALL_SITES** (n = 6):

- events at 0 (×3), 1.706 and 6.788; one site censored at 8.
- $\hat S(0) = 1 - 3/6 = 0.5$, so the **median is 0**.
- Censoring rate 1/6 = 0.167.

**INITIALLY_WRONG** (n = 3: t002, t004, t011):

- $\hat S(1.706) = 1 - 1/3 = 0.667$.
- $\hat S(6.788) = 0.667\cdot(1 - 1/2) = 0.333 \le 0.5$, so the **median is 6.788**.
- Censoring rate 1/3 = 0.333.

**Median among crossers** (diagnostic only):

- median{1.706, 6.788} = **4.248**.
- It drops t002, the strongest prior, so it is biased **down**. The CSV
  labels it `drops censored sites; underestimates k*; diagnostic only`.

**No interval at all here:** 6 sites from 6 templates is below the 8-cluster
minimum. The CSV says `NO INTERVAL (<8 template clusters)`.

---

## 5. The template-cluster bootstrap, with multiplicity

Clusters $g = 1..G$ (templates), with rows $R_g$. For $b = 1..B$:

1. Draw $G$ indices $i_1..i_G$ uniformly, with replacement.
2. Form the resample $\bigcup_j R_{i_j}$, **tagging every copy with `_draw = j`**.
3. Compute $\hat\theta^*_b$.

The interval is the $(\alpha/2,\ 1-\alpha/2)$ percentiles of $\hat\theta^*$.
Defaults: $B = 2000$, seed 20261002, α = 0.05. There is no interval if $G < 8$
or if the point statistic is undefined.

**Why the tag is the fix (P33-005).** A paired statistic matches *rule* with
*control* rows for the same site. Keyed by `site_id` alone, the two copies of
a twice-drawn template collapse into one:

```
templates  tA: d = 1      tB: d = 3       draw = [tA, tA, tB]
correct    (1 + 1 + 3) / 3 = 5/3 = 1.667     key (_draw, site_id)
old        mean{tA: 1, tB: 3} = 2.000        key site_id   ← weight lost
```

Every resample then behaved like a draw **without** replacement, so the
variance was too small. Corrected Phase 3.3 intervals:

| Model | Family | Mean | Old interval | Corrected interval |
|---|---|---:|---|---|
| 0.5B base | dom | +0.171 | [+0.029, +0.326] | **[−0.012, +0.370]** |
| 0.5B base | blk | +0.156 | [−0.020, +0.344] | [−0.068, +0.402] |
| 0.5B instruct | dom | +0.199 | [−0.003, +0.414] | [−0.054, +0.477] |
| 0.5B instruct | blk | +0.222 | [−0.004, +0.465] | [−0.064, +0.530] |

---

## 6. The paired rule effect

$$d_s = M_{\text{rule}}(s) - M_{\text{control}}(s), \qquad \hat\theta = \frac1n\sum_s d_s .$$

There are two controls: `norule` and `norule_lenmatched`.

**Smoke, against `norule`:** 12 sites from 11 templates. Template t006 carries two sites,
which move together in every resample.

```
d_s = −0.044 +1.108 −1.738 +0.648 +0.370 −1.730 −0.124 +3.170 +1.725 −1.642 +0.179 +0.258
sum = 2.181        mean = 0.1818        share helped = 7/12 = 0.583
```

| Control | Mean | Interval (B = 200, 11 clusters) | Excludes 0 |
|---|---:|---|---|
| norule | +0.182 | [−0.433, +0.911] | no |
| norule_lenmatched | +0.291 | [−0.368, +1.131] | no |

Reversion with the table present: 7/12 = **0.583**, interval [0.333, 0.833]. The
row is labelled `condition = rule`.

### Holm (step-down), for the H4 criteria

Sort the p-values as $p_{(1)} \le \dots \le p_{(m)}$. Then
$\tilde p_{(i)} = \max_{j\le i}\min\{1,(m-j+1)\,p_{(j)}\}$.

Test's hand example:

| p-value | Multiplier | Raw adjusted | After the running max |
|---|---:|---:|---:|
| a = 0.01 | ×3 | 0.03 | **0.03** |
| c = 0.03 | ×2 | 0.06 | **0.06** |
| b = 0.04 | ×1 | 0.04 | **0.06** |

---

## 7. H4 metrics

**The table** (one row per base/instruct pair × site):

- `risk` = −M(base, rule)
- `label` = 1 if M(instruct, rule) < 0

**The metrics:**

| Metric | Definition |
|---|---|
| AUROC | Mann–Whitney with average ranks: $\frac{R_1 - n_1(n_1+1)/2}{n_1 n_0}$ |
| AUPRC | step-wise average precision $\frac1P\sum_{\text{pos } i}\text{precision@rank}(i)$; report it **with** prevalence, its baseline |
| precision@k | positives among the k highest risks, k ∈ {10, 50} |
| Brier | $\frac1N\sum(p - y)^2$ |
| ECE | 10 equal-width bins: $\sum_b \frac{n_b}{N}\,\lvert\bar y_b - \bar p_b\rvert$ |
| calibration slope/intercept | logistic regression of $y$ on $\operatorname{logit}(p)$; perfect is (0, 1) |
| Platt calibration | $p = \sigma(a + b\cdot\text{risk})$ fitted by Newton–Raphson on **development**, then frozen |
| threshold | Youden's $J = \text{TPR} - \text{FPR}$, maximised on development, then frozen |

**Why the identity baseline is exactly 0.5.** On the SEMANTIC-only eligible
set every site has correct ≠ competitor, so `identity` = 1 for all of them.
With a constant score, every positive–negative pair is a tie worth ½, so
AUROC = ½. Criterion C1, "ΔAUROC vs identity ≥ 0.10", is therefore
**AUROC ≥ 0.60** (deviation D6). The exploratory `terminal_rate` baseline is
the instruct model's reversion rate for the same terminal in the *other*
templates (leave-one-template-out), shrunk toward the pair's overall rate with
one pseudo-count. It is the real "language-level" competitor: it knows which
*role* is hard, but nothing about the specific site.

**When a metric is NOT ESTIMABLE:** with a single class present, AUROC is undefined. The
group then reports `NOT ESTIMABLE` instead of crashing or inventing a number.

---

## 8. Power under clustering

| Quantity | Formula |
|---|---|
| design effect | $\text{DE} = 1 + (m-1)\rho$ ($m$ = sites per template, $\rho$ = ICC) |
| effective n | $n_{\text{eff}} = n/\text{DE}$ |
| ICC estimate | one-way ANOVA, truncated at 0: $\hat\rho = \frac{MSB - MSW}{MSB + (n_0-1)MSW}$, $n_0 = \frac{N - \sum n_g^2/N}{k-1}$ |

**Rule effect.** With $se = sd/\sqrt{n_{\text{eff}}}$:

$$\text{power} = 1 - \Phi\!\left(z_{1-\alpha/2} - d/se\right)$$

Plugging in the smoke's (uninterpretable) $d = 0.1818$ and $sd = 1.3916$:

| Design | ICC 0 | ICC 0.1 | ICC 0.2 |
|---|---:|---:|---:|
| smoke shape: 80 templates × 1.09 sites | 0.230 | 0.228 | — |
| **development shape: 80 templates × 10.65 sites** (852 sites) | **0.968** | **0.776** | **0.605** |

The design that looks overpowered at ICC 0 is marginal at ICC 0.2. The
development run estimates ρ instead of assuming it.

**H4 criterion C1.**

- The variance follows Hanley–McNeil:
  $\mathrm{Var}(\hat A) = \frac{A(1-A) + (n_1-1)(Q_1-A^2) + (n_0-1)(Q_2-A^2)}{n_1 n_0}$,
  with $Q_1 = \frac{A}{2-A}$ and $Q_2 = \frac{2A^2}{1+A}$, multiplied by DE.
- With $P(\text{C1}) = P(\hat A \ge 0.60 \text{ and lower bound} > 0.5)$, at the development shape (prevalence 0.45, ICC 0.1):

  | True AUROC | P(C1) |
  |---:|---:|
  | 0.60 | 0.500 |
  | 0.65 | 0.970 |
  | 0.70 | 1.000 |

- An analytic curve is checked against a clustered binormal simulation.

**Arm B.** The precision of $P(\text{revert}\mid\text{reach})$ is
$1.96\sqrt{p(1-p)/n_{\text{eff}}}$, with $n_{\text{eff}} = n\cdot P(\text{reach})/\text{DE}$.
The hurdle shrinks the sample before clustering does.

**Pilot data are development-only.** `pilot_from_rows` raises `HeldoutLeak` on any
other split label.

---

## 9. The Arm B hurdle

$$P(\text{revert}) = P(\text{reach})\cdot P(\text{revert}\mid\text{reach}).$$

- **Reach:** the generated text, after layout normalisation, starts with the site's
  normalised prefix.
- **Outcome, given reach:** the continuation starts with the correct spelling, the competitor,
  or something else. Longer candidates are tried first, so a prefix of a longer spelling
  never wins by accident.
- **Reporting:** the first two factors are reported, and the product only alongside them.
  A model that never reaches a site has an undefined conditional rate, never a low one.

---

## 10. H5 arithmetic

For each (model, family, lexicon, arm, seed), with $n_{\text{ch}}$ roles changed:

$$
\text{benefit per symbol} = \frac{R_{\text{before}} - R_{\text{after}}}{n_{\text{ch}}},
\qquad
\text{control degradation} = r^{\text{ctl}}_{\text{after}} - r^{\text{ctl}}_{\text{before}} \le 0.02 .
$$

- $R$ counts reverted sites; "before" is the same model's Arm A rule condition.
- $r^{\text{ctl}}$ is the reversion **rate** on sites whose role was not changed.
- Targeted arm: the 3 roles with the highest mean base-model risk. Random arm: seeds 1–5. Global
  arm: every remapped role.

**IR proof.** Each repaired lexicon is accepted only if all 142 programs × 2
families = **284** renderings re-parse to the original canonical IR.

---

## 11. Fertility, measured per tokenizer

Over the 80 templates, real Qwen tokenizer (`cc349caf`):

| Lexicon | Tokens | Characters | Tokens/char | Relative fertility | Relative token count | Fragmentation |
|---|---:|---:|---:|---:|---:|---:|
| identity | 2,928 | 7,980 | 0.366917 | 1 | 1 | 1.35714 |
| d50s1 | 3,158 | 7,995 | 0.394997 | **1.07653** | 1.07855 | 1.35714 |

- **Identity matches Phase 3.2:** 0.3669 was measured there independently.
- **Fragmentation is identical by construction.** A within-shape-class
  permutation reassigns spellings to roles but keeps the same *set* of
  spellings, and fragmentation is the mean token count of that set. It can only
  separate lexicons that introduce new spellings, such as Phase 3's
  `beta`/`gamma`.
- **The real difference is context:** `d50s1` costs 7.7% more tokens per character.
  A plausible explanation, not tested here: familiar spellings in unfamiliar
  positions, such as `')#recolor`, merge less often than in their usual ones,
  such as `').recolor`.

---

## 12. What is still not implemented

- **Bias-corrected (BCa) intervals.** Percentile intervals are used. With 11 clusters and
  skewed statistics, BCa would be better.
- **Mixed-effects models.** The template is handled by resampling, not modelled. A GLMM
  would estimate the ICC and the effects jointly.
- **A formal test of the KM median.** The k\* precision in `power.csv` is a
  resampling projection, not a test.
- **Equivalence tests.** "The rule table barely helps" would need a TOST with a
  pre-specified margin to become a positive claim of "no effect". None is preregistered.
