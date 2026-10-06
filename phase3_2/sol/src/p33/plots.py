"""plots.py — every figure, generated ONLY from the saved CSVs.

A plot never touches a model or a merged shard: if a number is on a figure it
is in a CSV, so any figure can be regenerated -- and audited -- from the table
beside it. Each figure is saved as PNG and SVG.

Every figure carries a footer stamp: stage / split label, grammar family,
model and resolved revision, tokenizer, rows / templates / mappings,
prevalence, failed and missing cells, the CI unit / repetitions / seed, and
censoring where it applies. A figure whose table says NOT RUN or NOT TESTABLE
is still produced, showing exactly that and why -- an absent figure is easy to
overlook, an explicit one is not.
"""

from __future__ import annotations

import csv
import json
import os
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PLOTS = ("margin_reversion_distributions", "rule_effect_forest",
         "family_mapping_model_stratum", "fertility_tokenization",
         "extinction_trajectories_km", "paraphrase_sensitivity",
         "model_size_tokenizer", "h2_three_scale", "h4_roc_pr_calibration",
         "h5_benefit_per_symbol", "armb_hurdle_outcomes", "power_curves")


def _read(csv_dir: str, name: str) -> list[dict]:
    p = os.path.join(csv_dir, f"{name}.csv")
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _not_run(rows):
    return not rows or rows[0].get("status") in ("NOT RUN", "NOT TESTABLE")


class Ctx:
    def __init__(self, run_dir: str, cfg):
        self.run_dir, self.cfg = run_dir, cfg
        self.csv = os.path.join(run_dir, "csv")
        self.out = os.path.join(run_dir, "plots")
        os.makedirs(self.out, exist_ok=True)
        comp = _read(self.csv, "run_completeness")
        self.failed = sum(int(_f(r.get("failed")) or 0) for r in comp)
        self.missing = sum(int(_f(r.get("missing")) or 0) for r in comp)
        self.excluded = sum(1 for r in _read(self.csv, "split_exclusion_audit")
                            if r.get("record_type") == "excluded_row")

    def stamp(self, fig, rows: list[dict], *, extra: str = "", ci=True):
        fams = sorted({r.get("family") for r in rows if r.get("family")})
        models = sorted({r.get("model") for r in rows if r.get("model")})
        revs = sorted({(r.get("model_revision") or "")[:10] for r in rows if r.get("model_revision")})
        toks = sorted({(r.get("tokenizer_id") or "")[:10] for r in rows if r.get("tokenizer_id")})
        splits = sorted({r.get("split") for r in rows if r.get("split")})
        temps = {r.get("template") for r in rows if r.get("template")}
        maps = {r.get("lexicon") for r in rows if r.get("lexicon")}
        a = self.cfg.analysis
        lines = [
            f"stage={self.cfg.stage}  split={'|'.join(splits) or 'n/a'}  family={'|'.join(fams) or 'n/a'}",
            f"model={'|'.join(m.split('/')[-1] for m in models) or 'n/a'}  rev={'|'.join(revs) or 'n/a'}  tokenizer={'|'.join(toks) or 'n/a'}",
            f"rows={len(rows)}  templates={len(temps)}  mappings={len(maps)}  excluded rows={self.excluded}  failed cells={self.failed}  missing cells={self.missing}",
        ]
        if ci:
            lines.append(f"CI: {a['unit']}-cluster bootstrap, B={a['B']}, seed={self.cfg.seeds['bootstrap']}, 95% percentile")
        if extra:
            lines.append(extra)
        fig.text(0.01, 0.005, "\n".join(lines), fontsize=6.5, family="monospace",
                 va="bottom", ha="left", color="#333")

    def save(self, fig, name: str) -> list[str]:
        fig.subplots_adjust(bottom=0.27, wspace=0.32)
        paths = []
        for ext in ("png", "svg"):
            p = os.path.join(self.out, f"{name}.{ext}")
            fig.savefig(p, dpi=130)
            paths.append(p)
        plt.close(fig)
        return paths

    def placeholder(self, name: str, title: str, reason: str) -> list[str]:
        fig = plt.figure(figsize=(8, 4))
        fig.suptitle(title)
        fig.text(0.5, 0.55, reason, ha="center", va="center", fontsize=12, wrap=True)
        self.stamp(fig, [], ci=False)
        return self.save(fig, name)


# ---------------------------------------------------------------------------
# figures
# ---------------------------------------------------------------------------

def margin_distributions(c: Ctx):
    rows = _read(c.csv, "arm_a_long")
    name = "margin_reversion_distributions"
    if _not_run(rows):
        return c.placeholder(name, "Arm A margins", "NOT RUN")
    ok = [r for r in rows if r.get("status") == "ok"]
    groups = sorted({(r["model"], r["family"]) for r in ok})
    fig, axes = plt.subplots(1, max(len(groups), 1), figsize=(5 * max(len(groups), 1), 4), squeeze=False)
    for ax, (m, fam) in zip(axes[0], groups):
        for cond in sorted({r["condition"] for r in ok}):
            xs = [_f(r["m_seq"]) for r in ok if (r["model"], r["family"], r["condition"]) == (m, fam, cond)]
            ax.hist(xs, bins=30, alpha=0.5, label=f"{cond} (rev={sum(x < 0 for x in xs)/len(xs):.2f})")
        ax.axvline(0, color="k", lw=0.8)
        ax.set_title(f"{m.split('/')[-1]} / {fam}", fontsize=9)
        ax.set_xlabel("M_seq = logP(correct) - logP(competitor)   (<0 = reversion)")
        ax.legend(fontsize=7)
    fig.suptitle("Arm A: margin distributions by condition")
    c.stamp(fig, ok, ci=False)
    return c.save(fig, name)


def rule_effect_forest(c: Ctx):
    rows = [r for r in _read(c.csv, "rule_effect") if r.get("record_type") == "rule_effect"]
    name = "rule_effect_forest"
    if not rows:
        return c.placeholder(name, "Arm A rule effect", "NOT RUN")
    rows = sorted(rows, key=lambda r: (r["family"], r["model"], r["lexicon"], r["control"], r["stratum"]))
    fig, ax = plt.subplots(figsize=(9, 0.28 * len(rows) + 2))
    for i, r in enumerate(rows):
        pt, lo, hi = _f(r["mean_rule_effect"]), _f(r.get("ci_lo")), _f(r.get("ci_hi"))
        ax.plot([pt], [i], "o", color="C0" if r["control"] == "norule" else "C1", ms=4)
        if lo is not None and hi is not None:
            ax.plot([lo, hi], [i, i], "-", color="C0" if r["control"] == "norule" else "C1", lw=1)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{r['family']}/{r['lexicon']}/{r['model'].split('/')[-1]}/{r['stratum']} vs {r['control']}"
                        for r in rows], fontsize=6)
    ax.set_xlabel("rule effect = M_seq(rule) - M_seq(control)   (>0: the table helped)")
    fig.suptitle("Arm A rule effect, template-cluster 95% CI (blue: no-rule; orange: length-matched no-rule)")
    c.stamp(fig, rows)
    return c.save(fig, name)


def comparisons(c: Ctx):
    rows = [r for r in _read(c.csv, "rule_effect") if r.get("record_type") == "reversion"]
    name = "family_mapping_model_stratum"
    if not rows:
        return c.placeholder(name, "Reversion by cell", "NOT RUN")
    rows = sorted(rows, key=lambda r: (r["family"], r["lexicon"], r["model"], r["stratum"]))
    fig, ax = plt.subplots(figsize=(9, 0.28 * len(rows) + 2))
    for i, r in enumerate(rows):
        pt, lo, hi = _f(r["reversion_rate"]), _f(r.get("ci_lo")), _f(r.get("ci_hi"))
        ax.plot([pt], [i], "s", color="C2", ms=4)
        if lo is not None:
            ax.plot([lo, hi], [i, i], "-", color="C2", lw=1)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{r['family']}/{r['lexicon']}/{r['model'].split('/')[-1]}/{r['stratum']}" for r in rows], fontsize=6)
    ax.set_xlim(0, 1)
    ax.set_xlabel("reversion rate with the token table present, P(M_seq < 0)")
    fig.suptitle("Family x mapping x model x stratum (never pooled across families)")
    c.stamp(fig, rows)
    return c.save(fig, name)


def fertility_plot(c: Ctx):
    rows = _read(c.csv, "fertility")
    arm = [r for r in _read(c.csv, "arm_a_long") if r.get("status") == "ok"]
    name = "fertility_tokenization"
    if _not_run(rows) and not arm:
        return c.placeholder(name, "Fertility / tokenisation", "NOT RUN")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    if not _not_run(rows):
        labels = [f"{r['tokenizer_id'][:6]}/{r['family']}/{r['lexicon']}" for r in rows]
        axes[0].barh(range(len(rows)), [_f(r["rel_fertility_vs_identity"]) for r in rows], color="C4")
        axes[0].axvline(1.0, color="k", lw=0.8)
        axes[0].set_yticks(range(len(rows)))
        axes[0].set_yticklabels(labels, fontsize=6)
        axes[0].set_xlabel("relative fertility (tok/char vs identity)")
    else:
        axes[0].text(0.5, 0.5, "fertility NOT RUN", ha="center")
    if arm:
        grp = defaultdict(list)
        for r in arm:
            grp[(r["model"].split("/")[-1], r["family"], r["stratum"])].append(r["merged"] in ("True", "true", "1"))
        keys = sorted(grp)
        axes[1].barh(range(len(keys)), [sum(v) / len(v) for v in (grp[k] for k in keys)], color="C5")
        axes[1].set_yticks(range(len(keys)))
        axes[1].set_yticklabels([f"{a}/{b}/{s}" for a, b, s in keys], fontsize=6)
        axes[1].set_xlabel("share of sites where the candidate merges into the prefix token")
    fig.suptitle("Tokenisation diagnostics (per tokenizer; P32-001 merge rate)")
    c.stamp(fig, arm or rows, ci=False)
    return c.save(fig, name)


def extinction(c: Ctx):
    lad = [r for r in _read(c.csv, "extinction_rung_long") if r.get("status") == "ok"]
    ks = [r for r in _read(c.csv, "kstar_survival") if r.get("record_type") == "site" and r.get("status") == "ok"]
    name = "extinction_trajectories_km"
    if not lad:
        return c.placeholder(name, "Extinction", "NOT RUN")
    from p33.kstar import kaplan_meier
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    grp = defaultdict(lambda: defaultdict(list))
    for r in lad:
        grp[(r["model"].split("/")[-1], r["family"])][int(r["rung"])].append(_f(r["m_seq"]))
    for (m, fam), d in sorted(grp.items()):
        xs = sorted(d)
        axes[0].plot(xs, [sum(d[x]) / len(d[x]) for x in xs], marker="o", label=f"{m}/{fam}")
    axes[0].axhline(0, color="k", lw=0.8)
    axes[0].set_xscale("symlog", linthresh=1)
    rungs = sorted({int(r["rung"]) for r in lad})
    axes[0].set_xticks(rungs)
    axes[0].set_xticklabels([str(x) for x in rungs])
    axes[0].set_xlabel("in-context demonstrations (leakage-free)")
    axes[0].set_ylabel("mean M_seq")
    axes[0].legend(fontsize=7)
    cens_txt = []
    for (m, fam) in sorted({(r["model"].split("/")[-1], r["family"]) for r in ks}):
        g = [r for r in ks if (r["model"].split("/")[-1], r["family"]) == (m, fam)
             and r["already_correct"] not in ("True", "true")]
        if not g:
            continue
        km = kaplan_meier([_f(r["top_rung"]) if r["censored"] in ("True", "true") else _f(r["k_star"]) for r in g],
                          [r["censored"] not in ("True", "true") for r in g], population="INITIALLY_WRONG")
        xs, ys = zip(*km.curve)
        axes[1].step(list(xs) + [_f(g[0]["top_rung"])], list(ys) + [ys[-1]], where="post", label=f"{m}/{fam}")
        cens_txt.append(f"{m}/{fam}: censored {km.n_censored}/{km.n}")
    axes[1].set_xlabel("shots")
    axes[1].set_ylabel("share still reverting (KM, initially-wrong sites)")
    axes[1].legend(fontsize=7)
    fig.suptitle("Extinction: trajectories (left) and Kaplan-Meier (right)")
    c.stamp(fig, lad, extra="censoring: " + "; ".join(cens_txt))
    return c.save(fig, name)


def paraphrase_plot(c: Ctx):
    rows = [r for r in _read(c.csv, "paraphrase") if r.get("record_type") == "variant"]
    name = "paraphrase_sensitivity"
    if not rows:
        return c.placeholder(name, "Paraphrase sensitivity", "NOT RUN")
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, (m, fam) in enumerate(sorted({(r["model"], r["family"]) for r in rows})):
        g = sorted([r for r in rows if (r["model"], r["family"]) == (m, fam)], key=lambda r: r["condition"])
        ax.errorbar([r["condition"] for r in g], [_f(r["reversion_rate"]) for r in g],
                    yerr=[[(_f(r["reversion_rate"]) - (_f(r.get("ci_lo")) or _f(r["reversion_rate"]))) for r in g],
                          [((_f(r.get("ci_hi")) or _f(r["reversion_rate"])) - _f(r["reversion_rate"])) for r in g]],
                    marker="o", capsize=3, label=f"{m.split('/')[-1]}/{fam}")
    ax.set_ylim(0, 1)
    ax.set_ylabel("reversion rate")
    ax.legend(fontsize=7)
    fig.suptitle("Prompt-paraphrase sensitivity (identical rendered table, three framings)")
    c.stamp(fig, rows)
    return c.save(fig, name)


def size_plot(c: Ctx):
    rows = [r for r in _read(c.csv, "arm_a_long") if r.get("status") == "ok" and r.get("condition") == "rule"]
    name = "model_size_tokenizer"
    if not rows:
        return c.placeholder(name, "Model size / tokenizer", "NOT RUN")
    grp = defaultdict(list)
    for r in rows:
        grp[(r["model_family"], r["model_kind"], r["family"], _f(r["model_size_b"]))].append(_f(r["m_seq"]) < 0)
    fig, ax = plt.subplots(figsize=(8, 4))
    for key in sorted({k[:3] for k in grp}):
        pts = sorted((k[3], sum(v) / len(v)) for k, v in grp.items() if k[:3] == key)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", label="/".join(key))
    ax.set_xlabel("parameters (B) -- a replication stratum, not a causal variable")
    ax.set_ylabel("reversion rate (rule condition)")
    ax.set_ylim(0, 1)
    ax.legend(fontsize=7)
    fig.suptitle("Reversion by model size and tokenizer family")
    c.stamp(fig, rows, ci=False)
    return c.save(fig, name)


def h2_plot(c: Ctx):
    rows = _read(c.csv, "h2_did")
    name = "h2_three_scale"
    if not rows or rows[0].get("status") != "EXPLORATORY":
        reason = rows[0].get("reason", "NOT RUN") if rows else "NOT RUN"
        return c.placeholder(name, "H2 prior x context interaction (three scales)",
                             f"NOT TESTABLE\n{reason}")
    r = rows[0]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["margin", "logit", "probability"], [_f(r["did_margin"]), _f(r["did_logit"]), _f(r["did_prob"])])
    ax.axhline(0, color="k", lw=0.8)
    fig.suptitle(f"H2 DiD on three scales (sign_agrees={r['sign_agrees']})")
    c.stamp(fig, rows)
    return c.save(fig, name)


def h4_plot(c: Ctx):
    rows = _read(c.csv, "h4_predictions")
    name = "h4_roc_pr_calibration"
    if _not_run(rows):
        return c.placeholder(name, "H4 ROC / PR / calibration", "NOT RUN")
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for (pair, fam, split) in sorted({(r["pair"], r["family"], r["split"]) for r in rows}):
        g = [r for r in rows if (r["pair"], r["family"], r["split"]) == (pair, fam, split)]
        y = [int(r["label"]) for r in g]
        s = [_f(r["risk"]) for r in g]
        P, N = sum(y), len(y) - sum(y)
        lab = f"{pair.split('|')[0].split('/')[-1]}/{fam}/{split}"
        if P and N:
            order = sorted(range(len(s)), key=lambda i: -s[i])
            tp = fp = 0
            roc, pr = [(0, 0)], []
            for i in order:
                tp += y[i]
                fp += 1 - y[i]
                roc.append((fp / N, tp / P))
                pr.append((tp / P, tp / (tp + fp)))
            axes[0].plot(*zip(*roc), label=lab)
            axes[1].plot(*zip(*pr), label=f"{lab} (prev={P/len(y):.2f})")
            axes[1].axhline(P / len(y), ls=":", lw=0.8)
        p = [_f(r["calibrated_p"]) for r in g]
        bins = defaultdict(list)
        for pi, yi in zip(p, y):
            bins[min(int(pi * 10), 9)].append((pi, yi))
        pts = [(sum(a for a, _ in v) / len(v), sum(b for _, b in v) / len(v)) for _, v in sorted(bins.items())]
        axes[2].plot(*zip(*pts), marker="o", label=lab)
    axes[0].plot([0, 1], [0, 1], "k:", lw=0.8)
    axes[0].set_title("ROC")
    axes[1].set_title("Precision-recall (dotted = prevalence)")
    axes[2].plot([0, 1], [0, 1], "k:", lw=0.8)
    axes[2].set_title("Calibration (10 bins)")
    for ax in axes:
        ax.legend(fontsize=6)
    fig.suptitle("H4: base-checkpoint site risk predicting instruct reversion")
    c.stamp(fig, rows)
    return c.save(fig, name)


def h5_plot(c: Ctx):
    rows = [r for r in _read(c.csv, "h5_budget_outcomes") if r.get("record_type") == "arm"]
    name = "h5_benefit_per_symbol"
    if not rows:
        return c.placeholder(name, "H5 repair", "NOT RUN")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for i, r in enumerate(rows):
        lab = f"{r['arm']}#{r['seed']}"
        axes[0].bar(i, _f(r["error_reduction_per_changed_symbol"]), color={"targeted": "C3", "random": "C7", "global": "C0"}.get(r["arm"], "C1"))
        axes[1].bar(i, _f(r.get("control_degradation")) or 0, color="C8")
    for ax in axes:
        ax.set_xticks(range(len(rows)))
        ax.set_xticklabels([f"{r['arm']}#{r['seed']}" for r in rows], rotation=60, fontsize=6)
    axes[0].set_ylabel("error reduction per changed symbol")
    axes[1].axhline(_f(c.cfg.h5["low_risk_tolerance"]), color="r", ls="--", lw=0.8)
    axes[1].set_ylabel("control-site degradation (<= tolerance)")
    fig.suptitle("H5: targeted vs random (matched budget) vs global repair")
    c.stamp(fig, rows, ci=False)
    return c.save(fig, name)


def armb_plot(c: Ctx):
    rows = [r for r in _read(c.csv, "arm_b_hurdle") if r.get("record_type") == "hurdle" and r.get("stratum") == "ALL"]
    name = "armb_hurdle_outcomes"
    if not rows:
        return c.placeholder(name, "Arm B", "NOT RUN")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    labs = [f"{r['model'].split('/')[-1]}/{r['family']}/{r['lexicon']}" for r in rows]
    x = range(len(rows))
    axes[0].bar([i - 0.2 for i in x], [_f(r["p_reach"]) or 0 for r in rows], 0.4, label="P(reach site)")
    axes[0].bar([i + 0.2 for i in x], [_f(r["p_revert_given_reach"]) or 0 for r in rows], 0.4, label="P(revert | reached)")
    axes[0].set_xticks(list(x))
    axes[0].set_xticklabels(labs, rotation=30, fontsize=6)
    axes[0].legend(fontsize=7)
    axes[0].set_title("hurdle -- two separate rates, never collapsed")
    buckets = ("n_lex_fail", "n_parse_fail", "n_valid_vacuous", "n_valid_wrong", "n_valid_correct")
    bottom = [0.0] * len(rows)
    for b in buckets:
        vals = [_f(r.get(b)) or 0 for r in rows]
        axes[1].bar(list(x), vals, bottom=bottom, label=b[2:])
        bottom = [a + v for a, v in zip(bottom, vals)]
    axes[1].set_xticks(list(x))
    axes[1].set_xticklabels(labs, rotation=30, fontsize=6)
    axes[1].legend(fontsize=6)
    axes[1].set_title("five-outcome taxonomy")
    fig.suptitle("Arm B: unrestricted generation")
    c.stamp(fig, rows, ci=False)
    return c.save(fig, name)


def power_plot(c: Ctx):
    rows = [r for r in _read(c.csv, "power") if r.get("analysis") == "h4_criterion1" and r.get("power")]
    name = "power_curves"
    if not rows:
        return c.placeholder(name, "Power", "NOT RUN")
    pilot_icc = _f(rows[0].get("pilot_icc"))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for T in sorted({int(_f(r["n_templates"])) for r in rows}):
        g = sorted([r for r in rows if int(_f(r["n_templates"])) == T and abs(_f(r["icc"]) - round(pilot_icc or 0, 3)) < 1e-9],
                   key=lambda r: _f(r["true_auroc"]))
        if g:
            axes[0].plot([_f(r["true_auroc"]) for r in g], [_f(r["power"]) for r in g], marker="o", label=f"{T} templates")
    axes[0].axhline(0.8, color="r", ls="--", lw=0.8)
    axes[0].set_xlabel("true AUROC")
    axes[0].set_ylabel("P(criterion 1 met)")
    axes[0].set_title(f"H4 power at pilot ICC={pilot_icc:.3f}" if pilot_icc is not None else "H4 power")
    axes[0].legend(fontsize=7)
    T0 = sorted({int(_f(r["n_templates"])) for r in rows})[-2] if len({r["n_templates"] for r in rows}) > 1 else None
    for icc in sorted({_f(r["icc"]) for r in rows}):
        g = sorted([r for r in rows if _f(r["icc"]) == icc and int(_f(r["n_templates"])) == T0], key=lambda r: _f(r["true_auroc"]))
        if g:
            axes[1].plot([_f(r["true_auroc"]) for r in g], [_f(r["power"]) for r in g], marker=".", label=f"ICC={icc}")
    axes[1].axhline(0.8, color="r", ls="--", lw=0.8)
    axes[1].set_title(f"ICC sensitivity at {T0} templates")
    axes[1].legend(fontsize=7)
    fig.suptitle("Power (development pilot estimates only; Hanley-McNeil x design effect)")
    c.stamp(fig, rows, ci=False, extra="assumptions: binormal scores, template random intercept, two-sided 95%")
    return c.save(fig, name)


ALL = (margin_distributions, rule_effect_forest, comparisons, fertility_plot,
       extinction, paraphrase_plot, size_plot, h2_plot, h4_plot, h5_plot,
       armb_plot, power_plot)


def make_all(run_dir: str, cfg) -> dict[str, list[str]]:
    c = Ctx(run_dir, cfg)
    out = {}
    for fn, name in zip(ALL, PLOTS):
        out[name] = fn(c)
    return out
