#!/bin/bash
# 11. Final analysis/export: merge + validate + every CSV, plot and report.
set -euo pipefail
# shellcheck disable=SC1091
source "${P4_SOL:?submit through submit.sh}/sol.env"
# shellcheck disable=SC1091
source "$P4_SOL/env/activate.sh"
cd "$P4_SOL"
echo "[$(date -Is)] $SLURM_JOB_NAME job=$SLURM_JOB_ID task=${SLURM_ARRAY_TASK_ID:-none} node=$SLURMD_NODENAME run=$RUN_ID"
STAGE=$("$P4_PY" -c "import json;print(json.load(open('$P4_RESULTS_ROOT/$RUN_ID/manifests/run_config.json'))['config']['stage'])")
[ "$STAGE" = smoke ] && STAGE=dev      # a smoke run is development data; `smoke` has no analyze group
srun "$P4_PY" ../run.py "$STAGE" fertility --run "$RUN_ID"
srun "$P4_PY" ../run.py "$STAGE" analyze --run "$RUN_ID"
srun "$P4_PY" ../run.py validate --run "$RUN_ID" || echo "PARTIAL run -- reports are labelled PARTIAL"
