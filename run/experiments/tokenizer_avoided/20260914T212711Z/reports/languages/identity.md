# `identity` — language report

_Run `20260914T212711Z` · an exploratory fertility-unmatched model evaluation._

## 1. What this language changes

**Ordinary 3DOM.** The baseline. `$S('.wheel').recolor('black')` — the selector entry is `$S`, the chain operator is `.`, classes start with `.`, and the operation names are ordinary English words (`recolor`, `scale`, `move`). This is the only arm whose spellings a code model plausibly saw during pretraining.


## 2. Tokenizer cost (a confound, not a verdict)

| tokenizer | tokens/program | tokens/char | vs identity | byte-fallback fragments |
|---|---:|---:|---:|---:|
| `Qwen2 BPE (shared by all 4 Qwen2.5-Coder repos)` | 19.435 | 0.3511 | 1.000× | 0.000% |
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
| `0.5B` | 14.3% (3/21, 95% CI 5.0%–34.6%) | 95.2% | 100.0% | 0.0% | — (baseline) | — | — |
| `1.5B` | 42.9% (9/21, 95% CI 24.5%–63.5%) | 85.7% | 100.0% | 0.0% | — (baseline) | — | — |
| `3B` | 57.1% (12/21, 95% CI 36.5%–75.5%) | 95.2% | 100.0% | 0.0% | — (baseline) | — | — |
| `7B` | 71.4% (15/21, 95% CI 50.0%–86.2%) | 90.5% | 100.0% | 0.0% | — (baseline) | — | — |

### scaffolded

| instruct model | semantic accuracy | parse validity | language compliance | vacuous | Δ vs identity | 95% paired CI | McNemar p |
|---|---|---|---|---:|---:|---|---:|
| `0.5B` | 4.8% (1/21, 95% CI 0.8%–22.7%) | 90.5% | 100.0% | 0.0% | — (baseline) | — | — |
| `1.5B` | 57.1% (12/21, 95% CI 36.5%–75.5%) | 100.0% | 100.0% | 0.0% | — (baseline) | — | — |
| `3B` | 81.0% (17/21, 95% CI 60.0%–92.3%) | 100.0% | 100.0% | 0.0% | — (baseline) | — | — |
| `7B` | 90.5% (19/21, 95% CI 71.1%–97.3%) | 95.2% | 100.0% | 0.0% | — (baseline) | — | — |

## 6. Task-specific strengths and failures

| model | condition | op-selection | selector-resolution | arg-extraction | multi-op |
|---|---|---|---|---|---|
| `0.5B` | bare | 66.7% (14/21) | 28.6% (6/21) | 76.2% (16/21) | 52.4% (11/21) |
| `0.5B` | scaffolded | 28.6% (6/21) | 9.5% (2/21) | 66.7% (14/21) | 23.8% (5/21) |
| `1.5B` | bare | 81.0% (17/21) | 47.6% (10/21) | 85.7% (18/21) | 81.0% (17/21) |
| `1.5B` | scaffolded | 85.7% (18/21) | 76.2% (16/21) | 95.2% (20/21) | 95.2% (20/21) |
| `3B` | bare | 90.5% (19/21) | 61.9% (13/21) | 95.2% (20/21) | 90.5% (19/21) |
| `3B` | scaffolded | 95.2% (20/21) | 85.7% (18/21) | 100.0% (21/21) | 95.2% (20/21) |
| `7B` | bare | 90.5% (19/21) | 76.2% (16/21) | 90.5% (19/21) | 85.7% (18/21) |
| `7B` | scaffolded | 95.2% (20/21) | 90.5% (19/21) | 95.2% (20/21) | 95.2% (20/21) |

## 7. Parse failures versus semantic failures

| model | condition | LEX_FAIL | PARSE_FAIL | VALID_VACUOUS | VALID_WRONG | VALID_CORRECT |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 0 | 1 | 0 | 17 | 3 |
| `0.5B` | scaffolded | 0 | 2 | 0 | 18 | 1 |
| `1.5B` | bare | 0 | 3 | 0 | 9 | 9 |
| `1.5B` | scaffolded | 0 | 0 | 0 | 9 | 12 |
| `3B` | bare | 0 | 1 | 0 | 8 | 12 |
| `3B` | scaffolded | 0 | 0 | 0 | 4 | 17 |
| `7B` | bare | 0 | 2 | 0 | 4 | 15 |
| `7B` | scaffolded | 0 | 1 | 0 | 1 | 19 |

These are orthogonal constructs and are never averaged. A program can parse perfectly and mean the wrong thing (`VALID_WRONG`), or parse and mean nothing at all (`VALID_VACUOUS` — a parse success and a task failure).

### Hallucination categories

| model | condition | invented_operation | invented_selector | invented_argument | wrong_language_spelling | extra_operation | missing_operation | prose_instead_of_code |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `0.5B` | bare | 6 | 6 | 4 | 0 | 3 | 0 | 0 |
| `0.5B` | scaffolded | 13 | 10 | 5 | 0 | 7 | 1 | 0 |
| `1.5B` | bare | 1 | 3 | 0 | 0 | 0 | 0 | 0 |
| `1.5B` | scaffolded | 3 | 0 | 1 | 0 | 0 | 0 | 0 |
| `3B` | bare | 1 | 3 | 0 | 0 | 1 | 0 | 0 |
| `3B` | scaffolded | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `7B` | bare | 0 | 1 | 0 | 0 | 1 | 0 | 0 |
| `7B` | scaffolded | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

A parse failure is **not** counted as a hallucination.

## 8. Representative outputs

**Correct:**

- **`all-four-wheels`** · 0.5B · bare · outcome `VALID_CORRECT`
  - request: _make all four wheels black_
  - model wrote: `(function(){ $S('.wheel').recolor('#000000'); })();`
  - parsed to: `[{"op": "recolor", "selector": ".wheel", "args": {"color": "#000000"}}]`
  - resolved nodes: `[["Object_20", "Object_21", "Object_22", "Object_23"]]`
  - scorer said: verb(s) ok: recolor; right nodes, nothing extra; n/a (case carries no arg expectation); 1 op(s), types ok
- **`lift`** · 0.5B · bare · outcome `VALID_CORRECT`
  - request: _lift the cab up a bit_
  - model wrote: `(function(){ $S('.cab').move(0,1,0).recolor('#ff0000'); })();`
  - parsed to: `[{"op": "move", "selector": ".cab", "args": {"dx": 0, "dy": 1, "dz": 0}}, {"op": "recolor", "selector": ".cab", "args": {"color": "#ff0000"}}]`
  - resolved nodes: `[["Object_03"], ["Object_03"]]`
  - scorer said: verb(s) ok: move; right nodes, nothing extra; args ok; 2 ops != target 1 (over-split)


**Failed:**

- **`all-four-wheels`** · 0.5B · scaffolded · outcome `VALID_WRONG`
  - request: _make all four wheels black_
  - model wrote: `(function(){
  $S('.dump-truck').setMaterial('#00ff00');
  $S('.object-03').setMaterial('#00ff00');
  $S('.object-07').setMaterial('#00ff00');
  $S('.object-12').setMaterial('#00ff00');
  $S('.object-`
  - parsed to: `[{"op": "setMaterial", "selector": ".dump-truck", "args": {"material": "#00ff00"}}, {"op": "setMaterial", "selector": ".object-03", "args": {"material": "#00ff00"}}, {"op": "setMaterial", "selector": `
  - resolved nodes: `[[], [], [], [], [], [], [], [], []]`
  - scorer said: op0: "setMaterial" != "recolor"; op0: missed Object_20, Object_21, Object_22, Object_23; n/a (case carries no arg expectation); 9 ops != target 1 (over-split)
- **`bed-and-lights`** · 0.5B · bare · outcome `VALID_WRONG`
  - request: _paint the bed red and remove the tail lights_
  - model wrote: `(function(){ $S('.bed').recolor('#ff0000'); $S('.taillights').delete(); })();`
  - parsed to: `[{"op": "recolor", "selector": ".bed", "args": {"color": "#ff0000"}}, {"op": "delete", "selector": ".taillights", "args": {}}]`
  - resolved nodes: `[["Object_07"], []]`
  - scorer said: verb(s) ok: recolor, delete; op1: missed Object_12, Object_13; n/a (case carries no arg expectation); 2 op(s), types ok


## 9. Runtime and token cost

| model | condition | input tok (med) | output tok (med) | e2e s (med) | e2e s (p95) | tok/s |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 716.000 | 21.000 | 0.483 | 0.822 | 45.881 |
| `0.5B` | scaffolded | 1171.000 | 35.000 | 0.835 | 10.027 | 45.217 |
| `1.5B` | bare | 716.000 | 24.000 | 0.713 | 1.191 | 38.171 |
| `1.5B` | scaffolded | 1171.000 | 25.000 | 0.745 | 1.218 | 46.338 |
| `3B` | bare | 716.000 | 22.000 | 0.912 | 1.646 | 29.288 |
| `3B` | scaffolded | 1171.000 | 22.000 | 0.997 | 1.817 | 29.673 |
| `7B` | bare | 716.000 | 24.000 | 1.174 | 2.205 | 27.636 |
| `7B` | scaffolded | 1171.000 | 23.000 | 1.442 | 2.243 | 28.047 |

## 10. Effect of scaffolding

| model | bare | scaffolded | difference |
|---|---:|---:|---:|
| `0.5B` | 14.3% | 4.8% | -0.095 |
| `1.5B` | 42.9% | 57.1% | +0.143 |
| `3B` | 57.1% | 81.0% | +0.238 |
| `7B` | 71.4% | 90.5% | +0.190 |

## 11. Uncertainty

Accuracy proportions carry Wilson 95% intervals. Language-vs-identity comparisons use matched items with a 95% paired item-level bootstrap (10 000 resamples, seed 20260910) and an exact McNemar test on the discordant pairs. With 21 generation cases the intervals are wide: read effect sizes and intervals, not p-values.

## 12. What can and cannot be concluded

**Can:** how many model tokens this language cost, how long it took, how often its outputs lexed, parsed, meant nothing, or meant the right thing, and how that compares to identity on the very same items.

**Cannot:** that tokenizer fertility *caused* any accuracy difference. Spelling, tokenization all change together here; nothing isolates one. No winner is selected, and nothing here makes any candidate eligible under Experiment 01's fertility gate.
