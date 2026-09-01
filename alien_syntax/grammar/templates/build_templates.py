"""build_templates.py — derive the slotted grammar templates from Phase 1.

The acceptance criterion says the winner's grammar must be RENDERED, not typed.
That pushes the problem back one step: the TEMPLATE must not be typed either, or
a transcription slip would silently corrupt every language generated from it.

So the templates are derived mechanically from `3dom_grammar.{iso,w3c}.ebnf`,
and the derivation is driven entirely by `terminals.json` — never by matching on
the surface character. The rule is:

    inside the production for rule R, a quoted literal L becomes the slot
    {{T}} iff there is exactly one terminal T with T.spelling == L and
    R in T.productions and T.substitutable.

That single rule resolves the "." overload without a special case, and it
protects the decimal point for free:

  * `operation_call = "." , verb , …`   -> T_CHAIN_OP    (productions: operation_call)
  * `class_selector = "." , identifier` -> T_CLASS_SIGIL (productions: class_selector)
  * `number = … [ "." , digit … ]`      -> NO terminal has spelling "." with
                                           "number" in productions, so the
                                           decimal point stays a literal. This
                                           is the case a character-keyed pass
                                           would have destroyed, and the case an
                                           identity-render check cannot catch.
  * `sign = "+" | "-"`, `quoted_string = "'" …` -> substitutable:false, untouched
                                                   (I8: delimiter symmetry).

Comments are slot-ified too, so a generated appendix does not carry 3DOM-spelled
examples in its prose. That pass is also mechanical, in three tiers, using the
nearest PRECEDING production as context:

  T1  a quoted literal in a comment whose (spelling, context-production) pair
      resolves under the rule above;
  T2  a quoted selector literal whose body parses as a `selector` under the
      Phase 1 inner lexer + grammar (so '.car .wheel' is rewritten and the
      character class example '-' is not);
  T3  a `$S( … )` call fragment or a `(function(){ … })();` fragment, rewritten
      by running the Phase 1 reference lexer over it.

Verification, run by this script and by tests/test_invariants.py:
    render(template, φ=identity) must reproduce the Phase 1 file BYTE-FOR-BYTE.
"""

from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ALIEN, "src"))

from phi import (GRAMMAR_VERSION, TerminalTable, identity_phi,  # noqa: E402
                 load_terminals, phase1_dir, render_slots)

# A production head in either notation:  name = …   /   name ::= …
ISO_HEAD = re.compile(r"^([a-z_][a-z0-9_]*)\s*=(?!=)")
W3C_HEAD = re.compile(r"^([a-z_][a-z0-9_]*)\s*::=")
# A quoted literal, either quote style.
LITERAL = re.compile(r"""('(?:[^']*)'|"(?:[^"]*)")""")


def _slot_for(table: TerminalTable, spelling: str, production: str | None) -> str | None:
    """The unique substitutable terminal with this spelling in this production."""
    if production is None:
        return None
    hits = [t for t in table.terminals
            if t.substitutable and t.spelling == spelling
            and production in t.productions]
    if len(hits) == 1:
        return "{{%s}}" % hits[0].id
    return None


def _slotify_literals(text: str, table: TerminalTable, production: str | None) -> str:
    def repl(m: "re.Match[str]") -> str:
        quote, body = m.group(0)[0], m.group(0)[1:-1]
        slot = _slot_for(table, body, production)
        # the QUOTES belong to the notation, not to the terminal: only the body
        # becomes a slot, so `"function"` -> `"{{T_FUNCTION}}"`.
        return quote + slot + quote if slot else m.group(0)
    return LITERAL.sub(repl, text)


# ── comment tier T2/T3: rewrite fragments via the Phase 1 reference engine ──
def _selector_slotifier(table: TerminalTable):
    """Return f(selector_body) -> slotted selector body, or None if it is not a
    selector at all. Uses Phase 1's own inner lexer so the decision is the
    grammar's, not a regex's."""
    sys.path.insert(0, os.path.join(phase1_dir(), "conformance"))
    import refgrammar as R                                     # noqa: N806

    inner_slot = {
        "HASH": "{{T_ID_SIGIL}}", "CSIG": "{{T_CLASS_SIGIL}}",
        "COLON": "{{T_PSEUDO_SIGIL}}", "GT": "{{T_CHILD}}",
        "STAR": "{{T_WILDCARD}}",
        "TYPE_MESH": "{{T_TYPE_MESH}}", "TYPE_GROUP": "{{T_TYPE_GROUP}}",
        "TYPE_LIGHT": "{{T_TYPE_LIGHT}}", "TYPE_CAMERA": "{{T_TYPE_CAMERA}}",
        "SELECTED": "{{T_PSEUDO_SELECTED}}", "LASSO": "{{T_PSEUDO_LASSO}}",
    }

    def parses_as_selector(body: str) -> bool:
        probe = "(function(){ $S('%s'); })();" % body
        return "'" not in body and R.num_parses(probe) == 1

    def slotify(body: str) -> str:
        out = []
        for tt, val, _pos in R._lex_selector_body(body, 0):
            out.append(inner_slot.get(tt, val))
        return "".join(out)

    return parses_as_selector, slotify, R


def _slotify_comment(text: str, table: TerminalTable, production: str | None,
                     helpers) -> str:
    parses_as_selector, slotify_selector, R = helpers

    # T3 — whole $S(...) / (function(){...})(); fragments, and chained calls.
    def rewrite_fragment(m: "re.Match[str]") -> str:
        frag = m.group(0)
        out = frag
        # selector literal inside the fragment
        for qm in re.finditer(r"""(['"])([^'"]*)\1""", frag):
            body = qm.group(2)
            if parses_as_selector(body):
                out = out.replace(qm.group(0),
                                  qm.group(1) + slotify_selector(body) + qm.group(1), 1)
        out = out.replace("$S", "{{T_SELECTOR_ENTRY}}")
        out = re.sub(r"\bfunction\b", "{{T_FUNCTION}}", out)
        for term in table.terminals:
            if term.role == "operation verb":
                out = re.sub(r"\.%s\(" % re.escape(term.spelling),
                             "{{T_CHAIN_OP}}{{%s}}(" % term.id, out)
        return out

    text = re.sub(r"\$S\s*\(\s*['\"][^'\"]*['\"]\s*\)(\s*\.\s*[A-Za-z]+\([^)]*\))*",
                  rewrite_fragment, text)
    text = re.sub(r"\(\s*function\s*\(\s*\)\s*\{", rewrite_fragment, text)

    # T2 — bare quoted selector literals ('.car .wheel', '*', '.wheel.front').
    def rewrite_literal(m: "re.Match[str]") -> str:
        q, body = m.group(0)[0], m.group(0)[1:-1]
        if "{{" in body:
            return m.group(0)
        # T1 FIRST — a quoted terminal read in the context of its production.
        slot = _slot_for(table, body, production)
        if slot:
            return q + slot + q
        # T2 — a quoted SELECTOR literal. Guarded by len > 1: a one-character
        # literal that T1 could not place is an EBNF OPERATOR being discussed,
        # not a terminal. Phase 1 comments say  '*' = the infinite-chaining rule
        # (the Kleene star) right next to  wildcard ::= '*'  (the terminal); only
        # the production context tells them apart, and T1 already tried that.
        if len(body) > 1 and parses_as_selector(body):
            return q + slotify_selector(body) + q
        return m.group(0)

    return LITERAL.sub(rewrite_literal, text)


def build(src_path: str, out_path: str, notation: str, table: TerminalTable) -> None:
    head_re = ISO_HEAD if notation == "iso" else W3C_HEAD
    helpers = _selector_slotifier(table)
    with open(src_path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    out: list[str] = []
    production: str | None = None   # nearest preceding production head
    in_rule = False                 # are we inside a (possibly wrapped) production?

    for line in lines:
        stripped = line.lstrip()
        head = head_re.match(stripped)
        is_comment_line = (stripped.startswith("(*") or stripped.startswith("/*")
                           or stripped.startswith("*") or stripped.startswith("//"))

        if head:
            production = head.group(1)
            in_rule = True
        elif not stripped or is_comment_line:
            in_rule = False

        if in_rule and not is_comment_line:
            if notation == "w3c":
                # inline /* … */ comments sit on production lines
                code, sep, comment = line.partition("/*")
                code = _slotify_literals(code, table, production)
                comment = (_slotify_comment(comment, table, production, helpers)
                           if sep else comment)
                out.append(code + sep + comment)
            else:
                out.append(_slotify_literals(line, table, production))
        else:
            out.append(_slotify_comment(line, table, production, helpers))

    text = "\n".join(out)
    text = text.replace(
        "version: 3dom-grammar/1.1.0",
        "version: 3dom-grammar/1.1.0  —  TEMPLATE (slots: {{ TERMINAL_ID }})")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text)

    # Verification: identity render must reproduce the Phase 1 file byte-for-byte.
    rendered = render_slots(text, identity_phi(table)).replace(
        "version: 3dom-grammar/1.1.0  —  TEMPLATE (slots: {{ TERMINAL_ID }})",
        "version: 3dom-grammar/1.1.0")
    with open(src_path, encoding="utf-8") as fh:
        original = fh.read()
    if rendered != original:
        for i, (a, b) in enumerate(zip(rendered.split("\n"), original.split("\n"))):
            if a != b:
                raise SystemExit(
                    f"IDENTITY RENDER MISMATCH in {os.path.basename(src_path)} "
                    f"line {i + 1}\n  rendered: {a!r}\n  phase 1 : {b!r}")
        raise SystemExit(f"IDENTITY RENDER MISMATCH (length) in {src_path}")
    print(f"  {os.path.basename(out_path):<32} identity render == Phase 1 ✓  "
          f"({len(set(re.findall(r'\{\{([A-Z0-9_]+)\}\}', text)))} distinct slots)")


def main() -> int:
    table = load_terminals()
    print(f"build_templates — {GRAMMAR_VERSION}")
    p1 = phase1_dir()
    build(os.path.join(p1, "3dom_grammar.iso.ebnf"),
          os.path.join(HERE, "grammar.iso.template.ebnf"), "iso", table)
    build(os.path.join(p1, "3dom_grammar.w3c.ebnf"),
          os.path.join(HERE, "grammar.w3c.template.ebnf"), "w3c", table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
