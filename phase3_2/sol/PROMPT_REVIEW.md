# PROMPT_REVIEW.md — what in the brief was accepted, corrected, ignored, repeated, or missing

You asked for the brief to be checked before it was executed: implement what
is accurate, ignore what is not, and explain the difference here. Every
verdict below has evidence; the evidence is in [`AUDIT.md`](AUDIT.md).

---

## 1. Accurate, implemented as written

Every one of the ten stop-ship defects was **verified true** before it was
fixed (AUDIT §2). The following were implemented as specified:

- per-site lexicon resolution with an agreement assertion and a two-lexicon regression test;
- leakage-free demonstrations with recorded ids, order and hash;
- the exact `k*` definition (`M(0) ≥ 0 ⇒ 0`; first upward crossing, interpolated; no crossing ⇒ censored; crossed-then-dropped not censored; every rung kept; crossing counts; non-monotonicity flag; KM summaries; median-among-crossers as a labelled diagnostic);
- template-cluster bootstrap with multiplicity preserved, B = 2000, seed 20261002, no interval below 8 clusters, families never pooled, Holm;
- tokenizer-specific fertility with all the requested fields;
- one canonical first-divergent-token scorer for Arm A, H4 and H5, with no silent zero;
- provenance bound to every runner and shard, with every field in the list;
- atomic JSONL shards, idempotent resume, failure/OOM/timeout records, duplicate and corrupt detection, deterministic merge, completeness validation, incompatible-configuration rejection, PARTIAL labelling;
- the registered split in code, an immutable `DEV_FREEZE.json`, a separate unlock, physically separate commands and output roots, and tests proving accidental access is refused;
- `blk` NOT presented as a held-out grammar; family-level confirmation marked NOT TESTABLE; the weaker `blk × never-scored mapping` alternative recorded as deviation D1; no family invented;
- the Sol facts as the documented, overridable defaults (account, `public`/`public`, `gpu:a100:1`, `a100_80`), safe activation under `set -u`, a separate project environment, the requested directory layout, a submit wrapper that creates log directories first, eleven separate jobs using `srun` and arrays, offline scoring, GPU preflight with every listed check;
- a download-only prefetcher with exact revisions, tiers, `--dry-run`, retries, space estimate, checksum verification, a model manifest, a failure list and pairing validation;
- one model per process, released between models;
- Arm A, primary, H4 (all metrics, all baselines, frozen criteria), Arm B (fixed decoding, all text saved, five outcomes, hurdle never collapsed), H5 (three arms, deterministic seeds, per-symbol reduction, ≤ 0.02 control tolerance, exhaustive IR proof), H2 (NOT TESTABLE with the machinery ready), power (clustered, development-only);
- all 19 CSVs, all 12 plot groups (PNG + SVG, from tables only), all 10 reports, with the required metadata and `NOT RUN` / `NOT TESTABLE` where data do not exist;
- every requested regression test, a fake-model end-to-end test, and the interrupted-vs-uninterrupted equality test;
- one development smoke; no full or held-out submission.

---

## 2. Accurate in intent, CORRECTED in detail

| the brief said | the problem | what was done instead |
|---|---|---|
| "Validate every expected family × lexicon × stratum cell" | A full grid would fail forever on `dom/d25s2/sigil`, which is **structurally empty** (seed 2 never remaps a sigil). | Expected cells are derived from the classified materials; empty grid cells are reported as STRUCTURALLY_EMPTY, and a sample is refused only if it misses a cell the materials actually offer. |
| "define the unit of de-duplication explicitly" | The obvious unit (a prefix, globally) is wrong: sites in different lexicons with identical program prefixes are DIFFERENT stimuli, because the rule table differs. | Unit = (family, lexicon) cell, with a canonical tie-break; every drop is logged with the site it duplicates (deviation D5). |
| "Exclude … equivalent prefix from demonstrations" | Read literally, this rejects EVERY `dom` demonstration: they all begin `(function(){ $S('`, which is exactly a first site's prefix. | A prefix counts as replaying the decision only if it is longer than the family's fixed common opening. Verified: 0 leaks and every site can fill all 32 rungs, in both families. |
| "Use `$SCRATCH/hf` for HF_HOME, HF_HUB_CACHE, TRANSFORMERS_CACHE" | Setting all three to the same path breaks the standard cache layout (`$HF_HOME/hub/models--…`) and the offline resolver. | `HF_HOME=$SCRATCH/hf`, `HF_HUB_CACHE=$SCRATCH/hf/hub`, `TRANSFORMERS_CACHE=$SCRATCH/hf/hub`. |
| "`TRANSFORMERS_CACHE`" | **It does nothing in transformers 5.x** — zero references in the installed 5.16.1. | Still exported, for older transformers only, and documented as inert. `HF_HUB_CACHE` is the variable that matters. |
| "Scoring must use `local_files_only=True`" | Necessary but not sufficient: huggingface_hub 1.x rejects a transformers-populated cache as an "incomplete snapshot" unless the SAME `allow_patterns` are given. | Prefetch chooses patterns per model (safetensors, else `.bin`), stores them in the pins, and every offline resolution reuses them. |
| "Use survival/Kaplan–Meier summaries" + "`k*=0` when already correct" | Correct, but with ~half the sites already correct the ALL-SITES KM median is often 0 — true, and easily misread as a bug. | Two labelled populations: ALL_SITES and INITIALLY_WRONG (the actionable number). |
| H4 criterion "ΔAUROC vs identity ≥ 0.10" | The identity baseline is **constant** on the preregistered SEMANTIC-only eligible set, so its AUROC is exactly 0.5 and C1 is really "AUROC ≥ 0.60". | Kept as frozen (it is preregistered), the reduction stated in every report (D6), and a stronger EXPLORATORY `terminal_rate` baseline added. |
| "AUROC ≥ 0.65 on a valid held-out grammar" | No valid held-out grammar exists. | C3 is emitted as NOT TESTABLE with its reason, in every criteria table. |
| "do not scale beyond 3B until the required grammar evidence exists" | That evidence cannot exist yet. | Implemented as "no model above 3B in any stage". |
| "statsmodels or the chosen statistical package" | Not installed anywhere locally, and not needed. | Chosen package: numpy + stdlib, every method implemented and tested against hand values; statsmodels not required (pandas/scipy listed as optional extras for interactive work). |
| "Parquet" | Optional ("JSONL/Parquet/CSV"); no pyarrow in the environment. | JSONL shards (append-safe, stdlib) and CSV exports. |
| "Prefetch on an appropriate allocated or transfer resource" | Sol's network topology (whether compute nodes reach the Hub) could not be verified from here. | A CPU prefetch job is provided; the README says to run the identical command on the data-transfer node if compute nodes are offline. |

---

## 3. Not implemented, or not done here — and why

| item | why |
|---|---|
| Running anything on Sol | This environment has no access to Sol. Every Sol fact in the brief (partition, QOS, constraint, env versions, "14 passed / 22 failed") is **user-reported** and used as documented defaults; none was independently verified. |
| "Permit exactly one development smoke" on an A100 | Done on the laptop RTX 3080 Ti instead, with the A100 check explicitly waived and recorded in the run's DEVIATIONS report. |
| A real Sol dependency lock | A lock is a resolution on a specific machine. `make_env.sh` writes `requirements.lock.sol.txt` the first time it runs on Sol; the shipped `requirements.lock.laptop.txt` is the verified local resolution, labelled as such. |
| A new grammar family | Explicitly forbidden by the brief without approval. `APPROVED_NEW_FAMILIES` is empty. |
| H2 analysis | No T/A calibration exists; deriving it from outcome margins would be circular. NOT TESTABLE. |
| Verifying model repo ids exist | Needs the Hub; `prefetch --dry-run` on Sol lists any that fail to resolve. |
| Seaborn | Not used; matplotlib only. |

Nothing in the brief was ignored for being *wrong in substance*. Everything
above is either a correction of detail (§2) or something that could not be
done from this machine (§3).

---

## 4. Things the brief repeated (implemented once, referenced everywhere)

| repeated instruction | appears in | implemented once in |
|---|---|---|
| never pool grammar families | bootstrap item, H4 item | `analysis` callers + `export` grouping |
| offline / pinned / `local_files_only` | Sol section, prefetch, preflight, jobs | `scorers.resolve_snapshot` + `HF_HUB_OFFLINE` in every scoring job |
| record resolved versions, never trust env names | Sol facts, provenance, preflight | `provenance.package_versions` / `gpu_info` |
| `NOT RUN` / `NOT TESTABLE`, never placeholders | H2, artifacts, reports | `export.write_csv(not_run=…)`, `reports` banners |
| revision / tokenizer / prompt hashes | provenance list, every-aggregate list, Arm A list | row fields + `export.meta` |
| development vs held-out separation | split item, freeze item, command list, final handoff | `splits` + CLI stage groups + run-id prefix |

---

## 5. Things the brief MISSED — added

| addition | why it matters |
|---|---|
| **fp32 output head** (P33-002, D7) | bf16 logits are quantised: the smoke's native margins `+0.6250` and `−4.4375` are multiples of 1/16 nat. The outcome is a margin's SIGN, so near-zero margins would be signed by rounding. Validated against native logits on three development sites: per-candidate log-probabilities within 0.005–0.042 nats, same margin sign every time. |
| **one-sided zero-length span** (P33-001) | The first P32-001 fix still returned 0.0 for one side in a rarer case. Now `ZeroLengthSpan`. |
| **length-matched no-rule control** | `norule` is a third shorter than `rule` (1,014 vs 1,527 characters; 237 vs 298 tokens), so a measured rule effect *could* be partly a context-length effect. `norule_lenmatched` pads to the rule prompt's token count per tokenizer (smoke: 307 vs 298 tokens). |
| **237/240 curves non-monotone** | First-crossing `k*` is noise-sensitive. Added a non-monotonicity flag, crossing counts and a "sustained" crossing per curve. |
| **Qwen2.5-Coder-3B already observed** | Recorded as D2; 3B labelled HELDOUT-WEAKENED. |
| **pre-freeze rule-effect intervals** | Recomputed with the fixed bootstrap: all four now include zero. Phase 3.3 ERRATA E2. |
| **Phase 3.3 headline withdrawn** | `k* ≈ 5–7` was contaminated by leakage; `phase3_3/ERRATA.md` + banners. |
| **`terminal_rate` baseline** (exploratory) | The preregistered identity baseline is degenerate. This one is the real "language detector" competitor: the instruct model's reversion rate for the same terminal in other templates, cross-fitted leave-one-template-out. |
| **legacy runners as guarded wrappers** | Otherwise `run_arm_a.py` / `run_primary.py` stay a second, unguarded route to held-out cells. They now delegate to `p33` and refuse held-out/contaminated cells. |
| **`HFModel.sequence_logprob` made loud** | Closes the last route to a silent 0.0 anywhere in the repository. |
| **BLOCKED test status** | A missing dependency is reported separately and makes the runner exit non-zero — exactly the Sol failure mode (missing `lark`) the brief described. |
| **scorer revision check at load time** | A model whose loaded snapshot differs from its pin is refused before scoring. |
| **plan artifacts are idempotent and verified** | A resumed run whose materials changed underneath it is refused. |

### Added in the final verification pass

These were found by rehearsing the runbook end to end with the fake scorer,
after the code was otherwise complete. Details, evidence and tests are in
`sol_experiment_explained/08 §1`.

| Addition | Why it matters |
|---|---|
| **P33-011** idempotent, atomic materials writer | The Phase 3.2 tests rewrote 9 tracked lexicons on every run. Rerunning `cpu_tests` on Sol mid-run would have failed every later GPU job's materials check. |
| **P33-012** array task *i* → model *i*; `P33_ARRAY` | Resubmitting one failed index silently scored nothing (`i % 1 == 2`). |
| **P33-013** runner exit codes 0/1/5 and `--cpu-node` | On a Sol CPU node the blocked A100 test made `set -e` stop the job after the first of three suites. |
| **P33-014** one unique-temp atomic writer; age-gated `clean_temp` | Array tasks on different nodes can share a pid and corrupt a shared plan file. The old scheme failed 5 of 5 concurrency trials. |
| **P33-015** drift check on every held-out access (source, materials, model pins) | The brief asked that held-out evaluation run the frozen analysis. The first version enforced that only at the moment of unlock. |
| **P33-016** `sol.env` unsets `P33_FAKE` | `--export=ALL` could carry test mode into a real job and label fake scores as real. |
| **P33-017** `status` is read-only | It created `raw/shards/armb`, which made `validate`, and so `dev_freeze`, refuse a complete development run. |
| **P33-018** prefetch keeps existing pins (`--repin` to move them) | Re-running prefetch after a freeze could silently re-pin models and block the held-out stage. |
| `prefetch --config` (default) | The `mid`/`large` tiers include 7B–32B models that no stage may score. |
| preflight in the H5 job; smoke → dev stage mapping in H5 and final export | H5 is a GPU job and had no preflight. |
| real-tokenizer fertility in the smoke | That path was otherwise first exercised on Sol. |
