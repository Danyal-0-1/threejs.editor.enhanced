#!/usr/bin/env python3
"""paper_figures.py — publication figures and tables for a held-out run.

    python3 scripts/paper_figures.py --run heldout-20261007a [--root DIR] [--out DIR]

The frozen pipeline's plots (<run>/plots/) are diagnostic dumps: every model x
family x lexicon at once, with a provenance stamp. They are registered outputs
of the frozen code and stay as they are. This script sits outside the frozen
source set, like scale_analysis.py. It reads only the exported CSVs, the D11
output and the development freeze, and draws the paper's figures:

  * one message per figure; panel letters; no stamps or numbers inside;
  * models as rows grouped by family, or along log(parameters) where scale is
    the point; Okabe-Ito family colours (colour-blind safe); black/grey for
    the dom/blk grammar families, which are never pooled;
  * the numbers the old plots printed are in tables/ (CSV + Markdown), the
    explanations are in CAPTIONS.md, and provenance is in PROVENANCE.md.

Intervals are 95% percentile template-cluster bootstraps with the registered
settings (B = 2000, seed 20261002), drawn exactly as scale_analysis.py draws
them, so the Qwen2.5-Coder ladder intervals equal the D11 ones. Before
drawing, the script checks what it recomputes against the frozen export (the
per-lexicon rule effects and reversion counts, the AUROCs, the Kaplan-Meier
medians, the Arm B counts, the D11 values and intervals, the frozen
calibration) and refuses on any mismatch.
These are figure statistics: no number here replaces a frozen confirmatory
number. Output: <run>/analysis_addenda/paper_figures/ (nothing is written
inside csv/, plots/ or reports/).
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import math
import os
import random
import re
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from p33 import config as CFG  # noqa: E402
from p33 import h4, kstar  # noqa: E402
from p33 import registry as R  # noqa: E402

B, SEED = 2000, 20261002            # the registered bootstrap settings
GRAMMARS = ("dom", "blk")
GLABEL = {"dom": "dom grammar", "blk": "blk grammar"}
GCOL = {"dom": "#000000", "blk": "#8C8C8C"}
GFACE = {"dom": "#000000", "blk": "white"}
GOFF = {"dom": 0.17, "blk": -0.17}  # dom above blk when both share a row
CONDS = ("rule", "norule", "norule_lenmatched")
FAM = {  # registry family -> (display name, colour, marker)
    "qwen2.5-coder": ("Qwen2.5-Coder", "#0072B2", "o"),
    "qwen2.5": ("Qwen2.5", "#56B4E9", "D"),
    "deepseek-coder": ("DeepSeek-Coder", "#D55E00", "s"),
    "llama-3.2": ("Llama-3.2", "#009E73", "^"),
    "starcoder2": ("StarCoder2", "#CC79A7", "v"),
    "olmo-2": ("OLMo-2", "#E69F00", "P"),
}
FAM_ORDER = list(FAM)
LADDER = "qwen2.5-coder"            # the D10/D11 scale ladder
WIDE = 6.5                          # inches: full text width (one-column layouts scale it)
RUNGS = [0, 1, 2, 4, 8, 16, 32]
SILENT = "#D55E00"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Liberation Sans", "Nimbus Sans", "Arial", "DejaVu Sans"],
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
    "axes.grid": True, "axes.grid.axis": "x", "grid.color": "0.88", "grid.linewidth": 0.5,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5,
    "ytick.major.size": 2.5, "lines.linewidth": 1.0, "lines.markersize": 4,
    "legend.frameon": False, "legend.handletextpad": 0.4, "legend.columnspacing": 1.2,
    "hatch.linewidth": 0.6,
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    "figure.constrained_layout.h_pad": 0.04, "figure.constrained_layout.w_pad": 0.04,
})
csv.field_size_limit(10 ** 9)


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def die(msg: str):
    raise SystemExit(f"REFUSED: {msg}")


def read_csv(path: str) -> list[dict]:
    if not os.path.exists(path):
        die(f"{path} does not exist; run the frozen export (and scale_analysis.py) first")
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def S(m: str):
    return R.spec(m)


def model_key(m: str):
    s = S(m)
    return (FAM_ORDER.index(s.family), s.size_b, s.kind != "base")


def short(m: str) -> str:
    return m.split("/")[-1]


def size_label(m: str) -> str:
    return f"{S(m).size_b:g}B"


def kind_label(m: str) -> str:
    return f"{S(m).size_b:g}B {S(m).kind}"


def num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return math.nan


def fmt(x, d=3) -> str:
    return "" if x is None or not math.isfinite(x) else f"{x:.{d}f}"


def sg(x, d=3) -> str:
    """Signed number with a typographic minus, for captions."""
    return f"{x:+.{d}f}".replace("-", "−")


def fci(pt, lohi, d=3, sign=False) -> str:
    f = "{:+.%df}" % d if sign else "{:.%df}" % d
    return f"{f.format(pt)} [{f.format(lohi[0])}, {f.format(lohi[1])}]"


def rng_text(vals, d=2) -> str:
    v = [x for x in vals if math.isfinite(x)]
    return f"{min(v):.{d}f}–{max(v):.{d}f}"


# ---------------------------------------------------------------------------
# bootstrap (identical draws to scale_analysis.py)
# ---------------------------------------------------------------------------

_DRAWS: dict[tuple, np.ndarray] = {}


def draws(templates: list[str], key: str) -> np.ndarray:
    """B x T template multiplicities, drawn as scale_analysis.py draws them:
    random.Random(f"{seed}/{key}"), T draws with replacement per replicate.
    Column j counts templates[j], so `templates` must be sorted as there."""
    k = (tuple(templates), key)
    if k not in _DRAWS:
        rng = random.Random(f"{SEED}/{key}")
        T = len(templates)
        W = np.zeros((B, T))
        for b in range(B):
            for _ in range(T):
                W[b, rng.randrange(T)] += 1
        _DRAWS[k] = W
    return _DRAWS[k]


def interval(boots) -> tuple[float, float]:
    """95% percentile interval with scale_analysis.py's order statistics."""
    v = np.sort(np.asarray(boots, float))
    v = v[np.isfinite(v)]
    if not v.size:
        return (math.nan, math.nan)
    n = v.size
    return float(v[int(0.025 * (n - 1))]), float(v[int(math.ceil(0.975 * (n - 1)))])


def ratio(numer, denom, W) -> tuple[float, tuple[float, float]]:
    numer, denom = np.asarray(numer, float), np.asarray(denom, float)
    with np.errstate(invalid="ignore", divide="ignore"):
        point = float(numer.sum() / denom.sum()) if denom.sum() else math.nan
        return point, interval((W @ numer) / (W @ denom))


def auroc_w(scores, labels, tix, W=None):
    """Mann-Whitney AUROC (ties count 1/2) at the point and for every template
    resample: a template drawn w times enters with weight w, as in D11."""
    s, y, t = np.asarray(scores, float), np.asarray(labels, float), np.asarray(tix, int)
    o = np.argsort(s, kind="mergesort")
    s, y, t = s[o], y[o], t[o]
    starts = np.r_[0, np.flatnonzero(np.diff(s)) + 1]

    def auc(w):
        wp, wn = w * y, w * (1 - y)
        gp, gn = np.add.reduceat(wp, starts, axis=1), np.add.reduceat(wn, starts, axis=1)
        below = np.cumsum(gn, axis=1) - gn
        with np.errstate(invalid="ignore", divide="ignore"):
            return (gp * (below + 0.5 * gn)).sum(1) / (wp.sum(1) * wn.sum(1))

    point = float(auc(np.ones((1, s.size)))[0])
    return point, (interval(auc(W[:, t])) if W is not None else (math.nan, math.nan))


# ---------------------------------------------------------------------------
# layout
# ---------------------------------------------------------------------------

def rows_layout(items, label):
    """Rows top to bottom, grouped by family, a bold header row per family."""
    entries, prev = [], None
    for m in sorted(items, key=model_key):
        if S(m).family != prev:
            prev = S(m).family
            entries.append((FAM[prev][0], None))
        entries.append((label(m), m))
    n = len(entries)
    ypos = {m: n - 1 - i for i, (_, m) in enumerate(entries) if m is not None}
    ticks = [(n - 1 - i, lab, m is None) for i, (lab, m) in enumerate(entries)]
    return ypos, ticks


def style_rows(ax, ticks, labels=True):
    ax.set_yticks([y for y, _, _ in ticks])
    ax.set_yticklabels([lab for _, lab, _ in ticks])
    if labels:
        for t, (_, _, head) in zip(ax.get_yticklabels(), ticks):
            if head:
                t.set_fontweight("bold")
    else:
        ax.tick_params(axis="y", labelleft=False)
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.7, len(ticks) - 0.3)
    groups = []
    for y, _, head in ticks:
        if head:
            groups.append([y, y])
        else:
            groups[-1][1] = y
    for k, (top, bottom) in enumerate(groups):
        if k % 2:
            ax.axhspan(bottom - 0.5, top + 0.5, color="0.955", lw=0, zorder=0)


def dodge(items, spacing=0.045, join=0.08):
    """x positions on a log axis: models within `join` dex of each other are
    spread `spacing` dex apart (smallest size first) so markers do not overlap."""
    clusters = []
    for m in sorted(items, key=lambda m: (S(m).size_b, FAM_ORDER.index(S(m).family), S(m).kind != "base")):
        lx = math.log10(S(m).size_b)
        if clusters and lx - clusters[-1][0] < join:
            clusters[-1][1].append(m)
        else:
            clusters.append([lx, [m]])
    x = {}
    for _, ms in clusters:
        centre = float(np.mean([math.log10(S(m).size_b) for m in ms]))
        for i, m in enumerate(ms):
            x[m] = 10 ** (centre + (i - (len(ms) - 1) / 2) * spacing)
    return x


def letter(ax, ch, desc=""):
    ax.set_title(ch, loc="left", fontweight="bold", fontsize=9)
    if desc:
        ax.set_title(desc, loc="center")


def hbar(ax, y, lo, hi, color, lw=1.0, z=2):
    ax.plot([lo, hi], [y, y], color=color, lw=lw, solid_capstyle="butt", zorder=z)


def vbar(ax, x, lo, hi, color, lw=0.9, z=2):
    ax.plot([x, x], [lo, hi], color=color, lw=lw, solid_capstyle="butt", zorder=z)


def dot(ax, x, y, marker="o", color="black", face=None, ms=3.8, mew=0.9, z=3):
    ax.plot(x, y, marker=marker, color=color, mfc=color if face is None else face, mec=color,
            mew=mew, ms=ms, ls="none", zorder=z)


def handle(label, marker="o", color="black", face=None, ls="none", ms=4, lw=1.0):
    return Line2D([], [], marker=marker, color=color, mfc=color if face is None else face, mec=color,
                  ls=ls, ms=ms, lw=lw, label=label)


def grammar_handles():
    return [handle("dom grammar", color=GCOL["dom"], face=GFACE["dom"]),
            handle("blk grammar", color=GCOL["blk"], face=GFACE["blk"])]


def log2_axis(ax, lo=0.5, hi=32):
    ax.set_xscale("log", base=2)
    ticks = [t for t in (0.5, 1, 2, 4, 8, 16, 32) if lo <= t <= hi]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:g}" for t in ticks])
    ax.minorticks_off()


def rung_axis(ax):
    ax.set_xscale("symlog", linthresh=1, linscale=0.6)
    ax.set_xticks(RUNGS)
    ax.set_xticklabels([str(t) for t in RUNGS])
    ax.minorticks_off()
    ax.set_xlim(0, 32)


def save(fig, out, name, made, book):
    """Each figure as PDF, PNG and SVG, and as one page of ALL_FIGURES.pdf (for review)."""
    for ext in ("pdf", "png", "svg"):
        fig.savefig(os.path.join(out, f"{name}.{ext}"))
    book.savefig(fig)
    plt.close(fig)
    made.append(name)


def write_table(out, name, rows, cols, title, note=""):
    with open(os.path.join(out, "tables", f"{name}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    md = [f"# {title}", ""] + ([note, ""] if note else [])
    md += ["| " + " | ".join(c.replace("|", "\\|") for c in cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    md += ["| " + " | ".join(str(r.get(c, "")).replace("|", "\\|") for c in cols) + " |" for r in rows]
    with open(os.path.join(out, "tables", f"{name}.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--root", default=None, help="results root (default: P33_RESULTS_ROOT or the Sol layout)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    root = a.root or CFG.results_root()
    rd = os.path.join(root, a.run)
    out = a.out or os.path.join(rd, "analysis_addenda", "paper_figures")
    os.makedirs(os.path.join(out, "tables"), exist_ok=True)

    def csvp(name):
        return os.path.join(rd, "csv", f"{name}.csv")

    made, checks, captions = [], [], {}
    book = PdfPages(os.path.join(out, "ALL_FIGURES.pdf"))

    # --- the development freeze that this run was unlocked against ------------
    with open(os.path.join(rd, "HELDOUT_UNLOCK.json"), encoding="utf-8") as fh:
        unlock = json.load(fh)
    dev_run = os.path.basename(os.path.dirname(unlock["freeze_path"]))
    freeze_path = os.path.join(root, dev_run, "DEV_FREEZE.json")
    if not os.path.exists(freeze_path) or CFG.sha256_file(freeze_path) != unlock["freeze_sha256"]:
        die(f"{freeze_path} is missing or is not the freeze this run was unlocked against")
    with open(freeze_path, encoding="utf-8") as fh:
        freeze = json.load(fh)
    checks.append(f"development freeze `{dev_run}/DEV_FREEZE.json` matches the unlock "
                  f"(sha256 {unlock['freeze_sha256'][:16]}…)")

    # =========================================================================
    # Arm A: per-template counts for every model x grammar x condition
    # =========================================================================
    arm = [r for r in read_csv(csvp("arm_a_long")) if r["status"] == "ok"]
    models = sorted({r["model"] for r in arm}, key=model_key)
    revision = {}
    for r in arm:
        revision.setdefault(r["model"], r["model_revision"])
    tpl = {g: sorted({r["template"] for r in arm if r["family"] == g}) for g in GRAMMARS}
    tix = {g: {t: i for i, t in enumerate(tpl[g])} for g in GRAMMARS}
    lexicons = {g: sorted({r["lexicon"] for r in arm if r["family"] == g}) for g in GRAMMARS}
    tokenizer = {}
    site = defaultdict(dict)
    where, stratum_of, lexicon_of = {}, {}, {}
    for r in arm:
        site[(r["model"], r["family"], r["site_id"])][r["condition"]] = float(r["m_seq"])
        where[(r["family"], r["site_id"])] = tix[r["family"]][r["template"]]
        stratum_of[(r["family"], r["site_id"])] = r["stratum"]
        lexicon_of[(r["family"], r["site_id"])] = r["lexicon"]
        tokenizer.setdefault(r["model"], r["tokenizer_id"])
    acc: dict[tuple, np.ndarray] = {}
    margins = defaultdict(list)

    def bump(key, g, i, v):
        if key not in acc:
            acc[key] = np.zeros(len(tpl[g]))
        acc[key][i] += v

    for (m, g, sid), c in site.items():
        i = where[(g, sid)]
        for cond, v in c.items():
            bump((m, g, cond, "n"), g, i, 1)
            bump((m, g, cond, "rev"), g, i, v < 0)
            margins[(m, g, cond)].append(v)
        if "rule" in c:
            bump((m, g, "rule", stratum_of[(g, sid)], "n"), g, i, 1)
            bump((m, g, "rule", stratum_of[(g, sid)], "rev"), g, i, c["rule"] < 0)
        for ctl in ("norule", "norule_lenmatched"):
            if "rule" in c and ctl in c:
                lx = lexicon_of[(g, sid)]
                bump((m, g, ctl, lx, "eff"), g, i, c["rule"] - c[ctl])
                bump((m, g, ctl, lx, "pairs"), g, i, 1)

    def W_rev(m, g):
        return draws(tpl[g], f"{g}/reversion/{S(m).kind}")

    def lexicon_mean(m, g, ctl):
        """Mean over the lexicons of the per-lexicon mean rule effect (each
        lexicon weighs the same, as in the results documents), with the
        template resample applied to every lexicon at once."""
        W = W_rev(m, g)
        pts, boots = [], []
        for lx in lexicons[g]:
            pt, _ = ratio(acc[(m, g, ctl, lx, "eff")], acc[(m, g, ctl, lx, "pairs")], W)
            pts.append(pt)
            with np.errstate(invalid="ignore", divide="ignore"):
                boots.append((W @ acc[(m, g, ctl, lx, "eff")]) / (W @ acc[(m, g, ctl, lx, "pairs")]))
        return float(np.mean(pts)), interval(np.mean(boots, axis=0))

    rate = {(m, g, c): ratio(acc[(m, g, c, "rev")], acc[(m, g, c, "n")], W_rev(m, g))
            for m in models for g in GRAMMARS for c in CONDS}
    effect = {(m, g, c): lexicon_mean(m, g, c)
              for m in models for g in GRAMMARS for c in ("norule", "norule_lenmatched")}
    rule_rows = read_csv(csvp("rule_effect"))
    n_re = 0
    for r in rule_rows:
        if r["record_type"] == "rule_effect" and r["stratum"] == "ALL":
            key = (r["model"], r["family"], r["control"], r["lexicon"])
            mine = acc[key[:3] + (key[3], "eff")].sum() / acc[key[:3] + (key[3], "pairs")].sum()
            if abs(mine - num(r["mean_rule_effect"])) > 1e-5:
                die(f"rule effect {key}: {mine:.6f} != frozen {r['mean_rule_effect']}")
            n_re += 1
    checks.append(f"the per-lexicon mean rule effect equals the frozen export in all {n_re} "
                  "model x grammar x lexicon x control cells")
    rev_cell = defaultdict(lambda: [0, 0])
    for (m, g, sid), c in site.items():
        if "rule" in c:
            for st in ("ALL", stratum_of[(g, sid)]):
                cell_ = rev_cell[(m, g, lexicon_of[(g, sid)], st)]
                cell_[0] += 1
                cell_[1] += c["rule"] < 0
    n_rv = 0
    for r in rule_rows:
        if r["record_type"] == "reversion" and r["condition"] == "rule":
            n_, k_ = rev_cell[(r["model"], r["family"], r["lexicon"], r["stratum"])]
            if n_ != int(r["n_rows"]) or abs(k_ / n_ - num(r["reversion_rate"])) > 1e-5:
                die(f"reversion {r['model']} {r['family']} {r['lexicon']} {r['stratum']}: "
                    f"{k_}/{n_} != frozen {r['reversion_rate']} of {r['n_rows']}")
            n_rv += 1
    checks.append(f"site counts and reversion rates with the table equal the frozen export in all {n_rv} "
                  "model x grammar x lexicon x role cells")

    # =========================================================================
    # H4: AUROC of the base-model risk, and of the two baselines that matter
    # =========================================================================
    h4p = read_csv(csvp("h4_predictions"))
    h4m = read_csv(csvp("h4_metrics_baselines_calibration"))
    pairs = sorted({r["pair"] for r in h4p}, key=lambda p: model_key(p.split("|")[0]))
    by_pair = defaultdict(list)
    for r in h4p:
        by_pair[(r["pair"], r["family"])].append(r)
    frozen_auc = {(r["pair"], r["family"], r["predictor"]): num(r["auroc"])
                  for r in h4m if r["record_type"] == "metric"}
    auc = {}
    for p in pairs:
        for g in GRAMMARS:
            rr = by_pair[(p, g)]
            idx = [tix[g][r["template"]] for r in rr]
            lab = [int(r["label"]) for r in rr]
            for col in ("risk", "terminal_rate", "length"):
                W = draws(tpl[g], f"{g}/h4_auroc/pair") if col == "risk" else None
                auc[(p, g, col)] = auroc_w([float(r[col]) for r in rr], lab, idx, W)
                ref = frozen_auc[(p, g, col)]
                if abs(auc[(p, g, col)][0] - ref) > 1e-5:
                    die(f"AUROC {p} {g} {col}: {auc[(p, g, col)][0]:.6f} != frozen {ref:.6f}")
            ref = h4.auroc([float(r["risk"]) for r in rr], lab)
            if abs(auc[(p, g, "risk")][0] - ref) > 1e-12:
                die(f"AUROC {p} {g}: vectorised {auc[(p, g, 'risk')][0]} != p33.h4.auroc {ref}")
    checks.append(f"AUROC of the risk score and of the role-level and length baselines equals the frozen "
                  f"export in all {len(pairs) * len(GRAMMARS)} pair x grammar groups")

    # --- D11: point values and per-size intervals must be the scale analysis's --
    d11 = {(r["family"], r["outcome"], r["kind"]): r
           for r in read_csv(os.path.join(rd, "analysis_addenda", "d11_scale", "scale_analysis.csv"))}
    n_d11 = 0
    for (g, outcome, kind), r in d11.items():
        for col in r:
            if not col.startswith("value_"):
                continue
            size = col[len("value_"):]
            base = next(s.id for s in R.REGISTRY.values()
                        if s.family == LADDER and s.kind == "base" and f"{s.size_b:g}B" == size)
            if outcome == "reversion":
                mine = rate[(base if kind == "base" else S(base).pair, g, "rule")]
            else:
                mine = auc[(f"{base}|{S(base).pair}", g, "risk")]
            lo, hi = json.loads(r[f"ci_{size}"])
            if abs(mine[0] - float(r[col])) > 1e-9 or abs(mine[1][0] - lo) > 1e-9 or abs(mine[1][1] - hi) > 1e-9:
                die(f"D11 {g}/{outcome}/{kind}/{size}: {mine} != ({r[col]}, [{lo}, {hi}])")
            n_d11 += 1
    checks.append(f"the {n_d11} Qwen2.5-Coder ladder values and their 95% intervals equal the D11 output exactly")

    # =========================================================================
    # Figure 2 — H4
    # =========================================================================
    bases = [p.split("|")[0] for p in pairs]
    yp, ticks = rows_layout(bases, size_label)
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 2.75), layout="constrained")
    for k, g in enumerate(GRAMMARS):
        ax = axes[k]
        style_rows(ax, ticks, labels=k == 0)
        ax.axvline(0.5, color="0.55", lw=0.6, ls=":", zorder=1)
        ax.axvline(0.6, color="0.55", lw=0.6, ls="--", zorder=1)
        for p in pairs:
            y = yp[p.split("|")[0]]
            pt, (lo, hi) = auc[(p, g, "risk")]
            hbar(ax, y, lo, hi, "black")
            dot(ax, pt, y, ms=4)
            dot(ax, auc[(p, g, "terminal_rate")][0], y, "D", "0.4", "white", ms=3.4, mew=0.8)
            dot(ax, auc[(p, g, "length")][0], y, "x", "0.4", ms=3.8, mew=0.9)
        ax.set_xlim(0.35, 1.0)
        ax.set_xlabel("AUROC for the instruct model's reversions")
        letter(ax, "ab"[k], GLABEL[g])
    fig.legend(handles=[handle("base-model margin (95% CI)", ls="-"),
                        handle("role-level baseline", "D", "0.4", "white", ms=3.4),
                        handle("length baseline", "x", "0.4", ms=3.8),
                        handle("chance (identity baseline)", None, "0.55", ls=":"),
                        handle("C1 threshold", None, "0.55", ls="--")],
               loc="outside lower center", ncol=5)
    save(fig, out, "fig2_h4", made, book)
    risk_vals = [auc[(p, g, "risk")][0] for p in pairs for g in GRAMMARS]
    c12 = [r for r in h4m if r["record_type"] == "criterion" and r["criterion"][:2] in ("C1", "C2")]
    met = {c: sum(1 for r in c12 if r["criterion"][:2] == c and r["status"] == "MET") for c in ("C1", "C2")}
    groups = len(pairs) * len(GRAMMARS)
    captions["fig2_h4"] = (
        "**H4: the base model's margin predicts where its instruct twin reverts.** "
        "Rows are base/instruct pairs on held-out mappings; (a) dom, (b) blk grammar. Filled circles: AUROC "
        "of the risk score, −M(base, rule), for the instruct model's reversions (M < 0), with 95% "
        "template-cluster bootstrap intervals (B = 2000). Open diamonds: role-level baseline (cross-fitted "
        "per-role reversion rate). Crosses: length baseline. Dotted line: chance, which is also the identity "
        f"baseline; dashed line: the C1 threshold (identity + 0.10). AUROC {rng_text(risk_vals)}; C1 is met in "
        f"{met['C1']} and C2 in {met['C2']} of the {groups} pair × grammar groups (Table 2).")

    # =========================================================================
    # Figure 3 — reversion with and without the token table
    # =========================================================================
    ym, mticks = rows_layout(models, kind_label)
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 3.9), layout="constrained")
    for k, g in enumerate(GRAMMARS):
        ax = axes[k]
        style_rows(ax, mticks, labels=k == 0)
        for m in models:
            y = ym[m]
            pr, (lo, hi) = rate[(m, g, "rule")]
            pn, pl = rate[(m, g, "norule")][0], rate[(m, g, "norule_lenmatched")][0]
            ax.plot([pr, pn], [y, y], color="0.72", lw=0.8, zorder=1)
            hbar(ax, y, lo, hi, "black")
            dot(ax, pn, y, "o", "0.4", "white", ms=3.6, mew=0.8)
            dot(ax, pl, y, "D", "0.4", "white", ms=3.0, mew=0.8)
            dot(ax, pr, y, ms=3.8)
        ax.set_xlabel("reversion rate (share of sites with M < 0)")
        letter(ax, "ab"[k], GLABEL[g])
    lo_ = min(min(rate[(m, g, c)][0], rate[(m, g, "rule")][1][0]) for m in models for g in GRAMMARS for c in CONDS)
    hi_ = max(max(rate[(m, g, c)][0], rate[(m, g, "rule")][1][1]) for m in models for g in GRAMMARS for c in CONDS)
    for ax in axes:
        ax.set_xlim(math.floor((lo_ - 0.005) * 40) / 40, math.ceil((hi_ + 0.005) * 40) / 40)
    fig.legend(handles=[handle("with the token table (95% CI)", ls="-"),
                        handle("without the table", "o", "0.4", "white", ms=3.6),
                        handle("without, length-matched", "D", "0.4", "white", ms=3.0)],
               loc="outside lower center", ncol=3)
    save(fig, out, "fig3_reversion", made, book)
    rr_rule = [rate[(m, g, "rule")][0] for m in models for g in GRAMMARS]
    rr_none = [rate[(m, g, "norule")][0] for m in models for g in GRAMMARS]
    lower = sum(1 for m in models for g in GRAMMARS if rate[(m, g, "rule")][0] < rate[(m, g, "norule")][0])
    eff_all = [effect[(m, g, c)][0] for m in models for g in GRAMMARS for c in ("norule", "norule_lenmatched")]
    eff_txt = (f"the table raises the mean margin for every checkpoint and grammar, against both controls "
               f"({rng_text(eff_all)} nats)" if min(eff_all) > 0 else
               f"the mean margin gain from the table ranges {rng_text(eff_all)} nats")
    captions["fig3_reversion"] = (
        "**Reversion persists with the token table.** Reversion rate (share of decision sites where the "
        "margin M, the log-probability of the correct spelling minus that of the familiar one scored from the "
        "first token where they differ, is negative) for every checkpoint, pooled over the five held-out "
        "lexicons; (a) dom, (b) blk. Filled: with the full token table (95% template-cluster bootstrap "
        "interval); open circle: without it; open diamond: without it, padded to the same prompt length. "
        f"Reversion is {rng_text(rr_rule, 3)} with the table and {rng_text(rr_none, 3)} without; the table "
        f"lowers it for {lower} of {len(rr_rule)} checkpoint × grammar combinations. On the margin scale, "
        f"{eff_txt}; Tables C1 and C2.")

    # =========================================================================
    # Figure 4 — scale (D10/D11)
    # =========================================================================
    xm, xp = dodge(models), dodge(bases)
    fig, axes = plt.subplots(2, 2, figsize=(WIDE, 4.3), layout="constrained", sharex=True, sharey="row")
    for k, g in enumerate(GRAMMARS):
        ax = axes[0, k]
        for kind, ls in (("base", "-"), ("instruct", "--")):
            lad = [m for m in models if S(m).family == LADDER and S(m).kind == kind]
            ax.plot([xm[m] for m in lad], [rate[(m, g, "rule")][0] for m in lad], ls=ls,
                    color=FAM[LADDER][1], lw=0.8, alpha=0.6, zorder=1)
        for m in models:
            pt, (lo, hi) = rate[(m, g, "rule")]
            _, col, mk = FAM[S(m).family]
            vbar(ax, xm[m], lo, hi, col)
            dot(ax, xm[m], pt, mk, col, col if S(m).kind == "base" else "white", ms=4)
        letter(ax, "ab"[k], GLABEL[g])
        ax = axes[1, k]
        lad = [p for p in pairs if S(p.split("|")[0]).family == LADDER]
        ax.plot([xp[p.split("|")[0]] for p in lad], [auc[(p, g, "risk")][0] for p in lad],
                color=FAM[LADDER][1], lw=0.8, alpha=0.6, zorder=1)
        for p in pairs:
            b = p.split("|")[0]
            pt, (lo, hi) = auc[(p, g, "risk")]
            _, col, mk = FAM[S(b).family]
            vbar(ax, xp[b], lo, hi, col)
            dot(ax, xp[b], pt, mk, col, ms=4)
        letter(ax, "cd"[k])
        ax.set_xscale("log")
        xt = [0.5, 1, 3, 7, 14, 32, 72]
        ax.set_xticks(xt)
        ax.set_xticklabels([f"{v:g}B" for v in xt])
        ax.minorticks_off()
        ax.set_xlim(0.38, 100)
        ax.set_xlabel("parameters")
    for ax in axes.flat:
        ax.grid(axis="y", visible=True)
        ax.grid(axis="x", visible=False)
    axes[0, 0].set_ylabel("reversion rate\nwith the token table")
    axes[1, 0].set_ylabel("H4 AUROC")
    fams = [f for f in FAM_ORDER if any(S(m).family == f for m in models)]
    enc = [handle("base", "o", "0.35"), handle("instruct", "o", "0.35", "white"),
           handle("ladder (base)", None, FAM[LADDER][1], ls="-"),
           handle("ladder (instruct)", None, FAM[LADDER][1], ls="--")]
    top = [handle(FAM[f][0], FAM[f][2], FAM[f][1]) for f in fams]
    ncol = max(len(top), len(enc))
    top += [Line2D([], [], ls="none", label=" ")] * (ncol - len(top))
    enc += [Line2D([], [], ls="none", label=" ")] * (ncol - len(enc))
    # legends fill column by column: interleave so that families form row 1
    fig.legend(handles=[h for pair in zip(top, enc) for h in pair], loc="outside lower center", ncol=ncol)
    save(fig, out, "fig4_scale", made, book)

    def holm_p(r):
        p = num(r["p_holm"])
        return f"< {len(d11) / B:.3g}" if p == 0 else f"= {p:.3f}"

    rev_sig = sum(1 for (g, o, _), r in d11.items() if o == "reversion" and num(r["p_holm"]) < 0.05)
    n_rev = sum(1 for (_, o, _) in d11 if o == "reversion")
    auc_d11 = {g: d11[(g, "h4_auroc", "pair")] for g in GRAMMARS}
    captions["fig4_scale"] = (
        "**Scale does not reduce reversion; in dom, the H4 AUROC declines across the ladder, "
        "non-monotonically.** "
        "(a, b) Reversion rate with the token table and (c, d) H4 AUROC against parameters (log axis), "
        "with 95% template-cluster bootstrap intervals. Filled: base; open: instruct (pairs in c, d). Lines "
        "join the Qwen2.5-Coder ladder (0.5–32B), the only series the pre-specified scale analysis (D10/D11) "
        "uses; the other families are shown for context. Markers within ~20% in size are spread "
        f"horizontally. Ladder slopes per tenfold size: reversion, {rev_sig} of {n_rev} series significant after "
        "Holm correction; AUROC "
        + "; ".join(f"{sg(num(r['slope_per_log10_size']))} in {g} (Holm p {holm_p(r)})" for g, r in auc_d11.items())
        + " (Table C4). Sizes are not randomized: these are associations.")

    # =========================================================================
    # Figure 5 — adaptation (extinction ladder)
    # =========================================================================
    ks = read_csv(csvp("kstar_survival"))
    sites = defaultdict(list)
    for r in ks:
        if r["record_type"] == "site" and r["status"] == "ok" and r["already_correct"] == "False":
            sites[(r["model"], r["family"])].append(r)
    kms = {(r["model"], r["family"]): r for r in ks
           if r["record_type"] == "km_summary" and r["population"] == "INITIALLY_WRONG"}

    def te(rs):
        return ([float(r["top_rung"]) if r["censored"] == "True" else float(r["k_star"]) for r in rs],
                [r["censored"] == "False" for r in rs])

    curves = {}
    for key, fr in kms.items():
        km = kstar.kaplan_meier(*te(sites[key]), population="INITIALLY_WRONG")
        ref = num(fr["km_median"])
        if not ((km.median is None and not math.isfinite(ref)) or
                (km.median is not None and abs(km.median - ref) < 1e-4)):
            die(f"KM median {key}: {km.median} != frozen {fr['km_median']}")
        curves[key] = km
    checks.append(f"Kaplan-Meier medians recomputed from the site rows equal the frozen export in all "
                  f"{len(kms)} model x grammar groups")

    fig = plt.figure(figsize=(WIDE, 3.9), layout="constrained")
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.15, 1.0])
    ax = fig.add_subplot(gs[0])
    pooled = {}
    for g in GRAMMARS:
        for m in models:
            c = curves[(m, g)].curve
            ax.step([t for t, _ in c] + [32], [s for _, s in c] + [c[-1][1]], where="post",
                    color=GCOL[g], lw=0.4, alpha=0.25)
        allr = [r for m in models for r in sites[(m, g)]]
        km = kstar.kaplan_meier(*te(allr), population="INITIALLY_WRONG")
        pooled[g] = km
        ax.step([t for t, _ in km.curve] + [32], [s for _, s in km.curve] + [km.curve[-1][1]], where="post",
                color=GCOL[g], lw=1.6, label=GLABEL[g])
    rung_axis(ax)
    ax.set_ylim(0, 1.02)
    ax.grid(axis="y", visible=True)
    ax.set_xlabel("worked examples in the prompt")
    ax.set_ylabel("share of initially wrong sites\nnot yet switched")
    letter(ax, "a")

    ax = fig.add_subplot(gs[1])
    style_rows(ax, mticks)
    for m in models:
        for g in GRAMMARS:
            r = kms[(m, g)]
            med, lo, hi = num(r["km_median"]), num(r["ci_lo"]), num(r["ci_hi"])
            y = ym[m] + GOFF[g]
            hbar(ax, y, lo if math.isfinite(lo) else med, hi if math.isfinite(hi) else 32, GCOL[g], lw=0.8)
            if not math.isfinite(hi):
                dot(ax, 32, y, ">", GCOL[g], ms=3)
            dot(ax, med, y, "o", GCOL[g], GFACE[g], ms=3.4, mew=0.8)
    log2_axis(ax, 0.5, 32)
    ax.set_xlim(0.5, 36)
    ax.set_xlabel("median examples to switch (95% CI)")
    letter(ax, "b")

    def median_of(v):                   # as kstar.median_among_crossers
        v = sorted(v)
        n = len(v)
        return math.nan if not n else (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)

    ax = fig.add_subplot(gs[2])
    switch = {}
    hold_top = RUNGS[-2]                # a switch first seen at the top rung cannot be checked for holding
    for g in list(GRAMMARS) + ["pooled"]:
        allr = [r for m in models for gg in (GRAMMARS if g == "pooled" else [g]) for r in sites[(m, gg)]]
        n0 = len(allr)
        k1 = sorted(float(r["k_star"]) for r in allr if r["censored"] == "False")
        k2 = sorted(float(r["sustained_k"]) for r in allr if r["censored"] == "False" and r["sustained_k"] != "")
        switch[g] = {"n": n0, "switched": len(k1), "first_median_crossers": median_of(k1),
                     "held": len(k2), "hold_median_holders": median_of(k2),
                     "held_by_16": sum(1 for v in k2 if v <= hold_top)}
        if g == "pooled":
            continue
        ax.step([0] + k1 + [32], [0] + [(i + 1) / n0 for i in range(len(k1))] + [len(k1) / n0],
                where="post", color=GCOL[g], lw=1.2)
        k2c = [v for v in k2 if v <= hold_top]
        ax.step([0] + k2c + [hold_top], [0] + [(i + 1) / n0 for i in range(len(k2c))] + [len(k2c) / n0],
                where="post", color=GCOL[g], ls="--", lw=1.2)
    rung_axis(ax)
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", visible=True)
    ax.set_xlabel("worked examples in the prompt")
    ax.set_ylabel("share of initially wrong sites switched")
    letter(ax, "c")
    fig.legend(handles=[handle("dom grammar", "o", GCOL["dom"], GFACE["dom"], ls="-", ms=3.4),
                        handle("blk grammar", "o", GCOL["blk"], GFACE["blk"], ls="-", ms=3.4),
                        handle("single models (a)", None, "0.6", ls="-", lw=0.5),
                        handle("first switch (c)", None, "0.3", ls="-"),
                        handle("switch that holds (c)", None, "0.3", ls="--")],
               loc="outside lower center", ncol=5)
    save(fig, out, "fig5_adaptation", made, book)
    meds = {g: [num(kms[(m, g)]["km_median"]) for m in models] for g in GRAMMARS}
    cens = sum(km.n_censored for km in pooled.values()) / sum(km.n for km in pooled.values())
    captions["fig5_adaptation"] = (
        "**Worked examples switch most initially wrong sites, but the first switch often does not last.** Sites wrong "
        "with zero examples (M < 0), given 0–32 leak-free worked examples in the target lexicon. "
        "(a) Kaplan–Meier share not yet switched (first upward crossing of M = 0, interpolated between "
        "rungs; censored at 32): thick lines pool all models, thin lines are single models. (b) Kaplan–Meier "
        "median per checkpoint with 95% template-cluster bootstrap intervals (frozen export): dom "
        f"{rng_text(meds['dom'])}, blk {rng_text(meds['blk'])} examples. (c) Share switched by k examples, pooled "
        "over models: first switch (solid) against the rung from which the margin stays non-negative through "
        "32 examples (dashed, shown to 16: a switch first seen at 32 cannot be checked). Among sites that "
        f"switch, the median first switch is {switch['pooled']['first_median_crossers']:.2f} examples; among sites "
        f"whose switch holds, it holds from a median of {switch['pooled']['hold_median_holders']:g}. "
        f"{cens:.0%} of initially wrong sites never switch within 32 examples (Table 3).")

    # =========================================================================
    # Figure 6 — generation (Arm B)
    # =========================================================================
    gens = read_csv(csvp("arm_b_generations"))
    inst = sorted({r["model"] for r in gens}, key=model_key)
    gacc: dict[tuple, np.ndarray] = {}
    role_acc: dict[tuple, np.ndarray] = {}
    progs = defaultdict(lambda: defaultdict(int))

    def gbump(store, key, g, i, v):
        if key not in store:
            store[key] = np.zeros(len(tpl[g]))
        store[key][i] += v

    for r in gens:
        m, g = r["model"], r["family"]
        i = tix[g][r["template"]]
        progs[(m, g)]["n"] += 1
        progs[(m, g)][r["bucket"]] += 1
        for o in json.loads(r["site_obs"] or "[]"):
            gbump(gacc, (m, g, "sites"), g, i, 1)
            gbump(gacc, (m, g, "reached"), g, i, bool(o["reached"]))
            gbump(gacc, (m, g, "reverted"), g, i, bool(o["reached"]) and o["outcome"] == "reverted")
            if o["reached"]:
                gbump(role_acc, (g, o["stratum"], "reached"), g, i, 1)
                gbump(role_acc, (g, o["stratum"], "reverted"), g, i, o["outcome"] == "reverted")
    frozen_hurdle = defaultdict(lambda: defaultdict(int))     # summed over lexicons (and models, per role)
    for r in read_csv(csvp("arm_b_hurdle")):
        if r["record_type"] == "hurdle":
            whole = r["stratum"] == "ALL"           # program counts exist on the ALL rows only
            key = (r["model"], r["family"]) if whole else (r["family"], r["stratum"])
            for c in ("n_sites", "n_reached", "n_reverted") + (("n_valid_correct", "n_parse_fail") if whole else ()):
                frozen_hurdle[key][c] += int(r[c])
    for m in inst:
        for g in GRAMMARS:
            mine = {"n_sites": gacc[(m, g, "sites")].sum(), "n_reached": gacc[(m, g, "reached")].sum(),
                    "n_reverted": gacc[(m, g, "reverted")].sum(),
                    "n_valid_correct": progs[(m, g)]["VALID_CORRECT"], "n_parse_fail": progs[(m, g)]["PARSE_FAIL"]}
            if any(int(v) != frozen_hurdle[(m, g)][c] for c, v in mine.items()):
                die(f"Arm B {m} {g}: {mine} != frozen {dict(frozen_hurdle[(m, g)])}")
    for (g, s, what), v in role_acc.items():
        if int(v.sum()) != frozen_hurdle[(g, s)][f"n_{what}"]:
            die(f"Arm B role {g} {s} {what}: {int(v.sum())} != frozen {frozen_hurdle[(g, s)][f'n_{what}']}")
    checks.append(f"Arm B site, reach, reversion, correct-program and parse-failure counts equal the frozen "
                  f"hurdle table for all {len(inst) * len(GRAMMARS)} model x grammar groups and every role")
    hb = {}
    for m in inst:
        for g in GRAMMARS:
            W = draws(tpl[g], f"{g}/figure/arm_b")
            hb[(m, g, "reach")] = ratio(gacc[(m, g, "reached")], gacc[(m, g, "sites")], W)
            hb[(m, g, "revert")] = ratio(gacc[(m, g, "reverted")], gacc[(m, g, "reached")], W)
    strata = [s for s in ("sigil", "keyword", "verb") if any(k[1] == s for k in role_acc)]
    role = {(g, s): ratio(role_acc[(g, s, "reverted")], role_acc[(g, s, "reached")],
                          draws(tpl[g], f"{g}/figure/arm_b"))
            for g in GRAMMARS for s in strata}

    yi, iticks = rows_layout(inst, size_label)
    fig = plt.figure(figsize=(WIDE, 2.75), layout="constrained")
    gs = fig.add_gridspec(1, 3, width_ratios=[1.12, 0.88, 0.85])
    for k, (what, xl) in enumerate((("reach", "reaches the decision site"),
                                    ("revert", "old spelling, given reached"))):
        ax = fig.add_subplot(gs[k])
        style_rows(ax, iticks, labels=k == 0)
        for m in inst:
            for g in GRAMMARS:
                pt, (lo, hi) = hb[(m, g, what)]
                y = yi[m] + GOFF[g]
                hbar(ax, y, lo, hi, GCOL[g], lw=0.8)
                dot(ax, pt, y, "o", GCOL[g], GFACE[g], ms=3.4, mew=0.8)
        ax.set_xlim(0, None)
        ax.set_xlabel(xl)
        letter(ax, "ab"[k])
    ax = fig.add_subplot(gs[2])
    for j, s in enumerate(strata):
        for g in GRAMMARS:
            pt, (lo, hi) = role[(g, s)]
            x = j + (-0.12 if g == "dom" else 0.12)
            vbar(ax, x, lo, hi, GCOL[g])
            dot(ax, x, pt, "o", GCOL[g], GFACE[g], ms=3.8)
    ax.set_xticks(range(len(strata)))
    ax.set_xticklabels(strata)
    ax.set_xlim(-0.5, len(strata) - 0.5)
    ax.set_ylim(0, None)
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", visible=True)
    ax.set_xlabel("role of the reassigned token")
    ax.set_ylabel("old spelling, given reached")
    letter(ax, "c")
    fig.legend(handles=grammar_handles(), loc="outside lower center", ncol=2)
    save(fig, out, "fig6_generation", made, book)
    tot = {k: sum(gacc[(m, g, k)].sum() for m in inst for g in GRAMMARS) for k in ("sites", "reached", "reverted")}
    correct = sum(progs[(m, g)]["VALID_CORRECT"] for m in inst for g in GRAMMARS)
    nprog = sum(progs[(m, g)]["n"] for m in inst for g in GRAMMARS)
    captions["fig6_generation"] = (
        "**In free generation, models rarely reach the decision sites, and revert at a fifth of those they "
        "reach.** Greedy generation by the instruct models from a natural-language request, with the token "
        "table and four worked examples in the prompt. (a) Share of decision sites the program reaches "
        "(the generated text equals the target up to the site, after whitespace normalization). (b) Share of "
        "reached sites where the model writes the familiar spelling. (c) Reversion given reached, by the role "
        "of the reassigned token, pooled over models. 95% template-cluster bootstrap intervals; the two "
        f"rates are reported separately and never multiplied. Overall: reach {int(tot['reached'])}/{int(tot['sites'])} "
        f"({tot['reached'] / tot['sites']:.1%}); reversion given reach {int(tot['reverted'])}/{int(tot['reached'])} "
        f"({tot['reverted'] / tot['reached']:.1%}); correct programs {correct}/{nprog} ({correct / nprog:.1%}) "
        "(Table C3).")

    # =========================================================================
    # Figure 7 — repair (H5)
    # =========================================================================
    h5 = [r for r in read_csv(csvp("h5_budget_outcomes")) if r["record_type"] == "arm"]
    cell = defaultdict(lambda: defaultdict(list))
    for r in h5:
        cell[(r["model"], r["family"], r["lexicon"])][r["arm"]].append(r)
    per = defaultdict(lambda: defaultdict(list))
    wins = defaultdict(lambda: [0, 0])
    for (m, g, lx), arms in cell.items():
        if len(arms["targeted"]) != 1 or len(arms["global"]) != 1 or not arms["random"]:
            die(f"H5 cell {m} {g} {lx}: expected one targeted, one global and at least one random row")
        t = num(arms["targeted"][0]["error_reduction_per_changed_symbol"])
        rnd = {r["seed"]: num(r["error_reduction_per_changed_symbol"]) for r in arms["random"]}
        per[(m, g)]["targeted"].append(t)
        per[(m, g)]["global"].append(num(arms["global"][0]["error_reduction_per_changed_symbol"]))
        per[(m, g)]["random"].append(float(np.mean(list(rnd.values()))))
        for sd, v in rnd.items():
            per[(m, g)][f"seed:{sd}"].append(v)
        wins[(m, g)][0] += t > np.mean(list(rnd.values()))
        wins[(m, g)][1] += 1
    hm = sorted({m for m, _ in per}, key=model_key)
    yh, hticks = rows_layout(hm, size_label)
    pooled_arm = {}
    for arm_ in ("targeted", "random", "global"):
        rs = [r for r in h5 if r["arm"] == arm_]
        pooled_arm[arm_] = {k: sum(int(r[c]) for r in rs) for k, c in
                            (("n", "n_repaired_sites"), ("before", "reversions_before_repaired"),
                             ("after", "reversions_after_repaired"), ("silent", "silent_errors_after_repaired"))}
    fig = plt.figure(figsize=(WIDE, 2.75), layout="constrained")
    gs = fig.add_gridspec(1, 3, width_ratios=[1.12, 0.88, 0.95])
    span, row_axes = [], []
    for k, g in enumerate(GRAMMARS):
        ax = fig.add_subplot(gs[k])
        row_axes.append(ax)
        style_rows(ax, hticks, labels=k == 0)
        ax.axvline(0, color="0.55", lw=0.6, zorder=1)
        for m in hm:
            v = per[(m, g)]
            y = yh[m]
            seeds = [float(np.mean(v[s])) for s in v if s.startswith("seed:")]
            pts = [float(np.mean(v[a_])) for a_ in ("random", "global", "targeted")]
            span += seeds + pts
            hbar(ax, y, min(seeds), max(seeds), "0.75", lw=2.6, z=1)
            dot(ax, pts[0], y, "o", "0.35", "white", ms=3.6, mew=0.8)
            dot(ax, pts[1], y, "s", "0.35", ms=3.2)
            dot(ax, pts[2], y, "o", "black", ms=3.8)
        ax.set_xlabel("reversions removed\nper changed symbol")
        letter(ax, "ab"[k], GLABEL[g])
    for ax in row_axes:
        ax.set_xlim(math.floor(min(span)) - 1, math.ceil(max(span)) + 1)
    ax = fig.add_subplot(gs[2])
    arms_ = ["targeted", "random", "global"]
    x = np.arange(len(arms_))

    def share(a_, k_):
        return pooled_arm[a_][k_] / pooled_arm[a_]["n"]

    ax.bar(x - 0.19, [share(a_, "before") for a_ in arms_], 0.36, color="0.78", label="before repair")
    ax.bar(x + 0.19, [share(a_, "after") for a_ in arms_], 0.36, color="0.3", label="after repair")
    ax.bar(x + 0.19, [share(a_, "silent") for a_ in arms_], 0.36, color="none", edgecolor=SILENT,
           hatch="//////", lw=0, label="after, silent")
    ax.set_xticks(x)
    ax.set_xticklabels(arms_)
    ax.set_ylim(0, max(share(a_, k_) for a_ in arms_ for k_ in ("before", "after")) * 1.4)
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", visible=True)
    ax.set_ylabel("share of repaired sites reverting")
    ax.legend(loc="upper right", fontsize=6.5, borderaxespad=0.1)
    letter(ax, "c")
    fig.legend(handles=[handle("targeted (3 riskiest roles)", "o"),
                        handle("random roles, mean of 5 seeds", "o", "0.35", "white", ms=3.6),
                        Patch(color="0.75", label="range over seeds"),
                        handle("global (every reassigned role)", "s", "0.35", ms=3.2)],
               loc="outside lower center", ncol=4)
    save(fig, out, "fig7_repair", made, book)
    tw = sum(w for w, _ in wins.values())
    tn = sum(n for _, n in wins.values())
    captions["fig7_repair"] = (
        "**Respelling the riskiest roles is no better than respelling random ones (H5 not supported).** "
        "(a, b) The registered H5 metric per instruct model, the mean over the five lexicon cells: reversions "
        "removed per changed symbol after respelling, from the β alphabet, the three roles the base model "
        "rated riskiest (filled), three random roles (open: mean of five seeds; bar: range of the seed means) "
        f"or every reassigned role (squares). Targeted beats the random mean in {tw} of {tn} cells. "
        "The registered metric counts every site of a cell, repaired or not. (c) Pooled over models and "
        "cells: the share of repaired sites that revert before and after repair, and the part of that after "
        "repair which is silent (the old spelling is still a valid program, so no parser flags it). "
        "Reverting repaired sites, before → after (silent after): "
        + "; ".join(f"{a_} {v['before']:,} → {v['after']:,} ({v['silent']:,})" for a_, v in pooled_arm.items())
        + " (Tables 4 and 4b).")

    # =========================================================================
    # Appendix A1 — calibration transfer, only where frozen parameters exist
    # =========================================================================
    params = freeze["calibration"]["params"]
    frozen_pairs = [p for p in pairs if p in params]
    ece = {(r["pair"], r["family"]): num(r["ece"]) for r in h4m
           if r["record_type"] == "metric" and r["predictor"] == "risk"}
    fig, axes = plt.subplots(1, len(frozen_pairs), figsize=(WIDE * 0.62, 2.3), layout="constrained",
                             sharey=True, squeeze=False)
    t_cal = []
    for k, p in enumerate(frozen_pairs):
        a_, b_ = params[p]
        ax = axes[0, k]
        ax.plot([0, 1], [0, 1], color="0.55", lw=0.6, ls=":")
        for g in GRAMMARS:
            rr = by_pair[(p, g)]
            err = max(abs(1 / (1 + math.exp(-(a_ + b_ * float(r["risk"])))) - float(r["calibrated_p"])) for r in rr)
            if err > 1e-4:
                die(f"calibrated_p of {p} {g} is not the frozen Platt fit (max error {err})")
            bins = defaultdict(list)
            for r in rr:
                q = float(r["calibrated_p"])
                bins[min(int(q * 10), 9)].append((q, int(r["label"])))
            pts = [(float(np.mean([q for q, _ in v])), float(np.mean([y for _, y in v])), len(v))
                   for _, v in sorted(bins.items()) if len(v) >= 10]
            ax.plot([q for q, _, _ in pts], [y for _, y, _ in pts], color=GCOL[g], lw=0.9, zorder=2)
            for q, y_, _ in pts:
                dot(ax, q, y_, "o", GCOL[g], GFACE[g], ms=3.2, mew=0.8)
            t_cal.append({"pair": short(p.split("|")[0]) + " / -Instruct", "grammar": g,
                          "frozen Platt (a, b)": f"({a_:.3f}, {b_:.3f})", "sites": len(rr),
                          "ECE": fmt(ece[(p, g)]), "bins shown (n >= 10)": len(pts)})
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.grid(axis="y", visible=True)
        ax.set_xlabel("predicted probability")
        letter(ax, "ab"[k], f"{FAM[S(p.split('|')[0]).family][0]} {size_label(p.split('|')[0])}")
    axes[0, 0].set_ylabel("observed reversion rate")
    axes[0, 0].legend(handles=grammar_handles(), loc="upper left", fontsize=6.5)
    save(fig, out, "figA1_calibration", made, book)
    checks.append(f"calibrated_p equals the frozen Platt fit for the {len(frozen_pairs)} development pairs")
    eces = [ece[(p, g)] for p in frozen_pairs for g in GRAMMARS]
    captions["figA1_calibration"] = (
        "**Calibration of the two pairs with frozen parameters, on held-out mappings.** "
        "Reliability diagrams: the Platt mapping fitted on the development run (frozen) applied to held-out "
        "sites; ten equal-width bins, bins with fewer than 10 sites omitted; dotted line: perfect calibration. "
        f"Expected calibration error {rng_text(eces, 3)}. The other eight pairs had no frozen parameters, so "
        "their calibration figures in the frozen export are in-sample (deviation D12) and are not shown "
        "(Table A1).")

    # =========================================================================
    # Appendix A2 — wording of the rule prompt
    # =========================================================================
    para = [r for r in read_csv(csvp("paraphrase")) if r["record_type"] == "variant"]
    pv = {(r["model"], r["family"], r["condition"]): num(r["reversion_rate"]) for r in para}
    # open markers first, the registered default last and smaller, so ties stay visible
    variants = [("p1", "terse", "s", "white", 3.6), ("p2", "explicit", "^", "white", 3.8),
                ("p0", "default", "o", None, 2.6)]
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 3.9), layout="constrained")
    t_pa = []
    for k, g in enumerate(GRAMMARS):
        ax = axes[k]
        style_rows(ax, mticks, labels=k == 0)
        for m in models:
            vals = [pv[(m, g, v)] for v, *_ in variants if (m, g, v) in pv]
            if not vals:
                continue
            y = ym[m]
            hbar(ax, y, min(vals), max(vals), "0.6", lw=0.8, z=1)
            for v, _, mk, face, ms in variants:
                if (m, g, v) in pv:
                    dot(ax, pv[(m, g, v)], y, mk, "black", face, ms=ms, mew=0.8)
            t_pa.append({"model": short(m), "grammar": g,
                         **{v: fmt(pv.get((m, g, v), math.nan)) for v in ("p0", "p1", "p2")},
                         "range": fmt(max(vals) - min(vals))})
        ax.set_xlabel("reversion rate")
        letter(ax, "ab"[k], GLABEL[g])
    allv = [v for v in pv.values() if math.isfinite(v)]
    for ax in axes:
        ax.set_xlim(math.floor((min(allv) - 0.005) * 40) / 40, math.ceil((max(allv) + 0.005) * 40) / 40)
    fig.legend(handles=[handle(f"{name} wording ({v})", mk, "black", face, ms=ms)
                        for v, name, mk, face, ms in sorted(variants)],
               loc="outside lower center", ncol=3)
    save(fig, out, "figA2_paraphrase", made, book)
    ranges = [num(r["range"]) for r in t_pa]
    n_para = [int(r["n_rows"]) for r in para]
    captions["figA2_paraphrase"] = (
        "**Sensitivity to the wording of the rule prompt.** Reversion rate on the extinction subset "
        f"({min(n_para)}–{max(n_para)} sites per checkpoint and grammar) under three framings of the same "
        "token table: the registered default (p0, filled), a terse one (p1) and a verbose one that names the "
        f"conflict with CSS/JavaScript (p2). Under every wording reversion stays within {rng_text(allv, 3)}; "
        f"the range across wordings per checkpoint is {rng_text(ranges, 3)} (Table A2).")

    # =========================================================================
    # Appendix A3 — reversion by the role of the reassigned token (Arm A)
    # =========================================================================
    strata_a = [s for s in ("sigil", "keyword", "verb")
                if any((m, g, "rule", s, "n") in acc for m in models for g in GRAMMARS)]
    role_a = {(m, g, s): ratio(acc[(m, g, "rule", s, "rev")], acc[(m, g, "rule", s, "n")], W_rev(m, g))
              for m in models for g in GRAMMARS for s in strata_a if (m, g, "rule", s, "n") in acc}
    smark = {"sigil": ("o", None, 3.4), "keyword": ("s", "white", 3.4), "verb": ("^", "0.6", 3.8)}
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 3.9), layout="constrained")
    for k, g in enumerate(GRAMMARS):
        ax = axes[k]
        style_rows(ax, mticks, labels=k == 0)
        for m in models:
            vals = [role_a[(m, g, s)][0] for s in strata_a if (m, g, s) in role_a]
            hbar(ax, ym[m], min(vals), max(vals), "0.7", lw=0.8, z=1)
            for s in strata_a:
                if (m, g, s) in role_a:
                    mk, face, ms = smark[s]
                    dot(ax, role_a[(m, g, s)][0], ym[m], mk, "black", face, ms=ms, mew=0.8)
        ax.set_xlabel("reversion rate with the token table")
        letter(ax, "ab"[k], GLABEL[g])
    allv = [v[0] for v in role_a.values()]
    for ax in axes:
        ax.set_xlim(math.floor((min(allv) - 0.01) * 20) / 20, math.ceil((max(allv) + 0.01) * 20) / 20)
    fig.legend(handles=[handle(s, *smark[s][:1], "black", smark[s][1], ms=smark[s][2]) for s in strata_a],
               loc="outside lower center", ncol=len(strata_a))
    save(fig, out, "figA3_roles", made, book)
    by_role = {(g, s): [role_a[(m, g, s)][0] for m in models if (m, g, s) in role_a]
               for g in GRAMMARS for s in strata_a}
    captions["figA3_roles"] = (
        "**Reversion by the role of the reassigned token (exploratory).** Reversion rate with the token "
        "table, per checkpoint, by the role whose spelling was reassigned: sigils (selector punctuation), "
        "keywords and verbs (method names); (a) dom, (b) blk. Medians across checkpoints: "
        + "; ".join(f"{g} " + ", ".join(f"{s} {np.median(by_role[(g, s)]):.2f}" for s in strata_a) for g in GRAMMARS)
        + ". Roles differ in length and frequency, so this is not a causal comparison (Table A3, with intervals).")

    # =========================================================================
    # Appendix A4 — distribution of the margins
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 3.9), layout="constrained")
    t_m = []
    lim = 0.0
    for k, g in enumerate(GRAMMARS):
        ax = axes[k]
        style_rows(ax, mticks, labels=k == 0)
        ax.axvline(0, color="0.55", lw=0.6, zorder=1)
        for m in models:
            rec = {"model": short(m), "grammar": g}
            for cond, off, col in (("rule", 0.17, "black"), ("norule", -0.17, "0.6")):
                v = np.asarray(margins[(m, g, cond)])
                p5, p25, p50, p75, p95 = np.percentile(v, [5, 25, 50, 75, 95])
                lim = max(lim, abs(p5), abs(p95))
                y = ym[m] + off
                hbar(ax, y, p5, p95, col, lw=0.7, z=2)
                hbar(ax, y, p25, p75, col, lw=3.2, z=3)
                ax.plot(p50, y, marker="|", color="white", ms=3.2, mew=1.0, ls="none", zorder=4)
                rec[f"{cond} median"] = f"{p50:+.2f}"
                rec[f"{cond} IQR"] = f"[{p25:+.2f}, {p75:+.2f}]"
                rec[f"{cond} 5–95%"] = f"[{p5:+.2f}, {p95:+.2f}]"
            t_m.append(rec)
        ax.set_xlabel("margin M (nats): correct − familiar spelling")
        letter(ax, "ab"[k], GLABEL[g])
    for ax in axes:
        ax.set_xlim(-math.ceil(lim), math.ceil(lim))
    fig.legend(handles=[Line2D([], [], color="black", lw=3.2, label="with the token table"),
                        Line2D([], [], color="0.6", lw=3.2, label="without"),
                        Line2D([], [], color="0.3", lw=0.7, label="5th–95th percentile")],
               loc="outside lower center", ncol=3)
    save(fig, out, "figA4_margins", made, book)
    captions["figA4_margins"] = (
        "**Margins are spread widely on both sides of zero.** Distribution of the margin "
        "M = log P(correct spelling) − log P(familiar spelling), scored from the first token where the two "
        "differ, over all decision sites, per checkpoint; M < 0 is a reversion. Thick bar: interquartile range, "
        "white tick: median, thin line: 5th–95th percentile; "
        "black: with the token table, grey: without; (a) dom, (b) blk (Table A4).")

    # --- tokenization: the remapping must not change how much text a site is ---
    fert = [r for r in read_csv(csvp("fertility")) if r["lexicon"] != "identity"]
    heldout_lex = sorted({r["lexicon"] for r in arm})
    t_f = []
    for tok in sorted({r["tokenizer_id"] for r in fert}):
        ms = sorted({m for r in fert if r["tokenizer_id"] == tok for m in r["models"].split("|") if m},
                    key=lambda m: model_key(m) if m in R.REGISTRY else (99, 0, 0))
        fams_ = sorted({FAM[S(m).family][0] for m in ms if m in R.REGISTRY})
        for g in GRAMMARS:
            rs = [r for r in fert if r["tokenizer_id"] == tok and r["family"] == g and r["lexicon"] in heldout_lex]
            if not rs:
                continue
            rf = [num(r["rel_fertility_vs_identity"]) for r in rs]
            rt = [num(r["rel_token_count"]) for r in rs]
            t_f.append({"tokenizer": tok[:12], "families": ", ".join(fams_), "grammar": g, "lexicons": len(rs),
                        "fertility vs identity": rng_text(rf, 3), "token count vs identity": rng_text(rt, 3)})
    if t_f:
        write_table(out, "A5_tokenization", t_f, list(t_f[0]),
                    "Table A5. Tokenization of the remapped programs relative to the standard spellings",
                    "Range over the held-out lexicons. Values near 1 mean the remapping does not make programs "
                    "longer or more fragmented for that tokenizer (frozen export, csv/fertility.csv).")

    # =========================================================================
    # tables
    # =========================================================================
    h4_inst = {p.split("|")[1] for p in pairs}
    t1 = [{"model": short(m), "family": FAM[S(m).family][0], "parameters (B)": f"{S(m).size_b:g}",
           "kind": S(m).kind, "revision": revision[m][:12], "tokenizer": tokenizer[m][:12],
           "H4 pair": "yes" if (m in bases or m in h4_inst) else "",
           "Arm B": "yes" if m in inst else "", "H5": "yes" if m in hm else ""} for m in models]
    write_table(out, "T1_models", t1, list(t1[0]),
                "Table 1. Checkpoints scored on the held-out mappings",
                "Every checkpoint enters Arm A (margins) and the extinction ladder. Full revisions: PROVENANCE.md.")

    dl = defaultdict(dict)
    crit = {}
    for r in h4m:
        if r["record_type"] == "metric" and r["predictor"].startswith("delta_vs_"):
            dl[(r["pair"], r["family"])][r["predictor"][len("delta_vs_"):]] = (
                num(r["delta_auroc"]), num(r["ci_lo"]), num(r["ci_hi"]))
        if r["record_type"] == "criterion":
            crit[(r["pair"], r["family"], r["criterion"][:2])] = r
    risk_row = {(r["pair"], r["family"]): r for r in h4m
                if r["record_type"] == "metric" and r["predictor"] == "risk"}

    def dfmt(d):
        return f"{d[0]:+.3f} [{d[1]:+.3f}, {d[2]:+.3f}]"

    t2 = []
    holm = set()
    for p in pairs:
        for g in GRAMMARS:
            d = dl[(p, g)]
            c1_, c2_ = crit[(p, g, "C1")], crit[(p, g, "C2")]
            holm.update({num(c1_["p_holm"]), num(c2_["p_holm"])})
            t2.append({"pair": short(p.split("|")[0]), "grammar": g, "sites": len(by_pair[(p, g)]),
                       "reversion prevalence": fmt(num(risk_row[(p, g)]["prevalence"])),
                       "AUROC [95% CI]": fci(*auc[(p, g, "risk")]),
                       "AUPRC": fmt(num(risk_row[(p, g)]["auprc"])),
                       "within-lexicon AUROC": fmt(num(risk_row[(p, g)]["within_lexicon_auroc_mean"])),
                       "Δ vs identity (C1)": dfmt(d["identity"]), "Δ vs length (C2)": dfmt(d["length"]),
                       "Δ vs role-level": dfmt(d["terminal_rate"]),
                       "C1": c1_["status"], "C2": c2_["status"]})
    holm_txt = ", ".join(f"{h:.4g}" for h in sorted(holm))
    write_table(out, "T2_h4", t2, list(t2[0]),
                "Table 2. H4 (confirmatory): base-model margins predict instruct-model reversions",
                "AUROC intervals: template-cluster bootstrap computed for the figure (B = 2000, seed 20261002, "
                "the D11 draws). Δ intervals and criteria: the frozen export. Holm-adjusted p for every C1 and C2 "
                f"test: {holm_txt} (the bootstrap floor). C3 is not testable (deviation D1).")

    t3 = []
    for m in models:
        rec = {"model": short(m)}
        for g in GRAMMARS:
            r = kms[(m, g)]
            rec[f"{g} median [95% CI]"] = f"{num(r['km_median']):.2f} [{num(r['ci_lo']):.2f}, {num(r['ci_hi']):.2f}]"
            rec[f"{g} never switched"] = f"{num(r['censoring_rate']):.0%}"
            rec[f"{g} sites"] = r["n"]
        t3.append(rec)
    write_table(out, "T3_adaptation", t3, list(t3[0]),
                "Table 3. Worked examples needed to switch (Kaplan–Meier median of k*, sites wrong at 0 examples)",
                "Frozen export (csv/kstar_survival.csv). 'Never switched' = censored at 32 examples. First switch "
                "against a switch that holds, pooled over models: see Table 3b.")
    t3b = [{"grammar": g, "initially wrong sites": v["n"],
            "switched within 32": f"{v['switched']} ({v['switched'] / v['n']:.1%})",
            "median first switch, among those (examples)": f"{v['first_median_crossers']:.2f}",
            "switch holds through 32": f"{v['held']} ({v['held'] / v['n']:.1%})",
            "median rung it holds from, among those": f"{v['hold_median_holders']:g}",
            "holds from 16 or earlier": f"{v['held_by_16']} ({v['held_by_16'] / v['n']:.1%})"}
           for g, v in switch.items()]
    write_table(out, "T3b_first_vs_lasting_switch", t3b, list(t3b[0]),
                "Table 3b. First switch against a switch that holds (initially wrong sites, all models)",
                "Medians among the sites that switch (or hold) are conditional: they ignore the sites that never do. "
                "Figure 5c shows the unconditional shares.")

    t4 = []
    for m in hm:
        for g in GRAMMARS:
            v = per[(m, g)]
            seeds = [float(np.mean(v[s])) for s in v if s.startswith("seed:")]
            t4.append({"model": short(m), "grammar": g, "targeted": f"{np.mean(v['targeted']):+.2f}",
                       "random (mean of seeds)": f"{np.mean(v['random']):+.2f}",
                       "random (range of seed means)": f"{min(seeds):+.2f} to {max(seeds):+.2f}",
                       "global": f"{np.mean(v['global']):+.2f}",
                       "cells targeted > random": f"{wins[(m, g)][0]}/{wins[(m, g)][1]}"})
    write_table(out, "T4_repair", t4, list(t4[0]),
                "Table 4. H5: reversions removed per changed symbol (mean over the five lexicon cells)",
                f"Targeted beats the random mean in {tw} of {tn} cells: H5 is not supported. The registered "
                "interval test was not implemented (deviation D12). The metric counts every site of a cell.")
    t4b = [{"arm": a_, "repaired sites": v["n"], "reverting before": f"{v['before']} ({v['before'] / v['n']:.1%})",
            "reverting after": f"{v['after']} ({v['after'] / v['n']:.1%})",
            "silent after": f"{v['silent']} ({v['silent'] / v['n']:.1%})"} for a_, v in pooled_arm.items()]
    write_table(out, "T4b_repaired_sites", t4b, list(t4b[0]),
                "Table 4b. What happens at the repaired sites, pooled over models, lexicons and (random) seeds",
                "Silent = the old spelling still yields a valid program, so no parser would flag it (Figure 7c).")

    c1 = []
    for m in models:
        rec = {"model": short(m)}
        for g in GRAMMARS:
            for c, name in (("rule", "with table"), ("norule", "without"),
                            ("norule_lenmatched", "without, length-matched")):
                rec[f"{g} {name}"] = fci(*rate[(m, g, c)])
        c1.append(rec)
    write_table(out, "C1_reversion", c1, list(c1[0]),
                "Table C1. Reversion rate (share of sites with M < 0), pooled over the five held-out lexicons",
                "95% template-cluster bootstrap intervals (the D11 draws; ladder values equal the D11 output).")

    pos = defaultdict(lambda: [0, 0])
    for r in rule_rows:
        if r["record_type"] == "rule_effect" and r["stratum"] == "ALL":
            k_ = (r["model"], r["family"], r["control"])
            pos[k_][1] += 1
            pos[k_][0] += num(r["ci_lo"]) > 0
    c2 = []
    for m in models:
        rec = {"model": short(m)}
        for g in GRAMMARS:
            for c, name in (("norule", "vs without"), ("norule_lenmatched", "vs length-matched")):
                rec[f"{g} {name}"] = fci(*effect[(m, g, c)], sign=True)
                rec[f"{g} {name}: lexicons with CI > 0"] = f"{pos[(m, g, c)][0]}/{pos[(m, g, c)][1]}"
        c2.append(rec)
    npos = sum(v[0] for v in pos.values())
    ntot = sum(v[1] for v in pos.values())
    write_table(out, "C2_rule_effect", c2, list(c2[0]),
                "Table C2. Rule effect: mean of M(with table) − M(control), nats, averaged over the five lexicons",
                "Paired by site; each lexicon weighs the same; 95% template-cluster bootstrap. Per-lexicon "
                "intervals (frozen export, "
                f"csv/rule_effect.csv) lie above zero in {npos} of {ntot} model x grammar x lexicon x control cells.")

    c3 = []
    for m in inst:
        for g in GRAMMARS:
            pg = progs[(m, g)]
            c3.append({"model": short(m), "grammar": g, "reach [95% CI]": fci(*hb[(m, g, "reach")]),
                       "reached / sites": f"{int(gacc[(m, g, 'reached')].sum())}/{int(gacc[(m, g, 'sites')].sum())}",
                       "old spelling given reached [95% CI]": fci(*hb[(m, g, "revert")]),
                       "reverted / reached":
                           f"{int(gacc[(m, g, 'reverted')].sum())}/{int(gacc[(m, g, 'reached')].sum())}",
                       "correct programs": f"{pg['VALID_CORRECT']}/{pg['n']}",
                       "valid but wrong": f"{pg['VALID_WRONG']}/{pg['n']}",
                       "parse failures": f"{pg['PARSE_FAIL']}/{pg['n']}"})
    n_pf = sum(1 for r in gens if r["bucket"] == "PARSE_FAIL")
    n_req = sum(1 for r in gens if r["bucket"] == "PARSE_FAIL"
                and re.search(r"\s+request\s*:", r["extracted"] or "", re.I))
    write_table(out, "C3_generation", c3, list(c3[0]),
                "Table C3. Arm B: free generation by the instruct models",
                "Reach: the generated program equals the target up to the site (normalized whitespace). 95% "
                f"template-cluster bootstrap. {n_req} of the {n_pf} parse failures keep a same-line 'Request:' "
                "continuation in the extracted program, so task accuracy is slightly understated "
                "(heldout_results_explained/08); reach and reversion given reach are prefix-based and unaffected.")
    c3b = [{"grammar": g, "role": s, "old spelling given reached [95% CI]": fci(*role[(g, s)]),
            "reverted / reached": f"{int(role_acc[(g, s, 'reverted')].sum())}/{int(role_acc[(g, s, 'reached')].sum())}"}
           for g in GRAMMARS for s in strata]
    write_table(out, "C3b_generation_by_role", c3b, list(c3b[0]),
                "Table C3b. Arm B: old spelling given reached, by the role of the reassigned token "
                "(all instruct models)",
                "Exploratory. 95% template-cluster bootstrap.")

    c4 = [{"grammar": g, "outcome": {"reversion": "reversion rate", "h4_auroc": "H4 AUROC"}[o], "models": kind,
           "slope per 10x parameters": f"{num(r['slope_per_log10_size']):+.4f}",
           "95% CI": f"[{num(r['ci_lo']):+.4f}, {num(r['ci_hi']):+.4f}]",
           "p (two-sided)": f"< {1 / B:.2g}" if num(r["p_two_sided"]) == 0 else f"{num(r['p_two_sided']):.3f}",
           "Holm p": holm_p(r).replace("= ", "")}
          for (g, o, kind), r in sorted(d11.items(), key=lambda kv: (GRAMMARS.index(kv[0][0]),
                                                                       kv[0][1] != "reversion", kv[0][2]))]
    write_table(out, "C4_scale_D11", c4, list(c4[0]),
                "Table C4. Scale (D10, specified by D11): OLS slopes across the Qwen2.5-Coder ladder, 0.5B–32B",
                "From analysis_addenda/d11_scale/. Template-cluster bootstrap, B = 2000; a p of 0 is reported as "
                "< 1/B. Holm over the six slopes. Sizes are not randomized: associations.")
    write_table(out, "A1_calibration", t_cal, list(t_cal[0]),
                "Table A1. Calibration transfer for the two pairs with frozen parameters",
                "ECE from the frozen export (10 bins). The other eight pairs are in-sample (deviation D12).")
    write_table(out, "A2_paraphrase", t_pa, list(t_pa[0]),
                "Table A2. Reversion rate under three wordings of the rule prompt (extinction subset)")
    t_r = []
    for m in models:
        rec = {"model": short(m)}
        for g in GRAMMARS:
            for s in strata_a:
                if (m, g, s) in role_a:
                    rec[f"{g} {s}"] = fci(*role_a[(m, g, s)])
        t_r.append(rec)
    write_table(out, "A3_roles", t_r, ["model"] + [f"{g} {s}" for g in GRAMMARS for s in strata_a],
                "Table A3. Reversion rate with the token table, by the role of the reassigned token (exploratory)",
                "95% template-cluster bootstrap (the D11 draws).")
    write_table(out, "A4_margins", t_m, list(t_m[0]),
                "Table A4. Distribution of the margin M (nats) over all decision sites")

    # =========================================================================
    # captions, provenance
    # =========================================================================
    order = ["fig2_h4", "fig3_reversion", "fig4_scale", "fig5_adaptation", "fig6_generation", "fig7_repair",
             "figA1_calibration", "figA2_paraphrase", "figA3_roles", "figA4_margins"]
    cap = [f"# Paper figures — `{a.run}`", "",
           "Draft captions. The figures carry no text beyond axes, legends and panel letters; everything a "
           "reader needs to decode them is here, and every number is in `tables/`. Figure 1 of the paper "
           "outline is a diagram of the testbed, not a data figure.", "",
           "Each figure is saved as PDF (vector, for LaTeX), SVG and PNG (300 dpi), 6.5 in wide (full text "
           "width), with 7–8 pt type. `ALL_FIGURES.pdf` holds all of them, one per page, for review.", ""]
    for name in order:
        cap += [f"## `{name}`", "", f"![{name}]({name}.png)", "", captions[name], ""]
    replaces = [("fig2_h4", "`h4_roc_pr_calibration` (ROC and PR curves)"),
                ("fig3_reversion", "`rule_effect_forest`"), ("fig4_scale", "`model_size_tokenizer`"),
                ("fig5_adaptation", "`extinction_trajectories_km`"), ("fig6_generation", "`armb_hurdle_outcomes`"),
                ("fig7_repair", "`h5_benefit_per_symbol`"),
                ("figA1_calibration", "`h4_roc_pr_calibration` (calibration panel; frozen pairs only)"),
                ("figA2_paraphrase", "`paraphrase_sensitivity`"), ("figA3_roles", "`family_mapping_model_stratum`"),
                ("figA4_margins", "`margin_reversion_distributions`"),
                ("table A5", "`fertility_tokenization` (a null check, so a table)"),
                ("—", "`h2_three_scale` (H2 not testable, D1) and `power_curves` (development planning): omitted")]
    cap += ["## What replaces each frozen diagnostic plot", "",
            "The frozen plots in `plots/` stay unchanged as registered outputs.", "",
            "| paper figure | frozen plot it replaces |", "|---|---|"] + [f"| {a_} | {b_} |" for a_, b_ in replaces]
    cap += ["", "## Tables", "", "| file | content |", "|---|---|"]
    for f in sorted(os.listdir(os.path.join(out, "tables"))):
        if f.endswith(".md"):
            with open(os.path.join(out, "tables", f), encoding="utf-8") as fh:
                first = fh.readline().strip("# \n")
            cap.append(f"| [`{f[:-3]}`](tables/{f}) | {first} |")
    with open(os.path.join(out, "CAPTIONS.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(cap) + "\n")

    inputs = ["arm_a_long", "h4_predictions", "h4_metrics_baselines_calibration", "kstar_survival",
              "arm_b_generations", "arm_b_hurdle", "h5_budget_outcomes", "paraphrase", "rule_effect", "fertility"]
    with open(os.path.abspath(__file__), "rb") as fh:
        me = hashlib.sha256(fh.read()).hexdigest()
    prov = [f"# Provenance of the paper figures — `{a.run}`", "",
            f"- generated {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')} by "
            f"`phase3_2/sol/scripts/paper_figures.py` (sha256 `{me[:16]}…`), outside the frozen source set",
            f"- frozen analysis: `{dev_run}/DEV_FREEZE.json`, sha256 `{unlock['freeze_sha256'][:16]}…`; held-out "
            f"unlocked {unlock['unlocked_utc']}",
            f"- figure intervals: template-cluster bootstrap, B = {B}, seed {SEED}, drawn as `scale_analysis.py` "
            "draws them (streams `<grammar>/reversion/<kind>`, `<grammar>/h4_auroc/pair`, `<grammar>/figure/arm_b`)",
            "- grammar families are never pooled; `blk` is a weak family test (deviation D1)",
            "- the frozen diagnostic plots in `plots/` are unchanged", "",
            "## Checks against the frozen export (all passed)", ""] + [f"- {c}" for c in checks]
    prov += ["", "## Checkpoints and the revisions scored", "", "| model | revision |", "|---|---|"]
    prov += [f"| {m} | `{revision[m]}` |" for m in models]
    prov += ["", "## Inputs (sha256)", "", "| file | sha256 |", "|---|---|"]
    prov += [f"| `csv/{n}.csv` | `{CFG.sha256_file(csvp(n))[:16]}…` |" for n in inputs]
    prov += [f"| `analysis_addenda/d11_scale/scale_analysis.csv` | "
             f"`{CFG.sha256_file(os.path.join(rd, 'analysis_addenda', 'd11_scale', 'scale_analysis.csv'))[:16]}…` |"]
    with open(os.path.join(out, "PROVENANCE.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(prov) + "\n")

    book.close()
    for c in checks:
        print(f"check: {c}")
    n_tables = sum(1 for f in os.listdir(os.path.join(out, "tables")) if f.endswith(".csv"))
    print(f"paper figures: {len(made)} figures x (pdf, svg, png), {n_tables} tables -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
