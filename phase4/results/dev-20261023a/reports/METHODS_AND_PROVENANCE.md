# Methods and provenance — `dev-20261023a`

> **Run** `dev-20261023a` · **stage** DEVELOPMENT · **status** COMPLETE
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
  "dom",
  "blk"
 ],
 "freeze_path": null,
 "h5": {
  "budget": 3,
  "low_risk_tolerance": 0.02
 },
 "lexicons": [
  "d25s3",
  "d50s3",
  "d75s1a",
  "d75s2a",
  "d75s3a"
 ],
 "lm_head_fp32": true,
 "models": [
  "asu-rc/olmo3-7b-instruct",
  "asu-rc/olmo3-32b-instruct",
  "asu-rc/olmo3-32b-think",
  "asu-rc/qwen3-coder-30b-a3b-instruct",
  "asu-rc/gemma4-31b-it",
  "asu-rc/deepseek-v4-1-flash",
  "asu-rc/qwen35-27b",
  "asu-rc/qwen35-122b-a10b",
  "asu-rc/qwen35-397b-a17b"
 ],
 "note": "Phase 4's first development run (exploratory; the preregistration is a draft): nine models served by the ASU RC API, on exactly the cells of Phase 3.3's held-out run (both grammar families x its five held-out lexicons, every site), with the same settings and seeds, so they compare cell for cell with Phase 3.3's 21 models. H4 and H5 need base twins, which served models do not have.",
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
 "run_id": "dev-20261023a",
 "schema_version": "p4/1",
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

**Config hash:** `c786cd79962fc455eb8c08eec2714954c10be0d6f33eaa081597493f88edae77`

## Scoring

One canonical scorer (`phase3_2.margins.TokenScorer`): both candidates are tokenised in full with the prefix, the longest common TOKEN prefix `k` is found, and log-probabilities are summed from `k` on both sides, so a candidate that BPE merges into the previous token is still measured (P32-001). Zero-length spans, identical tokenisations and `k = 0` raise and become excluded rows — never a silent 0.0 (P33-001). Output projection in float32 from the final hidden state: **True** (P33-002; bf16 logits quantise near-zero margins, and the sign of the margin is the outcome).

## Prompts

Rendered per lexicon from the φ-map (P33-006) and verified against every site: `rule` (28-role table), `norule` (role list, spellings withheld), `norule_lenmatched` (no-rule padded with content-free lines to the rule prompt's token count, per tokenizer), paraphrases `p0/p1/p2`. Hashes per (lexicon, condition) are in the job manifests.

## Demonstrations

Leakage-free (P33-008): never the site's template, never its program, never a prefix that replays the decision beyond the family's fixed opening. Seeded order per (family, lexicon); every ladder row stores demo ids, order hash and set hash.

## Jobs

| experiment | status | job | node | git | dirty | device | torch | cuda | transformers | models |
|---|---|---|---|---|---|---|---|---|---|---|
| arm_a | INTERRUPTED | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-27b@qwen35-27b |
| arm_a | RUNNING | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen3-coder-30b-a3b-instruct@qwen3-code |
| arm_a | RUNNING | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | olmo3-7b-instruct@olmo3-7b-i |
| arm_a | RUNNING | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | deepseek-v4-1-flash@deepseek-v |
| arm_a | RUNNING | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-122b-a10b@qwen35-122 |
| arm_a | RUNNING | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | olmo3-32b-think@olmo3-32b- |
| arm_a | INTERRUPTED | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | gemma4-31b-it@gemma4-31b |
| arm_a | RUNNING | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-397b-a17b@qwen35-397 |
| arm_a | RUNNING | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | olmo3-32b-instruct@olmo3-32b- |
| arm_a | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen3-coder-30b-a3b-instruct@qwen3-code |
| arm_a | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-27b@qwen35-27b |
| arm_a | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | olmo3-7b-instruct@olmo3-7b-i |
| arm_a | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-397b-a17b@qwen35-397 |
| arm_a | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-122b-a10b@qwen35-122 |
| arm_a | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | gemma4-31b-it@gemma4-31b |
| arm_a | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | olmo3-32b-instruct@olmo3-32b- |
| arm_a | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | olmo3-32b-think@olmo3-32b- |
| arm_a | INTERRUPTED | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | deepseek-v4-1-flash@deepseek-v |
| arm_a | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | deepseek-v4-1-flash@deepseek-v |
| armb | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | deepseek-v4-1-flash@deepseek-v |
| armb | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | olmo3-7b-instruct@olmo3-7b-i |
| armb | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | olmo3-32b-instruct@olmo3-32b- |
| armb | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-27b@qwen35-27b |
| armb | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | gemma4-31b-it@gemma4-31b |
| armb | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | olmo3-32b-think@olmo3-32b- |
| armb | INTERRUPTED | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-122b-a10b@qwen35-122 |
| armb | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen3-coder-30b-a3b-instruct@qwen3-code |
| armb | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-122b-a10b@qwen35-122 |
| armb | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-397b-a17b@qwen35-397 |
| primary | RUNNING | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-27b@qwen35-27b |
| primary | RUNNING | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | gemma4-31b-it@gemma4-31b |
| primary | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | olmo3-7b-instruct@olmo3-7b-i |
| primary | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | olmo3-32b-instruct@olmo3-32b- |
| primary | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | gemma4-31b-it@gemma4-31b |
| primary | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-27b@qwen35-27b |
| primary | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen3-coder-30b-a3b-instruct@qwen3-code |
| primary | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | olmo3-32b-think@olmo3-32b- |
| primary | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-122b-a10b@qwen35-122 |
| primary | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | qwen35-397b-a17b@qwen35-397 |
| primary | INTERRUPTED | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | deepseek-v4-1-flash@deepseek-v |
| primary | COMPLETE | local | mesquite-Alienware-m15-R7 | c173cf4a12 | True | NVIDIA GeForce RTX 3080 Ti Laptop GPU | 2.14.0+cu130 | 13.0 | 5.16.1 | deepseek-v4-1-flash@deepseek-v |

## Materials hashes

```json
{
 "blk_grammar": "3070a10af2f960c018b72dfbdf4525d42cb2d35e3ce0693c3d17c0535baea4f3",
 "phi_d25s3.json": "e62d20283c725b6682b80bae60b5ca4f4c85e7fc7a669a33c62aef4d5bf149b7",
 "phi_d50s3.json": "68baa8b14c9c474b90f5d57050d7f58c5ecb4e189a87510afff5a204fbd6975d",
 "phi_d75s1a.json": "0c791fb9aab85bfc9a7b8b319a7b5a7560269bc9fd8c560e390424d69b7d3e45",
 "phi_d75s2a.json": "f798b2eea25b01b76e803e37304a7049f0b1e250893028c71ea4450a173cea18",
 "phi_d75s3a.json": "f7b2e82e4bd9bf375aca1b34762e1393e4cde5678bd7019800a2828b7a186ff4",
 "templates": "482a72a7b0e27b2b29e8a6af3001ccaedb2ef8457c2e24b23172cabc84dc8e78",
 "terminals.json": "89a25a4ff6d28295e2002728696b88070908075eb592e7017ea0012499d50db5"
}
```

57 source files hashed (see any job manifest).
