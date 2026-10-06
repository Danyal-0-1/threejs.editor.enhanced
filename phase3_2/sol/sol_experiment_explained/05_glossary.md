# 05 — Glossary (Sol pipeline additions)

> Terms already defined in
> [`phase3/phase3_explained/05`](../../../phase3/phase3_explained/05_glossary.md)
> and [`phase3_2/phase3_2_explained/05`](../../phase3_2_explained/05_glossary.md)
> are not repeated. Those include site, collision class, reversion, φ-map,
> grammar family, delta family, stratum, M_seq, `k_common` and `merged`.
> Each entry here is: **term**: definition. *Example or where it lives.*

---

## Split and governance

**Registered split**: the preregistered partition into development and
held-out cells, enforced by `splits.classify` before anything is enumerated.
*Development: `dom × {d25s1, d25s2, d50s1, d50s2} ×` Qwen 0.5B/1.5B base and instruct.*

**Cell class / split label**: the class a (family, lexicon, model) belongs to,
copied onto every row: DEVELOPMENT, HELDOUT, HELDOUT-WEAKENED,
HELDOUT-WEAK-FAMILY, EXPLORATORY or FORBIDDEN.

**HELDOUT-WEAKENED**: a held-out model that was observed before the freeze
under a superseded protocol. *Qwen2.5-Coder-3B (deviation D2).*

**HELDOUT-WEAK-FAMILY**: `blk` with a never-scored mapping. The grammar has
been seen; the mapping has not. A weaker test, never a held-out-grammar test (D1).

**EXPLORATORY-CONTAMINATED**: `blk` with a development lexicon, which was already inspected.
Refused unless `allow_exploratory` is set, and labelled if allowed.

**FORBIDDEN**: an unregistered family or lexicon, or any model above 3B.

**Freeze (`DEV_FREEZE.json`)**: the immutable record of the development
analysis. It is written once, mode 444, with a `.sha256` sidecar.

**Unlock (`HELDOUT_UNLOCK.json`)**: your explicit, typed permission to touch held-out
cells for one run. It requires the phrase *"I have finished the development
analysis and will not change it"*.

**Drift**: any source file, materials file or frozen model pin that differs
from the freeze. Checked at unlock and again on every held-out access
(`splits.frozen_drift`).

**Deviation**: a dated, append-only entry under `## Deviations` in
`PREREGISTRATION.md`. D1–D8 were written on 2026-10-05. The text above that
heading is byte-frozen (sha256 `a0146494…`).

**NOT TESTABLE / NOT RUN / NOT ESTIMABLE**: three different statements, never
placeholders:

| Statement | Meaning | Example |
|---|---|---|
| NOT TESTABLE | the design cannot test it | H2, H4 C3 |
| NOT RUN | the data does not exist yet | — |
| NOT ESTIMABLE | the data exists but the statistic is undefined | AUROC when there is a single class |

## Measurement

**Canonical scorer**: `TokenScorer.score_pair_detailed`, the one
first-divergent-token scorer used by Arm A, the primary experiment, H4 and H5.

**Refusal**: the scorer raises instead of inventing a number:
`IdenticalCandidates`, `ZeroLengthSpan` or `NoContext`. A refused site becomes a
row with `status` and `exclusion_reason`, never a margin of 0.0.

**fp32 output head**: the final vocabulary projection recomputed in fp32 from
the bf16 decoder's last hidden state. *`fp32_head = true` on every row.*

**Tie**: `M_seq == 0` exactly. Counted in QC; 0 in the smoke.

**`norule_lenmatched`**: the no-rule prompt padded with neutral filler to the
rule prompt's token count, under each model's own tokenizer. *298 vs 307 tokens.*

**Prompt bundle**: (condition, lexicon, text) with a sha256. *The rule prompt for
`d50s1` is `9668e9c3…`.*

**Program NLL per char**: the base model's negative log-likelihood of the whole
rendered program, per character. An H4 baseline.

## Extinction and survival

**Ladder**: the shot counts 0, 1, 2, 4, 8, 16, 32 (0–8 in the smoke). **Rung**: one of them.

**Nested ladder**: the k-shot demonstration set is a prefix of the
(k+1)-shot set, so only the dose varies along a curve.

**Leak**: a demonstration from the same template, the identical program, or
one that replays the site's decision prefix beyond the family's fixed opening.

**Fixed opening**: the prefix every program in a pool shares. *`(function(){ $S('`
for `dom`.* Sharing it is not a leak.

**`k*`**: the first upward zero-crossing of the margin, interpolated
between rungs. It is 0 if the site is already correct, and **censored** if no crossing
happens by the top rung.

**Already correct**: `M(0) ≥ 0`, which gives `k* = 0`.

**Censored**: no crossing within the ladder. All we know is "more than 32".

**Re-crossed down**: the margin crossed zero and later fell below it again.
Such a curve is *not* censored.

**`sustained_k`**: the first rung after which the margin never returns below zero.

**Non-monotone**: the margin decreases somewhere along the ladder. *5 of 6 smoke
curves; 237 of 240 in the Phase 3.3 audit.*

**Kaplan–Meier (KM)**: the product-limit estimate of the share of sites not
yet crossed, as a function of shots. It handles censoring.

**ALL_SITES / INITIALLY_WRONG**: the two labelled KM populations. *Smoke
medians: 0 and 6.79.*

**Median among crossers**: a diagnostic that drops censored sites and is biased low.
Never the headline. *4.25 in the smoke.*

## Statistics

**Template cluster**: all sites from one abstract program, across lexicons. The
resampling unit.

**`_draw` tag**: the index marking each copy of a resampled cluster, so a
twice-drawn template counts twice.

**Multiplicity (bootstrap)**: how many times a cluster appears in a resample.
Losing it was defect P33-005. *5/3 vs 2.0.*

**Minimum clusters**: 8. Below that no interval is reported:
`NO INTERVAL (<8 template clusters)`.

**Holm correction**: a step-down multiple-testing adjustment, applied over H4's C1 and C2.

**Design effect (DE)**: `1 + (m − 1)·ICC`, the variance inflation from clustering.

**ICC**: intra-class correlation, the share of variance that sits between templates.

**Hanley–McNeil variance**: a closed-form variance of an AUROC.

**Platt calibration**: `p = σ(a + b·risk)`, fitted on development and frozen.

**Youden threshold**: the probability cut that maximises TPR − FPR on development, then frozen.

**ECE**: expected calibration error over 10 equal-width bins.

**Identity baseline**: 1 if correct ≠ competitor. It is constant on SEMANTIC sites,
so its AUROC is exactly 0.5 (D6).

**`terminal_rate`**: an exploratory H4 baseline. The instruct model's reversion
rate for the same terminal in *other* templates, cross-fitted
leave-one-template-out.

## Hypotheses and arms

**Risk score (H4)**: `−M_seq(base model, rule condition)`. **Label**: `1` if
`M_seq(instruct, rule) < 0`.

**C1 / C2 / C3**: H4's frozen criteria.

- **C1:** ΔAUROC vs identity ≥ 0.10.
- **C2:** ΔAUROC vs length ≥ 0.05.
- **C3:** AUROC ≥ 0.65 on a valid held-out grammar. NOT TESTABLE.

**Repair arm (H5)**: a set of remapped roles whose spellings are replaced from
the `beta` lexicon:

- **targeted:** the top 3 roles by base-model risk;
- **random:** 3 roles per seed, seeds 1–5;
- **global:** all remapped roles.

**IR proof**: re-parsing all 142 programs × 2 families = 284 renderings
under a repaired lexicon. All must keep their canonical IR.

**Benefit per symbol**: `(reversions before − after) / roles changed`.
**Control degradation**: the change in the reversion rate on unchanged roles. Must be ≤ 0.02.

**Hurdle (Arm B)**: generation first has to **reach** the site (the prefix matches),
and only then can it revert. `P(reach)` and `P(revert | reach)` are reported
separately.

**Five buckets (Arm B)**: LEX_FAIL, PARSE_FAIL, VALID_VACUOUS, VALID_WRONG,
VALID_CORRECT.

## Engineering

**Cell**: one unit of work. Its key is
`<experiment>_<family>_<lexicon>_<condition>_<chunk>__<16-hex hash of all its fields>`.

**Shard**: a cell's rows, `raw/shards/<exp>/<key>.jsonl`.

**Done marker**: `checkpoints/<exp>/<key>.done.json`, holding the shard's sha256 and row count.

**Cell state**: done / failed / corrupt / missing. *Corrupt means the shard and marker
disagree, or a marker exists with no shard.*

**Quarantine**: moving a corrupt cell aside so it is redone cleanly.

**Atomic write**: `atomic_write_text`. Write a unique `mkstemp` file in the target
directory, fsync it, then `os.replace` it over the target.

**Merge**: verify every shard, drop identical duplicates, refuse conflicting
ones, sort deterministically. Gives COMPLETE / PARTIAL / EMPTY.

**Resume**: resubmit the same command. Done cells are skipped.

**Config hash**: the sha256 of a run's configuration, excluding `run_id` and
`note`. A different hash under the same run id is refused.

**Source hashes**: sha256 of 43 files: the 24 `p33` modules plus the CLI, 11
`phase3_2/src` modules, and 7 `phase3/src` modules.

**Materials hashes**: sha256 of the lexicon files, the terminal table, the
canonical templates and the `blk` grammar.

**Job manifest**: `manifests/job_*.json`, one job's full identity and its status
(RUNNING → COMPLETE / PARTIAL / FAILED / INTERRUPTED).

**Model pin**: `results/model_pins.json`, holding each model's exact Hub revision,
`allow_patterns` and tokenizer fingerprint. Re-running prefetch keeps an existing
pin; only `--repin` moves a model to the Hub's current commit (never after a freeze).

**Started (experiment)**: an experiment whose shard directory exists, which
happens once a run of it begins. `validate` checks only started experiments;
`status` is read-only and reports the rest as `not started`.

**Tokenizer fingerprint**: a hash identifying a tokenizer. *`cc349caf59f0697a`
for Qwen2.5-Coder-0.5B.*

**Fake scorer**: `p33/fakes.py`, a deterministic CPU stand-in used by the tests and
the rehearsal. It is only active with `P33_FAKE=1`, which `sol.env` unsets.

**Exit codes**: 0 complete · 1 error · 2 refusal · 3 partial · 4 interrupted.
The test runner uses 0 all passed · 1 a failure · 5 only blocked.

**BLOCKED (test)**: a test that could not run for want of a dependency or a
device. Never counted as passed.

## Sol and Slurm

**Account / partition / QOS**: who is charged and which queue is used.
*`grp_tlingego` / `public` / `public`. `general` is rejected for public jobs.*

**GRES / constraint**: the generic resource request and the node feature filter.
*`gpu:a100:1` / `a100_80`.*

**Job array**: one submission with N tasks. Task *i* gets `SLURM_ARRAY_TASK_ID = i`
and scores model *i* of the run's config.

**`--signal=USR1@300`**: Slurm sends SIGUSR1 300 s before the time limit. The
pipeline finishes its current site, discards the unfinished cell (it is redone on
resume), records INTERRUPTED and exits 4.

**`srun`**: launches the job step on the allocated resources.

**Overlay environment**: a venv created with `--system-site-packages` on top of Sol's
shared PyTorch env. Torch comes from the shared env; pinned dependencies come from ours.

**Data-transfer node**: a node with network access for downloads, used for
prefetch if the compute nodes are offline. Not verified from here.

**`HF_HOME`, `HF_HUB_CACHE`**: the Hugging Face root and the cache under it
(`$SCRATCH/hf`, `$SCRATCH/hf/hub`). `TRANSFORMERS_CACHE` is ignored by
transformers 5.x.

**`allow_patterns`**: the file patterns a snapshot was downloaded with. The same
patterns are needed to resolve the snapshot offline.
