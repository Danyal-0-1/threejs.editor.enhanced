"""deltafam.py — a FAMILY of delta lexicons, parameterised by density and seed.

----------------------------------------------------------------------------
WHY A FAMILY INSTEAD OF ONE delta
----------------------------------------------------------------------------
Phase 3 shipped a single hand-designed `delta`. Parameterising it closes three
of the five components Phase 3 left unimplemented, in one change:

  1. DENSITY -- how many roles are remapped, hence how many SEMANTIC sites.
  2. COUNTERBALANCING -- the rotation seed changes WHICH spelling lands on
     which role, so no token is "always correct" across the dataset. Phase 3
     had no counterbalancing at all.
  3. HELD-OUT MAPPINGS -- train a predictor on some (density, seed) members,
     test on others. H4 requires held-out mappings and Phase 3 could not
     supply them from one lexicon.

----------------------------------------------------------------------------
WHY NOT MAXIMISE DENSITY
----------------------------------------------------------------------------
The ceiling is 306 of 387 sites (79%); the remaining 81 are T_CHAIN_OP, locked
LEXICAL by invariant I7. It is tempting to go straight there. Do not:

    H5 needs LOW-RISK, NON-COLLIDING sites as negative controls.

The repair claim is not "renaming helps" but "renaming ONLY the predicted-risky
sites helps more per changed symbol, and leaves ordinary sites alone". With
every role remapped there are no ordinary sites left, and the targeted-vs-global
comparison becomes untestable. Each member therefore keeps its unpermuted roles
as within-language controls, which is also what makes `identity_baseline` a
meaningful competitor rather than a formality.

----------------------------------------------------------------------------
SHAPE CLASSES, AND THE STRICT/ARITY TRADE
----------------------------------------------------------------------------
Phase 3 measured the rule: silent collisions require permutation WITHIN a
shape class. Groups available in 3DOM:

    sigils    {T_CLASS_SIGIL, T_ID_SIGIL}   (T_CHAIN_OP must follow CLASS, I7)
    types     {mesh, group, light, camera}
    pseudo    {selected, lasso}
    verbs     grouped by C8 signature

Only two verb groups are STRICTLY signature-matched -- {move, duplicate} and
{wireframe, castShadow, receiveShadow} -- so strict mode can permute just 5 of
15 verbs. To reach higher densities, `arity` mode permutes within equal-ARITY
groups instead (9 verbs share arity 1).

The honest cost of arity mode, stated here because it will otherwise be
discovered by a reviewer: swapping `recolor` with `setOpacity` keeps the
program parseable and changes the IR, so the collision is genuine, but the
argument KEY changes too (`{"color": "#111111"}` becomes
`{"opacity": "#111111"}`). The IR is well-formed and different, which is all
the collision classifier requires, but the resulting program is semantically
odd in a way a signature-matched swap is not. Use `strict` for the primary
arms; use `arity` only where the density target demands it, and report which
mode produced each member.
"""

from __future__ import annotations

import datetime
import json
import os
import random
from dataclasses import dataclass

from phase3_2 import _vendor  # noqa: F401

import canonicalize as C  # noqa: E402
import phi as P  # noqa: E402

OUT_DIR = _vendor.CANDIDATES

SIGIL_GROUP = ["T_CLASS_SIGIL", "T_ID_SIGIL"]
CHAIN_FOLLOWS = "T_CHAIN_OP"            # I7: must match T_CLASS_SIGIL
TYPE_GROUP = ["T_TYPE_MESH", "T_TYPE_GROUP", "T_TYPE_LIGHT", "T_TYPE_CAMERA"]
PSEUDO_GROUP = ["T_PSEUDO_SELECTED", "T_PSEUDO_LASSO"]

_VERB_TERMINAL = {
    "recolor": "T_VERB_RECOLOR", "scale": "T_VERB_SCALE", "move": "T_VERB_MOVE",
    "rotate": "T_VERB_ROTATE", "delete": "T_VERB_DELETE", "spin": "T_VERB_SPIN",
    "duplicate": "T_VERB_DUPLICATE", "setMaterial": "T_VERB_SETMATERIAL",
    "setOpacity": "T_VERB_SETOPACITY", "setVisible": "T_VERB_SETVISIBLE",
    "wireframe": "T_VERB_WIREFRAME", "metalness": "T_VERB_METALNESS",
    "roughness": "T_VERB_ROUGHNESS", "castShadow": "T_VERB_CASTSHADOW",
    "receiveShadow": "T_VERB_RECEIVESHADOW",
}


def verb_groups(mode: str) -> list[list[str]]:
    """Permutable verb groups. `strict` = identical C8 signature; `arity` = same arg count."""
    buckets: dict[tuple, list[str]] = {}
    for verb, sig in C.SIGNATURES.items():
        key = sig if mode == "strict" else (len(sig),)
        buckets.setdefault(key, []).append(_VERB_TERMINAL[verb])
    return [sorted(g) for g in buckets.values() if len(g) > 1]


def _groups_for(mode: str) -> list[tuple[str, list[str]]]:
    """All permutable groups, ordered cheapest-collision-first.

    Sigils lead because they are the cleanest contrast in the whole project:
    both roles are `sigil IDENT` in the inner stream, the competitor is the
    canonical CSS token, and no argument semantics are involved.
    """
    out = [("sigil", SIGIL_GROUP), ("type", TYPE_GROUP), ("pseudo", PSEUDO_GROUP)]
    out += [(f"verb{i}", g) for i, g in enumerate(verb_groups(mode))]
    return out


@dataclass(frozen=True)
class Member:
    phi_id: str
    density_target: float
    seed: int
    mode: str
    permuted: tuple[str, ...]
    n_substitutable: int

    @property
    def density_actual(self) -> float:
        return len(self.permuted) / self.n_substitutable


def build(density: float, seed: int, *, mode: str = "strict",
          table: P.TerminalTable | None = None) -> tuple[dict, Member]:
    """Construct one family member. Returns (phi blob, Member)."""
    table = table or P.load_terminals()
    spell = {t.id: t.spelling for t in table.terminals}
    subst = list(table.substitutable_ids)

    rng = random.Random(seed)
    groups = _groups_for(mode)
    rng.shuffle(groups)                       # which groups get used at low density

    out: dict[str, str] = {}
    permuted: list[str] = []
    budget = density * len(subst)

    for _name, members in groups:
        if len(permuted) >= budget:
            break
        g = list(members)
        rng.shuffle(g)                        # counterbalancing: rotation order
        for i, tid in enumerate(g):
            out[tid] = spell[g[(i + 1) % len(g)]]
        permuted += g
        if "T_CLASS_SIGIL" in g:
            out[CHAIN_FOLLOWS] = out["T_CLASS_SIGIL"]       # I7

    for t in table.terminals:                 # everything else stays at identity
        if t.substitutable and t.id not in out:
            out[t.id] = t.spelling

    phi_id = f"d{int(round(density*100)):02d}s{seed}" + ("" if mode == "strict" else "a")
    blob = {
        "phi_id": phi_id,
        "targets_grammar": table.grammar_version,
        "generated": datetime.datetime.now(datetime.timezone.utc)
                     .isoformat(timespec="seconds"),
        "construct": f"delta family member - density {density}, seed {seed}, mode {mode}",
        "map": {tid: {"from": spell[tid], "to": to} for tid, to in out.items()},
        "overload_groups": [["T_CHAIN_OP", "T_CLASS_SIGIL"]],
        "frozen": list(table.non_substitutable_ids),
        "notes": (
            f"Generated by phase3_2/src/phase3_2/deltafam.py. Identity except "
            f"within-shape-class permutations of: {sorted(set(permuted))}. "
            f"Rotation order is seeded ({seed}) so members counterbalance which "
            f"spelling carries which role. Mode={mode}."
            + (" ARITY MODE: verb swaps are arity-matched but not "
               "signature-matched, so argument KEYS change; see the module "
               "docstring." if mode == "arity" else "")),
    }
    member = Member(phi_id=phi_id, density_target=density, seed=seed, mode=mode,
                    permuted=tuple(sorted(set(permuted))), n_substitutable=len(subst))
    return blob, member


def write(blob: dict) -> str:
    path = os.path.join(OUT_DIR, f"phi_{blob['phi_id']}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(blob, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path


def build_family(densities=(0.25, 0.50, 0.75), seeds=(1, 2, 3),
                 *, mode_for_high: float = 0.5) -> list[tuple[dict, Member]]:
    """The default family: 3 densities x 3 seeds = 9 counterbalanced members.

    Densities above `mode_for_high` switch to arity mode, because strict mode
    cannot reach them -- only 5 of 15 verbs are signature-matched. The mode is
    recorded on every member and encoded in its phi_id suffix, so no analysis
    can mix the two without noticing.
    """
    out = []
    for d in densities:
        mode = "strict" if d <= mode_for_high else "arity"
        for s in seeds:
            out.append(build(d, s, mode=mode))
    return out
