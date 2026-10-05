"""run_primary.py — the PRIMARY estimand (extinction curves) + paraphrase
robustness, both on real weights.

    python3 scripts/run_primary.py --models Qwen/Qwen2.5-Coder-0.5B \
        --sites 120 --json outputs/primary.json

Two things that had never been run on a real model:

  EXTINCTION CURVES -- `k*`, the number of in-context examples at which
  `M_seq` crosses zero. This is the DECLARED PRIMARY ESTIMAND of the whole
  programme (see `phase3/phase3_explained/02 section 6`) and until now it
  existed only as code exercised by a fake model. A threshold on the x-axis is
  far more robust to monotone rescaling of the y-axis than a
  difference-of-differences, which is why it is primary.

  PARAPHRASE ROBUSTNESS -- every number so far rests on ONE rule phrasing.
  Three framings carry the identical rendered table. If the effect moves
  materially across them, the finding is about the wording.

Censoring is reported, never dropped: a curve still negative at the top rung
has `k_star = None`, and discarding those would bias `k*` downward exactly
where the prior is strongest.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics as st
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from phase3_2 import _vendor  # noqa: E402

import phi as P  # noqa: E402

from phase3_2 import prompts, sampling, sites2 as S, templates as TM  # noqa: E402
from phase3_2.backends import BACKENDS  # noqa: E402
from phase3_2.margins import TokenScorer, divergent_margin  # noqa: E402

LADDER = (0, 1, 2, 4, 8, 16, 32)


def collect(lexicons, families):
    ident = P.identity_phi()
    temps = TM.build_templates()
    out = []
    for fam in families:
        be = BACKENDS[fam]
        for pid in lexicons:
            lex = P.load_candidate(pid)
            for t in temps:
                try:
                    out += [s for s in S.classify(be.render(t.ir, lex), lex, be,
                                                  template_id=t.template_id,
                                                  identity=ident) if s.is_usable]
                except Exception:
                    continue
    return out


def interpolate(xs, ys):
    """First upward zero crossing, interpolated in x. None => censored."""
    for i in range(1, len(xs)):
        y0, y1 = ys[i - 1], ys[i]
        if y0 < 0.0 <= y1:
            if y1 == y0:
                return float(xs[i])
            t = (0.0 - y0) / (y1 - y0)
            return float(xs[i - 1]) + t * (xs[i] - xs[i - 1])
    return None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=["Qwen/Qwen2.5-Coder-0.5B"])
    ap.add_argument("--lexicons", nargs="*", default=["d50s1"])
    ap.add_argument("--families", nargs="*", default=["dom", "blk"])
    ap.add_argument("--sites", type=int, default=120)
    ap.add_argument("--skip-paraphrase", action="store_true")
    ap.add_argument("--skip-extinction", action="store_true")
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    _vendor.assert_self_contained()
    _vendor.assert_scorer_repaired()

    lex = P.load_candidate(args.lexicons[0])
    temps = TM.build_templates()
    pool = collect(args.lexicons, args.families)
    sites = sampling.balanced(pool, args.sites)
    sampling.assert_balanced(sites, families=args.families)
    counts = sampling.cell_counts(sites)
    print(f"sites: {counts['n']}  {counts['by_family']}  {counts['by_stratum']}")

    out = {"sample": counts, "ladder": list(LADDER),
           "env": {"python": platform.python_version(),
                   "platform": platform.platform(),
                   "dtype": os.environ.get("PHASE3_DTYPE", "float16")},
           "paraphrase": [], "extinction": []}

    for mid in args.models:
        scorer = TokenScorer(mid, dtype=out["env"]["dtype"])

        # ---- paraphrase robustness -------------------------------------
        if not args.skip_paraphrase:
            print(f"\n=== paraphrase robustness: {mid} ===")
            print(f"  {'variant':8s} {'family':6s} {'n':>4s} {'mean':>8s} "
                  f"{'median':>8s} {'revert':>7s}")
            for which in prompts.PARAPHRASES:
                rule = prompts.paraphrase(lex, which)
                for fam in sorted({sampling.family_of(s) for s in sites}):
                    rows = []
                    for s in [x for x in sites if sampling.family_of(x) == fam]:
                        m = divergent_margin(scorer, s, rule=rule)
                        rows.append(m.m_seq)
                        out["paraphrase"].append(
                            {"model": mid, "variant": which, "family": fam,
                             "site_id": s.site_id, "stratum": S.stratum(s),
                             "template": s.template_id, "lexicon": s.phi_id,
                             "m_seq": m.m_seq, "merged": m.merged,
                             "k_common": m.k_common})
                    print(f"  {which:8s} {fam:6s} {len(rows):4d} "
                          f"{st.mean(rows):+8.3f} {st.median(rows):+8.3f} "
                          f"{sum(x < 0 for x in rows)/len(rows):7.3f}")

        # ---- extinction curves -----------------------------------------
        if not args.skip_extinction:
            print(f"\n=== extinction curves (PRIMARY estimand): {mid} ===")
            rule = prompts.rule_prompt(lex)
            t0 = time.time()
            for fam in sorted({sampling.family_of(s) for s in sites}):
                be = BACKENDS[fam]
                ex = prompts.examples_for(lex, be, temps, max(LADDER))
                ks, cens = [], 0
                for s in [x for x in sites if sampling.family_of(x) == fam]:
                    ys = [divergent_margin(scorer, s, rule=rule, shots=k,
                                           examples=ex).m_seq for k in LADDER]
                    k_star = interpolate(LADDER, ys)
                    if k_star is None and ys[-1] < 0:
                        cens += 1
                    if k_star is not None:
                        ks.append(k_star)
                    out["extinction"].append(
                        {"model": mid, "family": fam, "site_id": s.site_id,
                         "stratum": S.stratum(s), "template": s.template_id,
                         "margins": ys, "k_star": k_star,
                         "censored": ys[-1] < 0})
                n = len([x for x in sites if sampling.family_of(x) == fam])
                already = sum(1 for r in out["extinction"]
                              if r["family"] == fam and r["model"] == mid
                              and r["margins"][0] >= 0)
                print(f"  {fam}: n={n}  already-correct at 0 shots={already}  "
                      f"crossed={len(ks)}  censored(still negative at "
                      f"{max(LADDER)})={cens}")
                if ks:
                    print(f"        k* median={st.median(ks):.2f} "
                          f"mean={st.mean(ks):.2f}")
            print(f"  ({time.time()-t0:.0f}s)")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)
        print(f"\nwrote {args.json}  "
              f"({len(out['paraphrase'])} paraphrase rows, "
              f"{len(out['extinction'])} curves)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
