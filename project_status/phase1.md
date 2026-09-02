# Phase 1 — A Masterclass in the 3DOM Formalisation

> **Subject:** `grammar_and_3DOM_client/` — 3DOM formalised in ISO/IEC 14977 and
> W3C EBNF at `3dom-grammar/1.1.0`, with five repaired defects (D1–D5) and six
> new deliverables.
>
> **Environment:** Python 3.12.3 · no third-party packages required by any Phase 1 artifact.
>
> **Verification status:** every number and behavioural claim below was executed
> against the artifacts on this machine. Where I ran something, the output is
> quoted. `conformance/coverage2.py` → **all six gates green**.

---

## Conventions

- **⚑ VERIFIED** — I executed this; output shown.
- **⚠ METHODOLOGIST** — my second hat. A CHI reviewer could use this against you.
- **📖** — a named technique, with a citation precise enough to look up. Chapter
  numbers only where I am confident; otherwise the concept name and the area of
  the book, because a wrong section number wastes more of your time than none.

---

## READ THIS FIRST — five places the artifacts differ from your brief

You asked me to teach, so I am not going to teach a version of your repository
that does not exist. Five corrections, each verified, each expanded later:

| # | Your brief says | The artifacts actually say | Where |
|---|---|---|---|
| 1 | *"ISO has no character classes — hence the 52-alternative `letter` rule"* | ISO/IEC 14977 **does** have an escape hatch: the **special sequence** `? … ?`. Your file uses it: `ident_char = ? one character from A-Z a-z 0-9 or '-' or '_' ? ;`. **The 52-alternative rule was never written and never needed to be.** | §1.1 |
| 2 | *"every Python import … especially `lark`, `re`, `json`, `pathlib`, `collections`, `itertools`"* | `coverage.py` imports **`os`, `sys`** only. `grammar_metrics.py` imports **`os`, `re`, `sys`** only. `refgrammar.py` — the 690-line engine — has **zero module-level imports**. No `lark`, `json`, `pathlib`, `collections`, or `itertools` anywhere in Phase 1. | §1.4 |
| 3 | Clause P1: *"REFERENCE PARSER = EARLEY"* | `refgrammar.py` does not implement Earley. Its own comment reads: *"Exact parse counter (ambiguity detector) — **memoized top-down** over a non-left-recursive CFG."* Same language, same exact derivation count, **different algorithm**. | §1.5 |
| 4 | CHANGELOG: *"Machine-verified before release: `python3 conformance/coverage.py` → all gates green"* | ⚑ That command **crashes**: `FileNotFoundError: … conformance/negatives.txt` (the file is `negative.txt`). `coverage2.py` is the one that runs, and it does pass all six gates. | §2.6 |
| 5 | METRICS.md: *"a naive `text.count('*')` counts 82; excluding quoted literals gives 6"* | ⚑ 82 → **7** by stripping `/* … */` comment delimiters; 7 → **6** by excluding quoted literals. Quote-exclusion accounts for **1** of the 76, not 76. The stated demonstration attributes the wrong cause. | §1.6 |

None of these invalidate the grammar. Items 4 and 5 are **paper-integrity**
problems — a cited command that errors, and a demonstration that misattributes
its own effect. Fix both before submission; details in §5.

---
---

# 1. NOTATIONS, METALANGUAGES & IMPORTS

## Part A — the two metalanguages

A metalanguage is a language for describing languages. You are using two, and the
reason you need two is not redundancy — it is that **they have different
consumers**, and a notation optimised for one consumer is bad for the other.

---

### 1.1 ISO/IEC 14977 — "Information technology — Syntactic metalanguage — Extended BNF"

**What it is.** A 1996 international standard that fixes a single canonical
spelling of EBNF. Its ancestry runs Backus → Naur (ALGOL 60 report) → Wirth's EBNF
(Pascal) → the ISO committee's attempt to end the proliferation of dialects.

**Its intended consumer is a human reading a standards document.** That is the
whole design brief, and it explains every otherwise-odd choice: the explicit
concatenation comma, the mandatory terminating semicolon, the `(* … *)` comment
form. It is the notation of the *normative appendix*.

**Its real-world use** is almost entirely in standards text: ISO/IEC language
standards, some ITU-T recommendations, government specification documents. It is
conspicuously **not** the notation of working parser generators — no mainstream
tool reads ISO 14977 natively. That fact is the whole reason your project needs a
second notation.

**The "Why" for this project, specifically.** Two reasons, and only the second is
really about ISO:

1. CHI reviewers of a paper claiming *"we formalised our DSL"* expect a normative
   grammar in a citable standard notation. `3dom_grammar.iso.ebnf` is the appendix
   artifact. It exists to be **read and cited**, not run.
2. More sharply: ISO 14977 is a *different* notation with *different* operators, so
   maintaining both files and mechanically cross-checking them is a **redundancy
   check on your own transcription**. A rule you got wrong in one file is unlikely
   to be wrong identically in the other. That is the anti-drift argument (§1.7),
   and it is the real payoff.

**The complete operator set.**

| Operator | Name | Meaning | In your file |
|---|---|---|---|
| `=` | definition | binds LHS to RHS | every rule |
| `,` | **concatenation** | sequence — *explicit*, unlike every other EBNF | `"$S" , "(" , quoted_selector , ")"` |
| `;` | rule terminator | ends a production | every rule |
| `\|` | alternation | **unordered set union** | `verb = "recolor" \| "scale" \| …` |
| `{ }` | repetition | **zero or more** | `{ statement }`, `{ operation_call }` |
| `[ ]` | option | zero or one | `[ argument_list ]`, `[ sign ]` |
| `( )` | grouping | precedence only | `( "selected" \| "lasso" )` |
| `" "` / `' '` | terminal string | a literal; the two quote forms are interchangeable and exist so a literal containing one quote can be written with the other | `"$S"`, `'"'` |
| `? ?` | **special sequence** | an escape into natural language — the standard's own hook for anything EBNF cannot express | `? one decimal digit 0-9 ?` |
| `(* *)` | comment | ignored | the L1–L3 clauses |
| `-` | exception | "this except that" (set difference) | **unused here** |
| `n *` | repetition count | exactly *n* repeats | **unused here** |

**What ISO CANNOT express, and what it forces.**

- **No `+`.** There is no one-or-more operator. The idiom is `A , { A }` — "an A,
  then zero or more A". Your file uses it exactly where W3C uses `+`:
  `identifier = ident_char , { ident_char } ;` ↔ `identifier ::= ident_char+`.
- **No character ranges.** There is no `[a-z]`.

> **⚠ Correction to your brief.** You wrote that this forces "the 52-alternative
> `letter` rule." It does not, and your file does not contain one. ISO 14977
> anticipates exactly this gap and provides the **special sequence** `? … ?` as a
> deliberate escape into prose. Your file uses it four times:
>
> ```
> ident_char = ? one character from A-Z a-z 0-9 or '-' or '_' ? ;
> digit      = ? one decimal digit 0-9 ? ;
> sq_char    = ? any character except the closing single quote ? ;
> dq_char    = ? any character except the closing double quote ? ;
> ```
>
> This is the *right* call and you should defend it, not apologise for it. A
> 52-alternative `letter` rule would have been a disaster for this project
> specifically: it inflates `|N|` and `|P|`, and **`|P|` is an INVARIANT row in
> METRICS.md** — the Alien grammar would have had to reproduce the same inflated
> count, so the noise would propagate into Phase 2's matched-complexity claim.
> The special sequence keeps the character classes *out* of the production count
> and into a separate, honest row: `Lexical char-classes | 5 | INVARIANT`.
>
> The cost is real and worth stating: a special sequence is **prose**, so it is
> not machine-checkable. `grammar_metrics.py` knows this and blanks them before
> analysis (`re.sub(r"\?[^?]*\?", " SPECIAL ", text)`), then declares in its own
> docstring: *"Lexical CHARACTER-CLASS terminals are compared by prose
> correspondence … and excluded here."* That is the honest trade: five
> hand-verified correspondences, in exchange for keeping 52 phantom productions
> out of an invariant.

---

### 1.2 W3C EBNF — XML 1.0, §6 "Notation"

**What it is.** Not a standalone standard. It is the notation the XML 1.0
Recommendation defines *for itself*, in a single section, in order to write its
own grammar. It escaped that document and became the de facto notation of the web
platform: XML, XML Schema, XPath, and — most consequentially for you — it is the
notation the **railroad-diagram generators** and most modern parser-toolkit
tutorials assume.

**Its intended consumer is a machine, or a human who is about to become one.**
Its operators are the regex operators, so it transliterates into a parser
generator almost character-for-character.

**The "Why" for this project, specifically.** Your file's header states it: *"Executable
notation (`::=`, `* + ?`, `[ranges]`). Transliterate into Lark/ANTLR."* This is the
file that becomes runnable. In Phase 2 it literally does — the `.lark` template is
a transliteration of this file with `{{T_TERMINAL_ID}}` slots punched into it.

**The complete operator set.**

| Operator | Meaning | In your file |
|---|---|---|
| `::=` | definition | every rule |
| *juxtaposition* | concatenation — **implicit**, no comma | `'$S' '(' quoted_selector ')'` |
| `\|` | alternation (unordered union) | `verb ::= 'recolor' \| …` |
| `*` | Kleene star, zero or more | `statement*`, `operation_call*` |
| `+` | one or more | `simple_matcher+`, `ident_char+`, `' '+` |
| `?` | optional | `argument_list?`, `sign?`, `whitespace?` |
| `( )` | grouping | `( ',' argument )*` |
| `[a-z]` | character range | `[a-zA-Z0-9_-]`, `[0-9]` |
| `[^']` | **negated** class | `sq_char ::= [^']` |
| `#xN` | character by hex codepoint | **unused here** |
| `'…'` / `"…"` | literal | `'$S'`, `"'"` |
| `A - B` | set difference | **unused here** |
| `/* */` | comment | the L1–L3 clauses |

**What W3C CANNOT express, and what that costs you.**

- **No standardised comment syntax in the Recommendation itself** — `/* */` is
  convention, not spec. Harmless, but note that `grammar_metrics.py` has to strip
  it with a regex it chose, not one the standard defines.
- **No rule terminator.** A rule ends where the next one begins. This is why
  `parse_ebnf` splits with a **lookahead** regex rather than a delimiter:
  ```python
  parts = re.split(r"\n(?=[A-Za-z_][A-Za-z0-9_]*\s*::=)", body)
  ```
  Read that `(?= … )`: split *before* a line that looks like a new rule head,
  consuming nothing. ISO needs no such trick — it splits on `";"`. This is a
  small, concrete illustration of "human-facing notation vs machine-facing
  notation" reversing which one is easier to *machine*-process.
- **Notation-level ambiguity between operator and literal.** `*` is both the
  Kleene star and, in `wildcard ::= '*'`, a literal. ISO has the same problem
  (`sign = "+" | "-"`). This is the miscounting hazard of §1.6, and it is not a
  defect of either notation — it is the unavoidable consequence of a metalanguage
  whose object language reuses its own punctuation.

---

### 1.3 Equal generative power — the desugaring proof

**Claim.** ISO/IEC 14977 and W3C EBNF have exactly the same generative power, and
both have exactly the power of plain BNF: they generate the **context-free
languages**, no more.

**Proof strategy.** Both are *syntactic sugar*. Show that every sugared operator
has a mechanical translation into plain BNF using only concatenation, alternation,
and a fresh non-terminal — with no change to the generated string set. Since BNF
generates exactly the CFLs, and sugar adds nothing, both notations generate
exactly the CFLs. Since ISO's and W3C's operators desugar to the *same* BNF, they
are equal to each other.

> 📖 The theorem that EBNF and BNF are equivalent, with these constructions, is
> standard. Grune & Jacobs, *Parsing Techniques* (2nd ed.), covers EBNF and its
> reduction to BNF in the grammar-notation material of Ch. 2; Hopcroft, Motwani &
> Ullman treat CFGs and derivations in Ch. 5.

**Desugaring 1 — `{ A }` (ISO) ≡ `A*` (W3C), zero or more.**

Introduce a fresh non-terminal `A_star`:

```
A_star  ::=  ε  |  A A_star            (right-recursive form)
```

or equivalently, left-recursively:

```
A_star  ::=  ε  |  A_star A            (left-recursive form)
```

Both generate `{ ε, A, AA, AAA, … } = L(A)*`, the **Kleene closure**.

> 📖 Formally the closure is the **least fixed point** of `X ↦ {ε} ∪ L(A)·X` over
> the lattice of languages ordered by ⊆. This is the standard denotational reading
> of a recursive production, and it is what "the smallest set closed under the
> rule" means. See HMU's treatment of closure properties of regular languages
> (Ch. 4) and the fixed-point characterisation of recursive definitions.

**Which form you pick matters enormously here**, and your engine picks
deliberately. `refgrammar.GRAMMAR` uses the **right-recursive** form everywhere:

```python
"stmts":   [[], ["statement", "stmts"]],
"ops":     [[], ["opcall", "ops"]],
"argtail": [[], ["COMMA", "argument", "argtail"]],
"ctail":   [[], ["combinator", "compound", "ctail"]],
"matchers":[["matcher"], ["matcher", "matchers"]],
```

Two consequences, both load-bearing:

- The parse counter is a **memoized top-down** recogniser, and top-down parsing
  **cannot handle left recursion** — `A ::= A α` recurses forever before consuming
  a token. The code says so: *"No left recursion (top-down-safe)"* and
  *"memoized top-down over a non-left-recursive CFG."*
  📖 Dragon Book §4.3.3, "Elimination of Left Recursion."
- Right-recursion is what makes these rules **right-linear**, which is what carries
  the regularity proof (§3.11).

**Desugaring 2 — `[ A ]` (ISO) ≡ `A?` (W3C), optional.**

```
A_opt   ::=  ε  |  A
```

That is all. Note `[ A ]` is *not* a character class in ISO — a real source of
confusion when reading both files in one sitting, since `[a-z]` in W3C is a class
and `[ A ]` in ISO is an option. **The same bracket means opposite things in the
two notations**, and you have both files open.

**Desugaring 3 — `A , { A }` (ISO) ≡ `A+` (W3C), one or more.**

Compose the first two:

```
A_plus  ::=  A A_star
A_star  ::=  ε | A A_star
```

which flattens to the single rule

```
A_plus  ::=  A  |  A A_plus
```

— and that is *exactly* the shape your engine uses for `matchers`:

```python
"matchers": [["matcher"], ["matcher", "matchers"]],
```

So `compound_selector ::= wildcard | simple_matcher+` desugars into the two-branch
`matchers` rule, and this is why **`matchers` has two coverage obligations**, not
one: `compound:single-matcher` and `compound:multi-matcher(AND)`. **Every desugared
branch becomes a coverage obligation.** That is the mechanical link between the
notation and the 57-obligation count in gate G2, and it is worth internalising:
sugar is invisible in the `.ebnf` file and *visible* in the coverage table.

**Correspondence table — the two notations, side by side.**

| Concept | ISO/IEC 14977 | W3C EBNF | Desugars to |
|---|---|---|---|
| definition | `A = … ;` | `A ::= …` | `A → …` |
| concatenation | `X , Y` (explicit comma) | `X Y` (juxtaposition) | `X Y` |
| alternation | `X \| Y` | `X \| Y` | two productions |
| zero or more | `{ X }` | `X*` | `Xs → ε \| X Xs` |
| one or more | `X , { X }` | `X+` | `Xp → X \| X Xp` |
| optional | `[ X ]` | `X?` | `Xo → ε \| X` |
| grouping | `( … )` | `( … )` | fresh non-terminal |
| terminal | `"x"` or `'x'` | `'x'` or `"x"` | terminal |
| char class | `? prose ?` | `[a-z]`, `[^']` | alternation over the class |
| comment | `(* … *)` | `/* … */` | — |

**Every row is a notation for the same operator and changes no generated string.**
That sentence is your CHANGELOG's support (1) for language equivalence, and the
table above is its expansion.

---

### 1.4 Lark's grammar syntax — the third notation

**Why it exists.** Lark is a *tool*, and a tool's notation has to carry
information a specification does not: which rules produce tree nodes and which are
inlined (`_rule`, `?rule`), which terminals are filtered out, what to `%ignore`,
what to `%import`, terminal-vs-rule case discipline (`UPPER` = terminal, `lower` =
rule), and priorities. These are **implementation directives**, not statements
about the language. A normative grammar must not contain them, because they would
be un-implementable claims about anything but Lark.

**Why the W3C file stays normative.** Three arguments, in ascending strength:

1. **Portability.** W3C EBNF transliterates to Lark, ANTLR, or a hand-written
   recogniser. A `.lark` file is a claim about Lark.
2. **Contamination.** A `.lark` file necessarily contains `%ignore WS`, tree-shaping
   sigils, and terminal priorities. Promote it to normative and your *specification*
   now asserts things about parser internals — and, fatally for you, `%ignore` is
   exactly the directive that would destroy L2 (§5, Trap 1).
3. **The one that decides it — the isomorphism claim.** Phase 2 must argue that
   3DOM and the alien language are the **same grammar** under a renaming. That
   argument is about productions and terminals. If the normative artifact were a
   `.lark` file, the claim would have to cover `%ignore` directives and inlining
   sigils too, and a reviewer could ask whether a difference in *tree shaping*
   breaks the isomorphism. Keeping the normative layer free of implementation
   directives keeps the isomorphism claim purely grammatical.

**What prevents drift — there is exactly one mechanism, and you should be able to
name it under questioning.** It is `grammar_metrics.cross_check`:

```python
def cross_check(w, i):
    problems = []
    nw, ni = set(w["nonterminals"]), set(i["nonterminals"])
    if nw != ni:
        problems.append("nonterminal sets differ: …")
    qw = {q for q in w["quoted"] if q not in ("", "LIT", "SPECIAL")}
    qi = {q for q in i["quoted"] if q not in ("", "LIT", "SPECIAL")}
    if qw != qi:
        problems.append("quoted-terminal inventories differ: …")
    return problems
```

Two set equalities: **identical non-terminal names** (|N| = 31) and **identical
quoted-terminal contents** (39). It runs on every regeneration of METRICS.md and
its result is printed into the file:

> `PASS` — the ISO and W3C files share an identical nonterminal set (|N| = 31) and
> an identical quoted-terminal inventory (39 terminals). The two notations have not
> drifted.

**Note precisely what it does and does not catch**, because this is a
reviewer-facing limit:

- ✅ Catches: a rule added to one file only; a terminal renamed in one file only; a
  terminal deleted from one file only. That is the D2-class failure — the exact
  shape of the defect that produced D2.
- ❌ Does **not** catch: the same non-terminals and the same terminals wired
  together **differently**. `A = X , Y ;` versus `A ::= Y X` passes this check.
  Structure is compared by *inventory*, not by *shape*.

The residual risk is covered by CHANGELOG support (1) — rule-by-rule manual
transliteration — which is human, and by support (3), which is the operational
one: **gate G6** asserts the Earley-style counter and the DFA agree on all 138
corpus items. That is a *behavioural* equivalence check, and it is the strongest
of the three. If a reviewer presses on ISO/W3C equivalence, lead with G6, not with
the inventory check.

**⚠ METHODOLOGIST.** There is no third file for Lark in Phase 1 — the `.lark`
transliteration is a Phase 2 artifact (`grammar/templates/grammar.lark.template`).
So in Phase 1 the "three notations" are really two files plus a plan. When you
write this up, say so; claiming a transliteration that lives in the next phase's
directory is the kind of small imprecision that costs credibility on the details
a reviewer *can* check.

---

## Part B — every Python import, and every import that is conspicuously absent

### 1.5 The honest inventory

⚑ VERIFIED by grep across all Phase 1 Python:

| File | Module-level imports |
|---|---|
| `conformance/coverage.py` | `os`, `sys`, `refgrammar as R` |
| `conformance/coverage2.py` | `os`, `sys`, `refgrammar as R` |
| `grammar_metrics.py` | `os`, `re`, `sys`, `refgrammar as R` |
| `conformance/refgrammar.py` | **none** (one lazy `import os` inside `load_positive_programs`) |

**`lark`, `json`, `pathlib`, `collections`, `itertools` do not appear anywhere in
Phase 1.** Your brief asked me to explain them; the honest and more useful answer
is to explain the four that *are* there, and then treat the five absent ones as
**roads not taken** — because in three cases the choice not to import is a real
architectural decision worth defending.

---

#### `os` — path resolution

**What it is.** OS-level services; here, exclusively `os.path`.

**The "Why".** Every script must locate artifacts relative to **its own file**,
never relative to the shell's working directory:

```python
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "conformance"))
```

**Key components:** `os.path.dirname`, `os.path.abspath`, `os.path.join`.

**Why not `pathlib`?** `pathlib.Path` is the modern, more readable API
(`Path(__file__).resolve().parent / "conformance"`). It would be a fine choice.
Two defensible reasons for `os.path`: it is what `sys.path` wants (a list of
`str`, not `Path` — `pathlib` would need `str()` at that boundary anyway), and
`os.path` is the older, wider-compatibility idiom for a research artifact that may
be run on an unknown machine years from now. **This is a style choice with no
correctness consequence.** Do not defend it as more than that.

#### `sys` — the module path, and the exit code

**The "Why" — two distinct jobs, and the second is the important one.**

1. `sys.path.insert(0, …)` so `import refgrammar` resolves. The engine lives in
   `conformance/`; `grammar_metrics.py` lives one level up. Inserting at index
   **0** rather than appending means the local copy wins over any same-named
   module elsewhere — deliberate, for reproducibility.
2. `sys.exit(main())` — and this is the one that matters. `main()` returns `0` iff
   every gate passes. **That makes conformance a CI-checkable proposition.** The
   grammar's correctness is not a claim in a document; it is an exit code. When a
   reviewer asks "how do you know the corpus still conforms," the answer is a
   command with a testable result, not a paragraph.

`sys.stderr` is also used to separate the human report (stdout) from the
pass/fail verdict (stderr), so `python3 grammar_metrics.py > METRICS.md` would
still show you the verdict.

#### `re` — the EBNF meta-parser (in `grammar_metrics.py` only)

**What it is.** Regular expressions.

**The "Why".** `grammar_metrics.py` must read **two EBNF files in two notations**
and extract non-terminals, terminals, production counts, and operator counts. It
is a parser for a metalanguage — and it deliberately uses regex, not a parser.

**Key components and what each does:**

| Call | Job |
|---|---|
| `re.sub(r"/\*.*?\*/", " ", text, flags=re.S)` | strip W3C comments. `.*?` is **non-greedy** — with greedy `.*` this would delete everything between the *first* `/*` and the *last* `*/`, i.e. the whole file. `re.S` makes `.` match newlines. |
| `re.sub(r"\(\*.*?\*\)", " ", …)` | strip ISO comments; parens escaped. |
| `re.sub(r"\?[^?]*\?", " SPECIAL ", text)` | blank ISO special sequences so prose char-classes are not mistaken for terminals or operators. |
| `re.split(r"\n(?=[A-Za-z_][A-Za-z0-9_]*\s*::=)", body)` | split W3C into rules on a **zero-width lookahead** (§1.2). |
| `re.finditer(r"'([^']*)'\|\"([^\"]*)\"", text)` | harvest quoted-literal **contents** — see below. |
| `re.sub(r"'[^']*'\|\"[^\"]*\"", " LIT ", rhs)` | blank quoted literals before counting `\|` and operators. |

**Why regex and not a real parser for the EBNF files?** Because the task is
**lexical**, not syntactic. Every quantity extracted — rule heads, quoted
contents, top-level `|` counts, operator occurrences — is a token-level property.
Writing a parser for two EBNF dialects to count them would be a second grammar to
maintain, and *that grammar could itself drift*, which is the exact failure mode
this script exists to detect. Regex here is the smaller, more auditable tool.
📖 The lexical/syntactic boundary is Dragon Book Ch. 3 (§3.1, "The Role of the
Lexical Analyzer") — regular expressions suffice for token-level structure and
stop being appropriate the moment you need nesting.

**The one genuinely elegant line — content-keyed literal harvesting:**

```python
for m in re.finditer(r"'([^']*)'|\"([^\"]*)\"", text):
    content = m.group(1) if m.group(1) is not None else m.group(2)
    lits.add(content)
```

Two alternation branches, two capture groups; exactly one matches per hit, so the
`is not None` test picks the live one. The result set holds **contents, not
spellings**. ISO writes `"$S"` and W3C writes `'$S'`; both contribute `$S`. Without
this, the cross-check would report a 39-terminal divergence on every single
terminal, purely because the two notations prefer different quote characters.
**Content-keying is what makes the cross-check about the grammar rather than about
punctuation.**

Note `m.group(1) is not None` and *not* `if m.group(1)` — an empty literal `''`
has content `""`, which is falsy. The explicit `None` test distinguishes "this
branch did not match" from "this branch matched the empty string."

#### `refgrammar as R` — the single source of executable truth

Not a third-party import, but the most important line in both scripts. **One
encoding of the token-level language**, imported by everything. `coverage.py` and
`grammar_metrics.py` both take their automaton facts from `R`, so METRICS.md's
DFA-state count and the conformance suite's accept/reject decision cannot
disagree — they are the same object.

---

#### The five absent imports — roads not taken

**`lark` — absent, and this is the deliberate one.** Phase 1's engine is a
**hand-written recogniser with zero dependencies**. ⚑ VERIFIED: `refgrammar.py`
has no module-level imports at all.

The argument for this is strong and you should make it:

- **The normative grammar must not be defined by a tool's behaviour.** If Phase 1's
  ground truth came from Lark, then "3DOM is the language accepted by Lark 1.x with
  these flags" — and a Lark version bump becomes a change to your language.
- **Independence for cross-checking.** Phase 2 *does* use Lark's Earley
  (`transpiler.py`). Because Phase 1's engine shares no code with it, agreement
  between them is evidence. Two implementations of one specification agreeing is a
  much stronger statement than one implementation agreeing with itself.
- **Reproducibility.** A reviewer, or you in 2029, can run Phase 1 on a bare Python
  install. No pip, no lockfile, no wheel that stopped building.

The cost, stated plainly: you wrote and must maintain a lexer, a parse counter, a
derivation extractor, a Thompson NFA construction, and a subset construction —
**690 lines of parsing infrastructure that is itself unverified except by the
corpus it checks.** Gate G6 (counter ≡ DFA) is the internal consistency check, and
Phase 2's Lark agreement is the external one. That is an adequate answer, but only
if you can state it.

**`json` — absent, and this is a real gap.** `terminals.json` and `ir_schema.json`
are JSON, and **nothing in Phase 1 reads them**. ⚑ I read `terminals.json` with
`json.load` to write this document; no Phase 1 script does. So `terminals.json` —
the *handoff artifact to Phase 2* — is hand-maintained and machine-unchecked
within Phase 1. Its 43 terminals are never asserted against the 39 quoted
terminals `grammar_metrics.py` extracts from the grammar. §5, Trap 7 gives the
concrete check to add; it is about ten lines.

**`collections` — absent, and correctly so.** `collections.Counter` would tidy the
branching-factor profile aggregation, and `defaultdict(list)` would replace
`by_pos.setdefault(idx, []).append(bf)`. Both are cosmetic. `setdefault` is the
zero-import idiom for exactly this, and in a file with a no-imports policy it is
the right call. 📖 The `setdefault`-vs-`defaultdict` trade-off is Fluent Python
Ch. 3, "Handling Missing Keys."

**`itertools` — absent, correctly.** Nothing here needs lazy combinatorics. The
one plausible use is `itertools.chain` in `all_features()`, where `base |
VERB_FEATURES` (set union) is already clearer.

**`pathlib` — absent; §1.5 above. Style only.**

---

### 1.6 The operator-counting problem — why `str.count('*')` is wrong, and what the real numbers are

This is the sharpest small lesson in Phase 1, because **the number goes in your
paper**, and because ⚑ the demonstration in METRICS.md currently misattributes its
own cause.

**The hazard.** In `wildcard ::= '*'` the asterisk is a **terminal of the object
language**. In `statement*` it is an **operator of the metalanguage**. Same
character, two levels. A naive count conflates the level being described with the
level doing the describing — a **use/mention** confusion, and the metalanguage
equivalent of the AST-vs-scene-graph error in TERMINOLOGY.md.

Three literals in your grammar are also metalanguage operators:

```
wildcard ::= '*'              /* Kleene star */
sign     ::= '+' | '-'        /* one-or-more */
```

**What the script does — blank first, count second:**

```python
body_noq = re.sub(r"'[^']*'|\"[^\"]*\"", " LIT ", body)
for ch in "*+?":
    ops[ch] = body_noq.count(ch)
```

Every quoted literal is replaced by the inert placeholder ` LIT `. **It is not
deleted** — deletion could fuse neighbouring tokens; replacement by a spaced
placeholder preserves separation. Then count.

**⚑ VERIFIED — the actual decomposition:**

```
raw * count in 3dom_grammar.w3c.ebnf : 82
after stripping /* … */ comments     :  7
after blanking quoted literals       :  6
```

Now read METRICS.md's demonstration:

> *A naive `text.count('*')` over the W3C file counts 82; excluding quoted literals
> gives the true Kleene-star count **6**.*

**Both numbers are right; the causal claim is wrong.** The 82 → 7 collapse is
**comment stripping** — the file's own `/* … */` delimiters contribute 75
asterisks, plus the `═══` decoration rules. Quoted-literal exclusion accounts for
**exactly one**: the `'*'` in `wildcard`. The sentence credits quote-exclusion with
all 76.

**⚠ METHODOLOGIST.** This matters more than a typo. The paragraph is titled *"the
number that goes in the paper"* and is a **worked demonstration of methodological
care**. A reviewer who reproduces it — and this one is trivially reproducible —
finds the stated mechanism accounts for 1.3 % of the stated effect. That converts
a strength into a liability. The fix is one sentence:

> *A naive `text.count('*')` over the raw W3C file counts 82. Stripping `/* … */`
> comments leaves 7; excluding the quoted literal in `wildcard ::= '*'` leaves the
> true Kleene-star count **6**. Both exclusions are necessary; the second is the
> one that is easy to forget, because a comment is obviously not grammar while a
> quoted `'*'` looks exactly like an operator.*

Same lesson, and now it survives being checked.

**The ISO branch of the same function is worth reading too:**

```python
ops["*"] = body_noq.count("{")     # { } == zero-or-more
ops["?"] = body_noq.count("[")     # [ ] == optional
ops["+"] = 0                       # ISO has no '+' operator
```

It counts **opening brackets** as operator occurrences, having desugared the
correspondence table of §1.3 into three lines. `ops["+"] = 0` is not a stub — it is
the assertion that ISO has no one-or-more operator, which is why the file writes
`A , { A }`. And note that counting `{` is safe here **only** because
`grammar_metrics.py` blanked the ISO special sequences first; had `? … ?` prose
contained a brace, it would have been counted.

📖 The general principle — that a scanner must distinguish an operator of the
describing language from a character of the described language — is the
maximal-munch / token-classification material in Dragon Book §3.4 and §3.8.3.

---

### 1.7 Earley versus LALR — and what your engine actually is

**The claim, from clause P1:**

> *(P1) REFERENCE PARSER = EARLEY. This grammar is intentionally NOT LL(1): on
> seeing whitespace inside a selector the parser cannot choose
> descendant_combinator vs child_combinator without a second token, so k = 2.*

**Why not LALR(1) / LL(1).** The combinator rule needs two tokens (full argument in
§3.12). Concretely:

```
combinator            ::= child_combinator | descendant_combinator
descendant_combinator ::= whitespace
child_combinator      ::= whitespace? '>' whitespace?
```

`FIRST(descendant_combinator) = { whitespace }` and `FIRST(child_combinator) ⊇
{ whitespace }`. The two alternatives' FIRST sets **overlap**, which is precisely
the condition an LL(1) table cannot represent. An LALR(1) generator would report a
shift/reduce conflict.

📖 FIRST/FOLLOW and the LL(1) condition: Dragon Book §4.4.2–4.4.3. Left factoring
as the standard repair: §4.3.4. LALR conflict construction: §4.7.

**Why Earley is the right mandate.** Three reasons, and the third is the one that
actually decides it:

1. **It handles k > 1 directly**, with no grammar surgery. General CFG parsing,
   no lookahead restriction.
2. **Cost is irrelevant here.** Earley is O(n³) worst case, O(n²) for unambiguous
   grammars, O(n) for LR-ish ones; LALR is O(n). ⚑ Your longest verified program
   is 36 tokens. n³ at n = 36 is 46,656 elementary steps. This is a genuine case
   where the asymptotic argument does not apply, and P1 says so: *"inputs are short
   (parse cost is irrelevant)."*
3. **Earley reports ambiguity explicitly.** This is the decisive one. An LALR
   generator resolves a conflict silently (default: shift) and hands you a parser
   that *works* while your grammar is ambiguous. Earley returns **all** derivations,
   so "is this grammar unambiguous?" becomes a **countable, testable property** —
   which is exactly what gate G1 checks: `num_parses(p) == 1`, not `>= 1`. **D3
   would not have been detectable with an LALR front end.** It would have been
   silently resolved and shipped.

**What Earley costs you that LALR would not:** the O(n³) bound (irrelevant here);
no table-construction-time conflict report (you get per-input ambiguity counts
instead, which for this project is *better*); and no free error recovery (LR's
viable-prefix property gives good error locations — you rebuilt that yourself as
`longest_valid_prefix`, §3.13).

📖 Earley's algorithm: Grune & Jacobs, *Parsing Techniques* (2nd ed.), §7.2. The
Dragon Book does not cover Earley in its main line.

---

#### **⚠ The engine is not Earley.** ⚑ VERIFIED.

`refgrammar.py`'s parse counter is documented in its own section header as:

```python
# Exact parse counter (ambiguity detector) — memoized top-down over a
# non-left-recursive CFG. count(sym, i) -> {end: number_of_derivations}.
```

That is **memoized recursive descent** (packrat-shaped), not Earley. `coverage.py`
and the CHANGELOG both call it "the Earley engine."

**Does this matter? Split the question, because the two halves have different
answers.**

*Correctness:* **no.** For this grammar the two are equivalent, and the reason is
stated in the code: the grammar is **non-left-recursive**. Memoized top-down over a
non-left-recursive CFG is a complete recogniser, and because `count(sym, i)`
returns a map `{end_position: number_of_derivations}` and combines alternatives by
**summation** and concatenation by **multiplication**, it computes the exact
derivation count — the same count Earley's forest would yield. The memo table makes
it polynomial. Gate G1's ambiguity test is therefore sound.

*Rhetoric:* **yes.** P1 is a **normative clause**. It says a conforming
implementation MUST use Earley, and your reference implementation does not. And the
difference is not cosmetic: Earley handles left recursion, memoized top-down does
not. The grammar happens to be non-left-recursive, so the substitution is safe —
but that safety is a **property of this grammar**, not of the two algorithms.

**The fix is a rewording, not a rewrite.** Say what is true:

> *(P1) The grammar is intentionally not LL(1) (k = 2), so the reference recogniser
> must be a general CFG parser that reports ambiguity explicitly. Two are used:
> `refgrammar.parse_counts`, an exact memoized top-down derivation counter
> (sound and complete for this grammar because it is non-left-recursive), and, in
> the Phase 2 toolchain, Lark's Earley parser with `ambiguity="explicit"`. Both
> report derivation counts, which is what gates G1 and I10 test.*

That is stronger than the current claim, because **two independent recognisers
agreeing is better evidence than one named algorithm**.

---
---
