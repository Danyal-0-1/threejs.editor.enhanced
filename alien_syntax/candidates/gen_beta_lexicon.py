"""gen_beta_lexicon.py — the constrained phonotactic generator behind CANDIDATE β.

β is the "pseudo-lexicon" arm: pronounceable ASCII non-words, novel as WHOLE
tokens but assembled from in-vocabulary subword material, so tokenizer fertility
can be tuned to match 3DOM instead of blowing up (the binding constraint in the
design target).

Two rules do the fertility matching, and both are stated as rules rather than
hand-tuned per word:

  R1  CHARACTER-LENGTH MATCH.  Every β spelling has exactly the same character
      count as the 3DOM spelling it replaces. Character length is the strongest
      cheap predictor of BPE token count; the real number is measured by
      measure/fertility.py, which is the arbiter.

  R2  MORPHOLOGICAL-SHAPE MATCH.  A 3DOM camelCase compound (`setMaterial`,
      `castShadow`, `receiveShadow`, `setOpacity`, `setVisible`) is replaced by a
      camelCase compound with the SAME split point. BPE tokenizers segment at
      case boundaries; dropping camelCase would change fertility for reasons
      that have nothing to do with lexical familiarity.

      R2 deliberately LEAVES a familiarity signal in β — the "this is a
      JS-style fluent API" convention. That is a conscious trade: the design
      target subordinates surface strangeness to matched fertility, and the
      convention is a property of the OPERATOR SKELETON (frozen by I3) rather
      than of the lexicon. Recorded here so it is a stated assumption, not an
      accident.

Phonotactics: syllable = onset + nucleus + optional coda, drawn from inventories
chosen for (i) pronounceability and (ii) high frequency as English subword
pieces. Rejection filters remove real words, cross-candidate collisions, and
proper-prefix pairs (which would break maximal munch — collisions.py check (a)).

Deterministic: the RNG is seeded per terminal ID, so the output is a function of
terminals.json alone and re-running reproduces phi_beta.json byte-for-byte.
"""

from __future__ import annotations

import json
import os
import random
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from phi import GRAMMAR_VERSION, load_terminals  # noqa: E402

ONSETS = ("b", "d", "f", "g", "k", "l", "m", "n", "p", "r", "s", "t", "v", "z",
          "br", "dr", "gr", "kr", "pr", "tr", "bl", "fl", "gl", "kl", "pl", "sl")
NUCLEI = ("a", "e", "i", "o", "u")
CODAS = ("", "l", "m", "n", "r", "s", "t")

# Words the generator must never produce: the 3DOM lexicon itself, every
# identifier and string value that appears in the Phase 1 corpora (an alien verb
# colliding with a corpus identifier would create a lexical hazard the collision
# checker exists to forbid), and a short list of common English words that the
# syllable inventory can otherwise stumble into.
BLACKLIST = frozenset("""
recolor scale move rotate delete spin duplicate setmaterial setopacity
setvisible wireframe metalness roughness castshadow receiveshadow
mesh group light camera selected lasso function
wheel front left right rear body window ground fan car truck cab hub rim axle
chassis robot arm tree leaf door metallic glass dump bed dumpbed
false true
tail sail rail nail mail fail bail male sale tale pale dale
ran run rat rot rate note nose rose lose lore more mere mire fire
mister listen molten silent talent parent moment linen linter mental
salad solar polar molar dollar collar
""".split())


SIMPLE_ONSETS = tuple(o for o in ONSETS if len(o) == 1)


def syllable(rng: random.Random, *, initial: bool) -> str:
    """onset + nucleus + optional coda. Consonant CLUSTERS only word-initially,
    which is what keeps multi-syllable output pronounceable."""
    onset = rng.choice(ONSETS if initial else SIMPLE_ONSETS)
    return onset + rng.choice(NUCLEI) + rng.choice(CODAS)


def word_of_length(rng: random.Random, length: int, reject) -> str:
    """A pronounceable non-word of EXACTLY `length` characters (R1)."""
    for _ in range(200_000):
        parts: list[str] = []
        total = 0
        while total < length:
            parts.append(syllable(rng, initial=not parts))
            total = sum(len(p) for p in parts)
        word = "".join(parts)
        if len(word) != length:
            continue
        if any(a == b for a, b in zip(word, word[1:])):
            continue                                    # no doubled letters
        if word in BLACKLIST:
            continue
        if not any(c in NUCLEI for c in word):
            continue
        if reject(word):
            continue
        return word
    raise RuntimeError(f"phonotactic generator exhausted for length {length}")


def camel_split(spelling: str) -> tuple[int, int] | None:
    """(head_len, tail_len) if `spelling` is a camelCase compound, else None."""
    for i, c in enumerate(spelling):
        if i and c.isupper():
            return i, len(spelling) - i
    return None


def generate(seed_salt: str = "3dom-beta-v1") -> dict[str, str]:
    table = load_terminals()
    chosen: dict[str, str] = {}
    lowered: set[str] = set()

    def reject(word: str) -> bool:
        w = word.lower()
        if w in lowered:
            return True
        # proper-prefix pairs break maximal munch (collisions.py check (a))
        return any(w.startswith(o) or o.startswith(w) for o in lowered)

    # Deterministic order: terminals.json order, word-class terminals only.
    for term in table.terminals:
        if not term.substitutable or not term.is_word_class:
            continue
        rng = random.Random(f"{seed_salt}:{term.id}")
        split = camel_split(term.spelling)
        if split is None:
            word = word_of_length(rng, len(term.spelling), reject)
        else:
            head_len, tail_len = split
            head = word_of_length(rng, head_len, reject)
            lowered.add(head)                       # keep the head distinct too
            tail = word_of_length(rng, tail_len, reject)
            lowered.discard(head)
            word = head + tail.capitalize()
        chosen[term.id] = word
        lowered.add(word.lower())
    return chosen


# The sigil layer. Punctuation has no phonotactics, so these are chosen by
# constraint rather than generated: single ASCII characters that are (i) outside
# the identifier charset, (ii) outside the reserved lexer characters (quotes,
# structural delimiters, numeric signs, digits, layout), and (iii) not the 3DOM
# spelling they replace. T_CHAIN_OP and T_CLASS_SIGIL share one character (I7).
# A fourth constraint, learned the hard way from tests/test_invariants.py: the
# spelling must not collide with the METASYNTAX of the notations the grammar is
# published in. `?` delimits an ISO/IEC 14977 SPECIAL SEQUENCE and `|` is the
# alternation operator in both ISO and W3C EBNF; either one silently corrupts
# the generated normative appendix (the ISO reader swallowed nine productions
# before |N| parity caught it). The safe ASCII residue, after removing the
# identifier charset, the characters the two-level lexer already claims, the
# EBNF metasyntax, and 3DOM's own CSS-flavoured sigils, is: ~ ! @ % ^ &.
SIGILS = {
    "T_SELECTOR_ENTRY": "&Q",   # sigil+capital, same shape and length as "$S"
    "T_CHAIN_OP":       "~",    # ─┐ one spelling, two roles: the "." overload
    "T_CLASS_SIGIL":    "~",    # ─┘ preserved (I7)
    "T_ID_SIGIL":       "%",
    "T_PSEUDO_SIGIL":   "@",
    "T_CHILD":          "^",
    "T_WILDCARD":       "!",
}


def build_phi_map() -> dict:
    table = load_terminals()
    words = generate()
    by_id = table.by_id
    mapping: dict[str, dict[str, str]] = {}
    for tid in table.substitutable_ids:
        to = words.get(tid) or SIGILS.get(tid)
        if to is None:
            raise RuntimeError(f"no β spelling produced for {tid}")
        mapping[tid] = {"from": by_id[tid].spelling, "to": to}
    return {
        "phi_id": "beta",
        "targets_grammar": GRAMMAR_VERSION,
        "generated": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "construct": "ABSENCE — novel whole tokens, matched fertility",
        "map": mapping,
        "overload_groups": [["T_CHAIN_OP", "T_CLASS_SIGIL"]],
        "frozen": list(table.non_substitutable_ids),
        "notes": (
            "Pseudo-lexicon. Word-class spellings come from the constrained "
            "phonotactic generator in candidates/gen_beta_lexicon.py under rules "
            "R1 (exact character-length match) and R2 (camelCase shape and split "
            "point preserved), both of which exist to hold tokenizer fertility "
            "near 1.00 — the binding constraint. Sigils are single ASCII "
            "characters outside the identifier charset. T_CHAIN_OP and "
            "T_CLASS_SIGIL share '~' so the '.' overload survives (I7); T_WS is "
            "untouched so the descendant combinator is still whitespace (I9); "
            "the quote terminals are untouched so delimiters stay symmetric (I8)."
        ),
    }


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phi_beta.json")
    blob = build_phi_map()
    if "--stamp" not in sys.argv:
        # keep the file byte-stable across re-runs unless a stamp is requested
        if os.path.exists(out):
            with open(out, encoding="utf-8") as fh:
                blob["generated"] = json.load(fh).get("generated", blob["generated"])
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(blob, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {out}")
    for tid, e in blob["map"].items():
        print(f"  {tid:<24} {e['from']:<15} -> {e['to']}")
