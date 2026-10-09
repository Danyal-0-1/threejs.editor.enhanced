#!/bin/bash
# submit_chain.sh <heldout run id> -- submit the whole held-out stage as ONE chain,
# one job at a time. Run on the Sol login node, after `heldout init` and the unlock.
#
#   heldout_eval (1 GPU, every model, %1) -> heldout_eval_2gpu (the 72B pair, %1)
#   -> arm_b (instruct models, %1) -> arm_b_2gpu -> h5 (instruct, %1) -> h5_2gpu -> final_export
#
# Each stage waits for the previous one (afterany), so one failed task does not stall
# the rest; it can be resubmitted later with P33_ARRAY. H5 is the exception: it
# derives its arms from the merged held-out Arm A and stores them for good, so both
# H5 jobs also need BOTH evaluation jobs to have succeeded (afterok). Arm B and H5 get
# longer limits than submit.sh's defaults (12 h, 10 h), which are tight for 32B/33B.
# The job ids go to results/<run>/logs/submission_chain.env.
set -euo pipefail
HO="${1:?usage: submit_chain.sh <heldout run id>}"
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source sol.env && source env/activate.sh
unset P33_FAKE P33_ARRAY
REC="$P33_RESULTS_ROOT/$HO/logs/submission_chain.env"
mkdir -p "$(dirname "$REC")"

# array indices per GPU class, and the instruct models (Arm B and H5 apply only to them)
ONE=$("$P33_PY" scripts/p33.py array-indices --run "$HO" --gpus 1)
TWO=$("$P33_PY" scripts/p33.py array-indices --run "$HO" --gpus 2)
read -r INST1 INST2 < <("$P33_PY" - "$HO" <<'PY'
import json, os, sys
sys.path.insert(0, "src")
from p33 import registry
cfg = json.load(open(os.path.join(os.environ["P33_RESULTS_ROOT"], sys.argv[1], "manifests", "run_config.json")))["config"]
inst = [(i, m) for i, m in enumerate(cfg["models"]) if registry.spec(m).kind == "instruct"]
one = [str(i) for i, m in inst if registry.gpus_needed(m) == 1]
two = [str(i) for i, m in inst if registry.gpus_needed(m) == 2]
print(",".join(one) or "-", ",".join(two) or "-")
PY
)
TRACE="$P33_RESULTS_ROOT/$HO/logs/submit_trace.txt"
sub() {   # sub <job> <array or ""> [sbatch args...]  -> prints the job id, or stops the script
  local job=$1 arr=$2 out id; shift 2
  out=$(P33_ARRAY="$arr" bash submit.sh "$job" "$HO" "$@" 2>>"$TRACE") || true
  id=$(printf '%s\n' "$out" | sed -n 's/^Submitted batch job \([0-9]*\)$/\1/p')
  if [ -z "$id" ]; then echo "submission of $job FAILED; see $TRACE" >&2; exit 1; fi
  echo "$id"
}
A=$(sub heldout_eval      "${ONE}%1")
B=$(sub heldout_eval_2gpu "${TWO}%1"   --dependency=afterany:$A)
C=$(sub arm_b             "${INST1}%1" --dependency=afterany:$B --time=12:00:00)   # 8 h default: tight for 32B/33B
D=$(sub arm_b_2gpu        "${INST2}%1" --dependency=afterany:$C)
# H5 derives its arms from the merged held-out Arm A and stores them for good:
# it must never start on an incomplete Arm A, hence afterok on BOTH evaluation jobs.
E=$(sub h5                "${INST1}%1" --dependency=afterany:$D,afterok:$A:$B --time=10:00:00)   # 6 h default: tight for 33B
F=$(sub h5_2gpu           "${INST2}%1" --dependency=afterany:$E,afterok:$A:$B)
G=$(sub final_export "" --dependency=afterany:$F)
cat > "$REC" <<REC
HO=$HO
SUBMITTED=$(date -Is)
HELDOUT_EVAL_JID=$A        # array ${ONE}%1
HELDOUT_EVAL_2GPU_JID=$B   # array ${TWO}%1
ARM_B_JID=$C               # array ${INST1}%1 (instruct models)
ARM_B_2GPU_JID=$D          # array ${INST2}%1
H5_JID=$E                  # array ${INST1}%1; afterok on $A and $B
H5_2GPU_JID=$F             # array ${INST2}%1; afterok on $A and $B
FINAL_EXPORT_JID=$G
REC
cat "$REC"
squeue -u "$USER" -o "%.12i %.22j %.9T %.10l %R"
