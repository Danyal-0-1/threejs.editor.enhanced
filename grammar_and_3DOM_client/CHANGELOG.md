# CHANGELOG — 3dom-grammar → `3dom-grammar/1.1.0`

Version bump **1.0.0 → 1.1.0** (semantic versioning; minor: repairs + additions,
no verb/type/pseudo set changes, no wrapper change, language *narrowed* only where
it was accidentally ambiguous — see D3). Every downstream artifact carries the
version string (A5). Prose blocks marked **[paper]** are drafted to be pasted into
the methodology/appendix.

Machine-verified before release: `python3 conformance/coverage.py` → all gates
green (62 positives unique-parse, **100% production coverage**, 64 negatives
rejected, 12 vacuous parse-with-zero-ops, L2 differential enforced, Earley≡DFA on
138 items); `python3 grammar_metrics.py` → ISO/W3C cross-check PASS, table
regenerated.

---

## Resolution note (a requirement-vs-requirement inconsistency, resolved not guessed)

A2's *illustrative* mutation list places “space inside a compound
(`.wheel .front` vs `.wheel.front`)” in the **negative** corpus, but A2's own CI
clause requires every negative to **raise**, and D1/L2 makes `.wheel .front` a
**valid** descendant selector. Both cannot hold. The governing clauses
over-determine the fix: `.wheel .front` is valid, so it cannot be a
parse-*failure* item. It was therefore moved to the **D1/L2 differential test**
(gate **G5**: `$S('.car .wheel')` and `$S('.car.wheel')` must parse to *different*
structures) — which is exactly the contrast that example was demonstrating. No
rule was invented; the language is unchanged. Had we instead forced a *raising*
item there, we would have had to add a rule rejecting internal selector spaces,
which D1/L2 forbids.

---

## D1 — Inter-token whitespace was forbidden by a strict reading

**What changed.** Added a **normative** "Lexical Conventions" preamble (numbered
clauses **L1–L3**, plus reference-parser clause **P1**) to *both* `.ebnf` files. No
layout non-terminal was threaded through the productions.

**Why.** Read strictly, `iife ::= '(' 'function' '(' ')' '{' statement* '}' …`
provides no whitespace between terminals, so the pretty-printed multi-line form an
LLM actually emits was *not* in the language. A harness scoring parse success would
have silently penalised correctly-formatted output. L1 states layout is elided by
the conventional lexer/parser separation; L2 states whitespace *inside* a selector
is significant (it is the descendant combinator); L3 states the two-level parse
(outer opaque-selector + layout-eliding; inner layout-significant) that makes L1
and L2 coexist. This is the correct engineering answer (prose convention + two-level
lexer) and it keeps the production count small so the Alien grammar can match it.

**Alternative rejected.** *Thread an explicit `layout` non-terminal between every
pair of terminals.* Rejected: it inflates |P| and the branching profile with tokens
that carry no meaning, destroys readability, and — fatally for this project —
forces the Alien grammar to replicate the same inflation, turning a lexer
convention into a spurious complexity difference.

**Verification.** `positive.txt` contains a deliberately multi-line, internally-
spaced program (`$S( '.wheel' ) . scale( 2 ) ;`) that parses (gate G1). L2 is
enforced by gate G5. **[paper]** *3DOM uses the conventional lexer/parser
separation: inter-token whitespace is insignificant (L1), except inside a selector
string, where it is the descendant combinator and is significant (L2). The two
regimes coexist via a two-level parse (L3): the outer parser treats a quoted
selector as one opaque token, the inner parser lexes its contents with whitespace
significant.*

---

## D2 — ISO permitted mismatched quotes; W3C did not

**What changed.** Introduced `quoted_selector` and `quoted_string` in **both**
files, each binding the opening and closing quote inside a single alternative
(`"'" selector "'" | '"' selector '"'`). The bare `quote` non-terminal, whose two
*independent* occurrences allowed `$S('.wheel")`, was **removed** (it is now
unreachable — there is no remaining site where the two quote occurrences are
genuinely independent).

**Why.** In v1.0 ISO, `selector_call = "$S" , "(" , quote , selector , quote , ")"`
had two independent `quote` occurrences, so ISO admitted `$S('.wheel")` while W3C
(already split by quote style) rejected it. The same drift existed in `hex_color`
and `string`. A dual-notation strategy is a liability, not a strength, exactly when
the two notations disagree; binding quotes structurally makes agreement impossible
to violate in either notation.

**Alternative rejected.** *Keep `quote` and add a semantic side-condition "closing
quote must equal opening quote."* Rejected: quote-matching is not expressible as a
context-free side note without leaving the formalism; the two-production split
expresses it *in the grammar*, is trivially checkable, and is what parser
generators consume directly.

**Verification.** Negative corpus includes both mismatch directions and the arg-
string mismatch, all rejected on both engines (gate G3). **[paper]** *String
delimiters are bound structurally: a selector or argument string is derived by a
single production whose opening and closing quote are the same alternative, so a
mismatched-quote literal is not derivable in either notation.*

---

## D3 — `argument` was ambiguous (`'#f00'` had two parse trees)

**What changed.** **Deleted** `hex_color`, `hex_body`, `hex_pair`, `hex_digit`
from both files (option **(b)**). `argument ::= number | quoted_string`; **all
quoted values parse as `quoted_string`**, and hex/axis/enum typing moves to the IR
builder's per-verb argument table.

**Why.** `argument ::= hex_color | number | string` made `'#f00'` a member of
`L(hex_color)` **and** `L(string)` (since `[^']*` matches `#f00`), so two
derivations existed — the grammar was **ambiguous**. The v1.0 annotation claimed
the alternatives were "ordered hex → number → string," but ISO/W3C alternation is
**unordered set union**; ordered choice is **PEG** semantics, a different
formalism. The comment described a PEG while the notation defined a CFG. This is
fixed, not annotated around. Value typing is *shared* between 3DOM and the Alien
language; encoding it in the grammar means maintaining the same semantic table
twice, in two syntaxes; encoding it in the IR encodes it **once**. The fix also
shrinks the grammar and *removes* the ambiguity rather than masking it. `number`
and `quoted_string` have disjoint first sets (`[+-0-9]` vs `['"]`), so the repaired
`argument` is unambiguous.

**Alternative rejected — option (a).** *Make `string` exclude a leading `#`:*
`string ::= "'" ( [^'#] [^']* )? "'" | '"' ( [^"#] [^"]* )? '"'` and keep
`hex_color`. Rejected because: (i) it retains two value productions and the
duplicated typing burden across two languages; (ii) it forbids the legitimate
string `'#label'` as a *string* argument, changing the language to dodge the
ambiguity; (iii) it is brittle — any future value form (`0x…`, rgb()) reopens the
same overlap. Deletion is simpler, removes the ambiguity at the root, and colocates
typing with the per-verb table that already exists.

**Recomputed counts (not carried forward).** All figures are regenerated by
`grammar_metrics.py`, not inherited from the v1.0 “|N| = 31”. Post-D3 composition:
the four `hex_*` productions are gone; string handling is now
`{quoted_string, sq_char, dq_char}`. Current machine-computed values:
**|N| = 31 nonterminals, |P| = 58 productions, |Σq| = 39 quoted terminals** (see
METRICS.md). The nonterminal *count* coincidentally returns to 31 but its
*membership* differs; the figures are freshly computed, not reused.

**Verification.** Gate G6 asserts **zero ambiguous parses** over the entire
positive corpus (the exact parse *count* is checked == 1 per item, not merely
≥ 1). **[paper]** *Argument typing (hex colour vs axis string vs enum) is a
semantic property and is resolved in the IR builder's per-verb table, not the
grammar; the grammar admits `number | quoted_string` with disjoint first sets and
is therefore unambiguous at the argument position.*

---

## D4 — the combinator is not LL(1): k documented, grammar not silently refactored

**What changed.** (1) `k = 2` recorded as a formal, **INVARIANT** property in
METRICS.md. (2) **Earley** mandated as the reference parser in the L-preamble
(clause P1), justified in one line. (3) The LL(1) left-factored variant added to a
clearly-marked **NON-NORMATIVE Appendix A** of the W3C file, with the note that if
it is ever adopted, the Alien grammar must be left-factored **identically**.

**Why.** `descendant_combinator ::= whitespace` and
`child_combinator ::= whitespace? '>' whitespace?` overlap on a leading
`whitespace`: on that token the parser cannot choose without a second token. This
is **not ambiguous** (exactly one parse succeeds) but it **is not LL(1)** (k = 2),
so an LALR front end reports a conflict. Lookahead requirement is part of
grammatical complexity; matching it is part of the equal-complexity claim. Silently
left-factoring one grammar and not the other would create an *unmeasured confound*.

**Alternative rejected.** *Left-factor the normative grammar to LL(1).* Rejected as
the normative choice: it would change the grammar's advertised complexity (k 2→1)
away from the surface form the language actually has, and would obligate an
identical, non-obvious refactor of the Alien grammar to preserve isomorphism. Kept
available (Appendix A) but non-normative.

**Verification.** The Earley engine parses all positives with a unique derivation
(G1) despite k = 2, and rejects all negatives (G3); the k = 2 decision point is the
selector-internal `whitespace`. **[paper]** *The combinator rule is deliberately
k = 2, not LL(1): a selector-internal space is disambiguated only by the following
token (a `>` for a child combinator, or a compound-start for a descendant). We
parse with Earley, which handles k > 1 and reports ambiguity explicitly; the
lookahead requirement is recorded as a matched-complexity invariant so the Alien
grammar inherits it.*

---

## D5 — vacuous chains: scoring rule fixed before numbers exist

**What changed.** No grammar change (`chain_expression ::= selector_call
operation_call*` with n = 0 is correct and intentional). The **scoring rule** is
written in `SCORING_POLICY.md`: a vacuous chain is a **PARSE SUCCESS** and a **TASK
FAILURE** on any task whose target IR has ≥ 1 operation; parse validity and task
accuracy are **separate columns**; vacuous programs form a **third corpus category**
(`conformance/vacuous.txt`), not negatives.

**Why.** `$S('.wheel');` is syntactically complete, zero-effect, and the most
plausible null output at 0.5B. Leaving its scoring undefined would let a "valid but
empty" output be silently counted as either a pass or a fail depending on who wrote
the harness. Fixing it in advance removes a researcher degree of freedom.

**Alternative rejected.** *Forbid n = 0 in the grammar (`operation_call+`).*
Rejected: a pure query is a legitimate, meaningful 3DOM program; banning it would
mis-model the language to simplify scoring, and would also remove the very null-
output category we want to *measure*. The correct home for "did it do the task" is
the task-accuracy column, not the grammar.

**Verification.** Gate G4: every vacuous item parses and yields zero operations.

---

## Additions A1–A6 (summary; see the named files)

- **A1 `terminals.json`** — 43 terminals with stable IDs, spelling, role,
  productions, and `substitutable`. **29 substitutable** (CSS/jQuery/JS lexicon
  renamed by the φ-map) / **14 not** (generic delimiters, string quotes,
  whitespace-as-combinator, and infinite value classes copied verbatim into the
  IR). **Justification for each `false`:** `(`,`)`,`{`,`}`,`;`,`,` are generic
  C-family delimiters, not domain familiarity signals; `'`/`"` are structural
  string delimiters the two-level lexer (L3) is defined against; `+`/`-` are
  generic numeric signs; `T_IDENT`/`T_NUMBER`/`T_STRING_BODY` are *infinite value
  classes* with no fixed spelling to substitute (their values are copied into the
  IR); `T_WS` is whitespace-*as-combinator*, whose “spelling” is load-bearing for
  the L2/L3 lexer contract. **Collisions block** flags three overloaded spellings:
  `.` (`T_CHAIN_OP` vs `T_CLASS_SIGIL`), ` ` (insignificant layout vs `T_WS`
  descendant combinator), `-` (`T_SIGN_MINUS` vs hyphen inside `T_IDENT`) — a naive
  substitution keyed on the *character* would break one role of each; the φ-map
  must key on the terminal **ID**. This makes structural isomorphism a *build
  artifact*, not a claim.
- **A2 conformance corpora + `coverage.py`** — 62 positive / 64 negative / 12
  vacuous; **100% production coverage** (57/57 W3C production branches, incl. all
  15 verbs, all 4 child-combinator spacing branches, both pseudos, wildcard, all
  matcher kinds); negatives are mutation-derived and annotated with
  `VIOLATES <production> | MUTATION <operator>`; CI asserts positives parse,
  negatives raise, vacuous parse-with-zero-ops, the L2 differential, and Earley≡DFA.
- **A3 graded metric** — `nLVP` (longest-valid-prefix over **DSL tokens**,
  normalised) + `FAILP` (failure location), defined in SCORING_POLICY.md, computed
  by `refgrammar.longest_valid_prefix`; DSL-token vs model-token spaces kept
  explicitly distinct.
- **A4 branching profile** — mean/max branching factor added as **INVARIANT** rows
  in METRICS.md, plus a position-indexed profile, all from the DFA.
- **A5 versioning + generated metrics** — `3dom-grammar/1.1.0` stamped in both
  `.ebnf` headers, `terminals.json`, METRICS.md, and required of every future IR
  object; `grammar_metrics.py` regenerates the table from the `.ebnf` files and
  correctly **excludes quoted literals** when counting operators (naive `*`-count
  82 → true Kleene-star count 6, because `wildcard ::= '*'` and every `/* */`
  comment contain a literal `*`).
- **A6 `TERMINOLOGY.md`** — AST-vs-scene-graph discipline, the `>` trap, the 1:N
  cardinality argument, a banned-phrase table, and the tie to the task taxonomy
  (selector-resolution is the only fixture-scene task). A matching syntax/semantics
  annotation sits beside `child_combinator` in the ISO file.

---

## Formal arguments (acceptance criteria)

### (i) The language is REGULAR (still non-self-embedding after every repair)

A CFG is **non-self-embedding** iff no non-terminal `A` has a derivation
`A ⇒* α A β` with `α ≠ ε` **and** `β ≠ ε`; such a grammar generates a **regular**
language (Chomsky 1959).

*Argument.* Enumerate the only recursive non-terminals of the flattened grammar:
`stmts → statement stmts`, `ops → opcall ops`,
`argtail → ',' argument argtail`, `ctail → combinator compound ctail`,
`matchers → matcher matchers`. **Every one is right-recursive** — the recursive
occurrence is the rightmost symbol, so `β = ε`. No production places a non-terminal
recursively with non-empty material on *both* sides. In particular `iife` wraps
`stmts` with material on both sides (`… '{' stmts '}' …`), but that is `iife`
embedding a *different* non-terminal; `stmts` does not derive `iife` (nothing
reachable from `stmts` re-derives `program`/`iife`), so no cycle `A ⇒* α A β`
passes through it. Hence there is **no self-embedding**, and the language is
**regular**. This survived every repair: D2 (quoted split) and D3 (hex deletion)
only *removed* or *renamed* non-recursive productions; D1/D4/D5 changed no
production structure. Operationally, we exhibit the DFA
(`refgrammar.build_dfa`, 52 states) — a finite automaton accepting the language,
which exists **iff** the language is regular.

### (ii) Lookahead k = 2 (not LL(1))

`FIRST(descendant_combinator) = { whitespace }` and
`FIRST(child_combinator) ⊇ { whitespace }` (the `whitespace? '>' …` branch), so a
single lookahead of `whitespace` cannot select the `combinator` alternative; the
*second* token (`>` ⇒ child, or a compound-start ⇒ descendant) decides. Thus
`k = 2`, exactly one parse succeeds (not ambiguous), and an LL(1)/LALR generator
reports a conflict. Recorded as an INVARIANT; the LL(1) equivalent is Appendix A.

### (iii) The ISO and W3C files accept the SAME language

Three independent supports:

1. **Rule-by-rule transliteration.** The files are mechanical transliterations with
   identical rule names and identical alternative structure. The only notational
   deltas are: `{X}` (ISO) ↔ `X*` (W3C); `[X]` ↔ `X?`; `X , Y` (ISO concatenation
   comma) ↔ `X Y`; ISO `X , {X}` ↔ W3C `X+`; ISO special sequence `? … ?` ↔ W3C
   `[ … ]` character class; and quote representation. Each delta is a notation for
   the *same* operator and changes no generated string.
2. **Machine cross-check** (`grammar_metrics.py`): the two files are parsed and
   asserted to share an **identical non-terminal set** (|N| = 31) and an
   **identical quoted-terminal inventory** (39 terminals, content-keyed so quote
   style is irrelevant). This catches the D2-class failure — a rule or terminal
   present in one file but not the other — automatically. Result: **PASS**.
3. **Operational recognizer check** (`coverage.py` gate G6): the reference engine
   that both files transcribe recognises via two *independent* mechanisms — an
   Earley parser (parse-count) and a DFA — and they **agree on accept/reject for
   all 138 corpus items**, evidence the transcribed language is single and
   deterministic-recognisable.

### (iv) Hard invariants intact

Verb set = **exactly 15** (asserted at import in `refgrammar.py`);
`type_selector` = {mesh, group, light, camera}; `pseudo_selector` = {selected,
lasso}; IIFE wrapper mandatory (an un-wrapped statement is negative item #1);
no recursion/nesting introduced (see (i)). Walking D1..D5 against the final files:
each repair either added prose (D1), split a production (D2), deleted productions
(D3), added metadata/appendix (D4), or touched only scoring (D5) — none introduced
a new ambiguity, recursion, or wrapper optionality.

---

## Note on the Mermaid diagram (out-of-scope guard)

`3dom_syntax_diagram.md` visualises `chain_expression`, `selector_call`, and
`operation_call`. None of these productions changed in 1.1.0 (`selector_call` still
`$S ( quoted_selector )`; `operation_call` still `. verb ( argument_list? )`;
`quoted_selector` was already the node label). **The diagram is unchanged and
remains correct**; no update was required.
