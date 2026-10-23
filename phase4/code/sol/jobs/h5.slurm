#!/bin/bash
#SBATCH --signal=USR1@300
# 10. H5 repair: needs merged Arm A in the same run (base-model risk chooses arms).
set -euo pipefail
# shellcheck disable=SC1091
source "${P4_SOL:?submit through submit.sh}/sol.env"
# shellcheck disable=SC1091
source "$P4_SOL/env/activate.sh"
cd "$P4_SOL"
echo "[$(date -Is)] $SLURM_JOB_NAME job=$SLURM_JOB_ID task=${SLURM_ARRAY_TASK_ID:-none} node=$SLURMD_NODENAME run=$RUN_ID"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1   # scoring never touches the network
STAGE=$("$P4_PY" -c "import json;print(json.load(open('$P4_RESULTS_ROOT/$RUN_ID/manifests/run_config.json'))['config']['stage'])")
[ "$STAGE" = smoke ] && STAGE=dev      # a smoke run is development data; `smoke` has no run group
srun "$P4_PY" ../run.py "$STAGE" preflight --run "$RUN_ID"
srun "$P4_PY" ../run.py merge --run "$RUN_ID" --experiment arm_a
srun "$P4_PY" ../run.py "$STAGE" run --run "$RUN_ID" --experiment h5
