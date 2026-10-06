# Deviations — `smoke-local-20261005`

> **Run** `smoke-local-20261005` · **stage** SMOKE (development cell) · **status** COMPLETE
>
> **Confirmatory evidence is possible only in a held-out run after the development analysis is frozen. These results are not confirmatory.**

## From the frozen preregistration (verbatim)

## Deviations

*(append below; do not edit anything above)*

- none yet

*(The "none yet" line above was true when the file was frozen on 2026-10-02.
Everything below was appended on 2026-10-05; nothing above "## Deviations"
has been edited — `sol/tests/test_prereg_env.py` verifies the frozen text's
SHA-256 is still a0146494a27d1206d0efc3cb7f77d2413bc09a4aedcb98a632a5c61f09f5f014.)*

### D1 — 2026-10-05 — `blk` is not a clean held-out grammar family

**What happened.** §2 lists "all of `blk`" as the held-out grammar family. But
`blk x d50s1` was scored BEFORE the freeze (Phase 3.2 balanced Arm A, 272 sites,
0.5B base + instruct; Phase 3.3 primary run, 60 sites), and §8 of this very
document reports "`blk` ≈ `dom` on reversion". The family was inspected.

**Change.** `blk` is no longer called a held-out grammar family anywhere in
code or reports. `sol/src/p33/splits.py` classifies `blk x {dev lexicon}` as
EXPLORATORY-CONTAMINATED (refused unless explicitly allowed, then labelled) and
`blk x {never-scored held-out mapping}` as HELDOUT-WEAK-FAMILY: a weaker test in
which the grammar has been seen but that mapping has not. No new grammar family
is invented; `APPROVED_NEW_FAMILIES` is empty.

**Scientific consequence.** H4 criterion 3 ("AUROC ≥ 0.65 on the held-out
grammar family") is **NOT TESTABLE** until a new grammar family is explicitly
approved, designed and frozen. H4 can therefore at most be supported on held-out
MAPPINGS and MODELS, never on a held-out grammar. The §6 gate "do not scale
beyond 3B until the effect is present in `blk`" cannot be satisfied by `blk`
evidence and is implemented as "no model above 3B in any stage".

### D2 — 2026-10-05 — Qwen2.5-Coder-3B was observed before the freeze

`arm_a_sizes.json` (Phase 3.2) scored 3B base and instruct on `dom x d50s1`
under a superseded protocol (dom only, no token table, pre-P32-002). 3B
remains a held-out model but every 3B row and aggregate is labelled
HELDOUT-WEAKENED. **Consequence:** 3B cannot be the sole basis of a held-out-model claim.

### D3 — 2026-10-05 — `k*` definition clarified; pre-freeze `k*` values withdrawn

§4 said only that curves which never cross are censored. The implementation
left already-correct sites without a `k*` (84 of 125), took a later re-crossing
for the other 41, and marked 16 crossed-then-dropped curves as censored.
Separately, 82 of the 120 pre-freeze extinction sites had their own target
program among the demonstrations. **Change:** `M(0) ≥ 0 ⇒ k* = 0`; otherwise
the first upward crossing, interpolated; no crossing ⇒ censored; a curve that
crosses and later drops is not censored; KM summaries for ALL sites and for
INITIALLY-WRONG sites; median-among-crossers retained as a labelled diagnostic
only; demonstrations exclude the target template, its program and any prefix
that replays the decision. **Consequence:** the pre-freeze `k*` ≈ 5–7 figures
(Phase 3.3 reports) are withdrawn as contaminated; they are not evidence.

### D4 — 2026-10-05 — pre-freeze rule-effect intervals withdrawn

The template-cluster bootstrap collapsed duplicate draws when pairing rule
with no-rule rows by `site_id`, so resamples were effectively drawn without
replacement (verified: a hand example returned 2.0 instead of 5/3). Fixed in
`phase3_2.analysis`. **Consequence:** the Phase 3.3 rule-effect intervals were
exploratory and are superseded; recomputed values are reported as exploratory.

### D5 — 2026-10-05 — the de-duplication unit is now (family, lexicon)

§5 exclusion 2 said "not prefix-distinct after `dedupe_by_prefix`". The global
first-occurrence implementation was CLI-order dependent (reversing the lexicon
order moved retained `d50s2` sites from 172 to 272). Sites in different
lexicons are different stimuli because the rule table differs, so
de-duplication is now WITHIN (family, lexicon), with a canonical tie-break.
**Consequence:** eligible-site counts change; every dropped site is listed in
`split_exclusion_audit.csv` with the site it duplicates.

### D6 — 2026-10-05 — the identity baseline is constant on the eligible set

Exclusion 1 keeps only SEMANTIC sites, all of which are remapped, so the §3
identity baseline is constant there and its AUROC is exactly 0.5. Nothing is
changed. **Consequence (stated, not hidden):** criterion 1 is equivalent to
"AUROC ≥ 0.60 with the difference's interval above 0". A non-preregistered
`terminal_rate` baseline (cross-fitted per-role reversion rate) is reported as
EXPLORATORY, because it is the stronger "language-identity detector".

### D7 — 2026-10-05 — measurement precision and the length-matched control

Scoring now computes the output projection in float32 from the final hidden
state (bf16 logits quantise near-zero margins; the outcome is a margin's sign),
and adds a `norule_lenmatched` control padded to the rule prompt's token count.
**Consequence:** a methods change made before any confirmatory run; both are
recorded in every job manifest.

### D8 — 2026-10-05 — development models include the matched instruct twins

§2 names "Qwen2.5-Coder 0.5B and 1.5B" as non-held-out. H4 needs both
checkpoints of a pair, so the development set is read as base AND instruct for
0.5B and 1.5B. No other model is development.


## Run-level

- `allow_non_a100=True`: the A100 preflight requirement was waived for this run (local smoke only).
- Smoke run: one model, one development lexicon, one family, small n. Not an experiment.