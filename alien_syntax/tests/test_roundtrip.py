"""test_roundtrip.py — φ is a bijection, and text↔IR is stable.

    assert phi_inv(phi(x)) == x                        # φ is a bijection
    assert emit_alien(ir(parse_alien(y))) == canon(y)  # text -> IR -> text stable
    assert ir(parse_alien(emit_alien(i))) == i         # IR -> text -> IR stable

`canon(y)` is `emit ∘ ir ∘ parse` applied to y — the canonical form frozen in
canonicalize.py. The second assertion is therefore the IDEMPOTENCE of that
composition, which is the only form of the claim that is well posed: there is no
canonical text independent of the canonicaliser.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))

from canonicalize import (CanonicalisationError, canonical_number,  # noqa: E402
                          content_hash, format_number, quote_string)
from phi import PhiValidationError, identity_phi, load_candidate  # noqa: E402
from transpiler import (canon_text, emit, parse, phi_forward,  # noqa: E402
                        phi_inverse)
import generate_corpus as G  # noqa: E402

CANDIDATES = ("alpha", "beta", "gamma")


def _corpus():
    return G.phase1_programs("positive", identity_phi())


def test_phi_is_a_bijection_on_text() -> None:
    for name in CANDIDATES:
        phi = load_candidate(name)
        for x in _corpus() + G.phase1_programs("vacuous", identity_phi()):
            assert phi_inverse(phi_forward(x, phi), phi) == x, \
                f"[{name}] φ⁻¹∘φ != id on {x!r}"


def test_phi_inverse_is_derived_not_declared() -> None:
    """φ⁻¹ must come out of φ, and the derivation must assert bijectivity."""
    for name in CANDIDATES:
        phi = load_candidate(name)
        inverse = phi.inverse_map()
        for tid in phi.substitutions:
            assert inverse.spelling(tid) == phi.source_spelling(tid), \
                f"[{name}] derived inverse disagrees with terminals.json on {tid}"
        # the spelling PARTITION must be preserved, which is bijectivity modulo
        # the '.' overload — the property phi.py's V6 enforces
        assert len(phi.invert()) == len(identity_phi(phi.table).invert()), \
            f"[{name}] φ changes the number of distinct spellings"


def test_text_to_ir_to_text_is_stable() -> None:
    for name in ("identity",) + CANDIDATES:
        phi = load_candidate(name)
        for x in _corpus():
            y = x if name == "identity" else phi_forward(x, phi)
            once = canon_text(y, phi)
            twice = canon_text(once, phi)
            assert once == twice, (
                f"[{name}] emit∘ir∘parse is not idempotent\n"
                f"  once : {once!r}\n  twice: {twice!r}")


def test_ir_to_text_to_ir_is_stable() -> None:
    for name in ("identity",) + CANDIDATES:
        phi = load_candidate(name)
        for x in _corpus():
            y = x if name == "identity" else phi_forward(x, phi)
            ir = parse(y, phi)
            back = parse(emit(ir, phi), phi)
            assert content_hash(back) == content_hash(ir), \
                f"[{name}] IR -> text -> IR changed the IR for {y!r}"


def test_canonical_form_is_actually_canonical() -> None:
    """C1/C2/C3: spelling variants of ONE program must reach ONE canonical text."""
    phi = load_candidate("beta")
    variants = [
        "(function(){ $S('.wheel.front').scale(2); })();",
        "(function(){ $S('.front.wheel').scale(2); })();",     # C3 matcher order
        '(function(){ $S(".wheel.front").scale(2.0); })();',   # C1 + C2
        "(function () {\n  $S( '.wheel.front' ) . scale( +2 ) ;\n})();",  # L1 layout
    ]
    texts = {canon_text(phi_forward(v, phi), phi) for v in variants}
    assert len(texts) == 1, f"canonicalisation is not canonical: {sorted(texts)}"


def test_number_canonicalisation_decisions() -> None:
    cases = {"+3": "3", "1.50": "1.5", "-0": "0", "2.0": "2",
             "0.5": "0.5", "-15": "-15", "2.25": "2.25"}
    for raw, want in cases.items():
        got = format_number(canonical_number(raw))
        assert got == want, f"C1: {raw!r} -> {got!r}, expected {want!r}"


def test_string_quoting_decisions() -> None:
    assert quote_string("#ff0000") == "'#ff0000'"          # C2 default
    assert quote_string("it's") == '"it\'s"'               # C2 fallback
    try:
        quote_string("both ' and \"")
        raise AssertionError("C2 must RAISE on a string needing an escape")
    except CanonicalisationError:
        pass


def test_loader_fails_loudly_not_softly() -> None:
    """A φ-map that breaks I7 / I8 / I9 must RAISE, never warn."""
    import copy
    import json
    from phi import load_terminals, validate_phi
    table = load_terminals()
    with open(os.path.join(ALIEN, "candidates", "phi_beta.json"),
              encoding="utf-8") as fh:
        good = json.load(fh)

    def must_raise(mutate, label: str) -> None:
        blob = copy.deepcopy(good)
        mutate(blob)
        try:
            validate_phi(blob, table)
        except PhiValidationError:
            return
        raise AssertionError(f"loader accepted a φ-map that violates {label}")

    must_raise(lambda b: b["map"]["T_CLASS_SIGIL"].__setitem__("to", "!"),
               "I7 (overload group split)")
    must_raise(lambda b: b["map"].__setitem__(
        "T_WS", {"from": "' '+", "to": "_"}), "I9 (frozen T_WS)")
    must_raise(lambda b: b["map"].__setitem__(
        "T_QUOTE_S", {"from": "'", "to": "‹"}), "I8 (frozen quote)")
    must_raise(lambda b: b["map"].pop("T_VERB_SPIN"), "V2 (incomplete cover)")
    must_raise(lambda b: b["map"]["T_VERB_SPIN"].__setitem__("to", "brom"),
               "V6 (bijectivity — two roles collapsed onto one spelling)")
    must_raise(lambda b: b["map"]["T_ID_SIGIL"].__setitem__("to", "9"),
               "V8 (spelling starts in FIRST(argument))")


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
    print("test_roundtrip — 3dom-grammar/1.1.0")
    raise SystemExit(main())
