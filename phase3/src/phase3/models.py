"""models.py — the language-model interface, plus a deterministic fake.

Phase 3 needs exactly three things from a model, and nothing else:

    sequence_logprob(prefix, continuation) -> float    teacher-forced, Arm A
    generate(prompt, max_new_tokens)       -> str      unrestricted, Arm B
    n_tokens(text)                         -> int      tokenisation diagnostics

Keeping the surface this small is deliberate. It means the whole pipeline can
run, and every test can pass, with no GPU, no `transformers`, and no network —
which is what makes `tests/test_end_to_end.py` a real regression test instead
of something that only runs on the cluster.

----------------------------------------------------------------------------
WHY THE FAKE MODEL PLANTS A KNOWN EFFECT
----------------------------------------------------------------------------
A fake model that returns noise proves only that the code does not crash.
`FakeLM` instead plants a *known* ground truth: a configurable log-odds bonus
for any continuation drawn from a declared "familiar" vocabulary. The
end-to-end test then asserts that the pipeline RECOVERS the planted bias —
right sign, right rough magnitude, at the right sites. A pipeline that cannot
recover an effect it was handed cannot be trusted to measure a real one.

`FakeLM` is deterministic: identical inputs give identical outputs across
processes and machines, because scoring is a pure function of a SHA-256 of the
text plus the declared bias. No RNG, no seeds to forget.

----------------------------------------------------------------------------
A NOTE ON SEQUENCE SCORING THAT IS EASY TO GET WRONG
----------------------------------------------------------------------------
`sequence_logprob` must return the log probability of the WHOLE continuation:

    log P(y | x) = sum_j log P(y_j | x, y_<j)

summed over every token of `y` under the model's own tokenizer. Two mistakes
the review calls out specifically, both of which this interface is shaped to
prevent:

  * Normalising by token count. That answers a different question and must not
    silently replace the full-sequence probability. `scoring.py` reports the
    normalised variants as explicit sensitivity analyses, never as the primary.
  * Scoring only the first token when candidates are multi-token. Candidates
    here can be multi-token (`castShadow` vs `receiveShadow`), so the full sum
    is required; the single-token logit margin is a different quantity and is
    named `G_tok`, not `M_seq`, everywhere in this codebase.
"""

from __future__ import annotations

import hashlib
import math
import os
from dataclasses import dataclass, field
from typing import Protocol, Sequence, runtime_checkable


@runtime_checkable
class LM(Protocol):
    name: str

    def sequence_logprob(self, prefix: str, continuation: str) -> float: ...
    def generate(self, prompt: str, max_new_tokens: int = 256) -> str: ...
    def n_tokens(self, text: str) -> int: ...


# ---------------------------------------------------------------------------
# deterministic fake
# ---------------------------------------------------------------------------

def _h(*parts: str) -> float:
    """A deterministic pseudo-random float in [0, 1) from the given strings."""
    d = hashlib.sha256("\x00".join(parts).encode("utf-8")).digest()
    return int.from_bytes(d[:8], "big") / 2 ** 64


@dataclass
class FakeLM:
    """A deterministic stand-in with a PLANTED, measurable familiarity bias.

    familiar       spellings the fake "knows" from pretraining
    favoured_pairs (prefix_tail, continuation) pairs to favour. Needed because
                   a PERMUTATION lexicon like `delta` has an identical set of
                   correct and competitor spellings — every spelling is correct
                   at one role and a competitor at another — so a bias keyed on
                   the spelling ALONE awards both candidates and cancels. Real
                   priors are contextual ("what belongs HERE"), not global, and
                   this field models that. A pair matches when the scored
                   prefix ends with `prefix_tail`.
    familiar_bonus log-odds added to any continuation equal to a familiar
                   spelling, or matching a favoured pair — the ground truth the
                   pipeline must recover
    context_bonus  EXTRA bonus when the prefix ends in a context the fake also
                   finds familiar (see `cue_suffixes`). This is the planted
                   prior x context INTERACTION; set it to 0.0 for a pure
                   main-effect fixture.
    cue_suffixes   prefix endings that count as competitor-cueing context
    """

    name: str = "fake-lm"
    familiar: frozenset[str] = frozenset()
    favoured_pairs: frozenset[tuple[str, str]] = frozenset()
    familiar_bonus: float = 2.5
    context_bonus: float = 1.5
    cue_suffixes: tuple[str, ...] = ("('", "(\"", " ", ".")
    per_token_cost: float = 0.75
    noise: float = 0.35
    echo: str = ""                     # what generate() returns, if set
    calls: list[tuple[str, str]] = field(default_factory=list)

    # -- LM protocol --------------------------------------------------------
    def n_tokens(self, text: str) -> int:
        """A crude but STABLE token count: runs of word chars / non-word chars."""
        n, prev_word = 0, None
        for ch in text:
            is_word = ch.isalnum() or ch == "_"
            if prev_word is None or is_word != prev_word:
                n += 1
                prev_word = is_word
        return max(n, 1)

    def sequence_logprob(self, prefix: str, continuation: str) -> float:
        self.calls.append((prefix, continuation))
        lp = -self.per_token_cost * self.n_tokens(continuation)
        lp -= self.noise * _h(prefix[-64:], continuation)

        hit = continuation in self.familiar or any(
            continuation == cont and prefix.endswith(tail)
            for tail, cont in self.favoured_pairs)

        if hit:
            lp += self.familiar_bonus
            if any(prefix.endswith(s) for s in self.cue_suffixes):
                lp += self.context_bonus
        return lp

    def generate(self, prompt: str, max_new_tokens: int = 256) -> str:
        return self.echo


# ---------------------------------------------------------------------------
# real models
# ---------------------------------------------------------------------------

@dataclass
class HFModel:
    """A causal-LM wrapper. Imports torch/transformers LAZILY, so that merely
    importing phase3 on a laptop with no CUDA costs nothing.

    NOT EXERCISED BY THE TEST SUITE — no weights are downloaded in CI. Tests
    cover the arithmetic through `FakeLM`; this class is the thin edge that
    must be smoke-tested on the cluster before a real run. See README
    "Status of each component".
    """

    model_id: str
    device: str = "cuda"
    dtype: str = "bfloat16"
    name: str = ""
    _tok = None
    _model = None

    def __post_init__(self) -> None:
        self.name = self.name or self.model_id

    def _load(self):
        if self._model is None:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self._tok = AutoTokenizer.from_pretrained(self.model_id)
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=getattr(torch, self.dtype),
            ).to(self.device).eval()
        return self._tok, self._model

    def n_tokens(self, text: str) -> int:
        tok, _ = self._load()
        return len(tok(text, add_special_tokens=False)["input_ids"])

    def sequence_logprob(self, prefix: str, continuation: str) -> float:
        """sum_j log P(y_j | x, y_<j) over every token of `continuation`.

        The prefix is tokenised WITH the continuation appended rather than
        separately, because tokenising them apart can split the boundary
        differently and silently score a different string than the model would
        ever see. The continuation's token span is then recovered by length.
        """
        import torch
        tok, model = self._load()
        pre_ids = tok(prefix, add_special_tokens=False)["input_ids"]
        all_ids = tok(prefix + continuation, add_special_tokens=False)["input_ids"]
        if len(all_ids) <= len(pre_ids):
            return 0.0
        ids = torch.tensor([all_ids], device=self.device)
        with torch.no_grad():
            logits = model(ids).logits.float()
        logprobs = torch.log_softmax(logits[0, :-1], dim=-1)
        targets = ids[0, 1:]
        start = len(pre_ids) - 1
        picked = logprobs[start:, :].gather(
            1, targets[start:].unsqueeze(1)).squeeze(1)
        return float(picked.sum().item())

    def generate(self, prompt: str, max_new_tokens: int = 256) -> str:
        import torch
        tok, model = self._load()
        ids = tok(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            out = model.generate(**ids, max_new_tokens=max_new_tokens,
                                 do_sample=False, num_beams=1,
                                 pad_token_id=tok.eos_token_id)
        return tok.decode(out[0][ids["input_ids"].shape[1]:],
                          skip_special_tokens=True)


def load(spec: str) -> LM:
    """'fake' -> FakeLM; anything else -> HFModel(spec)."""
    if spec == "fake" or os.environ.get("PHASE3_FAKE_LM"):
        return FakeLM()
    return HFModel(spec)
