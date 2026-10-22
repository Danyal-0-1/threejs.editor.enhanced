# ERRATA — Phase 3.3 (issued 2026-10-05)

Two Phase 3.3 headline results are **withdrawn or corrected**. The original
documents are left in place, each with a banner pointing here, so the record
of what was claimed survives alongside the correction.

---

## E1 — `k* ≈ 5–7 examples` is WITHDRAWN (contaminated)

**Claimed** (`00 Result 3`, `01 §2.3`, `README`): the extinction threshold was
4.96–6.94 shots, with 8–18% censored.

**Why it is invalid — three independent defects, all verified by computation:**

1. **Demonstration leakage.** The ladder's examples were the first 32
   templates (t000–t031) for every site. **82 of the 120** sites came from those
   templates, so once the ladder reached their index the model was shown the
   site's own correct program. That measures copying, not the breaking of a
   habit, and biases `k*` downward.
2. **Already-correct sites mishandled.** 125 of 240 curves started with
   `M(0) ≥ 0`. 84 of them got `k* = None` (treated as missing) and the other 41
   got a `k*` from a LATER re-crossing. Correct definition: `k* = 0`.
3. **Censoring mis-defined.** "Censored" meant "negative at the last rung", so
   16 curves that crossed and later dropped were marked BOTH crossed and
   censored. A curve that crosses is not censored.

And one finding the old report missed entirely: **237 of 240 curves are
non-monotone** — the margin goes up and down as examples are added, so a
first-crossing threshold is noise-sensitive. The corrected pipeline records a
non-monotonicity flag, crossing counts and a "sustained" crossing per curve.

**Status:** the corrected `k*` (leakage-free nested demonstrations, the
correct definition, Kaplan–Meier for ALL and INITIALLY-WRONG sites) has been
measured only in the 12-site development smoke (`phase3_2/sol/local_smoke/`),
which is far too small to estimate anything. **There is currently no valid
`k*` estimate.** Recorded as preregistration deviation D3.

---

## E2 — rule-effect intervals CORRECTED (bootstrap multiplicity)

The template-cluster bootstrap paired rule with no-rule rows by `site_id`
inside each resample, so a template drawn twice was silently counted once —
each resample was effectively drawn without replacement (hand example: 2.000
returned where 5/3 is correct). Point estimates are unaffected; intervals
were too narrow.

| model | family | reported in Phase 3.3 | **corrected** | excludes 0 |
|---|---|---|---|---|
| 0.5B base | dom | +0.171 [+0.029, +0.326] | **+0.171 [−0.012, +0.370]** | no (was yes) |
| 0.5B base | blk | +0.156 [−0.020, +0.344] | +0.156 [−0.068, +0.402] | no |
| 0.5B instruct | dom | +0.199 [−0.003, +0.414] | +0.199 [−0.054, +0.477] | no |
| 0.5B instruct | blk | +0.222 [−0.004, +0.465] | +0.222 [−0.064, +0.530] | no |

**The sentence "3 of 4 intervals include zero" becomes "all 4 intervals
include zero".** Still exploratory (pre-freeze, one lexicon, one model family).
Recorded as deviation D4.

---

## E3 — `blk` is not a held-out grammar family

`04_sol_readiness.md` and the earlier preregistration treat all of `blk` as
the held-out grammar. `blk × d50s1` was scored before the freeze, so it is
not. Held-out-grammar confirmation is **NOT TESTABLE** until a new grammar
family is explicitly approved; `blk × never-scored mappings` is retained as a
WEAKER test, always labelled. Deviation D1.

## E4 — the Phase 3.3 Sol scripts would not have run

`phase3_2/sol/{arm_a,primary}.slurm` used `--partition=general`, which Sol
rejects for public jobs, and the prefetcher instantiated full models to
download them. Superseded by `phase3_2/sol/` (see `legacy_superseded/`).

---

**What still stands from Phase 3.3:** reversion ≈ 0.41–0.46 with the token
table present (tight intervals; still one lexicon / one model family);
`blk ≈ dom`; paraphrase stability of the reversion rate; the withdrawal of the
3D-knowledge conclusion (strata occupy disjoint token-length signatures).
