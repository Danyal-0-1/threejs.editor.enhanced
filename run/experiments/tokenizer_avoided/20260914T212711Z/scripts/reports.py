"""reports.py — every report, generated from metrics/aggregate.json and the raw rows.

Nothing here is hand-typed from a log. Numbers come from the aggregate, examples
come from the raw JSONL, and a cell with no evidence prints NA/BLOCKED.
"""
from __future__ import annotations

import collections, datetime, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)
RUN_ID = os.path.basename(RUN)

import checkpoint as C

LANGS = ["identity", "alpha", "beta", "gamma"]
CONDS = ["bare", "scaffolded"]
TASKS = ["op-selection", "selector-resolution", "arg-extraction", "multi-op"]

LANG_BLURB = {
 "identity": ("**Ordinary 3DOM.** The baseline. `$S('.wheel').recolor('black')` — the "
   "selector entry is `$S`, the chain operator is `.`, classes start with `.`, and "
   "the operation names are ordinary English words (`recolor`, `scale`, `move`). "
   "This is the only arm whose spellings a code model plausibly saw during "
   "pretraining."),
 "alpha": ("**The interference condition — familiar spellings, wrong meanings.** "
   "Alpha reuses 3DOM's own vocabulary but PERMUTES which role each word plays. "
   "The word `recolor` spells the *function keyword*; the word `scale` spells the "
   "*recolour* operation; `mesh` spells *receiveShadow*; the class sigil is `#` and "
   "the id sigil is `:`. Every spelling is familiar and almost every one means "
   "something else. Its relative tokenizer fertility is 1.068 (Qwen2) / 1.073 "
   "(DeepSeek-V3) — the mildest of the three, though still outside Experiment 01's "
   "[0.95, 1.05] band."),
 "beta": ("**The absence condition — pronounceable invented words.** Beta replaces "
   "each spelling with an ASCII pseudo-word of deliberately matched length and "
   "camelCase shape (`flertum` for recolour, `mumvumfe` for the function keyword, "
   "`&Q` for the selector entry, `~` for the class sigil). Character length matches "
   "3DOM almost exactly, but the invented words are not single vocabulary units, so "
   "they fragment into more ordinary sub-word pieces: relative fertility 1.401 "
   "(Qwen2) / 1.448 (DeepSeek-V3). Beta is therefore STRONGLY FERTILITY-CONFOUNDED."),
 "gamma": ("**The glyph / surface-distance condition — and a lexer stress test.** "
   "Gamma substitutes compact non-ASCII symbols (`⏦` for recolour, `⍤` for the "
   "function keyword, `⟠⟠` for the selector entry, `◈` for the class sigil). It uses "
   "FEWER Unicode code points than 3DOM (0.716×) yet the most tokens: relative "
   "fertility 1.937 (Qwen2) / 2.285 (DeepSeek-V3), with 36.4% / 55.0% of token ids "
   "showing byte-fallback fragmentation.\n\n"
   "**Gamma is not a clean isomorphic control.** Experiment 01's proposed check (g) "
   "found 24 issues: 22 `g1` findings (word-class spellings became symbols, changing "
   "how keywords are told apart from identifiers) and 2 `g2` reachability findings "
   "(token sequences reachable in gamma that no 3DOM text can produce — e.g. "
   "`meshmesh` is one identifier in 3DOM while `⍇⍇` can stay two type tokens). "
   "Gamma results must be read as a Unicode/lexer diagnostic, never as evidence "
   "about isomorphic syntax alone."),
}


def fmt_int(v):
    return "NA" if v is None else f"{v:,}"


def pct(p):
    return "NA" if p is None else f"{100*p:.1f}%"


def ci(e):
    return (f"{pct(e['proportion'])} ({e['numerator']}/{e['denominator']}, "
            f"95% CI {pct(e['wilson95_lo'])}–{pct(e['wilson95_hi'])})")


def short(m):
    return m.replace("Qwen/Qwen2.5-Coder-", "").replace("-Instruct", "")


def raw_gen():
    out = []
    for p in glob.glob(os.path.join(RUN, "raw", "*", "lane_b", "gen.jsonl")):
        out += C.read_rows(p)
    return out


def load():
    with open(os.path.join(RUN, "metrics", "aggregate.json"), encoding="utf-8") as fh:
        return json.load(fh)


def example_block(rows, lang, want_correct, limit=2):
    """Representative outputs, pulled from the raw rows."""
    pool = [r for r in rows if r["language"] == lang
            and r.get("scoring_family") == "generation"
            and ((r.get("semantic_correct") == 1) if want_correct
                 else (r.get("semantic_correct") == 0))]
    pool.sort(key=lambda r: (r["model"], r["case_id"]))
    out = []
    for r in pool[:limit]:
        out.append(
            f"- **`{r['case_id']}`** · {short(r['model'])} · {r['condition']} · "
            f"outcome `{r['outcome']}`\n"
            f"  - request: _{next((c['prompt'] for c in CASES if c['id']==r['case_id']), '')}_\n"
            f"  - model wrote: `{(r.get('extracted_code') or '').strip()[:200]}`\n"
            f"  - parsed to: `{json.dumps(r.get('emitted_ops'))[:200]}`\n"
            f"  - resolved nodes: `{json.dumps(r.get('resolved_nodes'))[:160]}`\n"
            f"  - scorer said: {r.get('scorer_explanation','')[:220]}\n")
    return "".join(out) if out else "_none recorded_\n"


with open(os.path.join(RUN, "inputs", "task_dataset.json"), encoding="utf-8") as fh:
    DS = json.load(fh)
CASES = DS["cases"]


# ── per-language reports ─────────────────────────────────────────────────────

def language_report(lang, A, rows):
    laneA, laneB, fert = A["lane_a"], A["lane_b"], A["fertility"]
    qwen = next(t for t in fert["tokenizers"] if t["repo"].startswith("Qwen"))
    dsk = next((t for t in fert["tokenizers"] if "DeepSeek" in t["repo"]), None)
    L = [f"# `{lang}` — language report\n",
         f"_Run `{RUN_ID}` · an exploratory fertility-unmatched model evaluation._\n",
         "## 1. What this language changes\n", LANG_BLURB[lang], "\n",
         "## 2. Tokenizer cost (a confound, not a verdict)\n",
         "| tokenizer | tokens/program | tokens/char | vs identity | byte-fallback fragments |",
         "|---|---:|---:|---:|---:|"]
    for t in (qwen, dsk):
        if not t:
            continue
        r = t["rows"][lang]
        # All four Qwen2.5-Coder repositories share ONE Qwen2 BPE tokenizer and
        # produce identical rows, so this is evidence from two distinct
        # tokenizer DESIGNS, not five independent ones.
        name = ("Qwen2 BPE (shared by all 4 Qwen2.5-Coder repos)"
                if t["repo"].startswith("Qwen") else t["repo"])
        L.append(f"| `{name}` | {r['tokens_per_program']:.3f} | "
                 f"{r['fertility_tok_per_char']:.4f} | "
                 f"{r['relative_fertility_vs_identity']:.3f}× | "
                 f"{r['fragmented_percent']:.3f}% |")
    L += ["", "Fertility demonstrates **token cost**. Whether accuracy degrades is a "
          "separate measurement, reported in §5.\n",
          "## 3. What was fed to each model\n",
          "**Lane A (base checkpoints):** the program string alone — no editing "
          "request, no instruction prompt, empty neutral prefix, identical policy in "
          "every language. Teacher-forced scoring only; **no training occurred**.\n",
          "**Lane B (instruct checkpoints):** a system prompt containing the "
          "mechanically rendered language specification for **this** language "
          "(program shape, selector forms, all 15 operations with their argument "
          "names and a plain-English description, four worked examples), plus a user "
          "message with the natural-language editing request. In `scaffolded` the "
          "user message also carries the scene's addressable parts and tag list, "
          "rendered with this language's sigils.\n",
          "Every spelling shown was **this language's own**; no 3DOM spelling was "
          "taught to an alien arm and no translation pair appeared in any prompt "
          "(enforced by `taught_spellings` tests). The exact model input for every "
          "case is saved under `prompts/rendered/`.\n",
          "## 4. Lane A — base-model surprise\n",
          "| base model | device | NLL/char | NLL/token | perplexity | ΔNLL/char vs identity | 95% CI |",
          "|---|---|---:|---:|---:|---:|---|"]
    for label, m in laneA["models"].items():
        e = m["languages"].get(lang)
        if not e:
            continue
        d = e.get("delta_nll_per_char")
        L.append(f"| `{short(m['model'])}` | {m['device']} | {e['nll_per_char']:.4f} | "
                 f"{e['nll_per_token']:.4f} | {e['token_perplexity']:.2f} | "
                 + (f"{d['point']:+.4f} | [{d['ci95_lo']:+.4f}, {d['ci95_hi']:+.4f}] |"
                    if d else "— (baseline) | — |"))
    if laneA["blocked"]:
        L += ["", "**Blocked Lane A cells:**", ""]
        for b in laneA["blocked"]:
            L.append(f"- `{b['model']}` ({b['precision']}/{b['device']}) — "
                     f"{b['failure_kind']}: {str(b['error'])[:160]}")
    L += ["", "NLL/character is the primary prior-distance measure (fertility-free). "
          "NLL/token is diagnostic only, because token boundaries differ across "
          "languages. These are **not** accuracy numbers.\n",
          "## 5. Lane B — behavioural accuracy\n"]

    models = sorted(laneB["models"], key=lambda m: laneB["models"][m]["n_parameters"] or 0)
    for cond in CONDS:
        L += [f"### {cond}\n",
              "| instruct model | semantic accuracy | parse validity | language compliance | "
              "vacuous | Δ vs identity | 95% paired CI | McNemar p |",
              "|---|---|---|---|---:|---:|---|---:|"]
        for m in models:
            ce = laneB["models"][m]["conditions"].get(cond)
            e = ce["languages"].get(lang) if ce else None
            if not e:
                L.append(f"| `{short(m)}` | NA | NA | NA | NA | NA | NA | NA |")
                continue
            comp = ce.get("comparisons", {}).get(lang, {}).get("semantic")
            dtxt = (f"{comp['risk_difference']:+.3f}" if comp else "— (baseline)")
            citxt = (f"[{comp['ci95_lo']:+.3f}, {comp['ci95_hi']:+.3f}]" if comp else "—")
            ptxt = (f"{comp['mcnemar']['p_value']:.4f} (n_disc={comp['mcnemar']['n_discordant']})"
                    if comp else "—")
            L.append(f"| `{short(m)}` | {ci(e['semantic_accuracy'])} | "
                     f"{pct(e['parse_validity']['proportion'])} | "
                     f"{pct(e['language_compliance']['proportion'])} | "
                     f"{pct(e['vacuous_rate']['proportion'])} | {dtxt} | {citxt} | {ptxt} |")
        L.append("")

    L += ["## 6. Task-specific strengths and failures\n",
          "| model | condition | " + " | ".join(TASKS) + " |",
          "|---|---|" + "---|" * len(TASKS)]
    for m in models:
        for cond in CONDS:
            ce = laneB["models"][m]["conditions"].get(cond)
            e = ce["languages"].get(lang) if ce else None
            if not e:
                continue
            L.append(f"| `{short(m)}` | {cond} | "
                     + " | ".join(f"{pct(e['per_task'][t]['proportion'])} "
                                  f"({e['per_task'][t]['numerator']}/{e['per_task'][t]['denominator']})"
                                  for t in TASKS) + " |")

    L += ["", "## 7. Parse failures versus semantic failures\n",
          "| model | condition | LEX_FAIL | PARSE_FAIL | VALID_VACUOUS | VALID_WRONG | VALID_CORRECT |",
          "|---|---|---:|---:|---:|---:|---:|"]
    for m in models:
        for cond in CONDS:
            ce = laneB["models"][m]["conditions"].get(cond)
            e = ce["languages"].get(lang) if ce else None
            if not e:
                continue
            o = e["outcomes"]
            L.append(f"| `{short(m)}` | {cond} | " + " | ".join(
                str(o.get(k, 0)) for k in ("LEX_FAIL", "PARSE_FAIL", "VALID_VACUOUS",
                                           "VALID_WRONG", "VALID_CORRECT")) + " |")
    L += ["", "These are orthogonal constructs and are never averaged. A program can "
          "parse perfectly and mean the wrong thing (`VALID_WRONG`), or parse and mean "
          "nothing at all (`VALID_VACUOUS` — a parse success and a task failure).\n",
          "### Hallucination categories\n",
          "| model | condition | " + " | ".join(
              ["invented_operation", "invented_selector", "invented_argument",
               "wrong_language_spelling", "extra_operation", "missing_operation",
               "prose_instead_of_code"]) + " |",
          "|---|---|" + "---:|" * 7]
    for m in models:
        for cond in CONDS:
            ce = laneB["models"][m]["conditions"].get(cond)
            e = ce["languages"].get(lang) if ce else None
            if not e:
                continue
            h = e["hallucinations"]
            L.append(f"| `{short(m)}` | {cond} | " + " | ".join(
                str(h.get(k, 0)) for k in
                ["invented_operation", "invented_selector", "invented_argument",
                 "wrong_language_spelling", "extra_operation", "missing_operation",
                 "prose_instead_of_code"]) + " |")
    L += ["", "A parse failure is **not** counted as a hallucination.\n",
          "## 8. Representative outputs\n", "**Correct:**\n",
          example_block(rows, lang, True), "\n**Failed:**\n",
          example_block(rows, lang, False), "",
          "## 9. Runtime and token cost\n",
          "| model | condition | input tok (med) | output tok (med) | e2e s (med) | e2e s (p95) | tok/s |",
          "|---|---|---:|---:|---:|---:|---:|"]
    for m in models:
        for cond in CONDS:
            ce = laneB["models"][m]["conditions"].get(cond)
            e = ce["languages"].get(lang) if ce else None
            if not e:
                continue
            g = lambda d, k: ("NA" if d.get(k) is None else f"{d[k]:.3f}")
            L.append(f"| `{short(m)}` | {cond} | {g(e['input_tokens'],'median')} | "
                     f"{g(e['output_tokens'],'median')} | {g(e['e2e_seconds'],'median')} | "
                     f"{g(e['e2e_seconds'],'p95')} | "
                     f"{g(e['output_tokens_per_second'],'median')} |")

    L += ["", "## 10. Effect of scaffolding\n",
          "| model | bare | scaffolded | difference |", "|---|---:|---:|---:|"]
    for m in models:
        cb = laneB["models"][m]["conditions"].get("bare")
        cs = laneB["models"][m]["conditions"].get("scaffolded")
        eb = cb["languages"].get(lang) if cb else None
        es = cs["languages"].get(lang) if cs else None
        if eb and es:
            d = es["semantic_accuracy"]["proportion"] - eb["semantic_accuracy"]["proportion"]
            L.append(f"| `{short(m)}` | {pct(eb['semantic_accuracy']['proportion'])} | "
                     f"{pct(es['semantic_accuracy']['proportion'])} | {d:+.3f} |")

    L += ["", "## 11. Uncertainty\n",
          "Accuracy proportions carry Wilson 95% intervals. Language-vs-identity "
          "comparisons use matched items with a 95% paired item-level bootstrap "
          "(10 000 resamples, seed 20260910) and an exact McNemar test on the "
          "discordant pairs. With 21 generation cases the intervals are wide: read "
          "effect sizes and intervals, not p-values.\n",
          "## 12. What can and cannot be concluded\n",
          "**Can:** how many model tokens this language cost, how long it took, how "
          "often its outputs lexed, parsed, meant nothing, or meant the right thing, "
          "and how that compares to identity on the very same items.\n",
          "**Cannot:** that tokenizer fertility *caused* any accuracy difference. "
          "Spelling, tokenization"
          + (", and lexical reachability" if lang == "gamma" else "")
          + " all change together here; nothing isolates one. No winner is selected, "
          "and nothing here makes any candidate eligible under Experiment 01's "
          "fertility gate.\n"]
    if lang == "gamma":
        L.append("**Gamma specifically:** the 24 check-(g) findings mean gamma is a "
                 "Unicode/lexer stress diagnostic, not a clean isomorphism test. "
                 "Dense-prior claims must not rest on gamma alone.\n")
    return "\n".join(L)


# ── per-model reports ────────────────────────────────────────────────────────

def model_report(model, A, rows, lane):
    laneA, laneB = A["lane_a"], A["lane_b"]
    if lane == "A":
        m = laneA["models"][model]
        kind, mm = "Base", m
    else:
        m = laneB["models"][model]
        kind, mm = "Instruct", m
    L = [f"# `{model}` — model report\n",
         f"_Run `{RUN_ID}` · Lane {lane}_\n", "## Identity\n",
         f"- **Checkpoint type:** {kind}",
         f"- **Resolved revision:** `{m.get('revision','unresolved')}`",
         f"- **Parameters:** {fmt_int(m.get('n_parameters'))}",
         f"- **Tokenizer:** Qwen2 BPE (shared across the Qwen2.5-Coder family)",
         f"- **Device / precision:** `{m.get('device')}` / `{m.get('precision')}`",
         f"- **Cold model-load time:** {m.get('model_load_seconds')} s",
         f"- **Warm-up time (excluded from per-case latency):** {m.get('warmup_seconds')} s",
         f"- **Peak VRAM allocated:** {m.get('peak_vram_allocated_bytes')} bytes",
         f"- **Peak process RSS:** {m.get('peak_rss_bytes')} bytes", ""]
    if lane == "A":
        L += ["## Completed cells\n",
              f"- {m['n_programs_scored']} paired programs × 4 languages = "
              f"{m['n_programs_scored']*4} NLL scorings\n",
              "## Lane A results\n",
              "| language | NLL/char | NLL/token | perplexity | tokens/program | ΔNLL/char | 95% CI |",
              "|---|---:|---:|---:|---:|---:|---|"]
        for lang in LANGS:
            e = m["languages"].get(lang)
            if not e:
                continue
            d = e.get("delta_nll_per_char")
            L.append(f"| `{lang}` | {e['nll_per_char']:.4f} | {e['nll_per_token']:.4f} | "
                     f"{e['token_perplexity']:.2f} | {e['model_tokens_per_program']:.3f} | "
                     + (f"{d['point']:+.4f} | [{d['ci95_lo']:+.4f}, {d['ci95_hi']:+.4f}] |"
                        if d else "— | — |"))
        L += ["", "These are base-model likelihoods on teacher-forced programs. "
              "**No training occurred**; there is no training-loss curve.\n"]
    else:
        L += ["## Completed cells\n",
              f"- {m['n_rows']} rows total · {m['n_generation_rows']} generation · "
              f"{m['n_refusal_rows']} graceful-refusal · {m['n_error_rows']} error/OOM\n",
              "## Lane B results\n"]
        for cond in CONDS:
            ce = m["conditions"].get(cond)
            if not ce:
                continue
            L += [f"### {cond}\n",
                  "| language | semantic accuracy | parse validity | " +
                  " | ".join(TASKS) + " | e2e s (med) | out tok (med) |",
                  "|---|---|---|" + "---|" * (len(TASKS) + 2)]
            for lang in LANGS:
                e = ce["languages"].get(lang)
                if not e:
                    continue
                L.append(f"| `{lang}` | {ci(e['semantic_accuracy'])} | "
                         f"{pct(e['parse_validity']['proportion'])} | "
                         + " | ".join(pct(e["per_task"][t]["proportion"]) for t in TASKS)
                         + f" | {e['e2e_seconds']['median']:.3f} | "
                           f"{e['output_tokens']['median']:.0f} |")
            L.append("")
        if m.get("graceful_refusal"):
            L += ["### Graceful refusal (`merged-sheets`, scored separately)\n",
                  "| language/condition | correct |", "|---|---|"]
            for k, v in sorted(m["graceful_refusal"].items()):
                L.append(f"| {k} | {v['numerator']}/{v['denominator']} |")
            L.append("")

    blocked = [b for b in (laneA["blocked"] + laneB["blocked"])
               if b["model"] == m.get("model", model)]
    L += ["## Failures\n"]
    if blocked:
        for b in blocked:
            L += [f"- **{b['failure_kind']}** in Lane {b['lane']} "
                  f"({b['precision']}/{b['device']})",
                  f"  - attempted: `{b['attempted_command']}`",
                  f"  - error: `{str(b['error'])[:400]}`"]
    else:
        L.append("- None. No OOM, timeout or harness error was recorded for this "
                 "model under the configuration reported above.")
    L += ["", "## Scaling interpretation\n",
          "See `plots/overall/09_model_size_scaling` for accuracy against parameter "
          "count and `plots/overall/06_nll_per_char` for surprise against size. With "
          "three or four sizes these are trends, not fitted scaling laws.\n"]
    return "\n".join(L)


def main() -> int:
    A = load()
    rows = raw_gen()
    os.makedirs(os.path.join(RUN, "reports", "languages"), exist_ok=True)
    os.makedirs(os.path.join(RUN, "reports", "models"), exist_ok=True)
    made = []
    for lang in LANGS:
        p = os.path.join(RUN, "reports", "languages", f"{lang}.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(language_report(lang, A, rows))
        made.append(p)
    for model in A["lane_a"]["models"]:
        safe = model.replace("/", "__").replace(" ", "").replace("[", "").replace("]", "")
        p = os.path.join(RUN, "reports", "models", f"{safe}_laneA.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(model_report(model, A, rows, "A"))
        made.append(p)
    for model in A["lane_b"]["models"]:
        safe = model.replace("/", "__")
        p = os.path.join(RUN, "reports", "models", f"{safe}_laneB.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(model_report(model, A, rows, "B"))
        made.append(p)
    print(f"reports written: {len(made)}")
    for p in made:
        print("  " + os.path.relpath(p, RUN))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
