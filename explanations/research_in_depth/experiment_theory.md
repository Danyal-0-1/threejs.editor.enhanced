# The theory of this research

*A textbook-style guide to what the research asks and why each part of it is built the way it is.
Companion to [`experiment_math.md`](experiment_math.md) (how every number is computed) and
[`experiment_code.md`](experiment_code.md) (how the code computes it). Written 2026-10-28.*

This guide teaches the ideas behind the experiment, not just their names. The aim is to let you
explain **what is being studied, why each design decision was made, what each measurement can and
cannot show, and what the results mean**.

The recurring example is template `t011` under the held-out lexicon `d50s3`, in both grammar
families:

```text
dom   (function(){ $S('.panel>#frame>camera')#metalness(0.8); })();
blk   $S '.panel>#frame>camera' { metalness 0.8; }
```

The site followed most closely is the type keyword: the correct spelling is `camera`; the familiar
competitor is `mesh`. Under `d50s3`, `mesh` means *group* objects. Both spellings are legal there;
their meanings differ.

Numbers marked **held-out** come from the confirmatory Phase 3.3 run `heldout-20261007a`. Numbers
marked **development** come from `dev-20261006a`. Numbers marked **served** come from Phase 4's run
`dev-20261023a`. **Teaching examples** are invented to explain an idea and are labelled so.

## How to study this guide

Sections 1–5 build the instrument: the question, the language, its two grammars, the lexicons and
the decision sites. Sections 6–12 are the measurements and hypotheses: Arm A, the ladder, Arm B, H4,
H5, H2 and scale. Section 13 is the design that makes a result confirmatory; Section 14 the threats
to validity. Sections 15–17 are what was found, the served models of Phase 4, and where the work
sits in the literature. Section 18 is practice.

### Jump to a topic

- [The question](#1-the-question) · [3DOM](#2-the-language-3dom) · [two grammars](#3-two-grammar-families-dom-and-blk) · [lexicons](#4-lexicons-respelling-the-language) · [sites and collisions](#5-decision-sites-and-collisions)
- [Arm A](#6-measuring-a-preference-arm-a) · [the ladder](#7-adaptation-the-worked-example-ladder) · [Arm B](#8-free-generation-arm-b) · [H4](#9-prediction-h4) · [H5](#10-repair-h5) · [H2](#11-the-interaction-h2-and-why-it-is-not-testable) · [scale](#12-scale-deviations-d10-and-d11)
- [The confirmatory design](#13-making-a-result-confirmatory) · [threats to validity](#14-threats-to-validity-and-how-each-is-handled)
- [What was found](#15-what-was-found) · [served models](#16-phase-4-newer-and-larger-models-served-by-an-api) · [the literature](#17-where-this-sits-in-the-literature) · [practice](#18-practice-glossary-and-the-whole-research-said-aloud)

At the end of each main topic, **Say it aloud** gives a sentence you can use in a research
discussion.

---

## 1. The question

### 1.1 Habits against instructions

Imagine two doors. One leads to meshes and one to groups. Everyone who has ever used these doors
knows that the sign `mesh` is on the mesh door. A new building manager repaints the signs and hands
you a printed card: "in this building, the mesh door says `camera`, and the sign `mesh` is on the
group door." You read the card. Then you walk up to the doors. Which sign do you follow?

A code model is in exactly this position when a domain-specific language (DSL) borrows a familiar
surface and changes what parts of it mean. The model has seen `.wheel` mean "class wheel" and
`#panel` mean "id panel" millions of times in CSS and jQuery. The prompt says that in this language
`#` is the class sigil. At the moment it must type the sigil, the habit and the instruction
compete.

### 1.2 Why it matters

DSLs are everywhere: configuration languages, query languages, tool schemas, the small languages an
application defines for its own model. They are usually **specified in the prompt**, and they
usually **borrow familiar surface**, because familiar surface is easier for people to read.

When the habit wins, the result is not a syntax error. It is a **valid program that does the
wrong thing**: it selects groups instead of meshes, or copies instead of moves. Such errors are
silent; no parser complains. That is what makes them dangerous, and what makes them worth
measuring precisely.

### 1.3 The precise questions

The research asks five questions, each tied to a measurement:

1. **How often** does a model write the familiar spelling where the specification defines another,
   even with the specification in its prompt? (Arm A: reversion rate)
2. **How much** does the specification help? (Arm A: the rule effect, against two controls)
3. **How many worked examples** does it take before the model switches? (the ladder: `k*`)
4. **Can we predict** which exact sites will fail, before running the model people actually use?
   (H4)
5. **Can we repair** the language by respelling only the risky symbols? (H5)

A sixth, about real generation rather than forced choice, runs alongside: when a model writes a
program freely, does it reach the decision at all, and then which spelling does it write? (Arm B)

### 1.4 What is not the question

- **"Do models reason, or only pattern-match?"** Both words are loaded and neither has a measurable
  definition here. The study measures something narrower: whether the prompt-defined spelling or the
  familiar one is preferred at a defined place.
- **Learning a new language in general.** The languages here are deliberately *isomorphic* to 3DOM:
  same grammar, same meanings, different spellings. Only the surface changes.
- **3D knowledge.** The verb sites need some understanding of the request; the sigil sites do not.
  The strata (Section 5.3) keep these apart.

**Say it aloud:** "We measure, at the exact token where a prompt-defined spelling competes with a
familiar one, how often the familiar one wins, how much the specification and worked examples
change that, and whether a base model's preference predicts its instruction-tuned twin's failures."

---

## 2. The language: 3DOM

### 2.1 Where it comes from

3DOM was formalised in Phase 1 as the command language of a natural-language 3D editor built on the
Three.js editor. A program selects objects in the scene graph with a CSS-like selector and applies
operations to them in a jQuery-like chain:

```text
(function(){ $S('#panel>.frame>mesh').metalness(0.8); })();
```

Read it as: select the **meshes** that are direct children of objects of **class `frame`**, which
are direct children of the object with **id `panel`**, and set their metalness to 0.8. The wrapper
`(function(){ … })();` is an immediately invoked function expression (IIFE), mandatory in the
grammar.

The parts:

| part | spellings | meaning |
|---|---|---|
| selector entry | `$S` | start a selection |
| id sigil | `#` | the object with this id (`userData.label` or name) |
| class sigil | `.` | objects of this class |
| type keywords | `mesh`, `group`, `light`, `camera` | Three.js object kinds |
| wildcard | `*` | every object |
| pseudo-selectors | `:selected`, `:lasso` | the editor's current or lasso selection |
| combinators | `>` (child), a space (descendant) | relations between selector steps |
| chain operator | `.` | attach an operation |
| verbs (exactly 15) | `recolor`, `scale`, `move`, `rotate`, `delete`, `spin`, `duplicate`, `setMaterial`, `setOpacity`, `setVisible`, `wireframe`, `metalness`, `roughness`, `castShadow`, `receiveShadow` | the closed set of operations |

Notice that `.` plays two roles: the class sigil inside the quoted selector, and the chain operator
outside it. That overload is real CSS/jQuery practice, and it matters later (Section 4.1).

### 2.2 A grammar with two levels

The grammar is written in ISO EBNF and W3C EBNF (version `3dom-grammar/1.1.0`) and parsed with an
Earley parser. It has two levels:

- the **outer** level: the wrapper, `$S(…)`, the chain of `.verb(args)`;
- the **inner** level: the selector inside the quotes, where whitespace is **significant**
  (`'.car .wheel'`, a descendant, is a different program from `'.car.wheel'`, a compound).

The conformance suite requires every valid program to have **exactly one** derivation (zero
ambiguity). That property is what makes "the program parses" a precise statement.

### 2.3 Terminals: what can be respelled

The grammar has **43 terminals**. **29 are substitutable**: their spelling is a familiarity signal
(sigils, keywords, verbs, `$S`, `function`). **14 are frozen**: structural delimiters (`(`, `)`,
`{`, `}`, `;`, `,`), the quote characters, the numeric signs, identifiers, numbers, string bodies and
the significant whitespace. Freezing them keeps every respelled language exactly as hard to parse as
3DOM.

Because `.` is shared by the chain operator and the class sigil, the 29 substitutable terminals have
**28 distinct spellings**. The token table shown to models (Section 6.2) lists 28 roles: every
substitutable terminal except `function`.

### 2.4 Meaning: the canonical IR

Two programs mean the same thing exactly when they lower to the same **canonical intermediate
representation** (IR). The IR of `t011` is:

```json
{"grammar_version":"3dom-grammar/1.1.0",
 "ops":[{"op":"metalness","args":{"metalness":0.8},
         "selector":{"raw":"#panel>.frame>mesh",
                     "steps":[{"combinator":null,"matchers":[{"kind":"id","name":"panel"}]},
                              {"combinator":"child","matchers":[{"kind":"class","name":"frame"}]},
                              {"combinator":"child","matchers":[{"kind":"type","name":"mesh"}]}]}}]}
```

The canonicalisation rules (C0–C9) fix one form for every meaning: one number format (`1.50` → `1.5`),
one quote character, compound matchers sorted (they are ANDed, so order does not matter), operation
order kept (it does matter), and a selector `raw` string always rendered in 3DOM's own spelling. The
**content hash** is the SHA-256 of the canonical JSON; for `t011` it begins `fcdf05187d6a4e49`.

The IR is the ground truth of the whole study. A respelled program is correct if and only if it
lowers to the target hash; a site is a real collision if and only if swapping in the familiar
spelling changes the hash.

### 2.5 The 80 templates

The experiment's programs are **80 templates**, built as IR rather than written as text:

- 20 selector shapes, chosen to exercise every production of the selector grammar (a single class,
  an id, a type, a wildcard, compounds, child and descendant chains up to three steps, pseudo-selectors);
- each shape used in programs of 1, 2, 3 and 4 statements, with verbs and argument values rotating
  through the 15 verbs.

Building them as IR has three consequences: every template is valid by construction; the **same**
template can be rendered in both grammar families and in every lexicon, so a comparison varies only
the surface; and the target meaning of every program is known exactly, so free generation can be
graded without a human judge.

**Say it aloud:** "3DOM is a two-level grammar over the Three.js scene graph; its programs lower to
a canonical IR, and the IR hash, not the text, defines what a program means."

---

## 3. Two grammar families: `dom` and `blk`

### 3.1 Why one grammar is not enough

Respelling one grammar in nine ways still gives nine versions of *one* concrete syntax. A finding
could then be a property of that syntax, for example of the IIFE opening every program shares.
Phase 3.2 therefore added a **second grammar family** for the same meanings.

### 3.2 The two families

| | `dom` (Phases 1–2) | `blk` (Phase 3.2) |
|---|---|---|
| a program | `(function(){ $S('…').op(a).op(b); })();` | `$S '…' { op a; op b; }` |
| wrapper | IIFE | none |
| operations attach by | a fluent chain `.op(…)` | statements inside a block |
| argument delimiters | parentheses | none (juxtaposition) |
| `function`, chain operator, parentheses | used | absent |

What is held **fixed** on purpose:

- the **terminal table**, so the same lexicons apply to both families unchanged;
- the **inner selector language**, parsed by the same code in both, so the sigil and keyword
  collisions are the same contrast in both families;
- the **canonical IR**: `$S '.wheel' { recolor 'x'; scale 2; }` and
  `$S('.wheel').recolor('x').scale(2)` produce byte-identical IR.

### 3.3 The running example in both families

| | `dom` | `blk` |
|---|---|---|
| 3DOM | `(function(){ $S('#panel>.frame>mesh').metalness(0.8); })();` | `$S '#panel>.frame>mesh' { metalness 0.8; }` |
| `d50s3` | `(function(){ $S('.panel>#frame>camera')#metalness(0.8); })();` | `$S '.panel>#frame>camera' { metalness 0.8; }` |
| characters before the keyword site | 31 | 18 |

The keyword decision is the same contrast in both; what differs is everything around it. `blk` is
less familiar to models: nothing like it appears in ordinary code.

### 3.4 What `blk` can and cannot test

`blk` was meant to be a **held-out grammar family**: a test of whether H4 generalises to a syntax
never seen during development (criterion C3). But `blk × d50s1` was scored before the freeze, and
the preregistration itself reported that `blk` behaves like `dom`. Deviation D1 therefore
reclassified it: `blk` cells on new mappings are **HELDOUT-WEAK-FAMILY** ("a seen grammar, an
unseen mapping"), and C3 is **NOT TESTABLE**.

**Say it aloud:** "`dom` and `blk` are two concrete syntaxes for one IR; holding the terminals and
the selector language fixed makes the collision the same contrast in both."

---

## 4. Lexicons: respelling the language

### 4.1 A φ-map

A **lexicon**, or **φ-map**, assigns a spelling to each of the 29 substitutable terminals, keyed by
the terminal's id (never by its character, so the two roles of `.` stay distinct). 3DOM itself is
the **identity** lexicon. Every lexicon is validated mechanically (checks V1–V8) before use:

| check | what it guarantees |
|---|---|
| V1 | the lexicon targets grammar 1.1.0 |
| V2 | every substitutable terminal appears exactly once |
| V3, V7 | no frozen terminal is respelled, and the frozen list is complete |
| V4 | each entry's source spelling matches `terminals.json` |
| V5 | the chain operator and the class sigil share one spelling (invariant I7) |
| V6 | two terminals share a spelling exactly when they share one in 3DOM: the map is a bijection on spellings, so it can be inverted |
| V8 | no spelling contains a character the lexer already claims (quotes, delimiters, signs, digits, layout) |

Invariant I7 says the overload of `.` must be preserved: de-overloading it would make a respelled
language easier to lex than 3DOM.

### 4.2 Phase 2's alien lexicons, and what they taught

Phase 2 built three "alien" lexicons:

- **`alpha`** permutes the five structural symbols `. # : > *` in a cycle;
- **`beta`** respells everything into pronounceable pseudo-words from an alphabet disjoint from CSS
  (`mesh` → `plel`, `move` → `brom`, `#` → `%`), matched in character length to keep tokenizer
  fertility near 1;
- **`gamma`** uses unusual Unicode glyphs.

Phase 3 measured what `alpha` does at the class-sigil site: the familiar `.door` does not parse,
because under `alpha` `.` is the wildcard, which takes no identifier. The habit then produces a
**loud** failure, not a silent one. The design rule that followed: **silent collisions need a
permutation within a shape class**, among roles that accept the same syntax. In 3DOM the shape
classes are the two sigils {class, id}, the four type keywords, the two pseudo keywords, and the
verbs grouped by argument signature.

### 4.3 The delta family

The experiment's lexicons are generated (Phase 3.2) as a **family** with two parameters:

- **density**: the target share of the 29 terminals to permute: 25%, 50% or 75%;
- **seed**: which shape-class groups are drawn, and the rotation order inside each group.

Each chosen group is **rotated**: every member takes the next member's spelling. Two modes exist.
**Strict** mode permutes verbs only within an identical argument signature; only {`move`,
`duplicate`} and {`wireframe`, `castShadow`, `receiveShadow`} qualify, so strict mode cannot reach
75%. **Arity** mode permutes verbs with the same number of arguments (nine verbs take one argument);
it reaches 75% at a cost: swapping `recolor` with `setOpacity` changes the argument's key too, so
the IR differs in a semantically odd way. Lexicons made in arity mode carry an `a` suffix.

`d50s3` (density 0.5, seed 3, strict) remaps 14 terminals:

| role | 3DOM | `d50s3` | so the familiar spelling now means |
|---|---|---|---|
| class sigil (and chain operator) | `.` | `#` | the id sigil |
| id sigil | `#` | `.` | the class sigil |
| type: mesh | `mesh` | `camera` | groups |
| type: group | `group` | `mesh` | lights |
| type: light | `light` | `group` | cameras |
| type: camera | `camera` | `light` | meshes |
| pseudo: selected | `selected` | `lasso` | the lasso selection |
| pseudo: lasso | `lasso` | `selected` | the current selection |
| verb: move | `move` | `duplicate` | copy |
| verb: duplicate | `duplicate` | `move` | move |
| verbs: castShadow, receiveShadow, wireframe | | `receiveShadow`, `wireframe`, `castShadow` | each other |

Why not remap everything? **H5 needs controls**: sites whose roles were not remapped, to check that
a repair does not harm ordinary sites. Every member keeps its unpermuted roles as within-language
controls.

### 4.4 The nine lexicons

| lexicons | density, mode | role in Phase 3.3 |
|---|---|---|
| `d25s1`, `d25s2`, `d50s1`, `d50s2` | 25–50%, strict | **development** |
| `d25s3`, `d50s3` | 25%, 50%, strict | **held-out mappings** |
| `d75s1a`, `d75s2a`, `d75s3a` | 75%, arity | **held-out mappings** |

Seeds counterbalance: across lexicons, no spelling is "always correct" and no role is tied to one
spelling. `d25s2` never draws the sigil group, so it has no sigil sites at all (its sigil cells are
"structurally empty", not missing).

**Say it aloud:** "A lexicon is a validated bijection on spellings; ours permute familiar spellings
within shape classes, so the familiar habit produces a valid but wrong program instead of a syntax
error."

---

## 5. Decision sites and collisions

### 5.1 What a site is

A **decision site** is one occurrence of one substitutable terminal in one rendered program. At a
site, two spellings compete:

- the **correct** spelling $c$ = φ(terminal), what the lexicon defines;
- the **familiar** competitor $q$ = the 3DOM spelling of the same role, what the habit suggests.

The site's **prefix** is the program text before it. Its id names everything:
`dom:d50s3:t011:T_TYPE_MESH:0` is the first `T_TYPE_MESH` occurrence in template `t011`, rendered in
`dom` under `d50s3`.

### 5.2 The collision taxonomy

Whether a site is dangerous is not assumed; it is **tested**. Substitute $q$ for $c$ at the exact
offset and re-parse:

| class | the variant program… | consequence of a reversion |
|---|---|---|
| **NONE** | is identical: the role was not remapped ($c = q$) | no contrast |
| **LEXICAL** | does not lex or parse | a loud failure; the parser catches it |
| **BENIGN** | parses to the **same** IR | no harm: $q$ is an alias |
| **SEMANTIC** | parses to a **different** IR | a silent wrong program |

Only **SEMANTIC** sites are used: there both spellings are grammar-valid and their meanings differ,
which is the condition the literature review set and the one where a reversion is silent.

The running example in `dom` under `d50s3`:

| site | correct | familiar | class | the familiar spelling now means |
|---|---|---|---|---|
| id sigil, offset 17 | `.` | `#` | SEMANTIC | the class sigil |
| class sigil, offset 24 | `#` | `.` | SEMANTIC | the id sigil |
| type keyword, offset 31 | `camera` | `mesh` | SEMANTIC | group objects |
| chain operator, offset 39 | `#` | `.` | LEXICAL | nothing: `.metalness` does not parse, since `.` is now an inner sigil |
| `function`, `$S`, both `>`, `metalness` | unchanged | | NONE | |

In `blk` the same three inner sites are SEMANTIC, and there is no chain operator.

Sites are located with the grammar's own lexer, never by searching the text: `#` is also the first
character of every colour literal `'#111111'`, and a text search would invent collisions inside
arguments.

### 5.3 Strata

Sites are grouped by the kind of role, because the kinds ask different things of a model:

| stratum | terminals | what reverting there reveals |
|---|---|---|
| **sigil** | class, id, pseudo sigils; child; wildcard; chain operator | a pure surface habit: no 3D knowledge is needed to type `#` or `.` |
| **keyword** | the four type keywords and two pseudo keywords | a habit tied to a word that also names a concept |
| **verb** | the 15 operation verbs | a habit plus understanding the request: choosing `move` requires knowing what is asked |

A difference between sigil and verb sites is confounded with token length (a sigil is one
character, a verb a word), which the analysis handles by comparing only sites with the same token
lengths.

### 5.4 One site per prefix

Two sites are the same **stimulus** if the model sees exactly the same context: the same rule
table and the same program prefix. The rule table depends on the lexicon, so sites are
de-duplicated **within each (family, lexicon) cell**, keeping one site per distinct prefix by a
fixed canonical order.

Every `dom` program opens with the same 17 characters `(function(){ $S('`, so the first symbol of
every selector (a sigil, a keyword or a pseudo-selector) has the same prefix. Only one of those
survives per cell. That is why `t011`'s id-sigil
site (offset 17) is dropped as a duplicate, while its class-sigil and keyword sites, which follow
template-specific text, are kept.

### 5.5 The held-out sites

Over the 80 templates, the five held-out lexicons and both families, the classifier finds 4,700
SEMANTIC sites. De-duplication drops 1,670, leaving **3,030: 1,515 per family**.

| lexicon | `d25s3` | `d50s3` | `d75s1a` | `d75s2a` | `d75s3a` |
|---|---:|---:|---:|---:|---:|
| sites per family | 220 | 272 | 341 | 341 | 341 |

By stratum, in each family: 755 sigil, 487 verb and 273 keyword sites. The same 3,030 sites were
scored for every one of the 21 Phase 3.3 models and the nine Phase 4 served models.

**Say it aloud:** "A site enters the study only if the familiar spelling, swapped in at that exact
place, still parses to a different canonical IR; then a reversion there is a silent wrong program."

---

## 6. Measuring a preference: Arm A

### 6.1 Forced choice at an exact prefix

Arm A does not let the model write freely. It hands the model the context up to the decision and
asks which of the two spellings it supports more, by comparing their log-probabilities:

$$
M = \log P(c \mid r, x) - \log P(q \mid r, x),
$$

where $r$ is the specification in the prompt and $x$ the program prefix. $M > 0$: the model prefers
the defined spelling. $M < 0$: it prefers the familiar one, a **reversion**. Because both candidates
are scored in the same context, everything shared cancels; $M$ is a log-likelihood ratio. Scoring
starts at the first token where the two candidates differ, which handles tokenizers that merge a
candidate's first characters into the preceding token ([`experiment_math.md` §3.3](experiment_math.md#33-why-the-scorer-starts-at-the-first-token-divergence)).

Forced choice has two strengths. It removes the question of whether the model would ever *reach*
the decision (Arm B's problem), so every site gives a measurement. And it can be computed for a
**base** checkpoint, a pretrained model never tuned to follow instructions, which is what H4 needs.

### 6.2 The three conditions

| condition | what precedes the program | tokens (Qwen tokenizer) |
|---|---|---:|
| **`rule`** | the full token table for the lexicon: 28 roles and their spellings | 298 |
| **`norule`** | the same framing and role list, spellings withheld | 237 |
| **`norule_lenmatched`** | `norule` padded with copies of a neutral line until it is at least as long as `rule`, counted in the model's own tokens | 307 |

The `rule` prompt for `d50s3` begins:

```text
You are writing 3DOM, a domain-specific language for editing 3D scenes.
3DOM resembles CSS and jQuery, but several tokens have been REASSIGNED.
The table below is authoritative and overrides any CSS or JavaScript
convention you may expect.

TOKEN TABLE
  selector entry                     $S
  class selector sigil               #
  id selector sigil                  .
  …
  type keyword: mesh object          camera
  type keyword: group object         mesh
  …
Write 3DOM using exactly the spellings above.
```

The table is **rendered from the lexicon itself**, never written by hand: a hand-written table could
drift from the grammar, and the model would be graded against a mapping it was never told. Every
site is checked against its prompt before scoring (defect P33-006 once paired sites with another
lexicon's table).

The two controls answer different alternative explanations. `norule` asks whether the table's
**information** matters. `norule_lenmatched` asks whether it is only the extra **length** of the
rule prompt: the table is longer, and a longer context could change a preference by itself.

Three **paraphrases** of the rule prompt (p0 the default, p1 terse, p2 explicit about the conflict)
check that the results do not depend on one wording.

### 6.3 Reversion and the rule effect

- The **reversion rate** of a model in a cell is the share of its sites with $M < 0$ under `rule`.
- The **rule effect** at a site is $M_{\text{rule}} - M_{\text{control}}$: how far the table moved the
  preference. Averaged over sites, with an interval that resamples templates.

A positive rule effect does not mean the table *wins*: it can move a margin from −5.1 to −4.5 and
the familiar spelling still wins.

### 6.4 The running example

Qwen2.5-Coder-0.5B (base) at `dom:d50s3:t011:T_TYPE_MESH:0`, held-out:

| condition | log P(`camera`) | log P(`mesh`) | $M$ |
|---|---:|---:|---:|
| `rule` | −6.082 | −1.570 | **−4.512** |
| `norule` | −8.560 | −3.457 | −5.103 |
| `norule_lenmatched` | −8.275 | −2.847 | −5.428 |

With the table, the base model still prefers `mesh` by a factor $e^{4.512} \approx 91$. The table
helped (+0.59 nats against `norule`, +0.92 against the length-matched control), but not nearly
enough. Its instruction-tuned twin, Qwen2.5-Coder-0.5B-Instruct, gives $M = -0.638$ under `rule`:
much closer to a coin flip, but still a reversion.

### 6.5 Measurement precision

The outcome is the **sign** of $M$, so a margin near zero must be measured precisely. The models ran
in bf16, which keeps only 8 significant bits: near 20, neighbouring bf16 values are 1/8 apart, so a
logit can be off by up to 1/16. The scorer therefore recomputes the final projection to the
vocabulary in fp32 (defect P33-002). In the held-out
run, none of the 190,890 Arm A margins was an exact tie.

**Say it aloud:** "Arm A asks, at an exact prefix, which of two spellings the model supports more;
the table's effect is measured against both a no-table control and a control of the same length."

---

## 7. Adaptation: the worked-example ladder

### 7.1 More evidence, in context

The token table *tells* the model the mapping. Worked examples *show* it. The **ladder** keeps the
table and inserts $k$ complete example programs written in the lexicon before the prefix, for

$$
k \in \{0, 1, 2, 4, 8, 16, 32\}.
$$

No weights change: this is in-context adaptation. The question is how much demonstrated evidence it
takes to override the habit.

### 7.2 Clean, nested evidence

Two properties make the ladder a measurement rather than a trick:

- **Leak-free.** An example never comes from the site's own template, never is the site's program,
  and never replays the site's decision prefix beyond the opening every program shares. The first
  ladder (Phase 3.3 on the laptop) used templates t000–t031 for every site, and 82 of its 120 sites
  saw their own answer among the examples (defect P33-008). For `dom:d50s3:t011:T_TYPE_MESH:0`, the
  pool order skips `t071`, `t031` and `t051` (they replay the decision prefix) and `t011` itself.
- **Nested.** The examples come in a fixed seeded order, so the 2-example set is the 1-example set
  plus one more. Along a curve, only the dose changes.

### 7.3 The extinction threshold `k*`

`k*` is the **first** example count at which the margin becomes non-negative, interpolated between
the two rungs around the crossing. Three cases:

- already correct at $k = 0$ ($M(0) \ge 0$): $k^* = 0$;
- crosses on the ladder: the interpolated first upward crossing;
- never crosses by 32: **censored**: we know only that $k^* > 32$.

The curves are rarely smooth. A curve can cross and fall back (it **recrosses**); the first rung from
which it stays non-negative is recorded separately as `sustained_k`.

### 7.4 Summarising with censoring

A model's adaptation is summarised by the **Kaplan–Meier median** of `k*` over the sites that start
wrong: the example count by which half of them have switched. Kaplan–Meier keeps censored sites in
the denominator until the end of observation, so the hardest sites are not dropped
([`experiment_math.md` §10](experiment_math.md#10-kaplanmeier-median-and-censoring)).

### 7.5 The running example, in two grammars

The same site, the same model (Qwen2.5-Coder-0.5B base), held-out:

| $k$ | 0 | 1 | 2 | 4 | 8 | 16 | 32 | `k*` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `dom` | −4.512 | −3.492 | **+2.606** | +1.798 | +2.309 | +2.792 | +4.909 | **1.57** |
| `blk` | −3.755 | −2.710 | −2.944 | −3.971 | −4.053 | **+4.154** | +4.796 | **11.95** |

In `dom`, two examples are enough. In `blk`, the model needs between 8 and 16. The same holds for
the whole population of sites: for every one of the 21 models, the Kaplan–Meier median (Section
7.4) is larger in `blk` than in `dom`, by a factor of 1.1 to 5.0 (2.3 for the middle model). One
reading: worked examples teach faster when the rest of the syntax is already familiar.

**Say it aloud:** "`k*` is the first number of worked examples at which the model prefers the
defined spelling; sites that never switch are censored, and Kaplan–Meier keeps them in the summary."

---

## 8. Free generation: Arm B

### 8.1 What the model actually writes

Arm A forces a choice at a prefix the model may never have produced itself. Arm B asks the
instruction-tuned models to **write** each program from a natural-language request, rendered
deterministically from the IR:

```text
Request: Set the metalness of meshes directly inside objects of class 'frame' directly inside the object with id 'panel' to 0.8.
Program:
```

The prompt carries the token table, an instruction, and four leak-free worked examples, each a
request with its program. Decoding is greedy, up to 192 new tokens.

### 8.2 Two outcomes per program

**The program** is graded against the target IR into one of five buckets: `LEX_FAIL`,
`PARSE_FAIL`, `VALID_VACUOUS` (parses but does nothing), `VALID_WRONG`, `VALID_CORRECT`.

**Each site** is then observed as a **hurdle** with two stages:

1. **reach**: the generated text, with layout normalised, reproduces the target exactly up to the
   site;
2. **reversion given reach**: having reached it, the model writes the familiar spelling.

The two rates are reported separately and never multiplied. A model that rarely reaches sites
would otherwise look like a model that rarely reverts. (Phase 2's Experiment 02 made exactly that
mistake: "3/3 bare versus 15/20 scaffolded reversions" looked like scaffolding increased reversion,
when bare outputs simply reached the site less often.)

One consequence of the strict definition: a reversion at a decision that is **not** one of the
cell's sites, such as the first selector symbol (kept for one template only, Section 5.4), is not
counted as a reversion anywhere. It shows up only as lower reach at the sites after it.

### 8.3 The running example

Held-out, `t011` under `d50s3`:

| family | model | wrote | bucket | keyword site |
|---|---|---|---|---|
| `blk` | Qwen2.5-Coder-1.5B-Instruct | `$S '.panel>#frame>mesh' { metalness 0.8; }` | VALID_WRONG | reached, **reverted** |
| `blk` | DeepSeek-Coder-33B-Instruct | `$S '.panel>#frame>camera' { metalness 0.8; }` | VALID_CORRECT | reached, correct |
| `dom` | Qwen2.5-72B-Instruct | `(function(){ $S('#panel>camera.frame')#metalness(0.8); })();` | VALID_WRONG | not reached |

The 72B model's `dom` program begins `#panel`: the familiar id sigil, where `d50s3` requires `.`. It
diverged from the target before the keyword site, so that site was never reached. No model reached
it in `dom`.

**Say it aloud:** "Arm B separates whether a model gets to the decision from what it chooses there,
because a model that never arrives can look like a model that never reverts."

---

## 9. Prediction: H4

### 9.1 The claim

> **H4 (confirmatory, the primary scientific claim).** A base checkpoint's preference between the two
> spellings at an exact site predicts which sites its instruction-tuned checkpoint gets wrong, on
> held-out mappings.

Why it should hold: instruction tuning is a thin layer of training on top of pretraining. The habit
lives in the pretrained weights; if it survives tuning, the base model's preference is a measurement
of the habit that the tuned model inherits. Why it matters: the base margin can be computed for every
site of a new DSL **before** any instruct model is run, and it says *where* the danger is, not just
how much of it there is.

### 9.2 Risk and label

$$
\text{risk}_i = -M_i^{\text{base}}, \qquad Y_i = \mathbf{1}\left[M_i^{\text{instruct}} < 0\right],
$$

both under `rule`. Risk is oriented so that larger means more dangerous. The label comes from a
**different checkpoint** than the risk: using one model for both would build the result into the
definitions.

### 9.3 Baselines

A predictor is only interesting if it beats simpler ones:

| baseline | the alternative explanation it represents |
|---|---|
| **identity** (was the role remapped?) | any respelling at all is the problem |
| **length** (bytes of $q$ minus bytes of $c$) | longer spellings are the problem |
| **program NLL** per character | the whole program looks unfamiliar |
| **token count** | tokenization burden |
| **`terminal_rate`** (exploratory) | the *role* is hard, not the *site*: the reversion rate of the site's terminal elsewhere, cross-fitted |

On the eligible sites every role is remapped, so the identity baseline is constant and its AUROC is
exactly 0.5 (deviation D6). Criterion C1 therefore amounts to "AUROC ≥ 0.60 with an interval above
the coin".

### 9.4 Calibration and threshold

A ranking score can also be turned into a probability. On development data, a logistic (Platt)
curve $\hat p = \sigma(a + b \cdot \text{risk})$ and a decision threshold (Youden's) were fitted for
each development pair and **frozen**. For the 0.5B pair, $a = -0.2984$, $b = 0.9014$, threshold
0.364. At the running example, risk 4.512 gives $\hat p = 0.977$: a confident warning, and a correct
one.

The registered **criteria are rank-based** (AUROC), so they do not depend on calibration at all.

### 9.5 The criteria

| criterion | requirement |
|---|---|
| **C1** | AUROC(risk) − AUROC(identity) ≥ 0.10, with a 95% template-bootstrap interval above 0 |
| **C2** | AUROC(risk) − AUROC(length) ≥ 0.05, interval above 0 |
| **C3** | AUROC ≥ 0.65 on a held-out *grammar*: **NOT TESTABLE** (D1) |

Holm's correction is applied over C1 and C2; each grammar family is tested separately and never
pooled.

**Say it aloud:** "H4 says the habit is predictable at the site level: the base model's own margin
ranks the sites its instruction-tuned twin will get wrong, better than respelling, length,
unfamiliarity or token count."

---

## 10. Repair: H5

### 10.1 The claim

> **H5 (confirmatory, applied).** Respelling only the predicted-high-risk roles reduces reversion more
> **per changed symbol** than respelling random roles, while sites of unchanged roles do not get
> worse by more than 0.02.

It turns H4's diagnosis into an intervention, and the per-symbol framing makes it a claim about
**efficiency**: not "renaming helps", but "renaming *these* helps most for the least change".

### 10.2 What a repair does

A repaired role takes its spelling from `beta`, whose alphabet is disjoint from CSS. The repaired
lexicon must pass all of V1–V8, and an exhaustive **IR proof**: every one of 142 programs (the 62
Phase 1 conformance programs plus the 80 templates), in both families, must keep its canonical IR
when rendered and parsed under the repaired lexicon.

A repair does not always remove the danger. In a permuted lexicon, the familiar spelling of a
repaired role usually still means *another* role. Repair the id sigil of `d50s3` (`.` → `%`), and
`t011` becomes:

```text
dom   (function(){ $S('%panel>#frame>camera')#metalness(0.8); })();
```

| site after the repair | correct | familiar | class |
|---|---|---|---|
| id sigil | `%` | `#` | still **SEMANTIC**: `#` is the class sigil |
| class sigil | `#` | `.` | now **LEXICAL**: `.` no longer means anything |
| type keyword | `camera` | `mesh` | unchanged, SEMANTIC |

Repairing one role changed another role's site from silent to loud, and left its own site silent.
Only renaming **every** remapped role removes the silent errors.

### 10.3 The arms

For each instruct model, grammar and lexicon:

- **targeted**: the 3 remapped roles with the highest mean base-model risk;
- **random**: 3 remapped roles drawn at random, repeated with seeds 1–5;
- **global**: every remapped role.

### 10.4 What was found, and what was not tested

As reported (deviations D12, D13), H5 was **not supported**: targeted beat the mean of the random
arms in 43 of 100 cells, with a mean difference of −0.41 reversions saved per changed role; the
registered interval test, implemented post hoc, gave `dom` −0.77 [−1.96, +0.40] and `blk`
−0.04 [−1.19, +1.12].

While preparing these files, a defect was found (2026-10-28): in 84 of the 100 cells, the targeted
arm was scored with **another model's** targeted repair, the one chosen for Llama-3.2-1B-Instruct in
`dom` ([`experiment_code.md` §11.6](experiment_code.md#116-a-defect-found-on-2026-10-28-the-targeted-arm-scored-the-wrong-lexicon)).
In the 16 cells scored as designed, targeted beat random in 14, by +2.83 on average; in the 84 others,
in 29, by −1.02 on average. The 16 cells are not a random sample, so this is a post-hoc observation,
not a result. What it does establish is that **H5 was not tested as designed**: the verdict "not
supported" does not answer the registered question, and answering it needs the targeted arms scored
again with the right lexicons.

**Say it aloud:** "H5 asks whether respelling only the predicted-risky roles is the most efficient
repair; in a permuted language a partial repair can leave the error silent, and the registered test
has yet to be run as designed."

---

## 11. The interaction (H2), and why it is not testable

The refined hypothesis of the literature review is an **interaction**: the habit should do most
damage where a **strong prior** meets **local syntax that cues it**, more than the two effects
added together:

$$
\Delta = (\bar Z_{\text{strong,high}} - \bar Z_{\text{strong,low}})
       - (\bar Z_{\text{neutral,high}} - \bar Z_{\text{neutral,low}}).
$$

Testing it needs two factors calibrated **independently** of the outcome: prior strength (from a
neutral prompt) and local-context activation (from matched prefixes). Neither exists in these
materials. Deriving them from the same margins the test would explain is circular: the interaction
would appear because it was built in. H2 is therefore **NOT TESTABLE**, which is a result, not a
failure; the machinery to test it on three scales is implemented and waits for calibrated
materials.

**Say it aloud:** "An interaction needs both factors measured apart from the outcome; ours are not,
so H2 is reported as not testable rather than tested circularly."

---

## 12. Scale (deviations D10 and D11)

The preregistration stopped at 3B. Deviation D10 (2026-10-07, before the freeze) raised the ceiling to
72B, adding Qwen2.5-Coder 7B, 14B and 32B (a six-size ladder with one tokenizer and training
recipe), DeepSeek-Coder-33B and Qwen2.5-72B. D11 then specified the analysis before any held-out
outcome was seen: the OLS slope of each outcome on $\log_{10}$(parameters) within the Qwen2.5-Coder
ladder, per family, with a template bootstrap and Holm over six slopes.

Sizes were not randomized; different sizes differ in more than size. A slope is an association
within one family of checkpoints, not an effect of size.

**Say it aloud:** "Within the Qwen2.5-Coder ladder from 0.5B to 32B, no reversion slope survives the
correction for multiple tests; that is an association on one route, not a law."

---

## 13. Making a result confirmatory

### 13.1 Exploratory and confirmatory

An **exploratory** result can suggest; it is measured while the analysis is still being chosen. A
**confirmatory** result tests a choice committed in advance, on observations reserved for that test.
The difference is not in the data but in the order of decisions.

### 13.2 The registered split (Phase 3.3)

| class | cells | use |
|---|---|---|
| DEVELOPMENT | `dom` × {`d25s1`, `d25s2`, `d50s1`, `d50s2`} × Qwen2.5-Coder 0.5B and 1.5B, base and instruct | design, debug, calibrate |
| HELDOUT (mapping) | the development models on the five held-out lexicons, `dom` | confirmatory |
| HELDOUT (model) | the other models, held-out lexicons, `dom` | confirmatory |
| HELDOUT-WEAKENED | Qwen2.5-Coder-3B (observed under an old protocol, D2) | confirmatory, labelled |
| HELDOUT-WEAK-FAMILY | `blk` on held-out lexicons (D1) | a weaker test |
| EXPLORATORY-CONTAMINATED | `blk` on development lexicons | refused unless allowed, then labelled |
| FORBIDDEN | anything unregistered, or above the size ceiling | refused |

The split is **enforced in code**, before any site is enumerated or any model loaded: a development
command that so much as listed a held-out site would already have looked at held-out material.

### 13.3 Preregistration, freeze and unlock

1. **Preregistration** (2026-10-02): hypotheses, splits, numeric success criteria, analysis,
   exclusions and stopping rules, written before the confirmatory run. Its text is frozen; changes
   are appended as dated deviations.
2. **Development run** `dev-20261006a`: 4 models, `dom` × 4 development lexicons, 852 sites.
3. **Freeze** (2026-10-07, 23:04 MST): `DEV_FREEZE.json` records the risk formula, the calibration
   and thresholds, the hashes of every prompt, the exclusion rules, the analysis settings and seeds,
   the hashes of the source code and materials, and the model pins. It is written once and made
   read-only.
4. **Unlock** (44 seconds later): only by typing the exact phrase *"I have finished the development
   analysis and will not change it"*, and only if the freeze, the source, the materials and every
   model pin still match.
5. **Held-out run** `heldout-20261007a`: every access re-checks the same things.

### 13.4 The deviations, in one table

| | date | what | consequence |
|---|---|---|---|
| D1 | 10-05 | `blk` was scored before the freeze | C3 not testable; `blk` is a weak family |
| D2 | 10-05 | 3B was observed before the freeze | 3B labelled weakened |
| D3 | 10-05 | `k*` definition fixed; leaky examples | pre-freeze `k*` (≈ 5–7 shots) withdrawn |
| D4 | 10-05 | bootstrap collapsed duplicate draws | pre-freeze rule-effect intervals withdrawn |
| D5 | 10-05 | de-duplication within (family, lexicon) | eligible-site counts changed |
| D6 | 10-05 | identity baseline constant on eligible sites | C1 ≡ AUROC ≥ 0.60, stated |
| D7 | 10-05 | fp32 output head; length-matched control | methods change before any confirmatory run |
| D8 | 10-05 | development includes the instruct twins | needed for H4 |
| D9 | 10-07 | tie handling in AP and precision@k; power report | baseline AP values change; no criterion |
| D10 | 10-07 | size ceiling 3B → 72B; ten held-out checkpoints | scale analysis added |
| D11 | 10-08 | the scale analysis specified before outcomes | slopes, bootstrap, Holm |
| D12 | 10-09 | three gaps found after the results: calibration in sample for 8 pairs; the H5 test not implemented; the D10 analysis not in the frozen code (handled by D11) | disclosed; no verdict changed |
| D13 | 10-21 | the gaps corrected post hoc in Phase 4 | H5 not supported by its registered test; Arm B extraction fixed |

### 13.5 What counts as confirmatory

H4's C1 and C2, the `k*` endpoint, and the direction of H5. Everything else, including the stratum
and density cuts, the per-role analyses and everything in Phase 4, is exploratory and labelled so.

**Say it aloud:** "Every analysis choice was fixed on development data and frozen, the held-out cells
were unlocked only after that, and the code checked on every access that nothing had changed."

---

## 14. Threats to validity, and how each is handled

| threat | the risk | how it is handled |
|---|---|---|
| leakage in examples | the ladder measures copying | leak-free, nested demonstrations; a leak raises an error |
| length of the rule prompt | a length effect read as rule-following | the length-matched control |
| tokenization | a tokenizer that merges `('` with `#` scores both candidates over zero tokens | first-divergent-token scoring; refusals instead of zeros (P32-001, P33-001) |
| precision | bf16 rounding decides near-zero signs | fp32 output head; ties recorded |
| one wording | a result about one prompt | three paraphrases |
| clustering | sibling sites counted as independent | template-cluster bootstrap |
| multiplicity | one of many tests passes by luck | Holm within the declared families |
| opportunity | low reach read as low reversion | Arm B's hurdle |
| circularity | an interaction built from its outcome | H2 not testable |
| contamination | a "held-out" grammar that was seen | D1; C3 not testable |
| calibration in sample | ECE fitted on its own data | D12, D13 |
| H5's metric | repaired and control sites mixed | D13 split them |
| **H5's targeted arm** (2026-10-28) | another model's repair scored | found; not yet corrected |
| **Kaplan–Meier rounding** (2026-10-23) | a median moved to the next switch | found; not yet corrected |
| served models (Phase 4) | rounded scores, batching noise, quantized weights | ties counted; a re-scored sample; precision stated per model |

---

## 15. What was found

Held-out, 21 models, 3,030 sites, every experiment complete:

- **H4 is supported** in all 20 tests (10 base/instruct pairs × 2 families): AUROC **0.76–0.96**;
  C1 differences +0.26 to +0.46, C2 +0.14 to +0.49, every interval above zero, Holm p ≤ 0.001. The
  within-lexicon AUROC is as high as the overall one: the score separates *sites*, not just
  lexicons. It also beats the role-level baseline in 20 of 20 point estimates.
- **Reversion**: with the table, **40–56%** of sites revert for every model; without it, 46–66%.
- **The rule effect** is positive for every model and grammar: averaged over the five lexicons,
  +0.16 to +0.60 nats against `norule` and +0.18 to +0.62 against the length-matched control. Of
  the 420 intervals (21 models × 2 grammars × 5 lexicons × 2 controls), 263 lie above zero and none
  below. The length-matched control gives the same picture, so it is the information, not the
  length.
- **Adaptation**: the Kaplan–Meier median of `k*` is **1.4–4.6** examples in `dom` and **3.3–11.6** in
  `blk`, as exported (in exact arithmetic 1.4–4.5 and 3.2–11.6: see
  [`experiment_math.md` §10.10](experiment_math.md#1010-a-floating-point-trap-in-the-median));
  6–29% of initially wrong sites never switch within 32. A model first prefers the new spelling
  after about 2 examples, but needs about 8 before the preference stays.
- **Scale** (Qwen2.5-Coder 0.5B–32B): no reversion slope survives Holm's correction (the largest,
  `blk` base models, +3.3 points per tenfold increase, Holm p = 0.07). H4's AUROC declines in `dom`
  (−0.081 per tenfold increase) but stays at 0.76 or above.
- **Arm B**: reach **13.5%**; reversion given reach **19.8%**; task accuracy 9.6% (9.9% after the
  extraction fix). Verbs revert most when reached (29% in `dom`, 43% in `blk`), sigils least.
- **H5**: reported as not supported; not tested as designed (Section 10.4).
- **Exploratory**: verbs adapt slowest (KM median 6.6 examples in `dom`, a third never switch);
  the lexicon changed by 25% is harder to adopt than those changed by 50% or 75% (one lexicon each
  at 25% and 50%, so density and lexicon cannot be told apart).

---

## 16. Phase 4: newer and larger models served by an API

Phase 4 scored nine models served by ASU Research Computing's LLM API (OLMo 3 7B and 32B Instruct,
OLMo 3 32B Think, Qwen3-Coder 30B-A3B, Gemma 4 31B, DeepSeek-V4.1-Flash at about 550B, Qwen3.5 27B,
122B and 397B) on exactly the 3,030 held-out sites (run `dev-20261023a`, exploratory: Phase 4's
preregistration is still a draft).

**What changes when a model is served:**

- the model is a **deployment**, pinned by name and server fingerprint, not downloadable weights;
- a margin comes from **two requests**, each a log-probability computed by the server, mostly in bf16:
  778 of 81,810 margins were exact ties (0.95%);
- the same request can return a slightly different log-probability under load (**batching noise**):
  of 2,700 re-scored margins, 39 changed sign;
- many models run **quantized** (fp8, mxfp4);
- some models answer the raw-text prompt with their **end-of-turn token** and write nothing.

**What holds:** with the table, the served models revert at **40.4–51.2%** of sites, inside Phase
3.3's range. The table helps a little more (+0.34 to +0.86 nats). Size, up to about 550B, does not
cure the habit. The Kaplan–Meier medians run from 1.7 to 15.3 examples. In free generation, Gemma 4
reaches about half the sites, more than any other model, and writes the familiar spelling at only
4% of those. Details:
[`phase4/api_models_results_explained/`](../phase4/api_models_results_explained/00_complete_results.md).

---

## 17. Where this sits in the literature

Prior work already establishes the broad phenomenon:

- **PLSemanticsBench** (ICML 2026): models lean on familiar operator meanings over supplied formal
  semantics, tested with familiar operators reassigned and with novel symbols, when executing code
  rather than writing it;
- **identifier swaps in Python** (Findings of ACL 2023): models prefer the conventional meaning of
  swapped built-ins, sometimes more so when larger;
- **Persistent Priors** (2026): prompt definitions do not erase familiar word associations, and the
  ordinary prior predicts the interference;
- **counterfactual tasks** (NAACL 2024) and **inverse scaling** (TMLR 2023): default assumptions and
  memorized continuations beat in-context instructions across many tasks.

What this research adds is the conjunction: **production** of a prompt-defined DSL, at **exact
grammar sites** where both spellings are valid and the canonical IR differs, across **counterbalanced
mappings and two grammar families**, with **held-out site prediction from a base checkpoint** (H4),
leak-free adaptation curves with censoring, and a meaning-preserving **repair** test (H5). The
literature review and its baseline section are in
[`../background/litreture_reveiw_1.md`](../background/litreture_reveiw_1.md#baselines-for-this-paper).

---

## 18. Practice, glossary, and the whole research said aloud

### 18.1 Check your understanding

**Question 1.** Under `d50s3`, why is the chain-operator site of `t011` LEXICAL in `dom`, and why
does it not exist in `blk`?

**Answer:** The familiar `.` is now the id sigil, an inner-selector symbol; in the outer stream
`.metalness(0.8)` does not lex. `blk` has no chain operator.

**Question 2.** Why does the study keep only SEMANTIC sites?

**Answer:** Only there are both spellings grammar-valid with different canonical IRs, so a
reversion is a silent wrong program: the case the question is about.

**Question 3.** The table moves a site's margin from −5.1 to −4.5. Did the table work?

**Answer:** It helped (+0.6 nats), but the familiar spelling still wins: a positive rule effect is not
a flipped decision.

**Question 4.** Why is H4's label taken from the instruct model and its risk from the base model?

**Answer:** One model for both would build the prediction into the definitions; the claim is that
the base model's habit predicts its tuned twin's failures.

**Question 5.** Why is criterion C1 effectively "AUROC ≥ 0.60"?

**Answer:** Every eligible site is remapped, so the identity baseline is constant and its AUROC is 0.5.

**Question 6.** A model reaches 3% of sites in Arm B and reverts at none of them. Is it a good
model?

**Answer:** Not necessarily: low reach hides behaviour. Report reach and reversion given reach
separately.

**Question 7.** Why can a partial repair leave a reversion silent?

**Answer:** In a permuted lexicon the familiar spelling of the repaired role still means another
role, so the familiar program still parses to a different IR.

**Question 8.** Why is `blk` not a held-out grammar?

**Answer:** It was scored and reported before the freeze (D1).

**Question 9.** What would make H2 testable?

**Answer:** Prior strength and local context calibrated independently of the outcome, for example
from neutral prompts and matched prefixes on a separate checkpoint.

**Question 10.** What has to happen before H5 can be answered?

**Answer:** The targeted arms must be scored with each model's own targeted repair (Section 10.4),
then the registered test applied.

### 18.2 Compact glossary

| term | meaning here |
|---|---|
| 3DOM | the 3D-scene editing language: CSS-like selectors, jQuery-like operation chains |
| terminal | a token class of the grammar; 29 of 43 can be respelled |
| lexicon, φ-map | a validated assignment of spellings to the substitutable terminals |
| identity | 3DOM's own lexicon |
| grammar family | a concrete syntax: `dom` or `blk` |
| canonical IR | the language-neutral meaning of a program; its hash identifies the meaning |
| template | one abstract program (IR), rendered in every family and lexicon |
| decision site | one occurrence of a substitutable terminal in a rendered program |
| correct / familiar | φ(terminal) / the 3DOM spelling of the same role |
| collision class | NONE, LEXICAL, BENIGN or SEMANTIC, by substitution and re-parse |
| stratum | sigil, keyword or verb |
| margin $M$ | log P(correct) − log P(familiar) at the site |
| reversion | $M < 0$ (Arm A) or writing the familiar spelling (Arm B) |
| rule effect | $M$ with the table minus $M$ with a control |
| ladder, `k*` | worked examples 0–32; the first count with $M \ge 0$ |
| censored | no crossing observed by 32 |
| reach | Arm B output reproduces the target up to the site |
| risk, label | H4's $-M^{\text{base}}$ and $\mathbf 1[M^{\text{instruct}} < 0]$ |
| repair | respelling roles with `beta` spellings, proven meaning-preserving |
| development / held-out | cells for designing / cells reserved for the confirmatory test |
| freeze, unlock | the record of every analysis choice / the gated access to held-out cells |
| deviation | a dated, appended change to the registered design |

### 18.3 The whole research, said aloud

> We built a small language for editing 3D scenes and respelled it so that familiar CSS and jQuery
> spellings mean other things, then measured at every exact place where a respelled symbol must be
> written whether code models follow the prompt's token table or fall back to the familiar spelling.
> With the table in front of them, 21 models from 0.5B to 72B still fell back at 40–56% of sites, and
> nine newer served models up to about 550B at 40–51%. Worked examples help, after about two in the
> familiar grammar and more in an unfamiliar one, but rarely smoothly. Most importantly, a base
> model's own preference at a site predicts where its instruction-tuned twin will fail, on mappings it
> never saw during design, in all twenty preregistered tests. Repairing only the risky spellings has
> not yet been tested as designed.

### 18.4 The shortest mental model

> **The habit is a door sign everyone remembers. The token table is a card saying the signs were
> swapped. Arm A asks which sign the model trusts at one door; the ladder shows it more and more
> swapped buildings; Arm B lets it walk on its own; H4 predicts which doors it will get wrong from
> its untrained twin; H5 repaints only the dangerous signs.**
