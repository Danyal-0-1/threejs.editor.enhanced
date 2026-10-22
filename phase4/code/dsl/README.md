# dsl/ — the language

Everything the experiment knows about the language lives here:

- the 3DOM grammar;
- the vocabulary a lexicon can respell;
- the lexicons themselves;
- the code that applies a lexicon, parses programs and builds the canonical IR;
- the test programs the grammar is checked against.

**Where it came from.** It is a byte-identical copy of `phase3/vendor/`, which Phase 3 copied in
turn, with recorded provenance, from the Phase 1 and Phase 2 originals (`grammar_and_3DOM_client/`
and `alien_syntax/` at the repository root; see `phase3/SOURCE_MANIFEST.md`).

**The folder names are load-bearing.** `phi.py` finds its data by its own location, so
`alien_syntax/` and `grammar_and_3DOM_client/` must stay side by side. `../p4/paths.py` puts the
three source folders on `sys.path`, so the modules import each other by bare name (`import phi`).

```
dsl/
├── grammar_and_3DOM_client/        the 3DOM language (Phase 1)
│   ├── 3dom_grammar.iso.ebnf       the grammar, in ISO/IEC 14977 EBNF (3dom-grammar/1.1.0)
│   ├── 3dom_grammar.w3c.ebnf       the same grammar, in W3C EBNF
│   ├── terminals.json              the terminals (sigils, keywords, verbs, ...) and their known collisions
│   ├── ir_schema.json              the schema of the Operation IR every program lowers to
│   ├── tasks.py                    the five task scorers that grade an IR (with the P3-001 repair)
│   ├── fixture_scene.py            the fixture 3D scene, and the selector resolver the scorers use
│   └── conformance/                the grammar's test programs
│       ├── refgrammar.py           the reference engine for the grammar (the transpiler parses with it)
│       ├── positive.txt            valid programs: each must parse to exactly one derivation
│       ├── negative.txt            invalid programs, each annotated with the rule it breaks: all must be rejected
│       └── vacuous.txt             valid programs with zero operations: a parse success but a task failure
├── alien_syntax/                   respelled ("alien") versions of the language (Phase 2)
│   ├── src/
│   │   ├── phi.py                  a lexicon (a phi-map): load it, validate it, apply it, invert it
│   │   ├── transpiler.py           alien text -> IR, and IR -> alien text
│   │   ├── canonicalize.py         the frozen canonical form of the IR
│   │   ├── generate_corpus.py      the corpora in any lexicon, produced from the conformance programs by phi
│   │   └── heuristics_ir.py        Phase 2's scene-scaffolding heuristics (not used by the pipeline)
│   ├── grammar/
│   │   ├── render_grammar.py       renders the grammar for a lexicon, from the templates
│   │   └── templates/              the grammar templates (ISO, W3C and Lark)
│   └── candidates/                 the lexicons, phi_<id>.json
└── PATCHES/
    └── tasks.op_selection.md       the record of the P3-001 repair in tasks.py
```

## The lexicons (`alien_syntax/candidates/`)

| lexicons | made in | what they are | role in the experiment |
|---|---|---|---|
| identity | built into `phi.py` | the original spelling | the baseline |
| `alpha`, `beta`, `gamma` | Phase 2 | the first alien lexicons. `beta` and `gamma` use alphabets disjoint from CSS, so a familiar spelling can never be valid in them | `beta` is H5's repair alphabet (`p4/experiments/h5.py`, `REPAIR_SOURCE`) |
| `delta` | Phase 3 (`phase3/scripts/make_delta.py`) | the first permuted lexicon: symbols swapped within a shape class, so a familiar spelling stays valid but means something else | Phase 3 only |
| `d25s1`, `d25s2`, `d50s1`, `d50s2` | Phase 3.2 (`p4/language/deltafam.py`) | permuted the same way, by remap density (25 or 50%) and seed | **development** lexicons |
| `d25s3`, `d50s3`, `d75s1a`, `d75s2a`, `d75s3a` | Phase 3.2 | the same family, up to 75% density | **held-out** lexicons |

The split is registered in `p4/governance/splits.py` (`DEV_LEXICONS`, `HELDOUT_LEXICONS`). New
lexicons are made with `tools/build_materials.py`.

## How the pipeline uses these files

- **Every prompt and site:** `phi.py` applies a lexicon, `transpiler.py` parses and renders, and
  `canonicalize.py` fixes the IR form. They are used by `p4/language/`, `p4/sites/`,
  `p4/prompts/` and `p4/experiments/`.
- **H5's meaning-preservation proof:** each repaired lexicon is checked over the whole positive
  corpus (`generate_corpus.phase1_programs("positive", ...)` in `p4/experiments/h5.py`).
- **Arm B:** `transpiler.py` and `canonicalize.py` parse and grade each generated program.
- **The run's materials hash:** `p4/runtime/config.py` (`materials_hash`) hashes the lexicons,
  `terminals.json`, the 80 template programs and the `blk` grammar into every run's record. A
  changed lexicon or terminal file changes that hash.
- **The tests:** `tests/test_scorer_repair.py` checks the P3-001 repair, and `tests/test_sites.py`
  and `tests/test_phase3_2.py` use the conformance programs.

To read about this layer:

- the grammar: [`explanations/phase1/phase1.md`](../../../explanations/phase1/phase1.md);
- lexicons and the transpiler: [`explanations/phase2/phase2.md`](../../../explanations/phase2/phase2.md).
