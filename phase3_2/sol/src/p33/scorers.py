"""scorers.py — load ONE model at a time, from its pinned local snapshot.

Scoring never touches the network: the snapshot is resolved with
`local_files_only=True` and the SAME `allow_patterns` the prefetcher used.
That last point is not cosmetic. huggingface_hub 1.x refuses a
`local_files_only` snapshot as "incomplete" if files outside the patterns are
missing -- verified locally: a transformers-populated cache for
Qwen2.5-Coder-0.5B fails without patterns (README.md, LICENSE, .gitattributes
were never downloaded) and resolves to commit 8123ea2e... with them.
"""

from __future__ import annotations

import hashlib
import json
import os

DEFAULT_ALLOW_PATTERNS = ["*.json", "*.safetensors", "*.model", "*.txt",
                          "tokenizer*", "vocab.*", "merges.txt"]


def load_pins(path: str | None) -> dict:
    if not path or not os.path.exists(path):
        return {}
    return json.load(open(path, encoding="utf-8")).get("pins", {})


def resolve_snapshot(model_id: str, *, revision: str | None = None,
                     allow_patterns: list[str] | None = None) -> tuple[str, str]:
    """(local snapshot path, resolved commit sha). Offline. Raises if absent."""
    from huggingface_hub import snapshot_download
    path = snapshot_download(model_id, revision=revision or "main",
                             local_files_only=True,
                             allow_patterns=allow_patterns or DEFAULT_ALLOW_PATTERNS)
    sha = os.path.basename(os.path.normpath(path))
    if revision and len(revision) == 40 and sha != revision:
        raise RuntimeError(f"{model_id}: local snapshot is {sha}, pinned {revision}")
    return path, sha


def tokenizer_fingerprint(snapshot_path: str) -> str:
    """Hash of the tokenizer files, so models sharing a tokenizer are grouped."""
    h = hashlib.sha256()
    found = False
    for name in ("tokenizer.json", "tokenizer.model", "vocab.json", "merges.txt"):
        p = os.path.join(snapshot_path, name)
        if os.path.exists(p):
            found = True
            h.update(name.encode())
            h.update(open(p, "rb").read())
    return h.hexdigest()[:16] if found else "unknown"


def load_scorer(model_id: str, *, dtype: str, device: str = "cuda",
                lm_head_fp32: bool = True, pins: dict | None = None):
    """The canonical TokenScorer, pinned, offline, with identity attached."""
    from phase3_2.margins import TokenScorer
    from p33 import registry
    pin = (pins or {}).get(model_id, {})
    path, sha = resolve_snapshot(model_id, revision=pin.get("revision"),
                                 allow_patterns=pin.get("allow_patterns"))
    n_gpus = registry.gpus_needed(model_id) if model_id in registry.REGISTRY else 1
    sc = TokenScorer(model_id, device=device, dtype=dtype, snapshot_path=path,
                     local_files_only=True, lm_head_fp32=lm_head_fp32, n_gpus=n_gpus)
    sc.revision = sha
    sc.snapshot_path = path
    sc.tokenizer_id = tokenizer_fingerprint(path)
    return sc
