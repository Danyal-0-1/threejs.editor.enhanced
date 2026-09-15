#!/usr/bin/env bash
# TASK 4 labeling control across every Instruct model.
set -u
R="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$R/../../../.." && pwd)"
PY="$REPO/run/.venv/bin/python"
export PYTHONDONTWRITEBYTECODE=1
LOG="$R/logs/commands.log"
for M in Qwen/Qwen2.5-Coder-0.5B-Instruct Qwen/Qwen2.5-Coder-1.5B-Instruct \
         Qwen/Qwen2.5-Coder-3B-Instruct Qwen/Qwen2.5-Coder-7B-Instruct; do
  SAFE="${M//\//__}"
  mkdir -p "$R/raw/$SAFE/lane_b"
  echo "=== $(date -u +%FT%TZ) labeling $M fp16 cuda" | tee -a "$LOG"
  "$PY" "$R/scripts/labeling.py" --model "$M" \
      --out "$R/raw/$SAFE/lane_b/labeling.jsonl" --precision fp16 --device cuda \
      2>&1 | tee -a "$R/logs/labeling.log"
  echo "EXIT ${PIPESTATUS[0]}  labeling $M" | tee -a "$LOG"
done
echo "LABELING COMPLETE" | tee -a "$LOG"
