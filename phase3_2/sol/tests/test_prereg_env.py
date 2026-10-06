"""The frozen preregistration, configuration files, and dependency preflight."""

from __future__ import annotations

import hashlib
import json
import os

import _helpers as H  # noqa: F401
from p33 import _paths, config as CFG, registry, splits

FROZEN_SHA = "a0146494a27d1206d0efc3cb7f77d2413bc09a4aedcb98a632a5c61f09f5f014"


def _prereg() -> bytes:
    return open(os.path.join(_paths.PHASE3_2_ROOT, "PREREGISTRATION.md"), "rb").read()


def test_frozen_preregistration_text_is_byte_identical():
    t = _prereg()
    i = t.index(b"## Deviations")
    assert hashlib.sha256(t[:i]).hexdigest() == FROZEN_SHA


def test_deviations_are_appended_and_dated():
    t = _prereg().decode()
    dev = t[t.index("## Deviations"):]
    for d in ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"):
        assert f"### {d} — 2026-10-05" in dev, d
    assert "- none yet" in dev            # the original line was not edited away


def test_shipped_configs_only_touch_cells_their_stage_allows():
    root = os.path.join(_paths.SOL_ROOT, "configs")
    for name, stage in (("dev.json", "dev"), ("smoke.json", "smoke"), ("local_smoke.json", "smoke")):
        c = CFG.RunConfig.from_dict(json.load(open(os.path.join(root, name))))
        c.stage, c.run_id = stage, f"{stage}-x"
        c.validate()
        splits.enforce_config(c)
    h = CFG.RunConfig.from_dict(json.load(open(os.path.join(root, "heldout.json"))))
    for fam in h.families:
        for lx in h.lexicons:
            for m in h.models:
                assert splits.classify(fam, lx, m).kind in (
                    "heldout_mapping", "heldout_model", "heldout_model_weakened",
                    "heldout_weak_family"), (fam, lx, m)


def test_registry_pairs_are_consistent():
    assert registry.validate_pairs([m for m in registry.REGISTRY if registry.spec(m).pair]) == []
    assert registry.validate_pairs([H.DEV_BASE]) != []


def test_paths_resolve_from_environment_not_a_username():
    env = dict(os.environ)
    try:
        os.environ["HOME"] = "/home/someone"
        os.environ["SCRATCH"] = "/scratch/someone"
        for k in ("P33_RESULTS_ROOT", "P33_HF_ROOT", "P33_EXPERIMENT_ROOT", "P33_CODE_ROOT"):
            os.environ.pop(k, None)
        assert CFG.results_root() == "/home/someone/phase3-3_experiment_sol/results"
        assert CFG.code_root() == "/home/someone/phase3-3_experiment_sol/repo"
        assert CFG.hf_root() == "/scratch/someone/hf"
        e = CFG.hf_env()
        assert e["HF_HUB_CACHE"] == "/scratch/someone/hf/hub" and e["HF_HUB_OFFLINE"] == "1"
    finally:
        os.environ.clear()
        os.environ.update(env)


def test_sol_defaults_are_the_verified_values_and_overridable():
    d = CFG.SolDefaults()
    assert (d.partition, d.qos, d.constraint) == ("public", "public", "a100_80")
    os.environ["P33_PARTITION"] = "other"
    try:
        assert CFG.SolDefaults().partition == "other"
    finally:
        del os.environ["P33_PARTITION"]


def test_no_job_file_uses_the_rejected_general_partition():
    jobs = os.path.join(_paths.SOL_ROOT, "jobs")
    for f in os.listdir(jobs):
        assert "partition=general" not in open(os.path.join(jobs, f)).read(), f


def test_dependency_preflight_reports_missing_packages():
    from p33 import provenance
    pk = provenance.package_versions()
    assert pk["lark"] != "MISSING", "lark is required and must be installed"
    assert set(pk) >= {"python", "transformers", "numpy", "matplotlib", "lark"}


def test_preflight_fails_on_non_a100_unless_waived():
    from p33 import preflight

    class Cfg:
        allow_non_a100 = False
        dtype = "float16"
    try:
        import torch
        if not torch.cuda.is_available():
            from run_tests import Blocked
            raise Blocked("no CUDA device to test the A100 check against", hardware=True)
        if "A100" in torch.cuda.get_device_name(0):
            return
    except ImportError:
        from run_tests import Blocked
        raise Blocked("torch not installed")
    res = {c["check"]: c["result"] for c in preflight.gpu_checks(Cfg)}
    assert res["a100"] == "FAIL"
    Cfg.allow_non_a100 = True
    res = {c["check"]: c["result"] for c in preflight.gpu_checks(Cfg)}
    assert res["a100"] == "PASS"


def test_preflight_scheduler_mismatch_fails():
    from p33 import preflight
    os.environ.update({"SLURM_JOB_ID": "1", "SLURM_JOB_PARTITION": "general",
                       "SLURM_JOB_QOS": "public", "SLURM_JOB_ACCOUNT": "grp_tlingego"})
    try:
        res = {c["check"]: c["result"] for c in preflight.scheduler_checks(CFG.SolDefaults())}
        assert res["slurm_partition"] == "FAIL" and res["slurm_qos"] == "PASS"
    finally:
        for k in ("SLURM_JOB_ID", "SLURM_JOB_PARTITION", "SLURM_JOB_QOS", "SLURM_JOB_ACCOUNT"):
            os.environ.pop(k, None)


def test_prefetch_chooses_bin_when_no_safetensors():
    from p33 import prefetch
    assert "*.safetensors" in prefetch.choose_patterns(["a.safetensors", "config.json"])
    assert "*.bin" in prefetch.choose_patterns(["pytorch_model.bin", "config.json"])


def test_prefetch_plan_never_instantiates_a_model():
    """Checked on the AST, so the docstring describing the OLD defect does not count."""
    import ast
    import inspect
    from p33 import prefetch
    tree = ast.parse(inspect.getsource(prefetch))
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | \
           {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "AutoModelForCausalLM" not in used and "from_pretrained" not in used


def test_prefetch_keeps_existing_pins_unless_repin():
    """P33-018: a second prefetch (e.g. to add a gated model) must not move an
    already-pinned model to the Hub's newest commit -- after a freeze that would
    trip the held-out pin-drift check. A fake Hub API: no network."""
    from p33 import prefetch

    class Sib:
        def __init__(self, name):
            self.rfilename, self.size, self.lfs = name, 1, None

    class Info:
        def __init__(self, sha):
            self.sha = sha
            self.siblings = [Sib("config.json"), Sib("model.safetensors")]

    class Api:
        def __init__(self):
            self.asked = []

        def model_info(self, model_id, revision=None, files_metadata=True, token=None):
            self.asked.append(revision)
            return Info(revision or "hub-latest")

    out = os.path.join(H.tmpdir(), "model_pins.json")
    json.dump({"pins": {H.DEV_BASE: {"revision": "pinned-rev"}}}, open(out, "w"))
    api = Api()
    r = prefetch.run([H.DEV_BASE, H.DEV_INST], dry_run=True, verify_only_mode=False,
                     checksums=False, out_path=out, api=api)
    assert api.asked == ["pinned-rev", None], api.asked     # pinned kept; new one resolved
    assert [p["revision"] for p in r["plans"]] == ["pinned-rev", "hub-latest"]
    assert r["kept_existing_pins"] == [H.DEV_BASE]
    api2 = Api()
    r2 = prefetch.run([H.DEV_BASE], dry_run=True, verify_only_mode=False,
                      checksums=False, out_path=out, api=api2, repin=True)
    assert api2.asked == [None] and r2["plans"][0]["revision"] == "hub-latest"


def test_materials_writer_is_idempotent_and_atomic():
    """P33-011: rebuilding an unchanged member must not touch the file.

    The CPU-tests job rebuilds the delta family; a timestamp-only rewrite
    changed the lexicons' sha256 and failed every later job's materials check.
    Runs against a copy in a temp dir, so the tracked files are never touched.
    """
    import shutil
    from phase3_2 import deltafam
    from phase3_2._vendor import CANDIDATES
    blob, _ = deltafam.build(0.50, 1, mode="strict")
    td = H.tmpdir()
    dst = os.path.join(td, "phi_d50s1.json")
    shutil.copy2(os.path.join(CANDIDATES, "phi_d50s1.json"), dst)
    before = open(dst, "rb").read()
    saved, deltafam.OUT_DIR = deltafam.OUT_DIR, td
    try:
        deltafam.write(blob)                              # same map, new timestamp
        assert open(dst, "rb").read() == before, "unchanged member was rewritten"
        deltafam.write(dict(blob, notes=blob["notes"] + " (edited)"))
        assert json.load(open(dst))["notes"].endswith("(edited)"), "a real change was not written"
        assert not [f for f in os.listdir(td) if ".tmp." in f], "temp file left behind"
    finally:
        deltafam.OUT_DIR = saved


def test_test_mode_cannot_leak_into_a_real_job():
    """submit.sh passes --export=ALL, so a P33_FAKE=1 left in the caller's shell
    would make a GPU job score with the FAKE scorer under a real label."""
    import glob
    env = open(os.path.join(_paths.SOL_ROOT, "sol.env")).read()
    assert "unset P33_FAKE" in env
    for f in glob.glob(os.path.join(_paths.SOL_ROOT, "jobs", "*.slurm")):
        body = open(f).read()
        assert "sol.env" in body, f
        if os.path.basename(f) == "cpu_tests.slurm":
            assert body.index("export P33_FAKE=1") > body.index("sol.env")
        else:
            assert "P33_FAKE" not in body, f
