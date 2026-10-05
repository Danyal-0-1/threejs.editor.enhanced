# 01 — Changes and results (rigorous)

The precise version of `00_results_in_plain_language.md`. Code lives in
`../phase3_2/`; this directory holds the reports and a snapshot of the data.

---

## 1. What was done in this round

Next-steps items 1–6 and 9 were closed in the previous revision. This round
closes the rest of what could be closed without a cluster.

| next-step item | status | where |
|---|---|---|
| 7 — preregister splits and criteria | **DONE** | `../phase3_2/PREREGISTRATION.md` |
| 8 — uncertainty by resampling templates/mappings | **DONE** | `analysis.cluster_bootstrap` |
| length-matched stratum re-analysis | **DONE** | `analysis.length_matched_strata` |
| prompt-paraphrase robustness | **DONE** | `prompts.paraphrase`, 3 framings |
| **extinction curves on real weights** | **DONE — first time** | `scripts/run_primary.py` |
| model-revision pinning + env capture | **DONE** | `runmeta.py` |
| Sol launch kit | **DONE** | `../phase3_2/sol/` |
| 10 — scale to larger checkpoints + 2nd tokenizer family | **NOT DONE** | needs Sol |
| power simulation | **NOT DONE** | stated as a known weakness in the prereg |
| Arm B, H4 linter on real scores, external DSL | **NOT DONE** | unchanged |

New code in `../phase3_2/src/phase3_2/`: `analysis.py` (223),
`runmeta.py` (101), plus additions to `prompts.py` (201) and
`sampling.py` (106); `scripts/run_primary.py` (176); `sol/` (129).

---

## 2. Results

### 2.1 Reversion with the specification present

Balanced sample, `d50s1`, 272 sites per family, 2,176 per-site rows.
Intervals: 95% percentile cluster bootstrap over **templates**, B = 2000.

| model | family | reversion | 95% CI | n templates |
|---|---|---:|---|---:|
| 0.5B base | dom | 0.412 | [0.367, 0.457] | 76 |
| 0.5B base | blk | 0.456 | [0.410, 0.505] | 76 |
| 0.5B instruct | dom | 0.445 | [0.400, 0.490] | 76 |
| 0.5B instruct | blk | 0.423 | [0.376, 0.466] | 76 |

Reversion is **0.41–0.46 with the full 28-role token table in context**, and
the families agree.

### 2.2 Rule effect — 3 of 4 intervals include zero

`rule effect = M_seq(rule) − M_seq(norule)`, paired within site.

| model | family | mean | 95% CI | excludes 0 | helped |
|---|---|---:|---|---|---:|
| 0.5B base | dom | +0.171 | [+0.029, +0.326] | **yes** | 55.1% |
| 0.5B base | blk | +0.156 | [−0.020, +0.344] | no | 52.6% |
| 0.5B instruct | dom | +0.199 | [−0.003, +0.414] | no | 53.7% |
| 0.5B instruct | blk | +0.222 | [−0.004, +0.465] | no | 59.2% |

A 28-role authoritative mapping moves the margin by ~0.2 nats and helps
barely more often than chance. This is the first result in the project that
bears on **rule-following** rather than prior strength — and it is only
possible because P32-002 (a rule prompt with no rule) was fixed.

### 2.3 Extinction threshold `k*` — the primary estimand, first real-model run

Ladder (0, 1, 2, 4, 8, 16, 32); 120 balanced sites (60/60 family,
40/40/40 stratum); examples are correct programs in the target lexicon.

| model | family | n | crossed | **k\* median** | 95% CI | censored |
|---|---|---:|---:|---:|---|---:|
| 0.5B base | dom | 60 | 36 | **6.64** | [4.35, 10.40] | 11 (18%) |
| 0.5B base | blk | 60 | 37 | **4.96** | [3.84, 6.72] | 9 (15%) |
| 0.5B instruct | dom | 60 | 39 | **6.94** | [5.97, 12.38] | 7 (12%) |
| 0.5B instruct | blk | 60 | 36 | **5.83** | [5.37, 7.06] | 5 (8%) |

About half of all sites are already correct at 0 shots (30–33 of 60), so `k*`
describes the sites that start wrong.

**Censored curves are retained, never dropped.** They are the strongest
priors; discarding them would bias `k*` downward exactly where the effect is
largest.

`blk` requires consistently fewer examples than `dom` (4.96/5.83 vs
6.64/6.94), consistent with `dom`'s higher token fertility — but the intervals
overlap and this is not a tested contrast.

### 2.4 Paraphrase robustness

Three framings (`p0` default, `p1` terse, `p2` verbose) carrying the identical
rendered table; 1,291 / 1,527 / 1,716 characters.

| model | family | p0 | p1 | p2 | range |
|---|---|---:|---:|---:|---:|
| 0.5B base | dom | 0.450 | 0.450 | 0.500 | 0.050 |
| 0.5B base | blk | 0.500 | 0.467 | 0.483 | 0.033 |
| 0.5B instruct | dom | 0.500 | 0.500 | 0.483 | 0.017 |
| 0.5B instruct | blk | 0.467 | 0.483 | 0.483 | 0.017 |

**The reversion rate is stable to within 5 points; the mean margin is not**
(it ranges −0.32 to +0.19 across framings). The binary outcome is the robust
statistic and is what gets reported.

### 2.5 Length-matched strata — the 3D question is not identifiable

Token-length signatures `(n_tok_correct / n_tok_competitor)`:

| stratum | signatures |
|---|---|
| sigil | **1/1: 1,208** — exclusively |
| verb | 2/2: 288 · 1/1: 160 |
| keyword | 1/1: 416 · 2/1: 56 · 1/2: 48 |

Only the `1/1` cell is comparable:

| family | sigil (n=151) | verb (n=20) | difference |
|---|---:|---:|---:|
| dom | 0.430 | 0.350 | +0.080 |
| blk | 0.444 | 0.450 | −0.006 |

The strata occupy nearly disjoint length signatures; where they overlap there
are 20 verb sites and the difference is inconsistent in sign.

**The earlier claim is withdrawn.** The 3D-knowledge contrast is **not
identifiable with the present materials**, and fixing it requires
constructing verb collisions with single-token candidates — a materials
change, not more data.

---

## 3. Measurement health

| | first run | after all fixes |
|---|---:|---:|
| exact-zero margins | 106/240 (44.2%) | **3 / 2,176** (0.14%) |
| families scored | 1 of 2 | **2 of 2** |
| per-site rows saved | 0 | **2,176** + 720 paraphrase + 240 curves |
| intervals | none | cluster bootstrap on every headline |
| model revision pinned | no | **yes** (`runmeta.pin`) |
| prompt contains the rule | **no** | yes, rendered from φ |

Residual exact zeros are printed by site id every run; all three are
single-token sigil pairs receiving identical log-probs to float precision.

---

## 4. Honest limits

- **One lexicon** (`d50s1`), **one model family** (Qwen2.5-Coder), **one size**
  (0.5B) for the primary estimand.
- **No power analysis.** Declared in the preregistration: a null from the next
  run will be reported as underpowered unless a simulation is run first.
- **Rule-effect intervals include zero** in 3 of 4 cells.
- **The 3D question is unidentifiable** with these materials.
- Extinction used 120 sites, not the full 3,326 — a 0.5B model OOMed at the
  32-shot rung on a 16 GB card.
- `blk` vs `dom` `k*` differences are **not** a tested contrast; intervals
  overlap.
