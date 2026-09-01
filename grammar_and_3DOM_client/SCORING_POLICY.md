# SCORING_POLICY.md

**grammar version:** `3dom-grammar/1.1.0`

This policy is frozen **before any model numbers exist**, so scoring decisions
cannot be retrofitted to results. It defines (i) the error taxonomy, (ii) the
valid-but-vacuous rule (D5), (iii) the graded parse metric `nLVP` and the failure
locator `FAILP` (A3), and (iv) the branching-factor rows that enter the matched-
complexity table (A4). Every reported row must carry the grammar version above.

---

## 1. Two orthogonal axes — never collapse them

A model output is scored on **two independent constructs**. They are reported in
**separate columns** and must never be averaged into one "accuracy" number.

| Axis | Question | Ground truth | Depends on a scene? |
|---|---|---|---|
| **Parse validity** | Is the output a well-formed 3DOM program? | the grammar (`refgrammar` / the `.ebnf`) | no |
| **Task accuracy** | Does it do what the task asked? | the target **Operation IR** | selector-resolution tasks: yes |

Rationale (paper-ready): *Parse validity and task accuracy measure different
things. A string can be perfectly grammatical and semantically empty (Section 2),
or semantically "close" yet ungrammatical. Collapsing them hides exactly the
behaviour we study — whether scaffolding buys syntactic conformance, semantic
correctness, or both. We therefore report them as separate columns throughout.*

---

## 2. The valid-but-vacuous rule (D5)

`chain_expression ::= selector_call operation_call*` admits **n = 0**: the program
`(function(){ $S('.wheel'); })();` is syntactically complete and has **zero
effect** (a pure query). It is also the most plausible-looking null output a small
model emits. The rule:

- A vacuous chain is a **PARSE SUCCESS**.
- A vacuous chain is a **TASK FAILURE** on any task whose target IR contains **one
  or more operations**. (On a task whose target IR is itself empty — a pure query
  task — it is a task success; we currently ship no such task, but the rule is
  stated for completeness.)
- Vacuous programs are a **third corpus category**, `conformance/vacuous.txt`
  (`VALID-BUT-VACUOUS`). They are **not** in the negative corpus — they do not
  raise — and they add no production coverage the positives lack.
- CI enforces the definition: every vacuous item **parses** (`num_parses == 1`)
  **and** yields **zero operations** (zero `VERB` tokens → the IR builder emits an
  empty op list). See `coverage.py` gate **G4**.

Reporting: vacuous outputs are counted in a dedicated cell (`%vacuous`) so a
condition that "improves parse validity" purely by emitting more empty queries is
visible as such and cannot masquerade as a task-accuracy gain.

---

## 3. Error taxonomy

Each model output falls into exactly one bucket, evaluated in order:

1. **LEX_FAIL** — the lexer cannot tokenize (e.g. unterminated/mismatched quote,
   illegal character). `LVP = 0`.
2. **PARSE_FAIL** — tokenizes but no derivation exists. Report `nLVP` and `FAILP`
   (Section 4).
3. **VALID_VACUOUS** — parses; zero operations (Section 2).
4. **VALID_WRONG** — parses; ≥1 operation; but the resulting IR ≠ target IR
   (wrong selector, wrong verb, wrong args, wrong op count/order).
5. **VALID_CORRECT** — parses; IR == target IR under IR-identity scoring.

Parse-validity column = {3,4,5} count as valid; {1,2} invalid.
Task-accuracy column = {5} only.

---

## 4. Graded parse metric: `nLVP` and `FAILP` (A3)

Binary parse success saturates at 0.5B, where bare and scaffolded conditions both
sit near the floor and look identical. Because the language is **regular**, we
compile it to a DFA over DSL tokens (`refgrammar.build_dfa`) and grade *how far*
an output got before the automaton dies.

**Definitions.**

- **LVP** (longest valid prefix) = the number of **DSL tokens** consumed before the
  DFA has no legal transition. Computed by `refgrammar.longest_valid_prefix`.
- **nLVP** = `LVP / (length in DSL tokens of the reference solution)`.
  Reported per matrix cell alongside binary validity.
- **FAILP** = the DFA state / production at which the transition failed, i.e. the
  set of tokens that *would* have been legal there. Aggregated over a condition it
  yields a **failure-location distribution** — a mechanistic finding, not just an
  accuracy scalar.

**Token-space discipline (mandatory).** `nLVP` is measured in **DSL tokens**, which
is *distinct* from **model-token (sub-word) position**. Both are computed and kept
separate:

- **DSL-token LVP** is the *syntax* measure (this section).
- **Model-token position** feeds the **fertility analysis** (A5-adjacent): how many
  sub-word tokens the model spends per DSL token. A change in DSL-token LVP with
  flat model-token counts, or vice-versa, is itself a result.

Never report one as if it were the other; a table cell must state which space it
is in.

**Why this sharpens (not weakens) the capability-floor argument.** If scaffolding
raises `nLVP` at 0.5B while binary validity stays at floor, that is direct evidence
scaffolding *is* moving behaviour below the pass threshold — visible only with a
graded metric. If `nLVP` is also flat, the capability-floor claim is *strengthened*
by a measurement binary scoring could not make.

---

## 5. Branching-factor rows in the matched-complexity table (A4)

Production count is a crude difficulty proxy; **branching factor** is what the
decoder actually faces at each step. From the same DFA:

- **mean branching factor** and **max branching factor** are rows in
  `METRICS.md`, marked **INVARIANT** — the Alien-Syntax grammar must match them, or
  the two languages are not of equal decode difficulty and the isomorphism claim
  has an unmeasured confound.
- **branching factor as a function of position** is reported as a profile
  (`refgrammar.branching_profile_over_corpus`) and used to check that difficulty is
  distributed similarly across the program, not just equal on average.

Two grammars with identical |P| but different branching profiles are **not**
equally hard to emit; a reviewer who works on constrained decoding will know this,
so the profile — not just |P| — is the complexity claim we defend.

---

## 6. IR-identity scoring (forward reference — out of scope here)

Task accuracy (bucket 5) is scored on **IR identity**, not surface strings, so
3DOM and the Alien language are scored on the same ground truth. The IR schema is
**out of scope for this document and is designed in the next step**; this policy
only fixes that (a) the IR builder stamps `grammar_version` into every IR object,
and (b) selector-resolution is the sole task family whose ground truth depends on a
fixture scene (see `TERMINOLOGY.md`).
