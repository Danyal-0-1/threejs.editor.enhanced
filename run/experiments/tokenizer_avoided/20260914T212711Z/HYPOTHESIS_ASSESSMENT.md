# Hypothesis assessment — run `20260914T212711Z`

_Verdicts are computed mechanically by the rules frozen in `STUDY_PLAN.md` before any model ran. Nothing here was chosen after seeing the numbers._

| hypothesis | verdict | basis |
|---|---|---|
| **H1** base-model prior | **SUPPORTED** | 12/12 model×language cells have ΔNLL/char > 0 with a 95% paired-bootstrap CI excluding zero |
| **H2** behavioural performance | **SUPPORTED** | 22/24 cells show lower paired accuracy than identity; 15/24 have a CI entirely below zero |
| **H3** scaffolding | **SUPPORTED** | 12/16 model×language cells improved under scaffolding; the identity↔alien gap narrowed in 6/12 cells |
| **H4** tokenization | **SUPPORTED (token cost)** | 24/24 cells needed more prompt tokens than identity for the same information |

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
| `0.5B` | bare | `alpha` | -0.143 | [-0.286, +0.000] | 0.2500 | 3 |
| `0.5B` | bare | `beta` | -0.095 | [-0.238, +0.000] | 0.5000 | 2 |
| `0.5B` | bare | `gamma` | -0.143 | [-0.286, +0.000] | 0.2500 | 3 |
| `0.5B` | scaffolded | `alpha` | -0.048 | [-0.143, +0.000] | 1.0000 | 1 |
| `0.5B` | scaffolded | `beta` | -0.048 | [-0.143, +0.000] | 1.0000 | 1 |
| `0.5B` | scaffolded | `gamma` | -0.048 | [-0.143, +0.000] | 1.0000 | 1 |
| `1.5B` | bare | `alpha` | -0.286 | [-0.476, -0.095] | 0.0312 | 6 |
| `1.5B` | bare | `beta` | -0.238 | [-0.429, -0.095] | 0.0625 | 5 |
| `1.5B` | bare | `gamma` | -0.238 | [-0.429, -0.048] | 0.0625 | 5 |
| `1.5B` | scaffolded | `alpha` | -0.190 | [-0.381, -0.048] | 0.1250 | 4 |
| `1.5B` | scaffolded | `beta` | -0.286 | [-0.476, -0.095] | 0.0312 | 6 |
| `1.5B` | scaffolded | `gamma` | -0.190 | [-0.381, -0.048] | 0.1250 | 4 |
| `3B` | bare | `alpha` | -0.381 | [-0.571, -0.190] | 0.0078 | 8 |
| `3B` | bare | `beta` | +0.095 | [-0.095, +0.286] | 0.6250 | 4 |
| `3B` | bare | `gamma` | -0.190 | [-0.381, -0.048] | 0.1250 | 4 |
| `3B` | scaffolded | `alpha` | -0.381 | [-0.571, -0.190] | 0.0078 | 8 |
| `3B` | scaffolded | `beta` | +0.048 | [+0.000, +0.143] | 1.0000 | 1 |
| `3B` | scaffolded | `gamma` | -0.190 | [-0.429, +0.000] | 0.2188 | 6 |
| `7B` | bare | `alpha` | -0.714 | [-0.905, -0.524] | 0.0001 | 15 |
| `7B` | bare | `beta` | -0.524 | [-0.714, -0.333] | 0.0010 | 11 |
| `7B` | bare | `gamma` | -0.381 | [-0.571, -0.190] | 0.0078 | 8 |
| `7B` | scaffolded | `alpha` | -0.857 | [-1.000, -0.714] | 0.0000 | 18 |
| `7B` | scaffolded | `beta` | -0.381 | [-0.619, -0.143] | 0.0215 | 10 |
| `7B` | scaffolded | `gamma` | -0.524 | [-0.714, -0.286] | 0.0010 | 11 |

With 21 generation cases the discordant-pair counts are small, so the McNemar p-values have little power. Read the effect sizes and intervals.

## H3 — scaffolding

> _Language-neutral scaffolding may improve accuracy and reduce the gap._

| model | language | bare | scaffolded | difference |
|---|---|---:|---:|---:|
| `0.5B` | `identity` | 14.3% | 4.8% | -0.095 |
| `0.5B` | `alpha` | 0.0% | 0.0% | +0.000 |
| `0.5B` | `beta` | 4.8% | 0.0% | -0.048 |
| `0.5B` | `gamma` | 0.0% | 0.0% | +0.000 |
| `1.5B` | `identity` | 42.9% | 57.1% | +0.143 |
| `1.5B` | `alpha` | 14.3% | 38.1% | +0.238 |
| `1.5B` | `beta` | 19.0% | 28.6% | +0.095 |
| `1.5B` | `gamma` | 19.0% | 38.1% | +0.190 |
| `3B` | `identity` | 57.1% | 81.0% | +0.238 |
| `3B` | `alpha` | 19.0% | 42.9% | +0.238 |
| `3B` | `beta` | 66.7% | 85.7% | +0.190 |
| `3B` | `gamma` | 38.1% | 61.9% | +0.238 |
| `7B` | `identity` | 71.4% | 90.5% | +0.190 |
| `7B` | `alpha` | 0.0% | 4.8% | +0.048 |
| `7B` | `beta` | 19.0% | 52.4% | +0.333 |
| `7B` | `gamma` | 33.3% | 38.1% | +0.048 |

**Did scaffolding narrow the identity↔alien gap?**

| model | language | gap (bare) | gap (scaffolded) | narrowed |
|---|---|---:|---:|---|
| `0.5B` | `alpha` | -0.143 | -0.048 | yes |
| `0.5B` | `beta` | -0.095 | -0.048 | yes |
| `0.5B` | `gamma` | -0.143 | -0.048 | yes |
| `1.5B` | `alpha` | -0.286 | -0.190 | yes |
| `1.5B` | `beta` | -0.238 | -0.286 | no |
| `1.5B` | `gamma` | -0.238 | -0.190 | yes |
| `3B` | `alpha` | -0.381 | -0.381 | no |
| `3B` | `beta` | +0.095 | +0.048 | no |
| `3B` | `gamma` | -0.190 | -0.190 | no |
| `7B` | `alpha` | -0.714 | -0.857 | no |
| `7B` | `beta` | -0.524 | -0.381 | yes |
| `7B` | `gamma` | -0.381 | -0.524 | no |

## H4 — tokenization

> _Higher tokenizer fertility should increase token count and computational cost. Its relationship with semantic accuracy is exploratory and must not be assumed._

| model | condition | language | relative fertility | prompt tokens (median) | identity prompt tokens | ratio |
|---|---|---|---:|---:|---:|---:|
| `0.5B` | bare | `alpha` | 1.068× | 720 | 716 | 1.006 |
| `0.5B` | bare | `beta` | 1.401× | 789 | 716 | 1.102 |
| `0.5B` | bare | `gamma` | 1.937× | 808 | 716 | 1.128 |
| `0.5B` | scaffolded | `alpha` | 1.068× | 1175 | 1171 | 1.003 |
| `0.5B` | scaffolded | `beta` | 1.401× | 1244 | 1171 | 1.062 |
| `0.5B` | scaffolded | `gamma` | 1.937× | 1282 | 1171 | 1.095 |
| `1.5B` | bare | `alpha` | 1.068× | 720 | 716 | 1.006 |
| `1.5B` | bare | `beta` | 1.401× | 789 | 716 | 1.102 |
| `1.5B` | bare | `gamma` | 1.937× | 808 | 716 | 1.128 |
| `1.5B` | scaffolded | `alpha` | 1.068× | 1175 | 1171 | 1.003 |
| `1.5B` | scaffolded | `beta` | 1.401× | 1244 | 1171 | 1.062 |
| `1.5B` | scaffolded | `gamma` | 1.937× | 1282 | 1171 | 1.095 |
| `3B` | bare | `alpha` | 1.068× | 720 | 716 | 1.006 |
| `3B` | bare | `beta` | 1.401× | 789 | 716 | 1.102 |
| `3B` | bare | `gamma` | 1.937× | 808 | 716 | 1.128 |
| `3B` | scaffolded | `alpha` | 1.068× | 1175 | 1171 | 1.003 |
| `3B` | scaffolded | `beta` | 1.401× | 1244 | 1171 | 1.062 |
| `3B` | scaffolded | `gamma` | 1.937× | 1282 | 1171 | 1.095 |
| `7B` | bare | `alpha` | 1.068× | 720 | 716 | 1.006 |
| `7B` | bare | `beta` | 1.401× | 789 | 716 | 1.102 |
| `7B` | bare | `gamma` | 1.937× | 808 | 716 | 1.128 |
| `7B` | scaffolded | `alpha` | 1.068× | 1175 | 1171 | 1.003 |
| `7B` | scaffolded | `beta` | 1.401× | 1244 | 1171 | 1.062 |
| `7B` | scaffolded | `gamma` | 1.937× | 1282 | 1171 | 1.095 |

The token-cost half of H4 is confirmatory. The fertility↔accuracy relationship is **descriptive and non-causal**: only three fertility values exist (one per language), and each language changes spelling, tokenization and — for gamma — lexical behaviour simultaneously.

## The predeclared dense-prior rule

Suggestive support requires **all four** conditions:

| condition | met? |
|---|---|
| (a) base ΔNLL/character rises for alien syntax | YES |
| (b) paired canonical semantic accuracy falls for the same languages | YES |
| (c) the pattern is reasonably consistent across model sizes and tasks | YES |
| (d) the evidence does NOT come only from gamma | YES |

**Verdict: SUGGESTIVE SUPPORT.**

**Causality is not established, and cannot be established by this design.** Tokenizer fertility is not controlled: each alien language differs from 3DOM in spelling *and* in how many tokens that spelling costs, at the same time. Gamma carries an additional lexical-reachability defect (24 check-(g) findings). No experiment here manipulates one factor while holding the others fixed.

**This does not select a winning alien syntax**, and it does not make any candidate eligible under Experiment 01's fertility gate.
