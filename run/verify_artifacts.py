#!/usr/bin/env python3
"""verify_artifacts.py — checksums for every artifact a result depends on.

    python3 run/verify_artifacts.py                      # print
    python3 run/verify_artifacts.py --write PATH         # print and save
    python3 run/verify_artifacts.py --compare PATH       # diff against a saved set

A reported number is only reproducible if you can say WHICH corpus, WHICH
grammar and WHICH φ-map produced it. This writes a SHA-256 for each, so a later
run can prove it used the same inputs — or show exactly which one moved.

`--compare` exits nonzero on any difference, so it can gate a pipeline.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ALIEN = os.path.join(REPO, "alien_syntax")
P1 = os.path.abspath(os.environ.get("PHASE1_DIR",
                                    os.path.join(REPO, "grammar_and_3DOM_client")))

GROUPS: dict[str, list[str]] = {
    "phase1 (frozen reference)": [
        os.path.join(P1, n) for n in (
            "terminals.json", "ir_schema.json",
            "3dom_grammar.iso.ebnf", "3dom_grammar.w3c.ebnf",
            "conformance/refgrammar.py", "conformance/positive.txt",
            "conformance/negative.txt", "conformance/vacuous.txt",
        )
    ],
    "phase2 candidates (φ-maps)": [
        os.path.join(ALIEN, "candidates", f"phi_{n}.json")
        for n in ("alpha", "beta", "gamma")
    ],
    "phase2 templates": [
        os.path.join(ALIEN, "grammar", "templates", n) for n in (
            "grammar.lark.template", "grammar.iso.template.ebnf",
            "grammar.w3c.template.ebnf", "grammar.diagram.template.md",
        )
    ],
    "phase2 generated grammars": sorted(
        os.path.join(ALIEN, "grammar", "generated", f)
        for f in (os.listdir(os.path.join(ALIEN, "grammar", "generated"))
                  if os.path.isdir(os.path.join(ALIEN, "grammar", "generated"))
                  else [])
    ),
    "phase2 generated corpora": sorted(
        os.path.join(ALIEN, "conformance", f)
        for f in (os.listdir(os.path.join(ALIEN, "conformance"))
                  if os.path.isdir(os.path.join(ALIEN, "conformance")) else [])
        if f.endswith(".txt")
    ),
}


def digest(path: str) -> str:
    if not os.path.isfile(path):
        return "MISSING"
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect() -> list[str]:
    lines = [f"# artifact checksums (sha256)",
             f"# PHASE1_DIR={P1}"]
    for group, paths in GROUPS.items():
        lines.append(f"\n## {group}")
        for path in paths:
            try:
                label = os.path.relpath(path, REPO)
            except ValueError:                             # different drive
                label = path
            lines.append(f"{digest(path)}  {label}")
    return lines


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", metavar="PATH")
    ap.add_argument("--compare", metavar="PATH")
    args = ap.parse_args(argv[1:])

    lines = collect()
    text = "\n".join(lines) + "\n"
    missing = [line for line in lines if line.startswith("MISSING")]

    if args.compare:
        with open(args.compare, encoding="utf-8") as fh:
            old = [x for x in fh.read().splitlines()
                   if x and not x.startswith("#")]
        new = [x for x in lines if x and not x.startswith("#")]
        old_map = dict(reversed(x.split("  ", 1)) for x in old if "  " in x)
        new_map = dict(reversed(x.split("  ", 1)) for x in new if "  " in x)
        changed = sorted(k for k in set(old_map) & set(new_map)
                         if old_map[k] != new_map[k])
        added = sorted(set(new_map) - set(old_map))
        removed = sorted(set(old_map) - set(new_map))
        for label, items in (("CHANGED", changed), ("ADDED", added),
                             ("REMOVED", removed)):
            for item in items:
                print(f"{label:8} {item}")
        if changed or added or removed:
            print(f"\nFAIL — {len(changed)} changed, {len(added)} added, "
                  f"{len(removed)} removed since {args.compare}")
            return 1
        print(f"PASS — every artifact matches {args.compare}")
        return 0

    print(text, end="")
    if args.write:
        os.makedirs(os.path.dirname(os.path.abspath(args.write)), exist_ok=True)
        with open(args.write, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"\n(written to {args.write})")
    if missing:
        print(f"\nWARNING — {len(missing)} artifact(s) are MISSING", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
