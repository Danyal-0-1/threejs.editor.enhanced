#!/bin/bash
#SBATCH --job-name=p33-arm-a
#SBATCH --partition=general
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=outputs/slurm-%j-arm-a.out
#SBATCH --error=outputs/slurm-%j-arm-a.err

# Arm A: forward-only margins. Cheap; do not ration it.
# PREREGISTRATION.md holds out all of blk, all of d75, seed s3 and >1.5B.
# Development cells only unless the dev analysis is finished.

set -euo pipefail
module load mamba/latest
source activate phase3

export HF_HOME=${HF_HOME:-/scratch/$USER/hf}
export HF_HUB_OFFLINE=1          # weights are pre-staged; fail loudly if not
export PHASE3_DTYPE=bfloat16     # A100 native; RECORDED in every result file
export PHASE3_DEVICE=cuda
export TOKENIZERS_PARALLELISM=false

cd "$SLURM_SUBMIT_DIR"

python scripts/run_arm_a.py \
  --models Qwen/Qwen2.5-Coder-0.5B Qwen/Qwen2.5-Coder-0.5B-Instruct \
           Qwen/Qwen2.5-Coder-1.5B Qwen/Qwen2.5-Coder-1.5B-Instruct \
  --lexicons d25s1 d25s2 d50s1 d50s2 \
  --families dom \
  --limit 0 \
  --json "outputs/arm_a_dev_${SLURM_JOB_ID}.json"

echo "done ${SLURM_JOB_ID}"
