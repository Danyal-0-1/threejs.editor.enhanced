"""analysis.py — uncertainty at the right unit, and the length-matched stratum test.

Next-steps items 2 and 8. Both run on saved per-site rows; neither needs a GPU.
Without `margins.py`'s flight recorder (defect P32-004) neither would be
possible without re-running the models.

----------------------------------------------------------------------------
WHY NOT BOOTSTRAP OVER SITES
----------------------------------------------------------------------------
Sites are not independent. They are nested:

    mapping (9)  >  template (80)  >  site (many)

and 36.4% of semantic sites still share a prefix with another site. Resampling
sites treats one stimulus as several observations and produces intervals that
are far too narrow -- the classic cluster-ignoring error. The independently
constructed units are TEMPLATES and MAPPINGS, so those are what get resampled,
carrying all of their sites with them.

With two grammar families, FAMILY is a fixed stratification factor, not a
random effect: two levels cannot estimate a variance. Every statistic here is
therefore computed WITHIN a family and never pooled across them.

----------------------------------------------------------------------------
WHY THE STRATUM COMPARISON NEEDS LENGTH MATCHING
----------------------------------------------------------------------------
The 3D-knowledge test compares `sigil` sites (no domain knowledge needed)
against `verb` sites (the model must understand the request). But sigil
candidates are single characters and verb candidates are whole words, so the
two strata differ in CANDIDATE TOKEN LENGTH as well as in domain content.

A raw stratum difference is therefore confounded. `length_matched_strata`
compares only sites whose candidate pair has the same token-length signature
`(n_tok_correct, n_tok_competitor)`, so the surviving contrast is about domain
content and not about how many tokens the model had to commit to.

If no length-matched pairs exist, the function says so rather than returning a
number. That is the honest outcome and it is a real possibility here.
"""

from __future__ import annotations

import json
import math
import random
import statistics as st
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def load_rows(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["rows"]


def select(rows: Sequence[dict], **eq) -> list[dict]:
    return [r for r in rows if all(r.get(k) == v for k, v in eq.items())]


# ---------------------------------------------------------------------------
# cluster bootstrap
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Interval:
    point: float
    lo: float
    hi: float
    n_rows: int
    n_clusters: int
    unit: str

    def __str__(self) -> str:
        return (f"{self.point:+.3f} [{self.lo:+.3f}, {self.hi:+.3f}] "
                f"(n={self.n_rows}, {self.n_clusters} {self.unit}s)")

    @property
    def excludes_zero(self) -> bool:
        return (self.lo > 0) or (self.hi < 0)


def cluster_bootstrap(rows: Sequence[dict], stat: Callable[[Sequence[dict]], float],
                      *, unit: str = "template", B: int = 2000,
                      seed: int = 20261002, alpha: float = 0.05) -> Interval | None:
    """Percentile bootstrap resampling whole CLUSTERS, not rows.

    `unit` names the row field to cluster on -- "template" or "lexicon".
    Clusters are drawn with replacement and contribute all of their rows, so
    the within-cluster correlation is preserved rather than averaged away.

    Returns None when there are too few clusters for the interval to mean
    anything. With fewer than ~8 clusters the percentile bootstrap is
    badly behaved, and reporting a number would be worse than reporting none.
    """
    if not rows:
        return None
    buckets: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        buckets[r[unit]].append(r)
    keys = sorted(buckets)
    if len(keys) < 8:
        return None

    rng = random.Random(seed)
    point = stat(rows)
    draws: list[float] = []
    for _ in range(B):
        pick: list[dict] = []
        for _ in range(len(keys)):
            pick.extend(buckets[keys[rng.randrange(len(keys))]])
        try:
            draws.append(stat(pick))
        except (ZeroDivisionError, st.StatisticsError):
            continue
    if len(draws) < B // 2:
        return None
    draws.sort()
    lo = draws[int(alpha / 2 * len(draws))]
    hi = draws[min(len(draws) - 1, int((1 - alpha / 2) * len(draws)))]
    return Interval(point, lo, hi, len(rows), len(keys), unit)


# statistics, all written to take a row list so the bootstrap can reuse them
def mean_margin(rows: Sequence[dict]) -> float:
    return st.mean(r["m_seq"] for r in rows)


def reversion_rate(rows: Sequence[dict]) -> float:
    return sum(r["m_seq"] < 0 for r in rows) / len(rows)


def paired_rule_effect(rows: Sequence[dict]) -> float:
    """mean over sites of M_seq(rule) - M_seq(norule).

    Pairs are formed INSIDE the resample, so a template drawn twice
    contributes its pairs twice -- which is the point of a cluster bootstrap.
    """
    idx: dict[str, dict[str, float]] = defaultdict(dict)
    for r in rows:
        idx[r["site_id"]][r["condition"]] = r["m_seq"]
    d = [v["rule"] - v["norule"] for v in idx.values() if len(v) == 2]
    if not d:
        raise st.StatisticsError("no paired sites")
    return st.mean(d)


# ---------------------------------------------------------------------------
# length-matched stratum comparison
# ---------------------------------------------------------------------------

@dataclass
class StratumComparison:
    family: str
    condition: str
    matched: bool
    signature: str
    n_sigil: int
    n_verb: int
    sigil_reversion: float | None
    verb_reversion: float | None
    note: str = ""

    @property
    def difference(self) -> float | None:
        if self.sigil_reversion is None or self.verb_reversion is None:
            return None
        return self.sigil_reversion - self.verb_reversion


def length_signature(r: dict) -> tuple[int, int]:
    return (r["n_tok_correct"], r["n_tok_competitor"])


def length_matched_strata(rows: Sequence[dict], *, family: str,
                          condition: str) -> list[StratumComparison]:
    """Compare sigil vs verb reversion WITHIN each token-length signature.

    The raw comparison is confounded: sigil candidates are single characters,
    verb candidates are words. This restricts to signatures where BOTH strata
    are present, so the surviving difference is not a length effect.
    """
    sub = select(rows, family=family, condition=condition)
    by_sig: dict[tuple[int, int], dict[str, list[dict]]] = defaultdict(
        lambda: defaultdict(list))
    for r in sub:
        if r["stratum"] in ("sigil", "verb"):
            by_sig[length_signature(r)][r["stratum"]].append(r)

    out: list[StratumComparison] = []
    for sig, strata in sorted(by_sig.items()):
        sg, vb = strata.get("sigil", []), strata.get("verb", [])
        if sg and vb:
            out.append(StratumComparison(
                family=family, condition=condition, matched=True,
                signature=f"{sig[0]}/{sig[1]}", n_sigil=len(sg), n_verb=len(vb),
                sigil_reversion=reversion_rate(sg),
                verb_reversion=reversion_rate(vb)))
        else:
            out.append(StratumComparison(
                family=family, condition=condition, matched=False,
                signature=f"{sig[0]}/{sig[1]}", n_sigil=len(sg), n_verb=len(vb),
                sigil_reversion=reversion_rate(sg) if sg else None,
                verb_reversion=reversion_rate(vb) if vb else None,
                note="only one stratum at this length -- NOT comparable"))
    return out


def length_confound_report(rows: Sequence[dict]) -> dict:
    """How badly are stratum and candidate length confounded?

    Returns the token-length signature distribution per stratum. If the two
    strata occupy disjoint signatures, the raw comparison is uninterpretable
    and no amount of n fixes it.
    """
    out: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in rows:
        out[r["stratum"]][f"{r['n_tok_correct']}/{r['n_tok_competitor']}"] += 1
    return {k: dict(v) for k, v in out.items()}
