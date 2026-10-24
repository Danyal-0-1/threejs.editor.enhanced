# Table A1. Precision: ties and margins next to zero, all three Arm A conditions

share_on_1_32_grid: of a served model's margins between single tokens, the share that is a whole multiple of 1/32 nat. A margin is a difference of two log-probabilities from two requests: when the server rounds its scores and both requests are computed alike, it lands on the grid; batching with other requests moves it off (Table A2). By chance alone the share would be about 0.

| phase | model | arm_a_margins | ties | tie_share | within_1_8_nat | within_share | single_token_margins | share_on_1_32_grid |
|---|---|---|---|---|---|---|---|---|
| 3.3 | Qwen2.5-Coder 0.5B Instruct | 9090 | 0 | 0.0000 | 301 | 0.0331 |  |  |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | 9090 | 0 | 0.0000 | 443 | 0.0487 |  |  |
| 3.3 | Qwen2.5-Coder 3B Instruct | 9090 | 0 | 0.0000 | 494 | 0.0543 |  |  |
| 3.3 | Qwen2.5-Coder 7B Instruct | 9090 | 0 | 0.0000 | 415 | 0.0457 |  |  |
| 3.3 | Qwen2.5-Coder 14B Instruct | 9090 | 0 | 0.0000 | 383 | 0.0421 |  |  |
| 3.3 | Qwen2.5-Coder 32B Instruct | 9090 | 0 | 0.0000 | 381 | 0.0419 |  |  |
| 3.3 | Qwen2.5 72B Instruct | 9090 | 0 | 0.0000 | 365 | 0.0402 |  |  |
| 3.3 | DeepSeek-Coder 1.3B Instruct | 9090 | 0 | 0.0000 | 397 | 0.0437 |  |  |
| 3.3 | DeepSeek-Coder 33B Instruct | 9090 | 0 | 0.0000 | 664 | 0.0730 |  |  |
| 3.3 | Llama-3.2 1B Instruct | 9090 | 0 | 0.0000 | 348 | 0.0383 |  |  |
| 4 | OLMo 3 7B Instruct | 9090 | 85 | 0.0094 | 221 | 0.0243 | 6792 | 0.9230 |
| 4 | OLMo 3 32B Instruct | 9090 | 97 | 0.0107 | 213 | 0.0234 | 6792 | 0.9738 |
| 4 | OLMo 3 32B Think | 9090 | 71 | 0.0078 | 264 | 0.0290 | 6792 | 0.9576 |
| 4 | Qwen3-Coder 30B-A3B Instruct | 9090 | 141 | 0.0155 | 207 | 0.0228 | 6792 | 1.0000 |
| 4 | Qwen3.5 27B | 9090 | 162 | 0.0178 | 348 | 0.0383 | 6792 | 0.9778 |
| 4 | Qwen3.5 122B-A10B | 9090 | 28 | 0.0031 | 431 | 0.0474 | 6792 | 0.1780 |
| 4 | Qwen3.5 397B-A17B | 9090 | 167 | 0.0184 | 357 | 0.0393 | 6792 | 0.9988 |
| 4 | Gemma 4 31B | 9090 | 27 | 0.0030 | 91 | 0.0100 | 6162 | 0.7801 |
| 4 | DeepSeek-V4.1-Flash | 9090 | 0 | 0.0000 | 550 | 0.0605 | 4899 | 0.0000 |
