#!/bin/bash
# 6. CPU development analysis + power. Merge, validate, CSVs, plots, reports.
set -euo pipefail
# shellcheck disable=SC1091
source "${P33_SOL:?submit through submit.sh}/sol.env"
# shellcheck disable=SC1091
source "$P33_SOL/env/activate.sh"
cd "$P33_SOL"
echo "[$(date -Is)] $SLURM_JOB_NAME job=$SLURM_JOB_ID task=${SLURM_ARRAY_TASK_ID:-none} node=$SLURMD_NODENAME run=$RUN_ID"
srun "$P33_PY" scripts/p33.py dev fertility --run "$RUN_ID"
srun "$P33_PY" scripts/p33.py dev analyze --run "$RUN_ID"
srun "$P33_PY" scripts/p33.py validate --run "$RUN_ID" || echo "INCOMPLETE -- see csv/run_completeness.csv"
