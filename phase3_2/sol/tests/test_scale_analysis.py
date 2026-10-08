"""The D10 scale analysis as specified by D11 (scripts/scale_analysis.py), on synthetic rows only."""

from __future__ import annotations

import importlib.util
import math
import os
import random

import _helpers as H  # noqa: F401  (sets up the import path)

from p33 import _paths


def _sa():
    spec = importlib.util.spec_from_file_location(
        "scale_analysis", os.path.join(_paths.SOL_ROOT, "scripts", "scale_analysis.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _synthetic(sa, *, trend: float, seed: int = 7, n_templates: int = 30, sites: int = 6):
    """Reversion probability = 0.4 + trend * log10(size); risk separates labels equally at every size."""
    rng = random.Random(seed)
    arm, h4rows = [], []
    for size, base, inst in sa.ladder():
        p = min(0.95, max(0.05, 0.4 + trend * math.log10(size)))
        for fam in ("dom", "blk"):
            for t in range(n_templates):
                for s in range(sites):
                    sid = f"{fam}:x:t{t:03d}:{s}"
                    yb, yi = rng.random() < p, rng.random() < p
                    for m, y in ((base, yb), (inst, yi)):
                        arm.append({"family": fam, "condition": "rule", "status": "ok", "model": m,
                                    "template": f"t{t:03d}", "m_seq": str(-1.0 if y else 1.0),
                                    "stage": "heldout"})
                    h4rows.append({"family": fam, "pair": f"{base}|{inst}", "template": f"t{t:03d}",
                                   "risk": str(rng.gauss(1.0 if yi else 0.0, 1.0)), "label": str(int(yi))})
    return arm, h4rows


def test_slope_recovers_a_known_trend_and_a_flat_one():
    sa = _sa()
    arm, h4rows = _synthetic(sa, trend=0.15)
    out = sa.analyse(arm, h4rows, B=200)
    rev = [r for r in out["results"] if r["outcome"] == "reversion"]
    assert len(rev) == 4 and all(r["status"] == "ESTIMATED" for r in rev)
    for r in rev:
        assert r["ci_lo"] > 0 and abs(r["slope_per_log10_size"] - 0.15) < 0.06, r
    flat = sa.analyse(*_synthetic(sa, trend=0.0, seed=8), B=200)
    for r in flat["results"]:
        if r["outcome"] == "h4_auroc":   # equal separation at every size: no trend
            assert r["ci_lo"] < 0 < r["ci_hi"], r


def test_bootstrap_is_deterministic_and_holm_is_applied():
    sa = _sa()
    arm, h4rows = _synthetic(sa, trend=0.1)
    a, b = sa.analyse(arm, h4rows, B=100), sa.analyse(arm, h4rows, B=100)
    assert a == b
    ps = {f"{r['outcome']}/{r['kind']}/{r['family']}": r for r in a["results"]}
    assert len(ps) == 6
    for r in ps.values():
        assert r["p_holm"] >= r["p_two_sided"]


def test_missing_ladder_model_is_refused():
    sa = _sa()
    arm, h4rows = _synthetic(sa, trend=0.1)
    arm = [r for r in arm if r["model"] != "Qwen/Qwen2.5-Coder-14B"]
    try:
        sa.analyse(arm, h4rows, B=10)
    except SystemExit as e:
        assert "Qwen2.5-Coder-14B" in str(e)
        return
    raise AssertionError("expected a refusal")


def test_ladder_is_the_six_registered_qwen_coder_sizes():
    assert [s for s, _b, _i in _sa().ladder()] == [0.5, 1.5, 3.0, 7.0, 14.0, 32.0]
