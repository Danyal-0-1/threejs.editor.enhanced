"""build_task_dataset.py — freeze the behavioural task dataset.

Ports the 22 editing cases, 13 multi-op cases and 9 labeling cases from
docs/editor/js/ai/editMatrix.js into a machine-readable frozen dataset, and
GIVES EVERY POSITIVE CASE A CANONICAL GOLD IR.

editMatrix.js carries per-task expectations (opType / targetNodes / args /
opCount) but no gold PROGRAM. A gold IR is added here as a 3DOM program string
which is then parsed through the real grammar, so the gold is validated by the
same machinery that will grade the models rather than asserted by hand.

VALIDATION (all of it must pass or the script exits nonzero):
  T1  the gold program parses under identity
  T2  the gold IR resolves to EXACTLY the expected target nodes
  T3  the gold IR passes every scorer the case declares
  T4  the gold program transliterates to alpha/beta/gamma and each parses back
      to a BYTE-IDENTICAL canonical IR (the paired-design requirement)
  T5  a deliberately WRONG answer fails the scorers (the grader is not vacuous)

`merged-sheets` has no positive DSL target; it is marked
scoring_family="graceful_refusal" and carries gold_program=None. It is scored
separately and never enters ordinary generation accuracy.
"""
from __future__ import annotations

import hashlib, json, os, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "alien_syntax", "src"))
sys.path.insert(0, os.path.join(REPO, "grammar_and_3DOM_client"))

from phi import identity_phi, load_candidate                       # noqa: E402
from transpiler import parse, phi_forward                          # noqa: E402
from canonicalize import canonical_json, content_hash              # noqa: E402
import tasks as T                                                  # noqa: E402
from fixture_scene import scene_for                                # noqa: E402

LANGUAGES = ("identity", "alpha", "beta", "gamma")

# ── THE 22 EDITING CASES ─────────────────────────────────────────────────────
# `expect` is copied VERBATIM from editMatrix.js (JS object -> Python dict).
# `gold` is the 3DOM program added here; it is validated against `expect`.
CASES = [
 dict(id="wheels-black", asset="dumptruck", prompt="make the wheels black",
      expect=dict(opType="recolor", opCount=1, args=dict(color="black"),
                  targetNodes=["Object_20","Object_21","Object_22","Object_23"]),
      gold="(function(){ $S('.wheel').recolor('black'); })();"),
 dict(id="front-wheels", asset="dumptruck", prompt="make the front wheels red",
      expect=dict(opType="recolor", opCount=1, args=dict(color="red"),
                  targetNodes=["Object_20","Object_21"]),
      gold="(function(){ $S('.wheel.front').recolor('red'); })();"),
 dict(id="dump-bed", asset="dumptruck", prompt="make the dump bed grey",
      expect=dict(opType="recolor", opCount=1, args=dict(color="gray"),
                  targetNodes=["Object_07"]),
      gold="(function(){ $S('.dump-bed').recolor('gray'); })();"),
 dict(id="grille", asset="dumptruck", prompt="paint the grille gold",
      expect=dict(opType="recolor", opCount=1, args=dict(color="gold"),
                  targetNodes=["Object_03"]),
      gold="(function(){ $S('.grille').recolor('gold'); })();"),
 dict(id="bigger", asset="dumptruck", prompt="make it bigger",
      expect=dict(opType="scale", opCount=1, args=dict(factor=dict(min=1.05)),
                  targetNodes=["DumpTruck"]),
      gold="(function(){ $S('.truck').scale(1.5); })();"),
 dict(id="spin-wheels", asset="dumptruck", prompt="spin the wheels slowly",
      expect=dict(opType="spin", opCount=1, args=dict(duration=dict(min=3)),
                  targetNodes=["Object_20","Object_21","Object_22","Object_23"]),
      gold="(function(){ $S('.wheel').spin('y',1,4); })();"),
 dict(id="lift", asset="dumptruck", prompt="lift the cab up a bit",
      expect=dict(opType="move", opCount=1, args=dict(dy=dict(min=0.01)),
                  targetNodes=["Object_03"]),
      gold="(function(){ $S('.cab').move(0,0.5,0); })();"),
 dict(id="delete-front", asset="dumptruck", prompt="remove the front wheels",
      expect=dict(opType="delete", opCount=1,
                  targetNodes=["Object_20","Object_21"]),
      gold="(function(){ $S('.wheel.front').delete(); })();"),

 # ── multi-op decomposition (multiOp: true) ──────────────────────────────────
 dict(id="two-colors", asset="dumptruck", prompt="make the wheels black and the bed red",
      expect=dict(multiOp=True, opCount=2,
                  ops=[dict(opType="recolor", targetNodes=["Object_20","Object_21","Object_22","Object_23"]),
                       dict(opType="recolor", targetNodes=["Object_07"])]),
      gold="(function(){ $S('.wheel').recolor('black'); $S('.dump-bed').recolor('red'); })();"),
 dict(id="three-ops", asset="dumptruck",
      prompt="spin the wheels, paint the bed red, and remove the grille",
      expect=dict(multiOp=True, opCount=3,
                  ops=[dict(opType="spin", targetNodes=["Object_20","Object_21","Object_22","Object_23"]),
                       dict(opType="recolor", targetNodes=["Object_07"]),
                       dict(opType="delete", targetNodes=["Object_03"])]),
      gold="(function(){ $S('.wheel').spin('y',1,2); $S('.dump-bed').recolor('red'); $S('.grille').delete(); })();"),
 dict(id="no-oversplit", asset="dumptruck", prompt="make the wheels black",
      expect=dict(multiOp=True, opCount=1, opType="recolor",
                  targetNodes=["Object_20","Object_21","Object_22","Object_23"]),
      gold="(function(){ $S('.wheel').recolor('black'); })();"),
 dict(id="whole-truck", asset="dumptruck", prompt="paint the whole truck red",
      expect=dict(multiOp=True, opCount=1, opType="recolor",
                  targetNodes=["DumpTruck"]),
      gold="(function(){ $S('.truck').recolor('red'); })();"),
 dict(id="wheels-and-grille", asset="dumptruck",
      prompt="make the wheels black and paint the grille gold",
      expect=dict(multiOp=True, opCount=2,
                  ops=[dict(opType="recolor", targetNodes=["Object_20","Object_21","Object_22","Object_23"]),
                       dict(opType="recolor", targetNodes=["Object_03"])]),
      gold="(function(){ $S('.wheel').recolor('black'); $S('.grille').recolor('gold'); })();"),
 dict(id="bed-and-lights", asset="dumptruck",
      prompt="paint the bed red and remove the tail lights",
      expect=dict(multiOp=True, opCount=2,
                  ops=[dict(opType="recolor", targetNodes=["Object_07"]),
                       dict(opType="delete", targetNodes=["Object_12","Object_13"])]),
      gold="(function(){ $S('.dump-bed').recolor('red'); $S('.tail-light').delete(); })();"),
 dict(id="spin-and-color", asset="dumptruck",
      prompt="spin the wheels and make the bed grey",
      expect=dict(multiOp=True, opCount=2,
                  ops=[dict(opType="spin", targetNodes=["Object_20","Object_21","Object_22","Object_23"]),
                       dict(opType="recolor", targetNodes=["Object_07"])]),
      gold="(function(){ $S('.wheel').spin('y',1,2); $S('.dump-bed').recolor('gray'); })();"),
 dict(id="lift-and-paint", asset="dumptruck", prompt="lift the cab up and paint it blue",
      expect=dict(multiOp=True, opCount=2,
                  ops=[dict(opType="move", targetNodes=["Object_03"]),
                       dict(opType="recolor", targetNodes=["Object_03"])]),
      gold="(function(){ $S('.cab').move(0,0.5,0).recolor('blue'); })();"),
 dict(id="color-move-delete", asset="dumptruck",
      prompt="paint the cab blue, move the bed up, and delete the front wheels",
      expect=dict(multiOp=True, opCount=3,
                  ops=[dict(opType="recolor", targetNodes=["Object_03"]),
                       dict(opType="move", targetNodes=["Object_07"]),
                       dict(opType="delete", targetNodes=["Object_20","Object_21"])]),
      gold="(function(){ $S('.cab').recolor('blue'); $S('.dump-bed').move(0,0.5,0); $S('.wheel.front').delete(); })();"),
 dict(id="all-four-wheels", asset="dumptruck", prompt="make all four wheels black",
      expect=dict(multiOp=True, opCount=1, opType="recolor",
                  targetNodes=["Object_20","Object_21","Object_22","Object_23"]),
      gold="(function(){ $S('.wheel').recolor('black'); })();"),
 dict(id="both-lights", asset="dumptruck", prompt="make both tail lights bright red",
      expect=dict(multiOp=True, opCount=1, opType="recolor",
                  targetNodes=["Object_12","Object_13"]),
      gold="(function(){ $S('.tail-light').recolor('red'); })();"),
 dict(id="everything-red", asset="dumptruck", prompt="make everything red",
      expect=dict(multiOp=True, opCount=1, opType="recolor",
                  targetNodes=["DumpTruck"]),
      gold="(function(){ $S('.truck').recolor('red'); })();"),
 dict(id="wheels-and-rims", asset="dumptruck", prompt="darken the wheels and rims",
      expect=dict(multiOp=True, opCount=1, opType="recolor",
                  targetNodes=["Object_20","Object_21","Object_22","Object_23"]),
      gold="(function(){ $S('.wheel').recolor('#222222'); })();"),

 # ── graceful refusal — NO positive DSL target ───────────────────────────────
 dict(id="merged-sheets", asset="merged-bed", prompt="make the bed sheets blue",
      expect=dict(mergedFail=True, target="GothicBed"), gold=None),
]

# ── THE 9 LABELING CASES (verbatim from editMatrix.js) ───────────────────────
LABELING = [
 dict(kind="material-named", asset="dump truck", desc='leaf, round, low, pair(left), material:"Rims"', gold=["wheel","tire","rim"]),
 dict(kind="material-named", asset="dump truck", desc='leaf, blocky, front, material:"Grille"', gold=["grille","grill"]),
 dict(kind="material-named", asset="dump truck", desc='leaf, small, back, pair(right), material:"Tail Light"', gold=["tail light","taillight","light","lamp"]),
 dict(kind="material-named", asset="dump truck", desc='leaf, flat, front, low, material:"Bumper"', gold=["bumper","fender","guard"]),
 dict(kind="material-named", asset="dump truck", desc='leaf, transparent, front, top, material:"Windshield"', gold=["windshield","windscreen","window","glass"]),
 dict(kind="material-named", asset="dump truck", desc='leaf, round, low, pair(right), material:"Rims"', gold=["wheel","tire","rim"]),
 dict(kind="descriptor-only", asset="dump truck", desc="leaf, large, open-top, center, largest", gold=["bed","dump bed","tray","bucket","cargo","flatbed","container"]),
 dict(kind="descriptor-only", asset="dump truck", desc="leaf, blocky, front, top", gold=["cab","cabin","roof","canopy"]),
 dict(kind="descriptor-only", asset="dump truck", desc="leaf, round, low, pair(left)", gold=["wheel","tire"]),
]


def applicable_tasks(case: dict) -> list[str]:
    """Which semantic dimensions this case actually has a gold for.

    Recorded per case so an aggregate denominator can never silently include a
    case that carries no expectation for that task.
    """
    e = case["expect"]
    if e.get("mergedFail"):
        return ["graceful-refusal"]
    out = ["op-selection", "selector-resolution"]
    if e.get("args"):
        out.append("arg-extraction")
    if e.get("multiOp"):
        out.append("multi-op")
    return out


def main() -> int:
    ident = identity_phi()
    phis = {"identity": ident, **{n: load_candidate(n) for n in LANGUAGES[1:]}}
    failures: list[str] = []
    records = []

    for case in CASES:
        rec = dict(case)
        rec["applicable_tasks"] = applicable_tasks(case)
        rec["scoring_family"] = ("graceful_refusal"
                                 if case["expect"].get("mergedFail") else "generation")
        gold = case["gold"]

        if gold is None:
            rec["gold_ir"] = None
            rec["gold_ir_hash"] = None
            rec["gold_renderings"] = None
            records.append(rec)
            continue

        # T1 — parses under identity
        try:
            ir = parse(gold, ident)
        except Exception as exc:
            failures.append(f"T1 {case['id']}: gold does not parse: {type(exc).__name__}: {exc}")
            continue
        ir_json = json.loads(canonical_json(ir))
        rec["gold_ir"] = ir_json
        rec["gold_ir_hash"] = content_hash(ir)

        # T2/T3 — the gold passes the case's own scorers
        scene = scene_for(case["asset"])
        scores = T.score_case(ir_json, case["expect"], scene)
        for task in rec["applicable_tasks"]:
            if task == "graceful-refusal":
                continue
            if scores.get(task, 0.0) != 1.0:
                failures.append(f"T3 {case['id']}: gold fails its own scorer {task}: {scores}")

        # T4 — every language parses back to the SAME canonical IR
        rend = {}
        for lang in LANGUAGES:
            phi = phis[lang]
            src = gold if lang == "identity" else phi_forward(gold, phi)
            try:
                back = parse(src, phi)
            except Exception as exc:
                failures.append(f"T4 {case['id']}/{lang}: does not parse back: {type(exc).__name__}: {exc}")
                continue
            if content_hash(back) != rec["gold_ir_hash"]:
                failures.append(f"T4 {case['id']}/{lang}: canonical IR differs from identity")
            rend[lang] = src
        rec["gold_renderings"] = rend
        records.append(rec)

    # T5 — the grader is not vacuous: a deliberately WRONG answer must FAIL
    scene = scene_for("dumptruck")
    wrong = json.loads(canonical_json(parse(
        "(function(){ $S('.cab').scale(2); })();", ident)))
    wb = CASES[0]["expect"]                                   # wheels-black
    bad = T.score_case(wrong, wb, scene)
    if bad["op-selection"] != 0.0 or bad["selector-resolution"] != 0.0:
        failures.append(f"T5: a wrong answer passed the scorers: {bad}")
    # and the RIGHT answer must pass
    right = json.loads(canonical_json(parse(CASES[0]["gold"], ident)))
    good = T.score_case(right, wb, scene)
    if any(v != 1.0 for v in good.values()):
        failures.append(f"T5: the gold answer failed the scorers: {good}")
    # '*' must NOT pass selector-resolution (the bleed guard)
    star = json.loads(canonical_json(parse("(function(){ $S('*').recolor('black'); })();", ident)))
    if T.score_case(star, wb, scene)["selector-resolution"] != 0.0:
        failures.append("T5: wildcard '*' passed selector-resolution (bleed guard broken)")

    payload = {
        "grammar_version": "3dom-grammar/1.1.0",
        "source": "docs/editor/js/ai/editMatrix.js",
        "languages": list(LANGUAGES),
        "counts": {
            "editing_requests": len(CASES),
            "multi_op_cases": sum(1 for c in CASES if c["expect"].get("multiOp")),
            "labeling_cases": len(LABELING),
            "graceful_refusal_cases": sum(1 for c in CASES if c["expect"].get("mergedFail")),
            "generation_cases": sum(1 for c in CASES if not c["expect"].get("mergedFail")),
        },
        "cases": records,
        "labeling_cases": LABELING,
    }

    if failures:
        print("VALIDATION FAILED — dataset NOT written\n")
        for f in failures:
            print("  -", f)
        return 1

    dest = sys.argv[1]
    blob = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(blob + "\n")
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    print(f"VERIFIED  {dest}")
    print(f"  cases                 {payload['counts']}")
    print(f"  sha256(dataset body)  {digest}")
    print("  T1 parse / T2 resolve / T3 scorers / T4 four-language IR identity / T5 grader sanity: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
