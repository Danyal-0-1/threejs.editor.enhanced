# The mathematics of this experiment

*A textbook-style companion to [EXPERIMENT_IN_ONE_FILE.md](EXPERIMENT_IN_ONE_FILE.md). Written 2026-10-08.*

This guide teaches the mathematics behind the experiment, not just the names of its metrics. The aim is to let you explain **what was measured, why that equation was selected, what a number means, and what it does not establish**.

The recurring example is the development site `dom:d50s1:t011:T_TYPE_MESH:0`. Its correct spelling is `light`; the familiar competitor is `mesh`. Under this mapping, writing `mesh` selects groups rather than meshes. Both spellings are legal, but their meanings differ.

Numbers identified as the **worked development example** come from the companion document and its development measurements. Other small datasets are explicitly **teaching examples**, not additional experimental results. This document does not rerun the GPU experiment or change the frozen analysis.

## How to study this guide

Read Sections 1–6 to understand what one site produces. Read Sections 7–8 to understand prediction quality. Read Sections 9–10 to understand `k*` and Kaplan–Meier. Read Sections 11–14 to understand uncertainty, significance, power, and scale. Sections 15–18 connect the mathematics to the hypotheses, implementation limits, further study, and practice questions.

### Jump to a topic

- [Probability, logits, softmax, and logs](#2-probability-logits-softmax-and-logarithms)
- [Likelihood, cross-entropy, NLL, and perplexity](#3-likelihood-negative-log-likelihood-cross-entropy-and-perplexity)
- [Margin, risk, and rule effect](#4-margin-risk-reversion-rate-and-the-rule-effect)
- [Deriving sigmoid calibration](#5-sigmoid-calibration-where-the-function-comes-from)
- [Thresholds, Brier, and calibration error](#6-thresholds-and-probability-quality-diagnostics)
- [AUROC](#7-auroc-ranking-dangerous-sites-without-choosing-one-cutoff) and [average precision](#8-precision-recall-average-precision-and-ties)
- [Extinction threshold](#9-the-primary-endpoint-the-extinction-threshold-k) and [Kaplan–Meier censoring](#10-kaplanmeier-median-and-censoring)
- [Cluster bootstrap](#11-cluster-bootstrap-and-confidence-intervals), [Holm](#12-statistical-significance-bootstrap-tails-and-holm-correction), and [power](#13-correlation-design-effect-effective-sample-size-and-power)
- [Scale trends](#14-scale-trends-ordinary-least-squares-on-log-model-size)
- [Hypotheses and outcomes](#15-connect-the-mathematics-to-arm-b-h5-and-h2), [implementation limits](#16-development-freezing-and-the-limits-of-current-implementation), and [study materials](#17-what-else-should-you-learn)
- [Practice questions and glossary](#18-practice-glossary-and-a-research-explanation-you-can-say-aloud)

At the end of each main topic, **Say it aloud** gives a sentence you can use in a research discussion.

---

## 1. What is being measured?

Imagine two doors. One leads to meshes and one to groups. The new language changes the signs on the doors. The model's old habit pulls it toward the familiar sign, even though that sign now leads to the wrong destination.

The mathematical story is:

```text
Model logits → token probabilities → candidate log-likelihoods
             → correct-minus-competitor margin
             ├─→ reversion rate and rule effect
             ├─→ base-model risk → instruct-model prediction
             └─→ margins over example counts → k* → survival summary
```

These branches answer different questions. An AUROC does not tell you how many examples adaptation takes. A Kaplan–Meier median does not tell you how trustworthy a predicted probability is.

### 1.1 Essential notation

| Symbol | Meaning in this experiment |
|---|---|
| $i$ | One eligible decision site |
| $c_i$ | Correct spelling under the supplied mapping |
| $q_i$ | Familiar competitor spelling |
| $x_i$ | Exact output prefix before the decision |
| $r_i$ | Mapping specification or token table in the prompt |
| $\theta$ | The language model's fixed parameters |
| $\ell(c_i)$ | Log-likelihood assigned to the candidate continuation |
| $M_i$ | Correct-minus-competitor log-likelihood margin |
| $S_i$ | H4 risk score, $-M_i^{\mathrm{base}}$ |
| $Y_i$ | H4 binary label, $\mathbf1[M_i^{\mathrm{instruct}}<0]$ |
| $k$ | Number of worked examples placed in the prompt |
| $k_i^*$ | Estimated first example count where the margin becomes nonnegative |
| $\widehat p_i$ | Calibrated prediction of an instruct-model scoring failure |
| $\widehat{\mathcal S}(t)$ | Survival estimate: fraction not yet reaching the first crossing |

$\mathbf1[A]$ is an **indicator**: it equals 1 if statement $A$ is true and 0 otherwise. A hat, as in $\widehat p$, means an estimate. $\sum$ means add; $\prod$ means multiply.

A **template** is an abstract program. A **site** is a position within a rendered program. Multiple sites can share a template and therefore share sources of difficulty. They are not automatically independent observations.

### 1.2 Three probabilities you must never confuse

1. $P_\theta(\texttt{light}\mid r,x)$: the language model's probability for a token or candidate continuation.
2. $\widehat p_i$: a statistical predictor's estimated chance that the instruct checkpoint will favor the competitor at a site.
3. $p_{\mathrm{test}}$: a statistical testing quantity used when evaluating evidence against a null hypothesis.

They have different denominators, different meanings, and different uses. “The probability is 0.87” is incomplete until you name **the event whose probability you mean**.

---

## 2. Probability, logits, softmax, and logarithms

### 2.1 Conditional probability: the vertical bar

$$
P_\theta(c\mid r,x)
$$

Read this as: “The model's probability of the correct continuation, **given** this rule and this prefix.”

The bar $\mid$ means *given*, not division. Change the rule or prefix and you change the conditional distribution.

**Mental picture:** the same road sign can suggest different turns depending on the junction you are standing at. A probability always belongs to a context.

### 2.2 Logits are not probabilities

At an output position, the model produces one real-valued score $z_v$ for each vocabulary token $v$. These scores are **logits**. They may be negative or positive; they need not sum to one.

Softmax converts them into a distribution:

$$
P_\theta(v\mid h)
=
\frac{\exp(z_v)}
{\sum_{u\in V}\exp(z_u)},
$$

where $V$ is the vocabulary and $h$ is the available context.

Exponentiation makes every weight positive. Division by the total makes the probabilities add to one.

**Teaching example:** logits $(0,1,2)$ produce weights $(1,e,e^2)$ and probabilities approximately $(0.090,0.245,0.665)$. These are shares of one probability budget.

Adding the same constant to every logit changes nothing: the common factor cancels. What matters is their relative size.

### 2.3 Why log-softmax appears in the scorer

Taking the natural logarithm gives:

$$
\log P_\theta(v\mid h)
=
z_v-\log\!\left(\sum_{u\in V}e^{z_u}\right).
$$

For numerical stability, let $z_{\max}=\max_u z_u$ and calculate:

$$
\log P_\theta(v\mid h)
=
(z_v-z_{\max})
-
\log\!\left(\sum_{u\in V}e^{z_u-z_{\max}}\right).
$$

Subtracting the maximum avoids exponentiating very large numbers. This is the idea behind the scorer's `torch.log_softmax`.

A model logit can be positive. A **normalized discrete log probability cannot be positive**, because $0\le P\le1$. Synthetic FakeLM scores in older examples must not be mistaken for normalized likelihoods.

The output projection in the canonical scorer can use fp32 arithmetic to reduce numerical error. That improves measurement precision; it does not remove all floating-point error or prove statistical significance.

### 2.4 What is a logarithm?

$\log$ here means the natural logarithm, $\ln$. It is the inverse of the exponential:

$$
\log(e^a)=a,
\qquad
e^{\log p}=p.
$$

The useful identity is:

$$
\log(ab)=\log a+\log b.
$$

A product of probabilities can therefore become a sum of log probabilities.

| Probability | Natural log | Negative log, or surprise |
|---:|---:|---:|
| $1$ | $0$ | $0$ |
| $0.5$ | $-0.693$ | $0.693$ |
| $0.1$ | $-2.303$ | $2.303$ |
| $0.01$ | $-4.605$ | $4.605$ |

The unit of a natural-log quantity is a **nat**. With base-2 logarithms, the unit would be a bit.

**Mental picture:** negative log probability is a surprise meter. An expected event produces little surprise; a very unlikely event produces a large reading.

**Say it aloud:** “The model emits logits; log-softmax turns them into normalized log probabilities, which we add when scoring a multi-token continuation.”

---

## 3. Likelihood, negative log-likelihood, cross-entropy, and perplexity

These terms are connected. They are not four unrelated tricks.

### 3.1 From one token to a sequence: the chain rule

For a continuation $y=(y_1,\ldots,y_K)$:

$$
P_\theta(y\mid h)
=
\prod_{j=1}^{K}
P_\theta(y_j\mid h,y_{<j}).
$$

$y_{<j}$ means the continuation tokens before token $j$. This follows from the probability chain rule; it does **not** assume the tokens are independent.

Taking logs:

$$
\ell_\theta(y\mid h)
=
\log P_\theta(y\mid h)
=
\sum_{j=1}^{K}
\log P_\theta(y_j\mid h,y_{<j}).
$$

**Teaching example:** three observed tokens have conditional probabilities $0.5,0.2,0.1$. The sequence probability is $0.01$. Its log-likelihood is:

$$
\log(0.5)+\log(0.2)+\log(0.1)
=
\log(0.01)
=
-4.605.
$$

Logs make long products easier to calculate and less susceptible to numerical underflow.

### 3.2 Teacher forcing

When scoring a candidate, the scorer provides that candidate's preceding tokens to evaluate each next token. This is **teacher forcing**.

You are asking: “How much support does the model assign to this supplied continuation?” You are not asking the model to freely choose every preceding token.

**Mental picture:** reading a completed route to a driver and asking how plausible each turn is, rather than watching the driver choose a route unaided.

### 3.3 Why the scorer starts at the first token divergence

Tokenize `prefix + correct` and `prefix + competitor` together on each side. Let $d$ be the first token position where the two sequences differ. Their shared token prefix is $h$.

The actual contrast is:

$$
M
=
\sum_{j=d}^{L_c-1}\log P_\theta(c_j\mid h,c_{d:j-1})
-
\sum_{j=d}^{L_q-1}\log P_\theta(q_j\mid h,q_{d:j-1}).
$$

$L_c$ and $L_q$ are the total tokenized lengths of the two sides. All tokens **from the divergence to the end of each candidate** are scored, not just the first token unless each tail is one token.

Shared-token contributions cancel. Joint tokenization also handles a tokenizer merging characters across the prefix/candidate boundary.

This does **not** remove every length effect. A longer candidate tail has more probability factors. Length and token-count baselines are still needed.

The code refuses identical tokenizations, a zero-length tail on either side, and pairs without a usable shared context. An unscorable contrast is not assigned a fake margin of zero.

Implementation: [canonical candidate scorer](../src/phase3_2/margins.py).

### 3.4 What “likelihood” means

When you fix the model and vary the possible continuation, you discuss a probability. When you fix observed data and consider how different parameter values explain it, the same expression is a **likelihood function** of those parameters.

In this experiment, the language model is already trained. We evaluate its likelihoods; we do not train its weights using these programs.

### 3.5 Negative log-likelihood: turn support into a loss

$$
\operatorname{NLL}(y)
=
-\ell_\theta(y)
=
-\sum_j\log P_\theta(y_j\mid h,y_{<j}).
$$

A minus sign makes a quantity we want to maximize into one we want to minimize.

- High assigned likelihood: low NLL.
- Low assigned likelihood: high NLL.

In the worked development example:

$$
\operatorname{NLL}(c)=4.096,
\qquad
\operatorname{NLL}(q)=1.620.
$$

The model regards the correct spelling as more surprising.

**Important:** NLL is not an error rate. A high-NLL program can be semantically correct. A low-NLL program can express the wrong task very fluently.

### 3.6 Where cross-entropy comes from

Suppose $Q(v)$ is a target distribution over tokens, and $P(v)$ is the model's predicted distribution. Cross-entropy is:

$$
H(Q,P)=-\sum_{v\in V}Q(v)\log P(v).
$$

It averages the surprise assigned by $P$ to outcomes expected under $Q$.

For a one-hot target—the observed token $v^*$ has target probability 1 and every other token has target probability 0—this becomes:

$$
H(Q,P)=-\log P(v^*).
$$

That is exactly the one-token NLL. Summing these losses gives sequence NLL; averaging gives mean token cross-entropy.

The conceptual identity is:

$$
H(Q,P)=H(Q)+D_{\mathrm{KL}}(Q\Vert P),
$$

where:

$$
H(Q)=-\sum_vQ(v)\log Q(v),
\qquad
D_{\mathrm{KL}}(Q\Vert P)
=
\sum_vQ(v)\log\frac{Q(v)}{P(v)}.
$$

$H(Q)$ is the target's own uncertainty. The nonnegative KL term measures mismatch between the target and the prediction. Thus cross-entropy rewards putting probability where observed outcomes occur.

You do not need to compute KL separately for this experiment. It explains why cross-entropy is a sensible probability-learning objective.

### 3.7 The whole-program NLL baseline

The pipeline also asks whether a simpler measure of general program unfamiliarity predicts failure.

For tokenized program $w_1,\ldots,w_L$, its implementation computes:

$$
\operatorname{NLL}_{\mathrm{program}}
=
-\sum_{j=2}^{L}\log P_\theta(w_j\mid w_{<j}).
$$

The first token is not scored because this particular implementation supplies no preceding token context for it.

The H4 baseline uses:

$$
\operatorname{NLL}_{\mathrm{char}}
=
\frac{\operatorname{NLL}_{\mathrm{program}}}
{\text{number of characters in the program}}.
$$

Character normalization helps separate program length from total surprise. It does not eliminate every tokenizer or model comparability issue.

**Mental picture:** whole-program NLL asks whether the entire road network looks unfamiliar; exact-site risk asks whether this particular junction pulls the driver toward a specific wrong turn.

### 3.8 Perplexity: useful background, not a listed primary endpoint

For mean token NLL $\overline L$:

$$
\operatorname{PPL}=\exp(\overline L).
$$

If the three-token teaching example has NLL $4.605$, then $\overline L=4.605/3$ and perplexity is about $4.64$.

Perplexity can be imagined as an effective branching difficulty per token. It is not literally a count of equally likely choices in every situation.

This experiment does not list perplexity as a main endpoint. Do not exponentiate **NLL per character** and call the result ordinary token perplexity. Token perplexities across different tokenizers also need careful interpretation.

**Say it aloud:** “Cross-entropy and NLL penalize probability assigned away from observed outcomes. Here we use those probabilities to measure candidate preference, not to retrain the language model.”

---

## 4. Margin, risk, reversion rate, and the rule effect

### 4.1 Why subtract the two log-likelihoods?

$$
M_i=\ell(c_i)-\ell(q_i)
=
\log\frac{P(c_i)}{P(q_i)}.
$$

Subtraction creates a direct contrast between the two alternatives.

- $M_i>0$: correct continuation has greater likelihood.
- $M_i<0$: competitor has greater likelihood.
- $M_i=0$: equal likelihood.

The worked example gives:

$$
M_{\mathrm{base}}
=
-4.096-(-1.620)
=
-2.476.
$$

Exponentiate to interpret its scale:

$$
\frac{P(c)}{P(q)}=e^{-2.476}\approx0.084,
\qquad
\frac{P(q)}{P(c)}\approx11.9.
$$

The competitor has about 11.9 times the candidate likelihood. This is a relative comparison, not an 11.9-times probability of whole-program failure.

In NLL notation:

$$
M=\operatorname{NLL}(q)-\operatorname{NLL}(c).
$$

**Mental picture:** a balance with correct on one side and competitor on the other. Zero is balanced; the sign tells you which side wins.

### 4.2 Why does risk reverse the sign?

For H4:

$$
S_i=-M_i^{\mathrm{base}}
=
\ell_{\mathrm{base}}(q_i)-\ell_{\mathrm{base}}(c_i).
$$

Risk is oriented so that **larger means more danger**. The example has $S=2.476$.

The outcome label comes from a different checkpoint:

$$
Y_i=\mathbf1[M_i^{\mathrm{instruct}}<0].
$$

The instruct margin is approximately $-0.034$, so $Y=1$.

If you used the same model's margin both to define risk and to define its label, the ranking task would be largely built into the definitions. H4 instead tests whether the base checkpoint predicts its instruct sibling.

### 4.3 Reversion rate and prevalence

For $n$ eligible scored sites:

$$
\widehat r
=
\frac1n\sum_{i=1}^{n}\mathbf1[M_i<0].
$$

**Teaching example:** 43 negative margins among 100 sites give $\widehat r=0.43$.

This is the proportion of **pairwise scoring reversions**. It is not automatically the proportion of generated programs that fail.

For H4, positive prevalence is:

$$
\widehat\pi=\frac1n\sum_iY_i.
$$

Always state the denominator: which model, grammar, mappings, conditions, eligible sites, and exclusions? Forty percent in one restricted population need not mean forty percent in another.

Exact $M=0$ is not counted as a reversion by the strict inequality. The code's nonnegative crossing convention includes such ties.

### 4.4 Paired rule effect

For the same site under two prompt conditions:

$$
D_i=M_{i,\mathrm{rule}}-M_{i,\mathrm{control}},
\qquad
\overline D=\frac1n\sum_iD_i.
$$

Pairing holds the site fixed. It removes much of the variation caused by some sites being intrinsically harder than others.

The worked example has:

$$
D_{\mathrm{norule}}
=
-2.476-(-4.361)
=
1.885,
$$

$$
D_{\mathrm{length\ control}}
=
-2.476-(-4.738)
=
2.262.
$$

The table helps, but the final margin remains negative.

Why exponentiate the first difference?

$$
e^{D_i}
=
\frac{P_{\mathrm{rule}}(c_i)/P_{\mathrm{rule}}(q_i)}
{P_{\mathrm{control}}(c_i)/P_{\mathrm{control}}(q_i)}.
$$

Here $e^{1.885}\approx6.6$: the **correct-versus-competitor likelihood ratio** improves by about 6.6 times. This does not say the absolute probability of the correct candidate increases by that factor. For an average log effect, exponentiation describes a geometric-mean ratio change.

The length-matched control addresses the fact that the token table adds context as well as information. Matching is approximate and neutral padding has assumptions; it is a control for a confound, not magical isolation of every prompt effect.

**Say it aloud:** “The rule moves the preference toward the correct spelling, but a positive rule effect does not imply that the correct spelling ultimately wins.”

---

## 5. Sigmoid calibration: where the function comes from

### 5.1 Begin with odds

For a binary event with probability $p$:

$$
\operatorname{odds}(p)=\frac{p}{1-p}.
$$

If $p=0.8$, the odds are $4$: four events for each non-event in a population with that rate.

Odds are not probabilities: $p=0.5$ corresponds to odds 1, not odds 0.5.

Taking logs gives the **logit**:

$$
\operatorname{logit}(p)=\log\frac{p}{1-p}.
$$

Probability is restricted to $(0,1)$, but log-odds can range over all real numbers.

### 5.2 A simple statistical model

Assume the failure log-odds are a linear function of risk:

$$
\operatorname{logit}(\widehat p)=a+bS.
$$

Write $z=a+bS$. Solve for $\widehat p$:

$$
\frac{\widehat p}{1-\widehat p}=e^z,
$$

$$
\widehat p=e^z(1-\widehat p),
$$

$$
\widehat p(1+e^z)=e^z,
$$

$$
\boxed{
\widehat p=\frac{e^z}{1+e^z}
=
\frac1{1+e^{-z}}
=
\sigma(z)
}.
$$

The sigmoid is therefore not an arbitrary curve pasted onto the score. It is the inverse of log-odds under a linear-logit assumption.

| $z$ | $\sigma(z)$ |
|---:|---:|
| $-2$ | $0.119$ |
| $0$ | $0.500$ |
| $2$ | $0.881$ |

$a$ shifts the curve; $b$ controls its steepness and direction. If $b>0$, higher risk produces higher failure probability. A one-unit risk increase multiplies modeled failure odds by $e^b$.

The derivative is:

$$
\sigma'(z)=\sigma(z)[1-\sigma(z)].
$$

The curve is most responsive near its middle and flattens near 0 and 1.

### 5.3 How are a and b learned?

Development supplies paired observations $(S_i,Y_i)$. The binary likelihood is:

$$
L(a,b)
=
\prod_i
\widehat p_i^{Y_i}(1-\widehat p_i)^{1-Y_i}.
$$

Maximizing this is equivalent to minimizing binary NLL:

$$
\mathcal L(a,b)
=
-\sum_i
\left[
Y_i\log\widehat p_i
+
(1-Y_i)\log(1-\widehat p_i)
\right].
$$

This is **binary cross-entropy**. An observed failure ($Y=1$) penalizes $-\log\widehat p$; an observed non-failure ($Y=0$) penalizes $-\log(1-\widehat p)$.

The conceptual gradient is:

$$
\frac{\partial\mathcal L}{\partial a}
=
\sum_i(\widehat p_i-Y_i),
\qquad
\frac{\partial\mathcal L}{\partial b}
=
\sum_iS_i(\widehat p_i-Y_i).
$$

These residuals tell the fitting algorithm how the predictions differ from outcomes. The repository uses Newton-style updates with numerical stabilization. Only two statistical parameters are fitted per development pair; the LLM weights remain unchanged.

### 5.4 Work through the actual development example

Using rounded fitted values:

$$
a=-0.2984,\qquad b=0.9014,\qquad S=2.476,
$$

$$
z=-0.2984+0.9014(2.476)\approx1.934,
$$

$$
\widehat p=\frac1{1+e^{-1.934}}\approx0.874.
$$

This predicts the **instruct model's forced-prefix label**, not the base model's next-token probability.

The three distinct values at this example are:

| Quantity | Approximate value | Event |
|---|---:|---|
| Full-vocabulary model probability | $e^{-4.096}=0.0166$ | Base model assigns the token `light` |
| Pair-normalized candidate probability | $\sigma(-2.476)=0.0775$ | Correct candidate conditional on these two alternatives |
| H4 calibrated failure prediction | $\sigma(-0.2984+0.9014S)=0.874$ | Instruct model has a negative candidate margin |

The second identity follows from:

$$
\frac{P(c)}{P(c)+P(q)}
=
\frac1{1+P(q)/P(c)}
=
\sigma(M).
$$

It applies to the compared token continuations, not all possible outputs. $\sigma(M)$ is **not** automatically the H4 calibration function.

### 5.5 What calibration promises—and does not

If predictions around 0.8 are well calibrated in the evaluated population, approximately 80% of those sites should have $Y=1$. A single correct prediction cannot establish calibration.

A sigmoid produces a number in $(0,1)$, but that alone does not make it an accurate probability. Distribution shifts, incorrect functional assumptions, and overfitting can break calibration.

**Mental picture:** the base score is an instrument reading. Calibration paints probability markings on its gauge. A gauge can be correctly ordered but have inaccurate numbers.

**Say it aloud:** “Platt-style calibration fits a logistic relationship between base-model risk and instruct-model failures using development labels; it does not train the language model.”

## 6. Thresholds and probability-quality diagnostics

### 6.1 The alarm line

A calibrated probability and a binary decision are different outputs:

$$
\widehat Y_i=\mathbf1[\widehat p_i\ge\tau].
$$

The worked development threshold is about $\tau=0.364$. Its predicted probability $0.874$ is above the threshold, so the predictor issues a failure warning.

Do not confuse:

- $M_i^{\mathrm{instruct}}<0$: the definition of the observed label.
- $\widehat p_i\ge\tau$: the rule for a predicted label.

Neither rule changes the model's generated text.

### 6.2 Confusion matrix and Youden's criterion

| | Actual failure, $Y=1$ | Actual non-failure, $Y=0$ |
|---|---:|---:|
| Warn, $\widehat Y=1$ | True positive, TP | False positive, FP |
| Do not warn, $\widehat Y=0$ | False negative, FN | True negative, TN |

$$
\operatorname{TPR}
=
\frac{\mathrm{TP}}{\mathrm{TP}+\mathrm{FN}},
\qquad
\operatorname{FPR}
=
\frac{\mathrm{FP}}{\mathrm{FP}+\mathrm{TN}}.
$$

TPR is also **recall** or **sensitivity**. Specificity is $1-\operatorname{FPR}$.

The development cutoff maximizes:

$$
J(\tau)=\operatorname{TPR}(\tau)-\operatorname{FPR}(\tau),
\qquad
\tau^*=\underset{\tau}{\operatorname{argmax}}\,J(\tau).
$$

It seeks separation between warnings on failures and warnings on non-failures. It need not maximize ordinary accuracy or reflect a particular real-world cost of an error. That is why the cutoff need not be 0.5.

The implementation searches the distinct observed development probabilities. If several cutoffs have exactly the same best Youden value, it retains the smallest cutoff.

**Mental picture:** moving the alarm line downward catches more real hazards but also triggers more false alarms. Development chooses its position; freezing seals it.

### 6.3 Brier score: how wrong are the probabilities?

$$
\operatorname{Brier}
=
\frac1n\sum_i(\widehat p_i-Y_i)^2.
$$

For the worked site with $Y=1$ and $\widehat p\approx0.874$, its contribution is:

$$
(0.874-1)^2\approx0.0159.
$$

A confident wrong prediction, $\widehat p=0.01$ when $Y=1$, contributes about $0.9801$.

Lower is better. Brier measures overall probability error, involving both calibration and discrimination; it is not a pure calibration measure.

Binary cross-entropy is another probability loss. It penalizes confident mistakes particularly strongly: $-\log(0.01)=4.605$ when the event occurs. Brier uses squared distance; cross-entropy uses surprise.

### 6.4 Expected calibration error: inspect the gauge markings

Split predictions into probability bins. For bin $b$, define:

$$
\overline p_b=\frac1{n_b}\sum_{i\in b}\widehat p_i,
\qquad
\overline Y_b=\frac1{n_b}\sum_{i\in b}Y_i.
$$

Then:

$$
\operatorname{ECE}
=
\sum_b\frac{n_b}{n}
\left|\overline p_b-\overline Y_b\right|.
$$

**Teaching example:** a bin of 20 sites has mean predicted probability 0.8, but 12 failures, so observed frequency is 0.6. Its calibration gap is 0.2; its ECE contribution is $(20/n)(0.2)$.

The code uses ten equal-width bins. Empty bins contribute nothing. The observed frequency is **failure frequency**, not thresholded accuracy.

ECE depends on the binning and can hide problems inside a bin. A low ECE from small samples or coarse bins is not proof of perfect calibration.

### 6.5 Calibration intercept and slope

A separate diagnostic regression asks:

$$
P(Y_i=1\mid\widehat p_i)
=
\sigma\!\left(\alpha_{\mathrm{cal}}
+
\beta_{\mathrm{cal}}\operatorname{logit}(\widehat p_i)\right).
$$

Ideal values are:

$$
\alpha_{\mathrm{cal}}=0,
\qquad
\beta_{\mathrm{cal}}=1.
$$

Roughly, a slope below 1 indicates probability estimates that are too extreme; a slope above 1 indicates estimates that are too compressed, after accounting for the intercept.

These diagnostic parameters are not the original development parameters $a,b$. Fitting the diagnostic on evaluation outcomes measures calibration; using it to replace the frozen predictor would be recalibration.

Near-perfect diagnostic calibration on the **same rows used to fit** $a,b$ is not independent evidence of generalization.

**Say it aloud:** “A threshold decides when to warn. Brier and calibration diagnostics ask whether the probability numbers behind those warnings are reliable.”

---

## 7. AUROC: ranking dangerous sites without choosing one cutoff

### 7.1 Why accuracy alone is not enough

If only 5% of sites fail, always predicting “no failure” gives 95% accuracy and catches no failures. Also, accuracy changes when you move the cutoff.

H4 asks a more basic question:

> Does the base score put instruct-model failures above instruct-model non-failures?

That is a ranking question.

### 7.2 What ROC means

ROC means **receiver operating characteristic**, a name inherited from signal detection.

For every possible score cutoff, calculate:

- horizontal coordinate: FPR;
- vertical coordinate: TPR.

Lowering the cutoff admits more sites. Plotting the resulting pairs traces a curve from $(0,0)$ toward $(1,1)$.

A useful score rises toward high TPR while keeping FPR low. A non-informative score has a diagonal reference curve.

### 7.3 What the area means

AUROC is the **area under the ROC curve**. Its pairwise interpretation is:

$$
\operatorname{AUROC}
=
P(S^+>S^-)
+
\frac12P(S^+=S^-),
$$

where $S^+$ is a score from an actual failure and $S^-$ from an actual non-failure.

For a finite dataset:

$$
\widehat A
=
\frac1{n_+n_-}
\sum_{i:Y_i=1}\sum_{j:Y_j=0}
\left[
\mathbf1[S_i>S_j]
+
\frac12\mathbf1[S_i=S_j]
\right].
$$

Every positive-negative pair votes. A correct ordering earns 1, a reversed ordering earns 0, and a tie earns half.

The empirical ROC area equals this pairwise statistic, which is closely connected to the Mann–Whitney rank statistic.

### 7.4 Worked teaching example

Actual failures have risks $2.5$ and $1.0$. Actual non-failures have risks $1.8$ and $-1.2$.

| Failure score | Non-failure score | Ranking credit |
|---:|---:|---:|
| 2.5 | 1.8 | 1 |
| 2.5 | −1.2 | 1 |
| 1.0 | 1.8 | 0 |
| 1.0 | −1.2 | 1 |

$$
\widehat A=\frac{3}{4}=0.75.
$$

Interpretation: in 75% of these failure/non-failure comparisons, the score ranks the failure higher.

- AUROC 1: perfect ordering in the evaluated sample.
- AUROC 0.5: no directional ranking advantage.
- AUROC below 0.5: the score tends to rank in the wrong direction.
- Only one outcome class: AUROC is undefined, not zero.

AUROC 0.9 does **not** mean 90% accuracy or a 90% chance that every high-risk site fails.

**Mental picture:** line up road junctions from safest to most dangerous, then repeatedly compare one accident junction with one non-accident junction.

### 7.5 Why AUROC suits H4—and its limitations

AUROC evaluates the ranking before you choose a deployment cutoff. A strictly increasing transformation of risk preserves ordering and AUROC. It can therefore work even when the probability gauge needs calibration.

It does not guarantee useful precision at a chosen budget. It also does not prove the causal mechanism behind the ranking.

Pooling different lexicons can give good separation because whole lexicons differ. **Within-lexicon AUROC** asks whether the predictor distinguishes sites inside the same mapping, rather than merely sorting easy mappings below hard ones.

### 7.6 The mandatory baselines

| Baseline | What the code uses | Why compare with it? |
|---|---|---|
| Identity | Indicator that correct and competitor differ | Could any respelling alone explain the result? |
| Length | Competitor UTF-8 byte length minus correct byte length | Could spelling length explain it? |
| Program NLL | Base-model whole-program NLL per character | Could general unfamiliarity explain it? |
| Token count | Sum of the two scored candidate-tail token counts | Could tokenization burden explain it? |

On the SEMANTIC-only eligible set, correct and competitor differ at every site. Identity is therefore constant. With both label classes present, its AUROC is exactly 0.5.

The current C1 and C2 requirements are:

$$
\Delta A_{\mathrm{id}}
=
A_{\mathrm{risk}}-A_{\mathrm{id}}
\ge0.10,
$$

$$
\Delta A_{\mathrm{length}}
=
A_{\mathrm{risk}}-A_{\mathrm{length}}
\ge0.05,
$$

with uncertainty intervals above zero and the specified multiplicity correction.

C1 consequently requires a point AUROC of at least 0.60. **An interval above zero for the difference does not mean its lower bound exceeds the full practical target of 0.10.** These are two separate requirements.

The broader scientific case also compares the other mandatory baselines. Passing C1/C2 is not synonymous with passing an unseen-grammar criterion: C3 remains untestable in this repository.

**Say it aloud:** “AUROC is the chance that a randomly selected failure receives more risk than a randomly selected non-failure, counting ties as half.”

---

## 8. Precision, recall, average precision, and ties

### 8.1 Precision and recall ask different questions

$$
\operatorname{Precision}
=
\frac{\mathrm{TP}}{\mathrm{TP}+\mathrm{FP}},
\qquad
\operatorname{Recall}
=
\frac{\mathrm{TP}}{\mathrm{TP}+\mathrm{FN}}.
$$

Precision: “Among the warnings, how many are real failures?”

Recall: “Among the real failures, how many were warned about?”

**Mental picture:** precision is how clean your catch is; recall is how much of the target population you caught.

### 8.2 The field named AUPRC is average precision here

As the score threshold falls, recall increases. The implementation calculates **stepwise average precision**, often abbreviated AP:

$$
\operatorname{AP}
=
\sum_j(R_j-R_{j-1})P_j.
$$

Here $j$ indexes distinct score thresholds, $R_j$ is recall and $P_j$ precision after admitting that score group.

It is a weighted average of precision, where the weight is the extra recall obtained. It is not trapezoidal integration of precision-recall points.

For the previous teaching example, descending labels are $1,0,1,0$. The positives arrive at ranks 1 and 3:

$$
\operatorname{AP}
=
\frac12(1)
+
\frac12\left(\frac23\right)
=
\frac56
\approx0.833.
$$

The intervening negative lowers precision but adds no recall.

Positive prevalence is the PR reference level. A constant score gives AP equal to prevalence. Do not interpret a PR score without knowing how common failures are.

### 8.3 Why ties must enter together

If two rows have equal risk, the predictor cannot order them. A metric should not reward a favorable spreadsheet row order.

The code admits the entire equal-score group at once. This is why changing row order should not change AP.

**Teaching example:** risks $(3,2,2,1)$ with labels $(1,0,1,0)$ have AP $5/6$ and AUROC $7/8$. The score-2 failure ties one non-failure.

### 8.4 Precision at a limited repair budget

For the highest $K$ scores:

Here $K=\min(k,n)$, so a requested top-50 metric cannot select more than the available $n$ sites.

$$
P@K=\frac{\text{failures among the selected }K}{K}.
$$

The experiment reports budgets such as 10 and 50.

When a tie straddles the boundary, the implementation uses expected precision under uniform selection from the tied group:

$$
P@K
=
\frac{
p_{\mathrm{above}}
+
(K-a)\,p_{\mathrm{tie}}/g
}{K},
$$

where $a$ sites lie strictly above the tie, that tie has $g$ sites, and $p_{\mathrm{tie}}$ are failures.

For the tied example and $K=2$, the score-3 failure is selected, then one of the two score-2 sites:

$$
P@2=\frac{1+\frac12}{2}=0.75.
$$

AUPRC/AP and $P@K$ help answer whether a ranking is useful when failures are uncommon or only a few sites can receive attention.

**Say it aloud:** “AUROC assesses broad pairwise ordering; average precision and precision at a budget describe the quality of the warnings near the top of the list.”

---

## 9. The primary endpoint: the extinction threshold k*

### 9.1 What is an endpoint?

An **endpoint** is a predefined quantity the experiment measures. A **hypothesis** is a claim about one or more such quantities.

Here, $k^*$ is the adaptation endpoint: how many worked examples are needed before the margin first becomes nonnegative. H4 is a prediction claim assessed using ranking metrics.

“Primary endpoint” does not mean “the only number worth reporting.”

### 9.2 What changes as k increases?

The mapping table remains present. More worked programs in the same mapping are inserted into the prompt:

$$
k\in\{0,1,2,4,8,16,32\}.
$$

The example order is fixed and nested: the two-example prompt contains the first example plus one more.

This is **in-context adaptation**, not gradient training. $k=0$ means no worked examples, not no rule table.

The word “extinction” describes the operational disappearance of competitor preference. It does not claim permanent erasure of a learned neural habit.

### 9.3 From the ladder to a crossing

The worked development curve is:

| Worked examples $k$ | 0 | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Margin $M(k)$ | −2.476 | −1.651 | +0.702 | +0.403 | −1.104 | −1.496 | +3.014 |

The first tested nonnegative margin is at two examples. The specified endpoint interpolates between the preceding two tested rungs.

Draw a straight line through $(k_{j-1},M_{j-1})$ and $(k_j,M_j)$:

$$
\widetilde M(k)
=
M_{j-1}
+
\frac{k-k_{j-1}}{k_j-k_{j-1}}
(M_j-M_{j-1}).
$$

Set the line equal to zero and solve:

$$
k^*
=
k_{j-1}
+
(k_j-k_{j-1})
\frac{-M_{j-1}}{M_j-M_{j-1}}.
$$

For this site:

$$
k^*
=
1+(2-1)\frac{1.651}{0.702+1.651}
\approx1.70.
$$

**Mental picture:** a water level is below a marked line at one measurement and above it at the next. A straight segment estimates where it crossed the line.

Nobody supplied 1.70 physical examples. This is a fractional estimate from a measured ladder, not an observed fractional prompt.

### 9.4 The complete convention

$$
k_i^*=
\begin{cases}
0, & M_i(0)\ge0,\\
\text{interpolated first upward crossing}, & \text{a crossing is observed},\\
\text{unobserved; right-censored at }k_{\max}, & \text{otherwise}.
\end{cases}
$$

A zero margin counts as nonnegative. Already-correct sites are events at zero, not missing observations.

A no-crossing site has not been shown to need exactly 32 examples or infinitely many examples. We know only that no upward crossing appeared on its tested ladder.

### 9.5 First crossing is not sustained success

The example crosses near 1.70, then becomes negative again at 8 and 16.

Its diagnostics differ:

- `nonmonotone=True`: some adjacent margin decreases.
- `recrossed_down=True`: it returns below zero after a crossing.
- `sustained_k=32`: 32 is the first tested rung from which the remaining tested margins are all nonnegative.

A nonmonotone curve can stay positive at every rung. Therefore, “93% of curves wobble” does not mean “93% cross back into failure.”

A first crossing remains an observed event even after a later reversal. `sustained_k` only refers to the remaining **observed** rungs; it promises nothing beyond 32 examples.

### 9.6 What interpolation assumes

Interpolation chooses a straight-line approximation on the **example-count scale**. The exact fractional crossing depends on the margin scale: nonlinear transformations can change it even when they preserve signs.

The sparse ladder can miss crossings at untested counts, especially for nonmonotone curves. The implemented $k^*$ is a reproducible ladder-based estimate, not exact observation of an underlying continuous adaptation time.

**Say it aloud:** “Our extinction threshold is an interpolated first nonnegative margin on a fixed demonstration ladder; we report recrossing and sustained diagnostics because that first switch may not last.”

---

## 10. Kaplan–Meier median and censoring

This is the mathematical answer to: **how do we summarize adaptation when some sites never switch during the observation window?**

### 10.1 Why not just average the sites that switched?

Imagine timing runners. Some finish before the stopwatch is turned off; some are still running. If you average only finishers, you remove the slowest cases and make the race look easier.

Similarly, dropping every no-crossing site removes difficult adaptation cases.

Setting them all to 32 is also wrong: “not observed by 32” is not “switched at 32.”

### 10.2 Right-censoring is partial information

For a site, record an observed time $u_i$ and an event indicator $\delta_i$:

$$
u_i=
\begin{cases}
k_i^*, & \delta_i=1,\\
k_{\max,i}, & \delta_i=0,
\end{cases}
$$

$$
\delta_i=\mathbf1[\text{first crossing observed}].
$$

For the main ladder, $k_{\max}=32$. A censored site provides information through that observation horizon; its later crossing time is unknown.

A crashed, unscorable, or missing curve is **not** evidence that the model never switched. In the current export, unmeasurable curves are excluded with their status rather than silently converted into no-crossing censoring.

### 10.3 What does survival mean here?

Define:

$$
\mathcal S(t)=P(k^*>t).
$$

It is the probability that the **first crossing has not occurred** by example count $t$.

In ordinary survival analysis, the event might be equipment failure. Here the event is beneficial: a first nonnegative margin. “Survival” means the old preference has not yet been extinguished by this endpoint's definition.

It does not mean the current margin is negative. Once a site crosses, a later relapse does not undo that first-crossing event.

### 10.4 Derive the product-limit estimator

At each distinct event time $t_j$:

- $n_j$: sites still under observation and not yet crossed immediately before $t_j$;
- $d_j$: crossings at $t_j$.

The estimated fraction avoiding a crossing at that step is:

$$
1-\frac{d_j}{n_j}.
$$

To avoid crossing through several steps, you must survive each step. Multiply their conditional survival fractions:

$$
\boxed{
\widehat{\mathcal S}(t)
=
\prod_{t_j\le t}
\left(1-\frac{d_j}{n_j}\right)
}.
$$

This is Kaplan–Meier, also called the **product-limit estimator**.

Censoring does not create a downward jump. It removes a site from later risk sets. A censored site is not held in the denominator after observation stops.

With a common censoring horizon and no earlier censoring, the curve before that horizon simplifies to the fraction of original sites not yet crossed. The general formula also handles different observation horizons.

### 10.5 Work through five sites

**Teaching example:** first crossings occur at 1.7, 3.2, 6.0, and 12.5; the fifth site is censored at 32.

| Time | At risk before event | Crossings | Survival after step |
|---:|---:|---:|---:|
| 1.7 | 5 | 1 | $1(4/5)=0.8$ |
| 3.2 | 4 | 1 | $0.8(3/4)=0.6$ |
| 6.0 | 3 | 1 | $0.6(2/3)=0.4$ |
| 12.5 | 2 | 1 | $0.4(1/2)=0.2$ |
| 32 | 1 | 0; one censor | $0.2$, unchanged |

The censored site contributes to all the preceding risk sets. It has not been discarded.

### 10.6 What is the Kaplan–Meier median?

$$
\widehat m
=
\inf\{t:\widehat{\mathcal S}(t)\le0.5\}.
$$

Read this as: “The first example count where no more than half the population remains without a first crossing.”

The teaching example drops from 0.6 to 0.4 at $t=6.0$, so its Kaplan–Meier median is **6.0**.

This is not the average of all crossing times. It is the 50% crossing point of the estimated survival distribution.

If survival never reaches 0.5, report **median not reached within the observation window**. Do not invent a median of 32 or infinity.

### 10.7 Two populations give two legitimate answers

- **ALL_SITES:** includes sites with $M(0)\ge0$ as events at zero. If at least half are already nonnegative, the median can be zero.
- **INITIALLY_WRONG:** restricts to sites with $M(0)<0$. It asks how long initially failing sites take to first switch.

The companion's main adaptation summaries use the initially-wrong population. Different models can have different initially-wrong sets; this matters when comparing their medians.

Censoring rate is:

$$
\widehat c
=
\frac{n_{\mathrm{censored}}}{n_{\mathrm{population}}}.
$$

A median and a censoring rate answer different questions. A median of four examples can coexist with a substantial minority that never crosses by 32.

### 10.8 A small correction to the companion's median illustration

Dropping the censored site leaves crossing times $1.7,3.2,6.0,12.5$.

- Ordinary arithmetic median of these four numbers: $(3.2+6.0)/2=4.6$.
- Kaplan–Meier median recomputed on those four complete observations: 3.2, because survival reaches exactly 0.5 at the second event.

The companion says dropping the site gives 3.2. That describes the second convention. The code's `median_among_crossers` diagnostic uses the first and would report **4.6**.

Both are smaller than the censor-aware median 6.0. Name the convention rather than mixing them.

### 10.9 Assumptions and the measurement window

Kaplan–Meier avoids assuming a specific event-time distribution, such as an exponential or normal distribution. It still needs defensible observation and censoring assumptions.

A predetermined administrative stop at 32 is easier to justify than dropping difficult cases early. Outcome-dependent dropout can bias survival estimation.

The current implementation treats interpolated crossing times as exact input times. It is not an interval-censored estimator, and it does not solve the uncertainty about untested demonstration counts. Correlated sites require clustered uncertainty estimates, discussed next.

**Mental picture:** the survival curve is a staircase counting how many runners have not yet finished; a censor says “we stopped watching this runner,” not “this runner finished.”

**Say it aloud:** “We use a Kaplan–Meier median so no-crossing sites contribute their observed information instead of being dropped or assigned a false crossing time.”

## 11. Cluster bootstrap and confidence intervals

### 11.1 Why uncertainty exists even with deterministic model scoring

A score can be reproducible while its summary depends on which programs were evaluated. The uncertainty here is largely about variation across cases, not a claim that the same GPU calculation randomly changes every time.

An estimate $\widehat\psi$—a rate, rule effect, AUROC, or median—is calculated from a finite collection of templates. Another defensible collection could give a different estimate.

### 11.2 Why not treat every site as independent?

Sites from one template share syntax, task structure, identifiers, and context. They resemble siblings.

**Mental picture:** surveying twenty people from one household is not equivalent to surveying twenty households. A shared household circumstance can influence all twenty answers.

The cluster unit is the **template**. Grammar families such as `dom` and `blk` are analyzed separately; they are not the “families” being resampled.

### 11.3 The bootstrap recipe

Suppose there are $G$ eligible template clusters, with all rows of template $g$ denoted $\mathcal D_g$.

For bootstrap replicate $b$:

1. Draw $G$ template indices uniformly **with replacement**.
2. Bring along every row of each selected template.
3. Keep duplicate selections as separate copies.
4. Recompute the statistic.
5. Repeat, usually $B=2000$ times.

Formally:

$$
\mathcal D^{*(b)}
=
\biguplus_{j=1}^{G}\mathcal D_{I_j^{(b)}},
\qquad
\widehat\psi^{*(b)}
=
T(\mathcal D^{*(b)}).
$$

$\biguplus$ emphasizes multiplicity: a cluster drawn twice contributes twice.

If templates A, B, C have rule differences 1, 3, 5 and the resample is A, A, B, its mean is:

$$
\frac{1+1+3}{3}=\frac53.
$$

Deduplicating it into A, B would give 2 and destroy the intended resampling scheme. The code's `_draw` tag preserves copies when pairing conditions.

### 11.4 Where the interval comes from

Sort the valid bootstrap estimates. A 95% percentile interval uses their approximately 2.5th and 97.5th percentiles:

$$
\operatorname{CI}_{95\%}
=
\left[
Q_{0.025}(\widehat\psi^*),
Q_{0.975}(\widehat\psi^*)
\right].
$$

A rule-effect interval entirely above zero supports a positive effect under the method's assumptions. An interval spanning zero does not establish a nonzero effect; it also does not prove no effect exists.

A 95% frequentist confidence procedure is intended to cover the fixed target in 95% of repeated comparable studies. It is not a posterior statement that this fixed target has a 95% probability of lying inside this particular observed interval.

### 11.5 Implementation details that matter

The available template count can be below 80 after filtering. The code requires at least eight clusters for an interval. It skips undefined bootstrap replicates and refuses an interval if fewer than half the requested replicates are usable.

For an AUROC **difference**, risk and baseline are evaluated on the same resampled rows. This preserves the paired comparison. Bootstrapping two independent AUROCs and subtracting unrelated intervals would not represent that same paired design.

Two thousand resamples are two thousand computational views of the original observations, **not two thousand new experiments**. More resamples improve Monte Carlo resolution; they do not add independent templates.

Template resampling preserves the mapping rows inside a template. It does not automatically provide an uncertainty interval over an unrestricted population of new lexicons or grammar families.

**Say it aloud:** “We resample complete templates, retaining their correlated sites and paired conditions, so the uncertainty is not artificially narrowed by counting sibling sites as independent.”

---

## 12. Statistical significance, bootstrap tails, and Holm correction

### 12.1 What is a p-value trying to describe?

A conventional p-value asks how incompatible the observations are with a specified null hypothesis and sampling model. It concerns outcomes at least as extreme as the observed statistic **if that null model were true**.

It is not:

- the probability that the hypothesis is true;
- the probability the paper is wrong;
- the fraction of sites that failed;
- the size or practical value of an effect.

A small p-value with a tiny effect can be scientifically unimportant. A meaningful effect can remain uncertain in a small study.

### 12.2 The implementation's bootstrap tail quantity

For a positive AUROC difference, the code reports:

$$
p_{\mathrm{boot}}
=
\frac{
1+\#\{\widehat\Delta^{*(b)}\le0\}
}{
B_{\mathrm{valid}}+1
}.
$$

It counts how often the resampled difference fails to exceed zero. The $+1$ avoids an exact reported zero.

If all 2000 valid differences are positive:

$$
p_{\mathrm{boot}}=\frac1{2001}\approx0.0004998.
$$

This explains why multiple comparisons can print the same minimum value: the resampling calculation has finite resolution.

This is the repository's **bootstrap tail-based testing quantity**. The draws are centered around the observed data, not generated under a fully specified null-centered experiment. Do not present it as an exact null probability or as mathematical certainty.

### 12.3 Why multiple tests create a problem

If you try many analyses, an apparently impressive result may occur by chance somewhere. The relevant question becomes: “What is the chance of at least one false rejection across this declared collection of tests?”

This is **familywise error**. Here “family” means a set of statistical tests, not a grammar family.

**Mental picture:** buying many lottery tickets changes your chance of winning at least once. Testing many hypotheses changes your opportunity to obtain a lucky small p-value.

### 12.4 The full Holm equation

Sort $m$ input p-values:

$$
p_{(1)}\le p_{(2)}\le\cdots\le p_{(m)}.
$$

Holm-adjusted values are:

$$
\widetilde p_{(i)}
=
\min\!\left(
1,
\max_{j\le i}
\left[(m-j+1)p_{(j)}\right]
\right).
$$

The running maximum is essential.

**Teaching example:** raw values $0.01,0.03,0.04$ give products $0.03,0.06,0.04$, but adjusted values:

$$
0.03,\quad0.06,\quad0.06.
$$

Without the running maximum, a later test could receive an improperly smaller adjusted value.

With two tests both at the bootstrap floor, the adjustment is approximately:

$$
2\left(\frac1{2001}\right)\approx0.001.
$$

Holm protects a specified testing family when its input p-values are valid. It does not repair leakage, a broken metric, or an invalid sampling model.

### 12.5 What gets corrected here?

H4 applies Holm to **C1 and C2 within each pair/family/split group**. It is not a single correction over every pair, both grammars, and every reported metric.

The scale analysis has its own collection of slopes. Exploratory subgroup cuts are not retroactively confirmed just because some adjusted test elsewhere passed.

Be explicit about the correction's scope when presenting “all 20 comparisons passed.”

### 12.6 Significant, meaningful, and equivalent are different

For H4, “difference positive” and “difference at least 0.10” are different propositions. The criteria combine a point-effect target with uncertainty requirements.

Likewise, a nonsignificant scale slope does not establish that model sizes are equivalent. Establishing equivalence requires a justified practical tolerance and an analysis showing the plausible effect lies within that tolerance.

**Say it aloud:** “We report the effect, its uncertainty, and the multiplicity-adjusted testing quantity; none of those should be replaced by the word significant alone.”

---

## 13. Correlation, design effect, effective sample size, and power

### 13.1 Standard deviation versus standard error

Standard deviation describes variability among observations. Standard error describes variability of an **estimator** across comparable samples.

For independent observations with standard deviation $\sigma$, the mean has:

$$
\operatorname{SE}(\overline X)=\frac{\sigma}{\sqrt n}.
$$

The square-root improvement is why quadrupling independent sample size roughly halves the standard error. Correlated observations weaken that improvement.

### 13.2 Derive the design effect

Suppose $G$ independent template clusters each have $m$ observations. Let every observation have variance $\sigma^2$, and let pairs within a template have correlation $\rho$.

Then $n=Gm$. Summing individual variances and within-cluster covariances gives:

$$
\operatorname{Var}(\overline X)
=
\frac{\sigma^2}{n}
\left[1+(m-1)\rho\right].
$$

The bracket is the **design effect**:

$$
DE=1+(m-1)\rho.
$$

The corresponding variance-equivalent independent sample size is:

$$
n_{\mathrm{eff}}=\frac n{DE}.
$$

**Teaching example:** $G=80$, $m=20$, and $\rho=0.10$:

$$
n=1600,\qquad
DE=1+19(0.10)=2.9,
$$

$$
n_{\mathrm{eff}}\approx552.
$$

Those 1600 correlated rows provide approximately the mean-estimation precision of 552 independent observations under this approximation. Standard errors inflate by $\sqrt{2.9}\approx1.70$, not by 2.9.

At $\rho=0$, $DE=1$. At $\rho=1$, identical siblings contribute approximately one independent observation per template.

Using the mean cluster size is an approximation for unequal clusters. The formula is useful for planning, not a replacement for the cluster bootstrap or a literal count of new observations.

### 13.3 What ICC means

ICC is **intraclass correlation**: similarity between observations in the same cluster.

For a simple random-intercept model $X_{gj}=\mu+u_g+\epsilon_{gj}$:

$$
\rho=
\frac{\operatorname{Var}(u_g)}
{\operatorname{Var}(u_g)+\operatorname{Var}(\epsilon_{gj})}.
$$

Shared template difficulty contributes $\operatorname{Var}(u_g)$; within-template variation contributes the other term.

The planning code estimates ICC from development data and also varies it in sensitivity scenarios. Assuming $\rho=0$ because it gives attractive power is not justified.

The code's one-way ANOVA-style estimate uses between-cluster and within-cluster mean squares:

$$
\widehat\rho
=
\max\left(
0,
\frac{MS_B-MS_W}{MS_B+(n_0-1)MS_W}
\right),
$$

$$
n_0=
\frac{N-\sum_g n_g^2/N}{G-1}.
$$

$N$ is the total observation count; $n_g$ are cluster sizes. The $n_0$ term accounts approximately for unequal sizes. The function is also used for continuous rule differences, despite its name `icc_binary`.

### 13.4 Power is a planning probability

Power asks:

$$
\operatorname{Power}
=
P(\text{the specified success rule is met}\mid\text{an assumed true effect}).
$$

It depends on the effect, variability, independent information, decision rule, and assumptions. It is not the posterior chance that the hypothesis is correct.

For a positive rule effect $d$ with standard deviation $\sigma$:

$$
SE\approx\frac{\sigma}{\sqrt{n_{\mathrm{eff}}}}.
$$

The planning approximation used here is:

$$
\operatorname{Power}_{+}
\approx
1-\Phi\!\left(z_{1-\alpha/2}-\frac d{SE}\right).
$$

$\Phi$ is the standard normal cumulative distribution function; $z_{0.975}\approx1.96$ is its 97.5% quantile.

This calculates the positive rejection region corresponding to a two-sided interval. It is not the full two-tail power expression for effects in either direction.

**Mental picture:** an effect is a signal; variability is fog; independent templates clear the fog. Repeating correlated readings does less than adding genuinely new roads.

### 13.5 Advanced: the H4 power approximation

For assumed true AUROC $A$, positive count $n_+$ and negative count $n_-$, the code uses a Hanley–McNeil variance approximation:

$$
Q_1=\frac A{2-A},
\qquad
Q_2=\frac{2A^2}{1+A},
$$

$$
V(A)
=
\frac{
A(1-A)
+
(n_+-1)(Q_1-A^2)
+
(n_--1)(Q_2-A^2)
}{
n_+n_-
}.
$$

Inflate for clustering:

$$
SE=\sqrt{DE\,V(A)}.
$$

C1's approximate combined cutoff is:

$$
c=
\max\left(
0.60,\,
0.50+z_{0.975}SE
\right).
$$

The corresponding modeled power is:

$$
1-\Phi\!\left(\frac{c-A}{SE}\right).
$$

The first cutoff enforces the practical point target; the second approximates an interval above the identity reference.

This is a planning approximation for C1, with a simulation check. It does not reproduce the complete bootstrap, C2, Holm correction, and joint success of every model/family result.

Planning with 160 or 320 templates means creating new templates beyond the 80-template experiment—not rerunning the same templates or increasing bootstrap repetitions. Planning estimates must come from development, not from held-out outcomes used to select an advantageous sample size.

### 13.6 Arm B loses information when sites are not reached

If $n$ opportunities are offered but only a proportion $P(O=1)$ are reached, the effective information for conditional reversion is approximately:

$$
n_{\mathrm{eff},B}
\approx
\frac{nP(O=1)}{DE}.
$$

For conditional failure rate $p_B$, an approximate 95% interval half-width is:

$$
1.96\sqrt{
\frac{p_B(1-p_B)}{n_{\mathrm{eff},B}}
}.
$$

This is a planning normal approximation, not the final cluster interval for every dataset. Low reach can make conditional reversion very imprecise.

**Say it aloud:** “Power depends on independent information. More correlated sites or more bootstrap replicates cannot substitute for genuinely new templates.”

---

## 14. Scale trends: ordinary least squares on log model size

### 14.1 Why take log10 of parameter count?

The relevant ladder contains Qwen2.5-Coder sizes 0.5, 1.5, 3, 7, 14, and 32 billion parameters. Set:

$$
x_j=\log_{10}(P_j).
$$

A one-unit increase in $x$ means a tenfold increase in parameters. This makes multiplicative size changes easier to interpret than raw billions.

Using parameters rather than billions shifts $x$ by a constant and changes the intercept, not the slope.

The separate 72B checkpoint is not part of this six-size coder-ladder regression.

### 14.2 Where the OLS slope comes from

Fit a line:

$$
y_j\approx\beta_0+\beta_1x_j.
$$

Ordinary least squares chooses coefficients minimizing:

$$
\sum_j[y_j-(\beta_0+\beta_1x_j)]^2.
$$

Solving gives:

$$
\widehat\beta_1
=
\frac{
\sum_j(x_j-\overline x)(y_j-\overline y)
}{
\sum_j(x_j-\overline x)^2
},
\qquad
\widehat\beta_0=\overline y-\widehat\beta_1\overline x.
$$

The numerator measures whether larger $x$ accompanies larger $y$. The denominator measures how spread out the sizes are.

### 14.3 How to read a slope

- A reversion-rate slope of $+0.033$ means **+3.3 percentage points per tenfold increase**, not a relative 3.3% increase.
- An AUROC slope of $-0.081$ means an AUROC decrease of 0.081 per tenfold increase.

These examples match the units of the companion's reported slopes. They do not justify extrapolation to arbitrarily large models.

### 14.4 Paired stimulus uncertainty

Each scale bootstrap draw selects template multiplicities once and applies the same selection across all six sizes. This preserves the fact that the models were tested on matched material.

The slope estimates are separated by grammar and base/instruct outcome. Their testing family has its own Holm correction.

For the two-grammar analysis, that family contains six slopes: base reversion, instruct reversion, and H4 AUROC, separately for `dom` and `blk`.

The scale script uses an unsmoothed two-sided bootstrap tail count:

$$
p_{\mathrm{scale}}
=
\min\left(
1,\,
2\min\left[
\frac{\#\{\beta_1^*\le0\}}{B_{\mathrm{valid}}},
\frac{\#\{\beta_1^*\ge0\}}{B_{\mathrm{valid}}}
\right]
\right).
$$

If every sampled slope is negative, it stores zero. That numerical zero is not a proof that the underlying tail probability is exactly zero. Report the count and resolution: for example, “0 of 2000 bootstrap slopes were nonnegative.”

### 14.5 What a scale trend cannot establish

Sizes were not randomized, and checkpoints can differ in training choices as well as parameter count. The relationship is associational, not a causal experiment on size alone.

“No statistically detectable downward linear trend on this ladder” is more defensible than “size cannot help.” A nonsignificant slope does not rule out nonlinear behavior, small effects, or effects outside the tested range.

**Mental picture:** draw a trend line through six mountain elevations. It summarizes this route, not every mountain on Earth.

**Say it aloud:** “The scale slope describes outcome change per tenfold parameter increase within one checkpoint family; it is not a causal or universal scaling law.”

## 15. Connect the mathematics to Arm B, H5, and H2

### 15.1 Arm B: reaching a site is not choosing correctly there

Let $O_i=1$ mean free generation reaches a comparable decision site. Let $Y_i^B=1$ mean it emits the competitor there.

The probability chain rule gives:

$$
P(O=1,Y^B=1)
=
P(O=1)\,P(Y^B=1\mid O=1).
$$

**Teaching example:** 100 opportunities are offered; 40 are reached; 10 reached sites emit the competitor.

$$
\widehat P(O=1)=0.40,
\qquad
\widehat P(Y^B=1\mid O=1)=10/40=0.25,
$$

$$
\widehat P(O=1,Y^B=1)=10/100=0.10.
$$

The last rate alone conceals whether the model avoids failure because it makes good choices or because it never reaches the decision.

This is called a **hurdle** decomposition: cross the first hurdle of reaching the site, then assess the second decision.

The program-level outcomes add another layer:

- `LEX_FAIL`: an invalid lexical spelling.
- `PARSE_FAIL`: syntax does not form a valid program.
- `VALID_VACUOUS`: legal but operationally empty/vacuous under the evaluator.
- `VALID_WRONG`: legal program, wrong canonical task meaning.
- `VALID_CORRECT`: correct task meaning.

Task accuracy, parsing validity, conditional site reversion, and candidate-margin labels are not interchangeable endpoints.

**Say it aloud:** “Arm A measures preferences at an imposed prefix; Arm B checks actual generated behavior and separately reports whether the relevant decision was reached.”

### 15.2 H5: benefit per changed role

H5 asks whether predicted-risk targeting buys more improvement than indiscriminate changes.

The current arms select:

- targeted: roles with the largest mean base-model risk;
- random: the same selected-role budget over several fixed seeds;
- global: every eligible remapped role.

The mapping and its valid programs must be rewritten together. For tested corpus $\mathcal C$:

$$
\operatorname{IR}_{\phi'}(W(p))
=
\operatorname{IR}_{\phi}(p)
\qquad
\forall p\in\mathcal C.
$$

Here $\phi'$ is the repaired spelling map, $W$ the associated rewrite, and IR the canonical meaning.

**Mental picture:** replace misleading road signs without moving either destination or changing which route reaches it.

The implemented proof checks canonical-IR hashes over the 62 earlier corpus programs plus 80 templates in both grammar families. It validates that finite corpus, not every imaginable program in the language.

The exported efficiency metric is:

$$
\eta_a
=
\frac{
R_{\mathrm{before},a}-R_{\mathrm{after},a}
}{
B_a
},
$$

where $R$ are **reversion counts over successfully matched scored sites**, and $B_a$ is the number of independently selected roles changed in arm $a$.

**Teaching example:** reducing 90 reversions to 60 while changing three roles gives:

$$
\eta_{\mathrm{targeted}}=\frac{90-60}{3}=10.
$$

That is ten saved site-level reversions per changed role. It is not a ten-percentage-point rate change.

A random arm saving 15 reversions over three roles has efficiency 5. If the average over random seeds is 5, the targeted-minus-random advantage is:

$$
\Delta\eta
=
\eta_{\mathrm{targeted}}
-
\frac1J\sum_{j=1}^{J}\eta_{\mathrm{random},j}
=
5.
$$

For a rate-normalized analysis one could instead use $(r_{\mathrm{before}}-r_{\mathrm{after}})/B$, but that is a different quantity. Name the units and compare matched populations.

The code counts selected roles, not individual token occurrences. It does not count the coupled chain-operator follower separately when repairing the class sigil.

### 15.3 Control degradation and silent versus loud errors

For unchanged-role control sites:

$$
d_{\mathrm{control}}
=
r_{\mathrm{after,control}}
-
r_{\mathrm{before,control}}.
$$

A rise from 0.10 to 0.115 gives $d=0.015$: 1.5 percentage points, within the configured point-estimate tolerance 0.02.

This is not automatically a confidence-bound noninferiority test. Unchanged roles are also not necessarily a separately validated low-risk population.

The global arm can have no unchanged-role control sites; in that case a control degradation estimate is unavailable, not automatically zero.

Some repairs use unfamiliar spellings that turn a silent semantic collision into a loud lexical error. Thus:

$$
\text{silent error}
=
\text{reversion}
\ \land\
\text{collision remains SEMANTIC}.
$$

A decrease in silent errors can mean a change in error class, not fewer total reversions. Report both.

The current export provides arm outcomes but does not by itself calculate a paired targeted-minus-random superiority interval. A table of favorable point estimates is not yet the full confirmatory H5 test. Also check whether exclusions leave comparable paired-site coverage across arms.

**Say it aloud:** “H5 tests improvement per changed role while preserving intended meaning and monitoring collateral damage; reduced silent errors are not automatically reduced total errors.”

### 15.4 H2: interaction is more than two main effects

Suppose one factor is competitor-prior strength, strong versus neutral, and another is local competitor support, high versus low.

For an outcome $Z$, the difference-in-differences is:

$$
\Delta_Z
=
(\overline Z_{\mathrm{strong,high}}
-\overline Z_{\mathrm{strong,low}})
-
(\overline Z_{\mathrm{neutral,high}}
-\overline Z_{\mathrm{neutral,low}}).
$$

**Teaching example:** reversion probabilities are:

| | Low local cue | High local cue |
|---|---:|---:|
| Neutral prior | 0.15 | 0.20 |
| Strong prior | 0.30 | 0.50 |

$$
\Delta_p=(0.50-0.30)-(0.20-0.15)=0.15.
$$

The cue increases reversion by 0.20 under a strong prior but only 0.05 under a neutral prior: an extra 0.15 amplification.

The hypothesized interference direction is:

$$
\Delta_M<0,
\qquad
\Delta_p>0,
\qquad
\Delta_{\operatorname{logit}(p)}>0.
$$

Margins point toward correctness; reversion probabilities point toward failure. Their signs must be oriented consistently before checking agreement.

A probability-scale interaction can differ from a logit-scale interaction because the transformation is nonlinear. Agreement across these scales is a robustness requirement, not a mathematical invariance theorem.

The current experiment lacks the independently calibrated factors needed for this test. Constructing “prior strength” from the same margin being explained would be circular. H2 is therefore **NOT TESTABLE**, not “tested and false.”

**Mental picture:** one wind pushes toward the old road, and a nearby sign gives an extra push. Interaction asks whether the second push grows stronger when the first is already strong.

---

## 16. Development, freezing, and the limits of current implementation

### 16.1 What development learns and freeze records

The conceptual stages are:

```text
Development: obtain (risk, label) examples; learn a, b and a cutoff
Freeze:      record the recipe, a, b, cutoff, prompts and checked code/materials
Held-out:    apply the committed procedure; evaluate it without outcome-driven retuning
```

The freeze command actually fits the final calibration and threshold from completed development rows, separately for each available base/instruct pair, then writes `DEV_FREEZE.json`.

“Calibration” appears in both stages because development supplies its evidence and freeze stores its final settings. The LLM itself is not being trained or immobilized.

Exploratory analyses may use observed outcomes to generate ideas. Confirmatory analyses test precommitted choices on reserved observations. They remain subject to the validity of the actual measurement and statistical procedures.

### 16.2 Important calibration exception for new model pairs

This is an implementation limitation, not a mathematical property of sigmoid calibration.

The freeze contains calibration only for pairs present in development. For new pairs absent from it:

1. The export passes `calibration=None`.
2. The metric evaluator fits calibration on that held-out group's outcomes.
3. Prediction rows instead use the fallback $\sigma(S)$ while being labeled `DEV_FREEZE`.
4. No development-selected pair-specific threshold is available.

Consequently, probability metrics and prediction rows can use different mappings for those pairs. They should not be described as untouched validation of development-fitted calibration.

Raw-risk AUROC, AP, precision-at-budget, and C1/C2 ranking comparisons do not depend on that calibration fallback. The problem must not be generalized into “all ranking results are invalid,” nor ignored when discussing probability quality.

A held-out diagnostic calibration regression is legitimate as a diagnostic of fixed predictions. Fitting a new probability mapping to held-out labels and presenting it as frozen calibration is a different action.

### 16.3 What “held-out grammar” cannot mean here

`blk` was examined before the freeze. Fresh mappings under `blk` test **a previously examined syntax on new spelling assignments**, not a completely unseen grammar family.

The 21-model collection also includes the development checkpoints tested on new mappings. “Held-out” names the reserved evaluation cells; it does not mean every checkpoint was wholly unseen.

### 16.4 Source shorthand that this guide makes more precise

| Shorthand | Precise interpretation |
|---|---|
| “First divergent token” | Score every candidate-tail token from divergence onward |
| “Length effects removed” | Shared-prefix effects cancel; candidate-length effects can remain |
| “Reversion” | Distinguish forced-prefix negative margins from actual generated competitors |
| “Multiply by the rule effect” | Exponentiate a log contrast to obtain a likelihood-ratio change |
| “Never switches” | No first crossing was observed within the tested ladder |
| “Survival means still wrong” | No first crossing yet; later relapses do not restore survival |
| “Resample families” | Resample template clusters within fixed grammar-family analyses |
| “Holm multiplies each p-value” | It also applies a running maximum and caps at 1 |
| “All calibration was frozen” | Only development-present pairs have those saved fitted parameters |
| “No significant size effect” | No detected specified trend; not proof of equivalence |
| “Proof over the language” | Canonical-IR preservation checked over the finite corpus |
| “Per changed symbol” | Exported H5 denominator counts independently selected roles |

These qualifications are part of understanding the mathematics, not peripheral disclaimers.

---

## 17. What else should you learn?

### 17.1 Prerequisites in the right order

| Layer | What to understand | Why you need it here |
|---|---|---|
| Algebra | Ratios, exponentials, logs, solving linear equations | Margins, odds, sigmoid, interpolation |
| Probability | Conditional probability, chain rule, expectation | Sequence scoring, hurdle outcomes, rates |
| Information theory | Entropy, cross-entropy, KL, surprise | Why log-likelihood losses are sensible |
| Statistical estimation | Mean, variance, standard error, quantiles | Summaries and uncertainty |
| Binary prediction | Confusion matrix, ranking, prevalence, calibration | H4 interpretation |
| Survival analysis | Event time, risk set, censoring, median | $k^*$ summaries without discarding hard sites |
| Dependence and inference | Correlation, resampling, testing, multiplicity | Honest intervals and comparisons |
| Experimental design | Controls, leakage, frozen choices, identifiable factors | Defensible claims rather than attractive numbers |

You do not need advanced transformer internals to understand these endpoints. For mechanistic claims about pathways, attention, or activation patching, that would be a separate learning layer.

The minimum questions to ask of **every equation** are:

1. What is random or variable?
2. What is held fixed?
3. What is the unit and denominator?
4. Is this a measurement, an estimate, a prediction, or a hypothesis test?
5. What assumptions connect the number to the scientific claim?

### 17.2 Primary and official reading materials

These are further-reading pointers, not substitutes for the repository's actual definitions.

- [Jurafsky and Martin, *Speech and Language Processing*, Chapter 3](https://web.stanford.edu/~jurafsky/slp3/3.pdf): start with probability chain rules, log scoring, and perplexity. Its simpler language models make the foundations easier to see.
- [PyTorch, CrossEntropyLoss](https://docs.pytorch.org/docs/2.11/generated/torch.nn.CrossEntropyLoss.html): connect logits, log-softmax, target labels, and categorical negative log-likelihood.
- [scikit-learn, Probability calibration](https://scikit-learn.org/stable/modules/calibration.html): study reliability diagrams and the difference between discrimination and trustworthy probability estimates.
- [scikit-learn, Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html): compare ROC, precision-recall, average precision, and probability losses. Remember that this repository implements its own formulas.
- [NIST, Kaplan–Meier product-limit estimation](https://www.itl.nist.gov/div898/handbook/apr/section2/apr215.htm): work through event risk sets and censored observations.
- [Efron, *Bootstrap Methods: Another Look at the Jackknife* (1979)](https://projecteuclid.org/journals/annals-of-statistics/volume-7/issue-1/Bootstrap-Methods-Another-Look-at-the-Jackknife/10.1214/aos/1176344552.full): an original source for bootstrap reasoning. This experiment extends the resampling unit to templates.
- [Holm, *A Simple Sequentially Rejective Multiple Test Procedure* (1979)](https://www.ime.usp.br/~abe/lista/pdf4R8xPVzCnX.pdf): the original multiple-testing procedure, useful after understanding ordinary hypothesis tests.

### 17.3 Where the repository implements the equations

| Topic | Local source |
|---|---|
| Tokenization, log-softmax, candidate margins, program NLL | [margins.py](../src/phase3_2/margins.py) |
| AUROC, AP, precision@k, calibration, Youden, H4 criteria | [h4.py](src/p33/h4.py) |
| Development-fitted parameters and frozen recipe | [freeze.py](src/p33/freeze.py) |
| First crossing, recrossing diagnostics, Kaplan–Meier | [kstar.py](src/p33/kstar.py) |
| Cluster bootstrap, bootstrap tails, Holm | [analysis.py](../src/phase3_2/analysis.py) |
| ICC, design effects, planning power and precision | [power.py](src/p33/power.py) |
| Scale slopes and their resampling | [scale_analysis.py](scripts/scale_analysis.py) |
| Repair selection and corpus IR checks | [h5.py](src/p33/h5.py) |
| Export populations, calibration fallback and H5 units | [export.py](src/p33/export.py) |
| Reserved cells and freeze integrity | [splits.py](src/p33/splits.py) |
| Identifiability limitations of the interaction | [h2.py](src/p33/h2.py) |

---

## 18. Practice, glossary, and a research explanation you can say aloud

### 18.1 Check your understanding

**Question 1.** The correct candidate has log-likelihood $-2$ and the competitor $-3$. What are margin and risk?

**Answer:** $M=-2-(-3)=1$, so the correct candidate wins; $S=-1$. Its likelihood is $e$ times the competitor's.

**Question 2.** A probability predictor returns 0.8. Does that mean the correct token has probability 0.8?

**Answer:** No. Name the predicted event. For H4, it concerns the instruct checkpoint's negative-margin label across sites.

**Question 3.** What is the token NLL if the observed token gets probability 0.1?

**Answer:** $-\log(0.1)\approx2.303$ nats. For a one-hot target, that is also the token cross-entropy.

**Question 4.** What does AUROC 0.75 say?

**Answer:** The score earns 75% average ordering credit in failure/non-failure comparisons. It does not assert 75% classification accuracy.

**Question 5.** A model never crosses on the ladder ending at 32. What time should you record?

**Answer:** A censoring time of 32 and event indicator 0, not an observed crossing at 32 and not a missing value without explanation.

**Question 6.** Why can a $k^*$ of 1.7 coexist with a negative margin at 8?

**Answer:** $k^*$ is first crossing, not sustained success. Later margins can recross.

**Question 7.** Half the sites are already nonnegative at zero examples. Can the all-sites KM median be zero?

**Answer:** Yes. That says at least half need no examples under this endpoint. Use the initially-wrong summary for adaptation among starting failures.

**Question 8.** Does drawing 2000 bootstrap replicates increase the original template count?

**Answer:** No. It estimates uncertainty from the available clusters; it does not collect new evidence.

**Question 9.** Are a tiny p-value and a large effect the same thing?

**Answer:** No. Report magnitude, units, uncertainty, and the test's scope separately.

**Question 10.** Holm receives raw p-values 0.01, 0.03, 0.04. What are the adjusted values?

**Answer:** 0.03, 0.06, 0.06. The running maximum prevents the third adjusted value from falling back to 0.04.

**Question 11.** Three role changes save 30 matched-site reversions. What is the exported H5 benefit?

**Answer:** Ten saved site reversions per changed role. This is not a percentage-point improvement.

**Question 12.** The scale slope interval includes zero. Have you established that size never matters?

**Answer:** No. The specified trend is uncertain; equivalence, nonlinear behavior, causal effects, and untested ranges require different evidence.

### 18.2 Compact glossary

| Term | Meaning here |
|---|---|
| Logit | Unnormalized model token score, or the log-odds transform when applied to a probability |
| Likelihood | Support assigned to fixed observations as a function of a statistical/model specification |
| NLL | Negative log-likelihood; less surprise gives a smaller loss |
| Cross-entropy | Target-weighted average negative log probability |
| Margin | Correct log-likelihood minus competitor log-likelihood |
| Risk | H4's reversed base-model margin |
| Calibration | Matching predicted probabilities to outcome frequencies |
| Discrimination | Ordering failures above non-failures |
| Threshold | Probability or score cutoff used to make a binary warning |
| Prevalence | Proportion of positive outcome labels in the evaluated population |
| AUROC | Failure/non-failure ordering probability with half-credit for ties |
| AP | Recall-increment-weighted precision, computed by distinct-score groups |
| Endpoint | A predefined measured quantity |
| Censoring | Event time is only partially observed |
| Risk set | Observed cases not yet having the event at a survival step |
| Kaplan–Meier median | First time estimated survival is at most one-half |
| Cluster | Observations sharing a template-level source of dependence |
| Confidence interval | An uncertainty procedure with a stated intended coverage |
| Power | Chance of meeting a specified decision rule under an assumed effect |
| Holm correction | Step-down adjustment within a declared set of tests |
| OLS | A fitted line minimizing squared residuals |
| Confirmatory | Evaluation of precommitted choices on appropriately reserved observations |

### 18.3 A complete explanation for a meeting

> We compare the model's full candidate log-likelihoods at exact spelling decisions. Their difference is a log-likelihood ratio: a negative margin favors the familiar but wrong spelling. We test whether the base checkpoint's reversed margin ranks its instruct sibling's negative-margin sites, using AUROC and relevant baselines. Development calibration translates that score into estimated failure probability, while ranking and calibration remain distinct questions. We also add worked examples on a fixed ladder and estimate the first nonnegative crossing, reporting recrossing because adaptation may not last. Kaplan–Meier summarizes that endpoint without dropping sites that have not crossed by the observation limit. Template-cluster bootstrap intervals account for related sites; effect targets, correction scope, censoring, and implementation limits qualify what the results establish.

### 18.4 The shortest mental model

> **Likelihood weighs the two doors. Margin shows which door pulls harder. Calibration labels the warning gauge. AUROC checks its ordering. The demonstration ladder measures first switching. Kaplan–Meier keeps unfinished cases in the story. Clustered inference prevents related cases from pretending to be independent evidence.**

*This teaching companion changes documentation only. Implementation limitations described above are observations, not code fixes or retroactive changes to the frozen experiment.*
