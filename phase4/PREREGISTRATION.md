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
- the 21 models listed in `phase4/code/p4/governance/splits.py` (`DEV_MODELS`);
- since 2026-10-23, nine served models, scored on Phase 3.3's held-out cells in the development run
  `dev-20261023a` (§9). They are development models too.

**Held out: to be registered.** Options include:

- new lexicons, with new seeds or densities, made with `phase4/code/tools/build_materials.py`;
- a new grammar family;
- models Phase 3.3 never scored: the 9 unscored local models in
  `phase4/code/p4/governance/registry.py`, and the 36 served by the ASU RC API (`asu-rc/...`,
  18 of them above the 72B ceiling; §9).

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

**Already used (2026-10-23), so not held-out candidates:** OLMo 3 7B Instruct, OLMo 3 32B Instruct
and Think, Qwen3-Coder 30B-A3B Instruct, Gemma 4 31B, DeepSeek-V4.1-Flash, and Qwen3.5 27B, 122B
and 397B, in the development run `dev-20261023a` (exploratory; results in
`explanations/phase4/api_models_results_explained/`). For that run `MAX_SIZE_B` was set to 600
(total parameters), so that DeepSeek (about 550B) was allowed. A confirmatory test with these nine
needs held-out material: new lexicons or a new grammar family.

_The rest is to be decided._ The facts, from the probe of 2026-10-22
(`phase4/code/configs/voyager/probe_2026-10-22.md`; `phase4/code/VOYAGER.md`, §2):

- 36 text models serve Arm A and Arm B by Phase 3.3's protocol. All are in the registry as
  `asu-rc/<name>`.
- None is a base model, so none can enter H4 or H5.
- 33 of the 36 round their logits: their margins come in steps of 1/8 to 1/32 nats. beam-1-0,
  deepseek-v4-1-flash and muse-spark-open do not round.
- Many are served quantized (fp8 or mxfp4).
- 18 are above the 72B ceiling, and most of those are mixtures of experts.
- There is no revision. The pin is the deployment that answered, so a redeployment ends a run.

**Decisions to write here:**

1. **Which models, in which role:** development or held-out.
2. **The size ceiling:** whether to raise `MAX_SIZE_B`, and whether a mixture of experts counts
   its total or its active parameters.
3. **Rounding:** how a tie, or a margin within one rounding step of zero, is counted; or whether
   only the models that do not round are used for Arm A.
4. **A bridge:** one open-weights model scored both on Sol (fp32 head) and through the API, on
   development cells. That measures how often the API's rounding flips a sign. OLMo 3 and Qwen3
   are served, and their weights are public.
5. **Contamination:** this repository is public, and it holds the materials. A model trained on
   data collected after they were pushed could have seen them. Record each model's published
   training cutoff where there is one.

## Deviations

*(append below once registered; do not edit anything above)*

- none yet
