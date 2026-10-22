# What moved on 2026-10-22

The repository was reorganized on 2026-10-22, on the branch `reorganize-2026-10-22`, starting
from commit `87402234`. The map of the new layout is [`START_HERE.md`](START_HERE.md).

**Nothing was deleted.**

- **175 files moved** with `git mv`, so `git log --follow <new path>` shows each
  file's whole history.
- **49 compiled caches** (`*.pyc`) are no longer tracked by git. They are still on disk,
  and `.gitignore` now ignores them.
- **226 links in 24 documents** were rewritten. Every link in the repository
  resolves, except three inside a third-party library of the editor, which were broken before.
- **The code, the materials, the configs, the preregistration and the results did not move.**
  The freeze pins them (see [`START_HERE.md`](START_HERE.md)).

**In old commits the old paths still work.** For example:
`git show 87402234:phase3_2/sol/heldout_results_explained/00_complete_results.md`.

---

## At a glance

| old path | new path | files | what it is |
|---|---|---:|---|
| `project_status/phase1.md` | `explanations/phase1/phase1.md` | 1 | Phase 1 explained (3DOM grammar) |
| `project_status/phase2.md` | `explanations/phase2/phase2.md` | 1 | Phase 2 explained (alien-syntax transpiler) |
| `project_status/litreture_review.md` | `explanations/background/litreture_review.md` | 1 | literature review |
| `project_status/litreture_reveiw_1.md` | `explanations/background/litreture_reveiw_1.md` | 1 | literature review |
| `project_status/litreture_review_2.md` | `explanations/background/litreture_review_2.md` | 1 | literature review |
| `project_status/references.bib` | `explanations/background/references.bib` | 1 | bibliography |
| `project_status/hypothesis_strength_and_compute_analysis.md` | `explanations/background/hypothesis_strength_and_compute_analysis.md` | 1 | hypothesis strength and compute |
| `phase3/phase3_explained` | `explanations/phase3/phase3_explained` | 9 | Phase 3 explained |
| `phase3_2/phase3_2_explained` | `explanations/phase3_2/phase3_2_explained` | 8 | Phase 3.2 explained |
| `phase3_2/sol/sol_experiment_explained` | `explanations/phase3_3/sol_experiment_explained` | 11 | Phase 3.3 design, math and code (pre-run) |
| `phase3_2/sol/heldout_results_explained` | `explanations/phase3_3/heldout_results_explained` | 11 | Phase 3.3 held-out results |
| `phase4/fixes_before_phase4` | `explanations/phase4/fixes_before_phase4` | 4 | every fix before Phase 4 |
| `phase3_3/README.md` | `archive/phase3_3_first_laptop_run/README.md` | 1 | first Phase 3.3 run: its index |
| `phase3_3/00_results_in_plain_language.md` | `archive/phase3_3_first_laptop_run/00_results_in_plain_language.md` | 1 | first Phase 3.3 run (withdrawn/corrected by ERRATA) |
| `phase3_3/01_changes_and_results.md` | `archive/phase3_3_first_laptop_run/01_changes_and_results.md` | 1 | first Phase 3.3 run (withdrawn/corrected by ERRATA) |
| `phase3_3/02_theory_and_math.md` | `archive/phase3_3_first_laptop_run/02_theory_and_math.md` | 1 | first Phase 3.3 run (withdrawn/corrected by ERRATA) |
| `phase3_3/03_methods_and_pipeline.md` | `archive/phase3_3_first_laptop_run/03_methods_and_pipeline.md` | 1 | first Phase 3.3 run (withdrawn/corrected by ERRATA) |
| `phase3_3/04_sol_readiness.md` | `archive/phase3_3_first_laptop_run/04_sol_readiness.md` | 1 | first Phase 3.3 run (withdrawn/corrected by ERRATA) |
| `phase3_3/05_knowledge_check.md` | `archive/phase3_3_first_laptop_run/05_knowledge_check.md` | 1 | first Phase 3.3 run (withdrawn/corrected by ERRATA) |
| `phase3_3/ERRATA.md` | `archive/phase3_3_first_laptop_run/ERRATA.md` | 1 | the errata of the first Phase 3.3 run |
| `phase3_3/outputs_snapshot` | `archive/phase3_3_first_laptop_run/outputs_snapshot` | 6 | the data snapshot of the first run (5 of its 6 files are byte copies of phase3_2/outputs) |
| `phase3_2/sol/legacy_superseded` | `archive/phase3_2_sol/legacy_superseded` | 5 | old Sol scripts that would not have run |
| `phase3_2/sol/local_smoke` | `archive/phase3_2_sol/local_smoke` | 102 | the 2026-10-05 laptop smoke run |
| `ARCHITECTURE_NOTES.md` | `strata_eval/ARCHITECTURE_NOTES.md` | 1 | editor AI-layer map |
| `evalEditMatrix.md` | `strata_eval/evalEditMatrix.md` | 1 | eval-matrix handover |
| `plot_matrix.py` | `strata_eval/plot_matrix.py` | 1 | eval-matrix plotter |
| `strata_runner.js` | `strata_eval/strata_runner.js` | 1 | browser-console eval runner |

---

## Every moved file

### Explanations → `explanations/` (50 files)

<details><summary>show the list</summary>

| old | new |
|---|---|
| `phase3/phase3_explained/00_complete_phase3_guide.md` | `explanations/phase3/phase3_explained/00_complete_phase3_guide.md` |
| `phase3/phase3_explained/01_theory_and_research_design.md` | `explanations/phase3/phase3_explained/01_theory_and_research_design.md` |
| `phase3/phase3_explained/02_mathematics_and_statistics.md` | `explanations/phase3/phase3_explained/02_mathematics_and_statistics.md` |
| `phase3/phase3_explained/03_code_and_pipeline.md` | `explanations/phase3/phase3_explained/03_code_and_pipeline.md` |
| `phase3/phase3_explained/04_retyping_and_reading_plan.md` | `explanations/phase3/phase3_explained/04_retyping_and_reading_plan.md` |
| `phase3/phase3_explained/05_glossary.md` | `explanations/phase3/phase3_explained/05_glossary.md` |
| `phase3/phase3_explained/06_knowledge_check.md` | `explanations/phase3/phase3_explained/06_knowledge_check.md` |
| `phase3/phase3_explained/phase3_delta_full_equations.pdf` | `explanations/phase3/phase3_explained/phase3_delta_full_equations.pdf` |
| `phase3/phase3_explained/publications/README.md` | `explanations/phase3/phase3_explained/publications/README.md` |
| `phase3_2/phase3_2_explained/00_complete_phase3_2_guide.md` | `explanations/phase3_2/phase3_2_explained/00_complete_phase3_2_guide.md` |
| `phase3_2/phase3_2_explained/01_theory_and_research_design.md` | `explanations/phase3_2/phase3_2_explained/01_theory_and_research_design.md` |
| `phase3_2/phase3_2_explained/02_mathematics_and_statistics.md` | `explanations/phase3_2/phase3_2_explained/02_mathematics_and_statistics.md` |
| `phase3_2/phase3_2_explained/03_code_and_pipeline.md` | `explanations/phase3_2/phase3_2_explained/03_code_and_pipeline.md` |
| `phase3_2/phase3_2_explained/04_retyping_and_reading_plan.md` | `explanations/phase3_2/phase3_2_explained/04_retyping_and_reading_plan.md` |
| `phase3_2/phase3_2_explained/05_glossary.md` | `explanations/phase3_2/phase3_2_explained/05_glossary.md` |
| `phase3_2/phase3_2_explained/06_knowledge_check.md` | `explanations/phase3_2/phase3_2_explained/06_knowledge_check.md` |
| `phase3_2/phase3_2_explained/07_next_steps.md` | `explanations/phase3_2/phase3_2_explained/07_next_steps.md` |
| `phase3_2/sol/heldout_results_explained/00_complete_results.md` | `explanations/phase3_3/heldout_results_explained/00_complete_results.md` |
| `phase3_2/sol/heldout_results_explained/01_theory.md` | `explanations/phase3_3/heldout_results_explained/01_theory.md` |
| `phase3_2/sol/heldout_results_explained/02_mathematics_and_statistics.md` | `explanations/phase3_3/heldout_results_explained/02_mathematics_and_statistics.md` |
| `phase3_2/sol/heldout_results_explained/03_code_and_pipeline.md` | `explanations/phase3_3/heldout_results_explained/03_code_and_pipeline.md` |
| `phase3_2/sol/heldout_results_explained/04_retyping_plan.md` | `explanations/phase3_3/heldout_results_explained/04_retyping_plan.md` |
| `phase3_2/sol/heldout_results_explained/05_mental_image.md` | `explanations/phase3_3/heldout_results_explained/05_mental_image.md` |
| `phase3_2/sol/heldout_results_explained/06_publishability_and_paper.md` | `explanations/phase3_3/heldout_results_explained/06_publishability_and_paper.md` |
| `phase3_2/sol/heldout_results_explained/07_knowledge_check.md` | `explanations/phase3_3/heldout_results_explained/07_knowledge_check.md` |
| `phase3_2/sol/heldout_results_explained/08_issues_and_superseded_numbers.md` | `explanations/phase3_3/heldout_results_explained/08_issues_and_superseded_numbers.md` |
| `phase3_2/sol/heldout_results_explained/09_conclusions_claim_strength_and_venues.md` | `explanations/phase3_3/heldout_results_explained/09_conclusions_claim_strength_and_venues.md` |
| `phase3_2/sol/heldout_results_explained/10_humans_and_the_brain.md` | `explanations/phase3_3/heldout_results_explained/10_humans_and_the_brain.md` |
| `phase3_2/sol/sol_experiment_explained/00_complete_guide.md` | `explanations/phase3_3/sol_experiment_explained/00_complete_guide.md` |
| `phase3_2/sol/sol_experiment_explained/01_theory_and_research_design.md` | `explanations/phase3_3/sol_experiment_explained/01_theory_and_research_design.md` |
| `phase3_2/sol/sol_experiment_explained/02_mathematics_and_statistics.md` | `explanations/phase3_3/sol_experiment_explained/02_mathematics_and_statistics.md` |
| `phase3_2/sol/sol_experiment_explained/03_code_and_pipeline.md` | `explanations/phase3_3/sol_experiment_explained/03_code_and_pipeline.md` |
| `phase3_2/sol/sol_experiment_explained/04_retyping_and_reading_plan.md` | `explanations/phase3_3/sol_experiment_explained/04_retyping_and_reading_plan.md` |
| `phase3_2/sol/sol_experiment_explained/05_glossary.md` | `explanations/phase3_3/sol_experiment_explained/05_glossary.md` |
| `phase3_2/sol/sol_experiment_explained/06_knowledge_check.md` | `explanations/phase3_3/sol_experiment_explained/06_knowledge_check.md` |
| `phase3_2/sol/sol_experiment_explained/07_the_picture.md` | `explanations/phase3_3/sol_experiment_explained/07_the_picture.md` |
| `phase3_2/sol/sol_experiment_explained/08_changes_defects_and_superseded_numbers.md` | `explanations/phase3_3/sol_experiment_explained/08_changes_defects_and_superseded_numbers.md` |
| `phase3_2/sol/sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md` | `explanations/phase3_3/sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md` |
| `phase3_2/sol/sol_experiment_explained/experiment_math.md` | `explanations/phase3_3/sol_experiment_explained/experiment_math.md` |
| `phase4/fixes_before_phase4/01_phase4_step0_fixes.md` | `explanations/phase4/fixes_before_phase4/01_phase4_step0_fixes.md` |
| `phase4/fixes_before_phase4/02_fixes_during_phase3_3.md` | `explanations/phase4/fixes_before_phase4/02_fixes_during_phase3_3.md` |
| `phase4/fixes_before_phase4/03_doc_changes_before_after.md` | `explanations/phase4/fixes_before_phase4/03_doc_changes_before_after.md` |
| `phase4/fixes_before_phase4/README.md` | `explanations/phase4/fixes_before_phase4/README.md` |
| `project_status/hypothesis_strength_and_compute_analysis.md` | `explanations/background/hypothesis_strength_and_compute_analysis.md` |
| `project_status/litreture_reveiw_1.md` | `explanations/background/litreture_reveiw_1.md` |
| `project_status/litreture_review.md` | `explanations/background/litreture_review.md` |
| `project_status/litreture_review_2.md` | `explanations/background/litreture_review_2.md` |
| `project_status/phase1.md` | `explanations/phase1/phase1.md` |
| `project_status/phase2.md` | `explanations/phase2/phase2.md` |
| `project_status/references.bib` | `explanations/background/references.bib` |

</details>

### Archived → `archive/` (121 files)

<details><summary>show the list</summary>

| old | new |
|---|---|
| `phase3_2/sol/legacy_superseded/README.md` | `archive/phase3_2_sol/legacy_superseded/README.md` |
| `phase3_2/sol/legacy_superseded/WHY_SUPERSEDED.md` | `archive/phase3_2_sol/legacy_superseded/WHY_SUPERSEDED.md` |
| `phase3_2/sol/legacy_superseded/arm_a.slurm` | `archive/phase3_2_sol/legacy_superseded/arm_a.slurm` |
| `phase3_2/sol/legacy_superseded/prefetch_models.py` | `archive/phase3_2_sol/legacy_superseded/prefetch_models.py` |
| `phase3_2/sol/legacy_superseded/primary.slurm` | `archive/phase3_2_sol/legacy_superseded/primary.slurm` |
| `phase3_2/sol/local_smoke/model_pins.json` | `archive/phase3_2_sol/local_smoke/model_pins.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_norule_0__7781962813a5e94d.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_norule_0__7781962813a5e94d.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_norule_1__d6b1ac380f87ad4e.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_norule_1__d6b1ac380f87ad4e.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_norule_2__aee8069da2f50b0b.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_norule_2__aee8069da2f50b0b.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_norule_lenmatched_0__efdf50a5d19dcb11.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_norule_lenmatched_0__efdf50a5d19dcb11.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_norule_lenmatched_1__e2f7093d04069822.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_norule_lenmatched_1__e2f7093d04069822.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_norule_lenmatched_2__e8112977dc1e8fc7.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_norule_lenmatched_2__e8112977dc1e8fc7.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_rule_0__b7295562d1d0116a.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_rule_0__b7295562d1d0116a.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_rule_1__21b886ca6cf30882.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_rule_1__21b886ca6cf30882.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_rule_2__841bf30af093b39b.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/arm_a/arm_a_dom_d50s1_rule_2__841bf30af093b39b.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_ladder_0__0a5965e369fa0b20.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_ladder_0__0a5965e369fa0b20.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_ladder_1__91dc6ccf096bdea5.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_ladder_1__91dc6ccf096bdea5.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_p0_0__078c65dcbfee77a9.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_p0_0__078c65dcbfee77a9.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_p0_1__ea1c67357a25f3a4.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_p0_1__ea1c67357a25f3a4.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_p1_0__0067f9809f9d7e88.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_p1_0__0067f9809f9d7e88.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_p1_1__4e3c33332f46722b.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_p1_1__4e3c33332f46722b.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_p2_0__717b14342e037064.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_p2_0__717b14342e037064.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_p2_1__3a7de69c0f011c08.done.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/checkpoints/primary/primary_dom_d50s1_p2_1__3a7de69c0f011c08.done.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/arm_a_long.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/arm_a_long.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/arm_b_generations.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/arm_b_generations.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/arm_b_hurdle.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/arm_b_hurdle.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/extinction_rung_long.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/extinction_rung_long.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/failed_cells.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/failed_cells.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/fertility.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/fertility.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/h2_did.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/h2_did.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/h4_metrics_baselines_calibration.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/h4_metrics_baselines_calibration.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/h4_predictions.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/h4_predictions.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/h5_budget_outcomes.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/h5_budget_outcomes.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/h5_ir_proof.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/h5_ir_proof.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/job_provenance.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/job_provenance.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/kstar_survival.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/kstar_survival.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/paraphrase.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/paraphrase.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/power.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/power.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/rule_effect.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/rule_effect.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/run_completeness.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/run_completeness.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/site_inventory.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/site_inventory.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/csv/split_exclusion_audit.csv` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/csv/split_exclusion_audit.csv` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/logs/post_smoke_fertility_export.out` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/logs/post_smoke_fertility_export.out` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/logs/smoke.err` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/logs/smoke.err` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/logs/smoke.out` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/logs/smoke.out` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/manifests/fertility.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/manifests/fertility.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/manifests/job_arm_a_local_0_226102.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/manifests/job_arm_a_local_0_226102.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/manifests/job_primary_local_0_226102.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/manifests/job_primary_local_0_226102.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/manifests/plan_arm_a.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/manifests/plan_arm_a.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/manifests/plan_primary.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/manifests/plan_primary.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/manifests/preflight_2026-10-06T001732+0000.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/manifests/preflight_2026-10-06T001732+0000.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/manifests/run_config.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/manifests/run_config.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/merged/arm_a.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/merged/arm_a.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/merged/arm_a.status.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/merged/arm_a.status.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/merged/primary.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/merged/primary.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/merged/primary.status.json` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/merged/primary.status.json` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/armb_hurdle_outcomes.png` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/armb_hurdle_outcomes.png` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/armb_hurdle_outcomes.svg` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/armb_hurdle_outcomes.svg` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/extinction_trajectories_km.png` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/extinction_trajectories_km.png` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/extinction_trajectories_km.svg` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/extinction_trajectories_km.svg` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/family_mapping_model_stratum.png` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/family_mapping_model_stratum.png` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/family_mapping_model_stratum.svg` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/family_mapping_model_stratum.svg` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/fertility_tokenization.png` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/fertility_tokenization.png` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/fertility_tokenization.svg` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/fertility_tokenization.svg` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/h2_three_scale.png` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/h2_three_scale.png` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/h2_three_scale.svg` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/h2_three_scale.svg` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/h4_roc_pr_calibration.png` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/h4_roc_pr_calibration.png` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/h4_roc_pr_calibration.svg` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/h4_roc_pr_calibration.svg` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/h5_benefit_per_symbol.png` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/h5_benefit_per_symbol.png` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/h5_benefit_per_symbol.svg` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/h5_benefit_per_symbol.svg` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/margin_reversion_distributions.png` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/margin_reversion_distributions.png` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/margin_reversion_distributions.svg` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/margin_reversion_distributions.svg` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/model_size_tokenizer.png` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/model_size_tokenizer.png` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/model_size_tokenizer.svg` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/model_size_tokenizer.svg` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/paraphrase_sensitivity.png` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/paraphrase_sensitivity.png` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/paraphrase_sensitivity.svg` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/paraphrase_sensitivity.svg` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/power_curves.png` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/power_curves.png` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/power_curves.svg` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/power_curves.svg` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/rule_effect_forest.png` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/rule_effect_forest.png` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/plots/rule_effect_forest.svg` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/plots/rule_effect_forest.svg` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_norule_0__7781962813a5e94d.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_norule_0__7781962813a5e94d.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_norule_1__d6b1ac380f87ad4e.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_norule_1__d6b1ac380f87ad4e.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_norule_2__aee8069da2f50b0b.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_norule_2__aee8069da2f50b0b.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_norule_lenmatched_0__efdf50a5d19dcb11.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_norule_lenmatched_0__efdf50a5d19dcb11.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_norule_lenmatched_1__e2f7093d04069822.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_norule_lenmatched_1__e2f7093d04069822.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_norule_lenmatched_2__e8112977dc1e8fc7.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_norule_lenmatched_2__e8112977dc1e8fc7.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_rule_0__b7295562d1d0116a.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_rule_0__b7295562d1d0116a.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_rule_1__21b886ca6cf30882.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_rule_1__21b886ca6cf30882.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_rule_2__841bf30af093b39b.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/arm_a/arm_a_dom_d50s1_rule_2__841bf30af093b39b.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_ladder_0__0a5965e369fa0b20.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_ladder_0__0a5965e369fa0b20.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_ladder_1__91dc6ccf096bdea5.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_ladder_1__91dc6ccf096bdea5.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_p0_0__078c65dcbfee77a9.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_p0_0__078c65dcbfee77a9.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_p0_1__ea1c67357a25f3a4.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_p0_1__ea1c67357a25f3a4.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_p1_0__0067f9809f9d7e88.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_p1_0__0067f9809f9d7e88.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_p1_1__4e3c33332f46722b.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_p1_1__4e3c33332f46722b.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_p2_0__717b14342e037064.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_p2_0__717b14342e037064.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_p2_1__3a7de69c0f011c08.jsonl` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/raw/shards/primary/primary_dom_d50s1_p2_1__3a7de69c0f011c08.jsonl` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/reports/DEVELOPMENT_RESULTS.md` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/reports/DEVELOPMENT_RESULTS.md` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/reports/DEVIATIONS.md` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/reports/DEVIATIONS.md` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/reports/HELDOUT_RESULTS.md` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/reports/HELDOUT_RESULTS.md` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/reports/HYPOTHESIS_RESULTS.md` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/reports/HYPOTHESIS_RESULTS.md` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/reports/METHODS_AND_PROVENANCE.md` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/reports/METHODS_AND_PROVENANCE.md` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/reports/PLAIN_LANGUAGE_RESULTS.md` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/reports/PLAIN_LANGUAGE_RESULTS.md` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/reports/POWER_ANALYSIS.md` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/reports/POWER_ANALYSIS.md` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/reports/QUALITY_CONTROL.md` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/reports/QUALITY_CONTROL.md` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/reports/REPRODUCTION.md` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/reports/REPRODUCTION.md` |
| `phase3_2/sol/local_smoke/smoke-local-20261005/reports/RUN_SUMMARY.md` | `archive/phase3_2_sol/local_smoke/smoke-local-20261005/reports/RUN_SUMMARY.md` |
| `phase3_3/00_results_in_plain_language.md` | `archive/phase3_3_first_laptop_run/00_results_in_plain_language.md` |
| `phase3_3/01_changes_and_results.md` | `archive/phase3_3_first_laptop_run/01_changes_and_results.md` |
| `phase3_3/02_theory_and_math.md` | `archive/phase3_3_first_laptop_run/02_theory_and_math.md` |
| `phase3_3/03_methods_and_pipeline.md` | `archive/phase3_3_first_laptop_run/03_methods_and_pipeline.md` |
| `phase3_3/04_sol_readiness.md` | `archive/phase3_3_first_laptop_run/04_sol_readiness.md` |
| `phase3_3/05_knowledge_check.md` | `archive/phase3_3_first_laptop_run/05_knowledge_check.md` |
| `phase3_3/ERRATA.md` | `archive/phase3_3_first_laptop_run/ERRATA.md` |
| `phase3_3/README.md` | `archive/phase3_3_first_laptop_run/README.md` |
| `phase3_3/outputs_snapshot/arm_a_0.5b.json` | `archive/phase3_3_first_laptop_run/outputs_snapshot/arm_a_0.5b.json` |
| `phase3_3/outputs_snapshot/arm_a_0.5b_fixed.json` | `archive/phase3_3_first_laptop_run/outputs_snapshot/arm_a_0.5b_fixed.json` |
| `phase3_3/outputs_snapshot/arm_a_balanced.json` | `archive/phase3_3_first_laptop_run/outputs_snapshot/arm_a_balanced.json` |
| `phase3_3/outputs_snapshot/arm_a_sizes.json` | `archive/phase3_3_first_laptop_run/outputs_snapshot/arm_a_sizes.json` |
| `phase3_3/outputs_snapshot/primary.log` | `archive/phase3_3_first_laptop_run/outputs_snapshot/primary.log` |
| `phase3_3/outputs_snapshot/sites_v2.json` | `archive/phase3_3_first_laptop_run/outputs_snapshot/sites_v2.json` |

</details>

### The editor's eval files → `strata_eval/` (4 files)

<details><summary>show the list</summary>

| old | new |
|---|---|
| `ARCHITECTURE_NOTES.md` | `strata_eval/ARCHITECTURE_NOTES.md` |
| `evalEditMatrix.md` | `strata_eval/evalEditMatrix.md` |
| `plot_matrix.py` | `strata_eval/plot_matrix.py` |
| `strata_runner.js` | `strata_eval/strata_runner.js` |

</details>

---

## No longer tracked by git, still on disk (49 files)

These are compiled Python caches. Python rebuilds them, and `.gitignore` now ignores
`__pycache__/` and `*.pyc`.

<details><summary>show the list</summary>

- `__pycache__/canonicalize.cpython-312.pyc`
- `alien_syntax/grammar/__pycache__/render_grammar.cpython-312.pyc`
- `alien_syntax/measure/__pycache__/collisions.cpython-312.pyc`
- `alien_syntax/measure/__pycache__/dfa_parity.cpython-312.pyc`
- `alien_syntax/measure/__pycache__/fertility.cpython-312.pyc`
- `alien_syntax/measure/__pycache__/prior_strength.cpython-312.pyc`
- `alien_syntax/src/__pycache__/canonicalize.cpython-312.opt-1.pyc`
- `alien_syntax/src/__pycache__/canonicalize.cpython-312.pyc`
- `alien_syntax/src/__pycache__/generate_corpus.cpython-312.pyc`
- `alien_syntax/src/__pycache__/heuristics_ir.cpython-312.pyc`
- `alien_syntax/src/__pycache__/phi.cpython-312.opt-1.pyc`
- `alien_syntax/src/__pycache__/phi.cpython-312.pyc`
- `alien_syntax/src/__pycache__/transpiler.cpython-312.pyc`
- `grammar_and_3DOM_client/__pycache__/fixture_scene.cpython-312.opt-1.pyc`
- `grammar_and_3DOM_client/__pycache__/fixture_scene.cpython-312.pyc`
- `grammar_and_3DOM_client/__pycache__/grammar_metrics.cpython-312.pyc`
- `grammar_and_3DOM_client/__pycache__/tasks.cpython-312.opt-1.pyc`
- `grammar_and_3DOM_client/__pycache__/tasks.cpython-312.pyc`
- `grammar_and_3DOM_client/conformance/__pycache__/refgrammar.cpython-312.pyc`
- `phase3/src/phase3/__pycache__/__init__.cpython-312.pyc`
- `phase3/src/phase3/__pycache__/_vendor.cpython-312.pyc`
- `phase3/src/phase3/__pycache__/linter.cpython-312.pyc`
- `phase3/src/phase3/__pycache__/models.cpython-312.pyc`
- `phase3/src/phase3/__pycache__/outcomes.cpython-312.pyc`
- `phase3/src/phase3/__pycache__/scoring.cpython-312.pyc`
- `phase3/src/phase3/__pycache__/sites.cpython-312.pyc`
- `phase3/tests/__pycache__/test_pipeline.cpython-312.pyc`
- `phase3/tests/__pycache__/test_scorer_repair.cpython-312.pyc`
- `phase3/tests/__pycache__/test_sites.cpython-312.pyc`
- `phase3/vendor/alien_syntax/src/__pycache__/canonicalize.cpython-312.pyc`
- `phase3/vendor/alien_syntax/src/__pycache__/generate_corpus.cpython-312.pyc`
- `phase3/vendor/alien_syntax/src/__pycache__/phi.cpython-312.pyc`
- `phase3/vendor/alien_syntax/src/__pycache__/transpiler.cpython-312.pyc`
- `phase3/vendor/grammar_and_3DOM_client/__pycache__/fixture_scene.cpython-312.pyc`
- `phase3/vendor/grammar_and_3DOM_client/__pycache__/tasks.cpython-312.pyc`
- `phase3/vendor/grammar_and_3DOM_client/conformance/__pycache__/refgrammar.cpython-312.pyc`
- `phase3_2/scripts/__pycache__/run_arm_a.cpython-312.pyc`
- `phase3_2/src/phase3_2/__pycache__/__init__.cpython-312.pyc`
- `phase3_2/src/phase3_2/__pycache__/_vendor.cpython-312.pyc`
- `phase3_2/src/phase3_2/__pycache__/analysis.cpython-312.pyc`
- `phase3_2/src/phase3_2/__pycache__/backends.cpython-312.pyc`
- `phase3_2/src/phase3_2/__pycache__/deltafam.cpython-312.pyc`
- `phase3_2/src/phase3_2/__pycache__/margins.cpython-312.pyc`
- `phase3_2/src/phase3_2/__pycache__/prompts.cpython-312.pyc`
- `phase3_2/src/phase3_2/__pycache__/runmeta.cpython-312.pyc`
- `phase3_2/src/phase3_2/__pycache__/sampling.cpython-312.pyc`
- `phase3_2/src/phase3_2/__pycache__/sites2.cpython-312.pyc`
- `phase3_2/src/phase3_2/__pycache__/templates.cpython-312.pyc`
- `phase3_2/tests/__pycache__/test_phase3_2.cpython-312.pyc`

</details>

---

## Old paths that remain on purpose

These files still name an old path. They were **not edited**, because each is a record:

- frozen code;
- the append-only preregistration;
- an output of a past run;
- an immutable experiment log;
- an archived document;
- a dated record of earlier changes.

The new location is on the right.

| file | old path named there | it is now |
|---|---|---|
| `phase3_2/PREREGISTRATION.md` (deviation D13, append-only) | `sol/heldout_results_explained/08` | `explanations/phase3_3/heldout_results_explained/08_issues_and_superseded_numbers.md` |
| `phase3_2/sol/src/p33/prefetch.py` (frozen code, docstring) | `legacy_superseded/prefetch_models.py` | `archive/phase3_2_sol/legacy_superseded/prefetch_models.py` |
| `phase3_2/sol/scripts/paper_figures.py` (a caption), and its output `analysis_addenda/paper_figures/tables/C3_generation.md` | `heldout_results_explained/08` | `explanations/phase3_3/heldout_results_explained/08_issues_and_superseded_numbers.md` |
| `phase3_2/sol/PROMPT_REVIEW.md` (the review of 2026-10-05/07) | `phase3_3/ERRATA.md`; `sol_experiment_explained/08 §1` | `archive/phase3_3_first_laptop_run/ERRATA.md`; `explanations/phase3_3/sol_experiment_explained/08_changes_defects_and_superseded_numbers.md` |
| `phase3_3/sol_results/README.md` | `heldout_results_explained/08` §2 | `explanations/phase3_3/heldout_results_explained/08_issues_and_superseded_numbers.md` |
| `phase3_3/sol_results/dev-20261006a/analysis_revisions/r1-2026-10-07-metric-corrections/analysis_revision.json` (a run record) | `phase3_2/sol/sol_experiment_explained/…` | `explanations/phase3_3/sol_experiment_explained/…` |
| `archive/phase3_3_first_laptop_run/README.md`, `02_theory_and_math.md` | `../phase3/phase3_explained/`, `../phase3_2/phase3_2_explained/` | `explanations/phase3/phase3_explained/`, `explanations/phase3_2/phase3_2_explained/` |
| `archive/phase3_3_first_laptop_run/ERRATA.md` | `phase3_2/sol/local_smoke/` | `archive/phase3_2_sol/local_smoke/` |
| `explanations/phase3_3/sol_experiment_explained/08_changes_defects_and_superseded_numbers.md` (the table of files created on 2026-10-05) | `phase3_2/sol/…local_smoke/, legacy_superseded/, sol_experiment_explained/`; `phase3_3/ERRATA.md` | `archive/phase3_2_sol/…`, `explanations/phase3_3/sol_experiment_explained/`, `archive/phase3_3_first_laptop_run/ERRATA.md` |
| `explanations/phase4/fixes_before_phase4/03_doc_changes_before_after.md` (the quoted diffs of 2026-10-21) | `phase3_2/sol/heldout_results_explained/…`, `phase4/fixes_before_phase4/` | `explanations/phase3_3/heldout_results_explained/…`, `explanations/phase4/fixes_before_phase4/` |
| `run/experiments/…` (the immutable Phase 2 runs: `20260901-233702/AUDIT.md`, `RESULTS.md`, and `tokenizer_avoided/…/metadata/git-status-*.txt`) | `project_status/phase1.md`, `project_status/phase2.md` | `explanations/phase1/phase1.md`, `explanations/phase2/phase2.md` |
| commit messages before 2026-10-22 | any old path | this file |

**Inside `explanations/`, the old labels still read correctly.** The tree mirrors the phases, so a
label written as `phase3/phase3_explained/01` or `phase4/fixes_before_phase4/` is now a path
*within* `explanations/`. A label such as `heldout_results_explained/08` still names the right
document, because folder names were kept.

---

## For Sol

**Sol's checkout keeps working:** the pipeline's paths did not change. Before the next `git pull`
there, two steps are needed.

1. **The caches.** Python regenerates the `.pyc` files that git used to track, and git refuses to
   pull when that would delete files changed locally. If `git status --short` lists only `*.pyc`
   files, run `git checkout -- '*.pyc'` and pull.
2. **The environment lock** `phase3_2/sol/env/requirements.lock.sol.txt` is untracked on Sol, but
   tracked in git since `1750947b` (it was copied from Sol). If git refuses because of it:
   - move it aside;
   - pull;
   - check the two copies are identical.

---

## How it was checked

**Before anything moved:**

- The Phase 4 work was committed (`87402234`), and the moves were made on their own branch.
- Every tracked file was recorded with its checksum: 22,675 files.

**After the moves**, a script looked up each of those 22,675 files at its old or new path:

| result | files |
|---|---:|
| unchanged, same path | 22,443 |
| moved, byte-identical | 153 |
| moved, only link targets changed | 15 |
| moved, with the stale paths updated (listed in the commit) | 7 |
| same path, only link targets changed (`phase3_2/sol/AUDIT.md`) | 1 |
| same path, edited on purpose (four READMEs, `.gitignore`, the Phase 4 script and its regenerated report) | 7 |
| compiled cache, no longer tracked, still on disk | 49 |
| **missing** | **0** |

**What was added:** only the six new documents (`START_HERE.md`, `MOVES.md`,
`explanations/README.md`, `archive/README.md`, `strata_eval/README.md`, `phase3_3/README.md`).
Nothing else appeared.

**The pinned parts still work:**

- **The freeze:** the drift check (`splits.frozen_drift`) finds no change in the 44 frozen source
  files, the materials or the model pins.
- **The tests:** Phase 3.3 pipeline 147/147; Phase 4 6/6; Phase 3 54/54; Phase 3.2 36/36.
- **The Phase 4 script** reproduces its nine CSVs byte for byte.
- **The links:** 707 relative links in 275 documents all resolve, except three in a third-party
  library inside the editor, which were broken before.
- **Fixed by the move:** 12 links in `experiment_math.md` that were already broken (the file had
  once been moved without them).
