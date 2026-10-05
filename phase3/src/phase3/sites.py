"""sites.py — decision-site enumeration and MECHANICAL collision classification.

This is the centre of Phase 3. Everything else (calibration, forced-prefix
scoring, the extinction ladder, the linter, the repair) consumes what this
module produces.

----------------------------------------------------------------------------
WHAT A "SITE" IS
----------------------------------------------------------------------------
A **decision site** is one occurrence of one substitutable terminal in one
concrete program, together with the two spellings that compete there:

    c  the CORRECT spelling in this language           φ(tid)
    q  the FAMILIAR spelling of that same role         identity(tid)   (= 3DOM)

`q` is the spelling a model trained on CSS/jQuery expects to see *for that
role*. If the language remapped the role, `q` is wrong — but whether it is
*dangerously* wrong is an empirical question about the grammar, and this module
answers it by construction rather than by argument.

----------------------------------------------------------------------------
THE COLLISION CLASSIFIER — AND WHY IT IS THE WHOLE EXPERIMENT
----------------------------------------------------------------------------
The literature review requires a site where the correct and familiar-incorrect
forms "are both grammar-valid but produce different canonical IRs". That is not
a property you can assume; it is a property of the particular φ-map, and it is
cheap to TEST. Substitute q for c at the exact offset and re-run the pipeline:

    NONE      c == q. The role was not remapped here. No contrast exists.
    LEXICAL   the variant does not lex or does not parse. The familiar habit
              produces a LOUD failure: the harness sees LEX_FAIL / PARSE_FAIL.
    BENIGN    the variant parses to the SAME canonical IR. q is an alias; a
              model that "reverts" here is still correct. No contrast exists.
    SEMANTIC  the variant parses AND yields a DIFFERENT canonical IR.
              *** This is the only class that satisfies the review's
              requirement, and the only one where reversion is SILENT. ***

MEASURED RESULT, not an assumption: under the shipped `alpha` lexicon the
class-sigil site is **LEXICAL**, not SEMANTIC. alpha is a 5-cycle derangement
of {. # : > *}, and `.` is bound to T_WILDCARD, which takes no identifier — so
the familiar `.door` is a parse error, not a wrong-IR program. Run
`scripts/site_census.py` for the full table. The consequence is in README.md:
Phase 3 must *design* φ-maps that place silent collisions where it wants them,
and the design rule it derives is

    SILENT COLLISIONS REQUIRE PERMUTATION **WITHIN A SHAPE CLASS**.

Two roles collide silently only if they accept the same syntactic shape, so
swapping them keeps the program parseable while changing its meaning. In 3DOM
the within-shape classes are: {T_CLASS_SIGIL, T_ID_SIGIL} (both `sigil IDENT`
inside a quoted selector), the 15 operation verbs, the 4 type keywords, and
{T_PSEUDO_SELECTED, T_PSEUDO_LASSO}. Permuting ACROSS classes (as alpha does)
yields loud failures instead.

----------------------------------------------------------------------------
WHY THE LEXER LOCATES SITES, AND A NAIVE str.replace MUST NOT
----------------------------------------------------------------------------
`#` is alpha's class sigil AND the first character of every colour literal
`'#333333'`. A textual replace would silently corrupt arguments and produce a
"collision" that is an artifact of the edit. Sites are therefore located with
`transpiler.lex`, which returns `(token_type, value, char_offset)` and already
knows the two-level outer/inner distinction. Offsets come from the lexer; this
module never searches for a substring.
"""

from __future__ import annotations

import dataclasses
import enum
from dataclasses import dataclass
from typing import Iterator, Sequence

from phase3 import _vendor  # noqa: F401  — side-effecting: wires sys.path

import canonicalize as C  # noqa: E402
import phi as P  # noqa: E402
import transpiler as T  # noqa: E402

# ---------------------------------------------------------------------------
# token type -> terminal id, mirroring Lexicon.of() in transpiler.py.
#
# These names are NOT free parameters: they are the token types the vendored
# lexer actually emits. If transpiler.Lexicon.of() is ever changed upstream,
# `test_sites.py::test_token_type_map_matches_lexer` fails, because the map is
# verified against a freshly lexed program rather than trusted.
# ---------------------------------------------------------------------------
SIMPLE_TOKEN_TERMINAL: dict[str, str] = {
    "DOLLAR": "T_SELECTOR_ENTRY",
    "FUNC": "T_FUNCTION",
    "DOT": "T_CHAIN_OP",
    "HASH": "T_ID_SIGIL",
    "CSIG": "T_CLASS_SIGIL",
    "COLON": "T_PSEUDO_SIGIL",
    "GT": "T_CHILD",
    "STAR": "T_WILDCARD",
}

# Token types whose terminal id must be recovered from the token VALUE, because
# several terminals share one token type (all 15 verbs lex as "VERB").
VALUE_KEYED_TOKENS = frozenset({"VERB"})


class CollisionClass(enum.Enum):
    NONE = "none"
    LEXICAL = "lexical"
    BENIGN = "benign"
    SEMANTIC = "semantic"

    @property
    def is_usable(self) -> bool:
        """Only SEMANTIC sites satisfy the review's both-valid/different-IR rule."""
        return self is CollisionClass.SEMANTIC


@dataclass(frozen=True)
class Site:
    """One decision site. Serialisable; see `records.py` for the on-disk form."""

    site_id: str
    phi_id: str
    template_id: str
    terminal_id: str
    role: str
    occurrence: int            # 0-based index among same-terminal occurrences
    char_offset: int           # offset of `correct` in `program`
    inner: bool                # inside a quoted selector (CSS-like context)?

    program: str               # the full CORRECT program in this language
    prefix: str                # program[:char_offset] — what precedes the decision
    correct: str               # c = φ(terminal_id)
    competitor: str            # q = identity(terminal_id), the familiar spelling

    collision: CollisionClass
    competitor_binds_to: str | None   # which terminal q denotes under φ, if any
    ir_hash_correct: str
    ir_hash_competitor: str | None    # None when the variant does not parse
    variant_program: str              # program with q substituted at this site
    note: str = ""

    @property
    def is_usable(self) -> bool:
        return self.collision.is_usable


# ---------------------------------------------------------------------------
# terminal-id recovery
# ---------------------------------------------------------------------------

def _inverse_spelling_map(phi: P.PhiMap) -> dict[str, list[str]]:
    """alien spelling -> [terminal ids that carry it under φ].

    A list, not a scalar: overload groups (I7) deliberately give several ids one
    spelling, so {'.': [T_CHAIN_OP, T_CLASS_SIGIL]} is correct and expected for
    3DOM. Collapsing it to a scalar would silently drop one of the two roles.
    """
    out: dict[str, list[str]] = {}
    for term in phi.table.terminals:
        if term.substitutable:
            out.setdefault(phi.spelling(term.id), []).append(term.id)
    return out


def _terminal_of_token(tok_type: str, value: str, phi: P.PhiMap) -> str | None:
    """Recover the terminal id behind one lexed token, or None if not a site."""
    if tok_type in SIMPLE_TOKEN_TERMINAL:
        return SIMPLE_TOKEN_TERMINAL[tok_type]
    if tok_type.startswith("TYPE_") or tok_type in VALUE_KEYED_TOKENS or tok_type.isupper():
        # Verbs, type keywords and pseudo keywords: identify by spelling.
        hits = _inverse_spelling_map(phi).get(value, [])
        # Prefer a hit whose token type matches, so a spelling shared between a
        # verb and a type keyword cannot be mis-attributed.
        for tid in hits:
            term = phi.table.by_id[tid]
            if tok_type == "VERB" and term.role == "operation verb":
                return tid
            if tok_type.startswith("TYPE_") and term.role == "type selector keyword":
                return tid
            if term.role == "pseudo-selector keyword" and tok_type == term.spelling.upper():
                return tid
        return hits[0] if len(hits) == 1 else None
    return None


# ---------------------------------------------------------------------------
# classification
# ---------------------------------------------------------------------------

def _safe_ir_hash(src: str, phi: P.PhiMap) -> tuple[str | None, str]:
    """(content hash, note). None hash means the program did not reach an IR."""
    try:
        if T.num_parses(src, phi) != 1:
            return None, f"num_parses != 1 ({T.num_parses(src, phi)})"
    except (T.LexError, T.ParseError, T.AmbiguityError) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    except Exception as exc:                                  # pragma: no cover
        return None, f"{type(exc).__name__}: {exc}"
    try:
        return C.content_hash(T.parse(src, phi)), ""
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def classify(program: str, phi: P.PhiMap, *, template_id: str = "t?",
             identity: P.PhiMap | None = None) -> list[Site]:
    """Enumerate and classify every substitutable decision site in `program`.

    `program` must be a CORRECT program in language `phi`. Sites are located by
    lexing it; the competitor variant is built by splicing at the lexer's own
    char offset, never by string search.
    """
    identity = identity or P.identity_phi(phi.table)
    base_hash, base_note = _safe_ir_hash(program, phi)
    if base_hash is None:
        raise ValueError(f"template {template_id!r} is not a valid {phi.phi_id} "
                         f"program: {base_note}")

    inverse = _inverse_spelling_map(phi)
    toks = T.lex(program, phi)

    # Which tokens sit inside a quoted selector? The lexer's two-level contract
    # says the inner stream is exactly the span between the selector quotes.
    inner_types = {"HASH", "CSIG", "COLON", "GT", "STAR"}

    seen: dict[str, int] = {}
    sites: list[Site] = []

    for tok_type, value, offset in toks:
        tid = _terminal_of_token(tok_type, value, phi)
        if tid is None:
            continue
        term = phi.table.by_id[tid]
        if not term.substitutable:
            continue

        occ = seen.get(tid, 0)
        seen[tid] = occ + 1

        c = phi.spelling(tid)
        q = identity.spelling(tid)
        if value != c:                                         # defensive
            continue

        is_inner = tok_type in inner_types or tok_type.startswith("TYPE_")

        if c == q:
            sites.append(Site(
                site_id=f"{phi.phi_id}:{template_id}:{tid}:{occ}",
                phi_id=phi.phi_id, template_id=template_id, terminal_id=tid,
                role=term.role, occurrence=occ, char_offset=offset,
                inner=is_inner, program=program, prefix=program[:offset],
                correct=c, competitor=q, collision=CollisionClass.NONE,
                competitor_binds_to=tid, ir_hash_correct=base_hash,
                ir_hash_competitor=base_hash, variant_program=program,
                note="role not remapped in this language"))
            continue

        variant = program[:offset] + q + program[offset + len(c):]
        var_hash, var_note = _safe_ir_hash(variant, phi)

        if var_hash is None:
            klass = CollisionClass.LEXICAL
        elif var_hash == base_hash:
            klass = CollisionClass.BENIGN
        else:
            klass = CollisionClass.SEMANTIC

        bound = inverse.get(q, [])
        sites.append(Site(
            site_id=f"{phi.phi_id}:{template_id}:{tid}:{occ}",
            phi_id=phi.phi_id, template_id=template_id, terminal_id=tid,
            role=term.role, occurrence=occ, char_offset=offset,
            inner=is_inner, program=program, prefix=program[:offset],
            correct=c, competitor=q, collision=klass,
            competitor_binds_to=",".join(bound) if bound else None,
            ir_hash_correct=base_hash, ir_hash_competitor=var_hash,
            variant_program=variant, note=var_note))

    return sites


def census(sites: Sequence[Site]) -> dict[str, dict[str, int]]:
    """{phi_id: {collision class: count}} — the headline inventory table."""
    out: dict[str, dict[str, int]] = {}
    for s in sites:
        out.setdefault(s.phi_id, {k.value: 0 for k in CollisionClass})
        out[s.phi_id][s.collision.value] += 1
    return out


def usable(sites: Sequence[Site]) -> list[Site]:
    return [s for s in sites if s.is_usable]


def prefix_collisions(sites: Sequence[Site]) -> dict[str, list[Site]]:
    """Sites that share a byte-identical prefix but disagree on `correct`.

    A MATERIALS-VALIDATION CHECK, not a bug report. Many 3DOM programs open
    identically — `(function(){ $S('#wheel')#` is extremely common — so two
    sites in different templates can present a model with exactly the same
    context while expecting different spellings.

    Why it matters, in two places:

      * H4 (site prediction). The risk score is a function of (prefix,
        candidates). If two sites share a prefix and disagree about which
        candidate is correct, NO prefix-conditioned predictor can be right
        about both. They put a ceiling on achievable AUROC, and that ceiling
        belongs in the paper rather than being discovered by a reviewer.
      * Any analysis that treats sites as independent observations. Colliding
        sites are not independent; they are the same stimulus counted twice.

    Returns {prefix: [sites]} for prefixes with more than one distinct
    `correct` spelling. An empty dict means every site is identifiable from
    its context.
    """
    by_prefix: dict[str, list[Site]] = {}
    for s in sites:
        by_prefix.setdefault(s.prefix, []).append(s)
    return {p: ss for p, ss in by_prefix.items()
            if len({x.correct for x in ss}) > 1}


def dedupe_by_prefix(sites: Sequence[Site]) -> list[Site]:
    """One site per distinct prefix, first occurrence wins.

    Use when a prefix-conditioned measurement must be well defined. This
    DISCARDS data, so it is never applied silently inside an analysis — the
    caller asks for it and reports how many sites it dropped.
    """
    seen: set[str] = set()
    out: list[Site] = []
    for s in sites:
        if s.prefix not in seen:
            seen.add(s.prefix)
            out.append(s)
    return out


def iter_templates(phi: P.PhiMap, programs: Sequence[str]) -> Iterator[Site]:
    for i, prog in enumerate(programs):
        yield from classify(prog, phi, template_id=f"t{i:03d}")


def to_dict(site: Site) -> dict:
    d = dataclasses.asdict(site)
    d["collision"] = site.collision.value
    return d
