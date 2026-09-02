#!/usr/bin/env python3
"""preflight.py — fail BEFORE the parser imports, with an actionable message.

    python3 run/preflight.py            # structural lane requirements
    python3 run/preflight.py --model    # also check the model-lane requirements
    python3 run/preflight.py --json     # machine-readable, for logging

WHY THIS EXISTS
    Phase 2 reaches into Phase 1 for terminals.json, refgrammar.py, the frozen
    grammars, the IR schema and the three corpora. If any of them is missing,
    the failure surfaces as a ModuleNotFoundError three imports deep, in a file
    that has nothing to do with the missing artifact. This script names the
    exact path and what it is for, and it runs with NOTHING imported from either
    phase — so it still works when the thing being diagnosed is the import.

EXIT CODES
    0  everything required by the selected lane is present
    1  a required artifact or dependency is missing
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ALIEN = os.path.join(REPO, "alien_syntax")


def phase1_dir() -> str:
    """The same resolution src/phi.py uses, duplicated ON PURPOSE.

    Importing phi.py to ask where Phase 1 is would defeat the point: this
    script has to work when that import is what fails.
    """
    env = os.environ.get("PHASE1_DIR")
    if env:
        return os.path.abspath(env)
    return os.path.join(REPO, "grammar_and_3DOM_client")


P1 = phase1_dir()

# (path, why it is needed, which lane needs it)
PHASE1_ARTIFACTS = [
    ("terminals.json",
     "the 43-terminal table φ is keyed on; every φ-map is validated against it"),
    ("tasks.py",
     "the C8 signature cross-check in src/canonicalize.py reads its _SIGNATURES"),
    ("ir_schema.json",
     "tests/test_isomorphism.py validates every IR against it"),
    ("3dom_grammar.iso.ebnf",
     "gate G-R4: the identity render must reproduce it byte-for-byte"),
    ("3dom_grammar.w3c.ebnf",
     "gate G-R4, and the |N|/|P| invariants I1/I2"),
    ("grammar_metrics.py",
     "invariants I1-I3 are measured with Phase 1's own instrument"),
    ("conformance/refgrammar.py",
     "the reference engine: parse counter, DFA, and the 57 coverage features"),
    ("conformance/positive.txt", "the 62-item positive corpus"),
    ("conformance/negative.txt", "the 64-item negative corpus"),
    ("conformance/vacuous.txt", "the 12-item valid-but-vacuous corpus (D5)"),
]

PHASE2_ARTIFACTS = [
    ("candidates/phi_alpha.json", "the interference lexicon"),
    ("candidates/phi_beta.json", "the pseudo-lexicon"),
    ("candidates/phi_gamma.json", "the glyph lexicon"),
    ("grammar/templates/grammar.lark.template",
     "the ONE executable grammar, rendered through φ at both levels"),
    ("grammar/templates/grammar.iso.template.ebnf", "normative appendix template"),
    ("grammar/templates/grammar.w3c.template.ebnf", "normative appendix template"),
    ("grammar/templates/grammar.diagram.template.md", "syntax-diagram template"),
    ("src/phi.py", "φ validation, application and inversion"),
    ("src/canonicalize.py", "the frozen canonical IR and C0-C9"),
    ("src/transpiler.py", "lexer, transliterator, Lark front end, emitter"),
    ("src/generate_corpus.py", "the alien corpora and gates A1-A7"),
]

STRUCTURAL_MODULES = [
    ("lark", "the Earley front end (clause P1). pip install 'lark==1.3.1'"),
]
OPTIONAL_MODULES = [
    ("jsonschema", "validates the IR against Phase 1's schema; without it "
                   "test_isomorphism falls back to a weaker structural check"),
]
MODEL_MODULES = [
    ("transformers", "AutoTokenizer for CONSTRAINT 1 fertility. "
                     "pip install transformers"),
    ("torch", "base-model forward passes for ΔNLL. pip install torch"),
]


def check_file(root: str, rel: str, why: str) -> dict:
    path = os.path.join(root, rel)
    ok = os.path.isfile(path)
    return {"kind": "file", "path": path, "ok": ok, "why": why,
            "size": os.path.getsize(path) if ok else 0}


def check_module(name: str, why: str) -> dict:
    try:
        found = importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):                          # pragma: no cover
        found = False
    version = ""
    if found:
        try:
            import importlib.metadata as md
            version = md.version(name)
        except Exception:                                      # pragma: no cover
            version = "?"
    return {"kind": "module", "path": name, "ok": found, "why": why,
            "version": version}


def run(model_lane: bool) -> tuple[list[dict], list[dict]]:
    required = [check_file(P1, rel, why) for rel, why in PHASE1_ARTIFACTS]
    required += [check_file(ALIEN, rel, why) for rel, why in PHASE2_ARTIFACTS]
    required += [check_module(m, why) for m, why in STRUCTURAL_MODULES]
    if model_lane:
        required += [check_module(m, why) for m, why in MODEL_MODULES]
    optional = [check_module(m, why) for m, why in OPTIONAL_MODULES]
    if not model_lane:
        optional += [check_module(m, why) for m, why in MODEL_MODULES]
    return required, optional


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", action="store_true",
                    help="also require transformers and torch")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv[1:])

    required, optional = run(args.model)
    missing = [c for c in required if not c["ok"]]

    if args.json:
        print(json.dumps({
            "phase1_dir": P1,
            "phase1_dir_source": "PHASE1_DIR" if os.environ.get("PHASE1_DIR")
                                 else "default (<repo>/grammar_and_3DOM_client)",
            "python": sys.version.split()[0],
            "lane": "model" if args.model else "structural",
            "required": required, "optional": optional,
            "ok": not missing,
        }, indent=2))
        return 1 if missing else 0

    print(f"preflight — lane: {'model-dependent' if args.model else 'structural'}")
    print(f"  python      {sys.version.split()[0]}")
    print(f"  repo        {REPO}")
    print(f"  PHASE1_DIR  {P1}")
    print(f"              ({'from $PHASE1_DIR' if os.environ.get('PHASE1_DIR') else 'default'})")
    if not os.path.isdir(P1):
        print(f"\nFATAL: the Phase 1 directory does not exist.\n"
              f"  Expected: {P1}\n"
              f"  Fix     : export PHASE1_DIR=/path/to/grammar_and_3DOM_client\n"
              f"  It must contain terminals.json, tasks.py, ir_schema.json, both\n"
              f"  frozen .ebnf grammars, grammar_metrics.py, and conformance/\n"
              f"  with refgrammar.py plus positive/negative/vacuous .txt.")
        return 1

    print("\nrequired:")
    for check in required:
        mark = "ok  " if check["ok"] else "MISS"
        extra = f" ({check['version']})" if check.get("version") else ""
        label = check["path"] if check["kind"] == "module" else \
            os.path.relpath(check["path"], REPO)
        print(f"  [{mark}] {label}{extra}")
    print("\noptional:")
    for check in optional:
        mark = "ok  " if check["ok"] else "--  "
        extra = f" ({check['version']})" if check.get("version") else ""
        print(f"  [{mark}] {check['path']}{extra}")
        if not check["ok"]:
            print(f"         {check['why']}")

    if missing:
        print(f"\nFAIL — {len(missing)} required item(s) missing:\n")
        for check in missing:
            label = check["path"] if check["kind"] == "module" else \
                os.path.relpath(check["path"], REPO)
            print(f"  {label}")
            print(f"      needed for: {check['why']}")
        print("\nNothing downstream will run correctly until these exist. Do NOT")
        print("create placeholder Phase 1 artifacts to get past this: the whole")
        print("isomorphism argument rests on Phase 1 being the frozen reference.")
        return 1

    print("\nPASS — every required artifact and dependency is present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
