# 00 — The complete guide: Phase 3.3 on Sol

Read this first. For the whole thing as one image, read [`07`](07_the_picture.md).

| Doc | What it holds |
|---|---|
| [`01`](01_theory_and_research_design.md) | theory, every new concept in ten points |
| [`02`](02_mathematics_and_statistics.md) | mathematics, every formula with a real worked number |
| [`03`](03_code_and_pipeline.md) | code and pipeline, INPUT → TRANSFORMATION → OUTPUT → VALIDATION |
| [`04`](04_retyping_and_reading_plan.md) | what to read and retype, and the AI-code audit |
| [`05`](05_glossary.md) | glossary |
| [`06`](06_knowledge_check.md) | questions, no answers |
| [`07`](07_the_picture.md) | the mental image |
| [`08`](08_changes_defects_and_superseded_numbers.md) | every defect and every changed number |

Commands: [`../README.md`](../README.md). Evidence: [`../AUDIT.md`](../AUDIT.md).
What the brief got right or wrong: [`../PROMPT_REVIEW.md`](../PROMPT_REVIEW.md).

---

## Update — 2026-10-07: the first real development run

**What ran.** `dev-20261006a` ran on Sol's A100s. Four Qwen2.5-Coder checkpoints (0.5B and 1.5B, each
base and instruct) scored 10,224 Arm A rows and 16,000 extinction rows. No cell failed or went
missing, and the whole run used about 17 minutes of A100 time.

**What was corrected afterwards.** These are analysis corrections, made before the freeze
(deviation D9):

- tied scores in AP and precision@k;
- the power table and report;
- the run summary's counts.

All of them were re-derived from the saved measurements without re-scoring. Every measurement
file is byte-identical; see `08 §5` and the run's `analysis_revisions/`.

**What it says.** Development only, so exploratory and not confirmatory:

| Model | Reversion with the table | Extinction: KM median shots, initially-wrong sites |
|---|---|---|
| 0.5B base | 0.41–0.43 | 6.2 [2.4, 7.8], 13% censored |
| 0.5B instruct | 0.39–0.44 | 5.9 [2.6, 11.5], 18% censored |
| 1.5B base | **0.50–0.58** | 5.7 [3.1, 10.1], 22% censored |
| 1.5B instruct | 0.45–0.51 | 3.6 [2.3, 6.7], 20% censored |

- **Reversion, by lexicon.** In development, the 1.5B models revert more than the 0.5B ones.
  Two sizes cannot establish a trend. D10's larger held-out models were chosen for external
  validity, following prior work at 14B–70B, and their scale analysis is two-sided: it does
  not rest on this pattern.
- **Rule effect.** Small and positive, +0.08 to +0.36 nats; 31 of 32 intervals include zero.
- **H4.** The base model's margin predicts the instruct model's reversions:
  - AUROC 0.869 (0.5B pair) and 0.935 (1.5B pair);
  - AP 0.819 and 0.924, against prevalences of 0.41 and 0.47;
  - C1 and C2 are met *in development*. Against identity the gain is +0.37 [0.33, 0.40] and
    +0.43 [0.41, 0.46]. Against length it is +0.32 [0.25, 0.40] and +0.45 [0.39, 0.51].
    Holm p = 0.001 for each;
  - it also beats the exploratory `terminal_rate` baseline, the instruct model's reversion
    rate for the same terminal in other templates: +0.072 [0.009, 0.140] and
    +0.145 [0.097, 0.199].
- **Power.** At the clustering measured in development (ICC 0.252), the pooled rule effect has
  power 0.25 at the 80-template corpus. The report used to show 0.99, from the ICC = 0 row.
  H4 criterion 1 is well powered for a true AUROC of 0.62 or more.

**What's next:**

1. corrected analysis on Sol;
2. review power and design;
3. finish the model downloads (the Llama pair is approved and downloaded; the 10 large checkpoints are to fetch);
4. freeze;
5. held-out evaluation;
6. Arm B and H5;
7. final analysis.

---

## 1. What this phase is

Phase 3.3 produced the first extinction curves and rule-effect intervals on a
laptop. This phase turns that work into something that can run on ASU Sol
**and be believed**. That meant two jobs:

1. **Fix what made the old numbers wrong.** Ten stop-ship defects were named in the
   brief; all ten were verified, and all are fixed. Nine more were found along the way.
2. **Make it impossible to fool ourselves at scale.** The development/held-out
   split is enforced in code, with an immutable freeze and a typed unlock. Results are
   crash-safe and byte-reproducible, and every row carries full provenance.

The science is unchanged. H4 is the headline: predict *which* sites fail. H5
repairs them. Extinction curves are the scientific result. H2 is secondary.

| | Phase 3.3 (laptop) | This phase |
|---|---|---|
| headline `k*` | ≈ 5–7 shots | **withdrawn**: leakage plus definition errors |
| rule-effect intervals | 1 of 4 excluded zero | **all 4 include zero** |
| `blk` | the held-out grammar | **inspected**, so not held out (C3 NOT TESTABLE) |
| development / held-out | a promise | **code**: freeze, unlock, drift check on every access |
| output | one JSON at the end | atomic shards, resume, byte-identical merge |
| margin precision | bf16 | fp32 output head |
| controls | `norule` | + `norule_lenmatched` |
| Sol readiness | scripts that would not have run | 11 jobs, a submit wrapper, safe environment activation, preflight, pinned offline models |
| tests | Phase 3 (54) + Phase 3.2 (36) | **+ 112 Sol tests**, and a full CLI rehearsal |

---

## 2. What enters

| Input | Source | Size |
|---|---|---|
| frozen terminal table, 80 templates, 2 grammar families | Phase 3 / 3.2, unchanged | 43 terminals; `dom`, `blk` |
| 9 lexicons | the delta family | development `d25s1 d25s2 d50s1 d50s2`; held-out `d25s3 d50s3 d75s1a d75s2a d75s3a` |
| preregistration | `phase3_2/PREREGISTRATION.md` | frozen text, sha `a0146494…`; deviations D1–D8 appended |
| models | the Hugging Face Hub, pinned revisions | development: Qwen2.5-Coder 0.5B/1.5B base + instruct. Held-out adds Qwen 3B (weakened), deepseek-coder 1.3B, Llama-3.2-1B, starcoder2-3B |
| Sol facts | you, verified on 2026-10-05 | `grp_tlingego`, `public`/`public`, `gpu:a100:1`, `a100_80`; shared env torch 2.11.0+cu130; no `lark` in the shared env |

## 3. What happens

```
 prefetch (pins) ─► dev init ─► [Arm A ‖ primary] ─► dev analyze ─► FREEZE ─► UNLOCK (you)
                                     │                   │                         │
                         atomic shards, resume    19 CSVs · 12 plots · 10 reports  ▼
                                                                    held-out [Arm A, primary]
                                                                    ─► Arm B ─► H5 ─► final export
```

Each stage, with its inputs, outputs and checks, is in [`03 §4`](03_code_and_pipeline.md).

## 4. What exits

| Output | Status |
|---|---|
| corrected pipeline (`src/p33`, CLI, 11 jobs) | **built and tested** (2026-10-07, locally): 139 tests pass (venv); 135 + 4 dependency-blocked (bare python); the CPU-tests job, run as Slurm would on CPU only, exits 0 and writes nothing into the results root |
| full CLI rehearsal of the runbook, fake scorer | **passed** end to end, including a real SIGUSR1 interrupt and a single-index resume (`AUDIT.md` §6) |
| development smoke, one real model, 12 sites | **ran** on the laptop GPU (A100 check waived and recorded). 19 CSVs, 24 plot files, 10 reports |
| development sweep | **not run** (Sol) |
| freeze, unlock, held-out evaluation | **not run**. Your decision; nothing is automatic |
| H4, Arm B, H5 on a real model | **not run**. H4 needs an instruct twin, which the smoke does not include |
| H2; H4 criterion C3 | **NOT TESTABLE** with these materials |

---

## 5. The results that matter

### (1) Every stop-ship defect was real, and the old results inherited them

All ten claims in the brief were checked by computation before anything was
changed (`AUDIT.md` §2):

- 82 of 120 extinction sites had seen their own answer;
- 84 / 41 / 16 curves were mis-scored by the `k*` bookkeeping;
- the bootstrap returned 2.000 where 5/3 is correct;
- selection changed when the CLI order changed.

**The consequence:** the Phase 3.3 headline `k* ≈ 5–7` is **withdrawn**, and every
rule-effect interval now includes zero (`../../../phase3_3/ERRATA.md`).

### (2) Rehearsing the runbook found eight more defects the unit tests did not

All eight are listed in `08 §1`:

| Defect | What it would have done on Sol |
|---|---|
| P33-011 | the test suite rewrote tracked lexicons |
| P33-012 | resubmitting one model scored nothing |
| P33-013 | the CPU-tests job stopped after one suite |
| P33-014 | concurrent array tasks could corrupt a plan file |
| P33-015 | held-out access did not re-check the frozen code |
| P33-016 | test mode could leak into real jobs |
| P33-017 | a plain `status` made the freeze job refuse a complete run |
| P33-018 | re-running prefetch could re-pin models after the freeze |

Each now has a test.

> 🧠 *The unit tests check that each part works. The rehearsal checks that the
> parts work in the order a person will actually run them, on a machine that
> interrupts them.*

### (3) `blk` cannot confirm anything about new grammars

It was scored before the freeze. "H4 generalises to an unseen grammar"
(criterion C3) is **NOT TESTABLE** until a new family is approved, designed
and frozen. H4 can still be supported on held-out *mappings* and *models*.

### (4) The machine works, end to end, on a real model

The one development smoke (Qwen 0.5B, `dom × d50s1`, 12 sites) gave:

| Check | Result |
|---|---|
| preflight | all checks passed |
| Arm A | 36 / 36 rows, 9 / 9 cells |
| primary | 48 / 48 rows, 8 / 8 cells |
| exact-zero margins | 0 |
| ties | 0 |
| merged-token sites | 6 / 36 |
| demonstration leaks | 0 |
| fertility, identity `dom` | 0.3669 tokens/char, reproducing Phase 3.2's independent measurement exactly |

### (5) Interrupted work comes back identical

The merged output of an interrupted-and-resumed run is **byte-identical** to an
uninterrupted one. This is tested, and was checked with real signals on the
final code. A SIGUSR1 sent mid-run gave exit 4 (`INTERRUPTED, signal 10`); the
task, resubmitted alone, completed; and the merged 960 rows were byte-identical
to an uninterrupted run. A real SIGTERM recorded `INTERRUPTED, signal 15`.

### (6) What the smoke says, and what it does not

With the table present, the model reverted at 7 of 12 sites, 0.583 [0.333, 0.833]. The rule
effect is +0.182 [−0.433, +0.911] against `norule` and +0.291 [−0.368, +1.131]
against the length-matched control. Over the six ladder sites, the INITIALLY_WRONG KM median is 6.79 shots.

> **None of these numbers is evidence.** They show the arithmetic runs on real
> outputs. n = 12 cannot estimate anything, and every report produced from
> this run says so in its banner.

---

## 6. One complete example

Site `dom:d50s1:t000:T_CLASS_SIGIL:0`:

1. The program `(function(){ $S('#wheel')#recolor('#111111'); })();` puts the rule's `#`
   where CSS habit says `.`.
2. The tokenizer fuses `('#` into one token, so the divergence starts at token 302,
   one before the prefix ends.
3. With the table present: log P(`#`) = −4.4885 and log P(`.`) = −5.1358, so **M = +0.6473**.
   The model follows the rule, narrowly.
4. Along the ladder, M dips negative at 1 and 2 shots and recovers by 4. So `k* = 0`,
   the curve is non-monotone, and `sustained_k = 4`.

The whole trace through the code is [`03 §5`](03_code_and_pipeline.md); the
arithmetic is [`02 §1, §3`](02_mathematics_and_statistics.md).

## 7. Support and falsification

The full table is [`01 §18`](01_theory_and_research_design.md). In one line:
a held-out H4 result counts only if C1 and C2 pass after Holm on HELDOUT
cells, and does not rest on HELDOUT-WEAKENED (3B) cells alone. Extinction
counts only as an INITIALLY_WRONG KM median *with* its censoring rate and
interval.

## 8. What to read and retype first

[`04`](04_retyping_and_reading_plan.md):

- **Short list:** 7 files.
- **Core retype:** 827 lines (10.5%).
- **With the optional tier:** 1,030 lines (13.1%).

Start with `splits.classify`, `demos.is_leak`, `kstar.compute` and
`analysis._draw_rows`. Each is under 35 lines, and each one hid a defect that
changed a published number.

## 9. Honest status

| Item | Status |
|---|---|
| ten brief defects | **fixed**, each with a test that reproduces the old behaviour |
| nine further defects (P33-002, P33-011 … P33-018) | **fixed and tested** |
| 2026-10-07 analysis corrections (D9) | **fixed, tested and applied** to `dev-20261006a`; 652 measurement files unchanged |
| Phase 3.3 `k*` | **withdrawn**. The first valid, leakage-free estimate is development-only: KM medians 3.6–6.2 shots for initially-wrong sites |
| Phase 3.3 rule-effect intervals | **corrected**; all include zero |
| runbook | **rehearsed** locally with the fake scorer, in order |
| Sol | the development run **completed** (A100, 2026-10-07); held-out **not started** |
| real-model scoring | the laptop smoke plus the Sol development run. No held-out cell has been scored by a real model |
| held-out outcomes | **none inspected**; no full sweep submitted |
| H4 C3, H2 | **NOT TESTABLE** |
| power for the held-out size | **computed from the development pilot**; the rule effect is under-powered at the measured clustering, a design decision for you before the freeze |
| models | 21 held-out checkpoints (D10); the original 11 downloaded and pinned (Llama approved 2026-10-07); 10 large checkpoints not yet fetched |
