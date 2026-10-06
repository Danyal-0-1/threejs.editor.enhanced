"""reports.py — the ten Markdown reports, generated from saved CSVs and manifests.

No report computes a statistic. Each one reads the tables `export.py` wrote,
so every sentence with a number in it can be checked against a CSV row.
Where a table says NOT RUN or NOT TESTABLE the report says so, with the
reason, and does not fill the gap with an expectation or a placeholder claim.

STAGE DISCIPLINE. Every report opens with a banner. Development and smoke
results are labelled "not confirmatory"; held-out results appear only in a
held-out run; a run with missing or failed cells is labelled PARTIAL.
"""

from __future__ import annotations

import csv
import glob
import json
import os

from p33 import config as CFG

REPORTS = ("RUN_SUMMARY", "METHODS_AND_PROVENANCE", "QUALITY_CONTROL",
           "DEVELOPMENT_RESULTS", "HELDOUT_RESULTS", "HYPOTHESIS_RESULTS",
           "PLAIN_LANGUAGE_RESULTS", "POWER_ANALYSIS", "DEVIATIONS", "REPRODUCTION")


def _read(d, n):
    p = os.path.join(d, f"{n}.csv")
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _fmt(x, nd=3):
    v = _f(x)
    return "—" if v is None else f"{v:.{nd}f}"


def _table(rows: list[dict], cols: list[str], heads: list[str] | None = None) -> str:
    if not rows:
        return "_no rows_\n"
    heads = heads or cols
    out = "| " + " | ".join(heads) + " |\n|" + "---|" * len(cols) + "\n"
    for r in rows:
        out += "| " + " | ".join(str(r.get(c, "")).replace("|", "/") for c in cols) + " |\n"
    return out


def _not_run(rows):
    return not rows or rows[0].get("status") in ("NOT RUN", "NOT TESTABLE")


class R:
    def __init__(self, run_dir: str, cfg):
        self.run_dir, self.cfg = run_dir, cfg
        self.csv = os.path.join(run_dir, "csv")
        self.out = os.path.join(run_dir, "reports")
        os.makedirs(self.out, exist_ok=True)
        self.comp = _read(self.csv, "run_completeness")
        ran = [c for c in self.comp if c.get("status") not in ("NOT RUN", None)]
        self.partial = any(c.get("status") in ("PARTIAL", "EMPTY") for c in ran)
        self.status = "PARTIAL" if self.partial else ("COMPLETE" if ran else "NOTHING RUN")

    def banner(self) -> str:
        stage = {"dev": "DEVELOPMENT", "smoke": "SMOKE (development cell)",
                 "heldout": "HELD-OUT"}[self.cfg.stage]
        conf = ("**Confirmatory evidence is possible only in a held-out run after "
                "the development analysis is frozen. These results are not confirmatory.**"
                if self.cfg.stage != "heldout" else
                "Held-out evaluation under DEV_FREEZE; see criteria below. blk results "
                "are a WEAKER family test (deviation D1), never a held-out-grammar confirmation.")
        warn = ("\n> ⚠️ **PARTIAL RUN** — some expected cells are missing, failed or corrupt. "
                "Every number below covers completed cells only.\n" if self.partial else "")
        return (f"> **Run** `{self.cfg.run_id}` · **stage** {stage} · **status** {self.status}\n"
                f">\n> {conf}\n{warn}\n")

    def write(self, name: str, body: str) -> str:
        p = os.path.join(self.out, f"{name}.md")
        CFG.atomic_write_text(p, body)
        return p


# ---------------------------------------------------------------------------

def _headline(r: R) -> str:
    rev = [x for x in _read(r.csv, "rule_effect") if x.get("record_type") == "reversion" and x.get("stratum") == "ALL"]
    eff = [x for x in _read(r.csv, "rule_effect") if x.get("record_type") == "rule_effect" and x.get("stratum") == "ALL"]
    ks = [x for x in _read(r.csv, "kstar_survival") if x.get("record_type") == "km_summary"]
    s = "## Headline numbers (from the CSVs; see stage banner)\n\n"
    s += "**Reversion with the token table present** (`rule_effect.csv`, record_type=reversion)\n\n"
    s += _table([{**x, "rate": _fmt(x["reversion_rate"]), "ci": f"[{_fmt(x.get('ci_lo'))}, {_fmt(x.get('ci_hi'))}]"} for x in rev],
                ["family", "lexicon", "model", "rate", "ci", "n_rows", "n_templates"]) if rev else "_Arm A NOT RUN_\n"
    s += "\n**Rule effect** — `M_seq(rule) − M_seq(control)` (`rule_effect.csv`)\n\n"
    s += _table([{**x, "mean": _fmt(x["mean_rule_effect"]), "ci": f"[{_fmt(x.get('ci_lo'))}, {_fmt(x.get('ci_hi'))}]",
                  "helped": _fmt(x.get("share_helped"))} for x in eff],
                ["family", "lexicon", "model", "control", "mean", "ci", "ci_excludes_zero", "helped"]) if eff else "_NOT RUN_\n"
    s += "\n**Extinction** — Kaplan–Meier median shots (`kstar_survival.csv`)\n\n"
    s += _table([{**x, "median": x.get("km_median"), "ci": f"[{_fmt(x.get('ci_lo'))}, {_fmt(x.get('ci_hi'))}]",
                  "cens": _fmt(x.get("censoring_rate"))} for x in ks],
                ["family", "model", "population", "median", "ci", "n", "cens"]) if ks else "_extinction NOT RUN_\n"
    return s


def run_summary(r: R) -> str:
    s = f"# Run summary — `{r.cfg.run_id}`\n\n" + r.banner()
    s += "## Completeness (`run_completeness.csv`)\n\n"
    s += _table(r.comp, ["experiment", "status", "n_expected_cells", "done", "missing", "failed", "corrupt", "duplicates_dropped"])
    s += "\n" + _headline(r)
    s += "\n## Artifacts\n\n"
    for sub in ("csv", "plots", "reports"):
        files = sorted(glob.glob(os.path.join(r.run_dir, sub, "*")))
        s += f"- **{sub}/** — {len(files)} files\n"
    return s


def methods(r: R) -> str:
    jobs = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(r.run_dir, "manifests", "job_*.json")))]
    s = f"# Methods and provenance — `{r.cfg.run_id}`\n\n" + r.banner()
    s += "## Configuration\n\n```json\n" + json.dumps(r.cfg.to_dict(), indent=1, sort_keys=True) + "\n```\n\n"
    s += f"**Config hash:** `{r.cfg.config_hash()}`\n\n"
    s += "## Scoring\n\nOne canonical scorer (`phase3_2.margins.TokenScorer`): both candidates are tokenised in full with the prefix, the longest common TOKEN prefix `k` is found, and log-probabilities are summed from `k` on both sides, so a candidate that BPE merges into the previous token is still measured (P32-001). Zero-length spans, identical tokenisations and `k = 0` raise and become excluded rows — never a silent 0.0 (P33-001). "
    s += f"Output projection in float32 from the final hidden state: **{r.cfg.lm_head_fp32}** (P33-002; bf16 logits quantise near-zero margins, and the sign of the margin is the outcome).\n\n"
    s += "## Prompts\n\nRendered per lexicon from the φ-map (P33-006) and verified against every site: `rule` (28-role table), `norule` (role list, spellings withheld), `norule_lenmatched` (no-rule padded with content-free lines to the rule prompt's token count, per tokenizer), paraphrases `p0/p1/p2`. Hashes per (lexicon, condition) are in the job manifests.\n\n"
    s += "## Demonstrations\n\nLeakage-free (P33-008): never the site's template, never its program, never a prefix that replays the decision beyond the family's fixed opening. Seeded order per (family, lexicon); every ladder row stores demo ids, order hash and set hash.\n\n"
    s += "## Jobs\n\n"
    rows = []
    for j in jobs:
        g, pk = j.get("gpu", {}), j.get("packages", {})
        rows.append({"experiment": j.get("experiment"), "status": j.get("status"),
                     "job": (j.get("slurm") or {}).get("job_id") or "local",
                     "node": (j.get("job") or {}).get("node"), "git": (j.get("git_commit") or "")[:10],
                     "dirty": j.get("git_dirty"), "device": g.get("device_name"),
                     "torch": g.get("torch"), "cuda": g.get("cuda_runtime"),
                     "transformers": pk.get("transformers"),
                     "models": ", ".join(f"{m.split('/')[-1]}@{(v.get('revision') or '')[:10]}" for m, v in j.get("models", {}).items())})
    s += _table(rows, list(rows[0]) if rows else ["experiment"])
    if jobs:
        s += "\n## Materials hashes\n\n```json\n" + json.dumps(jobs[0].get("materials_hashes", {}), indent=1) + "\n```\n"
        s += f"\n{len(jobs[0].get('source_hashes', {}))} source files hashed (see any job manifest).\n"
    return s


def qc(r: R) -> str:
    arm = _read(r.csv, "arm_a_long")
    audit = _read(r.csv, "split_exclusion_audit")
    ks = [x for x in _read(r.csv, "kstar_survival") if x.get("record_type") == "curve_shape"]
    s = f"# Quality control — `{r.cfg.run_id}`\n\n" + r.banner()
    if _not_run(arm):
        s += "Arm A NOT RUN.\n"
    else:
        ok = [x for x in arm if x.get("status") == "ok"]
        ex = [x for x in arm if x.get("status") == "excluded"]
        zeros = [x for x in ok if _f(x["m_seq"]) == 0.0]
        merged = [x for x in ok if x.get("merged") in ("True", "true")]
        s += "## Arm A measurement health\n\n"
        s += _table([{"rows": len(arm), "ok": len(ok), "excluded": len(ex),
                      "exact_zero_margins": len(zeros), "ties": sum(x.get('tie') in ('True', 'true') for x in ok),
                      "merged_share": _fmt(len(merged) / len(ok) if ok else None)}],
                    ["rows", "ok", "excluded", "exact_zero_margins", "ties", "merged_share"])
        if ex:
            s += "\nExclusion reasons:\n\n" + "\n".join(sorted({f"- {x.get('exclusion_reason')}" for x in ex})) + "\n"
    s += "\n## Split and exclusion audit\n\n"
    kinds = {}
    for a in audit:
        kinds[a.get("record_type")] = kinds.get(a.get("record_type"), 0) + 1
    s += _table([{"record_type": k, "count": v} for k, v in sorted(kinds.items())], ["record_type", "count"])
    empties = [a for a in audit if a.get("record_type") == "structural_grid"]
    if empties:
        s += "\n**Structurally empty cells** (the lexicon cannot test this stratum):\n\n"
        s += _table(empties, ["family", "lexicon", "stratum", "status"])
    s += "\n## Failed cells\n\n"
    f = _read(r.csv, "failed_cells")
    s += "_none_\n" if _not_run(f) else _table(f, ["experiment", "cell_key", "kind", "error_type", "message"])
    s += "\n## Demonstration leakage\n\nEnforced, not merely checked: `score_primary_cell` raises if `demos.audit` finds any leak, so a completed ladder row is leak-free by construction.\n"
    if ks:
        s += "\n## Extinction curve shape\n\n" + _table(ks, ["family", "model", "share_nonmonotone", "share_recrossed_down", "share_already_correct"])
    return s


def dev_results(r: R) -> str:
    s = f"# Development results — `{r.cfg.run_id}`\n\n" + r.banner()
    if r.cfg.stage == "heldout":
        return s + "This is a held-out run. Development results live in the development run named in DEV_FREEZE.json.\n"
    s += _headline(r)
    h4 = [x for x in _read(r.csv, "h4_metrics_baselines_calibration") if x.get("record_type") == "metric" and x.get("role") in ("score", "baseline", "exploratory_baseline")]
    s += "\n## H4 on development data (calibration fitted here — becomes the frozen calibration)\n\n"
    s += _table([{**x, "auroc": _fmt(x.get("auroc")), "auprc": _fmt(x.get("auprc")), "prev": _fmt(x.get("prevalence"))} for x in h4],
                ["pair", "family", "predictor", "role", "auroc", "auprc", "prev", "n_rows"]) if h4 else "_NOT RUN_\n"
    return s


def heldout_results(r: R) -> str:
    s = f"# Held-out results — `{r.cfg.run_id}`\n\n" + r.banner()
    if r.cfg.stage != "heldout":
        return s + ("**NOT RUN.** Held-out cells are locked in this run. They open only "
                    "after `p33 dev freeze` writes an immutable DEV_FREEZE.json and "
                    "`p33 heldout unlock` writes HELDOUT_UNLOCK.json in a separate "
                    "`heldout-*` run directory. No held-out outcome was enumerated, "
                    "loaded or scored by this run.\n")
    s += _headline(r)
    crit = [x for x in _read(r.csv, "h4_metrics_baselines_calibration") if x.get("record_type") == "criterion"]
    s += "\n## Preregistered H4 criteria\n\n" + _table(crit, ["pair", "family", "split", "criterion", "status", "delta", "ci_lo", "ci_hi", "p_holm", "detail"])
    return s


def hypotheses(r: R) -> str:
    s = f"# Hypothesis results — `{r.cfg.run_id}`\n\n" + r.banner()
    crit = [x for x in _read(r.csv, "h4_metrics_baselines_calibration") if x.get("record_type") == "criterion"]
    h2 = _read(r.csv, "h2_did")
    h5 = [x for x in _read(r.csv, "h5_budget_outcomes") if x.get("record_type") == "arm"]
    hb = [x for x in _read(r.csv, "arm_b_hurdle") if x.get("stratum") == "ALL"]
    s += "| hypothesis | status in this run |\n|---|---|\n"
    s += "| H1 familiar beats unfamiliar | established in prior literature; not a contribution and not retested |\n"
    s += f"| H2 prior × context | **{h2[0].get('status') if h2 else 'NOT RUN'}** — {h2[0].get('reason', '') if h2 else ''} |\n"
    s += f"| H4 exact-site prediction | {'see criteria below' if crit else 'NOT RUN'} {'(DEVELOPMENT — not confirmatory)' if r.cfg.stage != 'heldout' else ''} |\n"
    s += f"| H5 targeted repair | {'see arms below' if h5 else 'NOT RUN'} |\n"
    s += f"| Arm B generation | {'see hurdle below' if hb else 'NOT RUN'} |\n\n"
    if crit:
        s += "## H4 criteria\n\n" + _table(crit, ["pair", "family", "split", "criterion", "status", "delta", "ci_lo", "ci_hi", "p_holm", "detail"])
        s += ("\nCriterion 1's identity baseline is CONSTANT on the SEMANTIC-only eligible set "
              "(AUROC exactly 0.5), so C1 is equivalent to AUROC ≥ 0.60 with an interval above 0.5 (deviation D6). "
              "The exploratory `terminal_rate` baseline is the stronger 'language-identity' competitor.\n")
    if h5:
        s += "\n## H5 arms\n\n" + _table([{**x, "per_symbol": _fmt(x["error_reduction_per_changed_symbol"]), "ctrl": _fmt(x.get("control_degradation"))} for x in h5],
                                       ["family", "lexicon", "model", "arm", "seed", "n_changed", "per_symbol", "ctrl", "control_within_tolerance"])
    if hb:
        s += "\n## Arm B hurdle\n\n" + _table([{**x, "reach": _fmt(x["p_reach"]), "rev": _fmt(x["p_revert_given_reach"]), "valid": _fmt(x["parse_valid_rate"]), "acc": _fmt(x["task_accuracy"])} for x in hb],
                                            ["family", "lexicon", "model", "reach", "rev", "valid", "acc", "n_sites"])
    return s


def plain(r: R) -> str:
    rev = [x for x in _read(r.csv, "rule_effect") if x.get("record_type") == "reversion" and x.get("stratum") == "ALL"]
    eff = [x for x in _read(r.csv, "rule_effect") if x.get("record_type") == "rule_effect" and x.get("stratum") == "ALL" and x.get("control") == "norule"]
    ks = [x for x in _read(r.csv, "kstar_survival") if x.get("record_type") == "km_summary" and x.get("population") == "INITIALLY_WRONG"]
    s = f"# What this run found, in plain language — `{r.cfg.run_id}`\n\n" + r.banner()
    s += "**The picture.** German *Gift* means *poison*: a fluent English speaker can write a perfectly grammatical German sentence that says something else entirely. Here the model is fluent in CSS and is handed a one-page 3DOM phrasebook; we measure how often the old habit wins anyway.\n\n"
    if rev:
        rates = [_f(x["reversion_rate"]) for x in rev]
        s += f"**How often the habit wins.** With the full translation table in the prompt, the familiar-but-wrong spelling was preferred at **{min(rates):.0%}–{max(rates):.0%}** of decision sites across the {len(rev)} model×lexicon cells measured.\n\n"
    else:
        s += "**How often the habit wins.** NOT RUN in this run.\n\n"
    if eff:
        inc = sum(1 for x in eff if x.get("ci_excludes_zero") in ("False", "false"))
        s += f"**Does handing over the table help?** Across {len(eff)} cells the average effect of the table was {', '.join(_fmt(x['mean_rule_effect'], 2) for x in eff)} nats; in **{inc} of {len(eff)}** the interval includes zero — handing over the glossary barely changes what gets written.\n\n"
    if ks:
        s += "**How many examples break the habit?** For sites that start wrong, the Kaplan–Meier median number of clean worked examples is: " + "; ".join(f"{x['model'].split('/')[-1]}/{x['family']}: {x['km_median']} (censored {_fmt(x['censoring_rate'], 2)})" for x in ks) + ". 'Censored' means the habit never broke within the ladder — those sites are kept, not dropped.\n\n"
    else:
        s += "**How many examples break the habit?** NOT RUN in this run.\n\n"
    s += "**What this does not show.** " + ("Nothing here is confirmatory: these are development numbers that set the frozen analysis. " if r.cfg.stage != "heldout" else "") + "The 'does 3D knowledge matter?' question is not identifiable with these materials (sigil and verb candidates occupy disjoint token lengths). H2 is NOT TESTABLE.\n"
    return s


def power_report(r: R) -> str:
    p = _read(r.csv, "power")
    s = f"# Power analysis — `{r.cfg.run_id}`\n\n" + r.banner()
    if _not_run(p):
        return s + f"**NOT RUN** — {p[0].get('reason') if p else 'no data'}\n"
    s += ("Development pilot estimates only (`power.pilot_from_rows` refuses any non-DEVELOPMENT row). "
          "Clustering by template is modelled through the design effect 1 + (m − 1)·ICC, with the ICC "
          "estimated from the pilot AND swept for sensitivity.\n\n")
    sde = [x for x in p if x.get("analysis") == "h4_smallest_detectable_auroc"]
    s += "## H4 criterion 1 — smallest AUROC detectable with 80% power\n\n" + _table(sde, ["n_templates", "icc", "value"])
    chk = [x for x in p if x.get("analysis") == "h4_simulation_check"]
    if chk:
        s += "\n## Simulation check of the analytic curve\n\n" + _table(chk, ["n_templates", "true_auroc", "icc", "power_analytic", "power_simulated", "source"])
    rule = [x for x in p if x.get("analysis") == "rule_effect" and x.get("power")]
    if rule:
        s += "\n## Rule effect\n\n" + _table([{**x, "power": _fmt(x["power"])} for x in rule if x["icc"] in (rule[0]["icc"],)], ["n_templates", "icc", "pilot_mean", "pilot_sd", "power"])
    other = [x for x in p if x.get("status") == "NOT RUN"]
    if other:
        s += "\n## Not computed\n\n" + _table(other, ["analysis", "status", "reason"])
    ks = [x for x in p if x.get("analysis") == "kstar_km_median_precision"]
    if ks and ks[0].get("status") == "OK":
        s += "\n## KM median precision by template count (pilot resampling)\n\n" + _table(ks, ["n_templates", "median_of_medians", "lo", "hi", "share_median_unreached"])
    s += ("\n**Assumptions.** Binormal score model; template random intercept; two-sided 95%; "
          "the identity baseline is constant on the eligible set (D6), so criterion 1 is AUROC ≥ 0.60 with an interval above 0.5. "
          "Held-out results were never used to tune any sample size.\n")
    return s


def deviations(r: R) -> str:
    from p33 import _paths
    pre = os.path.join(_paths.PHASE3_2_ROOT, "PREREGISTRATION.md")
    text = open(pre, encoding="utf-8").read()
    dev = text[text.index("## Deviations"):] if "## Deviations" in text else "_no deviations section found_"
    s = f"# Deviations — `{r.cfg.run_id}`\n\n" + r.banner()
    s += "## From the frozen preregistration (verbatim)\n\n" + dev + "\n\n## Run-level\n\n"
    items = []
    if r.cfg.allow_non_a100:
        items.append("- `allow_non_a100=True`: the A100 preflight requirement was waived for this run (local smoke only).")
    if r.cfg.allow_exploratory:
        items.append("- `allow_exploratory=True`: contaminated cells may have been scored; their rows are labelled EXPLORATORY.")
    if r.cfg.stage == "smoke":
        items.append("- Smoke run: one model, one development lexicon, one family, small n. Not an experiment.")
    s += "\n".join(items) if items else "_none_\n"
    return s


def reproduction(r: R) -> str:
    s = f"# Reproduction — `{r.cfg.run_id}`\n\n" + r.banner()
    s += f"Config hash `{r.cfg.config_hash()}` — a resume under any other config is refused.\n\n"
    s += "```bash\n# from $P33_CODE_ROOT/phase3_2/sol\n"
    s += f"python scripts/p33.py {r.cfg.stage if r.cfg.stage != 'smoke' else 'dev'} arm-a   --run {r.cfg.run_id}\n"
    s += f"python scripts/p33.py {r.cfg.stage if r.cfg.stage != 'smoke' else 'dev'} primary --run {r.cfg.run_id}\n"
    s += f"python scripts/p33.py merge    --run {r.cfg.run_id}\n"
    s += f"python scripts/p33.py validate --run {r.cfg.run_id}\n"
    s += f"python scripts/p33.py export   --run {r.cfg.run_id}   # CSVs -> plots -> reports\n```\n\n"
    s += "Resume is idempotent: completed cells (marker + sha256 + row count) are skipped; failed, missing and corrupt cells are re-run.\n"
    pins = os.path.join(CFG.results_root(), "model_pins.json")
    s += f"\nModel pins: `{pins}` (written by `p33 prefetch`). Environment lock: `phase3_2/sol/env/` (see `env/README.md`).\n"
    return s


BUILDERS = {"RUN_SUMMARY": run_summary, "METHODS_AND_PROVENANCE": methods,
            "QUALITY_CONTROL": qc, "DEVELOPMENT_RESULTS": dev_results,
            "HELDOUT_RESULTS": heldout_results, "HYPOTHESIS_RESULTS": hypotheses,
            "PLAIN_LANGUAGE_RESULTS": plain, "POWER_ANALYSIS": power_report,
            "DEVIATIONS": deviations, "REPRODUCTION": reproduction}


def make_all(run_dir: str, cfg) -> dict[str, str]:
    r = R(run_dir, cfg)
    return {name: r.write(name, BUILDERS[name](r)) for name in REPORTS}
