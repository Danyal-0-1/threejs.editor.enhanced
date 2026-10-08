# Phase 3.3 on ASU Sol — runbook

The commands below run the corrected Phase 3.3 pipeline on Sol, in the only
order the code permits.

| For | Read |
|---|---|
| why each step exists | [`sol_experiment_explained/`](sol_experiment_explained/) |
| what was wrong and how it was verified | [`AUDIT.md`](AUDIT.md) |
| which parts of the original brief were corrected or not done | [`PROMPT_REVIEW.md`](PROMPT_REVIEW.md) |

> **Where things stand (2026-10-07, 23:10 MST)**
>
> - **Development run.** `dev-20261006a` is complete: 4 models, 192/192 Arm A and 112/112 primary
>   cells. Its corrected analysis (D9) was re-derived **on Sol** without re-scoring
>   (`analysis_revisions/r1-2026-10-07-metric-corrections`):
>   - 652 inputs are byte-identical and every check passed;
>   - the source digest is `3c3e772c66ecf51e`, the same as the local record (§13).
> - **Models.** All **21** held-out checkpoints are on `$SCRATCH/hf` (641 GB) and pinned:
>   - the 10 D10 checkpoints came from prefetch job 64939806, with every file's sha256 verified;
>   - the gated Llama-3.2-1B pair was approved on 2026-10-07.
> - **Freeze.** `results/dev-20261006a/DEV_FREEZE.json` was written by job 64942745 on 2026-10-07:
>   sha256 `b319c3fc…`, commit `78b2bcd`, 21 model pins, 44 source hashes.
> - **Held-out run `heldout-20261007a`.**
>   - It was unlocked on 2026-10-07 at the investigator's direction (`UNLOCK_NOTE.md` in the run
>     directory).
>   - The whole stage runs as **one chain, one job at a time** (`submit_chain.sh`, §10). The job ids
>     are in `results/heldout-20261007a/logs/submission_chain.env`.
>   - Expect 2–4 days (§15).
> - **Keep Sol's checkout at `78b2bcd` until the chain finishes.** Every held-out job re-checks the
>   source against the freeze, and a changed source file stops it.

---

## 0. The five rules

1. **Never skip a step's check.** Each step below ends with the thing to look at
   before starting the next one.
2. **Resume means resubmitting the same command.** Finished cells are never
   redone. A different configuration under the same run id is refused.
3. **Do not edit `.py` files after `dev freeze`.** Every held-out command
   re-hashes the source, the materials and the model pins, and refuses on any
   difference. Commit before you freeze (§8).
4. **Held-out needs two acts by you**: an immutable freeze, then an unlock with
   a typed phrase. No job, script or flag does either for you.
5. **Submit only through `submit.sh`.** It creates the log directory first,
   takes account, partition, QOS and GPU flags from `sol.env`, and sends each
   model to the job profile of its GPU class (§10).

## 1. Layout on Sol

| What | Where (default) | Override |
|---|---|---|
| code | `$HOME/phase3-3_experiment_sol/repo` | `P33_CODE_ROOT` |
| results (one directory per run) | `$HOME/phase3-3_experiment_sol/results/<run_id>/` | `P33_RESULTS_ROOT` |
| project environment | `$HOME/phase3-3_experiment_sol/env` | `P33_ENV_DIR` |
| model weights | `$SCRATCH/hf` (`HF_HOME`), `$SCRATCH/hf/hub` (`HF_HUB_CACHE`) | `P33_HF_ROOT` |
| scheduler | `--account=grp_tlingego --partition=public --qos=public` | `P33_ACCOUNT` / `P33_PARTITION` / `P33_QOS` |
| one GPU | `--gres=gpu:a100:1 --constraint=a100_80` | `P33_GRES` / `P33_CONSTRAINT` |
| two GPUs (the 72B pair) | `--gres=gpu:a100:2 --constraint=a100_80` | `P33_GRES_2GPU` |

Weights, tokens and credentials never go into Git or into `results/`.

Every login-node command below assumes this prelude:

```bash
cd $HOME/phase3-3_experiment_sol/repo/phase3_2/sol
source sol.env && source env/activate.sh      # activate.sh is safe under `set -u`
P33="$P33_PY scripts/p33.py"
DEV=dev-20261006a                             # the completed development run
HO=heldout-$(date +%Y%m%d)
```

---

## 2. Environment (once — done)

```bash
bash env/make_env.sh                  # MODE=overlay (default) | MODE=standalone
source env/activate.sh && $P33_PY scripts/p33.py env-check
```

**Check:** `"missing_required": []`.

The versions Sol actually ran are recorded in [`env/README.md`](env/README.md):
torch 2.8.0+cu126, transformers 4.57.1, Python 3.12.3, accelerate 1.11.0.

## 3. Materials and tests (CPU)

```bash
bash submit.sh cpu_tests setup-$(date +%Y%m%d)
```

**Check** the job log:

- the last line is `cpu_tests: overall exit=0`;
- exactly one test is BLOCKED (the A100 test, which needs a GPU);
- any FAIL, or any BLOCKED for a missing dependency, means stop.

Since 2026-10-07 the test runner always uses a fresh temporary results root.
Before that, `sol.env` (which exports the real root) made two tests of the
committed code touch `$P33_RESULTS_ROOT` whenever the CPU-test job ran. On Sol it did:
`results/dev-status-readonly/` dates from 2026-10-06. On 2026-10-07 it was moved, not
deleted, to `results/_quarantine/`. The pins file was checked: its development
revisions match the job manifests. If you ran `cpu_tests` anywhere else before this fix,
check for both:

1. **A fake-scored run directory.** `test_status_is_read_only_so_validate_still_passes`
   created `$P33_RESULTS_ROOT/dev-status-readonly/`. It contains fake-scored test rows, not
   measurements: if it exists, delete it.
2. **A temporary pins file.** `test_a_model_repinned_after_the_freeze_is_refused` wrote a test
   pins file over `$P33_RESULTS_ROOT/model_pins.json`, restoring the original afterwards (or
   removing the file if there was none yet). Check that `model_pins.json` still lists your
   downloaded models with the revisions recorded in your job manifests. If the CPU-test and
   prefetch jobs ran at the same time, re-run `prefetch --verify-only` to rebuild it from the
   cache.

## 4. Prefetch (download only)

```bash
export HF_TOKEN=...                      # needed only for the gated Llama-3.2-1B pair
bash submit.sh prefetch setup-$(date +%Y%m%d)
```

- **What it fetches:** the 21 checkpoints used by `configs/{smoke,dev,heldout}.json`.
- **What it does:** a dry run with sizes and revisions, then pinned downloads with retries,
  size and sha256 checks. Nothing is instantiated.
- **Already-pinned models keep their revision**, so re-running is safe. `--repin` moves pins to
  the Hub's current commit; never use it after a freeze.
- **Disk:** about **0.7 TB** in `$SCRATCH` for all 21 checkpoints. The 72B pair alone is about
  290 GB; the two 32/33B pairs about 270 GB. The dry run prints the exact figure; check your
  quota and the scratch purge policy before downloading.
- **The Llama-3.2-1B pair is gated.** Access for `Daniel-00` was granted on 2026-10-07. The
  first two prefetch attempts that day got 401 and 403; the third (job 64914503) downloaded and
  pinned both. `HF_TOKEN` is needed again only to re-download them.
  - For any gated model still pending, do not resubmit while you wait: prefetch records the
    failure and downloads everything else.
  - Dropping a model is **your** decision. Make it before the freeze (§8), because pins taken
    after the freeze are not drift-checked. Record it as a dated deviation.
- **If compute nodes cannot reach the Hub**, run the same command on the data-transfer node:
  `$P33 prefetch --config configs/smoke.json configs/dev.json configs/heldout.json --checksums`.
- **Check:** `"failed": {}` and `"pairing_problems": []`.

## 5–7. Smoke, development Arm A and primary — done

`dev-20261006a` is complete. For a future development run the commands are:

```bash
bash submit.sh smoke smoke-$(date +%Y%m%d)
$P33 dev init --config configs/dev.json --run dev-<date>
bash submit.sh dev_arm_a dev-<date> && bash submit.sh dev_primary dev-<date>
```

**Check:** `$P33 status --run dev-<date>` shows every cell done.

## 8. Development analysis, then freeze

**Done on 2026-10-07.** The corrections were applied and recorded on Sol (§13), and the
freeze was written by job 64942745. The procedure is kept below for reference.

Then read `results/$DEV/reports/` in this order:

1. `RUN_SUMMARY.md`
2. `QUALITY_CONTROL.md`
3. `DEVELOPMENT_RESULTS.md`
4. `POWER_ANALYSIS.md` — the full ICC sensitivity, with the pilot estimate flagged.

At the pilot clustering, the pooled rule effect has power **0.251** at 80
templates (the whole corpus). 80% power is not reached even at 320 templates,
which would need new materials. H4 criterion 1 is well powered for AUROC ≥ 0.62.
Whether to change the design before freezing is your decision; nothing was
changed automatically.

When you decide to freeze, commit first:

```bash
cd $HOME/phase3-3_experiment_sol/repo && git add -A phase3_2 phase3 && git commit -m "freeze $DEV"
cd phase3_2/sol && bash submit.sh dev_freeze $DEV
```

- **Inputs:** `dev_freeze` validates, then writes `results/$DEV/DEV_FREEZE.json` (mode 444) and
  its `.sha256`.
- **Contents of the freeze:**
  - the calibration and decision thresholds;
  - prompts and exclusion rules;
  - analysis settings and seeds;
  - the config hash and the materials of all lexicons;
  - source hashes, git state and model pins.
- **Model pins:** pins taken after the freeze are not compared, so prefetch the held-out models
  you intend to use before freezing.
- **`git.dirty` will read true.** The repository tracks `__pycache__` files; the source hashes
  are what is enforced.

## 9. Explicit held-out unlock (you, on the login node)

```bash
$P33 heldout init --config configs/heldout.json --run $HO --freeze $P33_RESULTS_ROOT/$DEV/DEV_FREEZE.json
$P33 heldout unlock --run $HO --confirm "I have finished the development analysis and will not change it"
```

The unlock refuses unless the phrase is exact, the freeze is intact, and the
source, the materials and every frozen model pin still match. Every later
held-out command re-checks all three.

## 10. Held-out evaluation — two GPU classes

```bash
bash submit.sh heldout_eval      $HO   # models 0-18, one A100-80GB each
bash submit.sh heldout_eval_2gpu $HO   # models 19-20 (the Qwen2.5-72B pair), two A100-80GB each
```

| Index | Models | Label |
|---:|---|---|
| 0–3 | Qwen2.5-Coder 0.5B, 1.5B (base + instruct) | HELDOUT (new mappings) |
| 4–5 | Qwen2.5-Coder 3B | HELDOUT-WEAKENED (D2) |
| 6–7 | deepseek-coder 1.3B | HELDOUT model |
| 8–9 | Llama-3.2-1B | HELDOUT model (gated; downloaded 2026-10-07) |
| 10 | starcoder2-3B (no instruct twin: never in H4) | HELDOUT model |
| 11–16 | **Qwen2.5-Coder 7B, 14B, 32B** | HELDOUT model (D10) |
| 17–18 | **DeepSeek-Coder-33B** | HELDOUT model (D10) |
| 19–20 | **Qwen2.5-72B** | HELDOUT model (D10); 2 GPUs |

- **Cells:** `dom` and `blk` × the 5 held-out lexicons. `blk` cells are HELDOUT-WEAK-FAMILY (D1).
- **Preflight:** checks only the models of its own array task. A model that is not downloaded
  fails its own task and nothing else.
- **Resubmitting some models:** `P33_ARRAY=8,9 bash submit.sh heldout_eval $HO`.
- **Exact sizes:** printed by `$P33 status --run $HO` after the unlock.

**What ran on 2026-10-07** — the whole held-out stage as one chain, one job at a time:

```bash
bash submit_chain.sh heldout-20261007a      # after `heldout init` and the unlock
```

- **Order:** held-out evaluation (models 0–18, then the 72B pair) → Arm B → H5 → final
  export. Arrays use `%1`, so only one task runs at a time.
- **Gaps don't stall it:** each stage starts when the previous one ends (`afterany`). A failed
  task is resubmitted later with `P33_ARRAY`.
- **Instruct models only:** Arm B and H5 are submitted just for the instruct models (indices
  1, 3, 5, 7, 9, 12, 14, 16, 18 and 20). Base-model tasks would be no-ops holding a GPU.
- **H5 gating:** H5 also requires both evaluation jobs to have succeeded (`afterok`). It derives
  its arms from the merged held-out Arm A and stores them for good, so it must never start on an
  incomplete Arm A.
- **Time limits:** Arm B and H5 get 12 h and 10 h per task. `submit.sh`'s defaults (8 h, 6 h) are
  tight for the 32B/33B models.

## 11. Arm B and H5

```bash
bash submit.sh arm_b      $HO   &&  bash submit.sh arm_b_2gpu $HO        # instruct models only
bash submit.sh h5 $HO --dependency=afterok:<heldout_eval job>  &&  bash submit.sh h5_2gpu $HO --dependency=afterok:<heldout_eval_2gpu job>
```

H5 needs the merged held-out Arm A of the same run.

## 12. Final export

```bash
bash submit.sh final_export $HO
```

This writes 19 CSVs, 12 figures (PNG + SVG) and 10 reports. Data that does not exist reads
NOT RUN or NOT TESTABLE, and a PARTIAL run says so on every report.

**Then the D10 scale analysis**, as specified by deviation D11. It reads the export's CSVs,
uses no GPU and is not part of the frozen code:

```bash
git pull                                     # after the chain has finished: brings in the script
$P33_PY scripts/scale_analysis.py --run $HO   # -> results/$HO/analysis_addenda/d11_scale/
```

- **What it computes:** the slope of the reversion rate (base and instruct) and of the H4
  AUROC on log10(size), across the Qwen2.5-Coder ladder, for each grammar family.
- **Uncertainty:** template-cluster bootstrap intervals and Holm-adjusted two-sided p values.

---

## 13. Re-deriving an analysis from saved measurements (CPU, no model)

This is how the development analysis was corrected on 2026-10-07. Nothing is re-scored.

`analysis_revision.py snapshot` hashes every measurement input and copies the current CSVs,
plots and reports to `analysis_revisions/<rev>/before/`. `record` then refuses unless every input is
still byte-identical, and writes the before/after comparison.

**Locally** (the downloaded run in `phase3_3/sol_results/`; already done, recorded in
`dev-20261006a/analysis_revisions/r1-2026-10-07-metric-corrections/`):

```bash
cd phase3_2/sol
export P33_RESULTS_ROOT=$PWD/../../phase3_3/sol_results
PY=../../run/.venv/bin/python
$PY scripts/analysis_revision.py snapshot --run dev-20261006a --rev r1-2026-10-07-metric-corrections --reason "..."
$PY scripts/p33.py export --run dev-20261006a
$PY scripts/analysis_revision.py record --run dev-20261006a --rev r1-2026-10-07-metric-corrections \
    --command "p33.py export --run dev-20261006a"
# read-only completeness check; validation pins built from the run's job manifests (the real pins file stays on Sol)
$PY scripts/p33.py --pins $P33_RESULTS_ROOT/dev-20261006a/analysis_revisions/r1-2026-10-07-metric-corrections/validation_pins.json \
    status --run dev-20261006a
```

**On Sol** (after pulling or copying the reviewed changes into `repo/`):

```bash
cd $HOME/phase3-3_experiment_sol/repo && git pull         # or rsync the reviewed working tree
cd phase3_2/sol && source sol.env && source env/activate.sh
bash submit.sh cpu_tests setup-$(date +%Y%m%d)              # check: overall exit=0
$P33_PY scripts/analysis_revision.py snapshot --run $DEV --rev r1-2026-10-07-metric-corrections \
    --reason "D9: tied-score AP/P@k, per-ICC power scenarios, power report, artifact counts"
$P33_PY scripts/p33.py validate --run $DEV                  # VALID (the real model_pins.json is used)
srun --account=$P33_ACCOUNT --partition=$P33_PARTITION --qos=$P33_QOS \
     --cpus-per-task=8 --mem=32G --time=01:00:00 \
     $P33_PY scripts/p33.py export --run $DEV               # CPU only, on a compute node
$P33_PY scripts/analysis_revision.py record --run $DEV --rev r1-2026-10-07-metric-corrections \
    --command "p33.py export --run $DEV"
cat $P33_RESULTS_ROOT/$DEV/analysis_revisions/r1-2026-10-07-metric-corrections/ANALYSIS_REVISION.md
```

Between `snapshot` and `record`, run **only** `validate` and `export`. Do not run
`dev fertility` or the `dev_analyze` job there. They rewrite `manifests/fertility.json`,
a recorded input, and with a different tokenizer library `record` would rightly refuse.
`validate` re-merges, but the merge is byte-deterministic: on a copy of the run, all 652
inputs stayed byte-identical.

**Expect:**

- `record: inputs byte-identical (652 files); 2 CSV(s) changed; checks ALL PASSED`;
- the same analysis-source digest as the local record, `3c3e772c66ecf51e`, when the code is
  identical;
- if the record refuses or a check fails, stop and investigate before freezing.

## 14. Monitor, resume, merge, validate, regenerate

| Purpose | Command |
|---|---|
| queue | `squeue -u $USER` |
| finished-job accounting | `sacct -j <jobid> --format=JobID,JobName%22,State,Elapsed,ExitCode,MaxRSS` |
| live log | `tail -f $P33_RESULTS_ROOT/<run>/logs/p33-<job>-<jobid>_<task>.out` |
| progress (read-only) | `$P33 status --run <run>` |
| failed cells | `<run>/csv/failed_cells.csv`, `<run>/checkpoints/<exp>/*.failed.json` |
| **resume** | resubmit the same line |
| resume some models only | `P33_ARRAY=2 bash submit.sh <job> <run>` |
| merge (deterministic, verifies shards) | `$P33 merge --run <run> [--experiment arm_a]` |
| validate (0 = every started experiment complete; 3 = not) | `$P33 validate --run <run>` |
| regenerate CSVs → plots → reports (no model) | `$P33 export --run <run>`, wrapped by §13 when it matters |
| cancel | `scancel <jobid>` (finished cells stay finished) |
| the held-out chain's job ids | `cat $P33_RESULTS_ROOT/heldout-20261007a/logs/submission_chain.env` |
| the whole chain at once | `sacct -j $(grep -o '^[A-Z0-9_]*JID=[0-9]*' $P33_RESULTS_ROOT/heldout-20261007a/logs/submission_chain.env \| cut -d= -f2 \| paste -sd,) -X --format=JobID%18,JobName%22,State,Elapsed` |
| a failed held-out task (model *i*) | `P33_ARRAY=i bash submit.sh heldout_eval heldout-20261007a` (or `heldout_eval_2gpu` for 19, 20) |

**Interrupts and failures:**

- **Time limit:** Slurm sends `SIGUSR1` 300 s before a job's time limit. The task stops at the next site,
  discards the unfinished cell, records `INTERRUPTED` and exits 4. Resubmitting redoes that cell.
- **Crash or out of memory:** a crashed or out-of-memory cell is recorded as `failed`; the job continues.

**Exit codes:**

| Code | Meaning |
|---:|---|
| 0 | complete |
| 1 | error |
| 2 | refusal |
| 3 | partial |
| 4 | interrupted |

### Local verification (2026-10-07)

| What | Result |
|---|---|
| `tests/run_tests.py`, project venv | **139 passed, 0 failed, 0 blocked** |
| same, bare `python3` | 135 passed, 4 blocked (matplotlib, torch absent): exit 5, correctly not green |
| `../tests` (Phase 3.2) / `../../phase3/tests` | 36 passed / 54 passed |
| `jobs/cpu_tests.slurm` run as Slurm would on a CPU node (stand-in `srun`, `CUDA_VISIBLE_DEVICES=""`, a stand-in results root) | Sol 138 passed + 1 hardware-blocked (the A100 test); Phase 3.2 36; Phase 3 54; **overall exit 0**; **0 files** written into the results root |
| `submit.sh` against a stand-in `sbatch` | arrays `0,1,2,3` (dev); `0-18` on 1 GPU and `19,20` on 2 GPUs (held-out); `P33_ARRAY` respected; an empty GPU class refused |
| development re-analysis (§13) | 652 measurement files byte-identical; 17/19 CSVs byte-identical; only AP / P@k and power rows changed |

---

## 15. Cost and time — from the real development run

**Measured on Sol** (A100-SXM4-80GB, `dev-20261006a`):

| Model | Arm A, per row (2,556 rows) | Primary, per row (4,000 rows) | Time per model, both |
|---|---:|---:|---:|
| Qwen2.5-Coder 0.5B | 37 ms | 31 ms | ~3.6 min |
| Qwen2.5-Coder 1.5B | 48–51 ms | 39 ms | ~4.6 min |

The whole development run used about **17 minutes** of A100 time; the tasks ran
one after another.

**Held-out projection.** Per-row time is scaled by parameter count from the 1.5B
measurement, which is pessimistic for large models because they use the GPU more
efficiently. Each model is assumed to have about 7,500 Arm A rows (10 cells instead of 4;
exact after the unlock) and 4,000 primary rows. Treat every figure as ±2×.

| Model class | Per model (Arm A + primary) | Models | GPU-hours |
|---|---:|---:|---:|
| ≤ 1.5B | ~9 min | 8 | ~1.2 |
| 3B | ~18 min | 3 | ~0.9 |
| 7B | ~40 min | 2 | ~1.4 |
| 14B | ~1.4 h | 2 | ~2.7 |
| 32–33B | ~3.2 h | 4 | ~13 |
| 72B (2 GPUs) | ~7 h wall | 2 | ~28 |
| **all 21** | | | **~47** |

Arm B and H5 run on the 10 instruct models and roughly double that, mostly through
the 72B and 32/33B instruct models: **about 100 GPU-hours in all**. The time limits
in `submit.sh` cover these estimates with margin: 10 h for a 1-GPU held-out task,
24 h for a 2-GPU task.

**Wall time** depends on how many jobs the `public` QOS runs at once. At one at a time,
as in the development run, the held-out stage takes 2–4 days.
