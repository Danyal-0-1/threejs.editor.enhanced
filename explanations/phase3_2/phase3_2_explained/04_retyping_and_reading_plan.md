# 04 — Retyping and reading plan (Phase 3.2)

---

## 1. Inventory

Computed with `find`/`wc -l`, not estimated.

| Category | Files | Lines |
|---|---:|---:|
| **New Phase 3.2 Python** | **13** | **2,390** |
| Imported from Phase 3 (not copied) | 6 | 1,358 |
| Vendored via Phase 3 (not copied) | 8 | 4,380 |
| Generated φ files | 9 | — |

| File | Lines |
|---|---:|
| `src/phase3_2/backends.py` | 382 |
| `tests/test_phase3_2.py` | 437 |
| `src/phase3_2/templates.py` | 222 |
| `src/phase3_2/deltafam.py` | 201 |
| `scripts/run_arm_a.py` | 243 |
| `src/phase3_2/prompts.py` | 139 |
| `src/phase3_2/sampling.py` | 106 |
| `src/phase3_2/sites2.py` | 183 |
| `src/phase3_2/margins.py` | 163 |
| `scripts/build_materials.py` | 126 |
| `src/phase3_2/_vendor.py` | 99 |
| `tests/run_tests.py` | 89 |
| `src/phase3_2/__init__.py` | 0 |

---

## 2. Triage

**Rule:** LOAD-BEARING when a subtle mistake could invalidate the conclusion
*while the program still runs*. A crash is not the danger.

### LOAD-BEARING

| File | Why |
|---|---|
| `margins.py` | **The P32-001 fix.** Its predecessor returned a plausible `0.0` for 44.2% of sites and manufactured a false null. Nothing about that was visible from the output. |
| `backends.py` | `scan_sites` decides *where* a site is; `BlkBackend.parse` decides what the second family *means*. A wrong offset or a divergent IR silently reclassifies sites or fakes a cross-family effect. |
| `sites2.py` | The collision classifier. Same role as in Phase 3. |
| `deltafam.py` | A permutation that crosses a shape class turns SEMANTIC sites into LEXICAL ones and the contrast quietly disappears. The seed is also the entire counterbalancing mechanism. |
| `templates.py` (`selector_shapes`, `build_templates`) | Determines site count and prefix diversity — the thing Phase 3 got wrong. |
| `sampling.py` | **Defect P32-003 lived here.** A first-*N* slice scored one family and reported two. Selection bias is invisible in the output. |
| `prompts.py` | **Defect P32-002 lived here.** A prompt that claims to carry a rule and does not makes `M_seq` measure something else entirely. |

### PLUMBING

| File | Why |
|---|---|
| `_vendor.py` | Path wiring plus two guards that raise. Loud on failure. |
| `scripts/build_materials.py` | A reporting loop over the modules. |
| `scripts/run_arm_a.py` | Orchestration; the arithmetic is in `margins.py`. |
| `tests/run_tests.py` | Copied from Phase 3 unchanged. |
| `tests/test_phase3_2.py` | Read it — it is the executable spec — but no need to retype. |
| `templates.opening_diversity` | A **weak proxy**, documented as such; the real measure is `prefix_collisions`. |

---

## 3. The short list

Four files: `margins.py` (163), `backends.py` (382), `sites2.py` (183),
`deltafam.py` (201) — **929 lines = 46.3%** of the new code.

Understanding only these gives roughly **85%** of what is new in Phase 3.2.

**How that estimate was produced.** Not from line counts. Of the 8 rows in the
`01 §6` theory→metric table, **7** are implemented entirely inside these four
files; the eighth (real fertility) is 20 lines in `run_arm_a.py` that call a
tokenizer. Every quantity that reaches a result — collision class, site
offset, cross-family IR equality, density, counterbalancing, `M_seq`,
`k_common`, stratum — is defined here. The rest is orchestration and
reporting, where mistakes are loud.

---

## 4. Data structures first

| Object | What it is | Field that matters most |
|---|---|---|
| `backends.Backend` | one concrete syntax | `family` — tags every `site_id` |
| `templates.Template` | an abstract program as IR | `ir` — rendered per family/lexicon |
| `deltafam.Member` | one lexicon of the family | `permuted`, `density_actual`, `mode` |
| `sites2.Site` | one decision site (Phase 3's, unchanged) | `collision`, `prefix`, `correct`, `competitor` |
| `margins.MarginV2` | the corrected measurement | `m_seq`, **`k_common`**, **`merged`** |

The relationship to hold onto:

```
same template + same lexicon + different FAMILY
    => different prefix, different char_offset
    => IDENTICAL ir_hash_correct and ir_hash_competitor
```

Measured: `5be0d4314219` / `d74513ab1dcc` in both `dom` and `blk`. That is the
cross-family transfer test in one pair of objects.

---

## 5. One end-to-end path — the path to retype

| # | File | Function |
|---|---|---|
| 1 | `_vendor.py` | import → `assert_self_contained`, `assert_scorer_repaired` |
| 2 | `deltafam.py` | `verb_groups` → `_groups_for` → `build` |
| 3 | `phase3/vendor/.../phi.py` | `validate_phi` (V1–V8) via `load_candidate` |
| 4 | `templates.py` | `selector_shapes` → `build_templates` |
| 5 | `backends.py` | `DomBackend.render` / `BlkBackend.render` |
| 6 | `backends.py` | `scan_sites` → `_scan_inner` |
| 7 | `sites2.py` | `classify` → `_terminal_of_token`, `_safe_ir_hash` |
| 8 | `backends.py` | `BlkBackend.parse` (inside `_safe_ir_hash`, for blk) |
| 9 | `sites2.py` | `dedupe_by_prefix`, `stratum` |
| 10 | `margins.py` | `TokenScorer.score_pair` → `_score_from` → `divergent_margin` |

---

## 6. What to retype

### Core — 349 lines, **14.6%** of 2,390

| Function | File:lines | Lines | Why | In → Out | Invariant | Test after |
|---|---|---:|---|---|---|---|
| `score_pair` | margins 123–139 | 17 | **the P32-001 fix** | `(prefix,c,q)` → scores + `k` | both sides scored from the **same** `k` | `test_divergent_margin_scores_both_sides_from_the_same_point` |
| `_score_from` | margins 107–121 | 15 | the `logits[:-1]`/`ids[1:]` shift | `(ids,k)` → float | `k≥1`; empty span → 0.0 | same |
| `divergent_margin` | margins 142–163 | 22 | assembles the prefix once | `(scorer,site)` → `MarginV2` | one prefix, reused | `test_divergent_margin_finds_the_common_prefix` |
| `scan_sites` | backends 100–149 | 50 | where a site *is* | `(src,φ)` → tokens | first quoted string = selector; later = argument | `test_colour_literal_is_not_a_site_in_either_family` |
| `_scan_inner` | backends 152–169 | 18 | inner-stream offsets | `(body,base)` → tokens | offsets are **absolute** | `test_offsets_point_at_the_correct_spelling` |
| `BlkBackend.parse` | backends 290–332 | 43 | the second family's meaning | blk text → `IRProgram` | IR identical to `dom` | `test_blk_ir_roundtrip_whole_corpus_all_lexicons` |
| `classify` | sites2 83–149 | 67 | the collision classifier | `(text,φ,backend)` → `[Site]` | SEMANTIC ⇒ parses **and** different IR | `run_tests.py` |
| `build` | deltafam 125–176 | 52 | density + counterbalancing | `(density,seed)` → φ | I7: `CHAIN == CLASS`; density < 1 | `test_i7_overload_group_is_respected` |
| `verb_groups` | deltafam 90–96 | 7 | strict vs arity | mode → groups | strict ⇒ identical signature | `test_strict_mode_only_permutes_signature_matched_verbs` |
| `balanced` | sampling 56–82 | 27 | **P32-003** | `(sites,limit)` → sites | cell proportions preserved at any limit | `test_balanced_keeps_proportions_at_any_limit` |
| `assert_balanced` | sampling 98–106 | 9 | the check that was absent | sites → raises | every family present | `test_assert_balanced_fires_on_a_missing_family` |
| `rule_prompt` | prompts 93–104 | 12 | **P32-002** | φ → str | rendered FROM φ, never hard-coded | `test_rule_prompt_contains_the_actual_spellings` |
| `norule_prompt` | prompts 107–124 | 18 | the matched control | φ → str | same line count, spellings withheld | `test_norule_control_withholds_the_spellings_but_keeps_the_shape` |

### Optional — +112 lines, total **19.3%**

`BlkBackend.render` (34) · `templates.build_templates` (33) ·
`templates.selector_shapes` (45).

---

## 7. What to ignore for now

`_vendor.py` (read the docstring only) · both `scripts/` files (orchestration)
· `tests/run_tests.py` · `templates.opening_diversity` (a weak proxy) · all of
`phase3/vendor/` · `phase3/src/phase3/{scoring,outcomes,linter}.py` — imported
**unchanged** and already covered by Phase 3's 54 tests.

---

## 8. The three things you are most likely to get wrong

These are not hypothetical. All three happened in Phase 3.2's own first run.

### (1) Slicing a concatenated list and calling it a sample

- **Where:** `sampling.balanced` vs any `[:limit]`.
- **Misunderstanding:** that `dedupe_by_prefix(pool)[:240]` is a sample.
- **Reality:** the pool is built family by family, so the slice never reached
  `blk`. Measured: `Counter({'dom': 240})`, with 272 `blk` sites available.
- **Symptom:** a result reported as covering both families that covers one —
  and specifically drops the **fertility-matched** family, so the headline
  number is confounded with token cost.
- **Detector:** `sampling.assert_balanced`;
  `test_first_n_slice_would_have_scored_one_family_only` reproduces the defect
  deliberately so it cannot come back.

### (2) A rule prompt with no rule in it

- **Where:** `prompts.rule_prompt`.
- **Misunderstanding:** that saying "follow the token table" supplies a rule.
- **Reality:** the original prompt contained no table. `r` carried zero
  mapping information, so `M_seq` measured raw prior preference, not
  rule-override — a different quantity with a different meaning.
- **Symptom:** plausible reversion rates that cannot support any claim about
  specification-following, because nothing was specified.
- **Detector:** `test_rule_prompt_contains_the_actual_spellings`. Render the
  prompt and read it before trusting any margin.

### (3) The two sign conventions

- **Where:** `margins.divergent_margin` vs `phase3.linter.score_site`.
- **Reality:** `m_seq = logP(c) − logP(q)` → **positive is good**;
  `s_seq = logP(q) − logP(c)` → **positive is danger**. `s_seq == −m_seq`.
- **Symptom:** AUROC ≈ 1 − true AUROC. Invisible near 0.5; confidently
  backwards near 0.9.
- **Detector:** `phase3`'s `test_risk_sign_is_opposite_to_margin`.

> A fourth, retired but worth remembering: Phase 3's
> `sequence_logprob` returned `0.0` for 44.2% of sites (P32-001). Any exact-zero
> median is the signature. `run_arm_a.py` now prints the merged count and the
> residual exact-zero count every run.

## 9. AI-generated-code audit

Honest provenance labels. "Apparently arbitrary" is used freely — it is the
truthful label for most fixture constants.

| Value | Where | Role | Provenance |
|---|---|---|---|
| `(0.25, 0.50, 0.75)` | `deltafam.build_family` | densities | **Mathematically motivated** — spans the usable range below the 0.79 ceiling while keeping controls. The exact spacing is **apparently arbitrary**. |
| `(1, 2, 3)` | `deltafam.build_family` | seeds | **Apparently arbitrary.** Three is the minimum for a counterbalance claim; more is better and costs nothing. |
| `mode_for_high = 0.5` | `deltafam.build_family` | strict→arity switch | **Mathematically derived** — strict mode can only reach ~0.45 (5 of 15 verbs are signature-matched), so anything above it *must* use arity mode. |
| `target = 96` → yields 80 | `templates.build_templates` | corpus size | **Apparently arbitrary**; 80 is what 20 shapes × 4 statement counts produces. Not derived from a power calculation — **none has been run**. |
| `max_statements = 4` | `templates.build_templates` | depth | **Apparently arbitrary.** Drives prefix diversity; untuned. |
| 20 selector shapes | `templates.selector_shapes` | coverage | **Designed** to touch every inner production, but the *count* is arbitrary. |
| `NAMES` (12 identifiers) | `templates` | identifier pool | **Apparently arbitrary.** All are common English nouns, which may itself interact with the prior — **unmeasured**. |
| `VERB_VALUES` | `templates` | argument values | **Type-derived** from the C8 signatures; the specific numbers are arbitrary. |
| `k = 17` | `opening_diversity` default | window | **Mathematically derived** — `(function(){ $S('` is exactly 17 chars, the first sigil offset. Choosing 24 hides the problem (33 vs 3). |
| `TARGET = 300` | `build_materials` | success threshold | **Apparently arbitrary** — a round number chosen as "comfortably more than 40". Not a power calculation. |
| `--limit 240` | `run_arm_a` | sites scored | **Compute-constrained** — fits a laptop GPU in seconds. Far too small for inference. |
| `k < 1 → k = 1` | `margins._score_from` | guard | **Mathematically derived** — the first token has no context to be scored against. |
| `RULE` prompt text | `run_arm_a` | the remote specification | **Apparently arbitrary and scientifically load-bearing.** It is *one* prompt. The review requires paraphrase robustness; **not tested**. |
| `dtype float16`, `device cuda` | `run_arm_a` | precision | **Compute-constrained.** Phase 2 used fp32 for base scoring. Precision changes log-probs; **fix and record per run**. |
| `0.3669 / 0.4466` etc. | reported fertility | measurement | **Empirically measured** (Qwen tokenizer, 80 templates). |
| 28 roles in `ROLE_LABEL` | `prompts` | the token table | **Derived** from `terminals.json` substitutable set, minus the frozen value classes. The role *wording* ("operation: resize") is **apparently arbitrary** and is prompt-engineering that has not been varied. |
| rule 1,527 chars vs norule 1,014 | `prompts` | condition matching | **Empirically matched on line count (36 = 36), NOT on length.** A residual context-length effect cannot be excluded; reported with every result. |
| `--limit 0` default | `run_arm_a` | sample size | **Deliberate** — scoring everything removes the selection decision that caused P32-003. |

### Cross-file inconsistencies and declared deviations

1. **⚠ Phase 3.2 writes into Phase 3's tree.** `deltafam.write` puts
   `phi_d*.json` into `phase3/vendor/alien_syntax/candidates/` (9 files),
   because `phi.load_candidate` resolves there and nowhere else. **This is a
   real deviation from "create new work only inside the Phase 3.2
   directory."** It is declared rather than hidden. The clean fix is to make
   `candidates_dir` overridable; until then, `phase3/vendor/` is no longer
   byte-identical to what `vendor_sync.py` produced, and
   `vendor_sync.py --check` will still pass because it only checks the files
   it copied — it does not notice additions.
2. **Two scorers coexist.** `phase3.scoring.forced_prefix_margin` (defective
   for real models) and `margins.divergent_margin` (correct) are both
   importable. Nothing prevents using the wrong one. `run_arm_a.py` imports
   both; only the second is called.
3. **`FakeLM` vs `TokenScorer` are different interfaces.** `FakeLM` implements
   `sequence_logprob`; `TokenScorer` implements `score_pair`. They are not
   interchangeable, and `margins` requires the latter.
4. **Density semantics differ between fields.** `Member.density_actual` is a
   **role** fraction; the census reports a **site** fraction. 0.45 role ≈ 0.36
   site. Easy to quote the wrong one.
5. **No global run seed, and model revisions are unpinned.** Lexicons and
   templates are seeded and deterministic, and an `env` block (python,
   platform, dtype, device) is now recorded, but the HF model revision is
   not, so a silently updated checkpoint would not be detected.
6. **Two prompt conditions differ in length as well as content** (1,527 vs
   1,014 chars). Matched on line count only.

### Data assumptions that differ across files

- `scan_sites` assumes the **first** quoted string in a statement is a
  selector. True for both current families; a family with two selectors per
  statement would break it silently. No test guards a third family.
- `sites2.classify` assumes a site's `prefix` identifies it;
  `prefix_collisions` shows 36.4% of semantic sites still share prefixes after
  the rebuild. **The caller must dedupe; nothing enforces it.**
- `templates` assumes argument values do not interact with the prior. The
  identifier pool is English nouns and the colours are hex — both plausibly
  familiar to the model, both **unmeasured**.
