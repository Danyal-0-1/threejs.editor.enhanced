# Phase 3 — surface-collision detection, prediction and repair

Phase 3 implements the research direction that survived the literature review,
in the ordering chosen in `project_status/hypothesis_strength_and_compute_analysis.md`:

> **Linter first, extinction primary.** Site inventory → risk prediction (H4) →
> minimal semantics-preserving repair (H5) is the headline track. The primary
> *scientific* estimand is the extinction threshold `k*`. The A×T
> difference-in-differences is a **secondary** contrast.

Nothing outside `phase3/` and `phase3_explained/` is modified. Everything
Phase 3 borrows is **copied** into `vendor/` with provenance recorded in
[`SOURCE_MANIFEST.md`](SOURCE_MANIFEST.md).

---

## Why this ordering

H4 and H5 need only a **main effect** of competitor prior strength at sites.
They do not need the interaction. The audit gates them behind it anyway, which
puts its two most preemption-resistant contributions behind its most fragile
one. Inverting that means a null interaction costs one experiment instead of
the programme.

The primary estimand is a **threshold**, not a difference-of-differences,
because an ordinal interaction measured on a log-probability margin is partly
an artifact of the scale: two factors that both push the same way generically
produce "super-additivity" under a compressive nonlinearity. `k*` is read off
the x-axis and is far more robust to monotone rescaling. The DiD is still
computed, on three scales, with a preregistered sign-agreement rule.

---

## Four measured findings that changed the design

These came out of running the code, not out of reading the literature. Each is
reproducible with one command.

### 1. `beta` and `gamma` cannot support the primary contrast at all

`python3 scripts/site_census.py`

| lexicon | none | lexical | benign | **semantic** | usable |
|---|---:|---:|---:|---:|---:|
| alpha | 0 | 315 | 0 | **72** | 18.6% |
| beta | 0 | 387 | 0 | **0** | 0.0% |
| gamma | 0 | 387 | 0 | **0** | 0.0% |

The review requires sites where the correct and familiar spellings are **both
grammar-valid** and lower to **different canonical IRs**. `beta` and `gamma`
map onto alphabets disjoint from CSS, so the familiar spelling is always a
**lex error** — a loud failure, never a wrong meaning. Their large ΔNLL
distances are irrelevant to this contrast.

### 2. The headline Experiment-02 reversion site is LOUD, not silent

`T_CLASS_SIGIL` is **LEXICAL** in alpha (70 sites). In alpha `.` is bound to
`T_WILDCARD`, which takes no identifier, so the familiar `.door` is a *parse
error*. The `.`-for-`#` reversion reported in Experiment 02 was producing
unparseable output, not silently-wrong IR. That is a different error class with
a different interpretation.

### 3. Silent collisions require permutation **within a shape class**

Two roles collide silently only if they accept the same syntactic shape.
alpha permutes *across* classes (a 5-cycle on `. # : > *`), which is why its
familiar forms mostly fail to parse. The usable alpha sites are exactly the
within-class ones — verbs, type keywords, pseudo keywords.

So Phase 3 generates its own lexicon: `python3 scripts/make_delta.py`

**`delta` is identity everywhere except four within-shape-class permutations:**

| class | permutation |
|---|---|
| sigils | `T_CLASS_SIGIL` `.`↔`#` `T_ID_SIGIL` (with `T_CHAIN_OP` following per I7) |
| verbs, signature `("enabled",)` | wireframe → castShadow → receiveShadow → wireframe |
| verbs, signature `("dx","dy","dz")` | move ↔ duplicate |
| type keywords | mesh → group → light → camera → mesh |
| pseudo keywords | selected ↔ lasso |

Result: **103 semantic sites (26.6%), zero benign**, all 13 intended terminals
verified purely SEMANTIC by the classifier at generation time.

`delta` is a better experimental material than alpha for a reason that matters:
because the multiset of spellings is unchanged from 3DOM, **mean character
length is 1.0078× identity** (alpha 0.978, gamma 0.713). The fertility
confound the review calls unmatchable is largely removed *by construction*, and
the only manipulation left is role reassignment.

> Character length is **not** token fertility. The real check needs a
> tokenizer; `measure/fertility.py` is the vendored tool and **has not been
> run** — see *Status* below.

### 4. 61% of semantic sites are not identifiable from their prefix

`S.prefix_collisions` finds **3 prefix groups containing 63 of the 103 semantic
sites**. 3DOM programs share openings (`(function(){ $S('#wheel')#` is very
common), so two sites present a model with byte-identical context while
expecting different spellings. **No prefix-conditioned predictor can be right
about both**, which caps achievable AUROC for H4.

`S.dedupe_by_prefix` leaves **40** usable sites. That is the real N for a
prefix-conditioned analysis, and it is too small — **Phase 3 needs more diverse
AST templates before H4 is run for real.** This is the single most important
open item.

---

## Layout

```
phase3/
├── README.md                  this file
├── SOURCE_MANIFEST.md         provenance + SHA-256 for all 22 vendored files
├── PATCHES/                   modifications to vendored code, with rationale
├── requirements.txt
├── scripts/
│   ├── vendor_sync.py         copy upstream + record provenance (--check for drift)
│   ├── site_census.py         finding 1: the collision inventory
│   └── make_delta.py          finding 3: generate + verify the delta lexicon
├── src/phase3/
│   ├── _vendor.py             the ONE sys.path wiring + self-containment guard
│   ├── sites.py               site enumeration, collision classifier  ← the core
│   ├── models.py              LM protocol, deterministic FakeLM, HFModel
│   ├── scoring.py             M_seq margins, extinction curves, the DiD
│   ├── outcomes.py            error taxonomy, site reach, the opportunity hurdle
│   └── linter.py              H4 risk scoring + ranking, H5 repair + IR proof
├── tests/
│   ├── run_tests.py           dependency-free runner (no pytest in this repo)
│   ├── test_scorer_repair.py  adversarial tests for defect P3-001
│   ├── test_sites.py          classification, offsets, materials validation
│   └── test_pipeline.py       scoring, outcomes, linter, end-to-end
└── vendor/                    copied Phase 1 / Phase 2 code — DO NOT RENAME
```

`vendor/` directory **names are load-bearing**: `phi.phase1_dir()` and
`phi.alien_dir()` resolve by walking up from `phi.py`, so mirroring the upstream
names makes the tree self-resolving with no `$PHASE1_DIR` and no `sys.path`
surgery. `_vendor.assert_self_contained()` fails loudly if a vendored module
ever resolves outside `phase3/vendor/`.

---

## The scorer repair (P3-001)

`score_op_selection_report` guarded `len(ops) < len(wanted)` and then compared
only `ops[0:len(wanted)]`, so **extra trailing operations were never
examined**: a program that did the right thing and then three more things
scored PASS. Repaired to exact-length matching. Full rationale and blast radius
in [`PATCHES/tasks.op_selection.md`](PATCHES/tasks.op_selection.md).

Direction of bias is one-way: previously reported accuracy can only **fall**.
Experiment 02's table must be recomputed from retained raw outputs before use.

`tests/test_scorer_repair.py` fails if the repair is absent, so re-running
`vendor_sync.py` (which overwrites the vendored copy) cannot silently restore
the defect.

---

## Running it

```bash
cd phase3
python3 scripts/vendor_sync.py          # copy + manifest   (re-apply PATCHES after!)
python3 scripts/make_delta.py           # generate + verify the delta lexicon
python3 scripts/site_census.py          # the collision inventory
python3 tests/run_tests.py -v           # 54 tests, no GPU, no weights
```

Only `lark` is required for everything above. `torch`/`transformers` are needed
only for real models (`models.HFModel`).

---

## Status of each component

Honest labels, per the brief. Nothing here is reported as measured unless it was.

| Component | Status |
|---|---|
| Vendored tree + provenance + drift check | **tested** — 22 files, self-containment asserted |
| Scorer repair P3-001 | **tested** — 13 adversarial tests |
| Site enumeration + collision classifier | **tested** — 12 tests incl. the `'#333333'` hazard |
| `delta` lexicon | **tested** — validates V1–V8; all 13 intended terminals proven SEMANTIC |
| Collision census (findings 1–4) | **measured** — on the 62-program Phase 1 positive corpus |
| `M_seq` margins, extinction curve, DiD | **tested with a fake model** — arithmetic and sign conventions only |
| Error taxonomy, reach, hurdle | **tested** |
| H4 risk scoring + ranking metrics | **tested with a fake model** |
| H5 repair + IR-preservation proof | **tested** — proof runs over all 62 programs |
| `models.HFModel` | **ready to run, NOT exercised** — no weights are downloaded in CI; smoke-test on the cluster first |
| Token fertility of `delta` | **not run** — needs a real tokenizer |
| Any result from a real model | **not run** |
| Mixed-effects / power simulation | **not implemented** — needs `statsmodels`; deliberately deferred until materials are fixed |
| More diverse AST templates | **not done — the top blocker** (finding 4) |

---

## What is deliberately not here yet

- `phase3_explained/` — the teaching documents. Delivery order was code+tests
  first so the docs describe code that actually runs.
- The A-level (local context) construction. Finding 4 says the corpus is too
  templated to support prefix-conditioned contrasts at scale; template
  diversity has to come first or the A manipulation will be confounded with
  prefix collision.
- A second, independently designed **grammar family**. `alpha/beta/gamma/delta`
  are four *lexicons* over **one** grammar — invariants I1–I4 freeze N and the
  shape of P, and `render_grammar.py` asserts φ=identity reproduces Phase 1
  byte-for-byte. They are, by construction, exactly what the review calls
  "cosmetic renamings of one grammar". A real second family is new design work.
