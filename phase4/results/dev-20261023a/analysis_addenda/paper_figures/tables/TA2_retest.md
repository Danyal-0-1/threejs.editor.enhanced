# Table A2. Re-scoring a random sample of Arm A sites (rule condition) through the API

From `analysis_addenda/retest/retest_2026-10-24.csv` (tools/retest_api.py): the same request to the same pinned deployment, sent again. The changes come from the server: batching with other users' requests, or differences the API does not show.

| model | sites | same_to_the_bit | median_abs_change | p95_abs_change | max_abs_change | sign_changed | sign_changed_share | sign_changed_within_0_1_nat |
|---|---|---|---|---|---|---|---|---|
| OLMo 3 7B Instruct | 300 | 150 | 0.0000 | 0.3745 | 0.8125 | 1 | 0.0033 | 1 |
| OLMo 3 32B Instruct | 300 | 293 | 0.0000 | 0.0000 | 0.4484 | 0 | 0.0000 | 0 |
| OLMo 3 32B Think | 300 | 299 | 0.0000 | 0.0000 | 0.0166 | 0 | 0.0000 | 0 |
| Qwen3-Coder 30B-A3B Instruct | 300 | 300 | 0.0000 | 0.0000 | 0.0000 | 0 | 0.0000 | 0 |
| Qwen3.5 27B | 300 | 288 | 0.0000 | 0.0000 | 0.6250 | 0 | 0.0000 | 0 |
| Qwen3.5 122B-A10B | 300 | 27 | 0.2028 | 0.7387 | 1.2445 | 20 | 0.0667 | 7 |
| Qwen3.5 397B-A17B | 300 | 300 | 0.0000 | 0.0000 | 0.0000 | 0 | 0.0000 | 0 |
| Gemma 4 31B | 300 | 140 | 0.1145 | 3.7544 | 10.6886 | 14 | 0.0467 | 0 |
| DeepSeek-V4.1-Flash | 300 | 264 | 0.0000 | 0.1982 | 0.6848 | 4 | 0.0133 | 1 |
