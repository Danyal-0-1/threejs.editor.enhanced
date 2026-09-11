# Experiment 01 — Phase 1/2 baseline

| Field | Value |
|---|---|
| Status | **CLOSED — NO WINNER** |
| Canonical ID | `20260901-233702` (UTC) |
| Executed | 2026-09-01 |
| Archived | 2026-09-10 |
| Commit at experiment start | `c3f9b26` |
| Original consolidated experiment commit | `d35e574` |

This directory is the complete historical record of the first experiment. Its
timestamped name remains unchanged because the captured logs and reports embed
that exact path. “Experiment 01” is the human-readable label.

## Scope

The run verified the frozen Phase 1 grammar contract, the Phase 2 φ-based
compiler and structural invariants, and tokenizer fertility for the original
`alpha`, `beta`, and `gamma` candidate lexicons.

## Closure decision

No candidate was selected:

- All three candidates failed the pre-committed tokenizer-fertility band
  `[0.95, 1.05]`.
- The earlier provisional `beta` decision was withdrawn: character-length
  parity did not produce tokenizer parity.
- `gamma` also failed the proposed lexical-class/reachability check `(g)` and is
  not a clean isomorphic control.
- Base-model ΔNLL was not run because `torch` was unavailable.

The structural implementation remains verified, including all 149 tests. The
failed outcome concerns the candidate-design approach, not the basic compiler
pipeline.

## Archive contents

| Path | Purpose |
|---|---|
| [RESULTS.md](RESULTS.md) | Final measured results and candidate decision |
| [AUDIT.md](AUDIT.md) | Detailed implementation and methodology audit |
| [RUNBOOK.md](RUNBOOK.md) | Snapshot of the runbook used for this experiment |
| [metadata/candidate-selection-precommit.md](metadata/candidate-selection-precommit.md) | Selection rule as it stood before the binding measurement |
| [results/](results/) | Individual result tables and traces |
| [logs/](logs/) | Captured stdout, stderr, commands, and exit metadata |
| [artifacts/](artifacts/) | Generated and before/after comparison artifacts |
| [metadata/](metadata/) | Approved plan, environments, revisions, and checksums |

Phase 1 and Phase 2 source files remain in `grammar_and_3DOM_client/` and
`alien_syntax/`; they are implementation and experiment inputs, not run output.
Their Experiment 01 state is fixed by the start commit and by
[`metadata/checksums.txt`](metadata/checksums.txt). The project-status documents
also remain outside this archive because they explain the phases rather than
recording one run.

## Archive rule

Treat this directory as read-only historical evidence. Changes to candidate
construction, constraints, or measurements belong to a new timestamped
experiment directory and must not replace these results.
