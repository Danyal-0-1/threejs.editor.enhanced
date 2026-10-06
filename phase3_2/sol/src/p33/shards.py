"""shards.py — crash-safe result storage: atomic shards, resume, merge.

The Phase 3.2 runners wrote ONE JSON at job completion, so a timeout,
preemption, OOM or disconnection at minute 239 of 240 lost everything. Here
the unit of durability is the CELL:

    cell = (experiment, config hash, model, revision, family, lexicon,
            condition / rung-set, chunk, seed)

Each cell is written atomically and independently:

    raw/shards/<exp>/<cell>.jsonl.tmp.<pid>  --fsync-->  os.replace  -->  <cell>.jsonl
    checkpoints/<exp>/<cell>.done.json       (row count + sha256 of the shard)

A cell is DONE only if its marker exists AND the shard's sha256 and row count
match the marker. Anything else is classified -- missing, failed, corrupt or
an abandoned temp file -- and resume re-runs it. A killed job can therefore
lose at most the cell it was writing, never a finished one, and never leaves
a half-written file that looks complete.

`merge` is deterministic: rows are keyed by `row_key`, identical duplicates
are dropped and counted, CONFLICTING duplicates are an error, and the output
is sorted. A merge over an incomplete set is labelled PARTIAL, never silently
presented as complete.
"""

from __future__ import annotations

import glob
import json
import os
import socket
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, Iterator

from p33 import config as CFG


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def cell_key(fields: dict) -> str:
    """Deterministic, human-scannable cell id: readable prefix + content hash."""
    readable = "_".join(str(fields.get(k, "")).replace("/", "-")
                        for k in ("experiment", "family", "lexicon", "condition",
                                  "chunk") if k in fields)
    return f"{readable}__{CFG.sha256_json(fields)[:16]}"


def _atomic_write_text(path: str, text: str) -> None:
    CFG.atomic_write_text(path, text)


@dataclass
class CellStatus:
    key: str
    state: str                  # done | failed | corrupt | missing
    detail: str = ""


@dataclass
class MergeResult:
    rows: list[dict]
    status: str                 # COMPLETE | PARTIAL | EMPTY
    n_expected: int
    done: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    corrupt: list[str] = field(default_factory=list)
    duplicates_dropped: int = 0


class ShardStore:
    def __init__(self, run_dir: str, experiment: str):
        self.run_dir = run_dir
        self.experiment = experiment
        self.shard_dir = os.path.join(run_dir, "raw", "shards", experiment)
        self.ckpt_dir = os.path.join(run_dir, "checkpoints", experiment)
        self.quarantine_dir = os.path.join(run_dir, "checkpoints", "quarantine")
        for d in (self.shard_dir, self.ckpt_dir, self.quarantine_dir):
            os.makedirs(d, exist_ok=True)

    # -- paths -------------------------------------------------------------
    def shard_path(self, key: str) -> str:
        return os.path.join(self.shard_dir, f"{key}.jsonl")

    def done_path(self, key: str) -> str:
        return os.path.join(self.ckpt_dir, f"{key}.done.json")

    def failed_path(self, key: str) -> str:
        return os.path.join(self.ckpt_dir, f"{key}.failed.json")

    # -- state -------------------------------------------------------------
    def status(self, key: str) -> CellStatus:
        dp, sp = self.done_path(key), self.shard_path(key)
        if os.path.exists(dp):
            try:
                marker = json.load(open(dp, encoding="utf-8"))
            except Exception as exc:
                return CellStatus(key, "corrupt", f"unreadable marker: {exc}")
            if not os.path.exists(sp):
                return CellStatus(key, "corrupt", "marker without shard")
            if CFG.sha256_file(sp) != marker.get("sha256"):
                return CellStatus(key, "corrupt", "shard sha256 != marker")
            n = 0
            try:
                for line in open(sp, encoding="utf-8"):
                    if line.strip():
                        json.loads(line)
                        n += 1
            except Exception as exc:
                return CellStatus(key, "corrupt", f"unparseable shard: {exc}")
            if n != marker.get("n_rows"):
                return CellStatus(key, "corrupt", f"{n} rows != marker {marker.get('n_rows')}")
            return CellStatus(key, "done")
        if os.path.exists(self.failed_path(key)):
            try:
                rec = json.load(open(self.failed_path(key), encoding="utf-8"))
                return CellStatus(key, "failed", rec.get("error_type", ""))
            except Exception:
                return CellStatus(key, "failed", "unreadable failure record")
        return CellStatus(key, "missing")

    def is_done(self, key: str) -> bool:
        return self.status(key).state == "done"

    # -- writes ------------------------------------------------------------
    def write(self, key: str, fields: dict, rows: list[dict], *,
              job: dict | None = None) -> str:
        """Atomically write one cell's rows, then its done marker."""
        for r in rows:
            if "row_key" not in r:
                raise ValueError("every row needs a row_key")
        body = "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n"
                       for r in rows)
        sp = self.shard_path(key)
        _atomic_write_text(sp, body)
        marker = {"cell_key": key, "fields": fields, "n_rows": len(rows),
                  "sha256": CFG.sha256_file(sp), "written_utc": _now(),
                  "host": socket.gethostname(), "job": job or {}}
        _atomic_write_text(self.done_path(key), json.dumps(marker, sort_keys=True))
        if os.path.exists(self.failed_path(key)):
            os.remove(self.failed_path(key))        # superseded by success
        return sp

    def record_failure(self, key: str, fields: dict, exc: BaseException, *,
                       kind: str | None = None, job: dict | None = None) -> None:
        msg = str(exc)
        if kind is None:
            low = msg.lower()
            kind = ("OOM" if "out of memory" in low or type(exc).__name__ == "OutOfMemoryError"
                    else "INTERRUPTED" if isinstance(exc, KeyboardInterrupt)
                    else "ERROR")
        rec = {"cell_key": key, "fields": fields, "kind": kind,
               "error_type": type(exc).__name__, "message": msg[:2000],
               "traceback": traceback.format_exc()[-4000:],
               "failed_utc": _now(), "host": socket.gethostname(),
               "job": job or {}}
        _atomic_write_text(self.failed_path(key), json.dumps(rec, sort_keys=True))

    def quarantine(self, key: str) -> None:
        """Move a corrupt cell aside so a resume rewrites it cleanly."""
        for p in (self.shard_path(key), self.done_path(key)):
            if os.path.exists(p):
                os.replace(p, os.path.join(self.quarantine_dir,
                                           f"{os.path.basename(p)}.{_now()}"))

    def clean_temp(self, *, min_age_s: float = 900.0) -> int:
        """Delete abandoned .tmp files from killed writers. Returns count.

        Only files older than `min_age_s`: every array task calls this at start,
        and a fresh temp file may be ANOTHER task's write in flight (P33-014).
        Abandoned temps are harmless anyway -- they are never read as shards.
        """
        n, now = 0, time.time()
        for p in glob.glob(os.path.join(self.shard_dir, "*.tmp.*")) + \
                glob.glob(os.path.join(self.ckpt_dir, "*.tmp.*")):
            try:
                if now - os.path.getmtime(p) >= min_age_s:
                    os.remove(p)
                    n += 1
            except FileNotFoundError:          # its writer just finished
                pass
        return n

    # -- reads ---------------------------------------------------------------
    def iter_rows(self, key: str) -> Iterator[dict]:
        for line in open(self.shard_path(key), encoding="utf-8"):
            if line.strip():
                yield json.loads(line)

    def merge(self, expected_keys: Iterable[str]) -> MergeResult:
        expected = sorted(set(expected_keys))
        res = MergeResult(rows=[], status="EMPTY", n_expected=len(expected))
        by_key: dict[str, dict] = {}
        conflicts = []
        for k in expected:
            st = self.status(k)
            getattr(res, {"done": "done", "missing": "missing", "failed": "failed",
                          "corrupt": "corrupt"}[st.state]).append(k)
            if st.state != "done":
                continue
            for r in self.iter_rows(k):
                rk = r["row_key"]
                if rk in by_key:
                    if by_key[rk] == r:
                        res.duplicates_dropped += 1
                    else:
                        conflicts.append(rk)
                else:
                    by_key[rk] = r
        if conflicts:
            raise ValueError(f"{len(conflicts)} conflicting duplicate rows, e.g. "
                             f"{conflicts[:3]} -- refusing to merge")
        res.rows = [by_key[k] for k in sorted(by_key)]
        if not res.done:
            res.status = "EMPTY"
        elif res.missing or res.failed or res.corrupt:
            res.status = "PARTIAL"
        else:
            res.status = "COMPLETE"
        return res

    def write_merged(self, res: MergeResult) -> str:
        """merged/<exp>.jsonl + a status file. Deterministic byte-for-byte."""
        out_dir = os.path.join(self.run_dir, "merged")
        os.makedirs(out_dir, exist_ok=True)
        p = os.path.join(out_dir, f"{self.experiment}.jsonl")
        _atomic_write_text(p, "".join(json.dumps(r, sort_keys=True, ensure_ascii=False)
                                      + "\n" for r in res.rows))
        meta = {"experiment": self.experiment, "status": res.status,
                "n_rows": len(res.rows), "n_expected_cells": res.n_expected,
                "done": len(res.done), "missing": res.missing,
                "failed": res.failed, "corrupt": res.corrupt,
                "duplicates_dropped": res.duplicates_dropped,
                "sha256": CFG.sha256_file(p)}
        _atomic_write_text(os.path.join(out_dir, f"{self.experiment}.status.json"),
                           json.dumps(meta, sort_keys=True, indent=1))
        return p


def assert_compatible(run_dir: str, cfg: "CFG.RunConfig") -> None:
    """Refuse to resume a run directory under a different configuration."""
    p = os.path.join(run_dir, "manifests", "run_config.json")
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        _atomic_write_text(p, json.dumps({"config": cfg.to_dict(),
                                          "config_hash": cfg.config_hash()},
                                         sort_keys=True, indent=1))
        return
    stored = json.load(open(p, encoding="utf-8"))
    if stored.get("config_hash") != cfg.config_hash():
        raise RuntimeError(
            f"{run_dir} was created with config {stored.get('config_hash', '?')[:12]}, "
            f"this invocation has {cfg.config_hash()[:12]}. Resuming would mix "
            f"incompatible measurements. Use a new run_id.")
    if stored["config"].get("stage") != cfg.stage:
        raise RuntimeError("stage mismatch with the existing run directory")
