# `identity` — language report

_Run `20260914T212711Z` · an exploratory fertility-unmatched model evaluation._

## 1. What this language changes

**Ordinary 3DOM.** The baseline. `$S('.wheel').recolor('black')` — the selector entry is `$S`, the chain operator is `.`, classes start with `.`, and the operation names are ordinary English words (`recolor`, `scale`, `move`). This is the only arm whose spellings a code model plausibly saw during pretraining.


## 2. Tokenizer cost (a confound, not a verdict)

| tokenizer | tokens/program | tokens/char | vs identity | byte-fallback fragments |
|---|---:|---:|---:|---:|
| `Qwen/Qwen2.5-Coder-0.5B` | 19.435 | 0.3511 | 1.000× | 0.000% |
| `deepseek-ai/DeepSeek-V3` | 18.500 | 0.3342 | 1.000× | 0.000% |

Fertility demonstrates **token cost**. Whether accuracy degrades is a separate measurement, reported in §5.

## 3. What was fed to each model

**Lane A (base checkpoints):** the program string alone — no editing request, no instruction prompt, empty neutral prefix, identical policy in every language. Teacher-forced scoring only; **no training occurred**.

**Lane B (instruct checkpoints):** a system prompt containing the mechanically rendered language specification for **this** language (program shape, selector forms, all 15 operations with their argument names and a plain-English description, four worked examples), plus a user message with the natural-language editing request. In `scaffolded` the user message also carries the scene's addressable parts and tag list, rendered with this language's sigils.

Every spelling shown was **this language's own**; no 3DOM spelling was taught to an alien arm and no translation pair appeared in any prompt (enforced by `taught_spellings` tests). The exact model input for every case is saved under `prompts/rendered/`.

## 4. Lane A — base-model surprise

| base model | device | NLL/char | NLL/token | perplexity | ΔNLL/char vs identity | 95% CI |
|---|---|---:|---:|---:|---:|---|
| `0.5B` | cuda | 1.3314 | 3.9978 | 54.48 | — (baseline) | — |
| `1.5B` | cuda | 1.2723 | 3.8202 | 45.61 | — (baseline) | — |
| `3B` | cuda | 1.2491 | 3.7505 | 42.54 | — (baseline) | — |
| `7B` | cpu | 1.2675 | 3.8058 | 44.96 | — (baseline) | — |

**Blocked Lane A cells:**

- `Qwen/Qwen2.5-Coder-7B` (fp32/cuda) — OOM: OutOfMemoryError: CUDA out of memory. Tried to allocate 260.00 MiB. GPU 0 has a total capacity of 15.61 GiB of which 114.12 MiB is free. Including non-PyTorch m

NLL/character is the primary prior-distance measure (fertility-free). NLL/token is diagnostic only, because token boundaries differ across languages. These are **not** accuracy numbers.

## 5. Lane B — behavioural accuracy

### bare

| instruct model | semantic accuracy | parse validity | language compliance | vacuous | Δ vs identity | 95% paired CI | McNemar p |
|---|---|---|---|---:|---:|---|---:|
| `0.5B` | 12.5% (1/8, 95% CI 2.2%–47.1%) | 100.0% | 100.0% | 0.0% | — (baseline) | — | — |

### scaffolded

| instruct model | semantic accuracy | parse validity | language compliance | vacuous | Δ vs identity | 95% paired CI | McNemar p |
|---|---|---|---|---:|---:|---|---:|
| `0.5B` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 100.0% | 100.0% | 0.0% | — (baseline) | — | — |

## 6. Task-specific strengths and failures

| model | condition | op-selection | selector-resolution | arg-extraction | multi-op |
|---|---|---|---|---|---|
| `0.5B` | bare | 75.0% (6/8) | 37.5% (3/8) | 50.0% (4/8) | 62.5% (5/8) |
| `0.5B` | scaffolded | 50.0% (4/8) | 12.5% (1/8) | 37.5% (3/8) | 37.5% (3/8) |

## 7. Parse failures versus semantic failures

| model | condition | LEX_FAIL | PARSE_FAIL | VALID_VACUOUS | VALID_WRONG | VALID_CORRECT |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 0 | 0 | 0 | 7 | 1 |
| `0.5B` | scaffolded | 0 | 0 | 0 | 8 | 0 |

These are orthogonal constructs and are never averaged. A program can parse perfectly and mean the wrong thing (`VALID_WRONG`), or parse and mean nothing at all (`VALID_VACUOUS` — a parse success and a task failure).

### Hallucination categories

| model | condition | invented_operation | invented_selector | invented_argument | wrong_language_spelling | extra_operation | missing_operation | prose_instead_of_code |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `0.5B` | bare | 2 | 5 | 4 | 0 | 1 | 0 | 0 |
| `0.5B` | scaffolded | 4 | 6 | 5 | 0 | 2 | 0 | 0 |

A parse failure is **not** counted as a hallucination.

## 8. Representative outputs

**Correct:**

- **`lift`** · 0.5B · bare · outcome `VALID_CORRECT`
  - request: _lift the cab up a bit_
  - model wrote: `(function(){ $S('.cab').move(0,1,0).recolor('#ff0000'); })();`
  - parsed to: `[{"op": "move", "selector": ".cab", "args": {"dx": 0, "dy": 1, "dz": 0}}, {"op": "recolor", "selector": ".cab", "args": {"color": "#ff0000"}}]`
  - resolved nodes: `[["Object_03"], ["Object_03"]]`
  - scorer said: verb(s) ok: move; right nodes, nothing extra; args ok; 2 ops != target 1 (over-split)


**Failed:**

- **`bigger`** · 0.5B · bare · outcome `VALID_WRONG`
  - request: _make it bigger_
  - model wrote: `(function(){ $S('.box').scale(2); })();`
  - parsed to: `[{"op": "scale", "selector": ".box", "args": {"factor": 2}}]`
  - resolved nodes: `[[]]`
  - scorer said: verb(s) ok: scale; op0: missed DumpTruck; args ok; 1 op(s), types ok
- **`bigger`** · 0.5B · scaffolded · outcome `VALID_WRONG`
  - request: _make it bigger_
  - model wrote: `(function(){
  $S('.dump-truck').scale(2);
})();`
  - parsed to: `[{"op": "scale", "selector": ".dump-truck", "args": {"factor": 2}}]`
  - resolved nodes: `[[]]`
  - scorer said: verb(s) ok: scale; op0: missed DumpTruck; args ok; 1 op(s), types ok


## 9. Runtime and token cost

| model | condition | input tok (med) | output tok (med) | e2e s (med) | e2e s (p95) | tok/s |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 715.000 | 19.500 | 0.451 | 0.584 | 46.110 |
| `0.5B` | scaffolded | 1170.000 | 25.000 | 0.590 | 6.810 | 45.425 |

## 10. Effect of scaffolding

| model | bare | scaffolded | difference |
|---|---:|---:|---:|
| `0.5B` | 12.5% | 0.0% | -0.125 |

## 11. Uncertainty

Accuracy proportions carry Wilson 95% intervals. Language-vs-identity comparisons use matched items with a 95% paired item-level bootstrap (10 000 resamples, seed 20260910) and an exact McNemar test on the discordant pairs. With 21 generation cases the intervals are wide: read effect sizes and intervals, not p-values.

## 12. What can and cannot be concluded

**Can:** how many model tokens this language cost, how long it took, how often its outputs lexed, parsed, meant nothing, or meant the right thing, and how that compares to identity on the very same items.

**Cannot:** that tokenizer fertility *caused* any accuracy difference. Spelling, tokenization all change together here; nothing isolates one. No winner is selected, and nothing here makes any candidate eligible under Experiment 01's fertility gate.
