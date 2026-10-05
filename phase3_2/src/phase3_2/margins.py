"""margins.py — first-divergent-token margin scoring. Defect P32-001.

----------------------------------------------------------------------------
THE DEFECT THIS FIXES
----------------------------------------------------------------------------
`phase3.models.HFModel.sequence_logprob` tokenises the prefix alone, then
tokenises prefix+continuation, and scores the tail:

    pre_ids = tok(prefix)
    all_ids = tok(prefix + continuation)
    if len(all_ids) <= len(pre_ids):
        return 0.0                      # <-- silently unmeasurable

Measured on the real Qwen2.5-Coder tokenizer over 240 Phase 3.2 sites, that
branch fires for **44.2% of sites**, because BPE merges the candidate into the
preceding token. The canonical case is the one the whole project is about:

    prefix ends  "$S('"
    tok(prefix)     ... 492     ->  `('`
    tok(prefix+'#') ... 3515    ->  `('#`     same LENGTH, different last token
    tok(prefix+'.') ... 4291    ->  `('.`

Both candidates return 0.0, so `M_seq = 0`, which is not negative, so the site
is scored as "no reversion". The defect therefore manufactures a FALSE NULL,
and it does so hardest at the sigil sites -- the cleanest and most important
stratum in the design.

----------------------------------------------------------------------------
THE FIX: score from the FIRST DIVERGENT TOKEN
----------------------------------------------------------------------------
Tokenise both complete strings and find where they first differ:

    ids_c = tok(prefix + c)
    ids_q = tok(prefix + q)
    k     = len(longest common token prefix)

    M_seq = sum_{j>=k} log P(ids_c[j] | ids_c[<j])
          - sum_{j>=k} log P(ids_q[j] | ids_q[<j])

This is well defined whether or not the candidate merges, because the two
sums are conditioned on the SAME k-token context -- the common prefix cancels
exactly. It is the "score through the shortest unique, grammatically complete
decision event" rule from the Phase 3 mathematics document, applied at the
token level rather than the character level.

Properties worth stating, because each is a thing that can go wrong:

  * SYMMETRIC. Both candidates are scored from the same k. Scoring one from
    its own boundary and the other from a different one would make the margin
    a function of the tokenizer rather than of the model.
  * NO ZERO-LENGTH SPANS. If `k` equals the full length of either side the
    strings are identical, which cannot happen for a SEMANTIC site (c != q),
    and raises rather than returning a quiet 0.0.
  * TOKENIZER-DEPENDENT k. The same site has different k under different
    tokenizers. That is correct -- the divergence point is a property of the
    tokenizer -- but it means k must be recorded per model, which
    `MarginV2.k_common` does.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from phase3_2 import _vendor  # noqa: F401

from phase3.sites import Site  # noqa: E402


@dataclass(frozen=True)
class MarginV2:
    site_id: str
    model: str
    shots: int
    logp_correct: float
    logp_competitor: float
    m_seq: float
    k_common: int               # first divergent token index
    n_tok_correct: int          # tokens scored on the correct side
    n_tok_competitor: int
    merged: bool                # did the candidate merge into the prefix token?

    @property
    def reverted(self) -> bool:
        return self.m_seq < 0.0


class TokenScorer:
    """Wraps a causal LM and scores both candidates from their divergence point.

    Holds the model so the weights are loaded once per process. `score_pair`
    does ONE forward pass per candidate; there is no sampling and no gradient.
    """

    def __init__(self, model_id: str, device: str = "cuda", dtype: str = "float16"):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.name = model_id
        self.device = device
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, dtype=getattr(torch, dtype)).to(device).eval()

    def _ids(self, text: str) -> list[int]:
        return self.tok(text, add_special_tokens=False)["input_ids"]

    def _score_from(self, ids: list[int], k: int) -> float:
        """sum_{j>=k} log P(ids[j] | ids[<j]). Requires k >= 1."""
        import torch
        if k < 1:
            k = 1                       # the first token has no context to score against
        if k >= len(ids):
            return 0.0
        t = torch.tensor([ids], device=self.device)
        with torch.no_grad():
            logits = self.model(t).logits.float()
        logprobs = torch.log_softmax(logits[0, :-1], dim=-1)
        targets = t[0, 1:]
        picked = logprobs[k - 1:, :].gather(
            1, targets[k - 1:].unsqueeze(1)).squeeze(1)
        return float(picked.sum().item())

    def score_pair(self, prefix: str, correct: str, competitor: str
                   ) -> tuple[float, float, int, int, int, bool]:
        ids_c = self._ids(prefix + correct)
        ids_q = self._ids(prefix + competitor)
        n_pre = len(self._ids(prefix))

        k = 0
        for a, b in zip(ids_c, ids_q):
            if a != b:
                break
            k += 1
        if k >= len(ids_c) and k >= len(ids_q):
            raise ValueError("candidates tokenise identically; not a real contrast")

        merged = len(ids_c) <= n_pre or len(ids_q) <= n_pre
        return (self._score_from(ids_c, k), self._score_from(ids_q, k),
                k, len(ids_c) - k, len(ids_q) - k, merged)


def divergent_margin(scorer: TokenScorer, site: Site, *, rule: str = "",
                     shots: int = 0, examples: Sequence[str] = ()) -> MarginV2:
    """M_seq at one site, scored from the first divergent token.

    The prefix is built ONCE and reused for both candidates, exactly as in
    `phase3.scoring.forced_prefix_margin`; the only change is where scoring
    starts.
    """
    shown = list(examples[:shots])
    ctx = (rule.rstrip() + "\n\n") if rule else ""
    for ex in shown:
        ctx += ex.rstrip() + "\n"
    if shown:
        ctx += "\n"
    prefix = ctx + site.prefix

    lp_c, lp_q, k, nc, nq, merged = scorer.score_pair(
        prefix, site.correct, site.competitor)
    return MarginV2(site_id=site.site_id, model=scorer.name, shots=len(shown),
                    logp_correct=lp_c, logp_competitor=lp_q, m_seq=lp_c - lp_q,
                    k_common=k, n_tok_correct=nc, n_tok_competitor=nq,
                    merged=merged)
