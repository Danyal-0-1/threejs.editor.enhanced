# Reproduction — `smoke-20261023a`

> **Run** `smoke-20261023a` · **stage** SMOKE (development cell) · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

Config hash `58ed88ff927113336615c3f41e650ce48400019355ece4ddf79122faf3c392b9` — a resume under any other config is refused.

```bash
# from $P4_CODE_ROOT/phase3_2/sol, after `source sol.env && source env/activate.sh`
# scoring (GPU; on Sol through submit.sh, one array task per model)
python scripts/p33.py dev run --run smoke-20261023a --experiment arm_a
python scripts/p33.py dev run --run smoke-20261023a --experiment primary
# analysis (CPU; re-derives every table, plot and report from the saved measurements)
python scripts/p33.py merge    --run smoke-20261023a
python scripts/p33.py validate --run smoke-20261023a
python scripts/p33.py export   --run smoke-20261023a   # CSVs -> plots -> reports
```

Resume is idempotent: completed cells (marker + sha256 + row count) are skipped; failed, missing and corrupt cells are re-run.

Model pins: `/home/mesquite/Desktop/projects/Lab/threejs.editor/threejs.editor.enhanced/phase4/results/model_pins.json` (written by `p33 prefetch`). Environment lock: `phase3_2/sol/env/` (see `env/README.md`).
