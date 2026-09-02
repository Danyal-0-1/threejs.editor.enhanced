# RESULTS.md — results actually obtained

**Experiment:** `run/experiments/20260901-233702` (UTC) ·
**Commit at start:** `c3f9b26` ·
**Machine:** Ubuntu 24.04.4, Python 3.12.3, i7-12700H, 62 GB RAM,
RTX 3080 Ti Laptop 16 GB (unused) ·
**Versions:** `lark 1.3.1`, `jsonschema 4.10.3` (structural lane);
`transformers 5.16.1`, `tokenizers 0.23.1`, `huggingface_hub 1.29.0` (Lane B venv)

Every number below was produced by a command in this experiment directory.
Nothing is copied from prior documentation. Where a measurement was not run, it
is marked PENDING and left blank — not estimated.

**Status labels:** VERIFIED · FAILED · BLOCKED · REPORTED-BUT-NOT-REPRODUCED ·
INFERRED · PENDING-EMPIRICAL-MEASUREMENT · RESEARCH-DECISION-REQUIRED

---

## 1. Structural results (no models, no network)

### 1.1 Phase 1 contract — **VERIFIED**

`grammar_and_3DOM_client/conformance/coverage2.py` → exit 0.

```
corpus sizes: positive=62  negative=64  vacuous=12
G1 OK — all 62 positives parse to exactly one derivation
G2 OK — production coverage = 100% (57/57 branches)
G3 OK — all 64 negatives rejected
G4 OK — all 12 vacuous items parse with zero operations
G5 OK — '.car .wheel' (descendant) != '.car.wheel' (compound AND)
G6 OK — Earley and DFA agree on all 138 corpus items (same language)
RESULT: PASS — all gates green
```

> Note: `conformance/coverage.py` (without the `2`) still crashes with
> `FileNotFoundError: .../conformance/negatives.txt` — the file is
> `negative.txt`. Phase 1 defect, out of scope, not fixed.

### 1.2 φ validation V1–V8 — **VERIFIED**

`src/phi.py identity alpha beta gamma` → exit 0.

```
terminals.json  3dom-grammar/1.1.0
  43 terminals, 29 substitutable, 14 frozen
  spelling partition: 28 distinct substitutable spellings
OK  φ='identity'  29 substitutions, 1 overload group(s)
OK  φ='alpha'     29 substitutions, 1 overload group(s)
OK  φ='beta'      29 substitutions, 1 overload group(s)
OK  φ='gamma'     29 substitutions, 1 overload group(s)
```

### 1.3 Template reconstruction and grammar rendering — **VERIFIED**

| Check | Result |
|---|---|
| `build_templates.py` identity render == Phase 1 | both notations ✓, **29 distinct slots** each, byte-identical |
| Templates after rebuild vs committed | **IDENTICAL** |
| `render_grammar.py` G-R1…G-R4 | pass for α, β, γ |
| G-R5 (both levels load in Lark/Earley) | ✓ for α, β, γ |
| G-R6 (appendices re-parse as EBNF) | ✓ `\|N\|=31, \|P\|=58` in both notations, all three |
| Regenerated grammars vs committed | **IDENTICAL** (12 files) |

### 1.4 Corpus gates A1–A7 — **VERIFIED**

`src/generate_corpus.py alpha beta gamma --check-only` → exit 0.

```
φ = alpha    A1–A7 PASS
φ = beta     A1–A7 PASS
φ = gamma    A1–A7 PASS
```

A4 is now strictly stronger than when this was last run: it asserts zero VERB
tokens **and** `len(parse(p, φ).ops) == 0`. It still passes.

### 1.5 Collision checks (a)–(g) — **VERIFIED**

`measure/collisions.py identity alpha beta gamma --md` → exit 0.

| Lexicon | (a) | (b) | (c) | (d) | (e) | (f) | **(g) proposed** |
|---|---|---|---|---|---|---|---|
| `identity` | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `alpha` | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `beta` | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `gamma` | PASS | PASS | PASS | PASS | PASS | PASS | **FAIL (24)** |

CONSTRAINT 2 — checks (a)–(f) — is clean for all four.

**γ's 24 findings reproduce the documented count exactly**: 22 × g1 (lexical
class) + 2 × g2 (reachability). Full list at
`results/collisions-check-g-gamma.txt`. The two g2 witnesses:

```
g2 (outer) function+function lexes to 1 token in 3DOM but ⍤+⍤ lexes to 2
g2 (inner) mesh+mesh         lexes to 1 token in 3DOM but ⍇+⍇ lexes to 2
```

In 3DOM, `meshmesh` is one `IDENT`, so the token sequence TYPE TYPE is
**unreachable from any 3DOM string**. In γ it is reachable. L(γ) is a strict
superset of φ(L(3DOM)) — they are not isomorphic, whatever the production counts
say. V1–V8 still pass because bijectivity of the *spelling map* says nothing
about the *lexical class* of the spellings.

### 1.6 DFA parity — **VERIFIED**

`measure/dfa_parity.py --md`, tolerance **0.000** (pre-committed).

| lexicon | DFA states | mean branching | max branching | mean DSL tokens/program | parity |
|---|---|---|---|---|---|
| `identity` | 52 | 3.980 | 9 | 26.92 | **PASS** |
| `alpha` | 52 | 3.980 | 9 | 26.92 | **PASS** |
| `beta` | 52 | 3.980 | 9 | 26.92 | **PASS** |
| `gamma` | 52 | 3.980 | 9 | 26.92 | **PASS** |

P1 (token alphabet), P2 (per-item token stream), P4 (positional profile) all
identical. `measure/metrics_parity.py` regenerates `reports/METRICS_PARITY.md`
**byte-identically**.

### 1.7 Test suites — **VERIFIED**, reported independently

| Suite | Result | Covers |
|---|---|---|
| `test_isomorphism.py` | **4/4** | IR identity over positive + vacuous corpora; negatives stay negative; schema validation (with `jsonschema` present, so it genuinely ran) |
| `test_roundtrip.py` | **8/8** | φ bijection on text; text→IR→text; IR→text→IR; C1/C2; loader fails loudly |
| `test_invariants.py` | **14/14** | I1–I10 + templates render to Phase 1 under identity |
| `test_canonicalization.py` | **34/34** | C0–C8 with negative tests; `-O` safety; emitter dispatch; intent-vs-structure |
| `test_phi_validation.py` | **25/25** | V1–V8 on a miniature table; inversion; identity via the same API |
| `test_grammar_whitespace.py` | **21/21** | L2 whitespace, C9, quote symmetry, ambiguity, parser cache |
| `test_seams.py` | **14/14** | Lark ≡ DFA over 552 item/lexicon pairs; transliterator totality and defect preservation |
| `test_measure_formulas.py` | **22/22** | fertility and ΔNLL arithmetic against fakes; bootstrap |
| `test_preflight.py` | **7/7** | missing-Phase-1 behaviour via subprocesses |
| **Total** | **149/149** | 26 pre-existing + 123 added |

### 1.8 End-to-end trace — **VERIFIED**

`results/trace-end-to-end.txt`. One program through all four lexicons:

```
3DOM  : (function(){ $S('.wheel.front').scale(1.5); })();
alpha : (recolor(){ $$('#wheel#front')#move(1.5); })();
beta  : (mumvumfe(){ &Q('~wheel~front')~bungi(1.5); })();
gamma : (⍤(){ ⟠⟠('◈wheel◈front')◈⏥(1.5); })();
```

The β image matches the expected form in the audit brief exactly.

All four produce the **identical** DSL token-type stream (25 tokens), the
identical canonical JSON, and the identical digest:

```json
{"grammar_version":"3dom-grammar/1.1.0","ops":[{"args":{"factor":1.5},
 "op":"scale","selector":{"raw":".front.wheel","steps":[{"combinator":null,
 "matchers":[{"kind":"class","name":"front"},{"kind":"class","name":"wheel"}]}]}}]}
```

```
identity / alpha / beta / gamma
  → c2fd72263892a4b034de4ef09a367b8e9970233329d108b5c4c0a5dbe13341a4
```

Field by field: `grammar_version` is C0, pinned to the **grammar**, carrying no
lexicon marker. `op` is anchored on the Lark **terminal name** (`V_SCALE`), not
the surface text, which is what makes it lexicon-independent. `selector.raw` is
`.front.wheel` — re-rendered from the canonical steps in 3DOM reference spelling
(C5) and sorted (C3), never copied from the alien surface. `combinator: null` on
the first step is required by `ir_schema.json`'s enum. `args.factor` is C8's
positional→named mapping for `scale`, and `1.5` is C1-normalised.

φ⁻¹∘φ = identity holds textually for all three, and `emit ∘ ir ∘ parse` is
idempotent in all four.

### 1.9 Structural fertility **PROXY** — VERIFIED as a proxy, **NOT** a metric

| metric | identity | alpha | beta | gamma | β÷3DOM | γ÷3DOM |
|---|---|---|---|---|---|---|
| chars/program | 55.355 | 54.145 | 55.355 | 39.645 | 1.000 | 0.716 |
| utf8 bytes/program | 55.355 | 54.145 | 55.355 | 54.226 | 1.000 | 0.980 |
| bytes/char | 1.000 | 1.000 | 1.000 | 1.368 | 1.000 | 1.368 |
| multibyte chars/program | 0.000 | 0.000 | 0.000 | 7.290 | — | — |
| chars/operation | 15.679 | 15.469 | 15.679 | 9.642 | 1.000 | 0.615 |
| chars/selector | 9.457 | 9.481 | 9.457 | 8.704 | 1.000 | 0.920 |

**This is a character count, not a token count, and it does not satisfy
CONSTRAINT 1.** §2.1 shows exactly how far apart the two are.

### 1.10 Artifact integrity — **VERIFIED**

39 artifacts checksummed (`metadata/checksums.txt`), none missing. Regenerated
grammars, corpora and `METRICS_PARITY.md` are byte-identical to the committed
copies. **No generated artifact was hand-edited; no committed artifact was
modified by any phase.**

---

## 2. Model-dependent results

### 2.1 Tokenizer fertility — **MEASURED. CONSTRAINT 1 FAILS FOR EVERY CANDIDATE.**

`measure/fertility.py --md`, `transformers 5.16.1`,
`AutoTokenizer` with `add_special_tokens=False`, ratios from **corpus totals**.
62-item parallel positive corpus, sha256 `38bbbac1a335d254`. No `tiktoken`.

**Fertility ratio (tok/char, alien ÷ 3DOM). Pre-committed band: [0.95, 1.05].**

| tokenizer | revision | identity | alpha | beta | gamma |
|---|---|---:|---:|---:|---:|
| `Qwen/Qwen2.5-Coder-0.5B` | `8123ea2e…` | 1.000 | **1.068** | **1.401** | **1.937** |
| `Qwen/Qwen2.5-Coder-1.5B` | `df3ce67c…` | 1.000 | **1.068** | **1.401** | **1.937** |
| `Qwen/Qwen2.5-Coder-3B` | `09d9bc5d…` | 1.000 | **1.068** | **1.401** | **1.937** |
| `Qwen/Qwen2.5-Coder-7B` | `0396a761…` | 1.000 | **1.068** | **1.401** | **1.937** |
| `deepseek-ai/DeepSeek-V3` | `e815299b…` | 1.000 | **1.073** | **1.448** | **2.285** |

| candidate | worst ratio | in [0.95, 1.05]? | verdict |
|---|---:|---|---|
| `alpha` | 1.073 | **NO** | **FAIL CONSTRAINT 1** |
| `beta` | 1.448 | **NO** | **FAIL CONSTRAINT 1** |
| `gamma` | 2.285 | **NO** | **FAIL CONSTRAINT 1** |

**Absolute values (Qwen2.5-Coder family, all four identical):**

| metric | identity | alpha | beta | gamma |
|---|---:|---:|---:|---:|
| tokens/program | 19.435 | 20.306 | 27.226 | 26.968 |
| tokens/operation | 7.198 | 7.790 | 9.630 | 8.407 |
| tokens/selector | 3.630 | 3.790 | 4.778 | 5.012 |
| fertility (tok/char) | 0.3511 | 0.3750 | 0.4918 | 0.6802 |
| fertility (tok/utf8-byte) | 0.3511 | 0.3750 | 0.4918 | 0.4970 |
| **fragmented %** | 0.000 | 0.000 | **0.000** | **36.364** |

DeepSeek-V3: fragmented % — identity 0.000, α 0.000, β **0.000**, γ **55.035**.

**The critical reading.** β is *character-length identical* to 3DOM (proxy ratio
1.000) and costs **40% more tokens**. Its pronounceable nonwords are absent from
the BPE vocabulary and split into sub-word pieces at the same character count.
And because β is pure ASCII, its **fragmented-% is 0.000** — the byte-fallback
metric cannot detect this at all. Fragmentation and fertility measure different
things, and only fertility gates the constraint.

γ is the opposite shape: *shorter* in code points (0.716) but 1.368 bytes/char,
so `tok/char` (1.937) and `tok/utf8-byte` (1.416) disagree sharply. Both are now
reported; CONSTRAINT 1 remains defined on `tok/char`, unchanged.

**Methodological note:** the four Qwen repos return **byte-identical numbers**
because they share one tokenizer (`Qwen2Tokenizer`, vocab 151665). The five
listed repos are **two** distinct tokenizers, not five independent measurements.

### 2.2 Prior strength / ΔNLL — **PENDING-EMPIRICAL-MEASUREMENT**

Not run. `torch` is not installed. Nothing is reported.

| quantity | value |
|---|---|
| NLL/token | — |
| NLL/character | — |
| ΔNLL/token | — |
| ΔNLL/character (primary objective) | — |
| 95% CI (paired bootstrap) | — |

The formulas were verified without a model: `ratio_of_totals`, `prefix_offset`
(with and without BOS), and the paired bootstrap (pairing, reproducibility,
edge cases, and CI/point-estimate consistency) are covered by 22 tests in
`test_measure_formulas.py` against deterministic fakes. The full
`score_program` path against synthetic uniform logits runs only when `torch` is
present, and did not run here.

---

## 3. Blocked and pending results

### 3.1 Phase 10 — base-model ΔNLL — **BLOCKED**

- **Why:** `torch` is not installed.
- **Missing dependency:** `torch` (~2.5 GB installed) plus model weights
  (0.5B ≈ 1 GB, 1.5B ≈ 3 GB, 3B ≈ 6 GB, 7B ≈ 15 GB).
- **Hardware:** RTX 3080 Ti 16 GB is sufficient for ≤3B in fp32; 7B fp32 needs
  ~30 GB and would run on CPU.
- **Resume:**
  ```bash
  run/.venv/bin/python -m pip install torch
  cd alien_syntax && ../run/.venv/bin/python measure/prior_strength.py --md
  # or smaller: --models Qwen/Qwen2.5-Coder-0.5B --device cuda
  ```
- **Candidate decision remains provisional?** Moot — it is now *blocked by a
  different, resolved measurement*: CONSTRAINT 1 already excludes all three
  candidates (§2.1).

### 3.2 Candidate selection — **RESEARCH-DECISION-REQUIRED**

**No winner is selected, and the previously provisional winner β is withdrawn.**

Two independent reasons:

1. CONSTRAINT 1 is now measured and **no candidate satisfies it**. β was selected
   on the structural proxy (1.000); the binding measurement is 1.401–1.448.
2. ΔNLL, the primary objective, has never been measured.

γ additionally fails reachability check (g) and shows 36–55% byte fallback, so it
remains a **stress diagnostic, not a clean control**.

Options, consequences and the exact code that would change are in
`run/AUDIT.md §11 (RD-1)`. The smallest defensible recommendation: re-engineer β
against a **token-count** objective using the existing
`candidates/gen_beta_lexicon.py`, preserving the pre-committed band rather than
widening it after seeing the numbers.

### 3.3 Not attempted

| Item | Why |
|---|---|
| Phase 10 on 7B | fp32 exceeds 16 GB VRAM; CPU-only, slow. Excluded from the approved scope. |
| Gated tokenizers | none of the five are gated; all five loaded unauthenticated. |
| `pytest` run | not installed; all suites have standalone runners and were run that way. |

---

## 4. What changed in this repository

**Source files modified (12):** `src/canonicalize.py`, `src/transpiler.py`,
`src/phi.py`, `src/generate_corpus.py`, `measure/prior_strength.py`,
`measure/fertility.py`, `measure/collisions.py`, `measure/dfa_parity.py`,
`grammar/render_grammar.py`, `tests/test_isomorphism.py`,
`tests/test_roundtrip.py`, `tests/test_invariants.py`.

**Files added (12):** 6 test suites under `alien_syntax/tests/`, and
`run/{run.md,AUDIT.md,RESULTS.md,preflight.py,verify_artifacts.py,runlog.sh,run_structural.sh,run_model_metrics.sh}`.

**Did any reported result change?** **No.** Every structural number is identical
before and after the fixes — grammars, corpora and `METRICS_PARITY.md` regenerate
byte-identically, and the structural fertility table matches row for row. The one
fix that would change a number (the bootstrap estimand, `AUDIT.md` M-01) touches
a measurement that had never been run on this machine.

**Was any generated artifact hand-edited?** **No.** Regeneration was always into
the experiment directory or, where a script writes in place, snapshotted and
verified byte-identical.

**Unrelated change preserved:** `project_status/phase1.md` lost 2666 lines during
this session (truncated to line 743, the range open in the editor). **Not touched
by this audit.** If accidental: `git checkout -- project_status/phase1.md`.

**Repo hygiene, reported not fixed:** 13 `.pyc` files are tracked in git, so any
run dirties the worktree. Fix is `git rm -r --cached '**/__pycache__'` plus a
`.gitignore` entry — a decision for you, not an audit correction.
