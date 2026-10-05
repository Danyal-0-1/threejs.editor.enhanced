"""build_materials.py — build and MEASURE the Phase 3.2 materials.

    python3 scripts/build_materials.py              # build + report
    python3 scripts/build_materials.py --json out.json

Phase 3's blocker was materials, not science: 40 prefix-distinct SEMANTIC
sites in one grammar family. This script builds the replacement and reports
whether the target (>= 300 prefix-distinct semantic sites) was met. It writes
phi files and a site inventory; it runs no model and needs no GPU.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from phase3_2 import _vendor  # noqa: E402

import phi as P  # noqa: E402

from phase3_2 import deltafam, sites2 as S, templates as TM  # noqa: E402
from phase3_2.backends import BACKENDS  # noqa: E402

TARGET = 300


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    ap.add_argument("--target", type=int, default=TARGET)
    args = ap.parse_args(argv)

    _vendor.assert_self_contained()
    _vendor.assert_scorer_repaired()
    table = P.load_terminals()
    ident = P.identity_phi(table)

    # ---- 1. the delta family -------------------------------------------
    print("=== delta family ===")
    members = []
    for blob, mem in deltafam.build_family():
        deltafam.write(blob)
        P.load_candidate(mem.phi_id)                    # runs validate_phi V1-V8
        members.append(mem)
        print(f"  {mem.phi_id:10s} target {mem.density_target:.2f}  "
              f"actual {mem.density_actual:.2f}  mode {mem.mode:6s}  "
              f"{len(mem.permuted):2d} roles permuted")

    # ---- 2. templates ---------------------------------------------------
    print("\n=== templates ===")
    temps = TM.build_templates()
    print(f"  {len(temps)} templates, {sum(t.n_ops for t in temps)} operations")

    # ---- 3. render + classify over family x lexicon ---------------------
    print("\n=== site inventory ===")
    all_sites: list[S.Site] = []
    rows = []
    for fam, backend in BACKENDS.items():
        opened = TM.opening_diversity([backend.render(t.ir, ident) for t in temps])
        for mem in members:
            lex = P.load_candidate(mem.phi_id)
            got: list[S.Site] = []
            skipped = 0
            for t in temps:
                try:
                    text = backend.render(t.ir, lex)
                    got += S.classify(text, lex, backend,
                                      template_id=t.template_id, identity=ident)
                except Exception as exc:
                    skipped += 1
                    if skipped <= 2:
                        print(f"   [skip] {fam}/{mem.phi_id}/{t.template_id}: "
                              f"{type(exc).__name__}: {str(exc)[:60]}", file=sys.stderr)
            sem = S.usable(got)
            ded = S.dedupe_by_prefix(sem)
            all_sites += got
            rows.append((fam, mem.phi_id, len(got), len(sem), len(ded), skipped))
        print(f"  {fam}: {len(opened)} distinct 24-char openings")

    print(f"\n{'family':7s} {'lexicon':10s} {'sites':>7s} {'SEMANTIC':>9s} "
          f"{'prefix-distinct':>16s} {'skipped':>8s}")
    print("-" * 62)
    for fam, pid, n, nsem, nded, sk in rows:
        print(f"{fam:7s} {pid:10s} {n:7d} {nsem:9d} {nded:16d} {sk:8d}")

    # ---- 4. the headline numbers ----------------------------------------
    sem_all = S.usable(all_sites)
    ded_all = S.dedupe_by_prefix(sem_all)
    cols = S.prefix_collisions(sem_all)
    n_in_cols = sum(len(v) for v in cols.values())

    print(f"\n=== headline ===")
    print(f"  total sites classified   : {len(all_sites)}")
    print(f"  SEMANTIC (usable)        : {len(sem_all)}")
    print(f"  colliding prefix groups  : {len(cols)}  "
          f"({n_in_cols} sites, {100*n_in_cols/max(len(sem_all),1):.1f}%)")
    print(f"  PREFIX-DISTINCT SEMANTIC : {len(ded_all)}   "
          f"(Phase 3 had 40; target {args.target})")
    verdict = "MET" if len(ded_all) >= args.target else "NOT MET"
    print(f"  target {args.target}: {verdict}")

    # ---- 5. stratification (the free 3D-knowledge test) ------------------
    print("\n=== strata (sigil = pure surface; verb = surface + 3D domain) ===")
    for name, group in sorted(S.by_stratum(ded_all).items()):
        print(f"  {name:8s} {len(group):5d} prefix-distinct semantic sites")

    # ---- 6. cross-family / cross-lexicon split availability --------------
    fams = {s.site_id.split(":")[0] for s in ded_all}
    lexes = {s.phi_id for s in ded_all}
    print(f"\n  grammar families represented : {sorted(fams)}")
    print(f"  lexicons represented         : {len(lexes)} -> held-out mappings available")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump([S.to_dict(s) for s in all_sites], fh, indent=1)
        print(f"\nwrote {args.json} ({len(all_sites)} sites)")
    return 0 if len(ded_all) >= args.target else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
