# 09 — The conclusion, how strong each claim is, and where to submit

> Written 2026-10-09, after the held-out run, the paper figures and three new exploratory checks.
>
> - Every number comes from [00](00_complete_results.md), the paper tables
>   (`analysis_addenda/paper_figures/tables/`) or the exploratory report
>   (`analysis_addenda/exploratory/EXPLORATORY_CHECKS.md`).
> - **Exploratory** marks anything not preregistered.
> - Venue dates were checked on the web on 2026-10-09 (sources at the end). Recheck them before
>   you plan around them.

---

## 0. Bottom line

**The best conclusion, in one sentence:**

> Code language models treat a redefined DSL as a small edit of the languages they already
> know. With the full redefinition in the prompt, they still fall back to the familiar
> spelling at about half of the places where it matters, at every size from 0.5B to 72B. An
> instruction-tuned model falls back **where its own base model leans the old way**.

**Are the claims strong enough?**

- **Yes, for a rigorous evaluation paper**, if it is scoped honestly as one DSL, permuted
  spellings and open models. Its confirmatory core is unusually clean: preregistered,
  frozen with code-hash enforcement, tested once on held-out mappings and models, and met in
  20 of 20 groups.
- **The main risk is not the evidence. It is the "so what?" question.** "Models prefer
  familiar code" is known (§6). What is new, and must be the headline:
  1. **Site by site, the tuned model's failures are predictable from its own base model.**
     This is confirmatory, and the new exploratory check shows that much of it is
     lineage-specific inheritance, not shared difficulty.
  2. **The table and examples help only partly and unstably, and scale does not help.**
  3. **The failure is silent by construction in permuted languages**, and only a complete
     respelling into unfamiliar spellings removes the silent errors. That is DSL-design
     guidance.

---

## 1. The conclusion paragraph (abstract-ready, conservative)

> Across 21 open checkpoints (0.5B–72B, four model families) and five unseen remappings of a
> 3D-scene DSL, code language models chose the familiar spelling over the redefined one at
> 40–56% of designed collision sites, even with the full token table in context. The table
> moved every model toward the new spelling (+0.16 to +0.62 nats), but reversion did not
> fall with scale. A few leak-free worked examples flipped most sites: among sites that
> switched, the median was about two examples, but a switch that lasted took about eight, and
> 18% of initially wrong sites never switched within 32. In a preregistered held-out test,
> each instruction-tuned model's reversions were predictable from its base model's margins at
> the same sites (AUROC 0.76–0.96, all 20 pair × grammar groups), beyond length and identity
> baselines and, in most groups, beyond role-level difficulty. In free generation, about one
> in five reached sites reverted. Respelling only the predicted-riskiest symbols was no
> better than respelling random ones. Respelling every reassigned symbol into an unfamiliar
> alphabet cut reversion at the repaired sites from 48% to 16% and left no silent errors.

**Recommended title:** *Inherited Habits: Code Language Models Fall Back to Familiar Syntax
Where Their Base Models Lean — A Preregistered Study of Redefined DSLs from 0.5B to 72B.*
Alternatives are in [06 §5](06_publishability_and_paper.md).

---

## 2. Claim by claim: how strong, the main attack, the defence

**Strength scale:**

- **Strong**: confirmatory, or overwhelming descriptive evidence.
- **Moderate**: solid but limited in scope.
- **Suggestive**: exploratory only.
- **Not supported**.

| # | claim (as you may write it) | evidence | strength | the reviewer's attack | your defence |
|---|---|---|---|---|---|
| A | An instruct model's reversions are predictable, site by site, from its base model | preregistered H4: C1 and C2 met in 20/20; AUROC 0.76–0.96; within-lexicon AUROC 0.76–0.96; Δ vs role-level > 0 in 20/20 (CI > 0 in 16) | **Strong** | "Trivial: it is fine-tuned from the base" | It holds *with the rules in context*, where tuning should help most. And see A′ |
| A′ | …and much of the prediction is **inherited** from the model's own base, not just "some sites are hard for everyone" | own base beats a consensus of other-lineage bases in **20/20** groups, by +0.12 to +0.35 AUROC, all intervals > 0; the consensus reaches only 46% (median) of the own base's signal (§3.1) | **Moderate** (exploratory) | "Post hoc" | Say so; it uses only data that already existed; it is the obvious control a reviewer asks for |
| B | Reversion persists with the table and does not fall with scale | 21 checkpoints: 0.400–0.558 with the table vs 0.461–0.655 without; the table lowers it in 41/42; D11 reversion slopes all non-significant | **Strong** for *these* sites | "Your 50% depends on how you built the sites" | Yes: every site is a designed **collision**. Claim the *relative* findings (table, scale), not a general error rate |
| B′ | Scale does not fix it | D11: instruct slope per tenfold size −0.014 [−0.044, +0.017] (dom) and −0.013 [−0.044, +0.017] (blk) | **Moderate** | "One family; sizes not randomized" | The intervals rule out a fall of more than ~4.4 points per tenfold; say "association", show all points (`fig4_scale`) |
| C | The table helps every model, and not because of its length | rule effect +0.16…+0.62 nats; 263/420 per-lexicon intervals > 0, **none < 0**; the length-matched control gives the same | **Strong** | — | — |
| D | Examples switch most sites quickly but unstably | registered `k*`: KM medians 1.4–4.6 (dom) and 3.3–11.6 (blk); 18% censored; among switchers 2.06 first vs 8 lasting; **31% of switched sites fall back below zero, by a median of −0.76 nats** (§3.3) | **Moderate–strong** | "Ladder design decides the numbers; the wobble may be noise near M = 0" | Keep the KM medians as the endpoint. The dips are large: 59% of curves drop by more than 1 nat at some step (§3.3). Do **not** cite the frozen "92.8–99.5% non-monotone" alone: it counts any decrease, however small |
| E | Predictability declines with size in `dom` | D11: −0.081 [−0.111, −0.050] per tenfold, Holm p < 0.003; `blk` −0.037, Holm 0.055 | **Moderate** | "Non-monotone: the 7B dip carries it" | Specified before outcomes (D11); show the six points; frame as an association |
| F | In generation, ~1 in 5 reached sites revert; verbs most | Arm B: reach 13.5%, revert given reach 19.8%; verb > keyword > sigil in both grammars, the same ordering as the margins at 4 examples (§3.2) | **Moderate** (levels) / **Suggestive** (roles) | "Reach is 13.5%: the reached sites are a selected, easier subset" | Never multiply the two rates; claim the *ordering* agreement, not equal levels |
| G | Targeting the riskiest symbols does not beat random repair | H5 not supported: targeted > random in 43/100 cells | **Not supported** (honest negative) | "The interval test was not run, and the metric counts all sites" | Disclosed (D12, [08](08_issues_and_superseded_numbers.md)); report it as descriptive |
| G′ | Complete respelling into an unfamiliar alphabet removes silent errors | repaired sites: 47.7% → 15.5% reverting; 0 silent after | **Strong** but partly by construction | "Zero silent errors is guaranteed by design" | True for the *zero*: an invalid spelling cannot be silent. The *drop from 48% to 16%* is the empirical finding |
| H | Robust to the wording of the rule prompt | three framings: reversion stays within 0.42–0.62; per-model range 0.010–0.132 | **Moderate** | "13 points is not nothing" | Report the range, never the best wording |
| I | Calibration transfers | only the 2 development pairs: ECE 0.036–0.052 | **Weak–moderate** | "Two pairs" | Claim it for those two only (D12) |
| J | Partly changed languages are harder; base models adapt faster than instruct; punctuation is fixed faster than words | KM by density, kind and role | **Suggestive** | "Confounded; one lexicon per density" | Label them exploratory, in the discussion only |

**What you must *not* claim:**

- a general "DSL error rate" (the sites are designed collisions);
- generalization to new grammars (C3 was not testable, D1);
- that scale *causes* anything;
- that the models "ignore" the rules (they don't: claim C);
- that targeted repair can never work (only this rule, with this metric);
- the "about two / about eight" medians without "among sites that switch";
- "97% of curves wobble" without the size of the wobble (§3.3).

The full list is in [06 §4](06_publishability_and_paper.md).

---

## 3. The three new exploratory checks (2026-10-09)

All three use data that already existed, with no new GPU work. Run them with
[`scripts/exploratory_checks.py`](../scripts/exploratory_checks.py); the output is in
`analysis_addenda/exploratory/`. All are post hoc.

### 3.1 Inherited or shared? (strengthens claim A)

**Question.** Does an instruct model fail where *its own* base model leans the old way, or
where *any* model would?

**Method.**

- For every instruct model, take each base model in the run.
- Compute the AUROC of that base model's risk for the instruct model's reversions.
- The **consensus** averages the margins of all bases from *other lineages*. Qwen2.5 and
  Qwen2.5-Coder count as one lineage. The consensus is a pure "site difficulty" predictor.

| | AUROC |
|---|---|
| own base (the registered H4 pair, reproduced exactly) | 0.759–0.963 |
| same lineage, other sizes (mean) | 0.623–0.810 |
| other lineages (mean) | 0.475–0.722 |
| other-lineage consensus | 0.451–0.778 |
| **own − consensus** | **+0.118 to +0.354 (median +0.21); interval above 0 in 20/20** |

**Reading.**

- **About half of "where models fail" is shared difficulty.** The consensus reaches a median
  46% of the own base's signal above chance.
- **The rest is lineage-specific inheritance.** The gradient runs own > same lineage > other
  lineages.
- **The inherited part is larger for bigger models.** For models of 3B or less, the
  consensus reaches 48–69% (dom) and 22–65% (blk). For 7B and up, it reaches 20–47% (dom)
  and −16–30% (blk).
- **In one case the other lineages point the wrong way.** For Qwen2.5-Coder-32B-Instruct in
  `blk`, the consensus is *below chance* (0.451), while the own base gives 0.805.

**Use in the paper.** Make it the answer to "isn't H4 trivial?", labelled exploratory.

**Practical corollary:** screening a DSL's spellings with *any* open base model catches about
half the risk. Screening with the target model's own base catches the most.

### 3.2 Does generation agree with the margins? (refines claim F)

Instruct models, on the extinction subset of sites:

| grammar | role | margins, 0 examples: M < 0 | margins, 4 examples: M < 0 | Arm B (4 examples): old spelling given reached |
|---|---|---:|---:|---:|
| dom | sigil | 0.514 | 0.328 | 0.113 |
| dom | keyword | 0.497 | 0.395 | 0.232 |
| dom | verb | 0.495 | 0.483 | 0.294 |
| blk | sigil | 0.486 | 0.423 | 0.090 |
| blk | keyword | 0.496 | 0.440 | 0.176 |
| blk | verb | 0.506 | 0.493 | 0.428 |

**Reading.**

- **At the same number of examples (4), the orderings agree in both grammars:** verb >
  keyword > sigil. At 0 examples the roles are about equal.
- **So examples fix punctuation fast and word meanings slowly.** The same holds in the
  Kaplan–Meier cuts: sigils switch after 1.3 (dom) and 3.2 (blk) examples, verbs after 6.6
  and 11.4.
- **Levels are not comparable.** Generation's reached sites are a selected subset.
- **Correction.** The earlier sentence in 06, "the role ordering matches the margins", is
  true only at matched examples. 06 now says so.

### 3.3 How big are the wobbles? (refines claim D)

**The problem.** The frozen `nonmonotone` flag is true for *any* decrease between
consecutive rungs, however tiny. With seven noisy margins per site, almost every curve has
one, so "97% of curves wobble" alone would invite the reply "that's noise".

**The sizes.** All sites, all models:

| | dom | blk | pooled |
|---|---:|---:|---:|
| any decrease (the frozen flag) | 96.8% | 97.1% | 96.9% |
| a decrease of more than 0.5 nats between consecutive rungs | 81.0% | 82.2% | 81.6% |
| a decrease of more than 1 nat (odds factor 2.7) | 57.6% | 60.0% | 58.8% |
| switched sites that later fall back below zero | 31.7% | 31.1% | 31.4% (1,089 of 3,469) |
| how far they fall: median [IQR], nats | −0.71 [−1.44, −0.34] | −0.83 [−1.49, −0.38] | −0.76 [−1.46, −0.36] |
| of those, falling below −0.5 nats | 64.3% | 68.0% | 66.1% |

**Reading.**

- **The instability is real, not near-ties.** Nearly 6 in 10 curves drop by more than an
  odds factor of 2.7 at some step.
- **Relapses are confident.** About 1 in 3 switched sites relapse, and two-thirds of those
  relapses go deeper than −0.5 nats.
- **What to write:** "31% of sites that switch fall back later (median −0.76 nats)". Do not
  write "97% wobble".

---

## 4. Verdict by venue tier

| tier | examples | is the evidence enough? | what decides it |
|---|---|---|---|
| rigorous-evaluation venues | TMLR, NeurIPS Evaluations & Datasets track, ACL/EMNLP Findings | **Yes** | clear scoping; the figures and tables are ready |
| top NLP main conferences | ACL / EMNLP main, COLM | **Plausible** | framing around inheritance (A, A′) and design guidance (G′); the reviewers' novelty bar |
| top ML main conferences | ICML, NeurIPS main, ICLR | **Borderline** | they will want generality (a second language, or natural respellings) or a mechanism |
| software engineering / program comprehension | ICPC, ICSE workshops, MSR | **Yes**, if the DSL-design implications lead | a practitioner-facing discussion |
| cognitive science | CogSci | **Plausible** with the human framing ([10](10_humans_and_the_brain.md)) | treating the models as subjects; a small human comparison would make it strong |

---

## 5. What would make the paper stronger (in priority order)

| # | addition | cost | effect on reviewers |
|---|---|---|---|
| 1 | Report the inheritance check (§3.1) as exploratory | **done**, 0 GPU-hours | answers "trivial?" |
| 2 | Report the size of the non-monotone dips (are they noise near M = 0?) | **done** (§3.3), CSV only | answers "the wobble is noise": it is not |
| 3 | Run frontier API models in generation (Arm B) on the same tasks | API cost; days | answers "only small open models"; no H4 (no base models) |
| 4 | A second language, or natural respellings, preregistered like this study | weeks; about 40 GPU-hours | answers "one toy DSL": the biggest gap |
| 5 | A small human study (programmers, same collision sites) | IRB plus weeks | makes the CogSci version strong; gives a striking comparison figure |
| 6 | Mechanism: does attention to the token table predict the margin shift? | weeks | makes an ML main-track version possible |

Items 1 and 2 belong in this paper. Items 4 and 5 are the natural follow-up and fit a
**registered report** (§6).

---

## 6. Where to submit

**Closest prior work, both verified:**

- Miceli-Barone et al., *The Larger They Are, the Harder They Fail: Language Models do not
  Recognize Identifier Swaps in Python* (Findings of ACL 2023): inverse scaling when
  built-ins are swapped.
- Wu et al., *Reasoning or Reciting? Exploring the Capabilities and Limitations of Language
  Models Through Counterfactual Tasks* (NAACL 2024): includes counterfactual programming
  variants.

**How we differ:** a preregistered held-out test, site-level prediction from base models,
adaptation curves with censoring, and repair. Make this the related-work contrast; it is
also why NLP venues fit best.

### 6.1 The list (dates as checked on 2026-10-09)

| venue | fit | why it fits | realistic chance | deadline | notes |
|---|---|---|---|---|---|
| **ACL 2027** (via ARR), Kyoto, 17–22 Aug 2027 | ★★★ | evaluation and analysis of LMs; code; methodology | main: fair; **Findings: good** | **January 2027** (exact day TBA) | ACL 2025 accepted 20.3% to main and a further 16.7% to Findings. One review, two chances |
| **COLM 2027** | ★★★ | language-model behaviour: priors vs instructions, in-context learning | fair to good | **not yet announced** (late March in past editions) | a single-track, LM-focused audience |
| **TMLR** (journal, rolling) | ★★★ | judged on correctness and clarity, not novelty | **good**, if clearly written | any time | many desk rejections now (~53%), and per-author submission quotas; no conference trip |
| **NeurIPS 2027, Evaluations & Datasets track** | ★★★ | "evaluation as an object of study"; asks for explicit claims, assumptions and limitations, which a preregistered study has | fair | not announced (2026: 6 May) | release 3DOM as a benchmark with the paper |
| EMNLP 2027 (via ARR) | ★★★ | as ACL | as ACL | **~28 May 2027** (tentative) | the fallback after ACL reviews |
| **ICPC 2027** (program comprehension), Dublin, 25–26 Apr 2027 | ★★☆ | "do models comprehend a redefined language?" | fair to good | **abstract 29 Oct, paper 5 Nov 2026** | tight but possible: the results and figures are done |
| LLM4Code 2027 (ICSE workshop), Dublin | ★★☆ | empirical LLM-for-code studies | **good** | TBA | early feedback; check whether it is archival before submitting the same work elsewhere |
| **CogSci 2027**, Bilbao, 28–31 Jul 2027, theme *"Human Cognition in the Age of AI"* | ★★☆ | habit vs rule, interference, extinction ([10](10_humans_and_the_brain.md)) | fair; good with a human comparison | not announced (2026: 2 Feb) | archival proceedings: frame it as a *different* question from the NLP paper |
| ICML 2027 | ★☆☆ | empirical ML is in scope, but a methods-leaning audience | uncertain | ~22 Jan 2027 (estimated; call not yet out) | ICML 2025 accepted 26.9% |
| OOPSLA 2027, round 2 | ★☆☆ | DSL design for LLM users | uncertain | 7 Apr 2027 | PL reviewers expect a PL contribution |
| MSR 2027 Registered Reports (with EMSE), Dublin | — | for the **follow-up** study, reviewed before data collection | good for a sound protocol | TBA | the natural home for #4–5 in §5 |
| *passed or too close* | | | | | ICLR 2027 (25 Sep 2026, passed); FSE 2027 (2 Oct 2026, passed); EACL 2027 (ARR 3 Aug, passed); **NAACL 2027 (ARR 12 Oct 2026, in 3 days)**; OOPSLA 2027 round 1 (14 Oct 2026) |

### 6.2 A recommended plan

1. **Main target: ACL 2027, through the January 2027 ARR cycle.** It has the best topical
   fit, and Findings is a realistic fallback inside the same review. The paper outline,
   figures and tables are ready ([06 §7–8](06_publishability_and_paper.md)).
2. **If you want an ML audience instead:** COLM 2027 (deadline expected in late March; not
   yet announced). Do not have the same paper under review at ARR and COLM at once.
3. **If you want the surest outcome over prestige:** TMLR, at any time.
4. **Optional, for quick feedback first:** ICPC 2027 (5 Nov 2026) or LLM4Code 2027. ICPC is
   archival, and LLM4Code probably is too (check its call). Submit the *same* paper to only
   one archival venue. If a short workshop version comes first, the later full paper must
   say so.
5. **A second paper with the human angle:** CogSci 2027, ideally with a small human study on
   the same collision sites ([10](10_humans_and_the_brain.md)).
6. **The follow-up study:** a second language or natural respellings, as an MSR/EMSE
   registered report.

**A timeline from today (9 Oct 2026):**

- **by mid-December:** the full draft;
- **by Christmas:** internal review with the professor;
- **January:** the ARR submission;
- **around March:** reviews arrive;
- **then:** commit to ACL 2027, or revise for EMNLP 2027 (May).

> No venue can be promised. These are judgments of fit and of what reviewers typically ask
> for, given the evidence in §2.

---

## Sources (venue facts, checked 2026-10-09)

- ACL 2027 / NAACL 2027 / EACL 2027 dates: [EACL 2027 CFP](https://groups.google.com/g/ML-news/c/dZgPJQqLwP8), [NAACL 2027 CFP](https://list.sigdial.org/empathy/thread/HMN4FJ3FJ6OM6KZHGI5UVD3UR7DOQ64M), [ACL 2027](https://www.beri.net/events/acl-2027)
- ACL 2025 acceptance: [ACL 2025 Program Chairs report](https://www.aclweb.org/adminwiki/index.php/2025Q3_Reports%3A_Program_Chairs)
- ICML 2027 (estimated): [OpenCurious ICML 2027](https://www.opencurious.com/ai-conference-deadlines/icml-2027); ICML 2025 acceptance: [ICML 2025 fact sheet](https://media.icml.cc/Conferences/ICML2025/ICML2025_Fact_Sheet.pdf)
- ICLR 2027: [ICLR 2027 call for papers](https://www.iclr.cc/Conferences/2027/CallForPapers)
- COLM: [mldeadlines COLM](https://mldeadlines.com/conference/colm/) (2027 not yet announced)
- NeurIPS Evaluations & Datasets track: [NeurIPS 2026 E&D call](https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets); NeurIPS 2025 acceptance: [NeurIPS PC reflections](https://blog.neurips.cc/2025/09/30/reflections-on-the-2025-review-process-from-the-program-committee-chairs/)
- EMNLP 2027 (tentative): [trybibby NLP deadlines](https://trybibby.com/conference-deadlines/nlp)
- TMLR: [TMLR](https://jmlr.org/tmlr/index.html), [desk-rejection report](https://www.kucoin.com/news/flash/tmlr-editor-finds-authors-unfamiliar-with-their-own-ai-written-papers)
- ICPC 2027: [ICPC 2027 research track](https://conf.researchr.org/track/icpc-2027/icpc-2027-research-track); LLM4Code 2027: [conf.researchr.org](https://conf.researchr.org/home/llm4code-2027), [llm4code.github.io](https://llm4code.github.io/)
- FSE 2027: [FSE 2027 dates](https://conf.researchr.org/dates/fse-2027); OOPSLA 2027: [SPLASH 2027 OOPSLA](https://2027.splashcon.org/track/splashoopsla2027)
- MSR 2027 registered reports: [MSR 2027 RR track](https://2027.msrconf.org/track/msr-2027-registered-reports)
- CogSci 2027: [CogSci 2027](https://www.beri.net/events/cogsci-2027), [co-chair announcement](https://projects.cs.dal.ca/a2i2/news/2026-08-26-CogSci-2027.html)
- Related work: [Miceli-Barone et al. 2023](https://aclanthology.org/2023.findings-acl.19), [Wu et al. 2024](https://aclanthology.org/2024.naacl-long.102)
