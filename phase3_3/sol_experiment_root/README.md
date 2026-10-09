# Files from Sol's experiment root

These files were copied on 2026-10-09 from `~/phase3-3_experiment_sol/` on ASU Sol. They sit
outside the repository and the results folder there.

| folder | what |
|---|---|
| `postprocess/` | the post-processing job that ran after the held-out export (job 65042534): `run_postprocess.sh`, the D11 `scale_analysis.py` (identical to `phase3_2/sol/scripts/scale_analysis.py`, sha256 `9d0a30f5…`), `summarise_heldout.py` (wrote `analysis_addenda/summary/HELDOUT_SUMMARY.txt`) and `explore_density.py` (wrote `analysis_addenda/exploratory/adaptation_by_role_density.txt`; now reproduced by `phase3_2/sol/scripts/exploratory_checks.py`) |
| `smoke/` | the first A100 smoke-test job logs, 2026-10-05 |

**Not copied, on purpose:**

- `env/`, the Python environment. Its lock file is in git as
  `phase3_2/sol/env/requirements.lock.sol.txt`.
- `repo/` and the older `repo.*` copies. The code is in git.
- `results/_quarantine/`, a fake run made by an old test runner.
- the Hugging Face cache on `/scratch`, which holds model weights.
