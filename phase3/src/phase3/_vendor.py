"""_vendor.py — the ONE place Phase 3 puts the vendored tree on sys.path.

Import this before any vendored module. Nothing else in Phase 3 touches
`sys.path`, so there is exactly one answer to "where did `phi` come from?".

    from phase3 import _vendor          # noqa: F401  (side-effecting import)
    import phi, transpiler, canonicalize

WHY NOT A PACKAGE IMPORT
    The vendored modules import each other FLATLY (`from phi import ...`,
    `import refgrammar as R`) and resolve their data files by walking up from
    `__file__`. Re-packaging them as `phase3.vendor.phi` would require editing
    every import in 5,000+ lines of copied code, and each edit is a place the
    copy can silently diverge from the original. Keeping the copies byte-exact
    and adjusting sys.path instead means `vendor_sync.py --check` stays a
    meaningful drift test.

WHAT IS ON THE PATH, AND WHY
    vendor/alien_syntax/src        phi, canonicalize, transpiler, heuristics_ir,
                                   generate_corpus
    vendor/grammar_and_3DOM_client            tasks, fixture_scene
    vendor/grammar_and_3DOM_client/conformance  refgrammar  (transpiler needs it)

PATH RESOLUTION IS POSITIONAL, NOT CONFIGURED
    `phi.phase1_dir()` walks up three levels from `phi.py` and appends
    "grammar_and_3DOM_client"; `phi.alien_dir()` walks up two. Because
    vendor/ mirrors the upstream directory NAMES, both land inside vendor/.
    Phase 3 therefore reads NO file from the upstream tree at runtime. The
    assertion at the bottom of this module enforces that, so a renamed vendor
    directory fails here instead of silently reading upstream Phase 1 data and
    producing results that cannot be reproduced.
"""

from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))              # …/src/phase3
PHASE3_ROOT = os.path.dirname(os.path.dirname(_HERE))           # …/phase3
VENDOR = os.path.join(PHASE3_ROOT, "vendor")

ALIEN_SRC = os.path.join(VENDOR, "alien_syntax", "src")
PHASE1 = os.path.join(VENDOR, "grammar_and_3DOM_client")
PHASE1_CONF = os.path.join(PHASE1, "conformance")

OUTPUTS = os.path.join(PHASE3_ROOT, "outputs")

for _p in (ALIEN_SRC, PHASE1, PHASE1_CONF):
    if not os.path.isdir(_p):
        raise RuntimeError(
            f"vendored directory missing: {_p}\n"
            f"Run:  python3 {os.path.join(PHASE3_ROOT, 'scripts', 'vendor_sync.py')}")
    if _p not in sys.path:
        sys.path.insert(0, _p)


def assert_self_contained() -> None:
    """Fail if a vendored module resolves its data outside phase3/vendor/.

    This is the guard that makes the vendored tree trustworthy. If it ever
    fires, Phase 3 is reading Phase 1 data from the live upstream tree, and any
    result produced is tied to whatever state that tree happened to be in.
    """
    import phi

    for name, got in (("phase1_dir", phi.phase1_dir()),
                      ("alien_dir", phi.alien_dir()),
                      ("candidates_dir", phi.candidates_dir())):
        real = os.path.realpath(got)
        if not real.startswith(os.path.realpath(VENDOR)):
            raise RuntimeError(
                f"phi.{name}() resolved OUTSIDE the vendored tree:\n"
                f"  got    {real}\n  wanted under {os.path.realpath(VENDOR)}\n"
                f"Phase 3 would be reading upstream Phase 1 data. Check that "
                f"vendor/ still mirrors the upstream directory names.")
