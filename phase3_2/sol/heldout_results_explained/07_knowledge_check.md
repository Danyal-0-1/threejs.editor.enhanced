# 07 — Knowledge check: the held-out results

No answers are given. Each section names where its answers can be found.

- ✎ means pen and paper.
- ⌨ means run something on the local copy (`phase3_3/sol_results/heldout-20261007a/`).

---

## A. Confirmatory logic (`01 §1`, `03 §4–5`)

1. What exactly did the freeze fix? Name four things. Which held-out command re-checks them,
   and how often?
2. Why does `p33.py status` on the held-out run fail on your laptop but work on Sol? What does
   that protect against?
3. D11 was written *after* the freeze. Why can it still be called pre-specified? What evidence
   would a reviewer ask for?
4. The unlock phrase was entered by the assistant at your direction. Where is that recorded,
   and why does it matter?

## B. H4 (`00 §3`, `02 §1`)

5. ✎ For Qwen2.5-Coder-32B on `dom`: n₁ = 606, n₀ = 909, R₁ = 616,963. Compute the AUROC.
   Why does the identity baseline have an AUROC of exactly 0.5?
6. ✎ Both C1 and C2 have bootstrap p = 1/2001. What is each Holm-adjusted p? Why is 0.0009995 a
   floor, not a measurement?
7. What would the within-lexicon AUROC look like if the score only separated *lexicons*? What
   does it actually look like?
8. In 4 of the 20 groups, the site-level score does *not* significantly beat the role-level
   baseline (the interval includes 0). Which models are they? What might make site-level
   information add little there?
9. ⌨ Find the three highest-risk sites for the 32B `dom` pair in `csv/h4_predictions.csv`. What
   is their stratum and label?

## C. Reversion and the rule effect (`00 §4–5`, `02 §2`)

10. ✎ The mean rule effect is about +0.35 nats. By what factor does it change the odds? Why
    does reversion fall by only 5–6 points?
11. Which model has *higher* reversion with the table than without, in one family? Propose
    two explanations, and say how you would test each.
12. Why does the length-matched control matter? What result would have undermined the rule
    effect?

## D. Adaptation (`00 §6`, `02 §3`, `01 §6–7`)

13. ✎ Build the Kaplan–Meier curve for 5 sites: switches at 0.4, 1.2 and 2.0, and two sites
    censored at 32. What is the median? What is the "median among crossers"?
14. Explain the difference between `k*` (median ≈ 2) and `sustained_k` (median ≈ 8) to someone
    who has never seen an extinction curve.
15. Why is `k*` sometimes below 1? Give the interpolation for a site with M = −0.1 at k = 0 and
    M = +2.0 at k = 1.
16. Non-informative censoring is an assumption of KM. Why is it doubtful here, and how should
    that change the wording of the result?

## E. Scale (`00 §7`, `02 §4`, `01 §12`)

17. ✎ Recompute the D11 slope for H4 AUROC in `dom` from the six values. Which single point
    would change it most if removed?
18. Why is "no trend survives Holm" not the same as "there is no effect of scale"?
19. Why is the 72B model excluded from D11, even though it was run?

## F. Generation (`00 §8`, `02 §5`, `01 §10`)

20. ✎ 0.5B-Instruct on `dom`: 44 of 1,515 sites reached, 10 reverted. Compute reach, reversion
    given reach and the product. Why is the product misleading?
21. What does "reach" require, exactly? Name one correct program that would *not* reach.
22. ⌨ In `csv/arm_b_generations.csv`, find a PARSE_FAIL whose `extracted` text contains
    "Request:". What went wrong, and how many such rows are there?

## G. Repair (`00 §9`, `02 §6`, `01 §11`)

23. ✎ In the worked cell, reversions go from 90 to 49 with 3 roles changed. Compute the
    per-symbol reduction. How much of it came from the repaired sites?
24. Explain, with the `d50s1` table from the one-file overview, why respelling one keyword
    leaves a reversion *silent*.
25. Why does the global arm reach zero silent errors? What does that cost?
26. Design a targeted rule that might beat random. What would you have to preregister before
    testing it?

## H. Interpretation and the paper (`06`)

27. Write the one-sentence contribution for each of: H4, scale, adaptation, repair.
28. List three claims you must *not* make, and the evidence that forbids each.
29. A reviewer says "this is one toy DSL". Write your two-sentence reply.
30. Which three gaps in the frozen analysis does deviation D12 record? Which numbers do they
    affect, and which do they not?
