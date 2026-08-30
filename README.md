# Strata: A CSS-like language for 3D scenes

<img width="100%" src='docs/demo.gif'/>

**A deterministic, human-readable selector language for editing and versioning 3D scenes. Sovereign, browser-native, no build. Optional AI that stays within bounds.**

**The language is the workhorse.** Strata puts a small, familiar interface over a 3D scene: address parts with CSS-like selectors, change them with a closed set of command-backed ops, and version the result with git. The interface is deterministic and works entirely **by hand, without any AI**. It is the primary product. Every mutation is undoable, git-tracked, and human-readable.

**AI is a slim optional front door.** Because the language is small and explicit, a stock on-device model can map natural language onto it. No task-specific training is needed. The layer is **model-agnostic: bring your own AI**. Run a stock model on-device (WebGPU / WebLLM), or connect any external API (Ollama, OpenAI, Claude) through `fetchAPI`. The same scaffolding, harness, and constrained decoding wrap every model, so they lift both local small models and frontier APIs onto the language. It is the natural-language layer *over* the deterministic interface, not the foundation. It debuts most vividly at **animation**: "make it bounce" becomes a real keyframe clip. Generation (blocking out a scene from a prompt) is kept as **scaffolding**, not the headline.

**Production ships validated AI only.** Development mode (`DEV=1`) exposes all models for research. Production mode (default) shows only models that have passed the edit eval matrix. This confirms the zero-training claim.

> **The thesis.** 3D editing = deterministic shell (selector language + ops) + optional model for **4 fuzzy tasks**: op-selection, argument-extraction, labeling, multi-op decomposition. The 5th task (selector-resolution) is capability-bound and runs host-side. The shell is the standalone [3DOM library](https://github.com/tejaswigowda/3dom) ("jQuery for 3D"); Strata consumes it via host adapter. **Separation:** 3DOM = durable library; Strata = one consumer. On-device model suffices, zero training.

**Sovereign by default.** Nothing leaves the device except by your explicit action (git sync, `fetchAPI`). Inference is local. Scene state stays on-device.

---

## Quick start

```bash
npx serve docs       # local dev. Or go to: https://tejaswigowda.com/strata-editor/
```

or

```bash
node server.js
```

Requires **Chrome 113+** (WebGPU). Verify at [webgpureport.org](https://webgpureport.org).

**With external AI models (Ollama, OpenAI, Claude):**

```bash
# Terminal 1: start the server with dev mode enabled
export ANTHROPIC_API_KEY="sk-ant-..."  # or OPENAI_API_KEY
DEV=1 node server.js

# Terminal 2: open http://127.0.0.1:5500 in Chrome
# External models now appear in the model dropdown
```

---

## Documentation

This README is the landing page and the thesis. The reference material is split into focused guides:

| Guide | What's inside |
|-------|---------------|
| [**The language**](guides/LANGUAGE.md) | Selector grammar, name normalization, the closed op set, the `$S()` query/traversal API, class & id authoring, lasso, and host-enforced guards. |
| [**`$S` / 3DOM library**](https://github.com/tejaswigowda/3dom) | The standalone "jQuery for 3D" extraction: selectors + auto-labelling + op-chaining over any three.js scene, three as a peer dependency, and its own undo. Versioned surface in [SPEC.md](https://github.com/tejaswigowda/3dom/blob/main/SPEC.md). Now its own package/repo: `@tejaswigowda/3dom` (https://github.com/tejaswigowda/3dom), consumed here from a pinned CDN build. Docs: http://tejaswigowda.com/3dom/, [live demo](http://tejaswigowda.com/3dom/examples/bare.html). |
| [**Animation**](guides/ANIMATION.md) | The scene-wide universal timeline: absolute-time tracks, `.then`/`.with`/`.at` sugar, entrance/exit/attention recipes, lifecycle. |
| [**Scene intelligence**](guides/SCENE_INTELLIGENCE.md) | Descriptor-derived classes, symmetry pairs, texture-color naming, and `findByDescription`. No vision model. |
| [**JS Shell**](guides/JS_SHELL.md) | The primary editing surface: Monaco integration, core globals, object lookup, spatial helpers, modeling ops, Edit Mode, and `fetchAPI`. |
| [**Optional AI acceleration**](guides/AI_GUIDE.md) | The agentic loop, AI scene context, model configuration (WebLLM / external / client-side), cost tracking, and the generation eval. |
| [**Architecture**](guides/ARCHITECTURE.md) | Two-form scene representation (git-diffable round-trip) and the full module map. |
| [**Git versioning**](guides/GIT_VERSIONING.md) | Repository sync, the merge-conflict viewport, and access-token scope. |
| [**Roadmap**](guides/ROADMAP.md) | Done / next / then. |
| [**Dev Mode API**](guides/DEV_MODE_API.md) | Server-side external-model proxy and its security model. |
| Mesh editing | [Quick start](guides/MESH_EDITING_QUICK_START.md) · [Guide](guides/MESH_EDITING_GUIDE.md) · [Technical](guides/MESH_EDITING_TECHNICAL.md) · [Status](guides/IMPLEMENTATION_STATUS.md) |

---

## The two-way gate (host ↔ model)

The language is the primary interface. You edit by hand or with AI — same surface, one execution stack.

**By hand:**
```js
$S('.rims').recolor('#111')         // selector + op → execute
$S('.wheel.front').spin('y', 1, 2)  // compound selector + animation
op({ type:'recolor', selector:'.rims', color:'red' })   // explicit op-JSON
```

**With optional AI:** The host (deterministic) and model (user-chosen) form a gate.

```js
// "make the wheels black"
// → Host resolves ".wheels", validates
// → Model fills op-JSON (if needed)
// → execute, scene updates, git records
```

**Task split:** The eval showed selector-resolution caps at 77% even at Opus (capability-bound). It moved to the host. The design: **decompose, don't expand the model's job.**

| Task | Handler | Why |
|------|---------|-----|
| **Selector resolution** | **HOST** (deterministic) | ~97% resolved with no model call. Match labels + auto-classes over the known scene graph. When genuinely ambiguous, host clarifies (pick-don't-compose). Moved off the model because Opus caps 77% — it's capability-bound. |
| **Multi-op segmentation** | **HOST** (deterministic) | Host decides how many ops to emit and their order (request segmentation). |
| **Argument extraction** | **MODEL** | Fill in the values: the color for `recolor`, the scale factor for `scale`. Caps ~92% at both Opus and 1.5B (the achievable ceiling). |
| **Op-selection** | **MODEL** | Choose the operation type: `recolor` vs `scale` vs `move`. Constrained to the enum; ~77% at 1.5B. |
| **Labeling** | **MODEL** | Pure generation: name an unlabeled shape. The most model-bound task (~67% at 1.5B); also the least critical to decompose. |

The host enforces: clone-on-write (shared materials), normalization ("black" → `#111`), texture-tint warnings, merged-mesh graceful-fail, subset-sanity flags. The model stays in bounds: emits selector + op, host validates. See [AI guide](guides/AI_GUIDE.md).

---

## Features

| | |
|---|---|
| **Selector-based language** | Address parts by CSS-like selector (`$S('.wheel.front')`). Edit with guarded ops: `recolor`, `scale`, `spin`, etc. Deterministic resolution. See [LANGUAGE.md](guides/LANGUAGE.md). |
| **Git versioning** | Auto-load, commit, split-screen merge-conflict resolution. AI writes diff-aware messages. Diffable JSON. See [GIT_VERSIONING.md](guides/GIT_VERSIONING.md). |
| **JS Shell** | REPL: type queries, edit manually, or ask AI. Every command undoable and versioned. See [JS_SHELL.md](guides/JS_SHELL.md). |
| **Sovereign by default** | On-device inference (WebGPU/WebLLM). Nothing leaves the device except by your explicit action (git, `fetchAPI`). |
| **Universal timeline** | Scene-wide absolute clock. Tracks addressed by selector (objects + camera). Events versioned in JSON and glTF. AI authors via deterministic recipes. See [ANIMATION.md](guides/ANIMATION.md). |
| **Scene intelligence** | Geometry/color/symmetry descriptors → auto-classes (no vision model). Resolve descriptive references on imported GLBs. See [SCENE_INTELLIGENCE.md](guides/SCENE_INTELLIGENCE.md). |
| **Optional AI** | Natural language → selector + op. Model-agnostic (WebLLM, Ollama, OpenAI, Claude). Bounded 5-task decomposition. Self-correcting loop. Production ships validated models. See [AI_GUIDE.md](guides/AI_GUIDE.md). |
| **Modeling ops** | Boolean CSG, mirror, array, subdivide. Undoable, command-backed. |
| **Lasso & selection** | Freehand draw to select. Interactive or programmatic: `lasso([[x,y],…]).recolor('#f00')`. First-class pseudo-selectors `$S(':lasso')` / `$S(':selected')`. |
| **Class & id authoring** | jQuery-style: `.addClass()`, `.removeClass()`, `.editID()`. Names normalize; auto-derived and hand-typed tokens always match. |
| **Edit Mode** | Half-edge mesh editing: vertex/edge/face select, extrude, inset, bevel, delete, weld, UV. |

---

## Where Strata sits

**The authoring layer.** Build fast (AI + WebGL, no render wait), iterate with full undo/git, hand off to any renderer or engine.

- **Author here:** Structure + design (selectors / ops, labels, clips), versioned in git.
- **Hand off via glTF + labels** to any renderer (Blender / Unreal / media) or engine (three.js / Unity / runtime), where behavior attaches to the labels.

**Why the boundary matters:** No runtime, no interaction, no render-wait-during-iteration. Once a task needs one of those, it belongs downstream.

**Export status (honest):** glTF with animations works today. Label strings ride along on `userData → extras`. Auto-classes don't yet serialize; end-to-end handoff is partial/roadmap.

---

## The eval matrix: the editing gate

**The matrix ran, and it set the production model size.** Per-task, per-model-size, per-scaffolding, with resolved-correct-node scoring. 0.5B / 1.5B / 3B / 7B Qwen, plus Haiku/Opus ceilings. Run it yourself:

```js
await evalEditMatrix('scaffolded')   // then 'bare'
```

**Results (scaffolded):**

| task | 0.5B | 1.5B | 3B | Haiku | Opus |
|------|------|------|-----|-------|------|
| op-selection | 8% | **77%** | 69% | 85% | 92% |
| selector-resolution | 8% | 54% | 38% | 46% | 77% |
| arg-extraction | 46% | **92%** | 85% | 85% | 92% |
| labeling | 33% | 67% | 78% | 100% | 89% |
| multi-op | 0% | **75%** | 25% | 75% | 100% |
| **overall** | 19% | **73%** | 59% | 78% | 90% |

**Host-resolved (1.5B before/after):** Moving selector-resolution to the host doesn't change the model's architecture — it changes which **tasks need a model at all**. The gain is 97% of selector work moving off the model (no model call), so task performance becomes deterministic for the decomposed work.

| task | scaffolded (1.5B) | host-resolved (1.5B) |
|------|-------------------|----------------------|
| selector-resolution | 54% | **91%** |
| multi-op | 75% | **85%** |
| **overall** | 73% | **86%** |

**Dose-response (host-resolved, same 88 fixtures):** Model capability predicts performance in proportion to how much of a task stays on the model. The spread across 0.5B / 1.5B / Haiku shrinks with host share.

| task | 0.5B | 1.5B | Haiku* | spread | host does |
|------|------|------|--------|--------|-----------|
| selector-resolution | 91% | 91% | 86%* | 5pt | 97% host-side |
| multi-op | 62% | 85% | 77%* | 23pt | host segments N |
| arg-extraction | 73% | 91% | 95% | 22pt | model |
| op-selection | 45% | 86% | 100% | 55pt | model |
| labeling | 33% | 67% | 100% | 67pt | model |

*Haiku host-resolved results are contaminated by two unfixed selector bugs (tie-break, segment dedupe); clean re-run pending.

**The clearest finding: a 0.5B that scored 8% on selector-resolution scaffolded (reverted to boilerplate — under-capacity) reaches 91% host-resolved, identical to the 1.5B.** That is the decompose-don't-expand principle made concrete: task performance stops depending on model size once the hard part moves off the model.

**Quantization:** q4f16 (~1GB) == q4f32 (~1.9GB) byte-identical on all 88 fixtures. Host-side decomposition made the system quantization-insensitive too; model properties stop mattering once the task is off the model.

**What it shows:**

1. **Scaffolding unlocks capable models.** Delta: Haiku +52, Opus +45, small models +7–13. Not parity; sufficiency: 1.5B at 73% scaffolded becomes 86% host-resolved — sufficient for editing with host-resolution.

2. **Host-resolution collapses the hard task.** Selector-resolution: scaffolded 54% (capability-bound even at Opus 77%) → host-resolved 91% (97% host-side, only genuine ambiguity stays on model). Task spread: 77pt frontier gap → 5pt host-resolved gap. Model size becomes irrelevant for the decomposed work.

3. **1.5B ties the frontier on decomposed tasks.** Selector-resolution 91% (ties Haiku, Opus equivalent on the 3% ambiguous cases); multi-op 85% (Haiku 77* pending clean run). Still trails on pure-generation tasks (labeling 67 vs 100). Sufficiency, not parity: enough for production editing; correctly weaker on what's genuinely fuzzy.

4. **0.5B under-capacity scaffolded, sufficient host-resolved.** Scaffolded selector-resolution 8% (reverts to boilerplate); host-resolved 91% (identical to 1.5B). Proves decomposition works: even a model that can't do the task ends up 91% when the task is gone.

5. **~1GB is the default.** q4f16 quantization (1GB) identical to q4f32 (1.9GB) on all fixtures. Decomposition made the system quantization-insensitive.

**Ship decision:** Production shows 1.5B+ only; 0.5B excluded (under-capacity scaffolded, redundant host-resolved). Host-resolution is production-ready on the current model lineup. The eval demonstrated it; the gate proves it.

---

## Design principles

- **Sovereignty is a property, not a mode.** On-device by default (WebLLM). User picks the model: local ~1GB 1.5B (sovereign) or API (their key). Never silently escalates. Sovereignty falls out of the architecture.
- **Language is the workhorse. AI is optional.** Manual editing is first-class. You can edit entirely by hand. The model is not the subject.
- **Model-agnostic.** Wrap any model (WebLLM, Ollama, OpenAI, Claude) in the same scaffolding. Both local small models and frontier APIs lift from the same architecture.
- **Decompose, don't expand.** If a task caps out (selector-resolution at 77% even at Opus), move it host-side. Once decomposed, model capability becomes irrelevant.
- **One execution surface.** Manual code, AI code, eval fixtures all run through the same `execute()` binding and undo stack.
- **Never silently wrong.** Ambiguous resolution, lossy codegen, merged-mesh GLBs are flagged. Implemented ≠ validated. This README says which is which.
- **No build step.** Plain ES modules, importmap, three.js peer dependency. Serve and run.

---

## Prior art

Selector-over-graph exists (three-query-selector, querySelectorAll). NL-to-3D exists (Cypher, BBQ, FreeQ-Graph). Strata's synthesis: descriptor-derived classes, user-verified labels, selector editing + versioning, bounded optional AI. Integrated extension, not invention.

---

## Roadmap (at a glance)

- **Done.** Deterministic language (selectors + ops), `$S()` API, universal timeline (absolute + `.then`/`.with`/`.at`), git versioning, scene intelligence, constrained decoding, **eval matrix** (1.5B is viable floor), multi-op segmentation, bulk property ops, standalone [3DOM library](https://github.com/tejaswigowda/3dom) (Strata consumes via host adapter).
- **Next.** Host-side selector resolution. Haiku re-run. Op-selection host-assist. Alien-syntax ablation.
- **Then.** glTF label export, optional vision layer, renderer-agnostic pipeline, capture integration, sovereignty dashboard.

Full details in [ROADMAP.md](guides/ROADMAP.md).
