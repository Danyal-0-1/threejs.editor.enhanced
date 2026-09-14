#!/usr/bin/env bash
# Lane B driver. Waits for Lane A to release the GPU, then runs each Instruct
# model over all 4 languages x 2 conditions x 22 cases. Never stops after a
# failed model.
set -u
R="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$R/../../../.." && pwd)"
PY="$REPO/run/.venv/bin/python"
export PYTHONDONTWRITEBYTECODE=1
LOG="$R/logs/commands.log"

# Lane A completed before this driver was launched (see logs/lane_a.log).
# The earlier wait-loop was removed: `pgrep -f` also matches unrelated SHELL
# command lines that merely mention the pattern, which made it spin forever.
echo "=== $(date -u +%FT%TZ) starting Lane B" | tee -a "$LOG"

run() {
  local label="$1"; shift
  echo "=== $(date -u +%FT%TZ) $label" | tee -a "$LOG"
  echo "CMD: $*" >> "$LOG"
  "$@" 2>&1 | tee -a "$R/logs/lane_b.log"
  local rc=${PIPESTATUS[0]}
  echo "EXIT $rc  $label" | tee -a "$LOG"
  return 0
}

for M in Qwen/Qwen2.5-Coder-0.5B-Instruct Qwen/Qwen2.5-Coder-1.5B-Instruct Qwen/Qwen2.5-Coder-3B-Instruct; do
  SAFE="${M//\//__}"
  mkdir -p "$R/raw/$SAFE/lane_b"
  run "laneB $M fp16 cuda reps=3" "$PY" "$R/scripts/lane_b.py" --model "$M" \
      --out "$R/raw/$SAFE/lane_b/gen.jsonl" --precision fp16 --device cuda --reps 3
done

# 7B-Instruct: attempted under the IDENTICAL primary configuration (fp16/cuda).
# ~15.2 GB of weights against 16.76 GB of VRAM is tight; an OOM is recorded as
# an OOM outcome and is NOT retried at a lower precision.
M=Qwen/Qwen2.5-Coder-7B-Instruct; SAFE="${M//\//__}"
mkdir -p "$R/raw/$SAFE/lane_b"
run "laneB $M fp16 cuda reps=3 (sensitivity)" "$PY" "$R/scripts/lane_b.py" --model "$M" \
    --out "$R/raw/$SAFE/lane_b/gen.jsonl" --precision fp16 --device cuda --reps 3

echo "LANE B COMPLETE" | tee -a "$LOG"
