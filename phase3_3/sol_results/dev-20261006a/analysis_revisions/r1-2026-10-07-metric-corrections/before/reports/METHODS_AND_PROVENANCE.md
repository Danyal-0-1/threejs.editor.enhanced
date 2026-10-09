# Methods and provenance — `dev-20261006a`

> **Run** `dev-20261006a` · **stage** DEVELOPMENT · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

## Configuration

```json
{
 "allow_exploratory": false,
 "allow_non_a100": false,
 "analysis": {
  "B": 2000,
  "alpha": 0.05,
  "ece_bins": 10,
  "min_clusters": 8,
  "precision_at_k": [
   10,
   50
  ],
  "unit": "template"
 },
 "arm_a": {
  "conditions": [
   "rule",
   "norule",
   "norule_lenmatched"
  ],
  "program_nll": true
 },
 "armb": {
  "do_sample": false,
  "max_new_tokens": 192,
  "n_demos": 4,
  "num_beams": 1,
  "template_limit": 0
 },
 "chunk_size": 64,
 "dtype": "bfloat16",
 "families": [
  "dom"
 ],
 "freeze_path": null,
 "h5": {
  "budget": 3,
  "low_risk_tolerance": 0.02
 },
 "lexicons": [
  "d25s1",
  "d25s2",
  "d50s1",
  "d50s2"
 ],
 "lm_head_fp32": true,
 "models": [
  "Qwen/Qwen2.5-Coder-0.5B",
  "Qwen/Qwen2.5-Coder-0.5B-Instruct",
  "Qwen/Qwen2.5-Coder-1.5B",
  "Qwen/Qwen2.5-Coder-1.5B-Instruct"
 ],
 "note": "Registered development cells only (PREREGISTRATION \u00a72 + D8).",
 "primary": {
  "ladder": [
   0,
   1,
   2,
   4,
   8,
   16,
   32
  ],
  "paraphrases": [
   "p0",
   "p1",
   "p2"
  ],
  "site_limit": 400
 },
 "run_id": "dev-20261006a",
 "schema_version": "p33/1",
 "seeds": {
  "bootstrap": 20261002,
  "demo_order": 20261005,
  "h5_random": [
   1,
   2,
   3,
   4,
   5
  ],
  "power": 20261006
 },
 "site_limit": 0,
 "stage": "dev"
}
```

**Config hash:** `80a2d30e93d3b8aa3e7f2a398d9354601530ccb9093bf23bc04c4de28658a49b`

## Scoring

One canonical scorer (`phase3_2.margins.TokenScorer`): both candidates are tokenised in full with the prefix, the longest common TOKEN prefix `k` is found, and log-probabilities are summed from `k` on both sides, so a candidate that BPE merges into the previous token is still measured (P32-001). Zero-length spans, identical tokenisations and `k = 0` raise and become excluded rows — never a silent 0.0 (P33-001). Output projection in float32 from the final hidden state: **True** (P33-002; bf16 logits quantise near-zero margins, and the sign of the margin is the outcome).

## Prompts

Rendered per lexicon from the φ-map (P33-006) and verified against every site: `rule` (28-role table), `norule` (role list, spellings withheld), `norule_lenmatched` (no-rule padded with content-free lines to the rule prompt's token count, per tokenizer), paraphrases `p0/p1/p2`. Hashes per (lexicon, condition) are in the job manifests.

## Demonstrations

Leakage-free (P33-008): never the site's template, never its program, never a prefix that replays the decision beyond the family's fixed opening. Seeded order per (family, lexicon); every ladder row stores demo ids, order hash and set hash.

## Jobs

| experiment | status | job | node | git | dirty | device | torch | cuda | transformers | models |
|---|---|---|---|---|---|---|---|---|---|---|
| arm_a | COMPLETE | 64811905 | sg038 | 8650df5252 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-1.5B-Instruct@2e1fd397ee |
| arm_a | COMPLETE | 64811964 | sg038 | 8650df5252 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-0.5B@8123ea2e93 |
| arm_a | COMPLETE | 64812133 | sg038 | 8650df5252 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-0.5B-Instruct@ea3f2471cf |
| arm_a | COMPLETE | 64812372 | sg038 | 8650df5252 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-1.5B@df3ce67c0e |
| primary | COMPLETE | 64811906 | sg038 | 8650df5252 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-1.5B-Instruct@2e1fd397ee |
| primary | COMPLETE | 64813140 | sg038 | 8650df5252 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-0.5B@8123ea2e93 |
| primary | COMPLETE | 64813366 | sg038 | 8650df5252 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-0.5B-Instruct@ea3f2471cf |
| primary | COMPLETE | 64813796 | sg038 | 8650df5252 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-1.5B@df3ce67c0e |

## Materials hashes

```json
{
 "blk_grammar": "3070a10af2f960c018b72dfbdf4525d42cb2d35e3ce0693c3d17c0535baea4f3",
 "phi_d25s1.json": "16a2e9b3a6ad2998ea152fbb6de454c4fb4c3ea50b36db5d789059bb3ca7cbd8",
 "phi_d25s2.json": "c35af4593551f8e452908ed28458a8628af4db6f47c8dbf934b08863a9a00f65",
 "phi_d50s1.json": "b6fc5fdb764d85578b7f381e3e0d8182ea105919b4a8e12ed62e020916284b0b",
 "phi_d50s2.json": "5e4101448086a47e2aa8f0bd24ce76e8b5e7610448c8d35b70b2e3ecd6401ccd",
 "templates": "482a72a7b0e27b2b29e8a6af3001ccaedb2ef8457c2e24b23172cabc84dc8e78",
 "terminals.json": "89a25a4ff6d28295e2002728696b88070908075eb592e7017ea0012499d50db5"
}
```

43 source files hashed (see any job manifest).
