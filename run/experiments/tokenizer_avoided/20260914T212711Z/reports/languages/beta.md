# `beta` — language report

_Run `20260914T212711Z` · an exploratory fertility-unmatched model evaluation._

## 1. What this language changes

**The absence condition — pronounceable invented words.** Beta replaces each spelling with an ASCII pseudo-word of deliberately matched length and camelCase shape (`flertum` for recolour, `mumvumfe` for the function keyword, `&Q` for the selector entry, `~` for the class sigil). Character length matches 3DOM almost exactly, but the invented words are not single vocabulary units, so they fragment into more ordinary sub-word pieces: relative fertility 1.401 (Qwen2) / 1.448 (DeepSeek-V3). Beta is therefore STRONGLY FERTILITY-CONFOUNDED.


## 2. Tokenizer cost (a confound, not a verdict)

| tokenizer | tokens/program | tokens/char | vs identity | byte-fallback fragments |
|---|---:|---:|---:|---:|
| `Qwen/Qwen2.5-Coder-0.5B` | 27.226 | 0.4918 | 1.401× | 0.000% |
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
| `0.5B` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 100.0% | 100.0% | 0.0% | -0.125 | [-0.375, +0.000] | 1.0000 (n_disc=1) |

### scaffolded

| instruct model | semantic accuracy | parse validity | language compliance | vacuous | Δ vs identity | 95% paired CI | McNemar p |
|---|---|---|---|---:|---:|---|---:|
| `0.5B` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 0.0% | 100.0% | 0.0% | +0.000 | [+0.000, +0.000] | 1.0000 (n_disc=0) |

## 6. Task-specific strengths and failures

| model | condition | op-selection | selector-resolution | arg-extraction | multi-op |
|---|---|---|---|---|---|
| `0.5B` | bare | 62.5% (5/8) | 12.5% (1/8) | 37.5% (3/8) | 62.5% (5/8) |
| `0.5B` | scaffolded | 0.0% (0/8) | 0.0% (0/8) | 0.0% (0/8) | 0.0% (0/8) |

## 7. Parse failures versus semantic failures

| model | condition | LEX_FAIL | PARSE_FAIL | VALID_VACUOUS | VALID_WRONG | VALID_CORRECT |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 0 | 0 | 0 | 8 | 0 |
| `0.5B` | scaffolded | 0 | 8 | 0 | 0 | 0 |

These are orthogonal constructs and are never averaged. A program can parse perfectly and mean the wrong thing (`VALID_WRONG`), or parse and mean nothing at all (`VALID_VACUOUS` — a parse success and a task failure).

### Hallucination categories

| model | condition | invented_operation | invented_selector | invented_argument | wrong_language_spelling | extra_operation | missing_operation | prose_instead_of_code |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `0.5B` | bare | 3 | 6 | 5 | 0 | 0 | 0 | 0 |
| `0.5B` | scaffolded | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

A parse failure is **not** counted as a hallucination.

## 8. Representative outputs

**Correct:**

_none recorded_


**Failed:**

- **`bigger`** · 0.5B · bare · outcome `VALID_WRONG`
  - request: _make it bigger_
  - model wrote: `(mumvumfe(){ &Q('~rotate')~grom('x',1,2); })();`
  - parsed to: `[{"op": "spin", "selector": ".rotate", "args": {"axis": "x", "duration": 2, "turns": 1}}]`
  - resolved nodes: `[[]]`
  - scorer said: op0: "spin" != "scale"; op0: missed DumpTruck; missing arg factor; op0 "spin" != "scale"
- **`bigger`** · 0.5B · scaffolded · outcome `PARSE_FAIL`
  - request: _make it bigger_
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
| `0.5B` | bare | 788.000 | 24.500 | 0.568 | 0.618 | 45.666 |
| `0.5B` | scaffolded | 1243.000 | 512.000 | 11.710 | 11.746 | 43.907 |

## 10. Effect of scaffolding

| model | bare | scaffolded | difference |
|---|---:|---:|---:|
| `0.5B` | 0.0% | 0.0% | +0.000 |

## 11. Uncertainty

Accuracy proportions carry Wilson 95% intervals. Language-vs-identity comparisons use matched items with a 95% paired item-level bootstrap (10 000 resamples, seed 20260910) and an exact McNemar test on the discordant pairs. With 21 generation cases the intervals are wide: read effect sizes and intervals, not p-values.

## 12. What can and cannot be concluded

**Can:** how many model tokens this language cost, how long it took, how often its outputs lexed, parsed, meant nothing, or meant the right thing, and how that compares to identity on the very same items.

**Cannot:** that tokenizer fertility *caused* any accuracy difference. Spelling, tokenization all change together here; nothing isolates one. No winner is selected, and nothing here makes any candidate eligible under Experiment 01's fertility gate.
