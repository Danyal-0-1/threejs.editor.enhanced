# `alpha` — language report

_Run `20260914T212711Z` · an exploratory fertility-unmatched model evaluation._

## 1. What this language changes

**The interference condition — familiar spellings, wrong meanings.** Alpha reuses 3DOM's own vocabulary but PERMUTES which role each word plays. The word `recolor` spells the *function keyword*; the word `scale` spells the *recolour* operation; `mesh` spells *receiveShadow*; the class sigil is `#` and the id sigil is `:`. Every spelling is familiar and almost every one means something else. Its relative tokenizer fertility is 1.068 (Qwen2) / 1.073 (DeepSeek-V3) — the mildest of the three, though still outside Experiment 01's [0.95, 1.05] band.


## 2. Tokenizer cost (a confound, not a verdict)

| tokenizer | tokens/program | tokens/char | vs identity | byte-fallback fragments |
|---|---:|---:|---:|---:|
| `Qwen2 BPE (shared by all 4 Qwen2.5-Coder repos)` | 20.306 | 0.3750 | 1.068× | 0.000% |
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
| `0.5B` | 0.0% (0/21, 95% CI 0.0%–15.5%) | 61.9% | 100.0% | 0.0% | -0.143 | [-0.286, +0.000] | 0.2500 (n_disc=3) |
| `1.5B` | 14.3% (3/21, 95% CI 5.0%–34.6%) | 71.4% | 100.0% | 0.0% | -0.286 | [-0.476, -0.095] | 0.0312 (n_disc=6) |
| `3B` | 19.0% (4/21, 95% CI 7.7%–40.0%) | 61.9% | 100.0% | 0.0% | -0.381 | [-0.571, -0.190] | 0.0078 (n_disc=8) |
| `7B` | 0.0% (0/21, 95% CI 0.0%–15.5%) | 9.5% | 100.0% | 0.0% | -0.714 | [-0.905, -0.524] | 0.0001 (n_disc=15) |

### scaffolded

| instruct model | semantic accuracy | parse validity | language compliance | vacuous | Δ vs identity | 95% paired CI | McNemar p |
|---|---|---|---|---:|---:|---|---:|
| `0.5B` | 0.0% (0/21, 95% CI 0.0%–15.5%) | 0.0% | 100.0% | 0.0% | -0.048 | [-0.143, +0.000] | 1.0000 (n_disc=1) |
| `1.5B` | 38.1% (8/21, 95% CI 20.8%–59.1%) | 81.0% | 100.0% | 0.0% | -0.190 | [-0.381, -0.048] | 0.1250 (n_disc=4) |
| `3B` | 42.9% (9/21, 95% CI 24.5%–63.5%) | 95.2% | 100.0% | 0.0% | -0.381 | [-0.571, -0.190] | 0.0078 (n_disc=8) |
| `7B` | 4.8% (1/21, 95% CI 0.8%–22.7%) | 9.5% | 100.0% | 0.0% | -0.857 | [-1.000, -0.714] | 0.0000 (n_disc=18) |

## 6. Task-specific strengths and failures

| model | condition | op-selection | selector-resolution | arg-extraction | multi-op |
|---|---|---|---|---|---|
| `0.5B` | bare | 9.5% (2/21) | 19.0% (4/21) | 38.1% (8/21) | 9.5% (2/21) |
| `0.5B` | scaffolded | 0.0% (0/21) | 0.0% (0/21) | 0.0% (0/21) | 0.0% (0/21) |
| `1.5B` | bare | 47.6% (10/21) | 38.1% (8/21) | 52.4% (11/21) | 38.1% (8/21) |
| `1.5B` | scaffolded | 57.1% (12/21) | 57.1% (12/21) | 66.7% (14/21) | 57.1% (12/21) |
| `3B` | bare | 33.3% (7/21) | 42.9% (9/21) | 47.6% (10/21) | 33.3% (7/21) |
| `3B` | scaffolded | 61.9% (13/21) | 71.4% (15/21) | 81.0% (17/21) | 57.1% (12/21) |
| `7B` | bare | 4.8% (1/21) | 0.0% (0/21) | 4.8% (1/21) | 4.8% (1/21) |
| `7B` | scaffolded | 4.8% (1/21) | 9.5% (2/21) | 9.5% (2/21) | 4.8% (1/21) |

## 7. Parse failures versus semantic failures

| model | condition | LEX_FAIL | PARSE_FAIL | VALID_VACUOUS | VALID_WRONG | VALID_CORRECT |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 0 | 8 | 0 | 13 | 0 |
| `0.5B` | scaffolded | 0 | 21 | 0 | 0 | 0 |
| `1.5B` | bare | 0 | 6 | 0 | 12 | 3 |
| `1.5B` | scaffolded | 0 | 4 | 0 | 9 | 8 |
| `3B` | bare | 0 | 8 | 0 | 9 | 4 |
| `3B` | scaffolded | 0 | 1 | 0 | 11 | 9 |
| `7B` | bare | 0 | 19 | 0 | 2 | 0 |
| `7B` | scaffolded | 0 | 19 | 0 | 1 | 1 |

These are orthogonal constructs and are never averaged. A program can parse perfectly and mean the wrong thing (`VALID_WRONG`), or parse and mean nothing at all (`VALID_VACUOUS` — a parse success and a task failure).

### Hallucination categories

| model | condition | invented_operation | invented_selector | invented_argument | wrong_language_spelling | extra_operation | missing_operation | prose_instead_of_code |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `0.5B` | bare | 11 | 7 | 5 | 0 | 2 | 0 | 0 |
| `0.5B` | scaffolded | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `1.5B` | bare | 5 | 6 | 4 | 0 | 2 | 0 | 0 |
| `1.5B` | scaffolded | 5 | 0 | 3 | 0 | 1 | 0 | 0 |
| `3B` | bare | 6 | 4 | 3 | 0 | 0 | 0 | 0 |
| `3B` | scaffolded | 7 | 0 | 3 | 0 | 1 | 0 | 0 |
| `7B` | bare | 1 | 2 | 1 | 0 | 0 | 0 | 0 |
| `7B` | scaffolded | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

A parse failure is **not** counted as a hallucination.

## 8. Representative outputs

**Correct:**

- **`all-four-wheels`** · 1.5B · scaffolded · outcome `VALID_CORRECT`
  - request: _make all four wheels black_
  - model wrote: `(recolor(){ $$('#wheel')#scale('#000000'); })();`
  - parsed to: `[{"op": "recolor", "selector": ".wheel", "args": {"color": "#000000"}}]`
  - resolved nodes: `[["Object_20", "Object_21", "Object_22", "Object_23"]]`
  - scorer said: verb(s) ok: recolor; right nodes, nothing extra; n/a (case carries no arg expectation); 1 op(s), types ok
- **`bed-and-lights`** · 1.5B · scaffolded · outcome `VALID_CORRECT`
  - request: _paint the bed red and remove the tail lights_
  - model wrote: `(recolor(){ $$('#dump-bed')#scale('#ff0000'); $$('#tail-light')#spin(); })();`
  - parsed to: `[{"op": "recolor", "selector": ".dump-bed", "args": {"color": "#ff0000"}}, {"op": "delete", "selector": ".tail-light", "args": {}}]`
  - resolved nodes: `[["Object_07"], ["Object_12", "Object_13"]]`
  - scorer said: verb(s) ok: recolor, delete; right nodes, nothing extra; n/a (case carries no arg expectation); 2 op(s), types ok


**Failed:**

- **`all-four-wheels`** · 0.5B · bare · outcome `VALID_WRONG`
  - request: _make all four wheels black_
  - model wrote: `(recolor(){ $$('#wheel')#setMaterial('#000000'); $$('#wheel')#setOpacity('#000000'); $$('#wheel')#setMaterial('#000000'); $$('#wheel')#setOpacity('#000000'); })();`
  - parsed to: `[{"op": "duplicate", "selector": ".wheel", "args": {"dx": "#000000"}}, {"op": "setMaterial", "selector": ".wheel", "args": {"material": "#000000"}}, {"op": "duplicate", "selector": ".wheel", "args": {`
  - resolved nodes: `[["Object_20", "Object_21", "Object_22", "Object_23"], ["Object_20", "Object_21", "Object_22", "Object_23"], ["Object_20", "Object_21", "Object_22", "Object_23"`
  - scorer said: op0: "duplicate" != "recolor"; right nodes, nothing extra; n/a (case carries no arg expectation); 4 ops != target 1 (over-split)
- **`all-four-wheels`** · 0.5B · scaffolded · outcome `PARSE_FAIL`
  - request: _make all four wheels black_
  - model wrote: `recolor(){
  $$('#dump-truck').#duplicate('y',1,2);
  $$('#object-03').#scale('#00ff00');
  $$('#object-07').#move(2);
  $$('#object-12').#rotate(0,1,0)#scale('#ff0000');
  $$('#object-13').#rotate(0,`
  - parsed to: `null`
  - resolved nodes: `null`
  - scorer said: tokenised, but no derivation exists


## 9. Runtime and token cost

| model | condition | input tok (med) | output tok (med) | e2e s (med) | e2e s (p95) | tok/s |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 720.000 | 23.000 | 0.518 | 1.204 | 45.566 |
| `0.5B` | scaffolded | 1175.000 | 80.000 | 1.835 | 11.609 | 45.102 |
| `1.5B` | bare | 720.000 | 24.000 | 0.664 | 1.062 | 39.032 |
| `1.5B` | scaffolded | 1175.000 | 23.000 | 0.745 | 1.130 | 38.048 |
| `3B` | bare | 720.000 | 22.000 | 0.921 | 1.584 | 29.279 |
| `3B` | scaffolded | 1175.000 | 23.000 | 1.058 | 1.761 | 29.675 |
| `7B` | bare | 720.000 | 24.000 | 1.216 | 1.866 | 28.004 |
| `7B` | scaffolded | 1175.000 | 25.000 | 1.488 | 2.166 | 28.197 |

## 10. Effect of scaffolding

| model | bare | scaffolded | difference |
|---|---:|---:|---:|
| `0.5B` | 0.0% | 0.0% | +0.000 |
| `1.5B` | 14.3% | 38.1% | +0.238 |
| `3B` | 19.0% | 42.9% | +0.238 |
| `7B` | 0.0% | 4.8% | +0.048 |

## 11. Uncertainty

Accuracy proportions carry Wilson 95% intervals. Language-vs-identity comparisons use matched items with a 95% paired item-level bootstrap (10 000 resamples, seed 20260910) and an exact McNemar test on the discordant pairs. With 21 generation cases the intervals are wide: read effect sizes and intervals, not p-values.

## 12. What can and cannot be concluded

**Can:** how many model tokens this language cost, how long it took, how often its outputs lexed, parsed, meant nothing, or meant the right thing, and how that compares to identity on the very same items.

**Cannot:** that tokenizer fertility *caused* any accuracy difference. Spelling, tokenization all change together here; nothing isolates one. No winner is selected, and nothing here makes any candidate eligible under Experiment 01's fertility gate.
