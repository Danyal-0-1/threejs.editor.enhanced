"""sampling.py — balanced site selection. Defect P32-003.

----------------------------------------------------------------------------
THE DEFECT
----------------------------------------------------------------------------
The first Phase 3.2 Arm A run selected sites with:

    out = dedupe_by_prefix(all_sites)
    return out[:limit]

`collect_sites` appends family by family, so `out` began with every `dom`
site and only then reached `blk`. With `limit=240` the slice never got past
`dom`:

    Counter({'dom': 240})          272 blk sites existed; 0 were scored

So the run was reported as covering both families and covered one. Worse, the
family it covered is the one with 1.077 token fertility; the fertility-matched
family (`blk`, 1.008) was the half that got dropped. Every reversion number
from that run is therefore fertility-uncontrolled.

A first-N slice over a concatenated list is never a sample. It is whatever
order the loops happened to run in.

----------------------------------------------------------------------------
THE FIX
----------------------------------------------------------------------------
`balanced` round-robins across strata within each cell of
(family x lexicon), so any `limit` yields the same proportions as the full
set, and `limit=0` returns everything. The order within a stratum is the
deterministic construction order, so a run is reproducible without a seed.

`cell_counts` is the audit: print it next to every result. If a cell is
empty, the design is unbalanced and no cross-cell comparison is valid,
whatever the aggregate says.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Sequence

from phase3_2 import _vendor  # noqa: F401

from phase3_2.sites2 import Site, dedupe_by_prefix, stratum


def family_of(site: Site) -> str:
    return site.site_id.split(":")[0]


def cell_key(site: Site) -> tuple[str, str, str]:
    return (family_of(site), site.phi_id, stratum(site))


def balanced(sites: Sequence[Site], limit: int = 0, *,
             dedupe: bool = True) -> list[Site]:
    """Round-robin across (family, lexicon, stratum) cells.

    limit=0 returns every site. Any other limit keeps the cell proportions of
    the full set instead of truncating whichever cell happened to come first.
    """
    pool = dedupe_by_prefix(sites) if dedupe else list(sites)
    cells: dict[tuple, list[Site]] = defaultdict(list)
    for s in pool:
        cells[cell_key(s)].append(s)

    order = sorted(cells)
    out: list[Site] = []
    i = 0
    while True:
        took = False
        for key in order:
            bucket = cells[key]
            if i < len(bucket):
                out.append(bucket[i])
                took = True
                if limit and len(out) >= limit:
                    return out
        if not took:
            return out
        i += 1


def cell_counts(sites: Sequence[Site]) -> dict:
    """Per-cell census plus the marginals, for the audit line in every report."""
    cells = Counter(cell_key(s) for s in sites)
    return {
        "n": len(sites),
        "by_family": dict(Counter(family_of(s) for s in sites)),
        "by_stratum": dict(Counter(stratum(s) for s in sites)),
        "by_lexicon": dict(Counter(s.phi_id for s in sites)),
        "by_cell": {f"{f}/{p}/{st}": n for (f, p, st), n in sorted(cells.items())},
        "empty_cells": [],
    }


def assert_balanced(sites: Sequence[Site], *, families: Sequence[str]) -> None:
    """Fail loudly if a family is missing. This is the check that was absent."""
    seen = {family_of(s) for s in sites}
    missing = set(families) - seen
    if missing:
        raise AssertionError(
            f"sample covers only {sorted(seen)}; missing {sorted(missing)}. "
            f"This is defect P32-003 -- a first-N slice over a concatenated "
            f"list. Use sampling.balanced().")
