"""splits.py — the registered split, enforced in code, plus the freeze lock.

`PREREGISTRATION.md` §2 froze the split on 2026-10-02. Until now it was
enforced by discipline; this module enforces it mechanically. Every runner
calls `check_access` for every (family, lexicon, model) cell BEFORE it
enumerates, loads or scores anything, and a held-out cell is refused unless an
intact `DEV_FREEZE.json` AND a matching `HELDOUT_UNLOCK.json` exist.

----------------------------------------------------------------------------
WHAT THE PREREGISTRATION SAYS, AND WHAT HAS SINCE BEEN LEARNED
----------------------------------------------------------------------------
development       dom x {d25s1, d25s2, d50s1, d50s2}, Qwen2.5-Coder 0.5B/1.5B
held-out mapping  d25s3, d50s3, all of d75
held-out grammar  all of blk                       <-- NO LONGER CLEAN
held-out models   everything except Qwen2.5-Coder 0.5B/1.5B

`blk` was SCORED before the freeze (the Phase 3.2 balanced run and the Phase
3.3 primary run both used blk x d50s1), so it is not an unseen grammar family.
Calling a blk result "held-out grammar confirmation" would be false. This
module therefore:

  * classifies blk x d50s1 (and any blk x dev lexicon) as
    EXPLORATORY_CONTAMINATED -- refused unless explicitly allowed, and then
    labelled exploratory;
  * classifies blk x a never-scored held-out mapping as HELDOUT_WEAK_FAMILY --
    the weaker alternative recorded as deviation D1, always labelled weak;
  * keeps family-level confirmation NOT TESTABLE until a NEW grammar family is
    explicitly approved (`APPROVED_NEW_FAMILIES`, empty). No family is invented.

Qwen2.5-Coder-3B (base and instruct) was observed under a superseded protocol
before the freeze (dom only, no rule table). It remains a held-out model but is
labelled HELDOUT_MODEL_WEAKENED (deviation D2).

Model size (deviation D10, 2026-10-07): the registered "do not scale beyond
3B until the grammar evidence exists" gate could never be met (D1), so it is
replaced by a 72B ceiling. Every model above the development sizes is a
held-out MODEL; nothing above 72B may be scored in any stage.
"""

from __future__ import annotations

import json
import os
import stat
from dataclasses import dataclass
from datetime import datetime, timezone

from p33 import config as CFG
from p33 import registry as R

DEV_FAMILIES = frozenset({"dom"})
DEV_LEXICONS = frozenset({"d25s1", "d25s2", "d50s1", "d50s2"})
HELDOUT_LEXICONS = frozenset({"d25s3", "d50s3", "d75s1a", "d75s2a", "d75s3a"})
DEV_MODELS = frozenset({
    "Qwen/Qwen2.5-Coder-0.5B", "Qwen/Qwen2.5-Coder-0.5B-Instruct",
    "Qwen/Qwen2.5-Coder-1.5B", "Qwen/Qwen2.5-Coder-1.5B-Instruct"})

CONTAMINATED_FAMILIES = {
    "blk": "scored before the freeze (Phase 3.2 balanced Arm A and Phase 3.3 "
           "primary run, blk x d50s1); not an unseen grammar family"}
PREVIOUSLY_OBSERVED_MODELS = {
    "Qwen/Qwen2.5-Coder-3B": "observed under a superseded protocol before the "
                             "freeze (arm_a_sizes.json: dom only, no rule table)",
    "Qwen/Qwen2.5-Coder-3B-Instruct": "as above"}
APPROVED_NEW_FAMILIES: frozenset[str] = frozenset()   # none approved; none invented
KNOWN_FAMILIES = frozenset({"dom", "blk"})
# Deviation D10 (2026-10-07): the registered "no model above 3B" gate could
# never be met (it waited on blk evidence, which D1 made impossible) and kept
# the study at a scale reviewers would dismiss. Replaced, before any freeze or
# held-out access, by a 72B ceiling: every model above 3B is a HELD-OUT model.
MAX_SIZE_B = 72.0


class SplitViolation(PermissionError):
    """Raised before anything is enumerated, loaded or scored."""


@dataclass(frozen=True)
class CellClass:
    kind: str           # see KINDS
    label: str          # what every output row and aggregate must carry
    reason: str


KINDS = ("dev", "heldout_mapping", "heldout_model", "heldout_model_weakened",
         "heldout_weak_family", "exploratory_contaminated", "forbidden")


def classify(family: str, lexicon: str, model: str) -> CellClass:
    if family not in KNOWN_FAMILIES and family not in APPROVED_NEW_FAMILIES:
        return CellClass("forbidden", "FORBIDDEN",
                         f"grammar family {family!r} is not registered or approved")
    if lexicon not in DEV_LEXICONS | HELDOUT_LEXICONS:
        return CellClass("forbidden", "FORBIDDEN",
                         f"lexicon {lexicon!r} is not in the registered split")
    try:
        ms = R.spec(model)
    except KeyError as exc:
        return CellClass("forbidden", "FORBIDDEN", str(exc))
    if ms.size_b > MAX_SIZE_B:
        return CellClass("forbidden", "FORBIDDEN",
                         f"{model} is {ms.size_b}B > {MAX_SIZE_B}B, the size ceiling "
                         f"registered by deviation D10")

    if family in CONTAMINATED_FAMILIES:
        if lexicon in HELDOUT_LEXICONS:
            return CellClass("heldout_weak_family", "HELDOUT-WEAK-FAMILY",
                             "blk x never-scored mapping: deviation D1's weaker "
                             "alternative, NOT a held-out grammar confirmation")
        return CellClass("exploratory_contaminated", "EXPLORATORY",
                         CONTAMINATED_FAMILIES[family])

    model_dev = model in DEV_MODELS
    if family in DEV_FAMILIES and lexicon in DEV_LEXICONS and model_dev:
        return CellClass("dev", "DEVELOPMENT", "registered development cell")
    if lexicon in HELDOUT_LEXICONS and model_dev:
        return CellClass("heldout_mapping", "HELDOUT", "held-out mapping")
    if model in PREVIOUSLY_OBSERVED_MODELS:
        return CellClass("heldout_model_weakened", "HELDOUT-WEAKENED",
                         PREVIOUSLY_OBSERVED_MODELS[model])
    return CellClass("heldout_model", "HELDOUT", "held-out model")


_ALLOWED = {
    "smoke": {"dev"},
    "dev": {"dev"},
    "heldout": {"heldout_mapping", "heldout_model", "heldout_model_weakened",
                "heldout_weak_family"},
}


def check_access(stage: str, family: str, lexicon: str, model: str, *,
                 run_dir: str | None = None, allow_exploratory: bool = False
                 ) -> CellClass:
    """Return the cell's class or raise SplitViolation. Call before touching it."""
    cc = classify(family, lexicon, model)
    if cc.kind == "forbidden":
        raise SplitViolation(f"{family}/{lexicon}/{model}: {cc.reason}")
    if cc.kind == "exploratory_contaminated":
        if allow_exploratory and stage in ("dev", "smoke"):
            return cc
        raise SplitViolation(
            f"{family}/{lexicon}/{model} is EXPLORATORY-CONTAMINATED "
            f"({cc.reason}); pass allow_exploratory to score it, and its "
            f"outputs will be labelled EXPLORATORY")
    if cc.kind not in _ALLOWED.get(stage, set()):
        if stage in ("dev", "smoke"):
            raise SplitViolation(
                f"{family}/{lexicon}/{model} is {cc.kind.upper()} and stage "
                f"{stage!r} may touch development cells only")
        raise SplitViolation(
            f"{family}/{lexicon}/{model} is a {cc.kind} cell; the held-out "
            f"stage scores held-out cells only -- development data belong in "
            f"a dev run")
    if stage == "heldout":
        if not run_dir:
            raise SplitViolation("held-out access needs the run directory "
                                 "holding HELDOUT_UNLOCK.json")
        load_unlock(run_dir)        # raises if missing or not matching the freeze
    return cc


def enforce_config(cfg: "CFG.RunConfig", *, run_dir: str | None = None) -> dict:
    """Check EVERY cell a config would touch, up front. Returns {cell: class}."""
    out = {}
    for fam in cfg.families:
        for lx in cfg.lexicons:
            for m in cfg.models:
                cc = check_access(cfg.stage, fam, lx, m, run_dir=run_dir,
                                  allow_exploratory=cfg.allow_exploratory)
                out[f"{fam}/{lx}/{m}"] = cc
    return out


# ---------------------------------------------------------------------------
# DEV_FREEZE.json — immutable once written
# ---------------------------------------------------------------------------

FREEZE_REQUIRED = ("risk_score_formula", "calibration", "decision_threshold",
                   "prompts", "exclusions", "analysis_config", "config_hashes",
                   "source_hashes", "model_pins", "timestamp_utc", "dev_run_id")


class FreezeError(RuntimeError):
    pass


def _sidecar(path: str) -> str:
    return path + ".sha256"


def write_freeze(path: str, payload: dict) -> str:
    """Write DEV_FREEZE.json exactly once. Refuses to overwrite.

    The file is made read-only and a `.sha256` sidecar records its hash, so a
    later edit -- accidental or not -- is detected by `load_freeze`.
    """
    missing = [k for k in FREEZE_REQUIRED if k not in payload]
    if missing:
        raise FreezeError(f"freeze payload missing {missing}")
    if os.path.exists(path) or os.path.exists(_sidecar(path)):
        raise FreezeError(f"{path} already exists; a freeze is immutable. "
                          f"Start a new development run to change anything.")
    blob = json.dumps(payload, sort_keys=True, indent=1, ensure_ascii=False)
    CFG.atomic_write_text(path, blob)
    digest = CFG.sha256_file(path)
    with open(_sidecar(path), "w", encoding="utf-8") as fh:
        fh.write(digest + "\n")
    for p in (path, _sidecar(path)):
        os.chmod(p, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return digest


def load_freeze(path: str) -> dict:
    if not os.path.isfile(path):
        raise FreezeError(f"no DEV_FREEZE at {path}")
    if not os.path.isfile(_sidecar(path)):
        raise FreezeError(f"{path} has no .sha256 sidecar; treat as untrusted")
    want = open(_sidecar(path), encoding="utf-8").read().strip()
    got = CFG.sha256_file(path)
    if want != got:
        raise FreezeError(f"{path} was modified after freezing "
                          f"(sha {got[:12]} != recorded {want[:12]})")
    payload = json.load(open(path, encoding="utf-8"))
    missing = [k for k in FREEZE_REQUIRED if k not in payload]
    if missing:
        raise FreezeError(f"freeze missing {missing}")
    return payload


# ---------------------------------------------------------------------------
# HELDOUT_UNLOCK.json — explicit, separate, and tied to unchanged code
# ---------------------------------------------------------------------------

UNLOCK_PHRASE = "I have finished the development analysis and will not change it"
UNLOCK_NAME = "HELDOUT_UNLOCK.json"


def write_unlock(run_dir: str, freeze_path: str, confirm: str) -> dict:
    """Unlock held-out cells for ONE held-out run directory.

    Refuses unless (1) the phrase is typed exactly, (2) the freeze is intact,
    and (3) the source code is byte-identical to what was frozen -- otherwise
    the analysis being executed is not the one that was frozen.
    """
    if confirm != UNLOCK_PHRASE:
        raise FreezeError(f"unlock requires the exact phrase: {UNLOCK_PHRASE!r}")
    fz = load_freeze(freeze_path)
    drift = frozen_drift(fz)
    if drift:
        kinds = sorted({d.split(":", 1)[0].replace("model_pin", "model pins") for d in drift})
        raise FreezeError(f"{' and '.join(kinds)} changed since the freeze ({len(drift)} "
                          f"items, e.g. {drift[:3]}); held-out evaluation would not run "
                          f"the frozen analysis")
    os.makedirs(run_dir, exist_ok=True)
    path = os.path.join(run_dir, UNLOCK_NAME)
    if os.path.exists(path):
        raise FreezeError(f"{path} already exists")
    rec = {"freeze_path": os.path.abspath(freeze_path),
           "freeze_sha256": CFG.sha256_file(freeze_path),
           "unlocked_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "user": os.environ.get("USER", "unknown"),
           "phrase": confirm}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1)
    os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return rec


def _current_pins() -> dict:
    try:
        with open(os.path.join(CFG.results_root(), "model_pins.json"), encoding="utf-8") as fh:
            return json.load(fh).get("pins", {})
    except (OSError, ValueError):
        return {}


def frozen_drift(fz: dict) -> list[str]:
    """Source files, materials and model pins that now differ from the freeze.

    A pin counts only for models pinned AT freeze time; together with the
    load-time check (loaded snapshot == current pin) it ties every scored model
    to the revision that was frozen.
    """
    now, was = CFG.source_hashes(), fz.get("source_hashes", {})
    out = [f"source:{k}" for k in sorted(set(now) | set(was)) if now.get(k) != was.get(k)]
    want = (fz.get("config_hashes") or {}).get("materials") or {}
    lex = [k[4:-5] for k in want if k.startswith("phi_") and k.endswith(".json")]
    if lex:
        got = CFG.materials_hash(lex)
        out += [f"materials:{k}" for k in sorted(set(got) | set(want))
                if got.get(k) != want.get(k)]
    frozen_pins = fz.get("model_pins") or {}
    if isinstance(frozen_pins, dict) and frozen_pins:
        cur = _current_pins()
        for m, p in sorted(frozen_pins.items()):
            if isinstance(p, dict) and "revision" in p:
                rev = (cur.get(m) or {}).get("revision")
                if rev is not None and rev != p["revision"]:
                    out.append(f"model_pin:{m}")
    return out


_VERIFIED: set[tuple[str, str]] = set()     # (unlock path, freeze sha) checked in this process


def load_unlock(run_dir: str) -> dict:
    """The unlock record -- re-verified against the freeze on EVERY held-out access.

    Checking the code only when unlocking (as first written) left a gap: code
    edited AFTER the unlock still scored held-out cells. Now any source or
    materials drift from the freeze refuses held-out scoring and analysis. The
    check runs once per process (a running process cannot change its code).
    """
    path = os.path.join(run_dir, UNLOCK_NAME)
    if not os.path.isfile(path):
        raise SplitViolation(
            f"held-out cells are locked: {path} does not exist. Freeze the "
            f"development analysis, then run `p33 heldout unlock`.")
    rec = json.load(open(path, encoding="utf-8"))
    fz_path = rec.get("freeze_path", "")
    try:
        fz = load_freeze(fz_path)
    except FreezeError as exc:
        raise SplitViolation(f"unlock refers to an invalid freeze: {exc}") from exc
    if CFG.sha256_file(fz_path) != rec.get("freeze_sha256"):
        raise SplitViolation("the freeze changed after the unlock was written")
    key = (os.path.abspath(path), str(rec.get("freeze_sha256")))
    if key not in _VERIFIED:
        drift = frozen_drift(fz)
        if drift:
            raise SplitViolation(
                f"{len(drift)} source/materials/model-pin item(s) differ from the freeze "
                f"(e.g. {drift[:3]}). Held-out scoring and analysis must run the "
                f"frozen analysis: restore the frozen code (the freeze's `git` "
                f"record) or start a new development run.")
        _VERIFIED.add(key)
    return rec
