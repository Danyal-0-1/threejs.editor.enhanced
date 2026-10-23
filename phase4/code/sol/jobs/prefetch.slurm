#!/bin/bash
# 2. Model prefetch + verification. DOWNLOAD ONLY -- no model is instantiated.
#    Needs network: if Sol compute nodes are offline, run the same command on
#    the data-transfer node instead (see README). Set HF_TOKEN for gated models.
set -euo pipefail
# shellcheck disable=SC1091
source "${P4_SOL:?submit through submit.sh}/sol.env"
# shellcheck disable=SC1091
source "$P4_SOL/env/activate.sh"
cd "$P4_SOL"
echo "[$(date -Is)] $SLURM_JOB_NAME job=$SLURM_JOB_ID task=${SLURM_ARRAY_TASK_ID:-none} node=$SLURMD_NODENAME run=$RUN_ID"
# Default: exactly the models the shipped configs use (smoke + dev + held-out:
# 21 models since deviation D10, up to the 72B pair; about 0.7 TB in all).
# Already-pinned models keep their revision but are re-planned against the Hub,
# so a gated model needs HF_TOKEN even when it is already downloaded; to fetch
# only some models, list them.
# Overrides: P4_MODELS="id1 id2"  or  P4_TIER=small|mid|large|all
if [ -n "${P4_MODELS:-}" ]; then
  # shellcheck disable=SC2206
  SEL=(--models $P4_MODELS)
elif [ -n "${P4_TIER:-}" ]; then
  SEL=(--tier "$P4_TIER")
else
  SEL=(--config ../configs/smoke.json ../configs/phase3_3/dev.json ../configs/phase3_3/heldout.json)
fi
# a failed dry-run entry (e.g. a gated model without HF_TOKEN) must not stop the others
srun "$P4_PY" ../run.py prefetch "${SEL[@]}" --dry-run || echo "dry-run reported problems (above); downloading the rest"
srun "$P4_PY" ../run.py prefetch "${SEL[@]}" --checksums
