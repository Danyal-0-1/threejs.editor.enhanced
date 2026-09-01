#!/usr/bin/env python3
"""
coverage.py  —  conformance CI for 3dom-grammar/1.1.0

Run:  python3 conformance/coverage.py
Exit code 0 iff every acceptance gate below passes; non-zero otherwise.

Gates (each maps to an acceptance criterion in the task):
  G1  every positive item parses to EXACTLY ONE derivation (zero ambiguity)   [D3]
  G2  positive corpus achieves 100% PRODUCTION COVERAGE of the W3C grammar     [A2]
  G3  every negative item is REJECTED (parse-count == 0)                       [A2]
  G4  every vacuous item PARSES and yields ZERO operations                     [D5]
  G5  D1/L2 differential: $S('.car .wheel') and $S('.car.wheel') parse to
      DIFFERENT structures                                                     [D1]
  G6  language equivalence (operational): the Earley engine and the DFA agree
      (accept/reject) on ALL items in ALL three corpora                        [ISO==W3C]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refgrammar as R

HERE = os.path.dirname(os.path.abspath(__file__))


def read_programs(path):
    """Positive/vacuous reader: accumulate non-comment lines, flush each time the
    buffer parses (programs may span multiple physical lines)."""
    items, buf = [], ""
    for raw in open(os.path.join(HERE, path)):
        s = raw.strip()
        if not buf and (not s or s.startswith("#")):
            continue
        if s.startswith("#"):
            continue
        buf += (("\n" if buf else "") + raw.rstrip("\n"))
        if R.num_parses(buf) >= 1:
            items.append(buf)
            buf = ""
    if buf.strip():
        items.append(buf)   # keep a trailing non-parsing block so G1 flags it
    return items


def read_lines(path):
    """Negative reader: one program per non-comment line (single-line by contract)."""
    out = []
    for raw in open(os.path.join(HERE, path)):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        out.append(raw.rstrip("\n"))
    return out


def verb_count(src):
    return sum(1 for t in R.lex(src) if t[0] == "VERB")


def main():
    fails = []
    print("3DOM conformance — %s" % R.GRAMMAR_VERSION)
    print("=" * 60)

    positives = read_programs("positive.txt")
    negatives = read_lines("negative.txt")
    vacuous = read_programs("vacuous.txt")
    print("corpus sizes: positive=%d  negative=%d  vacuous=%d"
          % (len(positives), len(negatives), len(vacuous)))

    # G1 — unambiguous parse of every positive
    amb = [(p, R.num_parses(p)) for p in positives if R.num_parses(p) != 1]
    if amb:
        fails.append("G1: %d positive item(s) not uniquely parsing" % len(amb))
        for p, n in amb[:8]:
            print("  G1 FAIL parses=%d: %r" % (n, p[:70]))
    else:
        print("G1 OK  — all %d positives parse to exactly one derivation" % len(positives))

    # G2 — 100% production coverage
    covered = set()
    for p in positives:
        if R.num_parses(p) == 1:
            covered |= R.features_with_verbs(p)
    obligations = R.all_features()
    missing = obligations - covered
    if missing:
        fails.append("G2: %d uncovered production branch(es)" % len(missing))
        for m in sorted(missing):
            print("  G2 MISSING:", m)
    else:
        print("G2 OK  — production coverage = 100%% (%d/%d branches)"
              % (len(covered & obligations), len(obligations)))

    # G3 — every negative rejects
    accepted = [s for s in negatives if R.num_parses(s) != 0]
    if accepted:
        fails.append("G3: %d negative item(s) accepted" % len(accepted))
        for s in accepted[:8]:
            print("  G3 FAIL accepted: %r" % s)
    else:
        print("G3 OK  — all %d negatives rejected" % len(negatives))

    # G4 — vacuous parse + zero operations
    vbad = []
    for s in vacuous:
        if R.num_parses(s) != 1 or verb_count(s) != 0:
            vbad.append((s, R.num_parses(s), verb_count(s)))
    if vbad:
        fails.append("G4: %d vacuous item(s) invalid" % len(vbad))
        for s, n, vc in vbad[:8]:
            print("  G4 FAIL parses=%d ops=%d: %r" % (n, vc, s[:60]))
    else:
        print("G4 OK  — all %d vacuous items parse with zero operations" % len(vacuous))

    # G5 — D1/L2 differential
    a = "(function(){ $S('.car .wheel').delete(); })();"
    b = "(function(){ $S('.car.wheel').delete(); })();"
    fa, _ = R.derive(R.lex(a))
    fb, _ = R.derive(R.lex(b))
    desc_used = ("combinator", 0) in fa      # descendant combinator present in (a)
    and_used = ("matchers", 1) in fb         # multi-matcher AND present in (b)
    if not (desc_used and and_used and fa != fb):
        fails.append("G5: L2 differential not enforced")
        print("  G5 FAIL: desc=%s and=%s differ=%s" % (desc_used, and_used, fa != fb))
    else:
        print("G5 OK  — '.car .wheel' (descendant) != '.car.wheel' (compound AND)")

    # G6 — Earley/DFA agreement over ALL corpora (operational language-equivalence)
    disagree = []
    for tag, items in (("pos", positives), ("neg", negatives), ("vac", vacuous)):
        for s in items:
            earley = R.num_parses(s) >= 1
            dfa = R.dfa_accepts(s)
            if earley != dfa:
                disagree.append((tag, s, earley, dfa))
    if disagree:
        fails.append("G6: %d Earley/DFA disagreement(s)" % len(disagree))
        for tag, s, e, d in disagree[:8]:
            print("  G6 FAIL [%s] earley=%s dfa=%s: %r" % (tag, e, d, s[:50]))
    else:
        print("G6 OK  — Earley and DFA agree on all %d corpus items (same language)"
              % (len(positives) + len(negatives) + len(vacuous)))

    print("=" * 60)
    if fails:
        print("RESULT: FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("RESULT: PASS — all gates green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
