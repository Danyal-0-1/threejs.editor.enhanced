"""run_arm_a.py — DEPRECATED wrapper over the corrected Phase 3.3 pipeline.

The original Phase 3.2 runner had four stop-ship defects, fixed in `sol/src/p33`:

  P33-006  rendered ONE rule table, from `--lexicons[0]`, for every site
  P33-003  global first-occurrence de-duplication (CLI-order dependent)
  P33-009  fertility from `--models[0]` only, reported for every model
  P33-010  provenance (`runmeta`) never called; one JSON at the very end

Keeping a second scoring path alive would keep those defects one typo away,
and would be an unguarded route to held-out cells. This file now builds a
development `RunConfig` and runs `p33.pipeline` -- same fixes, same split lock
(a held-out lexicon or model is REFUSED), same crash-safe shards.

    python3 scripts/run_arm_a.py --lexicons d50s1 --families dom --limit 0 --json out.json

For anything beyond a quick check use `sol/scripts/p33.py dev ...`.
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
    ap.add_argument("--models", nargs="*", default=["Qwen/Qwen2.5-Coder-0.5B", "Qwen/Qwen2.5-Coder-0.5B-Instruct"])
    ap.add_argument("--lexicons", nargs="*", default=["d50s1"])
    ap.add_argument("--families", nargs="*", default=["dom"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--conditions", nargs="*", default=["rule", "norule", "norule_lenmatched"])
    ap.add_argument("--fertility-only", action="store_true")
    ap.add_argument("--json", default=None)
    ap.add_argument("--run", default=None, help="run id (default dev-legacy-<timestamp>)")
    a = ap.parse_args(argv)
    print("NOTE: run_arm_a.py is a deprecated wrapper over sol/src/p33 (see its docstring).",
          file=sys.stderr)
    cfg = CFG.RunConfig(run_id=a.run or f"dev-legacy-{int(time.time())}", stage="dev",
                        models=a.models, families=a.families, lexicons=a.lexicons,
                        site_limit=a.limit)
    cfg.arm_a["conditions"] = a.conditions
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
    if a.fertility_only:
        return cli.cmd_fertility(argparse.Namespace(run=cfg.run_id, pins=None), "dev")
    st = PL.run(cfg, rd, "arm_a", scorer_factory=cli.scorer_factory(cfg, pins), pins=pins)
    res = PL.merge(cfg, rd, "arm_a", pins=pins)
    print(f"arm_a: {st}; merged {len(res.rows)} rows -> {rd}/merged/arm_a.jsonl")
    if a.json:
        json.dump({"status": res.status, "run_dir": rd, "rows": res.rows}, open(a.json, "w"), indent=1)
    return cli.EXIT.get(st, 1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
