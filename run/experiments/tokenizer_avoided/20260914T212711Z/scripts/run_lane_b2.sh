#!/usr/bin/env bash
# Lane B driver, part 2 (resumes part 1 via the checkpoint).
#
# PROTOCOL DEVIATION (2026-09-14, recorded in STUDY_PLAN.md "Protocol deviations"):
# reps=3 is kept for 0.5B-Instruct and 1.5B-Instruct; 3B-Instruct and
# 7B-Instruct run with reps=1. Greedy decoding was VERIFIED deterministic (0 of
# 73 checked rows differed across repetitions), so repetitions measure TIMING
# JITTER ONLY and accuracy is unaffected. Timing for 3B/7B is therefore
# single-shot and carries no IQR. The repetition count is never mixed WITHIN a
# model: 0.5B resumes at the same reps=3 it started with.
set -u
R="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$R/../../../.." && pwd)"
PY="$REPO/run/.venv/bin/python"
export PYTHONDONTWRITEBYTECODE=1
LOG="$R/logs/commands.log"

run() {
  local label="$1"; shift
  echo "=== $(date -u +%FT%TZ) $label" | tee -a "$LOG"
  echo "CMD: $*" >> "$LOG"
  "$@" 2>&1 | tee -a "$R/logs/lane_b.log"
  echo "EXIT ${PIPESTATUS[0]}  $label" | tee -a "$LOG"
  return 0
}

while IFS='|' read -r M REPS; do
  [ -z "$M" ] && continue
  SAFE="${M//\//__}"
  mkdir -p "$R/raw/$SAFE/lane_b"
  run "laneB $M fp16 cuda reps=$REPS" "$PY" "$R/scripts/lane_b.py" --model "$M" \
      --out "$R/raw/$SAFE/lane_b/gen.jsonl" --precision fp16 --device cuda --reps "$REPS"
done <<'MODELS'
Qwen/Qwen2.5-Coder-0.5B-Instruct|3
Qwen/Qwen2.5-Coder-1.5B-Instruct|3
Qwen/Qwen2.5-Coder-3B-Instruct|1
Qwen/Qwen2.5-Coder-7B-Instruct|1
MODELS

# Secondary analysis: conditional task loss on the Instruct checkpoints.
for M in Qwen/Qwen2.5-Coder-0.5B-Instruct Qwen/Qwen2.5-Coder-1.5B-Instruct \
         Qwen/Qwen2.5-Coder-3B-Instruct; do
  SAFE="${M//\//__}"
  mkdir -p "$R/raw/$SAFE/lane_b"
  run "condloss $M fp16 cuda" "$PY" "$R/scripts/conditional_loss.py" --model "$M" \
      --out "$R/raw/$SAFE/lane_b/condloss.jsonl" --precision fp16 --device cuda
done

echo "LANE B COMPLETE" | tee -a "$LOG"
