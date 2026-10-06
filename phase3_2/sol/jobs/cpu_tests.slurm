#!/bin/bash
# 1. CPU / unit / fake-model tests. No GPU, no weights.
set -euo pipefail
# shellcheck disable=SC1091
source "${P33_SOL:?submit through submit.sh}/sol.env"
# shellcheck disable=SC1091
source "$P33_SOL/env/activate.sh"
cd "$P33_SOL"
echo "[$(date -Is)] $SLURM_JOB_NAME job=$SLURM_JOB_ID task=${SLURM_ARRAY_TASK_ID:-none} node=$SLURMD_NODENAME run=$RUN_ID"
export P33_FAKE=1
# Run ALL three suites even if one fails (set -e would stop at the first), then
# exit non-zero if any FAILED or was BLOCKED by a missing dependency. On this
# CPU node the A100 preflight test is BLOCKED for want of a GPU; --cpu-node
# lists it without failing the job (the smoke job exercises that path on a GPU).
rc=0
for suite in "tests/run_tests.py --cpu-node" "../tests/run_tests.py" "../../phase3/tests/run_tests.py"; do
  # shellcheck disable=SC2086
  if srun "$P33_PY" $suite; then r=0; else r=$?; fi
  echo "[$(date -Is)] suite '$suite' exit=$r"
  [ "$r" -ne 0 ] && rc=1
done
echo "cpu_tests: overall exit=$rc (0 = every suite passed; anything else = read the FAIL/BLOCKED lines above)"
exit "$rc"
