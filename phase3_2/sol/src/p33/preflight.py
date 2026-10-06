"""preflight.py — refuse to start a GPU job that would waste its allocation.

Every GPU job calls `run()` BEFORE loading any model. Each check returns
PASS / WARN / FAIL with evidence; any FAIL stops the job with exit code 2.

    scheduler      actual partition / QOS / account match the configured ones
    gpu            nvidia-smi answers; torch sees CUDA; the device is an A100
                   (waivable only with allow_non_a100, which is recorded)
    precision      bfloat16 supported when the run asks for bf16
    versions       torch / CUDA runtime / driver / transformers recorded --
                   Sol's env NAMED pytorch-gpu-2.3.1-cuda-12.1 reported torch
                   2.11.0+cu130, so names are never trusted
    space          free GPU memory, free space in results and in the HF cache
    models         every model resolves OFFLINE to its pinned revision with
                   the pinned allow_patterns
    output         the run directory is writable
    materials      materials hashes equal those recorded at run creation
    split          every (family, lexicon, model) cell is allowed for the stage
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone

from p33 import config as CFG
from p33 import provenance, splits


def _check(name, ok, detail, *, warn=False):
    """PASS / FAIL, or WARN for informational checks that never block a job."""
    if warn:
        return {"check": name, "result": "WARN", "detail": detail}
    return {"check": name, "result": "PASS" if ok else "FAIL", "detail": detail}


def scheduler_checks(d: "CFG.SolDefaults") -> list[dict]:
    s = provenance.slurm_identity()
    if not s["job_id"]:
        return [_check("scheduler", True, "not inside Slurm (local run)", warn=True)]
    out = []
    for key, want in (("partition", d.partition), ("qos", d.qos), ("account", d.account)):
        got = s.get(key)
        out.append(_check(f"slurm_{key}", got == want or got is None,
                          f"actual={got!r} configured={want!r}"))
    return out


def gpu_checks(cfg) -> list[dict]:
    out = []
    smi = shutil.which("nvidia-smi")
    if smi:
        r = subprocess.run([smi, "--query-gpu=name,driver_version,memory.total,memory.free",
                            "--format=csv,noheader"], capture_output=True, text=True)
        out.append(_check("nvidia_smi", r.returncode == 0, r.stdout.strip() or r.stderr.strip()))
    else:
        out.append(_check("nvidia_smi", False, "nvidia-smi not found"))
    try:
        import torch
        avail = torch.cuda.is_available()
        out.append(_check("torch_cuda", avail, f"torch {torch.__version__}, CUDA runtime {torch.version.cuda}"))
        if avail:
            name = torch.cuda.get_device_name(0)
            is_a100 = "A100" in name
            out.append(_check("a100", is_a100 or cfg.allow_non_a100,
                              f"{name}" + ("" if is_a100 else " (waived: allow_non_a100)" if cfg.allow_non_a100 else "")))
            if cfg.dtype == "bfloat16":
                out.append(_check("bf16", torch.cuda.is_bf16_supported(), "bfloat16 support"))
            free, total = torch.cuda.mem_get_info()
            out.append(_check("gpu_memory", free > 2 * 2**30,
                              f"free {free/2**30:.1f} GiB of {total/2**30:.1f} GiB"))
    except Exception as exc:
        out.append(_check("torch_cuda", False, f"torch import failed: {exc}"))
    return out


def space_checks(run_dir: str) -> list[dict]:
    out = []
    for name, path, need in (("results_space", run_dir, 2.0), ("hf_cache_space", CFG.hf_root(), 5.0)):
        p = path
        while p and not os.path.exists(p):
            p = os.path.dirname(p)
        gb = provenance.disk_free_gb(p) if p else None
        out.append(_check(name, gb is not None and gb >= need, f"{gb} GiB free at {p} (need {need})"))
    return out


def model_checks(models, pins) -> list[dict]:
    from p33.scorers import resolve_snapshot
    out = []
    for m in models:
        pin = pins.get(m)
        if not pin:
            out.append(_check(f"model:{m}", False, "not pinned -- run `p33 prefetch`"))
            continue
        try:
            path, sha = resolve_snapshot(m, revision=pin.get("revision"),
                                         allow_patterns=pin.get("allow_patterns"))
            out.append(_check(f"model:{m}", sha == pin.get("revision"),
                              f"local {sha[:12]} pinned {str(pin.get('revision'))[:12]}"))
        except Exception as exc:
            out.append(_check(f"model:{m}", False, f"{type(exc).__name__}: {str(exc)[:160]}"))
    return out


def output_checks(run_dir: str) -> list[dict]:
    try:
        os.makedirs(run_dir, exist_ok=True)
        probe = os.path.join(run_dir, f".write_probe_{os.getpid()}")
        open(probe, "w").write("ok")
        os.remove(probe)
        return [_check("output_writable", True, run_dir)]
    except Exception as exc:
        return [_check("output_writable", False, f"{run_dir}: {exc}")]


def materials_checks(run_dir: str, cfg) -> list[dict]:
    now = CFG.materials_hash(cfg.lexicons)
    jobs = sorted(f for f in os.listdir(os.path.join(run_dir, "manifests"))
                  if f.startswith("job_")) if os.path.isdir(os.path.join(run_dir, "manifests")) else []
    if not jobs:
        return [_check("materials", True, "first job in this run; hashes recorded now", warn=True)]
    first = json.load(open(os.path.join(run_dir, "manifests", jobs[0])))
    same = first.get("materials_hashes") == now
    return [_check("materials", same, "materials identical to the run's first job" if same
                   else "materials CHANGED since this run started")]


def split_checks(cfg, run_dir: str) -> list[dict]:
    try:
        cls = splits.enforce_config(cfg, run_dir=run_dir if cfg.stage == "heldout" else None)
        return [_check("split_permission", True,
                       f"{len(cls)} cells allowed for stage {cfg.stage}: "
                       f"{sorted({c.label for c in cls.values()})}")]
    except splits.SplitViolation as exc:
        return [_check("split_permission", False, str(exc))]


def run(cfg, run_dir: str, *, pins: dict, require_gpu: bool = True) -> dict:
    d = CFG.SolDefaults()
    checks = scheduler_checks(d)
    if require_gpu:
        checks += gpu_checks(cfg)
    checks += space_checks(run_dir) + output_checks(run_dir)
    checks += model_checks(cfg.models, pins) + materials_checks(run_dir, cfg)
    checks += split_checks(cfg, run_dir)
    rep = {"utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "run_id": cfg.run_id, "stage": cfg.stage, "checks": checks,
           "versions": provenance.package_versions(), "gpu": provenance.gpu_info(),
           "ok": all(c["result"] != "FAIL" for c in checks)}
    os.makedirs(os.path.join(run_dir, "manifests"), exist_ok=True)
    p = os.path.join(run_dir, "manifests", f"preflight_{rep['utc'].replace(':', '')}.json")
    json.dump(rep, open(p, "w"), indent=1, default=str)
    rep["path"] = p
    return rep
