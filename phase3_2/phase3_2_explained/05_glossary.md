# 05 — Glossary (Phase 3.2 additions)

> `phase3/phase3_explained/05_glossary.md` defines ~55 terms (collision
> classes, `M_seq`, `S_seq`, `k*`, hurdle, canonical IR, AUROC, vendoring,
> fixtures, two-level lexer, …). **Unchanged; not repeated.** Only new or
> corrected terms appear here.

Each entry: **technical** · *simple* · project example · **common confusion**.

---

## Grammar families

**Grammar family** — A concrete syntax with its own non-terminals and
production shapes. · *A different sentence structure, not just different
words.* · `dom` (IIFE + fluent chaining) vs `blk` (block form). ·
**Confusion:** the central one in this project. `alpha/beta/gamma/delta` are
**lexicons**, not families — I1–I4 freeze N and the shape of P, so all four
are one grammar. Only `dom` vs `blk` is a family contrast.

**`dom` family** — The Phase 1/2 syntax. · *The jQuery-looking one.* ·
`(function(){ $S('.wheel').recolor('#111111'); })();` · **Confusion:** its
17-character opening is fixed by the grammar, so **no corpus can vary the
first site's prefix**. That is a property of the language, not of the data.

**`blk` family** — New in Phase 3.2. No IIFE, no chaining, no parentheses;
selector as a block header, operations as semicolon-terminated statements. ·
*The block-structured one.* · `$S '.wheel' { recolor '#111111'; }` ·
**Confusion:** it is not a renaming — it uses a **subset** of the same frozen
terminals in different productions, which is exactly what lets the same
φ-maps apply to both.

**Shared sub-language** — The inner selector grammar, identical in both
families and parsed by the **same vendored** parser. · *The part both
languages agree on.* · `'.wheel'` · **Confusion:** sharing it is deliberate,
not laziness — the sigil collision lives there, so it transfers across
families with the competitor held constant. A reimplementation could drift and
fake a cross-family effect.

**`program : block*`** — blk's start rule, with `*` not `+`. · *Zero blocks is
a legal program.* · **Confusion:** looks like a typo. It exists because
`(function(){})();` has zero operations, and under D5 that is a parse success
and a task failure. With `block+`, blk could not express it and the two
families would disagree on the most plausible null output a small model emits.

---

## The delta family

**Delta family** — A parameterised set of lexicons, `(density, seed, mode)`. ·
*Many versions of the same idea, varied on purpose.* · `d25s1`, `d50s2`,
`d75s3a`. · **Confusion:** it is not nine arbitrary lexicons; density and seed
are the two factors, and the seed is the entire counterbalancing mechanism.

**Collision density** — Fraction of substitutable roles remapped. ·
*How much of the language is a false friend.* · `d50s1` permutes 13 of 29. ·
**Confusion:** **role** density ≠ **site** density. 0.45 of roles gives ≈0.36
of sites, because roles occur at different frequencies. Quote the right one.

**Density ceiling (79%)** — 306 of 387 sites; the other 81 are `T_CHAIN_OP`,
locked LEXICAL by I7. · *The most false friends the grammar allows.* ·
**Confusion:** it is a limit to stay well below, not a target. At the ceiling
there are no non-colliding control sites and **H5 becomes untestable**.

**Rotation seed** — Seeds the shuffle that decides which spelling lands on
which role. · *Which word means what, varied deliberately.* ·
**Confusion:** this *is* the counterbalancing, and it is also what supplies
held-out mappings. Phase 3 had neither because it had one lexicon.

**Strict vs arity mode** — `strict` permutes verbs with identical C8
signatures; `arity` permutes verbs with the same argument **count**. ·
*Swap only verbs that take exactly the same arguments, or merely the same
number of them.* · strict reaches ~0.45 density; arity reaches 0.76. ·
**Confusion:** arity mode changes argument **keys** —
`{"color": "#111111"}` becomes `{"opacity": "#111111"}`. Well-formed,
different IR, genuine collision, but semantically odd. The `a` suffix in the
`phi_id` exists so the two modes cannot be pooled unnoticed.

---

## Site strata

**Stratum** — A partition of sites by what competence the decision needs:
`sigil`, `verb`, `keyword`. · *How much you need to understand the task, as
opposed to the syntax.* · **Confusion:** not a difficulty ordering. It is a
**confound control** for the question "does 3D knowledge matter?".

**Sigil stratum** — `.` vs `#`, `>` vs `*`. · *Pure punctuation.* ·
**Confusion:** this is the **cleanest** arm, needing no 3D knowledge at all —
and the one the P32-001 defect was hiding almost entirely (0.106 → 0.515).

**Verb stratum** — `scale` vs `move`. · *You must understand the request.* ·
**Confusion:** these sites **conflate** surface collision with 3D-domain
competence. Measured: they revert *less* than sigil sites at every
checkpoint, so domain knowledge is not driving the effect.

---

## Measurement

**First divergent token** — The first index at which the two candidates'
tokenisations differ. · *Where the two versions stop being the same.* ·
`k_common = 11` for the class-sigil site under Qwen. · **Confusion:** a
**token** index, not a character index. Characters and tokens do not align —
the merged token `('#` straddles the boundary.

**Candidate merging** — BPE folding the candidate into the preceding token, so
`tok(prefix + c)` is no longer than `tok(prefix)`. · *The tokenizer glues them
together.* · `('` + `#` → the single token `('#`. **44.2% of real sites.** ·
**Confusion:** it is not rare or exotic. It is the normal case at exactly the
sites that matter most.

**P32-001** — The defect where the old scorer returned `0.0` for merged
candidates. · *The bug that hid the effect.* · sigil reversion 0.106 → 0.515
after the fix. · **Confusion:** the bias is **one-way** — `M_seq = 0` is not
negative, so the defect can only ever *understate* reversion. It produces
false nulls, never false positives.

**`MarginV2`** — The corrected margin record, with `k_common` and `merged`. ·
*The fixed measurement, plus the evidence it is fixed.* ·
**Confusion:** not interchangeable with Phase 3's `MarginRecord`; it needs a
`TokenScorer` (`score_pair`), not an `LM` (`sequence_logprob`).

**Token fertility (measured)** — Tokens per character under a real tokenizer,
relative to identity. · *How much more the alien version costs the model.* ·
`dom` 1.072–1.078; `blk` 1.003–1.009. · **Confusion:** **character length is
not fertility.** Phase 3's 1.0078 proxy understated the `dom` confound ~10×.
Only `blk` is actually fertility-controlled.

**Fertility-controlled arm** — The `blk` family, where `F_rel ≈ 1.00`. ·
*The comparison where token cost is not a confound.* · **Confusion:** this is
an observation about one tokenizer (Qwen). It needs re-checking per model
family before it is relied on.

---

## Process

**Superseded number** — A previously reported figure that a later measurement
replaces. · *Something we used to believe.* · delta fertility 1.0078 → 1.077;
sigil reversion 0.106 → 0.515; "Phase 1 has one opening" → 3 at k=17. ·
**Confusion:** superseding is not erratum-hiding. `CHANGES_FROM_PHASE3.md`
keeps both numbers and the blast radius, so a reader of the old document can
find out it is stale.

**Declared deviation** — A rule the work knowingly breaks, written down. ·
*We did the thing we said we would not, and here is why.* · Phase 3.2 writes
9 `phi_d*.json` files into `phase3/vendor/.../candidates/`, because
`phi.load_candidate` resolves only there. · **Confusion:** a declared
deviation is still a deviation. `vendor_sync.py --check` will **not** catch
it, because it verifies the files it copied and does not notice additions.

---

## Added in revision 2

**Balanced sampling** — Round-robin selection across every
(family × lexicon × stratum) cell, so any limit preserves the full set's
proportions. · *Take some from every bucket, not the first N off the pile.* ·
`sampling.balanced`. · **Confusion:** `dedupe_by_prefix(pool)[:240]` looks
like a sample and is not — it is whatever order the loops ran in. That slice
scored 240 `dom` sites and zero `blk` (defect P32-003).

**Cell** — One (family, lexicon, stratum) combination. · *One box in the
design grid.* · `blk/d50s1/sigil`. · **Confusion:** an empty cell invalidates
every cross-cell comparison, however healthy the aggregate looks. Print
`cell_counts` next to every result.

**Rule condition / no-rule control** — Two matched prompts: one carrying the
full φ token table, one with the spellings withheld. · *Told the mapping vs
not told.* · 1,527 vs 1,014 chars, 36 lines each. · **Confusion:** the control
is **matched**, not absent. A bare prompt would differ in length, register and
token count as well as content, so any difference could be attributed to those.

**Rule effect** — `M_seq(rule) − M_seq(norule)` per site. · *How much the
table actually bought.* · Measured +0.156 to +0.222 nats, helping 52.6–59.2%
of sites. · **Confusion:** a near-zero rule effect is a **result**, not a null
measurement — it says the specification is not being used.

**P32-002** — The defect where the rule prompt contained no rule. · *We told
it to follow a table we never showed it.* · **Confusion:** this is worse than
a wrong number. Without a supplied mapping, `M_seq` is not a reversion measure
at all; it is raw prior preference over a language the model has never seen.

**P32-003** — The defect where first-*N* slicing scored one family. ·
*We only drove on half the runway.* · **Confusion:** the dropped half was
`blk`, the **fertility-matched** family — so the surviving numbers were
confounded with token cost in exactly the way the second family existed to
rule out.

**P32-004** — The defect where only aggregates were saved. · *No flight
recorder.* · **Confusion:** aggregates look like data. They cannot be
re-analysed, re-split by family, or checked for the merge structure, so a
defect found later forces a full re-run.

**Flight recorder / per-site row** — One saved record per (model, condition,
site), carrying family, lexicon, template, terminal, role, stratum, both
candidates, `m_seq`, both log-probs, `k_common`, `merged`, token counts and
char offset. · *Everything needed to re-analyse without re-running.* · 2,176
rows in the balanced run. · **Confusion:** provenance is not optional
metadata; without `family` on the row the P32-003 defect is undetectable
after the fact.

**Withdrawn result** — A reported conclusion later retracted because the run
that produced it was invalid. · *We said it; it wasn't true.* · The
"sigil ≥ verb, so 3D knowledge doesn't matter" claim. · **Confusion:** a
withdrawn result is not the same as a negative one. The question is reopened,
not answered, and the retraction and its cause stay in the record.
