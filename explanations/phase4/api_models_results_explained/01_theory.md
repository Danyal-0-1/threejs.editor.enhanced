# 01 — Theory: what the served-model results mean

> The design concepts (site, collision, margin, reversion, rule effect, ladder, `k*`, Arm B,
> cluster bootstrap) are defined in
> [`../../phase3_3/sol_experiment_explained/01_theory_and_research_design.md`](../../phase3_3/sol_experiment_explained/01_theory_and_research_design.md),
> and what they meant for Phase 3.3's models in
> [`../../phase3_3/heldout_results_explained/01_theory.md`](../../phase3_3/heldout_results_explained/01_theory.md).
> They are not repeated here.
>
> This file covers what is **new** when the model is served by someone else. Each concept gets
> 10 points:
>
> 1. technical;
> 2. simple;
> 3. real example from this run;
> 4. inputs → outputs;
> 5. assumptions;
> 6. silent failure;
> 7. symptom;
> 8. test;
> 9. where in code;
> 10. why it matters.

---

## 1. Development evidence

1. **Technical.** A development result is measured before the hypotheses, criteria and analysis
   are registered and frozen. It can describe, suggest and calibrate. It cannot confirm, because
   anything in the design could still be chosen with it in view.
2. **Simple.** A practice exam. You learn from it; you don't grade yourself on it.
3. **Example.** `dev-20261023a` ran on 2026-10-23 while `phase4/PREREGISTRATION.md` still said
   "DRAFT". Every row carries `split: DEVELOPMENT`, and every report opens with "These results are
   not confirmatory".
4. **In → out.** A draft design plus data gives descriptions, effect sizes and a design for the
   confirmatory test.
5. **Assumptions.** Nothing measured here is later reported as if it had been predicted.
6. **Silent failure.** Quoting a development rate in a paper as a test of a hypothesis.
7. **Symptom.** A "confirmatory" claim whose model or cells appear in `DEV_MODELS`.
8. **Test.** `test_a_draft_preregistration_cannot_be_frozen`: the freeze, and so any held-out
   run, refuses while the preregistration is a draft.
9. **Where.** `p4/governance/splits.py` (`DEV_MODELS`, `classify`), `p4/governance/freeze.py`
   (`DRAFT_MARKER`).
10. **Why it matters.** It decides what the paper can say about these nine models: "we
    observed", never "we predicted". Phase 3.3's numbers next to them are confirmatory
    held-out results; mixing the two kinds in one sentence is the most likely mistake in
    writing this up.

---

## 2. A served model, pinned to a deployment

1. **Technical.** The model is computed on Research Computing's servers. The only identity the
   API gives is the name of the model the gateway ran and the server's `system_fingerprint`. The
   pipeline pins `"<served name>@<fingerprint>"` at `prefetch` and checks every answer against it;
   an answer from another deployment raises `ServedModelChanged`, and that cell fails instead of
   mixing two deployments.
2. **Simple.** We can't keep a copy of the model, so we write down which copy answered, and stop
   if a different copy answers.
3. **Example.** `asu-rc/qwen35-27b` is pinned as `qwen35-27b-fp8@vllm-0.26.0-5c5b7be4`: the gateway
   ran the fp8 variant. Every answer of the run was checked (three per Arm A or ladder pair, one
   per generation): none came from another deployment (0 cells failed with `ServedModelChanged`),
   nor did any of the re-test's 2,700 answers, five to six hours later.
4. **In → out.** One answer gives (served name, fingerprint), compared with the pin: equal, or the
   cell fails.
5. **Assumptions.**
   - A changed model gets a changed fingerprint. Three models send no fingerprint at all
     (granite41-30b, minimax-m2-7, qwen-agentworld-35b-a3b; none was used here).
   - The same fingerprint means the same weights.
6. **Silent failure.** A redeployment with the same fingerprint, or no fingerprint, would mix two
   models without any error.
7. **Symptom.** A shift in a model's margins partway through the run, cell by cell.
8. **Test.** `test_an_answer_from_another_deployment_is_refused`,
   `test_prefetch_pins_the_answering_deployment_and_keeps_it`.
9. **Where.** `p4/scoring/api.py` (`_post`, `__init__`), `p4/runtime/prefetch.py` (`pin_served`),
   `p4/runtime/preflight.py` (`model_checks`).
10. **Why it matters.** Phase 3.3 pinned a git commit of the weights: anyone can download them
    and repeat a number. A served model can be repeated only while that deployment exists. The
    paper must say so.

---

## 3. The same measurement through an API

1. **Technical.** Phase 3.3 scored raw text: no chat template and no special tokens. vLLM's
   `/v1/completions` returns, for a prompt, every token's id (`return_token_ids`) and its
   log-probability given the tokens before it (`prompt_logprobs: 0`), with special tokens off
   (`add_special_tokens: false`). From two such answers (prefix + correct, prefix + familiar) the
   margin is computed by Phase 3.3's own `check_pair` and first-divergent-token sum; a third request
   counts the prefix's tokens for the `merged` flag.
2. **Simple.** We ask the server for the exact numbers our own scorer used to compute, then do the
   same arithmetic.
3. **Example.** [03 §10](03_code_and_pipeline.md#10-one-site-through-the-api): OLMo 3 7B Instruct,
   correct `" '#"` −17.0033, familiar `" '."` −15.5814, M = −1.4219, merged.
4. **In → out.** prefix, correct, familiar → three requests → `PairScore`, the same object
   `TokenScorer` returns.
5. **Assumptions.**
   - The server tokenizes exactly as its model was trained to (true for vLLM).
   - A log-probability for every prompt token is returned; the scorer refuses an answer without
     one.
6. **Silent failure.** Leaving special tokens on: five served models (devstral2, gemma4, the two
   llama4, muse-glimmer) add a beginning-of-text token by default, which would shift `k` and
   change the context of every prompt.
7. **Symptom.** `k_common` one larger than the prefix's own token count.
8. **Test.** `test_the_margin_is_margins_py_algorithm_on_the_served_tokens`,
   `test_special_tokens_stay_off_even_where_the_server_would_add_them`,
   `test_the_refusals_are_margins_pys`.
9. **Where.** `p4/scoring/api.py` (`_tokens`, `score_pair_detailed`).
10. **Why it matters.** It is what makes these numbers comparable with Phase 3.3's: the same
    sites, the same prompts, the same algorithm. What still differs is the server's arithmetic
    (§4–5) and the weights' precision (§6).

---

## 4. Rounded scores, and ties

1. **Technical.** Most servers compute the output layer in bf16. A bf16 number near 16–32 is
   resolved only to 1/8; near 8–16, to 1/16. For two single-token candidates M is a difference of
   two such logits, so it comes in steps, and two candidates can tie exactly. Phase 3.3 computed
   the output layer in fp32 to avoid this (defect P33-002) and had 0 ties in 190,890 margins.
2. **Simple.** A ruler with marks every eighth of an inch can't tell you which of two lines is
   longer when they differ by less than that.
3. **Example.** In the probe 33 of 36 models gave margins on a grid of 1/8, 1/16 or 1/32 nat. In
   the run: 778 ties among 81,810 served Arm A margins (0.95%), none for DeepSeek, which does not
   round (Table A1); Phase 3.3's instruct models: 0 in 90,900.
4. **In → out.** Two rounded logits give a margin on a grid; a tie is a margin of exactly 0.
5. **Assumptions.** A tie is neither reversion nor correct. The pipeline counts reversion as
   M < 0, so a tie counts as *not* reverted, as in Phase 3.3.
6. **Silent failure.** Counting ties as reversions (M ≤ 0) would raise every served model's rate.
7. **Symptom.** Exact zeros in `m_seq`; `tie: true` rows.
8. **Test.** The probe's `resolution()` and `test_margin_resolution_tells_rounded_logits_from_full_precision`.
9. **Where.** `p4/scoring/margins.py` (`PairScore.tie`); the probe in
   `tools/voyager_models.py` (`check_margins`).
10. **Why it matters.** In Phase 3.3, 2.5% of margins lay within 0.0625 nat of zero and 5.1%
    within 0.125 (its ten instruct models: 2.3% and 4.6%). Those are the margins whose sign
    rounding can decide. The effect on a reversion rate is bounded by that share (Figure A1); for
    the served models it is 1.0–6.1%.

---

## 5. Batching noise: the same request, a different answer

1. **Technical.** The server batches each request with other users' requests. The order of the
   floating-point sums depends on the batch, so the same prompt can come back with slightly
   different log-probabilities. A margin is computed from two requests that may sit in different
   batches. The API shows none of this: the answer names the same deployment either way, so any
   other server-side difference between two answers looks the same to us.
2. **Simple.** The same question to the same clerk, at a busy moment and a quiet one, gets
   answers that differ in the last digit.
3. **Example.** The probe's repeat (a short sentence, one request at a time, quiet server) was
   identical to the bit. In the run, one site re-scored by hand moved from M = −1.4616 to
   −1.4219. Re-scoring a fixed sample of 300 sites per model, after the run (Table A2): 2,061 of
   2,700 margins came back identical to the bit, and 39 changed sign. It depends on the
   deployment: Qwen3-Coder and Qwen3.5 397B repeated all 300; Gemma 4 repeated 140, with a median
   change of 0.11 nat and a largest of 10.7; Qwen3.5 122B repeated 27, median change 0.20 nat.
4. **In → out.** The same request at two times gives two log-probabilities, and so a margin
   difference.
5. **Assumptions.** The variation is small and symmetric; it does not change the model. The
   re-test shows that it is small for seven deployments but not for Gemma 4 and Qwen3.5 122B, and
   symmetric enough that a rate moved by at most 1.3 points on a 300-site sample.
6. **Silent failure.** Treating one served measurement as exact, so that a sign change near zero
   reads as a real difference between conditions.
7. **Symptom.** A margin that changes sign on re-scoring; margins that miss the bf16 grid.
8. **Test.** `tools/retest_api.py` (Table A2).
9. **Where.** The server; measured by `tools/retest_api.py`.
10. **Why it matters.** It joins rounding as the second reason why margins near zero are
    uncertain for served models. Rates are averages over thousands of sites, so they move
    little; single sites near zero are not reliable, and for Gemma 4 and Qwen3.5 122B single sites
    are not reliable even far from zero (Gemma 4's sign changes were at margins of 0.25–4.6 nats).

---

## 6. Quantized weights

1. **Technical.** Many served models run with weights stored in 8-bit floats (fp8) or 4-bit
   micro-scaled floats (mxfp4), not the 16-bit originals. The measured model is the quantized one.
2. **Simple.** A compressed photo of the model: the same picture, with some fine detail gone.
3. **Example.** Qwen3.5 27B, 122B and 397B: fp8; DeepSeek-V4.1-Flash: mxfp4; Gemma 4, Qwen3-Coder:
   bf16; OLMo 3: not stated (Table 1).
4. **In → out.** The original weights → compressed weights → a slightly different distribution.
5. **Assumptions.** Compression changes margins little compared with the differences between
   models.
6. **Silent failure.** Calling a result "Qwen3.5 397B" without saying "fp8 as served".
7. **Symptom.** None in the data; only the listing says it.
8. **Test.** —
9. **Where.** `registry.py` (`quantization`); every row's `dtype`.
10. **Why it matters.** A reader who downloads "Qwen3.5 397B" in bf16 is not testing the same
    model.

---

## 7. Mixture of experts: total and active parameters

1. **Technical.** A mixture of experts has many parameter blocks and uses a few per token. "397B
   with 17B active" stores 397 billion parameters and computes with about 17 billion per token.
2. **Simple.** A library of 397 books where each question is answered from the 17 relevant ones.
3. **Example.** The size axis of Figure 3 uses total parameters: Qwen3-Coder 30B (3B active),
   Qwen3.5 122B (10B), 397B (17B), DeepSeek about 550B (active not stated).
4. **In → out.** Two numbers per model; the figures use the total and mark mixtures of experts
   with open symbols.
5. **Assumptions.** Neither number alone is "the size"; both are reported (Table 1).
6. **Silent failure.** A scale trend drawn on total parameters that is really a trend in active
   parameters, or the reverse.
7. **Symptom.** Mixtures of experts sitting off a dense family's curve.
8. **Test.** —
9. **Where.** `registry.py` (`size_b`, `active_b`); `splits.MAX_SIZE_B` = 600, on total parameters.
10. **Why it matters.** Phase 3.3's scale analysis used dense models only. Here the largest models
    are all mixtures of experts, so "size" is no longer one number.

---

## 8. Instruct and thinking post-training

1. **Technical.** The API serves two post-trainings of OLMo 3 32B: Instruct (answer directly)
   and Think (reason at length before answering). They share one tokenizer (fingerprint
   `api-4d65…`) and one size. Under the raw-text protocol neither the chat template nor the
   reasoning mode is used: both are scored as plain language models.
2. **Simple.** Two students from the same school, one taught to answer at once, one taught to
   think aloud first. Here both just read the same page.
3. **Example.** OLMo 3 32B Instruct against Think (Tables 2–5):

   | | Instruct | Think |
   |---|---|---|
   | reversion with the table, `dom` / `blk` | 0.412 / 0.410 | 0.426 / 0.441 |
   | the table's effect, nats | +0.80 / +0.86 | +0.49 / +0.61 |
   | median examples to switch | 3.8 / 12.7 | 5.4 / 15.3 |
   | Arm B: empty generations | 334 of 780 | 0 of 780 |

   The intervals of the reversion rates overlap. The clearest differences are in Arm B (Think
   writes) and in the table's effect (larger for Instruct).
4. **In → out.** One base and two post-trainings give two sets of margins on identical sites.
5. **Assumptions.** Both come from the same OLMo 3 32B base model (the API describes them as one
   family whose member is chosen by reasoning effort), so the post-training is what differs.
6. **Silent failure.** Reading a difference as "reasoning helps" when no reasoning happened:
   the raw-text protocol never asks the model to think.
7. **Symptom.** —
8. **Test.** —
9. **Where.** `configs/dev_api.json`; the paired rows in the tables.
10. **Why it matters.** It is the cleanest within-family contrast in the run, and a question a
    reviewer will ask.

---

## 9. Same cells, different models

1. **Technical.** The served models met exactly the 3,030 sites of Phase 3.3's held-out run, with
   the same prompts, ladder, paraphrases and Arm B requests. Only the model and its serving
   changed.
2. **Simple.** The same exam paper, given to new students.
3. **Example.** The figure script refuses unless both runs scored the same sites: "both runs scored
   the same 1515 dom and 1515 blk sites, on 80 and 80 templates".
4. **In → out.** Two runs on one set of cells give per-model rates that can be put side by side.
5. **Assumptions.** The materials did not change (the materials hashes of both runs are recorded).
6. **Silent failure.** Comparing rates over different site sets: with 1,670 duplicate sites
   dropped and lexicon-specific sites, a different selection would change every rate.
7. **Symptom.** The check above failing.
8. **Test.** The figure script's first check; `write_plan_artifacts` refuses changed materials.
9. **Where.** `tools/paper_figures_api.py` (the site check), `configs/dev_api.json`.
10. **Why it matters.** It is what lets "with the table, the served models revert at 40–51% of
    sites where Phase 3.3's instruct models reverted at 40–53%" be a statement about models, not
    about materials.

---

## 10. Ending the turn: empty generations

1. **Technical.** In Arm B the prompt ends `Program:`. Under the raw-text protocol, OLMo 3's most
   likely next token was its chat end-of-turn token `<|im_end|>` (OLMo 3 7B: log-probability
   −0.34, so p ≈ 0.71; 32B Instruct: −0.09, p ≈ 0.91), so generation stopped at once with no text.
   At some prompts the same happened to Qwen3.5 397B.
2. **Simple.** Asked to write the program, the model said "done" before writing anything.
3. **Example.** Empty generations, of 780 per model (Table 5): OLMo 3 7B Instruct 290 (37%),
   OLMo 3 32B Instruct 334 (43%), OLMo 3 32B Think 0; Qwen3.5 397B 48 (6%), for the same reason:
   two of them, asked again with special tokens kept, generated only `<|im_end|>` (−0.46 and
   −0.70, against −1.08 and −0.83 for `" $"`). Phase 3.3's ten instruct models: 0 in 780 each. On
   the first Arm B prompt, Qwen3-Coder, Gemma 4, Qwen3.5 27B and DeepSeek began with `" $"`, the
   start of the program, at a log-probability of −0.001 or closer to zero.
4. **In → out.** An empty output → a lexicon failure → no site reached.
5. **Assumptions.** The protocol stays Phase 3.3's (raw text), so the result is comparable; it is
   reported, not repaired.
6. **Silent failure.** Reading OLMo 3's near-zero reach as "OLMo 3 cannot write 3DOM" rather than
   "OLMo 3 ends its turn under this prompt".
7. **Symptom.** `raw_output == ""`, `finish_reason: stop` after one token.
8. **Test.** The first-token check in [08 §2](08_issues_and_superseded_numbers.md).
9. **Where.** `p4/experiments/armb.py` (`build_prompt`, `score_armb_cell`); `p4/scoring/api.py`
   (`generate`).
10. **Why it matters.** Arm A is unaffected (a margin compares two continuations). For Arm B, a
    chat-formatted variant would be needed to measure OLMo 3 fairly: a design decision for the
    preregistration, not something to patch after seeing the data.

---

## 11. Reversion, the rule effect and adaptation, for served models

1. **Technical.** The same quantities as Phase 3.3: reversion = share of sites with M < 0; rule
   effect = mean M(table) − M(control); `k*` = examples until the margin first turns positive
   (Kaplan–Meier median over sites wrong at 0 examples).
2. **Simple.** How often the habit wins; how much the dictionary helps; how many examples it takes.
3. **Example.** With the table, the nine served models revert at 40.4–51.2% of sites (Phase
   3.3's instruct models: 40.0–52.9%); the table moves the margin by +0.34 to +0.86 nats; the
   median number of worked examples to switch is 1.7–15.3 ([00](00_complete_results.md)).
4. **In → out.** Rows → per-model rates with 95% template-cluster intervals.
5. **Assumptions.** As in Phase 3.3, plus §4–5: rounding and batching move margins near zero.
6. **Silent failure.** Comparing a served model's rate with a Phase 3.3 model's as if both were
   exact, when the difference is smaller than the near-zero share. And, for `k*`, taking an
   exported Kaplan–Meier median as exact: a rounding fault inherited from Phase 3.3 can move it
   to the next switch ([08 §6](08_issues_and_superseded_numbers.md#6-found-not-fixed-a-rounding-fault-in-the-kaplan-meier-median)).
7. **Symptom.** A median that changes when S is computed in exact fractions (6 of 18 here).
8. **Test.** The figure script checks every rate and effect against the run's own export.
9. **Where.** `p4/reporting/export.py`; `tools/paper_figures_api.py`.
10. **Why it matters.** They answer the question Phase 3.3 left open: is prior reliance a
    property of the 0.5–72B checkpoints it tested, or does it persist in newer and much larger
    models? It persists. With the table, the served models' rates (0.404–0.512, both grammars)
    lie inside the range of Phase 3.3's instruct models (0.400–0.529), up to about 550B, with
    every caveat of §1 and §4–7.

---

## Glossary of the new terms

| term | meaning |
|---|---|
| **served model** | a model computed on Research Computing's servers and reached through the ASU RC LLM API |
| **deployment** | one running copy of a served model: a served name plus a server fingerprint |
| **pin** | the deployment recorded at `prefetch`, which every answer must match |
| **gateway** | the API's front door, which routes each request to a deployment and queues it fairly |
| **`system_fingerprint`** | the server's identifier of its build and configuration, in every answer |
| **bf16** | a 16-bit float with 8 bits of precision; rounds a number near 20 to the nearest 1/8 |
| **fp8, mxfp4** | 8-bit and 4-bit formats for stored weights |
| **mixture of experts (MoE)** | a model that uses a few of many parameter blocks per token; total vs active parameters |
| **tie** | a margin of exactly 0: neither spelling preferred |
| **batching noise** | variation in a log-probability caused by the batch a request was computed in |
| **empty generation** | Arm B output with no text: the model ended its turn first |
| **cell workers** | how many cells of one model the pipeline scores at once (`P4_API_CELL_WORKERS`) |
| **development model** | a model in `DEV_MODELS`: its data may shape the design, so it cannot be held out |
