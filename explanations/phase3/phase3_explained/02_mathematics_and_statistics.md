# 02 — Mathematics and statistics

Every quantity Phase 3 computes, with its symbol, expected sign, assumptions,
and the one implementation mistake people actually make. All numerical
examples in this document were **computed by running the code**, not written by
hand — the commands are shown so you can reproduce them.

---

## 1. Notation

Fix one **decision site** `i`:

| Symbol | Meaning | In code |
|---|---|---|
| `c_i` | the DSL-correct candidate (a string) | `Site.correct` |
| `q_i` | the predeclared familiar competitor | `Site.competitor` |
| `r_i` | the remote specification (the rule text) | `rule=` argument |
| `r⁰` | a matched context with **no** rule | `rule=""` |
| `x_i` | the exact program prefix before the site | `Site.prefix` |
| `O_i` | 1 if generation **reached** a comparable site | `SiteObservation.reached` |
| `Y_i` | 1 if it emitted `q_i`, given it reached | `SiteObservation.reverted` |

`q_i` must be fixed **before** any outcome is observed. `Site` is a frozen
dataclass built by `sites.classify` for exactly this reason: you cannot decide
after the fact that whatever the model emitted "was" the competitor.

---

## 2. The full-sequence margin `M_seq`

$$M^{\text{seq}}_i = \log P(c_i \mid r_i, x_i) - \log P(q_i \mid r_i, x_i)$$

where each term is the sum over **every** token of the candidate:

$$\log P(y \mid x) = \sum_{j=1}^{K} \log P(y_j \mid x,\, y_{<j})$$

- **Expected sign.** `> 0` = the model prefers the specified token (good).
  `< 0` = reversion.
- **Interpretation.** Log-odds of correct over competitor. `M_seq = −2` means
  the competitor is about `e² ≈ 7.4×` more likely.
- **Assumptions.** Both candidates scored against a **byte-identical** prefix;
  both scored with the model's own tokenizer; the event is the full candidate.
- **Common mistake #1 — asymmetric prefixes.** Rebuilding the prefix separately
  for each candidate. `forced_prefix_margin` builds it **once** and reuses it;
  `test_margin_scores_both_candidates_against_identical_prefix` asserts the
  model saw exactly one distinct prefix.
- **Common mistake #2 — scoring only the first token.** `castShadow` vs
  `receiveShadow` are multi-token. Summing only the first token silently
  measures something else.
- **Common mistake #3 — normalising by length and calling it primary.**
  `MarginRecord.m_per_token` exists but is documented as a sensitivity
  analysis. Per-token normalisation answers a different question.

### 2.1 `M_seq` is not `G_tok`

$$G^{\text{tok}}_i = z_i(q^\star) - z_i(c^\star)$$

the single-next-token **logit** margin. These coincide **only** when both
candidates are exactly one token. Note `G_tok` also has the **opposite sign
convention** (positive = reversion), because it is used in the mechanistic
phase where "how much is the competitor promoted" is the natural reading.
Phase 3's behavioural endpoint is `M_seq`; `G_tok` appears nowhere in this
code, deliberately, so the two cannot be confused.

### 2.2 Shared suffixes and EOS change the estimand

If you score `c + s` and `q + s` for some shared suffix `s`, you are no longer
comparing `c` against `q`: `P(s | …c)` and `P(s | …q)` differ. Define the event
in advance as the candidate **plus any required grammar boundary**, and include
that boundary in both. Never append EOS mid-program to force a decision — that
asks the model whether the program ends here, not which spelling belongs.

---

## 3. Prior-strength calibration `T`

$$T_i = \log P_{\text{base}}(q_i \mid r^{0}, x^{\text{neutral}}) - \log P_{\text{base}}(c_i \mid r^{0}, x^{\text{neutral}})$$

- **Expected sign.** `> 0` = the base model prefers the familiar form before
  being taught anything.
- **Assumptions.** A *base* checkpoint (instruction tuning reshapes the
  likelihood surface); a neutral prefix that cues neither candidate; same role
  and comparable length.
- **What it is not.** Corpus frequency. It is model preference. See
  `01 §4.1`.
- **Status.** **Not implemented** in Phase 3. `measure/prior_strength.py` is
  vendored and computes whole-program NLL, which is a *different* quantity
  (program-level, not site-level).

---

## 4. Local-context activation `A`, and the circularity trap

Define a no-rule, local-context margin:

$$G^{\text{loc}}_i(x) = \log P(q_i \mid r^{0}, x) - \log P(c_i \mid r^{0}, x)$$

with `T_i = G^loc_i(x_neutral)`. A **valid** calibrated activation score is:

$$A^{\text{cal}}_i = G^{\text{loc}}_i(x_i) - T_i$$

**Why a naive version is circular.** If you instead define

$$A_i = \big[\log P(q_i \mid r_i, x_i) - \log P(c_i \mid r_i, x_i)\big] - T_i = -M^{\text{seq}}_i - T_i$$

then `A_i` *contains the outcome it is meant to explain*. Regressing reversion
on `T`, `A` and `T·A` would leak the response into the predictor and produce an
impressive, meaningless fit.

Two non-circular options:
1. **Randomise `A`** by constructing matched prefixes before any outcome is
   observed (the clean factorial estimand).
2. **Calibrate `A^cal`** on a *separate* base checkpoint or held-out items,
   then **freeze** it before touching instruction checkpoints.

**Status.** **Not implemented.** Avoiding the circular version is the single
most important thing to get right when it is built.

---

## 5. The 3×3 factorial and the difference-in-differences

With `T ∈ {neutral, medium, strong}` and `A ∈ {low, medium, high}`, the
preregistered finite contrast uses only the four corners:

$$\Delta_{\text{int}} = \big[\bar{M}_{\text{strong,high}} - \bar{M}_{\text{strong,low}}\big] - \big[\bar{M}_{\text{neutral,high}} - \bar{M}_{\text{neutral,low}}\big]$$

- **Expected sign on `M_seq`: negative.** More interference = lower (more
  negative) margin, and the hypothesis says the high-vs-low gap *grows* as the
  prior strengthens.
- **Expected sign on reversion probability: positive.** Because `M_seq` is
  "correct minus competitor" but `P(revert)` counts the competitor winning,
  the two scales have **opposite** signs for the same phenomenon. This is the
  easiest sign error in the whole project; `interaction_did` flips the margin
  sign internally before comparing agreement.
- The medium level is a monotonicity check; it is not needed for the contrast.

### 5.1 Why the DiD is **secondary**

An *ordinal* (non-crossing) interaction measured on a monotonically
transformed scale is partly an artifact of that scale. If `T=neutral` sits in a
near-linear region and `T=strong` in a compressed one, you get
"super-additivity" from the nonlinearity alone, with no mechanism.

Phase 3's rule: **the DiD counts as support only if its sign agrees on all
three scales** (margin, logit, probability). `InteractionResult.sign_agrees`
encodes it; `verdict()` returns `SCALE-DEPENDENT: …` otherwise.

A **crossover** (sign-reversing) interaction would be immune — those are
transformation-invariant. If the theory can be sharpened to predict one, it
becomes a far stronger claim.

### 5.2 Complete numerical example (computed, not hand-written)

Four corner cells, four observations each:

| cell | `M_seq` values | mean `M_seq` | `p_revert` |
|---|---|---:|---:|
| strong / high | −3.0, −2.0, −1.0, +0.5 | **−1.3750** | 0.750 |
| strong / low | −1.5, −0.5, +1.0, +2.0 | **+0.2500** | 0.500 |
| neutral / high | −1.0, +0.5, +1.0, +1.5 | **+0.5000** | 0.250 |
| neutral / low | −0.5, +1.0, +1.5, +2.0 | **+1.0000** | 0.250 |

`p_revert` is the fraction with `M_seq < 0`.

**Margin scale.**
`(−1.3750 − 0.2500) − (0.5000 − 1.0000) = (−1.6250) − (−0.5000) = −1.1250`

**Probability scale.**
`(0.750 − 0.500) − (0.250 − 0.250) = 0.250 − 0.000 = +0.2500`

**Logit scale.** `logit(.75)=+1.0986`, `logit(.50)=0`, `logit(.25)=−1.0986`
`(1.0986 − 0) − (−1.0986 − (−1.0986)) = +1.0986`

**Verdict.** Flipping the margin sign gives `+1.1250`; all three are positive,
so `sign_agrees = True` → *"sign agrees on all three scales."* The
interaction survives reparameterisation here and may be interpreted.

Reproduce:
```bash
PYTHONPATH=src python3 -c "
from phase3 import scoring as S
def mk(v): return [S.MarginRecord('s','m',0,0,0,x,1,1,True) for x in v]
r = S.interaction_did({('strong','high'):mk([-3,-2,-1,.5]),
                       ('strong','low'):mk([-1.5,-.5,1,2]),
                       ('neutral','high'):mk([-1,.5,1,1.5]),
                       ('neutral','low'):mk([-.5,1,1.5,2])})
print(r.did_margin, r.did_logit, r.did_prob, r.sign_agrees)"
```

**A contrasting case.** Make every strong cell revert (all `M_seq < 0`). Then
`p_revert = 1.0` in both strong cells, `did_prob = 0`, while `did_margin`
stays large. Saturation on the probability scale with a big margin effect is
exactly the scale-dependence this rule is designed to catch.
`test_interaction_flags_scale_dependence` covers it.

---

## 6. The extinction threshold `k*` — the primary estimand

Score `M_seq` at each rung of the ladder `(0,1,2,4,8,16,32,64,128)` and define
`k*` as the first upward zero crossing, linearly interpolated:

$$k^\star = k_{j-1} + \frac{0 - M_{j-1}}{M_j - M_{j-1}}\,(k_j - k_{j-1})$$

- **Expected sign/range.** `k* ≥ 0`. Larger = a more stubborn prior.
- **Interpretation.** "This collision costs about `k*` worth of in-context
  evidence." Directly actionable for a DSL designer.
- **Why interpolate rather than snap to a rung.** The ladder is geometric, so
  snapping quantises `k*` into buckets whose width grows with `k`, inventing
  ties between sites that are far apart.
- **Censoring.** A curve still negative at the last rung has `k_star = None`
  and `censored = True`. **Never drop censored sites** — they are precisely the
  strongest priors, so dropping them biases `k*` downward. Analyse them with
  survival methods, or report the censoring rate alongside the median.
- **Common mistake.** Padding the example pool by repeating examples. That
  changes the estimand from "more evidence" to "more repetition."
  `extinction_curve` truncates the ladder to `len(examples)` instead.

**Worked example (computed):**

| shots | 0 | 1 | 2 | 4 | 8 | 16 |
|---|---|---|---|---|---|---|
| `M_seq` | −2.0 | −1.6 | −1.1 | −0.4 | +0.6 | +1.2 |

The crossing lies between 4 and 8: `t = (0−(−0.4))/(0.6−(−0.4)) = 0.4`, so
`k* = 4 + 0.4·(8−4) = ` **`5.6`**.

---

## 7. The hurdle decomposition

$$P(\text{observed reversion}) = \underbrace{P(O=1)}_{\text{reach}} \times \underbrace{P(Y=1 \mid O=1)}_{\text{choice}}$$

- **Why two parts.** They are different processes with different causes.
  Reach depends on whether the program parses that far; choice depends on the
  competition at the site.
- **The real failure this prevents.** Experiment 02's `3/3` bare vs `15/20`
  scaffolded. Worked out:

| condition | reached | reverted | `P(O)` | `P(Y\|O)` | product |
|---|---:|---:|---:|---:|---:|
| bare | 3 / 20 | 3 | 0.150 | **1.000** | 0.150 |
| scaffolded | 20 / 20 | 15 | 1.000 | **0.750** | 0.750 |

The raw count is 5× higher under scaffolding, but **conditional reversion is
lower**. The headline reading was backwards.
- **Implementation note.** `HurdleResult` has **no** single "reversion rate"
  field, so the two cannot be silently collapsed. `p_revert_given_reach` is
  `None` — not `0.0` — when nothing reached, because "never got there" and
  "got there and never reverted" are different facts.
- Test: `test_hurdle_separates_reach_from_choice`.

---

## 8. Hierarchical / mixed-effects models

The intended behavioural model, with `M_seq` as outcome:

$$M^{\text{seq}}_i = \beta_0 + \beta_T T_i + \beta_A A_i + \beta_{TA}T_iA_i + b_{\text{task}} + b_{\text{mapping}} + b_{\text{grammar}} + b_{\text{model}} + \epsilon_i$$

- **Random intercepts** for AST template, mapping rotation, grammar family,
  model. Random slopes for manipulated factors where groups and convergence
  allow.
- **Expected sign.** `β_TA < 0` on `M_seq`; `β_TA > 0` on logit `P(Y=1)`.
- **Fixed, not random, with few levels.** With 2–3 grammar families, grammar is
  a **fixed stratification factor**. A random effect needs roughly 10–20+
  independently designed levels to estimate its variance at all.
- **Common mistake.** Treating 4,860 correlated site rows as independent. They
  are nested in templates, mappings and grammars; naive binomial intervals will
  be far too narrow.
- **Status.** **Not implemented.** Requires `statsmodels` — a new dependency.

### 8.1 Resampling units

Bootstrap at the **independent** unit: AST template or mapping block, not the
individual token site. Do **not** nonparametrically bootstrap 2–3 grammar
clusters — with that few clusters the bootstrap distribution is degenerate.

**Phase 3's own ceiling.** `sites.prefix_collisions` finds **3 prefix groups
containing 63 of 103 semantic sites**. Sites sharing a prefix are *the same
stimulus counted twice*; treating them as independent inflates `n` by ~2.5×.
After `dedupe_by_prefix`, **40** independent sites remain.

---

## 9. Prediction metrics (H4)

Site risk uses the **opposite** sign convention to `M_seq`:

$$S^{\text{seq}}_i = \log P_{\text{base}}(q_i \mid r_i, x_i) - \log P_{\text{base}}(c_i \mid r_i, x_i)$$
$$S^{\text{local}}_i = \log P_{\text{base}}(q_i \mid r^{0}, x_i) - \log P_{\text{base}}(c_i \mid r^{0}, x_i), \qquad S^{\text{shift}}_i = S^{\text{seq}}_i - S^{\text{local}}_i$$

**`S > 0` means danger.** `S_local` isolates local default support; `S_shift`
measures how far the rule moves the base model. Without the decomposition you
cannot tell "this spelling is doomed" from "this rule was ignored."
`test_risk_decomposition_adds_up` asserts `S_local + S_shift == S_seq`.

| Metric | Definition | Expected | Trap |
|---|---|---|---|
| **AUROC** | P(random positive ranked above random negative), ties = ½ | 0.5 = chance | Returns `None` if one class is absent — never report 0.5 for a degenerate split |
| **AUPRC** | average precision | baseline = **prevalence** | Meaningless without stating prevalence; reversion may be rare |
| **P@k** | precision in the top `k` | — | The right metric for a linter with a fixed rewrite budget |
| **Brier** | mean `(p − y)²` | lower better | A calibration metric; needs probabilities, not raw scores |
| **Calibration slope / intercept** | regress `y` on the predicted log-odds | slope 1, intercept 0 | Slope < 1 = overconfident. Not implemented yet |

**Mandatory baselines** (`linter.rank_report` takes them as an argument so they
cannot be forgotten):
- `length_baseline` — `|q| − |c|` in bytes, model-free;
- `identity_baseline` — "does this lexicon remap this role at all"; **if this
  matches your score, you built a language-identity detector, not a site
  predictor.**

Also required before claiming H4: whole-program NLL, token count/fragmentation,
and a supervised hidden-state probe with equal information.

---

## 10. Power, multiplicity, intervals

- **Power.** Simulate from the intended hierarchical/hurdle model using pilot
  estimates of reach rate, conditional reversion, ICCs, and the smallest
  meaningful interaction. A plain independent-binomial calculator is wrong
  here by a wide margin. **Not implemented.**
- **Multiplicity.** One preregistered primary (`k*`). Holm for a small
  confirmatory family; Benjamini–Hochberg FDR for exploratory site/component
  sweeps. Do not "correct away" the single declared primary, but do disclose
  every variant tested.
- **Intervals.** 95% intervals on all primary effects, bootstrapped at the
  template/mapping level (§8.1). For `k*`, intervals must respect censoring.

---

## 11. Learning resources

> **Verification note.** Not fetched or verified in this session — I had no
> browsing in this run and will not claim a check I did not do. Canonical,
> stable URLs. Listed 2026-10-01.

| Resource | Teaches | Why here | Read | Level | Time |
|---|---|---|---|---|---|
| Loftus (1978), "On interpretation of interactions", *Memory & Cognition* 6:312–319 | scale-dependence of ordinal interactions | **the justification for `k*` over the DiD** | whole (short) | intermediate | 1 h |
| Gelman & Hill, *Data Analysis Using Regression and Multilevel/Hierarchical Models* | mixed-effects, partial pooling | §8's model | ch. 11–13 | intermediate | 8 h |
| [Statsmodels mixed LM docs](https://www.statsmodels.org/stable/mixed_linear.html) | fitting the §8 model in Python | the unimplemented layer | "Mixed Linear Models" | intermediate | 2 h |
| Efron & Tibshirani, *An Introduction to the Bootstrap* | resampling, cluster bootstrap | §8.1 resampling units | ch. 1–6 | intermediate | 6 h |
| [scikit-learn: ROC and PR](https://scikit-learn.org/stable/modules/model_evaluation.html) | AUROC vs AUPRC, prevalence | §9 | "Precision-Recall", "ROC" | beginner | 1 h |
| [scikit-learn: probability calibration](https://scikit-learn.org/stable/modules/calibration.html) | reliability curves, Brier | §9 calibration | whole page | intermediate | 1.5 h |
| Mullahy (1986), "Specification and testing of some modified count data models", *J. Econometrics* 33:341–365 | hurdle models | §7 formalised | §1–2 | advanced | 2 h |
| [docs.python.org/3/library/math.html](https://docs.python.org/3/library/math.html) | `log`, `copysign` | the sign-agreement logic | `copysign` | beginner | 10 min |
