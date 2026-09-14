# Hypothesis assessment — run `20260914T212711Z`

_Verdicts are computed mechanically by the rules frozen in `STUDY_PLAN.md` before any model ran. Nothing here was chosen after seeing the numbers._

| hypothesis | verdict | basis |
|---|---|---|
| **H1** base-model prior | **SUPPORTED** | 12/12 model×language cells have ΔNLL/char > 0 with a 95% paired-bootstrap CI excluding zero |
| **H2** behavioural performance | **MIXED** | 3/6 cells show lower paired accuracy than identity; 0/6 have a CI entirely below zero |
| **H3** scaffolding | **NOT SUPPORTED** | 0/4 model×language cells improved under scaffolding; the identity↔alien gap narrowed in 3/3 cells |
| **H4** tokenization | **SUPPORTED (token cost)** | 6/6 cells needed more prompt tokens than identity for the same information |

## H1 — base-model prior

> _For semantically matched programs, alien languages will have higher NLL/character than identity._

| base model | language | ΔNLL/char | 95% CI | CI excludes 0 |
|---|---|---:|---|---|
| `0.5B` | `alpha` | +0.5525 | [+0.5059, +0.6005] | yes |
| `0.5B` | `beta` | +1.7235 | [+1.6256, +1.8126] | yes |
| `0.5B` | `gamma` | +2.8189 | [+2.6293, +2.9919] | yes |
| `1.5B` | `alpha` | +0.6311 | [+0.5867, +0.6778] | yes |
| `1.5B` | `beta` | +1.7079 | [+1.6159, +1.7901] | yes |
| `1.5B` | `gamma` | +3.1218 | [+2.9225, +3.3056] | yes |
| `3B` | `alpha` | +0.6530 | [+0.6089, +0.6991] | yes |
| `3B` | `beta` | +1.6631 | [+1.5701, +1.7472] | yes |
| `3B` | `gamma` | +2.6647 | [+2.4849, +2.8321] | yes |
| `7B [cpu]` | `alpha` | +0.5871 | [+0.5409, +0.6355] | yes |
| `7B [cpu]` | `beta` | +1.5910 | [+1.5094, +1.6659] | yes |
| `7B [cpu]` | `gamma` | +2.7822 | [+2.5852, +2.9682] | yes |

## H2 — behavioural performance

> _Under information-matched prompts, alien-language generations may have lower canonical-IR accuracy than identity._

| model | condition | language | paired Δaccuracy | 95% CI | McNemar p | discordant pairs |
|---|---|---|---:|---|---:|---:|
| `0.5B` | bare | `alpha` | -0.111 | [-0.333, +0.000] | 1.0000 | 1 |
| `0.5B` | bare | `beta` | -0.111 | [-0.333, +0.000] | 1.0000 | 1 |
| `0.5B` | bare | `gamma` | -0.111 | [-0.333, +0.000] | 1.0000 | 1 |
| `0.5B` | scaffolded | `alpha` | +0.000 | [+0.000, +0.000] | 1.0000 | 0 |
| `0.5B` | scaffolded | `beta` | +0.000 | [+0.000, +0.000] | 1.0000 | 0 |
| `0.5B` | scaffolded | `gamma` | +0.000 | [+0.000, +0.000] | 1.0000 | 0 |

With 21 generation cases the discordant-pair counts are small, so the McNemar p-values have little power. Read the effect sizes and intervals.

## H3 — scaffolding

> _Language-neutral scaffolding may improve accuracy and reduce the gap._

| model | language | bare | scaffolded | difference |
|---|---|---:|---:|---:|
| `0.5B` | `identity` | 11.1% | 0.0% | -0.111 |
| `0.5B` | `alpha` | 0.0% | 0.0% | +0.000 |
| `0.5B` | `beta` | 0.0% | 0.0% | +0.000 |
| `0.5B` | `gamma` | 0.0% | 0.0% | +0.000 |

**Did scaffolding narrow the identity↔alien gap?**

| model | language | gap (bare) | gap (scaffolded) | narrowed |
|---|---|---:|---:|---|
| `0.5B` | `alpha` | -0.111 | +0.000 | yes |
| `0.5B` | `beta` | -0.111 | +0.000 | yes |
| `0.5B` | `gamma` | -0.111 | +0.000 | yes |

## H4 — tokenization

> _Higher tokenizer fertility should increase token count and computational cost. Its relationship with semantic accuracy is exploratory and must not be assumed._

| model | condition | language | relative fertility | prompt tokens (median) | identity prompt tokens | ratio |
|---|---|---|---:|---:|---:|---:|
| `0.5B` | bare | `alpha` | 1.068× | 719 | 715 | 1.006 |
| `0.5B` | bare | `beta` | 1.401× | 788 | 715 | 1.102 |
| `0.5B` | bare | `gamma` | 1.937× | 807 | 715 | 1.129 |
| `0.5B` | scaffolded | `alpha` | 1.068× | 1174 | 1170 | 1.003 |
| `0.5B` | scaffolded | `beta` | 1.401× | 1243 | 1170 | 1.062 |
| `0.5B` | scaffolded | `gamma` | 1.937× | 1281 | 1170 | 1.095 |

The token-cost half of H4 is confirmatory. The fertility↔accuracy relationship is **descriptive and non-causal**: only three fertility values exist (one per language), and each language changes spelling, tokenization and — for gamma — lexical behaviour simultaneously.

## The predeclared dense-prior rule

Suggestive support requires **all four** conditions:

| condition | met? |
|---|---|
| (a) base ΔNLL/character rises for alien syntax | YES |
| (b) paired canonical semantic accuracy falls for the same languages | NO |
| (c) the pattern is reasonably consistent across model sizes and tasks | NO |
| (d) the evidence does NOT come only from gamma | NO |

**Verdict: NOT ALL CONDITIONS MET.**

**Causality is not established, and cannot be established by this design.** Tokenizer fertility is not controlled: each alien language differs from 3DOM in spelling *and* in how many tokens that spelling costs, at the same time. Gamma carries an additional lexical-reachability defect (24 check-(g) findings). No experiment here manipulates one factor while holding the others fixed.

**This does not select a winning alien syntax**, and it does not make any candidate eligible under Experiment 01's fertility gate.
