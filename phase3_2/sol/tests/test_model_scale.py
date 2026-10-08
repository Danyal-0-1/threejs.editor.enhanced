"""Deviation D10: models above 3B, up to the 72B pair on two GPUs.

No GPU and no weights: the registry, the split, the per-GPU-class arrays, the
per-task preflight and submit.sh against a stand-in `sbatch`.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys

import _helpers as H

from p33 import _paths, config as CFG, preflight, registry, splits

NEW = ["Qwen/Qwen2.5-Coder-7B", "Qwen/Qwen2.5-Coder-7B-Instruct",
       "Qwen/Qwen2.5-Coder-14B", "Qwen/Qwen2.5-Coder-14B-Instruct",
       "Qwen/Qwen2.5-Coder-32B", "Qwen/Qwen2.5-Coder-32B-Instruct",
       "deepseek-ai/deepseek-coder-33b-base", "deepseek-ai/deepseek-coder-33b-instruct",
       "Qwen/Qwen2.5-72B", "Qwen/Qwen2.5-72B-Instruct"]


def _heldout_cfg():
    return CFG.RunConfig.from_dict(json.load(open(os.path.join(_paths.SOL_ROOT, "configs", "heldout.json"))))


def test_heldout_config_appends_the_scale_models_and_keeps_indices():
    models = _heldout_cfg().models
    assert models[:11] == [
        "Qwen/Qwen2.5-Coder-0.5B", "Qwen/Qwen2.5-Coder-0.5B-Instruct",
        "Qwen/Qwen2.5-Coder-1.5B", "Qwen/Qwen2.5-Coder-1.5B-Instruct",
        "Qwen/Qwen2.5-Coder-3B", "Qwen/Qwen2.5-Coder-3B-Instruct",
        "deepseek-ai/deepseek-coder-1.3b-base", "deepseek-ai/deepseek-coder-1.3b-instruct",
        "meta-llama/Llama-3.2-1B", "meta-llama/Llama-3.2-1B-Instruct", "bigcode/starcoder2-3b"]
    assert models[11:] == NEW                                   # Llama kept, nothing replaced
    assert registry.validate_pairs(models) == []
    for m in models:
        assert registry.spec(m).size_b <= splits.MAX_SIZE_B


def test_only_the_72b_pair_needs_two_gpus():
    two = {m for m in _heldout_cfg().models if registry.gpus_needed(m) == 2}
    assert two == {"Qwen/Qwen2.5-72B", "Qwen/Qwen2.5-72B-Instruct"}
    assert preflight.model_memory_gib("Qwen/Qwen2.5-72B") > 80          # cannot fit one A100-80GB
    assert preflight.model_memory_gib("Qwen/Qwen2.5-Coder-32B") < 80    # fits one


def test_development_config_is_unchanged_by_the_scale_deviation():
    dev = CFG.RunConfig.from_dict(json.load(open(os.path.join(_paths.SOL_ROOT, "configs", "dev.json"))))
    assert dev.models == ["Qwen/Qwen2.5-Coder-0.5B", "Qwen/Qwen2.5-Coder-0.5B-Instruct",
                          "Qwen/Qwen2.5-Coder-1.5B", "Qwen/Qwen2.5-Coder-1.5B-Instruct"]


def test_preflight_checks_only_the_models_of_its_own_task():
    """A gated model awaiting approval must fail ITS task, not every task."""
    cfg = H.small_cfg(models=("Qwen/Qwen2.5-Coder-0.5B", "meta-llama/Llama-3.2-1B"))
    rd = H.tmpdir()
    pins = {}                                                   # nothing pinned at all
    rep = preflight.run(cfg, rd, pins=pins, require_gpu=False,
                        task_models=["Qwen/Qwen2.5-Coder-0.5B"])
    checked = {c["check"] for c in rep["checks"] if c["check"].startswith("model:")}
    assert checked == {"model:Qwen/Qwen2.5-Coder-0.5B"} and rep["task_models"] == ["Qwen/Qwen2.5-Coder-0.5B"]


def _cli():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "p33cli_scale", os.path.join(_paths.SOL_ROOT, "scripts", "p33.py"))
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    return cli


def _write_run(root: str, rid: str, cfg_file: str, stage: str) -> None:
    c = json.load(open(os.path.join(_paths.SOL_ROOT, "configs", cfg_file)))
    c = c.get("config", c)
    c["stage"], c["run_id"] = stage, rid
    os.makedirs(os.path.join(root, rid, "manifests"), exist_ok=True)
    json.dump({"config": c}, open(os.path.join(root, rid, "manifests", "run_config.json"), "w"))


def test_array_indices_split_the_run_by_gpu_class():
    import contextlib
    import io
    root = H.tmpdir()
    _write_run(root, "heldout-arr", "heldout.json", "heldout")
    saved = os.environ.get("P33_RESULTS_ROOT")
    os.environ["P33_RESULTS_ROOT"] = root
    try:
        cli = _cli()
        outs = {}
        for g in (1, 2):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                assert cli.main(["array-indices", "--run", "heldout-arr", "--gpus", str(g)]) == 0
            outs[g] = buf.getvalue().strip()
    finally:
        os.environ["P33_RESULTS_ROOT"] = saved
    assert outs[1] == ",".join(str(i) for i in range(19)) and outs[2] == "19,20"


def test_submit_wrapper_sends_the_72b_pair_to_the_two_gpu_profile():
    root, fake = H.tmpdir(), H.tmpdir()
    _write_run(root, "heldout-sub", "heldout.json", "heldout")
    sb = os.path.join(fake, "sbatch")
    open(sb, "w").write('#!/bin/bash\nfor a in "$@"; do echo "ARG $a"; done\n')
    os.chmod(sb, os.stat(sb).st_mode | stat.S_IEXEC)
    env = dict(os.environ, PATH=fake + os.pathsep + os.environ["PATH"], P33_RESULTS_ROOT=root,
               P33_PY=sys.executable)
    env.pop("P33_ARRAY", None)

    def args(job):
        r = subprocess.run(["bash", os.path.join(_paths.SOL_ROOT, "submit.sh"), job, "heldout-sub"],
                           env=env, capture_output=True, text=True, timeout=120)
        return r.returncode, [l[4:] for l in r.stdout.splitlines() if l.startswith("ARG ")]
    rc, a = args("heldout_eval_2gpu")
    assert rc == 0 and "--array=19,20" in a and "--gres=gpu:a100:2" in a, a
    assert a[-1].endswith("jobs/heldout_eval.slurm")
    rc, a = args("heldout_eval")
    assert rc == 0 and "--gres=gpu:a100:1" in a and "--array=" + ",".join(map(str, range(19))) in a
    assert "P33_FAKE" not in " ".join(a)
