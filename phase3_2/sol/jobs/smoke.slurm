#!/bin/bash
#SBATCH --signal=USR1@120
# 3. A100 / CUDA / model smoke: ONE cached 0.5B model, ONE dev lexicon, ONE family.
set -euo pipefail
# shellcheck disable=SC1091
source "${P33_SOL:?submit through submit.sh}/sol.env"
# shellcheck disable=SC1091
source "$P33_SOL/env/activate.sh"
cd "$P33_SOL"
echo "[$(date -Is)] $SLURM_JOB_NAME job=$SLURM_JOB_ID task=${SLURM_ARRAY_TASK_ID:-none} node=$SLURMD_NODENAME run=$RUN_ID"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1   # scoring never touches the network
srun "$P33_PY" scripts/p33.py env-check
srun "$P33_PY" scripts/p33.py smoke --config configs/smoke.json --run "$RUN_ID"
