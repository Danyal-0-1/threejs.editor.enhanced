# Hypothesis-strength and compute-strategy analysis

**Date:** 25 September 2026
**Inputs read:** `litreture_reveiw_1.md` (the audit), `litreture_review_2.md` (the prompt that produced it), `run/experiments/tokenizer_avoided/20260914T212711Z/*` (Experiment 02 results), `alien_syntax/src/phi.py`, `alien_syntax/measure/*`, `project_status/phase2.md`
**Status:** my own adversarial read, written to disagree with the audit where I think it is wrong
**Purpose:** (1) is the refined hypothesis strong enough to build the whole pipeline on? (2) what compute-enabled angles are missing, given A100 + ASU Sol access?

> **One caveat up front.** My own knowledge cutoff is earlier than the audit's 23 Sep 2026 literature cutoff. I have not independently verified the 2026 citations in `litreture_reveiw_1.md` (Persistent Priors, Conflict and Congruency, A Mechanistic Lens, Override Gap, TokDrift, PA-Tool's ACL 2026 record, Anka). I take them as reported. Everything below about *your* experiments, *your* code, and the *structure* of the argument is verified against the repo.

---

## Part 0 — TL;DR

**On the hypothesis.** The refined H2 interaction is real research, but it is **not strong enough to justify building the entire pipeline around it.** It is a single contrast, it is fragile to a measurement problem the audit never raises (Section 2.1), one of its two factors is not actually randomized (2.2), and it sits in a fast-moving space where three of the closest works are live preprints. If H2 comes back null, the audit's own stop rule (`Stage 1 → stop`) throws away the whole program.

**The fix is a reframe, not a retreat.** Build the pipeline for the **artifact** — a parity-checked, IR-grounded, counterbalanced multi-grammar *platform* — and treat H2 as the first experiment you run on it rather than its reason for existing. Two of the three "apparently unstudied" contributions (held-out exact-site prediction, minimal semantics-preserving repair) **do not depend on the interaction at all**, and the audit gates them behind it anyway. That sequencing is wrong and it is the most consequential error in the review.

**On compute.** The A100/Sol unlock does *not* mainly buy you the mechanistic phase — mechanism is design-bound, not compute-bound, and it is the most preempted part of the program. It buys you four things nobody in your lit table has done for DSL surfaces:

1. **Extinction curves** — how many in-context examples to erase the prior, as a function of prior strength. Dose-response instead of a binary interaction, which *structurally immunizes you* against the scale critique in 2.1. Best ROI in the whole document.
2. **Corpus-grounded priors** — replace "model preference" with *measured pretraining frequency* using open-data models (OLMo/Dolma, StarCoder2/The Stack v2). This is a CPU-and-storage job, i.e. the thing Sol is uniquely good for and A100s are not.
3. **Training the prior instead of selecting it** — controlled continued-pretraining where competitor frequency × context-specificity are set by you. Converts H2 from correlational to causal.
4. **Tokenizer-equalized fertility arm** — kill the fertility confound by construction rather than by matching.

And one thing to *stop* doing: Arm A (forced-prefix scoring) is essentially free at A100 scale — single-digit GPU-hours across twenty checkpoints. You have been rationing the cheapest measurement you own.

---

# Part 1 — What the new hypothesis is actually looking for

## 1.1 Plain restatement

Strip the notation and H2 says:

> A model has an old habit (`.` means "class selector"). Your prompt tells it the new rule (`#` means that now). The claim is that the habit wins **specifically and disproportionately** at the exact spot where the surrounding code *looks like* the context that trained the habit — not merely everywhere the habit-token appears.

Two independently-set dials:

| dial | what it is | how you set it |
|---|---|---|
| **T** — competitor prior strength | how much the base model prefers `q` over `c` with no rule present | *pick* token pairs whose neutral-context margin is small/medium/large |
| **A** — local competitor activation | how much the immediately preceding text cues `q` specifically | *construct* prefixes that all lower to the same AST but differ in CSS-likeness |

The claim is the **interaction**, not either main effect: the high-vs-low context gap should *grow* as T grows.

## 1.2 What it would buy you if true

This is the part worth defending. A confirmed H2 gives you a **locality result**: interference is not a property of the token, it is a property of the (token, position, neighborhood) triple. That has three real consequences:

- **Diagnostically:** you can score a grammar *before* generating anything and say "this spelling is safe here, dangerous there." Token-level familiarity scores (PA-Tool peakedness, fertility) cannot do this because they have no position argument.
- **For DSL design:** the advice changes from "don't reuse familiar symbols" (impractical — every DSL inherits a host-language look) to "don't reuse a familiar symbol *in the position where it normally appears*." That is an actionable, cheap, non-obvious rule.
- **Mechanistically:** it licenses the two-route question. Without locality, "remote rule vs local prefix" has no purchase, because there is no local factor to vary.

Your Experiment 02 data genuinely motivates this. `7B/alpha` at 0.0% bare and 4.8% scaffolded, against `7B/identity` at 71.4%/90.5%, is a spectacular collapse — and it is *not* monotone in surprisal, since `gamma` has ~4.7× alpha's ΔNLL/char and does far better (33.3%/38.1%). Something other than raw distance is operating in alpha. That is the honest core of the project and it is a good observation.

## 1.3 But that motivation has a confound baked into your own artifact

`alien_syntax/src/phi.py` documents invariant **I7**: `T_CHAIN_OP` and `T_CLASS_SIGIL` are two distinct terminal IDs that in 3DOM share the spelling `.`, and the validator (V5/V6) *requires* them to share their alien spelling too. `collisions.py` check (c) enforces it.

So when 7B/alpha emits `.` where the spec says `#`, you cannot currently distinguish:

- **role-specific reversion** — it reverted the *class-sigil* role, and the chain-op role is incidental; versus
- **character-level reversion** — it reverted the glyph `.`, indifferent to which of the two roles it is filling.

These are exactly the two readings of your "the same reassigned symbol appeared to survive in another syntactic location" note, and H2 lives or dies on the difference. **This confound is not in the literature — it is in your φ-map**, and your own docstring already tells you the escape hatch:

> `set overload_groups: [] in the φ-map and V5/V6 relax accordingly; that is the whole cost of the change.`

**This is the single cheapest high-information experiment you own.** A φ variant that gives the two roles *different* spellings turns one ambiguous observation into a clean 2×2. The honest cost, which `phi.py` also states, is that de-overloading makes the alien language strictly easier to lex than 3DOM, so it breaks complexity-matching — run it as a declared diagnostic arm with the deviation stated, not as your main isomorphic condition. It is a config change and a rerun, on hardware you already have.

---

# Part 2 — Is it strong enough to build the whole pipeline on?

**My verdict: no, not as the load-bearing claim.** Six reasons, in descending order of how much they should change your plan. The first two are not in the audit.

## 2.1 The interaction is scale-dependent, and the audit never says so ⚠️ *biggest threat*

This is the one that worries me most, because it can make you *see* H2 when nothing mechanistic is there.

H2's primary endpoint is a difference-in-differences on a log-probability margin. **A difference of differences on a monotone-transformed scale is not a fact about the world; it is partly a fact about the scale.** Two factors that both push the same direction will generically produce super-additivity on one scale and additivity or sub-additivity on another. This is the classic Loftus (1978) warning about interpreting interactions when the dependent variable's scale is not independently justified, and it bites hardest for *ordinal* (non-crossover) interactions — which is precisely the shape H2 predicts.

Concretely: if `T=neutral` sits near margin 0 and `T=strong` sits far out, you are comparing an effect measured in a near-linear regime against one measured in a compressed regime. You will find "super-additivity" from the compressive nonlinearity alone. Reversion rate is bounded in [0,1]; logit is unbounded; `M^seq` is unbounded but its mapping to behavior is not. The audit specifies the endpoint carefully but never asks *why that scale*, and its falsification criteria (§8.6) do not include "the interaction vanishes under a defensible reparameterization."

**Three ways out, in order of strength:**

1. **Predict a crossover.** Qualitative (sign-reversing) interactions *are* transformation-invariant. If your theory can be sharpened to predict that low-A actively *protects* a strong-prior token — i.e. strong-prior/low-A does better than neutral-prior/low-A — you have a claim no reparameterization can erase. Worth an hour's thought: can the theory deliver a crossover?
2. **Go dose-response instead of factorial.** Estimate a *threshold* ("how much context support flips this site") rather than a contrast. Thresholds are far more robust to monotone rescaling than DiDs. See **E1** in Part 3 — this is the same reason I rank the extinction curve first.
3. **Preregister the scale-robustness check.** Report the interaction on ≥3 scales (probability, logit, and the raw sequence margin) plus a rank-based test, and declare in advance that H2 is supported only if the sign holds across all of them. This is the minimum. Do this regardless of 1 and 2.

If you build the full pipeline for a claim that evaporates under reparameterization, you will find out at review time.

## 2.2 T is *selected*, not randomized — so H2 is observational dressed as factorial

Read §8.1 of the audit closely. The T levels are defined as "candidate pair *with* near-zero / intermediate / large calibrated advantage." That is **selection on an observable**, not randomization. A is genuinely constructed and randomized; T is not, and cannot be, as long as manipulating it means *choosing different tokens*.

The audit half-sees this — it concedes "candidate identity necessarily changes in a token-selection design" and asks for tokenization matching and role counterbalancing. But matching on tokenization and role does not make T exogenous. Tokens with strong priors differ from tokens with weak priors in every correlated way: corpus frequency, morphological transparency, positional distribution in real code, co-occurrence structure, how many *other* roles they play. Any of these can drive the interaction.

So the honest framing of the whole design is: **A-randomized, T-stratified.** The causal claim is only about A; T is a moderator estimated observationally. That is publishable, but you must say it, and a reviewer who spots it before you do will treat it as a gotcha.

**The real fix requires compute** — you have to *create* the prior rather than find it. See **E3**. This is the strongest single argument for why the A100 access changes what paper you should write.

## 2.3 Conjunctive novelty discounts badly at review

The audit's §1 "what remains novel" is an **eight-item conjunction**. It is candid that this counts only if it yields a new falsifiable result, but then the paper's novelty rests on: no single prior work does all eight. Reviewers discount that heavily — the standard response is "each component is known; the combination is engineering." You need novelty that survives someone removing any two conjuncts. Of the three "apparently unstudied" claims, exactly one (the interaction) is a *scientific* claim and two (site prediction, minimal repair) are *artifact* claims. Artifact claims are far more robust to preemption because they are tied to a thing you built.

## 2.4 The gating order is backwards ⚠️ *most actionable*

The audit says, twice and emphatically:

> **Stop here** if the interaction is absent, unstable, fully tokenization-mediated, or does not generalize.

But look at what H4 (exact-site prediction) and H5 (targeted rewrite) actually require. They need a **main effect of T at sites** — "base-checkpoint margin at this exact position predicts instruction-model reversion." They do **not** need the interaction. A linter that flags risky sites and rewrites them minimally is valuable, testable, and publishable whether reversion risk is additive or super-additive in T and A.

So the audit gates its two most preemption-resistant contributions behind its most fragile one. **Invert it.** Build the site-prediction and repair track first: it is cheaper, it is the SE-venue story, it does not depend on H2's sign, and it produces the very apparatus (enumerated sites, competitor candidates, calibrated margins) that H2 needs anyway. Then H2 is a nearly-free follow-on experiment on infrastructure you already built for another reason.

## 2.5 The ecological-validity question you will be asked first

At ICSE/ASE/FSE, the first reviewer question is: *"Why would anyone design a DSL whose tokens collide with CSS meanings? Just pick different symbols."*

The Stroop framing has no good answer — it concedes the collision is artificial. The linter framing has an excellent one: **real DSLs inherit surface conventions from host languages and the collisions are accidental and invisible to their designers.** jQuery-like chaining, SQL-like clauses, YAML-like indentation, Terraform-like blocks — nobody sat down and chose to collide. A tool that surfaces the collisions before you ship the grammar is obviously useful; a Stroop effect in a language nobody uses is not. **This also argues for reordering toward the linter.**

## 2.6 The preemption clock

Persistent Priors is at v5. Conflict and Congruency is from Aug 2026. A Mechanistic Lens is Jul 2026. These are active preprints in a crowded area, and the audit places all three as direct or near-direct threats. A 12–18-month mechanistic program aimed at the interaction has a real chance of being scooped mid-flight. The parts that *cannot* be scooped are the ones welded to your artifact: the φ-validated isomorphic grammar families, the canonical-IR equality proof, the three-seam parity checking, the linter. Build those.

## 2.7 What I am *not* saying

I am not saying the science is bad. Your Phase 2 infrastructure is, frankly, more rigorous than most of what is in the audit's own table — bijectivity as a `frozenset` comparison, three independent recognizer seams, hash-excluding-source canonicalization, reachability-parity checking as a *theorem about glyph lexicons*. That is a genuine asset and most groups attempting this would confound themselves immediately. My argument is about **what to hang the pipeline on**, not whether to build it.

## 2.8 The reframe

> **Build the pipeline for the platform, not for the hypothesis.**

Concretely, the deliverable is: *a validated, counterbalanced, multi-grammar, IR-grounded benchmark and linter for surface-collision risk in prompt-defined DSLs* — with H2 as the headline scientific experiment run on it.

Under that framing:

- a **null H2** is a publishable negative result on a released benchmark, not a dead project;
- a **positive H2** is the headline and the mechanism phase becomes justified;
- the **linter** ships either way;
- and every stop rule in the audit's §13 stops *one experiment* instead of the program.

That is the difference between a bet and a portfolio.

---

# Part 3 — Compute edges you have not considered

Baseline for comparison: Experiment 02 ran on a laptop **RTX 3080 16GB**, fp32 base-model scoring, **7B forced onto CPU**, 21 generation cases, 1 completion each, one model family. Essentially every design limitation in the audit's "evidence boundary" is downstream of that machine.

A100s + Sol do not just make that bigger. They make *different* experiments possible. Ranked by scientific return per GPU-hour.

### First, recalibrate what things cost

| workload | rough cost | note |
|---|---|---|
| **Arm A** — forced-prefix scoring, 4,860 sites × 2 candidates | **single-digit A100-hours across ~20 checkpoints** | forward-only, short seqs; ~5M tokens per checkpoint |
| **Arm B** — unrestricted generation, same sites | **tens of A100-hours** for the same sweep | vLLM-batched; generation dominates |
| Extinction curves (E1), 0→128 shots | low hundreds of A100-hours | long-context forward passes dominate |
| Controlled pretraining (E3) | ~300–900 A100-hours | 18 runs; see below |
| Corpus indexing (E2) | **~0 GPU-hours**, TB-scale storage + CPU | Sol's actual comparative advantage |
| Mechanism Stages 3–5 | tens–low hundreds of A100-hours | *design*-bound, not compute-bound |

*(Rough figures: 6·N·D FLOPs for training at ~150 TFLOP/s effective bf16; forward-only at ~20–50k tok/s for 7B. Order-of-magnitude only.)*

**The headline:** your **primary endpoint is nearly free.** Arm A across Qwen + Llama + DeepSeek + StarCoder2 + OLMo, base *and* instruct, at several sizes, is a few GPU-hours. The audit asks for "at least two model families if compute allows" — at A100 scale that is not a concession, it is a rounding error. Stop treating the primary measurement as scarce.

---

### E1 — Extinction curves (dose-response, not a binary interaction) ★ best ROI

**The question:** not *whether* the prior interferes, but **how much in-context evidence it takes to extinguish it** — and whether that dose scales with prior strength and local context.

Sweep shots ∈ {0, 1, 2, 4, 8, 16, 32, 64, 128} crossed with your T and A levels. Estimate, per site, the **extinction threshold** `k*` = shots needed for the rule-consistent margin to cross zero.

**Why this is the best idea in this document:**

- It **structurally defeats the scale critique in 2.1.** A threshold on the x-axis is far more robust to monotone rescaling of the y-axis than a difference-of-differences. You are reading off *where* a curve crosses, not *how much* two gaps differ.
- It is a **dose-response curve**, which is the strongest form of observational evidence short of randomization, and reviewers know it.
- It **subsumes your scaffolding condition.** H3's bare-vs-scaffolded is a noisy 2-point sample of this curve — which is exactly why it produced the `3/3` vs `15/20` opportunity-bias mess. A curve has no opportunity-bias problem because you score margins, not reachability.
- It is **directly actionable**: "a colliding symbol costs you ~N extra examples" is a number a DSL designer can act on.
- The extinction/habit-strength framing is the *right* half of the Stroop analogy, and the audit's §11 never reaches for it.
- It gives you a clean, novel dependent variable: **relapse** — does reversion return at sites *after* the model has demonstrably learned the mapping elsewhere in the same completion? Nothing in your lit table measures within-completion relapse.

Compute: low hundreds of A100-hours for a full curve across ~8 checkpoints. Trivially parallel across shots × sites × checkpoints — ideal Sol array-job shape.

---

### E2 — Corpus-grounded priors: measure the prior instead of proxying it

**The gap this closes.** The audit concedes the central weakness of T in one sentence and moves on:

> Because pretraining data are not fully observable, `T_i` measures model preference—not literal corpus frequency.

For most models, true. But for **open-data** models it is false: OLMo-family (Dolma), Pythia (the Pile), StarCoder2 (The Stack v2). For those you can count the actual thing.

**What to do:** build (or query) suffix-array / infini-gram-style indexes over the pretraining corpus and measure, for each candidate site, the **contextual** frequency of `(prefix-shape, competitor)` versus `(prefix-shape, correct-token)` — not unigram frequency, the *conditional* count that A is supposed to be operationalizing. Then ask:

- Does corpus co-occurrence predict reversion **beyond** base-model likelihood? (If yes: you have a data-origin account, not just a behavioral one.)
- Is your constructed A-manipulation actually tracking real corpus contingencies, or did you construct prefixes that *feel* CSS-like to a human but are not distributionally distinctive? **This is a manipulation check you currently cannot run**, and if it fails, H2 was never testable with those materials.

**Why it is a Sol job specifically.** This is TB-scale storage, parallel I/O and CPU — a suffix array over The Stack v2 is roughly multi-TB — and **near-zero GPU**. It is the one thing in this document that a pile of A100s cannot do and a supercomputer's parallel filesystem can. Cheap tier first: public infini-gram/WIMBD-style APIs over Dolma/Pile before you build anything locally. *(Verify current API coverage — my information here predates your literature cutoff.)*

Nothing in your lit table does corpus-grounded prior measurement for *code surfaces*. The closest row, "How Training Data Shapes...", uses synthetic training.

---

### E3 — Train the prior instead of selecting it (fixes 2.2)

**The clean answer to "T is not randomized."** Stop looking for tokens with different priors. *Create* them.

Continued-pretrain (or train from scratch) on a corpus where you control:

- **frequency** of the competitor surface — the T dial, now genuinely manipulated;
- **context-specificity** — does the competitor appear only in the cueing frame, or everywhere? The A dial, now *also* in the training distribution rather than only in the prompt.

Then test override on the resulting checkpoints. Now the interaction is a **causal claim about pretraining exposure**, which is a strictly stronger and much more interesting result than a correlational claim about token identity. Conflict and Congruency's LoRA default-strengthening is the cheap version of this; the pretraining version dominates it.

Two tiers:

- **From scratch, ~100–300M params, ~6–10B tokens:** total data control, no contamination, ~20 A100-hours/run. 6 conditions × 3 seeds ≈ **360 A100-hours**. Small models will be weak at NL→DSL, so pair with forced-prefix margins (Arm A) rather than free generation.
- **Continued pretraining, ~1B, 2–5B tokens:** ~33 A100-hours/run, 18 runs ≈ **600 A100-hours**. Keeps real-model competence; costs you clean data provenance.

Either fits comfortably in a Sol allocation. Run E3 on an **open-data base model** so it composes with E2.

---

### E4 — Tokenizer-equalized fertility arm (kill the confound by construction)

Your fertility spread is 1.068 / 1.401 / 1.937 for alpha/beta/gamma. The audit correctly treats this as an unmatchable confound and asks you to match and report sensitivity. But matching cannot fully work — you have three fertility values and they are perfectly confounded with language identity.

**Construction beats matching.** Extend the tokenizer so alien spellings are single tokens, briefly continued-pretrain so the new embeddings are not random, and rerun. Fertility becomes a *manipulated* factor instead of a nuisance.

Honest trade: adding tokens and training perturbs the prior too, so this is a **sensitivity arm**, not a replacement for the main design. Its value is a clean disjunction — *if the effect survives fertility equalization, TokDrift-style tokenization explanations are ruled out; if it vanishes, you have found that your effect was tokenization, which is itself a real and reportable finding.* Either outcome is informative, which is the mark of a good experiment. Cheap: tens of A100-hours.

---

### E5 — The model sweep you have been rationing (near-free)

Because Arm A is single-digit GPU-hours, just do the full cross:

- **families:** Qwen2.5-Coder, Llama-3, DeepSeek-Coder, StarCoder2, OLMo — five tokenizers, not one;
- **matched base/instruct pairs at every size** — this is the axis that actually separates "pretraining prior" from "instruction tuning," and it is the inference your current base-NLL-to-instruct-accuracy link cannot support;
- **sizes** spanning 0.5B→32B+, reported as **replication strata**, never as a causal size effect.

The `3B/beta` cell that *beats* identity (+0.095 bare, +0.048 scaffolded) is either noise at n=21 or the single most interesting number in Experiment 02. At 5 families × 4 sizes × ~500 sites you will know which — and if it replicates, "an unfamiliar surface can outperform the familiar one" is a headline finding that converges with Anka from a controlled direction Anka cannot claim.

Also: **run more than one completion per case.** Experiment 02 is 1 greedy completion (3 reps only at 0.5B/1.5B, logged as deviation D1). Sampling-based pass@k and choice *distributions* at decision sites cost almost nothing now and give you per-site variance, which you currently do not have.

---

### E6 — Learnability, not just accuracy (the reframe with the longest legs)

Every question in the current program is *"which surface does a fixed model handle better?"* Flip it:

> **"Which surface can a model be *taught* fastest, and which one does it keep relapsing on?"**

Measure sample-efficiency of adaptation — fine-tuning curves, LoRA curves, ICL curves (E1 is the ICL slice) — as a function of surface familiarity and collision structure. Predictions the collision hypothesis makes that nothing else does:

- colliding surfaces are **slower to learn** at matched fertility;
- colliding surfaces show **higher relapse** — reversion recurs at collision sites after the model has demonstrably learned the mapping;
- **non-colliding unfamiliar** surfaces (your beta, Anka) may learn *faster* than familiar-but-remapped ones, because there is no habit to unlearn.

That last prediction is a **crossover** — the transformation-invariant kind from 2.1 — and if it holds it is the cleanest result available anywhere in this program.

Why it is a better paper: it is what a DSL designer in 2026 actually needs to know (adaptation cost, not zero-shot accuracy), it is much less preempted than the Stroop interaction, and it is fundamentally compute-hungry, i.e. exactly what you could not do before and can now.

---

### What *not* to spend the windfall on

**Do not start the mechanistic phase because you now have GPUs.** Stages 3–5 are limited by *design* — matched donor construction, position alignment, multiplicity control over layers × heads × MLPs × positions × paths, held-out grammar validation — not by FLOPs. A100s make a badly-designed patching study fail faster. It is also the most preempted part of your program (Conflict and Congruency; A Mechanistic Lens; the factual-conflict line), and the TMLR replication caveats the audit cites in §3 mean the bar for component-role claims is now high and rising. Mechanism last, and only after E1/E5 give you a robust phenomenon.

---

## Compute summary

| # | Edge | GPU cost | Resource shape | Fixes | Priority |
|---|---|---|---|---|---|
| **E1** | Extinction / dose-response curves | ~100–250 A100-h | array jobs, long ctx | **2.1** scale-dependence | **1** |
| **E5** | Multi-family × base/instruct sweep | <10 A100-h (Arm A) | trivially parallel | single-family limit | **2** |
| **E2** | Corpus-grounded priors | ~0 GPU, TB storage + CPU | **Sol-specific** | T-as-proxy; A manipulation check | **3** |
| **E6** | Learnability + relapse | ~200–500 A100-h | many small FT runs | "who cares"; preemption | **4** |
| **E3** | Train the prior | ~360–600 A100-h | multi-GPU training | **2.2** T not randomized | **5** |
| **E4** | Tokenizer-equalized fertility | tens of A100-h | short CPT | fertility confound | **6** |
| — | Mechanism Stages 3–5 | tens–hundreds | design-bound | — | **last** |

---

# Part 4 — Recommended sequencing

**Stage 0 — repair (unchanged from the audit, do it first).** Fix the extra-operation scorer defect + adversarial scorer tests; rescore all retained raw outputs; implement site-alignment and opportunity labels; preregister. *No new compute.* Nothing below is trustworthy until this lands.

**Stage 0.5 — the de-overloading diagnostic (new, ~1 day).** Build a φ variant with `overload_groups: []` so `T_CHAIN_OP` and `T_CLASS_SIGIL` get distinct spellings; rerun the alpha condition. Declare the lexing-complexity deviation. Answers "role or character?" — which H2's entire construction presumes. Runs on the 3080.

**Stage 1 — platform + site inventory (the reframe).** Enumerate substitutable sites and their IR roles; generate competitor candidates; build 2–3 *independently designed* grammar families (not cosmetic renamings); counterbalanced mapping rotations. **This is the pipeline, and it is justified by the linter alone.**

**Stage 2 — E5 + E1 together.** Arm A across five families and matched base/instruct pairs is hours. Extinction curves on top. **Decision gate:** is there a *phenomenon* — a reliable, replicating, scale-robust site-level effect?

**Stage 3 — H4/H5: the linter.** Exact-site prediction against the audit's §10.2 baselines; minimal semantics-preserving rewrite against §10.4 baselines. **Ships regardless of H2's sign.** This is your SE-venue paper.

**Stage 4 — H2 proper.** The 3×3, with the 2.1 scale-robustness preregistration and the 2.2 selected-vs-randomized framing stated openly. Cheap now, because Stages 1–3 built the apparatus.

**Stage 5 — E2/E3/E6**, chosen by what Stages 2–4 turned up.

**Stage 6 — mechanism**, only if a robust phenomenon survived.

## Next two weeks (no new hardware required)

1. Fix the scorer + adversarial tests; rescore retained outputs. *(Blocking.)*
2. Run the `overload_groups: []` diagnostic on alpha.
3. Write down, before any A100 time, the **scale-robustness preregistration** from 2.1: which scales, which sign must hold on all of them, what counts as a failure.
4. Draft the site-inventory schema — enumerated sites × IR roles × competitor candidates. It is the shared substrate of the linter, H2, and E1.
5. Get the Sol allocation request in. Ask for CPU/storage for E2 as well as GPU — the corpus indexing is the long-lead item and it is the piece nobody else in your literature has.

---

# Part 5 — Honest caveats on this analysis

- I did not verify the audit's 2026 citations; my knowledge predates its cutoff. If any of Persistent Priors / Conflict and Congruency / A Mechanistic Lens is weaker than the audit describes, H2's novelty is **better** than assessed here, and the case for the H2-first ordering strengthens.
- The compute numbers are order-of-magnitude from standard FLOP accounting, not benchmarked on Sol. Treat them as sizing for an allocation request, not a budget.
- My disagreement with the audit is about **sequencing and framing**, not facts. Its literature work is thorough and its statistical cautions (opportunity hurdle, bootstrap clustering at 2–3 grammars, DLA-is-not-causation, `R>1` overshoot) are all correct and worth obeying exactly as written.
- Section 2.1 is the claim I am least willing to soften and the one I would most want an independent statistician to check before you commit A100 time. If I am right, it changes the endpoint. If I am wrong, you lose an afternoon.
