"""render_grammar.py — template + φ-map -> concrete grammar package.

    python3 grammar/render_grammar.py beta
    python3 grammar/render_grammar.py alpha beta gamma identity

Validates the φ-map against terminals.json FIRST and fails loudly, then renders
four artifacts per lexicon:

    generated/alien.<id>.iso.ebnf      ISO/IEC 14977 (normative appendix)
    generated/alien.<id>.w3c.ebnf      W3C EBNF      (normative appendix)
    generated/alien.<id>.lark          executable, two-level (outer + selector)
    generated/alien.<id>.diagram.md    Mermaid, mirroring the Phase 1 diagram

Pre-render gates (all raise; none warn):

  G-R1  the φ-map passes every check in src/phi.py (V1–V8), which is where
        I7 (overload groups), I8 (quote terminals frozen) and I9 (T_WS frozen)
        are enforced.
  G-R2  every slot in every template names a SUBSTITUTABLE terminal.
  G-R3  the two EBNF templates between them open a slot for EVERY substitutable
        terminal — a terminal with no slot would silently keep its 3DOM spelling
        in the generated grammar, which is the exact failure this pipeline
        exists to make impossible.
  G-R4  rendering with φ = identity reproduces the Phase 1 .ebnf files
        BYTE-FOR-BYTE. This is the proof that the templates are the Phase 1
        grammar and not a retyping of it.
  G-R5  the rendered .lark loads in Lark at both levels (if lark is installed),
        so a broken lexicon cannot reach the corpus generator.
  G-R6  NOTATION SAFETY. The rendered .ebnf files are re-parsed with Phase 1's
        own grammar_metrics.parse_ebnf and must yield the SAME |N| and |P| as
        the Phase 1 grammar. This catches a spelling that collides with the
        METASYNTAX of the notation rather than with the language: `?` delimits
        an ISO/IEC 14977 special sequence and `|` is the alternation operator,
        so either one silently swallows productions in the generated appendix
        while leaving the language itself untouched. A blacklist would have
        missed the next such character; re-parsing cannot.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))

from phi import (GRAMMAR_VERSION, PhiMap, PhiValidationError,  # noqa: E402
                 identity_phi, load_candidate, load_terminals, phase1_dir,
                 render_slots, slots_in)

TEMPLATES = os.path.join(HERE, "templates")
GENERATED = os.path.join(HERE, "generated")

BANNER = "version: 3dom-grammar/1.1.0  —  TEMPLATE (slots: {{ TERMINAL_ID }})"
PHASE1_BANNER = "version: 3dom-grammar/1.1.0"

ARTIFACTS = (
    ("grammar.iso.template.ebnf", "iso.ebnf", "3dom_grammar.iso.ebnf"),
    ("grammar.w3c.template.ebnf", "w3c.ebnf", "3dom_grammar.w3c.ebnf"),
    ("grammar.lark.template", "lark", None),
    ("grammar.diagram.template.md", "diagram.md", None),
)

LEVEL_SPLIT = "// ══════ LEVEL SPLIT ══════"


def read_template(name: str) -> str:
    with open(os.path.join(TEMPLATES, name), encoding="utf-8") as fh:
        return fh.read()


def _header(phi: PhiMap, kind: str) -> str:
    comment = {"iso.ebnf": ("(*", "*)"), "w3c.ebnf": ("/*", "*/"),
               "lark": ("//", ""), "diagram.md": ("<!--", "-->")}[kind]
    open_c, close_c = comment
    lines = [
        f"{open_c} GENERATED FILE — do not edit.",
        f"   rendered by grammar/render_grammar.py from grammar/templates/",
        f"   lexicon  : φ = {phi.phi_id}",
        f"   grammar  : {GRAMMAR_VERSION} (N and P frozen; only Σ moves)",
        f"   to change the lexicon, edit candidates/phi_{phi.phi_id}.json and re-render. "
        f"{close_c}".rstrip(),
    ]
    if kind == "lark":
        return "\n".join("// " + line.lstrip("/ ") if not line.startswith("//")
                         else line for line in lines) + "\n\n"
    return "\n".join(lines) + "\n\n"


def check_coverage(phi: PhiMap) -> None:
    """G-R2 / G-R3."""
    ebnf_slots: set[str] = set()
    for template_name, _kind, _p1 in ARTIFACTS:
        slots = slots_in(read_template(template_name))
        slots.discard("TERMINAL_ID")            # the banner's illustrative slot
        slots.discard("PHI_ID")                 # diagram metadata slot
        unknown = {s for s in slots if s not in phi.table.by_id}
        if unknown:
            raise PhiValidationError(
                f"[G-R2] {template_name} names unknown terminal id(s): "
                f"{', '.join(sorted(unknown))}")
        frozen = {s for s in slots if not phi.table.by_id[s].substitutable}
        if frozen:
            raise PhiValidationError(
                f"[G-R2] {template_name} opens a slot for frozen terminal(s) "
                f"{', '.join(sorted(frozen))} (I8/I9)")
        if template_name.endswith(".ebnf"):
            ebnf_slots |= slots
    missing = sorted(set(phi.table.substitutable_ids) - ebnf_slots)
    if missing:
        raise PhiValidationError(
            f"[G-R3] {len(missing)} substitutable terminal(s) have no slot in the "
            f"EBNF templates and would silently keep their 3DOM spelling: "
            f"{', '.join(missing)}")


def check_identity_render() -> None:
    """G-R4 — templates ARE the Phase 1 grammar."""
    ident = identity_phi()
    for template_name, kind, phase1_name in ARTIFACTS:
        if phase1_name is None:
            continue
        rendered = render_slots(read_template(template_name), ident)
        rendered = rendered.replace(BANNER, PHASE1_BANNER)
        with open(os.path.join(phase1_dir(), phase1_name), encoding="utf-8") as fh:
            original = fh.read()
        if rendered != original:
            for i, (a, b) in enumerate(zip(rendered.split("\n"),
                                           original.split("\n")), start=1):
                if a != b:
                    raise PhiValidationError(
                        f"[G-R4] identity render of {template_name} differs from "
                        f"Phase 1 at line {i}:\n  rendered {a!r}\n  phase 1  {b!r}")
            raise PhiValidationError(f"[G-R4] identity render of {template_name} "
                                     f"differs from Phase 1 in length")


def split_lark(text: str) -> tuple[str, str]:
    """Split a rendered .lark into (outer, selector) grammar sources (L3)."""
    head, sep, tail = text.partition(LEVEL_SPLIT)
    if not sep:
        raise PhiValidationError("rendered .lark has no LEVEL SPLIT marker")
    tail = tail.split("\n", 1)[1] if "\n" in tail else ""
    return head, tail


def check_lark(text: str, phi_id: str) -> None:
    """G-R5 — the rendered executable grammar actually loads, at both levels."""
    try:
        from lark import Lark
    except ImportError:                                        # pragma: no cover
        print("    (lark not installed — skipping G-R5 executable check)")
        return
    outer, inner = split_lark(text)
    Lark(outer, start="program", parser="earley", ambiguity="explicit",
         lexer="dynamic")
    Lark(inner, start="selector", parser="earley", ambiguity="explicit",
         lexer="dynamic")
    print(f"    G-R5 ✓ both levels of alien.{phi_id}.lark load in Lark (Earley)")


def render_one(phi: PhiMap, *, outdir: str = GENERATED) -> dict[str, str]:
    check_coverage(phi)                                        # G-R2, G-R3
    check_identity_render()                                    # G-R4
    os.makedirs(outdir, exist_ok=True)
    written: dict[str, str] = {}
    for template_name, kind, _p1 in ARTIFACTS:
        text = read_template(template_name)
        text = text.replace("{{ PHI_ID }}", phi.phi_id)
        body = render_slots(text, phi).replace(BANNER, PHASE1_BANNER)
        out = _header(phi, kind) + body
        path = os.path.join(outdir, f"alien.{phi.phi_id}.{kind}")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(out)
        written[kind] = path
        print(f"    wrote {os.path.relpath(path, ALIEN)}")
    with open(written["lark"], encoding="utf-8") as fh:
        check_lark(fh.read(), phi.phi_id)                      # G-R5
    check_notation(written, phi)                               # G-R6
    return written


def check_notation(written: dict[str, str], phi: PhiMap) -> None:
    """G-R6 — the generated appendix must still parse AS EBNF."""
    sys.path.insert(0, phase1_dir())
    import grammar_metrics as GM
    for kind, notation, phase1_name in (("iso.ebnf", "iso", "3dom_grammar.iso.ebnf"),
                                        ("w3c.ebnf", "w3c", "3dom_grammar.w3c.ebnf")):
        base = GM.parse_ebnf(os.path.join(phase1_dir(), phase1_name), notation)
        got = GM.parse_ebnf(written[kind], notation)
        for metric in ("N", "P"):
            if base[metric] != got[metric]:
                raise PhiValidationError(
                    f"[G-R6] alien.{phi.phi_id}.{kind} has |{metric}| = "
                    f"{got[metric]} but Phase 1 has {base[metric]}. A terminal "
                    f"spelling is colliding with the {notation.upper()} EBNF "
                    f"metasyntax and is corrupting the generated appendix. "
                    f"Missing rules: "
                    f"{sorted(set(base['nonterminals']) - set(got['nonterminals']))}")
    print(f"    G-R6 ✓ generated appendices re-parse as EBNF "
          f"(|N|={base['N']}, |P|={base['P']} in both notations)")


def main(argv: list[str]) -> int:
    """`render_grammar.py [--outdir DIR] [lexicon ...]`

    --outdir renders somewhere other than grammar/generated/. It exists so the
    committed artifacts can be REGENERATED AND COMPARED without being
    overwritten first: verifying reproducibility by clobbering the thing you are
    verifying leaves nothing to diff against if the render is wrong.
    """
    outdir = GENERATED
    args = list(argv[1:])
    for i, arg in enumerate(args):
        if arg == "--outdir" and i + 1 < len(args):
            outdir = os.path.abspath(args[i + 1])
            args = args[:i] + args[i + 2:]
            break
        if arg.startswith("--outdir="):
            outdir = os.path.abspath(arg.split("=", 1)[1])
            args = args[:i] + args[i + 1:]
            break
    names = [a for a in args if not a.startswith("-")] or ["alpha", "beta", "gamma"]
    table = load_terminals()
    print(f"render_grammar — {GRAMMAR_VERSION}  "
          f"({len(table.substitutable_ids)} substitutable terminals)")
    if outdir != GENERATED:
        print(f"  outdir = {outdir}")
    for name in names:
        print(f"  φ = {name}")
        phi = load_candidate(name)                             # G-R1
        render_one(phi, outdir=outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
