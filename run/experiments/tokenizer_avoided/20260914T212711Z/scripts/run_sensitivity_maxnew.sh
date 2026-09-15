#!/usr/bin/env bash
# D2 SENSITIVITY CONDITION — truncation at max_new_tokens.
#
# The primary matrix used a common max_new_tokens = 512. A non-trivial share of
# 0.5B-Instruct generations reached that cap, concentrated in beta and gamma.
# Inspection indicated TASK ABANDONMENT (the model stops writing the target
# language and emits unrelated Python) rather than answer-length pressure -- the
# correct answer is ~20-60 model tokens in every language.
#
# This run TESTS that claim instead of asserting it. It re-runs the affected
# model/condition at a larger common limit, in ALL FOUR LANGUAGES (never only
# the language that truncated), and writes to a SEPARATELY LABELLED condition
# (`bare@maxnew1536` / `scaffolded@maxnew1536`) so these rows can never be
# pooled with the primary matrix.
#
# Interpretation rule fixed in advance:
#   - if cases that truncated at 512 now terminate and score VALID_CORRECT,
#     the 512 limit WAS biting and the primary matrix must be re-run at the
#     larger limit for every language arm;
#   - if they still fail (truncate again, or parse-fail), the 512 limit was not
#     the binding constraint and the primary matrix stands, with the truncation
#     rate reported per language as a failure mode in its own right.
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
  "$@" 2>&1 | tee -a "$R/logs/sensitivity.log"
  echo "EXIT ${PIPESTATUS[0]}  $label" | tee -a "$LOG"
  return 0
}

M="Qwen/Qwen2.5-Coder-0.5B-Instruct"
SAFE="${M//\//__}"
mkdir -p "$R/raw/$SAFE/lane_b"

for COND in scaffolded bare; do
  run "SENSITIVITY $M $COND maxnew=1536 (all 4 languages)" \
      "$PY" "$R/scripts/lane_b.py" --model "$M" \
      --out "$R/raw/$SAFE/lane_b/gen_maxnew1536.jsonl" \
      --prompts-dir "$R/prompts/rendered_sensitivity" \
      --precision fp16 --device cuda --reps 1 \
      --max-new-tokens 1536 --conditions "$COND" \
      --condition-suffix "@maxnew1536"
done

echo "SENSITIVITY COMPLETE" | tee -a "$LOG"
