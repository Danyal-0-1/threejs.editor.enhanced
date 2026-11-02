# The research in depth

*Written 2026-10-28. Start here.*

These files explain the whole research in one place, at the depth of
[`experiment_math.md`](experiment_math.md): what the research asks, why every part of it is
built the way it is, the mathematics behind every number, and every step of the code, in both
of the experiment's languages (`dom` and `blk`). Read them to get the fundamental picture first;
the earlier explanation sets then become reference material.

---

## The five files

| file | what it teaches | read it |
|---|---|---|
| **README.md** (this file) | the research on one page, the pipeline in one picture, the running example | first |
| [`experiment_theory.md`](experiment_theory.md) | the question; the language 3DOM and its two grammars; lexicons; decision sites; the four measurements (Arm A, the ladder, Arm B, H5) and the hypotheses; the design that makes a result confirmatory; what was found | second |
| [`experiment_math.md`](experiment_math.md) | every equation, derived and worked with real numbers. Improved from Phase 3.3's [`experiment_math.md`](../phase3_3/sol_experiment_explained/experiment_math.md), which stays unchanged where it is | third, slowly |
| [`experiment_code.md`](experiment_code.md) | what the code computes, step by step, in both languages: the language library, sites, prompts, the scorer, Arm A, the ladder, Arm B, H4, H5 and H2 | fourth |
| [`experiment_pipeline.md`](experiment_pipeline.md) | how the code runs: configurations, the split and the freeze, crash-safe storage, Slurm jobs on Sol, the API path for served models, merging, exporting, reports, the analyses after a run, and the tests | fifth |

Each file is self-contained and can be read alone. Each ends with practice questions.

---

## The research on one page

**The question.** Code models carry strong habits about what familiar symbols mean: `.` is a CSS
class, `#` an id, `mesh` a 3D mesh. A domain-specific language (DSL) is often specified to the
model in its prompt. When that specification reassigns a familiar spelling, does the model follow
the specification, or does the old habit win? When the habit wins, the program still runs but
does the wrong thing. We call that a **reversion**.

**The instrument.**

- **3DOM**, a small language for editing Three.js 3D scenes with CSS-like selectors and
  jQuery-like operation chains, formalised in Phase 1.
- **Lexicons** (φ-maps) that **respell** 3DOM by permuting familiar spellings among roles of the
  same shape: under the lexicon `d50s3`, the keyword for meshes is written `camera`, and `mesh`
  now means groups.
- **Two grammar families** for the same programs: `dom` (the jQuery-like syntax) and `blk` (a
  block syntax built for this study).
- **Decision sites**: the exact places in a program where a respelled terminal must be written,
  kept only when the familiar spelling there would still parse but mean something else
  (a **semantic collision**).

**The four measurements.**

| measurement | question | how |
|---|---|---|
| **Arm A** | which spelling does the model prefer at the site? | the margin M = log P(correct) − log P(familiar), with the token table in the prompt (`rule`), without it (`norule`), and with a length-matched control |
| **the ladder** (primary endpoint `k*`) | how many worked examples until it switches? | M again with 0, 1, 2, 4, 8, 16, 32 leak-free example programs; `k*` = first crossing above zero; Kaplan–Meier over sites |
| **Arm B** | what does it actually write? | free generation from a natural-language request; reach the site, then reversion given reach |
| **H5** | can the risky spellings be repaired? | respell only the predicted-risky roles; compare with random and global respelling |

**The hypotheses** (preregistered 2026-10-02): **H4**, a base checkpoint's own margin at a site
predicts which sites its instruction-tuned twin gets wrong (confirmatory, primary claim); the
**`k*` endpoint**; **H5**, targeted repair beats random repair per changed symbol (confirmatory);
**H2**, a prior × local-context interaction (exploratory; not testable).

**The design.** Everything was built and calibrated on development cells, **frozen**, then tested
once on held-out mappings with 21 models from 0.5B to 72B (Phase 3.3, on ASU's Sol cluster). Phase 4
then scored nine newer, larger models served by the ASU RC LLM API on the same cells
(exploratory).

**What was found** (Phase 3.3 held-out, unless marked):

- With the token table in the prompt, every model still reverts at **40–56%** of sites (the nine
  served models of Phase 4: 40–51%). Size does not change it.
- The table helps: averaged over the five lexicons, it moves the margin toward the correct spelling
  by +0.16 to +0.62 nats, depending on the model and grammar, and no interval lies below zero. That
  is not enough to flip most sites: reversion falls by about 5 points on average (12 at most; for
  Qwen2.5-Coder-7B-Instruct in `dom` it rises by 1.5).
- Models first switch after a median of **1.4–4.6** examples in `dom` and **3.3–11.6** in `blk`
  (as exported; see the second fault below); 6–29% of initially wrong sites never switch within
  32; nearly every curve wobbles.
- **H4 is supported** in all 20 tests (10 pairs × 2 grammars): AUROC 0.76–0.96, well above every
  baseline.
- **H5 was not supported** as reported, but see the first fault below: its targeted arm was not
  scored as designed.
- In free generation, models reach a site 13.5% of the time and then write the familiar spelling
  19.8% of the time; verbs revert most.

---

## The pipeline in one picture

```
 1 MATERIALS               2 SITES                       3 PROMPTS                 4 SCORING (one model at a time)
 ───────────               ───────                       ─────────                 ───────────────────────────────
 3DOM grammar              render each of the 80         rule: the token table     Arm A: M at every site,
 43 terminals       ──►    templates in dom and blk ──►  norule: roles only   ──►    three conditions
 80 templates (IR)         under each lexicon; keep      length-matched control    ladder: M with 0…32 examples
 lexicons φ (JSON)         SEMANTIC sites; one site      + worked examples         Arm B: one program per request
                           per prefix in each cell       + NL requests             H5: M under repaired lexicons
                           → 1,515 sites per grammar

 5 STORAGE                     6 ANALYSIS                                        7 REPORTING
 ─────────                     ──────────                                        ───────────
 one atomic shard per   ──►    reversion and rule effect (template bootstrap) ──► 19 CSVs, 24 plot files,
 cell + done-marker;           k*, Kaplan–Meier medians                           10 reports; paper figures
 merge, validate               H4: AUROC vs baselines, C1/C2 with Holm            and tables (scripts after
                               H5: reversions saved per changed role              the run)
                               Arm B: reach, reversion given reach

 GOVERNANCE around all of it: registered split → development run → DEV_FREEZE.json → unlock → held-out run
```

---

## The running example

Every file follows one abstract program, template **`t011`**, through the whole research:
*"Set the metalness of meshes directly inside objects of class 'frame' directly inside the object
with id 'panel' to 0.8."*

| | `dom` | `blk` |
|---|---|---|
| 3DOM (identity) | `(function(){ $S('#panel>.frame>mesh').metalness(0.8); })();` | `$S '#panel>.frame>mesh' { metalness 0.8; }` |
| lexicon `d50s3` | `(function(){ $S('.panel>#frame>camera')#metalness(0.8); })();` | `$S '.panel>#frame>camera' { metalness 0.8; }` |

The site followed most closely is the type keyword: **correct `camera`, familiar `mesh`**. Under
`d50s3`, `mesh` means *group* objects, so writing it still parses but selects groups instead of
meshes.

What happened at this site in the held-out run, for the Qwen2.5-Coder-0.5B pair:

| | `dom` | `blk` |
|---|---:|---:|
| base model, margin with the table | −4.512 | −3.755 |
| instruct model, margin with the table | −0.638 (reverts) | −0.215 (reverts) |
| H4: base risk → frozen calibrated probability that the instruct model reverts | 4.512 → 0.977 | 3.755 → 0.956 |
| ladder: examples until the base model switches (`k*`) | 1.57 | 11.95 |

In free generation (Arm B), Qwen2.5-Coder-1.5B-Instruct wrote `$S '.panel>#frame>mesh' { metalness 0.8; }`
in `blk`: the class sigil right, the keyword reverted. DeepSeek-Coder-33B-Instruct wrote the target
exactly. In `dom`, no model reproduced the program up to this site.

The development example of Phase 3.3's guides, site `dom:d50s1:t011:T_TYPE_MESH:0` (correct
`light`, familiar `mesh`), is the same template under another lexicon, and
[`experiment_math.md`](experiment_math.md) keeps it beside the held-out one.

---

## How these files relate to the earlier explanations

| earlier set | what it is | after reading these files |
|---|---|---|
| [`phase3_3/sol_experiment_explained/`](../phase3_3/sol_experiment_explained/00_complete_guide.md) | the Sol design, concept by concept (10 points each); `EXPERIMENT_IN_ONE_FILE.md`; the original `experiment_math.md` | reference for any one concept's tests and failure modes |
| [`phase3_3/heldout_results_explained/`](../phase3_3/heldout_results_explained/00_complete_results.md) | every held-out result, in tables | the source of the result tables |
| [`phase4/fixes_before_phase4/`](../phase4/fixes_before_phase4/README.md) | the post-hoc corrections of 2026-10-21 (deviation D13) | what changed after the results |
| [`phase4/api_models_results_explained/`](../phase4/api_models_results_explained/00_complete_results.md) | the nine served models (Phase 4, exploratory) | the served-model numbers |
| [`phase1`](../phase1/phase1.md), [`phase2`](../phase2/phase2.md), [`phase3`](../phase3/phase3_explained/00_complete_phase3_guide.md), [`phase3_2`](../phase3_2/phase3_2_explained/00_complete_phase3_2_guide.md) | how each layer was built | the history of each design choice |

These files do not change any number. Where they state a result, the source is the run's own
files; where they compute something new, the computation is shown.

---

## Two faults in the frozen analysis code

Both are in the frozen Phase 3.3 analysis code, which is copied unchanged into Phase 4. The first
was found while writing these files (2026-10-28); the second was found with the Phase 4 run
(2026-10-23) and is explained here in full. Neither is fixed: fixing either is a decision for the
investigator, and a correction to registered Phase 3.3 numbers needs a dated deviation first.

1. **H5's targeted arm was scored with the wrong repaired lexicon in 84 of 100 cells.** The repaired
   lexicon's name (`<lexicon>__h5_targeted_0`) is the same for every model and grammar, so a cache
   kept only the last one prepared, and every model was scored with the targeted repair chosen for
   Llama-3.2-1B-Instruct in `dom`. In the 16 cells where that repair happened to be the model's own,
   targeted beat random in 14 (mean +2.83 reversions saved per changed role); in the other 84, in 29
   (mean −1.02). The registered H5 test was therefore not run as designed. Details:
   [`experiment_code.md` §11.6](experiment_code.md#116-a-defect-found-on-2026-10-28-the-targeted-arm-scored-the-wrong-lexicon).
2. **A rounding fault in the Kaplan–Meier median.** When the survival curve equals exactly 1/2 at a
   switch, floating-point arithmetic can push the median to the next switch: 14 of Phase 3.3's 42
   held-out medians and 6 of Phase 4's 18 moved. The running example's own model is one of them:
   Qwen2.5-Coder-0.5B in `dom`, exactly 1.83 examples, exported as 2.58. Details:
   [`experiment_math.md` §10.10](experiment_math.md#1010-a-floating-point-trap-in-the-median).
