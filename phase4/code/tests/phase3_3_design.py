"""phase3_3_design.py — Phase 3.3's registered design, for the tests and the comparison tool.

The copied tests check the split and freeze machinery against facts Phase 3.3 registered: its
split (with deviations D1, D2 and D10), its preregistration (phase3_2/PREREGISTRATION.md) and
its schema label. Those facts are known and fixed, so they make good test data.

  * run_tests.py installs this design before any test runs;
  * tests/test_phase4_design.py takes it off again, to check Phase 4's own design;
  * tools/compare_with_phase3_3.py installs it (with the schema label), so that the copy runs
    exactly the design the Phase 3.3 pipeline runs, and any difference in their outputs comes
    from the code.

A run never uses it: nothing in p4/ imports this file.
"""

from __future__ import annotations

import contextlib
import os

import p4
from p4 import paths
from p4.governance import splits

# The constants of phase3_2/sol/src/p33/splits.py, exactly
# (test_phase4_design.py checks them against that file).
SPLIT = {
    "DEV_FAMILIES": frozenset({"dom"}),
    "DEV_LEXICONS": frozenset({"d25s1", "d25s2", "d50s1", "d50s2"}),
    "HELDOUT_LEXICONS": frozenset({"d25s3", "d50s3", "d75s1a", "d75s2a", "d75s3a"}),
    "DEV_MODELS": frozenset({
        "Qwen/Qwen2.5-Coder-0.5B", "Qwen/Qwen2.5-Coder-0.5B-Instruct",
        "Qwen/Qwen2.5-Coder-1.5B", "Qwen/Qwen2.5-Coder-1.5B-Instruct"}),
    "CONTAMINATED_FAMILIES": {
        "blk": "scored before the freeze (Phase 3.2 balanced Arm A and Phase 3.3 "
               "primary run, blk x d50s1); not an unseen grammar family"},
    "PREVIOUSLY_OBSERVED_MODELS": {
        "Qwen/Qwen2.5-Coder-3B": "observed under a superseded protocol before the "
                                 "freeze (arm_a_sizes.json: dom only, no rule table)",
        "Qwen/Qwen2.5-Coder-3B-Instruct": "as above"},
    "APPROVED_NEW_FAMILIES": frozenset(),
    "KNOWN_FAMILIES": frozenset({"dom", "blk"}),
    "MAX_SIZE_B": 72.0,
}
PREREGISTRATION = os.path.join(paths.PHASE3_2_ROOT, "PREREGISTRATION.md")
SCHEMA_VERSION = "p33/1"
_SCHEMA_HOLDERS = ("p4", "p4.experiments.pipeline", "p4.governance.provenance")

_saved: dict | None = None


def _modules():
    import importlib
    return [importlib.import_module(m) for m in _SCHEMA_HOLDERS]


def install(*, schema: bool = False) -> None:
    """Put Phase 3.3's design in place of Phase 4's (for tests and the comparison tool)."""
    global _saved
    if _saved is not None:
        return
    _saved = {"split": {k: getattr(splits, k) for k in SPLIT},
              "prereg": paths.PREREGISTRATION,
              "schema": {m.__name__: m.SCHEMA_VERSION for m in _modules()} if schema else None}
    for k, v in SPLIT.items():
        setattr(splits, k, v)
    paths.PREREGISTRATION = PREREGISTRATION
    if schema:
        for m in _modules():
            m.SCHEMA_VERSION = SCHEMA_VERSION


def remove() -> None:
    """Put Phase 4's own design back."""
    global _saved
    if _saved is None:
        return
    for k, v in _saved["split"].items():
        setattr(splits, k, v)
    paths.PREREGISTRATION = _saved["prereg"]
    if _saved["schema"]:
        for m in _modules():
            m.SCHEMA_VERSION = _saved["schema"][m.__name__]
    _saved = None


@contextlib.contextmanager
def phase4_design():
    """Run a block under Phase 4's own design, then reinstall Phase 3.3's if it was installed."""
    was = _saved is not None
    schema = bool(was and _saved["schema"])
    remove()
    try:
        yield
    finally:
        if was:
            install(schema=schema)

