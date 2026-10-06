"""demos.py — leakage-free in-context demonstrations for the extinction ladder.

DEFECT P33-008. `prompts.examples_for` took the FIRST 32 templates
(t000..t031) as demonstrations for every site. A site from template t005 then
saw its own exact correct program as demonstration #6 once the ladder reached
8 shots. Measured: 82 of the 120 Phase 3.3 extinction sites had their target
program in the pool. Those curves measure copying, not the breaking of a
habit, and bias k* downward.

The rule implemented here, for a demonstration candidate D and target site S:

  * D must come from a DIFFERENT template than S;
  * D's rendered text must differ from S's full program;
  * D must not replay S's decision prefix -- unless that prefix is nothing
    more than the family's FIXED OPENING. Every `dom` program begins
    `(function(){ $S('`, which is exactly a first site's prefix; a rule
    that rejected every demonstration starting with it would reject them
    all. Sharing the opening teaches the general lesson. Only a prefix that
    carries template-specific content (longer than the common opening of the
    rendered pool) counts as replaying the decision.

Demonstrations still TEACH the mapping -- they contain the reassigned
spellings, which is the point of the dose -- but none of them hands the model
this site's answer in this site's context.

Order is a seeded permutation of the template pool (`seeds.demo_order`), fixed
per lexicon and family, so every site's ladder is nested (the k-shot set is a
prefix of the (k+1)-shot set) and the dose is the only thing that varies.
Every row records the exact demonstration ids, their order, and a hash.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class DemoSet:
    ids: tuple[str, ...]          # template ids, in presentation order
    texts: tuple[str, ...]

    def first(self, k: int) -> "DemoSet":
        return DemoSet(self.ids[:k], self.texts[:k])

    @property
    def sha(self) -> str:
        h = hashlib.sha256()
        for i, t in zip(self.ids, self.texts):
            h.update(i.encode())
            h.update(b"\x00")
            h.update(t.encode())
            h.update(b"\x01")
        return h.hexdigest()


def pool_order(template_ids: Sequence[str], seed: int, salt: str) -> list[str]:
    """Deterministic permutation of the pool for one (family, lexicon)."""
    ids = sorted(template_ids)
    rng = random.Random(f"{seed}:{salt}")
    rng.shuffle(ids)
    return ids


def common_opening(rendered: dict[str, str]) -> str:
    """The prefix shared by EVERY rendered program in the pool."""
    import os
    texts = list(rendered.values())
    return os.path.commonprefix(texts) if texts else ""


def is_leak(site, demo_template_id: str, demo_text: str, *,
            opening: str = "") -> str | None:
    """Reason this demonstration leaks the site's answer, or None."""
    if demo_template_id == site.template_id:
        return "same_template"
    if demo_text == site.program:
        return "identical_program"
    if len(site.prefix) > len(opening) and demo_text.startswith(site.prefix):
        return "replays_decision_prefix"
    return None


def for_site(site, rendered: dict[str, str], order: Sequence[str],
             n: int) -> DemoSet:
    """The first `n` non-leaking demonstrations in the fixed pool order.

    `rendered` maps template id -> program text in the site's own lexicon and
    family. Raises if the pool cannot supply `n` clean demonstrations, rather
    than silently running a shorter ladder.
    """
    opening = common_opening(rendered)
    ids, texts = [], []
    for tid in order:
        text = rendered.get(tid)
        if text is None or is_leak(site, tid, text, opening=opening):
            continue
        ids.append(tid)
        texts.append(text)
        if len(ids) == n:
            return DemoSet(tuple(ids), tuple(texts))
    raise ValueError(f"only {len(ids)} clean demonstrations available for "
                     f"{site.site_id}; the ladder needs {n}")


def audit(site, demos: DemoSet, *, opening: str = "") -> list[str]:
    """Every leak in a demonstration set (empty = clean). Used by tests and QC."""
    return [f"{i}:{r}" for i, t in zip(demos.ids, demos.texts)
            if (r := is_leak(site, i, t, opening=opening))]
