# 05 — Knowledge check (Phase 3.3)

No answers here. **[R]** = run something. **[†]** = judgment call.

## Extinction and the primary estimand

1. Write the `k*` interpolation formula. Why interpolate rather than snap to a
   rung, given the ladder is geometric?
2. `k*` is primary and the A×T interaction is not. Give the invariance
   argument in two sentences.
3. 18% of `dom` curves never crossed at 32 shots. What is `k_star` for those,
   and what happens to the median if you drop them? Which direction is the
   bias?
4. The reported `k*` is a **median among crossers**. Why is that an
   underestimate, and what should replace it?
5. About half of sites are already correct at 0 shots. What does `k*`
   therefore describe, and how should that be worded in a paper?
6. **[R]** Load `outputs_snapshot/primary.json`. Recompute median `k*` for
   `blk`, 0.5B base, counting censored sites as `k* = 32`. Compare to 4.96.
   Which is more honest?

## Rule effect

7. Define the rule effect. Why could it not be measured at all before P32-002
   was fixed?
8. Three of four intervals include zero. State that result for an abstract
   without overclaiming in either direction.
9. The two prompts match on line count but not length (1,527 vs 1,014). What
   confound remains, and how would you remove it?
10. +0.2 nats — express that as a change in odds. Is it large?

## Uncertainty

11. Why resample templates and not sites? Estimate how wrong a site-level
    interval would be, using the rows-per-template figure.
12. `cluster_bootstrap` returns `None` below 8 clusters. Defend that choice
    against "just report it with a caveat."
13. Why is family a fixed factor rather than a random effect?

## The withdrawn conclusion

14. Sigil sites are exclusively `1/1`; verb sites are mostly `2/2`. Explain
    why this makes the 3D contrast *unidentifiable* rather than merely noisy.
15. At the one overlapping signature there are 151 sigil and 20 verb sites,
    with differences +0.080 and −0.006. What can you conclude?
16. **[†]** Design the materials change that would make the 3D question
    answerable. What would you have to build, and what would it cost?
17. Both defects that produced the withdrawn conclusion pushed toward a
    *cleaner* story. Why is that the dangerous direction?

## Robustness and readiness

18. Reversion moves ≤0.05 across paraphrases; mean `M_seq` moves from −0.32 to
    +0.19. Explain both facts with one property of the statistics.
19. **[R]** Render `p0`, `p1`, `p2`. Which differ in register, and which in
    length? What does that make them a test of?
20. Name three things in `runmeta.capture()` that would let you detect a
    result you could not reproduce.
21. The prereg says a null will be reported as underpowered. Why is saying so
    *in advance* different from saying it afterwards?
22. **[†]** The gate is "effect present in `blk` with an interval excluding
    the null." Current `blk` reversion is 0.423–0.456 with tight intervals.
    Does that pass the gate? Defend your answer against the prereg's wording.
