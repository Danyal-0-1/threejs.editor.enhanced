# 08 — Issues found in this run, and superseded numbers

> What went wrong or was found wanting, what it changed, and which earlier statements no longer
> hold. Nothing here changes a Phase 3.3 number, but §6 reports a rounding fault, inherited from
> Phase 3.3's code, that moves some Kaplan–Meier medians of both phases; it is left for the author
> to decide.

---

## 1. Operational incidents (no effect on any number)

| incident | what happened | effect | fix |
|---|---|---|---|
| **The first launch stalled** (12:12–12:20) | 54 requests in flight, each on a new TLS connection; the laptop's path to the API dropped packets, and TCP waited up to 120 s between resends. 8 of 9 processes read nothing for minutes ([03 §7](03_code_and_pipeline.md#7-the-first-launch-and-why-it-stalled-12121220)) | none: finished cells are atomic files; 15 Arm A and 6 ladder cells were kept, and the rest redone | one reused connection per thread; a 150 s limit per request, then a retry on a fresh connection; 27 requests in flight ([03 §8](03_code_and_pipeline.md#8-the-fix-and-the-relaunch-122541)) |
| **A server error failed a cell** | the first client did not retry `HTTP 500`; one DeepSeek cell failed with "Internal server error" | none: the failure was recorded and the cell redone on resume | 500 is now retried with backoff, like 502–504 |
| **Killed jobs left "RUNNING" manifests** | the jobs stopped with SIGKILL in the first launch never wrote their end status | `job_provenance.csv` lists them as RUNNING; their finished cells are valid and verified by `validate` | — (kept as the honest record) |
| **DeepSeek and Arm B were slow** | DeepSeek scored 1 Arm A cell per minute with two cells side by side, against 1.6–8 for the others with one; Arm B made one generation at a time per cell | none | DeepSeek ran two cells at a time in Arm A and three in the ladder; the Arm B of Qwen3.5 122B, Qwen3.5 397B and DeepSeek ran four ([03 §9](03_code_and_pipeline.md#9-the-slow-ones-deepseek-and-arm-b)) |
| **The first probe hung** (2026-10-22) | four deployments did not answer; each request waited 360 s, four times | none (stopped, nothing written) | probe requests wait 60 s, twice; a model that does not answer is recorded and skipped |
| **Gateway error texts named its internals** | a 500 answer quoted an internal route name | it would have gone into the public repository with the probe's record | errors are cut to their first sentence (`_err` in `tools/voyager_models.py`) |

**Retries over the run** (the logs, from the relaunch on): 1,294 retries of 1,156 requests
(1,100 `RemoteDisconnected`, 147 `HTTP 503`, 46 `HTTP 500`, 1 timeout), 1,167 of them
DeepSeek-V4.1-Flash's. Every retried request succeeded by its fourth attempt of the eight
allowed ([03 §8](03_code_and_pipeline.md#8-the-fix-and-the-relaunch-122541)).

---

## 2. Measurement findings (not bugs: they are reported)

| finding | evidence | consequence |
|---|---|---|
| **Rounded scores** | the probe: 33 of 36 models' margins on a 1/8–1/32 nat grid; the run: 778 exact ties in 81,810 margins (Table A1) | a tie is not counted as reversion; margins near zero are uncertain |
| **Batching noise** | the same request gave a different log-probability (0.04 nat at one site); the re-scored sample: 2,061 of 2,700 margins identical to the bit, 39 changed sign (Table A2) | single margins near zero are not reliable; rates moved by at most 1.3 points on the samples |
| **Two deployments vary far more** | Gemma 4: median change 0.11 nat, largest 10.7, 14 sign changes at margins of 0.25–4.6 nats; Qwen3.5 122B: 273 of 300 margins changed, 20 sign changes. Same pinned deployment throughout | for these two, single margins are not reliable even far from zero; Gemma 4's rule-effect intervals are the widest of any model. The cause is on the server and not visible to us |
| **OLMo 3 ends its turn in Arm B** | first generated token `<\|im_end\|>` (7B: log-probability −0.34; 32B Instruct: −0.09); 290 (7B) and 334 (32B Instruct) of 780 generations empty; Phase 3.3: 0 of 7,800 | OLMo 3's Arm B measures "stops at once", not reversion; Arm A unaffected |
| **Qwen3.5 397B also ends its turn, sometimes** | 48 of 780 generations empty, 28 of them in `blk` × `d50s3`. Two of them asked again after the run, with special tokens kept: the only token generated was `<\|im_end\|>` (log-probability −0.46 and −0.70, against −1.08 and −0.83 for `" $"`); the same deployment answered | its reach is lowered by those 48; Arm A unaffected |
| **Quantized weights** | the listing: Qwen3.5 fp8, DeepSeek mxfp4 | the served model is the quantized one (Table 1) |
| **Job manifests describe the laptop** | every job manifest records `dtype: bfloat16`, `lm_head_fp32: true` and the laptop's GPU | these are the config's local settings, unused by served models; the rows' `dtype` (served precision) and `fp32_head: false`, and `model_pins.json`, record what was measured ([03 §13](03_code_and_pipeline.md#13-merge-export-and-validate)) |

---

## 3. Fixed in the code during this work

| what | before | after |
|---|---|---|
| **Arm B and H5 row labels** | `"p33/1"` written as a literal, whatever the run | the pipeline's label, `p4/1` (a test checks every experiment's rows) |
| **Slurm job names** | `p33-<job>` | `p4-<job>` |
| **H5 for a model with no base twin** | its "targeted" arm would have been the first roles in alphabetical order (no base risk to rank them by) | an instruct model without a base twin is not an H5 model; every served model is left out |
| **The plain-language report** | one verdict whatever the numbers; on this run it would have read "in **18 of 90** the interval includes zero — handing over the glossary barely changes what gets written" | the counts, and no verdict: "Its interval lies above zero (the table helps) in **72 of 90**, below zero in 0, and includes zero in 18. Helping is not the same as being enough" (a test checks the counts) |

---

## 4. Superseded statements

| earlier | now |
|---|---|
| "Every model gave the same margins twice, bit for bit" (the probe, 2026-10-22) | true for short requests sent one at a time to a quiet server; **under load the same request can return a different log-probability** ([01 §5](01_theory.md#5-batching-noise-the-same-request-a-different-answer)) |
| "About 0.9 s per pair, so roughly 4 hours per model" (one model at 200 tokens) | measured: Arm A took 19.9 minutes (OLMo 3 7B Instruct) to 160.5 (DeepSeek-V4.1-Flash, two cells at a time); a whole model 45 minutes to 5 h 43 min, nine models side by side ([03 §9](03_code_and_pipeline.md#9-the-slow-ones-deepseek-and-arm-b)) |
| "36 models serve both arms" | still true of the protocol; but OLMo 3 Instruct mostly, and Qwen3.5 397B sometimes, return empty text under it (§2) |
| `share_on_1_32_grid` as a test of rounding | a margin is computed from two requests; batching moves it off the grid, so the run's grid share is lower than the probe's (Table A1) |

---

## 5. What is *not* an issue (checked)

- **The materials.** The plan of `dev-20261023a` has the same 3,030 sites as Phase 3.3's held-out
  run; the figure script refuses otherwise.
- **The key.** It is in no file of the repository or of the results (searched for the key's text).
- **Concurrency.** Two cells side by side give the same rows as one at a time (a test).
- **The pins.** Every answer was checked against its deployment's pin; 0 cells failed with
  `ServedModelChanged`, and the re-test's 2,700 answers came from the pinned deployments too.
- **Phase 3.3's numbers.** Unchanged: the comparison tool still reproduces its 36 + 19 tables.

---

## 6. Found, not fixed: a rounding fault in the Kaplan-Meier median

| | |
|---|---|
| **What** | `kaplan_meier` ([`p4/analysis/kstar.py`](../../../phase4/code/p4/analysis/kstar.py) 124–149, a copy of Phase 3.3's frozen code) takes as the median the first event at which the survival curve S ≤ 0.5, and computes S as a product of floating-point factors. When S is exactly 1/2 at an event, the product can come out as 0.5000000000000001, and the median moves to the next event. |
| **Evidence** | OLMo 3 7B Instruct, `dom`: S = 45/90 = 1/2 exactly at the 45th switch (`k*` = 7.27); the code gets 0.5000000000000001 and reports 9.44 ([02 §3](02_mathematics_and_statistics.md#3-kaplanmeier-for-one-model-olmo-3-7b-instruct-dom)). Recomputed in exact fractions from the exported site rows: 8 of the 18 served model × grammar groups reach S = 1/2 exactly, and 6 of their medians move, by 0.03 to 2.16 examples. In Phase 3.3's held-out run, 21 of 42 groups reach it and 14 medians move, by 0.02 to 1.56 examples (the largest: Llama-3.2 1B, `blk`, 6.86 against 5.30). |
| **Effect** | the point medians of Table 4 and Figure 4 only; rates, effects, reach and the other numbers are untouched. The bootstrap intervals call the same function, so some of their replicates carry the same rounding. |
| **Why not fixed here** | Phase 3.3's medians are registered results of frozen code: correcting them is a dated deviation, and a decision for the author. Phase 4's copy should change with it, or the two phases' medians stop being comparable. A fix is one line: compare with a tolerance (`s <= 0.5 + 1e-12`), or compute S in exact fractions. |

The six served medians that move, as exported → in exact arithmetic: OLMo 3 7B Instruct `dom`
9.44 → 7.27 and `blk` 12.09 → 12.06; Qwen3-Coder `blk` 5.91 → 5.06; DeepSeek-V4.1-Flash `blk`
5.93 → 5.43; Qwen3.5 122B `blk` 5.98 → 5.75; Gemma 4 `blk` 2.70 → 2.58.
