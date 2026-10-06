"""run_tests.py — dependency-free runner for the Phase 3.3 Sol pipeline tests.

    python3 tests/run_tests.py            # everything
    python3 tests/run_tests.py kstar -v   # modules matching "kstar", verbose

Same convention as the Phase 3 / 3.2 runners (no pytest in this repository).

A test that needs an optional dependency (numpy, matplotlib) raises
`Blocked` when it is absent. Blocked tests are reported in their own column
and are NEVER counted as passed -- a missing dependency must stay visible, as
it did on Sol, where the shared env lacked `lark` (14 passed / 22 failed).

Exit code: 1 if any test failed, 5 if none failed but any was blocked, 0 only
when everything passed (a count would wrap to 0 at 256). With `--cpu-node`, a
test blocked only for want of a GPU (`Blocked(..., hardware=True)`) is still
listed as BLOCKED but does not set the exit code: the Sol CPU-tests job runs
on a CPU node by design, and the smoke job exercises the GPU path for real.
A missing DEPENDENCY always sets it.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
SOL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SOL, "src"))
sys.path.insert(0, HERE)

os.environ.setdefault("P33_RESULTS_ROOT", tempfile.mkdtemp(prefix="p33_test_results_"))


class Blocked(Exception):
    """A required dependency (or, with hardware=True, a device) is missing.
    Not a pass, not a fail."""

    def __init__(self, msg: str = "", *, hardware: bool = False):
        super().__init__(msg)
        self.hardware = hardware


# Tests do `from run_tests import Blocked`. When this file runs as __main__,
# that import would create a SECOND module with a DIFFERENT Blocked class, and
# a blocked test would be miscounted as a failure. Register under both names.
sys.modules.setdefault("run_tests", sys.modules[__name__])


def needs(*mods: str) -> None:
    for m in mods:
        if importlib.util.find_spec(m) is None:
            raise Blocked(f"missing dependency: {m}")


def load(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main(argv: list[str]) -> int:
    verbose = "-v" in argv
    cpu_node = "--cpu-node" in argv
    pats = [a for a in argv if not a.startswith("-")]
    files = sorted(f for f in os.listdir(HERE) if f.startswith("test_") and f.endswith(".py"))
    if pats:
        files = [f for f in files if any(p in f for p in pats)]
    passed = failed = blocked = expected_hw = 0
    fails, blocks = [], []
    for fname in files:
        print(f"\n=== {fname} ===")
        try:
            mod = load(os.path.join(HERE, fname))
        except Blocked as exc:
            blocked += 1
            blocks.append((fname, str(exc)))
            print(f"  BLOCKED (module): {exc}")
            continue
        except Exception:
            failed += 1
            fails.append((fname, "import"))
            traceback.print_exc()
            continue
        for tname in sorted(n for n in dir(mod) if n.startswith("test_")):
            fn = getattr(mod, tname)
            if not callable(fn):
                continue
            try:
                fn()
            except Blocked as exc:
                blocked += 1
                expected_hw += bool(cpu_node and getattr(exc, "hardware", False))
                blocks.append((f"{fname}::{tname}", str(exc)))
                print(f"  BLOCKED {tname}: {exc}")
            except Exception as exc:
                failed += 1
                fails.append((f"{fname}::{tname}", f"{type(exc).__name__}: {exc}"))
                print(f"  FAIL {tname}")
                for line in traceback.format_exc().strip().splitlines()[-5:]:
                    print(f"       {line}")
            else:
                passed += 1
                if verbose:
                    print(f"  ok   {tname}")
    print(f"\n{'-' * 58}\n{passed} passed, {failed} failed, {blocked} blocked")
    for name, why in fails:
        print(f"  FAIL    {name}\n          {why}")
    for name, why in blocks:
        print(f"  BLOCKED {name}: {why}")
    if expected_hw:
        print(f"  ({expected_hw} blocked for want of a GPU: expected with --cpu-node)")
    if failed:
        return 1
    return 5 if blocked - expected_hw else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
