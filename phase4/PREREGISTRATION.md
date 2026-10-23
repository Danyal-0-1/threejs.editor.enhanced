# Phase 4 — preregistration

**Status: DRAFT — not registered.** The pipeline's freeze (`phase4/code/p4/governance/freeze.py`)
refuses to freeze a development run while this line is here.

**To register:**

1. Write every section below.
2. Write the held-out set of §2 into `phase4/code/p4/governance/splits.py`, in the same commit.
3. Replace the status line with `**Status: REGISTERED on <date>**` and commit.

From then on, nothing above "Deviations" changes. Every later change is an appended, dated
deviation with its reason and scientific consequence, as in Phase 3.2's preregistration.

**What this file is.** Phase 4's pipeline (`phase4/code/`) reads this file:

- it is pointed to by `phase4/code/p4/paths.py` (`PREREGISTRATION`);
- its hash goes into every freeze;
- its Deviations section goes into every run's `DEVIATIONS.md` report.

Phase 3.3 ran under `phase3_2/PREREGISTRATION.md` (frozen 2026-10-02, deviations D1–D13). That
file stays as it is.

---

## 1. Hypotheses

_To be written._ Each hypothesis states its prediction and its direction. The candidate studies
are in [`README.md`](README.md):

- H5 again, with a repaired-site metric and frequency-aware targeting;
- a second language, or natural respellings;
- models served by the ASU RC API in free generation (Arm B), and in Arm A where their API
  returns prompt log-probabilities;
- the spelling-risk linter;
- a human comparison.

## 2. Splits

**Already seen, so they cannot be held out.** Phase 3.3 scored all of the following, its held-out
material included, and its results have been read:

- both grammar families (`dom`, `blk`);
- the nine lexicons `d25s1`, `d25s2`, `d50s1`, `d50s2`, `d25s3`, `d50s3`, `d75s1a`, `d75s2a`,
  `d75s3a`;
- the 21 models listed in `phase4/code/p4/governance/splits.py` (`DEV_MODELS`).

**Held out: to be registered.** Options include:

- new lexicons, with new seeds or densities, made with `phase4/code/tools/build_materials.py`;
- a new grammar family;
- models Phase 3.3 never scored: the 9 unscored models in `phase4/code/p4/governance/registry.py`,
  and models served by the ASU RC API.

Until this section is written into `splits.py`, the pipeline holds nothing out, and a model
outside `DEV_MODELS` is classified held-out, so it cannot be scored in a development run.

## 3. Success criteria (numeric, declared in advance)

_To be written._

## 4. Analysis

_To be written._ Phase 3.3's defaults, for reference:

- a 95% template-cluster bootstrap, B = 2000, seed 20261002;
- Holm across a hypothesis's tests;
- grammar families never pooled.

## 5. Exclusions

_To be written._

## 6. Stopping rules

_To be written._

## 7. Power

_To be written._ Phase 3.3's development power analysis is in
`phase3_3/sol_results/dev-20261006a/reports/POWER_ANALYSIS.md`.

## 8. What is already known, and therefore NOT confirmatory

- **Phase 3.3's held-out results** ([`explanations/phase3_3/heldout_results_explained/00`](../explanations/phase3_3/heldout_results_explained/00_complete_results.md)):
  - H4 met in 20 of 20 groups;
  - reversion 40–56% with the rule table;
  - H5 not supported.
- **Phase 4 step 0's post-hoc findings** (deviation D13 of Phase 3.2's preregistration;
  [`explanations/phase4/fixes_before_phase4/01`](../explanations/phase4/fixes_before_phase4/01_phase4_step0_fixes.md)).
  In particular, at the repaired sites targeted respelling beats random (F4). That is a hypothesis
  the data suggested, so only a test on new material can confirm it.

## 9. Models served by the ASU RC API

_To be written, if used._ What each model can measure comes from the probe in
`phase4/code/configs/voyager/` (see `phase4/code/VOYAGER.md`).

A model behind the API can change without notice. So record two things:

- the `/v1/models` snapshot used;
- the date range of the requests.

## Deviations

*(append below once registered; do not edit anything above)*

- none yet
