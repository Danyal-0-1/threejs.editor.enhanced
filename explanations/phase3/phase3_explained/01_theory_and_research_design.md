# 01 — Theory and research design

> **How to read this.** Every important idea gets a precise definition, a plain
> one, a concrete example from this repository, and — where it is something the
> code computes — what can silently go wrong and which test catches it. Terms
> are defined where they first appear. Nothing here assumes you have read the
> literature review.

---

## 1. The original hypothesis, and why it was too broad

The project began with:

> LLMs generate DSLs well mainly because those DSLs resemble syntax densely
> represented during pretraining, rather than because of general rule-following
> or reasoning ability.

**Why this cannot be tested as written.** Three separate problems:

1. **"Reasoning" vs "pattern matching" is a false dichotomy.** Neither is a
   measurable quantity. There is no experiment whose outcome distinguishes
   them, because nobody has defined what measurement would.
2. **"Mainly" has no estimand.** An estimand is the precise numerical quantity
   an experiment estimates. "Mainly" names no number, so no result can confirm
   or refute it.
3. **The design confounds four things at once.** Changing the surface changes
   familiarity, tokenization, prompt interpretation *and* language design
   together. A difference in accuracy cannot be attributed to any one of them.

The weaker version — "familiar syntax outperforms unfamiliar syntax" — is
testable but **already established** (PLSemanticsBench; Miceli Barone et al.
2023; TokDrift). Restating it is not a contribution.

## 2. What the prior literature already settled

| Claim | Status | Key work |
|---|---|---|
| Familiar syntax often beats reassigned/unfamiliar syntax | established | PLSemanticsBench (ICML 2026); Identifier Swaps (Findings ACL 2023) |
| Reassigning familiar symbols can hurt more than novel symbols | established | PLSemanticsBench KeywordSwap vs KeywordObf |
| Explicit prompt definitions do not fully override pretrained meaning | established | Persistent Priors; When Models Ignore Definitions |
| Grammar/API context improves DSL generation | established | Grammar Prompting (NeurIPS 2023); Context-Aware Text2DSL |
| Constrained decoding fixes form, not necessarily meaning | partly established | Hidden Cost of Structure (RANLP 2025) |
| Model-aligned naming improves tool reliability | established | PA-Tool (ACL 2026) |
| Memory/context components mediate conflict | established in selected tasks | Yu et al. 2023; Jin et al. 2024 |

**Consequence:** Phase 3 must not claim any row above as new.

## 3. The narrow hypothesis that remains open

Two distinct claims, deliberately separated because one is far safer:

**H4 — exact-site prediction (the headline track).**
> A base checkpoint's preference between the two competing spellings *at an
> exact grammar position* predicts which positions an instruction checkpoint
> will get wrong, on unseen mappings and unseen grammar families.

**H2 — the interaction (secondary).**
> Reversion rises super-additively when a strong competitor prior meets an
> immediate context that specifically cues that competitor.

Phase 3 puts **H4 first**. H4 needs only a *main effect* of prior strength at
sites. H2 needs an interaction, which is both more fragile and more easily
preempted. Ordering H4 first means a null H2 costs one experiment, not the
programme.

---

## 4. Core concepts

### 4.1 Pretrained association (not "corpus frequency")

- **Technical.** The degree to which a model's parameters favour one
  continuation over another in a stated neutral context, measured as a
  log-probability difference on a *base* (non-instruction-tuned) checkpoint.
- **Simple.** How strongly the model expects one spelling rather than another,
  before you tell it anything.
- **Example.** In `('` context, Qwen base assigns higher probability to `.`
  than to `#`, because CSS class selectors are everywhere in its training data.
- **Why the name matters.** We cannot observe the pretraining corpus for most
  models, so we cannot measure *frequency*. We measure *model preference*. The
  review is emphatic about this and so is `measure/prior_strength.py`'s own
  docstring: "'Zero training priors' is unprovable and is never claimed."
- **Silent failure.** Writing "frequency" in the paper invites a reviewer to
  ask for corpus counts you do not have.

### 4.2 Surface familiarity

- **Technical.** A property of the *concrete syntax* (the spellings), holding
  the abstract syntax and semantics fixed.
- **Simple.** Same program, different-looking characters.
- **Example.** `$S('.wheel').recolor('#111')` and its `delta` twin express an
  identical canonical IR; only the spellings differ.
- **Assumption it depends on.** That the two surfaces really are isomorphic.
  In this repo that is enforced mechanically: invariants I1–I4 freeze the
  non-terminals and production shapes, and `render_grammar.py` asserts that
  φ=identity reproduces the Phase 1 grammar byte-for-byte.

### 4.3 Prompt-local rule following

- **Technical.** Conditioning output on a specification supplied in-context
  rather than on in-weight defaults.
- **Simple.** Doing what the prompt just told you, not what you usually do.
- **Example.** The prompt says "the class sigil is `#`"; following that rule
  means emitting `#wheel`, not `.wheel`.

### 4.4 Familiar-token reversion

- **Technical.** Emitting a **predeclared** competitor `q` at a decision site
  where the specification requires `c`.
- **Simple.** Falling back to the habitual spelling.
- **Crucial restriction.** "Reversion" applies **only** when `q` was named in
  advance. Labelling every error in an alien language a reversion is the single
  easiest way to inflate the effect. `sites.Site` stores `competitor` at
  construction time precisely so the label cannot be assigned after the fact.
- **Caught by.** `outcomes.observe_site` scores reversion on the terminal
  **role** the emitted spelling denotes, not on string equality, so an
  unrelated token that happens to share a spelling is not miscounted.

### 4.5 Local syntactic activation

- **Technical.** The degree to which the immediately preceding text raises the
  competitor's probability *specifically*, relative to a neutral prefix, with
  no rule present.
- **Simple.** How much the nearby code "looks like" the place the old habit
  belongs.
- **Example.** A prefix ending `$S('` is a strong CSS-selector cue; a prefix
  ending in an unfamiliar frame is not.
- **Silent failure.** Building a "low activation" prefix that is simply
  *harder* overall. Then you have raised entropy for every token, not lowered
  support for `q`. The manipulation check is that the change must be
  **candidate-specific**.
- **Status in Phase 3.** **Not implemented.** See §9.

### 4.6 Token identity vs tokenization

- **Token identity** = which character string. **Tokenization** = how the
  tokenizer splits it into model tokens.
- **Simple.** Same letters can cost different numbers of model steps.
- **Example.** `castShadow` and `wireframe` are both one *word* but may be two
  and one model tokens respectively.
- **Common confusion.** Equal-length strings are *not* automatically
  token-matched.

### 4.7 Token fertility — a confound, not a finding

- **Technical.** Tokens per character (or per program) under a given tokenizer.
- **Simple.** How finely the tokenizer chops your language up.
- **Example.** Relative Qwen fertility in Phase 2 was alpha 1.068, beta 1.401,
  gamma 1.937 — and beta, the *middle* one, sometimes outperformed identity.
- **Why it is a confound.** Fertility co-varies with language identity, so an
  accuracy difference cannot be attributed to familiarity. Worse, it is
  **unmatchable by selection** when you have only three languages.
- **What Phase 3 does about it.** `delta` fixes it by *construction*: because
  it permutes 3DOM's own spellings, the multiset of spellings is nearly
  unchanged. Measured mean character-length ratio is **1.0078** vs identity
  (alpha 0.978, gamma 0.713).
- **⚠ Honest limit.** Character length is **not** fertility. The real check
  needs a tokenizer and **has not been run**.

### 4.8 Grammar validity vs semantic correctness

- **Technical.** Validity = membership in the language. Correctness = the
  canonical IR equals the target IR.
- **Simple.** "Is it well-formed?" and "does it do the right thing?" are
  different questions.
- **Example.** A `delta` program using `.door` where `#door` was required
  parses perfectly and edits the *wrong* object.
- **Rule.** Never average them. `SCORING_POLICY.md` §1 forbids it and
  `outcomes.Outcome` keeps `parse_valid` and `task_correct` as separate fields.

### 4.9 The three collision classes (Phase 3's central idea)

Substituting the familiar spelling `q` for the correct `c` at a site has
exactly three possible outcomes, and only one is scientifically usable:

| Class | What happens | Usable? |
|---|---|---|
| **LEXICAL** | the variant does not lex/parse | ✗ loud failure |
| **BENIGN** | parses to the **same** IR — `q` is an alias | ✗ no contrast |
| **SEMANTIC** | parses to a **different** IR | ✓ **the only usable class** |

The review requires sites where both forms are grammar-valid but mean
different things. That is exactly **SEMANTIC**. It is a property of the
particular φ-map, and `sites.classify` **tests** it rather than assuming it.

**Measured consequence:** `beta` and `gamma` have **zero** SEMANTIC sites, and
alpha's famous `T_CLASS_SIGIL` site is **LEXICAL**.

### 4.10 Teacher-forced preference vs unrestricted generation

- **Teacher-forced (Arm A).** Supply the exact prefix; read off
  `log P(c) − log P(q)`. No decoding, no sampling, high statistical efficiency.
- **Unrestricted (Arm B).** Let the model write the whole program; parse it.
- **Simple.** "Which would you prefer?" vs "what did you actually write?"
- **Why both.** Arm A is efficient but artificial; Arm B is ecological but
  noisy and subject to opportunity bias (§4.11).

### 4.11 Decision-site opportunity bias

- **Technical.** An observed reversion requires two events: reaching a
  comparable decision site (`O=1`), then choosing the competitor (`Y=1`).
- **Simple.** You cannot make a mistake at a place you never got to.
- **Example — the real one.** Experiment 02 reported `3/3` bare reversions vs
  `15/20` scaffolded, and read it as "scaffolding increases reversion." It
  cannot: bare generation created only **three** opportunities because most
  bare outputs never parsed far enough. Conditional on reaching the site, bare
  reversion was 100% and scaffolded 75% — the *opposite* direction.
- **Caught by.** `outcomes.hurdle`, which has no single "reversion rate" field
  by design. Test: `test_hurdle_separates_reach_from_choice`.

### 4.12 Canonical IR, and why it is required

- **Technical.** A normal form such that two programs have the same canonical
  JSON (and SHA-256) **iff** they mean the same thing.
- **Simple.** A fingerprint of meaning that ignores spelling and formatting.
- **Example.** `canonicalize.content_hash` deliberately **excludes** `source`
  (rule C7), so the identity and delta renderings of one program hash equally.
- **Why required.** Without it, "semantically correct" would be string
  comparison, and every surface change would look like a semantic change —
  which would make the entire study circular.

### 4.13 Correlation, prediction, intervention, causation

| Level | Question | Phase 3 |
|---|---|---|
| Correlation | do they co-vary? | site risk vs reversion, in-sample |
| **Prediction** | does it work on **unseen** data? | **H4** — the headline |
| Intervention | does changing X change Y? | **H5** repair |
| Causation | is the mechanism established? | deferred to Phase 4 |

Prediction requires held-out data. An in-sample regression coefficient is not
a predictive result.

### 4.14 Counterbalancing

- **Technical.** Rotating which spelling carries which meaning across items so
  that no token is always correct.
- **Simple.** Don't let the model win by memorising "`#` is always right."
- **Status.** **Not implemented** (§9).

### 4.15 Factorial design and interaction

- **Factorial.** Cross two factors so every combination occurs.
- **Interaction.** The effect of one factor *depends on* the level of the
  other. Formally a difference of differences.
- **The trap.** On a transformed scale (log-probability, logit) an *ordinal*
  interaction can be produced by a compressive nonlinearity alone. Two factors
  pushing the same direction generically give "super-additivity."
- **What Phase 3 does.** The primary estimand is a **threshold** (§4.16); the
  DiD is secondary and reported on three scales with a sign-agreement rule.
  `scoring.interaction_did` returns `sign_agrees` and `verdict()` says
  `SCALE-DEPENDENT` when they disagree.

### 4.16 The extinction threshold `k*` (the primary estimand)

- **Technical.** The smallest number of in-context examples at which `M_seq`
  crosses from negative to positive, linearly interpolated between rungs.
- **Simple.** How many examples it takes to break the habit.
- **Why primary.** A threshold is read off the **x-axis**; rescaling the y-axis
  monotonically cannot move it the way it moves a difference of two gaps. It
  therefore survives the §4.15 critique.
- **Censoring.** Curves that never cross are `k_star=None, censored=True`.
  Dropping them would bias `k*` downward exactly where the prior is strongest.

### 4.17 Held-out mappings and grammar families

- **Mapping** = one assignment of spellings to roles (a φ-map).
- **Grammar family** = a genuinely different concrete syntax.
- **⚠ The trap this repo is in.** `alpha/beta/gamma/delta` are four *lexicons*
  over **one** grammar. I1–I4 freeze N and the shape of P. They are by
  construction what the review calls "cosmetic renamings of one grammar."
  A real second family is new design work and does not exist yet.

### 4.18 Falsification criteria

H4 is **not supported** if, with adequate power:
- site risk does not beat the `length` and `language_identity` baselines
  (`linter.rank_report` computes both);
- AUROC collapses on held-out mappings or an unseen grammar family;
- the score only separates lexicons, not sites within a lexicon.

H2 is **not supported** if:
- the DiD sign disagrees across the three scales (`sign_agrees == False`);
- the interval excludes the smallest meaningful effect;
- it reverses on held-out grammars.

### 4.19 The behavioural gate

No mechanistic work (activation patching, path patching) begins until a
behavioural effect replicates on held-out mappings **and** at least one
held-out grammar family. Explaining a non-robust effect is wasted effort, and
mechanism is the most preempted part of the programme.

### 4.20 Claims Phase 3 must not make

| Do not say | Say instead |
|---|---|
| "Models don't reason." | "Under these remappings the models often fail to condition on the supplied rule." |
| "Models only pattern-match." | "Local distributional associations measurably compete with the specified mapping at these sites." |
| "Larger models rely more on priors." | "Scaling patterns are heterogeneous; size is not causally isolated." |
| "Fertility causes semantic failure." | "Fertility is a plausible confound; causal attribution needs matched interventions." |
| "Gamma shows Unicode is worse." | "Gamma is a lexer stress condition, not a clean isomorphic control." |
| "We found the memory head." | "This component promotes one source under this preregistered contrast." |
| "Scaffolding increases reversion." | "Scaffolding changes both reach and conditional choice; the raw counts cannot separate them." |

---

## 5. Theory → variable → code → metric

| Theory | Experimental variable | Code | Output metric |
|---|---|---|---|
| Surface familiarity | φ-map choice | `phi.load_candidate`, `scripts/make_delta.py` | lexicon id on every record |
| Collision is silent | collision class | `sites.classify` | `CollisionClass.SEMANTIC` |
| Both forms grammar-valid | parse check on the variant | `sites._safe_ir_hash` | `ir_hash_competitor is not None` |
| Different meanings | canonical IR inequality | `canonicalize.content_hash` | `ir_hash_competitor != ir_hash_correct` |
| Pretrained association | base-model margin, no rule | `linter.score_site` → `s_local` | `S_local` |
| Rule moves the model | rule-present minus rule-absent | `linter.score_site` → `s_shift` | `S_shift` |
| Prompt-local rule following | `M_seq` with rule present | `scoring.forced_prefix_margin` | `M_seq` |
| Habit strength / extinction | number of in-context examples | `scoring.extinction_curve` | **`k*`** (primary) |
| Prior × context interaction | T × A cells | `scoring.interaction_did` | DiD ×3 scales + `sign_agrees` |
| Opportunity bias | reach vs choice | `outcomes.observe_site`, `hurdle` | `P(O)`, `P(Y\|O)` |
| Grammar vs semantics | five-bucket taxonomy | `outcomes.evaluate` | `parse_valid`, `task_correct` |
| Exact-site prediction | risk ranking vs baselines | `linter.rank_report` | AUROC / AUPRC / P@10 |
| Semantics-preserving repair | new φ, IR equality proof | `linter.verify_repair` | pass/fail over 62 programs |
| Predictor ceiling | prefix identifiability | `sites.prefix_collisions` | 3 groups / 63 of 103 sites |

---

## 6. Learning resources

> **Verification note.** These were **not fetched or verified in this session**
> — I had no browsing in this run, and I will not claim a check I did not
> perform. They are canonical, stable URLs (python.org, ACL Anthology, arXiv
> abstract pages). Confirm before citing. Listed 2026-10-01.

| Resource | Teaches | Why you need it here | Read | Level | Time |
|---|---|---|---|---|---|
| [docs.python.org/3/library/dataclasses.html](https://docs.python.org/3/library/dataclasses.html) | dataclasses, `frozen=` | `Site`, `Outcome`, `MarginRecord` are all frozen dataclasses | "Module contents", `frozen` | beginner | 45 min |
| [docs.python.org/3/library/enum.html](https://docs.python.org/3/library/enum.html) | enums | `CollisionClass`, `Bucket` | basic tutorial | beginner | 20 min |
| [docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html) | `Protocol`, generics | `models.LM` is a structural Protocol | `Protocol` section | intermediate | 40 min |
| [lark-parser.readthedocs.io](https://lark-parser.readthedocs.io/) | Earley parsing, grammars | the reference recognizer in `transpiler.py` | "Grammar reference", "Earley" | intermediate | 2 h |
| [PLSemanticsBench, arXiv:2510.03415](https://arxiv.org/abs/2510.03415) | priors vs supplied semantics | the closest prior work; defines what is *not* novel | §3 setup, §5 results | intermediate | 2 h |
| [Identifier Swaps, ACL 2023](https://aclanthology.org/2023.findings-acl.19/) | reassignment of familiar identifiers | the original form of this question | full | intermediate | 1.5 h |
| [Grammar Prompting, NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/cd40d0d65bfebb894ccc9ea822b47fa8-Abstract-Conference.html) | grammar-conditioned DSL generation | the "context helps" baseline | §3–4 | intermediate | 1.5 h |
| Loftus (1978), "On interpretation of interactions", *Memory & Cognition* 6:312–319 | why ordinal interactions are scale-dependent | **the reason `k*` is primary, not the DiD** | whole (short) | intermediate | 1 h |

(Statistics-specific resources are in `02_mathematics_and_statistics.md`.)

---

## 7. What is implemented, and what is not

Honest status. Nothing below is described as working unless a test exercises it.

| Design element | Status |
|---|---|
| Collision classification (§4.9) | **tested** — 14 tests |
| Canonical-IR scoring (§4.12) | **tested** |
| Opportunity hurdle (§4.11) | **tested** |
| `M_seq` margins (§4.10) | **tested with `FakeLM`** |
| Extinction curve `k*` (§4.16) | **tested with `FakeLM`** |
| DiD + scale-agreement rule (§4.15) | **tested with synthetic cells** |
| Site-risk prediction (H4) | **tested with `FakeLM`**; no real model yet |
| Repair + IR proof (H5) | **tested** over all 62 programs |
| Prior-strength calibration (T levels) | **not implemented** |
| Local-context calibration (A levels, §4.5) | **not implemented** |
| Counterbalanced mappings (§4.14) | **not implemented** |
| Second grammar family (§4.17) | **not implemented** |
| Mixed-effects / power simulation | **not implemented** |
| Environment capture + run manifest | **not implemented** |
| Any real-model number | **not run** |

The top blocker is none of these individually: it is that after
`dedupe_by_prefix` only **40** prefix-distinct SEMANTIC sites exist. Fix
template diversity before building T and A levels on top of them.
