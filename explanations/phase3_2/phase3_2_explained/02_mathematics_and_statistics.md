# 02 — Mathematics and statistics (Phase 3.2)

> Companion to `phase3/phase3_explained/02_mathematics_and_statistics.md`,
> which defines the notation (`c_i`, `q_i`, `r_i`, `x_i`, `O_i`, `Y_i`),
> `M_seq` vs `G_tok`, the circular-activation trap, the DiD and its
> three-scale rule, `k*` and censoring, the hurdle, mixed-effects models and
> the prediction metrics. **Unchanged; not repeated.** This document covers
> the one equation Phase 3.2 corrects and the new quantities it introduces.

---

## 1. The corrected margin — first divergent token (P32-001)

### What Phase 3 computed

$$M^{\text{seq}} = \underbrace{\log P(c \mid r,x)}_{\text{tail after } |\text{tok}(r x)|} - \underbrace{\log P(q \mid r,x)}_{\text{tail after } |\text{tok}(r x)|}$$

with the tail taken as the tokens beyond `len(tok(prefix))`.

**The flaw.** That assumes `tok(prefix + c)` *extends* `tok(prefix)`. BPE is
greedy and does no such thing: it re-tokenises the whole string, and the
candidate frequently **merges** into the preceding token.

### What Phase 3.2 computes

Let $a = \text{tok}(r x c)$ and $b = \text{tok}(r x q)$, and let

$$k = \max\{\,j : a_{<j} = b_{<j}\,\}$$

be the first divergent token index. Then

$$M^{\text{seq}} = \sum_{j \ge k} \log P(a_j \mid a_{<j}) \;-\; \sum_{j \ge k} \log P(b_j \mid b_{<j})$$

- **Symbols.** `a`, `b` the two full token sequences; `k` the length of their
  common prefix; the sums run to each sequence's own end.
- **Expected sign.** `> 0` prefers the specified token; `< 0` is reversion.
  Unchanged.
- **Interpretation.** Log-odds of correct over competitor, conditioned on the
  **same** `k`-token context. The shared prefix contributes identically to
  both sums and cancels exactly, which is what makes the difference meaningful
  even when the candidates tokenise to different lengths.
- **Assumptions.** (i) `k < len(a)` or `k < len(b)` — otherwise the candidates
  are tokenisation-identical and there is no contrast; the code raises rather
  than returning a quiet number. (ii) Both scored by the same model and
  tokenizer. (iii) `k ≥ 1`, since the first token has no context to be scored
  against.
- **Common implementation mistake.** Taking `k` from the *character* prefix
  instead of the *token* prefix. Characters and tokens do not align; the
  merged token `('#` spans the boundary, so a character-level `k` would score
  part of the shared prefix on one side only.

### Why `k` is a property of the tokenizer, not the site

The same site has different `k` under different tokenizers, so `k_common` is
recorded per measurement in `MarginV2`. A cross-model comparison that assumed
a fixed `k` would be comparing different quantities.

### Measured effect of the correction

Qwen2.5-Coder-0.5B base, 240 prefix-distinct SEMANTIC sites, `d50s1`:

| | merged candidates | sigil reversion | overall reversion | median `M_seq` |
|---|---:|---:|---:|---:|
| Phase 3 scorer | 106/240 (44.2%) | 0.106 | 0.258 | 0.000 |
| P32-001 fixed | 106/240 (44.2%) | **0.515** | **0.504** | −0.041 |

The bias is **one-way**: merged sites returned `M_seq = 0`, which is not
negative, so they could only ever be scored as "no reversion." The defect can
understate reversion and never overstate it.

**Diagnostic to keep in every run:** the count of merged candidates and the
count of exact-zero margins *after* the fix. `run_arm_a.py` prints both. A
nonzero post-fix exact-zero count means some pair is still degenerate and
should be inspected, not averaged.

---

## 2. Token fertility, measured rather than approximated

$$F(\mathcal{C}) = \frac{\sum_{p \in \mathcal{C}} |\text{tok}(p)|}{\sum_{p \in \mathcal{C}} |p|}, \qquad F_{\text{rel}} = \frac{F(\mathcal{C}_\phi)}{F(\mathcal{C}_{\text{identity}})}$$

- **Expected value.** `F_rel = 1` means the lexicon costs the model no extra
  tokens; `> 1` means the alien surface fragments more.
- **Assumptions.** Same corpus of abstract programs on both sides — which is
  why templates are built as IR and rendered, so `C_φ` and `C_identity`
  express *identical* programs.
- **Common mistake — the one Phase 3 made.** Using **character length** as a
  proxy. Phase 3 reported 1.0078 and flagged it unverified. Real measurement:

| family | `F_rel` (measured) |
|---|---:|
| `dom` / delta family | **1.072 – 1.078** |
| `blk` / delta family | **1.003 – 1.009** |

The proxy understated the `dom` confound by roughly **10×**. Actual `dom`
fertility matches Phase 2's alpha (1.068), so **delta does not remove the
fertility confound in `dom`.** `blk` does, and is therefore the
fertility-controlled arm.

- **Why the two families differ.** In `dom`, `.recolor` is one common
  JavaScript token; remapping `.`→`#` makes it `#recolor`, which fragments.
  `blk` has no chain operator, so the penalty does not exist. This is a
  hypothesis consistent with the numbers, not a measured mechanism.

---

## 2b. The rule effect — the quantity P32-002 made unmeasurable

With two matched conditions, per site:

$$\text{rule effect}_i = M^{\text{seq}}_i(\text{rule}) - M^{\text{seq}}_i(\text{norule})$$

- **Symbols.** `rule` = the full φ table rendered into the prompt; `norule` =
  a length- and shape-matched control with the spellings withheld.
- **Expected sign.** Positive — supplying the correct mapping should move the
  margin toward the specified token.
- **Interpretation.** How many nats the authoritative table buys at this site.
  It is the instruction-side analogue of `S_shift` in `phase3.linter`.
- **Assumptions.** The two prompts differ *only* in the mapping. They do not
  differ in line count (36 both) but they do differ in length (1,527 vs 1,014
  chars), so a residual context-length effect cannot be excluded and the
  lengths are reported with every result.
- **Common mistake — the one that was made.** Omitting the table entirely and
  calling the preamble a rule. Then `M_seq` is not a reversion measure at all;
  it is raw prior preference, because the "correct" spelling was never
  specified. See P32-002.

**Measured.** Mean +0.156 to +0.222 nats; the table helps **52.6–59.2%** of
sites — barely above chance — while reversion stays at **0.42–0.46 with the
table present**. A 28-role authoritative mapping moves a 0.5B model's token
preference about as often as a coin flip.

---

## 3. Collision density

$$d_{\text{role}} = \frac{|\text{permuted roles}|}{|\text{substitutable roles}|}, \qquad d_{\text{site}} = \frac{|\text{SEMANTIC sites}|}{|\text{all sites}|}$$

- **Expected relation.** Monotone but **not equal**. Measured: `d_role = 0.45`
  gives `d_site ≈ 0.36`.
- **Why they differ.** Roles occur at different frequencies in the corpus.
  Permuting a rare role (pseudo keywords) adds few sites; permuting a common
  one (class sigil) adds many.
- **Common mistake.** Reporting the target density as if it were the achieved
  site density. `Member.density_actual` is the role fraction; the site
  fraction comes from the census. They are different numbers and both belong
  in the methods section.
- **Ceiling.** 306 of 387 sites (79%); the remaining 81 are `T_CHAIN_OP`,
  locked LEXICAL by I7. **Do not approach it** — H5 needs non-colliding
  control sites (see `01 §3`).

---

## 4. Stratified reversion

For stratum $s \in \{\text{sigil}, \text{verb}, \text{keyword}\}$:

$$\hat{R}_s = \frac{1}{|S_s|}\sum_{i \in S_s} \mathbb{1}[M^{\text{seq}}_i < 0]$$

- **The contrast that answers the 3D question.** $\hat{R}_{\text{sigil}}$ needs
  no domain knowledge; $\hat{R}_{\text{verb}}$ does.
  $\hat{R}_{\text{sigil}} \gtrsim \hat{R}_{\text{verb}}$ ⇒ domain competence is
  not driving the effect.
- **Measured** (6 checkpoints, n=240): sigil 0.439–0.583, verb 0.367–0.469.
  Sigil ≥ verb at **every** checkpoint.
- **Assumptions.** Strata are comparable in difficulty apart from the domain
  component — **not established**. Sigil candidates are single characters and
  verb candidates are words, so they differ in token length too. A
  length-matched sub-analysis is needed before this is a finding.
- **Common mistake.** Reading the stratum gap as an effect size. It is a
  **direction check** on a confound, at n=240 on one model family.

---

## 5. Worked example — the divergence computation

Site `dom:d50s1:t000:T_CLASS_SIGIL:0`, prefix ending `$S('`, `c = '#'`,
`q = '.'`, Qwen2.5-Coder tokenizer:

```
tok(prefix)      = [ …, 400, 50, 492 ]        len 12     492  = `('`
tok(prefix + '#')= [ …, 400, 50, 3515 ]       len 12     3515 = `('#`
tok(prefix + '.')= [ …, 400, 50, 4291 ]       len 12     4291 = `('.`
```

Phase 3: `len(all) <= len(pre)` → **0.0 for both** → `M_seq = 0`, "no reversion".

Phase 3.2: common prefix is the first 11 tokens, so `k = 11`.

$$M^{\text{seq}} = \log P(3515 \mid a_{<11}) - \log P(4291 \mid b_{<11})$$

One token scored per side, same 11-token context, difference meaningful. Note
`n_tok_correct = n_tok_competitor = 1` here — the merge means the *sigil* is
never a token of its own, and the contrast is carried entirely by which merged
token follows `$S`.

---

## 6. What is still not implemented

Unchanged from Phase 3, and still honest:

| Quantity | Status |
|---|---|
| prior-strength `T` calibration | **not implemented** |
| local-context `A` calibration | **not implemented** |
| mixed-effects model (§8 of the Phase 3 doc) | **not implemented** — needs `statsmodels` |
| power simulation | **not implemented** |
| bootstrap intervals at template level | **not implemented** |
| extinction curves on a real model | code exists (`phase3.scoring`), **not run** |
| rule-effect intervals | **not implemented** — point estimates only |
| calibration slope / Brier | **not implemented** |

Every real-model number in Phase 3.2 is a **point estimate with no interval**.
Treat all of them as direction checks.

---

## 7. Learning resources (additions only)

> **Not fetched or verified in this session.** Canonical URLs. Listed 2026-10-02.

| Resource | Teaches | Why here | Read | Level | Time |
|---|---|---|---|---|---|
| [Sennrich et al. 2016 (arXiv:1508.07909)](https://arxiv.org/abs/1508.07909) | BPE merge behaviour | the mechanism behind P32-001 | §3 | intermediate | 1 h |
| [HF tokenizers pipeline](https://huggingface.co/docs/tokenizers/pipeline) | re-tokenisation is global, not incremental | why `tok(x+y) != tok(x)+tok(y)` | "Model", "Post-processing" | intermediate | 1.5 h |
| [PyTorch `log_softmax`](https://pytorch.org/docs/stable/generated/torch.nn.functional.log_softmax.html) | logits → log-probs | `_score_from` | the page | intermediate | 30 min |
| [HF causal LM task guide](https://huggingface.co/docs/transformers/tasks/language_modeling) | the `logits[:-1]` / `ids[1:]` shift | the off-by-one in `_score_from` | "Causal language modeling" | intermediate | 1.5 h |
