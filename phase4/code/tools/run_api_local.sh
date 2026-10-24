#!/bin/bash
# run_api_local.sh — run a run's SERVED models on this machine, one process per model.
#
#   P4_RESULTS_ROOT=<results folder> P4_PY=<python> \
#     bash phase4/code/tools/run_api_local.sh <RUN_ID> [experiment ...]   (default: arm_a primary armb)
#
# For models served by the ASU RC LLM API (registry gpus=0): they need the network, not a GPU, so
# a laptop can run them; on Sol, use sol/submit.sh's *_api jobs instead. The run must exist
# (`run.py <stage> init`) and its models must be pinned (`run.py prefetch`).
#
# What it does: preflight (refuses on any FAIL), then every served model at once, each running
# the experiments in order; fertility runs alongside. Each process writes its own log to
# <results>/<RUN_ID>/logs/local_*.log. Resume = the same command again: finished cells are
# skipped. The key is read by the scorer from ~/.config/asu-rc/llm_api_key, never from here.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN="${1:?usage: run_api_local.sh <RUN_ID> [experiment ...]}"
shift
EXPS=("$@")
[ ${#EXPS[@]} -gt 0 ] || EXPS=(arm_a primary armb)
STAGE="${RUN%%-*}"
PY="${P4_PY:-python3}"
CLI="$HERE/../run.py"
: "${P4_RESULTS_ROOT:?set P4_RESULTS_ROOT to the results folder}"
LOG="$P4_RESULTS_ROOT/$RUN/logs"
mkdir -p "$LOG"

IDX="$("$PY" "$CLI" array-indices --run "$RUN" --gpus 0)"
[ -n "$IDX" ] || { echo "run_api_local.sh: no served model in $RUN" >&2; exit 2; }
"$PY" "$CLI" "$STAGE" preflight --run "$RUN"

pids=()
for i in ${IDX//,/ }; do
  (
    echo "[$(date -Is)] task $i: $("$PY" -c "import json,sys; print(json.load(open(sys.argv[1]))['config']['models'][int(sys.argv[2])])" "$P4_RESULTS_ROOT/$RUN/manifests/run_config.json" "$i")"
    for e in "${EXPS[@]}"; do
      if "$PY" "$CLI" "$STAGE" run --run "$RUN" --experiment "$e" --task "$i"; then r=0; else r=$?; fi
      echo "[$(date -Is)] task $i: $e exit=$r"
    done
  ) > "$LOG/local_task_${i}.log" 2>&1 &
  pids+=($!)
done
(
  if "$PY" "$CLI" "$STAGE" fertility --run "$RUN"; then r=0; else r=$?; fi
  echo "[$(date -Is)] fertility exit=$r"
) > "$LOG/local_fertility.log" 2>&1 &
pids+=($!)
echo "[$(date -Is)] started ${#pids[@]} processes (models: $IDX; and fertility); logs: $LOG/local_*.log"

rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "[$(date -Is)] all processes finished; check the logs, then: $PY $CLI $STAGE analyze --run $RUN"
exit $rc
