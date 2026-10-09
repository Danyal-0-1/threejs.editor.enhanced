# Methods and provenance — `smoke-20261006a`

> **Run** `smoke-20261006a` · **stage** SMOKE (development cell) · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

## Configuration

```json
{
 "allow_exploratory": false,
 "allow_non_a100": false,
 "analysis": {
  "B": 200,
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
 "chunk_size": 4,
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
  "d50s1"
 ],
 "lm_head_fp32": true,
 "models": [
  "Qwen/Qwen2.5-Coder-0.5B"
 ],
 "note": "Sol A100 smoke: one cached model, one development lexicon, one family, tiny n.",
 "primary": {
  "ladder": [
   0,
   1,
   2,
   4,
   8
  ],
  "paraphrases": [
   "p0",
   "p1",
   "p2"
  ],
  "site_limit": 6
 },
 "run_id": "smoke-20261006a",
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
 "site_limit": 12,
 "stage": "smoke"
}
```

**Config hash:** `6fde06710358bc63714c6d039403f45442f9a6fc5d9b90fa9c0ba4be3fa159bc`

## Scoring

One canonical scorer (`phase3_2.margins.TokenScorer`): both candidates are tokenised in full with the prefix, the longest common TOKEN prefix `k` is found, and log-probabilities are summed from `k` on both sides, so a candidate that BPE merges into the previous token is still measured (P32-001). Zero-length spans, identical tokenisations and `k = 0` raise and become excluded rows — never a silent 0.0 (P33-001). Output projection in float32 from the final hidden state: **True** (P33-002; bf16 logits quantise near-zero margins, and the sign of the margin is the outcome).

## Prompts

Rendered per lexicon from the φ-map (P33-006) and verified against every site: `rule` (28-role table), `norule` (role list, spellings withheld), `norule_lenmatched` (no-rule padded with content-free lines to the rule prompt's token count, per tokenizer), paraphrases `p0/p1/p2`. Hashes per (lexicon, condition) are in the job manifests.

## Demonstrations

Leakage-free (P33-008): never the site's template, never its program, never a prefix that replays the decision beyond the family's fixed opening. Seeded order per (family, lexicon); every ladder row stores demo ids, order hash and set hash.

## Jobs

| experiment | status | job | node | git | dirty | device | torch | cuda | transformers | models |
|---|---|---|---|---|---|---|---|---|---|---|
| arm_a | COMPLETE | 64809175 | sg023 | 8650df5252 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-0.5B@8123ea2e93 |
| primary | COMPLETE | 64809175 | sg023 | 8650df5252 | True | NVIDIA A100-SXM4-80GB | 2.8.0+cu126 | 12.6 | 4.57.1 | Qwen2.5-Coder-0.5B@8123ea2e93 |

## Materials hashes

```json
{
 "blk_grammar": "3070a10af2f960c018b72dfbdf4525d42cb2d35e3ce0693c3d17c0535baea4f3",
 "phi_d50s1.json": "b6fc5fdb764d85578b7f381e3e0d8182ea105919b4a8e12ed62e020916284b0b",
 "templates": "482a72a7b0e27b2b29e8a6af3001ccaedb2ef8457c2e24b23172cabc84dc8e78",
 "terminals.json": "89a25a4ff6d28295e2002728696b88070908075eb592e7017ea0012499d50db5"
}
```

43 source files hashed (see any job manifest).
