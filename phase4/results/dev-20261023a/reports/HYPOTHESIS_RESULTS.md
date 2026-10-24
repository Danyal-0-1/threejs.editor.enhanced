# Hypothesis results — `dev-20261023a`

> **Run** `dev-20261023a` · **stage** DEVELOPMENT · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

| hypothesis | status in this run |
|---|---|
| H1 familiar beats unfamiliar | established in prior literature; not a contribution and not retested |
| H2 prior × context | **NOT TESTABLE** — no calibrated prior-strength (T) or local-context (A) levels exist; deriving them from outcome margins would be circular (review section 6.3) |
| H4 exact-site prediction | NOT RUN (DEVELOPMENT — not confirmatory) |
| H5 targeted repair | NOT RUN |
| Arm B generation | see hurdle below |


## Arm B hurdle

| family | lexicon | model | reach | rev | valid | acc | n_sites |
|---|---|---|---|---|---|---|---|
| blk | d25s3 | asu-rc/deepseek-v4-1-flash | 0.286 | 0.302 | 0.770 | 0.270 | 220 |
| blk | d50s3 | asu-rc/deepseek-v4-1-flash | 0.408 | 0.126 | 0.961 | 0.329 | 272 |
| blk | d75s1a | asu-rc/deepseek-v4-1-flash | 0.056 | 0.474 | 0.900 | 0.037 | 341 |
| blk | d75s2a | asu-rc/deepseek-v4-1-flash | 0.138 | 0.340 | 0.988 | 0.062 | 341 |
| blk | d75s3a | asu-rc/deepseek-v4-1-flash | 0.070 | 0.458 | 0.412 | 0.013 | 341 |
| dom | d25s3 | asu-rc/deepseek-v4-1-flash | 0.386 | 0.165 | 1.000 | 0.257 | 220 |
| dom | d50s3 | asu-rc/deepseek-v4-1-flash | 0.235 | 0.219 | 1.000 | 0.184 | 272 |
| dom | d75s1a | asu-rc/deepseek-v4-1-flash | 0.167 | 0.140 | 0.650 | 0.175 | 341 |
| dom | d75s2a | asu-rc/deepseek-v4-1-flash | 0.179 | 0.279 | 0.838 | 0.075 | 341 |
| dom | d75s3a | asu-rc/deepseek-v4-1-flash | 0.182 | 0.226 | 0.988 | 0.163 | 341 |
| blk | d25s3 | asu-rc/gemma4-31b-it | 0.582 | 0.023 | 0.919 | 0.432 | 220 |
| blk | d50s3 | asu-rc/gemma4-31b-it | 0.768 | 0.014 | 0.974 | 0.618 | 272 |
| blk | d75s1a | asu-rc/gemma4-31b-it | 0.326 | 0.072 | 0.850 | 0.188 | 341 |
| blk | d75s2a | asu-rc/gemma4-31b-it | 0.484 | 0.018 | 0.900 | 0.400 | 341 |
| blk | d75s3a | asu-rc/gemma4-31b-it | 0.264 | 0.144 | 0.450 | 0.125 | 341 |
| dom | d25s3 | asu-rc/gemma4-31b-it | 0.591 | 0.008 | 0.932 | 0.459 | 220 |
| dom | d50s3 | asu-rc/gemma4-31b-it | 0.529 | 0.042 | 0.868 | 0.382 | 272 |
| dom | d75s1a | asu-rc/gemma4-31b-it | 0.463 | 0.076 | 0.738 | 0.400 | 341 |
| dom | d75s2a | asu-rc/gemma4-31b-it | 0.496 | 0.041 | 0.900 | 0.325 | 341 |
| dom | d75s3a | asu-rc/gemma4-31b-it | 0.642 | 0.023 | 0.963 | 0.550 | 341 |
| blk | d25s3 | asu-rc/olmo3-32b-instruct | 0.068 | 0.267 | 0.135 | 0.041 | 220 |
| blk | d50s3 | asu-rc/olmo3-32b-instruct | 0.136 | 0.324 | 0.461 | 0.066 | 272 |
| blk | d75s1a | asu-rc/olmo3-32b-instruct | 0.038 | 0.385 | 0.287 | 0.025 | 341 |
| blk | d75s2a | asu-rc/olmo3-32b-instruct | 0.021 | 0.286 | 0.175 | 0.000 | 341 |
| blk | d75s3a | asu-rc/olmo3-32b-instruct | 0.035 | 0.333 | 0.163 | 0.013 | 341 |
| dom | d25s3 | asu-rc/olmo3-32b-instruct | 0.118 | 0.385 | 0.581 | 0.095 | 220 |
| dom | d50s3 | asu-rc/olmo3-32b-instruct | 0.037 | 0.400 | 0.355 | 0.039 | 272 |
| dom | d75s1a | asu-rc/olmo3-32b-instruct | 0.070 | 0.125 | 0.650 | 0.087 | 341 |
| dom | d75s2a | asu-rc/olmo3-32b-instruct | 0.059 | 0.300 | 0.400 | 0.013 | 341 |
| dom | d75s3a | asu-rc/olmo3-32b-instruct | 0.056 | 0.368 | 0.525 | 0.037 | 341 |
| blk | d25s3 | asu-rc/olmo3-32b-think | 0.173 | 0.421 | 0.689 | 0.122 | 220 |
| blk | d50s3 | asu-rc/olmo3-32b-think | 0.235 | 0.266 | 0.921 | 0.184 | 272 |
| blk | d75s1a | asu-rc/olmo3-32b-think | 0.050 | 0.412 | 0.688 | 0.037 | 341 |
| blk | d75s2a | asu-rc/olmo3-32b-think | 0.047 | 0.188 | 0.475 | 0.037 | 341 |
| blk | d75s3a | asu-rc/olmo3-32b-think | 0.035 | 0.583 | 0.312 | 0.013 | 341 |
| dom | d25s3 | asu-rc/olmo3-32b-think | 0.168 | 0.378 | 0.851 | 0.108 | 220 |
| dom | d50s3 | asu-rc/olmo3-32b-think | 0.162 | 0.386 | 0.803 | 0.092 | 272 |
| dom | d75s1a | asu-rc/olmo3-32b-think | 0.088 | 0.167 | 0.662 | 0.075 | 341 |
| dom | d75s2a | asu-rc/olmo3-32b-think | 0.126 | 0.256 | 0.525 | 0.013 | 341 |
| dom | d75s3a | asu-rc/olmo3-32b-think | 0.065 | 0.227 | 0.762 | 0.025 | 341 |
| blk | d25s3 | asu-rc/olmo3-7b-instruct | 0.009 | 0.500 | 0.068 | 0.000 | 220 |
| blk | d50s3 | asu-rc/olmo3-7b-instruct | 0.004 | 1.000 | 0.013 | 0.000 | 272 |
| blk | d75s1a | asu-rc/olmo3-7b-instruct | 0.009 | 1.000 | 0.263 | 0.000 | 341 |
| blk | d75s2a | asu-rc/olmo3-7b-instruct | 0.000 | — | 0.037 | 0.000 | 341 |
| blk | d75s3a | asu-rc/olmo3-7b-instruct | 0.023 | 0.625 | 0.075 | 0.013 | 341 |
| dom | d25s3 | asu-rc/olmo3-7b-instruct | 0.114 | 0.560 | 0.500 | 0.054 | 220 |
| dom | d50s3 | asu-rc/olmo3-7b-instruct | 0.070 | 0.263 | 0.408 | 0.000 | 272 |
| dom | d75s1a | asu-rc/olmo3-7b-instruct | 0.023 | 0.250 | 0.388 | 0.037 | 341 |
| dom | d75s2a | asu-rc/olmo3-7b-instruct | 0.038 | 0.385 | 0.537 | 0.025 | 341 |
| dom | d75s3a | asu-rc/olmo3-7b-instruct | 0.047 | 0.438 | 0.525 | 0.025 | 341 |
| blk | d25s3 | asu-rc/qwen3-coder-30b-a3b-instruct | 0.386 | 0.118 | 0.703 | 0.324 | 220 |
| blk | d50s3 | asu-rc/qwen3-coder-30b-a3b-instruct | 0.423 | 0.061 | 0.921 | 0.303 | 272 |
| blk | d75s1a | asu-rc/qwen3-coder-30b-a3b-instruct | 0.076 | 0.308 | 0.925 | 0.062 | 341 |
| blk | d75s2a | asu-rc/qwen3-coder-30b-a3b-instruct | 0.120 | 0.244 | 0.675 | 0.062 | 341 |
| blk | d75s3a | asu-rc/qwen3-coder-30b-a3b-instruct | 0.070 | 0.500 | 0.400 | 0.013 | 341 |
| dom | d25s3 | asu-rc/qwen3-coder-30b-a3b-instruct | 0.409 | 0.078 | 0.743 | 0.284 | 220 |
| dom | d50s3 | asu-rc/qwen3-coder-30b-a3b-instruct | 0.162 | 0.250 | 0.921 | 0.118 | 272 |
| dom | d75s1a | asu-rc/qwen3-coder-30b-a3b-instruct | 0.150 | 0.098 | 0.562 | 0.125 | 341 |
| dom | d75s2a | asu-rc/qwen3-coder-30b-a3b-instruct | 0.199 | 0.324 | 0.850 | 0.100 | 341 |
| dom | d75s3a | asu-rc/qwen3-coder-30b-a3b-instruct | 0.126 | 0.256 | 0.912 | 0.075 | 341 |
| blk | d25s3 | asu-rc/qwen35-122b-a10b | 0.218 | 0.312 | 0.554 | 0.216 | 220 |
| blk | d50s3 | asu-rc/qwen35-122b-a10b | 0.522 | 0.042 | 0.987 | 0.421 | 272 |
| blk | d75s1a | asu-rc/qwen35-122b-a10b | 0.135 | 0.174 | 0.850 | 0.100 | 341 |
| blk | d75s2a | asu-rc/qwen35-122b-a10b | 0.282 | 0.135 | 0.887 | 0.175 | 341 |
| blk | d75s3a | asu-rc/qwen35-122b-a10b | 0.097 | 0.364 | 0.350 | 0.025 | 341 |
| dom | d25s3 | asu-rc/qwen35-122b-a10b | 0.300 | 0.227 | 0.824 | 0.189 | 220 |
| dom | d50s3 | asu-rc/qwen35-122b-a10b | 0.210 | 0.070 | 0.737 | 0.105 | 272 |
| dom | d75s1a | asu-rc/qwen35-122b-a10b | 0.196 | 0.119 | 0.675 | 0.150 | 341 |
| dom | d75s2a | asu-rc/qwen35-122b-a10b | 0.208 | 0.254 | 0.800 | 0.075 | 341 |
| dom | d75s3a | asu-rc/qwen35-122b-a10b | 0.229 | 0.077 | 0.875 | 0.212 | 341 |
| blk | d25s3 | asu-rc/qwen35-27b | 0.391 | 0.140 | 0.743 | 0.284 | 220 |
| blk | d50s3 | asu-rc/qwen35-27b | 0.562 | 0.026 | 0.763 | 0.355 | 272 |
| blk | d75s1a | asu-rc/qwen35-27b | 0.158 | 0.167 | 0.838 | 0.100 | 341 |
| blk | d75s2a | asu-rc/qwen35-27b | 0.305 | 0.106 | 0.812 | 0.188 | 341 |
| blk | d75s3a | asu-rc/qwen35-27b | 0.117 | 0.350 | 0.263 | 0.025 | 341 |
| dom | d25s3 | asu-rc/qwen35-27b | 0.123 | 0.037 | 0.189 | 0.054 | 220 |
| dom | d50s3 | asu-rc/qwen35-27b | 0.037 | 0.300 | 0.145 | 0.013 | 272 |
| dom | d75s1a | asu-rc/qwen35-27b | 0.082 | 0.357 | 0.475 | 0.037 | 341 |
| dom | d75s2a | asu-rc/qwen35-27b | 0.155 | 0.208 | 0.525 | 0.050 | 341 |
| dom | d75s3a | asu-rc/qwen35-27b | 0.173 | 0.102 | 0.438 | 0.100 | 341 |
| blk | d25s3 | asu-rc/qwen35-397b-a17b | 0.250 | 0.273 | 0.784 | 0.230 | 220 |
| blk | d50s3 | asu-rc/qwen35-397b-a17b | 0.364 | 0.010 | 0.566 | 0.342 | 272 |
| blk | d75s1a | asu-rc/qwen35-397b-a17b | 0.164 | 0.250 | 0.963 | 0.138 | 341 |
| blk | d75s2a | asu-rc/qwen35-397b-a17b | 0.390 | 0.113 | 0.900 | 0.300 | 341 |
| blk | d75s3a | asu-rc/qwen35-397b-a17b | 0.126 | 0.372 | 0.325 | 0.025 | 341 |
| dom | d25s3 | asu-rc/qwen35-397b-a17b | 0.468 | 0.136 | 0.973 | 0.365 | 220 |
| dom | d50s3 | asu-rc/qwen35-397b-a17b | 0.386 | 0.124 | 1.000 | 0.289 | 272 |
| dom | d75s1a | asu-rc/qwen35-397b-a17b | 0.220 | 0.120 | 0.550 | 0.188 | 341 |
| dom | d75s2a | asu-rc/qwen35-397b-a17b | 0.346 | 0.229 | 0.825 | 0.175 | 341 |
| dom | d75s3a | asu-rc/qwen35-397b-a17b | 0.463 | 0.095 | 0.950 | 0.375 | 341 |
