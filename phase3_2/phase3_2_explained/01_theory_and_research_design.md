# 01 — Theory and research design (Phase 3.2)

> Companion to `phase3/phase3_explained/01_theory_and_research_design.md`,
> which defines the 20 core concepts (surface familiarity, reversion, token
> fertility, the collision taxonomy, the hurdle, canonical IR, falsification,
> claims to avoid). **Those definitions are unchanged and are not repeated.**
> This document covers only what Phase 3.2 adds or corrects.

---

## 1. What changed in the research position

Phase 3 ended with a single blocker: **40 prefix-distinct semantic sites in
one grammar family.** Not a scientific problem — a materials problem. Phase 3.2
is the materials rebuild, plus the cheap real-model check that materials
rebuild made worth running.

| | Phase 3 | Phase 3.2 |
|---|---|---|
| grammar families | 1 | **2** (`dom`, `blk`) |
| lexicons | 1 hand-built `delta` | **9** (3 densities × 3 seeds) |
| templates | 62 Phase 1 programs | **80** purpose-built |
| prefix-distinct semantic sites | 40 | **3,326** |
| counterbalancing | none | seeded rotation |
| held-out mappings | impossible | available |
| real-model Arm A | never run | **6 checkpoints measured** |

---

## 2. New concept: the grammar family, and why four lexicons were never two languages

**Technical.** A *grammar family* is a concrete syntax with its own
non-terminals and production shapes. A *lexicon* (φ-map) only renames the
terminal spellings of an existing family.

**Simple.** New words versus a new sentence structure.

**Example.** The same abstract program in both families:

```
dom   (function(){ $S('.wheel').recolor('#111111'); })();
blk   $S '.wheel' { recolor '#111111'; }
```

**Inputs** an `IRProgram`, a φ-map. **Outputs** concrete text that lowers back
to a byte-identical canonical IR.

**Assumptions it depends on.** That the terminal table stays frozen, so the
*same* φ-maps apply to both families. If `blk` introduced new terminals, a
cross-family comparison would vary the mapping and the grammar together and
measure neither.

**What can silently go wrong.** Building a "second family" that is really a
renaming. Phase 3's `alpha/beta/gamma/delta` are exactly that: invariants
I1–I4 freeze N and the shape of P, and `render_grammar.py` asserts φ=identity
reproduces Phase 1 byte-for-byte. Four lexicons, one grammar.

**How the failure shows up in results.** "Cross-family generalisation" that is
really cross-lexicon generalisation — an inflated H4 claim a reviewer dismantles
in one sentence.

**Which test catches it.** `test_blk_is_structurally_different_from_dom`
asserts `blk` contains no parentheses, no `T_FUNCTION` and no chain operator;
`test_families_disagree_on_token_count_but_not_on_ir` asserts the text differs
while the IR hash does not.

**Why it matters scientifically.** H4 requires prediction on an unseen grammar
family. Without a real second family the headline claim cannot be tested at all.

### What `blk` holds fixed, on purpose

- the **frozen terminal table**, so the same φ-maps apply unchanged;
- the **inner selector sub-language**, parsed by the *vendored* parser and
  transformer in both families. The class/id sigil collision lives in the
  inner language, so it transfers across families with the competitor identity
  held constant — which is what makes cross-family transfer a clean test;
- the **canonical IR**.

---

## 3. New concept: collision density, and why maximising it is wrong

**Technical.** The fraction of substitutable roles a lexicon remaps, hence
roughly the fraction of sites that are SEMANTIC.

**Simple.** How much of the language is a false friend.

**Example.** `d25s1` permutes 9 of 29 roles; `d75s1a` permutes 22.

**Assumptions.** That the remaining roles stay at identity.

**What can silently go wrong.** Pushing density to the 79% ceiling (306 of 387
sites; the other 81 are `T_CHAIN_OP`, locked LEXICAL by I7).

**How the failure shows up.** **H5 becomes untestable.** The repair claim is
not "renaming helps" but "renaming *only* the predicted-risky sites helps more
per changed symbol, and leaves ordinary sites alone." With every role remapped
there are no ordinary sites left, `identity_baseline` becomes degenerate, and
the targeted-versus-global comparison has nothing to compare.

**Which test catches it.** `test_family_keeps_unpermuted_control_roles`.

**Why it matters.** Low-risk sites are not spare capacity; they are the control
condition.

### The family closes three gaps at once

1. **density** → more semantic sites;
2. **counterbalancing** → the rotation seed changes which spelling lands on
   which role, so no token is "always correct." Phase 3 had none;
3. **held-out mappings** → train on δ25/δ50, test on δ75, or hold out seeds.

### The strict/arity trade, stated honestly

Only two verb groups are strictly signature-matched — `{move, duplicate}` and
`{wireframe, castShadow, receiveShadow}` — so strict mode can permute 5 of 15
verbs. Reaching higher densities needs **arity** mode, which permutes within
equal-argument-count groups.

The cost: swapping `recolor` with `setOpacity` keeps the program parseable and
changes the IR (so the collision is genuine), but the argument **key** changes
too — `{"color": "#111111"}` becomes `{"opacity": "#111111"}`. Well-formed,
different, and semantically odd. Use strict for the primary arms; report which
mode produced each member. The `phi_id` carries an `a` suffix for arity mode so
no analysis can mix them unnoticed.

---

## 4. New concept: site strata — the answer to "does 3D knowledge matter?"

A real question about this DSL: it is built for 3D editing, so does the model's
knowledge of 3D worlds confound the surface effect?

**Technical.** Sites partition into three strata by what competence the
decision requires:

| stratum | decision | competence needed |
|---|---|---|
| **sigil** | `.` vs `#` | **pure CSS lexical prior** — no 3D knowledge |
| **verb** | `scale` vs `move` | surface prior **+ understanding the request** |
| **keyword** | `mesh` vs `group` | surface prior + object-kind knowledge |

**Simple.** You don't need to know what a mesh is to type the right sigil. You
do need to understand "make it bigger" to pick `scale`.

**Where domain knowledge enters the hurdle.** It drives `P(O)` — whether free
generation reaches the site at all — far more than `P(Y|O)`, the choice once
there, because Arm A hands the model the prefix. The hurdle already separates
these, so the question is testable rather than rhetorical.

**The test is cheap** — `sites2.stratum` tags every site — but it is only
valid on a balanced sample scored against a real rule prompt. The first
attempt had neither.

**Measured answer — and it is now NEGATIVE.** The first attempt at this test
was invalid twice over: it scored only `dom` sites (defect P32-003) and its
"rule" prompt contained no token table (defect P32-002). It produced a clean
story — sigil ≥ verb at every checkpoint — and that story **did not survive**
the balanced re-run with a real rule table.

Reversion rate with the token table present, `d50s1`, 272 sites per family:

| model | family | **sigil** | **verb** | keyword |
|---|---|---:|---:|---:|
| 0.5B base | dom | 0.430 | **0.286** | 0.477 |
| 0.5B base | blk | 0.444 | **0.482** | 0.462 |
| 0.5B instruct | dom | 0.391 | **0.500** | 0.523 |
| 0.5B instruct | blk | 0.391 | **0.429** | 0.492 |

**The ordering flips between conditions.** Verb sites are the *lowest* cell
for 0.5B base/dom (0.286) and the *highest* for 0.5B instruct/dom (0.500).
There is no stable stratum ordering at n = 151/56/65 per cell.

**Conclusion: the 3D question is reopened, not answered.** What can be said:

- the effect is **not** confined to verb sites, so it is not purely a
  domain-competence artifact;
- it is **not** cleanly stronger at sigil sites either, so the earlier claim
  that domain knowledge is irrelevant is unsupported.

**What the test still needs.** Sigil candidates are single characters; verb
candidates are whole words. The strata therefore differ in token length as
well as in domain content, and a length-matched sub-analysis must come before
any claim either way. See `07_next_steps.md`.

**The lesson worth keeping.** A clean, interpretable result from an
uncontrolled run is more dangerous than a messy one, because it invites
belief. Both defects produced *more* order, not less.

---

## 5. New concept: the first-divergent-token margin (P32-001)

**Technical.** Score both candidates from the first token index at which their
tokenisations differ, rather than from the end of the separately-tokenised
prefix.

**Simple.** Find where the two versions first disagree, and compare from there.

**Example.** `('` + `#` tokenises as the single token `('#`. The old scorer saw
"no new tokens" and returned 0.0 for both candidates.

**Assumptions.** Both sides conditioned on the same `k`-token context, so the
shared prefix cancels exactly.

**What can silently go wrong.** The old code returned `0.0`, a plausible
number, for **44.2%** of sites.

**How the failure shows up.** `M_seq = 0` is not negative, so the site counts
as "no reversion": a **false null**, concentrated at sigil sites. Measured:
sigil reversion **0.106 → 0.515** after the fix.

**Which test catches it.** `test_divergent_margin_finds_the_common_prefix` and
`test_divergent_margin_scores_both_sides_from_the_same_point`; the real-model
run prints the merge count and the post-fix exact-zero count every time.

**Why it matters.** This single defect would have produced a confident null at
the most important stratum, on a cluster, at cost.

---

## 6. Theory → variable → code → metric (new rows only)

| Theory | Variable | Code | Metric |
|---|---|---|---|
| grammar family is a real factor | `dom` vs `blk` | `backends.BACKENDS` | family tag on every `site_id` |
| families share meaning | same IR both ways | `BlkBackend.parse/render` | IR hash equality, 62/62 × 5 lexicons |
| collision density | permuted-role fraction | `deltafam.build(density, seed)` | `Member.density_actual` |
| counterbalancing | rotation seed | `deltafam.build(…, seed)` | 9 distinct mappings |
| held-out mappings | member split | δ25/δ50 → δ75 | train/test separation |
| domain knowledge is a confound | site stratum | `sites2.stratum` | reversion by stratum |
| tokenisation merges candidates | divergence index | `margins.score_pair` | `k_common`, `merged` |
| real fertility | tokens/char | `run_arm_a.fertility` | 1.077 dom / 1.008 blk |

---

## 7. Falsification criteria (updated)

**H4 is not supported** if site risk fails to beat `identity_baseline`, **or**
if it collapses when transferred `dom → blk`. The second is new and is the
sharper test: a predictor that works within a family but not across one has
learned the family, not the collision.

**The materials are inadequate** if, after all this, the usable site count
falls back below ~300 prefix-distinct, or if the `blk` fertility advantage
(1.008) disappears under another tokenizer.

**The surface framing is wrong** if the sigil stratum — which needs no 3D
knowledge — shows *no* effect while verb sites do. Measured so far: the
opposite.

---

## 8. Learning resources (additions only)

> **Not fetched or verified in this session.** I had no browsing in this run
> and will not claim a check I did not perform. Canonical, stable URLs.
> Listed 2026-10-02.

| Resource | Teaches | Why here | Read | Level | Time |
|---|---|---|---|---|---|
| [lark: grammar reference](https://lark-parser.readthedocs.io/en/latest/grammar.html) | EBNF-in-lark, `*` vs `+` | `blk`'s grammar; `block*` vs `block+` is the D5 bug | whole page | intermediate | 1.5 h |
| [HF tokenizers: the pipeline](https://huggingface.co/docs/tokenizers/pipeline) | BPE merges, offsets | **why P32-001 exists** | "Normalization", "Model" | intermediate | 1.5 h |
| [Sennrich et al. 2016, BPE (arXiv:1508.07909)](https://arxiv.org/abs/1508.07909) | why subwords merge greedily | the mechanism behind the 44.2% | §3 | intermediate | 1 h |
| [docs.python.org — random.Random](https://docs.python.org/3/library/random.html) | seeded, reproducible shuffling | `deltafam` counterbalancing | `Random`, `shuffle` | beginner | 20 min |
