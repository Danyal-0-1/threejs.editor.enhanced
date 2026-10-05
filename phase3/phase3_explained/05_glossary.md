# 05 — Glossary

Each entry: **technical definition** · *simple definition* · project example ·
**common confusion**.

---

## Research design

**Estimand** — The precise numerical quantity an experiment estimates, defined
before data collection. · *The exact number you are trying to measure.* ·
Phase 3's primary estimand is `k*`, the extinction threshold. · **Confusion:**
an estimand is not a hypothesis and not a test statistic. "Models rely on
priors" is not an estimand; "the median `k*` at SEMANTIC sites" is.

**Factorial design** — Crossing two or more factors so every combination
occurs. · *Try every combination.* · `T ∈ {neutral, medium, strong}` ×
`A ∈ {low, medium, high}`. · **Confusion:** a factorial design does not make a
factor *causal*. Phase 3's `T` is **selected** on an observable, not
randomised, so the design is A-randomised and T-stratified.

**Interaction** — The effect of one factor depends on the level of another; a
difference of differences. · *Two things together do more than the sum.* ·
H2. · **Confusion:** an *ordinal* interaction is partly a property of the
measurement scale. Only a **crossover** (sign-reversing) interaction is
transformation-invariant.

**Difference-in-differences (DiD)** — `(A₁−A₂) − (B₁−B₂)`. · *The gap between
two gaps.* · `scoring.interaction_did`. · **Confusion:** a DiD on a
log-probability scale and on a probability scale can disagree and both be
"correct". Hence `sign_agrees`.

**Counterbalancing** — Rotating which spelling carries which meaning so no
token is always correct. · *Don't let the model win by memorising.* ·
**Not implemented in Phase 3.** · **Confusion:** randomising prompts is not
counterbalancing; you must hold out whole mapping rotations.

**Held-out** — Data not used in any way to build or tune the thing being
evaluated. · *Never seen, not even peeked at.* · H4 requires held-out mappings
*and* a held-out grammar family. · **Confusion:** reserving a random subset of
prompts from the *same* mapping is not held-out at the level that matters.

**Mapping vs grammar family** — A *mapping* assigns spellings to roles; a
*grammar family* is a genuinely different concrete syntax. ·
*New words vs new sentence structure.* · `alpha/beta/gamma/delta` are four
**mappings over one grammar**. · **Confusion:** the central one in this
project. Four lexicons look like four languages but invariants I1–I4 freeze
the non-terminals and production shapes, so they are what the review calls
"cosmetic renamings of one grammar."

**Preregistration** — Fixing hypotheses, endpoints, exclusions and analyses
before seeing outcomes. · *Write down what counts as success first.* ·
**Confusion:** it does not forbid exploration; it forbids *relabelling*
exploration as confirmation.

**Falsification criterion** — A prespecified result that would count as
disconfirming. · *What would prove me wrong.* · See `01 §4.18`.

---

## The phenomenon

**Pretrained association / in-weight default** — A model's parameter-encoded
preference between continuations in a neutral context. · *What it expects
before you tell it anything.* · Qwen prefers `.` to `#` after `('`. ·
**Confusion:** this is **not corpus frequency**. We cannot see most
pretraining data. Say "model preference."

**Surface familiarity** — A property of the concrete syntax, holding abstract
syntax and semantics fixed. · *Same program, different-looking characters.* ·
**Confusion:** not the same as *alienness*. `delta` uses entirely familiar
characters and is still a remapping.

**Familiar-token reversion** — Emitting a **predeclared** competitor `q` where
the specification requires `c`. · *Falling back to the old habit.* ·
Emitting `.wheel` under `delta`, where `#wheel` was required. ·
**Confusion:** not every error in an alien language is a reversion. The
competitor must be named in advance — which is why `Site` is frozen.

**Local syntactic activation** — How much the immediately preceding text
raises the competitor's probability *specifically*. · *How much the nearby
code looks like the habit's home.* · **Not implemented.** · **Confusion:**
making the prompt harder raises entropy for every token; that is not
competitor-specific activation.

**Token identity vs tokenization** — Which string, vs how the tokenizer splits
it. · *Same letters, different number of model steps.* · **Confusion:**
equal-length strings are not automatically token-matched.

**Token fertility** — Tokens per character under a given tokenizer. ·
*How finely your language gets chopped.* · Phase 2: alpha 1.068, beta 1.401,
gamma 1.937. · **Confusion:** fertility is a **confound**, not evidence.
Beta had middling fertility and sometimes beat identity. Also: **character
length is not fertility** — `delta`'s measured 1.0078 is a length ratio, and
the tokenizer check has not been run.

---

## Collision taxonomy (Phase 3's core)

**Decision site** — One occurrence of one substitutable terminal in one
program, with its competing spellings. · *One spot where two spellings
compete.* · `delta:t000:T_CLASS_SIGIL:0`. · **Confusion:** a site is not a
token type; it is a specific occurrence at a specific offset in a specific
program.

**NONE** — `c == q`; the role is not remapped here. · *Nothing to compete.*

**LEXICAL collision** — The familiar spelling does not lex or parse. ·
*The habit produces a syntax error.* · `T_CLASS_SIGIL` under **alpha**: `.`
binds to `T_WILDCARD`, which takes no identifier, so `.door` is a parse
error. · **Confusion:** this is a **loud** failure. It is still interesting,
but it is not the review's contrast.

**BENIGN collision** — The variant parses to the **same** IR. · *The habit is
a harmless alias.* · **Confusion:** a model "reverting" here is still correct,
so these cannot measure anything. `delta` has **zero**.

**SEMANTIC collision** — The variant parses **and** yields a **different**
IR. · *The habit silently does the wrong thing.* · `T_CLASS_SIGIL` under
**delta**: `.` binds to `T_ID_SIGIL`, so `.wheel` edits a different object. ·
**Confusion:** this is the **only** usable class, and it is a property of the
φ-map, not of the language's "alienness." beta and gamma have **zero** despite
large NLL distances.

**Shape class** — A set of roles accepting the same syntactic shape. ·
*Slots the same kind of thing fits into.* · `{T_CLASS_SIGIL, T_ID_SIGIL}`
(both `sigil IDENT`); the 15 verbs; the 4 type keywords. · **Confusion:** the
design rule is that **silent collisions require permutation within a shape
class.** alpha permutes across classes, which is why its sites are mostly
LEXICAL.

**Prefix collision** — Two sites with byte-identical prefixes but different
correct spellings. · *The model sees the same context and is expected to do
two different things.* · 3 groups covering 63 of `delta`'s 103 semantic
sites. · **Confusion:** not a bug — a ceiling. No prefix-conditioned predictor
can be right about both, and they are not independent observations.

---

## Grammar and IR

**Terminal** — An atomic grammar symbol with a spelling. · *A literal piece of
text the grammar knows.* · `T_CLASS_SIGIL` spelled `.` in 3DOM. ·
**Confusion:** terminal **id** (`T_CLASS_SIGIL`, stable) vs **spelling** (`.`,
varies by φ). The whole project depends on keying by id.

**φ-map (phi-map)** — A validated bijection from terminal ids to spellings. ·
*The dictionary that renames the language.* · `phi_delta.json`. ·
**Confusion:** φ renames **roles**, not characters. Keying on the character
`.` would break whichever of the two `.`-roles you did not target.

**Overload group (I7)** — Terminals sharing one spelling in 3DOM must share
one in any φ. · *Roles that look alike must stay alike.* ·
`{T_CHAIN_OP, T_CLASS_SIGIL}`. · **Confusion:** de-overloading would make the
alien language *easier* to lex than 3DOM — an unmatched complexity change.
`phi.py` allows it via `overload_groups: []`, as a declared deviation.

**AST vs scene graph** — The AST is built by the parser from *text*; the scene
graph is the 3D engine's spatial tree. · *Syntax tree vs the actual objects.* ·
`>` is an AST **leaf** with zero children, whose *meaning* is a scene-graph
edge walk. · **Confusion:** `TERMINOLOGY.md` exists because this one sinks
papers. "`>` selects the AST node's children" is wrong.

**Canonical IR** — A normal form where equal meaning ⇒ equal representation. ·
*A fingerprint of meaning.* · `canonicalize.content_hash`. ·
**Confusion:** the hash **excludes `source`** (rule C7) — that is what lets
identity and delta renderings of one program hash equally.

**Valid-but-vacuous (D5)** — A program that parses with zero operations. ·
*Grammatically fine, does nothing.* · `(function(){ $S('.wheel'); })();` ·
**Confusion:** it is a **parse success** and a **task failure**. It is also
the most plausible null output a small model emits, so folding it either way
lets a condition look better by emitting more empty queries.

---

## Measurement

**Teacher forcing** — Supplying the exact prefix and reading off candidate
probabilities. · *"Which would you prefer?" rather than "what did you write?"* ·
Arm A. · **Confusion:** teacher-forced preference is not generation behaviour;
a model can prefer `c` and still never reach the site.

**`M_seq`** — `log P(c) − log P(q)`, summed over **all** tokens. ·
*How much more likely the right spelling is.* · **>0 good, <0 reversion.** ·
**Confusion:** not `G_tok`, the single-token **logit** margin, which also uses
the **opposite** sign. They coincide only for single-token candidates.

**`S_seq`** — `log P_base(q) − log P_base(c)`. **>0 means danger.** ·
*How risky this site is.* · `s_seq == −m_seq`. · **Confusion:** the sign flip
between `scoring` and `linter` is deliberate and is the easiest bug in the
project.

**`S_local` / `S_shift`** — Risk with no rule / how far the rule moved it. ·
*Habit strength vs rule effect.* · `S_local + S_shift == S_seq`. ·
**Confusion:** without the split you cannot tell "this spelling is doomed"
from "this rule was ignored."

**Extinction threshold `k*`** — Shots at which `M_seq` first crosses zero,
interpolated. · *How many examples to break the habit.* · 5.6 in the worked
example. · **Confusion:** `k* = None` means **censored**, not zero. Dropping
censored curves biases `k*` downward exactly where priors are strongest.

**Censoring** — The event did not occur within the observation window. ·
*Still hadn't happened when we stopped looking.* · **Confusion:** censored ≠
missing. Discarding censored observations is a classic, severe bias.

**Hurdle model** — `P(observed) = P(O) · P(Y|O)`. · *First get there, then
choose.* · **Confusion:** collapsing them reproduces the Experiment 02 error
exactly: `3/3` vs `15/20` looked like more reversion, but conditional
reversion *fell* from 1.00 to 0.75.

**Opportunity bias** — Comparing raw error counts across conditions with
different reach rates. · *You can't err where you never arrived.*

**AUROC** — P(random positive outranks random negative), ties ½. ·
*How well the ranking separates.* · 0.5 = chance. · **Confusion:** undefined
when one class is absent — `linter.auroc` returns `None`, deliberately, rather
than a misleading 0.5.

**AUPRC** — Average precision; baseline is **prevalence**. ·
*Precision across all thresholds.* · **Confusion:** meaningless unless you
state prevalence. For rare reversion AUPRC 0.3 can be excellent.

**Calibration** — Whether predicted probabilities match observed frequencies. ·
*When you say 70%, is it right 70% of the time?* · **Confusion:** calibration
and discrimination are independent. **Not implemented.**

**Brier score** — Mean squared error of probabilistic predictions. ·
*Average squared miss.* · **Confusion:** a proper scoring rule, not an
accuracy; lower is better and it mixes calibration with discrimination.

---

## Code

**Protocol (structural typing)** — An interface satisfied by shape, not
inheritance. · *If it has the methods, it fits.* · `models.LM`; `FakeLM`
inherits nothing. · **Confusion:** `@runtime_checkable` checks method
*presence*, not signatures.

**Frozen dataclass** — Immutable after construction. · *Can't be changed.* ·
`Site`. · **Confusion:** frozen is shallow — a mutable field's *contents* can
still change.

**Vendoring** — Copying a dependency into your tree instead of importing it. ·
*Keeping your own copy.* · `phase3/vendor/`. · **Confusion:** copies do not
receive upstream fixes. Hence `vendor_sync.py --check` and the test that fails
if the P3-001 patch goes missing.

**Fixture** — Fixed test data or a stand-in component. · *Fake input with a
known answer.* · `FakeLM`. · **Confusion:** a fixture that returns noise only
proves the code does not crash. `FakeLM` plants a **known** bias so the test
can assert recovery.

**Two-level lexer** — Separate token streams for the outer program and the
inner quoted selector. · *A little language inside the big one.* ·
`T_CHAIN_OP` lives outside, `T_CLASS_SIGIL` only inside quotes. ·
**Confusion:** the same character means different things at the two levels —
which is exactly why `sites.py` keys on `(token_type, value, offset)` from the
lexer and never on a string search.
