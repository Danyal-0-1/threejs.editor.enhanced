"""Split locks, the immutable development freeze, and the held-out unlock."""

from __future__ import annotations

import json
import os
import stat

import _helpers as H

from p33 import config as CFG
from p33 import pipeline as PL
from p33 import splits

PHRASE = splits.UNLOCK_PHRASE


def _raises(fn, exc, contains=""):
    try:
        fn()
    except exc as e:
        assert contains in str(e), f"{contains!r} not in {e}"
        return
    raise AssertionError(f"expected {exc.__name__}")


# ---------------------------------------------------------------------------
# classification
# ---------------------------------------------------------------------------

def test_registered_split_classification():
    c = splits.classify
    assert c("dom", "d50s1", H.DEV_BASE).kind == "dev"
    assert c("dom", "d75s1a", H.DEV_BASE).kind == "heldout_mapping"
    assert c("dom", "d50s1", "deepseek-ai/deepseek-coder-1.3b-base").kind == "heldout_model"
    assert c("dom", "d50s1", "Qwen/Qwen2.5-Coder-3B").kind == "heldout_model_weakened"
    assert c("blk", "d50s1", H.DEV_BASE).kind == "exploratory_contaminated"
    assert c("blk", "d75s1a", H.DEV_BASE).kind == "heldout_weak_family"
    assert c("dom", "d50s1", "Qwen/Qwen2.5-Coder-7B").kind == "forbidden"
    assert c("dom", "alpha", H.DEV_BASE).kind == "forbidden"
    assert c("newfam", "d50s1", H.DEV_BASE).kind == "forbidden"


def test_blk_is_never_labelled_a_heldout_grammar():
    for lx in splits.DEV_LEXICONS | splits.HELDOUT_LEXICONS:
        cc = splits.classify("blk", lx, H.DEV_BASE)
        assert cc.label != "HELDOUT", (lx, cc)


def test_no_model_above_3b_in_any_stage():
    for stage in ("smoke", "dev", "heldout"):
        _raises(lambda: splits.check_access(stage, "dom", "d50s1", "Qwen/Qwen2.5-Coder-7B"),
                splits.SplitViolation, "3B")


# ---------------------------------------------------------------------------
# accidental held-out access
# ---------------------------------------------------------------------------

def test_dev_stage_refuses_a_heldout_mapping():
    _raises(lambda: splits.check_access("dev", "dom", "d75s1a", H.DEV_BASE),
            splits.SplitViolation, "development cells only")


def test_dev_stage_refuses_a_heldout_model():
    _raises(lambda: splits.check_access("dev", "dom", "d50s1", "deepseek-ai/deepseek-coder-1.3b-base"),
            splits.SplitViolation)


def test_contaminated_cell_needs_explicit_permission():
    _raises(lambda: splits.check_access("dev", "blk", "d50s1", H.DEV_BASE),
            splits.SplitViolation, "EXPLORATORY")
    cc = splits.check_access("dev", "blk", "d50s1", H.DEV_BASE, allow_exploratory=True)
    assert cc.label == "EXPLORATORY"


def test_heldout_stage_refuses_without_unlock():
    rd = H.tmpdir()
    _raises(lambda: splits.check_access("heldout", "dom", "d75s1a", H.DEV_BASE, run_dir=rd),
            splits.SplitViolation, "locked")


def test_heldout_stage_refuses_development_cells():
    _raises(lambda: splits.check_access("heldout", "dom", "d50s1", H.DEV_BASE, run_dir=H.tmpdir()),
            splits.SplitViolation, "dev run")


def test_plan_refuses_before_enumerating_any_heldout_site():
    """The split check happens before a single held-out site is classified."""
    cfg = H.small_cfg(lexicons=("d50s1", "d75s1a"))
    import phase3_2.sites2 as S
    calls = {"n": 0}
    orig = S.classify

    def spy(*a, **k):
        calls["n"] += 1
        return orig(*a, **k)
    PL.S.classify = spy
    try:
        _raises(lambda: PL.build_plan(cfg, site_limit=0), splits.SplitViolation)
    finally:
        PL.S.classify = orig
    assert calls["n"] == 0, "sites were enumerated before the split check"


# ---------------------------------------------------------------------------
# DEV_FREEZE.json
# ---------------------------------------------------------------------------

def _payload():
    return {k: {"x": 1} for k in splits.FREEZE_REQUIRED} | {
        "source_hashes": CFG.source_hashes(), "dev_run_id": "dev-x",
        "timestamp_utc": "2026-10-05T00:00:00+00:00"}


def test_freeze_is_written_read_only_with_a_sidecar():
    p = os.path.join(H.tmpdir(), "DEV_FREEZE.json")
    splits.write_freeze(p, _payload())
    mode = os.stat(p).st_mode
    assert not mode & stat.S_IWUSR and os.path.exists(p + ".sha256")
    assert splits.load_freeze(p)["dev_run_id"] == "dev-x"


def test_freeze_cannot_be_written_twice():
    p = os.path.join(H.tmpdir(), "DEV_FREEZE.json")
    splits.write_freeze(p, _payload())
    _raises(lambda: splits.write_freeze(p, _payload()), splits.FreezeError, "immutable")


def test_tampered_freeze_is_detected():
    p = os.path.join(H.tmpdir(), "DEV_FREEZE.json")
    splits.write_freeze(p, _payload())
    os.chmod(p, 0o644)
    with open(p, "a") as fh:
        fh.write(" ")
    _raises(lambda: splits.load_freeze(p), splits.FreezeError, "modified after freezing")


def test_freeze_requires_every_field():
    p = os.path.join(H.tmpdir(), "DEV_FREEZE.json")
    bad = _payload()
    del bad["calibration"]
    _raises(lambda: splits.write_freeze(p, bad), splits.FreezeError, "calibration")


# ---------------------------------------------------------------------------
# unlock
# ---------------------------------------------------------------------------

def _frozen():
    d = H.tmpdir()
    p = os.path.join(d, "DEV_FREEZE.json")
    splits.write_freeze(p, _payload())
    return p


def test_unlock_needs_the_exact_phrase():
    _raises(lambda: splits.write_unlock(H.tmpdir(), _frozen(), "yes"), splits.FreezeError, "phrase")


def test_unlock_refuses_if_source_changed_since_freeze():
    fz = _frozen()
    orig = CFG.source_hashes
    CFG.source_hashes = lambda: {**orig(), "phase3_2/sol/src/p33/h4.py": "0" * 64}
    try:
        _raises(lambda: splits.write_unlock(H.tmpdir(), fz, PHRASE),
                splits.FreezeError, "source changed")
    finally:
        CFG.source_hashes = orig


def test_heldout_access_refuses_if_source_changes_after_unlock():
    """The frozen analysis must be the one EXECUTED, not only the one unlocked:
    an edit made after the unlock refuses every later held-out access."""
    rd = H.tmpdir()
    splits.write_unlock(rd, _frozen(), PHRASE)
    orig = CFG.source_hashes
    CFG.source_hashes = lambda: {**orig(), "phase3_2/sol/src/p33/kstar.py": "0" * 64}
    try:
        _raises(lambda: splits.check_access("heldout", "dom", "d75s1a", H.DEV_BASE, run_dir=rd),
                splits.SplitViolation, "differ from the freeze")
    finally:
        CFG.source_hashes = orig


def test_a_model_repinned_after_the_freeze_is_refused():
    """The frozen analysis includes WHICH revision of each model is scored."""
    m = H.DEV_BASE
    fz = os.path.join(H.tmpdir(), "DEV_FREEZE.json")
    splits.write_freeze(fz, _payload() | {"model_pins": {m: {"revision": "rev-frozen"}}})
    pins = os.path.join(CFG.results_root(), "model_pins.json")
    saved = open(pins).read() if os.path.exists(pins) else None
    os.makedirs(os.path.dirname(pins), exist_ok=True)
    try:
        json.dump({"pins": {m: {"revision": "rev-frozen"}}}, open(pins, "w"))
        rd = H.tmpdir()
        splits.write_unlock(rd, fz, PHRASE)                       # same pin: allowed
        json.dump({"pins": {m: {"revision": "rev-NEW"}}}, open(pins, "w"))
        _raises(lambda: splits.write_unlock(H.tmpdir(), fz, PHRASE),
                splits.FreezeError, "model pins changed")
        splits._VERIFIED.clear()                                  # a fresh process
        _raises(lambda: splits.check_access("heldout", "dom", "d75s1a", m, run_dir=rd),
                splits.SplitViolation, "differ from the freeze")
    finally:
        splits._VERIFIED.clear()
        if saved is None:
            os.remove(pins)
        else:
            open(pins, "w").write(saved)


def test_unlock_then_heldout_access_is_permitted():
    rd = H.tmpdir()
    splits.write_unlock(rd, _frozen(), PHRASE)
    cc = splits.check_access("heldout", "dom", "d75s1a", H.DEV_BASE, run_dir=rd)
    assert cc.kind == "heldout_mapping"


def test_unlock_is_void_if_the_freeze_is_later_tampered():
    rd = H.tmpdir()
    fz = _frozen()
    splits.write_unlock(rd, fz, PHRASE)
    os.chmod(fz, 0o644)
    with open(fz, "a") as fh:
        fh.write("\n")
    _raises(lambda: splits.check_access("heldout", "dom", "d75s1a", H.DEV_BASE, run_dir=rd),
            splits.SplitViolation, "invalid freeze")


def test_run_ids_physically_separate_stages():
    cfg = H.small_cfg(run_id="heldout-oops")
    _raises(cfg.validate, ValueError, "physically separated")
