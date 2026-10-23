#!/usr/bin/env python3
"""compare_with_phase3_3.py — run the Phase 3.3 pipeline and this copy side by side.

    python3 tools/compare_with_phase3_3.py               # the fake-scorer experiment (a few minutes)
    python3 tools/compare_with_phase3_3.py --real-dev    # also re-export the real development run

Each pipeline runs in its own process and its own temporary results root, so the two can never
read each other's files. Then every CSV the two produced is compared byte for byte.

  fake experiment   the same flow as tests/test_e2e.py, with the deterministic fake scorer and
                    two Qwen2.5-Coder-0.5B checkpoints: a development run with all four
                    experiments (Arm A, the extinction ladder, Arm B, H5) and its export; the
                    freeze; the unlock; a held-out run with all four experiments and its export.
  --real-dev        copies phase3_3/sol_results/dev-20261006a (the real development run, scored
                    on Sol) twice and rebuilds its 19 CSVs from the saved measurements, once with
                    each pipeline. No model is loaded.

The copy runs with Phase 3.3's registered design installed (tests/phase3_3_design.py: its split,
its preregistration and its schema label), so both pipelines run the same design, and any
difference comes from the code. Every CSV must then be identical except job_provenance.csv,
which records each job's process id, clock times and GPU state. After a change to the
measurement code, the differences this prints are exactly what that change did to the outputs.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile

CODE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(CODE))
MODELS = ["Qwen/Qwen2.5-Coder-0.5B", "Qwen/Qwen2.5-Coder-0.5B-Instruct"]
REAL_DEV = os.path.join(REPO, "phase3_3", "sol_results", "dev-20261006a")
PROVENANCE_ONLY = {"job_provenance.csv"}       # process id, clock, GPU state: differs by design


def load(tree: str):
    """The modules of one pipeline: 'old' = Phase 3.3 (phase3_2/sol), 'new' = this copy."""
    if tree == "old":
        sys.path.insert(0, os.path.join(REPO, "phase3_2", "sol", "src"))
        import p33  # noqa: F401
        from p33 import config as CFG, export, freeze, h5, pipeline as PL, splits
        from p33 import armb  # noqa: F401  (registers Arm B)
        from p33.fakes import FakeScorer
    else:
        sys.path.insert(0, CODE)
        sys.path.insert(0, os.path.join(CODE, "tests"))
        import p4  # noqa: F401
        import phase3_3_design
        phase3_3_design.install(schema=True)    # the same design as the Phase 3.3 pipeline
        from p4.experiments import armb, h5, pipeline as PL  # noqa: F401
        from p4.governance import freeze, splits
        from p4.reporting import export
        from p4.runtime import config as CFG
        from p4.scoring.fakes import FakeScorer
    return CFG, export, freeze, h5, PL, splits, FakeScorer


def results_env(tree: str) -> str:
    return "P33_RESULTS_ROOT" if tree == "old" else "P4_RESULTS_ROOT"


def drive_fake(tree: str, root: str) -> None:
    os.environ[results_env(tree)] = root
    # The held-out config names its freeze, and that path enters the config hash and with it
    # every cell key. Named relative to the results root, it is the same string for both
    # pipelines, so their configurations are byte-identical.
    os.makedirs(root, exist_ok=True)
    os.chdir(root)
    CFG, export, freeze, h5, PL, splits, FakeScorer = load(tree)
    pins = {m: {"revision": "fakerev0001"} for m in MODELS}

    def cfg_for(run_id, stage, lexicons, site_limit, primary_sites):
        cfg = CFG.RunConfig(run_id=run_id, stage=stage, models=list(MODELS), families=["dom"],
                            lexicons=list(lexicons), site_limit=site_limit, chunk_size=8)
        cfg.primary.update({"site_limit": primary_sites, "ladder": [0, 1, 2, 4, 8]})
        cfg.analysis["B"] = 200
        cfg.armb["template_limit"] = 4
        cfg.schema_version = "p33/1"           # the label is part of the config hash
        return cfg

    def run_all(cfg, rd):
        for exp in ("arm_a", "primary", "armb"):
            PL.run(cfg, rd, exp, scorer_factory=lambda m: FakeScorer(m), pins=pins)
            PL.merge(cfg, rd, exp, pins=pins)
        h5.prepare(cfg, rd)
        PL.run(cfg, rd, "h5", scorer_factory=lambda m: FakeScorer(m), pins=pins)
        PL.merge(cfg, rd, "h5", pins=pins)
        export.export_all(rd, cfg)

    dev = cfg_for("dev-compare", "dev", ("d50s1", "d25s1"), 40, 16)
    drd = CFG.run_dir(dev.run_id)
    run_all(dev, drd)
    fz = os.path.relpath(freeze.freeze(drd, dev), root)
    ho = cfg_for("heldout-compare", "heldout", ("d75s1a",), 20, 8)
    ho.freeze_path = fz
    hrd = CFG.run_dir(ho.run_id)
    splits.write_unlock(hrd, fz, splits.UNLOCK_PHRASE)
    run_all(ho, hrd)


def drive_export(tree: str, root: str, run_id: str) -> None:
    os.environ[results_env(tree)] = root
    CFG, export, *_ = load(tree)
    rd = CFG.run_dir(run_id)
    cfg = CFG.RunConfig.from_dict(json.load(open(os.path.join(rd, "manifests", "run_config.json")))["config"])
    export.export_all(rd, cfg)


def compare(root_old: str, root_new: str) -> tuple[list[str], list[str], list[str]]:
    same, prov, diff = [], [], []
    for dirpath, _dirs, files in os.walk(root_old):
        if os.path.basename(dirpath) != "csv":
            continue
        for f in sorted(files):
            a = os.path.join(dirpath, f)
            rel = os.path.relpath(a, root_old)
            b = os.path.join(root_new, rel)
            if not os.path.exists(b):
                diff.append(f"{rel}: missing in the copy's output")
            elif filecmp.cmp(a, b, shallow=False):
                same.append(rel)
            elif f in PROVENANCE_ONLY:
                prov.append(rel)
            else:
                diff.append(rel)
    return same, prov, diff


def report(title: str, root_old: str, root_new: str) -> bool:
    same, prov, diff = compare(root_old, root_new)
    print(f"\n{title}")
    print(f"  identical:                            {len(same)} CSVs")
    print(f"  different, provenance only by design: {len(prov)} ({', '.join(sorted({os.path.basename(p) for p in prov})) or '-'})")
    print(f"  DIFFERENT:                            {len(diff)}")
    for d in diff:
        print(f"    {d}")
    return not diff and bool(same)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--real-dev", action="store_true", help="also re-export the real development run")
    ap.add_argument("--keep", metavar="DIR", help="keep the outputs under DIR instead of a temporary folder")
    ap.add_argument("--driver", nargs="+", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.driver:                                            # internal: one pipeline, one process
        kind, tree, root, *rest = a.driver
        drive_fake(tree, root) if kind == "fake" else drive_export(tree, root, rest[0])
        return 0
    base = a.keep or tempfile.mkdtemp(prefix="p4_compare_")
    os.makedirs(base, exist_ok=True)
    env = {k: v for k, v in os.environ.items()
           if k not in ("P33_FAKE", "P33_ARRAY", "P4_FAKE", "P4_ARRAY", "PHASE1_DIR")}
    ok = True

    roots = {t: os.path.join(base, f"fake_{t}") for t in ("old", "new")}
    procs = [subprocess.Popen([sys.executable, __file__, "--driver", "fake", t, r], env=env)
             for t, r in roots.items()]
    if any(p.wait() for p in procs):
        print("a pipeline failed: see the traceback above")
        return 1
    ok &= report("Fake-scorer experiment (development + held-out, all four experiments):",
                 roots["old"], roots["new"])

    if a.real_dev:
        roots = {t: os.path.join(base, f"realdev_{t}") for t in ("old", "new")}
        for r in roots.values():
            shutil.copytree(REAL_DEV, os.path.join(r, os.path.basename(REAL_DEV)),
                            ignore=shutil.ignore_patterns("plots", "reports", "analysis_revisions"))
        procs = [subprocess.Popen([sys.executable, __file__, "--driver", "export", t, r,
                                   os.path.basename(REAL_DEV)], env=env) for t, r in roots.items()]
        if any(p.wait() for p in procs):
            print("a pipeline failed: see the traceback above")
            return 1
        ok &= report("Real development run dev-20261006a, its 19 CSVs rebuilt from the saved measurements:",
                     roots["old"], roots["new"])
    print(f"\noutputs: {base}")
    print("RESULT: " + ("the copy reproduces the Phase 3.3 pipeline" if ok else "DIFFERENCES FOUND (listed above)"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
