# Start here

This repository holds two things.

- **Strata**, the editor: a CSS-like language for editing 3D scenes in the browser. Its files
  (`README.md`, `docs/`, `guides/`, `server.js`, `scripts/`) belong to the upstream project
  (`tejaswigowda/threejs.editor.enhanced`); start with [`README.md`](README.md).
- **The research**: what language models do when a language they know well is respelled, so that
  familiar symbols mean something new. It ran in phases 1 to 4, and this page is its map.

---

## Where everything is

| kind | where | what you find there |
|---|---|---|
| **Explanations** | [`explanations/`](explanations/README.md) | every explanation of every phase: theory, mathematics, code walk-throughs, retype plans, glossaries, knowledge checks, results. The README gives a reading order and an index by topic |
| **Code** | [`phase3/`](phase3/README.md), [`phase3_2/`](phase3_2/README.md), [`phase3_2/sol/`](phase3_2/sol/README.md), [`phase4/code/`](phase4/code/README.md) (the pipeline for the next experiment, a verified copy organized by stage); the Phase 1 and 2 originals in [`grammar_and_3DOM_client/`](grammar_and_3DOM_client/) and [`alien_syntax/`](alien_syntax/) | everything needed to run the experiment: source, materials, configs, Slurm jobs, tests. **Pinned:** never move it (below) |
| **Results** | [`phase3_3/sol_results/`](phase3_3/sol_results/README.md) | every run on ASU Sol (development, held-out, setup, smoke), with the later analyses in each run's `analysis_addenda/` (scale analysis, paper figures, exploratory checks, Phase 4 fixes) |
| | [`run/experiments/`](run/experiments/README.md) | the Phase 2 experiments |
| | `phase3/outputs/`, `phase3_2/outputs/` | the laptop runs of Phases 3 and 3.2, cited as evidence in the audit |
| **Records** | [`phase3_2/PREREGISTRATION.md`](phase3_2/PREREGISTRATION.md) | the preregistration and its dated deviations D1–D13 |
| | [`phase4/PREREGISTRATION.md`](phase4/PREREGISTRATION.md) | Phase 4's preregistration: a **draft**. The Phase 4 pipeline reads it and will not freeze until it is registered |
| | [`phase3_2/sol/AUDIT.md`](phase3_2/sol/AUDIT.md), [`phase3_2/sol/PROMPT_REVIEW.md`](phase3_2/sol/PROMPT_REVIEW.md) | how the Sol pipeline was audited, and what the briefs got wrong |
| | [`phase3/SOURCE_MANIFEST.md`](phase3/SOURCE_MANIFEST.md) | where every vendored file came from |
| **Archive** | [`archive/`](archive/README.md) | superseded or repeated material. Nothing was deleted; nothing in it is needed to continue |
| **Editor AI eval** | [`strata_eval/`](strata_eval/README.md) | your eval-matrix harness for the editor's AI layer, separate from the research |
| **What moved on 2026-10-22** | [`MOVES.md`](MOVES.md) | the old and new path of every moved file |

---

## The phases

| phase | the question | code | explanations | results | status |
|---|---|---|---|---|---|
| 1 | Formalise the 3DOM language as a grammar | `grammar_and_3DOM_client/` | [phase1](explanations/phase1/phase1.md) | its conformance gates | done |
| 2 | Build a transpiler for respelled ("alien") versions of it; first model runs | `alien_syntax/`, `run/` | [phase2](explanations/phase2/phase2.md) | `run/experiments/` | closed, no winner |
| 3 | Find the collision sites, score them, predict risk, repair | `phase3/` | [phase3](explanations/phase3/phase3_explained/00_complete_phase3_guide.md) | `phase3/outputs/` | done; its scorer is reused, frozen, by 3.3 |
| 3.2 | New materials, a second grammar, a better margin; the preregistration | `phase3_2/` | [phase3_2](explanations/phase3_2/phase3_2_explained/00_complete_phase3_2_guide.md) | `phase3_2/outputs/` | done; preregistered 2026-10-02 |
| 3.3 | The preregistered study on ASU Sol: 21 models, held-out mappings | `phase3_2/sol/` | [design](explanations/phase3_3/sol_experiment_explained/00_complete_guide.md), [results](explanations/phase3_3/heldout_results_explained/00_complete_results.md) | `phase3_3/sol_results/` | complete, 2026-10-09 |
| 4 | Fix what 3.3 left open, then plan new studies | `phase4/code/` (the pipeline), `phase4/scripts/` (step 0) | [fixes](explanations/phase4/fixes_before_phase4/README.md) | `…/heldout-20261007a/analysis_addenda/phase4_fixes/` | step 0 done, 2026-10-21; own settings 2026-10-22; preregistration in draft |

**If you only read one thing about the current experiment:**
[`explanations/phase3_3/sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md`](explanations/phase3_3/sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md),
then [`explanations/phase3_3/heldout_results_explained/00_complete_results.md`](explanations/phase3_3/heldout_results_explained/00_complete_results.md).

---

## Why some names look wrong, and must stay

**Phase 3.3's code lives in `phase3_2/sol/`, and its results in `phase3_3/sol_results/`.** The
pipeline was built inside Phase 3.2's folder, and the freeze then pinned it there.

**Never move or rename these.** Moving one breaks something, even when no byte changes.

| path | why it is pinned |
|---|---|
| `phase3/src/phase3/`, `phase3_2/src/phase3_2/`, `phase3_2/sol/src/p33/`, `phase3_2/sol/scripts/p33.py` | the development freeze (`phase3_3/sol_results/dev-20261006a/DEV_FREEZE.json`) records these 44 files by path. On every held-out access, the pipeline re-hashes them and refuses if any differs or is missing |
| `phase3/vendor/` | the materials (lexicons, grammar, terminals). The frozen code finds them by their position next to `phase3_2/`, and their hashes are in the freeze |
| `phase3_2/PREREGISTRATION.md` | the frozen code reads it by this path. Its text above "Deviations" is frozen; deviations are only appended |
| the rest of `phase3_2/sol/` | its configs, jobs and env are used by the command-line tool, by Slurm and by Sol's checkout |
| `run/.venv` | the Python environment every command uses. A virtual environment stops working if it is moved |
| `run/experiments/` | the Phase 2 runs, declared immutable: their logs record their own paths |
| `alien_syntax/`, `grammar_and_3DOM_client/` | the originals that `phase3/vendor/` copies. `phase3/scripts/vendor_sync.py --check` and `phase3/SOURCE_MANIFEST.md` point at them |
| `phase3_3/sol_results/` | the local mirror of Sol. Every analysis script, the restore script and dozens of docs use this path |
| `README.md`, `docs/`, `guides/`, `server.js`, `scripts/`, `.gitignore` | upstream's editor files. Keeping them in place keeps the fork easy to sync |

---

## How to run things

Everything runs from the repository root with the project environment, `run/.venv`. It is built
as in [`run/run.md`](run/run.md) ("Full venv"); on Sol, the environment comes from
[`phase3_2/sol/env/`](phase3_2/sol/env/README.md).

```bash
# after a fresh clone: restore the four result files stored gzipped (it checks every byte)
bash phase3_3/sol_results/restore_large_files.sh heldout-20261007a

# the test suites
run/.venv/bin/python phase3_2/sol/tests/run_tests.py            # Phase 3.3 pipeline: 147 tests (about 7 min)
run/.venv/bin/python phase4/tests/run_tests.py                  # Phase 4: 6
(cd phase3 && ../run/.venv/bin/python tests/run_tests.py)       # Phase 3: 54
(cd phase3_2 && ../run/.venv/bin/python tests/run_tests.py)     # Phase 3.2: 36

# Phase 4, step 0: the post-hoc fixes (CPU, about 40 s; writes only its own addenda folder)
run/.venv/bin/python phase4/scripts/fix_heldout_problems.py
```

- **Re-deriving the Phase 3.3 analyses locally** (scale analysis, paper figures, exploratory
  checks): the exact commands are in
  [`explanations/phase3_3/heldout_results_explained/03_code_and_pipeline.md`](explanations/phase3_3/heldout_results_explained/03_code_and_pipeline.md)
  §11.
- **Running anything on Sol:** the runbook, [`phase3_2/sol/README.md`](phase3_2/sol/README.md).
