"""p33 — the Phase 3.3 Sol pipeline.

Layered on `phase3_2` (materials, canonical scorer, sampling, analysis) and,
through it, on `phase3` and the vendored Phase 1/2 tree. Import order matters:
`p33._paths` puts `phase3_2/src` on sys.path, and `phase3_2._vendor` then
wires everything beneath it.
"""

from p33 import _paths  # noqa: F401  (side-effecting: sys.path)

SCHEMA_VERSION = "p33/1"
