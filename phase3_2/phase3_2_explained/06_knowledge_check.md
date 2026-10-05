# 06 — Knowledge check (Phase 3.2)

**No answers in this file.** Work them out against the code, then check.
**[R]** = run something. **[†]** = judgment call with no settled answer here.

> Phase 3's 50 questions still apply. These 40 cover what is new.

---

## A. Grammar families

1. State the exact difference between a *lexicon* and a *grammar family*. Why
   are `alpha/beta/gamma/delta` not four families? Name the invariant and the
   file that enforces it.
2. List four structural differences between `dom` and `blk`. Which three
   terminals does `blk` not use at all?
3. `blk` reuses the **vendored** inner selector parser rather than
   reimplementing it. Give the scientific reason, not the engineering one.
4. Why must `blk` use the *frozen terminal table* rather than inventing new
   terminals? What would break in the cross-family comparison otherwise?
5. `program : block*` not `block+`. Which Phase 1 program forces this, what is
   its canonical IR, and what would silently go wrong with `+`?
6. **[R]** Render template `t000` in both families under `d50s1`. Report both
   prefixes, both `char_offset`s, and both IR hash pairs. Why are the hashes
   identical and the prefixes not — and why is that the whole point?
7. **[†]** `blk` shares the inner selector language with `dom`. Argue that
   this makes the cross-family test *weaker* (too much is shared). Then argue
   it makes it *stronger*. Which do you believe?

---

## B. The delta family

8. Name the three Phase 3 gaps the family closes, and say which parameter
   closes each.
9. The density ceiling is 79%. What are the remaining 21%, and which invariant
   locks them?
10. Give the concrete reason not to run the primary arms at maximum density.
    Which hypothesis becomes untestable, and why exactly?
11. Why can `strict` mode only reach ~0.45 density? Compute it from
    `C.SIGNATURES`.
12. In `arity` mode, swapping `recolor` with `setOpacity` produces
    `{"opacity": "#111111"}`. Is that still a valid SEMANTIC collision? Defend
    your answer, then say what you would report in the methods section.
13. `Member.density_actual` is 0.45 but the census says ~0.36. Explain the gap
    without looking it up.
14. How does the rotation seed supply held-out mappings? Describe a concrete
    train/test split over the nine members, and say what it does **not**
    control for.
15. **[R]** Build `(0.50, 1)` twice and `(0.50, 2)` once. Show that the first
    two are identical and the third is not. Why does each property matter?

---

## C. P32-001 — the defect

16. State the defect in one sentence, then write the three lines of code that
    caused it.
17. Why does `tok(prefix + c)` fail to extend `tok(prefix)`? Name the
    tokenisation algorithm and the property responsible.
18. For the class-sigil site: give the three token sequences, their lengths,
    and the last token id of each. What was `M_seq`?
19. Why is the bias **one-way**? Prove that the defect can never *overstate*
    reversion.
20. Sigil reversion went 0.106 → 0.515; verb reversion did not move at all.
    Explain both facts with one mechanism.
21. Write the corrected margin formula. Explain precisely why the shared
    prefix cancels.
22. Why must `k` be a **token** index and not a character index? Give the
    concrete token that makes a character index wrong.
23. `_score_from` forces `k ≥ 1`. Why can the first token never be scored?
24. **[R]** Run `run_arm_a.py` on any checkpoint. Report the merged count and
    the post-fix exact-zero count. What would a nonzero post-fix count mean?
25. **[†]** `phase3.scoring.forced_prefix_margin` is still importable and
    still defective for real models. Should Phase 3.2 have patched it in
    place, like P3-001? Argue both sides.

---

## D. Fertility and materials

26. Phase 3 claimed 1.0078; the measurement says 1.077 for `dom`. What was
    measured in each case, and why does the proxy fail?
27. `blk` fertility is 1.003–1.009 while `dom` is 1.072–1.078, with the
    **same** lexicons. Give the proposed mechanism. Is it measured or
    hypothesised?
28. Which family is the fertility-controlled arm, and what must be re-checked
    before relying on that?
29. Phase 1 has 3 distinct first-site openings at k=17 but 33 at k=24. Which
    is the right width and why? What Phase 3 number does the 3 correspond to?
30. Phase 3.2's `dom` corpus has **1** first-site opening — worse than Phase
    1's 3. Why is that not a regression, and what does it prove about template
    variety?
31. Prefix collisions fell from 61% to 36.4% but did not vanish. Why can they
    not be eliminated, and what must every analysis do about it?

---

## E. Strata and the 3D question

32. Why do sigil sites require no 3D knowledge while verb sites do? Give an
    example of each decision.
33. Domain knowledge affects `P(O)` much more than `P(Y|O)`. Explain why, and
    say which arm is therefore immune.
34. The measured result is sigil ≥ verb at all six checkpoints. State the
    conclusion in one sentence, then state two reasons it is not yet a
    finding.
35. **[†]** Sigil candidates are single characters; verb candidates are words.
    Design the sub-analysis that removes this confound. What would it cost?

---

## F. Interpretation

36. Instruct reverts less than base at every size, but never near zero. What
    does that support, and what does it rule out?
37. A reviewer says 3,326 prefix-distinct sites are not 3,326 independent
    observations. They are right. What is the correct unit, and roughly how
    many are there?
38. Cross-family transfer gives AUROC 0.81 within `dom` and 0.54 `dom`→`blk`.
    What do you conclude about H4, and what do you publish?
39. **[†]** Every Phase 3.2 real-model number is a point estimate with no
    interval, n=240, one model family, one prompt. Write the two sentences you
    would put in a paper describing them honestly.

---

## G. Status

40. Of the 15 required components, which remain **not implemented** after
    Phase 3.2? Name them without looking, then check `03 §6`. Which two did
    Phase 3.2 close?
41. Two reproducibility checks are still **blocked or partial**. Which, and
    what do they have in common?
42. Phase 3.2 writes files into Phase 3's tree. Which files, why is it
    necessary, and why will `vendor_sync.py --check` not catch it?
43. Name three constants in the audit labelled "apparently arbitrary" that
    could change a **scientific** conclusion, as opposed to fixture-only ones.
44. **[†]** What is the single biggest reason Phase 3.2 is still not ready for
    a full Sol run? Give the number that supports your answer.

---

## H. Revision 2 — the three self-inflicted defects

45. The first Arm A run reported "both families." Show from `collect_sites`
    and `[:limit]` why it scored only `dom`. Why is a first-*N* slice over a
    concatenated list never a sample?
46. Of the two families, the dropped one was `blk`. Why does *which* family
    was dropped make the defect worse than a coverage gap?
47. The original `RULE` string said "follow the token table exactly." What was
    missing, and why does that change what `M_seq` measures — not just its
    value?
48. Why must `rule_prompt` be rendered **from** the φ-map rather than written
    out? Describe the failure mode of a hand-written table.
49. The `norule` control keeps the role list and the line count but removes
    the spellings. Give two reasons a bare prompt would be a worse control,
    and name the residual mismatch that remains.
50. **[R]** Render both prompts for `d50s1`. Report both lengths. What
    confound does the difference leave open, and where is it reported?
51. Define the rule effect. Measured: mean ≈ +0.2 nats, helping 52.6–59.2% of
    sites. State that result in one sentence for a paper abstract.
52. Reversion stays at 0.42–0.46 **with** the full table in context. Which
    prior finding does this reproduce, and at what level of analysis?
53. `blk` ≈ `dom` on reversion. Why could that not have been known from the
    first run, and what confound does it now rule out?
54. The "sigil ≥ verb" conclusion was withdrawn. Give the two defects that
    produced it, and explain why both pushed toward a *cleaner* story rather
    than a messier one.
55. **[†]** Sigil candidates are single characters; verb candidates are words.
    Design the length-matched sub-analysis. What is the smallest version that
    would change your mind about the 3D question?
56. 3 of 2,176 margins are still exactly zero, all single-token sigil pairs,
    `merged` sometimes False. What are the possible causes, and should they be
    excluded or reported?
57. **[R]** Load `outputs/arm_a_balanced.json`. Recompute the dom/blk
    reversion rates for the rule condition from `rows`. Why does the ability
    to do this at all count as a fix?
58. **[†]** Items 7, 8 and 10 of the next-steps list are still open. Which one
    would you do first, and what would you refuse to run until it is done?
