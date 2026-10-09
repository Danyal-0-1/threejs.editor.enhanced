# Provenance of the paper figures — `heldout-20261007a`

- generated 2026-10-09T22:48:42+00:00 by `phase3_2/sol/scripts/paper_figures.py` (sha256 `d953759997544b00…`), outside the frozen source set
- frozen analysis: `dev-20261006a/DEV_FREEZE.json`, sha256 `b319c3fcba3dd325…`; held-out unlocked 2026-10-08T06:05:31+00:00
- figure intervals: template-cluster bootstrap, B = 2000, seed 20261002, drawn as `scale_analysis.py` draws them (streams `<grammar>/reversion/<kind>`, `<grammar>/h4_auroc/pair`, `<grammar>/figure/arm_b`)
- grammar families are never pooled; `blk` is a weak family test (deviation D1)
- the frozen diagnostic plots in `plots/` are unchanged

## Checks against the frozen export (all passed)

- development freeze `dev-20261006a/DEV_FREEZE.json` matches the unlock (sha256 b319c3fcba3dd325…)
- the per-lexicon mean rule effect equals the frozen export in all 420 model x grammar x lexicon x control cells
- site counts and reversion rates with the table equal the frozen export in all 840 model x grammar x lexicon x role cells
- AUROC of the risk score and of the role-level and length baselines equals the frozen export in all 20 pair x grammar groups
- the 36 Qwen2.5-Coder ladder values and their 95% intervals equal the D11 output exactly
- Kaplan-Meier medians recomputed from the site rows equal the frozen export in all 42 model x grammar groups
- Arm B site, reach, reversion, correct-program and parse-failure counts equal the frozen hurdle table for all 20 model x grammar groups and every role
- calibrated_p equals the frozen Platt fit for the 2 development pairs

## Checkpoints and the revisions scored

| model | revision |
|---|---|
| Qwen/Qwen2.5-Coder-0.5B | `8123ea2e9354afb7ffcc6c8641d1b2f5ecf18301` |
| Qwen/Qwen2.5-Coder-0.5B-Instruct | `ea3f2471cf1b1f0db85067f1ef93848e38e88c25` |
| Qwen/Qwen2.5-Coder-1.5B | `df3ce67c0e24480f20468b6ef2894622d69eb73b` |
| Qwen/Qwen2.5-Coder-1.5B-Instruct | `2e1fd397ee46e1388853d2af2c993145b0f1098a` |
| Qwen/Qwen2.5-Coder-3B | `09d9bc5d376b0cfa0100a0694ea7de7232525803` |
| Qwen/Qwen2.5-Coder-3B-Instruct | `488639f1ff808d1d3d0ba301aef8c11461451ec5` |
| Qwen/Qwen2.5-Coder-7B | `0396a76181e127dfc13e5c5ec48a8cee09938b02` |
| Qwen/Qwen2.5-Coder-7B-Instruct | `c03e6d358207e414f1eca0bb1891e29f1db0e242` |
| Qwen/Qwen2.5-Coder-14B | `f2ad5164aade432d6d56c24bb71589184d5d613d` |
| Qwen/Qwen2.5-Coder-14B-Instruct | `aedcc2d42b622764e023cf882b6652e646b95671` |
| Qwen/Qwen2.5-Coder-32B | `2e12b5f7bc878d424d222e224ed40aee564ec45f` |
| Qwen/Qwen2.5-Coder-32B-Instruct | `381fc969f78efac66bc87ff7ddeadb7e73c218a7` |
| Qwen/Qwen2.5-72B | `efba10c8e54e91e0d9570ab5f7b51a958474d4cb` |
| Qwen/Qwen2.5-72B-Instruct | `495f39366efef23836d0cfae4fbe635880d2be31` |
| deepseek-ai/deepseek-coder-1.3b-base | `c919139c3a9b4070729c8b2cca4847ab29ca8d94` |
| deepseek-ai/deepseek-coder-1.3b-instruct | `e063262dac8366fc1f28a4da0ff3c50ea66259ca` |
| deepseek-ai/deepseek-coder-33b-base | `45c85cadf3720ef3e85a492e24fd4b8c5d21d8ac` |
| deepseek-ai/deepseek-coder-33b-instruct | `61dc97b922b13995e7f83b7c8397701dbf9cfd4c` |
| meta-llama/Llama-3.2-1B | `4e20de362430cd3b72f300e6b0f18e50e7166e08` |
| meta-llama/Llama-3.2-1B-Instruct | `9213176726f574b556790deb65791e0c5aa438b6` |
| bigcode/starcoder2-3b | `733247c55e3f73af49ce8e9c7949bf14af205928` |

## Inputs (sha256)

| file | sha256 |
|---|---|
| `csv/arm_a_long.csv` | `2d1ef380b2384dee…` |
| `csv/h4_predictions.csv` | `acbd8d0c6b207ffc…` |
| `csv/h4_metrics_baselines_calibration.csv` | `5c3b0c8cf7af8302…` |
| `csv/kstar_survival.csv` | `f40d35775c8779ad…` |
| `csv/arm_b_generations.csv` | `ad697518d561db06…` |
| `csv/arm_b_hurdle.csv` | `f4848325cf551c9a…` |
| `csv/h5_budget_outcomes.csv` | `c0fc7031697d60f4…` |
| `csv/paraphrase.csv` | `fc81dd99a003c2ea…` |
| `csv/rule_effect.csv` | `76311f8e45875bf0…` |
| `csv/fertility.csv` | `a0f56d6d2539ea95…` |
| `analysis_addenda/d11_scale/scale_analysis.csv` | `60b5aab4f9cd8f5f…` |
