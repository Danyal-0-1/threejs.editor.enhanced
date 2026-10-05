"""linter.py — H4 (predict risky sites) and H5 (repair them), the headline track.

This is the contribution that does NOT depend on the A x T interaction. It
needs only a MAIN effect of competitor prior strength at sites, which is the
far safer claim (analysis doc section 2.4). If the interaction is null, this
still stands.

    detect  ->  predict  ->  repair  ->  verify

----------------------------------------------------------------------------
H4 — THE SITE RISK SCORE
----------------------------------------------------------------------------
    S_seq   = log P_base(q | r, x) - log P_base(c | r, x)
    S_local = log P_base(q | r0, x) - log P_base(c | r0, x)      (no rule)
    S_shift = S_seq - S_local

Note the sign is DELIBERATELY the opposite of `scoring.M_seq`: risk is high
when the competitor is preferred, so S > 0 means danger. Keeping the two
quantities under different names with opposite signs is the one thing that
stops the sign error the review warns about; they are never interchangeable.

`S_local` isolates how much the LOCAL context supports the competitor with no
rule present, and `S_shift` how far the remote rule moves the base model. A
predictor built on `S_seq` alone cannot distinguish "this spelling is doomed"
from "this rule was ignored"; the decomposition can.

WHAT WOULD MAKE THIS A RESULT RATHER THAN A RETROSPECTIVE EXPLANATION
    Freeze candidate construction, the score, the calibration and the
    threshold on DEVELOPMENT grammars; then test on unseen mappings, an unseen
    grammar family, unseen AST templates, and preferably another tokenizer
    family. A predictor that merely recognises "this is lexicon alpha" is a
    language-identity detector, not a site predictor — which is why
    `rank_report` demands an explicit baseline comparison and why
    `scripts/run_linter.py` refuses to report without held-out groups.

----------------------------------------------------------------------------
H5 — REPAIR, AND WHY ITS CORRECTNESS IS MECHANICAL
----------------------------------------------------------------------------
A repair rewrites the SPELLING of a risky terminal and must not change any
program's meaning:

    IR(p) == IR( psi( W(p) ) )      for every program p

Because a repair here is exactly a new phi-map, and phi-maps are validated
bijections on the spelling partition (V6), IR preservation is PROVABLE rather
than assumed — `verify_repair` re-parses the whole corpus under the new map
and compares canonical IR hashes. Nothing is accepted on a model's judgment.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Sequence

from phase3 import _vendor  # noqa: F401

import canonicalize as C  # noqa: E402
import phi as P  # noqa: E402
import transpiler as T  # noqa: E402

from phase3.models import LM
from phase3.sites import Site

# ---------------------------------------------------------------------------
# H4 — risk scoring
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RiskScore:
    site_id: str
    model: str
    s_seq: float            # with the rule present   (> 0 == danger)
    s_local: float          # with no rule present
    s_shift: float          # s_seq - s_local
    terminal_id: str
    collision: str

    def as_row(self) -> dict:
        return {"site_id": self.site_id, "model": self.model,
                "s_seq": self.s_seq, "s_local": self.s_local,
                "s_shift": self.s_shift, "terminal_id": self.terminal_id,
                "collision": self.collision}


def score_site(base: LM, site: Site, *, rule: str) -> RiskScore:
    """Compute S_seq, S_local and S_shift at one site on a BASE checkpoint."""
    def margin(ctx: str) -> float:
        prefix = (ctx.rstrip() + "\n\n" if ctx else "") + site.prefix
        return (base.sequence_logprob(prefix, site.competitor)
                - base.sequence_logprob(prefix, site.correct))

    s_seq = margin(rule)
    s_local = margin("")
    return RiskScore(site_id=site.site_id, model=base.name, s_seq=s_seq,
                     s_local=s_local, s_shift=s_seq - s_local,
                     terminal_id=site.terminal_id,
                     collision=site.collision.value)


# ---------------------------------------------------------------------------
# ranking / calibration metrics
# ---------------------------------------------------------------------------

def auroc(scores: Sequence[float], labels: Sequence[int]) -> float | None:
    """Rank-based AUROC with explicit tie handling (the Mann-Whitney form).

    Returns None when one class is absent, rather than a misleading 0.5.
    """
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return None
    wins = sum((1.0 if a > b else 0.5 if a == b else 0.0)
               for a in pos for b in neg)
    return wins / (len(pos) * len(neg))


def auprc(scores: Sequence[float], labels: Sequence[int]) -> float | None:
    """Average precision. Report WITH prevalence: it is the baseline."""
    if not any(labels):
        return None
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    tp = 0
    total_pos = sum(labels)
    acc = 0.0
    for rank, i in enumerate(order, 1):
        if labels[i] == 1:
            tp += 1
            acc += tp / rank
    return acc / total_pos


def precision_at_k(scores: Sequence[float], labels: Sequence[int], k: int) -> float:
    order = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
    return sum(labels[i] for i in order) / max(len(order), 1)


def brier(probs: Sequence[float], labels: Sequence[int]) -> float:
    return sum((p - y) ** 2 for p, y in zip(probs, labels)) / max(len(labels), 1)


@dataclass
class RankReport:
    n: int
    prevalence: float
    auroc: float | None
    auprc: float | None
    p_at_10: float
    baselines: dict[str, float | None]

    def describe(self) -> str:
        lines = [f"n={self.n}  prevalence={self.prevalence:.3f}  "
                 f"AUROC={self.auroc}  AUPRC={self.auprc}  P@10={self.p_at_10:.3f}"]
        for k, v in self.baselines.items():
            lines.append(f"    baseline {k:28s} AUROC={v}")
        return "\n".join(lines)


def rank_report(sites: Sequence[Site], scores: Sequence[float],
                labels: Sequence[int], *,
                baselines: dict[str, Sequence[float]] | None = None) -> RankReport:
    """Rank the proposed score AND the mandatory baselines side by side.

    The baselines are not optional garnish. Analysis doc section 2.4 and the
    review's section 10.2 both insist that a site score must beat language
    identity, candidate token/byte count and whole-program NLL before it counts
    as an exact-site predictor. `scripts/run_linter.py` passes them in.
    """
    base_auc = {name: auroc(vals, labels)
                for name, vals in (baselines or {}).items()}
    return RankReport(
        n=len(sites),
        prevalence=(sum(labels) / len(labels)) if labels else 0.0,
        auroc=auroc(scores, labels), auprc=auprc(scores, labels),
        p_at_10=precision_at_k(scores, labels, 10),
        baselines=base_auc,
    )


def length_baseline(sites: Sequence[Site]) -> list[float]:
    """Byte-count baseline: |q| - |c|. Cheap, model-free, and often decent."""
    return [float(len(s.competitor.encode()) - len(s.correct.encode()))
            for s in sites]


def identity_baseline(sites: Sequence[Site]) -> list[float]:
    """Language-identity baseline: 1.0 if the lexicon remaps this role at all.

    If this scores as well as the model-based site score, the 'predictor' has
    learned nothing beyond 'alpha is weird'.
    """
    return [0.0 if s.correct == s.competitor else 1.0 for s in sites]


# ---------------------------------------------------------------------------
# H5 — minimal, semantics-preserving repair
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Repair:
    terminal_id: str
    old_spelling: str
    new_spelling: str
    risk_before: float
    risk_after: float

    @property
    def gain(self) -> float:
        return self.risk_before - self.risk_after


def propose_repair(base: LM, site: Site, phi: P.PhiMap, *, rule: str,
                   alphabet: Sequence[str]) -> Repair | None:
    """Pick the lowest-risk replacement spelling for this site's terminal.

    Only the ONE terminal is changed; every other spelling is left alone. That
    is the "minimum change" objective — the claim being tested is not that
    rewriting helps, but that rewriting ONLY the predicted-risky sites buys
    more per changed symbol than a global rename.

    Candidate spellings must not already be in use, or the new map would fail
    the V6 partition check downstream.
    """
    in_use = {phi.spelling(t.id) for t in phi.table.terminals if t.substitutable}
    best: Repair | None = None
    before = score_site(base, site, rule=rule).s_seq

    for cand in alphabet:
        if cand in in_use or cand == site.correct:
            continue
        probe = Site(**{**site.__dict__, "correct": cand})
        after = score_site(base, probe, rule=rule).s_seq
        if best is None or after < best.risk_after:
            best = Repair(site.terminal_id, site.correct, cand, before, after)
    return best


def apply_repairs(phi_blob: dict, repairs: Sequence[Repair]) -> dict:
    """Return a NEW phi blob with the repairs applied. The input is not mutated."""
    out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in phi_blob.items()}
    out["map"] = {k: dict(v) for k, v in phi_blob["map"].items()}
    for r in repairs:
        if r.terminal_id not in out["map"]:
            raise KeyError(f"terminal {r.terminal_id} absent from phi map")
        out["map"][r.terminal_id]["to"] = r.new_spelling
    out["phi_id"] = phi_blob["phi_id"] + "_repaired"
    return out


def verify_repair(old: P.PhiMap, new: P.PhiMap, programs: Sequence[str],
                  identity: P.PhiMap) -> tuple[bool, list[str]]:
    """PROVE IR preservation: every program must keep its canonical IR hash.

    This is the H5 correctness condition, checked mechanically over the whole
    corpus rather than argued. A repair that changes any program's IR is
    rejected outright — there is no tolerance and no sampling.
    """
    problems: list[str] = []
    for i, p3dom in enumerate(programs):
        try:
            a = C.content_hash(T.parse(T.transliterate(p3dom, identity, old), old))
            b = C.content_hash(T.parse(T.transliterate(p3dom, identity, new), new))
        except Exception as exc:
            problems.append(f"t{i:03d}: {type(exc).__name__}: {str(exc)[:80]}")
            continue
        if a != b:
            problems.append(f"t{i:03d}: IR changed {a[:12]} -> {b[:12]}")
    return (not problems), problems
