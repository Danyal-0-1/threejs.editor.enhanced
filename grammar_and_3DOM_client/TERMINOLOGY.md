# TERMINOLOGY.md — AST (syntax) vs Scene Graph (semantics)

**grammar version:** `3dom-grammar/1.1.0`

This document fixes the vocabulary the paper uses for two trees that are
constantly, fatally, confused: the **Abstract Syntax Tree** (what the grammar
builds from *text*) and the **Scene Graph** (what the 3D engine walks in *space*).
It is written to be lifted directly into the paper's terminology section, and it
ends with a banned-phrase list for our own drafts.

---

## The fatal trap: the child combinator `>`

Consider the command `$S('.car > .wheel')`.

If the paper says *"the `>` symbol selects the AST node's children,"* Reviewer 2
rejects the paper. Here is why, stated precisely:

- **In the AST (SYNTAX):** `>` is a **terminal** — a literal character. It is a
  **leaf** of the grammar/derivation tree. It has **zero children**. It is a piece
  of text sitting in memory. In `3dom_grammar.iso.ebnf` it is defined by
  `child_combinator = [ whitespace ] , ">" , [ whitespace ]` and annotated in
  place with exactly this warning.

- **In the Scene Graph (SEMANTICS):** the `>` terminal is *translated by the IR
  builder* into an instruction to the 3D engine: *"start at the `Car` scene node
  and walk exactly one level down its physical spatial tree to find the `Wheel`
  scene node."*

**The note-taker's rule:** EBNF and ASTs deal strictly with **syntax** (text
structure). Scene graphs deal strictly with **semantics** (physical meaning). The
`>` does not "have children" in the AST and does not "exist" in the scene graph; it
is a syntactic leaf whose *meaning* is a scene-graph traversal.

---

## 1. Side-by-side: AST node vs Scene node

| Property | **AST node** (syntax) | **Scene node** (semantics) |
|---|---|---|
| What produces it | the **parser**, from source text | the 3D engine / asset import, from geometry |
| What it is typed by | a grammar **production** (`class_selector`, `child_combinator`, …) | a three.js **class** (`Mesh`, `Group`, `Light`, …) |
| What "**parent**" means | the enclosing grammar rule (e.g. `simple_matcher` is the parent of `class_selector`) | the enclosing **spatial** container (`Group` is the parent of its child `Mesh`) |
| What determines its **count** | the **length of the string** (more tokens → more nodes) | the **contents of the scene** (more objects → more nodes) |
| Exists when the scene is **empty**? | **yes** — parsing `$S('.wheel')` builds AST nodes regardless of any scene | **no** — with an empty scene there are zero scene nodes to resolve against |
| Lifetime | transient: exists during parse/compile | persistent: exists as long as the object is in the scene |
| `>` specifically | a leaf terminal, 0 children | not a node at all — an *edge-walk instruction* between two scene nodes |

The columns never touch. A `class_selector` **AST** node and the **scene** nodes it
eventually matches are related only by the IR builder's *resolution* step, which
runs against a scene the grammar never sees.

---

## 2. The 1:N cardinality point (why the DSL is expressive at small model sizes)

One **`selector_call` AST node** resolves to **N scene nodes**:

```
$S('.wheel')          — 1 AST node (one selector_call)
   │  resolution (IR builder + fixture scene)
   ▼
[wheel_fl, wheel_fr, wheel_rl, wheel_rr]   — N = 4 scene nodes
```

That fan-out **is** the jQuery idiom, and it is precisely why 3DOM is expressive
for small models: the model writes **one short chain**, and the **engine iterates**
over the resolved set. The model does not enumerate the four wheels, write a loop,
or track indices — it emits `$S('.wheel').recolor('#111')` and the 1:N resolution
does the rest. A capability claim about "generating 3D edits" must not confuse the
model's job (produce one AST) with the engine's job (apply it to N scene nodes).

Paper-ready sentence: *Because a single selector AST node resolves to an
arbitrary-sized set of scene nodes, output length is decoupled from edit
magnitude; this 1:N fan-out is what lets a 0.5B model express a four-wheel recolour
in one nine-token chain.*

---

## 3. Banned phrases (for our own drafts) → correct replacement

| ❌ Banned phrase | Why it is wrong | ✅ Correct replacement |
|---|---|---|
| "the AST node's children" (when scene traversal is meant) | conflates a syntactic leaf with a spatial subtree | "the child **scene nodes** of the matched object" |
| "the parser selects the mesh" | the parser builds an AST; it never touches the scene | "the parser builds a selector AST; the **IR builder resolves** it to meshes" |
| "the grammar validates the scene" | the grammar validates **strings**, not scenes | "the grammar validates the **command string**; the **resolver** checks it against the scene" |
| "the `>` operator traverses the AST" | `>` is an AST **leaf**; it is not a traversal, and any traversal is of the **scene** | "the `>` terminal **compiles to** a one-level **scene-graph** traversal" |
| "the selector node has 4 children" | an AST `selector_call` has grammar children, not the 4 matched objects | "the selector **resolves to** 4 scene nodes" |
| "parse the scene graph" | scene graphs are not parsed; strings are | "**traverse** the scene graph" / "**parse** the command" |

---

## 4. Why this is not pedantry — it is the task taxonomy

This distinction is load-bearing for the study design, not stylistic. Of our five
task families, **selector-resolution is the only one whose ground truth depends on
data outside the string** — namely the scene. `op-type`, `arg-extract`, `labeling`,
and `multi-op` can be graded from the emitted IR alone; **selector-resolution
cannot**, because `$S('.wheel')` is correct or incorrect only *relative to a
particular scene's node set*.

Consequences we commit to:

- Selector-resolution tasks ship with a **fixture scene**; the other four do not
  need one.
- The syntax/semantics split is exactly the parse-validity vs task-accuracy split
  in `SCORING_POLICY.md`: parse validity is an AST-only judgement; task accuracy for
  selector-resolution is a scene-dependent judgement.
- Therefore any sentence that lets the grammar/AST "reach into" the scene (or the
  scene "validate" a string) is not just imprecise — it misdescribes which tasks
  need a fixture and why, which is a methods error a careful reviewer will catch.
