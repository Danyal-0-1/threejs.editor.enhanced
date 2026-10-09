#!/bin/bash
# Restore the files that are stored gzipped because they exceed GitHub's 100 MB limit,
# and verify every byte against the run's LARGE_FILES.sha256.
#
#   bash phase3_3/sol_results/restore_large_files.sh heldout-20261007a
#
# Keeps the .gz files; never overwrites an existing original that already verifies.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN="${1:?usage: restore_large_files.sh <run id>}"
cd "$HERE/$RUN"
[ -f LARGE_FILES.sha256 ] || { echo "no LARGE_FILES.sha256 in $RUN: nothing to restore"; exit 0; }
grep -v '^#' LARGE_FILES.sha256 | while read -r sum path; do
  case "$path" in *.gz) continue ;; esac
  if [ -f "$path" ] && [ "$(sha256sum "$path" | cut -d' ' -f1)" = "$sum" ]; then
    echo "ok (already present)  $path"; continue
  fi
  [ -f "$path.gz" ] || { echo "MISSING $path.gz" >&2; exit 1; }
  gzip -dc "$path.gz" > "$path.tmp"
  if [ "$(sha256sum "$path.tmp" | cut -d' ' -f1)" != "$sum" ]; then
    rm -f "$path.tmp"; echo "CHECKSUM MISMATCH for $path; nothing written" >&2; exit 1
  fi
  mv "$path.tmp" "$path"
  echo "restored and verified  $path"
done
