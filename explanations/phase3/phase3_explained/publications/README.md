# Publication venues for Phase 3

**Last checked:** 2026-10-02. Deadlines and track names can change, so always
open the linked official call before planning a submission.

## 1. Where this research belongs

Phase 3 sits where four research areas overlap:

1. **AI for Software Engineering (AI4SE):** evaluating and improving LLM code
   generation.
2. **Programming languages and DSLs:** changing a language's surface spelling
   while keeping its meaning fixed.
3. **Software testing and analysis:** detecting an exact risky site and proving
   a repair preserves the canonical IR.
4. **Empirical software engineering:** designing fair controls, held-out tests,
   calibrated predictions, and reproducible experiments.

The paper can therefore be aimed in different directions:

```text
exact-site predictor + minimal repair       -> ASE / FSE / ICSE
measurement design + controlled experiment  -> EASE / EMSE
benchmark + canonical-IR oracle             -> FORGE Data / EASE AI Models & Data
semantic testing and repair                  -> ISSTA
general model-behaviour result               -> ACL / TMLR (only after broadening)
general result about language design         -> OOPSLA (only after broadening)
```

Here, **venue** is the general word for a conference, journal, workshop, or
special track. A conference has a fixed deadline, a tighter paper-length limit,
and a presentation. A journal normally accepts submissions throughout the year
and allows a longer, more complete treatment with one or more revision rounds.

## 2. Short answer

- **Best eventual conference fit:** **ASE**, if H4 is a real exact-site
  predictor and H5 is a demonstrated automated repair.
- **Closest currently open venue by topic:** **FORGE 2027**, because it is
  specifically about foundation models and software engineering. Its October
  deadlines are probably too soon for this project, however.
- **Most realistic 2027 route:** **EASE 2027**, especially its **AI Models &
  Data** track on 2027-03-15, if the benchmark and artifact become the center of
  the paper.
- **Best journal for the present hypothesis-driven design:** **Empirical
  Software Engineering (EMSE)**.
- **Best journal if the repair tool becomes the main contribution:**
  **Automated Software Engineering**.
- **Ambitious destinations after broad replication:** **FSE, ICSE, TOSEM,** or
  **TSE**.

**My recommendation:** do not rush the current repository into the nearest
deadline. Finish the real-model study and external-validity work, then aim the
full H4/H5 paper at ASE. If a 2027 submission is important, EASE AI Models &
Data is the most credible schedule. EMSE or the Automated Software Engineering
journal avoids forcing the work into a premature conference deadline.

## 3. Conference shortlist, ranked by closeness

The ranking measures fit to *this particular project*, not general prestige.

| Priority | Venue | What the venue studies | Why Phase 3 fits | Main caution |
|---:|---|---|---|---|
| 1 | [ASE — Automated Software Engineering](https://conf.researchr.org/track/ase-2026/ase-2026-research-track) | Automation for software analysis, synthesis, repair, testing, and maintenance, including AI4SE and DSLs. | The cleanest story is an automated linter that predicts a risky DSL site and applies a minimal semantics-preserving repair. | The 2027 call was not yet available when checked. A design plus `FakeLM` tests is not enough; show real models, held-out generalization, and a usable artifact. |
| 2 | [FORGE 2027](https://conf.researchr.org/track/forge-2027/forge-2027-research-papers) | Foundation models used in software engineering: code generation, quality assurance, prompting, testing, and verification. | This is the closest topical description of the current LLM-to-DSL problem. Both H4 risk prediction and H5 reliability intervention belong here. | Full/new-idea deadlines are 2026-10-25/30, which is too close unless the experiments and manuscript already exist. Keep the contribution about reliable software generation, not unsupported claims about model cognition. |
| 3 | [EASE 2027 Research](https://conf.researchr.org/track/ease-2027/ease-2027-papers) | Evidence-based and empirical software engineering, including benchmarking, AI4SE, study infrastructure, replication, and negative findings. | Excellent for the methodological lesson: silent versus loud collisions, opportunity bias, canonical-IR equality, counterbalancing, mandatory baselines, and held-out tests. | Reviewers will expect the experimental design to be finished: enough independent sites, effect sizes and uncertainty, and no hidden grammar/lexicon confound. |
| 4 | [FSE 2027](https://conf.researchr.org/track/fse-2027/fse-2027-papers) | Broad, high-impact software-engineering research, including AI/ML for SE, program analysis, synthesis, languages, testing, and tools. | Its longer research-paper format can hold the full H4 + H2 + H5 story and artifact evaluation. | Very high evidence and generality bar. The paper deadline is 2026-10-02 AoE—the date of this review—so this cycle is not a responsible target from the current state. |
| 5 | [ICSE 2027](https://conf.researchr.org/track/icse-2027/icse-2027-research-track) | The broad flagship conference for software-engineering methods, tools, experiments, and theory. Its AI4SE scope includes LLM code generation, trustworthy AI, prompting, synthesis, and better evaluation. | Strong home for a mature result that matters beyond 3DOM: exact-site prediction across models, mappings, and grammar families, followed by useful repair. | The 2027 research deadline closed on 2026-06-30. One small DSL or only in-sample evidence would be too narrow for the likely review bar. |
| 6 | [ISSTA 2027](https://conf.researchr.org/track/issta-2027/issta-2027-research-papers) | Software testing and program analysis. | Fits if the main object is the semantic-collision generator, canonical-IR oracle, and risk-guided testing/repair of LLM-produced programs. | Only a medium fit if the paper mainly asks about pretrained lexical habits. The page listed 2027-01-08/11 deadlines, but the detailed CFP was still marked TBD when checked. |
| 7 | [EASE 2027 AI Models & Data](https://conf.researchr.org/track/ease-2027/ease-2027-ai-models---data) | Evaluation of AI models and datasets for software engineering. | A natural home for the collision corpus, mapping generator, exact-site annotations, IR oracle, evaluation protocol, and real-model benchmark. | The artifact must be available at submission. This route makes the benchmark—not the whole H2/H4/H5 theory—the paper's center. Deadline: 2027-03-15. |
| 8 | [FORGE 2027 Data & Benchmarking](https://conf.researchr.org/track/forge-2027/forge-2027-data-and-benchmarking-track) | Datasets, benchmarks, metrics, construct validity, robustness, and reproducibility for foundation models in SE. | Almost exact scope for an IR-grounded collision benchmark and an audit of misleading evaluation. | Only 4 pages plus references and due 2026-11-15. That is too small for the complete theory, and publishing a thin archival slice may reduce novelty available to a later full paper. |
| 9 | [OOPSLA 2027](https://2027.splashcon.org/track/splashoopsla2027) | Programming languages and systems: language design, semantics, analysis, generation, verification, testing, and tools. | Possible if the result becomes a general principle for designing prompt-defined DSL surfaces, supported across multiple unrelated grammar families. | A stretch for the current empirical LLM benchmark. It needs a general PL contribution, not just one model failure mode. Review rounds: 2026-10-14 and 2027-04-07. |
| 10 | [ACL 2027](https://2027.aclweb.org/calls/main/) | Natural-language processing, language models, interpretability/model analysis, reasoning, and code models. | Possible for a paper centered on competition between pretrained lexical priors and prompt-local rules, with strong cross-model evidence. | The linter/repair artifact is more naturally SE. Use ACL only if the general finding about model behavior—not the software tool—is the headline. ARR deadline: 2027-01-04. |

### A venue not to force

[SANER 2027](https://conf.researchr.org/track/saner-2027/saner-2027-papers)
mentions LLMs, parsing, transformation, and repair, but its call requires AI/ML
work to address a real software-evolution or maintenance problem. Phase 3 does
not currently do that. It would become a fit only if the research question were
about safely migrating or evolving DSL vocabularies. Its main-track deadline
also passed on 2026-09-25.

## 4. Journal shortlist

| Priority | Journal | Best Phase 3 version for it | What must be true before submission |
|---:|---|---|---|
| 1 | [Empirical Software Engineering (EMSE)](https://link.springer.com/journal/10664/aims-and-scope) | The complete hypothesis-driven empirical study: controlled comparisons, calibrated prediction, replication, uncertainty, and AI applied to SE. | Complete real-model runs; expand beyond 40 prefix-distinct sites; use held-out mappings and a held-out grammar; report effect sizes, uncertainty, validity threats, and a replication package. |
| 2 | [Automated Software Engineering](https://link.springer.com/journal/10515/aims-and-scope) | H4 + H5 as a practical automated method for detecting and repairing unsafe DSL surfaces. | Make the implemented predictor and repair system central. Demonstrate improvement against random and global-renaming baselines and prove IR preservation over the evaluation corpus. |
| 3 | [ACM TOSEM](https://dl.acm.org/journal/tosem) | A substantial, archival H2/H4/H5 paper combining a method, tool, and broad empirical evaluation. | Generalize beyond a 3DOM case study with several models, mappings, grammar families, held-out evidence, and a reusable artifact. This is an ambitious target. |
| 4 | [IEEE TSE](https://www.computer.org/digital-library/journals/ts/cfp-ieee-transactions-on-software-engineering) | A mature result with broad importance to software construction, analysis, measurement, validation, and tooling. | Establish a general SE result rather than a single-DSL observation. This is also an ambitious target. |
| 5 | [Journal of Systems and Software (JSS)](https://shop.elsevier.com/journals/journal-of-systems-and-software/0164-1212) | A rigorous but somewhat more broadly placed AI4SE method and evaluation paper. | Extract reusable knowledge for LLM/DSL design that is independent of this specific application. |
| 6 | [Information and Software Technology (IST)](https://shop.elsevier.com/journals/information-and-software-technology/0950-5849) | A practical empirical contribution that improves software-development technology. | Present the lexicon constructor, site-risk method, or repair procedure as a concrete technology and validate it strongly. |
| Conditional | [Transactions on Machine Learning Research (TMLR)](https://jmlr.org/tmlr/editorial-policies.html) | A general learning-system result about lexical prior strength, local activation, extinction curves, or prompt-rule generalization. | Reframe beyond software engineering and validate across model families and tasks. TMLR does not accept an expanded version of an archival conference paper, so choose this route before publishing overlapping results elsewhere. |

## 5. Current submission calendar

This calendar is a planning snapshot, not a substitute for the official calls.

| Date | Venue/track | Practical decision |
|---|---|---|
| 2026-06-30 | ICSE 2027 research paper | Closed. Aim at a later cycle. |
| 2026-09-25 | SANER 2027 research paper | Closed, and not a natural fit. |
| 2026-10-02 | FSE 2027 research paper | Deadline date is today; do not rush an incomplete study. |
| 2026-10-14 | OOPSLA 2027, round 1 | Too soon and currently a stretch fit. Round 2 is 2027-04-07. |
| 2026-10-25/30 | FORGE 2027 abstract/paper | Closest live full-paper topic, but an aggressive and likely unrealistic schedule. |
| 2026-11-12 | [PLDI 2027](https://pldi27.sigplan.org/) | Stretch target only after a much stronger, general PL contribution. |
| 2026-11-15 | FORGE Data & Benchmarking | Possible only as a deliberately scoped four-page benchmark paper. |
| 2027-01-04 | ACL 2027 ARR submission | Use only for a broad model-behavior paper. |
| 2027-01-08/11 | ISSTA 2027 abstract/paper | Aggressive; use only with a testing/analysis-centered contribution. |
| 2027-01-15/22 | EASE 2027 research abstract/paper | Strong methodological target if the study can be completed rigorously. |
| 2027-03-15 | EASE AI Models & Data | Most realistic listed 2027 target for the benchmark/artifact version. |
| 2027-04-07 | OOPSLA 2027, round 2 | Time is better, but fit still depends on producing a general PL result. |
| Not announced when checked | ASE 2027 | Monitor the official ASE conference site; this is the best eventual conference fit. |

## 6. Why the paper is not ready yet

The repository already has a valuable platform: a generated `delta` mapping,
site census, canonical IR, corrected scoring path, H4 risk pipeline, and H5
repair proof over 62 programs. But the current evidence is not yet a conference
or journal result:

- no complete real-model Phase 3 result has been run;
- 63 of 103 semantic sites share ambiguous prefixes, leaving only **40**
  prefix-distinct examples;
- all of those examples belong to one grammar family;
- `delta` character length was checked, but actual tokenizer fertility was not;
- local-activation materials and mapping counterbalancing are incomplete;
- H4 still needs unseen mappings and at least one held-out grammar family;
- H2 needs the preregistered three-scale sign-agreement test;
- H5 needs targeted repair versus global renaming and random rewriting at the
  same symbol budget.

These are not cosmetic additions. They determine whether the paper shows a
general method or only describes one carefully engineered example.

## 7. A practical publication plan

### Route A — recommended: one complete SE paper

1. Expand the templates so the predictor has substantially more than 40
   independent prefixes.
2. Add a genuinely different grammar family and counterbalanced mappings.
3. Run the tokenizer-fertility check and the real-model experiments.
4. Evaluate H4 on held-out mappings and a held-out grammar, with calibration and
   all mandatory baselines.
5. Evaluate H5 against random rewriting and global renaming at matched budgets,
   with whole-corpus IR equality.
6. Submit the resulting predictor-and-repair paper to **ASE**; consider **FSE**
   or **ICSE** if the effect is broad and the evidence is especially strong.

### Route B — empirical-methods paper

Make opportunity bias, silent collision construction, prefix independence,
counterbalancing, and scale-robust interaction testing the main contribution.
Target **EASE** or **EMSE**.

### Route C — benchmark paper

Make the corpus, generated mappings, collision labels, canonical-IR oracle,
evaluation protocol, and reproducible harness the deliverable. Target **EASE AI
Models & Data** or **FORGE Data & Benchmarking**. Before choosing this route,
check whether publishing a short archival paper would restrict a later full
paper containing the same core contribution.

### Route D — model-behavior paper

Make extinction threshold `k*`, lexical-prior competition, and local activation
the central scientific result. This needs several model families, unrelated
grammars/tasks, and a claim that generalizes beyond software tooling. Only then
consider **ACL** or **TMLR**.

## 8. Possible titles by framing

- **ASE/FSE/ICSE:** *Predicting and Repairing Silent Surface Collisions in
  Prompt-Defined DSLs*
- **EASE/EMSE:** *Measuring Familiar-Token Reversion Without Opportunity Bias*
- **FORGE/EASE Data:** *An IR-Grounded Benchmark for Surface-Collision Risk in
  LLM-Generated DSLs*
- **ISSTA:** *Semantic-Collision Testing and Risk-Guided Repair for
  LLM-Generated Programs*
- **ACL/TMLR:** *When Pretrained Lexical Priors Override Prompt-Local Grammar
  Rules*

## 9. Final choice rule

Do not choose the venue first and bend the project until it resembles that
venue. After the real experiments, ask which result is genuinely strongest:

- **prediction and repair work best** -> ASE;
- **measurement/design lesson is strongest** -> EASE or EMSE;
- **the reusable benchmark is strongest** -> EASE AI Models & Data or FORGE;
- **the effect becomes broad and field-significant** -> FSE, ICSE, TOSEM, or
  TSE;
- **the model-behavior law generalizes outside software engineering** -> ACL or
  TMLR.

That choice keeps the paper's central claim honest and gives it to the reviewers
most likely to understand why it matters.
