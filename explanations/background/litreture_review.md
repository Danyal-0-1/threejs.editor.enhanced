# Literature Review and Publication-Venue Strategy

**Project:** Strata / 3DOM and the alien-syntax experiment  
**Research cut-off:** 9 September 2026  
**Status:** Working review based on the repository and primary literature. Venue rules are time-sensitive and must be rechecked on the linked official pages before submission.

## 1. The paper this repository can support

The repository contains two related but separable research contributions.

### Study A — Strata as an intelligent 3D editing system

Strata puts a small language between a person, an optional language model, and a Three.js scene. The language provides CSS-like selectors and a closed operation set. The host application performs deterministic work such as selector resolution, validation, execution, undo, and versioning; the model handles only the residual fuzzy mapping from natural language to operations and arguments.

The strongest defensible hypotheses are:

- **H1 — decomposition:** Moving deterministic subproblems from the model into the host will improve task success, with the largest gain on the subproblems the host almost completely removes.
- **H2 — reduced capability requirement:** Once deterministic work is removed, smaller stock models can be sufficient for the remaining bounded translation task without task-specific training.
- **H3 — interaction quality:** A typed, inspectable, reversible intermediate language can make AI-assisted editing more controllable and easier to correct than unconstrained code or scene generation.
- **H4 — local deployment:** A bounded language and a small model make private, in-browser editing technically plausible, although actual usability, latency, memory, and device coverage still require measurement.

The current repository offers preliminary support for H1 and H2 on synthetic fixtures: the reported 1.5B result rises from 73% under the current scaffold to 86% with host resolution, selector resolution rises from 54% to 91%, and a 0.5B model reaches 91% on the host-resolved selector condition. These are promising **system-evaluation results**, not yet evidence of human usability or broad real-world generalization.

### Study B — alien syntax as a controlled probe of pretraining priors

The alien-syntax package keeps the grammar structure and canonical JSON IR fixed while changing terminal spellings through a bijection \(\phi\). It separates two mechanisms:

- **Interference (alpha):** familiar surface tokens are deliberately assigned the wrong meanings.
- **Absence (beta):** pronounceable pseudo-lexical tokens reduce direct overlap with familiar programming-language spellings.
- **Glyph novelty (gamma):** visually unusual symbols explore a more extreme intervention, but the current gamma mapping is not lexically isomorphic to the source language.

The intended hypotheses are:

- **H5 — lexical-prior effect:** For meaning-equivalent programs with matched structural complexity and token cost, changing only terminal spellings changes base-model likelihood and/or task accuracy.
- **H6 — interference versus absence:** Familiar-but-wrong spellings and unfamiliar spellings create different failure modes and should not be pooled into one “unfamiliarity” variable.
- **H7 — structural equivalence:** If parsing, canonicalization, and round-trip tests agree, observed model differences can be attributed more narrowly to the surface intervention rather than to a changed task language.

The repository does **not yet establish H5 or H6**. All three candidates fail the precommitted tokenizer-fertility band: worst ratios are alpha 1.073, beta 1.448, and gamma 2.285 against the allowed range [0.95, 1.05]. The primary \(\Delta\)NLL-per-character measurement is still absent. Gamma also changes lexical reachability and is therefore not a clean isomorphic arm. The 149 passing structural tests are valuable evidence for the implementation, but they do not substitute for the missing model experiment.

## 2. Evidence map

| Claim | Literature that supports or motivates it | Literature that qualifies or challenges it | What this project must demonstrate |
|---|---|---|---|
| Surface familiarity affects models of code | Hindle et al.; CodeT5; identifier-swap study; ReCode; SeqCoBench | ContraCode and SPACE show robustness can be learned; prompt-label studies show surface meaning is not always used in a human-like way | Paired model results with identical IR, matched token cost, several models/seeds, and confidence intervals |
| Grammar/host constraints can make small or untuned models useful | Yin & Neubig; Shin et al.; PICARD; Geng et al.; DOMINO | Constraints guarantee form, not correct intent; poor token/grammar alignment can reduce accuracy | Separate syntax validity, canonical IR correctness, execution correctness, and end-task success |
| Decomposing an AI workflow improves control and outcomes | AI Chains; Human-AI Interaction Guidelines; LLMR | These studies do not establish Strata's exact causal mechanism or on-device sufficiency | A controlled bare/scaffolded/host-resolved comparison and a user study |
| Natural language is useful for 3D authoring | WordsEye; SceneSeer; LLMR; 3D-GPT | Prior systems already establish the general concept, so “natural language for 3D” is not novel | Position novelty in selector-based editing, deterministic execution, reversibility, local inference, and measured decomposition |
| In-browser local LLM execution is feasible | WebLLM | Feasibility does not imply acceptable performance on representative devices | Device matrix: load time, memory, time-to-first-token, tokens/s, energy if possible, and task success |
| Canonical hashes can witness equivalent normalized outputs | RFC 8785 motivates deterministic JSON for repeatable hashes | Equal digests are not a mathematical proof of grammar isomorphism; the repository is not automatically JCS-compliant | Define the exact canonicalization contract, test it independently, and call hashes witnesses rather than proofs |

## 3. Detailed literature review

The “direction” labels below mean **supporting**, **challenging**, or **mixed** relative to the project hypotheses. A supporting paper motivates a hypothesis; it does not prove the hypothesis for Strata.

### 3.1 Code naturalness, lexical priors, and semantics-preserving changes

#### 1. Hindle et al. (2012), “On the Naturalness of Software”

- **Source:** [author copy and publication record](https://softwareprocess.es/homepage/papers/2012-hindle12012icse/) · ICSE 2012 · DOI 10.1109/ICSE.2012.6227135.
- **Claim:** Software is highly repetitive and statistically predictable, so language-model methods can capture regularities in code.
- **Direction:** **Supporting background** for H5. If source code has a learnable surface distribution, replacing familiar terminal spellings can move examples away from that distribution.
- **Related part:** The entropy/predictability argument, especially the comparison between code and natural language.
- **How to use it:** Open the related-work section with this as the foundation for “pretraining proximity.” Then explain that alien syntax asks a narrower causal question: what happens when grammar and denotation are held fixed while surface tokens change?
- **Limitation:** The paper predates transformers and does not test instruction-following LLMs or bijective grammar transformations.
- **Read?** **Yes—essential.** Read the introduction, empirical entropy results, and threats/limitations.

#### 2. Allamanis et al. (2018), “A Survey of Machine Learning for Big Code and Naturalness”

- **Source:** [open institutional copy](https://discovery.ucl.ac.uk/id/eprint/10060012/) · ACM Computing Surveys 51(4) · DOI 10.1145/3212695.
- **Claim:** Statistical regularities in large code corpora support many software-engineering tasks, but programming languages differ from natural language through formal syntax, semantics, and identifiers.
- **Direction:** **Supporting and framing** for H5/H7.
- **Related part:** The taxonomy of models of code, the role of identifiers, and the separation of code syntax from semantics.
- **How to use it:** Use it to define the intellectual area and to avoid claiming that code is simply natural language. It supports the need to control formal structure while manipulating surface statistics.
- **Limitation:** It surveys pre-LLM work and cannot validate the current experiment.
- **Read?** **Yes—essential reference work.** Read selectively rather than cover to cover.

#### 3. Wang et al. (2021), “CodeT5: Identifier-aware Unified Pre-trained Encoder–Decoder Models”

- **Source:** [ACL Anthology](https://aclanthology.org/2021.emnlp-main.685/) · EMNLP 2021 · DOI 10.18653/v1/2021.emnlp-main.685.
- **Claim:** Explicit identifier-aware pretraining and bimodal code/comment objectives improve code understanding and generation; developer-assigned identifiers carry useful semantic information.
- **Direction:** **Supporting, with an important qualification.** It supports the idea that lexical choices matter, but identifiers normally communicate intended meaning whereas alien syntax deliberately changes fixed terminals.
- **Related part:** Identifier tagging, masked-identifier recovery, and NL–code alignment.
- **How to use it:** Cite it when motivating why terminal spellings may provide shortcuts or priors. State clearly that the intervention is not ordinary identifier renaming.
- **Limitation:** Its gains could reflect genuine semantic information in good names, not undesirable memorized bias.
- **Read?** **Yes.** Focus on the pretraining objectives and ablations.

#### 4. Miceli-Barone et al. (2023), “The Larger They Are, the Harder They Fail”

- **Source:** [ACL paper](https://aclanthology.org/2023.findings-acl.19/) · Findings of ACL 2023 · [arXiv record](https://arxiv.org/abs/2305.15507).
- **Claim:** When Python built-in identifiers are swapped, LMs often fail to respect the new meanings; some larger models become more confident in wrong predictions.
- **Direction:** **Strongly supporting** H5 and especially H6's interference mechanism; **challenging** any claim that scale alone yields abstract program understanding.
- **Related part:** The construction of meaning-swapped identifiers, inverse-scaling results, and confidence analysis.
- **How to use it:** Present alpha as a DSL-level analogue: familiar tokens remain, but their learned associations conflict with the supplied mapping. Compare error types and model-size trends, not just aggregate accuracy.
- **Limitation:** Python built-ins have far stronger pretrained associations and much richer semantics than 3DOM terminals.
- **Read?** **Yes—highest priority.** It is the closest conceptual precedent for alpha.

#### 5. Wang et al. (2023), “ReCode: Robustness Evaluation of Code Generation Models”

- **Source:** [ACL Anthology](https://aclanthology.org/2023.acl-long.773/) · ACL 2023 · DOI 10.18653/v1/2023.acl-long.773.
- **Claim:** Code-generation models are brittle under more than 30 largely semantics-preserving transformations to docstrings, names, syntax, and formatting; syntax perturbations cause the greatest sensitivity in their tests.
- **Direction:** **Strongly supporting** H5/H7.
- **Related part:** Transformation taxonomy, human validation that perturbations preserve meaning, and worst-case robustness metrics.
- **How to use it:** Adopt its discipline: validate transformations, report clean and perturbed performance jointly, and report transformation-specific robustness rather than one pooled score.
- **Limitation:** ReCode changes natural prompts and general-purpose code rather than a fully generated DSL with a shared IR.
- **Read?** **Yes—highest priority.** It supplies both related work and evaluation design.

#### 6. Maveli et al. (2025), “What Can Large Language Models Capture about Code Functional Equivalence?”

- **Source:** [ACL Anthology](https://aclanthology.org/2025.findings-naacl.382/) · Findings of NAACL 2025 · DOI 10.18653/v1/2025.findings-naacl.382.
- **Claim:** On SeqCoBench's semantics-preserving and semantics-changing transformations, the gap between Code-LLMs and classical matching scores is small, raising doubts about deep functional understanding.
- **Direction:** **Supporting** the need for H7-style controlled probes and **challenging** broad claims that success implies semantic understanding.
- **Related part:** The paired transformation design and distinction between equivalent and non-equivalent transformations.
- **How to use it:** Cite it to justify evaluating invariance and equivariance directly. Use it as a warning not to call correct output “understanding” without stronger evidence.
- **Limitation:** Equivalence classification differs from natural-language-to-DSL generation.
- **Read?** **Yes.** Read methods, transformations, and error analysis.

#### 7. Jain et al. (2021), “Contrastive Code Representation Learning”

- **Source:** [ACL Anthology](https://aclanthology.org/2021.emnlp-main.482/) · EMNLP 2021 · DOI 10.18653/v1/2021.emnlp-main.482.
- **Claim:** Reconstruction-trained code representations are sensitive to semantics-preserving edits; contrastive training on compiler-generated variants substantially improves adversarial robustness and some ordinary tasks.
- **Direction:** **Mixed.** It supports the diagnosis of surface sensitivity, but challenges any claim that such sensitivity is inevitable.
- **Related part:** Compiler-generated transformations and the robustness-versus-natural-accuracy result.
- **How to use it:** Put it in the counterevidence paragraph: alien-syntax effects may diagnose current pretrained models, while augmentation or contrastive objectives may reduce the effect.
- **Limitation:** It studies representation learning and downstream tasks, not instruction-tuned generation.
- **Read?** **Yes.** It is the cleanest constructive counterpoint.

#### 8. Li et al. (2022), “Semantic-Preserving Adversarial Code Comprehension”

- **Source:** [ACL Anthology](https://aclanthology.org/2022.coling-1.267/) · COLING 2022.
- **Claim:** The SPACE method trains code models against worst-case semantics-preserving embedding perturbations and improves both adversarial robustness and ordinary task performance.
- **Direction:** **Challenging/constructive counterevidence** for H5 as a universal statement.
- **Related part:** Robustness training under transformations intended not to change program meaning.
- **How to use it:** Explain that the scientific contribution is a probe and benchmark, not a claim that models can never become invariant to surface form.
- **Limitation:** Continuous embedding attacks are not the same intervention as replacing grammar terminals.
- **Read?** **Read selectively.** Useful for the counterargument and future-work section.

#### 9. Karampatsis et al. (2020), “Big Code ≠ Big Vocabulary”

- **Source:** [official ICSE program and abstract](https://conf.researchr.org/details/icse-2020/icse-2020-papers/57/Big-Code-Big-Vocabulary-Open-Vocabulary-Models-for-Source-code) · ICSE 2020 · DOI 10.1145/3377811.3380342.
- **Claim:** Identifier growth produces severe vocabulary and out-of-vocabulary problems for code models; BPE-based open-vocabulary models scale better across a corpus of 13,362 projects.
- **Direction:** **Strongly supporting** the tokenization-control requirement and **challenging** naive claims that equal character length means equal model difficulty.
- **Related part:** Vocabulary modeling choices, BPE, and identifier novelty.
- **How to use it:** Cite it when explaining why beta's character parity but 40% token overhead is a confound rather than a cosmetic issue.
- **Limitation:** The models and tasks predate modern instruction-tuned LLMs.
- **Read?** **Yes.** Read the vocabulary analysis and model comparison.

### 3.2 Tokenization as a confound and outcome

#### 10. Rust et al. (2021), “How Good Is Your Tokenizer?”

- **Source:** [ACL Anthology](https://aclanthology.org/2021.acl-long.243/) · ACL-IJCNLP 2021 · DOI 10.18653/v1/2021.acl-long.243.
- **Claim:** In controlled multilingual experiments, tokenizer specialization matters alongside pretraining-data size; replacing a multilingual tokenizer with a monolingual one improves downstream performance for almost every tested language/task.
- **Direction:** **Strongly challenging** an alien-syntax experiment that does not match tokenization.
- **Related part:** Controlled separation of tokenizer and data effects.
- **How to use it:** Justify fertility as a design constraint and report tokenizer statistics as first-class experimental variables, not appendix trivia.
- **Limitation:** Human-language multilinguality is not identical to an artificial programming lexicon.
- **Read?** **Yes—essential methods citation.**

#### 11. Ahia et al. (2023), “Do All Languages Cost the Same?”

- **Source:** [ACL Anthology](https://aclanthology.org/2023.emnlp-main.614/) · EMNLP 2023.
- **Claim:** Commercial LM tokenizers encode equivalent information with substantially different token counts across languages, affecting monetary cost and usable context.
- **Direction:** **Supporting** the project's decision to measure token cost and **challenging** beta/gamma in their current form.
- **Related part:** Cross-tokenizer cost analysis and the distinction between linguistic content and encoded length.
- **How to use it:** Explain why matched strings or matched UTF-8 bytes do not create matched model inputs. Extend the rationale from human languages to artificial lexicons cautiously.
- **Limitation:** It studies translated natural-language content, not code generation or NLL causality.
- **Read?** **Yes.** The methods are useful; the fairness framing is secondary here.

#### 12. Petrov et al. (2023), “Language Model Tokenizers Introduce Unfairness Between Languages”

- **Source:** [OpenReview paper](https://openreview.net/forum?id=Pj4YYuxTq9) · ICML Deployable Generative AI workshop 2023.
- **Claim:** Across 17 tokenizers, encoding-length disparities can be extreme and affect cost, latency, and context capacity before the model is invoked.
- **Direction:** **Supporting the control variable; opposing the current gamma arm as a clean causal test.**
- **Related part:** Unicode/byte-level results and encoding-length comparisons.
- **How to use it:** Cite it alongside the repository's observation that gamma's multibyte glyphs fragment heavily. Use it to motivate reporting tokens, UTF-8 bytes, and characters separately.
- **Limitation:** Workshop evidence and natural-language data; it does not show that higher fertility alone causes lower task accuracy.
- **Read?** **Read selectively.**

### 3.3 Prompt form, labels, and in-context learning

#### 13. Min et al. (2022), “Rethinking the Role of Demonstrations”

- **Source:** [ACL Anthology](https://aclanthology.org/2022.emnlp-main.759/) · EMNLP 2022 · DOI 10.18653/v1/2022.emnlp-main.759.
- **Claim:** On their classification and multiple-choice tasks, replacing demonstration labels with random labels often barely hurts; label space, input distribution, and sequence format can matter more than the correct input–label mapping.
- **Direction:** **Challenging** a simplistic claim that familiar token meanings directly determine all in-context behavior; **supporting** careful controls over format and demonstrations.
- **Related part:** Random-label ablations and decomposition of what examples communicate.
- **How to use it:** State a rival explanation: model differences may arise from format learning, demonstrations, or output-space exposure rather than semantic associations of individual terminals.
- **Limitation:** Classification labels are not compositional programming-language terminals.
- **Read?** **Yes.** It is important counterevidence.

#### 14. Webson and Pavlick (2022), “Do Prompt-Based Models Really Understand the Meaning of Their Prompts?”

- **Source:** [ACL Anthology](https://aclanthology.org/2022.naacl-main.167/) · NAACL 2022 · DOI 10.18653/v1/2022.naacl-main.167.
- **Claim:** Models can perform well with irrelevant or misleading prompts, casting doubt on human-like interpretations of prompt following.
- **Direction:** **Mixed/challenging.** It reinforces that surface-performance changes are real but warns against treating them as direct evidence of human-like understanding or misunderstanding.
- **Related part:** Irrelevant and misleading prompt conditions across model scales.
- **How to use it:** Use in the construct-validity section. Describe alien-syntax outcomes operationally—likelihood, validity, and execution—not as proof of comprehension.
- **Limitation:** Natural-language inference prompts are far removed from executable DSLs.
- **Read?** **Yes, selectively.** Read the experimental conditions and discussion.

#### 15. Lu et al. (2022), “Fantastically Ordered Prompts and Where to Find Them”

- **Source:** [ACL Anthology](https://aclanthology.org/2022.acl-long.556/) · ACL 2022 · DOI 10.18653/v1/2022.acl-long.556.
- **Claim:** Few-shot example order can move performance from near state of the art to near random, and good orders do not reliably transfer between models.
- **Direction:** **Challenging unless controlled.** Prompt order is an alternative cause of any measured difference between lexicons.
- **Related part:** Cross-model order sensitivity and entropy-based prompt selection.
- **How to use it:** Require identical demonstration order, semantic examples, decoding parameters, and seeds across paired conditions; ideally rotate or randomize order and model it statistically.
- **Limitation:** The result is from text classification rather than code generation.
- **Read?** **Yes for experimental design.**

### 3.4 Grammar-aware generation and executable semantic parsing

#### 16. Yin and Neubig (2017), “A Syntactic Neural Model for General-Purpose Code Generation”

- **Source:** [ACL Anthology](https://aclanthology.org/P17-1041/) · ACL 2017 · DOI 10.18653/v1/P17-1041.
- **Claim:** Explicitly modeling target-language grammar improves natural-language-to-code generation over treating code as unconstrained text.
- **Direction:** **Supporting** H1/H2 and the grammar-first architecture.
- **Related part:** Grammar-driven AST action generation.
- **How to use it:** Establish the older neural-code-generation lineage: syntax is known structure and need not be relearned entirely from samples.
- **Limitation:** This is a trained architecture, whereas Strata emphasizes stock models and host scaffolding.
- **Read?** **Yes—foundational.**

#### 17. Shin et al. (2021), “Constrained Language Models Yield Few-Shot Semantic Parsers”

- **Source:** [ACL Anthology](https://aclanthology.org/2021.emnlp-main.608/) · EMNLP 2021 · DOI 10.18653/v1/2021.emnlp-main.608.
- **Claim:** An LM can map user input into a controlled English-like sublanguage, which a synchronous grammar then maps to meaning representations; this gives effective few-shot semantic parsers with little task data.
- **Direction:** **Strongly supporting** H1/H2, but also a direct novelty challenge.
- **Related part:** Controlled sublanguage, grammar-constrained search, and rapid bootstrapping.
- **How to use it:** Treat this as a closest architectural ancestor. Explain Strata's distinct domain and contribution: live 3D scene selection, deterministic canonical IR, host-resolved scene context, undo/versioning, and on-device size/decomposition measurements.
- **Limitation:** It does not study 3D editing or browser-local models.
- **Read?** **Yes—highest priority.** A paper that ignores it will look under-researched.

#### 18. Scholak et al. (2021), “PICARD”

- **Source:** [ACL Anthology](https://aclanthology.org/2021.emnlp-main.779/) · EMNLP 2021 · DOI 10.18653/v1/2021.emnlp-main.779.
- **Claim:** Incremental parsing can reject inadmissible tokens during decoding and substantially improve text-to-SQL systems by preventing invalid continuations.
- **Direction:** **Supporting** grammar-constrained decoding as a next scaffold.
- **Related part:** Incremental parser integration and separation between model probabilities and admissible language continuations.
- **How to use it:** Cite when describing the not-yet-wired constrained-decoding condition. Do not use it to explain current gains if the current system only injects selectors or resolves them host-side.
- **Limitation:** SQL constraints and a fine-tuned T5 setting differ from Strata.
- **Read?** **Yes.**

#### 19. Geng et al. (2023), “Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning”

- **Source:** [ACL Anthology](https://aclanthology.org/2023.emnlp-main.674/) · EMNLP 2023 · DOI 10.18653/v1/2023.emnlp-main.674.
- **Claim:** Formal and input-dependent grammars can guarantee output structure and can outperform unconstrained or task-specific fine-tuned models on several structured tasks.
- **Direction:** **Strongly supporting** H1/H2 and model-agnostic scaffolding.
- **Related part:** Input-dependent grammars are particularly relevant to scene-dependent valid selectors and arguments.
- **How to use it:** Position the scene graph as a source of per-input constraints. Compare static 3DOM grammar constraints with dynamic host-generated selector domains.
- **Limitation:** It does not show that grammar constraints recover correct user intent; validity and semantics remain distinct.
- **Read?** **Yes—highest priority.**

#### 20. Beurer-Kellner et al. (2024), “Guiding LLMs the Right Way”

- **Source:** [PMLR](https://proceedings.mlr.press/v235/beurer-kellner24a.html) · ICML 2024.
- **Claim:** Constrained generation can impose formal languages efficiently, but implementations that misalign grammar constraints with subword vocabularies may hurt task accuracy; DOMINO aligns constraints to subwords with little overhead in their evaluation.
- **Direction:** **Mixed and highly relevant.** It supports constrained decoding but directly warns that the alien-syntax tokenizer problem can interact with the decoder.
- **Related part:** Tokenizer–grammar alignment, invasiveness, accuracy, and runtime overhead.
- **How to use it:** Motivate a four-part constrained-decoding report: validity, semantic accuracy, latency, and tokenization interaction. Never assume that a grammar mask is performance-neutral.
- **Limitation:** It focuses on decoding infrastructure rather than HCI or 3D tasks.
- **Read?** **Yes—highest priority before implementing constrained decoding.**

#### 21. Stengel-Eskin and Van Durme (2023), “Calibrated Interpretation”

- **Source:** [ACL Anthology](https://aclanthology.org/2023.tacl-1.69/) · TACL 2023 · DOI 10.1162/tacl_a_00598.
- **Claim:** Confidence calibration varies across sequence-generation models and semantic-parsing datasets; executable actions make calibration a safety concern.
- **Direction:** **Challenging an accuracy-only evaluation** and supporting a safer UI.
- **Related part:** Confidence/error calibration for natural-language-to-program translation.
- **How to use it:** Add calibration or selective-execution evaluation: at a confidence threshold, what fraction of actions is accepted and what is the error rate? Use low confidence to request clarification rather than mutate the scene.
- **Limitation:** Model token probabilities may be unavailable or incomparable for some hosted APIs.
- **Read?** **Yes if the paper makes safety, trust, or production claims.**

### 3.5 Evaluation methodology

#### 22. Ribeiro et al. (2020), “Beyond Accuracy: Behavioral Testing of NLP Models with CheckList”

- **Source:** [ACL Anthology](https://aclanthology.org/2020.acl-main.442/) · ACL 2020 · DOI 10.18653/v1/2020.acl-main.442.
- **Claim:** Held-out accuracy can hide important model failures; a matrix of capabilities and behavioral test types reveals actionable bugs.
- **Direction:** **Supporting** the repository's task-by-scaffolding matrix and invariant tests; **challenging** any conclusion from one aggregate score.
- **Related part:** Minimum-functionality, invariance, and directional-expectation tests.
- **How to use it:** Recast fixtures into named capabilities: operation choice, argument extraction, labeling, decomposition, selector resolution, ambiguity, negation, scope, and multi-operation order. Publish the matrix and individual failures.
- **Limitation:** Synthetic behavioral tests do not replace ecological or human evaluation.
- **Read?** **Yes—essential evaluation citation.**

#### 23. Koehn (2004), “Statistical Significance Tests for Machine Translation Evaluation”

- **Source:** [author PDF](https://people.csail.mit.edu/people/koehn/publications/bootstrap2004.pdf) · EMNLP 2004.
- **Claim:** Bootstrap resampling can estimate uncertainty and significance for paired system comparisons when analytical metric distributions are unavailable.
- **Direction:** **Supporting the paired bootstrap method**, while warning that the estimand and resampling unit must match the research question.
- **Related part:** Paired resampling of test items and confidence/significance estimation.
- **How to use it:** Resample semantic program pairs, not individual tokens; preserve within-item pairing across lexicons and conditions. State the statistic explicitly, such as the mean per-program \(\Delta\)NLL/character or accuracy delta.
- **Limitation:** BLEU and machine translation differ from DSL NLL; the method must be adapted transparently.
- **Read?** **Yes, especially because the repository already found and fixed a bootstrap-estimand defect.**

#### 24. RFC 8785, “JSON Canonicalization Scheme”

- **Source:** [RFC Editor](https://www.rfc-editor.org/rfc/rfc8785.html) · 2020 · DOI 10.17487/RFC8785.
- **Claim:** Repeatable hashing/signing requires an invariant JSON representation with specified primitive serialization, property ordering, and UTF-8 behavior.
- **Direction:** **Supporting** canonical IR serialization, but also a specification challenge.
- **Related part:** Deterministic property sorting, number serialization, string preservation, and UTF-8 generation.
- **How to use it:** Either state that the project defines its own narrower C0–C8 canonicalization or implement and test JCS conformance. Do not casually call Python `json.dumps(sort_keys=True)` “JCS.” Note that non-finite values are outside valid JSON and that negative zero requires explicit treatment.
- **Limitation:** Canonical JSON only establishes stable bytes for the same normalized data; it does not prove two grammars isomorphic.
- **Read?** **Yes for the artifact/method paper; optional for a user-study-focused HCI paper.**

### 3.6 Human–AI interaction and decomposition

#### 25. Wu et al. (2022), “AI Chains”

- **Source:** [author project page](https://idl.uw.edu/papers/ai-chains) and [author PDF](https://www.cs.cmu.edu/~sherryw/assets/pubs/2022-chain.pdf) · CHI 2022 · DOI 10.1145/3491102.3517582.
- **Claim:** Chaining an LLM task into editable modules improved outcome quality and increased perceived transparency, controllability, and collaboration in their user study; users debugged subcomponents.
- **Direction:** **Strongly supporting** H1/H3.
- **Related part:** Modular decomposition, intermediate-state inspection, and user correction.
- **How to use it:** Compare Strata's deterministic stages to chain primitives. Design the user study to measure discoverability of failures, correction time, successful recovery, and perceived control—not only final accuracy.
- **Limitation:** AI Chains operates on prompt workflows, not typed scene mutations, and does not establish that every decomposition helps.
- **Read?** **Yes—highest priority for an HCI submission.**

#### 26. Amershi et al. (2019), “Guidelines for Human–AI Interaction”

- **Source:** [Microsoft Research publication page](https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/) · CHI 2019 · DOI 10.1145/3290605.3300233.
- **Claim:** Eighteen human-AI design guidelines were synthesized and validated through multiple rounds, including 49 practitioners evaluating 20 AI products.
- **Direction:** **Supporting** H3's design rationale; **challenging** an interface that hides capability limits or makes errors hard to correct.
- **Related part:** Communicate capabilities and limitations, support efficient correction, provide controls, and convey consequences.
- **How to use it:** Turn relevant guidelines into design requirements and study measures. Show intended targets before execution, preview the operation, make errors undoable, and distinguish parser/validation/model failures.
- **Limitation:** Guidelines are not evidence that Strata satisfies them; that requires inspection and user evaluation.
- **Read?** **Yes—essential for CHI, DIS, or IUI framing.**

### 3.7 Natural-language 3D authoring and scene editing

#### 27. Coyne and Sproat (2001), “WordsEye”

- **Source:** [author PDF](https://www.cs.columbia.edu/~coyne/papers/wordseye_siggraph.pdf) · SIGGRAPH 2001 · DOI 10.1145/383259.383316.
- **Claim:** Natural language can be converted into representative 3D scenes using linguistic analysis, a database of models/poses, and depiction rules.
- **Direction:** **Supporting the value of language-based 3D authoring**, but **challenging novelty claims** about the basic idea.
- **Related part:** Separation between language interpretation, semantic representation, and low-level depiction.
- **How to use it:** Use as the historical anchor. Contrast scene creation from descriptions with Strata's selection and mutation of an existing, structured scene.
- **Limitation:** It is rule- and asset-database-driven, not LLM-based or focused on reversible editing.
- **Read?** **Yes—essential historical citation.**

#### 28. Chang et al. (2014/2017), “SceneSeer: 3D Scene Design with Natural Language”

- **Source:** [paper record](https://arxiv.org/abs/1703.00050); related [ACL workshop paper on interactive spatial learning](https://aclanthology.org/W14-3102/).
- **Claim:** Users can iteratively design 3D scenes through natural language, with learned spatial knowledge supporting object arrangement and later corrections.
- **Direction:** **Supporting** iterative language-based authoring and **challenging** claims that conversational scene editing is new.
- **Related part:** Iteration, spatial relations, object insertion, and user corrections.
- **How to use it:** Distinguish Strata's core operation: address existing graph nodes with selectors and apply deterministic mutations rather than synthesize complete layouts from text.
- **Limitation:** Publication versions and dates should be normalized carefully in the final bibliography; cite the version actually read.
- **Read?** **Yes.** Focus on interaction workflow and evaluation.

#### 29. De La Torre et al. (2024), “LLMR: Real-time Prompting of Interactive Worlds using Large Language Models”

- **Source:** [Microsoft Research publication page](https://www.microsoft.com/en-us/research/?p=1030200) · CHI 2024 · DOI 10.1145/3613904.3642579.
- **Claim:** A modular LLM framework using scene understanding, planning, self-debugging, and memory reduced average error relative to simpler GPT-4 baselines; an N=11 usability study reported positive experiences.
- **Direction:** **Strongly supporting** modular 3D/world authoring, but it is the closest current system-level novelty challenge.
- **Related part:** Ablation of modules, creation/modification tasks, Unity integration, and the usability study.
- **How to use it:** Compare architecture and task taxonomy directly. Strata should emphasize deterministic selectors/IR, model-size sufficiency, browser-local deployment, undo/versioning, and controlled host-share dose response.
- **Limitation:** The sample is small, it uses Unity and GPT-4-centered modules, and it addresses mixed reality rather than the Three.js editor.
- **Read?** **Yes—highest priority.** Reproduce its evaluation table structure where useful.

#### 30. Sun et al. (2024), “3D-GPT: Procedural 3D Modeling with Large Language Models”

- **Source:** [OpenReview paper](https://openreview.net/pdf/462ce05fe1aeb7ccf1141155c73a3b770ebb344f.pdf) and [arXiv record](https://arxiv.org/abs/2310.12945).
- **Claim:** Multiple specialized LLM agents can decompose natural-language requests and drive procedural Blender modeling.
- **Direction:** **Supporting** decomposition and language-to-3D workflows; **challenging** a broad “LLM controls 3D software” novelty claim.
- **Related part:** Task dispatch, conceptualization, modeling agents, and editable procedural outputs.
- **How to use it:** Contrast agentic procedural creation with a narrow, verifiable edit language. A useful argument is that Strata intentionally reduces agent freedom to gain determinism, local feasibility, and testability.
- **Limitation:** Evidence is primarily system demonstrations; it does not isolate host-side decomposition or tiny-model sufficiency.
- **Read?** **Yes, but after LLMR and SceneSeer.**

### 3.8 Browser-local inference and graph-selection foundations

#### 31. Ruan et al. (2024), “WebLLM: A High-Performance In-Browser LLM Inference Engine”

- **Source:** [arXiv paper and authors' code link](https://arxiv.org/abs/2412.15803); [official project repository](https://github.com/mlc-ai/web-llm).
- **Claim:** WebGPU, WebAssembly, TVM, and MLC-LLM make entirely in-browser LLM inference practical; the reported evaluation reaches up to 80% of native performance on the same device.
- **Direction:** **Supporting technical feasibility** for H4.
- **Related part:** Browser architecture, compilation, API integration, benchmark design, and device support.
- **How to use it:** Cite it as infrastructure enabling Strata, not as evidence that Strata itself is fast or universally deployable. Report exact browser, GPU, quantization, model, memory, cold-load, and warm-inference conditions.
- **Limitation:** It is a systems/preprint result, and “up to” performance is not a guarantee for the project's target users or models.
- **Read?** **Yes—essential for the on-device claim.**

#### 32. W3C Selectors Level 4

- **Source:** [W3C working draft](https://www.w3.org/TR/selectors-4/) · 22 January 2026.
- **Claim:** Selectors are predicates over elements in a tree and support filtering nodes by structural and local properties.
- **Direction:** **Supporting the interface lineage**, but **challenging any claim that selector-based addressing is itself new.**
- **Related part:** Compound selectors, combinators, tree matching, specificity only if Strata implements an analogue.
- **How to use it:** State that 3DOM deliberately borrows a familiar tree-query interaction style and then adapts it to a Three.js scene graph and edit operations.
- **Limitation:** This is a working specification, not an empirical paper, and DOM trees differ from 3D scene graphs.
- **Read?** **Read the selector model and implemented subset; do not read the entire specification.**

#### 33. Francis et al. (2018), “Cypher: An Evolving Query Language for Property Graphs”

- **Source:** [author PDF](https://homepages.inf.ed.ac.uk/pguaglia/papers/sigmod18.pdf) · SIGMOD 2018 · DOI 10.1145/3183713.3190657.
- **Claim:** Cypher is a declarative query language for labeled property graphs with composable graph-pattern matching.
- **Direction:** **Supporting graph-query-language lineage**, not natural-language-to-3D lineage.
- **Related part:** Property-graph model, pattern matching, and language design/evolution.
- **How to use it:** Cite it only when discussing selectors or declarative queries over graphs. The repository README currently groups “Cypher” under “NL-to-3D”; that categorization should be corrected before publication.
- **Limitation:** Cypher is neither a 3D editing system nor a natural-language interface.
- **Read?** **Read selectively.** The introduction and language-design overview are enough.

#### 34. Three.js Scene Graph documentation

- **Source:** [official Three.js manual](https://threejs.org/manual/en/scenegraph.html).
- **Claim:** Three.js represents scenes as hierarchical nodes with local coordinate spaces and parent/child relationships.
- **Direction:** **Supporting technical context**, not a research claim.
- **Related part:** Hierarchical object selection, parent/child effects, and local versus world transformations.
- **How to use it:** Define why selector combinators and host-side resolution are natural for the target representation. Cite a stable Three.js release or archived documentation in the artifact.
- **Limitation:** Documentation establishes API behavior, not novelty or user benefit.
- **Read?** **Yes, briefly.**

## 4. Synthesis: what the literature lets the paper claim

### Strong claims after the planned experiments

If the paired experiments and user evaluation succeed, the paper can reasonably argue:

- A deterministic selector/operation layer can remove a measurable portion of a natural-language 3D editor's model burden.
- Host-resolving scene-dependent references can reduce the model-size sensitivity of that subtask.
- Grammar and canonical IR provide a testable boundary between output validity, denotation, and execution.
- Small, browser-local models can be sufficient for a specified residual task set on specified hardware—not for unrestricted 3D creation.
- Meaning-preserving terminal remapping is a useful probe of model dependence on surface familiarity, provided tokenization and lexical-language equivalence are controlled.

### Claims the present evidence does not support

- **“The hypotheses are proven.”** Literature motivates; only the project's measurements test them, and no finite experiment proves a universal model claim.
- **“Zero training priors.”** Absence from a chosen vocabulary or corpus does not prove absence from pretraining.
- **“The alien grammars are isomorphic because their hashes match.”** Equal canonical hashes on a finite corpus are witnesses; they are not a proof over the entire language.
- **“Gamma changes only spelling.”** The current collision analysis shows different lexical reachability, so gamma is a strict language change under the current lexer.
- **“Beta is matched in difficulty.”** It has equal character length but approximately 40–45% greater token fertility on the measured tokenizers.
- **“Constrained decoding produced the current gains.”** The repository says that constrained decoding is not yet wired into the relevant evaluation.
- **“Strata is usable” or “users prefer it.”** A synthetic fixture suite cannot establish usability, learnability, preference, creative support, or recovery behavior.
- **“Natural language for 3D editing is new.”** WordsEye, SceneSeer, LLMR, and 3D-GPT make that position untenable.
- **“Cypher is prior natural-language-to-3D work.”** It is a property-graph query language.

### The clearest novelty statement

> Strata investigates whether a small, deterministic, selector-based edit language can serve as a verifiable boundary between natural-language intent and a live 3D scene, and whether progressively relocating scene-dependent work from an LLM to the host reduces the model capability needed for reliable, local interaction. A companion alien-syntax method probes how much measured performance depends on the familiar surface form of that otherwise fixed language.

This statement is narrower than “an LLM edits 3D scenes,” but it is more defensible and better differentiated from prior work.

## 5. Recommended reading order

### Read before writing the related-work section

1. Shin et al., **Constrained Language Models Yield Few-Shot Semantic Parsers**.
2. De La Torre et al., **LLMR**.
3. Miceli-Barone et al., **Identifier Swaps**.
4. Wang et al., **ReCode**.
5. Geng et al., **Grammar-Constrained Decoding**.
6. Wu et al., **AI Chains**.
7. Hindle et al., **Naturalness of Software**.
8. Rust et al., **How Good Is Your Tokenizer?**

### Read while redesigning the experiment

1. Beurer-Kellner et al., **DOMINO**.
2. Min et al., **Role of Demonstrations**.
3. Lu et al., **Prompt Order Sensitivity**.
4. Ribeiro et al., **CheckList**.
5. Koehn, **Paired Bootstrap**.
6. Jain et al., **ContraCode**.

### Read for historical and interface positioning

1. WordsEye.
2. SceneSeer.
3. 3D-GPT.
4. Amershi et al.'s human-AI guidelines.
5. W3C Selectors and the Three.js scene-graph manual.

## 6. Experiments reviewers are likely to request

### For the Strata paper

- **A complete causal matrix:** identical fixtures across bare, selector-injected, grammar-constrained, host-resolved, and combined conditions. Do not label conditions with unavailable mechanisms.
- **Multiple model families:** current results from several sizes of one family mainly measure scale. Add at least one other open family and separate base-model likelihood tests from instruct-model task tests.
- **Repeated stochastic runs:** if decoding is not deterministic, publish seeds and report item-paired intervals. If temperature is zero, still report API/model revision and investigate remaining nondeterminism.
- **Semantic layers:** report parse validity, IR-schema validity, canonical IR exact match, target-node resolution, execution success, and final scene-state correctness separately.
- **Real scenes:** supplement synthetic fixtures with heterogeneous imported scenes containing duplicate names, unlabeled objects, deep nesting, instancing, ambiguous descriptions, and transforms inherited through parents.
- **Human study:** compare at least manual UI, raw chat/code generation, and Strata-assisted editing. Measure task completion, time, correction/recovery, unintended mutations, undo usage, workload, perceived control, and understanding of the pending action.
- **On-device systems results:** cold model-download/load time, peak memory, browser/GPU coverage, time to first token, generation rate, interaction latency, and failure/fallback behavior.
- **Safety and reversibility:** preview/confirm conditions for destructive or broad selectors; measure false execution and recovery, not only model text accuracy.

### For the alien-syntax paper

- **Repair the treatment construction before task evaluation:** generate new beta-like spellings that meet the fertility band for every preregistered tokenizer or redefine the estimand transparently before observing \(\Delta\)NLL.
- **Drop or repair gamma as a primary isomorphic arm:** lexical class and concatenation reachability must match, not just terminal-table bijection and parser acceptance on a finite corpus.
- **Measure the primary outcome:** per-program \(\Delta\)NLL/character with paired confidence intervals, plus NLL/token as a diagnostic—not as an interchangeable estimate.
- **Use negative and null controls:** identity-to-identity reproducibility, alternative bijections within each treatment family, and a length/tokenization perturbation that should affect cost but not familiarity in the same way.
- **Avoid one-map inference:** one alpha and one beta conflate treatment family with the particular chosen mapping. Sample many valid maps or justify a fixed map through a precommitted selection algorithm.
- **Control prompt exposure:** identical semantic demonstrations and order; no accidental original/alien token clues; report whether the grammar, translation table, examples, or only task instructions are visible to the model.
- **Test both likelihood and behavior:** base-model prior strength and instruction-model generation answer different questions. Do not infer one from the other.
- **Analyze errors mechanistically:** familiar-token reversion, invalid terminal, valid-but-wrong operation, selector error, argument error, extra operation, and failure to terminate.
- **Release the full artifact:** grammar templates, phi maps, generated corpora, tokenizer revisions, model hashes/revisions, raw token-level log probabilities, bootstrap code, seeds, environment, and checksums.

## 7. Venue strategy and current requirements

### Recommendation at a glance

| Rank | Venue/path | Best version of the contribution | Current recommendation |
|---:|---|---|---|
| 1 | **DIS 2027 Papers — Artifacts and Systems** | Strata system + user study + design implications | **Best realistic full-paper target** |
| 2 | **EICS 2027 Full Paper or Technical Note** | Language/IR architecture, verification, reproducible engineering | **Best fit if the technical system is stronger than the user study** |
| 3 | **CHI 2027 Poster** | Honest work-in-progress after core experiment | **Realistic feedback path; not a substitute for a full paper** |
| 4 | **OOPSLA 2027** | Alien-syntax methodology with a real PL contribution and rigorous artifact | **Conditional; current application paper is out of scope** |
| 5 | **CHI 2027 Paper** | Mature Strata HCI paper with human evidence | **Do not rush: deadline is tomorrow and required evidence is incomplete** |
| 6 | **PLDI 2027** | New language/constraint/verification technique | **Long shot; wait for the full CFP and submit only with clear PL novelty** |

### 7.1 ACM DIS 2027 — recommended primary target

- **Official call:** [DIS 2027 Call for Papers](https://dis.acm.org/2027/call-for-papers/).
- **Fit:** Strong for a paper whose contribution is the designed artifact, progressive host decomposition, interaction model, and lessons for controllable creative AI. Select **Artifacts and Systems**; the [subcommittee description](https://dis.acm.org/2027/selecting-a-subcommittee/) explicitly covers designed and evaluated interactive systems, including AR/VR.
- **Deadlines (AoE):** title/abstract **11 January 2027**; paper/pictorial **18 January 2027**; notification **19 March 2027**.
- **Length:** no fixed page limit; typical paper is approximately **7,000–8,000 words**, excluding references, captions, and appendices. Submissions above **12,000** or below **4,000** words may be desk-rejected.
- **Format:** ACM Primary Article Template, single-column review PDF; LaTeX uses `\documentclass[manuscript,review,anonymous]{acmart}`.
- **Review:** anonymized submission through PCS. Paper must clearly state an HCI/design contribution, be grounded in DIS/HCI literature, describe methods transparently, and provide data sufficient for its claims. The 2027 call includes an assisted desk-reject stage for grossly inadequate positioning, methods, or evidence.
- **Other requirements:** original/non-concurrent work; follow ACM human-participant policy and accessibility guidance; all authors should obtain ORCID. Accepted papers use TAPS and ACM's open-access model.
- **What must be ready:** a stable working system, the completed model/scaffolding evaluation, and preferably a human study. A purely internal synthetic benchmark is unlikely to carry the HCI/design contribution.
- **Recommended framing:** “Designing a deterministic boundary for local language-model assistance in 3D scene editing.” Keep alien syntax as a methods subsection or a separate paper unless it directly answers an HCI question.

### 7.2 ACM EICS 2027 — recommended technical alternative

- **Official call:** [EICS 2027 Full Papers and Technical Notes](https://eics.acm.org/2027/contributions/full-papers.html); [conference scope](https://eics.acm.org/2027/index.html).
- **Fit:** Excellent for the architecture: formal grammar, canonical IR, host/model boundary, validation, reproducibility, and engineering an AI-embedded interactive system. The call explicitly includes software architectures, formal methods, verification/validation, VR/AR/MR, and interactive systems embedding AI.
- **Paper types:** **Full Papers** for mature research; **Technical Notes** for focused reproducible system contributions. Technical Notes require an illustrative example but may validate through user studies, simulation, feasibility, or comparison.
- **Deadlines:** The 2027 page states three PACM review rounds but, as of this review date, does **not publish the round dates**. Treat every date as TBA and monitor the official call; do not copy the 2026 dates as if they applied.
- **Length:** no paper or reference limit; length must be proportional to contribution.
- **Format/submission:** ACM TAPS workflow through PCS.
- **Review/anonymity:** double blind between authors and reviewers; Associate Chairs know identities. Remove names/institutions and PDF metadata, leave acknowledgements blank, and cite prior work in the third person.
- **Publication:** accepted articles appear in PACM on Human-Computer Interaction, EICS series, under ACM Open; APC rules may apply if the corresponding author's institution does not participate.
- **What must be ready:** stronger technical validation than the current corpus-only isomorphism evidence—property-based testing or a formal argument, end-to-end execution tests, performance measurements, and a carefully scoped model evaluation.
- **Recommended framing:** “Engineering a typed, canonical, and host-resolved intermediate language for reliable AI-assisted 3D editing.”

### 7.3 CHI 2027 Poster — realistic near-term feedback path

- **Official call:** [CHI 2027 Posters](https://chi2027.acm.org/authors/posters/).
- **Fit:** A concise work-in-progress report on either the decomposition result or the repaired alien-syntax experimental method.
- **Deadline (AoE):** **21 January 2027**; notification **18 February 2027**.
- **Length/format:** up to **4 pages excluding references**, ACM single-column template.
- **Review/anonymity:** anonymous; omit author names, affiliations, and contact information.
- **What must be ready:** one clear contribution, a small number of credible figures/results, limitations, and a precise next study. Do not compress both full stories into four pages.
- **Tradeoff:** Useful for feedback and visibility, but a poster/extended abstract is not the same archival contribution as a full research paper. Check later-venue prior-publication rules before reusing material.

### 7.4 PACMPL/OOPSLA 2027 — only for a genuine programming-languages paper

- **Official call:** [OOPSLA 2027](https://2027.splashcon.org/track/splashoopsla2027).
- **Fit:** Potentially suitable for the alien-syntax transformation, canonical semantics, grammar equivalence, and evaluation methodology **only if** the work advances programming languages. The official FAQ says black-box LLM applications or prompt-engineering papers without a substantial PL angle may be desk-rejected.
- **Deadlines (AoE):** Round 1 **14 October 2026**; Round 2 **7 April 2027**. A Round-1 rejection cannot be resubmitted to Round 2 of the same year.
- **Length/format:** initial submission at most **23 pages** excluding required statements, references, and supplementary material; revision at most 25 pages. Use `\documentclass[acmsmall,screen,review,anonymous]{acmart}`.
- **Review/anonymity:** double blind. Omit authors/institutions, use third-person self-citation, and anonymize supplements.
- **Special requirements:** include a short **Data-Availability Statement** before references. At least one senior author must register as a reserve reviewer unless an exemption applies. Closely related submissions must be disclosed; no concurrent archival review.
- **Artifacts:** not mandatory, but a paper whose claims imply an artifact must explain why none is provided. An artifact is strategically important for this project.
- **What must change first:** repair token matching and gamma, run the primary measurements, introduce a general method or theorem beyond this one DSL, and formally state what equivalence is guaranteed. A finite hash-equality corpus alone is below the likely PL contribution threshold.
- **Recommended framing:** “Semantics-preserving surface-language transformations for measuring lexical priors in neural program synthesis,” not “an alien skin for 3DOM.”

### 7.5 CHI 2027 full papers — ideal field, wrong current timing

- **Official call:** [CHI 2027 Papers](https://chi2027.acm.org/authors/papers/).
- **Fit:** Strong if the main contribution is human-centered 3D editing, control, correction, privacy, and the consequences of host/model decomposition.
- **Deadline (AoE):** **10 September 2026**; reviews 5 November; revise-and-resubmit deadline 3 December; final notification 17 December. The deadline is one day after this review's cut-off.
- **Length:** **5,000–8,000 words encouraged**; abstract at most **150 words**. Above 12,000 words is desk-rejected unless exceptional justification is provided; under 5,000 is treated as a short paper but receives the same process.
- **Format/anonymity:** correct ACM single-column review template; anonymized paper and supplementary materials. The main PDF must stand alone.
- **Author metadata:** all authors must have ORCID, and the PCS DBLP field must contain a profile URL or “n/a.” Author names cannot be added or removed after the deadline.
- **Review responsibility:** authors are subject to CHI's Full Paper Review Responsibility Policy.
- **Recommendation:** **Do not submit the current project merely because the deadline is open.** The missing human study, pending \(\Delta\)NLL, failed alien-syntax controls, and unresolved scope would make a rushed paper fragile. Target DIS/EICS, a CHI poster, or the next CHI cycle.

### 7.6 PLDI 2027 — monitor, but do not plan around it yet

- **Official page:** [PLDI 2027](https://pldi27.sigplan.org/) and [research-paper track](https://pldi27.sigplan.org/track/pldi-2027-papers).
- **Fit:** Only if the contribution becomes a general programming-language, constrained-generation, formal-semantics, compiler, or verification advance. The Strata application and current phi experiment alone are not enough.
- **Deadline (AoE):** **12 November 2026**; author response 16–18 February 2027; notification 4 March; revision 23 March; final acceptance 1 April.
- **Current requirements status:** As of 9 September 2026, the official research-paper track says **“No information available yet”** beyond its double-blind FAQ and dates. Page limit, final template rules, artifact process, and complete scope requirements are therefore TBA.
- **Known anonymity guidance:** double blind; omit names and acknowledgements, remove identifying affiliation information, cite prior work in the third person, and anonymize supplementary material.
- **Recommendation:** Monitor the CFP. Do not infer 2027 rules from earlier PLDI editions, and do not force an HCI contribution into a PL venue.

### 7.7 IUI — best thematic fit in a future cycle, but 2027 is closed

- **Official 2027 call:** [ACM IUI 2027](https://iui.acm.org/2027/call-for-papers/).
- **Fit:** Extremely strong: the call explicitly includes intelligent interfaces for generative AI, intelligent AR/VR, human control, prompt engineering, user steering, model evaluation, and reproducibility.
- **2027 status:** abstract deadline was **13 August 2026** and full paper deadline **20 August 2026**, so new paper submissions are closed.
- **2027 format as a planning baseline only:** single-column anonymous ACM template; variable length with 8,000 words encouraged, and a justification required above 10,000 words; PCS submission; double-blind review; evidence appropriate to claims; human-participant ethics context; optional supplements encouraged.
- **Recommendation:** Watch for IUI 2028 rather than treating the 2027 rules as guaranteed. A future IUI paper should combine computational ablations with a human-centered evaluation, because IUI explicitly expects both aspects.

## 8. Proposed paper structures

### Strata / DIS–EICS paper

1. Problem: unrestricted LLM control is too unconstrained and large-model dependent for local creative tools.
2. Design goals: deterministic core, bounded residual AI, inspectability, reversibility, portability, and local execution.
3. System: selector language, closed operations, canonical IR, host resolver, validation/execution, and optional model.
4. Study 1: scaffold dose-response across model sizes/families and task types.
5. Study 2: end-user editing study with failure recovery and control measures.
6. Systems evaluation: browser/device performance and privacy boundary.
7. Discussion: which work belongs to the host, which remains fuzzy, and when the small model stops being sufficient.

### Alien-syntax / OOPSLA–NLP methods paper

1. Problem: code/DSL model evaluations conflate structural ability, surface familiarity, and tokenization.
2. Method: grammar template plus terminal bijection, canonical shared IR, and formal/empirical invariants.
3. Treatment construction: interference, absence, and matched-token controls sampled from families rather than single maps.
4. Structural validation: lexical-language equivalence, round trip, canonical semantics, and property-based or exhaustive bounded tests.
5. Experiment 1: base-model \(\Delta\)NLL/character with paired uncertainty.
6. Experiment 2: instruction-model task behavior and error categories.
7. Counterfactual training/robustness experiment, if feasible.
8. Limits: no claim of zero priors, complete isomorphism beyond guarantees, or human-like understanding.

## 9. Final recommendation

Prioritize a **DIS 2027 Strata paper** and treat **EICS 2027** as the technical alternative. Complete the causal scaffold matrix, realistic-scene evaluation, on-device measurements, and a user study before submission. Use the alien-syntax work as a careful diagnostic section only if its controls are repaired in time; otherwise develop it as a separate methods paper for OOPSLA or an NLP/code-model venue.

The most urgent research correction is not more writing: it is constructing a tokenization-matched, lexically equivalent alien treatment and running the preregistered \(\Delta\)NLL measurement. The most important Strata addition is not another model: it is human evidence showing that the deterministic boundary improves editing, correction, and control.
