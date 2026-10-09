# 03 — Code and pipeline: how the held-out run was executed

> **Scope.** The development pipeline (plan → score → shard → merge → export) is described in
> [`../sol_experiment_explained/03_code_and_pipeline.md`](../sol_experiment_explained/03_code_and_pipeline.md).
> This file covers what happened **from the pull on Sol to the results on your laptop**.
>
> **Format.** Each stage is INPUT → TRANSFORMATION → OUTPUT → VALIDATION, with real dumps.
>
> **Times** are Sol time (MST, UTC−7).

```
 2026-10-07                                                    2026-10-08 … 10-09
 push ─► pull ─► CPU tests ─► D9 re-analysis ─► prefetch ─► FREEZE ─► init+UNLOCK ─► chain ─► export ─► postprocess ─► copy home
         78b2bcd  64939805     r1 on Sol         64939806    64942745  heldout-...   7 jobs   64943136   65042534      rsync, 72 s
```

---

## 0. Bring the code to Sol

| | |
|---|---|
| **Input** | local commit `78b2bcd` on branch `sol-d9-d10`, pushed to `origin` (your fork) |
| **Transformation** | on Sol: `git fetch origin sol-d9-d10 && git checkout -b sol-d9-d10 --track origin/sol-d9-d10` |
| **Output** | Sol's `~/phase3-3_experiment_sol/repo` on `78b2bcd`; regenerated `__pycache__` files and the untracked `requirements.lock.sol.txt` preserved |
| **Validation** | `git log --oneline -1` → `78b2bcd`; only `.pyc` files and the lock file differ from the commit |

**The SSH session.** It ran over one persistent multiplexed connection (one Duo approval).
Every later poll used `ControlMaster=no`, and pollers *refused to reconnect* when the
connection dropped, so no surprise Duo pushes were sent.

---

## 1. CPU tests on Sol (job 64939805)

| | |
|---|---|
| **Input** | `submit.sh cpu_tests setup-20261007b` |
| **Transformation** | the three test suites under `P33_FAKE=1`, on a CPU node |
| **Output** | `results/setup-20261007b/logs/p33-cpu_tests-*.out` |
| **Validation** | `138 passed, 0 failed, 1 blocked` (the A100 test, no GPU); `36 passed`; `54 passed`; `overall exit=0`; the results root untouched (the runner fix) |

---

## 2. The D9 re-analysis of the development run, on Sol

| | |
|---|---|
| **Input** | `results/dev-20261006a` (saved GPU measurements) |
| **Transformation** | `analysis_revision.py snapshot` → `p33.py validate` → `srun … p33.py export` → `analysis_revision.py record` |
| **Output** | `analysis_revisions/r1-2026-10-07-metric-corrections/` on Sol (copied locally into `sol_record/`) |
| **Validation** | `record: inputs byte-identical (652 files); 2 CSV(s) changed; checks ALL PASSED`; digest `3c3e772c66ecf51e`, the same as the local record. Sol vs local CSVs: 18/19 identical, one 6e-18 difference |

---

## 3. Download the ten large checkpoints (job 64939806)

| | |
|---|---|
| **Input** | `P33_MODELS="<10 ids>" submit.sh prefetch setup-20261007b`. The gated Llama pair was left out because it was already pinned |
| **Transformation** | dry run (sizes, revisions) → `snapshot_download` at exact revisions → sha256 of every file |
| **Output** | 641 GB under `/scratch/dkhorami/hf/hub`; `results/model_pins.json` with **21 pins** |
| **Validation** | `failed {}`, `pairing_problems []`, `verified_checksums True` for all 10; 36 min |

Real dry-run dump (GB = GiB):

```
Qwen/Qwen2.5-Coder-7B            0396a76181e1   14.2 GB      Qwen/Qwen2.5-Coder-32B-Instruct  381fc969f78e   61.0 GB
Qwen/Qwen2.5-Coder-7B-Instruct   c03e6d358207   14.2 GB      deepseek-ai/deepseek-coder-33b-base  45c85cadf372 62.1 GB
Qwen/Qwen2.5-Coder-14B           f2ad5164aade   27.5 GB      deepseek-ai/deepseek-coder-33b-instruct 61dc97b922b1 62.1 GB
Qwen/Qwen2.5-Coder-14B-Instruct  aedcc2d42b62   27.5 GB      Qwen/Qwen2.5-72B                 efba10c8e54e  135.4 GB
Qwen/Qwen2.5-Coder-32B           2e12b5f7bc87   61.0 GB      Qwen/Qwen2.5-72B-Instruct        495f39366efe  135.4 GB
```

---

## 4. Freeze (job 64942745)

| | |
|---|---|
| **Input** | the complete dev run; the 21 pins; the source at `78b2bcd` |
| **Transformation** | `validate`, which is fatal if it fails → [`freeze.build_payload`](../src/p33/freeze.py), which fits Platt calibration and the Youden threshold per development pair, and hashes prompts, materials, sources and pins → `splits.write_freeze` (written once, mode 444, `.sha256` sidecar) |
| **Output** | `results/dev-20261006a/DEV_FREEZE.json` (58,462 bytes) |
| **Validation** | `load_freeze` verified; 44 source hashes; `frozen_drift == []`; 21 model pins |

Real verification dump:

```
freeze verified; dev_run_id dev-20261006a | utc 2026-10-08T06:04:47+00:00
git 78b2bcdbf2c3 dirty True          ← only tracked __pycache__ files and the untracked Sol lock
source hashes: 44 | drift now: []
model pins: 21
calibration: {'…0.5B|…0.5B-Instruct': [-0.2984, 0.9014], '…1.5B|…1.5B-Instruct': [-0.2982, 2.1419]}
thresholds:  {'…0.5B|…0.5B-Instruct': 0.3643, '…1.5B|…1.5B-Instruct': 0.3519}
```

**Note.** The calibration covers only the two development pairs. That is the root of the
labelling gap in [08](08_issues_and_superseded_numbers.md).

---

## 5. Held-out init and unlock

| | |
|---|---|
| **Input** | `configs/heldout.json` (21 models); the freeze path; the typed phrase |
| **Transformation** | `p33.py heldout init --config … --run heldout-20261007a --freeze …`, then `p33.py heldout unlock --run … --confirm "I have finished the development analysis and will not change it"` |
| **Output** | `results/heldout-20261007a/` (config `d664de71837d`), `HELDOUT_UNLOCK.json` (mode 444), `UNLOCK_NOTE.md` (records that the phrase was entered at the investigator's direction) |
| **Validation** | `write_unlock` re-checked the phrase, the freeze integrity and `frozen_drift == []` |

---

## 6. The chain: one job at a time ([`submit_chain.sh`](../submit_chain.sh))

| order | job | array | depends on | why |
|---|---|---|---|---|
| A | 64943130 `heldout_eval` | 0–18 `%1` | — | Arm A + extinction, one model at a time |
| B | 64943131 `heldout_eval_2gpu` | 19, 20 | `afterany:A` | the 72B pair, 2 GPUs |
| C | 64943132 `arm_b` | instruct indices `%1` | `afterany:B` | base-model tasks would be no-ops |
| D | 64943133 `arm_b_2gpu` | 20 | `afterany:C` | |
| E | 64943134 `h5` | instruct indices `%1` | `afterany:D`, **`afterok:A:B`** | H5 stores arms derived from Arm A, which must be complete |
| F | 64943135 `h5_2gpu` | 20 | `afterany:E`, `afterok:A:B` | |
| G | 64943136 `final_export` | — | `afterany:F` | |

**Every GPU task runs [`preflight`](../src/p33/preflight.py) on its own models first.** Here
is the real dump for task 19, the 72B on two GPUs:

```
[PASS] gpu_count              2 visible, 2 needed by ['Qwen/Qwen2.5-72B']
[PASS] gpu_memory:Qwen/Qwen2.5-72B ~152 GiB needed, 158 GiB free on 2 GPU(s)
[PASS] model:Qwen/Qwen2.5-72B local efba10c8e54e pinned efba10c8e54e
[PASS] materials              materials identical to the run's first job
[PASS] split_permission       210 cells allowed for stage heldout: ['HELDOUT', 'HELDOUT-WEAK-FAMILY', 'HELDOUT-WEAKENED']
preflight OK
```

**Sharded loading worked on its first real run.** `nvidia-smi` during task 19:

```
0, NVIDIA A100-SXM4-80GB, 68399 MiB, 81920 MiB, 60 %
1, NVIDIA A100-SXM4-80GB, 76761 MiB, 81920 MiB, 47 %     ← last GPU also holds the fp32 output head
```

**Task timings** (wall clock; `—` means not applicable):

| idx | model | Arm A + extinction | Arm B | H5 |
|---:|---|---:|---:|---:|
| 0 | Qwen2.5-Coder-0.5B | 0:09:00 | — | — |
| 1 | … 0.5B-Instruct | 0:08:33 | 0:43:06 | 0:17:12 |
| 2 | Qwen2.5-Coder-1.5B | 0:10:11 | — | — |
| 3 | … 1.5B-Instruct | 0:10:16 | 0:50:52 | 0:19:01 |
| 4 | Qwen2.5-Coder-3B | 0:13:06 | — | — |
| 5 | … 3B-Instruct | 0:12:39 | 0:55:36 | 0:22:41 |
| 6 | DeepSeek-Coder-1.3B | 0:10:19 | — | — |
| 7 | … 1.3B-Instruct | 0:10:17 | 0:42:29 | 0:18:39 |
| 8 | Llama-3.2-1B | 0:06:52 | — | — |
| 9 | … 1B-Instruct | 0:06:53 | 0:14:52 | 0:14:04 |
| 10 | StarCoder2-3B | 0:09:38 | — | — |
| 11 | Qwen2.5-Coder-7B | 0:16:14 | — | — |
| 12 | … 7B-Instruct | 0:16:38 | 0:24:28 | 0:28:19 |
| 13 | Qwen2.5-Coder-14B | 0:29:14 | — | — |
| 14 | … 14B-Instruct | 0:29:19 | 0:30:14 | 0:44:59 |
| 15 | Qwen2.5-Coder-32B | 0:53:29 | — | — |
| 16 | … 32B-Instruct | 0:53:19 | 1:40:39 | 1:17:05 |
| 17 | DeepSeek-Coder-33B | 1:11:15 | — | — |
| 18 | … 33B-Instruct | 1:11:08 | 2:19:51 | 1:40:32 |
| 19 | Qwen2.5-72B (2 GPUs) | 1:47:46 | — | — |
| 20 | … 72B-Instruct (2 GPUs) | 1:48:25 | 3:27:22 | 2:33:11 |

**GPU-hours: 40.8 in total.**

- evaluation: 7.47 + 2 × 3.60;
- Arm B: 8.37 + 2 × 3.46;
- H5: 5.71 + 2 × 2.55.

The README projected about 100. The large models were faster than the conservative
estimate.

**Arm B is slower for small models.** They ramble to the 192-token cap, while large models
finish their program and stop.

---

## 7. Each stage's own transformation

| stage | input | transformation (code) | output rows |
|---|---|---|---|
| Arm A | the plan's sites × 3 conditions | [`pipeline.score_arm_a_cell`](../src/p33/pipeline.py#L275) → `margins.score_pair_detailed` | 190,890 |
| extinction | 400 sites × ladder + paraphrases | [`pipeline.score_primary_cell`](../src/p33/pipeline.py#L300); leak-free `demos.for_site` | 84,000 |
| Arm B | templates × lexicons, instruct models | [`armb.score_armb_cell`](../src/p33/armb.py#L238): greedy, ≤ 192 tokens → `extract_program` → `evaluate` (5 buckets) → `observe` (reach/outcome per site) | 7,800 generations |
| H5 | merged Arm A (base-model risk) | [`h5.prepare`](../src/p33/h5.py#L125) (arms + IR proofs) → [`score_h5_cell`](../src/p33/h5.py#L200) under each repaired lexicon | 212,100 |

**Validation, all of it built in.**

- Each cell writes an atomic shard and a sha256 marker.
- A demonstration leak raises an error.
- A repair whose IR proof fails is rejected before anything is scored. All 35 proofs passed,
  each over 284 programs.

---

## 8. The final export (job 64943136): a Slurm incident, then success

| | |
|---|---|
| **Input** | every shard of the run |
| **Transformation** | `heldout fertility` → `heldout analyze` (merge 4 experiments → [`export.export_all`](../src/p33/export.py#L102) → plots → reports) → `validate` |
| **Output** | 19 CSVs, 24 figure files, 10 reports in `results/heldout-20261007a/` |
| **Validation** | `VALID: every expected cell is done and verified` |

**The incident.**

- The first start (10:16, node sc034) was cancelled after 2 minutes, and the job was requeued
  and held. The reason was `user_env_retrieval_failed_requeued_held`: Slurm could not load the
  job's login environment.
- No log file was created, so the script never ran.
- `scontrol release 64943136` → it ran on sc099 from 10:23 for 56 min.

Real dump of the end of the export:

```
merge arm_a    COMPLETE  rows=190890 done=3402/3402 missing=0 failed=0 corrupt=0 dup_dropped=0
merge primary  COMPLETE  rows= 84000 done=840/840 missing=0 failed=0 corrupt=0 dup_dropped=0
merge armb     COMPLETE  rows=  7800 done=200/200 missing=0 failed=0 corrupt=0 dup_dropped=0
merge h5       COMPLETE  rows=212100 done=3780/3780 missing=0 failed=0 corrupt=0 dup_dropped=0
VALID: every expected cell is done and verified
```

---

## 9. Post-processing (job 65042534; 56 s; dependency `afterany:64943136`)

| | |
|---|---|
| **Input** | the export's CSVs; `scale_analysis.py` (sha `9d0a30f5…`, from `origin/sol-d9-d10`); the summary and exploratory scripts |
| **Transformation** | D11 slopes → `analysis_addenda/d11_scale/`; summary → `analysis_addenda/summary/HELDOUT_SUMMARY.txt`; exploratory cuts → `analysis_addenda/exploratory/` |
| **Output** | three folders; **nothing written inside** `csv/`, `plots/` or `reports/` |
| **Validation** | D11 identical to the preview computed before the export (same inputs, same code) |

---

## 10. Results to your laptop

| | |
|---|---|
| **Input** | Sol: `results/heldout-20261007a`, `model_pins.json`, the dev run's new files (freeze, freeze logs, Sol's revision record) |
| **Transformation** | `rsync -az` over the existing SSH connection, 72 s. For the dev run, `--ignore-existing`, so the local revision record is kept, and Sol's record goes into `analysis_revisions/r1…/sol_record/` |
| **Output** | `phase3_3/sol_results/heldout-20261007a/`: 1.6 GB, 16,710 files |
| **Validation** | sha256 identical on Sol and locally: `merged/arm_a.jsonl` 4ef9f28f…, `merged/h5.jsonl` 6bcf7583…, `csv/h4_metrics_baselines_calibration.csv` 5c3b0c8c…, `reports/HYPOTHESIS_RESULTS.md` b33708e0… |

**In git since 2026-10-09.** A second file-by-file checksum comparison with Sol found the
held-out run identical. The dev run differed in 27 exported files, where Sol's later export
now replaces the laptop's ([`SOL_SYNC_2026-10-09.md`](../../../phase3_3/sol_results/dev-20261006a/SOL_SYNC_2026-10-09.md)).
Both runs, Sol's setup and smoke runs, its post-processing scripts and its environment lock
(`env/requirements.lock.sol.txt`) are committed. The four files over 100 MB are committed
gzipped ([`phase3_3/sol_results/README.md`](../../../phase3_3/sol_results/README.md)).

**Sol's checkout was left on `78b2bcd`.** A `git pull` there refused to overwrite a
regenerated `.pyc` that a later commit also contains, and Git changed nothing. This is
harmless: every newer file is on GitHub and on your laptop.

---

## 11. Reproducing any number

**Locally,** every number can be recomputed from the exported CSVs. The pipeline's
*held-out* commands refuse to run locally, and that is by design:

```bash
cd phase3_2/sol
export P33_RESULTS_ROOT=$PWD/../../phase3_3/sol_results
PY=../../run/.venv/bin/python
$PY scripts/scale_analysis.py --run heldout-20261007a      # D11 from the CSVs: works locally
$PY scripts/paper_figures.py --run heldout-20261007a       # paper figures and tables: works locally (§12)
$PY scripts/exploratory_checks.py --run heldout-20261007a  # post hoc checks for 09 §3: works locally
$PY scripts/p33.py --pins $P33_RESULTS_ROOT/model_pins.json status --run heldout-20261007a
#  -> SplitViolation: unlock refers to an invalid freeze: no DEV_FREEZE at /home/dkhorami/…
```

**Why it refuses.** `HELDOUT_UNLOCK.json` binds the unlock to the freeze at its **Sol** path,
and [`load_unlock`](../src/p33/splits.py#L307) re-verifies that freeze on every held-out
access. A copy elsewhere is not "the" freeze.

**On Sol,** `status`, `validate` and `heldout analyze` work as long as the source still
matches the freeze. It does at `78b2bcd`, and at any later commit that changes only
non-source files.

---

## 12. Paper figures (local, CPU, 2026-10-09)

| | |
|---|---|
| **Input** | 10 of the export's CSVs, `analysis_addenda/d11_scale/scale_analysis.csv`, and the development freeze `dev-20261006a/DEV_FREEZE.json`, accepted only if its sha256 equals the one in `HELDOUT_UNLOCK.json` |
| **Transformation** | [`scripts/paper_figures.py`](../scripts/paper_figures.py), about 15 s. It recomputes the per-template counts, draws the template bootstrap exactly as the D11 script does (same seeds and streams), draws the figures and writes the tables. It imports the frozen `h4.auroc` and `kstar.kaplan_meier` instead of re-implementing them |
| **Output** | `analysis_addenda/paper_figures/`: 10 figures (PDF, SVG, PNG), `ALL_FIGURES.pdf` (all ten, for review), 16 tables (CSV + Markdown), `CAPTIONS.md` and `PROVENANCE.md`. **Nothing written inside** `csv/`, `plots/` or `reports/` |
| **Validation** | 8 checks against the frozen export, all passed; the script refuses on any mismatch (listed below). 4 tests in [`tests/test_paper_figures.py`](../tests/test_paper_figures.py); the suite has 147 tests, all passing |

**The eight checks** (from `PROVENANCE.md`):

1. the development freeze matches the unlock (sha256 `b319c3fc…`);
2. the per-lexicon mean rule effect equals the export in all 420 model × grammar × lexicon ×
   control cells;
3. site counts and reversion rates with the table equal the export in all 840 model ×
   grammar × lexicon × role cells;
4. the AUROC of the risk score and of the role-level and length baselines equals the export
   in all 20 pair × grammar groups;
5. the 36 Qwen2.5-Coder ladder values and their 95% intervals equal the D11 output exactly;
6. the Kaplan–Meier medians, recomputed from the site rows, equal the export in all 42
   model × grammar groups;
7. the Arm B site, reach, reversion, correct-program and parse-failure counts equal the
   frozen hurdle table;
8. `calibrated_p` equals the frozen Platt fit for the two development pairs.

**Why check 5 can be exact.** The D11 script seeds `random.Random(f"20261002/{family}/{outcome}/{kind}")`
and draws 80 templates with replacement, 2,000 times. `paper_figures.draws` makes the same
calls in the same order, stores the draws as a 2,000 × 80 matrix of template counts, and
takes the same order statistics for the interval. The two computations are therefore one
computation done twice, and any difference would be a bug.

**Why the freeze check works locally when `status` does not.** `load_unlock` binds the
unlock to the freeze's **Sol path** (§11). The figure script only reads, so it binds to the
freeze's **content**: the sha256 recorded at unlock time. A copy with the same bytes is accepted;
any other file is refused.
