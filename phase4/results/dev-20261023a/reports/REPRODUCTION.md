# Reproduction — `dev-20261023a`

> **Run** `dev-20261023a` · **stage** DEVELOPMENT · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

Config hash `c786cd79962fc455eb8c08eec2714954c10be0d6f33eaa081597493f88edae77` — a resume under any other config is refused.

```bash
# from $P4_CODE_ROOT/phase3_2/sol, after `source sol.env && source env/activate.sh`
# scoring (GPU; on Sol through submit.sh, one array task per model)
python scripts/p33.py dev run --run dev-20261023a --experiment arm_a
python scripts/p33.py dev run --run dev-20261023a --experiment primary
# analysis (CPU; re-derives every table, plot and report from the saved measurements)
python scripts/p33.py merge    --run dev-20261023a
python scripts/p33.py validate --run dev-20261023a
python scripts/p33.py export   --run dev-20261023a   # CSVs -> plots -> reports
```

Resume is idempotent: completed cells (marker + sha256 + row count) are skipped; failed, missing and corrupt cells are re-run.

Model pins: `/home/mesquite/Desktop/projects/Lab/threejs.editor/threejs.editor.enhanced/phase4/results/model_pins.json` (written by `p33 prefetch`). Environment lock: `phase3_2/sol/env/` (see `env/README.md`).
