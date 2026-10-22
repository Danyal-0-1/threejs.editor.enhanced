"""The Phase 4 fixes (phase4/scripts/fix_heldout_problems.py), on synthetic data only."""

from __future__ import annotations

import importlib.util
import math
import os
import random

from run_tests import needs

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "scripts", "fix_heldout_problems.py")


def _fx():
    needs("numpy", "matplotlib")
    spec = importlib.util.spec_from_file_location("fix_heldout_problems", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _logistic_data(seed=5, n_templates=20, per_template=30):
    rng = random.Random(seed)
    risk, lab, tpl = [], [], []
    for t in range(n_templates):
        for _ in range(per_template):
            x = rng.gauss(0, 1.5)
            risk.append(x)
            lab.append(int(rng.random() < 1 / (1 + math.exp(-(0.3 + 1.2 * x)))))
            tpl.append(f"t{t:03d}")
    return risk, lab, tpl


def test_template_folds_are_deterministic_and_balanced():
    fx = _fx()
    ts = [f"t{i:03d}" for i in range(80)]
    a, b = fx.template_folds(ts, "dom/x"), fx.template_folds(list(reversed(ts)), "dom/x")
    assert a == b                                            # independent of input order
    sizes = [sum(1 for v in a.values() if v == k) for k in range(fx.FOLDS)]
    assert sizes == [16] * fx.FOLDS, sizes
    assert fx.template_folds(ts, "blk/x") != a               # the key changes the assignment


def test_cross_fitted_probabilities_never_see_their_own_template():
    """Flipping one template's labels must not move that template's own predictions."""
    fx = _fx()
    risk, lab, tpl = _logistic_data()
    folds = fx.template_folds(sorted(set(tpl)), "dom/test")
    p1 = fx.cross_fitted_probs(risk, lab, tpl, folds)
    flipped = [1 - y if t == "t007" else y for y, t in zip(lab, tpl)]
    p2 = fx.cross_fitted_probs(risk, flipped, tpl, folds)
    own = [i for i, t in enumerate(tpl) if t == "t007"]
    other_fold = [i for i, t in enumerate(tpl) if folds[t] != folds["t007"]]
    assert all(p1[i] == p2[i] for i in own)                  # out of sample for its own rows
    assert any(p1[i] != p2[i] for i in other_fold)           # but it does train the other folds


def test_in_sample_slope_is_one_and_cross_fitted_is_not_exactly_one():
    fx = _fx()
    risk, lab, tpl = _logistic_data(seed=9)
    cal = fx.h4.logistic_fit(risk, lab)
    ins = fx.calibration_metrics(fx.platt_probs(cal, risk), lab, 10)
    assert abs(ins["cal_slope"] - 1.0) < 1e-6 and abs(ins["cal_intercept"]) < 1e-6
    folds = fx.template_folds(sorted(set(tpl)), "dom/test")
    cf = fx.calibration_metrics(fx.cross_fitted_probs(risk, lab, tpl, folds), lab, 10)
    assert abs(cf["cal_slope"] - 1.0) > 1e-6                 # the in-sample identity is gone
    assert 0.5 < cf["cal_slope"] < 1.5 and cf["ece"] < 0.1   # but a well-specified model stays calibrated


def test_h5_parts_split_exactly_and_weights_count_templates():
    import numpy as np
    fx = _fx()
    rng = np.random.default_rng(3)
    v = [rng.integers(0, 9, 12).astype(float) for _ in range(6)]
    v[3] = v[3] + 1                                          # at least one control site per template
    ones = np.ones((1, 12))
    r = fx.h5_parts(v, 3, ones)
    assert abs(r["all"][0] - ((v[1].sum() + v[4].sum() - v[2].sum() - v[5].sum()) / 3)) < 1e-12
    assert abs(r["all"][0] - (r["rep"][0] + r["ctl"][0])) < 1e-12
    assert abs(r["cdeg"][0] - (v[5].sum() - v[4].sum()) / v[3].sum()) < 1e-12
    W = np.zeros((1, 12))
    W[0, 4] = 2                                              # template 4 drawn twice, nothing else
    r2 = fx.h5_parts(v, 3, W)
    assert abs(r2["rep"][0] - 2 * (v[1][4] - v[2][4]) / 3) < 1e-12


def test_corrected_extraction_cuts_only_a_same_line_request():
    fx = _fx()
    raw = "Program: $S 'mesh' { duplicate 1, 2, 3; } Request: First, set the visibility of ..."
    assert fx.extract_corrected(raw) == "$S 'mesh' { duplicate 1, 2, 3; }"
    assert fx.extract_corrected("$S 'a' { move 1, 2, 3; } request : next") == "$S 'a' { move 1, 2, 3; }"
    plain = "```\n$S 'requests' { move 1, 0, 0; }\n```"
    assert fx.extract_corrected(plain) == fx.armb.extract_program(plain) == "$S 'requests' { move 1, 0, 0; }"


def test_two_sided_p_and_holm():
    import numpy as np
    fx = _fx()
    assert fx.two_sided_p(np.array([1.0, 2.0, 3.0, 4.0])) == 0.0
    assert fx.two_sided_p(np.array([-1.0, 1.0, 2.0, 3.0])) == 0.5
    adj = fx.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj == {"a": 0.03, "c": 0.06, "b": 0.06}
