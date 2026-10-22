# Strata eval — the editor's AI-layer eval matrix

Your files for evaluating the optional AI layer of the Strata editor: the per-task ×
per-model-size × per-scaffolding eval matrix ("the gate"). They are separate from the
alien-syntax research of phases 1–4.

**History.** They were added on 2026-09-01 at the repository root, and grouped here on
2026-10-22 ([`../MOVES.md`](../MOVES.md)). No file was changed except for the link targets in
`ARCHITECTURE_NOTES.md`, which now start with `../`.

| file | what |
|---|---|
| [`ARCHITECTURE_NOTES.md`](ARCHITECTURE_NOTES.md) | a map of the editor's AI layer: how prompts become scene code, run in the browser by a small local model |
| [`evalEditMatrix.md`](evalEditMatrix.md) | the handover: how to run the eval matrix and what it decides |
| [`strata_runner.js`](strata_runner.js) | paste into the browser console on the editor page. It runs `evalEditMatrix()` and downloads a CSV |
| [`plot_matrix.py`](plot_matrix.py) | aggregates those CSVs and plots them: `python3 strata_eval/plot_matrix.py <folder of CSVs>` |

The harness itself, the function `evalEditMatrix()`, is part of the editor:
[`docs/editor/js/Shell.js`](../docs/editor/js/Shell.js).
