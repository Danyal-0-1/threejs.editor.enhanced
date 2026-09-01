"""test_tasks.py -- the PREREQUISITE GATE from evalEditMatrix.md S1, in code.

"A wrong ruler makes the whole matrix meaningless." Every check below is one line
of that gate: each scorer is spot-checked against a hand-verified case, and each
known false-positive class is asserted to FAIL.

Run:  python3 test_tasks.py
"""

from __future__ import annotations

import sys

from fixture_scene import scene_for
from tasks import (
    GRAMMAR_VERSION, arg_bag, colour_family, has_grammar_version, is_vacuous,
    score_arg_extraction, score_arg_extraction_report, score_case, score_labeling,
    score_multi_op, score_op_selection, score_selector_resolution,
    score_selector_resolution_report,
)

CHECKS: list[tuple[str, bool]] = []


def check(name: str, condition: bool) -> None:
    CHECKS.append((name, bool(condition)))


def ir(*ops, version: str = GRAMMAR_VERSION) -> dict:
    return {"grammar_version": version, "ops": list(ops)}


def op(verb: str, selector: str, **args) -> dict:
    return {"op": verb, "selector": {"raw": selector}, "args": args}


TRUCK = scene_for("dumptruck")
WHEELS = ["Object_20", "Object_21", "Object_22", "Object_23"]
FRONT_WHEELS = ["Object_20", "Object_21"]
BED = ["Object_07"]

# -- Task 1: op-selection ------------------------------------------------------
check("op-selection: correct verb passes",
      score_op_selection(ir(op("recolor", ".wheel", color="black")), "recolor") == 1.0)
check("op-selection: wrong verb fails",
      score_op_selection(ir(op("scale", ".wheel", factor=2)), "recolor") == 0.0)
check("op-selection: NO synonyms (paint != recolor)",
      score_op_selection(ir(op("paint", ".wheel", color="black")), "recolor") == 0.0)
check("op-selection: vacuous IR fails",
      score_op_selection(ir(), "recolor") == 0.0)
check("op-selection: dropped 'op' field fails without raising",
      score_op_selection({"grammar_version": GRAMMAR_VERSION,
                          "ops": [{"selector": {"raw": ".wheel"}}]}, "recolor") == 0.0)
check("op-selection: garbage input fails without raising",
      score_op_selection("not json at all", "recolor") == 0.0)
check("op-selection: type sequence checked in order",
      score_op_selection(ir(op("spin", ".wheel"), op("recolor", ".bed", color="red")),
                         ["spin", "recolor"]) == 1.0)
check("op-selection: swapped sequence fails",
      score_op_selection(ir(op("recolor", ".bed", color="red"), op("spin", ".wheel")),
                         ["spin", "recolor"]) == 0.0)

# -- Task 2: arg-extraction ----------------------------------------------------
check("arg: 'black' matches gold black",
      score_arg_extraction(ir(op("recolor", ".wheel", color="black")), {"color": "black"}) == 1.0)
check("arg: host hex 0x111111 matches gold black",
      score_arg_extraction(ir(op("recolor", ".wheel", color="#111111")), {"color": "black"}) == 1.0)
check("arg: short hex #111 matches gold black",
      score_arg_extraction(ir(op("recolor", ".wheel", color="#111")), {"color": "black"}) == 1.0)
check("arg: int 0x111111 matches gold black",
      score_arg_extraction(ir(op("recolor", ".wheel", color=0x111111)), {"color": "black"}) == 1.0)
check("arg: blue does NOT match gold black",
      score_arg_extraction(ir(op("recolor", ".wheel", color="#0000ff")), {"color": "black"}) == 0.0)
check("arg: KEY SYNONYM 'colour' accepted",
      score_arg_extraction(ir({"op": "recolor", "selector": {"raw": ".wheel"},
                               "args": {"colour": "black"}}), {"color": "black"}) == 1.0)
check("arg: KEY SYNONYM 'value' on scale accepted (op-specific)",
      score_arg_extraction(ir(op("scale", "#dumptruck", value=2)), {"factor": {"min": 1.05}}) == 1.0)
check("arg: strict_keys=True rejects 'value' (host-executability mode)",
      score_arg_extraction(ir(op("scale", "#dumptruck", value=2)),
                           {"factor": {"min": 1.05}}, strict_keys=True) == 0.0)
check("arg: MATH still enforced under key leniency (0.5 is not 'bigger')",
      score_arg_extraction(ir(op("scale", "#dumptruck", amount=0.5)), {"factor": {"min": 1.05}}) == 0.0)
check("arg: 'slowly' -> duration 4 passes the >=3 range",
      score_arg_extraction(ir(op("spin", ".wheel", duration=4)), {"duration": {"min": 3}}) == 1.0)
check("arg: default duration 2 fails the range (modifier not extracted)",
      score_arg_extraction(ir(op("spin", ".wheel", duration=2)), {"duration": {"min": 3}}) == 0.0)
check("arg: 'speed' is NOT aliased to duration (inverse quantity)",
      score_arg_extraction(ir(op("spin", ".wheel", speed=4)), {"duration": {"min": 3}}) == 0.0)
check("arg: missing arg fails",
      score_arg_extraction(ir(op("spin", ".wheel")), {"duration": {"min": 3}}) == 0.0)
check("arg: nested {'position': {'y': 0.5}} flattens to dy",
      score_arg_extraction(ir({"op": "move", "selector": {"raw": ".cab"},
                               "args": {"position": {"y": 0.5}}}), {"dy": {"min": 0.01}}) == 1.0)
check("arg: positional move(0, 0.5, 0) maps by signature",
      score_arg_extraction(ir({"op": "move", "selector": {"raw": ".cab"},
                               "args": [0, 0.5, 0]}), {"dy": {"min": 0.01}}) == 1.0)
check("arg: string number '1.5x' parses",
      score_arg_extraction(ir(op("scale", "#dumptruck", factor="1.5x")), {"factor": {"min": 1.05}}) == 1.0)
check("arg: True is not accepted as a numeric factor",
      score_arg_extraction(ir(op("scale", "#dumptruck", factor=True)), {"factor": {"min": 1.05}}) == 0.0)
check("arg: no expectation on the case -> n/a passes",
      score_arg_extraction(ir(op("delete", ".front.wheel")), None) == 1.0)
check("colour_family: gold and yellow share a family",
      colour_family("#FFD700") == colour_family("gold") == "gold")
check("colour_family: 0x888888 is gray",
      colour_family(0x888888) == "gray")

# -- Task 3: labeling ----------------------------------------------------------
check("labeling: exact gold hit",
      score_labeling("wheel", ["wheel", "tire", "rim"]) == 1.0)
check("labeling: synonym hit",
      score_labeling("Tire", ["wheel", "tire", "rim"]) == 1.0)
check("labeling: substring either direction ('dump bed' ~ 'bed')",
      score_labeling("dump bed", ["bed", "tray"]) == 1.0)
check("labeling: punctuation/case normalised",
      score_labeling("Tail-Light!", ["tail light", "lamp"]) == 1.0)
check("labeling: wrong part fails",
      score_labeling("grille", ["wheel", "tire", "rim"]) == 0.0)
check("labeling: empty label fails",
      score_labeling("", ["wheel"]) == 0.0)
check("labeling: reads op['label'] from an IR object",
      score_labeling(ir({"op": "recolor", "selector": {"raw": ".wheel"},
                         "args": {}, "label": "tire"}), ["wheel", "tire"]) == 1.0)

# -- Task 4: multi-op ----------------------------------------------------------
check("multi-op: 2-op split scores 1.0",
      score_multi_op(ir(op("recolor", ".wheel", color="black"),
                        op("recolor", ".bed", color="red")), 2) == 1.0)
check("multi-op: MISSED split (1 of 2) fails",
      score_multi_op(ir(op("recolor", ".wheel", color="black")), 2) == 0.0)
check("multi-op: OVER-split (4 of 1) fails -- the 'all four wheels' trap",
      score_multi_op(ir(*[op("recolor", f"#object_2{i}", color="black") for i in range(4)]), 1) == 0.0)
check("multi-op: vacuous IR fails a 1-op target",
      score_multi_op(ir(), 1) == 0.0)
check("multi-op: type sequence enforced",
      score_multi_op(ir(op("recolor", ".wheel", color="black"), op("spin", ".bed")),
                     2, ["spin", "recolor"]) == 0.0)
check("multi-op: SYNONYM rotate~spin accepted (decomposition, not naming)",
      score_multi_op(ir(op("rotate", ".wheel"), op("recolor", ".bed", color="red")),
                     2, ["spin", "recolor"]) == 1.0)
check("multi-op: setMaterial WITH colour counts as recolor",
      score_multi_op(ir(op("setMaterial", ".bed", color="red")), 1, ["recolor"]) == 1.0)
check("multi-op: setMaterial WITHOUT colour does NOT count as recolor",
      score_multi_op(ir(op("setMaterial", ".bed", texture="rust")), 1, ["recolor"]) == 0.0)

# -- Task 5: selector-resolution (RCN) -----------------------------------------
check("RCN: '.wheel' hits exactly the four wheels",
      score_selector_resolution(ir(op("recolor", ".wheel", color="black")), WHEELS, TRUCK) == 1.0)
check("RCN: '*' (changed EVERYTHING) FAILS -- the critical false pass",
      score_selector_resolution(ir(op("recolor", "*", color="black")), WHEELS, TRUCK) == 0.0)
check("RCN: whole-group '#dumptruck' FAILS a wheels-only target",
      score_selector_resolution(ir(op("recolor", "#dumptruck", color="black")), WHEELS, TRUCK) == 0.0)
check("RCN: under-selection (one wheel of four) fails",
      score_selector_resolution(ir(op("recolor", "#object_20", color="black")), WHEELS, TRUCK) == 0.0)
check("RCN: compound '.front.wheel' hits exactly the two front wheels",
      score_selector_resolution(ir(op("recolor", ".front.wheel", color="red")), FRONT_WHEELS, TRUCK) == 1.0)
check("RCN: '.wheel' OVER-selects a front-wheels-only target (bleed)",
      score_selector_resolution(ir(op("recolor", ".wheel", color="red")), FRONT_WHEELS, TRUCK) == 0.0)
check("RCN: child combinator '.truck > .bed' resolves one level down",
      score_selector_resolution(ir(op("recolor", ".truck > .bed", color="gray")), BED, TRUCK) == 1.0)
check("RCN: structured `steps` and raw string agree",
      score_selector_resolution(
          ir({"op": "recolor",
              "selector": {"raw": ".wheel",
                           "steps": [{"combinator": None,
                                      "matchers": [{"kind": "class", "name": "wheel"}]}]},
              "args": {"color": "black"}}), WHEELS, TRUCK) == 1.0)
check("RCN: nonsense selector resolves to nothing and fails",
      score_selector_resolution(ir(op("recolor", ".nonexistent", color="black")), WHEELS, TRUCK) == 0.0)
check("RCN: per-op target sets for a 2-op decomposition",
      score_selector_resolution(ir(op("recolor", ".wheel", color="black"),
                                   op("recolor", ".bed", color="red")),
                                [WHEELS, BED], TRUCK) == 1.0)
check("RCN: merged mesh -- resolving NOTHING is the pass",
      score_selector_resolution(ir(op("recolor", ".sheets", color="blue")), [],
                                scene_for("merged-bed"), merged_fail=True) == 1.0)
check("RCN: merged mesh -- hitting the whole merged node FAILS",
      score_selector_resolution(ir(op("recolor", "#gothicbed", color="blue")), [],
                                scene_for("merged-bed"), merged_fail=True) == 0.0)

# -- IR hygiene ----------------------------------------------------------------
check("D5: empty ops array is vacuous", is_vacuous(ir()) is True)
check("D5: non-empty ops array is not vacuous", is_vacuous(ir(op("recolor", ".wheel"))) is False)
check("S6a: grammar_version present", has_grammar_version(ir(op("recolor", ".wheel"))) is True)
check("S6a: wrong grammar_version rejected",
      has_grammar_version(ir(op("recolor", ".wheel"), version="3dom-grammar/0.9.0")) is False)
check("arg_bag: positional recolor maps to color",
      arg_bag({"op": "recolor", "args": ["#111111"]}).get("color") == "#111111")

# -- Aggregate: five INDEPENDENT columns ---------------------------------------
# The blended-score trap: a 'change everything' edit gets the verb and the colour
# right and MUST still be scored 0 on selector-resolution.
_bleed = score_case(
    ir(op("recolor", "*", color="black")),
    {"opType": "recolor", "opCount": 1, "args": {"color": "black"},
     "targetNodes": WHEELS}, TRUCK)
check("score_case: bleed edit passes op/arg but FAILS selector",
      _bleed["op-selection"] == 1.0 and _bleed["arg-extraction"] == 1.0
      and _bleed["selector-resolution"] == 0.0)

_clean = score_case(
    ir(op("recolor", ".wheel", color="black")),
    {"opType": "recolor", "opCount": 1, "args": {"color": "black"},
     "targetNodes": WHEELS}, TRUCK)
check("score_case: clean edit passes all four columns",
      all(v == 1.0 for v in _clean.values()))

# -- report --------------------------------------------------------------------
failed = [name for name, ok in CHECKS if not ok]
for name, ok in CHECKS:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
print(f"\n{len(CHECKS) - len(failed)}/{len(CHECKS)} checks passed")
if failed:
    print("\nFAILED:")
    for name in failed:
        print(f"  - {name}")
sys.exit(1 if failed else 0)
