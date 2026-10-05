# Phase 3.2 — materials rebuild, second grammar family, first real-model numbers

Phase 3 ended with one blocker, and it was not scientific: **40
prefix-distinct semantic sites in one grammar family.** Phase 3.2 fixes the
materials, adds a real second grammar family, and runs the cheap real-model
check that the rebuild made worth running.

**Teaching documents:** [`phase3_2_explained/`](phase3_2_explained/) — start
with `00_complete_phase3_2_guide.md`.
**What changed and what is superseded:** [`CHANGES_FROM_PHASE3.md`](CHANGES_FROM_PHASE3.md).

```bash
cd phase3_2
python3 scripts/build_materials.py        # build + measure the materials
python3 tests/run_tests.py                # 36 tests, lark only, no GPU
../run/.venv/bin/python scripts/run_arm_a.py --fertility-only   # real tokenizer
../run/.venv/bin/python scripts/run_arm_a.py --limit 0          # all 544 sites
```

## Headline

| | Phase 3 | Phase 3.2 |
|---|---|---|
| grammar families | 1 | **2** (`dom`, `blk`) |
| lexicons | 1 | **9** (3 densities × 3 seeds) |
| templates | 62 | **80** |
| prefix-distinct semantic sites | **40** | **3,326** |
| counterbalancing / held-out mappings | none | both |
| real-model Arm A | never run | **6 checkpoints** |

## Results

**1. Materials target met.** 18,258 sites classified, 7,290 SEMANTIC, **3,326
prefix-distinct** (target 300; Phase 3 had 40). Strata: sigil 1,594 / verb
1,000 / keyword 732.

**2. Four defects found and fixed — three of them Phase 3.2's own.** ⚠️

| id | defect | effect |
|---|---|---|
| P32-001 | `sequence_logprob` returned `0.0` when BPE merged the candidate into the prefix token (**44.2%** of sites) | **false null**, worst at sigil sites |
| P32-002 | the "rule" prompt said *follow the token table* and **contained no table** | measured prior preference, **not rule-override** |
| P32-003 | `out[:limit]` over a family-concatenated list scored **240 dom, 0 blk** | dropped the **fertility-matched** family |
| P32-004 | aggregates only | no re-analysis, no family split |

Each has a regression test that reproduces the defect deliberately.

**3. Balanced Arm A: `blk` ≈ `dom`.** 272 sites per family, both conditions,
0.5B base + instruct, **2,176 per-site rows saved**. Reversion **with the
full token table in context**:

| model | family | sigil | verb | keyword | all |
|---|---|---:|---:|---:|---:|
| 0.5B base | dom | 0.430 | 0.286 | 0.477 | 0.412 |
| 0.5B base | **blk** | 0.444 | 0.482 | 0.462 | **0.456** |
| 0.5B instruct | dom | 0.391 | 0.500 | 0.523 | 0.445 |
| 0.5B instruct | **blk** | 0.391 | 0.429 | 0.492 | **0.423** |

`blk` is fertility-matched (1.008 vs `dom`'s 1.077) and shows the same rates,
so the effect is **not** token cost in disguise.

**4. The token table barely helps.** Mean rule effect +0.156 to +0.222 nats;
it helps **52.6–59.2%** of sites — barely above a coin flip — while reversion
stays at 0.42–0.46 *with the table present*. This is the first result here
that is genuinely about rule-following rather than prior strength.

**5. WITHDRAWN — the 3D-knowledge conclusion.** The earlier "sigil ≥ verb at
every checkpoint" came from the dom-only, no-table run. Balanced, the ordering
flips (verb 0.286 in one condition, 0.500 in another). **The 3D question is
reopened**; a length-matched sub-analysis is needed first.

*All real-model numbers: one lexicon, one model family, one prompt, no
confidence intervals.*

## Layout

```
phase3_2/
├── README.md · CHANGES_FROM_PHASE3.md
├── phase3_2_explained/      00–06, the teaching set
├── src/phase3_2/
│   ├── _vendor.py           declared dependency on phase3/ + two guards
│   ├── backends.py          Backend protocol · DomBackend · BlkBackend  ← new family
│   ├── templates.py         80 IR-built templates, varied openings
│   ├── deltafam.py          density × seed lexicon family
│   ├── sites2.py            Phase 3's classifier, backend-generic
│   ├── margins.py           first-divergent-token scoring (P32-001)
│   ├── prompts.py           the real token table + matched control (P32-002)
│   └── sampling.py          balanced selection across cells (P32-003)
├── scripts/                 build_materials.py · run_arm_a.py
├── tests/                   36 tests, no GPU
└── outputs/                 site inventory + Arm A JSON
```

## Dependency on Phase 3 (declared, not silent)

Phase 3.2 **imports** `phase3.scoring`, `phase3.outcomes`, `phase3.linter` and
reads `phase3/vendor/` rather than re-copying 4,380 lines. Holding the
measurement code fixed while changing the materials is the design: a
difference in results cannot be blamed on a changed scorer. `_vendor.py`
checks both at import, including that the P3-001 scorer repair is still
applied.

**Declared deviation:** `deltafam.write` puts 9 `phi_d*.json` into
`phase3/vendor/alien_syntax/candidates/`, because `phi.load_candidate`
resolves only there. `vendor_sync.py --check` will not notice — it verifies
the files it copied, not additions. See `phase3_2_explained/04 §9`.

## Status

**Closed since Phase 3:** grammar-family definitions · counterbalanced
mappings · held-out mappings · real-model Arm A · real fertility · P32-001.

**Not implemented:** preregistration · bootstrap intervals at template/mapping
level · mixed-effects and power simulation · `T`/`A` calibration ·
length-matched stratum analysis · prompt-paraphrase robustness · model-revision
pinning.

**Not run:** Arm B · extinction curves on a real model · the H4 linter on real
scores · any external DSL · 7B+ checkpoints (3B already warned on a 16 GB
laptop GPU — that is what Sol is for).

**Next:** see [`phase3_2_explained/07_next_steps.md`](phase3_2_explained/07_next_steps.md).
In order: preregister the splits and success criteria, re-analyse the strata
length-matched, check prompt-paraphrase robustness, then run extinction curves
on `blk`. Scale to Sol only if the effect survives there with intervals.
