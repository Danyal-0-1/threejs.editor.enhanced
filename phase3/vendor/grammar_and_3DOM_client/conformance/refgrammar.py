"""
refgrammar.py  —  reference engine for 3dom-grammar/1.1.0

Single machine-readable encoding of the 3DOM token-level language, shared by
coverage.py and grammar_metrics.py. It is the executable twin of the normative
.ebnf files; conformance/coverage.py cross-checks that this engine and the corpora
agree, and asserts language-equivalence operationally over the whole corpus.

It provides:
  * a two-mode lexer (L1 outside quotes: layout elided; L2 inside a selector
    string: whitespace significant) that FLATTENS a program into one token stream,
  * a non-left-recursive CFG (the flattened grammar) with an exact parse COUNTER
    (ambiguity detector) and a unique-derivation extractor (coverage instrument),
  * a Thompson NFA -> DFA built from the SAME grammar, used for recognition,
    longest-valid-prefix (LVP) and branching-factor metrics (A3/A4).

The language is regular (non-self-embedding): every metric below is well-defined.

GRAMMAR_VERSION is stamped into every downstream artifact.
"""

GRAMMAR_VERSION = "3dom-grammar/1.1.0"

# The closed verb set — EXACTLY 15. Do not add/remove/rename (hard invariant).
VERBS = [
    "recolor", "scale", "move", "rotate", "delete", "spin", "duplicate",
    "setMaterial", "setOpacity", "setVisible", "wireframe",
    "metalness", "roughness", "castShadow", "receiveShadow",
]
assert len(VERBS) == 15 and len(set(VERBS)) == 15, "verb count invariant broken"

TYPES = ["mesh", "group", "light", "camera"]      # type_selector set (frozen)
PSEUDO = ["selected", "lasso"]                     # pseudo_selector set (frozen)


# ─────────────────────────────────────────────────────────────────────────────
# Lexer  (produces the FLAT token stream; selector string expanded, arg strings
# atomic).  Token = (type, value, char_pos).  Raises LexError on unlexable input.
# ─────────────────────────────────────────────────────────────────────────────

class LexError(Exception):
    pass


IDENT_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
_VERBSET = set(VERBS)
_TYPESET = set(TYPES)
_PSEUDOSET = set(PSEUDO)


def _lex_selector_body(body, base):
    """Lex the INSIDE of a selector string (L2: whitespace significant)."""
    toks = []
    i = 0
    prev = None  # previous emitted inner token type (context for ident classing)
    n = len(body)
    while i < n:
        c = body[i]
        if c == " ":
            j = i
            while j < n and body[j] == " ":
                j += 1
            toks.append(("WS", " ", base + i))
            prev = "WS"
            i = j
        elif c in "\t\r\n":
            # Only the plain space is the descendant combinator; other layout is
            # not permitted inside a selector (keeps L2 unambiguous).
            raise LexError("illegal whitespace char inside selector at %d" % (base + i))
        elif c == "#":
            toks.append(("HASH", "#", base + i)); prev = "HASH"; i += 1
        elif c == ".":
            toks.append(("CSIG", ".", base + i)); prev = "CSIG"; i += 1
        elif c == ":":
            toks.append(("COLON", ":", base + i)); prev = "COLON"; i += 1
        elif c == ">":
            toks.append(("GT", ">", base + i)); prev = "GT"; i += 1
        elif c == "*":
            toks.append(("STAR", "*", base + i)); prev = "STAR"; i += 1
        elif c in IDENT_CHARS:
            j = i
            while j < n and body[j] in IDENT_CHARS:
                j += 1
            run = body[i:j]
            if prev in ("HASH", "CSIG"):
                tt = "IDENT"                 # name after a sigil is always a literal id
            elif run in _TYPESET:
                tt = "TYPE_" + run.upper()   # bare known type keyword
            elif run in _PSEUDOSET:
                tt = run.upper()             # bare 'selected' / 'lasso'
            else:
                tt = "IDENT"                 # bare unknown word -> grammar rejects it
            toks.append((tt, run, base + i)); prev = tt; i = j
        else:
            raise LexError("illegal char %r inside selector at %d" % (c, base + i))
    return toks


def lex(src):
    """Flat-lex a whole program. Layout elided outside quotes (L1)."""
    toks = []
    i = 0
    n = len(src)
    expect_selector_string = 0  # >0 right after `$S (` : the next string is a selector
    # track last two significant emitted token types for the $S ( STRING rule
    while i < n:
        c = src[i]
        if c in " \t\r\n":
            i += 1
            continue
        if c == "(":
            toks.append(("LP", "(", i)); i += 1
            continue
        if c == ")":
            toks.append(("RP", ")", i)); i += 1
            continue
        if c == "{":
            toks.append(("LB", "{", i)); i += 1
            continue
        if c == "}":
            toks.append(("RB", "}", i)); i += 1
            continue
        if c == ";":
            toks.append(("SEMI", ";", i)); i += 1
            continue
        if c == ",":
            toks.append(("COMMA", ",", i)); i += 1
            continue
        if c == ".":
            toks.append(("DOT", ".", i)); i += 1
            continue
        if c in "'\"":
            # A quoted string. Selector-position strings are expanded; argument
            # strings are atomic. Detect selector position: previous two tokens
            # are DOLLAR, LP.
            q = c
            j = i + 1
            while j < n and src[j] != q:
                if src[j] in "\r\n":
                    raise LexError("newline inside string at %d" % j)
                j += 1
            if j >= n:
                raise LexError("unterminated string starting at %d" % i)
            body = src[i + 1:j]
            is_selpos = (len(toks) >= 2 and toks[-1][0] == "LP" and toks[-2][0] == "DOLLAR")
            if is_selpos:
                toks.append(("QUOTE", q, i))
                toks.extend(_lex_selector_body(body, i + 1))
                toks.append(("QUOTE", q, j))
            else:
                toks.append(("STRING", body, i))
            i = j + 1
            continue
        if c in "+-0123456789":
            j = i
            if src[j] in "+-":
                j += 1
            d0 = j
            while j < n and src[j].isdigit():
                j += 1
            if j == d0:
                raise LexError("malformed number at %d" % i)
            if j < n and src[j] == ".":
                j += 1
                d1 = j
                while j < n and src[j].isdigit():
                    j += 1
                if j == d1:
                    raise LexError("malformed float at %d" % i)
            toks.append(("NUMBER", src[i:j], i)); i = j
            continue
        if c == "$":
            if src[i:i + 2] == "$S":
                toks.append(("DOLLAR", "$S", i)); i += 2
                continue
            raise LexError("stray '$' at %d" % i)
        if c.isalpha():
            j = i
            while j < n and (src[j].isalnum() or src[j] == "_"):
                j += 1
            w = src[i:j]
            if w == "function":
                toks.append(("FUNC", w, i))
            elif w in _VERBSET:
                toks.append(("VERB", w, i))
            else:
                # unknown bareword in the OUTER language (e.g. an unknown verb):
                # emit a token the grammar cannot consume so LVP fails exactly here.
                toks.append(("BADWORD", w, i))
            i = j
            continue
        raise LexError("illegal char %r at %d" % (c, i))
    return toks


# ─────────────────────────────────────────────────────────────────────────────
# The flattened CFG.  Rules are (lhs, [alternatives]); each alternative is a list
# of symbols.  Terminals are UPPERCASE token types; nonterminals are lowercase.
# Alternatives are indexed so we can report per-branch coverage that maps 1:1 to
# the W3C productions (see FEATURES).  No left recursion (top-down-safe).
# ε is the empty list [].
# ─────────────────────────────────────────────────────────────────────────────

def _matcher_alts():
    alts = [["HASH", "IDENT"], ["CSIG", "IDENT"]]
    alts += [["TYPE_" + t.upper()] for t in TYPES]     # mesh/group/light/camera
    return alts


GRAMMAR = {
    "program": [["iife"]],
    "iife": [["LP", "FUNC", "LP", "RP", "LB", "stmts", "RB", "RP", "LP", "RP", "SEMI"]],
    "stmts": [[], ["statement", "stmts"]],
    "statement": [["chain", "SEMI"]],
    "chain": [["selcall", "ops"]],
    "ops": [[], ["opcall", "ops"]],
    "selcall": [["DOLLAR", "LP", "QUOTE", "selector", "QUOTE", "RP"]],
    "opcall": [["DOT", "VERB", "LP", "optargs", "RP"]],
    "optargs": [[], ["arglist"]],
    "arglist": [["argument", "argtail"]],
    "argtail": [[], ["COMMA", "argument", "argtail"]],
    "argument": [["NUMBER"], ["STRING"]],
    "selector": [["pseudo"], ["complex"]],
    "pseudo": [["COLON", "SELECTED"], ["COLON", "LASSO"]],
    "complex": [["compound", "ctail"]],
    "ctail": [[], ["combinator", "compound", "ctail"]],
    # combinator = descendant | child ; child = WS? '>' WS?  (4 spacing branches)
    "combinator": [["desc_comb"], ["child_comb"]],
    "desc_comb": [["WS"]],
    "child_comb": [["WS", "GT", "WS"], ["WS", "GT"], ["GT", "WS"], ["GT"]],
    "compound": [["wildcard"], ["matchers"]],
    "wildcard": [["STAR"]],
    "matchers": [["matcher"], ["matcher", "matchers"]],
    "matcher": _matcher_alts(),
}

START = "program"
TERMINALS = set()
for _lhs, _alts in GRAMMAR.items():
    for _alt in _alts:
        for _s in _alt:
            if _s not in GRAMMAR:
                TERMINALS.add(_s)
# BADWORD is a lexer-only sentinel (never in any rule) -> guarantees rejection.


# ─────────────────────────────────────────────────────────────────────────────
# Exact parse counter (ambiguity detector) — memoized top-down over a
# non-left-recursive CFG. count(sym, i) -> {end: number_of_derivations}.
# ─────────────────────────────────────────────────────────────────────────────

def parse_counts(tokens):
    types = [t[0] for t in tokens]
    N = len(types)
    memo = {}

    def count(sym, i):
        key = (sym, i)
        if key in memo:
            return memo[key]
        memo[key] = {}          # guard (grammar is non-left-recursive, so safe)
        out = {}
        if sym not in GRAMMAR:  # terminal
            if i < N and types[i] == sym:
                out[i + 1] = 1
            memo[key] = out
            return out
        for alt in GRAMMAR[sym]:
            cur = {i: 1}
            for s in alt:
                nxt = {}
                for pos, c in cur.items():
                    for pos2, c2 in count(s, pos).items():
                        nxt[pos2] = nxt.get(pos2, 0) + c * c2
                cur = nxt
                if not cur:
                    break
            for pos, c in cur.items():
                out[pos] = out.get(pos, 0) + c
        memo[key] = out
        return out

    total = count(START, 0).get(N, 0)
    return total, memo


def num_parses(src):
    """Number of distinct derivations of src (0 = reject, 1 = unambiguous)."""
    try:
        tokens = lex(src)
    except LexError:
        return 0
    total, _ = parse_counts(tokens)
    return total


def accepts(src):
    return num_parses(src) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# Unique-derivation extractor (coverage instrument). Requires the input to be
# unambiguous (num_parses == 1). Returns the set of FEATURE ids exercised.
# ─────────────────────────────────────────────────────────────────────────────

def derive(tokens):
    types = [t[0] for t in tokens]
    N = len(types)
    _, memo = parse_counts(tokens)

    def reach(sym, i):
        if sym not in GRAMMAR:
            return {i + 1} if (i < N and types[i] == sym) else set()
        return set(memo.get((sym, i), {}).keys())

    used = set()  # (lhs, alt_index)

    def build(sym, i, j):
        """Build the unique derivation of sym over tokens[i:j]."""
        if sym not in GRAMMAR:
            assert i < N and types[i] == sym and j == i + 1
            return
        for ai, alt in enumerate(GRAMMAR[sym]):
            spans = _find_split(alt, i, j, reach)
            if spans is not None:
                used.add((sym, ai))
                for s, (a, b) in zip(alt, spans):
                    build(s, a, b)
                return
        raise AssertionError("no derivation for %s over [%d,%d)" % (sym, i, j))

    def _find_split(alt, i, j, reach):
        # find positions i=p0<=...<=pk=j with each symbol deriving its span
        if not alt:
            return [] if i == j else None
        results = [None]

        def rec(idx, pos, acc):
            if idx == len(alt):
                if pos == j:
                    results[0] = list(acc)
                    return True
                return False
            s = alt[idx]
            for nxt in sorted(reach(s, pos)):
                if nxt > j:
                    continue
                acc.append((pos, nxt))
                if rec(idx + 1, nxt, acc):
                    return True
                acc.pop()
            return False

        rec(0, i, [])
        return results[0]

    build(START, 0, N)
    return used, tokens


# Map (lhs, alt_index) -> stable FEATURE id that mirrors a W3C production branch.
def features_of(src):
    tokens = lex(src)
    total, _ = parse_counts(tokens)
    if total != 1:
        raise AssertionError("features_of requires an unambiguous parse (got %d)" % total)
    used, _ = derive(tokens)
    feats = set()
    for (lhs, ai) in used:
        feats.add(FEATURE_ID.get((lhs, ai), "%s#%d" % (lhs, ai)))
    return feats


# Human-readable feature ids for the coverage obligations. One per grammar
# alternative / optional-branch that the W3C grammar exposes.
FEATURE_ID = {
    ("program", 0): "program",
    ("iife", 0): "iife",
    ("stmts", 0): "stmts:empty",
    ("stmts", 1): "stmts:more",
    ("statement", 0): "statement",
    ("chain", 0): "chain",
    ("ops", 0): "ops:zero(terminate-chain)",
    ("ops", 1): "ops:more(chained-op)",
    ("selcall", 0): "selector_call",
    ("opcall", 0): "operation_call",
    ("optargs", 0): "operation_call:no-args",
    ("optargs", 1): "operation_call:with-args",
    ("arglist", 0): "argument_list",
    ("argtail", 0): "argument_list:one",
    ("argtail", 1): "argument_list:comma-more",
    ("argument", 0): "argument:number",
    ("argument", 1): "argument:string",
    ("selector", 0): "selector:pseudo",
    ("selector", 1): "selector:complex",
    ("pseudo", 0): "pseudo:selected",
    ("pseudo", 1): "pseudo:lasso",
    ("complex", 0): "complex_selector",
    ("ctail", 0): "complex:single-compound",
    ("ctail", 1): "complex:combined-compound",
    ("combinator", 0): "combinator:descendant",
    ("combinator", 1): "combinator:child",
    ("desc_comb", 0): "descendant_combinator",
    ("child_comb", 0): "child_combinator: WS>WS",
    ("child_comb", 1): "child_combinator: WS>",
    ("child_comb", 2): "child_combinator: >WS",
    ("child_comb", 3): "child_combinator: >",
    ("compound", 0): "compound:wildcard",
    ("compound", 1): "compound:matchers",
    ("wildcard", 0): "wildcard",
    ("matchers", 0): "compound:single-matcher",
    ("matchers", 1): "compound:multi-matcher(AND)",
    ("matcher", 0): "matcher:id",
    ("matcher", 1): "matcher:class",
    ("matcher", 2): "type_selector:mesh",
    ("matcher", 3): "type_selector:group",
    ("matcher", 4): "type_selector:light",
    ("matcher", 5): "type_selector:camera",
}

# Verb coverage is tracked separately (the grammar folds all 15 into one VERB
# terminal). Every verb spelling is its own obligation.
VERB_FEATURES = {("verb:" + v) for v in VERBS}


def all_features():
    base = set(FEATURE_ID.values())
    return base | VERB_FEATURES


def features_with_verbs(src):
    feats = features_of(src)
    for t in lex(src):
        if t[0] == "VERB":
            feats.add("verb:" + t[1])
    return feats


# ─────────────────────────────────────────────────────────────────────────────
# Thompson NFA -> DFA over the FLAT token alphabet, built from the SAME grammar
# by structural recursion. Used for recognition, LVP and branching factor.
# Because the language is regular (non-self-embedding) this terminates: we expand
# each nonterminal inline, and the only repetition is via *-rules which we detect
# and compile to NFA loops rather than infinite inline expansion.
# ─────────────────────────────────────────────────────────────────────────────

class _NFA:
    def __init__(self):
        self.states = 0
        self.trans = {}     # state -> list of (symbol_or_None, state)
        self.start = None
        self.accept = None

    def new(self):
        s = self.states
        self.states += 1
        self.trans[s] = []
        return s

    def edge(self, a, sym, b):
        self.trans[a].append((sym, b))


# The grammar's recursion is exactly these right-recursive "list" rules; we
# compile them as loops instead of inlining (keeps the automaton finite).
_LIST_RULES = {
    "stmts": ("statement",),        # stmts -> ε | statement stmts
    "ops": ("opcall",),             # ops   -> ε | opcall ops
    "argtail": ("COMMA", "argument"),   # argtail -> ε | COMMA argument argtail
    "ctail": ("combinator", "compound"),  # ctail -> ε | combinator compound ctail
    "matchers_more": None,          # handled specially below
}


def build_nfa():
    nfa = _NFA()

    def frag(sym):
        """Return (start, accept) NFA fragment for a symbol/nonterminal."""
        if sym not in GRAMMAR:
            a = nfa.new(); b = nfa.new(); nfa.edge(a, sym, b)
            return a, b
        # special list rules -> loops
        if sym == "stmts":
            a = nfa.new(); b = nfa.new()
            nfa.edge(a, None, b)                      # ε (zero statements)
            s0, s1 = frag("statement")
            nfa.edge(a, None, s0); nfa.edge(s1, None, a)  # loop
            return a, b
        if sym == "ops":
            a = nfa.new(); b = nfa.new()
            nfa.edge(a, None, b)
            s0, s1 = frag("opcall")
            nfa.edge(a, None, s0); nfa.edge(s1, None, a)
            return a, b
        if sym == "argtail":
            a = nfa.new(); b = nfa.new()
            nfa.edge(a, None, b)
            c0 = nfa.new()
            nfa.edge(a, "COMMA", c0)
            g0, g1 = frag("argument")
            nfa.edge(c0, None, g0); nfa.edge(g1, None, a)
            return a, b
        if sym == "ctail":
            a = nfa.new(); b = nfa.new()
            nfa.edge(a, None, b)
            cs, ce = frag("combinator")
            ps, pe = frag("compound")
            nfa.edge(a, None, cs); nfa.edge(ce, None, ps); nfa.edge(pe, None, a)
            return a, b
        if sym == "matchers":
            # matchers -> matcher+  (one or more), compiled as a loop
            a = nfa.new(); b = nfa.new()
            ms, me = frag("matcher")
            nfa.edge(a, None, ms); nfa.edge(me, None, b); nfa.edge(me, None, a)
            return a, b
        # generic: alternation of concatenations (inline; no self-recursion here)
        a = nfa.new(); b = nfa.new()
        for alt in GRAMMAR[sym]:
            if not alt:
                nfa.edge(a, None, b)
                continue
            prev = a
            for s in alt:
                s0, s1 = frag(s)
                nfa.edge(prev, None, s0)
                prev = s1
            nfa.edge(prev, None, b)
        return a, b

    s, e = frag(START)
    nfa.start = s
    nfa.accept = e
    return nfa


def _eps_closure(nfa, states):
    stack = list(states)
    seen = set(states)
    while stack:
        s = stack.pop()
        for (sym, t) in nfa.trans[s]:
            if sym is None and t not in seen:
                seen.add(t); stack.append(t)
    return frozenset(seen)


def build_dfa():
    nfa = build_nfa()
    start = _eps_closure(nfa, {nfa.start})
    dfa_trans = {}
    dfa_states = {start: 0}
    order = [start]
    queue = [start]
    while queue:
        cur = queue.pop()
        moves = {}
        for s in cur:
            for (sym, t) in nfa.trans[s]:
                if sym is not None:
                    moves.setdefault(sym, set()).add(t)
        dfa_trans[dfa_states[cur]] = {}
        for sym, targets in moves.items():
            cl = _eps_closure(nfa, targets)
            if cl not in dfa_states:
                dfa_states[cl] = len(order)
                order.append(cl); queue.append(cl)
            dfa_trans[dfa_states[cur]][sym] = dfa_states[cl]
    accepts_set = {dfa_states[st] for st in order if nfa.accept in st}
    return {"start": 0, "trans": dfa_trans, "accepts": accepts_set,
            "nstates": len(order)}


_DFA = None
def dfa():
    global _DFA
    if _DFA is None:
        _DFA = build_dfa()
    return _DFA


def dfa_accepts(src):
    try:
        tokens = lex(src)
    except LexError:
        return False
    d = dfa()
    st = d["start"]
    for (tt, _v, _p) in tokens:
        nxt = d["trans"].get(st, {}).get(tt)
        if nxt is None:
            return False
        st = nxt
    return st in d["accepts"]


# ── A3: longest valid prefix ────────────────────────────────────────────────
def longest_valid_prefix(src):
    """Return (LVP_tokens, total_tokens, fail_state_symbol_set).
    LVP = number of DSL tokens consumed before the DFA has no legal transition.
    If the whole input is consumed, LVP == total_tokens (accepts iff final state
    is accepting; a consumed-but-non-accepting tail is reported as LVP==total)."""
    try:
        tokens = lex(src)
    except LexError:
        return 0, 0, set()
    d = dfa()
    st = d["start"]
    consumed = 0
    for (tt, _v, _p) in tokens:
        nxt = d["trans"].get(st, {}).get(tt)
        if nxt is None:
            return consumed, len(tokens), set(d["trans"].get(st, {}).keys())
        st = nxt
        consumed += 1
    return consumed, len(tokens), set(d["trans"].get(st, {}).keys())


def nlvp(src, reference_token_len):
    lvp, _tot, _f = longest_valid_prefix(src)
    if reference_token_len <= 0:
        return 0.0
    return lvp / reference_token_len


def ref_token_len(src):
    return len(lex(src))


# ── A4: branching-factor profile ────────────────────────────────────────────
def branching_factors():
    """Return list of out-degrees over reachable non-dead DFA states."""
    d = dfa()
    return [len(d["trans"].get(s, {})) for s in range(d["nstates"])]


def branching_profile_over_corpus(programs):
    """Branching factor as a function of token position, averaged over inputs."""
    d = dfa()
    by_pos = {}
    for src in programs:
        try:
            tokens = lex(src)
        except LexError:
            continue
        st = d["start"]
        for idx, (tt, _v, _p) in enumerate(tokens):
            bf = len(d["trans"].get(st, {}))
            by_pos.setdefault(idx, []).append(bf)
            nxt = d["trans"].get(st, {}).get(tt)
            if nxt is None:
                break
            st = nxt
    prof = []
    for idx in sorted(by_pos):
        xs = by_pos[idx]
        prof.append((idx, sum(xs) / len(xs)))
    return prof


def load_positive_programs():
    """Read the positive corpus (multi-line-aware) for corpus-based metrics."""
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "positive.txt")
    items, buf = [], ""
    for raw in open(path):
        s = raw.strip()
        if not buf and (not s or s.startswith("#")):
            continue
        if s.startswith("#"):
            continue
        buf += (("\n" if buf else "") + raw.rstrip("\n"))
        if num_parses(buf) >= 1:
            items.append(buf)
            buf = ""
    return items


def branching_profile_over_corpus_default():
    return branching_profile_over_corpus(load_positive_programs())


if __name__ == "__main__":
    # tiny self-test
    ok = "(function(){ $S('.wheel').recolor('#111').scale(2); })();"
    print("version:", GRAMMAR_VERSION)
    print("parses:", num_parses(ok), "dfa:", dfa_accepts(ok))
    print("features:", len(features_with_verbs(ok)))
    d = dfa()
    print("dfa states:", d["nstates"], "terminals:", len(TERMINALS))
