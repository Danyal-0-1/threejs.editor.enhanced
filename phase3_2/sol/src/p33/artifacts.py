"""artifacts.py — the ONE registry of what an export produces.

`export.py` writes the CSVs, `plots.py` the figures, `reports.py` the reports;
each takes its names from here, and RUN_SUMMARY counts against this registry,
so a summary can neither count a file the pipeline did not produce nor miss
one that it did. (Before 2026-10-07 RUN_SUMMARY globbed `reports/` while it
was itself the first report being written: 0 files on a fresh export, and
whatever happened to be lying there on a repeated one.)

No matplotlib here, so counting needs only the standard library.
"""

from __future__ import annotations

import os

CSV_NAMES = (
    "site_inventory", "split_exclusion_audit", "run_completeness", "failed_cells",
    "job_provenance", "fertility", "arm_a_long", "rule_effect", "paraphrase",
    "extinction_rung_long", "kstar_survival", "h4_predictions",
    "h4_metrics_baselines_calibration", "arm_b_generations", "arm_b_hurdle",
    "h5_budget_outcomes", "h5_ir_proof", "h2_did", "power")

PLOT_NAMES = ("margin_reversion_distributions", "rule_effect_forest",
              "family_mapping_model_stratum", "fertility_tokenization",
              "extinction_trajectories_km", "paraphrase_sensitivity",
              "model_size_tokenizer", "h2_three_scale", "h4_roc_pr_calibration",
              "h5_benefit_per_symbol", "armb_hurdle_outcomes", "power_curves")
PLOT_FORMATS = ("png", "svg")

REPORT_NAMES = ("RUN_SUMMARY", "METHODS_AND_PROVENANCE", "QUALITY_CONTROL",
                "DEVELOPMENT_RESULTS", "HELDOUT_RESULTS", "HYPOTHESIS_RESULTS",
                "PLAIN_LANGUAGE_RESULTS", "POWER_ANALYSIS", "DEVIATIONS", "REPRODUCTION")


def expected(run_dir: str) -> dict[str, list[str]]:
    """Every registered artifact path, by directory."""
    return {
        "csv": [os.path.join(run_dir, "csv", f"{n}.csv") for n in CSV_NAMES],
        "plots": [os.path.join(run_dir, "plots", f"{n}.{ext}")
                  for n in PLOT_NAMES for ext in PLOT_FORMATS],
        "reports": [os.path.join(run_dir, "reports", f"{n}.md") for n in REPORT_NAMES],
    }


def counts(run_dir: str) -> dict[str, tuple[int, int]]:
    """{dir: (registered files present, registered files)}. Unregistered files
    in those directories (copies, notes, stale names) are never counted."""
    return {d: (sum(os.path.isfile(p) for p in paths), len(paths))
            for d, paths in expected(run_dir).items()}
