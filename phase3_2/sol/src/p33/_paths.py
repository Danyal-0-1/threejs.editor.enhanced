"""_paths.py — locate the repository pieces p33 depends on.

    phase3_2/sol/src/p33/_paths.py
                 ^^^ SOL_ROOT      phase3_2/sol
         ^^^^^^^^ PHASE3_2_ROOT    phase3_2
"""

from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))           # …/sol/src/p33
SOL_ROOT = os.path.dirname(os.path.dirname(_HERE))           # …/phase3_2/sol
PHASE3_2_ROOT = os.path.dirname(SOL_ROOT)                    # …/phase3_2
REPO_ROOT = os.path.dirname(PHASE3_2_ROOT)
PHASE3_2_SRC = os.path.join(PHASE3_2_ROOT, "src")
P33_SRC = os.path.dirname(_HERE)

for _p in (P33_SRC, PHASE3_2_SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from phase3_2 import _vendor  # noqa: E402,F401  (wires phase3 + vendor)
