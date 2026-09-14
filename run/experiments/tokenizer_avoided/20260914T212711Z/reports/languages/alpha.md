# `alpha` — language report

_Run `20260914T212711Z` · an exploratory fertility-unmatched model evaluation._

## 1. What this language changes

**The interference condition — familiar spellings, wrong meanings.** Alpha reuses 3DOM's own vocabulary but PERMUTES which role each word plays. The word `recolor` spells the *function keyword*; the word `scale` spells the *recolour* operation; `mesh` spells *receiveShadow*; the class sigil is `#` and the id sigil is `:`. Every spelling is familiar and almost every one means something else. Its relative tokenizer fertility is 1.068 (Qwen2) / 1.073 (DeepSeek-V3) — the mildest of the three, though still outside Experiment 01's [0.95, 1.05] band.


## 2. Tokenizer cost (a confound, not a verdict)

| tokenizer | tokens/program | tokens/char | vs identity | byte-fallback fragments |
|---|---:|---:|---:|---:|
| `Qwen/Qwen2.5-Coder-0.5B` | 20.306 | 0.3750 | 1.068× | 0.000% |
| `deepseek-ai/DeepSeek-V3` | 19.419 | 0.3587 | 1.073× | 0.000% |

Fertility demonstrates **token cost**. Whether accuracy degrades is a separate measurement, reported in §5.

## 3. What was fed to each model

**Lane A (base checkpoints):** the program string alone — no editing request, no instruction prompt, empty neutral prefix, identical policy in every language. Teacher-forced scoring only; **no training occurred**.

**Lane B (instruct checkpoints):** a system prompt containing the mechanically rendered language specification for **this** language (program shape, selector forms, all 15 operations with their argument names and a plain-English description, four worked examples), plus a user message with the natural-language editing request. In `scaffolded` the user message also carries the scene's addressable parts and tag list, rendered with this language's sigils.

Every spelling shown was **this language's own**; no 3DOM spelling was taught to an alien arm and no translation pair appeared in any prompt (enforced by `taught_spellings` tests). The exact model input for every case is saved under `prompts/rendered/`.

## 4. Lane A — base-model surprise

| base model | device | NLL/char | NLL/token | perplexity | ΔNLL/char vs identity | 95% CI |
|---|---|---:|---:|---:|---:|---|
| `0.5B` | cuda | 1.8839 | 5.2834 | 197.04 | +0.5525 | [+0.5059, +0.6005] |
| `1.5B` | cuda | 1.9034 | 5.3381 | 208.12 | +0.6311 | [+0.5867, +0.6778] |
| `3B` | cuda | 1.9021 | 5.3344 | 207.35 | +0.6530 | [+0.6089, +0.6991] |
| `7B` | cpu | 1.8546 | 5.2011 | 181.48 | +0.5871 | [+0.5409, +0.6355] |

**Blocked Lane A cells:**

- `Qwen/Qwen2.5-Coder-7B` (fp32/cuda) — OOM: OutOfMemoryError: CUDA out of memory. Tried to allocate 260.00 MiB. GPU 0 has a total capacity of 15.61 GiB of which 114.12 MiB is free. Including non-PyTorch m

NLL/character is the primary prior-distance measure (fertility-free). NLL/token is diagnostic only, because token boundaries differ across languages. These are **not** accuracy numbers.

## 5. Lane B — behavioural accuracy

### bare

| instruct model | semantic accuracy | parse validity | language compliance | vacuous | Δ vs identity | 95% paired CI | McNemar p |
|---|---|---|---|---:|---:|---|---:|
| `0.5B` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 87.5% | 100.0% | 0.0% | -0.125 | [-0.375, +0.000] | 1.0000 (n_disc=1) |

### scaffolded

| instruct model | semantic accuracy | parse validity | language compliance | vacuous | Δ vs identity | 95% paired CI | McNemar p |
|---|---|---|---|---:|---:|---|---:|
| `0.5B` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 0.0% | 100.0% | 0.0% | +0.000 | [+0.000, +0.000] | 1.0000 (n_disc=0) |

## 6. Task-specific strengths and failures

| model | condition | op-selection | selector-resolution | arg-extraction | multi-op |
|---|---|---|---|---|---|
| `0.5B` | bare | 12.5% (1/8) | 25.0% (2/8) | 25.0% (2/8) | 12.5% (1/8) |
| `0.5B` | scaffolded | 0.0% (0/8) | 0.0% (0/8) | 0.0% (0/8) | 0.0% (0/8) |

## 7. Parse failures versus semantic failures

| model | condition | LEX_FAIL | PARSE_FAIL | VALID_VACUOUS | VALID_WRONG | VALID_CORRECT |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 0 | 1 | 0 | 7 | 0 |
| `0.5B` | scaffolded | 0 | 8 | 0 | 0 | 0 |

These are orthogonal constructs and are never averaged. A program can parse perfectly and mean the wrong thing (`VALID_WRONG`), or parse and mean nothing at all (`VALID_VACUOUS` — a parse success and a task failure).

### Hallucination categories

| model | condition | invented_operation | invented_selector | invented_argument | wrong_language_spelling | extra_operation | missing_operation | prose_instead_of_code |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `0.5B` | bare | 6 | 5 | 5 | 0 | 0 | 0 | 0 |
| `0.5B` | scaffolded | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

A parse failure is **not** counted as a hallucination.

## 8. Representative outputs

**Correct:**

_none recorded_


**Failed:**

- **`bigger`** · 0.5B · bare · outcome `VALID_WRONG`
  - request: _make it bigger_
  - model wrote: `(recolor(){ $$('#box')#scale('#00ff00'); })();`
  - parsed to: `[{"op": "recolor", "selector": ".box", "args": {"color": "#00ff00"}}]`
  - resolved nodes: `[[]]`
  - scorer said: op0: "recolor" != "scale"; op0: missed DumpTruck; missing arg factor; op0 "recolor" != "scale"
- **`bigger`** · 0.5B · scaffolded · outcome `PARSE_FAIL`
  - request: _make it bigger_
  - model wrote: `recolor(){
  $$('#dumpTruck').#duplicate('y',1,2);
}`
  - parsed to: `null`
  - resolved nodes: `null`
  - scorer said: tokenised, but no derivation exists


## 9. Runtime and token cost

| model | condition | input tok (med) | output tok (med) | e2e s (med) | e2e s (p95) | tok/s |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 719.000 | 21.000 | 0.488 | 0.505 | 45.738 |
| `0.5B` | scaffolded | 1174.000 | 25.500 | 0.606 | 9.696 | 45.331 |

## 10. Effect of scaffolding

| model | bare | scaffolded | difference |
|---|---:|---:|---:|
| `0.5B` | 0.0% | 0.0% | +0.000 |

## 11. Uncertainty

Accuracy proportions carry Wilson 95% intervals. Language-vs-identity comparisons use matched items with a 95% paired item-level bootstrap (10 000 resamples, seed 20260910) and an exact McNemar test on the discordant pairs. With 21 generation cases the intervals are wide: read effect sizes and intervals, not p-values.

## 12. What can and cannot be concluded

**Can:** how many model tokens this language cost, how long it took, how often its outputs lexed, parsed, meant nothing, or meant the right thing, and how that compares to identity on the very same items.

**Cannot:** that tokenizer fertility *caused* any accuracy difference. Spelling, tokenization all change together here; nothing isolates one. No winner is selected, and nothing here makes any candidate eligible under Experiment 01's fertility gate.
