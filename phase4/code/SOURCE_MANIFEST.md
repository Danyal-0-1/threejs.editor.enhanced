# Where every file came from

The copied files below came from commit `3da4511d`, by a one-time builder, on 2026-10-22.
Phase 4's own settings were applied afterwards, the same day; `tools/verify_copy.py` lists the
files they changed ("changed since the copy").

- **The same record, with checksums:** [`source_manifest.json`](source_manifest.json).
- **To check it again at any time:** `run/.venv/bin/python phase4/code/tools/verify_copy.py`.
  With `--diff <file>` it prints the exact differences of one file from its origin.

| change | meaning |
|---|---|
| identical | identical to the origin, byte for byte |
| imports | only import lines changed (the line numbers are the same) |
| imports and paths | import lines, plus the path lines listed in source_manifest.json |
| paths | the path lines listed in source_manifest.json (Sol scripts) |
| subset | a subset of the origin: the tests of code that was not copied are left out |

## The 109 copied files

### at the top

| file here | came from | change |
|---|---|---|
| `run.py` | `phase3_2/sol/scripts/p33.py` | imports and paths |

### `configs/`

| file here | came from | change |
|---|---|---|
| `configs/phase3_3/dev.json` | `phase3_2/sol/configs/dev.json` | identical (moved from configs/ on 2026-10-22: Phase 3.3's configs, kept as a record) |
| `configs/phase3_3/heldout.json` | `phase3_2/sol/configs/heldout.json` | identical (moved from configs/ on 2026-10-22: Phase 3.3's configs, kept as a record) |
| `configs/phase3_3/local_smoke.json` | `phase3_2/sol/configs/local_smoke.json` | identical (moved from configs/ on 2026-10-22: Phase 3.3's configs, kept as a record) |
| `configs/phase3_3/smoke.json` | `phase3_2/sol/configs/smoke.json` | identical (Phase 3.3's smoke config, kept with its other configs as a record) |
| `configs/smoke.json` | `phase3_2/sol/configs/smoke.json` | identical (kept at configs/ as Phase 4's smoke config (a development cell)) |

### `p4/language/`

| file here | came from | change |
|---|---|---|
| `p4/language/backends.py` | `phase3_2/src/phase3_2/backends.py` | imports |
| `p4/language/deltafam.py` | `phase3_2/src/phase3_2/deltafam.py` | imports |
| `p4/language/templates.py` | `phase3_2/src/phase3_2/templates.py` | imports |

### `p4/sites/`

| file here | came from | change |
|---|---|---|
| `p4/sites/sampling.py` | `phase3_2/src/phase3_2/sampling.py` | imports |
| `p4/sites/sites.py` | `phase3/src/phase3/sites.py` | imports |
| `p4/sites/sites2.py` | `phase3_2/src/phase3_2/sites2.py` | imports |

### `p4/prompts/`

| file here | came from | change |
|---|---|---|
| `p4/prompts/demos.py` | `phase3_2/sol/src/p33/demos.py` | identical |
| `p4/prompts/prompts.py` | `phase3_2/src/phase3_2/prompts.py` | imports |

### `p4/scoring/`

| file here | came from | change |
|---|---|---|
| `p4/scoring/fakes.py` | `phase3_2/sol/src/p33/fakes.py` | imports |
| `p4/scoring/fertility.py` | `phase3_2/sol/src/p33/fertility.py` | imports |
| `p4/scoring/margins.py` | `phase3_2/src/phase3_2/margins.py` | imports |
| `p4/scoring/models.py` | `phase3/src/phase3/models.py` | identical |
| `p4/scoring/scorers.py` | `phase3_2/sol/src/p33/scorers.py` | imports |
| `p4/scoring/scoring.py` | `phase3/src/phase3/scoring.py` | imports |

### `p4/experiments/`

| file here | came from | change |
|---|---|---|
| `p4/experiments/armb.py` | `phase3_2/sol/src/p33/armb.py` | imports |
| `p4/experiments/h5.py` | `phase3_2/sol/src/p33/h5.py` | imports |
| `p4/experiments/pipeline.py` | `phase3_2/sol/src/p33/pipeline.py` | imports |

### `p4/analysis/`

| file here | came from | change |
|---|---|---|
| `p4/analysis/analysis.py` | `phase3_2/src/phase3_2/analysis.py` | identical |
| `p4/analysis/h2.py` | `phase3_2/sol/src/p33/h2.py` | imports |
| `p4/analysis/h4.py` | `phase3_2/sol/src/p33/h4.py` | imports |
| `p4/analysis/kstar.py` | `phase3_2/sol/src/p33/kstar.py` | identical |
| `p4/analysis/power.py` | `phase3_2/sol/src/p33/power.py` | imports |

### `p4/reporting/`

| file here | came from | change |
|---|---|---|
| `p4/reporting/artifacts.py` | `phase3_2/sol/src/p33/artifacts.py` | identical |
| `p4/reporting/export.py` | `phase3_2/sol/src/p33/export.py` | imports |
| `p4/reporting/plots.py` | `phase3_2/sol/src/p33/plots.py` | imports |
| `p4/reporting/reports.py` | `phase3_2/sol/src/p33/reports.py` | imports |

### `p4/governance/`

| file here | came from | change |
|---|---|---|
| `p4/governance/freeze.py` | `phase3_2/sol/src/p33/freeze.py` | imports |
| `p4/governance/provenance.py` | `phase3_2/sol/src/p33/provenance.py` | imports |
| `p4/governance/registry.py` | `phase3_2/sol/src/p33/registry.py` | identical |
| `p4/governance/splits.py` | `phase3_2/sol/src/p33/splits.py` | imports |

### `p4/runtime/`

| file here | came from | change |
|---|---|---|
| `p4/runtime/config.py` | `phase3_2/sol/src/p33/config.py` | imports and paths |
| `p4/runtime/prefetch.py` | `phase3_2/sol/src/p33/prefetch.py` | imports |
| `p4/runtime/preflight.py` | `phase3_2/sol/src/p33/preflight.py` | imports |
| `p4/runtime/shards.py` | `phase3_2/sol/src/p33/shards.py` | imports |

### `dsl/`

| file here | came from | change |
|---|---|---|
| `dsl/PATCHES/tasks.op_selection.md` | `phase3/PATCHES/tasks.op_selection.md` | identical |
| `dsl/alien_syntax/candidates/phi_alpha.json` | `phase3/vendor/alien_syntax/candidates/phi_alpha.json` | identical |
| `dsl/alien_syntax/candidates/phi_beta.json` | `phase3/vendor/alien_syntax/candidates/phi_beta.json` | identical |
| `dsl/alien_syntax/candidates/phi_d25s1.json` | `phase3/vendor/alien_syntax/candidates/phi_d25s1.json` | identical |
| `dsl/alien_syntax/candidates/phi_d25s2.json` | `phase3/vendor/alien_syntax/candidates/phi_d25s2.json` | identical |
| `dsl/alien_syntax/candidates/phi_d25s3.json` | `phase3/vendor/alien_syntax/candidates/phi_d25s3.json` | identical |
| `dsl/alien_syntax/candidates/phi_d50s1.json` | `phase3/vendor/alien_syntax/candidates/phi_d50s1.json` | identical |
| `dsl/alien_syntax/candidates/phi_d50s2.json` | `phase3/vendor/alien_syntax/candidates/phi_d50s2.json` | identical |
| `dsl/alien_syntax/candidates/phi_d50s3.json` | `phase3/vendor/alien_syntax/candidates/phi_d50s3.json` | identical |
| `dsl/alien_syntax/candidates/phi_d75s1a.json` | `phase3/vendor/alien_syntax/candidates/phi_d75s1a.json` | identical |
| `dsl/alien_syntax/candidates/phi_d75s2a.json` | `phase3/vendor/alien_syntax/candidates/phi_d75s2a.json` | identical |
| `dsl/alien_syntax/candidates/phi_d75s3a.json` | `phase3/vendor/alien_syntax/candidates/phi_d75s3a.json` | identical |
| `dsl/alien_syntax/candidates/phi_delta.json` | `phase3/vendor/alien_syntax/candidates/phi_delta.json` | identical |
| `dsl/alien_syntax/candidates/phi_gamma.json` | `phase3/vendor/alien_syntax/candidates/phi_gamma.json` | identical |
| `dsl/alien_syntax/grammar/render_grammar.py` | `phase3/vendor/alien_syntax/grammar/render_grammar.py` | identical |
| `dsl/alien_syntax/grammar/templates/grammar.iso.template.ebnf` | `phase3/vendor/alien_syntax/grammar/templates/grammar.iso.template.ebnf` | identical |
| `dsl/alien_syntax/grammar/templates/grammar.lark.template` | `phase3/vendor/alien_syntax/grammar/templates/grammar.lark.template` | identical |
| `dsl/alien_syntax/grammar/templates/grammar.w3c.template.ebnf` | `phase3/vendor/alien_syntax/grammar/templates/grammar.w3c.template.ebnf` | identical |
| `dsl/alien_syntax/src/canonicalize.py` | `phase3/vendor/alien_syntax/src/canonicalize.py` | identical |
| `dsl/alien_syntax/src/generate_corpus.py` | `phase3/vendor/alien_syntax/src/generate_corpus.py` | identical |
| `dsl/alien_syntax/src/heuristics_ir.py` | `phase3/vendor/alien_syntax/src/heuristics_ir.py` | identical |
| `dsl/alien_syntax/src/phi.py` | `phase3/vendor/alien_syntax/src/phi.py` | identical |
| `dsl/alien_syntax/src/transpiler.py` | `phase3/vendor/alien_syntax/src/transpiler.py` | identical |
| `dsl/grammar_and_3DOM_client/3dom_grammar.iso.ebnf` | `phase3/vendor/grammar_and_3DOM_client/3dom_grammar.iso.ebnf` | identical |
| `dsl/grammar_and_3DOM_client/3dom_grammar.w3c.ebnf` | `phase3/vendor/grammar_and_3DOM_client/3dom_grammar.w3c.ebnf` | identical |
| `dsl/grammar_and_3DOM_client/conformance/negative.txt` | `phase3/vendor/grammar_and_3DOM_client/conformance/negative.txt` | identical |
| `dsl/grammar_and_3DOM_client/conformance/positive.txt` | `phase3/vendor/grammar_and_3DOM_client/conformance/positive.txt` | identical |
| `dsl/grammar_and_3DOM_client/conformance/refgrammar.py` | `phase3/vendor/grammar_and_3DOM_client/conformance/refgrammar.py` | identical |
| `dsl/grammar_and_3DOM_client/conformance/vacuous.txt` | `phase3/vendor/grammar_and_3DOM_client/conformance/vacuous.txt` | identical |
| `dsl/grammar_and_3DOM_client/fixture_scene.py` | `phase3/vendor/grammar_and_3DOM_client/fixture_scene.py` | identical |
| `dsl/grammar_and_3DOM_client/ir_schema.json` | `phase3/vendor/grammar_and_3DOM_client/ir_schema.json` | identical |
| `dsl/grammar_and_3DOM_client/tasks.py` | `phase3/vendor/grammar_and_3DOM_client/tasks.py` | identical |
| `dsl/grammar_and_3DOM_client/terminals.json` | `phase3/vendor/grammar_and_3DOM_client/terminals.json` | identical |

### `tests/`

| file here | came from | change |
|---|---|---|
| `tests/_helpers.py` | `phase3_2/sol/tests/_helpers.py` | imports |
| `tests/run_tests.py` | `phase3_2/sol/tests/run_tests.py` | paths |
| `tests/test_analysis.py` | `phase3_2/sol/tests/test_analysis.py` | imports |
| `tests/test_e2e.py` | `phase3_2/sol/tests/test_e2e.py` | imports |
| `tests/test_metric_and_report_corrections.py` | `phase3_2/sol/tests/test_metric_and_report_corrections.py` | imports |
| `tests/test_model_scale.py` | `phase3_2/sol/tests/test_model_scale.py` | imports and paths |
| `tests/test_phase3_2.py` | `phase3_2/tests/test_phase3_2.py` | imports and paths |
| `tests/test_phase3_scoring.py` | `phase3/tests/test_pipeline.py` | subset |
| `tests/test_prereg_env.py` | `phase3_2/sol/tests/test_prereg_env.py` | imports and paths |
| `tests/test_scorer_repair.py` | `phase3/tests/test_scorer_repair.py` | imports and paths |
| `tests/test_shards_resume.py` | `phase3_2/sol/tests/test_shards_resume.py` | imports and paths |
| `tests/test_sites.py` | `phase3/tests/test_sites.py` | imports and paths |
| `tests/test_splits_freeze.py` | `phase3_2/sol/tests/test_splits_freeze.py` | imports and paths |
| `tests/test_stop_ship.py` | `phase3_2/sol/tests/test_stop_ship.py` | imports |

### `tools/`

| file here | came from | change |
|---|---|---|
| `tools/analysis_revision.py` | `phase3_2/sol/scripts/analysis_revision.py` | imports and paths |
| `tools/build_materials.py` | `phase3_2/scripts/build_materials.py` | imports and paths |

### `sol/`

| file here | came from | change |
|---|---|---|
| `sol/env/README.md` | `phase3_2/sol/env/README.md` | identical |
| `sol/env/activate.sh` | `phase3_2/sol/env/activate.sh` | identical |
| `sol/env/make_env.sh` | `phase3_2/sol/env/make_env.sh` | identical |
| `sol/env/requirements.in` | `phase3_2/sol/env/requirements.in` | identical |
| `sol/env/requirements.lock.laptop.txt` | `phase3_2/sol/env/requirements.lock.laptop.txt` | identical |
| `sol/env/requirements.lock.sol.txt` | `phase3_2/sol/env/requirements.lock.sol.txt` | identical |
| `sol/jobs/arm_b.slurm` | `phase3_2/sol/jobs/arm_b.slurm` | paths |
| `sol/jobs/cpu_tests.slurm` | `phase3_2/sol/jobs/cpu_tests.slurm` | paths |
| `sol/jobs/dev_analyze.slurm` | `phase3_2/sol/jobs/dev_analyze.slurm` | paths |
| `sol/jobs/dev_arm_a.slurm` | `phase3_2/sol/jobs/dev_arm_a.slurm` | paths |
| `sol/jobs/dev_freeze.slurm` | `phase3_2/sol/jobs/dev_freeze.slurm` | paths |
| `sol/jobs/dev_primary.slurm` | `phase3_2/sol/jobs/dev_primary.slurm` | paths |
| `sol/jobs/final_export.slurm` | `phase3_2/sol/jobs/final_export.slurm` | paths |
| `sol/jobs/h5.slurm` | `phase3_2/sol/jobs/h5.slurm` | paths |
| `sol/jobs/heldout_eval.slurm` | `phase3_2/sol/jobs/heldout_eval.slurm` | paths |
| `sol/jobs/prefetch.slurm` | `phase3_2/sol/jobs/prefetch.slurm` | paths |
| `sol/jobs/smoke.slurm` | `phase3_2/sol/jobs/smoke.slurm` | paths |
| `sol/sol.env` | `phase3_2/sol/sol.env` | paths |
| `sol/submit.sh` | `phase3_2/sol/submit.sh` | paths |
| `sol/submit_chain.sh` | `phase3_2/sol/submit_chain.sh` | paths |

## The 24 new files (written for this folder, not copied)

| file | what it is |
|---|---|
| `README.md` | the map of this folder |
| `SOURCE_MANIFEST.md` | this file |
| `source_manifest.json` | the same record with checksums, read by tools/verify_copy.py |
| `p4/paths.py` | where everything is; replaces p33/_paths.py, phase3_2/_vendor.py and phase3/_vendor.py |
| `p4/__init__.py` | the package, rewritten from p33/__init__.py |
| `p4/language/__init__.py` | the stage's file list, in reading order |
| `p4/sites/__init__.py` | the stage's file list, in reading order |
| `p4/prompts/__init__.py` | the stage's file list, in reading order |
| `p4/scoring/__init__.py` | the stage's file list, in reading order |
| `p4/experiments/__init__.py` | the stage's file list, in reading order |
| `p4/analysis/__init__.py` | the stage's file list, in reading order |
| `p4/reporting/__init__.py` | the stage's file list, in reading order |
| `p4/governance/__init__.py` | the stage's file list, in reading order |
| `p4/runtime/__init__.py` | the stage's file list, in reading order |
| `dsl/README.md` | what each language file is |
| `configs/README.md` | what each config is |
| `tools/verify_copy.py` | checks every file against its origin |
| `tools/compare_with_phase3_3.py` | runs both pipelines side by side and compares their CSVs |
| `tools/voyager_models.py` | lists the ASU RC API's models and probes what each can measure |
| `VOYAGER.md` | using the ASU RC LLM API in Phase 4 |
| `tests/phase3_3_design.py` | Phase 3.3's registered design, which the copied tests run under |
| `tests/test_phase4_design.py` | the tests of Phase 4's own settings |
| `tests/test_voyager_models.py` | the tests of tools/voyager_models.py, against a stand-in API |
| `.gitignore` | caches, environments and weights stay out of git |
