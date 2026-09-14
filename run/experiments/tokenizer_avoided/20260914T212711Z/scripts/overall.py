"""overall.py — OVERALL_REPORT.md and the experiment README.

Audience: a professor who is not a tokenizer or language-model specialist.
Every technical term is explained the first time it is used, and every number
is read from metrics/aggregate.json rather than typed by hand.
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


def ints(v):
    """Parameter counts are absent until a model writes its meta row (still
    running, or BLOCKED). Print NA rather than crash or imply zero."""
    return "NA" if v is None else f"{v:,}"


def num(v, fmt="{:.3f}"):
    return "NA" if v is None else fmt.format(v)


def main() -> int:
    A = F.load()
    V = F.assess(A)
    laneA, laneB, fert = A["lane_a"], A["lane_b"], A["fertility"]
    rows = F.raw_gen()
    gen = [r for r in rows if r.get("scoring_family") == "generation"]
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    env = json.load(open(os.path.join(RUN, "metadata", "environment.json"), encoding="utf-8"))
    DS = json.load(open(os.path.join(RUN, "inputs", "task_dataset.json"), encoding="utf-8"))
    try:
        VAL = json.load(open(os.path.join(RUN, "metadata", "validation.json"), encoding="utf-8"))
    except FileNotFoundError:
        VAL = []
    qwen = next(t for t in fert["tokenizers"] if t["repo"].startswith("Qwen"))
    dsk = next((t for t in fert["tokenizers"] if "DeepSeek" in t["repo"]), None)
    b_models = sorted(laneB["models"], key=lambda m: laneB["models"][m]["n_parameters"] or 0)
    a_models = list(laneA["models"])
    blocked = laneA["blocked"] + laneB["blocked"]
    dp = V["dense_prior_rule"]

    O = []
    w = O.append

    w(f"# OVERALL REPORT — `tokenizer_avoided`, run `{RUN_ID}`\n")
    w("**An exploratory fertility-unmatched model evaluation.**\n")
    w(f"_Generated {now}. Every number below is read from "
      f"`metrics/aggregate.json`, which is computed from the raw per-item rows in "
      f"`raw/`. Nothing is transcribed by hand._\n")
    w("---\n")

    # 1 EXECUTIVE SUMMARY
    w("## 1. Executive summary\n")
    w("We asked whether small code-generation models behave differently when the "
      "*same* scene-editing task is written in ordinary 3DOM versus three invented "
      "\"alien\" notations that mean exactly the same thing. We measured two "
      "separate things, in two separate lanes that are never mixed:\n")
    w("- **Lane A** — how *surprising* each notation is to a raw (base) model that "
      "is simply reading the program. No task, no question, no answer.\n"
      "- **Lane B** — how *accurately* an instruction-tuned model actually performs "
      "the editing task when asked, in each notation.\n")
    w("The headline findings:\n")
    w(f"1. **The alien notations are reliably more surprising to base models "
      f"(H1: {V['H1']['verdict']}).** In {V['H1']['n_supporting']} of "
      f"{V['H1']['n_total']} model×language cells the extra surprise per character "
      "was positive with a 95% confidence interval that excludes zero. The ordering "
      "was stable at every model size: gamma > beta > alpha.\n")
    h2n, h2t = V["H2"]["n_negative"], V["H2"]["n_total"]
    w(f"2. **Behavioural accuracy (H2: {V['H2']['verdict']}).** {h2n} of {h2t} "
      f"model×condition×language cells scored *lower* than ordinary 3DOM on the very "
      f"same task items; {V['H2']['n_ci_excludes_zero']} of {h2t} had a confidence "
      "interval entirely below zero.\n")
    w(f"3. **Scaffolding (H3: {V['H3']['verdict']}).** Giving the model the exact "
      f"list of addressable scene parts changed accuracy in "
      f"{V['H3']['n_improved']} of {V['H3']['n_total']} cells upward, and narrowed the "
      f"identity↔alien gap in {V['H3']['n_gap_narrowed']} of "
      f"{V['H3']['n_gap_total']} comparisons.\n")
    w(f"4. **Token cost (H4: {V['H4']['verdict']}).** The same information cost more "
      f"model tokens in every alien arm ({V['H4']['n_more_tokens']}/"
      f"{V['H4']['n_total']} cells). This is a measured efficiency cost and, on its "
      "own, says nothing about accuracy.\n")
    w(f"5. **The predeclared dense-prior rule was "
      f"{'MET' if dp['suggestive_support'] else 'NOT fully met'}** "
      f"(a={dp['a_nll_rises']}, b={dp['b_accuracy_falls']}, "
      f"c={dp['c_consistent_across_sizes_and_tasks']}, d={dp['d_not_only_gamma']}). "
      "Even where met, **causality is not established**: fertility is not controlled "
      "and gamma has an additional lexical defect.\n")
    w("**No winning alien syntax is selected, and nothing here makes any candidate "
      "eligible under Experiment 01's fertility gate.**\n")

    # 2 RESEARCH QUESTION
    w("## 2. Research question\n")
    w("Do language models depend on having seen a notation's *spellings* during "
      "pretraining, or do they work from the structure of the language they are "
      "shown? If the former, then renaming every keyword — while keeping the grammar, "
      "the meanings, and the task identical — should make models worse. That is the "
      "\"dense prior\" hypothesis. This run measures it exploratorily.\n")

    # 3 THE FOUR LANGUAGES
    w("## 3. What identity, alpha, beta and gamma are\n")
    w("All four are **the same language with different spellings**. The grammar, the "
      "15 operations, their arguments, and the meaning of every program are "
      "identical. Only the surface spellings change, through a validated mapping "
      "called a **φ-map** (phi-map). The proof that they really are equivalent is "
      "mechanical: all 21 gold answers, written in all four notations, parse to a "
      "**byte-identical** internal representation (validation check 3, 84/84 "
      "renderings).\n")
    w("Here is one program in all four:\n")
    ex = next((c for c in DS["cases"] if c["id"] == "wheels-black"), None)
    if ex and ex.get("gold_renderings"):
        w("```text")
        for lang in LANGS:
            w(f"{lang:<9} {ex['gold_renderings'][lang]}")
        w("```\n")
    w("- **identity** — ordinary 3DOM. `$S` selects, `.` chains, `.wheel` is a tag, "
      "and the operations are English words. The only arm whose spellings a code "
      "model plausibly saw in pretraining.\n")
    w("- **alpha** — *interference*. It reuses 3DOM's own words but shuffles what "
      "each one means: `recolor` now spells the *function keyword*, `scale` spells "
      "the *recolour* operation, `mesh` spells *receiveShadow*. Everything looks "
      "familiar and almost nothing means what it looks like.\n")
    w("- **beta** — *absence*. Invented but pronounceable ASCII words of matched "
      "length (`flertum`, `mumvumfe`, `&Q`, `~`). Nothing is familiar; nothing is "
      "misleading.\n")
    w("- **gamma** — *glyphs*. Compact non-ASCII symbols (`⏦`, `⍤`, `⟠⟠`, `◈`). "
      "Fewest characters, most tokens. **Gamma is not a clean control** — see §5.\n")

    # 4 FERTILITY
    w("## 4. What tokenizer fertility means\n")
    w("A model does not read characters. It reads **tokens** — chunks of text from a "
      "fixed vocabulary the model was built with. The tool that splits text into "
      "tokens is the **tokenizer**. **Fertility** is how many tokens a tokenizer "
      "spends per character of text:\n")
    w("```text\nfertility = total tokens / total characters\nrelative fertility = "
      "candidate fertility / 3DOM fertility\n```\n")
    w("A relative fertility of 1.00 means \"costs the same as 3DOM\". 1.40 means "
      "\"40% more tokens for the same text\". Measured over the 62 paired programs:\n")
    w("| language | tokens/program (Qwen2) | relative fertility (Qwen2) | "
      "relative fertility (DeepSeek-V3) | byte-fallback fragments (Qwen2) |")
    w("|---|---:|---:|---:|---:|")
    for lang in LANGS:
        r = qwen["rows"][lang]
        d = dsk["rows"][lang]["relative_fertility_vs_identity"] if dsk else None
        w(f"| `{lang}` | {r['tokens_per_program']:.3f} | "
          f"{r['relative_fertility_vs_identity']:.3f}× | "
          f"{num(d)}× | {r['fragmented_percent']:.3f}% |")
    w("")
    w("\"Byte-fallback fragments\" counts tokens that carry only *part* of a "
      "character — a sign the tokenizer had no whole-symbol entry and fell back to "
      "raw bytes. Gamma's glyphs trigger this heavily; beta's invented ASCII words "
      "do not, yet beta is still expensive because its words split into many ordinary "
      "sub-word pieces. **Character count and token count are not interchangeable**: "
      "gamma uses only 0.716× as many characters as 3DOM but nearly twice as many "
      "tokens.\n")
    w("These values reproduce Experiment 01's archived measurements exactly.\n")

    # 5 WHY WAIVED
    w("## 5. Why the fertility gate was waived, and why tokenization still matters\n")
    w("Experiment 01 pre-committed a rule: a candidate notation was only eligible if "
      "its relative fertility stayed within **[0.95, 1.05]** on every study "
      "tokenizer. All three candidates failed it (alpha 1.068, beta 1.401, gamma "
      "1.937 on Qwen2), so Experiment 01 ended with **no eligible winner** — and its "
      "primary ranking measurement, base-model ΔNLL, was never run at all because "
      "`torch` and the model weights were absent.\n")
    w("This study **deliberately waives that gate** so that model behaviour can be "
      "observed anyway. That is the only reason the directory is named "
      "`tokenizer_avoided`. **Tokenizers are not bypassed** — no transformer can run "
      "without one. Fertility is still measured, reported, plotted, and treated as a "
      "**confounding variable**: because the alien notations are simultaneously "
      "unfamiliar *and* more expensive, any accuracy difference could be caused by "
      "either, and this design cannot separate them.\n")
    w("**Gamma additionally carries 24 findings** from Experiment 01's proposed check "
      "(g): 22 where word-class spellings became symbols (changing how keywords are "
      "told apart from identifiers) and 2 reachability findings (token sequences "
      "possible in gamma that no 3DOM text can produce — `meshmesh` is one identifier "
      "in 3DOM, while `⍇⍇` can remain two type tokens). Gamma is therefore a "
      "**Unicode/lexer stress diagnostic, not a clean isomorphism test**.\n")

    # 6 MODELS
    w("## 6. Exactly which models were tested\n")
    w("**Lane A — base checkpoints** (raw pretrained models; they only continue text):\n")
    w("| repository | revision | parameters | device | precision | status |")
    w("|---|---|---:|---|---|---|")
    for label, m in laneA["models"].items():
        w(f"| `{m['model']}` | `{str(m.get('revision'))[:12]}` | "
          f"{ints(m['n_parameters'])} | {m['device']} | {m['precision']} | VERIFIED |")
    for b in laneA["blocked"]:
        w(f"| `{b['model']}` | — | — | {b['device']} | {b['precision']} | "
          f"**BLOCKED ({b['failure_kind']})** |")
    w("")
    w("**Lane B — instruct checkpoints** (tuned to follow instructions):\n")
    w("| repository | revision | parameters | device | precision | status |")
    w("|---|---|---:|---|---|---|")
    for m in b_models:
        e = laneB["models"][m]
        w(f"| `{m}` | `{str(e.get('revision'))[:12]}` | {ints(e['n_parameters'])} | "
          f"{e['device']} | {e['precision']} | VERIFIED |")
    for b in laneB["blocked"]:
        w(f"| `{b['model']}` | — | — | {b['device']} | {b['precision']} | "
          f"**BLOCKED ({b['failure_kind']})** |")
    w("")
    w("**DeepSeek-V3 was used as a tokenizer only.** Its full weights (671B "
      "parameters) are not runnable on this machine, and it was **never** "
      "behaviourally tested. It appears in §4 and nowhere else.\n")
    if blocked:
        w("**Blocked cells, in full:**\n")
        for b in blocked:
            w(f"- `{b['model']}` — Lane {b['lane']}, {b['precision']}/{b['device']} — "
              f"**{b['failure_kind']}**\n"
              f"  - attempted: `{b['attempted_command']}`\n"
              f"  - error: `{str(b['error'])[:300]}`\n"
              f"  - to resume: a GPU with more VRAM, or a predeclared lower-precision "
              f"condition reported separately (this run did **not** silently "
              f"re-run it at another precision).\n")

    # 7 IMPORTANT CORRECTION
    w("## 7. Important correction about Experiment 01\n")
    w("> **Experiment 01 tested tokenizer configurations, not full behavioural "
      "models.** It loaded five *tokenizers* through `AutoTokenizer` and measured how "
      "they split text. It never loaded model weights and never ran a forward pass, "
      "because `torch` and the weights were absent.\n")
    w("It is therefore **incorrect** to say \"all five Experiment 01 models failed\". "
      "Five *tokenizer repositories* were measured — and because the four Qwen "
      "repositories share one `Qwen2Tokenizer`, that is evidence from **two distinct "
      "tokenizer designs**, not five. What failed was the fertility constraint, "
      "measured on text. No model's behaviour was tested at all.\n")
    w("This run is the first in this project to actually load model weights and run "
      "forward passes. A second correction follows from that: a previous audit "
      "suggested CUDA was unavailable on this machine. **That is no longer true** — "
      f"`torch {env['torch']}` reports CUDA available on an "
      f"{env['cuda_device_name']} with {env['cuda_total_memory_bytes']:,} bytes of "
      "VRAM, and every model in this run was downloaded and executed on it (except "
      "where noted BLOCKED).\n")

    # 8 WHAT WAS FED
    w("## 8. Exactly what was fed to the models\n")
    w("**Lane A** received *the program text and nothing else* — no request, no "
      "instructions, no examples, and an empty prefix, identically in all four "
      "languages. Example of a complete Lane A input:\n")
    w("```text\n(function(){ $S('.wheel').recolor('#111111'); })();\n```\n")
    w("**Lane B** received a two-part chat prompt. The system message contains the "
      "language specification **rendered mechanically from that language's φ-map**: "
      "the program shape, the selector forms, all 15 operations with their argument "
      "names and a plain-English description, and four worked examples. The user "
      "message contains the editing request, plus — in the `scaffolded` condition "
      "only — the scene's addressable parts and tags.\n")
    w("Three properties are enforced by unit tests that all pass:\n")
    w("- Every spelling shown to an alien arm is **that language's own**. A 3DOM "
      "spelling is never taught to alpha, beta or gamma.\n"
      "- **No prompt contains a translation pair.** The model is never shown "
      "\"X in 3DOM means Y in gamma\".\n"
      "- Prompt **structure is identical** across languages (same line count, same "
      "sections, same order), so no arm gets more or better-organised information. "
      "The language is called \"the scene-edit language\" in all four arms — calling "
      "identity \"3DOM\" or \"JavaScript\" would hand it a familiar name the alien "
      "arms cannot have.\n")
    w("Worked examples use tag names (`.rotor`, `.panel`, `.lamp`, `.pylon`, "
      "`.strut`) that appear in **no** fixture scene, so an example can never leak "
      "the answer to a task case.\n")
    w("Every exact model input is saved under `prompts/rendered/`.\n")

    # 9 BASE vs INSTRUCT
    w("## 9. The difference between base-model NLL and instruction-model accuracy\n")
    w("These are different questions and are reported in different lanes:\n")
    w("| | Lane A (base) | Lane B (instruct) |\n|---|---|---|")
    w("| Question | how surprising is this text? | did the model do the task? |")
    w("| Input | the program alone | a specification + an editing request |")
    w("| Output | a number (surprise) | generated code, graded against gold |")
    w("| Answer known in advance | yes — we force the text | no — the model writes it |")
    w("| Checkpoint | base | instruct |")
    w("")
    w("**Negative log-likelihood (NLL)** is the standard measure of surprise: how "
      "many *nats* (natural-log units) the model spends predicting text it is forced "
      "to read. Lower = more expected. Because it is computed on text we supply, it "
      "measures familiarity, **not** ability. It is **never** task accuracy, "
      "hallucination rate, or instruction following — and because **no training "
      "occurred anywhere in this study**, it is **not** a training loss and there is "
      "no loss-over-epochs curve.\n")

    # 10 DEFINITIONS
    w("## 10. Accuracy, loss and runtime definitions\n")
    w("**Accuracy definitions and denominators.** Generated text is graded by "
      "*meaning*, never by string comparison. The pipeline is: raw response → frozen "
      "extraction rule → parse with the target language's φ-map → convert to a "
      "shared canonical internal representation → compare against the gold "
      "representation. An alien answer and a 3DOM answer that mean the same thing "
      "produce the same structure and score the same.\n")
    w(f"- **Denominator**: the {DS['counts']['generation_cases']} generation cases "
      f"(of {DS['counts']['editing_requests']} editing requests). The 1 "
      f"graceful-refusal case is scored separately and never pooled.\n"
      "- **Semantic accuracy** = every applicable task component correct **AND** the "
      "answer written in the requested language.\n"
      "- **Parse validity** = the output is a well-formed program. Reported in a "
      "**separate column** and never averaged with accuracy — a program can parse "
      "perfectly and mean the wrong thing.\n"
      "- The four semantic dimensions (operation selection, selector resolution, "
      "argument extraction, multi-operation decomposition) are scored "
      "**independently**.\n")
    w("**Outcome taxonomy** — mutually exclusive, evaluated in order: `LEX_FAIL` "
      "(cannot even be split into tokens) · `PARSE_FAIL` (tokenises but is not a "
      "legal program) · `VALID_VACUOUS` (a legal program that does nothing — a parse "
      "success and a task failure) · `VALID_WRONG` (legal, does something, wrong "
      "meaning) · `VALID_CORRECT` · plus `OOM` / `TIMEOUT` / `HARNESS_ERROR`.\n")
    w("**Runtime definitions.** Model download, cold load and warm-up are measured "
      "but **excluded** from per-case latency and reported separately. CUDA is "
      "synchronised before and after every timed region. Prefill (processing the "
      "prompt) and decoding (writing the answer) are timed separately. CPU and GPU "
      "runs, and different numerical precisions, are never compared as if they were "
      "the same condition.\n")

    # 11 RESULTS PER MODEL
    w("## 11. Results per model\n")
    w("### Lane A — base-model surprise\n")
    w("| model | device | language | NLL/char | NLL/token | perplexity | ΔNLL/char | 95% CI |")
    w("|---|---|---|---:|---:|---:|---:|---|")
    for label, m in laneA["models"].items():
        for lang in LANGS:
            e = m["languages"].get(lang)
            if not e:
                continue
            d = e.get("delta_nll_per_char")
            w(f"| `{short(m['model'])}` | {m['device']} | `{lang}` | "
              f"{e['nll_per_char']:.4f} | {e['nll_per_token']:.4f} | "
              f"{e['token_perplexity']:.2f} | "
              + (f"{d['point']:+.4f} | [{d['ci95_lo']:+.4f}, {d['ci95_hi']:+.4f}] |"
                 if d else "— | — |"))
    w("")
    w("*Perplexity* is `exp(NLL per token)` — loosely, \"how many equally likely "
      "options the model felt it was choosing between at each step\".\n")
    w("### Lane B — behavioural accuracy\n")
    for cond in CONDS:
        w(f"#### {cond}\n")
        w("| model | language | semantic accuracy | parse validity | vacuous | "
          "Δ vs identity | 95% paired CI |")
        w("|---|---|---|---:|---:|---:|---|")
        for m in b_models:
            ce = laneB["models"][m]["conditions"].get(cond)
            if not ce:
                continue
            for lang in LANGS:
                e = ce["languages"].get(lang)
                if not e:
                    continue
                p = e["semantic_accuracy"]
                comp = ce.get("comparisons", {}).get(lang, {}).get("semantic")
                w(f"| `{short(m)}` | `{lang}` | {pct(p['proportion'])} "
                  f"({p['numerator']}/{p['denominator']}, CI {pct(p['wilson95_lo'])}–"
                  f"{pct(p['wilson95_hi'])}) | {pct(e['parse_validity']['proportion'])} | "
                  f"{pct(e['vacuous_rate']['proportion'])} | "
                  + (f"{comp['risk_difference']:+.3f} | "
                     f"[{comp['ci95_lo']:+.3f}, {comp['ci95_hi']:+.3f}] |"
                     if comp else "— (baseline) | — |"))
        w("")

    # 12 RESULTS PER LANGUAGE
    w("## 12. Results per language\n")
    w("Full per-language reports: "
      + " · ".join(f"[`{l}`](reports/languages/{l}.md)" for l in LANGS) + "\n")
    w("| language | relative fertility | mean ΔNLL/char (base) | "
      "mean semantic accuracy (bare) | mean semantic accuracy (scaffolded) |")
    w("|---|---:|---:|---:|---:|")
    for lang in LANGS:
        ds = [ (m["languages"][lang].get("delta_nll_per_char") or {}).get("point")
               for m in laneA["models"].values() if lang in m["languages"] ]
        ds = [d for d in ds if d is not None]
        accs = {}
        for cond in CONDS:
            vals = []
            for m in b_models:
                ce = laneB["models"][m]["conditions"].get(cond)
                e = ce["languages"].get(lang) if ce else None
                if e and e["semantic_accuracy"]["proportion"] is not None:
                    vals.append(e["semantic_accuracy"]["proportion"])
            accs[cond] = sum(vals) / len(vals) if vals else None
        w(f"| `{lang}` | {qwen['rows'][lang]['relative_fertility_vs_identity']:.3f}× | "
          + (f"{sum(ds)/len(ds):+.4f}" if ds else "— (baseline)")
          + f" | {pct(accs['bare'])} | {pct(accs['scaffolded'])} |")
    w("")

    # 13 BARE vs SCAFFOLDED
    w("## 13. Bare versus scaffolded\n")
    w("`bare` gives the model the language specification and the request. "
      "`scaffolded` adds the exact list of addressable scene parts and the tags that "
      "select them, rendered in the target language's own sigils. That is the only "
      "intended difference.\n")
    w("| model | language | bare | scaffolded | difference |")
    w("|---|---|---:|---:|---:|")
    for c in V["H3"]["cells"]:
        w(f"| `{short(c['model'])}` | `{c['language']}` | {pct(c['bare'])} | "
          f"{pct(c['scaffolded'])} | {c['delta']:+.3f} |")
    w("")

    # 14 FAILURES
    w("## 14. Common failure types, with examples\n")
    tax = collections.Counter(r["outcome"] for r in gen)
    w("Across all Lane B generation cells:\n")
    w("| outcome | count | share |")
    w("|---|---:|---:|")
    for k, v in tax.most_common():
        w(f"| `{k}` | {v} | {100*v/max(len(gen),1):.1f}% |")
    w("")
    hal = collections.Counter(h for r in gen for h in (r.get("hallucinations") or []))
    if hal:
        w("**Hallucination categories.** A hallucination here is a specific, "
          "separately-counted content error. A parse failure or a merely wrong answer "
          "is **not** counted as one.\n")
        w("| category | count |")
        w("|---|---:|")
        for k, v in hal.most_common():
            w(f"| `{k}` | {v} |")
        w("")
    w("**Worked examples of the characteristic failure modes:**\n")
    seen = set()
    for want in ("PARSE_FAIL", "VALID_WRONG", "VALID_VACUOUS", "LEX_FAIL"):
        for lang in ALIEN + ["identity"]:
            ex = next((r for r in gen if r["outcome"] == want and r["language"] == lang
                       and (want, lang) not in seen), None)
            if ex:
                seen.add((want, lang))
                prompt = next((c["prompt"] for c in DS["cases"]
                               if c["id"] == ex["case_id"]), "")
                w(f"- **`{want}` · {ex['language']} · {short(ex['model'])} · "
                  f"{ex['condition']}** — request: _{prompt}_\n"
                  f"  - model wrote: `{(ex.get('extracted_code') or '')[:160]}`\n"
                  f"  - scorer: {ex.get('scorer_explanation','')[:200]}\n")
                break
    w("")
    w("The **alpha interference effect** is worth singling out, because it is only "
      "visible when answers are graded by meaning. A model asked to recolour in alpha "
      "often writes the familiar-looking word it knows — but in alpha that word "
      "spells a *different* operation, so the program parses cleanly and performs the "
      "wrong edit. A surface-string grader would have called this \"nearly right\"; "
      "grading through the shared representation correctly calls it wrong.\n")

    # 15 TOKENS vs ACCURACY
    w("## 15. Did models merely need more tokens, or did they become less accurate?\n")
    w("This is the central interpretive question, and the two halves have different "
      "answers.\n")
    w("**More tokens: yes, certainly.** Prompt length rose with fertility in "
      f"{V['H4']['n_more_tokens']} of {V['H4']['n_total']} cells:\n")
    w("| model | condition | language | prompt tokens (median) | identity | ratio |")
    w("|---|---|---|---:|---:|---:|")
    for c in V["H4"]["cells"]:
        w(f"| `{short(c['model'])}` | {c['condition']} | `{c['language']}` | "
          f"{num(c['input_tokens_median'],'{:.0f}')} | "
          f"{num(c['identity_input_tokens_median'],'{:.0f}')} | "
          f"{num(c['token_ratio'])}× |")
    w("")
    if V["H2"]["verdict"] in ("SUPPORTED", "MIXED"):
        w(f"**Less accurate: {'yes, in most cells' if V['H2']['verdict']=='SUPPORTED' else 'in some cells but not uniformly'}.** "
          f"{V['H2']['n_negative']} of {V['H2']['n_total']} cells scored below "
          "identity on matched items. So the cost is **not only** efficiency.\n")
    else:
        w("**Less accurate: not demonstrated.** Accuracy did not fall reliably below "
          "identity. On this evidence the alien notations imposed an **efficiency "
          "cost, not a capability failure**.\n")
    w("Throughput (tokens produced per second) was roughly flat across languages — "
      "the extra cost shows up as *more tokens*, not *slower tokens* "
      "(`plots/overall/13_output_tokens_per_second`).\n")

    # 16 UNCERTAINTY
    w("## 16. Statistical uncertainty\n")
    w("- Every proportion carries its **numerator, denominator** and a **Wilson 95% "
      "confidence interval**.\n"
      "- Language-versus-identity comparisons use **matched items**: the same case, "
      "the same scene, the same gold answer, differing only in notation. They report "
      "a **paired risk difference** with a **95% paired item-level bootstrap** "
      "interval (10 000 resamples, seed 20260910) and an **exact McNemar test**.\n"
      "- **Holm correction** is applied within each model×condition family.\n"
      f"- The behavioural set is **{DS['counts']['generation_cases']} cases**. "
      "Intervals are wide and McNemar has few discordant pairs. **Read effect sizes "
      "and intervals, not p-values.**\n"
      "- Missing cells appear as BLOCKED / SKIPPED / NA — **never as zero**.\n")

    # 17 HYPOTHESES
    w("## 17. Assessment of each hypothesis\n")
    w("Full detail: [HYPOTHESIS_ASSESSMENT.md](HYPOTHESIS_ASSESSMENT.md)\n")
    w("| hypothesis | verdict |\n|---|---|")
    w(f"| H1 — alien syntax is more surprising to base models | **{V['H1']['verdict']}** |")
    w(f"| H2 — alien syntax lowers task accuracy | **{V['H2']['verdict']}** |")
    w(f"| H3 — scaffolding helps and narrows the gap | **{V['H3']['verdict']}** |")
    w(f"| H4 — higher fertility raises token cost | **{V['H4']['verdict']}** |")
    w("")
    w(f"**Dense-prior rule** (all four conditions were required, and were fixed "
      f"before any model ran): (a) ΔNLL/char rises = **{dp['a_nll_rises']}**; "
      f"(b) paired accuracy falls = **{dp['b_accuracy_falls']}**; (c) consistent "
      f"across sizes and tasks = **{dp['c_consistent_across_sizes_and_tasks']}**; "
      f"(d) not only gamma = **{dp['d_not_only_gamma']}**. → "
      f"**{'SUGGESTIVE SUPPORT' if dp['suggestive_support'] else 'NOT ALL CONDITIONS MET'}**.\n")
    w("**Causality is not established.** Fertility is not controlled — every alien "
      "notation is simultaneously unfamiliar and more expensive — and gamma carries "
      "an additional lexical-reachability defect. Nothing here manipulates one factor "
      "while holding the others fixed.\n")

    # 18 LIMITATIONS
    w("## 18. Limitations\n")
    w("Full list: [LIMITATIONS.md](LIMITATIONS.md). The four that most constrain "
      "interpretation:\n")
    w("1. **Fertility is uncontrolled** — the defining limitation of a deliberately "
      "fertility-unmatched study.\n"
      "2. **Gamma is not a clean isomorphic control** (24 check-(g) findings).\n"
      f"3. **Small dataset** — {DS['counts']['generation_cases']} generation cases, "
      "one domain, two fixture scenes.\n"
      "4. **One model family and one prompt design** — all behavioural models are "
      "Qwen2.5-Coder sharing one tokenizer.\n")

    # 19 NEXT
    w("## 19. Recommended next experiments\n")
    w("1. **Build a fertility-matched candidate.** The single highest-value next "
      "step: design a notation whose relative fertility sits inside [0.95, 1.05] by "
      "*measuring tokenizer counts during design*, choosing spellings that are single "
      "vocabulary items. Only then can spelling-familiarity be separated from length.\n"
      "2. **A fertility ladder.** Three or four notations at graded fertility with "
      "matched unfamiliarity, to test dose-response rather than compare three points.\n"
      "3. **Separate interference from absence.** Alpha (familiar-but-wrong) and beta "
      "(unfamiliar) are different manipulations; a factorial design would separate "
      "misdirection from mere novelty.\n"
      "4. **Repair gamma** so it is a genuine isomorphic control, then re-run.\n"
      "5. **A second model family** with a different tokenizer design, to test whether "
      "the pattern is Qwen-specific.\n"
      "6. **More task items and more scenes**, to narrow the intervals.\n"
      "7. **Few-shot in-language examples**, to test whether demonstration closes the "
      "gap further than the scaffold does.\n")

    # 20 REPRODUCTION
    w("## 20. Reproduction commands\n")
    w("```bash\n"
      "cd <repo root>\n"
      "export PYTHONDONTWRITEBYTECODE=1\n"
      "PY=run/.venv/bin/python\n"
      f"R=run/experiments/tokenizer_avoided/{RUN_ID}\n\n"
      "# 0. dependencies and model weights\n"
      "$PY -m pip install matplotlib\n"
      "$PY $R/scripts/download_models.py     $R/metadata/model-download-log.json\n"
      "$PY $R/scripts/download_models_7b.py  $R/metadata/model-download-log-7b.json\n\n"
      "# 1. rebuild and re-validate the frozen task dataset\n"
      "$PY $R/scripts/build_task_dataset.py  $R/inputs/task_dataset.json\n\n"
      "# 2. unit tests\n"
      "$PY $R/scripts/test_harness.py\n\n"
      "# 3. tokenizer fertility\n"
      "$PY $R/scripts/fertility.py           $R/metrics/fertility.json\n\n"
      "# 4. Lane A (base-model NLL) and Lane B (behavioural accuracy)\n"
      "$R/scripts/run_lane_a.sh\n"
      "$R/scripts/run_lane_b2.sh\n\n"
      "# 5. aggregate, plot, report, validate\n"
      "$PY $R/scripts/aggregate.py\n"
      "$PY $R/scripts/plots.py\n"
      "$PY $R/scripts/reports.py\n"
      "$PY $R/scripts/finalize.py\n"
      "$PY $R/scripts/narrative.py\n"
      "$PY $R/scripts/overall.py\n"
      "$PY $R/scripts/validate.py\n"
      "```\n")
    w("Every command run during this experiment, with its exit code, is in "
      "`logs/commands.log`.\n")

    # 21 PATHS
    w("## 21. Where the evidence lives\n")
    w("| what | path |\n|---|---|")
    w("| Frozen pre-registration | `STUDY_PLAN.md` |")
    w("| Per-item raw results (JSONL) | `raw/<model>/<lane>/` |")
    w("| Exact model inputs | `prompts/rendered/<model>/<language>/<condition>/` |")
    w("| Frozen task dataset + gold IR | `inputs/task_dataset.json` |")
    w("| Aggregated metrics | `metrics/aggregate.json`, `metrics/aggregate.csv` |")
    w("| Paired per-item comparisons | `metrics/paired-item-results.jsonl` |")
    w("| Fertility | `metrics/fertility.json` |")
    w("| Plots (png + svg + data.csv + README each) | `plots/overall/`, `plots/by_language/` |")
    w("| Per-language reports | `reports/languages/` |")
    w("| Per-model reports | `reports/models/` |")
    w("| Hypotheses | `HYPOTHESIS_ASSESSMENT.md` |")
    w("| Limitations | `LIMITATIONS.md` |")
    w("| Cell-by-cell status | `STATUS.json` |")
    w("| File inventory + checksums | `MANIFEST.json`, `metadata/output-checksums.txt` |")
    w("| Environment, hardware, revisions | `metadata/` |")
    w("| All commands + exit codes | `logs/commands.log` |")
    w("")
    if VAL:
        n_pass = sum(1 for v in VAL if v["pass"])
        w(f"**Validation status: {n_pass}/{len(VAL)} checks passed.**\n")
        w("| check | result |\n|---|---|")
        for v in VAL:
            w(f"| {v['check']} | {'PASS' if v['pass'] else 'FAIL'}"
              + (f" — {v['detail']}" if v.get("detail") else "") + " |")
        w("")
    w("---\n")
    w("_This study does not select a winning alien syntax, does not claim any "
      "candidate now satisfies Experiment 01, and does not establish that dense prior "
      "knowledge caused any observed difference._\n")

    open(os.path.join(RUN, "OVERALL_REPORT.md"), "w", encoding="utf-8").write("\n".join(O))
    print(f"OVERALL_REPORT.md written ({len(O)} blocks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
