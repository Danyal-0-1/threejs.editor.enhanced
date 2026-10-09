# Phase 3.3 results from ASU Sol

This folder mirrors Sol's results root, `~/phase3-3_experiment_sol/results/`, as checked
file by file with checksums on 2026-10-09.

| folder | what | status |
|---|---|---|
| `dev-20261006a/` | the development run (4 models, `dom`), its D9 re-analysis records and the freeze `DEV_FREEZE.json` | identical to Sol, plus the laptop's own revision record; see `SOL_SYNC_2026-10-09.md` |
| `heldout-20261007a/` | the held-out run: 21 models, every cell COMPLETE, `validate` VALID | identical to Sol, plus the laptop-made `analysis_addenda/paper_figures/` and `analysis_addenda/exploratory/` |
| `setup-20261006a/`, `setup-20261007a/`, `setup-20261007b/` | logs of the CPU-test and model-download (prefetch) jobs | copied from Sol |
| `smoke-20261006a/` | the first end-to-end GPU smoke run | copied from Sol |
| `model_pins.json` | the exact Hugging Face revision of every checkpoint | identical to Sol |
| `restore_large_files.sh` | restores the files stored gzipped (below) | |

**Not copied from Sol, on purpose:**

- `_quarantine/`: a fake run written by an old test runner. It is not real data
  (`heldout_results_explained/08` §2).
- the Python environment, the old repository copies, and the Hugging Face model cache on
  `/scratch`. Weights and tokens never go into git.

## Files stored gzipped

GitHub refuses files over 100 MB. Four files in `heldout-20261007a/` are therefore committed
as `.gz` (gzip -9 -n), and their originals are listed in that run's `.gitignore`:

| file | original | gzipped |
|---|---:|---:|
| `csv/arm_a_long.csv` | 106 MB | 8.2 MB |
| `merged/arm_a.jsonl` | 253 MB | 14.9 MB |
| `merged/h5.jsonl` | 275 MB | 14.4 MB |
| `merged/primary.jsonl` | 120 MB | 6.2 MB |

**After cloning, restore them** (this checks every byte against `LARGE_FILES.sha256`):

```bash
bash phase3_3/sol_results/restore_large_files.sh heldout-20261007a
```

The analysis scripts (`phase3_2/sol/scripts/paper_figures.py`, `exploratory_checks.py`,
`scale_analysis.py`) read the restored originals.

## Where the scripts that ran on Sol are

- **Pipeline code:** the frozen commit `78b2bcd`.
- **Post-processing scripts:** they produced `heldout-20261007a/analysis_addenda/summary/` and
  `exploratory/adaptation_by_role_density.txt`. They are in `../sol_experiment_root/postprocess/`.
- **Sol's Python environment lock:** `phase3_2/sol/env/requirements.lock.sol.txt`.
