"""vendor_sync.py — copy the Phase 1 / Phase 2 files Phase 3 depends on, and
record provenance for every one of them.

    python3 scripts/vendor_sync.py            # copy + write SOURCE_MANIFEST.md
    python3 scripts/vendor_sync.py --check    # verify nothing has drifted

WHY A SCRIPT AND NOT A `cp`
    Phase 3 must be reproducible and must never silently diverge from the code
    it was derived from. Every copied file is recorded with its ORIGINAL path,
    the git commit the repository was on, and the SHA-256 of the bytes that were
    copied. `--check` re-hashes both sides and reports drift, so a Phase 3 result
    can always be tied to an exact upstream state.

THE DIRECTORY NAMES UNDER vendor/ ARE LOad-BEARING
    `phi.phase1_dir()` falls back to `dirname(dirname(dirname(phi.py)))/
    grammar_and_3DOM_client`, and `phi.alien_dir()` to
    `dirname(dirname(phi.py))`. Mirroring the upstream directory NAMES under
    vendor/ therefore makes the vendored tree self-resolving: no $PHASE1_DIR,
    no sys.path surgery. Renaming these directories WILL break resolution.

NOTHING UPSTREAM IS WRITTEN. This script only reads from the repository root.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE3 = os.path.dirname(HERE)
REPO = os.path.dirname(PHASE3)
VENDOR = os.path.join(PHASE3, "vendor")


@dataclass(frozen=True)
class Item:
    src: str          # path relative to REPO
    dst: str          # path relative to VENDOR
    why: str          # why Phase 3 needs it
    modified: bool = False   # True => Phase 3 edits it after copying


# ---------------------------------------------------------------------------
# The copy set. Keep this list short and justified: every entry is a file whose
# upstream changes can silently change a Phase 3 result.
# ---------------------------------------------------------------------------
ITEMS: tuple[Item, ...] = (
    # --- the alien-syntax core: φ, parsing, IR, emission -------------------
    Item("alien_syntax/src/phi.py",
         "alien_syntax/src/phi.py",
         "φ-map loading/validation/inversion; defines the terminal table Phase 3 "
         "enumerates decision sites from."),
    Item("alien_syntax/src/canonicalize.py",
         "alien_syntax/src/canonicalize.py",
         "Canonical IR dataclasses, canonical JSON and content hash. Phase 3's "
         "semantic equality test is IR hash equality, so this IS the scorer."),
    Item("alien_syntax/src/transpiler.py",
         "alien_syntax/src/transpiler.py",
         "Lexer, Lark front end, transliterator, parse() and emit(). Phase 3 uses "
         "parse() for grammar-validity proofs and emit() to render prefixes."),
    Item("alien_syntax/src/heuristics_ir.py",
         "alien_syntax/src/heuristics_ir.py",
         "IR-building helpers used by the transformers."),
    Item("alien_syntax/src/generate_corpus.py",
         "alien_syntax/src/generate_corpus.py",
         "Paired positive/negative/vacuous corpora; Phase 3 reuses the paired "
         "program generator to build AST-matched templates."),

    # --- candidate φ-maps ---------------------------------------------------
    Item("alien_syntax/candidates/phi_alpha.json", "alien_syntax/candidates/phi_alpha.json",
         "alpha lexicon: familiar-looking spellings with reassigned meanings — the "
         "condition in which the observed `.`-for-`#` reversion occurred."),
    Item("alien_syntax/candidates/phi_beta.json", "alien_syntax/candidates/phi_beta.json",
         "beta lexicon: invented ASCII words; the novel-but-non-colliding arm."),
    Item("alien_syntax/candidates/phi_gamma.json", "alien_syntax/candidates/phi_gamma.json",
         "gamma lexicon: retained as a REPORTED lexer/Unicode stress condition only. "
         "Excluded from causal claims (lexical-reachability parity fails, g1/g2)."),

    # --- grammar templates --------------------------------------------------
    Item("alien_syntax/grammar/templates/grammar.iso.template.ebnf",
         "alien_syntax/grammar/templates/grammar.iso.template.ebnf",
         "ISO EBNF template; φ=identity must reproduce Phase 1 byte for byte."),
    Item("alien_syntax/grammar/templates/grammar.w3c.template.ebnf",
         "alien_syntax/grammar/templates/grammar.w3c.template.ebnf",
         "W3C EBNF template, same contract."),
    Item("alien_syntax/grammar/templates/grammar.lark.template",
         "alien_syntax/grammar/templates/grammar.lark.template",
         "Lark template: the executable recognizer Phase 3 parses with."),
    Item("alien_syntax/grammar/render_grammar.py",
         "alien_syntax/grammar/render_grammar.py",
         "template + φ -> grammar artifacts; Phase 3 renders grammars for new "
         "mapping rotations at build time."),

    # --- Phase 1 artifacts (directory name is load-bearing, see module docstring)
    Item("grammar_and_3DOM_client/terminals.json",
         "grammar_and_3DOM_client/terminals.json",
         "The frozen terminal inventory. Phase 3's decision-site enumeration is a "
         "function of this file; `substitutable` and `collisions` drive site choice."),
    Item("grammar_and_3DOM_client/ir_schema.json",
         "grammar_and_3DOM_client/ir_schema.json",
         "IR JSON schema; validates serialized IR in tests."),
    Item("grammar_and_3DOM_client/3dom_grammar.iso.ebnf",
         "grammar_and_3DOM_client/3dom_grammar.iso.ebnf",
         "Phase 1 reference grammar; render_grammar asserts byte equality against it."),
    Item("grammar_and_3DOM_client/3dom_grammar.w3c.ebnf",
         "grammar_and_3DOM_client/3dom_grammar.w3c.ebnf",
         "Phase 1 reference grammar, W3C flavour; same byte-equality assertion."),
    Item("grammar_and_3DOM_client/fixture_scene.py",
         "grammar_and_3DOM_client/fixture_scene.py",
         "Deterministic scene for selector-resolution scoring."),
    Item("grammar_and_3DOM_client/conformance/refgrammar.py",
         "grammar_and_3DOM_client/conformance/refgrammar.py",
         "HARD DEPENDENCY of transpiler.py (`import refgrammar as R`). The "
         "independent hand-written recognizer — seam #2 of the three-seam parity "
         "check. Without it Phase 3 cannot parse at all."),
    Item("grammar_and_3DOM_client/conformance/positive.txt",
         "grammar_and_3DOM_client/conformance/positive.txt",
         "Phase 1 positive corpus; generate_corpus.phase1_programs() reads it to "
         "build the AST-matched paired programs Phase 3 derives templates from."),
    Item("grammar_and_3DOM_client/conformance/negative.txt",
         "grammar_and_3DOM_client/conformance/negative.txt",
         "Phase 1 negative corpus; needed by generate_corpus for the paired build."),
    Item("grammar_and_3DOM_client/conformance/vacuous.txt",
         "grammar_and_3DOM_client/conformance/vacuous.txt",
         "Phase 1 valid-but-vacuous corpus (D5). Vacuous output is a PARSE SUCCESS "
         "and a TASK FAILURE; Phase 3's reach detector must distinguish it."),
    Item("grammar_and_3DOM_client/tasks.py",
         "grammar_and_3DOM_client/tasks.py",
         "Task scorers. MODIFIED IN PHASE 3: score_op_selection_report accepted "
         "extra trailing operations (prefix match, not exact match). See "
         "PATCHES/tasks.op_selection.md.",
         modified=True),
)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except Exception:                                   # pragma: no cover
        return "UNKNOWN"


def git_dirty(rel: str) -> bool:
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--", rel],
                             cwd=REPO, capture_output=True, text=True, check=True)
        return bool(out.stdout.strip())
    except Exception:                                   # pragma: no cover
        return False


def do_copy() -> list[dict]:
    rows = []
    for it in ITEMS:
        src = os.path.join(REPO, it.src)
        dst = os.path.join(VENDOR, it.dst)
        if not os.path.isfile(src):
            raise SystemExit(f"MISSING UPSTREAM FILE: {it.src}")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        rows.append({
            "src": it.src, "dst": "vendor/" + it.dst,
            "sha256": sha256(src), "why": it.why,
            "modified": it.modified, "dirty": git_dirty(it.src),
        })
    return rows


def do_check(rows_expected: dict[str, str]) -> int:
    """Re-hash upstream and report drift. Returns a process exit code."""
    bad = 0
    for it in ITEMS:
        src = os.path.join(REPO, it.src)
        if not os.path.isfile(src):
            print(f"GONE      {it.src}")
            bad += 1
            continue
        now = sha256(src)
        was = rows_expected.get(it.src)
        if was is None:
            print(f"UNRECORDED {it.src}")
            bad += 1
        elif now != was:
            print(f"DRIFTED   {it.src}\n            manifest {was[:16]}…  now {now[:16]}…")
            bad += 1
    print(f"\n{len(ITEMS) - bad}/{len(ITEMS)} vendored files match the manifest.")
    return 1 if bad else 0


MANIFEST_HEADER = """# SOURCE_MANIFEST.md

Provenance for every file Phase 3 copied out of Phase 1 / Phase 2.

Generated by `scripts/vendor_sync.py`. Re-run with `--check` to detect drift
between these copies and the upstream originals.

- **Repository commit at copy time:** `{commit}`
- **Files copied:** {n}
- **`dirty`** means the upstream file had uncommitted changes when it was copied,
  so the commit hash alone does not identify its contents — trust the SHA-256.

> The directory names under `vendor/` are load-bearing. `phi.phase1_dir()` and
> `phi.alien_dir()` resolve by walking *up* from `phi.py`, so mirroring the
> upstream directory names makes the vendored tree self-resolving with no
> `$PHASE1_DIR` and no `sys.path` surgery. Do not rename them.

| # | Phase 3 destination | Original source | SHA-256 (at copy) | State | Why Phase 3 needs it |
|---|---|---|---|---|---|
"""

DIVERGENCE_NOTE = """
## Divergence risk

Every file above is a **copy**. Upstream fixes do not propagate automatically.

- `scripts/vendor_sync.py --check` re-hashes the originals and reports drift.
  Run it before any result you intend to report.
- One file is **modified** after copying (`tasks.py`). Re-running
  `vendor_sync.py` overwrites that edit — the patch must be re-applied. The patch
  and its rationale live in `PATCHES/tasks.op_selection.md`, and
  `tests/test_scorer_repair.py` fails loudly if the repair is absent, so an
  un-re-applied patch cannot reach a result silently.
"""


def write_manifest(rows: list[dict]) -> str:
    commit = git_commit()
    out = [MANIFEST_HEADER.format(commit=commit, n=len(rows))]
    for i, r in enumerate(rows, 1):
        state = "**MODIFIED**" if r["modified"] else "unchanged"
        if r["dirty"]:
            state += " · dirty"
        out.append(f"| {i} | `{r['dst']}` | `{r['src']}` | `{r['sha256'][:32]}…` "
                   f"| {state} | {r['why']} |")
    out.append(DIVERGENCE_NOTE)
    return "\n".join(out) + "\n"


def parse_manifest(path: str) -> dict[str, str]:
    """Recover src -> sha256 from a previously written manifest."""
    rows: dict[str, str] = {}
    if not os.path.isfile(path):
        return rows
    for line in open(path, encoding="utf-8"):
        if not line.startswith("| ") or "`" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        src, sha = cells[2].strip("`"), cells[3].strip("`").rstrip("…")
        if sha and all(c in "0123456789abcdef" for c in sha):
            rows[src] = sha
    return rows


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="verify vendored copies against upstream; do not copy")
    args = ap.parse_args(argv)

    manifest_path = os.path.join(PHASE3, "SOURCE_MANIFEST.md")

    if args.check:
        recorded = parse_manifest(manifest_path)
        # stored hashes are truncated to 32 chars in the table
        return do_check({k: v for k, v in recorded.items()}) if not recorded else _check_trunc(recorded)

    rows = do_copy()
    with open(manifest_path, "w", encoding="utf-8") as fh:
        fh.write(write_manifest(rows))
    print(f"copied {len(rows)} files -> {VENDOR}")
    print(f"wrote  {manifest_path}")
    dirty = [r["src"] for r in rows if r["dirty"]]
    if dirty:
        print(f"NOTE: {len(dirty)} upstream file(s) had uncommitted changes:")
        for d in dirty:
            print(f"  - {d}")
    return 0


def _check_trunc(recorded: dict[str, str]) -> int:
    bad = 0
    for it in ITEMS:
        src = os.path.join(REPO, it.src)
        if not os.path.isfile(src):
            print(f"GONE       {it.src}")
            bad += 1
            continue
        now = sha256(src)
        was = recorded.get(it.src)
        if was is None:
            print(f"UNRECORDED {it.src}")
            bad += 1
        elif not now.startswith(was):
            print(f"DRIFTED    {it.src}\n             manifest {was[:16]}…  now {now[:16]}…")
            bad += 1
    print(f"\n{len(ITEMS) - bad}/{len(ITEMS)} vendored files match the manifest.")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
