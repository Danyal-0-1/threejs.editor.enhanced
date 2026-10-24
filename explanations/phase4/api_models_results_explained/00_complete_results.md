# 00 — Complete results of the served-model run

> **Run:** `dev-20261023a`, Phase 4's first development run, in
> [`phase4/results/dev-20261023a/`](../../../phase4/results/dev-20261023a/).
>
> **Dates:** 2026-10-23. Scoring 12:12 → 18:08 (MST), on the laptop; the models ran on
> ASU Research Computing's servers.
>
> **Status:**
>
> - **Complete:** all 1,998 cells (1,458 Arm A, 360 ladder, 180 Arm B) done; 0 missing, 0 failed,
>   0 corrupt; every row `status: ok`, `split: DEVELOPMENT`, `schema_version: p4/1`.
> - `validate`: "VALID: every expected cell is done and verified" (18:27).
> - Every exported number was checked again by the figure script, which refuses on any mismatch
>   (its checks are listed in `analysis_addenda/paper_figures/PROVENANCE.md`).
>
> **How to read it:**
>
> - **Every number for the nine served models is a development result: exploratory.** The run
>   was made while `phase4/PREREGISTRATION.md` was a draft ([01 §1](01_theory.md#1-development-evidence)).
> - **Phase 3.3's numbers beside them are its registered held-out results**, on the same cells.
> - H4 and H5 need a base model and its instruct twin; no served model has one, so neither was
>   run.

| doc | for |
|---|---|
| **00 (this file)** | every result, in tables |
| [01 theory](01_theory.md) | what is new when the model is served: pins, rounding, batching, quantization, ending the turn |
| [02 math](02_mathematics_and_statistics.md) | each number computed by hand, with real values |
| [03 code and pipeline](03_code_and_pipeline.md) | how the run was executed, stage by stage, with real dumps |
| [04 retyping plan](04_retyping_plan.md) | which new code to retype to understand the results |
| [05 mental image](05_mental_image.md) | the whole result as one picture |
| [06 the paper](06_publishability_and_paper.md) | what it adds, where it goes, how to state it |
| [07 knowledge check](07_knowledge_check.md) | questions, no answers |
| [08 issues and superseded numbers](08_issues_and_superseded_numbers.md) | what went wrong, what changed |

The method is Phase 3.3's: [`../../phase3_3/sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md`](../../phase3_3/sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md).

**Figures.** In `phase4/results/dev-20261023a/analysis_addenda/paper_figures/` (open
`CAPTIONS.md` first). Every figure names every model on its axis.

| figure | section | shows |
|---|---|---|
| `fig1_reversion` | §3 | reversion with and without the table, every model of both phases |
| `fig2_rule_effect` | §4 | what the table does to the margin, against both controls |
| `fig3_scale` | §5 | reversion against total parameters, 0.5B to about 550B |
| `fig4_adaptation` | §6 | worked examples to switch |
| `fig5_generation` | §7 | free generation: reach, and reversion given reach |
| `figA1_precision`, `figA2_retest` | §8 | ties, near-zero margins, and re-scoring |

---

## 1. What ran

**Models: 9, all served by the ASU RC LLM API** (sizes and precision from the API's listing):

| model | parameters | active | served as | deployment |
|---|---:|---:|---|---|
| OLMo 3 7B Instruct | 7B | – | not stated | `olmo3-7b-instruct@vllm-0.26.0-9c8d2749` |
| OLMo 3 32B Instruct | 32B | – | not stated | `olmo3-32b-instruct@vllm-0.26.0-e58ad632` |
| OLMo 3 32B Think | 32B | – | not stated | `olmo3-32b-think@vllm-0.26.0-c1dad0c2` |
| Qwen3-Coder 30B-A3B Instruct | 30B | 3B | bf16 | `qwen3-coder-30b-a3b-instruct@vllm-0.26.0-9d422224` |
| Qwen3.5 27B | 27B | – | fp8 | `qwen35-27b-fp8@vllm-0.26.0-5c5b7be4` |
| Qwen3.5 122B-A10B | 122B | 10B | fp8 | `qwen35-122b-a10b-fp8@vllm-0.26.0-tp4-ep-39012ab1` |
| Qwen3.5 397B-A17B | 397B | 17B | fp8 | `qwen35-397b-a17b-fp8@vllm-0.28.1rc1…-448245c1` |
| Gemma 4 31B | 31B | – | bf16 | `gemma4-31b-it@vllm-0.26.0-tp4-0e321782` |
| DeepSeek-V4.1-Flash | about 550B | not stated | mxfp4 | `deepseek-v4-1-flash@vllm-0.28.1rc1…-d26393b7` |

**Cells:** exactly those of Phase 3.3's held-out run: 2 grammar families (`dom`, `blk`) × 5
lexicons (`d25s3`, `d50s3`, `d75s1a`, `d75s2a`, `d75s3a`), every site: **1,515 sites per
grammar**, the same 3,030 for every model. 90 cells (model × family × lexicon), all
DEVELOPMENT.

| experiment | rows | cells | what |
|---|---:|---:|---|
| Arm A | 81,810 | 1,458 | the margin at every site: with the table, without it, and the length-matched control |
| ladder (primary) | 36,000 | 360 | 400 sites per model × 7 rungs (0–32 worked examples) + 3 prompt paraphrases |
| Arm B | 7,020 generations | 180 | each model writes programs from natural-language requests |
| H4, H5 | – | – | not run: no base twins |

**Measurement health:**

- Every answer came from its model's pinned deployment: 0 cells failed with `ServedModelChanged`.
- 1,294 requests were retried after a dropped connection or a server error, and every one then
  succeeded; 1,167 of them were DeepSeek-V4.1-Flash's ([03 §8](03_code_and_pipeline.md#8-the-fix-and-the-relaunch-122541)).
- 778 Arm A margins are exact ties, and re-scoring moved some margins (§8).

**Compute:** no GPU of ours. 117,810 scored pairs (three requests each) and 7,020 generations,
sent from the laptop. The whole run took 5 h 56 min, nine models side by side; DeepSeek-V4.1-Flash
took longest (Arm A 2 h 41 min, the ladder 2 h 11 min). Per-model times:
[03 §9](03_code_and_pipeline.md#9-the-slow-ones-deepseek-and-arm-b).

---

## 2. The answers in one table

| question | result | compared with Phase 3.3 |
|---|---|---|
| **Do served models revert?** | **Yes, all nine.** With the table: `dom` 0.404–0.466, `blk` 0.410–0.512 | Phase 3.3's instruct models: `dom` 0.400–0.523, `blk` 0.436–0.529 |
| **Does the table help?** | **Yes, not enough.** +0.34 to +0.86 nats against no table, interval above zero in 17 of 18 model × grammar groups; reversion falls by only 3–10 points | +0.16 to +0.60; above zero in 19 of 20 |
| **Does size help?** | **No trend.** Qwen3.5 27B → 122B → 397B: `dom` 0.404 → 0.434 → 0.424; DeepSeek-V4.1-Flash (about 550B): 0.438 | Phase 3.3 (D11): no reversion trend, 0.5–72B |
| **Instruct or thinking?** | OLMo 3 32B: Think reverts a little more (0.426 / 0.441 against 0.412 / 0.410; the intervals overlap); the table helps Instruct more (+0.80 / +0.86 against +0.49 / +0.61) | – |
| **Worked examples** | They switch served models too: median 1.7–9.4 examples (`dom`), 1.9–15.3 (`blk`); at 32 examples 19–36% of sites still revert | `dom` 1.6–4.6, `blk` 3.5–11.2; at 32 examples 17–31% |
| **Free generation (Arm B)** | Gemma 4 reaches the most sites (0.541 / 0.464) and writes the familiar spelling at only 0.038 / 0.043 of them; OLMo 3 Instruct mostly writes nothing (290 and 334 of 780 empty) | reach 0.029–0.328; familiar given reached 0.149–0.265; 0 empty |
| **Precision** | 778 ties in 81,810 margins (0.95%); re-scoring changed the sign of 39 of 2,700 margins, 34 of them Gemma 4's and Qwen3.5 122B's | Phase 3.3: 0 ties |

---

## 3. Reversion: how often the familiar spelling wins

Share of sites with M < 0, with the token table (95% template-cluster interval) and without it.
Rows are Phase 3.3's instruct models, then Phase 4's served models, on identical sites.

| phase | model | `dom` with the table | `dom` without | `blk` with the table | `blk` without |
|---|---|---|---|---|---|
| 3.3 | Qwen2.5-Coder 0.5B Instruct | 0.445 [0.412, 0.478] | 0.488 | 0.441 [0.405, 0.479] | 0.493 |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | 0.462 [0.417, 0.508] | 0.513 | 0.521 [0.469, 0.572] | 0.575 |
| 3.3 | Qwen2.5-Coder 3B Instruct | 0.475 [0.427, 0.523] | 0.510 | 0.490 [0.439, 0.539] | 0.516 |
| 3.3 | Qwen2.5-Coder 7B Instruct | 0.519 [0.473, 0.567] | 0.504 | 0.481 [0.433, 0.530] | 0.553 |
| 3.3 | Qwen2.5-Coder 14B Instruct | 0.459 [0.420, 0.498] | 0.493 | 0.436 [0.385, 0.485] | 0.525 |
| 3.3 | Qwen2.5-Coder 32B Instruct | 0.400 [0.353, 0.444] | 0.461 | 0.454 [0.403, 0.503] | 0.471 |
| 3.3 | Qwen2.5 72B Instruct | 0.477 [0.422, 0.530] | 0.522 | 0.448 [0.403, 0.496] | 0.551 |
| 3.3 | DeepSeek-Coder 1.3B Instruct | 0.498 [0.456, 0.541] | 0.574 | 0.529 [0.486, 0.573] | 0.575 |
| 3.3 | DeepSeek-Coder 33B Instruct | 0.523 [0.482, 0.564] | 0.610 | 0.506 [0.462, 0.546] | 0.591 |
| 3.3 | Llama-3.2 1B Instruct | 0.481 [0.447, 0.519] | 0.509 | 0.500 [0.464, 0.533] | 0.568 |
| 4 | OLMo 3 7B Instruct | 0.414 [0.371, 0.455] | 0.483 | 0.418 [0.375, 0.462] | 0.478 |
| 4 | OLMo 3 32B Instruct | 0.412 [0.370, 0.451] | 0.475 | 0.410 [0.363, 0.456] | 0.506 |
| 4 | OLMo 3 32B Think | 0.426 [0.379, 0.470] | 0.475 | 0.441 [0.390, 0.490] | 0.499 |
| 4 | Qwen3-Coder 30B-A3B Instruct | 0.445 [0.397, 0.489] | 0.501 | 0.463 [0.413, 0.513] | 0.560 |
| 4 | Qwen3.5 27B | 0.404 [0.368, 0.440] | 0.500 | 0.420 [0.375, 0.464] | 0.499 |
| 4 | Qwen3.5 122B-A10B | 0.434 [0.392, 0.471] | 0.500 | 0.444 [0.396, 0.488] | 0.535 |
| 4 | Qwen3.5 397B-A17B | 0.424 [0.376, 0.472] | 0.487 | 0.433 [0.387, 0.479] | 0.522 |
| 4 | Gemma 4 31B | 0.466 [0.429, 0.504] | 0.520 | 0.512 [0.477, 0.548] | 0.546 |
| 4 | DeepSeek-V4.1-Flash | 0.438 [0.403, 0.474] | 0.494 | 0.430 [0.390, 0.467] | 0.464 |

**What it shows.**

- **The habit survives in every served model.** With the full token table in the prompt, the
  nine served models prefer the familiar spelling at **40.4–46.6%** of `dom` sites and
  **41.0–51.2%** of `blk` sites. Phase 3.3's ten instruct models, on the same sites: 40.0–52.3%
  and 43.6–52.9%. The ranges overlap almost entirely.
- **The newest and largest are not better.** The lowest served rate (Qwen3.5 27B, `dom` 0.404) is
  no lower than Phase 3.3's lowest (Qwen2.5-Coder 32B, 0.400). Qwen3.5 397B and DeepSeek-V4.1-Flash
  (about 550B) sit in the middle of the range (0.42–0.44). In `blk`, three served models
  (OLMo 3 32B Instruct 0.410, OLMo 3 7B 0.418, Qwen3.5 27B 0.420) are 1.6–2.6 points below Phase
  3.3's lowest (0.436), with overlapping intervals.
- **Without the table** every served model reverts more: 46.4–56.0% (Phase 3.3: 46.1–61.0%).
- **The length-matched control** reverts within 1.6 points of no table for every served model
  (`tables/T2_reversion.csv`): it is the table's content that helps, not its length, as in
  Phase 3.3.

---

## 4. The rule effect: what the table does to the margin

Mean of M(table) − M(control), averaged over the five lexicons, nats, 95% interval.

| phase | model | `dom`: table − none | `dom`: − length-matched | `blk`: table − none | `blk`: − length-matched |
|---|---|---|---|---|---|
| 3.3 | Qwen2.5-Coder 0.5B Instruct | +0.349 [+0.154, +0.581] | +0.318 [+0.141, +0.525] | +0.437 [+0.218, +0.658] | +0.412 [+0.193, +0.623] |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | +0.394 [+0.154, +0.646] | +0.412 [+0.169, +0.663] | +0.435 [+0.220, +0.662] | +0.446 [+0.227, +0.677] |
| 3.3 | Qwen2.5-Coder 3B Instruct | +0.385 [+0.147, +0.643] | +0.384 [+0.146, +0.640] | +0.371 [+0.131, +0.617] | +0.357 [+0.119, +0.608] |
| 3.3 | Qwen2.5-Coder 7B Instruct | +0.320 [+0.092, +0.561] | +0.315 [+0.084, +0.556] | +0.451 [+0.184, +0.741] | +0.443 [+0.174, +0.734] |
| 3.3 | Qwen2.5-Coder 14B Instruct | +0.444 [+0.178, +0.731] | +0.439 [+0.168, +0.724] | +0.597 [+0.334, +0.880] | +0.557 [+0.289, +0.842] |
| 3.3 | Qwen2.5-Coder 32B Instruct | +0.461 [+0.183, +0.753] | +0.476 [+0.204, +0.779] | +0.580 [+0.307, +0.857] | +0.624 [+0.349, +0.902] |
| 3.3 | Qwen2.5 72B Instruct | +0.359 [+0.148, +0.592] | +0.353 [+0.140, +0.587] | +0.532 [+0.313, +0.753] | +0.537 [+0.316, +0.757] |
| 3.3 | DeepSeek-Coder 1.3B Instruct | +0.465 [+0.252, +0.701] | +0.445 [+0.229, +0.687] | +0.162 [-0.039, +0.375] | +0.183 [-0.022, +0.401] |
| 3.3 | DeepSeek-Coder 33B Instruct | +0.337 [+0.132, +0.554] | +0.369 [+0.167, +0.578] | +0.351 [+0.144, +0.587] | +0.390 [+0.182, +0.626] |
| 3.3 | Llama-3.2 1B Instruct | +0.294 [+0.146, +0.449] | +0.356 [+0.211, +0.517] | +0.345 [+0.136, +0.552] | +0.344 [+0.129, +0.556] |
| 4 | OLMo 3 7B Instruct | +0.845 [+0.616, +1.104] | +0.802 [+0.560, +1.076] | +0.772 [+0.493, +1.065] | +0.666 [+0.383, +0.949] |
| 4 | OLMo 3 32B Instruct | +0.798 [+0.427, +1.171] | +0.867 [+0.490, +1.246] | +0.856 [+0.495, +1.235] | +0.916 [+0.565, +1.294] |
| 4 | OLMo 3 32B Think | +0.488 [+0.223, +0.763] | +0.520 [+0.256, +0.806] | +0.612 [+0.325, +0.908] | +0.649 [+0.363, +0.943] |
| 4 | Qwen3-Coder 30B-A3B Instruct | +0.545 [+0.252, +0.867] | +0.538 [+0.235, +0.864] | +0.742 [+0.432, +1.069] | +0.767 [+0.442, +1.108] |
| 4 | Qwen3.5 27B | +0.485 [+0.276, +0.707] | +0.487 [+0.286, +0.703] | +0.433 [+0.225, +0.645] | +0.434 [+0.216, +0.648] |
| 4 | Qwen3.5 122B-A10B | +0.497 [+0.316, +0.677] | +0.464 [+0.274, +0.652] | +0.546 [+0.324, +0.781] | +0.544 [+0.322, +0.779] |
| 4 | Qwen3.5 397B-A17B | +0.422 [+0.221, +0.620] | +0.441 [+0.234, +0.648] | +0.537 [+0.327, +0.765] | +0.553 [+0.333, +0.778] |
| 4 | Gemma 4 31B | +0.665 [+0.164, +1.182] | +0.424 [-0.099, +0.976] | +0.485 [-0.026, +0.998] | +0.330 [-0.205, +0.835] |
| 4 | DeepSeek-V4.1-Flash | +0.336 [+0.161, +0.520] | +0.345 [+0.172, +0.520] | +0.452 [+0.240, +0.661] | +0.423 [+0.219, +0.639] |

**What it shows.**

- **The table helps every served model, and a little more than it helped Phase 3.3's.** Against
  no table, the mean effect is **+0.34 to +0.86 nats** for the served models (Phase 3.3's instruct
  models: +0.16 to +0.60). The interval lies above zero in **17 of 18** served model × grammar
  groups; the exception is Gemma 4 on `blk` (+0.49, interval −0.03 to +1.00). Against the
  length-matched control: 16 of 18 (Gemma 4's interval includes zero on both grammars). Gemma 4's
  intervals are the widest of any model, about ±0.5 nats; §8 shows that its margins are noisy.
- **The largest effects are OLMo 3 Instruct's** (+0.77 to +0.86), and they are still not enough:
  OLMo 3 still reverts at 41–42% with the table.
- **Helping is not steering.** If every margin moved by the mean effect, only the sites that
  close to zero would change side, and without the table only 5–21% of served margins lie within
  0.5 nat of zero. Most sites are decided firmly one way or the other, which is why reversion
  falls by only 3–10 points when the table is added.

---

## 5. Size

Reversion with the table against total parameters (Figure 3):

| family | sizes | `dom` | `blk` |
|---|---|---|---|
| Qwen3.5 (fp8) | 27B → 122B → 397B | 0.404 → 0.434 → 0.424 | 0.420 → 0.444 → 0.433 |
| OLMo 3 Instruct | 7B → 32B | 0.414 → 0.412 | 0.418 → 0.410 |
| Phase 3.3: Qwen2.5-Coder Instruct | 0.5B → 32B | 0.445 → 0.400 | 0.441 → 0.454 |

**No family gets better with size.** Within Qwen3.5 the 15-fold increase from 27B to 397B leaves
reversion where it was (the intervals overlap at every step). Across the whole range, 0.5B to about
550B, every instruct model's rate lies between 0.40 and 0.53.

**Caution.** The served models differ in more than size: architecture (Qwen3.5 122B and 397B
are mixtures of experts with 10B and 17B active parameters; DeepSeek's active size is not
stated), precision (fp8, mxfp4), training and serving. This is an association across models, not
an effect of size.

---

## 6. Worked examples: the ladder

Kaplan–Meier median number of worked examples until an initially wrong site switches (95%
interval), and how many never switch within 32.

| phase | model | `dom` median examples [95% CI]; never switched | `blk` |
|---|---|---|---|
| 3.3 | Qwen2.5-Coder 0.5B Instruct | 4.6 [1.6, 12.8]; 11/88 never | 9.1 [3.7, 12.1]; 21/102 never |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | 3.8 [1.2, 6.5]; 14/87 never | 9.2 [3.9, 13.4]; 27/103 never |
| 3.3 | Qwen2.5-Coder 3B Instruct | 3.2 [1.3, 8.8]; 28/99 never | 7.1 [3.1, 16.3]; 32/112 never |
| 3.3 | Qwen2.5-Coder 7B Instruct | 2.1 [1.3, 5.5]; 15/115 never | 10.5 [5.4, 18.5]; 27/105 never |
| 3.3 | Qwen2.5-Coder 14B Instruct | 3.2 [2.5, 6.0]; 16/111 never | 6.3 [2.0, 10.3]; 15/102 never |
| 3.3 | Qwen2.5-Coder 32B Instruct | 1.8 [1.2, 4.0]; 18/86 never | 3.6 [1.8, 9.9]; 17/86 never |
| 3.3 | Qwen2.5 72B Instruct | 4.2 [2.1, 6.9]; 21/89 never | 11.2 [7.2, 19.1]; 28/97 never |
| 3.3 | DeepSeek-Coder 1.3B Instruct | 3.6 [1.8, 7.1]; 16/104 never | 5.9 [3.2, 12.0]; 20/109 never |
| 3.3 | DeepSeek-Coder 33B Instruct | 3.1 [1.9, 4.8]; 13/98 never | 3.5 [2.0, 6.8]; 12/98 never |
| 3.3 | Llama-3.2 1B Instruct | 1.6 [0.9, 3.0]; 6/102 never | 3.6 [1.4, 13.3]; 18/102 never |
| 4 | OLMo 3 7B Instruct | 9.4 [3.3, 31.5]; 33/90 never | 12.1 [6.5, 17.7]; 31/102 never |
| 4 | OLMo 3 32B Instruct | 3.8 [2.2, 9.6]; 20/85 never | 12.7 [6.5, 24.9]; 30/101 never |
| 4 | OLMo 3 32B Think | 5.4 [2.8, 11.6]; 27/93 never | 15.3 [11.4, 30.0]; 29/97 never |
| 4 | Qwen3-Coder 30B-A3B Instruct | 3.7 [1.3, 7.6]; 17/99 never | 5.9 [3.0, 14.8]; 27/92 never |
| 4 | Qwen3.5 27B | 1.8 [1.3, 3.2]; 9/72 never | 1.9 [1.4, 9.3]; 15/83 never |
| 4 | Qwen3.5 122B-A10B | 6.1 [2.3, 12.8]; 20/75 never | 6.0 [2.3, 7.8]; 18/88 never |
| 4 | Qwen3.5 397B-A17B | 4.4 [1.4, 9.3]; 13/78 never | 10.7 [5.9, 14.3]; 22/87 never |
| 4 | Gemma 4 31B | 1.7 [1.3, 3.4]; 3/109 never | 2.7 [1.7, 4.0]; 10/104 never |
| 4 | DeepSeek-V4.1-Flash | 2.4 [1.5, 5.0]; 12/89 never | 5.9 [3.0, 12.2]; 14/96 never |

**A caution on these medians.** They are the pipeline's, as exported. A rounding fault in the
Kaplan–Meier code, inherited from Phase 3.3, moves a median to the next switch when the survival
curve is exactly 1/2 there: 6 of the 18 served medians (OLMo 3 7B `dom`: 9.44 instead of 7.27)
and 14 of Phase 3.3's 42 held-out ones. No comparison below changes
([08 §6](08_issues_and_superseded_numbers.md#6-found-not-fixed-a-rounding-fault-in-the-kaplan-meier-median)).

Reversion at each number of worked examples (the same 400 sites per model at every rung, with
the table):

| phase | model | grammar | sites | 0 | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---:|---|---|---|---|---|---|---|
| 3.3 | Qwen2.5-Coder 0.5B Instruct | dom | 195 | 0.451 | 0.426 | 0.400 | 0.359 | 0.338 | 0.287 | 0.226 |
| 3.3 | Qwen2.5-Coder 0.5B Instruct | blk | 205 | 0.498 | 0.483 | 0.498 | 0.454 | 0.424 | 0.288 | 0.234 |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | dom | 195 | 0.446 | 0.426 | 0.431 | 0.379 | 0.338 | 0.303 | 0.246 |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | blk | 205 | 0.502 | 0.512 | 0.483 | 0.483 | 0.424 | 0.298 | 0.278 |
| 3.3 | Qwen2.5-Coder 3B Instruct | dom | 195 | 0.508 | 0.523 | 0.441 | 0.390 | 0.359 | 0.308 | 0.262 |
| 3.3 | Qwen2.5-Coder 3B Instruct | blk | 205 | 0.546 | 0.522 | 0.502 | 0.488 | 0.483 | 0.322 | 0.288 |
| 3.3 | Qwen2.5-Coder 7B Instruct | dom | 195 | 0.590 | 0.518 | 0.467 | 0.436 | 0.359 | 0.241 | 0.221 |
| 3.3 | Qwen2.5-Coder 7B Instruct | blk | 205 | 0.512 | 0.478 | 0.493 | 0.478 | 0.444 | 0.322 | 0.239 |
| 3.3 | Qwen2.5-Coder 14B Instruct | dom | 195 | 0.569 | 0.559 | 0.508 | 0.395 | 0.349 | 0.328 | 0.226 |
| 3.3 | Qwen2.5-Coder 14B Instruct | blk | 205 | 0.498 | 0.522 | 0.478 | 0.429 | 0.459 | 0.327 | 0.254 |
| 3.3 | Qwen2.5-Coder 32B Instruct | dom | 195 | 0.441 | 0.451 | 0.451 | 0.395 | 0.333 | 0.297 | 0.256 |
| 3.3 | Qwen2.5-Coder 32B Instruct | blk | 205 | 0.420 | 0.454 | 0.478 | 0.429 | 0.459 | 0.332 | 0.254 |
| 3.3 | Qwen2.5 72B Instruct | dom | 195 | 0.456 | 0.518 | 0.508 | 0.446 | 0.333 | 0.313 | 0.246 |
| 3.3 | Qwen2.5 72B Instruct | blk | 205 | 0.473 | 0.546 | 0.541 | 0.498 | 0.488 | 0.332 | 0.307 |
| 3.3 | DeepSeek-Coder 1.3B Instruct | dom | 195 | 0.533 | 0.538 | 0.451 | 0.405 | 0.328 | 0.313 | 0.236 |
| 3.3 | DeepSeek-Coder 1.3B Instruct | blk | 205 | 0.532 | 0.556 | 0.541 | 0.473 | 0.439 | 0.312 | 0.249 |
| 3.3 | DeepSeek-Coder 33B Instruct | dom | 195 | 0.503 | 0.595 | 0.497 | 0.441 | 0.338 | 0.308 | 0.221 |
| 3.3 | DeepSeek-Coder 33B Instruct | blk | 205 | 0.478 | 0.454 | 0.454 | 0.376 | 0.459 | 0.298 | 0.244 |
| 3.3 | Llama-3.2 1B Instruct | dom | 195 | 0.523 | 0.441 | 0.421 | 0.374 | 0.338 | 0.251 | 0.169 |
| 3.3 | Llama-3.2 1B Instruct | blk | 205 | 0.498 | 0.473 | 0.463 | 0.410 | 0.459 | 0.322 | 0.249 |
| 4 | OLMo 3 7B Instruct | dom | 195 | 0.462 | 0.426 | 0.467 | 0.390 | 0.400 | 0.349 | 0.297 |
| 4 | OLMo 3 7B Instruct | blk | 205 | 0.498 | 0.478 | 0.517 | 0.478 | 0.434 | 0.371 | 0.327 |
| 4 | OLMo 3 32B Instruct | dom | 195 | 0.436 | 0.487 | 0.451 | 0.405 | 0.405 | 0.379 | 0.292 |
| 4 | OLMo 3 32B Instruct | blk | 205 | 0.493 | 0.488 | 0.463 | 0.449 | 0.444 | 0.356 | 0.312 |
| 4 | OLMo 3 32B Think | dom | 195 | 0.477 | 0.482 | 0.446 | 0.400 | 0.385 | 0.354 | 0.359 |
| 4 | OLMo 3 32B Think | blk | 205 | 0.473 | 0.527 | 0.463 | 0.439 | 0.449 | 0.380 | 0.298 |
| 4 | Qwen3-Coder 30B-A3B Instruct | dom | 195 | 0.508 | 0.523 | 0.492 | 0.426 | 0.364 | 0.297 | 0.215 |
| 4 | Qwen3-Coder 30B-A3B Instruct | blk | 205 | 0.449 | 0.478 | 0.502 | 0.444 | 0.420 | 0.337 | 0.283 |
| 4 | Qwen3.5 27B | dom | 195 | 0.369 | 0.477 | 0.415 | 0.338 | 0.308 | 0.236 | 0.195 |
| 4 | Qwen3.5 27B | blk | 205 | 0.405 | 0.444 | 0.400 | 0.405 | 0.415 | 0.302 | 0.215 |
| 4 | Qwen3.5 122B-A10B | dom | 195 | 0.385 | 0.446 | 0.410 | 0.369 | 0.333 | 0.313 | 0.221 |
| 4 | Qwen3.5 122B-A10B | blk | 205 | 0.429 | 0.410 | 0.424 | 0.405 | 0.390 | 0.259 | 0.239 |
| 4 | Qwen3.5 397B-A17B | dom | 195 | 0.400 | 0.441 | 0.472 | 0.405 | 0.354 | 0.251 | 0.190 |
| 4 | Qwen3.5 397B-A17B | blk | 205 | 0.424 | 0.483 | 0.493 | 0.459 | 0.444 | 0.268 | 0.229 |
| 4 | Gemma 4 31B | dom | 195 | 0.559 | 0.523 | 0.441 | 0.379 | 0.297 | 0.246 | 0.195 |
| 4 | Gemma 4 31B | blk | 205 | 0.507 | 0.502 | 0.463 | 0.410 | 0.400 | 0.273 | 0.200 |
| 4 | DeepSeek-V4.1-Flash | dom | 195 | 0.456 | 0.492 | 0.467 | 0.426 | 0.323 | 0.215 | 0.200 |
| 4 | DeepSeek-V4.1-Flash | blk | 205 | 0.468 | 0.449 | 0.434 | 0.415 | 0.420 | 0.298 | 0.190 |

**What it shows.**

- **Worked examples switch served models' sites, as they did Phase 3.3's.** Every model reverts
  less at 32 examples than at none: at 32, 19–36% of the 400 ladder sites still revert (Phase
  3.3's instruct models: 17–31%).
- **The OLMo 3 models need the most.** Their `blk` medians, 12.1 (7B), 12.7 (32B Instruct) and
  15.3 (32B Think) examples, are above Phase 3.3's largest (11.2, Qwen2.5 72B Instruct), with wide
  intervals (upper bounds 17.7–30.0).
- **Qwen3.5 27B and Gemma 4 need few:** Qwen3.5 27B 1.8 (`dom`) and 1.9 (`blk`), Gemma 4 1.7
  and 2.7, as fast as Phase 3.3's fastest (Llama-3.2 1B Instruct, 1.6 in `dom`).
- **Never switched within 32:** 3–33 of each served model's 72–109 initially wrong sites
  (Phase 3.3: 6–32).
- **One example is not better than none.** At 1 example, `dom` reversion is higher than at 0 for
  7 of 9 served models (Qwen3.5 27B: 0.369 → 0.477); Phase 3.3: 5 of 10. The fall starts at 2–4
  examples. Each rung has 195 `dom` sites, so a single step is uncertain.

---

## 7. Free generation (Arm B)

Greedy generation from a natural-language request, with the table and four worked examples.
Reach = share of decision sites the program gets to; then the share of reached sites where the
familiar spelling is written. The two are never multiplied.

| phase | model | programs | empty | correct | `dom` reach | `dom` familiar given reached | `blk` reach | `blk` familiar given reached |
|---|---|---:|---:|---:|---|---|---|---|
| 3.3 | Qwen2.5-Coder 0.5B Instruct | 780 | 0 | 17 | 0.029 [0.016, 0.046] | 0.227 [0.085, 0.429] | 0.030 [0.017, 0.048] | 0.174 [0.056, 0.310] |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | 780 | 0 | 33 | 0.065 [0.045, 0.089] | 0.265 [0.179, 0.353] | 0.074 [0.049, 0.103] | 0.214 [0.112, 0.350] |
| 3.3 | Qwen2.5-Coder 3B Instruct | 780 | 0 | 70 | 0.144 [0.110, 0.178] | 0.211 [0.155, 0.280] | 0.125 [0.097, 0.156] | 0.237 [0.169, 0.309] |
| 3.3 | Qwen2.5-Coder 7B Instruct | 780 | 0 | 72 | 0.146 [0.110, 0.184] | 0.190 [0.140, 0.250] | 0.121 [0.093, 0.153] | 0.223 [0.159, 0.304] |
| 3.3 | Qwen2.5-Coder 14B Instruct | 780 | 0 | 119 | 0.205 [0.169, 0.245] | 0.212 [0.165, 0.270] | 0.194 [0.156, 0.235] | 0.204 [0.154, 0.261] |
| 3.3 | Qwen2.5-Coder 32B Instruct | 780 | 0 | 118 | 0.234 [0.192, 0.280] | 0.194 [0.153, 0.238] | 0.174 [0.136, 0.212] | 0.221 [0.183, 0.263] |
| 3.3 | Qwen2.5 72B Instruct | 780 | 0 | 172 | 0.328 [0.274, 0.381] | 0.149 [0.115, 0.187] | 0.277 [0.236, 0.324] | 0.169 [0.130, 0.218] |
| 3.3 | DeepSeek-Coder 1.3B Instruct | 780 | 0 | 39 | 0.073 [0.049, 0.100] | 0.243 [0.162, 0.340] | 0.055 [0.037, 0.079] | 0.167 [0.079, 0.273] |
| 3.3 | DeepSeek-Coder 33B Instruct | 780 | 0 | 94 | 0.177 [0.141, 0.216] | 0.168 [0.119, 0.221] | 0.165 [0.133, 0.200] | 0.220 [0.156, 0.290] |
| 3.3 | Llama-3.2 1B Instruct | 780 | 0 | 13 | 0.045 [0.028, 0.065] | 0.235 [0.137, 0.354] | 0.046 [0.028, 0.067] | 0.214 [0.118, 0.357] |
| 4 | OLMo 3 7B Instruct | 780 | 290 | 12 | 0.053 [0.037, 0.075] | 0.407 [0.279, 0.553] | 0.009 [0.004, 0.015] | 0.714 [0.462, 1.000] |
| 4 | OLMo 3 32B Instruct | 780 | 334 | 32 | 0.065 [0.044, 0.092] | 0.303 [0.197, 0.437] | 0.055 [0.037, 0.078] | 0.321 [0.220, 0.449] |
| 4 | OLMo 3 32B Think | 780 | 0 | 54 | 0.116 [0.085, 0.150] | 0.295 [0.213, 0.399] | 0.097 [0.070, 0.129] | 0.340 [0.253, 0.448] |
| 4 | Qwen3-Coder 30B-A3B Instruct | 780 | 0 | 112 | 0.195 [0.156, 0.236] | 0.189 [0.142, 0.240] | 0.192 [0.157, 0.232] | 0.162 [0.121, 0.210] |
| 4 | Qwen3.5 27B | 780 | 0 | 93 | 0.117 [0.086, 0.148] | 0.175 [0.121, 0.238] | 0.288 [0.251, 0.329] | 0.114 [0.082, 0.152] |
| 4 | Qwen3.5 122B-A10B | 780 | 0 | 129 | 0.224 [0.179, 0.271] | 0.150 [0.114, 0.194] | 0.241 [0.197, 0.290] | 0.148 [0.113, 0.195] |
| 4 | Qwen3.5 397B-A17B | 780 | 48 | 188 | 0.369 [0.309, 0.434] | 0.140 [0.110, 0.172] | 0.255 [0.214, 0.299] | 0.158 [0.127, 0.193] |
| 4 | Gemma 4 31B | 780 | 0 | 301 | 0.541 [0.480, 0.603] | 0.038 [0.026, 0.051] | 0.464 [0.417, 0.513] | 0.043 [0.029, 0.057] |
| 4 | DeepSeek-V4.1-Flash | 780 | 0 | 120 | 0.217 [0.174, 0.262] | 0.204 [0.164, 0.250] | 0.174 [0.139, 0.213] | 0.261 [0.201, 0.329] |

**What it shows.**

- **Gemma 4 writes the most, and almost never reverts when it writes.** It reaches 54% (`dom`)
  and 46% (`blk`) of decision sites, against at most 33% for any Phase 3.3 model. At the sites it
  reaches, it writes the familiar spelling 3.8% and 4.3% of the time, against 14.9–26.5% for
  Phase 3.3's models. 301 of its 780 programs are exactly correct (Phase 3.3's best: 172,
  Qwen2.5 72B Instruct).
- **Qwen3.5 397B is next:** reach 0.369 / 0.255, familiar given reached 0.140 / 0.158, 188
  correct programs. It also returned 48 empty generations, for the same reason as OLMo 3: at
  those prompts its first token was the end-of-turn token
  ([08 §2](08_issues_and_superseded_numbers.md#2-measurement-findings-not-bugs-they-are-reported)).
- **OLMo 3 Instruct mostly writes nothing** under the raw-text prompt: 290 (7B) and 334 (32B) of
  780 generations are empty, because its most likely first token is its end-of-turn token
  ([01 §10](01_theory.md#10-ending-the-turn-empty-generations)). What it does write reaches
  0.9–6.5% of sites and reverts at 30–71% of them, from few sites (OLMo 3 7B `blk`: 10 of 14,
  interval 0.46–1.00). OLMo 3 32B Think wrote every time (0 empty).
- **The models that reach more sites revert less at them**: a rank correlation of −0.96 over
  the 18 served model × grammar groups (Phase 3.3's 20: −0.47). Description, not a test.
- **Writing is not the forced choice.** Reversion given reach is below the model's Arm A rate
  for every served model except OLMo 3 7B (which reached few sites). The two arms measure
  different things: what a model writes freely, and which of two spellings it prefers.

---

## 8. Precision: rounding and batching

**Ties and near-zero margins** (all three Arm A conditions):

| phase | model | Arm A margins | ties | within 1/8 nat of zero | single-token margins on the 1/32 grid |
|---|---|---:|---:|---:|---:|
| 3.3 | Qwen2.5-Coder 0.5B Instruct | 9,090 | 0 (0.00%) | 301 (3.3%) | – |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | 9,090 | 0 (0.00%) | 443 (4.9%) | – |
| 3.3 | Qwen2.5-Coder 3B Instruct | 9,090 | 0 (0.00%) | 494 (5.4%) | – |
| 3.3 | Qwen2.5-Coder 7B Instruct | 9,090 | 0 (0.00%) | 415 (4.6%) | – |
| 3.3 | Qwen2.5-Coder 14B Instruct | 9,090 | 0 (0.00%) | 383 (4.2%) | – |
| 3.3 | Qwen2.5-Coder 32B Instruct | 9,090 | 0 (0.00%) | 381 (4.2%) | – |
| 3.3 | Qwen2.5 72B Instruct | 9,090 | 0 (0.00%) | 365 (4.0%) | – |
| 3.3 | DeepSeek-Coder 1.3B Instruct | 9,090 | 0 (0.00%) | 397 (4.4%) | – |
| 3.3 | DeepSeek-Coder 33B Instruct | 9,090 | 0 (0.00%) | 664 (7.3%) | – |
| 3.3 | Llama-3.2 1B Instruct | 9,090 | 0 (0.00%) | 348 (3.8%) | – |
| 4 | OLMo 3 7B Instruct | 9,090 | 85 (0.94%) | 221 (2.4%) | 0.9230 |
| 4 | OLMo 3 32B Instruct | 9,090 | 97 (1.07%) | 213 (2.3%) | 0.9738 |
| 4 | OLMo 3 32B Think | 9,090 | 71 (0.78%) | 264 (2.9%) | 0.9576 |
| 4 | Qwen3-Coder 30B-A3B Instruct | 9,090 | 141 (1.55%) | 207 (2.3%) | 1.0000 |
| 4 | Qwen3.5 27B | 9,090 | 162 (1.78%) | 348 (3.8%) | 0.9778 |
| 4 | Qwen3.5 122B-A10B | 9,090 | 28 (0.31%) | 431 (4.7%) | 0.1780 |
| 4 | Qwen3.5 397B-A17B | 9,090 | 167 (1.84%) | 357 (3.9%) | 0.9988 |
| 4 | Gemma 4 31B | 9,090 | 27 (0.30%) | 91 (1.0%) | 0.7801 |
| 4 | DeepSeek-V4.1-Flash | 9,090 | 0 (0.00%) | 550 (6.1%) | 0.0000 |

**Re-scoring a fixed sample** after the run (300 sites with the table per model, the same pinned
deployment):

| model | sites | same to the bit | median abs. change | 95th percentile | largest | sign changed |
|---|---:|---:|---:|---:|---:|---:|
| OLMo 3 7B Instruct | 300 | 150 | 0.0000 | 0.3745 | 0.8125 | 1 (0.3%) |
| OLMo 3 32B Instruct | 300 | 293 | 0.0000 | 0.0000 | 0.4484 | 0 (0.0%) |
| OLMo 3 32B Think | 300 | 299 | 0.0000 | 0.0000 | 0.0166 | 0 (0.0%) |
| Qwen3-Coder 30B-A3B Instruct | 300 | 300 | 0.0000 | 0.0000 | 0.0000 | 0 (0.0%) |
| Qwen3.5 27B | 300 | 288 | 0.0000 | 0.0000 | 0.6250 | 0 (0.0%) |
| Qwen3.5 122B-A10B | 300 | 27 | 0.2028 | 0.7387 | 1.2445 | 20 (6.7%) |
| Qwen3.5 397B-A17B | 300 | 300 | 0.0000 | 0.0000 | 0.0000 | 0 (0.0%) |
| Gemma 4 31B | 300 | 140 | 0.1145 | 3.7544 | 10.6886 | 14 (4.7%) |
| DeepSeek-V4.1-Flash | 300 | 264 | 0.0000 | 0.1982 | 0.6848 | 4 (1.3%) |

**What it shows.**

- **Ties exist, and are rare.** 778 of the 81,810 served Arm A margins are exactly zero (0.95%),
  from 0 (DeepSeek-V4.1-Flash, which does not round) to 167 (Qwen3.5 397B, 1.8%). Phase 3.3: none
  in 90,900. A tie is not counted as a reversion.
- **Rounding did not crowd the margins near zero.** The share within 1/8 nat of zero is 1.0–6.1%
  for the served models and 3.3–7.3% for Phase 3.3's. So the sites whose sign rounding could decide
  are few, and no more common than in Phase 3.3's exact scores: they bound any effect of rounding on
  a rate at a few points.
- **The grid.** Single-token margins fall on the 1/32-nat grid for 92–100% of six rounding models'
  sites, 78% for Gemma 4 and 18% for Qwen3.5 122B, and 0% for DeepSeek, which does not round.
  For a rounding model, an off-grid margin means that the two requests of a pair were not
  computed alike: the variation that the re-scoring measures.
- **Re-scoring: seven deployments repeat closely, two do not.** Of the 2,700 re-scored margins,
  2,061 (76%) came back identical to the bit. Qwen3-Coder and Qwen3.5 397B repeated all 300;
  OLMo 3 32B Instruct, OLMo 3 32B Think and Qwen3.5 27B 288–299; DeepSeek 264; OLMo 3 7B 150,
  with changes up to 0.81 nat. **Gemma 4** (140 identical; median change 0.11 nat, 95th
  percentile 3.75, largest 10.7) and **Qwen3.5 122B** (27 identical; median 0.20, 95th percentile
  0.74) vary far more than rounding can explain. Every answer came from the pinned deployment, so
  the variation is inside one deployment; its cause is on the server, out of our sight.
- **Signs and rates.** 39 of the 2,700 margins changed sign: 20 Qwen3.5 122B's, 14 Gemma 4's, 4
  DeepSeek's, 1 OLMo 3 7B's. On each 300-site sample, the reversion rate moved by at most 1.3
  points (Gemma 4: 0.487 → 0.500); Qwen3.5 122B's 20 changes cancelled, 10 each way. So rates are
  stable to about a point, but single margins of Gemma 4 and Qwen3.5 122B are not reliable, even
  far from zero: Gemma 4's sign changes were at margins of 0.25 to 4.6 nats.

---

## 9. What this run does not show

- **Nothing confirmatory.** Every served-model number here is development.
- **No H4 or H5.** No served model has a base twin.
- **Nothing about size as a cause.** The large models differ from the small in architecture
  (mixtures of experts), precision (fp8, mxfp4), family and serving, all at once.
- **Nothing about whether OLMo 3 can write 3DOM** under a chat prompt: under Phase 3.3's raw-text
  prompt it mostly ended its turn ([01 §10](01_theory.md#10-ending-the-turn-empty-generations)).
- **Nothing about why Gemma 4 and Qwen3.5 122B vary** between identical requests: the API shows
  only that the same deployment answered.
