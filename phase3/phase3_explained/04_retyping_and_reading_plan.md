# 04 — Retyping and reading plan

---

## 1. Inventory

Computed from the repository with `find`/`wc -l`, not estimated.

| Category | Files | Lines |
|---|---:|---:|
| **New Phase 3 Python** | **14** | **2,820** |
| Vendored Python (copied, unmodified except 1) | 8 | 4,380 |
| Vendored data (JSON/EBNF/corpora) | 22 | — |
| Markdown (README, manifest, patch note) | 3 | — |

Per file:

| File | Lines |
|---|---:|
| `tests/test_pipeline.py` | 414 |
| `src/phase3/sites.py` | 347 |
| `scripts/vendor_sync.py` | 319 |
| `src/phase3/linter.py` | 270 |
| `src/phase3/scoring.py` | 247 |
| `scripts/make_delta.py` | 234 |
| `src/phase3/models.py` | 220 |
| `src/phase3/outcomes.py` | 198 |
| `tests/test_sites.py` | 182 |
| `scripts/site_census.py` | 116 |
| `tests/test_scorer_repair.py` | 108 |
| `tests/run_tests.py` | 89 |
| `src/phase3/_vendor.py` | 76 |
| `src/phase3/__init__.py` | 0 |

---

## 2. Triage

**Rule applied:** code is LOAD-BEARING when a subtle mistake could invalidate
the scientific conclusion *while the program still runs correctly*. A crash is
not the danger; a plausible wrong number is.

### LOAD-BEARING — understand, possibly retype

| File | Why |
|---|---|
| `src/phase3/sites.py` | The collision classifier **is** the experiment. A wrong offset, a mis-recovered terminal id, or a swallowed parse error silently reclassifies sites and every downstream number inherits it. |
| `src/phase3/scoring.py` | Holds the sign convention, the full-sequence summation, the `k*` interpolation and the three-scale agreement rule. A flipped sign here reverses the paper's conclusion and nothing crashes. |
| `src/phase3/outcomes.py` | The hurdle. Collapsing reach and choice reproduces exactly the Experiment 02 error, and the collapsed number looks perfectly reasonable. |
| `src/phase3/linter.py` | Opposite sign convention to `scoring.py` (deliberately), plus the H5 IR-preservation proof. Confusing the two signs inverts the risk ranking. |
| `vendor/grammar_and_3DOM_client/tasks.py` (the ~18-line P3-001 patch only) | The defect it repairs inflated accuracy silently for who knows how long. |
| `scripts/make_delta.py` (the permutation tables, ~20 lines) | If a permutation crosses a shape class, its sites become LEXICAL and the primary contrast quietly disappears. |
| `src/phase3/models.py` (`HFModel.sequence_logprob` only, 23 lines) | The `logits[:-1]` / `ids[1:]` alignment is the classic off-by-one. Wrong by one and you score the wrong tokens — plausibly, without error. |

### PLUMBING — skim, do not retype

| File | Why |
|---|---|
| `scripts/vendor_sync.py` | Provenance bookkeeping. Failures are loud (missing file, hash mismatch). |
| `scripts/site_census.py` | A reporting loop over `sites.classify`. All the logic is in the module. |
| `src/phase3/_vendor.py` | `sys.path` wiring plus a guard that raises. Nothing subtle. |
| `tests/run_tests.py` | A test runner. If broken, you see it immediately. |
| `tests/*.py` | Read them — they are the executable specification — but there is no need to retype them. |
| `src/phase3/models.py` (rest) | `FakeLM` is a fixture; `load()` is a switch. |
| `src/phase3/__init__.py` | Empty. |
| All of `vendor/` except the patch | Copied Phase 1/2 code, already covered by its own suites and by `--check`. |

---

## 3. The short list

Four files:

1. `src/phase3/sites.py` (347)
2. `src/phase3/scoring.py` (247)
3. `src/phase3/outcomes.py` (198)
4. `src/phase3/linter.py` (270)

**1,062 lines = 37.7% of the new code.** Understanding only these gives you
roughly **85% of the scientific system**.

**How I produced that estimate.** Not from line counts — from coverage of the
causal chain. Of the 14 rows in the "theory → variable → code → metric" table
in `01 §5`, **12** are implemented entirely inside these four files. The two
that are not (φ-map construction, corpus generation) are either vendored and
already verified upstream, or a ~20-line permutation table in `make_delta.py`.
Every quantity that reaches a result — collision class, `M_seq`, `k*`, DiD,
`P(O)`, `P(Y|O)`, `S_seq`, AUROC, the IR proof — is defined in these four
files. The remaining ~15% is provenance, reporting and test scaffolding, where
mistakes are loud rather than silent.

---

## 4. Data structures first

Learn these before any function. Full real dumps are in `03 §1`.

| Object | What it is | Field that matters most |
|---|---|---|
| `phi.PhiMap` | terminal id → spelling, validated bijection | `substitutions`, `overload_groups` |
| `sites.Site` | one decision site, frozen | `collision`, `prefix`, `correct`, `competitor` |
| `sites.CollisionClass` | NONE / LEXICAL / BENIGN / SEMANTIC | `is_usable` — true only for SEMANTIC |
| `scoring.MarginRecord` | one Arm-A measurement | `m_seq` (>0 good, <0 reversion) |
| `scoring.ExtinctionCurve` | the dose-response curve | `k_star`, `censored` |
| `outcomes.Outcome` | five-bucket classification | `parse_valid` **and** `task_correct`, never averaged |
| `outcomes.HurdleResult` | reach × choice | has **no** single "reversion rate" field, by design |
| `linter.RiskScore` | one H4 prediction | `s_seq` (>0 = danger — opposite sign to `m_seq`) |

The single most important relationship in the codebase:

```
s_seq  ==  -m_seq        (same model, same site, same rule)
```

Asserted by `test_risk_sign_is_opposite_to_margin`. If you ever find yourself
unsure which sign means trouble, re-read that test.

---

## 5. One end-to-end path — the path to retype

Input: the first Phase 1 positive program.
Output: a classified site, a margin, an outcome, and a risk score.

| # | File | Function |
|---|---|---|
| 1 | `src/phase3/_vendor.py` | module import → `assert_self_contained` |
| 2 | `vendor/.../phi.py` | `identity_phi`, `load_candidate('delta')` |
| 3 | `vendor/.../generate_corpus.py` | `phase1_programs('positive', ident)` |
| 4 | `vendor/.../transpiler.py` | `transliterate(p, ident, delta)` |
| 5 | `src/phase3/sites.py` | `classify` |
| 6 | ″ | `_inverse_spelling_map` |
| 7 | ″ | `_terminal_of_token` |
| 8 | ″ | `_safe_ir_hash` (twice: base, then variant) |
| 9 | `src/phase3/scoring.py` | `forced_prefix_margin` |
| 10 | ″ | `extinction_curve` → `_interpolate_crossing` |
| 11 | `src/phase3/outcomes.py` | `evaluate` |
| 12 | ″ | `observe_site` → `hurdle` |
| 13 | `src/phase3/linter.py` | `score_site` |
| 14 | ″ | `verify_repair` |

Runnable version in `03 §4`.

---

## 6. What to retype

### Core — 381 lines, **13.5%** of 2,820

| Function | File | Lines | Why it matters | Prereqs | In → Out | Invariant | Test after |
|---|---|---:|---|---|---|---|---|
| `classify` | sites.py 203–278 | 76 | the experiment itself | PhiMap, lex, IR hash | `(program, φ)` → `list[Site]` | every site's offset points at `correct`; variant differs by exactly that splice | `run_tests.py sites` |
| `_terminal_of_token` | sites.py 163–181 | 19 | wrong id ⇒ wrong role ⇒ wrong competitor | token types | `(type, value, φ)` → `tid\|None` | verbs resolved by **value**, not type | `test_token_type_map_matches_lexer` |
| `_safe_ir_hash` | sites.py 188–200 | 13 | decides LEXICAL vs SEMANTIC | transpiler errors | `(src, φ)` → `(hash\|None, note)` | `num_parses != 1` ⇒ `None`; never raises | `test_lexical_sites_really_do_not_parse` |
| `prefix_collisions` | sites.py 294–320 | 27 | caps achievable AUROC | `Site.prefix` | `list[Site]` → `{prefix: [Site]}` | only prefixes with ≥2 distinct `correct` | `test_prefix_collisions_are_detected_and_removable` |
| `forced_prefix_margin` | scoring.py 82–112 | 31 | the measurement | LM protocol | `(lm, site)` → `MarginRecord` | **one** prefix string, reused for both candidates | `test_margin_scores_both_candidates_against_identical_prefix` |
| `_interpolate_crossing` | scoring.py 137–154 | 18 | the primary estimand | the ladder | `(xs, ys)` → `k*\|None` | first **upward** crossing; `None` ⇒ censored | `test_extinction_curve_detects_a_crossing` |
| `interaction_did` | scoring.py 201–247 | 47 | the scale-robustness rule | logit, copysign | 4 cells → `InteractionResult` | margin sign flipped before comparison | `test_interaction_flags_scale_dependence` |
| `evaluate` | outcomes.py 77–108 | 32 | the taxonomy | SCORING_POLICY §3 | `(text, φ, target)` → `Outcome` | vacuous = parse-success **and** task-failure | `test_vacuous_is_parse_success_and_task_failure` |
| `observe_site` | outcomes.py 124–165 | 42 | O and Y | lexing | `(text, φ, site)` → `SiteObservation` | reversion scored on **role**, not string equality | `test_observe_site_detects_competitor` |
| `hurdle` | outcomes.py 190–198 | 9 | prevents the Exp-02 error | — | `[obs]` → `HurdleResult` | `P(Y\|O)` is `None`, not 0, when nothing reached | `test_hurdle_separates_reach_from_choice` |
| `score_site` | linter.py 87–99 | 13 | H4 | LM | `(lm, site, rule)` → `RiskScore` | `s_local + s_shift == s_seq` | `test_risk_decomposition_adds_up` |
| `auroc` | linter.py 106–117 | 12 | the headline metric | — | `(scores, labels)` → `float\|None` | ties count ½; `None` if one class absent | `test_auroc_perfect_and_degenerate` |
| `verify_repair` | linter.py 252–270 | 19 | H5's proof | transliterate, hash | two φ → `(bool, problems)` | **all** 62 programs, no sampling | `test_repair_preserves_ir_over_the_whole_corpus` |
| `HFModel.sequence_logprob` | models.py 180–202 | 23 | the classic off-by-one | torch | `(prefix, cont)` → float | tokenise `prefix+cont` **together** | ⚠ no test — needs weights |
| P3-001 patch | vendor tasks.py | ~18 | the defect | — | — | `len(ops) != len(wanted)` | `run_tests.py scorer` |

### Optional extension — +67 lines, total **15.9%**

`_inverse_spelling_map` (12) · `extinction_curve` (17) · `propose_repair` (24) ·
`FakeLM.sequence_logprob` (14).

Both figures are within the brief's 15–20% band.

---

## 7. What to ignore for now

- `scripts/vendor_sync.py` — read the `ITEMS` list, skip the machinery.
- `scripts/site_census.py` — a printing loop.
- `src/phase3/_vendor.py` — read the docstring, skip the code.
- `tests/run_tests.py` — infrastructure.
- `src/phase3/models.py` apart from the two `sequence_logprob` bodies.
- **All of `vendor/`** except the P3-001 patch. 4,380 lines of already-tested
  Phase 1/2 code. You will want `transpiler.Lexicon.of` eventually (it defines
  the token types `sites.py` mirrors), but not on a first pass.
- `vendor/alien_syntax/candidates/phi_{alpha,beta,gamma}.json` — generated
  artifacts, retained for comparison only.
- Anything about mixed-effects models — **not written yet**.

---

## 8. The three things you are most likely to get wrong

### (1) The two sign conventions

- **Where:** `scoring.forced_prefix_margin` vs `linter.score_site`.
- **Misunderstanding:** that "the margin" is one quantity.
- **Reality:** `m_seq = logP(c) − logP(q)` → **positive is good**.
  `s_seq = logP(q) − logP(c)` → **positive is danger**. `s_seq == −m_seq`.
- **Bug:** rank sites by `m_seq` descending in the linter.
- **Symptom:** AUROC ≈ 1 − (true AUROC). Near 0.5 it looks like noise; far
  from it, you confidently flag the **safest** sites as riskiest.
- **Detector:** `test_risk_sign_is_opposite_to_margin`.

### (2) Collapsing the hurdle

- **Where:** `outcomes.hurdle`, and any aggregation you write over it.
- **Misunderstanding:** that "reversion rate" is one number.
- **Reality:** `P(observed) = P(O) · P(Y|O)`. Conditions that differ in reach
  are not comparable on the raw count.
- **Bug:** reporting `n_reverted / n`.
- **Symptom:** exactly Experiment 02 — `3/3` vs `15/20` read as "scaffolding
  increases reversion," when conditional reversion *fell* from 1.00 to 0.75.
- **Detector:** `test_hurdle_separates_reach_from_choice`. `HurdleResult` has
  no such field, so you would have to add one on purpose.

### (3) Treating sites as independent

- **Where:** any analysis consuming `sites.classify` output.
- **Misunderstanding:** 103 semantic sites = 103 observations.
- **Reality:** 3 prefix groups contain 63 of them. Sites sharing a byte-
  identical prefix are the **same stimulus** counted twice, and no
  prefix-conditioned predictor can be right about both when they disagree.
- **Bug:** bootstrapping at the site level; quoting `n = 103`.
- **Symptom:** intervals ~2.5× too narrow; an AUROC ceiling you cannot explain
  and that a reviewer finds for you.
- **Detector:** `sites.prefix_collisions`; `dedupe_by_prefix` leaves **40**.

---

## 9. AI-generated-code audit

Every tunable constant in `src/` and `scripts/`, with an honest provenance
label. **"Apparently arbitrary" is used freely below — it is the truthful label
for most fixture constants, and pretending otherwise would be the failure mode
this audit exists to prevent.**

| Value | Where | Role | Provenance |
|---|---|---|---|
| `(0,1,2,4,8,16,32,64,128)` | `scoring.DEFAULT_LADDER` | shot ladder | **Mathematically motivated** — geometric spacing gives uniform resolution in log-dose, the right scale for a threshold. The endpoint 128 is **compute-constrained**. |
| `eps = 1e-6` | `scoring._logit` | logit clipping | **Apparently arbitrary.** Standard practice, but it determines the DiD when a cell saturates at p=0 or 1. With n=4 per cell, `logit(1−1e-6)=13.8` can dominate. **Should be replaced** by a principled continuity correction (e.g. Haldane–Anscombe, add ½). Flagged as a real weakness. |
| `p_at_10 = 10` | `linter.rank_report` | top-k | **Apparently arbitrary** placeholder. Should be set by the realistic rewrite budget for a grammar. |
| `0.5` for ties | `linter.auroc` | tie handling | **Mathematically derived** — the Mann–Whitney definition. |
| `2.5` | `models.FakeLM.familiar_bonus` | planted bias | **Apparently arbitrary** — fixture only, overridden in every test. |
| `1.5` | `models.FakeLM.context_bonus` | planted interaction | **Apparently arbitrary** — fixture only; defaults to 0.0 at call sites. |
| `0.75` | `models.FakeLM.per_token_cost` | length penalty | **Apparently arbitrary** — fixture only. |
| `0.35` | `models.FakeLM.noise` | tie-breaking jitter | **Apparently arbitrary.** Chosen small enough not to swamp a 3.0 bonus. Note `test_margin_is_zero_without_bias_at_matched_token_length` only holds at `noise=0`. |
| `("('", '("', " ", ".")` | `models.FakeLM.cue_suffixes` | context cue | **Apparently arbitrary** — a stand-in for the unbuilt A-level calibration. |
| `prefix[-64:]` | `models._h` | hash window | **Apparently arbitrary.** Determinism is unaffected, but two prefixes agreeing in the last 64 chars get identical noise. |
| `max_new_tokens = 256` | `models` | generation cap | **Inherited** — Experiment 02 used 512. **Inconsistent**; align before Arm B. |
| `dtype="bfloat16"`, `device="cuda"` | `models.HFModel` | precision | **Compute-constrained.** Phase 2 used fp32 for base scoring and fp16 for generation. Changing precision changes log-probs; **must be fixed and recorded per run.** |
| `48` | `tests.PREFIX_TAIL` | fixture key | **Empirically calibrated** — and found inadequate: prefixes collide, which is how finding 4 was discovered. Now unused for keying (full prefixes are used). |
| `1e-9`, `1e-12` | tests | float tolerances | **Mathematically derived** — these are exact-arithmetic identities; the tolerance only absorbs float error. |
| `20260925` | `configs/experiment.json` | seed | **Apparently arbitrary.** **Not consumed by any code.** |
| `65536` | `vendor_sync.sha256` | read buffer | **Standard**, no scientific effect. |
| `limit=40`, `bonus=3.0/4.0/5.0/50.0`, `[:8]` | tests | fixture sizes | **Apparently arbitrary** — fixture only. |

### Cross-file inconsistencies

1. **`max_new_tokens`: 256 (`models.py`) vs 512 (Experiment 02 config).** Will
   change truncation and therefore `P(O)`. Reconcile before Arm B.
2. **`seed` in `configs/experiment.json` is never read.** The config is a
   template; nothing consumes it. A reader may reasonably assume it is live.
3. **Precision is unmanaged.** `HFModel` defaults to bf16 for everything;
   Phase 2 used fp32 for base NLL and fp16 for generation. Base-model
   log-probs are the input to H4, so this is not cosmetic.
4. **"Fertility" is claimed on character length.** README and `make_delta`
   report a **character-length** ratio of 1.0078 and reason about fertility.
   These are different quantities. The tokenizer check has **not been run**.
   Both documents flag it; do not let the flag get dropped.
5. **`FakeLM.n_tokens` is not any real tokenizer.** It counts alternating
   word/non-word runs. Fine as a fixture, but no conclusion about token-length
   matching may be drawn from tests that use it.

### Data assumptions that differ across files

- `sites.py` assumes a site's `prefix` identifies it (used for keying and for
  `score_site`). `prefix_collisions` proves that assumption false for 61% of
  sites. The two coexist; **the caller must dedupe**, and nothing enforces it.
- `outcomes.observe_site` deliberately does **not** require the whole program
  to parse, while `evaluate` does. Both are correct for their purpose, but a
  record joining them will contain rows where `reached=True` and
  `bucket=PARSE_FAIL`. That is intended, and will look like a bug if you do
  not expect it.
