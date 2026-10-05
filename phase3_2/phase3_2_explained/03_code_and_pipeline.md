# 03 — Code and pipeline (Phase 3.2)

> Companion to `phase3/phase3_explained/03_code_and_pipeline.md`. The Phase 3
> stages (collision classification, Arm A/B, hurdle, linter) are unchanged.
> This document covers the new stages and the one corrected stage, with real
> dumps produced by running the code.

---

## 1. New data structures

### `backends.Backend` (Protocol) — one concrete syntax

```python
family: str
lex(src, phi)        -> list[(token_type, value, char_offset)]
num_parses(src, phi) -> int
parse(src, phi)      -> IRProgram
render(ir, phi)      -> str
```

Two implementations: `DOM` (Phase 1/2 syntax) and `BLK` (new). Everything
downstream is written against the protocol, so the identical classifier runs
over both families.

### `deltafam.Member` — one lexicon of the family

```python
{'phi_id': 'd50s1', 'density_target': 0.5, 'seed': 1, 'mode': 'strict',
 'n_substitutable': 29,
 'permuted': ('T_CLASS_SIGIL', 'T_ID_SIGIL', 'T_PSEUDO_LASSO',
              'T_PSEUDO_SELECTED', 'T_TYPE_CAMERA', 'T_TYPE_GROUP',
              'T_TYPE_LIGHT', 'T_TYPE_MESH', 'T_VERB_CASTSHADOW',
              'T_VERB_DUPLICATE', 'T_VERB_MOVE', 'T_VERB_RECEIVESHADOW',
              'T_VERB_WIREFRAME')}
```

13 of 29 roles permuted → `density_actual = 0.448`.

### `templates.Template` — an abstract program, not text

```python
Template(template_id='t000', shape='class', n_statements=1, ir=IRProgram(...))
```

Built as IR and rendered per (family, lexicon). Valid by construction, and the
*same* template is expressible in both families — which is what lets a
cross-family comparison hold the abstract program fixed.

### `margins.MarginV2` — the corrected measurement

```python
MarginV2(site_id=…, model=…, shots=0,
         logp_correct=…, logp_competitor=…, m_seq=…,
         k_common=11,            # first divergent TOKEN index
         n_tok_correct=1, n_tok_competitor=1,
         merged=True)            # candidate merged into the prefix token
```

`merged` and `k_common` are the new fields. They exist because P32-001 was
invisible without them.

---

## 2. Pipeline

```
terminals.json ─► deltafam.build(density, seed) ─► phi_dNNsS.json
                        │  permute WITHIN shape classes; I7 keeps CHAIN=CLASS
                        ▼  validate_phi V1–V8
                   9 counterbalanced lexicons

               ─► templates.build_templates() ─► 80 IRPrograms
                        │  shapes × statement counts, deterministic
                        ▼
        ┌───────────────┴───────────────┐
   DOM.render(ir, phi)            BLK.render(ir, phi)
   (function(){ $S('#wheel')…      $S '#wheel' { recolor …; }
        └───────────────┬───────────────┘
                        ▼ sites2.classify(text, phi, backend)
                 scan_sites → (type, value, OFFSET)
                 splice q at the offset → re-parse → re-hash
                        │
                 NONE / LEXICAL / BENIGN / SEMANTIC
                        ▼  dedupe_by_prefix
                 3,326 prefix-distinct SEMANTIC sites
                        │
          ┌─────────────┴──────────────┐
    margins.divergent_margin      sites2.stratum
      (P32-001-correct M_seq)      sigil / verb / keyword
          └─────────────┬──────────────┘
                        ▼
              run_arm_a.py  →  reversion by stratum, per checkpoint
```

---

## 3. Stage detail

### `backends.scan_sites` — INPUT → TRANSFORMATION → OUTPUT → VALIDATION

- **INPUT** concrete text + φ.
- **TRANSFORMATION** scan left to right. A quoted string is a **selector**
  (inner stream) the first time it appears in a statement and an **argument**
  every time after; `;` resets the statement. Outer symbols are matched
  longest-first from `Lexicon.of(φ)`.
- **OUTPUT** `(token_type, value, char_offset)` per substitutable terminal.
- **VALIDATION** `test_colour_literal_is_not_a_site_in_either_family`,
  `test_offsets_point_at_the_correct_spelling`.

One scanner serves both families because they share the quoting convention and
the two-level contract. The alternative — two lexers — is two things to keep
in sync, and a divergence would look like a cross-family effect.

### `BlkBackend.parse` — the second family

- **INPUT** blk text + φ.
- **TRANSFORMATION** lark Earley parse of the *outer* block grammar; the
  **inner selector** goes to the **vendored** selector parser and transformer.
- **OUTPUT** the same `IRProgram` the `dom` family produces.
- **VALIDATION** `test_blk_ir_roundtrip_whole_corpus_all_lexicons` — 62
  programs × 5 lexicons, IR hash equality, **310/310**.

Reusing the vendored inner parser is deliberate: the shared sub-language
cannot drift between families, so a bug there shows up in both rather than as
a spurious cross-family difference.

`program : block*`, not `block+`. The empty program is derivable because Phase
1 ships `(function(){})();` — zero operations, canonical IR `{"ops":[]}`,
which D5 calls a parse success and a task failure. With `block+` the blk
rendering of an empty IR would not parse and the families would disagree on
exactly the most plausible null output. Caught by
`test_empty_program_is_derivable_in_blk`.

### `deltafam.build` — density × seed

- **INPUT** density target, seed, mode.
- **TRANSFORMATION** shuffle the shape-class groups (seeded), take groups
  until the role budget is met, cycle spellings within each group, force
  `T_CHAIN_OP = T_CLASS_SIGIL` (I7), leave the rest at identity.
- **OUTPUT** a φ blob + `Member`.
- **VALIDATION** `validate_phi` V1–V8 on load; `test_i7_overload_group_is_respected`,
  `test_seeds_counterbalance_the_assignment`, `test_build_is_reproducible_for_a_fixed_seed`.

### `margins.divergent_margin` — the corrected scorer

- **INPUT** a `TokenScorer`, a `Site`, a rule, a shot count.
- **TRANSFORMATION** build the prefix **once**; tokenise `prefix+c` and
  `prefix+q` in full; find the common token prefix `k`; sum log-probs from `k`
  on both sides.
- **OUTPUT** `MarginV2`.
- **VALIDATION** `test_divergent_margin_finds_the_common_prefix`,
  `test_divergent_margin_scores_both_sides_from_the_same_point`; at runtime,
  the merged count and the post-fix exact-zero count are printed every run.

---

## 4. One site, both families — the cross-family demonstration

Real output. Same template, same lexicon, same terminal.

```
--- dom ---
 text        (function(){ $S('#wheel')#recolor('#111111'); })();
  site_id              'dom:d50s1:t000:T_CLASS_SIGIL:0'
  char_offset          17
  prefix               "(function(){ $S('"
  correct / competitor '#' / '.'
  collision            semantic      binds_to  T_ID_SIGIL
  stratum              sigil
  variant              (function(){ $S('.wheel')#recolor('#111111'); })();
  ir correct/competitor  5be0d4314219 / d74513ab1dcc

--- blk ---
 text        $S '#wheel' { recolor '#111111'; }
  site_id              'blk:d50s1:t000:T_CLASS_SIGIL:0'
  char_offset          4
  prefix               "$S '"
  correct / competitor '#' / '.'
  collision            semantic      binds_to  T_ID_SIGIL
  stratum              sigil
  variant              $S '.wheel' { recolor '#111111'; }
  ir correct/competitor  5be0d4314219 / d74513ab1dcc
```

**Read the last line of each.** The IR hashes are **identical across
families** — `5be0d4314219` correct, `d74513ab1dcc` reverted. Same abstract
program, same collision, same competitor, **different concrete syntax and a
different prefix** (17 chars vs 4).

That is the cross-family transfer test in one object: a predictor trained on
`dom` prefixes must rank the `blk` site, with everything except the surface
held constant.

---

## 5. Measured results

### Materials (`python3 scripts/build_materials.py`)

```
delta family      9 members, densities 0.28–0.76, all validate
templates         80 templates, 200 operations
total sites       18,258
SEMANTIC          7,290
prefix-distinct   3,326        (Phase 3: 40; target 300 — MET)
strata            sigil 1,594 | verb 1,000 | keyword 732
families          dom, blk     lexicons 9 → held-out mappings available
```

### Real-model Arm A — balanced, with a real rule table and a control

`d50s1`, **272 `dom` + 272 `blk`** sites, both conditions, Qwen2.5-Coder 0.5B
base and instruct. ~70 s per checkpoint on one laptop RTX 3080 Ti. **2,176
per-site rows saved.**

Reversion rate **with the full 28-role token table in context**:

| model | family | sigil | verb | keyword | all |
|---|---|---:|---:|---:|---:|
| 0.5B base | dom | 0.430 | 0.286 | 0.477 | 0.412 |
| 0.5B base | blk | 0.444 | 0.482 | 0.462 | 0.456 |
| 0.5B instruct | dom | 0.391 | 0.500 | 0.523 | 0.445 |
| 0.5B instruct | blk | 0.391 | 0.429 | 0.492 | 0.423 |

Rule effect, `M_seq(rule) − M_seq(norule)`:

| model | family | mean | median | sites helped |
|---|---|---:|---:|---:|
| 0.5B base | dom | +0.171 | +0.070 | 55.1% |
| 0.5B base | blk | +0.156 | +0.043 | 52.6% |
| 0.5B instruct | dom | +0.199 | +0.098 | 53.7% |
| 0.5B instruct | blk | +0.222 | +0.238 | 59.2% |

**Three readings, all preliminary (n = 272 per cell, one lexicon, one model
family, one prompt, point estimates with no intervals):**

1. **`blk` ≈ `dom`.** 0.41–0.46 in both. The effect is **not** an artifact of
   `dom`'s 1.077 fertility — which could not be known before, because the
   first run never scored `blk`.
2. **Supplying the table barely helps.** ~0.2 nats, helping 52.6–59.2% of
   sites — barely above a coin flip — while reversion stays near 0.42–0.46
   *with the table present*. This is the first result here that is genuinely
   about rule-following rather than prior strength.
3. **No stable stratum ordering.** Verb is the lowest cell in one condition
   (0.286) and the highest in another (0.500). The earlier "sigil ≥ verb"
   claim came from the dom-only, no-table run and is **withdrawn**.

Measurement health: **3 exact-zero margins out of 2,176** (0.14%), all
single-token sigil pairs, printed by name every run. Merged candidates: dom
118/272, blk 138/272.

### Fertility (real tokenizer)

| family | `F_rel` vs identity |
|---|---:|
| `dom` | 1.072 – 1.078 |
| `blk` | **1.003 – 1.009** |

Phase 3's character-length proxy said 1.0078 and understated the `dom`
confound ~10×. `blk` is the fertility-controlled arm.

---

## 6. Component status

| # | Component | Status |
|---|---|---|
| 1 | experiment configuration | **partial** — `configs/` template, not consumed; `env` block now recorded per run |
| 2 | candidate-pair definitions | **tested** |
| 2b | **grammar-family definitions** | **tested** — 2 real families |
| 3 | prior-strength `T` calibration | **not implemented** |
| 4 | local-context `A` calibration | **not implemented** |
| 5 | **counterbalanced mappings** | **tested** — 9 seeded members |
| 6 | forced-prefix scoring | **tested + measured**, P32-001 corrected |
| 7 | unrestricted generation | **not run** |
| 8 | parsing + canonical IR | **tested** |
| 9 | site-reach detection | inherited from Phase 3, **not re-run** |
| 10 | reversion classification | **tested + measured** |
| 11 | result serialization | **tested** — 2,176 per-site rows with full provenance; no formal schema |
| 12 | statistical-analysis prep | **not implemented** |
| 13 | invariant validation | **tested** — V1–V8, IR round-trip, offsets, I7 |
| 14 | seeds + env capture | **partial** — seeded lexicons/templates; `env` block (python, platform, dtype, device); **no global run seed, no model revision pinning** |
| 15 | unit + end-to-end tests | **tested** — 36 passing |

### Reproducibility checklist

| # | Check | Result |
|---|---|---|
| 1 | unit tests | **PASS** — 36/36 |
| 2 | end-to-end fake-model test | **PASS** — fake scorer, divergence arithmetic |
| 3 | counterbalancing validated | **PASS** — `test_seeds_counterbalance_the_assignment` |
| 4 | both candidates grammar-valid | **PASS** — both families |
| 5 | candidates map to different IR | **PASS** |
| 6 | context variants share AST/IR | **CANNOT RUN** — A-levels not built |
| 7 | train/calibration/test separation | **PARTIAL** — held-out mappings possible; **no split enforced and no preregistration written** (next step 7) |
| 8 | deterministic seeds | **PASS** for lexicons and templates; **no global run seed** |
| 9 | exact result serialization | **PARTIAL** — JSON round-trips, no schema |
| 10 | nothing outside phase3_2/ modified | **PASS** except the 10 generated `phi_d*.json` written into `phase3/vendor/alien_syntax/candidates/` — **declared**, see `04 §9` |

Checks 6 and 7 are **blocked or partial, not passing.**
