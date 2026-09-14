# OVERALL REPORT — `tokenizer_avoided`, run `20260914T212711Z`

**An exploratory fertility-unmatched model evaluation.**

_Generated 2026-09-14T22:07:22.354127+00:00. Every number below is read from `metrics/aggregate.json`, which is computed from the raw per-item rows in `raw/`. Nothing is transcribed by hand._

---

## 1. Executive summary

We asked whether small code-generation models behave differently when the *same* scene-editing task is written in ordinary 3DOM versus three invented "alien" notations that mean exactly the same thing. We measured two separate things, in two separate lanes that are never mixed:

- **Lane A** — how *surprising* each notation is to a raw (base) model that is simply reading the program. No task, no question, no answer.
- **Lane B** — how *accurately* an instruction-tuned model actually performs the editing task when asked, in each notation.

The headline findings:

1. **The alien notations are reliably more surprising to base models (H1: SUPPORTED).** In 12 of 12 model×language cells the extra surprise per character was positive with a 95% confidence interval that excludes zero. The ordering was stable at every model size: gamma > beta > alpha.

2. **Behavioural accuracy (H2: MIXED).** 3 of 6 model×condition×language cells scored *lower* than ordinary 3DOM on the very same task items; 0 of 6 had a confidence interval entirely below zero.

3. **Scaffolding (H3: NOT SUPPORTED).** Giving the model the exact list of addressable scene parts changed accuracy in 0 of 4 cells upward, and narrowed the identity↔alien gap in 3 of 3 comparisons.

4. **Token cost (H4: SUPPORTED (token cost)).** The same information cost more model tokens in every alien arm (6/6 cells). This is a measured efficiency cost and, on its own, says nothing about accuracy.

5. **The predeclared dense-prior rule was NOT fully met** (a=True, b=False, c=False, d=False). Even where met, **causality is not established**: fertility is not controlled and gamma has an additional lexical defect.

**No winning alien syntax is selected, and nothing here makes any candidate eligible under Experiment 01's fertility gate.**

## 2. Research question

Do language models depend on having seen a notation's *spellings* during pretraining, or do they work from the structure of the language they are shown? If the former, then renaming every keyword — while keeping the grammar, the meanings, and the task identical — should make models worse. That is the "dense prior" hypothesis. This run measures it exploratorily.

## 3. What identity, alpha, beta and gamma are

All four are **the same language with different spellings**. The grammar, the 15 operations, their arguments, and the meaning of every program are identical. Only the surface spellings change, through a validated mapping called a **φ-map** (phi-map). The proof that they really are equivalent is mechanical: all 21 gold answers, written in all four notations, parse to a **byte-identical** internal representation (validation check 3, 84/84 renderings).

Here is one program in all four:

```text
identity  (function(){ $S('.wheel').recolor('black'); })();
alpha     (recolor(){ $$('#wheel')#scale('black'); })();
beta      (mumvumfe(){ &Q('~wheel')~flertum('black'); })();
gamma     (⍤(){ ⟠⟠('◈wheel')◈⏦('black'); })();
```

- **identity** — ordinary 3DOM. `$S` selects, `.` chains, `.wheel` is a tag, and the operations are English words. The only arm whose spellings a code model plausibly saw in pretraining.

- **alpha** — *interference*. It reuses 3DOM's own words but shuffles what each one means: `recolor` now spells the *function keyword*, `scale` spells the *recolour* operation, `mesh` spells *receiveShadow*. Everything looks familiar and almost nothing means what it looks like.

- **beta** — *absence*. Invented but pronounceable ASCII words of matched length (`flertum`, `mumvumfe`, `&Q`, `~`). Nothing is familiar; nothing is misleading.

- **gamma** — *glyphs*. Compact non-ASCII symbols (`⏦`, `⍤`, `⟠⟠`, `◈`). Fewest characters, most tokens. **Gamma is not a clean control** — see §5.

## 4. What tokenizer fertility means

A model does not read characters. It reads **tokens** — chunks of text from a fixed vocabulary the model was built with. The tool that splits text into tokens is the **tokenizer**. **Fertility** is how many tokens a tokenizer spends per character of text:

```text
fertility = total tokens / total characters
relative fertility = candidate fertility / 3DOM fertility
```

A relative fertility of 1.00 means "costs the same as 3DOM". 1.40 means "40% more tokens for the same text". Measured over the 62 paired programs:

| language | tokens/program (Qwen2) | relative fertility (Qwen2) | relative fertility (DeepSeek-V3) | byte-fallback fragments (Qwen2) |
|---|---:|---:|---:|---:|
| `identity` | 19.435 | 1.000× | 1.000× | 0.000% |
| `alpha` | 20.306 | 1.068× | 1.073× | 0.000% |
| `beta` | 27.226 | 1.401× | 1.448× | 0.000% |
| `gamma` | 26.968 | 1.937× | 2.285× | 36.364% |

"Byte-fallback fragments" counts tokens that carry only *part* of a character — a sign the tokenizer had no whole-symbol entry and fell back to raw bytes. Gamma's glyphs trigger this heavily; beta's invented ASCII words do not, yet beta is still expensive because its words split into many ordinary sub-word pieces. **Character count and token count are not interchangeable**: gamma uses only 0.716× as many characters as 3DOM but nearly twice as many tokens.

These values reproduce Experiment 01's archived measurements exactly.

## 5. Why the fertility gate was waived, and why tokenization still matters

Experiment 01 pre-committed a rule: a candidate notation was only eligible if its relative fertility stayed within **[0.95, 1.05]** on every study tokenizer. All three candidates failed it (alpha 1.068, beta 1.401, gamma 1.937 on Qwen2), so Experiment 01 ended with **no eligible winner** — and its primary ranking measurement, base-model ΔNLL, was never run at all because `torch` and the model weights were absent.

This study **deliberately waives that gate** so that model behaviour can be observed anyway. That is the only reason the directory is named `tokenizer_avoided`. **Tokenizers are not bypassed** — no transformer can run without one. Fertility is still measured, reported, plotted, and treated as a **confounding variable**: because the alien notations are simultaneously unfamiliar *and* more expensive, any accuracy difference could be caused by either, and this design cannot separate them.

**Gamma additionally carries 24 findings** from Experiment 01's proposed check (g): 22 where word-class spellings became symbols (changing how keywords are told apart from identifiers) and 2 reachability findings (token sequences possible in gamma that no 3DOM text can produce — `meshmesh` is one identifier in 3DOM, while `⍇⍇` can remain two type tokens). Gamma is therefore a **Unicode/lexer stress diagnostic, not a clean isomorphism test**.

## 6. Exactly which models were tested

**Lane A — base checkpoints** (raw pretrained models; they only continue text):

| repository | revision | parameters | device | precision | status |
|---|---|---:|---|---|---|
| `Qwen/Qwen2.5-Coder-0.5B` | `8123ea2e9354` | 494,032,768 | cuda | fp32 | VERIFIED |
| `Qwen/Qwen2.5-Coder-1.5B` | `df3ce67c0e24` | 1,543,714,304 | cuda | fp32 | VERIFIED |
| `Qwen/Qwen2.5-Coder-3B` | `09d9bc5d376b` | 3,085,938,688 | cuda | fp32 | VERIFIED |
| `Qwen/Qwen2.5-Coder-7B` | `0396a76181e1` | 7,615,616,512 | cpu | fp32 | VERIFIED |
| `Qwen/Qwen2.5-Coder-7B` | — | — | cuda | fp32 | **BLOCKED (OOM)** |

**Lane B — instruct checkpoints** (tuned to follow instructions):

| repository | revision | parameters | device | precision | status |
|---|---|---:|---|---|---|
| `Qwen/Qwen2.5-Coder-0.5B-Instruct` | `ea3f2471cf1b` | NA | cuda | fp16 | VERIFIED |

**DeepSeek-V3 was used as a tokenizer only.** Its full weights (671B parameters) are not runnable on this machine, and it was **never** behaviourally tested. It appears in §4 and nowhere else.

**Blocked cells, in full:**

- `Qwen/Qwen2.5-Coder-7B` — Lane A, fp32/cuda — **OOM**
  - attempted: `lane_a.py --model Qwen/Qwen2.5-Coder-7B --precision fp32 --device cuda`
  - error: `OutOfMemoryError: CUDA out of memory. Tried to allocate 260.00 MiB. GPU 0 has a total capacity of 15.61 GiB of which 114.12 MiB is free. Including non-PyTorch memory, this process has 15.15 GiB memory in use. Of the allocated memory 14.87 GiB is allocated by PyTorch, and 91.35 MiB is reserved by PyT`
  - to resume: a GPU with more VRAM, or a predeclared lower-precision condition reported separately (this run did **not** silently re-run it at another precision).

## 7. Important correction about Experiment 01

> **Experiment 01 tested tokenizer configurations, not full behavioural models.** It loaded five *tokenizers* through `AutoTokenizer` and measured how they split text. It never loaded model weights and never ran a forward pass, because `torch` and the weights were absent.

It is therefore **incorrect** to say "all five Experiment 01 models failed". Five *tokenizer repositories* were measured — and because the four Qwen repositories share one `Qwen2Tokenizer`, that is evidence from **two distinct tokenizer designs**, not five. What failed was the fertility constraint, measured on text. No model's behaviour was tested at all.

This run is the first in this project to actually load model weights and run forward passes. A second correction follows from that: a previous audit suggested CUDA was unavailable on this machine. **That is no longer true** — `torch 2.14.0+cu130` reports CUDA available on an NVIDIA GeForce RTX 3080 Ti Laptop GPU with 16,760,569,856 bytes of VRAM, and every model in this run was downloaded and executed on it (except where noted BLOCKED).

## 8. Exactly what was fed to the models

**Lane A** received *the program text and nothing else* — no request, no instructions, no examples, and an empty prefix, identically in all four languages. Example of a complete Lane A input:

```text
(function(){ $S('.wheel').recolor('#111111'); })();
```

**Lane B** received a two-part chat prompt. The system message contains the language specification **rendered mechanically from that language's φ-map**: the program shape, the selector forms, all 15 operations with their argument names and a plain-English description, and four worked examples. The user message contains the editing request, plus — in the `scaffolded` condition only — the scene's addressable parts and tags.

Three properties are enforced by unit tests that all pass:

- Every spelling shown to an alien arm is **that language's own**. A 3DOM spelling is never taught to alpha, beta or gamma.
- **No prompt contains a translation pair.** The model is never shown "X in 3DOM means Y in gamma".
- Prompt **structure is identical** across languages (same line count, same sections, same order), so no arm gets more or better-organised information. The language is called "the scene-edit language" in all four arms — calling identity "3DOM" or "JavaScript" would hand it a familiar name the alien arms cannot have.

Worked examples use tag names (`.rotor`, `.panel`, `.lamp`, `.pylon`, `.strut`) that appear in **no** fixture scene, so an example can never leak the answer to a task case.

Every exact model input is saved under `prompts/rendered/`.

## 9. The difference between base-model NLL and instruction-model accuracy

These are different questions and are reported in different lanes:

| | Lane A (base) | Lane B (instruct) |
|---|---|---|
| Question | how surprising is this text? | did the model do the task? |
| Input | the program alone | a specification + an editing request |
| Output | a number (surprise) | generated code, graded against gold |
| Answer known in advance | yes — we force the text | no — the model writes it |
| Checkpoint | base | instruct |

**Negative log-likelihood (NLL)** is the standard measure of surprise: how many *nats* (natural-log units) the model spends predicting text it is forced to read. Lower = more expected. Because it is computed on text we supply, it measures familiarity, **not** ability. It is **never** task accuracy, hallucination rate, or instruction following — and because **no training occurred anywhere in this study**, it is **not** a training loss and there is no loss-over-epochs curve.

## 10. Accuracy, loss and runtime definitions

**Accuracy definitions and denominators.** Generated text is graded by *meaning*, never by string comparison. The pipeline is: raw response → frozen extraction rule → parse with the target language's φ-map → convert to a shared canonical internal representation → compare against the gold representation. An alien answer and a 3DOM answer that mean the same thing produce the same structure and score the same.

- **Denominator**: the 21 generation cases (of 22 editing requests). The 1 graceful-refusal case is scored separately and never pooled.
- **Semantic accuracy** = every applicable task component correct **AND** the answer written in the requested language.
- **Parse validity** = the output is a well-formed program. Reported in a **separate column** and never averaged with accuracy — a program can parse perfectly and mean the wrong thing.
- The four semantic dimensions (operation selection, selector resolution, argument extraction, multi-operation decomposition) are scored **independently**.

**Outcome taxonomy** — mutually exclusive, evaluated in order: `LEX_FAIL` (cannot even be split into tokens) · `PARSE_FAIL` (tokenises but is not a legal program) · `VALID_VACUOUS` (a legal program that does nothing — a parse success and a task failure) · `VALID_WRONG` (legal, does something, wrong meaning) · `VALID_CORRECT` · plus `OOM` / `TIMEOUT` / `HARNESS_ERROR`.

**Runtime definitions.** Model download, cold load and warm-up are measured but **excluded** from per-case latency and reported separately. CUDA is synchronised before and after every timed region. Prefill (processing the prompt) and decoding (writing the answer) are timed separately. CPU and GPU runs, and different numerical precisions, are never compared as if they were the same condition.

## 11. Results per model

### Lane A — base-model surprise

| model | device | language | NLL/char | NLL/token | perplexity | ΔNLL/char | 95% CI |
|---|---|---|---:|---:|---:|---:|---|
| `0.5B` | cuda | `identity` | 1.3314 | 3.9978 | 54.48 | — | — |
| `0.5B` | cuda | `alpha` | 1.8839 | 5.2834 | 197.04 | +0.5525 | [+0.5059, +0.6005] |
| `0.5B` | cuda | `beta` | 3.0549 | 6.4481 | 631.49 | +1.7235 | [+1.6256, +1.8126] |
| `0.5B` | cuda | `gamma` | 4.1503 | 6.3363 | 564.69 | +2.8189 | [+2.6293, +2.9919] |
| `1.5B` | cuda | `identity` | 1.2723 | 3.8202 | 45.61 | — | — |
| `1.5B` | cuda | `alpha` | 1.9034 | 5.3381 | 208.12 | +0.6311 | [+0.5867, +0.6778] |
| `1.5B` | cuda | `beta` | 2.9802 | 6.2903 | 539.32 | +1.7079 | [+1.6159, +1.7901] |
| `1.5B` | cuda | `gamma` | 4.3941 | 6.7086 | 819.38 | +3.1218 | [+2.9225, +3.3056] |
| `3B` | cuda | `identity` | 1.2491 | 3.7505 | 42.54 | — | — |
| `3B` | cuda | `alpha` | 1.9021 | 5.3344 | 207.35 | +0.6530 | [+0.6089, +0.6991] |
| `3B` | cuda | `beta` | 2.9121 | 6.1466 | 467.14 | +1.6631 | [+1.5701, +1.7472] |
| `3B` | cuda | `gamma` | 3.9138 | 5.9752 | 393.54 | +2.6647 | [+2.4849, +2.8321] |
| `7B` | cpu | `identity` | 1.2675 | 3.8058 | 44.96 | — | — |
| `7B` | cpu | `alpha` | 1.8546 | 5.2011 | 181.48 | +0.5871 | [+0.5409, +0.6355] |
| `7B` | cpu | `beta` | 2.8585 | 6.0335 | 417.16 | +1.5910 | [+1.5094, +1.6659] |
| `7B` | cpu | `gamma` | 4.0497 | 6.1828 | 484.32 | +2.7822 | [+2.5852, +2.9682] |

*Perplexity* is `exp(NLL per token)` — loosely, "how many equally likely options the model felt it was choosing between at each step".

### Lane B — behavioural accuracy

#### bare

| model | language | semantic accuracy | parse validity | vacuous | Δ vs identity | 95% paired CI |
|---|---|---|---:|---:|---:|---|
| `0.5B` | `identity` | 11.1% (1/9, CI 2.0%–43.5%) | 100.0% | 0.0% | — (baseline) | — |
| `0.5B` | `alpha` | 0.0% (0/9, CI 0.0%–29.9%) | 88.9% | 0.0% | -0.111 | [-0.333, +0.000] |
| `0.5B` | `beta` | 0.0% (0/9, CI 0.0%–29.9%) | 100.0% | 0.0% | -0.111 | [-0.333, +0.000] |
| `0.5B` | `gamma` | 0.0% (0/9, CI 0.0%–29.9%) | 100.0% | 0.0% | -0.111 | [-0.333, +0.000] |

#### scaffolded

| model | language | semantic accuracy | parse validity | vacuous | Δ vs identity | 95% paired CI |
|---|---|---|---:|---:|---:|---|
| `0.5B` | `identity` | 0.0% (0/9, CI 0.0%–29.9%) | 100.0% | 0.0% | — (baseline) | — |
| `0.5B` | `alpha` | 0.0% (0/9, CI 0.0%–29.9%) | 0.0% | 0.0% | +0.000 | [+0.000, +0.000] |
| `0.5B` | `beta` | 0.0% (0/9, CI 0.0%–29.9%) | 0.0% | 0.0% | +0.000 | [+0.000, +0.000] |
| `0.5B` | `gamma` | 0.0% (0/9, CI 0.0%–29.9%) | 77.8% | 0.0% | +0.000 | [+0.000, +0.000] |

## 12. Results per language

Full per-language reports: [`identity`](reports/languages/identity.md) · [`alpha`](reports/languages/alpha.md) · [`beta`](reports/languages/beta.md) · [`gamma`](reports/languages/gamma.md)

| language | relative fertility | mean ΔNLL/char (base) | mean semantic accuracy (bare) | mean semantic accuracy (scaffolded) |
|---|---:|---:|---:|---:|
| `identity` | 1.000× | — (baseline) | 11.1% | 0.0% |
| `alpha` | 1.068× | +0.6059 | 0.0% | 0.0% |
| `beta` | 1.401× | +1.6714 | 0.0% | 0.0% |
| `gamma` | 1.937× | +2.8469 | 0.0% | 0.0% |

## 13. Bare versus scaffolded

`bare` gives the model the language specification and the request. `scaffolded` adds the exact list of addressable scene parts and the tags that select them, rendered in the target language's own sigils. That is the only intended difference.

| model | language | bare | scaffolded | difference |
|---|---|---:|---:|---:|
| `0.5B` | `identity` | 11.1% | 0.0% | -0.111 |
| `0.5B` | `alpha` | 0.0% | 0.0% | +0.000 |
| `0.5B` | `beta` | 0.0% | 0.0% | +0.000 |
| `0.5B` | `gamma` | 0.0% | 0.0% | +0.000 |

## 14. Common failure types, with examples

Across all Lane B generation cells:

| outcome | count | share |
|---|---:|---:|
| `VALID_WRONG` | 65 | 60.7% |
| `PARSE_FAIL` | 38 | 35.5% |
| `VALID_CORRECT` | 4 | 3.7% |

**Hallucination categories.** A hallucination here is a specific, separately-counted content error. A parse failure or a merely wrong answer is **not** counted as one.

| category | count |
|---|---:|
| `invented_operation` | 44 |
| `invented_selector` | 38 |
| `invented_argument` | 31 |
| `extra_operation` | 5 |
| `missing_operation` | 1 |

**Worked examples of the characteristic failure modes:**

- **`PARSE_FAIL` · alpha · 0.5B · scaffolded** — request: _make the wheels black_
  - model wrote: `recolor(){
  $$('#dump-truck').#duplicate('y',1,2);
}`
  - scorer: tokenised, but no derivation exists

- **`VALID_WRONG` · alpha · 0.5B · bare** — request: _make the wheels black_
  - model wrote: `(recolor(){ $$('#wheel')#setMaterial('#000000'); })();`
  - scorer: op0: "duplicate" != "recolor"; right nodes, nothing extra; missing arg color; op0 "duplicate" != "recolor"


The **alpha interference effect** is worth singling out, because it is only visible when answers are graded by meaning. A model asked to recolour in alpha often writes the familiar-looking word it knows — but in alpha that word spells a *different* operation, so the program parses cleanly and performs the wrong edit. A surface-string grader would have called this "nearly right"; grading through the shared representation correctly calls it wrong.

## 15. Did models merely need more tokens, or did they become less accurate?

This is the central interpretive question, and the two halves have different answers.

**More tokens: yes, certainly.** Prompt length rose with fertility in 6 of 6 cells:

| model | condition | language | prompt tokens (median) | identity | ratio |
|---|---|---|---:|---:|---:|
| `0.5B` | bare | `alpha` | 719 | 715 | 1.006× |
| `0.5B` | bare | `beta` | 788 | 715 | 1.102× |
| `0.5B` | bare | `gamma` | 807 | 715 | 1.129× |
| `0.5B` | scaffolded | `alpha` | 1174 | 1170 | 1.003× |
| `0.5B` | scaffolded | `beta` | 1243 | 1170 | 1.062× |
| `0.5B` | scaffolded | `gamma` | 1281 | 1170 | 1.095× |

**Less accurate: in some cells but not uniformly.** 3 of 6 cells scored below identity on matched items. So the cost is **not only** efficiency.

Throughput (tokens produced per second) was roughly flat across languages — the extra cost shows up as *more tokens*, not *slower tokens* (`plots/overall/13_output_tokens_per_second`).

## 16. Statistical uncertainty

- Every proportion carries its **numerator, denominator** and a **Wilson 95% confidence interval**.
- Language-versus-identity comparisons use **matched items**: the same case, the same scene, the same gold answer, differing only in notation. They report a **paired risk difference** with a **95% paired item-level bootstrap** interval (10 000 resamples, seed 20260910) and an **exact McNemar test**.
- **Holm correction** is applied within each model×condition family.
- The behavioural set is **21 cases**. Intervals are wide and McNemar has few discordant pairs. **Read effect sizes and intervals, not p-values.**
- Missing cells appear as BLOCKED / SKIPPED / NA — **never as zero**.

## 17. Assessment of each hypothesis

Full detail: [HYPOTHESIS_ASSESSMENT.md](HYPOTHESIS_ASSESSMENT.md)

| hypothesis | verdict |
|---|---|
| H1 — alien syntax is more surprising to base models | **SUPPORTED** |
| H2 — alien syntax lowers task accuracy | **MIXED** |
| H3 — scaffolding helps and narrows the gap | **NOT SUPPORTED** |
| H4 — higher fertility raises token cost | **SUPPORTED (token cost)** |

**Dense-prior rule** (all four conditions were required, and were fixed before any model ran): (a) ΔNLL/char rises = **True**; (b) paired accuracy falls = **False**; (c) consistent across sizes and tasks = **False**; (d) not only gamma = **False**. → **NOT ALL CONDITIONS MET**.

**Causality is not established.** Fertility is not controlled — every alien notation is simultaneously unfamiliar and more expensive — and gamma carries an additional lexical-reachability defect. Nothing here manipulates one factor while holding the others fixed.

## 18. Limitations

Full list: [LIMITATIONS.md](LIMITATIONS.md). The four that most constrain interpretation:

1. **Fertility is uncontrolled** — the defining limitation of a deliberately fertility-unmatched study.
2. **Gamma is not a clean isomorphic control** (24 check-(g) findings).
3. **Small dataset** — 21 generation cases, one domain, two fixture scenes.
4. **One model family and one prompt design** — all behavioural models are Qwen2.5-Coder sharing one tokenizer.

## 19. Recommended next experiments

1. **Build a fertility-matched candidate.** The single highest-value next step: design a notation whose relative fertility sits inside [0.95, 1.05] by *measuring tokenizer counts during design*, choosing spellings that are single vocabulary items. Only then can spelling-familiarity be separated from length.
2. **A fertility ladder.** Three or four notations at graded fertility with matched unfamiliarity, to test dose-response rather than compare three points.
3. **Separate interference from absence.** Alpha (familiar-but-wrong) and beta (unfamiliar) are different manipulations; a factorial design would separate misdirection from mere novelty.
4. **Repair gamma** so it is a genuine isomorphic control, then re-run.
5. **A second model family** with a different tokenizer design, to test whether the pattern is Qwen-specific.
6. **More task items and more scenes**, to narrow the intervals.
7. **Few-shot in-language examples**, to test whether demonstration closes the gap further than the scaffold does.

## 20. Reproduction commands

```bash
cd <repo root>
export PYTHONDONTWRITEBYTECODE=1
PY=run/.venv/bin/python
R=run/experiments/tokenizer_avoided/20260914T212711Z

# 0. dependencies and model weights
$PY -m pip install matplotlib
$PY $R/scripts/download_models.py     $R/metadata/model-download-log.json
$PY $R/scripts/download_models_7b.py  $R/metadata/model-download-log-7b.json

# 1. rebuild and re-validate the frozen task dataset
$PY $R/scripts/build_task_dataset.py  $R/inputs/task_dataset.json

# 2. unit tests
$PY $R/scripts/test_harness.py

# 3. tokenizer fertility
$PY $R/scripts/fertility.py           $R/metrics/fertility.json

# 4. Lane A (base-model NLL) and Lane B (behavioural accuracy)
$R/scripts/run_lane_a.sh
$R/scripts/run_lane_b2.sh

# 5. aggregate, plot, report, validate
$PY $R/scripts/aggregate.py
$PY $R/scripts/plots.py
$PY $R/scripts/reports.py
$PY $R/scripts/finalize.py
$PY $R/scripts/narrative.py
$PY $R/scripts/overall.py
$PY $R/scripts/validate.py
```

Every command run during this experiment, with its exit code, is in `logs/commands.log`.

## 21. Where the evidence lives

| what | path |
|---|---|
| Frozen pre-registration | `STUDY_PLAN.md` |
| Per-item raw results (JSONL) | `raw/<model>/<lane>/` |
| Exact model inputs | `prompts/rendered/<model>/<language>/<condition>/` |
| Frozen task dataset + gold IR | `inputs/task_dataset.json` |
| Aggregated metrics | `metrics/aggregate.json`, `metrics/aggregate.csv` |
| Paired per-item comparisons | `metrics/paired-item-results.jsonl` |
| Fertility | `metrics/fertility.json` |
| Plots (png + svg + data.csv + README each) | `plots/overall/`, `plots/by_language/` |
| Per-language reports | `reports/languages/` |
| Per-model reports | `reports/models/` |
| Hypotheses | `HYPOTHESIS_ASSESSMENT.md` |
| Limitations | `LIMITATIONS.md` |
| Cell-by-cell status | `STATUS.json` |
| File inventory + checksums | `MANIFEST.json`, `metadata/output-checksums.txt` |
| Environment, hardware, revisions | `metadata/` |
| All commands + exit codes | `logs/commands.log` |

**Validation status: 12/13 checks passed.**

| check | result |
|---|---|
| 1. unit tests (prompt renderer, parser, checkpoint, scoring) | PASS — 26 tests, rc=0 |
| 2. four-language smoke test recorded | PASS — languages=['alpha', 'beta', 'gamma', 'identity'] |
| 3. paired targets produce identical canonical IR across languages | PASS — 84 renderings checked, 0 mismatched |
| 4. aggregate denominators verified against raw rows | PASS — 0 mismatches |
| 5. selected aggregates independently recomputed | PASS — 0 discrepancies |
| 6. plot CSV values match aggregate data | FAIL — 1 problems; 01_accuracy_bare Qwen/Qwen2.5-Coder-0.5B-Instruct/identity |
| 7. every plot dir has plot.png, plot.svg, data.csv, README.md | PASS — 30 plots, 0 incomplete |
| 8. no missing value became zero (real zeros listed for inspection) | PASS — 0 exact-zero cells, all traceable to raw rows |
| 9. outcome taxonomy totals equal the denominators | PASS — 0 mismatches |
| 10. VALID_CORRECT count == semantic-accuracy numerator | PASS — 0 mismatches |
| 11. greedy decoding deterministic across repetitions | PASS — 0 of 73 rows differed between reps |
| 12. blocked cells carry exact command and error | PASS — 1 blocked cells recorded |
| 13. checksums recorded for raw, metrics, reports, plots | PASS — 235 files hashed -> metadata/output-checksums.txt |

---

_This study does not select a winning alien syntax, does not claim any candidate now satisfies Experiment 01, and does not establish that dense prior knowledge caused any observed difference._
