# Run summary — `heldout-20261007a`

> **Run** `heldout-20261007a` · **stage** HELD-OUT · **status** COMPLETE
>
> Held-out evaluation under DEV_FREEZE; see criteria below. blk results are a WEAKER family test (deviation D1), never a held-out-grammar confirmation.

## Completeness (`run_completeness.csv`)

| experiment | status | n_expected_cells | done | missing | failed | corrupt | duplicates_dropped |
|---|---|---|---|---|---|---|---|
| arm_a | COMPLETE | 3402 | 3402 | 0 | 0 | 0 | 0 |
| primary | COMPLETE | 840 | 840 | 0 | 0 | 0 | 0 |
| armb | COMPLETE | 200 | 200 | 0 | 0 | 0 | 0 |
| h5 | COMPLETE | 3780 | 3780 | 0 | 0 | 0 | 0 |

## Headline numbers (from the CSVs; see stage banner)

**Reversion with the token table present** (`rule_effect.csv`, record_type=reversion)

| family | lexicon | model | rate | ci | n_rows | n_templates |
|---|---|---|---|---|---|---|
| blk | d25s3 | Qwen/Qwen2.5-72B | 0.459 | [0.400, 0.521] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-72B | 0.471 | [0.413, 0.524] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-72B | 0.478 | [0.436, 0.525] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-72B | 0.504 | [0.457, 0.553] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-72B | 0.519 | [0.465, 0.574] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-72B | 0.500 | [0.441, 0.556] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-72B | 0.460 | [0.404, 0.510] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-72B | 0.496 | [0.441, 0.552] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-72B | 0.548 | [0.497, 0.599] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-72B | 0.513 | [0.451, 0.575] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-72B-Instruct | 0.391 | [0.341, 0.444] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-72B-Instruct | 0.441 | [0.383, 0.498] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-72B-Instruct | 0.434 | [0.383, 0.485] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-72B-Instruct | 0.472 | [0.418, 0.524] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-72B-Instruct | 0.481 | [0.422, 0.540] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-72B-Instruct | 0.409 | [0.342, 0.475] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-72B-Instruct | 0.445 | [0.379, 0.511] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-72B-Instruct | 0.463 | [0.406, 0.521] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-72B-Instruct | 0.551 | [0.498, 0.603] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-72B-Instruct | 0.487 | [0.423, 0.547] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B | 0.436 | [0.385, 0.490] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B | 0.397 | [0.346, 0.451] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B | 0.431 | [0.381, 0.485] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B | 0.499 | [0.457, 0.540] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B | 0.416 | [0.367, 0.467] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B | 0.445 | [0.395, 0.498] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B | 0.423 | [0.374, 0.473] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B | 0.466 | [0.414, 0.520] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B | 0.510 | [0.466, 0.554] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B | 0.422 | [0.374, 0.475] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.405 | [0.347, 0.464] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.426 | [0.378, 0.474] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.469 | [0.420, 0.518] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.449 | [0.408, 0.489] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.440 | [0.387, 0.488] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.368 | [0.319, 0.417] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.426 | [0.376, 0.473] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.487 | [0.444, 0.530] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.478 | [0.441, 0.517] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | 0.434 | [0.390, 0.482] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B | 0.495 | [0.431, 0.558] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B | 0.493 | [0.424, 0.561] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B | 0.537 | [0.479, 0.599] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B | 0.522 | [0.476, 0.570] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B | 0.490 | [0.434, 0.549] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B | 0.477 | [0.416, 0.536] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B | 0.500 | [0.437, 0.563] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B | 0.531 | [0.481, 0.584] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B | 0.519 | [0.470, 0.571] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B | 0.455 | [0.400, 0.511] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.532 | [0.472, 0.593] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.518 | [0.454, 0.580] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.534 | [0.471, 0.593] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.516 | [0.460, 0.568] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.510 | [0.448, 0.570] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.436 | [0.384, 0.488] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.456 | [0.395, 0.514] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.516 | [0.464, 0.573] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.457 | [0.404, 0.509] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | 0.434 | [0.380, 0.489] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B | 0.536 | [0.477, 0.599] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B | 0.474 | [0.420, 0.532] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B | 0.475 | [0.424, 0.528] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B | 0.513 | [0.461, 0.567] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B | 0.472 | [0.419, 0.523] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B | 0.523 | [0.462, 0.583] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B | 0.460 | [0.407, 0.514] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B | 0.434 | [0.389, 0.482] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B | 0.481 | [0.429, 0.534] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B | 0.449 | [0.400, 0.497] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | 0.468 | [0.410, 0.527] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | 0.423 | [0.364, 0.483] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | 0.416 | [0.355, 0.478] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | 0.484 | [0.426, 0.542] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | 0.399 | [0.339, 0.460] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | 0.464 | [0.411, 0.519] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | 0.474 | [0.429, 0.525] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | 0.446 | [0.398, 0.495] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | 0.484 | [0.439, 0.532] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | 0.431 | [0.383, 0.480] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B | 0.536 | [0.464, 0.609] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B | 0.489 | [0.421, 0.555] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B | 0.519 | [0.466, 0.571] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B | 0.534 | [0.482, 0.586] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B | 0.496 | [0.434, 0.557] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B | 0.514 | [0.463, 0.564] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B | 0.471 | [0.418, 0.525] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B | 0.411 | [0.364, 0.458] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B | 0.496 | [0.453, 0.539] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B | 0.440 | [0.389, 0.491] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | 0.491 | [0.419, 0.560] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | 0.467 | [0.408, 0.522] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | 0.457 | [0.403, 0.507] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | 0.446 | [0.394, 0.494] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | 0.425 | [0.368, 0.480] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | 0.414 | [0.352, 0.474] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | 0.412 | [0.355, 0.468] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | 0.405 | [0.353, 0.456] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | 0.396 | [0.351, 0.441] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | 0.381 | [0.329, 0.434] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B | 0.514 | [0.452, 0.577] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B | 0.500 | [0.435, 0.563] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B | 0.525 | [0.470, 0.582] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B | 0.507 | [0.454, 0.561] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B | 0.496 | [0.429, 0.558] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B | 0.559 | [0.496, 0.621] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B | 0.478 | [0.424, 0.529] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B | 0.472 | [0.422, 0.523] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B | 0.496 | [0.446, 0.539] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B | 0.425 | [0.375, 0.474] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | 0.505 | [0.441, 0.566] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | 0.489 | [0.425, 0.545] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | 0.490 | [0.436, 0.542] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | 0.475 | [0.422, 0.530] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | 0.496 | [0.430, 0.557] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | 0.500 | [0.432, 0.567] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | 0.467 | [0.405, 0.528] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | 0.481 | [0.428, 0.533] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | 0.469 | [0.425, 0.511] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | 0.463 | [0.409, 0.513] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B | 0.555 | [0.498, 0.613] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B | 0.577 | [0.518, 0.632] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B | 0.566 | [0.511, 0.620] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B | 0.522 | [0.476, 0.568] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B | 0.519 | [0.460, 0.571] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B | 0.509 | [0.456, 0.566] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B | 0.507 | [0.447, 0.564] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B | 0.531 | [0.481, 0.580] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B | 0.490 | [0.439, 0.536] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B | 0.501 | [0.449, 0.553] | 341 | 80 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | 0.477 | [0.420, 0.541] | 220 | 74 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | 0.489 | [0.424, 0.553] | 272 | 76 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | 0.516 | [0.463, 0.570] | 341 | 80 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | 0.455 | [0.399, 0.511] | 341 | 80 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | 0.469 | [0.410, 0.524] | 341 | 80 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | 0.505 | [0.446, 0.563] | 220 | 74 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | 0.522 | [0.462, 0.584] | 272 | 76 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | 0.525 | [0.472, 0.575] | 341 | 80 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | 0.528 | [0.478, 0.575] | 341 | 80 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | 0.513 | [0.452, 0.571] | 341 | 80 |
| blk | d25s3 | bigcode/starcoder2-3b | 0.614 | [0.552, 0.676] | 220 | 74 |
| blk | d50s3 | bigcode/starcoder2-3b | 0.566 | [0.518, 0.618] | 272 | 76 |
| blk | d75s1a | bigcode/starcoder2-3b | 0.545 | [0.500, 0.595] | 341 | 80 |
| blk | d75s2a | bigcode/starcoder2-3b | 0.572 | [0.522, 0.618] | 341 | 80 |
| blk | d75s3a | bigcode/starcoder2-3b | 0.516 | [0.462, 0.573] | 341 | 80 |
| dom | d25s3 | bigcode/starcoder2-3b | 0.495 | [0.433, 0.559] | 220 | 74 |
| dom | d50s3 | bigcode/starcoder2-3b | 0.504 | [0.443, 0.563] | 272 | 76 |
| dom | d75s1a | bigcode/starcoder2-3b | 0.475 | [0.423, 0.529] | 341 | 80 |
| dom | d75s2a | bigcode/starcoder2-3b | 0.463 | [0.414, 0.510] | 341 | 80 |
| dom | d75s3a | bigcode/starcoder2-3b | 0.469 | [0.414, 0.527] | 341 | 80 |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-base | 0.586 | [0.528, 0.650] | 220 | 74 |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-base | 0.559 | [0.515, 0.606] | 272 | 76 |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-base | 0.551 | [0.507, 0.598] | 341 | 80 |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-base | 0.516 | [0.468, 0.571] | 341 | 80 |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-base | 0.513 | [0.471, 0.558] | 341 | 80 |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-base | 0.595 | [0.530, 0.664] | 220 | 74 |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-base | 0.581 | [0.538, 0.628] | 272 | 76 |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-base | 0.587 | [0.545, 0.631] | 341 | 80 |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-base | 0.522 | [0.476, 0.571] | 341 | 80 |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-base | 0.519 | [0.468, 0.570] | 341 | 80 |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | 0.564 | [0.506, 0.625] | 220 | 74 |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | 0.555 | [0.502, 0.607] | 272 | 76 |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | 0.543 | [0.490, 0.596] | 341 | 80 |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | 0.487 | [0.434, 0.540] | 341 | 80 |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | 0.513 | [0.460, 0.567] | 341 | 80 |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | 0.495 | [0.438, 0.553] | 220 | 74 |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | 0.537 | [0.483, 0.590] | 272 | 76 |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | 0.510 | [0.457, 0.564] | 341 | 80 |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | 0.481 | [0.431, 0.535] | 341 | 80 |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | 0.472 | [0.420, 0.526] | 341 | 80 |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-base | 0.509 | [0.450, 0.566] | 220 | 74 |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-base | 0.529 | [0.473, 0.584] | 272 | 76 |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-base | 0.551 | [0.504, 0.599] | 341 | 80 |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-base | 0.548 | [0.494, 0.603] | 341 | 80 |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-base | 0.528 | [0.473, 0.583] | 341 | 80 |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-base | 0.518 | [0.464, 0.574] | 220 | 74 |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-base | 0.515 | [0.458, 0.572] | 272 | 76 |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-base | 0.510 | [0.459, 0.563] | 341 | 80 |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-base | 0.493 | [0.447, 0.538] | 341 | 80 |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-base | 0.501 | [0.438, 0.563] | 341 | 80 |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | 0.505 | [0.448, 0.560] | 220 | 74 |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | 0.529 | [0.475, 0.583] | 272 | 76 |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | 0.507 | [0.460, 0.555] | 341 | 80 |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | 0.501 | [0.453, 0.548] | 341 | 80 |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | 0.490 | [0.431, 0.548] | 341 | 80 |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | 0.527 | [0.475, 0.580] | 220 | 74 |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | 0.533 | [0.482, 0.582] | 272 | 76 |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | 0.525 | [0.475, 0.572] | 341 | 80 |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | 0.499 | [0.452, 0.543] | 341 | 80 |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | 0.534 | [0.474, 0.591] | 341 | 80 |
| blk | d25s3 | meta-llama/Llama-3.2-1B | 0.495 | [0.436, 0.561] | 220 | 74 |
| blk | d50s3 | meta-llama/Llama-3.2-1B | 0.511 | [0.454, 0.570] | 272 | 76 |
| blk | d75s1a | meta-llama/Llama-3.2-1B | 0.522 | [0.478, 0.569] | 341 | 80 |
| blk | d75s2a | meta-llama/Llama-3.2-1B | 0.513 | [0.467, 0.562] | 341 | 80 |
| blk | d75s3a | meta-llama/Llama-3.2-1B | 0.513 | [0.473, 0.554] | 341 | 80 |
| dom | d25s3 | meta-llama/Llama-3.2-1B | 0.450 | [0.402, 0.497] | 220 | 74 |
| dom | d50s3 | meta-llama/Llama-3.2-1B | 0.467 | [0.423, 0.515] | 272 | 76 |
| dom | d75s1a | meta-llama/Llama-3.2-1B | 0.475 | [0.432, 0.519] | 341 | 80 |
| dom | d75s2a | meta-llama/Llama-3.2-1B | 0.460 | [0.421, 0.503] | 341 | 80 |
| dom | d75s3a | meta-llama/Llama-3.2-1B | 0.475 | [0.435, 0.518] | 341 | 80 |
| blk | d25s3 | meta-llama/Llama-3.2-1B-Instruct | 0.482 | [0.425, 0.539] | 220 | 74 |
| blk | d50s3 | meta-llama/Llama-3.2-1B-Instruct | 0.482 | [0.433, 0.532] | 272 | 76 |
| blk | d75s1a | meta-llama/Llama-3.2-1B-Instruct | 0.501 | [0.458, 0.542] | 341 | 80 |
| blk | d75s2a | meta-llama/Llama-3.2-1B-Instruct | 0.510 | [0.467, 0.552] | 341 | 80 |
| blk | d75s3a | meta-llama/Llama-3.2-1B-Instruct | 0.513 | [0.468, 0.555] | 341 | 80 |
| dom | d25s3 | meta-llama/Llama-3.2-1B-Instruct | 0.491 | [0.443, 0.538] | 220 | 74 |
| dom | d50s3 | meta-llama/Llama-3.2-1B-Instruct | 0.478 | [0.436, 0.526] | 272 | 76 |
| dom | d75s1a | meta-llama/Llama-3.2-1B-Instruct | 0.484 | [0.440, 0.528] | 341 | 80 |
| dom | d75s2a | meta-llama/Llama-3.2-1B-Instruct | 0.463 | [0.421, 0.507] | 341 | 80 |
| dom | d75s3a | meta-llama/Llama-3.2-1B-Instruct | 0.490 | [0.448, 0.532] | 341 | 80 |

**Rule effect** — `M_seq(rule) − M_seq(control)` (`rule_effect.csv`)

| family | lexicon | model | control | mean | ci | ci_excludes_zero | helped |
|---|---|---|---|---|---|---|---|
| blk | d25s3 | Qwen/Qwen2.5-72B | norule | 0.258 | [0.079, 0.457] | True | 0.623 |
| blk | d25s3 | Qwen/Qwen2.5-72B | norule_lenmatched | 0.323 | [0.151, 0.518] | True | 0.609 |
| blk | d50s3 | Qwen/Qwen2.5-72B | norule | 0.396 | [0.224, 0.573] | True | 0.574 |
| blk | d50s3 | Qwen/Qwen2.5-72B | norule_lenmatched | 0.445 | [0.274, 0.627] | True | 0.614 |
| blk | d75s1a | Qwen/Qwen2.5-72B | norule | 0.394 | [0.131, 0.679] | True | 0.554 |
| blk | d75s1a | Qwen/Qwen2.5-72B | norule_lenmatched | 0.431 | [0.160, 0.724] | True | 0.554 |
| blk | d75s2a | Qwen/Qwen2.5-72B | norule | 0.666 | [0.433, 0.893] | True | 0.622 |
| blk | d75s2a | Qwen/Qwen2.5-72B | norule_lenmatched | 0.698 | [0.461, 0.931] | True | 0.622 |
| blk | d75s3a | Qwen/Qwen2.5-72B | norule | 0.504 | [0.245, 0.757] | True | 0.587 |
| blk | d75s3a | Qwen/Qwen2.5-72B | norule_lenmatched | 0.550 | [0.291, 0.799] | True | 0.598 |
| dom | d25s3 | Qwen/Qwen2.5-72B | norule | 0.159 | [-0.031, 0.369] | False | 0.545 |
| dom | d25s3 | Qwen/Qwen2.5-72B | norule_lenmatched | 0.231 | [0.053, 0.435] | True | 0.509 |
| dom | d50s3 | Qwen/Qwen2.5-72B | norule | 0.348 | [0.170, 0.536] | True | 0.585 |
| dom | d50s3 | Qwen/Qwen2.5-72B | norule_lenmatched | 0.417 | [0.232, 0.607] | True | 0.596 |
| dom | d75s1a | Qwen/Qwen2.5-72B | norule | 0.251 | [0.005, 0.514] | True | 0.572 |
| dom | d75s1a | Qwen/Qwen2.5-72B | norule_lenmatched | 0.291 | [0.045, 0.558] | True | 0.589 |
| dom | d75s2a | Qwen/Qwen2.5-72B | norule | 0.572 | [0.341, 0.811] | True | 0.592 |
| dom | d75s2a | Qwen/Qwen2.5-72B | norule_lenmatched | 0.595 | [0.363, 0.834] | True | 0.604 |
| dom | d75s3a | Qwen/Qwen2.5-72B | norule | 0.476 | [0.225, 0.729] | True | 0.595 |
| dom | d75s3a | Qwen/Qwen2.5-72B | norule_lenmatched | 0.534 | [0.294, 0.766] | True | 0.622 |
| blk | d25s3 | Qwen/Qwen2.5-72B-Instruct | norule | 0.276 | [0.018, 0.550] | True | 0.618 |
| blk | d25s3 | Qwen/Qwen2.5-72B-Instruct | norule_lenmatched | 0.311 | [0.057, 0.579] | True | 0.623 |
| blk | d50s3 | Qwen/Qwen2.5-72B-Instruct | norule | 0.398 | [0.148, 0.668] | True | 0.603 |
| blk | d50s3 | Qwen/Qwen2.5-72B-Instruct | norule_lenmatched | 0.397 | [0.152, 0.666] | True | 0.614 |
| blk | d75s1a | Qwen/Qwen2.5-72B-Instruct | norule | 0.328 | [-0.033, 0.716] | False | 0.610 |
| blk | d75s1a | Qwen/Qwen2.5-72B-Instruct | norule_lenmatched | 0.314 | [-0.051, 0.713] | False | 0.587 |
| blk | d75s2a | Qwen/Qwen2.5-72B-Instruct | norule | 0.938 | [0.588, 1.281] | True | 0.630 |
| blk | d75s2a | Qwen/Qwen2.5-72B-Instruct | norule_lenmatched | 0.922 | [0.562, 1.276] | True | 0.625 |
| blk | d75s3a | Qwen/Qwen2.5-72B-Instruct | norule | 0.721 | [0.369, 1.072] | True | 0.625 |
| blk | d75s3a | Qwen/Qwen2.5-72B-Instruct | norule_lenmatched | 0.740 | [0.393, 1.085] | True | 0.622 |
| dom | d25s3 | Qwen/Qwen2.5-72B-Instruct | norule | -0.005 | [-0.247, 0.240] | False | 0.514 |
| dom | d25s3 | Qwen/Qwen2.5-72B-Instruct | norule_lenmatched | 0.008 | [-0.230, 0.251] | False | 0.514 |
| dom | d50s3 | Qwen/Qwen2.5-72B-Instruct | norule | 0.220 | [-0.014, 0.472] | False | 0.559 |
| dom | d50s3 | Qwen/Qwen2.5-72B-Instruct | norule_lenmatched | 0.180 | [-0.059, 0.443] | False | 0.555 |
| dom | d75s1a | Qwen/Qwen2.5-72B-Instruct | norule | 0.134 | [-0.236, 0.513] | False | 0.578 |
| dom | d75s1a | Qwen/Qwen2.5-72B-Instruct | norule_lenmatched | 0.102 | [-0.261, 0.474] | False | 0.572 |
| dom | d75s2a | Qwen/Qwen2.5-72B-Instruct | norule | 0.732 | [0.326, 1.121] | True | 0.543 |
| dom | d75s2a | Qwen/Qwen2.5-72B-Instruct | norule_lenmatched | 0.761 | [0.352, 1.155] | True | 0.557 |
| dom | d75s3a | Qwen/Qwen2.5-72B-Instruct | norule | 0.715 | [0.387, 1.071] | True | 0.575 |
| dom | d75s3a | Qwen/Qwen2.5-72B-Instruct | norule_lenmatched | 0.716 | [0.404, 1.056] | True | 0.575 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B | norule | 0.183 | [-0.043, 0.415] | False | 0.559 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.181 | [-0.044, 0.411] | False | 0.545 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B | norule | 0.224 | [0.015, 0.438] | True | 0.592 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.209 | [0.001, 0.423] | True | 0.566 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B | norule | 0.186 | [-0.066, 0.435] | False | 0.572 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.163 | [-0.097, 0.423] | False | 0.581 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B | norule | 0.392 | [0.216, 0.562] | True | 0.601 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.439 | [0.257, 0.613] | True | 0.622 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B | norule | 0.394 | [0.188, 0.615] | True | 0.610 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.401 | [0.177, 0.631] | True | 0.610 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B | norule | 0.161 | [-0.020, 0.362] | False | 0.505 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.178 | [-0.011, 0.382] | False | 0.509 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B | norule | 0.219 | [0.052, 0.397] | True | 0.596 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.206 | [0.034, 0.382] | True | 0.585 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B | norule | 0.233 | [0.051, 0.415] | True | 0.604 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.248 | [0.067, 0.435] | True | 0.595 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B | norule | 0.258 | [0.117, 0.399] | True | 0.563 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.334 | [0.187, 0.484] | True | 0.601 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B | norule | 0.392 | [0.239, 0.541] | True | 0.616 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B | norule_lenmatched | 0.448 | [0.280, 0.616] | True | 0.630 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.301 | [-0.015, 0.642] | False | 0.582 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.265 | [-0.047, 0.595] | False | 0.559 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.317 | [0.059, 0.587] | True | 0.566 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.262 | [0.009, 0.528] | True | 0.562 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.240 | [-0.026, 0.531] | False | 0.601 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.215 | [-0.050, 0.507] | False | 0.563 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.630 | [0.340, 0.921] | True | 0.616 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.628 | [0.350, 0.903] | True | 0.613 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.694 | [0.481, 0.906] | True | 0.625 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.692 | [0.476, 0.913] | True | 0.598 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.209 | [-0.054, 0.510] | False | 0.545 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.158 | [-0.091, 0.442] | False | 0.523 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.215 | [-0.013, 0.461] | False | 0.526 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.166 | [-0.050, 0.397] | False | 0.500 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.236 | [-0.020, 0.507] | False | 0.534 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.229 | [-0.025, 0.496] | False | 0.525 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.468 | [0.195, 0.759] | True | 0.557 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.438 | [0.193, 0.692] | True | 0.584 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule | 0.619 | [0.434, 0.813] | True | 0.572 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-0.5B-Instruct | norule_lenmatched | 0.596 | [0.411, 0.786] | True | 0.572 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B | norule | 0.287 | [0.093, 0.510] | True | 0.586 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.268 | [0.075, 0.482] | True | 0.586 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B | norule | 0.348 | [0.159, 0.545] | True | 0.625 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.321 | [0.135, 0.517] | True | 0.610 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B | norule | 0.199 | [-0.076, 0.474] | False | 0.578 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.179 | [-0.104, 0.455] | False | 0.575 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B | norule | 0.482 | [0.216, 0.768] | True | 0.601 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.477 | [0.222, 0.751] | True | 0.595 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B | norule | 0.503 | [0.306, 0.696] | True | 0.636 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.485 | [0.282, 0.683] | True | 0.628 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B | norule | 0.157 | [-0.073, 0.405] | False | 0.536 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.168 | [-0.048, 0.406] | False | 0.550 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B | norule | 0.229 | [0.028, 0.446] | True | 0.555 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.245 | [0.044, 0.455] | True | 0.537 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B | norule | 0.254 | [0.008, 0.518] | True | 0.543 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.265 | [0.025, 0.525] | True | 0.543 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B | norule | 0.489 | [0.237, 0.769] | True | 0.584 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.490 | [0.240, 0.761] | True | 0.584 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B | norule | 0.487 | [0.335, 0.647] | True | 0.569 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B | norule_lenmatched | 0.495 | [0.335, 0.662] | True | 0.563 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.423 | [0.148, 0.729] | True | 0.600 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.405 | [0.130, 0.705] | True | 0.600 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.386 | [0.114, 0.669] | True | 0.607 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.372 | [0.103, 0.662] | True | 0.592 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.200 | [-0.139, 0.545] | False | 0.572 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.208 | [-0.138, 0.557] | False | 0.557 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.533 | [0.179, 0.894] | True | 0.572 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.581 | [0.228, 0.947] | True | 0.572 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.631 | [0.461, 0.803] | True | 0.601 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.663 | [0.482, 0.853] | True | 0.607 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.214 | [-0.092, 0.558] | False | 0.564 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.222 | [-0.077, 0.564] | False | 0.559 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.231 | [-0.050, 0.538] | False | 0.570 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.250 | [-0.024, 0.556] | False | 0.574 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.296 | [-0.037, 0.631] | False | 0.557 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.298 | [-0.044, 0.644] | False | 0.560 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.555 | [0.233, 0.892] | True | 0.566 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.591 | [0.247, 0.946] | True | 0.572 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule | 0.672 | [0.517, 0.842] | True | 0.595 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-1.5B-Instruct | norule_lenmatched | 0.697 | [0.536, 0.869] | True | 0.613 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B | norule | 0.290 | [-0.033, 0.650] | False | 0.641 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B | norule_lenmatched | 0.254 | [-0.069, 0.617] | False | 0.664 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B | norule | 0.463 | [0.168, 0.760] | True | 0.654 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B | norule_lenmatched | 0.441 | [0.138, 0.743] | True | 0.643 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B | norule | 0.470 | [0.185, 0.765] | True | 0.604 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B | norule_lenmatched | 0.461 | [0.183, 0.755] | True | 0.607 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B | norule | 0.418 | [0.131, 0.716] | True | 0.566 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B | norule_lenmatched | 0.387 | [0.104, 0.682] | True | 0.557 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B | norule | 0.583 | [0.382, 0.787] | True | 0.625 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B | norule_lenmatched | 0.573 | [0.362, 0.789] | True | 0.616 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B | norule | 0.200 | [-0.099, 0.523] | False | 0.555 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B | norule_lenmatched | 0.202 | [-0.097, 0.524] | False | 0.550 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B | norule | 0.356 | [0.099, 0.633] | True | 0.618 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B | norule_lenmatched | 0.379 | [0.115, 0.661] | True | 0.640 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B | norule | 0.307 | [0.027, 0.609] | True | 0.572 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B | norule_lenmatched | 0.324 | [0.059, 0.617] | True | 0.592 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B | norule | 0.395 | [0.116, 0.687] | True | 0.504 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B | norule_lenmatched | 0.391 | [0.134, 0.670] | True | 0.528 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B | norule | 0.459 | [0.265, 0.663] | True | 0.592 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B | norule_lenmatched | 0.480 | [0.288, 0.682] | True | 0.601 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | norule | 0.321 | [-0.065, 0.745] | False | 0.600 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | norule_lenmatched | 0.298 | [-0.097, 0.732] | False | 0.573 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | norule | 0.639 | [0.278, 1.005] | True | 0.643 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | norule_lenmatched | 0.582 | [0.217, 0.951] | True | 0.640 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | norule | 0.498 | [0.153, 0.862] | True | 0.622 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | norule_lenmatched | 0.452 | [0.126, 0.806] | True | 0.604 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | norule | 0.597 | [0.191, 1.021] | True | 0.557 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | norule_lenmatched | 0.579 | [0.175, 0.999] | True | 0.560 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | norule | 0.928 | [0.720, 1.156] | True | 0.645 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | norule_lenmatched | 0.873 | [0.668, 1.101] | True | 0.642 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | norule | 0.138 | [-0.223, 0.530] | False | 0.495 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-14B-Instruct | norule_lenmatched | 0.140 | [-0.217, 0.540] | False | 0.505 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | norule | 0.457 | [0.137, 0.788] | True | 0.614 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-14B-Instruct | norule_lenmatched | 0.441 | [0.110, 0.777] | True | 0.581 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | norule | 0.309 | [-0.065, 0.697] | False | 0.581 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-14B-Instruct | norule_lenmatched | 0.298 | [-0.061, 0.667] | False | 0.566 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | norule | 0.495 | [0.112, 0.888] | True | 0.519 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-14B-Instruct | norule_lenmatched | 0.504 | [0.132, 0.885] | True | 0.513 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | norule | 0.819 | [0.628, 1.031] | True | 0.622 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-14B-Instruct | norule_lenmatched | 0.811 | [0.620, 1.025] | True | 0.613 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B | norule | 0.035 | [-0.191, 0.292] | False | 0.541 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B | norule_lenmatched | 0.051 | [-0.181, 0.308] | False | 0.591 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B | norule | 0.154 | [-0.026, 0.341] | False | 0.599 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B | norule_lenmatched | 0.160 | [-0.022, 0.351] | False | 0.621 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B | norule | 0.194 | [-0.040, 0.445] | False | 0.575 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B | norule_lenmatched | 0.185 | [-0.058, 0.442] | False | 0.589 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B | norule | 0.377 | [0.127, 0.631] | True | 0.554 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B | norule_lenmatched | 0.359 | [0.118, 0.606] | True | 0.578 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B | norule | 0.335 | [0.139, 0.530] | True | 0.563 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B | norule_lenmatched | 0.327 | [0.144, 0.510] | True | 0.589 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B | norule | 0.013 | [-0.219, 0.255] | False | 0.509 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B | norule_lenmatched | 0.024 | [-0.215, 0.278] | False | 0.491 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B | norule | 0.121 | [-0.094, 0.332] | False | 0.548 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B | norule_lenmatched | 0.127 | [-0.097, 0.343] | False | 0.548 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B | norule | 0.168 | [-0.057, 0.422] | False | 0.528 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B | norule_lenmatched | 0.156 | [-0.076, 0.414] | False | 0.540 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B | norule | 0.330 | [0.106, 0.556] | True | 0.537 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B | norule_lenmatched | 0.328 | [0.098, 0.558] | True | 0.543 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B | norule | 0.356 | [0.209, 0.513] | True | 0.563 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B | norule_lenmatched | 0.357 | [0.212, 0.510] | True | 0.566 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | norule | 0.343 | [0.056, 0.672] | True | 0.559 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | norule_lenmatched | 0.405 | [0.114, 0.734] | True | 0.568 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | norule | 0.513 | [0.221, 0.821] | True | 0.577 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | norule_lenmatched | 0.533 | [0.235, 0.842] | True | 0.607 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | norule | 0.306 | [-0.157, 0.788] | False | 0.531 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | norule_lenmatched | 0.343 | [-0.100, 0.811] | False | 0.566 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | norule | 0.934 | [0.470, 1.431] | True | 0.601 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | norule_lenmatched | 1.004 | [0.540, 1.490] | True | 0.616 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | norule | 0.805 | [0.500, 1.133] | True | 0.587 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | norule_lenmatched | 0.834 | [0.519, 1.162] | True | 0.628 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | norule | 0.099 | [-0.205, 0.446] | False | 0.532 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-32B-Instruct | norule_lenmatched | 0.146 | [-0.166, 0.509] | False | 0.532 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | norule | 0.288 | [-0.002, 0.621] | False | 0.555 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-32B-Instruct | norule_lenmatched | 0.289 | [-0.001, 0.629] | False | 0.588 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | norule | 0.237 | [-0.217, 0.717] | False | 0.569 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-32B-Instruct | norule_lenmatched | 0.247 | [-0.201, 0.710] | False | 0.566 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | norule | 0.759 | [0.373, 1.159] | True | 0.587 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-32B-Instruct | norule_lenmatched | 0.797 | [0.410, 1.189] | True | 0.587 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | norule | 0.920 | [0.620, 1.266] | True | 0.616 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-32B-Instruct | norule_lenmatched | 0.903 | [0.619, 1.236] | True | 0.619 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B | norule | 0.243 | [-0.022, 0.512] | False | 0.645 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B | norule_lenmatched | 0.250 | [-0.013, 0.522] | False | 0.632 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B | norule | 0.272 | [0.028, 0.528] | True | 0.588 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B | norule_lenmatched | 0.255 | [0.012, 0.515] | True | 0.562 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B | norule | 0.216 | [-0.070, 0.518] | False | 0.589 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B | norule_lenmatched | 0.218 | [-0.078, 0.522] | False | 0.581 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B | norule | 0.504 | [0.262, 0.756] | True | 0.628 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B | norule_lenmatched | 0.515 | [0.265, 0.774] | True | 0.633 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B | norule | 0.553 | [0.357, 0.760] | True | 0.607 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B | norule_lenmatched | 0.541 | [0.346, 0.744] | True | 0.592 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B | norule | 0.207 | [-0.001, 0.433] | False | 0.600 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B | norule_lenmatched | 0.238 | [0.017, 0.473] | True | 0.568 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B | norule | 0.235 | [0.023, 0.446] | True | 0.548 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B | norule_lenmatched | 0.248 | [0.038, 0.464] | True | 0.537 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B | norule | 0.211 | [-0.040, 0.477] | False | 0.545 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B | norule_lenmatched | 0.212 | [-0.047, 0.478] | False | 0.537 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B | norule | 0.384 | [0.151, 0.637] | True | 0.616 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B | norule_lenmatched | 0.418 | [0.178, 0.673] | True | 0.610 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B | norule | 0.509 | [0.325, 0.706] | True | 0.589 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B | norule_lenmatched | 0.500 | [0.319, 0.684] | True | 0.575 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | norule | 0.132 | [-0.202, 0.492] | False | 0.545 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | norule_lenmatched | 0.102 | [-0.228, 0.467] | False | 0.527 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | norule | 0.302 | [-0.015, 0.646] | False | 0.559 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | norule_lenmatched | 0.259 | [-0.054, 0.596] | False | 0.537 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | norule | 0.167 | [-0.171, 0.503] | False | 0.554 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | norule_lenmatched | 0.169 | [-0.168, 0.514] | False | 0.548 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | norule | 0.544 | [0.196, 0.913] | True | 0.592 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | norule_lenmatched | 0.554 | [0.205, 0.921] | True | 0.604 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | norule | 0.709 | [0.480, 0.947] | True | 0.566 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | norule_lenmatched | 0.700 | [0.455, 0.957] | True | 0.560 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | norule | 0.121 | [-0.210, 0.483] | False | 0.495 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-3B-Instruct | norule_lenmatched | 0.121 | [-0.219, 0.490] | False | 0.514 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | norule | 0.301 | [-0.003, 0.639] | False | 0.529 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-3B-Instruct | norule_lenmatched | 0.290 | [-0.020, 0.628] | False | 0.537 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | norule | 0.288 | [-0.016, 0.615] | False | 0.531 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-3B-Instruct | norule_lenmatched | 0.275 | [-0.031, 0.592] | False | 0.557 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | norule | 0.492 | [0.172, 0.843] | True | 0.598 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-3B-Instruct | norule_lenmatched | 0.529 | [0.197, 0.892] | True | 0.622 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | norule | 0.723 | [0.512, 0.939] | True | 0.592 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-3B-Instruct | norule_lenmatched | 0.703 | [0.486, 0.926] | True | 0.592 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B | norule | 0.377 | [0.075, 0.706] | True | 0.659 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B | norule_lenmatched | 0.378 | [0.068, 0.709] | True | 0.668 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B | norule | 0.394 | [0.126, 0.685] | True | 0.618 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B | norule_lenmatched | 0.398 | [0.128, 0.687] | True | 0.629 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B | norule | 0.097 | [-0.187, 0.396] | False | 0.578 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B | norule_lenmatched | 0.133 | [-0.150, 0.436] | False | 0.592 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B | norule | 0.589 | [0.248, 0.949] | True | 0.604 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B | norule_lenmatched | 0.649 | [0.313, 1.002] | True | 0.607 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B | norule | 0.554 | [0.349, 0.771] | True | 0.613 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B | norule_lenmatched | 0.574 | [0.363, 0.796] | True | 0.630 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B | norule | 0.217 | [-0.110, 0.574] | False | 0.527 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B | norule_lenmatched | 0.219 | [-0.106, 0.570] | False | 0.550 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B | norule | 0.276 | [0.010, 0.560] | True | 0.559 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B | norule_lenmatched | 0.283 | [0.021, 0.563] | True | 0.566 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B | norule | 0.088 | [-0.168, 0.356] | False | 0.528 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B | norule_lenmatched | 0.118 | [-0.126, 0.375] | False | 0.543 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B | norule | 0.493 | [0.174, 0.830] | True | 0.581 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B | norule_lenmatched | 0.522 | [0.220, 0.847] | True | 0.578 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B | norule | 0.501 | [0.339, 0.678] | True | 0.581 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B | norule_lenmatched | 0.511 | [0.343, 0.687] | True | 0.581 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | norule | 0.289 | [-0.067, 0.689] | False | 0.573 |
| blk | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | norule_lenmatched | 0.262 | [-0.104, 0.663] | False | 0.568 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | norule | 0.450 | [0.104, 0.815] | True | 0.570 |
| blk | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | norule_lenmatched | 0.423 | [0.077, 0.793] | True | 0.592 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | norule | 0.158 | [-0.201, 0.542] | False | 0.560 |
| blk | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | norule_lenmatched | 0.178 | [-0.172, 0.551] | False | 0.560 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | norule | 0.628 | [0.230, 1.033] | True | 0.598 |
| blk | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | norule_lenmatched | 0.638 | [0.250, 1.034] | True | 0.607 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | norule | 0.730 | [0.517, 0.956] | True | 0.592 |
| blk | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | norule_lenmatched | 0.715 | [0.492, 0.951] | True | 0.598 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | norule | 0.052 | [-0.289, 0.426] | False | 0.477 |
| dom | d25s3 | Qwen/Qwen2.5-Coder-7B-Instruct | norule_lenmatched | 0.028 | [-0.315, 0.408] | False | 0.491 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | norule | 0.238 | [-0.090, 0.575] | False | 0.511 |
| dom | d50s3 | Qwen/Qwen2.5-Coder-7B-Instruct | norule_lenmatched | 0.229 | [-0.093, 0.560] | False | 0.518 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | norule | 0.195 | [-0.128, 0.540] | False | 0.525 |
| dom | d75s1a | Qwen/Qwen2.5-Coder-7B-Instruct | norule_lenmatched | 0.224 | [-0.091, 0.556] | False | 0.531 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | norule | 0.475 | [0.160, 0.804] | True | 0.560 |
| dom | d75s2a | Qwen/Qwen2.5-Coder-7B-Instruct | norule_lenmatched | 0.470 | [0.163, 0.788] | True | 0.545 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | norule | 0.642 | [0.469, 0.837] | True | 0.575 |
| dom | d75s3a | Qwen/Qwen2.5-Coder-7B-Instruct | norule_lenmatched | 0.625 | [0.450, 0.822] | True | 0.595 |
| blk | d25s3 | bigcode/starcoder2-3b | norule | 0.127 | [-0.096, 0.366] | False | 0.482 |
| blk | d25s3 | bigcode/starcoder2-3b | norule_lenmatched | 0.121 | [-0.098, 0.349] | False | 0.523 |
| blk | d50s3 | bigcode/starcoder2-3b | norule | 0.246 | [0.024, 0.475] | True | 0.607 |
| blk | d50s3 | bigcode/starcoder2-3b | norule_lenmatched | 0.212 | [0.002, 0.430] | True | 0.581 |
| blk | d75s1a | bigcode/starcoder2-3b | norule | 0.143 | [-0.162, 0.447] | False | 0.587 |
| blk | d75s1a | bigcode/starcoder2-3b | norule_lenmatched | 0.137 | [-0.169, 0.433] | False | 0.560 |
| blk | d75s2a | bigcode/starcoder2-3b | norule | 0.441 | [0.245, 0.656] | True | 0.587 |
| blk | d75s2a | bigcode/starcoder2-3b | norule_lenmatched | 0.463 | [0.259, 0.679] | True | 0.589 |
| blk | d75s3a | bigcode/starcoder2-3b | norule | 0.464 | [0.212, 0.721] | True | 0.607 |
| blk | d75s3a | bigcode/starcoder2-3b | norule_lenmatched | 0.426 | [0.169, 0.685] | True | 0.589 |
| dom | d25s3 | bigcode/starcoder2-3b | norule | 0.094 | [-0.142, 0.345] | False | 0.477 |
| dom | d25s3 | bigcode/starcoder2-3b | norule_lenmatched | 0.118 | [-0.113, 0.367] | False | 0.477 |
| dom | d50s3 | bigcode/starcoder2-3b | norule | 0.221 | [-0.009, 0.482] | False | 0.529 |
| dom | d50s3 | bigcode/starcoder2-3b | norule_lenmatched | 0.219 | [-0.007, 0.475] | False | 0.515 |
| dom | d75s1a | bigcode/starcoder2-3b | norule | 0.229 | [0.002, 0.472] | True | 0.531 |
| dom | d75s1a | bigcode/starcoder2-3b | norule_lenmatched | 0.231 | [0.003, 0.475] | True | 0.519 |
| dom | d75s2a | bigcode/starcoder2-3b | norule | 0.339 | [0.099, 0.579] | True | 0.534 |
| dom | d75s2a | bigcode/starcoder2-3b | norule_lenmatched | 0.396 | [0.155, 0.642] | True | 0.543 |
| dom | d75s3a | bigcode/starcoder2-3b | norule | 0.542 | [0.378, 0.722] | True | 0.601 |
| dom | d75s3a | bigcode/starcoder2-3b | norule_lenmatched | 0.556 | [0.383, 0.742] | True | 0.604 |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-base | norule | 0.095 | [-0.097, 0.300] | False | 0.491 |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-base | norule_lenmatched | 0.085 | [-0.107, 0.289] | False | 0.459 |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-base | norule | 0.166 | [-0.026, 0.366] | False | 0.544 |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-base | norule_lenmatched | 0.161 | [-0.037, 0.368] | False | 0.537 |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-base | norule | -0.112 | [-0.412, 0.186] | False | 0.531 |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-base | norule_lenmatched | -0.113 | [-0.417, 0.191] | False | 0.516 |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-base | norule | 0.513 | [0.272, 0.780] | True | 0.563 |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-base | norule_lenmatched | 0.522 | [0.280, 0.784] | True | 0.572 |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-base | norule | 0.321 | [0.054, 0.586] | True | 0.569 |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-base | norule_lenmatched | 0.305 | [0.028, 0.574] | True | 0.554 |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-base | norule | 0.064 | [-0.119, 0.256] | False | 0.523 |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-base | norule_lenmatched | 0.078 | [-0.092, 0.265] | False | 0.514 |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-base | norule | 0.161 | [-0.029, 0.347] | False | 0.559 |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-base | norule_lenmatched | 0.174 | [-0.005, 0.359] | False | 0.537 |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-base | norule | 0.010 | [-0.207, 0.240] | False | 0.531 |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-base | norule_lenmatched | -0.006 | [-0.226, 0.225] | False | 0.501 |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-base | norule | 0.452 | [0.188, 0.730] | True | 0.551 |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-base | norule_lenmatched | 0.461 | [0.200, 0.737] | True | 0.540 |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-base | norule | 0.723 | [0.523, 0.931] | True | 0.604 |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-base | norule_lenmatched | 0.714 | [0.506, 0.939] | True | 0.581 |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | norule | -0.051 | [-0.312, 0.244] | False | 0.432 |
| blk | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | norule_lenmatched | -0.076 | [-0.334, 0.207] | False | 0.436 |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | norule | 0.060 | [-0.213, 0.350] | False | 0.456 |
| blk | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | norule_lenmatched | 0.052 | [-0.220, 0.341] | False | 0.460 |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | norule | -0.018 | [-0.357, 0.344] | False | 0.499 |
| blk | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | norule_lenmatched | 0.054 | [-0.281, 0.402] | False | 0.487 |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | norule | 0.585 | [0.299, 0.873] | True | 0.554 |
| blk | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | norule_lenmatched | 0.617 | [0.329, 0.907] | True | 0.551 |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | norule | 0.232 | [-0.043, 0.508] | False | 0.487 |
| blk | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | norule_lenmatched | 0.265 | [-0.019, 0.547] | False | 0.499 |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | norule | 0.142 | [-0.134, 0.430] | False | 0.536 |
| dom | d25s3 | deepseek-ai/deepseek-coder-1.3b-instruct | norule_lenmatched | 0.070 | [-0.199, 0.344] | False | 0.527 |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | norule | 0.155 | [-0.113, 0.451] | False | 0.500 |
| dom | d50s3 | deepseek-ai/deepseek-coder-1.3b-instruct | norule_lenmatched | 0.145 | [-0.122, 0.435] | False | 0.507 |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | norule | 0.311 | [-0.036, 0.665] | False | 0.522 |
| dom | d75s1a | deepseek-ai/deepseek-coder-1.3b-instruct | norule_lenmatched | 0.298 | [-0.056, 0.665] | False | 0.510 |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | norule | 0.799 | [0.450, 1.155] | True | 0.569 |
| dom | d75s2a | deepseek-ai/deepseek-coder-1.3b-instruct | norule_lenmatched | 0.807 | [0.470, 1.154] | True | 0.575 |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | norule | 0.920 | [0.686, 1.166] | True | 0.563 |
| dom | d75s3a | deepseek-ai/deepseek-coder-1.3b-instruct | norule_lenmatched | 0.908 | [0.674, 1.159] | True | 0.537 |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-base | norule | 0.295 | [0.031, 0.587] | True | 0.623 |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-base | norule_lenmatched | 0.361 | [0.093, 0.665] | True | 0.632 |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-base | norule | 0.397 | [0.165, 0.660] | True | 0.599 |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-base | norule_lenmatched | 0.448 | [0.208, 0.711] | True | 0.654 |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-base | norule | 0.299 | [0.056, 0.562] | True | 0.566 |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-base | norule_lenmatched | 0.340 | [0.081, 0.616] | True | 0.604 |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-base | norule | 0.482 | [0.277, 0.700] | True | 0.604 |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-base | norule_lenmatched | 0.529 | [0.316, 0.752] | True | 0.595 |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-base | norule | 0.552 | [0.317, 0.792] | True | 0.584 |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-base | norule_lenmatched | 0.600 | [0.363, 0.844] | True | 0.639 |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-base | norule | 0.246 | [-0.026, 0.521] | False | 0.595 |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-base | norule_lenmatched | 0.299 | [0.024, 0.572] | True | 0.668 |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-base | norule | 0.354 | [0.111, 0.616] | True | 0.559 |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-base | norule_lenmatched | 0.411 | [0.170, 0.673] | True | 0.603 |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-base | norule | 0.262 | [0.040, 0.500] | True | 0.537 |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-base | norule_lenmatched | 0.316 | [0.093, 0.556] | True | 0.587 |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-base | norule | 0.472 | [0.252, 0.711] | True | 0.572 |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-base | norule_lenmatched | 0.530 | [0.307, 0.768] | True | 0.575 |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-base | norule | 0.556 | [0.315, 0.814] | True | 0.548 |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-base | norule_lenmatched | 0.605 | [0.369, 0.865] | True | 0.572 |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | norule | 0.250 | [-0.097, 0.654] | False | 0.605 |
| blk | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | norule_lenmatched | 0.319 | [-0.021, 0.712] | False | 0.623 |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | norule | 0.309 | [0.001, 0.665] | True | 0.526 |
| blk | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | norule_lenmatched | 0.326 | [0.020, 0.675] | True | 0.559 |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | norule | 0.202 | [-0.080, 0.501] | False | 0.522 |
| blk | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | norule_lenmatched | 0.218 | [-0.082, 0.539] | False | 0.534 |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | norule | 0.498 | [0.274, 0.734] | True | 0.589 |
| blk | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | norule_lenmatched | 0.558 | [0.321, 0.813] | True | 0.604 |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | norule | 0.495 | [0.240, 0.761] | True | 0.563 |
| blk | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | norule_lenmatched | 0.531 | [0.258, 0.800] | True | 0.584 |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | norule | 0.195 | [-0.167, 0.564] | False | 0.564 |
| dom | d25s3 | deepseek-ai/deepseek-coder-33b-instruct | norule_lenmatched | 0.244 | [-0.109, 0.591] | False | 0.568 |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | norule | 0.279 | [-0.026, 0.611] | False | 0.515 |
| dom | d50s3 | deepseek-ai/deepseek-coder-33b-instruct | norule_lenmatched | 0.294 | [-0.006, 0.617] | False | 0.518 |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | norule | 0.139 | [-0.125, 0.417] | False | 0.507 |
| dom | d75s1a | deepseek-ai/deepseek-coder-33b-instruct | norule_lenmatched | 0.176 | [-0.083, 0.448] | False | 0.519 |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | norule | 0.599 | [0.332, 0.885] | True | 0.581 |
| dom | d75s2a | deepseek-ai/deepseek-coder-33b-instruct | norule_lenmatched | 0.635 | [0.366, 0.913] | True | 0.575 |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | norule | 0.473 | [0.214, 0.745] | True | 0.531 |
| dom | d75s3a | deepseek-ai/deepseek-coder-33b-instruct | norule_lenmatched | 0.496 | [0.233, 0.769] | True | 0.519 |
| blk | d25s3 | meta-llama/Llama-3.2-1B | norule | 0.220 | [0.078, 0.379] | True | 0.564 |
| blk | d25s3 | meta-llama/Llama-3.2-1B | norule_lenmatched | 0.192 | [0.046, 0.346] | True | 0.595 |
| blk | d50s3 | meta-llama/Llama-3.2-1B | norule | 0.209 | [0.058, 0.362] | True | 0.603 |
| blk | d50s3 | meta-llama/Llama-3.2-1B | norule_lenmatched | 0.192 | [0.045, 0.344] | True | 0.614 |
| blk | d75s1a | meta-llama/Llama-3.2-1B | norule | 0.086 | [-0.239, 0.425] | False | 0.548 |
| blk | d75s1a | meta-llama/Llama-3.2-1B | norule_lenmatched | 0.101 | [-0.224, 0.444] | False | 0.554 |
| blk | d75s2a | meta-llama/Llama-3.2-1B | norule | 0.326 | [0.087, 0.578] | True | 0.537 |
| blk | d75s2a | meta-llama/Llama-3.2-1B | norule_lenmatched | 0.342 | [0.090, 0.598] | True | 0.543 |
| blk | d75s3a | meta-llama/Llama-3.2-1B | norule | 0.331 | [0.069, 0.565] | True | 0.592 |
| blk | d75s3a | meta-llama/Llama-3.2-1B | norule_lenmatched | 0.306 | [0.028, 0.554] | True | 0.610 |
| dom | d25s3 | meta-llama/Llama-3.2-1B | norule | 0.300 | [0.158, 0.463] | True | 0.586 |
| dom | d25s3 | meta-llama/Llama-3.2-1B | norule_lenmatched | 0.303 | [0.164, 0.456] | True | 0.600 |
| dom | d50s3 | meta-llama/Llama-3.2-1B | norule | 0.287 | [0.142, 0.444] | True | 0.607 |
| dom | d50s3 | meta-llama/Llama-3.2-1B | norule_lenmatched | 0.272 | [0.127, 0.422] | True | 0.618 |
| dom | d75s1a | meta-llama/Llama-3.2-1B | norule | 0.177 | [-0.056, 0.418] | False | 0.510 |
| dom | d75s1a | meta-llama/Llama-3.2-1B | norule_lenmatched | 0.179 | [-0.055, 0.427] | False | 0.522 |
| dom | d75s2a | meta-llama/Llama-3.2-1B | norule | 0.255 | [0.066, 0.447] | True | 0.537 |
| dom | d75s2a | meta-llama/Llama-3.2-1B | norule_lenmatched | 0.292 | [0.085, 0.501] | True | 0.545 |
| dom | d75s3a | meta-llama/Llama-3.2-1B | norule | 0.402 | [0.271, 0.535] | True | 0.601 |
| dom | d75s3a | meta-llama/Llama-3.2-1B | norule_lenmatched | 0.414 | [0.268, 0.558] | True | 0.598 |
| blk | d25s3 | meta-llama/Llama-3.2-1B-Instruct | norule | 0.433 | [0.175, 0.699] | True | 0.614 |
| blk | d25s3 | meta-llama/Llama-3.2-1B-Instruct | norule_lenmatched | 0.404 | [0.124, 0.688] | True | 0.582 |
| blk | d50s3 | meta-llama/Llama-3.2-1B-Instruct | norule | 0.342 | [0.115, 0.562] | True | 0.588 |
| blk | d50s3 | meta-llama/Llama-3.2-1B-Instruct | norule_lenmatched | 0.322 | [0.082, 0.548] | True | 0.588 |
| blk | d75s1a | meta-llama/Llama-3.2-1B-Instruct | norule | 0.158 | [-0.219, 0.555] | False | 0.522 |
| blk | d75s1a | meta-llama/Llama-3.2-1B-Instruct | norule_lenmatched | 0.154 | [-0.252, 0.580] | False | 0.528 |
| blk | d75s2a | meta-llama/Llama-3.2-1B-Instruct | norule | 0.297 | [-0.023, 0.601] | False | 0.554 |
| blk | d75s2a | meta-llama/Llama-3.2-1B-Instruct | norule_lenmatched | 0.314 | [0.001, 0.616] | True | 0.540 |
| blk | d75s3a | meta-llama/Llama-3.2-1B-Instruct | norule | 0.494 | [0.235, 0.746] | True | 0.610 |
| blk | d75s3a | meta-llama/Llama-3.2-1B-Instruct | norule_lenmatched | 0.528 | [0.251, 0.800] | True | 0.613 |
| dom | d25s3 | meta-llama/Llama-3.2-1B-Instruct | norule | 0.374 | [0.186, 0.586] | True | 0.618 |
| dom | d25s3 | meta-llama/Llama-3.2-1B-Instruct | norule_lenmatched | 0.398 | [0.217, 0.607] | True | 0.591 |
| dom | d50s3 | meta-llama/Llama-3.2-1B-Instruct | norule | 0.237 | [0.065, 0.408] | True | 0.570 |
| dom | d50s3 | meta-llama/Llama-3.2-1B-Instruct | norule_lenmatched | 0.290 | [0.124, 0.447] | True | 0.585 |
| dom | d75s1a | meta-llama/Llama-3.2-1B-Instruct | norule | 0.211 | [-0.083, 0.519] | False | 0.507 |
| dom | d75s1a | meta-llama/Llama-3.2-1B-Instruct | norule_lenmatched | 0.257 | [-0.063, 0.597] | False | 0.531 |
| dom | d75s2a | meta-llama/Llama-3.2-1B-Instruct | norule | 0.196 | [-0.028, 0.419] | False | 0.566 |
| dom | d75s2a | meta-llama/Llama-3.2-1B-Instruct | norule_lenmatched | 0.273 | [0.049, 0.503] | True | 0.575 |
| dom | d75s3a | meta-llama/Llama-3.2-1B-Instruct | norule | 0.450 | [0.280, 0.638] | True | 0.589 |
| dom | d75s3a | meta-llama/Llama-3.2-1B-Instruct | norule_lenmatched | 0.565 | [0.391, 0.756] | True | 0.628 |

**Extinction** — Kaplan–Meier median shots (`kstar_survival.csv`)

| family | model | population | median | ci | n | cens |
|---|---|---|---|---|---|---|
| blk | Qwen/Qwen2.5-72B | ALL_SITES | 0 | [0.000, 0.337] | 205 | 0.112 |
| blk | Qwen/Qwen2.5-72B | INITIALLY_WRONG | 8.42849 | [3.234, 11.687] | 93 | 0.247 |
| dom | Qwen/Qwen2.5-72B | ALL_SITES | 0 | [0.000, 0.540] | 195 | 0.082 |
| dom | Qwen/Qwen2.5-72B | INITIALLY_WRONG | 3.35111 | [1.915, 6.300] | 83 | 0.193 |
| blk | Qwen/Qwen2.5-72B-Instruct | ALL_SITES | 0 | [0.000, 0.907] | 205 | 0.137 |
| blk | Qwen/Qwen2.5-72B-Instruct | INITIALLY_WRONG | 11.2236 | [7.235, 19.062] | 97 | 0.289 |
| dom | Qwen/Qwen2.5-72B-Instruct | ALL_SITES | 0 | [0.000, 0.631] | 195 | 0.108 |
| dom | Qwen/Qwen2.5-72B-Instruct | INITIALLY_WRONG | 4.19518 | [2.083, 6.924] | 89 | 0.236 |
| blk | Qwen/Qwen2.5-Coder-0.5B | ALL_SITES | 0.455665 | [0.000, 1.277] | 205 | 0.112 |
| blk | Qwen/Qwen2.5-Coder-0.5B | INITIALLY_WRONG | 4.96643 | [1.848, 11.721] | 114 | 0.202 |
| dom | Qwen/Qwen2.5-Coder-0.5B | ALL_SITES | 0.257451 | [0.000, 0.971] | 195 | 0.067 |
| dom | Qwen/Qwen2.5-Coder-0.5B | INITIALLY_WRONG | 2.57902 | [1.247, 6.462] | 104 | 0.125 |
| blk | Qwen/Qwen2.5-Coder-0.5B-Instruct | ALL_SITES | 0 | [0.000, 0.971] | 205 | 0.102 |
| blk | Qwen/Qwen2.5-Coder-0.5B-Instruct | INITIALLY_WRONG | 9.09806 | [3.700, 12.136] | 102 | 0.206 |
| dom | Qwen/Qwen2.5-Coder-0.5B-Instruct | ALL_SITES | 0 | [0.000, 0.693] | 195 | 0.056 |
| dom | Qwen/Qwen2.5-Coder-0.5B-Instruct | INITIALLY_WRONG | 4.60239 | [1.584, 12.750] | 88 | 0.125 |
| blk | Qwen/Qwen2.5-Coder-1.5B | ALL_SITES | 0.252898 | [0.000, 1.451] | 205 | 0.141 |
| blk | Qwen/Qwen2.5-Coder-1.5B | INITIALLY_WRONG | 5.18706 | [2.669, 11.682] | 110 | 0.264 |
| dom | Qwen/Qwen2.5-Coder-1.5B | ALL_SITES | 0.159048 | [0.000, 0.772] | 195 | 0.138 |
| dom | Qwen/Qwen2.5-Coder-1.5B | INITIALLY_WRONG | 3.07947 | [1.416, 18.733] | 100 | 0.270 |
| blk | Qwen/Qwen2.5-Coder-1.5B-Instruct | ALL_SITES | 0.00802767 | [0.000, 1.103] | 205 | 0.132 |
| blk | Qwen/Qwen2.5-Coder-1.5B-Instruct | INITIALLY_WRONG | 9.24575 | [3.884, 13.370] | 103 | 0.262 |
| dom | Qwen/Qwen2.5-Coder-1.5B-Instruct | ALL_SITES | 0 | [0.000, 0.559] | 195 | 0.072 |
| dom | Qwen/Qwen2.5-Coder-1.5B-Instruct | INITIALLY_WRONG | 3.80592 | [1.227, 6.545] | 87 | 0.161 |
| blk | Qwen/Qwen2.5-Coder-14B | ALL_SITES | 0 | [0.000, 0.678] | 205 | 0.063 |
| blk | Qwen/Qwen2.5-Coder-14B | INITIALLY_WRONG | 3.86112 | [1.852, 10.098] | 101 | 0.129 |
| dom | Qwen/Qwen2.5-Coder-14B | ALL_SITES | 0 | [0.000, 0.544] | 195 | 0.036 |
| dom | Qwen/Qwen2.5-Coder-14B | INITIALLY_WRONG | 1.62838 | [0.991, 3.083] | 91 | 0.077 |
| blk | Qwen/Qwen2.5-Coder-14B-Instruct | ALL_SITES | 0 | [0.000, 0.814] | 205 | 0.073 |
| blk | Qwen/Qwen2.5-Coder-14B-Instruct | INITIALLY_WRONG | 6.27853 | [1.955, 10.294] | 102 | 0.147 |
| dom | Qwen/Qwen2.5-Coder-14B-Instruct | ALL_SITES | 0.622478 | [0.000, 1.415] | 195 | 0.082 |
| dom | Qwen/Qwen2.5-Coder-14B-Instruct | INITIALLY_WRONG | 3.21038 | [2.481, 5.994] | 111 | 0.144 |
| blk | Qwen/Qwen2.5-Coder-32B | ALL_SITES | 0.328432 | [0.000, 1.094] | 205 | 0.063 |
| blk | Qwen/Qwen2.5-Coder-32B | INITIALLY_WRONG | 3.7464 | [2.288, 8.111] | 107 | 0.121 |
| dom | Qwen/Qwen2.5-Coder-32B | ALL_SITES | 0 | [0.000, 0.565] | 195 | 0.062 |
| dom | Qwen/Qwen2.5-Coder-32B | INITIALLY_WRONG | 1.36045 | [1.039, 2.662] | 95 | 0.126 |
| blk | Qwen/Qwen2.5-Coder-32B-Instruct | ALL_SITES | 0 | [0.000, 0.214] | 205 | 0.083 |
| blk | Qwen/Qwen2.5-Coder-32B-Instruct | INITIALLY_WRONG | 3.60567 | [1.753, 9.932] | 86 | 0.198 |
| dom | Qwen/Qwen2.5-Coder-32B-Instruct | ALL_SITES | 0 | [0.000, 0.323] | 195 | 0.092 |
| dom | Qwen/Qwen2.5-Coder-32B-Instruct | INITIALLY_WRONG | 1.78338 | [1.230, 3.972] | 86 | 0.209 |
| blk | Qwen/Qwen2.5-Coder-3B | ALL_SITES | 0.204034 | [0.000, 1.515] | 205 | 0.146 |
| blk | Qwen/Qwen2.5-Coder-3B | INITIALLY_WRONG | 11.6422 | [2.998, 18.277] | 107 | 0.280 |
| dom | Qwen/Qwen2.5-Coder-3B | ALL_SITES | 0.161085 | [0.000, 0.956] | 195 | 0.138 |
| dom | Qwen/Qwen2.5-Coder-3B | INITIALLY_WRONG | 3.33119 | [1.227, 14.790] | 99 | 0.273 |
| blk | Qwen/Qwen2.5-Coder-3B-Instruct | ALL_SITES | 0.361723 | [0.000, 1.243] | 205 | 0.156 |
| blk | Qwen/Qwen2.5-Coder-3B-Instruct | INITIALLY_WRONG | 7.14216 | [3.112, 16.326] | 112 | 0.286 |
| dom | Qwen/Qwen2.5-Coder-3B-Instruct | ALL_SITES | 0.136851 | [0.000, 0.733] | 195 | 0.144 |
| dom | Qwen/Qwen2.5-Coder-3B-Instruct | INITIALLY_WRONG | 3.19036 | [1.253, 8.784] | 99 | 0.283 |
| blk | Qwen/Qwen2.5-Coder-7B | ALL_SITES | 0.0677686 | [0.000, 1.904] | 205 | 0.117 |
| blk | Qwen/Qwen2.5-Coder-7B | INITIALLY_WRONG | 11.0416 | [5.864, 18.638] | 104 | 0.231 |
| dom | Qwen/Qwen2.5-Coder-7B | ALL_SITES | 0.224401 | [0.000, 0.779] | 195 | 0.103 |
| dom | Qwen/Qwen2.5-Coder-7B | INITIALLY_WRONG | 2.66881 | [1.590, 7.053] | 103 | 0.194 |
| blk | Qwen/Qwen2.5-Coder-7B-Instruct | ALL_SITES | 0.122588 | [0.000, 1.399] | 205 | 0.132 |
| blk | Qwen/Qwen2.5-Coder-7B-Instruct | INITIALLY_WRONG | 10.5342 | [5.352, 18.487] | 105 | 0.257 |
| dom | Qwen/Qwen2.5-Coder-7B-Instruct | ALL_SITES | 0.470986 | [0.000, 1.122] | 195 | 0.077 |
| dom | Qwen/Qwen2.5-Coder-7B-Instruct | INITIALLY_WRONG | 2.1184 | [1.275, 5.478] | 115 | 0.130 |
| blk | bigcode/starcoder2-3b | ALL_SITES | 0.472499 | [0.000, 1.026] | 205 | 0.098 |
| blk | bigcode/starcoder2-3b | INITIALLY_WRONG | 6.37577 | [2.456, 14.640] | 109 | 0.183 |
| dom | bigcode/starcoder2-3b | ALL_SITES | 0.246761 | [0.000, 1.003] | 195 | 0.108 |
| dom | bigcode/starcoder2-3b | INITIALLY_WRONG | 2.39566 | [1.252, 4.764] | 109 | 0.193 |
| blk | deepseek-ai/deepseek-coder-1.3b-base | ALL_SITES | 0 | [0.000, 0.926] | 205 | 0.102 |
| blk | deepseek-ai/deepseek-coder-1.3b-base | INITIALLY_WRONG | 5.53941 | [1.752, 12.673] | 99 | 0.212 |
| dom | deepseek-ai/deepseek-coder-1.3b-base | ALL_SITES | 0.411454 | [0.000, 1.386] | 195 | 0.077 |
| dom | deepseek-ai/deepseek-coder-1.3b-base | INITIALLY_WRONG | 3.26974 | [1.873, 6.261] | 106 | 0.142 |
| blk | deepseek-ai/deepseek-coder-1.3b-instruct | ALL_SITES | 0.377582 | [0.000, 1.538] | 205 | 0.098 |
| blk | deepseek-ai/deepseek-coder-1.3b-instruct | INITIALLY_WRONG | 5.90649 | [3.170, 11.994] | 109 | 0.183 |
| dom | deepseek-ai/deepseek-coder-1.3b-instruct | ALL_SITES | 0.274558 | [0.000, 1.449] | 195 | 0.082 |
| dom | deepseek-ai/deepseek-coder-1.3b-instruct | INITIALLY_WRONG | 3.62268 | [1.768, 7.124] | 104 | 0.154 |
| blk | deepseek-ai/deepseek-coder-33b-base | ALL_SITES | 0 | [0.000, 0.517] | 205 | 0.054 |
| blk | deepseek-ai/deepseek-coder-33b-base | INITIALLY_WRONG | 3.32642 | [1.880, 10.904] | 92 | 0.120 |
| dom | deepseek-ai/deepseek-coder-33b-base | ALL_SITES | 0 | [0.000, 0.801] | 195 | 0.046 |
| dom | deepseek-ai/deepseek-coder-33b-base | INITIALLY_WRONG | 1.94278 | [1.461, 3.054] | 92 | 0.098 |
| blk | deepseek-ai/deepseek-coder-33b-instruct | ALL_SITES | 0 | [0.000, 0.853] | 205 | 0.059 |
| blk | deepseek-ai/deepseek-coder-33b-instruct | INITIALLY_WRONG | 3.46877 | [1.974, 6.814] | 98 | 0.122 |
| dom | deepseek-ai/deepseek-coder-33b-instruct | ALL_SITES | 0.362685 | [0.000, 1.126] | 195 | 0.067 |
| dom | deepseek-ai/deepseek-coder-33b-instruct | INITIALLY_WRONG | 3.07736 | [1.885, 4.753] | 98 | 0.133 |
| blk | meta-llama/Llama-3.2-1B | ALL_SITES | 0.706434 | [0.000, 1.845] | 205 | 0.122 |
| blk | meta-llama/Llama-3.2-1B | INITIALLY_WRONG | 6.85507 | [2.173, 11.410] | 126 | 0.198 |
| dom | meta-llama/Llama-3.2-1B | ALL_SITES | 0.49309 | [0.000, 0.860] | 195 | 0.051 |
| dom | meta-llama/Llama-3.2-1B | INITIALLY_WRONG | 1.48731 | [0.963, 3.626] | 114 | 0.088 |
| blk | meta-llama/Llama-3.2-1B-Instruct | ALL_SITES | 0 | [0.000, 0.524] | 205 | 0.088 |
| blk | meta-llama/Llama-3.2-1B-Instruct | INITIALLY_WRONG | 3.57874 | [1.385, 13.287] | 102 | 0.176 |
| dom | meta-llama/Llama-3.2-1B-Instruct | ALL_SITES | 0.139567 | [0.000, 0.648] | 195 | 0.031 |
| dom | meta-llama/Llama-3.2-1B-Instruct | INITIALLY_WRONG | 1.57141 | [0.874, 3.017] | 102 | 0.059 |

## Artifacts

- **csv/** — 19 of 19 registered files present (tables)
- **plots/** — 24 of 24 registered files present (12 figures x PNG/SVG)
- **reports/** — 10 of 10 registered files present (Markdown reports)

Counted against the pipeline's registry (`p33/artifacts.py`) after every other artifact of this export was written; unregistered files are not counted.
