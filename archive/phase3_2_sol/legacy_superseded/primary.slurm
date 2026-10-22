#!/bin/bash
#SBATCH --job-name=p33-primary
#SBATCH --partition=general
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=80G
#SBATCH --time=08:00:00
#SBATCH --output=outputs/slurm-%j-primary.out
#SBATCH --error=outputs/slurm-%j-primary.err

# Extinction curves: the PRIMARY estimand. More expensive than Arm A because
# context grows with the shot ladder -- a 0.5B model OOMed at 32 shots on a
# 16 GB card. Budget memory by (sites x top rung), not by parameter count.

set -euo pipefail
module load mamba/latest
source activate phase3

export HF_HOME=${HF_HOME:-/scratch/$USER/hf}
export HF_HUB_OFFLINE=1
export PHASE3_DTYPE=bfloat16
export PHASE3_DEVICE=cuda
export TOKENIZERS_PARALLELISM=false

cd "$SLURM_SUBMIT_DIR"

python scripts/run_primary.py \
  --models Qwen/Qwen2.5-Coder-0.5B Qwen/Qwen2.5-Coder-1.5B \
  --lexicons d25s1 d50s1 \
  --families dom \
  --sites 400 \
  --json "outputs/primary_dev_${SLURM_JOB_ID}.json"

echo "done ${SLURM_JOB_ID}"
