# Reproduction — `smoke-20261006a`

> **Run** `smoke-20261006a` · **stage** SMOKE (development cell) · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

Config hash `6fde06710358bc63714c6d039403f45442f9a6fc5d9b90fa9c0ba4be3fa159bc` — a resume under any other config is refused.

```bash
# from $P33_CODE_ROOT/phase3_2/sol
python scripts/p33.py dev arm-a   --run smoke-20261006a
python scripts/p33.py dev primary --run smoke-20261006a
python scripts/p33.py merge    --run smoke-20261006a
python scripts/p33.py validate --run smoke-20261006a
python scripts/p33.py export   --run smoke-20261006a   # CSVs -> plots -> reports
```

Resume is idempotent: completed cells (marker + sha256 + row count) are skipped; failed, missing and corrupt cells are re-run.

Model pins: `/home/dkhorami/phase3-3_experiment_sol/results/model_pins.json` (written by `p33 prefetch`). Environment lock: `phase3_2/sol/env/` (see `env/README.md`).
