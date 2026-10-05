"""Adversarial tests for the semantic scorer (defect P3-001).

These are the tests the literature review demands before any Phase 3 number is
believed: extra, missing, duplicated, reordered and wrong-target operations,
plus parse-valid-but-semantically-wrong programs.

`test_extra_operation_fails` is the regression guard for the actual defect. It
also protects against `scripts/vendor_sync.py` silently restoring the upstream
version, since re-running the sync overwrites the patched copy.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from phase3 import _vendor  # noqa: E402,F401

import tasks  # noqa: E402


def ir(*ops):
    return {"ops": [{"op": o, "args": a} for o, a in ops]}


RECOLOR = ("recolor", {"color": "#111111"})
DELETE = ("delete", {})
SCALE = ("scale", {"factor": 2})


# --- the defect itself -----------------------------------------------------

def test_extra_operation_fails():
    """P3-001. The program does what was asked AND something else => FAIL."""
    assert tasks.score_op_selection(ir(RECOLOR, DELETE), "recolor") == 0.0


def test_many_extra_operations_fail():
    assert tasks.score_op_selection(ir(RECOLOR, DELETE, SCALE), "recolor") == 0.0


def test_extra_operation_fails_on_multi_target():
    assert tasks.score_op_selection(
        ir(RECOLOR, DELETE, SCALE), ["recolor", "delete"]) == 0.0


def test_repair_is_present_in_source():
    """Guard against vendor_sync.py restoring the unpatched upstream copy."""
    src = os.path.join(_vendor.PHASE1, "tasks.py")
    text = open(src, encoding="utf-8").read()
    assert "PHASE 3 REPAIR (P3-001)" in text, (
        "the P3-001 repair is missing from the vendored tasks.py — re-apply "
        "PATCHES/tasks.op_selection.md after running vendor_sync.py")
    assert "if len(ops) != len(wanted):" in text


# --- the cases that already worked, which must keep working ---------------

def test_exact_match_passes():
    assert tasks.score_op_selection(ir(RECOLOR), "recolor") == 1.0


def test_exact_sequence_passes():
    assert tasks.score_op_selection(ir(RECOLOR, DELETE),
                                    ["recolor", "delete"]) == 1.0


def test_missing_operation_fails():
    assert tasks.score_op_selection(ir(RECOLOR), ["recolor", "delete"]) == 0.0


def test_duplicated_operation_fails():
    assert tasks.score_op_selection(ir(RECOLOR, RECOLOR), "recolor") == 0.0


def test_reordered_operations_fail():
    assert tasks.score_op_selection(ir(DELETE, RECOLOR),
                                    ["recolor", "delete"]) == 0.0


def test_wrong_verb_fails():
    assert tasks.score_op_selection(ir(SCALE), "recolor") == 0.0


def test_vacuous_fails():
    assert tasks.score_op_selection(ir(), "recolor") == 0.0


# --- the other two axes must not have regressed ---------------------------

def test_multi_op_overproduction_still_fails():
    assert tasks.score_multi_op(ir(RECOLOR, DELETE), 1) == 0.0


def test_multi_op_exact_still_passes():
    assert tasks.score_multi_op(ir(RECOLOR, DELETE), 2) == 1.0


def test_report_explains_direction():
    ok, why = tasks.score_op_selection_report(ir(RECOLOR, DELETE), "recolor")
    assert ok == 0.0
    assert any("over-production" in w for w in why), why
    ok2, why2 = tasks.score_op_selection_report(ir(RECOLOR), ["recolor", "delete"])
    assert ok2 == 0.0
    assert any("under-production" in w for w in why2), why2
