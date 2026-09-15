# `gamma` — language report

_Run `20260914T212711Z` · an exploratory fertility-unmatched model evaluation._

## 1. What this language changes

**The glyph / surface-distance condition — and a lexer stress test.** Gamma substitutes compact non-ASCII symbols (`⏦` for recolour, `⍤` for the function keyword, `⟠⟠` for the selector entry, `◈` for the class sigil). It uses FEWER Unicode code points than 3DOM (0.716×) yet the most tokens: relative fertility 1.937 (Qwen2) / 2.285 (DeepSeek-V3), with 36.4% / 55.0% of token ids showing byte-fallback fragmentation.

**Gamma is not a clean isomorphic control.** Experiment 01's proposed check (g) found 24 issues: 22 `g1` findings (word-class spellings became symbols, changing how keywords are told apart from identifiers) and 2 `g2` reachability findings (token sequences reachable in gamma that no 3DOM text can produce — e.g. `meshmesh` is one identifier in 3DOM while `⍇⍇` can stay two type tokens). Gamma results must be read as a Unicode/lexer diagnostic, never as evidence about isomorphic syntax alone.


## 2. Tokenizer cost (a confound, not a verdict)

| tokenizer | tokens/program | tokens/char | vs identity | byte-fallback fragments |
|---|---:|---:|---:|---:|
| `Qwen2 BPE (shared by all 4 Qwen2.5-Coder repos)` | 26.968 | 0.6802 | 1.937× | 36.364% |
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
| `0.5B` | 0.0% (0/21, 95% CI 0.0%–15.5%) | 95.2% | 100.0% | 0.0% | -0.143 | [-0.286, +0.000] | 0.2500 (n_disc=3) |
| `1.5B` | 19.0% (4/21, 95% CI 7.7%–40.0%) | 66.7% | 100.0% | 0.0% | -0.238 | [-0.429, -0.048] | 0.0625 (n_disc=5) |
| `3B` | 38.1% (8/21, 95% CI 20.8%–59.1%) | 81.0% | 100.0% | 0.0% | -0.190 | [-0.381, -0.048] | 0.1250 (n_disc=4) |
| `7B` | 33.3% (7/21, 95% CI 17.2%–54.6%) | 42.9% | 100.0% | 0.0% | -0.381 | [-0.571, -0.190] | 0.0078 (n_disc=8) |

### scaffolded

| instruct model | semantic accuracy | parse validity | language compliance | vacuous | Δ vs identity | 95% paired CI | McNemar p |
|---|---|---|---|---:|---:|---|---:|
| `0.5B` | 0.0% (0/21, 95% CI 0.0%–15.5%) | 52.4% | 100.0% | 0.0% | -0.048 | [-0.143, +0.000] | 1.0000 (n_disc=1) |
| `1.5B` | 38.1% (8/21, 95% CI 20.8%–59.1%) | 95.2% | 100.0% | 0.0% | -0.190 | [-0.381, -0.048] | 0.1250 (n_disc=4) |
| `3B` | 61.9% (13/21, 95% CI 40.9%–79.2%) | 85.7% | 100.0% | 0.0% | -0.190 | [-0.429, +0.000] | 0.2188 (n_disc=6) |
| `7B` | 38.1% (8/21, 95% CI 20.8%–59.1%) | 38.1% | 100.0% | 0.0% | -0.524 | [-0.714, -0.286] | 0.0010 (n_disc=11) |

## 6. Task-specific strengths and failures

| model | condition | op-selection | selector-resolution | arg-extraction | multi-op |
|---|---|---|---|---|---|
| `0.5B` | bare | 4.8% (1/21) | 9.5% (2/21) | 61.9% (13/21) | 4.8% (1/21) |
| `0.5B` | scaffolded | 4.8% (1/21) | 4.8% (1/21) | 28.6% (6/21) | 4.8% (1/21) |
| `1.5B` | bare | 38.1% (8/21) | 38.1% (8/21) | 57.1% (12/21) | 33.3% (7/21) |
| `1.5B` | scaffolded | 57.1% (12/21) | 66.7% (14/21) | 85.7% (18/21) | 52.4% (11/21) |
| `3B` | bare | 66.7% (14/21) | 47.6% (10/21) | 76.2% (16/21) | 66.7% (14/21) |
| `3B` | scaffolded | 71.4% (15/21) | 76.2% (16/21) | 81.0% (17/21) | 71.4% (15/21) |
| `7B` | bare | 42.9% (9/21) | 33.3% (7/21) | 42.9% (9/21) | 42.9% (9/21) |
| `7B` | scaffolded | 38.1% (8/21) | 38.1% (8/21) | 38.1% (8/21) | 38.1% (8/21) |

## 7. Parse failures versus semantic failures

| model | condition | LEX_FAIL | PARSE_FAIL | VALID_VACUOUS | VALID_WRONG | VALID_CORRECT |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 0 | 1 | 0 | 20 | 0 |
| `0.5B` | scaffolded | 0 | 10 | 0 | 11 | 0 |
| `1.5B` | bare | 0 | 7 | 0 | 10 | 4 |
| `1.5B` | scaffolded | 0 | 1 | 0 | 12 | 8 |
| `3B` | bare | 0 | 4 | 0 | 9 | 8 |
| `3B` | scaffolded | 0 | 3 | 0 | 5 | 13 |
| `7B` | bare | 0 | 12 | 0 | 2 | 7 |
| `7B` | scaffolded | 0 | 13 | 0 | 0 | 8 |

These are orthogonal constructs and are never averaged. A program can parse perfectly and mean the wrong thing (`VALID_WRONG`), or parse and mean nothing at all (`VALID_VACUOUS` — a parse success and a task failure).

### Hallucination categories

| model | condition | invented_operation | invented_selector | invented_argument | wrong_language_spelling | extra_operation | missing_operation | prose_instead_of_code |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `0.5B` | bare | 19 | 12 | 7 | 0 | 2 | 0 | 0 |
| `0.5B` | scaffolded | 10 | 10 | 5 | 0 | 0 | 1 | 0 |
| `1.5B` | bare | 6 | 3 | 2 | 0 | 1 | 0 | 0 |
| `1.5B` | scaffolded | 8 | 2 | 2 | 0 | 2 | 0 | 0 |
| `3B` | bare | 3 | 5 | 1 | 0 | 0 | 0 | 0 |
| `3B` | scaffolded | 3 | 0 | 1 | 0 | 0 | 0 | 0 |
| `7B` | bare | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| `7B` | scaffolded | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

A parse failure is **not** counted as a hallucination.

## 8. Representative outputs

**Correct:**

- **`all-four-wheels`** · 1.5B · bare · outcome `VALID_CORRECT`
  - request: _make all four wheels black_
  - model wrote: `(⍤(){ ⟠⟠('◈wheel')◈⏦('#000000'); })();`
  - parsed to: `[{"op": "recolor", "selector": ".wheel", "args": {"color": "#000000"}}]`
  - resolved nodes: `[["Object_20", "Object_21", "Object_22", "Object_23"]]`
  - scorer said: verb(s) ok: recolor; right nodes, nothing extra; n/a (case carries no arg expectation); 1 op(s), types ok
- **`all-four-wheels`** · 1.5B · scaffolded · outcome `VALID_CORRECT`
  - request: _make all four wheels black_
  - model wrote: `(⍤(){ ⟠⟠('◈wheel')◈⏦('#000000'); })();`
  - parsed to: `[{"op": "recolor", "selector": ".wheel", "args": {"color": "#000000"}}]`
  - resolved nodes: `[["Object_20", "Object_21", "Object_22", "Object_23"]]`
  - scorer said: verb(s) ok: recolor; right nodes, nothing extra; n/a (case carries no arg expectation); 1 op(s), types ok


**Failed:**

- **`all-four-wheels`** · 0.5B · bare · outcome `VALID_WRONG`
  - request: _make all four wheels black_
  - model wrote: `(⍤(){ ⟠⟠('◈wheels')◈⌇('black'); })();`
  - parsed to: `[{"op": "spin", "selector": ".wheels", "args": {"axis": "black"}}]`
  - resolved nodes: `[[]]`
  - scorer said: op0: "spin" != "recolor"; op0: missed Object_20, Object_21, Object_22, Object_23; n/a (case carries no arg expectation); op0 "spin" != "recolor"
- **`all-four-wheels`** · 0.5B · scaffolded · outcome `VALID_WRONG`
  - request: _make all four wheels black_
  - model wrote: `(⍤(){ ⟠⟠('◈black')◈⌇('black'); })();`
  - parsed to: `[{"op": "spin", "selector": ".black", "args": {"axis": "black"}}]`
  - resolved nodes: `[[]]`
  - scorer said: op0: "spin" != "recolor"; op0: missed Object_20, Object_21, Object_22, Object_23; n/a (case carries no arg expectation); op0 "spin" != "recolor"


## 9. Runtime and token cost

| model | condition | input tok (med) | output tok (med) | e2e s (med) | e2e s (p95) | tok/s |
|---|---|---:|---:|---:|---:|---:|
| `0.5B` | bare | 808.000 | 24.000 | 0.548 | 1.216 | 45.246 |
| `0.5B` | scaffolded | 1282.000 | 29.000 | 0.697 | 11.743 | 44.901 |
| `1.5B` | bare | 808.000 | 30.000 | 0.874 | 1.393 | 37.347 |
| `1.5B` | scaffolded | 1282.000 | 29.000 | 0.915 | 1.351 | 37.948 |
| `3B` | bare | 808.000 | 28.000 | 1.142 | 2.271 | 29.135 |
| `3B` | scaffolded | 1282.000 | 29.000 | 1.234 | 2.335 | 29.333 |
| `7B` | bare | 808.000 | 29.000 | 1.453 | 2.485 | 28.409 |
| `7B` | scaffolded | 1282.000 | 30.000 | 1.684 | 9.599 | 27.923 |

## 10. Effect of scaffolding

| model | bare | scaffolded | difference |
|---|---:|---:|---:|
| `0.5B` | 0.0% | 0.0% | +0.000 |
| `1.5B` | 19.0% | 38.1% | +0.190 |
| `3B` | 38.1% | 61.9% | +0.238 |
| `7B` | 33.3% | 38.1% | +0.048 |

## 11. Uncertainty

Accuracy proportions carry Wilson 95% intervals. Language-vs-identity comparisons use matched items with a 95% paired item-level bootstrap (10 000 resamples, seed 20260910) and an exact McNemar test on the discordant pairs. With 21 generation cases the intervals are wide: read effect sizes and intervals, not p-values.

## 12. What can and cannot be concluded

**Can:** how many model tokens this language cost, how long it took, how often its outputs lexed, parsed, meant nothing, or meant the right thing, and how that compares to identity on the very same items.

**Cannot:** that tokenizer fertility *caused* any accuracy difference. Spelling, tokenization, and lexical reachability all change together here; nothing isolates one. No winner is selected, and nothing here makes any candidate eligible under Experiment 01's fertility gate.

**Gamma specifically:** the 24 check-(g) findings mean gamma is a Unicode/lexer stress diagnostic, not a clean isomorphism test. Dense-prior claims must not rest on gamma alone.
