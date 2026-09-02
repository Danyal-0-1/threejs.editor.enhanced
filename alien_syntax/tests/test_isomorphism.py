"""test_isomorphism.py — the contract, checked item by item.

    for x in positive_corpus:
        assert ir(parse_alien(phi(x))) == ir(parse_3dom(x))

Equality is on CANONICAL CONTENT HASHES (canonicalize.C7), never on dict
equality over unsorted structures: compound-selector matchers are semantically
order-independent, so an unsorted comparison would be strict where the language
is not and would fail on `.wheel.front` vs `.front.wheel`.

Run standalone (`python3 tests/test_isomorphism.py`) or under pytest.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))

from canonicalize import canonical_json, content_hash  # noqa: E402
from phi import identity_phi, load_candidate  # noqa: E402
from transpiler import parse, phi_forward  # noqa: E402
import generate_corpus as G  # noqa: E402

CANDIDATES = ("alpha", "beta", "gamma")


def _corpus():
    return G.phase1_programs("positive", identity_phi())


def test_ir_identity_over_positive_corpus() -> None:
    ident = identity_phi()
    programs = _corpus()
    assert programs, "positive corpus is empty"
    for name in CANDIDATES:
        phi = load_candidate(name)
        for x in programs:
            alien = phi_forward(x, phi)
            got = parse(alien, phi)
            want = parse(x, ident)
            # A bare "hash mismatch" is unactionable: the digests are the LAST
            # step, so the message has to carry everything needed to find where
            # the two pipelines diverged — both surfaces AND both canonical
            # JSONs, so a reader can diff the IR without re-running anything.
            assert content_hash(got) == content_hash(want), (
                f"\n[{name}] IR content hashes differ.\n"
                f"  candidate      : {name}\n"
                f"  3DOM program   : {x!r}\n"
                f"  alien program  : {alien!r}\n"
                f"  3DOM canonical : {canonical_json(want)}\n"
                f"  alien canonical: {canonical_json(got)}\n"
                f"  3DOM digest    : {content_hash(want)}\n"
                f"  alien digest   : {content_hash(got)}\n"
                f"  NOTE: the digest is the operational WITNESS, not the "
                f"theorem. A mismatch localises to the first differing field "
                f"of the two canonical JSONs above.")


def test_ir_identity_over_vacuous_corpus() -> None:
    """D5: a vacuous chain must lower to the SAME empty op list in both."""
    ident = identity_phi()
    for name in CANDIDATES:
        phi = load_candidate(name)
        for x in G.phase1_programs("vacuous", ident):
            alien = phi_forward(x, phi)
            got, want = parse(alien, phi), parse(x, ident)
            assert content_hash(got) == content_hash(want), \
                f"[{name}] vacuous IR differs for {x!r}"
            assert got.ops == (), f"[{name}] vacuous item produced operations"


def test_negatives_stay_negative() -> None:
    """Generating the negative corpus by φ IS an isomorphism check: a 3DOM
    near-miss that stopped being a near-miss would mean φ moved structure."""
    ident = identity_phi()
    for name in CANDIDATES:
        phi = load_candidate(name)
        for x in G.phase1_programs("negative", ident):
            from transpiler import num_parses
            assert num_parses(x, ident) == 0, f"corpus defect: {x!r} parses in 3DOM"
            alien = phi_forward(x, phi)
            assert num_parses(alien, phi) == 0, (
                f"[{name}] near-miss became valid after φ: {x!r} -> {alien!r}")


def test_ir_validates_against_phase1_schema() -> None:
    """The IR both languages produce must satisfy Phase 1's ir_schema.json,
    which is additionalProperties:false — so nothing can be smuggled in."""
    import json
    from phi import phase1_dir
    with open(os.path.join(phase1_dir(), "ir_schema.json"), encoding="utf-8") as fh:
        schema = json.load(fh)
    try:
        import jsonschema
    except ImportError:
        print("    (jsonschema not installed — structural check only)")
        jsonschema = None
    ident = identity_phi()
    phi = load_candidate("beta")
    for x in _corpus()[:20]:
        for src, p in ((x, ident), (phi_forward(x, phi), phi)):
            obj = parse(src, p).to_json()
            assert obj["grammar_version"] == "3dom-grammar/1.1.0"
            assert set(obj) <= {"grammar_version", "ops", "source"}
            if jsonschema is not None:
                jsonschema.validate(obj, schema)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for fn in tests:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"  FAIL  {fn.__name__}\n        {exc}")
        except Exception as exc:
            # An ERROR is not a pass. Catching only AssertionError let a
            # ParseError or a missing Phase 1 file abort the runner before the
            # summary line, so a red run could be mistaken for an interrupted one.
            failures += 1
            print(f"  ERROR {fn.__name__}\n        {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    print("test_isomorphism — 3dom-grammar/1.1.0")
    raise SystemExit(main())
