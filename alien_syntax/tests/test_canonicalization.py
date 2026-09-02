"""test_canonicalization.py — one test per canonicalisation rule C0–C8.

The existing suites test canonicalisation END TO END (a program goes in, a hash
comes out, two lexicons agree). That is the right top-level claim, but it cannot
localise a defect and it cannot see an OVER-normalisation: a canonicaliser that
erased operation order would still make every lexicon agree with every other.

So each rule gets its own test, and each rule gets a NEGATIVE test — a pair of
inputs the rule must keep APART. Under-normalisation shows up as a loud false
failure in the isomorphism suite; over-normalisation shows up as a false PASS
there and is only visible here.

Run standalone (`python3 tests/test_canonicalization.py`) or under pytest.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))

from canonicalize import (GRAMMAR_VERSION, CanonicalisationError,  # noqa: E402
                          IRProgram, Matcher, Operation, Selector, Step,
                          args_in_order, build_args, canonical_json,
                          canonical_number, content_hash, format_number,
                          quote_string)
from phi import identity_phi, load_candidate  # noqa: E402
from transpiler import Emitter, parse, phi_forward  # noqa: E402


def _sel(*matchers: Matcher) -> Selector:
    return Selector((Step(None, tuple(matchers)),))


def _prog(*ops: Operation) -> IRProgram:
    return IRProgram(tuple(ops))


def _hash_of(src: str, lexicon: str = "identity") -> str:
    phi = load_candidate(lexicon)
    return content_hash(parse(src, phi))


# ── C0 — grammar version ─────────────────────────────────────────────────────
def test_C0_grammar_version_on_every_top_level_object() -> None:
    for name in ("identity", "alpha", "beta", "gamma"):
        phi = load_candidate(name)
        src = phi_forward("(function(){ $S('.a').delete(); })();", phi)
        obj = parse(src, phi).to_json()
        assert obj["grammar_version"] == GRAMMAR_VERSION, \
            f"C0 [{name}] grammar_version is {obj['grammar_version']!r}"


def test_C0_no_lexicon_identifier_leaks_into_identity() -> None:
    """The IR must not record WHICH language produced it, or the hashes could
    never agree and the scoring ground truth would stop being shared."""
    for name in ("alpha", "beta", "gamma"):
        phi = load_candidate(name)
        src = phi_forward("(function(){ $S('.a').delete(); })();", phi)
        blob = canonical_json(parse(src, phi))
        for leak in (name, phi.phi_id, phi.spelling("T_SELECTOR_ENTRY")):
            assert leak not in blob, \
                f"C0 [{name}] lexicon marker {leak!r} leaked into {blob}"


# ── C1 — numbers ─────────────────────────────────────────────────────────────
def test_C1_number_normalisation() -> None:
    for raw, want in {"+3": "3", "3.0": "3", "1.50": "1.5", "-0": "0",
                      "0.5": "0.5", "-15": "-15", "2.25": "2.25"}.items():
        got = format_number(canonical_number(raw))
        assert got == want, f"C1 {raw!r} -> {got!r}, expected {want!r}"


def test_C1_booleans_are_rejected() -> None:
    """bool is a subclass of int, so an unguarded formatter emits True as '1'."""
    assert isinstance(True, int), "premise: bool subclasses int"
    for value in (True, False):
        try:
            format_number(value)
        except CanonicalisationError:
            continue
        raise AssertionError(f"C1 format_number({value!r}) must raise, not coerce")


def test_C1_non_finite_values_raise_a_canonicalisation_error() -> None:
    """inf/nan cannot come from a parse (NUMBER is [+-]?[0-9]+(\\.[0-9]+)?), so
    they can only arrive from a hand-built IR. They must fail DISTINGUISHABLY
    rather than as a bare OverflowError from deep inside int()."""
    for text in ("inf", "-inf", "nan"):
        try:
            canonical_number(text)
        except CanonicalisationError:
            continue
        raise AssertionError(f"C1 canonical_number({text!r}) must raise "
                             f"CanonicalisationError")
    for value in (float("inf"), float("-inf"), float("nan")):
        try:
            format_number(value)
        except CanonicalisationError:
            continue
        raise AssertionError(f"C1 format_number({value!r}) must raise "
                             f"CanonicalisationError")


def test_C1_true_and_one_are_distinct_in_the_IR() -> None:
    """Python says 1 == 1.0 == True. The canonical JSON must not."""
    sel = _sel(Matcher("class", "a"))
    as_bool = canonical_json(_prog(Operation("scale", sel, {"factor": True})))
    as_int = canonical_json(_prog(Operation("scale", sel, {"factor": 1})))
    assert as_bool != as_int, \
        "C1 True and 1 serialise identically; a bool would score as a number"
    assert content_hash(_prog(Operation("scale", sel, {"factor": True}))) != \
        content_hash(_prog(Operation("scale", sel, {"factor": 1}))), \
        "C1 the content hash cannot tell True from 1"


# ── C2 — strings ─────────────────────────────────────────────────────────────
def test_C2_quote_selection() -> None:
    assert quote_string("#ff0000") == "'#ff0000'"
    assert quote_string("it's") == '"it\'s"'


def test_C2_both_quotes_raises_rather_than_inventing_an_escape() -> None:
    try:
        quote_string("both ' and \"")
    except CanonicalisationError:
        return
    raise AssertionError("C2 must raise; the grammar has no escape mechanism")


# ── C3 — matcher sorting (commutative, so it MUST collapse) ──────────────────
def test_C3_compound_matcher_order_is_not_meaning() -> None:
    a = _hash_of("(function(){ $S('.wheel.front').scale(2); })();")
    b = _hash_of("(function(){ $S('.front.wheel').scale(2); })();")
    assert a == b, "C3 '.wheel.front' and '.front.wheel' must share one hash"


def test_C3_sort_key_is_an_explicit_rank_not_alphabetical() -> None:
    """type < id < class < pseudo < label < wildcard. Alphabetically 'class'
    would precede 'type', so a generated dataclass ordering would silently give
    the wrong answer here."""
    step = Step(None, (Matcher("class", "zzz"), Matcher("type", "mesh")))
    kinds = [m.kind for m in step.canonical().matchers]
    assert kinds == ["type", "class"], \
        f"C3 rank order is {kinds}, expected type before class"


def test_C3_sorts_ONLY_within_one_compound() -> None:
    """Sorting across steps would destroy the combinator structure."""
    ir = parse("(function(){ $S('.b .a').delete(); })();", identity_phi())
    raws = [".".join(m.name or "*" for m in s.matchers) for s in ir.ops[0].selector.steps]
    assert raws == ["b", "a"], f"C3 sorted across steps: {raws}"


# ── C4 — order preservation (non-commutative, so it MUST be kept) ────────────
def test_C4_operation_order_is_meaning() -> None:
    a = _hash_of("(function(){ $S('.a').scale(2).move(1,0,0); })();")
    b = _hash_of("(function(){ $S('.a').move(1,0,0).scale(2); })();")
    assert a != b, \
        "C4 scale-then-move and move-then-scale collapsed to one hash — the " \
        "canonicaliser is OVER-normalising and every order test is a false pass"


def test_C4_selector_step_order_is_meaning() -> None:
    a = _hash_of("(function(){ $S('.a > .b').delete(); })();")
    b = _hash_of("(function(){ $S('.b > .a').delete(); })();")
    assert a != b, "C4 selector step order collapsed"


def test_C4_combinator_kind_is_meaning() -> None:
    a = _hash_of("(function(){ $S('.a .b').delete(); })();")
    b = _hash_of("(function(){ $S('.a > .b').delete(); })();")
    assert a != b, "C4 descendant and child combinators collapsed"


# ── C5 — reference raw selector ──────────────────────────────────────────────
def test_C5_raw_is_rendered_from_steps_in_3DOM_spelling() -> None:
    """`raw` is required by ir_schema.json. If it held the SURFACE substring the
    alien IR could never equal the 3DOM IR."""
    for name in ("alpha", "beta", "gamma"):
        phi = load_candidate(name)
        src = phi_forward("(function(){ $S('.car > .wheel').delete(); })();", phi)
        raw = parse(src, phi).ops[0].selector.raw
        assert raw == ".car>.wheel", f"C5 [{name}] raw is {raw!r}"
        assert phi.spelling("T_CLASS_SIGIL") not in raw or name == "identity", \
            f"C5 [{name}] the alien class sigil leaked into raw: {raw!r}"


def test_C5_raw_agrees_with_the_sorted_steps() -> None:
    ir = parse("(function(){ $S('.wheel.front').delete(); })();", identity_phi())
    assert ir.ops[0].selector.raw == ".front.wheel", \
        f"C5 raw {ir.ops[0].selector.raw!r} disagrees with C3 sorting"


# ── C6 — canonical JSON ──────────────────────────────────────────────────────
def test_C6_serialisation_is_sorted_and_compact() -> None:
    blob = canonical_json(_prog(Operation("scale", _sel(Matcher("class", "a")),
                                          {"factor": 2})))
    assert ", " not in blob and '": ' not in blob, \
        f"C6 separators are not compact: {blob}"
    obj = json.loads(blob)
    assert list(obj) == sorted(obj), f"C6 top-level keys are not sorted: {list(obj)}"


def test_C6_is_independent_of_dict_insertion_order() -> None:
    sel = _sel(Matcher("class", "a"))
    forward = Operation("move", sel, {"dx": 1, "dy": 2, "dz": 3})
    reverse = Operation("move", sel, {"dz": 3, "dy": 2, "dx": 1})
    assert canonical_json(_prog(forward)) == canonical_json(_prog(reverse)), \
        "C6 insertion order of args changed the canonical bytes"


# ── C7 — content hash ────────────────────────────────────────────────────────
def test_C7_source_is_excluded_from_identity() -> None:
    """ir_schema.json says scorers MUST NOT read `source`. If it entered the
    hash, the surface string would leak into a surface-blind equality test."""
    src = "(function(){ $S('.a').delete(); })();"
    ident = identity_phi()
    without = parse(src, ident)
    with_src = parse(src, ident, keep_source=True)
    assert with_src.source == src, "keep_source did not retain the source"
    assert without.source is None, "source was retained without keep_source"
    assert content_hash(with_src) == content_hash(without), \
        "C7 `source` changed the content hash"
    assert "source" not in canonical_json(with_src), \
        "C7 `source` appears in the canonical JSON"


def test_C7_hash_is_sha256_of_the_utf8_canonical_json() -> None:
    import hashlib
    ir = _prog(Operation("scale", _sel(Matcher("class", "a")), {"factor": 2}))
    expect = hashlib.sha256(canonical_json(ir).encode("utf-8")).hexdigest()
    assert content_hash(ir) == expect, "C7 hash is not SHA-256 over the C6 bytes"
    assert len(content_hash(ir)) == 64


def test_C7_hash_is_stable_across_processes() -> None:
    """Python's built-in hash() is randomised per process by PYTHONHASHSEED.
    SHA-256 must not be, or a digest stored in an artifact is meaningless."""
    src = "(function(){ $S('.wheel.front').scale(1.5); })();"
    here = content_hash(parse(src, identity_phi()))
    script = (
        "import sys; sys.path.insert(0, %r)\n"
        "from canonicalize import content_hash\n"
        "from phi import identity_phi\n"
        "from transpiler import parse\n"
        "print(content_hash(parse(%r, identity_phi())))\n"
        % (os.path.join(ALIEN, "src"), src)
    )
    digests = {here}
    for seed in ("0", "1", "12345"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        out = subprocess.run([sys.executable, "-c", script], capture_output=True,
                             text=True, env=env, cwd=ALIEN)
        assert out.returncode == 0, f"C7 subprocess failed: {out.stderr[-400:]}"
        digests.add(out.stdout.strip())
    assert len(digests) == 1, \
        f"C7 digest varies across processes/hash seeds: {sorted(digests)}"


# ── C8 — argument signatures ─────────────────────────────────────────────────
def test_C8_positional_arguments_map_to_named_fields() -> None:
    assert build_args("move", [1, 2, 3]) == {"dx": 1, "dy": 2, "dz": 3}
    assert build_args("delete", []) == {}


def test_C8_a_prefix_is_legal_and_round_trips() -> None:
    args = build_args("scale", [2])
    assert args == {"factor": 2}, f"C8 prefix mapping is {args}"
    assert args_in_order("scale", args) == [2]


def test_C8_overflow_is_detected_not_truncated() -> None:
    """zip() would silently DISCARD the extra value."""
    args = build_args("recolor", ["#fff", "extra", "more"])
    assert args == {"_positional": ["#fff", "extra", "more"]}, \
        f"C8 overflow was truncated instead of captured: {args}"
    assert args_in_order("recolor", args) == ["#fff", "extra", "more"]


def test_C8_a_hole_in_the_mapping_raises() -> None:
    """{'degrees': 90} skips 'axis'; it cannot be emitted positionally."""
    try:
        args_in_order("rotate", {"degrees": 90})
    except CanonicalisationError:
        return
    raise AssertionError("C8 a non-prefix argument mapping must raise")


def test_C8_structural_validity_is_not_intent_correctness() -> None:
    """$S('.a').rotate(90) with SIGNATURES['rotate'] == ('axis','degrees') binds
    90 to AXIS. That is parse-valid, schema-valid, hash-stable and WRONG, and no
    amount of compiler correctness can detect it — only a heuristic that reads
    the VALUE can. This test pins the behaviour so the layering stays visible."""
    ir = parse("(function(){ $S('.a').rotate(90); })();", identity_phi())
    assert dict(ir.ops[0].args) == {"axis": 90}, \
        f"C8 rotate(90) bound to {dict(ir.ops[0].args)}"
    assert args_in_order("rotate", ir.ops[0].args) == [90]
    # round-trip stable, hash stable — and still an intent error
    from transpiler import canon_text
    once = canon_text("(function(){ $S('.a').rotate(90); })();", identity_phi())
    assert content_hash(parse(once, identity_phi())) == content_hash(ir)

    sys.path.insert(0, os.path.join(ALIEN, "src"))
    import heuristics_ir as H
    issues = H.run("(function(){ $S('.a').rotate(90); })();", identity_phi())
    codes = {i.code for i in issues}
    assert "H5.axis" in codes, (
        "the axis heuristic did not fire on rotate(90); legal arity and legal "
        f"argument NAMES cannot catch this, only the VALUE can. got {codes}")


# ── the frozen dataclasses themselves ────────────────────────────────────────
def test_frozen_dataclasses_reject_field_rebinding() -> None:
    m = Matcher("class", "a")
    try:
        m.kind = "id"                                    # type: ignore[misc]
    except Exception:
        pass
    else:
        raise AssertionError("Matcher is not actually frozen")


def test_operation_args_is_nested_mutable_and_unhashable() -> None:
    """DOCUMENTED HAZARD, pinned so it cannot regress silently: frozen=True is
    shallow. Operation.args is a dict, so Operation is UNHASHABLE and its args
    can be mutated in place. Identity therefore travels through content_hash,
    never through set/dict membership."""
    op = Operation("scale", _sel(Matcher("class", "a")), {"factor": 1})
    try:
        hash(op)
    except TypeError:
        pass
    else:
        raise AssertionError("Operation became hashable; the comment in "
                             "transpiler._phi_key and this test are now stale")
    op.args["factor"] = 99                               # type: ignore[index]
    assert op.args["factor"] == 99, "nested args unexpectedly immutable"


def test_matcher_post_init_enforces_invariants() -> None:
    for bad, label in (
        (lambda: Matcher("nonsense", "a"), "unknown kind"),
        (lambda: Matcher("wildcard", "x"), "wildcard with a name"),
        (lambda: Matcher("class", None), "class without a name"),
        (lambda: Matcher("class", ""), "class with an empty name"),
    ):
        try:
            bad()
        except CanonicalisationError:
            continue
        raise AssertionError(f"__post_init__ accepted {label}")


def test_step_post_init_enforces_invariants() -> None:
    try:
        Step("sideways", (Matcher("class", "a"),))
    except CanonicalisationError:
        pass
    else:
        raise AssertionError("Step accepted an impossible combinator")
    try:
        Step(None, ())
    except CanonicalisationError:
        pass
    else:
        raise AssertionError("Step accepted zero matchers")


def test_operation_post_init_rejects_a_verb_outside_the_closed_set() -> None:
    try:
        Operation("teleport", _sel(Matcher("class", "a")), {})
    except CanonicalisationError:
        return
    raise AssertionError("Operation accepted a verb outside the closed set")


# ── invariants must survive python -O ────────────────────────────────────────
def test_closed_set_invariants_survive_python_dash_O() -> None:
    """A module-level `assert` is REMOVED by -O. An invariant asserted that way
    is not enforced in an optimised run, which is exactly when nobody is
    watching."""
    script = (
        "import sys; sys.path.insert(0, %r)\n"
        "import canonicalize as C\n"
        "ok = True\n"
        "try:\n"
        "    C._assert_closed_sets()\n"
        "except AttributeError:\n"
        "    ok = False\n"
        "print('GUARD_PRESENT' if ok else 'GUARD_ABSENT')\n"
        % os.path.join(ALIEN, "src")
    )
    out = subprocess.run([sys.executable, "-O", "-c", script],
                         capture_output=True, text=True, cwd=ALIEN)
    assert out.returncode == 0, f"-O import failed: {out.stderr[-400:]}"
    assert "GUARD_PRESENT" in out.stdout, (
        "the closed-verb-set invariant is carried by a module-level `assert`, "
        "which python -O deletes; it must be a real raise")


# ── emitter dispatch ─────────────────────────────────────────────────────────
def test_emitter_raises_on_an_unsupported_node_type() -> None:
    """No fallback to str(node): a debugging repr must never be emitted as if it
    were source text."""
    em = Emitter(identity_phi())
    for node in ("a raw string", 42, None, {"kind": "class"}):
        try:
            em.emit(node)
        except TypeError:
            continue
        raise AssertionError(f"Emitter silently emitted {node!r}")


def test_emitter_rejects_an_impossible_combinator() -> None:
    """Reached only from a hand-built IR, but it must RAISE rather than emit an
    empty lead and silently drop the combinator."""
    em = Emitter(identity_phi())
    step = Step.__new__(Step)                      # bypass __post_init__
    object.__setattr__(step, "combinator", "sideways")
    object.__setattr__(step, "matchers", (Matcher("class", "a"),))
    try:
        em.emit(step)
    except CanonicalisationError:
        return
    raise AssertionError("the emitter accepted an impossible combinator, or "
                         "failed with an undiagnostic bare KeyError")


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
        except Exception as exc:                      # an error is not a pass
            failures += 1
            print(f"  ERROR {name}\n        {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    print("test_canonicalization — 3dom-grammar/1.1.0")
    raise SystemExit(main())
