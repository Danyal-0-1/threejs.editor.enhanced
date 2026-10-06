"""Crash safety: atomic shards, resume, duplicates, corruption, missing cells,
deterministic merge, incompatible configuration, provenance binding."""

from __future__ import annotations

import glob
import json
import os
import time

import _helpers as H

from p33 import pipeline as PL
from p33 import shards
from p33.fakes import ExplodingScorer, FakeScorer


def _rows(n, tag="a"):
    return [{"row_key": f"k{i:03d}", "v": i, "tag": tag} for i in range(n)]


def test_atomic_write_then_done():
    st = shards.ShardStore(H.tmpdir(), "x")
    st.write("c1", {"f": 1}, _rows(5))
    assert st.is_done("c1")
    assert not glob.glob(os.path.join(st.shard_dir, "*.tmp.*"))


def test_abandoned_temp_file_is_not_a_shard():
    st = shards.ShardStore(H.tmpdir(), "x")
    p = os.path.join(st.shard_dir, "c1.jsonl.tmp.999")
    open(p, "w").write('{"row_key":"k"}\n')
    assert st.status("c1").state == "missing"
    assert st.clean_temp() == 0, "a fresh temp may be another array task's write in flight"
    old = time.time() - 3600
    os.utime(p, (old, old))
    assert st.clean_temp() == 1


def test_concurrent_writers_never_share_a_temp_file():
    """P33-014: array tasks write the same plan/arms file at the same moment, on
    different nodes that can share a pid. Threads share one pid: the collision
    the old `.tmp.<pid>` / fixed `.tmp` names allowed."""
    import threading
    from p33 import config as CFG
    path = os.path.join(H.tmpdir(), "plan_arm_a.json")
    texts = [json.dumps({"writer": i, "pad": "x" * 200_000}) for i in range(8)]
    errors = []

    def writer(text):
        try:
            for _ in range(5):
                CFG.atomic_write_text(path, text)
        except Exception as exc:                  # noqa: BLE001 -- collected below
            errors.append(repr(exc))
    threads = [threading.Thread(target=writer, args=(t,)) for t in texts]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, errors
    assert open(path).read() in texts, "a reader saw an interleaved file"
    assert not glob.glob(path + ".tmp*"), "temp file left behind"


def test_corrupt_shard_detected_quarantined_and_rewritable():
    st = shards.ShardStore(H.tmpdir(), "x")
    st.write("c1", {}, _rows(4))
    with open(st.shard_path("c1"), "a") as fh:
        fh.write('{"row_key":"evil"}\n')
    assert st.status("c1").state == "corrupt"
    st.quarantine("c1")
    assert st.status("c1").state == "missing"
    st.write("c1", {}, _rows(4))
    assert st.is_done("c1")


def test_marker_without_shard_is_corrupt():
    st = shards.ShardStore(H.tmpdir(), "x")
    st.write("c1", {}, _rows(2))
    os.remove(st.shard_path("c1"))
    assert st.status("c1").state == "corrupt"


def test_identical_duplicates_dropped_conflicting_refused():
    st = shards.ShardStore(H.tmpdir(), "x")
    st.write("c1", {}, _rows(3))
    st.write("c2", {}, _rows(3))                      # identical rows, other cell
    res = st.merge(["c1", "c2"])
    assert len(res.rows) == 3 and res.duplicates_dropped == 3
    st.write("c3", {}, _rows(3, tag="b"))             # same keys, different content
    try:
        st.merge(["c1", "c3"])
    except ValueError as exc:
        assert "conflicting" in str(exc)
    else:
        raise AssertionError("conflicting duplicates were merged")


def test_missing_and_failed_cells_are_reported_partial():
    st = shards.ShardStore(H.tmpdir(), "x")
    st.write("c1", {}, _rows(2))
    st.record_failure("c2", {}, RuntimeError("CUDA out of memory"))
    res = st.merge(["c1", "c2", "c3"])
    assert res.status == "PARTIAL"
    assert res.failed == ["c2"] and res.missing == ["c3"]
    rec = json.load(open(st.failed_path("c2")))
    assert rec["kind"] == "OOM"


def test_merge_is_byte_deterministic():
    a, b = H.tmpdir(), H.tmpdir()
    for d, order in ((a, ["c1", "c2"]), (b, ["c2", "c1"])):
        st = shards.ShardStore(d, "x")
        for c in order:
            st.write(c, {}, [{"row_key": f"{c}|{i}", "v": i} for i in range(3)])
        st.write_merged(st.merge(["c1", "c2"]))
    pa = open(os.path.join(a, "merged", "x.jsonl"), "rb").read()
    pb = open(os.path.join(b, "merged", "x.jsonl"), "rb").read()
    assert pa == pb


def test_incompatible_configuration_is_rejected():
    rd = H.tmpdir()
    cfg = H.small_cfg()
    shards.assert_compatible(rd, cfg)
    cfg2 = H.small_cfg()
    cfg2.primary["ladder"] = [0, 1, 2]
    try:
        shards.assert_compatible(rd, cfg2)
    except RuntimeError as exc:
        assert "incompatible" in str(exc)
    else:
        raise AssertionError("a changed ladder resumed into the old run")


def test_rename_does_not_invalidate_a_run():
    a, b = H.small_cfg(run_id="dev-a"), H.small_cfg(run_id="dev-b")
    assert a.config_hash() == b.config_hash()


# ---------------------------------------------------------------------------
# interruption and resume through the real runner
# ---------------------------------------------------------------------------

def _run_all(rd, cfg, factory, exp="arm_a"):
    pins = H.fake_pins(cfg)
    st = PL.run(cfg, rd, exp, scorer_factory=factory, pins=pins)
    return st, PL.merge(cfg, rd, exp, pins=pins)


def test_crash_mid_run_then_resume_completes_without_duplicates():
    cfg = H.small_cfg(models=(H.DEV_BASE,))
    rd = H.tmpdir()
    st, res = _run_all(rd, cfg, lambda m: ExplodingScorer(m, fail_after=20))
    assert st == "PARTIAL" and res.status == "PARTIAL" and res.failed
    st2, res2 = _run_all(rd, cfg, lambda m: FakeScorer(m))
    assert st2 == "COMPLETE" and res2.status == "COMPLETE"
    keys = [r["row_key"] for r in res2.rows]
    assert len(keys) == len(set(keys))


def test_signal_interruption_leaves_finished_cells_and_resumes():
    cfg = H.small_cfg(models=(H.DEV_BASE,))
    rd = H.tmpdir()

    class Stopper(FakeScorer):
        def score_pair_detailed(self, *a, **k):
            if self.calls == 30:
                PL._handler(15, None)                 # SIGTERM arrives
            return super().score_pair_detailed(*a, **k)
    st, res = _run_all(rd, cfg, lambda m: Stopper(m))
    PL.reset_stop()
    assert st == "INTERRUPTED"
    assert 0 < len(res.done) < res.n_expected
    man = [json.load(open(p)) for p in glob.glob(os.path.join(rd, "manifests", "job_*.json"))]
    assert any(m["status"] == "INTERRUPTED" for m in man)
    st2, res2 = _run_all(rd, cfg, lambda m: FakeScorer(m))
    assert st2 == "COMPLETE" and res2.status == "COMPLETE"


def test_resumed_output_equals_uninterrupted_output():
    cfg = H.small_cfg(models=(H.DEV_BASE, H.DEV_INST))
    clean, broken = H.tmpdir(), H.tmpdir()
    for exp in ("arm_a", "primary"):
        _run_all(clean, cfg, lambda m: FakeScorer(m), exp)
        _run_all(broken, cfg, lambda m: ExplodingScorer(m, fail_after=37), exp)
        _run_all(broken, cfg, lambda m: FakeScorer(m), exp)
    for exp in ("arm_a", "primary"):
        a = open(os.path.join(clean, "merged", f"{exp}.jsonl"), "rb").read()
        b = open(os.path.join(broken, "merged", f"{exp}.jsonl"), "rb").read()
        assert a == b, f"{exp}: resumed output differs from uninterrupted output"


def test_status_is_read_only_so_validate_still_passes():
    """P33-017: `status` created raw/shards/armb, so a never-run Arm B became a
    started, EMPTY experiment and `validate` -- and with it `dev_freeze` -- refused.
    Runs the real CLI in the order the README gives."""
    import importlib.util
    from p33 import config as CFG
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "scripts", "p33.py")
    spec = importlib.util.spec_from_file_location("p33cli_status", path)
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    rid = "dev-status-readonly"
    cfg_path = os.path.join(H.tmpdir(), "cfg.json")
    json.dump(H.small_cfg(run_id=rid).to_dict(), open(cfg_path, "w"))
    saved = os.environ.get("P33_FAKE")
    os.environ["P33_FAKE"] = "1"
    try:
        assert cli.main(["dev", "init", "--config", cfg_path, "--run", rid]) == 0
        assert cli.main(["dev", "run", "--run", rid, "--experiment", "arm_a"]) == 0
        assert cli.main(["status", "--run", rid]) == 0
        assert not os.path.isdir(os.path.join(CFG.run_dir(rid), "raw", "shards", "armb"))
        assert cli.main(["validate", "--run", rid]) == 0
    finally:
        if saved is None:
            os.environ.pop("P33_FAKE", None)
        else:
            os.environ["P33_FAKE"] = saved


def test_array_task_i_scores_model_i_even_when_resubmitted_alone():
    """P33-012: `--array=1` alone gave SLURM_ARRAY_TASK_COUNT=1, and the old
    stride `i % 1 == 1` selected no model, so the resubmission scored nothing."""
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "scripts", "p33.py")
    spec = importlib.util.spec_from_file_location("p33cli_array", path)
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    keys = ("SLURM_ARRAY_TASK_ID", "SLURM_ARRAY_TASK_COUNT")
    saved = {k: os.environ.get(k) for k in keys}
    os.environ.update(SLURM_ARRAY_TASK_ID="1", SLURM_ARRAY_TASK_COUNT="1")
    try:
        task, n = cli.task_args(type("A", (), {"task": None, "n_tasks": None})())
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    cfg = H.small_cfg(models=(H.DEV_BASE, H.DEV_INST))
    assert PL.assigned_models(cfg.models, task, n) == [H.DEV_INST]
    # Arm B applies to instruct models only: task 0 is the base model -> no-op
    rd, pins = H.tmpdir(), H.fake_pins(cfg)
    PL.run(cfg, rd, "armb", scorer_factory=lambda m: FakeScorer(m), pins=pins, task=0)
    assert not PL.merge(cfg, rd, "armb", pins=pins).done
    PL.run(cfg, rd, "armb", scorer_factory=lambda m: FakeScorer(m), pins=pins, task=1)
    assert PL.merge(cfg, rd, "armb", pins=pins).status == "COMPLETE"


def test_wrong_revision_is_refused():
    cfg = H.small_cfg(models=(H.DEV_BASE,))
    pins = {H.DEV_BASE: {"revision": "a-different-revision"}}
    try:
        PL.run(cfg, H.tmpdir(), "arm_a", scorer_factory=lambda m: FakeScorer(m), pins=pins)
    except RuntimeError as exc:
        assert "pinned" in str(exc)
    else:
        raise AssertionError("a model with the wrong revision was scored")


def test_unpinned_model_is_refused():
    cfg = H.small_cfg(models=(H.DEV_BASE,))
    try:
        PL.run(cfg, H.tmpdir(), "arm_a", scorer_factory=lambda m: FakeScorer(m), pins={})
    except RuntimeError as exc:
        assert "not pinned" in str(exc)
    else:
        raise AssertionError("an unpinned model was scored")


# ---------------------------------------------------------------------------
# provenance binding
# ---------------------------------------------------------------------------

def test_provenance_is_bound_to_every_job_and_shard():
    cfg = H.small_cfg(models=(H.DEV_BASE,))
    rd = H.tmpdir()
    _run_all(rd, cfg, lambda m: FakeScorer(m))
    man = [json.load(open(p)) for p in glob.glob(os.path.join(rd, "manifests", "job_*.json"))]
    assert len(man) == 1
    m = man[0]
    for k in ("git_commit", "git_dirty", "command", "config", "config_hash", "seeds",
              "packages", "gpu", "dtype", "slurm", "source_hashes", "materials_hashes",
              "models", "prompt_hashes", "start_utc", "end_utc", "status", "schema_version"):
        assert k in m, k
    assert m["status"] == "COMPLETE" and m["models"][H.DEV_BASE]["revision"] == "fakerev0001"
    assert m["prompt_hashes"]
    marker = json.load(open(glob.glob(os.path.join(rd, "checkpoints", "arm_a", "*.done.json"))[0]))
    assert "job" in marker and "host" in marker and marker["sha256"]


def test_every_row_carries_its_split_revision_and_prompt():
    cfg = H.small_cfg(models=(H.DEV_BASE,))
    _, res = _run_all(H.tmpdir(), cfg, lambda m: FakeScorer(m))
    for r in res.rows:
        assert r["split"] == "DEVELOPMENT" and r["model_revision"] == "fakerev0001"
        assert r["prompt_sha"] and r["tokenizer_id"] and r["schema_version"] == "p33/1"
