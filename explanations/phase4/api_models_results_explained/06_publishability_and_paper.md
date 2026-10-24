# 06 — What this run adds to the paper, and how to report it

> An honest assessment for planning. Every number is from [00](00_complete_results.md). Model
> descriptions come from the API's own listing (`configs/voyager/models_2026-10-22.json`) and
> were not checked against the model makers' publications.

---

## 1. Short answer

**It adds external validity, not a new confirmatory result.**

- **What it shows.** Nine newer and much larger models, served by ASU Research Computing (7B to
  about 550B parameters), prefer the familiar spelling as often as Phase 3.3's 21 checkpoints did:
  40–51% of sites with the token table, on the identical held-out cells.
- **What it is.** A development run: exploratory, measured before Phase 4's hypotheses were
  registered. It can be reported as such, next to Phase 3.3's confirmatory results.
- **Why it is still strong.** The nine models met exactly Phase 3.3's held-out cells: the same
  sites, prompts, ladder and requests. The comparison is cell for cell; only the model changed.
- **What it cannot carry.** A claim that these models were *predicted* to behave so; H4 or H5
  for them (no base twins); a precise size trend (the large models are mixtures of experts,
  quantized, served).

---

## 2. Where it goes in the paper

A section after the confirmatory results, titled for what it is:

> **6.x Exploratory: newer and larger served models.** To see whether prior reliance persists
> beyond the 0.5–72B checkpoints, we scored nine models served by ASU Research Computing
> (7B to about 550B total parameters, including mixtures of experts with 3–17B active parameters) on
> the identical held-out cells, after the confirmatory analysis was complete. These results are
> exploratory.

And one sentence in the abstract, after the main findings:

> In an exploratory extension, nine newer models served by a university inference service (7B to
> about 550B parameters) reverted at 40–51% of the same held-out sites with the token table.

---

## 3. Claims you can and cannot make

| ✅ you can say | ❌ do not say |
|---|---|
| with the table, nine served models from 7B to about 550B revert at 40–51% of the same held-out sites, overlapping Phase 3.3's 40–53% (exploratory) | that these models were tested confirmatorily |
| within Qwen3.5, 27B, 122B and 397B revert alike (0.40–0.44 with the table) | that size does or does not matter, from these nine (sizes, architectures, precisions and serving all differ at once) |
| the table moves served models' margins toward the correct spelling, by +0.34 to +0.86 nats, with an interval above zero in 17 of 18 model × grammar groups | that a served margin near zero has a known sign (rounding, batching) |
| OLMo 3 ends its turn at once under the raw-text Arm B prompt | that OLMo 3 cannot write 3DOM |
| served scores are rounded, and repeat only approximately under load; for Gemma 4 and Qwen3.5 122B, single margins changed substantially on re-scoring (Tables A1–A2) | "the same as Phase 3.3's measurement" without that caveat |

---

## 4. The limitations to state next to any served-model number

1. **No revision.** The model is pinned to a deployment, not to downloadable weights; it can be
   repeated only while that deployment runs.
2. **Precision.** Rounded scores (bf16) and quantized weights (fp8, mxfp4) for most models; ties
   occur, and margins move between identical requests: slightly for seven deployments, by up to
   10.7 nats for Gemma 4.
3. **Post-trained only.** No base models are served, so H4 and H5 cannot use them.
4. **Development status.** Measured before Phase 4's preregistration.
5. **Protocol.** Raw text, as in Phase 3.3. It makes the measurements comparable, but OLMo 3's
   Arm B ends at once under it.
6. **Contamination.** The materials are in a public repository; a model trained on data
   collected after they were pushed could have seen them.

---

## 5. The confirmatory test this run makes possible

The nine models are now development models, so a confirmatory test with them must hold out
**material**, as Phase 3.3 held out its mappings:

| design element | proposal |
|---|---|
| held-out material | new lexicons, made with `tools/build_materials.py` (new seeds at the same densities), registered in `splits.py` before any score |
| models | the nine served models (development) and, as held-out models, served models not used here and within the 600B ceiling (e.g. Llama 4 Scout and Maverick, gpt-oss-120b, Devstral 2, MiniMax-M3) |
| hypotheses | set from these development numbers, for example: "with the token table, every served model reverts at ≥ 35% of held-out sites" (here the lowest was 40.4%); "the table's effect is positive in every model × grammar group" (here 17 of 18) |
| measurement | as here, with four additions: (1) a pre-specified rule for ties and margins within one rounding step; (2) a bridge model scored both on Sol (fp32 head) and through the API, to measure the API's effect on the same weights; (3) a re-scored sample in every run, with a pre-set limit on how far a deployment may vary (here Gemma 4 and Qwen3.5 122B would fail it); (4) the Kaplan–Meier median computed without the rounding fault |
| Arm B | decide in advance between the raw-text protocol (comparability) and a chat format (models such as OLMo 3) |

---

## 6. The figures

| figure | message | for the paper? |
|---|---|---|
| `fig1_reversion` | served models revert like Phase 3.3's, with and without the table | **yes**: the main exploratory figure |
| `fig2_rule_effect` | the table helps every model, but not enough | yes, or as a panel of fig 1 |
| `fig3_scale` | no size cures it, up to about 550B | yes, with the caveat on sizes |
| `fig4_adaptation` | worked examples switch served models' sites as they did Phase 3.3's | appendix |
| `fig5_generation` | generation: reach and reversion given reach | appendix (OLMo 3 explained) |
| `figA1_precision`, `figA2_retest` | rounding and batching | methods appendix |

---

## 7. Threats to validity, and the answers

| threat | answer |
|---|---|
| "Served models aren't fixed artefacts." | Each was pinned to its deployment and every answer checked against it; 0 answers came from another deployment, in the run or in the re-test five to six hours later. |
| "Rounding decides the near-zero sites." | Their share is reported (Table A1) and bounds the effect on every rate. |
| "Batching noise." | Measured on a re-scored sample (Table A2): rates moved by at most 1.3 points. Two deployments (Gemma 4, Qwen3.5 122B) are not repeatable site by site, and the paper says so next to their numbers. |
| "The Kaplan–Meier medians." | A rounding fault inherited from Phase 3.3's code moves some medians to the next switch ([08 §6](08_issues_and_superseded_numbers.md#6-found-not-fixed-a-rounding-fault-in-the-kaplan-meier-median)). Fix it, with a dated deviation for Phase 3.3, before any median is reported. |
| "Quantized models are not the published ones." | Stated per model (Table 1); the measured model is the served one. |
| "The prompts were tuned on these models." | No: the prompts, sites and settings are Phase 3.3's, fixed before Phase 4 began. |
