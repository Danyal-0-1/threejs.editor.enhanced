# 02 — Theory and mathematics behind the new results

> ⚠️ **ERRATUM (2026-10-05) — read [`ERRATA.md`](ERRATA.md) first.** The `k*` ≈ 5–7 result below is **withdrawn** (82/120 sites saw their own target program among the demonstrations, plus two definition errors), and the rule-effect intervals are **corrected** (all four now include zero). `blk` is not a clean held-out grammar family.


> Full definitions live in `../phase3/phase3_explained/02_*` and
> `../phase3_2/phase3_2_explained/02_*`. This covers only what the new
> analyses require.

---

## 1. The extinction threshold `k*` — and why it is primary

Score `M_seq` at each rung of the ladder and take the first upward zero
crossing, interpolated:

$$k^\star = k_{j-1} + \frac{0 - M_{j-1}}{M_j - M_{j-1}}\,(k_j - k_{j-1})$$

- **Symbols.** `k_j` the shot count at rung `j`; `M_j` the margin there.
- **Expected value.** `k* ≥ 0`. Larger = a more stubborn prior.
- **Interpretation.** "This collision costs about `k*` worked examples."
  Directly actionable for a DSL designer in a way a log-odds is not.
- **Assumption.** Monotonicity between the bracketing rungs. The ladder is
  geometric, so the interpolation is coarse at the top — a crossing between
  16 and 32 is located only to within a few examples.
- **Implementation mistake to avoid.** Snapping to the rung instead of
  interpolating. The ladder is geometric, so snapping quantises `k*` into
  buckets whose width grows with `k`, inventing ties between distant sites.

### Why a threshold, not an interaction

An *ordinal* interaction measured on a monotonically transformed scale is
partly a property of the scale. Two factors that both push the same direction
generically produce "super-additivity" under a compressive nonlinearity, and
the same data can show the effect on one scale and not another.

`k*` is read off the **x-axis**. Rescaling the y-axis monotonically cannot
move where a curve crosses zero. That invariance is the whole reason it is
the declared primary endpoint.

### Censoring

A curve still negative at the top rung has `k_star = None` and `censored =
True`. These are **retained**.

$$\text{Dropping censored sites biases } \hat{k}^\star \text{ downward,}$$

because the dropped sites are exactly the ones with the largest `k*`. Measured
censoring here is 8–18%, reported beside every median. A proper treatment uses
survival methods (Kaplan–Meier median) rather than the median of the crossers;
that is not yet implemented and the current figure is therefore a **median
among crossers**, which is an underestimate.

---

## 2. The rule effect

$$\text{rule effect}_i = M^{\text{seq}}_i(\text{rule}) - M^{\text{seq}}_i(\text{norule})$$

- **Expected sign.** Positive — supplying the mapping should help.
- **Interpretation.** Nats bought by the authoritative table at this site.
- **Assumption.** The two prompts differ *only* in the mapping. They match on
  line count (36 = 36) but not on length (1,527 vs 1,014 chars), so a residual
  context-length effect cannot be excluded and is reported with every result.
- **Measured.** +0.156 to +0.222 nats; **3 of 4 intervals include zero**.

In odds terms, +0.2 nats is a factor of `e^0.2 ≈ 1.22` — a 22% shift in
relative odds, against a prior that is often several times stronger.

---

## 3. The cluster bootstrap

For a statistic `T` over rows nested in clusters `c = 1…C`:

1. draw `C` clusters **with replacement**;
2. take **all** rows of each drawn cluster;
3. recompute `T`;
4. repeat `B = 2000` times; report the 2.5th and 97.5th percentiles.

- **Unit.** `template` (80 of them). Sites are **not** independent: they are
  nested in templates, and 36.4% share a prefix with another site.
- **Why it matters quantitatively.** Ignoring clustering inflates the
  effective sample size by roughly the average cluster size — here about
  `2176 / 76 ≈ 29` rows per template — so naive intervals would be too narrow
  by a factor of order `√29 ≈ 5`.
- **Refusal rule.** With fewer than 8 clusters the percentile bootstrap is
  unreliable, so `cluster_bootstrap` returns `None`. With one lexicon, a
  lexicon-level bootstrap correctly returns nothing rather than a number.
- **Family is fixed, not random.** Two levels cannot estimate a variance, so
  every statistic is computed **within** a family.

---

## 4. Length matching as confound control

The stratum contrast asks whether reversion differs between sites needing no
domain knowledge (`sigil`) and sites that do (`verb`). But candidate token
length differs too, so the raw contrast estimates

$$\text{(domain effect)} + \text{(length effect)}$$

with no way to separate them. Restricting to a fixed length signature
`(n_tok_correct, n_tok_competitor)` removes the second term **by design**
rather than by adjustment.

**Measured identifiability.** `sigil` is exclusively `1/1`; `verb` is mostly
`2/2`. Overlap exists only at `1/1`, with 151 sigil against 20 verb sites.

A contrast is **identifiable** only where both groups occupy the same stratum
of the confounder. Here they barely do, so the quantity is not estimable from
these materials — and no increase in n fixes it. The fix is to construct verb
collisions with single-token candidates.

---

## 5. Why the reversion rate is more robust than the mean margin

Across three prompt paraphrases:

| statistic | spread |
|---|---|
| reversion rate `P(M < 0)` | 0.017 – 0.050 |
| mean `M_seq` | −0.32 to +0.19 |

The rate depends only on the **sign** of `M`, so it is invariant to any
monotone rescaling of the margin and is insensitive to a few extreme sites.
The mean is not: a handful of sites with very large `|M|` dominate it, and
which sites those are changes with the prompt.

This is the same invariance argument that makes `k*` primary, applied to the
outcome rather than the x-axis. **Report the rate; treat the mean as a
diagnostic.**
