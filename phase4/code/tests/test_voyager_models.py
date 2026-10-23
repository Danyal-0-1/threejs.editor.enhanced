"""tools/voyager_models.py, against a stand-in API (no network, no real key)."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import stat
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SECRET = "sk-test-NEVER-WRITE-THIS-1234567890"
TOKEN = re.compile(r"\s?\w+|\s|[^\w\s]+")


def _vm():
    spec = importlib.util.spec_from_file_location(
        "voyager_models", os.path.join(os.path.dirname(HERE), "tools", "voyager_models.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


LISTING = {"object": "list", "data": [
    {"id": "scorer-32b-instruct", "model_type": "chat", "context_window": 32768, "quantization": "bf16",
     "supports_function_calling": True, "supports_vision": False, "description": "A 32B model."},
    {"id": "chatonly-27b", "model_type": "chat", "context_window": 131072, "quantization": "fp8",
     "supports_function_calling": False, "supports_vision": True, "description": "Chat only."},
    {"id": "fam-7b", "model_type": "chat", "description": "Set reasoning effort to choose.",
     "family": {"default_level": "none",
                "members": {"none": "fam-7b-instruct", "low": "fam-7b-think", "high": "fam-7b-think"}}},
    {"id": "draft-model", "model_type": "chat", "description": "A draft model, not meant for direct use."},
    {"id": "text-embedding-x", "model_type": "embedding", "context_window": 8192},
]}


def _lp(ctx, tid):
    h = int(hashlib.sha1(json.dumps([ctx[-6:], tid]).encode()).hexdigest()[:6], 16)
    return -round((h % 4000) / 400.0 * 16) / 16 - 0.0625          # bf16-like: multiples of 1/16


def _fake_api(calls):
    def request(key, method, path, body=None, **kw):
        calls.append((key, method, path, dict(body or {})))
        assert key == SECRET
        if path == "/models":
            return 200, LISTING
        model = body["model"]
        if path == "/chat/completions":
            ch = {"message": {"role": "assistant", "content": "ready"}}
            if body.get("logprobs"):
                ch["logprobs"] = {"content": [{"token": "ready", "logprob": -0.1,
                                               "top_logprobs": [{"token": "ready", "logprob": -0.1}] * 5}]}
            return 200, {"model": model, "choices": [ch]}
        if path == "/completions":
            if model == "chatonly-27b":
                return 404, "completions not served for this model"
            toks = TOKEN.findall(body["prompt"])
            ids = [100 + int(hashlib.sha1(t.encode()).hexdigest()[:6], 16) % 9000 for t in toks]
            ch = {"text": "    return a + b"}
            if body.get("return_token_ids"):
                ch["prompt_token_ids"] = ids
            if body.get("prompt_logprobs") is not None:
                ch["prompt_logprobs"] = [None] + [{str(ids[j]): {"logprob": _lp(ids[:j], ids[j])}}
                                                  for j in range(1, len(ids))]
            return 200, {"model": model, "system_fingerprint": "vllm-test-1", "choices": [ch]}
        return 404, "unknown path"
    return request


def test_a_key_file_others_can_read_is_refused():
    vm = _vm()
    d = tempfile.mkdtemp()
    f = os.path.join(d, "llm_api_key")
    open(f, "w").write(SECRET)
    os.chmod(f, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)
    vm.KEY_FILE = f
    saved = os.environ.pop("ASU_RC_API_KEY", None)
    try:
        try:
            vm.load_key()
        except vm.NoKey as e:
            assert "chmod 600" in str(e) and SECRET not in str(e)
        else:
            raise AssertionError("a group-readable key file was accepted")
        os.chmod(f, stat.S_IRUSR | stat.S_IWUSR)
        assert vm.load_key() == SECRET
    finally:
        if saved is not None:
            os.environ["ASU_RC_API_KEY"] = saved


def test_the_key_never_reaches_an_output_file_and_the_prompts_are_neutral():
    vm = _vm()
    calls = []
    vm.request = _fake_api(calls)
    out = tempfile.mkdtemp()
    saved = os.environ.get("ASU_RC_API_KEY")
    os.environ["ASU_RC_API_KEY"] = SECRET
    try:
        assert vm.main(["list", "--out", out]) == 0
        assert vm.main(["probe", "--out", out, "--workers", "2"]) == 0
    finally:
        if saved is None:
            os.environ.pop("ASU_RC_API_KEY", None)
        else:
            os.environ["ASU_RC_API_KEY"] = saved
    files = os.listdir(out)
    assert any(f.startswith("models_") for f in files) and any(f.startswith("probe_") for f in files)
    for f in files:
        assert SECRET not in open(os.path.join(out, f), encoding="utf-8").read(), f
    probed = {c[3].get("model") for c in calls if c[2] != "/models"}
    assert probed == {"scorer-32b-instruct", "chatonly-27b", "fam-7b-instruct", "fam-7b-think"}, probed
    for c in calls:                                      # neutral prompts only
        text = str(c[3])
        assert "$S" not in text and "phi" not in text.lower()


def test_the_probe_reads_what_each_model_can_serve():
    vm = _vm()
    vm.request = _fake_api([])
    full = vm.probe_model(SECRET, "scorer-32b-instruct")
    assert full["serves"] == {"arm_a": True, "arm_b": True, "chat": True, "first_token_logprobs": True}
    mg = full["margins"]
    assert mg["repeatable"] and mg["resolution_log2"] is not None and mg["resolution_log2"] <= 4
    assert full["prompt_logprobs"]["served"] == "scorer-32b-instruct"
    assert full["raw_generation"]["deterministic"]
    chat = vm.probe_model(SECRET, "chatonly-27b")
    assert chat["serves"]["chat"] and not chat["serves"]["arm_a"] and not chat["serves"]["arm_b"]
    assert chat["prompt_logprobs"]["status"] == 404


def test_margin_resolution_tells_rounded_logits_from_full_precision():
    vm = _vm()
    assert vm.resolution([-1.125, 0.5, 3.0625]) == 4
    assert vm.resolution([0.123456789, -2.718281828, 1.414213562]) is None
    assert vm.resolution([0.0, 0.0]) is None


def test_the_model_table_reads_the_documented_fields():
    vm = _vm()
    rows = vm.models_table(LISTING)
    assert [r["id"] for r in rows] == ["chatonly-27b", "draft-model", "fam-7b", "scorer-32b-instruct",
                                       "text-embedding-x"]
    r = rows[3]
    assert (r["type"], r["context"], r["tools"], r["vision"], r["served as"]) == ("chat", "32768", "yes", "no", "bf16")
    assert rows[2]["members"] == "fam-7b-instruct, fam-7b-think"
