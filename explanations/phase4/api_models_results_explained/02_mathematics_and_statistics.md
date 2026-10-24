# 02 — Mathematics: how each number is computed, with worked examples

> The formulas are Phase 3.3's ([`../../phase3_3/heldout_results_explained/02_mathematics_and_statistics.md`](../../phase3_3/heldout_results_explained/02_mathematics_and_statistics.md));
> they are not re-derived here. This file works through **real numbers of this run**, and adds
> the arithmetic that is new for served models: margins built from two requests, ties, and the
> re-test. Every number below was computed from the run's files.

---

## 1. One margin from two requests

From [03 §10](03_code_and_pipeline.md#10-one-site-through-the-api): OLMo 3 7B Instruct,
`blk:d25s3:t000:T_CLASS_SIGIL:0`, correct `#`, familiar `.`.

The server returns, for each request, the log-probability of every prompt token given the ones
before it. The two token lists agree up to index 299 and differ at index 300 (`k` = 300):

$$
M \;=\; \sum_{j \ge k} \log p(a_j \mid a_{<j}) \;-\; \sum_{j \ge k} \log p(b_j \mid b_{<j})
\;=\; (-17.0033) - (-15.5814) \;=\; -1.4219
$$

Each candidate is one token here, so each sum has one term. Because both requests share the
first 300 tokens, the two terms are conditioned on the same context: this is Phase 3.3's
first-divergent-token margin, unchanged.

**What is new.** The two terms come from two requests. In Phase 3.3 they came from one forward
pass over the shared prefix, computed in fp32, so M was a difference of two exact logits. Here
each log-probability is `logit − logsumexp(all logits)`, computed by the server for its own
request:

$$
M = (z_a - \mathrm{LSE}_a) - (z_b - \mathrm{LSE}_b)
$$

When both requests are computed alike, LSE_a = LSE_b and M = z_a − z_b: a difference of two
rounded logits, on the bf16 grid (§4). When batching makes LSE_a ≠ LSE_b, M moves off the grid
by the difference (§5).

---

## 2. Reversion and the rule effect for one cell

**OLMo 3 7B Instruct, `dom`, lexicon `d25s3`, with the token table (`rule`):** 220 sites, 90 with
M < 0, and 1 tie (M = 0).

$$
\text{reversion} = \frac{\#\{M < 0\}}{n} = \frac{90}{220} = 0.4091
$$

The tie counts as not reverted (M < 0 is strict), as in Phase 3.3, which had no ties.

**The rule effect** pairs each site with itself without the table (`norule`):

| site | M(rule) | M(norule) | difference |
|---|---:|---:|---:|
| `t000:T_CLASS_SIGIL:0` | −0.4375 | +1.7812 | −2.2188 |
| `t002:T_VERB_MOVE:0` | −2.6250 | −2.5938 | −0.0312 |
| `t004:T_PSEUDO_SELECTED:0` | −7.5972 | −16.6223 | +9.0251 |

Over the 220 pairs the mean difference is **+1.0994 nats**: the table helped at 137 sites, hurt
at 80, and changed nothing at 3. Notice the first row: the table *moved this site from correct to
reverted*. A positive mean effect is a statement about the average, not about every site.

**Over all five lexicons of `dom`:** 627 of 1,515 sites reverted with the table, 0.4139; its 95%
template-cluster interval is [0.371, 0.455] (Table 2). The interval resamples the 80 templates, not the
1,515 sites, because sites of one template are not independent (Phase 3.3's `02 §2`).

---

## 3. Kaplan–Meier for one model: OLMo 3 7B Instruct, `dom`

The ladder scored 195 `dom` sites at 0, 1, 2, 4, 8, 16 and 32 worked examples.

- 105 were already correct at 0 examples (M ≥ 0) and leave the analysis.
- **90 were initially wrong**; 57 switched within 32 examples and 33 never did (censored at 32).

The switch point of one site, `dom:d75s3a:t000:T_CLASS_SIGIL:0`, margins at the seven rungs:

```
 rung:   0       1      2       4      8      16     32
 M:     −0.281  +3.312 −0.312  +0.250 +0.875 +1.000 +0.875
```

M first crosses zero between 0 and 1 example. Linear interpolation:

$$
k^* = 0 + \frac{0 - (-0.281)}{3.312 - (-0.281)} \times (1 - 0) = 0.078
$$

It falls back below zero at 2 examples (a "recrossing"), then holds from 4.

**The median.** No site is censored before 32 examples, so up to there the survival curve is
S(t) = 1 − (sites switched by t) / 90. The median is the first switch at which S ≤ 1/2:

```
 switch:    43       44       45                    46       47
 k*:        6.857    7.200    7.273                 9.436    9.455
 S:         0.5222   0.5111   0.5000000000000001    0.4889   0.4778
```

In exact arithmetic S = 45/90 = 1/2 at the 45th switch, so the median is 7.27. The pipeline
computes S as a product of floating-point factors, one per switch (1 − 1/n, with n the sites
still at risk), and gets 0.5000000000000001 after 45 of them, just above 1/2, so it moves on to
the 46th switch. The exported median is therefore **9.44 examples**
(95% interval 3.33–31.47, Table 4). The same rounding moves 6 of the 18 served medians and 14 of
Phase 3.3's 42 held-out medians to the next switch
([08 §6](08_issues_and_superseded_numbers.md#6-found-not-fixed-a-rounding-fault-in-the-kaplan-meier-median)).
Either way, OLMo 3 7B needs more examples than Phase 3.3's instruct models in `dom` (1.6–4.6).

---

## 4. Ties and the bf16 grid

A bf16 number has 8 significant bits. Near 16–32, consecutive bf16 values differ by 2^−3 = 1/8;
near 8–16, by 1/16; near 4–8, by 1/32. If both candidates are single tokens and LSE_a = LSE_b,

$$
M = z_a - z_b \in \tfrac{1}{8}\mathbb{Z} \text{ (or a finer grid, if the logits are smaller)}
$$

and M = 0 exactly whenever both logits round to the same value. In the cell of §2, one of 220
margins is an exact tie. Over the run: 778 ties in 81,810 Arm A margins, 0.95% (Table A1).
DeepSeek-V4.1-Flash, which does not round, has none.

**How much can rounding move a rate?** At most by the share of margins within one step of zero,
because only those can change sign. Table A1 gives the share within 1/8 nat for every model:
1.0–6.1% for the served models. For Phase 3.3's models, which did not round, the same share was
5.1% of all Arm A margins (4.6% for its ten instruct models). This bounds rounding only; the
variation between identical requests (§5) can move margins further.

---

## 5. The re-test: batching noise in numbers

For a fixed sample of sites (seed 20261023), the margin was computed again by the same
deployment, after the run. For each site, Δ = M_retest − M_run.

- **same to the bit:** Δ = 0;
- **sign changed:** M_run < 0 ≠ M_retest < 0, a site moving between reverted and not.

**Three re-scored sites of Qwen3.5 122B**, the least repeatable deployment:

| site | M_run | M_retest | Δ | |
|---|---:|---:|---:|---|
| `blk:d75s2a:t066:T_CLASS_SIGIL:3` | −1.249441 | −1.249441 | 0 | same to the bit |
| `blk:d50s3:t077:T_VERB_WIREFRAME:0` | −0.000700 | +0.948298 | +0.948997 | reverted → not reverted |
| `blk:d75s3a:t068:T_VERB_ROTATE:0` | 0 (a tie) | −0.122498 | −0.122498 | not reverted → reverted |

And Gemma 4's largest change, `blk:d75s3a:t078:T_VERB_RECOLOR:0`: −18.520540 → −29.209158,
Δ = −10.688618. It is far from zero, so the sign stays.

**From sites to a rate.** Qwen3.5 122B: 130 of its 300 sampled sites reverted in the run
(0.4333); on re-scoring, 10 moved to reverted and 10 away, so 130 again (0.4333). Gemma 4: 146
(0.4867); 9 to reverted and 5 away, so 150 (0.5000), a change of +4/300 = +1.33 points.

The expected change in a reversion *rate* from re-scoring every site is the difference between
the flips in each direction, divided by the number of sites, so it is at most the share of sites
whose sign changed.

---

## 6. Arm B for one model: Gemma 4 31B, `dom`

Gemma 4 wrote 390 `dom` programs: one per template with a decision site in the lexicon (80 in
`d75s1a`, `d75s2a` and `d75s3a`, 76 in `d50s3`, 74 in `d25s3`). Of these, 165 are exactly the
target program, 178 are valid programs that differ from it, 47 do not parse, and none is empty.

**A correct one** (`d25s3`, template `t000`):

```
 request:  Change the colour of objects of class 'wheel' to #111111.
 target:   (function(){ $S('#wheel')#recolor('#111111'); })();
 written:  (function(){ $S('#wheel')#recolor('#111111'); })();
           Request: Move meshes of class 'wheel' by (1, 2, 3).        <- it went on writing;
           Program: (function(){ $S('mesh#wheel')#duplicate(1, 2, 3); })();   the extractor keeps
           …                                                             only the first program
```

Its one decision site, the class sigil (`T_CLASS_SIGIL`): reached, and `#` written, the correct
spelling in this lexicon.

**A reversion** (`d25s3`, template `t002`):

```
 request:  Move meshes by (1, 2, 3).
 target:   (function(){ $S('mesh')#duplicate(1,2,3); })();
 written:  (function(){ $S('mesh')#move(1, 2, 3); })();
```

In this lexicon the verb for moving is spelled `duplicate`. Gemma 4 wrote the familiar `move`:
the site `T_VERB_MOVE` is reached and reverted, and the program is valid but wrong.

**The two numbers.** Over the 1,515 `dom` sites of the 390 programs, 820 were reached and 31 of
those reverted:

$$
\text{reach} = \frac{820}{1515} = 0.541, \qquad
\text{reversion given reach} = \frac{31}{820} = 0.038
$$

They are reported side by side and never multiplied: the product (0.020) would mix how far a
model gets with what it writes once there. Gemma 4 gets far and almost never reverts; OLMo 3 7B
Instruct (`blk`) reaches 14 sites and reverts at 10.

---

## 7. Formulas at a glance

| quantity | formula | here |
|---|---|---|
| margin | M = Σ_{j≥k} log p(a_j) − Σ_{j≥k} log p(b_j) | from two requests |
| reversion | #{M < 0} / n | a tie is not a reversion |
| rule effect | mean over lexicons of mean_site (M_rule − M_control) | as Phase 3.3 |
| interval | 95% percentile, template-cluster bootstrap, B = 2000, seed 20261002 | Phase 3.3's streams |
| `k*` | first upward crossing of 0, interpolated; censored at 32 | Kaplan–Meier median over initially wrong sites |
| reach, reversion given reach | reached / sites; reverted / reached | never multiplied |
| near zero | #{\|M\| < 1/8} / n | Table A1 |
| re-test change | Δ = M_retest − M_run; sign changed if (M_run < 0) ≠ (M_retest < 0) | Table A2 |
