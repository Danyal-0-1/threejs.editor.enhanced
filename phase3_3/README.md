# Phase 3.3 — next steps executed, results, and Sol readiness

> ⚠️ **ERRATUM (2026-10-05) — read [`ERRATA.md`](ERRATA.md) first.** The `k*` ≈ 5–7 result below is **withdrawn** (82/120 sites saw their own target program among the demonstrations, plus two definition errors), and the rule-effect intervals are **corrected** (all four now include zero). `blk` is not a clean held-out grammar family.


**Code stays in [`../phase3_2/`](../phase3_2/)** — almost all of it was
already there, and holding the measurement code fixed while the analysis
changes is the design. This directory holds the **reports, the results, and a
snapshot of the data**.

## Read in this order

| file | what it is |
|---|---|
| **[`00_results_in_plain_language.md`](00_results_in_plain_language.md)** | **start here.** Every result with a mental image, plus the theory and maths in simple terms |
| [`01_changes_and_results.md`](01_changes_and_results.md) | the rigorous version — all numbers with intervals |
| [`02_theory_and_math.md`](02_theory_and_math.md) | `k*`, the rule effect, cluster bootstrap, length matching |
| [`03_methods_and_pipeline.md`](03_methods_and_pipeline.md) | the runbook and the reproducibility checklist |
| [`04_sol_readiness.md`](04_sol_readiness.md) | the go/no-go checklist with evidence |
| [`05_knowledge_check.md`](05_knowledge_check.md) | 22 questions, no answers |
| `outputs_snapshot/` | the data these reports are computed from |

Earlier documents remain valid for their own phases:
`../phase3/phase3_explained/` (concepts, 7 docs) and
`../phase3_2/phase3_2_explained/` (materials and defects, 8 docs).

## Headline

| | |
|---|---|
| **Reversion with the full token table present** | **0.41 – 0.46** (tight intervals) |
| **Effect of supplying the table** | +0.16 to +0.22 nats — **3 of 4 intervals include zero** |
| **`k*` — examples needed to break the habit** ⭐ | **4.96 – 6.94** median; **8–18% never cross** |
| **Fertility-controlled family (`blk`)** | same rates — not a tokenizer artifact |
| **Paraphrase stability** | reversion moves ≤ 0.05 across three framings |
| **3D-knowledge conclusion** | **withdrawn** — not identifiable with these materials |

## What was executed from `07_next_steps`

**Done:** preregistration (item 7) · cluster-bootstrap intervals at the
template level (item 8) · length-matched stratum re-analysis ·
prompt-paraphrase robustness · **extinction curves on real weights — the
declared primary estimand, run for the first time** · model-revision pinning
and environment capture · the Sol launch kit.

**Not done:** item 10 (scale to larger checkpoints and a second tokenizer
family — that is the Sol run itself) · power simulation · Arm B · the H4
linter on real scores · the external DSL.

## New code (in `../phase3_2/`)

`src/phase3_2/analysis.py` (223) · `src/phase3_2/runmeta.py` (101) ·
additions to `prompts.py` (201) and `sampling.py` (106) ·
`scripts/run_primary.py` (176) · `PREREGISTRATION.md` (142) ·
`sol/` (129: README, 2 SLURM scripts, prefetch).

**Tests: 36 pass in `phase3_2`, 54 in `phase3`.**

## Sol

```bash
cd ../phase3_2
export HF_HOME=/scratch/$USER/hf
python sol/prefetch_models.py --tier small    # login node
sbatch sol/arm_a.slurm                        # development cells only
sbatch sol/primary.slurm
```

**The gate:** do not scale beyond 3B until the effect is present in `blk`
with an interval excluding the null, and do not read a held-out cell until
the development analysis is finished and frozen.
