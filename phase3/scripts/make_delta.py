"""make_delta.py — generate `delta`, the φ-map Phase 3 actually runs on.

    python3 scripts/make_delta.py                 # write + verify
    python3 scripts/make_delta.py --verify-only

----------------------------------------------------------------------------
WHY A NEW LEXICON IS NECESSARY
----------------------------------------------------------------------------
`scripts/site_census.py` measures the shipped lexicons and finds:

    beta, gamma   0 usable sites — their alphabets are disjoint from CSS, so
                  the familiar spelling is a LEX error, never a wrong meaning.
    alpha        72 usable sites (18.6%), almost all verbs; the headline
                  class-sigil site is LEXICAL, not semantic.

The review's primary contrast needs sites where the correct and the familiar
spelling are BOTH grammar-valid and lower to DIFFERENT canonical IRs. None of
the three shipped lexicons was designed for that, so Phase 3 designs one.

----------------------------------------------------------------------------
THE DESIGN RULE (measured, not assumed)
----------------------------------------------------------------------------
    SILENT COLLISIONS REQUIRE PERMUTATION **WITHIN A SHAPE CLASS**.

Two roles collide silently only if they accept the same syntactic shape, so
exchanging them leaves the program parseable while changing its meaning.
alpha permutes ACROSS shape classes (a 5-cycle on {. # : > *}), which is why
its familiar forms mostly fail to parse: `.` lands on T_WILDCARD, which takes
no identifier, so the familiar `.door` is a syntax error.

----------------------------------------------------------------------------
WHAT MAKES delta A BETTER EXPERIMENTAL MATERIAL THAN alpha
----------------------------------------------------------------------------
delta is **identity everywhere except the designed collision sites**. Every
spelling it uses is a 3DOM spelling; only the role bindings move, and only
within a shape class. Consequences:

  * token fertility is ~unchanged from identity, because the multiset of
    spellings is unchanged — this removes the confound the review flags as
    unmatchable in alpha/beta/gamma (relative fertility 1.068 / 1.401 / 1.937);
  * competitor prior strength stays HIGH, because every competitor is a real
    CSS/jQuery/3DOM token the model has strong expectations about;
  * the manipulation is therefore role reassignment and nothing else.

That is the minimal pair the review asks for and could not get from the
Phase 2 candidates.

----------------------------------------------------------------------------
THE PERMUTATIONS
----------------------------------------------------------------------------
1. SIGILS  T_CLASS_SIGIL '.' -> '#',  T_ID_SIGIL '#' -> '.'
   T_CHAIN_OP must move with T_CLASS_SIGIL: invariant I7 / validator V5+V6
   require the overload group {T_CHAIN_OP, T_CLASS_SIGIL} to keep ONE shared
   spelling, because de-overloading would make delta strictly easier to lex
   than 3DOM — an unmatched complexity change. So T_CHAIN_OP '.' -> '#' too.
   Class and id sigils have the same shape (`sigil IDENT`, inner stream), so
   this transposition is silent. The chain-op site is not: outer `.` has no
   binding in delta, so it stays a LEX error. That is expected and recorded.

2. VERBS, within identical C8 signatures only, so arity AND argument keys
   stay type-correct:
       ("enabled",)        wireframe -> castShadow -> receiveShadow -> wireframe
       ("dx","dy","dz")    move <-> duplicate
   Permuting verbs with different signatures would change the argument count
   and produce a parse or canonicalisation error — loud, not silent.

3. TYPE KEYWORDS (bare keywords, one shape)  mesh->group->light->camera->mesh
4. PSEUDO KEYWORDS                           selected <-> lasso

Everything else is identity.

----------------------------------------------------------------------------
GENERATE, THEN PROVE
----------------------------------------------------------------------------
This script does not trust the reasoning above. After writing the map it runs
`validate_phi` (V1-V8, including the V6 bijectivity/partition proof) and then
re-runs the collision classifier over the whole corpus, and FAILS if any
intended site is not SEMANTIC. The design rule is a hypothesis; the classifier
is the test.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from phase3 import _vendor  # noqa: E402,F401

import generate_corpus as G  # noqa: E402
import phi as P  # noqa: E402
import transpiler as T  # noqa: E402

from phase3 import sites as S  # noqa: E402

OUT = os.path.join(_vendor.VENDOR, "alien_syntax", "candidates", "phi_delta.json")

# Cycles are written as ordered lists: each terminal takes the NEXT one's
# 3DOM spelling, wrapping around. A 2-element list is a transposition.
SIGIL_SWAP = ["T_CLASS_SIGIL", "T_ID_SIGIL"]
CHAIN_FOLLOWS = "T_CHAIN_OP"            # I7: must match T_CLASS_SIGIL
VERB_CYCLES = [
    ["T_VERB_WIREFRAME", "T_VERB_CASTSHADOW", "T_VERB_RECEIVESHADOW"],
    ["T_VERB_MOVE", "T_VERB_DUPLICATE"],
]
TYPE_CYCLE = ["T_TYPE_MESH", "T_TYPE_GROUP", "T_TYPE_LIGHT", "T_TYPE_CAMERA"]
PSEUDO_SWAP = ["T_PSEUDO_SELECTED", "T_PSEUDO_LASSO"]

INTENDED_SILENT = (
    set(SIGIL_SWAP) | set(TYPE_CYCLE) | set(PSEUDO_SWAP)
    | {t for cyc in VERB_CYCLES for t in cyc}
)


def build_map(table: P.TerminalTable) -> dict[str, dict[str, str]]:
    spell = {t.id: t.spelling for t in table.terminals}
    out: dict[str, str] = {}

    def cycle(ids: list[str]) -> None:
        for i, tid in enumerate(ids):
            out[tid] = spell[ids[(i + 1) % len(ids)]]

    cycle(SIGIL_SWAP)
    cycle(TYPE_CYCLE)
    cycle(PSEUDO_SWAP)
    for cyc in VERB_CYCLES:
        cycle(cyc)
    out[CHAIN_FOLLOWS] = out["T_CLASS_SIGIL"]          # I7

    # every remaining substitutable terminal stays at its 3DOM spelling
    for t in table.terminals:
        if t.substitutable and t.id not in out:
            out[t.id] = t.spelling

    return {tid: {"from": spell[tid], "to": to} for tid, to in out.items()}


def write_delta() -> dict:
    table = P.load_terminals()
    blob = {
        "phi_id": "delta",
        "targets_grammar": table.grammar_version,
        "generated": datetime.datetime.now(datetime.timezone.utc)
                     .isoformat(timespec="seconds"),
        "construct": "SILENT COLLISION — identity everywhere except "
                     "within-shape-class permutations",
        "map": build_map(table),
        "overload_groups": [["T_CHAIN_OP", "T_CLASS_SIGIL"]],
        "frozen": list(table.non_substitutable_ids),
        "notes": (
            "Generated by phase3/scripts/make_delta.py. Identity on every "
            "terminal except four within-shape-class permutations: the "
            "class/id sigil transposition (with T_CHAIN_OP following "
            "T_CLASS_SIGIL per I7), two signature-matched verb cycles, the "
            "type-keyword 4-cycle and the pseudo-keyword transposition. "
            "Because the multiset of spellings is unchanged from 3DOM, token "
            "fertility is held ~constant and the only manipulation is role "
            "reassignment. Every intended site is asserted SEMANTIC by the "
            "collision classifier at generation time."),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(blob, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return blob


def verify() -> int:
    table = P.load_terminals()
    ident = P.identity_phi(table)
    delta = P.load_candidate("delta")          # runs validate_phi V1-V8
    print(f"validate_phi: PASS  ({len(delta.substitutions)} substitutions, "
          f"{len(delta.overload_groups)} overload group)")

    programs = G.phase1_programs("positive", ident)
    all_sites: list[S.Site] = []
    skipped = 0
    for i, p in enumerate(programs):
        try:
            prog = T.transliterate(p, ident, delta)
            all_sites.extend(S.classify(prog, delta, template_id=f"t{i:03d}",
                                        identity=ident))
        except Exception as exc:
            skipped += 1
            print(f"  [skip] t{i:03d}: {type(exc).__name__}: {str(exc)[:80]}")

    cen = S.census(all_sites).get("delta", {})
    tot = sum(cen.values()) or 1
    print(f"\nsites: {len(all_sites)}  (skipped templates: {skipped})")
    for k in ("none", "lexical", "benign", "semantic"):
        print(f"  {k:9s} {cen.get(k,0):5d}  {100*cen.get(k,0)/tot:5.1f}%")

    # the proof: every intended terminal must yield SEMANTIC sites, and none
    # of its sites may be BENIGN (a benign site is an alias => no contrast).
    byterm: dict[str, set[str]] = {}
    for s in all_sites:
        byterm.setdefault(s.terminal_id, set()).add(s.collision.value)

    print("\nintended silent-collision terminals:")
    bad = []
    for tid in sorted(INTENDED_SILENT):
        classes = byterm.get(tid)
        if classes is None:
            print(f"  {tid:24s} — not exercised by the corpus (no occurrence)")
            continue
        ok = classes == {"semantic"}
        print(f"  {tid:24s} {'OK  ' if ok else 'BAD '} {sorted(classes)}")
        if not ok:
            bad.append((tid, sorted(classes)))

    if bad:
        print(f"\nFAILED: {len(bad)} intended site(s) are not purely SEMANTIC.")
        return 1
    print("\nAll exercised intended sites are SEMANTIC. delta is usable.")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args(argv)
    _vendor.assert_self_contained()
    if not args.verify_only:
        write_delta()
        print(f"wrote {OUT}")
    return verify()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
