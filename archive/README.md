# Archive

Material that is superseded or repeated, kept so that nothing is lost.

- **Nothing here is needed** to run the experiment or to continue it.
- **Moved on 2026-10-22** with `git mv`, so `git log --follow <file>` shows each file's history.
- **File names are unchanged.**
- **The text is as it was:** these documents describe things as they stood at the time.
- **Their links were updated** so that they still resolve.
- **Old and new paths:** [`../MOVES.md`](../MOVES.md).

| folder | what it is | why it is archived | came from |
|---|---|---|---|
| [`phase3_3_first_laptop_run/`](phase3_3_first_laptop_run/README.md) | the first Phase 3.3 run, made on the laptop before the Sol pipeline existed: its index, reports 00–05, its errata, and the data snapshot it used | see below | `phase3_3/` |
| [`phase3_2_sol/legacy_superseded/`](phase3_2_sol/legacy_superseded/WHY_SUPERSEDED.md) | the first Sol scripts: `arm_a.slurm`, `primary.slurm`, `prefetch_models.py` | they would not have run on Sol (erratum E4): Sol rejects `--partition=general`, and the prefetcher instantiated every model. They were replaced by `phase3_2/sol/jobs/` and `p33/prefetch.py` | `phase3_2/sol/legacy_superseded/` |
| [`phase3_2_sol/local_smoke/`](phase3_2_sol/local_smoke/) | the one real-model smoke run on the laptop, 2026-10-05: Qwen2.5-Coder-0.5B, 12 sites | a pre-Sol check of the pipeline ([`AUDIT.md`](../phase3_2/sol/AUDIT.md) §5), superseded by the smoke and development runs on Sol | `phase3_2/sol/local_smoke/` |

**Why the first laptop run is archived:**

- **Its claims were withdrawn or corrected on 2026-10-05** ([`ERRATA.md`](phase3_3_first_laptop_run/ERRATA.md)):
  - E1: the headline "`k*` ≈ 5–7" was contaminated by leaked demonstrations;
  - E2: its rule-effect intervals were too narrow;
  - E3: `blk` had been inspected, so it is not a held-out grammar;
  - E4: its Sol scripts would not have run.
- **The Sol study replaced it.**
- **`outputs_snapshot/` is repetition:** five of its six files are byte-identical copies of files
  in `phase3_2/outputs/`.

**Two things stay elsewhere:**

- **The local smoke run's config** stays at `phase3_2/sol/configs/local_smoke.json`, because the
  tests use it.
- **The old paths of archived files remain in a few records that are not edited.** For example:
  - the docstring of `phase3_2/sol/src/p33/prefetch.py` (frozen code) mentions
    `legacy_superseded/prefetch_models.py`;
  - [`PROMPT_REVIEW.md`](../phase3_2/sol/PROMPT_REVIEW.md) names `phase3_3/ERRATA.md`.

  [`../MOVES.md`](../MOVES.md) lists every such mention.

**Removed from git tracking, not archived:** 49 compiled Python caches (`*.pyc`). They are still
on disk, Python rebuilds them, and `.gitignore` now ignores them. The list is in
[`../MOVES.md`](../MOVES.md).
