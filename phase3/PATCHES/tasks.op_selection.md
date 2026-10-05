# P3-001 — `score_op_selection_report` accepted extra trailing operations

**File:** `vendor/grammar_and_3DOM_client/tasks.py`
**Function:** `score_op_selection_report`
**Upstream:** `grammar_and_3DOM_client/tasks.py:103` at commit `4e98055`
**Class:** silent false PASS — inflates task accuracy

## The defect

```python
if len(ops) < len(wanted):
    return FAIL, [...]
for i, want in enumerate(wanted):        # only ops[0 : len(wanted)]
    ...
```

The guard rejects under-production and ignores over-production. The loop never
looks past `len(wanted)`, so a program that performs the requested operation
**and then any number of additional operations** is scored PASS.

An extra operation is a wrong edit to the user's scene. On a single-op task
nothing else in the matrix catches it: `score_multi_op_report` would (it uses
`got != target_count`) but it is only *applicable* to multi-op cases, and
`score.py` emits an `extra_operation` hallucination label that no scorer reads.

## Why this is clearly a defect and not a policy choice

`SCORING_POLICY.md` §3 puts "wrong op count/order" in **VALID_WRONG**, not
VALID_CORRECT. And this same file already applies the exact-match rule on both
other axes:

- `score_multi_op_report`: `if got != target_count: return FAIL`
- `score_selector_resolution`: "The check is SET EQUALITY, not containment …
  Containment would pass `'*'` on every case, the single most important false
  pass in the whole matrix."

Prefix-matching an operation list is that same false pass, one axis over.

## The repair

```python
if len(ops) != len(wanted):
    direction = "under" if len(ops) < len(wanted) else "over"
    return FAIL, [f"... ({direction}-production)"]
```

## Blast radius

Affects any previously reported `op-selection` and therefore
`all_components_correct` figure wherever a model over-produced. Direction of
bias is one-way: **previously reported accuracy can only fall or stay equal.**
Experiment 02's accuracy table must be recomputed from retained raw outputs
before it is used; the Phase 3 result set is unaffected because no Phase 3
number predates this patch.

## Guard

`tests/test_scorer_repair.py` fails if the repair is absent, so re-running
`scripts/vendor_sync.py` (which overwrites the vendored copy) cannot silently
restore the defect.
