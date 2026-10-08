# PREREGISTRATION — Phase 3.3 confirmatory run

**Frozen:** 2026-10-02, before any Sol run and before any checkpoint above 3B
has been scored. Everything below is fixed in advance. Deviations go in a
"Deviations" section appended at the end, never by editing the text above it.

Next-steps item 7. Nothing here may be revised after a held-out cell is seen.

---

## 1. Hypotheses

**H4 (confirmatory, primary scientific claim).** A base checkpoint's
preference between the two competing spellings at an exact decision site
predicts which sites an instruction checkpoint gets wrong, on **held-out
mappings and a held-out grammar family**.

**Primary endpoint:** the extinction threshold `k*` — the interpolated number
of in-context examples at which `M_seq` first crosses zero.

**H5 (confirmatory, applied claim).** Rewriting only predicted-high-risk
sites reduces reversion more **per changed symbol** than random or global
rewriting, with canonical-IR equality proved over the whole corpus.

**H2 (exploratory, not confirmatory).** The prior × local-context interaction.
Reported on three scales with the sign-agreement rule; **never** promoted to a
headline claim in this run.

---

## 2. Splits — frozen

| role | cells |
|---|---|
| **development** | family `dom` × lexicons {δ25s1, δ25s2, δ50s1, δ50s2} |
| **held-out mapping** | δ25s3, δ50s3, and all of δ75 (s1a, s2a, s3a) |
| **held-out grammar family** | **all of `blk`** |
| **held-out models** | everything except Qwen2.5-Coder 0.5B/1.5B |

No held-out cell may inform candidate construction, score definition,
calibration, thresholds, prompt wording, or site exclusions. Development data
may be re-used freely.

---

## 3. Success criteria — numeric, declared in advance

**H4 is supported** iff **all** hold on the held-out cells:

1. AUROC of the site-risk score exceeds `identity_baseline` by **≥ 0.10**,
   with a 95% cluster-bootstrap interval on the difference excluding 0;
2. AUROC exceeds `length_baseline` by **≥ 0.05**, interval excluding 0;
3. AUROC ≥ **0.65** in absolute terms on the held-out **grammar family**;
4. the ranking holds in **both** families separately — never pooled.

**H4 is refuted** if any of (1)–(3) fails on held-out data, or if the score
separates lexicons but not sites within a lexicon.

**H5 is supported** iff error reduction per changed symbol exceeds the
matched-budget random-rewrite control with an interval excluding 0, **and**
reversion at low-risk control sites does not worsen by more than 0.02.

---

## 4. Analysis — frozen

- **Resampling unit:** `template` (primary) and `lexicon` (secondary, only
  once ≥ 8 lexicons are in the cell). **Never sites** — they are nested in
  templates and 36.4% share a prefix.
- **Intervals:** 95% percentile cluster bootstrap, B = 2000, seed 20261002.
  `analysis.cluster_bootstrap` returns `None` below 8 clusters and that is
  reported as "no interval", never as a point estimate alone.
- **Family:** fixed stratification factor, never a random effect (2 levels).
- **Censoring:** curves that never cross have `k_star = None` and are
  **retained** as censored. Censoring rate is reported beside every `k*`.
- **Multiplicity:** one primary (`k*` on held-out). Holm within the
  confirmatory family of H4 criteria; Benjamini–Hochberg for exploratory
  stratum and per-terminal comparisons.
- **Primary prompt:** `prompts.rule_prompt` (`p0`). `p1`/`p2` are a
  robustness check; if the three disagree in sign, the headline is the
  **range**, not the best variant.

---

## 5. Exclusions — declared before seeing data

A site is ineligible if **any** of:

1. `collision != SEMANTIC`;
2. it is not prefix-distinct after `dedupe_by_prefix`;
3. `m_seq == 0.0` exactly (degenerate tokenisation; currently 3 / 2,176);
4. its template fails to render or parse in either family.

Exclusion counts are reported. No exclusion may be added after inspecting
held-out outcomes.

---

## 6. Stopping rules

- **Stop and publish a negative result** if H4 fails criteria (1)–(3) on
  held-out data with adequate power. A released benchmark plus a
  well-powered null is a result.
- **Do not proceed to mechanism** unless a behavioural effect replicates on
  the held-out grammar family. (Unchanged behavioural gate.)
- **Do not scale beyond 3B** until the effect is present in `blk` with an
  interval excluding the null.

---

## 7. Power — stated honestly

**No power simulation has been run.** The planned Sol run is sized by what is
cheap (Arm A is forward-only), not by a power calculation. Consequence,
stated in advance: a null result from this run is **not** strong evidence of
absence, and will be reported as "underpowered for the smallest meaningful
effect" unless a simulation is completed first.

Known n: 3,326 prefix-distinct semantic sites in 80 templates and 9 lexicons.
The effective unit count is **80 templates**, not 3,326.

---

## 8. What is already known and therefore NOT confirmatory

These were measured before freezing and are **exploratory** regardless of how
they come out at scale:

- reversion ≈ 0.41–0.46 with the token table present (0.5B, `d50s1`);
- the rule effect is ≈ +0.16 to +0.22 nats, with **3 of 4 cells'
  intervals including zero**;
- `blk` ≈ `dom` on reversion;
- sigil and verb strata occupy nearly disjoint token-length signatures, so
  the 3D-knowledge contrast is **not currently identifiable**.

---

## Deviations

*(append below; do not edit anything above)*

- none yet

*(The "none yet" line above was true when the file was frozen on 2026-10-02.
Everything below was appended on 2026-10-05; nothing above "## Deviations"
has been edited — `sol/tests/test_prereg_env.py` verifies the frozen text's
SHA-256 is still a0146494a27d1206d0efc3cb7f77d2413bc09a4aedcb98a632a5c61f09f5f014.)*

### D1 — 2026-10-05 — `blk` is not a clean held-out grammar family

**What happened.** §2 lists "all of `blk`" as the held-out grammar family. But
`blk x d50s1` was scored BEFORE the freeze (Phase 3.2 balanced Arm A, 272 sites,
0.5B base + instruct; Phase 3.3 primary run, 60 sites), and §8 of this very
document reports "`blk` ≈ `dom` on reversion". The family was inspected.

**Change.** `blk` is no longer called a held-out grammar family anywhere in
code or reports. `sol/src/p33/splits.py` classifies `blk x {dev lexicon}` as
EXPLORATORY-CONTAMINATED (refused unless explicitly allowed, then labelled) and
`blk x {never-scored held-out mapping}` as HELDOUT-WEAK-FAMILY: a weaker test in
which the grammar has been seen but that mapping has not. No new grammar family
is invented; `APPROVED_NEW_FAMILIES` is empty.

**Scientific consequence.** H4 criterion 3 ("AUROC ≥ 0.65 on the held-out
grammar family") is **NOT TESTABLE** until a new grammar family is explicitly
approved, designed and frozen. H4 can therefore at most be supported on held-out
MAPPINGS and MODELS, never on a held-out grammar. The §6 gate "do not scale
beyond 3B until the effect is present in `blk`" cannot be satisfied by `blk`
evidence and is implemented as "no model above 3B in any stage".

### D2 — 2026-10-05 — Qwen2.5-Coder-3B was observed before the freeze

`arm_a_sizes.json` (Phase 3.2) scored 3B base and instruct on `dom x d50s1`
under a superseded protocol (dom only, no token table, pre-P32-002). 3B
remains a held-out model but every 3B row and aggregate is labelled
HELDOUT-WEAKENED. **Consequence:** 3B cannot be the sole basis of a held-out-model claim.

### D3 — 2026-10-05 — `k*` definition clarified; pre-freeze `k*` values withdrawn

§4 said only that curves which never cross are censored. The implementation
left already-correct sites without a `k*` (84 of 125), took a later re-crossing
for the other 41, and marked 16 crossed-then-dropped curves as censored.
Separately, 82 of the 120 pre-freeze extinction sites had their own target
program among the demonstrations. **Change:** `M(0) ≥ 0 ⇒ k* = 0`; otherwise
the first upward crossing, interpolated; no crossing ⇒ censored; a curve that
crosses and later drops is not censored; KM summaries for ALL sites and for
INITIALLY-WRONG sites; median-among-crossers retained as a labelled diagnostic
only; demonstrations exclude the target template, its program and any prefix
that replays the decision. **Consequence:** the pre-freeze `k*` ≈ 5–7 figures
(Phase 3.3 reports) are withdrawn as contaminated; they are not evidence.

### D4 — 2026-10-05 — pre-freeze rule-effect intervals withdrawn

The template-cluster bootstrap collapsed duplicate draws when pairing rule
with no-rule rows by `site_id`, so resamples were effectively drawn without
replacement (verified: a hand example returned 2.0 instead of 5/3). Fixed in
`phase3_2.analysis`. **Consequence:** the Phase 3.3 rule-effect intervals were
exploratory and are superseded; recomputed values are reported as exploratory.

### D5 — 2026-10-05 — the de-duplication unit is now (family, lexicon)

§5 exclusion 2 said "not prefix-distinct after `dedupe_by_prefix`". The global
first-occurrence implementation was CLI-order dependent (reversing the lexicon
order moved retained `d50s2` sites from 172 to 272). Sites in different
lexicons are different stimuli because the rule table differs, so
de-duplication is now WITHIN (family, lexicon), with a canonical tie-break.
**Consequence:** eligible-site counts change; every dropped site is listed in
`split_exclusion_audit.csv` with the site it duplicates.

### D6 — 2026-10-05 — the identity baseline is constant on the eligible set

Exclusion 1 keeps only SEMANTIC sites, all of which are remapped, so the §3
identity baseline is constant there and its AUROC is exactly 0.5. Nothing is
changed. **Consequence (stated, not hidden):** criterion 1 is equivalent to
"AUROC ≥ 0.60 with the difference's interval above 0". A non-preregistered
`terminal_rate` baseline (cross-fitted per-role reversion rate) is reported as
EXPLORATORY, because it is the stronger "language-identity detector".

### D7 — 2026-10-05 — measurement precision and the length-matched control

Scoring now computes the output projection in float32 from the final hidden
state (bf16 logits quantise near-zero margins; the outcome is a margin's sign),
and adds a `norule_lenmatched` control padded to the rule prompt's token count.
**Consequence:** a methods change made before any confirmatory run; both are
recorded in every job manifest.

### D8 — 2026-10-05 — development models include the matched instruct twins

§2 names "Qwen2.5-Coder 0.5B and 1.5B" as non-held-out. H4 needs both
checkpoints of a pair, so the development set is read as base AND instruct for
0.5B and 1.5B. No other model is development.

### D9 — 2026-10-07 — tied scores in AP and precision@k; power and report corrections (before the freeze)

**What happened.** The development run `dev-20261006a` (four Qwen2.5-Coder
checkpoints on A100s; 10,224 Arm A and 16,000 primary rows) was analysed with
metric code in which AP ordered tied scores by input row, precision@k broke a
tie at the k boundary by input row, every smallest-detectable-AUROC power row
used the pilot ICC whatever ICC scenario it belonged to (25 rows, 5 distinct),
the power report showed only the ICC = 0 rule-effect rows, and the run summary
counted its report files before writing them. On the development data the
constant identity baseline's AP was 0.452 or 0.492 depending on row order (its
correct value is the prevalence, 0.468) and its precision@10 was 0.4 or 0.6.

**Change.** AP is step-wise average precision with every tied score admitted
as ONE threshold, AP = sum_j (R_j − R_(j−1)) · P_j over the distinct scores.
Precision@k is the expected precision when the k boundary falls inside a tie
and the remaining places are filled uniformly from it:
P@K = (positives above + (K − a) · p / g) / K, with K = min(k, n). Both are
invariant to row order; a constant score yields the prevalence; distinct scores
give the previous values bit for bit; with no positive class AP stays undefined.
Every power scenario (template count × ICC) is computed once, with the ICC it
reports, the pilot estimate flagged, and template counts above the 80-template
corpus labelled hypothetical. The power report shows every ICC scenario and the
design effect and effective sample size behind them.

**Scientific consequence.** No registered criterion changes: C1 and C2 compare
AUROCs, and the average-rank AUROC was already tie-correct. The risk score has
852 distinct values per pair, so its AP and precision@k are unchanged; baseline
AP and precision@k values change. The rule-effect power at the pilot ICC (0.252)
is 0.251 at 80 templates, not the 0.994 that the report displayed (ICC = 0).
The registered design is NOT changed in response here; that decision belongs
to the investigator, before the freeze. All tables were re-derived from the
saved GPU measurements without re-scoring (analysis revision
`r1-2026-10-07-metric-corrections` in the run directory).

### D10 — 2026-10-07 — models above 3B, replacing the 3B gate

**What happened.** §6 registered "do not scale beyond 3B until the effect is
present in `blk`"; D1 showed that `blk` can never supply that evidence, so the
gate was implemented as "no model above 3B in any stage". The closest prior
work evaluates 14B–70B open models, and the literature disagrees on the
direction of scale effects (inverse scaling was reported for identifier swaps),
so a study capped at 3B cannot say whether its effect survives scale.

**Change.** Decided on 2026-10-07, after the development run `dev-20261006a`
and before any freeze or held-out access, for external validity and not in
response to development outcomes: the size ceiling becomes 72B. Ten held-out
MODEL checkpoints are added, each a base/instruct pair: Qwen2.5-Coder 7B, 14B
and 32B (with 0.5B, 1.5B and 3B, a six-size ladder at a fixed tokenizer and
training recipe), DeepSeek-Coder-33B (a second code family) and Qwen2.5-72B
(general model; two A100-80GB GPUs). All are scored in bf16 with the fp32
output head and never quantized. The development set and the completed
development run are unchanged; the new models are appended to the held-out
configuration. The gated Llama-3.2-1B pair stays in the design; access to it
was granted on 2026-10-07 and both checkpoints are downloaded and pinned.

**Pre-specified analysis.** Two-sided, no predicted direction: the reversion
rate and the H4 AUROC as functions of log(parameters) within the
Qwen2.5-Coder ladder, on held-out mappings, per family and never pooled
across families. Models of other families test generality, not scale.

**Scientific consequence.** H4 is tested on held-out models up to 72B with a
calibration frozen on 0.5B and 1.5B, a stronger transfer test: the criteria
are rank-based, and calibration metrics are reported knowing they may degrade.
Outside the Qwen2.5-Coder ladder, size remains confounded with everything else
that differs between checkpoints.

### D11 — 2026-10-08 — specification of the D10 scale analysis (after the freeze, before any held-out outcome was examined)

**What happened.** D10 pre-specified a two-sided scale analysis, but the
frozen pipeline (`DEV_FREEZE.json` of `dev-20261006a`, 2026-10-07) exports only
its inputs: the per-model Arm A rows and the per-pair H4 predictions. The
analysis itself was never implemented, and D10 did not state its statistic.
This was found on 2026-10-08, while the held-out chain of `heldout-20261007a`
was running and before any held-out outcome had been examined: only job
states and cell counts had been read.

**Change.** The analysis is computed by `phase3_2/sol/scripts/scale_analysis.py`
from the frozen export's CSVs, after the export and outside the frozen code.
It adds no file to the frozen source set; the analysis-source digest stays
`3c3e772c66ecf51e`.

- Ladder: Qwen2.5-Coder 0.5B, 1.5B, 3B, 7B, 14B and 32B (registry sizes); x = log10(parameters).
- Reversion: per model, the share of Arm A rows with M < 0 in the rule condition
  (status ok), base and instruct models separately.
- H4: the AUROC of the risk score per base/instruct pair.
- Data: every lexicon of the held-out run; each grammar family separately, never pooled.
- Statistic: the OLS slope across the six sizes.
- Uncertainty: 95% percentile template-cluster bootstrap within the family, with the same
  template draw for every size; B = 2000, seed 20261002.
- Tests: two-sided bootstrap p, and Holm over all six slopes.

**Scientific consequence.** The analysis follows D10 wherever D10 is explicit.
The statistic, interval and multiplicity rule are the project's registered
defaults, applied to D10's question. It was written by the assistant and is
pending the investigator's review. Any change made after held-out outcomes are
seen would be post hoc and must be labelled so. Size is not randomized: within
the ladder the tokenizer and training recipe are fixed, but other differences
between sizes remain, so a trend is an association.

**Review.** Approved by the investigator on 2026-10-08, unchanged, before any
held-out outcome was examined.
