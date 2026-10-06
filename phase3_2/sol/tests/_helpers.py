"""Shared fixtures for the Phase 3.3 tests. No GPU, no weights."""

from __future__ import annotations

import os
import tempfile

import p33  # noqa: F401
from p33 import config as CFG

DEV_BASE = "Qwen/Qwen2.5-Coder-0.5B"
DEV_INST = "Qwen/Qwen2.5-Coder-0.5B-Instruct"


def tmpdir(prefix="p33t_") -> str:
    return tempfile.mkdtemp(prefix=prefix)


def small_cfg(run_id="dev-t1", *, models=(DEV_BASE, DEV_INST), lexicons=("d50s1",),
              families=("dom",), stage="dev", site_limit=24, chunk=8,
              ladder=(0, 1, 2, 4, 8), primary_sites=12) -> CFG.RunConfig:
    cfg = CFG.RunConfig(run_id=run_id, stage=stage, models=list(models),
                        families=list(families), lexicons=list(lexicons),
                        site_limit=site_limit, chunk_size=chunk)
    cfg.primary.update({"site_limit": primary_sites, "ladder": list(ladder)})
    cfg.analysis["B"] = 200
    return cfg


def fake_pins(cfg) -> dict:
    return {m: {"revision": "fakerev0001"} for m in cfg.models}


def fake_factory(**kw):
    from p33.fakes import FakeScorer
    return lambda m: FakeScorer(m, **kw)
