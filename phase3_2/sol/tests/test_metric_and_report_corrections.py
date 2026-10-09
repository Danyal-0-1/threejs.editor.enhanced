"""Regression tests for the 2026-10-07 analysis corrections (deviation D9).

  * AP and precision@k with tied scores: grouped thresholds, row order cannot matter;
  * power: one row per (template count, ICC) scenario, computed with its OWN ICC;
  * POWER_ANALYSIS.md: every ICC scenario, the pilot flagged, zero power kept;
  * RUN_SUMMARY.md: artifact counts right on a first AND a repeated export;
  * figures, tables and reports agree; figure footers pair each model with its revision.

Every fixture lives in a temporary results root: nothing here reads or writes
the real development run.
"""

from __future__ import annotations

import csv
import json
import os
import random
import re

import _helpers as H
from run_tests import needs

from p33 import artifacts, export, h4, pipeline as PL, power, reports
from p33.fakes import FakeScorer


# ---------------------------------------------------------------------------
# the PREVIOUS algorithms, verbatim: references for "unchanged on distinct scores"
# ---------------------------------------------------------------------------

def _old_auprc(scores, labels):
    P = sum(labels)
    if P == 0:
        return None
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    tp, ap = 0, 0.0
    for rank, i in enumerate(order, 1):
        if labels[i]:
            tp += 1
            ap += tp / rank
    return ap / P


def _old_p_at_k(scores, labels, k):
    if not scores:
        return None
    order = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
    return sum(labels[i] for i in order) / len(order)


def _raises(fn, exc):
    try:
        fn()
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__}")


def _tied_data(n=60, seed=3):
    rng = random.Random(seed)
    scores = [rng.choice([0.1, 0.5, 0.5, 0.9, 2.0]) for _ in range(n)]
    labels = [int(rng.random() < 0.3 + 0.2 * s) for s in scores]
    return scores, labels


def _shuffles(scores, labels, n=25, seed=11):
    rng = random.Random(seed)
    idx = list(range(len(scores)))
    for _ in range(n):
        rng.shuffle(idx)
        yield [scores[i] for i in idx], [labels[i] for i in idx]


# ---------------------------------------------------------------------------
# AP
# ---------------------------------------------------------------------------

def test_auprc_constant_score_equals_prevalence():
    for labels in ([1, 0], [0, 1], [1, 1, 0, 0, 0], [0, 0, 0, 1]):
        assert abs(h4.auprc([7.0] * len(labels), labels) - sum(labels) / len(labels)) < 1e-12
    assert h4.auprc([1, 1], [1, 0]) == h4.auprc([1, 1], [0, 1]) == 0.5   # the confirmed defect


def test_auprc_is_invariant_to_permutations_within_ties():
    s, y = _tied_data()
    ref = h4.auprc(s, y)
    assert all(h4.auprc(a, b) == ref for a, b in _shuffles(s, y))


def test_auprc_hand_example_five_sixths():
    # thresholds 3 -> P=1, R=1/2; {2,2} -> P=2/3, R=1; 1 -> R unchanged
    assert abs(h4.auprc([3, 2, 2, 1], [1, 0, 1, 0]) - 5 / 6) < 1e-12


def test_auprc_unchanged_for_distinct_scores():
    rng = random.Random(5)
    for _ in range(20):
        n = rng.randint(2, 80)
        s = rng.sample(range(10_000), n)
        y = [rng.randint(0, 1) for _ in range(n)]
        assert h4.auprc(s, y) == _old_auprc(s, y)         # bit-identical


def test_auprc_degenerate_conventions():
    assert h4.auprc([], []) is None                       # no positive class: undefined
    assert h4.auprc([1.0, 2.0], [0, 0]) is None
    assert h4.auprc([1.0, 2.0], [1, 1]) == 1.0
    _raises(lambda: h4.auprc([float("nan"), 1.0], [1, 0]), ValueError)
    _raises(lambda: h4.auprc([1.0, 2.0], [1, 2]), ValueError)
    _raises(lambda: h4.auprc([1.0], [1, 0]), ValueError)


# ---------------------------------------------------------------------------
# precision@k
# ---------------------------------------------------------------------------

def test_precision_at_k_constant_score_equals_prevalence():
    y = [1, 0, 0, 1, 0, 0, 0]
    prevalence = sum(y) / len(y)                          # 2/7
    for k in range(1, len(y) + 4):                        # including k > n
        assert abs(h4.precision_at_k([3.3] * len(y), y, k) - prevalence) < 1e-12


def test_precision_at_k_boundary_ties_are_permutation_invariant():
    s, y = _tied_data()
    for k in (1, 5, 10, 17, 40, 60, 99):
        ref = h4.precision_at_k(s, y, k)
        assert all(abs(h4.precision_at_k(a, b, k) - ref) < 1e-12 for a, b in _shuffles(s, y))


def test_precision_at_k_hand_example_three_quarters():
    # score 3 is in; one of the two 2s is drawn: 0.5 expected positives
    assert h4.precision_at_k([3, 2, 2, 1], [1, 0, 1, 0], 2) == 0.75
    assert h4.precision_at_k([3, 2, 2, 1], [1, 0, 1, 0], 3) == 2 / 3   # boundary not cut


def test_precision_at_k_unchanged_for_distinct_scores():
    rng = random.Random(9)
    for _ in range(20):
        n = rng.randint(1, 60)
        s = rng.sample(range(10_000), n)
        y = [rng.randint(0, 1) for _ in range(n)]
        for k in (1, 3, 10, 50, 100):
            assert h4.precision_at_k(s, y, k) == _old_p_at_k(s, y, k)


def test_precision_at_k_edge_cases():
    assert h4.precision_at_k([], [], 5) is None
    assert h4.precision_at_k([2, 1], [1, 0], 10) == 0.5    # K = n: the whole set
    for bad in (0, -1, 2.5, True, "3", None):
        _raises(lambda bad=bad: h4.precision_at_k([2, 1], [1, 0], bad), ValueError)

    class Idx:                                            # integer-like (e.g. numpy) k is fine
        def __index__(self):
            return 1
    assert h4.precision_at_k([2, 1], [1, 0], Idx()) == 1.0


def test_curves_use_the_same_grouped_thresholds_as_the_metrics():
    s, y = _tied_data()
    pr = h4.pr_curve(s, y)
    P = sum(y)
    ap, prev_r = 0.0, 0.0
    for r, p in pr:
        ap += (r - prev_r) * p
        prev_r = r
    assert abs(ap - h4.auprc(s, y)) < 1e-12
    roc = h4.roc_curve(s, y)
    area = sum((x1 - x0) * (y0 + y1) / 2 for (x0, y0), (x1, y1) in zip(roc, roc[1:]))
    assert abs(area - h4.auroc(s, y)) < 1e-12 and P > 0


# ---------------------------------------------------------------------------
# the actual H4 table -> evaluation path is row-order invariant
# ---------------------------------------------------------------------------

def _arm_a_pair_rows(n_templates=14, seed=1):
    rng = random.Random(seed)
    rows = []
    for t in range(n_templates):
        for j in range(4):
            sid = f"dom:d50s1:t{t:03d}:T{j}:0"
            base = rng.gauss(0.2 * (j - 1.5), 1.0)
            for model, m in (("Qwen/Qwen2.5-Coder-0.5B", base),
                             ("Qwen/Qwen2.5-Coder-0.5B-Instruct", base + rng.gauss(0.3, 0.8))):
                rows.append({"condition": "rule", "status": "ok", "model": model,
                             "model_revision": "rev", "tokenizer_id": "tok", "site_id": sid,
                             "family": "dom", "lexicon": "d50s1", "template": f"t{t:03d}",
                             "terminal": f"T{j}", "stratum": "sigil", "split": "DEVELOPMENT",
                             "m_seq": m, "correct": "#", "competitor": ".",
                             "n_tok_correct": 1 + j % 2, "n_tok_competitor": 1,
                             "program_nll_per_char": 1.0 + (t % 3) / 10})
    return rows


def _close(a, b):
    if isinstance(a, float) and isinstance(b, float):
        return abs(a - b) <= 1e-12 * max(1.0, abs(a))
    return a == b


def test_h4_evaluation_is_invariant_to_row_order():
    table = h4.build_table(_arm_a_pair_rows())
    kw = dict(calibration=None, threshold=None, ks=[5, 10], bins=10, B=200, seed=1, min_clusters=8)
    ref = h4.evaluate_group(table, **kw)
    rng = random.Random(4)
    for _ in range(3):
        shuffled = table[:]
        rng.shuffle(shuffled)
        got = h4.evaluate_group(shuffled, **kw)
        assert len(got) == len(ref)
        for a, b in zip(ref, got):
            assert a.keys() == b.keys()
            assert all(_close(a[k], b[k]) for k in a), (a["predictor"], [k for k in a if not _close(a[k], b[k])])
    ident = [m for m in ref if m["predictor"] == "identity"][0]
    assert abs(ident["auprc"] - ident["prevalence"]) < 1e-12       # constant baseline = prevalence
    assert abs(ident["p_at_5"] - ident["prevalence"]) < 1e-12


# ---------------------------------------------------------------------------
# power
# ---------------------------------------------------------------------------

def _power_inputs(n_templates=30, seed=2):
    rng = random.Random(seed)
    table, arm = [], []
    for t in range(n_templates):
        u = rng.gauss(0, 0.8)
        for j in range(3):
            sid = f"s{t}_{j}"
            risk = rng.gauss(u, 1)
            table.append({"pair": "B|I", "model": "B|I", "model_revision": "r|r", "template": f"t{t}",
                          "lexicon": "d50s1", "split": "DEVELOPMENT", "risk": risk,
                          "label": int(risk + rng.gauss(0, 1) > 0.3)})
            for model in ("A", "B"):
                d = rng.gauss(0.15 + 0.5 * u, 1.0)
                for cond, m in (("rule", d), ("norule", 0.0)):
                    arm.append({"status": "ok", "condition": cond, "model": model, "site_id": sid,
                                "template": f"t{t}", "lexicon": "d50s1", "split": "DEVELOPMENT",
                                "m_seq": m})
    return table, arm


def test_power_scenarios_are_unique_and_each_uses_its_own_icc():
    table, arm = _power_inputs()
    rows = power.analyse(table, arm, [], [], corpus_templates=80)
    prev = sum(r["label"] for r in table) / len(table)
    prev_c = max(min(prev, .99), .01)
    m_h4 = len(table) / 30
    icc_h4 = power.icc_binary(table, value="label")
    scen_h4 = [ic for ic, _src in power.icc_scenarios(icc_h4)]
    for an in ("h4_criterion1", "h4_smallest_detectable_auroc", "rule_effect"):
        rs = [r for r in rows if r["analysis"] == an]
        keys = [(r["n_templates"], r["icc"], r.get("true_auroc")) for r in rs]
        assert len(keys) == len(set(keys)), f"{an}: duplicate scenario keys"
        for T in power.GRID_T:
            assert sum(1 for r in rs if r["n_templates"] == T and r["is_pilot_icc"]
                       and r.get("true_auroc") in (None, power.GRID_A[0])) == 1, (an, T)
    sde = [r for r in rows if r["analysis"] == "h4_smallest_detectable_auroc"]
    assert {(r["n_templates"], r["icc"]) for r in sde} == {(T, ic) for T in power.GRID_T for ic in scen_h4}
    for r in rows:
        if r["analysis"] == "h4_criterion1":
            want = power.h4_power(r["true_auroc"], n_templates=r["n_templates"], m=m_h4,
                                  prevalence=prev_c, icc=r["icc"])
            assert r["power"] == want
        if r["analysis"] == "h4_smallest_detectable_auroc":
            def fn(a, r=r):
                return power.h4_power(a, n_templates=r["n_templates"], m=m_h4, prevalence=prev_c, icc=r["icc"])
            first = next((a for a in power.SDE_GRID if fn(a) >= power.POWER_TARGET), None)
            assert r["value"] == first, (r["n_templates"], r["icc"])
            assert (r["value_status"] == "reached") == (first is not None)
            if first is not None:
                assert r["power_at_value"] == fn(first)
        if r["analysis"] in ("h4_criterion1", "rule_effect", "h4_smallest_detectable_auroc"):
            assert r["t_status"].startswith("HYPOTHETICAL") == (r["n_templates"] > 80)
    diffs = {}
    for a in arm:
        diffs.setdefault((a["model"], a["site_id"]), {})[a["condition"]] = a
    d = [v["rule"]["m_seq"] - v["norule"]["m_seq"] for v in diffs.values()]
    import statistics as st
    m_r = len(d) / 30
    for r in rows:
        if r["analysis"] == "rule_effect":
            assert r["power"] == power.rule_power(st.mean(d), st.pstdev(d), n_templates=r["n_templates"],
                                                  m=m_r, icc=r["icc"])
            assert abs(r["effective_n"] - r["n_templates"] * m_r / (1 + (m_r - 1) * r["icc"])) < 1e-9


def test_power_not_reached_is_explicit():
    table, arm = _power_inputs()
    saved = power.h4_power
    power.h4_power = lambda *a, **k: 0.0          # a design where nothing reaches the target
    try:
        rows = power.analyse(table, arm, [], [], corpus_templates=80)
    finally:
        power.h4_power = saved
    sde = [r for r in rows if r["analysis"] == "h4_smallest_detectable_auroc"]
    assert sde and all(r["value"] is None and r["value_status"].startswith("NOT REACHED") for r in sde)


# ---------------------------------------------------------------------------
# reports and figures read the corrected tables faithfully
# ---------------------------------------------------------------------------

_STATE: dict = {}


def _fake_run():
    """A small fake development run in its own temporary results root."""
    if "run" not in _STATE:
        cfg = H.small_cfg(run_id="dev-corrections", site_limit=24, primary_sites=12)
        rd = os.path.join(H.tmpdir("p33_corr_"), cfg.run_id)
        pins = H.fake_pins(cfg)
        for exp in ("arm_a", "primary"):
            PL.run(cfg, rd, exp, scorer_factory=lambda m: FakeScorer(m), pins=pins)
            PL.merge(cfg, rd, exp, pins=pins)
        export.export_all(rd, cfg)
        _STATE["run"] = (cfg, rd)
    return _STATE["run"]


def _pivot_cells(md: str, heading: str) -> dict:
    """{(icc, T): cell} from the pivot table under `heading` in a report."""
    sec = md[md.index(heading):]
    lines = [l for l in sec.splitlines() if l.startswith("|")]
    head = [c.strip() for c in lines[0].strip("|").split("|")]
    Ts = [int(re.sub(r"\D", "", h)) for h in head[2:]]
    out = {}
    for l in lines[2:]:
        cells = [c.strip() for c in l.strip("|").split("|")]
        if len(cells) != len(head) or not re.match(r"^\d", cells[0]):
            break
        for T, c in zip(Ts, cells[2:]):
            out[(cells[0], T)] = c
    return out


def test_power_report_shows_every_icc_scenario_and_flags_the_pilot():
    cfg, rd = _fake_run()
    reports.make_all(rd, cfg)
    md = open(os.path.join(rd, "reports", "POWER_ANALYSIS.md"), encoding="utf-8").read()
    rows = list(csv.DictReader(open(os.path.join(rd, "csv", "power.csv"), encoding="utf-8")))
    rule = [r for r in rows if r["analysis"] == "rule_effect"]
    cells = _pivot_cells(md, "## Rule effect")
    for r in rule:                                         # every CSV row is in the table, same value
        key = (f"{float(r['icc']):.3f}", int(r["n_templates"]))
        assert cells[key] == f"{float(r['power']):.3f}", key
    assert "**pilot estimate**" in md
    assert "1 + (m − 1) · ICC" in md and "T · m / DE" in md
    assert "criterion 1 only" in md and "hypothetical" in md.lower()
    sde = [r for r in rows if r["analysis"] == "h4_smallest_detectable_auroc"]
    sc = _pivot_cells(md, "## H4 criterion 1")
    for r in sde:
        key = (f"{float(r['icc']):.3f}", int(r["n_templates"]))
        want = f"{float(r['value']):.2f}" if r["value"] else "not reached"
        assert sc[key] == want, key


def test_zero_power_scenarios_stay_visible():
    cfg, rd = _fake_run()
    p = os.path.join(rd, "csv", "power.csv")
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    saved = open(p, encoding="utf-8").read()
    target = [r for r in rows if r["analysis"] == "rule_effect"][0]
    target["power"] = "0"
    try:
        export.write_csv(p, rows)
        md = reports.power_report(reports.R(rd, cfg))
        key = (f"{float(target['icc']):.3f}", int(target["n_templates"]))
        assert _pivot_cells(md, "## Rule effect")[key] == "0.000"
    finally:
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(saved)


def test_run_summary_counts_registered_artifacts_on_first_and_repeated_generation():
    cfg = H.small_cfg(run_id="dev-counts", site_limit=24, primary_sites=12)
    rd = os.path.join(H.tmpdir("p33_cnt_"), cfg.run_id)
    pins = H.fake_pins(cfg)
    PL.run(cfg, rd, "arm_a", scorer_factory=lambda m: FakeScorer(m), pins=pins)
    PL.merge(cfg, rd, "arm_a", pins=pins)
    export.export_all(rd, cfg)
    n_csv, n_rep, n_plot = len(artifacts.CSV_NAMES), len(artifacts.REPORT_NAMES), \
        len(artifacts.PLOT_NAMES) * len(artifacts.PLOT_FORMATS)

    def summary():
        return open(os.path.join(rd, "reports", "RUN_SUMMARY.md"), encoding="utf-8").read()
    assert not os.path.exists(os.path.join(rd, "reports", "RUN_SUMMARY.md"))   # fresh directory
    reports.make_all(rd, cfg)
    s = summary()
    assert f"{n_csv} of {n_csv} registered" in s and f"{n_rep} of {n_rep} registered" in s
    assert f"0 of {n_plot} registered" in s and "INCOMPLETE" in s            # no figures were made
    for stray in ("reports/NOTES.md", "csv/extra.csv"):                       # never counted
        open(os.path.join(rd, stray), "w").write("not a pipeline artifact\n")
    reports.make_all(rd, cfg)
    s = summary()
    assert f"{n_csv} of {n_csv} registered" in s and f"{n_rep} of {n_rep} registered" in s


def test_full_export_counts_and_figure_series_match_the_tables():
    needs("matplotlib")
    from p33 import plots
    cfg, rd = _fake_run()
    for _ in range(2):                                    # first and repeated export
        plots.make_all(rd, cfg)
        reports.make_all(rd, cfg)
        s = open(os.path.join(rd, "reports", "RUN_SUMMARY.md"), encoding="utf-8").read()
        for d, (present, registered) in artifacts.counts(rd).items():
            assert present == registered, d
            assert f"{present} of {registered} registered" in s
    rows = list(csv.DictReader(open(os.path.join(rd, "csv", "power.csv"), encoding="utf-8")))
    ser = plots.power_series(rows)
    rule = [r for r in rows if r["analysis"] == "rule_effect"]
    plotted = {(ic, T): p for ic, pts in ser["rule"].items() for T, p in pts}
    assert plotted == {(float(r["icc"]), int(r["n_templates"])): float(r["power"]) for r in rule}
    pil = [r for r in rows if r["analysis"] == "h4_criterion1" and r["is_pilot_icc"] == "True"]
    drawn = {(T, a): p for T, pts in ser["h4_pilot"].items() for a, p in pts}
    assert drawn == {(int(r["n_templates"]), float(r["true_auroc"])): float(r["power"]) for r in pil}


def test_figure_footer_pairs_each_model_with_its_own_revision():
    """Two separately sorted lists paired models and revisions by position:
    on the development run, 3 of the 4 positional readings were wrong."""
    needs("matplotlib")
    from p33 import plots
    rows = [{"model": "Org/B-base|Org/A-inst", "model_revision": "aaaaaaaaaaaa|bbbbbbbbbbbb"},
            {"model": "Org/C", "model_revision": "cccccccccccc"}]
    line = plots.model_revisions(rows)
    assert line == "model@revision=A-inst@bbbbbbbbbb, B-base@aaaaaaaaaa, C@cccccccccc", line
    many = [{"model": f"Org/M{i}", "model_revision": f"{i:012d}"} for i in range(21)]
    assert plots.model_revisions(many).startswith("models=21 ")
    assert plots.model_revisions([{"model": "Org/X"}]) == "model@revision=X@n/a"


def test_reproduction_report_names_commands_that_exist():
    cfg, rd = _fake_run()
    md = reports.reproduction(reports.R(rd, cfg))
    assert " arm-a " not in md and "--experiment arm_a" in md and "--experiment primary" in md
    from p33 import _paths
    assert os.path.exists(os.path.join(_paths.SOL_ROOT, "env", "README.md"))
    json.dumps(md)   # plain text
