# The code of this research

*A textbook-style guide to what the code computes, step by step, for every experiment and in both
grammar families. Companion to [`experiment_theory.md`](experiment_theory.md) (why) and
[`experiment_math.md`](experiment_math.md) (the equations). How the code is run, stored and
reported is in [`experiment_pipeline.md`](experiment_pipeline.md). Written 2026-10-28.*

This guide follows the data through the code, from a grammar rule to a number in a CSV. For each
step it shows **the function that does it, what goes in, what comes out, and the real values** for
the running example. The aim is that you can open any file of the pipeline and know where you are.

## How to read this guide

- **Which code.** The registered Phase 3.3 numbers were computed by the frozen code in
  `phase3_2/src/phase3_2/`, `phase3_2/sol/src/p33/`, `phase3/src/phase3/` and `phase3/vendor/`,
  driven by `phase3_2/sol/scripts/p33.py`. Phase 4 runs a **verified copy** of all of it, in one
  folder, [`phase4/code/`](../../phase4/code/README.md): each copied file differs from its origin
  only in import lines and recorded path edits (checked by `tools/verify_copy.py` against
  `source_manifest.json`), plus Phase 4's additions for served models. This guide cites the
  Phase 4 copy, because it is the code you will run and edit; every function named here exists,
  with the same logic, in the frozen original.
- **Line numbers** are clickable: [`h5.py:71`](../../phase4/code/p4/experiments/h5.py#L71).
- **The running example** is template `t011` under lexicon `d50s3`, in both families:

```text
dom   (function(){ $S('.panel>#frame>camera')#metalness(0.8); })();
blk   $S '.panel>#frame>camera' { metalness 0.8; }
```

  The site followed through every experiment is the type keyword (`T_TYPE_MESH`): correct
  `camera`, familiar `mesh`. Its ids are `dom:d50s3:t011:T_TYPE_MESH:0` and
  `blk:d50s3:t011:T_TYPE_MESH:0`. Values marked **held-out** are read from the run
  `heldout-20261007a`.

### Jump to a topic

- [The map](#1-the-map-of-the-code) · [the language library](#2-the-language-library-dsl) · [templates, families, lexicons](#3-the-experiments-language-layer-p4language) · [sites](#4-decision-sites-p4sites) · [prompts and examples](#5-prompts-and-worked-examples-p4prompts) · [the scorer](#6-the-scorer-p4scoring)
- [plan and cells](#7-the-plan-and-the-cells-p4experimentspipelinepy) · [Arm A](#8-arm-a-step-by-step) · [the ladder](#9-the-ladder-and-the-paraphrases-step-by-step) · [Arm B](#10-arm-b-step-by-step) · [H5](#11-h5-step-by-step) and [its defect](#116-a-defect-found-on-2026-10-28-the-targeted-arm-scored-the-wrong-lexicon)
- [bootstrap and rule effect](#12-from-rows-to-numbers-the-bootstrap-and-the-rule-effect) · [k* and Kaplan–Meier](#13-k-and-kaplanmeier) · [H4](#14-h4-step-by-step) · [H2 and power](#15-h2-and-power)
- [one site through everything](#16-one-site-through-all-the-code) · [defect history](#17-the-defect-history-what-each-guard-in-the-code-is-for) · [practice](#18-practice)

---

## 1. The map of the code

```text
phase4/code/
├── run.py                 the command line: init, run, merge, export, freeze, unlock …   (442 lines)
├── dsl/                   the language library (Phases 1–3), on sys.path                 (4,380)
│   ├── grammar_and_3DOM_client/   terminals.json, the EBNF grammars, refgrammar.py
│   └── alien_syntax/              phi.py, transpiler.py, canonicalize.py; candidates/phi_*.json
├── p4/                    the pipeline, one folder per stage
│   ├── language/          templates, the two grammar families, the lexicon family          (838)
│   ├── sites/             decision sites, collision classes, de-duplication, sampling      (725)
│   ├── prompts/           the token table, its controls, worked examples                   (408)
│   ├── scoring/           the margin scorer (local GPU and served API), fakes, fertility   (1,400)
│   ├── experiments/       pipeline (Arm A, ladder), Arm B, H5                              (1,036)
│   ├── analysis/          bootstrap, k* and Kaplan–Meier, H4, H2, power                    (1,292)
│   ├── governance/        model registry, split, freeze and unlock, provenance             (807)
│   ├── runtime/           configuration, crash-safe shards, prefetch, preflight, API       (1,104)
│   └── reporting/         19 CSVs, 12 plots, 10 reports                                    (1,440)
├── configs/  sol/  tools/  tests/  (240 tests in 15 files)
```

**Data flows in this order:** language → sites → prompts → scoring → experiments → analysis →
reporting, with governance checking access before anything starts and runtime storing every result.

**One import trick to know.** The language library is not a Python package: its modules import each
other by bare name (`import phi`). [`p4/paths.py`](../../phase4/code/p4/paths.py) puts its three
source folders on `sys.path` once, and `import p4` runs it first. That is why pipeline files say
`import phi as P` and `import canonicalize as C` at the top.

---

## 2. The language library (`dsl/`)

### 2.1 The terminal table

[`terminals.json`](../../phase4/code/dsl/grammar_and_3DOM_client/terminals.json) lists the 43
terminals of grammar `3dom-grammar/1.1.0`, each with an **id** (`T_CLASS_SIGIL`), its 3DOM
**spelling** (`.`), a **role** (`class selector sigil`) and whether it is **substitutable**. 29
are; 14 are frozen. Everything downstream is keyed on the id, never on the spelling.

### 2.2 A lexicon: `phi.py`

[`phi.py`](../../phase4/code/dsl/alien_syntax/src/phi.py) loads a φ-map (a JSON file
`candidates/phi_<id>.json`) and **validates it or raises** — there is no warning path:

| function | line | what it does |
|---|---:|---|
| `load_terminals` | [150](../../phase4/code/dsl/alien_syntax/src/phi.py#L150) | reads `terminals.json`; refuses another grammar version |
| `validate_phi` | [266](../../phase4/code/dsl/alien_syntax/src/phi.py#L266) | checks V1–V8 (theory §4.1), collects every defect, raises once with all of them |
| `PhiMap.spelling(tid)` | [191](../../phase4/code/dsl/alien_syntax/src/phi.py#L191) | φ(tid): the spelling this language uses for that role |
| `PhiMap.invert()` | [212](../../phase4/code/dsl/alien_syntax/src/phi.py#L212) | φ⁻¹ as derived data: spelling → the set of ids it denotes |
| `identity_phi` | [399](../../phase4/code/dsl/alien_syntax/src/phi.py#L399) | 3DOM itself, as the identity member of the family |
| `load_candidate(pid)` | [471](../../phase4/code/dsl/alien_syntax/src/phi.py#L471) | `"identity"` → 3DOM; otherwise loads and validates `phi_<pid>.json` |

V6 is the heart of it. It compares two **partitions** of the 29 substitutable ids: group the ids by
their 3DOM spelling, group them by their new spelling, and require the same groups. 3DOM has 28
groups: 27 singletons plus {`T_CHAIN_OP`, `T_CLASS_SIGIL`}, which share `.`. So a lexicon may move
spellings around, but two roles share a spelling **exactly when** they share one in 3DOM. That is
what makes φ invertible.

Under `d50s3`: `spelling("T_TYPE_MESH") = "camera"`, `spelling("T_TYPE_GROUP") = "mesh"`, and
`invert()["mesh"] = {T_TYPE_GROUP}`. That last fact is the whole collision: the familiar `mesh` is
a real word of this language, naming another role.

### 2.3 Lexing and parsing: `transpiler.py`

[`transpiler.py`](../../phase4/code/dsl/alien_syntax/src/transpiler.py) has one code path for
every lexicon; 3DOM is just the identity data.

1. **`Lexicon.of(phi)`** ([line 100](../../phase4/code/dsl/alien_syntax/src/transpiler.py#L100))
   arranges φ for a lexer: outer symbols (`$S`, the chain operator), outer words (`function`, the
   15 verbs), inner symbols (sigils, `>`, `*`) and inner words (type and pseudo keywords). A
   spelling made only of identifier characters is a **word** (lexed by maximal munch, then looked
   up); anything else is a **symbol** (matched longest first). Token **types** are role names
   (`CSIG`, `HASH`, `TYPE_MESH`, `VERB`), never spellings, so the token stream of a program and of
   its φ-image are directly comparable.
2. **`Lexer`** ([line 168](../../phase4/code/dsl/alien_syntax/src/transpiler.py#L168)) is the
   **two-level** lexer: outside quotes, layout is skipped (level 1); inside the quoted selector
   that follows `$S(`, a run of spaces is the descendant combinator and a tab is an error
   (level 2). The **seam** (level 3) is the rule that only the string right after `$S(` is a
   selector; every other string is an opaque argument, so `'#111111'` is never read as a sigil.
3. **`num_parses`** ([line 309](../../phase4/code/dsl/alien_syntax/src/transpiler.py#L309)) feeds
   that token stream to Phase 1's reference grammar ([`refgrammar.py`](../../phase4/code/dsl/grammar_and_3DOM_client/conformance/refgrammar.py)),
   whose memoized counter returns the **number of derivations**: 0 rejects, 1 is a valid program,
   2 or more would be an ambiguity (the conformance suite requires exactly 1).
4. **`parse`** ([line 752](../../phase4/code/dsl/alien_syntax/src/transpiler.py#L752)) is the
   reference recognizer: two Lark **Earley** parsers built from a grammar template with φ's
   spellings filled in (`render_slots`), the outer one for the program and the inner one for the
   selector, with `ambiguity="explicit"` so that any ambiguity raises. Lark transformers then turn
   the parse tree into the IR dataclasses.
5. **`Emitter`** ([line 793](../../phase4/code/dsl/alien_syntax/src/transpiler.py#L793)) goes the
   other way, IR → text in a lexicon. Each operation becomes its own statement,
   `entry(quote(selector))chain verb(args);`, and the program is wrapped in `(function(){ … })();`.

### 2.4 Meaning: `canonicalize.py`

[`canonicalize.py`](../../phase4/code/dsl/alien_syntax/src/canonicalize.py) defines the IR
(`Matcher`, `Step`, `Selector`, `Operation`, `IRProgram`) and rules C0–C9 (theory §2.4).
`canonical_json` ([line 378](../../phase4/code/dsl/alien_syntax/src/canonicalize.py#L378)) sorts
keys and removes spaces; `content_hash` ([line 383](../../phase4/code/dsl/alien_syntax/src/canonicalize.py#L383))
is its SHA-256. `SIGNATURES` ([line 100](../../phase4/code/dsl/alien_syntax/src/canonicalize.py#L100))
names each verb's arguments: `metalness` takes one, `metalness`; `move` takes `dx, dy, dz`.

For `t011`, in **both** families and **every** lexicon:

```text
{"grammar_version":"3dom-grammar/1.1.0","ops":[{"args":{"metalness":0.8},"op":"metalness",
 "selector":{"raw":"#panel>.frame>mesh","steps":[…]}}]}        sha256 fcdf05187d6a4e49…
```

`raw` is always rendered with 3DOM's sigils (C5), which is why the IR of the `d50s3` program, whose
text says `.panel>#frame>camera`, still says `#panel>.frame>mesh`.

**Say it aloud:** "The language library is one φ-parameterised lexer, parser and emitter; a lexicon
is validated data, and the canonical IR hash is the only notion of meaning anywhere in the code."

---

## 3. The experiment's language layer (`p4/language`)

### 3.1 The 80 templates: `templates.py`

[`build_templates`](../../phase4/code/p4/language/templates.py#L163) enumerates programs
deterministically: for 1, 2, 3 and 4 statements, it walks the 20 selector shapes of
[`selector_shapes`](../../phase4/code/p4/language/templates.py#L77) and gives each statement the
next verb in a rotating list, with fixed argument values (`VERB_VALUES`). 4 × 20 = **80
templates**, `t000`–`t079`, built as IR, never as text.

`t011` is the 12th one-statement template: shape number 11, `deep_child`
(`#panel > .frame > mesh`, an id, then a child class, then a child type), and the 12th verb of the
rotation, `metalness`, with its value `0.8`.

### 3.2 The two grammar families: `backends.py`

[`backends.py`](../../phase4/code/p4/language/backends.py) defines a `Backend` with four methods,
`lex`, `num_parses`, `parse` and `render`, and two implementations:

| | `DomBackend` ([line 190](../../phase4/code/p4/language/backends.py#L190)) | `BlkBackend` ([line 258](../../phase4/code/p4/language/backends.py#L258)) |
|---|---|---|
| `render` | the vendored `Emitter` | its own: consecutive operations on one selector share one block `$S '…' { op args; … }` |
| `parse` | the vendored Lark parser | its own outer grammar (`BLK_GRAMMAR`), with the **vendored inner selector parser and transformer** |
| `num_parses` | Phase 1's derivation counter | the Earley tree, raising on any ambiguity |
| `lex` | `scan_sites` (shared) | `scan_sites` (shared) |

Reusing the inner parser in `blk` is deliberate: the selector sub-language cannot drift between
the families, so a sigil or keyword difference between them comes from the outer grammar alone.

[`scan_sites`](../../phase4/code/p4/language/backends.py#L100) is the offset-accurate scanner both
families use to **find** decision sites (the real parsing is Lark's). The first quoted string of a
statement is a selector and is scanned with the inner tables; later strings are arguments and are
skipped. A `;` resets the statement. It yields `(token type, spelling, character offset)` for every
substitutable terminal.

### 3.3 The lexicon family: `deltafam.py`

[`deltafam.build(density, seed, mode)`](../../phase4/code/p4/language/deltafam.py#L125) makes one
lexicon:

1. list the shape-class groups: sigils {class, id}, the 4 types, the 2 pseudo keywords, and verb
   groups by signature (`strict`) or by argument count (`arity`);
2. shuffle the groups with `random.Random(seed)`;
3. take groups until the number of permuted roles reaches `density × 29`; inside each group,
   shuffle the members and give each the **next** member's spelling (a rotation);
4. copy the class sigil's new spelling onto the chain operator (invariant I7);
5. leave every other role at its 3DOM spelling.

In strict mode there are only five groups (2 + 4 + 2 + 2 + 3 = 13 roles), so a 50% target stops at
13 of 29: `d50s3` permutes all five groups. Arity mode, used at 75%, has larger verb groups and gets
the suffix `a`. [`write`](../../phase4/code/p4/language/deltafam.py#L184) saves a lexicon only if
its content changed, atomically (defect P33-011: the tests used to rewrite nine tracked files).

---

## 4. Decision sites (`p4/sites`)

### 4.1 Classifying every site: `sites2.classify`

[`classify(program, phi, backend)`](../../phase4/code/p4/sites/sites2.py#L83):

1. computes the program's own IR hash, and refuses a program that is not valid in its lexicon;
2. walks `backend.lex(program, phi)`; for each token, recovers its terminal id
   ([`_terminal_of_token`](../../phase4/code/p4/sites/sites2.py#L54)) and skips frozen terminals;
3. sets `c = phi.spelling(tid)` and `q = identity.spelling(tid)`;
4. if `c == q`: class **NONE**; otherwise builds the **variant**, the program with `q` written over
   `c` at that exact offset, and tries to hash it ([`_safe_ir_hash`](../../phase4/code/p4/sites/sites2.py#L69)):
   no hash (lexes or parses wrongly) → **LEXICAL**; the same hash → **BENIGN**; a different hash →
   **SEMANTIC**;
5. stores a `Site` with its id `family:lexicon:template:terminal:occurrence`, the offset, the
   **prefix** `program[:offset]`, both spellings, the class, and which terminal `q` names
   (`competitor_binds_to`).

The running example, `dom`:

| offset | terminal | `c` | `q` | variant | class |
|---:|---|---|---|---|---|
| 1 | `T_FUNCTION` | `function` | `function` | — | NONE |
| 13 | `T_SELECTOR_ENTRY` | `$S` | `$S` | — | NONE |
| 17 | `T_ID_SIGIL` | `.` | `#` | `$S('#panel>#frame>camera')…` | SEMANTIC (`#` names the class sigil) |
| 23 | `T_CHILD` | `>` | `>` | — | NONE |
| 24 | `T_CLASS_SIGIL` | `#` | `.` | `$S('.panel>.frame>camera')…` | SEMANTIC (`.` names the id sigil) |
| 30 | `T_CHILD` | `>` | `>` | — | NONE |
| **31** | **`T_TYPE_MESH`** | **`camera`** | **`mesh`** | **`$S('.panel>#frame>mesh')…`** | **SEMANTIC** (`mesh` names `T_TYPE_GROUP`) |
| 39 | `T_CHAIN_OP` | `#` | `.` | `…camera').metalness(0.8)…` | LEXICAL (0 derivations) |
| 40 | `T_VERB_METALNESS` | `metalness` | `metalness` | — | NONE |

In `blk` the same program has no `function` and no chain operator, and the inner sites sit earlier:
the id sigil at offset 4, the class sigil at 11 and the type keyword at **18**, all SEMANTIC.

[`stratum(site)`](../../phase4/code/p4/sites/sites2.py#L170) assigns `sigil`, `keyword` (types
and pseudo keywords) or `verb`.

### 4.2 One site per prefix: `sampling.dedupe_within_cells`

[`dedupe_within_cells`](../../phase4/code/p4/sites/sampling.py#L82) sorts every SEMANTIC site by
the **canonical key** `(family, lexicon, template, terminal, occurrence, offset)` and keeps the
first site of each `(family, lexicon, prefix)`. Sorting first makes the result independent of input
order (defect P33-003: reversing the lexicon list on the command line used to move hundreds of
sites). Each dropped site is recorded with the id it duplicates.

`dom:d50s3:t011:T_ID_SIGIL:0` has the prefix `(function(){ $S('`, shared by the first selector
symbol of every `dom` program, so it is dropped: in `d50s3` that prefix belongs to `t000`'s first
site. Its class-sigil and keyword sites survive. Over the held-out materials: 4,700 SEMANTIC sites,
1,670 dropped, **3,030 kept** (1,515 per family).

### 4.3 Balanced sampling: `sampling.balanced`

[`balanced(sites, limit)`](../../phase4/code/p4/sites/sampling.py#L121) deals sites out
round-robin across the cells `(family, lexicon, stratum)` in sorted order, so a limit keeps every
cell's share instead of truncating whichever came first (defect P32-003 once scored 240 `dom` sites
and no `blk` site while reporting both). `limit=0` means every site. Arm A uses every site; the
ladder uses `primary.site_limit = 400`. [`assert_balanced`](../../phase4/code/p4/sites/sampling.py#L173)
then refuses a sample that misses any cell the materials offer (P33-004).

---

## 5. Prompts and worked examples (`p4/prompts`)

### 5.1 The token table and its controls: `prompts.py`

| function | line | output for `d50s3` (Qwen tokenizer) |
|---|---:|---|
| `rule_prompt` | [93](../../phase4/code/p4/prompts/prompts.py#L93) | preamble + `TOKEN TABLE` + 28 lines `label  spelling` + closer: 1,527 characters, 298 tokens |
| `norule_prompt` | [107](../../phase4/code/p4/prompts/prompts.py#L107) | the same framing, `ROLE LIST` with the 28 labels, no spellings: 1,014 characters, 237 tokens |
| `norule_lenmatched` | [235](../../phase4/code/p4/prompts/prompts.py#L235) | `norule` plus copies of a neutral line until it has at least the rule prompt's token count **in the scoring model's tokenizer**: 7 lines, 307 tokens |
| `paraphrase(phi, "p0"/"p1"/"p2")` | [173](../../phase4/code/p4/prompts/prompts.py#L173) | the same table under three framings: p0 is the rule prompt itself (298 tokens), p1 terse (251), p2 explicit about the conflict (333) |

The table lines come from `ROLE_LABEL` ([line 61](../../phase4/code/p4/prompts/prompts.py#L61))
and `phi.spelling`: the table is **rendered from the lexicon**, so it cannot disagree with the
grammar. The neutral line is `  (this line intentionally carries no token information)`, 10 Qwen
tokens; whole lines are added, so the control can overshoot the target by up to one line (307 for
298).

[`bundle(condition, phi)`](../../phase4/code/p4/prompts/prompts.py#L254) is the only constructor
the runners use; it returns a `PromptBundle` that remembers its lexicon and its SHA-256.
[`assert_prompt_matches(site, phi, bundle)`](../../phase4/code/p4/prompts/prompts.py#L271) then
refuses a site from another lexicon, a prompt rendered for another lexicon (defect P33-006), a site
whose correct spelling disagrees with φ, and a table that does not literally state the site's
mapping.

### 5.2 Worked examples: `demos.py`

| function | line | what it does |
|---|---:|---|
| `pool_order(ids, seed, salt)` | [59](../../phase4/code/p4/prompts/demos.py#L59) | sorts the 80 template ids and shuffles them with `random.Random(f"{seed}:{salt}")`; the salt is `dom/d50s3` for the ladder and `armb/dom/d50s3` for Arm B |
| `common_opening(rendered)` | [67](../../phase4/code/p4/prompts/demos.py#L67) | the prefix shared by every rendered program: `(function(){ $S('` in `dom`, `$S '` in `blk` |
| `is_leak(site, id, text)` | [74](../../phase4/code/p4/prompts/demos.py#L74) | `same_template`, `identical_program`, or `replays_decision_prefix` (the example starts with the site's prefix, and that prefix is longer than the common opening) |
| `for_site(site, rendered, order, n)` | [86](../../phase4/code/p4/prompts/demos.py#L86) | the first `n` non-leaking examples in pool order; raises if fewer exist |

For `dom:d50s3:t011:T_TYPE_MESH:0`, the pool order skips `t071`, `t031` and `t051`
(`replays_decision_prefix`: they begin `(function(){ $S('.panel>#frame>…`) and `t011` itself. The
first eight examples are `t024, t049, t019, t015, t017, t063, t057, t014`; the first one is
`(function(){ $S(':lasso')#receiveShadow(1); $S('mesh#bus')#wireframe(0); })();`.

### 5.3 Putting a context together: `build_prefix`

[`build_prefix(site, rule, shots, examples)`](../../phase4/code/p4/scoring/margins.py#L332)
builds the exact text handed to the scorer:

```text
<prompt, trailing whitespace removed>\n\n
<example 1>\n<example 2>\n … <example k>\n      (only when k > 0)
\n                                              (only when k > 0)
<site.prefix>
```

For Arm A with the rule prompt, the context ends like this (`⏎` marks a line break):

```text
dom   …Write 3DOM using exactly the spellings above.⏎⏎(function(){ $S('.panel>#frame>
blk   …Write 3DOM using exactly the spellings above.⏎⏎$S '.panel>#frame>
```

---

## 6. The scorer (`p4/scoring`)

### 6.1 Validating a pair: `check_pair`

[`check_pair(ids_c, ids_q)`](../../phase4/code/p4/scoring/margins.py#L137) takes the token ids of
`prefix + c` and `prefix + q`, finds `k`, the length of their common prefix, and **raises** instead
of returning a number in three cases: identical tokenizations (`IdenticalCandidates`), one side
being a prefix of the other so that it would be scored over zero tokens (`ZeroLengthSpan`, the
P33-001 failure), and divergence at the very first token (`NoContext`). It is separate from the
model so the tests can exercise it without weights.

### 6.2 Scoring a pair: `TokenScorer.score_pair_detailed`

[`score_pair_detailed(prefix, c, q)`](../../phase4/code/p4/scoring/margins.py#L258):

1. `a = ids(prefix + c)`, `b = ids(prefix + q)` (no special tokens), `k = check_pair(a, b)`;
2. one forward pass over `a[:k]` gives the log-softmax row **predicting position `k`**; it is shared
   by both candidates;
3. a side with one divergent token reads its log-probability from that row; a longer side gets one
   more pass over its own tokens and sums `log P(a_j | a_<j)` for `j ≥ k`;
4. it returns a `PairScore`: both log-likelihoods, `k`, the tail lengths, `merged` (the candidate
   fused with the prefix's last token), the prefix's own token count, the first divergent tokens
   as strings, and whether the fp32 head was used. `m_seq` is `logp_correct − logp_competitor`.

**The fp32 head** ([`_logprobs_rows`](../../phase4/code/p4/scoring/margins.py#L237)): the model
body runs in bf16, but the last projection to the vocabulary is recomputed in float32 from the
decoder's final hidden state, so a margin near zero is not decided by bf16 rounding (P33-002). It
is disabled, with a recorded note, for models that transform their logits after the head.

**The running example** (held-out, Qwen2.5-Coder-0.5B, `rule`): `k = 307` in `dom`, 305 in `blk`;
one token per side (`camera`, `mesh`); not merged. The class-sigil site of the same program is
merged: its first divergent tokens are `>#` and `>.`.

Two more methods serve other experiments:
[`program_nll(text)`](../../phase4/code/p4/scoring/margins.py#L290) (H4's whole-program baseline:
the summed negative log-probability of every token after the first, also per character) and
[`generate(prompt)`](../../phase4/code/p4/scoring/margins.py#L308) (Arm B: greedy decoding,
`do_sample=False`, `num_beams=1`, at most 192 new tokens, special tokens skipped in the output).

### 6.3 Loading a model: `scorers.load_scorer`

[`load_scorer`](../../phase4/code/p4/scoring/scorers.py) resolves the model's **pinned** snapshot
offline (`local_files_only=True`, the pinned `allow_patterns`), refuses if the snapshot is not the
pinned commit, loads the `TokenScorer` (sharded over two GPUs for the 72B pair), and attaches
`revision`, `snapshot_path` and `tokenizer_id` (a hash of the tokenizer files). The runner checks
`scorer.revision` against the pin again before scoring.

### 6.4 Served models: `api.APIScorer`

[`APIScorer`](../../phase4/code/p4/scoring/api.py#L66) has the same interface. For a pair it
sends three requests at once to `/v1/completions`: `prefix + c` and `prefix + q` with
`prompt_logprobs=0` (each token's log-probability given the ones before it), and the prefix alone
for its token count. Then the same `check_pair` and the same sums
([line 165](../../phase4/code/p4/scoring/api.py#L165)). Every answer is checked against the pinned
deployment (`"<served name>@<system fingerprint>"`); any other raises `ServedModelChanged`. The key
is read by [`asu_api.load_key`](../../phase4/code/p4/runtime/asu_api.py) from the environment or a
private file and goes only into the request header.

### 6.5 The fake scorer and fertility

[`fakes.FakeScorer`](../../phase4/code/p4/scoring/fakes.py) lets the whole pipeline run without a
GPU: a BPE-like vocabulary that really merges `('` with a sigil (so the P32-001 path is exercised),
a planted habit that the table reduces and examples extinguish, and deterministic SHA-256 "noise".
The end-to-end test checks that the analyses **recover** the planted effects.
[`fertility.py`](../../phase4/code/p4/scoring/fertility.py) counts tokens per character for every
distinct tokenizer, family and lexicon (defect P33-009: it used to measure only the first model).

---

## 7. The plan and the cells (`p4/experiments/pipeline.py`)

### 7.1 `build_plan`: from config to sites

[`build_plan(cfg, site_limit)`](../../phase4/code/p4/experiments/pipeline.py#L103), in order:

1. **`splits.enforce_config`** — every (family, lexicon, model) cell of the config is checked
   against the registered split **before** anything is enumerated
   ([`splits.py:181`](../../phase4/code/p4/governance/splits.py#L181)); a held-out cell needs a valid
   unlock;
2. for each family and lexicon: render all 80 templates, `classify` each, keep the SEMANTIC sites,
   and keep the rendered texts (the example pool);
3. `dedupe_within_cells`, then `balanced(kept, site_limit)` and `assert_balanced`;
4. group the chosen sites by (family, lexicon) in canonical order.

The plan is written to `manifests/plan_<experiment>.json`; a later run that recomputes a different
plan refuses ("the materials changed under an existing run").

### 7.2 Cells, the unit of work and of storage

A **cell** ([`_cells`](../../phase4/code/p4/experiments/pipeline.py#L165)) is one experiment ×
model × revision × family × lexicon × condition × chunk of at most 64 sites. Its key is a readable
prefix plus a hash of all its fields ([`shards.cell_key`](../../phase4/code/p4/runtime/shards.py#L46)),
so a cell scored under another configuration can never be mistaken for this one.

| experiment | conditions per (family, lexicon) | sites per cell | cells per model (held-out materials) |
|---|---|---|---:|
| Arm A | `rule`, `norule`, `norule_lenmatched` | chunks of the cell's sites (220, 272 or 341) | 162 |
| primary | `ladder`, `p0`, `p1`, `p2` | the 400-site subset, about 40 per (family, lexicon) | 40 |
| Arm B | `generate` | templates with a site (74–80), in chunks | 20 |
| H5 | 7 arms (targeted, random 1–5, global) | as Arm A | 378 |

Experiments register themselves ([`register`](../../phase4/code/p4/experiments/pipeline.py#L210))
with a cell builder, a scoring function and a model filter: Arm B and H5 apply only to instruct
models, and H5 only to instruct models with a base twin.

### 7.3 `run`: the loop

[`run(cfg, run_dir, experiment)`](../../phase4/code/p4/experiments/pipeline.py#L362) builds the
plan, opens the shard store, starts a job manifest (status `RUNNING`), and then, for each model
assigned to this task (task *i* → model *i* of the config):

1. lists the model's cells and keeps those not `done` (a corrupt one is quarantined first);
2. loads the scorer **once** and refuses if its revision is not the pinned one;
3. scores each pending cell and writes it atomically with its done-marker; a failing cell (an OOM,
   say) is recorded and the run becomes `PARTIAL`, the others continue;
4. releases the GPU memory before the next model.

A stop signal (SIGTERM, SIGUSR1 from Slurm before the time limit, SIGINT) only sets a flag; the loop
stops between sites, the cell in progress is abandoned, and the manifest ends `INTERRUPTED`.
Served models score several cells side by side
([`_score_cells_side_by_side`](../../phase4/code/p4/experiments/pipeline.py#L443)), because they
wait on the network, not on a GPU.

### 7.4 What every row carries

[`_base_row`](../../phase4/code/p4/experiments/pipeline.py#L229) stamps every row with the run,
stage and **split label**, the cell key, the model, its kind, family and size, its **revision**
and **tokenizer id**, the dtype, the site's family, lexicon, template, id, terminal, role,
stratum, occurrence and offset, both spellings, the condition, and the prompt's SHA-256 and
length. [`_score_into`](../../phase4/code/p4/experiments/pipeline.py#L250) adds the `PairScore`, or,
when the scorer refuses, `status: excluded` with the reason and **no margin**: never a silent 0.

---

## 8. Arm A, step by step

[`score_arm_a_cell`](../../phase4/code/p4/experiments/pipeline.py#L275), for each site of the cell:

1. `L = phi(site.phi_id)` — the lexicon **of this site** (P33-006);
2. `pb = prompts.bundle(condition, L, count_tokens=…)` — the rule prompt, the no-rule control or the
   length-matched control, the last counted in this model's tokens;
3. `assert_prompt_matches(site, L, pb)`;
4. `prefix = build_prefix(site, rule=pb.text)`;
5. the row: `_base_row`, `prompt_tokens`, `row_key = cell|site`, then `_score_into`;
6. the whole-program NLL of `site.program`, cached per program, added to every row.

**The held-out rows of the running site** (Qwen2.5-Coder-0.5B, base):

| family | condition | `logp_correct` | `logp_competitor` | `m_seq` | `k_common` | `prompt_tokens` |
|---|---|---:|---:|---:|---:|---:|
| `dom` | `rule` | −6.0821 | −1.5700 | −4.5121 | 307 | 298 |
| `dom` | `norule` | −8.5602 | −3.4574 | −5.1028 | 246 | 237 |
| `dom` | `norule_lenmatched` | −8.2749 | −2.8469 | −5.4280 | 316 | 307 |
| `blk` | `rule` | −6.3450 | −2.5901 | −3.7548 | 305 | 298 |
| `blk` | `norule` | −7.2571 | −2.5890 | −4.6681 | 244 | 237 |
| `blk` | `norule_lenmatched` | −8.0005 | −2.7419 | −5.2585 | 314 | 307 |

In every row `k_common − prompt_tokens` is the program prefix: 9 tokens in `dom`, 7 in `blk`. Each
row also carries `first_div_correct = 'camera'`, `first_div_competitor = 'mesh'`,
`n_tok_correct = n_tok_competitor = 1`, `merged = False`, `fp32_head = True` and
`program_nll_per_char` (1.942 in `dom`, 2.298 in `blk`).

**Say it aloud:** "Arm A renders the site's own lexicon's prompt, checks it states the site's
mapping, prepends it to the program prefix, and scores both spellings from their first divergent
token; three conditions, one row each, never a silent zero."

---

## 9. The ladder and the paraphrases, step by step

### 9.1 Which sites

[`primary_site_source`](../../phase4/code/p4/experiments/pipeline.py#L184) takes the plan's sites
and draws `balanced(…, 400)`: 400 sites per model, spread over the 30 cells (2 families × 5
lexicons × 3 strata). The running site is one of them in both families.

### 9.2 `score_primary_cell`

[`score_primary_cell`](../../phase4/code/p4/experiments/pipeline.py#L300) handles two kinds of
cell:

- **`ladder`**: the rule prompt; `demos = for_site(site, rendered, order, 32)` once per site, with
  the pool order salted `family/lexicon`; an `audit` that raises on any leak; then for each rung
  `k` in `0, 1, 2, 4, 8, 16, 32`, the context `build_prefix(site, rule, shots=k,
  examples=demos[:k])` and one scored row carrying `rung`, the exact `demo_ids`, the demo-set hash,
  the pool-order hash and the seed. Because each rung takes the first `k` of the **same** 32
  examples, the ladder is nested.
- **`p0`, `p1`, `p2`**: one row per site with the paraphrased prompt and no examples
  (`kind = paraphrase`, `rung = 0`).

So each ladder site yields 7 + 3 = 10 rows per model: 4,000 rows per model.

**The running site's rows** (held-out, Qwen2.5-Coder-0.5B):

| rung | 0 | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `dom` `m_seq` | −4.512 | −3.492 | +2.606 | +1.798 | +2.309 | +2.792 | +4.909 |
| `blk` `m_seq` | −3.755 | −2.710 | −2.944 | −3.971 | −4.053 | +4.154 | +4.796 |

Rung 0 is not Arm A's `rule` row re-used: it is scored again, in another job, from the same prompt
and prefix, and gives the same value to the printed precision.

---

## 10. Arm B, step by step

[`armb.py`](../../phase4/code/p4/experiments/armb.py): the unit is a **template**, not a site.

### 10.1 The request: `describe_program`

[`describe_program(ir)`](../../phase4/code/p4/experiments/armb.py#L105) renders the IR in plain
English, deterministically: matchers become phrases (`objects of class 'frame'`, `meshes`), child
steps become `directly inside`, descendants `anywhere inside`, and each verb has a sentence
pattern. `t011` becomes *"Set the metalness of meshes directly inside objects of class 'frame'
directly inside the object with id 'panel' to 0.8."* The request names roles in English (`meshes`),
never in the lexicon's spellings.

### 10.2 The prompt: `build_prompt`

[`build_prompt(table, demos, requests, request)`](../../phase4/code/p4/experiments/armb.py#L123)
writes: the rule prompt; the instruction *"Write exactly one 3DOM program for the request, on one
line, using the spellings in the table."*; `EXAMPLES`; four `Request: …` / `Program: …` pairs; and
the target's `Request:` with an open `Program:`. The four examples come from
`for_site(anchor, …)`, where the anchor is the template's first site and the template itself is
removed from the pool; the pool order is salted `armb/family/lexicon`. For `dom` × `d50s3` × `t011`
the examples are `t055, t004, t008, t037`, and the prompt's SHA-256 begins `dfddd2cf`.

### 10.3 Generate, extract, evaluate, observe

[`score_armb_cell`](../../phase4/code/p4/experiments/armb.py#L238), for each template:

1. `raw = scorer.generate(prompt, max_new_tokens=192)` (greedy);
2. [`extract_program(raw)`](../../phase4/code/p4/experiments/armb.py#L132): the first non-empty line,
   with code fences and a `Program:` label removed, skipping lines that start `Request:`;
3. [`evaluate(text, backend, phi, target_hash)`](../../phase4/code/p4/experiments/armb.py#L159):
   empty → `LEX_FAIL`; not exactly one derivation → `PARSE_FAIL` (a text that does not even lex
   lands here too, because the derivation counter returns 0 for it); a lexing error raised by the
   parser itself → `LEX_FAIL`; a valid program with no operations → `VALID_VACUOUS`; otherwise
   `VALID_CORRECT` if its IR hash is the target's, else `VALID_WRONG`. In the held-out run the
   7,800 programs split into 4,047 `VALID_WRONG`, 3,006 `PARSE_FAIL` and 747 `VALID_CORRECT`, with
   no `LEX_FAIL` and no `VALID_VACUOUS`;
4. [`observe(text, site)`](../../phase4/code/p4/experiments/armb.py#L179) for every site of the
   template in the plan: remove whitespace outside quotes from both the output and the site's
   prefix ([`normalize_layout`](../../phase4/code/p4/experiments/armb.py#L143)); if the output does
   not start with the prefix, `not_reached`; otherwise compare what follows with the correct and the
   familiar spelling, longer first: `correct`, `reverted` or `other`;
5. one row per template: the request, the prompt and demo hashes, the decoding settings, the raw
   output, the extracted program, the target, the bucket, and the list of site observations.

[`hurdle(obs)`](../../phase4/code/p4/experiments/armb.py#L194) then counts, per cell and stratum:
sites, reached, reverted, `p_reach`, `p_revert_given_reach`, and the product, **reported alongside,
never instead**.

### 10.4 The running template in both families

| family | model | extracted | bucket | class-sigil site | keyword site |
|---|---|---|---|---|---|
| `blk` | Qwen2.5-Coder-1.5B-Instruct | `$S '.panel>#frame>mesh' { metalness 0.8; }` | `VALID_WRONG` | reached, `#`: correct | reached, `mesh`: **reverted** |
| `blk` | DeepSeek-Coder-33B-Instruct | `$S '.panel>#frame>camera' { metalness 0.8; }` | `VALID_CORRECT` | correct | correct |
| `blk` | Qwen2.5-72B-Instruct | `$S '.panel>#frame>camera' { metalness 0.8; } Request: First, set …` | `PARSE_FAIL` | correct | correct |
| `dom` | Qwen2.5-Coder-1.5B-Instruct | `(function(){ $S('#panel>.frame')#metalness(0.8); })();` | `VALID_WRONG` | not reached | not reached |
| `dom` | Qwen2.5-72B-Instruct | `(function(){ $S('#panel>camera.frame')#metalness(0.8); })();` | `VALID_WRONG` | not reached | not reached |

The 72B row in `blk` shows the extraction artifact corrected post hoc by D13 (item F5): the model
wrote the correct program, then continued **on the same line** with `Request: …`, which the
extractor kept, so the program failed to parse; with the cut, this generation is `VALID_CORRECT`.
Cutting at a same-line `Request:` changed 63 of
7,800 generations and raised task accuracy from 9.6% to 9.9%, without changing any site outcome
(the site observations only read the text up to the site). In `dom`, both models wrote `#panel`:
the familiar id sigil at the first selector symbol, a decision kept for another template only, so
it shows up here as "not reached".

**Say it aloud:** "Arm B turns the IR into an English request, asks for one program with four
leak-free examples, grades the program by its IR hash, and observes each site as reached or not,
then correct or reverted."

---

## 11. H5, step by step

[`h5.py`](../../phase4/code/p4/experiments/h5.py) runs in two stages: `prepare` once per run (it
needs the merged Arm A), then cells scored like Arm A, under repaired lexicons.

### 11.1 Candidate roles and base-model risk

[`remapped_roles(L)`](../../phase4/code/p4/experiments/h5.py#L64) lists the roles whose spelling
differs from 3DOM, leaving out the chain operator, which follows the class sigil: 13 roles for
`d50s3`. [`prepare`](../../phase4/code/p4/experiments/h5.py#L125) reads the merged Arm A rows and,
for every (family, lexicon, **base** model, terminal), averages the risk $-M$ over the `rule`
rows. For `d50s3`, Qwen2.5-Coder-0.5B, the ranking is:

| rank | `dom` | mean risk | `blk` | mean risk |
|---:|---|---:|---|---:|
| 1 | `T_PSEUDO_SELECTED` (7 sites) | +6.27 | `T_PSEUDO_SELECTED` | +4.95 |
| 2 | `T_VERB_CASTSHADOW` (12) | +2.48 | `T_VERB_CASTSHADOW` | +2.51 |
| 3 | `T_ID_SIGIL` (46) | +1.33 | `T_VERB_MOVE` | +0.96 |
| 4 | `T_TYPE_MESH` (21) | +1.17 | `T_TYPE_MESH` | +0.85 |
| 5 | `T_VERB_MOVE` (10) | +1.06 | `T_ID_SIGIL` | +0.73 |
| … | … | … | … | … |
| 13 | `T_PSEUDO_LASSO` (6) | −6.34 | `T_PSEUDO_LASSO` | −6.15 |

The mean is over every site of the role in the cell, so a role with 7 sites counts as much as one
with 105.

### 11.2 The arms: `define_arms`

[`define_arms(L, risk_by_role, budget=3, seeds=[1..5])`](../../phase4/code/p4/experiments/h5.py#L113)
returns seven arms: **targeted**, the 3 highest-risk roles (ties broken by id); **random**, 3 roles
drawn by `random.Random(seed).sample` for seeds 1–5; **global**, all 13. The instruct model's arms
use its **base twin's** risk. For the 0.5B instruct model: targeted `dom` = id sigil, `selected`,
`castShadow`; targeted `blk` = `selected`, `castShadow`, `move`. The random arms depend only on the
lexicon and the seed, so every model and family shares them.

### 11.3 The repaired lexicon and its proof

[`repaired_phi(base_pid, roles, tag)`](../../phase4/code/p4/experiments/h5.py#L71) copies the
lexicon's JSON, gives each chosen role its `beta` spelling (and the chain operator too, when the
class sigil is chosen), names the result `<lexicon>__<tag>`, validates it (V1–V8), and stores it in
the pipeline's lexicon cache under that name. `beta`'s spellings include `%` (id sigil), `~` (class
sigil), `plel` (mesh), `taltazat` (`selected`), `brom` (`move`) and `blisVetbis` (`castShadow`).

[`ir_proof(L, L2)`](../../phase4/code/p4/experiments/h5.py#L92) then renders and re-parses every
program of the proof corpus (the 62 Phase 1 conformance programs plus the 80 templates) in both
families under the original and the repaired lexicon, and requires the three hashes (original IR,
original lexicon, repaired lexicon) to agree: 284 checks, no sampling, no tolerance.

`prepare` writes the arms and proofs to `manifests/h5_arms.json`; a resumed run must re-derive
exactly the same file, or it refuses.

### 11.4 Scoring: `score_h5_cell`

[`score_h5_cell`](../../phase4/code/p4/experiments/h5.py#L200) looks up the repaired lexicon by
name, and for each site of the cell:

1. renders the site's template under the repaired lexicon and re-classifies it;
2. finds the same (terminal, occurrence) again; if it vanished or now has no contrast, the row is
   `excluded`;
3. otherwise scores it with the repaired rule prompt (after `assert_prompt_matches`) and records
   `collision_after`, the new spellings, `m_seq`, `reverted_after`, and `silent_error_after`
   (reverted **and** still SEMANTIC);
4. labels the row `repaired_role = terminal in roles`.

**The running site, Qwen2.5-Coder-0.5B-Instruct, `dom`** (before any repair, Arm A gave
$M=-0.638$):

| arm | roles changed | `repaired_role` | spellings after | class after | $M$ after |
|---|---|---|---|---|---:|
| targeted | id sigil, `selected`, `castShadow` | no | `camera` / `mesh` | SEMANTIC | −1.005 |
| random 1 | id sigil, `lasso`, `duplicate` | no | `camera` / `mesh` | SEMANTIC | −1.347 |
| random 5 | `camera`, `group`, `duplicate` | no | `camera` / `mesh` | **LEXICAL** | **+0.131** |
| global | all 13 | yes | `plel` / `mesh` | LEXICAL | −3.100 |

Random 5 did not touch `T_TYPE_MESH`, but it respelled `T_TYPE_GROUP`, the role whose spelling was
`mesh`; so `mesh` now names nothing, the site's error became loud, and this model's margin turned
positive. The global arm respelled the site's own role to `plel`; the model still prefers the
meaningless `mesh` by 3.1 nats, a reversion that would now fail to parse.

### 11.5 From rows to the H5 numbers: the export

[`export.py:362`](../../phase4/code/p4/reporting/export.py#L362) groups the H5 rows by (model,
family, lexicon, arm, seed), keeps the sites that are `ok` and also have the instruct model's Arm A
`rule` row, and splits them by `repaired_role`:

```text
rb(rows) = # rows whose Arm A margin (before) < 0        ra(rows) = # rows with reverted_after
error_reduction_per_changed_symbol = (rb(all) − ra(all)) / n_changed
control_degradation = ra(control)/n_control − rb(control)/n_control
```

`n_changed` is the number of intended roles (3, or 13 for global). The registered test, the split
into repaired and control parts, and their values are in
[`experiment_math.md` §15.2](experiment_math.md#152-h5-benefit-per-changed-role).

### 11.6 A defect found on 2026-10-28: the targeted arm scored the wrong lexicon

**What the code does.** In `prepare`, the loop is

```python
for fam in sorted(cfg.families):          # blk, dom
    for lx in sorted(cfg.lexicons):
        for inst in sorted(cfg.models):   # all 21, base and instruct, alphabetically
            for arm, sd, roles in define_arms(L, rbr, …):
                tag = f"h5_{arm}_{sd}"                 # "h5_targeted_0" for every model
                L2 = repaired_phi(lx, roles, tag)      # named f"{lx}__{tag}"; cached by name
```

and `repaired_phi` ends with ([`h5.py:78–80`](../../phase4/code/p4/experiments/h5.py#L78); the frozen
original is [`p33/h5.py`](../../phase3_2/sol/src/p33/h5.py#L78), the same lines):

```python
blob["phi_id"] = f"{base_pid}__{tag}"
L2 = P.validate_phi(blob, P.load_terminals())
PL._PHI_CACHE[L2.phi_id] = L2
```

The name depends on the lexicon and the tag only, **not on the family or the model**. Every
targeted repair of a lexicon is stored under the same key, each overwriting the previous one. The
loop ends with family `dom` and model `meta-llama/Llama-3.2-1B-Instruct` (lowercase names sort
after `Qwen/…`), so the cache keeps **Llama's `dom` targeted repair** for each lexicon.
`score_h5_cell` then fetches the lexicon by name, `PL.phi(cell.fields["repaired_phi"])`, and every
cell of that lexicon is scored under Llama's repair. The labels do not follow: `roles` and
`repaired_role` come from each cell's own intended roles, and `n_changed` too. The proof is not
re-checked either: it is computed only for the first `(lexicon, tag)` it meets (`blk` ×
Qwen2.5-72B), and that role set differs from the scored one in 4 of 5 lexicons. (Each scored
lexicon is nonetheless a valid repair: re-proved on 2026-10-28, 284 checks, no mismatch.)

**The evidence is in the run's own rows.** For `d50s3` × Qwen2.5-Coder-0.5B-Instruct, the
spelling each targeted row was actually scored with, against its label:

| family | terminal | labelled repaired? | scored spelling | so it really was |
|---|---|---|---|---|
| `dom` | `T_ID_SIGIL` | yes | `%` (beta) | repaired ✓ |
| `dom` | `T_PSEUDO_SELECTED` | yes | `taltazat` (beta) | repaired ✓ |
| `dom` | `T_VERB_CASTSHADOW` | yes | `blisVetbis` (beta) | repaired ✓ |
| `blk` | `T_ID_SIGIL` | **no** | `%` (beta) | **repaired** |
| `blk` | `T_VERB_MOVE` | **yes** | `duplicate` (the `d50s3` spelling) | **not repaired** |
| `blk` | `T_PSEUDO_SELECTED`, `T_VERB_CASTSHADOW` | yes | `taltazat`, `blisVetbis` | repaired ✓ |

In `dom` the intended roles happen to equal Llama's; in `blk` they do not.

**How far it reaches.** Over the 100 instruct cells (10 models × 2 families × 5 lexicons), the
intended and scored role sets agree in all three roles in 16 cells, two in 29, one in 48, none in
7. In the 16 cells scored as designed, targeted beats the random mean in 14 (mean
$\Delta\eta=+2.83$); in the other 84, in 29 (mean $-1.02$); together, 43 of 100 and $-0.41$, the
reported result. The random and global arms are correct: their role sets depend only on the lexicon and the
seed, so the shared name points to the right content. D13's repaired/control split (F4) inherits
the wrong labels in the same 84 targeted cells.

**What it means, and what is not claimed.** The registered H5 test compared a mixture of the
designed comparison (16 cells) and an unintended one (84), so it did not test H5 as designed. The
16 cells are not a random sample, so their favourable numbers are not evidence for H5 either.

**The fix, not applied** (the frozen code and its registered numbers change only by the
investigator's decision and a dated deviation):

1. name each repair by everything that determines it, for example
   `f"{lx}__{fam}__{model}__{tag}"`, or by a hash of the role set;
2. key the proofs by the role set, so every scored lexicon is proved;
3. score the 100 targeted cells again (about one seventh of H5's compute), keeping the random and
   global rows;
4. apply the registered test, and report it under a new dated deviation.

A regression test is easy to write: two models with different targeted roles in one lexicon must
be scored with different spellings at the role they disagree on.

---

## 12. From rows to numbers: the bootstrap and the rule effect

### 12.1 `cluster_bootstrap`

[`cluster_bootstrap(rows, stat, unit="template", B=2000, seed=20261002)`](../../phase4/code/p4/analysis/analysis.py#L103):

1. group the rows by `template`; refuse (return `None`) below 8 clusters;
2. compute the statistic on all rows: the point estimate;
3. 2,000 times: draw as many templates as there are, with replacement; collect their rows, each
   copy tagged with its draw position `_draw` ([`_draw_rows`](../../phase4/code/p4/analysis/analysis.py#L87));
   recompute the statistic, skipping a replicate where it is undefined;
4. refuse if fewer than 1,000 replicates were usable; sort; `lo = draws[int(0.025·n)]`,
   `hi = draws[int(0.975·n)]` (indexes 50 and 1950 when all 2,000 are usable).

The `_draw` tag is defect P33-005's fix: a statistic that pairs rows by `site_id` used to collapse a
template drawn twice into one copy.

### 12.2 The rule effect and the reversion rate in the export

[`export.py:191`](../../phase4/code/p4/reporting/export.py#L191), for each (model, family,
lexicon) and each stratum (`ALL` first):

- **reversion**: [`reversion_rate`](../../phase4/code/p4/analysis/analysis.py#L172) of the `rule`
  rows, with its template interval;
- **rule effect**, for each control: relabel the control rows `norule`, then
  [`paired_rule_effect`](../../phase4/code/p4/analysis/analysis.py#L176), the mean over (draw,
  site) of $M_{\mathrm{rule}} - M_{\mathrm{control}}$, with its interval; also the median and the
  share of sites the table helped.

Families are never pooled. The model summaries in the papers (the mean of the five lexicons'
effects) are computed by the figure scripts from these rows.

### 12.3 Holm and the bootstrap p

[`bootstrap_pvalue_greater(draws)`](../../phase4/code/p4/analysis/analysis.py#L148) is
$(1+\#\{d\le0\})/(n+1)$; [`holm(p)`](../../phase4/code/p4/analysis/analysis.py#L154) sorts, multiplies
by $m, m-1, \ldots$, caps at 1 and carries the running maximum.

---

## 13. `k*` and Kaplan–Meier

### 13.1 `kstar.compute`

[`compute(ladder, margins)`](../../phase4/code/p4/analysis/kstar.py#L74) returns a `KStar`:

| field | the running site, `dom` | `blk` |
|---|---|---|
| `k_star` | 1.5727 (between rungs 1 and 2) | 11.951 (between 8 and 16) |
| `already_correct` | False | False |
| `censored` | False | False |
| `n_up_crossings` / `n_down_crossings` | 1 / 0 | 1 / 0 |
| `nonmonotone` | True (2.606 → 1.798) | True (−2.710 → −2.944) |
| `recrossed_down` | False | False |
| `sustained_k` | 2 | 16 |

The rules: $M(0)\ge0$ gives `k_star = 0`; otherwise the first `y0 < 0 <= y1`, interpolated; no
crossing gives `censored = True` and no `k_star` (defect P33-007 had censored curves with a `k*`,
and already-correct sites with none).

### 13.2 `kaplan_meier`

[`kaplan_meier(times, events)`](../../phase4/code/p4/analysis/kstar.py#L124) sorts by time (events
before censorings at the same time), walks the distinct times, multiplies `s *= 1 − d/n_at_risk`
at each event time, records the median at the first `s <= 0.5`, and removes events and censorings
from the risk set. [`km_from_kstars`](../../phase4/code/p4/analysis/kstar.py#L152) turns `KStar`s
into times (censored → the top rung, 32) and events, for **ALL_SITES** or **INITIALLY_WRONG**. The
floating-point product is where the trap of
[`experiment_math.md` §10.10](experiment_math.md#1010-a-floating-point-trap-in-the-median) lives:
line 143, `s *= (1 - d / n_at_risk)`, and line 145, `s <= 0.5`.

### 13.3 In the export

[`export.py:254`](../../phase4/code/p4/reporting/export.py#L254) builds one curve per (model,
site), drops a curve with any unmeasurable rung (status `excluded`, never a censoring), computes
`KStar`, then per (model, family): both Kaplan–Meier summaries with template intervals, the
diagnostic median among crossers, and the curve-shape shares.

---

## 14. H4, step by step

### 14.1 The table: `build_table`

[`build_table(arm_a_rows)`](../../phase4/code/p4/analysis/h4.py#L302) keeps the `rule` rows with
status `ok`, finds the registered base/instruct pairs present ([`pairs_present`](../../phase4/code/p4/analysis/h4.py#L291)),
joins base and instruct rows on `site_id`, and writes one row per (pair, site):

| column | definition | the running site, 0.5B pair, `dom` |
|---|---|---|
| `risk` | $-M$ of the base model | +4.5121 |
| `label` | 1 if the instruct model's $M<0$ | 1 |
| `identity` | 1 if $c\ne q$ (always, on SEMANTIC sites) | 1 |
| `length` | bytes of $q$ − bytes of $c$ | 4 − 6 = −2 |
| `program_nll` | base model's NLL per character | 1.942 |
| `token_count` | tail tokens of both candidates | 1 + 1 = 2 |
| `terminal_rate` | exploratory, below | 0.208 |

[`_crossfit_terminal_rate`](../../phase4/code/p4/analysis/h4.py#L334) scores each site by the
reversion rate of its **terminal** among the pair's other templates, shrunk toward the pair's
overall rate: $(s+\bar y)/(n+1)$, where $s$ and $n$ count the terminal's labels outside the
site's template. A site never contributes to its own score.

### 14.2 The metrics

| function | line | what it computes |
|---|---:|---|
| `auroc` | [52](../../phase4/code/p4/analysis/h4.py#L52) | Mann–Whitney with average ranks for ties: $(R_1 - n_1(n_1+1)/2)/(n_1 n_0)$; `None` with one class |
| `threshold_groups` | [73](../../phase4/code/p4/analysis/h4.py#L73) | (score, n, positives) per **distinct** score, highest first; every threshold metric uses these |
| `auprc` | [98](../../phase4/code/p4/analysis/h4.py#L98) | step-wise average precision over the groups (D9: tied rows enter together) |
| `precision_at_k` | [134](../../phase4/code/p4/analysis/h4.py#L134) | expected precision of the top $k$, uniform within the boundary tie (D9) |
| `brier`, `ece` | [212](../../phase4/code/p4/analysis/h4.py#L212), [216](../../phase4/code/p4/analysis/h4.py#L216) | squared error; 10 equal bins, observed failure frequency against mean probability |
| `logistic_fit` | [236](../../phase4/code/p4/analysis/h4.py#L236) | Newton–Raphson for $\sigma(a+bx)$, 50 iterations, ridge $10^{-6}$ |
| `calibration_slope_intercept` | [263](../../phase4/code/p4/analysis/h4.py#L263) | `logistic_fit` of the labels on $\operatorname{logit}(\widehat p)$ |
| `youden_threshold` | [274](../../phase4/code/p4/analysis/h4.py#L274) | the observed probability maximizing TPR − FPR; the smallest on ties |

### 14.3 `evaluate_group` and `criteria`

[`evaluate_group(rows, calibration, threshold, …)`](../../phase4/code/p4/analysis/h4.py#L363),
for one (pair, family, split):

1. for `risk` and each baseline: AUROC, AP and P@10, P@50 on the rows where the predictor is
   finite; for `risk` also Brier, ECE, the calibration slope and intercept, and the mean
   within-lexicon AUROC;
2. **if `calibration` is `None`, it fits one on these very rows**, `logistic_fit(risk, labels)`:
   the in-sample fallback behind deviation D12;
3. for each baseline, `cluster_bootstrap` of the difference `AUROC(risk) − AUROC(baseline)` on the
   same resampled rows, with its one-sided p.

[`criteria(metrics)`](../../phase4/code/p4/analysis/h4.py#L437) turns the differences against
identity and length into C1 and C2 (point ≥ 0.10 and ≥ 0.05; lower bound > 0), applies `holm`
to their two p-values, and marks each `MET` only if the point, the interval and the Holm value
(< 0.05) all pass. C3 is written `NOT TESTABLE` (deviation D1).

### 14.4 Where the calibration comes from

- **At the freeze** ([`freeze.build_payload`](../../phase4/code/p4/governance/freeze.py#L48)): for
  each development pair, `logistic_fit` on the development table, and `youden_threshold` on its
  probabilities. The 0.5B pair got $a=-0.29844$, $b=0.90142$, threshold 0.364.
- **In the held-out export** ([`export.py:308`](../../phase4/code/p4/reporting/export.py#L308)):
  a pair present in the freeze gets its frozen parameters; any other pair gets `cal = None`, so
  its prediction rows use $(a,b)=(0,1)$, that is $\sigma(\text{risk})$, while still being labelled
  `DEV_FREEZE`, and its metrics refit in sample. The 72B pair's prediction at the running `blk`
  site is $\sigma(0.6866)=0.6652$. D13 (F1) added out-of-sample estimates post hoc.

**Say it aloud:** "H4's code joins base and instruct margins site by site, ranks with tie-safe
metrics, bootstraps every difference on the same template draws, and applies Holm to exactly two
tests per pair and family."

---

## 15. H2 and power

[`h2.evaluate(None)`](../../phase4/code/p4/analysis/h2.py) returns `NOT TESTABLE` with the reason;
the machinery for three scales and the sign-agreement rule exists (`scoring.interaction_did`) and
is tested on synthetic cells. [`power.py`](../../phase4/code/p4/analysis/power.py) estimates the
ICC from development data ([`icc_binary`](../../phase4/code/p4/analysis/power.py#L52)), computes
design effects and planning power for H4 (Hanley–McNeil, with a simulation check), for the rule
effect, for Arm B's conditional rate and for the `k*` median, and runs only in the development
stage: a held-out export writes `power.csv` as `NOT RUN`.

---

## 16. One site through all the code

`dom:d50s3:t011:T_TYPE_MESH:0`, and its `blk` twin, end to end (held-out values, Qwen2.5-Coder-0.5B
and its instruct twin unless named):

| step | function | `dom` | `blk` |
|---|---|---|---|
| IR | `templates.build_templates` | `t011` = `metalness(0.8)` on `#panel>.frame>mesh`; hash `fcdf0518…` | the same IR |
| render | `Backend.render` | `(function(){ $S('.panel>#frame>camera')#metalness(0.8); })();` | `$S '.panel>#frame>camera' { metalness 0.8; }` |
| find the site | `scan_sites` | `TYPE_MESH`, `camera`, offset 31 | offset 18 |
| classify | `sites2.classify` | variant with `mesh` parses to another hash: SEMANTIC | SEMANTIC |
| keep | `dedupe_within_cells` | prefix unique in the cell: kept | kept |
| prompt | `prompts.bundle("rule", d50s3)` | 1,527 characters, 298 tokens | the same |
| context | `build_prefix` | prompt + `\n\n` + 31-character prefix: 307 tokens | prompt + 18 characters: 305 tokens |
| score | `score_pair_detailed` | `camera` −6.082, `mesh` −1.570: $M=-4.512$ | −6.345, −2.590: $M=-3.755$ |
| controls | Arm A | `norule` −5.103, length-matched −5.428 | −4.668, −5.259 |
| instruct twin | Arm A | $M=-0.638$ | $M=-0.215$ |
| H4 row | `h4.build_table` | risk 4.512, label 1 | risk 3.755, label 1 |
| H4 probability | export, frozen $a,b$ | 0.977 | 0.956 |
| ladder | `score_primary_cell` | −4.51, −3.49, **+2.61**, +1.80, +2.31, +2.79, +4.91 | −3.76, −2.71, −2.94, −3.97, −4.05, **+4.15**, +4.80 |
| `k*` | `kstar.compute` | 1.573, sustained from 2 | 11.951, sustained from 16 |
| Arm B (1.5B-Instruct) | `armb.observe` | not reached (`#panel` at the start) | reached, `mesh`: reverted |
| H5 (0.5B-Instruct) | `score_h5_cell` | a control site in the targeted arm: $M=-1.005$, still SEMANTIC | a control site; scored under the wrong repair (§11.6) |

---

## 17. The defect history: what each guard in the code is for

Most of the defensive code above exists because a specific defect was found. Knowing them is the
fastest way to understand why the code looks the way it does.

| id | where | the defect | the guard now |
|---|---|---|---|
| P32-001 | scorer | the candidate merged into the prefix's last token; both sides scored 0.0 | first-divergent-token scoring on joint tokenizations |
| P32-002 | prompts | the "rule" prompt contained no table | `rule_prompt` renders the table from φ |
| P32-003 | sampling | a first-N slice scored only `dom` | `balanced`, `assert_balanced` |
| P32-004 | scoring | per-site details were not saved | every row carries the full `PairScore` |
| P33-001 | scorer | one side scored over zero tokens returned 0.0 | `ZeroLengthSpan` |
| P33-002 | scorer | bf16 margins quantized; signs arbitrary near zero | fp32 output head; `tie` recorded |
| P33-003 | sampling | de-duplication depended on input order | canonical key; per (family, lexicon) cell |
| P33-004 | sampling | the balance check ignored cells | expected cells from the materials |
| P33-005 | bootstrap | a template drawn twice counted once | `_draw` tags |
| P33-006 | prompts | every site saw the first lexicon's table | per-site bundle; `assert_prompt_matches` |
| P33-007 | `k*` | wrong for already-correct and censored curves | `kstar.compute` as specified |
| P33-008 | ladder | 82 of 120 sites saw their own program | `demos.is_leak`, `audit` |
| P33-009 | fertility | measured for one tokenizer only | per tokenizer |
| P33-010 | runtime | one JSON at the end of a job | atomic shards, done-markers, manifests |
| P33-011 | lexicons | the tests rewrote tracked files | idempotent atomic `write` |
| P33-012 | Slurm | a resubmitted single index scored no model | task *i* → model *i* |
| P33-013 | tests | one blocked test stopped the suite | exit codes 0/1/5 |
| P33-014 | runtime | temp-file names collided across tasks | `mkstemp` + fsync + replace |
| P33-015 | split | drift checked only at unlock | `load_unlock` re-checks on every access |
| P33-016 | runtime | the fake scorer could leak into real jobs | `P4_FAKE` unset in real jobs |
| P33-017 | CLI | `status` created a shard directory | `status` is read-only |
| P33-018 | prefetch | re-running prefetch re-pinned models | pins kept unless `--repin` |
| R1, R2 (D9) | H4 | AP and P@k depended on row order within ties | `threshold_groups` |
| F5 (D13) | Arm B | a same-line `Request:` kept by the extractor | cut post hoc in `fix_heldout_problems.py`; frozen code unchanged |
| **open** | KM | the median can land one switch late (§13.2) | none yet |
| **open** | H5 | targeted repairs share one cache name (§11.6) | none yet |

---

## 18. Practice

**Question 1.** Why does the site classifier substitute the familiar spelling at an offset from
the lexer instead of using `str.replace`?

**Answer:** `#` is also the first character of every colour literal; a text replacement would
corrupt arguments and invent collisions. The offset from `scan_sites` is exact, and arguments are
skipped.

**Question 2.** `dom:d50s3:t011:T_ID_SIGIL:0` is SEMANTIC. Why is it not scored?

**Answer:** Its prefix, `(function(){ $S('`, is shared with the first selector symbol of every
`dom` program; `dedupe_within_cells` keeps one site per prefix in each cell, chosen by the canonical
key, and that site belongs to `t000`.

**Question 3.** In which tokenizer is the length-matched control 307 tokens long, and why not
exactly 298?

**Answer:** In the scoring model's own tokenizer (here Qwen's), because the control is built with
the scorer's token counter. Whole neutral lines of 10 tokens are added until the count reaches the
target, so it can overshoot by up to one line.

**Question 4.** What stops a `d25s3` site from being scored against `d50s3`'s table?

**Answer:** `score_arm_a_cell` builds the bundle from the site's own lexicon, and
`assert_prompt_matches` checks the site's lexicon, the prompt's lexicon, and that the table states
the site's mapping.

**Question 5.** A cell's shard exists but its done-marker's SHA-256 does not match. What happens on
resume?

**Answer:** `ShardStore.status` reports `corrupt`; `run` quarantines the shard and marker, and the
cell is scored again.

**Question 6.** Arm B extracted a correct `blk` program for Qwen2.5-72B-Instruct but called it
`PARSE_FAIL`. Why, and why did no site outcome change after the fix?

**Answer:** The model continued on the same line with `Request: …`, which `extract_program` kept.
Site observations only compare the text up to and at each site, which the continuation does not
touch.

**Question 7.** In H5, why can a control site's margin change at all?

**Answer:** The repaired lexicon changes the token table in the prompt and the spellings of earlier
symbols in the program, so the context of an unrepaired role changes too.

**Question 8.** Which single line would you change to fix §11.6, and what else must change with
it?

**Answer:** The repair's name in `repaired_phi` (and so the cache key) must include the family and
the model, or the role set. The proofs must then be keyed the same way, and the targeted cells
re-scored, under a dated deviation.

**Question 9.** Where would a held-out run fail if someone edited `h4.py` after the unlock?

**Answer:** `splits.load_unlock`, called through `check_access` before any held-out cell is touched,
re-hashes every source file against the freeze and raises `SplitViolation`.

**Question 10.** Why is the 72B pair's held-out probability $\sigma(\text{risk})$ even though the
column says `DEV_FREEZE`?

**Answer:** The freeze holds parameters only for the two development pairs; for any other pair the
export passes `cal = None`, and the prediction rows fall back to $(a,b)=(0,1)$ while keeping the
label.
