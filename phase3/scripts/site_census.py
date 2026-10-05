"""site_census.py — enumerate every decision site in every lexicon and report
how many are SILENT (usable) versus LOUD (not usable).

    python3 scripts/site_census.py            # table to stdout
    python3 scripts/site_census.py --json out.json

This is the first thing to run in Phase 3 and the first thing to read. It
answers, with no model and no GPU, the question the literature review says the
whole design rests on:

    at how many sites are the correct and familiar-incorrect spellings BOTH
    grammar-valid while lowering to DIFFERENT canonical IRs?

A lexicon with zero SEMANTIC sites cannot support the primary contrast,
whatever its NLL distance from pretraining.
"""

from __future__ import annotations

import argparse
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

LEXICONS = ("alpha", "beta", "gamma")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None, help="also write the full site list here")
    ap.add_argument("--limit", type=int, default=0, help="cap templates (debug)")
    args = ap.parse_args(argv)

    _vendor.assert_self_contained()
    ident = P.identity_phi()
    programs = G.phase1_programs("positive", ident)
    if args.limit:
        programs = programs[: args.limit]

    all_sites: list[S.Site] = []
    per_lang_errors: dict[str, int] = {}

    for name in LEXICONS:
        lex = P.load_candidate(name)
        errs = 0
        for i, p3dom in enumerate(programs):
            try:
                prog = T.transliterate(p3dom, ident, lex)
                all_sites.extend(S.classify(prog, lex, template_id=f"t{i:03d}",
                                            identity=ident))
            except Exception as exc:
                errs += 1
                print(f"  [skip] {name} t{i:03d}: {type(exc).__name__}: "
                      f"{str(exc)[:90]}", file=sys.stderr)
        per_lang_errors[name] = errs

    # ---- headline table ---------------------------------------------------
    cen = S.census(all_sites)
    print(f"\nPrograms per lexicon: {len(programs)}      "
          f"Total sites classified: {len(all_sites)}\n")
    print(f"{'lexicon':10s} {'none':>7s} {'lexical':>8s} {'benign':>7s} "
          f"{'SEMANTIC':>9s} {'usable %':>9s} {'skipped':>8s}")
    print("-" * 64)
    for name in LEXICONS:
        row = cen.get(name, {})
        tot = sum(row.values()) or 1
        sem = row.get("semantic", 0)
        print(f"{name:10s} {row.get('none',0):7d} {row.get('lexical',0):8d} "
              f"{row.get('benign',0):7d} {sem:9d} {100*sem/tot:8.1f}% "
              f"{per_lang_errors[name]:8d}")

    # ---- which ROLES yield silent collisions? -----------------------------
    print("\nBy terminal role (SEMANTIC sites only — the usable ones):\n")
    byrole: dict[tuple[str, str], int] = {}
    for s in all_sites:
        if s.is_usable:
            byrole[(s.phi_id, s.terminal_id)] = byrole.get((s.phi_id, s.terminal_id), 0) + 1
    if not byrole:
        print("  *** NONE. No lexicon produces a silent semantic collision. ***")
        print("  The familiar spelling always fails to parse instead, so every")
        print("  reversion is a LOUD error. The primary contrast as specified in")
        print("  the literature review is NOT constructible with these lexicons.")
    else:
        for (lang, tid), n in sorted(byrole.items(), key=lambda kv: -kv[1]):
            print(f"  {lang:8s} {tid:22s} {n:4d}")

    # ---- why the loud ones are loud ---------------------------------------
    print("\nLEXICAL (loud) sites by terminal — these are NOT usable for the "
          "primary contrast:\n")
    byloud: dict[tuple[str, str], int] = {}
    for s in all_sites:
        if s.collision is S.CollisionClass.LEXICAL:
            byloud[(s.phi_id, s.terminal_id)] = byloud.get((s.phi_id, s.terminal_id), 0) + 1
    for (lang, tid), n in sorted(byloud.items(), key=lambda kv: -kv[1])[:12]:
        print(f"  {lang:8s} {tid:22s} {n:4d}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump([S.to_dict(s) for s in all_sites], fh, indent=1)
        print(f"\nwrote {args.json} ({len(all_sites)} sites)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
