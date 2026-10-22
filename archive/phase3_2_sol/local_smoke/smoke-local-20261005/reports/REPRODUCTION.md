# Reproduction — `smoke-local-20261005`

> **Run** `smoke-local-20261005` · **stage** SMOKE (development cell) · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

Config hash `190fbc72fc747e109582e4fd29ad6a4c5b6241dd267667fd2a08ef4e565c65bb` — a resume under any other config is refused.

```bash
# from $P33_CODE_ROOT/phase3_2/sol
python scripts/p33.py dev arm-a   --run smoke-local-20261005
python scripts/p33.py dev primary --run smoke-local-20261005
python scripts/p33.py merge    --run smoke-local-20261005
python scripts/p33.py validate --run smoke-local-20261005
python scripts/p33.py export   --run smoke-local-20261005   # CSVs -> plots -> reports
```

Resume is idempotent: completed cells (marker + sha256 + row count) are skipped; failed, missing and corrupt cells are re-run.

Model pins: `/home/mesquite/Desktop/projects/Lab/threejs.editor/threejs.editor.enhanced/phase3_2/sol/local_smoke/model_pins.json` (written by `p33 prefetch`). Environment lock: `phase3_2/sol/env/` (see `env/README.md`).
