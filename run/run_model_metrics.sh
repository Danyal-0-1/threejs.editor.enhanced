#!/usr/bin/env bash
# run_model_metrics.sh — the MODEL-DEPENDENT lane. Network required.
#
#   run/run_model_metrics.sh [experiment-dir] [--fertility-only]
#
# Kept separate from run_structural.sh on purpose: these phases download data,
# take real time, and can fail for reasons that say nothing about the compiler.
# A structural PASS must never be contingent on them, and their absence must
# never look like a pass.
#
# Phase 9  real tokenizer fertility   ~50 MB download, no GPU   (CONSTRAINT 1)
# Phase 10 base-model prior strength  ~10-25 GB download, GPU   (primary objective)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

FERTILITY_ONLY=0
ARGS=()
for a in "$@"; do
  if [ "$a" = "--fertility-only" ]; then FERTILITY_ONLY=1; else ARGS+=("$a"); fi
done

EXP_REL="${ARGS[0]:-run/experiments/$(date -u +%Y%m%d-%H%M%S)}"
mkdir -p "$REPO_ROOT/$EXP_REL"/{logs,results,artifacts,metadata}
echo "$EXP_REL" > "$REPO_ROOT/run/.current_experiment"
EXP="$REPO_ROOT/$EXP_REL"

VENV="$REPO_ROOT/run/.venv"
PY="${PYTHON:-$VENV/bin/python}"
[ -x "$PY" ] || { echo "no interpreter at $PY — see run/run.md §3 (venv setup)"; exit 1; }
ALIEN="$REPO_ROOT/alien_syntax"
export PHASE1_DIR="${PHASE1_DIR:-$REPO_ROOT/grammar_and_3DOM_client}"

echo "════════════════════════════════════════════════════════════════════"
echo " MODEL-DEPENDENT LANE — network required"
echo " experiment : $EXP_REL"
echo " python     : $("$PY" -V 2>&1)  ($PY)"
echo " fertility only: $FERTILITY_ONLY"
echo "════════════════════════════════════════════════════════════════════"

fail=0

echo; echo "── Phase 0: preflight (model lane) ──"
if [ "$FERTILITY_ONLY" -eq 1 ]; then
  "$REPO_ROOT/run/runlog.sh" m0-preflight "$PY" run/preflight.py || fail=1
else
  "$REPO_ROOT/run/runlog.sh" m0-preflight "$PY" run/preflight.py --model || fail=1
fi
"$PY" -m pip list --format=freeze 2>/dev/null | sort \
  > "$EXP/metadata/pip-freeze-model-lane.txt" || true
{
  echo "captured_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "interpreter=$PY"
  echo "python=$("$PY" -V 2>&1)"
  echo "gpu=$(nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || echo none)"
  echo "hf_home=${HF_HOME:-<unset>}"
  echo "hf_token_set=$([ -n "${HF_TOKEN:-}" ] && echo yes || echo no)"
} > "$EXP/metadata/environment-model-lane.txt"
# NB: the token VALUE is never logged, only whether one is set.

echo; echo "── Phase 9: real tokenizer fertility (CONSTRAINT 1) ──"
( cd "$ALIEN" && "$REPO_ROOT/run/runlog.sh" m9-fertility \
    "$PY" measure/fertility.py --md ) || fail=1
cp "$EXP/logs/m9-fertility.out" "$EXP/results/fertility-tokenizers.md"
echo "    -> $EXP_REL/results/fertility-tokenizers.md"

if [ "$FERTILITY_ONLY" -eq 1 ]; then
  echo; echo "── Phase 10 SKIPPED (--fertility-only) ──"
  echo "    ΔNLL remains PENDING-EMPIRICAL-MEASUREMENT."
  echo "    Resume with: run/run_model_metrics.sh $EXP_REL"
  exit "$fail"
fi

echo; echo "── Phase 10: base-model prior strength and ΔNLL ──"
echo "    downloads model weights; safe to rerun (the HF cache is reused)"
( cd "$ALIEN" && "$REPO_ROOT/run/runlog.sh" m10-prior-strength \
    "$PY" measure/prior_strength.py --md ) || fail=1
cp "$EXP/logs/m10-prior-strength.out" "$EXP/results/prior-strength.md"
echo "    -> $EXP_REL/results/prior-strength.md"

echo
echo "════════════════════════════════════════════════════════════════════"
if [ "$fail" -eq 0 ]; then
  echo " MODEL LANE: completed"
else
  echo " MODEL LANE: FAILURES PRESENT — see $EXP_REL/logs/"
fi
echo " Every number above depends on the tokenizer/model revisions recorded"
echo " in the Provenance block of each report. Cite them, not just the repo."
echo "════════════════════════════════════════════════════════════════════"
exit "$fail"
