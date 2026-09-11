# run.md — executing and verifying the Phase 2 pipeline

**Grammar:** `3dom-grammar/1.1.0` · **Repo:** `threejs.editor.enhanced` ·
**Last executed:** 2026-09-01, experiment `run/experiments/20260901-233702`

This runbook is authoritative. The scripts in `run/` sequence the commands below
and preserve logs; they hide nothing. If you prefer, run every phase by hand from
this file.

---

## 1. Purpose and claim boundary

### What this runbook verifies

That the φ-parameterised family of languages is built the way the design claims:
one grammar template, one parser, one canonicaliser, one emitter, one IR — with
only Σ (the terminal spellings) varying. It verifies that claim **operationally**,
by running the pipeline over a finite corpus and comparing digests.

### What it cannot prove

**SHA-256 equality is not a proof of isomorphism.** The digest is the final
operational witness *after* the construction and the invariants have established
what is permitted to vary. The argument has three tiers and they are not
interchangeable:

| Tier | What it is | What it covers |
|---|---|---|
| **Constructive argument** | One shared template rendered through a validated φ; N and the shape of P frozen; I1–I10 asserted | The *family*. This is the part that generalises beyond the corpus. |
| **Finite regression evidence** | Gates A1–A7 and the test suites, over 62 positive / 64 negative / 12 vacuous programs | The *tested programs*. Nothing more. |
| **Operational witness** | `content_hash(canonical_json(IR))` agreeing across lexicons | That the two pipelines *did in fact* produce the same IR on these inputs. |

A structurally valid, hash-stable program can still express an unintended
operation. `$S('.a').rotate(90)` binds `90` to `axis`, not `degrees` — it parses,
validates against the schema, round-trips, and hashes stably, and it is wrong.
Compiler correctness and intent correctness are separate layers; only the
heuristics in `src/heuristics_ir.py` address the second.

### Structural vs empirical steps

- **Phases 0–8 and 12 are structural.** No models, no network, no GPU. They are
  deterministic: the same inputs give the same digests on any machine.
- **Phases 9–11 are empirical.** They depend on external tokenizer/model
  revisions and on hardware. A structural PASS says nothing about them.

The two lanes are separate scripts on purpose. A structural PASS must never be
mistaken for a completed empirical validation.

---

## 2. Repository assumptions

### Layout

```
<repo root>/
├── grammar_and_3DOM_client/      ← PHASE 1 (the frozen reference)
│   ├── terminals.json                43 terminals; 29 substitutable, 14 frozen
│   ├── tasks.py                      _SIGNATURES, cross-checked by C8
│   ├── ir_schema.json                additionalProperties:false
│   ├── grammar_metrics.py            the instrument that measures I1–I3
│   ├── 3dom_grammar.iso.ebnf         normative appendix (ISO/IEC 14977)
│   ├── 3dom_grammar.w3c.ebnf         normative appendix (W3C EBNF)
│   └── conformance/
│       ├── refgrammar.py             parse counter, DFA, 57 coverage features
│       ├── positive.txt  (62 programs)
│       ├── negative.txt  (64 programs)
│       └── vacuous.txt   (12 programs)
├── alien_syntax/                 ← PHASE 2
│   ├── candidates/     phi_{alpha,beta,gamma}.json
│   ├── grammar/        templates/ + generated/ + render_grammar.py
│   ├── src/            phi.py, canonicalize.py, transpiler.py,
│   │                   generate_corpus.py, heuristics_ir.py
│   ├── measure/        collisions.py, dfa_parity.py, fertility.py,
│   │                   prior_strength.py, metrics_parity.py
│   ├── tests/          9 suites (see §7)
│   ├── conformance/    generated alien corpora
│   └── reports/        CANDIDATE_SELECTION.md, METRICS_PARITY.md
└── run/                ← this runbook and its outputs
```

### `PHASE1_DIR`

`src/phi.py:phase1_dir()` resolves Phase 1 as:

1. `$PHASE1_DIR` if set (absolutised), else
2. `<repo root>/grammar_and_3DOM_client`.

Set it only if Phase 1 lives elsewhere:

```bash
export PHASE1_DIR=/path/to/grammar_and_3DOM_client
```

### Preflight

`run/preflight.py` checks all of it **before anything from either phase is
imported** — it deliberately imports nothing from `src/`, so it can still
diagnose the case where that import is what fails.

```bash
python3 run/preflight.py            # structural lane
python3 run/preflight.py --model    # also require transformers + torch
python3 run/preflight.py --json     # machine-readable
```

It names each missing path *and what needs it*. **Do not create placeholder
Phase 1 artifacts to get past it** — the entire isomorphism argument rests on
Phase 1 being the frozen reference.

---

## 3. Environment setup

**Python 3.12+** (developed and executed on 3.12.3). `functools.cached_property`
on a frozen dataclass and PEP 604 unions in `singledispatchmethod` registrations
are used; 3.10 is the realistic floor, 3.12 is what is tested.

### Structural lane — no venv needed if `lark` is importable

```bash
cd <repo root>
python3 -c "import lark; print(lark.__version__)"   # need 1.3.x
python3 run/preflight.py
```

If `lark` is missing, use the venv below.

### Full venv (required for Lane B/C; Ubuntu marks the system Python
`EXTERNALLY-MANAGED`, so `pip install` outside a venv is refused)

```bash
cd <repo root>
python3 -m venv run/.venv
run/.venv/bin/python -m pip install --upgrade pip

# structural + tokenizer lane
run/.venv/bin/python -m pip install 'lark==1.3.1' jsonschema transformers

# add for the model lane (Phase 10) — large
run/.venv/bin/python -m pip install torch
```

> `lark` and `jsonschema` are easy to forget: `transformers` alone leaves the
> venv unable to *parse* anything, and Phase 9 fails deep inside `corpus_for`
> with `ModuleNotFoundError: No module named 'lark'`. This actually happened
> during the 2026-09-01 run; `run/preflight.py` now catches it first.

### Capture versions

```bash
run/.venv/bin/python -m pip list --format=freeze | sort > versions.txt
python3 -V; uname -srmo; nvidia-smi --query-gpu=name,memory.total --format=csv
```

### Hugging Face (optional)

Public for every repo used here. Set a token only to raise rate limits:

```bash
export HF_TOKEN=hf_...          # never logged; scripts record only whether it is set
export HF_HOME=/path/with/space # models are multi-GB
```

### CPU vs GPU

`measure/prior_strength.py --device auto` picks CUDA when available. In fp32,
0.5B ≈ 2 GB, 1.5B ≈ 6 GB, 3B ≈ 12 GB of VRAM; **7B ≈ 30 GB does not fit in
16 GB** and falls back to CPU, where it is slow but correct. Force with
`--device cpu` or `--device cuda`.

---

## 4. Quick structural verification

```bash
cd <repo root>
./run/run_structural.sh
```

One command, ~40 s on the reference machine. It runs phases 0–8 and 12, writes
to a fresh `run/experiments/<UTC timestamp>/`, and **modifies no committed
artifact**: grammars are re-rendered into the experiment directory and diffed,
corpora are checked with `--check-only`, `METRICS_PARITY.md` is regenerated to a
temp file and diffed.

It covers imports, φ validation, template rendering, corpus generation, collision
checks, DFA parity, structural metrics, isomorphism, round trip, invariants, and
the structural fertility proxy.

> **This lane does NOT satisfy the tokenizer-fertility constraint.** The
> structural proxy measures characters. CONSTRAINT 1 is defined on the fertility
> RATIO in *tokens*, and characters are not tokens — the 2026-09-01 run measured
> β at **1.000 by characters and 1.401 by tokens**. Character-length parity is
> not tokenizer parity. Phase 9 is the only thing that settles CONSTRAINT 1.

---

## 5. Full ordered pipeline

All commands run from the repo root unless stated. `$EXP` is the experiment
directory.

---

### Phase 0 — environment preflight

- **Objective:** fail before any parser import, naming the missing path.
- **Prerequisites:** none.
- **Command:** `python3 run/preflight.py`
- **Input:** `$PHASE1_DIR`, the Phase 2 tree, importable modules.
- **Output:** `$EXP/metadata/preflight.json`
- **Pass:** exit 0, `PASS — every required artifact and dependency is present.`
- **Likely failure:** `FATAL: the Phase 1 directory does not exist.`
- **Troubleshooting:** set `PHASE1_DIR`; see §10.
- **Network/GPU:** no / no. **Rerun-safe:** yes. **Resume:** from the start.

### Phase 1 — Phase 1 contract verification

- **Objective:** confirm the frozen reference still passes its own gates before
  measuring anything against it.
- **Command:** `cd grammar_and_3DOM_client && python3 conformance/coverage2.py`
- **Pass:** `RESULT: PASS — all gates green` (G1–G6), exit 0.
- **Note:** `conformance/coverage.py` (no `2`) **crashes** —
  `FileNotFoundError: .../conformance/negatives.txt`; the file is `negative.txt`.
  Use `coverage2.py`. This is a Phase 1 defect, unfixed here (out of scope).
- **Network/GPU:** no / no. **Rerun-safe:** yes.

### Phase 2 — template reconstruction

- **Objective:** prove the templates are the Phase 1 grammar *slotified*, not a
  retyping of it.
- **Command:** `cd alien_syntax && python3 grammar/templates/build_templates.py`
- **⚠ Writes to `grammar/templates/*.ebnf` in place.** It is deterministic and
  self-verifying, so a clean checkout is rewritten byte-for-byte — but snapshot
  first if you want a guarantee. `run_structural.sh` snapshots and restores on
  drift.
- **Pass:** `identity render == Phase 1 ✓ (29 distinct slots)` for both notations.
- **Likely failure:** `IDENTITY RENDER MISMATCH ... line N` — Phase 1's grammar
  changed, or a terminal spelling moved in `terminals.json`.
- **Network/GPU:** no / no. **Rerun-safe:** yes.

### Phase 3 — alpha/beta/gamma grammar rendering

- **Objective:** render four artifacts per lexicon through gates G-R1…G-R6.
- **Command (non-destructive, preferred):**
  ```bash
  cd alien_syntax
  python3 grammar/render_grammar.py --outdir "$EXP/artifacts/generated" alpha beta gamma
  diff -rq grammar/generated "$EXP/artifacts/generated"
  ```
- **Command (in place):** `python3 grammar/render_grammar.py alpha beta gamma`
- **Output:** `alien.<id>.{iso.ebnf,w3c.ebnf,lark,diagram.md}`
- **Pass:** `G-R5 ✓ both levels ... load in Lark (Earley)` and
  `G-R6 ✓ ... (|N|=31, |P|=58 in both notations)` for each lexicon.
- **Likely failure:** G-R6 `|N|` mismatch — a terminal spelling collided with the
  EBNF *metasyntax* (`?` opens an ISO special sequence, `|` is alternation), so
  the generated appendix silently lost productions while the language is fine.
- **Network/GPU:** no / no. **Rerun-safe:** yes.

### Phase 4 — corpus regeneration and gates A1–A7

- **Objective:** generate the alien corpora **by φ**, never by hand, and gate them.
- **Command (check only, writes nothing):**
  ```bash
  cd alien_syntax && python3 src/generate_corpus.py alpha beta gamma --check-only
  ```
- **Command (write):** drop `--check-only`; add `--winner=<id>` to also write the
  unsuffixed `alien.{positive,negative,vacuous}.txt`.
- **Gates:** A1 unique parse · A2 100% production coverage (57 branches) ·
  A3 negatives reject · A4 vacuous parse **and lower to zero operations** ·
  A5 the L2 whitespace differential survives φ · A6 Lark ≡ DFA ·
  A7 φ⁻¹∘φ = id and IR hashes match the 3DOM twin.
- **Pass:** `φ = <id>  A1–A7 PASS` for each, exit 0.
- **Network/GPU:** no / no. **Rerun-safe:** yes (idempotent).

### Phase 5 — collisions and lexical reachability

- **Command:** `cd alien_syntax && python3 measure/collisions.py identity alpha beta gamma --md`
- **Checks:** (a) prefix · (b) bare identifier · (c) overload preservation (I7) ·
  (d) frozen terminals (I9) · (e) delimiter symmetry (I8) · (f) D3 argument
  unambiguity — these six are **CONSTRAINT 2** and set the exit code.
  **(g) is PROPOSED**, reported separately, and deliberately does *not* affect
  the exit code, so a pre-committed decision cannot turn on a criterion added
  afterwards.
- **Pass:** zero violations on (a)–(f).
- **Expect:** γ reports **24 findings on (g)** (22 × g1 lexical-class, 2 × g2
  reachability). That is a real property of a glyph lexicon, not a bug.
- **Network/GPU:** no / no. **Rerun-safe:** yes.

### Phase 6 — DFA and metrics parity

```bash
cd alien_syntax
python3 measure/dfa_parity.py identity alpha beta gamma --md
python3 measure/metrics_parity.py > /tmp/mp.md && diff reports/METRICS_PARITY.md /tmp/mp.md
```

- **Pass:** P1/P2/P4 parity at **tolerance 0.000** (pre-committed, stated before
  any number existed); `METRICS_PARITY.md` regenerates identically.
- **Never** redirect straight onto `reports/METRICS_PARITY.md` — write to a temp
  file and diff, so a bad run cannot silently replace a good report.
- **Network/GPU:** no / no. **Rerun-safe:** yes.

### Phase 7 — isomorphism, round-trip, invariant, and unit suites

Run and report **independently** — a single aggregate number hides which claim
broke.

```bash
cd alien_syntax
for s in isomorphism roundtrip invariants canonicalization phi_validation \
         grammar_whitespace seams measure_formulas preflight; do
  echo "== $s"; python3 "tests/test_$s.py" || echo "FAILED: $s"
done
```

They also run under `pytest tests/` if you prefer; the standalone runners exist
so the lane needs no test framework.

- **Pass:** every suite exits 0 and prints `N/N passed`.
- **Network/GPU:** no / no. **Rerun-safe:** yes.

### Phase 8 — structural fertility proxy

- **Command:** `cd alien_syntax && python3 measure/fertility.py --structural --md`
- **Pass:** it runs. **It is a PROXY.** It reports characters and UTF-8 bytes.
  It does **not** satisfy CONSTRAINT 1 and the output says so.
- **Network/GPU:** no / no.

### Phase 9 — real tokenizer fertility (**CONSTRAINT 1**)

- **Objective:** the binding experimental constraint.
- **Prerequisites:** venv with `transformers` **and `lark`**; network.
- **Command:**
  ```bash
  cd alien_syntax && ../run/.venv/bin/python measure/fertility.py --md
  # or: ../run/.venv/bin/python measure/fertility.py --tokenizers Qwen/Qwen2.5-Coder-0.5B --md
  ```
- **Method:** `transformers.AutoTokenizer`, `add_special_tokens=False`, ratios
  from **corpus totals** (not a mean of per-item ratios). **Never `tiktoken`** —
  it does not cover the Qwen2.5-Coder family.
- **Output:** per-tokenizer table + a **Provenance** JSON block recording repo,
  resolved revision SHA, `transformers` version, tokenizer class, vocab size,
  corpus hash, program count and timestamp.
- **Pass criterion:** fertility ratio ∈ **[0.95, 1.05]** per
  `reports/CANDIDATE_SELECTION.md`.
- **Exit codes:** 0 measured · 2 `transformers` absent · 3 **no tokenizer loaded**
  (a failure, not an empty result) · 4 corpora not paired.
- **Download:** ~50 MB total (tokenizer files only). **Network:** yes. **GPU:** no.
- **Rerun-safe:** yes; the HF cache is reused. **Resume:** rerun; it is stateless.

### Phase 10 — base-model prior strength and ΔNLL

- **Prerequisites:** venv with `torch` **and** `transformers`; network; GPU
  strongly preferred.
- **Command:**
  ```bash
  cd alien_syntax && ../run/.venv/bin/python measure/prior_strength.py --md
  # smaller: --models Qwen/Qwen2.5-Coder-0.5B --device cuda
  ```
- **Method:** BASE checkpoints (never Instruct — instruction tuning reshapes the
  likelihood surface, and the claim is about *pretraining* proximity).
  `NEUTRAL_PREFIX = ""`. Both normalisations reported:
  `NLL/token = ΣNLL / Σtokens`, `NLL/char = ΣNLL / Σchars`,
  `ΔNLL = alien − identity`, paired per item.
- **CI:** paired bootstrap, `BOOTSTRAP = 10000`, `SEED = 20260910`, resampling
  **item indices** applied to both arms and recomputing the *same* ratio-of-totals
  estimand as the point estimate.
- **Download:** 0.5B ≈ 1 GB, 1.5B ≈ 3 GB, 3B ≈ 6 GB, 7B ≈ 15 GB.
- **Exit codes:** 0 scored · 2 torch/transformers absent · 3 **no model scored**.
- **Network:** yes. **GPU:** yes for ≤3B in fp32. **Rerun-safe:** yes.
- **Resume after interruption:** rerun; the HF cache keeps completed downloads,
  and the script is stateless per model.

### Phase 11 — candidate selection

Not a command — a decision, made against §9's table. **Do not select a winner
while a binding criterion is unmeasured.** As of 2026-09-01 CONSTRAINT 1 is
measured and **no candidate satisfies it**; see §9.

### Phase 12 — final artifact and checksum verification

```bash
python3 run/verify_artifacts.py --write "$EXP/metadata/checksums.txt"
python3 run/verify_artifacts.py --compare run/experiments/<earlier>/metadata/checksums.txt
```

`--compare` exits nonzero on any change and names each changed artifact, so a
result can be tied to the exact corpus, grammar and φ-map that produced it.

---

## 6. Baseline command inventory

Inspected and corrected against the actual repository. Differences from the
originally proposed list are called out.

| Proposed | Verified form | Note |
|---|---|---|
| `python3 grammar/templates/build_templates.py` | ✅ as-is | run from `alien_syntax/`; writes templates in place |
| `python3 grammar/render_grammar.py alpha beta gamma` | ✅ as-is | `--outdir DIR` **added** for non-destructive regeneration |
| `python3 src/generate_corpus.py alpha beta gamma --winner=beta` | ⚠ **do not run as-is** | `--winner=beta` promotes β to the unsuffixed corpus. β **fails CONSTRAINT 1** (§9); use `--check-only` until the winner is settled |
| `python3 measure/collisions.py` | ✅ as-is | defaults to all four lexicons |
| `python3 measure/dfa_parity.py` | ✅ as-is | |
| `python3 measure/metrics_parity.py` | ⚠ redirect to a **temp file**, then diff | it regenerates a tracked report |
| `python3 tests/test_isomorphism.py` | ✅ as-is | |
| `python3 tests/test_roundtrip.py` | ✅ as-is | |
| `python3 tests/test_invariants.py` | ✅ as-is | |
| — | **6 new suites** | `test_canonicalization`, `test_phi_validation`, `test_grammar_whitespace`, `test_seams`, `test_measure_formulas`, `test_preflight` |
| `python3 measure/fertility.py --structural --md` | ✅ as-is | proxy only |
| `python3 measure/fertility.py --md` | ✅ needs venv with `transformers` **and `lark`** | |
| `python3 measure/prior_strength.py --md` | ✅ needs `torch` | not run on 2026-09-01 |

---

## 7. Logging

`run/runlog.sh <slug> <command...>` records, per command: the command line, cwd,
exit code, start/finish UTC, duration, and separate `.out` / `.err` files, under
`$EXP/logs/`.

Each experiment directory is:

```
run/experiments/YYYYMMDD-HHMMSS/
├── logs/        <slug>.out, .err, .meta per command
├── results/     the reports a reader should look at
├── artifacts/   regenerated grammars/corpora/reports, for diffing
└── metadata/    environment, pip freeze, preflight.json, checksums, git state
```

Captured: Python version, package freeze, OS, CPU/GPU, `PHASE1_DIR`,
`PYTHONPATH`, git commit and dirty flag, model/tokenizer revisions (in each
report's Provenance block), corpus hashes, artifact checksums.

**Secrets are never logged** — `HF_TOKEN` is recorded only as `hf_token_set=yes|no`.

Experiment directories are never overwritten: the timestamp is the identity.

---

## 8. Expected-result table

Observed values are from `run/experiments/20260901-233702` on Ubuntu 24.04,
Python 3.12.3, RTX 3080 Ti (16 GB), `lark 1.3.1`, `transformers 5.16.1`.

| Phase | Command | Expected | Observed | Status | Artifact/log |
|---|---|---|---|---|---|
| 0 | `run/preflight.py` | all present | all present; `torch` absent (optional) | **PASS** | `logs/p0-preflight.*` |
| 1 | `conformance/coverage2.py` | G1–G6 green | `PASS — all gates green`; 62/64/12, 57/57 branches, 138 items | **PASS** | `logs/p1-phase1-coverage.out` |
| 2 | `build_templates.py` | identity render == Phase 1 | both notations ✓, 29 slots each, byte-identical | **PASS** | `logs/p2-build-templates.out` |
| 3 | `render_grammar.py α β γ` | G-R1…G-R6 | all ✓, \|N\|=31 \|P\|=58; regenerated == committed | **PASS** | `logs/p3-render-grammar.out` |
| 4 | `generate_corpus.py --check-only` | A1–A7 pass | α, β, γ all `A1–A7 PASS` | **PASS** | `logs/p4-corpus-gates.out` |
| 5 | `collisions.py --md` | (a)–(f) clean | identity/α/β/γ: 0 violations. γ (g): **24 findings** | **PASS** (a–f) | `results/collisions.md` |
| 6 | `dfa_parity.py --md` | parity @ 0.000 | 52 states, mean 3.980, max 9, 26.92 tok/prog — identical across all four | **PASS** | `results/dfa-parity.md` |
| 6 | `metrics_parity.py` | regenerates identically | byte-identical to committed | **PASS** | `artifacts/METRICS_PARITY.regenerated.md` |
| 7 | 9 test suites | all green | 149/149 (4+8+14+34+25+21+14+22+7) | **PASS** | `logs/p7-test-*.out` |
| 8 | `fertility.py --structural` | proxy runs | β 1.000 by characters; γ 0.716 chars, 1.368 bytes/char | **PASS (proxy)** | `results/fertility-structural-proxy.md` |
| 9 | `fertility.py --md` | ratio ∈ [0.95, 1.05] | **α 1.068–1.073, β 1.401–1.448, γ 1.937–2.285** | **MEASURED — all candidates FAIL** | `results/fertility-tokenizers.md` |
| 10 | `prior_strength.py --md` | ΔNLL/token, ΔNLL/char, CI | not run (`torch` not installed) | **PENDING-EMPIRICAL-MEASUREMENT** | — |
| 11 | candidate selection | one winner | **no candidate satisfies CONSTRAINT 1** | **RESEARCH-DECISION-REQUIRED** | §9 |
| 12 | `verify_artifacts.py` | checksums written | 39 artifacts, none missing | **PASS** | `metadata/checksums.txt` |

---

## 9. Candidate decision table

Fertility from `run/experiments/20260901-233702`, `transformers 5.16.1`,
`add_special_tokens=False`, 62-item parallel corpus, sha256 `38bbbac1a335d254`.
Ratio = alien tok/char ÷ 3DOM tok/char; the range spans the two distinct
tokenizers.

| Criterion | Alpha | Beta | Gamma | Required threshold | Status |
|---|---:|---:|---:|---|---|
| Corpus gates A1–A7 | PASS | PASS | PASS | all pass | **VERIFIED** |
| Collisions (a)–(f) — CONSTRAINT 2 | 0 | 0 | 0 | zero violations | **VERIFIED** |
| Reachability (g), proposed | 0 | 0 | **24** | zero (if adopted) | **VERIFIED**; γ fails |
| DFA branching parity — CONSTRAINT 3 | PASS | PASS | PASS | tolerance 0.000 | **VERIFIED** |
| Test suites — CONSTRAINT 4 | PASS | PASS | PASS | all green | **VERIFIED** |
| **Fertility ratio — CONSTRAINT 1** | **1.068–1.073** | **1.401–1.448** | **1.937–2.285** | **[0.95, 1.05]** | **MEASURED — all three FAIL** |
| Fragmented % (Qwen / DeepSeek) | 0.0 / 0.0 | 0.0 / 0.0 | 36.4 / 55.0 | — | REPORTED |
| ΔNLL / token | — | — | — | — | **PENDING** |
| ΔNLL / character (primary objective) | — | — | — | — | **PENDING** |
| 95% CI (Δ/char) | — | — | — | — | **PENDING** |
| **Final interpretation** | closest to the band, still outside | fails by ~40% | fails by ~2× | — | **RESEARCH-DECISION-REQUIRED** |

**No winner is selected.** Two independent reasons:

1. **CONSTRAINT 1 is now measured and no candidate satisfies it.** The
   provisional winner β was chosen on the *structural proxy*, which reports
   β ÷ 3DOM = **1.000** because β is character-length matched. The real
   tokenizers report **1.401** (Qwen) and **1.448** (DeepSeek): β's pronounceable
   nonwords are absent from the BPE vocabulary and fragment into sub-word pieces
   at the same character count. β's fragmented-% is **0.0** — this is *not* byte
   fallback, it is ordinary sub-word splitting, which the fragmentation metric
   by design cannot see.
2. **ΔNLL, the primary objective, has never been measured** on this machine.

γ additionally fails reachability (g) and shows heavy byte fallback (36–55%), so
it remains a **stress diagnostic, not a clean control**.

A methodological note for the writeup: the four Qwen2.5-Coder repos share **one**
tokenizer (`Qwen2Tokenizer`, vocab 151665). The five listed repos are **two**
distinct tokenizers, not five independent measurements.

---

## 10. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'refgrammar'` | Phase 1 not found | `python3 run/preflight.py`; set `PHASE1_DIR` |
| `FATAL: the Phase 1 directory does not exist` | wrong `PHASE1_DIR` | point it at the dir holding `terminals.json` |
| `No module named 'lark'` inside `corpus_for` | venv has `transformers` but not `lark` | `run/.venv/bin/python -m pip install 'lark==1.3.1'` |
| `AmbiguityError: N ambiguous node(s)` | grammar became ambiguous (I10) | a φ spelling collided; check `collisions.py (a)` and the rendered `.lark` |
| `[G-R4] identity render ... differs at line N` | template no longer *is* the Phase 1 grammar | rerun Phase 2; if it persists, Phase 1's `.ebnf` changed |
| `[G-R6] \|N\| = 30 but Phase 1 has 31` | a spelling collided with EBNF **metasyntax** (`?`, `\|`) | change that spelling in the φ-map |
| Stale generated files | edited a φ-map without re-rendering | rerun Phase 3, then Phase 4 |
| `PhiValidationError: ... (N defect(s))` | φ-map broke V1–V8 | each line is prefixed with its code; see `tests/test_phi_validation.py` |
| A negative is accepted | φ repaired a near-miss | `tests/test_seams.py::test_a_near_miss_stays_a_near_miss` localises it |
| Lark/DFA disagreement (A6) | the two seams diverged | `tests/test_seams.py` runs the biconditional over all 552 item/lexicon pairs |
| `**transformers is not installed**`, exit 2 | structural venv | install into the venv, or accept CONSTRAINT 1 as PENDING |
| Tokenizer download 401/403 | gated repo | `export HF_TOKEN=...`, or `--tokenizers` with ungated repos |
| `torch.cuda.OutOfMemoryError` | 7B fp32 needs ~30 GB | `--device cpu`, or drop 7B from `--models` |
| Model run very slow | CPU fp32 | use `--device cuda` for ≤3B |
| Tokenizer/model revision drift | HF repo moved | compare the `revision` SHA in the Provenance block against a previous run |
| Artifact hash mismatch | corpus/grammar/φ changed | `run/verify_artifacts.py --compare <earlier checksums>` names the file |
| Nonzero exit, no obvious message | a phase failed | `grep -l 'exit_code=[^0]' $EXP/logs/*.meta` |
| Model run interrupted | — | rerun; HF cache keeps downloads, the script is stateless per model |

---

## 11. Claim ledger

| Claim | Formal argument | Test evidence | Empirical measurement | Current status |
|---|---|---|---|---|
| N and the shape of P are frozen across lexicons | One template, slots only for substitutable terminals (G-R2/G-R3); \|N\|=31, \|P\|=58 | `test_invariants` I1–I3; G-R6 re-parses both appendices | n/a | **VERIFIED** |
| The templates *are* the Phase 1 grammar | Identity render is byte-for-byte equality (G-R4) | `test_templates_render_to_phase1_under_identity` | n/a | **VERIFIED** |
| φ is a bijection modulo the '.' overload | V6 spelling-partition equality; φ⁻¹ derived, never declared | `test_phi_validation` (25), `test_roundtrip` | n/a | **VERIFIED** |
| Baseline and alien share one code path | `identity_phi` is a member of the same family; one parser, one canonicaliser, one emitter | all 9 suites run identity alongside α/β/γ | n/a | **VERIFIED** |
| Alien IR ≡ 3DOM IR on the corpus | Constructive: role-keyed transformers, C0–C9 | `test_isomorphism`; A7 | SHA-256 agreement over 62 programs × 3 lexicons | **VERIFIED (finite corpus)** — the digest is an operational witness, not the theorem |
| Two independent recognizers agree | Lark (Earley) and the hand lexer + Phase 1 DFA share no code | `test_seams`: biconditional over 552 item/lexicon pairs | n/a | **VERIFIED** |
| Selector whitespace stays significant | I9; `WS : / +/` with no `%ignore` at L2 | `test_grammar_whitespace` (21), A5 | n/a | **VERIFIED** |
| Grammar-level layout normalisation (C9) | `WS` matches a run; `child_combinator : WS? CHILD WS?` | `test_grammar_whitespace` C9 tests | n/a | **VERIFIED**, now registered in `canonicalize.py` |
| Zero ambiguity | Earley with `ambiguity="explicit"`, counted before transformation | I10; `test_grammar_whitespace` incl. a synthetic ambiguous control | n/a | **VERIFIED** |
| Parse complexity is matched | Shared DFA; role-named token types | DFA parity @ tolerance 0.000 | n/a | **VERIFIED** |
| γ is lexically reachable-parity with 3DOM | — | check (g): **24 findings** | n/a | **FAILED** — γ is a stress diagnostic |
| **Token cost is matched (CONSTRAINT 1)** | — | structural proxy only (characters) | **Measured: α 1.068–1.073, β 1.401–1.448, γ 1.937–2.285 vs band [0.95, 1.05]** | **FAILED for all three candidates** |
| Reduced pretraining proximity (ΔNLL) | — | formulas unit-tested with fakes; alignment verified | **not run** | **PENDING-EMPIRICAL-MEASUREMENT** |
| β is the winner | — | — | — | **WITHDRAWN** — see §9 |
| A hash-stable program matches user intent | — | `test_C8_structural_validity_is_not_intent_correctness` shows it does **not** follow | n/a | **Explicitly NOT claimed** |

---

*Generated during the audit of 2026-09-01. Every "Observed" value above was
produced by a command in this file on this machine; nothing is copied from prior
documentation.*
