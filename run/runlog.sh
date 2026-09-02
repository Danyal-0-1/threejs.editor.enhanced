#!/usr/bin/env bash
# runlog.sh — thin execution recorder. It HIDES NOTHING: the command it runs is
# printed, echoed into the log, and reproduced verbatim in run/run.md. Its only
# job is to capture stdout, stderr, exit code and timing next to each other so a
# later reader can tell a real PASS from an unread one.
#
#   run/runlog.sh <slug> <command...>
#
# Writes: $EXP/logs/<slug>.out, .err, .meta
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXP_REL="$(cat "$REPO_ROOT/run/.current_experiment")"
EXP="$REPO_ROOT/$EXP_REL"

slug="$1"; shift
out="$EXP/logs/${slug}.out"
err="$EXP/logs/${slug}.err"
meta="$EXP/logs/${slug}.meta"

printf '=== %s\n    cwd: %s\n    cmd: %s\n' "$slug" "$PWD" "$*"
start_epoch=$(date -u +%s)
start_iso=$(date -u +%Y-%m-%dT%H:%M:%SZ)

"$@" >"$out" 2>"$err"
rc=$?

end_epoch=$(date -u +%s)
{
  echo "slug=$slug"
  echo "command=$*"
  echo "cwd=$PWD"
  echo "exit_code=$rc"
  echo "started_utc=$start_iso"
  echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "duration_seconds=$((end_epoch - start_epoch))"
  echo "stdout_bytes=$(wc -c <"$out")"
  echo "stderr_bytes=$(wc -c <"$err")"
} >"$meta"

printf '    exit: %s   (%ss)   log: %s\n' "$rc" "$((end_epoch - start_epoch))" "$EXP_REL/logs/${slug}.out"
exit $rc
