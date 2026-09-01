# ARCHITECTURE_NOTES.md

A map of this repo: a fork of the **three.js editor** with an added **AI layer** that
turns natural-language prompts into Three.js scene code, executed in-browser by a
small local model (WebLLM / Qwen) — with an optional cloud "teacher" path
(Anthropic / OpenAI / Ollama) proxied through `server.js`.

All paths below are relative to the repo root. Line numbers are from the state of
the tree when these notes were written; treat them as "look near here," not exact
forever.

---

## 1. High-level repo structure

```
.
├── server.js                  # Node static server + /api proxy to cloud LLMs (Claude/OpenAI/Ollama)
├── docs/                      # the actual web app (served statically)
│   ├── index.html             # app entry — importmap + boots Editor/Sidebar/Viewport/...
│   ├── build/                 # bundled three.js
│   ├── examples/              # three.js addons (jsm)
│   └── editor/
│       ├── css/  images/  manifest.json  sw.js
│       └── js/
│           ├── Editor.js          # ← core state object (scene, signals, history, selection)
│           ├── Command.js         # base Command class
│           ├── History.js         # undo/redo stack; editor.execute() lands here
│           ├── commands/          # all Set*/Add*/Remove* commands (undoable mutations)
│           ├── Viewport*.js Sidebar*.js Menubar*.js Toolbar.js  # the UI panels
│           ├── Selector.js Loader.js Config.js Storage.js Strings.js
│           │
│           ├── ── AI LAYER (the fork's additions) ──
│           ├── Shell.js           # ★ AI + JS REPL hub. Input capture, scope, eval, agentic dispatch
│           ├── AIEngine.js        # WebLLM wrapper + external-API adapter
│           ├── AIPrompt.js        # SYSTEM_PROMPT, model registry, Q&A prompt
│           ├── AIUtils.js         # code extractor, message builder, token budgeting
│           ├── ai/
│           │   ├── agentLoop.js   # ★ bounded generate→validate→execute→observe→fix loop
│           │   ├── apiIndex.js    # local RAG index over the REAL exposed API
│           │   ├── validate.js    # static lint of generated code vs the API index
│           │   ├── eval.js        # standing eval harness (evalAI())
│           │   ├── editEval.js    # edit-specific eval scoring
│           │   └── threejsApi.js  # large hand-curated three.js signature corpus (RAG source)
│           ├── intelligence/      # NL → scene-object resolution (sceneIndex, observe, gpuPick, ...)
│           ├── scene/             # codegen.js, summarize.js, sceneEqual.js (scene ↔ JS, diffing)
│           ├── mesh/              # EditMode + modeling ops (boolean/extrude/bevel/...)
│           └── import/            # asset import pipeline (normalize/diagnose/label)
└── *.md                       # design docs (DEV_MODE_API, MESH_EDITING_*, IMPLEMENTATION_STATUS)
```

**Boot order** (`docs/index.html:82+`): `new Editor()` → `new Sidebar(editor)` →
the rest of the panels. The Shell (and therefore the whole AI layer) is created
inside the Sidebar: [Sidebar.js:69](docs/editor/js/Sidebar.js#L69) `const shell = new Shell( editor )`,
registered as the "Shell" tab at [Sidebar.js:90](docs/editor/js/Sidebar.js#L90).

---

## 2. How the underlying three.js editor works

### 2.1 The Editor state object — [Editor.js](docs/editor/js/Editor.js)

`Editor()` ([Editor.js:15](docs/editor/js/Editor.js#L15)) is a plain constructor
function (prototype-style, not a class) that **owns all application state**:

- `this.scene` (`THREE.Scene`), `this.sceneHelpers`, `this.camera`, `this.viewportCamera`
- registries: `this.geometries`, `this.materials`, `this.textures`, `this.scripts`,
  `this.cameras`, `this.helpers`, plus `materialsRefCounter` (a `Map`)
- selection: `this.selected`, `this.selectionMultiple`
- subsystems: `this.config`, `this.history`, `this.selector`, `this.storage`,
  `this.strings`, `this.loader`
- `this.signals` — the pub/sub bus (see 2.3)

Key mutators (these are what Commands call):
- `addObject(object, parent, index)` [Editor.js:188](docs/editor/js/Editor.js#L188) —
  traverses the object, registers geometries/materials/cameras/helpers, adds it to
  the scene, then **dispatches `objectAdded` + `sceneGraphChanged`**.
- `removeObject` [Editor.js:225](docs/editor/js/Editor.js#L225), `addMaterial`,
  `setScene`, `clear`, `fromJSON`/`toJSON` (project serialization).
- `execute(cmd)` [Editor.js:777](docs/editor/js/Editor.js#L777) → delegates to
  `this.history.execute(cmd)`. `undo()`/`redo()` likewise.

The AI layer attaches a few extra things onto the editor instance at runtime
(in Shell.js): `editor.aiEngine`, `editor.editModeController`,
`editor.sceneIntelligence`, `editor.importLog`.

### 2.2 The Command system — [Command.js](docs/editor/js/Command.js), [commands/](docs/editor/js/commands/)

Every undoable mutation is a **Command** object. `Command`
([Command.js:1](docs/editor/js/Command.js#L1)) is the base: it holds `id`, `type`,
`name`, `editor`, and `toJSON`/`fromJSON`. Concrete commands extend it and
implement `execute()` / `undo()`.

Example — [AddObjectCommand.js](docs/editor/js/commands/AddObjectCommand.js):
- `execute()` [:27](docs/editor/js/commands/AddObjectCommand.js#L27) → `editor.addObject(obj)` then `editor.select(obj)`
- `undo()` [:34](docs/editor/js/commands/AddObjectCommand.js#L34) → `editor.removeObject(obj)` then `editor.deselect()`

The full command vocabulary lives in [commands/](docs/editor/js/commands/):
`AddObjectCommand`, `RemoveObjectCommand`, `SetPositionCommand`,
`SetRotationCommand`, `SetScaleCommand`, `SetMaterialColorCommand`,
`SetMaterialCommand`, `SetValueCommand`, `SetGeometryCommand`, … The AI is told
(in the system prompt, rule 4) to **only ever mutate the scene through these
commands via `editor.execute(...)`**, never `scene.add()` directly — so AI edits
remain undoable.

### 2.3 The History stack — [History.js](docs/editor/js/History.js)

`History.execute(cmd)` [History.js:34](docs/editor/js/History.js#L34):
- optional command coalescing (`updatable` commands within 500 ms merge — e.g.
  dragging a slider),
- pushes onto `this.undos`, assigns `cmd.id`,
- calls `cmd.execute()`,
- serializes to JSON if history persistence is enabled,
- clears `this.redos`,
- dispatches `historyChanged`.

`undo()`/`redo()` pop/push between `undos` and `redos` and call `cmd.undo()` /
`cmd.execute()`. The agentic loop uses `editor.history.undos.length` as a
**checkpoint** and `editor.history.undo()` to **roll back** a bad AI attempt (see
section 4 deps `historyLen`/`rollbackTo`).

### 2.4 The signals pub/sub — [signals.min.js](docs/editor/js/libs/signals.min.js)

A tiny global `signals` library (`signals.Signal`). The editor declares ~70
signals in one block at [Editor.js:19-108](docs/editor/js/Editor.js#L19-L108):
`objectAdded`, `objectChanged`, `objectRemoved`, `sceneGraphChanged`,
`selectionChanged`, `materialChanged`, `historyChanged`, plus fork-added ones like
`toggleShell`, `showJSForSelection`, `editModeChanged`, `subObjectSelected`.

Usage pattern: producers call `editor.signals.X.dispatch(payload)`; consumers
(UI panels, Viewport) call `editor.signals.X.add(handler)`. This is how a Command
mutating the scene causes the Viewport to re-render and the Sidebar to refresh —
they're decoupled through the signal bus. A signal can be muted with
`.active = false` (see `setScene` batching, [Editor.js:171](docs/editor/js/Editor.js#L171)).

### 2.5 The scene graph

Standard three.js: `editor.scene` is a `THREE.Scene`; objects are `Object3D`/`Mesh`/
`Group` with `.children`, `.parent`, `.position/.rotation/.scale`, `.geometry`,
`.material`, `.uuid`, `.name`, `.userData`. Helpers (lights, cameras) live in a
parallel `editor.sceneHelpers` scene. Object lookup utilities:
`editor.objectByUuid`, `selectByUuid`, plus the AI-facing `findObject` family
defined in Shell's scope (section 3.4).

---

## 3. The AI subsystem

### 3.1 Where the user's prompt is captured

The Shell tab has **two** input rows ([Shell.js:199-238](docs/editor/js/Shell.js#L199-L238)):
- `aiInput` (`#shell-ai-input`) — natural language ("AI" row)
- `input` (`#shell-input`) — raw JS REPL

The AI text box's `keydown` handler is at
[Shell.js:1563](docs/editor/js/Shell.js#L1563): on **Enter** it reads
`aiInput.value` and calls **`runAI(val)`** ([Shell.js:1123](docs/editor/js/Shell.js#L1123)).
That is the entry point for the whole NL→scene pipeline.

(A `?`-prefixed prompt is routed to **Q&A mode** instead — `buildQAMessages` +
`aiEngine.stream`, answer printed, nothing executed: [Shell.js:1136-1154](docs/editor/js/Shell.js#L1136-L1154).)

### 3.2 Where the model is loaded and called

**The engine wrapper:** [AIEngine.js](docs/editor/js/AIEngine.js).

- Local path (WebLLM): imports `@mlc-ai/web-llm` from a CDN at module load
  ([AIEngine.js:7](docs/editor/js/AIEngine.js#L7)). `getModelList()` reads
  `webllm.prebuiltAppConfig.model_list`. `AIEngine.init(modelId, onProgress)`
  ([AIEngine.js:72](docs/editor/js/AIEngine.js#L72)) calls
  `webllm.CreateMLCEngine(...)` — tries an 8192 context window, falls back to 4096.
  Inference: `stream()` ([:130](docs/editor/js/AIEngine.js#L130)) and `complete()`
  ([:173](docs/editor/js/AIEngine.js#L173)) call
  `this._engine.chat.completions.create(...)`.
- External/cloud path: `setExternalAPI(modelId, streamFn, interruptFn)`
  ([AIEngine.js:202](docs/editor/js/AIEngine.js#L202)) swaps in an override
  `_externalStream`, so `stream()`/`complete()` transparently call the cloud
  instead of WebLLM. `ready` is true when either engine is live.

**Loading is triggered** by the "Load AI" button handler
([Shell.js:1337](docs/editor/js/Shell.js#L1337)). It branches on the selected model id:
- prefix `ollama:` / `gpt-` / `claude-` → **external** ([Shell.js:1342](docs/editor/js/Shell.js#L1342)):
  health-checks `/api/health`, then builds a `streamFn` that POSTs to **`/api/chat`**
  ([Shell.js:1370-1482](docs/editor/js/Shell.js#L1370-L1482)) — supports SSE streaming and
  one-shot JSON, with 429 backoff — and registers it via `aiEngine.setExternalAPI`.
- otherwise → **WebLLM** ([Shell.js:1495](docs/editor/js/Shell.js#L1495)): requires
  `navigator.gpu`, then `aiEngine.init(...)` with a progress bar.

**Model registry:** the dropdown ([Shell.js:71-160](docs/editor/js/Shell.js#L71-L160))
is populated from WebLLM's built-in list (filtered to coder models) **plus** whatever
`/api/models` returns (external). `AIPrompt.js:7` (`AI_MODELS`) also lists three
preferred local Qwen/Llama models.

**The cloud "teacher" / frontier path:** [server.js](server.js). A plain Node
`http` server. Routes: `/api/models` ([server.js:44](server.js#L44)),
`/api/chat` ([server.js:189](server.js#L189)), `/api/health` ([server.js:507](server.js#L507)).
`handleApiChat` dispatches by model-id prefix:
- `ollama:` → `http://127.0.0.1:11434/api/chat`
- `gpt-` → `https://api.openai.com/v1/chat/completions` (needs `OPENAI_API_KEY`)
- `claude-` → `https://api.anthropic.com/v1/messages`
  ([server.js:350-470](server.js#L350-L470), needs `ANTHROPIC_API_KEY`). Note the
  Anthropic adapter pulls the `system` role **out** of the messages array into the
  top-level `system` param ([server.js:363-389](server.js#L363-L389)) and drops
  `temperature` for Opus 4.7/4.8. Both streaming (SSE relay) and one-shot, with 429
  retry/backoff. Model ids are declared in `/api/models`
  ([server.js:75-111](server.js#L75-L111)) and gated by env-var presence.
  Cloud models are intended for `--dev` mode (`DEV` flag, [server.js:7](server.js#L7);
  see `DEV_MODE_API.md`).

### 3.3 Where the system prompt and RAG context are assembled

- **System prompt:** `SYSTEM_PROMPT` in
  [AIPrompt.js:15](docs/editor/js/AIPrompt.js#L15) — a long instruction block: output
  rules (fenced JS, IIFE, run-immediately), world orientation, the **GLOBALS list**
  it's allowed to use, 25 numbered RULES, and many worked EXAMPLES (red box, pong,
  chess board, bounce clip, …). `buildSystemPrompt(opsSchema)`
  ([AIPrompt.js:372](docs/editor/js/AIPrompt.js#L372)) injects the live EditMode op
  registry into it.
- **RAG context (Technique 2, local):** [ai/apiIndex.js](docs/editor/js/ai/apiIndex.js).
  `buildIndex()` is called once on Shell construction
  ([Shell.js:265](docs/editor/js/Shell.js#L265)). It indexes the **real** exposed
  API — command signatures + arities, allowed material keys, geometry params, op
  registry, and the big `threejsApi.js` corpus. Per request,
  `retrieveForPrompt(question)` ([Shell.js:1160](docs/editor/js/Shell.js#L1160))
  returns a compact string of the most relevant real signatures.
- **Scene context:** `buildMessages(systemPrompt, editor, userPrompt, apiHints)`
  ([AIUtils.js:168](docs/editor/js/AIUtils.js#L168)) builds the final
  `[{system}, {user}]` array. The user message = `apiHints` + a JS-comment
  description of the current scene (`sceneContextString`, from
  [scene/summarize.js](docs/editor/js/scene/summarize.js)) + `Request: <prompt>`.
  It falls back to a compact JSON summary if the scene text exceeds the char budget.

So the full message assembly for a code-gen request happens in
[Shell.js:1160-1162](docs/editor/js/Shell.js#L1160-L1162):
```js
const apiHints     = retrieveForPrompt( question );          // RAG
const systemPrompt = buildSystemPrompt( opsSchema() );       // prompt + live ops
const messages     = buildMessages( systemPrompt, editor, question, apiHints );
```

### 3.4 Where the returned code string is executed (the eval site)

**There is exactly one execution surface: `execute(code)` in Shell.js**
([Shell.js:314](docs/editor/js/Shell.js#L314)). Both human REPL keystrokes and AI
output flow through it.

It builds a big **`scope` object** ([Shell.js:330-1068](docs/editor/js/Shell.js#L330-L1068))
exposing `editor`, `THREE`, the command classes, all whitelisted geometry/material/
object globals, and the AI helper functions (`findObject`, `findByDescription`,
`findParts`, `makeTable`, `makeChair`, `lineFromPoints`, `addClip`, `whatsVisible`,
`booleanUnion`, EditMode ops, etc. — this is the live implementation of the GLOBALS
list in the system prompt).

The actual eval is **`new Function` + indirect `eval`** at
[Shell.js:1073-1076](docs/editor/js/Shell.js#L1073-L1076):
```js
const __keys = Object.keys( scope );
const __vals = __keys.map( k => scope[ k ] );
const __fn   = new Function( ...__keys, '__shell_src__', 'return eval(__shell_src__)' );
const result = __fn.call( null, ...__vals, code );
```
Every scope key becomes a named parameter, so the model's `editor.execute(new
AddObjectCommand(...))` resolves those identifiers as locals. `execute` returns
`{ ok: true }` or `{ ok: false, error }`. **This is the single most important file
to understand** — it's both the capability surface and the eval point.

> Note: the JS REPL row's `new Function` is the editor's *AI/console* eval. It is
> distinct from the editor's user-script feature (`Script.js`) and from
> `THREE.ObjectLoader` (de)serialization.

### 3.5 The agentic loop (what wraps the eval) — [ai/agentLoop.js](docs/editor/js/ai/agentLoop.js)

`runAI` doesn't call the model once and run the result. It builds messages, snapshots
the mesh set, and calls **`runAgentic({...})`**
([Shell.js:1167](docs/editor/js/Shell.js#L1167)). `runAgentic`
([agentLoop.js:298](docs/editor/js/ai/agentLoop.js#L298)) is a pure orchestrator —
all side-effects are injected as `deps`. Per attempt (capped at `maxRetries = 3`):

1. **Generate** — `deps.streamCode(convo)` → `streamToOutput` → `aiEngine.stream` →
   `extractCode(...)` ([AIUtils.js:76](docs/editor/js/AIUtils.js#L76), the
   fenced-block / IIFE extractor; prose never runs).
2. **Static validate** — `validateCode(code)`
   ([ai/validate.js:249](docs/editor/js/ai/validate.js#L249)): lints against the API
   index for invented classes, wrong command arity, bad material keys. Failure →
   feed the issue back, retry (before any execution).
3. **Execute + observe** — `snapshotScene` → `deps.execute(code)` (the Shell eval) →
   `snapshotScene` → `sceneDiff` → `confirmChange` (from
   [intelligence/observe.js](docs/editor/js/intelligence/observe.js)).
4. **Fix signals** — retry on "nothing changed" (`diff.total === 0`), color collapse
   (C5), subset-misresolution (C7), or geometric defects (`inspectScene`, Tier-2,
   one corrective pass). Error strings are translated to actionable hints
   (`translateError`, [agentLoop.js:57](docs/editor/js/ai/agentLoop.js#L57)). Bad
   attempts can be rolled back via `rollbackTo` (history undo).

So the real reliability machinery is **generate → validate → execute → observe →
fix**, not just "run whatever came back."

---

## 4. End-to-end trace: typing "make a ball"

Files/functions in order:

1. **`aiInput` keydown (Enter)** — [Shell.js:1563-1580](docs/editor/js/Shell.js#L1563-L1580).
   Reads `"make a ball"`, clears the box, calls `runAI("make a ball")`.
2. **`runAI(userPrompt)`** — [Shell.js:1123](docs/editor/js/Shell.js#L1123). Not a
   `?` query, so code-gen mode. Sets status "thinking…", `aiAborted = false`.
3. **Assemble the request** — [Shell.js:1160-1162](docs/editor/js/Shell.js#L1160):
   - `retrieveForPrompt("make a ball")` → RAG hints (apiIndex.js)
   - `buildSystemPrompt(opsSchema())` → SYSTEM_PROMPT + live ops (AIPrompt.js)
   - `buildMessages(...)` → `[{system}, {user: hints + scene + "Request: make a ball"}]`
     (AIUtils.js:168). Snapshots `beforeMeshes` ([Shell.js:1164](docs/editor/js/Shell.js#L1164)).
4. **`runAgentic({ editor, messages, intent, deps, ... })`** —
   [Shell.js:1167](docs/editor/js/Shell.js#L1167) → [agentLoop.js:298](docs/editor/js/ai/agentLoop.js#L298).
5. **Generate** — `deps.streamCode` = `streamToOutput`
   ([Shell.js:1117](docs/editor/js/Shell.js#L1117)) → `streamRaw` →
   `aiEngine.stream(messages)` ([AIEngine.js:130](docs/editor/js/AIEngine.js#L130),
   WebLLM Qwen or the external streamFn) → tokens render live → `extractCode(...)`
   pulls the fenced JS. The model emits roughly:
   ```js
   (function(){
     const ball = new Mesh(new SphereGeometry(0.5,32,16),
       new MeshStandardMaterial({color:0xff2222,roughness:0.4,metalness:0}));
     ball.name='Ball'; ball.position.y=0.5;
     editor.execute(new AddObjectCommand(editor, ball));
   })();
   ```
6. **Validate** — `validateCode(code)` ([ai/validate.js:249](docs/editor/js/ai/validate.js#L249)).
   `Mesh`, `SphereGeometry`, `AddObjectCommand(editor,ball)` are all in the index → OK.
7. **Execute** — `deps.execute(code)` = Shell's `execute`
   ([Shell.js:314](docs/editor/js/Shell.js#L314)) → builds `scope` → the
   `new Function(...eval...)` site ([Shell.js:1075](docs/editor/js/Shell.js#L1075))
   runs the IIFE.
8. **Command runs** — `editor.execute(cmd)` ([Editor.js:777](docs/editor/js/Editor.js#L777))
   → `history.execute(cmd)` ([History.js:34](docs/editor/js/History.js#L34)) →
   `AddObjectCommand.execute()` ([AddObjectCommand.js:27](docs/editor/js/commands/AddObjectCommand.js#L27))
   → `editor.addObject(ball)` ([Editor.js:188](docs/editor/js/Editor.js#L188)).
9. **Scene updates + render** — `addObject` adds the mesh to `editor.scene`,
   registers its geometry/material, and dispatches `objectAdded` +
   `sceneGraphChanged` ([Editor.js:213-214](docs/editor/js/Editor.js#L213-L214)).
   `AddObjectCommand` also selects it. The Viewport listens on those signals and
   re-renders → **the ball appears.**
10. **Observe** — back in the loop: `sceneDiff` sees one added mesh, `confirmChange`
    passes, `diffSummary` is printed (`✓ …`), `runAgentic` returns `{ ok: true }`.
    `runAI`'s post-check may print the "try Power model" hint if a multi-part object
    came back as a single primitive — not the case here.

---

## 5. The two best hook points for later

### (a) Capture (prompt → generated code) training pairs

**Best spot: inside `runAgentic`, at the success return**
([agentLoop.js:507-508](docs/editor/js/ai/agentLoop.js#L507-L508)), and at each
failure/retry branch. Reasons:
- `intent` (the raw user prompt) and `code` (the exact extracted, *executed* string)
  are both in scope there, plus the full outcome: `attempt` count, `validateCode`
  result, the `sceneDiff`, and `confirmChange`. That gives you **labeled** pairs —
  prompt, code, and whether it actually worked — not just raw generations.
- Because **every** generation (REPL, AI, and `evalAI`) funnels through this one
  function, a single hook captures all of them with consistent metadata.

Concretely: add an injected `deps.record({ intent, code, attempt, validation,
diff, ok, model: editor.aiEngine.modelId })` and call it on the success return and on
each `lastFail` assignment. Wire the dep in from Shell where the other deps are
created ([Shell.js:1174-1186](docs/editor/js/Shell.js#L1174-L1186)). A secondary,
lower-fidelity option is to log at the Shell `execute` boundary
([Shell.js:314](docs/editor/js/Shell.js#L314)), but that loses the prompt/intent
linkage and mixes in human REPL input — prefer the loop.

> If you also want the cloud "teacher" answer as the *target* label for distillation,
> capture it at the `streamFn` boundary in the external path
> ([Shell.js:1370](docs/editor/js/Shell.js#L1370)) or server-side in `handleApiChat`
> ([server.js:189](server.js#L189)), keyed by the same `intent`.

### (b) Add a real result-verification check (not just "did it run")

**Best spot: the observe/verify stage of `runAgentic`**, between execution and the
success return ([agentLoop.js:413-508](docs/editor/js/ai/agentLoop.js#L413-L508)).
The scaffolding for "verify the *result*, not the run" already lives here:
- `snapshotScene` / `sceneDiff` / `confirmChange` — did the scene change as intended?
- `inspectScene` (Tier-2 geometric: below-ground / interpenetration / floating)
  ([agentLoop.js:480](docs/editor/js/ai/agentLoop.js#L480))
- C5 color-collapse and C7 subset-misresolution semantic checks.

Add your verifier as **one more gate before the `return { ok: true }`** at
[agentLoop.js:507](docs/editor/js/ai/agentLoop.js#L507): compute it from `before`/
`after` snapshots (already in scope) and, on failure, set `lastFail = { code, error:
<actionable message> }` and `continue` so the existing retry machinery feeds it back
to the model. The supporting analysis utilities live in
[intelligence/observe.js](docs/editor/js/intelligence/observe.js) (snapshot/diff/
inspect) and [scene/sceneEqual.js](docs/editor/js/scene/sceneEqual.js) /
[scene/summarize.js](docs/editor/js/scene/summarize.js) (geometry measurement); the
eval harness [ai/eval.js](docs/editor/js/ai/eval.js) shows how scoring axes
(structure / spatial / semantic) are computed and is the place to add new
**graded** checks. Keep new gates capped to one corrective pass (mirror
`spatialRepaired` / `subsetRepaired`) to avoid retry storms.

---

## 6. One-paragraph mental model

A prompt typed in the **Shell** AI box → `runAI` assembles **system prompt +
local-RAG API hints + scene summary** → the **bounded agentic loop** asks the model
(local **WebLLM/Qwen** via `AIEngine`, or a cloud model proxied by `server.js`) for
a fenced **IIFE of editor commands** → the loop **validates** it against the real API
index, **executes** it through Shell's single `new Function`/`eval` surface (whose
scope is the live capability list), and **observes** the scene diff, retrying with
actionable feedback on failure. Execution only ever mutates the scene via
**Commands → `editor.execute` → History**, so every AI edit is undoable and every UI
panel updates through the **signals** bus.
