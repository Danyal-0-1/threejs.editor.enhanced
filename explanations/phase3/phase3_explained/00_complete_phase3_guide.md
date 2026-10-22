# 00 — The complete Phase 3 guide

The single document to read first. It answers twelve questions, carries one
ASCII pipeline diagram and one complete worked example, and points everywhere
else.

Companions: `01` theory · `02` mathematics · `03` code · `04` retyping ·
`05` glossary · `06` questions.

---

## 1. What scientific question is Phase 3 testing?

Two, deliberately ordered so that the safer one comes first.

**H4 — exact-site prediction (headline).**
> Does a **base** checkpoint's preference between the two competing spellings
> *at an exact grammar position* predict which positions an **instruction**
> checkpoint gets wrong — on unseen mappings and unseen grammar families?

**H2 — the interaction (secondary).**
> Does reversion rise super-additively when a strong competitor prior meets an
> immediate context that specifically cues that competitor?

H4 needs only a *main effect* of prior strength at sites. H2 needs an
interaction, which is both more fragile and more easily preempted. So a null
H2 costs one experiment rather than the programme.

**What is deliberately not claimed:** that familiar syntax beats unfamiliar
syntax (established), that definitions fail to override priors (established),
that grammar context helps (established), or anything about "reasoning" versus
"pattern matching" (not measurable). See `01 §2` and `01 §4.20`.

---

## 2. The idea in one paragraph

A DSL that borrows a familiar surface for human readability inherits the
prior attached to that surface. When the DSL rebinds a familiar spelling to a
different role, the model can emit the familiar form and be **silently wrong**:
the program parses, and it edits the wrong thing. Phase 3 (a) finds every
place in a grammar where that can happen, mechanically; (b) asks whether a base
model can predict which of those places will actually fail; and (c) repairs
them by rewriting only the risky spellings, with meaning preservation proved
rather than argued.

---

## 3. What enters the pipeline

| Input | Where from | Size |
|---|---|---|
| Frozen terminal inventory | `vendor/grammar_and_3DOM_client/terminals.json` | 43 terminals, 29 substitutable |
| Grammar templates | `vendor/alien_syntax/grammar/templates/` | 3 |
| Paired 3DOM programs | `conformance/positive.txt` via `generate_corpus` | **62** |
| φ-maps | `alpha`, `beta`, `gamma` (Phase 2) + **`delta`** (generated here) | 4 |
| A language model | `FakeLM` (tests) or `HFModel` (not yet run) | — |

---

## 4. What transformations occur

```
terminals.json ──► make_delta.py ──► phi_delta.json
                        │  permute WITHIN shape classes
                        ▼  validate_phi V1–V8  +  re-classify to prove SEMANTIC

positive.txt ──► phase1_programs ──► 62 × 3DOM text
                        │
                        ▼ transliterate(·, identity, delta)     [rename by ROLE]
                   62 × delta text
                        │
                        ▼ sites.classify          ◄── THE CORE
                   lex → (type, value, OFFSET)
                   splice q at the offset
                   re-lex / re-parse / re-hash the variant
                        │
                        ▼
              ┌─────────┴──────────┐
         NONE / LEXICAL         SEMANTIC   (103 for delta)
         (not usable)                │
                        ┌────────────┴────────────┐
                   ARM A │                        │ ARM B
            forced_prefix_margin → M_seq     generate → text
            extinction_curve     → k*  ★     evaluate → Bucket
            interaction_did      → DiD×3     observe_site → O, Y
                        │                     hurdle → P(O), P(Y|O)
                        └────────────┬────────────┘
                                     ▼
                                  linter
                      score_site  → S_seq / S_local / S_shift   (H4)
                      rank_report → AUROC / AUPRC / P@10 + baselines
                      propose_repair → Repair                   (H5)
                      verify_repair  → IR equality, all 62      (H5 proof)
```
★ primary estimand.

---

## 5. What exits

| Output | Object | Status |
|---|---|---|
| Classified sites | `list[Site]` + `outputs/site_census.json` | **measured** |
| Collision census | the table in §8 | **measured** |
| `delta` lexicon | `phi_delta.json` | **measured/validated** |
| Arm-A margins | `MarginRecord` | **tested on `FakeLM` only** |
| Extinction curves | `ExtinctionCurve` | **tested on `FakeLM` only** |
| Interaction | `InteractionResult` + `sign_agrees` | **tested on synthetic cells** |
| Arm-B outcomes | `Outcome`, `HurdleResult` | **tested** |
| Site risk + ranking | `RiskScore`, `RankReport` | **tested on `FakeLM` only** |
| Repair + proof | `Repair`, `verify_repair` | **tested over 62 programs** |

**No number in this repository comes from a real language model.**

---

## 6. The single primary result

**`k*`, the extinction threshold** — the number of in-context examples at
which `M_seq` crosses zero at a site.

Why a threshold and not the interaction: an *ordinal* interaction measured on a
log-probability margin is partly an artifact of the scale, because two factors
pushing the same direction generically produce "super-additivity" under a
compressive nonlinearity. `k*` is read off the **x-axis** and survives
monotone rescaling of the y-axis. (`01 §4.15–4.16`, `02 §5.1`, `02 §6`.)

## 7. Secondary results

- A×T difference-in-differences, reported on **three** scales with the
  preregistered rule that **the sign must agree on all three**
  (`sign_agrees`; `verdict()` says `SCALE-DEPENDENT` otherwise);
- exact canonical-IR accuracy (Arm B);
- `P(site reached)` and `P(revert | reached)`, never collapsed;
- parse validity and valid-but-vacuous rate, never averaged with accuracy;
- H4 ranking against mandatory baselines;
- H5 error reduction **per changed symbol**.

---

## 8. Four measured findings that already changed the design

Each reproducible with one command; none of them came from reading papers.

**(1) `beta` and `gamma` cannot support the primary contrast at all.**
`python3 scripts/site_census.py`

| lexicon | none | lexical | benign | **semantic** | usable |
|---|---:|---:|---:|---:|---:|
| alpha | 0 | 315 | 0 | **72** | 18.6% |
| beta | 0 | 387 | 0 | **0** | 0.0% |
| gamma | 0 | 387 | 0 | **0** | 0.0% |
| **delta** | 203 | 81 | 0 | **103** | 26.6% |

Their alphabets are disjoint from CSS, so the familiar spelling is always a
**lex error** — loud, never silently wrong. Their large ΔNLL distances are
irrelevant to this contrast.

**(2) Experiment 02's headline reversion site is LOUD, not silent.**
`T_CLASS_SIGIL` is **LEXICAL** under alpha: `.` binds to `T_WILDCARD`, which
takes no identifier, so the familiar `.door` is a *parse error*. The reported
`.`-for-`#` reversion was producing unparseable output — a different error
class with a different interpretation.

**(3) Silent collisions require permutation within a shape class.**
Hence `delta`: identity everywhere except four within-class permutations
(sigils; two signature-matched verb cycles; type keywords; pseudo keywords).
103 semantic sites, **zero benign**, all 13 intended terminals proven SEMANTIC
at generation time. Because the multiset of spellings is unchanged, measured
mean **character-length** ratio is **1.0078** vs identity (alpha 0.978, gamma
0.713) — so the fertility confound is largely removed *by construction*.
**⚠ Character length is not fertility; the tokenizer check has not been run.**

**(4) 61% of semantic sites are not identifiable from their prefix.**
3 prefix groups contain **63 of 103** sites: byte-identical context, different
correct spelling. No prefix-conditioned predictor can be right about both.
`dedupe_by_prefix` leaves **40**. This is simultaneously an AUROC ceiling and
an independence violation, and it is **the top blocker**.

---

## 9. One complete end-to-end example

Real output. Reproduce with the snippet in `03 §4`.

```
3DOM     (function(){ $S('.wheel').recolor('#111111'); })();
delta    (function(){ $S('#wheel')#recolor('#111111'); })();
                            ↑ offset 17 · T_CLASS_SIGIL · correct '#'

Site     site_id              delta:t000:T_CLASS_SIGIL:0
         prefix               "(function(){ $S('"
         correct / competitor '#'  /  '.'
         collision            SEMANTIC
         competitor_binds_to  T_ID_SIGIL      ← '.' means "id" in delta
         ir_hash_correct      5be0d4314219e5d2…
         ir_hash_competitor   d74513ab1dcc9490…   ← different meaning
         variant              (function(){ $S('.wheel')#recolor('#111111'); })();

Margin   logp_correct −1.0295 · logp_competitor +3.5227
         m_seq −4.5522  → reverted = True            (FakeLM, planted bias)

Outcome  VALID_WRONG · parse_valid True · task_correct False · n_ops 1

Observe  reached True · reverted True · emitted '.'
         "competitor spelling bound to T_ID_SIGIL"

Risk     s_seq +4.5522 · s_local +4.6957 · s_shift −0.1435
```

Two programs differing by **one character**, hashing differently: one edits
the wheel, the other edits an object with id `wheel`. `parse_valid=True,
task_correct=False` is the phenomenon in two fields.

This is the same `T_CLASS_SIGIL` site as Experiment 02's headline reversion —
**LEXICAL under alpha, SEMANTIC under delta.** Creating that difference is
what Phase 3 is for.

---

## 10. What would support the hypotheses

**H4.** Site risk ranks reversion above *all* mandatory baselines
(`length_baseline`, `identity_baseline`, whole-program NLL, token count) on
**held-out** mappings and at least one **held-out grammar family**, with
calibration reported and prevalence stated.

**H2.** The DiD has the predicted sign, a practically meaningful magnitude,
**agrees across all three scales**, and replicates on held-out mappings.

**H5.** Predicted high-risk sites benefit disproportionately, low-risk sites
stay stable, and the targeted rewrite matches global renaming with materially
**fewer changed symbols** — with IR equality proved over the whole corpus.

## 11. What would falsify them

**H4** — AUROC does not beat `identity_baseline`; or it collapses on held-out
mappings; or it separates lexicons but not sites within a lexicon.

**H2** — `sign_agrees == False`; or the interval excludes the smallest
meaningful effect; or it reverses on held-out grammars; or the A manipulation
changes general difficulty rather than competitor-specific support.

**H5** — repair helps no more per changed symbol than random rewriting at the
same budget; or it degrades ordinary non-colliding sites.

## 12. What would prevent mechanistic follow-up

The behavioural gate: **no** mechanistic work until an effect replicates on
held-out mappings **and** at least one held-out grammar family. Phase 3 cannot
currently pass it — there is only one grammar family (`01 §4.17`). Explaining
a non-robust effect is wasted effort, and mechanism is the most preempted part
of the programme.

---

## 13. Which code to read first

1. `src/phase3/sites.py` — the collision classifier **is** the experiment
2. `README.md` — the four findings and the status table
3. `scripts/make_delta.py` — why `delta` exists and how it is proved
4. `src/phase3/scoring.py` — sign conventions, `k*`, the three-scale rule
5. `PATCHES/tasks.op_selection.md` — the defect and its blast radius

## 14. Which code to retype

**Core: 381 lines = 13.5%** of the 2,820 new lines.

`sites.classify` · `sites._terminal_of_token` · `sites._safe_ir_hash` ·
`sites.prefix_collisions` · `scoring.forced_prefix_margin` ·
`scoring._interpolate_crossing` · `scoring.interaction_did` ·
`outcomes.evaluate` · `outcomes.observe_site` · `outcomes.hurdle` ·
`linter.score_site` · `linter.auroc` · `linter.verify_repair` ·
`HFModel.sequence_logprob` · the P3-001 patch.

Line ranges, invariants and the test to run after each: `04 §6`.

## 15. Which mathematical ideas first

1. **Log-probability margins and their signs** — `M_seq > 0` good;
   `S_seq > 0` danger; `s_seq == −m_seq`. (`02 §2`, `02 §9`)
2. **The hurdle decomposition** — `P(obs) = P(O)·P(Y|O)`. (`02 §7`)
3. **Scale-dependence of ordinal interactions** — why `k*` is primary.
   (`02 §5.1`)
4. **Censoring** — `k_star = None` is not zero. (`02 §6`)
5. **AUROC/AUPRC with prevalence** — and why `None` beats 0.5. (`02 §9`)
6. Only then: mixed-effects models and resampling units. (`02 §8`)

---

## 16. Honest status

**Tests: 54 passed, 0 failed** (`python3 tests/run_tests.py`, lark only, no
GPU). **Vendored files: 22/22 match the manifest.** Nothing outside `phase3/`
was modified.

**Built and tested:** vendoring + provenance + drift check · the P3-001 scorer
repair (13 adversarial tests) · site enumeration and collision classification ·
the `delta` lexicon · `M_seq`, `k*`, the three-scale DiD · the error taxonomy,
reach and hurdle · H4 risk scoring and ranking · H5 repair with a mechanical
IR-preservation proof.

**Not implemented:** prior-strength (T) calibration · local-context (A)
calibration · counterbalanced mapping generation · a second grammar family ·
statistical export · mixed-effects and power simulation · environment capture.

**Not run:** any real model · `delta`'s token fertility · three of the ten
reproducibility checks (counterbalancing, context-variant AST equality,
train/calibration/test separation) — these are **blocked**, because they test
features that do not exist. They are not passing.

**The one number that matters most right now:** after `dedupe_by_prefix`,
**40** prefix-distinct semantic sites, in **one** grammar family. That is too
few and too narrow to spend A100 time on. Template diversity and a genuine
second grammar family come before any real-model run.
