# phase4/code — the pipeline for the next experiment

This folder holds all the code the next experiment needs:

- the pipeline itself;
- the language: grammar, lexicons and the test programs;
- the run configurations;
- the Sol jobs;
- the tests.

It is organized by stage, so the code can be read from top to bottom.

**What it is.** A copy of the Phase 3.3 pipeline, made on 2026-10-22 from commit `3da4511d`.
Phase 3.3's own code stays where it is, untouched and frozen (see
[`../../START_HERE.md`](../../START_HERE.md) for why). This copy is where Phase 4 will make its
changes.

- **Only the import lines changed**, plus a few listed path lines.
- **Every line kept its line number.** A line reference in the explanations, such as "`h5.py`
  125–173" in a retype plan, points to the same lines here.
- **It is proven equivalent** to the original (section "How the copy was checked").
- **Nothing has been changed for Phase 4 yet,** and nothing has run on Sol from this copy.

---

## The layout

```
phase4/code/
├── README.md              this map
├── run.py                 the one command-line entry point (Phase 3.3's scripts/p33.py)
├── configs/               what a run scores: dev.json, heldout.json, smoke.json, local_smoke.json
├── p4/                    the pipeline: one folder per stage, in the order the data flows
│   ├── paths.py           where everything is (replaces Phase 3.3's three path modules)
│   ├── language/          the two grammar families, the 80 programs, the lexicon family
│   ├── sites/             decision sites and their collision classes; balanced selection
│   ├── prompts/           the rule table and its controls; leakage-free worked examples
│   ├── scoring/           one model's margin at one site
│   ├── experiments/       Arm A and the extinction ladder, Arm B, H5
│   ├── analysis/          H4, k*, H2, the template-cluster bootstrap, power
│   ├── reporting/         a run's CSVs, figures and reports
│   ├── governance/        the model registry, the registered split, freeze and unlock, provenance
│   └── runtime/           configuration and locations, crash-safe shards, preflight, downloads
├── dsl/                   the language: grammar, lexicons, test programs, transpiler (dsl/README.md)
├── tests/                 the tests of all of the above
├── tools/                 build_materials, analysis_revision, verify_copy, compare_with_phase3_3
├── sol/                   running on ASU Sol: jobs/, env/, sol.env, submit.sh, submit_chain.sh
├── SOURCE_MANIFEST.md     every file: where it came from, and what changed (readable)
└── source_manifest.json   the same, with both checksums (read by tools/verify_copy.py)
```

Each folder of `p4/` has an `__init__.py` that lists its files in reading order.

---

## Read it in this order

The explanations named below were written for Phase 3.3's folders, and their file and line
references hold here:

- **design:** `sol_experiment_explained/`;
- **materials and margins:** `phase3_2_explained/`;
- **sites and scoring:** `phase3_explained/`;
- **the analysis code behind the results:** `heldout_results_explained/`.

For the retype plans, start with
[`sol_experiment_explained/04`](../../explanations/phase3_3/sol_experiment_explained/04_retyping_and_reading_plan.md).
For one site traced through every step of the code, read
[`EXPERIMENT_IN_ONE_FILE.md`](../../explanations/phase3_3/sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md).

### 0. What a run is

| file | what it does | came from |
|---|---|---|
| [`configs/dev.json`](configs/dev.json), [`configs/heldout.json`](configs/heldout.json) | the models, lexicons, grammar families, site limits and seeds of a run | `phase3_2/sol/configs/` |
| [`p4/runtime/config.py`](p4/runtime/config.py) | `RunConfig`, the fields of those files; where things are (environment variables); hashing | `p33/config.py` |
| [`p4/governance/registry.py`](p4/governance/registry.py) | every model the programme may touch, with its base/instruct pair and GPU class | `p33/registry.py` |

### 1. The language: `dsl/` and `p4/language/`

| file | what it does | came from |
|---|---|---|
| [`dsl/`](dsl/README.md) | the grammar (ISO and W3C EBNF), the terminals, the lexicons, the conformance test programs, and `phi`, `transpiler` and `canonicalize` | `phase3/vendor/` (byte-identical) |
| [`p4/language/backends.py`](p4/language/backends.py) | the two grammar families: `dom` (jQuery-style chaining) and `blk` (block syntax) | `phase3_2/backends.py` |
| [`p4/language/templates.py`](p4/language/templates.py) | the 80 programs, built as IR and rendered in each family | `phase3_2/templates.py` |
| [`p4/language/deltafam.py`](p4/language/deltafam.py) | the lexicon family `d25s1` … `d75s3a`, by remap density and seed | `phase3_2/deltafam.py` |

Read: [`phase1.md`](../../explanations/phase1/phase1.md) (the grammar),
[`phase2.md`](../../explanations/phase2/phase2.md) (lexicons, transpiler),
[`phase3_2_explained/03`](../../explanations/phase3_2/phase3_2_explained/03_code_and_pipeline.md).

### 2. Sites: `p4/sites/`

| file | what it does | came from |
|---|---|---|
| [`sites.py`](p4/sites/sites.py) | where a decision is made, and its mechanical collision class | `phase3/sites.py` |
| [`sites2.py`](p4/sites/sites2.py) | the same classifier, for both grammar families | `phase3_2/sites2.py` |
| [`sampling.py`](p4/sites/sampling.py) | deterministic, balanced, order-independent site selection | `phase3_2/sampling.py` |

Read: [`phase3_explained/03`](../../explanations/phase3/phase3_explained/03_code_and_pipeline.md),
[`phase3_2_explained/03`](../../explanations/phase3_2/phase3_2_explained/03_code_and_pipeline.md).

### 3. Prompts: `p4/prompts/`

| file | what it does | came from |
|---|---|---|
| [`prompts.py`](p4/prompts/prompts.py) | the rule table shown to the model, the no-rule control and the length-matched control | `phase3_2/prompts.py` |
| [`demos.py`](p4/prompts/demos.py) | the worked examples of the extinction ladder, never containing the target | `p33/demos.py` |

### 4. Scoring: `p4/scoring/`

| file | what it does | came from |
|---|---|---|
| [`margins.py`](p4/scoring/margins.py) | **the scorer:** M = log P(correct) − log P(competitor), from the first divergent token, with an fp32 output head | `phase3_2/margins.py` |
| [`scorers.py`](p4/scoring/scorers.py) | loads one model, offline, from its pinned snapshot | `p33/scorers.py` |
| [`fakes.py`](p4/scoring/fakes.py) | a deterministic, GPU-free scorer for the tests | `p33/fakes.py` |
| [`fertility.py`](p4/scoring/fertility.py) | tokens per character, for every distinct tokenizer | `p33/fertility.py` |
| [`scoring.py`](p4/scoring/scoring.py), [`models.py`](p4/scoring/models.py) | Phase 3's scorer and model interface. The pipeline uses only `interaction_did` (for H2) | `phase3/` |

### 5. The experiments: `p4/experiments/`

| file | what it does | came from |
|---|---|---|
| [`pipeline.py`](p4/experiments/pipeline.py) | plans the cells, scores them, stores the shards: Arm A (the rule table against its controls) and the extinction ladder | `p33/pipeline.py` |
| [`armb.py`](p4/experiments/armb.py) | Arm B: natural-language requests, free generation, five outcome buckets, reach | `p33/armb.py` |
| [`h5.py`](p4/experiments/h5.py) | H5: targeted, random and global respelling arms, each proved to keep the meaning | `p33/h5.py` |

Read: [`sol_experiment_explained/03`](../../explanations/phase3_3/sol_experiment_explained/03_code_and_pipeline.md),
[`heldout_results_explained/04`](../../explanations/phase3_3/heldout_results_explained/04_retyping_plan.md).

### 6. Analysis: `p4/analysis/`

| file | what it does | came from |
|---|---|---|
| [`analysis.py`](p4/analysis/analysis.py) | the template-cluster bootstrap, and Holm | `phase3_2/analysis.py` |
| [`h4.py`](p4/analysis/h4.py) | H4: the risk score, baselines, AUROC / AP / P@k with ties handled, calibration, the criteria | `p33/h4.py` |
| [`kstar.py`](p4/analysis/kstar.py) | k*: the first switch, the lasting switch, censoring, Kaplan–Meier | `p33/kstar.py` |
| [`h2.py`](p4/analysis/h2.py) | H2, the prior × context interaction: not testable, its machinery kept | `p33/h2.py` |
| [`power.py`](p4/analysis/power.py) | template-clustered power, from development data only | `p33/power.py` |

Read: [`heldout_results_explained/02`](../../explanations/phase3_3/heldout_results_explained/02_mathematics_and_statistics.md)
(every formula, with numbers from the run),
[`experiment_math.md`](../../explanations/phase3_3/sol_experiment_explained/experiment_math.md).

### 7. Reporting: `p4/reporting/`

| file | what it does | came from |
|---|---|---|
| [`export.py`](p4/reporting/export.py) | the 19 CSVs, built only from merged shards and manifests | `p33/export.py` |
| [`plots.py`](p4/reporting/plots.py) | the 12 diagnostic figures, from the CSVs only | `p33/plots.py` |
| [`reports.py`](p4/reporting/reports.py) | the 10 Markdown reports | `p33/reports.py` |
| [`artifacts.py`](p4/reporting/artifacts.py) | the list of what an export must produce | `p33/artifacts.py` |

### 8. Governance: `p4/governance/`

| file | what it does | came from |
|---|---|---|
| [`splits.py`](p4/governance/splits.py) | the registered split, the size ceiling, the freeze lock, unlock, the drift check | `p33/splits.py` |
| [`freeze.py`](p4/governance/freeze.py) | builds `DEV_FREEZE.json` from a complete development run | `p33/freeze.py` |
| [`provenance.py`](p4/governance/provenance.py) | job manifests: git, Slurm, GPU and package identity on every shard | `p33/provenance.py` |
| [`registry.py`](p4/governance/registry.py) | (see 0) | `p33/registry.py` |

### 9. Runtime: `p4/runtime/`

| file | what it does | came from |
|---|---|---|
| [`config.py`](p4/runtime/config.py) | (see 0) | `p33/config.py` |
| [`shards.py`](p4/runtime/shards.py) | crash-safe storage: atomic shards, resume, deterministic merge | `p33/shards.py` |
| [`preflight.py`](p4/runtime/preflight.py) | refuses a GPU job that would waste its allocation | `p33/preflight.py` |
| [`prefetch.py`](p4/runtime/prefetch.py) | download-only model staging, with pinned revisions | `p33/prefetch.py` |

### The entry point: [`run.py`](run.py)

Every command of a run, in order:

```
run.py dev init    --config configs/dev.json --run dev-…    runtime/config.py; governance/splits.py
run.py dev run     --run dev-… --experiment arm_a           experiments/pipeline.py: sites/ + prompts/ → scoring/margins.py → runtime/shards.py
run.py dev run     --run dev-… --experiment primary         the extinction ladder (prompts/demos.py)
run.py dev run     --run dev-… --experiment armb | h5       experiments/armb.py, experiments/h5.py
run.py dev analyze --run dev-…                              merge → reporting/export.py (analysis/) → plots.py, reports.py
run.py dev freeze  --run dev-…                              governance/freeze.py → DEV_FREEZE.json
run.py heldout init | unlock | run | analyze                governance/splits.py: locked until unlock; drift check on every access
```

---

## How to run it

```bash
# from the repository root, with the project environment
run/.venv/bin/python phase4/code/tests/run_tests.py                 # all the tests
run/.venv/bin/python phase4/code/tools/verify_copy.py               # every file against its Phase 3.3 origin
run/.venv/bin/python phase4/code/tools/compare_with_phase3_3.py     # both pipelines side by side (+ --real-dev)
```

- **A run on the laptop, with the fake scorer:** set `P33_RESULTS_ROOT` to a scratch folder and
  `P33_FAKE=1`, then use `run.py` as in the table above.
- **On Sol:** follow Phase 3.3's runbook, [`phase3_2/sol/README.md`](../../phase3_2/sol/README.md),
  with two substitutions: `phase4/code/sol/` for `phase3_2/sol/`, and `../run.py` for
  `scripts/p33.py`. Make the changes of the next section first.

---

## How the copy was checked

Every check below passed on 2026-10-22.

| check | result |
|---|---|
| **every file against its origin** (`tools/verify_copy.py`) | 108 copied files, 0 problems:<br>• 49 identical;<br>• 32 with only import lines changed;<br>• 11 with import lines plus listed path lines;<br>• 15 Sol scripts with listed path lines;<br>• 1 test subset.<br>Apart from the test subset, every Python file kept its line count, and each changed line is an import line or a recorded path edit |
| **the tests** (`tests/run_tests.py`) | **212 passed**, 0 failed, 0 blocked:<br>• 139 from `phase3_2/sol/tests`;<br>• 36 from `phase3_2/tests`;<br>• 37 from `phase3/tests` |
| **both pipelines on the same fake experiment** (`tools/compare_with_phase3_3.py`) | a development run and a held-out run, each with all four experiments, the freeze and the unlock in between: **all 36 CSVs byte-identical**. The 2 `job_provenance.csv` files differ only in each job's process id, clock times and GPU memory |
| **both pipelines on the real development run** (`--real-dev`) | `dev-20261006a`, scored on Sol, with its 19 CSVs rebuilt from the saved measurements by each pipeline: **19 of 19 byte-identical** |
| **where the code loads from** | all 34 modules import; the language modules load only from `dsl/`; nothing loads from the Phase 3.3 folders |
| **Phase 3.3 untouched** | the freeze's drift check on the original code is empty, and no file outside `phase4/code/` changed except three docs that now point here |

**One lesson from the comparison.** A run's config hash includes the path of its freeze file,
and every cell key is built from that hash. So two held-out runs whose configs name their freeze
by different absolute paths get different cell keys, even when every measured value is the same.
The tool therefore names the freeze by a relative path. Keep this in mind when comparing runs.

---

## Before the first Phase 4 run: what must change

None of these is changed yet, on purpose: the copy first had to be proven identical. Make each
change with a record, then run the tests and `tools/compare_with_phase3_3.py`, which shows
exactly which outputs the change moved.

1. **Its own experiment folder.** `p4/runtime/config.py` and `sol/sol.env` still default to
   `$HOME/phase3-3_experiment_sol`, and the environment variables are still named `P33_*`. Left
   as they are, a Phase 4 run on Sol would write into Phase 3.3's results folder.
2. **Its own preregistration.** `p4/paths.py` (`PHASE3_2_ROOT`) points `governance/freeze.py`
   and `reporting/reports.py` at `phase3_2/PREREGISTRATION.md`.
3. **Its own split and models:**
   - `p4/governance/splits.py` (`DEV_LEXICONS`, `HELDOUT_LEXICONS`, the size ceiling);
   - `p4/governance/registry.py`;
   - `configs/`.
4. **Its own version label:** `SCHEMA_VERSION = "p33/1"` in `p4/__init__.py`.
5. **Freeze the language code too.** `runtime/config.py` `source_hashes()` hashes `p4/` and
   `run.py`. The language files in `dsl/` are covered only through the materials hash (lexicons,
   terminals, templates), as in Phase 3.3, so the `dsl/*.py` files are not.
6. **The study itself.** For example, a preregistered repaired-site metric for H5, or a second
   language in `p4/language/backends.py` and `dsl/`.

---

## What was not copied, and why

| left out | why |
|---|---|
| `phase3/src/phase3/linter.py`, `outcomes.py`; `phase3_2/src/phase3_2/runmeta.py` | the pipeline never imports them (the import graph from `run.py` never reaches them). The 17 Phase 3 tests that cover `linter.py` and `outcomes.py` stay in `phase3/tests/` |
| `phase3_2/sol/scripts/paper_figures.py`, `scale_analysis.py`, `exploratory_checks.py`, and their tests | analyses of the Phase 3.3 held-out run. Copy and adapt them when Phase 4 has results |
| `phase3_2/scripts/run_arm_a.py`, `run_primary.py` | deprecated wrappers from before the Sol pipeline |
| `phase3/scripts/vendor_sync.py`, `make_delta.py`, `site_census.py` | Phase 3's own maintenance |
| `phase4/scripts/fix_heldout_problems.py` | corrects Phase 3.3's numbers with Phase 3.3's own functions, so it keeps importing the frozen code |
| `phase3_2/sol/README.md`, `AUDIT.md`, `PROMPT_REVIEW.md` | Phase 3.3's runbook and records |

**Only names changed in the code.** Docstrings and comments were not edited (except the usage
lines of `run.py`), so some still name Phase 3.3's folders, such as `phase3_2/_vendor.py` or
`scripts/p33.py`. [`source_manifest.json`](source_manifest.json) gives every file's origin.
