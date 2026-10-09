# 01 — Theory and research design (the Sol pipeline)

> **Companion documents.**
> [`phase3/phase3_explained/01`](../../../phase3/phase3_explained/01_theory_and_research_design.md)
> defines the core concepts: surface familiarity, reversion, the collision
> taxonomy, the hurdle, canonical IR and falsification.
> [`phase3_2/phase3_2_explained/01`](../../phase3_2_explained/01_theory_and_research_design.md)
> adds grammar families, the delta family, collision density, strata and the
> first-divergent-token margin.
> **Those are not repeated here.** This document covers only what the Sol
> pipeline adds or corrects. Every new concept gets the same ten points.

The ten points, used for every concept:

| # | Point | What it answers |
|---:|---|---|
| 1 | Technical | the precise definition |
| 2 | Simple | the plain version |
| 3 | Example | a real case from this repository |
| 4 | Inputs → outputs | what goes in and what comes out |
| 5 | Assumptions | what it depends on |
| 6 | Silent failure | what can go wrong without any error |
| 7 | Symptom | how that failure would look in the results |
| 8 | Test | which test catches it |
| 9 | Where | where it lives in the code |
| 10 | Why it matters | why it matters scientifically |

---

## 1. What changed in the research position

The science is the same as Phase 3.3: **H4** (predict the exact risky sites)
is the headline, **H5** (repair them) goes with it, **extinction curves** are
the scientific result, and **H2** is secondary. What changed is what the
evidence can be trusted for:

| | Phase 3.3 (laptop) | Sol pipeline |
|---|---|---|
| headline `k* ≈ 5–7 shots` | reported | **withdrawn**: leakage plus two definition errors |
| rule-effect intervals | 1 of 4 excluded zero | **all 4 include zero**: bootstrap multiplicity fixed |
| `blk` | "the held-out grammar family" | **inspected before the freeze**, so not held out |
| development / held-out | a promise in a document | **enforced in code**, with a freeze and an unlock |
| crash safety | one JSON at the end | atomic shards, resume, byte-identical merge |
| provenance | model id only | revision, tokenizer, prompt, demonstration and source hashes on every row and job |
| margin precision | bf16 logits | fp32 output head |
| no-rule control | ~a third shorter than the rule prompt | plus a **length-matched** control |

Nothing in this table is a new result about models. It is a list of reasons
the old results could not support the claims made from them.

---

## 2. The registered split, enforced in code

1. **Technical.** Every (family, lexicon, model) cell has a class:
   DEVELOPMENT, HELDOUT, HELDOUT-WEAKENED, HELDOUT-WEAK-FAMILY, EXPLORATORY or
   FORBIDDEN. A stage may touch only the classes it is allowed, and the check
   runs **before** any site is enumerated, any model is loaded or anything is
   scored.
2. **Simple.** Practice roads and exam roads are different roads, and the car
   physically refuses to drive onto an exam road during practice.
3. **Example.**
   - `dom × d50s1 × Qwen 0.5B` is DEVELOPMENT.
   - `dom × d75s1a × Qwen 0.5B` is HELDOUT (mapping).
   - `blk × d50s1` is EXPLORATORY.
   - `blk × d75s1a` is HELDOUT-WEAK-FAMILY.
   - `Qwen 3B` is HELDOUT-WEAKENED.
   - `Qwen 7B` is a HELDOUT model since deviation D10 (2026-10-07). It was FORBIDDEN under
     the old 3B gate.
   - A model above 72B is FORBIDDEN in every stage.
4. **Inputs → outputs.** (family, lexicon, model, stage) → a `CellClass`, or
   `SplitViolation`.
5. **Assumptions.** The registry lists every model with its size and pairing.
   The lexicon split is the preregistered one (`d25s1 d25s2 d50s1 d50s2` for
   development; `d25s3 d50s3 d75s1a d75s2a d75s3a` held out).
6. **Silent failure.** A development command that *enumerates* held-out sites
   "just to count them" has already looked at held-out material. So does a
   legacy script that bypasses the check.
7. **Symptom.** Nothing visible. Held-out numbers would look like confirmation
   and would not be.
8. **Test.**
   - `test_registered_split_classification`
   - `test_dev_stage_refuses_a_heldout_mapping`
   - `test_plan_refuses_before_enumerating_any_heldout_site`, which spies on the
     classifier and asserts 0 calls before the refusal
   - `test_run_ids_physically_separate_stages`
9. **Where.** `p33/splits.py`: `classify`, `check_access`, `enforce_config`.
   The check is called first in `pipeline.build_plan`, and the legacy wrappers
   `scripts/run_arm_a.py` and `run_primary.py` call `enforce_config` too.
10. **Why it matters.** A held-out test is worth exactly as much as the
    guarantee that it was not used during development. A promise in a
    document is not a guarantee; a refusal in code is.

---

## 3. The freeze and the unlock

1. **Technical.**
   - `DEV_FREEZE.json` fixes everything the held-out stage will use. It is
     written once, made read-only and given a sha256 sidecar. Its contents:
     the risk formula, Platt calibration, decision thresholds, prompt hashes,
     exclusion rules, analysis settings, seeds, config hash, materials hashes
     for every lexicon, source hashes, git state and model pins.
   - `HELDOUT_UNLOCK.json` can be written only when the exact phrase is typed,
     the freeze is intact, and the source, the materials and every frozen model
     pin still match it.
   - Every later held-out access re-checks the same things.
2. **Simple.** Write the grading rules in ink, then sign to open the envelope.
   If anyone touches the ink afterwards, the envelope refuses to open again.
3. **Example.** In the CLI rehearsal (`AUDIT.md` §6):
   - a second `dev freeze` returned `REFUSED … a freeze is immutable` (exit 2);
   - `heldout unlock --confirm "yes"` returned `REFUSED: unlock requires the exact phrase` (exit 2);
   - `heldout run` before the unlock returned `REFUSED: held-out cells are locked` (exit 2).
4. **Inputs → outputs.** A COMPLETE development run → `DEV_FREEZE.json`.
   That plus the phrase → `HELDOUT_UNLOCK.json` → permission for held-out cells.
5. **Assumptions.** The code that runs on held-out data is the code whose
   hashes were frozen. The materials (lexicons, templates, terminal table)
   are byte-stable unless their content changes. That stability needed defect fix
   P33-011.
6. **Silent failure.** The first version checked the source only **at
   unlock**, and never the materials or the model pins. Code edited *after* the
   unlock, or a model re-pinned to a new revision, still scored held-out cells.
7. **Symptom.** A held-out result produced by an analysis that was never
   frozen, which is exactly the forking-paths problem preregistration exists
   to prevent.
8. **Test.**
   - `test_freeze_cannot_be_written_twice`
   - `test_tampered_freeze_is_detected`
   - `test_unlock_needs_the_exact_phrase`
   - `test_unlock_refuses_if_source_changed_since_freeze`
   - `test_heldout_access_refuses_if_source_changes_after_unlock`, new in the final pass
   - `test_a_model_repinned_after_the_freeze_is_refused`, new in the final pass
   - `test_unlock_is_void_if_the_freeze_is_later_tampered`
9. **Where.**
   - `p33/freeze.py`: `build_payload`, `freeze`.
   - `p33/splits.py`: `write_freeze`, `load_freeze`, `write_unlock`, `load_unlock`, `frozen_drift`.
10. **Why it matters.** Preregistration converts "we found X" into "we
    predicted X and then observed it". That conversion is only as strong as
    the barrier between analysis choices and held-out data.

---

## 4. Contamination: what `blk` lost

1. **Technical.** A held-out *grammar family* must be one whose outcomes no
   one has seen. `blk × d50s1` was scored twice before the freeze: Phase 3.2's
   balanced Arm A (272 sites) and Phase 3.3's primary run (60 sites). The
   preregistration's own §8 reports "`blk ≈ dom`". So `blk` is no longer
   unseen.
2. **Simple.** We drove on that exam road during practice. It can still be a
   practice exam, but it is not the exam.
3. **Example.**
   - `blk × {d25s1, d25s2, d50s1, d50s2}` is EXPLORATORY-CONTAMINATED. It is refused unless
     `allow_exploratory`, and labelled if allowed.
   - `blk × {d25s3, d50s3, d75*}` is HELDOUT-WEAK-FAMILY: the grammar has been seen, but these
     mappings have not.
4. **Inputs → outputs.** The scoring history → a class change, recorded as preregistration
   deviation D1.
5. **Assumptions.** Inspection is what contaminates, not just tuning. Seeing
   that `blk` behaves like `dom` is already information.
6. **Silent failure.** Reporting "H4 generalises to an unseen grammar" from
   `blk` held-out cells.
7. **Symptom.** A cross-family claim a reviewer dismantles in one sentence:
   *"you looked at that family before freezing."*
8. **Test.**
   - `test_blk_is_never_labelled_a_heldout_grammar`
   - `test_contaminated_cell_needs_explicit_permission`
   - `test_criteria_c3_not_testable_without_a_valid_grammar`
9. **Where.** `splits.CONTAMINATED_FAMILIES`, `APPROVED_NEW_FAMILIES = frozenset()`
   (none approved and none invented), and `h4.criteria`, which emits C3 as NOT TESTABLE.
10. **Why it matters.** H4 criterion C3 ("AUROC ≥ 0.65 on the held-out grammar
    family") is **NOT TESTABLE** until a new family is approved, designed and
    frozen. H4 can be supported on held-out **mappings** and **models** only.

---

## 5. Demonstration leakage

1. **Technical.** A demonstration leaks for a target site if any of these holds:
   - it comes from the same template;
   - it is the identical program;
   - it replays the site's decision prefix beyond the family's fixed opening, `(function(){ $S('`.
2. **Simple.** The practice packet must not contain the exam question.
3. **Example.**
   - **The old ladder:** it used templates t000–t031 for every site, and **82 of the 120** Phase 3.3
     extinction sites came from those templates.
   - **The real development plan now:** 400 primary sites and 2,800 demonstration
     sets (7 rungs each), **0 leaks**. The old rule would have leaked for **177
     of these 400** sites.
4. **Inputs → outputs.** (site, the rendered pool for its own family × lexicon, a seeded
   order) → the first *n* clean demonstrations, a nested ladder, and hashes.
5. **Assumptions.**
   - Demonstrations should still *teach the mapping*: they contain the reassigned spellings, which is
     the dose.
   - The ladder is nested: the k-shot set is a prefix of the (k+1)-shot set. So
     the dose is the only thing that varies along a curve.
6. **Silent failure.** A rule so strict that it rejects every demonstration,
   because every `dom` program starts with a first site's prefix. That forces
   short ladders or silent fallbacks.
7. **Symptom.**
   - **With leakage:** `k*` biased downward, because the curve measures copying.
   - **With an over-strict rule:** ladders that quietly stop short.
8. **Test.**
   - `test_old_first_32_pool_leaked_the_target`
   - `test_demonstrations_never_contain_the_target`
   - `test_replayed_decision_prefix_is_a_leak_but_the_fixed_opening_is_not`
   - `test_ladder_is_nested_and_hashed`
   - e2e `test_no_demonstration_leaks_in_any_ladder_row`
   - `score_primary_cell` itself **raises** if `demos.audit` finds a leak.
9. **Where.** `p33/demos.py`: `is_leak`, `for_site`, `audit`, `common_opening`, `pool_order`.
10. **Why it matters.** The extinction curve claims to measure *how much
    evidence it takes to override a prior*. Showing the answer measures
    something else entirely.

---

## 6. The extinction threshold as a survival time

1. **Technical.**
   - **The event** is "the margin first becomes ≥ 0", and time is the number of shots.
   - `M(0) ≥ 0` gives `k* = 0`.
   - Otherwise `k*` is the first upward crossing, linearly interpolated between
     the two rungs.
   - A curve that never crosses is **right-censored** at the top rung.
   - A curve that crosses and later drops is **not** censored.
   - The summary is a Kaplan–Meier median, reported for two labelled populations:
     ALL_SITES and INITIALLY_WRONG.
2. **Simple.** "How many practice trips until it turns right?", where "more
   than 32" is a real answer and not a blank.
3. **Example** (the smoke, 6 sites):
   - k* values: 0, 0, 0, 1.71, 6.79, censored.
   - ALL_SITES KM median: **0**.
   - INITIALLY_WRONG KM median: **6.79**.
   - The diagnostic "median among crossers" is 4.25. It drops the censored site, so it is lower.
4. **Inputs → outputs.** (ladder, margins per rung) → `KStar`, then a set of KStars → `KMSummary`.
5. **Assumptions.**
   - Censoring is *non-informative* given the population label. That is debatable: the
     censored sites are exactly the strongest priors. This is one more reason to report
     the censoring rate next to every median.
6. **Silent failure.** The Phase 3.3 code did three wrong things:
   - It treated already-correct sites as missing: 84 of 125 got `k* = None`.
   - It took a later re-crossing for 41 of them.
   - It marked 16 curves as both crossed and censored.
7. **Symptom.** A threshold that looks like a property of the model but is a
   property of the bookkeeping.
8. **Test.**
   - `test_kstar_zero_when_already_correct`
   - `test_kstar_already_correct_at_exactly_zero_margin`
   - `test_kstar_first_crossing_interpolated`
   - `test_kstar_no_crossing_is_censored`
   - `test_crossed_then_dropped_is_not_censored`
   - `test_kaplan_meier_hand_example`
   - `test_median_among_crossers_is_labelled_diagnostic_and_drops_censored`
9. **Where.** `p33/kstar.py`: `compute`, `kaplan_meier`, `km_from_kstars`.
10. **Why it matters.** With about half the sites already correct, the
    ALL_SITES median is 0, which is true and useless. The actionable number is
    "how many examples, for sites that start wrong", and it is only honest if
    "never within 32" is counted.

---

## 7. Non-monotone curves and the sustained threshold

1. **Technical.**
   - **`nonmonotone`** is set if the margin ever decreases between consecutive rungs.
   - **Crossing counts:** the number of up-crossings and down-crossings.
   - **`sustained_k`** is the first rung after which M never returns below 0.
2. **Simple.** The needle wobbles. "The first time it pointed right" and "when
   it started *staying* right" are different questions.
3. **Example.**
   - In the Phase 3.3 audit, **237 of 240** curves were non-monotone.
   - Smoke site `t011`: margins −2.57, −1.70, +0.71, +0.41, −1.02 at 0, 1, 2, 4 and 8 shots. First crossing at
     ≈ 1.71, one down-crossing, and `sustained_k = None`.
4. **Inputs → outputs.** The same as §6, plus four extra fields per curve.
5. **Assumptions.** The rungs are coarse (0, 1, 2, 4, 8, 16, 32). Interpolation between rungs is a
   convention, not a measurement.
6. **Silent failure.** Treating a first crossing as stable when the curve
   falls back. The threshold then over-states how easily the habit breaks.
7. **Symptom.** k* estimates that do not replicate across seeds or demonstration orders.
8. **Test.** `test_nonmonotone_flag_and_sustained_crossing`.
9. **Where.** `kstar.compute`. The summary columns are in `kstar_survival.csv`
   (`share_nonmonotone`, `share_recrossed_down`).
10. **Why it matters.** It tells the reader how much of an extinction claim
    survives the noise in a single curve.

---

## 8. The template is the unit of evidence

1. **Technical.**
   - Sites are nested in templates, so uncertainty comes from a
     **template-cluster bootstrap**: resample templates with replacement,
     B = 2000, seed 20261002.
   - Duplicates keep their multiplicity: each copy is tagged `_draw`, and pairs
     are keyed on (`_draw`, `site_id`).
   - There is **no interval below 8 clusters**.
   - Families are never pooled.
   - Holm correction is applied across the H4 criteria.
2. **Simple.** Twenty siblings are not twenty independent witnesses. Resample
   whole families, and when a family is drawn twice, count it twice.
3. **Example.**
   - **The hand example:** templates with paired effects tA = 1 and tB = 3, drawn
     [tA, tA, tB], should average **5/3**. The old pairing by `site_id` returned **2.0**.
   - **Consequence:** every Phase 3.3 rule-effect interval widened. For instance,
     0.5B base `dom` went from [+0.029, +0.326] to **[−0.012, +0.370]**.
4. **Inputs → outputs.** (rows, a statistic, the unit) → an `Interval`, or `None`
   when there are too few clusters or the point statistic is undefined.
5. **Assumptions.** Templates are exchangeable, and the template is the right level. In this design,
   `template` means the abstract program, shared across lexicons.
6. **Silent failure.** Pairing inside a resample by `site_id` turns sampling
   *with* replacement into sampling *without* it, without any error.
7. **Symptom.** Intervals too narrow, and a "significant" effect that is not.
8. **Test.**
   - `test_bootstrap_keeps_duplicate_cluster_weight_hand_example`
   - `test_old_dict_pairing_collapsed_the_duplicate`
   - `test_no_interval_below_eight_clusters`
   - `test_holm_hand_example`
9. **Where.** `phase3_2/src/phase3_2/analysis.py`: `_draw_rows`, `cluster_bootstrap`,
   `paired_rule_effect`, `holm`.
10. **Why it matters.** A claim's uncertainty must be computed at the level
    where the evidence is actually independent. Here that is the program, not
    the character position.

---

## 9. The length-matched control

1. **Technical.** `norule_lenmatched` is the no-rule prompt padded with neutral
   filler until its token count, **under each model's own tokenizer**, reaches
   the rule prompt's.
2. **Simple.** Compare the rulebook with a blank booklet of the same
   thickness, not with a thin pamphlet.
3. **Example (smoke, Qwen tokenizer).**

   | Condition | Tokens | Characters |
   |---|---:|---:|
   | rule | 298 | 1,527 |
   | norule | 237 | 1,014 |
   | norule_lenmatched | 307 | 1,413 |

   Rule effect vs norule is +0.182; vs the length-matched control it is +0.291. Both
   intervals include zero, and n = 12 cannot separate them.
4. **Inputs → outputs.** (phi, a token counter) → a `PromptBundle` with its hash.
5. **Assumptions.** The neutral filler carries no mapping information. It
   could still carry *some* signal, which is why it is a control and not proof.
6. **Silent failure.** Attributing a context-length effect to rule-following.
7. **Symptom.** A rule effect that shrinks or flips against the
   length-matched control.
8. **Test.** `test_norule_lenmatched_reaches_rule_token_count`.
9. **Where.** `phase3_2/prompts.py`: `norule_lenmatched`, `bundle`; scored in
   `pipeline.score_arm_a_cell`.
10. **Why it matters.** "Specification-following" is the claim. Length is the
    cheapest alternative explanation, so it is controlled directly.

---

## 10. Measurement precision: the fp32 output head

1. **Technical.**
   - The decoder runs in bf16, but the final projection to the vocabulary is recomputed in
     fp32 from the last hidden state, using an fp32 copy of the output matrix.
   - It is disabled automatically for models with logit soft-capping or
     scaling.
2. **Simple.** Read the speedometer with enough decimal places to tell
   whether you are above or below zero.
3. **Example.**

   | Site | fp32 head | native bf16 |
   |---|---:|---:|
   | t000 | +0.6473 | +0.6250 (exactly 10/16) |
   | t002 | −4.4436 | −4.4375 (−71/16) |

   Across three development sites, the per-candidate log-probabilities agreed within 0.005–0.042 nats,
   with the same sign of M every time.
4. **Inputs → outputs.** (token ids, the span) → fp32 log-probabilities for that span.
5. **Assumptions.** The hidden state is accurate enough; only the last
   projection is quantised in a way that matters for a difference of two
   logits.
6. **Silent failure.** Near-zero margins get a sign decided by rounding.
7. **Symptom.** Reversion rates that shift with the dtype, and inflated
   ties. The QC report counts ties: 0 in the smoke.
8. **Test.**
   - A real-weights validation on three development sites (disclosed in `AUDIT.md` §5, not a unit test).
   - `fp32_head` and `tie` columns on every row.
9. **Where.** `phase3_2/margins.py`: `TokenScorer.__init__`, `_logprobs_rows`.
10. **Why it matters.** The outcome is a **sign**. A measurement whose
    precision is coarser than the effect around zero decides the result by
    rounding.

---

## 11. Provenance and crash safety as validity

1. **Technical.**
   - Each finished cell is written atomically: a unique temp file, fsync, then
     `os.replace`. A marker file carries the shard's sha256 and row count.
   - A cell's state is `done`, `failed`, `corrupt` or `missing`.
   - Merging is deterministic.
   - Each job writes a `JobManifest`: git state, Slurm identity, package
     versions, GPU, the HF environment, source and materials hashes, model
     revisions, tokenizer fingerprints and prompt hashes.
2. **Simple.** A logbook with sealed pages. You can always tell which pages
   are finished, and finished pages cannot be half-written.
3. **Example.** A real SIGTERM sent to a running fake-scorer job left its
   manifest at `INTERRUPTED, signal 15`. A real SIGUSR1, sent once 7 cells were
   written, made a task exit 4. Rerunning that one task completed it, and the
   merged 960 rows were byte-identical to an uninterrupted run.
4. **Inputs → outputs.** Cells → shards, markers and manifests → merged JSONL,
   `merged/<exp>.status.json` and `run_completeness.csv`.
5. **Assumptions.** `os.replace` is atomic on the target filesystem. This is
   standard POSIX behaviour, but Sol's filesystems were not tested from here.
6. **Silent failures, found and fixed in the final pass:**
   - Every test run rewrote nine tracked lexicon files (P33-011).
   - A single resubmitted array task scored nothing (P33-012).
   - Concurrent array tasks could interleave a plan file (P33-014).
   - A plain `status` created an empty Arm B directory, so `validate`, and with
     it the freeze, refused a complete development run (P33-017).
   - Any of these would have produced a refused resume, an unexplained gap, or a
     run that never completes.
7. **Symptom.** A PARTIAL run that looks COMPLETE, or a COMPLETE run that
   cannot be reproduced.
8. **Test.**
   - `test_resumed_output_equals_uninterrupted_output`, a byte-for-byte check
   - `test_concurrent_writers_never_share_a_temp_file`
   - `test_array_task_i_scores_model_i_even_when_resubmitted_alone`
   - `test_materials_writer_is_idempotent_and_atomic`
   - `test_merge_is_byte_deterministic`
   - `test_status_is_read_only_so_validate_still_passes`
9. **Where.** `p33/shards.py`, `p33/provenance.py`, `config.atomic_write_text`,
   `pipeline.run`.
10. **Why it matters.** A number you cannot regenerate from recorded inputs is
    an anecdote. On a shared cluster with time limits, interruption is the
    normal case, not the exception.

---

## 12. H4 as operationalised

1. **Technical.**
   - **Risk** is `−M_seq(base, rule)`. **Label** is `1` if `M_seq(instruct, rule) < 0`.
   - Rows are paired by `site_id` within each registered base/instruct pair.
   - **Metrics:** AUROC, AUPRC, precision@{10, 50}, Brier score, ECE (10 bins), calibration
     slope and intercept.
   - **Mandatory baselines:** identity, length, program NLL and token count. An
     exploratory baseline, `terminal_rate`, is cross-fitted leave-one-template-out.
   - **Frozen on development data:** a Platt calibration and a Youden threshold.
   - **Criteria:**
     - C1: ΔAUROC vs identity ≥ 0.10, with the interval above 0.
     - C2: ΔAUROC vs length ≥ 0.05, with the interval above 0.
     - Holm correction over C1 and C2.
     - C3: NOT TESTABLE.
2. **Simple.** Can the base model's hesitation at an intersection predict
   where its instruction-tuned sibling will take the wrong turn?
3. **Example.** Not run in the smoke, because it needs a base **and** an instruct model. The
   e2e test runs it on the fake scorer.
4. **Inputs → outputs.** Arm A rule-condition rows → an H4 table → metrics with intervals →
   criteria.
5. **Assumptions.** Pairing is by `site_id`, which is defined on characters, so
   a pair need not share a tokenizer. It does for the Qwen pairs; the other pairs
   were not checked here, and each row records its own `tokenizer_id`. The base
   margin is available before the instruct model is ever run.
6. **Silent failure.** The identity baseline is **constant** on the
   SEMANTIC-only eligible set, because every site has correct ≠ competitor. Its AUROC is
   therefore exactly 0.5, and C1 quietly reduces to "AUROC ≥ 0.60".
7. **Symptom.** A "beats the identity baseline" claim that beats a coin.
8. **Test.**
   - `test_identity_baseline_is_constant_on_semantic_sites`
   - `test_h4_metrics_against_hand_values`
   - `test_calibration_of_a_fitted_model_is_identity`
   - `test_single_class_labels_are_not_estimable_not_a_crash`
   - `test_build_table_pairs_base_with_instruct_on_site`
9. **Where.** `p33/h4.py`: `build_table`, `evaluate_group`, `criteria`. The calibration is
   in `freeze.build_payload`.
10. **Why it matters.** H4 is the claim that the vulnerability is
    *predictable at the site level*. A degenerate baseline would make it look
    stronger than it is, so the degeneracy is stated in every report
    (deviation D6) and a stronger exploratory competitor is added.

---

## 13. H5 as operationalised

1. **Technical.**
   - For each (family, lexicon, instruct model) there are three kinds of repair arm:
     - **targeted:** the 3 remapped roles with the highest mean base-model risk;
     - **random:** 3 roles per seed, seeds 1–5;
     - **global:** every remapped role.
   - Each repair takes its new spelling from the `beta` lexicon and respects the I7 overload group.
   - Each repair must pass an exhaustive IR proof: 142 programs × 2 families = 284
     re-parses with an unchanged canonical IR.
   - **Outcome:** reversions avoided per symbol changed. The control is that
     low-risk sites may degrade by at most 0.02.
2. **Simple.** Repaint only the dangerous signs, and check whether that beats
   repainting random signs or all of them, per sign repainted.
3. **Example.** The e2e and analysis tests prove every arm IR-preserving.
   `test_ir_proof_can_fail` shows the proof is not vacuous: break one family's
   renderer and it fails.
4. **Inputs → outputs.** Merged Arm A for the run → `manifests/h5_arms.json`
   (arms and proofs) → scored rows → `h5_budget_outcomes.csv`, `h5_ir_proof.csv`.
5. **Assumptions.** Base-model risk is available without instruct outcomes.
   The `beta` spellings are not themselves new false friends.
6. **Silent failure.** A "repair" that changes the program's meaning would
   make reversion disappear for the wrong reason.
7. **Symptom.** Implausibly large benefits on global repair.
8. **Test.**
   - `test_every_arm_preserves_ir_over_the_whole_corpus`
   - `test_ir_proof_can_fail`
   - `test_repair_respects_i7_overload_group`
   - `test_targeted_arm_ranks_by_base_risk_and_random_is_seeded`
9. **Where.** `p33/h5.py`: `define_arms`, `repaired_phi`, `ir_proof`, `prepare`.
10. **Why it matters.** It turns a diagnosis (H4) into an intervention, and
    the per-symbol framing is what makes targeted repair a claim about
    *efficiency* rather than "renaming helps".

---

## 14. Arm B: the hurdle

1. **Technical.**
   - The model generates from a natural-language request: greedy, at most 192 new
     tokens, 4 demonstrations.
   - Every output is saved and bucketed: LEX_FAIL, PARSE_FAIL, VALID_VACUOUS,
     VALID_WRONG or VALID_CORRECT.
   - At each site the question is first whether the output **reached** it (the
     normalised prefix matches), and only then whether it emitted the correct or the
     reverted spelling.
   - `P(reach)` and `P(revert | reach)` are reported separately. The product is
     shown alongside them, never instead of them.
2. **Simple.** First: did it even drive to the intersection? Only then: did it
   turn the right way?
3. **Example.** Not run in the smoke. The tests check the five buckets and the separation.
4. **Inputs → outputs.** (an IR rendered as a request, a lexicon) → generations → buckets
   and per-site observations → the hurdle table.
5. **Assumptions.** The natural-language requests are rendered from the IR.
   They still contain verb cues, which is a known limitation.
6. **Silent failure.** Collapsing the two stages into one rate. A model that
   never reaches the site then looks like a model that never reverts.
7. **Symptom.** Low reversion caused by low reach.
8. **Test.**
   - `test_reach_and_conditional_reversion_are_separate`
   - `test_five_bucket_evaluation`
   - `test_extraction_and_layout_normalisation`
9. **Where.** `p33/armb.py`: `evaluate`, `observe`, `hurdle`, `score_armb_cell`.
10. **Why it matters.** It is the only arm where the model writes the program
    itself, and the measure most like real use.

---

## 15. H2: why it is not testable

1. **Technical.**
   - H2 predicts a three-scale interaction: prior strength (T) × local
     context (A).
   - Testing it needs **independently calibrated** levels of T and A.
   - None exist. Deriving them from the outcome margins would make the test circular.
2. **Simple.** You cannot test whether "strong habits and weak hints" interact
   if the only way to measure habit strength is the outcome itself.
3. **Example.** `h2_did.csv` in the smoke: `NOT TESTABLE`, with the reason and the
   expected directions (logit +, probability +, margin −).
4. **Inputs → outputs.** Calibrated (T, A) cells → difference-in-differences on three scales.
   Today there are none, so the output is NOT TESTABLE.
5. **Assumptions.** Calibration must come from data that are not the outcome.
6. **Silent failure.** Splitting sites by their own margin, then "finding"
   an interaction.
7. **Symptom.** An interaction that appears on every scale and survives every
   control, because it is built in.
8. **Test.**
   - `test_h2_is_not_testable_without_calibration`
   - `test_h2_machinery_reports_three_scales_when_cells_exist`
9. **Where.** `p33/h2.py`.
10. **Why it matters.** Saying "not testable" is a result. A circular test would be a false one.

---

## 16. Power from a development pilot

1. **Technical.**
   - **Pilot data:** development rows only. `pilot_from_rows` refuses any
     other split.
   - **Variances:** inflated by the design effect `1 + (m − 1)·ICC`. The ICC is
     estimated from the pilot and also swept.
   - **H4:** Hanley–McNeil variance, checked against a clustered simulation.
   - **Rule effect:** a clustered one-sample test.
   - **Arm B:** precision shrinks with `P(reach)`.
   - **k\*:** KM-median precision, by resampling templates.
2. **Simple.** Before the exam, work out whether it has enough questions to
   detect what you are looking for, using only practice data.
3. **Example.**
   - The smoke pilot (n = 12, uninterpretable) gives a rule-effect power of 0.23 at 80 templates × 1.09
     sites.
   - At real development scale (80 templates × 10.65 sites) with the same effect
     size, the power is **0.97 / 0.78 / 0.61 for an ICC of 0 / 0.1 / 0.2**.
   - The clustering assumption alone moves the answer from "plenty" to "marginal".
   - **The real development pilot (2026-10-07)** measured the clustering instead of
     assuming it. The pooled ICC of the rule effect is **0.252**, so power at 80 templates is
     **0.251**. At an ICC of 0 it would be 0.994, and that ICC = 0 row was the only one the
     report printed before D9. 80% power is not reached even at a hypothetical 320 templates.
   - H4 criterion 1 is different. At its pilot ICC of 0.073 it has 80% power for a true AUROC
     of 0.62 or more ([`02 §8`](02_mathematics_and_statistics.md#8-power-under-clustering)).
4. **Inputs → outputs.** Development rows → `power.csv` and `POWER_ANALYSIS.md`.
5. **Assumptions.** The development effect sizes transfer roughly to the held-out
   cells. That is the usual pilot assumption, and it is weak.
6. **Silent failure.** Using held-out data to choose the held-out sample size.
7. **Symptom.** A sample size tuned to the result.
8. **Test.**
   - `test_power_refuses_heldout_pilot_data`
   - `test_power_is_monotone_in_effect_and_size`
   - `test_icc_estimator_hand_example`
9. **Where.** `p33/power.py`.
10. **Why it matters.** The Phase 3.2 preregistration admitted it had no power
    analysis, so a null result could not be interpreted. This supplies one before
    the held-out run is sized.

---

## 17. Theory → variable → code → metric (new rows only)

| Construct | Variable | Code | Metric / artifact |
|---|---|---|---|
| no peeking | cell class, freeze, unlock | `splits`, `freeze` | refusals; `split_exclusion_audit.csv` |
| habit strength under evidence | `k*`, censoring, sustained | `kstar` | `kstar_survival.csv`, KM plots |
| clean dose | leak-free nested ladder | `demos` | `demo_ids`, `demo_set_sha` per row |
| evidence-level uncertainty | template-cluster interval | `analysis.cluster_bootstrap` | `ci_*` columns, `n_clusters` |
| length confound | `norule_lenmatched` | `prompts` | `rule_effect.csv` (`control` column) |
| sign precision | fp32 head | `margins.TokenScorer` | `fp32_head`, `tie` per row |
| reproducibility | shards, manifests, hashes | `shards`, `provenance` | `run_completeness.csv`, `job_provenance.csv` |
| site-level predictability | risk vs label | `h4` | `h4_*.csv`, ROC/PR/calibration plots |
| efficient repair | reversions avoided per symbol | `h5` | `h5_budget_outcomes.csv`, `h5_ir_proof.csv` |
| generation reality | reach, conditional reversion | `armb` | `arm_b_*.csv` |
| design adequacy | power under clustering | `power` | `power.csv`, `POWER_ANALYSIS.md` |

---

## 18. What would support, and what would refute

| Claim | Supported if (held-out, after freeze) | Refuted or weakened if |
|---|---|---|
| H4 on new **mappings** | C1 and C2 pass after Holm on HELDOUT mapping cells | AUROC CI includes 0.60, or the gain over length is under 0.05 |
| H4 on new **models** | the same on HELDOUT model cells (not resting on 3B alone; since D10 these include 7B–72B) | it passes only on HELDOUT-WEAKENED (3B) cells |
| scale (D10) | no direction is registered: the reversion rate and the H4 AUROC are reported against log(parameters) within the Qwen2.5-Coder ladder (0.5B–32B), per family, with intervals | — (two-sided by design; a flat trend with a wide interval says nothing) |
| H4 on a new **grammar** | — | **NOT TESTABLE** (no valid family) |
| extinction | an INITIALLY_WRONG KM median with an interval and a censoring rate, stable across paraphrases | median unreached (> 32), or high censoring |
| rule-following | rule effect > 0 against **both** controls | effect vanishes against `norule_lenmatched` |
| H5 | targeted beats random per symbol, with control degradation ≤ 0.02 | targeted ≈ random, or controls degrade |
| H2 | — | **NOT TESTABLE** |

---

## 19. Claims to avoid

- **"The model needs ~6 examples."** Withdrawn. The development run now gives KM medians
  of 3.6–6.2 shots for initially-wrong sites, with 13–22% censored. That is a development
  estimate (exploratory); only the held-out run can confirm one.
- **"The rule table helps."** In development, 31 of 32 intervals include zero. The one that
  does not is one of 32 comparisons, with no multiplicity correction. At most: "a small
  positive point estimate, not distinguishable from zero".
- **"The design is well powered."** For H4 criterion 1, yes. For the pooled rule effect,
  no: power is 0.25 at the pilot ICC, so a held-out null would say little.
- **"Bigger models revert more."** Development has two sizes. The D10 scale analysis is
  held-out and two-sided.
- **"H4 generalises across grammars."** Not testable.
- **"`blk` confirms …"** `blk` is exploratory or weak-family only.
- **Any development number described as confirmatory.** The reports refuse this
  by banner.
- **"Results from Sol show …"** Only the development run has run on Sol, and its results are
  exploratory. Nothing held-out has run.

---

## 20. Learning resources (additions only; **links not verified from this environment**)

| Topic | Resource |
|---|---|
| Kaplan–Meier, censoring | Kaplan & Meier (1958), *Nonparametric estimation from incomplete observations*, JASA 53(282) |
| bootstrap | Efron & Tibshirani (1993), *An Introduction to the Bootstrap*, ch. 6 & 13 |
| clustered bootstrap | Field & Welsh (2007), *Bootstrapping clustered data*, JRSS-B 69(3) |
| multiple testing | Holm (1979), *A simple sequentially rejective multiple test procedure*, Scand. J. Stat. 6(2) |
| AUC variance | Hanley & McNeil (1982), *The meaning and use of the area under a ROC curve*, Radiology 143 |
| design effect | Kish (1965), *Survey Sampling*, §5.4 |
| calibration | Platt (1999), *Probabilistic outputs for SVMs*; Guo et al. (2017), *On calibration of modern neural networks*, ICML |
| leakage | Kapoor & Narayanan (2023), *Leakage and the reproducibility crisis in ML-based science*, Patterns 4(9) |
| preregistration | Nosek et al. (2018), *The preregistration revolution*, PNAS 115(11) |
| bf16 | Kalamkar et al. (2019), *A study of BFLOAT16 for deep learning training*, arXiv:1905.12322 |
| Slurm arrays / signals | https://slurm.schedmd.com/job_array.html · https://slurm.schedmd.com/sbatch.html (`--signal`) |
| HF offline cache | https://huggingface.co/docs/huggingface_hub/guides/manage-cache |
