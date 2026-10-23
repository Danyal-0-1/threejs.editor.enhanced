"""api.py — the scorer for models served by the ASU RC LLM API, with TokenScorer's interface.

THE SAME MEASUREMENT. Phase 3.3 scored raw text, with no chat template and no special tokens
(margins.py, `TokenScorer.ids`). The API's /v1/completions (vLLM, behind Research Computing's
gateway) returns, for a prompt, the id of every prompt token (`return_token_ids`) and each
token's log-probability given the tokens before it (`prompt_logprobs: 0`), with special tokens
off (`add_special_tokens: false`). So the margin is computed by the same algorithm, from the
served model's own tokenisation:

    a = ids(prefix + c)    b = ids(prefix + q)    k = margins.check_pair(a, b)
    M = sum_{j>=k} lp_a[j]  -  sum_{j>=k} lp_b[j]

with the same refusals (IdenticalCandidates, ZeroLengthSpan, NoContext) and the same `merged`
flag (a third request tokenises the prefix alone). The three requests of a pair are sent at once.
Arm B's greedy generation is temperature 0 from the raw prompt, with the tokenizer's default
special tokens, as `TokenScorer.generate` does.

WHAT DIFFERS, RECORDED ON EVERY ROW
  fp32_head = False   the server computes the logits in its own precision. In the probe of
                      2026-10-22, 33 of the 36 registered models gave margins that were whole
                      multiples of 2^-3 to 2^-5 nats (bf16 logits): a margin nearer zero than
                      that has an unreliable sign, and exact ties occur (`tie`), as before
                      P33-002. beam-1-0, deepseek-v4-1-flash and muse-spark-open did not round.
  dtype               the precision of the served weights (bf16, fp8, mxfp4), from /v1/models
  model_revision      "<served model>@<system_fingerprint>", the only identity the API gives. It
                      is pinned (`run.py prefetch`), checked when the scorer starts, and checked
                      on EVERY answer: an answer from any other deployment raises
                      ServedModelChanged, so a cell never mixes two of them (the cell fails and
                      is resumed later, after a deliberate new pin in a new run). Three models
                      sent no fingerprint (granite41-30b, minimax-m2-7, qwen-agentworld-35b-a3b):
                      for them only the served name is checked.
  tokenizer_id        "api-" + a hash of the served token ids of a fixed reference text

Nothing is cached on disk. The key never leaves p4/runtime/asu_api.py.
"""

from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import threading
from collections import OrderedDict

from p4.runtime import asu_api as API
from p4.scoring.margins import PairScore, check_pair

# Tokenised once per scorer; its ids fingerprint the served tokenizer (code, sigils, Unicode, layout).
REFERENCE = ("$S('#cube.red > .wheel').move(1, -2.5).scale(0.5); // done\n"
             "\tif (a <= b && c != d) { x[i] = y?.z ?? 0; }\n"
             "Größe, naïve, 東京, ελληνικά, emoji \U0001F600, quotes \"'`, math ±×÷√∞.")


class ServedModelChanged(RuntimeError):
    """An answer came from a deployment other than the one this scorer is bound to."""


class APIError(RuntimeError):
    """The API did not answer as the scorer needs. Never turned into a number."""


class APIScorer:
    """One served model. `transport` replaces asu_api.request in the tests."""

    def __init__(self, model_id: str, *, served_name: str, quantization: str = "",
                 pin: dict | None = None, key: str | None = None, transport=None,
                 workers: int = 3, tries: int = 8, ids_cache: int = 4096):
        self.name = model_id
        self.served_name = served_name
        self.dtype = quantization or "served"
        self.lm_head_fp32 = False
        self.snapshot_path = None
        self._key = key if key is not None else API.load_key()
        self._send = transport or API.request
        self._tries = tries
        self._pool = cf.ThreadPoolExecutor(max_workers=max(1, workers))
        self._lock = threading.Lock()
        self._ids: OrderedDict[str, list[int]] = OrderedDict()
        self._ids_max = ids_cache
        self._strs: dict[int, str] = {}
        self.revision: str | None = None
        ref = self._tokens(REFERENCE, logprobs=False)["ids"]          # binds self.revision
        self.tokenizer_id = "api-" + hashlib.sha256(json.dumps(ref).encode()).hexdigest()[:16]
        pinned = (pin or {}).get("revision")
        if pinned and pinned != self.revision:
            raise ServedModelChanged(
                f"{model_id}: the API now serves {self.revision}, but {pinned} is pinned. A run "
                f"cannot mix two deployments; pin the new one deliberately, in a new run")

    @classmethod
    def for_model(cls, model_id: str, *, pin: dict | None = None, **kw) -> "APIScorer":
        from p4.governance import registry
        s = registry.spec(model_id)
        if s.serving != "api":
            raise ValueError(f"{model_id} is not served by the ASU RC API")
        return cls(model_id, served_name=s.api_model, quantization=s.quantization, pin=pin, **kw)

    # -- one request -------------------------------------------------------
    def _post(self, body: dict) -> dict:
        status, r = self._send(self._key, "POST", "/completions", body, tries=self._tries)
        if status != 200 or not isinstance(r, dict) or not r.get("choices"):
            raise APIError(f"{self.name}: HTTP {status}: {str(r)[:200]}")
        got = f"{r.get('model')}@{r.get('system_fingerprint')}"
        with self._lock:
            if self.revision is None:
                self.revision = got
        if got != self.revision:
            raise ServedModelChanged(f"{self.name}: answered by {got}, bound to {self.revision}")
        return r["choices"][0]

    def _tokens(self, text: str, *, logprobs: bool = True) -> dict:
        """The served ids of `text` (special tokens off) and, with `logprobs`, each token's
        log-probability given the ones before it (None for the first, which has no context)."""
        body = {"model": self.served_name, "prompt": text, "max_tokens": 1, "temperature": 0,
                "return_token_ids": True, "add_special_tokens": False}
        if logprobs:
            body["prompt_logprobs"] = 0
        ch = self._post(body)
        ids = ch.get("prompt_token_ids")
        if not isinstance(ids, list) or not ids:
            raise APIError(f"{self.name}: the answer has no prompt token ids")
        ids = [int(x) for x in ids]
        out: dict = {"ids": ids}
        if logprobs:
            pl = ch.get("prompt_logprobs")
            if not isinstance(pl, list) or len(pl) != len(ids):
                raise APIError(f"{self.name}: prompt log-probabilities missing or misaligned")
            lps: list = [None]
            for j in range(1, len(ids)):
                e = (pl[j] or {}).get(str(ids[j]))
                if not isinstance(e, dict) or not isinstance(e.get("logprob"), (int, float)):
                    raise APIError(f"{self.name}: position {j} has no log-probability for its own token")
                lps.append(float(e["logprob"]))
                if isinstance(e.get("decoded_token"), str):
                    self._strs[ids[j]] = e["decoded_token"]
            out["lps"] = lps
        return out

    # -- tokenisation ------------------------------------------------------
    def ids(self, text: str) -> list[int]:
        with self._lock:
            if text in self._ids:
                self._ids.move_to_end(text)
                return self._ids[text]
        got = self._tokens(text, logprobs=False)["ids"]
        with self._lock:
            self._ids[text] = got
            while len(self._ids) > self._ids_max:
                self._ids.popitem(last=False)
        return got

    def tok_str(self, tid: int) -> str:
        return self._strs.get(tid, f"<id {tid}>")

    # -- the canonical call ------------------------------------------------
    def score_pair_detailed(self, prefix: str, correct: str, competitor: str) -> PairScore:
        fa = self._pool.submit(self._tokens, prefix + correct)
        fb = self._pool.submit(self._tokens, prefix + competitor)
        fp = self._pool.submit(self._tokens, prefix, logprobs=False) if prefix else None
        A, B = fa.result(), fb.result()
        n_pre = len(fp.result()["ids"]) if fp else 0
        a, b = A["ids"], B["ids"]
        k = check_pair(a, b)
        return PairScore(
            logp_correct=sum(A["lps"][k:]), logp_competitor=sum(B["lps"][k:]), k_common=k,
            n_tok_correct=len(a) - k, n_tok_competitor=len(b) - k,
            merged=len(a) <= n_pre or len(b) <= n_pre, n_prefix_tokens=n_pre,
            first_div_correct=a[k], first_div_competitor=b[k],
            first_div_correct_str=self.tok_str(a[k]),
            first_div_competitor_str=self.tok_str(b[k]),
            fp32_head=False)

    def score_pair(self, prefix: str, correct: str, competitor: str):
        """Legacy tuple interface, as TokenScorer has."""
        return self.score_pair_detailed(prefix, correct, competitor).legacy()

    def program_nll(self, text: str) -> dict:
        """Whole-program negative log-likelihood, as TokenScorer.program_nll."""
        t = self._tokens(text)
        if len(t["ids"]) < 2:
            return {"nll": float("nan"), "n_scored": 0, "n_chars": len(text),
                    "nll_per_char": float("nan")}
        nll = -sum(t["lps"][1:])
        return {"nll": nll, "n_scored": len(t["ids"]) - 1, "n_chars": len(text),
                "nll_per_char": nll / max(len(text), 1)}

    def generate(self, prompt: str, *, max_new_tokens: int = 192) -> str:
        """Greedy (temperature 0), from the raw prompt with the tokenizer's default special
        tokens, special tokens skipped in the output: TokenScorer.generate's settings."""
        ch = self._post({"model": self.served_name, "prompt": prompt, "max_tokens": max_new_tokens,
                         "temperature": 0, "add_special_tokens": True, "skip_special_tokens": True})
        return ch.get("text") or ""

    def release(self) -> None:
        self._pool.shutdown(wait=True)
