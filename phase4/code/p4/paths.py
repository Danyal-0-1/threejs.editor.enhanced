"""paths.py — the ONE place that knows where everything is.

Phase 3.3 needed three modules for this (`p33/_paths.py`, `phase3_2/_vendor.py` and
`phase3/_vendor.py`), because its code sat in three phase folders that found each other by
position. Here everything is under `phase4/code/`, so one module does it:

    phase4/code/                  CODE_ROOT
    ├── run.py                    CLI            the one command-line entry point
    ├── p4/                       PACKAGE        the pipeline, one folder per stage
    ├── configs/                  CONFIGS        what a run scores: models, lexicons, families
    ├── dsl/                      DSL (VENDOR)   the language library and its data files
    │   ├── alien_syntax/src/     ALIEN_SRC      phi, transpiler, canonicalize, generate_corpus
    │   ├── alien_syntax/candidates/  CANDIDATES the lexicons (phi_*.json)
    │   └── grammar_and_3DOM_client/  PHASE1     grammar, terminals, task scorers
    │       └── conformance/      PHASE1_CONF    the reference grammar and its test programs
    └── sol/                      SOL_ROOT       running on ASU Sol: jobs, environment, submit scripts

The language library is not a package: its modules import each other by bare name
(`import phi`), and `phi.py` finds its data from its own location (the folder names under dsl/
are load-bearing). So, as in Phase 3.3, its three source folders go on sys.path, here, once.

PREREGISTRATION is Phase 4's own: `phase4/PREREGISTRATION.md`, read by governance/freeze.py
and reporting/reports.py. The freeze refuses while it is still a draft. PHASE3_2_ROOT is where
Phase 3.2's preregistration lives, the design Phase 3.3 ran: the tests use it to check the
machinery against Phase 3.3's registered facts (tests/phase3_3_design.py).
"""

from __future__ import annotations

import os
import sys

PACKAGE = os.path.dirname(os.path.abspath(__file__))           # …/phase4/code/p4
CODE_ROOT = os.path.dirname(PACKAGE)                           # …/phase4/code
REPO_ROOT = os.path.dirname(os.path.dirname(CODE_ROOT))        # the repository
CLI = os.path.join(CODE_ROOT, "run.py")
CONFIGS = os.path.join(CODE_ROOT, "configs")
SOL_ROOT = os.path.join(CODE_ROOT, "sol")
PREREGISTRATION = os.path.join(REPO_ROOT, "phase4", "PREREGISTRATION.md")   # Phase 4's own
PHASE3_2_ROOT = os.path.join(REPO_ROOT, "phase3_2")            # Phase 3.2's, for the tests

DSL = os.path.join(CODE_ROOT, "dsl")
VENDOR = DSL                                                   # the name Phase 3 and 3.2 used
ALIEN_SRC = os.path.join(DSL, "alien_syntax", "src")
CANDIDATES = os.path.join(DSL, "alien_syntax", "candidates")
PHASE1 = os.path.join(DSL, "grammar_and_3DOM_client")
PHASE1_CONF = os.path.join(PHASE1, "conformance")
PATCHES = os.path.join(DSL, "PATCHES")

for _p in (ALIEN_SRC, PHASE1, PHASE1_CONF):
    if not os.path.isdir(_p):
        raise RuntimeError(f"missing language folder: {_p}\n"
                           f"phase4/code/dsl/ must hold the language library (see dsl/README.md)")
    if _p not in sys.path:
        sys.path.insert(0, _p)


def assert_self_contained() -> None:
    """Prove the language modules resolve their data inside dsl/.

    If this fires, the pipeline is reading language files from somewhere else (for example the
    original `phase3/vendor/`, or `$PHASE1_DIR`), and a result would depend on that tree.
    """
    import phi

    for name, got in (("phase1_dir", phi.phase1_dir()),
                      ("alien_dir", phi.alien_dir()),
                      ("candidates_dir", phi.candidates_dir())):
        real = os.path.realpath(got)
        if not real.startswith(os.path.realpath(DSL)):
            raise RuntimeError(
                f"phi.{name}() resolved OUTSIDE phase4/code/dsl:\n"
                f"  got {real}\n  wanted under {os.path.realpath(DSL)}")


def assert_scorer_repaired() -> None:
    """The P3-001 repair of the task scorer must be in dsl/.../tasks.py.

    Phase 3 found that `tasks.py` scored op-selection wrongly and patched it
    (dsl/PATCHES/tasks.op_selection.md). A copy taken from an unpatched upstream would bring the
    defect back silently; this check makes that impossible to miss.
    """
    text = open(os.path.join(PHASE1, "tasks.py"), encoding="utf-8").read()
    if "PHASE 3 REPAIR (P3-001)" not in text or "if len(ops) != len(wanted):" not in text:
        raise RuntimeError(
            "the P3-001 scorer repair is MISSING from phase4/code/dsl/"
            "grammar_and_3DOM_client/tasks.py. Re-apply "
            "dsl/PATCHES/tasks.op_selection.md before trusting any result.")
