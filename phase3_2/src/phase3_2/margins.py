"""margins.py — THE canonical first-divergent-token scorer.

Every measurement in Phase 3.2/3.3 that compares two candidate spellings goes
through `TokenScorer.score_pair_detailed`: Arm A, the extinction ladder, H4's
risk score, and H5's repaired-lexicon scoring. There is deliberately no second
implementation. (The old `phase3.models.HFModel.sequence_logprob` path now
raises instead of returning 0.0 -- see "defect history" below.)

----------------------------------------------------------------------------
DEFECT HISTORY
----------------------------------------------------------------------------
P32-001  `phase3.models.HFModel.sequence_logprob` tokenised the prefix alone,
         then prefix+continuation, and returned 0.0 when the second was no
         longer than the first. BPE merges the candidate into the preceding
         token for 44.2% of real sites (`('` + `#` -> the single token `('#`),
         so both candidates scored 0.0, `M_seq = 0`, and the site counted as
         "no reversion". A silent false null, worst at sigil sites.

P33-001  The first P32-001 fix still returned 0.0 for ONE side when that
         side's tokens were a strict prefix of the other's (`k >= len(ids)`).
         Same failure mode, rarer trigger. Now raises `ZeroLengthSpan`.

P33-002  Precision. In bf16/fp16 the logits themselves are quantised (bf16
         keeps 8 mantissa bits, so a logit near 20 is resolved only to about
         0.06 nats). The OUTCOME of this study is the SIGN of a margin, so a
         margin within the quantisation step of zero has an arbitrary sign. The
         first Phase 3.2 runs found 3 exact-zero margins in fp16 -- exact ties
         between different tokens. The scorer now computes the output
         projection in float32 from the decoder's final hidden state
         (`lm_head_fp32=True`), leaving the body in the run dtype. Exact ties
         are recorded per site (`tie`) rather than silently signed.

----------------------------------------------------------------------------
THE ALGORITHM
----------------------------------------------------------------------------
    a = tok(prefix + c)        b = tok(prefix + q)
    k = length of the longest common TOKEN prefix of a and b

    M_seq = sum_{j>=k} log P(a_j | a_<j)  -  sum_{j>=k} log P(b_j | b_<j)

Both sums are conditioned on the SAME k-token context, so the shared prefix
cancels exactly whether or not the candidate merged into the previous token.

Efficiency: the logit predicting position k comes from the hidden state at
k-1, which is shared. One decoder pass over a[:k] therefore scores BOTH
candidates whenever each has exactly one divergent token -- the common case
(all sigil sites are 1/1). Only multi-token candidates need extra passes.

Refusals (each raises; none returns a number):
    IdenticalCandidates   a == b; there is no contrast to measure
    ZeroLengthSpan        k == len(a) or k == len(b); one side has no tokens
    NoContext             k == 0; the divergent token has nothing before it
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from phase3_2 import _vendor  # noqa: F401

from phase3.sites import Site  # noqa: E402


class ScoringError(ValueError):
    """Base for every refusal. Callers record the reason; nobody gets 0.0."""


class IdenticalCandidates(ScoringError):
    pass


class ZeroLengthSpan(ScoringError):
    pass


class NoContext(ScoringError):
    pass


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


@dataclass(frozen=True)
class PairScore:
    """Everything one scoring call learned. Saved per site by the runners."""
    logp_correct: float
    logp_competitor: float
    k_common: int
    n_tok_correct: int
    n_tok_competitor: int
    merged: bool
    n_prefix_tokens: int
    first_div_correct: int          # token id at index k on the correct side
    first_div_competitor: int
    first_div_correct_str: str
    first_div_competitor_str: str
    fp32_head: bool

    @property
    def m_seq(self) -> float:
        return self.logp_correct - self.logp_competitor

    @property
    def tie(self) -> bool:
        return self.logp_correct == self.logp_competitor

    def legacy(self) -> tuple[float, float, int, int, int, bool]:
        return (self.logp_correct, self.logp_competitor, self.k_common,
                self.n_tok_correct, self.n_tok_competitor, self.merged)


def common_prefix_len(a: Sequence[int], b: Sequence[int]) -> int:
    k = 0
    for x, y in zip(a, b):
        if x != y:
            break
        k += 1
    return k


def check_pair(ids_c: Sequence[int], ids_q: Sequence[int]) -> int:
    """Validate a tokenised pair and return k. Raises on every degenerate case.

    Separated from the model so it can be tested without weights.
    """
    if list(ids_c) == list(ids_q):
        raise IdenticalCandidates("candidates tokenise identically")
    k = common_prefix_len(ids_c, ids_q)
    if k >= len(ids_c) or k >= len(ids_q):
        raise ZeroLengthSpan(
            f"one candidate's tokens are a strict prefix of the other's "
            f"(k={k}, len_c={len(ids_c)}, len_q={len(ids_q)}); one side would "
            f"be scored over zero tokens -- this is the P33-001 failure mode")
    if k < 1:
        raise NoContext("candidates diverge at the first token; nothing to "
                        "condition on")
    return k


class TokenScorer:
    """Causal-LM wrapper implementing the canonical scorer.

    Load from a resolved snapshot directory (`snapshot_path`) whenever a run
    must be tied to a pinned revision; `local_files_only=True` then guarantees
    no network access and no silent upgrade.
    """

    def __init__(self, model_id: str, device: str = "cuda",
                 dtype: str = "float16", *, snapshot_path: str | None = None,
                 revision: str | None = None, local_files_only: bool = False,
                 lm_head_fp32: bool = True):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.name = model_id
        self.revision = revision
        self.device = device
        self.dtype = dtype
        src = snapshot_path or model_id
        kw = {"local_files_only": local_files_only}
        if revision and not snapshot_path:
            kw["revision"] = revision
        self.tok = AutoTokenizer.from_pretrained(src, **kw)
        self.model = AutoModelForCausalLM.from_pretrained(
            src, dtype=getattr(torch, dtype), **kw).to(device).eval()

        cfg = self.model.config
        exotic = any(getattr(cfg, a, None) for a in
                     ("final_logit_softcapping", "logit_scale",
                      "output_multiplier_scale"))
        self.lm_head_fp32 = bool(lm_head_fp32 and not exotic)
        self.fp32_head_note = ("disabled: model applies a logit transform after "
                               "the head" if lm_head_fp32 and exotic else "")
        if self.lm_head_fp32:
            head = self.model.get_output_embeddings()
            self._W = head.weight.detach().float()
            self._b = (head.bias.detach().float()
                       if getattr(head, "bias", None) is not None else None)
        self._decoder = (self.model.get_decoder()
                         if hasattr(self.model, "get_decoder") else None)

    # -- tokenisation ------------------------------------------------------
    def ids(self, text: str) -> list[int]:
        return self.tok(text, add_special_tokens=False)["input_ids"]

    def tok_str(self, tid: int) -> str:
        return self.tok.decode([tid])

    # -- internals ---------------------------------------------------------
    def _logprobs_rows(self, ids: list[int], start: int, end: int):
        """log-softmax rows predicting ids[start+1 .. end] from hidden[start..end-1].

        Returns a [end-start, V] float32 tensor. With `lm_head_fp32` the output
        projection is done in float32 from the final hidden state; otherwise
        the model's own logits are used (and upcast).
        """
        import torch
        t = torch.tensor([ids[:end]], device=self.device)
        with torch.no_grad():
            if self.lm_head_fp32 and self._decoder is not None:
                h = self._decoder(input_ids=t).last_hidden_state[0, start:end]
                logits = torch.nn.functional.linear(h.float(), self._W, self._b)
            else:
                logits = self.model(t).logits[0, start:end].float()
        return torch.log_softmax(logits, dim=-1)

    # -- the canonical call ------------------------------------------------
    def score_pair_detailed(self, prefix: str, correct: str,
                            competitor: str) -> PairScore:
        a = self.ids(prefix + correct)
        b = self.ids(prefix + competitor)
        k = check_pair(a, b)
        n_pre = len(self.ids(prefix))

        # one pass over the shared prefix gives the row predicting index k
        first = self._logprobs_rows(a, k - 1, k)[0]

        def side(seq: list[int]) -> float:
            if len(seq) == k + 1:
                return float(first[seq[k]])
            rows = self._logprobs_rows(seq, k - 1, len(seq) - 1)
            import torch
            tgt = torch.tensor(seq[k:], device=rows.device)
            return float(rows.gather(1, tgt.unsqueeze(1)).sum())

        return PairScore(
            logp_correct=side(a), logp_competitor=side(b), k_common=k,
            n_tok_correct=len(a) - k, n_tok_competitor=len(b) - k,
            merged=len(a) <= n_pre or len(b) <= n_pre, n_prefix_tokens=n_pre,
            first_div_correct=a[k], first_div_competitor=b[k],
            first_div_correct_str=self.tok_str(a[k]),
            first_div_competitor_str=self.tok_str(b[k]),
            fp32_head=self.lm_head_fp32)

    def score_pair(self, prefix: str, correct: str, competitor: str
                   ) -> tuple[float, float, int, int, int, bool]:
        """Legacy tuple interface, kept so older callers stay correct."""
        return self.score_pair_detailed(prefix, correct, competitor).legacy()

    def program_nll(self, text: str) -> dict:
        """Whole-program negative log-likelihood -- an H4 baseline.

        The first token has no context and is not scored; `n_scored` says how
        many were. Reported per character as well, because per-token NLL is
        contaminated by fertility.
        """
        ids = self.ids(text)
        if len(ids) < 2:
            return {"nll": float("nan"), "n_scored": 0, "n_chars": len(text),
                    "nll_per_char": float("nan")}
        import torch
        rows = self._logprobs_rows(ids, 0, len(ids) - 1)
        tgt = torch.tensor(ids[1:], device=rows.device)
        nll = -float(rows.gather(1, tgt.unsqueeze(1)).sum())
        return {"nll": nll, "n_scored": len(ids) - 1, "n_chars": len(text),
                "nll_per_char": nll / max(len(text), 1)}

    def generate(self, prompt: str, *, max_new_tokens: int = 192) -> str:
        """Greedy, deterministic. The decoding config is fixed and saved by Arm B."""
        import torch
        enc = self.tok(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            out = self.model.generate(
                **enc, do_sample=False, num_beams=1,
                max_new_tokens=max_new_tokens,
                pad_token_id=self.tok.eos_token_id)
        return self.tok.decode(out[0][enc["input_ids"].shape[1]:],
                               skip_special_tokens=True)

    def release(self) -> None:
        """Free GPU memory before the next model is loaded."""
        import gc
        import torch
        for attr in ("model", "_W", "_b", "_decoder"):
            if hasattr(self, attr):
                setattr(self, attr, None)
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def build_prefix(site: Site, *, rule: str = "", shots: int = 0,
                 examples: Sequence[str] = ()) -> str:
    """The exact context handed to the scorer. Built ONCE per measurement."""
    shown = list(examples[:shots])
    ctx = (rule.rstrip() + "\n\n") if rule else ""
    for ex in shown:
        ctx += ex.rstrip() + "\n"
    if shown:
        ctx += "\n"
    return ctx + site.prefix


def divergent_margin(scorer, site: Site, *, rule: str = "",
                     shots: int = 0, examples: Sequence[str] = ()) -> MarginV2:
    """M_seq at one site, scored from the first divergent token.

    Accepts any object with a `score_pair(prefix, c, q)` returning the legacy
    tuple, so the tokenizer-free fakes used in tests keep working.
    """
    prefix = build_prefix(site, rule=rule, shots=shots, examples=examples)
    lp_c, lp_q, k, nc, nq, merged = scorer.score_pair(
        prefix, site.correct, site.competitor)
    return MarginV2(site_id=site.site_id, model=scorer.name,
                    shots=min(shots, len(examples)),
                    logp_correct=lp_c, logp_competitor=lp_q, m_seq=lp_c - lp_q,
                    k_common=k, n_tok_correct=nc, n_tok_competitor=nq,
                    merged=merged)
