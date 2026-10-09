# Reproduction — `heldout-20261007a`

> **Run** `heldout-20261007a` · **stage** HELD-OUT · **status** COMPLETE
>
> Held-out evaluation under DEV_FREEZE; see criteria below. blk results are a WEAKER family test (deviation D1), never a held-out-grammar confirmation.

Config hash `d664de71837d9e9a078525b2472f678c79a68138314ac90a2c576a30d95f6a99` — a resume under any other config is refused.

```bash
# from $P33_CODE_ROOT/phase3_2/sol, after `source sol.env && source env/activate.sh`
# scoring (GPU; on Sol through submit.sh, one array task per model)
python scripts/p33.py heldout run --run heldout-20261007a --experiment arm_a
python scripts/p33.py heldout run --run heldout-20261007a --experiment primary
# analysis (CPU; re-derives every table, plot and report from the saved measurements)
python scripts/p33.py merge    --run heldout-20261007a
python scripts/p33.py validate --run heldout-20261007a
python scripts/p33.py export   --run heldout-20261007a   # CSVs -> plots -> reports
```

Resume is idempotent: completed cells (marker + sha256 + row count) are skipped; failed, missing and corrupt cells are re-run.

Model pins: `/home/dkhorami/phase3-3_experiment_sol/results/model_pins.json` (written by `p33 prefetch`). Environment lock: `phase3_2/sol/env/` (see `env/README.md`).
