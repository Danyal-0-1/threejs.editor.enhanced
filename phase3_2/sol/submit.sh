#!/bin/bash
# submit.sh — the ONLY way to submit a Phase 3.3 job.
#
#   bash submit.sh <job> <RUN_ID> [extra sbatch args...]
#
# Why a wrapper: Slurm opens --output/--error BEFORE the job body runs. If the
# log directory does not exist the job fails with no log at all. This creates
# results/<RUN_ID>/logs first, then calls sbatch with account / partition /
# QOS / GPU resources taken from sol.env -- never hard-coded in the job files.
#
# jobs: cpu_tests prefetch smoke dev_arm_a dev_primary dev_analyze dev_freeze
#       heldout_eval arm_b h5 final_export
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$HERE/sol.env"

JOB="${1:?usage: submit.sh <job> <RUN_ID> [sbatch args]}"
RUN_ID="${2:?usage: submit.sh <job> <RUN_ID> [sbatch args]}"
shift 2

LOG="$P33_RESULTS_ROOT/$RUN_ID/logs"
mkdir -p "$LOG"

GPU=(--gres="$P33_GRES" --constraint="$P33_CONSTRAINT")
n_models() {   # array size = models in the run's stored config
  "${P33_PY:-python3}" -c "import json,sys;print(len(json.load(open(sys.argv[1]))['config']['models'])-1)" \
    "$P33_RESULTS_ROOT/$RUN_ID/manifests/run_config.json" 2>/dev/null || echo 0
}
# Array task i scores model i of run_config.json. To resubmit only some models:
#   P33_ARRAY=2 bash submit.sh dev_arm_a <RUN_ID>        (or P33_ARRAY=1,3)
ARRAY="${P33_ARRAY:-0-$(n_models)}"

case "$JOB" in
  cpu_tests)    RES=(--cpus-per-task=4 --mem=16G --time=01:00:00) ;;
  prefetch)     RES=(--cpus-per-task=4 --mem=16G --time=06:00:00) ;;
  smoke)        RES=("${GPU[@]}" --cpus-per-task=8 --mem=64G --time=00:45:00) ;;
  dev_arm_a)    RES=("${GPU[@]}" --cpus-per-task=8 --mem=64G --time=04:00:00 --array="$ARRAY") ;;
  dev_primary)  RES=("${GPU[@]}" --cpus-per-task=8 --mem=80G --time=08:00:00 --array="$ARRAY") ;;
  dev_analyze)  RES=(--cpus-per-task=8 --mem=32G --time=02:00:00) ;;
  dev_freeze)   RES=(--cpus-per-task=2 --mem=8G --time=00:30:00) ;;
  heldout_eval) RES=("${GPU[@]}" --cpus-per-task=8 --mem=80G --time=10:00:00 --array="$ARRAY") ;;
  arm_b)        RES=("${GPU[@]}" --cpus-per-task=8 --mem=64G --time=08:00:00 --array="$ARRAY") ;;
  h5)           RES=("${GPU[@]}" --cpus-per-task=8 --mem=64G --time=06:00:00 --array="$ARRAY") ;;
  final_export) RES=(--cpus-per-task=8 --mem=32G --time=02:00:00) ;;
  *) echo "unknown job '$JOB'" >&2; exit 2 ;;
esac

set -x
sbatch --account="$P33_ACCOUNT" --partition="$P33_PARTITION" --qos="$P33_QOS" \
  "${RES[@]}" --job-name="p33-$JOB" \
  --output="$LOG/%x-%A_%a.out" --error="$LOG/%x-%A_%a.err" \
  --export=ALL,RUN_ID="$RUN_ID",P33_SOL="$HERE" \
  "$@" "$HERE/jobs/$JOB.slurm"
