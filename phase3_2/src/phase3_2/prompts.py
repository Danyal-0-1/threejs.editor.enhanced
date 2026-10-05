"""prompts.py — the remote specification r, and its matched no-rule control.

----------------------------------------------------------------------------
DEFECT P32-002: THE RULE PROMPT CONTAINED NO RULE
----------------------------------------------------------------------------
The first Phase 3.2 Arm A run used:

    "You are writing 3DOM, a language for editing 3D scenes.
     Follow the token table exactly; it overrides any CSS or JavaScript
     convention you may expect."

There is no token table in it. The remote specification `r` therefore carried
**zero mapping information**, so that run did not measure rule-override at
all -- it measured raw prior preference with an irrelevant preamble attached.

The distinction is the entire hypothesis. `M_seq` is only a reversion measure
if the correct spelling was actually SPECIFIED somewhere in the context. With
no table, the "correct" spelling is one the model was never told about, and a
low margin means nothing more than "the model has never seen this language".

----------------------------------------------------------------------------
THE TWO CONDITIONS
----------------------------------------------------------------------------
    rule     the full phi mapping table, rendered from the phi-map itself
    norule   a LENGTH- AND SHAPE-MATCHED control with the mapping removed

The control is matched, not absent. A bare prompt would differ from the rule
prompt in length, token count and register as well as in content, and any
difference between conditions could be attributed to those. `norule` keeps the
same framing sentences and the same table SHAPE, listing the roles while
withholding which spelling each takes.

The contrast that matters is then

    rule_effect_i = M_seq(rule)_i - M_seq(norule)_i

which is how much the supplied table moved this site. It is the direct
analogue of `S_shift` in `phase3.linter`, measured on the instruction side.

A rule prompt that fails to move the margin at all is itself a finding: it
means the specification is not being used, which is the PLSemanticsBench
result reproduced at the token level.
"""

from __future__ import annotations

from phase3_2 import _vendor  # noqa: F401

import phi as P  # noqa: E402

PREAMBLE = (
    "You are writing 3DOM, a domain-specific language for editing 3D scenes.\n"
    "3DOM resembles CSS and jQuery, but several tokens have been REASSIGNED.\n"
    "The table below is authoritative and overrides any CSS or JavaScript\n"
    "convention you may expect.\n")

CLOSER = "\nWrite 3DOM using exactly the spellings above.\n"

# Roles whose spelling the model must get right. Listed in a fixed order so
# the prompt is deterministic and two runs are comparable.
ROLE_LABEL: dict[str, str] = {
    "T_SELECTOR_ENTRY": "selector entry",
    "T_CLASS_SIGIL": "class selector sigil",
    "T_ID_SIGIL": "id selector sigil",
    "T_PSEUDO_SIGIL": "pseudo selector sigil",
    "T_CHILD": "child combinator",
    "T_WILDCARD": "universal selector",
    "T_CHAIN_OP": "operation chain operator",
    "T_TYPE_MESH": "type keyword: mesh object",
    "T_TYPE_GROUP": "type keyword: group object",
    "T_TYPE_LIGHT": "type keyword: light object",
    "T_TYPE_CAMERA": "type keyword: camera object",
    "T_PSEUDO_SELECTED": "pseudo keyword: current selection",
    "T_PSEUDO_LASSO": "pseudo keyword: lasso selection",
    "T_VERB_RECOLOR": "operation: change colour",
    "T_VERB_SCALE": "operation: resize",
    "T_VERB_MOVE": "operation: translate",
    "T_VERB_ROTATE": "operation: rotate",
    "T_VERB_DELETE": "operation: remove",
    "T_VERB_SPIN": "operation: animated spin",
    "T_VERB_DUPLICATE": "operation: copy",
    "T_VERB_SETMATERIAL": "operation: set material",
    "T_VERB_SETOPACITY": "operation: set opacity",
    "T_VERB_SETVISIBLE": "operation: set visibility",
    "T_VERB_WIREFRAME": "operation: wireframe on/off",
    "T_VERB_METALNESS": "operation: set metalness",
    "T_VERB_ROUGHNESS": "operation: set roughness",
    "T_VERB_CASTSHADOW": "operation: cast shadow on/off",
    "T_VERB_RECEIVESHADOW": "operation: receive shadow on/off",
}


def rule_prompt(phi: P.PhiMap) -> str:
    """The full mapping table, rendered FROM the phi-map.

    Rendered, never hand-written: a hand-written table would drift from the
    lexicon it claims to describe, and the model would be told a mapping the
    grammar does not implement -- which would look exactly like reversion.
    """
    lines = [PREAMBLE, "\nTOKEN TABLE\n"]
    for tid, label in ROLE_LABEL.items():
        lines.append(f"  {label:34s} {phi.spelling(tid)}\n")
    lines.append(CLOSER)
    return "".join(lines)


def norule_prompt(phi: P.PhiMap) -> str:
    """Matched control: same framing and table SHAPE, spellings withheld.

    `phi` is accepted and deliberately unused for the spellings, so that the
    two prompts are generated from the same call site and cannot drift apart
    in framing. The only thing removed is the mapping itself.
    """
    lines = [
        "You are writing 3DOM, a domain-specific language for editing 3D scenes.\n"
        "3DOM resembles CSS and jQuery, but several tokens have been REASSIGNED.\n"
        "The roles below are authoritative and override any CSS or JavaScript\n"
        "convention you may expect.\n",
        "\nROLE LIST\n",
    ]
    for _tid, label in ROLE_LABEL.items():
        lines.append(f"  {label}\n")
    lines.append("\nWrite 3DOM using the correct spellings.\n")
    return "".join(lines)


CONDITIONS = {"rule": rule_prompt, "norule": norule_prompt}


def describe(phi: P.PhiMap) -> dict:
    """Prompt metadata for the result record -- lengths must be reported.

    If the two conditions differ wildly in length, a difference between them
    is partly a context-length effect and must be reported as such.
    """
    r, n = rule_prompt(phi), norule_prompt(phi)
    return {"rule_chars": len(r), "norule_chars": len(n),
            "rule_lines": r.count("\n"), "norule_lines": n.count("\n"),
            "n_roles": len(ROLE_LABEL)}


# ---------------------------------------------------------------------------
# paraphrase robustness (next-steps item: the result rests on ONE prompt)
# ---------------------------------------------------------------------------
# Every Phase 3.2 number so far comes from a single rule phrasing. If the
# effect moves materially across paraphrases, the finding is about that
# wording and not about the language. These three keep the SAME table --
# rendered identically from phi -- and vary only the framing around it:
#
#   p0  the default: "authoritative, overrides CSS/JS"
#   p1  terse, imperative, no justification
#   p2  verbose and explicit about the override, naming the conflict
#
# They are deliberately different in register and length, because that is what
# a robustness check has to vary. Report all three; if they disagree, the
# honest headline is the range, not the best one.

_FRAMINGS = {
    "p0": (PREAMBLE, CLOSER),
    "p1": ("3DOM token table. Use these spellings.\n",
           "\nEmit 3DOM.\n"),
    "p2": ("You are writing 3DOM, a domain-specific language for editing 3D scenes.\n"
           "Its surface resembles CSS selectors and jQuery method chaining, and\n"
           "that resemblance is misleading: several tokens have been reassigned to\n"
           "different roles. Where the table below disagrees with what CSS or\n"
           "JavaScript would lead you to expect, the table is correct and your\n"
           "expectation is wrong.\n",
           "\nUse exactly the spellings in the table above. Do not substitute the\n"
           "CSS or JavaScript spelling for any role.\n"),
}


def paraphrase(phi: P.PhiMap, which: str = "p0") -> str:
    """The same rendered table under a different framing."""
    pre, close = _FRAMINGS[which]
    lines = [pre, "\nTOKEN TABLE\n"]
    for tid, label in ROLE_LABEL.items():
        lines.append(f"  {label:34s} {phi.spelling(tid)}\n")
    lines.append(close)
    return "".join(lines)


PARAPHRASES = tuple(_FRAMINGS)


def examples_for(phi, backend, templates, n: int) -> list[str]:
    """Correct programs in the target lexicon, used as in-context evidence.

    These are the DOSE in the extinction ladder. They must be correct programs
    in the lexicon under test, because the question is how much demonstrated
    evidence it takes to overcome the prior -- not how much text.
    """
    out = []
    for t in templates:
        try:
            out.append(backend.render(t.ir, phi))
        except Exception:
            continue
        if len(out) >= n:
            break
    return out
