# 03 — Code and pipeline (the Sol pipeline)

**Where the numbers come from:**

- every dump is real, from the development smoke `local_smoke/smoke-local-20261005` (Qwen2.5-Coder-0.5B, `dom × d50s1`, 12 sites);
- or from the fake-scorer CLI rehearsal (`AUDIT.md` §6);
- or from the planner run on the real development configuration.

The commands are in [`../README.md`](../README.md); the maths is in [`02`](02_mathematics_and_statistics.md).

---

## 1. Map of the code

```
phase3_2/sol/
├── src/p33/            the pipeline (25 modules, 5,530 lines)
├── scripts/p33.py      the ONE command-line entry point (stage groups: dev / heldout / smoke)
├── scripts/analysis_revision.py  records a re-derivation from saved measurements (no model)
├── jobs/*.slurm        11 Slurm jobs, each a thin wrapper around scripts/p33.py
├── submit.sh           the only way to submit (log dir first; account/partition/QOS from sol.env;
│                       array indices per GPU class)
├── sol.env             defaults, all overridable; never a username
├── env/                make_env.sh, activate.sh (safe under set -u), requirements.in, lock
├── configs/            smoke.json, local_smoke.json, dev.json, heldout.json
├── tests/              8 test modules + a dependency-free runner (139 tests)
├── local_smoke/        the one real-model development smoke
└── legacy_superseded/  the Phase 3.3 scripts that would not have run, kept with WHY_SUPERSEDED.md
```

| Module | Lines | Role | Kind |
|---|---:|---|---|
| `splits.py` | 338 | registered split, size ceiling (72B, D10), freeze, unlock, drift check | **load-bearing** |
| `pipeline.py` | 448 | plan → cells → score → shards; signals | **load-bearing** |
| `shards.py` | 262 | atomic shards, status, quarantine, deterministic merge | **load-bearing** |
| `kstar.py` | 166 | `k*`, censoring, Kaplan–Meier | **load-bearing** |
| `demos.py` | 111 | leakage-free nested demonstrations | **load-bearing** |
| `h4.py` | 468 | H4 table, tie-grouped metrics and curves (D9), baselines, criteria | **load-bearing** |
| `h5.py` | 249 | repair arms, IR proof | **load-bearing** |
| `armb.py` | 289 | NL requests, generation, five buckets, hurdle | **load-bearing** |
| `power.py` | 342 | clustered power from development data, one row per (T, ICC) scenario (D9) | load-bearing (for sizing) |
| `freeze.py` | 109 | builds `DEV_FREEZE.json` | load-bearing |
| `config.py` | 274 | paths, Sol defaults, `RunConfig`, hashing, `atomic_write_text` | plumbing (with teeth) |
| `provenance.py` | 154 | `JobManifest`, git/Slurm/GPU/package identity | plumbing |
| `preflight.py` | 188 | refuse a job that would waste an allocation; checks only its own task's models, GPU count and memory (D10) | plumbing |
| `prefetch.py` | 184 | download-only, pinned revisions; keeps existing pins | plumbing |
| `scorers.py` | 68 | load one model from its pinned snapshot, offline, on its GPU class (D10) | plumbing |
| `fertility.py` | 80 | tokens/char per distinct tokenizer | plumbing |
| `export.py` | 411 | the 19 CSVs, from merged shards only | reporting |
| `plots.py` | 507 | the 12 figures, from CSVs only; footers pair each model with its revision | reporting |
| `reports.py` | 460 | the 10 reports, from CSVs and manifests only | reporting |
| `artifacts.py` | 50 | the registry of files an export must produce; `RUN_SUMMARY` counts against it (D9) | reporting |
| `registry.py` | 100 | every model the programme may touch, with its GPU class (D10) | data |
| `fakes.py` | 194 | deterministic GPU-free scorer for tests | test support |
| `h2.py` | 43 | NOT TESTABLE, with the machinery ready | — |
| `_paths.py`, `__init__.py` | 35 | locating `phase3_2` and `phase3` | — |

The shared scientific code lives outside `p33`, in `phase3_2/src/phase3_2/`
(rewritten or extended here):

| File | Lines | What it holds |
|---|---:|---|
| `margins.py` | 358 | canonical scorer, refusals, fp32 head; two-GPU sharded load (D10) |
| `sampling.py` | 189 | within-cell de-duplication, balanced selection, expected cells |
| `analysis.py` | 263 | cluster bootstrap with multiplicity, Holm |
| `prompts.py` | 291 | prompt bundles, length-matched control, per-site check |
| `deltafam.py` | 223 | idempotent writer, P33-011 |

`phase3/src/phase3/models.py` (229 lines) now raises instead of returning 0.0.

---

## 2. Data structures to hold in your head

| Object | Module | What it is | Field that matters most |
|---|---|---|---|
| `RunConfig` | config | everything a run depends on | `config_hash()`: excludes `run_id` and `note`, so renaming a run never invalidates it |
| `CellClass` | splits | (kind, label, reason) for a family/lexicon/model | `label`, copied onto every row and aggregate |
| `Plan` | pipeline | sites by (family, lexicon), expected cells, drops, grid, classes, rendered pool | `expected`, the cells the materials offer |
| `Cell` | pipeline | one unit of work: model × family × lexicon × condition × chunk | `key`, a readable prefix plus a hash of its fields |
| shard + marker | shards | `raw/shards/<exp>/<key>.jsonl` + `checkpoints/<exp>/<key>.done.json` | `sha256` of the shard, inside the marker |
| `CellStatus` | shards | done / failed / corrupt / missing | `state` |
| `MergeResult` | shards | merged rows + COMPLETE / PARTIAL / EMPTY | `status` |
| `PairScore` | margins | the scorer's output for one site | `k_common`, `merged`, `m_seq` |
| `DemoSet` | demos | demonstration ids and texts, in order | `sha` |
| `KStar` / `KMSummary` | kstar | one curve's threshold / one population's survival | `censored`, `km_median` |
| `JobManifest` | provenance | one job's identity and lifecycle | `status`: RUNNING → COMPLETE / PARTIAL / FAILED / INTERRUPTED |

A real done-marker, the thing that makes a cell "done":

```json
{ "cell_key": "arm_a_dom_d50s1_norule_0__7781962813a5e94d",
  "fields": { "experiment": "arm_a", "family": "dom", "lexicon": "d50s1",
              "condition": "norule", "chunk": 0,
              "model": "Qwen/Qwen2.5-Coder-0.5B",
              "revision": "8123ea2e9354afb7ffcc6c8641d1b2f5ecf18301",
              "config_hash": "190fbc72fc74…", "site_ids_sha": "74c03986…" },
  "n_rows": 4, "sha256": "230d1726…", "host": "mesquite-Alienware-m15-R7",
  "written_utc": "2026-10-06T00:17:40+00:00" }
```

The key already encodes the configuration, the revision and the exact sites.
A resumed run with a different configuration computes different keys, and
`shards.assert_compatible` refuses it before any work starts.

---

## 3. The pipeline, end to end

```
 sol.env + env/activate.sh ──► prefetch ──► results/model_pins.json (revision, allow_patterns, hashes)
                                   │
 configs/<stage>.json ──► <stage> init ──► manifests/run_config.json (config_hash)
                                   │
                         preflight (GPU jobs) ──► manifests/preflight_*.json   any FAIL → exit 2
                                   │
                ┌──────────── build_plan ────────────┐
                │ 1 splits.enforce_config  (REFUSE FIRST: nothing enumerated yet)
                │ 2 render 80 templates × family × lexicon, classify sites (SEMANTIC only)
                │ 3 dedupe WITHIN (family, lexicon) cells, canonical tie-break, log every drop
                │ 4 balanced selection; assert every materially available cell is present
                │ 5 structural grid (e.g. dom/d25s2/sigil = STRUCTURALLY_EMPTY)
                └──────────────────┬─────────────────┘
                                   ▼  manifests/plan_<exp>.json (idempotent, verified on resume)
             cells = model × family × lexicon × condition × chunk(chunk_size)
                                   │   array task i → model i of run_config.json
                                   ▼
   for each cell not yet done:  score ──► rows ──► atomic shard + marker
        (check_stop between sites; failure → <key>.failed.json with kind; job continues)
                                   │
                                 merge ──► merged/<exp>.jsonl + .status.json (COMPLETE/PARTIAL/EMPTY)
                                   │
         fertility ──► export: 19 CSVs ──► plots: 12 (PNG+SVG) ──► reports: 10
                                   │
       dev only:  freeze ──► DEV_FREEZE.json (444, .sha256)
       held-out:  init --freeze ──► unlock --confirm "<phrase>" ──► the same pipeline, re-verified
```

### The Slurm job graph

| # | Job | Resources (`submit.sh`) | Runs | Needs |
|---:|---|---|---|---|
| 1 | `cpu_tests` | 4 CPU, 16G, 1h | Sol / Phase 3.2 / Phase 3 suites (fake scorer, `--cpu-node`) | env |
| 2 | `prefetch` | 4 CPU, 16G, 6h | `prefetch --config smoke dev heldout` (dry run, then download) | network |
| 3 | `smoke` | A100, 64G, 45m | `env-check` + `smoke` (init, preflight, Arm A, primary, fertility, export) | 2 |
| 4 | `dev_arm_a` | A100, 64G, 4h, array | `dev preflight` + `dev run --experiment arm_a` | `dev init` |
| 5 | `dev_primary` | A100, 80G, 8h, array | `dev preflight` + `dev run --experiment primary` | `dev init` |
| 6 | `dev_analyze` | 8 CPU, 32G, 2h | `dev fertility`, `dev analyze`, `validate` | 4, 5 |
| 7 | `dev_freeze` | 2 CPU, 8G, 30m | `validate` (fatal), then `dev freeze` | 6, a git commit |
| 8 | `heldout_eval` | A100, 80G, 10h, array | `heldout preflight` + held-out Arm A + primary | `heldout init`, `unlock` |
| 8b | `heldout_eval_2gpu` | 2 × A100, 160G, 24h, array | the same job file, for the models with `gpus = 2` (the Qwen2.5-72B pair) | as 8 |
| 9 | `arm_b` | A100, 64G, 8h, array | `<stage> preflight` + `run --experiment armb` | a run |
| 10 | `h5` | A100, 64G, 6h, array | `<stage> preflight` + `merge arm_a` + `run --experiment h5` | Arm A of the same run |
| 11 | `final_export` | 8 CPU, 32G, 2h | fertility, analyze, validate | everything |

`arm_b_2gpu` and `h5_2gpu` mirror 9 and 10 on two GPUs. `submit.sh` asks
`p33.py array-indices --run <RUN> --gpus N` which array indices belong to each GPU
class. A one-GPU profile never submits the 72B pair, and a `*_2gpu` profile submits
nothing else. An empty class is refused (exit 2).

**Every job does the same things:**

- sources `sol.env`, which **unsets `P33_FAKE`**; only job 1 sets it, afterwards;
- sources `env/activate.sh`;
- runs `srun "$P33_PY" scripts/p33.py …`.

**Scoring jobs** also set `HF_HUB_OFFLINE=1` and receive `--signal=USR1@300` (smoke: `@120`).

---

## 4. Stage detail: INPUT → TRANSFORMATION → OUTPUT → VALIDATION

### 4.1 Environment (`env/make_env.sh`, `env/activate.sh`)

| | |
|---|---|
| **Input** | Sol's shared PyTorch env (overlay) or the PyTorch wheel index (standalone); `env/requirements.in` |
| **Transformation** | build a venv; overlay mode adds the shared env's `lib/` to `LD_LIBRARY_PATH`; `nounset` disabled **only** around activation (Sol's MKL activation script reads an unset variable) |
| **Output** | `$P33_ENV_DIR`, `$P33_PY`, `requirements.lock.sol.txt` |
| **Validation** | `p33.py env-check` exits 2 if lark, numpy, matplotlib, transformers or huggingface_hub is missing; versions are re-measured, never read from the env's name |

### 4.2 Prefetch (`p33/prefetch.py`)

| | |
|---|---|
| **Input** | model ids (default: every model of the shipped configs: 21 since D10, about 0.7 TB in all, nearly all of it the 10 large checkpoints) |
| **Transformation** | `HfApi.model_info` with file metadata → choose patterns (`*.safetensors`, else `*.bin`, plus tokenizer and config files) → `snapshot_download` at the exact revision, 3 retries → size and optional sha256 checks. **Never instantiates a model.** |
| **Output** | `results/model_pins.json`: revision, `allow_patterns`, snapshot path, tokenizer fingerprint, failures, pairing problems |
| **Validation** | `--verify-only` re-resolves offline with the **same** `allow_patterns` (huggingface_hub 1.x calls a transformers-populated cache "incomplete" without them). The smoke config pinned `8123ea2e…` and tokenizer `cc349caf…`. Pairing problems for the default set: `[]`. An already-pinned model keeps its revision on a re-run (`kept_existing_pins`); only `--repin` moves it |

### 4.3 Init (`scripts/p33.py <stage> init`)

| | |
|---|---|
| **Input** | a config JSON, a run id, and for held-out the freeze path |
| **Transformation** | set the stage from the command group; `validate()` (the run id must start with its stage; a smoke is one model × one lexicon × one family); `enforce_config`, where held-out may still be locked |
| **Output** | `results/<run>/manifests/run_config.json`, the run directory layout |
| **Validation** | `assert_compatible` refuses a different `config_hash` under an existing run id |

### 4.4 Preflight (`p33/preflight.py`)

| | |
|---|---|
| **Input** | the run config, model pins, the run directory |
| **Transformation** | the checks: scheduler (partition, QOS, account vs `sol.env`) · `nvidia-smi` · torch CUDA · **A100** (waivable only by `allow_non_a100`, which is recorded) · bf16 · free GPU memory · **GPU count and memory for each of the task's models** (D10: `size × 2 × 1.03 + 4` GiB) · disk space for results and the HF cache · every model **of this array task** resolves offline to its pin · output writable · materials unchanged since the run's first job · split permission |
| **Output** | `manifests/preflight_<utc>.json`; one `[PASS|WARN|FAIL]` line per check |
| **Validation** | any FAIL → exit 2 before a model is loaded. WARN is informational (not in Slurm; first job of a run) |

Real (laptop smoke; 9 of the 12 checks shown, the three space/writability
checks omitted. Recorded before WARN was split out of PASS, so the first and
second-to-last lines read PASS where today's code prints WARN):

```
[PASS] scheduler        not inside Slurm (local run)
[PASS] nvidia_smi       NVIDIA GeForce RTX 3080 Ti Laptop GPU, 595.91.07, 16384 MiB, 14927 MiB
[PASS] torch_cuda       torch 2.14.0+cu130, CUDA runtime 13.0
[PASS] a100             NVIDIA GeForce RTX 3080 Ti Laptop GPU (waived: allow_non_a100)
[PASS] bf16             bfloat16 support
[PASS] gpu_memory       free 14.4 GiB of 15.6 GiB
[PASS] model:Qwen/Qwen2.5-Coder-0.5B  local 8123ea2e9354 pinned 8123ea2e9354
[PASS] materials        first job in this run; hashes recorded now
[PASS] split_permission 1 cells allowed for stage smoke: ['DEVELOPMENT']
```

### 4.5 Plan (`pipeline.build_plan`)

| | |
|---|---|
| **Input** | the config; the frozen terminal table; 80 templates; the lexicons |
| **Transformation** | **split check first** (a spy test asserts the classifier is called 0 times before a refusal) → render and classify → keep SEMANTIC sites → dedupe within (family, lexicon) with a canonical tie-break → balanced selection → `assert_balanced(expected=…)` → structural grid |
| **Output** | `Plan`; `manifests/plan_<exp>.json` |
| **Validation** | the plan file is written once and **re-derived and compared** on every resume. A change raises `materials changed under an existing run` |

Real, development configuration (4 lexicons, `dom`):

| Lexicon | Sites kept | Primary subset |
|---|---:|---:|
| `d25s1` | 220 | 95 |
| `d25s2` | 88 | 62 |
| `d50s1` | 272 | 123 |
| `d50s2` | 272 | 120 |
| **total** | **852** | **400** |

- **Strata:** 11 non-empty cells; 1 STRUCTURALLY_EMPTY cell (`dom/d25s2/sigil`).
- **Duplicates:** 443 within-cell duplicates dropped, each logged with the site it duplicates.
- **Smoke:** `dom/d50s1` offers keyword 65, sigil 151, verb 56 (= 272). 144
  duplicates were dropped. The balanced 12 are 4 + 4 + 4.

### 4.6 Scoring a cell (`pipeline.score_arm_a_cell`, `score_primary_cell`, `_score_into`)

| | |
|---|---|
| **Input** | a `Cell` (≤ `chunk_size` sites), a scorer for one model, the plan |
| **Transformation** | per site: build the `PromptBundle` for **the site's own lexicon** (`assert_prompt_matches`) → for primary rungs, `demos.for_site(…, 32)` then `.first(k)`, `demos.audit` must be empty → `margins` scores the pair (refusals become `status` + `exclusion_reason`, never 0.0) → attach split label, revision, tokenizer id, prompt sha, demonstration ids and hashes |
| **Output** | rows (Arm A: one per site × condition; primary: one per site × rung, plus paraphrases) |
| **Validation** | `check_stop()` between sites (signals); a leak or a prompt/lexicon mismatch **raises** |

**A real Arm A row (abridged), with every field present in `arm_a_long.csv`:**

```
site_id dom:d50s1:t000:T_CLASS_SIGIL:0   stratum sigil   char_offset 17
condition norule  prompt_tokens 237  prompt_chars 1014  prompt_sha ac47da8d…
correct "#"  competitor "."  first_div "('#" vs "('."  merged true
k_common 241  n_prefix_tokens 242  n_tok 1/1  fp32_head true  tie false
logp_correct −5.6932  logp_competitor −6.3846  m_seq +0.6913
program_nll 81.74 (20 tokens)  split DEVELOPMENT  model_revision 8123ea2e…  tokenizer_id cc349caf…
```

**A real primary row (rung 4, same site):**

```
kind ladder  rung 4  demo_ids [t001, t035, t017, t010]  demo_seed 20261005
demo_set_sha a93eca94…  demo_order_sha ac3a3278…  prompt_sha 9668e9c3… (= the rule prompt)
k_common 392  logp_correct −1.0771  logp_competitor −1.5873  m_seq +0.5102
```

None of the four demonstrations is t000. Each is a different template from
the site's own lexicon and family.

### 4.7 Shards, failures, signals (`p33/shards.py`, `pipeline.run`)

| | |
|---|---|
| **Input** | the rows of one cell |
| **Transformation** | `atomic_write_text`: a unique `mkstemp` temp file → fsync → `os.replace`. Then the marker, with sha256 and row count. On an exception: `record_failure` with kind OOM / INTERRUPTED / ERROR, and the job moves on. On SIGTERM, SIGUSR1 or SIGINT: a stop flag, checked between sites. The unfinished cell's rows are discarded, never written, so the cell is redone on resume. The manifest is set to INTERRUPTED and the job exits 4 |
| **Output** | `raw/shards/<exp>/<key>.jsonl`, `checkpoints/<exp>/<key>.done.json` (or `.failed.json`) |
| **Validation** | `status()` recomputes the shard's sha against the marker. A mismatch or a marker without a shard is **corrupt**: quarantined and redone. Temp files are never read as shards, and only those older than 15 min are cleaned (another array task may be writing) |

### 4.8 Merge, validate (`ShardStore.merge`, `p33.py validate`)

| | |
|---|---|
| **Input** | every expected cell key for the experiment |
| **Transformation** | verify each shard; identical duplicate rows are dropped and conflicting ones refused; deterministic sort by `row_key` |
| **Output** | `merged/<exp>.jsonl` + `.status.json` |
| **Validation** | `validate` exits 0 only if every *started* experiment (one whose shard directory exists) is COMPLETE. `status` is read-only: it never creates that directory (P33-017) |

Real smoke status files:

- Arm A: `COMPLETE`, 36 rows, 9/9 cells, sha `8b23811c…`.
- primary: `COMPLETE`, 48 rows, 8/8 cells, sha `87cbc6e2…`.

### 4.9 Fertility (`p33/fertility.py`)

| | |
|---|---|
| **Input** | every distinct tokenizer among the run's models (fingerprinted); 80 templates |
| **Transformation** | tokens, chars, tokens/char, fertility relative to identity, relative token count, fragmentation — per tokenizer × family × lexicon |
| **Output** | `manifests/fertility.json` → `fertility.csv` |
| **Validation** | models sharing a tokenizer share one measurement. The smoke reproduces Phase 3.2's identity value (0.3669) exactly |

### 4.10 Export, plots, reports (`export.py`, `plots.py`, `reports.py`)

| | |
|---|---|
| **Input** | merged rows and manifests only, never a model |
| **Transformation** | build the tables; every figure from the CSVs; every report from the CSVs and manifests |
| **Output** | 19 CSVs, 12 figures × (PNG + SVG), 10 reports, all listed in `p33/artifacts.py`. `RUN_SUMMARY.md` is written **last** and reports "present of registered" per directory |
| **Validation** | each table, figure and report carries its stage, split, revision, tokenizer, prompt hashes, cluster counts and bootstrap settings. Missing data is written as `NOT RUN` / `NOT TESTABLE` rows, never as placeholder numbers. Each report starts with a stage banner; a development report cannot call itself confirmatory |

- **CSVs:** `site_inventory · split_exclusion_audit · run_completeness ·
  failed_cells · job_provenance · fertility · arm_a_long · rule_effect ·
  paraphrase · extinction_rung_long · kstar_survival · h4_predictions ·
  h4_metrics_baselines_calibration · arm_b_generations · arm_b_hurdle ·
  h5_budget_outcomes · h5_ir_proof · h2_did · power`.
- **Figures:** `margin_reversion_distributions · rule_effect_forest ·
  family_mapping_model_stratum · fertility_tokenization ·
  extinction_trajectories_km · paraphrase_sensitivity · model_size_tokenizer ·
  h2_three_scale · h4_roc_pr_calibration · h5_benefit_per_symbol ·
  armb_hurdle_outcomes · power_curves`.
- **Reports:** `RUN_SUMMARY · METHODS_AND_PROVENANCE · QUALITY_CONTROL ·
  DEVELOPMENT_RESULTS · HELDOUT_RESULTS · HYPOTHESIS_RESULTS ·
  PLAIN_LANGUAGE_RESULTS · POWER_ANALYSIS · DEVIATIONS · REPRODUCTION`.

**Since 2026-10-07 (D9):**

- AP, precision@k and the PR/ROC curves treat tied scores as one threshold.
- `power.csv` has one row per (template count, ICC) scenario, each computed with its own ICC.
- `POWER_ANALYSIS.md` shows every scenario, with the pilot flagged.

An export can be repeated on saved measurements at any time; it never loads a model. When
the outputs of a real run are regenerated, `scripts/analysis_revision.py` keeps the
evidence:

1. `snapshot` hashes the 652 measurement files of `dev-20261006a`: shards, markers, merged
   rows, manifests and logs.
2. It copies the old `csv/`, `plots/` and `reports/` to `before/`.
3. After the export, `record` refuses if any input changed. Otherwise it writes the
   before/after comparison.

### 4.11 Freeze and unlock (`freeze.py`, `splits.py`)

| | |
|---|---|
| **Input** | a development run whose Arm A is COMPLETE; then the freeze path and the phrase |
| **Transformation** | fit the Platt calibration and the Youden threshold per pair on development → hash prompts, materials (all 9 lexicons), source and git → write once → `chmod 444` + `.sha256`. Unlock re-checks the freeze, the phrase and `frozen_drift` |
| **Output** | `DEV_FREEZE.json`, `HELDOUT_UNLOCK.json` |
| **Validation** | `load_unlock` runs on every held-out access and refuses any source, materials or model-pin drift, checked once per process |

### 4.12 Arm B (`p33/armb.py`) and H5 (`p33/h5.py`)

| | |
|---|---|
| **Input** | Arm B: instruct models, rendered NL requests, 4 demonstrations. H5: the run's merged Arm A |
| **Transformation** | Arm B: greedy decoding (≤ 192 tokens) → extract the program → normalise layout → bucket → `observe` each site → `hurdle`. H5: `define_arms` (targeted / random×5 / global) → `repaired_phi` (spellings from `beta`, I7 respected) → `ir_proof` over 284 renderings → score under the repaired lexicon |
| **Output** | `arm_b_generations.csv` (all text), `arm_b_hurdle.csv`; `manifests/h5_arms.json`, `h5_budget_outcomes.csv`, `h5_ir_proof.csv` |
| **Validation** | `h5.prepare` is idempotent: re-derived arms must equal the stored ones, or the job refuses. A failed proof aborts before scoring |

---

## 5. One site through the whole machine

`dom:d50s1:t000:T_CLASS_SIGIL:0`:

1. **Template** `t000`: an IR that selects `.wheel` and recolours it.
2. **Render** under `d50s1`: `(function(){ $S('#wheel')#recolor('#111111'); })();`.
   The sigil and, by I7, the chain operator are both swapped.
3. **Classify:** at char 17, `#` → `.` re-parses to a *different* valid IR, so the site is
   **SEMANTIC**, stratum `sigil`.
4. **Plan:** kept by within-cell de-duplication, then picked by balanced
   selection as one of the 4 sigil sites.
5. **Cells:**
   - Arm A puts it in `…_norule_0__7781…`, `…_rule_0__…` and `…_norule_lenmatched_0__…`.
   - Primary puts it in the ladder and paraphrase cells.
6. **Score:**

   | Condition | k_common | M |
   |---|---:|---:|
   | rule | 302 | **+0.6473** |
   | norule | 241 | +0.6913 |
   | norule_lenmatched | 311 | +0.6104 |

   In every condition `('#` vs `('.` is merged.
7. **Ladder:** M at 0, 1, 2, 4, 8 shots is +0.647, −1.396, −0.931, +0.510, +0.216. So
   `k* = 0`, non-monotone, `recrossed_down`, `sustained_k = 4`.
8. **Shard:** 4 rows in `arm_a_dom_d50s1_norule_0__7781962813a5e94d.jsonl`. The marker
   records sha `230d1726…`.
9. **Merge:** these rows land in `merged/arm_a.jsonl` (sha `8b23811c…`).
10. **Export:** the site appears in `arm_a_long.csv`, `extinction_rung_long.csv` and
    `kstar_survival.csv`, and feeds the `rule_effect.csv` mean (+0.182, where its own
    contribution is −0.044) and the KM summaries.
11. **H4:** not computable in the smoke, because there is no instruct twin.

---

## 6. Component status

The columns are:

- **Laptop smoke:** one model, 12 sites, a laptop GPU.
- **Sol development run:** `dev-20261006a`, four Qwen2.5-Coder checkpoints on A100s, completed
  2026-10-06 and re-analysed 2026-10-07.

| Component | Implemented | Unit-tested | Fake end-to-end | CLI rehearsal | Laptop smoke | Sol development run |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| split, freeze, unlock, drift | ✔ | ✔ | ✔ | ✔ | — (development only) | split ✔; **no freeze yet** |
| plan, de-duplication, expected cells | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ (852 sites, 400 primary) |
| canonical scorer + fp32 head | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ (1 GPU) |
| two-GPU sharded load (D10) | ✔ | registry, preflight, submit only | — | `submit.sh` with a stand-in `sbatch` | — | **NOT RUN** (needs two GPUs) |
| leak-free ladder | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| shards, resume, merge | ✔ | ✔ | ✔ | ✔ (real SIGUSR1) | ✔ | ✔ (COMPLETE; `validate` VALID) |
| `k*`, KM | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| rule effect + bootstrap | ✔ | ✔ | ✔ | ✔ | ✔ (no interval for strata < 8 clusters) | ✔ |
| fertility (real tokenizer) | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| H4 (tie-grouped AP / P@k since D9) | ✔ | ✔ | ✔ | ✔ | NOT RUN (needs an instruct twin) | ✔ (two pairs, development only) |
| Arm B | ✔ | ✔ | ✔ | ✔ | NOT RUN | NOT RUN |
| H5 | ✔ | ✔ | ✔ | ✔ | NOT RUN | NOT RUN |
| H2 | NOT TESTABLE | ✔ | ✔ | ✔ | — | — |
| power (per-scenario since D9) | ✔ | ✔ | ✔ | ✔ | ✔ (pilot n = 12, uninterpretable) | ✔ (real pilot) |
| Slurm jobs, `submit.sh` | ✔ | `bash -n` + text tests + stand-in `sbatch` | — | commands rehearsed | — | `dev_arm_a`, `dev_primary` and `dev_analyze` submitted and complete. Prefetch fetched all 11 original checkpoints (the Llama pair after its approval on 2026-10-07) |

---

## 7. Reproducibility checklist

- [x] Model revision pinned and checked at load (`scorer.revision != pin` → refuse).
- [x] Tokenizer fingerprint on every row.
- [x] Prompt sha on every row; demonstration ids, order sha and set sha on every ladder row.
- [x] Seeds in the config and in every manifest (bootstrap 20261002, demonstration order
      20261005, H5 random 1–5, power 20261006).
- [x] Config hash, source hashes (44 files, CLI included; 43 when `dev-20261006a` ran),
      materials hashes and git state per job.
- [x] Package, CUDA and driver versions measured per job.
- [x] Merge byte-deterministic; resumed output equals uninterrupted output.
- [x] Materials byte-stable under repeated test runs (P33-011).
- [x] Every figure regenerable from CSVs, every CSV from merged shards (`p33.py export`).
- [x] Re-derivations of a real run recorded with input hashes and before/after values
      (`scripts/analysis_revision.py`; `r1-2026-10-07-metric-corrections`).
- [ ] Sol lock file (`requirements.lock.sol.txt`): written by `make_env.sh` on Sol, not in this
      repository. `env/README.md` records the versions the development jobs measured.
- [ ] A real held-out run: requires the freeze and the unlock, by you.
