# STUDY_PLAN — `tokenizer_avoided`, run `20260914T212711Z`

**An exploratory fertility-unmatched model evaluation.**

> **Frozen 2026-09-14, before any model forward pass.** Everything from
> "Pre-experiment audit" to "Plot list" below was written and checksummed
> before a single logit was computed. Deviations discovered later appear ONLY
> in the dated *Protocol deviations* section at the end, never by editing the
> text above it.

---

## 0. What this study is, and what it is not

This experiment **deliberately waives** the Experiment 01 token-fertility
eligibility gate (relative fertility ∈ [0.95, 1.05]) so that model behaviour on
`alpha`, `beta` and `gamma` can be observed **anyway**. Tokenizer fertility is
still measured, reported, plotted, and treated as a **confounding variable**.

The directory name `tokenizer_avoided` is a requested label only. **Tokenizers
are not bypassed.** Transformer models cannot run without them. Nothing here is
tokenizer-free, tokenization-matched, confirmatory, or a repair of Experiment 01.

It does **not** select a winning alien syntax, and it cannot make any candidate
eligible under Experiment 01's rule.

---

## 1. Pre-experiment audit (recorded BEFORE any new result existed)

Each known limitation from the work order was checked against the code.

| # | Claim to verify | Finding | Status |
|---|---|---|---|
| A1 | `prior_strength.py` measures base-model likelihood, not task accuracy | **Confirmed.** It teacher-forces a program with `NEUTRAL_PREFIX = ""` and reports NLL/token and NLL/char. There is no task, no prompt, no gold answer anywhere in the file. | VERIFIED |
| A2 | The browser eval harness is not proven alpha/beta/gamma-aware | **Confirmed.** `docs/editor/js/ai/editMatrix.js` hard-codes 3DOM spellings in `parseEmittedOps` (`$S`/`$$`/`Pick`, `ANIM_METHODS = spin,bounce,pulse,…`). Nothing consults a φ-map. | VERIFIED |
| A3 | The browser regex parser must not grade alien output | **Confirmed and obeyed.** `parseEmittedOps` is a JS regex scanner over 3DOM spellings; on gamma input it would return `[]` and score 0 for reasons unrelated to the model. **It is not used anywhere in this study.** | VERIFIED |
| A4 | `strata_runner.js` may use obsolete task names / whole-matrix runtime | **Task names OK, runtime claim CONFIRMED.** Its `TASKS` list (`op-type, selector, arg-extract, labeling, multi-op`) matches the five dimensions. But it times the whole `evalEditMatrix()` call and writes that one number onto every row, so a "per-case" second is really a whole-matrix second. **Not used in this study**; all timing here is measured per case. | VERIFIED |
| A5 | Some fixtures have partial expected fields, not complete gold IR | **Confirmed.** `EDIT_TASK_CASES` carries `opType`/`targetNodes`/`args`/`opCount` but **no gold program**. **Fixed here**: every positive case was given a canonical gold IR, validated (§6). | VERIFIED → RESOLVED |
| A6 | There is no completed alien-syntax instruction-model harness | **Confirmed.** No file in the repo renders a φ-aware prompt or scores a generation through `PhiMap`. **Built here** as `scripts/prompts.py` + `scripts/score.py`. | VERIFIED → BUILT |
| A7 | Experiment 01 ran tokenizer measurements, not behavioural model inference | **Confirmed.** `run/experiments/20260901-233702` loaded five tokenizers via `AutoTokenizer`; `torch` and all model weights were absent, so ΔNLL was never computed and no forward pass occurred. | VERIFIED |
| A8 | CUDA availability (a previous audit suggested it was unavailable) | **REFUTED — this is a change from the earlier audit.** `torch 2.14.0+cu130` reports `cuda_available=True`, RTX 3080 Ti Laptop, 16 760 569 856 bytes VRAM, capability (8,6), driver 595.84. Only tokenizer files were cached; **all weights were downloaded for this run**. | VERIFIED |
| A9 | Task inventory: 22 editing / 13 multi-op / 9 labeling | **All three verified by count**, plus 1 `mergedFail` case (`merged-sheets`) inside the 22. So: 21 generation cases + 1 graceful-refusal case. | VERIFIED |
| A10 | The φ pipeline produces a shared canonical IR across languages | **Verified mechanically.** All four languages parse to byte-identical `content_hash` for all 21 gold programs (§6, test T4). | VERIFIED |
| A11 | Lane A corpus reproducibility | The 62-item parallel positive corpus hashes to `38bbbac1a335d2541594f4a3f11157daadd6c724350ebd0ffba88142da33339d`, **identical to the Experiment 01 archived hash**. | VERIFIED |

**Files inspected:** `alien_syntax/measure/{prior_strength,fertility}.py`,
`alien_syntax/src/{phi,transpiler,canonicalize,generate_corpus}.py`,
`grammar_and_3DOM_client/{tasks,fixture_scene}.py`,
`grammar_and_3DOM_client/SCORING_POLICY.md`, `docs/editor/js/ai/editMatrix.js`,
`evalEditMatrix.md`, `strata_runner.js`, `plot_matrix.py`,
`alien_syntax/reports/CANDIDATE_SELECTION.md`, `run/run.md`,
`run/experiments/20260901-233702/result_summary/why_no_winner.md`.

---

## 2. Hypotheses (predeclared)

| ID | Hypothesis | Primary test |
|---|---|---|
| **H1** | For semantically matched programs, alien languages have **higher NLL/character** than identity under base checkpoints. | Lane A paired ΔNLL/char > 0 with 95% paired-bootstrap CI excluding 0. |
| **H2** | Under information-matched prompts, alien generations **may have lower canonical-IR accuracy** than identity. | Lane B paired risk difference in semantic accuracy vs identity; exact McNemar. |
| **H3** | Language-neutral **scaffolding may improve** accuracy and shrink the identity↔alien gap. | Lane B `scaffolded` − `bare` within each language; and the interaction (gap under bare vs gap under scaffolded). |
| **H4** | Higher tokenizer fertility **increases token count and cost**. Its relation to accuracy is **exploratory and must not be assumed**. | Fertility vs prompt/output tokens and runtime (confirmatory); fertility vs Δaccuracy (**descriptive, non-causal**). |

**Gamma is treated separately throughout.** It carries 24 lexical/reachability
findings (22 `g1`, 2 `g2`) from Experiment 01's proposed check (g) and is **not
a clean isomorphic control**. It is a Unicode/lexer stress diagnostic.

**Dense-prior support rule (predeclared).** Suggestive support requires ALL of:
(a) base ΔNLL/char rises for alien syntax; (b) paired semantic accuracy falls
for the same languages; (c) the pattern is reasonably consistent across model
sizes and tasks; (d) the evidence does **not** come only from gamma. Even then,
causality is **not** established — fertility is uncontrolled and gamma has an
additional lexical defect.

---

## 3. Outcomes

**Primary**
- Lane A: paired **ΔNLL per Unicode character** vs identity.
- Lane B: **canonical semantic accuracy** = `all_components_correct AND
  requested_language_compliance`, over the 21 generation cases.

**Secondary** — NLL/token, NLL/UTF-8 byte, perplexity; parse validity; per-task
accuracy (operation selection, selector resolution, argument extraction,
multi-op decomposition); vacuity rate; nLVP; outcome taxonomy shares;
hallucination categories; prompt/output token counts; fertility; runtime,
throughput, peak RAM/VRAM; bare vs scaffolded; conditional task loss.

**Control** — labeling (language-independent; a negative control, never used as
evidence of a syntax effect).
**Separate family** — graceful refusal (`merged-sheets`), never pooled into
generation accuracy.

---

## 4. Models

Two lanes, never mixed.

**Lane A — base checkpoints (prior strength / LM surprise)**

| Repo | Resolved revision | Role |
|---|---|---|
| `Qwen/Qwen2.5-Coder-0.5B` | `8123ea2e9354afb7ffcc6c8641d1b2f5ecf18301` | primary |
| `Qwen/Qwen2.5-Coder-1.5B` | `df3ce67c0e24480f20468b6ef2894622d69eb73b` | primary |
| `Qwen/Qwen2.5-Coder-3B` | `09d9bc5d376b0cfa0100a0694ea7de7232525803` | primary |
| `Qwen/Qwen2.5-Coder-7B` | `0396a76181e127dfc13e5c5ec48a8cee09938b02` | **sensitivity** (see policy) |

**Lane B — instruct checkpoints (behavioural accuracy)**

| Repo | Resolved revision | Role |
|---|---|---|
| `Qwen/Qwen2.5-Coder-0.5B-Instruct` | resolved at load, recorded per row | primary |
| `Qwen/Qwen2.5-Coder-1.5B-Instruct` | resolved at load, recorded per row | primary |
| `Qwen/Qwen2.5-Coder-3B-Instruct` | resolved at load, recorded per row | primary |
| `Qwen/Qwen2.5-Coder-7B-Instruct` | `c03e6d358207e414f1eca0bb1891e29f1db0e242` | **sensitivity** (see policy) |

**7B policy (predeclared).** 7B is attempted under the **identical** primary
configuration (FP16, CUDA, batch 1, greedy). FP16 weights ≈ 15.2 GB against
16.76 GB VRAM is tight. If it OOMs, that is recorded as an **OOM outcome** — it
is **not** retried at lower precision, and it is **not** silently quantised. Its
timings are **never pooled** with the 0.5B/1.5B/3B primary runs; it is reported
as a separately labelled condition.

**DeepSeek-V3** was used in Experiment 01 as a **tokenizer only**. Its full
weights (671B) are not runnable on this machine. It is included here **only** in
the fertility measurement and is labelled **tokenizer-only / BLOCKED for
behavioural testing**. It is never listed as behaviourally tested.

---

## 5. Languages and support conditions

**Languages:** `identity` (ordinary 3DOM), `alpha`, `beta`, `gamma`.

**Support conditions (Lane B):**
- **`bare`** — mechanically rendered language/API specification + the
  natural-language editing request. **No** dynamic scene-selector list.
- **`scaffolded`** — the same specification and request, **plus** the exact
  addressable-part/selector information (node names, labels, kinds, and the tag
  list), rendered in the target language's sigils.

The **only** intended difference is the predeclared scaffold. No `unassisted`
condition is run in this study.

---

## 6. Task data — frozen dataset

Ported from `docs/editor/js/ai/editMatrix.js` to
`inputs/task_dataset.json`.

**Verified counts:** 22 editing requests · 13 multi-op cases · 9 labeling cases
· 1 graceful-refusal case (`merged-sheets`, inside the 22) · **21 generation
cases**.

Every positive case was given a **canonical gold IR** (absent from
`editMatrix.js`) expressed as a 3DOM program and validated by the real grammar:

- **T1** the gold program parses under identity — PASS (21/21)
- **T2** the gold IR resolves to **exactly** the expected target node set — PASS
- **T3** the gold IR passes every scorer its own case declares — PASS
- **T4** the gold transliterates to alpha/beta/gamma and each **parses back to a
  byte-identical canonical IR** — PASS (21 × 4)
- **T5** grader sanity: a deliberately wrong answer FAILS; the gold PASSES; the
  wildcard `*` FAILS selector resolution (bleed guard) — PASS

`merged-sheets` has **no positive DSL target**; it is
`scoring_family = "graceful_refusal"`, carries `gold_program = null`, and is
scored only as refusal/error handling.

**No case required component-level-only expectations** — all 21 generation cases
carry full gold IR.

**Hashes**
- task dataset body: `b311ffd2dbb039b351178d3a1ecab032e0f72e010a77d69ace981da426bee904`
- Lane A parallel corpus (62 × 4): `38bbbac1a335d2541594f4a3f11157daadd6c724350ebd0ffba88142da33339d`
- all input/script checksums: `metadata/input-checksums.txt`

---

## 7. Prompts

Rendered **mechanically from the target language's PhiMap** by
`scripts/prompts.py`. Nothing is hand-written per language.

**Information-matching rule.** For every role the spec gives (i) the spelling
**this** language uses and (ii) a plain-English description of what that role
means. Descriptions are **identical** across languages; only spellings change.
The language is called "the scene-edit language" in **all four** arms — calling
identity "3DOM" or "JavaScript" would hand it a pretraining-familiar name the
alien arms cannot have.

**Guarantees, enforced by tests (all passing):**
- `taught_spellings(lang)` — the exact set of tokens the spec presents as
  language tokens — equals that language's own φ spellings for every role. A
  3DOM spelling is therefore **never** taught to alpha/beta/gamma.
- No 3DOM symbol sigil appears in any alien example-code line.
- Prompt structure (line count, section order) is **identical** across languages.
- **No side-by-side identity↔alien translation appears in any prompt.**
- Worked examples use class names (`.rotor`, `.panel`, `.upper`, `.lamp`,
  `.pylon`, `.strut`) **absent from every fixture scene**, so an example can
  never hand a model the answer to a task case.

Note: English descriptions necessarily use English words ("rotate", "group")
that coincide with 3DOM spellings. This is unavoidable when meaning must be
conveyed, is **identical in all four arms**, and is itself part of the
phenomenon under study — identity's spellings *are* English words.

Every rendered system prompt, user prompt, chat-template output and model input
is saved under `prompts/rendered/`.

---

## 8. Generation settings (Lane B)

| Setting | Value |
|---|---|
| Sampling | `do_sample=False` — **greedy**, deterministic |
| Batch size | 1 |
| Completions per case | 1 primary |
| `max_new_tokens` | **512**, common to every language |
| Stop / EOS policy | model's own EOS via the chat template; identical across arms |
| Chat template | `tokenizer.apply_chat_template(..., add_generation_prompt=True)`, identical across arms |
| Retries / repair / second attempts | **none** |
| Manual editing of completions | **none** |
| Seed | `20260910` (recorded; greedy decoding is deterministic regardless) |
| Precision | **FP16** on CUDA (predeclared primary) |
| Device | `cuda:0` |
| Language order | **Latin square** over (identity, alpha, beta, gamma), rotated per case index, so warm-cache and thermal effects are not assigned consistently to one language |

**Truncation rule (predeclared).** If truncation is *material*, that is a
protocol deviation and **all four language arms** of the affected
model/condition are re-run at one larger common limit. The limit is **never**
raised for only the language that failed.

---

## 9. Lane A procedure

Teacher-forced causal-LM scoring. **No training occurs; there is no training
loss and no loss-over-epochs curve.**

- Input: **the program string only** — no editing request, no instruction
  prompt.
- Conditioning: `NEUTRAL_PREFIX = ""` for **every** language (BOS + program).
- Alignment: `logits[t]` predicts `ids[t+1]`; the first token is unscored. This
  costs one token per program **identically in every lexicon**, so the paired Δ
  is unaffected.
- Corpus: the existing 62-item paired positive corpus. **Index *i* is the same
  semantic program in identity, alpha, beta and gamma.**
- Precision: **FP32** for Lane A (numerical stability of the NLL sum), CUDA.
  Lane A and Lane B precisions are **never** compared as runtime conditions.

**Reported:** total NLL (nats), NLL/model-token, NLL/Unicode-character,
NLL/UTF-8-byte (diagnostic), token-level perplexity, model tokens/program,
chars/program, UTF-8 bytes/program, paired ΔNLL/char and ΔNLL/token vs identity,
95% paired-bootstrap CIs, NLL-scoring runtime.

**NLL/character is primary.** NLL/token is **diagnostic only**, because token
boundaries differ across languages.

This is **never** called task accuracy, hallucination rate, instruction
following, or training loss.

---

## 10. Scoring (Lane B)

**Frozen flow:** raw response → frozen extraction → parse with the **target
language's PhiMap** → canonical shared IR → score against canonical gold.

Surface-string equality is **never** used. The browser's identity-only JS regex
parser is **never** used.

**Extraction rule (frozen, `scripts/extract.py`):** E1 first fenced block → E2
otherwise the first line containing the language's selector-entry spelling
through the last line containing `)();` → E3 otherwise the whole response.
Extraction **never repairs**. The complete raw response is preserved, and both
raw-response compliance and extracted-code validity are reported.

**Per-case columns retained:** raw output present · requested-language
compliance · lexical validity · parse validity · schema validity · valid but
vacuous · canonical-IR exact match · operation correct · resolved selector/node
correct · arguments correct · multi-op decomposition correct · labeling correct
(where applicable) · all-applicable-components correct · LVP tokens · nLVP ·
truncation · timeout · OOM · error category · scorer explanation.

**Mutually exclusive top-level outcome taxonomy:** `LEX_FAIL`, `PARSE_FAIL`,
`VALID_VACUOUS`, `VALID_WRONG`, `VALID_CORRECT`, `TIMEOUT`, `OOM`,
`HARNESS_ERROR`.

Parse validity and semantic correctness are **never averaged** into one score.

**Semantic correctness** = all applicable components correct **AND** the answer
was written in the language that was asked for. A 3DOM answer in the gamma arm
is not a gamma success.

**Hallucination** is defined operationally and broken out as: invented
operation · invented selector/scene entity · invented argument · wrong-language
spelling · extra operation · missing operation · unsupported prose instead of
code. **A parse failure or a wrong answer is not, by itself, a hallucination.**

---

## 11. Conditional task loss (secondary)

Using the **Instruct** models: condition on the exact chat prompt, teacher-force
the **frozen canonical gold completion** for that language, mask prompt tokens,
and compute loss over target-completion tokens only. Reported **separately** from
Lane A — it answers a different question and depends on the chosen reference
serialisation.

---

## 12. Runtime measurement

Recorded separately: dependency/model **download** time · **cold model-load**
time · **warm-up** time · tokenization time · prompt-prefill time · decoding
time · end-to-end per-case time · NLL-scoring time · input tokens · output
tokens · output tokens/second · peak process RAM · peak allocated/reserved VRAM
· device · precision.

- `torch.cuda.synchronize()` **before and after** every GPU timing region.
- Download, model loading and warm-up are **excluded** from per-case latency and
  **reported separately**.
- **At least one excluded warm-up per model.**
- **Three timing repetitions per case** for Lane B, reporting **median and IQR**.
  If three are infeasible, one is used and the limitation is stated — variability
  is **never manufactured**.
- CPU/GPU and FP32/FP16/8-bit/4-bit runtimes are **never** compared as if they
  were the same condition.

---

## 13. Resource policy

One model at a time · `.eval()` · `torch.inference_mode()` · batch size 1 ·
memory released between models (`del`, `gc.collect()`, `empty_cache()`,
`reset_peak_memory_stats()`).

Primary GPU precision is **FP16** (predeclared). **No silent quantisation after
OOM.** If a model OOMs, the cell is recorded `OOM` with the exact error.

Dependencies are installed **only** into the project venv `run/.venv`
(`matplotlib` was added for plotting); never global Python, never `sudo`.

---

## 14. Stopping rules

- A model that fails to load is **BLOCKED**; every other model continues.
- A case that raises inside the harness is `HARNESS_ERROR` and the run continues.
- A cell that OOMs is `OOM`; the remaining cells for that model are still
  attempted, and the run continues to the next model.
- **The run never stops after the first failed model.**
- No cell is retried with changed settings. A changed configuration is a **new,
  separately labelled condition**.

---

## 15. Statistics

- **Proportions:** numerator, denominator, percentage, **Wilson 95% CI**.
- **Language vs identity:** matched items → **paired risk difference**, **95%
  paired-bootstrap interval**, and **exact McNemar** (binomial on discordant
  pairs) where applicable.
- **Bootstrap:** **10 000** paired **item-level** resamples, seed **`20260910`**.
  Lane A resamples **paired program indices**, not individual tokens, and
  recomputes the same ratio-of-totals estimand as the point estimate.
- **Multiplicity:** **Holm** correction within each declared model/support
  family across the task-family tests.
- **NLL and latency:** paired item differences with paired bootstrap intervals;
  latency prioritises **median and IQR/p95**.
- Missing cells are shown as **BLOCKED / SKIPPED / ERROR / NA — never zero**.
- The behavioural dataset is small (21 generation cases): **effect sizes and
  intervals are emphasised over p-values**.

---

## 16. Handling of failure modes

| Situation | Handling |
|---|---|
| OOM | outcome `OOM`, exact error recorded, no retry at other precision |
| Truncation (hit `max_new_tokens`) | `truncated=1` recorded; if material, protocol deviation + re-run **all four** language arms at one larger common limit |
| Malformed output | scored honestly as `LEX_FAIL` / `PARSE_FAIL`; **never repaired** |
| Missing data | `NA` in tables and plots; **never imputed, never zero-filled** |
| Model load failure | `BLOCKED` with exact command and error |

---

## 17. Plot list (predeclared)

1. Accuracy by language and model, with CIs · 2. Paired semantic-accuracy
difference from identity · 3. Per-task accuracy heatmap · 4. Parse validity vs
semantic correctness · 5. Stacked failure/error taxonomy · 6. NLL/char by model
and language · 7. NLL/token by model and language · 8. Paired ΔNLL/char with CIs
· 9. Model-size scaling curves · 10. Median and p95 end-to-end runtime ·
11. Prefill and decoding runtime · 12. Input/output token counts · 13. Output
tokens/second · 14. Peak RAM and VRAM · 15. Fertility vs semantic-accuracy
difference · 16. Fertility vs runtime · 17. Bare vs scaffolded accuracy
difference · 18. nLVP distributions for invalid generations.

Every plot directory contains `plot.png`, `plot.svg`, `data.csv` and a
`README.md` giving axes, denominator, uncertainty interval and result. **Every
chart is generated from its own saved `data.csv`**; no value is transcribed by
hand. Fertility-vs-performance plots are marked **descriptive and non-causal**.

---

## 18. Result key (checkpointing)

`model | revision | tokenizer_revision | lane | language | condition | case_id |
seed | precision | device | prompt_hash`

Checkpoint after **every** completed item, append-only JSONL with `fsync`. On
resume a row counts as done only if it is a complete JSON object carrying its
own `result_key`; a truncated final line is ignored and the cell re-runs. Every
aggregate is reproducible from the raw rows.

---

## 19. Forbidden conclusions (binding on the reports)

Never concluded: that the experiment *proves* dense prior knowledge caused the
failures · that fertility *confirms* hallucination · that a model "cannot
understand" alien syntax · that "all five Experiment 01 models failed" · that
gamma is isomorphic to 3DOM · that candidates now satisfy Experiment 01 · that a
winner has been established.

High fertility demonstrates **increased token cost**. Whether accuracy degrades
is a **separate measurement**. If only token count and runtime worsen while
accuracy holds, the evidence supports an **efficiency cost, not a capability
failure**.

---

## Protocol deviations

*(Appended only after inference began. Nothing above this line was edited.)*

### 2026-09-14 — D1: timing repetitions reduced from 3 to 1 for 3B and 7B

**Frozen plan said:** three timing repetitions per case, reporting median and IQR.

**What changed:** 3 repetitions are kept for `0.5B-Instruct` and `1.5B-Instruct`.
`3B-Instruct` and `7B-Instruct` run with **one** repetition.

**Why:** at three repetitions the full Lane B matrix projected to ~5.8 hours of
wall time, dominated by cases that run to the `max_new_tokens` cap. The frozen
plan already permits this fallback ("If three are infeasible, use one and state
the limitation — do not manufacture variability").

**Why it does not affect accuracy:** greedy decoding was **verified
deterministic** — validation check 11 found 0 of 73 checked rows whose generated
text differed across repetitions. Repetitions therefore measure timing jitter
only; every accuracy, parse-validity and taxonomy number is unchanged.

**Consequence, stated plainly:** end-to-end latency for `3B-Instruct` and
`7B-Instruct` is a **single-shot measurement with no IQR**. It is reported as
such and is never presented as a median-of-three. The repetition count is never
mixed *within* a model: `0.5B-Instruct` resumed at the same reps=3 it began with.

### 2026-09-14 — D2: truncation at `max_new_tokens = 512`

**Frozen plan said:** if truncation is material, declare a deviation and re-run
**all four** language arms of the affected model/condition at one larger common
limit.

**Observed:** a non-trivial share of `0.5B-Instruct` generations reached the
512-token cap, concentrated in `beta` and `gamma`.

**Diagnosis (evidence, not assertion):** inspection of the truncated responses
shows they are **task abandonment, not answer-length pressure**. The model stops
writing the target language and emits unrelated Python — e.g. a `scene = {...}`
dictionary and a table of `lambda`s transcribing the specification. The correct
answer in every language is ~20-60 model tokens, so 512 is roughly 10-25x the
required length and is not the binding constraint on correctness.

**Action:** the limit is **not** raised for the primary matrix. Instead the
claim above is tested empirically in a separately labelled sensitivity condition
(`maxnew1536`) that re-runs the affected cases **in all four languages** at a
larger common limit. Its result is reported separately and is never pooled with
the primary runs. Truncation rates are reported per language throughout.

**RESULT (2026-09-14, after the sensitivity run).** `0.5B-Instruct`, both
conditions, all four languages, `max_new_tokens = 1536`
(`raw/Qwen__Qwen2.5-Coder-0.5B-Instruct/lane_b/gen_maxnew1536.jsonl`):

| condition | language | truncated @512 | truncated @1536 | correct @512 | correct @1536 |
|---|---|---:|---:|---:|---:|
| bare | identity | 0 | 0 | 3 | 3 |
| bare | alpha | 0 | 0 | 0 | 0 |
| bare | beta | 0 | 0 | 1 | 1 |
| bare | gamma | 0 | 0 | 0 | 0 |
| scaffolded | identity | 2 | 0 | 1 | 1 |
| scaffolded | alpha | 5 | 5 | 0 | 0 |
| scaffolded | beta | 19 | 3 | 0 | 0 |
| scaffolded | gamma | 4 | 4 | 0 | 0 |

**Of the 30 cases that truncated at 512, 0 became `VALID_CORRECT` at 1536**, and
semantic accuracy is **identical in every cell**. Tripling the budget let beta's
scaffolded generations terminate (19 truncations to 3) without producing a single
additional correct answer.

**Conclusion, by the interpretation rule fixed in advance:** the 512-token limit
was **not** the binding constraint. The primary matrix **stands unchanged**, and
truncation is reported per language as a failure mode in its own right rather
than as a measurement artefact.

