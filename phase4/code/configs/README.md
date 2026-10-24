# configs/ — what a run scores

A run config names its models, lexicons and grammar families, its site limits and its seeds.
`run.py dev init --config <file>` starts a run from one.

| file | what it is |
|---|---|
| [`smoke.json`](smoke.json) | **Phase 4's smoke test:** one model on one development cell (`dom` × `d50s1`). `sol/jobs/smoke.slurm` uses it |
| [`dev_api.json`](dev_api.json) | **Phase 4's first development run** (2026-10-23, exploratory): nine models served by the ASU RC API, on exactly the cells of Phase 3.3's held-out run, with its settings and seeds |
| [`smoke_api.json`](smoke_api.json) | the smoke test of the API path: one served model on one development cell |
| [`phase3_3/`](phase3_3/) | **Phase 3.3's four configs** (`dev`, `heldout`, `smoke`, `local_smoke`), kept as a record. The tests use them under Phase 3.3's design (`tests/phase3_3_design.py`). Under Phase 4's split, `heldout.json` is refused, because nothing is held out yet |
| [`voyager/`](voyager/) | made by `tools/voyager_models.py`: the ASU RC API's model list and what each model can measure. On 2026-10-22: 52 models, of which 36 serve both arms (see [`../VOYAGER.md`](../VOYAGER.md)) |

Phase 4's own development and held-out configs are written together with its preregistration
(`phase4/PREREGISTRATION.md`, §2). Every cell they name must be allowed by
`p4/governance/splits.py` for their stage, and `tests/test_prereg_env.py` checks that.
