# 03 — Methods and pipeline (what runs, in what order)

Code is in `../phase3_2/`. This is the runbook.

```
                      PREREGISTRATION.md  (frozen first — nothing below may revise it)
                                 │
build_materials.py ──────────────┤   80 templates × 9 lexicons × 2 families
   deltafam.build(density,seed)  │   → 18,258 sites, 7,290 SEMANTIC,
   templates.build_templates()   │     3,326 prefix-distinct
   sites2.classify(..., backend) │
                                 ▼
                     sampling.balanced(pool, limit)
                     sampling.assert_balanced(...)      ← P32-003 guard
                                 │
         ┌───────────────────────┴───────────────────────┐
  run_arm_a.py                                    run_primary.py
   prompts.rule_prompt / norule_prompt             prompts.paraphrase p0/p1/p2
   margins.divergent_margin   ← P32-001 fix        LADDER 0..32 → k*
   → 2,176 per-site rows                           → 720 rows + 240 curves
         └───────────────────────┬───────────────────────┘
                                 ▼
                       analysis.cluster_bootstrap     (templates, B=2000)
                       analysis.length_matched_strata
                       runmeta.capture / pin          (env + model revisions)
```

## Stage notes

**`sampling.balanced`** — round-robins across (family × lexicon × stratum).
`assert_balanced` raises if a family is missing; a regression test reproduces
the original first-*N* defect deliberately.

**`prompts`** — `rule_prompt` renders the 28-role table **from the φ-map**, so
it cannot drift from the lexicon it describes. `norule_prompt` is the matched
control: same framing, same line count, spellings withheld.

**`margins.divergent_margin`** — scores both candidates from the first
divergent **token**, so a candidate that BPE merges into the previous token is
still measurable. Records `k_common` and `merged` per site.

**`run_primary.py`** — the extinction ladder plus paraphrase robustness. The
in-context examples are correct programs in the target lexicon, because the
dose is *demonstrated evidence*, not text volume.

**`analysis`** — cluster bootstrap at the template level; length-matched
stratum comparison; both run on saved rows with no GPU.

**`runmeta`** — writes git commit, dirty flag, python/torch/transformers/CUDA,
device name, dtype, SLURM job id, source-file hashes, and the **resolved HF
revision sha** of every model from the local cache.

## Commands

```bash
cd ../phase3_2
python3 scripts/build_materials.py                       # materials + census
python3 tests/run_tests.py                               # 36 tests, no GPU
../run/.venv/bin/python scripts/run_arm_a.py --limit 0 --json outputs/arm_a_balanced.json
../run/.venv/bin/python scripts/run_primary.py --sites 120 --json outputs/primary.json
PYTHONPATH=src python3 -c "from phase3_2 import analysis as A; ..."   # intervals
```

## Reproducibility checklist

| # | check | result |
|---|---|---|
| 1 | unit tests | **PASS** — 36/36 (Phase 3's 54 also still pass) |
| 2 | end-to-end fake-model test | **PASS** |
| 3 | counterbalancing validated | **PASS** |
| 4 | both candidates grammar-valid | **PASS** |
| 5 | candidates map to different IR | **PASS** |
| 6 | context variants share AST/IR | **CANNOT RUN** — A-levels not built |
| 7 | train/calibration/test separation | **PASS (declared)** — frozen in `PREREGISTRATION.md`; **not enforced in code** |
| 8 | deterministic seeds | **PASS** for lexicons/templates/bootstrap; no global run seed |
| 9 | exact result serialization | **PASS** — 2,176 + 720 + 240 rows with provenance |
| 10 | nothing modified outside the phase dirs | **PASS**, except the declared φ-file deviation |

Checks 6 remains blocked. Check 7 is now declared but relies on discipline,
not on a guard.
