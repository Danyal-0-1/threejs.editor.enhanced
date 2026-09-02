"""prior_strength.py — the operationalisation of "reduced pretraining proximity".

    python3 measure/prior_strength.py --md
    python3 measure/prior_strength.py --models Qwen/Qwen2.5-Coder-0.5B --md

"Zero training priors" is unprovable and is never claimed anywhere in this
repository. The claim is REDUCED PRETRAINING PROXIMITY, and prior distance is a
MEASUREMENT: the base model's mean negative log-likelihood on matched programs,
with no task prompt.

    NLL_per_token = -(1/T) Σ log p(x_t | x_<t)
    NLL_per_char  = -(1/C) Σ log p(x_t | x_<t)        C = len(program) in chars
    ΔNLL          = NLL_alien − NLL_3DOM              paired, per model

WHY BOTH NORMALISATIONS, AND WHAT THEY DECIDE
    Per-TOKEN NLL is contaminated by fertility: a lexicon that fragments into
    more tokens spreads the same surprise over more steps. Per-CHARACTER NLL
    holds the string fixed and is therefore the fertility-free view.

        Δ/token LARGE and Δ/char LARGE  -> genuine prior distance
        Δ/token LARGE and Δ/char SMALL  -> the "alienness" is mostly token
                                           FRAGMENTATION, and the report says so
                                           in those words

    The selection rule in reports/CANDIDATE_SELECTION.md takes ΔNLL PER
    CHARACTER as the primary objective for exactly this reason.

CONDITIONING, fixed here and held constant across every model and lexicon:
    NEUTRAL_PREFIX = ""  — no task prompt at all; the model sees BOS + program.
    Change it only with --prefix, which stamps the value into the output table
    so a run can never be reported without its conditioning.

MODELS: BASE checkpoints, not Instruct. Instruction tuning reshapes the
likelihood surface, and what is being measured here is pretraining proximity.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import random
import sys
from typing import Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))

from phi import identity_phi, load_candidate  # noqa: E402
import generate_corpus as G  # noqa: E402

DEFAULT_MODELS = (
    "Qwen/Qwen2.5-Coder-0.5B",
    "Qwen/Qwen2.5-Coder-1.5B",
    "Qwen/Qwen2.5-Coder-3B",
    "Qwen/Qwen2.5-Coder-7B",
)
CANDIDATES = ("identity", "alpha", "beta", "gamma")
NEUTRAL_PREFIX = ""
BOOTSTRAP = 10_000
SEED = 20260910          # the CHI deadline; fixed so resamples are reproducible


def parallel_corpora(names: list[str]) -> dict[str, list[str]]:
    """Matched program pairs: index i is the same operation chain in every column."""
    ident = identity_phi()
    base = G.phase1_programs("positive", ident)
    out = {"identity": base}
    for name in names:
        if name in ("identity", "3dom"):
            continue
        phi = load_candidate(name)
        out[name] = G.generate(phi, write=False)["positive"]
    lengths = {k: len(v) for k, v in out.items()}
    if len(set(lengths.values())) != 1:
        raise SystemExit(f"corpora are not matched: {lengths}")
    return out


def prefix_offset(tok, prefix: str) -> int:
    """How many leading entries of `picked` belong to the PREFIX, not the program.

    Pulled out of score_program so the alignment can be tested against fake
    tokenizers — with and without a BOS — without loading a model. Getting this
    off by one silently scores the prefix as if it were the program, which would
    move every NLL in the study by a constant that differs per tokenizer.
    """
    if not prefix:
        return 0
    return len(tok(prefix, add_special_tokens=True).input_ids) - 1


def score_program(model, tok, text: str, prefix: str, device) -> tuple[float, int, int]:
    """(total NLL in nats, scored token count, character count).

    ALIGNMENT. `logits[t]` predicts `ids[t+1]`, so `picked[k]` is the log-prob of
    `ids[k+1]` and the sequence's FIRST token is never scored — there is nothing
    to condition it on. With an empty prefix that costs one token per program,
    identically in every lexicon, so the paired Δ is unaffected; it does mean
    `scored tokens` is one fewer than `len(ids)` and NLL/char divides by the full
    character count. Both are stated rather than silently absorbed.

    PREFIX EXCLUSION. `n_prefix` is `len(tok(prefix, add_special_tokens=True)) - 1`,
    which lands on the right offset whether or not the tokenizer prepends a BOS:
    with BOS the prefix occupies ids[1..P], program starts at ids[P+1], scored at
    picked[P]; without BOS the prefix occupies ids[0..P-1], program starts at
    ids[P], scored at picked[P-1]. The `-1` absorbs exactly that difference.

    KNOWN LIMITATION. A non-empty prefix can MERGE with the program's first
    token at the boundary (BPE), in which case no integer offset separates them
    cleanly. NEUTRAL_PREFIX is "" precisely so this cannot arise in the reported
    configuration; a non-default --prefix should be checked before it is trusted.
    """
    import torch
    full = prefix + text
    ids = tok(full, return_tensors="pt", add_special_tokens=True).input_ids.to(device)
    n_prefix = prefix_offset(tok, prefix)
    with torch.no_grad():
        logits = model(ids).logits
    logprobs = torch.log_softmax(logits[0, :-1].float(), dim=-1)
    targets = ids[0, 1:]
    picked = logprobs.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    picked = picked[n_prefix:]                 # score only the program itself
    return float(-picked.sum().item()), int(picked.numel()), len(text)


Scored = tuple[float, int, int]        # (total NLL in nats, tokens, characters)


def ratio_of_totals(rows: Sequence[Scored], denominator: int) -> float:
    """NLL per token (denominator=1) or per character (denominator=2).

    CORPUS TOTALS, not a mean of per-item ratios. A short program contributes
    fewer nats AND fewer tokens; averaging per-item ratios would weight it the
    same as a long one and silently change the estimand.
    """
    den = sum(r[denominator] for r in rows)
    if den == 0:
        raise ZeroDivisionError("empty corpus: no tokens/characters to divide by")
    return sum(r[0] for r in rows) / den


def paired_bootstrap(alien: Sequence[Scored], base: Sequence[Scored],
                     denominator: int, *, rounds: int = BOOTSTRAP,
                     seed: int = SEED) -> tuple[float, float]:
    """95% CI for ΔNLL, resampling PAIRED ITEMS and recomputing the SAME
    estimand the point estimate uses.

    WHY THIS IS NOT A BOOTSTRAP OVER PER-ITEM DELTAS
        The reported Δ is a difference of RATIOS OF TOTALS:
            Δ = Σnll_alien/Σden_alien − Σnll_base/Σden_base
        Resampling per-item ratios and averaging them estimates a DIFFERENT
        quantity — the mean of per-item deltas — whose value generally differs
        from Δ. A CI built that way can legitimately exclude the point estimate
        printed beside it, which is worse than having no CI at all.

        So each resample draws item INDICES with replacement (once, applied to
        both arms — that is what makes it paired) and recomputes Δ end to end.

    The pairing is essential: index i is the same operation chain in every
    lexicon, so the two arms share the resampled item set and the between-item
    variance cancels.
    """
    n = len(alien)
    if n != len(base):
        raise ValueError(f"unpaired corpora: {n} alien vs {len(base)} baseline")
    if n == 0:
        raise ValueError("cannot bootstrap an empty corpus")
    if n == 1:
        # Every resample is the same single pair, so the interval is degenerate.
        # Reporting it as a point rather than crashing keeps a one-item smoke
        # run readable, and the degeneracy is visible in the output.
        point = ratio_of_totals(alien, denominator) - ratio_of_totals(base, denominator)
        return point, point

    rng = random.Random(seed)
    deltas: list[float] = []
    for _ in range(rounds):
        idx = [rng.randrange(n) for _ in range(n)]
        a = [alien[i] for i in idx]
        b = [base[i] for i in idx]
        deltas.append(ratio_of_totals(a, denominator) - ratio_of_totals(b, denominator))
    deltas.sort()
    # 0-indexed percentile positions; int() truncates, which is the conventional
    # choice and is stated here rather than left to be inferred.
    lo = deltas[max(0, int(0.025 * rounds) - 1)]
    hi = deltas[min(rounds - 1, int(0.975 * rounds) - 1)]
    return lo, hi


def provenance(repo: str) -> dict[str, str]:
    """What must be recorded for a model-dependent number to be reproducible.

    A revision that cannot be resolved is recorded as 'unresolved', never
    omitted: a missing field reads as 'not applicable', which is a stronger
    claim than 'we could not determine it'.
    """
    info = {"repo": repo, "revision": "unresolved"}
    try:
        import huggingface_hub
        info["revision"] = huggingface_hub.model_info(repo).sha or "unresolved"
        info["huggingface_hub"] = huggingface_hub.__version__
    except Exception as exc:                                   # offline / gated
        info["revision_error"] = f"{type(exc).__name__}: {exc}"[:120]
    for module in ("transformers", "torch"):
        try:
            info[module] = __import__(module).__version__
        except Exception:                                      # pragma: no cover
            info[module] = "absent"
    return info


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("candidates", nargs="*", default=list(CANDIDATES))
    ap.add_argument("--models", nargs="*", default=list(DEFAULT_MODELS))
    ap.add_argument("--prefix", default=NEUTRAL_PREFIX,
                    help="fixed neutral prefix; default is the empty string")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--md", action="store_true")
    args = ap.parse_args(argv[1:])
    names = args.candidates or list(CANDIDATES)

    print("# Prior strength — base-model NLL on matched programs\n")
    print(f"- grammar: `3dom-grammar/1.1.0`")
    print(f"- conditioning: neutral prefix = {args.prefix!r} "
          f"(no task prompt), held constant across every model and lexicon")
    print(f"- checkpoints: BASE, not Instruct")
    print(f"- CI: paired bootstrap, {BOOTSTRAP} resamples, seed {SEED}\n")

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        print("**torch / transformers are not installed.** Install them and re-run:\n")
        print("    pip install torch transformers\n")
        print("Until then ΔNLL is UNMEASURED, and the primary objective of the "
              "selection rule (ΔNLL per character) has no value. The provisional "
              "winner in reports/CANDIDATE_SELECTION.md is provisional for "
              "exactly this reason.")
        return 2

    corpora = parallel_corpora(names)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if args.device == "auto" else args.device

    corpus_hash = hashlib.sha256(
        json.dumps(corpora, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    print(f"- corpus: {len(corpora['identity'])} paired programs per lexicon, "
          f"sha256 `{corpus_hash[:16]}`")
    print(f"- device: `{device}`")
    print(f"- run started: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")

    print("| model | lexicon | NLL/token | NLL/char | ΔNLL/token | ΔNLL/char | "
          "95% CI (Δ/char) | reading |")
    print("|---|---|---|---|---|---|---|---|")

    scored_models: list[str] = []
    skipped: list[str] = []
    runs: list[dict] = []

    for repo in args.models:
        try:
            tok = AutoTokenizer.from_pretrained(repo)
            model = AutoModelForCausalLM.from_pretrained(
                repo, torch_dtype=torch.float32).to(device).eval()
        except Exception as exc:                              # pragma: no cover
            skipped.append(f"{repo}: {type(exc).__name__}: {exc}")
            print(f"| `{repo}` | — | — | — | — | — | — | skipped: "
                  f"{type(exc).__name__} |")
            continue

        per_item: dict[str, list[Scored]] = {}
        for name, programs in corpora.items():
            per_item[name] = [score_program(model, tok, p, args.prefix, device)
                              for p in programs]

        base_tok = ratio_of_totals(per_item["identity"], 1)
        base_chr = ratio_of_totals(per_item["identity"], 2)
        run = {"model": provenance(repo), "device": device,
               "corpus_sha256": corpus_hash, "seed": SEED, "bootstrap": BOOTSTRAP,
               "prefix": args.prefix, "lexicons": {}}

        for name in corpora:
            n_tok = ratio_of_totals(per_item[name], 1)
            n_chr = ratio_of_totals(per_item[name], 2)
            if name == "identity":
                print(f"| `{repo}` | `identity` (3DOM) | {n_tok:.4f} | {n_chr:.4f} "
                      f"| — | — | — | baseline |")
                run["lexicons"][name] = {"nll_per_token": n_tok,
                                         "nll_per_char": n_chr}
                continue
            # CI on the SAME estimand as the point estimate (see paired_bootstrap)
            lo, hi = paired_bootstrap(per_item[name], per_item["identity"], 2)
            d_tok, d_chr = n_tok - base_tok, n_chr - base_chr
            # The reading rule, applied mechanically. NOTE: the 5%/15% cut points
            # are NOT registered in reports/CANDIDATE_SELECTION.md, which
            # pre-commits only the fertility band and the collision/parity
            # constraints. They are reported here as a reading AID and must not
            # be presented as a pre-committed decision rule until registered.
            if d_chr <= 0.05 * base_chr and d_tok > 0.15 * base_tok:
                reading = "**fragmentation, not distance**"
            elif d_chr > 0.15 * base_chr:
                reading = "genuine prior distance"
            else:
                reading = "small / inconclusive"
            print(f"| `{repo}` | `{name}` | {n_tok:.4f} | {n_chr:.4f} | "
                  f"{d_tok:+.4f} | {d_chr:+.4f} | [{lo:+.4f}, {hi:+.4f}] | "
                  f"{reading} |")
            run["lexicons"][name] = {
                "nll_per_token": n_tok, "nll_per_char": n_chr,
                "delta_nll_per_token": d_tok, "delta_nll_per_char": d_chr,
                "ci95_delta_per_char": [lo, hi], "reading": reading}

        runs.append(run)
        scored_models.append(repo)
        del model
        if device == "cuda":
            torch.cuda.empty_cache()

    print("\n**Reading rule** applied mechanically above: a large Δ per token "
          "with a small Δ per character means the apparent alienness is mostly "
          "token fragmentation, not pretraining distance. Such a candidate must "
          "not be reported as more alien; it is more EXPENSIVE. The 5%/15% cut "
          "points are a reading aid, NOT a pre-committed threshold — "
          "reports/CANDIDATE_SELECTION.md registers only the fertility band and "
          "the collision/parity constraints.")

    print("\n### Provenance\n")
    print("```json")
    print(json.dumps(runs, indent=2, ensure_ascii=False))
    print("```")

    if skipped:
        print("\n**Skipped models:**\n")
        for line in skipped:
            print(f"- `{line}`")

    if not scored_models:
        print("\n**NO MODEL WAS SCORED.** ΔNLL is UNMEASURED and the primary "
              "objective of the selection rule has no value. This is a FAILURE, "
              "not an empty result: exiting nonzero so a pipeline cannot record "
              "it as a completed phase.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
