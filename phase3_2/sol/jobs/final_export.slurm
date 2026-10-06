#!/bin/bash
# 11. Final analysis/export: merge + validate + every CSV, plot and report.
set -euo pipefail
# shellcheck disable=SC1091
source "${P33_SOL:?submit through submit.sh}/sol.env"
# shellcheck disable=SC1091
source "$P33_SOL/env/activate.sh"
cd "$P33_SOL"
echo "[$(date -Is)] $SLURM_JOB_NAME job=$SLURM_JOB_ID task=${SLURM_ARRAY_TASK_ID:-none} node=$SLURMD_NODENAME run=$RUN_ID"
STAGE=$("$P33_PY" -c "import json;print(json.load(open('$P33_RESULTS_ROOT/$RUN_ID/manifests/run_config.json'))['config']['stage'])")
[ "$STAGE" = smoke ] && STAGE=dev      # a smoke run is development data; `smoke` has no analyze group
srun "$P33_PY" scripts/p33.py "$STAGE" fertility --run "$RUN_ID"
srun "$P33_PY" scripts/p33.py "$STAGE" analyze --run "$RUN_ID"
srun "$P33_PY" scripts/p33.py validate --run "$RUN_ID" || echo "PARTIAL run -- reports are labelled PARTIAL"
