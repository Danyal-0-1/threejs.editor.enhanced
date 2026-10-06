# Phase 3.3 on ASU Sol — runbook

The commands below run the corrected Phase 3.3 pipeline on Sol, in the only
order the code permits. Why each step exists is in
[`sol_experiment_explained/`](sol_experiment_explained/); what was wrong before
and how it was verified is in [`AUDIT.md`](AUDIT.md); which parts of the brief
were corrected or not done is in [`PROMPT_REVIEW.md`](PROMPT_REVIEW.md).

> **Nothing here has been run on Sol.** The `p33.py` commands of §5–§12 were
> rehearsed locally, in this order, with the fake scorer (`AUDIT.md` §6), and
> `submit.sh` was checked against a stand-in `sbatch`. Slurm itself and the
> network download were not exercised. One real-model development smoke ran on
> a laptop GPU. The Sol values below (account, partition, QOS, GPU
> flags, shared-env behaviour) are the ones **you** verified on 2026-10-05. They
> are defaults in `sol.env`, and any of them can be overridden from the environment.

---

## 0. The five rules

1. **Never skip a step's check.** Each step below ends with the thing to look at
   before starting the next one.
2. **Resume means resubmitting the same command.** Finished cells are never
   redone. A different configuration under the same run id is refused.
3. **Do not edit `.py` files after `dev freeze`.** Every held-out command
   re-hashes the source, the materials and the model pins, and refuses on any
   difference.
   Commit before you freeze (§8).
4. **Held-out needs two acts by you**: an immutable freeze, then an unlock with
   a typed phrase. No job, script or flag does either for you.
5. **Submit only through `submit.sh`.** It creates the log directory first (Slurm
   cannot write a log into a directory that does not exist) and takes account,
   partition, QOS and GPU flags from `sol.env`.

## 1. Layout on Sol

| What | Where (default) | Override |
|---|---|---|
| code | `$HOME/phase3-3_experiment_sol/repo` | `P33_CODE_ROOT` |
| results (one directory per run) | `$HOME/phase3-3_experiment_sol/results/<run_id>/` | `P33_RESULTS_ROOT` |
| project environment | `$HOME/phase3-3_experiment_sol/env` | `P33_ENV_DIR` |
| model weights | `$SCRATCH/hf` (`HF_HOME`), `$SCRATCH/hf/hub` (`HF_HUB_CACHE`) | `P33_HF_ROOT` |
| scheduler | `--account=grp_tlingego --partition=public --qos=public` | `P33_ACCOUNT` / `P33_PARTITION` / `P33_QOS` |
| GPU | `--gres=gpu:a100:1 --constraint=a100_80` | `P33_GRES` / `P33_CONSTRAINT` |

Weights, tokens and credentials never go into Git or into `results/`.

Every login-node command below assumes this prelude in your shell:

```bash
cd $HOME/phase3-3_experiment_sol/repo/phase3_2/sol
source sol.env && source env/activate.sh      # activate.sh is safe under `set -u`
P33="$P33_PY scripts/p33.py"
```

Pick the run ids once and reuse them (each id must start with its stage):

```bash
SMOKE=smoke-$(date +%Y%m%d)   DEV=dev-$(date +%Y%m%d)   HO=heldout-$(date +%Y%m%d)
```

---

## 2. Environment (once)

```bash
mkdir -p $HOME/phase3-3_experiment_sol
git clone <your remote> $HOME/phase3-3_experiment_sol/repo      # or rsync the working tree
cd $HOME/phase3-3_experiment_sol/repo/phase3_2/sol
source sol.env
bash env/make_env.sh                  # MODE=overlay (default) | MODE=standalone
source env/activate.sh && $P33_PY scripts/p33.py env-check
```

- **Overlay** (the default) is a venv on top of `/packages/envs/pytorch-gpu-2.3.1-cuda-12.1`, using
  `--system-site-packages`. Torch comes from the shared env, which reported
  torch 2.11.0+cu130 despite the name. `lark` and the other dependencies are added from
  `env/requirements.in`. The shared env itself is never modified.
- **Standalone** is a fresh venv with torch from the PyTorch cu121 wheel index.
  It is slower to build, but immune to the shared env changing under you.
- The resolved versions are written to `$P33_ENV_DIR/requirements.lock.sol.txt` and to `env/`.
- **Check:** `env-check` prints `"missing_required": []` and exits 0.

## 3. Materials and tests (CPU)

```bash
bash submit.sh cpu_tests setup-$(date +%Y%m%d)
```

This runs the Sol suite, the Phase 3.2 suite and the Phase 3 suite with the
fake scorer. It needs no GPU and no weights.

**Check** `results/setup-*/logs/p33-cpu_tests-*.out`:

- the last line is `cpu_tests: overall exit=0`;
- **exactly one BLOCKED** test, the A100 preflight test, marked
  `(blocked for want of a GPU: expected with --cpu-node)`.

Any FAIL, or any BLOCKED for a *missing dependency*, means stop. The latter is the
failure Sol's shared env produced before (no `lark`: 14 passed / 22 failed).
Expected local counts are given in §13.

## 4. Prefetch (download only)

```bash
export HF_TOKEN=...            # only for the gated Llama-3.2-1B pair; accept its licence on the Hub first
bash submit.sh prefetch setup-$(date +%Y%m%d)
```

- **What it fetches by default:** exactly the 11 models used by `configs/{smoke,dev,heldout}.json`, none
  above 3B. To fetch others, set `P33_MODELS="id1 id2"`. Do **not** use
  `P33_TIER=mid|large`: those tiers contain 7B–32B checkpoints that no stage
  may score (`MAX_SIZE_B = 3.0`).
- **What it does:** a `--dry-run` that lists each model's revision, files and bytes, then a download of
  pinned revisions with retries, size checks and sha256 checks. Nothing is
  instantiated. The output is `results/model_pins.json`: revision, `allow_patterns` and file hashes
  for each model, plus any failures.
- **Re-running is safe.** An already-pinned model keeps its revision, so you can
  re-run prefetch later (for example, to add the Llama pair) without moving any
  other model. `--repin` moves pins to the Hub's current commit. Never use it
  after a freeze: every held-out command would then refuse on pin drift.
- **If compute nodes cannot reach the Hub**, run the same command on the data-transfer node:
  `$P33 prefetch --config configs/smoke.json configs/dev.json configs/heldout.json --checksums`.
- **Check:** `"failed": {}` and `"pairing_problems": []` in the job log.
  - If you cannot get Llama access, remove that pair from `configs/heldout.json`
    **before** `heldout init` (§9), and record the change as a dated deviation in
    `phase3_2/PREREGISTRATION.md`.

## 5. Preflight and smoke (one GPU job)

```bash
bash submit.sh smoke $SMOKE
```

This runs `env-check`, then `smoke`. The smoke covers init, the full GPU preflight, then
Arm A and primary for **one** cached 0.5B model, **one** development lexicon
(`d50s1`) and **one** family (`dom`), 12 sites. It then computes fertility from the real
tokenizer, merges, and exports.

**Check** `results/$SMOKE/`:

- **Preflight:** every line in `logs/p33-smoke-*.out` is `[PASS]`. The `a100` check must not be
  waived on Sol.
- **Completeness:** `reports/RUN_SUMMARY.md` shows Arm A and primary `COMPLETE`.
- **Measurement health:** `reports/QUALITY_CONTROL.md` shows `exact_zero_margins 0` and `ties 0`.
- **Fertility:** `csv/fertility.csv` has real numbers. On the laptop: identity `dom` 2,928
  tokens and 0.3669 tokens per char; `d50s1` 3,158 tokens and 0.3950.
  The same tokenizer must reproduce these exactly.

## 6. Development Arm A (GPU array, one task per model)

```bash
$P33 dev init --config configs/dev.json --run $DEV
bash submit.sh dev_arm_a $DEV
```

- **Size:** 4 models (Qwen2.5-Coder 0.5B/1.5B, base + instruct) × `dom` × 4 development
  lexicons. That is 852 sites × 3 conditions (rule, norule, norule_lenmatched),
  so 2,556 rows and 48 cells per model, 192 cells in total.
- **Array mapping:** task *i* scores model *i* of `results/$DEV/manifests/run_config.json`.
- **Each task:** preflight, then score. Every finished cell is an atomic shard with a
  sha256 marker.
- **Check:** `$P33 status --run $DEV` shows `arm_a expected=192 {'done': 192}`.

## 7. Development primary (GPU array)

```bash
bash submit.sh dev_primary $DEV          # may run alongside dev_arm_a
```

- **Size:** 400 sites (95 / 62 / 123 / 120 per lexicon). Each site gets the
  leakage-free ladder (0, 1, 2, 4, 8, 16, 32 shots) and 3 paraphrases. That is 4,000 rows and 28 cells
  per model.
- **Check:** `status` shows `primary expected=112 {'done': 112}`.

## 8. Development analysis, power, then freeze

```bash
bash submit.sh dev_analyze $DEV          # fertility + merge + 19 CSVs + plots + 10 reports + validate
```

**Read** `results/$DEV/reports/` in this order:

1. `RUN_SUMMARY.md`
2. `QUALITY_CONTROL.md`
3. `DEVELOPMENT_RESULTS.md`
4. `POWER_ANALYSIS.md` — clustered power from **this** pilot. It decides whether the held-out
   sample is large enough. If it is not, change `configs/heldout.json` now, not later.

Every development number is labelled exploratory.

**Then freeze.** Commit first, so the freeze's `git` record can restore the frozen
code exactly:

```bash
cd $HOME/phase3-3_experiment_sol/repo && git add -A phase3_2 phase3 && git commit -m "freeze $DEV"
cd phase3_2/sol && bash submit.sh dev_freeze $DEV
```

- **Inputs:** `dev_freeze` runs `validate` and refuses unless every *started* experiment is complete,
  then writes `results/$DEV/DEV_FREEZE.json` (mode 444) and its `.sha256`.
- **Contents of the freeze:**
  - risk formula, Platt calibration and decision thresholds;
  - prompts;
  - exclusion rules, analysis settings and seeds;
  - config hash and the materials of **all** lexicons;
  - source hashes and git state;
  - model pins.
- **A freeze is permanent.** A second freeze is refused. To change anything,
  start a new development run.
- **Expect `git.dirty` to be true.** This repository tracks `__pycache__/*.pyc`
  files, which Python rewrites in a fresh clone, so the flag reads true even
  right after the commit. The hashes of the 43 source files are what the
  held-out stage enforces; the commit is how you would restore them.

## 9. Explicit held-out unlock (you, on the login node)

```bash
$P33 heldout init --config configs/heldout.json --run $HO --freeze $P33_RESULTS_ROOT/$DEV/DEV_FREEZE.json
$P33 heldout unlock --run $HO --confirm "I have finished the development analysis and will not change it"
```

- **Unlock refuses** unless the phrase is exact, the freeze is intact, and the
  source, the materials and every frozen model pin still match the freeze.
  Every later held-out command re-checks all three.
- **It writes** `results/$HO/HELDOUT_UNLOCK.json` (mode 444).
- **Before unlock**, any held-out command is refused with `held-out cells are locked`.

## 10. Held-out evaluation (GPU array, 11 tasks)

```bash
bash submit.sh heldout_eval $HO
```

- **Per task:** preflight, held-out Arm A, held-out primary.
- **Models:** the 4 development models plus Qwen 3B (base + instruct, labelled
  **HELDOUT-WEAKENED**, deviation D2), deepseek-coder 1.3B (pair), Llama-3.2-1B (pair) and
  starcoder2-3B.
- **Cells:** `dom` and `blk` × the 5 held-out lexicons. `blk` cells are
  **HELDOUT-WEAK-FAMILY** (deviation D1).
- **Exact sizes:** printed by `$P33 status --run $HO`. They cannot be computed before the
  unlock, because the planner refuses to enumerate held-out cells while they are locked.

## 11. Arm B and H5 (GPU arrays)

```bash
bash submit.sh arm_b $HO                 # instruct models only; base-model tasks exit as no-ops
bash submit.sh h5 $HO --dependency=afterok:<heldout_eval job id>    # needs merged held-out Arm A
```

- **Arm B:** greedy generation with every output saved, five outcome buckets, and the hurdle
  P(reach) and P(correct | reach) kept separate.
- **H5:** targeted, random (5 seeds) and global repair arms, each chosen from base-model
  risk, each proven IR-preserving over the whole corpus before anything is scored.
- **Development run:** both jobs also accept `$DEV`. On a development run they are exploratory,
  and running them after the freeze changes nothing that was frozen.

## 12. Final export

```bash
bash submit.sh final_export $HO           # and, if wanted, again for $DEV
```

- **Outputs:**
  - `results/$HO/csv/` — 19 tables;
  - `plots/` — 12 figures, each as PNG + SVG;
  - `reports/` — 10 Markdown reports.
- **Labelling:** every table, figure and report carries its stage, split label, model
  revision, tokenizer and prompt hashes, cluster counts, and bootstrap
  settings. Data that does not exist is written as `NOT RUN` or `NOT TESTABLE`,
  never as a placeholder number. A PARTIAL run says PARTIAL on every report.

---

## 13. Monitor, resume, merge, validate, regenerate

| Purpose | Command |
|---|---|
| queue | `squeue -u $USER` |
| finished-job accounting | `sacct -j <jobid> --format=JobID,JobName%22,State,Elapsed,ExitCode,MaxRSS` |
| live log | `tail -f $P33_RESULTS_ROOT/<run>/logs/p33-<job>-<jobid>_<task>.out` |
| per-experiment progress | `$P33 status --run <run>` |
| failed cells | `<run>/csv/failed_cells.csv` (after export), `<run>/checkpoints/<exp>/*.failed.json` |
| **resume a whole array** | resubmit the same line: `bash submit.sh dev_arm_a $DEV` |
| **resume one model** | `P33_ARRAY=2 bash submit.sh dev_arm_a $DEV` (or `P33_ARRAY=1,3`) |
| merge (deterministic, verifies every shard) | `$P33 merge --run <run> [--experiment arm_a]` |
| validate (exit 0 = every started experiment complete; 3 = not) | `$P33 validate --run <run>` |
| regenerate CSVs → plots → reports (no model, no GPU) | `$P33 export --run <run>` |
| cancel | `scancel <jobid>` (cells finished so far stay finished) |

- **Time limits:** Slurm sends `SIGUSR1` 300 s before a job's time limit (`--signal=USR1@300`). The task
  stops at the next site boundary and discards the unfinished cell, whose rows were never written. It
  writes its manifest as `INTERRUPTED` and exits 4. Resubmitting redoes that cell and continues.
- **Failures:** a crash or out-of-memory error in one cell is recorded as `failed` with its kind
  (OOM / INTERRUPTED / ERROR), and the job continues. Corrupt shards are quarantined and
  redone.
- **Resume test:** the merged output of an interrupted-and-resumed run is
  byte-identical to an uninterrupted one (`test_resumed_output_equals_uninterrupted_output`).
  The same was checked with a real SIGUSR1 on the final code: 960 rows, identical bytes.

**Exit codes of `p33.py`:**

| Code | Meaning |
|---:|---|
| 0 | complete |
| 1 | error |
| 2 | refusal (preflight, split, freeze or unlock) |
| 3 | partial or incomplete |
| 4 | interrupted — resume with the same command |

### Local verification (all on 2026-10-05)

| What | Result |
|---|---|
| `tests/run_tests.py`, project venv | 112 passed, 0 failed, 0 blocked |
| same, bare `python3` | 110 passed, 0 failed, 2 blocked (matplotlib, torch absent): exit 5, correctly not green |
| `../tests` (Phase 3.2) | 36 passed |
| `../../phase3/tests` | 54 passed |
| `jobs/cpu_tests.slurm` run as Slurm would, on CPU only (`srun` stand-in) | Sol 111 passed + 1 blocked for want of a GPU; Phase 3.2 36; Phase 3 54; job exit 0 |
| `submit.sh` with a stand-in `sbatch`, all jobs | correct account / partition / QOS / GPU flags; arrays `0-3` (dev) and `0-10` (held-out); `P33_ARRAY=2` → `--array=2`; log dirs created; `P33_FAKE` not exported |
| full CLI rehearsal with the fake scorer, §5–§12 in order | see `AUDIT.md` §6 |

---

## 14. Cost and time

These are **planning estimates, not measurements on Sol.** The only real timing is the laptop smoke on an RTX 3080 Ti with
Qwen 0.5B, model load included: 36 Arm A rows in 6 s and 48 primary rows (ladder ≤ 8) in 4 s.
That is at most ≈ 0.17 s per row. The estimates below assume:

- 0.15 s per row for 0.5B, scaled by parameter count (×3 for 1–1.5B, ×6 for 3B);
- primary prompts ≈ 1.7× longer than Arm A, because the ladder runs to 32 shots;
- an A100 at least as fast as the laptop GPU.

Treat every figure as ±2×. Re-plan from the first real manifest: each
`manifests/job_*.json` records `start_utc`, `end_utc` and the cells it scored.

### Development (`configs/dev.json`)

The site and row counts are exact, from the planner.

| Task | Rows per model | 0.5B, per model | 1.5B, per model | Array wall time | GPU-hours |
|---|---:|---:|---:|---|---:|
| `dev_arm_a` (4 tasks) | 2,556 | ~6 min | ~20 min | ~20–30 min | ~0.9 |
| `dev_primary` (4 tasks) | 4,000 | ~17 min | ~50 min | ~1 h | ~2.3 |
| `arm_b` on dev (2 instruct tasks) | ≤ 320 generations × 192 tokens | ~16 min | ~27 min | ~30 min | ~0.7 |
| `h5` on dev (2 instruct tasks) | ≈ 7 arms × the Arm A rule-condition sites | ~15 min | ~45 min | ~45 min | ~1 |
| `dev_analyze`, `dev_freeze`, `final_export` | — | CPU | CPU | ~10–30 min each | 0 |

**Development total:** ≈ 5 GPU-hours, ≈ 3 hours of wall time plus queue.

### Held-out (`configs/heldout.json`, 11 tasks)

The sizes are estimates, because the held-out cells cannot be counted before the unlock. Development cells hold 88–272
sites. With 10 held-out cells (2 families × 5 lexicons), expect roughly 2,000–3,000 sites:
6,000–9,000 Arm A rows plus 4,000 primary rows per model.

| Model tier | Models | GPU-hours per model | Total GPU-hours |
|---|---|---:|---:|
| 0.5B | Qwen pair | ~0.6 | ~1.2 |
| 1–1.5B | Qwen 1.5B pair, deepseek 1.3B pair, Llama 1B pair | ~1.8 | ~11 |
| 3B | Qwen 3B pair, starcoder2-3B | ~3.6 | ~11 |
| Arm B + H5, 5 instruct models | — | ~0.5–2 | ~6 |

**Held-out total:** ≈ 30 GPU-hours. The longest single task is a 3B model at ~3.6 h,
inside the 10 h `heldout_eval` limit. Every limit in `submit.sh` has at least 2.5× headroom over these estimates.

The cost in service units depends on your allocation's charging rules for the
`public` QOS, which were not verified here. Memory is not a constraint:
3B in bf16 is under 8 GB, and the fp32 output head is about 1.2 GB.

---

## 15. Status of this hand-off

- **Done:** the corrected pipeline; 112 tests; the fake-scorer CLI rehearsal of every step
  above; **one** development smoke (laptop GPU, A100 check waived and recorded).
- **Not done:** anything on Sol; any held-out real-model scoring; any full development sweep.
  **No held-out outcome was inspected and no full sweep was submitted.**
- **Not testable with these materials** (`sol_experiment_explained/08`):
  - H4 criterion C3 (no valid held-out grammar family);
  - H2 (no calibrated prior-strength or local-context levels).
