# Table 4. Worked examples to switch: Kaplan-Meier median over sites wrong with none

Exported by each run (csv/kstar_survival.csv). 'Never switched' = censored at 32 examples.

| phase | model | grammar | initially_wrong | switched | never_switched | km_median | ci95 |
|---|---|---|---|---|---|---|---|
| 3.3 | Qwen2.5-Coder 0.5B Instruct | dom | 88 | 77 | 11 | 4.60239 | [1.58371, 12.7504] |
| 3.3 | Qwen2.5-Coder 0.5B Instruct | blk | 102 | 81 | 21 | 9.09806 | [3.69952, 12.1358] |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | dom | 87 | 73 | 14 | 3.80592 | [1.22746, 6.54455] |
| 3.3 | Qwen2.5-Coder 1.5B Instruct | blk | 103 | 76 | 27 | 9.24575 | [3.88431, 13.3699] |
| 3.3 | Qwen2.5-Coder 3B Instruct | dom | 99 | 71 | 28 | 3.19036 | [1.25331, 8.78441] |
| 3.3 | Qwen2.5-Coder 3B Instruct | blk | 112 | 80 | 32 | 7.14216 | [3.11243, 16.3262] |
| 3.3 | Qwen2.5-Coder 7B Instruct | dom | 115 | 100 | 15 | 2.1184 | [1.27496, 5.47815] |
| 3.3 | Qwen2.5-Coder 7B Instruct | blk | 105 | 78 | 27 | 10.5342 | [5.35245, 18.4874] |
| 3.3 | Qwen2.5-Coder 14B Instruct | dom | 111 | 95 | 16 | 3.21038 | [2.4807, 5.99424] |
| 3.3 | Qwen2.5-Coder 14B Instruct | blk | 102 | 87 | 15 | 6.27853 | [1.95502, 10.294] |
| 3.3 | Qwen2.5-Coder 32B Instruct | dom | 86 | 68 | 18 | 1.78338 | [1.2297, 3.97205] |
| 3.3 | Qwen2.5-Coder 32B Instruct | blk | 86 | 69 | 17 | 3.60567 | [1.75283, 9.93231] |
| 3.3 | Qwen2.5 72B Instruct | dom | 89 | 68 | 21 | 4.19518 | [2.0833, 6.924] |
| 3.3 | Qwen2.5 72B Instruct | blk | 97 | 69 | 28 | 11.2236 | [7.23467, 19.0616] |
| 3.3 | DeepSeek-Coder 1.3B Instruct | dom | 104 | 88 | 16 | 3.62268 | [1.76797, 7.12379] |
| 3.3 | DeepSeek-Coder 1.3B Instruct | blk | 109 | 89 | 20 | 5.90649 | [3.16953, 11.9938] |
| 3.3 | DeepSeek-Coder 33B Instruct | dom | 98 | 85 | 13 | 3.07736 | [1.88485, 4.75315] |
| 3.3 | DeepSeek-Coder 33B Instruct | blk | 98 | 86 | 12 | 3.46877 | [1.97362, 6.8135] |
| 3.3 | Llama-3.2 1B Instruct | dom | 102 | 96 | 6 | 1.57141 | [0.874, 3.01746] |
| 3.3 | Llama-3.2 1B Instruct | blk | 102 | 84 | 18 | 3.57874 | [1.38536, 13.2868] |
| 4 | OLMo 3 7B Instruct | dom | 90 | 57 | 33 | 9.4359 | [3.33032, 31.4667] |
| 4 | OLMo 3 7B Instruct | blk | 102 | 71 | 31 | 12.0889 | [6.5, 17.7143] |
| 4 | OLMo 3 32B Instruct | dom | 85 | 65 | 20 | 3.83871 | [2.2069, 9.55552] |
| 4 | OLMo 3 32B Instruct | blk | 101 | 71 | 30 | 12.7379 | [6.5, 24.8889] |
| 4 | OLMo 3 32B Think | dom | 93 | 66 | 27 | 5.38912 | [2.83076, 11.6491] |
| 4 | OLMo 3 32B Think | blk | 97 | 68 | 29 | 15.3333 | [11.4167, 29.9759] |
| 4 | Qwen3-Coder 30B-A3B Instruct | dom | 99 | 82 | 17 | 3.71429 | [1.33333, 7.57895] |
| 4 | Qwen3-Coder 30B-A3B Instruct | blk | 92 | 65 | 27 | 5.91304 | [3, 14.7692] |
| 4 | Qwen3.5 27B | dom | 72 | 63 | 9 | 1.83314 | [1.34483, 3.16] |
| 4 | Qwen3.5 27B | blk | 83 | 68 | 15 | 1.89474 | [1.39884, 9.26554] |
| 4 | Qwen3.5 122B-A10B | dom | 75 | 55 | 20 | 6.12683 | [2.34144, 12.7786] |
| 4 | Qwen3.5 122B-A10B | blk | 88 | 70 | 18 | 5.97948 | [2.33704, 7.7957] |
| 4 | Qwen3.5 397B-A17B | dom | 78 | 65 | 13 | 4.38846 | [1.42424, 9.33333] |
| 4 | Qwen3.5 397B-A17B | blk | 87 | 65 | 22 | 10.6918 | [5.87888, 14.303] |
| 4 | Gemma 4 31B | dom | 109 | 106 | 3 | 1.67941 | [1.2865, 3.3626] |
| 4 | Gemma 4 31B | blk | 104 | 94 | 10 | 2.69528 | [1.65503, 4.02755] |
| 4 | DeepSeek-V4.1-Flash | dom | 89 | 77 | 12 | 2.43465 | [1.54374, 4.95657] |
| 4 | DeepSeek-V4.1-Flash | blk | 96 | 82 | 14 | 5.93416 | [3.04933, 12.2249] |
