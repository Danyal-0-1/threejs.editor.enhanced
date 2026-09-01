"""
tasks.py -- the five task scores, grading the Operation IR.
"""

from __future__ import annotations

import math
import re
from typing import Any, Iterable, Mapping, Sequence

from fixture_scene import FixtureScene, resolve, resolve_all

GRAMMAR_VERSION = "3dom-grammar/1.1.0"

PASS: float = 1.0 
FAIL: float = 0.0

report = tuple[float, list[str]]


def ops_of(ir):
    """
    Pull the op list out of whatever shape actually arrived.

    Canonical form is {"grammar_version":...., "ops":[...]}. In practice models
    also emit a bare op object, or a bare array. Accepting thoes costs nothing
    and prevents the grader from scoring its own strictness.
    Output:
    A list containig only mapping-like operation objects.
    Returns an empty list when nothing can be recovered.
    """
    if isinstance(ir, Mapping):
        ops = ir.get("ops")
        if isinstance(ops, list):
            return[op for op in ops if isinstance(op, Mapping)]
        if ir.get("op") is not None:
            return [dict(ir)]
        return[]

    if isinstance(ir,Sequence) and not isinstance(ir, (str, bytes)):
        return[op for op in ir if isinstance(op,Mapping)]
    return[]



def is_vacuous(ir:Any) -> bool:

   """The D5 case: parses, zero operations. A parse SUCCESS and a task FAILURE
    on every task whose target IR carries at least one op."""
   return len(ops_of(ir)) == 0

def has_grammar_version(ir:Any) ->bool:
    """SCORING_POLICY S6a: the builder stamps a version into every IR object. An
        unstamped IR is unreportable -- checked by the corpus gate, not by scoring,
        so a builder bug never silently changes a task number."""
    return isinstance(ir, Mapping) and ir.get("grammar_version") == GRAMMAR_VERSION


# ==============================================================================
# TASK 1 -- OP-SELECTION
# ==============================================================================
# INPUT   ir: dict (parsed IR)   target: str | Sequence[str]
# OUTPUT  float in {0.0, 1.0}
#
# Exact verb match against the closed 15-verb set. NO synonyms here, on purpose:
# op-selection asks whether the model picked the right verb from a set it was
# shown. Accepting 'paint' for 'recolor' would measure something else. (Synonyms
# ARE allowed in task 4, where the question is decomposition, not naming.)

def score_op_selection(ir: Any, target: str | Sequence[str]) -> float:
    return score_op_selection_report(ir, target)[0]

def score_op_selection_report(ir:Any, target: str | Sequence[str]) -> Report:
    ops = ops_of(ir)
    if not ops:
        return FAIL, ["no ops in IR (vacuous or unparsed)"]

    wanted = [target] if isinstance(target, str) else list(target or [])
    if not wanted:
        return FAIL, ["no target verb supplied"]

    if len(ops) < len (wanted):
        return FAIL, [f"{len(ops)} op(s) emitted, target sequence needs {len(wanted)}"]

    reasons: list[str] = []
    for i, want in enumerate(wanted):
        got = ops[i].get("op")
        if not isinstance(got, str) or got != want:
             reasons.append(f'op{i}: "{got}" !="{want}"')
    return (FAIL, reasons) if reasons else(PASS, [f"verb(s) ok: {','.join(wanted)}"])
