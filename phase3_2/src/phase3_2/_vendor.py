"""_vendor.py — the ONE place Phase 3.2 wires its dependencies onto sys.path.

DECLARED EXTERNAL DEPENDENCY (the brief forbids *silent* ones)
--------------------------------------------------------------
Phase 3.2 deliberately does NOT re-vendor the 4,380 lines of Phase 1/2 code
that Phase 3 already copied. It reads them from `phase3/vendor/`, and it
imports Phase 3's own modules (`scoring`, `outcomes`, `linter`) directly.

    phase3_2  ──depends on──►  phase3/src/phase3/*      (scoring, outcomes, linter)
                           └─►  phase3/vendor/*          (phi, transpiler, canonicalize, tasks)

Why, and what it costs:

  * Re-copying would double the drift surface. There would be two copies of
    `tasks.py`, each needing the P3-001 repair re-applied, and
    `vendor_sync.py --check` could pass on one while the other rotted.
  * Phase 3.2 is a SUCCESSOR, not an isolated replication. Its whole point is
    to change the materials while holding the measurement code fixed, so
    sharing `scoring.py`/`outcomes.py`/`linter.py` is the scientific design,
    not a shortcut: a difference in results cannot come from a changed scorer.
  * The cost is that Phase 3.2 is not independently relocatable. Moving it
    without `phase3/` breaks it loudly (see the checks below), never silently.

`assert_self_contained()` additionally proves that the vendored modules still
resolve their DATA inside `phase3/vendor/`, so nothing reads the live upstream
Phase 1 tree at runtime.
"""

from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))              # …/src/phase3_2
PHASE3_2_ROOT = os.path.dirname(os.path.dirname(_HERE))         # …/phase3_2
REPO = os.path.dirname(PHASE3_2_ROOT)
PHASE3_ROOT = os.path.join(REPO, "phase3")

PHASE3_SRC = os.path.join(PHASE3_ROOT, "src")
VENDOR = os.path.join(PHASE3_ROOT, "vendor")
ALIEN_SRC = os.path.join(VENDOR, "alien_syntax", "src")
PHASE1 = os.path.join(VENDOR, "grammar_and_3DOM_client")
PHASE1_CONF = os.path.join(PHASE1, "conformance")

OUTPUTS = os.path.join(PHASE3_2_ROOT, "outputs")
GRAMMARS = os.path.join(PHASE3_2_ROOT, "grammars")
CANDIDATES = os.path.join(VENDOR, "alien_syntax", "candidates")

_REQUIRED = (
    (PHASE3_ROOT, "Phase 3 is missing. Phase 3.2 builds on it; see the module "
                  "docstring. Expected it at ../phase3 relative to phase3_2/."),
    (PHASE3_SRC, "phase3/src not found — Phase 3.2 imports phase3.scoring, "
                 "phase3.outcomes and phase3.linter unchanged, on purpose."),
    (ALIEN_SRC, "phase3/vendor not populated. Run: "
                "python3 phase3/scripts/vendor_sync.py"),
    (PHASE1, "phase3/vendor/grammar_and_3DOM_client missing — see above."),
)

for _p, _msg in _REQUIRED:
    if not os.path.isdir(_p):
        raise RuntimeError(f"missing dependency: {_p}\n  {_msg}")

for _p in (PHASE3_SRC, ALIEN_SRC, PHASE1, PHASE1_CONF):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def assert_self_contained() -> None:
    """Prove the vendored modules resolve their data inside phase3/vendor/.

    Same guard as Phase 3's. If it fires, Phase 3.2 is reading Phase 1 data
    from the live upstream tree and any result is tied to whatever state that
    tree happened to be in.
    """
    import phi

    for name, got in (("phase1_dir", phi.phase1_dir()),
                      ("alien_dir", phi.alien_dir()),
                      ("candidates_dir", phi.candidates_dir())):
        real = os.path.realpath(got)
        if not real.startswith(os.path.realpath(VENDOR)):
            raise RuntimeError(
                f"phi.{name}() resolved OUTSIDE phase3/vendor:\n"
                f"  got {real}\n  wanted under {os.path.realpath(VENDOR)}")


def assert_scorer_repaired() -> None:
    """Phase 3.2 inherits the P3-001 repair. Verify it is still applied.

    Phase 3.2 shares Phase 3's `tasks.py`, so a `vendor_sync.py` re-run in
    phase3/ would silently restore the defect HERE too. This check makes that
    impossible to miss from either phase.
    """
    text = open(os.path.join(PHASE1, "tasks.py"), encoding="utf-8").read()
    if "PHASE 3 REPAIR (P3-001)" not in text or "if len(ops) != len(wanted):" not in text:
        raise RuntimeError(
            "the P3-001 scorer repair is MISSING from phase3/vendor/"
            "grammar_and_3DOM_client/tasks.py. Re-apply "
            "phase3/PATCHES/tasks.op_selection.md before trusting any result.")
