"""Fake-model end to end: dev run -> analysis -> freeze -> unlock -> held-out.

No GPU, no weights. Plot and report generation need matplotlib and are
BLOCKED (not passed) where it is absent.
"""

from __future__ import annotations

import csv
import glob
import json
import os

import _helpers as H
from run_tests import needs

from p33 import export, h5, pipeline as PL, splits
from p33 import armb  # noqa: F401  (registers the experiment)
from p33.fakes import FakeScorer

_STATE: dict = {}


def _dev_run():
    if "dev" in _STATE:
        return _STATE["dev"]
    cfg = H.small_cfg(run_id="dev-e2e", lexicons=("d50s1", "d25s1"), site_limit=40,
                      primary_sites=16)
    cfg.armb["template_limit"] = 4
    rd = os.path.join(H.tmpdir(), cfg.run_id)
    pins = H.fake_pins(cfg)
    st = {}
    for exp in ("arm_a", "primary", "armb"):
        st[exp] = PL.run(cfg, rd, exp, scorer_factory=lambda m: FakeScorer(m), pins=pins)
        PL.merge(cfg, rd, exp, pins=pins)
    h5.prepare(cfg, rd)
    st["h5"] = PL.run(cfg, rd, "h5", scorer_factory=lambda m: FakeScorer(m), pins=pins)
    PL.merge(cfg, rd, "h5", pins=pins)
    _STATE["dev"] = (cfg, rd, pins, st)
    return _STATE["dev"]


def test_every_dev_experiment_completes():
    cfg, rd, pins, st = _dev_run()
    assert st == {"arm_a": "COMPLETE", "primary": "COMPLETE", "armb": "COMPLETE",
                  "h5": "COMPLETE"}, st


def test_all_nineteen_csvs_exist_and_say_not_run_where_empty():
    cfg, rd, pins, _ = _dev_run()
    paths = export.export_all(rd, cfg)
    assert set(paths) == set(export.CSV_NAMES) and len(paths) == 19
    for name in export.CSV_NAMES:
        rows = list(csv.DictReader(open(paths[name])))
        assert rows, name
    h2 = list(csv.DictReader(open(paths["h2_did"])))
    assert h2[0]["status"] == "NOT TESTABLE"


def test_aggregates_carry_the_required_metadata():
    cfg, rd, pins, _ = _dev_run()
    paths = export.export_all(rd, cfg)
    rev = [r for r in csv.DictReader(open(paths["rule_effect"])) if r["record_type"] == "reversion"]
    for r in rev:
        for k in ("stage", "split", "family", "model", "model_revision", "tokenizer_id",
                  "n_rows", "n_templates", "n_mappings", "prevalence",
                  "ci_unit", "ci_reps", "ci_seed"):
            assert r.get(k) not in (None, ""), k
    km = [r for r in csv.DictReader(open(paths["kstar_survival"])) if r["record_type"] == "km_summary"]
    assert km and all(r["censoring_rate"] != "" for r in km)


def test_kstar_rows_follow_the_corrected_definition():
    cfg, rd, pins, _ = _dev_run()
    paths = export.export_all(rd, cfg)
    for r in csv.DictReader(open(paths["kstar_survival"])):
        if r.get("record_type") != "site" or r.get("status") != "ok":
            continue
        if r["already_correct"] == "True":
            assert float(r["k_star"]) == 0.0 and r["censored"] == "False"
        if r["censored"] == "True":
            assert r["k_star"] == ""


def test_no_demonstration_leaks_in_any_ladder_row():
    cfg, rd, pins, _ = _dev_run()
    rows = [json.loads(l) for l in open(os.path.join(rd, "merged", "primary.jsonl"))]
    for r in rows:
        if r.get("kind") == "ladder":
            assert r["template"] not in r["demo_ids"]
            assert len(r["demo_ids"]) == r["rung"]


def test_h5_ir_proofs_all_pass():
    cfg, rd, pins, _ = _dev_run()
    arms = json.load(open(os.path.join(rd, "manifests", "h5_arms.json")))
    assert arms["proofs"] and all(p["passed"] and p["n_mismatch"] == 0
                                  for p in arms["proofs"].values())


def test_plots_and_reports_are_generated_from_saved_tables():
    needs("matplotlib")
    from p33 import plots, reports
    cfg, rd, pins, _ = _dev_run()
    export.export_all(rd, cfg)
    pl = plots.make_all(rd, cfg)
    assert len(pl) == 12 and all(len(v) == 2 for v in pl.values())
    rp = reports.make_all(rd, cfg)
    assert len(rp) == 10
    held = open(rp["HELDOUT_RESULTS"]).read()
    assert "NOT RUN" in held and "locked" in held
    assert "not confirmatory" in open(rp["RUN_SUMMARY"]).read()
    assert "D1" in open(rp["DEVIATIONS"]).read()


def test_freeze_unlock_and_heldout_flow():
    from p33 import freeze
    cfg, rd, pins, _ = _dev_run()
    fz = freeze.freeze(rd, cfg)
    payload = splits.load_freeze(fz)
    assert payload["risk_score_formula"]["id"] == "neg_mseq_base_rule"
    assert payload["calibration"]["params"]

    hcfg = H.small_cfg(run_id="heldout-e2e", lexicons=("d75s1a",), site_limit=20,
                       primary_sites=8, stage="heldout")
    hcfg.freeze_path = fz
    hrd = os.path.join(os.path.dirname(rd), hcfg.run_id)
    hp = H.fake_pins(hcfg)
    try:                                                     # locked
        PL.run(hcfg, hrd, "arm_a", scorer_factory=lambda m: FakeScorer(m), pins=hp)
    except splits.SplitViolation as exc:
        assert "locked" in str(exc)
    else:
        raise AssertionError("held-out cells were scored before unlock")
    assert not glob.glob(os.path.join(hrd, "raw", "shards", "arm_a", "*.jsonl"))

    splits.write_unlock(hrd, fz, splits.UNLOCK_PHRASE)
    st = PL.run(hcfg, hrd, "arm_a", scorer_factory=lambda m: FakeScorer(m), pins=hp)
    assert st == "COMPLETE"
    res = PL.merge(hcfg, hrd, "arm_a", pins=hp)
    assert {r["split"] for r in res.rows} == {"HELDOUT"}
    paths = export.export_all(hrd, hcfg)
    crit = [r for r in csv.DictReader(open(paths["h4_metrics_baselines_calibration"]))
            if r.get("record_type") == "criterion"]
    assert crit and all(r["confirmatory"] == "True" for r in crit)
    assert any(r["criterion"] == "C3_auroc_heldout_grammar" and r["status"] == "NOT TESTABLE"
               for r in crit)
    preds = list(csv.DictReader(open(paths["h4_predictions"])))
    assert preds and all(r["calibration_source"] == "DEV_FREEZE" for r in preds)
