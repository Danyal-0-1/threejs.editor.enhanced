# Literature review and novelty audit: surface priors in prompt-defined DSL generation

**Project:** 3DOM / alien concrete syntaxes  
**Literature-search cutoff:** 23 September 2026  
**Status:** adversarial review; not a publication guarantee  
**Requested output filename:** `litreture_reveiw_1.md` (spelling preserved)

## Scope and an important evidence boundary

This review asks whether the proposed project is new, not merely whether its current results are interesting. It uses the preliminary 3DOM experiments as motivation, but it does **not** treat their exploratory verdict labels as established findings. In particular:

- the behavioral study has only 21 scored generation tasks per condition, one model family, one prompt family, and one deterministic completion per task;
- `alpha`, `beta`, and `gamma` are not tokenization-matched to `identity`; relative Qwen fertility was 1.068, 1.401, and 1.937 respectively;
- `gamma` is not a clean language-isomorphism control because its lexical reachability differs from 3DOM;
- `alpha` jointly changes familiarity and creates misleading familiar meanings;
- bare and scaffolded conditions differ in whether outputs reach the selector decision, so unconditional reversion counts have opportunity bias;
- a semantic-scoring defect can count some extra-operation outputs as correct and must be repaired before the behavioral results are used in a paper; and
- base-checkpoint likelihood and instruction-checkpoint generation answer different questions. Their association is not automatically causal.

The strongest current observation is therefore descriptive: Qwen2.5-Coder base checkpoints assigned higher NLL per character to all three alien surfaces, and Qwen2.5-Coder-Instruct usually produced lower exact-IR accuracy on them, while `beta` was an important counterexample in the 3B condition. That pattern motivates a controlled experiment; it does not yet establish the proposed cause.

---

## 1. Executive verdict

### Direct answer

The **broad original hypothesis is substantially covered**. Prior work already establishes that:

1. models often perform worse when familiar operators, identifiers, words, or formal semantics are reassigned;
2. explicit prompt-local definitions do not always suppress pretrained associations;
3. prior strength predicts some conflict failures;
4. grammar descriptions, examples, and constrained decoding can improve structured generation, but formal validity and semantic correctness are different outcomes;
5. renaming tool schemas toward model-compatible names can improve tool use;
6. tokenization and semantics-preserving code-surface changes can affect performance; and
7. internal components supporting memorized/default and contextual answers can sometimes be localized and causally manipulated.

The strongest broad statement — “LLMs generate DSLs well mainly because they pattern-match familiar syntax rather than reason” — should be abandoned. “Reasoning” and “pattern matching” are not mutually exclusive measurable mechanisms, “mainly” has no defined estimand, and the existing design does not isolate pretraining familiarity from tokenization, prompt interpretation, or language design. PLSemanticsBench already makes the narrower, defensible finding that performance under mutated formal semantics can fall sharply despite supplied rules ([Thimmaiah et al., ICML 2026](https://arxiv.org/abs/2510.03415)).

The **refined behavioral hypothesis is potentially distinct**, but only in a narrow factorial form:

> At an AST-matched output site, does independently increasing the familiar competitor's prior strength and its immediate, competitor-specific syntactic support produce a super-additive increase in reversion, while tokenization, role, semantics, and grammar legality are controlled?

I did not identify a paper in the searched literature that tests that exact two-factor interaction during concrete prompt-defined DSL generation. However, this is a narrow gap. Persistent Priors directly studies prior strength under lexical override. Conflict and Congruency is a close task-specific conceptual and methodological precedent for competition between a short-range default cue and a distant rule in its verbal color task ([Wang, 2026](https://arxiv.org/abs/2606.07555); [Hu et al., 2026](https://arxiv.org/abs/2608.11510)). It substantially preempts novelty for merely proposing that architecture, but it does not establish a universal cross-task mechanism. A paper cannot claim novelty merely for saying “local habits compete with distant instructions.”

The **generic mechanistic hypothesis is already covered**. Prior work has reported short-range/default versus long-range/rule pathways, memory versus context heads, causal head interventions, and residual-stream patching under semantic code conflict. What appears open is their exact realization at a controlled DSL emission site, plus out-of-distribution prediction and a minimal surface repair.

### What exact conjunction may remain novel?

Within the searched sources, I did not find one study combining all of the following:

- concrete natural-language-to-DSL production;
- a remote, prompt-local definition that conflicts with a familiar surface convention;
- an exact output site where correct and familiar-incorrect forms are both grammar-valid but produce different canonical IRs;
- an independent factorial manipulation of competitor prior strength and local competitor-specific grammar activation;
- counterbalancing over mappings and several grammar families;
- causal separation of remote specification binding from local completion at that site;
- prediction of failures on unseen mappings, grammars, and preferably model families; and
- a semantics-preserving, site-specific rewrite that prevents the predicted error while translating to the same IR.

That conjunction is more than “combination novelty” only if it yields a new falsifiable result: a reproducible interaction, an out-of-distribution site predictor, and a targeted intervention that beats matched controls.

### Recommendation

**Continue, but pivot.** Do not run an expensive mechanistic study yet. First repair the scorer and run a preregistered, tokenization-controlled 3×3 behavioral experiment. Continue to mechanism only if the prior-strength × local-context interaction is robust across held-out mappings and grammar families. A publishable contribution would require substantially more than the current identity/alpha/beta/gamma comparison.

---

## 2. Corrected hypothesis definitions

### H1 — surface-familiarity effect

Let \(g\) index a grammar family, \(m\) a counterbalanced token-to-meaning mapping, \(t\) a task, and \(s\) a concrete surface. Let \(C_{gmts}\) indicate exact semantic correctness under canonical-IR or executed-state comparison.

$$
H_{1}:\quad
\mathbb{E}[C\mid s=\text{familiar}]
>
\mathbb{E}[C\mid s=\text{novel}]
$$

under a design that holds the canonical program, semantic request, grammar structure, prompt information, decoding method, and approximately the model-token sequence length constant, and counterbalances symbol meanings.

**Plain language:** when only the external spelling changes, does a familiar-looking version work better? This is a behavioral contrast, not proof that a model “reasoned” or “only pattern-matched.” Because Anka and some 3DOM `beta` cells show that a novel surface can work well, this must be a conditional average hypothesis, not a universal law ([Al Mazrouei, 2025, unreviewed preprint](https://arxiv.org/abs/2512.23214)).

### H2 — competitor prior × local activation interaction

Let \(T_i\) be a preregistered measure or categorical manipulation of how strongly the base model favors familiar competitor \(q_i\) over DSL-correct candidate \(c_i\) in a neutral context. Let \(A_i\) be an **independently constructed** level of local context support for \(q_i\), measured without the remote DSL rule. Let \(O_i=1\) mean that unrestricted generation reaches a comparable decision site, and let \(Y_i=1\) mean that the instruction model emits \(q_i\) at that site. For categorical levels, define

$$
p_{ta}=P(Y_i=1\mid O_i=1,T_i=t,A_i=a).
$$

For the conditional-reversion outcome, the preregistered finite contrast is

$$
H_2:\quad \Delta_{\mathrm{int}}=
\left[\operatorname{logit}p_{\mathrm{strong,high}}-
      \operatorname{logit}p_{\mathrm{strong,low}}\right]
-
\left[\operatorname{logit}p_{\mathrm{neutral,high}}-
      \operatorname{logit}p_{\mathrm{neutral,low}}\right]>0.
$$

The medium levels provide a preregistered monotonicity and model-fit check; they are not needed to define this contrast. The corresponding difference-in-differences in the forced-prefix sequence margin is the study's single primary endpoint (Section 6.6); conditional unrestricted reversion is a key secondary endpoint because it additionally depends on reaching the site. A continuous cross-partial is appropriate only in a separate analysis with independently calibrated continuous \(T\) and \(A\), not as the definition of a categorical factorial effect.

**Plain language:** a strong old habit should be most damaging exactly where the nearby syntax cues that habit. A strong prior alone or a CSS-like prefix alone is not the full claim.

### H3 — remote specification versus local completion mechanism

At the matched output position, define a competitor logit margin

$$
G_i^{\mathrm{tok}}=z_i(q_i^\star)-z_i(c_i^\star).
$$

The mechanistic hypothesis is that one distributed causal pathway carries information from the remote mapping/specification and decreases \(G_i^{\mathrm{tok}}\), while another carries competitor-specific information from the immediate prefix and increases it. The hypothesis predicts **selective causal transfer in two different matched-pair families**. For a local-context pair with the same correct remote mapping, patch a high-context donor into a low-context recipient and define

$$
\Delta_{\mathrm{local}}=
G_i^{\mathrm{tok}}(\text{high}\rightarrow\text{low patched})-
G_i^{\mathrm{tok}}(\text{low})>0.
$$

For a rule-binding pair with the same local prefix, patch a correct-rule donor into a wrong-rule or rule-absent recipient and define

$$
\Delta_{\mathrm{rule}}=
G_i^{\mathrm{tok}}(\text{correct rule}\rightarrow\text{wrong/absent rule patched})-
G_i^{\mathrm{tok}}(\text{wrong/absent rule})<0.
$$

The reverse patch directions predict the opposite signs. Donor, recipient, baseline, and patched component must therefore always be reported with a patch effect.

**Plain language:** the nearby code pattern pushes toward the familiar wrong symbol while the earlier rule pushes toward the new correct symbol. These need not be single heads, and “short” versus “long” describes source information, not a guaranteed architectural module.

### H4 — exact-site prediction

For a matched base checkpoint, define

$$
S_i^{\mathrm{seq}}=
\log P_{\text{base}}(q_i\mid r_i,x_i)-
\log P_{\text{base}}(c_i\mid r_i,x_i),
$$

where \(r_i\) is the relevant remote specification and \(x_i\) the exact output prefix. A predictor trained only on development grammars should rank instruction-model reversion risk on entirely held-out mappings and grammar families better than predefined baselines: token count, whole-program NLL, generic input surprisal, and surface identity alone.

**Plain language:** before running generation, can a base model tell us which exact grammar positions are dangerous? The new part would be cross-checkpoint, exact-site, held-out prediction—not the general fact that likelihood or prior confidence can predict errors.

### H5 — semantics-preserving targeted intervention

Let \(\mathcal{W}\) be a rewrite policy that changes only sites whose predicted risk exceeds a threshold, and let \(\psi_{\mathcal{W}}\) deterministically map rewritten outputs back to the original API or canonical IR. Require

$$
\mathrm{IR}(p)=\mathrm{IR}\!\left(\psi_{\mathcal{W}}(\mathcal{W}(p))\right)
$$

for every valid program, and test whether targeted rewriting produces a larger error reduction per changed symbol than random, global, human-designed, and PA-Tool-style renaming controls.

**Plain language:** change only the dangerous spellings, without changing program meaning, and check that this focused repair buys more than a blanket redesign.

### Terminology corrections

- Use **pretrained association**, **base-model preference**, or **in-weight default**, not “dense prior knowledge,” unless density is explicitly measured.
- Use **prompt-local rule following** versus **pretrained/default response**, not “reasoning versus pattern matching.”
- Use **surface-form reversion** only when the emitted competitor is identified in advance; do not label every alien-language error a reversion.
- Keep **token identity** separate from **tokenization**. The same character can be split differently across tokenizers, and equally long strings can have different token costs.
- Keep **grammar validity** separate from **semantic correctness**. A constrained decoder may guarantee the former without the latter.
- Treat model size as an observed model characteristic, not a causal treatment.

---
## 3. Master literature table

**Classification key:** DP = directly preempting a broad claim; SP = strong partial overlap; MA = methodologically adjacent; AR = application-related; BG = background only. “Threat” refers to the proposed project's novelty, not a defect in the cited work. Preprints are explicitly distinguished from peer-reviewed work.

| Paper / class | Authors | Date and venue/status | Task and models | Main manipulation | Main result | Overlap with original hypothesis | Overlap with refined hypothesis | Mechanistic overlap | What it does not cover | Threat | Official link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **PLSemanticsBench / DP** — *LLMs Lean on Priors, Not Programming Language Semantics* | Aditya Thimmaiah; Jiyang Zhang; Jayanth Srinivasa; Junyi Jessy Li; Milos Gligoric | Submitted 2025-10-03; v3 2026-05-29; accepted ICML 2026 | C* final-state/rule/trace prediction; Llama-3.3-70B, Qwen2.5-14B/32B, GPT-4o-mini, DeepSeek-R1 distills on Qwen-14B/32B and Llama-70B, QwQ-32B, o3-mini, GPT-5-mini, Gemini-2.5-Pro | standard semantics vs familiar-operator reassignment vs novel symbols; human, translated, and fuzzed programs | Up to 90% under standard semantics; declines as large as 40–60 points under mutations/complexity; best long-trace result 35% | Directly tests supplied formal semantics against lexical/operator priors | Separates reassigned familiar from novel symbols, but does not independently cross token prior with matched local syntax | Behavioral, not component-level | Not NL→DSL free generation; no exact local-factorial emission site, held-out site predictor, or repair | **Very high** for broad claim | [arXiv / ICML status](https://arxiv.org/abs/2510.03415) |
| **Persistent Priors / DP** — *Persistent Priors, Preserved Targets* | Han-yu Wang | Submitted 2026-05-25; v5 2026-08-08; preprint | Teacher-forced lexical override: Qwen2.5-1.5B/7B base+IT, Gemma-2-2B/9B base+IT, OLMo-1B, Mistral-7B base+IT; patching on Qwen-1.5B base+IT, Gemma-2B base+IT, OLMo-1B | conflict definition such as “doctor means forest” vs matched neutral word; four families/wrappers | All model-level mean interference effects positive; ordinary prior predicts interference in three of four families; matched residual patches recover the lost margin | Direct evidence that prompt definitions do not erase familiar associations | Strong prior-strength precursor, but local syntax is not independently varied | Residual patching establishes causal sufficiency for the selected contrast, not a full circuit | No executable syntax, AST matching, free generation, exact grammar-site prediction, or rewrite | **Very high** | [arXiv](https://arxiv.org/abs/2606.07555) |
| **Conflict and Congruency / DP** | Xiaoyang Hu; Mike Angstadt; Shane Storks; Zan Huang; Aman Taxali; Alex Weigard; Richard L. Lewis; Chandra Sripada | 2026-08-11; preprint | Verbal color conflict; Gemma-2-2B and six Pythia sizes (410M–12B) | immediate same-color default vs distant if–then rule; congruent/incongruent; default-strength LoRA; rule-set size | Six of seven models show congruency effects; attribution and attention ablation distinguish immediate-cue and distant-rule information; strengthening default selectively harms conflict | Directly covers in-weight/default versus in-context rule competition in the evaluated task | Closest task-specific conceptual and methodological precedent for local-default × distant-rule competition | Causal attention ablation plus behavioral interventions in this task; not proof of a universal two-path circuit | Not DSL/code, no AST/site match, no independently crossed lexical prior and grammar activation | **Highest** for an unqualified generic mechanism claim | [arXiv](https://arxiv.org/abs/2608.11510) |
| **Identifier swaps / DP** — *The Larger They Are, the Harder They Fail* | Antonio Valerio Miceli Barone; Fazl Barez; Shay B. Cohen; Ioannis Konstas | Findings of ACL 2023 | Whole-Python-body likelihood/candidate choice with GPT-3, InstructGPT, Codex, CodeGen-multi/mono, OPT, FLAN-T5; chat tests with Claude and GPT-3.5/4 | swap meanings of familiar Python built-ins | Likelihood models generally prefer ordinary meanings; some inverse scaling; chat systems also fail badly | Directly establishes familiar identifier-reassignment difficulty and non-monotonic size effects | Does not isolate local grammar activation from identifier prior | Behavioral only | No novel DSL, canonical IR, factorial context, or causal mechanism | **High** | [ACL Anthology](https://aclanthology.org/2023.findings-acl.19/) |
| **PA-Tool / SP** — *Don't Adapt Small Language Models for Tools; Adapt Tool Schemas to the Models* | Jonggeun Lee; Woojung Song; Jongwook Han; Haesung Pyun; Yohan Jo | Submitted 2025-10-08; ACL 2026 Long | Tool/parameter selection on MetaTool, RoTBench, API-Bank, and tau-Bench; main Qwen2.5-3B/7B, Llama-3.2-3B, Llama-3.1-8B experiments plus wider model appendix | generate schema-name candidates and choose high “peakedness” names | Up to 17-point improvement and author-reported 80% reduction in schema-misalignment errors | Shows surface naming aligned with model expectation can improve reliability | Repair is global schema renaming, not exact local collision diagnosis | None beyond behavioral signal | No isomorphic grammar experiment, IR-site predictor, or minimum-change rewrite | **High** for practical renaming claim | [ACL Anthology](https://aclanthology.org/2026.acl-long.948/) |
| **A Mechanistic Lens on Semantic Conflicts / SP** | Youssef Abdelsalam; Norman Peitek; Anna-Maria Maurer; Marvin Wyrich; Sven Apel | 2026-07-06; preprint | 45 token-aligned Python triplets; output prediction and pytest generation; CodeLlama-7B-Python, Qwen2.5-7B-Instruct, Mistral-7B-Instruct, Llama-3.1-8B-Instruct | align/conflict identifiers or comments with executable implementation | Conflict reduces execution-grounded correctness; bidirectional residual patching localizes causal carrier states in changed regions, intermediate tokens, and late readout | Strong code-domain evidence that misleading semantic cues affect behavior | Context is semantic cue versus code, not lexical prior × immediate grammar context | Bidirectional residual-stream causal localization | No head/MLP/path decomposition; no prompt-defined syntax or exact reversion | **High** for “first mechanistic code conflict” | [arXiv](https://arxiv.org/abs/2607.05587) |
| **Characterizing Mechanisms for Factual Recall / SP** | Qinan Yu; Jack Merullo; Ellie Pavlick | EMNLP 2023 | Counterfactual country–capital prompts; Pythia and GPT-2 | memorized capital vs in-context alternative; head value scaling | Training frequency affects conflict resolution; scaling selected heads shifts contextual answers, reaching as high as 88% in the reported setting | Establishes prior/context conflict and causal steering | No syntactic context manipulation | Heads can promote memorized or contextual answers in these contrasts | Factual QA only; component roles may not transfer to code | **Medium-high** | [ACL Anthology](https://aclanthology.org/2023.emnlp-main.615/) |
| **Cutting Off the Head Ends the Conflict / SP** | Zhuoran Jin; Pengfei Cao; Hongbang Yuan; Yubo Chen; Jiexin Xu; Huaijun Li; Xiaojian Jiang; Kang Liu; Jun Zhao | Findings of ACL 2024 | Subject–attribute QA across eight LMs | internal-memory/context conflict; information-flow blocking, path patching, head pruning | Later-layer “memory” and “context” heads have opposing effects; PH3 steers toward either source | Establishes causal interventions over context–memory conflict | No exact grammar context factor | Head/edge path interventions; subsequent work cautions that head labels can be prompt/domain dependent | Not code, surface remapping, or local grammar completion | **Medium-high** | [ACL Anthology](https://aclanthology.org/2024.findings-acl.70/) |
| **Competition of Mechanisms / SP** | Francesco Ortu; Zhijing Jin; Diego Doimo; Mrinmaya Sachan; Alberto Cazzaniga; Bernhard Schölkopf | ACL 2024 | Counterfactual factual prompts across transformer LMs | parametric facts versus contextual counterfacts; logit/attention interventions | Reports competition between recall and contextual mechanisms | Covers the generic competition story | Does not cross lexical prior and syntax | Mechanistic/causal analyses in factual QA | Not concrete syntax production | **Medium** | [ACL Anthology](https://aclanthology.org/2024.acl-long.458/) |
| **TokDrift / SP** | Yinxi Li; Yuntian Deng; Pengyu Nie | ACL 2026 Long | Instruction-tuned Llama-3 3B/8B/70B, Qwen2.5-Coder 1.5B/7B/32B, DeepSeek-Coder 1.3B/6.7B/33B on eight Python/Java benchmarks | 24 semantics-preserving identifier-casing and spacing rewrites | Average sensitivity 9.26% for naming and 8.29% for spacing; tokenizer-fragment changes are often more sensitive | Establishes that code surface/tokenization perturbations can change correctness | Does not manipulate prompt-defined meaning or competitor-specific local context | Hidden-state analysis is observational, not causal | Sensitivity includes improvements and failures; fertility is not isolated as a cause | **High** for tokenization/surface claims | [ACL Anthology](https://aclanthology.org/2026.acl-long.2199/) |
| **Anka / AR** — *A Domain-Specific Language for Reliable LLM Code Generation* | Saif Khalfan Saif Al Mazrouei | 2025-12-29; arXiv v1 preprint | Author-reported 100 data-transformation tasks; Claude 3.5 Haiku, limited GPT-4o-mini validation | purpose-designed novel canonical DSL versus Python | Author reports 99.9% parse, 95.8% Anka vs 91.2% Python accuracy, and larger multi-step gains | Counterexample to any universal “familiar syntax is better” claim | No controlled factor isolation | None | Simultaneously changes grammar, language design, prompt, canonicalization, and state; paper/repository protocol counts conflict | **High as a counterexample; evidence provisional** | [arXiv](https://arxiv.org/abs/2512.23214) |
| **When Models Ignore Definitions / SP** | Yogeswar Reddy Thota; Setareh Rafatirad; Houman Homayoun; Tooraj Nikoubin | 2026-02-19; preprint | 30 digital-logic/circuit prompts; Claude Haiku 4.5, ChatGPT-5.2 Pro, Gemini 3 Pro | locally redefine operators/gates | Reports persistent semantic-override and assumption-injection errors | Directly overlaps “definitions fail to override defaults” | No local syntax factorial | None | Small curated set, one response per prompt, no mechanism or strong inference | **Medium-high** | [arXiv](https://arxiv.org/abs/2602.17520) |
| **The Override Gap / SP** | Shuaizhi Cheng; Xiang Shi; Zhiwei Zhang; Mingwei Li | Submitted 2026-04-26; v2 2026-05-11; preprint | KID-Bench factual conflicts; Gemma-2B and Mistral-7B with Doc-to-LoRA | grade prior strength; selectively amplify instant adapters | Base prior predicts accuracy drop from 68% to 16% across weak-to-strong bins; boosting improves conflict accuracy | Strong evidence for prior magnitude as a predictor and repair target | No immediate syntactic activation | Parameter-space causal intervention, not inference-time route isolation | Factual QA and adapter method, not prompt DSL | **Medium-high** for prior-strength novelty | [arXiv](https://arxiv.org/abs/2604.23750) |
| **Grammar Prompting / AR** | Bailin Wang; Zi Wang; Xuezhi Wang; Yuan Cao; Rif A. Saurous; Yoon Kim | NeurIPS 2023 | SMCalFlow, Overnight, GeoQuery, PDDL, SMILES; primarily Codex `davinci-002` | generate a specialized BNF then generate the DSL output | Grammar prompting improves few-shot structured generation and can be competitive across tasks | Establishes that explicit grammar can help DSL generation | No familiarity conflict or matched local site | None | Does not test remapped isomorphic surfaces or exact priors | **High** for “grammars help” claim | [NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2023/hash/cd40d0d65bfebb894ccc9ea822b47fa8-Abstract-Conference.html) |
| **From Text to DSL / AR** | Junaid Baber; Nicolas Hili; Didier Schwab; Léo Challier; Cécilia Satrin | SoMeT 2025; corrected arXiv revision 2026 | Few-shot UI/data-model generation with 39 open LMs, 0.5–32B | grammar-based prompts and model/scale comparison | Documents wide variation in syntax and expert semantic quality | Application evidence for open-model DSL generation | No prior × local-context factor | None | No controlled familiar/alien isomorphism | **Medium** | [arXiv](https://arxiv.org/abs/2605.15865) |
| **Text2DSL / AR** | Alexander V. Kozachok; Alexander M. Nazimov; Shamil G. Magomedov | 2026-06-21; accepted KES 2026 | 4,204 PolkitBench NL–DSL pairs; GigaChat and Nemotron | add BNF, API, identifier context; AST evaluation | Reports very high syntax validity and large structural/CodeBLEU gains from context | Supports grammar/API context benefit | No familiarity conflict | None | Domain application, not controlled remapping | **Medium** | [arXiv](https://arxiv.org/abs/2606.22586) |
| **Context-Aware Distillation and Ablation for Text2DSL / SP** | Alexander V. Kozachok; Alexander M. Nazimov; Shamil G. Magomedov | Submitted 2026-06-21; arXiv preprint | PolkitBench-v2 NL→policy DSL; DeepSeek-V4-Flash data teacher and quantized GigaChat-10B-A1.8B evaluator | full 2×2×2 ablation of prompt BNF, API information, and closed identifier vocabulary | Full context improved syntax validity from 58.51% to 97.37% and the combined score from 0.252 to 0.750; components had different form/meaning effects | Strong evidence that explicit grammar, API, and vocabulary context improves one fixed DSL | Factorial context ablation, but no pretrained-competitor prior or matched immediate-prefix manipulation | Behavioral, not mechanistic | One DSL and evaluated model; no isomorphic remapping, unseen grammar families, or exact reversion sites | **High** for a broad “DSL context helps” claim | [arXiv](https://arxiv.org/abs/2606.22578) |
| **Plan with Code / AR** | Nastaran Bassamzadeh; Chhaya Methani | Submitted 2024-08-15; arXiv preprint | NL→JavaScript-like workflow DSL; fine-tuned Codex baseline and GPT-4 retrieval-augmented generation; 67k train/1k test workflows | retrieve 5/20 examples plus function/API descriptions; 10 APIs held out from fine-tuning | More retrieved examples and API metadata reduce several fabrication errors; on held-out APIs, RAG improves sequence similarity but worsens parsing and parameter hallucination relative to fine-tuning | Prior art for grounding fixed-DSL generation with examples and evolving API metadata | No familiar-versus-reassigned surface conflict or local-context factorial | None | Syntax is fixed; API novelty is not unseen-grammar generalization; overlapping precursor should not count as independent evidence | **Medium** for retrieval/context claims | [arXiv](https://arxiv.org/abs/2408.08335) |
| **Hidden Cost of Structure / SP** | Maximilian Schall; Gerard de Melo | RANLP 2025 | 11 open base/instruction models on SQuAD, IFEval, FActScore, MMLU, TruthfulQA | JSON-schema decoding through Outlines, simple/advanced constraints, prompt adaptation | Constraints can help, hurt, or leave performance unchanged; adapted prompting matters | Refutes the absolute claim that constraints “only fix syntax” | No relevance to local lexical competition | Diagnostic likelihood analysis is correlational | JSON output, not isomorphic code surface; limited uncertainty analysis | **High** for constrained-decoding wording | [ACL Anthology](https://aclanthology.org/2025.ranlp-1.124/) |
| **Input Perception to Predictive Insight / MA** | Maggie Mi; Aline Villavicencio; Nafise Sadat Moosavi | EMNLP 2025 | Seven Llama/Qwen instruction models on five figurative-language datasets | supervised error predictors from surprisal, entropy, contextual influence | Likelihood-derived features sometimes improve in-distribution error prediction, heterogeneously | Precedent for pre-generation error prediction | Not exact q-vs-c DSL-site risk | Predictive, not mechanistic | No strong cross-family/grammar transfer; requires prior labels | **Medium** for predictor novelty | [ACL Anthology](https://aclanthology.org/2025.emnlp-main.1740/) |
| **Syntactic Code Completion / BG** | Samuel Miller; Daking Rai; Ziyu Yao | AAAI 2025 workshop paper | CodeLlama-7B on synthetic Python closing-parenthesis completion | vary nesting; inspect layers, attention, and FFN contributions | Some heads track closed parentheses; tracking does not always mean direct output promotion | Supports local code-syntax state representations | No remote rule or competitor prior | Primarily descriptive | One model/task; no semantic conflict or intervention | **Low-medium** | [arXiv](https://arxiv.org/abs/2502.18499) |
| **In-context Learning and Induction Heads / BG** | Catherine Olsson; Nelson Elhage; Neel Nanda; Nicholas Joseph; Nova DasSarma; Tom Henighan; Ben Mann; Amanda Askell; Yuntao Bai; Anna Chen; Tom Conerly; Dawn Drain; Deep Ganguli; Zac Hatfield-Dodds; Danny Hernandez; Scott Johnston; Andy Jones; Jackson Kernion; Liane Lovitt; Kamal Ndousse; Dario Amodei; Tom Brown; Jack Clark; Jared Kaplan; Sam McCandlish; Chris Olah | 2022; research article/preprint, not a peer-reviewed conference paper | Small attention-only through larger transformers | repeated-token pattern `[A][B] … [A] → [B]` | Strong causal evidence in small attention-only models; larger-model evidence mainly correlational | General mechanism for local pattern completion | Does not establish the proposed DSL route | Candidate mechanism only | No conflict, remote binding, code, or DSL | **Low** unless overclaimed as induction | [Official article](https://transformer-circuits.pub/2022/in-context-learning-and-induction-head/index.html) |
| **Do as I Say, Not as I Do / SP** | Carolina Camassa; Derek Shiller | v3 2026-09-01; Sci-FM Workshop at COLM 2026 poster | 13 model configurations, 16 instructions, repeated conflicting assistant turns | explicit instruction versus induced pattern over up to 50 examples | All models drift to some degree, but amount is model- and task-specific | Establishes instruction–demonstration conflict | Repeated examples, not immediate grammar context | Behavioral only | No concrete DSL mechanism or exact matched site | **Medium** | [arXiv](https://arxiv.org/abs/2605.20382) |
| **How Training Data Shapes… / MA** | Minsung Kim; Dong-Kyum Kim; Jea Kwon; Nakyeong Yang; Kyomin Jung; Meeyoung Cha | v3 2026-04-20; preprint | Controlled synthetic training plus real checkpoints | manipulate repetition, inconsistency, and skew in parametric/context knowledge | Training distribution changes arbitration between sources | Causal origin evidence for prior/context behavior | No concrete syntax or local-site factor | Training-level mechanism, not inference circuit | Does not test DSL generation | **Low-medium** | [arXiv](https://arxiv.org/abs/2510.02370) |
| **Code over Words / SP** | Manjie Xu; Isabella Yin; Xinyi Tu; Chi Zhang; Yixin Zhu | Findings of ACL 2026 | Counterfactual mutable-physics rules | natural-language versus executable-code representation and training | Code grounding mitigates author-termed “semantic inertia” | Shows representation affects override | Does not isolate surface familiarity | No matched DSL circuit | Planner, representation, execution, and training change together | **Medium** | [ACL Anthology](https://aclanthology.org/2026.findings-acl.819/) |
| **Patterns of Priming in Production / MA** | Giulia Pucci; Ruizhe Li; Arabella Sinclair | 2026-09-03; preprint; arXiv states EMNLP 2026 Findings, proceedings not independently verified at cutoff | Dative sentence completion across seven base models | lexical repetition, semantic coherence, syntactic prime | Immediate context changes structural continuation tendencies | General local structural activation | Strong conceptual adjacency, but no conflict/remapping/code | Behavioral only | No exact token prior, prompt rule, or causal component | **Medium** | [arXiv](https://arxiv.org/abs/2609.04484) |

### How to read the table

The first three rows set the novelty boundary. PLSemanticsBench makes “models struggle with reassigned formal semantics” non-novel. Persistent Priors makes “familiar meanings survive explicit definitions” non-novel. Conflict and Congruency is a close task-specific precedent for an immediate/default cue competing with a distant explicit rule; it does not by itself establish a generic cross-task architecture. The proposed paper must therefore establish the **DSL-specific factorial interaction, exact-site generalization, and selective repair**, not merely reproduce an analogous effect with different punctuation.

The mechanism literature also needs a replication caveat. Later studies report that alleged “memory” and “context” heads can be architecture-, prompt-, domain-, and contrast-dependent, and that some heads behave more like general copying or category mechanisms. The safe wording is “component \(k\) causally promotes the contextual (or memorized) answer in this preregistered contrast,” not “we discovered the memory head.” Relevant checks include [Dotsinski et al., TMLR 2025](https://openreview.net/forum?id=15keyzQj9h), [Campregher et al., TMLR 2025](https://openreview.net/forum?id=1QrB5WSWOR), and [Li et al., ICML 2025](https://proceedings.mlr.press/v267/li25c.html).

---

## 4. Claim-by-claim novelty matrix

| Proposed claim | Verdict | Strongest evidence | Why this verdict / what remains |
|---|---|---|---|
| Familiar formal syntax often outperforms unfamiliar or reassigned syntax | **Substantially established** | [PLSemanticsBench](https://arxiv.org/abs/2510.03415); [Identifier Swaps](https://aclanthology.org/2023.findings-acl.19/); [TokDrift](https://aclanthology.org/2026.acl-long.2199/) | Already demonstrated in operator semantics, Python identifiers, and code surface perturbations. Not a universal result: task, language design, and model matter. |
| Reassigning familiar symbols can interfere more than using novel symbols | **Substantially established** | PLSemanticsBench KeywordSwap versus KeywordObf | Its broad version is covered. The remaining question is whether the difference is specifically gated by a controlled immediate grammar context during source emission. |
| Explicit definitions cannot fully override pretrained meanings | **Already established as an existence claim** | [Persistent Priors](https://arxiv.org/abs/2606.07555); [When Models Ignore Definitions](https://arxiv.org/abs/2602.17520); Identifier Swaps | “Cannot” must not mean “never can.” The defensible claim is that residual interference occurs under specified tasks and models. |
| Larger models necessarily rely more on learned priors | **Contradicted as a universal claim / unresolved conditionally** | Identifier Swaps reports some inverse scaling; PLSemanticsBench and the current 3DOM cells are heterogeneous | Parameter count co-varies with training data, optimization, architecture, and instruction tuning. Model size is not an isolated treatment. |
| Token fertility predicts semantic accuracy | **Partially studied; causal version unsupported** | [TokDrift](https://aclanthology.org/2026.acl-long.2199/); [Haslett 2025](https://aclanthology.org/2025.cl-3.3/) | Tokenization changes can affect behavior, but lower fertility is not always semantically better. The 3DOM study has only three alien fertility values and confounds language identity. |
| Grammar specifications, API context, vocabularies, and examples improve novel DSL generation | **Already established, conditionally** | [Grammar Prompting](https://proceedings.neurips.cc/paper_files/paper/2023/hash/cd40d0d65bfebb894ccc9ea822b47fa8-Abstract-Conference.html); [Context-Aware Text2DSL](https://arxiv.org/abs/2606.22578); [Text2DSL](https://arxiv.org/abs/2606.22586); [Plan with Code](https://arxiv.org/abs/2408.08335); [From Text to DSL](https://doi.org/10.3233/FAIA250513) | Improvement depends on context component, retrieval, prompt design, model, and task. It is not guaranteed, and it does not establish arbitrary unseen-grammar generalization. |
| Constrained decoding improves syntax more than semantics | **Partially established; absolute form false** | [Hidden Cost of Structure](https://aclanthology.org/2025.ranlp-1.124/); [Raspanti et al.](https://aclanthology.org/2025.acl-industry.34/) | Constraints guarantee only membership in the allowed language, but this can indirectly improve or harm semantic accuracy. Measure both separately. |
| Base-model likelihood predicts instruction-model failure | **Partially studied** | [Override Gap](https://arxiv.org/abs/2604.23750); [Input Perception](https://aclanthology.org/2025.emnlp-main.1740/); PA-Tool | Prior/likelihood signals already predict errors in some settings. Exact q-vs-c site prediction from a matched base checkpoint across held-out DSL grammars appears open. |
| Model-aligned tool/API naming improves reliability | **Already established** | [PA-Tool](https://aclanthology.org/2026.acl-long.948/) | A new contribution must be site-specific risk prediction/minimal rewriting, not simply “better names help.” |
| LLM conflict behavior resembles a Stroop/congruency effect | **Already established as a behavioral analogy** | Persistent Priors; Conflict and Congruency; [Patel et al. 2026](https://doi.org/10.1093/pnasnexus/pgag149) | Similar interference curves do not imply human-like control mechanisms or consciousness. |
| Memory/context or default/rule components can mediate conflict | **Already established in selected tasks** | [Yu et al.](https://aclanthology.org/2023.emnlp-main.615/); [Jin et al.](https://aclanthology.org/2024.findings-acl.70/); Conflict and Congruency | General existence is non-novel; component labels may not generalize. |
| Competitor prior strength × competitor-specific local syntactic activation at a matched DSL emission site | **Apparently unstudied after this search** | Closest: Persistent Priors + Conflict and Congruency + PLSemanticsBench | I found no source that independently crosses both factors in concrete DSL generation. Within each \(A\) comparison, candidate identity, tokenization, semantic role, AST position, grammar legality, and meaning can be fixed. Across \(T\) levels, candidate identity necessarily changes in a token-selection design, so tokenization must instead be closely matched and token meanings/roles counterbalanced. |
| Remote-rule and immediate-prefix pathways are causally separable in that DSL setting | **Unresolved; generic form substantially established** | Conflict and Congruency; A Mechanistic Lens; factual conflict papers | Novelty requires the matched DSL contrast, bidirectional causal tests, and held-out validation—not just an attention plot. |
| Base-checkpoint margin predicts exact reversion sites on unseen mappings/grammars/model families | **Apparently unstudied in this exact form** | Closest: Override Gap; Input Perception; PA-Tool | The cross-checkpoint, exact-site, held-out combination appears open. It must beat simple tokenization and language-identity baselines. |
| Risk-targeted, semantics-preserving local rewrites reduce reversion better than global renaming | **Apparently unstudied in this exact form** | Closest: PA-Tool; TokDrift | Needs deterministic IR equivalence, minimum-change objective, strong baselines, and low-risk negative controls. |

**Search-bounded wording:** within arXiv, ACL Anthology, NeurIPS/ICLR/ICML proceedings, OpenReview, publisher pages, official repositories, the listed keyword searches, and backward/forward searches through 23 September 2026, I did not identify a paper testing the three claims marked “apparently unstudied” in their exact controlled form. This is not proof that no such manuscript, unpublished result, non-English paper, or concurrent submission exists.

---

## 5. Deep comparison with the closest papers

### 5.1 PLSemanticsBench

1. **Task:** execute small Featherweight-C programs under supplied small-step or K semantics; predict state, rule, or full trace. The benchmark has human-written, LLM-translated, and fuzzed splits.
2. **Model output:** answers about execution states/rules/traces—not concrete source code in the mutated language.
3. **Manipulation:** Standard semantics, `KeywordSwap` among familiar operators, and `KeywordObf` with novel symbols. It globally changes several semantics rather than one matched output site.
4. **Quantities:** task accuracy and accuracy changes across semantic systems, program complexity, and trace length. The paper reports standard accuracy up to roughly 90%, drops as large as 40–60 points, and best long-trace performance of 35%. A one-token-obfuscation appendix helps show that token count alone does not explain all degradation.
5. **Evidence type:** controlled behavioral evidence, not causal internal intervention.
6. **Preempted claim:** models can rely on ordinary operator associations instead of supplied mutated formal rules; swapped familiar symbols can be harder than novel ones.
7. **Open dimension:** source generation, the exact reversion opportunity, independent prior × local-context factors, canonical-IR scoring, causal route separation, and targeted surface repair.

**Bottom line:** this is the closest threat to the original paper idea. A submission framed as “alien programming-language semantics reveal pretrained priors” would look incremental beside it.

### 5.2 Persistent Priors, Preserved Targets

1. **Task:** lexical override, for example defining a familiar word as an unrelated target and then comparing the target with the familiar distractor.
2. **Output:** teacher-forced likelihoods of fixed target and distractor strings, not unrestricted generation.
3. **Manipulation:** conflict definition versus a matched neutral-word definition across four semantic families and prompt wrappers.
4. **Quantities:** \(S=\log P(\text{target})-\log P(\text{distractor})\); interference is a neutral-minus-conflict difference. Ordinary no-remapping prior advantage predicts interference in three families; the antonym slope is null. Five small models receive residual-stream patches, with reported normalized recovery \(R\in[0.92,1.06]\) for a combined position patch.
5. **Evidence type:** behavioral prediction plus a causal sufficiency intervention for a selected lexical contrast; not a complete circuit discovery.
6. **Preempted claim:** definitions leave measurable familiar-associate interference, and prior strength can predict it.
7. **Open dimension:** executable prompt-defined syntax, free code generation, grammar-matched local contexts, independent two-factor manipulation, exact site prediction, and a rewrite intervention.

### 5.3 Conflict and Congruency Effects

1. **Task:** a verbal color task in which an if–then rule agrees or conflicts with a strong same-color default completion.
2. **Output:** a color token/probability, with the main result often visible in confidence even when accuracy remains 100%.
3. **Manipulation:** congruent versus incongruent rule, rule-set size, and a LoRA intervention strengthening the default mapping.
4. **Quantities:** correct-answer probability/log-probability and congruency differences; causal-attribution and attention-ablation effects. In Gemma, the reported probability contrast was approximately .964 in congruent versus .568 in incongruent trials.
5. **Evidence type:** behavioral, representation analysis, and direct attention ablation. Ablating access to the rule consequent selectively harms conflict performance.
6. **Preempted claim:** a short-range/default cue can compete with a distant explicit rule through distinguishable information routes.
7. **Open dimension:** code/DSL emission, AST matching, independently calibrated lexical-prior levels, concrete grammar activation, and semantics-preserving repair.

**Bottom line:** proposing a “short local pathway versus long rule pathway” without a DSL-specific causal test is not novel after this paper. Its evidence is nevertheless task-specific and does not prove a universal cross-task two-path architecture.

### 5.4 Identifier Swaps in Python

1. **Task:** evaluate Python functions after pairwise builtin swaps such as swapping `len` and `print`.
2. **Output:** whole-body likelihood/ranking for base models and candidate selection for chat models; it is not ordinary open-ended source generation.
3. **Manipulation:** an original body that becomes semantically wrong under the swap versus a consistently swapped body that is semantically correct.
4. **Quantities:** binary preference/classification across functions and models. Every likelihood-scored model preferred the conventional but wrong body in the reported experiment; chat selection was also poor, with heterogeneous scaling.
5. **Evidence type:** behavioral.
6. **Preempted claim:** familiar identifiers resist prompt-local reassignment; larger models are not guaranteed to override them better.
7. **Open dimension:** familiar-versus-novel competitors, local context as an independent factor, isomorphic DSL families, exact emitted-token opportunity, and causal components.

### 5.5 PA-Tool

1. **Task:** tool and parameter selection from schemas.
2. **Output:** tool/API calls using renamed schema elements.
3. **Manipulation:** sample candidate names from the target model, estimate character-edit-distance “peakedness,” and choose model-aligned names.
4. **Quantities:** task reliability and schema-misalignment errors. The paper reports gains up to 17 points and up to 80% fewer misalignment errors; effects and constraint benefits vary by model/task.
5. **Evidence type:** behavioral intervention at the schema level.
6. **Preempted claim:** adapting names toward model expectations can improve reliability.
7. **Open dimension:** a directly measured q-vs-c collision at an AST-matched site, counterbalanced semantics, local-context interaction, held-out site prediction, and minimum-change repair.

### 5.6 A Mechanistic Lens on Semantic Conflicts

1. **Task:** predict Python outputs and generate unit-test assertions for 45 aligned/conflicting code triplets.
2. **Output:** greedy predicted values or pytest code.
3. **Manipulation:** change semantic cues such as names/comments or change implementation while retaining token alignment suitable for patching.
4. **Quantities:** execution-grounded correctness, cue-consistent error rates, and patch-induced recovery across token-layer states. The authors report an average correctness decline of about 39.7 points under conflict and cue-following errors reaching roughly 49% in some conditions.
5. **Evidence type:** behavioral plus bidirectional residual-stream activation patching; this causally localizes carrier states for the contrast.
6. **Preempted claim:** misleading code cues affect execution judgments and conflict-relevant states can be causally localized.
7. **Open dimension:** prompt-defined concrete syntax, exact familiar-token reversion, prior × grammar-context manipulation, and component/path-level rule-versus-prefix decomposition.

### 5.7 Characterizing Mechanisms for Factual Recall

1. **Task:** answer country-capital questions where an in-context counterfactual conflicts with memory.
2. **Output:** a city token/string.
3. **Manipulation:** factual versus counterfactual prefix; training-frequency proxies; runtime scaling of selected head value vectors.
4. **Quantities:** contextual-answer rate and head contributions to answer logits. A selected intervention can drive contextual responding as high as 88% in a reported condition.
5. **Evidence type:** attribution plus causal value-vector scaling on held-out examples.
6. **Preempted claim:** individual components can promote memorized or contextual candidates and can be manipulated at runtime.
7. **Open dimension:** syntax, executable semantics, immediate grammar activation, and evidence that a component has the same role outside the factual contrast.

### 5.8 Cutting Off the Head Ends the Conflict

1. **Task:** subject–attribute factual QA with inconsistent external context.
2. **Output:** memory-consistent or context-consistent answer.
3. **Manipulation:** context conflict, information-flow blocking, path patching, and pruning of heads.
4. **Quantities:** answer preference and changes after PH3 pruning; the paper reports steering improvements toward internal or contextual answers across eight LMs.
5. **Evidence type:** causal interventions in selected factual contrasts.
6. **Preempted claim:** separable late-layer pathways can contribute oppositely to knowledge conflict and intervention can alter the outcome.
7. **Open dimension:** prompt-defined code syntax and whether apparent head roles survive models, prompts, and tasks. Replication work specifically warns against universal head labels.

### 5.9 TokDrift

1. **Task:** bug fixing, summarization-to-generation round trips, and translation on Python/Java benchmarks.
2. **Output:** ordinary code under established programming languages.
3. **Manipulation:** 24 semantics-preserving identifier-casing and whitespace variants.
4. **Quantities:** sensitivity—the fraction of cases whose correctness flips in either direction—plus token-fragment and hidden-state analyses. Mean sensitivities are 9.26% for names and 8.29% for spacing.
5. **Evidence type:** controlled behavioral perturbation; hidden-state results are observational.
6. **Preempted claim:** apparently harmless surface/tokenization changes can materially alter code-model results.
7. **Open dimension:** prompt-defined remapping, competitor identity, a monotonic fertility→accuracy claim, local rule conflict, and causal path testing.

### 5.10 Anka

1. **Task:** natural-language data transformations in a purpose-built DSL versus Python.
2. **Output:** freely generated Anka or Python programs.
3. **Manipulation:** entire language design, grammar, canonicalization, state handling, prompt, and surface form change together.
4. **Quantities:** author-reported parse and task accuracy; headline results are 99.9% parsing and 95.8% task accuracy for Anka versus 91.2% for Python, with larger reported multi-step differences.
5. **Evidence type:** behavioral application study only.
6. **Preempted claim:** none of the causal familiarity claims; it does provide a counterexample to “novel syntax must be worse.”
7. **Open dimension:** nearly all factor isolation. Moreover, paper and repository disagree about number of tasks/categories/samples and temperature, and displayed results do not transparently reconcile the inventory. Treat the numbers as author-reported and unverified.

---

## 6. Behavioral mathematical framework

### 6.1 Define one sign convention and keep it throughout

Let:

- \(r_i\): the remote DSL specification and examples;
- \(x_i\): the exact generated prefix immediately before decision site \(i\);
- \(c_i\): the DSL-correct candidate sequence;
- \(q_i\): the preregistered familiar but semantically wrong competitor;
- \(O_i=1\): unrestricted generation reaches a comparable decision site; and
- \(Y_i=1\): the model emits \(q_i\) conditional on reaching it.

Use the full-sequence rule-consistent margin

$$
M_i^{\mathrm{seq}}=
\log P(c_i\mid r_i,x_i)-\log P(q_i\mid r_i,x_i).
$$

Then \(M_i^{\mathrm{seq}}>0\) favors the specified DSL and \(M_i^{\mathrm{seq}}<0\) favors reversion. For a pair of single next-token alternatives—or at the first divergent token of longer candidates—define the mechanistic competitor margin

$$
G_i^{\mathrm{tok}}=z_i(q_i^\star)-z_i(c_i^\star).
$$

Only when each complete candidate is exactly one token is \(G_i^{\mathrm{tok}}=-M_i^{\mathrm{seq}}\). Longer candidate sequences pass through different autoregressive states, so no single residual-stream logit margin equals their full-sequence preference. Keeping distinct symbols prevents this common sign and level-of-analysis error.

### 6.2 Prior strength

Estimate competitor prior strength in a preregistered neutral, **no-override** calibration prompt:

$$
T_i=\log P(q_i\mid r_i^{(0)},x_i^{(0)})-
\log P(c_i\mid r_i^{(0)},x_i^{(0)}).
$$

Positive \(T_i\) means the base model prefers the familiar competitor before being taught the new mapping. The neutral context must preserve candidate role and comparable length without itself cueing either surface. Because pretraining data are not fully observable, \(T_i\) measures model preference—not literal corpus frequency or a Bayesian prior known independently of the model.

### 6.3 When an activation score is circular—and how to avoid it

Define a no-rule, local-context competitor margin

$$
G_i^{\mathrm{loc}}(x)=
\log P(q_i\mid r_i^{(0)},x)-
\log P(c_i\mid r_i^{(0)},x),
$$

where \(r_i^{(0)}\) contains no override rule, and let \(T_i=G_i^{\mathrm{loc}}(x_i^{\mathrm{neutral}})\). A valid separately calibrated continuous activation score is then

$$
A_i^{\mathrm{cal}}=G_i^{\mathrm{loc}}(x_i)-T_i.
$$

This score is not circular if the rule is absent and it is computed with a separate base checkpoint or held-out calibration items before instruction-model outcomes are observed. By contrast, if \(x_i\) is shorthand for the same full evaluated prompt \((r_i,x_i)\) and the same model used to define the outcome, then

$$
A_i=
\big[\log P(q_i\mid r_i,x_i)-\log P(c_i\mid r_i,x_i)\big]-T_i
=-M_i^{\mathrm{seq}}-T_i,
$$

for the same candidate events. In that case \(A_i\) contains the response margin it is supposed to explain; using \(T_i\), \(A_i\), and their interaction to predict reversion leaks outcome information.

Use one of two better definitions:

1. **Primary, causal definition:** randomize \(A_i\in\{\text{low},\text{medium},\text{high}\}\) by constructing matched prefixes before observing instruction-model outcomes. This produces a clean factorial estimand.
2. **Secondary, continuous calibration:** compute \(A_i^{\mathrm{cal}}\) above on a separate base checkpoint or held-out no-specification corpus using the same \(q_i,c_i\), then freeze it before testing instruction checkpoints. A high-minus-low manipulation-check contrast can additionally be reported.

The categorical randomized analysis should be primary; calibrated continuous scores can explain heterogeneity.

### 6.4 Interaction model

For the randomized categorical 3×3 design, fit cell indicators or categorical main effects and interactions, then estimate the preregistered finite contrast directly. Do not assume that labels low/medium/high are equally spaced. The single primary forced-prefix contrast is defined in Section 6.6.

As a secondary analysis with independently calibrated, centered continuous predictors, fit a hierarchical model to the sequence margin:

$$
M_i^{\mathrm{seq}} =
\beta_0+\beta_T T_i+\beta_A A_i+\beta_{TA}T_iA_i+
b_{\text{task}}+b_{\text{mapping}}+b_{\text{grammar}}+b_{\text{model}}+\epsilon_i.
$$

With \(M^{\mathrm{seq}}\) coded “correct minus competitor,” the proposed interaction predicts **\(\beta_{TA}<0\)**: strong priors become more damaging as local competitor support rises. If the outcome is \(Y_i=1\) for observed reversion,

$$
\operatorname{logit}P(Y_i=1\mid O_i=1)=
\beta_0+\beta_TT_i+\beta_AA_i+\beta_{TA}T_iA_i+
u_{\text{task}}+u_{\text{mapping}}+u_{\text{grammar}}+u_{\text{model}},
$$

then **\(\beta_{TA}>0\)** has the intended sign, provided that larger \(T\) and \(A\) both mean more support for \(q\), predictors are centered/scaled, and \(A\) was independently manipulated or calibrated. An observational interaction is not automatically causal; the randomized 3×3 planned contrast is the causal test.

Include random intercepts for task/AST template, mapping rotation, grammar family, and model. Add random slopes for the manipulated factors where the number of groups and convergence support them. With only a few model families, report family-specific estimates and a fixed/meta-analytic comparison rather than pretending that four checkpoints estimate the population of all LLMs.

### 6.5 Opportunity is a separate process

For unrestricted generation,

$$
P(\text{observed reversion})
=P(O_i=1)P(Y_i=1\mid O_i=1).
$$

Model both parts:

1. **site reach/eligibility:** does the output parse far enough and enter the relevant AST decision?
2. **conditional choice:** when it reaches the decision, does it choose \(q_i\), \(c_i\), or another form?

This is a hurdle/two-part model. Report \(P(O_i=1)\), \(P(Y_i=1\mid O_i=1)\), and their product. The existing `3/3` bare versus `15/20` scaffolded selector reversions cannot show that scaffolding caused more reversion: bare generation created only three opportunities, and conditions differ in reachability.

### 6.6 Primary and secondary outcomes

**Single primary confirmatory endpoint:** the strong-versus-neutral prior × high-versus-low context difference-in-differences in the forced-prefix full-candidate margin:

$$
\Delta_{\mathrm{int}}^{M}=
\big[\mathbb{E}(M^{\mathrm{seq}}\mid T=\mathrm{strong},A=\mathrm{high})-
     \mathbb{E}(M^{\mathrm{seq}}\mid T=\mathrm{strong},A=\mathrm{low})\big]
-
\big[\mathbb{E}(M^{\mathrm{seq}}\mid T=\mathrm{neutral},A=\mathrm{high})-
     \mathbb{E}(M^{\mathrm{seq}}\mid T=\mathrm{neutral},A=\mathrm{low})\big]<0.
$$

**Key secondary endpoints** are exact canonical-IR or executed-state correctness under unrestricted generation, conditional familiar-competitor reversion \(P(Y_i=1\mid O_i=1)\), and site reach \(P(O_i=1)\). Arm A supplies the primary endpoint; Arm B is the key ecological secondary test; Arm C is a secondary intervention.

**Other diagnostic outcomes**

- lexical and parse validity;
- grammar-valid but semantically wrong rate;
- decision-site reach rate;
- operation, selector, argument, and decomposition correctness, scored without allowing an extra operation to count as exactly correct;
- candidate token/byte count and latency; and
- non-competitor error classes.

Do not average parse validity and semantic accuracy into one score. Report both. Correct the extra-operation scorer and rerun all raw outputs before using the exploratory accuracy table.

### 6.7 Candidate sequences with unequal token lengths

For a candidate string \(y=(y_1,\dots,y_K)\), score the exact sequence:

$$
\log P(y\mid r,x)=
\sum_{j=1}^{K}\log P(y_j\mid r,x,y_{<j}).
$$

Use the model's actual tokenizer and include every token in each candidate. Prefer prefix-free candidate strings with matched token boundaries. Define the event in advance as the **candidate plus any required grammar boundary**, and include that boundary in both scores. If a common suffix is scored, report candidate-only and candidate-plus-boundary results separately: its conditional probability can differ after the two candidates, so it changes the estimand. Never append EOS in the middle of a program merely to force a decision. Score through the shortest unique, grammatically complete decision event rather than an arbitrary later “rejoin” point.

The sum is the probability of the full event and should be primary. It naturally penalizes longer strings, so design candidates with closely matched token lengths and report per-token and per-UTF-8-byte normalized sensitivity analyses. Normalized scores answer a different question and must not silently replace full-sequence probability.

### 6.8 Uncertainty, prediction, and multiplicity

- **Intervals:** report 95% intervals for all primary effects and predicted probabilities. Use profile/bootstrap intervals for frequentist fits or posterior credible intervals with prior-sensitivity checks for Bayesian fits.
- **Resampling unit:** resample sufficiently numerous independent randomized units—not individual token sites. With only two or three grammar families, treat grammar as a fixed stratification factor and cluster/bootstrap at the independent AST-template or mapping-block level while preserving all paired cells. Do **not** nonparametrically bootstrap two or three grammar clusters. A population-of-grammars claim requires many independently designed families (roughly 10–20 or more, justified by simulation) before a grammar-level random effect or cluster bootstrap is credible.
- **Calibration:** reliability plots with uncertainty, expected calibration error only as a supplement, calibration intercept/slope, Brier score, and log loss.
- **Discrimination:** AUROC plus AUPRC because reversion may be rare; always report the prevalence baseline. For a linter, also report top-\(k\) lift/precision, recall at a fixed rewrite budget, and NDCG or reciprocal-rank summaries by grammar.
- **Multiplicity:** one preregistered interaction is primary. Use Holm family-wise correction for a small confirmatory family or Benjamini–Hochberg FDR for explicitly exploratory component/site comparisons. Do not correct away a single declared primary test, but do disclose all tested variants.
- **Robustness:** repeat with exact matching on token count, remove `gamma`, vary tokenizer/model family, and estimate results separately for reassigned-familiar and novel controls.

### 6.9 Power and sample size

Do not use a simple independent-binomial calculator. Simulate data from the intended hierarchical/hurdle model using pilot estimates for:

- baseline site-reach and conditional reversion rates;
- task, mapping, grammar, and model intraclass correlations;
- plausible main effects and the smallest scientifically meaningful interaction;
- missing opportunities and parse failures; and
- multiplicity and held-out splits.

Choose sample size for at least 80–90% probability of detecting the declared interaction **and** a useful interval width. A reasonable pilot scale is 30 AST templates × 6 mapping rotations × 3 grammar families × 9 factorial cells = 4,860 site observations per model before exclusions; the final number must come from simulation rather than treating 4,860 correlated rows as independent. With three pilot grammars, inference is conditional on those grammars; a population-level grammar claim needs substantially more independently designed families. If compute is limited, reduce repeated decoding before reducing the number of independent templates or mapping blocks.

---

## 7. Mechanistic mathematical framework

### 7.1 The margin and residual decomposition

Throughout this section, \(G_i^{\mathrm{tok}}\) denotes a single-next-token margin (or the margin at the first divergent token), not the behavioral full-sequence margin:

$$
G_i^{\mathrm{tok}}=z_i(q^\star)-z_i(c^\star)
=(u_q-u_c)^\top \operatorname{LN}(r_{i,L})+(b_q-b_c),
$$

where \(u_q,u_c\) are unembedding vectors, \(b_q,b_c\) are output biases, and \(r_{i,L}\) is the final residual state. For models without an unembedding bias, \(b_q-b_c=0\). Positive \(G^{\mathrm{tok}}\) means familiar-token reversion is favored. In a pre-LN transformer, schematically,

$$
r_{i,L}=r_{i,0}+
\sum_{\ell,h}o_{i,\ell,h}+
\sum_{\ell}m_{i,\ell}.
$$

This additive residual decomposition does **not** make final logits exactly additive component by component, because the final LayerNorm/RMSNorm is nonlinear and depends on the total residual state.

This single-position equation is exact only for a pair of next-token alternatives. For mechanistic work, prefer candidates that are each one tokenizer token for the analyzed checkpoint, or define the site as their first divergent token. If \(q\) and \(c\) are multi-token sequences, full-sequence preference is a sum over different autoregressive states; repeat the analysis at each aligned divergence and keep \(M^{\mathrm{seq}}\) as the behavioral outcome. A token pair that is single-token in one model family may not be single-token in another, so document this per tokenizer rather than assuming universal alignment.

### 7.2 Layerwise development

A logit-lens curve

$$
G_{i,\ell}^{\text{lens}}
=(u_q-u_c)^\top\operatorname{LN}(r_{i,\ell})+(b_q-b_c)
$$

shows where a linearly decoded competitor preference becomes visible. A tuned lens may reduce early-layer basis mismatch. Either is descriptive: the fact that a direction is decodable at layer \(\ell\) does not show that later computation uses it.

Use the lens to choose a broad layer range on a discovery split, then confirm causal importance by patching on a disjoint test split.

### 7.3 Component contribution

The naive score

$$
(u_q-u_c)^\top o_{i,k}
$$

ignores final normalization. A better direct-logit-attribution approximation is

$$
\operatorname{DLA}_{i,k}
\approx
(u_q-u_c)^\top
J_{\operatorname{LN}}(r_{i,L})\,o_{i,k},
$$

or an explicitly documented frozen final-normalization scale. Report the unexplained remainder and verify that approximate component contributions reconstruct the observed margin closely enough for the intended use. DLA is still attribution, not causation. Establish causal effect with an intervention on the component output.

For attention head \(h\), a source-position decomposition can be written schematically as

$$
o_{i,\ell,h}
=\sum_j \alpha_{ij}^{\ell h}
W_O^{\ell h}W_V^{\ell h}r_{j,\ell}.
$$

The contribution associated with source \(j\) depends on both the attention weight \(\alpha_{ij}\) and the value/output vector. A large attention weight can carry irrelevant or canceling information; an attention heat map alone is not an explanation.

### 7.4 Required causal contrasts

Create two separate token-aligned pair families plus an ordinary-language control:

1. **Local-context family:** the remote rule, mapping, candidate pair, and task are identical; only the immediate prefix has low versus high competitor activation.
2. **Rule-binding family:** the immediate prefix, candidate pair, and task are identical; only the remote rule is correct versus wrong, absent, or counterbalanced.
3. **Ordinary familiar control:** the familiar token is genuinely correct, so indiscriminate suppression of it is harmful.

Do not use the same donor pair to claim both pathways. In a causal decoder, an earlier remote-rule token's state cannot differ because of a later high/low prefix. Within the local-context family, patch immediate-prefix states or downstream states that have integrated that prefix. Within the rule-binding family, patch remote-definition states or later states carrying the retrieved binding.

Then run bidirectional residual patching, condition-matched mean and resample ablations, both attention-head and MLP interventions, and path patching from the relevant source tokens through candidate receiver components to the output. Mean ablation can be distribution-shifting; document every donor's semantics and positional alignment.

The desired directional results are:

| Pair family / patched information | Donor → recipient | Predicted effect relative to recipient |
|---|---|---|
| Local-context / high competitor signal | high context → low context | \(G^{\mathrm{tok}}\) increases; reversion transfers |
| Local-context / low competitor signal | low context → high context | \(G^{\mathrm{tok}}\) decreases; reversion weakens |
| Rule-binding / correct binding | correct rule → wrong/absent rule | \(G^{\mathrm{tok}}\) decreases; DSL answer restores |
| Rule-binding / wrong or absent binding | wrong/absent rule → correct rule | \(G^{\mathrm{tok}}\) increases; correct mapping weakens |

These effects should be selective: the same patch should not generally degrade unrelated code tokens, low-context sites, novel controls, or ordinary CSS conditions where the familiar token is correct. Bidirectionality helps distinguish information transfer from generic activation corruption.

### 7.5 Normalized recovery

For either matched pair family, name the intended donor state and recipient baseline explicitly and define

$$
R=
\frac{G^{\mathrm{tok}}_{\text{patched}}-G^{\mathrm{tok}}_{\text{recipient}}}
{G^{\mathrm{tok}}_{\text{donor}}-G^{\mathrm{tok}}_{\text{recipient}}}.
$$

Thus \(R=1\) means the patched recipient reaches the donor's token margin and \(R=0\) means no movement from the recipient baseline. Always report raw \(\Delta G^{\mathrm{tok}}\) beside \(R\): the denominator becomes unstable when the donor–recipient difference is small, and \(R>1\) can reflect overshoot rather than perfect mechanistic recovery. Predefine a minimum denominator and do not discard low-denominator items after looking at component results.

### 7.6 Proposed path model

A useful hypothesis is a distributed graph, not two named heads:

```text
remote DSL mapping tokens
        ↓
binding / rule-retrieval state ───────────→ correct-candidate support
                                                ↓
                                     output margin G^{tok}
                                                ↑
local prefix → grammar-context state → familiar-competitor support
```

Test four roles separately:

1. **remote rule retriever/binder:** carries which surface maps to which DSL role;
2. **local context detector:** distinguishes high from low competitor-supporting prefixes while holding the candidate pair fixed;
3. **candidate writer:** projects information toward \(q\) or \(c\) at the output;
4. **integrator/readout:** combines these signals at the final position.

Do not infer a role merely because a head attends to a source. Require contrast selectivity, causal necessity/sufficiency tests, and generalization to held-out mappings.

### 7.7 Causal mediation—what can and cannot be claimed

One may test whether manipulating local context \(A\) changes an internal mediator \(H\), whether patching \(H\) changes \(G^{\mathrm{tok}}\), and whether the \(A\to G^{\mathrm{tok}}\) effect shrinks when \(H\) is controlled. But transformer activations are high-dimensional, causally entangled, and patching may create off-manifold states. Therefore:

- call the result **causal mediation evidence under specified interventions**, not a complete natural indirect effect, unless the necessary identification assumptions are defended;
- use matched same-item donors, different-item donors, random layers/positions, and token-position controls;
- check symmetric patch directions and dose/steering curves;
- verify that patched states remain within a plausible activation distribution;
- reserve entire grammar families and mappings for confirmatory testing; and
- correct for the large search over layers, heads, MLPs, positions, and paths.

[Zhang and Nanda's activation-patching best-practices study](https://arxiv.org/abs/2309.16042) is a useful design reference. [Jain and Wallace](https://aclanthology.org/N19-1357/) remains the basic warning that attention weights are not automatically explanations. [Mueller et al.](https://aclanthology.org/2026.cl-1.10/) gives a broader mediation-method caution.

### 7.8 Novelty verdict for the mechanistic prediction

The unqualified generic prediction is **not new enough to support a novelty claim**: Conflict and Congruency provides a close task-specific behavioral and intervention precedent for immediate/default versus distant/rule information; factual-conflict work has causally altered memory/context competition; and A Mechanistic Lens patches conflict information in code. None of these alone establishes a universal cross-task two-path architecture.

The following specific prediction remains plausible as a contribution:

> In AST-matched, prompt-defined DSL production, a local-prefix intervention will selectively transfer the familiar surface competitor, while a remote-binding intervention will selectively transfer the specified DSL candidate; the magnitudes will track an independently manipulated prior × local-context interaction and generalize to held-out token mappings.

That result would be specific and falsifiable. An attention map or a successful single residual patch without held-out validation would not establish it.

---

## 8. Required causal experiment

### 8.1 Core 3×3 design

Cross two randomized or preselected factors:

| Factor | Low / neutral | Medium / weak | High / strong |
|---|---|---|---|
| Familiar-competitor strength \(T\) | candidate pair with near-zero no-override q-vs-c advantage in neutral context | candidate pair with an intermediate calibrated advantage | candidate pair with a large calibrated advantage in neutral context |
| Competitor-specific local activation \(A\) | prefix empirically neutral between \(q,c\) | partial/ambiguous conventional frame | strongly competitor-associated immediate code frame |

For each cell require:

- the same natural-language request;
- the same canonical AST and intended IR;
- the same decision role and comparable position;
- the same candidate pair within each context comparison;
- both \(q\) and \(c\) accepted by the grammar at that position;
- \(q\) and \(c\) mapped to different IR semantics, so reversion is not a harmless alias;
- approximately matched model-token lengths, boundary behavior, and UTF-8 bytes;
- mappings rotated across tokens by a Latin square or balanced permutation;
- context levels chosen using separate base-model calibration data before instruction outcomes are inspected; and
- multiple grammar families designed independently, not cosmetic renamings of one grammar.

Candidate identity cannot remain constant while \(T\) is manipulated by selecting tokens with different pretrained associations. It is held fixed **within each low/medium/high \(A\) comparison**. Across \(T\) levels, token count, boundary behavior, and bytes should be closely matched, and token-to-meaning roles must be counterbalanced. This separates the intended prior manipulation from avoidable tokenization and semantic-role confounds without pretending that the token identities are identical.

The key estimand is not simply identity versus alien accuracy. It is whether the high-minus-low context effect becomes larger as independently measured competitor strength rises.

### 8.2 Constructing honest minimal pairs

The hardest requirement is altering local competitor support without changing the semantic role. One workable construction is:

1. Define several **surface aliases for the already-completed prefix** that the parser deterministically lowers to the same selector/receiver AST.
2. Make the high-activation alias end in a familiar CSS/jQuery-like frame immediately before the decision; make the low alias end in a tokenization-matched unfamiliar frame; create a medium alias by partial cueing.
3. Place the same \(q/c\) alternatives in the same next grammatical slot. Both must remain legal continuations, but only \(c\) maps to the requested operation or relation.
4. Verify by construction that all prefix variants have the same canonical IR up to that point and reach the same abstract parser state/AST role.
5. Calibrate the no-rule competitor margin without the remote mapping. Retain only triples ordered low < medium < high on held-out calibration models, subject to tokenization and semantic checks.

Illustrative, not final, pattern:

```text
high context:   SELECT(css_like_selector) <decision> OP(arg)
medium context: SELECT(partly_familiar_form) <decision> OP(arg)
low context:    SELECT(neutral_form) <decision> OP(arg)
```

All three selector spellings lower to the same selector AST. The decision is still the chain/relation slot. The prompt-local table assigns \(c\) to the required meaning and \(q\) to a different legal meaning. Avoid “low” contexts that merely make the whole prompt harder; the calibration must show a candidate-specific change rather than a large rise in entropy for every token.

An even stricter option is to use equal-length, semantically inert prefix markers that the grammar explicitly discards. That improves AST control but risks creating an artificial benchmark; include both naturalistic alias contexts and these diagnostic minimal contexts.

### 8.3 Counterbalancing

For each candidate set, rotate:

- which surface is correct;
- which IR operation/selector relation it denotes;
- task content and entity names;
- order and wording of specification entries; and
- example order and whether the relevant mapping appears early or late.

No token should be “always correct” across the dataset. No operation should be tied to one familiarity level. Hold out entire mapping rotations, not random prompts derived from the same mapping.

### 8.4 Evaluation arms

**Arm A — forced prefix / teacher-forced candidate score (primary endpoint).** Supply the exact prefix immediately before the decision site and compute full-sequence \(M^{\mathrm{seq}}\). This removes site-reach noise and has high statistical efficiency.

**Arm B — unrestricted NL→DSL generation (key ecological secondary test).** Generate the full program; parse, lower to canonical IR, execute if possible, and use the opportunity hurdle analysis.

**Arm C — grammar-constrained generation (secondary intervention).** The constraint must permit both \(q\) and \(c\); otherwise it trivially deletes the outcome. This tests whether general syntax support changes integration while preserving the semantic conflict.

**Arm D — semantic constraint or oracle (upper bound).** A semantic validator may reject the wrong IR. Keep it distinct from ordinary grammar constraints.

For unrestricted Arm B, use greedy decoding as the preregistered primary decoding policy and a sampling arm for exploratory pass@\(k\), choice distributions, and robustness. Store raw logits and outputs. Arm A's likelihood contrast does not require a decoding policy.

### 8.5 Splits and models

- **Discovery:** some AST templates, mappings, and grammar families; use for prompt/debugging and mechanistic localization.
- **Within-family test:** unseen tasks and mappings in known grammar families.
- **Grammar transfer test:** at least one entirely unseen grammar family.
- **Model transfer test:** at least one different tokenizer/architecture family, not only another Qwen size.

At minimum, evaluate a matched base/instruct pair from two model families at two useful capacity points, if compute allows. Do not interpret size differences causally; treat them as replication strata.

### 8.6 Falsification criteria

The local-context hypothesis is not supported if, with adequate power and valid manipulation checks:

- the interaction is near zero with a narrow interval excluding the smallest meaningful effect;
- it reverses consistently on held-out grammars;
- context changes only general difficulty/entropy, not \(q\)-specific preference;
- tokenization or simple main effects explain all apparent interaction; or
- the effect appears only in one mapping, one grammar, or one checkpoint.

---

## 9. Staged mechanistic experiment plan

### Stage 0 — repair and lock the measurement pipeline

Before new model runs:

- fix the semantic scorer so an output with extra operations cannot count as exact-correct;
- add adversarial scorer tests for extra, missing, duplicated, reordered, and wrong-target operations;
- retain all raw outputs and rescore the exploratory run;
- exclude `gamma` from clean causal claims or redesign it to restore lexical reachability;
- implement exact site-alignment and opportunity labels; and
- preregister hypotheses, exclusions, prompts, decoding, models, and primary contrasts.

### Stage 1 — behavioral validation

Run the 3×3 factorial design. Confirm manipulation checks on independent base-model prompts. Establish the interaction on forced-prefix margins and unrestricted exact-IR behavior, then replicate it on held-out mappings and at least one held-out grammar family.

**Stop here** if the interaction is absent, unstable, fully tokenization-mediated, or does not generalize. A mechanistic explanation of a non-robust effect is not useful.

### Stage 2 — layer localization

On open-weight models only, trace \(G_{i,\ell}^{\mathrm{lens}}\) with tuned-lens/logit-lens methods across high/low context and strong/neutral prior cells. Use discovery data to identify broad intervals where:

- mapping identity becomes decodable;
- high/low local context separates; and
- the final q-vs-c margin changes sharply.

This stage generates hypotheses; it does not establish causality.

### Stage 3 — coarse causal localization

Run the two pair families from Section 7.4 separately across layer × source position:

- **local-context pair:** identical remote mapping, task, and candidates; low versus high immediate context. Patch immediate-prefix positions and downstream integration states;
- **rule-binding pair:** identical local prefix, task, and candidates; correct versus wrong/absent counterbalanced remote mapping. Patch remote definition/example positions and downstream binding states;
- in both families, test intermediate generated positions and the final decision position.

Use bidirectional, same-item, different-item, random-position, and token-matched donors. Do not interpret identical earlier rule-token states from the same-rule local-context pair as evidence about rule binding: in a causal decoder they cannot contain information about a later prefix. Confirm the patch map on untouched grammar/mapping data.

### Stage 4 — component localization

Only within preregistered layer/position ranges, test attention heads and MLP outputs using activation patching, resample ablation, mean ablation, and DLA as a descriptive aid. Report all components searched and multiplicity control. Expect a distributed explanation; do not require one “CSS head.”

### Stage 5 — path testing

Test candidate paths in this order:

1. remote mapping tokens → binding state;
2. binding state → correct-candidate writer/readout;
3. local prefix → grammar-context state;
4. grammar-context state → familiar-competitor writer/readout; and
5. both paths → output margin.

The critical evidence is a double dissociation: local-path intervention changes high-context reversion more than low-context/novel controls, while remote-binding intervention changes rule-consistent choice without broadly damaging ordinary code completion.

### Stage 6 — intervention

Compare:

- activation steering or component patching as a mechanistic proof of concept;
- a prompt-level reminder near the site;
- the proposed semantics-preserving local surface rewrite; and
- grammar versus semantic constraints.

The practical rewrite is preferable for deployment if it improves accuracy without model-internal access. Mechanistic steering matters scientifically but may be brittle across models.

### Essential negative controls

- ordinary CSS/jQuery cases where `.` or the familiar form is correct;
- low-context and novel-token conditions;
- same target with a different source prefix;
- same source prefix with a different target mapping;
- random layers, heads, MLPs, and positions;
- different-item and permuted activation donors;
- prompt paraphrases and specification-order changes;
- tokenization-matched nonsense forms;
- unrelated code decisions in the same completion; and
- interventions designed to be null at the tested site.

Measure both intended benefit and collateral cost. A patch that suppresses `.` everywhere has not discovered selective rule binding; it has damaged punctuation production.

---

## 10. Prediction and repair contribution

### 10.1 Is the base-checkpoint score novel?

The raw idea that model confidence predicts override failure is **not new**. Persistent Priors relates ordinary distractor preference to interference; Override Gap relates base-model prior strength to conflict failure; Input Perception uses likelihood-derived input features to predict errors; PA-Tool uses a familiarity-like peakedness proxy; and structured-output work has proposed base-model behavior as a useful signal.

The potentially new sequence-level estimator is narrower:

$$
S_i^{\mathrm{seq}}=
\log P_{\text{base}}(q_i\mid x_i,r_i)-
\log P_{\text{base}}(c_i\mid x_i,r_i),
$$

where \(q,c\) are predefined competing grammar-valid sequences at the **exact AST emission site**, and the matched base checkpoint is used to predict an instruction checkpoint's eventual conditional reversion. If the goal is to isolate surface collision rather than base-model rule following, also compute a no-specification score and decompose:

$$
S_i^{\text{local}}=
\log P_{\text{base}}(q_i\mid r^{(0)},x_i)-
\log P_{\text{base}}(c_i\mid r^{(0)},x_i),
\qquad
S_i^{\text{rule shift}}=S_i^{\mathrm{seq}}-S_i^{\text{local}}.
$$

This distinguishes local default support from how much the remote rule moves the base model.

To count as a result rather than a retrospective explanation, freeze candidate construction, score calculation, calibration, and threshold on development grammars. Test on:

- unseen token-to-meaning mappings;
- at least one unseen grammar family;
- unseen AST/task templates;
- a different instruct checkpoint size; and
- preferably a different architecture/tokenizer family.

### 10.2 Required baselines

Compare the exact-site margin against:

1. language identity (`identity`/`alpha`/`beta`);
2. candidate token count, byte count, and fragmentation;
3. whole-program NLL per character and per token;
4. generic input surprisal and entropy near the site;
5. q-only and c-only likelihood rather than their contrast;
6. same instruction model's own margin, clearly labeled as less useful for pre-run prediction;
7. a supervised hidden-state probe with equal training information;
8. PA-Tool-style peakedness/name scoring; and
9. random ranking and frequency-only heuristics.

Report calibration and ranking on untouched groups, not only an in-sample regression coefficient. A predictor that merely recognizes `alpha` is not an exact-site predictor.

### 10.3 Surface-collision linter

A useful system contribution could work as follows:

1. enumerate substitutable grammar sites and their canonical IR roles;
2. identify plausible familiar competitors that are grammar-valid but semantically different;
3. render representative prefixes across AST templates;
4. compute \(S_i\) and uncertainty under one or more base checkpoints;
5. flag only sites above a preregistered risk threshold;
6. select a low-risk replacement satisfying lexical, tokenization, readability, and invertibility constraints;
7. validate the new \(\phi\)-map and grammar mechanically; and
8. deterministically translate generated code back to the original API/canonical IR.

The linter must preserve language semantics by proof/check, not by model judgment. Re-run parser/lexer equivalence, corpus round trips, reachability/collision checks, and canonical-IR equality after every rewrite.

### 10.4 Repair baselines and metrics

Compare:

- no rewrite;
- random rewrite at the same number of sites;
- random rewrite matched for token length/fertility;
- human-designed rewrite;
- global familiar renaming;
- PA-Tool-style naming;
- grammar-constrained decoding with both candidates legal;
- semantic constrained decoding;
- an oracle that knows held-out failures; and
- the targeted linter.

Measure:

- exact IR/execution error reduction and conditional reversion reduction;
- number and proportion of symbols changed;
- error reduction per changed site;
- false-positive rewrite rate on low-risk sites;
- performance on ordinary CSS/identity negative controls;
- token/byte cost and context-window impact;
- generation latency and linter computation;
- human readability/comprehension in a small preregistered study if a usability claim is made; and
- robustness across mappings, grammars, and model families.

A strong result is not “rewriting helps.” It is that predicted high-risk sites benefit disproportionately, low-risk sites remain stable, and the targeted method reaches comparable accuracy with materially fewer changes than global baselines.

---

## 11. Human analogy

### What is reasonably Stroop-like?

The analogy is methodological. A Stroop-style design holds a response set fixed and compares congruent/neutral/conflicting cues. Here the specified DSL token is the target, the familiar code token is the distractor, and a high-association local prefix creates conflict. A larger conflict-minus-neutral reduction in the correct-versus-distractor log-probability margin is behaviorally analogous to an interference cost.

[Persistent Priors](https://arxiv.org/abs/2606.07555) explicitly uses this matched lexical-override framing. [Conflict and Congruency](https://arxiv.org/abs/2608.11510) uses congruent and incongruent verbal mappings. [Patel, Wang, and Fan](https://doi.org/10.1093/pnasnexus/pgag149) study Stroop-like congruency behavior in frontier systems. [Patterns of Priming](https://arxiv.org/abs/2609.04484) is relevant to structural/lexical activation, although it is not a Stroop conflict task.

### What must not be inferred?

- Similar accuracy or probability interference does not show that humans and transformers use the same algorithm.
- “Automatic” can operationally mean a response supported without the task-local rule and difficult to suppress under conflict; it should not imply consciousness, intention, or a human executive-control faculty.
- Wall-clock generation latency depends on hardware, batching, cache state, output length, and kernels. It is not a clean analogue of human reaction time.
- A component called a “memory head” in one model/task is not equivalent to a human memory system.

### Best computational analogue

For a fixed competitor pair, the most useful analogue is the signed sequence-probability margin \(M^{\mathrm{seq}}=\log P(c)-\log P(q)\), because it is response-specific. At a single-token decision, the corresponding logit margin is also useful. Surprisal of the correct response does not say whether probability moved specifically to the familiar competitor. Entropy measures global uncertainty and can rise because of unrelated alternatives. Report all three if helpful, but use the q-vs-c sequence margin as the primary conflict measure.

The analogy should be phrased as:

> “We use a Stroop-style congruency manipulation to quantify competition between a prompt-specified DSL response and a familiar surface competitor.”

It should not be phrased as:

> “The model has human automatic and controlled cognitive systems.”

---

## 12. Strongest surviving contribution

### One-sentence scientific contribution

> We test whether exact surface-token reversions in prompt-defined DSL production arise from a factorial interaction between independently calibrated competitor priors and immediate competitor-specific grammar context, then ask whether remote binding and local completion are causally separable, predict failures on unseen grammars, and support minimal semantics-preserving repair.

### Abstract-style contribution

Existing work shows that familiar lexical and programming-language meanings can resist prompt-local redefinition, and that default cues can compete with distant rules. What is not yet established is whether this interference is selectively activated by the immediate grammar environment during concrete DSL generation. We propose a counterbalanced multi-grammar benchmark in which the correct and familiar-incorrect candidates occupy the same AST role, are both grammar-valid, and differ in canonical semantics. Competitor prior strength and local syntactic activation are independently crossed: candidate identity and tokenization are fixed within context comparisons, while tokenization is closely matched and roles are counterbalanced across prior levels. We evaluate forced-prefix margins and unrestricted canonical-IR accuracy with opportunity-aware analysis. Conditional on a robust held-out interaction, we use bidirectional activation and path patching to test remote specification-binding and local completion routes. Finally, we test whether a matched base-checkpoint margin predicts exact failure sites on unseen mappings and whether a surface-collision linter can rewrite only high-risk forms while preserving IR semantics. The contribution is the controlled interaction, out-of-distribution prediction, and selective intervention—not the already-known existence of pretrained surface priors.

### Plain-language explanation for a professor

Models already have strong habits about what familiar pieces of code usually mean. Other researchers have shown that those habits can survive even when a prompt gives a new definition. My narrower question is **when** that old habit wins during code generation. I will hold the intended program fixed and vary two things separately: how strong the model's old preference is and how strongly the few nearby symbols resemble the old code pattern. If the combination reliably predicts the exact wrong symbol, I will then test which internal information comes from the distant rule and which comes from the nearby code. The practical goal is a linter that changes only risky spellings and translates them back to the same internal program. The current experiment suggests this question, but it does not yet prove it.

---

## 13. Go/no-go assessment

### Decision

**Conditional go.** The project is worth continuing as a narrow causal and predictive study. It is not worth continuing under the broad “familiar versus alien syntax proves models only pattern-match” framing.

### First pilot

Run a small but properly counterbalanced behavioral pilot before any interpretability work:

1. repair and regression-test the IR scorer;
2. create two independent grammar families, at least 12–20 AST templates, several mapping rotations, and the full 3×3 manipulation;
3. validate context and prior levels using no-specification base-model prompts that are disjoint from test items;
4. run forced-prefix scoring plus unrestricted generation on one matched base/instruct model pair;
5. analyze site reach and conditional reversion separately; and
6. replicate the interaction on held-out mappings.

If the manipulation itself fails—high/medium/low contexts do not order q-vs-c support—redesign it before testing the hypothesis.

### Continue when

Continue to the full behavioral study if the pilot shows:

- the preregistered interaction has the predicted direction and a practically meaningful magnitude;
- it is not driven solely by token count, one token pair, or failed site reach;
- exact IR and conditional reversion agree directionally;
- held-out mappings retain the effect; and
- ordinary familiar-language controls are not broadly harmed.

Proceed to mechanisms only after replication across grammar families. A strong main effect of prior or context without an interaction may still be publishable as benchmark evidence, but it does not support the refined hypothesis.

### Stop or pivot when

- a well-powered interval excludes the smallest meaningful interaction;
- the effect disappears under tokenizer matching;
- the interaction does not transfer beyond the grammar used to select contexts;
- q-specific support is indistinguishable from general prompt difficulty;
- results depend on `gamma` or on the known scorer defect; or
- simple token-count/language labels predict as well as the proposed site score.

If behavioral interaction is absent, a mechanistic study of “two competing pathways” becomes unnecessary. One could instead publish a careful negative result or study the main effects of specification and tokenization.

### Evidence tiers

**Workshop / short paper candidate**

- corrected scorer and released benchmark/harness;
- preregistered multi-grammar 3×3 behavioral result;
- forced-prefix and free-generation outcomes;
- exact IR scoring and opportunity analysis;
- at least two open checkpoints; and
- explicit tokenization controls and limitations.

**ACL/EMNLP Findings or ICSE/ASE/FSE candidate**

- robust interaction across several mappings and grammar families;
- at least two model families;
- held-out exact-site prediction beating strong likelihood/token baselines;
- targeted linter beating random/global/PA-Tool-style rewrites;
- ablations, uncertainty, and artifact release; and
- clear software-engineering relevance or NLP generalization.

**Main-track NLP/ML candidate**

- causal behavioral manipulation with broad held-out generalization;
- a convincing, replicated mechanistic double dissociation across architectures or a principled reason for model specificity;
- intervention results linking mechanism to behavior;
- strong predictive calibration and practical repair; and
- substantially broader task/model coverage than the present Qwen-only study.

None of these evidence packages guarantees acceptance.

---

## 14. Claims to avoid

| Likely reviewer objection | Defensible replacement |
|---|---|
| “Models do not reason.” | “Under these controlled remappings, the tested models often fail to condition their outputs on the supplied rule.” |
| “Models only pattern-match.” | “Local distributional associations measurably compete with the prompt-specified mapping at these output sites.” |
| “DSL success mainly comes from pretraining familiarity.” | “Surface familiarity is one candidate contributor; this study estimates its effect under controlled semantics, structure, and tokenization.” |
| “Attention explains the behavior.” | “Bidirectional interventions on selected attention/component outputs causally change the q-vs-c margin in this contrast.” |
| “This is the first LLM Stroop effect.” | “This is a DSL-specific Stroop-style congruency design building on prior lexical and verbal LLM conflict paradigms.” |
| “No one has studied prior override.” | “Prior override is well studied; the exact prior × local-grammar interaction in prompt-defined DSL source production was not identified in the bounded search.” |
| “Familiar syntax is always superior.” | “Familiarity often helps under conflict, but language design and task structure can outweigh it; novel DSLs can perform well.” |
| “Larger models have stronger habits.” | “Scaling patterns are heterogeneous across the tested checkpoints; size is not causally isolated.” |
| “Token fertility causes hallucination/semantic failure.” | “Fertility measures token cost and is a plausible confound; causal attribution requires matched interventions.” |
| “Gamma proves unfamiliar Unicode is worse.” | “Gamma is a Unicode/lexer stress condition and is not a clean isomorphic control because lexical reachability differs.” |
| “Constrained decoding only fixes syntax.” | “It guarantees allowed form under the constraint; downstream semantic accuracy may improve, decline, or remain unchanged.” |
| “Base-model likelihood prediction is entirely new.” | “The proposed novelty is exact-site, cross-checkpoint prediction with held-out mappings and grammars, beyond existing likelihood-based error prediction.” |
| “Generation rather than comprehension makes the work novel.” | “Concrete free generation creates a measurable reach-and-choice process; novelty depends on the controlled interaction, generalization, and intervention.” |
| “The current experiment proves contextual gating.” | “The current outputs motivate contextual gating, but roles, opportunity, tokenization, and scoring are confounded; the factorial study is the test.” |
| “Scaffolding increases reversion.” | “Scaffolding changes both site reach and conditional behavior; the current 3/3 versus 15/20 counts are insufficient for a causal claim.” |
| “Beta disproves tokenization effects.” | “Beta shows that fertility alone does not determine task success in these small cells; the design does not estimate a causal fertility effect.” |
| “We found a memory/context head.” | “This component promotes one source under the specified contrast; role stability is tested across prompts, mappings, and models.” |
| “Activation patching reveals the algorithm.” | “Patching establishes causal sufficiency or necessity under selected counterfactual replacements; it does not by itself recover the full algorithm.” |
| “The language variants are perfectly controlled.” | “Identity, alpha, and beta preserve the intended grammar/IR mapping but differ in tokenization; gamma also fails a lexical-reachability control.” |

---

## 15. Bibliography and search audit

### 15.1 Search procedure

**Cutoff:** 23 September 2026. Searches included work available online by the cutoff, regardless of whether it was peer-reviewed. Publication status is reported separately from technical relevance.

**Primary databases and sources:**

- ACL Anthology and DOI records for ACL-family publications;
- arXiv abstracts, HTML/PDF full text, version histories, and linked repositories;
- official NeurIPS, ICML/PMLR, ICLR, and OpenReview records;
- publisher pages for RANLP, SoMeT, and PNAS Nexus;
- official author/project repositories where implementation or protocol details needed verification; and
- exact-title/author searches and scholarly web search for discovery. Blogs and generated summaries were not used as evidence when a primary source was available.

**Core query families:**

```text
"prompt-defined semantics" LLM
"semantic override" language model
"lexical override" LLM Stroop
operator swap OR identifier swap language model code
symbol reassignment programming language LLM
syntax familiarity OR surface-form prior code generation
context memory conflict OR parametric contextual knowledge transformer
rule habit competition OR congruency effect LLM
structural priming language-model production
DSL generation grammar prompting LLM
tokenizer grammar mismatch code
tool schema alignment pretrained naming
constrained decoding semantic accuracy structured output
attention head syntax completion code
residual stream semantic conflict activation patching
path patching memory context heads
specification following local completion language model
base model likelihood predict instruction model error
```

Exact titles, arXiv identifiers, author names, and distinctive method names (`PLSemanticsBench`, `PA-Tool`, `TokDrift`, `PH3`, “induction heads”) were then searched. For the directly overlapping papers, references were followed backward and exact-title/author/citing-term searches were used to discover later work. Citation-index availability differed by source, so this is a broad structured search, not a guaranteed complete systematic-review citation graph.

**Reading depth:** full text and relevant appendices/repository evidence were inspected for the ten deep-comparison papers and the strongest constraints/tokenization counterweights. Abstract/metadata plus relevant methods/results sections were used for more distant background papers. Numerical claims in this report are limited to values that could be verified in the primary paper or official record.

### 15.2 Publication-status and metadata corrections

- **PLSemanticsBench:** the current title is *LLMs Lean on Priors, Not Programming Language Semantics*; arXiv v3 reports acceptance at ICML 2026. Older title variants should not be used as the authoritative citation.
- **PA-Tool:** now has an ACL 2026 Long Paper record and DOI, not merely an arXiv preprint.
- **From Text to DSL:** published at SoMeT 2025; the arXiv posting/revision is from 2026.
- **Text2DSL:** the manuscript says accepted to KES 2026, but the inspected version retained publication placeholders; cite it as an accepted manuscript unless a final proceedings record is verified.
- **Anka:** arXiv v1 only at the cutoff; no peer-reviewed venue was verified, and the paper/repository protocols conflict.
- **Patterns of Priming:** arXiv comments state EMNLP 2026 Findings, but a matching ACL Anthology record was not verified at the cutoff; treat the venue as unverified.
- **Mechanistic Understanding of Language Models in Syntactic Code Completion:** workshop paper, not an AAAI main-track paper.
- **Persistent Priors, Conflict and Congruency, A Mechanistic Lens, Override Gap, and When Models Ignore Definitions:** preprints at the cutoff.

### 15.3 Complete bibliography used in this audit

#### Direct and strong-overlap sources

1. Aditya Thimmaiah, Jiyang Zhang, Jayanth Srinivasa, Junyi Jessy Li, and Milos Gligoric. “LLMs Lean on Priors, Not Programming Language Semantics.” ICML 2026. [Official arXiv record](https://arxiv.org/abs/2510.03415).
2. Han-yu Wang. “Persistent Priors, Preserved Targets: A Stroop-Style Paradigm for Lexical Override.” arXiv preprint, v5, 2026. [Official record](https://arxiv.org/abs/2606.07555).
3. Xiaoyang Hu, Mike Angstadt, Shane Storks, Zan Huang, Aman Taxali, Alex Weigard, Richard L. Lewis, and Chandra Sripada. “Conflict and Congruency Effects in Large Language Models: In-Weight and In-Context Competition in a Verbal Conflict Task.” arXiv preprint, 2026. [Official record](https://arxiv.org/abs/2608.11510).
4. Antonio Valerio Miceli Barone, Fazl Barez, Shay B. Cohen, and Ioannis Konstas. “The Larger They Are, the Harder They Fail: Language Models Do Not Recognize Identifier Swaps in Python.” Findings of ACL 2023. DOI: 10.18653/v1/2023.findings-acl.19. [ACL Anthology](https://aclanthology.org/2023.findings-acl.19/).
5. Jonggeun Lee, Woojung Song, Jongwook Han, Haesung Pyun, and Yohan Jo. “Don't Adapt Small Language Models for Tools; Adapt Tool Schemas to the Models.” ACL 2026 Long Papers. DOI: 10.18653/v1/2026.acl-long.948. [ACL Anthology](https://aclanthology.org/2026.acl-long.948/).
6. Youssef Abdelsalam, Norman Peitek, Anna-Maria Maurer, Marvin Wyrich, and Sven Apel. “A Mechanistic Lens on Semantic Conflicts: Using Activation Patching to Understand LLM Behavior.” arXiv preprint, 2026. [Official record](https://arxiv.org/abs/2607.05587).
7. Qinan Yu, Jack Merullo, and Ellie Pavlick. “Characterizing Mechanisms for Factual Recall in Language Models.” EMNLP 2023. DOI: 10.18653/v1/2023.emnlp-main.615. [ACL Anthology](https://aclanthology.org/2023.emnlp-main.615/).
8. Zhuoran Jin, Pengfei Cao, Hongbang Yuan, Yubo Chen, Jiexin Xu, Huaijun Li, Xiaojian Jiang, Kang Liu, and Jun Zhao. “Cutting Off the Head Ends the Conflict: A Mechanism for Interpreting and Mitigating Knowledge Conflicts in Language Models.” Findings of ACL 2024. DOI: 10.18653/v1/2024.findings-acl.70. [ACL Anthology](https://aclanthology.org/2024.findings-acl.70/).
9. Francesco Ortu, Zhijing Jin, Diego Doimo, Mrinmaya Sachan, Alberto Cazzaniga, and Bernhard Schölkopf. “Competition of Mechanisms: Tracing How Language Models Handle Facts and Counterfactuals.” ACL 2024. [ACL Anthology](https://aclanthology.org/2024.acl-long.458/).
10. Yinxi Li, Yuntian Deng, and Pengyu Nie. “TokDrift: When LLM Speaks in Subwords but Code Speaks in Grammar.” ACL 2026 Long Papers. DOI: 10.18653/v1/2026.acl-long.2199. [ACL Anthology](https://aclanthology.org/2026.acl-long.2199/).
11. Saif Khalfan Saif Al Mazrouei. “Anka: A Domain-Specific Language for Reliable LLM Code Generation.” arXiv v1 preprint, 2025. [Official record](https://arxiv.org/abs/2512.23214); [author repository](https://github.com/BleBlo/Anka).
12. Yogeswar Reddy Thota, Setareh Rafatirad, Houman Homayoun, and Tooraj Nikoubin. “When Models Ignore Definitions: Measuring Semantic Override Hallucinations in LLM Reasoning.” arXiv preprint, 2026. [Official record](https://arxiv.org/abs/2602.17520).
13. Shuaizhi Cheng, Xiang Shi, Zhiwei Zhang, and Mingwei Li. “The Override Gap: A Magnitude Account of Knowledge Conflict Failure in Hypernetwork-Based Instant LLM Adaptation.” arXiv preprint, v2, 2026. [Official record](https://arxiv.org/abs/2604.23750).

#### DSL, structured generation, tokenization, and prediction

14. Bailin Wang, Zi Wang, Xuezhi Wang, Yuan Cao, Rif A. Saurous, and Yoon Kim. “Grammar Prompting for Domain-Specific Language Generation with Large Language Models.” NeurIPS 2023. [Official proceedings](https://proceedings.neurips.cc/paper_files/paper/2023/hash/cd40d0d65bfebb894ccc9ea822b47fa8-Abstract-Conference.html).
15. Junaid Baber, Nicolas Hili, Didier Schwab, Léo Challier, and Cécilia Satrin. “From Text to DSL: Evaluating Grammar-Based Model Generation Using Open LLMs.” SoMeT 2025. DOI: 10.3233/FAIA250513. [Publisher DOI](https://doi.org/10.3233/FAIA250513); [arXiv](https://arxiv.org/abs/2605.15865).
16. Alexander V. Kozachok, Alexander M. Nazimov, and Shamil G. Magomedov. “Text2DSL: LLM-Based Code Generation for Domain-Specific Languages.” KES 2026 accepted manuscript. [arXiv](https://arxiv.org/abs/2606.22586).
17. Maximilian Schall and Gerard de Melo. “The Hidden Cost of Structure: How Constrained Decoding Affects Language Model Performance.” RANLP 2025. [ACL Anthology](https://aclanthology.org/2025.ranlp-1.124/).
18. Federico Raspanti, Tanir Ozcelebi, and Mike Holenderski. “Grammar-Constrained Decoding Makes Large Language Models Better Logical Parsers.” ACL 2025 Industry Track. [ACL Anthology](https://aclanthology.org/2025.acl-industry.34/).
19. Maggie Mi, Aline Villavicencio, and Nafise Sadat Moosavi. “From Input Perception to Predictive Insight: Modeling Model Blind Spots Before They Become Errors.” EMNLP 2025. DOI: 10.18653/v1/2025.emnlp-main.1740. [ACL Anthology](https://aclanthology.org/2025.emnlp-main.1740/).
20. David A. Haslett. “Tokenization Changes Meaning in Large Language Models: Evidence from Chinese.” *Computational Linguistics*, 2025. DOI: 10.1162/coli_a_00557. [ACL Anthology](https://aclanthology.org/2025.cl-3.3/).
21. Omer Goldman, Avi Caciularu, Matan Eyal, Kris Cao, Idan Szpektor, and Reut Tsarfaty. “Unpacking Tokenization: Evaluating Text Compression and its Correlation with Model Performance.” Findings of ACL 2024. [ACL Anthology](https://aclanthology.org/2024.findings-acl.134/).

#### Mechanism, priming, and context–memory background

22. Samuel Miller, Daking Rai, and Ziyu Yao. “Mechanistic Understanding of Language Models in Syntactic Code Completion.” AAAI 2025 workshop paper. [arXiv](https://arxiv.org/abs/2502.18499).
23. Catherine Olsson, Nelson Elhage, Neel Nanda, Nicholas Joseph, Nova DasSarma, Tom Henighan, Ben Mann, Amanda Askell, Yuntao Bai, Anna Chen, Tom Conerly, Dawn Drain, Deep Ganguli, Zac Hatfield-Dodds, Danny Hernandez, Scott Johnston, Andy Jones, Jackson Kernion, Liane Lovitt, Kamal Ndousse, Dario Amodei, Tom Brown, Jack Clark, Jared Kaplan, Sam McCandlish, and Chris Olah. “In-context Learning and Induction Heads.” 2022 research article. [Official Transformer Circuits article](https://transformer-circuits.pub/2022/in-context-learning-and-induction-head/index.html); [arXiv metadata](https://arxiv.org/abs/2209.11895).
24. Carolina Camassa and Derek Shiller. “Do as I Say, Not as I Do: Instruction–Induction Conflict in LLMs.” Sci-FM Workshop at COLM 2026 poster / arXiv preprint. [Official arXiv record](https://arxiv.org/abs/2605.20382).
25. Minsung Kim, Dong-Kyum Kim, Jea Kwon, Nakyeong Yang, Kyomin Jung, and Meeyoung Cha. “How Training Data Shapes the Use of Parametric and In-Context Knowledge in Language Models.” arXiv preprint, 2026. [Official record](https://arxiv.org/abs/2510.02370).
26. Manjie Xu, Isabella Yin, Xinyi Tu, Chi Zhang, and Yixin Zhu. “Code over Words: Overcoming Semantic Inertia via Code-Grounded Reasoning.” Findings of ACL 2026. DOI: 10.18653/v1/2026.findings-acl.819. [ACL Anthology](https://aclanthology.org/2026.findings-acl.819/).
27. Giulia Pucci, Ruizhe Li, and Arabella Sinclair. “Patterns of Priming in Production: Lexical, Semantic and Structural Alignment in LM Generation.” arXiv preprint, 2026. [Official record](https://arxiv.org/abs/2609.04484).
28. Itay Yona, Amir Sarid, Michael Karasik, and Yossi Gandelsman. “In-Context Representation Hijacking.” ACL 2026. [ACL Anthology](https://aclanthology.org/2026.acl-long.768/).
29. Kaiser Sun, Fan Bai, and Mark Dredze. “Task Matters: Knowledge Requirements Shape LLM Responses to Context–Memory Conflict.” Findings of ACL 2026. [ACL Anthology](https://aclanthology.org/2026.findings-acl.202/).
30. Fred Zhang and Neel Nanda. “Towards Best Practices of Activation Patching in Language Models: Metrics and Methods.” 2023. [arXiv](https://arxiv.org/abs/2309.16042).
31. Sarthak Jain and Byron C. Wallace. “Attention is not Explanation.” NAACL 2019. [ACL Anthology](https://aclanthology.org/N19-1357/).
32. Aaron Mueller, Jannik Brinkmann, Millicent Li, Samuel Marks, Koyena Pal, Nikhil Prakash, Can Rager, Aruna Sankaranarayanan, Arnab Sen Sharma, Jiuding Sun, Eric Todd, David Bau, and Yonatan Belinkov. “The Quest for the Right Mediator: Surveying Mechanistic Interpretability for NLP Through the Lens of Causal Mediation Analysis.” *Computational Linguistics*, 2026. DOI: 10.1162/coli.a.572. [ACL Anthology](https://aclanthology.org/2026.cl-1.10/).
33. Suketu Chandrakant Patel, Hongbin Wang, and Jin Fan. “Deficient Executive Control in Large Language Models.” *PNAS Nexus*, 2026. DOI: 10.1093/pnasnexus/pgag149. [Publisher](https://doi.org/10.1093/pnasnexus/pgag149).
34. Asen Dotsinski, Udit Thakur, Marko Ivanov, Mohammad Hafeez Khan, and Maria Heuss. “On the Generalizability of ‘Competition of Mechanisms: Tracing How Language Models Handle Facts and Counterfactuals.’” TMLR 2025. [OpenReview](https://openreview.net/forum?id=15keyzQj9h).
35. Dante Campregher, Yanxu Chen, Sander Hoffman, and Maria Heuss. “Tracing Facts or Just Copies? A Critical Investigation of the Competitions of Mechanisms in Large Language Models.” TMLR 2025. [OpenReview](https://openreview.net/forum?id=1QrB5WSWOR).
36. Gaotang Li, Yuzhong Chen, and Hanghang Tong. “Taming Knowledge Conflicts in Language Models.” ICML 2025. [PMLR](https://proceedings.mlr.press/v267/li25c.html).

### 15.4 Papers excluded from the core novelty comparison

The following families were discovered but not treated as direct novelty threats:

- **Generic constrained decoding** such as PICARD and grammar-masking systems: important implementation baselines, but they do not manipulate pretrained surface meaning or local competitor activation. They remain relevant controls.
- **Ordinary text-to-code/semantic parsing benchmarks:** demonstrate generation ability but do not compare controlled isomorphic surfaces or prompt-local remapping.
- **General retrieval/context–memory factual QA:** relevant mechanism background, but excluded from the core DSL novelty claim unless it included causal component tests.
- **Human Stroop and psycholinguistic priming studies:** used only to define the analogy; they do not establish transformer mechanisms.
- **Tokenizer-vocabulary design papers:** useful for fertility controls, but not evidence that fertility causes instruction-following failure in a fixed model.
- **Very recent single-author constrained-decoding preprints** such as *The Constraint Tax* and the 20 September 2026 Chavan preprint: considered as counterweights but assigned low evidential weight because they were unreviewed and extremely recent at the cutoff.

No directly overlapping named seed paper was inaccessible. Remaining verification limitations are the unresolved Anka protocol discrepancies, incomplete final bibliographic status for Text2DSL, and unverified proceedings status for Patterns of Priming. Concurrent submissions, unpublished negative results, and work outside indexed English-language sources remain sources of uncertainty.

### 15.5 BibTeX for the most directly relevant papers

The following entries use official conference metadata where available and current arXiv metadata otherwise.

```bibtex
@misc{thimmaiah2026priors,
  title   = {LLMs Lean on Priors, Not Programming Language Semantics},
  author  = {Thimmaiah, Aditya and Zhang, Jiyang and Srinivasa, Jayanth and Li, Junyi Jessy and Gligoric, Milos},
  year    = {2026},
  eprint  = {2510.03415},
  archivePrefix = {arXiv},
  note    = {Accepted at ICML 2026},
  url     = {https://arxiv.org/abs/2510.03415}
}

@article{wang2026persistent,
  title   = {Persistent Priors, Preserved Targets: A Stroop-Style Paradigm for Lexical Override},
  author  = {Wang, Han-yu},
  year    = {2026},
  journal = {arXiv preprint arXiv:2606.07555},
  url     = {https://arxiv.org/abs/2606.07555}
}

@article{hu2026conflict,
  title   = {Conflict and Congruency Effects in Large Language Models: In-Weight and In-Context Competition in a Verbal Conflict Task},
  author  = {Hu, Xiaoyang and Angstadt, Mike and Storks, Shane and Huang, Zan and Taxali, Aman and Weigard, Alex and Lewis, Richard L. and Sripada, Chandra},
  year    = {2026},
  journal = {arXiv preprint arXiv:2608.11510},
  url     = {https://arxiv.org/abs/2608.11510}
}

@inproceedings{miceli-barone-etal-2023-larger,
  title     = {The Larger They Are, the Harder They Fail: Language Models Do Not Recognize Identifier Swaps in Python},
  author    = {Miceli Barone, Antonio Valerio and Barez, Fazl and Cohen, Shay B. and Konstas, Ioannis},
  booktitle = {Findings of the Association for Computational Linguistics: ACL 2023},
  year      = {2023},
  pages     = {272--292},
  doi       = {10.18653/v1/2023.findings-acl.19},
  url       = {https://aclanthology.org/2023.findings-acl.19/}
}

@inproceedings{lee-etal-2026-dont,
  title     = {Don't Adapt Small Language Models for Tools; Adapt Tool Schemas to the Models},
  author    = {Lee, Jonggeun and Song, Woojung and Han, Jongwook and Pyun, Haesung and Jo, Yohan},
  booktitle = {Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  year      = {2026},
  pages     = {20695--20719},
  doi       = {10.18653/v1/2026.acl-long.948},
  url       = {https://aclanthology.org/2026.acl-long.948/}
}

@article{abdelsalam2026mechanistic,
  title   = {A Mechanistic Lens on Semantic Conflicts: Using Activation Patching to Understand LLM Behavior},
  author  = {Abdelsalam, Youssef and Peitek, Norman and Maurer, Anna-Maria and Wyrich, Marvin and Apel, Sven},
  year    = {2026},
  journal = {arXiv preprint arXiv:2607.05587},
  url     = {https://arxiv.org/abs/2607.05587}
}

@inproceedings{yu-etal-2023-characterizing,
  title     = {Characterizing Mechanisms for Factual Recall in Language Models},
  author    = {Yu, Qinan and Merullo, Jack and Pavlick, Ellie},
  booktitle = {Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing},
  year      = {2023},
  pages     = {9924--9959},
  doi       = {10.18653/v1/2023.emnlp-main.615},
  url       = {https://aclanthology.org/2023.emnlp-main.615/}
}

@inproceedings{jin-etal-2024-cutting,
  title     = {Cutting Off the Head Ends the Conflict: A Mechanism for Interpreting and Mitigating Knowledge Conflicts in Language Models},
  author    = {Jin, Zhuoran and Cao, Pengfei and Yuan, Hongbang and Chen, Yubo and Xu, Jiexin and Li, Huaijun and Jiang, Xiaojian and Liu, Kang and Zhao, Jun},
  booktitle = {Findings of the Association for Computational Linguistics: ACL 2024},
  year      = {2024},
  doi       = {10.18653/v1/2024.findings-acl.70},
  url       = {https://aclanthology.org/2024.findings-acl.70/}
}

@inproceedings{li-etal-2026-tokdrift,
  title     = {TokDrift: When LLM Speaks in Subwords but Code Speaks in Grammar},
  author    = {Li, Yinxi and Deng, Yuntian and Nie, Pengyu},
  booktitle = {Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  year      = {2026},
  doi       = {10.18653/v1/2026.acl-long.2199},
  url       = {https://aclanthology.org/2026.acl-long.2199/}
}

@inproceedings{wang-etal-2023-grammar,
  title     = {Grammar Prompting for Domain-Specific Language Generation with Large Language Models},
  author    = {Wang, Bailin and Wang, Zi and Wang, Xuezhi and Cao, Yuan and Saurous, Rif A. and Kim, Yoon},
  booktitle = {Advances in Neural Information Processing Systems 36},
  year      = {2023},
  url       = {https://proceedings.neurips.cc/paper_files/paper/2023/hash/cd40d0d65bfebb894ccc9ea822b47fa8-Abstract-Conference.html}
}

@inproceedings{schall-demelo-2025-hidden,
  title     = {The Hidden Cost of Structure: How Constrained Decoding Affects Language Model Performance},
  author    = {Schall, Maximilian and de Melo, Gerard},
  booktitle = {Proceedings of the 15th International Conference on Recent Advances in Natural Language Processing},
  year      = {2025},
  url       = {https://aclanthology.org/2025.ranlp-1.124/}
}

@article{almazrouei2025anka,
  title   = {Anka: A Domain-Specific Language for Reliable LLM Code Generation},
  author  = {Al Mazrouei, Saif Khalfan Saif},
  year    = {2025},
  journal = {arXiv preprint arXiv:2512.23214},
  url     = {https://arxiv.org/abs/2512.23214}
}
```

---

## Final narrow hypothesis and single next experiment

### Narrowest defensible hypothesis

> Conditional on reaching an AST-matched DSL decision site, familiar-token reversion increases super-additively when a strong independently measured competitor prior is paired with an immediate prefix that specifically activates that competitor, even though the remote prompt defines another grammar-valid token as correct and tokenization, semantic role, task meaning, and canonical structure are controlled.

### Single most important next experiment

**Repair the semantic scorer, then run the preregistered 3×3 competitor-prior × local-context factorial experiment with forced-prefix margins and unrestricted canonical-IR generation, using counterbalanced mappings and at least two independently designed grammar families.**

Do not begin the mechanistic phase until this interaction replicates on held-out mappings. That experiment decides whether the refined research program has a real phenomenon to explain.
