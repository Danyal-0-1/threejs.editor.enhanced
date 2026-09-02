"""test_preflight.py — the failure mode a fresh clone actually hits.

Phase 2 reaches into Phase 1 for terminals.json, refgrammar.py, the frozen
grammars, the IR schema and the three corpora. The interesting question is not
"does it work when everything is present" — every other suite answers that — but
"what does it SAY when something is missing".

The answer must name the missing path. A ModuleNotFoundError raised three
imports deep inside transpiler.py tells a new user nothing about the fact that
$PHASE1_DIR points at the wrong directory.

Each test runs a real subprocess with a poisoned environment, because that is
the only way to observe import-time behaviour honestly.

Run standalone (`python3 tests/test_preflight.py`) or under pytest.
"""

from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
REPO = os.path.dirname(ALIEN)
PREFLIGHT = os.path.join(REPO, "run", "preflight.py")


def _run(args: list[str], env_extra: dict[str, str] | None = None):
    env = dict(os.environ)
    env.pop("PHASE1_DIR", None)
    env.update(env_extra or {})
    return subprocess.run([sys.executable] + args, capture_output=True,
                          text=True, env=env, cwd=REPO)


def test_preflight_passes_on_this_checkout() -> None:
    out = _run([PREFLIGHT])
    assert out.returncode == 0, \
        f"preflight failed on a complete checkout:\n{out.stdout}\n{out.stderr}"
    assert "PASS" in out.stdout


def test_preflight_reports_a_missing_phase1_directory_by_path() -> None:
    out = _run([PREFLIGHT], {"PHASE1_DIR": "/nonexistent/phase1"})
    assert out.returncode != 0, "preflight passed with no Phase 1 directory"
    assert "/nonexistent/phase1" in out.stdout, \
        f"the message does not name the path it looked in:\n{out.stdout}"
    assert "PHASE1_DIR" in out.stdout, \
        "the message does not say which variable to set"


def test_preflight_names_each_missing_artifact_and_its_purpose() -> None:
    """Point PHASE1_DIR at a directory that EXISTS but is empty: every Phase 1
    artifact must be listed individually, with what it is needed for."""
    import tempfile
    with tempfile.TemporaryDirectory() as empty:
        out = _run([PREFLIGHT], {"PHASE1_DIR": empty})
        assert out.returncode != 0, "preflight passed against an empty Phase 1"
        for artifact in ("terminals.json", "refgrammar.py", "ir_schema.json",
                         "positive.txt", "3dom_grammar.w3c.ebnf"):
            assert artifact in out.stdout, \
                f"{artifact} was not reported as missing:\n{out.stdout}"
        assert "needed for:" in out.stdout, \
            "missing artifacts are listed without saying what needs them"
        assert "placeholder" in out.stdout.lower(), (
            "the message does not warn against fabricating Phase 1 artifacts "
            "to get past the check")


def test_preflight_does_not_import_phase2() -> None:
    """It has to work when the import IS the problem, so it must not depend on
    src/phi.py to find out where Phase 1 lives."""
    with open(PREFLIGHT, encoding="utf-8") as fh:
        source = fh.read()
    for forbidden in ("import phi", "from phi ", "import transpiler",
                      "import canonicalize", "import refgrammar"):
        assert forbidden not in source, \
            f"preflight.py contains {forbidden!r}; it cannot diagnose an import " \
            f"failure it is itself subject to"


def test_preflight_model_lane_requires_transformers_and_torch() -> None:
    out = _run([PREFLIGHT, "--model", "--json"])
    import json
    blob = json.loads(out.stdout)
    required = {c["path"] for c in blob["required"] if c["kind"] == "module"}
    assert {"transformers", "torch"} <= required, \
        f"the model lane does not require transformers and torch: {required}"
    structural = json.loads(_run([PREFLIGHT, "--json"]).stdout)
    structural_required = {c["path"] for c in structural["required"]
                           if c["kind"] == "module"}
    assert "torch" not in structural_required, \
        "the structural lane requires torch; it must run with no models"
    assert "lark" in structural_required, \
        "the structural lane does not require lark"


def test_phase1_dir_default_matches_the_implementation() -> None:
    """preflight duplicates phi.phase1_dir() deliberately. Duplicated logic
    drifts, so the two must be asserted equal rather than assumed equal."""
    sys.path.insert(0, os.path.join(ALIEN, "src"))
    from phi import phase1_dir
    import json
    blob = json.loads(_run([PREFLIGHT, "--json"]).stdout)
    env = dict(os.environ)
    env.pop("PHASE1_DIR", None)
    expected = phase1_dir() if "PHASE1_DIR" not in os.environ else None
    if expected is not None:
        assert os.path.realpath(blob["phase1_dir"]) == os.path.realpath(expected), (
            f"preflight resolves Phase 1 to {blob['phase1_dir']!r} but "
            f"phi.phase1_dir() resolves it to {expected!r}; the duplicated "
            f"resolution has drifted")


def test_canonicalize_records_a_skipped_phase1_signature_check() -> None:
    """If Phase 1's tasks.py is absent the C8 cross-check cannot run. That must
    be RECORDED, not silently swallowed — a check that quietly did not happen
    reads exactly like a check that passed."""
    import tempfile
    with tempfile.TemporaryDirectory() as empty:
        # terminals.json is still needed to import at all, so copy just that
        import shutil
        src = os.path.join(REPO, "grammar_and_3DOM_client")
        shutil.copy(os.path.join(src, "terminals.json"), empty)
        script = (
            "import sys; sys.path.insert(0, %r)\n"
            "import canonicalize as C\n"
            "print('SKIPPED' if C.PHASE1_SIGNATURE_CHECK_SKIPPED else 'RAN')\n"
            "print(C.PHASE1_SIGNATURE_CHECK_SKIPPED or '')\n"
            % os.path.join(ALIEN, "src")
        )
        out = _run(["-c", script], {"PHASE1_DIR": empty})
        assert out.returncode == 0, f"import failed outright:\n{out.stderr[-600:]}"
        assert "SKIPPED" in out.stdout, (
            "canonicalize did not record that the Phase 1 signature check was "
            f"skipped:\n{out.stdout}")
        assert "tasks.py" in out.stdout, \
            f"the recorded reason does not name what was missing:\n{out.stdout}"

    # and on a complete checkout it must actually RUN
    script = ("import sys; sys.path.insert(0, %r)\n"
              "import canonicalize as C\n"
              "print('SKIPPED' if C.PHASE1_SIGNATURE_CHECK_SKIPPED else 'RAN')\n"
              % os.path.join(ALIEN, "src"))
    out = _run(["-c", script])
    assert "RAN" in out.stdout, (
        "the C8 signature cross-check did not run on a complete checkout; it "
        f"is being skipped silently:\n{out.stdout}")


def main() -> int:
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as exc:
            failures += 1
            print(f"  FAIL  {name}\n        {exc}")
        except Exception as exc:
            failures += 1
            print(f"  ERROR {name}\n        {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    print("test_preflight — 3dom-grammar/1.1.0")
    raise SystemExit(main())
