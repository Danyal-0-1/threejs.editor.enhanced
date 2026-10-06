"""sampling.py — deterministic, balanced, order-independent site selection.

----------------------------------------------------------------------------
DEFECT HISTORY
----------------------------------------------------------------------------
P32-003  `dedupe_by_prefix(pool)[:limit]` over a family-concatenated list
         scored 240 `dom` sites and zero `blk` while reporting both.

P33-003  The P32-003 fix still de-duplicated GLOBALLY by first occurrence, so
         the result depended on CLI order. Measured on the four development
         lexicons: reversing `--lexicons` moved retained `d50s2` sites from
         172 to 272 and `d25s1` from 220 to 150.

P33-004  `assert_balanced` checked only families, and `cell_counts` returned a
         hard-coded `"empty_cells": []`, so a sample could miss an entire
         (family, lexicon, stratum) cell and still pass.

----------------------------------------------------------------------------
THE UNIT OF DE-DUPLICATION, STATED EXPLICITLY
----------------------------------------------------------------------------
Two sites are the same STIMULUS only if the model sees the same full context.
The context is (rule table, program prefix). The rule table is a function of
the LEXICON, so sites in different lexicons with byte-identical program
prefixes are DIFFERENT stimuli and must both be kept. Different families never
share prefixes at all.

    de-duplication unit  =  (family, lexicon)  cell
    within a cell        =  keep one site per distinct prefix

Which site of a prefix group is kept is decided by the CANONICAL KEY
`(template_id, terminal_id, occurrence)` -- never by input order. So any
permutation of the input yields the same output. Every dropped site is
returned with the id of the site it duplicates, for `split_exclusion_audit.csv`.

----------------------------------------------------------------------------
EXPECTED CELLS ARE DERIVED FROM THE MATERIALS, NOT A FULL GRID
----------------------------------------------------------------------------
`d25s2` never remaps a sigil (its seed did not draw the sigil group), so
`dom/d25s2/sigil` CANNOT contain a semantic site. A naive
family x lexicon x stratum grid would declare that cell missing forever.
Expected cells are therefore computed from the de-duplicated pool, and every
grid cell that is empty in the pool is reported as STRUCTURALLY_EMPTY -- a
property of the lexicon, which also means that lexicon cannot contribute to
that stratum's comparisons.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Sequence

from phase3_2 import _vendor  # noqa: F401

from phase3_2.sites2 import Site, stratum


STRATA = ("keyword", "sigil", "verb")


def family_of(site: Site) -> str:
    return site.site_id.split(":")[0]


def cell_key(site: Site) -> tuple[str, str, str]:
    return (family_of(site), site.phi_id, stratum(site))


def canonical_key(site: Site) -> tuple:
    """Total order on sites that does not depend on how they were collected."""
    return (family_of(site), site.phi_id, site.template_id, site.terminal_id,
            site.occurrence, site.char_offset)


@dataclass(frozen=True)
class Dropped:
    site_id: str
    reason: str
    duplicate_of: str | None


def dedupe_within_cells(sites: Iterable[Site]) -> tuple[list[Site], list[Dropped]]:
    """Keep one site per (family, lexicon, prefix). Order-independent."""
    ordered = sorted(sites, key=canonical_key)
    kept: list[Site] = []
    dropped: list[Dropped] = []
    owner: dict[tuple[str, str, str], str] = {}
    for s in ordered:
        k = (family_of(s), s.phi_id, s.prefix)
        if k in owner:
            dropped.append(Dropped(s.site_id, "prefix_duplicate_within_cell",
                                   owner[k]))
        else:
            owner[k] = s.site_id
            kept.append(s)
    return kept, dropped


def available_cells(pool: Sequence[Site]) -> Counter:
    """Counts per (family, lexicon, stratum) after within-cell de-duplication."""
    kept, _ = dedupe_within_cells(pool)
    return Counter(cell_key(s) for s in kept)


def structural_grid(pool: Sequence[Site], *, families: Sequence[str],
                    lexicons: Sequence[str],
                    strata: Sequence[str] = STRATA) -> list[dict]:
    """Every grid cell with its available count and status."""
    avail = available_cells(pool)
    rows = []
    for f in sorted(families):
        for lx in sorted(lexicons):
            for st in sorted(strata):
                n = avail.get((f, lx, st), 0)
                rows.append({"family": f, "lexicon": lx, "stratum": st,
                             "available": n,
                             "status": "OK" if n else "STRUCTURALLY_EMPTY"})
    return rows


def balanced(sites: Sequence[Site], limit: int = 0, *,
             dedupe: bool = True) -> list[Site]:
    """Round-robin across cells in canonical order. Deterministic.

    limit=0 returns every (de-duplicated) site. Any other limit keeps the cell
    proportions instead of truncating whichever cell came first. The output is
    identical for every permutation of `sites`.
    """
    pool = dedupe_within_cells(sites)[0] if dedupe else sorted(sites, key=canonical_key)
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


def cell_counts(sites: Sequence[Site], *, expected: Counter | None = None) -> dict:
    """Observed counts, the expected counts they are judged against, and gaps.

    `expected` should come from `available_cells(full_pool)`. A cell is EMPTY
    when the materials offer sites there but the sample took none -- the
    condition `assert_balanced` refuses.
    """
    obs = Counter(cell_key(s) for s in sites)
    exp = expected if expected is not None else obs
    empty = sorted(f"{f}/{p}/{st}" for (f, p, st), n in exp.items()
                   if n > 0 and obs.get((f, p, st), 0) == 0)
    return {
        "n": len(sites),
        "by_family": dict(Counter(family_of(s) for s in sites)),
        "by_stratum": dict(Counter(stratum(s) for s in sites)),
        "by_lexicon": dict(Counter(s.phi_id for s in sites)),
        "by_cell": {f"{f}/{p}/{st}": n for (f, p, st), n in sorted(obs.items())},
        "expected_by_cell": {f"{f}/{p}/{st}": n
                             for (f, p, st), n in sorted(exp.items())},
        "empty_cells": empty,
    }


def assert_balanced(sites: Sequence[Site], *, families: Sequence[str],
                    expected: Counter | None = None) -> None:
    """Refuse a sample that misses a family or any materially available cell."""
    seen = {family_of(s) for s in sites}
    missing = set(families) - seen
    if missing:
        raise AssertionError(
            f"sample covers only {sorted(seen)}; missing {sorted(missing)}. "
            f"This is defect P32-003 -- a first-N slice over a concatenated "
            f"list. Use sampling.balanced().")
    if expected is not None:
        empty = cell_counts(sites, expected=expected)["empty_cells"]
        if empty:
            raise AssertionError(
                f"sample is missing {len(empty)} materially available cell(s): "
                f"{empty[:6]}{' ...' if len(empty) > 6 else ''} "
                f"(defect P33-004). Raise the limit or use limit=0.")
