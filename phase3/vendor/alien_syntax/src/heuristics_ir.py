"""heuristics_ir.py — the scaffolding heuristics, ported off surface strings.

    python3 src/heuristics_ir.py --report        # the porting table
    python3 src/heuristics_ir.py --demo beta     # run them in one lexicon

WHY THIS FILE EXISTS
    The current scaffolding is CSS-specific and operates on surface text: a
    regex over `$S('…')` looking for spaces, an allowlist of CSS-shaped selector
    strings, prompt rules phrased in `.class` / `#id`. None of that transfers to
    an alien lexicon. If scaffolding is stronger in one language than the other,
    RQ3 is confounded at the root — the measured "scaffolding benefit" would be
    partly a measure of which condition the scaffold was written for.

    So every heuristic here operates on the IR or on the grammar's DFA, never on
    surface text, and every message it produces is EMITTED THROUGH φ, so the
    scaffold speaks whichever language the condition is in. A heuristic that
    cannot be ported without surface knowledge is DROPPED FROM BOTH CONDITIONS
    rather than kept in one; those are listed at the bottom of the report with
    the reason.

    The surface originals live in:
      docs/editor/js/ai/validate.js       (the selector-space lint, the JS lint)
      docs/editor/js/AIPrompt.js          (rules 8, 9, 12, 12b, 12c; exemplars)
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from canonicalize import (SIGNATURES, IRProgram, Matcher,  # noqa: E402
                          Operation, Selector, Step, content_hash)
from phi import PhiMap, identity_phi, load_candidate  # noqa: E402
from transpiler import (AmbiguityError, Emitter, ParseError,  # noqa: E402
                        longest_valid_prefix, parse)


@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    severity: str = "warn"          # "warn" | "block"


@dataclass
class Context:
    """Everything a ported heuristic is allowed to see.

    Note what is ABSENT: the surface string is carried only so the DFA-based
    prefix heuristic can locate a failure, and no heuristic may pattern-match on
    it. `addressable` is a set of IR MATCHERS, not a set of selector strings.
    """
    phi: PhiMap
    text: str
    ir: IRProgram | None = None
    parse_error: str | None = None
    addressable: frozenset[Matcher] = frozenset()
    container_names: frozenset[str] = frozenset()

    @property
    def emitter(self) -> Emitter:
        return Emitter(self.phi)

    def say_selector(self, selector: Selector) -> str:
        """Render a selector in THIS condition's lexicon, so feedback never
        leaks 3DOM spelling into the alien arm (or vice versa)."""
        return self.emitter.emit(selector)

    def say_matcher(self, matcher: Matcher) -> str:
        return self.emitter.emit(matcher)


@dataclass(frozen=True)
class Heuristic:
    id: str
    name: str
    before: str
    operates_on: str
    neutrality: str
    source: str
    fn: Callable[[Context], list[Issue]] = field(repr=False, default=lambda c: [])


# ─────────────────────────────────────────────────────────────────────────────
# The ported heuristics
# ─────────────────────────────────────────────────────────────────────────────

def h_parses(ctx: Context) -> list[Issue]:
    if ctx.ir is not None:
        return []
    lvp, total, expected = longest_valid_prefix(ctx.text, ctx.phi)
    where = f"after {lvp} of {total} tokens" if total else "at the first token"
    kinds = ", ".join(sorted(expected)[:6]) or "nothing"
    return [Issue("H3.parse",
                  f"the output is not a program in this language; it stops being "
                  f"one {where}, where the grammar allows: {kinds}", "block")]


def h_nonempty(ctx: Context) -> list[Issue]:
    if ctx.ir is None or ctx.ir.ops:
        return []
    return [Issue("H3.vacuous",
                  "the output is a valid but VACUOUS chain: it selects and then "
                  "does nothing (zero operations)", "block")]


def h_addressable(ctx: Context) -> list[Issue]:
    if ctx.ir is None or not ctx.addressable:
        return []
    out: list[Issue] = []
    for op in ctx.ir.ops:
        for step in op.selector.steps:
            for matcher in step.matchers:
                if matcher.kind in ("wildcard", "pseudo", "type"):
                    continue
                if matcher not in ctx.addressable:
                    allowed = ", ".join(sorted(ctx.say_matcher(m)
                                               for m in ctx.addressable)[:8])
                    out.append(Issue(
                        "H1.unlisted",
                        f"{ctx.say_matcher(matcher)} is not an addressable part; "
                        f"the addressable parts are: {allowed}", "block"))
    return out


def h_concatenated_selector(ctx: Context) -> list[Issue]:
    if ctx.ir is None or not ctx.addressable:
        return []
    out: list[Issue] = []
    for op in ctx.ir.ops:
        steps = op.selector.steps
        if len(steps) < 2:
            continue
        each_listed = all(
            all(m in ctx.addressable for m in step.matchers) for step in steps)
        if each_listed:
            first = ctx.say_selector(Selector((Step(None, steps[0].matchers),)))
            out.append(Issue(
                "H2.concatenation",
                f"this selector has {len(steps)} steps joined by combinators, and "
                f"every step is itself an addressable part — that is usually two "
                f"separate selectors glued together, not one path. Use "
                f"{first} on its own, or one operation per part.", "warn"))
    return out


def h_arg_names(ctx: Context) -> list[Issue]:
    if ctx.ir is None:
        return []
    out: list[Issue] = []
    for op in ctx.ir.ops:
        names = SIGNATURES[op.op]
        unknown = [k for k in op.args if k != "_positional" and k not in names]
        if unknown:
            out.append(Issue(
                "H4.argnames",
                f"operation {op.op!r} takes {list(names)}; got unexpected "
                f"{unknown}", "block"))
        if len(op.args.get("_positional", ())) > len(names):
            out.append(Issue(
                "H4.arity",
                f"operation {op.op!r} takes at most {len(names)} argument(s), "
                f"got {len(op.args['_positional'])}", "block"))
    return out


def h_axis_default(ctx: Context) -> list[Issue]:
    if ctx.ir is None:
        return []
    out: list[Issue] = []
    for op in ctx.ir.ops:
        if op.op not in ("rotate", "spin") or "_positional" in op.args:
            continue
        axis = op.args.get("axis")
        if axis is None:
            out.append(Issue("H5.axis",
                             f"operation {op.op!r} needs an axis and has none; "
                             f"'y' is the conventional default for an "
                             f"unspecified rotation", "warn"))
        elif str(axis) not in ("x", "y", "z"):
            # `rotate(90)` binds 90 to the FIRST signature slot, which is `axis`.
            # The arity is legal and the arg names are legal; only the VALUE
            # reveals the mistake, so the check has to look at the value.
            out.append(Issue("H5.axis",
                             f"operation {op.op!r} has axis={axis!r}; the axis "
                             f"must be 'x', 'y' or 'z' and comes first",
                             "block"))
    return out


def h_colour_value(ctx: Context) -> list[Issue]:
    if ctx.ir is None:
        return []
    out: list[Issue] = []
    for op in ctx.ir.ops:
        value = op.args.get("color")
        if value is None:
            continue
        text = str(value)
        ok = (text.startswith("#") and len(text) in (4, 7)
              and all(c in "0123456789abcdefABCDEF" for c in text[1:]))
        if not ok:
            out.append(Issue("H6.colour",
                             f"{text!r} is not a hex colour; recolor takes "
                             f"#rgb or #rrggbb", "block"))
    return out


def h_chain_not_repeat(ctx: Context) -> list[Issue]:
    if ctx.ir is None:
        return []
    seen: dict[str, int] = {}
    for op in ctx.ir.ops:
        key = content_hash(IRProgram((Operation("delete", op.selector),)))
        seen[key] = seen.get(key, 0) + 1
    if any(n > 1 for n in seen.values()):
        return [Issue("H7.chain",
                      "two or more operations target the identical selector; "
                      "chain them on one selection instead of re-selecting",
                      "warn")]
    return []


def h_part_not_container(ctx: Context) -> list[Issue]:
    if ctx.ir is None or not ctx.container_names:
        return []
    return [Issue("H8.container",
                  f"{ctx.say_matcher(m)} names a container, not a part; editing "
                  f"it affects the whole asset", "block")
            for op in ctx.ir.ops for step in op.selector.steps
            for m in step.matchers
            if m.name in ctx.container_names]


PORTED: tuple[Heuristic, ...] = (
    Heuristic(
        "H3", "output is a program in this language",
        before="looked for the literal token `$S(` in the text and rejected "
               "`ops([...])` by string match (AIPrompt rules 8, 12, 12c)",
        operates_on="the grammar's DFA + the parser",
        neutrality="'does it parse, and if not how far did it get' is defined by "
                   "the grammar, and the two grammars are the same grammar under "
                   "φ; the nLVP figure it reports is measured on the DSL token "
                   "stream, which is token-identical across lexicons",
        source="validate.js / AIPrompt.js rules 8, 12, 12c", fn=h_parses),
    Heuristic(
        "H3b", "output is not vacuous",
        before="not present — a bare `$S('.x');` passed the surface lint",
        operates_on="IR (`len(ops)`)",
        neutrality="the op list is the shared IR; emptiness is a property of the "
                   "IR, and D5 already fixes how it scores",
        source="new, from SCORING_POLICY.md D5", fn=h_nonempty),
    Heuristic(
        "H1", "selector names an addressable part",
        before="string-compared the selector text against a list of CSS-shaped "
               "strings ('.body #body .wheel .treebark')",
        operates_on="IR matchers (`kind` + `name`)",
        neutrality="matcher NAMES are T_IDENT values, which are substitutable:"
                   "false and copied verbatim into the IR — identical in every "
                   "lexicon; the sigil that used to carry the kind is now the "
                   "IR's `kind` field, so no spelling is consulted",
        source="AIPrompt.js rule 12", fn=h_addressable),
    Heuristic(
        "H2", "selector is not two selectors glued together",
        before="regex `/[.#]\\s+[.#a-zA-Z]/` over the raw selector string, "
               "flagging spaces (validate.js:271-283)",
        operates_on="IR steps + combinators",
        neutrality="the descendant combinator is an IR `combinator` field, not a "
                   "space; the heuristic asks 'are these steps each independently "
                   "addressable', which is a question about the scene, not the "
                   "syntax",
        source="validate.js:271-283", fn=h_concatenated_selector),
    Heuristic(
        "H4", "argument names and arity match the operation",
        before="matched parameter-name strings (`angle`, `speed`, `duration`) in "
               "the emitted JSON (AIPrompt rule 12b)",
        operates_on="IR args + canonicalize.SIGNATURES",
        neutrality="SIGNATURES is keyed on the CANONICAL verb name in the IR, "
                   "not on the surface verb spelling; the same table serves both "
                   "conditions",
        source="AIPrompt.js rule 12b", fn=h_arg_names),
    Heuristic(
        "H5", "rotation carries an axis",
        before="prose rule 'when unsure which axis, default to y'",
        operates_on="IR args",
        neutrality="a missing key in the IR arg bag; no spelling involved",
        source="AIPrompt.js rule 12b", fn=h_axis_default),
    Heuristic(
        "H6", "colour argument is a hex value",
        before="prose colour table plus 'do not guess colour codes' (rule 9)",
        operates_on="IR arg VALUE",
        neutrality="the value is a T_STRING_BODY copied verbatim into the IR; "
                   "the colour-word prior is a natural-language prior about "
                   "colour, equally available in both conditions and not a "
                   "property of the DSL's syntax",
        source="AIPrompt.js rules 9, 20", fn=h_colour_value),
    Heuristic(
        "H7", "chain rather than re-select",
        before="prose examples contrasting `$S('.a').x().y()` with two `$S` "
               "statements",
        operates_on="IR (selector content hashes)",
        neutrality="identity of two selectors is decided by the canonical content "
                   "hash, which is surface-blind by construction (C7)",
        source="AIPrompt.js rules 8, 12", fn=h_chain_not_repeat),
    Heuristic(
        "H8", "target a part, not the container",
        before="prose blocklist of container spellings (#tree, #model, "
               "#dumptruck) and 'never traverse-all'",
        operates_on="IR matcher names + the fixture scene",
        neutrality="container-ness is a property of the SCENE GRAPH, resolved "
                   "against the fixture (TERMINOLOGY.md §4); the surface version "
                   "only looked like syntax because the names were spelled with "
                   "CSS sigils",
        source="AIPrompt.js rule 12", fn=h_part_not_container),
)

# ─────────────────────────────────────────────────────────────────────────────
# The ones that CANNOT be ported. These are dropped from BOTH conditions.
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Dropped:
    id: str
    name: str
    why_unportable: str
    action: str


DROPPED: tuple[Dropped, ...] = (
    Dropped(
        "H9", "sigil forgiveness / CSS-typo repair",
        why_unportable=(
            "The surface scaffold silently accepts `#wheel` where the addressable "
            "list has `.wheel`, and repairs `recolour`->`recolor`. Both repairs "
            "work by exploiting a CSS/English prior about which spellings are "
            "'nearly right'. In the alien lexicon there is no such prior to "
            "exploit: `%wheel` versus `~wheel` are not near-neighbours to a model "
            "that has never seen either. Any edit-distance surrogate would be a "
            "DIFFERENT mechanism, not the same heuristic ported."),
        action="DROPPED FROM BOTH CONDITIONS. Keeping it in the 3DOM arm would "
               "hand that arm a repair path the alien arm cannot have, which is "
               "precisely the RQ3 confound this file exists to remove."),
    Dropped(
        "H10", "three.js / editor JS API hallucination lint",
        why_unportable=(
            "validate.js's ALLOWED_CLASSES / COMMAND_ARITY / MATERIAL_KEYS lint "
            "targets the RAW-JS escape hatch (`new FBXLoader()`, "
            "`AddObjectCommand` arity, `metal:1` vs `metalness:1`). It is about "
            "the surrounding JavaScript API, not about the DSL, and the DSL has "
            "no analogue of it in either lexicon."),
        action="DROPPED FROM BOTH CONDITIONS by disabling the raw-JS path for the "
               "study. If the escape hatch is ever re-enabled it must be enabled "
               "in both arms with the identical lint, and reported as its own "
               "factor."),
    Dropped(
        "H11", "memorised few-shot exemplars",
        why_unportable=(
            "The exemplars in AIPrompt.js are 3DOM source strings. Handing the "
            "3DOM arm text the model may have seen and the alien arm text it "
            "certainly has not is the confound in miniature."),
        action="REPLACED, not dropped: exemplars are RENDERED from a fixed list "
               "of IR objects through transpiler.Emitter, so both arms get the "
               "same COUNT of exemplars carrying the same IR content, each spelled "
               "in its own lexicon. See exemplars() below."),
)


EXEMPLAR_IR: tuple[str, ...] = (
    "(function(){ $S('.wheel').recolor('#111111'); })();",
    "(function(){ $S('.wheel').recolor('#111111').scale(1.5); })();",
    "(function(){ $S('.wheel').recolor('#111111'); $S('.body').recolor('#ff0000'); })();",
    "(function(){ $S('.fan').spin('y',1,2); })();",
    "(function(){ $S('#dump-bed').scale(1.5); })();",
)


def exemplars(phi: PhiMap) -> list[str]:
    """The few-shot exemplars for one condition, rendered from shared IR.

    Same count, same IR content, one lexicon each — so exemplar strength is held
    constant across conditions by construction rather than by inspection.
    """
    ident = identity_phi(phi.table)
    emitter = Emitter(phi)
    return [emitter.emit(parse(src, ident)) for src in EXEMPLAR_IR]


def run(text: str, phi: PhiMap, *, addressable: Iterable[Matcher] = (),
        containers: Iterable[str] = ()) -> list[Issue]:
    """Run every ported heuristic over one model output, in one lexicon."""
    ctx = Context(phi=phi, text=text, addressable=frozenset(addressable),
                  container_names=frozenset(containers))
    try:
        ctx.ir = parse(text, phi)
    except (ParseError, AmbiguityError) as exc:
        ctx.parse_error = str(exc)
    issues: list[Issue] = []
    for heuristic in PORTED:
        issues.extend(heuristic.fn(ctx))
    return issues


def report() -> None:
    print("# Heuristic porting table — surface -> IR/DFA\n")
    print("| id | heuristic | what it did BEFORE (surface) | what it operates on "
          "NOW | why that is syntax-neutral |")
    print("|---|---|---|---|---|")
    for h in PORTED:
        print(f"| `{h.id}` | {h.name} | {h.before} | **{h.operates_on}** | "
              f"{h.neutrality} |")
    print("\n## Not portable — dropped from BOTH conditions\n")
    for d in DROPPED:
        print(f"### `{d.id}` — {d.name}\n")
        print(f"**Why it cannot be ported.** {d.why_unportable}\n")
        print(f"**Action.** {d.action}\n")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--demo", metavar="LEXICON", default=None)
    args = ap.parse_args(argv[1:])
    if args.report or not args.demo:
        report()
    if args.demo:
        phi = load_candidate(args.demo)
        from transpiler import phi_forward
        listed = frozenset({Matcher("class", "wheel"), Matcher("class", "body"),
                            Matcher("class", "car"), Matcher("id", "dump-bed")})
        print(f"\n## Demo — lexicon `{phi.phi_id}`\n")
        print("Exemplars handed to the model in this condition:")
        for e in exemplars(phi):
            print(f"    {e}")
        cases = [
            "(function(){ $S('.car .wheel').recolor('#111111'); })();",   # H2
            "(function(){ $S('.rims').scale(2); })();",                   # H1
            "(function(){ $S('.wheel'); })();",                           # H3b
            "(function(){ $S('.wheel').rotate(90); })();",                # H5/H4
            "(function(){ $S('.wheel').recolor('red'); })();",            # H6
            "(function(){ $S('.wheel').scale(2); $S('.wheel').move(0,1,0); })();",
        ]
        for src in cases:
            alien = phi_forward(src, phi)
            print(f"\n  {alien}")
            for issue in run(alien, phi, addressable=listed) or [
                    Issue("ok", "no issues")]:
                print(f"    [{issue.severity:5}] {issue.code:17} {issue.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
