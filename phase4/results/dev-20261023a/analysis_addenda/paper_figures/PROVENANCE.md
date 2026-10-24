# Provenance (dev-20261023a)

- made: 2026-10-24T02:21:17+00:00
- script: `phase4/code/tools/paper_figures_api.py` (sha256 6e5cdaef46e83407…)
- Phase 4 run: `/home/mesquite/Desktop/projects/Lab/threejs.editor/threejs.editor.enhanced/phase4/results/dev-20261023a`; config hash c786cd79962f
- Phase 3.3 run: `/home/mesquite/Desktop/projects/Lab/threejs.editor/threejs.editor.enhanced/phase3_3/sol_results/heldout-20261007a` (instruct models only)
- bootstrap: B = 2000, seed 20261002, template clusters, Phase 3.3's streams (`<grammar>/reversion/instruct`, `<grammar>/figure/arm_b`)

## Checks (each one refuses on a mismatch)

- both runs scored the same 1515 dom and 1515 blk sites, on 80 and 80 templates and the lexicons d25s3, d50s3, d75s1a, d75s2a, d75s3a
- Phase 3.3: the per-lexicon mean rule effect equals the export in all 200 model x grammar x lexicon x control cells, and the reversion counts and rates in all 400 model x grammar x lexicon x role cells
- Phase 4: the per-lexicon mean rule effect equals the export in all 180 model x grammar x lexicon x control cells, and the reversion counts and rates in all 360 model x grammar x lexicon x role cells
- Kaplan-Meier medians recomputed from the site rows equal each run's export in all 38 model x grammar groups
- Arm B site, reach, reversion, correct-program and parse-failure counts equal each run's hurdle table for all 38 model x grammar groups
- every one of the 2700 re-scored sites' 'run' margins is the run's exported margin

## Inputs (sha256)

- Phase 3.3: csv/arm_a_long.csv: `2d1ef380b2384dee5076441ecf712093ceed08064dd5e4df0b54269d694f56f2`
- Phase 3.3: csv/arm_b_generations.csv: `ad697518d561db0651fd709517d38f422de1e7efda5accd0d44d42bb37ac01ec`
- Phase 3.3: csv/arm_b_hurdle.csv: `f4848325cf551c9a845960b9733a5476226feac373b75f9b63c219b4182d7a51`
- Phase 3.3: csv/extinction_rung_long.csv: `b45135cd3e66618c0946019eb3a02d1df3956379b67a809f92278040641f2745`
- Phase 3.3: csv/kstar_survival.csv: `f40d35775c8779adadd77757eeb4b598116d92c577739137980656dd3f63fe0d`
- Phase 3.3: csv/rule_effect.csv: `76311f8e45875bf0c414aafd365e6e79cfcce8d2fcc8b70b7e9e9e53f668c9d1`
- Phase 4: analysis_addenda/retest/retest_2026-10-24.csv: `40282406944adc4c8c41aeea3f433cf1452cb58fb21c16a44d8bcf6c70cace34`
- Phase 4: csv/arm_a_long.csv: `cd48f20f76b2f56dc002f4096b97f334613f9654fd18c55153ad0dc2e068ff7e`
- Phase 4: csv/arm_b_generations.csv: `6908ff62592464760bc0360e216d38fd181cde130a5a8c77cc06d974845559c6`
- Phase 4: csv/arm_b_hurdle.csv: `e28219ec27ee84d880dcd903200316f6ccc75153b4d8a0ba5c32c5fa08ce236a`
- Phase 4: csv/extinction_rung_long.csv: `73ff942898206b8f9250c8d7a09639628df5bbe7b9cc8f95e719a31fda4de7c7`
- Phase 4: csv/kstar_survival.csv: `68bb4e863da5d353d0c7e5fa0c76d6b99a9eaaa95d044a86378d72f9bc623db3`
- Phase 4: csv/rule_effect.csv: `88aa3bfd7daeff5dab9b4c6d51e6c50889927cf89c42e685cf6b17e3706178df`
