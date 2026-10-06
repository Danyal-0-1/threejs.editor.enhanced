"""provenance.py — bind full run metadata to every runner and every shard.

Phase 3.2 wrote `runmeta.py` and then called it from no runner. Here every
job writes a manifest at START (status RUNNING) and rewrites it at the END
(COMPLETE / PARTIAL / FAILED / INTERRUPTED), so even a crashed job leaves a
record of exactly what it was running. Every shard marker carries the job
identity, so any row can be traced to the job, node, code and weights that
produced it.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone

from p33 import SCHEMA_VERSION
from p33 import config as CFG


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20,
                              check=True).stdout.strip()
    except Exception:
        return "UNAVAILABLE"


def git_state() -> dict:
    here = os.path.dirname(__file__)
    return {"commit": _run(["git", "-C", here, "rev-parse", "HEAD"]),
            "dirty": _run(["git", "-C", here, "status", "--porcelain"]) not in ("", "UNAVAILABLE")}


def slurm_identity() -> dict:
    e = os.environ.get
    return {"job_id": e("SLURM_JOB_ID"), "array_job_id": e("SLURM_ARRAY_JOB_ID"),
            "array_task_id": e("SLURM_ARRAY_TASK_ID"), "node": e("SLURMD_NODENAME"),
            "partition": e("SLURM_JOB_PARTITION"), "qos": e("SLURM_JOB_QOS"),
            "account": e("SLURM_JOB_ACCOUNT"), "cpus": e("SLURM_CPUS_PER_TASK")}


def job_identity() -> dict:
    s = slurm_identity()
    return {"job_id": s["job_id"], "array_task_id": s["array_task_id"],
            "node": s["node"] or platform.node(), "pid": os.getpid()}


def gpu_info() -> dict:
    out = {"nvidia_smi": _run(["nvidia-smi", "--query-gpu=name,driver_version,"
                               "memory.total,memory.free", "--format=csv,noheader"])}
    try:
        import torch
        out.update({
            "torch": torch.__version__, "cuda_runtime": torch.version.cuda,
            "cuda_available": torch.cuda.is_available(),
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "device_mem_gb": (round(torch.cuda.get_device_properties(0).total_memory / 2**30, 1)
                              if torch.cuda.is_available() else None),
            "bf16_supported": (torch.cuda.is_bf16_supported()
                               if torch.cuda.is_available() else False)})
    except Exception as exc:
        out["torch"] = f"UNAVAILABLE: {exc}"
    return out


def package_versions() -> dict:
    out = {"python": sys.version.split()[0], "platform": platform.platform()}
    for m in ("transformers", "huggingface_hub", "tokenizers", "lark", "numpy",
              "matplotlib", "safetensors", "accelerate"):
        try:
            mod = __import__(m)
            out[m] = getattr(mod, "__version__", "?")
        except Exception:
            out[m] = "MISSING"
    return out


def disk_free_gb(path: str) -> float | None:
    try:
        return round(shutil.disk_usage(path).free / 2**30, 1)
    except Exception:
        return None


class JobManifest:
    """Lifecycle record for one job (or one array task)."""

    def __init__(self, run_dir: str, cfg: "CFG.RunConfig", *, experiment: str,
                 extra: dict | None = None):
        self.run_dir = run_dir
        ident = job_identity()
        tag = f"{experiment}_{ident['job_id'] or 'local'}_{ident['array_task_id'] or 0}_{ident['pid']}"
        self.path = os.path.join(run_dir, "manifests", f"job_{tag}.json")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.data = {
            "schema_version": SCHEMA_VERSION,
            "experiment": experiment,
            "status": "RUNNING",
            "start_utc": _now(), "end_utc": None,
            "command": sys.argv,
            "cwd": os.getcwd(),
            "run_id": cfg.run_id, "stage": cfg.stage,
            "config": cfg.to_dict(), "config_hash": cfg.config_hash(),
            "seeds": cfg.seeds,
            **{f"git_{k}": v for k, v in git_state().items()},
            "slurm": slurm_identity(),
            "job": ident,
            "packages": package_versions(),
            "gpu": gpu_info(),
            "dtype": cfg.dtype, "lm_head_fp32": cfg.lm_head_fp32,
            "hf_env": {k: os.environ.get(k) for k in
                       ("HF_HOME", "HF_HUB_CACHE", "TRANSFORMERS_CACHE",
                        "HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")},
            "disk_free_gb": {"results": disk_free_gb(run_dir),
                             "hf_root": disk_free_gb(CFG.hf_root())},
            "source_hashes": CFG.source_hashes(),
            "materials_hashes": CFG.materials_hash(cfg.lexicons),
            "models": {},            # filled by add_model
            "prompt_hashes": {},     # filled by add_prompt
            "artifacts": {},
        }
        if extra:
            self.data.update(extra)
        self._flush()

    def add_model(self, model_id: str, info: dict) -> None:
        self.data["models"][model_id] = info
        self._flush()

    def add_prompt(self, key: str, sha: str) -> None:
        self.data["prompt_hashes"][key] = sha

    def finish(self, status: str, *, artifacts: list[str] = (), note: str = "") -> None:
        self.data["status"] = status
        self.data["end_utc"] = _now()
        if note:
            self.data["note"] = note
        for p in artifacts:
            if os.path.isfile(p):
                self.data["artifacts"][os.path.relpath(p, self.run_dir)] = CFG.sha256_file(p)
        self._flush()

    def _flush(self) -> None:
        CFG.atomic_write_text(self.path, json.dumps(self.data, indent=1, sort_keys=True,
                                                    default=str))
