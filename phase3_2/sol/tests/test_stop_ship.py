"""Regression tests for the stop-ship defects. Each one demonstrates the OLD
behaviour failing where that is possible, not just the new one passing."""

from __future__ import annotations

from collections import Counter

import _helpers as H  # noqa: F401  (sets up sys.path via p33)
import phi as P

from phase3_2 import analysis as AN
from phase3_2 import prompts, sampling, sites2 as S, templates as TM
from phase3_2.backends import BACKENDS
from phase3_2.margins import (IdenticalCandidates, NoContext, ZeroLengthSpan,
                              check_pair)

from p33 import demos as D
from p33 import kstar
from p33.fakes import FakeScorer

IDENT = P.identity_phi()
TEMPS = TM.build_templates()


def _pool(lexicons, family="dom"):
    be = BACKENDS[family]
    out = []
    for lx in lexicons:
        L = P.load_candidate(lx)
        for t in TEMPS:
            out += [s for s in S.classify(be.render(t.ir, L), L, be,
                                          template_id=t.template_id, identity=IDENT)
                    if s.is_usable]
    return out


# ---------------------------------------------------------------------------
# 1. multi-lexicon prompt corruption (P33-006)
# ---------------------------------------------------------------------------

def test_old_behaviour_first_lexicon_table_is_rejected():
    """The old runners rendered ONE table from lexicons[0] for every site."""
    lex0, lex1 = P.load_candidate("d25s1"), P.load_candidate("d50s2")
    site = next(s for s in _pool(["d50s2"]) if s.terminal_id == "T_TYPE_MESH")
    old = prompts.bundle("rule", lex0)                        # the defect
    try:
        prompts.assert_prompt_matches(site, lex1, old)
    except AssertionError as exc:
        assert "P33-006" in str(exc) or "d25s1" in str(exc)
    else:
        raise AssertionError("a d25s1 table was accepted for a d50s2 site")


def test_old_behaviour_caught_even_when_the_table_line_coincides():
    """d25s1 and d50s2 share the SIGIL mapping, so a table-line check alone
    would pass by coincidence -- the bundle's lexicon id must catch it."""
    lex0, lex1 = P.load_candidate("d25s1"), P.load_candidate("d50s2")
    assert lex0.spelling("T_CLASS_SIGIL") == lex1.spelling("T_CLASS_SIGIL")
    site = next(s for s in _pool(["d50s2"]) if s.terminal_id == "T_CLASS_SIGIL")
    try:
        prompts.assert_prompt_matches(site, lex1, prompts.bundle("rule", lex0))
    except AssertionError:
        return
    raise AssertionError("coincident sigil line let a cross-lexicon prompt through")


def test_every_site_gets_its_own_lexicons_table_in_a_two_lexicon_run():
    for s in _pool(["d25s1", "d50s2"])[:200]:
        L = P.load_candidate(s.phi_id)
        prompts.assert_prompt_matches(s, L, prompts.bundle("rule", L))


def test_norule_lenmatched_reaches_rule_token_count():
    L = P.load_candidate("d50s1")
    fs = FakeScorer()
    count = lambda t: len(fs.ids(t))  # noqa: E731
    n = prompts.norule_lenmatched(L, count)
    assert count(n) >= count(prompts.rule_prompt(L))
    assert "TOKEN TABLE" not in n
    assert count(prompts.norule_prompt(L)) < count(prompts.rule_prompt(L))


# ---------------------------------------------------------------------------
# 2. sampling: expected cells + order independence (P33-003 / P33-004)
# ---------------------------------------------------------------------------

DEV = ["d25s1", "d25s2", "d50s1", "d50s2"]


def test_selection_is_identical_under_every_lexicon_order():
    ref = [s.site_id for s in sampling.balanced(_pool(DEV))]
    for order in (DEV[::-1], ["d50s1", "d25s2", "d50s2", "d25s1"],
                  ["d25s2", "d50s2", "d25s1", "d50s1"]):
        got = [s.site_id for s in sampling.balanced(_pool(order))]
        assert got == ref, order


def test_old_global_dedup_was_order_dependent():
    a = Counter(s.phi_id for s in S.dedupe_by_prefix(_pool(DEV)))
    b = Counter(s.phi_id for s in S.dedupe_by_prefix(_pool(DEV[::-1])))
    assert a != b, "the regression this guards against no longer reproduces"


def test_dedup_unit_is_family_lexicon_and_records_drops():
    kept, dropped = sampling.dedupe_within_cells(_pool(["d50s1"]))
    prefixes = Counter((sampling.family_of(s), s.phi_id, s.prefix) for s in kept)
    assert max(prefixes.values()) == 1
    assert dropped and all(d.duplicate_of for d in dropped)


def test_missing_cell_is_refused():
    pool = _pool(DEV)
    expected = sampling.available_cells(pool)
    sample = [s for s in sampling.balanced(pool)
              if not (s.phi_id == "d50s1" and S.stratum(s) == "verb")]
    try:
        sampling.assert_balanced(sample, families=["dom"], expected=expected)
    except AssertionError as exc:
        assert "dom/d50s1/verb" in str(exc)
    else:
        raise AssertionError("a sample missing dom/d50s1/verb passed")


def test_structurally_empty_cell_is_reported_not_failed():
    grid = sampling.structural_grid(_pool(DEV), families=["dom"], lexicons=DEV)
    empty = [g for g in grid if g["status"] == "STRUCTURALLY_EMPTY"]
    assert {(g["lexicon"], g["stratum"]) for g in empty} == {("d25s2", "sigil")}
    pool = _pool(DEV)
    sampling.assert_balanced(sampling.balanced(pool), families=["dom"],
                             expected=sampling.available_cells(pool))


def test_cell_counts_serialises_expected_and_observed():
    pool = _pool(["d50s1"])
    c = sampling.cell_counts(sampling.balanced(pool, 6),
                             expected=sampling.available_cells(pool))
    assert c["expected_by_cell"] and c["by_cell"]
    assert isinstance(c["empty_cells"], list)


# ---------------------------------------------------------------------------
# 3. demonstration leakage (P33-008)
# ---------------------------------------------------------------------------

def _rendered(lx="d50s1", fam="dom"):
    L, be = P.load_candidate(lx), BACKENDS[fam]
    return {t.template_id: be.render(t.ir, L) for t in TEMPS}


def test_old_first_32_pool_leaked_the_target():
    rendered = _rendered()
    old_pool = list(rendered)[:32]
    site = next(s for s in _pool(["d50s1"]) if s.template_id == "t005")
    assert site.template_id in old_pool and rendered["t005"] == site.program


def test_demonstrations_never_contain_the_target():
    rendered = _rendered()
    op = D.common_opening(rendered)
    order = D.pool_order(list(rendered), 20261005, "dom/d50s1")
    for s in _pool(["d50s1"])[:150]:
        ds = D.for_site(s, rendered, order, 32)
        assert s.template_id not in ds.ids
        assert s.program not in ds.texts
        assert D.audit(s, ds, opening=op) == []


def test_replayed_decision_prefix_is_a_leak_but_the_fixed_opening_is_not():
    rendered = _rendered()
    op = D.common_opening(rendered)
    sites = _pool(["d50s1"])
    first = next(s for s in sites if s.prefix == op)
    assert D.is_leak(first, "tX", "(function(){ $S('#other')#recolor('#1'); })();", opening=op) is None
    deep = next(s for s in sites if len(s.prefix) > len(op) + 10)
    assert D.is_leak(deep, "tX", deep.prefix + deep.correct + "...", opening=op) == "replays_decision_prefix"


def test_ladder_is_nested_and_hashed():
    rendered = _rendered()
    order = D.pool_order(list(rendered), 7, "s")
    s = _pool(["d50s1"])[0]
    full = D.for_site(s, rendered, order, 8)
    assert full.first(4).ids == full.ids[:4]
    assert full.first(4).sha != full.sha
    assert D.pool_order(list(rendered), 7, "s") == order


# ---------------------------------------------------------------------------
# 4. k* and censoring (P33-007)
# ---------------------------------------------------------------------------

L7 = [0, 1, 2, 4, 8, 16, 32]


def test_kstar_zero_when_already_correct():
    k = kstar.compute(L7, [0.3, -0.1, 0.2, 0.4, 0.5, 0.6, 0.7])
    assert k.k_star == 0.0 and k.already_correct and not k.censored


def test_kstar_already_correct_at_exactly_zero_margin():
    k = kstar.compute(L7, [0.0, -1, -1, -1, -1, -1, -1])
    assert k.k_star == 0.0 and k.already_correct and not k.censored and k.recrossed_down


def test_kstar_first_crossing_interpolated():
    k = kstar.compute([0, 1, 2, 4, 8], [-3.0, -2.5, -1.5, -0.5, 1.5])
    assert abs(k.k_star - (4 + 0.25 * 4)) < 1e-12        # hand: 4 + (0.5/2.0)*4 = 5.0
    assert not k.censored and not k.already_correct


def test_kstar_no_crossing_is_censored():
    k = kstar.compute(L7, [-3, -2.9, -2.5, -2, -1.5, -1, -0.2])
    assert k.k_star is None and k.censored


def test_crossed_then_dropped_is_not_censored():
    k = kstar.compute(L7, [-1, 0.5, -0.2, -0.4, -0.1, -0.3, -0.6])
    assert k.k_star is not None and not k.censored
    assert k.recrossed_down and k.nonmonotone and k.n_up_crossings == 1
    assert k.sustained_k is None


def test_nonmonotone_flag_and_sustained_crossing():
    k = kstar.compute(L7, [-2, -1, -1.5, 0.2, -0.1, 0.4, 0.9])
    assert k.nonmonotone and k.n_up_crossings == 2 and k.n_down_crossings == 1
    assert abs(k.k_star - (2 + (1.5 / 1.7) * 2)) < 1e-12
    assert k.sustained_k == 16.0


def test_kaplan_meier_hand_example():
    km = kstar.kaplan_meier([1, 2, 2, 3, 32], [True, True, False, True, False],
                            population="t")
    # S(1)=4/5=0.8; S(2)=0.8*(1-1/4)=0.6; S(3)=0.6*(1-1/2)=0.3 -> median 3
    assert [round(s, 6) for _, s in km.curve] == [1.0, 0.8, 0.6, 0.3]
    assert km.median == 3 and km.n_censored == 2


def test_median_among_crossers_is_labelled_diagnostic_and_drops_censored():
    ks = [kstar.compute([0, 1, 2], m) for m in ([-1, 1, 1], [-1, -1, 1], [-1, -1, -1])]
    assert kstar.median_among_crossers(ks) == 1.0     # crossers at 0.5 and 1.5
    km = kstar.km_from_kstars(ks, initially_wrong_only=True)
    assert km.n_censored == 1


# ---------------------------------------------------------------------------
# 5. bootstrap multiplicity (P33-005)
# ---------------------------------------------------------------------------

def _pair_rows(vals):
    rows = []
    for tpl, d in vals.items():
        rows += [{"site_id": tpl + "s", "template": tpl, "condition": "rule", "m_seq": d},
                 {"site_id": tpl + "s", "template": tpl, "condition": "norule", "m_seq": 0.0}]
    return rows


def test_bootstrap_keeps_duplicate_cluster_weight_hand_example():
    from collections import defaultdict
    rows = _pair_rows({"tA": 1.0, "tB": 3.0})
    b = defaultdict(list)
    for r in rows:
        b[r["template"]].append(r)
    draw = AN._draw_rows(b, sorted(b), [0, 0, 1])           # tA twice, tB once
    assert abs(AN.paired_rule_effect(draw) - 5 / 3) < 1e-12


def test_old_dict_pairing_collapsed_the_duplicate():
    rows = _pair_rows({"tA": 1.0, "tB": 3.0})
    tA = [r for r in rows if r["template"] == "tA"]
    tB = [r for r in rows if r["template"] == "tB"]
    untagged = tA + tA + tB                                  # the old resample
    assert AN.paired_rule_effect(untagged) == 2.0           # wrong: weight lost


def test_no_interval_below_eight_clusters():
    assert AN.cluster_bootstrap(_pair_rows({f"t{i}": float(i) for i in range(7)}),
                                AN.paired_rule_effect) is None
    iv = AN.cluster_bootstrap(_pair_rows({f"t{i}": float(i) for i in range(12)}),
                              AN.paired_rule_effect, B=300)
    assert iv is not None and iv.lo <= iv.point <= iv.hi and iv.n_clusters == 12


def test_holm_hand_example():
    assert AN.holm({"a": .01, "b": .04, "c": .03}) == {"a": .03, "c": .06, "b": .06}


# ---------------------------------------------------------------------------
# 6. tokenizer-specific fertility (P33-009)
# ---------------------------------------------------------------------------

def test_fertility_is_computed_per_distinct_tokenizer():
    from p33 import fertility
    fake = FakeScorer()
    loaders = {"A-base": ("tokA", lambda t: len(fake.ids(t))),
               "A-inst": ("tokA", lambda t: len(fake.ids(t))),
               "B": ("tokB", lambda t: len(t))}
    rows = fertility.compute(list(loaders), ["dom"], ["d50s1"],
                             tokenizer_loader=lambda m: loaders[m])
    toks = {r["tokenizer_id"] for r in rows}
    assert toks == {"tokA", "tokB"}
    a = [r for r in rows if r["tokenizer_id"] == "tokA"][0]
    assert a["models"] == "A-base|A-inst"
    b_id = [r for r in rows if r["tokenizer_id"] == "tokB" and r["lexicon"] == "identity"][0]
    assert abs(b_id["tok_per_char"] - 1.0) < 1e-12
    assert all(k in a for k in ("tokens", "chars", "rel_fertility_vs_identity", "fragmentation"))


# ---------------------------------------------------------------------------
# 7. BPE-boundary scoring, no silent zero (P32-001 / P33-001)
# ---------------------------------------------------------------------------

def test_check_pair_refuses_every_degenerate_case():
    for a, b, exc in (([1, 2, 3], [1, 2, 3], IdenticalCandidates),
                      ([1, 2], [1, 2, 3], ZeroLengthSpan),
                      ([1, 2, 3], [1, 2], ZeroLengthSpan),
                      ([5], [6], NoContext)):
        try:
            check_pair(a, b)
        except exc:
            continue
        raise AssertionError(f"{a} vs {b} did not raise {exc.__name__}")
    assert check_pair([1, 2, 3], [1, 2, 4]) == 2


def test_merged_candidate_is_measured_not_zeroed():
    """`('` + `#` fuses into one token in the fake tokenizer, as in Qwen's BPE,
    in both grammar families."""
    fs = FakeScorer()
    for prefix in ("RULE\n\n(function(){ $S('", "RULE\n\n$S '"):
        assert len(fs.ids(prefix + "#")) == len(fs.ids(prefix)), prefix   # merged
        ps = fs.score_pair_detailed(prefix, "#", ".")
        assert ps.merged and ps.n_tok_correct == 1 and ps.n_tok_competitor == 1
        assert ps.m_seq != 0.0 and ps.k_common == len(fs.ids(prefix)) - 1


def test_old_phase3_scorer_now_raises_instead_of_returning_zero():
    import inspect
    from phase3 import models
    src = inspect.getsource(models.HFModel.sequence_logprob)
    code = "\n".join(l.split("#")[0] for l in src.splitlines())   # drop comments
    assert "raise ValueError" in code and "return 0.0" not in code


def test_canonical_scorer_has_no_silent_zero_branch():
    import inspect
    from phase3_2 import margins
    src = inspect.getsource(margins.TokenScorer.score_pair_detailed)
    code = "\n".join(l.split("#")[0] for l in src.splitlines())
    assert "return 0.0" not in code and "check_pair" in code
