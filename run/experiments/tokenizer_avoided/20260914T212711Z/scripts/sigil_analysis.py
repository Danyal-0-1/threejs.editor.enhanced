"""sigil_analysis.py — quantify 3DOM sigil reversion inside selector strings.

The most interpretable failure in this run: a model writes an alien program
whose STRUCTURE and VERBS are correct, then reverts to 3DOM's `.` class sigil
inside the quoted selector. This measures how often that happens, per model,
language and condition -- including in the SCAFFOLDED condition, where the
prompt literally displays the correct sigil next to the tag.

Counted only on outputs that used the target language's selector-entry
spelling, so it measures reversion WITHIN an otherwise on-language answer, not
a wholesale refusal to use the language.
"""
from __future__ import annotations

import collections, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)

import checkpoint as C
import prompts as P

def selector_bodies(code: str, entry: str) -> list[str]:
    """The quoted string that immediately follows each selector-entry token.

    Scoped deliberately. A blanket scan of every quoted literal would also pick
    up ARGUMENTS such as recolor('#000000'), and filtering those out by a hex
    pattern would wrongly discard legitimate alpha selectors like '#bed' and
    '#cab', whose letters happen to be hex digits. Reading only the selector
    position avoids both errors.
    """
    out: list[str] = []
    i = 0
    while True:
        j = code.find(entry, i)
        if j < 0:
            return out
        k = j + len(entry)
        while k < len(code) and code[k] in " \t(":
            k += 1
        if k < len(code) and code[k] in "'\"":
            q = code[k]
            end = code.find(q, k + 1)
            if end > 0:
                out.append(code[k + 1:end])
        i = j + len(entry)


def main() -> int:
    out = {"rows": [], "definition": (
        "A generation is counted as SIGIL-REVERTED when its extracted code uses "
        "this language's selector-entry spelling (so it is an on-language answer) "
        "but the quoted selector body contains 3DOM's class sigil '.' while this "
        "language's class sigil is something else. Denominator: on-language "
        "generations with at least one quoted selector.")}
    for path in sorted(glob.glob(os.path.join(RUN, "raw", "*", "lane_b", "gen.jsonl"))):
        for r in C.read_rows(path):
            if r.get("scoring_family") != "generation":
                continue
            lang = r["language"]
            phi = P.phi_for(lang)
            cls = phi.spelling("T_CLASS_SIGIL")
            entry = phi.spelling("T_SELECTOR_ENTRY")
            code = r.get("extracted_code") or ""
            if entry not in code:
                continue
            bodies = [b for b in selector_bodies(code, entry) if b]
            if not bodies:
                continue
            used_dom = any("." in b for b in bodies)
            used_own = any(cls in b for b in bodies) if cls != "." else False
            out["rows"].append({
                "model": r["model"], "language": lang, "condition": r["condition"],
                "case_id": r["case_id"], "own_class_sigil": cls,
                "selector_bodies": bodies,
                "reverted_to_3dom_sigil": int(cls != "." and used_dom),
                "used_own_sigil": int(used_own),
                "parse_valid": r.get("parse_valid", 0),
                "outcome": r.get("outcome")})

    agg = collections.defaultdict(lambda: {"n": 0, "reverted": 0, "own": 0})
    for r in out["rows"]:
        k = (r["model"], r["language"], r["condition"])
        agg[k]["n"] += 1
        agg[k]["reverted"] += r["reverted_to_3dom_sigil"]
        agg[k]["own"] += r["used_own_sigil"]
    out["summary"] = [
        {"model": m, "language": l, "condition": c, "n_on_language": v["n"],
         "n_reverted_to_3dom_sigil": v["reverted"],
         "reversion_rate": v["reverted"] / v["n"] if v["n"] else None,
         "n_used_own_sigil": v["own"]}
        for (m, l, c), v in sorted(agg.items())]

    dest = os.path.join(RUN, "metrics", "sigil_reversion.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    print(f"{'model':<34}{'lang':<9}{'cond':<12}{'n':>4}{'reverted':>10}{'rate':>8}")
    for s in out["summary"]:
        if s["language"] == "identity":
            continue
        print(f"{s['model'].replace('Qwen/Qwen2.5-Coder-',''):<34}{s['language']:<9}"
              f"{s['condition']:<12}{s['n_on_language']:>4}"
              f"{s['n_reverted_to_3dom_sigil']:>10}"
              f"{(100*s['reversion_rate']):>7.1f}%")
    print(f"\nwrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
