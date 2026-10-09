# Methods and provenance — `heldout-20261007a`

> **Run** `heldout-20261007a` · **stage** HELD-OUT · **status** COMPLETE
>
> Held-out evaluation under DEV_FREEZE; see criteria below. blk results are a WEAKER family test (deviation D1), never a held-out-grammar confirmation.

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
 "freeze_path": "/home/dkhorami/phase3-3_experiment_sol/results/dev-20261006a/DEV_FREEZE.json",
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
  "Qwen/Qwen2.5-Coder-0.5B",
  "Qwen/Qwen2.5-Coder-0.5B-Instruct",
  "Qwen/Qwen2.5-Coder-1.5B",
  "Qwen/Qwen2.5-Coder-1.5B-Instruct",
  "Qwen/Qwen2.5-Coder-3B",
  "Qwen/Qwen2.5-Coder-3B-Instruct",
  "deepseek-ai/deepseek-coder-1.3b-base",
  "deepseek-ai/deepseek-coder-1.3b-instruct",
  "meta-llama/Llama-3.2-1B",
  "meta-llama/Llama-3.2-1B-Instruct",
  "bigcode/starcoder2-3b",
  "Qwen/Qwen2.5-Coder-7B",
  "Qwen/Qwen2.5-Coder-7B-Instruct",
  "Qwen/Qwen2.5-Coder-14B",
  "Qwen/Qwen2.5-Coder-14B-Instruct",
  "Qwen/Qwen2.5-Coder-32B",
  "Qwen/Qwen2.5-Coder-32B-Instruct",
  "deepseek-ai/deepseek-coder-33b-base",
  "deepseek-ai/deepseek-coder-33b-instruct",
  "Qwen/Qwen2.5-72B",
  "Qwen/Qwen2.5-72B-Instruct"
 ],
 "note": "Held-out evaluation. Models 11-20 added 2026-10-07 by deviation D10 (scale: Qwen2.5-Coder 7B/14B/32B, DeepSeek-Coder-33B, Qwen2.5-72B on 2 GPUs). Appended so models 0-10 keep their array indices. Previous note: Held-out mappings x (dev + held-out models <=3B). blk cells are HELDOUT-WEAK-FAMILY (D1); 3B is HELDOUT-WEAKENED (D2). Requires DEV_FREEZE + unlock.",
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
 "run_id": "heldout-20261007a",
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
 "stage": "heldout"
}
```

**Config hash:** `d664de71837d9e9a078525b2472f678c79a68138314ac90a2c576a30d95f6a99`

## Scoring

One canonical scorer (`phase3_2.margins.TokenScorer`): both candidates are tokenised in full with the prefix, the longest common TOKEN prefix `k` is found, and log-probabilities are summed from `k` on both sides, so a candidate that BPE merges into the previous token is still measured (P32-001). Zero-length spans, identical tokenisations and `k = 0` raise and become excluded rows — never a silent 0.0 (P33-001). Output projection in float32 from the final hidden state: **True** (P33-002; bf16 logits quantise near-zero margins, and the sign of the margin is the outcome).

## Prompts

Rendered per lexicon from the φ-map (P33-006) and verified against every site: `rule` (28-role table), `norule` (role list, spellings withheld), `norule_lenmatched` (no-rule padded with content-free lines to the rule prompt's token count, per tokenizer), paraphrases `p0/p1/p2`. Hashes per (lexicon, condition) are in the job manifests.

## Demonstrations

Leakage-free (P33-008): never the site's template, never its program, never a prefix that replays the decision beyond the family's fixed opening. Seeded order per (family, lexicon); every ladder row stores demo ids, order hash and set hash.

## Jobs

| experiment | status | job | node | git | dirty | device | torch | cuda | transformers | models |
|---|---|---|---|---|---|---|---|---|---|---|
| arm_a | COMPLETE | 64943130 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | deepseek-coder-33b-instruct@61dc97b922 |
| arm_a | COMPLETE | 64943131 | sg025 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-72B-Instruct@495f39366e |
| arm_a | COMPLETE | 64943137 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-0.5B@8123ea2e93 |
| arm_a | COMPLETE | 64943843 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-0.5B-Instruct@ea3f2471cf |
| arm_a | COMPLETE | 64944483 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-1.5B@df3ce67c0e |
| arm_a | COMPLETE | 64945338 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-1.5B-Instruct@2e1fd397ee |
| arm_a | COMPLETE | 64945845 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-3B@09d9bc5d37 |
| arm_a | COMPLETE | 64946580 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-3B-Instruct@488639f1ff |
| arm_a | COMPLETE | 64947201 | sg025 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | deepseek-coder-1.3b-base@c919139c3a |
| arm_a | COMPLETE | 64947740 | sg020 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | deepseek-coder-1.3b-instruct@e063262dac |
| arm_a | COMPLETE | 64948214 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Llama-3.2-1B@4e20de3624 |
| arm_a | COMPLETE | 64948542 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Llama-3.2-1B-Instruct@9213176726 |
| arm_a | COMPLETE | 64948976 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | starcoder2-3b@733247c55e |
| arm_a | COMPLETE | 64949556 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-7B@0396a76181 |
| arm_a | COMPLETE | 64950416 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-7B-Instruct@c03e6d3582 |
| arm_a | COMPLETE | 64951379 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-14B@f2ad5164aa |
| arm_a | COMPLETE | 64953093 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-14B-Instruct@aedcc2d42b |
| arm_a | COMPLETE | 64954786 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-32B@2e12b5f7bc |
| arm_a | COMPLETE | 64957776 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-32B-Instruct@381fc969f7 |
| arm_a | COMPLETE | 64960922 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | deepseek-coder-33b-base@45c85cadf3 |
| arm_a | COMPLETE | 64972804 | sg025 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-72B@efba10c8e5 |
| armb | COMPLETE | 64943132 | sg020 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | deepseek-coder-33b-instruct@61dc97b922 |
| armb | COMPLETE | 64943133 | sg022 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-72B-Instruct@495f39366e |
| armb | COMPLETE | 64989110 | sg009 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-0.5B-Instruct@ea3f2471cf |
| armb | COMPLETE | 64993878 | sg009 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-1.5B-Instruct@2e1fd397ee |
| armb | COMPLETE | 64999498 | sg009 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-3B-Instruct@488639f1ff |
| armb | COMPLETE | 65005128 | sg009 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | deepseek-coder-1.3b-instruct@e063262dac |
| armb | COMPLETE | 65009912 | sg007 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Llama-3.2-1B-Instruct@9213176726 |
| armb | COMPLETE | 65011352 | sg007 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-7B-Instruct@c03e6d3582 |
| armb | COMPLETE | 65013394 | sg015 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-14B-Instruct@aedcc2d42b |
| armb | COMPLETE | 65016312 | sg015 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-32B-Instruct@381fc969f7 |
| h5 | COMPLETE | 64943134 | sg004 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | deepseek-coder-33b-instruct@61dc97b922 |
| h5 | COMPLETE | 64943135 | sg027 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-72B-Instruct@495f39366e |
| h5 | COMPLETE | 65052395 | sg022 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-0.5B-Instruct@ea3f2471cf |
| h5 | COMPLETE | 65053680 | sg022 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-1.5B-Instruct@2e1fd397ee |
| h5 | COMPLETE | 65055241 | sg022 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-3B-Instruct@488639f1ff |
| h5 | COMPLETE | 65057230 | sg022 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | deepseek-coder-1.3b-instruct@e063262dac |
| h5 | COMPLETE | 65058641 | sg022 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Llama-3.2-1B-Instruct@9213176726 |
| h5 | COMPLETE | 65059694 | sg019 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-7B-Instruct@c03e6d3582 |
| h5 | COMPLETE | 65061426 | sg019 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-14B-Instruct@aedcc2d42b |
| h5 | COMPLETE | 65063991 | sg013 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-32B-Instruct@381fc969f7 |
| primary | COMPLETE | 64943130 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | deepseek-coder-33b-instruct@61dc97b922 |
| primary | COMPLETE | 64943131 | sg025 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-72B-Instruct@495f39366e |
| primary | COMPLETE | 64943137 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-0.5B@8123ea2e93 |
| primary | COMPLETE | 64943843 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-0.5B-Instruct@ea3f2471cf |
| primary | COMPLETE | 64944483 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-1.5B@df3ce67c0e |
| primary | COMPLETE | 64945338 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-1.5B-Instruct@2e1fd397ee |
| primary | COMPLETE | 64945845 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-3B@09d9bc5d37 |
| primary | COMPLETE | 64946580 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-3B-Instruct@488639f1ff |
| primary | COMPLETE | 64947201 | sg025 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | deepseek-coder-1.3b-base@c919139c3a |
| primary | COMPLETE | 64947740 | sg020 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | deepseek-coder-1.3b-instruct@e063262dac |
| primary | COMPLETE | 64948214 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Llama-3.2-1B@4e20de3624 |
| primary | COMPLETE | 64948542 | sg014 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Llama-3.2-1B-Instruct@9213176726 |
| primary | COMPLETE | 64948976 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | starcoder2-3b@733247c55e |
| primary | COMPLETE | 64949556 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-7B@0396a76181 |
| primary | COMPLETE | 64950416 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-7B-Instruct@c03e6d3582 |
| primary | COMPLETE | 64951379 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-14B@f2ad5164aa |
| primary | COMPLETE | 64953093 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-14B-Instruct@aedcc2d42b |
| primary | COMPLETE | 64954786 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-32B@2e12b5f7bc |
| primary | COMPLETE | 64957776 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-32B-Instruct@381fc969f7 |
| primary | COMPLETE | 64960922 | sg005 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | deepseek-coder-33b-base@45c85cadf3 |
| primary | COMPLETE | 64972804 | sg025 | 78b2bcdbf2 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-72B@efba10c8e5 |

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

44 source files hashed (see any job manifest).
