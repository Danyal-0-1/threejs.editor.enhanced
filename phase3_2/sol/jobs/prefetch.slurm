#!/bin/bash
# 2. Model prefetch + verification. DOWNLOAD ONLY -- no model is instantiated.
#    Needs network: if Sol compute nodes are offline, run the same command on
#    the data-transfer node instead (see README). Set HF_TOKEN for gated models.
set -euo pipefail
# shellcheck disable=SC1091
source "${P33_SOL:?submit through submit.sh}/sol.env"
# shellcheck disable=SC1091
source "$P33_SOL/env/activate.sh"
cd "$P33_SOL"
echo "[$(date -Is)] $SLURM_JOB_NAME job=$SLURM_JOB_ID task=${SLURM_ARRAY_TASK_ID:-none} node=$SLURMD_NODENAME run=$RUN_ID"
# Default: exactly the models the shipped configs use (smoke + dev + held-out,
# 11 models, none above 3B). The `mid`/`large` tiers also hold 7B-32B models
# that no stage may score (MAX_SIZE_B = 3.0) -- do not prefetch them for this study.
# Overrides: P33_MODELS="id1 id2"  or  P33_TIER=small|mid|large|all
if [ -n "${P33_MODELS:-}" ]; then
  # shellcheck disable=SC2206
  SEL=(--models $P33_MODELS)
elif [ -n "${P33_TIER:-}" ]; then
  SEL=(--tier "$P33_TIER")
else
  SEL=(--config configs/smoke.json configs/dev.json configs/heldout.json)
fi
# a failed dry-run entry (e.g. a gated model without HF_TOKEN) must not stop the others
srun "$P33_PY" scripts/p33.py prefetch "${SEL[@]}" --dry-run || echo "dry-run reported problems (above); downloading the rest"
srun "$P33_PY" scripts/p33.py prefetch "${SEL[@]}" --checksums
