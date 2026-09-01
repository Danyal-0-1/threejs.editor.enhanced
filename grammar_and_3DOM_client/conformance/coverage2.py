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




# #!/usr/bin/env python3
# """Conformance CI for the 3DOM grammar reference implementation.

# Usage
# -----
#     python3 conformance/coverage.py
#     python3 conformance/coverage.py --corpus-dir ./corpora --json
#     python3 conformance/coverage.py --max-violations 25

# Exit status
# -----------
#     0   every gate passed
#     1   at least one gate failed -- the grammar or the corpus is wrong
#     2   the harness itself could not run (missing corpus, bad arguments)

# Design
# ------
# ``refgrammar`` is the system under test and is treated as opaque. This module
# asks it six independent questions ("gates"). Every gate is a pure function
# ``Corpora -> GateResult``; registering a new one means writing one function and
# decorating it with ``@gate``. Nothing else changes.

#     G1  every positive program has EXACTLY ONE derivation -> no ambiguity    [D3]
#     G2  the positive corpus exercises EVERY grammar production -> 100%       [A2]
#     G3  every negative program is rejected (zero derivations)                [A2]
#     G4  every vacuous program parses AND emits zero operations               [D5]
#     G5  '.car .wheel' (descendant) derives differently from '.car.wheel'     [D1]
#     G6  the Earley recogniser and the DFA agree on every corpus item  [ISO==W3C]

# G6 establishes *operational* agreement over a finite sample. It is a strong
# witness, not a proof of language equivalence.

# Requires Python 3.10+.
# """

# from __future__ import annotations

# import argparse
# import json
# import sys
# from collections.abc import Callable, Iterator, Sequence
# from dataclasses import dataclass
# from functools import lru_cache
# from pathlib import Path

# # --------------------------------------------------------------------------- #
# # Import bootstrap                                                             #
# # --------------------------------------------------------------------------- #
# # refgrammar.py is a sibling file, not an installed package. Put this script's
# # own directory at the front of the module search path so the import resolves
# # regardless of the working directory, of whether this file is executed or
# # imported by a test runner, and of whether Python was started with -P /
# # PYTHONSAFEPATH=1 (which suppresses the automatic sys.path[0] insertion).

# SCRIPT_DIR = Path(__file__).resolve().parent
# if str(SCRIPT_DIR) not in sys.path:
#     sys.path.insert(0, str(SCRIPT_DIR))

# import refgrammar  # noqa: E402  -- deliberately after the sys.path bootstrap

# # --------------------------------------------------------------------------- #
# # Constants                                                                    #
# # --------------------------------------------------------------------------- #

# Feature = tuple[str, int]  # (production name, branch index)

# COMMENT_PREFIX = "#"
# VERB_TOKEN = "VERB"
# EXCERPT_WIDTH = 72

# #: G5 fixtures. Whitespace inside the selector is semantically load-bearing:
# #: '.car .wheel' is a descendant combinator, '.car.wheel' is a compound AND.
# DESCENDANT_FIXTURE = "(function(){ $S('.car .wheel').delete(); })();"
# COMPOUND_FIXTURE = "(function(){ $S('.car.wheel').delete(); })();"
# DESCENDANT_COMBINATOR: Feature = ("combinator", 0)
# COMPOUND_AND: Feature = ("matchers", 1)

# EXIT_PASS, EXIT_GATE_FAILURE, EXIT_HARNESS_ERROR = 0, 1, 2


# # --------------------------------------------------------------------------- #
# # Layer 1 -- memoised adapter over the system under test                       #
# # --------------------------------------------------------------------------- #
# # The ONLY code that touches refgrammar. Every gate asks the same questions
# # about the same strings, so each answer is computed once and reused. In the
# # original harness a single positive program was fully parsed four separate
# # times; Earley is O(n^3) in the worst case, so this is the dominant cost.
# #
# # Note the frozenset returns: a cached function that hands back a *mutable*
# # object gives every caller the same object, and one mutation silently
# # corrupts every later reader.


# @lru_cache(maxsize=None)
# def parse_count(source: str) -> int:
#     """Number of distinct derivations. 0 = rejected, 1 = unambiguous, >1 = ambiguous."""
#     return refgrammar.num_parses(source)


# def earley_accepts(source: str) -> bool:
#     """Whether the Earley engine recognises ``source`` at all."""
#     return parse_count(source) > 0


# @lru_cache(maxsize=None)
# def dfa_accepts(source: str) -> bool:
#     """Whether the independent DFA recogniser accepts ``source``."""
#     return bool(refgrammar.dfa_accepts(source))


# @lru_cache(maxsize=None)
# def covered_features(source: str) -> frozenset[Feature]:
#     """Grammar branches exercised by ``source`` under an operation."""
#     return frozenset(refgrammar.features_with_verbs(source))


# @lru_cache(maxsize=None)
# def derived_features(source: str) -> frozenset[Feature]:
#     """Grammar branches taken by the derivation of ``source`` (used by G5)."""
#     features, _ = refgrammar.derive(refgrammar.lex(source))
#     return frozenset(features)


# @lru_cache(maxsize=None)
# def operation_count(source: str) -> int:
#     """How many mutating operations ``source`` performs. Lexing only, no parse."""
#     return sum(1 for token in refgrammar.lex(source) if token[0] == VERB_TOKEN)


# def all_obligations() -> frozenset[Feature]:
#     """Every production branch the grammar has -- the coverage denominator."""
#     return frozenset(refgrammar.all_features())


# # --------------------------------------------------------------------------- #
# # Layer 2 -- data model                                                        #
# # --------------------------------------------------------------------------- #


# @dataclass(frozen=True, slots=True)
# class Program:
#     """One corpus item, carrying enough provenance to be actionable in a report."""

#     source: str
#     origin: str  # e.g. "positive.txt:41"

#     def excerpt(self, width: int = EXCERPT_WIDTH) -> str:
#         """Single-line, length-capped rendering suitable for a failure message."""
#         flat = " ".join(self.source.split())
#         return flat if len(flat) <= width else f"{flat[: width - 1]}\u2026"


# @dataclass(frozen=True, slots=True)
# class Violation:
#     """One concrete reason a gate failed."""

#     subject: str
#     detail: str


# @dataclass(frozen=True, slots=True)
# class GateResult:
#     """The verdict of one gate. ``passed`` is derived, never stored."""

#     gate_id: str
#     title: str
#     summary: str
#     violations: tuple[Violation, ...] = ()

#     @property
#     def passed(self) -> bool:
#         return not self.violations


# @dataclass(frozen=True, slots=True)
# class Corpora:
#     """The three corpora, immutable once loaded."""

#     positive: tuple[Program, ...]
#     negative: tuple[Program, ...]
#     vacuous: tuple[Program, ...]

#     @property
#     def every_program(self) -> tuple[Program, ...]:
#         return self.positive + self.negative + self.vacuous

#     @property
#     def total(self) -> int:
#         return len(self.positive) + len(self.negative) + len(self.vacuous)


# class CorpusError(RuntimeError):
#     """Raised when a corpus file cannot be read. Distinct from a gate failure."""


# # --------------------------------------------------------------------------- #
# # Layer 3 -- corpus loading                                                    #
# # --------------------------------------------------------------------------- #


# def _significant_lines(path: Path) -> Iterator[tuple[int, str]]:
#     """Yield ``(1-based line number, line)`` for lines that are neither blank
#     nor comments.

#     Deliberately returns a generator *expression* rather than containing a
#     ``yield``: that keeps the CorpusError eager. Were this a generator
#     function, a missing file would not surface until the first iteration,
#     somewhere far from the cause.
#     """
#     try:
#         text = path.read_text(encoding="utf-8")
#     except OSError as exc:
#         raise CorpusError(f"cannot read corpus {path.name}: {exc}") from exc

#     return (
#         (number, line)
#         for number, line in enumerate(text.splitlines(), start=1)
#         if line.strip() and not line.lstrip().startswith(COMMENT_PREFIX)
#     )


# def load_line_delimited(path: Path) -> tuple[Program, ...]:
#     """One program per line -- the contract for the negative corpus."""
#     return tuple(
#         Program(source=line, origin=f"{path.name}:{number}")
#         for number, line in _significant_lines(path)
#     )


# def _accumulate_programs(path: Path) -> Iterator[Program]:
#     """Split a corpus in which programs may span several physical lines.

#     There is no delimiter, so the boundary is found by asking the parser after
#     every line: "is what I have so far a complete program?" This flushes at the
#     *shortest* parsing prefix, which is the format's contract.

#     This is a fold with a flush condition and mutable state, so it is a
#     generator function and not a comprehension -- forcing it into one would
#     need walrus operators and side effects inside an expression, and would be
#     strictly worse to read. It still composes like a comprehension: the caller
#     just wraps it in ``tuple()``.
#     """
#     buffer: list[str] = []
#     start_line = 0

#     for lineno, line in _significant_lines(path):
#         if not buffer:
#             start_line = lineno
#         buffer.append(line)

#         candidate = "\n".join(buffer)
#         if parse_count(candidate) >= 1:
#             yield Program(candidate, f"{path.name}:{start_line}")
#             buffer.clear()

#     if buffer:
#         # Never parsed. Emit it anyway rather than swallowing it: G1 will fail
#         # on it, which is the correct signal that the corpus file is malformed.
#         yield Program("\n".join(buffer), f"{path.name}:{start_line} (unterminated)")


# def load_multiline(path: Path) -> tuple[Program, ...]:
#     """Load a corpus whose programs may span several lines."""
#     return tuple(_accumulate_programs(path))


# def load_corpora(directory: Path) -> Corpora:
#     """Load all three corpora from ``directory``. Raises CorpusError on I/O failure."""
#     return Corpora(
#         positive=load_multiline(directory / "positive.txt"),
#         negative=load_line_delimited(directory / "negative.txt"),
#         vacuous=load_multiline(directory / "vacuous.txt"),
#     )


# # --------------------------------------------------------------------------- #
# # Layer 4 -- gate registry                                                     #
# # --------------------------------------------------------------------------- #

# GateFn = Callable[[Corpora], GateResult]
# GATES: list[GateFn] = []


# def gate(function: GateFn) -> GateFn:
#     """Register a gate. Execution order follows definition order."""
#     GATES.append(function)
#     return function


# @gate
# def g1_positives_are_unambiguous(corpora: Corpora) -> GateResult:
#     """Ambiguity is the cardinal sin: >1 derivation means two conforming
#     implementations may disagree about what a program *means*."""
#     violations = tuple(
#         Violation(program.origin, f"{parse_count(program.source)} derivations - {program.excerpt()}")
#         for program in corpora.positive
#         if parse_count(program.source) != 1
#     )
#     return GateResult(
#         "G1",
#         "unambiguous positives",
#         f"{len(corpora.positive)} positives, one derivation each",
#         violations,
#     )


# @gate
# def g2_production_coverage(corpora: Corpora) -> GateResult:
#     """Grammar coverage, not line coverage: every production branch must be
#     exercised. Only unambiguous items may contribute -- coverage claimed via an
#     ambiguous parse is meaningless."""
#     obligations = all_obligations()
#     covered = {
#         feature
#         for program in corpora.positive
#         if parse_count(program.source) == 1
#         for feature in covered_features(program.source)
#     }
#     violations = tuple(
#         Violation("uncovered branch", repr(feature))
#         for feature in sorted(obligations - covered, key=repr)
#     )
#     return GateResult(
#         "G2",
#         "production coverage",
#         f"{len(obligations & covered)}/{len(obligations)} branches exercised",
#         violations,
#     )


# @gate
# def g3_negatives_are_rejected(corpora: Corpora) -> GateResult:
#     """Without this gate, a grammar that accepts everything would pass G1 and G2."""
#     violations = tuple(
#         Violation(
#             program.origin,
#             f"accepted with {parse_count(program.source)} derivation(s) - {program.excerpt()}",
#         )
#         for program in corpora.negative
#         if parse_count(program.source) != 0
#     )
#     return GateResult(
#         "G3",
#         "negatives rejected",
#         f"{len(corpora.negative)} negatives, all rejected",
#         violations,
#     )


# @gate
# def g4_vacuous_programs_are_inert(corpora: Corpora) -> GateResult:
#     """Two properties at once: well-formed AND side-effect free."""
#     violations = tuple(
#         Violation(
#             program.origin,
#             f"parses={parse_count(program.source)} "
#             f"operations={operation_count(program.source)} - {program.excerpt()}",
#         )
#         for program in corpora.vacuous
#         if parse_count(program.source) != 1 or operation_count(program.source) != 0
#     )
#     return GateResult(
#         "G4",
#         "vacuous programs inert",
#         f"{len(corpora.vacuous)} vacuous items parse with zero operations",
#         violations,
#     )


# @gate
# def g5_selector_differential(_: Corpora) -> GateResult:
#     """Regression guard for significant whitespace inside selectors.

#     Expressed as {failure message: must-be-true predicate} so the comprehension
#     below reads as "report every expectation that did not hold".
#     """
#     descendant = derived_features(DESCENDANT_FIXTURE)
#     compound = derived_features(COMPOUND_FIXTURE)

#     expectations: dict[str, bool] = {
#         "'.car .wheel' did not use the descendant combinator": DESCENDANT_COMBINATOR in descendant,
#         "'.car.wheel' did not use the compound AND": COMPOUND_AND in compound,
#         "both selectors produced identical feature sets": descendant != compound,
#     }
#     violations = tuple(
#         Violation("L2 differential", reason) for reason, holds in expectations.items() if not holds
#     )
#     return GateResult(
#         "G5",
#         "selector differential",
#         "'.car .wheel' (descendant) derives differently from '.car.wheel' (AND)",
#         violations,
#     )


# @gate
# def g6_recognisers_agree(corpora: Corpora) -> GateResult:
#     """Two independent recognisers must agree on accept/reject across every
#     corpus item. Disagreement proves one is wrong -- though not which one."""
#     violations = tuple(
#         Violation(
#             program.origin,
#             f"earley={earley_accepts(program.source)} "
#             f"dfa={dfa_accepts(program.source)} - {program.excerpt()}",
#         )
#         for program in corpora.every_program
#         if earley_accepts(program.source) != dfa_accepts(program.source)
#     )
#     return GateResult(
#         "G6",
#         "recogniser agreement",
#         f"Earley and DFA agree on all {corpora.total} corpus items",
#         violations,
#     )


# # --------------------------------------------------------------------------- #
# # Reporting                                                                    #
# # --------------------------------------------------------------------------- #


# def render_text(corpora: Corpora, results: Sequence[GateResult], max_violations: int) -> str:
#     """Human-readable report. Pure: builds a string, does not print."""
#     rule = "=" * 72
#     lines = [
#         f"3DOM conformance - {refgrammar.GRAMMAR_VERSION}",
#         rule,
#         f"corpus sizes: positive={len(corpora.positive)}  "
#         f"negative={len(corpora.negative)}  vacuous={len(corpora.vacuous)}",
#         "",
#     ]

#     for result in results:
#         status = "OK  " if result.passed else "FAIL"
#         lines.append(f"{result.gate_id} {status} {result.title:<24} {result.summary}")
#         lines.extend(
#             f"       - {violation.subject}: {violation.detail}"
#             for violation in result.violations[:max_violations]
#         )
#         if len(result.violations) > max_violations:
#             lines.append(f"       ... and {len(result.violations) - max_violations} more")

#     failed = [result for result in results if not result.passed]
#     lines.append(rule)
#     if failed:
#         lines.append(f"RESULT: FAIL ({len(failed)}/{len(results)} gates)")
#         lines.extend(
#             f"  - {result.gate_id}: {len(result.violations)} violation(s)" for result in failed
#         )
#     else:
#         lines.append(f"RESULT: PASS - all {len(results)} gates green")
#     return "\n".join(lines)


# def render_json(corpora: Corpora, results: Sequence[GateResult]) -> str:
#     """Machine-readable report for dashboards and downstream tooling."""
#     return json.dumps(
#         {
#             "grammar_version": refgrammar.GRAMMAR_VERSION,
#             "corpus_sizes": {
#                 "positive": len(corpora.positive),
#                 "negative": len(corpora.negative),
#                 "vacuous": len(corpora.vacuous),
#             },
#             "passed": all(result.passed for result in results),
#             "gates": [
#                 {
#                     "id": result.gate_id,
#                     "title": result.title,
#                     "summary": result.summary,
#                     "passed": result.passed,
#                     "violations": [
#                         {"subject": violation.subject, "detail": violation.detail}
#                         for violation in result.violations
#                     ],
#                 }
#                 for result in results
#             ],
#         },
#         indent=2,
#     )


# # --------------------------------------------------------------------------- #
# # Entry point                                                                  #
# # --------------------------------------------------------------------------- #


# def build_parser() -> argparse.ArgumentParser:
#     parser = argparse.ArgumentParser(
#         prog="coverage.py",
#         description="Conformance CI for the 3DOM grammar reference implementation.",
#     )
#     parser.add_argument(
#         "--corpus-dir",
#         type=Path,
#         default=SCRIPT_DIR,
#         metavar="DIR",
#         help="directory holding positive.txt, negative.txt and vacuous.txt "
#         "(default: this script's directory)",
#     )
#     parser.add_argument(
#         "--max-violations",
#         type=int,
#         default=8,
#         metavar="N",
#         help="violations printed per failing gate (default: 8)",
#     )
#     parser.add_argument(
#         "--json",
#         action="store_true",
#         help="emit a machine-readable report instead of the text report",
#     )
#     return parser


# def main(argv: Sequence[str] | None = None) -> int:
#     args = build_parser().parse_args(argv)

#     try:
#         corpora = load_corpora(args.corpus_dir)
#     except CorpusError as exc:
#         # A broken harness is not a failing grammar: distinct exit code.
#         print(f"harness error: {exc}", file=sys.stderr)
#         return EXIT_HARNESS_ERROR

#     results = [run_gate(corpora) for run_gate in GATES]

#     report = render_json(corpora, results) if args.json else render_text(
#         corpora, results, args.max_violations
#     )
#     print(report)

#     return EXIT_PASS if all(result.passed for result in results) else EXIT_GATE_FAILURE


# if __name__ == "__main__":
#     sys.exit(main())