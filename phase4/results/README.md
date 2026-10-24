# Phase 4 results

Phase 4's results root (`P4_RESULTS_ROOT`). These runs were made on the laptop: the models are
served by the ASU RC LLM API, so they need the network, not a GPU.

| folder | what | status |
|---|---|---|
| `smoke-20261023a/` | the smoke test of the API path: OLMo 3 7B Instruct on `dom` × `d50s1`, 12 Arm A and 6 ladder sites | COMPLETE |
| `dev-20261023a/` | **Phase 4's first development run (exploratory):** nine served models on exactly the cells of Phase 3.3's held-out run (both grammars × its five held-out lexicons, every site) | COMPLETE: 1,998 of 1,998 cells; `validate` VALID; figures and a re-scored sample in `analysis_addenda/` |
| `model_pins.json` | the deployment that answered for each served model (`<served name>@<system_fingerprint>`), at the start of the run | |
| `restore_large_files.sh` | restores the files stored gzipped (below) | |

**Read first:** [`explanations/phase4/api_models_results_explained/00_complete_results.md`](../../explanations/phase4/api_models_results_explained/00_complete_results.md).
The figures and their tables are in `dev-20261023a/analysis_addenda/paper_figures/`
(open `CAPTIONS.md` there first).

**What is never here:** the API key (it stays in `~/.config/asu-rc/llm_api_key`), weights, or
tokens.

## Files stored gzipped

One file is over GitHub's 100 MB limit. It is committed gzipped (`gzip -9 -n`), with the SHA-256
of both forms in the run's `LARGE_FILES.sha256`, and the original is ignored by git (the run's
`.gitignore`), as Phase 3.3 does:

| file | size | stored as |
|---|---:|---|
| `dev-20261023a/merged/arm_a.jsonl` | 105.9 MiB | `arm_a.jsonl.gz`, 5.7 MiB |

Restore and check it: `bash phase4/results/restore_large_files.sh dev-20261023a`. The figure
script reads `csv/arm_a_long.csv` (43.6 MiB, the same 81,810 rows), so only a re-export or a
re-test needs the restored file.
