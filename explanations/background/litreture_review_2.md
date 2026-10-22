You are acting as a senior research scientist specializing in large language models, code generation, domain-specific languages, in-context learning, knowledge conflict, cognitive modeling, and mechanistic interpretability.

I need a rigorous, comprehensive, and adversarial literature review and novelty audit for a research project. Do not simply confirm my hypothesis. Assume that my terminology, interpretation, and proposed novelty may be partly incorrect. Correct my wording whenever necessary and explain the correction in plain language.

Your goal is to determine:

1. Which parts of my original hypothesis have already been established.
2. Which papers established them and exactly how.
3. Which parts have only partial evidence.
4. Which parts remain genuinely untested.
5. Whether my refined behavioral and mechanistic hypotheses could support a publishable contribution.
6. What minimum experiments would be required to demonstrate that contribution.
7. What claims I must avoid because existing literature already covers them.

Use current literature available on the date of the search. State the literature-search cutoff date.

# Research background

I am studying natural-language-to-DSL generation using a 3D-editing language called 3DOM. The familiar version resembles CSS selectors and jQuery method chaining.

A representative familiar form looks approximately like:

```javascript
(function(){ $T111('.bus > .door').resize('#333333'); })();
```

The system parses generated programs and translates them through a mapping layer into a canonical intermediate representation, or IR. Different surface languages are intended to express the same underlying programs.

My preliminary experiment compared:

* `identity`: familiar CSS/jQuery-like 3DOM syntax.
* `alpha`: familiar-looking tokens and symbols assigned different meanings.
* `beta`: unfamiliar invented ASCII words.
* `gamma`: unfamiliar Unicode symbols.

The experiment included:

* Base-model likelihood measurements.
* Instruction-model natural-language-to-DSL generation.
* Bare and scaffolded prompts.
* Qwen2.5-Coder models from approximately 0.5B to 7B.
* Parsing and semantic evaluation through a canonical IR.

Important preliminary observations included:

* All alien languages were more surprising to the base models than identity.
* Alien syntax generally reduced accuracy, but not invariably.
* Beta sometimes performed very well despite worse token fertility.
* Alpha produced severe failures in some larger-model conditions.
* In alpha, the model frequently emitted the familiar selector sigil `.` when the supplied DSL specification required `#`.
* The same reassigned symbol appeared to survive in another syntactic location, suggesting that token identity alone might not explain the failure.
* However, those locations had different grammatical and semantic roles, so this is not yet a controlled context comparison.
* The apparent increase in reversion from bare to scaffolded prompting was affected by opportunity bias: bare outputs often failed to reach the selector decision at all.
* Conditional counts were approximately `3/3` bare reversions versus `15/20` scaffolded reversions, so the current experiment does not demonstrate that scaffolding caused reversion.
* Gamma has tokenizer and lexer problems and should not be treated as a clean isomorphic control.
* Only one main model family and approximately 21 tasks per condition were used.
* A semantic-scoring defect was discovered and must be corrected.

Treat all of these as preliminary observations, not established conclusions.

# Original hypothesis to audit

The original hypothesis was approximately:

> Holding task semantics, abstract program structure, grammar complexity, and approximate token budget constant, models will generate semantically correct programs more reliably in a concrete syntax constructed from familiar CSS/jQuery patterns than in structurally isomorphic unfamiliar syntaxes. Explicit specifications and examples should attenuate this surface-familiarity effect, while grammar-constrained decoding should primarily eliminate syntactic errors rather than necessarily eliminating semantic errors. The magnitude of these effects may vary with model capacity.

A stronger but potentially overclaimed version was:

> LLMs generate DSLs well mainly because those DSLs resemble syntax densely represented during pretraining rather than because of general rule-following or reasoning ability.

Critically evaluate both versions. Do not accept the philosophical opposition between “reasoning” and “pattern matching” unless it can be operationalized scientifically.

Determine whether the following possible claims are already covered:

* Familiar syntax performs better than unfamiliar syntax.
* Reassigning familiar symbols causes more interference than using novel symbols.
* Explicit definitions cannot fully override pretrained meanings.
* Smaller or larger models rely more heavily on learned priors.
* Token fertility predicts generation accuracy.
* Grammar specifications and examples improve novel DSL generation.
* Constrained decoding improves syntax more than semantics.
* Base-model likelihood predicts instruction-model performance.
* Renaming tool schemas or APIs to match model expectations improves reliability.
* LLM behavior under conflicting rules resembles human Stroop interference.
* Attention heads or residual-stream components mediate conflict between learned and contextual information.

# Refined behavioral hypothesis

The refined hypothesis is not “context rather than tokens.” It is an interaction:

> Surface-form interference during DSL production may result from the joint presence of a strong familiar-token competitor and a local syntactic context that activates that competitor. A familiar token may survive reassignment in an unfamiliar context but revert to its pretrained meaning in a context strongly associated with that meaning.

A simple version is:

> Models may learn a new symbol, but fail when that symbol replaces a strong convention exactly where the old convention is most strongly expected.

Audit whether this exact interaction has already been tested:

$$
\text{competitor-token prior strength}
\times
\text{competitor-specific local syntactic activation}
$$

The key requirement is that token identity, semantic role, AST position, grammar legality, and task meaning are properly controlled. Search specifically for papers that independently manipulate both factors rather than varying them together.

# Refined mechanistic hypothesis

The proposed mechanistic question is:

> At a DSL generation site, does a short-range grammar-completion pathway support the familiar but incorrect token, while a long-range specification-binding pathway supports the newly defined DSL token? Does reversion occur when the contribution of the local grammar-completion pathway becomes stronger than the specification-binding contribution?

For example:

* A distant rule in the prompt says that `#` is the correct DSL token.
* The immediate CSS-like prefix strongly predicts the familiar token `.`.
* The model must integrate those conflicting signals at the output location.

Do not assume that these are literally two attention heads. The mechanism could involve attention, MLP layers, embeddings, distributed residual-stream representations, or several interacting components.

Investigate whether prior work has already identified:

* Short-range versus long-range attention pathways under rule conflict.
* Memory heads versus context heads.
* Attention heads promoting memorized versus in-context answers.
* Residual-stream states carrying familiar and newly defined meanings.
* Rule-binding or entity-binding representations.
* Induction heads and pattern-completion mechanisms.
* Mechanisms of code-syntax completion.
* Activation patching or path patching under code or semantic conflict.
* Causal interventions that switch a model between pretrained and contextual answers.
* Human Stroop or congruency analogies applied to LLMs.
* Structural or lexical priming during language-model production.

The potential novelty is not merely that such pathways exist. Determine whether anyone has demonstrated them for:

1. Concrete-syntax production in a prompt-defined DSL.
2. Exact emitted-token reversion.
3. The same token mapping at matched grammatical positions.
4. Competitor-specific local grammar activation.
5. Competition between a remote DSL definition and the immediate generation prefix.
6. Prediction of exact failure sites on unseen grammars.
7. Semantics-preserving local rewrites that reduce the predicted internal conflict.

# Seed papers

Start with the following papers, but do not limit the review to them:

1. “Don’t Adapt Small Language Models for Tools; Adapt Tool Schemas to the Models”
   arXiv:2510.07248

2. “Persistent Priors, Preserved Targets: A Stroop-Style Paradigm for Lexical Override”
   arXiv:2606.07555

3. “The Larger They Are, the Harder They Fail: Language Models Do Not Recognize Identifier Swaps in Python”
   Findings of ACL 2023
   https://aclanthology.org/2023.findings-acl.19/

4. “LLMs Lean on Priors, Not Programming Language Semantics” / PLSemanticsBench
   arXiv:2510.03415

5. “Conflict and Congruency Effects in Large Language Models: In-Weight and In-Context Competition in a Verbal Conflict Task”
   arXiv:2608.11510

6. “A Mechanistic Lens on Semantic Conflicts: Using Activation Patching to Understand LLM Behavior”
   arXiv:2607.05587

7. “Characterizing Mechanisms for Factual Recall in Language Models”
   EMNLP 2023
   https://aclanthology.org/2023.emnlp-main.615/

8. “Cutting Off the Head Ends the Conflict”
   Findings of ACL 2024
   https://aclanthology.org/2024.findings-acl.70/

9. “Mechanistic Understanding of Language Models in Syntactic Code Completion”
   arXiv:2502.18499

10. “Grammar Prompting for Domain-Specific Language Generation with Large Language Models”
    arXiv:2305.19234

11. “From Text to DSL: Evaluating Grammar-Based Model Generation Using Open LLMs”
    arXiv:2605.15865

12. “Text2DSL: LLM-Based Code Generation for Domain-Specific Languages”
    arXiv:2606.22586

13. “TokDrift: When LLM Speaks in Subwords but Code Speaks in Grammar”
    ACL 2026

14. “Anka: A Domain-Specific Language for Reliable LLM Code Generation”
    arXiv:2512.23214

15. “When Models Ignore Definitions: Measuring Semantic Override Hallucinations in LLM Reasoning”
    arXiv:2602.17520

16. “The Override Gap”
    arXiv:2604.23750

17. “The Hidden Cost of Structure: How Constrained Decoding Affects Language Model Performance”
    RANLP 2025

18. “From Input Perception to Predictive Insight: Modeling Model Blind Spots Before They Become Errors”
    EMNLP 2025

19. “In-Context Learning and Induction Heads”
    arXiv:2209.11895

20. “Do as I Say, Not as I Do: Instruction–Induction Conflict in LLMs”
    arXiv:2605.20382

21. “How Training Data Shapes the Use of Parametric and In-Context Knowledge in Language Models”
    arXiv:2510.02370

22. “Code over Words: Overcoming Semantic Inertia via Code-Grounded Reasoning”
    Findings of ACL 2026

23. “Patterns of Priming in Production: Lexical, Semantic and Structural Alignment in LM Generation”
    arXiv:2609.04484

Search backward through these papers’ references and forward for papers that cite them. Search for additional work using terms such as:

* prompt-defined semantics;
* semantic override;
* counterfactual remapping;
* lexical override;
* operator swapping;
* identifier swapping;
* symbol reassignment;
* syntax familiarity;
* surface-form priors;
* context–memory conflict;
* parametric versus contextual knowledge;
* rule–habit competition;
* congruency effects;
* structural priming;
* code-generation priors;
* DSL generation;
* grammar prompting;
* tokenizer–grammar mismatch;
* tool-schema alignment;
* constrained decoding;
* attention heads for syntax;
* residual-stream conflict;
* activation patching;
* path patching;
* causal mediation in transformers;
* specification following versus local completion.

# Literature-review method

Use primary sources whenever possible:

* Official conference proceedings.
* ACL Anthology.
* arXiv full papers.
* Publisher or author project pages.
* Official code repositories when needed to verify implementation details.

Do not rely on blogs or AI-generated summaries when the original paper is available.

Read the full paper and relevant appendices for every paper classified as directly overlapping or potentially preempting the contribution. Do not infer experimental details from the abstract alone.

For every paper, verify:

* Exact title.
* Full author list in correct order.
* Initial publication or submission date.
* Latest revision date when relevant.
* Publication venue and whether it is peer-reviewed, accepted, workshop-only, or only a preprint.
* DOI or official persistent URL.
* Models used.
* Task direction: comprehension, execution, candidate ranking, completion, or unrestricted generation.
* Whether the model emits concrete source syntax.
* Whether outputs are free-generated or evaluated through teacher-forced likelihood.
* What variables are manipulated.
* What variables remain confounded.
* Whether tokenization is controlled.
* Whether the work is behavioral, predictive, mechanistic, or interventional.
* Whether the reported evidence is correlational or causal.
* Whether generalization is tested on held-out items, mappings, grammars, or model families.

Never invent page numbers, sections, tables, quotations, or results. If information cannot be verified, label it as unverified.

Use only brief quotations when necessary. Prefer faithful paraphrases and identify the exact section, page, table, figure, or appendix supporting the interpretation.

# Required output

Produce a structured Markdown report with the following sections.

## 1. Executive verdict

Give a direct answer:

* Is the original hypothesis already covered?
* Which pieces are fully covered?
* Which pieces remain partially open?
* Is the refined local-context hypothesis genuinely different?
* Is the mechanistic short-range-versus-long-range hypothesis already covered generically?
* What exact conjunction remains potentially novel?
* Is the project worth continuing?
* What would make it publishable?

Do not guarantee publication.

## 2. Corrected hypothesis definitions

Rewrite the following into precise, falsifiable hypotheses:

* Original surface-familiarity hypothesis.
* Token-prior × local-context interaction hypothesis.
* Remote-specification versus local-completion mechanistic hypothesis.
* Exact-site prediction hypothesis.
* Semantics-preserving intervention hypothesis.

Explain each in simple language after its formal version.

If any hypothesis contains a false dichotomy or unmeasurable concept, replace it with an operational definition.

## 3. Master literature table

Create a table with one row per paper and these columns:

| Paper | Authors | Date and venue/status | Task and models | Main manipulation | Main result | Exact overlap with original hypothesis | Exact overlap with refined hypothesis | Mechanistic overlap | What it does not cover | Threat to my novelty | Official link |

Classify each paper as:

* Directly preempting.
* Strong partial overlap.
* Methodologically adjacent.
* Application-related.
* Background only.

## 4. Claim-by-claim novelty matrix

For every claim in the original and refined hypotheses, label it:

* Already established.
* Substantially established.
* Partially studied.
* Unresolved.
* Apparently unstudied after this search.

For every classification, cite the strongest supporting papers and explain why.

Do not say “no one has studied this.” Instead say:

> “Within the databases, keywords, citations, and publication period searched, I did not identify a paper that tests…”

Then state the search boundary.

## 5. Deep comparison with the closest papers

Provide detailed comparisons with at least:

* PLSemanticsBench.
* Persistent Priors.
* Conflict and Congruency Effects.
* Identifier Swaps in Python.
* PA-Tool.
* A Mechanistic Lens on Semantic Conflicts.
* Characterizing Mechanisms for Factual Recall.
* Cutting Off the Head Ends the Conflict.
* TokDrift.
* Anka.

For each one, answer:

1. What was the task?
2. What was emitted by the model?
3. What was manipulated?
4. What mathematical quantities were measured?
5. Was the evidence behavioral, mechanistic, or causal?
6. Which of my claims does it preempt?
7. What exact experimental dimension does it leave open?

## 6. Behavioral mathematical framework

Evaluate and improve the following notation.

Let:

* \(c_i\) be the DSL-correct token or candidate string.
* \(q_i\) be the familiar but incorrect competitor.
* \(x_i\) be the exact prefix at output site \(i\).
* \(Y_i=1\) indicate that the instruction model emits \(q_i\).
* \(O_i=1\) indicate that unrestricted generation reaches the relevant decision site.

Define the local correct-versus-competitor margin:

$$
D_i=
\log P(c_i\mid x_i)
-
\log P(q_i\mid x_i)
$$

Explain:

* \(D_i>0\): rule-consistent token preferred.
* \(D_i<0\): familiar competitor preferred.

Define token-prior strength under a neutral context:

$$
T_i=
\log P(q_i\mid x_{\text{neutral}})
-
\log P(c_i\mid x_{\text{neutral}})
$$

Define competitor-specific contextual activation:

$$
A_i=
\left[
\log P(q_i\mid x_i)
-
\log P(c_i\mid x_i)
\right]
-T_i
$$

Consider the mixed-effects model:

$$
\operatorname{logit}P(Y_i=1\mid O_i=1)
=
\beta_0+
\beta_TT_i+
\beta_AA_i+
\beta_{TA}T_iA_i+
u_{\text{task}}+
u_{\text{mapping}}+
u_{\text{grammar}}+
u_{\text{model}}
$$

Evaluate whether \(\beta_{TA}>0\) correctly captures the proposed interaction.

Also explain the opportunity decomposition:

$$
P(\text{observed reversion})
=
P(O_i=1)
P(Y_i=1\mid O_i=1)
$$

Recommend:

* Primary behavioral outcomes.
* Confidence intervals.
* Mixed-effects structure.
* Clustered bootstrap strategy.
* Calibration metrics.
* AUROC/AUPRC.
* Brier score and log loss.
* Ranking metrics.
* Multiple-comparison controls.
* Sample-size and power-simulation strategy.

If candidate strings have different token lengths, explain the correct sequence-scoring procedure and whether to include a common suffix.

## 7. Mechanistic mathematical framework

Analyze the final logit difference:

$$
D=
(z_q-z_c)
=
(u_q-u_c)^\top\operatorname{LN}(r_L)
$$

where \(r_L\) is the final residual stream.

Use the residual decomposition:

$$
r_L=
r_0+
\sum_{\ell,h}o_{\ell,h}
+
\sum_\ell m_\ell
$$

where \(o_{\ell,h}\) is an attention-head output and \(m_\ell\) is an MLP output.

Explain how to measure:

1. Layerwise development of the competitor margin:

$$
D_{i,\ell}
=
(u_q-u_c)^\top
\operatorname{LN}(r_{i,\ell})
$$

2. Direct component contribution:

$$
A_{i,k}=
(u_q-u_c)^\top o_{i,k}
$$

3. Source-position-specific attention contribution.

4. Clean-to-conflict activation patching.

5. Conflict-to-clean reverse patching.

6. Mean ablation and resample ablation.

7. Path patching from:

   * remote DSL rule positions;
   * immediate local-prefix positions;
   * candidate context-detector components;
   * candidate competitor-writing components;
   * final output position.

8. Normalized recovery:

$$
R=
\frac{D_{\text{patched}}-D_{\text{conflict}}}
{D_{\text{clean}}-D_{\text{conflict}}}
$$

9. Causal mediation from local context through internal activation to token reversion.

Explain why:

* Attention weights alone are not causal evidence.
* Logit-lens analysis is descriptive.
* Activation patching can create off-manifold states.
* A sparse single-head explanation may not exist.
* MLP components may be as important as attention.
* A discovery/test split is necessary when selecting layers or heads.

The strongest proposed mechanistic prediction is:

> Patching the local-prefix pathway should transfer or remove familiar-token reversion, while patching the remote-definition pathway should transfer or restore the correct DSL binding.

Determine whether this prediction is already directly tested in prior literature or remains specific to DSL production.

## 8. Required causal experiment

Design the minimum clean experiment crossing:

| Factor                                         | Levels                      |
| ---------------------------------------------- | --------------------------- |
| Familiar-competitor strength                   | strong, weak, neutral/novel |
| Competitor-specific local syntactic activation | high, medium, low           |

Require:

* Same canonical AST and IR.
* Same semantic request.
* Same grammatical role.
* Same output decision position.
* Counterbalanced token mappings.
* Approximately matched token lengths.
* Both correct and familiar competitor forms grammar-valid.
* Correct and competitor forms mapping to different IR semantics.
* Context levels selected before observing instruction-model outcomes.
* Multiple independently designed grammar families.
* Held-out mappings, grammars, and model families.
* Forced-choice/forced-prefix evaluation plus unrestricted generation.
* Exact IR or executed-state scoring.
* Correct opportunity-conditioned reversion analysis.

Explain how to construct minimal pairs that change competitor-specific contextual activation without changing semantic role.

## 9. Mechanistic experiment plan

Provide a staged, computationally realistic plan:

### Stage 1: Behavioral validation

Establish that the token-prior × local-context interaction exists.

### Stage 2: Layer localization

Use a tuned lens or equivalent method to identify where the correct-versus-competitor margin changes.

### Stage 3: Coarse causal localization

Patch residual-stream states across layers and source positions.

### Stage 4: Component localization

Investigate attention heads and MLP components only in the layer range identified previously.

### Stage 5: Path testing

Distinguish:

* a local grammar-context detector;
* a familiar-competitor writer;
* a remote rule/specification retriever;
* a correct-token writer.

### Stage 6: Intervention

Test whether patching, steering, or semantics-preserving syntax rewriting selectively reduces reversion.

Include essential negative controls:

* Ordinary CSS tasks where `.` is correct.
* Low-context conditions.
* Novel-token controls.
* Random component patches.
* Different-item activation patches.
* Prompt paraphrases.
* Tokenization-matched controls.
* Interventions that should not affect the decision.

## 10. Prediction and repair contribution

Evaluate the novelty of using the matched base checkpoint to compute:

$$
S_i=
\log P_{\text{base}}(q_i\mid x_i)
-
\log P_{\text{base}}(c_i\mid x_i)
$$

and predicting exact instruction-model failures.

Distinguish this from:

* Same-model prior-strength prediction.
* Generic input surprisal.
* Whole-program NLL.
* Hidden-state error probes.
* Base-model structured-output performance.
* PA-Tool’s peakedness measure.

Require held-out evaluation on:

* Unseen token mappings.
* Unseen grammar families.
* Unseen model families.

Then evaluate the proposed practical method:

> A surface-collision linter that identifies dangerous grammar sites and changes only high-risk surface forms while deterministically translating them back to the original API or canonical IR.

Compare against:

* No rewrite.
* Random rewrite.
* Human-designed rewrite.
* Global familiar renaming.
* PA-Tool-style renaming.
* Grammar-constrained decoding.
* Semantic constrained decoding.
* Oracle rewriting.

Measure error reduction, number of changed symbols, token cost, human readability, latency, and performance on low-risk negative controls.

## 11. Human analogy

Explain carefully:

* In what behavioral sense this resembles the human Stroop effect.
* Which claims about human automaticity are reasonable analogies.
* Why similar observable behavior does not prove the same internal mechanism.
* Why model latency should not automatically be interpreted as human reaction time.
* Whether token surprisal, entropy, or probability margin is the better computational analogue.

Identify prior papers explicitly using Stroop, congruency, automatic-versus-controlled processing, priming, or cognitive-control language for LLMs.

## 12. Strongest surviving contribution

Give three versions:

1. One-sentence scientific contribution.
2. One-paragraph abstract-style contribution.
3. Plain-language explanation for a professor.

The candidate contribution should be approximately:

> Existing work shows that pretrained meanings can resist prompt-local redefinition. This project tests whether that resistance is selectively activated by the immediate grammatical environment during concrete DSL production, whether remote specification binding and local grammar completion form causally separable pathways, whether their competition predicts exact reversion sites on unseen grammars, and whether targeted semantics-preserving rewrites prevent those failures.

Revise this if the literature does not support its novelty.

## 13. Go/no-go assessment

Give a candid decision:

* What result would justify continuing?
* What pilot should be run first?
* What result would falsify the local-context hypothesis?
* What result would make the mechanistic study unnecessary?
* What minimum evidence could support a workshop paper?
* What evidence could support ACL/EMNLP Findings or an ICSE/ASE/FSE paper?
* What additional evidence might be needed for a main-track NLP or ML contribution?

Do not promise acceptance.

## 14. Claims to avoid

Create a list of statements that would likely be rejected by reviewers, including any unsupported form of:

* “Models do not reason.”
* “Models only pattern-match.”
* “Attention explains the behavior.”
* “This is the first LLM Stroop effect.”
* “No one has studied prior override.”
* “Familiar syntax is always superior.”
* “Larger models necessarily have stronger habits.”
* “Token fertility causes semantic failure.”
* “Constrained decoding only fixes syntax.”
* “Base-model likelihood prediction is entirely new.”
* “Generation rather than comprehension is sufficient novelty.”
* “The current experiment proves contextual gating.”

Provide a defensible replacement for each rejected statement.

## 15. Bibliography and search audit

Include:

* A complete bibliography with official links.
* BibTeX entries for directly relevant papers.
* Search engines and databases used.
* Search queries used.
* Date range searched.
* Backward- and forward-citation procedure.
* Papers excluded after full-text review and the reason for exclusion.
* Papers that could not be accessed or verified.
* Remaining uncertainty about concurrent or unpublished work.

# Quality requirements

* Be skeptical and evidence-driven.
* Clearly distinguish correlation, prediction, causal manipulation, and mechanistic explanation.
* Separate token identity from tokenization.
* Separate local syntactic context from document-level prompt framing.
* Separate grammar validity from semantic correctness.
* Separate teacher-forced token preference from unrestricted generation.
* Separate reaching a decision site from reverting conditional on reaching it.
* Separate a learned model prior from unverifiable claims about exact pretraining-corpus frequency.
* Separate behavioral similarity to humans from mechanistic equivalence.
* Do not treat model size as a controlled causal variable.
* Do not treat an attention map as proof.
* Do not exaggerate “combination novelty”; determine whether the combination produces a new falsifiable result or merely combines known methods.
* Cite every substantive literature claim.
* Whenever possible, cite the exact section, page, table, figure, or appendix supporting the claim.
* End with the narrowest defensible hypothesis and the single most important next experiment.

If workspace access is available, save the completed review as:

```text
literature_review_and_novelty_audit.md
```

and save verified BibTeX entries as:

```text
references.bib
```

Also provide a concise summary in the response containing:

1. What is already known.
2. What remains open.
3. The strongest proposed novelty.
4. The single next experiment I should run.
