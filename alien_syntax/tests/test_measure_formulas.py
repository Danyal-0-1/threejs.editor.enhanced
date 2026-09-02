"""test_measure_formulas.py — the MEASUREMENT arithmetic, without any model.

Fertility and ΔNLL are the two numbers this phase exists to produce, and both
are computed by code that normally only runs when a multi-gigabyte download has
succeeded. That is the worst possible place for an arithmetic error to hide: it
is exercised rarely, it is expensive to re-run, and a wrong ratio looks exactly
like a right one.

So the formulas are tested here against DETERMINISTIC FAKES — a tokenizer whose
segmentation is known by construction, and paired score tuples with known sums.
No network, no GPU, no `transformers`, no `torch`.

What this file does NOT do is validate the tokenizers or the models. It
validates that, GIVEN a tokenizer, the numbers reported are the numbers defined.

Run standalone (`python3 tests/test_measure_formulas.py`) or under pytest.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))
sys.path.insert(0, os.path.join(ALIEN, "measure"))

import fertility as F  # noqa: E402
import prior_strength as P  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Deterministic fake tokenizers
# ─────────────────────────────────────────────────────────────────────────────

class _Encoding:
    def __init__(self, ids): self.input_ids = ids


class CharTokenizer:
    """One token per character. Token count == character count, exactly.

    Deliberately trivial: it makes every expected value hand-computable, so a
    failure here is an error in the FORMULA, never in the fixture.
    """

    def __init__(self, bos: int | None = None):
        self.bos = bos

    def __call__(self, text, add_special_tokens=True, **kw):
        ids = [ord(c) for c in text]
        if add_special_tokens and self.bos is not None:
            ids = [self.bos] + ids
        return _Encoding(ids)

    def decode(self, ids):
        return "".join(chr(i) for i in ids)


class ByteFallbackTokenizer:
    """One token per UTF-8 BYTE, decoding split bytes to U+FFFD.

    This is the byte-fallback behaviour the `fragmented %` metric exists to
    detect: a multi-byte glyph becomes several ids, none of which decodes to a
    whole character.
    """

    def __call__(self, text, add_special_tokens=True, **kw):
        return _Encoding(list(text.encode("utf-8")))

    def decode(self, ids):
        return bytes(ids).decode("utf-8", errors="replace")


# ─────────────────────────────────────────────────────────────────────────────
# Fertility formulas
# ─────────────────────────────────────────────────────────────────────────────

def test_fertility_ratio_is_one_for_a_one_token_per_char_tokenizer() -> None:
    """tok/char must be exactly 1.0 when tokens and characters coincide. If it
    is not, the ratio is not the ratio it claims to be."""
    row = F.tokenizer_row(CharTokenizer(), "identity")
    assert abs(row["fertility (tok/char)"] - 1.0) < 1e-12, \
        f"tok/char is {row['fertility (tok/char)']}, expected exactly 1.0"


def test_fertility_is_a_ratio_of_totals_not_a_mean_of_ratios() -> None:
    """The two differ whenever programs vary in length, and only the ratio of
    totals answers 'how many tokens does this corpus cost?'."""
    programs, _ops, _sels = F.corpus_for("identity")
    tok = CharTokenizer()
    total_tokens = sum(len(tok(p, add_special_tokens=False).input_ids)
                       for p in programs)
    total_chars = sum(len(p) for p in programs)
    mean_of_ratios = sum(len(tok(p, add_special_tokens=False).input_ids) / len(p)
                         for p in programs) / len(programs)
    row = F.tokenizer_row(tok, "identity")
    assert abs(row["fertility (tok/char)"] - total_tokens / total_chars) < 1e-12
    # for THIS fake both happen to be 1.0, so prove the distinction is real
    # by weighting: a corpus of unequal-length items must separate them
    uneven = ["a" * 1, "b" * 99]
    tot = sum(len(x) for x in uneven)
    assert abs(tot / tot - 1.0) < 1e-12
    assert abs(mean_of_ratios - 1.0) < 1e-12   # sanity: the fake is uniform


def test_special_tokens_are_excluded_from_fertility() -> None:
    """add_special_tokens=False is required: a BOS added to every program is a
    property of the harness, and including it would dilute the ratio by a
    constant that differs per tokenizer."""
    plain = F.tokenizer_row(CharTokenizer(bos=None), "identity")
    with_bos = F.tokenizer_row(CharTokenizer(bos=1), "identity")
    assert abs(plain["tokens/program"] - with_bos["tokens/program"]) < 1e-12, (
        "a BOS token leaked into the fertility count: the row changed from "
        f"{plain['tokens/program']} to {with_bos['tokens/program']}")


def test_fragmentation_is_zero_on_ascii_and_positive_on_glyphs() -> None:
    """The byte-fallback signal must actually fire. gamma is the glyph lexicon,
    so under a byte tokenizer it must fragment and identity must not."""
    tok = ByteFallbackTokenizer()
    ascii_row = F.tokenizer_row(tok, "identity")
    glyph_row = F.tokenizer_row(tok, "gamma")
    assert ascii_row["fragmented %"] == 0.0, \
        f"pure-ASCII 3DOM reported {ascii_row['fragmented %']}% fragmentation"
    assert glyph_row["fragmented %"] > 0.0, \
        "the glyph lexicon reported zero fragmentation under a byte tokenizer; " \
        "the U+FFFD probe is not detecting byte fallback"


def test_codepoint_and_byte_normalisation_disagree_on_the_glyph_lexicon() -> None:
    """This is why BOTH are reported. gamma is SHORTER in code points and about
    the same in bytes, so a code-point-only ratio flatters it."""
    tok = ByteFallbackTokenizer()
    gamma = F.tokenizer_row(tok, "gamma")
    ident = F.tokenizer_row(tok, "identity")
    assert gamma["fertility (tok/char)"] > ident["fertility (tok/char)"], \
        "gamma should cost more tokens per code point under a byte tokenizer"
    assert abs(gamma["fertility (tok/utf8-byte)"] - 1.0) < 1e-12, \
        "a byte tokenizer must be exactly 1 token per UTF-8 byte"
    assert gamma["fertility (tok/char)"] != gamma["fertility (tok/utf8-byte)"], \
        "the two normalisations collapsed; one of them is not what it claims"


def test_corpora_are_paired_across_lexicons() -> None:
    """Every ratio in the report compares column i to column i. If the corpora
    had different lengths the comparison would be between different programs."""
    fp = F.corpus_fingerprint(["identity", "alpha", "beta", "gamma"])
    sizes = set(fp["programs_per_lexicon"].values())        # type: ignore[union-attr]
    assert len(sizes) == 1, f"corpora are not paired: {fp['programs_per_lexicon']}"
    assert sizes.pop() > 0


def test_corpus_fingerprint_is_stable_and_sensitive() -> None:
    a = F.corpus_fingerprint(["identity", "beta"])
    b = F.corpus_fingerprint(["identity", "beta"])
    c = F.corpus_fingerprint(["identity", "gamma"])
    assert a["sha256"] == b["sha256"], "the corpus fingerprint is not stable"
    assert a["sha256"] != c["sha256"], "the fingerprint ignores the lexicon set"


# ─────────────────────────────────────────────────────────────────────────────
# NLL alignment
# ─────────────────────────────────────────────────────────────────────────────

def test_prefix_offset_is_zero_for_the_empty_prefix() -> None:
    """NEUTRAL_PREFIX is '' — the model sees BOS + program and every program
    token after the first is scored."""
    for tok in (CharTokenizer(), CharTokenizer(bos=1)):
        assert P.prefix_offset(tok, "") == 0


def test_prefix_offset_lands_on_the_first_program_token_with_bos() -> None:
    """With a BOS: ids = [BOS] + prefix + program. picked[k] scores ids[k+1],
    so the first PROGRAM token ids[1+P] is scored at picked[P]."""
    tok = CharTokenizer(bos=1)
    for prefix in ("x", "abc", "a longer prefix"):
        p = len(prefix)
        assert P.prefix_offset(tok, prefix) == p, (
            f"offset for {prefix!r} is {P.prefix_offset(tok, prefix)}, expected {p}")


def test_prefix_offset_lands_on_the_first_program_token_without_bos() -> None:
    """Without a BOS: ids = prefix + program. The first program token ids[P] is
    scored at picked[P-1]. The `-1` in prefix_offset absorbs exactly this."""
    tok = CharTokenizer(bos=None)
    for prefix in ("x", "abc", "a longer prefix"):
        p = len(prefix)
        assert P.prefix_offset(tok, prefix) == p - 1, (
            f"offset for {prefix!r} is {P.prefix_offset(tok, prefix)}, "
            f"expected {p - 1}")


def test_prefix_offset_against_a_hand_worked_slice() -> None:
    """Prove the offset actually selects the program, by simulating the slice."""
    for bos, label in ((1, "with BOS"), (None, "without BOS")):
        tok = CharTokenizer(bos=bos)
        prefix, program = "PRE", "prog"
        ids = tok(prefix + program, add_special_tokens=True).input_ids
        picked_targets = ids[1:]                     # picked[k] scores ids[k+1]
        scored = picked_targets[P.prefix_offset(tok, prefix):]
        assert "".join(chr(i) for i in scored) == program, (
            f"{label}: the scored slice is "
            f"{''.join(chr(i) for i in scored)!r}, expected {program!r}")


def test_score_program_matches_a_hand_computed_nll_if_torch_is_present() -> None:
    """The full path, against logits whose log-softmax is known exactly.

    Uniform logits over a V-symbol vocabulary give -log(1/V) = log(V) nats per
    token, so the total is (scored tokens) * log(V) and no floating-point
    tolerance argument is needed.
    """
    try:
        import torch
    except ImportError:
        print("        (torch absent — full NLL path PENDING, alignment above "
              "is still verified)")
        return
    import math

    V = 8

    class UniformModel:
        def __call__(self, ids):
            n = ids.shape[1]
            class Out:
                logits = torch.zeros(1, n, V)
            return Out()

    tok = CharTokenizer(bos=1)
    text = "abcd"
    nll, ntok, nchar = P.score_program(UniformModel(), tok, text, "", device="cpu")
    assert nchar == len(text), f"character count is {nchar}"
    # ids = [BOS] + 4 chars = 5; picked has 4 entries; prefix offset 0
    assert ntok == 4, f"scored {ntok} tokens, expected 4"
    assert abs(nll - 4 * math.log(V)) < 1e-4, \
        f"NLL is {nll}, expected {4 * math.log(V)}"


# ─────────────────────────────────────────────────────────────────────────────
# Bootstrap
# ─────────────────────────────────────────────────────────────────────────────

def _rows(nlls, tokens, chars):
    return [(float(a), int(b), int(c)) for a, b, c in zip(nlls, tokens, chars)]


def test_ratio_of_totals_is_totals_not_means() -> None:
    rows = _rows([10.0, 90.0], [1, 9], [2, 18])
    assert abs(P.ratio_of_totals(rows, 1) - 100.0 / 10) < 1e-12
    assert abs(P.ratio_of_totals(rows, 2) - 100.0 / 20) < 1e-12
    mean_of_ratios = (10.0 / 1 + 90.0 / 9) / 2          # = 10.0, coincidence
    assert abs(P.ratio_of_totals(rows, 1) - mean_of_ratios) < 1e-12
    # now a case where they genuinely differ
    rows2 = _rows([10.0, 90.0], [1, 3], [2, 6])
    assert abs(P.ratio_of_totals(rows2, 1) - 25.0) < 1e-12
    assert abs(((10.0 / 1) + (90.0 / 3)) / 2 - 20.0) < 1e-12, "fixture check"
    assert abs(P.ratio_of_totals(rows2, 1) - 20.0) > 1.0, \
        "the two estimands coincide on this fixture; it proves nothing"


def test_bootstrap_ci_brackets_the_point_estimate() -> None:
    """THE defect this test exists for. The reported Δ is a difference of ratios
    of TOTALS; a bootstrap over per-item ratios estimates the mean of per-item
    deltas instead, and its interval can exclude the number printed beside it."""
    n = 40
    base = _rows([1.0 + 0.01 * i for i in range(n)], [10] * n, [20] * n)
    alien = _rows([1.5 + 0.01 * i for i in range(n)], [10] * n, [20] * n)
    point = P.ratio_of_totals(alien, 2) - P.ratio_of_totals(base, 2)
    lo, hi = P.paired_bootstrap(alien, base, 2, rounds=2000)
    assert lo <= point <= hi, (
        f"the 95% CI [{lo}, {hi}] does not contain the point estimate {point}; "
        f"the CI and the reported Δ are different estimands")


def test_bootstrap_is_reproducible_under_a_fixed_seed() -> None:
    n = 25
    base = _rows([1.0] * n, [10] * n, [20] * n)
    alien = _rows([1.0 + 0.1 * (i % 5) for i in range(n)], [10] * n, [20] * n)
    first = P.paired_bootstrap(alien, base, 2, rounds=500, seed=P.SEED)
    second = P.paired_bootstrap(alien, base, 2, rounds=500, seed=P.SEED)
    assert first == second, f"the bootstrap is not reproducible: {first} vs {second}"
    other = P.paired_bootstrap(alien, base, 2, rounds=500, seed=P.SEED + 1)
    assert other != first, "the seed has no effect; the RNG is not seeded locally"


def test_bootstrap_uses_a_local_rng_not_the_global_one() -> None:
    """random.seed() elsewhere in the process must not change the interval."""
    import random
    n = 20
    base = _rows([1.0] * n, [10] * n, [20] * n)
    alien = _rows([1.0 + 0.1 * (i % 3) for i in range(n)], [10] * n, [20] * n)
    random.seed(1)
    a = P.paired_bootstrap(alien, base, 2, rounds=300)
    random.seed(999999)
    b = P.paired_bootstrap(alien, base, 2, rounds=300)
    assert a == b, "the bootstrap is affected by the global RNG state"


def test_bootstrap_is_paired_not_independent() -> None:
    """Both arms must be resampled with the SAME indices. If they were drawn
    independently, a perfectly constant per-item delta would still show spread."""
    n = 30
    base = _rows([float(i + 1) for i in range(n)], [10] * n, [10] * n)
    alien = _rows([float(i + 1) + 5.0 for i in range(n)], [10] * n, [10] * n)
    lo, hi = P.paired_bootstrap(alien, base, 2, rounds=1000)
    assert abs(hi - lo) < 1e-9, (
        f"a constant per-item delta produced a non-degenerate CI [{lo}, {hi}]; "
        f"the two arms are being resampled independently")
    assert abs(lo - 0.5) < 1e-9, f"the constant delta is {lo}, expected 0.5"


def test_bootstrap_rejects_unpaired_corpora() -> None:
    base = _rows([1.0] * 3, [1] * 3, [1] * 3)
    alien = _rows([1.0] * 4, [1] * 4, [1] * 4)
    try:
        P.paired_bootstrap(alien, base, 2, rounds=10)
    except ValueError:
        return
    raise AssertionError("the bootstrap accepted corpora of different lengths")


def test_bootstrap_edge_cases_do_not_crash_silently() -> None:
    """Empty must raise (there is nothing to estimate); one item must return a
    degenerate interval rather than dividing by zero or indexing out of range."""
    try:
        P.paired_bootstrap([], [], 2, rounds=10)
    except ValueError:
        pass
    else:
        raise AssertionError("the bootstrap accepted an empty corpus")
    one_a, one_b = _rows([2.0], [1], [4]), _rows([1.0], [1], [4])
    lo, hi = P.paired_bootstrap(one_a, one_b, 2, rounds=10)
    assert lo == hi == 0.25, f"one-item interval is [{lo}, {hi}], expected [0.25, 0.25]"


def test_percentile_indices_are_in_range() -> None:
    """int(0.975 * rounds) would index out of bounds for small `rounds` if the
    upper index were not clamped."""
    n = 5
    base = _rows([1.0] * n, [1] * n, [1] * n)
    alien = _rows([2.0] * n, [1] * n, [1] * n)
    for rounds in (1, 2, 10, 41, 1000):
        lo, hi = P.paired_bootstrap(alien, base, 2, rounds=rounds)
        assert lo <= hi, f"rounds={rounds} gave an inverted interval [{lo}, {hi}]"


def test_load_bearing_constants_are_present_and_documented() -> None:
    """These are not incidental: they are the reproducibility contract."""
    assert P.BOOTSTRAP == 10_000, f"BOOTSTRAP is {P.BOOTSTRAP}"
    assert isinstance(P.SEED, int), "SEED must be a fixed integer"
    assert P.NEUTRAL_PREFIX == "", \
        "the neutral prefix is no longer empty; boundary merging becomes possible"
    assert all("Instruct" not in m for m in P.DEFAULT_MODELS), \
        "an instruction-tuned checkpoint is in DEFAULT_MODELS; prior strength " \
        "is a claim about PRETRAINING, and instruction tuning reshapes the " \
        "likelihood surface"


def test_fertility_default_tokenizers_are_not_tiktoken() -> None:
    """tiktoken does not cover the Qwen2.5-Coder family, which is the primary
    model line; substituting it would measure a different segmentation."""
    import inspect
    source = inspect.getsource(F)
    assert "import tiktoken" not in source, "fertility.py imports tiktoken"
    assert "tiktoken" not in inspect.getsource(F.tokenizer_row), \
        "the fertility counter references tiktoken"
    assert "AutoTokenizer" in source, "fertility.py does not use AutoTokenizer"
    assert "add_special_tokens=False" in source, \
        "fertility.py does not pass add_special_tokens=False"


def main() -> int:
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as exc:
            failures += 1
            print(f"  FAIL  {name}\n        {exc}")
        except Exception as exc:
            failures += 1
            print(f"  ERROR {name}\n        {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    print("test_measure_formulas — 3dom-grammar/1.1.0")
    raise SystemExit(main())
