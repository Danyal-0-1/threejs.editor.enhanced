# Explanations

Every document that explains the research is here: the theory, the mathematics, code
walk-throughs, retype plans, glossaries, knowledge checks and results. The code they explain
stays where it runs (the last table below).

- **Organized by phase.** Each folder keeps the name it had before the move of 2026-10-22, so a
  reference such as "`heldout_results_explained/08` §1" still names the right document.
- **Old paths:** [`../MOVES.md`](../MOVES.md) gives the old path of every file.
- **The map of the whole repository:** [`../START_HERE.md`](../START_HERE.md).

---

## Two ways to read

### A. Only the current experiment (Phase 3.3 on Sol, and Phase 4)

1. [`phase3_3/sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md`](phase3_3/sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md):
   the hypotheses, the design, the math and one site traced through the code.
2. [`phase3_3/heldout_results_explained/00_complete_results.md`](phase3_3/heldout_results_explained/00_complete_results.md):
   every result.
3. Then, in either order:
   - [`01_theory`](phase3_3/heldout_results_explained/01_theory.md) and
     [`02_mathematics`](phase3_3/heldout_results_explained/02_mathematics_and_statistics.md): what
     the results mean, and how each number is computed;
   - [`03_code`](phase3_3/heldout_results_explained/03_code_and_pipeline.md) and
     [`04_retyping_plan`](phase3_3/heldout_results_explained/04_retyping_plan.md): how the run was
     executed, and which code to retype.
4. [`09_conclusions`](phase3_3/heldout_results_explained/09_conclusions_claim_strength_and_venues.md):
   the conclusion, how strong each claim is, and the venues.
5. [`phase4/fixes_before_phase4/`](phase4/fixes_before_phase4/README.md): what was corrected
   afterwards.
6. [`phase4/api_models_results_explained/00_complete_results.md`](phase4/api_models_results_explained/00_complete_results.md):
   nine served models on the same cells (Phase 4's first development run, exploratory).

### B. The whole project, in the order it was built

| step | read | it explains | its code |
|---|---|---|---|
| 0 | [`background/`](background/) | the literature reviews, the novelty audit, and why the hypotheses were ordered as they were | — |
| 1 | [`phase1/phase1.md`](phase1/phase1.md) | the 3DOM language, formalised as a grammar | [`grammar_and_3DOM_client/`](../grammar_and_3DOM_client/) |
| 2 | [`phase2/phase2.md`](phase2/phase2.md) | the alien-syntax transpiler: one language, many spellings | [`alien_syntax/`](../alien_syntax/), [`run/`](../run/) |
| 3 | [`phase3/phase3_explained/`](phase3/phase3_explained/00_complete_phase3_guide.md) | collision sites, the scorer, risk and repair | [`phase3/src/phase3/`](../phase3/src/phase3/) |
| 3.2 | [`phase3_2/phase3_2_explained/`](phase3_2/phase3_2_explained/00_complete_phase3_2_guide.md) | new materials, a second grammar, first-divergent-token margins | [`phase3_2/src/phase3_2/`](../phase3_2/src/phase3_2/) |
| 3.3, design | [`phase3_3/sol_experiment_explained/`](phase3_3/sol_experiment_explained/00_complete_guide.md) | the preregistered pipeline built for ASU Sol | [`phase3_2/sol/`](../phase3_2/sol/) |
| 3.3, results | [`phase3_3/heldout_results_explained/`](phase3_3/heldout_results_explained/00_complete_results.md) | the held-out results: 21 models, two grammars | [`phase3_2/sol/scripts/`](../phase3_2/sol/scripts/) (analysis) |
| 4 | [`phase4/fixes_before_phase4/`](phase4/fixes_before_phase4/README.md) | every fix made before Phase 4's new work | [`phase4/code/`](../phase4/code/README.md) (the pipeline), [`phase4/scripts/`](../phase4/scripts/) |
| 4, served models | [`phase4/api_models_results_explained/`](phase4/api_models_results_explained/00_complete_results.md) | nine models served by the ASU RC API on Phase 3.3's held-out cells: the development run `dev-20261023a` (exploratory) | [`phase4/code/p4/scoring/api.py`](../phase4/code/p4/scoring/api.py), [`phase4/code/tools/`](../phase4/code/tools/) |

Each phase folder from 3 onward follows the same numbering, so you can read one topic across
phases (next table).

---

## By topic

| topic | Phase 3 | Phase 3.2 | Phase 3.3, design | Phase 3.3, results | Phase 4, served models |
|---|---|---|---|---|---|
| **the whole phase in one place** | [00](phase3/phase3_explained/00_complete_phase3_guide.md) | [00](phase3_2/phase3_2_explained/00_complete_phase3_2_guide.md) | [00](phase3_3/sol_experiment_explained/00_complete_guide.md), [in one file](phase3_3/sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md) | [00](phase3_3/heldout_results_explained/00_complete_results.md) | [00](phase4/api_models_results_explained/00_complete_results.md) |
| **theory** | [01](phase3/phase3_explained/01_theory_and_research_design.md) | [01](phase3_2/phase3_2_explained/01_theory_and_research_design.md) | [01](phase3_3/sol_experiment_explained/01_theory_and_research_design.md) | [01](phase3_3/heldout_results_explained/01_theory.md) | [01](phase4/api_models_results_explained/01_theory.md) |
| **mathematics and statistics** | [02](phase3/phase3_explained/02_mathematics_and_statistics.md), [equations (PDF)](phase3/phase3_explained/phase3_delta_full_equations.pdf) | [02](phase3_2/phase3_2_explained/02_mathematics_and_statistics.md) | [02](phase3_3/sol_experiment_explained/02_mathematics_and_statistics.md), [the full math](phase3_3/sol_experiment_explained/experiment_math.md) | [02](phase3_3/heldout_results_explained/02_mathematics_and_statistics.md) | [02](phase4/api_models_results_explained/02_mathematics_and_statistics.md) |
| **code and pipeline** | [03](phase3/phase3_explained/03_code_and_pipeline.md) | [03](phase3_2/phase3_2_explained/03_code_and_pipeline.md) | [03](phase3_3/sol_experiment_explained/03_code_and_pipeline.md) | [03](phase3_3/heldout_results_explained/03_code_and_pipeline.md) | [03](phase4/api_models_results_explained/03_code_and_pipeline.md) |
| **what to retype, and in what order** | [04](phase3/phase3_explained/04_retyping_and_reading_plan.md) | [04](phase3_2/phase3_2_explained/04_retyping_and_reading_plan.md) | [04](phase3_3/sol_experiment_explained/04_retyping_and_reading_plan.md) | [04](phase3_3/heldout_results_explained/04_retyping_plan.md) | [04](phase4/api_models_results_explained/04_retyping_plan.md) |
| **glossary** | [05](phase3/phase3_explained/05_glossary.md) | [05](phase3_2/phase3_2_explained/05_glossary.md) | [05](phase3_3/sol_experiment_explained/05_glossary.md) | — | [01, end](phase4/api_models_results_explained/01_theory.md#glossary-of-the-new-terms) |
| **knowledge check** | [06](phase3/phase3_explained/06_knowledge_check.md) | [06](phase3_2/phase3_2_explained/06_knowledge_check.md) | [06](phase3_3/sol_experiment_explained/06_knowledge_check.md) | [07](phase3_3/heldout_results_explained/07_knowledge_check.md) | [07](phase4/api_models_results_explained/07_knowledge_check.md) |
| **the picture, in plain images** | — | — | [07](phase3_3/sol_experiment_explained/07_the_picture.md) | [05](phase3_3/heldout_results_explained/05_mental_image.md), [10: people and the brain](phase3_3/heldout_results_explained/10_humans_and_the_brain.md) | [05](phase4/api_models_results_explained/05_mental_image.md) |
| **defects, changes, superseded numbers** | — | [07: next steps](phase3_2/phase3_2_explained/07_next_steps.md) | [08](phase3_3/sol_experiment_explained/08_changes_defects_and_superseded_numbers.md) | [08](phase3_3/heldout_results_explained/08_issues_and_superseded_numbers.md) | [08](phase4/api_models_results_explained/08_issues_and_superseded_numbers.md) |
| **the paper: claims and venues** | [publications](phase3/phase3_explained/publications/README.md) | — | — | [06](phase3_3/heldout_results_explained/06_publishability_and_paper.md), [09](phase3_3/heldout_results_explained/09_conclusions_claim_strength_and_venues.md) | [06](phase4/api_models_results_explained/06_publishability_and_paper.md) |

**Phase 4:** [README](phase4/fixes_before_phase4/README.md) (the index of every fix),
[01](phase4/fixes_before_phase4/01_phase4_step0_fixes.md) (the six fixes of 2026-10-21),
[02](phase4/fixes_before_phase4/02_fixes_during_phase3_3.md) (every fix during Phase 3.3),
[03](phase4/fixes_before_phase4/03_doc_changes_before_after.md) (the before/after of each doc change).

**Background:**

- [`litreture_review.md`](background/litreture_review.md): the literature and the venues;
- [`litreture_reveiw_1.md`](background/litreture_reveiw_1.md): the novelty audit (the file name's
  spelling is the one requested; see its line 6);
- [`litreture_review_2.md`](background/litreture_review_2.md): the research background, the
  brief the novelty audit answered;
- [`hypothesis_strength_and_compute_analysis.md`](background/hypothesis_strength_and_compute_analysis.md):
  how strong each hypothesis is, and the compute it needs;
- [`references.bib`](background/references.bib).

---

## Where the code is

The explanations link to the code by file and line. These are the folders they point to.

| phase | code | tests | how it runs |
|---|---|---|---|
| 1 | [`grammar_and_3DOM_client/`](../grammar_and_3DOM_client/) | `grammar_and_3DOM_client/test_tasks.py`, `conformance/` | — |
| 2 | [`alien_syntax/src/`](../alien_syntax/src/) | [`alien_syntax/tests/`](../alien_syntax/tests/) | [`run/run.md`](../run/run.md) |
| 3 | [`phase3/src/phase3/`](../phase3/src/phase3/) (frozen), [`phase3/vendor/`](../phase3/vendor/) (materials) | [`phase3/tests/`](../phase3/tests/) (54) | [`phase3/README.md`](../phase3/README.md) |
| 3.2 | [`phase3_2/src/phase3_2/`](../phase3_2/src/phase3_2/) (frozen) | [`phase3_2/tests/`](../phase3_2/tests/) (36) | [`phase3_2/README.md`](../phase3_2/README.md) |
| 3.3 | [`phase3_2/sol/src/p33/`](../phase3_2/sol/src/p33/) (frozen), [`phase3_2/sol/scripts/`](../phase3_2/sol/scripts/) | [`phase3_2/sol/tests/`](../phase3_2/sol/tests/) (147) | [`phase3_2/sol/README.md`](../phase3_2/sol/README.md) (the Sol runbook) |
| 4 | [`phase4/code/p4/`](../phase4/code/p4/__init__.py) (a verified copy of all of the above, one folder per stage), [`phase4/scripts/`](../phase4/scripts/) | [`phase4/code/tests/`](../phase4/code/tests/), [`phase4/tests/`](../phase4/tests/) (6) | [`phase4/code/README.md`](../phase4/code/README.md) |

"Frozen" means the development freeze of 2026-10-07 records the file by its path: it is never
edited or moved ([`../START_HERE.md`](../START_HERE.md) explains why).
