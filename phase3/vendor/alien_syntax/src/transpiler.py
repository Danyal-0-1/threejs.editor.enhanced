"""transpiler.py — alien text -> IR, and IR -> alien text.

ONE code path serves every lexicon. 3DOM is the φ = identity member of the
family (see `phi.identity_phi`), so `ir(parse(x, identity))` and
`ir(parse(φ(x), φ))` are produced by the same functions with different data.
That is what makes the isomorphism test a statement about the languages rather
than about two hand-written parsers agreeing.

Layers, bottom to top:

  Lexer           a φ-parameterised TWO-LEVEL lexer (L1/L2/L3) emitting the
                  same DSL token alphabet as Phase 1's refgrammar.py. Used for
                  the DFA metrics, nLVP, and as an INDEPENDENT recognizer to
                  cross-check the Lark front end (Phase 1's gate G6, repeated
                  per lexicon).

  Transliterator  φ applied to raw TEXT, including malformed text. The negative
                  corpus does not parse by construction, so it cannot be mapped
                  through the parser; it is mapped by this character-level
                  state machine instead.

  Lark front end  the reference recognizer, EARLEY as clause P1 mandates,
                  instantiated twice from the rendered two-level .lark grammar.
                  `ambiguity="explicit"` is what the I10 zero-ambiguity
                  regression counts.

  Transformers    lark.Transformer subclasses, CST -> the frozen IR dataclasses
                  in canonicalize.py.

  Emitter         IR -> alien text, dispatched with functools.singledispatchmethod
                  over the IR node types. No stringly-typed dicts cross a
                  boundary: everything between the parser and the emitter is a
                  dataclass.
"""

from __future__ import annotations

import functools
import os
import sys
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from canonicalize import (GRAMMAR_VERSION, CanonicalisationError,  # noqa: E402
                          IRProgram, Matcher, Operation, Selector, Step,
                          args_in_order, build_args, canonical_number,
                          format_number, quote_string)
from phi import (IDENT_CHARS, PhiMap, identity_phi,  # noqa: E402
                 phase1_dir, render_slots)

_P1_CONF = os.path.join(phase1_dir(), "conformance")
if _P1_CONF not in sys.path:
    sys.path.insert(0, _P1_CONF)
import refgrammar as R                                          # noqa: E402

LEVEL_SPLIT = "// ══════ LEVEL SPLIT ══════"
LARK_TEMPLATE = os.path.join(ALIEN, "grammar", "templates", "grammar.lark.template")

STRUCTURAL = {"(": "LP", ")": "RP", "{": "LB", "}": "RB", ";": "SEMI", ",": "COMMA"}
OUTER_WORD_START = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
OUTER_WORD_BODY = OUTER_WORD_START | set("0123456789")


class LexError(Exception):
    pass


class ParseError(Exception):
    pass


class AmbiguityError(Exception):
    """Raised when the Earley parser reports more than one derivation (I10)."""


Token = tuple[str, str, int]        # (type, value, char offset) — as refgrammar


# ─────────────────────────────────────────────────────────────────────────────
# Spelling tables — the only thing that varies between languages
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Lexicon:
    """φ, arranged the way a lexer needs to read it."""
    phi: PhiMap
    outer_symbols: tuple[tuple[str, str], ...]      # (spelling, token type), long first
    outer_words: dict[str, str]                     # spelling -> token type
    inner_symbols: tuple[tuple[str, str], ...]
    inner_words: dict[str, str]
    verb_of: dict[str, str]                         # token type -> canonical verb
    canonical_of_word: dict[str, str]               # alien spelling -> 3DOM spelling

    @staticmethod
    def of(phi: PhiMap) -> "Lexicon":
        table = phi.table
        outer_sym: list[tuple[str, str]] = []
        outer_word: dict[str, str] = {}
        inner_sym: list[tuple[str, str]] = []
        inner_word: dict[str, str] = {}
        verb_of: dict[str, str] = {}
        canon: dict[str, str] = {}

        def place(tid: str, tok: str, *, inner: bool) -> None:
            spell = phi.spelling(tid)
            word_class = bool(spell) and all(c in IDENT_CHARS for c in spell)
            if word_class:
                (inner_word if inner else outer_word)[spell] = tok
            else:
                (inner_sym if inner else outer_sym).append((spell, tok))
            canon[spell] = table.by_id[tid].spelling

        place("T_SELECTOR_ENTRY", "DOLLAR", inner=False)
        place("T_FUNCTION", "FUNC", inner=False)
        place("T_CHAIN_OP", "DOT", inner=False)
        for term in table.terminals:
            if term.role == "operation verb":
                place(term.id, "VERB", inner=False)
        place("T_ID_SIGIL", "HASH", inner=True)
        place("T_CLASS_SIGIL", "CSIG", inner=True)
        place("T_PSEUDO_SIGIL", "COLON", inner=True)
        place("T_CHILD", "GT", inner=True)
        place("T_WILDCARD", "STAR", inner=True)
        for term in table.terminals:
            if term.role == "type selector keyword":
                place(term.id, "TYPE_" + term.spelling.upper(), inner=True)
            elif term.role == "pseudo-selector keyword":
                place(term.id, term.spelling.upper(), inner=True)
        for term in table.terminals:
            if term.role == "operation verb":
                verb_of[phi.spelling(term.id)] = term.spelling

        return Lexicon(
            phi=phi,
            outer_symbols=tuple(sorted(outer_sym, key=lambda p: -len(p[0]))),
            outer_words=outer_word,
            inner_symbols=tuple(sorted(inner_sym, key=lambda p: -len(p[0]))),
            inner_words=inner_word,
            verb_of=verb_of,
            canonical_of_word=canon,
        )


# PhiMap holds dicts, so it is not hashable; cache on a derived string key.
_LEXICON_CACHE: dict[str, Lexicon] = {}


def _phi_key(phi: PhiMap) -> str:
    return phi.phi_id + "|" + repr(sorted(phi.substitutions.items()))


def _lex_of(phi: PhiMap) -> Lexicon:
    key = _phi_key(phi)
    if key not in _LEXICON_CACHE:
        _LEXICON_CACHE[key] = Lexicon.of(phi)
    return _LEXICON_CACHE[key]


# ─────────────────────────────────────────────────────────────────────────────
# The two-level lexer (L1 outside quotes, L2 inside a selector, L3 the seam)
# ─────────────────────────────────────────────────────────────────────────────

class Lexer:
    """Flat-lexes a program into the Phase 1 DSL token alphabet.

    Token TYPES are role names, never spellings, so the stream produced from a
    3DOM program and from its φ-image are literally comparable — which is how
    measure/dfa_parity.py can assert branching parity rather than estimate it.
    """

    def __init__(self, phi: PhiMap) -> None:
        self.phi = phi
        self.lx = _lex_of(phi)

    # ── level 2: inside a quoted selector, whitespace is SIGNIFICANT ────────
    def lex_selector_body(self, body: str, base: int) -> list[Token]:
        toks: list[Token] = []
        i, n, prev = 0, len(body), None
        while i < n:
            c = body[i]
            if c == " ":
                j = i
                while j < n and body[j] == " ":
                    j += 1
                toks.append(("WS", " ", base + i)); prev = "WS"; i = j
                continue
            if c in "\t\r\n":
                raise LexError(
                    f"illegal whitespace char inside selector at {base + i}")
            hit = self._match(self.lx.inner_symbols, body, i)
            if hit is not None:
                spell, tok = hit
                toks.append((tok, spell, base + i)); prev = tok; i += len(spell)
                continue
            if c in IDENT_CHARS:
                j = i
                while j < n and body[j] in IDENT_CHARS:
                    j += 1
                run = body[i:j]
                if prev in ("HASH", "CSIG"):
                    tt = "IDENT"          # a name after a sigil is always literal
                else:
                    tt = self.lx.inner_words.get(run, "IDENT")
                toks.append((tt, run, base + i)); prev = tt; i = j
                continue
            raise LexError(f"illegal char {c!r} inside selector at {base + i}")
        return toks

    # ── level 1: outside quotes, layout is elided ──────────────────────────
    def lex(self, src: str) -> list[Token]:
        toks: list[Token] = []
        i, n = 0, len(src)
        while i < n:
            c = src[i]
            if c in " \t\r\n":
                i += 1
                continue
            if c in STRUCTURAL:
                toks.append((STRUCTURAL[c], c, i)); i += 1
                continue
            hit = self._match(self.lx.outer_symbols, src, i)
            if hit is not None:
                spell, tok = hit
                toks.append((tok, spell, i)); i += len(spell)
                continue
            if c in "'\"":
                i = self._lex_string(src, i, toks)
                continue
            if c in "+-0123456789":
                i = self._lex_number(src, i, toks)
                continue
            if c in OUTER_WORD_START:
                j = i
                while j < n and src[j] in OUTER_WORD_BODY:
                    j += 1
                run = src[i:j]
                # An unknown bareword is emitted as a token no rule can consume,
                # so the longest-valid-prefix metric (A3) fails exactly here.
                toks.append((self.lx.outer_words.get(run, "BADWORD"), run, i))
                i = j
                continue
            raise LexError(f"illegal char {c!r} at {i}")
        return toks

    @staticmethod
    def _match(table: Sequence[tuple[str, str]], src: str, i: int):
        for spell, tok in table:            # longest spelling first
            if src.startswith(spell, i):
                return spell, tok
        return None

    def _lex_string(self, src: str, i: int, toks: list[Token]) -> int:
        q, n = src[i], len(src)
        j = i + 1
        while j < n and src[j] != q:
            if src[j] in "\r\n":
                raise LexError(f"newline inside string at {j}")
            j += 1
        if j >= n:
            raise LexError(f"unterminated string starting at {i}")
        body = src[i + 1:j]
        # L3 seam: a string in selector position is DESCENDED INTO; every other
        # string is one opaque argument value.
        is_selpos = (len(toks) >= 2 and toks[-1][0] == "LP"
                     and toks[-2][0] == "DOLLAR")
        if is_selpos:
            toks.append(("QUOTE", q, i))
            toks.extend(self.lex_selector_body(body, i + 1))
            toks.append(("QUOTE", q, j))
        else:
            toks.append(("STRING", body, i))
        return j + 1

    @staticmethod
    def _lex_number(src: str, i: int, toks: list[Token]) -> int:
        n = len(src)
        j = i
        if src[j] in "+-":
            j += 1
        d0 = j
        while j < n and src[j].isdigit():
            j += 1
        if j == d0:
            raise LexError(f"malformed number at {i}")
        if j < n and src[j] == ".":
            j += 1
            d1 = j
            while j < n and src[j].isdigit():
                j += 1
            if j == d1:
                raise LexError(f"malformed float at {i}")
        toks.append(("NUMBER", src[i:j], i))
        return j


def lex(src: str, phi: PhiMap) -> list[Token]:
    return Lexer(phi).lex(src)


def token_types(src: str, phi: PhiMap) -> list[str]:
    return [t[0] for t in lex(src, phi)]


def num_parses(src: str, phi: PhiMap) -> int:
    """Exact derivation count via Phase 1's parse counter over OUR token stream.

    The grammar object is Phase 1's, unmodified: both languages are recognised
    by the same token-level CFG, which is I1/I2/I3 made operational instead of
    asserted.
    """
    try:
        tokens = lex(src, phi)
    except LexError:
        return 0
    total, _memo = R.parse_counts(tokens)
    return total


def dfa_accepts(src: str, phi: PhiMap) -> bool:
    try:
        tokens = lex(src, phi)
    except LexError:
        return False
    d = R.dfa()
    st = d["start"]
    for tt, _v, _p in tokens:
        nxt = d["trans"].get(st, {}).get(tt)
        if nxt is None:
            return False
        st = nxt
    return st in d["accepts"]


def longest_valid_prefix(src: str, phi: PhiMap) -> tuple[int, int, set[str]]:
    """A3's nLVP support, per lexicon."""
    try:
        tokens = lex(src, phi)
    except LexError:
        return 0, 0, set()
    d = R.dfa()
    st, consumed = d["start"], 0
    for tt, _v, _p in tokens:
        nxt = d["trans"].get(st, {}).get(tt)
        if nxt is None:
            return consumed, len(tokens), set(d["trans"].get(st, {}))
        st = nxt
        consumed += 1
    return consumed, len(tokens), set(d["trans"].get(st, {}))


def features_with_verbs(src: str, phi: PhiMap) -> set[str]:
    """Phase 1's production-coverage instrument, per lexicon.

    Reuses refgrammar's derivation extractor and its FEATURE_ID table unchanged —
    the feature ids are production-branch names, which are frozen by I1/I2, so
    "100% production coverage" means the SAME 57 obligations in every language.
    """
    tokens = lex(src, phi)
    total, _memo = R.parse_counts(tokens)
    if total != 1:
        raise ParseError(f"coverage needs an unambiguous parse (got {total})")
    used, _ = R.derive(tokens)
    feats = {R.FEATURE_ID.get(key, "%s#%d" % key) for key in used}
    verb_of = _lex_of(phi).verb_of
    for tt, value, _pos in tokens:
        if tt == "VERB":
            feats.add("verb:" + verb_of[value])
    return feats


# ─────────────────────────────────────────────────────────────────────────────
# Transliteration: φ on raw TEXT, malformed input included
# ─────────────────────────────────────────────────────────────────────────────

class Transliterator:
    """Rewrite a program from one lexicon into another, character by character.

    Never raises and never requires a successful parse: the negative corpus is
    invalid by construction, and mapping it through φ is itself the isomorphism
    check (a 3DOM near-miss must stay a near-miss). Layout, identifiers, numbers,
    argument-string bodies, comments and the quote characters are all preserved
    byte-for-byte; only terminal SPELLINGS move.
    """

    def __init__(self, src_phi: PhiMap, dst_phi: PhiMap) -> None:
        self.src = _lex_of(src_phi)
        self.dst_phi = dst_phi
        self.src_phi = src_phi
        # spelling -> spelling, per level
        self.outer_sym = tuple(sorted(
            ((src_phi.spelling(t), dst_phi.spelling(t)) for t in self._outer_ids()
             if not self._is_word(src_phi.spelling(t))),
            key=lambda p: -len(p[0])))
        self.outer_word = {src_phi.spelling(t): dst_phi.spelling(t)
                           for t in self._outer_ids()
                           if self._is_word(src_phi.spelling(t))}
        self.inner_sym = tuple(sorted(
            ((src_phi.spelling(t), dst_phi.spelling(t)) for t in self._inner_ids()
             if not self._is_word(src_phi.spelling(t))),
            key=lambda p: -len(p[0])))
        self.inner_word = {src_phi.spelling(t): dst_phi.spelling(t)
                           for t in self._inner_ids()
                           if self._is_word(src_phi.spelling(t))}
        self.src_verbs = {src_phi.spelling(t.id) for t in src_phi.table.terminals
                          if t.role == "operation verb"}
        self.src_func = src_phi.spelling("T_FUNCTION")
        self.src_entry = src_phi.spelling("T_SELECTOR_ENTRY")
        self.src_sigils = {src_phi.spelling("T_ID_SIGIL"),
                           src_phi.spelling("T_CLASS_SIGIL")}

    def _outer_ids(self) -> Iterator[str]:
        yield "T_SELECTOR_ENTRY"
        yield "T_FUNCTION"
        yield "T_CHAIN_OP"
        for t in self.src_phi.table.terminals:
            if t.role == "operation verb":
                yield t.id

    def _inner_ids(self) -> Iterator[str]:
        yield from ("T_ID_SIGIL", "T_CLASS_SIGIL", "T_PSEUDO_SIGIL",
                    "T_CHILD", "T_WILDCARD")
        for t in self.src_phi.table.terminals:
            if t.role in ("type selector keyword", "pseudo-selector keyword"):
                yield t.id

    @staticmethod
    def _is_word(spelling: str) -> bool:
        return bool(spelling) and all(c in IDENT_CHARS for c in spelling)

    @staticmethod
    def _match(table, src: str, i: int):
        for a, b in table:
            if src.startswith(a, i):
                return a, b
        return None

    # ── selector body (level 2) ────────────────────────────────────────────
    def _selector(self, body: str) -> str:
        out: list[str] = []
        i, n, after_sigil = 0, len(body), False
        while i < n:
            hit = self._match(self.inner_sym, body, i)
            if hit is not None:
                a, b = hit
                out.append(b)
                after_sigil = a in self.src_sigils
                i += len(a)
                continue
            c = body[i]
            if c in IDENT_CHARS:
                j = i
                while j < n and body[j] in IDENT_CHARS:
                    j += 1
                run = body[i:j]
                # after a sigil the run is an IDENTIFIER (a value copied into the
                # IR); only a BARE run can be a type/pseudo keyword
                out.append(run if after_sigil else self.inner_word.get(run, run))
                after_sigil = False
                i = j
                continue
            out.append(c)
            after_sigil = False
            i += 1
        return "".join(out)

    # ── whole program (level 1) ────────────────────────────────────────────
    def __call__(self, src: str) -> str:
        out: list[str] = []
        i, n = 0, len(src)
        prev: list[str] = []          # coarse token history, for selector position

        def push(kind: str) -> None:
            prev.append(kind)
            del prev[:-2]

        while i < n:
            c = src[i]
            if c in " \t\r\n":
                out.append(c); i += 1
                continue
            if c in STRUCTURAL:
                out.append(c); push(STRUCTURAL[c]); i += 1
                continue
            hit = self._match(self.outer_sym, src, i)
            if hit is not None:
                a, b = hit
                out.append(b)
                push("ENTRY" if a == self.src_entry else "SYM")
                i += len(a)
                continue
            if c in "'\"":
                i = self._string(src, i, out, prev)
                push("STRING")
                continue
            if c in "+-0123456789":
                j = i
                if src[j] in "+-":
                    j += 1
                while j < n and (src[j].isdigit() or src[j] == "."):
                    j += 1
                out.append(src[i:j]); push("NUMBER"); i = j
                continue
            if c in OUTER_WORD_START:
                j = i
                while j < n and src[j] in OUTER_WORD_BODY:
                    j += 1
                run = src[i:j]
                out.append(self.outer_word.get(run, run))
                push("VERB" if run in self.src_verbs
                     else "FUNC" if run == self.src_func else "WORD")
                i = j
                continue
            out.append(c); push("OTHER"); i += 1
        return "".join(out)

    def _string(self, src: str, i: int, out: list[str], prev: list[str]) -> int:
        q, n = src[i], len(src)
        j = i + 1
        while j < n and src[j] != q and src[j] not in "\r\n":
            j += 1
        if j >= n or src[j] != q:
            # UNTERMINATED (a D2 near-miss). Emit the opening quote and keep
            # reading in OUTER mode: any transliteration leaves it a near-miss on
            # the same production, and this reading renames the most structure.
            out.append(q)
            return i + 1
        body = src[i + 1:j]
        # selector position: `<entry> (` immediately before. The second clause is
        # deliberately lenient so a MISSPELLED entry ($D instead of $S) still has
        # its selector transliterated — otherwise a one-defect negative would
        # arrive in the alien corpus carrying two defects.
        selpos = (len(prev) >= 2 and prev[-1] == "LP"
                  and prev[-2] in ("ENTRY", "WORD", "OTHER"))
        out.append(q + (self._selector(body) if selpos else body) + q)
        return j + 1


def transliterate(src: str, src_phi: PhiMap, dst_phi: PhiMap) -> str:
    return Transliterator(src_phi, dst_phi)(src)


def phi_forward(src: str, phi: PhiMap) -> str:
    """3DOM text -> alien text."""
    return transliterate(src, identity_phi(phi.table), phi)


def phi_inverse(src: str, phi: PhiMap) -> str:
    """alien text -> 3DOM text. Derived from φ, never hand-maintained."""
    return transliterate(src, phi, identity_phi(phi.table))


# ─────────────────────────────────────────────────────────────────────────────
# Lark front end (EARLEY — clause P1) and the CST -> IR transformers
# ─────────────────────────────────────────────────────────────────────────────

_PARSER_CACHE: dict[str, tuple[Any, Any]] = {}


def _lark_sources(phi: PhiMap) -> tuple[str, str]:
    with open(LARK_TEMPLATE, encoding="utf-8") as fh:
        text = render_slots(fh.read().replace("{{ PHI_ID }}", phi.phi_id), phi)
    head, sep, tail = text.partition(LEVEL_SPLIT)
    if not sep:
        raise ParseError("grammar.lark.template has no LEVEL SPLIT marker")
    return head, tail.split("\n", 1)[1]


def parsers_for(phi: PhiMap):
    """(outer, selector) Lark parsers for this lexicon, built once and cached."""
    key = _phi_key(phi)
    if key not in _PARSER_CACHE:
        from lark import Lark
        outer_src, inner_src = _lark_sources(phi)
        _PARSER_CACHE[key] = (
            Lark(outer_src, start="program", parser="earley",
                 ambiguity="explicit", lexer="dynamic"),
            Lark(inner_src, start="selector", parser="earley",
                 ambiguity="explicit", lexer="dynamic"),
        )
    return _PARSER_CACHE[key]


def _count_ambiguities(tree) -> int:
    return sum(1 for node in tree.iter_subtrees() if node.data == "_ambig")


def _import_transformer():
    from lark import Transformer, v_args
    return Transformer, v_args


def _build_transformers(phi: PhiMap):
    Transformer, v_args = _import_transformer()
    table = phi.table

    # Lark terminal name -> canonical 3DOM spelling. Role-keyed, so it is the
    # same table in every language: this is where the shared IR is anchored.
    verb_by_token = {
        "V_" + t.id[len("T_VERB_"):]: t.spelling
        for t in table.terminals if t.role == "operation verb"
    }
    type_by_token = {
        "TYPE_" + t.spelling.upper(): t.spelling
        for t in table.terminals if t.role == "type selector keyword"
    }
    pseudo_by_token = {
        "PSEUDO_" + t.spelling.upper(): t.spelling
        for t in table.terminals if t.role == "pseudo-selector keyword"
    }

    class SelectorTransformer(Transformer):
        """CST -> Selector (level 2)."""

        def id_selector(self, kids):
            return Matcher("id", str(kids[1]))

        def class_selector(self, kids):
            return Matcher("class", str(kids[1]))

        def type_selector(self, kids):
            return Matcher("type", type_by_token[kids[0].type])

        def wildcard(self, _kids):
            return Matcher("wildcard")

        def simple_matcher(self, kids):
            return kids[0]

        def compound_selector(self, kids):
            return tuple(kids)

        def descendant_combinator(self, _kids):
            return "descendant"

        def child_combinator(self, _kids):
            return "child"

        def combinator(self, kids):
            return kids[0]

        def complex_selector(self, kids):
            # kids is compound (combinator compound)*, so the tail must have EVEN
            # length. zip() over the strided halves would silently DROP a
            # trailing combinator and hand back a selector with a step missing —
            # a shorter selector that still parses, still hashes, and quietly
            # means something else. Check before pairing.
            rest = kids[1:]
            if len(rest) % 2:
                raise ParseError(
                    f"complex_selector has {len(kids)} children: the "
                    f"(combinator compound)* tail is odd-length, so a "
                    f"combinator has no compound to attach to")
            steps: list[Step] = [Step(None, tuple(kids[0]))]
            for combinator, compound in zip(rest[0::2], rest[1::2]):
                steps.append(Step(combinator, tuple(compound)))
            return Selector(tuple(steps))

        def pseudo_selector(self, kids):
            name = pseudo_by_token[kids[1].type]
            return Selector((Step(None, (Matcher("pseudo", name),)),))

        def selector(self, kids):
            return kids[0]

    class ProgramTransformer(Transformer):
        """CST -> IRProgram (level 1). Descends into level 2 at quoted_selector."""

        def __init__(self, selector_parser, selector_transformer):
            super().__init__()
            self._sel_parser = selector_parser
            self._sel_tf = selector_transformer

        def quoted_selector(self, kids):
            body = str(kids[0])[1:-1]                 # strip the bound quotes (D2)
            tree = self._sel_parser.parse(body)
            if _count_ambiguities(tree):
                raise AmbiguityError(f"ambiguous selector {body!r}")
            return self._sel_tf.transform(tree)

        def quoted_string(self, kids):
            return str(kids[0])[1:-1]                 # opaque value (D3)

        def argument(self, kids):
            kid = kids[0]
            if hasattr(kid, "type") and kid.type == "NUMBER":
                return canonical_number(str(kid))
            return kid

        def argument_list(self, kids):
            return list(kids)

        def verb(self, kids):
            return verb_by_token[kids[0].type]

        def operation_call(self, kids):
            verb = kids[1]
            values = kids[2] if len(kids) > 2 else []
            return (verb, values)

        def selector_call(self, kids):
            return kids[1]

        def chain_expression(self, kids):
            selector, calls = kids[0], kids[1:]
            return [Operation(verb, selector, build_args(verb, values))
                    for verb, values in calls]

        def statement(self, kids):
            return kids[0]

        def iife(self, kids):
            # kids carries the FUNC keyword token plus zero or more statements.
            # Each statement has already been lowered to a list of Operations by
            # chain_expression; the FUNC token is a lark Token (a str subclass).
            # Anything else means a rule was added to the grammar without a
            # transformer method, and DROPPING it silently would lose operations
            # from the IR while still producing a parse and a hash.
            ops: list[Operation] = []
            for kid in kids:
                if isinstance(kid, list):
                    ops.extend(kid)
                elif isinstance(kid, str):          # the FUNC keyword token
                    continue
                else:
                    raise ParseError(
                        f"iife received an unlowered child of type "
                        f"{type(kid).__name__}: every statement must reach the "
                        f"IR, so this cannot be skipped")
            return tuple(ops)

        def program(self, kids):
            return IRProgram(kids[0])

    return ProgramTransformer, SelectorTransformer


_TRANSFORMER_CACHE: dict[str, tuple[Any, Any]] = {}


def _transformers_for(phi: PhiMap):
    key = _phi_key(phi)
    if key not in _TRANSFORMER_CACHE:
        _TRANSFORMER_CACHE[key] = _build_transformers(phi)
    return _TRANSFORMER_CACHE[key]


def parse(src: str, phi: PhiMap, *, keep_source: bool = False) -> IRProgram:
    """alien text -> canonical IR. Raises on reject or on ambiguity (I10)."""
    from lark.exceptions import LarkError
    outer, inner = parsers_for(phi)
    ProgramTransformer, SelectorTransformer = _transformers_for(phi)
    try:
        tree = outer.parse(src)
    except LarkError as exc:
        raise ParseError(f"{type(exc).__name__}: {exc}".split("\n")[0]) from exc
    ambiguities = _count_ambiguities(tree)
    if ambiguities:
        raise AmbiguityError(
            f"{ambiguities} ambiguous node(s) — the grammar must be unambiguous (I10)")
    try:
        # The level-2 descent happens INSIDE the transformer (the L3 seam), so a
        # malformed selector surfaces here rather than at the outer parse — an
        # empty selector `$S('')` is the canonical case.
        ir = ProgramTransformer(inner, SelectorTransformer()).transform(tree)
    except LarkError as exc:
        cause = exc.orig_exc if hasattr(exc, "orig_exc") else exc
        if isinstance(cause, AmbiguityError):
            raise cause
        raise ParseError(
            f"selector: {type(cause).__name__}: {cause}".split("\n")[0]) from exc
    if keep_source:
        ir = IRProgram(ir.ops, source=src, grammar_version=GRAMMAR_VERSION)
    return ir.canonical()


def accepts(src: str, phi: PhiMap) -> bool:
    try:
        parse(src, phi)
        return True
    except (ParseError, AmbiguityError):
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Emitter: IR -> alien text
# ─────────────────────────────────────────────────────────────────────────────

class Emitter:
    """IR -> canonical alien source text.

    Dispatched on IR node type with functools.singledispatchmethod, so adding a
    node type is a new method rather than a new branch in a growing if-chain,
    and no dictionary of loose strings is threaded through the recursion.
    """

    def __init__(self, phi: PhiMap) -> None:
        self.phi = phi
        self.sigil = {
            "id": phi.spelling("T_ID_SIGIL"),
            "class": phi.spelling("T_CLASS_SIGIL"),
            "pseudo": phi.spelling("T_PSEUDO_SIGIL"),
        }
        self.wildcard = phi.spelling("T_WILDCARD")
        self.child = phi.spelling("T_CHILD")
        self.chain = phi.spelling("T_CHAIN_OP")
        self.entry = phi.spelling("T_SELECTOR_ENTRY")
        self.func = phi.spelling("T_FUNCTION")
        self.type_spelling = {
            t.spelling: phi.spelling(t.id)
            for t in phi.table.terminals if t.role == "type selector keyword"
        }
        self.pseudo_spelling = {
            t.spelling: phi.spelling(t.id)
            for t in phi.table.terminals if t.role == "pseudo-selector keyword"
        }
        self.verb_spelling = {
            t.spelling: phi.spelling(t.id)
            for t in phi.table.terminals if t.role == "operation verb"
        }

    @functools.singledispatchmethod
    def emit(self, node: Any) -> str:
        raise TypeError(f"no emitter for {type(node).__name__}")

    @emit.register
    def _(self, node: Matcher) -> str:
        if node.kind == "wildcard":
            return self.wildcard
        if node.kind == "type":
            return self.type_spelling[node.name or ""]
        if node.kind == "pseudo":
            return self.sigil["pseudo"] + self.pseudo_spelling[node.name or ""]
        return self.sigil[node.kind] + (node.name or "")

    @emit.register
    def _(self, node: Step) -> str:
        # C4: step order is meaning; C3: matcher order inside a step is not, and
        # was normalised by canonicalize before we got here.
        leads = {"descendant": " ", "child": self.child, None: ""}
        if node.combinator not in leads:
            raise CanonicalisationError(
                f"cannot emit combinator {node.combinator!r}: the only "
                f"combinators in the language are {sorted(k for k in leads if k)} "
                f"and None (first step). Emitting an empty lead here would drop "
                f"the combinator and silently change the selector's meaning")
        return leads[node.combinator] + "".join(self.emit(m) for m in node.matchers)

    @emit.register
    def _(self, node: Selector) -> str:
        return "".join(self.emit(s) for s in node.steps)

    @emit.register
    def _(self, node: Operation) -> str:
        args = ",".join(
            format_number(v) if isinstance(v, (int, float)) else quote_string(str(v))
            for v in args_in_order(node.op, node.args)
        )
        return (f"{self.entry}({quote_string(self.emit(node.selector))})"
                f"{self.chain}{self.verb_spelling[node.op]}({args})")

    @emit.register
    def _(self, node: IRProgram) -> str:
        body = " ".join(self.emit(op) + ";" for op in node.ops)
        inner = f"{{ {body} }}" if body else "{}"
        return f"({self.func}(){inner})();"


def emit(ir: IRProgram, phi: PhiMap) -> str:
    return Emitter(phi).emit(ir.canonical())


def canon_text(src: str, phi: PhiMap) -> str:
    """The canonical alien rendering of a program: emit ∘ ir ∘ parse."""
    return emit(parse(src, phi), phi)


if __name__ == "__main__":
    from phi import load_candidate
    ident = identity_phi()
    prog = "(function(){ $S('.car > .wheel.front').recolor('#111111').scale(1.5); })();"
    ir = parse(prog, ident)
    print("3DOM   :", prog)
    print("IR raw :", ir.ops[0].selector.raw)
    for name in ("alpha", "beta", "gamma"):
        p = load_candidate(name)
        alien = phi_forward(prog, p)
        print(f"{name:<7}:", alien)
        assert phi_inverse(alien, p) == prog, "φ⁻¹∘φ != id"
        assert parse(alien, p).canonical() == ir.canonical(), "IR mismatch"
    print("round trips and IR equality hold")
