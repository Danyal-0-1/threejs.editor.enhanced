# 07 — Next steps: what must happen before Sol

The ten items below are the full list. Items 1–6 and 9 were **done in this
revision**; 7, 8 and 10 are **not done** and are what stands between Phase 3.2
and a justified cluster run.

> **The summary that prompted this revision, and which was accurate:**
> Phase 3.2 built a much better runway and repaired the speedometer. The
> engine started and produced a real signal — but the first run drove only on
> the `dom` half of the runway, never tested the clean `blk` half, and did not
> save the flight recorder.

---

## Status of the ten items

| # | Item | Status |
|---|---|---|
| 1 | balanced sampling across family/mapping/stratum/template/role | **done** — `sampling.balanced` + `assert_balanced` |
| 2 | score all 544 `d50s1` sites (272 dom + 272 blk) | **done** |
| 3 | report family × stratum, never pooled | **done** |
| 4 | real mapping table in the prompt + no-rule control | **done** — `prompts.py` |
| 5 | save every individual margin with full provenance | **done** — per-site rows |
| 6 | inspect remaining exact-zero margins | **done** — printed every run |
| 7 | freeze held-out mappings and the analysis before the larger run | **NOT DONE** |
| 8 | uncertainty by resampling templates/mappings, not sites | **NOT DONE** |
| 9 | run one small balanced checkpoint first | **done** — 0.5B base + instruct, 544 sites x 2 conditions, 2,176 rows |
| 10 | if the effect survives in `blk`, scale up and add a second tokenizer family | **NOT DONE** — but the gate has now been *checked*: `blk` reversion is 0.423-0.456, matching `dom`, so the effect does survive in the fertility-matched family |

Three defects were found and fixed along the way: **P32-002** (the rule prompt
contained no rule), **P32-003** (first-*N* slicing scored only `dom`), and
**P32-004** (aggregates only, no per-site records). All three are documented
with blast radius in `../CHANGES_FROM_PHASE3.md`.

**And one conclusion was withdrawn.** The "sigil >= verb, so 3D-domain
knowledge is not driving the effect" claim was produced by the dom-only,
no-table run. Balanced and with a real rule, the stratum ordering flips
between conditions. Item 2 below (length-matched re-analysis) is what the
question now needs, and it costs no GPU.

---

## Step 7 — Preregistration (the next thing to write)

**Why first.** Everything after this point is confirmatory. Once a large run
has been seen, no amount of discipline makes the analysis preregistered, and
the H4 claim depends on the predictor having been frozen before the test data
existed.

**What to freeze, in one file, before any further model runs:**

- **Splits.** Development: `dom` × {δ25, δ50}. Held out: **`blk`** (grammar
  family) and **δ75** (mapping density), plus at least one unseen seed.
  Nothing from a held-out cell may inform score construction, thresholds or
  calibration.
- **Primary endpoint.** The `k*` extinction threshold, per `02 §6`. Declare
  the ladder and the censoring rule.
- **H4 success criterion.** A numeric margin over `identity_baseline` and
  `length_baseline`, declared in advance. "Beats the baseline" is not a
  criterion; "AUROC exceeds `identity_baseline` by ≥ 0.10 with a 95% interval
  excluding zero" is.
- **Scale-robustness rule for H2.** Sign must agree on margin, logit and
  probability scales (`phase3.scoring.interaction_did.sign_agrees`).
- **Exclusions.** What makes a site ineligible — exact-zero margins,
  degenerate tokenisations, prefix-collision group membership.
- **Stopping rule.** What result ends the programme rather than prompting
  another variant.

**Deliverable:** `phase3_2/PREREGISTRATION.md`, committed before the next run.

---

## Step 8 — Uncertainty at the right unit

**The error to avoid.** Every number currently reported is a point estimate.
Bootstrapping over *sites* would be wrong: sites are nested in templates,
which are nested in mappings, and 36.4% of semantic sites still share a prefix
with another site. Resampling sites treats one stimulus as several
observations and produces intervals far too narrow.

**What to do.**

- Resample **templates** (80) and **mappings** (9) — the independently
  constructed units — not the 3,326 sites.
- Keep paired cells intact: a template resample must carry all of that
  template's sites, in every family and condition.
- With two grammar families, treat **family as a fixed stratification factor**,
  not a random effect. Two levels cannot estimate a variance.
- Report intervals on every headline number, including `k*` (respecting
  censoring) and the rule effect.

**New dependency:** `statsmodels` for the mixed-effects layer. Still not in
the repository.

---

## Step 10 — Scale, conditional on `blk`

**The gate.** If the effect does not appear in `blk`, do not scale. `blk` is
the fertility-controlled family (`F_rel ≈ 1.00` vs `dom`'s 1.077), so a `dom`-only
effect is confounded with token cost and a bigger run would only buy a more
precise estimate of a confound.

**If the gate passes**, scale on two axes, in this order:

1. **Tokenizer families.** DeepSeek-Coder, StarCoder2, Llama-3, OLMo-2 — not
   more Qwen sizes. P32-002's merging behaviour is a property of the
   tokenizer, so the whole `k_common` structure will differ, and that is the
   point. StarCoder2 and OLMo-2 have open training data, which later allows
   corpus-grounded priors instead of model-preference proxies.
2. **Capacity**, as replication strata, never as a causal variable. The 3B run
   already produced an allocator warning on a 16 GB laptop GPU; 7B–32B is what
   Sol is for.

**Costs.** Arm A is forward-only and cheap: 544 sites × 2 conditions ran in
seconds per checkpoint. The full sweep across 5 families × 4 sizes ×
base/instruct is single-digit A100-hours. **Arm A is not the expensive part
and should not be rationed.**

---

## Beyond the ten: what is still missing entirely

| Gap | Why it matters | Blocking? |
|---|---|---|
| **Arm B** (unrestricted generation) | Arm A is teacher-forced and artificial; `P(O)` and the ecological claim need real generation | yes for the paper |
| **Extinction curves on a real model** | the declared *primary* estimand has never been computed on real weights | yes |
| **H4 linter on real scores** | the headline contribution is still untested end to end | yes |
| **External DSL** (tool schemas) | kills the "why not just use CSS" objection permanently | yes for a venue |
| **`T` / `A` calibration** | needed only for H2, which is secondary | no |
| **Prompt paraphrase robustness** | the current result rests on **one** prompt | yes |
| **Length-matched stratum analysis** | sigil candidates are 1 char, verb candidates are words; the stratum contrast is confounded with token length | yes for the 3D claim |
| **Environment capture** | no run manifest, no model revisions pinned, no global seed | yes for reproducibility |

---

## The order I would actually run it

1. **Preregister** (step 7). Nothing else first.
2. **Length-matched stratum re-analysis** on `outputs/arm_a_balanced.json`,
   which already has every per-site row. Sigil candidates are 1 character and
   verb candidates are words, so the stratum contrast is confounded with token
   length. Costs no GPU and is what reopens or closes the 3D question.
3. **Prompt paraphrase check** — three rule phrasings, same sites. Cheap, and
   it tests the one thing the entire result currently rests on.
4. **Extinction curves** on 0.5B/1.5B, `blk` only. This is the primary
   estimand and it has never been run.
5. **Gate:** does the effect hold in `blk` with intervals? If no, stop and
   write the negative result — it is publishable on a released benchmark.
6. **Scale** (step 10) on Sol, with uncertainty (step 8) built in from the
   start.
7. **Arm B + the H4 linter**, then the **external DSL**.

---

## The one sentence to keep in view

Phase 3.2's materials are ready; its **results are not yet results**. Every
real-model number here comes from one lexicon, one model family, one prompt,
and no confidence intervals. Fix items 7, 8 and 10 — and the paraphrase and
length-matching checks above — and Sol is justified.
