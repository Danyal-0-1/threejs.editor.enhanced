# Table 3. Rule effect: M(table) − M(control), the mean over lexicons of each lexicon's mean

Positive = the table moves the margin toward the correct spelling. 95% template-cluster bootstrap (the same resample applied to every lexicon), B = 2000.

| phase | model | grammar | control | mean_rule_effect | ci95 | excludes_zero |
|---|---|---|---|---|---|---|
| 3.3 | Qwen2.5-Coder 0.5B Instruct | dom | norule | 0.349 | +0.349 [+0.154, +0.581] | True |
| 3.3 | Qwen2.5-Coder 0.5B Instruct | dom | norule_lenmatched | 0.318 | +0.318 [+0.141, +0.525] | True |
| 3.3 | Qwen2.5-Coder 0.5B Instruct | blk | norule | 0.437 | +0.437 [+0.218, +0.658] | True |
| 3.3 | Qwen2.5-Coder 0.5B Instruct | blk | norule_lenmatched | 0.412 | +0.412 [+0.193, +0.623] | True |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | dom | norule | 0.394 | +0.394 [+0.154, +0.646] | True |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | dom | norule_lenmatched | 0.412 | +0.412 [+0.169, +0.663] | True |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | blk | norule | 0.435 | +0.435 [+0.220, +0.662] | True |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | blk | norule_lenmatched | 0.446 | +0.446 [+0.227, +0.677] | True |
| 3.3 | Qwen2.5-Coder 3B Instruct | dom | norule | 0.385 | +0.385 [+0.147, +0.643] | True |
| 3.3 | Qwen2.5-Coder 3B Instruct | dom | norule_lenmatched | 0.384 | +0.384 [+0.146, +0.640] | True |
| 3.3 | Qwen2.5-Coder 3B Instruct | blk | norule | 0.371 | +0.371 [+0.131, +0.617] | True |
| 3.3 | Qwen2.5-Coder 3B Instruct | blk | norule_lenmatched | 0.357 | +0.357 [+0.119, +0.608] | True |
| 3.3 | Qwen2.5-Coder 7B Instruct | dom | norule | 0.320 | +0.320 [+0.092, +0.561] | True |
| 3.3 | Qwen2.5-Coder 7B Instruct | dom | norule_lenmatched | 0.315 | +0.315 [+0.084, +0.556] | True |
| 3.3 | Qwen2.5-Coder 7B Instruct | blk | norule | 0.451 | +0.451 [+0.184, +0.741] | True |
| 3.3 | Qwen2.5-Coder 7B Instruct | blk | norule_lenmatched | 0.443 | +0.443 [+0.174, +0.734] | True |
| 3.3 | Qwen2.5-Coder 14B Instruct | dom | norule | 0.444 | +0.444 [+0.178, +0.731] | True |
| 3.3 | Qwen2.5-Coder 14B Instruct | dom | norule_lenmatched | 0.439 | +0.439 [+0.168, +0.724] | True |
| 3.3 | Qwen2.5-Coder 14B Instruct | blk | norule | 0.597 | +0.597 [+0.334, +0.880] | True |
| 3.3 | Qwen2.5-Coder 14B Instruct | blk | norule_lenmatched | 0.557 | +0.557 [+0.289, +0.842] | True |
| 3.3 | Qwen2.5-Coder 32B Instruct | dom | norule | 0.461 | +0.461 [+0.183, +0.753] | True |
| 3.3 | Qwen2.5-Coder 32B Instruct | dom | norule_lenmatched | 0.476 | +0.476 [+0.204, +0.779] | True |
| 3.3 | Qwen2.5-Coder 32B Instruct | blk | norule | 0.580 | +0.580 [+0.307, +0.857] | True |
| 3.3 | Qwen2.5-Coder 32B Instruct | blk | norule_lenmatched | 0.624 | +0.624 [+0.349, +0.902] | True |
| 3.3 | Qwen2.5 72B Instruct | dom | norule | 0.359 | +0.359 [+0.148, +0.592] | True |
| 3.3 | Qwen2.5 72B Instruct | dom | norule_lenmatched | 0.353 | +0.353 [+0.140, +0.587] | True |
| 3.3 | Qwen2.5 72B Instruct | blk | norule | 0.532 | +0.532 [+0.313, +0.753] | True |
| 3.3 | Qwen2.5 72B Instruct | blk | norule_lenmatched | 0.537 | +0.537 [+0.316, +0.757] | True |
| 3.3 | DeepSeek-Coder 1.3B Instruct | dom | norule | 0.465 | +0.465 [+0.252, +0.701] | True |
| 3.3 | DeepSeek-Coder 1.3B Instruct | dom | norule_lenmatched | 0.445 | +0.445 [+0.229, +0.687] | True |
| 3.3 | DeepSeek-Coder 1.3B Instruct | blk | norule | 0.162 | +0.162 [-0.039, +0.375] | False |
| 3.3 | DeepSeek-Coder 1.3B Instruct | blk | norule_lenmatched | 0.183 | +0.183 [-0.022, +0.401] | False |
| 3.3 | DeepSeek-Coder 33B Instruct | dom | norule | 0.337 | +0.337 [+0.132, +0.554] | True |
| 3.3 | DeepSeek-Coder 33B Instruct | dom | norule_lenmatched | 0.369 | +0.369 [+0.167, +0.578] | True |
| 3.3 | DeepSeek-Coder 33B Instruct | blk | norule | 0.351 | +0.351 [+0.144, +0.587] | True |
| 3.3 | DeepSeek-Coder 33B Instruct | blk | norule_lenmatched | 0.390 | +0.390 [+0.182, +0.626] | True |
| 3.3 | Llama-3.2 1B Instruct | dom | norule | 0.294 | +0.294 [+0.146, +0.449] | True |
| 3.3 | Llama-3.2 1B Instruct | dom | norule_lenmatched | 0.356 | +0.356 [+0.211, +0.517] | True |
| 3.3 | Llama-3.2 1B Instruct | blk | norule | 0.345 | +0.345 [+0.136, +0.552] | True |
| 3.3 | Llama-3.2 1B Instruct | blk | norule_lenmatched | 0.344 | +0.344 [+0.129, +0.556] | True |
| 4 | OLMo 3 7B Instruct | dom | norule | 0.845 | +0.845 [+0.616, +1.104] | True |
| 4 | OLMo 3 7B Instruct | dom | norule_lenmatched | 0.802 | +0.802 [+0.560, +1.076] | True |
| 4 | OLMo 3 7B Instruct | blk | norule | 0.772 | +0.772 [+0.493, +1.065] | True |
| 4 | OLMo 3 7B Instruct | blk | norule_lenmatched | 0.666 | +0.666 [+0.383, +0.949] | True |
| 4 | OLMo 3 32B Instruct | dom | norule | 0.798 | +0.798 [+0.427, +1.171] | True |
| 4 | OLMo 3 32B Instruct | dom | norule_lenmatched | 0.867 | +0.867 [+0.490, +1.246] | True |
| 4 | OLMo 3 32B Instruct | blk | norule | 0.856 | +0.856 [+0.495, +1.235] | True |
| 4 | OLMo 3 32B Instruct | blk | norule_lenmatched | 0.916 | +0.916 [+0.565, +1.294] | True |
| 4 | OLMo 3 32B Think | dom | norule | 0.488 | +0.488 [+0.223, +0.763] | True |
| 4 | OLMo 3 32B Think | dom | norule_lenmatched | 0.520 | +0.520 [+0.256, +0.806] | True |
| 4 | OLMo 3 32B Think | blk | norule | 0.612 | +0.612 [+0.325, +0.908] | True |
| 4 | OLMo 3 32B Think | blk | norule_lenmatched | 0.649 | +0.649 [+0.363, +0.943] | True |
| 4 | Qwen3-Coder 30B-A3B Instruct | dom | norule | 0.545 | +0.545 [+0.252, +0.867] | True |
| 4 | Qwen3-Coder 30B-A3B Instruct | dom | norule_lenmatched | 0.538 | +0.538 [+0.235, +0.864] | True |
| 4 | Qwen3-Coder 30B-A3B Instruct | blk | norule | 0.742 | +0.742 [+0.432, +1.069] | True |
| 4 | Qwen3-Coder 30B-A3B Instruct | blk | norule_lenmatched | 0.767 | +0.767 [+0.442, +1.108] | True |
| 4 | Qwen3.5 27B | dom | norule | 0.485 | +0.485 [+0.276, +0.707] | True |
| 4 | Qwen3.5 27B | dom | norule_lenmatched | 0.487 | +0.487 [+0.286, +0.703] | True |
| 4 | Qwen3.5 27B | blk | norule | 0.433 | +0.433 [+0.225, +0.645] | True |
| 4 | Qwen3.5 27B | blk | norule_lenmatched | 0.434 | +0.434 [+0.216, +0.648] | True |
| 4 | Qwen3.5 122B-A10B | dom | norule | 0.497 | +0.497 [+0.316, +0.677] | True |
| 4 | Qwen3.5 122B-A10B | dom | norule_lenmatched | 0.464 | +0.464 [+0.274, +0.652] | True |
| 4 | Qwen3.5 122B-A10B | blk | norule | 0.546 | +0.546 [+0.324, +0.781] | True |
| 4 | Qwen3.5 122B-A10B | blk | norule_lenmatched | 0.544 | +0.544 [+0.322, +0.779] | True |
| 4 | Qwen3.5 397B-A17B | dom | norule | 0.422 | +0.422 [+0.221, +0.620] | True |
| 4 | Qwen3.5 397B-A17B | dom | norule_lenmatched | 0.441 | +0.441 [+0.234, +0.648] | True |
| 4 | Qwen3.5 397B-A17B | blk | norule | 0.537 | +0.537 [+0.327, +0.765] | True |
| 4 | Qwen3.5 397B-A17B | blk | norule_lenmatched | 0.553 | +0.553 [+0.333, +0.778] | True |
| 4 | Gemma 4 31B | dom | norule | 0.665 | +0.665 [+0.164, +1.182] | True |
| 4 | Gemma 4 31B | dom | norule_lenmatched | 0.424 | +0.424 [-0.099, +0.976] | False |
| 4 | Gemma 4 31B | blk | norule | 0.485 | +0.485 [-0.026, +0.998] | False |
| 4 | Gemma 4 31B | blk | norule_lenmatched | 0.330 | +0.330 [-0.205, +0.835] | False |
| 4 | DeepSeek-V4.1-Flash | dom | norule | 0.336 | +0.336 [+0.161, +0.520] | True |
| 4 | DeepSeek-V4.1-Flash | dom | norule_lenmatched | 0.345 | +0.345 [+0.172, +0.520] | True |
| 4 | DeepSeek-V4.1-Flash | blk | norule | 0.452 | +0.452 [+0.240, +0.661] | True |
| 4 | DeepSeek-V4.1-Flash | blk | norule_lenmatched | 0.423 | +0.423 [+0.219, +0.639] | True |
