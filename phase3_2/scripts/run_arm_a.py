"""run_arm_a.py — balanced Arm A with a real rule table, a control, and a
full per-site flight recorder.

    python3 scripts/run_arm_a.py --fertility-only
    python3 scripts/run_arm_a.py --models Qwen/Qwen2.5-Coder-0.5B --json out.json

Supersedes the first Phase 3.2 runner, which carried three defects:

  P32-002  the "rule" prompt contained no token table, so the remote
           specification carried zero mapping information and the run measured
           raw prior preference rather than rule-override. Fixed: the table is
           rendered from the phi-map, and a length-matched `norule` control is
           scored alongside it.
  P32-003  `out[:limit]` over a family-concatenated list scored 240 `dom`
           sites and zero `blk` sites while reporting both. Fixed:
           `sampling.balanced` round-robins across (family, lexicon, stratum),
           and `assert_balanced` fails loudly if a family is missing.
  P32-004  only aggregates were written, so nothing could be re-analysed and
           the family split could not be recovered. Fixed: every margin is
           saved with its full provenance.

Arm A is forward-only: two short scoring calls per (site, condition). No
generation, no sampling, no gradients.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from phase3_2 import _vendor  # noqa: E402

import phi as P  # noqa: E402

from phase3_2 import deltafam, prompts, sampling, sites2 as S, templates as TM  # noqa: E402
from phase3_2.backends import BACKENDS  # noqa: E402
from phase3_2.margins import TokenScorer, divergent_margin  # noqa: E402

DEFAULT_MODELS = ("Qwen/Qwen2.5-Coder-0.5B", "Qwen/Qwen2.5-Coder-0.5B-Instruct")


def collect_sites(lexicons, families):
    """Every usable site. Selection happens later, in sampling.balanced."""
    ident = P.identity_phi()
    temps = TM.build_templates()
    out = []
    for fam in families:
        backend = BACKENDS[fam]
        for pid in lexicons:
            lex = P.load_candidate(pid)
            for t in temps:
                try:
                    text = backend.render(t.ir, lex)
                    out += [s for s in S.classify(text, lex, backend,
                                                  template_id=t.template_id,
                                                  identity=ident) if s.is_usable]
                except Exception:
                    continue
    return out


def fertility(model_id, lexicons):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id)
    ident = P.identity_phi()
    temps = TM.build_templates()
    out = {}
    for fam, backend in BACKENDS.items():
        base = [backend.render(t.ir, ident) for t in temps]
        btok = sum(len(tok(x, add_special_tokens=False)["input_ids"]) for x in base)
        bchr = sum(len(x) for x in base)
        for pid in ["identity"] + list(lexicons):
            lex = ident if pid == "identity" else P.load_candidate(pid)
            txt = [backend.render(t.ir, lex) for t in temps]
            n = sum(len(tok(x, add_special_tokens=False)["input_ids"]) for x in txt)
            c = sum(len(x) for x in txt)
            out[f"{fam}/{pid}"] = {
                "tokens": n, "chars": c, "tok_per_char": n / c,
                "rel_fertility_vs_identity": (n / c) / (btok / bchr)}
    return out


def summarise(rows):
    if not rows:
        return None
    return {"n": len(rows),
            "mean_m_seq": statistics.mean(r["m_seq"] for r in rows),
            "median_m_seq": statistics.median(r["m_seq"] for r in rows),
            "reversion_rate": sum(r["m_seq"] < 0 for r in rows) / len(rows),
            "n_merged": sum(r["merged"] for r in rows),
            "n_exact_zero": sum(r["m_seq"] == 0.0 for r in rows)}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=list(DEFAULT_MODELS))
    ap.add_argument("--lexicons", nargs="*", default=["d50s1"])
    ap.add_argument("--families", nargs="*", default=["dom", "blk"])
    ap.add_argument("--limit", type=int, default=0, help="0 = every site")
    ap.add_argument("--conditions", nargs="*", default=["rule", "norule"])
    ap.add_argument("--fertility-only", action="store_true")
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    _vendor.assert_self_contained()
    _vendor.assert_scorer_repaired()

    for d, s in ((0.25, 1), (0.50, 1), (0.75, 1)):
        blob, mem = deltafam.build(d, s, mode="strict" if d <= 0.5 else "arity")
        if mem.phi_id in args.lexicons and not os.path.exists(
                os.path.join(_vendor.CANDIDATES, f"phi_{mem.phi_id}.json")):
            deltafam.write(blob)

    print("=== token fertility (real tokenizer) ===")
    fert = fertility(args.models[0], args.lexicons)
    for k, v in fert.items():
        print(f"  {k:22s} tok/char {v['tok_per_char']:.4f}   "
              f"rel {v['rel_fertility_vs_identity']:.4f}")
    if args.fertility_only:
        return 0

    pool = collect_sites(args.lexicons, args.families)
    sites = sampling.balanced(pool, args.limit)
    sampling.assert_balanced(sites, families=args.families)
    counts = sampling.cell_counts(sites)

    print(f"\n=== balanced sample: {counts['n']} sites ===")
    print(f"  by family : {counts['by_family']}")
    print(f"  by stratum: {counts['by_stratum']}")

    lex0 = P.load_candidate(args.lexicons[0])
    pdesc = prompts.describe(lex0)
    print(f"  prompts   : rule {pdesc['rule_chars']} chars / "
          f"norule {pdesc['norule_chars']} chars over {pdesc['n_roles']} roles")

    results = {
        "fertility": fert,
        "sample": counts,
        "prompts": pdesc,
        "env": {"python": platform.python_version(),
                "platform": platform.platform(),
                "dtype": os.environ.get("PHASE3_DTYPE", "float16"),
                "device": os.environ.get("PHASE3_DEVICE", "cuda")},
        "rows": [],
        "summary": {},
    }

    for mid in args.models:
        t0 = time.time()
        scorer = TokenScorer(mid, device=results["env"]["device"],
                             dtype=results["env"]["dtype"])
        for cond in args.conditions:
            rule = prompts.CONDITIONS[cond](lex0) if cond == "rule" else \
                prompts.CONDITIONS[cond](lex0)
            for s in sites:
                m = divergent_margin(scorer, s, rule=rule)
                results["rows"].append({
                    "model": mid, "condition": cond, "site_id": s.site_id,
                    "family": sampling.family_of(s), "lexicon": s.phi_id,
                    "template": s.template_id, "terminal": s.terminal_id,
                    "role": s.role, "stratum": S.stratum(s),
                    "correct": s.correct, "competitor": s.competitor,
                    "m_seq": m.m_seq, "logp_correct": m.logp_correct,
                    "logp_competitor": m.logp_competitor,
                    "k_common": m.k_common, "merged": m.merged,
                    "n_tok_correct": m.n_tok_correct,
                    "n_tok_competitor": m.n_tok_competitor,
                    "char_offset": s.char_offset,
                })
        print(f"\n--- {mid}  ({time.time()-t0:.0f}s) ---")

        rows = [r for r in results["rows"] if r["model"] == mid]
        # ---- family x stratum, per condition; NEVER pooled across families
        for cond in args.conditions:
            cr = [r for r in rows if r["condition"] == cond]
            print(f"  [{cond}]  {'family':6s} {'stratum':9s} {'n':>5s} "
                  f"{'mean':>8s} {'median':>8s} {'revert':>7s} {'merged':>7s}")
            for fam in sorted({r["family"] for r in cr}):
                fr = [r for r in cr if r["family"] == fam]
                a = summarise(fr)
                print(f"           {fam:6s} {'ALL':9s} {a['n']:5d} "
                      f"{a['mean_m_seq']:8.3f} {a['median_m_seq']:8.3f} "
                      f"{a['reversion_rate']:7.3f} {a['n_merged']:7d}")
                for st in sorted({r["stratum"] for r in fr}):
                    b = summarise([r for r in fr if r["stratum"] == st])
                    print(f"           {'':6s} {st:9s} {b['n']:5d} "
                          f"{b['mean_m_seq']:8.3f} {b['median_m_seq']:8.3f} "
                          f"{b['reversion_rate']:7.3f} {b['n_merged']:7d}")

        # ---- the rule effect: how much did the supplied table move things?
        if set(args.conditions) >= {"rule", "norule"}:
            idx = defaultdict(dict)
            for r in rows:
                idx[r["site_id"]][r["condition"]] = r["m_seq"]
            paired = [(v["rule"] - v["norule"], sid) for sid, v in idx.items()
                      if "rule" in v and "norule" in v]
            fam_of = {r["site_id"]: r["family"] for r in rows}
            print(f"\n  rule effect = M_seq(rule) - M_seq(norule); "
                  f"positive = the table helped")
            for fam in sorted({f for f in fam_of.values()}):
                d = [x for x, sid in paired if fam_of[sid] == fam]
                if d:
                    print(f"           {fam:6s} n={len(d):4d}  "
                          f"mean {statistics.mean(d):+.3f}  "
                          f"median {statistics.median(d):+.3f}  "
                          f"helped {sum(x > 0 for x in d)/len(d):.3f}")

        # ---- exact-zero inspection
        zeros = [r for r in rows if r["m_seq"] == 0.0]
        print(f"\n  exact-zero margins: {len(zeros)}")
        for r in zeros[:5]:
            print(f"    {r['site_id']} [{r['condition']}] k={r['k_common']} "
                  f"ntok {r['n_tok_correct']}/{r['n_tok_competitor']} "
                  f"merged={r['merged']} {r['correct']!r} vs {r['competitor']!r}")

        results["summary"][mid] = {
            f"{c}/{f}/{st}": summarise(
                [r for r in rows if r["condition"] == c and r["family"] == f
                 and r["stratum"] == st])
            for c in args.conditions
            for f in sorted({r["family"] for r in rows})
            for st in sorted({r["stratum"] for r in rows})
        }

    print("\nM_seq < 0 => the model prefers the FAMILIAR competitor (reversion).")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=1)
        print(f"wrote {args.json}  ({len(results['rows'])} per-site rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
