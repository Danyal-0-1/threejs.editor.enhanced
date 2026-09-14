# `gamma` — language report

_Run `20260914T212711Z` · an exploratory fertility-unmatched model evaluation._

## 1. What this language changes

**The glyph / surface-distance condition — and a lexer stress test.** Gamma substitutes compact non-ASCII symbols (`⏦` for recolour, `⍤` for the function keyword, `⟠⟠` for the selector entry, `◈` for the class sigil). It uses FEWER Unicode code points than 3DOM (0.716×) yet the most tokens: relative fertility 1.937 (Qwen2) / 2.285 (DeepSeek-V3), with 36.4% / 55.0% of token ids showing byte-fallback fragmentation.

**Gamma is not a clean isomorphic control.** Experiment 01's proposed check (g) found 24 issues: 22 `g1` findings (word-class spellings became symbols, changing how keywords are told apart from identifiers) and 2 `g2` reachability findings (token sequences reachable in gamma that no 3DOM text can produce — e.g. `meshmesh` is one identifier in 3DOM while `⍇⍇` can stay two type tokens). Gamma results must be read as a Unicode/lexer diagnostic, never as evidence about isomorphic syntax alone.


## 2. Tokenizer cost (a confound, not a verdict)

| tokenizer | tokens/program | tokens/char | vs identity | byte-fallback fragments |
|---|---:|---:|---:|---:|
| `Qwen/Qwen2.5-Coder-0.5B` | 26.968 | 0.6802 | 1.937× | 36.364% |
| `deepseek-ai/DeepSeek-V3` | 30.274 | 0.7636 | 2.285× | 55.035% |

Fertility demonstrates **token cost**. Whether accuracy degrades is a separate measurement, reported in §5.

## 3. What was fed to each model

**Lane A (base checkpoints):** the program string alone — no editing request, no instruction prompt, empty neutral prefix, identical policy in every language. Teacher-forced scoring only; **no training occurred**.

**Lane B (instruct checkpoints):** a system prompt containing the mechanically rendered language specification for **this** language (program shape, selector forms, all 15 operations with their argument names and a plain-English description, four worked examples), plus a user message with the natural-language editing request. In `scaffolded` the user message also carries the scene's addressable parts and tag list, rendered with this language's sigils.

Every spelling shown was **this language's own**; no 3DOM spelling was taught to an alien arm and no translation pair appeared in any prompt (enforced by `taught_spellings` tests). The exact model input for every case is saved under `prompts/rendered/`.

## 4. Lane A — base-model surprise

| base model | device | NLL/char | NLL/token | perplexity | ΔNLL/char vs identity | 95% CI |
|---|---|---:|---:|---:|---:|---|
| `0.5B` | cuda | 4.1503 | 6.3363 | 564.69 | +2.8189 | [+2.6293, +2.9919] |
| `1.5B` | cuda | 4.3941 | 6.7086 | 819.38 | +3.1218 | [+2.9225, +3.3056] |
| `3B` | cuda | 3.9138 | 5.9752 | 393.54 | +2.6647 | [+2.4849, +2.8321] |
| `7B` | cpu | 4.0497 | 6.1828 | 484.32 | +2.7822 | [+2.5852, +2.9682] |

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
| `0.5B` | 0.0% (0/8, 95% CI 0.0%–32.4%) | 75.0% | 100.0% | 0.0% | +0.000 | [+0.000, +0.000] | 1.0000 (n_disc=0) |

## 6. Task-specific strengths and failures

| model | condition | op-selection | selector-resolution | arg-extraction | multi-op |
|---|---|---|---|---|---|
| `0.5B` | bare | 12.5% (1/8) | 12.5% (1/8) | 12.5% (1/8) | 12.5% (1/8) |
| `0.5B` | scaffolded | 12.5% (1/8) | 12.5% (1/8) | 12.5% (1/8) | 12.5% (1/8) |

## 7. Parse failures versus semantic failures

| model | condition | LEX_FAIL | PARSE_FAIL | VALID_VACUOUS | VALID_WRONG | VALID_CORRECT |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 0 | 0 | 0 | 8 | 0 |
| `0.5B` | scaffolded | 0 | 2 | 0 | 6 | 0 |

These are orthogonal constructs and are never averaged. A program can parse perfectly and mean the wrong thing (`VALID_WRONG`), or parse and mean nothing at all (`VALID_VACUOUS` — a parse success and a task failure).

### Hallucination categories

| model | condition | invented_operation | invented_selector | invented_argument | wrong_language_spelling | extra_operation | missing_operation | prose_instead_of_code |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `0.5B` | bare | 7 | 6 | 7 | 0 | 0 | 0 | 0 |
| `0.5B` | scaffolded | 5 | 5 | 5 | 0 | 0 | 0 | 0 |

A parse failure is **not** counted as a hallucination.

## 8. Representative outputs

**Correct:**

_none recorded_


**Failed:**

- **`bigger`** · 0.5B · bare · outcome `VALID_WRONG`
  - request: _make it bigger_
  - model wrote: `(⍤(){ ⟠⟠('◈rotate')◈⌇('x',1,2); })();`
  - parsed to: `[{"op": "spin", "selector": ".rotate", "args": {"axis": "x", "duration": 2, "turns": 1}}]`
  - resolved nodes: `[[]]`
  - scorer said: op0: "spin" != "scale"; op0: missed DumpTruck; missing arg factor; op0 "spin" != "scale"
- **`bigger`** · 0.5B · scaffolded · outcome `PARSE_FAIL`
  - request: _make it bigger_
  - model wrote: `(⍤(){ ⟠⟠('◈rotate')◈⌇('y',1,2); })();
(⍤(){ ⟠⟠('◈lamp')◈⌎(0.5); ⟠⟠('◈pylon')◈⏥(2); })();
(⍤(){ ⟠⟠('◈strut')◈⏢(0,1,0)◈⏦('#ff0000'); })();
(⍤(){ ⟠⟠('◈material')◈⌎('steel'); })();
(⍤(){ ⟠⟠('◈opacity')◈1;`
  - parsed to: `null`
  - resolved nodes: `null`
  - scorer said: tokenised, but no derivation exists


## 9. Runtime and token cost

| model | condition | input tok (med) | output tok (med) | e2e s (med) | e2e s (p95) | tok/s |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 807.000 | 22.000 | 0.516 | 0.617 | 45.369 |
| `0.5B` | scaffolded | 1281.000 | 27.500 | 0.649 | 7.883 | 45.288 |

## 10. Effect of scaffolding

| model | bare | scaffolded | difference |
|---|---:|---:|---:|
| `0.5B` | 0.0% | 0.0% | +0.000 |

## 11. Uncertainty

Accuracy proportions carry Wilson 95% intervals. Language-vs-identity comparisons use matched items with a 95% paired item-level bootstrap (10 000 resamples, seed 20260910) and an exact McNemar test on the discordant pairs. With 21 generation cases the intervals are wide: read effect sizes and intervals, not p-values.

## 12. What can and cannot be concluded

**Can:** how many model tokens this language cost, how long it took, how often its outputs lexed, parsed, meant nothing, or meant the right thing, and how that compares to identity on the very same items.

**Cannot:** that tokenizer fertility *caused* any accuracy difference. Spelling, tokenization, and lexical reachability all change together here; nothing isolates one. No winner is selected, and nothing here makes any candidate eligible under Experiment 01's fertility gate.

**Gamma specifically:** the 24 check-(g) findings mean gamma is a Unicode/lexer stress diagnostic, not a clean isomorphism test. Dense-prior claims must not rest on gamma alone.
