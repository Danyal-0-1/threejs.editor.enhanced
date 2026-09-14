"""prompts.py — the φ-aware prompt renderer.

Every syntax-bearing string handed to a model is rendered MECHANICALLY from the
target language's PhiMap. Nothing is hand-written per language, so alpha, beta
and gamma cannot be accidentally taught using 3DOM spellings, and identity gets
no informational advantage.

THE INFORMATION-MATCHING RULE
    The spec tells the model, for every role: the spelling THIS language uses,
    and a plain-English description of what that role MEANS. The description is
    identical across languages; only the spelling changes. A 3DOM spelling never
    appears in an alien prompt, and no prompt ever shows a translation pair.

    The language is called "the scene-edit language" in all four arms. Calling
    identity "3DOM" or "JavaScript" would hand it a name the model has seen in
    pretraining and that the alien arms cannot have.

WHAT IS *NOT* MATCHED, and is the confound under study
    Token count. The same information costs more model tokens in beta and gamma.
    That is measured (fertility), reported, and never corrected for.
"""
from __future__ import annotations

import os, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "alien_syntax", "src"))
sys.path.insert(0, os.path.join(REPO, "grammar_and_3DOM_client"))

from phi import identity_phi, load_candidate, PhiMap                   # noqa: E402
from transpiler import phi_forward                                     # noqa: E402
from fixture_scene import scene_for                                    # noqa: E402

LANGUAGES = ("identity", "alpha", "beta", "gamma")
SUPPORT_CONDITIONS = ("bare", "scaffolded")

# Plain-English meaning of each canonical verb. IDENTICAL in every language;
# only the spelling beside it changes. Argument names are the canonical
# signature from canonicalize.SIGNATURES.
VERB_DOC: dict[str, tuple[str, str]] = {
    "recolor":       ("color",                 "set the colour of the matched parts"),
    "scale":         ("factor",                "resize the matched parts by a factor"),
    "move":          ("dx, dy, dz",            "shift the matched parts along x, y and z"),
    "rotate":        ("axis, degrees",         "rotate the matched parts about an axis"),
    "delete":        ("",                      "remove the matched parts from the scene"),
    "spin":          ("axis, turns, duration", "spin the matched parts; duration is in seconds, larger = slower"),
    "duplicate":     ("dx, dy, dz",            "copy the matched parts, offset by dx, dy, dz"),
    "setMaterial":   ("material",              "replace the material of the matched parts"),
    "setOpacity":    ("opacity",               "set transparency, 0 = invisible, 1 = solid"),
    "setVisible":    ("visible",               "show or hide the matched parts"),
    "wireframe":     ("enabled",               "draw the matched parts as wireframe"),
    "metalness":     ("metalness",             "set how metallic the surface is, 0 to 1"),
    "roughness":     ("roughness",             "set how rough the surface is, 0 to 1"),
    "castShadow":    ("enabled",               "let the matched parts cast shadows"),
    "receiveShadow": ("enabled",               "let the matched parts receive shadows"),
}

# Worked examples, written once in 3DOM and mechanically transliterated. The
# class names are deliberately ABSENT from every fixture scene, so an example
# can never hand a model the answer to a task case.
# The note is a TEMPLATE: {C} is replaced by this language's class sigil, so a
# comment can never print a 3DOM sigil inside an alien prompt.
EXAMPLE_SOURCES = (
    ("one operation on one set of parts",
     "(function(){ $S('.rotor').spin('y',1,2); })();"),
    ("a compound selector - parts that are BOTH {C}panel AND {C}upper",
     "(function(){ $S('.panel.upper').recolor('#00ff00'); })();"),
    ("two separate operations, written as two statements",
     "(function(){ $S('.lamp').setOpacity(0.5); $S('.pylon').scale(2); })();"),
    ("two operations on the SAME parts, chained",
     "(function(){ $S('.strut').move(0,1,0).recolor('#ff0000'); })();"),
)


def phi_for(language: str) -> PhiMap:
    return identity_phi() if language == "identity" else load_candidate(language)


def render_spec(language: str) -> str:
    """The language/API specification — mechanically derived, no 3DOM leakage."""
    phi = phi_for(language)
    s = phi.spelling
    entry, chain = s("T_SELECTOR_ENTRY"), s("T_CHAIN_OP")
    fn = s("T_FUNCTION")
    cls, idd, pseudo = s("T_CLASS_SIGIL"), s("T_ID_SIGIL"), s("T_PSEUDO_SIGIL")
    child, wild = s("T_CHILD"), s("T_WILDCARD")

    # alien spelling -> canonical verb; invert to canonical -> alien so the
    # table is emitted in the fixed canonical order (identical row order in
    # every language, so ordering cannot advantage one arm).
    alien_of_verb = {canon: alien for alien, canon in phi.verbs().items()}
    alien_of_type = {canon: alien for alien, canon in phi.types().items()}
    alien_of_pseudo = {canon: alien for alien, canon in phi.pseudos().items()}

    lines = [
        "You write programs in the scene-edit language described below.",
        "This language is defined ONLY by this specification. Do not assume it",
        "behaves like any other language you have seen.",
        "",
        "PROGRAM SHAPE",
        f"  A program is exactly:   ({fn}(){{ <statements> }})();",
        f"  Each statement selects parts and applies operations:",
        f"      {entry}('<selector>'){chain}<operation>(<args>);",
        f"  Operations may be chained with '{chain}' to act on the same parts:",
        f"      {entry}('<selector>'){chain}<op1>(...){chain}<op2>(...);",
        "  Two different groups of parts need two separate statements.",
        "",
        "SELECTORS  (inside the quotes)",
        f"  {cls}name        parts carrying the tag `name`",
        f"  {idd}name        the part whose identifier is `name`",
        f"  {pseudo}{alien_of_pseudo['selected']}    the parts currently selected by the user",
        f"  {pseudo}{alien_of_pseudo['lasso']}       the parts inside the user's lasso",
        f"  {wild}           every part in the scene",
        f"  {cls}a{cls}b        parts carrying BOTH tags (no space)",
        f"  {cls}a {cls}b       parts tagged `b` anywhere beneath parts tagged `a`",
        f"  {cls}a{child}{cls}b       parts tagged `b` that are DIRECT children of parts tagged `a`",
        "  bare words are node kinds: "
        + ", ".join(f"`{alien_of_type[k]}`" for k in ("mesh", "group", "light", "camera")),
        "",
        "OPERATIONS",
    ]
    calls = {c: f"{alien_of_verb[c]}({a})" for c, (a, _) in VERB_DOC.items()}
    width = max(len(v) for v in calls.values())
    for canon, (_, doc) in VERB_DOC.items():
        lines.append(f"  {calls[canon]:<{width}}   {doc}")

    lines += ["", "EXAMPLES"]
    for note, src in EXAMPLE_SOURCES:
        rendered = src if language == "identity" else phi_forward(src, phi)
        lines += [f"  {note.format(C=cls)}:", f"  {rendered}"]

    lines += [
        "",
        "OUTPUT FORMAT",
        "  Reply with exactly ONE fenced code block containing ONE complete",
        "  program in the language above. No explanation, no prose, no",
        "  alternatives. Emit only operations the request actually asks for.",
    ]
    return "\n".join(lines)


def taught_spellings(language: str) -> dict[str, str]:
    """Every language token the spec TEACHES, as role -> spelling.

    This is the machine-readable contract behind the prompt: a test asserts it
    equals this language's own φ spellings, which proves no 3DOM spelling is
    ever presented to an alien model as a token to write. Scanning the prose
    for 3DOM words cannot do this -- the English DESCRIPTIONS legitimately
    contain words like "rotate" and "group", in every language identically.
    """
    phi = phi_for(language)
    alien_of_verb = {c: a for a, c in phi.verbs().items()}
    alien_of_type = {c: a for a, c in phi.types().items()}
    alien_of_pseudo = {c: a for a, c in phi.pseudos().items()}
    out = {r: phi.spelling(r) for r in (
        "T_SELECTOR_ENTRY", "T_FUNCTION", "T_CHAIN_OP", "T_CLASS_SIGIL",
        "T_ID_SIGIL", "T_PSEUDO_SIGIL", "T_CHILD", "T_WILDCARD")}
    for canon in VERB_DOC:
        out[f"verb:{canon}"] = alien_of_verb[canon]
    for canon in ("mesh", "group", "light", "camera"):
        out[f"type:{canon}"] = alien_of_type[canon]
    for canon in ("selected", "lasso"):
        out[f"pseudo:{canon}"] = alien_of_pseudo[canon]
    return out


def render_scaffold(language: str, asset: str) -> str:
    """The scaffolded condition's addressable-part list, in the target spellings.

    Exactly the information the existing browser scaffolding supplies: which
    parts exist and which tags address them. Rendered with THIS language's
    class sigil, so the scaffold never teaches a 3DOM spelling.
    """
    phi = phi_for(language)
    cls = phi.spelling("T_CLASS_SIGIL")
    scene = scene_for(asset)

    by_class: dict[str, list[str]] = {}
    for name, node in scene.nodes.items():
        for c in sorted(node.classes):
            by_class.setdefault(c, []).append(name)

    lines = ["ADDRESSABLE PARTS IN THE CURRENT SCENE", "", "  parts:"]
    for name in sorted(scene.nodes):
        node = scene.nodes[name]
        lines.append(f"    {name}  \"{node.label}\"  ({node.node_type})")
    lines += ["", "  tags you may select with:"]
    for c in sorted(by_class):
        lines.append(f"    {cls}{c}".ljust(24) + " -> " + ", ".join(sorted(by_class[c])))
    return "\n".join(lines)


def render_user(case: dict, language: str, condition: str) -> str:
    parts = [f'The user asks: "{case["prompt"]}"']
    if condition == "scaffolded":
        parts += ["", render_scaffold(language, case["asset"])]
    parts += ["", "Write the program."]
    return "\n".join(parts)


def render_messages(case: dict, language: str, condition: str) -> list[dict]:
    """The chat messages for one behavioural cell. Identical structure in every
    language and condition; only the rendered spellings and the scaffold move."""
    return [
        {"role": "system", "content": render_spec(language)},
        {"role": "user", "content": render_user(case, language, condition)},
    ]


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "identity"
    cond = sys.argv[2] if len(sys.argv) > 2 else "bare"
    demo = {"prompt": "make the wheels black", "asset": "dumptruck"}
    for m in render_messages(demo, lang, cond):
        print(f"───── {m['role']} ─────")
        print(m["content"])
