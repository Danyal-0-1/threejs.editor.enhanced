"""outcomes.py — Arm B scoring: the error taxonomy, site reach, and reversion.

----------------------------------------------------------------------------
THE OPPORTUNITY HURDLE — THE THING EXPERIMENT 02 GOT WRONG
----------------------------------------------------------------------------
An observed reversion is the product of two different events:

    P(observed reversion) = P(O = 1) * P(Y = 1 | O = 1)

    O = 1   the generated program REACHED a comparable decision site
    Y = 1   having reached it, the model emitted the familiar competitor

Experiment 02 compared `3/3` bare reversions against `15/20` scaffolded ones
and read it as "scaffolding increases reversion". It cannot: bare generation
created only three opportunities, because most bare outputs never parsed far
enough to reach the selector at all. The conditions differ in P(O), so the raw
counts are not comparable. This module therefore ALWAYS reports the two parts
separately and refuses to collapse them — `HurdleResult` has no single
"reversion rate" field, on purpose.

----------------------------------------------------------------------------
THE TAXONOMY IS PHASE 1'S, NOT A NEW ONE
----------------------------------------------------------------------------
`SCORING_POLICY.md` section 3 fixes a five-bucket taxonomy, evaluated in order,
and this module implements exactly it. In particular the valid-but-vacuous
rule (D5) is load-bearing: a program that parses but performs zero operations
is a PARSE SUCCESS and a TASK FAILURE. It is also the most plausible-looking
null output a small model emits, so folding it into either side would let a
condition look better by emitting more empty queries.

Parse validity and task accuracy are returned as separate fields and must
never be averaged (SCORING_POLICY section 1).
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Sequence

from phase3 import _vendor  # noqa: F401

import canonicalize as C  # noqa: E402
import phi as P  # noqa: E402
import transpiler as T  # noqa: E402

from phase3.sites import Site, _terminal_of_token


class Bucket(enum.Enum):
    LEX_FAIL = "lex_fail"
    PARSE_FAIL = "parse_fail"
    VALID_VACUOUS = "valid_vacuous"
    VALID_WRONG = "valid_wrong"
    VALID_CORRECT = "valid_correct"

    @property
    def parse_valid(self) -> bool:
        return self in (Bucket.VALID_VACUOUS, Bucket.VALID_WRONG,
                        Bucket.VALID_CORRECT)

    @property
    def task_correct(self) -> bool:
        return self is Bucket.VALID_CORRECT


@dataclass(frozen=True)
class Outcome:
    bucket: Bucket
    ir_hash: str | None
    n_ops: int
    detail: str
    parse_valid: bool
    task_correct: bool


def evaluate(text: str, phi: P.PhiMap, target_ir_hash: str) -> Outcome:
    """Classify one generated program against a target canonical IR hash."""
    try:
        T.lex(text, phi)
    except T.LexError as exc:
        return Outcome(Bucket.LEX_FAIL, None, 0, f"LexError: {exc}", False, False)
    except Exception as exc:
        return Outcome(Bucket.LEX_FAIL, None, 0,
                       f"{type(exc).__name__}: {exc}", False, False)

    try:
        n = T.num_parses(text, phi)
        if n != 1:
            return Outcome(Bucket.PARSE_FAIL, None, 0,
                           f"num_parses={n}", False, False)
        ir = T.parse(text, phi)
    except Exception as exc:
        return Outcome(Bucket.PARSE_FAIL, None, 0,
                       f"{type(exc).__name__}: {exc}", False, False)

    n_ops = len(ir.ops)
    if n_ops == 0:                                    # D5
        return Outcome(Bucket.VALID_VACUOUS, C.content_hash(ir), 0,
                       "vacuous chain: parses, zero operations", True, False)

    got = C.content_hash(ir)
    if got == target_ir_hash:
        return Outcome(Bucket.VALID_CORRECT, got, n_ops, "IR hash matches",
                       True, True)
    return Outcome(Bucket.VALID_WRONG, got, n_ops,
                   f"IR hash {got[:12]} != target {target_ir_hash[:12]}",
                   True, False)


# ---------------------------------------------------------------------------
# reach (O) and reversion (Y)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SiteObservation:
    site_id: str
    reached: bool                 # O
    reverted: bool | None         # Y, defined ONLY when reached
    emitted: str | None
    detail: str


def observe_site(text: str, phi: P.PhiMap, site: Site) -> SiteObservation:
    """Did generation reach this decision site, and what did it emit there?

    "Reached" means the output lexes AND contains a token occupying the same
    terminal ROLE at the same occurrence index. It deliberately does not
    require the whole program to parse: a model can reach and botch a decision
    inside a program that later fails, and discarding those would bias P(Y|O)
    toward the easy cases.

    Reversion is scored on the terminal ROLE the emitted spelling denotes, not
    on string equality with `site.competitor`, so an unrelated token that
    happens to share the spelling cannot be miscounted.
    """
    try:
        toks = T.lex(text, phi)
    except Exception as exc:
        return SiteObservation(site.site_id, False, None, None,
                               f"did not lex: {type(exc).__name__}")

    # Tokens are role-identified the same way sites are, so the comparison is
    # role-to-role rather than character-to-character.
    occ = 0
    for tok_type, value, _off in toks:
        tid = _terminal_of_token(tok_type, value, phi)
        if tid is None:
            continue
        if tid != site.terminal_id and value != site.competitor:
            continue
        if tid == site.terminal_id:
            if occ == site.occurrence:
                return SiteObservation(site.site_id, True,
                                       value == site.competitor, value,
                                       "correct role emitted")
            occ += 1
        elif value == site.competitor:
            # The familiar spelling appeared, bound to a DIFFERENT role: this
            # is exactly the silent semantic collision the site was built for.
            return SiteObservation(site.site_id, True, True, value,
                                   f"competitor spelling bound to {tid}")

    return SiteObservation(site.site_id, False, None, None,
                           "no token at this role/occurrence")


@dataclass(frozen=True)
class HurdleResult:
    n: int
    n_reached: int
    n_reverted: int
    p_reach: float                     # P(O = 1)
    p_revert_given_reach: float | None  # P(Y = 1 | O = 1); None if never reached

    @property
    def p_observed(self) -> float:
        """The product. Reported ALONGSIDE the parts, never instead of them."""
        return self.p_reach * (self.p_revert_given_reach or 0.0)

    def describe(self) -> str:
        cond = ("n/a" if self.p_revert_given_reach is None
                else f"{self.p_revert_given_reach:.3f}")
        return (f"P(reach)={self.p_reach:.3f} [{self.n_reached}/{self.n}]  "
                f"P(revert|reach)={cond} "
                f"[{self.n_reverted}/{self.n_reached or 0}]  "
                f"product={self.p_observed:.3f}")


def hurdle(observations: Sequence[SiteObservation]) -> HurdleResult:
    n = len(observations)
    reached = [o for o in observations if o.reached]
    rev = [o for o in reached if o.reverted]
    return HurdleResult(
        n=n, n_reached=len(reached), n_reverted=len(rev),
        p_reach=(len(reached) / n) if n else 0.0,
        p_revert_given_reach=(len(rev) / len(reached)) if reached else None,
    )
