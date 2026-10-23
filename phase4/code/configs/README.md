# configs/ — what a run scores

A run config names its models, lexicons and grammar families, its site limits and its seeds.
`run.py dev init --config <file>` starts a run from one.

| file | what it is |
|---|---|
| [`smoke.json`](smoke.json) | **Phase 4's smoke test:** one model on one development cell (`dom` × `d50s1`). `sol/jobs/smoke.slurm` uses it |
| [`phase3_3/`](phase3_3/) | **Phase 3.3's four configs** (`dev`, `heldout`, `smoke`, `local_smoke`), kept as a record. The tests use them under Phase 3.3's design (`tests/phase3_3_design.py`). Under Phase 4's split, `heldout.json` is refused, because nothing is held out yet |
| `voyager/` | made by `tools/voyager_models.py`: the ASU RC API's model list and probe tables (see `../VOYAGER.md`) |

Phase 4's own development and held-out configs are written together with its preregistration
(`phase4/PREREGISTRATION.md`, §2). Every cell they name must be allowed by
`p4/governance/splits.py` for their stage, and `tests/test_prereg_env.py` checks that.
