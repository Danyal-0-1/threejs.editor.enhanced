"""prefetch.py — download-only model staging, with revisions pinned.

Replaces `legacy_superseded/prefetch_models.py`, which instantiated every
causal LM (`AutoModelForCausalLM.from_pretrained`) just to download it --
gigabytes of RAM and minutes per model on a login node, for no reason.

Here nothing is instantiated. `huggingface_hub.snapshot_download` fetches the
files of an EXACT commit, restricted to `allow_patterns` that are chosen per
model from its file list (safetensors when the repo has them, otherwise .bin)
and RECORDED in the pins. Scoring later resolves the same snapshot offline
with the same patterns -- which matters: hub 1.x rejects an offline snapshot
as "incomplete" when files outside the patterns are absent.

Modes
    --dry-run       resolve revisions, list files and sizes, check free space;
                    download nothing (needs network)
    (default)       download, then verify every file is present with the right
                    size and, with --checksums, the LFS sha256
    --verify-only   offline: resolve already-cached models and write pins
                    (used for the local smoke, where the cache already exists)

Writes `model_pins.json` (revision, patterns, files, tokenizer fingerprint
per model) and lists every failure explicitly. A model that is ALREADY pinned
keeps its pinned revision; only `--repin` moves it to the Hub's current
commit (P33-018). Otherwise re-running prefetch -- say, to add a gated model
after access is granted -- would silently re-pin every model the Hub updated,
and after a freeze every held-out command would refuse on pin drift. A gated model (Llama) needs
`HF_TOKEN` in the environment; the token is never written anywhere.
Base/instruct pairing is validated against the registry.

A model served by the ASU RC LLM API (`registry.is_api`) has nothing to
download: its pin is the deployment that answers now, "<served model>@<system
fingerprint>" (p4/scoring/api.py), and it is kept like any other pin.
"""

from __future__ import annotations

import hashlib
import json
import os
import time

from p4.runtime import config as CFG
from p4.governance import registry

CONFIG_PATTERNS = ["*.json", "*.model", "*.txt", "tokenizer*", "vocab.*", "merges.txt"]


def choose_patterns(filenames: list[str]) -> list[str]:
    has_st = any(f.endswith(".safetensors") for f in filenames)
    weights = ["*.safetensors"] if has_st else ["*.bin"]
    return CONFIG_PATTERNS + weights


def _matches(name: str, patterns: list[str]) -> bool:
    import fnmatch
    base = os.path.basename(name)
    return any(fnmatch.fnmatch(name, p) or fnmatch.fnmatch(base, p) for p in patterns)


def plan(model_id: str, api, *, revision: str | None = None) -> dict:
    """Resolve the exact commit (the pinned one, if given) and its files."""
    info = api.model_info(model_id, revision=revision, files_metadata=True,
                          token=os.environ.get("HF_TOKEN"))
    names = [s.rfilename for s in info.siblings]
    pats = choose_patterns(names)
    files = []
    for s in info.siblings:
        if "/" in s.rfilename and s.rfilename.split("/")[0] in ("original", "onnx", "gguf"):
            continue
        if _matches(s.rfilename, pats):
            lfs = getattr(s, "lfs", None)
            files.append({"name": s.rfilename, "size": s.size,
                          "sha256": (lfs.get("sha256") if isinstance(lfs, dict)
                                     else getattr(lfs, "sha256", None))})
    return {"model": model_id, "revision": info.sha, "allow_patterns": pats,
            "files": files, "bytes": sum(f["size"] or 0 for f in files)}


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(p: dict, *, retries: int = 3, checksums: bool = False) -> dict:
    from huggingface_hub import snapshot_download
    last = None
    for attempt in range(1, retries + 1):
        try:
            path = snapshot_download(p["model"], revision=p["revision"],
                                     allow_patterns=p["allow_patterns"],
                                     token=os.environ.get("HF_TOKEN"))
            break
        except Exception as exc:                 # resumable; retry with backoff
            last = exc
            time.sleep(min(60, 5 * attempt))
    else:
        raise RuntimeError(f"{p['model']}: download failed after {retries} tries: {last}")
    problems = []
    for f in p["files"]:
        fp = os.path.join(path, f["name"])
        if not os.path.exists(fp):
            problems.append(f"missing {f['name']}")
        elif f["size"] is not None and os.path.getsize(fp) != f["size"]:
            problems.append(f"size mismatch {f['name']}")
        elif checksums and f["sha256"] and _sha256(fp) != f["sha256"]:
            problems.append(f"sha256 mismatch {f['name']}")
    if problems:
        raise RuntimeError(f"{p['model']}: verification failed: {problems[:5]}")
    from p4.scoring.scorers import tokenizer_fingerprint
    return {**p, "snapshot_path": path, "tokenizer_id": tokenizer_fingerprint(path),
            "verified_checksums": checksums}


def verify_only(models: list[str], kept: dict | None = None) -> tuple[dict, dict]:
    from p4.scoring.scorers import DEFAULT_ALLOW_PATTERNS, resolve_snapshot, tokenizer_fingerprint
    pins, failed = {}, {}
    kept = kept or {}
    for m in models:
        try:
            pats = kept.get(m, {}).get("allow_patterns") or DEFAULT_ALLOW_PATTERNS
            path, sha = resolve_snapshot(m, revision=kept.get(m, {}).get("revision"),
                                         allow_patterns=pats)
            pins[m] = {"revision": sha, "allow_patterns": pats,
                       "snapshot_path": path, "tokenizer_id": tokenizer_fingerprint(path),
                       "source": "verify-only (already cached)"}
        except Exception as exc:
            failed[m] = f"{type(exc).__name__}: {str(exc)[:200]}"
    return pins, failed


def pin_served(models: list[str], kept: dict) -> tuple[dict, dict]:
    """Served models: pin the deployment that answers now. Nothing is downloaded. An already
    pinned model keeps its pin; preflight and the scorer refuse when another one answers."""
    from datetime import datetime, timezone
    from p4.runtime import asu_api
    from p4.scoring.api import APIScorer
    pins, failed = {}, {}
    for m in models:
        if m in kept:
            continue
        try:
            sc = APIScorer.for_model(m)
            sc.release()
            s = registry.spec(m)
            pins[m] = {"revision": sc.revision, "serving": "api", "api_model": s.api_model,
                       "quantization": s.quantization, "tokenizer_id": sc.tokenizer_id,
                       "base_url": asu_api.BASE,
                       "pinned_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       "source": "the ASU RC LLM API deployment that answered"}
        except Exception as exc:
            failed[m] = f"{type(exc).__name__}: {str(exc)[:200]}"
    return pins, failed


def run(models: list[str], *, dry_run: bool, verify_only_mode: bool,
        checksums: bool, out_path: str, repin: bool = False, api=None) -> dict:
    problems = registry.validate_pairs(models)
    old = {}
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as fh:
            old = json.load(fh).get("pins", {})
    kept = {} if repin else {m: old[m] for m in models if old.get(m, {}).get("revision")}
    served = [m for m in models if registry.is_api(m)]
    models = [m for m in models if m not in served]
    if verify_only_mode:
        pins, failed = verify_only(models, kept)
        result = {"mode": "verify-only", "pins": pins, "failed": failed,
                  "pairing_problems": problems}
    else:
        if api is None and models:
            from huggingface_hub import HfApi
            api = HfApi()
        plans, failed = [], {}
        for m in models:
            try:
                plans.append(plan(m, api, revision=kept.get(m, {}).get("revision")))
            except Exception as exc:
                failed[m] = f"{type(exc).__name__}: {str(exc)[:200]}"
        need_gb = sum(p["bytes"] for p in plans) / 2**30
        root = CFG.hf_root()
        probe = root
        while probe and not os.path.exists(probe):
            probe = os.path.dirname(probe)
        import shutil
        free_gb = shutil.disk_usage(probe).free / 2**30 if probe else None
        result = {"mode": "dry-run" if dry_run else "download",
                  "estimated_gb": round(need_gb, 2), "free_gb_at_hf_root": free_gb,
                  "space_ok": free_gb is None or free_gb > need_gb * 1.1,
                  "plans": plans, "failed": failed, "pairing_problems": problems, "pins": {}}
        if not dry_run:
            if not result["space_ok"]:
                raise RuntimeError(f"need ~{need_gb:.1f} GiB at {root}, have {free_gb:.1f}")
            for p in plans:
                try:
                    got = download(p, checksums=checksums)
                    result["pins"][p["model"]] = {k: got[k] for k in
                                                  ("revision", "allow_patterns", "files",
                                                   "snapshot_path", "tokenizer_id",
                                                   "verified_checksums")}
                except Exception as exc:
                    failed[p["model"]] = str(exc)[:300]
    if served:
        got, bad = pin_served(served, kept)
        result["pins"].update(got)
        result["failed"].update(bad)
        result["served"] = sorted(served)
    result["kept_existing_pins"] = sorted(kept)
    if not dry_run:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        existing = dict(old)
        existing.update(result["pins"])
        blob = {"pins": existing, "failed": result["failed"],
                "pairing_problems": problems, "hf_root": CFG.hf_root()}
        CFG.atomic_write_text(out_path, json.dumps(blob, indent=1, sort_keys=True))
    return result
