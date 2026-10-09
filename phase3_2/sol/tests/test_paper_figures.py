"""The paper-figure statistics (scripts/paper_figures.py), on synthetic rows only."""

from __future__ import annotations

import importlib.util
import os
import random

import _helpers as H  # noqa: F401  (sets up the import path)
from run_tests import needs

from p33 import _paths, h4


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_paths.SOL_ROOT, "scripts", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _synthetic(sa, *, seed=3, n_templates=12, sites=3):
    rng = random.Random(seed)
    arm, h4rows = [], []
    for _size, base, inst in sa.ladder():
        for t in range(n_templates):
            for _s in range(sites):
                yb, yi = rng.random() < 0.45, rng.random() < 0.45
                for m, y in ((base, yb), (inst, yi)):
                    arm.append({"family": "dom", "condition": "rule", "status": "ok", "model": m,
                                "template": f"t{t:03d}", "m_seq": str(-1.0 if y else 1.0)})
                # rounded scores, so that tied scores occur
                h4rows.append({"family": "dom", "pair": f"{base}|{inst}", "template": f"t{t:03d}",
                               "risk": str(round(rng.gauss(0.8 if yi else 0.0, 1.0), 1)), "label": str(int(yi))})
    return arm, h4rows


def test_figure_intervals_are_the_d11_intervals():
    """Same draws, same order statistics: the ladder intervals in the figures
    must equal the per-size intervals of the D11 scale analysis exactly."""
    needs("numpy", "matplotlib")
    import numpy as np
    sa, pf = _load("scale_analysis"), _load("paper_figures")
    arm, h4rows = _synthetic(sa)
    out = sa.analyse(arm, h4rows, B=pf.B, seed=pf.SEED)
    rec = {(r["outcome"], r["kind"]): r for r in out["results"] if r["family"] == "dom"}
    templates = sorted({r["template"] for r in arm})
    ti = {t: i for i, t in enumerate(templates)}
    for size, base, inst in sa.ladder():
        for kind, m in (("base", base), ("instruct", inst)):
            n, k = np.zeros(len(templates)), np.zeros(len(templates))
            for r in arm:
                if r["model"] == m:
                    n[ti[r["template"]]] += 1
                    k[ti[r["template"]]] += float(r["m_seq"]) < 0
            point, ci = pf.ratio(k, n, pf.draws(templates, f"dom/reversion/{kind}"))
            want = rec[("reversion", kind)]
            assert abs(point - want[f"value_{size:g}B"]) < 1e-12
            assert all(abs(a - b) < 1e-12 for a, b in zip(ci, want[f"ci_{size:g}B"])), (m, ci)
        rows = [r for r in h4rows if r["pair"] == f"{base}|{inst}"]
        point, ci = pf.auroc_w([float(r["risk"]) for r in rows], [int(r["label"]) for r in rows],
                               [ti[r["template"]] for r in rows], pf.draws(templates, "dom/h4_auroc/pair"))
        want = rec[("h4_auroc", "pair")]
        assert abs(point - want[f"value_{size:g}B"]) < 1e-12
        assert all(abs(a - b) < 1e-12 for a, b in zip(ci, want[f"ci_{size:g}B"])), (size, ci)


def test_weighted_auroc_equals_auroc_on_replicated_rows():
    """A template drawn w times counts w times, ties count one half."""
    needs("numpy", "matplotlib")
    import numpy as np
    pf = _load("paper_figures")
    rng = random.Random(11)
    scores = [round(rng.gauss(0, 1), 1) for _ in range(60)]
    labels = [int(rng.random() < 0.4 + 0.2 * (s > 0)) for s in scores]
    tix = [i % 7 for i in range(60)]
    assert abs(pf.auroc_w(scores, labels, tix)[0] - h4.auroc(scores, labels)) < 1e-12
    for _ in range(5):
        w = [rng.randrange(0, 3) for _ in range(7)]
        rep_s = [s for s, t in zip(scores, tix) for _ in range(w[t])]
        rep_y = [y for y, t in zip(labels, tix) for _ in range(w[t])]
        # every replicate carries the same weights, so the interval collapses onto that resample
        _, (lo, hi) = pf.auroc_w(scores, labels, tix, np.tile(np.array(w, float), (pf.B, 1)))
        assert abs(lo - h4.auroc(rep_s, rep_y)) < 1e-12 and abs(hi - lo) < 1e-12, (w, lo, hi)


def test_rows_are_grouped_by_family_with_one_header_each():
    needs("numpy", "matplotlib")
    pf = _load("paper_figures")
    models = ["deepseek-ai/deepseek-coder-1.3b-base", "Qwen/Qwen2.5-Coder-0.5B-Instruct",
              "Qwen/Qwen2.5-Coder-0.5B", "deepseek-ai/deepseek-coder-1.3b-instruct"]
    ypos, ticks = pf.rows_layout(models, pf.kind_label)
    labels = [lab for _, lab, _ in sorted(ticks, reverse=True)]
    assert labels == ["Qwen2.5-Coder", "0.5B base", "0.5B instruct",
                      "DeepSeek-Coder", "1.3B base", "1.3B instruct"], labels
    assert sum(1 for *_, head in ticks if head) == 2
    assert ypos["Qwen/Qwen2.5-Coder-0.5B"] > ypos["Qwen/Qwen2.5-Coder-0.5B-Instruct"]


def test_dodge_separates_neighbouring_sizes_and_keeps_order():
    needs("numpy", "matplotlib")
    pf = _load("paper_figures")
    ms = ["Qwen/Qwen2.5-Coder-32B", "deepseek-ai/deepseek-coder-33b-base", "Qwen/Qwen2.5-Coder-0.5B"]
    x = pf.dodge(ms)
    assert x["Qwen/Qwen2.5-Coder-32B"] < x["deepseek-ai/deepseek-coder-33b-base"]
    assert x["deepseek-ai/deepseek-coder-33b-base"] / x["Qwen/Qwen2.5-Coder-32B"] > 1.05
    assert abs(x["Qwen/Qwen2.5-Coder-0.5B"] - 0.5) < 1e-12      # alone: not moved
