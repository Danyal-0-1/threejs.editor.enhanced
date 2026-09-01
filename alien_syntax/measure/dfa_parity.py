"""dfa_parity.py — DFA branching parity between 3DOM and each candidate.

    python3 measure/dfa_parity.py              # all candidates
    python3 measure/dfa_parity.py beta --md

These are INVARIANT rows in METRICS.md. Any deviation is reported as a FAILURE,
not a footnote.

WHAT IS ACTUALLY BEING TESTED
    The language is regular (non-self-embedding), so an exact DFA over the DSL
    token alphabet exists; Phase 1 exhibits it (refgrammar.build_dfa, 52 states).
    Because the token TYPES are role names rather than spellings, 3DOM and its
    φ-image are recognised by the SAME automaton — so comparing the two DFAs is
    trivially equal and would be a vacuous test on its own.

    The test that is not vacuous is whether each language's LEXER actually
    delivers that automaton the same input. A φ-map that accidentally merged two
    roles into one spelling, or split a maximal-munch run, would leave the DFA
    untouched while changing the token stream — and the decoder's branching
    profile with it. So this script measures four things:

      P1  token-alphabet parity   the set of token types the lexer can emit
      P2  token-stream parity     per parallel corpus item, the exact stream
      P3  branching factor        mean and max over reachable DFA states
      P4  positional profile      mean branching by token index, over the corpus

    TOLERANCE: 0.000, exactly. These are not noisy measurements — the streams are
    either identical or φ broke something — so any nonzero difference is a
    failure. The tolerance is stated here rather than chosen after seeing the
    numbers.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))

from phi import PhiMap, identity_phi, load_candidate  # noqa: E402
from transpiler import lex  # noqa: E402
import generate_corpus as G  # noqa: E402
import refgrammar as R  # noqa: E402

TOLERANCE = 0.0        # pre-committed, stated before any number was produced


def branching_stats() -> dict[str, float]:
    d = R.dfa()
    live = [len(d["trans"].get(s, {})) for s in range(d["nstates"])
            if d["trans"].get(s)]
    return {"states": float(d["nstates"]),
            "mean_branching": sum(live) / len(live),
            "max_branching": float(max(live))}


def positional_profile(programs: list[str], phi: PhiMap) -> list[float]:
    d = R.dfa()
    by_pos: dict[int, list[int]] = {}
    for src in programs:
        try:
            tokens = lex(src, phi)
        except Exception:
            continue
        st = d["start"]
        for idx, (tt, _v, _p) in enumerate(tokens):
            by_pos.setdefault(idx, []).append(len(d["trans"].get(st, {})))
            nxt = d["trans"].get(st, {}).get(tt)
            if nxt is None:
                break
            st = nxt
    return [sum(by_pos[i]) / len(by_pos[i]) for i in sorted(by_pos)]


def alphabet(programs: list[str], phi: PhiMap) -> set[str]:
    out: set[str] = set()
    for src in programs:
        try:
            out |= {t[0] for t in lex(src, phi)}
        except Exception:
            continue
    return out


def compare(phi: PhiMap) -> dict[str, object]:
    ident = identity_phi(phi.table)
    base = G.phase1_programs("positive", ident)
    alien = G.generate(phi, write=False)["positive"]

    fails: list[str] = []

    # P1 — token-alphabet parity
    a_base, a_alien = alphabet(base, ident), alphabet(alien, phi)
    if a_base != a_alien:
        fails.append(f"P1 token alphabet differs: only-3DOM={sorted(a_base - a_alien)}, "
                     f"only-alien={sorted(a_alien - a_base)}")

    # P2 — token-stream parity, item by item
    mismatches = 0
    first = ""
    for b, a in zip(base, alien):
        tb = [t[0] for t in lex(b, ident)]
        ta = [t[0] for t in lex(a, phi)]
        if tb != ta:
            mismatches += 1
            first = first or f"{b[:50]!r}"
    if mismatches:
        fails.append(f"P2 {mismatches} item(s) have different token streams, "
                     f"first {first}")

    # P3 — branching factor over the shared automaton
    stats = branching_stats()

    # P4 — positional profile
    p_base = positional_profile(base, ident)
    p_alien = positional_profile(alien, phi)
    if len(p_base) != len(p_alien):
        fails.append(f"P4 profile length differs: {len(p_base)} vs {len(p_alien)}")
    else:
        worst = max((abs(x - y) for x, y in zip(p_base, p_alien)), default=0.0)
        if worst > TOLERANCE:
            fails.append(f"P4 positional branching differs by {worst:.4f} "
                         f"(tolerance {TOLERANCE:.3f})")

    return {"phi_id": phi.phi_id, "stats": stats, "profile": p_alien,
            "profile_base": p_base, "fails": fails,
            "tokens_per_program": sum(len(lex(a, phi)) for a in alien) / len(alien)}


def main(argv: list[str]) -> int:
    names = [a for a in argv[1:] if not a.startswith("-")] or \
        ["identity", "alpha", "beta", "gamma"]
    as_md = "--md" in argv
    results = [compare(load_candidate(n)) for n in names]
    base = next((r for r in results if r["phi_id"] == "identity"), results[0])

    if as_md:
        print("| lexicon | DFA states | mean branching | max branching | "
              "mean DSL tokens/program | parity |")
        print("|---|---|---|---|---|---|")
        for r in results:
            s = r["stats"]
            verdict = "**PASS**" if not r["fails"] else f"**FAIL** ({len(r['fails'])})"
            print(f"| `{r['phi_id']}` | {int(s['states'])} | "
                  f"{s['mean_branching']:.3f} | {int(s['max_branching'])} | "
                  f"{r['tokens_per_program']:.2f} | {verdict} |")
        print()
        print("Positional branching profile (mean legal next-tokens by DSL token "
              "index), first 16 positions — identical across lexicons by "
              "construction, and asserted so:")
        print()
        print("| token idx | " + " | ".join(f"`{r['phi_id']}`" for r in results) + " |")
        print("|---" * (len(results) + 1) + "|")
        for i in range(min(16, min(len(r["profile"]) for r in results))):
            print(f"| {i} | " + " | ".join(f"{r['profile'][i]:.2f}" for r in results)
                  + " |")
        return 1 if any(r["fails"] for r in results) else 0

    status = 0
    for r in results:
        s = r["stats"]
        print(f"\nφ = {r['phi_id']}")
        print(f"  P3 DFA states {int(s['states'])}, mean branching "
              f"{s['mean_branching']:.3f}, max {int(s['max_branching'])}")
        print(f"     mean DSL tokens per positive program: "
              f"{r['tokens_per_program']:.2f}")
        if r["fails"]:
            status = 1
            print(f"  PARITY FAIL ({len(r['fails'])}):")
            for f in r["fails"]:
                print(f"    - {f}")
        else:
            print(f"  P1/P2/P4 PARITY PASS (tolerance {TOLERANCE:.3f})")
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
