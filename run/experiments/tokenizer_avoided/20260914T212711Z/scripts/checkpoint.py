"""checkpoint.py — append-only, auditable result storage with safe resume.

A result key must identify EVERY axis that could change the number, so a resume
can never skip a cell that was actually run under a different configuration.
On resume, a row counts as done only if it is a complete JSON object carrying
its own result_key: a truncated final line (the crash case) is ignored and the
cell is re-run.
"""
from __future__ import annotations

import hashlib, json, os


def result_key(*, model: str, revision: str, tokenizer_revision: str, lane: str,
               language: str, condition: str, case_id: str, seed: int,
               precision: str, device: str, prompt_hash: str) -> str:
    return "|".join((model, revision, tokenizer_revision, lane, language,
                     condition, case_id, str(seed), precision, device, prompt_hash))


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def append_row(path: str, row: dict) -> None:
    """Append one row and fsync, so a kill between items cannot lose it."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def load_done(path: str) -> set[str]:
    """The set of result_keys already completed and INTACT in `path`."""
    done: set[str] = set()
    if not os.path.exists(path):
        return done
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue                      # truncated / corrupt -> re-run
            key = row.get("result_key")
            if isinstance(key, str) and key:
                done.add(key)
    return done


def read_rows(path: str) -> list[dict]:
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows
