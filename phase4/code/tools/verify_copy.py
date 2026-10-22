#!/usr/bin/env python3
"""verify_copy.py — compare every copied file with the Phase 3.3 file it came from.

    python3 tools/verify_copy.py              # one line per kind of change, and any problem
    python3 tools/verify_copy.py -v           # one line per file
    python3 tools/verify_copy.py --diff p4/analysis/h4.py   # the exact differences of one file

phase4/code/ was built as a copy of the Phase 3.3 pipeline (see ../README.md). Every copied
file is listed in source_manifest.json with its origin and both checksums. This script checks,
for each one:

  1. the origin still has the checksum it had when it was copied (Phase 3.3 is frozen, so it
     should never change);
  2. the copy still has the checksum it had when it was made. If not, the file was changed
     since: in Phase 4 that is expected, and the file is listed as "changed since the copy";
  3. the copy differs from its origin only as recorded. A Python file must keep every line
     number, and each line that differs must be an import line in both versions or part of a
     recorded path edit. A shell file must equal its origin with the recorded edits applied.

Exit code: 0 when every file is as recorded (changes made since the copy are reported but are
not errors), 1 when an origin changed or a copy differs from its origin in an unrecorded way.
"""

from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import json
import os
import sys

CODE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(CODE))


def sha(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def import_lines(text: str) -> set[int]:
    out = set()
    for n in ast.walk(ast.parse(text)):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            out.update(range(n.lineno, n.end_lineno + 1))
    return out


def edit_lines(text: str, edits: list[dict]) -> set[int]:
    out = set()
    for e in edits:
        start = 0
        while (i := text.find(e["new"], start)) >= 0:
            first = text.count("\n", 0, i) + 1
            out.update(range(first, first + e["new"].count("\n") + 1))
            start = i + max(len(e["new"]), 1)
    return out


def unrecorded(entry: dict, origin_text: str, copy_text: str) -> list[str]:
    """Differences between origin and copy that the manifest does not explain."""
    if entry["change"] == "subset":
        return []                                  # a hand-made subset: shown by --diff only
    if not entry["path"].endswith(".py"):
        expect = origin_text
        for e in entry["edits"]:
            expect = expect.replace(e["old"], e["new"])
        return [] if expect == copy_text else ["differs from its origin with the recorded edits applied"]
    a, b = origin_text.split("\n"), copy_text.split("\n")
    if len(a) != len(b):
        return [f"line count {len(a)} -> {len(b)}"]
    ia, ib = import_lines(origin_text), import_lines(copy_text)
    eb = edit_lines(copy_text, entry["edits"])
    bad = [i for i in range(1, len(a) + 1)
           if a[i - 1] != b[i - 1] and not ((i in ia and i in ib) or i in eb)]
    return [f"line {i} changed outside imports and recorded edits" for i in bad[:5]]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-v", action="store_true", help="one line per file")
    ap.add_argument("--diff", metavar="PATH", help="print the differences of one file (path as in the manifest)")
    a = ap.parse_args(argv)
    man = json.load(open(os.path.join(CODE, "source_manifest.json"), encoding="utf-8"))
    entries = {e["path"]: e for e in man["files"]}
    if a.diff:
        e = entries[a.diff]
        old = open(os.path.join(REPO, e["origin"]), encoding="utf-8").read().split("\n")
        new = open(os.path.join(CODE, e["path"]), encoding="utf-8").read().split("\n")
        sys.stdout.writelines(l + "\n" for l in difflib.unified_diff(
            old, new, fromfile=e["origin"], tofile="phase4/code/" + e["path"], lineterm="", n=0))
        return 0
    counts: dict[str, int] = {}
    problems, since = [], []
    for e in man["files"]:
        o, c = os.path.join(REPO, e["origin"]), os.path.join(CODE, e["path"])
        if not os.path.exists(o):
            problems.append(f"{e['path']}: its origin {e['origin']} is missing")
            continue
        if not os.path.exists(c):
            problems.append(f"{e['path']}: missing from phase4/code")
            continue
        if sha(o) != e["origin_sha256"]:
            problems.append(f"{e['path']}: its origin {e['origin']} changed after the copy")
        now = sha(c)
        if now != e["sha256"]:
            since.append(e["path"])
        elif e["change"] != "identical":
            text_o = open(o, encoding="utf-8").read()
            text_c = open(c, encoding="utf-8").read()
            for p in unrecorded(e, text_o, text_c):
                problems.append(f"{e['path']}: {p}")
        counts[e["change"]] = counts.get(e["change"], 0) + 1
        if a.v:
            state = "CHANGED SINCE THE COPY" if now != e["sha256"] else e["change"]
            print(f"  {state:24s} {e['path']:45s} <- {e['origin']}")
    print(f"{len(man['files'])} copied files, from commit {man['source_commit'][:8]}:")
    for k in ("identical", "imports", "imports and paths", "paths", "subset"):
        if k in counts:
            print(f"  {counts[k]:4d}  {k}")
    print(f"changed since the copy (Phase 4 changes): {len(since)}")
    for p in since:
        print(f"  {p}")
    print(f"problems: {len(problems)}")
    for p in problems:
        print(f"  {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
