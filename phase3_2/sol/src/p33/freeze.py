"""freeze.py — build DEV_FREEZE.json from a COMPLETE development run.

What is frozen, and why each item must be:

  risk_score_formula   the H4 predictor's definition -- changing it after
                       seeing held-out data would be choosing the winner.
  calibration          Platt (logistic) parameters per base/instruct pair,
                       FITTED ON DEVELOPMENT DATA ONLY and applied unchanged
                       to held-out rows (Brier / ECE / slope are then honest).
  decision_threshold   Youden-optimal on development calibrated probabilities.
  prompts              hashes of every rendered prompt for every registered
                       lexicon (development AND held-out -- rendering a φ-map
                       reads materials, not outcomes) plus prompts.py itself.
  exclusions           the exclusion rules, verbatim.
  analysis_config      bootstrap unit / B / seed / alpha, Holm, the criteria.
  config_hashes        the development config and every material hash.
  source_hashes        every .py file whose change could change a number;
                       `splits.write_unlock` refuses if any differs later.
  model_pins           resolved revisions of every model that may be scored.

A freeze refuses an incomplete development run: a calibration fitted on a
partial run would be frozen without anyone noticing it was partial.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from phase3_2 import prompts

from p33 import config as CFG
from p33 import h4, provenance, splits
from p33 import _paths

EXCLUSION_RULES = [
    "collision != SEMANTIC",
    "not prefix-distinct WITHIN its (family, lexicon) cell (deviation D5)",
    "scoring refused: IdenticalCandidates / ZeroLengthSpan / NoContext (row kept, status=excluded)",
    "template fails to render or parse in its family",
]


def build_payload(run_dir: str, cfg) -> dict:
    status = json.load(open(os.path.join(run_dir, "merged", "arm_a.status.json")))
    if status["status"] != "COMPLETE":
        raise splits.FreezeError(f"development Arm A is {status['status']}; a freeze "
                                 f"needs a COMPLETE development run")
    if cfg.stage != "dev":
        raise splits.FreezeError("only a dev-stage run can be frozen")
    rows = [json.loads(l) for l in open(os.path.join(run_dir, "merged", "arm_a.jsonl")) if l.strip()]
    table = h4.build_table(rows)
    if not table:
        raise splits.FreezeError("no base/instruct pair in the development run -- "
                                 "H4 cannot be calibrated")
    cal, thr = {}, {}
    for pair in sorted({r["pair"] for r in table}):
        g = [r for r in table if r["pair"] == pair]
        a, b = h4.logistic_fit([r["risk"] for r in g], [r["label"] for r in g])
        cal[pair] = [a, b]
        thr[pair] = h4.youden_threshold([h4._sigmoid(a + b * r["risk"]) for r in g],
                                        [r["label"] for r in g])
    import phi as P
    lexicons = sorted(splits.DEV_LEXICONS | splits.HELDOUT_LEXICONS)
    rendered = {}
    for lx in lexicons:
        L = P.load_candidate(lx)
        for cond in ("rule", "norule") + prompts.PARAPHRASES:
            rendered[f"{lx}/{cond}"] = prompts.bundle(cond, L).sha
    pre = open(os.path.join(_paths.PHASE3_2_ROOT, "PREREGISTRATION.md"), "rb").read()
    pins_path = os.path.join(CFG.results_root(), "model_pins.json")
    pins = json.load(open(pins_path))["pins"] if os.path.exists(pins_path) else {}
    return {
        "dev_run_id": cfg.run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "risk_score_formula": {"id": h4.RISK_FORMULA,
                               "definition": "risk = -M_seq(base checkpoint, rule condition)",
                               "label": "1 if M_seq(instruct checkpoint, rule condition) < 0"},
        "calibration": {"method": "platt_logistic_fit_on_development", "params": cal},
        "decision_threshold": thr,
        "prompts": {"conditions": ["rule", "norule", "norule_lenmatched", *prompts.PARAPHRASES],
                    "prompts_py_sha256": CFG.sha256_file(prompts.__file__),
                    "rendered_sha256": rendered,
                    "note": "norule_lenmatched is tokenizer-specific; its construction "
                            "(prompts.norule_lenmatched) is frozen through prompts_py_sha256"},
        "exclusions": EXCLUSION_RULES,
        "analysis_config": {**cfg.analysis, "seeds": cfg.seeds,
                            "criteria": {"C1": "dAUROC vs identity >= 0.10, CI above 0",
                                         "C2": "dAUROC vs length >= 0.05, CI above 0",
                                         "C3": "AUROC >= 0.65 on a VALID held-out grammar "
                                               "(NOT TESTABLE: deviation D1)",
                                         "multiplicity": "Holm over C1, C2"},
                            "never_pool_families": True},
        "config_hashes": {"dev_config_hash": cfg.config_hash(),
                          "materials": CFG.materials_hash(lexicons)},
        "source_hashes": CFG.source_hashes(),
        "git": provenance.git_state(),      # commit BEFORE freezing, or `dirty` is true
        "model_pins": pins,
        "preregistration_sha256": CFG.sha256_json(pre.decode("utf-8")),
        "dev_arm_a_status": status,
    }


def freeze(run_dir: str, cfg) -> str:
    path = os.path.join(run_dir, "DEV_FREEZE.json")
    payload = build_payload(run_dir, cfg)
    splits.write_freeze(path, payload)
    return path
