# Table 3. Worked examples needed to switch (Kaplan–Meier median of k*, sites wrong at 0 examples)

Frozen export (csv/kstar_survival.csv). 'Never switched' = censored at 32 examples. First switch against a switch that holds, pooled over models: see Table 3b.

| model | dom median [95% CI] | dom never switched | dom sites | blk median [95% CI] | blk never switched | blk sites |
|---|---|---|---|---|---|---|
| Qwen2.5-Coder-0.5B | 2.58 [1.25, 6.46] | 12% | 104 | 4.97 [1.85, 11.72] | 20% | 114 |
| Qwen2.5-Coder-0.5B-Instruct | 4.60 [1.58, 12.75] | 12% | 88 | 9.10 [3.70, 12.14] | 21% | 102 |
| Qwen2.5-Coder-1.5B | 3.08 [1.42, 18.73] | 27% | 100 | 5.19 [2.67, 11.68] | 26% | 110 |
| Qwen2.5-Coder-1.5B-Instruct | 3.81 [1.23, 6.54] | 16% | 87 | 9.25 [3.88, 13.37] | 26% | 103 |
| Qwen2.5-Coder-3B | 3.33 [1.23, 14.79] | 27% | 99 | 11.64 [3.00, 18.28] | 28% | 107 |
| Qwen2.5-Coder-3B-Instruct | 3.19 [1.25, 8.78] | 28% | 99 | 7.14 [3.11, 16.33] | 29% | 112 |
| Qwen2.5-Coder-7B | 2.67 [1.59, 7.05] | 19% | 103 | 11.04 [5.86, 18.64] | 23% | 104 |
| Qwen2.5-Coder-7B-Instruct | 2.12 [1.27, 5.48] | 13% | 115 | 10.53 [5.35, 18.49] | 26% | 105 |
| Qwen2.5-Coder-14B | 1.63 [0.99, 3.08] | 8% | 91 | 3.86 [1.85, 10.10] | 13% | 101 |
| Qwen2.5-Coder-14B-Instruct | 3.21 [2.48, 5.99] | 14% | 111 | 6.28 [1.96, 10.29] | 15% | 102 |
| Qwen2.5-Coder-32B | 1.36 [1.04, 2.66] | 13% | 95 | 3.75 [2.29, 8.11] | 12% | 107 |
| Qwen2.5-Coder-32B-Instruct | 1.78 [1.23, 3.97] | 21% | 86 | 3.61 [1.75, 9.93] | 20% | 86 |
| Qwen2.5-72B | 3.35 [1.92, 6.30] | 19% | 83 | 8.43 [3.23, 11.69] | 25% | 93 |
| Qwen2.5-72B-Instruct | 4.20 [2.08, 6.92] | 24% | 89 | 11.22 [7.23, 19.06] | 29% | 97 |
| deepseek-coder-1.3b-base | 3.27 [1.87, 6.26] | 14% | 106 | 5.54 [1.75, 12.67] | 21% | 99 |
| deepseek-coder-1.3b-instruct | 3.62 [1.77, 7.12] | 15% | 104 | 5.91 [3.17, 11.99] | 18% | 109 |
| deepseek-coder-33b-base | 1.94 [1.46, 3.05] | 10% | 92 | 3.33 [1.88, 10.90] | 12% | 92 |
| deepseek-coder-33b-instruct | 3.08 [1.88, 4.75] | 13% | 98 | 3.47 [1.97, 6.81] | 12% | 98 |
| Llama-3.2-1B | 1.49 [0.96, 3.63] | 9% | 114 | 6.86 [2.17, 11.41] | 20% | 126 |
| Llama-3.2-1B-Instruct | 1.57 [0.87, 3.02] | 6% | 102 | 3.58 [1.39, 13.29] | 18% | 102 |
| starcoder2-3b | 2.40 [1.25, 4.76] | 19% | 109 | 6.38 [2.46, 14.64] | 18% | 109 |
