# `beta` — language report

_Run `20260914T212711Z` · an exploratory fertility-unmatched model evaluation._

## 1. What this language changes

**The absence condition — pronounceable invented words.** Beta replaces each spelling with an ASCII pseudo-word of deliberately matched length and camelCase shape (`flertum` for recolour, `mumvumfe` for the function keyword, `&Q` for the selector entry, `~` for the class sigil). Character length matches 3DOM almost exactly, but the invented words are not single vocabulary units, so they fragment into more ordinary sub-word pieces: relative fertility 1.401 (Qwen2) / 1.448 (DeepSeek-V3). Beta is therefore STRONGLY FERTILITY-CONFOUNDED.


## 2. Tokenizer cost (a confound, not a verdict)

| tokenizer | tokens/program | tokens/char | vs identity | byte-fallback fragments |
|---|---:|---:|---:|---:|
| `Qwen2 BPE (shared by all 4 Qwen2.5-Coder repos)` | 27.226 | 0.4918 | 1.401× | 0.000% |
| `deepseek-ai/DeepSeek-V3` | 26.790 | 0.4840 | 1.448× | 0.000% |

Fertility demonstrates **token cost**. Whether accuracy degrades is a separate measurement, reported in §5.

## 3. What was fed to each model

**Lane A (base checkpoints):** the program string alone — no editing request, no instruction prompt, empty neutral prefix, identical policy in every language. Teacher-forced scoring only; **no training occurred**.

**Lane B (instruct checkpoints):** a system prompt containing the mechanically rendered language specification for **this** language (program shape, selector forms, all 15 operations with their argument names and a plain-English description, four worked examples), plus a user message with the natural-language editing request. In `scaffolded` the user message also carries the scene's addressable parts and tag list, rendered with this language's sigils.

Every spelling shown was **this language's own**; no 3DOM spelling was taught to an alien arm and no translation pair appeared in any prompt (enforced by `taught_spellings` tests). The exact model input for every case is saved under `prompts/rendered/`.

## 4. Lane A — base-model surprise

| base model | device | NLL/char | NLL/token | perplexity | ΔNLL/char vs identity | 95% CI |
|---|---|---:|---:|---:|---:|---|
| `0.5B` | cuda | 3.0549 | 6.4481 | 631.49 | +1.7235 | [+1.6256, +1.8126] |
| `1.5B` | cuda | 2.9802 | 6.2903 | 539.32 | +1.7079 | [+1.6159, +1.7901] |
| `3B` | cuda | 2.9121 | 6.1466 | 467.14 | +1.6631 | [+1.5701, +1.7472] |
| `7B` | cpu | 2.8585 | 6.0335 | 417.16 | +1.5910 | [+1.5094, +1.6659] |

**Blocked Lane A cells:**

- `Qwen/Qwen2.5-Coder-7B` (fp32/cuda) — OOM: OutOfMemoryError: CUDA out of memory. Tried to allocate 260.00 MiB. GPU 0 has a total capacity of 15.61 GiB of which 114.12 MiB is free. Including non-PyTorch m

NLL/character is the primary prior-distance measure (fertility-free). NLL/token is diagnostic only, because token boundaries differ across languages. These are **not** accuracy numbers.

## 5. Lane B — behavioural accuracy

### bare

| instruct model | semantic accuracy | parse validity | language compliance | vacuous | Δ vs identity | 95% paired CI | McNemar p |
|---|---|---|---|---:|---:|---|---:|
| `0.5B` | 4.8% (1/21, 95% CI 0.8%–22.7%) | 95.2% | 100.0% | 0.0% | -0.095 | [-0.238, +0.000] | 0.5000 (n_disc=2) |
| `1.5B` | 19.0% (4/21, 95% CI 7.7%–40.0%) | 90.5% | 100.0% | 0.0% | -0.238 | [-0.429, -0.095] | 0.0625 (n_disc=5) |
| `3B` | 66.7% (14/21, 95% CI 45.4%–82.8%) | 100.0% | 100.0% | 0.0% | +0.095 | [-0.095, +0.286] | 0.6250 (n_disc=4) |
| `7B` | 19.0% (4/21, 95% CI 7.7%–40.0%) | 100.0% | 100.0% | 0.0% | -0.524 | [-0.714, -0.333] | 0.0010 (n_disc=11) |

### scaffolded

| instruct model | semantic accuracy | parse validity | language compliance | vacuous | Δ vs identity | 95% paired CI | McNemar p |
|---|---|---|---|---:|---:|---|---:|
| `0.5B` | 0.0% (0/21, 95% CI 0.0%–15.5%) | 0.0% | 100.0% | 0.0% | -0.048 | [-0.143, +0.000] | 1.0000 (n_disc=1) |
| `1.5B` | 28.6% (6/21, 95% CI 13.8%–50.0%) | 95.2% | 100.0% | 0.0% | -0.286 | [-0.476, -0.095] | 0.0312 (n_disc=6) |
| `3B` | 85.7% (18/21, 95% CI 65.4%–95.0%) | 95.2% | 100.0% | 0.0% | +0.048 | [+0.000, +0.143] | 1.0000 (n_disc=1) |
| `7B` | 52.4% (11/21, 95% CI 32.4%–71.7%) | 66.7% | 100.0% | 0.0% | -0.381 | [-0.619, -0.143] | 0.0215 (n_disc=10) |

## 6. Task-specific strengths and failures

| model | condition | op-selection | selector-resolution | arg-extraction | multi-op |
|---|---|---|---|---|---|
| `0.5B` | bare | 66.7% (14/21) | 9.5% (2/21) | 71.4% (15/21) | 57.1% (12/21) |
| `0.5B` | scaffolded | 0.0% (0/21) | 0.0% (0/21) | 0.0% (0/21) | 0.0% (0/21) |
| `1.5B` | bare | 42.9% (9/21) | 38.1% (8/21) | 66.7% (14/21) | 42.9% (9/21) |
| `1.5B` | scaffolded | 52.4% (11/21) | 66.7% (14/21) | 81.0% (17/21) | 52.4% (11/21) |
| `3B` | bare | 95.2% (20/21) | 66.7% (14/21) | 100.0% (21/21) | 95.2% (20/21) |
| `3B` | scaffolded | 90.5% (19/21) | 90.5% (19/21) | 95.2% (20/21) | 90.5% (19/21) |
| `7B` | bare | 81.0% (17/21) | 38.1% (8/21) | 90.5% (19/21) | 81.0% (17/21) |
| `7B` | scaffolded | 52.4% (11/21) | 66.7% (14/21) | 61.9% (13/21) | 52.4% (11/21) |

## 7. Parse failures versus semantic failures

| model | condition | LEX_FAIL | PARSE_FAIL | VALID_VACUOUS | VALID_WRONG | VALID_CORRECT |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 0 | 1 | 0 | 19 | 1 |
| `0.5B` | scaffolded | 0 | 21 | 0 | 0 | 0 |
| `1.5B` | bare | 0 | 2 | 0 | 15 | 4 |
| `1.5B` | scaffolded | 0 | 1 | 0 | 14 | 6 |
| `3B` | bare | 0 | 0 | 0 | 7 | 14 |
| `3B` | scaffolded | 0 | 1 | 0 | 2 | 18 |
| `7B` | bare | 0 | 0 | 0 | 17 | 4 |
| `7B` | scaffolded | 0 | 7 | 0 | 3 | 11 |

These are orthogonal constructs and are never averaged. A program can parse perfectly and mean the wrong thing (`VALID_WRONG`), or parse and mean nothing at all (`VALID_VACUOUS` — a parse success and a task failure).

### Hallucination categories

| model | condition | invented_operation | invented_selector | invented_argument | wrong_language_spelling | extra_operation | missing_operation | prose_instead_of_code |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `0.5B` | bare | 6 | 10 | 5 | 0 | 3 | 0 | 0 |
| `0.5B` | scaffolded | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `1.5B` | bare | 10 | 8 | 5 | 0 | 1 | 0 | 0 |
| `1.5B` | scaffolded | 9 | 0 | 3 | 0 | 2 | 0 | 0 |
| `3B` | bare | 1 | 4 | 0 | 0 | 0 | 0 | 0 |
| `3B` | scaffolded | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `7B` | bare | 4 | 11 | 2 | 0 | 1 | 0 | 0 |
| `7B` | scaffolded | 3 | 0 | 1 | 0 | 0 | 0 | 0 |

A parse failure is **not** counted as a hallucination.

## 8. Representative outputs

**Correct:**

- **`whole-truck`** · 0.5B · bare · outcome `VALID_CORRECT`
  - request: _paint the whole truck red_
  - model wrote: `(mumvumfe(){ &Q('~truck')~flertum('#ff0000'); })();`
  - parsed to: `[{"op": "recolor", "selector": ".truck", "args": {"color": "#ff0000"}}]`
  - resolved nodes: `[["DumpTruck"]]`
  - scorer said: verb(s) ok: recolor; right nodes, nothing extra; n/a (case carries no arg expectation); 1 op(s), types ok
- **`all-four-wheels`** · 1.5B · bare · outcome `VALID_CORRECT`
  - request: _make all four wheels black_
  - model wrote: `(mumvumfe(){ &Q('~wheel')~flertum('#000000'); })();`
  - parsed to: `[{"op": "recolor", "selector": ".wheel", "args": {"color": "#000000"}}]`
  - resolved nodes: `[["Object_20", "Object_21", "Object_22", "Object_23"]]`
  - scorer said: verb(s) ok: recolor; right nodes, nothing extra; n/a (case carries no arg expectation); 1 op(s), types ok


**Failed:**

- **`all-four-wheels`** · 0.5B · bare · outcome `VALID_WRONG`
  - request: _make all four wheels black_
  - model wrote: `(mumvumfe(){ &Q('~wheels')~flertum('#000000'); })();`
  - parsed to: `[{"op": "recolor", "selector": ".wheels", "args": {"color": "#000000"}}]`
  - resolved nodes: `[[]]`
  - scorer said: verb(s) ok: recolor; op0: missed Object_20, Object_21, Object_22, Object_23; n/a (case carries no arg expectation); 1 op(s), types ok
- **`all-four-wheels`** · 0.5B · scaffolded · outcome `PARSE_FAIL`
  - request: _make all four wheels black_
  - model wrote: `# Define the scene
scene = {
    "DumpTruck": {"tag": "DumpTruck"},
    "Object_03": {"tag": "Cab"},
    "Object_07": {"tag": "Dump Bed"},
    "Object_12": {"tag": "Tail Light (left)"},
    "Object_13`
  - parsed to: `null`
  - resolved nodes: `null`
  - scorer said: tokenised, but no derivation exists


## 9. Runtime and token cost

| model | condition | input tok (med) | output tok (med) | e2e s (med) | e2e s (p95) | tok/s |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 789.000 | 27.000 | 0.626 | 1.244 | 45.324 |
| `0.5B` | scaffolded | 1244.000 | 512.000 | 11.691 | 11.747 | 43.977 |
| `1.5B` | bare | 789.000 | 29.000 | 0.864 | 1.529 | 37.532 |
| `1.5B` | scaffolded | 1244.000 | 29.000 | 0.901 | 1.641 | 37.601 |
| `3B` | bare | 789.000 | 28.000 | 1.178 | 1.809 | 28.818 |
| `3B` | scaffolded | 1244.000 | 28.000 | 1.263 | 2.129 | 29.251 |
| `7B` | bare | 789.000 | 31.000 | 1.477 | 2.383 | 27.979 |
| `7B` | scaffolded | 1244.000 | 30.000 | 1.601 | 2.722 | 28.019 |

## 10. Effect of scaffolding

| model | bare | scaffolded | difference |
|---|---:|---:|---:|
| `0.5B` | 4.8% | 0.0% | -0.048 |
| `1.5B` | 19.0% | 28.6% | +0.095 |
| `3B` | 66.7% | 85.7% | +0.190 |
| `7B` | 19.0% | 52.4% | +0.333 |

## 11. Uncertainty

Accuracy proportions carry Wilson 95% intervals. Language-vs-identity comparisons use matched items with a 95% paired item-level bootstrap (10 000 resamples, seed 20260910) and an exact McNemar test on the discordant pairs. With 21 generation cases the intervals are wide: read effect sizes and intervals, not p-values.

## 12. What can and cannot be concluded

**Can:** how many model tokens this language cost, how long it took, how often its outputs lexed, parsed, meant nothing, or meant the right thing, and how that compares to identity on the very same items.

**Cannot:** that tokenizer fertility *caused* any accuracy difference. Spelling, tokenization all change together here; nothing isolates one. No winner is selected, and nothing here makes any candidate eligible under Experiment 01's fertility gate.
