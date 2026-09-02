"""test_phi_validation.py — V1–V8 against a MINIATURE terminal table.

The existing loader test mutates the real `phi_beta.json` and checks that the
mutation raises. That is a good end-to-end check but a poor localiser: the real
table has 43 terminals, so a single mutation trips several rules at once and the
test cannot tell which one fired.

Here the table is eight terminals wide and hand-built, so each test isolates ONE
defect class and asserts the SPECIFIC error code that must report it. If a rule
is silently dropped from validate_phi, exactly one test here goes red.

Run standalone (`python3 tests/test_phi_validation.py`) or under pytest.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))

from phi import (GRAMMAR_VERSION, PhiMap, PhiValidationError,  # noqa: E402
                 Terminal, TerminalTable, identity_phi, load_candidate,
                 load_terminals, render_slots, validate_phi)


# ─────────────────────────────────────────────────────────────────────────────
# An eight-terminal miniature of the real table. It reproduces every structural
# feature the validator cares about:
#   * two substitutable WORDS            (T_VERB_A, T_VERB_B)
#   * one substitutable SYMBOL           (T_SELECTOR_ENTRY)
#   * the OVERLOAD PAIR sharing '.'      (T_CHAIN_OP, T_CLASS_SIGIL)
#   * both frozen quote delimiters       (T_QUOTE_S, T_QUOTE_D)
#   * the frozen descendant combinator   (T_WS)
#
# The five ids above are named EXACTLY as in terminals.json on purpose.
# validate_phi and identity_phi refer to them literally, because I7 (the '.'
# overload), I8 (quote symmetry) and I9 (significant whitespace) are claims
# about those specific roles, not about arbitrary table positions. A miniature
# that renamed them would be testing genericity the design never promised.
# ─────────────────────────────────────────────────────────────────────────────
def mini_table() -> TerminalTable:
    def t(tid, spelling, role, substitutable):
        return Terminal(id=tid, spelling=spelling, role=role,
                        productions=("p",), substitutable=substitutable, note="")
    return TerminalTable(
        grammar_version=GRAMMAR_VERSION,
        terminals=(
            t("T_VERB_A", "scale", "operation verb", True),
            t("T_VERB_B", "move", "operation verb", True),
            t("T_SELECTOR_ENTRY", "$S", "selector entry point", True),
            t("T_CHAIN_OP", ".", "fluent chain operator", True),
            t("T_CLASS_SIGIL", ".", "class matcher sigil", True),
            t("T_QUOTE_S", "'", "string delimiter (single)", False),
            t("T_QUOTE_D", '"', "string delimiter (double)", False),
            t("T_WS", " ", "descendant combinator", False),
        ),
    )


def good_blob() -> dict:
    """A φ-map over the miniature table that must VALIDATE."""
    return {
        "phi_id": "mini",
        "targets_grammar": GRAMMAR_VERSION,
        "generated": "test",
        "notes": "miniature fixture",
        "map": {
            "T_VERB_A": {"from": "scale", "to": "bungi"},
            "T_VERB_B": {"from": "move", "to": "vasto"},
            "T_SELECTOR_ENTRY": {"from": "$S", "to": "&Q"},
            "T_CHAIN_OP": {"from": ".", "to": "~"},
            "T_CLASS_SIGIL": {"from": ".", "to": "~"},
        },
        "overload_groups": [["T_CHAIN_OP", "T_CLASS_SIGIL"]],
        "frozen": ["T_QUOTE_S", "T_QUOTE_D", "T_WS"],
    }


TABLE = mini_table()


def _expect(mutate, code: str, label: str) -> None:
    """Mutate the good blob, expect PhiValidationError mentioning `code`."""
    blob = good_blob()
    mutate(blob)
    try:
        validate_phi(blob, TABLE)
    except PhiValidationError as exc:
        assert code in str(exc), (
            f"{label}: raised, but not under {code}. Message was:\n{exc}")
        return
    raise AssertionError(f"{label}: validate_phi ACCEPTED a φ-map violating {code}")


# ── the fixture itself ───────────────────────────────────────────────────────
def test_the_miniature_fixture_validates() -> None:
    """If this fails every other test here is meaningless."""
    phi = validate_phi(good_blob(), TABLE)
    assert phi.phi_id == "mini"
    assert len(phi.substitutions) == 5


# ── V1 — version pin ─────────────────────────────────────────────────────────
def test_V1_wrong_grammar_version() -> None:
    _expect(lambda b: b.__setitem__("targets_grammar", "3dom-grammar/9.9.9"),
            "V1", "a φ-map aimed at another grammar version")


# ── V2 — exact cover ─────────────────────────────────────────────────────────
def test_V2_missing_terminal() -> None:
    _expect(lambda b: b["map"].pop("T_VERB_B"),
            "V2", "a substitutable terminal absent from the map")


def test_V2_unknown_terminal() -> None:
    _expect(lambda b: b["map"].__setitem__("T_NOT_A_TERMINAL",
                                           {"from": "x", "to": "y"}),
            "V2", "an id that is not in terminals.json")


def test_V2_malformed_entry() -> None:
    _expect(lambda b: b["map"].__setitem__("T_VERB_A", {"to": "bungi"}),
            "V2", "an entry with no 'from'")


# ── V3 — frozen terminals are not substituted ────────────────────────────────
def test_V3_substituting_a_frozen_terminal() -> None:
    _expect(lambda b: b["map"].__setitem__("T_WS", {"from": " ", "to": "_"}),
            "V3", "substituting the frozen descendant combinator")


# ── V4 — `from` matches Phase 1 byte for byte ────────────────────────────────
def test_V4_incorrect_from_spelling() -> None:
    _expect(lambda b: b["map"]["T_VERB_A"].__setitem__("from", "Scale"),
            "V4", "a declared source spelling that differs by one byte")


# ── V5 — overload groups receive ONE spelling ────────────────────────────────
def test_V5_split_overload_group() -> None:
    _expect(lambda b: b["map"]["T_CLASS_SIGIL"].__setitem__("to", "!"),
            "V5", "splitting the '.' overload across two spellings")


def test_V5_unknown_id_in_an_overload_group() -> None:
    _expect(lambda b: b.__setitem__("overload_groups", [["T_CHAIN_OP", "T_NOPE"]]),
            "V5", "an overload group naming an unknown id")


# ── V6 — the spelling PARTITION is preserved (bijectivity mod overloads) ─────
def test_V6_unrelated_collision_collapses_two_roles() -> None:
    """Two roles that are DISTINCT in 3DOM must stay distinct. This is the
    defect a naive 'is it injective?' check misses, because φ restricted to the
    overload pair is legitimately non-injective."""
    _expect(lambda b: b["map"]["T_VERB_B"].__setitem__("to", "bungi"),
            "V6", "collapsing two unrelated verbs onto one spelling")


def test_V6_holds_when_the_overload_moves_together() -> None:
    """The pair may take ANY shared spelling; only the PARTITION is fixed."""
    blob = good_blob()
    blob["map"]["T_CHAIN_OP"]["to"] = "@"
    blob["map"]["T_CLASS_SIGIL"]["to"] = "@"
    phi = validate_phi(blob, TABLE)
    assert phi.spelling("T_CHAIN_OP") == phi.spelling("T_CLASS_SIGIL") == "@"


# ── V7 — the frozen declaration is honest and complete ───────────────────────
def test_V7_incomplete_frozen_declaration() -> None:
    _expect(lambda b: b.__setitem__("frozen", ["T_WS", "T_QUOTE_D"]),
            "V7", "a frozen list that omits a substitutable:false terminal")


def test_V7_T_WS_must_be_named_explicitly() -> None:
    _expect(lambda b: b.__setitem__("frozen", ["T_QUOTE_S", "T_QUOTE_D"]),
            "V7/I9", "a frozen list that does not name T_WS")


# ── V8 — lexability ──────────────────────────────────────────────────────────
def test_V8_empty_spelling() -> None:
    _expect(lambda b: b["map"]["T_VERB_A"].__setitem__("to", ""),
            "V8", "an empty alien spelling")


def test_V8_reserved_leading_character() -> None:
    """A spelling starting with a digit intrudes on FIRST(number)."""
    _expect(lambda b: b["map"]["T_SELECTOR_ENTRY"].__setitem__("to", "9x"),
            "V8", "a spelling starting with a digit")


def test_V8_reserved_character_inside_a_spelling() -> None:
    _expect(lambda b: b["map"]["T_VERB_A"].__setitem__("to", "bun(gi"),
            "V8", "a spelling containing a structural delimiter")


def test_V8_quote_and_layout_are_reserved() -> None:
    for spelling, label in (("'x", "a leading quote"),
                            (" x", "a leading space"),
                            ("x y", "an embedded space")):
        _expect(lambda b, s=spelling: b["map"]["T_VERB_A"].__setitem__("to", s),
                "V8", label)


# ── errors ACCUMULATE rather than short-circuiting ───────────────────────────
def test_multiple_defects_are_all_reported() -> None:
    """A closure-based accumulator only earns its keep if the report is
    complete: fixing one defect and re-running should not reveal a new one."""
    blob = good_blob()
    blob["map"]["T_VERB_A"]["to"] = ""                    # V8
    blob["map"]["T_VERB_B"]["from"] = "WRONG"             # V4
    blob["frozen"] = ["T_WS", "T_QUOTE_D"]                # V7
    try:
        validate_phi(blob, TABLE)
    except PhiValidationError as exc:
        text = str(exc)
        for code in ("V8", "V4", "V7"):
            assert code in text, f"defect {code} was not reported:\n{text}"
        return
    raise AssertionError("validate_phi accepted a φ-map with three defects")


def test_fatal_shape_error_is_distinguished_from_accumulated_defects() -> None:
    """A missing 'map' is not a semantic defect to be collected alongside
    others — there is nothing to validate — so it raises immediately."""
    blob = good_blob()
    del blob["map"]
    try:
        validate_phi(blob, TABLE)
    except PhiValidationError as exc:
        assert "'map'" in str(exc), f"unexpected message: {exc}"
        return
    raise AssertionError("validate_phi accepted a blob with no 'map'")


# ── inversion ────────────────────────────────────────────────────────────────
def test_inversion_is_derived_and_correct_on_the_miniature() -> None:
    phi = validate_phi(good_blob(), TABLE)
    inv = phi.inverse_map()
    for tid in phi.substitutions:
        assert inv.spelling(tid) == phi.source_spelling(tid), \
            f"derived inverse disagrees on {tid}"
    # φ⁻¹ is a FUNCTION on spellings only because V6 holds
    back = phi.invert()
    assert back["~"] == frozenset({"T_CHAIN_OP", "T_CLASS_SIGIL"}), \
        f"the overload pair did not invert as one class: {back['~']}"
    assert back["bungi"] == frozenset({"T_VERB_A"})


def test_inversion_partition_matches_the_source_partition() -> None:
    phi = validate_phi(good_blob(), TABLE)
    ident = identity_phi(TABLE)
    alien_sizes = sorted(len(v) for v in phi.invert().values())
    src_sizes = sorted(len(v) for v in ident.invert().values())
    assert alien_sizes == src_sizes, \
        f"φ changed the spelling partition shape: {alien_sizes} vs {src_sizes}"


# ── identity is produced by the same API ─────────────────────────────────────
def test_identity_is_the_same_data_structure_and_api() -> None:
    """3DOM must be the φ = id member of the family, not a special case with a
    separate code path — that is what makes the isomorphism test a statement
    about one pipeline rather than two."""
    ident = identity_phi(TABLE)
    assert isinstance(ident, PhiMap), "identity_phi returned another type"
    assert ident.is_identity(), "identity_phi is not the identity"
    assert set(ident.substitutions) == set(TABLE.substitutable_ids), \
        "identity_phi does not cover the substitutable set"
    for tid in TABLE.substitutable_ids:
        assert ident.spelling(tid) == TABLE.by_id[tid].spelling


def test_identity_over_the_real_table_is_the_identity() -> None:
    real = load_terminals()
    ident = identity_phi(real)
    assert ident.is_identity()
    for name in ("alpha", "beta", "gamma"):
        assert not load_candidate(name).is_identity(), \
            f"candidate {name} is indistinguishable from 3DOM"


def test_spelling_of_an_unknown_id_raises() -> None:
    phi = validate_phi(good_blob(), TABLE)
    for method in (phi.spelling, phi.source_spelling):
        try:
            method("T_NOT_REAL")
        except PhiValidationError:
            continue
        raise AssertionError(f"{method.__name__} returned a default for an "
                             f"unknown terminal id instead of raising")


# ── render_slots refuses to open a slot for a frozen terminal ────────────────
def test_render_slots_rejects_a_frozen_slot() -> None:
    phi = validate_phi(good_blob(), TABLE)
    assert render_slots("verb: {{T_VERB_A}}", phi) == "verb: bungi"
    for template, label in (("ws: {{T_WS}}", "a frozen terminal"),
                            ("x: {{T_NOPE}}", "an unknown terminal")):
        try:
            render_slots(template, phi)
        except PhiValidationError:
            continue
        raise AssertionError(f"render_slots accepted a slot for {label}")


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
    print("test_phi_validation — 3dom-grammar/1.1.0")
    raise SystemExit(main())
