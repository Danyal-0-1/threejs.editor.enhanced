# The Phase 3.3 experiment in one file

> Written 2026-10-08 for a meeting with the professor.
>
> **Sources.** Every number was checked against the code and the data:
>
> - **Development** (`dev-20261006a`, 4 models): final, and **exploratory** by design.
> - **Held-out** (`heldout-20261007a`, 21 models): produced by the **frozen** analysis code on
>   measurements that are complete (Arm A and the extinction ladder). The official export will
>   reproduce these numbers.
> - **Still running:** Arm B (free generation), H5 (repairs) and the final export.

---

## 0. The idea in 60 seconds

Code models carry strong habits about what symbols mean: `.` is member access, `#` is an
id, `mesh` is a 3D mesh. We built a small 3D-scene language, **3DOM**, then **reassigned some
of its spellings**. In one version, the keyword for meshes is written `light`. We told the
model the new spellings in a token table, then measured, at each exact place where a
reassigned symbol must be written, whether it writes the **new** spelling or **falls back to
the old one**. That fallback is a *reversion*. It produces a program that still runs but
does the wrong thing.

Three questions:

1. **How often** do models revert, even with the table, and how much does the table help?
2. **How many worked examples** does it take before a model switches to the new spelling?
   This is the *extinction threshold* `k*`, our measure of adaptation to a new DSL.
3. **H4 (the preregistered confirmatory claim):** does a base model's own preference predict
   **which** sites its instruction-tuned twin will get wrong?

**Design.** Everything was designed on 4 development models and **frozen**. It was then tested
once on **held-out** mappings with **21 models** (0.5B–72B).

**What the held-out data say:**

- H4 holds for all 10 base/instruct pairs, in both grammars (AUROC 0.76–0.96).
- With the table, every model still reverts on 40–56% of sites, and size does not change that.
- Models switch after a median of about 1.4–4.6 examples in the familiar grammar and 3–12 in
  the unfamiliar one.
- 6–29% of sites never switch within 32 examples, and almost every curve wobbles on the way.

---

## 1. The setup

### 1.1 The language and its two grammars

3DOM edits 3D scenes in the style of jQuery and CSS. There are **80 abstract programs**
(*templates*), each an intermediate representation (IR). Each can be written in two
**grammar families**:

- **`dom`** — JavaScript/jQuery-like. Template `t011` in standard spelling:
  ```js
  (function(){ $S('#panel>.frame>mesh').metalness(0.8); })();
  ```
  *"Select the meshes inside class `frame` inside id `panel`; set their metalness to 0.8."*
- **`blk`** — a block-structured surface for the same programs. It is less familiar to models.

### 1.2 Reassigned spellings: the lexicons

A **lexicon** (φ-map) reassigns the spellings of *roles*. There are 9 lexicons:

- `d25*`: 25% of roles respelled;
- `d50*`: 50%;
- `d75*`: 75%.

Part of `d50s1`, the lexicon used in the worked example:

| role | standard | `d50s1` |
|---|---|---|
| class selector sigil | `.` | `#` |
| id selector sigil | `#` | `.` |
| operation chain operator | `.` | `#` |
| type keyword: mesh object | `mesh` | **`light`** |
| type keyword: group object | `group` | `mesh` |
| type keyword: light object | `light` | `camera` |
| operation: translate | `move` | `duplicate` |

So `t011` in `d50s1` reads:

```js
(function(){ $S('.panel>#frame>light')#metalness(0.8); })();
```

### 1.3 Sites, collisions, reversion

- A **site** is one position in one program where a reassigned spelling must be written.
- At a site there are two candidates:
  - **correct**: the new spelling;
  - **competitor**: the old spelling that the model's prior pulls toward.
- Only **semantic collisions** are kept: writing the competitor *still parses but means
  something else*. In `d50s1`, `mesh` now means "group object", so writing it selects groups
  instead of meshes. A reversion is a silent wrong program, not a syntax error.
- Sites are grouped by role (**stratum**):
  - **sigil**: `#`, `.`;
  - **keyword**: `mesh`, `lasso`;
  - **verb**: `metalness`, `duplicate`.

### 1.4 Models

| | checkpoints |
|---|---|
| development | Qwen2.5-Coder 0.5B and 1.5B, base + instruct (4) |
| held-out | Qwen2.5-Coder 0.5B / 1.5B / 3B / 7B / 14B / 32B; DeepSeek-Coder 1.3B / 33B; Llama-3.2-1B; StarCoder2-3B (base only); Qwen2.5-72B (on two A100s). All in base + instruct pairs: **21 checkpoints** |

### 1.5 Why development → freeze → held-out

```
 DEVELOPMENT                       FREEZE                    HELD-OUT (confirmatory)
 dom x {d25s1,d25s2,d50s1,d50s2}   DEV_FREEZE.json:          dom + blk x {d25s3,d50s3,d75s1a,d75s2a,d75s3a}
 4 models                   ──►    calibration, thresholds,  ──►  21 models, 0.5B-72B
 design, debug, calibrate          prompts, code hashes,          analysed by the FROZEN code;
                                   model revisions                any code change is refused
```

Nothing measured on held-out data can influence any choice: the analysis code, the
calibration and the model revisions were fixed first. That is what makes the held-out
result *confirmatory* rather than exploratory.

---

## 2. Hypotheses, as preregistered (2026-10-02)

| | statement | how it is measured | success criterion |
|---|---|---|---|
| **H4** (confirmatory, primary claim) | A base model's preference at an exact site predicts which sites its **instruction-tuned twin** gets wrong, on held-out mappings | AUROC of the base model's risk score against the instruct model's reversions (§3, step 7) | **C1:** AUROC − identity baseline ≥ 0.10, CI > 0. **C2:** AUROC − length baseline ≥ 0.05, CI > 0. **C3:** AUROC ≥ 0.65 on a held-out *grammar*. Each grammar family separately; Holm correction |
| **Primary endpoint** | the extinction threshold `k*`: how many in-context examples until the model switches | the example ladder 0, 1, 2, 4, 8, 16, 32 (§3, step 6) | Kaplan–Meier median, with censoring reported |
| **H5** (confirmatory, applied) | Respelling only the *predicted-high-risk* roles reduces reversion more **per changed symbol** than random or global respelling, with meaning provably unchanged | repair arms: targeted, random ×5, global | reduction per symbol > random, CI > 0; low-risk sites worsen ≤ 0.02 |
| **H2** (exploratory) | prior × context interaction | — | **NOT TESTABLE**: prior strength was never manipulated |
| also measured | reversion rate; **rule effect** (table vs no table, vs a length-matched control); **Arm B** (free generation); **scale trend** (deviations D10/D11) | | |

**C3 is NOT TESTABLE** (deviation D1). `blk` was looked at during development, so no truly
unseen grammar exists. `blk` is reported as a weaker, "seen grammar, unseen mapping" test.

---

## 3. One site, start to finish (real numbers from Sol)

**Site** `dom:d50s1:t011:T_TYPE_MESH:0`.

**Run:** development run `dev-20261006a` on an A100-80GB, in bf16 with an fp32 output head.

**Models:** Qwen2.5-Coder-0.5B (base) and Qwen2.5-Coder-0.5B-Instruct.

### Step 1 — Render the program and find the decision point

The template's IR is rendered in family `dom` with lexicon `d50s1`. The decision point is
character 31:

```
prefix:      (function(){ $S('.panel>#frame>
correct:     light      ← the new spelling of "mesh object"
competitor:  mesh       ← the old spelling the prior pulls toward
```

- **Code:** the plan builder renders every template in every (family, lexicon) and lists the
  sites: [`pipeline.build_plan`](src/p33/pipeline.py#L103).
- **Rendering:** `BACKENDS["dom"].render(ir, phi)`.

### Step 2 — Is it a real collision?

The competitor is substituted and the program re-parsed. The *variant*
`$S('.panel>#frame>mesh')#metalness(0.8)` parses, but to a **different IR**: `mesh` is bound
to **group objects** in `d50s1` (`competitor_binds_to = T_TYPE_GROUP`). So the site is a
**SEMANTIC collision** and is kept. Sites whose competitor fails to parse, or yields the same
IR, are excluded.

- **Code:** [`phase3_2/sites2.classify`](../src/phase3_2/sites2.py).
- **Duplicates:** removed within each (family, lexicon) cell:
  [`sampling.dedupe_within_cells`](../src/phase3_2/sampling.py#L82).

### Step 3 — Build what the model sees (three conditions)

| condition | context before the program | tokens |
|---|---|---:|
| **rule** | the full TOKEN TABLE (all 28 roles with their `d50s1` spellings) | 298 |
| **norule** | the same framing and role list, **spellings withheld** | 237 |
| **norule_lenmatched** | `norule` padded with a neutral line until it is as long as `rule` | 307 |

The rule prompt, abbreviated:

```
You are writing 3DOM, a domain-specific language for editing 3D scenes.
3DOM resembles CSS and jQuery, but several tokens have been REASSIGNED.
...
TOKEN TABLE
  class selector sigil               #
  id selector sigil                  .
  type keyword: mesh object          light
  type keyword: group object         mesh
  ...
Write 3DOM using exactly the spellings above.

(function(){ $S('.panel>#frame>          ← the model continues from here
```

**Why a length-matched control?** The table prompt is longer, and a longer context could
change the answer by itself. Comparing against `norule_lenmatched` isolates the table's
*information* from its *length*.

**Code:**

- [`prompts.bundle`](../src/phase3_2/prompts.py#L254) (rule / norule / norule_lenmatched);
- [`margins.build_prefix`](../src/phase3_2/margins.py#L332):
  ```python
  ctx = (rule.rstrip() + "\n\n") if rule else ""
  for ex in shown:                       # worked examples (step 6); none in Arm A
      ctx += ex.rstrip() + "\n"
  return ctx + site.prefix
  ```

### Step 4 — Measure the preference: the margin M

**Math.** Tokenize `prefix + correct` and `prefix + competitor`. Find the first token where
they differ: position `k`, after `k_common` shared tokens (here 307). Score each candidate's
tokens from that point on, given the **same** shared context:

$$
M \;=\; \sum_{t\ge k}\log P(c_t \mid \text{shared}, c_{k..t-1}) \;-\; \sum_{t\ge k}\log P(q_t \mid \text{shared}, q_{k..t-1})
\qquad (\text{natural log, "nats"})
$$

Here both candidates are a single token, so each sum has one term:
$M = \log P(\texttt{light}\mid\text{prefix}) - \log P(\texttt{mesh}\mid\text{prefix})$.

- **M > 0** means the model prefers the new spelling.
- **M < 0** means it prefers the old one: a **reversion**.

**Simple explanation.** M is "how many times more likely" on a log scale:
$e^{M}$ = P(correct) / P(competitor).

**Code** — [`TokenScorer.score_pair_detailed`](../src/phase3_2/margins.py#L258):

```python
a = self.ids(prefix + correct)
b = self.ids(prefix + competitor)
k = check_pair(a, b)                          # first divergent token; refuses degenerate pairs
first = self._logprobs_rows(a, k - 1, k)[0]   # log-softmax at position k (fp32 output head)

def side(seq):                                # one candidate's log-probability from k on
    if len(seq) == k + 1:                     # a single token: read it off `first`
        return float(first[seq[k]])
    rows = self._logprobs_rows(seq, k - 1, len(seq) - 1)
    return float(rows.gather(1, tgt.unsqueeze(1)).sum())   # several tokens: sum them

PairScore(logp_correct=side(a), logp_competitor=side(b), k_common=k, ...)
```

**Safeguards.**

- [`check_pair`](../src/phase3_2/margins.py#L137) **refuses** pairs that tokenize identically,
  or where one is a prefix of the other. An unscorable site is recorded with its reason, never
  scored as 0.
- The output layer is computed in **fp32**
  ([`_logprobs_rows`](../src/phase3_2/margins.py#L237)), so bf16 rounding cannot decide the
  sign of a small margin.

**Numbers** (one token each: `light` vs `mesh`):

| model | condition | log P(light) | log P(mesh) | **M** | in words |
|---|---|---:|---:|---:|---|
| 0.5B base | rule | −4.096 (1.7%) | −1.620 (19.8%) | **−2.476** | prefers the *old* `mesh`, 11.9× |
| 0.5B base | norule | −7.819 | −3.457 | −4.361 | 78× for `mesh` |
| 0.5B base | norule_lenmatched | −7.585 | −2.847 | −4.738 | |
| 0.5B instruct | rule | −2.812 (6.0%) | −2.779 (6.2%) | **−0.034** | a near coin-flip, slightly for `mesh` |
| 0.5B instruct | norule | −7.642 | −3.085 | −4.557 | |

**Result:** both models **revert** at this site even when given the table.

### Step 5 — Did the table help? The rule effect

**Math**, per site, paired:

$$\Delta_{\text{rule}} = M_{\text{rule}} - M_{\text{control}}$$

averaged over sites, with a template-bootstrap interval (§4.8).

**This site (0.5B base):**

- against `norule`: −2.476 − (−4.361) = **+1.885**;
- against the length-matched control: −2.476 − (−4.738) = **+2.262**.

**In words:** the table multiplied the odds of the new spelling by $e^{1.885} \approx 6.6$.
That is real help, but not enough to flip the decision.

**Code** — [`analysis.paired_rule_effect`](../src/phase3_2/analysis.py#L176):

```python
d = [v["rule"] - v["norule"] for v in idx.values() if "rule" in v and "norule" in v]
return st.mean(d)
```

### Step 6 — How many examples to switch? The ladder and `k*`

**Procedure.** Keep the table, and prepend `k` **worked example programs** written in
`d50s1`, for `k` = 0, 1, 2, 4, 8, 16, 32. Measure M again at each rung.

**The examples are leak-free** ([`demos.for_site`](src/p33/demos.py#L86),
[`is_leak`](src/p33/demos.py#L74)):

- never the site's own template, and never a program that replays the decision;
- taken in a fixed seeded order, so rung 2 = rung 1 + one more example (nested).

The first example is `t001` in `d50s1`: `(function(){ $S('.door')#scale(2,'x'); })();`.

**This site, 0.5B base:**

| examples k | 0 | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---:|---:|---:|---:|---:|---:|---:|
| M | −2.476 | −1.651 | **+0.702** | +0.403 | −1.104 | −1.496 | **+3.014** |

**Math.** `k*` is the first **upward zero-crossing**, linearly interpolated between the two
rungs:

$$
k^* = k_{i-1} + (k_i - k_{i-1})\,\frac{0 - M_{i-1}}{M_i - M_{i-1}}
     = 1 + 1\cdot\frac{1.651}{0.702 + 1.651} = \mathbf{1.70}
$$

- If M ≥ 0 already at k = 0, then `k* = 0` ("already correct").
- If M never crosses by 32, `k*` is **censored**: it is "more than 32", and the site is kept
  as such.

**Simple explanation.** "How many examples until the model would rather write the new word
than the old one."

**Notice the wobble.** The curve crosses at about 1.7 examples, **falls back below zero at 8
and 16**, and only stays positive at 32. The code records:

- `nonmonotone = True`;
- `recrossed_down = True`;
- `sustained_k = 32`, the rung from which it stays correct.

Adaptation is not smooth, and this is typical: 93–100% of curves wobble.

**Other models at the same site:**

- the instruct twin switches at `k*` = 1.00;
- the 1.5B base needs `k*` = **23.0**. A bigger model is not always faster.

**Code** — [`kstar.compute`](src/p33/kstar.py#L74):

```python
if margins[0] >= 0:                                   # already correct
    return KStar(0.0, ...)
for i in range(1, len(margins)):
    y0, y1 = margins[i - 1], margins[i]
    if y0 < 0 <= y1:                                  # first upward crossing
        t = (0.0 - y0) / (y1 - y0)
        k = float(ladder[i - 1]) + t * (ladder[i] - ladder[i - 1])
        return KStar(k, ...)
return KStar(None, ..., censored=True, ...)          # never crossed: censored
```

### Step 7 — H4 at this site: does the base model predict the instruct model?

**Math.**

- **risk** = −M(base, rule) = **+2.476**. The more the base model prefers the old spelling,
  the riskier the site.
- **label** = 1 if M(instruct, rule) < 0. Here M = −0.034, so **label = 1**: the instruct model
  reverts.
- **Calibrated probability** (Platt scaling, fitted on development and frozen):
  $p = \sigma(a + b\cdot\text{risk}) = \sigma(-0.2984 + 0.9014 \times 2.476) = \sigma(1.934) = \mathbf{0.874}$.
- **Decision threshold** (Youden, frozen): 0.364. Since 0.874 > 0.364, the prediction is
  "will revert", and it is **correct**.

**Simple explanation.** The base model's own hesitation at this exact spot is a warning light
for its instruction-tuned version.

**Why site-level matters.** A *role-level* baseline that only knows "how often does this
symbol cause trouble elsewhere" gives this terminal a rate of **0.136**, i.e. low risk. It
would have missed this site. The site-level score caught it.

**Code** — [`h4.build_table`](src/p33/h4.py#L302) pairs base and instruct on the same site:

```python
"risk":  -b["m_seq"],                 # base model, rule condition
"label": int(i["m_seq"] < 0),         # instruct model, rule condition
"identity": 1.0 ...,                  # baseline: "this symbol was respelled" (constant)
"length": float(len(b["competitor"].encode()) - len(b["correct"].encode())),
```

### Step 8 — Recorded once, never lost

- **Shards.** Each block of up to 64 sites is written atomically as a *shard*, with a
  *done-marker* holding its sha256. A crash or timeout never leaves a half-written result,
  and a resubmitted job skips finished blocks.
- **Row contents.** Every row carries the model revision, tokenizer fingerprint, prompt hash
  and example ids.
- **Code:** [`shards.ShardStore`](src/p33/shards.py).

### Step 9 — From one site to a model-level result

| statistic | over what | this model: development (0.5B base, `dom`) | held-out |
|---|---|---|---|
| **reversion rate** | share of sites with M(rule) < 0 | 0.41–0.43 per lexicon | 0.455 (`dom`), 0.438 (`blk`) |
| **rule effect** | mean Δ over sites | +0.14 nats (mean over lexicons) | +0.25 (`dom`), +0.28 (`blk`) |
| **`k*` median** | Kaplan–Meier over initially-wrong sites | 6.2 examples [2.4, 7.8], 13% censored | 2.6 [1.2, 6.5] (`dom`), 5.0 [1.8, 11.7] (`blk`) |
| **H4 AUROC** | 0.5B pair, all sites | 0.869 | 0.888 (`dom`), 0.836 (`blk`) |

The intervals come from the **template-cluster bootstrap** (§4.8).

---

## 4. The math on one page, with a plain explanation for each

| # | quantity | formula | in plain words |
|---|---|---|---|
| 4.1 | margin | $M = \log P(c) - \log P(q)$ at the first divergent token | how strongly the model prefers the new spelling *c* over the old *q*; below 0 means it falls back |
| 4.2 | reversion rate | $\frac{1}{n}\sum_i \mathbf 1[M_i<0]$ | the share of sites where it falls back |
| 4.3 | rule effect | $\overline{M_{\text{rule}} - M_{\text{control}}}$, paired by site | how much showing the table moves the preference |
| 4.4 | `k*` | first upward zero-crossing of $M(k)$, interpolated | how many examples until it switches |
| 4.5 | Kaplan–Meier | $S(t) = \prod_{t_j \le t}\left(1 - \frac{d_j}{n_j}\right)$; median = first $t$ with $S(t) \le 0.5$ | the share still not switched after *t* examples. Sites that never switch stay in the denominator, so the habit does not look easier to break than it is |
| 4.6 | AUROC | $P(\text{risk}_{+} > \text{risk}_{-})$, ties count ½ | pick one site the instruct model got wrong and one it got right; the chance the base model ranked the wrong one riskier |
| 4.7 | calibration | $p = \sigma(a + b\cdot\text{risk})$; threshold maximises TPR − FPR | turns a margin into a probability; fitted on development only |
| 4.8 | cluster bootstrap | resample the 80 **templates** with replacement, 2000 times; 95% interval = 2.5th–97.5th percentile | sites from one program are siblings, so whole families are resampled, not sites |
| 4.9 | Holm | sort the *p* values; multiply the *i*-th smallest by (m − i + 1) | protects against "one of several tests passed by luck" |
| 4.10 | design effect | $DE = 1 + (m-1)\rho$, $n_{\text{eff}} = n/DE$ | correlated sites are worth fewer independent observations |
| 4.11 | scale slope (D11) | OLS slope of the outcome on $\log_{10}$(parameters), within the Qwen2.5-Coder ladder | "per 10× more parameters, does reversion or predictability change?" |

**Three tiny examples.**

- **Kaplan–Meier.** Five sites switch at 1.7, 3.2, 6.0 and 12.5 examples; a fifth never does
  (censored at 32).
  - $S = 1\cdot\frac45 = 0.8$ at 1.7;
  - $0.8\cdot\frac34 = 0.6$ at 3.2;
  - $0.6\cdot\frac23 = 0.4$ at 6.0.
  - So the **median is 6.0**.
  - *Dropping* the never-switching site would wrongly give 3.2. Censoring keeps the estimate
    honest.
- **AUROC.** Four sites:
  - risks 2.5 and 1.0, label 1 (reverted);
  - risks 0.3 and −1.2, label 0 (correct).
  - Every reverted site ranks above every correct one, so AUROC = **1.0**. Swap one pair and
    it drops to 0.75. A useless score gives 0.5.
- **Why "identity ≥ 0.10" means AUROC ≥ 0.60.** The identity baseline is the same for every
  eligible site, so its AUROC is exactly 0.5. Criterion C1 therefore asks for AUROC ≥ 0.60
  with an interval above 0.5 (deviation D6).

**Code:**

- [`kstar.kaplan_meier`](src/p33/kstar.py#L124)
- [`h4.auroc`](src/p33/h4.py#L52)
- [`h4.criteria`](src/p33/h4.py#L437)
- [`analysis.cluster_bootstrap`](../src/phase3_2/analysis.py#L103)
- [`power.py`](src/p33/power.py)
- [`scripts/scale_analysis.py`](scripts/scale_analysis.py) (D11)

---

## 5. Results

### 5.1 Development (exploratory)

The development run (`dev-20261006a`): 4 models, `dom` only, 852 sites, 10,224 Arm A and
16,000 extinction rows, about 17 A100-minutes. Its results:

- **Reversion with the table:** 0.39–0.58 by model and lexicon.
- **Rule effect:** +0.08 to +0.36 nats; only 1 of 32 intervals excluded zero.
- **`k*` medians:** 3.6–6.2 examples; 13–22% censored.
- **H4 AUROC:** 0.869 (0.5B) and 0.935 (1.5B); C1 and C2 met *in development*.

### 5.2 Held-out (confirmatory)

The held-out run (`heldout-20261007a`):

- 21 models;
- `dom` + `blk` × 5 held-out lexicons;
- 1,515 sites per model and family: 190,890 Arm A rows and 84,000 extinction rows, with
  0 failed cells.

**H4 holds:**

- **C1 and C2 are MET in all 20 tests** (10 base/instruct pairs × 2 grammar families), each
  with Holm p = 0.001.
- AUROC ranges from **0.76 (7B) to 0.96 (1.5B)**. The within-lexicon AUROC is just as high, so
  the score separates *sites*, not just lexicons.
- Against the role-level baseline the score is better in 20/20 comparisons, with the interval
  above zero in 16. The prediction is site-specific.
- C3 stays NOT TESTABLE as registered. (`blk` AUROCs are 0.76–0.95, but `blk` is not a
  held-out grammar.)

**Reversion does not shrink with scale.** With the table, all 21 models revert on
**40–56%** of sites. The D11 scale analysis (Qwen2.5-Coder, 0.5B → 32B):

| family | reversion, base | reversion, instruct | H4 AUROC |
|---|---|---|---|
| `dom` | −0.001 per 10× (Holm p = 1.0) | −0.014 (1.0) | **−0.081 per 10× (none of 2,000 bootstrap slopes ≥ 0: p < 0.0005, Holm p < 0.003)** |
| `blk` | +0.033 (Holm p = 0.07) | −0.013 (1.0) | −0.037 (Holm p = 0.055) |

**In words.** Bigger models revert just as often. In `dom`, their failures are slightly
*less* predictable from the base model, but the AUROC stays at 0.76 or above.

**The table helps, but not enough.**

- The rule effect is positive for every model: about +0.2 to +0.6 nats.
- 59–71 of 105 model × lexicon cells have an interval above zero, and none below.
- Even so, about half the sites still revert.

**Adaptation (`k*`, Kaplan–Meier median, sites wrong at k = 0):**

| | `dom` (familiar) | `blk` (unfamiliar) |
|---|---|---|
| median examples to switch | 1.4–4.6 | 3.3–11.6 |
| never switch within 32 | 6–28% | 12–29% |
| curves that wobble | 93–99% | 94–100% |

**Exploratory cuts (pooled over models; not preregistered):**

| | `dom` | `blk` |
|---|---|---|
| sigils (`#`, `.`) | 1.3 examples | 3.2 |
| keywords | 2.9 | 9.0 |
| **verbs (method names)** | **6.6, and 34% never switch** | **11.4, and 35% never** |
| 25% of symbols respelled | 5.4 | 10.2 |
| 50% / 75% respelled | 1.6 / 2.2 | 5.8 / 6.2 |
| base / instruct | 2.4 / 3.0 | 5.8 / 7.2 |

Two things stand out:

- **Punctuation adapts fast, words do not.**
- **A *partly* changed language is harder to adopt than a heavily changed one.** A plausible
  reading: when most of it looks familiar, old habits dominate. Each density level rests on
  one to three lexicons, so this needs confirmation.

**Robustness.** Three paraphrases of the prompt change reversion by at most 0.13 (usually
under 0.08).

### 5.3 Still running (results tomorrow)

- **Arm B:** the instruct models *write* programs from natural-language requests. Does
  reversion show up in real generated code?
- **H5:** do targeted respellings beat random ones?
- **The final export.**

---

## 6. For the meeting

### 6.1 A two-minute story

1. "We test whether code models follow a **redefined** language, or fall back on what they
   learned."
2. "We measure it at the exact token where the choice is made, as a log-probability margin,
   with leak-free examples, a length-matched control, and statistics that treat each program
   family as one unit."
3. "We preregistered, built and froze everything on 4 small models. We then tested once on
   held-out mappings and 21 models up to 72B."
4. "The confirmatory claim holds everywhere: a base model's own margin predicts where its
   instruction-tuned twin will fail (AUROC 0.76–0.96)."
5. "Scale doesn't fix it: even 72B models revert on about half the sites with the table in
   front of them."
6. "Few-shot adaptation is fast for punctuation, slow and often incomplete for renamed words,
   and almost never smooth."

### 6.2 Questions you will likely get

- **Why the first divergent token?** That is where the two spellings actually compete. Scoring
  whole strings would mix in tokenization length. The code refuses any pair it cannot compare
  cleanly.
- **Is H4 trivial, since the instruct model is fine-tuned from the base?** Shared pretraining
  is exactly the hypothesis: the prior survives instruction tuning. Three checks say it is not
  trivial:
  - the score beats identity and length baselines by +0.14 to +0.49 AUROC;
  - it beats a role-level baseline in 20/20 comparisons;
  - it works *within* each lexicon.
- **Why resample templates, not sites?** Sites from one program are correlated (the pilot ICC
  was 0.25 for the rule effect), so treating them as independent would make the intervals far
  too narrow.
- **Was anything tuned on held-out data?** No. The code, calibration and model revisions were
  frozen, and each held-out job re-checked the code hashes. The one post-freeze addition, the
  D11 scale analysis, was written and approved before any held-out outcome was examined, and is
  timestamped in git.
- **What can't you claim?**
  - generalisation to a brand-new grammar (C3 is not testable);
  - causal effects of size (sizes are not randomized);
  - the exploratory cuts (roles, density, instruct vs base) as confirmed.
- **What about the old "6 examples" result?** It was withdrawn: its examples leaked the answer.
  The corrected held-out numbers are 1.4–4.6 examples for `dom` and 3–12 for `blk`, with
  censoring and wobble reported.

---

## 7. Where the details are (after the meeting)

| topic | file |
|---|---|
| step-by-step commands on Sol | [`README.md`](README.md) |
| every concept explained in depth | [`sol_experiment_explained/00_complete_guide.md`](sol_experiment_explained/00_complete_guide.md) and 01–08 |
| all formulas with worked numbers | [`sol_experiment_explained/02_mathematics_and_statistics.md`](sol_experiment_explained/02_mathematics_and_statistics.md) |
| the preregistration and every deviation (D1–D11) | [`../PREREGISTRATION.md`](../PREREGISTRATION.md) |
| what was wrong and how it was fixed | [`AUDIT.md`](AUDIT.md) |
| results on Sol | `~/phase3-3_experiment_sol/results/heldout-20261007a/` (official, after the export); `/scratch/dkhorami/p33_preview_20261008/` (the preview used here) |
