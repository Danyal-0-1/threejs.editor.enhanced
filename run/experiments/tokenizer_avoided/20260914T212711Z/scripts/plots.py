"""plots.py — every predeclared plot, each in its own directory.

CONTRACT (enforced by validate.py):
    every plot directory contains plot.png, plot.svg, data.csv and README.md,
    and the figure is drawn FROM data.csv -- never from a value typed by hand.
    `emit()` writes data.csv first, reads it back, and plots the rows it read.

Missing cells are drawn as gaps and labelled NA. A missing value is NEVER
plotted as zero.
"""
from __future__ import annotations

import csv, json, math, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)
PLOTS = os.path.join(RUN, "plots")

LANGS = ["identity", "alpha", "beta", "gamma"]
LCOL = {"identity": "#4C72B0", "alpha": "#DD8452", "beta": "#55A868", "gamma": "#C44E52"}
CONDS = ["bare", "scaffolded"]
TASKS = ["op-selection", "selector-resolution", "arg-extraction", "multi-op"]


def short(model: str) -> str:
    return (model.replace("Qwen/Qwen2.5-Coder-", "").replace("-Instruct", "")
            .replace(" [cpu]", "·cpu"))


def emit(subdir: str, name: str, rows: list[dict], fields: list[str],
         draw, readme: str) -> str:
    """Write data.csv, READ IT BACK, and draw the figure from what was read."""
    d = os.path.join(PLOTS, subdir, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "data.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    with open(os.path.join(d, "data.csv"), encoding="utf-8") as fh:
        back = list(csv.DictReader(fh))
    fig = draw(back)
    fig.savefig(os.path.join(d, "plot.png"), dpi=160, bbox_inches="tight")
    fig.savefig(os.path.join(d, "plot.svg"), bbox_inches="tight")
    plt.close(fig)
    with open(os.path.join(d, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(readme)
    return d


def f(v, default=None):
    """CSV read-back gives strings; '' and 'None' mean NA, never 0."""
    if v is None or v == "" or v == "None":
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def main() -> int:
    with open(os.path.join(RUN, "metrics", "aggregate.json"), encoding="utf-8") as fh:
        A = json.load(fh)
    laneA, laneB, fert = A["lane_a"], A["lane_b"], A["fertility"]
    made = []

    a_models = [m for m in laneA["models"] if "[cpu]" not in m]
    a_cpu = [m for m in laneA["models"] if "[cpu]" in m]
    b_models = sorted(laneB["models"], key=lambda m: laneB["models"][m]["n_parameters"] or 0)

    # ── 6 / 7. NLL per char and per token ──────────────────────────────────
    for metric, key, unit in (("nll_per_char", "nll_per_char", "nats / Unicode character"),
                              ("nll_per_token", "nll_per_token", "nats / model token")):
        rows = [{"model": m, "n_parameters": laneA["models"][m]["n_parameters"],
                 "device": laneA["models"][m]["device"], "language": l,
                 "value": laneA["models"][m]["languages"][l][key]}
                for m in laneA["models"] for l in LANGS
                if l in laneA["models"][m]["languages"]]

        def draw(back, unit=unit, metric=metric):
            models = list(dict.fromkeys(r["model"] for r in back))
            fig, ax = plt.subplots(figsize=(1.9 * len(models) + 3, 4.2))
            w = 0.2
            for i, l in enumerate(LANGS):
                xs, ys = [], []
                for j, m in enumerate(models):
                    v = next((f(r["value"]) for r in back
                              if r["model"] == m and r["language"] == l), None)
                    if v is not None:
                        xs.append(j + (i - 1.5) * w); ys.append(v)
                ax.bar(xs, ys, w, label=l, color=LCOL[l])
            ax.set_xticks(range(len(models)))
            ax.set_xticklabels([short(m) for m in models])
            ax.set_ylabel(unit)
            ax.set_title(f"Lane A — base-model {metric.replace('_',' ')} "
                         f"(language-model surprise, NOT task accuracy)")
            ax.legend(title="language", ncol=4, fontsize=8)
            ax.grid(axis="y", alpha=0.3)
            return fig

        made.append(emit("overall", f"{'06' if metric=='nll_per_char' else '07'}_{metric}",
            rows, ["model", "n_parameters", "device", "language", "value"], draw,
            f"""# Lane A — {metric.replace('_', ' ')}

**Y axis** {unit}. **X axis** base checkpoint. Bars are the four languages.

**Denominator** corpus TOTALS over the 62 paired positive programs
(Σ nats ÷ Σ {'characters' if metric == 'nll_per_char' else 'scored tokens'}),
not a mean of per-program ratios.

**Uncertainty** none shown here — this panel is the point estimate. Paired
uncertainty is in `08_delta_nll_per_char`.

**Reading** higher = the base model found that language's programs more
surprising. {'NLL/character is the PRIMARY prior-distance measure: it holds the '
'string fixed and is therefore fertility-free.' if metric == 'nll_per_char' else
'NLL/token is DIAGNOSTIC ONLY: token boundaries differ across languages, so a '
'lexicon that fragments more spreads the same surprise over more steps.'}

This is language-model surprise on teacher-forced text. It is **not** task
accuracy, hallucination rate, instruction following, or training loss. **No
training occurred.**
"""))

    # ── 8. paired ΔNLL/char with CI ────────────────────────────────────────
    rows = []
    for m in laneA["models"]:
        for l in ("alpha", "beta", "gamma"):
            e = laneA["models"][m]["languages"].get(l, {})
            d = e.get("delta_nll_per_char")
            if d:
                rows.append({"model": m, "language": l, "delta": d["point"],
                             "ci_lo": d["ci95_lo"], "ci_hi": d["ci95_hi"],
                             "n_pairs": d["n_pairs"]})

    def draw_d(back):
        models = list(dict.fromkeys(r["model"] for r in back))
        fig, ax = plt.subplots(figsize=(1.9 * len(models) + 3, 4.2))
        w = 0.26
        for i, l in enumerate(["alpha", "beta", "gamma"]):
            xs, ys, lo, hi = [], [], [], []
            for j, m in enumerate(models):
                r = next((r for r in back if r["model"] == m and r["language"] == l), None)
                if r:
                    xs.append(j + (i - 1) * w); ys.append(f(r["delta"]))
                    lo.append(f(r["delta"]) - f(r["ci_lo"]))
                    hi.append(f(r["ci_hi"]) - f(r["delta"]))
            ax.bar(xs, ys, w, yerr=[lo, hi], capsize=3, label=l, color=LCOL[l])
        ax.axhline(0, color="k", lw=1)
        ax.set_xticks(range(len(models)))
        ax.set_xticklabels([short(m) for m in models])
        ax.set_ylabel("Δ NLL per character vs identity (nats)")
        ax.set_title("Lane A — paired ΔNLL/character, 95% paired-bootstrap CI\n"
                     "(10 000 resamples of paired program indices, seed 20260910)")
        ax.legend(title="language", fontsize=8)
        ax.grid(axis="y", alpha=0.3)
        return fig

    made.append(emit("overall", "08_delta_nll_per_char", rows,
        ["model", "language", "delta", "ci_lo", "ci_hi", "n_pairs"], draw_d,
        """# Lane A — paired ΔNLL per character vs identity

**Y axis** ΔNLL/char = (alien NLL/char) − (identity NLL/char), in nats. Zero =
no difference from ordinary 3DOM.

**Denominator** the 62 paired programs; index *i* is the SAME semantic program
in every language.

**Uncertainty** 95% paired bootstrap, 10 000 resamples, seed 20260910.
Resampling draws paired program INDICES (once, applied to both arms) and
recomputes the same ratio-of-totals estimand as the point estimate — so the
interval can never exclude the point beside it.

**Reading** a bar above zero whose interval excludes zero means the base model
found that language reliably more surprising per character than 3DOM. This is
the primary evidence for H1. It measures prior distance, **not** capability.
""")) if rows else None

    # ── 1. accuracy by language and model ──────────────────────────────────
    for cond in CONDS:
        rows = []
        for m in b_models:
            ce = laneB["models"][m]["conditions"].get(cond)
            if not ce:
                continue
            for l in LANGS:
                e = ce["languages"].get(l)
                if e:
                    p = e["semantic_accuracy"]
                    rows.append({"model": m, "language": l, "k": p["numerator"],
                                 "n": p["denominator"], "accuracy": p["proportion"],
                                 "wilson_lo": p["wilson95_lo"], "wilson_hi": p["wilson95_hi"]})
        if not rows:
            continue

        def draw_acc(back):
            models = list(dict.fromkeys(r["model"] for r in back))
            fig, ax = plt.subplots(figsize=(1.9 * len(models) + 3, 4.2))
            w = 0.2
            for i, l in enumerate(LANGS):
                xs, ys, lo, hi = [], [], [], []
                for j, m in enumerate(models):
                    r = next((r for r in back if r["model"] == m and r["language"] == l), None)
                    if r and f(r["accuracy"]) is not None:
                        v = f(r["accuracy"])
                        xs.append(j + (i - 1.5) * w); ys.append(v)
                        lo.append(max(0, v - f(r["wilson_lo"])))
                        hi.append(max(0, f(r["wilson_hi"]) - v))
                ax.bar(xs, ys, w, yerr=[lo, hi], capsize=2, label=l, color=LCOL[l])
            ax.set_xticks(range(len(models)))
            ax.set_xticklabels([short(m) for m in models])
            ax.set_ylim(0, 1.05)
            ax.set_ylabel("canonical semantic accuracy")
            ax.set_title(f"Lane B — semantic accuracy by language ({cond})\n"
                         f"Wilson 95% CI; denominator = paired generation cases")
            ax.legend(title="language", ncol=4, fontsize=8)
            ax.grid(axis="y", alpha=0.3)
            return fig

        made.append(emit("overall", f"01_accuracy_{cond}", rows,
            ["model", "language", "k", "n", "accuracy", "wilson_lo", "wilson_hi"], draw_acc,
            f"""# Lane B — semantic accuracy by language and model ({cond})

**Y axis** canonical semantic accuracy = all applicable task components correct
**AND** the answer was written in the language that was asked for.

**Denominator** the paired generation cases (`n` in data.csv) — the graceful
refusal case is excluded and scored separately.

**Uncertainty** Wilson 95% interval on the proportion.

**Reading** these are INSTRUCT checkpoints answering an editing request. They
are task accuracy, and must never be read as base-model NLL.
"""))

    # ── 2. paired accuracy difference from identity ────────────────────────
    for cond in CONDS:
        rows = []
        for m in b_models:
            ce = laneB["models"][m]["conditions"].get(cond)
            if not ce:
                continue
            for l, comp in ce.get("comparisons", {}).items():
                s = comp["semantic"]
                rows.append({"model": m, "language": l,
                             "risk_difference": s["risk_difference"],
                             "ci_lo": s["ci95_lo"], "ci_hi": s["ci95_hi"],
                             "n_pairs": s["n_pairs"],
                             "mcnemar_p": s["mcnemar"]["p_value"],
                             "n_discordant": s["mcnemar"]["n_discordant"]})
        if not rows:
            continue

        def draw_rd(back):
            models = list(dict.fromkeys(r["model"] for r in back))
            fig, ax = plt.subplots(figsize=(1.9 * len(models) + 3, 4.2))
            w = 0.26
            for i, l in enumerate(["alpha", "beta", "gamma"]):
                xs, ys, lo, hi = [], [], [], []
                for j, m in enumerate(models):
                    r = next((r for r in back if r["model"] == m and r["language"] == l), None)
                    if r and f(r["risk_difference"]) is not None:
                        v = f(r["risk_difference"])
                        xs.append(j + (i - 1) * w); ys.append(v)
                        lo.append(max(0, v - f(r["ci_lo"]))); hi.append(max(0, f(r["ci_hi"]) - v))
                ax.bar(xs, ys, w, yerr=[lo, hi], capsize=3, label=l, color=LCOL[l])
            ax.axhline(0, color="k", lw=1)
            ax.set_xticks(range(len(models)))
            ax.set_xticklabels([short(m) for m in models])
            ax.set_ylabel("accuracy difference vs identity")
            ax.set_title(f"Lane B — paired semantic-accuracy difference from identity ({cond})\n"
                         "95% paired item-level bootstrap, 10 000 resamples")
            ax.legend(title="language", fontsize=8)
            ax.grid(axis="y", alpha=0.3)
            return fig

        made.append(emit("overall", f"02_paired_accuracy_difference_{cond}", rows,
            ["model", "language", "risk_difference", "ci_lo", "ci_hi", "n_pairs",
             "mcnemar_p", "n_discordant"], draw_rd,
            f"""# Lane B — paired semantic-accuracy difference from identity ({cond})

**Y axis** paired risk difference = (alien accuracy) − (identity accuracy) on
MATCHED items. Negative = the alien arm solved fewer of the same cases.

**Denominator** `n_pairs` matched cases per bar.

**Uncertainty** 95% paired item-level bootstrap (10 000 resamples, seed
20260910). `mcnemar_p` is the exact McNemar two-sided p on the discordant pairs
only; `n_discordant` shows how much evidence that test actually has. With a
21-case set, effect sizes and intervals matter more than p-values.
"""))

    # ── 3. per-task accuracy heatmap ───────────────────────────────────────
    for cond in CONDS:
        rows = []
        for m in b_models:
            ce = laneB["models"][m]["conditions"].get(cond)
            if not ce:
                continue
            for l in LANGS:
                e = ce["languages"].get(l)
                if not e:
                    continue
                for t in TASKS:
                    p = e["per_task"][t]
                    rows.append({"model": m, "language": l, "task": t,
                                 "k": p["numerator"], "n": p["denominator"],
                                 "accuracy": p["proportion"]})
        if not rows:
            continue

        def draw_hm(back):
            models = list(dict.fromkeys(r["model"] for r in back))
            ylabels = [f"{short(m)}·{l}" for m in models for l in LANGS]
            grid = []
            for m in models:
                for l in LANGS:
                    grid.append([f(next((r["accuracy"] for r in back
                                         if r["model"] == m and r["language"] == l
                                         and r["task"] == t), None)) for t in TASKS])
            fig, ax = plt.subplots(figsize=(6.5, 0.36 * len(ylabels) + 2))
            arr = [[(v if v is not None else float("nan")) for v in row] for row in grid]
            im = ax.imshow(arr, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
            ax.set_xticks(range(len(TASKS))); ax.set_xticklabels(TASKS, rotation=30, ha="right")
            ax.set_yticks(range(len(ylabels))); ax.set_yticklabels(ylabels, fontsize=8)
            for i, row in enumerate(arr):
                for j, v in enumerate(row):
                    ax.text(j, i, "NA" if (v != v) else f"{v:.2f}",
                            ha="center", va="center", fontsize=7,
                            color="black" if (v == v and 0.25 < v < 0.8) else "white"
                            if v == v else "black")
            fig.colorbar(im, ax=ax, label="accuracy")
            ax.set_title(f"Lane B — per-task accuracy ({cond})")
            return fig

        made.append(emit("overall", f"03_per_task_heatmap_{cond}", rows,
            ["model", "language", "task", "k", "n", "accuracy"], draw_hm,
            f"""# Lane B — per-task accuracy heatmap ({cond})

**Cells** accuracy on each semantic dimension, per model × language.
**Denominator** `n` in data.csv — the paired generation cases for that cell.
**NA** means no raw evidence for that cell; it is never drawn as zero.

**Reading** the four dimensions are scored INDEPENDENTLY and are never averaged
into one number: a blended score hides which part of the task broke.
"""))

    # ── 4. parse validity vs semantic correctness ──────────────────────────
    rows = []
    for m in b_models:
        for cond in CONDS:
            ce = laneB["models"][m]["conditions"].get(cond)
            if not ce:
                continue
            for l in LANGS:
                e = ce["languages"].get(l)
                if e:
                    rows.append({"model": m, "condition": cond, "language": l,
                                 "parse_validity": e["parse_validity"]["proportion"],
                                 "semantic_accuracy": e["semantic_accuracy"]["proportion"],
                                 "n": e["semantic_accuracy"]["denominator"]})

    def draw_pv(back):
        fig, ax = plt.subplots(figsize=(6, 5.5))
        for l in LANGS:
            for cond, mk in (("bare", "o"), ("scaffolded", "^")):
                pts = [(f(r["parse_validity"]), f(r["semantic_accuracy"])) for r in back
                       if r["language"] == l and r["condition"] == cond
                       and f(r["parse_validity"]) is not None]
                if pts:
                    ax.scatter([p[0] for p in pts], [p[1] for p in pts], marker=mk,
                               color=LCOL[l], s=70, alpha=0.85,
                               label=f"{l} · {cond}", edgecolor="k", linewidth=0.4)
        ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5)
        ax.set_xlabel("parse validity"); ax.set_ylabel("semantic accuracy")
        ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.03, 1.03)
        ax.set_title("Parse validity vs semantic correctness\n"
                     "(orthogonal constructs — never averaged)")
        ax.legend(fontsize=7, ncol=2); ax.grid(alpha=0.3)
        return fig

    made.append(emit("overall", "04_parse_vs_semantic", rows,
        ["model", "condition", "language", "parse_validity", "semantic_accuracy", "n"],
        draw_pv,
        """# Parse validity vs semantic correctness

**X** fraction of outputs that are well-formed programs in the target language.
**Y** fraction that are also semantically correct against the gold IR.
**Denominator** `n` paired generation cases per point.

The dashed diagonal is parity. Points far below it parse but mean the wrong
thing — SCORING_POLICY.md S1's whole point: these are orthogonal constructs and
collapsing them into one "accuracy" number hides the behaviour under study.
"""))

    # ── 5. stacked outcome taxonomy ────────────────────────────────────────
    OUT = ["VALID_CORRECT", "VALID_WRONG", "VALID_VACUOUS", "PARSE_FAIL",
           "LEX_FAIL", "OOM", "TIMEOUT", "HARNESS_ERROR"]
    OC = {"VALID_CORRECT": "#2E8B57", "VALID_WRONG": "#F0C05A", "VALID_VACUOUS": "#9BB7D4",
          "PARSE_FAIL": "#DD8452", "LEX_FAIL": "#C44E52", "OOM": "#7F7F7F",
          "TIMEOUT": "#BBBBBB", "HARNESS_ERROR": "#000000"}
    for cond in CONDS:
        rows = []
        for m in b_models:
            ce = laneB["models"][m]["conditions"].get(cond)
            if not ce:
                continue
            for l in LANGS:
                e = ce["languages"].get(l)
                if e:
                    r = {"model": m, "language": l,
                         "n": e["semantic_accuracy"]["denominator"]}
                    for o in OUT:
                        r[o] = e["outcomes"].get(o, 0)
                    rows.append(r)
        if not rows:
            continue

        def draw_st(back):
            labels = [f"{short(r['model'])}\n{r['language']}" for r in back]
            fig, ax = plt.subplots(figsize=(0.62 * len(labels) + 3, 4.6))
            bottom = [0.0] * len(back)
            for o in OUT:
                vals = [f(r.get(o), 0.0) for r in back]
                if sum(vals) == 0:
                    continue
                ax.bar(range(len(back)), vals, 0.75, bottom=bottom, label=o, color=OC[o])
                bottom = [b + v for b, v in zip(bottom, vals)]
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, fontsize=7)
            ax.set_ylabel("cases")
            ax.set_title(f"Outcome taxonomy ({cond}) — mutually exclusive buckets")
            ax.legend(fontsize=7, ncol=3)
            return fig

        made.append(emit("overall", f"05_outcome_taxonomy_{cond}", rows,
            ["model", "language", "n"] + OUT, draw_st,
            f"""# Outcome taxonomy ({cond})

**Y axis** case counts. **Denominator** `n` paired generation cases per bar.

Buckets are MUTUALLY EXCLUSIVE and evaluated in order (SCORING_POLICY.md S3):
`LEX_FAIL` (cannot tokenise) · `PARSE_FAIL` (tokenises, no derivation) ·
`VALID_VACUOUS` (parses, zero operations — the D5 rule: a parse success and a
task failure) · `VALID_WRONG` (parses, ≥1 op, IR ≠ gold) · `VALID_CORRECT` ·
plus `OOM` / `TIMEOUT` / `HARNESS_ERROR`.

A parse failure is **not** a hallucination; hallucination categories are counted
separately.
"""))

    # ── 9. model-size scaling ──────────────────────────────────────────────
    rows = []
    for m in b_models:
        for cond in CONDS:
            ce = laneB["models"][m]["conditions"].get(cond)
            if not ce:
                continue
            for l in LANGS:
                e = ce["languages"].get(l)
                if e:
                    rows.append({"model": m,
                                 "n_parameters": laneB["models"][m]["n_parameters"],
                                 "condition": cond, "language": l,
                                 "accuracy": e["semantic_accuracy"]["proportion"]})

    def draw_sc(back):
        fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), sharey=True)
        for ax, cond in zip(axes, CONDS):
            for l in LANGS:
                # a model still running (or BLOCKED) has no meta row yet, so
                # n_parameters can be missing -- such points are DROPPED, never
                # plotted at zero.
                pts = sorted(((f(r["n_parameters"]), f(r["accuracy"])) for r in back
                              if r["language"] == l and r["condition"] == cond
                              and f(r["accuracy"]) is not None
                              and f(r["n_parameters"]) is not None),
                             key=lambda p: p[0])
                if pts:
                    ax.plot([p[0] / 1e9 for p in pts], [p[1] for p in pts],
                            "o-", color=LCOL[l], label=l)
            ax.set_xscale("log"); ax.set_xlabel("parameters (billions, log)")
            ax.set_title(cond); ax.grid(alpha=0.3); ax.set_ylim(-0.03, 1.03)
        axes[0].set_ylabel("semantic accuracy")
        axes[0].legend(fontsize=8)
        fig.suptitle("Lane B — model-size scaling by language")
        return fig

    made.append(emit("overall", "09_model_size_scaling", rows,
        ["model", "n_parameters", "condition", "language", "accuracy"], draw_sc,
        """# Model-size scaling by language

**X** parameter count (log scale). **Y** semantic accuracy.
**Denominator** the paired generation cases (see `01_accuracy_*/data.csv`).

**Uncertainty** not drawn here to keep the trend readable; Wilson intervals for
every point are in `01_accuracy_bare` / `01_accuracy_scaffolded`.

With only three or four sizes these are trends, not fitted scaling laws.
"""))

    # ── 10-14. runtime, tokens, throughput, memory ─────────────────────────
    rt = []
    for m in b_models:
        for cond in CONDS:
            ce = laneB["models"][m]["conditions"].get(cond)
            if not ce:
                continue
            for l in LANGS:
                e = ce["languages"].get(l)
                if not e:
                    continue
                rt.append({
                    "model": m, "condition": cond, "language": l,
                    "n_parameters": laneB["models"][m]["n_parameters"],
                    "e2e_median": e["e2e_seconds"]["median"], "e2e_p95": e["e2e_seconds"]["p95"],
                    "e2e_iqr": e["e2e_seconds"]["iqr"],
                    "prefill_median": e["prefill_seconds"]["median"],
                    "decode_median": e["decode_seconds"]["median"],
                    "input_tokens_median": e["input_tokens"]["median"],
                    "output_tokens_median": e["output_tokens"]["median"],
                    "tok_per_s_median": e["output_tokens_per_second"]["median"],
                    "peak_vram_bytes": laneB["models"][m]["peak_vram_allocated_bytes"],
                    "peak_rss_bytes": laneB["models"][m]["peak_rss_bytes"],
                })
    RTF = ["model", "condition", "language", "n_parameters", "e2e_median", "e2e_p95",
           "e2e_iqr", "prefill_median", "decode_median", "input_tokens_median",
           "output_tokens_median", "tok_per_s_median", "peak_vram_bytes", "peak_rss_bytes"]

    def grouped(back, cols, ylabel, title, logy=False):
        models = list(dict.fromkeys(r["model"] for r in back))
        fig, axes = plt.subplots(1, len(CONDS), figsize=(5.4 * len(CONDS), 4.2), sharey=True)
        axes = axes if hasattr(axes, "__len__") else [axes]
        w = 0.2
        for ax, cond in zip(axes, CONDS):
            for i, l in enumerate(LANGS):
                xs, ys = [], []
                for j, m in enumerate(models):
                    r = next((r for r in back if r["model"] == m and r["language"] == l
                              and r["condition"] == cond), None)
                    v = f(r[cols]) if r else None
                    if v is not None:
                        xs.append(j + (i - 1.5) * w); ys.append(v)
                ax.bar(xs, ys, w, color=LCOL[l], label=l)
            ax.set_xticks(range(len(models)))
            ax.set_xticklabels([short(m) for m in models], fontsize=8)
            ax.set_title(cond); ax.grid(axis="y", alpha=0.3)
            # Only log-scale when positive data actually exists: a model still
            # running (or BLOCKED) has no meta row, so its bar is absent rather
            # than zero, and log scaling an all-missing panel raises.
            if logy and any(p.get_height() > 0 for p in ax.patches):
                ax.set_yscale("log")
            if not ax.patches:
                ax.text(0.5, 0.5, "no data yet (NA)", transform=ax.transAxes,
                        ha="center", va="center", fontsize=11)
        axes[0].set_ylabel(ylabel); axes[0].legend(fontsize=7, ncol=2)
        fig.suptitle(title)
        return fig

    if rt:
        made.append(emit("overall", "10_runtime_median_p95", rt, RTF,
            lambda b: grouped(b, "e2e_median", "seconds (median of 3 reps)",
                              "Lane B — end-to-end per-case latency (median)"),
            """# End-to-end per-case latency

**Y** median of the repetitions for each case, then the median across cases.
**Denominator** paired generation cases. `e2e_p95` and `e2e_iqr` are in data.csv.

Model download, cold load and warm-up are **excluded** here and reported
separately in the model reports. CUDA is synchronised before and after every
timed region.

All bars are the SAME condition (FP16, CUDA, batch 1, greedy). CPU/GPU and
different precisions are never compared as if they were one condition.
"""))
        made.append(emit("overall", "11_prefill_and_decode", rt, RTF,
            lambda b: grouped(b, "prefill_median", "seconds",
                              "Lane B — prompt-prefill time (median)"),
            """# Prompt-prefill runtime

**Y** median prefill seconds, measured as a 1-new-token `generate` on the same
input. `decode_median` (end-to-end minus prefill) is in the same data.csv.

**Denominator** paired generation cases. Prefill grows with PROMPT length, which
is where scaffolding and higher-fertility languages cost extra tokens.
"""))
        made.append(emit("overall", "12_token_counts", rt, RTF,
            lambda b: grouped(b, "input_tokens_median", "input tokens (median)",
                              "Lane B — prompt token count by language"),
            """# Input / output model-token counts

**Y** median input (prompt) tokens per case; `output_tokens_median` is in the
same data.csv. **Denominator** paired generation cases.

This is the most direct behavioural consequence of tokenizer fertility: the SAME
information costs more model tokens in beta and gamma. That is a measured cost,
and it says nothing by itself about accuracy.
"""))
        made.append(emit("overall", "13_output_tokens_per_second", rt, RTF,
            lambda b: grouped(b, "tok_per_s_median", "output tokens / second",
                              "Lane B — decoding throughput"),
            """# Output tokens per second

**Y** median output tokens ÷ median decode seconds, per case.
**Denominator** paired generation cases.

Throughput is a property of the model and hardware; it is roughly flat across
languages. The COST difference shows up as more tokens (plot 12), not slower
tokens.
"""))
        made.append(emit("overall", "14_peak_memory", rt, RTF,
            lambda b: grouped(b, "peak_vram_bytes", "peak VRAM allocated (bytes)",
                              "Lane B — peak VRAM (per model; FP16/CUDA)", logy=True),
            """# Peak RAM and VRAM

**Y** peak CUDA memory allocated during that model's run (log scale);
`peak_rss_bytes` (peak process RSS) is in the same data.csv.

These are **per-model** figures, not per-language: memory is dominated by the
weights. They are repeated across the language bars so the per-model value is
readable beside the other panels.
"""))

    # ── 15/16. fertility vs accuracy difference and vs runtime ─────────────
    qwen = next((t for t in fert["tokenizers"] if t["repo"].startswith("Qwen")), None)
    if qwen:
        frows = []
        for m in b_models:
            for cond in CONDS:
                ce = laneB["models"][m]["conditions"].get(cond)
                if not ce:
                    continue
                for l in ("alpha", "beta", "gamma"):
                    comp = ce.get("comparisons", {}).get(l)
                    e = ce["languages"].get(l)
                    if comp and e:
                        frows.append({
                            "model": m, "condition": cond, "language": l,
                            "relative_fertility": qwen["rows"][l]["relative_fertility_vs_identity"],
                            "accuracy_difference": comp["semantic"]["risk_difference"],
                            "e2e_median": e["e2e_seconds"]["median"],
                            "input_tokens_median": e["input_tokens"]["median"]})

        def draw_fa(back):
            fig, ax = plt.subplots(figsize=(6.4, 4.6))
            for l in ("alpha", "beta", "gamma"):
                pts = [(f(r["relative_fertility"]), f(r["accuracy_difference"]))
                       for r in back if r["language"] == l
                       and f(r["accuracy_difference"]) is not None]
                if pts:
                    ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=70,
                               color=LCOL[l], label=l, edgecolor="k", linewidth=0.4)
            ax.axhline(0, color="k", lw=1)
            ax.set_xlabel("relative tokenizer fertility vs identity (Qwen2)")
            ax.set_ylabel("paired semantic-accuracy difference")
            ax.set_title("DESCRIPTIVE AND NON-CAUSAL\nfertility vs accuracy difference")
            ax.legend(fontsize=8); ax.grid(alpha=0.3)
            return fig

        made.append(emit("overall", "15_fertility_vs_accuracy", frows,
            ["model", "condition", "language", "relative_fertility",
             "accuracy_difference", "e2e_median", "input_tokens_median"], draw_fa,
            """# Tokenizer fertility vs semantic-accuracy difference

> **DESCRIPTIVE AND NON-CAUSAL.** Each language differs from identity in
> spelling, tokenization **and** — for gamma — lexical behaviour, all at once.
> Nothing here isolates fertility as a cause.

**X** relative fertility (candidate tokens/char ÷ identity tokens/char), Qwen2
tokenizer, 62 paired programs. **Y** paired semantic-accuracy difference.

Fertility directly demonstrates increased TOKEN COST. Whether accuracy degrades
is a separate measurement, shown on the Y axis. Only three fertility values
exist (one per language), so this cannot support a dose-response claim.
"""))
        made.append(emit("overall", "16_fertility_vs_runtime", frows,
            ["model", "condition", "language", "relative_fertility",
             "accuracy_difference", "e2e_median", "input_tokens_median"],
            lambda back: (lambda fig_ax: fig_ax[0])((lambda: (
                (lambda fig, ax: (
                    [ax.scatter([f(r["relative_fertility"]) for r in back if r["language"] == l],
                                [f(r["input_tokens_median"]) for r in back if r["language"] == l],
                                s=70, color=LCOL[l], label=l, edgecolor="k", linewidth=0.4)
                     for l in ("alpha", "beta", "gamma")],
                    ax.set_xlabel("relative tokenizer fertility vs identity (Qwen2)"),
                    ax.set_ylabel("median prompt tokens"),
                    ax.set_title("DESCRIPTIVE\nfertility vs prompt token cost"),
                    ax.legend(fontsize=8), ax.grid(alpha=0.3), (fig, ax))[-1]
                 )(*plt.subplots(figsize=(6.4, 4.6)))
            ))()),
            """# Tokenizer fertility vs cost

**X** relative fertility. **Y** median prompt tokens per case (`e2e_median` is
in the same data.csv).

This is the relationship fertility DOES establish: more tokens for the same
information. Marked descriptive because fertility is not manipulated
independently of spelling.
"""))

    # ── 17. bare vs scaffolded ─────────────────────────────────────────────
    rows = []
    for m in b_models:
        cb = laneB["models"][m]["conditions"].get("bare")
        cs = laneB["models"][m]["conditions"].get("scaffolded")
        if not (cb and cs):
            continue
        for l in LANGS:
            eb, es = cb["languages"].get(l), cs["languages"].get(l)
            if eb and es:
                rows.append({"model": m, "language": l,
                             "bare": eb["semantic_accuracy"]["proportion"],
                             "scaffolded": es["semantic_accuracy"]["proportion"],
                             "difference": es["semantic_accuracy"]["proportion"]
                                           - eb["semantic_accuracy"]["proportion"],
                             "n": eb["semantic_accuracy"]["denominator"]})

    def draw_bs(back):
        models = list(dict.fromkeys(r["model"] for r in back))
        fig, ax = plt.subplots(figsize=(1.9 * len(models) + 3, 4.2))
        w = 0.2
        for i, l in enumerate(LANGS):
            xs, ys = [], []
            for j, m in enumerate(models):
                r = next((r for r in back if r["model"] == m and r["language"] == l), None)
                if r and f(r["difference"]) is not None:
                    xs.append(j + (i - 1.5) * w); ys.append(f(r["difference"]))
            ax.bar(xs, ys, w, color=LCOL[l], label=l)
        ax.axhline(0, color="k", lw=1)
        ax.set_xticks(range(len(models))); ax.set_xticklabels([short(m) for m in models])
        ax.set_ylabel("scaffolded − bare (accuracy)")
        ax.set_title("Lane B — effect of scaffolding, by language")
        ax.legend(fontsize=8, ncol=4); ax.grid(axis="y", alpha=0.3)
        return fig

    made.append(emit("overall", "17_bare_vs_scaffolded", rows,
        ["model", "language", "bare", "scaffolded", "difference", "n"], draw_bs,
        """# Bare vs scaffolded

**Y** scaffolded accuracy − bare accuracy, same model and language.
**Denominator** `n` paired generation cases (identical in both conditions).

The only intended difference between the conditions is the predeclared
scaffold: the addressable-part and tag list, rendered in the target language's
sigils. Positive bars mean explicit task information helped.
"""))

    # ── 18. nLVP for invalid generations ───────────────────────────────────
    rows = []
    for m in b_models:
        for cond in CONDS:
            ce = laneB["models"][m]["conditions"].get(cond)
            if not ce:
                continue
            for l in LANGS:
                e = ce["languages"].get(l)
                if e:
                    s = e["nlvp_invalid_only"]
                    rows.append({"model": m, "condition": cond, "language": l,
                                 "n_invalid": s["n"], "median": s.get("median"),
                                 "q1": s.get("q1"), "q3": s.get("q3"),
                                 "min": s.get("min"), "max": s.get("max")})

    def draw_nl(back):
        fig, ax = plt.subplots(figsize=(8.5, 4.4))
        labels, meds, los, his, cols = [], [], [], [], []
        for r in back:
            if not r["n_invalid"] or int(f(r["n_invalid"], 0)) == 0:
                continue
            med = f(r["median"])
            if med is None:
                continue
            labels.append(f"{short(r['model'])}\n{r['language']}·{r['condition'][:4]}")
            meds.append(med)
            los.append(max(0, med - f(r["q1"], med))); his.append(max(0, f(r["q3"], med) - med))
            cols.append(LCOL[r["language"]])
        if not labels:
            ax.text(0.5, 0.5, "No invalid generations to plot\n"
                              "(every output lexed and parsed)",
                    ha="center", va="center", fontsize=12)
            ax.axis("off")
            return fig
        ax.bar(range(len(labels)), meds, 0.7, yerr=[los, his], capsize=3, color=cols)
        ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, fontsize=7)
        ax.set_ylabel("nLVP (median, IQR)")
        ax.set_title("nLVP for INVALID generations only (LEX_FAIL / PARSE_FAIL)")
        ax.grid(axis="y", alpha=0.3)
        return fig

    made.append(emit("overall", "18_nlvp_invalid", rows,
        ["model", "condition", "language", "n_invalid", "median", "q1", "q3", "min", "max"],
        draw_nl,
        """# nLVP distribution for invalid generations

**Y** nLVP = longest valid prefix in **DSL tokens** ÷ DSL-token length of the
reference solution in that language. Bars are medians with IQR whiskers.

**Denominator** `n_invalid` — ONLY outputs whose outcome was `LEX_FAIL` or
`PARSE_FAIL`. A cell with `n_invalid = 0` is omitted rather than drawn as zero.

nLVP is measured in DSL tokens, which is a different space from model
(sub-word) tokens; the two are never reported as one another
(SCORING_POLICY.md S4).
"""))

    # ── per-language directories ───────────────────────────────────────────
    for lang in LANGS:
        rows = []
        for m in b_models:
            for cond in CONDS:
                ce = laneB["models"][m]["conditions"].get(cond)
                e = ce["languages"].get(lang) if ce else None
                if not e:
                    continue
                r = {"model": m, "condition": cond,
                     "semantic_accuracy": e["semantic_accuracy"]["proportion"],
                     "wilson_lo": e["semantic_accuracy"]["wilson95_lo"],
                     "wilson_hi": e["semantic_accuracy"]["wilson95_hi"],
                     "parse_validity": e["parse_validity"]["proportion"],
                     "language_compliance": e["language_compliance"]["proportion"],
                     "n": e["semantic_accuracy"]["denominator"]}
                for t in TASKS:
                    r[t] = e["per_task"][t]["proportion"]
                rows.append(r)
        if not rows:
            continue
        fields = (["model", "condition", "n", "semantic_accuracy", "wilson_lo",
                   "wilson_hi", "parse_validity", "language_compliance"] + TASKS)

        def draw_lang(back, lang=lang):
            models = list(dict.fromkeys(r["model"] for r in back))
            fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
            for ax, cond in zip(axes, CONDS):
                series = ["semantic_accuracy", "parse_validity"] + TASKS
                w = 0.13
                for i, s in enumerate(series):
                    xs, ys = [], []
                    for j, m in enumerate(models):
                        r = next((r for r in back if r["model"] == m
                                  and r["condition"] == cond), None)
                        v = f(r[s]) if r else None
                        if v is not None:
                            xs.append(j + (i - len(series) / 2 + 0.5) * w); ys.append(v)
                    ax.bar(xs, ys, w, label=s)
                ax.set_xticks(range(len(models)))
                ax.set_xticklabels([short(m) for m in models], fontsize=8)
                ax.set_title(cond); ax.set_ylim(0, 1.05); ax.grid(axis="y", alpha=0.3)
            axes[0].set_ylabel("proportion")
            axes[0].legend(fontsize=6, ncol=2)
            fig.suptitle(f"{lang} — accuracy, parse validity and per-task scores")
            return fig

        made.append(emit(os.path.join("by_language", lang), "01_summary", rows, fields,
            draw_lang,
            f"""# {lang} — summary

**Y** proportion in [0,1]. **X** model, split by support condition.
**Denominator** `n` paired generation cases per bar (Wilson 95% bounds for
semantic accuracy are `wilson_lo`/`wilson_hi` in data.csv).

Series: semantic accuracy · parse validity · the four semantic dimensions.
Parse validity and semantic accuracy are shown side by side but are **never**
averaged together.
"""))

        arows = []
        for m in laneA["models"]:
            e = laneA["models"][m]["languages"].get(lang)
            if e:
                d = e.get("delta_nll_per_char") or {}
                arows.append({"model": m, "device": laneA["models"][m]["device"],
                              "nll_per_char": e["nll_per_char"],
                              "nll_per_token": e["nll_per_token"],
                              "delta_nll_per_char": d.get("point"),
                              "ci_lo": d.get("ci95_lo"), "ci_hi": d.get("ci95_hi"),
                              "fertility_tok_per_char": e["fertility_tok_per_char"]})
        if arows:
            def draw_la(back, lang=lang):
                fig, ax = plt.subplots(figsize=(6.4, 4.2))
                models = [r["model"] for r in back]
                ax.bar(range(len(models)), [f(r["nll_per_char"]) for r in back],
                       0.6, color=LCOL[lang])
                ax.set_xticks(range(len(models)))
                ax.set_xticklabels([short(m) for m in models], fontsize=8)
                ax.set_ylabel("NLL per character (nats)")
                ax.set_title(f"{lang} — Lane A base-model NLL/character")
                ax.grid(axis="y", alpha=0.3)
                return fig
            made.append(emit(os.path.join("by_language", lang), "02_lane_a_nll", arows,
                ["model", "device", "nll_per_char", "nll_per_token",
                 "delta_nll_per_char", "ci_lo", "ci_hi", "fertility_tok_per_char"],
                draw_la,
                f"""# {lang} — Lane A base-model NLL per character

**Y** nats per Unicode character on the 62-item paired positive corpus.
**Denominator** corpus totals (Σ nats ÷ Σ characters).
**Uncertainty** `delta_nll_per_char` with `ci_lo`/`ci_hi` (95% paired bootstrap,
10 000 resamples) is in data.csv{'' if lang != 'identity' else ' — empty for identity, which IS the baseline'}.

Language-model surprise on teacher-forced programs with no task prompt. **Not**
task accuracy; **no training occurred.**
"""))

    print(f"plots written: {len(made)}")
    for d in made:
        print("  " + os.path.relpath(d, RUN))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
