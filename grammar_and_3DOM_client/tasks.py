"""tasks.py -- the five task scorers, grading the Operation IR.

WHAT CHANGED AND WHY
    The previous grader read raw text. That made 3DOM and the Alien-Syntax
    language incomparable: identical semantics scored differently because the
    surface strings differed. Every scorer below now reads the JSON IR defined in
    ir_schema.json, so both languages are graded against ONE ground truth
    (SCORING_POLICY.md S6).

THE UNIVERSAL CONTRACT
    Every scorer takes a parsed IR object (a dict, already through json.loads)
    plus that case's gold expectation, and returns a float: 1.0 or 0.0. Never
    None, never a bool, never a raise. Scorers run over adversarial input -- a
    0.5B model emits half-formed JSON, dropped fields, wrong types -- and a
    scorer that raises turns a model failure into a HARNESS failure and loses the
    row. Malformed input is a 0.0, which is the honest reading: the model did not
    do the task.

    Every scorer also has a _report twin returning (score, reasons). The float is
    what the matrix aggregates; the reasons are what you read when a cell looks
    wrong. Debuggability is not optional in a grader you intend to publish from.
"""

from __future__ import annotations

import math
import re
from typing import Any, Iterable, Mapping, Sequence

from fixture_scene import FixtureScene, resolve, resolve_all

GRAMMAR_VERSION = "3dom-grammar/1.1.0"

PASS: float = 1.0
FAIL: float = 0.0

Report = tuple[float, list[str]]


# ==============================================================================
# SHARED IR TRAVERSAL
# ==============================================================================

def ops_of(ir: Any) -> list[dict[str, Any]]:
    """Pull the op list out of whatever shape actually arrived.

    Canonical form is {"grammar_version":..., "ops":[...]}. In practice models
    also emit a bare op object, or a bare array. Accepting those costs nothing
    and prevents the grader from scoring its own strictness.

    Note `.get("ops")` rather than `ir["ops"]`: a dropped field is a MISSING
    ANSWER (score 0.0), not a KeyError that kills the run.
    """
    if isinstance(ir, Mapping):
        ops = ir.get("ops")
        if isinstance(ops, list):
            return [op for op in ops if isinstance(op, Mapping)]
        if ir.get("op") is not None:
            return [dict(ir)]
        return []
    if isinstance(ir, Sequence) and not isinstance(ir, (str, bytes)):
        return [op for op in ir if isinstance(op, Mapping)]
    return []


def is_vacuous(ir: Any) -> bool:
    """The D5 case: parses, zero operations. A parse SUCCESS and a task FAILURE
    on every task whose target IR carries at least one op."""
    return len(ops_of(ir)) == 0


def has_grammar_version(ir: Any) -> bool:
    """SCORING_POLICY S6a: the builder stamps a version into every IR object. An
    unstamped IR is unreportable -- checked by the corpus gate, not by scoring,
    so a builder bug never silently changes a task number."""
    return isinstance(ir, Mapping) and ir.get("grammar_version") == GRAMMAR_VERSION


# ==============================================================================
# TASK 1 -- OP-SELECTION
# ==============================================================================
# INPUT   ir: dict (parsed IR)   target: str | Sequence[str]
# OUTPUT  float in {0.0, 1.0}
#
# Exact verb match against the closed 15-verb set. NO synonyms here, on purpose:
# op-selection asks whether the model picked the right verb from a set it was
# shown. Accepting 'paint' for 'recolor' would measure something else. (Synonyms
# ARE allowed in task 4, where the question is decomposition, not naming.)

def score_op_selection(ir: Any, target: str | Sequence[str]) -> float:
    return score_op_selection_report(ir, target)[0]


def score_op_selection_report(ir: Any, target: str | Sequence[str]) -> Report:
    ops = ops_of(ir)
    if not ops:
        return FAIL, ["no ops in IR (vacuous or unparsed)"]

    wanted = [target] if isinstance(target, str) else list(target or [])
    if not wanted:
        return FAIL, ["no target verb supplied"]

    if len(ops) < len(wanted):
        return FAIL, [f"{len(ops)} op(s) emitted, target sequence needs {len(wanted)}"]

    reasons: list[str] = []
    for i, want in enumerate(wanted):
        got = ops[i].get("op")
        if not isinstance(got, str) or got != want:
            reasons.append(f'op{i}: "{got}" != "{want}"')

    return (FAIL, reasons) if reasons else (PASS, [f"verb(s) ok: {', '.join(wanted)}"])


# ==============================================================================
# TASK 2 -- ARG-EXTRACTION
# ==============================================================================
# INPUT   ir: dict   expected_args: Mapping[str, Any]   strict_keys: bool
# OUTPUT  float in {0.0, 1.0}
#
# POLICY (this is the axis that changed): grade the MATHEMATICAL CONTENT, ignore
# arbitrary key spelling. {"factor":2}, {"scale":2} and {"amount":2} all express
# the same edit, so all three pass; {"factor":0.5} does not, because 0.5 is a
# different edit. Values are compared three ways depending on the gold's TYPE:
#   colour -> perceptual family ("black", 0x111111 and "#111" are one answer)
#   dict   -> a {min}/{max} RANGE, for modifiers with no canonical number
#             ("slowly" is any duration >= 3; demanding an exact 4 tests nothing)
#   scalar -> numeric equality under tolerance, else normalised string equality
#
# strict_keys=True restores the old canonical-KEY-only behaviour. Keep it around:
# the host dispatcher (opPrimitive.js) does NOT map synonyms, so {"value":2} is
# correct IR that the ENGINE would drop. Key-lenient measures the model,
# key-strict measures end-to-end executability. They are different claims -- pick
# one per column and say which in the table.

_ARG_ALIASES: dict[str, frozenset[str]] = {
    "color":    frozenset({"color", "colour", "hex", "fill", "tint", "rgb"}),
    "factor":   frozenset({"factor", "scale", "amount", "multiplier", "ratio", "size"}),
    "dx":       frozenset({"dx", "x", "offsetx", "deltax", "translatex"}),
    "dy":       frozenset({"dy", "y", "offsety", "deltay", "translatey", "height", "up"}),
    "dz":       frozenset({"dz", "z", "offsetz", "deltaz", "translatez"}),
    "axis":     frozenset({"axis", "around", "about"}),
    "degrees":  frozenset({"degrees", "deg", "angle", "rotation"}),
    "turns":    frozenset({"turns", "revolutions", "rotations", "spins"}),
    "duration": frozenset({"duration", "dur", "time", "seconds", "secs", "length"}),
    "opacity":  frozenset({"opacity", "alpha", "transparency"}),
}

# Ambiguous aliases resolved by the OP, not globally. A bare "value" means colour
# on a recolor and a magnitude on a scale; mapping it globally would silently
# credit the wrong argument.
_OP_SPECIFIC_ALIASES: dict[str, dict[str, str]] = {
    "recolor":    {"value": "color", "to": "color"},
    "scale":      {"value": "factor", "by": "factor"},
    "setOpacity": {"value": "opacity"},
    "rotate":     {"value": "degrees"},
    "spin":       {"value": "duration"},
}

# DELIBERATELY ABSENT: a global "speed" -> "duration" alias. Speed is the INVERSE
# of duration; "speed: 4" for "slowly" is the opposite edit. Aliasing it would
# manufacture passes out of wrong answers -- the exact false-positive class the
# eval gate lists.

# Positional chain args map to names by op signature: $S(...).move(0,0.5,0).
_SIGNATURES: dict[str, tuple[str, ...]] = {
    "recolor": ("color",),
    "scale": ("factor", "axis"),
    "move": ("dx", "dy", "dz"),
    "rotate": ("axis", "degrees"),
    "duplicate": ("dx", "dy", "dz"),
    "spin": ("axis", "turns", "duration"),
    "setOpacity": ("opacity",),
}

_NESTED_CONTAINERS = frozenset({"position", "offset", "translate", "delta", "vector", "vec"})
_AXIS_TO_DELTA = {"x": "dx", "y": "dy", "z": "dz"}


def arg_bag(op: Mapping[str, Any], *, canonicalise: bool = True) -> dict[str, Any]:
    """One op's args -> a flat {canonical_key: value} bag.

    Handles four shapes the builder can hand us: an object bag, a positional
    list, a `_positional` escape hatch, and one level of nesting
    ({"position": {"y": 0.5}} -> {"dy": 0.5}).
    """
    verb = str(op.get("op") or "")
    raw = op.get("args")

    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, Mapping)):
        raw = {"_positional": list(raw)}
    if not isinstance(raw, Mapping):
        return {}

    flat: dict[str, Any] = {}

    positional = raw.get("_positional")
    if isinstance(positional, Sequence) and not isinstance(positional, (str, bytes)):
        for name, value in zip(_SIGNATURES.get(verb, ()), positional):
            flat[name] = value

    for key, value in raw.items():
        if key == "_positional":
            continue
        if isinstance(value, Mapping) and str(key).lower() in _NESTED_CONTAINERS:
            for axis, inner in value.items():
                mapped = _AXIS_TO_DELTA.get(str(axis).lower())
                if mapped:
                    flat[mapped] = inner
            continue
        flat[_canonical_key(verb, key) if canonicalise else str(key)] = value

    return flat


def _canonical_key(verb: str, key: Any) -> str:
    normalised = re.sub(r"[^a-z0-9]", "", str(key).lower())
    op_specific = _OP_SPECIFIC_ALIASES.get(verb, {})
    if normalised in {re.sub(r"[^a-z0-9]", "", k) for k in op_specific}:
        for alias, canonical in op_specific.items():
            if re.sub(r"[^a-z0-9]", "", alias) == normalised:
                return canonical
    for canonical, aliases in _ARG_ALIASES.items():
        if normalised in aliases:
            return canonical
    return str(key)


def score_arg_extraction(ir: Any, expected_args: Mapping[str, Any] | None,
                         *, strict_keys: bool = False) -> float:
    return score_arg_extraction_report(ir, expected_args, strict_keys=strict_keys)[0]


def score_arg_extraction_report(ir: Any, expected_args: Mapping[str, Any] | None,
                                *, strict_keys: bool = False) -> Report:
    if not expected_args:
        return PASS, ["n/a (case carries no arg expectation)"]

    ops = ops_of(ir)
    if not ops:
        return FAIL, ["no ops in IR"]

    bag = arg_bag(ops[0], canonicalise=not strict_keys)
    reasons: list[str] = []

    for key, want in expected_args.items():
        if key not in bag:
            reasons.append(f"missing arg {key}")
            continue
        got = bag[key]

        if key == "color":
            got_family, want_family = colour_family(got), colour_family(want)
            if got_family is None or got_family != want_family:
                reasons.append(f"color {got!r} -> {got_family} != {want} ({want_family})")
        elif isinstance(want, Mapping):
            n = as_number(got)
            if n is None:
                reasons.append(f"{key}={got!r} is not numeric")
                continue
            low, high = want.get("min"), want.get("max")
            if low is not None and n < low:
                reasons.append(f"{key}={n} < min {low}")
            if high is not None and n > high:
                reasons.append(f"{key}={n} > max {high}")
        else:
            got_n, want_n = as_number(got), as_number(want)
            if got_n is not None and want_n is not None:
                if not math.isclose(got_n, want_n, rel_tol=1e-6, abs_tol=1e-9):
                    reasons.append(f"{key}={got_n} != {want_n}")
            elif str(got).strip().lower() != str(want).strip().lower():
                reasons.append(f"{key}={got!r} != {want!r}")

    return (FAIL, reasons) if reasons else (PASS, ["args ok"])


# -- numeric + colour helpers --------------------------------------------------

_NUMBER = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def as_number(value: Any) -> float | None:
    """Coerce to float, or None. Booleans are rejected: `True` is not 1.0 here,
    and letting it through would pass a visibility flag as a scale factor."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = _NUMBER.search(value)          # tolerates "1.5x", "2 units", "+0.5"
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
    return None


_NAMED_COLOURS = {
    "black": 0x000000, "white": 0xFFFFFF, "gray": 0x808080, "grey": 0x808080,
    "silver": 0xC0C0C0, "red": 0xFF0000, "crimson": 0xDC143C, "maroon": 0x800000,
    "orange": 0xFFA500, "gold": 0xFFD700, "yellow": 0xFFFF00, "amber": 0xFFBF00,
    "green": 0x008000, "lime": 0x00FF00, "cyan": 0x00FFFF, "teal": 0x008080,
    "blue": 0x0000FF, "navy": 0x000080, "purple": 0x800080, "violet": 0xEE82EE,
    "magenta": 0xFF00FF, "pink": 0xFFC0CB, "brown": 0x8B4513,
}

# Families collapse the answers a human would call "the same colour". The gold
# values in the case table are family names.
_FAMILY_OF = {
    "black": "black", "white": "white",
    "gray": "gray", "grey": "gray", "silver": "gray",
    "red": "red", "crimson": "red", "maroon": "red",
    "orange": "gold", "gold": "gold", "yellow": "gold", "amber": "gold",
    "green": "green", "lime": "green",
    "cyan": "cyan", "teal": "cyan",
    "blue": "blue", "navy": "blue",
    "purple": "purple", "violet": "purple", "magenta": "purple", "pink": "purple",
    "brown": "brown",
}


def as_rgb(value: Any) -> tuple[int, int, int] | None:
    """'black' | '#111' | '#111111' | '0x111111' | 0x111111 -> (r, g, b)."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)
    if not isinstance(value, str):
        return None

    text = value.strip().lower()
    if text in _NAMED_COLOURS:
        return as_rgb(_NAMED_COLOURS[text])

    hex_match = re.fullmatch(r"(?:#|0x)?([0-9a-f]{3}|[0-9a-f]{6})", text)
    if not hex_match:
        return None
    digits = hex_match.group(1)
    if len(digits) == 3:                        # '#111' -> '#111111'
        digits = "".join(c * 2 for c in digits)
    return as_rgb(int(digits, 16))


def colour_family(value: Any) -> str | None:
    """Classify any colour form into a perceptual family.

    Named input takes the table directly. Hex input is classified numerically:
    low chroma splits into black/gray/white by lightness, otherwise hue picks the
    family. That is why 'black' and 0x111111 score identically -- which they must,
    since the host renders 'black' AS 0x111111.
    """
    if isinstance(value, str) and value.strip().lower() in _FAMILY_OF:
        return _FAMILY_OF[value.strip().lower()]

    rgb = as_rgb(value)
    if rgb is None:
        return None

    r, g, b = (channel / 255.0 for channel in rgb)
    high, low = max(r, g, b), min(r, g, b)
    chroma = high - low

    if chroma < 0.12:                           # achromatic
        if high < 0.25:
            return "black"
        if high > 0.85:
            return "white"
        return "gray"

    if high == r:
        hue = 60.0 * (((g - b) / chroma) % 6.0)
    elif high == g:
        hue = 60.0 * (((b - r) / chroma) + 2.0)
    else:
        hue = 60.0 * (((r - g) / chroma) + 4.0)

    if hue < 20 or hue >= 330:
        return "brown" if high < 0.55 and chroma < 0.55 else "red"
    if hue < 70:
        return "gold"
    if hue < 170:
        return "green"
    if hue < 200:
        return "cyan"
    if hue < 260:
        return "blue"
    return "purple"


# ==============================================================================
# TASK 3 -- LABELING
# ==============================================================================
# INPUT   ir_or_label: dict | str    gold: Sequence[str]
# OUTPUT  float in {0.0, 1.0}
#
# The only task whose "IR" may legitimately be a bare string: the labeling probe
# asks for a human name, not a program. Accept both, read op["label"] or a
# top-level "label" when given an object.
#
# Matching is normalise-then-substring-either-direction against a SYNONYM LIST.
# "dump bed" and "bed" are the same answer; rejecting one would measure phrasing,
# not part identification. Substring cuts both ways deliberately -- but only after
# normalisation strips punctuation and case, so the leniency is bounded.

def score_labeling(ir_or_label: Any, gold: Sequence[str]) -> float:
    return score_labeling_report(ir_or_label, gold)[0]


def score_labeling_report(ir_or_label: Any, gold: Sequence[str]) -> Report:
    predicted = _extract_label(ir_or_label)
    if not predicted:
        return FAIL, ["no label produced"]

    needle = _normalise_label(predicted)
    if not needle:
        return FAIL, [f"label {predicted!r} normalised to nothing"]

    for candidate in gold or ():
        hay = _normalise_label(candidate)
        if hay and (needle == hay or needle in hay or hay in needle):
            return PASS, [f'"{predicted}" ~ "{candidate}"']

    return FAIL, [f'"{predicted}" not in {{{", ".join(gold or ())}}}']


def _extract_label(source: Any) -> str:
    if isinstance(source, str):
        return source
    if isinstance(source, Mapping):
        if isinstance(source.get("label"), str):
            return source["label"]
        for op in ops_of(source):
            if isinstance(op.get("label"), str):
                return op["label"]
    return ""


def _normalise_label(text: Any) -> str:
    """Punctuation becomes a SPACE, not nothing. Deleting the hyphen in
    "Tail-Light" yields "taillight", which is not a substring of the gold
    "tail light" in either direction -- a correct answer scored wrong."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", str(text or "").lower())).strip()


# ==============================================================================
# TASK 4 -- MULTI-OP DECOMPOSITION
# ==============================================================================
# INPUT   ir: dict   target_count: int   expected_types: Sequence[str] | None
# OUTPUT  float in {0.0, 1.0}
#
# len(ir["ops"]) must EQUAL the target. Under-splitting and over-splitting both
# fail: half the case table are traps ("all four wheels" is ONE set op), so a
# model cannot inflate this column by splitting everything.
#
# Optional type-sequence check, WITH synonyms. Count alone over-credits a model
# that emits N arbitrary statements. Synonyms are correct here and wrong in task
# 1: this task asks whether the request was cut into the right pieces, so losing
# a correct decomposition to spin-vs-rotate would measure naming instead.

_OP_SYNONYMS: dict[str, frozenset[str]] = {
    "recolor": frozenset({"recolor", "recolour", "setmaterial", "material", "retexture", "paint", "setcolor"}),
    "spin": frozenset({"spin", "rotate"}),
    "rotate": frozenset({"rotate", "spin"}),
    "delete": frozenset({"delete", "remove"}),
    "move": frozenset({"move", "translate", "setposition"}),
    "scale": frozenset({"scale", "resize"}),
    "duplicate": frozenset({"duplicate", "clone", "copy"}),
}

# setMaterial counts as a recolor ONLY when it carries a colour. A full material
# swap with no colour is a different intent and must not pass as one.
_COLOUR_GATED = frozenset({"setmaterial", "material", "retexture"})


def op_type_matches(op: Mapping[str, Any], want: str) -> bool:
    got = str(op.get("op") or "").lower()
    want_lower = str(want or "").lower()
    if not got:
        return False
    if got == want_lower:
        return True
    if got not in _OP_SYNONYMS.get(want_lower, frozenset()):
        return False
    if want_lower == "recolor" and got in _COLOUR_GATED:
        return arg_bag(op).get("color") is not None
    return True


def score_multi_op(ir: Any, target_count: int,
                   expected_types: Sequence[str] | None = None) -> float:
    return score_multi_op_report(ir, target_count, expected_types)[0]


def score_multi_op_report(ir: Any, target_count: int,
                          expected_types: Sequence[str] | None = None) -> Report:
    ops = ops_of(ir)
    got = len(ops)

    if got != target_count:
        direction = "under" if got < target_count else "over"
        return FAIL, [f"{got} ops != target {target_count} ({direction}-split)"]

    for i, want in enumerate(expected_types or ()):
        if not op_type_matches(ops[i], want):
            return FAIL, [f'op{i} "{ops[i].get("op")}" != "{want}"']

    return PASS, [f"{got} op(s), types ok"]


# ==============================================================================
# TASK 5 -- SELECTOR-RESOLUTION  (RESOLVED-CORRECT-NODE)
# ==============================================================================
# INPUT   ir: dict   expected_nodes: Sequence[str] | Sequence[Sequence[str]]
#         scene: FixtureScene   merged_fail: bool
# OUTPUT  float in {0.0, 1.0}
#
# The ONLY scene-dependent task. '.wheel' is neither right nor wrong on its own;
# it is right or wrong RELATIVE TO A SCENE'S NODE SET (TERMINOLOGY.md S4).
#
# The check is SET EQUALITY, not containment. resolved == expected. Both halves
# are load-bearing:
#   missing -> the edit did not reach the parts asked for
#   extra   -> BLEED: it also changed parts nobody asked about
# Containment would pass '*' ("change everything") on every case, which is the
# single most important false pass in the whole matrix. Equality makes that
# structurally impossible.

def score_selector_resolution(ir: Any, expected_nodes: Sequence[Any],
                              scene: FixtureScene, *, merged_fail: bool = False) -> float:
    return score_selector_resolution_report(ir, expected_nodes, scene, merged_fail=merged_fail)[0]


def score_selector_resolution_report(ir: Any, expected_nodes: Sequence[Any],
                                     scene: FixtureScene, *, merged_fail: bool = False) -> Report:
    ops = ops_of(ir)
    resolved = resolve_all(ops, scene)

    # Graceful-fail case: on an unsplittable mesh the right answer is NOTHING.
    # Resolving to the merged node and proceeding recolours the whole object --
    # a pass here would be the co-location false-positive.
    if merged_fail:
        hit = [name for s in resolved for name in s]
        if hit:
            return FAIL, [f"resolved into a merged mesh: {sorted(set(hit))}"]
        return PASS, ["correctly resolved nothing"]

    if not ops:
        return FAIL, ["no ops in IR (nothing to resolve)"]

    expected_sets = _expected_node_sets(expected_nodes)
    if len(resolved) < len(expected_sets):
        return FAIL, [f"{len(resolved)} selector(s) for {len(expected_sets)} expected target set(s)"]

    reasons: list[str] = []
    for i, want in enumerate(expected_sets):
        got = resolved[i]
        missing = sorted(want - got)
        extra = sorted(got - want)
        if missing:
            reasons.append(f"op{i}: missed {', '.join(missing)}")
        if extra:
            reasons.append(f"op{i}: also changed {', '.join(extra)} (bleed)")

    return (FAIL, reasons) if reasons else (PASS, ["right nodes, nothing extra"])


def _expected_node_sets(expected: Sequence[Any]) -> list[frozenset[str]]:
    """Accept ['Object_20', ...] (one op) or [['Object_20'], ['Object_07']] (N ops)."""
    if not expected:
        return [frozenset()]
    if all(isinstance(item, str) for item in expected):
        return [frozenset(expected)]
    return [frozenset(group or ()) for group in expected]


# ==============================================================================
# AGGREGATE -- one case, five independent columns
# ==============================================================================
# Never average these. Parse validity and task accuracy are orthogonal
# constructs, and a blended "accuracy" hides the cliff (SCORING_POLICY S1).

def score_case(ir: Any, expect: Mapping[str, Any], scene: FixtureScene) -> dict[str, float]:
    merged_fail = bool(expect.get("mergedFail"))
    expected_ops = expect.get("ops")
    types = [o.get("opType") for o in expected_ops] if expected_ops else (
        [expect["opType"]] if expect.get("opType") else None)
    targets = ([o.get("targetNodes", []) for o in expected_ops] if expected_ops
               else expect.get("targetNodes", []))
    count = expect.get("opCount", len(expected_ops) if expected_ops else 1)

    return {
        "op-selection": PASS if merged_fail else score_op_selection(ir, types or []),
        "selector-resolution": score_selector_resolution(ir, targets, scene, merged_fail=merged_fail),
        "arg-extraction": PASS if merged_fail else score_arg_extraction(ir, expect.get("args")),
        "multi-op": PASS if merged_fail else score_multi_op(ir, count, types),
    }
