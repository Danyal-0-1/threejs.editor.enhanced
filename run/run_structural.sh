#!/usr/bin/env bash
# run_structural.sh — the NO-MODEL, NO-NETWORK lane, end to end.
#
#   run/run_structural.sh [experiment-dir]
#
# Every command it runs is also written out verbatim in run/run.md; this script
# exists to sequence them and preserve logs, not to hide them. If you would
# rather drive the phases by hand, run.md is the authoritative runbook.
#
# It does NOT overwrite committed artifacts. Grammars are re-rendered into the
# experiment's artifacts/ directory and diffed; corpora are checked with
# --check-only; METRICS_PARITY.md is regenerated to a temp file and diffed.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

EXP_REL="${1:-run/experiments/$(date -u +%Y%m%d-%H%M%S)}"
mkdir -p "$REPO_ROOT/$EXP_REL"/{logs,results,artifacts,metadata}
echo "$EXP_REL" > "$REPO_ROOT/run/.current_experiment"
EXP="$REPO_ROOT/$EXP_REL"

PY="${PYTHON:-python3}"
ALIEN="$REPO_ROOT/alien_syntax"
P1="${PHASE1_DIR:-$REPO_ROOT/grammar_and_3DOM_client}"
export PHASE1_DIR="$P1"

echo "════════════════════════════════════════════════════════════════════"
echo " STRUCTURAL LANE — no models, no network, no GPU"
echo " experiment : $EXP_REL"
echo " python     : $($PY -V 2>&1)"
echo " PHASE1_DIR : $PHASE1_DIR"
echo "════════════════════════════════════════════════════════════════════"

fail=0
phase() { echo; echo "── Phase $1: $2 ──"; }

phase 0 "environment preflight"
"$REPO_ROOT/run/runlog.sh" p0-preflight "$PY" run/preflight.py || fail=1
"$PY" run/preflight.py --json > "$EXP/metadata/preflight.json" || true
{
  echo "captured_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "python=$($PY -V 2>&1)"
  echo "os=$(uname -srmo)"
  echo "git_commit=$(git rev-parse HEAD 2>/dev/null || echo 'not a git repo')"
  echo "git_dirty=$(test -n "$(git status --porcelain 2>/dev/null)" && echo yes || echo no)"
  echo "PHASE1_DIR=$PHASE1_DIR"
} > "$EXP/metadata/environment-structural.txt"
"$PY" -m pip list --format=freeze 2>/dev/null | sort > "$EXP/metadata/pip-freeze.txt" || true

phase 1 "Phase 1 contract verification"
( cd "$P1" && "$REPO_ROOT/run/runlog.sh" p1-phase1-coverage "$PY" conformance/coverage2.py ) || fail=1

phase 2 "template reconstruction (writes to templates/, restored if it drifts)"
cp "$ALIEN/grammar/templates/grammar.iso.template.ebnf" \
   "$ALIEN/grammar/templates/grammar.w3c.template.ebnf" "$EXP/artifacts/"
( cd "$ALIEN" && "$REPO_ROOT/run/runlog.sh" p2-build-templates \
    "$PY" grammar/templates/build_templates.py ) || fail=1
if ! diff -q "$EXP/artifacts/grammar.iso.template.ebnf" \
        "$ALIEN/grammar/templates/grammar.iso.template.ebnf" >/dev/null ||
   ! diff -q "$EXP/artifacts/grammar.w3c.template.ebnf" \
        "$ALIEN/grammar/templates/grammar.w3c.template.ebnf" >/dev/null; then
  echo "  TEMPLATE DRIFT — restoring the committed templates"
  cp "$EXP/artifacts/grammar.iso.template.ebnf" \
     "$EXP/artifacts/grammar.w3c.template.ebnf" "$ALIEN/grammar/templates/"
  fail=1
else
  echo "  templates reproduce byte-for-byte"
fi

phase 3 "alpha/beta/gamma grammar rendering (into artifacts/, then diff)"
mkdir -p "$EXP/artifacts/generated"
( cd "$ALIEN" && "$REPO_ROOT/run/runlog.sh" p3-render-grammar \
    "$PY" grammar/render_grammar.py --outdir "$EXP/artifacts/generated" \
    alpha beta gamma ) || fail=1
if diff -rq "$ALIEN/grammar/generated" "$EXP/artifacts/generated" >/dev/null; then
  echo "  generated grammars match the committed artifacts"
else
  echo "  GENERATED-GRAMMAR DRIFT (committed files NOT modified):"
  diff -rq "$ALIEN/grammar/generated" "$EXP/artifacts/generated" | sed 's/^/    /'
  fail=1
fi

phase 4 "corpus regeneration and gates A1-A7 (check-only: writes nothing)"
( cd "$ALIEN" && "$REPO_ROOT/run/runlog.sh" p4-corpus-gates \
    "$PY" src/generate_corpus.py alpha beta gamma --check-only ) || fail=1

phase 5 "collision checks (a)-(f) and proposed (g)"
( cd "$ALIEN" && "$REPO_ROOT/run/runlog.sh" p5-collisions \
    "$PY" measure/collisions.py identity alpha beta gamma --md ) || fail=1
cp "$EXP/logs/p5-collisions.out" "$EXP/results/collisions.md"

phase 6 "DFA and metrics parity"
( cd "$ALIEN" && "$REPO_ROOT/run/runlog.sh" p6-dfa-parity \
    "$PY" measure/dfa_parity.py identity alpha beta gamma --md ) || fail=1
cp "$EXP/logs/p6-dfa-parity.out" "$EXP/results/dfa-parity.md"
( cd "$ALIEN" && "$REPO_ROOT/run/runlog.sh" p6-metrics-parity \
    "$PY" measure/metrics_parity.py ) || fail=1
cp "$EXP/logs/p6-metrics-parity.out" "$EXP/artifacts/METRICS_PARITY.regenerated.md"
if diff -q "$ALIEN/reports/METRICS_PARITY.md" \
      "$EXP/artifacts/METRICS_PARITY.regenerated.md" >/dev/null; then
  echo "  METRICS_PARITY.md regenerates identically"
else
  echo "  METRICS_PARITY.md DRIFT (committed file NOT modified); see artifacts/"
  fail=1
fi

phase 7 "verification suites, reported independently"
for suite in isomorphism roundtrip invariants canonicalization phi_validation \
             grammar_whitespace seams measure_formulas preflight; do
  ( cd "$ALIEN" && "$REPO_ROOT/run/runlog.sh" "p7-test-$suite" \
      "$PY" "tests/test_${suite}.py" ) || fail=1
  tail -1 "$EXP/logs/p7-test-$suite.out" | sed "s/^/    test_$suite: /"
done

phase 8 "structural fertility PROXY (NOT the tokenizer constraint)"
( cd "$ALIEN" && "$REPO_ROOT/run/runlog.sh" p8-fertility-proxy \
    "$PY" measure/fertility.py --structural --md ) || fail=1
cp "$EXP/logs/p8-fertility-proxy.out" "$EXP/results/fertility-structural-proxy.md"
echo "    NOTE: character-length parity is NOT tokenizer parity. CONSTRAINT 1"
echo "    is defined on the fertility RATIO and needs a real tokenizer."

phase 12 "artifact checksums"
"$REPO_ROOT/run/runlog.sh" p12-verify-artifacts \
  "$PY" run/verify_artifacts.py --write "$EXP/metadata/checksums.txt" || fail=1

echo
echo "════════════════════════════════════════════════════════════════════"
if [ "$fail" -eq 0 ]; then
  echo " STRUCTURAL LANE: PASS"
else
  echo " STRUCTURAL LANE: FAILURES PRESENT — see $EXP_REL/logs/"
fi
echo " CONSTRAINT 1 (tokenizer fertility) is NOT covered by this lane."
echo " experiment: $EXP_REL"
echo "════════════════════════════════════════════════════════════════════"
exit "$fail"
