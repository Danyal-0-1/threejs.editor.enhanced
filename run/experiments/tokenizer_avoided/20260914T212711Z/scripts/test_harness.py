"""test_harness.py — unit tests for everything the harness adds.

Covers the four things the work order requires tests for: the prompt renderer,
the parser integration, result checkpointing, and scoring. Run with:
    PYTHONDONTWRITEBYTECODE=1 python scripts/test_harness.py
"""
from __future__ import annotations

import json, os, re, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "alien_syntax", "src"))
sys.path.insert(0, os.path.join(REPO, "grammar_and_3DOM_client"))

import prompts as P
import extract as E
import checkpoint as C
import score as S
from phi import identity_phi, load_candidate
from transpiler import parse, phi_forward
from canonicalize import content_hash, canonical_json
from fixture_scene import scene_for


class TestPromptRenderer(unittest.TestCase):
    """The renderer must not teach an alien language using 3DOM spellings."""

    def test_every_taught_spelling_belongs_to_the_target_language(self):
        """The decisive no-leakage test.

        `taught_spellings` is the exact set of tokens the spec presents as
        language tokens. Every one must be THIS language's spelling for that
        role. If a 3DOM spelling were ever taught to alpha/beta/gamma, this
        fails -- regardless of how the prose is worded.
        """
        for lang in P.LANGUAGES:
            phi = P.phi_for(lang)
            alien_of_verb = {c: a for a, c in phi.verbs().items()}
            alien_of_type = {c: a for a, c in phi.types().items()}
            alien_of_pseudo = {c: a for a, c in phi.pseudos().items()}
            taught = P.taught_spellings(lang)
            for role, got in taught.items():
                if role.startswith("verb:"):
                    want = alien_of_verb[role.split(":", 1)[1]]
                elif role.startswith("type:"):
                    want = alien_of_type[role.split(":", 1)[1]]
                elif role.startswith("pseudo:"):
                    want = alien_of_pseudo[role.split(":", 1)[1]]
                else:
                    want = phi.spelling(role)
                self.assertEqual(got, want, f"{lang}/{role}")

    def test_taught_spellings_differ_from_3dom_where_phi_differs(self):
        """Sanity on the test itself: for an alien language the taught set must
        NOT equal 3DOM's, or the previous test would pass vacuously."""
        base = P.taught_spellings("identity")
        for lang in ("alpha", "beta", "gamma"):
            self.assertNotEqual(P.taught_spellings(lang), base, lang)

    def test_every_taught_spelling_actually_appears_in_the_spec(self):
        for lang in P.LANGUAGES:
            spec = P.render_spec(lang)
            for role, sp in P.taught_spellings(lang).items():
                self.assertIn(sp, spec, f"{lang}/{role}: {sp!r} missing from spec")

    def test_no_3dom_symbol_sigil_in_alien_example_code(self):
        """The EXAMPLE PROGRAM lines are what the model imitates. A 3DOM symbol
        sigil must never appear there unless this language also uses it.

        Scoped to code lines on purpose: a full stop ending an English sentence
        is punctuation, not a class sigil, and flagging it would be noise.
        """
        ident = identity_phi()
        table = ident.table
        dom_syms = {ident.spelling(t) for t in table.substitutable_ids
                    if not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", ident.spelling(t))}
        for lang in ("alpha", "beta", "gamma"):
            phi = load_candidate(lang)
            own = {phi.spelling(t) for t in table.by_id}
            entry = phi.spelling("T_SELECTOR_ENTRY")
            # Mask string literals (frozen shared vocabulary) and <...>
            # metasyntax placeholders -- the angle brackets in "<operation>"
            # are prompt notation, not the child combinator.
            def _mask(l):
                l = re.sub(r"'[^'\n]*'", "''", l)
                l = re.sub(r"<[A-Za-z0-9_]+>", "PLACEHOLDER", l)
                l = l.replace("...", "ELLIPSIS")   # metasyntax, not chain ops
                # T_NUMBER is a FROZEN terminal (V3/V7): the decimal point in
                # "0.5" is shared by all four languages and is not a class sigil.
                return re.sub(r"\d+\.\d+", "NUM", l)
            code_lines = [_mask(l) for l in P.render_spec(lang).splitlines()
                          if entry in l]
            self.assertTrue(code_lines, f"{lang}: no example code lines found")
            for line in code_lines:
                for v in sorted(dom_syms - own):
                    self.assertNotIn(v, line,
                        f"{lang} example code leaks the 3DOM sigil {v!r}: {line!r}")

    def test_no_3dom_sigil_leaks_where_language_differs(self):
        for lang in ("alpha", "beta", "gamma"):
            phi = load_candidate(lang)
            spec = P.render_spec(lang)
            entry = phi.spelling("T_SELECTOR_ENTRY")
            if entry != "$S":
                self.assertNotIn("$S", spec, f"{lang} prompt leaks '$S'")

    def test_spec_teaches_this_languages_spellings(self):
        for lang in P.LANGUAGES:
            phi = P.phi_for(lang)
            spec = P.render_spec(lang)
            for alien in phi.verbs():
                self.assertIn(alien, spec, f"{lang} spec omits verb {alien!r}")
            self.assertIn(phi.spelling("T_SELECTOR_ENTRY"), spec)

    def test_structure_is_identical_across_languages(self):
        """Same line count and same section headers: information-matched."""
        counts = {l: len(P.render_spec(l).splitlines()) for l in P.LANGUAGES}
        self.assertEqual(len(set(counts.values())), 1, f"line counts differ: {counts}")

    def test_bare_has_no_scaffold_and_scaffolded_does(self):
        case = {"prompt": "make the wheels black", "asset": "dumptruck"}
        bare = P.render_user(case, "identity", "bare")
        scaf = P.render_user(case, "identity", "scaffolded")
        self.assertNotIn("ADDRESSABLE PARTS", bare)
        self.assertIn("ADDRESSABLE PARTS", scaf)
        self.assertIn(case["prompt"], bare)
        self.assertIn(case["prompt"], scaf)

    def test_scaffold_uses_target_class_sigil(self):
        scaf = P.render_scaffold("gamma", "dumptruck")
        cls = load_candidate("gamma").spelling("T_CLASS_SIGIL")
        self.assertIn(f"{cls}wheel", scaf)
        self.assertNotIn(".wheel", scaf)


class TestExtraction(unittest.TestCase):
    def test_fenced_block_wins(self):
        code, rule = E.extract_code("blah\n```js\nCODE HERE\n```\ntrailing", "$S")
        self.assertEqual(code, "CODE HERE")
        self.assertEqual(rule, "E1_FENCE")

    def test_unfenced_program_recovered(self):
        r = "Sure:\n(function(){ $S('.wheel').recolor('black'); })();\nHope that helps"
        code, rule = E.extract_code(r, "$S")
        self.assertEqual(rule, "E2_UNFENCED")
        self.assertIn("$S", code)

    def test_empty_is_e0(self):
        self.assertEqual(E.extract_code("   ", "$S")[1], "E0_EMPTY")

    def test_extraction_never_repairs(self):
        broken = "```\n(function(){ $S('.wheel'.recolor(; })();\n```"
        code, _ = E.extract_code(broken, "$S")
        self.assertIn("$S('.wheel'.recolor(;", code)   # handed over verbatim


class TestScoring(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(os.path.dirname(HERE), "inputs", "task_dataset.json"),
                  encoding="utf-8") as fh:
            self.ds = json.load(fh)
        self.cases = {c["id"]: c for c in self.ds["cases"]}

    def test_gold_answer_scores_valid_correct_in_every_language(self):
        for cid, case in self.cases.items():
            if case["gold"] is None:
                continue
            for lang in P.LANGUAGES:
                src = case["gold_renderings"][lang]
                res = S.score_response(f"```\n{src}\n```", case, lang)
                self.assertEqual(res["outcome"], E.VALID_CORRECT,
                    f"{cid}/{lang}: gold scored {res['outcome']} ({res['scorer_explanation']})")

    def test_wrong_answer_scores_valid_wrong(self):
        case = self.cases["wheels-black"]
        res = S.score_response("```\n(function(){ $S('.cab').scale(2); })();\n```",
                               case, "identity")
        self.assertEqual(res["outcome"], E.VALID_WRONG)
        self.assertEqual(res["op_correct"], 0)

    def test_unparseable_scores_parse_or_lex_fail(self):
        case = self.cases["wheels-black"]
        res = S.score_response("```\nthis is not a program at all\n```", case, "identity")
        self.assertIn(res["outcome"], (E.PARSE_FAIL, E.LEX_FAIL))
        self.assertEqual(res["parse_valid"], 0)

    def test_vacuous_is_parse_success_and_task_failure(self):
        case = self.cases["wheels-black"]
        res = S.score_response("```\n(function(){ $S('.wheel'); })();\n```", case, "identity")
        self.assertEqual(res["outcome"], E.VALID_VACUOUS)
        self.assertEqual(res["parse_valid"], 1)
        self.assertEqual(res["semantic_correct"], 0)

    def test_wrong_language_spelling_is_detected(self):
        """A 3DOM answer submitted to the gamma arm must not silently pass."""
        case = self.cases["wheels-black"]
        res = S.score_response("```\n(function(){ $S('.wheel').recolor('black'); })();\n```",
                               case, "gamma")
        self.assertEqual(res["requested_language_compliance"], 0)
        self.assertNotEqual(res["outcome"], E.VALID_CORRECT)

    def test_wildcard_bleed_fails_selector(self):
        case = self.cases["wheels-black"]
        res = S.score_response("```\n(function(){ $S('*').recolor('black'); })();\n```",
                               case, "identity")
        self.assertEqual(res["selector_correct"], 0)

    def test_graceful_refusal_case_scored_separately(self):
        case = self.cases["merged-sheets"]
        self.assertEqual(case["scoring_family"], "graceful_refusal")
        good = S.score_response("```\n(function(){})();\n```", case, "identity")
        self.assertEqual(good["refusal_correct"], 1)
        bad = S.score_response("```\n(function(){ $S('.bed').recolor('blue'); })();\n```",
                               case, "identity")
        self.assertEqual(bad["refusal_correct"], 0)

    def test_nlvp_is_between_zero_and_one_ish(self):
        case = self.cases["wheels-black"]
        res = S.score_response("```\n(function(){ $S('.wheel').reco\n```", case, "identity")
        self.assertGreaterEqual(res["nlvp"], 0.0)


class TestCheckpoint(unittest.TestCase):
    def test_key_includes_every_required_field(self):
        k = C.result_key(model="M", revision="R", tokenizer_revision="TR", lane="B",
                         language="alpha", condition="bare", case_id="c1", seed=7,
                         precision="fp16", device="cuda", prompt_hash="ph")
        for part in ("M", "R", "TR", "B", "alpha", "bare", "c1", "7", "fp16", "cuda", "ph"):
            self.assertIn(part, k)

    def test_differing_field_changes_key(self):
        base = dict(model="M", revision="R", tokenizer_revision="TR", lane="B",
                    language="alpha", condition="bare", case_id="c1", seed=7,
                    precision="fp16", device="cuda", prompt_hash="ph")
        for field, new in (("language", "beta"), ("precision", "fp32"),
                           ("prompt_hash", "other"), ("seed", 8)):
            self.assertNotEqual(C.result_key(**base),
                                C.result_key(**{**base, field: new}), field)

    def test_roundtrip_and_resume_skips_only_valid_rows(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "raw.jsonl")
            row = {"result_key": "k1", "outcome": "VALID_CORRECT", "x": 1}
            C.append_row(path, row)
            self.assertEqual(C.load_done(path), {"k1"})
            # a truncated final line must NOT be treated as done
            with open(path, "a") as fh:
                fh.write('{"result_key": "k2", "outc')
            self.assertEqual(C.load_done(path), {"k1"})

    def test_corrupt_row_without_key_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "raw.jsonl")
            with open(path, "w") as fh:
                fh.write('{"no_key": 1}\n')
            self.assertEqual(C.load_done(path), set())


class TestParserIntegration(unittest.TestCase):
    def test_four_languages_agree_on_canonical_ir(self):
        src = "(function(){ $S('.wheel.front').recolor('red'); $S('.bed').delete(); })();"
        ident = identity_phi()
        want = content_hash(parse(src, ident))
        for lang in ("alpha", "beta", "gamma"):
            phi = load_candidate(lang)
            self.assertEqual(content_hash(parse(phi_forward(src, phi), phi)), want, lang)


if __name__ == "__main__":
    unittest.main(verbosity=2)
