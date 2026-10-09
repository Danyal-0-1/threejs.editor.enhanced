# 00 — Complete results of the held-out run

> **Run:** `heldout-20261007a`, analysed by the frozen code of `dev-20261006a`.
>
> **Dates:** unlocked 2026-10-07 23:05 MST; GPU work finished 2026-10-09 10:15; exported 11:20.
>
> **Status:**
>
> - Every experiment is **COMPLETE**: 0 missing, 0 failed and 0 corrupt cells.
> - `validate` passed: VALID.
> - The local copy (`phase3_3/sol_results/heldout-20261007a/`) is byte-identical to Sol on
>   the merged data, the H4 table and the hypothesis report.
>
> **How to read it:**
>
> - **Confirmatory** = registered before the freeze and tested once here: H4 C1/C2, the `k*`
>   endpoint and the H5 direction.
> - **D11** = specified after the freeze but before any held-out outcome was seen.
> - **Exploratory** = everything else, and labelled so.
> - Two gaps in the frozen analysis are disclosed in §13.

| doc | for |
|---|---|
| **00 (this file)** | every result, in tables |
| [01 theory](01_theory.md) | what each result means, concept by concept |
| [02 math](02_mathematics_and_statistics.md) | how each number is computed, with real worked examples |
| [03 code and pipeline](03_code_and_pipeline.md) | how the run was executed, stage by stage, with real dumps |
| [04 retyping plan](04_retyping_plan.md) | which analysis code to retype to understand the results |
| [05 mental image](05_mental_image.md) | the whole result as one picture |
| [06 publishability and paper](06_publishability_and_paper.md) | what is publishable and how to structure the paper |
| [07 knowledge check](07_knowledge_check.md) | questions, no answers |
| [08 issues and superseded numbers](08_issues_and_superseded_numbers.md) | defects found, and numbers that changed |
| [09 conclusions, claim strength and venues](09_conclusions_claim_strength_and_venues.md) | the best conclusion, how strong each claim is, three exploratory checks, where to submit |
| [10 the human mirror](10_humans_and_the_brain.md) | the results as human behaviour, and the brain systems involved |

The method is explained in [`../sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md`](../sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md).

**Figures.** The publication figures and their tables are in
`phase3_3/sol_results/heldout-20261007a/analysis_addenda/paper_figures/`; open `CAPTIONS.md`
there first. Each figure maps to a section below:

| figure | section | shows |
|---|---|---|
| `fig2_h4` | §3 | AUROC per pair, with the role-level and length baselines |
| `fig3_reversion` | §4–5 | reversion with and without the table, and the length-matched control |
| `fig4_scale` | §7 | reversion and AUROC against size; the ladder intervals equal D11's |
| `fig5_adaptation` | §6 | Kaplan–Meier curves, medians per checkpoint, first against lasting switch |
| `fig6_generation` | §8 | reach and reversion given reach, with intervals; by role |
| `fig7_repair` | §9 | the H5 metric per model; what happens at the repaired sites |
| `figA1`–`figA4` | §3, §10, §11 | calibration (frozen pairs only), prompt wording, roles, margin distributions |

Wherever the figure script recomputes a number that the frozen export also reports, it refuses
unless the two agree (eight checks, listed in its `PROVENANCE.md`). The figure intervals are new
descriptive statistics; for the Qwen2.5-Coder ladder they equal the D11 intervals exactly.

---

## 1. What ran

**Models: 21**

- Qwen2.5-Coder at 0.5B, 1.5B, 3B, 7B, 14B and 32B;
- DeepSeek-Coder at 1.3B and 33B;
- Llama-3.2-1B;
- StarCoder2-3B (base only);
- Qwen2.5-72B, on two GPUs.

All are base + instruct pairs except StarCoder2.

**Cells:** 2 grammar families (`dom`, `blk`) × 5 held-out lexicons (`d25s3`, `d50s3`,
`d75s1a`, `d75s2a`, `d75s3a`) gives **210 cells**. By class:

- 105 HELDOUT-WEAK-FAMILY (`blk`, deviation D1);
- 75 HELDOUT model;
- 20 HELDOUT mapping;
- 10 HELDOUT-WEAKENED (3B, deviation D2).

**Sites:** 1,515 per model and family; 3,030 in all. 1,670 duplicates were dropped within
cells. Per lexicon: `d25s3` 220, `d50s3` 272, each `d75` 341.

| experiment | rows | cells | what |
|---|---:|---:|---|
| Arm A | 190,890 | 3,402 | margin at every site, with the table (`rule`), without it (`norule`), and a length-matched control |
| extinction (primary) | 84,000 | 840 | 400 sites per model × 7 ladder rungs (0–32 examples) + 3 prompt paraphrases |
| Arm B | 7,800 generations | 200 | 10 instruct models write programs from natural-language requests |
| H5 | 212,100 | 3,780 | 10 instruct models, scored again under 7 repaired lexicons per cell |

**Measurement health:**

- 190,890 of 190,890 Arm A rows scored;
- 0 exact-zero margins and 0 ties;
- at 43.7% of sites the candidate's first characters merge into the prompt's last token when
  tokenized ("merged"). Scoring from the first divergent token handles this;
- every demonstration is leak-free by construction.

**Compute:** 40.8 A100 GPU-hours.

- held-out evaluation: 7.5 h on 1 GPU + 3.6 h × 2 GPUs;
- Arm B: 8.4 h + 3.5 h × 2;
- H5: 5.7 h + 2.6 h × 2.

Details are in [03](03_code_and_pipeline.md).

---

## 2. The verdicts in one table

| question | registered criterion | result | status |
|---|---|---|---|
| **H4**: does the base model's margin predict where the instruct model reverts? | C1: AUROC − identity ≥ 0.10, CI > 0; C2: AUROC − length ≥ 0.05, CI > 0; Holm; each family separately | AUROC 0.76–0.96; C1 deltas +0.26…+0.46; C2 deltas +0.14…+0.49; all CIs > 0; Holm p = 0.001 | **MET in 20/20** (10 pairs × 2 families) |
| H4 C3: AUROC ≥ 0.65 on a held-out *grammar* | — | `blk` AUROCs are 0.76–0.95, but `blk` was seen in development | **NOT TESTABLE** (D1) |
| H4 refutation clause: separates lexicons but not sites | within-lexicon AUROC | 0.758–0.963, as high as overall | **not triggered** |
| **Primary endpoint `k*`**: how many examples to switch | KM median with censoring | median 1.4–4.6 examples (`dom`), 3.3–11.6 (`blk`); 6–29% censored | **estimated** |
| **H5**: targeted repair beats random per changed symbol | interval excluding 0; control sites worsen ≤ 0.02 | targeted beats the mean of random in **43/100** cells; mean difference **−0.41** per symbol | **NOT SUPPORTED** (descriptive; the interval test was never implemented, §13) |
| H2: prior × context | — | — | **NOT TESTABLE** |
| **D11**: scale trend within Qwen2.5-Coder (0.5–32B) | slope on log₁₀ size; bootstrap; Holm | reversion: no trend. H4 AUROC: −0.081 per 10× in `dom` (Holm p < 0.003) | reported |
| Arm B (generation) | descriptive hurdle | reach 13.5%; reversion given reach 19.8%; task accuracy 9.6% | reported |

---

## 3. H4: the base model predicts where its instruct twin reverts

Columns:

- **AUROC**: the chance the base model's risk ranks a reverting site above a correct one.
- **AP**: average precision. **prev**: the share of reverting sites.
- **Δ id / Δ len**: the C1 and C2 differences, with 95% template-bootstrap intervals.
- **Δ role**: the difference from the exploratory role-level baseline `terminal_rate`.

**`dom` (HELDOUT mapping):**

| pair | AUROC | AP | prev | within-lex | Δ id (C1) | Δ len (C2) | Δ role |
|---|---:|---:|---:|---:|---|---|---|
| Qwen2.5-Coder-0.5B | 0.888 | 0.868 | 0.445 | 0.890 | +0.388 [0.361, 0.412] | +0.297 [0.250, 0.340] | +0.033 [−0.012, 0.072] |
| Qwen2.5-Coder-1.5B | 0.963 | 0.953 | 0.462 | 0.963 | +0.463 [0.447, 0.475] | +0.493 [0.456, 0.534] | +0.216 [0.166, 0.265] |
| Qwen2.5-Coder-3B ᵂ | 0.949 | 0.948 | 0.475 | 0.950 | +0.449 [0.432, 0.464] | +0.413 [0.368, 0.459] | +0.289 [0.235, 0.343] |
| Qwen2.5-Coder-7B | 0.760 | 0.762 | 0.519 | 0.759 | +0.260 [0.218, 0.301] | +0.293 [0.236, 0.347] | +0.048 [−0.020, 0.114] |
| Qwen2.5-Coder-14B | 0.852 | 0.819 | 0.459 | 0.850 | +0.352 [0.320, 0.383] | +0.369 [0.319, 0.420] | +0.136 [0.087, 0.184] |
| Qwen2.5-Coder-32B | 0.786 | 0.718 | 0.400 | 0.787 | +0.286 [0.243, 0.325] | +0.331 [0.272, 0.394] | +0.184 [0.122, 0.245] |
| Qwen2.5-72B | 0.854 | 0.828 | 0.477 | 0.852 | +0.354 [0.322, 0.384] | +0.366 [0.320, 0.411] | +0.195 [0.150, 0.237] |
| DeepSeek-Coder-1.3B | 0.841 | 0.823 | 0.498 | 0.835 | +0.341 [0.310, 0.370] | +0.303 [0.257, 0.348] | +0.176 [0.119, 0.234] |
| DeepSeek-Coder-33B | 0.926 | 0.932 | 0.523 | 0.926 | +0.426 [0.403, 0.448] | +0.412 [0.371, 0.456] | +0.227 [0.161, 0.296] |
| Llama-3.2-1B | 0.893 | 0.883 | 0.481 | 0.891 | +0.393 [0.364, 0.417] | +0.414 [0.377, 0.450] | +0.137 [0.101, 0.171] |

ᵂ HELDOUT-WEAKENED: 3B was observed before the freeze (D2).

**`blk` (HELDOUT-WEAK-FAMILY):**

| pair | AUROC | AP | prev | within-lex | Δ id (C1) | Δ len (C2) | Δ role |
|---|---:|---:|---:|---:|---|---|---|
| Qwen2.5-Coder-0.5B | 0.836 | 0.809 | 0.441 | 0.841 | +0.336 [0.299, 0.369] | +0.267 [0.207, 0.323] | +0.050 [−0.001, 0.093] |
| Qwen2.5-Coder-1.5B | 0.920 | 0.920 | 0.521 | 0.919 | +0.420 [0.400, 0.438] | +0.426 [0.383, 0.468] | +0.278 [0.223, 0.331] |
| Qwen2.5-Coder-3B | 0.939 | 0.940 | 0.490 | 0.941 | +0.439 [0.421, 0.456] | +0.406 [0.359, 0.454] | +0.277 [0.225, 0.327] |
| Qwen2.5-Coder-7B | 0.759 | 0.728 | 0.481 | 0.758 | +0.259 [0.213, 0.303] | +0.267 [0.207, 0.325] | +0.050 [−0.022, 0.122] |
| Qwen2.5-Coder-14B | 0.875 | 0.853 | 0.436 | 0.876 | +0.375 [0.344, 0.403] | +0.387 [0.340, 0.435] | +0.223 [0.183, 0.263] |
| Qwen2.5-Coder-32B | 0.805 | 0.766 | 0.454 | 0.807 | +0.305 [0.259, 0.347] | +0.409 [0.345, 0.468] | +0.148 [0.080, 0.213] |
| Qwen2.5-72B | 0.866 | 0.839 | 0.448 | 0.862 | +0.366 [0.338, 0.393] | +0.425 [0.376, 0.473] | +0.195 [0.157, 0.228] |
| DeepSeek-Coder-1.3B | 0.788 | 0.806 | 0.529 | 0.787 | +0.288 [0.246, 0.331] | +0.136 [0.092, 0.187] | +0.083 [0.037, 0.127] |
| DeepSeek-Coder-33B | 0.946 | 0.947 | 0.506 | 0.947 | +0.446 [0.432, 0.460] | +0.369 [0.326, 0.411] | +0.321 [0.252, 0.388] |
| Llama-3.2-1B | 0.840 | 0.841 | 0.500 | 0.836 | +0.340 [0.310, 0.366] | +0.304 [0.253, 0.351] | +0.172 [0.123, 0.221] |

**Baselines (AUROC across the 20 pair × family groups):**

| baseline | AUROC |
|---|---|
| identity | exactly 0.500 (constant, D6) |
| length | 0.396–0.651 |
| token count | 0.410–0.527 |
| program NLL | 0.475–0.545 |
| role-level `terminal_rate` | 0.602–0.856 |

**What it means.** The site-specific risk beats every baseline. It beats even the role-level
one in 20/20 point estimates and 16/20 intervals; the exceptions are 0.5B and 7B. The
prediction is about the exact place, not just about which symbol is hard.

**Calibration.**

- **Frozen transfer, the 0.5B and 1.5B pairs only.** ECE was 0.036–0.052, with calibration
  slopes of 0.83–1.18: the development calibration transferred to new mappings and to `blk`.
- **The other 8 pairs have no frozen calibration.** Their ECE (0.017–0.111) and Brier
  (0.089–0.194) were fitted on the held-out rows themselves, so they are in-sample (§13).

---

## 4. Reversion: how often the old spelling wins

Each cell gives the share of the 1,515 sites with M < 0, under rule / norule /
length-matched:

| model | `dom` | `blk` |
|---|---|---|
| Qwen2.5-Coder-0.5B | 0.455 / 0.517 / 0.515 | 0.438 / 0.491 / 0.490 |
| … 0.5B-Instruct | 0.445 / 0.488 / 0.492 | 0.441 / 0.493 / 0.506 |
| Qwen2.5-Coder-1.5B | 0.498 / 0.540 / 0.538 | 0.509 / 0.540 / 0.523 |
| … 1.5B-Instruct | 0.462 / 0.513 / 0.523 | 0.521 / 0.575 / 0.565 |
| Qwen2.5-Coder-3B | 0.481 / 0.539 / 0.550 | 0.508 / 0.547 / 0.562 |
| … 3B-Instruct | 0.475 / 0.510 / 0.527 | 0.490 / 0.516 / 0.512 |
| Qwen2.5-Coder-7B | 0.508 / 0.548 / 0.551 | 0.546 / 0.592 / 0.603 |
| … 7B-Instruct | **0.519 / 0.504** / 0.521 | 0.481 / 0.553 / 0.557 |
| Qwen2.5-Coder-14B | 0.465 / 0.534 / 0.533 | 0.492 / 0.568 / 0.569 |
| … 14B-Instruct | 0.459 / 0.493 / 0.488 | 0.436 / 0.525 / 0.529 |
| Qwen2.5-Coder-32B | 0.462 / 0.491 / 0.490 | 0.514 / 0.539 / 0.533 |
| … 32B-Instruct | 0.400 / 0.461 / 0.466 | 0.454 / 0.471 / 0.489 |
| Qwen2.5-72B | 0.506 / 0.546 / 0.561 | 0.489 / 0.560 / 0.563 |
| … 72B-Instruct | 0.477 / 0.522 / 0.516 | 0.448 / 0.551 / 0.562 |
| DeepSeek-Coder-1.3B | 0.557 / 0.589 / 0.578 | 0.541 / 0.567 / 0.568 |
| … 1.3B-Instruct | 0.498 / 0.574 / 0.579 | 0.529 / 0.575 / 0.573 |
| DeepSeek-Coder-33B | 0.506 / 0.622 / 0.628 | 0.535 / 0.636 / 0.644 |
| … 33B-Instruct | 0.523 / 0.610 / 0.627 | 0.506 / 0.591 / 0.594 |
| Llama-3.2-1B | 0.467 / 0.525 / 0.521 | 0.512 / 0.554 / 0.552 |
| … 1B-Instruct | 0.481 / 0.509 / 0.496 | 0.500 / 0.568 / 0.560 |
| StarCoder2-3B | 0.479 / 0.579 / 0.595 | 0.558 / 0.655 / 0.648 |
| **mean** | **0.482 / 0.534 / 0.538** | **0.498 / 0.556 / 0.557** |

**What it means.**

- With the table, every model reverts on **40–56%** of sites.
- Without it, the rate is 46–66%. The table lowers reversion by about **5–6 percentage points
  on average**.
- One exception: Qwen2.5-Coder-7B-Instruct on `dom` (0.519 with the table, 0.504 without).

---

## 5. The rule effect: how much the table moves the margin

**Mean of M(rule) − M(control), in nats, over the 5 lexicons:**

| | min–max across models | mean | model × lexicon intervals > 0 | < 0 |
|---|---|---|---|---|
| `dom` vs norule | +0.198 … +0.465 | +0.340 | 59 / 105 | 0 |
| `dom` vs length-matched | +0.198 … +0.476 | +0.353 | 63 / 105 | 0 |
| `blk` vs norule | +0.162 … +0.597 | +0.376 | 70 / 105 | 0 |
| `blk` vs length-matched | +0.183 … +0.624 | +0.380 | 71 / 105 | 0 |

**Instruct models use the table more than their base model** (`blk`, vs norule):

- 14B: +0.60 vs +0.44;
- 32B: +0.58 vs +0.22;
- 72B: +0.53 vs +0.44.

The full per-model list is in `analysis_addenda/summary/HELDOUT_SUMMARY.txt`.

**What it means.**

- The table *always* helps on average, and the length control confirms it is the
  information, not the extra length.
- But a shift of about 0.35 nats multiplies the odds by only e^0.35 ≈ 1.4. That is too
  little to flip most sites, which is why reversion falls by only 5–6 points.

---

## 6. Adaptation: how many worked examples until the model switches

**Kaplan–Meier median `k*`** for sites wrong with 0 examples. Each cell gives the median
[95% template bootstrap], the share censored (never switched within 32) and n:

| model | `dom` | `blk` |
|---|---|---|
| Qwen2.5-Coder-0.5B | 2.58 [1.25, 6.46], 12%, 104 | 4.97 [1.85, 11.72], 20%, 114 |
| … 0.5B-Instruct | 4.60 [1.58, 12.75], 12%, 88 | 9.10 [3.70, 12.14], 21%, 102 |
| Qwen2.5-Coder-1.5B | 3.08 [1.42, 18.73], 27%, 100 | 5.19 [2.67, 11.68], 26%, 110 |
| … 1.5B-Instruct | 3.81 [1.23, 6.54], 16%, 87 | 9.25 [3.88, 13.37], 26%, 103 |
| Qwen2.5-Coder-3B | 3.33 [1.23, 14.79], 27%, 99 | 11.64 [3.00, 18.28], 28%, 107 |
| … 3B-Instruct | 3.19 [1.25, 8.78], 28%, 99 | 7.14 [3.11, 16.33], 29%, 112 |
| Qwen2.5-Coder-7B | 2.67 [1.59, 7.05], 19%, 103 | 11.04 [5.86, 18.64], 23%, 104 |
| … 7B-Instruct | 2.12 [1.27, 5.48], 13%, 115 | 10.53 [5.35, 18.49], 26%, 105 |
| Qwen2.5-Coder-14B | 1.63 [0.99, 3.08], 8%, 91 | 3.86 [1.85, 10.10], 13%, 101 |
| … 14B-Instruct | 3.21 [2.48, 5.99], 14%, 111 | 6.28 [1.96, 10.29], 15%, 102 |
| Qwen2.5-Coder-32B | **1.36** [1.04, 2.66], 13%, 95 | 3.75 [2.29, 8.11], 12%, 107 |
| … 32B-Instruct | 1.78 [1.23, 3.97], 21%, 86 | 3.61 [1.75, 9.93], 20%, 86 |
| Qwen2.5-72B | 3.35 [1.92, 6.30], 19%, 83 | 8.43 [3.23, 11.69], 25%, 93 |
| … 72B-Instruct | 4.20 [2.08, 6.92], 24%, 89 | 11.22 [7.23, 19.06], 29%, 97 |
| DeepSeek-Coder-1.3B | 3.27 [1.87, 6.26], 14%, 106 | 5.54 [1.75, 12.67], 21%, 99 |
| … 1.3B-Instruct | 3.62 [1.77, 7.12], 15%, 104 | 5.91 [3.17, 11.99], 18%, 109 |
| DeepSeek-Coder-33B | 1.94 [1.46, 3.05], 10%, 92 | **3.33** [1.88, 10.90], 12%, 92 |
| … 33B-Instruct | 3.08 [1.88, 4.75], 13%, 98 | 3.47 [1.97, 6.81], 12%, 98 |
| Llama-3.2-1B | 1.49 [0.96, 3.63], 9%, 114 | 6.86 [2.17, 11.41], 20%, 126 |
| … 1B-Instruct | 1.57 [0.87, 3.02], 6%, 102 | 3.58 [1.39, 13.29], 18%, 102 |
| StarCoder2-3B | 2.40 [1.25, 4.76], 19%, 109 | 6.38 [2.46, 14.64], 18%, 109 |

**Across all 21 models (8,400 site-model ladders):**

| | value |
|---|---|
| wrong at 0 examples | 4,253 (50.6%) |
| never switched within 32 (censored) | 784 of those (18.4%) |
| first switch (crossers) | 3,469; median `k*` = **2.06** |
| switch that holds through 32 examples | 2,912; median rung where it starts holding (`sustained_k`) = **8** |
| wobbly curves (non-monotone), per model × family | 92.8–99.5% |
| curves that cross back below zero | 28.8–53.3% |
| already correct at 0 examples | 38.5–58.0% |

**What it means.**

- **Fast, then unstable.** A model first prefers the new spelling after about **2** examples,
  but needs about **8** before the preference *stays*.
- **Grammar matters.** The familiar `dom` grammar adapts 2–4× faster than the unfamiliar
  `blk`.
- **Some sites never adapt.** 1 in 5 initially-wrong sites never switches within 32
  examples.

---

## 7. Scale: D11, within the Qwen2.5-Coder ladder from 0.5B to 32B

**Slope per 10× parameters** (OLS on log₁₀ size; template bootstrap, B = 2000; Holm over 6):

| family | outcome | models | slope | 95% CI | p | Holm p |
|---|---|---|---:|---|---:|---:|
| `blk` | reversion | base | +0.033 | [+0.005, +0.060] | 0.018 | 0.072 |
| `blk` | reversion | instruct | −0.013 | [−0.044, +0.017] | 0.391 | 1.000 |
| `blk` | H4 AUROC | pair | −0.037 | [−0.066, −0.009] | 0.011 | 0.055 |
| `dom` | reversion | base | −0.001 | [−0.026, +0.023] | 0.962 | 1.000 |
| `dom` | reversion | instruct | −0.014 | [−0.044, +0.017] | 0.361 | 1.000 |
| `dom` | H4 AUROC | pair | **−0.081** | [−0.111, −0.050] | < 0.0005 | **< 0.003** |

**What it means.**

- **Reversion does not shrink with size.** No slope survives Holm. The 32B model reverts as
  often as the 0.5B.
- **Predictability declines in `dom`.** The base model's margin predicts its instruct twin
  less well as models grow, but it is still at least 0.76.
- **Associations, not causes.** Sizes were not randomized.

---

## 8. Arm B: real code generation (instruct models; table + 4 examples in the prompt)

**Pooled over lexicons:**

| model | family | reach | reversion given reach | correct programs | parse failures |
|---|---|---|---|---|---|
| Qwen2.5-Coder-0.5B-I | `dom` / `blk` | 2.9% / 3.0% | 22.7% / 17.4% | 7 / 10 of 390 | 208 / 273 |
| Qwen2.5-Coder-1.5B-I | | 6.5% / 7.4% | 26.5% / 21.4% | 14 / 19 | 213 / 219 |
| Qwen2.5-Coder-3B-I | | 14.4% / 12.5% | 21.1% / 23.7% | 36 / 34 | 135 / 161 |
| Qwen2.5-Coder-7B-I | | 14.6% / 12.1% | 19.0% / 22.3% | 37 / 35 | 102 / 109 |
| Qwen2.5-Coder-14B-I | | 20.5% / 19.4% | 21.2% / 20.4% | 57 / 62 | 48 / 115 |
| Qwen2.5-Coder-32B-I | | 23.4% / 17.4% | 19.4% / 22.1% | 60 / 58 | 86 / 137 |
| Qwen2.5-72B-I | | **32.8% / 27.7%** | **14.9% / 16.9%** | **107** / 65 | 51 / 177 |
| DeepSeek-Coder-1.3B-I | | 7.3% / 5.5% | 24.3% / 16.7% | 20 / 19 | 154 / 193 |
| DeepSeek-Coder-33B-I | | 17.7% / 16.5% | 16.8% / 22.0% | 49 / 45 | 65 / 112 |
| Llama-3.2-1B-I | | 4.5% / 4.6% | 23.5% / 21.4% | 8 / 5 | 171 / 277 |
| **all** | | **13.5%** (4,104 / 30,300) | **19.8%** (812) | **747 / 7,800 (9.6%)** | 3,006 (38.5%) |

**Reversion given reach, by role:**

| role | `dom` | `blk` |
|---|---|---|
| sigil | 11.3% | 9.0% |
| keyword | 23.2% | 17.6% |
| **verb** | **29.4%** | **42.8%** |

**What it means.**

- **Exact replay is hard.** "Reach" requires the generated program to match the target
  exactly up to the decision point, so it is a strict filter.
- **When models do reach the site, about 1 in 5 writes the old spelling,** even with 4
  examples in the prompt.
- **Verbs revert most,** the same ordering as in the extinction curves (§11). Two
  independent methods agree.

---

## 9. H5: repairing risky spellings

- **The arms.** Each cell is one instruct model × family × lexicon; there are 100. In each, 3
  roles were respelled using the targeted choice (the highest base-model risk), 3 random
  seeds' worth of random choices, or all remapped roles (global).
- **Proof.** All 35 repairs were proven meaning-preserving on 284 programs.

| | value |
|---|---|
| targeted > mean of 5 random arms | **43 of 100 cells**; mean difference **−0.41** reversions per changed symbol |
| per model, targeted − random (wins / 10) | 0.5B-I +1.45 (8), 1.5B-I −1.01 (4), 3B-I −2.99 (2), 7B-I −1.40 (3), 14B-I −1.71 (1), 32B-I −0.42 (3), 72B-I −1.80 (4), DS-1.3B-I −0.37 (4), DS-33B-I +1.20 (6), Llama-1B-I +2.99 (8) |
| targeted arm: control sites within the 0.02 tolerance | 87 / 100 cells; worst +0.175 (DS-33B-I) |
| repaired sites, targeted arms | reversions 2,963 → 2,804; still silent afterwards: 2,672 |
| repaired sites, random arms | 13,195 → 14,649; silent afterwards 13,158 |
| repaired sites, **global** arms | **14,459 → 4,696; silent afterwards 0** |

**What it means.**

- **H5 fails.** Choosing the riskiest roles does not beat random choice.
- **Why.** These lexicons *permute* familiar spellings, so the old spelling of a repaired role
  usually still means another role. A partial repair therefore leaves the error silent.
- **Only renaming everything works.** Moving every reassigned role to an unfamiliar alphabet
  removes all silent errors and two-thirds of the reversions at repaired sites.
- **The metric is confounded.** Much of the "per-symbol" change happens at *control* sites,
  because changing the table changes the whole prompt. See the worked example in
  [02 §6](02_mathematics_and_statistics.md).

---

## 10. Robustness and quality control

- **Prompt wording.** Three paraphrases of the rule prompt change reversion by 0.010–0.132
  (median 0.046); 5 of 42 model × family groups exceed 0.08.
- **Measurement.** Arm A had no exclusions, no ties and no exact zeros, and no cell failed in
  any experiment.

---

## 11. Exploratory cuts (not preregistered)

**Kaplan–Meier median examples to switch, pooled over models:**

| cut | `dom` | `blk` |
|---|---|---|
| sigils | 1.28 (2% censored) | 3.21 (10%) |
| keywords | 2.85 (13%) | 9.02 (17%) |
| **verbs** | **6.57 (34%)** | **11.36 (35%)** |
| 25% of symbols respelled | 5.40 (18%) | 10.19 (27%) |
| 50% respelled | 1.57 (12%) | 5.80 (19%) |
| 75% respelled | 2.15 (17%) | 6.19 (19%) |
| base / instruct | 2.37 / 3.04 | 5.78 / 7.23 |

**What it suggests.**

- **Words are stickier than punctuation.** This matches Arm B's role ordering.
- **A *partly* changed language is harder to adopt than a heavily changed one.**
- **Instruct models adapt a little more slowly.**
- **Caveat.** The density levels rest on one lexicon (`d25s3`), one (`d50s3`) and three (`d75*`),
  so lexicon and density are confounded. These are hypotheses for a follow-up study.

---

## 12. Development vs held-out: did it replicate?

| | development (4 models, `dom`) | held-out |
|---|---|---|
| H4 AUROC, 0.5B pair | 0.869 | 0.888 (`dom`), 0.836 (`blk`) |
| H4 AUROC, 1.5B pair | 0.935 | 0.963 (`dom`), 0.920 (`blk`) |
| reversion with the table | 0.39–0.58 | 0.40–0.56 |
| rule effect | +0.08…+0.36; 1/32 intervals > 0 | +0.16…+0.62; 263/420 intervals > 0 |
| KM median `k*` | 3.6–6.2 | 1.4–4.6 (`dom`), 3.3–11.6 (`blk`) |

**What it means.**

- **H4 replicated and slightly strengthened** on new mappings.
- **The rule effect became clearly detectable.** Held-out cells are larger, and `d75`
  lexicons change more symbols. The development power analysis (0.25) was conservative for
  these effect sizes.

---

## 13. Gaps in the frozen analysis (disclosed, not corrected post hoc)

1. **H4 calibration labels.** For the 8 pairs without frozen Platt parameters (everything
   but 0.5B and 1.5B), the frozen export does two things wrong:
   - **The probability.** It writes `calibrated_p = σ(risk)`, i.e. uncalibrated, but labels
     it `DEV_FREEZE`.
   - **The calibration metrics.** It computes ECE, Brier and the calibration slope after
     fitting a calibration on the held-out rows themselves, so the slope is exactly 1.00.
   - **Unaffected:** AUROC, AP, the C1/C2 criteria and every other rank-based number.
   - **The only genuine calibration-transfer claims are for the 0.5B and 1.5B pairs.**
2. **The H5 interval test was never implemented.** The frozen export lists each arm's
   per-symbol reduction but not the registered test (targeted − random with an interval). The
   descriptive result (43/100 cells; mean −0.41) already contradicts H5. No post-hoc test is
   offered as confirmatory.
3. **The D10 scale analysis** was likewise missing from the frozen code. It was specified
   (D11) and approved before outcomes were examined, and was run after the export.

All three are recorded in [08](08_issues_and_superseded_numbers.md) and in deviation D12 of
`phase3_2/PREREGISTRATION.md`.

---

## 14. Where every number lives

All paths are under `phase3_3/sol_results/heldout-20261007a/`. Everything is in git; after
cloning, run `bash phase3_3/sol_results/restore_large_files.sh heldout-20261007a` once to
restore the four files stored gzipped (`csv/arm_a_long.csv` and three `merged/*.jsonl`):

| what | file |
|---|---|
| H4 metrics, baselines, deltas, criteria | `csv/h4_metrics_baselines_calibration.csv` |
| H4 per-site predictions | `csv/h4_predictions.csv` |
| reversion and rule effect per cell | `csv/rule_effect.csv`; all rows in `csv/arm_a_long.csv` |
| extinction curves and KM | `csv/extinction_rung_long.csv`, `csv/kstar_survival.csv` |
| Arm B | `csv/arm_b_hurdle.csv`, `csv/arm_b_generations.csv` (every generated program) |
| H5 | `csv/h5_budget_outcomes.csv`, `csv/h5_ir_proof.csv` |
| official reports | `reports/HYPOTHESIS_RESULTS.md`, `HELDOUT_RESULTS.md`, `QUALITY_CONTROL.md`, `RUN_SUMMARY.md` |
| **paper figures and tables** | `analysis_addenda/paper_figures/`: 10 figures (PDF, SVG, PNG), 16 tables, `CAPTIONS.md`, `PROVENANCE.md` |
| diagnostic figures (frozen, not for the paper) | `plots/*.png` and `*.svg` (12 figures) |
| D11 | `analysis_addenda/d11_scale/SCALE_ANALYSIS.md` |
| summary and exploratory | `analysis_addenda/summary/HELDOUT_SUMMARY.txt`, `analysis_addenda/exploratory/` (`EXPLORATORY_CHECKS.md`: inheritance, role ordering, adaptation cuts, wobble size) |
| unlock provenance | `HELDOUT_UNLOCK.json`, `UNLOCK_NOTE.md` |
