# Strata — Eval Matrix Handover

> **What this is.** The instructions to run **the gate**: the per-task × per-model-size ×
> per-scaffolding eval matrix (plus a cloud-model ceiling) that turns Strata's 5 fuzzy
> tasks from *implemented* into *validated*. This run confirms (or refutes) the
> zero-training claim, sets the model size to ship, and produces the core publication
> evidence.
>
> **Why it matters.** Everything the README honestly defers points here. The
> architecture is built and stated; this is the measurement that proves it works. Until
> this runs, the 5 tasks are *built, not validated* — this run closes that gap.
>
> **Owner:** whoever runs it. **Prereq:** a machine that can load the model sizes below
> (see §2). **Output:** a results table + a short written interpretation (§7–8).

---

## 0. TL;DR — what you're doing

```
For each MODEL SIZE × each SCAFFOLDING CONDITION:
  run evalEditMatrix(condition)  → get per-task pass rates for the 5 fuzzy tasks
Assemble into ONE matrix. Add a cloud-model (Haiku) row as the CEILING.
Read: (a) does a small model clear the bar scaffolded?  (the ship-size decision)
      (b) how much does scaffolding move each task?     (the thesis: scaffolding-moves-the-cliff)
      (c) where's the cliff?                            (which task fails first, at which size)
```

---

## 1. PREREQUISITE GATE — verify BEFORE running (do not skip)

The results are only trustworthy if the harness and its checks are sound. Confirm each,
because a broken check produces confident-but-wrong numbers (the exact failure the
"never silently wrong" principle exists to prevent).

```
[ ] editMatrix.js actually RUNS end-to-end. Call `await evalEditMatrix('scaffolded')`
    on a loaded model and confirm it returns a real per-task table, not an error / stub.
    (The README lists it as a built harness; confirm the RUN works, not just that the
    file exists.)
[ ] The per-task SCORERS are trustworthy. Spot-check each of the 5 scorers against a
    hand-verified case:
      - op-type selection  → correct op chosen for a known verb
      - selector resolution → RESOLVED-CORRECT-NODE (right nodes changed, ONLY those —
        this is the critical axis; verify it flags "changed everything" as FAIL, not pass)
      - argument extraction → "black"→#111, "slowly"→dur, verified against expected
      - labeling           → proposed label matches ground truth on a known part
      - multi-op           → "wheels black and body red" scored as 2 correct ops, and
        a MISSED split (only 1 op) scored as FAIL
[ ] Known false-positive classes are NOT firing. Confirm the scorer doesn't repeat the
    old eval bugs: co-location/adjacency false-pass, duplicate-const misread,
    extractCode running prose. (These bit the generation eval; make sure editMatrix
    doesn't inherit them.)
[ ] Non-destructive confirmed. The harness snapshots + restores the scene (README says
    so) — verify your working scene survives a run.
[ ] Synthetic assets are representative. The harness uses synthetic fixtures; confirm
    they exercise the HARD cases (compound selectors, symmetry pairs, name-stem classes,
    merged-mesh graceful-fail), not just trivial single-part edits. If fixtures are too
    easy, the matrix will look better than reality.
```

**If any check fails, fix the harness FIRST.** A wrong ruler makes the whole matrix
meaningless. This gate protects the publication claim.

---

## 2. THE MATRIX AXES

### Axis 1 — Model size (the ship-size question)
Run each size you can load. Suggested set (adjust to what runs on your hardware):

```
[ ] 7B   Qwen2.5-Coder-7B   (the "Power" tier — expected strong; upper baseline)
[ ] 1.5B Qwen2.5-Coder-1.5B (the current "Default" — the candidate ship size)
[ ] ~0.5B a smaller coder model if available (test "can we go smaller?")
[ ] (optional) 1B Llama-3.2-1B (the "Lite" tier — expected weak; lower baseline)
```
The point is to find the **cliff**: the size below which a task falls apart. Predicted
cliff is at selector-resolution + multi-op (the two tasks with residual reasoning).

### Axis 2 — Scaffolding condition (the thesis)
```
[ ] 'scaffolded'  — selector injection ON (current scaffolding). NOTE: per the README,
                    this is SELECTOR-INJECTION-ONLY. Constrained decoding is NOT yet
                    wired, so these numbers are a FLOOR, not the ceiling of scaffolding.
[ ] 'bare'        — no scaffolding (raw model). The baseline.
```
The **delta between bare and scaffolded** IS the thesis ("scaffolding moves the cliff").
Report it per task, per size — it's the most important number in the whole run.

### Axis 3 — The ceiling (a cloud model)
```
[ ] Haiku (via dev mode or client-side API) — run the SAME matrix as an upper bound.
    This is the "what's the best achievable" reference, NOT a ship candidate. It tells
    you how much headroom the small local model is leaving on the table per task.
```

---

## 3. THE 5 TASKS SCORED (what each column means)

```
1. op-type selection      — did it pick the right op from the closed set?
2. selector resolution    — RESOLVED-CORRECT-NODE: right nodes changed, ONLY those.
                            (the critical axis — a task that changes the wrong/all nodes
                            is a FAIL even if it "ran clean")
3. argument extraction    — did modifiers map to correct args (color/dur/axis/factor)?
4. labeling (import)      — did descriptors+material→label match ground truth?
5. multi-op decomposition — did one request split into the correct N ops?
```
Each scored INDEPENDENTLY from one generated edit (per the harness design). Report each
as a pass rate over the fixture set.

---

## 4. RUN PROCEDURE

```
For each model size:
  1. Load the model (shell header → select → Load AI). Confirm it's ready.
  2. await evalEditMatrix('scaffolded')   → record the 5 per-task pass rates
  3. await evalEditMatrix('bare')         → record the 5 per-task pass rates
  4. Note: context window in effect, any load warnings, wall-clock per run.
Then:
  5. Load Haiku (dev mode or client-side API). Run both conditions → the ceiling row.
  6. Assemble the full matrix (§5 template).
```
Run each condition MORE THAN ONCE if there's output variance (small models can be
nondeterministic). Report mean + whether variance is high enough to affect conclusions.
If the harness has a seed/temperature control, fix it and say what you used.

---

## 5. RESULTS TEMPLATE (fill this in)

```
SCAFFOLDED
model    | op-type | selector(RCN) | arg-extract | labeling | multi-op | notes
---------|---------|---------------|-------------|----------|----------|------
7B       |         |               |             |          |          |
1.5B     |         |               |             |          |          |
0.5B     |         |               |             |          |          |
Haiku*   |         |               |             |          |          | *ceiling

BARE
model    | op-type | selector(RCN) | arg-extract | labeling | multi-op | notes
---------|---------|---------------|-------------|----------|----------|------
7B       |         |               |             |          |          |
1.5B     |         |               |             |          |          |
0.5B     |         |               |             |          |          |
Haiku*   |         |               |             |          |          | *ceiling

DELTA (scaffolded − bare)  ← THE THESIS
model    | op-type | selector(RCN) | arg-extract | labeling | multi-op
---------|---------|---------------|-------------|----------|----------
7B       |         |               |             |          |
1.5B     |         |               |             |          |
0.5B     |         |               |             |          |
```

---

## 6. WHAT THE RESULTS DECIDE

```
SHIP-SIZE DECISION:
  → the smallest model whose SCAFFOLDED pass rates clear your bar on all 5 tasks
    (define the bar BEFORE looking — e.g. ≥90% per task, or per-task thresholds).
    That's the model Strata ships as default.

ZERO-TRAINING CLAIM:
  → CONFIRMED if a stock (untrained) small model clears the bar scaffolded.
  → QUALIFIED if it clears most tasks but one lags → that one task is the fine-tune
    candidate (the PINNED narrow fine-tune: hundreds of (text→op-JSON) pairs teaching
    YOUR op-JSON conventions, NOT CSS — the model has CSS). Only pursue if the eval
    demands it.

THE THESIS (scaffolding-moves-the-cliff):
  → SUPPORTED if the bare→scaffolded DELTA is large, especially on selector-resolution
    and multi-op (the predicted cliff tasks). This delta is the paper's core evidence.

HOW-SMALL-CAN-WE-GO:
  → if 0.5B clears scaffolded, the "tiny model suffices" claim is strong. If it cliffs,
    1.5B is the floor. Either is a publishable, honest result.
```

---

## 7. HONESTY NOTES (carry into the writeup — non-negotiable)

```
- "scaffolded" here = SELECTOR-INJECTION-ONLY. Constrained decoding is NOT wired yet.
  So scaffolded numbers are a FLOOR — a task that fails scaffolded MIGHT pass with
  constrained decoding added. Do NOT conclude "the model can't do X" from this run;
  conclude "selector-injection scaffolding isn't enough for X yet." State this explicitly.
- Report BARE too, always. The delta is the point; scaffolded-alone hides the thesis.
- resolved-correct-node is the honest selector metric. Don't soften it to "ran clean."
  Changing the wrong nodes is a FAIL.
- Report variance. Small-model nondeterminism can swing a task; say how many runs and
  whether the conclusion is robust to the spread.
- Fixtures are synthetic. Note that real imported GLBs may be harder; the matrix is a
  controlled lower-bound on difficulty, not a field test. A follow-up on real assets
  strengthens the claim.
- Implemented ≠ validated, still. This run validates the TASKS under the CURRENT
  scaffolding on SYNTHETIC fixtures. Say exactly that; don't overclaim to "Strata works."
```

---

## 8. DELIVERABLE OF THIS RUN

```
[ ] The filled matrix (§5): scaffolded, bare, and delta, across sizes + Haiku ceiling
[ ] The ship-size decision + the bar you set (stated before looking)
[ ] The zero-training verdict (confirmed / qualified-with-which-task-lagging)
[ ] The thesis verdict (is the bare→scaffolded delta large on the cliff tasks?)
[ ] The honesty notes (§7) folded into the interpretation
[ ] A one-paragraph summary: "with [scaffolding], a [size] on-device model achieves
    [rates] on the 5 editing tasks — [confirming/qualifying] that no task-specific
    training is needed; the largest scaffolding gain is on [task]; the cliff is at [size/task]."
→ this paragraph + the matrix ARE the publication evidence and the README update.
```

---

## 9. AFTER THE RUN — what it unblocks

```
- UPDATE THE README eval section: replace "NOT yet run" with the results + interpretation.
  Move the 5 tasks from "built, not validated" to "validated (under selector-injection
  scaffolding, synthetic fixtures) — see matrix."
- THE SHIP-SIZE is now decided → set the default model accordingly.
- THE FINE-TUNE decision resolves: only pursue the pinned narrow fine-tune if a task
  lagged. Otherwise, zero-training holds — say so.
- IF the thesis held (big scaffolding delta) → this is the spine of the UIST/CHI paper,
  paired with the student user study (the human eval).
- NEXT scaffolding lever (if a task lagged): wire CONSTRAINED DECODING, re-run that task,
  measure the additional gain (the roadmap's next item — and a second data point for
  scaffolding-moves-the-cliff).
```

---

## THE NORTH STAR FOR THIS RUN
This is the measurement the whole project has been built to enable. The architecture
decomposed 3D editing into a deterministic shell + 5 fuzzy tasks precisely so this
matrix could be run and a small sovereign model could be shown to suffice. Run it
honestly (verify the ruler first), report bare + scaffolded + delta across sizes with a
cloud ceiling, set the ship size, render the zero-training verdict, and state exactly
what was measured (current scaffolding, synthetic fixtures) and what wasn't. The result
— whatever it is — is publishable and honest. A small model clearing the bar validates
the thesis; a cliff at a specific task/size is a precise, useful, honest finding that
names the next lever. Either way, this run turns "implemented" into "measured," which is
the gate everything else waits behind.
