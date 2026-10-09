#!/bin/bash
# Runs after the held-out chain's final export (job dependency). CPU only, no model.
# Writes ONLY under <run>/analysis_addenda/: never inside csv/, plots/ or reports/.
set -uo pipefail
HO=heldout-20261007a
E=$HOME/phase3-3_experiment_sol
PP=$E/postprocess
SOL=$E/repo/phase3_2/sol
source "$SOL/sol.env"; source "$SOL/env/activate.sh"
R=$P33_RESULTS_ROOT/$HO
OUT=$R/analysis_addenda
mkdir -p "$OUT/summary" "$OUT/exploratory"
echo "[$(date -Is)] postprocess for $HO on $(hostname)"
echo "--- completeness"; cat "$R/csv/run_completeness.csv" 2>/dev/null
echo "--- D11 scale analysis (pre-specified, approved 2026-10-08)"
PYTHONPATH="$SOL/src" "$P33_PY" "$PP/scale_analysis.py" --run "$HO" 2>&1 | grep -vE "FutureWarning|warnings.warn"
echo "--- summary"
python3 "$PP/summarise_heldout.py" "$R" > "$OUT/summary/HELDOUT_SUMMARY.txt" 2>&1; echo "exit=$?"
echo "--- exploratory (NOT preregistered)"
{ echo "EXPLORATORY, not preregistered: adaptation (KM median examples to switch) by role, remap density and model kind."
  python3 "$PP/explore_density.py" "$R/csv/kstar_survival.csv"; } > "$OUT/exploratory/adaptation_by_role_density.txt" 2>&1; echo "exit=$?"
ls -la "$OUT" "$OUT"/*
echo "[$(date -Is)] postprocess done"
