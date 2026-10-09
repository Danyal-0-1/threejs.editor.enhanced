# Reproduction — `dev-20261006a`

> **Run** `dev-20261006a` · **stage** DEVELOPMENT · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

Config hash `80a2d30e93d3b8aa3e7f2a398d9354601530ccb9093bf23bc04c4de28658a49b` — a resume under any other config is refused.

```bash
# from $P33_CODE_ROOT/phase3_2/sol, after `source sol.env && source env/activate.sh`
# scoring (GPU; on Sol through submit.sh, one array task per model)
python scripts/p33.py dev run --run dev-20261006a --experiment arm_a
python scripts/p33.py dev run --run dev-20261006a --experiment primary
# analysis (CPU; re-derives every table, plot and report from the saved measurements)
python scripts/p33.py merge    --run dev-20261006a
python scripts/p33.py validate --run dev-20261006a
python scripts/p33.py export   --run dev-20261006a   # CSVs -> plots -> reports
```

Resume is idempotent: completed cells (marker + sha256 + row count) are skipped; failed, missing and corrupt cells are re-run.

Model pins: `/home/dkhorami/phase3-3_experiment_sol/results/model_pins.json` (written by `p33 prefetch`). Environment lock: `phase3_2/sol/env/` (see `env/README.md`).
