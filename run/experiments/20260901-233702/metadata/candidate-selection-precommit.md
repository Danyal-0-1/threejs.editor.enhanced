# CANDIDATE_SELECTION.md

**grammar version:** `3dom-grammar/1.1.0` · **phase:** 2 (lexicon design) ·
**status:** provisional winner selected; primary objective **not yet measured**

---

## 0. Read this first — what is and is not measured

| Selection criterion | Status today | Blocker |
|---|---|---|
| **PRIMARY** ΔNLL per character | **UNMEASURED** | needs `torch` + the four Qwen2.5-Coder BASE checkpoints |
| **CONSTRAINT 1** fertility ratio ∈ [0.95, 1.05] | **UNMEASURED** | needs `transformers` + the five study tokenizers |
| **CONSTRAINT 2** zero collision violations | **MEASURED** | — |
| **CONSTRAINT 3** DFA branching parity | **MEASURED** | — |
| **CONSTRAINT 4** isomorphism + round-trip suites | **MEASURED** | — |

The winner below is therefore **provisional in the strict sense**: it is the
candidate that survives every criterion that can be evaluated today, chosen under
a rule written down before any of those evaluations were run. Two of the five
criteria — including the primary objective — are pending. Section 4 states what
switching would cost if they overturn it.

---

## 1. The selection rule — PRE-COMMITTED

**This section was written before any measurement in this repository was run,
and is followed mechanically.** It is a garden-of-forking-paths defence: with
three candidates, five criteria and a dozen defensible ways to weight them, a
rule chosen after seeing the numbers is a rule chosen to produce the numbers.
Writing it first is what makes "β won" a result rather than a preference.

```
PRIMARY OBJECTIVE   maximise ΔNLL per CHARACTER (prior distance)

CONSTRAINT 1        fertility ratio (alien ÷ 3DOM) within [0.95, 1.05]
                    on EVERY study tokenizer, with no exceptions and no
                    per-tokenizer weighting

CONSTRAINT 2        zero collision violations, checks (a)–(f)

CONSTRAINT 3        DFA branching parity within TOLERANCE 0.000 — mean
                    branching, max branching, and the position-indexed
                    profile, all exact. These are not noisy quantities:
                    the token streams are either identical or φ broke
                    something, so any nonzero deviation is a failure

CONSTRAINT 4        passes tests/test_isomorphism.py, tests/test_roundtrip.py
                    and tests/test_invariants.py in full

TIEBREAK            higher human readability, which preserves the option of
                    the small readability study as a CHI framing arm
```

Two clarifications, also pre-committed:

- **ΔNLL per character, not per token, is the primary objective.** Per-token NLL
  is contaminated by fertility: a lexicon that fragments into more tokens spreads
  the same surprise over more steps and scores as "more alien" for a reason that
  has nothing to do with pretraining. Per-character NLL holds the string fixed.
  If Δ/token is large while Δ/char is small, `measure/prior_strength.py` prints
  **"fragmentation, not distance"**, and the candidate is not reported as more
  alien — it is reported as more expensive.
- **"Zero training priors" is never claimed.** It is unprovable. The claim is
  reduced pretraining proximity, quantified in §4 of the paper. No artifact in
  this repository claims that any lexicon removes, eliminates or nullifies a
  pretraining prior; prior distance is only ever reported as a measurement.

---

## 2. The three candidates, and what each one measures

| | construct | mechanism | expected ΔNLL/char |
|---|---|---|---|
| **α** permuted | **INTERFERENCE** | Σ_3DOM deranged onto itself: a 5-cycle on the punctuation spellings, a 22-cycle on the word spellings, `$S` → `$$`. Every token is familiar; every prior points the wrong way. | small by construction — the surface distribution is 3DOM's |
| **β** pseudo | **ABSENCE, matched cost** | pronounceable ASCII non-words from a constrained phonotactic generator, character-length-matched and camelCase-shape-matched to the 3DOM word they replace | the design target |
| **γ** glyph | **SURFACE DISTANCE, unmatched cost** | non-ASCII symbols, 3 UTF-8 bytes each | largest per token; per character is the open question |

α and β are **different psychological constructs and are labelled as such**
throughout. α has strong priors that mislead; β has weak priors. "Interference"
and "absence" must not be pooled into one "unfamiliarity" factor in the analysis,
and the paper should report them as two levels of a *lexicon* factor with
different theoretical predictions, not as two points on one familiarity scale.

---

## 3. What the measurable criteria say today

### CONSTRAINT 2 — collisions (`measure/collisions.py`)

| lexicon | checks (a)–(f) | check (g), proposed |
|---|---|---|
| `identity` (3DOM) | **PASS** (0) | **PASS** (0) |
| `alpha` | **PASS** (0) | **PASS** (0) |
| `beta` | **PASS** (0) | **PASS** (0) |
| `gamma` | **PASS** (0) | **FAIL** (24) |

Check (g) is a **proposed addition**, reported separately and deliberately kept
out of the pre-committed rule, so the decision never turns on a criterion added
after the fact. It tests two things the specified checks do not:

- **g1, lexical-class parity.** A terminal spelled from the identifier charset in
  3DOM must be spelled from it in the alien language. 3DOM's lexer must do
  maximal munch and then a keyword-membership test to tell `mesh` (a type) from
  `wheel` (an identifier); a glyph type keyword makes that decision by character
  class alone, which is strictly easier.
- **g2, reachability parity.** The sharp one. In 3DOM, `mesh` + `mesh` lexes as
  the **single** token `IDENT("meshmesh")`, so the token sequence `TYPE TYPE` —
  although the grammar derives it — is **unreachable from any 3DOM string**. In
  γ, `⍇⍇` is two tokens and reaches it. Therefore
  **L(γ) ⊋ φ(L(3DOM))**: γ's language is a strict superset, and the two are not
  isomorphic, whatever the production counts say. The script prints one witness
  per level; both are in the output.

**This is a theorem about glyph lexicons, not a defect in this particular one.**
Identifier VALUES are copied verbatim into the shared IR, so `T_IDENT` is frozen
ASCII. Any non-ASCII word-class spelling is therefore disjoint from the
identifier charset, so no glyph lexicon can satisfy g1, and in general none can
satisfy g2. γ cannot be repaired into a primary experimental language; the cost
to "fix" it is to stop being a glyph lexicon.

### CONSTRAINT 3 — DFA branching parity (`measure/dfa_parity.py`)

All four lexicons: 52 DFA states, mean branching **3.980**, max branching **9** —
identical to Phase 1's INVARIANT rows. Token-alphabet parity, per-item token-stream
parity over the 62-item parallel corpus, and the position-indexed branching
profile all match at **tolerance 0.000**. **PASS for α, β, γ.**

### CONSTRAINT 4 — the verification suites

| suite | α | β | γ |
|---|---|---|---|
| `test_isomorphism.py` (4 tests) | PASS | PASS | PASS |
| `test_roundtrip.py` (8 tests) | PASS | PASS | PASS |
| `test_invariants.py` (14 tests, I1–I10) | PASS | PASS | PASS |
| corpus gates A1–A7 | PASS | PASS | PASS |

All three alien positive corpora achieve **100% production coverage** over the
same 57 W3C production branches, with **zero ambiguous parses**, and every item's
IR content hash equals its 3DOM twin's.

### CONSTRAINT 1 — fertility (**pending**), with the structural proxy today

| | chars/program | UTF-8 bytes/program | bytes/char | multibyte chars/program |
|---|---|---|---|---|
| 3DOM | 55.355 | 55.355 | 1.000 | 0.00 |
| α | 54.145 | 54.145 | 1.000 | 0.00 |
| β | **55.355** | **55.355** | **1.000** | 0.00 |
| γ | 39.645 | 54.226 | **1.368** | **7.29** |

β matches 3DOM's character length **exactly** — that is rule R1 of the
phonotactic generator working, not a coincidence. α is 2.2% shorter because the
derangement reshuffles verb lengths against a corpus whose verb distribution is
not uniform. γ is 28% **shorter in characters** and 37% **larger per character in
bytes**, which is the confound in one line: any per-token comparison involving γ
is measuring encoding, not familiarity.

**None of this is the fertility ratio.** Character length is a proxy; CONSTRAINT
1 is defined on tokens and stays unevaluated until
`python3 measure/fertility.py --md` runs with `transformers` installed.

---

## 4. Provisional winner: **β (pseudo-lexicon)**

Applying the rule mechanically to what is evaluable: γ is out on CONSTRAINT 2 as
soon as check (g) is adopted, and is expected to fail CONSTRAINT 1 on fertility
regardless. α and β both clear CONSTRAINTS 2, 3 and 4. Between them the PRIMARY
OBJECTIVE decides, and it is unmeasured — but α's construction *guarantees* a
small ΔNLL per character, because Σ_α **is** Σ_3DOM: an α program is drawn from
the same surface distribution as a 3DOM program. α is therefore the wrong tool
for maximising prior distance, and the right tool for a different question.

> **Provisional winner: β.** α is retained as a full second arm measuring
> INTERFERENCE, not demoted to a control. γ is retained as a control (§5).

### Switching costs nothing, and that is the whole point

The grammar package is `template + φ`. If the ΔNLL measurement overturns this:

```bash
python3 grammar/render_grammar.py alpha              # re-render the package
python3 src/generate_corpus.py alpha --winner=alpha  # re-generate all 3 corpora
```

Two commands. No grammar is edited, no corpus is rewritten by hand, no test is
adjusted — the suites are parameterised by φ and re-run unchanged. The
by-construction approach was chosen so that the winner is a **configuration
value, not a commitment**, and pre-committing the rule is only credible because
following it is cheap.

### Tiebreak note (readability)

Not invoked — the rule reached a decision before it. Recorded for the readability
arm: β is pronounceable by construction, so a human study can ask participants to
read `~car ^ ~wheel` aloud; γ cannot be read aloud at all, and α can be read but
is actively misleading, which is a third and interesting condition for that study.

---

## 5. γ as a control — the honest answer

You asked whether proposing γ as a fertility-stress control is a real
contribution or invented work. The honest answer has three parts.

**First: γ is not a clean fertility control, and calling it one would be wrong.**
Check (g) shows γ differs from β on **at least two** dimensions: token
fragmentation *and* lexical-class/reachability parity. A control that moves two
factors cannot attribute an effect to one of them. If you present γ as isolating
fertility, the first careful reviewer will notice that its type keywords are also
easier to lex, and the contribution evaporates. Worse, γ's language is a strict
superset of φ(L(3DOM)) — so it is not even the same language, and a fair "same
task, different syntax" framing does not hold for it.

**Second: it is still worth running, reframed.** The defensible claim is not
"this isolates the fertility confound" but:

> *The naive glyph substitution — the thing a practitioner reaches for when asked
> to make a DSL unfamiliar — inflates the apparent familiarity gap by a measured
> amount, and the inflation decomposes into a fertility component we measure and
> a lexical-class component we prove analytically.*

That is a smaller claim than the one you floated, and it is true, and it is still
a methodological contribution: it converts "we thought about the confound" into
"we measured it, and here is the size."

**Third, and this is the part that changes the cost calculation.** The
decomposition you actually need is **nearly free** and does not require γ in the
Phase 3 generation matrix at all. `measure/prior_strength.py` reports ΔNLL per
token *and* per character from the same forward passes: 62 programs × 4 models,
scoring only, no sampling. That is minutes of GPU time, and it produces the
"length effect vs prior effect" decomposition for **all three** candidates.

So, concretely:

| use of γ | cost | verdict |
|---|---|---|
| γ in `fertility.py` and `prior_strength.py` | ~62 forward passes per model | **Do it.** Essentially free, and it is what makes the confound *measured* rather than argued. |
| γ as a single-model arm in the Phase 3 matrix | 1 model × 1 syntax × both scaffolding conditions | **Do it if budget allows, last.** It answers the "why not just use weird symbols?" reviewer question with a number instead of a paragraph. Cut it first if the schedule slips. |
| γ as the primary experimental language | — | **No.** It fails g1/g2 and CONSTRAINT 1. |

**If you want a genuinely single-factor fertility manipulation**, γ is the wrong
instrument and there is a cheaper right one: a **β′** built by the same generator
with the same rules, except that R1 targets spellings drawn from rare ASCII
digraphs (`qx`, `zj`, `vk`, `xh`) that fragment badly while remaining
identifier-charset words. β′ would hold lexical class, reachability, delimiter
symmetry and readability-class constant and move **only** fertility — which is
the control γ cannot be. It is one edit to
`candidates/gen_beta_lexicon.py`'s syllable inventory and one re-render. That is a
suggestion, not part of this deliverable, and it is only worth building if the
fertility decomposition in `prior_strength.py` comes back ambiguous.

**Are you inventing work?** Not with the γ measurement arm — that is a real
confound, cheaply measured, and the decomposition strengthens the main result
whichever way it lands. You would be inventing work if you built γ out into a
full model × scaffolding matrix arm before the four Qwen forward passes have told
you whether the fertility gap is even large enough to matter.

---

## 6. Where the structural-prior condition would slot in — and stop

Out of scope for Phase 2, noted so the seam is visible. A prefix/postfix/
stack-based condition is a manipulation of **P and the operator skeleton**, not of
Σ, so it cannot be expressed as a φ-map: it would violate I3 (infix,
left-to-right) and change the max RHS length and the branching profile by design.

It would slot in as a **second template pair**, `grammar/templates/
grammar.prefix.{iso,w3c}.template.ebnf`, rendered by the same
`render_grammar.py` with the same φ-maps — so that lexicon and structure become
two crossed factors rather than one confounded one. `measure/dfa_parity.py`
would then report a *deliberate, quantified* branching difference instead of
asserting parity, and `METRICS_PARITY.md` would gain a column whose INVARIANT
rows are expected to differ.

Nothing further is designed here.
