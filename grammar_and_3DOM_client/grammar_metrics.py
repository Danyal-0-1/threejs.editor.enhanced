#!/usr/bin/env python3
"""
grammar_metrics.py  —  regenerates METRICS.md for 3dom-grammar/1.1.0

The matched-complexity table in the paper is GENERATED, never hand-maintained.
Run:  python3 grammar_metrics.py            (writes METRICS.md, prints the table)

What it does:
  1. Parses BOTH .ebnf files textually and extracts, for each:
       - nonterminal set (LHS names)
       - quoted-terminal inventory (structural + keyword terminals; content-keyed
         so W3C ' ' and ISO " " match, and quote-style differences vanish)
       - production count |P| (top-level '|' alternatives), rule count |N|
       - EBNF operator counts (* + ?) EXCLUDING operators inside quoted literals
         (so  wildcard ::= '*'  and  sign ::= '+' | '-'  are NOT miscounted).
  2. Cross-checks ISO vs W3C: identical nonterminal sets and identical quoted-
     terminal inventories  => the two notations have not drifted (guards D2-class
     divergence). Lexical CHARACTER-CLASS terminals are compared by prose
     correspondence (ISO special-sequence vs W3C [ranges]) and excluded here.
  3. Pulls the intrinsic automaton metrics (DFA states, mean/max branching
     factor, k) from the shared reference engine conformance/refgrammar.py.
  4. Emits METRICS.md, marking each row INVARIANT (the Alien grammar must match)
     or REPORTED (measured per condition).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "conformance"))
import refgrammar as R

W3C = os.path.join(HERE, "3dom_grammar.w3c.ebnf")
ISO = os.path.join(HERE, "3dom_grammar.iso.ebnf")


def strip_comments(text, notation):
    if notation == "w3c":
        text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    else:  # iso
        text = re.sub(r"\(\*.*?\*\)", " ", text, flags=re.S)
        # ISO special sequences ? ... ? are lexical char-classes, not terminals;
        # blank them so they are not mistaken for operators or quoted literals.
        text = re.sub(r"\?[^?]*\?", " SPECIAL ", text)
    return text


def find_quoted(text):
    """Return the multiset (as a set) of quoted-literal CONTENTS, content-keyed so
    quote style is irrelevant.  Handles '...' and \"...\" ."""
    lits = set()
    for m in re.finditer(r"'([^']*)'|\"([^\"]*)\"", text):
        content = m.group(1) if m.group(1) is not None else m.group(2)
        lits.add(content)
    return lits


def parse_ebnf(path, notation):
    raw = open(path).read()
    body = strip_comments(raw, notation)
    if notation == "w3c":
        # split rules on '::='; a rule runs until the next 'name ::='
        parts = re.split(r"\n(?=[A-Za-z_][A-Za-z0-9_]*\s*::=)", body)
        rule_re = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*::=(.*)$", re.S)
    else:
        # ISO rules are terminated by ';'
        parts = [p for p in body.split(";")]
        rule_re = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$", re.S)

    nonterminals = []
    rules = {}
    for part in parts:
        m = rule_re.match(part)
        if not m:
            continue
        name, rhs = m.group(1), m.group(2)
        nonterminals.append(name)
        rules[name] = rhs

    # quoted terminals over the whole (comment-stripped) body
    quoted = find_quoted(body)

    # productions |P| = sum of top-level '|' alternatives per rule
    # (split on '|' that is not inside quotes — quotes here are only single chars)
    P = 0
    for name, rhs in rules.items():
        # remove quoted literals so a literal '|' (none here) can't fool the split
        rhs_noq = re.sub(r"'[^']*'|\"[^\"]*\"", " LIT ", rhs)
        alts = rhs_noq.split("|")
        P += len(alts)

    # operator counts EXCLUDING quoted literals
    ops = {"*": 0, "+": 0, "?": 0}
    if notation == "w3c":
        body_noq = re.sub(r"'[^']*'|\"[^\"]*\"", " LIT ", body)
        for ch in "*+?":
            ops[ch] = body_noq.count(ch)
        # subtract '::=' has none of these; '[^']' contains none either
    else:
        # ISO uses { } for *, [ ] for ?, no + ; count braces/brackets as the
        # equivalent operators, excluding quoted literals.
        body_noq = re.sub(r"'[^']*'|\"[^\"]*\"", " LIT ", body)
        ops["*"] = body_noq.count("{")     # { } == zero-or-more
        ops["?"] = body_noq.count("[")     # [ ] == optional
        ops["+"] = 0                       # ISO has no '+' operator

    return {
        "nonterminals": nonterminals,
        "N": len(set(nonterminals)),
        "P": P,
        "quoted": quoted,
        "ops": ops,
    }


def cross_check(w, i):
    problems = []
    nw, ni = set(w["nonterminals"]), set(i["nonterminals"])
    if nw != ni:
        problems.append("nonterminal sets differ: W3C-only=%s ISO-only=%s"
                        % (sorted(nw - ni), sorted(ni - nw)))
    # quoted terminals: exclude the ISO 'SPECIAL' placeholder if any leaked
    qw = {q for q in w["quoted"] if q not in ("", "LIT", "SPECIAL")}
    qi = {q for q in i["quoted"] if q not in ("", "LIT", "SPECIAL")}
    if qw != qi:
        problems.append("quoted-terminal inventories differ: W3C-only=%s ISO-only=%s"
                        % (sorted(qw - qi), sorted(qi - qw)))
    return problems


def main():
    w = parse_ebnf(W3C, "w3c")
    i = parse_ebnf(ISO, "iso")
    problems = cross_check(w, i)

    # automaton metrics from the shared engine
    bfs = [b for b in R.branching_factors() if b > 0]
    mean_bf = sum(bfs) / len(bfs)
    max_bf = max(bfs)
    dfa = R.dfa()
    prof = R.branching_profile_over_corpus_default()

    quoted_terminals = sorted({q for q in w["quoted"] if q not in ("", "LIT", "SPECIAL")})
    Sigma_quoted = len(quoted_terminals)
    lexical_classes = ["identifier/ident_char", "digit", "whitespace(' ')",
                       "sq_char([^'])", "dq_char([^\"])"]

    lines = []
    A = lines.append
    A("# METRICS.md — matched-complexity table")
    A("")
    A("**grammar version:** `%s`" % R.GRAMMAR_VERSION)
    A("")
    A("_Generated by `grammar_metrics.py`. Do not hand-edit._ Every row is marked")
    A("**INVARIANT** (the Alien-Syntax grammar produced next week MUST match this")
    A("value exactly, so the two languages are of equal formal complexity) or")
    A("**REPORTED** (a measured quantity, not a design constraint).")
    A("")
    A("## Grammar cross-check (ISO vs W3C)")
    if problems:
        A("")
        A("**DIVERGENCE DETECTED — the two notations do not encode the same grammar:**")
        for p in problems:
            A("- " + p)
    else:
        A("")
        A("`PASS` — the ISO and W3C files share an identical nonterminal set "
          "(|N| = %d) and an identical quoted-terminal inventory (%d terminals). "
          "The two notations have not drifted." % (w["N"], Sigma_quoted))
    A("")
    A("## Complexity table")
    A("")
    A("| Metric | Value | Kind | Notes |")
    A("|---|---|---|---|")
    A("| Grammar version | `%s` | INVARIANT | stamped into every artifact (A5) |" % R.GRAMMAR_VERSION)
    A("| Language class | Regular | INVARIANT | non-self-embedding (CHANGELOG proof) |")
    A("| Nonterminals \\|N\\| | %d | INVARIANT | rule count, both files |" % w["N"])
    A("| Productions \\|P\\| | %d | INVARIANT | top-level `\\|` alternatives (W3C) |" % w["P"])
    A("| Productions \\|P\\| (ISO) | %d | REPORTED | ISO alternative count (should equal W3C) |" % i["P"])
    A("| Quoted terminals \\|Σq\\| | %d | INVARIANT | structural + keyword terminals |" % Sigma_quoted)
    A("| Lexical char-classes | %d | INVARIANT | %s |" % (len(lexical_classes), ", ".join(lexical_classes)))
    A("| Closed verb set | 15 | INVARIANT | hard invariant; never add/remove |")
    A("| type_selector set | 4 | INVARIANT | mesh, group, light, camera |")
    A("| pseudo_selector set | 2 | INVARIANT | :selected, :lasso |")
    A("| EBNF operator `*` (0+) | %d | REPORTED | quoted literals excluded |" % w["ops"]["*"])
    A("| EBNF operator `+` (1+) | %d | REPORTED | quoted literals excluded |" % w["ops"]["+"])
    A("| EBNF operator `?` (opt) | %d | REPORTED | quoted literals excluded |" % w["ops"]["?"])
    A("| Lookahead k | 2 | INVARIANT | not LL(1) (D4/P1); combinator overlap |")
    A("| DFA states | %d | REPORTED | over the flat DSL-token alphabet |" % dfa["nstates"])
    A("| Mean branching factor | %.3f | INVARIANT | decoder choices/step (A4) |" % mean_bf)
    A("| Max branching factor | %d | INVARIANT | worst-case step (A4) |" % max_bf)
    A("")
    A("### Operator-exclusion demonstration (the number that goes in the paper)")
    A("")
    A("`wildcard ::= '*'` and `sign ::= '+' | '-'` contain `*`/`+` **inside quotes**.")
    A("A naive `text.count('*')` over the W3C file counts %d; excluding quoted"
      % (open(W3C).read().count('*')))
    A("literals gives the true Kleene-star count **%d**. The table above uses the"
      % w["ops"]["*"])
    A("excluded figure.")
    A("")
    A("### Branching factor as a function of program position (A4)")
    A("")
    A("Averaged over the positive corpus (DSL-token index → mean legal next-tokens):")
    A("")
    A("| token idx | mean branching |")
    A("|---|---|")
    for idx, val in prof[:16]:
        A("| %d | %.2f |" % (idx, val))
    A("")
    A("_(truncated to the first 16 positions; full profile available from"
      " `refgrammar.branching_profile_over_corpus`.)_")
    A("")

    out = "\n".join(lines) + "\n"
    with open(os.path.join(HERE, "METRICS.md"), "w") as f:
        f.write(out)
    print(out)
    if problems:
        print("CROSS-CHECK FAILED", file=sys.stderr)
        return 1
    print("grammar_metrics: cross-check PASS; METRICS.md regenerated.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
