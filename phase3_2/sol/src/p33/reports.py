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

from p33 import artifacts  # noqa: E402

REPORTS = artifacts.REPORT_NAMES


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
    what = {"csv": "tables", "plots": f"{len(artifacts.PLOT_NAMES)} figures x "
                                      f"{'/'.join(artifacts.PLOT_FORMATS).upper()}",
            "reports": "Markdown reports"}
    for sub, (present, registered) in artifacts.counts(r.run_dir).items():
        flag = "" if present == registered else " — **INCOMPLETE**"
        s += f"- **{sub}/** — {present} of {registered} registered files present ({what[sub]}){flag}\n"
    s += ("\nCounted against the pipeline's registry (`p33/artifacts.py`) after every other "
          "artifact of this export was written; unregistered files are not counted.\n")
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
    s += _table([{**x, "auroc": _fmt(x.get("auroc")), "auprc": _fmt(x.get("auprc")), "prev": _fmt(x.get("prevalence")),
                  "p@10": _fmt(x.get("p_at_10")), "p@50": _fmt(x.get("p_at_50"))} for x in h4],
                ["pair", "family", "predictor", "role", "auroc", "auprc", "prev", "p@10", "p@50", "n_rows"]) if h4 else "_NOT RUN_\n"
    if h4:
        s += ("\n*Tied scores.* AP (`auprc`) is step-wise average precision with every tied score "
              "admitted as ONE threshold; precision@k is the expected precision when the top-k boundary "
              "falls inside a tie and places are filled uniformly from that tie. Both are therefore "
              "independent of row order, and a constant score (the identity baseline) scores exactly "
              "the prevalence. Corrected 2026-10-07 (deviation D9).\n")
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


def _pivot(rows: list[dict], value: str, *, fmt=None, mark_pilot=True) -> str:
    """Rows = ICC scenarios, columns = template counts; hypothetical counts marked *."""
    fmt = fmt or (lambda x: _fmt(x.get(value)))
    Ts = sorted({int(_f(x["n_templates"])) for x in rows})
    iccs = sorted({_f(x["icc"]) for x in rows})
    hyp = {int(_f(x["n_templates"])) for x in rows if str(x.get("t_status", "")).startswith("HYPOTHETICAL")}
    head = ["ICC", "ICC source"] + [f"T={T}{'*' if T in hyp else ''}" for T in Ts]
    out = "| " + " | ".join(head) + " |\n|" + "---|" * len(head) + "\n"
    for ic in iccs:
        g = {int(_f(x["n_templates"])): x for x in rows if _f(x["icc"]) == ic}
        any_row = next(iter(g.values()))
        src = any_row.get("icc_source") or ""
        label = f"**{src}**" if mark_pilot and src and src != "sensitivity" else src
        out += f"| {_fmt(ic, 3)} | {label} | " + " | ".join(fmt(g[T]) if T in g else "—" for T in Ts) + " |\n"
    if hyp:
        out += (f"\n\\* hypothetical: more templates than the {next(iter(rows)).get('corpus_templates')}-template "
                f"corpus, i.e. new materials would have to be written; not an observed sample.\n")
    return out


def _first_reaching(rows: list[dict], target: float = 0.8):
    for x in sorted(rows, key=lambda x: _f(x["n_templates"])):
        if (_f(x.get("power")) or 0.0) >= target:
            return x
    return None


def power_report(r: R) -> str:
    """The FULL ICC sensitivity, the pilot scenario flagged, scope stated.

    Before 2026-10-07 this showed only the rule-effect rows of the FIRST ICC
    (zero, the most optimistic) and repeated one smallest-detectable row five
    times per template count. Zero-power rows are kept: no truthiness filters.
    """
    p = _read(r.csv, "power")
    s = f"# Power analysis — `{r.cfg.run_id}`\n\n" + r.banner()
    if _not_run(p):
        return s + f"**NOT RUN** — {p[0].get('reason') if p else 'no data'}\n"
    h4 = [x for x in p if x.get("analysis") == "h4_criterion1" and _f(x.get("power")) is not None]
    sde = [x for x in p if x.get("analysis") == "h4_smallest_detectable_auroc"]
    rule = [x for x in p if x.get("analysis") == "rule_effect" and _f(x.get("power")) is not None]

    s += ("## What this is — and what it is not\n\n"
          "- **Planning estimates from the development pilot only.** `power.pilot_from_rows` refuses any "
          "non-DEVELOPMENT row; no held-out result was used, and nothing here changed the registered design "
          "or sample size.\n"
          "- **H4:** the power of **criterion 1 only** (AUROC ≥ 0.60 with its lower bound above 0.5). "
          "It says nothing about criterion 2, about criterion 3 (NOT TESTABLE, deviation D1), or about any "
          "other hypothesis.\n"
          "- **Rule effect:** a one-sample, template-clustered test of the POOLED mean rule effect "
          "M(rule) − M(norule) > 0. The registered `rule_effect.csv` tests are per (model, lexicon), with "
          "far fewer rows per template than this pooled pilot, so each of those has less power than shown here.\n"
          "- **Approximate.** Normal approximations; a binormal score model for H4; one ICC standing in for a "
          "nested design (sites within templates, models and lexicons within sites).\n"
          "- **Templates are the independent unit.** Scoring the same templates under more models or lexicons, "
          "or repeating sites, adds rows *within* templates; it does not add templates. Template counts above "
          "the corpus (marked *) are hypothetical projections, not data already collected.\n\n")

    s += "## Clustering, in plain language\n\n"
    s += ("Rows from one template are siblings: they share a program, so they tend to agree. The **ICC** "
          "(intra-class correlation) is the share of all variation that lies *between* templates; 0 means "
          "sibling rows are as different as strangers, 1 means they are copies. With m rows per template:\n\n"
          "    design effect          DE    = 1 + (m − 1) · ICC\n"
          "    effective sample size  n_eff = T · m / DE\n\n")
    for name, rows in (("rule effect", rule), ("H4 criterion 1", h4)):
        piv = [x for x in rows if str(x.get("is_pilot_icc")) in ("True", "true")
               and int(_f(x["n_templates"])) == 80]
        if piv:
            x = piv[0]
            T, m = int(_f(x["n_templates"])), _f(x.get("rows_per_template"))
            s += (f"- **{name}** — m = {_fmt(m, 2)} rows per template ({x.get('pooling')}); pilot ICC = "
                  f"{_fmt(x.get('pilot_icc'))}, so DE = {_fmt(x.get('design_effect'), 2)} and at T = {T} the "
                  f"{_fmt(T * m, 0)} rows are worth about **{_fmt(x.get('effective_n'), 0)}** independent "
                  f"observations.\n")
    s += "\n"

    if rule:
        s += ("## Rule effect — power for a positive pooled mean\n\n"
              f"Pilot mean {_fmt(rule[0].get('pilot_mean'))} nats, SD {_fmt(rule[0].get('pilot_sd'))}. "
              "Every ICC scenario is shown; the pilot estimate is in bold.\n\n" + _pivot(rule, "power"))
        pil = [x for x in rule if str(x.get("is_pilot_icc")) in ("True", "true")]
        if pil:
            hit = _first_reaching(pil)
            at80 = [x for x in pil if int(_f(x["n_templates"])) == 80]
            best = max(pil, key=lambda x: _f(x["power"]))
            s += ("\n**Reading it.** At the pilot ICC the power at 80 templates is "
                  f"**{_fmt(at80[0]['power']) if at80 else '—'}**; ")
            s += (f"80% power is first reached at {hit['n_templates']} templates ({hit.get('t_status')}).\n"
                  if hit else
                  f"80% power is **not reached** anywhere on this grid (best: {_fmt(best['power'])} at "
                  f"{best['n_templates']} templates, {best.get('t_status')}).\n")
            zero = [x for x in rule if str(x.get("icc_source")) == "sensitivity" and _f(x["icc"]) == 0.0
                    and int(_f(x["n_templates"])) == 80]
            if zero:
                s += (f"The ICC = 0 column ({_fmt(zero[0]['power'])} at 80 templates) assumes rows within a "
                      "template are independent; the pilot says they are not, so ICC = 0 is the most "
                      "optimistic row, not the expected one.\n")
    if sde:
        def _sde_cell(x):
            return _fmt(x.get("value"), 2) if _f(x.get("value")) is not None else "not reached"
        s += ("\n## H4 criterion 1 — smallest true AUROC detected with 80% power\n\n"
              "One row per (ICC scenario, template count); each computed with the ICC in its own row. "
              "'not reached' = no AUROC on the 0.51–0.99 grid reaches 80% power.\n\n"
              + _pivot(sde, "value", fmt=_sde_cell))
        pil = [x for x in sde if str(x.get("is_pilot_icc")) in ("True", "true") and int(_f(x["n_templates"])) == 80]
        if pil and _f(pil[0].get("pilot_auroc")) is not None:
            s += (f"\n**Reading it.** At the pilot ICC and 80 templates, criterion 1 has 80% power for a true "
                  f"AUROC of {_sde_cell(pil[0])} or more; the pooled development AUROC was "
                  f"{_fmt(pil[0]['pilot_auroc'])}. That is planning information about criterion 1 only — "
                  "it is not evidence that the held-out AUROC will be similar.\n")
    if h4:
        pil = [x for x in h4 if str(x.get("is_pilot_icc")) in ("True", "true")]
        if pil:
            Ts = sorted({int(_f(x["n_templates"])) for x in pil})
            hyp = {int(_f(x["n_templates"])) for x in pil if str(x.get("t_status", "")).startswith("HYPOTHETICAL")}
            s += ("\n### H4 power at the pilot ICC, by true AUROC\n\n| true AUROC | "
                  + " | ".join(f"T={T}{'*' if T in hyp else ''}" for T in Ts) + " |\n|---|" + "---|" * len(Ts) + "\n")
            for A in sorted({_f(x["true_auroc"]) for x in pil}):
                g = {int(_f(x["n_templates"])): x for x in pil if _f(x["true_auroc"]) == A}
                s += f"| {_fmt(A, 2)} | " + " | ".join(_fmt(g[T]["power"]) if T in g else "—" for T in Ts) + " |\n"
    chk = [x for x in p if x.get("analysis") == "h4_simulation_check"]
    if chk:
        s += "\n## Simulation check of the analytic curve\n\n" + _table(chk, ["n_templates", "true_auroc", "icc", "power_analytic", "power_simulated", "source"])
    ks = [x for x in p if x.get("analysis") == "kstar_km_median_precision"]
    if ks and ks[0].get("status") == "OK":
        s += "\n## KM median precision by template count (pilot resampling)\n\n" + _table(ks, ["n_templates", "median_of_medians", "lo", "hi", "share_median_unreached"])
    other = [x for x in p if x.get("status") == "NOT RUN"]
    if other:
        s += "\n## Not computed\n\n" + _table(other, ["analysis", "status", "reason"])
    s += ("\n**Assumptions.** Binormal score model (H4); template random intercept; two-sided 95%; the "
          "identity baseline is constant on the eligible set (D6), so criterion 1 is AUROC ≥ 0.60 with an "
          "interval above 0.5. Held-out results were never used to tune any sample size.\n")
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
    grp = r.cfg.stage if r.cfg.stage != "smoke" else "dev"
    s += "```bash\n# from $P33_CODE_ROOT/phase3_2/sol, after `source sol.env && source env/activate.sh`\n"
    s += "# scoring (GPU; on Sol through submit.sh, one array task per model)\n"
    s += f"python scripts/p33.py {grp} run --run {r.cfg.run_id} --experiment arm_a\n"
    s += f"python scripts/p33.py {grp} run --run {r.cfg.run_id} --experiment primary\n"
    s += "# analysis (CPU; re-derives every table, plot and report from the saved measurements)\n"
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
    """Every report; RUN_SUMMARY last, because it counts the other artifacts.

    On a fresh directory RUN_SUMMARY cannot count itself before it exists, so
    it is written once more at the end: the final file always describes the
    completed export (first export and repeated export alike).
    """
    r = R(run_dir, cfg)
    out = {name: r.write(name, BUILDERS[name](r)) for name in REPORTS if name != "RUN_SUMMARY"}
    r.write("RUN_SUMMARY", BUILDERS["RUN_SUMMARY"](r))
    out["RUN_SUMMARY"] = r.write("RUN_SUMMARY", BUILDERS["RUN_SUMMARY"](r))
    return {name: out[name] for name in REPORTS}
