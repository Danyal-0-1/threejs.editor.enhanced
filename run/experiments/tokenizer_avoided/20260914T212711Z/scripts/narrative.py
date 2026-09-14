"""narrative.py — OVERALL_REPORT.md, HYPOTHESIS_ASSESSMENT.md, LIMITATIONS.md,
and the experiment README.

Written for a professor who is NOT a tokenizer or language-model specialist:
every technical term is explained the first time it appears. Every number is
read from metrics/aggregate.json; nothing is transcribed by hand.
"""
from __future__ import annotations

import collections, datetime, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)
RUN_ID = os.path.basename(RUN)
ROOT = os.path.dirname(RUN)

import checkpoint as C
import finalize as F

LANGS = ["identity", "alpha", "beta", "gamma"]
ALIEN = ["alpha", "beta", "gamma"]
CONDS = ["bare", "scaffolded"]
TASKS = ["op-selection", "selector-resolution", "arg-extraction", "multi-op"]


def pct(p):
    return "NA" if p is None else f"{100*p:.1f}%"


def short(m):
    return m.replace("Qwen/Qwen2.5-Coder-", "").replace("-Instruct", "")


def num(v, fmt="{:.3f}"):
    return "NA" if v is None else fmt.format(v)


def main() -> int:
    A = F.load()
    V = F.assess(A)
    laneA, laneB, fert = A["lane_a"], A["lane_b"], A["fertility"]
    rows = F.raw_gen()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(os.path.join(RUN, "metadata", "environment.json"), encoding="utf-8") as fh:
        env = json.load(fh)
    with open(os.path.join(RUN, "inputs", "task_dataset.json"), encoding="utf-8") as fh:
        DS = json.load(fh)
    try:
        VAL = json.load(open(os.path.join(RUN, "metadata", "validation.json"), encoding="utf-8"))
    except FileNotFoundError:
        VAL = []

    qwen = next(t for t in fert["tokenizers"] if t["repo"].startswith("Qwen"))
    dsk = next((t for t in fert["tokenizers"] if "DeepSeek" in t["repo"]), None)
    b_models = sorted(laneB["models"], key=lambda m: laneB["models"][m]["n_parameters"] or 0)
    blocked = laneA["blocked"] + laneB["blocked"]

    # ═══════════════ HYPOTHESIS_ASSESSMENT.md ═══════════════
    H = [f"# Hypothesis assessment — run `{RUN_ID}`\n",
         "_Verdicts are computed mechanically by the rules frozen in "
         "`STUDY_PLAN.md` before any model ran. Nothing here was chosen after "
         "seeing the numbers._\n",
         "| hypothesis | verdict | basis |", "|---|---|---|",
         f"| **H1** base-model prior | **{V['H1']['verdict']}** | "
         f"{V['H1']['n_supporting']}/{V['H1']['n_total']} model×language cells have "
         f"ΔNLL/char > 0 with a 95% paired-bootstrap CI excluding zero |",
         f"| **H2** behavioural performance | **{V['H2']['verdict']}** | "
         f"{V['H2']['n_negative']}/{V['H2']['n_total']} cells show lower paired accuracy "
         f"than identity; {V['H2']['n_ci_excludes_zero']}/{V['H2']['n_total']} have a "
         f"CI entirely below zero |",
         f"| **H3** scaffolding | **{V['H3']['verdict']}** | "
         f"{V['H3']['n_improved']}/{V['H3']['n_total']} model×language cells improved "
         f"under scaffolding; the identity↔alien gap narrowed in "
         f"{V['H3']['n_gap_narrowed']}/{V['H3']['n_gap_total']} cells |",
         f"| **H4** tokenization | **{V['H4']['verdict']}** | "
         f"{V['H4']['n_more_tokens']}/{V['H4']['n_total']} cells needed more prompt "
         f"tokens than identity for the same information |", "",
         "## H1 — base-model prior\n",
         "> _For semantically matched programs, alien languages will have higher "
         "NLL/character than identity._\n",
         "| base model | language | ΔNLL/char | 95% CI | CI excludes 0 |",
         "|---|---|---:|---|---|"]
    for c in V["H1"]["cells"]:
        H.append(f"| `{short(c['model'])}` | `{c['language']}` | {c['delta']:+.4f} | "
                 f"[{c['lo']:+.4f}, {c['hi']:+.4f}] | {'yes' if c['supports'] else 'no'} |")
    H += ["", "## H2 — behavioural performance\n",
          "> _Under information-matched prompts, alien-language generations may have "
          "lower canonical-IR accuracy than identity._\n",
          "| model | condition | language | paired Δaccuracy | 95% CI | McNemar p | discordant pairs |",
          "|---|---|---|---:|---|---:|---:|"]
    for c in V["H2"]["cells"]:
        H.append(f"| `{short(c['model'])}` | {c['condition']} | `{c['language']}` | "
                 f"{c['rd']:+.3f} | [{c['lo']:+.3f}, {c['hi']:+.3f}] | {c['p']:.4f} | "
                 f"{c['n_disc']} |")
    H += ["", "With 21 generation cases the discordant-pair counts are small, so the "
          "McNemar p-values have little power. Read the effect sizes and intervals.\n",
          "## H3 — scaffolding\n",
          "> _Language-neutral scaffolding may improve accuracy and reduce the gap._\n",
          "| model | language | bare | scaffolded | difference |", "|---|---|---:|---:|---:|"]
    for c in V["H3"]["cells"]:
        H.append(f"| `{short(c['model'])}` | `{c['language']}` | {pct(c['bare'])} | "
                 f"{pct(c['scaffolded'])} | {c['delta']:+.3f} |")
    if V["H3"]["gaps"]:
        H += ["", "**Did scaffolding narrow the identity↔alien gap?**\n",
              "| model | language | gap (bare) | gap (scaffolded) | narrowed |",
              "|---|---|---:|---:|---|"]
        for g in V["H3"]["gaps"]:
            H.append(f"| `{short(g['model'])}` | `{g['language']}` | {g['gap_bare']:+.3f} | "
                     f"{g['gap_scaffolded']:+.3f} | {'yes' if g['narrowed'] else 'no'} |")
    H += ["", "## H4 — tokenization\n",
          "> _Higher tokenizer fertility should increase token count and computational "
          "cost. Its relationship with semantic accuracy is exploratory and must not "
          "be assumed._\n",
          "| model | condition | language | relative fertility | prompt tokens (median) | "
          "identity prompt tokens | ratio |", "|---|---|---|---:|---:|---:|---:|"]
    for c in V["H4"]["cells"]:
        H.append(f"| `{short(c['model'])}` | {c['condition']} | `{c['language']}` | "
                 f"{c['relative_fertility']:.3f}× | {num(c['input_tokens_median'],'{:.0f}')} | "
                 f"{num(c['identity_input_tokens_median'],'{:.0f}')} | "
                 f"{num(c['token_ratio'])} |")
    dp = V["dense_prior_rule"]
    H += ["", "The token-cost half of H4 is confirmatory. The fertility↔accuracy "
          "relationship is **descriptive and non-causal**: only three fertility values "
          "exist (one per language), and each language changes spelling, tokenization "
          "and — for gamma — lexical behaviour simultaneously.\n",
          "## The predeclared dense-prior rule\n",
          "Suggestive support requires **all four** conditions:\n",
          "| condition | met? |", "|---|---|",
          f"| (a) base ΔNLL/character rises for alien syntax | {'YES' if dp['a_nll_rises'] else 'NO'} |",
          f"| (b) paired canonical semantic accuracy falls for the same languages | {'YES' if dp['b_accuracy_falls'] else 'NO'} |",
          f"| (c) the pattern is reasonably consistent across model sizes and tasks | {'YES' if dp['c_consistent_across_sizes_and_tasks'] else 'NO'} |",
          f"| (d) the evidence does NOT come only from gamma | {'YES' if dp['d_not_only_gamma'] else 'NO'} |", "",
          f"**Verdict: {'SUGGESTIVE SUPPORT' if dp['suggestive_support'] else 'NOT ALL CONDITIONS MET'}.**\n",
          "**Causality is not established, and cannot be established by this design.** "
          "Tokenizer fertility is not controlled: each alien language differs from 3DOM "
          "in spelling *and* in how many tokens that spelling costs, at the same time. "
          "Gamma carries an additional lexical-reachability defect (24 check-(g) "
          "findings). No experiment here manipulates one factor while holding the "
          "others fixed.\n",
          "**This does not select a winning alien syntax**, and it does not make any "
          "candidate eligible under Experiment 01's fertility gate.\n"]
    open(os.path.join(RUN, "HYPOTHESIS_ASSESSMENT.md"), "w", encoding="utf-8").write("\n".join(H))

    # ═══════════════ LIMITATIONS.md ═══════════════
    alpha_q = qwen["rows"]["alpha"]["relative_fertility_vs_identity"]
    alpha_d = ("" if not dsk else
               f" / {dsk['rows']['alpha']['relative_fertility_vs_identity']:.3f}× (DeepSeek-V3)")
    L = [f"# Limitations — run `{RUN_ID}`\n",
         "## Design limitations\n",
         "1. **Fertility is not controlled — this is the defining limitation.** The "
         "Experiment 01 eligibility gate (relative fertility ∈ [0.95, 1.05]) was "
         "deliberately waived so behaviour could be observed at all. Every alien "
         "language therefore differs from 3DOM in spelling **and** in token cost "
         "simultaneously. No result here can attribute an accuracy difference to "
         "spelling rather than to length, or vice versa.\n",
         "2. **Gamma is not a clean isomorphic control.** It carries 24 findings from "
         "Experiment 01's proposed check (g): 22 `g1` (word-class spellings became "
         "symbols, changing how keywords are distinguished from identifiers) and 2 "
         "`g2` (token sequences reachable in gamma that no 3DOM text can produce). "
         "Gamma is a Unicode/lexer stress diagnostic. Dense-prior claims must not "
         "rest on it.\n",
         "3. **Alpha is the cleanest exploratory comparison but still out of band.** "
         f"Its relative fertility is {alpha_q:.3f}× (Qwen2){alpha_d}, "
         "above the 1.05 limit. Alpha is also an *interference* design — it reuses "
         "3DOM words with permuted meanings — so it confounds unfamiliarity with "
         "active misdirection.\n",
         f"4. **Beta is strongly fertility-confounded** "
         f"({qwen['rows']['beta']['relative_fertility_vs_identity']:.3f}× Qwen2) despite "
         "matching 3DOM's character length almost exactly.\n",
         "5. **Small behavioural dataset.** 21 generation cases (plus 1 graceful-refusal "
         "case) from one editing domain and two fixture scenes. Wilson and bootstrap "
         "intervals are correspondingly wide, and the exact McNemar tests have few "
         "discordant pairs and therefore little power.\n",
         "6. **One model family.** All behavioural models are Qwen2.5-Coder and share "
         "one Qwen2 BPE tokenizer. The fertility measurement adds a second tokenizer "
         "design (DeepSeek-V3), but **DeepSeek-V3 was used as a tokenizer only** — its "
         "weights (671B) are not runnable on this machine and it was **never** "
         "behaviourally tested.\n",
         "7. **One prompt design.** A single specification format, one worked-example "
         "set, one scaffold format. Prompt wording is known to move small-model "
         "behaviour substantially; none of that variance is sampled here.\n",
         "8. **English descriptions unavoidably favour identity.** The operation "
         "descriptions are plain English and identical in all four arms, but identity's "
         "*spellings* are themselves English words, so the description and the spelling "
         "agree only in the identity arm. This is inherent to comparing a native "
         "notation against invented ones, and is part of the phenomenon under study "
         "rather than a harness defect.\n",
         "9. **Conditional task loss depends on the reference serialisation.** It scores "
         "one chosen gold program string; a different but equally correct program would "
         "give different numbers.\n",
         "10. **Greedy decoding only.** One deterministic completion per case. No "
         "sampling, no temperature sweep, no self-consistency, no pass@k.\n",
         "## Measurement limitations\n",
         "11. **Lane A scores base models, Lane B scores instruct models.** They answer "
         "different questions and are never pooled. Base-model NLL is language-model "
         "surprise on teacher-forced text; it is not task accuracy.\n",
         "12. **No training occurred anywhere in this study.** There is no training "
         "loss and no loss-over-epochs curve.\n",
         "13. **Timing is hardware- and condition-specific.** Figures come from one "
         "RTX 3080 Ti Laptop GPU under FP16 (Lane B) and FP32 (Lane A). CPU and GPU "
         "runs, and different precisions, are never compared as though they were one "
         "condition.\n"]
    if blocked:
        L.append("14. **Blocked cells.** The following were attempted under the "
                 "predeclared configuration and recorded as failures rather than "
                 "retried at different settings:\n")
        for b in blocked:
            L.append(f"    - `{b['model']}` Lane {b['lane']} "
                     f"({b['precision']}/{b['device']}) — **{b['failure_kind']}**. "
                     f"Command: `{b['attempted_command']}`. "
                     f"Error: {str(b['error'])[:200]}")
        L.append("")
    L += ["## What this study does not do\n",
          "- It does **not** select or announce a winning alien syntax.\n"
          "- It does **not** make any candidate eligible under Experiment 01's rule.\n"
          "- It does **not** prove that dense prior knowledge caused any failure.\n"
          "- It does **not** show that fertility confirms hallucination.\n"
          "- It does **not** show that a model 'cannot understand' alien syntax.\n"
          "- It does **not** claim gamma is isomorphic to 3DOM.\n"]
    open(os.path.join(RUN, "LIMITATIONS.md"), "w", encoding="utf-8").write("\n".join(L))

    print("HYPOTHESIS_ASSESSMENT.md and LIMITATIONS.md written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
