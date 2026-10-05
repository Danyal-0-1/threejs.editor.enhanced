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
