"""H4 metrics and criteria, Arm B, H5 IR proof, H2 and power."""

from __future__ import annotations

import _helpers as H  # noqa: F401
import canonicalize as C
import phi as P

from phase3_2 import templates as TM
from phase3_2.backends import BACKENDS

from p33 import armb, h2, h4, h5, power

TEMPS = TM.build_templates()


# ---------------------------------------------------------------------------
# H4
# ---------------------------------------------------------------------------

def test_h4_metrics_against_hand_values():
    assert h4.auroc([3, 2, 1, 0], [1, 1, 0, 0]) == 1.0
    assert h4.auroc([1, 1, 1, 1], [1, 1, 0, 0]) == 0.5
    assert h4.auroc([1, 2], [1, 1]) is None
    assert abs(h4.auprc([3, 2, 1], [1, 0, 1]) - (1 + 2 / 3) / 2) < 1e-12
    assert h4.precision_at_k([3, 2, 1], [1, 0, 1], 2) == 0.5
    assert abs(h4.brier([0.1, 0.9], [0, 1]) - 0.01) < 1e-12
    assert abs(h4.ece([0.1, 0.9], [0, 1]) - 0.1) < 1e-12


def test_calibration_of_a_fitted_model_is_identity():
    x, y = [-2, -1, 0, 1, 2, 3], [0, 0, 1, 0, 1, 1]
    a, b = h4.logistic_fit(x, y)
    a2, b2 = h4.calibration_slope_intercept([h4._sigmoid(a + b * v) for v in x], y)
    assert abs(a2) < 1e-6 and abs(b2 - 1) < 1e-6


def _table_rows(n_templates=12, lex="d50s1"):
    rows = []
    for t in range(n_templates):
        for j in range(3):
            risk = (t * 3 + j) / 10
            rows.append({"pair": "B|I", "site_id": f"s{t}_{j}", "family": "dom",
                         "lexicon": lex, "template": f"t{t:03d}", "terminal": f"T{j}",
                         "stratum": "sigil", "split": "DEVELOPMENT", "risk": risk,
                         "label": int(risk > 1.5), "identity": 1.0,
                         "length": float(j), "program_nll": float(t % 3),
                         "token_count": 2.0})
    h4._crossfit_terminal_rate(rows)
    return rows


def test_identity_baseline_is_constant_on_semantic_sites():
    rows = _table_rows()
    assert h4.auroc([r["identity"] for r in rows], [r["label"] for r in rows]) == 0.5


def test_criteria_c3_not_testable_without_a_valid_grammar():
    ms = h4.evaluate_group(_table_rows(), calibration=None, threshold=None,
                           ks=[5], bins=10, B=200, seed=1, min_clusters=8)
    crit = {c["criterion"]: c for c in h4.criteria(ms, grammar_valid=False)}
    assert crit["C3_auroc_heldout_grammar"]["status"] == "NOT TESTABLE"
    assert "D1" in crit["C3_auroc_heldout_grammar"]["detail"]
    assert crit["C1_delta_vs_identity"]["status"] in ("MET", "NOT MET")
    assert "p_holm" in crit["C1_delta_vs_identity"]


def test_single_class_labels_are_not_estimable_not_a_crash():
    rows = _table_rows()
    for r in rows:
        r["label"] = 1
    ms = h4.evaluate_group(rows, calibration=None, threshold=None, ks=[5], bins=10,
                           B=100, seed=1, min_clusters=8)
    d = [m for m in ms if m["predictor"].startswith("delta_vs_")]
    assert d and all("NOT ESTIMABLE" in m["ci_status"] for m in d)


def test_build_table_pairs_base_with_instruct_on_site():
    def row(model, sid, m):
        return {"model": model, "site_id": sid, "condition": "rule", "status": "ok",
                "m_seq": m, "family": "dom", "lexicon": "d50s1", "template": "t000",
                "terminal": "T", "stratum": "sigil", "split": "DEVELOPMENT",
                "model_revision": "r", "tokenizer_id": "k", "correct": "#",
                "competitor": ".", "n_tok_correct": 1, "n_tok_competitor": 1,
                "program_nll_per_char": 1.0}
    rows = [row(H.DEV_BASE, "s1", 0.5), row(H.DEV_INST, "s1", -0.2),
            row(H.DEV_BASE, "s2", -1.0)]
    t = h4.build_table(rows)
    assert len(t) == 1 and t[0]["risk"] == -0.5 and t[0]["label"] == 1
    assert t[0]["model_revision"] == "r|r"


# ---------------------------------------------------------------------------
# Arm B
# ---------------------------------------------------------------------------

def test_nl_rendering_is_deterministic_and_complete():
    a = [armb.describe_program(t.ir) for t in TEMPS]
    assert a == [armb.describe_program(t.ir) for t in TEMPS]
    assert all(x.endswith(".") and len(x) > 10 for x in a)


def test_extraction_and_layout_normalisation():
    assert armb.extract_program("```js\n$S '#a' { delete; }\n```") == "$S '#a' { delete; }"
    assert armb.extract_program("Program: (function(){})();") == "(function(){})();"
    assert armb.normalize_layout("$S ( '.a  b' ) ;") == "$S('.a  b');"


def test_five_bucket_evaluation():
    L, be = P.load_candidate("d50s1"), BACKENDS["dom"]
    t = TEMPS[0]
    target = C.content_hash(t.ir)
    good = be.render(t.ir, L)
    assert armb.evaluate(good, be, L, target)["bucket"] == "VALID_CORRECT"
    assert armb.evaluate("", be, L, target)["bucket"] == "LEX_FAIL"
    assert armb.evaluate("(function(){ $S(", be, L, target)["bucket"] in ("LEX_FAIL", "PARSE_FAIL")
    assert armb.evaluate("(function(){})();", be, L, target)["bucket"] == "VALID_VACUOUS"


def test_reach_and_conditional_reversion_are_separate():
    import phase3_2.sites2 as S
    L, be = P.load_candidate("d50s1"), BACKENDS["dom"]
    text = be.render(TEMPS[0].ir, L)
    s = next(x for x in S.classify(text, L, be, identity=P.identity_phi()) if x.is_usable)
    assert armb.observe(text, s)["outcome"] == "correct"
    assert armb.observe(s.variant_program, s)["outcome"] == "reverted"
    assert armb.observe("nonsense", s)["outcome"] == "not_reached"
    h = armb.hurdle([armb.observe(text, s), armb.observe(s.variant_program, s),
                     armb.observe("x", s), armb.observe("y", s)])
    assert h["p_reach"] == 0.5 and h["p_revert_given_reach"] == 0.5
    assert "product_reported_alongside" in h


# ---------------------------------------------------------------------------
# H5: whole-corpus IR equality
# ---------------------------------------------------------------------------

def test_every_arm_preserves_ir_over_the_whole_corpus():
    L = P.load_candidate("d50s1")
    arms = h5.define_arms(L, {"T_CLASS_SIGIL": 2.0, "T_VERB_MOVE": 1.0}, budget=3, seeds=[1])
    for arm, sd, roles in arms:
        L2 = h5.repaired_phi("d50s1", roles, f"h5t_{arm}_{sd}")
        pr = h5.ir_proof(L, L2)
        assert pr["passed"] and pr["n_checked"] == 2 * len(h5.proof_corpus()), (arm, pr)


def test_ir_proof_can_fail():
    """The proof is not vacuous: break rendering for one family, it must fail."""
    L = P.load_candidate("d50s1")
    L2 = h5.repaired_phi("d50s1", ["T_TYPE_MESH"], "h5t_break")
    be = BACKENDS["blk"]
    orig = be.render

    def broken(ir, phi):
        if phi.phi_id == L2.phi_id and ir.ops:
            return orig(C.IRProgram(ir.ops[:-1] or ir.ops), phi) if len(ir.ops) > 1 else orig(ir, phi)
        return orig(ir, phi)
    be.render = broken
    try:
        pr = h5.ir_proof(L, L2)
    finally:
        be.render = orig
    assert not pr["passed"] and pr["n_mismatch"] > 0


def test_repair_respects_i7_overload_group():
    L2 = h5.repaired_phi("d50s1", ["T_CLASS_SIGIL"], "h5t_i7")
    assert L2.spelling("T_CHAIN_OP") == L2.spelling("T_CLASS_SIGIL") != "#"


def test_targeted_arm_ranks_by_base_risk_and_random_is_seeded():
    L = P.load_candidate("d50s1")
    arms = h5.define_arms(L, {"T_TYPE_MESH": 9, "T_VERB_MOVE": 8, "T_ID_SIGIL": 7},
                          budget=2, seeds=[1, 2])
    assert arms[0] == ("targeted", 0, ["T_TYPE_MESH", "T_VERB_MOVE"])
    again = h5.define_arms(L, {}, budget=2, seeds=[1, 2])
    assert [a for a in arms if a[0] == "random"] == [a for a in again if a[0] == "random"]
    assert arms[-1][0] == "global" and len(arms[-1][2]) == len(h5.remapped_roles(L))


# ---------------------------------------------------------------------------
# H2, power
# ---------------------------------------------------------------------------

def test_h2_is_not_testable_without_calibration():
    r = h2.evaluate(None)
    assert r["status"] == "NOT TESTABLE" and "circular" in r["reason"]


def test_h2_machinery_reports_three_scales_when_cells_exist():
    from phase3.scoring import MarginRecord
    mk = lambda v: [MarginRecord("s", "m", 0, 0, 0, x, 1, 1, True) for x in v]  # noqa: E731
    r = h2.evaluate({("strong", "high"): mk([-3, -2, -1, .5]), ("strong", "low"): mk([-1.5, -.5, 1, 2]),
                     ("neutral", "high"): mk([-1, .5, 1, 1.5]), ("neutral", "low"): mk([-.5, 1, 1.5, 2])})
    assert r["sign_agrees"] and r["directions_as_expected"]


def test_power_refuses_heldout_pilot_data():
    try:
        power.pilot_from_rows([{"split": "HELDOUT", "label": 1}])
    except power.HeldoutLeak:
        return
    raise AssertionError("held-out rows were accepted as pilot data")


def test_power_is_monotone_in_effect_and_size():
    p = lambda A, T: power.h4_power(A, n_templates=T, m=4, prevalence=0.4, icc=0.1)  # noqa: E731
    assert p(0.55, 80) < p(0.70, 80) < p(0.85, 80)
    assert p(0.70, 20) < p(0.70, 80) < p(0.70, 320)


def test_icc_estimator_hand_example():
    rows = [{"template": "a", "v": 1}, {"template": "a", "v": 1},
            {"template": "b", "v": 0}, {"template": "b", "v": 0}]
    assert power.icc_binary(rows, value="v") == 1.0
    rows2 = [{"template": "a", "v": 1}, {"template": "a", "v": 0},
             {"template": "b", "v": 1}, {"template": "b", "v": 0}]
    assert power.icc_binary(rows2, value="v") == 0.0
