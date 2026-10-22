"""run_tests.py — Phase 4 tests, run by the Phase 3.3 runner (same conventions, same
temporary results root, so a test can never touch real data).

    python3 phase4/tests/run_tests.py [pattern] [-v]
"""

from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOL_TESTS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "phase3_2", "sol", "tests")

spec = importlib.util.spec_from_file_location("run_tests", os.path.join(SOL_TESTS, "run_tests.py"))
runner = importlib.util.module_from_spec(spec)
sys.modules["run_tests"] = runner          # tests do `from run_tests import needs`
spec.loader.exec_module(runner)
runner.HERE = HERE                         # discover phase4/tests/test_*.py instead

if __name__ == "__main__":
    raise SystemExit(runner.main(sys.argv[1:]))
