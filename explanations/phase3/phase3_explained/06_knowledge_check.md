# 06 — Knowledge check

**No answers in this file.** That is deliberate. Work them out, then check
against the code and the other documents — and where a question asks you to
*run* something, run it.

Questions marked **[R]** require running code. Questions marked **[†]** have
no settled answer in the repository; they are judgment calls you will have to
defend to a reviewer.

---

## A. Theory

1. The original hypothesis said LLMs succeed at DSLs "mainly because" of
   pretraining familiarity. Give **three** distinct reasons that sentence
   cannot be tested as written. For each, say what you would have to add.

2. PLSemanticsBench already shows models lean on priors rather than supplied
   semantics. State precisely what Phase 3 can still claim that it does not
   preempt — in one sentence, with no hedging words.

3. Why is "pretrained association" preferred over "corpus frequency"? What
   specific question could a reviewer ask that the second phrasing invites and
   the first does not?

4. A colleague says: "gamma had the highest ΔNLL, so it is the strongest test
   of surface familiarity." Give the measured reason this is wrong.

5. Explain why `delta` is a better experimental material than `alpha`, naming
   the specific confound it removes **and** the mechanism by which it removes
   it. Then state the one claim about `delta` that is currently **unverified**.

6. Phase 3 deliberately puts H4 before H2. Give the argument. Then give the
   strongest argument *against* that ordering.

7. **[†]** `delta` keeps the `{T_CHAIN_OP, T_CLASS_SIGIL}` overload group, so
   the chain-op site stays LEXICAL. Argue both sides of de-overloading, and
   say what you would actually do.

---

## B. Experimental design

8. Experiment 02 reported `3/3` bare vs `15/20` scaffolded reversions and
   concluded scaffolding increased reversion. Compute `P(O)` and `P(Y|O)` for
   both conditions. What is the correct conclusion, and why is it the
   opposite?

9. A reviewer says the T×A design is a randomised factorial experiment.
   Explain why that is false for one of the two factors, and what the honest
   description is.

10. You want an A-level manipulation. You write a "low activation" prefix that
    is simply more unusual overall. What manipulation check fails, and why
    does the design collapse without it?

11. Why can grammar **not** be a random effect with 2–3 families? What is it
    instead, and roughly how many families would you need?

12. Phase 3 has 103 semantic sites but reports `n = 40`. Explain the gap. Then
    say what it implies for (a) the bootstrap and (b) the maximum achievable
    AUROC.

13. **[†]** Design a falsification test for H4 that cannot be satisfied by a
    predictor that has merely learned "this lexicon is delta." Name the
    baseline it must beat and by what margin you would find convincing.

---

## C. Mathematics

14. Write `M_seq` in full, including the summation over tokens. State the
    expected sign for a reversion and explain in words what `M_seq = −2.3`
    means in odds.

15. `M_seq` and `G_tok` are different quantities with **opposite** sign
    conventions. When do they coincide? Why does Phase 3 use `M_seq`?

16. Show algebraically that the naive activation score
    `A_i = [log P(q|r,x) − log P(c|r,x)] − T_i` equals `−M_seq − T_i`.
    Explain, in one sentence, why using it to predict reversion is circular.

17. Compute the DiD on the **margin** scale:
    strong/high −1.4, strong/low +0.3, neutral/high +0.5, neutral/low +1.0.
    Then suppose every strong-cell observation has `M_seq < 0` and every
    neutral-cell observation has `M_seq > 0`. Compute the DiD on the
    **probability** scale. What does the disagreement tell you, and what does
    `interaction_did` do about it?

18. Given shots `(0,1,2,4,8)` and margins `(−3.0, −2.5, −1.5, −0.5, +1.5)`,
    compute `k*` by hand. Show the interpolation.

19. A site's curve is still negative at 128 shots. What is `k_star`? What is
    `censored`? Why is dropping this site from the median a **bias** and not
    just a loss of data — and in which direction?

20. `linter.auroc` returns `None` when one class is absent. Why is that better
    than returning 0.5? Construct a case where returning 0.5 would mislead.

21. Why must the shared suffix (or EOS) be handled carefully when scoring
    multi-token candidates? Give a concrete pair from `delta` where it matters.

---

## D. Data structures and pipeline

22. List the eight fields of `sites.Site` that determine whether a site is
    usable, and say what each contributes.

23. `Site.ir_hash_competitor` is `None`. Which collision class is this, what
    happened, and is the site usable?

24. Trace the **exact** call order from a 3DOM program to a `RiskScore`. Name
    every file and function. (This is the path you retype.)

25. Why does `sites.classify` locate sites via `transpiler.lex` rather than
    `str.find`? Give the specific string in the corpus that breaks the naive
    approach, and name the test that guards it.

26. `canonicalize.content_hash` excludes `source` (rule C7). What would break
    if it did not? Relate your answer to why the study would become circular.

27. `outcomes.observe_site` does **not** require the whole program to parse,
    but `outcomes.evaluate` does. Why the asymmetry? What combination of
    fields will look like a bug but is not?

28. **[R]** Run the end-to-end snippet in `03 §4`. Report `char_offset`,
    `collision`, `competitor_binds_to`, and both IR hashes. Why does
    `competitor_binds_to` matter scientifically?

---

## E. Debugging

29. Someone ranks sites by `m_seq` descending in the linter. What AUROC do you
    expect relative to the truth? Why is this near-invisible when the true
    AUROC is ~0.5, and dangerous when it is ~0.9? Which test catches it?

30. A new φ-map passes `validate_phi` but `verify_repair` reports IR changes
    on 12 of 62 programs. Name two mechanisms that could cause this. Which
    layer should have caught it?

31. **[R]** `test_margin_is_zero_without_bias_at_matched_token_length` asserts
    `|m_seq| < 1e-12`. Set `FakeLM.noise = 0.35` and predict whether it still
    passes. Run it. Explain.

32. During development, `test_margin_sign_negative_when_competitor_preferred`
    failed with `m_seq = +0.1665` even though a bias was planted. The cause
    was a property of `delta` itself. What was it, and what does it tell you
    about priors in permutation lexicons?

33. A results table shows `reversion rate = 0.75` for one condition and `0.15`
    for another. What is the **first** question you ask before interpreting
    it, and which object in the codebase was designed to make that question
    unavoidable?

34. `vendor_sync.py` is re-run to pick up an upstream fix. What silently
    breaks, and which test fires? Why was that test written to inspect the
    file's **text**?

---

## F. Interpretation

35. H4 returns AUROC 0.82 for the site score, 0.79 for `length_baseline`, and
    0.81 for `identity_baseline`. Is H4 supported? What have you actually
    built?

36. The DiD is strongly negative on the margin scale, exactly zero on the
    probability scale, and positive on the logit scale. What does
    `interaction_did` report? What do you write in the paper?

37. Median `k*` is 3.2 at low-prior sites and 41.0 at high-prior sites, with
    28% of high-prior curves censored. State the finding in one sentence a DSL
    designer could act on. Then state the caveat the censoring forces.

38. A repair reduces reversion by 40% but changes 25 of 29 substitutable
    spellings. Why is this a weak result? What would a strong one look like?

39. **[†]** Every effect replicates on held-out mappings but vanishes on a new
    grammar family. What do you conclude, and what do you publish?

40. Arm A shows strong reversion; Arm B shows almost none, because most
    generations never reach the site. Are these contradictory? What do you
    report, and which is the ecological claim?

---

## G. What would falsify this?

41. State a concrete, numerical result that would falsify **H4**.
42. State one that would falsify **H2** but leave H4 intact.
43. State one that would make the mechanistic phase **not worth running**.
44. State a result that would show `delta` is a bad experimental material,
    even if H4 and H2 both "worked".
45. **[†]** State a result that would make you abandon the surface-collision
    framing entirely and say so in print.

---

## H. Status (checks you should be able to make unaided)

46. Of the brief's 15 required components, which are **not implemented**? List
    them without looking, then check `03 §5`.

47. Three of the ten reproducibility checks are reported as **CANNOT RUN**.
    Which three, and what do they have in common?

48. Name three constants in the audit (`04 §9`) labelled "apparently
    arbitrary" that could **change a scientific conclusion** — as opposed to
    those that are fixture-only. Defend each.

49. The README claims `delta` has a character-length ratio of 1.0078 and
    reasons about fertility. What is the gap, and what command closes it?

50. **[†]** What is the single biggest reason Phase 3 is not yet ready to
    consume A100 time? Give the number that supports your answer.
