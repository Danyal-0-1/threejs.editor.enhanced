# Re-scoring a sample of dev-20261023a's Arm A sites (2026-10-24)

300 sites of the `rule` condition per served model, drawn with seed 20261023 (`random.Random(f'{seed}/{model}')`), rebuilt by the pipeline and scored again by the same pinned deployment. Rows: `retest_2026-10-24.csv`.

| model | sites | same to the bit | median abs. change | 95th pct | max | sign changed | of those within 0.1 nat |
|---|---:|---:|---:|---:|---:|---:|---:|
| asu-rc/olmo3-7b-instruct | 300 | 150 | 0.0000 | 0.3745 | 0.8125 | 1 | 1 |
| asu-rc/olmo3-32b-instruct | 300 | 293 | 0.0000 | 0.0000 | 0.4484 | 0 | 0 |
| asu-rc/olmo3-32b-think | 300 | 299 | 0.0000 | 0.0000 | 0.0166 | 0 | 0 |
| asu-rc/qwen3-coder-30b-a3b-instruct | 300 | 300 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |
| asu-rc/gemma4-31b-it | 300 | 140 | 0.1145 | 3.7544 | 10.6886 | 14 | 0 |
| asu-rc/deepseek-v4-1-flash | 300 | 264 | 0.0000 | 0.1982 | 0.6848 | 4 | 1 |
| asu-rc/qwen35-27b | 300 | 288 | 0.0000 | 0.0000 | 0.6250 | 0 | 0 |
| asu-rc/qwen35-122b-a10b | 300 | 27 | 0.2028 | 0.7387 | 1.2445 | 20 | 7 |
| asu-rc/qwen35-397b-a17b | 300 | 300 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |
