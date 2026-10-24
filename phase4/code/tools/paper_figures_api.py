#!/usr/bin/env python3
"""paper_figures_api.py — figures and tables for Phase 4's served-model run, beside Phase 3.3.

    python3 tools/paper_figures_api.py --run dev-20261023a [--root DIR] [--phase3-3 DIR] [--out DIR]

Phase 4's first development run scored nine models served by the ASU RC API on exactly the cells
of Phase 3.3's held-out run (both grammars x its five held-out lexicons, every site, the same
prompts, settings and seeds). This script puts the two side by side. It reads only exported CSVs:

  * the Phase 4 run's csv/ and the pins it ran with (<root>/model_pins.json);
  * Phase 3.3's held-out run's csv/, restricted to its instruct models: every served model is
    post-trained, so those are the comparable kind.

It draws, one message per figure, with panel letters, every model named on its axis, and no
numbers inside the plots (they are in tables/, CSV + Markdown):

  fig1_reversion    how often each model prefers the familiar spelling, with the table and without
  fig2_rule_effect  how much the table moves the margin, against both controls
  fig3_scale        reversion with the table against total parameters, one line per family ladder
  fig4_adaptation   how many worked examples it takes to switch
  fig5_generation   free generation (Arm B): reaching a site, and reverting there
  figA1_precision   the served models' rounded scores: ties and margins next to zero

Intervals are 95% percentile template-cluster bootstraps with the registered settings (B = 2000,
seed 20261002), drawn exactly as Phase 3.3's paper_figures.py draws them (the same streams), so
Phase 3.3's intervals here equal its own figures'. Before drawing, the script checks every
reversion rate, rule effect, Kaplan-Meier median and Arm B count it recomputes against each run's
own export, and refuses on any mismatch.

STATUS. Phase 4's numbers are DEVELOPMENT results: exploratory, because phase4/PREREGISTRATION.md
was a draft when the run was made. Phase 3.3's are its registered held-out results.

Output: <run>/analysis_addenda/paper_figures/ (nothing is written to csv/, plots/ or reports/).
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
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(CODE))
sys.path.insert(0, CODE)

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import p4  # noqa: E402,F401
from p4.analysis import kstar  # noqa: E402
from p4.governance import registry as R  # noqa: E402
from p4.runtime import config as CFG  # noqa: E402

B, SEED = 2000, 20261002            # the registered bootstrap settings
GRAMMARS = ("dom", "blk")
GLABEL = {"dom": "dom grammar", "blk": "blk grammar"}
GCOL = {"dom": "#000000", "blk": "#8C8C8C"}
GFACE = {"dom": "#000000", "blk": "white"}
GOFF = {"dom": 0.17, "blk": -0.17}  # dom above blk on a shared row
CONDS = ("rule", "norule", "norule_lenmatched")
RUNGS = [0, 1, 2, 4, 8, 16, 32]
WIDE = 6.5
PHASE3_3 = os.path.join(REPO, "phase3_3", "sol_results", "heldout-20261007a")

# registry family -> (display name, Okabe-Ito colour, marker). Phase 3.3's colours are its figures'.
FAM = {
    "qwen2.5-coder": ("Qwen2.5-Coder", "#0072B2", "o"),
    "qwen2.5": ("Qwen2.5", "#56B4E9", "D"),
    "deepseek-coder": ("DeepSeek-Coder", "#D55E00", "s"),
    "llama-3.2": ("Llama-3.2", "#009E73", "^"),
    "olmo-3": ("OLMo 3", "#E69F00", "P"),
    "qwen3-coder": ("Qwen3-Coder", "#CC79A7", "h"),
    "qwen3.5": ("Qwen3.5", "#000000", "*"),
    "gemma-4": ("Gemma 4", "#F0E442", "v"),
    "deepseek-v4": ("DeepSeek-V4.1", "#D55E00", "X"),
}
FAM_ORDER = list(FAM)
SERVED_NAMES = {
    "olmo3-7b-instruct": "OLMo 3 7B Instruct",
    "olmo3-32b-instruct": "OLMo 3 32B Instruct",
    "olmo3-32b-think": "OLMo 3 32B Think",
    "qwen3-coder-30b-a3b-instruct": "Qwen3-Coder 30B-A3B Instruct",
    "qwen35-27b": "Qwen3.5 27B",
    "qwen35-122b-a10b": "Qwen3.5 122B-A10B",
    "qwen35-397b-a17b": "Qwen3.5 397B-A17B",
    "gemma4-31b-it": "Gemma 4 31B",
    "deepseek-v4-1-flash": "DeepSeek-V4.1-Flash",
}

plt.rcParams.update({
    "font.size": 7.5, "axes.titlesize": 7.5, "axes.labelsize": 7.5, "xtick.labelsize": 7,
    "ytick.labelsize": 7, "legend.fontsize": 7, "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6, "axes.grid": True,
    "grid.color": "0.9", "grid.linewidth": 0.5, "axes.axisbelow": True, "savefig.dpi": 300,
    "pdf.fonttype": 42, "svg.fonttype": "none", "legend.frameon": False,
})


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def die(msg: str):
    raise SystemExit(f"REFUSED: {msg}")


def read_csv(path: str, keep=None) -> list[dict]:
    if not os.path.exists(path):
        die(f"{path} does not exist; run the export first")
    with open(path, encoding="utf-8") as fh:
        rows = csv.DictReader(fh)
        return [r for r in rows if keep is None or keep(r)]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return math.nan


def S(m: str):
    return R.spec(m)


def served(m: str) -> bool:
    return R.is_api(m)


def name(m: str) -> str:
    s = S(m)
    if s.serving == "api":
        return SERVED_NAMES.get(s.api_model, s.api_model)
    return f"{FAM[s.family][0]} {s.size_b:g}B" + (" Instruct" if s.kind == "instruct" else " base")


def model_key(m: str):
    s = S(m)
    return (served(m), FAM_ORDER.index(s.family), s.size_b, s.api_model)


def fmt(x, d=3) -> str:
    return "" if x is None or not math.isfinite(x) else f"{x:.{d}f}"


def fci(pt, lohi, d=3, sign=False) -> str:
    f = "{:+.%df}" % d if sign else "{:.%df}" % d
    if not math.isfinite(pt):
        return ""
    lo, hi = lohi
    return f"{f.format(pt)} [{f.format(lo) if math.isfinite(lo) else '–'}, {f.format(hi) if math.isfinite(hi) else '–'}]"


def rng_text(vals, d=2) -> str:
    v = [x for x in vals if math.isfinite(x)]
    return f"{min(v):.{d}f}–{max(v):.{d}f}" if v else "–"


# ---------------------------------------------------------------------------
# bootstrap (the draws of Phase 3.3's paper_figures.py and scale_analysis.py)
# ---------------------------------------------------------------------------

_DRAWS: dict[tuple, np.ndarray] = {}


def draws(templates: list[str], key: str) -> np.ndarray:
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


# ---------------------------------------------------------------------------
# layout
# ---------------------------------------------------------------------------

def rows_layout(items):
    """Rows top to bottom: a bold header per phase, then the models by family and size."""
    entries, prev = [], None
    for m in sorted(items, key=model_key):
        head = "Phase 4: served by the ASU RC API" if served(m) else "Phase 3.3: run on Sol, fp32 head"
        if head != prev:
            prev = head
            entries.append((head, None))
        entries.append((name(m), m))
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
    ax.grid(axis="y", visible=False)
    heads = [y for y, _, h in ticks if h]
    for k, top in enumerate(heads):
        bottom = (heads[k + 1] + 1) if k + 1 < len(heads) else 0
        if k % 2:
            ax.axhspan(bottom - 0.5, top + 0.5, color="0.955", lw=0, zorder=0)


def letter(ax, ch, desc=""):
    ax.set_title(ch, loc="left", fontweight="bold", fontsize=9)
    if desc:
        ax.set_title(desc, loc="center")


def hbar(ax, y, lo, hi, color, lw=1.0, z=2):
    if math.isfinite(lo) and math.isfinite(hi):
        ax.plot([lo, hi], [y, y], color=color, lw=lw, solid_capstyle="butt", zorder=z)


def dot(ax, x, y, marker="o", color="black", face=None, ms=3.8, mew=0.9, z=3, edge=None):
    ax.plot(x, y, marker=marker, color=color, mfc=color if face is None else face,
            mec=edge or color, mew=mew, ms=ms, ls="none", zorder=z)


def handle(label, marker="o", color="black", face=None, ls="none", ms=4, lw=1.0, edge=None):
    return Line2D([], [], marker=marker, color=color, mfc=color if face is None else face,
                  mec=edge or color, ls=ls, ms=ms, lw=lw, label=label)


def grammar_handles():
    return [handle("dom grammar", color=GCOL["dom"], face=GFACE["dom"]),
            handle("blk grammar", color=GCOL["blk"], face=GFACE["blk"])]


def edge_of(fam):
    return "black" if FAM[fam][1] == "#F0E442" else None


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


def save(fig, out, name_, made, book):
    for ext in ("pdf", "png", "svg"):
        fig.savefig(os.path.join(out, f"{name_}.{ext}"))
    book.savefig(fig)
    plt.close(fig)
    made.append(name_)


def write_table(out, name_, rows, cols, title, note=""):
    with open(os.path.join(out, "tables", f"{name_}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    md = [f"# {title}", ""] + ([note, ""] if note else [])
    md += ["| " + " | ".join(c.replace("|", "\\|") for c in cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    md += ["| " + " | ".join(str(r.get(c, "")).replace("|", "\\|") for c in cols) + " |" for r in rows]
    with open(os.path.join(out, "tables", f"{name_}.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")


# ---------------------------------------------------------------------------
# reading one run
# ---------------------------------------------------------------------------

class Run:
    """The exported tables of one run, for the models kept."""

    def __init__(self, rd: str, keep_model, label: str):
        self.rd, self.label = rd, label
        self.inputs = {}
        fields = ("model", "family", "lexicon", "template", "site_id", "stratum", "condition",
                  "m_seq", "tie", "n_tok_correct", "n_tok_competitor", "model_revision", "tokenizer_id")
        self.arm = [{k: r[k] for k in fields} for r in self.csv("arm_a_long")
                    if r["status"] == "ok" and keep_model(r["model"])]
        self.models = sorted({r["model"] for r in self.arm}, key=model_key)
        self.rule_effect = [r for r in self.csv("rule_effect") if keep_model(r["model"])]
        self.kstar = [r for r in self.csv("kstar_survival") if keep_model(r.get("model", ""))]
        self.gens = [r for r in self.csv("arm_b_generations") if keep_model(r["model"])]
        self.hurdle = [r for r in self.csv("arm_b_hurdle")
                       if r.get("record_type") == "hurdle" and keep_model(r["model"])]
        self.ladder = [{k: r[k] for k in ("model", "family", "template", "rung", "m_seq")}
                       for r in self.csv("extinction_rung_long")
                       if r["status"] == "ok" and r["kind"] == "ladder" and keep_model(r["model"])]

    def csv(self, name_):
        p = os.path.join(self.rd, "csv", f"{name_}.csv")
        self.inputs[f"{self.label}: csv/{name_}.csv"] = sha256_file(p) if os.path.exists(p) else "missing"
        return read_csv(p)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--root", default=None, help="results root (default: P4_RESULTS_ROOT)")
    ap.add_argument("--phase3-3", default=PHASE3_3, help="Phase 3.3's held-out run folder")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    root = a.root or CFG.results_root()
    rd = os.path.join(root, a.run)
    out = a.out or os.path.join(rd, "analysis_addenda", "paper_figures")
    os.makedirs(os.path.join(out, "tables"), exist_ok=True)
    made, checks, captions = [], [], {}
    book = PdfPages(os.path.join(out, "ALL_FIGURES.pdf"))

    p4run = Run(rd, served, "Phase 4")
    p33 = Run(a.phase3_3, lambda m: m in R.REGISTRY and S(m).kind == "instruct" and not served(m), "Phase 3.3")
    if not p4run.models:
        die(f"no served model has Arm A rows in {rd}")
    cfg4 = json.load(open(os.path.join(rd, "manifests", "run_config.json")))["config"]
    pp = os.path.join(root, "model_pins.json")
    pins = json.load(open(pp))["pins"] if os.path.exists(pp) else {}
    runs = (p33, p4run)
    models = sorted(p33.models + p4run.models, key=model_key)

    # the same cells: both runs' sites per grammar must be identical
    for g in GRAMMARS:
        s3 = {r["site_id"] for r in p33.arm if r["family"] == g}
        s4 = {r["site_id"] for r in p4run.arm if r["family"] == g}
        if s3 != s4:
            die(f"{g}: the two runs scored different sites ({len(s3 ^ s4)} differ)")
    tpl = {g: sorted({r["template"] for r in p4run.arm if r["family"] == g}) for g in GRAMMARS}
    tix = {g: {t: i for i, t in enumerate(tpl[g])} for g in GRAMMARS}
    lexicons = {g: sorted({r["lexicon"] for r in p4run.arm if r["family"] == g}) for g in GRAMMARS}
    n_sites = {g: len({r["site_id"] for r in p4run.arm if r["family"] == g}) for g in GRAMMARS}
    checks.append(f"both runs scored the same {n_sites['dom']} dom and {n_sites['blk']} blk sites, on "
                  f"{len(tpl['dom'])} and {len(tpl['blk'])} templates and the lexicons "
                  f"{', '.join(lexicons['dom'])}")

    # =========================================================================
    # Arm A: per-template counts for every model x grammar x condition
    # =========================================================================
    site = defaultdict(dict)
    where, stratum_of, lexicon_of, single = {}, {}, {}, {}
    for run in runs:
        for r in run.arm:
            site[(r["model"], r["family"], r["site_id"])][r["condition"]] = float(r["m_seq"])
            where[(r["family"], r["site_id"])] = tix[r["family"]][r["template"]]
            stratum_of[(r["family"], r["site_id"])] = r["stratum"]
            lexicon_of[(r["family"], r["site_id"])] = r["lexicon"]
            single[(r["model"], r["family"], r["site_id"], r["condition"])] = (
                r["n_tok_correct"] == "1" and r["n_tok_competitor"] == "1")
    acc: dict[tuple, np.ndarray] = {}

    def bump(key, g, i, v):
        if key not in acc:
            acc[key] = np.zeros(len(tpl[g]))
        acc[key][i] += v

    for (m, g, sid), c in site.items():
        i = where[(g, sid)]
        for cond, v in c.items():
            bump((m, g, cond, "n"), g, i, 1)
            bump((m, g, cond, "rev"), g, i, v < 0)
            bump((m, g, cond, "tie"), g, i, v == 0)
            bump((m, g, cond, "near"), g, i, abs(v) < 0.125)
        for ctl in ("norule", "norule_lenmatched"):
            if "rule" in c and ctl in c:
                lx = lexicon_of[(g, sid)]
                bump((m, g, ctl, lx, "eff"), g, i, c["rule"] - c[ctl])
                bump((m, g, ctl, lx, "pairs"), g, i, 1)

    def W_rev(g):
        return draws(tpl[g], f"{g}/reversion/instruct")       # Phase 3.3's stream for instruct models

    rate = {(m, g, c): ratio(acc[(m, g, c, "rev")], acc[(m, g, c, "n")], W_rev(g))
            for m in models for g in GRAMMARS for c in CONDS}

    def lexicon_mean(m, g, ctl):
        W = W_rev(g)
        pts, boots = [], []
        for lx in lexicons[g]:
            e, p = acc[(m, g, ctl, lx, "eff")], acc[(m, g, ctl, lx, "pairs")]
            pts.append(e.sum() / p.sum())
            with np.errstate(invalid="ignore", divide="ignore"):
                boots.append((W @ e) / (W @ p))
        return float(np.mean(pts)), interval(np.mean(boots, axis=0))

    effect = {(m, g, c): lexicon_mean(m, g, c)
              for m in models for g in GRAMMARS for c in ("norule", "norule_lenmatched")}

    # checks against each run's own export
    for run in runs:
        n_re = n_rv = 0
        rev_cell = defaultdict(lambda: [0, 0])
        for (m, g, sid), c in site.items():
            if m in run.models and "rule" in c:
                for st in ("ALL", stratum_of[(g, sid)]):
                    cell_ = rev_cell[(m, g, lexicon_of[(g, sid)], st)]
                    cell_[0] += 1
                    cell_[1] += c["rule"] < 0
        for r in run.rule_effect:
            if r["record_type"] == "rule_effect" and r["stratum"] == "ALL":
                key = (r["model"], r["family"], r["control"], r["lexicon"])
                mine = acc[key + ("eff",)].sum() / acc[key + ("pairs",)].sum()
                if abs(mine - num(r["mean_rule_effect"])) > 1e-5:
                    die(f"{run.label} rule effect {key}: {mine:.6f} != exported {r['mean_rule_effect']}")
                n_re += 1
            if r["record_type"] == "reversion" and r["condition"] == "rule":
                n_, k_ = rev_cell[(r["model"], r["family"], r["lexicon"], r["stratum"])]
                if n_ != int(r["n_rows"]) or abs(k_ / n_ - num(r["reversion_rate"])) > 1e-5:
                    die(f"{run.label} reversion {r['model']} {r['family']} {r['lexicon']} {r['stratum']}: "
                        f"{k_}/{n_} != exported {r['reversion_rate']} of {r['n_rows']}")
                n_rv += 1
        if not n_re or not n_rv:
            die(f"{run.label}: no rule-effect or reversion records to check against")
        checks.append(f"{run.label}: the per-lexicon mean rule effect equals the export in all {n_re} "
                      f"model x grammar x lexicon x control cells, and the reversion counts and rates in "
                      f"all {n_rv} model x grammar x lexicon x role cells")

    # =========================================================================
    # Table 1: the models
    # =========================================================================
    t1 = []
    for m in models:
        s = S(m)
        rev = next(r["model_revision"] for run in runs for r in run.arm if r["model"] == m)
        tok = next(r["tokenizer_id"] for run in runs for r in run.arm if r["model"] == m)
        t1.append({"phase": "4" if served(m) else "3.3", "model": name(m), "id": m,
                   "family": FAM[s.family][0], "parameters_B": f"{s.size_b:g}",
                   "active_B": "" if s.active_b is None else f"{s.active_b:g}",
                   "served_precision": s.quantization if served(m) else "bf16 + fp32 head",
                   "revision_or_deployment": rev, "tokenizer_id": tok,
                   "pinned_utc": pins.get(m, {}).get("pinned_utc", "") if served(m) else ""})
    write_table(out, "T1_models", t1, ["phase", "model", "id", "family", "parameters_B", "active_B",
                                       "served_precision", "revision_or_deployment", "tokenizer_id",
                                       "pinned_utc"],
                "Table 1. The models",
                "Phase 3.3: its 10 instruct models (base models are not comparable: every served model is "
                "post-trained). Phase 4: the nine served models, pinned to the deployment that answered. "
                "Sizes are total parameters; active_B is a mixture of experts' active parameters.")

    # =========================================================================
    # Figure 1: reversion with and without the table
    # =========================================================================
    yp, ticks = rows_layout(models)
    h = 0.17 * len(ticks) + 1.0
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, h), layout="constrained", sharey=True)
    for k, g in enumerate(GRAMMARS):
        ax = axes[k]
        style_rows(ax, ticks, labels=k == 0)
        for m in models:
            y = yp[m]
            pt, (lo, hi) = rate[(m, g, "rule")]
            hbar(ax, y, lo, hi, "black")
            dot(ax, pt, y, "o", "black", ms=3.8)
            dot(ax, rate[(m, g, "norule")][0], y, "o", "0.45", "white", ms=3.6, mew=0.8)
            dot(ax, rate[(m, g, "norule_lenmatched")][0], y, "|", "0.45", ms=5, mew=1.0)
        ax.set_xlim(0, 1)
        ax.grid(axis="x", visible=True)
        ax.set_xlabel("reversion (share of sites)")
        letter(ax, "ab"[k], GLABEL[g])
    fig.legend(handles=[handle("with the token table (95% CI)", ls="-"),
                        handle("without the table", "o", "0.45", "white", ms=3.6),
                        handle("length-matched control", "|", "0.45", ms=5)],
               loc="outside lower center", ncol=3)
    save(fig, out, "fig1_reversion", made, book)
    t2 = []
    for m in models:
        for g in GRAMMARS:
            for c in CONDS:
                pt, ci = rate[(m, g, c)]
                t2.append({"phase": "4" if served(m) else "3.3", "model": name(m), "grammar": g,
                           "condition": c, "sites": int(acc[(m, g, c, "n")].sum()),
                           "reverted": int(acc[(m, g, c, "rev")].sum()),
                           "ties": int(acc[(m, g, c, "tie")].sum()),
                           "reversion_rate": fmt(pt), "ci95": fci(pt, ci)})
    write_table(out, "T2_reversion", t2, ["phase", "model", "grammar", "condition", "sites", "reverted",
                                          "ties", "reversion_rate", "ci95"],
                "Table 2. Reversion: the share of sites where the familiar spelling scores higher (M < 0)",
                "A tie (M = 0) is not a reversion, as in Phase 3.3. 95% template-cluster bootstrap, B = 2000.")
    r4 = {g: [rate[(m, g, "rule")][0] for m in p4run.models] for g in GRAMMARS}
    r3 = {g: [rate[(m, g, "rule")][0] for m in p33.models] for g in GRAMMARS}
    captions["fig1_reversion"] = (
        "**The served models, like Phase 3.3's, often prefer the familiar spelling even with the token table "
        "in the prompt.** Each row is a model; Phase 3.3's instruct models (top) and Phase 4's served models "
        "(bottom) were scored on the same sites with the same prompts. (a) dom, (b) blk grammar. Filled "
        "circles: share of decision sites where the familiar spelling scores higher than the correct one "
        "(M < 0) with the token table, with 95% template-cluster bootstrap intervals; open circles: without "
        "the table; bars: the length-matched control. With the table, Phase 4: dom "
        f"{rng_text(r4['dom'])}, blk {rng_text(r4['blk'])}; Phase 3.3: dom {rng_text(r3['dom'])}, blk "
        f"{rng_text(r3['blk'])} (Table 2). Phase 4's numbers are development results (exploratory).")

    # =========================================================================
    # Figure 2: the rule effect
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, h), layout="constrained", sharey=True)
    lo_x = min(min(effect[(m, g, c)][1][0] for m in models for g in GRAMMARS for c in ("norule", "norule_lenmatched")), 0)
    hi_x = max(effect[(m, g, c)][1][1] for m in models for g in GRAMMARS for c in ("norule", "norule_lenmatched"))
    for k, g in enumerate(GRAMMARS):
        ax = axes[k]
        style_rows(ax, ticks, labels=k == 0)
        ax.axvline(0, color="0.55", lw=0.6, ls=":", zorder=1)
        for m in models:
            y = yp[m]
            for ctl, off, face in (("norule", 0.17, "black"), ("norule_lenmatched", -0.17, "white")):
                pt, (lo, hi) = effect[(m, g, ctl)]
                hbar(ax, y + off, lo, hi, "black", lw=0.8)
                dot(ax, pt, y + off, "o", "black", face, ms=3.4, mew=0.8)
        ax.set_xlim(lo_x - 0.2, hi_x + 0.2)
        ax.grid(axis="x", visible=True)
        ax.set_xlabel("change in margin from the table (nats)")
        letter(ax, "ab"[k], GLABEL[g])
    fig.legend(handles=[handle("table − no table (95% CI)", "o", "black", ls="-", ms=3.4),
                        handle("table − length-matched control", "o", "black", "white", ls="-", ms=3.4)],
               loc="outside lower center", ncol=2)
    save(fig, out, "fig2_rule_effect", made, book)
    t3 = []
    for m in models:
        for g in GRAMMARS:
            for ctl in ("norule", "norule_lenmatched"):
                pt, ci = effect[(m, g, ctl)]
                t3.append({"phase": "4" if served(m) else "3.3", "model": name(m), "grammar": g,
                           "control": ctl, "mean_rule_effect": fmt(pt), "ci95": fci(pt, ci, sign=True),
                           "excludes_zero": str(ci[0] > 0 or ci[1] < 0)})
    write_table(out, "T3_rule_effect", t3, ["phase", "model", "grammar", "control", "mean_rule_effect",
                                            "ci95", "excludes_zero"],
                "Table 3. Rule effect: M(table) − M(control), the mean over lexicons of each lexicon's mean",
                "Positive = the table moves the margin toward the correct spelling. 95% template-cluster "
                "bootstrap (the same resample applied to every lexicon), B = 2000.")
    e4 = {g: [effect[(m, g, "norule")][0] for m in p4run.models] for g in GRAMMARS}
    pos4 = sum(1 for m in p4run.models for g in GRAMMARS if effect[(m, g, "norule")][1][0] > 0)
    captions["fig2_rule_effect"] = (
        "**The token table moves every served model's margins toward the correct spelling, but not far "
        "enough to remove reversion.** Mean change in the margin M when the token table is added, (a) dom, "
        "(b) blk: against the prompt without the table (filled) and against a length-matched control (open), "
        "with 95% template-cluster bootstrap intervals. Phase 4, against no table: dom "
        f"{rng_text(e4['dom'])}, blk {rng_text(e4['blk'])} nats; the interval excludes zero (positive) in "
        f"{pos4} of {2 * len(p4run.models)} served model × grammar groups (Table 3).")

    # =========================================================================
    # Figure 3: scale
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 2.9), layout="constrained", sharey=True)
    ladders = defaultdict(list)
    for m in models:
        s = S(m)
        lad = (s.family, "think" in (s.api_model or ""))
        ladders[lad].append(m)
    for k, g in enumerate(GRAMMARS):
        ax = axes[k]
        for (fam, think), ms in ladders.items():
            ms = sorted(ms, key=lambda m: S(m).size_b)
            col, mk = FAM[fam][1], ("d" if think else FAM[fam][2])     # OLMo 3 Think: a thin diamond
            xs = [S(m).size_b for m in ms]
            ys = [rate[(m, g, "rule")][0] for m in ms]
            if len(ms) > 1:
                ax.plot(xs, ys, color=col if col != "#F0E442" else "#B8AC00", lw=0.9,
                        ls="--" if think else "-", zorder=2)
            for m, x, y_ in zip(ms, xs, ys):
                lo, hi = rate[(m, g, "rule")][1]
                ax.plot([x, x], [lo, hi], color="0.6", lw=0.6, zorder=1)
                moe = S(m).active_b is not None
                dot(ax, x, y_, mk, col, "white" if moe else col, ms=5 if mk == "*" else 4, mew=0.9,
                    edge=edge_of(fam))
        ax.set_xscale("log")
        ax.set_xlim(0.35, 1200)
        ax.set_xticks([0.5, 1, 3, 10, 30, 100, 300, 1000])
        ax.set_xticklabels(["0.5", "1", "3", "10", "30", "100", "300", "1000"])
        ax.minorticks_off()
        ax.set_ylim(0, 1)
        ax.set_xlabel("total parameters (billions, log scale)")
        if k == 0:
            ax.set_ylabel("reversion with the table")
        letter(ax, "ab"[k], GLABEL[g])
    fams = [f for f in FAM_ORDER if any(S(m).family == f for m in models)]
    hs = [handle(FAM[f][0], FAM[f][2], FAM[f][1], ms=5 if FAM[f][2] == "*" else 4, edge=edge_of(f))
          for f in fams]
    hs += [handle("OLMo 3 32B Think", "d", FAM["olmo-3"][1], ms=4),
           handle("mixture of experts (open)", "o", "0.3", "white", ms=4)]
    fig.legend(handles=hs, loc="outside lower center", ncol=4)
    save(fig, out, "fig3_scale", made, book)
    captions["fig3_scale"] = (
        "**Size alone does not remove reversion.** Reversion with the token table against total parameters "
        "(log scale), (a) dom, (b) blk; every instruct model of both phases, coloured by family, with 95% "
        "template-cluster bootstrap intervals (grey). Lines join one family's sizes: Qwen2.5-Coder "
        "0.5–32B and Qwen2.5 72B (Phase 3.3), Qwen3.5 27B, 122B and 397B and OLMo 3 7B and 32B (Phase 4). "
        "Open markers: mixtures of experts, plotted at total parameters (active parameters are in Table 1). "
        "Sizes are not randomized; these are associations, and Phase 4's served models also differ in "
        "precision (Table 1).")

    # =========================================================================
    # Figure 4: adaptation (worked examples)
    # =========================================================================
    def te(rs):
        return ([float(r["top_rung"]) if r["censored"] == "True" else float(r["k_star"]) for r in rs],
                [r["censored"] == "False" for r in rs])

    sites_k, kms = defaultdict(list), {}
    for run in runs:
        for r in run.kstar:
            if r["record_type"] == "site" and r["status"] == "ok" and r["already_correct"] == "False":
                sites_k[(r["model"], r["family"])].append(r)
            if r["record_type"] == "km_summary" and r["population"] == "INITIALLY_WRONG":
                kms[(r["model"], r["family"])] = r
    for key, fr in kms.items():
        km = kstar.kaplan_meier(*te(sites_k[key]), population="INITIALLY_WRONG")
        ref = num(fr["km_median"])
        if not ((km.median is None and not math.isfinite(ref)) or
                (km.median is not None and abs(km.median - ref) < 1e-4)):
            die(f"KM median {key}: {km.median} != exported {fr['km_median']}")
    checks.append(f"Kaplan-Meier medians recomputed from the site rows equal each run's export in all "
                  f"{len(kms)} model x grammar groups")
    fig = plt.figure(figsize=(WIDE, max(h, 3.2)), layout="constrained")
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.25])
    ax = fig.add_subplot(gs[0])
    for g in GRAMMARS:
        for run, ls in ((p33, ":"), (p4run, "-")):
            allr = [r for m in run.models for r in sites_k[(m, g)]]
            km = kstar.kaplan_meier(*te(allr), population="INITIALLY_WRONG")
            ax.step([t for t, _ in km.curve] + [32], [s for _, s in km.curve] + [km.curve[-1][1]],
                    where="post", color=GCOL[g], lw=1.4, ls=ls)
    rung_axis(ax)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("worked examples in the prompt")
    ax.set_ylabel("share of initially wrong sites\nnot yet switched")
    letter(ax, "a")
    ax = fig.add_subplot(gs[1])
    style_rows(ax, ticks)
    clipped = []
    for m in models:
        for g in GRAMMARS:
            r = kms.get((m, g))
            if r is None:
                continue
            if 0 <= num(r["km_median"]) < 0.5:
                clipped.append(f"{name(m)} {g}")
            med, lo, hi = num(r["km_median"]), num(r["ci_lo"]), num(r["ci_hi"])
            y = yp[m] + GOFF[g]
            if math.isfinite(med):
                hbar(ax, y, lo if math.isfinite(lo) else med, hi if math.isfinite(hi) else 32, GCOL[g], lw=0.8)
                if not math.isfinite(hi):
                    dot(ax, 32, y, ">", GCOL[g], ms=3)
                dot(ax, max(med, 0.5), y, "o", GCOL[g], GFACE[g], ms=3.4, mew=0.8)
            else:
                dot(ax, 32, y, ">", GCOL[g], GFACE[g], ms=3.4, mew=0.8)
    log2_axis(ax, 0.5, 32)
    ax.set_xlim(0.45, 36)
    ax.grid(axis="x", visible=True)
    ax.set_xlabel("median examples to switch (95% CI)")
    letter(ax, "b")
    fig.legend(handles=grammar_handles() + [handle("Phase 3.3, pooled (a)", None, "0.3", ls=":"),
                                            handle("Phase 4, pooled (a)", None, "0.3", ls="-")],
               loc="outside lower center", ncol=4)
    save(fig, out, "fig4_adaptation", made, book)
    t4 = []
    for m in models:
        for g in GRAMMARS:
            r = kms.get((m, g), {})
            t4.append({"phase": "4" if served(m) else "3.3", "model": name(m), "grammar": g,
                       "initially_wrong": r.get("n", ""), "switched": r.get("n_events", ""),
                       "never_switched": r.get("n_censored", ""), "km_median": r.get("km_median", ""),
                       "ci95": f"[{r.get('ci_lo', '')}, {r.get('ci_hi', '')}]" if r else ""})
    write_table(out, "T4_adaptation", t4, ["phase", "model", "grammar", "initially_wrong", "switched",
                                           "never_switched", "km_median", "ci95"],
                "Table 4. Worked examples to switch: Kaplan-Meier median over sites wrong with none",
                "Exported by each run (csv/kstar_survival.csv). 'Never switched' = censored at 32 examples.")
    med4 = {g: [num(kms[(m, g)]["km_median"]) for m in p4run.models if (m, g) in kms] for g in GRAMMARS}
    med3 = {g: [num(kms[(m, g)]["km_median"]) for m in p33.models if (m, g) in kms] for g in GRAMMARS}
    captions["fig4_adaptation"] = (
        "**Worked examples switch the served models' wrong sites as they switched Phase 3.3's.** Sites wrong "
        "with zero examples (M < 0), given 0–32 leak-free worked examples in the target lexicon. (a) "
        "Kaplan–Meier share not yet switched, pooled over each phase's models (dotted: Phase 3.3; solid: "
        "Phase 4); black dom, grey blk. (b) Kaplan–Meier median per model with 95% template-cluster bootstrap "
        f"intervals (each run's export). Phase 4 medians: dom {rng_text(med4['dom'])}, blk {rng_text(med4['blk'])} "
        f"examples; Phase 3.3: dom {rng_text(med3['dom'])}, blk {rng_text(med3['blk'])} (Table 4)."
        + (f" Medians below 0.5 are drawn at 0.5 ({', '.join(clipped)})." if clipped else "")
        + " A rounding fault in the Kaplan–Meier code, inherited from Phase 3.3, can move a median to the "
          "next switch when the survival curve is exactly 1/2 there (explanations/phase4/"
          "api_models_results_explained/08, §6).")

    # =========================================================================
    # Figure 5: generation (Arm B)
    # =========================================================================
    gacc: dict[tuple, np.ndarray] = {}
    progs = defaultdict(lambda: defaultdict(int))

    def gbump(key, g, i, v):
        if key not in gacc:
            gacc[key] = np.zeros(len(tpl[g]))
        gacc[key][i] += v

    for run in runs:
        for r in run.gens:
            m, g = r["model"], r["family"]
            i = tix[g][r["template"]]
            progs[(m, g)]["n"] += 1
            progs[(m, g)][r["bucket"]] += 1
            progs[(m, g)]["empty"] += (r["raw_output"] or "").strip() == ""
            for o in json.loads(r["site_obs"] or "[]"):
                gbump((m, g, "sites"), g, i, 1)
                gbump((m, g, "reached"), g, i, bool(o["reached"]))
                gbump((m, g, "reverted"), g, i, bool(o["reached"]) and o["outcome"] == "reverted")
    gen_models = sorted({m for (m, _g) in progs}, key=model_key)
    frozen = defaultdict(lambda: defaultdict(int))
    for run in runs:
        for r in run.hurdle:
            if r["stratum"] == "ALL":
                for c in ("n_sites", "n_reached", "n_reverted", "n_valid_correct", "n_parse_fail"):
                    frozen[(r["model"], r["family"])][c] += int(r[c])
    for m in gen_models:
        for g in GRAMMARS:
            mine = {"n_sites": gacc[(m, g, "sites")].sum(), "n_reached": gacc[(m, g, "reached")].sum(),
                    "n_reverted": gacc[(m, g, "reverted")].sum(),
                    "n_valid_correct": progs[(m, g)]["VALID_CORRECT"], "n_parse_fail": progs[(m, g)]["PARSE_FAIL"]}
            if any(int(v) != frozen[(m, g)][c] for c, v in mine.items()):
                die(f"Arm B {m} {g}: {mine} != exported {dict(frozen[(m, g)])}")
    checks.append(f"Arm B site, reach, reversion, correct-program and parse-failure counts equal each run's "
                  f"hurdle table for all {len(gen_models) * len(GRAMMARS)} model x grammar groups")
    hb = {}
    for m in gen_models:
        for g in GRAMMARS:
            W = draws(tpl[g], f"{g}/figure/arm_b")
            hb[(m, g, "reach")] = ratio(gacc[(m, g, "reached")], gacc[(m, g, "sites")], W)
            hb[(m, g, "revert")] = ratio(gacc[(m, g, "reverted")], gacc[(m, g, "reached")], W)
    yi, iticks = rows_layout(gen_models)
    hb_h = 0.17 * len(iticks) + 1.0
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, hb_h), layout="constrained", sharey=True)
    for k, (what, xl) in enumerate((("reach", "share of decision sites reached"),
                                    ("revert", "familiar spelling, given reached"))):
        ax = axes[k]
        style_rows(ax, iticks, labels=k == 0)
        for m in gen_models:
            for g in GRAMMARS:
                pt, (lo, hi) = hb[(m, g, what)]
                if not math.isfinite(pt):
                    continue
                y = yi[m] + GOFF[g]
                hbar(ax, y, lo, hi, GCOL[g], lw=0.8)
                dot(ax, pt, y, "o", GCOL[g], GFACE[g], ms=3.4, mew=0.8)
        ax.set_xlim(0, 1)
        ax.grid(axis="x", visible=True)
        ax.set_xlabel(xl)
        letter(ax, "ab"[k])
    fig.legend(handles=grammar_handles(), loc="outside lower center", ncol=2)
    save(fig, out, "fig5_generation", made, book)
    t5 = []
    for m in gen_models:
        for g in GRAMMARS:
            p = progs[(m, g)]
            t5.append({"phase": "4" if served(m) else "3.3", "model": name(m), "grammar": g,
                       "programs": p["n"], "empty_outputs": p["empty"], "parse_failures": p["PARSE_FAIL"],
                       "lexicon_failures": p["LEX_FAIL"],
                       "valid_wrong": p["VALID_WRONG"], "valid_vacuous": p["VALID_VACUOUS"],
                       "correct": p["VALID_CORRECT"], "sites": int(gacc[(m, g, "sites")].sum()),
                       "reached": int(gacc[(m, g, "reached")].sum()),
                       "reverted": int(gacc[(m, g, "reverted")].sum()),
                       "reach": fci(*hb[(m, g, "reach")]), "revert_given_reach": fci(*hb[(m, g, "revert")])})
    write_table(out, "T5_generation", t5, ["phase", "model", "grammar", "programs", "empty_outputs",
                                           "parse_failures", "lexicon_failures", "valid_wrong", "valid_vacuous", "correct",
                                           "sites", "reached", "reverted", "reach", "revert_given_reach"],
                "Table 5. Free generation (Arm B): greedy programs from a natural-language request",
                "Reach and reversion given reach are separate rates, never multiplied. 95% template-cluster "
                "bootstrap, B = 2000. empty_outputs: the model ended its turn at once (counted as lexicon failures).")
    tot = {ph: {k: sum(gacc[(m, g, k)].sum() for m in gen_models if served(m) == (ph == "4") for g in GRAMMARS)
                for k in ("sites", "reached", "reverted")} for ph in ("3.3", "4")}
    corr = {ph: (sum(progs[(m, g)]["VALID_CORRECT"] for m in gen_models if served(m) == (ph == "4") for g in GRAMMARS),
                 sum(progs[(m, g)]["n"] for m in gen_models if served(m) == (ph == "4") for g in GRAMMARS))
            for ph in ("3.3", "4")}

    def share(x, n):
        return f"{int(x)}/{int(n)} ({x / n:.1%})" if n else "–"

    empty = sorted(((sum(progs[(m, g)]["empty"] for g in GRAMMARS) / sum(progs[(m, g)]["n"] for g in GRAMMARS), m)
                    for m in gen_models if served(m)), reverse=True)
    empty_text = "; ".join(f"{name(m)} {v:.0%}" for v, m in empty if v >= 0.05)

    captions["fig5_generation"] = (
        "**In free generation the served models reach more decision sites than Phase 3.3's, and write the "
        "familiar spelling less often at them, with large differences between models.** Greedy generation from a natural-language request, with the token table "
        "and four worked examples in the prompt; each row is an instruct model of either phase. (a) Share of "
        "decision sites the program reaches (the generated text equals the target up to the site, after "
        "whitespace normalization). (b) Share of reached sites where the model writes the familiar spelling. "
        "95% template-cluster bootstrap intervals; the two rates are never multiplied. Phase 4: reach "
        f"{share(tot['4']['reached'], tot['4']['sites'])}, reversion given reach "
        f"{share(tot['4']['reverted'], tot['4']['reached'])}, correct programs {share(*corr['4'])}; Phase 3.3: "
        f"reach {share(tot['3.3']['reached'], tot['3.3']['sites'])}, reversion given reach "
        f"{share(tot['3.3']['reverted'], tot['3.3']['reached'])}, correct programs {share(*corr['3.3'])} (Table 5)."
        + (f" Some served models ended their turn at once, writing nothing (share of generations: {empty_text}); "
           "Phase 3.3's models never did." if empty_text else ""))

    # =========================================================================
    # Table 6: reversion at each rung of the ladder (the same 400 sites per model)
    # =========================================================================
    lad = defaultdict(lambda: np.zeros(0))
    for run in runs:
        for r in run.ladder:
            g, i = r["family"], tix[r["family"]][r["template"]]
            for what, v in (("n", 1), ("rev", float(r["m_seq"]) < 0)):
                key = (r["model"], g, int(r["rung"]), what)
                if not lad[key].size:
                    lad[key] = np.zeros(len(tpl[g]))
                lad[key][i] += v
    t6 = []
    for m in models:
        for g in GRAMMARS:
            row = {"phase": "4" if served(m) else "3.3", "model": name(m), "grammar": g}
            for k in RUNGS:
                n_, v = lad[(m, g, k, "n")], lad[(m, g, k, "rev")]
                pt, ci = ratio(v, n_, draws(tpl[g], f"{g}/ladder/{k}")) if n_.size and n_.sum() else (math.nan, (math.nan, math.nan))
                row[f"k{k}"] = fci(pt, ci)
            row["sites"] = int(lad[(m, g, 0, "n")].sum()) if lad[(m, g, 0, "n")].size else 0
            t6.append(row)
    write_table(out, "T6_ladder", t6, ["phase", "model", "grammar", "sites"] + [f"k{k}" for k in RUNGS],
                "Table 6. Reversion at each number of worked examples (the ladder, with the token table)",
                "The same 400 sites per model at every rung (k = examples in the prompt). 95% template-cluster "
                "bootstrap, B = 2000 (stream `<grammar>/ladder/<k>`). Arm B shows the model 4 examples, so "
                "compare its reversion given reach with k4.")

    # =========================================================================
    # Figure A1: the served models' precision
    # =========================================================================
    grid = defaultdict(lambda: [0, 0])
    for (m, g, sid, cond), one in single.items():
        if one and m in p4run.models:
            v = site[(m, g, sid)][cond]
            grid[m][0] += 1
            grid[m][1] += abs(v * 32 - round(v * 32)) < 1e-6
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, h), layout="constrained", sharey=True)
    for k, (what, xl) in enumerate((("tie", "ties: margins exactly zero (share)"),
                                    ("near", "margins within 1/8 nat of zero (share)"))):
        ax = axes[k]
        style_rows(ax, ticks, labels=k == 0)
        for m in models:
            for g in GRAMMARS:
                n_ = acc[(m, g, "rule", "n")].sum()
                v = acc[(m, g, "rule", what)].sum() / n_ if n_ else math.nan
                dot(ax, v, yp[m] + GOFF[g], "o", GCOL[g], GFACE[g], ms=3.4, mew=0.8)
        ax.set_xlim(0, None)
        ax.grid(axis="x", visible=True)
        ax.set_xlabel(xl)
        letter(ax, "ab"[k])
    fig.legend(handles=grammar_handles(), loc="outside lower center", ncol=2)
    save(fig, out, "figA1_precision", made, book)
    tA = []
    for m in models:
        n_ = sum(acc[(m, g, c, "n")].sum() for g in GRAMMARS for c in CONDS)
        ties = sum(acc[(m, g, c, "tie")].sum() for g in GRAMMARS for c in CONDS)
        near = sum(acc[(m, g, c, "near")].sum() for g in GRAMMARS for c in CONDS)
        g_n, g_k = grid.get(m, (0, 0))
        tA.append({"phase": "4" if served(m) else "3.3", "model": name(m), "arm_a_margins": int(n_),
                   "ties": int(ties), "tie_share": fmt(ties / n_ if n_ else math.nan, 4),
                   "within_1_8_nat": int(near), "within_share": fmt(near / n_ if n_ else math.nan, 4),
                   "single_token_margins": g_n if served(m) else "",
                   "share_on_1_32_grid": fmt(g_k / g_n, 4) if served(m) and g_n else ""})
    write_table(out, "TA1_precision", tA, ["phase", "model", "arm_a_margins", "ties", "tie_share",
                                           "within_1_8_nat", "within_share", "single_token_margins",
                                           "share_on_1_32_grid"],
                "Table A1. Precision: ties and margins next to zero, all three Arm A conditions",
                "share_on_1_32_grid: of a served model's margins between single tokens, the share that is a whole "
                "multiple of 1/32 nat. A margin is a difference of two log-probabilities from two requests: when "
                "the server rounds its scores and both requests are computed alike, it lands on the grid; batching "
                "with other requests moves it off (Table A2). By chance alone the share would be about 0.")
    ties4 = sum(int(r["ties"]) for r in tA if r["phase"] == "4")
    n4 = sum(int(r["arm_a_margins"]) for r in tA if r["phase"] == "4")
    gtext = ", ".join(f"{r['model']} {num(r['share_on_1_32_grid']):.2f}" for r in
                      sorted((r for r in tA if r["phase"] == "4"), key=lambda r: -num(r["share_on_1_32_grid"])))
    captions["figA1_precision"] = (
        "**Rounded scores give the served models exact ties, but do not crowd their margins near zero.** For "
        "every model, with the token table: (a) the share of margins that are exactly zero (a tie: neither "
        "spelling preferred), (b) the share within 1/8 nat of zero, where a rounded score can carry the wrong "
        f"sign. Phase 3.3 computed its output layer in fp32 and had no ties. Phase 4: {ties4} ties in {n4} Arm A "
        "margins (all three conditions). Share of single-token margins on the 1/32-nat grid of rounded (bf16) "
        f"scores: {gtext} (Table A1). A tie is not counted as a reversion.")

    # =========================================================================
    # Figure A2: re-scoring a sample (tools/retest_api.py), if it has been run
    # =========================================================================
    order = ["fig1_reversion", "fig2_rule_effect", "fig3_scale", "fig4_adaptation", "fig5_generation",
             "figA1_precision"]
    rt_dir = os.path.join(rd, "analysis_addenda", "retest")
    rts = sorted(f for f in os.listdir(rt_dir) if f.startswith("retest_") and f.endswith(".csv")) \
        if os.path.isdir(rt_dir) else []
    if rts:
        rp = os.path.join(rt_dir, rts[-1])
        p4run.inputs[f"Phase 4: analysis_addenda/retest/{rts[-1]}"] = sha256_file(rp)
        rt = [r for r in read_csv(rp) if r["note"] == ""]
        stored = {(r["model"], r["family"], r["site_id"]): float(site[(r["model"], r["family"], r["site_id"])]["rule"])
                  for r in rt}
        for r in rt:                       # the export prints 6 significant digits
            x, y = float(r["m_run"]), stored[(r["model"], r["family"], r["site_id"])]
            if abs(x - y) > 1e-5 * max(1.0, abs(x)):
                die(f"retest {r['model']} {r['site_id']}: m_run {r['m_run']} is not the run's margin {y}")
        checks.append(f"every one of the {len(rt)} re-scored sites' 'run' margins is the run's exported margin")
        by = defaultdict(list)
        for r in rt:
            by[r["model"]].append(r)
        rmodels = sorted(by, key=model_key)
        yr, rticks = rows_layout(rmodels)
        fig, axes = plt.subplots(1, 2, figsize=(WIDE, 0.17 * len(rticks) + 1.1), layout="constrained", sharey=True)
        ax = axes[0]
        style_rows(ax, rticks)
        tA2 = []
        for m in rmodels:
            ch = sorted(abs(float(r["change"])) for r in by[m])
            med = float(np.percentile(ch, 50))
            p95 = float(np.percentile(ch, 95))
            hbar(ax, yr[m], max(med, 1e-4), max(p95, 1e-4), "black")
            dot(ax, max(med, 1e-4), yr[m], "o", "black", ms=3.6)
            dot(ax, max(ch[-1], 1e-4), yr[m], "|", "0.45", ms=5, mew=1.0)
            flips = sum(r["sign_changed"] == "True" for r in by[m])
            same = sum(r["same_bits"] == "True" for r in by[m])
            dot(axes[1], flips / len(by[m]), yr[m], "o", "black", ms=3.6)
            tA2.append({"model": name(m), "sites": len(by[m]), "same_to_the_bit": same,
                        "median_abs_change": f"{med:.4f}", "p95_abs_change": f"{p95:.4f}",
                        "max_abs_change": f"{ch[-1]:.4f}", "sign_changed": flips,
                        "sign_changed_share": f"{flips / len(by[m]):.4f}",
                        "sign_changed_within_0_1_nat": sum(1 for r in by[m] if r["sign_changed"] == "True"
                                                           and abs(float(r["m_run"])) < 0.1)})
        ax.set_xscale("log")
        ax.set_xlim(1e-4, 30)
        ax.set_xlabel("|change in margin| on re-scoring (nats)")
        letter(ax, "a")
        ax = axes[1]
        style_rows(ax, rticks, labels=False)
        ax.set_xlim(0, None)
        ax.grid(axis="x", visible=True)
        ax.set_xlabel("sites whose margin changed sign (share)")
        letter(ax, "b")
        fig.legend(handles=[handle("median, to the 95th percentile", ls="-", ms=3.6),
                            handle("largest", "|", "0.45", ms=5)], loc="outside lower center", ncol=2)
        save(fig, out, "figA2_retest", made, book)
        write_table(out, "TA2_retest", tA2, ["model", "sites", "same_to_the_bit", "median_abs_change",
                                             "p95_abs_change", "max_abs_change", "sign_changed",
                                             "sign_changed_share", "sign_changed_within_0_1_nat"],
                    "Table A2. Re-scoring a random sample of Arm A sites (rule condition) through the API",
                    f"From `analysis_addenda/retest/{rts[-1]}` (tools/retest_api.py): the same request to the "
                    "same pinned deployment, sent again. The changes come from the server: batching with other "
                    "users' requests, or differences the API does not show.")
        tot = sum(len(v) for v in by.values())
        flips_all = sum(int(r["sign_changed"]) for r in tA2)
        captions["figA2_retest"] = (
            "**The same request does not always return the same margin.** A fixed random sample of Arm A sites "
            "(with the token table) per served model was scored again, by the same pinned deployment, after the "
            "run. (a) Absolute change in the margin: median to 95th percentile, and the largest (log scale; "
            "changes of 0 are drawn at 10⁻⁴). (b) Share of sites whose margin changed sign, which flips the "
            f"site between reverted and not. Overall {flips_all} of {tot} re-scored sites changed sign "
            "(Table A2). Every answer came from the pinned deployment, so the variation is on the server's "
            "side: batching with other users' requests changes the arithmetic order, and for some deployments "
            "the changes are far larger than one rounding step.")
        order.append("figA2_retest")

    # =========================================================================
    # captions, provenance
    # =========================================================================
    book.close()
    with open(os.path.join(out, "CAPTIONS.md"), "w", encoding="utf-8") as fh:
        fh.write(f"# Figures: Phase 4's served models beside Phase 3.3 ({a.run})\n\n"
                 "Each figure is in PDF, SVG and 300-dpi PNG; `ALL_FIGURES.pdf` has them all. The numbers are in "
                 "`tables/`.\n\n**Status:** Phase 4's numbers are development results (exploratory): "
                 "`phase4/PREREGISTRATION.md` was a draft when the run was made. Phase 3.3's are its registered "
                 "held-out results, on the same cells.\n\n")
        for k in order:
            fh.write(f"## {k}\n\n{captions[k]}\n\n")
    with open(os.path.join(out, "PROVENANCE.md"), "w", encoding="utf-8") as fh:
        fh.write(f"# Provenance ({a.run})\n\n")
        fh.write(f"- made: {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}\n")
        fh.write(f"- script: `phase4/code/tools/paper_figures_api.py` (sha256 {sha256_file(__file__)[:16]}…)\n")
        fh.write(f"- Phase 4 run: `{rd}`; config hash {CFG.RunConfig.from_dict(cfg4).config_hash()[:12]}\n")
        fh.write(f"- Phase 3.3 run: `{a.phase3_3}` (instruct models only)\n")
        fh.write(f"- bootstrap: B = {B}, seed {SEED}, template clusters, Phase 3.3's streams "
                 "(`<grammar>/reversion/instruct`, `<grammar>/figure/arm_b`)\n\n")
        fh.write("## Checks (each one refuses on a mismatch)\n\n")
        for c in checks:
            fh.write(f"- {c}\n")
        fh.write("\n## Inputs (sha256)\n\n")
        for k, v in sorted({**p33.inputs, **p4run.inputs}.items()):
            fh.write(f"- {k}: `{v}`\n")
    print(f"{len(made)} figures, {len(os.listdir(os.path.join(out, 'tables'))) // 2} tables -> {out}")
    for c in checks:
        print("  check:", c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
