# AUDIT.md — Phase 2 end-to-end audit

**Date:** 2026-09-01 · **Commit at start:** `c3f9b26` ·
**Experiment:** `run/experiments/20260901-233702` ·
**Environment:** Ubuntu 24.04.4, Python 3.12.3, `lark 1.3.1`, `transformers 5.16.1`,
RTX 3080 Ti 16 GB (unused — `torch` not installed)

Every claim below cites a file and function, or a command whose output is in the
experiment directory.

---

## 1. Executive summary

The Phase 2 compiler is in **substantially better shape than the audit brief
anticipated**. The `refgrammar` import blocker is not active; every structural
gate passes; the committed generated grammars, corpora and `METRICS_PARITY.md`
all regenerate byte-for-byte. Three of the four "known status" items I was asked
to treat as hypotheses reproduced exactly, including γ's **24** findings on
check (g).

Two findings change what the paper can say.

**Finding 1 — the binding constraint is now measured, and every candidate fails
it.** CONSTRAINT 1 (fertility ratio ∈ [0.95, 1.05]) had never been run. It runs
now: α **1.068–1.073**, β **1.401–1.448**, γ **1.937–2.285**. The provisional
winner β was selected on the *structural proxy*, which reports β ÷ 3DOM =
**1.000** because β is character-length matched to 3DOM. Characters are not
tokens. β's pronounceable nonwords (`mumvumfe`, `bungi`, `taltazat`) are absent
from the BPE vocabulary and fragment into sub-word pieces at identical character
count — and because they are pure ASCII, β's fragmented-% is **0.0**, so the
byte-fallback metric cannot see the problem at all. This is exactly the failure
the brief warned against ("never call character-length parity tokenizer parity"),
and it was live.

**Finding 2 — the ΔNLL confidence interval measured a different quantity than
the point estimate it was printed beside.** `paired_bootstrap` resampled the
*mean of per-item ratios*; the reported Δ is a *difference of ratios of totals*.
On a corpus whose programs vary in length — the real case — the 95% CI can
exclude the number next to it. Demonstrated at
`results/bootstrap-estimand-defect.txt`: point estimate `+0.005714`, old CI
`[+0.022950, +0.040050]`. Fixed. **No reported result changes**, because ΔNLL has
never been run on this machine.

Beyond those: two hard invariants were carried by module-level `assert`s that
`python -O` deletes; the Phase 1 signature cross-check was silently disabled by a
bare `except Exception`; the isomorphism assertion omitted half of what §16
requires; and all three test runners treated a crash as neither pass nor fail.
All fixed, each with a test that fails without the fix.

**149 tests now pass** (26 pre-existing, 123 added). No generated artifact was
hand-edited. No test was weakened.

---

## 2. Repository map

### 2.1 Load-bearing compiler code

> *"If this file were subtly wrong, what research claim would become invalid?"*

| File | If subtly wrong… |
|---|---|
| `src/phi.py` | φ would not be a bijection modulo the '.' overload, and "same grammar under a renaming" — the entire isomorphism argument — would be false while every downstream test still passed. |
| `src/canonicalize.py` | The shared IR would stop being shared: over-normalisation makes non-equivalent programs hash equal (a false PASS on isomorphism); under-normalisation makes equivalent ones differ (a false FAIL). |
| `src/transpiler.py` (lexer) | The DFA parity and nLVP metrics would describe a token stream the parser never sees, so "matched parse complexity" would be unsupported. |
| `src/transpiler.py` (Transliterator) | The alien negative corpus would carry a different number of defects than the 3DOM one, making the alien language measurably harder or easier for reasons unrelated to surface familiarity. |
| `src/transpiler.py` (Lark front end) | Ambiguity could reach the IR, breaking I10 and making derivation counts meaningless. |
| `src/transpiler.py` (Emitter) | Round-trip stability would be vacuous, and the emitted exemplars in `heuristics_ir.exemplars` would differ in content across conditions. |
| `grammar/templates/grammar.lark.template` | The single-grammar claim collapses: two lexicons would be two languages, not one language twice. |
| `grammar/render_grammar.py` | A terminal could silently keep its 3DOM spelling (G-R3), or the appendix could lose productions to metasyntax collision (G-R6), invalidating the \|N\|/\|P\| invariants. |
| `src/generate_corpus.py` | Corpora would drift out of pairing, and every per-item comparison in the study would compare different programs. |
| `tests/test_isomorphism.py` | The central contract would be unenforced. |

### 2.2 Load-bearing experimental code

| File | If subtly wrong… |
|---|---|
| `measure/fertility.py` | CONSTRAINT 1 would gate on a wrong number, and the familiarity effect would be confounded with sequence length — the most likely reason this paper gets rejected. |
| `measure/prior_strength.py` | ΔNLL — the primary objective — and its CI would be wrong; "reduced pretraining proximity" is *defined* by this measurement. |
| `measure/collisions.py` | A lexicon with a real lexical hazard could pass CONSTRAINT 2, making the alien language harder to lex than 3DOM for reasons the design claims are held constant. |
| `measure/dfa_parity.py` | "Matched parse complexity" would be asserted without evidence. |
| `measure/metrics_parity.py` | The INVARIANT rows of the parity report would not reflect the grammars they describe. |
| `src/heuristics_ir.py` | The intent-vs-structure layer would mis-score model output, conflating a compiler-valid program with a correct one. |

### 2.3 Plumbing (not rewritten)

CLI argument parsing in every `main()`; markdown table formatting in
`emit_table` / `--md` branches; `sys.path` insertion preambles; `run/runlog.sh`;
`__pycache__`. One exception: `render_grammar.main` gained `--outdir`, because
regenerate-and-compare is impossible if the only render target is the artifact
being compared.

---

## 3. Dependency and execution blockers

**None.** The brief's hypothesis that "the current Phase 2 package may fail if
`refgrammar.py` from Phase 1 cannot be imported" is **REPORTED-BUT-NOT-REPRODUCED**:
`phi.phase1_dir()` (`src/phi.py:73-80`) falls back to
`<repo>/grammar_and_3DOM_client`, which is present and complete. Verified by
`run/preflight.py` and by every phase running to completion.

`torch` is absent, so Phase 10 is **BLOCKED**, not failed. `transformers` was
installed into `run/.venv` during this audit and Phase 9 completed.

One real dependency trap was found by hitting it: a venv with `transformers` but
without `lark` fails deep inside `fertility.corpus_for` at
`transpiler.parse` → `from lark.exceptions import LarkError`. `run/preflight.py`
now catches this before any import.

---

## 4. Compiler-correctness findings

| ID | Severity | Status | File / function | Evidence | Research risk | Action | Test |
|---|---|---|---|---|---|---|---|
| C-01 | CRITICAL | **FIXED** | `canonicalize.py` module level | Two `assert`s carried "15 distinct verbs" and "signatures cover the verb set"; `python -O` deletes both | The closed-verb-set invariant — pinned in `ir_schema.json` and in METRICS.md — would be unenforced in any optimised run | Replaced with `_assert_closed_sets()` raising `CanonicalisationError` | `test_canonicalization.py::test_closed_set_invariants_survive_python_dash_O` |
| C-02 | CRITICAL | **FIXED** | `canonicalize._check_against_phase1` | `except Exception: return` swallowed *any* failure, not just an absent Phase 1 | The C8 signature table could drift from `tasks.py::_SIGNATURES` — the scorers' ground truth — with no signal | Narrowed: a missing `tasks.py` is recorded in `PHASE1_SIGNATURE_CHECK_SKIPPED`; an ImportError from a *present* file now raises | `test_preflight.py::test_canonicalize_records_a_skipped_phase1_signature_check` |
| C-03 | HIGH | **FIXED** | `transpiler.ProgramTransformer.complex_selector` | `zip(rest[0::2], rest[1::2])` silently drops a trailing combinator | A selector with a step missing would still parse and hash — a *different query*, silently | Explicit odd-length check raising `ParseError` | `test_grammar_whitespace.py` (selector-structure suite) |
| C-04 | HIGH | **FIXED** | `transpiler.ProgramTransformer.iife` | `if isinstance(stmt, list)` silently discarded anything else | A grammar rule added without a transformer method would drop operations from the IR while still producing a parse and a hash | Explicit branch: lists extend, `str` (the FUNC token) skipped, anything else raises | covered by the 9-suite run; regression-guarded by A4's new IR check |
| C-05 | MEDIUM | **FIXED** | `transpiler.Emitter.emit(Step)` | Dict lookup raised a bare `KeyError` on an impossible combinator | Undiagnostic failure; §8.5 requires canonicalisation failures to be distinguishable from parser and φ failures | Raises `CanonicalisationError` naming the value and the legal set | `test_canonicalization.py::test_emitter_rejects_an_impossible_combinator` |
| C-06 | MEDIUM | **FIXED** | `canonicalize.canonical_number` / `format_number` | `inf`/`nan` escaped as `OverflowError` / `ValueError` from inside `int()` | Indistinguishable from an arithmetic bug | `_reject_non_finite` raises `CanonicalisationError` explaining that NUMBER cannot express them | `test_canonicalization.py::test_C1_non_finite_values_raise_a_canonicalisation_error` |
| C-07 | MEDIUM | **FIXED** | `generate_corpus.check` (A4) | Gate checked zero VERB *tokens*, a proxy for the actual claim | An IR-lowering regression that produced operations from a vacuous chain would pass A4 | A4 now asserts the token count **and** `len(parse(p, phi).ops) == 0` — strictly stronger | gate itself; `test_isomorphism.py::test_ir_identity_over_vacuous_corpus` |
| C-08 | MEDIUM | **FIXED** | `generate_corpus.check` (A7) | `zip` over unpaired corpora would silently compare a prefix | A7 could PASS by comparing fewer items | Explicit pairing guard that returns before the loop | pairing asserted in `test_measure_formulas.py::test_corpora_are_paired_across_lexicons` |
| C-09 | LOW | **DOCUMENTED** | `canonicalize.Operation` | `frozen=True` is shallow: `args` is a `dict`, so `Operation` is unhashable and its args are mutable in place | None — identity travels through `content_hash`, never through set/dict membership. But an unpinned hazard invites a future `set(ops)` | Pinned by a test that fails if it ever becomes hashable, with the reason | `test_canonicalization.py::test_operation_args_is_nested_mutable_and_unhashable` |
| C-10 | LOW | **FIXED** | `phi.TerminalTable.by_id` | A plain `@property` rebuilt a 43-entry dict on **every** lookup, and `PhiMap.spelling` calls it per terminal | Performance only | `functools.cached_property` (works on a frozen dataclass — it writes through `__dict__`, bypassing the blocked `__setattr__`) | exercised by every suite |

### Verified correct — no change made

- `build_args` / `args_in_order` (`canonicalize.py:304-324`) handle prefixes,
  overflow (`_positional`) and **holes** correctly. `rotate(90) → {"axis": 90}`
  and `args_in_order → [90]`: the §17 intent-error case is faithfully preserved,
  not accidentally repaired.
- `h_axis_default` (`heuristics_ir.py:174-196`) inspects the **value** of `axis`
  (`str(axis) not in ("x","y","z")`), which is the only way this class of error
  is detectable. Legal arity and legal argument names cannot see it.
- `Emitter` uses `functools.singledispatchmethod` correctly under
  `from __future__ import annotations`; the base implementation raises
  `TypeError` and there is **no** `str(node)` fallback. Verified by execution.
- `prefix_offset` arithmetic is correct for tokenizers **with and without** a
  BOS — the `-1` absorbs exactly that difference. Extracted from `score_program`
  so it is testable without `torch`; behaviour unchanged.
- `_phi_key` is content-derived, so a parser cache cannot serve a stale φ.
- The hand lexer's token alphabet matches `refgrammar`'s exactly (pseudo →
  `SELECTED`/`LASSO`, types → `TYPE_MESH`), which is why `parse_counts` over our
  stream is meaningful.

---

## 5. Fluent Python findings

Audited against §8; only items with a correctness or auditability consequence
were changed.

| Question | Finding |
|---|---|
| `frozen=True` where immutability is intended? | Yes on `Matcher`, `Step`, `Selector`, `Operation`, `IRProgram`, `Terminal`, `TerminalTable`, `PhiMap`. |
| Nested mutable values? | **Yes** — `Operation.args` and `PhiMap.substitutions` are dicts. Consequence: both unhashable. Documented and pinned (C-09). |
| Hashability assumed from frozen? | No. `transpiler._phi_key` explicitly notes `PhiMap` is unhashable and derives a string key. Correct. |
| `order=False` where domain order matters? | Yes, explicitly on `Matcher`. Generated ordering would sort `class` before `type` alphabetically; `MATCHER_KIND_RANK` requires the opposite. Pinned by `test_C3_sort_key_is_an_explicit_rank_not_alphabetical`. |
| `__post_init__` enforces invariants? | Yes on `Matcher`, `Step`, `Operation`. All four `Matcher` cases and both `Step` cases now tested. |
| Optional keys omitted vs null? | `combinator: null` **is** emitted — and `ir_schema.json:90-92` explicitly enumerates `null` in the step enum. Correct as-is. |
| `Selector.raw` computed, not stored? | Yes, a `@property` rendering from canonical steps (C5). Verified it never contains an alien sigil. |
| `zip` truncation where equality is required? | **Three sites found**: `complex_selector` (C-03), A7 (C-08), `dfa_parity` P2 (M-04). All guarded. |
| Generator reuse after consumption? | `Transliterator._outer_ids`/`_inner_ids` are generators, but each is consumed exactly once per comprehension. No defect. |
| Symbol tables ordered by negative length? | Yes — `Lexicon.of` sorts `key=lambda p: -len(p[0])`, and `Transliterator` does the same. Maximal munch is correct. |
| Closure-based error accumulator? | `validate_phi`'s `bad()` closes over `errors` only. Fatal shape errors (missing `map`) raise immediately; semantic defects accumulate. Both behaviours now tested. |
| Validation performed twice inconsistently? | No. `render_grammar` re-runs φ validation via `load_candidate`, which is the same code path. |
| `singledispatchmethod` correct? | Yes; base raises `TypeError`. Registrations resolve string annotations via `get_type_hints` on 3.12. |
| Minimum Python declared? | **Not declared anywhere.** Now stated in `run/run.md §3` (3.12 tested, 3.10 realistic floor). No `pyproject.toml` exists to hold `requires-python`. |
| Exceptions distinguishable? | `LexError`, `ParseError`, `AmbiguityError`, `CanonicalisationError`, `PhiValidationError` — five distinct types, and after C-05/C-06 the canonicaliser no longer leaks `KeyError`/`OverflowError`. |
| `raise ... from exc`? | Present at `transpiler.parse` and in all new raises. |
| Broad `except Exception`? | Was in three non-optional places (C-02, M-03, M-05). Narrowed or made loud. Remaining broad catches are around genuinely optional integrations (HF revision lookup, tokenizer download) and each records what it caught. |
| Module-level `assert`? | Two, both removed (C-01). `python -O` now preserves both invariants. |
| `TerminalTable.by_id` rebuilt per access? | Was. Now `cached_property` (C-10). |
| Cache keys? | `_phi_key` = `phi_id` + sorted substitutions. Content-derived, collision-free across the four lexicons; asserted by `test_parser_cache_cannot_serve_the_wrong_lexicon`. |
| `bool` ⊂ `int` / `1 == 1.0 == True`? | `format_number` guards bools. And **`content_hash` already distinguishes them** (`true` vs `1` in JSON) — this is the concrete reason the isomorphism test compares digests rather than Python objects. Now tested explicitly. |
| Lark `Token` subclasses `str`? | Relied on in `argument` (`hasattr(kid, "type")`) and now in `iife` (`isinstance(kid, str)`). Both correct and commented. |
| Cross-process `hash()`? | Not used for identity anywhere. SHA-256 stability verified across three `PYTHONHASHSEED` values in a subprocess. |

---

## 6. Canonicalization findings

Each of C0–C8 now has an isolated test **and a negative test**. The distinction
matters: under-normalisation shows up as a loud false failure in the isomorphism
suite, while **over-normalisation shows up as a false PASS** and is only visible
in a test that keeps two things apart.

| Rule | Verified | Negative test |
|---|---|---|
| C0 grammar version | present on every top-level object; no lexicon marker leaks into the canonical JSON | `test_C0_no_lexicon_identifier_leaks_into_identity` checks for `phi_id` and the alien entry spelling |
| C1 numbers | `+3→3`, `3.0→3`, `1.50→1.5`, `-0→0` | booleans rejected; `inf`/`nan` rejected; `True` and `1` hash **differently** |
| C2 strings | `'` default, `"` fallback | both quotes ⇒ raises rather than inventing an escape |
| C3 matcher sort | `.wheel.front` ≡ `.front.wheel` | rank is `type < id < class …`, **not** alphabetical; sorting does not cross step boundaries |
| C4 order preservation | steps and operations kept | `scale→move` ≠ `move→scale`; `.a>.b` ≠ `.b>.a`; descendant ≠ child |
| C5 reference raw | rendered from canonical steps in 3DOM spelling | asserted the alien class sigil never appears in `raw`, for all three lexicons |
| C6 canonical JSON | sorted keys, compact separators, UTF-8 | independent of dict insertion order |
| C7 content hash | SHA-256 over the C6 bytes; `source` excluded | verified stable across 3 separate processes with different `PYTHONHASHSEED` |
| C8 signatures | prefix mapping; overflow → `_positional` | a hole (`{"degrees": 90}`) raises; overflow is captured, not truncated |
| **C9 (new)** | **grammar-level** selector layout normalisation | see below |

### C9 — a canonicalisation rule that existed but was unregistered

`.a  .b` ≡ `.a .b` and `.a>.b` ≡ `.a > .b` ≡ `.a  >  .b` all reach one canonical
form — but **not** via `canonicalize.py`. The collapse happens in the grammar:
`WS : / +/` matches a whole run of spaces as one token, and
`child_combinator : WS? CHILD WS?` absorbs its own padding. These are one
derivation, not several that later merge.

That is a real canonicalisation, it is load-bearing for I9, and it was absent
from the C0–C8 register — which made the list look complete when it was not. It
is now documented as **C9** in `canonicalize.py`'s module docstring and tested in
`tests/test_grammar_whitespace.py`.

**It was deliberately NOT moved into Python.** The grammar already decides it
correctly at parse time; re-implementing it as a post-pass would add a second
authority that can disagree with the parser — strictly worse than an
asymmetric-looking register.

---

## 7. Corpus and parser findings

**A1–A7, derived from `generate_corpus.check`:** A1 unique parse · A2 100%
production coverage over `refgrammar.all_features()` (57 branches) · A3 negatives
rejected · A4 vacuous parse and (now) lower to zero operations · A5 the
descendant/compound differential survives φ · A6 Lark ≡ DFA over all three
corpora · A7 φ⁻¹∘φ = id and IR hashes match the 3DOM twin.

All pass for α, β, γ (`logs/p4-corpus-gates.out`).

**Corpora are generated mechanically, never translated.** `generate()` maps every
program through `phi_forward`, including the negative corpus — which cannot go
through the parser because it does not parse, and so goes through the
character-level `Transliterator` instead. That is not a weakness; it *is* the
test.

**Regeneration vs committed artifacts:** generated grammars, `METRICS_PARITY.md`
and the alien corpora were all regenerated into the experiment directory and
diffed. **All byte-identical.** No committed artifact was modified.

**The three seams** (`tests/test_seams.py`) are now compared explicitly:

- Lark and the hand lexer + Phase 1 DFA agree on **552 item/lexicon pairs**
  (138 items × 4 lexicons), as a **biconditional** — plus a non-vacuity test
  proving both actually reject things, so the agreement is not two functions
  that always say yes.
- The `Transliterator` is total (never raises) on the negative corpus and on
  eight deliberately hostile inputs.
- It **preserves defects without multiplying them**: `$S`→`SS` (one defect) still
  has its *selector body* translated, so the alien image carries exactly one
  defect too. A stricter rule would leave the selector in 3DOM spelling and the
  item would arrive carrying **two** — silently making the alien negative corpus
  harder than the 3DOM one. This asymmetry is intentional and is now pinned.
- The three components' selector-position rules differ on purpose (lexer requires
  `DOLLAR LP`; transliterator also accepts `WORD LP` / `OTHER LP`) and agree on
  all well-formed text.

**Argument strings are never treated as selectors** — `recolor('.b#c')` keeps its
body verbatim in every lexicon (D3).

---

## 8. Measurement-validity findings

| ID | Severity | Status | File / function | Evidence | Research risk | Action | Test |
|---|---|---|---|---|---|---|---|
| M-01 | **CRITICAL** | **FIXED** | `prior_strength.paired_bootstrap` | CI resampled the mean of per-item ratios; the point estimate is a difference of ratios of totals | A published 95% CI that does not contain the published point estimate. Demonstrated: point `+0.005714`, old CI `[+0.022950, +0.040050]` (`results/bootstrap-estimand-defect.txt`) | Resamples paired item **indices** applied to both arms and recomputes the same estimand | `test_measure_formulas.py::test_bootstrap_ci_brackets_the_point_estimate` (+5 more) |
| M-02 | HIGH | **FIXED** | `prior_strength.paired_bootstrap` | `rng.randrange(0)` on an empty list; `int(0.975*rounds)` could index out of range for small `rounds` | Crash or a silently wrong interval on a smoke run | Empty raises `ValueError`; n=1 returns a degenerate interval; indices clamped | `test_bootstrap_edge_cases_do_not_crash_silently`, `test_percentile_indices_are_in_range` |
| M-03 | HIGH | **FIXED** | `fertility.main`, `prior_strength.main` | Every tokenizer/model could fail to load and the script still exited **0** | A pipeline would record "Phase 9 complete" having measured nothing | Exit 3 when nothing was measured, with an explicit "this is a FAILURE, not an empty result" | exercised by the Lane B run |
| M-04 | HIGH | **FIXED** | `dfa_parity.compare` / `alphabet` / `positional_profile` | `zip` over unpaired corpora; `except Exception: continue` skipped unlexable programs silently | Two lexicons that both failed on the same items would compare **equal** — parity by mutual absence | Length check added; skipping is now `strict=True` by default and raises | pairing tested; strictness exercised by every parity run |
| M-05 | HIGH | **FIXED** | `fertility.main`, `prior_strength.main` | No tokenizer/model revision, `transformers` version, corpus hash, or timestamp recorded | A fertility number without its tokenizer revision is an anecdote, not a measurement | Provenance JSON block on both; resolved revision SHAs captured for all 5 repos in the Lane B run | provenance asserted present by the Lane B output |
| M-06 | MEDIUM | **FIXED** | `fertility.tokenizer_row` | Only code-point normalisation reported | γ is *shorter* in code points and *longer* in bytes, so a code-point-only ratio flatters a glyph lexicon | Both `tok/char` and `tok/utf8-byte` reported; CONSTRAINT 1 still defined on `tok/char` (unchanged) | `test_codepoint_and_byte_normalisation_disagree_on_the_glyph_lexicon` |
| M-07 | MEDIUM | **FIXED** | `fertility.main` | Corpus size hardcoded as "62-item" in the output prose | Would silently misreport after any corpus change | Computed, plus a corpus sha256; **the value 62 was correct** — withdrawn as a defect, kept as a hardening | `test_corpora_are_paired_across_lexicons`, `test_corpus_fingerprint_is_stable_and_sensitive` |
| M-08 | MEDIUM | **DOCUMENTED** | `prior_strength.score_program` | The sequence's first token is never scored (nothing to condition it on); a non-empty prefix can merge with the program's first token under BPE | Neither affects the paired Δ with `NEUTRAL_PREFIX=""`, but both must be stated | Documented in the docstring; `prefix_offset` extracted and tested with/without BOS | `test_prefix_offset_*` (4 tests) |
| M-09 | LOW | **FIXED** | `collisions._corpus_identifiers` | Called `G.generate()` inside a loop over three corpus names — nine full transliterations per lexicon | Runtime only | Generated once, cached per φ content | exercised by every collisions run |

### Load-bearing constants, classified (§21)

| Constant | Value | Classification | Note |
|---|---|---|---|
| `BOOTSTRAP` | 10 000 | **Conventional** | Standard for percentile bootstrap; no sensitivity analysis needed at this size. |
| `SEED` | 20260910 | **Arbitrary but fixed and documented** | The CHI deadline. Arbitrariness is fine *because* it is fixed and recorded; reproducibility is now tested. |
| `NEUTRAL_PREFIX` | `""` | **Precommitted, and load-bearing** | Empty specifically so prefix/program BPE boundary merging cannot arise. Changing it invalidates M-08's argument. |
| Fertility band | [0.95, 1.05] | **Precommitted** | Registered in `reports/CANDIDATE_SELECTION.md` before measurement. Honoured: all three candidates fail it. |
| DFA tolerance | 0.000 | **Mathematically required** | The streams are identical or φ broke something; there is no noise to tolerate. |
| ΔNLL 5% / 15% cut points | 0.05, 0.15 | **CURRENTLY UNJUSTIFIED** | See §11. `prior_strength.py`'s docstring called them "pre-committed"; they appear **nowhere** in `CANDIDATE_SELECTION.md`. |
| Model list | 4× Qwen2.5-Coder base | **Precommitted**, but see below | Base, not Instruct — correct, and now asserted by a test. |
| Tokenizer list | 4× Qwen + DeepSeek-V3 | **Overstated** | The four Qwen repos share **one** tokenizer (`Qwen2Tokenizer`, vocab 151665). Five repos = **two** distinct tokenizers. |

---

## 9. Reproducibility findings

| Finding | Status |
|---|---|
| Templates, generated grammars, corpora and `METRICS_PARITY.md` all regenerate byte-for-byte | **VERIFIED** |
| SHA-256 content hashes stable across processes and `PYTHONHASHSEED` values | **VERIFIED** |
| `build_templates.py` writes tracked templates in place with no `--check` mode | **DOCUMENTED** — `run_structural.sh` snapshots and restores on drift |
| `render_grammar.py` could only write to the tracked directory | **FIXED** — `--outdir` added |
| `metrics_parity.py` is documented as `> reports/METRICS_PARITY.md` | **DOCUMENTED** — the runbook redirects to a temp file and diffs |
| No preflight; missing Phase 1 surfaced as a deep `ModuleNotFoundError` | **FIXED** — `run/preflight.py`, which imports nothing from either phase |
| No artifact checksums | **FIXED** — `run/verify_artifacts.py`, 39 artifacts, with `--compare` |
| **13 `.pyc` files are tracked in git** | **REPORTED, NOT FIXED** — running any phase dirties the worktree. Fix is `git rm -r --cached '**/__pycache__'` plus a `.gitignore` entry; that is a repo-hygiene decision for you, not an audit correction |
| No `pyproject.toml` / `requires-python` | **REPORTED** — minimum version now stated in `run/run.md §3` only |
| `conformance/coverage.py` (Phase 1) crashes: `negatives.txt` vs `negative.txt` | **REPORTED, NOT FIXED** — Phase 1 is out of scope; `coverage2.py` is the working entry point |

### Unrelated change preserved

`project_status/phase1.md` **lost 2666 lines** during this session — truncated to
exactly line 743, which is the range your editor had selected. **I did not touch
this file and have left it exactly as found.** It looks accidental; recover with
`git checkout -- project_status/phase1.md` if so.

---

## 10. Issues implemented

19 issues fixed across 10 files. Full detail in §4 and §8.

**Compiler:** C-01 … C-08, C-10.
**Measurement:** M-01 … M-07, M-09.
**Reproducibility:** preflight, `--outdir`, checksums, test-runner error handling.

Files changed: `src/canonicalize.py`, `src/transpiler.py`, `src/phi.py`,
`src/generate_corpus.py`, `measure/prior_strength.py`, `measure/fertility.py`,
`measure/collisions.py`, `measure/dfa_parity.py`, `grammar/render_grammar.py`,
`tests/test_isomorphism.py`, `tests/test_roundtrip.py`, `tests/test_invariants.py`.

**Before/after:** every structural number is unchanged. Grammars, corpora and
`METRICS_PARITY.md` regenerate byte-identically post-fix; the structural fertility
table is identical row for row. The only output differences are additive: a
corpus hash in the fertility header, provenance blocks, and richer failure
messages. **No reported result changed**, because the one fix that changes a
number (M-01) touches a measurement that had never been run.

### Test-runner change (all three pre-existing suites)

`main()` caught only `AssertionError`. A `ParseError` or a missing Phase 1 file
aborted the runner **before the summary line**, so a red run looked like an
interrupted one. All three now count a non-assertion exception as `ERROR` and
still print `N/M passed`.

---

## 11. Issues requiring a research decision

### RD-1 — No candidate satisfies CONSTRAINT 1 (**blocking**)

**Observed:** α 1.068–1.073, β 1.401–1.448, γ 1.937–2.285, against a
pre-committed band of [0.95, 1.05].

**Alternatives:**

1. **Re-engineer β for token-level parity.** Build the pseudo-lexicon from
   spellings that tokenize to the *same number of tokens* as their 3DOM
   counterparts under the study tokenizers, rather than the same number of
   characters. `candidates/gen_beta_lexicon.py` already generates β
   programmatically, so the objective function changes, not the method.
   *Validity:* preserves the pre-committed rule intact. *Cost:* a new lexicon and
   a full re-run. **This is the smallest defensible recommendation.**
2. **Widen the band.** Changing [0.95, 1.05] after seeing the numbers is exactly
   the move pre-commitment exists to prevent. *Validity:* severely damaged unless
   disclosed as a post-hoc amendment.
3. **Accept α (1.07) as closest.** Only 7% over, but α is the *interference*
   condition — familiar words in wrong roles — so it answers a different question
   than β. *Validity:* changes what the study measures.
4. **Retain the mismatch and control for it statistically.** Report ΔNLL per
   character as primary (which is already the design) and treat fertility as a
   measured covariate. *Validity:* defensible, but it concedes that token cost is
   not held constant, weakening the "no length confound" claim.

**Code that would change after approval:** `candidates/gen_beta_lexicon.py`
(objective function), `candidates/phi_beta.json` (regenerated), then Phases 3–9
re-run. No compiler code changes.

### RD-2 — Is check (g) part of CONSTRAINT 2?

**Observed:** γ has 24 findings (22 g1 lexical-class, 2 g2 reachability);
α and β have 0. (g) currently does **not** affect the exit code, by explicit
design, so a pre-committed decision cannot turn on a criterion added afterwards.

The g2 witnesses are the sharp ones: in 3DOM `mesh`+`mesh` lexes to **one** token
`IDENT("meshmesh")`, so the sequence TYPE TYPE is *unreachable from any 3DOM
string*. In γ, `⍇`+`⍇` lexes to **two**. L(γ) is therefore a strict superset of
φ(L(3DOM)) — the two are not isomorphic, whatever the production counts say.

**Recommendation:** adopt (g) as a *reported diagnostic*, not a retroactive
constraint, and classify γ as a stress diagnostic on the strength of the g2
argument alone — which is a proof, not a threshold. Document that (g) was
proposed after the original rule was written. **Do not fold it into a silent
pass/fail.**

### RD-3 — The ΔNLL 5% / 15% cut points claim a precommitment they do not have

`prior_strength.py`'s docstring and output called the reading rule
"pre-committed". `reports/CANDIDATE_SELECTION.md` registers only the fertility
band and the collision/parity constraints — **the 0.05 and 0.15 thresholds appear
nowhere in it**.

**Action taken:** the output now says they are a reading *aid*, explicitly not a
pre-committed threshold. **Decision required:** either register them in
`CANDIDATE_SELECTION.md` before Phase 10 runs (preferable — it is still genuinely
pre-measurement here), cite a source, or replace them with a sensitivity analysis.

### RD-4 — "Five study tokenizers" is two

The four Qwen2.5-Coder repos share one tokenizer. Reporting five would overstate
external validity. **Recommendation:** describe the tokenizer arm as two distinct
tokenizers (Qwen2, DeepSeek-V3) and, if more breadth is wanted, add a genuinely
different family (e.g. a SentencePiece model) rather than more Qwen sizes. The
*model* arm is unaffected — four sizes of one family is a legitimate scaling axis.

---

## 12. Tests added

**123 new tests in 6 files**, bringing the repository to **149** (derived by
running them, not carried forward from documentation).

| File | Tests | Claim protected | Deterministic | Network | GPU |
|---|---:|---|---|---|---|
| `test_canonicalization.py` | 34 | C0–C8, frozen-dataclass invariants, `-O` safety, emitter dispatch, intent-vs-structure | yes (1 subprocess) | no | no |
| `test_phi_validation.py` | 25 | V1–V8 on an 8-terminal miniature; inversion; identity via the same API | yes | no | no |
| `test_grammar_whitespace.py` | 21 | L2 whitespace significance, C9, quote symmetry, ambiguity, parser cache | yes | no | no |
| `test_seams.py` | 14 | Lark ≡ DFA biconditional (552 pairs); transliterator totality and defect preservation | yes | no | no |
| `test_measure_formulas.py` | 22 | Fertility and ΔNLL arithmetic against deterministic fakes; bootstrap pairing/reproducibility | yes | no | no |
| `test_preflight.py` | 7 | Missing-Phase-1 behaviour, via real subprocesses with poisoned env | yes | no | no |

Pre-existing: `test_isomorphism` (4), `test_roundtrip` (8), `test_invariants` (14).

Every fix in §4 and §8 has a test that **fails without it** — verified for C-01,
C-06 and M-01 by running the test against the pre-fix code.

Explicitly covered from the §22 matrix: φ V1–V8 · I1–I10 · A1–A7 · C0–C9 ·
collisions (a)–(g) · DFA parity · baseline/alien IR identity · negative-corpus
preservation · text→IR→text · IR→text→IR · canonical text idempotence · source
exclusion · numeric coercion · cross-process digest stability · emitter
unsupported-type failure · dataclass ordering hazards · `python -O` · fertility
with a fake tokenizer · bootstrap reproducibility · missing Phase 1 dependency.

**Not covered:** NLL alignment with synthetic *logits* runs only when `torch` is
present (the offset arithmetic it depends on **is** covered without torch). One
generator single-use hazard was searched for and none found.

---

## 13. Remaining risks

1. **CONSTRAINT 1 fails for every candidate.** The study currently has no lexicon
   that satisfies its own binding pre-committed constraint. Everything else is
   downstream of resolving RD-1.
2. **ΔNLL — the primary objective — is unmeasured.** Needs `torch` and ~10 GB of
   downloads. Until then "reduced pretraining proximity" has no value attached,
   and the formulas, while unit-tested against fakes, have never met a real model.
3. **γ is not a clean control and must not be presented as one.** Check (g)'s g2
   witnesses show L(γ) ⊋ φ(L(3DOM)); byte fallback is 36% (Qwen) / 55%
   (DeepSeek).
4. **The isomorphism argument's structural half rests on inventory comparison,
   not shape.** `grammar_metrics.cross_check` compares non-terminal *sets* and
   terminal *inventories*; `A = X , Y` vs `A ::= Y X` would pass. The behavioural
   check (Lark ≡ DFA over 552 pairs) is the strong evidence; lead with it.
5. **The 62/64/12-item corpus is small.** Every "VERIFIED" gate is finite
   regression evidence over these programs. The generalisation comes from the
   construction, not the corpus.
6. **13 tracked `.pyc` files** dirty the worktree on every run, which makes
   "did this run change anything?" harder to answer honestly.
7. **`build_templates.py` writes tracked files in place.** Mitigated by the
   runner's snapshot/restore, but a hand-run on a dirty tree can still surprise.

---

## 14. Recommended order of work

1. **Decide RD-1.** Nothing downstream is meaningful until a candidate can satisfy
   CONSTRAINT 1. Recommended: re-engineer β against a token-count objective using
   the existing `gen_beta_lexicon.py`.
2. **Register or replace the ΔNLL thresholds (RD-3)** — while it is still
   genuinely pre-measurement. This window closes the moment Phase 10 runs.
3. **Install `torch`, run Phase 10** on 0.5B–3B (GPU) to get ΔNLL, even on the
   current lexicons — the *relative* ΔNLL/char ordering informs RD-1.
4. **Re-run Phases 3–9** on any new β and re-check CONSTRAINT 1.
5. **Settle RD-2** and fix γ's description everywhere it appears.
6. **Correct "five tokenizers" to two (RD-4)** in `fertility.py`'s docstring and
   in `CANDIDATE_SELECTION.md`.
7. **Repo hygiene:** untrack `__pycache__`; add `pyproject.toml` with
   `requires-python = ">=3.10"`; consider fixing Phase 1's `coverage.py`
   filename bug.
8. **Recover `project_status/phase1.md`** if its truncation was accidental.
