"""run_tests.py — dependency-free test runner.

    python3 tests/run_tests.py             # everything
    python3 tests/run_tests.py sites       # only modules matching "sites"
    python3 tests/run_tests.py -v          # show each test name

There is no pytest in this repository and the Phase 1 / Phase 2 suites are
plain assert scripts run directly (`python3 tests/test_isomorphism.py`). Phase 3
keeps that convention: the tests must run on a bare interpreter with lark and
nothing else, because the machine that checks them is not always the machine
that has the models.

Discovery is `test_*` module -> `test_*` zero-argument function. A test passes
if it returns without raising. Failures print the assertion and a short
traceback, and the process exit code is the failure count.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE3 = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PHASE3, "src"))


def load(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main(argv: list[str]) -> int:
    verbose = "-v" in argv
    pats = [a for a in argv if not a.startswith("-")]

    files = sorted(f for f in os.listdir(HERE)
                   if f.startswith("test_") and f.endswith(".py"))
    if pats:
        files = [f for f in files if any(p in f for p in pats)]

    passed = failed = 0
    failures: list[tuple[str, str]] = []

    for fname in files:
        print(f"\n=== {fname} ===")
        try:
            mod = load(os.path.join(HERE, fname))
        except Exception:
            print(f"  MODULE IMPORT FAILED")
            traceback.print_exc()
            failed += 1
            failures.append((fname, "import"))
            continue

        for tname in sorted(n for n in dir(mod) if n.startswith("test_")):
            fn = getattr(mod, tname)
            if not callable(fn):
                continue
            try:
                fn()
            except Exception as exc:
                failed += 1
                failures.append((f"{fname}::{tname}", f"{type(exc).__name__}: {exc}"))
                print(f"  FAIL {tname}")
                tb = traceback.format_exc().strip().splitlines()
                for line in tb[-4:]:
                    print(f"       {line}")
            else:
                passed += 1
                if verbose:
                    print(f"  ok   {tname}")

    print(f"\n{'-'*58}\n{passed} passed, {failed} failed")
    if failures:
        print("\nfailures:")
        for name, why in failures:
            print(f"  {name}\n      {why}")
    return failed


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
