"""The scorer for models served by the ASU RC LLM API (p4/scoring/api.py), against a stand-in
vLLM server: no network, no real key. Plus its plumbing: registry, split, prefetch, preflight,
the pipeline, and the key never reaching an output."""

from __future__ import annotations

import hashlib
import http.server
import json
import os
import re
import threading

import _helpers as H

from p4.experiments import armb, h5, pipeline as PL  # noqa: F401  (armb, h5 register)
from p4.governance import registry, splits
from p4.runtime import asu_api as API, prefetch, preflight
from p4.scoring import api as A
from p4.scoring.margins import IdenticalCandidates, NoContext, ZeroLengthSpan

MODEL = "asu-rc/olmo3-7b-instruct"
SERVED = "olmo3-7b-instruct"
KEY = "sk-test-NEVER-WRITE-THIS-0987654321"
TOKEN = re.compile(r"\s?\w+|\s|[^\w\s]+")       # runs of punctuation are ONE token: ('# merges


def _tid(tok: str) -> int:
    return 100 + int(hashlib.sha1(tok.encode()).hexdigest()[:8], 16) % 50000


def _lp(ctx: list[int], tid: int) -> float:
    """Deterministic, and rounded to 1/16 like the served bf16 logits."""
    h = int(hashlib.sha1(json.dumps([ctx[-8:], tid]).encode()).hexdigest()[:6], 16)
    return -round((h % 4000) / 400.0 * 16) / 16 - 0.0625


class FakeVLLM:
    """The parts of vLLM's /v1/completions answer the scorer reads, and a log of every request."""

    def __init__(self, served=SERVED, fingerprint="vllm-test-0001", bos=False):
        self.served, self.fingerprint, self.bos = served, fingerprint, bos
        self.calls: list[dict] = []

    def tokens(self, text, special):
        toks = TOKEN.findall(text)
        ids = [_tid(t) for t in toks]
        if special and self.bos:
            return [1] + ids, ["<s>"] + toks
        return ids, toks

    def __call__(self, key, method, path, body=None, **kw):
        assert key == KEY and method == "POST" and path == "/completions"
        self.calls.append(dict(body))
        ids, toks = self.tokens(body["prompt"], body.get("add_special_tokens", True))
        ch = {"index": 0, "text": "    return a + b\n" if body["max_tokens"] > 1 else "."}
        if body.get("return_token_ids"):
            ch["prompt_token_ids"] = ids
        if body.get("prompt_logprobs") is not None:
            ch["prompt_logprobs"] = [None] + [
                {str(ids[j]): {"logprob": _lp(ids[:j], ids[j]), "rank": 1, "decoded_token": toks[j]}}
                for j in range(1, len(ids))]
        return 200, {"model": self.served, "system_fingerprint": self.fingerprint, "choices": [ch]}


def _scorer(fake=None, pin=None):
    fake = fake or FakeVLLM()
    return A.APIScorer.for_model(MODEL, pin=pin, key=KEY, transport=fake), fake


def _reference(fake, prefix, c, q):
    """margins.py's algorithm, computed directly from the stand-in model."""
    a, _ = fake.tokens(prefix + c, False)
    b, _ = fake.tokens(prefix + q, False)
    k = next(i for i, (x, y) in enumerate(zip(a, b)) if x != y)
    return (sum(_lp(a[:j], a[j]) for j in range(k, len(a))),
            sum(_lp(b[:j], b[j]) for j in range(k, len(b))), k)


def _raises(fn, exc, text=""):
    try:
        fn()
    except exc as e:
        assert text in str(e), str(e)
    else:
        raise AssertionError(f"expected {exc.__name__}")


# ------------------------------------------------------------------ the measurement

def test_the_margin_is_margins_py_algorithm_on_the_served_tokens():
    sc, fake = _scorer()
    prefix = "$S('.wheel').scale(2).move"
    ps = sc.score_pair_detailed(prefix, "(1, 2)", " left")
    lc, lq, k = _reference(fake, prefix, "(1, 2)", " left")
    assert (ps.logp_correct, ps.logp_competitor, ps.k_common) == (lc, lq, k)
    assert ps.m_seq == lc - lq and ps.fp32_head is False
    scoring = [c for c in fake.calls if c.get("prompt_logprobs") == 0]
    assert len(scoring) == 2 and all(c["add_special_tokens"] is False and c["temperature"] == 0
                                     and c["return_token_ids"] for c in scoring)
    assert ps.first_div_correct_str == "(" and ps.first_div_competitor_str == " left"


def test_special_tokens_stay_off_even_where_the_server_would_add_them():
    sc, fake = _scorer(FakeVLLM(bos=True))
    ps = sc.score_pair_detailed("x = foo", " bar", " baz")
    assert ps.k_common == len(fake.tokens("x = foo", False)[0])      # no BOS in front
    assert all(c["add_special_tokens"] is False for c in fake.calls)


def test_the_refusals_are_margins_pys():
    sc, _ = _scorer()
    _raises(lambda: sc.score_pair_detailed("a b", " c", " c"), IdenticalCandidates)
    _raises(lambda: sc.score_pair_detailed("a b", " c", " c d"), ZeroLengthSpan)
    _raises(lambda: sc.score_pair_detailed("", "x", "y"), NoContext)


def test_merged_is_flagged_when_the_candidate_joins_the_prefix_token():
    sc, _ = _scorer()
    ps = sc.score_pair_detailed("$S('", "#", ".")            # ('# and (' . are single tokens
    assert ps.merged and ps.n_tok_correct == 1
    assert not sc.score_pair_detailed("go to the", " road", " river").merged


def test_program_nll_ids_and_generation():
    sc, fake = _scorer()
    text = "$S('#cube').move(1, 2);"
    ids, _ = fake.tokens(text, False)
    nl = sc.program_nll(text)
    assert nl["n_scored"] == len(ids) - 1
    assert nl["nll"] == -sum(_lp(ids[:j], ids[j]) for j in range(1, len(ids)))
    n = len(fake.calls)
    assert sc.ids(text) == ids and sc.ids(text) == ids and len(fake.calls) == n + 1   # cached
    out = sc.generate("def add(a, b):\n", max_new_tokens=192)
    g = fake.calls[-1]
    assert out == "    return a + b\n"
    assert (g["temperature"], g["max_tokens"], g["add_special_tokens"]) == (0, 192, True)


# ------------------------------------------------------------------ identity

def test_an_answer_from_another_deployment_is_refused():
    sc, fake = _scorer()
    assert sc.revision == f"{SERVED}@vllm-test-0001" and sc.tokenizer_id.startswith("api-")
    fake.fingerprint = "vllm-test-0002"                     # the server was redeployed mid-run
    _raises(lambda: sc.score_pair_detailed("go to the", " road", " river"),
            A.ServedModelChanged, "bound to")
    _raises(lambda: _scorer(FakeVLLM(fingerprint="vllm-test-0003"),
                            pin={"revision": f"{SERVED}@vllm-test-0001"}),
            A.ServedModelChanged, "is pinned")


def test_prefetch_pins_the_answering_deployment_and_keeps_it():
    saved = API.request
    out = os.path.join(H.tmpdir(), "model_pins.json")
    os.environ["ASU_RC_API_KEY"] = KEY
    try:
        API.request = FakeVLLM()
        res = prefetch.run([MODEL], dry_run=False, verify_only_mode=False, checksums=False,
                           out_path=out, api=object())       # an HF client here would be an error
        pin = json.load(open(out))["pins"][MODEL]
        assert pin["revision"] == f"{SERVED}@vllm-test-0001" and pin["serving"] == "api"
        assert res["failed"] == {} and KEY not in open(out).read()
        API.request = FakeVLLM(fingerprint="vllm-test-0009")   # redeployed: the pin is kept
        prefetch.run([MODEL], dry_run=False, verify_only_mode=False, checksums=False, out_path=out)
        assert json.load(open(out))["pins"][MODEL]["revision"] == f"{SERVED}@vllm-test-0001"
        checks = preflight.model_checks([MODEL], json.load(open(out))["pins"])
        assert checks[0]["result"] == "FAIL" and "vllm-test-0009" in checks[0]["detail"]
        API.request = FakeVLLM()
        assert preflight.model_checks([MODEL], json.load(open(out))["pins"])[0]["result"] == "PASS"
    finally:
        API.request = saved
        os.environ.pop("ASU_RC_API_KEY", None)


# ------------------------------------------------------------------ registry and split

def test_served_models_are_registered_and_decide_nothing():
    served = [s for s in registry.REGISTRY.values() if s.serving == "api"]
    assert len(served) >= 30
    for s in served:
        assert s.id == f"asu-rc/{s.api_model}" and s.gpus == 0 and s.kind == "instruct"
        assert s.pair is None and registry.is_api(s.id)
        assert not h5._is_instruct(s.id) and armb._is_generator(s.id)   # Arm B yes, H5 no
    assert not set(registry.tier_models("all")) & {s.id for s in served}   # nothing to download
    assert h5._is_instruct("Qwen/Qwen2.5-Coder-7B-Instruct")              # paired: still H5
    import phase3_3_design as D
    with D.phase4_design():
        for s in served:
            kind = splits.classify("dom", "d50s1", s.id).kind
            want = ("dev" if s.id in splits.DEV_MODELS else
                    "heldout_model" if s.size_b <= splits.MAX_SIZE_B else "forbidden")
            assert kind == want, (s.id, kind)


# ------------------------------------------------------------------ the pipeline

def test_a_served_model_runs_through_arm_a_and_arm_b():
    saved = splits.DEV_MODELS
    splits.DEV_MODELS = frozenset(saved | {MODEL})           # as a registered development model would be
    try:
        cfg = H.small_cfg(models=(MODEL,), site_limit=24)
        cfg.armb["template_limit"] = 2
        rd = H.tmpdir()
        fake = FakeVLLM()
        pins = {MODEL: {"revision": f"{SERVED}@vllm-test-0001"}}
        make = lambda m: A.APIScorer.for_model(m, pin=pins[m], key=KEY, transport=fake,  # noqa: E731
                                               cell_workers=2)
        assert PL.models_for(cfg, "h5") == []                 # no base twin: no H5
        for exp in ("arm_a", "armb"):
            assert PL.run(cfg, rd, exp, scorer_factory=make, pins=pins) == "COMPLETE", exp
            res = PL.merge(cfg, rd, exp, pins=pins)
            assert res.status == "COMPLETE" and res.rows
            for r in res.rows:
                assert r["model_revision"] == f"{SERVED}@vllm-test-0001"
                assert r["tokenizer_id"].startswith("api-") and r["schema_version"] == "p4/1"
        rows = PL.merge(cfg, rd, "arm_a", pins=pins).rows
        ok = [r for r in rows if r["status"] == "ok"]
        assert ok and all(r["fp32_head"] is False and r["model_kind"] == "instruct" for r in ok)
        # two cells side by side (above) give exactly the rows of one at a time (the default)
        rd1 = H.tmpdir()
        one = lambda m: A.APIScorer.for_model(m, pin=pins[m], key=KEY, transport=FakeVLLM())  # noqa: E731
        assert make(MODEL).cell_workers == 2 and one(MODEL).cell_workers == 1
        assert PL.run(cfg, rd1, "arm_a", scorer_factory=one, pins=pins) == "COMPLETE"
        key = lambda r: r["row_key"]  # noqa: E731
        assert sorted(PL.merge(cfg, rd1, "arm_a", pins=pins).rows, key=key) == sorted(rows, key=key)
        for dp, _ds, fs in os.walk(rd):
            for f in fs:
                assert KEY not in open(os.path.join(dp, f), encoding="utf-8", errors="replace").read(), f
    finally:
        splits.DEV_MODELS = saved


# ------------------------------------------------------------------ the key

def test_the_real_client_scrubs_the_key_from_an_error():
    class Echo(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            body = ("bad key: " + self.headers.get("Authorization", "")).encode()
            self.send_response(401)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), Echo)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        st, text = API.request(KEY, "POST", "/completions", {"x": 1}, tries=1,
                               base=f"http://127.0.0.1:{srv.server_port}")
        assert st == 401 and KEY not in text and "<key>" in text
    finally:
        srv.shutdown()


def test_the_real_client_retries_a_server_error_and_a_stall_on_a_fresh_connection():
    seen = []

    class Flaky(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_POST(self):
            n = len(seen)
            seen.append(self.path)
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            if n == 0:                       # a server error
                body, code = b'{"error":{"message":"Internal server error"}}', 500
            elif n == 1:                     # a stall longer than the client's timeout
                threading.Event().wait(1.5)  # not time.sleep, which the test silences
                body, code = b'{"late": true}', 200
            else:
                body, code = b'{"ok": true}', 200
            self.send_response(code)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Flaky)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    saved = API.time.sleep
    API.time.sleep = lambda s: None                  # no real backoff in a test
    try:
        st, r = API.request(KEY, "POST", "/completions", {"x": 1}, tries=4, timeout=0.5,
                            base=f"http://127.0.0.1:{srv.server_port}")
        assert (st, r) == (200, {"ok": True}) and len(seen) == 3, (st, r, seen)
    finally:
        API.time.sleep = saved
        srv.shutdown()
