#!/bin/bash
# 6. CPU development analysis + power. Merge, validate, CSVs, plots, reports.
set -euo pipefail
# shellcheck disable=SC1091
source "${P4_SOL:?submit through submit.sh}/sol.env"
# shellcheck disable=SC1091
source "$P4_SOL/env/activate.sh"
cd "$P4_SOL"
echo "[$(date -Is)] $SLURM_JOB_NAME job=$SLURM_JOB_ID task=${SLURM_ARRAY_TASK_ID:-none} node=$SLURMD_NODENAME run=$RUN_ID"
srun "$P4_PY" ../run.py dev fertility --run "$RUN_ID"
srun "$P4_PY" ../run.py dev analyze --run "$RUN_ID"
srun "$P4_PY" ../run.py validate --run "$RUN_ID" || echo "INCOMPLETE -- see csv/run_completeness.csv"
