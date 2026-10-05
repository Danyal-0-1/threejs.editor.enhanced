# 03 — Code and pipeline

Every stage as `INPUT → TRANSFORMATION → OUTPUT → VALIDATION`, then one real
fixture traced end to end. **All object dumps below are real output**, produced
by running the code; the command is given so you can reproduce them.

---

## 1. Data structures first

Learn these five objects and the pipeline becomes obvious — everything else is
a function mapping one to the next.

### `sites.Site` (frozen dataclass) — the atom of Phase 3

One decision site: a place in a concrete program where a correct spelling and
a familiar competitor compete. **Real instance:**

```python
site_id             = 'delta:t000:T_CLASS_SIGIL:0'
phi_id              = 'delta'
template_id         = 't000'
terminal_id         = 'T_CLASS_SIGIL'
role                = 'class matcher sigil'
occurrence          = 0
char_offset         = 17
inner               = True          # inside a quoted selector (CSS-like context)
program             = "(function(){ $S('#wheel')#recolor('#111111'); })();"
prefix              = "(function(){ $S('"
correct             = '#'           # c — delta's class sigil
competitor          = '.'           # q — the familiar CSS class sigil
collision           = 'semantic'
competitor_binds_to = 'T_ID_SIGIL'  # what '.' MEANS in delta
ir_hash_correct     = '5be0d4314219e5d2…'
ir_hash_competitor  = 'd74513ab1dcc9490…'
variant_program     = "(function(){ $S('.wheel')#recolor('#111111'); })();"
```

Read that last pair carefully: **the two programs differ by one character and
hash differently.** That is the whole experiment in one object.

### `models.LM` (Protocol) — the only thing asked of a model

```python
sequence_logprob(prefix, continuation) -> float   # teacher-forced (Arm A)
generate(prompt, max_new_tokens)       -> str     # unrestricted  (Arm B)
n_tokens(text)                         -> int     # diagnostics
```

Three methods, so the whole pipeline runs on `FakeLM` with no GPU.

### `scoring.MarginRecord` — one Arm-A measurement

```python
{'site_id': 'delta:t000:T_CLASS_SIGIL:0', 'model': 'fake-lm', 'shots': 0,
 'logp_correct': -1.0295, 'logp_competitor': 3.5227, 'm_seq': -4.5522,
 'n_tok_correct': 1, 'n_tok_competitor': 1, 'rule_present': True}
```

`m_seq = -4.55` → the fake prefers `.` by ~4.55 nats. `reverted == True`.

### `outcomes.Outcome` — one Arm-B classification

```python
{'bucket': Bucket.VALID_WRONG, 'n_ops': 1,
 'ir_hash': 'd74513ab1dcc9490…',
 'detail': 'IR hash d74513ab1dcc != target 5be0d4314219',
 'parse_valid': True, 'task_correct': False}
```

`parse_valid=True, task_correct=False` — the output is *perfectly grammatical
and wrong*. That combination is the phenomenon.

### `linter.RiskScore` — one H4 prediction

```python
{'site_id': 'delta:t000:T_CLASS_SIGIL:0', 'model': 'fake-lm',
 's_seq': 4.5522, 's_local': 4.6957, 's_shift': -0.1435,
 'terminal_id': 'T_CLASS_SIGIL', 'collision': 'semantic'}
```

Note `s_seq = -m_seq` exactly. **Opposite sign convention on purpose**: risk is
high when the competitor wins. `s_shift = -0.14` says the rule barely moved
this fake — which is the point of the decomposition.

---

## 2. The pipeline, stage by stage

```
 ┌─ STAGE 0 ── vendor_sync.py
 │   INPUT  upstream Phase 1/2 files @ commit 4e98055
 │   TRANS  copy + SHA-256 + record provenance
 │   OUTPUT phase3/vendor/ (30 files) + SOURCE_MANIFEST.md
 │   VALID  --check re-hashes: "22/22 vendored files match"
 │          _vendor.assert_self_contained(): nothing resolves upstream
 │          tests/test_scorer_repair.py: the P3-001 patch is still applied
 ▼
 ┌─ STAGE 1 ── make_delta.py
 │   INPUT  terminals.json (43 terminals, 29 substitutable)
 │   TRANS  permute WITHIN shape classes; T_CHAIN_OP follows T_CLASS_SIGIL (I7)
 │   OUTPUT vendor/alien_syntax/candidates/phi_delta.json
 │   VALID  validate_phi V1–V8 (incl. V6 partition/bijectivity proof)
 │          then re-classify the corpus: all 13 intended terminals SEMANTIC
 ▼
 ┌─ STAGE 2 ── generate_corpus.phase1_programs + transpiler.transliterate
 │   INPUT  conformance/positive.txt
 │   TRANS  3DOM text → delta text, renaming by terminal ROLE
 │   OUTPUT 62 paired programs
 │   VALID  num_parses == 1; IR hash equal across lexicons (C7 excludes source)
 ▼
 ┌─ STAGE 3 ── sites.classify            ← THE CORE
 │   INPUT  one delta program + φ_delta + φ_identity
 │   TRANS  lex → locate terminals by (token_type, value, OFFSET)
 │          → splice q at the offset → re-lex/parse/hash the variant
 │   OUTPUT list[Site] with a collision class each
 │   VALID  offsets point at `correct`; colour literals are not sites;
 │          SEMANTIC ⇒ variant parses AND hashes differently
 ▼
 ┌─ STAGE 4a ── scoring (Arm A)        ┌─ STAGE 4b ── outcomes (Arm B)
 │   forced_prefix_margin → M_seq      │   model.generate → text
 │   extinction_curve     → k*  ★      │   evaluate   → Bucket
 │   interaction_did      → DiD ×3     │   observe_site → O, Y
 │                                     │   hurdle     → P(O), P(Y|O)
 ▼                                     ▼
 └─ STAGE 5 ── linter
     score_site  → S_seq / S_local / S_shift          (H4)
     rank_report → AUROC / AUPRC / P@10 + baselines   (H4)
     propose_repair → Repair                          (H5)
     verify_repair  → IR equality over all 62 programs (H5 proof)
```
★ = the primary estimand.

---

## 3. Stage detail

### Stage 3 — `sites.classify`, the one function to understand

**Why offsets, not string search.** `#` is delta's class sigil **and** the
first character of every colour literal `'#111111'`. A `str.replace` would
corrupt arguments and invent collisions that are artifacts of the edit. Sites
come from `transpiler.lex`, which returns `(token_type, value, char_offset)`
and already knows the outer/inner two-level distinction.

Guarded by `test_colour_literal_is_not_a_site`. If that test ever fails, every
number downstream is junk.

**The classifier.** For each located terminal:

```
c = φ(tid)            the correct spelling here
q = identity(tid)     the familiar 3DOM spelling of the SAME role

c == q                              → NONE      (role not remapped)
variant doesn't lex/parse           → LEXICAL   (loud failure)
variant parses, SAME IR hash        → BENIGN    (alias; no contrast)
variant parses, DIFFERENT IR hash   → SEMANTIC  ✓ the only usable class
```

**Measured census** (`python3 scripts/site_census.py`):

| lexicon | none | lexical | benign | **semantic** |
|---|---:|---:|---:|---:|
| alpha | 0 | 315 | 0 | **72** |
| beta | 0 | 387 | 0 | **0** |
| gamma | 0 | 387 | 0 | **0** |
| **delta** | 203 | 81 | 0 | **103** |

### Stage 5 — `verify_repair`, mechanical not argued

H5's correctness condition is `IR(p) == IR(ψ(W(p)))`. Because a repair **is** a
new φ-map, and φ-maps are validated bijections on the spelling partition (V6),
preservation is *provable*: re-parse all 62 programs under both maps and
compare canonical IR hashes. Nothing is accepted on a model's judgment.

A counter-intuitive consequence, asserted in
`test_a_verb_swap_is_ir_preserving_because_renaming_is_by_role`: swapping two
verbs' **spellings** does *not* change any program's meaning, because
transliteration renames by role. The real guard against a bad repair is
`validate_phi` rejecting a spelling collision — `test_colliding_repair_is_rejected_at_validation`.

---

## 4. One real fixture, end to end

Reproduce everything below with:

```bash
cd phase3 && PYTHONPATH=src python3 -c "
from phase3 import _vendor
import phi as P, transpiler as T, generate_corpus as G
from phase3 import sites as S, scoring, outcomes, linter
from phase3.models import FakeLM
IDENT=P.identity_phi(); d=P.load_candidate('delta')
prog=T.transliterate(G.phase1_programs('positive',IDENT)[0],IDENT,d)
s=[x for x in S.classify(prog,d,template_id='t000',identity=IDENT) if x.is_usable][0]
print(S.to_dict(s))"
```

**Call order, exact:**

| # | File | Function | Produces |
|---|---|---|---|
| 1 | `src/phase3/_vendor.py` | import side effect → `assert_self_contained` | `sys.path`, guard passes |
| 2 | `vendor/.../phi.py` | `identity_phi` / `load_candidate('delta')` | two `PhiMap`s |
| 3 | `vendor/.../generate_corpus.py` | `phase1_programs('positive', ident)` | 62 3DOM programs |
| 4 | `vendor/.../transpiler.py` | `transliterate(p, ident, delta)` | the delta program |
| 5 | `src/phase3/sites.py` | `classify` → `_terminal_of_token`, `_safe_ir_hash` | `list[Site]` |
| 6 | `src/phase3/scoring.py` | `forced_prefix_margin` | `MarginRecord` |
| 7 | `src/phase3/scoring.py` | `extinction_curve` → `_interpolate_crossing` | `ExtinctionCurve` |
| 8 | `src/phase3/outcomes.py` | `evaluate` | `Outcome` |
| 9 | `src/phase3/outcomes.py` | `observe_site` → `hurdle` | `SiteObservation`, `HurdleResult` |
| 10 | `src/phase3/linter.py` | `score_site` → `rank_report` | `RiskScore`, `RankReport` |
| 11 | `src/phase3/linter.py` | `propose_repair` → `verify_repair` | `Repair`, proof |

**The values, step by step:**

```
3DOM    (function(){ $S('.wheel').recolor('#111111'); })();
delta   (function(){ $S('#wheel')#recolor('#111111'); })();
                           ↑ char_offset 17, T_CLASS_SIGIL, correct '#'

Site        competitor '.', binds to T_ID_SIGIL, collision SEMANTIC
            ir_hash_correct    5be0d4314219e5d2…
            ir_hash_competitor d74513ab1dcc9490…   ← different meaning

variant     (function(){ $S('.wheel')#recolor('#111111'); })();

MarginRecord  logp_correct −1.0295, logp_competitor +3.5227
              m_seq −4.5522  → reverted = True

Outcome       VALID_WRONG · parse_valid True · task_correct False · n_ops 1

Observation   reached True · reverted True · emitted '.'
              detail "competitor spelling bound to T_ID_SIGIL"

RiskScore     s_seq +4.5522 · s_local +4.6957 · s_shift −0.1435
```

**Why this fixture is the one to memorise.** `T_CLASS_SIGIL` is precisely the
site of Experiment 02's headline `.`-for-`#` reversion. Under `alpha` that site
is **LEXICAL** — the familiar form is a parse error. Under `delta` it is
**SEMANTIC** — the familiar form parses and silently edits the wrong object.
Same site, same model, completely different error class. That difference is
what Phase 3 exists to create.

---

## 5. Required components: implementation status

The brief lists 15 required components. Honest status — several are **not
built**, and saying otherwise would be the worst thing this document could do.

| # | Component | Status | Where |
|---|---|---|---|
| 1 | experiment configuration | **partial** — template exists, not consumed by any script | `configs/experiment.json` |
| 2 | candidate-pair definitions | **done** | `sites.classify` |
| 2b | grammar-**family** definitions | **not implemented** — 4 lexicons, 1 grammar | — |
| 3 | prior-strength (T) calibration | **not implemented** | — |
| 4 | local-context (A) calibration | **not implemented** | — |
| 5 | counterbalanced mapping generation | **not implemented** | — |
| 6 | forced-prefix sequence scoring | **done, tested** | `scoring.forced_prefix_margin` |
| 7 | unrestricted generation interface | **done** (thin), **untested on a real model** | `models.HFModel.generate` |
| 8 | parsing + canonical-IR evaluation | **done, tested** | `outcomes.evaluate` |
| 9 | opportunity / site-reach detection | **done, tested** | `outcomes.observe_site` |
| 10 | conditional reversion classification | **done, tested** | `outcomes.hurdle` |
| 11 | result serialization | **partial** — `sites.to_dict` + census JSON; no unified writer | `sites.to_dict` |
| 12 | statistical-analysis input prep | **not implemented** | — |
| 13 | validation of experimental invariants | **partial** — classifier, `make_delta --verify-only`, `prefix_collisions`; no single module | several |
| 14 | deterministic seeds + env capture | **partial** — `FakeLM` is seedless-deterministic; **no env capture** | `models._h` |
| 15 | unit + end-to-end tests | **done** — 54 passing | `tests/` |

### The 10-point reproducibility checklist

| # | Check | Result |
|---|---|---|
| 1 | lightweight unit tests | **PASS** — 54/54, `python3 tests/run_tests.py` |
| 2 | end-to-end fake-model test | **PASS** — `test_end_to_end_recovers_a_planted_effect` |
| 3 | validate counterbalancing | **CANNOT RUN** — counterbalancing not implemented |
| 4 | both candidates grammar-valid | **PASS** — `test_semantic_requires_both_valid_and_different_ir` |
| 5 | candidates map to different IR | **PASS** — same test, hash inequality asserted |
| 6 | context variants share AST/IR before the decision | **CANNOT RUN** — A-level variants not built |
| 7 | train/calibration/test separation | **CANNOT RUN** — no calibration stage exists |
| 8 | deterministic seeds | **PARTIAL** — `FakeLM` is a pure function of SHA-256 (verified by repeat runs); no global seed capture, no real-model determinism check |
| 9 | exact result serialization | **PARTIAL** — `site_census.py --json` round-trips; no unified record schema |
| 10 | nothing outside phase3/ modified | **PASS** — `git status` shows only `?? phase3/` plus pre-existing items |

Checks 3, 6 and 7 are **blocked, not passing.** They test features that do not
exist yet.

---

## 6. Learning resources

> **Verification note.** Not fetched or verified in this session. Canonical,
> stable URLs. Listed 2026-10-01.

| Resource | Teaches | Why here | Read | Level | Time |
|---|---|---|---|---|---|
| [docs.python.org/3/library/dataclasses.html](https://docs.python.org/3/library/dataclasses.html) | frozen dataclasses, `asdict` | every record object | "Module contents" | beginner | 45 min |
| [docs.python.org/3/library/enum.html](https://docs.python.org/3/library/enum.html) | enums + properties | `CollisionClass.is_usable` | tutorial | beginner | 20 min |
| [docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html) | `Protocol` | `models.LM` is structural, so `FakeLM` needs no base class | `Protocol` | intermediate | 40 min |
| [docs.python.org/3/library/hashlib.html](https://docs.python.org/3/library/hashlib.html) | SHA-256 | IR content hashing, `FakeLM` determinism | `sha256` | beginner | 15 min |
| [docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html) | canonical JSON (`sort_keys`, separators) | rule C6; hash stability depends on it | "Basic usage" | beginner | 30 min |
| [lark-parser.readthedocs.io](https://lark-parser.readthedocs.io/) | Earley parsing, ambiguity | `num_parses`, `AmbiguityError` | "Grammar reference", "Earley" | intermediate | 2 h |
| [Crafting Interpreters](https://craftinginterpreters.com/) ch. 4–6 | lexing, tokens, ASTs | why the two-level lexer exists | "Scanning", "Representing Code" | beginner | 4 h |
| [docs.python.org/3/library/unittest.html](https://docs.python.org/3/library/unittest.html) | test structure | `tests/run_tests.py` is a mini-runner; same ideas | "Basic example" | beginner | 45 min |
| [Hypothesis](https://hypothesis.readthedocs.io/) | property-based testing | the natural next step for the classifier | "Quick start" | intermediate | 2 h |
| [PyTorch: softmax / log_softmax](https://pytorch.org/docs/stable/generated/torch.nn.functional.log_softmax.html) | logits → log-probs | `HFModel.sequence_logprob` | the page | intermediate | 30 min |
| [HF: causal LM](https://huggingface.co/docs/transformers/tasks/language_modeling) | the off-by-one in `logits[:-1]` vs `ids[1:]` | the single easiest bug in `HFModel` | "Causal language modeling" | intermediate | 1.5 h |
