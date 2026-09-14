"""score.py — generated text -> canonical IR -> per-dimension scores.

THE ONLY SCORING PATH IN THIS STUDY

    raw response
      -> frozen extraction (extract.py)
      -> lex/parse with the TARGET LANGUAGE's PhiMap (transpiler.parse)
      -> canonical shared IR (canonicalize)
      -> the Phase-1 scorers (grammar_and_3DOM_client/tasks.py) against the
         frozen gold

Surface-string equality is never used, and the browser's identity-only regex
parser is never used. An alien answer is graded by its MEANING, through the
same canonical IR an identity answer produces.

Parse validity and semantic correctness are kept in SEPARATE columns
(SCORING_POLICY.md S1) and never averaged.
"""
from __future__ import annotations

import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "alien_syntax", "src"))
sys.path.insert(0, os.path.join(REPO, "grammar_and_3DOM_client"))

import extract as E
import prompts as P
from transpiler import parse, longest_valid_prefix, LexError, ParseError, AmbiguityError
from canonicalize import canonical_json, content_hash, CanonicalisationError
import tasks as T
from fixture_scene import scene_for, resolve_all

# Hallucination categories. A parse failure is NOT a hallucination; these are
# specific, separately-counted content errors.
HALLUCINATION_CATEGORIES = (
    "invented_operation", "invented_selector", "invented_argument",
    "wrong_language_spelling", "extra_operation", "missing_operation",
    "prose_instead_of_code",
)


def _blank(case: dict, language: str) -> dict:
    return {
        "case_id": case["id"], "language": language,
        "scoring_family": case["scoring_family"],
        "raw_output_present": 0, "requested_language_compliance": 0,
        "extraction_rule": None, "extracted_code": "",
        "lex_valid": 0, "parse_valid": 0, "schema_valid": 0, "vacuous": 0,
        "ir_exact_match": 0, "op_correct": 0, "selector_correct": 0,
        "args_correct": 0, "multi_op_correct": 0, "labeling_correct": None,
        "all_components_correct": 0, "semantic_correct": 0,
        "refusal_correct": None,
        "nlvp": 0.0, "lvp_tokens": 0, "reference_dsl_tokens": None,
        "outcome": E.HARNESS_ERROR, "error_category": None,
        "scorer_explanation": "", "hallucinations": [],
        "emitted_ops": None, "resolved_nodes": None, "ir_hash": None,
    }


def _language_compliance(code: str, language: str) -> int:
    """Did the model answer in the language it was asked for?

    Operational test: the code lexes under the TARGET language's φ but the
    verb/entry spellings it uses belong to that language. The cheap, decisive
    check is the selector-entry spelling, which is mandatory in every program
    and differs across all four languages.
    """
    phi = P.phi_for(language)
    entry = phi.spelling("T_SELECTOR_ENTRY")
    if entry in code:
        return 1
    # An empty program is compliant-by-vacuity only if it has no entry at all
    # in ANY language; otherwise it answered in the wrong one.
    for other in P.LANGUAGES:
        if other == language:
            continue
        if P.phi_for(other).spelling("T_SELECTOR_ENTRY") in code:
            return 0
    return 1 if code.strip() else 0


def _hallucinations(case: dict, ir_json: dict, language: str,
                    compliance: int, code: str, resolved) -> list[str]:
    out: list[str] = []
    if not compliance:
        out.append("wrong_language_spelling")
    expect = case["expect"]
    gold_ir = case.get("gold_ir")
    ops = T.ops_of(ir_json)
    if gold_ir is not None:
        want_n = len(gold_ir.get("ops", []))
        if len(ops) > want_n:
            out.append("extra_operation")
        elif len(ops) < want_n:
            out.append("missing_operation")
    # a selector that resolves to nothing at all names parts the scene lacks
    if ops and resolved is not None and all(len(s) == 0 for s in resolved):
        out.append("invented_selector")
    return out


def score_response(response: str, case: dict, language: str) -> dict:
    """Grade one raw model response. Never raises; never repairs the output."""
    r = _blank(case, language)
    phi = P.phi_for(language)
    entry = phi.spelling("T_SELECTOR_ENTRY")

    r["raw_output_present"] = 1 if isinstance(response, str) and response.strip() else 0
    code, rule = E.extract_code(response or "", entry)
    r["extraction_rule"] = rule
    r["extracted_code"] = code

    if not code:
        r["outcome"] = E.PARSE_FAIL
        r["error_category"] = "empty_response"
        r["scorer_explanation"] = "model produced no text"
        r["hallucinations"] = ["prose_instead_of_code"]
        return r

    r["requested_language_compliance"] = _language_compliance(code, language)
    if entry not in code:
        r["hallucinations"].append("prose_instead_of_code")

    # ── lex / parse under the TARGET language ───────────────────────────────
    try:
        lvp, _state, _legal = longest_valid_prefix(code, phi)
        r["lvp_tokens"] = int(lvp)
    except Exception:
        r["lvp_tokens"] = 0

    gold_ir = case.get("gold_ir")
    if gold_ir is not None:
        try:
            from transpiler import token_types
            ref = len(token_types(case["gold_renderings"][language], phi))
            r["reference_dsl_tokens"] = ref
            r["nlvp"] = round(r["lvp_tokens"] / ref, 6) if ref else 0.0
        except Exception:
            r["reference_dsl_tokens"] = None

    try:
        ir = parse(code, phi)
        r["lex_valid"] = 1
        r["parse_valid"] = 1
    except LexError as exc:
        r["outcome"] = E.LEX_FAIL
        r["error_category"] = f"LexError: {exc}"[:200]
        r["scorer_explanation"] = "the lexer could not tokenise the output"
        r["hallucinations"] = (["wrong_language_spelling"]
                               if not r["requested_language_compliance"] else [])
        return r
    except (ParseError, AmbiguityError) as exc:
        r["lex_valid"] = 1
        r["outcome"] = E.PARSE_FAIL
        r["error_category"] = f"{type(exc).__name__}: {exc}"[:200]
        r["scorer_explanation"] = "tokenised, but no derivation exists"
        r["hallucinations"] = (["wrong_language_spelling"]
                               if not r["requested_language_compliance"] else [])
        return r
    except Exception as exc:
        r["outcome"] = E.HARNESS_ERROR
        r["error_category"] = f"{type(exc).__name__}: {exc}"[:200]
        return r

    try:
        ir_json = json.loads(canonical_json(ir))
        r["ir_hash"] = content_hash(ir)
        r["schema_valid"] = 1 if T.has_grammar_version(ir_json) else 0
    except CanonicalisationError as exc:
        r["outcome"] = E.HARNESS_ERROR
        r["error_category"] = f"CanonicalisationError: {exc}"[:200]
        return r

    ops = T.ops_of(ir_json)
    r["emitted_ops"] = [{"op": o.get("op"),
                         "selector": (o.get("selector") or {}).get("raw"),
                         "args": o.get("args", {})} for o in ops]
    scene = scene_for(case["asset"])
    resolved = resolve_all(ops, scene)
    r["resolved_nodes"] = [sorted(s) for s in resolved]

    # ── graceful refusal family — scored separately, never pooled ───────────
    if case["scoring_family"] == "graceful_refusal":
        ok, why = T.score_selector_resolution_report(ir_json, [], scene, merged_fail=True)
        r["refusal_correct"] = int(ok == 1.0)
        r["vacuous"] = 1 if T.is_vacuous(ir_json) else 0
        r["outcome"] = E.VALID_CORRECT if r["refusal_correct"] else E.VALID_WRONG
        r["scorer_explanation"] = "; ".join(why)
        if not r["requested_language_compliance"]:
            r["hallucinations"].append("wrong_language_spelling")
            r["outcome"] = E.VALID_WRONG
            r["refusal_correct"] = 0
        return r

    # ── D5: valid but vacuous ───────────────────────────────────────────────
    if T.is_vacuous(ir_json):
        r["vacuous"] = 1
        r["outcome"] = E.VALID_VACUOUS
        r["scorer_explanation"] = "parses, zero operations (D5)"
        return r

    # ── the per-dimension scorers ───────────────────────────────────────────
    expect = case["expect"]
    expected_ops = expect.get("ops")
    types = ([o.get("opType") for o in expected_ops] if expected_ops
             else ([expect["opType"]] if expect.get("opType") else None))
    targets = ([o.get("targetNodes", []) for o in expected_ops] if expected_ops
               else expect.get("targetNodes", []))
    count = expect.get("opCount", len(expected_ops) if expected_ops else 1)

    why: list[str] = []
    ok, w = T.score_op_selection_report(ir_json, types or []);        r["op_correct"] = int(ok); why += w
    ok, w = T.score_selector_resolution_report(ir_json, targets, scene); r["selector_correct"] = int(ok); why += w
    ok, w = T.score_arg_extraction_report(ir_json, expect.get("args")); r["args_correct"] = int(ok); why += w
    ok, w = T.score_multi_op_report(ir_json, count, types);           r["multi_op_correct"] = int(ok); why += w

    applicable = case["applicable_tasks"]
    per_task = {"op-selection": r["op_correct"], "selector-resolution": r["selector_correct"],
                "arg-extraction": r["args_correct"], "multi-op": r["multi_op_correct"]}
    r["all_components_correct"] = int(all(per_task[t] for t in applicable))

    if case.get("gold_ir_hash"):
        r["ir_exact_match"] = int(r["ir_hash"] == case["gold_ir_hash"])

    # SEMANTIC CORRECTNESS = every dimension the case declares, AND the answer
    # was written in the language that was asked for. A 3DOM answer in the
    # gamma arm is not a gamma success.
    r["semantic_correct"] = int(r["all_components_correct"]
                                and r["requested_language_compliance"])
    r["outcome"] = E.VALID_CORRECT if r["semantic_correct"] else E.VALID_WRONG
    r["scorer_explanation"] = "; ".join(why)[:600]
    r["hallucinations"] += _hallucinations(case, ir_json, language,
                                           r["requested_language_compliance"],
                                           code, resolved)
    if not r["op_correct"] and ops:
        r["hallucinations"].append("invented_operation")
    if not r["args_correct"] and expect.get("args"):
        r["hallucinations"].append("invented_argument")
    r["hallucinations"] = sorted(set(r["hallucinations"]))
    return r


def score_labeling(response: str, gold: list[str]) -> dict:
    """Labeling probe — language-independent control task."""
    ok, why = T.score_labeling_report(response, gold)
    return {"labeling_correct": int(ok), "scorer_explanation": "; ".join(why)}
