"""sites2.py — the Phase 3 collision classifier, generalised over grammar families.

The TAXONOMY is Phase 3's and is imported unchanged: `Site`, `CollisionClass`,
`census`, `usable`, `prefix_collisions`, `dedupe_by_prefix`. Only the plumbing
changes -- `classify` now takes a `Backend` instead of calling `transpiler`
directly, so the identical classification logic runs over both grammar
families.

Keeping the taxonomy shared is deliberate. A cross-family difference in
results must come from the grammar, not from a reimplemented classifier, so
the classifier is the thing held fixed.

THE CLASSIFICATION RULE, unchanged from Phase 3
-----------------------------------------------
    c = phi(tid)            the correct spelling here
    q = identity(tid)       the familiar 3DOM spelling of the SAME role

    c == q                            -> NONE      (role not remapped)
    variant does not lex/parse        -> LEXICAL   (loud failure)
    variant parses, SAME IR hash      -> BENIGN    (alias; no contrast)
    variant parses, DIFFERENT IR hash -> SEMANTIC  (the only usable class)

Only SEMANTIC satisfies the review's "both grammar-valid, different canonical
IR" requirement, and it is TESTED rather than assumed.
"""

from __future__ import annotations

from typing import Sequence

from phase3_2 import _vendor  # noqa: F401

import canonicalize as C  # noqa: E402
import phi as P  # noqa: E402

# the taxonomy and the analysis helpers come from Phase 3, unchanged
from phase3.sites import (  # noqa: E402
    CollisionClass, Site, census, dedupe_by_prefix, prefix_collisions,
    to_dict, usable, SIMPLE_TOKEN_TERMINAL, VALUE_KEYED_TOKENS,
)

__all__ = ["CollisionClass", "Site", "census", "dedupe_by_prefix",
           "prefix_collisions", "to_dict", "usable", "classify"]


def _inverse_spelling_map(phi: P.PhiMap) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for term in phi.table.terminals:
        if term.substitutable:
            out.setdefault(phi.spelling(term.id), []).append(term.id)
    return out


def _terminal_of_token(tok_type: str, value: str, phi: P.PhiMap) -> str | None:
    if tok_type in SIMPLE_TOKEN_TERMINAL:
        return SIMPLE_TOKEN_TERMINAL[tok_type]
    hits = _inverse_spelling_map(phi).get(value, [])
    for tid in hits:
        term = phi.table.by_id[tid]
        if tok_type == "VERB" and term.role == "operation verb":
            return tid
        if tok_type.startswith("TYPE_") and term.role == "type selector keyword":
            return tid
        if term.role == "pseudo-selector keyword" and tok_type == term.spelling.upper():
            return tid
    return hits[0] if len(hits) == 1 else None


def _safe_ir_hash(src: str, phi: P.PhiMap, backend) -> tuple[str | None, str]:
    """(content hash, note). None means the program never reached an IR."""
    try:
        n = backend.num_parses(src, phi)
        if n != 1:
            return None, f"num_parses != 1 ({n})"
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"
    try:
        return C.content_hash(backend.parse(src, phi)), ""
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def classify(program: str, phi: P.PhiMap, backend, *, template_id: str = "t?",
             identity: P.PhiMap | None = None) -> list[Site]:
    """Enumerate and classify every substitutable decision site in `program`.

    `site_id` carries the FAMILY as well as the lexicon, because the same
    template and terminal occur in both families and their ids would otherwise
    collide in a merged result file.
    """
    identity = identity or P.identity_phi(phi.table)
    base_hash, base_note = _safe_ir_hash(program, phi, backend)
    if base_hash is None:
        raise ValueError(f"{backend.family}/{template_id} is not a valid "
                         f"{phi.phi_id} program: {base_note}")

    inverse = _inverse_spelling_map(phi)
    inner_types = {"HASH", "CSIG", "COLON", "GT", "STAR"}
    seen: dict[str, int] = {}
    sites: list[Site] = []

    for tok_type, value, offset in backend.lex(program, phi):
        tid = _terminal_of_token(tok_type, value, phi)
        if tid is None:
            continue
        term = phi.table.by_id[tid]
        if not term.substitutable:
            continue

        occ = seen.get(tid, 0)
        seen[tid] = occ + 1

        c, q = phi.spelling(tid), identity.spelling(tid)
        if value != c:
            continue
        is_inner = tok_type in inner_types or tok_type.startswith("TYPE_")
        sid = f"{backend.family}:{phi.phi_id}:{template_id}:{tid}:{occ}"

        if c == q:
            sites.append(Site(
                site_id=sid, phi_id=phi.phi_id, template_id=template_id,
                terminal_id=tid, role=term.role, occurrence=occ,
                char_offset=offset, inner=is_inner, program=program,
                prefix=program[:offset], correct=c, competitor=q,
                collision=CollisionClass.NONE, competitor_binds_to=tid,
                ir_hash_correct=base_hash, ir_hash_competitor=base_hash,
                variant_program=program, note="role not remapped"))
            continue

        variant = program[:offset] + q + program[offset + len(c):]
        var_hash, var_note = _safe_ir_hash(variant, phi, backend)
        if var_hash is None:
            klass = CollisionClass.LEXICAL
        elif var_hash == base_hash:
            klass = CollisionClass.BENIGN
        else:
            klass = CollisionClass.SEMANTIC

        bound = inverse.get(q, [])
        sites.append(Site(
            site_id=sid, phi_id=phi.phi_id, template_id=template_id,
            terminal_id=tid, role=term.role, occurrence=occ,
            char_offset=offset, inner=is_inner, program=program,
            prefix=program[:offset], correct=c, competitor=q, collision=klass,
            competitor_binds_to=",".join(bound) if bound else None,
            ir_hash_correct=base_hash, ir_hash_competitor=var_hash,
            variant_program=variant, note=var_note))

    return sites


# ---------------------------------------------------------------------------
# site stratification — the free test for the 3D-knowledge question
# ---------------------------------------------------------------------------
# The sigil decision ('.' vs '#') is a pure CSS lexical prior: you do not need
# to know what a mesh is to type the right sigil. The VERB decision is not --
# picking `scale` over `move` requires understanding the request, so verb sites
# CONFLATE surface collision with 3D-domain competence.
#
# Stratifying Arm A by these strata costs nothing and decides the question:
#   similar effect at both  -> domain knowledge is not driving it
#   effect only at verbs    -> domain-competence confound; sigil is the clean arm

SIGIL_TERMINALS = frozenset({"T_CLASS_SIGIL", "T_ID_SIGIL", "T_PSEUDO_SIGIL",
                             "T_CHILD", "T_WILDCARD", "T_CHAIN_OP"})
TYPE_TERMINALS = frozenset({"T_TYPE_MESH", "T_TYPE_GROUP", "T_TYPE_LIGHT",
                            "T_TYPE_CAMERA", "T_PSEUDO_SELECTED", "T_PSEUDO_LASSO"})


def stratum(site: Site) -> str:
    """'sigil' (pure surface) | 'verb' (surface + domain) | 'keyword'."""
    if site.terminal_id in SIGIL_TERMINALS:
        return "sigil"
    if site.terminal_id in TYPE_TERMINALS:
        return "keyword"
    return "verb"


def by_stratum(sites: Sequence[Site]) -> dict[str, list[Site]]:
    out: dict[str, list[Site]] = {}
    for s in sites:
        out.setdefault(stratum(s), []).append(s)
    return out
