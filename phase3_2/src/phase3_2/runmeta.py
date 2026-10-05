"""runmeta.py — environment capture and model-revision pinning.

Next-steps item: Phase 3.2 recorded python/platform/dtype but NOT the model
revision, so a silently updated checkpoint would not be detected and a result
could not be tied to the weights that produced it.

`capture()` records everything needed to reproduce a run, and `pin()` resolves
each model id to the exact HF commit sha actually loaded from the local cache.
Both are written into every result file before scoring starts, so a crashed
run still leaves a usable manifest.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return "UNKNOWN"


def pin(model_ids):
    """model id -> resolved HF revision sha from the local cache.

    Reads the cache's refs rather than calling the Hub, so a run on an offline
    compute node records the same thing an online one does -- and records what
    was ACTUALLY loaded rather than what is currently on the Hub.
    """
    out = {}
    hub = os.environ.get("HF_HOME") or os.path.expanduser("~/.cache/huggingface")
    for mid in model_ids:
        d = os.path.join(hub, "hub", "models--" + mid.replace("/", "--"))
        sha = "NOT_CACHED"
        refs = os.path.join(d, "refs", "main")
        if os.path.isfile(refs):
            sha = open(refs, encoding="utf-8").read().strip()
        out[mid] = {"revision": sha, "cache_dir": d if os.path.isdir(d) else None}
    return out


def _file_sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def capture(model_ids=(), *, extra=None) -> dict:
    """The run manifest. Write this FIRST, before any scoring."""
    try:
        import torch
        tv, cuda, dev = (torch.__version__, torch.version.cuda,
                         torch.cuda.get_device_name(0)
                         if torch.cuda.is_available() else "cpu")
    except Exception:
        tv = cuda = dev = "UNAVAILABLE"
    try:
        import transformers
        hfv = transformers.__version__
    except Exception:
        hfv = "UNAVAILABLE"

    here = os.path.dirname(os.path.abspath(__file__))
    srcs = {}
    for name in ("margins.py", "sampling.py", "prompts.py", "sites2.py",
                 "backends.py", "deltafam.py", "templates.py", "analysis.py"):
        p = os.path.join(here, name)
        if os.path.isfile(p):
            srcs[name] = _file_sha(p)

    return {
        "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_dirty": bool(_git("status", "--porcelain")),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "torch": tv, "cuda": cuda, "device_name": dev,
        "transformers": hfv,
        "dtype": os.environ.get("PHASE3_DTYPE", "float16"),
        "slurm_job": os.environ.get("SLURM_JOB_ID"),
        "models": pin(model_ids),
        "source_sha256_16": srcs,
        **(extra or {}),
    }


def write(path: str, meta: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1)
