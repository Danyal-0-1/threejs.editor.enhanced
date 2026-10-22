# 06 — Knowledge check (the Sol pipeline)

No answers are given. Each section names where its answers can be found.
Questions marked ✎ need pen and paper; ⌨ means run something.

---

## A. The split, the freeze and the unlock (`01 §2–4`, `splits.py`)

1. For each cell, give its class and say whether `dev run` may score it:
   - `dom × d50s2 × Qwen2.5-Coder-1.5B-Instruct`
   - `dom × d75s2a × Qwen2.5-Coder-0.5B`
   - `blk × d25s1 × Qwen2.5-Coder-0.5B`
   - `blk × d50s3 × deepseek-coder-1.3b-base`
   - `dom × d50s1 × Qwen2.5-Coder-7B`
2. Why does `build_plan` call `enforce_config` *before* classifying a single
   site? What would be lost if it counted held-out sites first "just to size the run"?
3. Name every item `frozen_drift` compares. For each one, describe a realistic way it
   could drift on Sol without anyone intending to change the analysis.
4. The first version checked the source only inside `write_unlock`. Construct a
   sequence of events in which held-out cells are scored by code that was never frozen.
5. Why is `blk` × a held-out lexicon called HELDOUT-WEAK-FAMILY and not HELDOUT?
   What exactly can a positive H4 result on those cells support, and what can it not?
6. Why is H4's criterion C3 NOT TESTABLE, rather than "failed"?
7. ⌨ In a scratch results root, freeze a fake development run, then run
   `heldout run` before and after `heldout unlock`. Which exit code does each give,
   and what does each message say?
8. Under deviation D10, which stage may score `Qwen/Qwen2.5-72B-Instruct`, on how many GPUs,
   and through which `submit.sh` profile? What does plain `heldout_eval` do with it?
9. A held-out model is first pinned *after* the freeze. What does `frozen_drift` report
   for it? Why does README §8 ask for every held-out model to be prefetched before
   freezing, and which models did that concern on 2026-10-07?
10. D10 was decided after the development run. What makes it legitimate as a deviation,
    and what would have made it illegitimate?

## B. Demonstrations (`01 §5`, `demos.py`)

1. State the three conditions under which a demonstration leaks.
2. Every `dom` program starts with `(function(){ $S('`. Why would a rule that
   rejects any demonstration starting with a site's prefix reject *all* of
   them for some sites? How does `common_opening` fix that without letting a real leak through?
3. Why must the ladder be nested? What confound appears if the 8-shot set is
   not a superset of the 4-shot set?
4. On the development plan, the old "first 32 templates" rule would leak for 177 of 400
   sites. In which direction does leakage bias `k*`, and why?
5. Why does `for_site` *raise* when it cannot find enough clean
   demonstrations, instead of running a shorter ladder?

## C. `k*` and survival (`02 §3–4`, `kstar.py`)

1. ✎ Margins at 0, 1, 2, 4, 8 shots are −3.0, −2.0, −0.5, +1.5, −0.2. Give
   `k*`, `censored`, `nonmonotone`, `recrossed_down` and `sustained_k`.
2. ✎ The same, for +0.4, −0.6, −0.1, +0.2, +0.9.
3. ✎ Six sites have `k*` = 0, 0, 2.5, 5.0, censored at 8, censored at 8.
   Compute the Kaplan–Meier median for ALL_SITES and for INITIALLY_WRONG, the
   censoring rate of each, and the median among crossers. Which of these numbers
   should a paper report, and which must it never report alone?
4. Why does "already correct" give `k* = 0` and not `None`? What did treating it
   as `None` do to the old headline?
5. In the smoke, the ALL_SITES median is 0. Is that a bug? What does it tell you,
   and what does it not?
6. 237 of 240 audited curves were non-monotone. Give two mechanisms that could
   make adding a correct example *lower* the margin.

## D. Uncertainty (`02 §5–6`, `analysis.py`, `power.py`)

1. ✎ Templates tA (d = 2) and tB (d = −1) are resampled as [tB, tB, tA]. What
   should the paired mean be? What would pairing by `site_id` alone give?
2. Why is the template, and not the site, the resampling unit? Give a concrete
   reason that two sites from the same template are not independent.
3. Why is no interval reported below 8 clusters? What would a percentile
   interval over 5 clusters look like?
4. ✎ Development shape: 80 templates × 10.65 sites, d = 0.18, sd = 1.39. The power
   is 0.97 at ICC 0 and 0.61 at ICC 0.2. Compute the design effect and the effective
   sample size for both.
5. Why must the power pilot use development rows only? What would go wrong if
   the held-out sample size were chosen with held-out data?
6. ✎ Holm with p = {C1: 0.012, C2: 0.030}. Which criteria pass at α = 0.05?
7. ✎ Scores (5, 4, 4, 4, 1) with labels (1, 1, 0, 0, 1). Compute AP with tie groups.
   Compute the lowest and highest AP the pre-D9 code could return, depending on row order.
   Then compute the expected precision@2 and precision@4.
8. ✎ Is the tie-grouped AP the *average* of the old AP over all orders of the tied rows?
   Check on scores (3, 2, 2, 1), labels (1, 0, 1, 0). Is the new precision@k such an average?
9. ✎ The rule-effect pilot has m = 44.84 rows per template and an ICC of 0.252. Compute the DE
   and n_eff at T = 80 and at T = 320. Show that n_eff can never exceed T / ICC however many
   rows a template has. What does that say about adding lexicons or models, compared with
   adding templates?
10. Before D9 the power report said 0.994 for the rule effect at 80 templates. Which
    assumption produced that number? What does the pilot say about it?
11. H4 criterion 1's smallest detectable AUROC at T = 80 is 0.62–0.63 for every ICC from
    0 to 0.2. Explain why clustering barely moves it, using the criterion's definition.

## E. Measurement (`02 §1–2`, `margins.py`)

1. ✎ A single-token divergence has bf16 logits 11.3125 and 10.6875. What is the
   native margin? Why is it a multiple of 1/16? What could the true margin be?
2. When is `M` *not* just a difference of two logits, so that the 1/16 grid argument fails?
   Use site t004 as the example.
3. Why does `k_common` (302) differ from the number of prefix tokens (303) for site
   t000? What would a scorer that assumed the prefix ends on a token boundary get wrong?
4. Give one case for each refusal: `IdenticalCandidates`, `ZeroLengthSpan`,
   `NoContext`. Why is raising better than returning 0.0?
5. The `norule` prompt is 237 tokens and `rule` is 298. Describe a result that
   would look like rule-following but is explained by length. Which control rules it out?

## F. Crash safety and provenance (`03 §4.7–4.8`, `shards.py`, `pipeline.py`)

1. A job receives SIGUSR1 while scoring site 30 of a 64-site cell. Trace what
   happens to that cell, the job manifest, the exit code, and the next submission.
2. A shard exists but its marker's sha256 does not match. What is the cell's
   state, and what does the next run do with it?
3. Why does `clean_temp` delete only temp files older than 15 minutes?
4. Explain why `.tmp.<pid>` is not a unique name on Sol. What happened in the
   concurrency test when the old scheme was used?
5. Before P33-012, what did resubmitting one failed array index
   (`sbatch --array=2 …`) do, and why did it *look* successful?
6. Why did running the Phase 3.2 tests on Sol threaten every later GPU job
   (P33-011)? Why is "make the writer idempotent" a better fix than "stop
   checking materials"?
7. Why does `sol.env` unset `P33_FAKE`? Describe the failure it prevents.
8. ⌨ Run the Sol test suite with `CUDA_VISIBLE_DEVICES=""` with and without
   `--cpu-node`. Explain the difference in exit codes.
9. Why could running `p33 status` once make the next `dev_freeze` refuse a complete
   development run (P33-017)? What does "started" mean for an experiment, and
   why must a status command never create anything?
10. You get Llama access after the freeze and re-run prefetch. Under the old
    behaviour, what could happen to the *other* ten models' pins, and what would
    every held-out command then do? What does `--repin` exist for?
11. An analysis revision regenerated `csv/`, `plots/` and `reports/` from saved
    measurements. Which files must be byte-identical before and after? How does
    `analysis_revision.py record` show that no measurement changed?
12. The Sol CPU-test job sourced `sol.env`, and the runner used `setdefault` for its
    results root. Trace what the tests then wrote, and where. Why did no test fail?
13. `RUN_SUMMARY.md` on Sol said "reports/ — 0 files". Why? Why is counting against a
    registry better than counting whatever is in the directory?

## G. Hypotheses (`01 §12–15`, `h4.py`, `h5.py`, `armb.py`, `h2.py`)

1. Write the H4 risk score and label. Why is the base model's margin used to
   predict the *instruct* model's reversion, rather than the instruct model's own margin?
2. Why is the identity baseline's AUROC exactly 0.5 on the eligible set? What
   does criterion C1 reduce to, and why is `terminal_rate` the more honest competitor?
3. A targeted repair changes 3 roles and removes 12 reversions. A random arm
   changes 3 roles and removes 6. Global changes 14 roles and removes 30. Rank
   them by benefit per symbol. Which control check could still invalidate the targeted result?
4. What does the H5 IR proof quantify over, and how does `test_ir_proof_can_fail`
   show the proof is not vacuous?
5. In Arm B, a model reaches 20% of sites and reverts at 50% of those it reaches.
   Another reaches 80% and reverts at 25%. Which is "better"? Why is the product
   alone misleading?
6. Why would deriving H2's prior-strength levels from the outcome margins make
   any interaction test circular?

## H. Interpretation and status

1. Which Phase 3.3 headline numbers are withdrawn, which are corrected, and which still stand?
2. The smoke's rule effect is +0.182 with interval [−0.433, +0.911]. Write the
   strongest sentence you are entitled to write about it, and one sentence you are not.
3. List everything that has been run on Sol. List everything a reviewer could
   still call "not yet shown".
4. If a development result looks surprising after the freeze, what are your
   options? Why is "edit the code and re-run held-out" not one of them?
5. Name three things this pipeline could still get wrong that no test here
   would catch.
6. After D9, which development numbers changed and which did not? Why did the risk
   score's AP stay exactly the same while the identity baseline's moved?
7. D10 tests H4 on models up to 72B with a calibration frozen on 0.5B and 1.5B. Which H4
   quantities should transfer, and which may degrade? Why are C1 and C2 still fair tests?
8. The development rule effect has 1 interval of 32 that excludes zero. Write the
   strongest sentence you are entitled to write about the rule effect, and one you are not.
