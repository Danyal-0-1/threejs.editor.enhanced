#!/usr/bin/env python3
"""plot_matrix.py — aggregate the Strata browser-eval CSVs and plot them.

INPUT   a folder of CSVs downloaded by strata_runner.js (one per model x quant),
        each with columns: model,condition,run,task,score,seconds,error
OUTPUT  matrix_scaffolded.csv, matrix_bare.csv, matrix_delta.csv   (handover §5)
        evaluation_matrix.png       bare vs scaffolded, faceted by model size
        quant_comparison.png        q4f16 vs q4f32, per task           (if both present)
        Also prints mean ± std so you can report VARIANCE (handover §4).

USAGE   python3 plot_matrix.py ./results
        python3 plot_matrix.py ./results --bar 0.90

Requires: pandas, matplotlib, seaborn
"""

import argparse
import glob
import os
import re

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

TASK_ORDER = ["op-type", "selector", "arg-extract", "labeling", "multi-op"]
ORDER_C = ["bare", "scaffolded", "constrained", "reason-constrained"]
PALETTE = {"bare": "#b0b7c3", "scaffolded": "#2f6df6",
           "constrained": "#12b886", "reason-constrained": "#f08c00"}
SIZE_RE = re.compile(r"(\d+\.?\d*)\s*[bB]\b")
QUANT_RE = re.compile(r"(q4f16|q4f32|q0f16|q4f16_1|q4f32_1)", re.I)


def parse_model(m):
    """Pull a size label ('1.5B') and quant ('q4f16') out of the model id."""
    size = SIZE_RE.search(m)
    quant = QUANT_RE.search(m)
    return (size.group(1) + "B" if size else m[:14],
            quant.group(1).lower().replace("_1", "") if quant else "n/a")


def size_key(s):
    try:
        return float(s.rstrip("Bb"))
    except ValueError:
        return 1e9  # non-numeric (e.g. "Haiku") sorts last


def load(folder):
    files = sorted(glob.glob(os.path.join(folder, "*.csv")))
    if not files:
        raise SystemExit(f"no CSVs found in {folder}")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df[df["task"].isin(TASK_ORDER)].copy()
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    dropped = df["score"].isna().sum()
    if dropped:
        print(f"warning: dropping {dropped} rows with no score (harness errors?)")
    df = df.dropna(subset=["score"])
    parsed = df["model"].apply(lambda m: pd.Series(parse_model(m), index=["size", "_q"]))
    df["size"] = parsed["size"]
    if "quant" not in df.columns:          # exporter may already provide it
        df["quant"] = parsed["_q"]
    df["quant"] = df["quant"].astype(str).str.lower().str.replace("_1", "", regex=False)
    print(f"loaded {len(files)} files, {len(df)} rows, "
          f"sizes={sorted(df['size'].unique(), key=size_key)}, "
          f"quants={sorted(df['quant'].unique())}")
    return df


def report_variance(df):
    """Handover §4: report mean AND spread across runs."""
    n_runs = df["run"].nunique()
    print(f"\n=== variance across {n_runs} run(s) per cell ===")
    v = (df.groupby(["size", "quant", "condition", "task"])["score"]
           .agg(["mean", "std", "count"]).reset_index())
    worst = v.sort_values("std", ascending=False).head(5)
    if n_runs > 1:
        print("highest-spread cells (check these before trusting a conclusion):")
        print(worst.to_string(index=False))
    else:
        print("only 1 run per cell — rerun with runs>1 to measure nondeterminism.")
    return v


def write_matrices(df, bar):
    """Handover §5: one matrix per condition, plus delta-vs-bare for each."""
    sizes = sorted(df["size"].unique(), key=size_key)
    conds = [c for c in ["bare", "scaffolded", "constrained", "reason-constrained"]
             if c in set(df["condition"])]
    piv = (df.groupby(["size", "condition", "task"])["score"].mean()
             .unstack("task").reindex(columns=TASK_ORDER))

    tables = {}
    for c in conds:
        t = piv.xs(c, level="condition").reindex(sizes)
        tables[c] = t
        t.round(2).to_csv(f"matrix_{c}.csv")
        print(f"\n{c.upper()}")
        print(t.round(2).to_string())

    # delta vs bare for every other condition -- THE THESIS
    if "bare" in tables:
        for c in conds:
            if c == "bare":
                continue
            d = tables[c] - tables["bare"]
            d.round(2).to_csv(f"matrix_delta_{c}_vs_bare.csv")
            print(f"\nDELTA ({c} - bare)  <- THE THESIS")
            print(d.round(2).to_string())

    # ship-size hint on the STRONGEST available condition
    best = "constrained" if "constrained" in tables else (
           "scaffolded" if "scaffolded" in tables else conds[-1])
    t = tables[best]
    ok = t[(t >= bar).all(axis=1)]
    print(f"\nbar = {bar:.2f} on all 5 tasks ({best})")
    if len(ok):
        print(f"→ ship size: {ok.index[0]}")
    else:
        print("→ no size clears the bar on all 5. tasks below bar per size:")
        print((t < bar).sum(axis=1).to_string())
    return tables


def plot_main(df, bar):
    sns.set_theme(style="whitegrid", context="talk")
    sizes = sorted(df["size"].unique(), key=size_key)
    d = df.copy()
    d["task"] = pd.Categorical(d["task"], TASK_ORDER, ordered=True)
    d["size"] = pd.Categorical(d["size"], sizes, ordered=True)

    g = sns.catplot(
        data=d, kind="bar", x="task", y="score", hue="condition",
        col="size", col_order=sizes, col_wrap=min(4, len(sizes)),
        hue_order=[c for c in ORDER_C if c in set(d["condition"])], errorbar="sd",
        palette=PALETTE,
        height=4.2, aspect=1.15,
    )
    g.set_axis_labels("", "mean pass rate")
    g.set_titles("{col_name}")
    g.set(ylim=(0, 1.05))
    for ax in g.axes.flat:
        ax.axhline(bar, ls="--", lw=1, color="#d1495b", alpha=.8)
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(30); lbl.set_ha("right")
    g.figure.suptitle("Strata: conditions by task and model size", y=1.02)
    g.figure.savefig("evaluation_matrix.png", dpi=300, bbox_inches="tight")
    print("\nwrote evaluation_matrix.png")


def plot_quant(df):
    """q4f16 vs q4f32 — does fp16 activation precision cost accuracy?"""
    quants = [q for q in df["quant"].unique() if q != "n/a"]
    if len(quants) < 2:
        print("only one quant present — skipping quant_comparison.png")
        return
    d = df.copy()
    d["task"] = pd.Categorical(d["task"], TASK_ORDER, ordered=True)
    g = sns.catplot(data=d, kind="bar", x="task", y="score", hue="quant",
                    col="condition", col_order=[c for c in ORDER_C if c in set(d["condition"])],
                    errorbar="sd", palette="viridis", height=4.2, aspect=1.1)
    g.set(ylim=(0, 1.05)); g.set_axis_labels("", "mean pass rate")
    g.set_titles("{col_name}")
    for ax in g.axes.flat:
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(30); lbl.set_ha("right")
    g.figure.suptitle("q4f16 vs q4f32 — activation precision", y=1.03)
    g.figure.savefig("quant_comparison.png", dpi=300, bbox_inches="tight")
    print("wrote quant_comparison.png")

    diff = (d.groupby(["quant", "task"])["score"].mean().unstack()[TASK_ORDER])
    print("\nquant means (all conditions pooled):")
    print(diff.round(2).to_string())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", default="./results")
    ap.add_argument("--bar", type=float, default=0.90,
                    help="pass bar per task; SET THIS BEFORE LOOKING (handover §6)")
    a = ap.parse_args()

    df = load(a.folder)
    report_variance(df)
    write_matrices(df, a.bar)
    plot_main(df, a.bar)
    plot_quant(df)
    print("\nwrote matrix_<condition>.csv and matrix_delta_<condition>_vs_bare.csv")


if __name__ == "__main__":
    main()