# Development results — `dev-20261023a`

> **Run** `dev-20261023a` · **stage** DEVELOPMENT · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

## Headline numbers (from the CSVs; see stage banner)

**Reversion with the token table present** (`rule_effect.csv`, record_type=reversion)

| family | lexicon | model | rate | ci | n_rows | n_templates |
|---|---|---|---|---|---|---|
| blk | d25s3 | asu-rc/deepseek-v4-1-flash | 0.432 | [0.373, 0.490] | 220 | 74 |
| blk | d50s3 | asu-rc/deepseek-v4-1-flash | 0.423 | [0.374, 0.470] | 272 | 76 |
| blk | d75s1a | asu-rc/deepseek-v4-1-flash | 0.416 | [0.370, 0.464] | 341 | 80 |
| blk | d75s2a | asu-rc/deepseek-v4-1-flash | 0.446 | [0.399, 0.489] | 341 | 80 |
| blk | d75s3a | asu-rc/deepseek-v4-1-flash | 0.434 | [0.384, 0.482] | 341 | 80 |
| dom | d25s3 | asu-rc/deepseek-v4-1-flash | 0.445 | [0.396, 0.494] | 220 | 74 |
| dom | d50s3 | asu-rc/deepseek-v4-1-flash | 0.430 | [0.384, 0.480] | 272 | 76 |
| dom | d75s1a | asu-rc/deepseek-v4-1-flash | 0.416 | [0.373, 0.460] | 341 | 80 |
| dom | d75s2a | asu-rc/deepseek-v4-1-flash | 0.469 | [0.427, 0.513] | 341 | 80 |
| dom | d75s3a | asu-rc/deepseek-v4-1-flash | 0.428 | [0.377, 0.478] | 341 | 80 |
| blk | d25s3 | asu-rc/gemma4-31b-it | 0.491 | [0.431, 0.551] | 220 | 74 |
| blk | d50s3 | asu-rc/gemma4-31b-it | 0.504 | [0.448, 0.557] | 272 | 76 |
| blk | d75s1a | asu-rc/gemma4-31b-it | 0.510 | [0.466, 0.557] | 341 | 80 |
| blk | d75s2a | asu-rc/gemma4-31b-it | 0.519 | [0.476, 0.564] | 341 | 80 |
| blk | d75s3a | asu-rc/gemma4-31b-it | 0.525 | [0.482, 0.569] | 341 | 80 |
| dom | d25s3 | asu-rc/gemma4-31b-it | 0.459 | [0.408, 0.511] | 220 | 74 |
| dom | d50s3 | asu-rc/gemma4-31b-it | 0.445 | [0.392, 0.502] | 272 | 76 |
| dom | d75s1a | asu-rc/gemma4-31b-it | 0.455 | [0.413, 0.500] | 341 | 80 |
| dom | d75s2a | asu-rc/gemma4-31b-it | 0.507 | [0.460, 0.555] | 341 | 80 |
| dom | d75s3a | asu-rc/gemma4-31b-it | 0.457 | [0.413, 0.505] | 341 | 80 |
| blk | d25s3 | asu-rc/olmo3-32b-instruct | 0.423 | [0.363, 0.483] | 220 | 74 |
| blk | d50s3 | asu-rc/olmo3-32b-instruct | 0.404 | [0.347, 0.463] | 272 | 76 |
| blk | d75s1a | asu-rc/olmo3-32b-instruct | 0.381 | [0.334, 0.432] | 341 | 80 |
| blk | d75s2a | asu-rc/olmo3-32b-instruct | 0.416 | [0.360, 0.469] | 341 | 80 |
| blk | d75s3a | asu-rc/olmo3-32b-instruct | 0.428 | [0.374, 0.478] | 341 | 80 |
| dom | d25s3 | asu-rc/olmo3-32b-instruct | 0.391 | [0.338, 0.445] | 220 | 74 |
| dom | d50s3 | asu-rc/olmo3-32b-instruct | 0.415 | [0.360, 0.472] | 272 | 76 |
| dom | d75s1a | asu-rc/olmo3-32b-instruct | 0.419 | [0.370, 0.469] | 341 | 80 |
| dom | d75s2a | asu-rc/olmo3-32b-instruct | 0.443 | [0.395, 0.483] | 341 | 80 |
| dom | d75s3a | asu-rc/olmo3-32b-instruct | 0.384 | [0.339, 0.429] | 341 | 80 |
| blk | d25s3 | asu-rc/olmo3-32b-think | 0.455 | [0.392, 0.517] | 220 | 74 |
| blk | d50s3 | asu-rc/olmo3-32b-think | 0.434 | [0.374, 0.495] | 272 | 76 |
| blk | d75s1a | asu-rc/olmo3-32b-think | 0.443 | [0.385, 0.497] | 341 | 80 |
| blk | d75s2a | asu-rc/olmo3-32b-think | 0.428 | [0.375, 0.476] | 341 | 80 |
| blk | d75s3a | asu-rc/olmo3-32b-think | 0.449 | [0.394, 0.503] | 341 | 80 |
| dom | d25s3 | asu-rc/olmo3-32b-think | 0.423 | [0.366, 0.480] | 220 | 74 |
| dom | d50s3 | asu-rc/olmo3-32b-think | 0.412 | [0.355, 0.470] | 272 | 76 |
| dom | d75s1a | asu-rc/olmo3-32b-think | 0.411 | [0.356, 0.467] | 341 | 80 |
| dom | d75s2a | asu-rc/olmo3-32b-think | 0.472 | [0.420, 0.524] | 341 | 80 |
| dom | d75s3a | asu-rc/olmo3-32b-think | 0.408 | [0.356, 0.460] | 341 | 80 |
| blk | d25s3 | asu-rc/olmo3-7b-instruct | 0.395 | [0.339, 0.452] | 220 | 74 |
| blk | d50s3 | asu-rc/olmo3-7b-instruct | 0.382 | [0.331, 0.434] | 272 | 76 |
| blk | d75s1a | asu-rc/olmo3-7b-instruct | 0.393 | [0.342, 0.444] | 341 | 80 |
| blk | d75s2a | asu-rc/olmo3-7b-instruct | 0.484 | [0.436, 0.525] | 341 | 80 |
| blk | d75s3a | asu-rc/olmo3-7b-instruct | 0.422 | [0.365, 0.476] | 341 | 80 |
| dom | d25s3 | asu-rc/olmo3-7b-instruct | 0.409 | [0.351, 0.471] | 220 | 74 |
| dom | d50s3 | asu-rc/olmo3-7b-instruct | 0.368 | [0.315, 0.420] | 272 | 76 |
| dom | d75s1a | asu-rc/olmo3-7b-instruct | 0.416 | [0.367, 0.465] | 341 | 80 |
| dom | d75s2a | asu-rc/olmo3-7b-instruct | 0.443 | [0.390, 0.493] | 341 | 80 |
| dom | d75s3a | asu-rc/olmo3-7b-instruct | 0.422 | [0.365, 0.475] | 341 | 80 |
| blk | d25s3 | asu-rc/qwen3-coder-30b-a3b-instruct | 0.482 | [0.418, 0.546] | 220 | 74 |
| blk | d50s3 | asu-rc/qwen3-coder-30b-a3b-instruct | 0.463 | [0.409, 0.518] | 272 | 76 |
| blk | d75s1a | asu-rc/qwen3-coder-30b-a3b-instruct | 0.466 | [0.404, 0.525] | 341 | 80 |
| blk | d75s2a | asu-rc/qwen3-coder-30b-a3b-instruct | 0.469 | [0.408, 0.528] | 341 | 80 |
| blk | d75s3a | asu-rc/qwen3-coder-30b-a3b-instruct | 0.443 | [0.387, 0.496] | 341 | 80 |
| dom | d25s3 | asu-rc/qwen3-coder-30b-a3b-instruct | 0.418 | [0.354, 0.481] | 220 | 74 |
| dom | d50s3 | asu-rc/qwen3-coder-30b-a3b-instruct | 0.438 | [0.384, 0.489] | 272 | 76 |
| dom | d75s1a | asu-rc/qwen3-coder-30b-a3b-instruct | 0.469 | [0.419, 0.518] | 341 | 80 |
| dom | d75s2a | asu-rc/qwen3-coder-30b-a3b-instruct | 0.437 | [0.383, 0.490] | 341 | 80 |
| dom | d75s3a | asu-rc/qwen3-coder-30b-a3b-instruct | 0.452 | [0.393, 0.509] | 341 | 80 |
| blk | d25s3 | asu-rc/qwen35-122b-a10b | 0.405 | [0.343, 0.463] | 220 | 74 |
| blk | d50s3 | asu-rc/qwen35-122b-a10b | 0.441 | [0.385, 0.491] | 272 | 76 |
| blk | d75s1a | asu-rc/qwen35-122b-a10b | 0.452 | [0.397, 0.503] | 341 | 80 |
| blk | d75s2a | asu-rc/qwen35-122b-a10b | 0.434 | [0.380, 0.490] | 341 | 80 |
| blk | d75s3a | asu-rc/qwen35-122b-a10b | 0.472 | [0.417, 0.524] | 341 | 80 |
| dom | d25s3 | asu-rc/qwen35-122b-a10b | 0.418 | [0.362, 0.472] | 220 | 74 |
| dom | d50s3 | asu-rc/qwen35-122b-a10b | 0.423 | [0.364, 0.476] | 272 | 76 |
| dom | d75s1a | asu-rc/qwen35-122b-a10b | 0.457 | [0.409, 0.507] | 341 | 80 |
| dom | d75s2a | asu-rc/qwen35-122b-a10b | 0.416 | [0.370, 0.462] | 341 | 80 |
| dom | d75s3a | asu-rc/qwen35-122b-a10b | 0.446 | [0.395, 0.496] | 341 | 80 |
| blk | d25s3 | asu-rc/qwen35-27b | 0.441 | [0.374, 0.513] | 220 | 74 |
| blk | d50s3 | asu-rc/qwen35-27b | 0.415 | [0.354, 0.478] | 272 | 76 |
| blk | d75s1a | asu-rc/qwen35-27b | 0.411 | [0.368, 0.456] | 341 | 80 |
| blk | d75s2a | asu-rc/qwen35-27b | 0.408 | [0.359, 0.454] | 341 | 80 |
| blk | d75s3a | asu-rc/qwen35-27b | 0.431 | [0.378, 0.479] | 341 | 80 |
| dom | d25s3 | asu-rc/qwen35-27b | 0.418 | [0.362, 0.473] | 220 | 74 |
| dom | d50s3 | asu-rc/qwen35-27b | 0.404 | [0.347, 0.459] | 272 | 76 |
| dom | d75s1a | asu-rc/qwen35-27b | 0.399 | [0.351, 0.449] | 341 | 80 |
| dom | d75s2a | asu-rc/qwen35-27b | 0.411 | [0.367, 0.454] | 341 | 80 |
| dom | d75s3a | asu-rc/qwen35-27b | 0.393 | [0.348, 0.436] | 341 | 80 |
| blk | d25s3 | asu-rc/qwen35-397b-a17b | 0.373 | [0.311, 0.433] | 220 | 74 |
| blk | d50s3 | asu-rc/qwen35-397b-a17b | 0.445 | [0.386, 0.506] | 272 | 76 |
| blk | d75s1a | asu-rc/qwen35-397b-a17b | 0.437 | [0.383, 0.493] | 341 | 80 |
| blk | d75s2a | asu-rc/qwen35-397b-a17b | 0.428 | [0.368, 0.485] | 341 | 80 |
| blk | d75s3a | asu-rc/qwen35-397b-a17b | 0.463 | [0.404, 0.526] | 341 | 80 |
| dom | d25s3 | asu-rc/qwen35-397b-a17b | 0.382 | [0.317, 0.447] | 220 | 74 |
| dom | d50s3 | asu-rc/qwen35-397b-a17b | 0.434 | [0.372, 0.493] | 272 | 76 |
| dom | d75s1a | asu-rc/qwen35-397b-a17b | 0.411 | [0.356, 0.468] | 341 | 80 |
| dom | d75s2a | asu-rc/qwen35-397b-a17b | 0.452 | [0.396, 0.509] | 341 | 80 |
| dom | d75s3a | asu-rc/qwen35-397b-a17b | 0.428 | [0.368, 0.487] | 341 | 80 |

**Rule effect** — `M_seq(rule) − M_seq(control)` (`rule_effect.csv`)

| family | lexicon | model | control | mean | ci | ci_excludes_zero | helped |
|---|---|---|---|---|---|---|---|
| blk | d25s3 | asu-rc/deepseek-v4-1-flash | norule | 0.262 | [0.038, 0.508] | True | 0.555 |
| blk | d25s3 | asu-rc/deepseek-v4-1-flash | norule_lenmatched | 0.250 | [-0.011, 0.527] | False | 0.595 |
| blk | d50s3 | asu-rc/deepseek-v4-1-flash | norule | 0.352 | [0.125, 0.593] | True | 0.636 |
| blk | d50s3 | asu-rc/deepseek-v4-1-flash | norule_lenmatched | 0.322 | [0.072, 0.574] | True | 0.621 |
| blk | d75s1a | asu-rc/deepseek-v4-1-flash | norule | 0.351 | [-0.034, 0.752] | False | 0.589 |
| blk | d75s1a | asu-rc/deepseek-v4-1-flash | norule_lenmatched | 0.332 | [-0.006, 0.694] | False | 0.575 |
| blk | d75s2a | asu-rc/deepseek-v4-1-flash | norule | 0.638 | [0.281, 1.016] | True | 0.566 |
| blk | d75s2a | asu-rc/deepseek-v4-1-flash | norule_lenmatched | 0.651 | [0.334, 0.966] | True | 0.569 |
| blk | d75s3a | asu-rc/deepseek-v4-1-flash | norule | 0.657 | [0.332, 0.987] | True | 0.610 |
| blk | d75s3a | asu-rc/deepseek-v4-1-flash | norule_lenmatched | 0.561 | [0.289, 0.841] | True | 0.630 |
| dom | d25s3 | asu-rc/deepseek-v4-1-flash | norule | 0.185 | [-0.049, 0.421] | False | 0.523 |
| dom | d25s3 | asu-rc/deepseek-v4-1-flash | norule_lenmatched | 0.212 | [-0.045, 0.475] | False | 0.586 |
| dom | d50s3 | asu-rc/deepseek-v4-1-flash | norule | 0.274 | [0.046, 0.498] | True | 0.570 |
| dom | d50s3 | asu-rc/deepseek-v4-1-flash | norule_lenmatched | 0.303 | [0.062, 0.539] | True | 0.614 |
| dom | d75s1a | asu-rc/deepseek-v4-1-flash | norule | 0.283 | [0.012, 0.596] | True | 0.587 |
| dom | d75s1a | asu-rc/deepseek-v4-1-flash | norule_lenmatched | 0.302 | [0.043, 0.593] | True | 0.581 |
| dom | d75s2a | asu-rc/deepseek-v4-1-flash | norule | 0.472 | [0.222, 0.724] | True | 0.540 |
| dom | d75s2a | asu-rc/deepseek-v4-1-flash | norule_lenmatched | 0.463 | [0.242, 0.677] | True | 0.554 |
| dom | d75s3a | asu-rc/deepseek-v4-1-flash | norule | 0.465 | [0.231, 0.709] | True | 0.581 |
| dom | d75s3a | asu-rc/deepseek-v4-1-flash | norule_lenmatched | 0.445 | [0.257, 0.652] | True | 0.619 |
| blk | d25s3 | asu-rc/gemma4-31b-it | norule | 0.481 | [-0.227, 1.278] | False | 0.500 |
| blk | d25s3 | asu-rc/gemma4-31b-it | norule_lenmatched | 0.105 | [-0.673, 0.977] | False | 0.518 |
| blk | d50s3 | asu-rc/gemma4-31b-it | norule | 0.822 | [0.050, 1.578] | True | 0.570 |
| blk | d50s3 | asu-rc/gemma4-31b-it | norule_lenmatched | 0.633 | [-0.094, 1.337] | False | 0.540 |
| blk | d75s1a | asu-rc/gemma4-31b-it | norule | 0.574 | [-0.323, 1.567] | False | 0.490 |
| blk | d75s1a | asu-rc/gemma4-31b-it | norule_lenmatched | 0.281 | [-0.532, 1.127] | False | 0.478 |
| blk | d75s2a | asu-rc/gemma4-31b-it | norule | 0.063 | [-0.741, 0.776] | False | 0.519 |
| blk | d75s2a | asu-rc/gemma4-31b-it | norule_lenmatched | 0.086 | [-0.725, 0.817] | False | 0.496 |
| blk | d75s3a | asu-rc/gemma4-31b-it | norule | 0.484 | [-0.159, 1.086] | False | 0.540 |
| blk | d75s3a | asu-rc/gemma4-31b-it | norule_lenmatched | 0.543 | [-0.143, 1.161] | False | 0.551 |
| dom | d25s3 | asu-rc/gemma4-31b-it | norule | 0.731 | [0.052, 1.505] | True | 0.541 |
| dom | d25s3 | asu-rc/gemma4-31b-it | norule_lenmatched | 0.384 | [-0.317, 1.143] | False | 0.545 |
| dom | d50s3 | asu-rc/gemma4-31b-it | norule | 1.135 | [0.426, 1.883] | True | 0.562 |
| dom | d50s3 | asu-rc/gemma4-31b-it | norule_lenmatched | 0.643 | [-0.088, 1.392] | False | 0.518 |
| dom | d75s1a | asu-rc/gemma4-31b-it | norule | 0.243 | [-0.491, 0.985] | False | 0.528 |
| dom | d75s1a | asu-rc/gemma4-31b-it | norule_lenmatched | 0.144 | [-0.551, 0.834] | False | 0.510 |
| dom | d75s2a | asu-rc/gemma4-31b-it | norule | 0.429 | [-0.414, 1.233] | False | 0.531 |
| dom | d75s2a | asu-rc/gemma4-31b-it | norule_lenmatched | 0.015 | [-0.815, 0.800] | False | 0.516 |
| dom | d75s3a | asu-rc/gemma4-31b-it | norule | 0.788 | [0.218, 1.336] | True | 0.537 |
| dom | d75s3a | asu-rc/gemma4-31b-it | norule_lenmatched | 0.934 | [0.431, 1.445] | True | 0.598 |
| blk | d25s3 | asu-rc/olmo3-32b-instruct | norule | 0.567 | [0.093, 1.039] | True | 0.600 |
| blk | d25s3 | asu-rc/olmo3-32b-instruct | norule_lenmatched | 0.693 | [0.229, 1.148] | True | 0.636 |
| blk | d50s3 | asu-rc/olmo3-32b-instruct | norule | 0.957 | [0.513, 1.412] | True | 0.665 |
| blk | d50s3 | asu-rc/olmo3-32b-instruct | norule_lenmatched | 1.078 | [0.659, 1.523] | True | 0.669 |
| blk | d75s1a | asu-rc/olmo3-32b-instruct | norule | 0.665 | [0.219, 1.148] | True | 0.651 |
| blk | d75s1a | asu-rc/olmo3-32b-instruct | norule_lenmatched | 0.672 | [0.201, 1.162] | True | 0.628 |
| blk | d75s2a | asu-rc/olmo3-32b-instruct | norule | 1.091 | [0.554, 1.683] | True | 0.584 |
| blk | d75s2a | asu-rc/olmo3-32b-instruct | norule_lenmatched | 1.093 | [0.561, 1.664] | True | 0.584 |
| blk | d75s3a | asu-rc/olmo3-32b-instruct | norule | 1.000 | [0.624, 1.375] | True | 0.625 |
| blk | d75s3a | asu-rc/olmo3-32b-instruct | norule_lenmatched | 1.045 | [0.658, 1.455] | True | 0.633 |
| dom | d25s3 | asu-rc/olmo3-32b-instruct | norule | 0.619 | [0.188, 1.091] | True | 0.605 |
| dom | d25s3 | asu-rc/olmo3-32b-instruct | norule_lenmatched | 0.700 | [0.255, 1.179] | True | 0.627 |
| dom | d50s3 | asu-rc/olmo3-32b-instruct | norule | 0.719 | [0.257, 1.193] | True | 0.607 |
| dom | d50s3 | asu-rc/olmo3-32b-instruct | norule_lenmatched | 0.847 | [0.398, 1.317] | True | 0.607 |
| dom | d75s1a | asu-rc/olmo3-32b-instruct | norule | 0.741 | [0.268, 1.229] | True | 0.572 |
| dom | d75s1a | asu-rc/olmo3-32b-instruct | norule_lenmatched | 0.762 | [0.306, 1.238] | True | 0.592 |
| dom | d75s2a | asu-rc/olmo3-32b-instruct | norule | 0.999 | [0.517, 1.543] | True | 0.598 |
| dom | d75s2a | asu-rc/olmo3-32b-instruct | norule_lenmatched | 1.028 | [0.547, 1.570] | True | 0.598 |
| dom | d75s3a | asu-rc/olmo3-32b-instruct | norule | 0.911 | [0.586, 1.250] | True | 0.595 |
| dom | d75s3a | asu-rc/olmo3-32b-instruct | norule_lenmatched | 0.996 | [0.651, 1.363] | True | 0.622 |
| blk | d25s3 | asu-rc/olmo3-32b-think | norule | 0.246 | [-0.139, 0.641] | False | 0.568 |
| blk | d25s3 | asu-rc/olmo3-32b-think | norule_lenmatched | 0.344 | [-0.035, 0.727] | False | 0.586 |
| blk | d50s3 | asu-rc/olmo3-32b-think | norule | 0.683 | [0.317, 1.057] | True | 0.614 |
| blk | d50s3 | asu-rc/olmo3-32b-think | norule_lenmatched | 0.742 | [0.392, 1.111] | True | 0.621 |
| blk | d75s1a | asu-rc/olmo3-32b-think | norule | 0.558 | [0.189, 0.965] | True | 0.619 |
| blk | d75s1a | asu-rc/olmo3-32b-think | norule_lenmatched | 0.583 | [0.197, 0.998] | True | 0.607 |
| blk | d75s2a | asu-rc/olmo3-32b-think | norule | 0.815 | [0.384, 1.296] | True | 0.563 |
| blk | d75s2a | asu-rc/olmo3-32b-think | norule_lenmatched | 0.778 | [0.353, 1.239] | True | 0.569 |
| blk | d75s3a | asu-rc/olmo3-32b-think | norule | 0.755 | [0.442, 1.067] | True | 0.581 |
| blk | d75s3a | asu-rc/olmo3-32b-think | norule_lenmatched | 0.799 | [0.460, 1.137] | True | 0.572 |
| dom | d25s3 | asu-rc/olmo3-32b-think | norule | 0.152 | [-0.151, 0.512] | False | 0.505 |
| dom | d25s3 | asu-rc/olmo3-32b-think | norule_lenmatched | 0.184 | [-0.139, 0.567] | False | 0.514 |
| dom | d50s3 | asu-rc/olmo3-32b-think | norule | 0.444 | [0.103, 0.793] | True | 0.533 |
| dom | d50s3 | asu-rc/olmo3-32b-think | norule_lenmatched | 0.490 | [0.145, 0.848] | True | 0.529 |
| dom | d75s1a | asu-rc/olmo3-32b-think | norule | 0.538 | [0.187, 0.889] | True | 0.557 |
| dom | d75s1a | asu-rc/olmo3-32b-think | norule_lenmatched | 0.587 | [0.254, 0.950] | True | 0.575 |
| dom | d75s2a | asu-rc/olmo3-32b-think | norule | 0.688 | [0.336, 1.074] | True | 0.540 |
| dom | d75s2a | asu-rc/olmo3-32b-think | norule_lenmatched | 0.667 | [0.321, 1.054] | True | 0.537 |
| dom | d75s3a | asu-rc/olmo3-32b-think | norule | 0.619 | [0.364, 0.880] | True | 0.543 |
| dom | d75s3a | asu-rc/olmo3-32b-think | norule_lenmatched | 0.671 | [0.404, 0.950] | True | 0.554 |
| blk | d25s3 | asu-rc/olmo3-7b-instruct | norule | 0.880 | [0.552, 1.229] | True | 0.609 |
| blk | d25s3 | asu-rc/olmo3-7b-instruct | norule_lenmatched | 0.789 | [0.493, 1.125] | True | 0.623 |
| blk | d50s3 | asu-rc/olmo3-7b-instruct | norule | 0.940 | [0.618, 1.265] | True | 0.618 |
| blk | d50s3 | asu-rc/olmo3-7b-instruct | norule_lenmatched | 0.802 | [0.510, 1.086] | True | 0.621 |
| blk | d75s1a | asu-rc/olmo3-7b-instruct | norule | 0.620 | [0.084, 1.144] | True | 0.595 |
| blk | d75s1a | asu-rc/olmo3-7b-instruct | norule_lenmatched | 0.495 | [-0.029, 1.009] | False | 0.595 |
| blk | d75s2a | asu-rc/olmo3-7b-instruct | norule | 0.545 | [0.160, 0.932] | True | 0.528 |
| blk | d75s2a | asu-rc/olmo3-7b-instruct | norule_lenmatched | 0.479 | [0.088, 0.888] | True | 0.528 |
| blk | d75s3a | asu-rc/olmo3-7b-instruct | norule | 0.878 | [0.444, 1.307] | True | 0.616 |
| blk | d75s3a | asu-rc/olmo3-7b-instruct | norule_lenmatched | 0.765 | [0.316, 1.210] | True | 0.613 |
| dom | d25s3 | asu-rc/olmo3-7b-instruct | norule | 1.099 | [0.787, 1.471] | True | 0.623 |
| dom | d25s3 | asu-rc/olmo3-7b-instruct | norule_lenmatched | 1.122 | [0.776, 1.489] | True | 0.632 |
| dom | d50s3 | asu-rc/olmo3-7b-instruct | norule | 1.058 | [0.770, 1.360] | True | 0.610 |
| dom | d50s3 | asu-rc/olmo3-7b-instruct | norule_lenmatched | 1.006 | [0.720, 1.318] | True | 0.610 |
| dom | d75s1a | asu-rc/olmo3-7b-instruct | norule | 0.728 | [0.374, 1.076] | True | 0.587 |
| dom | d75s1a | asu-rc/olmo3-7b-instruct | norule_lenmatched | 0.674 | [0.299, 1.030] | True | 0.578 |
| dom | d75s2a | asu-rc/olmo3-7b-instruct | norule | 0.383 | [0.009, 0.787] | True | 0.545 |
| dom | d75s2a | asu-rc/olmo3-7b-instruct | norule_lenmatched | 0.335 | [-0.049, 0.747] | False | 0.543 |
| dom | d75s3a | asu-rc/olmo3-7b-instruct | norule | 0.956 | [0.697, 1.236] | True | 0.578 |
| dom | d75s3a | asu-rc/olmo3-7b-instruct | norule_lenmatched | 0.872 | [0.599, 1.176] | True | 0.578 |
| blk | d25s3 | asu-rc/qwen3-coder-30b-a3b-instruct | norule | 0.666 | [0.344, 1.010] | True | 0.668 |
| blk | d25s3 | asu-rc/qwen3-coder-30b-a3b-instruct | norule_lenmatched | 0.621 | [0.286, 0.995] | True | 0.668 |
| blk | d50s3 | asu-rc/qwen3-coder-30b-a3b-instruct | norule | 0.664 | [0.328, 1.016] | True | 0.566 |
| blk | d50s3 | asu-rc/qwen3-coder-30b-a3b-instruct | norule_lenmatched | 0.672 | [0.336, 1.035] | True | 0.585 |
| blk | d75s1a | asu-rc/qwen3-coder-30b-a3b-instruct | norule | 0.574 | [0.010, 1.132] | True | 0.531 |
| blk | d75s1a | asu-rc/qwen3-coder-30b-a3b-instruct | norule_lenmatched | 0.598 | [0.017, 1.175] | True | 0.531 |
| blk | d75s2a | asu-rc/qwen3-coder-30b-a3b-instruct | norule | 0.794 | [0.255, 1.357] | True | 0.525 |
| blk | d75s2a | asu-rc/qwen3-coder-30b-a3b-instruct | norule_lenmatched | 0.829 | [0.253, 1.428] | True | 0.543 |
| blk | d75s3a | asu-rc/qwen3-coder-30b-a3b-instruct | norule | 1.013 | [0.699, 1.352] | True | 0.545 |
| blk | d75s3a | asu-rc/qwen3-coder-30b-a3b-instruct | norule_lenmatched | 1.116 | [0.798, 1.454] | True | 0.569 |
| dom | d25s3 | asu-rc/qwen3-coder-30b-a3b-instruct | norule | 0.289 | [-0.066, 0.696] | False | 0.564 |
| dom | d25s3 | asu-rc/qwen3-coder-30b-a3b-instruct | norule_lenmatched | 0.284 | [-0.082, 0.670] | False | 0.577 |
| dom | d50s3 | asu-rc/qwen3-coder-30b-a3b-instruct | norule | 0.387 | [0.041, 0.774] | True | 0.548 |
| dom | d50s3 | asu-rc/qwen3-coder-30b-a3b-instruct | norule_lenmatched | 0.371 | [0.021, 0.751] | True | 0.577 |
| dom | d75s1a | asu-rc/qwen3-coder-30b-a3b-instruct | norule | 0.419 | [-0.079, 0.914] | False | 0.504 |
| dom | d75s1a | asu-rc/qwen3-coder-30b-a3b-instruct | norule_lenmatched | 0.398 | [-0.112, 0.910] | False | 0.522 |
| dom | d75s2a | asu-rc/qwen3-coder-30b-a3b-instruct | norule | 0.756 | [0.236, 1.274] | True | 0.543 |
| dom | d75s2a | asu-rc/qwen3-coder-30b-a3b-instruct | norule_lenmatched | 0.754 | [0.200, 1.301] | True | 0.534 |
| dom | d75s3a | asu-rc/qwen3-coder-30b-a3b-instruct | norule | 0.876 | [0.595, 1.194] | True | 0.548 |
| dom | d75s3a | asu-rc/qwen3-coder-30b-a3b-instruct | norule_lenmatched | 0.883 | [0.592, 1.209] | True | 0.557 |
| blk | d25s3 | asu-rc/qwen35-122b-a10b | norule | 0.488 | [0.214, 0.798] | True | 0.600 |
| blk | d25s3 | asu-rc/qwen35-122b-a10b | norule_lenmatched | 0.486 | [0.200, 0.814] | True | 0.609 |
| blk | d50s3 | asu-rc/qwen35-122b-a10b | norule | 0.529 | [0.245, 0.831] | True | 0.603 |
| blk | d50s3 | asu-rc/qwen35-122b-a10b | norule_lenmatched | 0.532 | [0.244, 0.837] | True | 0.614 |
| blk | d75s1a | asu-rc/qwen35-122b-a10b | norule | 0.248 | [-0.120, 0.615] | False | 0.584 |
| blk | d75s1a | asu-rc/qwen35-122b-a10b | norule_lenmatched | 0.227 | [-0.120, 0.589] | False | 0.592 |
| blk | d75s2a | asu-rc/qwen35-122b-a10b | norule | 0.814 | [0.467, 1.153] | True | 0.581 |
| blk | d75s2a | asu-rc/qwen35-122b-a10b | norule_lenmatched | 0.853 | [0.530, 1.160] | True | 0.598 |
| blk | d75s3a | asu-rc/qwen35-122b-a10b | norule | 0.653 | [0.372, 0.956] | True | 0.589 |
| blk | d75s3a | asu-rc/qwen35-122b-a10b | norule_lenmatched | 0.620 | [0.355, 0.906] | True | 0.604 |
| dom | d25s3 | asu-rc/qwen35-122b-a10b | norule | 0.258 | [0.030, 0.487] | True | 0.573 |
| dom | d25s3 | asu-rc/qwen35-122b-a10b | norule_lenmatched | 0.257 | [0.018, 0.502] | True | 0.577 |
| dom | d50s3 | asu-rc/qwen35-122b-a10b | norule | 0.449 | [0.210, 0.703] | True | 0.607 |
| dom | d50s3 | asu-rc/qwen35-122b-a10b | norule_lenmatched | 0.406 | [0.153, 0.671] | True | 0.614 |
| dom | d75s1a | asu-rc/qwen35-122b-a10b | norule | 0.306 | [0.000, 0.642] | True | 0.589 |
| dom | d75s1a | asu-rc/qwen35-122b-a10b | norule_lenmatched | 0.284 | [-0.027, 0.615] | False | 0.566 |
| dom | d75s2a | asu-rc/qwen35-122b-a10b | norule | 0.768 | [0.469, 1.046] | True | 0.581 |
| dom | d75s2a | asu-rc/qwen35-122b-a10b | norule_lenmatched | 0.721 | [0.420, 1.010] | True | 0.563 |
| dom | d75s3a | asu-rc/qwen35-122b-a10b | norule | 0.701 | [0.447, 0.974] | True | 0.575 |
| dom | d75s3a | asu-rc/qwen35-122b-a10b | norule_lenmatched | 0.650 | [0.390, 0.917] | True | 0.595 |
| blk | d25s3 | asu-rc/qwen35-27b | norule | 0.211 | [-0.081, 0.521] | False | 0.568 |
| blk | d25s3 | asu-rc/qwen35-27b | norule_lenmatched | 0.214 | [-0.093, 0.533] | False | 0.559 |
| blk | d50s3 | asu-rc/qwen35-27b | norule | 0.318 | [0.069, 0.582] | True | 0.585 |
| blk | d50s3 | asu-rc/qwen35-27b | norule_lenmatched | 0.303 | [0.039, 0.590] | True | 0.566 |
| blk | d75s1a | asu-rc/qwen35-27b | norule | 0.254 | [-0.103, 0.609] | False | 0.563 |
| blk | d75s1a | asu-rc/qwen35-27b | norule_lenmatched | 0.266 | [-0.083, 0.617] | False | 0.545 |
| blk | d75s2a | asu-rc/qwen35-27b | norule | 0.655 | [0.237, 1.073] | True | 0.540 |
| blk | d75s2a | asu-rc/qwen35-27b | norule_lenmatched | 0.683 | [0.273, 1.098] | True | 0.534 |
| blk | d75s3a | asu-rc/qwen35-27b | norule | 0.729 | [0.505, 0.961] | True | 0.587 |
| blk | d75s3a | asu-rc/qwen35-27b | norule_lenmatched | 0.701 | [0.469, 0.942] | True | 0.595 |
| dom | d25s3 | asu-rc/qwen35-27b | norule | 0.209 | [-0.068, 0.505] | False | 0.532 |
| dom | d25s3 | asu-rc/qwen35-27b | norule_lenmatched | 0.230 | [-0.045, 0.522] | False | 0.527 |
| dom | d50s3 | asu-rc/qwen35-27b | norule | 0.377 | [0.111, 0.649] | True | 0.577 |
| dom | d50s3 | asu-rc/qwen35-27b | norule_lenmatched | 0.377 | [0.099, 0.666] | True | 0.599 |
| dom | d75s1a | asu-rc/qwen35-27b | norule | 0.353 | [-0.005, 0.712] | False | 0.578 |
| dom | d75s1a | asu-rc/qwen35-27b | norule_lenmatched | 0.372 | [0.014, 0.731] | True | 0.566 |
| dom | d75s2a | asu-rc/qwen35-27b | norule | 0.718 | [0.322, 1.128] | True | 0.545 |
| dom | d75s2a | asu-rc/qwen35-27b | norule_lenmatched | 0.719 | [0.333, 1.110] | True | 0.554 |
| dom | d75s3a | asu-rc/qwen35-27b | norule | 0.769 | [0.575, 0.964] | True | 0.607 |
| dom | d75s3a | asu-rc/qwen35-27b | norule_lenmatched | 0.737 | [0.539, 0.942] | True | 0.607 |
| blk | d25s3 | asu-rc/qwen35-397b-a17b | norule | 0.637 | [0.321, 0.986] | True | 0.627 |
| blk | d25s3 | asu-rc/qwen35-397b-a17b | norule_lenmatched | 0.653 | [0.332, 1.005] | True | 0.650 |
| blk | d50s3 | asu-rc/qwen35-397b-a17b | norule | 0.449 | [0.186, 0.750] | True | 0.574 |
| blk | d50s3 | asu-rc/qwen35-397b-a17b | norule_lenmatched | 0.476 | [0.196, 0.791] | True | 0.592 |
| blk | d75s1a | asu-rc/qwen35-397b-a17b | norule | 0.358 | [0.019, 0.720] | True | 0.543 |
| blk | d75s1a | asu-rc/qwen35-397b-a17b | norule_lenmatched | 0.365 | [0.029, 0.713] | True | 0.566 |
| blk | d75s2a | asu-rc/qwen35-397b-a17b | norule | 0.639 | [0.297, 0.984] | True | 0.578 |
| blk | d75s2a | asu-rc/qwen35-397b-a17b | norule_lenmatched | 0.645 | [0.316, 0.986] | True | 0.595 |
| blk | d75s3a | asu-rc/qwen35-397b-a17b | norule | 0.603 | [0.334, 0.868] | True | 0.551 |
| blk | d75s3a | asu-rc/qwen35-397b-a17b | norule_lenmatched | 0.628 | [0.358, 0.894] | True | 0.548 |
| dom | d25s3 | asu-rc/qwen35-397b-a17b | norule | 0.413 | [0.142, 0.728] | True | 0.605 |
| dom | d25s3 | asu-rc/qwen35-397b-a17b | norule_lenmatched | 0.415 | [0.129, 0.732] | True | 0.573 |
| dom | d50s3 | asu-rc/qwen35-397b-a17b | norule | 0.336 | [0.088, 0.607] | True | 0.489 |
| dom | d50s3 | asu-rc/qwen35-397b-a17b | norule_lenmatched | 0.362 | [0.101, 0.654] | True | 0.515 |
| dom | d75s1a | asu-rc/qwen35-397b-a17b | norule | 0.248 | [-0.053, 0.575] | False | 0.504 |
| dom | d75s1a | asu-rc/qwen35-397b-a17b | norule_lenmatched | 0.269 | [-0.022, 0.583] | False | 0.519 |
| dom | d75s2a | asu-rc/qwen35-397b-a17b | norule | 0.504 | [0.165, 0.833] | True | 0.537 |
| dom | d75s2a | asu-rc/qwen35-397b-a17b | norule_lenmatched | 0.523 | [0.200, 0.846] | True | 0.534 |
| dom | d75s3a | asu-rc/qwen35-397b-a17b | norule | 0.611 | [0.391, 0.839] | True | 0.545 |
| dom | d75s3a | asu-rc/qwen35-397b-a17b | norule_lenmatched | 0.636 | [0.404, 0.870] | True | 0.554 |

**Extinction** — Kaplan–Meier median shots (`kstar_survival.csv`)

| family | model | population | median | ci | n | cens |
|---|---|---|---|---|---|---|
| blk | asu-rc/deepseek-v4-1-flash | ALL_SITES | 0 | [0.000, 0.929] | 205 | 0.068 |
| blk | asu-rc/deepseek-v4-1-flash | INITIALLY_WRONG | 5.93416 | [3.049, 12.225] | 96 | 0.146 |
| dom | asu-rc/deepseek-v4-1-flash | ALL_SITES | 0 | [0.000, 0.470] | 195 | 0.062 |
| dom | asu-rc/deepseek-v4-1-flash | INITIALLY_WRONG | 2.43465 | [1.544, 4.957] | 89 | 0.135 |
| blk | asu-rc/gemma4-31b-it | ALL_SITES | 0.13242 | [0.000, 0.606] | 205 | 0.049 |
| blk | asu-rc/gemma4-31b-it | INITIALLY_WRONG | 2.69528 | [1.655, 4.028] | 104 | 0.096 |
| dom | asu-rc/gemma4-31b-it | ALL_SITES | 0.216783 | [0.000, 0.856] | 195 | 0.015 |
| dom | asu-rc/gemma4-31b-it | INITIALLY_WRONG | 1.67941 | [1.286, 3.363] | 109 | 0.028 |
| blk | asu-rc/olmo3-32b-instruct | ALL_SITES | 0 | [0.000, 1.143] | 205 | 0.146 |
| blk | asu-rc/olmo3-32b-instruct | INITIALLY_WRONG | 12.7379 | [6.500, 24.889] | 101 | 0.297 |
| dom | asu-rc/olmo3-32b-instruct | ALL_SITES | 0 | [0.000, 0.574] | 195 | 0.103 |
| dom | asu-rc/olmo3-32b-instruct | INITIALLY_WRONG | 3.83871 | [2.207, 9.556] | 85 | 0.235 |
| blk | asu-rc/olmo3-32b-think | ALL_SITES | 0 | [0.000, 1.707] | 205 | 0.141 |
| blk | asu-rc/olmo3-32b-think | INITIALLY_WRONG | 15.3333 | [11.417, 29.976] | 97 | 0.299 |
| dom | asu-rc/olmo3-32b-think | ALL_SITES | 0 | [0.000, 1.304] | 195 | 0.138 |
| dom | asu-rc/olmo3-32b-think | INITIALLY_WRONG | 5.38912 | [2.831, 11.649] | 93 | 0.290 |
| blk | asu-rc/olmo3-7b-instruct | ALL_SITES | 0 | [0.000, 0.903] | 205 | 0.151 |
| blk | asu-rc/olmo3-7b-instruct | INITIALLY_WRONG | 12.0889 | [6.500, 17.714] | 102 | 0.304 |
| dom | asu-rc/olmo3-7b-instruct | ALL_SITES | 0 | [0.000, 0.906] | 195 | 0.169 |
| dom | asu-rc/olmo3-7b-instruct | INITIALLY_WRONG | 9.4359 | [3.330, 31.467] | 90 | 0.367 |
| blk | asu-rc/qwen3-coder-30b-a3b-instruct | ALL_SITES | 0 | [0.000, 0.333] | 205 | 0.132 |
| blk | asu-rc/qwen3-coder-30b-a3b-instruct | INITIALLY_WRONG | 5.91304 | [3.000, 14.769] | 92 | 0.293 |
| dom | asu-rc/qwen3-coder-30b-a3b-instruct | ALL_SITES | 0.0869565 | [0.000, 0.500] | 195 | 0.087 |
| dom | asu-rc/qwen3-coder-30b-a3b-instruct | INITIALLY_WRONG | 3.71429 | [1.333, 7.579] | 99 | 0.172 |
| blk | asu-rc/qwen35-122b-a10b | ALL_SITES | 0 | [0.000, 0.176] | 205 | 0.088 |
| blk | asu-rc/qwen35-122b-a10b | INITIALLY_WRONG | 5.97948 | [2.337, 7.796] | 88 | 0.205 |
| dom | asu-rc/qwen35-122b-a10b | ALL_SITES | 0 | [0.000, 0.000] | 195 | 0.103 |
| dom | asu-rc/qwen35-122b-a10b | INITIALLY_WRONG | 6.12683 | [2.341, 12.779] | 75 | 0.267 |
| blk | asu-rc/qwen35-27b | ALL_SITES | 0 | [0.000, 0.056] | 205 | 0.073 |
| blk | asu-rc/qwen35-27b | INITIALLY_WRONG | 1.89474 | [1.399, 9.266] | 83 | 0.181 |
| dom | asu-rc/qwen35-27b | ALL_SITES | 0 | [0.000, 0.000] | 195 | 0.046 |
| dom | asu-rc/qwen35-27b | INITIALLY_WRONG | 1.83314 | [1.345, 3.160] | 72 | 0.125 |
| blk | asu-rc/qwen35-397b-a17b | ALL_SITES | 0 | [0.000, 0.321] | 205 | 0.107 |
| blk | asu-rc/qwen35-397b-a17b | INITIALLY_WRONG | 10.6918 | [5.879, 14.303] | 87 | 0.253 |
| dom | asu-rc/qwen35-397b-a17b | ALL_SITES | 0 | [0.000, 0.333] | 195 | 0.067 |
| dom | asu-rc/qwen35-397b-a17b | INITIALLY_WRONG | 4.38846 | [1.424, 9.333] | 78 | 0.167 |

## H4 on development data (calibration fitted here — becomes the frozen calibration)

_NOT RUN_
