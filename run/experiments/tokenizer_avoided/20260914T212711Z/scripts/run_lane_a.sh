#!/usr/bin/env bash
# Lane A driver. Never stops after a failed model: each model is attempted and
# its exit code recorded, then the next one runs.
set -u
R="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$R/../../../.." && pwd)"
PY="$REPO/run/.venv/bin/python"
export PYTHONDONTWRITEBYTECODE=1
LOG="$R/logs/commands.log"

run() {  # run <label> <args...>
  local label="$1"; shift
  echo "=== $(date -u +%FT%TZ) $label" | tee -a "$LOG"
  echo "CMD: $*" >> "$LOG"
  "$@" 2>&1 | tee -a "$R/logs/lane_a.log"
  local rc=${PIPESTATUS[0]}
  echo "EXIT $rc  $label" | tee -a "$LOG"
  return 0
}

for M in Qwen/Qwen2.5-Coder-0.5B Qwen/Qwen2.5-Coder-1.5B Qwen/Qwen2.5-Coder-3B; do
  SAFE="${M//\//__}"
  mkdir -p "$R/raw/$SAFE/lane_a"
  run "laneA $M fp32 cuda" "$PY" "$R/scripts/lane_a.py" --model "$M" \
      --out "$R/raw/$SAFE/lane_a/nll.jsonl" --precision fp32 --device cuda
done

# 7B: attempted under the SAME predeclared FP32/CUDA configuration. FP32 weights
# are ~30.5 GB against 16.76 GB VRAM, so an OOM here is an expected, HONESTLY
# RECORDED outcome -- not a reason to silently change precision.
M=Qwen/Qwen2.5-Coder-7B; SAFE="${M//\//__}"
mkdir -p "$R/raw/$SAFE/lane_a"
run "laneA $M fp32 cuda (sensitivity, expected VRAM-bound)" "$PY" "$R/scripts/lane_a.py" \
    --model "$M" --out "$R/raw/$SAFE/lane_a/nll.jsonl" --precision fp32 --device cuda

# SEPARATELY LABELLED CONDITION: same FP32 numerics on CPU. NLL values are
# comparable to the GPU FP32 runs; TIMING IS NOT and is never pooled with them.
run "laneA $M fp32 cpu (separate condition)" "$PY" "$R/scripts/lane_a.py" \
    --model "$M" --out "$R/raw/$SAFE/lane_a/nll_cpu.jsonl" --precision fp32 --device cpu

echo "LANE A COMPLETE" | tee -a "$LOG"
