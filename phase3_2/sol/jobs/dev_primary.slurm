#!/bin/bash
#SBATCH --signal=USR1@300
# 5. Development primary: extinction ladder (leakage-free) + paraphrases.
set -euo pipefail
# shellcheck disable=SC1091
source "${P33_SOL:?submit through submit.sh}/sol.env"
# shellcheck disable=SC1091
source "$P33_SOL/env/activate.sh"
cd "$P33_SOL"
echo "[$(date -Is)] $SLURM_JOB_NAME job=$SLURM_JOB_ID task=${SLURM_ARRAY_TASK_ID:-none} node=$SLURMD_NODENAME run=$RUN_ID"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1   # scoring never touches the network
srun "$P33_PY" scripts/p33.py dev preflight --run "$RUN_ID"
srun "$P33_PY" scripts/p33.py dev run --run "$RUN_ID" --experiment primary
