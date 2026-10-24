# Figures: Phase 4's served models beside Phase 3.3 (dev-20261023a)

Each figure is in PDF, SVG and 300-dpi PNG; `ALL_FIGURES.pdf` has them all. The numbers are in `tables/`.

**Status:** Phase 4's numbers are development results (exploratory): `phase4/PREREGISTRATION.md` was a draft when the run was made. Phase 3.3's are its registered held-out results, on the same cells.

## fig1_reversion

**The served models, like Phase 3.3's, often prefer the familiar spelling even with the token table in the prompt.** Each row is a model; Phase 3.3's instruct models (top) and Phase 4's served models (bottom) were scored on the same sites with the same prompts. (a) dom, (b) blk grammar. Filled circles: share of decision sites where the familiar spelling scores higher than the correct one (M < 0) with the token table, with 95% template-cluster bootstrap intervals; open circles: without the table; bars: the length-matched control. With the table, Phase 4: dom 0.40–0.47, blk 0.41–0.51; Phase 3.3: dom 0.40–0.52, blk 0.44–0.53 (Table 2). Phase 4's numbers are development results (exploratory).

## fig2_rule_effect

**The token table moves every served model's margins toward the correct spelling, but not far enough to remove reversion.** Mean change in the margin M when the token table is added, (a) dom, (b) blk: against the prompt without the table (filled) and against a length-matched control (open), with 95% template-cluster bootstrap intervals. Phase 4, against no table: dom 0.34–0.84, blk 0.43–0.86 nats; the interval excludes zero (positive) in 17 of 18 served model × grammar groups (Table 3).

## fig3_scale

**Size alone does not remove reversion.** Reversion with the token table against total parameters (log scale), (a) dom, (b) blk; every instruct model of both phases, coloured by family, with 95% template-cluster bootstrap intervals (grey). Lines join one family's sizes: Qwen2.5-Coder 0.5–32B and Qwen2.5 72B (Phase 3.3), Qwen3.5 27B, 122B and 397B and OLMo 3 7B and 32B (Phase 4). Open markers: mixtures of experts, plotted at total parameters (active parameters are in Table 1). Sizes are not randomized; these are associations, and Phase 4's served models also differ in precision (Table 1).

## fig4_adaptation

**Worked examples switch the served models' wrong sites as they switched Phase 3.3's.** Sites wrong with zero examples (M < 0), given 0–32 leak-free worked examples in the target lexicon. (a) Kaplan–Meier share not yet switched, pooled over each phase's models (dotted: Phase 3.3; solid: Phase 4); black dom, grey blk. (b) Kaplan–Meier median per model with 95% template-cluster bootstrap intervals (each run's export). Phase 4 medians: dom 1.68–9.44, blk 1.89–15.33 examples; Phase 3.3: dom 1.57–4.60, blk 3.47–11.22 (Table 4). A rounding fault in the Kaplan–Meier code, inherited from Phase 3.3, can move a median to the next switch when the survival curve is exactly 1/2 there (explanations/phase4/api_models_results_explained/08, §6).

## fig5_generation

**In free generation the served models reach more decision sites than Phase 3.3's, and write the familiar spelling less often at them, with large differences between models.** Greedy generation from a natural-language request, with the token table and four worked examples in the prompt; each row is an instruct model of either phase. (a) Share of decision sites the program reaches (the generated text equals the target up to the site, after whitespace normalization). (b) Share of reached sites where the model writes the familiar spelling. 95% template-cluster bootstrap intervals; the two rates are never multiplied. Phase 4: reach 5567/27270 (20.4%), reversion given reach 827/5567 (14.9%), correct programs 1041/7020 (14.8%); Phase 3.3: reach 4104/30300 (13.5%), reversion given reach 812/4104 (19.8%), correct programs 747/7800 (9.6%) (Table 5). Some served models ended their turn at once, writing nothing (share of generations: OLMo 3 32B Instruct 43%; OLMo 3 7B Instruct 37%; Qwen3.5 397B-A17B 6%); Phase 3.3's models never did.

## figA1_precision

**Rounded scores give the served models exact ties, but do not crowd their margins near zero.** For every model, with the token table: (a) the share of margins that are exactly zero (a tie: neither spelling preferred), (b) the share within 1/8 nat of zero, where a rounded score can carry the wrong sign. Phase 3.3 computed its output layer in fp32 and had no ties. Phase 4: 778 ties in 81810 Arm A margins (all three conditions). Share of single-token margins on the 1/32-nat grid of rounded (bf16) scores: Qwen3-Coder 30B-A3B Instruct 1.00, Qwen3.5 397B-A17B 1.00, Qwen3.5 27B 0.98, OLMo 3 32B Instruct 0.97, OLMo 3 32B Think 0.96, OLMo 3 7B Instruct 0.92, Gemma 4 31B 0.78, Qwen3.5 122B-A10B 0.18, DeepSeek-V4.1-Flash 0.00 (Table A1). A tie is not counted as a reversion.

## figA2_retest

**The same request does not always return the same margin.** A fixed random sample of Arm A sites (with the token table) per served model was scored again, by the same pinned deployment, after the run. (a) Absolute change in the margin: median to 95th percentile, and the largest (log scale; changes of 0 are drawn at 10⁻⁴). (b) Share of sites whose margin changed sign, which flips the site between reverted and not. Overall 39 of 2700 re-scored sites changed sign (Table A2). Every answer came from the pinned deployment, so the variation is on the server's side: batching with other users' requests changes the arithmetic order, and for some deployments the changes are far larger than one rounding step.

