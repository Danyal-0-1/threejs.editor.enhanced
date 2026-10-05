# 00 — The complete Phase 3.2 guide

Read this first. Companions: `01` theory · `02` mathematics · `03` code ·
`04` retyping · `05` glossary · `06` questions. Changes and superseded
numbers: `../CHANGES_FROM_PHASE3.md`.

---

## 1. What Phase 3.2 is

Phase 3 ended with one blocker, and it was not scientific: **40
prefix-distinct semantic sites in one grammar family.** Too few and too narrow
to spend cluster time on.

Phase 3.2 is the materials rebuild, plus the cheap real-model check the
rebuild made worth running. The science is unchanged — H4 (predict risky
sites) first, H5 (repair them) with it, extinction curves as the scientific
result, H2 secondary.

| | Phase 3 | Phase 3.2 |
|---|---|---|
| grammar families | 1 | **2** (`dom`, `blk`) |
| lexicons | 1 | **9** (3 densities × 3 seeds) |
| templates | 62 Phase 1 programs | **80** purpose-built |
| prefix-distinct semantic sites | **40** | **3,326** |
| counterbalancing | none | seeded rotation |
| held-out mappings | impossible | available |
| real-model Arm A | never run | **6 checkpoints measured** |

---

## 2. What enters

| Input | Source | Size |
|---|---|---|
| frozen terminal table | `terminals.json` (via Phase 3's vendor tree) | 43 terminals, 29 substitutable |
| delta family | generated here | 9 lexicons |
| templates | generated here, as IR | 80 templates / 200 ops |
| grammar families | `DomBackend`, `BlkBackend` | 2 |
| models | Qwen2.5-Coder 0.5B/1.5B/3B, base + instruct | locally cached |

## 3. What happens

```
terminals.json ─► deltafam.build(density, seed) ─► 9 φ, each validate_phi V1–V8
templates.build_templates()                     ─► 80 IRPrograms
                         │
          ┌──────────────┴──────────────┐
    DOM.render(ir, φ)              BLK.render(ir, φ)
 (function(){ $S('#wheel')…         $S '#wheel' { recolor …; }
          └──────────────┬──────────────┘
                         ▼  sites2.classify(text, φ, backend)
                 scan_sites → (type, value, OFFSET)
                 splice q → re-parse → re-hash
                 NONE / LEXICAL / BENIGN / SEMANTIC
                         ▼  dedupe_by_prefix
                   3,326 prefix-distinct SEMANTIC sites
                         │
           ┌─────────────┴─────────────┐
   margins.divergent_margin       sites2.stratum
   (first-divergent-token M_seq)   sigil / verb / keyword
           └─────────────┬─────────────┘
                         ▼
                  reversion per stratum, per checkpoint
```

## 4. What exits

| Output | Status |
|---|---|
| 9 validated lexicons | **measured** |
| 80 templates, both families | **tested** — 0 IR mismatches |
| 18,258 classified sites / 7,290 SEMANTIC / 3,326 prefix-distinct | **measured** |
| real token fertility | **measured** |
| Arm A reversion, 6 checkpoints, stratified | **measured** (n=240, no intervals) |
| extinction curves, Arm B, linter | **not run** |

---

## 5. The results that matter

### (1) The materials target was met

**3,326** prefix-distinct semantic sites (Phase 3: 40; target: 300), across
**2 grammar families** and **9 counterbalanced lexicons**. Strata: sigil
1,594 / verb 1,000 / keyword 732.

### (2) Four defects found and fixed — three of them Phase 3.2's own ⚠️

| id | defect | effect |
|---|---|---|
| **P32-001** | `sequence_logprob` returned `0.0` when BPE merged the candidate into the prefix token — **44.2%** of sites | manufactured a **false null**, worst at sigil sites |
| **P32-002** | the "rule" prompt said *follow the token table* and **contained no table** | measured raw prior preference, **not rule-override** |
| **P32-003** | `out[:limit]` over a family-concatenated list scored **240 dom, 0 blk** | dropped the **fertility-matched** family and reported both |
| **P32-004** | only aggregates were saved | no re-analysis, no family split recoverable |

All four are fixed, with regression tests that reproduce each defect
deliberately. Full blast radius in `../CHANGES_FROM_PHASE3.md`.

### (3) Balanced Arm A — `blk` ≈ `dom`, so the effect is not a fertility artifact

`d50s1`, **272 dom + 272 blk**, both conditions, 0.5B base + instruct,
**2,176 per-site rows saved**.

Reversion **with the full 28-role token table in context**:

| model | family | sigil | verb | keyword | all |
|---|---|---:|---:|---:|---:|
| 0.5B base | dom | 0.430 | 0.286 | 0.477 | 0.412 |
| 0.5B base | **blk** | 0.444 | 0.482 | 0.462 | **0.456** |
| 0.5B instruct | dom | 0.391 | 0.500 | 0.523 | 0.445 |
| 0.5B instruct | **blk** | 0.391 | 0.429 | 0.492 | **0.423** |

`blk` is the fertility-controlled family (1.008 vs `dom`'s 1.077), and it
shows the same rates. The effect is **not** token-cost in disguise — which
could not be known before, because the first run never scored `blk`.

### (4) The token table barely helps — the first genuine rule-following result

| model | family | mean rule effect | median | sites helped |
|---|---|---:|---:|---:|
| 0.5B base | dom | +0.171 | +0.070 | 55.1% |
| 0.5B base | blk | +0.156 | +0.043 | 52.6% |
| 0.5B instruct | dom | +0.199 | +0.098 | 53.7% |
| 0.5B instruct | blk | +0.222 | +0.238 | 59.2% |

A 28-role authoritative mapping moves the margin ~0.2 nats and helps **barely
more often than a coin flip**, while reversion stays at **0.42–0.46 with the
table present**. This is PLSemanticsBench's finding at the token level, on
prompt-defined DSL surfaces.

### (5) WITHDRAWN: the 3D-knowledge conclusion

The earlier claim — "sigil ≥ verb at every checkpoint, so 3D-domain knowledge
is not driving the effect" — came from the dom-only, no-table run. Under
balanced sampling with a real rule, the ordering **flips**: verb is the lowest
cell for 0.5B base/dom (0.286) and the highest for 0.5B instruct/dom (0.500).

**The 3D question is reopened.** A length-matched sub-analysis is required
first: sigil candidates are single characters, verb candidates are words.

*All real-model numbers: n = 272 per cell, one lexicon, one model family, one
prompt, point estimates with **no confidence intervals**.*

## 6. One complete example

```
3DOM template t000, lexicon d50s1, the SAME site in both families:

dom  (function(){ $S('#wheel')#recolor('#111111'); })();
                  ↑ offset 17   prefix "(function(){ $S('"
blk  $S '#wheel' { recolor '#111111'; }
         ↑ offset 4            prefix "$S '"

both:  terminal T_CLASS_SIGIL · correct '#' · competitor '.'
       collision SEMANTIC · competitor binds to T_ID_SIGIL · stratum sigil
       ir_hash_correct     5be0d4314219      ← IDENTICAL across families
       ir_hash_competitor  d74513ab1dcc      ← IDENTICAL across families

variant (dom)  (function(){ $S('.wheel')#recolor('#111111'); })();
variant (blk)  $S '.wheel' { recolor '#111111'; }

Qwen2.5-Coder tokenisation at the dom site:
  tok(prefix)       … 492   `('`     len 12
  tok(prefix + '#') … 3515  `('#`    len 12   ← merged: Phase 3 returned 0.0
  tok(prefix + '.') … 4291  `('.`    len 12
  k_common = 11  →  one token scored per side, same 11-token context
```

Same abstract program, same collision, same competitor; different surface,
different prefix, **identical meaning**. That pair *is* the cross-family
transfer test.

---

## 7. Support and falsification

**H4 supported** if site risk beats `identity_baseline` and `length_baseline`
on held-out mappings **and** transfers `dom → blk`. The second is new and
sharper: a predictor that works within a family but not across one has learned
the family.

**H4 falsified** if it fails either, or if it separates lexicons but not sites
within a lexicon.

**Materials inadequate** if usable sites fall back below ~300 prefix-distinct,
or if `blk`'s fertility advantage vanishes under another tokenizer.

**Surface framing wrong** if the sigil stratum shows no effect while verb
sites do. Measured so far: the opposite.

**Mechanistic follow-up still blocked** — the behavioural gate requires
replication on a held-out grammar family, which is now *possible* but has not
been *done*.

---

## 8. What to read, retype, and understand first

**Read:** `margins.py` → `CHANGES_FROM_PHASE3.md` → `backends.py` →
`deltafam.py` → `04_retyping_and_reading_plan.md`.

**Retype — 291 lines, 14.5%:** `margins.score_pair`, `_score_from`,
`divergent_margin`; `backends.scan_sites`, `_scan_inner`, `BlkBackend.parse`;
`sites2.classify`; `deltafam.build`, `verb_groups`. Line ranges, invariants
and the test to run after each: `04 §6`.

**Mathematics first:** the first-divergent-token margin and why the shared
prefix cancels (`02 §1`) → why character length is not fertility (`02 §2`) →
role density vs site density (`02 §3`) → everything in Phase 3's `02`.

---

## 9. Honest status

**Tests: 36 passed, 0 failed** (`python3 tests/run_tests.py`, lark only).
Phase 3's 54 still pass unchanged.

**Closed since Phase 3:** grammar-family definitions · counterbalanced
mappings · held-out mappings · real-model Arm A · real fertility · balanced
sampling · a real rule prompt with a matched control · per-site records ·
defects P32-001 through P32-004.

**Still not implemented:** preregistration · bootstrap intervals at the
template/mapping level · mixed-effects and power simulation · prior-strength
`T` and local-context `A` calibration · length-matched stratum analysis ·
prompt-paraphrase robustness · model-revision pinning. See `07_next_steps.md`.

**Still not run:** Arm B (unrestricted generation) · extinction curves on a
real model · the H4 linter on real scores · any external DSL · 7B+ checkpoints
(the 3B run already hit an allocator warning on a 16 GB laptop GPU; this is
what Sol is for).

**Declared deviation:** Phase 3.2 writes 9 `phi_d*.json` into
`phase3/vendor/alien_syntax/candidates/`, because `phi.load_candidate`
resolves only there. `vendor_sync.py --check` will not catch it — it verifies
the files it copied and does not notice additions. See `04 §9`.

**The number that matters most now:** every real-model figure comes from
**one lexicon, one model family, one prompt, and no confidence intervals** —
and the one clean story this project produced so far (the stratum ordering)
**did not survive** its first properly controlled re-run. The materials are
ready; the results are not yet results. `07_next_steps.md` says what closes
the gap.
