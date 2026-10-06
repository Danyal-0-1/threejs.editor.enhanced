"""run_primary.py — DEPRECATED wrapper over the corrected Phase 3.3 pipeline.

The original runner had three stop-ship defects, fixed in `sol/src/p33`:

  P33-006  one rule table and one example pool from `--lexicons[0]` for all sites
  P33-008  demonstrations = the first 32 templates, so 82 of 120 sites saw
           their own target program (the pre-freeze k* is withdrawn, D3)
  P33-007  k* left already-correct sites as None, took later re-crossings,
           and marked crossed-then-dropped curves as censored

This file now runs `p33.pipeline` with experiment "primary": leakage-free
nested demonstrations, every rung saved, the corrected k* computed at export,
and the development split lock enforced.

    python3 scripts/run_primary.py --lexicons d50s1 --sites 120 --json out.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sol", "src"))

import p33  # noqa: E402,F401
from p33 import config as CFG, pipeline as PL, splits  # noqa: E402


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="*", default=["Qwen/Qwen2.5-Coder-0.5B"])
    ap.add_argument("--lexicons", nargs="*", default=["d50s1"])
    ap.add_argument("--families", nargs="*", default=["dom"])
    ap.add_argument("--sites", type=int, default=120)
    ap.add_argument("--skip-paraphrase", action="store_true")
    ap.add_argument("--json", default=None)
    ap.add_argument("--run", default=None)
    a = ap.parse_args(argv)
    print("NOTE: run_primary.py is a deprecated wrapper over sol/src/p33 (see its docstring).",
          file=sys.stderr)
    cfg = CFG.RunConfig(run_id=a.run or f"dev-legacy-{int(time.time())}", stage="dev",
                        models=a.models, families=a.families, lexicons=a.lexicons)
    cfg.primary["site_limit"] = a.sites
    if a.skip_paraphrase:
        cfg.primary["paraphrases"] = []
    try:
        splits.enforce_config(cfg)
    except splits.SplitViolation as exc:
        print(f"REFUSED: {exc}")
        return 2
    sol = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sol", "scripts", "p33.py")
    import importlib.util
    spec = importlib.util.spec_from_file_location("p33cli", sol)
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    rd = CFG.run_dir(cfg.run_id)
    CFG.ensure_run_layout(rd)
    from p33 import shards
    shards.assert_compatible(rd, cfg)
    pins = cli.load_pins(cfg, argparse.Namespace(pins=None))
    st = PL.run(cfg, rd, "primary", scorer_factory=cli.scorer_factory(cfg, pins), pins=pins)
    res = PL.merge(cfg, rd, "primary", pins=pins)
    print(f"primary: {st}; merged {len(res.rows)} rows -> {rd}/merged/primary.jsonl")
    if a.json:
        json.dump({"status": res.status, "run_dir": rd, "rows": res.rows}, open(a.json, "w"), indent=1)
    return cli.EXIT.get(st, 1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
