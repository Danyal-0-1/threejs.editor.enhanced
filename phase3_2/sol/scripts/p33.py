#!/usr/bin/env python3
"""p33.py — the one command-line entry point for the Phase 3.3 pipeline.

STAGE GROUPS ARE PHYSICALLY SEPARATE. `dev ...` refuses a run directory whose
stored stage is not dev, `heldout ...` refuses one that is not heldout, and
run ids must start with their stage (`dev-`, `heldout-`, `smoke-`), so the two
can never share an output root.

  # shared
  p33.py env-check
  p33.py prefetch [--config CFG.json ...|--models ...|--tier small|mid|large|all]
                  [--dry-run|--verify-only] [--checksums] [--repin]
  p33.py status   --run RUN
  p33.py merge    --run RUN [--experiment arm_a|primary|armb|h5]
  p33.py validate --run RUN            # exit 3 if any expected cell is not done
  p33.py export   --run RUN            # CSVs -> plots -> reports (no model)

  # development
  p33.py dev init      --config CONFIG.json --run dev-...
  p33.py dev preflight --run dev-... [--no-gpu]
  p33.py dev run       --run dev-... --experiment arm_a|primary|armb|h5 [--task N --n-tasks M]
  p33.py dev fertility --run dev-...
  p33.py dev analyze   --run dev-...  # merge everything, export, power, plots, reports
  p33.py dev freeze    --run dev-...  # writes the immutable DEV_FREEZE.json

  # held-out (locked until unlock)
  p33.py heldout init    --config CONFIG.json --run heldout-... --freeze .../DEV_FREEZE.json
  p33.py heldout unlock  --run heldout-... --confirm "<exact phrase>"
  p33.py heldout run     --run heldout-... --experiment ...
  p33.py heldout analyze --run heldout-...

  # smoke (one model, one dev lexicon, one family)
  p33.py smoke --config CONFIG.json --run smoke-... [--allow-non-a100]

Environment: P33_RESULTS_ROOT, P33_HF_ROOT, P33_FAKE=1 (CPU fake scorer for tests).
Exit codes: 0 complete · 2 preflight/split refusal · 3 partial/incomplete ·
4 interrupted (resume with the same command) · 1 error.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import p33  # noqa: E402,F401
from p33 import config as CFG  # noqa: E402
from p33 import export, pipeline as PL, shards, splits  # noqa: E402
# plots/reports import matplotlib; loaded lazily so a scoring job never needs it
from p33 import armb, h5  # noqa: E402,F401  (register experiments)

EXIT = {"COMPLETE": 0, "PARTIAL": 3, "INTERRUPTED": 4, "EMPTY": 3}


def run_dir_of(run_id: str) -> str:
    return CFG.run_dir(run_id)


def load_cfg(run_id: str, *, stage: str | None = None) -> CFG.RunConfig:
    p = os.path.join(run_dir_of(run_id), "manifests", "run_config.json")
    if not os.path.exists(p):
        sys.exit(f"no run {run_id!r} under {CFG.results_root()} -- run `init` first")
    cfg = CFG.RunConfig.from_dict(json.load(open(p))["config"])
    if stage and cfg.stage != stage and not (stage == "dev" and cfg.stage == "smoke"):
        print(f"REFUSED: {run_id} is a {cfg.stage!r} run; the `{stage}` command group "
              f"cannot touch it (development and held-out are physically separated)",
              file=sys.stderr)
        sys.exit(2)                       # the documented refusal code, not a crash
    return cfg


def pins_path(a) -> str:
    return getattr(a, "pins", None) or os.path.join(CFG.results_root(), "model_pins.json")


def load_pins(cfg, a) -> dict:
    if os.environ.get("P33_FAKE") == "1":
        return {m: {"revision": "fakerev0001"} for m in cfg.models}
    from p33.scorers import load_pins as lp
    return lp(pins_path(a))


def scorer_factory(cfg, pins):
    if os.environ.get("P33_FAKE") == "1":
        from p33.fakes import FakeScorer
        return lambda m: FakeScorer(m)
    from p33.scorers import load_scorer
    dev = os.environ.get("P33_DEVICE", "cuda")
    return lambda m: load_scorer(m, dtype=cfg.dtype, device=dev,
                                 lm_head_fp32=cfg.lm_head_fp32, pins=pins)


def task_args(a):
    """Array task i scores model i of the run's config, so `--array=2` resubmits model 2.

    The stride is never read from SLURM_ARRAY_TASK_COUNT (P33-012): resubmitting
    one failed index gives a count of 1, and `i % 1 == 2` selected no model --
    the resubmitted task silently scored nothing.
    """
    task = a.task if a.task is not None else (int(os.environ["SLURM_ARRAY_TASK_ID"])
                                              if "SLURM_ARRAY_TASK_ID" in os.environ else None)
    return task, a.n_tasks


# ---------------------------------------------------------------------------

def cmd_env_check(a):
    from p33 import provenance
    pk = provenance.package_versions()
    need = ["lark", "numpy", "matplotlib", "transformers", "huggingface_hub"]
    missing = [m for m in need if pk.get(m) == "MISSING"]
    print(json.dumps({"packages": pk, "gpu": provenance.gpu_info(),
                      "hf_env": CFG.hf_env(), "results_root": CFG.results_root(),
                      "missing_required": missing}, indent=1, default=str))
    return 2 if missing else 0


def cmd_prefetch(a):
    from p33 import prefetch, registry
    if a.config:       # exactly the models these run configs use (the default job)
        models = sorted({m for p in a.config for m in CFG.RunConfig.load(p).models})
    else:
        models = a.models or registry.tier_models(a.tier)
    res = prefetch.run(models, dry_run=a.dry_run, verify_only_mode=a.verify_only,
                       checksums=a.checksums, out_path=pins_path(a), repin=a.repin)
    slim = {k: v for k, v in res.items() if k not in ("plans",)}
    if "plans" in res:
        slim["plans"] = [{k: p[k] for k in ("model", "revision", "bytes", "allow_patterns")} for p in res["plans"]]
    print(json.dumps(slim, indent=1, default=str))
    return 1 if res.get("failed") else 0


def cmd_init(a, stage):
    cfg = CFG.RunConfig.load(a.config)
    cfg.run_id = a.run
    cfg.stage = stage
    if stage == "heldout":
        cfg.freeze_path = os.path.abspath(a.freeze)
        splits.load_freeze(cfg.freeze_path)
    if getattr(a, "allow_non_a100", False):
        cfg.allow_non_a100 = True
    cfg.validate()
    rd = run_dir_of(cfg.run_id)
    CFG.ensure_run_layout(rd)
    shards.assert_compatible(rd, cfg)
    try:
        splits.enforce_config(cfg, run_dir=rd if stage == "heldout" else None)
    except splits.SplitViolation as exc:
        if stage != "heldout" or "locked" not in str(exc):
            print(f"REFUSED: {exc}")
            return 2
    print(f"initialised {rd} (config {cfg.config_hash()[:12]})")
    return 0


def cmd_preflight(a, stage):
    from p33 import preflight
    cfg = load_cfg(a.run, stage=stage)
    rep = preflight.run(cfg, run_dir_of(a.run), pins=load_pins(cfg, a),
                        require_gpu=not a.no_gpu)
    for c in rep["checks"]:
        print(f"  [{c['result']:4s}] {c['check']:22s} {c['detail']}")
    print(f"preflight {'OK' if rep['ok'] else 'FAILED'} -> {rep['path']}")
    return 0 if rep["ok"] else 2


def cmd_run(a, stage):
    cfg = load_cfg(a.run, stage=stage)
    pins = load_pins(cfg, a)
    rd = run_dir_of(a.run)
    try:
        if a.experiment == "h5":
            h5.prepare(cfg, rd)
        task, n = task_args(a)
        st = PL.run(cfg, rd, a.experiment, scorer_factory=scorer_factory(cfg, pins),
                    pins=pins, task=task, n_tasks=n)
    except splits.SplitViolation as exc:
        print(f"REFUSED: {exc}")
        return 2
    print(f"{a.experiment}: {st}")
    return EXIT.get(st, 1)


def cmd_fertility(a, stage):
    from p33 import fertility
    cfg = load_cfg(a.run, stage=stage)
    splits.enforce_config(cfg, run_dir=run_dir_of(a.run) if cfg.stage == "heldout" else None)
    pins = load_pins(cfg, a)
    if os.environ.get("P33_FAKE") == "1":
        from p33.fakes import FakeScorer
        loader = lambda m: ("fake-tok-v1", lambda t: len(FakeScorer(m).ids(t)))  # noqa: E731
    else:
        loader = lambda m: fertility.load_tokenizer(m, pins)  # noqa: E731
    rows = fertility.compute(cfg.models, cfg.families, cfg.lexicons, tokenizer_loader=loader)
    p = os.path.join(run_dir_of(a.run), "manifests", "fertility.json")
    json.dump(rows, open(p, "w"), indent=1)
    print(f"fertility: {len(rows)} rows across {len({r['tokenizer_id'] for r in rows})} tokenizer(s) -> {p}")
    return 0


def _merge(cfg, rd, pins, exps):
    out = {}
    for e in exps:
        if e == "h5" and not os.path.exists(os.path.join(rd, "manifests", "h5_arms.json")):
            continue
        if not os.path.isdir(os.path.join(rd, "raw", "shards", e)):
            continue
        if e == "h5":
            h5.prepare(cfg, rd)
        res = PL.merge(cfg, rd, e, pins=pins)
        out[e] = res
        print(f"merge {e:8s} {res.status:9s} rows={len(res.rows):6d} done={len(res.done)}/{res.n_expected} "
              f"missing={len(res.missing)} failed={len(res.failed)} corrupt={len(res.corrupt)} "
              f"dup_dropped={res.duplicates_dropped}")
    return out


def cmd_merge(a):
    cfg = load_cfg(a.run)
    exps = [a.experiment] if a.experiment else ["arm_a", "primary", "armb", "h5"]
    res = _merge(cfg, run_dir_of(a.run), load_pins(cfg, a), exps)
    return 0 if all(r.status == "COMPLETE" for r in res.values()) else 3


def cmd_validate(a):
    cfg = load_cfg(a.run)
    rd = run_dir_of(a.run)
    res = _merge(cfg, rd, load_pins(cfg, a), ["arm_a", "primary", "armb", "h5"])
    bad = {e: r.status for e, r in res.items() if r.status != "COMPLETE"}
    print("VALID: every expected cell is done and verified" if not bad
          else f"INCOMPLETE: {bad}")
    return 0 if not bad else 3


def cmd_export(a):
    cfg = load_cfg(a.run)
    rd = run_dir_of(a.run)
    from p33 import plots, reports
    p = export.export_all(rd, cfg)
    pl = plots.make_all(rd, cfg)
    rp = reports.make_all(rd, cfg)
    print(f"export: {len(p)} CSVs, {sum(len(v) for v in pl.values())} plot files, {len(rp)} reports -> {rd}")
    return 0


def cmd_analyze(a, stage):
    cfg = load_cfg(a.run, stage=stage)
    _merge(cfg, run_dir_of(a.run), load_pins(cfg, a), ["arm_a", "primary", "armb", "h5"])
    return cmd_export(a)


def cmd_freeze(a):
    from p33 import freeze
    cfg = load_cfg(a.run, stage="dev")
    try:
        p = freeze.freeze(run_dir_of(a.run), cfg)
    except splits.FreezeError as exc:
        print(f"REFUSED: {exc}")
        return 2
    print(f"FROZEN: {p}\n  sha256 {open(p + '.sha256').read().strip()}")
    return 0


def cmd_unlock(a):
    cfg = load_cfg(a.run, stage="heldout")
    try:
        rec = splits.write_unlock(run_dir_of(a.run), cfg.freeze_path, a.confirm)
    except splits.FreezeError as exc:
        print(f"REFUSED: {exc}")
        return 2
    print(f"UNLOCKED held-out cells for {a.run}: {json.dumps(rec, indent=1)}")
    return 0


def cmd_status(a):
    """Read-only. An experiment counts as started once its shard directory
    exists; constructing a ShardStore here created that directory, so a plain
    `status` turned a never-run Arm B into a started, EMPTY one and made the
    next `validate` -- and with it `dev_freeze` -- refuse (P33-017)."""
    cfg = load_cfg(a.run)
    rd = run_dir_of(a.run)
    pins = load_pins(cfg, a)
    plan = PL.build_plan(cfg, site_limit=cfg.site_limit, run_dir=rd if cfg.stage == "heldout" else None)
    for e in ("arm_a", "primary", "armb", "h5"):
        if not os.path.isdir(os.path.join(rd, "raw", "shards", e)):
            print(f"{e:8s} not started")
            continue
        if e == "h5":
            if not os.path.exists(os.path.join(rd, "manifests", "h5_arms.json")):
                print(f"{e:8s} not started")
                continue
            h5.prepare(cfg, rd)
        store = shards.ShardStore(rd, e)
        keys = PL.expected_keys(cfg, plan, pins, e)
        counts = {}
        for k in keys:
            s = store.status(k).state
            counts[s] = counts.get(s, 0) + 1
        print(f"{e:8s} expected={len(keys):5d} {counts}")
    return 0


def cmd_smoke(a):
    if cmd_init(a, "smoke"):
        return 2
    cfg = load_cfg(a.run)
    pins = load_pins(cfg, a)
    rd = run_dir_of(a.run)
    if os.environ.get("P33_FAKE") != "1":
        from p33 import preflight
        rep = preflight.run(cfg, rd, pins=pins, require_gpu=True)
        for c in rep["checks"]:
            print(f"  [{c['result']:4s}] {c['check']:22s} {c['detail']}")
        if not rep["ok"]:
            return 2
    rc = 0
    for e in ("arm_a", "primary"):
        st = PL.run(cfg, rd, e, scorer_factory=scorer_factory(cfg, pins), pins=pins)
        print(f"smoke {e}: {st}")
        rc = max(rc, EXIT.get(st, 1))
    a.experiment = None
    _merge(cfg, rd, pins, ["arm_a", "primary"])
    rc = max(rc, cmd_fertility(a, "smoke"))    # tokenizer only: the real offline tokenizer path
    cmd_export(a)
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pins", default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("env-check")
    pf = sub.add_parser("prefetch")
    pf.add_argument("--tier", default="small")
    pf.add_argument("--models", nargs="*")
    pf.add_argument("--config", nargs="*", help="prefetch the models these configs use")
    g = pf.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--verify-only", action="store_true")
    pf.add_argument("--checksums", action="store_true")
    pf.add_argument("--repin", action="store_true",
                    help="move already-pinned models to the Hub's current revision "
                         "(never after a freeze: held-out would refuse on pin drift)")
    for name in ("status", "merge", "validate", "export"):
        p = sub.add_parser(name)
        p.add_argument("--run", required=True)
        if name == "merge":
            p.add_argument("--experiment")
    sm = sub.add_parser("smoke")
    sm.add_argument("--config", required=True)
    sm.add_argument("--run", required=True)
    sm.add_argument("--allow-non-a100", action="store_true")

    for stage in ("dev", "heldout"):
        sp = sub.add_parser(stage).add_subparsers(dest="sub", required=True)
        i = sp.add_parser("init")
        i.add_argument("--config", required=True)
        i.add_argument("--run", required=True)
        i.add_argument("--allow-non-a100", action="store_true")
        if stage == "heldout":
            i.add_argument("--freeze", required=True)
        p = sp.add_parser("preflight")
        p.add_argument("--run", required=True)
        p.add_argument("--no-gpu", action="store_true")
        r = sp.add_parser("run")
        r.add_argument("--run", required=True)
        r.add_argument("--experiment", required=True, choices=["arm_a", "primary", "armb", "h5"])
        r.add_argument("--task", type=int)
        r.add_argument("--n-tasks", type=int)
        for name in ("fertility", "analyze"):
            sp.add_parser(name).add_argument("--run", required=True)
        if stage == "dev":
            sp.add_parser("freeze").add_argument("--run", required=True)
        else:
            u = sp.add_parser("unlock")
            u.add_argument("--run", required=True)
            u.add_argument("--confirm", required=True)

    a = ap.parse_args(argv)
    if a.cmd == "env-check":
        return cmd_env_check(a)
    if a.cmd == "prefetch":
        return cmd_prefetch(a)
    if a.cmd in ("status", "merge", "validate", "export"):
        return {"status": cmd_status, "merge": cmd_merge, "validate": cmd_validate,
                "export": cmd_export}[a.cmd](a)
    if a.cmd == "smoke":
        return cmd_smoke(a)
    stage = a.cmd
    if a.sub == "init":
        return cmd_init(a, stage)
    if a.sub == "preflight":
        return cmd_preflight(a, stage)
    if a.sub == "run":
        return cmd_run(a, stage)
    if a.sub == "fertility":
        return cmd_fertility(a, stage)
    if a.sub == "analyze":
        return cmd_analyze(a, stage)
    if a.sub == "freeze":
        return cmd_freeze(a)
    if a.sub == "unlock":
        return cmd_unlock(a)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
