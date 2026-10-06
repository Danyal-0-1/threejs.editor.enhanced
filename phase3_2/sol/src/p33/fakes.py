"""fakes.py — a deterministic, GPU-free stand-in for the canonical scorer.

It exists so the WHOLE pipeline -- planning, sharding, resume, merge, every
analysis, every CSV, plot and report -- can run in CI with no weights.

What makes it a useful fake rather than a noise generator:

  * its tokenizer MERGES like BPE. The vocabulary contains `('#`, `('.`,
    `$S '` and friends, so a sigil candidate fuses with the preceding `('` and
    the first-divergent-token path (P32-001) is genuinely exercised. Pair
    validation is the REAL `margins.check_pair`, so P33-001's zero-length
    refusal is exercised too;
  * it plants KNOWN effects the analyses must recover: a habit favouring the
    familiar competitor by `habit` nats, reduced by `rule_effect` when a token
    table is in context, and decaying with the number of demonstrations
    (extinction), plus small deterministic wobble so curves can be
    non-monotone;
  * it is a pure function of its inputs (SHA-256 based) -- identical output
    across processes, runs and machines, which the resume test relies on.
"""

from __future__ import annotations

import hashlib
import math

from phase3_2.margins import PairScore, check_pair

FAKE_VOCAB = sorted({
    # BPE-like merges: the quote fuses with the following sigil, exactly the
    # P32-001 situation (`('` + `#` -> `('#`; blk: ` '` + `#` -> ` '#`).
    "('#", "('.", "('~", "('%", "('@", "(':", "('*", "('",
    " '#", " '.", " '~", " '%", " '@", " ':", " '*", " '",
    "$S", "(function(){", "})();", "{", "}", "(", ")", ";", ",",
    "'", "#", ".", "~", ":", ">", "*", "^", "%", "@", "!", " ",
    "recolor", "scale", "move", "rotate", "delete", "spin", "duplicate",
    "setMaterial", "setOpacity", "setVisible", "wireframe", "metalness",
    "roughness", "castShadow", "receiveShadow",
    "mesh", "group", "light", "camera", "selected", "lasso",
}, key=lambda s: (-len(s), s))


def _h(*parts: str) -> float:
    d = hashlib.sha256("\x00".join(parts).encode("utf-8")).digest()
    return int.from_bytes(d[:8], "big") / 2 ** 64


class FakeTokenizer:
    """Greedy longest-match over FAKE_VOCAB; unknown chars become 1-char tokens.

    Fast enough for full-size fake runs: candidates are indexed by first
    character, and the text before the LAST blank line (the prompt head, which
    is identical across every site of a cell) is encoded once and cached.
    Splitting there is consistent for `prefix` and `prefix + candidate`, which
    is the only property the pair scorer relies on.
    """

    def __init__(self):
        self.vocab: dict[str, int] = {}
        self.inv: dict[int, str] = {}
        self._by_first: dict[str, list[str]] = {}
        for v in FAKE_VOCAB:
            self._by_first.setdefault(v[0], []).append(v)
        self._head_cache: dict[str, list[int]] = {}

    def _id(self, piece: str) -> int:
        """Content-derived id, like a fixed real vocabulary.

        An earlier version numbered pieces in ENCOUNTER order, so a resumed
        scorer that met texts in a different order assigned different ids and
        the id-hashed fake NLL changed -- caught by
        test_resumed_output_equals_uninterrupted_output. Ids must never depend
        on call history.
        """
        if piece not in self.vocab:
            i = int(hashlib.sha256(piece.encode("utf-8")).hexdigest()[:12], 16)
            self.vocab[piece] = i
            self.inv[i] = piece
        return self.vocab[piece]

    def _encode_raw(self, text: str) -> list[int]:
        out, i = [], 0
        while i < len(text):
            for v in self._by_first.get(text[i], ()):
                if text.startswith(v, i):
                    out.append(self._id(v))
                    i += len(v)
                    break
            else:
                out.append(self._id(text[i]))
                i += 1
        return out

    def encode(self, text: str) -> list[int]:
        cut = text.rfind("\n\n")
        if cut < 0:
            return self._encode_raw(text)
        head, tail = text[:cut + 2], text[cut + 2:]
        if head not in self._head_cache:
            if len(self._head_cache) > 512:
                self._head_cache.clear()
            self._head_cache[head] = self._encode_raw(head)
        return self._head_cache[head] + self._encode_raw(tail)

    def decode(self, ids) -> str:
        return "".join(self.inv.get(i, "?") for i in ids)


class FakeScorer:
    def __init__(self, name: str = "fake/Fake-0.5B", *, revision: str = "fakerev0001",
                 habit: float = 1.2, rule_effect: float = 0.4,
                 extinction_rate: float = 0.35, wobble: float = 0.25,
                 tok_cost: float = 0.6, generator=None):
        self.name = name
        self.revision = revision
        self.tokenizer_id = "fake-tok-v1"
        self.dtype = "fake"
        self.lm_head_fp32 = True
        self.habit, self.rule_effect = habit, rule_effect
        self.extinction_rate, self.wobble, self.tok_cost = extinction_rate, wobble, tok_cost
        self.tok = FakeTokenizer()
        self.generator = generator
        self.calls = 0

    # -- tokenizer surface -------------------------------------------------
    def ids(self, text: str) -> list[int]:
        return self.tok.encode(text)

    def tok_str(self, tid: int) -> str:
        return self.tok.decode([tid])

    # -- the planted model -------------------------------------------------
    def _shots(self, prefix: str) -> int:
        n = prefix.count("})();") + prefix.count("} \n") + prefix.count("}\n")
        return n

    def score_pair_detailed(self, prefix: str, correct: str, competitor: str) -> PairScore:
        self.calls += 1
        a, b = self.ids(prefix + correct), self.ids(prefix + competitor)
        k = check_pair(a, b)                       # REAL validation
        n_pre = len(self.ids(prefix))
        shots = self._shots(prefix)
        # site-level habit strength, SHARED across checkpoints of one family so
        # a base model's margin genuinely predicts its instruct twin's (H4)
        site_key = prefix[-60:] + "|" + competitor
        habit = self.habit * (2.0 * _h("site", site_key) - 0.6)
        if "Instruct" in self.name:
            habit *= 0.7
        if "TOKEN TABLE" in prefix:
            habit -= self.rule_effect
        habit -= self.extinction_rate * math.log1p(shots) * 2
        tail = prefix[-40:]
        lc = -self.tok_cost * (len(a) - k) - self.wobble * _h("c", tail, correct, str(shots))
        lq = (-self.tok_cost * (len(b) - k) - self.wobble * _h("q", tail, competitor, str(shots))
              + habit)
        return PairScore(
            logp_correct=lc, logp_competitor=lq, k_common=k,
            n_tok_correct=len(a) - k, n_tok_competitor=len(b) - k,
            merged=len(a) <= n_pre or len(b) <= n_pre, n_prefix_tokens=n_pre,
            first_div_correct=a[k], first_div_competitor=b[k],
            first_div_correct_str=self.tok_str(a[k]),
            first_div_competitor_str=self.tok_str(b[k]),
            fp32_head=True)

    def score_pair(self, prefix, correct, competitor):
        return self.score_pair_detailed(prefix, correct, competitor).legacy()

    def program_nll(self, text: str) -> dict:
        ids = self.ids(text)
        nll = sum(0.5 + _h("nll", str(i), str(t)) for i, t in enumerate(ids[1:]))
        return {"nll": nll, "n_scored": max(len(ids) - 1, 0), "n_chars": len(text),
                "nll_per_char": nll / max(len(text), 1)}

    def generate(self, prompt: str, *, max_new_tokens: int = 192) -> str:
        if self.generator is not None:
            return self.generator(prompt)
        return "I cannot write that program."

    def release(self) -> None:
        pass


class ExplodingScorer(FakeScorer):
    """Fails on the N-th scoring call -- used to simulate a crash mid-run."""

    def __init__(self, *a, fail_after: int, exc: BaseException | None = None, **kw):
        super().__init__(*a, **kw)
        self.fail_after = fail_after
        self.exc = exc or RuntimeError("simulated crash")

    def score_pair_detailed(self, *a, **kw):
        if self.calls >= self.fail_after:
            raise self.exc
        return super().score_pair_detailed(*a, **kw)
