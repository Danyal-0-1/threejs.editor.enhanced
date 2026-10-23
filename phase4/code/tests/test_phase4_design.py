"""Phase 4's own design: its folders, environment names, preregistration, split and label.

The rest of the suite runs under Phase 3.3's registered design (phase3_3_design.py); every test
here takes it off first.
"""

from __future__ import annotations

import json
import os
import tempfile

import phase3_3_design as D

import p4
from p4 import paths
from p4.governance import freeze, registry, splits
from p4.runtime import config as CFG


def _raises(fn, exc, text):
    try:
        fn()
    except exc as e:
        assert text in str(e), str(e)
    else:
        raise AssertionError(f"expected {exc.__name__} ({text!r})")


def test_phase4_never_uses_phase3_3s_folder_even_in_a_phase3_3_shell():
    env = dict(os.environ)
    try:
        for k in list(os.environ):
            if k.startswith(("P4_", "P33_")):
                del os.environ[k]
        os.environ["HOME"] = "/home/someone"
        # a shell that sourced Phase 3.3's sol.env
        os.environ["P33_RESULTS_ROOT"] = "/home/someone/phase3-3_experiment_sol/results"
        os.environ["P33_EXPERIMENT_ROOT"] = "/home/someone/phase3-3_experiment_sol"
        assert CFG.experiment_root() == "/home/someone/phase4_experiment_sol"
        assert CFG.results_root() == "/home/someone/phase4_experiment_sol/results"
        assert CFG.code_root() == "/home/someone/phase4_experiment_sol/repo"
    finally:
        os.environ.clear()
        os.environ.update(env)


def test_no_phase3_3_environment_name_is_left_in_the_code():
    for root in (paths.PACKAGE, paths.SOL_ROOT, os.path.join(paths.CODE_ROOT, "tools")):
        for dp, _ds, fs in os.walk(root):
            for f in fs:
                if f.endswith((".py", ".sh", ".slurm", ".env")) and f != "compare_with_phase3_3.py":
                    text = open(os.path.join(dp, f), encoding="utf-8").read()
                    assert "P33_" not in text, os.path.join(dp, f)
    sol_env = open(os.path.join(paths.SOL_ROOT, "sol.env"), encoding="utf-8").read()
    assert "$HOME/phase4_experiment_sol" in sol_env and "phase3-3_experiment_sol" not in sol_env


def test_the_pipeline_reads_phase4s_own_preregistration():
    with D.phase4_design():
        assert paths.PREREGISTRATION == os.path.join(paths.REPO_ROOT, "phase4", "PREREGISTRATION.md")
        assert os.path.isfile(paths.PREREGISTRATION)


def test_a_draft_preregistration_cannot_be_frozen():
    with D.phase4_design():
        fd, tmp = tempfile.mkstemp(suffix=".md")
        os.write(fd, b"# Phase 4 preregistration\n\n**Status: DRAFT - not registered.**\n")
        os.close(fd)
        saved = paths.PREREGISTRATION
        paths.PREREGISTRATION = tmp
        try:
            _raises(lambda: freeze.build_payload("/no/run/needed", None), splits.FreezeError, "still a draft")
        finally:
            paths.PREREGISTRATION = saved


def test_phase4s_split_holds_nothing_out_yet():
    with D.phase4_design():
        assert splits.HELDOUT_LEXICONS == frozenset()
        for fam in ("dom", "blk"):
            for lx in ("d25s1", "d50s2", "d25s3", "d50s3", "d75s1a", "d75s3a"):   # Phase 3.3 dev and held-out
                assert splits.classify(fam, lx, "Qwen/Qwen2.5-Coder-7B").kind == "dev", (fam, lx)
        _raises(lambda: splits.check_access("heldout", "dom", "d75s1a", "Qwen/Qwen2.5-72B",
                                            run_dir=tempfile.mkdtemp()),
                splits.SplitViolation, "held-out stage scores held-out cells only")


def test_every_model_phase3_3_scored_is_development_and_an_unseen_model_is_not():
    with D.phase4_design():
        c = json.load(open(os.path.join(paths.CONFIGS, "phase3_3", "heldout.json")))
        assert splits.DEV_MODELS == frozenset(c.get("config", c)["models"])
        unseen = sorted(set(registry.REGISTRY) - splits.DEV_MODELS)
        assert unseen, "the registry should still hold models Phase 3.3 never scored"
        for m in unseen:          # held-out, or above the size ceiling: either way not development
            big = registry.spec(m).size_b > splits.MAX_SIZE_B
            assert splits.classify("dom", "d50s1", m).kind == ("forbidden" if big else "heldout_model"), m
            _raises(lambda m=m: splits.check_access("dev", "dom", "d50s1", m), splits.SplitViolation,
                    "size ceiling" if big else "may touch development cells only")


def test_phase4s_label_and_frozen_source_set():
    assert p4.SCHEMA_VERSION == "p4/1"
    keys = CFG.source_hashes()
    assert "phase4/code/run.py" in keys
    assert any(k.startswith("phase4/code/p4/") for k in keys)
    assert "phase4/code/dsl/alien_syntax/src/phi.py" in keys     # the language code is frozen too


def test_the_phase3_3_design_is_exactly_the_frozen_split():
    src = open(os.path.join(paths.REPO_ROOT, "phase3_2", "sol", "src", "p33", "splits.py"),
               encoding="utf-8").read()
    block = src[src.index("DEV_FAMILIES = "):src.index("class SplitViolation")]
    ns: dict = {}
    exec(block, {"frozenset": frozenset}, ns)
    names = {k for k in ns if not k.startswith("__")}
    assert names == set(D.SPLIT), sorted(names ^ set(D.SPLIT))
    for k, v in D.SPLIT.items():
        assert ns[k] == v, k


def test_phase4s_configs_only_touch_cells_their_stage_allows():
    """Every config at the top of configs/ is Phase 4's: its stage comes from its name
    (smoke*, dev*, heldout*), and each of its cells must be allowed by Phase 4's split."""
    with D.phase4_design():
        found = 0
        for f in sorted(os.listdir(paths.CONFIGS)):
            if not f.endswith(".json"):
                continue
            stage = next(s for s in ("smoke", "dev", "heldout") if f.startswith(s))
            c = json.load(open(os.path.join(paths.CONFIGS, f)))
            c = c.get("config", c)
            for fam in c["families"]:
                for lx in c["lexicons"]:
                    for m in c["models"]:
                        kind = splits.classify(fam, lx, m).kind
                        assert kind in splits._ALLOWED[stage], (f, fam, lx, m, kind)
            found += 1
        assert found >= 1


def test_phase4s_jobs_and_their_logs_are_named_p4():
    """squeue, `scancel --name` and the log files (%x) must never mix the two phases."""
    submit = open(os.path.join(paths.SOL_ROOT, "submit.sh"), encoding="utf-8").read()
    assert '--job-name="p4-$JOB"' in submit
    assert "p33-" not in submit


def test_every_experiments_rows_carry_phase4s_label():
    """Arm B and H5 once wrote Phase 3.3's label ("p33/1") into their rows, whatever the run."""
    import test_e2e
    _cfg, rd, _pins, _st = test_e2e._dev_run()
    for exp in ("arm_a", "primary", "armb", "h5"):
        rows = [json.loads(x) for x in open(os.path.join(rd, "merged", f"{exp}.jsonl")) if x.strip()]
        assert rows and {r["schema_version"] for r in rows} == {p4.SCHEMA_VERSION}, exp
