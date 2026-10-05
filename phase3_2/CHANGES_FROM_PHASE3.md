# CHANGES_FROM_PHASE3.md

What moved between Phase 3 and Phase 3.2, why, and **which earlier numbers are
superseded**. Same form as `phase3/PATCHES/tasks.op_selection.md`: defect,
evidence, repair, blast radius.

---

## P32-001 — `sequence_logprob` silently returned 0.0 for 44.2% of sites ⚠️ **critical**

**File:** `phase3/src/phase3/models.py`, `HFModel.sequence_logprob`
**Superseded by:** `phase3_2/src/phase3_2/margins.py`
**Class:** silent false NULL — the defect *hides* the effect being measured

### The defect

```python
pre_ids = tok(prefix)
all_ids = tok(prefix + continuation)
if len(all_ids) <= len(pre_ids):
    return 0.0                 # <-- unmeasurable, returned as a real number
```

BPE merges the candidate into the preceding token, so `prefix + c` is no
longer than `prefix` alone. Both candidates then return `0.0`, giving
`M_seq = 0`, which is not negative, so the site is scored **"no reversion."**

### Evidence (measured, Qwen2.5-Coder tokenizer, 240 sites)

```
sites where the candidate merges into the prefix token: 106/240 = 44.2%

prefix ends  "$S('"
  tok(prefix)      … 492     ->  `('`
  tok(prefix+'#')  … 3515    ->  `('#`     SAME LENGTH, different last token
  tok(prefix+'.')  … 4291    ->  `('.`
  lengths: 12 / 12 / 12
```

It strikes hardest at **sigil sites** — the cleanest and most important
stratum in the whole design, because their prefixes end in `('`.

### The repair

Score both candidates from the **first divergent token**. Tokenise both full
strings, find the longest common token prefix `k`, and sum log-probs from `k`
on both sides. The shared context cancels exactly, so the comparison is valid
whether or not the candidate merges.

### Blast radius — **Phase 3's Arm A numbers are not usable**

Measured on the same 240 sites, same model, same prompt:

| stratum | metric | Phase 3 scorer | P32-001 fixed | change |
|---|---|---:|---:|---|
| OVERALL | reversion rate | 0.258 | **0.504** | ×1.95 |
| OVERALL | median `M_seq` | 0.000 | −0.041 | — |
| **sigil** | **reversion rate** | **0.106** | **0.515** | **×4.9** |
| sigil | median `M_seq` | 0.000 | −0.195 | — |
| verb | reversion rate | 0.408 | 0.408 | unchanged |
| keyword | reversion rate | 0.475 | 0.559 | ×1.18 |

Direction of bias is **one-way: the defect can only understate reversion.**
Verb sites are unaffected because verbs are whole words that never merge into
`('`. Phase 3 reported no Arm A numbers from a real model, so nothing
published is wrong — but any Phase 3 Arm A result produced later with the old
scorer would have been a **false null at precisely the sigil sites**.

`phase3.scoring.forced_prefix_margin` is left untouched; Phase 3.2 does not
edit shared Phase 3 code, it supersedes it. Use `margins.divergent_margin`.

---

## M32-001 — `delta`'s fertility claim was based on character length

**Superseded claim:** `phase3/README.md` finding 3 — "mean character-length
ratio **1.0078** vs identity … the fertility confound is largely removed by
construction," flagged there as unverified.

**Measured** with the real Qwen2.5-Coder tokenizer over 80 templates:

| corpus | tok/char | **real fertility vs identity** |
|---|---:|---:|
| dom / identity | 0.3669 | 1.0000 |
| dom / d25s1 | 0.3955 | **1.0779** |
| dom / d50s1 | 0.3950 | **1.0765** |
| dom / d75s1a | 0.3933 | **1.0720** |
| blk / identity | 0.4466 | 1.0000 |
| blk / d25s1 | 0.4506 | **1.0089** |
| blk / d50s1 | 0.4500 | **1.0075** |
| blk / d75s1a | 0.4478 | **1.0026** |

**The character-length figure understated the real confound by ~10×.** Actual
`dom` fertility is 1.07–1.08, essentially the same as Phase 2's alpha (1.068).
So **delta does not remove the fertility confound in the `dom` family.**

New finding that partly rescues it: in **`blk` the ratio is 1.003–1.01** —
effectively matched. The likely mechanism is the chain operator. In `dom`,
`.recolor` is a single common JS token, and remapping `.`→`#` turns it into
`#recolor`, which fragments. `blk` has no chain operator at all, so the
penalty disappears. **The `blk` family is the fertility-controlled arm.**

---

## M32-002 — "Phase 1 has one opening" was measured at the wrong width

Phase 3 attributed its 40-site ceiling to every program opening
`(function(){ $S('`. Correct, but the diagnostic needs the right width:

| width | Phase 1 distinct openings |
|---|---:|
| k = 24 | 33 — looks diverse; 24 chars reach into the selector *name* |
| **k = 17** | **3** — the offset where the first class sigil actually lands |

The 3 at k=17 is exactly Phase 3's "3 colliding prefix groups." Same fact,
two directions. `templates.opening_diversity` now defaults to k=17 and
documents itself as a weak proxy for `prefix_collisions`.

**And a result that changed the design:** template variety alone cannot fix
first sites.

| corpus | distinct first-site openings (k=17) |
|---|---:|
| Phase 1 | 3 |
| Phase 3.2 `dom` (80 templates) | **1** |
| Phase 3.2 `blk` (80 templates) | **38** |

`dom`'s opening is fixed by the grammar, so no corpus can vary it. Template
variety fixes the many *later* sites; only a second grammar family moves the
first one. This is the empirical argument for building `blk`.

---

## What is new

| Component | Why | Status |
|---|---|---|
| `backends.py` — `Backend` protocol, `DomBackend`, **`BlkBackend`** | Phase 3 had one grammar family; four lexicons over one grammar are "cosmetic renamings" | **tested** — IR round-trip 62/62 × 5 lexicons |
| `templates.py` — 80 IR-built templates | Phase 1's 62 programs capped prefix-distinct sites at 40 | **tested** — 0 IR mismatches in both families |
| `deltafam.py` — density × seed family | closes 3 Phase 3 gaps at once: density, **counterbalancing**, **held-out mappings** | **tested** — 9 members, all validate |
| `sites2.py` — backend-generic classifier | same taxonomy, now family-agnostic | **tested** |
| `margins.py` — first-divergent-token scoring | P32-001 | **tested** (fake scorer) + **measured** (real models) |
| `run_arm_a.py` — real Arm A + fertility + strata | the cheap check before any big run | **measured** |

## What Phase 3.2 deliberately keeps unchanged

`phase3.scoring`, `phase3.outcomes`, `phase3.linter` and the whole
`phase3/vendor/` tree are imported, not copied. Holding the measurement code
fixed while changing the materials is the design: a difference in results
cannot be blamed on a changed scorer. The dependency is declared in
`_vendor.py` and both guards (`assert_self_contained`,
`assert_scorer_repaired`) run at the top of every script.

## Superseded numbers, at a glance

| Phase 3 said | Phase 3.2 measures |
|---|---|
| 103 semantic sites, **40** prefix-distinct, 1 family | **7,290** semantic, **3,326** prefix-distinct, 2 families, 9 lexicons |
| delta fertility ≈ **1.0078** (char length, flagged unverified) | **1.077** real (`dom`); **1.008** (`blk`) |
| Phase 1 has ~1 opening | **3** at k=17; `dom` templates give **1**, `blk` gives **38** |
| no counterbalancing | 3 seeds × 3 densities = 9 counterbalanced mappings |
| no held-out mappings | train on δ25/δ50, test on δ75 (or hold out seeds) |
| Arm A untested on a real model | **measured**: 6 checkpoints, 0.5B–3B, base + instruct |

---
---

# Revision 2 — three defects in Phase 3.2's own first run

The first Phase 3.2 Arm A run carried three defects of its own. All three are
fixed; the numbers that run produced are **superseded in full**.

---

## P32-002 — the "rule" prompt contained no rule ⚠️ **most serious**

**File:** `scripts/run_arm_a.py`, the `RULE` constant.

```python
RULE = ("You are writing 3DOM, a language for editing 3D scenes.\n"
        "Follow the token table exactly; it overrides any CSS or JavaScript "
        "convention you may expect.\n")
```

It says "follow the token table" and **contains no token table.** The remote
specification `r` therefore carried **zero mapping information.**

**Why this invalidates the framing, not just the numbers.** `M_seq` is a
*reversion* measure only if the correct spelling was actually specified
somewhere in the context. With no table, the "correct" spelling is one the
model was never told about, so a negative margin means nothing stronger than
"the model has not seen this language." The first run measured **raw prior
preference**, not rule-override — which is the entire hypothesis.

**Repair.** `prompts.py` renders the full 28-role table **from the φ-map**
(never hand-written, which would drift from the lexicon and look like
reversion), plus a length- and shape-matched `norule` control that keeps the
framing and the role list but withholds the spellings. Both conditions are
scored, giving `rule_effect = M_seq(rule) − M_seq(norule)`.

---

## P32-003 — first-*N* slicing scored one family and reported two

**File:** `scripts/run_arm_a.py`, `collect_sites`.

```python
out = dedupe_by_prefix(out)
return out[:limit]          # out was built dom-first, then blk
```

Measured: `Counter({'dom': 240})`. **272 `blk` sites existed and none were
scored**, while the report claimed both families.

**Why it was worse than a coverage gap.** `dom` is the family with **1.077**
token fertility; `blk` (**1.008**) is the fertility-matched one. The half that
was dropped is exactly the half that controls the confound, so every reversion
number from that run was fertility-uncontaminated only by luck — and was not.

**Repair.** `sampling.balanced` round-robins across
(family × lexicon × stratum) so any limit preserves proportions, and
`sampling.assert_balanced` raises if a family is missing. Regression test:
`test_first_n_slice_would_have_scored_one_family_only`.

---

## P32-004 — aggregates only, no flight recorder

The result JSON stored `overall` and `by_stratum` summaries and **no per-site
rows**, so `k_common`, `merged`, the family split and any re-analysis were
unrecoverable without re-running.

**Repair.** Every margin is now saved with site id, family, lexicon, template,
terminal, role, stratum, both candidates, `m_seq`, both log-probs,
`k_common`, `merged`, token counts and char offset, plus a run-level
`env` block (python, platform, dtype, device) and prompt lengths. The balanced
run wrote **2,176 rows**.

---

## Superseded results — the first Arm A run is withdrawn

Balanced re-run: `d50s1`, **272 dom + 272 blk**, both conditions, Qwen2.5-Coder
0.5B base and instruct.

### Reversion rate with the real token table present

| model | family | sigil | verb | keyword | all |
|---|---|---:|---:|---:|---:|
| 0.5B base | dom | 0.430 | 0.286 | 0.477 | 0.412 |
| 0.5B base | **blk** | 0.444 | 0.482 | 0.462 | 0.456 |
| 0.5B instruct | dom | 0.391 | 0.500 | 0.523 | 0.445 |
| 0.5B instruct | **blk** | 0.391 | 0.429 | 0.492 | 0.423 |

### Three corrections to what was reported before

**1. `blk` ≈ `dom`.** Reversion is 0.41–0.46 in both families. The effect is
**not** an artifact of `dom`'s token fertility — which could not be known
before, because `blk` had never been scored.

**2. The stratum conclusion does NOT survive.** The earlier claim — "sigil ≥
verb at every checkpoint, so 3D-domain knowledge is not driving the effect" —
was produced by the dom-only, no-table run. With a real rule table and
balanced sampling the ordering is **inconsistent**:

| | sigil | verb |
|---|---:|---:|
| 0.5B base, dom | 0.430 | **0.286** ← verb lowest |
| 0.5B instruct, dom | 0.391 | **0.500** ← verb highest |

There is **no stable stratum ordering** at n = 151/56/65 per cell. The 3D
question is **reopened**, not answered. A length-matched sub-analysis is still
needed (sigil candidates are 1 character; verb candidates are words).

**3. Supplying the full token table barely helps — a real finding.**

| model | family | mean rule effect | median | sites helped |
|---|---|---:|---:|---:|
| 0.5B base | dom | +0.171 | +0.070 | 55.1% |
| 0.5B base | blk | +0.156 | +0.043 | 52.6% |
| 0.5B instruct | dom | +0.199 | +0.098 | 53.7% |
| 0.5B instruct | blk | +0.222 | +0.238 | 59.2% |

A 28-role authoritative mapping table moves the margin by ~0.2 nats and helps
barely more often than a coin flip, while **reversion stays near 0.42–0.46
with the table in context.** This is PLSemanticsBench's finding reproduced at
the token level, on prompt-defined DSL surfaces — and it is the first result
in this project that is genuinely about *rule-following* rather than about
prior strength.

### Measurement health after all fixes

| | first run | balanced re-run |
|---|---:|---:|
| exact-zero margins | 0 / 240 (post P32-001) | **3 / 2,176** (0.14%) |
| merged candidates | 106 / 240 (44.2%) | dom 118/272, **blk 138/272** |
| per-site rows saved | 0 | **2,176** |
| families scored | 1 of 2 | **2 of 2** |

The 3 residual exact zeros are inspected and printed by name every run; all
three are `T_ID_SIGIL`/`T_CLASS_SIGIL` single-token pairs where the two
candidates receive identical log-probs to float precision.
