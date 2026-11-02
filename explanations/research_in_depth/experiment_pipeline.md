# How the experiment runs

*A guide to everything around the measurements: configurations, the registered split, the freeze
and the unlock, model pins, crash-safe storage, Slurm jobs on ASU's Sol cluster, the API path for
served models, the export, the analyses after a run, and the tests. Companion to
[`experiment_code.md`](experiment_code.md) (what each measurement computes). Written 2026-10-28.*

The pipeline was built for one property above all: **a number in a CSV can always be traced back,
and nothing can quietly change what it means.** Every section below is one mechanism that serves
that property.

### Jump to a topic

- [The whole run in one picture](#1-the-whole-run-in-one-picture) · [configurations](#2-a-run-configuration) · [the split](#3-the-registered-split-enforced-in-code) · [freeze and unlock](#4-development-freeze-unlock-held-out)
- [models and pins](#5-models-pins-and-preflight) · [storage](#6-crash-safe-storage-shards-markers-merge) · [provenance](#7-provenance-what-every-job-records)
- [Sol](#8-running-on-sol) · [served models](#9-running-served-models-the-api-path) · [the export](#10-the-export-19-csvs-12-plots-10-reports) · [after the run](#11-after-the-run-the-scripts-outside-the-frozen-code)
- [tests](#12-the-tests) · [the real runs](#13-the-real-runs-in-numbers) · [reproducing](#14-reproducing-a-result) · [practice](#15-practice)

---

## 1. The whole run in one picture

```text
 configs/<run>.json ──► run.py <stage> init ──► results/<run_id>/manifests/run_config.json
                                    │                 (config hash; the split checked for every cell)
 run.py prefetch ──► model_pins.json (one revision per model; served: the deployment)
                                    │
 run.py <stage> preflight ──► GPU, precision, versions, space, pins, materials, split: PASS/FAIL
                                    │
 run.py <stage> run --experiment arm_a | primary | armb | h5      (one model per array task)
        │   build_plan ─► cells ─► score ─► raw/shards/<exp>/<cell>.jsonl + checkpoints/<cell>.done.json
        ▼
 run.py merge / validate ──► merged/<exp>.jsonl + .status.json (COMPLETE | PARTIAL | EMPTY)
        ▼
 run.py export ──► csv/ (19) ─► plots/ (12 × png, svg) ─► reports/ (10)
        ▼
 after-run scripts ──► analysis_addenda/  (scale, paper figures, exploratory checks, D13 fixes)

 Governance across it all:
 dev run ─► run.py dev freeze ─► DEV_FREEZE.json (read-only + .sha256)
          ─► run.py heldout init --freeze … ─► run.py heldout unlock --confirm "<phrase>"
          ─► every held-out access re-checks code, materials and pins against the freeze
```

A run lives in one folder, `results/<run_id>/`, with fixed subfolders:
`raw/shards`, `checkpoints`, `merged`, `csv`, `plots`, `reports`, `manifests`, `logs`
([`config.RUN_SUBDIRS`](../../phase4/code/p4/runtime/config.py#L89)), plus `analysis_addenda/`
for the scripts that run after it.

---

## 2. A run configuration

[`RunConfig`](../../phase4/code/p4/runtime/config.py#L115) holds everything that decides what is
measured:

| field | Phase 3.3 held-out value | meaning |
|---|---|---|
| `run_id`, `stage` | `heldout-20261007a`, `heldout` | the id **must** start with its stage (`dev-`, `heldout-`, `smoke-`) |
| `models` | 21 checkpoints | the order fixes the array index: task *i* scores model *i* |
| `families`, `lexicons` | `dom`, `blk`; 5 held-out lexicons | every combination is checked against the split |
| `site_limit` | 0 (every site) | Arm A's sample size |
| `chunk_size` | 64 | sites per cell |
| `dtype`, `lm_head_fp32` | `bfloat16`, true | the model body's precision; the fp32 output head |
| `seeds` | bootstrap 20261002, demo order 20261005, H5 random 1–5, power 20261006 | every random choice is seeded |
| `arm_a` | the three conditions; program NLL on | |
| `primary` | ladder 0–32, paraphrases p0–p2, 400 sites | |
| `armb` | greedy, 192 tokens, 4 examples | |
| `h5` | budget 3, tolerance 0.02 | |
| `analysis` | B = 2000, α = 0.05, unit template, ≥ 8 clusters, P@10 and P@50, 10 ECE bins | |
| `freeze_path` | the development run's `DEV_FREEZE.json` | required for a held-out run |

[`config_hash()`](../../phase4/code/p4/runtime/config.py#L161) is the SHA-256 of every field except
`run_id` and `note`. It is stored at init ([`shards.assert_compatible`](../../phase4/code/p4/runtime/shards.py#L246)),
written into every cell's key, and checked on every resume: a run cannot be continued under a
changed ladder, seed, lexicon list or precision.

The configs themselves are in [`phase4/code/configs/`](../../phase4/code/configs/README.md):
`phase3_3/dev.json` and `phase3_3/heldout.json` (Phase 3.3's, kept as a record), `dev_api.json`
(Phase 4's served-model run), and the smoke configs.

---

## 3. The registered split, enforced in code

### 3.1 Classes

[`splits.classify(family, lexicon, model)`](../../phase4/code/p4/governance/splits.py#L107) returns
one of seven kinds, each with the **label** every output row carries:

| kind | label | Phase 3.3's cells of that kind |
|---|---|---|
| `dev` | DEVELOPMENT | `dom` × {`d25s1`, `d25s2`, `d50s1`, `d50s2`} × Qwen2.5-Coder 0.5B and 1.5B, base and instruct |
| `heldout_mapping` | HELDOUT | the development models on the held-out lexicons, `dom` |
| `heldout_model` | HELDOUT | every other registered model, held-out lexicons, `dom` |
| `heldout_model_weakened` | HELDOUT-WEAKENED | Qwen2.5-Coder 3B, observed before the freeze (D2) |
| `heldout_weak_family` | HELDOUT-WEAK-FAMILY | `blk` × held-out lexicons (D1) |
| `exploratory_contaminated` | EXPLORATORY | `blk` × development lexicons; refused unless allowed |
| `forbidden` | FORBIDDEN | an unregistered family, lexicon or model, or a model above the size ceiling |

### 3.2 Access

[`check_access(stage, family, lexicon, model)`](../../phase4/code/p4/governance/splits.py#L150)
raises `SplitViolation` unless the cell's kind is allowed for the stage: `dev` and `smoke` touch
development cells only; `heldout` touches held-out cells only, and only with a valid unlock in its
run folder. [`enforce_config`](../../phase4/code/p4/governance/splits.py#L181) checks **every**
cell of a configuration, and it runs first in `build_plan`, in `init`, in `preflight` and in
`fertility`: a held-out site is refused before it is even listed.

### 3.3 Phase 4's split

Phase 3.3's held-out results have been read, so nothing can be held out again. In Phase 4's copy,
every Phase 3.3 family, lexicon and model is development, `HELDOUT_LEXICONS` is empty, a held-out
run is refused, a new model is classified held-out until the preregistration decides its role, and
the size ceiling is 600B (served models need no GPU). Phase 3.3's own split is kept in
`tests/phase3_3_design.py`, so the tests can check the machinery against the registered design.

---

## 4. Development, freeze, unlock, held-out

### 4.1 The freeze

`run.py dev freeze --run dev-…` calls [`freeze.build_payload`](../../phase4/code/p4/governance/freeze.py#L48),
which refuses unless the preregistration is no longer a draft, the development Arm A is
`COMPLETE`, and the run is a dev run. It then records:

| item | what | Phase 3.3's freeze |
|---|---|---|
| `risk_score_formula` | $-M$ of the base model under `rule`; label $M_{\mathrm{instruct}}<0$ | `neg_mseq_base_rule` |
| `calibration` | Platt parameters per development pair, fitted on development rows | 0.5B: $(-0.2984, 0.9014)$; 1.5B: $(-0.2982, 2.1419)$ |
| `decision_threshold` | Youden-optimal per pair | 0.364; 0.352 |
| `prompts` | the hash of every rendered prompt for every registered lexicon, and of `prompts.py` | 45 prompts (9 lexicons × 5 conditions) |
| `exclusions` | the four exclusion rules, verbatim | |
| `analysis_config` | B, α, unit, seeds, the criteria, "never pool families" | |
| `config_hashes` | the development config and the materials (lexicons, templates, terminals, `blk` grammar) | |
| `source_hashes` | every source file whose change could change a number | 44 files |
| `git` | the commit, and whether the tree was clean | `78b2bcd`, not clean |
| `model_pins` | the revision of every model that may be scored | 21 |

[`splits.write_freeze`](../../phase4/code/p4/governance/splits.py#L210) writes it **once**,
atomically, with a `.sha256` sidecar, and makes both read-only. A second freeze is refused.
The git record says the tree was not clean; what protects the analysis is the source hashes, which
every held-out access re-checks (§4.3).

Phase 3.3's freeze was written at **2026-10-08 06:04:47 UTC** (23:04 MST on the 7th) by Sol job
64942745, from the development run `dev-20261006a`.

### 4.2 The unlock

`run.py heldout init --config … --run heldout-… --freeze …/DEV_FREEZE.json` creates the held-out
run. `run.py heldout unlock --run … --confirm "I have finished the development analysis and will
not change it"` calls [`write_unlock`](../../phase4/code/p4/governance/splits.py#L257), which
refuses unless the phrase is exact, the freeze is intact, and **no source file, material or model
pin has drifted** from the freeze ([`frozen_drift`](../../phase4/code/p4/governance/splits.py#L296)).
It writes a read-only `HELDOUT_UNLOCK.json` with the freeze's SHA-256. Phase 3.3's was written at
**06:05:31 UTC**, 44 seconds after the freeze; its provenance note
(`heldout-20261007a/UNLOCK_NOTE.md`) records that the phrase was entered by the AI assistant at the
investigator's explicit direction.

### 4.3 Every held-out access

[`load_unlock`](../../phase4/code/p4/governance/splits.py#L325), reached through `check_access`,
re-verifies the freeze's sidecar, the unlock's freeze hash and, once per process, the drift check
itself. This closes the gap of the first version, which checked the code only when unlocking
(defect P33-015): code edited after the unlock now refuses to score or analyse held-out cells.

**Say it aloud:** "The freeze is a read-only hash of every choice and every file the analysis
depends on; the unlock needs an exact phrase, and every held-out access re-checks that nothing has
moved since."

---

## 5. Models, pins and preflight

### 5.1 The registry

[`registry.py`](../../phase4/code/p4/governance/registry.py) lists every model the programme may
touch, as `ModelSpec`: id, family, size, kind (base or instruct), its **pair**, size tier, whether
it is gated, how many A100-80GB GPUs it needs, and, for served models, the served name and
quantization. A model without a twin (StarCoder2-3B; every served model) can enter Arm A, Arm B
and fertility, but never H4 or H5.

### 5.2 Pins: `run.py prefetch`

[`prefetch.py`](../../phase4/code/p4/runtime/prefetch.py) downloads **without instantiating**
(the old script loaded each model into memory just to download it): `snapshot_download` of an exact
commit, restricted to `allow_patterns` chosen from the repo's file list, then a size check (and,
with `--checksums`, the LFS SHA-256). It writes `model_pins.json`: per model, the revision, the
patterns, the files and the tokenizer fingerprint. An already pinned model keeps its pin unless
`--repin` (defect P33-018: re-running prefetch used to re-pin every updated model, which would have
made every held-out command refuse on drift). A served model's pin is the deployment that answers,
`"<served name>@<system fingerprint>"`. Gated models read `HF_TOKEN` from the environment; the
token is never written.

### 5.3 Preflight

[`preflight.run`](../../phase4/code/p4/runtime/preflight.py) runs before any model is loaded and
fails the job (exit 2) on any `FAIL`:

| check | what |
|---|---|
| scheduler | the job's partition, QOS and account are the configured ones |
| gpu | `nvidia-smi` answers, CUDA is visible, the device is an A100 (waivable, and recorded) |
| precision | bf16 is supported when the run asks for it |
| versions | torch, CUDA, driver and transformers recorded (Sol's environment named *pytorch-gpu-2.3.1* reported torch 2.11.0, so names are never trusted) |
| space | free GPU memory for the task's models, free disk for results and the model cache |
| models | every model resolves **offline** to its pinned revision; served models: the answering deployment equals the pin |
| output | the run folder is writable |
| materials | the materials hashes equal those recorded at run creation |
| split | every cell is allowed for the stage |

---

## 6. Crash-safe storage: shards, markers, merge

### 6.1 Writing a cell

[`ShardStore.write`](../../phase4/code/p4/runtime/shards.py#L132):

1. every row must have a `row_key`;
2. the rows are written as JSON lines to a temporary file made by `mkstemp` **in the target
   folder**, flushed, `fsync`ed and moved into place with `os.replace`, which is atomic: a reader
   sees the old file or the new one, never half of one ([`config.atomic_write_text`](../../phase4/code/p4/runtime/config.py#L198));
3. then the **done-marker** `checkpoints/<exp>/<cell>.done.json`, also atomic: the cell's fields,
   its row count, the shard's SHA-256, the time, the host and the job.

A killed job can therefore lose at most the cell it was writing. Unique temporary names matter on a
cluster: Slurm array tasks start together on different nodes and can share a process id (defect
P33-014).

### 6.2 The four states of a cell

[`ShardStore.status`](../../phase4/code/p4/runtime/shards.py#L98):

| state | when |
|---|---|
| `done` | the marker exists, the shard exists, its SHA-256 and its row count match the marker, and every line parses |
| `corrupt` | a marker without a shard, a hash or count mismatch, or an unreadable file: quarantined on the next run |
| `failed` | a `.failed.json` records the error (OOM, ERROR, INTERRUPTED) and its traceback |
| `missing` | nothing yet |

A resume re-runs everything that is not `done`.

### 6.3 Merging

[`ShardStore.merge(expected_keys)`](../../phase4/code/p4/runtime/shards.py#L196) reads every
expected cell that is `done`, keys rows by `row_key`, drops exact duplicates (and counts them),
**refuses** conflicting duplicates, sorts, and labels the result `COMPLETE`, `PARTIAL` or `EMPTY`.
`write_merged` writes `merged/<exp>.jsonl` and a status file with the hash, byte-for-byte
deterministic. `run.py validate` merges everything and exits 3 unless all four experiments are
`COMPLETE`.

### 6.4 Exit codes

| code | meaning |
|---:|---|
| 0 | complete |
| 1 | an error |
| 2 | a refusal: preflight failed, a split violation, a freeze or unlock refused |
| 3 | partial or incomplete |
| 4 | interrupted: run the same command again to resume |

---

## 7. Provenance: what every job records

[`JobManifest`](../../phase4/code/p4/governance/provenance.py) writes
`manifests/job_<experiment>_<job>_<task>_<pid>.json` at the **start** (status `RUNNING`) and
rewrites it at the end (`COMPLETE`, `PARTIAL`, `FAILED` or `INTERRUPTED`): the command line, the
configuration and its hash, the seeds, the git commit and cleanliness, the Slurm identity (job,
array task, node, partition, QOS, account), package versions, the GPU, the dtype and fp32 flag, the
Hugging Face environment, free disk, every source and materials hash, each model's revision and
tokenizer, and the hash of every prompt used. Every shard marker carries the job identity, so any
row can be traced to the job, node, code and weights that produced it. `job_provenance.csv`
collects them.

---

## 8. Running on Sol

### 8.1 Environment

[`sol/sol.env`](../../phase4/code/sol/sol.env) sets every location and scheduler value from the
environment, with documented defaults and **no username**: the account, `public` partition and QOS,
one A100-80GB (`--gres=gpu:a100:1 --constraint=a100_80`), the code and results roots under
`$HOME`, and the model cache **in scratch** (`$SCRATCH/hf`). It also unsets `P4_FAKE`, so a fake
scorer left over from the tests can never score a real job. Scoring jobs run with
`HF_HUB_OFFLINE=1`: they never touch the network.

### 8.2 `submit.sh`: the only way to submit

[`sol/submit.sh <job> <run_id>`](../../phase4/code/sol/submit.sh) creates the log folder first
(Slurm opens the log files before the job body runs), takes the resources from `sol.env`, and picks
the array indices of the models that need **this** profile's number of GPUs
(`run.py array-indices --gpus N`):

| job | resources | runs |
|---|---|---|
| `cpu_tests` | 4 CPUs, 1 h | the test suite on a CPU node |
| `prefetch` | 4 CPUs, 6 h | `run.py prefetch` |
| `smoke` | 1 GPU, 45 min | one model, one cell, every stage |
| `dev_arm_a`, `dev_primary` | 1 GPU, 4 h / 8 h, array | development Arm A / ladder |
| `dev_analyze`, `dev_freeze` | CPU | merge and export / freeze |
| `heldout_eval` | 1 GPU, 10 h, array | preflight, Arm A, then the ladder, one model per task |
| `arm_b`, `h5` | 1 GPU, 8 h / 6 h, array | Arm B; H5 (merges Arm A first, then `prepare`) |
| `*_2gpu` | 2 GPUs on one node, 24 h | the same, for the 72B pair |
| `*_api` | 2 CPUs, 24 h | the same, for served models |
| `final_export` | CPU | fertility, analyze, validate |

Every scoring job asks Slurm for `SIGUSR1` five minutes before its time limit
(`#SBATCH --signal=USR1@300`), so the runner stops cleanly between sites and the next submission
resumes.

### 8.3 The held-out chain: `submit_chain.sh`

[`sol/submit_chain.sh <run_id>`](../../phase4/code/sol/submit_chain.sh) submitted Phase 3.3's whole
held-out stage at once (2026-10-07, 23:07 MST), **one task at a time** (`%1`):

```text
heldout_eval      models 0–18        %1
  → heldout_eval_2gpu   19, 20 (72B)  %1     afterany
  → arm_b               the 9 one-GPU instruct models   (12 h limit)
  → arm_b_2gpu          20
  → h5                  the 9 one-GPU instruct models   afterany + afterok on BOTH evaluation jobs
  → h5_2gpu             20                               afterok on both
  → final_export
```

`afterany` lets one failed task leave the rest running (it can be resubmitted with `P4_ARRAY`);
H5 uses `afterok`, because it derives its arms from the merged held-out Arm A and stores them for
good. The job ids are kept in `logs/submission_chain.env`.

### 8.4 Working with Sol from this laptop

Sol's SSH login needs Duo approval, and an automated session should not trigger Duo pushes on its
own. The practice in this project: the investigator runs the Sol commands (or opens one multiplexed
connection that later commands reuse), and results are copied back to `phase3_3/sol_results/`.
Pollers stop instead of reconnecting when a connection drops.

---

## 9. Running served models: the API path

Served models (Phase 4) need the network, not a GPU, so they can run from a laptop or a CPU node.

- [`tools/run_api_local.sh <run_id>`](../../phase4/code/tools/run_api_local.sh) runs preflight, then
  one process per served model, each running Arm A, the ladder and Arm B in order, plus fertility,
  each with its own log. Resuming is the same command.
- On Sol, the `*_api` profiles of `submit.sh` do the same on CPU nodes.
- [`runtime/asu_api.py`](../../phase4/code/p4/runtime/asu_api.py) is the one place that knows the
  address and the key. The key is read from `ASU_RC_API_KEY` or from a file readable by its owner
  only (`~/.config/asu-rc/llm_api_key`, mode 600), goes only into the `Authorization` header, and
  is never printed, logged or written to a result. Each thread keeps one connection; a request that
  hangs is retried on a fresh connection, as are 500 and 502–504 answers and dropped connections,
  with backoff.
- The scorer checks every answer against the pinned deployment and stops a cell that gets another
  one ([`api.py`](../../phase4/code/p4/scoring/api.py)).

Phase 4's run `dev-20261023a` scored its nine served models this way, from the laptop, in 5 h 56
min (details: [`phase4/api_models_results_explained/03`](../phase4/api_models_results_explained/03_code_and_pipeline.md)).

---

## 10. The export: 19 CSVs, 12 plots, 10 reports

`run.py export --run …` (or `<stage> analyze`, which merges first) builds everything from the merged
rows and manifests only; no model is touched. The registry of outputs is
[`reporting/artifacts.py`](../../phase4/code/p4/reporting/artifacts.py), so a summary can neither
miss a file nor count a stale one.

### 10.1 The 19 CSVs ([`export.py`](../../phase4/code/p4/reporting/export.py))

| CSV | one row per | holds |
|---|---|---|
| `site_inventory` | planned site | family, lexicon, template, terminal, stratum, prefix length |
| `split_exclusion_audit` | cell class, dropped site, empty grid cell, excluded row | why anything is missing |
| `run_completeness` | experiment | expected, done, missing, failed, corrupt cells; merged hash |
| `failed_cells` | failed cell | the error and where |
| `job_provenance` | job | git, config hash, node, versions, GPU, dtype, revisions |
| `fertility` | tokenizer × family × lexicon | tokens per character and relative to 3DOM |
| `arm_a_long` | Arm A row | every scored margin with all its fields |
| `rule_effect` | model × family × lexicon × stratum | reversion with its interval; rule effect against each control with its interval |
| `paraphrase` | model × family × prompt variant | reversion and mean margin per framing, and their range |
| `extinction_rung_long` | ladder row | every rung's margin with its demonstration ids |
| `kstar_survival` | site curve, and model × family | `k*` and diagnostics; Kaplan–Meier for both populations; curve shapes |
| `h4_predictions` | pair × site | risk, label, baselines, calibrated probability and its source |
| `h4_metrics_baselines_calibration` | pair × family | AUROC, AP, P@k, Brier, ECE, calibration, differences with intervals, C1–C3 |
| `arm_b_generations` | generation | prompt hash, raw output, extracted program, bucket, site observations |
| `arm_b_hurdle` | model × family × lexicon × stratum | buckets, reach, reversion given reach, product |
| `h5_budget_outcomes` | model × family × lexicon × arm × seed | repaired and control counts, silent errors, the per-symbol metric, control degradation |
| `h5_ir_proof` | repair | checks and mismatches |
| `h2_did` | — | `NOT TESTABLE` and why |
| `power` | scenario | development stage only; `NOT RUN` in a held-out export |

A CSV with no data still exists, with one row saying `NOT RUN` or `NOT TESTABLE` and why: never a
placeholder number.

### 10.2 Plots and reports

[`plots.py`](../../phase4/code/p4/reporting/plots.py) draws 12 diagnostic figures, each as PNG and
SVG (margins and reversion, the rule-effect forest, family × mapping × model × stratum, fertility,
extinction trajectories with Kaplan–Meier, paraphrase sensitivity, size and tokenizer, H2, H4 ROC
and PR and calibration, H5 benefit, Arm B hurdle, power). They are registered outputs of the frozen
code: dense, stamped, and not for a paper; the paper figures come from the scripts of §11.
[`reports.py`](../../phase4/code/p4/reporting/reports.py) writes 10 Markdown reports:
`RUN_SUMMARY`, `METHODS_AND_PROVENANCE`, `QUALITY_CONTROL`, `DEVELOPMENT_RESULTS`,
`HELDOUT_RESULTS`, `HYPOTHESIS_RESULTS`, `PLAIN_LANGUAGE_RESULTS`, `POWER_ANALYSIS`, `DEVIATIONS`
and `REPRODUCTION`.

---

## 11. After the run: the scripts outside the frozen code

Analyses decided after the freeze run **outside** the frozen code, from the exported files, write
only to `analysis_addenda/`, and refuse if they cannot first reproduce the frozen numbers they
build on.

| script | when | what |
|---|---|---|
| [`scale_analysis.py`](../../phase3_2/sol/scripts/scale_analysis.py) | specified by D11 before any held-out outcome | the six size slopes with template intervals and Holm (`analysis_addenda/d11_scale/`) |
| [`paper_figures.py`](../../phase3_2/sol/scripts/paper_figures.py) | 2026-10-09 | 10 figures and 16 tables for the paper; checks every number against the export first |
| [`exploratory_checks.py`](../../phase3_2/sol/scripts/exploratory_checks.py) | 2026-10-09, post hoc | own-base against other-lineage H4; roles by rung; adaptation by density, role and model kind |
| [`analysis_revision.py`](../../phase4/code/tools/analysis_revision.py) | D9, 2026-10-07 | re-derives a run's tables from its saved measurements and proves the measurements unchanged (652 inputs byte-identical) |
| [`fix_heldout_problems.py`](../../phase4/scripts/fix_heldout_problems.py) | D13, 2026-10-21, post hoc | F1 cross-fitted calibration, F2 H5's registered test, F4 its split, F5 Arm B extraction, F6 H4 per role (`analysis_addenda/phase4_fixes/`) |
| [`retest_api.py`](../../phase4/code/tools/retest_api.py) | Phase 4 | re-scores 300 sampled margins per served model, to measure batching noise |
| [`paper_figures_api.py`](../../phase4/code/tools/paper_figures_api.py) | Phase 4 | the served models beside Phase 3.3's instruct models |
| [`compare_with_phase3_3.py`](../../phase4/code/tools/compare_with_phase3_3.py) | Phase 4 | runs the frozen pipeline and the copy side by side and compares every CSV byte for byte |
| [`verify_copy.py`](../../phase4/code/tools/verify_copy.py) | Phase 4 | checks every copied file against its origin and the manifest |

Four result files are larger than GitHub's 100 MB limit (`merged/arm_a.jsonl`,
`merged/primary.jsonl`, `merged/h5.jsonl`, `csv/arm_a_long.csv`); they are stored gzipped, with
their SHA-256 in `LARGE_FILES.sha256`, and `phase3_3/sol_results/restore_large_files.sh` restores
and verifies them after a fresh clone.

---

## 12. The tests

`phase4/code/tests/` holds **240 tests in 15 files**, run by a dependency-free runner
(`python3 tests/run_tests.py [pattern] [-v]`; no pytest in this repository). A test that needs a
missing optional dependency is reported **BLOCKED**, never passed; the exit code is 1 on any
failure, 5 if anything is blocked, 0 only when everything passed. The runner always uses a fresh
temporary results root, so a test can never touch real data (on Sol it once did, defect R8).

| file | tests | what it guards |
|---|---:|---|
| `test_stop_ship.py` | 31 | each stop-ship defect, showing the old behaviour failing where possible |
| `test_phase3_2.py` | 36 | the families, templates, lexicon family and margins, on `lark` alone |
| `test_metric_and_report_corrections.py` | 20 | D9: tie-safe AP and P@k, power scenarios, report counts, figure footers |
| `test_splits_freeze.py` | 20 | split locks, the immutable freeze, the unlock |
| `test_analysis.py` | 19 | H4 metrics and criteria, Arm B, the H5 proof, H2, power |
| `test_shards_resume.py` | 19 | atomic shards, resume, duplicates, corruption, deterministic merge, incompatible configs |
| `test_prereg_env.py` | 16 | the frozen preregistration (its SHA-256), configs, dependency preflight |
| `test_scorer_repair.py` | 14 | the semantic scorer against extra, missing, duplicated and reordered operations |
| `test_sites.py` | 12 | site enumeration and classification (the colour-literal hazard; the token-type map) |
| `test_phase4_design.py` | 12 | Phase 4's own folders, split, labels and preregistration |
| `test_api_scorer.py` | 11 | the API scorer against a stand-in server; the key never reaching an output |
| `test_phase3_scoring.py` | 11 | the scoring module; the fake model's planted bias is recovered |
| `test_e2e.py` | 8 | a fake-model run end to end: dev → analysis → freeze → unlock → held-out |
| `test_model_scale.py` | 6 | D10: models above 3B, the 2-GPU profile, `submit.sh` against a stand-in `sbatch` |
| `test_voyager_models.py` | 5 | the model list and probe tool against a stand-in API |

`phase4/tests/test_fix_heldout_problems.py` adds 6 tests for the D13 script. Neither defect of
2026-10-23 and 2026-10-28 (the Kaplan–Meier boundary and the shared H5 repair name) is covered by a
test yet; [`experiment_code.md` §11.6](experiment_code.md#116-a-defect-found-on-2026-10-28-the-targeted-arm-scored-the-wrong-lexicon)
sketches the missing one.

---

## 13. The real runs, in numbers

| run | what | cells | rows | compute |
|---|---|---|---|---|
| `dev-20261006a` | development: 4 Qwen2.5-Coder checkpoints (0.5B, 1.5B, base and instruct), `dom` × 4 development lexicons, 852 sites | Arm A 192, ladder 112 | Arm A 10,224; ladder 16,000 | Sol A100 |
| `heldout-20261007a` | confirmatory: 21 checkpoints, both families × 5 held-out lexicons, 3,030 sites | Arm A 3,402; ladder 840; Arm B 200; H5 3,780 | Arm A 190,890; ladder 84,000; Arm B 7,800 generations; H5 212,100 | 40.8 A100 GPU-hours |
| `dev-20261023a` | Phase 4, exploratory: 9 served models, the same 3,030 sites | Arm A 1,458; ladder 360; Arm B 180 | Arm A 81,810; ladder 36,000; Arm B 7,020 generations | no GPU of ours; 5 h 56 min |

The held-out GPU-hours split as: evaluation 7.47 + 2 × 3.60, Arm B 8.37 + 2 × 3.46, H5 5.71 + 2 ×
2.55 (the 2 × for the 72B pair on two GPUs). Small models are slower in Arm B than their size
suggests: they ramble to the 192-token cap, while large models stop after the program. A re-score
of H5's 100 targeted cells (§11.6 of the code guide) is one of its seven arms: about 1.5 A100
GPU-hours.

---

## 14. Reproducing a result

From the repository root, with the project's virtual environment:

```bash
# restore the large files after a fresh clone
bash phase3_3/sol_results/restore_large_files.sh heldout-20261007a

# rebuild a run's 19 CSVs, plots and reports from its saved measurements (no model needed)
P4_RESULTS_ROOT=<a copy of phase3_3/sol_results> python3 phase4/code/run.py export --run heldout-20261007a

# the after-run analyses
python3 phase3_2/sol/scripts/scale_analysis.py --run heldout-20261007a
python3 phase3_2/sol/scripts/paper_figures.py  --run heldout-20261007a
python3 phase4/scripts/fix_heldout_problems.py          # refuses on any mismatch with the frozen numbers

# the two pipelines side by side, and the test suites
python3 phase4/code/tools/compare_with_phase3_3.py --real-dev
python3 phase4/code/tests/run_tests.py
python3 phase3_2/sol/tests/run_tests.py
```

Work on a copy of a results folder when re-exporting: an export rewrites `csv/`, `plots/` and
`reports/` in place (`analysis_revision.py` exists to do this with a recorded before and after).

---

## 15. Practice

**Question 1.** A job is killed while writing a cell. What is lost, and what does the next run do?

**Answer:** Only that cell: its temporary file never became a shard, and it has no done-marker. The
next run sees it as `missing` and scores it again; the abandoned temporary file is cleaned after 15
minutes.

**Question 2.** Why must a run id start with its stage?

**Answer:** So that development and held-out outputs can never share a folder:
`RunConfig.validate` refuses an id without its stage's prefix, and each command group (`dev …`,
`heldout …`) refuses a run of another stage with exit code 2.

**Question 3.** Someone edits `p4/analysis/h4.py` after the unlock and runs `heldout analyze`. What
happens?

**Answer:** `load_unlock` finds a source hash that differs from the freeze and raises
`SplitViolation`: held-out scoring and analysis must run the frozen code.

**Question 4.** Why does H5 wait with `afterok` on both evaluation jobs, when Arm B only waits with
`afterany`?

**Answer:** H5 chooses its arms from the merged held-out Arm A and stores them for good; starting on
an incomplete Arm A would freeze arms derived from partial data.

**Question 5.** Where is the API key, and how could it leak into the public repository?

**Answer:** In `~/.config/asu-rc/llm_api_key` (mode 600) or the environment; only `asu_api.py`
reads it, and only into a request header. It could leak only through a message or log line that
quotes a request, so none does: retries are logged without it, the probe tool cuts gateway error
texts to their first sentence, and a test checks that no output of a scored run contains the key.

**Question 6.** What does `PARTIAL` in `run_completeness.csv` tell you, and what must a report do
with it?

**Answer:** Some expected cells are missing, failed or corrupt; the merged rows are real but
incomplete, and every report built from them is labelled PARTIAL.

**Question 7.** Why are the paper figures not the plots in `plots/`?

**Answer:** The plots are registered outputs of the frozen code, kept as they are; the paper's
figures were decided after the results, so they come from a separate script that first reproduces
the frozen numbers and writes only to `analysis_addenda/`.
