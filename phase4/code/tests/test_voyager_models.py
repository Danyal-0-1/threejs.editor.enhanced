"""tools/voyager_models.py, against a stand-in API (no network, no real key)."""

from __future__ import annotations

import importlib.util
import os
import stat
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SECRET = "sk-test-NEVER-WRITE-THIS-1234567890"


def _vm():
    spec = importlib.util.spec_from_file_location(
        "voyager_models", os.path.join(os.path.dirname(HERE), "tools", "voyager_models.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


LISTING = {"object": "list", "data": [
    {"id": "scorer-32b-instruct", "model_type": "chat", "context_window": 32768,
     "supports_function_calling": True, "supports_vision": False},
    {"id": "chatonly-27b", "model_type": "chat", "context_window": 131072,
     "supports_function_calling": False, "supports_vision": True},
    {"id": "text-embedding-x", "model_type": "embedding", "context_window": 8192},
]}


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
            return 200, {"choices": [ch]}
        if path == "/completions":
            if model == "chatonly-27b":
                return 404, "completions not served for this model"
            if body.get("echo"):
                return 200, {"choices": [{"text": " Paris", "logprobs": {
                    "token_logprobs": [None, -3.2, -1.1, -0.4, -0.2, -0.05]}}]}
            return 200, {"choices": [{"text": " Paris"}]}
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


def test_the_key_never_reaches_an_output_file():
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
    assert "text-embedding-x" not in probed, "a non-text model was probed"
    for c in calls:                                      # neutral prompts only
        text = str(c[3])
        assert "$S" not in text and "phi" not in text.lower()


def test_the_probe_reads_what_each_model_can_serve():
    vm = _vm()
    vm.request = _fake_api([])
    full = vm.probe_model(SECRET, "scorer-32b-instruct")
    assert full["serves"] == {"arm_b": True, "arm_a": True, "first_token_logprobs": True}
    assert full["prompt_logprobs"]["via"] == "echo" and full["prompt_logprobs"]["scored_tokens"] == 5
    chat = vm.probe_model(SECRET, "chatonly-27b")
    assert chat["serves"]["arm_b"] and not chat["serves"]["arm_a"]
    assert chat["completions"]["status"] == 404


def test_the_model_table_reads_the_documented_fields():
    vm = _vm()
    rows = vm.models_table(LISTING)
    assert [r["id"] for r in rows] == ["chatonly-27b", "scorer-32b-instruct", "text-embedding-x"]
    r = rows[1]
    assert (r["type"], r["context"], r["tools"], r["vision"]) == ("chat", "32768", "yes", "no")
