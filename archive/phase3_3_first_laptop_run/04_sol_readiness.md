# 04 — Sol readiness

> ⚠️ **ERRATUM (2026-10-05) — read [`ERRATA.md`](ERRATA.md) first.** The `k*` ≈ 5–7 result below is **withdrawn** (82/120 sites saw their own target program among the demonstrations, plus two definition errors), and the rule-effect intervals are **corrected** (all four now include zero). `blk` is not a clean held-out grammar family.


A checklist with evidence, not an assertion. Launch kit: `../phase3_2/sol/`.

---

## Ready

| requirement | evidence |
|---|---|
| **Preregistration frozen** | `../phase3_2/PREREGISTRATION.md` — splits, numeric success criteria, exclusions, stopping rules, all dated before any run above 3B |
| **Measurement validated** | 4 scorer/sampling defects found and fixed, each with a regression test that reproduces it deliberately |
| **Materials sufficient** | 3,326 prefix-distinct SEMANTIC sites, 2 grammar families, 9 counterbalanced lexicons |
| **Balanced sampling enforced** | `sampling.assert_balanced` raises on a missing family |
| **Full provenance saved** | per-site rows + `runmeta` (git sha, dirty flag, torch/CUDA/transformers, device, dtype, SLURM id, source hashes, **resolved HF model revisions**) |
| **Intervals computed at the right unit** | template-level cluster bootstrap; refuses below 8 clusters |
| **Robustness checked** | 3 prompt paraphrases; reversion stable within 0.05 |
| **Primary estimand exercised on real weights** | `k*` = 4.96–6.94, intervals, censoring reported |
| **Submission scripts** | `sol/arm_a.slurm`, `sol/primary.slurm`, `sol/prefetch_models.py` |
| **Offline-node safe** | `HF_HUB_OFFLINE=1` + login-node prefetch; fails loudly rather than silently downloading |

## Known gaps — go anyway, but know them

| gap | consequence | mitigation |
|---|---|---|
| **No power analysis** | a null is weak evidence of absence | declared in the prereg; run a simulation before interpreting any null |
| **Dev cells only so far** | held-out performance unknown | that *is* the Sol run |
| `k*` uses median-among-crossers | **underestimates** `k*` | report censoring %; move to Kaplan–Meier |
| Rule/no-rule prompts differ in length | residual context-length confound | lengths reported with every result |
| 3D-knowledge contrast unidentifiable | one question unanswerable | needs single-token verb collisions — a materials change |
| Split enforced by discipline, not code | a held-out cell could be read by accident | keep dev and held-out runs in separate job scripts |

## Sizing

Measured on one RTX 3080 Ti, 0.5B, fp16:

| workload | measured |
|---|---|
| Arm A, 544 sites × 2 conditions | **70 s** |
| extinction, 120 sites × 7 rungs | **58 s** |
| paraphrase, 360 scorings | included above |

**Arm A is forward-only and cheap.** The full planned sweep (5 model families
× base/instruct × 9 lexicons × 2 families) is single-digit A100-hours. Do not
ration it.

**Extinction is the expensive arm** — context grows with the ladder. A 0.5B
model OOMed at the 32-shot rung on 16 GB. Budget by (sites × top rung), not by
parameter count, and prefer many short jobs to one long one.

## Run order on Sol

1. `sol/prefetch_models.py --tier small` on a **login** node; commit
   `outputs/model_pins.json`.
2. `sbatch sol/arm_a.slurm` — **development cells only** (`dom`, δ25/δ50,
   seeds s1/s2, ≤1.5B).
3. `sbatch sol/primary.slurm` — extinction on the same development cells.
4. Analyse with `analysis.cluster_bootstrap`. **Decide H4's score and
   threshold here, and freeze them.**
5. Only then touch held-out: all of `blk`, all of δ75, seed s3, >1.5B.
6. Scale to a second tokenizer family (DeepSeek-Coder, StarCoder2) — this
   matters more than more Qwen sizes, because the P32-001 merge behaviour is a
   property of the tokenizer and `k_common` will differ.

## The gate

> **Do not scale beyond 3B until the effect is present in `blk` with an
> interval excluding the null.**

Current status of that gate: reversion in `blk` is 0.423–0.456 with intervals
excluding 0.5 at the low end but **not excluding "no effect"** in the sense
that matters for H4 — because H4 is about *prediction*, and the predictor has
not been run on real scores yet. The gate is **not yet passed**; step 4 above
is what passes or fails it.
