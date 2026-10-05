"""backends.py — the language-backend abstraction, and the SECOND grammar family.

----------------------------------------------------------------------------
WHY THIS FILE EXISTS
----------------------------------------------------------------------------
Phase 3's site classifier called `transpiler.lex` / `transpiler.parse`
directly, so it could only ever see ONE concrete syntax. The literature review
requires generalisation across independently designed **grammar families**, and
Phase 3's four lexicons do not qualify: invariants I1-I4 freeze the
non-terminal set and the shape of the productions, and `render_grammar.py`
asserts that phi=identity reproduces the Phase 1 grammar byte for byte. Four
lexicons over one grammar are, by construction, exactly what the review calls
"cosmetic renamings of one grammar".

A `Backend` is one concrete syntax: how to lex it, parse it, and lower it to
the shared canonical IR. Two exist:

    dom   the Phase 1/2 syntax: IIFE wrapper + jQuery-style fluent chaining
          (function(){ $S('.wheel').recolor('#111111'); })();

    blk   NEW in Phase 3.2: block form. No IIFE, no method chaining, no
          parentheses; the selector is a block header and operations are
          semicolon-terminated statements inside braces.
          $S '.wheel' { recolor '#111111'; scale 2; }

----------------------------------------------------------------------------
WHAT MAKES `blk` A REAL SECOND FAMILY AND NOT ANOTHER RENAMING
----------------------------------------------------------------------------
Different NON-TERMINALS and different production SHAPES:

  | aspect              | dom                      | blk                     |
  |---------------------|--------------------------|-------------------------|
  | wrapper             | IIFE `(function(){…})();`| none                    |
  | op attachment       | fluent chain `.op(a)`    | statement in a block    |
  | argument delimiters | parentheses              | none (juxtaposition)    |
  | grouping            | chain order              | braces                  |
  | T_FUNCTION          | used                     | **absent**              |
  | T_CHAIN_OP          | used                     | **absent**              |
  | T_LPAREN/T_RPAREN   | used                     | **absent**              |

What is held FIXED on purpose:

  * the frozen terminal table (`terminals.json`) — so the SAME phi-maps apply
    to both families unchanged. Without this, cross-family transfer would be
    untestable, because the mapping would differ along with the grammar.
  * the inner selector sub-language — `'.wheel'` parses identically in both.
    This is the scientific point: the class/id sigil collision lives in the
    INNER language, so it transfers across families, and a predictor trained
    on `dom` sites can be tested on `blk` sites with the competitor identity
    held constant.
  * the canonical IR. `$S '.wheel' { recolor 'x'; scale 2; }` and
    `$S('.wheel').recolor('x').scale(2)` produce byte-identical canonical JSON
    and the same content hash. `tests/test_blk.py` asserts this over the whole
    corpus; it is the proof that `blk` is a re-surfacing and not a new language.

Because `blk` reuses the vendored inner-selector parser and transformer rather
than reimplementing them, the shared sub-language cannot drift between
families — a bug there would show up as an IR mismatch in both, not as a
spurious cross-family difference.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterator, Protocol

from phase3_2 import _vendor  # noqa: F401

import canonicalize as C  # noqa: E402
import phi as P  # noqa: E402
import transpiler as T  # noqa: E402

Token = tuple[str, str, int]          # (token type, value, char offset)


# ---------------------------------------------------------------------------
# a generic, offset-accurate site lexer shared by both families
# ---------------------------------------------------------------------------
# Both families use the same quoting convention and the same two-level
# contract: outside quotes is the OUTER stream, inside a quoted selector is the
# INNER stream. Site location only needs to find substitutable terminals and
# their offsets -- lark does the real parsing -- so one scanner serves both and
# there is no second lexer to keep in sync.
#
# The hazard this exists to avoid is unchanged from Phase 3: `#` is both a
# sigil spelling and the first character of every colour literal '#111111'. A
# textual search would corrupt arguments and invent collisions.

IDENT_CHARS = set("abcdefghijklmnopqrstuvwxyz"
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")


def _tables(phi: P.PhiMap):
    lex = T.Lexicon.of(phi)
    return (lex.outer_symbols, lex.outer_words,
            lex.inner_symbols, lex.inner_words)


def scan_sites(src: str, phi: P.PhiMap) -> Iterator[Token]:
    """Yield (token_type, value, offset) for every substitutable terminal.

    Quote handling decides the level: the first quoted string in a statement is
    a SELECTOR (inner stream); later quoted strings are ARGUMENTS and are
    skipped entirely, which is what keeps '#111111' from being read as a sigil.
    """
    outer_sym, outer_word, inner_sym, inner_word = _tables(phi)
    i, n = 0, len(src)
    selector_seen_in_stmt = False

    while i < n:
        ch = src[i]

        # ---- quoted string: selector (inner) or argument (skip) -----------
        if ch in "'\"":
            end = src.find(ch, i + 1)
            if end < 0:
                return                                   # unterminated
            body, body_at = src[i + 1:end], i + 1
            if not selector_seen_in_stmt:
                yield from _scan_inner(body, body_at, inner_sym, inner_word)
                selector_seen_in_stmt = True
            i = end + 1
            continue

        if ch == ";":                                    # statement boundary
            selector_seen_in_stmt = False
            i += 1
            continue

        # ---- outer symbols, longest match first ---------------------------
        hit = next((s for s, _t in outer_sym if src.startswith(s, i)), None)
        if hit:
            yield (dict(outer_sym)[hit], hit, i)
            i += len(hit)
            continue

        # ---- outer words ---------------------------------------------------
        if ch in IDENT_CHARS:
            j = i
            while j < n and src[j] in IDENT_CHARS:
                j += 1
            word = src[i:j]
            if word in outer_word:
                yield (outer_word[word], word, i)
            i = j
            continue

        i += 1


def _scan_inner(body: str, base: int, inner_sym, inner_word) -> Iterator[Token]:
    i, n = 0, len(body)
    while i < n:
        hit = next((s for s, _t in inner_sym if body.startswith(s, i)), None)
        if hit:
            yield (dict(inner_sym)[hit], hit, base + i)
            i += len(hit)
            continue
        if body[i] in IDENT_CHARS:
            j = i
            while j < n and body[j] in IDENT_CHARS:
                j += 1
            word = body[i:j]
            if word in inner_word:
                yield (inner_word[word], word, base + i)
            i = j
            continue
        i += 1


# ---------------------------------------------------------------------------
# backend protocol
# ---------------------------------------------------------------------------

class Backend(Protocol):
    family: str

    def lex(self, src: str, phi: P.PhiMap) -> list[Token]: ...
    def num_parses(self, src: str, phi: P.PhiMap) -> int: ...
    def parse(self, src: str, phi: P.PhiMap) -> C.IRProgram: ...
    def render(self, ir: C.IRProgram, phi: P.PhiMap) -> str: ...


# ---------------------------------------------------------------------------
# family 1 — dom (Phase 1/2 syntax, unchanged)
# ---------------------------------------------------------------------------

@dataclass
class DomBackend:
    family: str = "dom"

    def lex(self, src, phi):
        return list(scan_sites(src, phi))

    def num_parses(self, src, phi):
        return T.num_parses(src, phi)

    def parse(self, src, phi):
        return T.parse(src, phi)

    def render(self, ir, phi):
        return T.emit(ir, phi)


# ---------------------------------------------------------------------------
# family 2 — blk (new)
# ---------------------------------------------------------------------------

BLK_GRAMMAR = r"""
program   : block*
block     : ENTRY STRING "{" stmt* "}"
stmt      : verb arglist? ";"
arglist   : argument ("," argument)*
argument  : NUMBER | STRING
verb      : V_RECOLOR | V_SCALE | V_MOVE | V_ROTATE | V_DELETE | V_SPIN
          | V_DUPLICATE | V_SETMATERIAL | V_SETOPACITY | V_SETVISIBLE
          | V_WIREFRAME | V_METALNESS | V_ROUGHNESS | V_CASTSHADOW
          | V_RECEIVESHADOW

ENTRY           : "{{T_SELECTOR_ENTRY}}"
V_RECOLOR       : "{{T_VERB_RECOLOR}}"
V_SCALE         : "{{T_VERB_SCALE}}"
V_MOVE          : "{{T_VERB_MOVE}}"
V_ROTATE        : "{{T_VERB_ROTATE}}"
V_DELETE        : "{{T_VERB_DELETE}}"
V_SPIN          : "{{T_VERB_SPIN}}"
V_DUPLICATE     : "{{T_VERB_DUPLICATE}}"
V_SETMATERIAL   : "{{T_VERB_SETMATERIAL}}"
V_SETOPACITY    : "{{T_VERB_SETOPACITY}}"
V_SETVISIBLE    : "{{T_VERB_SETVISIBLE}}"
V_WIREFRAME     : "{{T_VERB_WIREFRAME}}"
V_METALNESS     : "{{T_VERB_METALNESS}}"
V_ROUGHNESS     : "{{T_VERB_ROUGHNESS}}"
V_CASTSHADOW    : "{{T_VERB_CASTSHADOW}}"
V_RECEIVESHADOW : "{{T_VERB_RECEIVESHADOW}}"

STRING    : /'[^'\n]*'/ | /"[^"\n]*"/
NUMBER    : /[+-]?[0-9]+(\.[0-9]+)?/
LAYOUT    : /[ \t\r\n]+/
%ignore LAYOUT
"""

_BLK_CACHE: dict[str, object] = {}


def _blk_parser(phi: P.PhiMap):
    key = phi.phi_id + "|" + repr(sorted(phi.substitutions.items()))
    if key not in _BLK_CACHE:
        from lark import Lark
        src = P.render_slots(BLK_GRAMMAR, phi)
        _BLK_CACHE[key] = Lark(src, start="program", parser="earley",
                               ambiguity="explicit", lexer="dynamic")
    return _BLK_CACHE[key]


@dataclass
class BlkBackend:
    """Block-form syntax. Shares the inner selector language with `dom`.

    NOTE on `program : block*` (not `block+`). The empty program is derivable
    on purpose. Phase 1 ships `(function(){})();` -- a program with zero
    operations, whose canonical IR is `{"ops":[]}`. Under D5 that is a PARSE
    SUCCESS and a TASK FAILURE, and the reach detector has to be able to tell
    it apart from a parse failure. With `block+` the blk rendering of an empty
    IR (the empty string) would not parse, and the family would silently
    disagree with `dom` on exactly the most plausible null output a small model
    emits. Caught by `test_blk.py::test_ir_roundtrip_whole_corpus`.
    """

    family: str = "blk"

    def lex(self, src, phi):
        return list(scan_sites(src, phi))

    def _tree(self, src, phi):
        from lark.exceptions import LarkError
        try:
            return _blk_parser(phi).parse(src)
        except LarkError as exc:
            raise T.ParseError(f"{type(exc).__name__}: {exc}".split("\n")[0]) from exc

    def num_parses(self, src, phi):
        tree = self._tree(src, phi)
        ambig = sum(1 for n in tree.iter_subtrees() if n.data == "_ambig")
        if ambig:
            raise T.AmbiguityError(f"{ambig} ambiguous node(s) (I10)")
        return 1

    def parse(self, src, phi):
        """blk text -> the SAME canonical IR the dom family produces.

        The inner selector is parsed with the VENDORED selector parser and
        transformer, so the shared sub-language cannot drift between families.
        """
        from lark.exceptions import LarkError
        tree = self._tree(src, phi)
        ambig = sum(1 for n in tree.iter_subtrees() if n.data == "_ambig")
        if ambig:
            raise T.AmbiguityError(f"{ambig} ambiguous node(s) (I10)")

        _outer, inner_parser = T.parsers_for(phi)
        _PT, SelectorTransformer = T._transformers_for(phi)
        verb_of = T.Lexicon.of(phi).verb_of

        ops: list[C.Operation] = []
        for block in tree.children:
            kids = list(block.children)
            sel_tok = next(k for k in kids if getattr(k, "type", None) == "STRING")
            try:
                sel_tree = inner_parser.parse(str(sel_tok)[1:-1])
                selector = SelectorTransformer().transform(sel_tree)
            except LarkError as exc:
                raise T.ParseError(
                    f"selector: {type(exc).__name__}: {exc}".split("\n")[0]) from exc

            for stmt in (k for k in kids if getattr(k, "data", None) == "stmt"):
                vtree = stmt.children[0]
                verb = verb_of[str(vtree.children[0])]
                values: list = []
                for sub in stmt.children[1:]:
                    if getattr(sub, "data", None) != "arglist":
                        continue
                    for arg in sub.children:
                        tok = arg.children[0]
                        if getattr(tok, "type", None) == "NUMBER":
                            values.append(C.canonical_number(str(tok)))
                        else:
                            values.append(str(tok)[1:-1])
                ops.append(C.Operation(verb, selector, C.build_args(verb, values)))

        return C.IRProgram(tuple(ops)).canonical()

    def render(self, ir: C.IRProgram, phi: P.PhiMap) -> str:
        """IR -> blk text. Consecutive ops sharing a selector share a block.

        Grouping matters: emitting one block per operation would still be
        valid, but it would change the TOKEN COUNT and the prefix shapes, and
        those are exactly what the experiment measures.
        """
        entry = phi.spelling("T_SELECTOR_ENTRY")
        # Selector.raw is the LANGUAGE-NEUTRAL reference rendering (rule C5):
        # it always carries 3DOM sigils. Using it here would emit `.wheel` even
        # under a lexicon whose class sigil is `#`, producing text that does not
        # parse in its own language. The vendored Emitter renders a Selector
        # with phi's spellings, so reuse it rather than re-deriving the sigils.
        emitter = T.Emitter(phi)
        out: list[str] = []
        i = 0
        ops = list(ir.ops)
        while i < len(ops):
            sel = ops[i].selector
            group = []
            while i < len(ops) and ops[i].selector == sel:
                group.append(ops[i])
                i += 1
            body = []
            for op in group:
                vals = C.args_in_order(op.op, op.args)
                rendered = ", ".join(
                    C.format_number(v) if isinstance(v, (int, float))
                    else C.quote_string(str(v)) for v in vals)
                spell = phi.spelling(_VERB_TERMINAL[op.op])
                body.append(f"{spell} {rendered};" if rendered else f"{spell};")
            sel_text = emitter.emit(sel)
            out.append(f"{entry} {C.quote_string(sel_text)} {{ {' '.join(body)} }}")
        return " ".join(out)


_VERB_TERMINAL = {
    "recolor": "T_VERB_RECOLOR", "scale": "T_VERB_SCALE", "move": "T_VERB_MOVE",
    "rotate": "T_VERB_ROTATE", "delete": "T_VERB_DELETE", "spin": "T_VERB_SPIN",
    "duplicate": "T_VERB_DUPLICATE", "setMaterial": "T_VERB_SETMATERIAL",
    "setOpacity": "T_VERB_SETOPACITY", "setVisible": "T_VERB_SETVISIBLE",
    "wireframe": "T_VERB_WIREFRAME", "metalness": "T_VERB_METALNESS",
    "roughness": "T_VERB_ROUGHNESS", "castShadow": "T_VERB_CASTSHADOW",
    "receiveShadow": "T_VERB_RECEIVESHADOW",
}

DOM = DomBackend()
BLK = BlkBackend()
BACKENDS: dict[str, Backend] = {"dom": DOM, "blk": BLK}
