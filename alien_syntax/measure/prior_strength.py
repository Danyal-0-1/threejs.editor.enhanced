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
import math
import os
import random
import sys

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


def score_program(model, tok, text: str, prefix: str, device) -> tuple[float, int, int]:
    """(total NLL in nats, scored token count, character count)."""
    import torch
    full = prefix + text
    ids = tok(full, return_tensors="pt", add_special_tokens=True).input_ids.to(device)
    n_prefix = 0
    if prefix:
        n_prefix = len(tok(prefix, add_special_tokens=True).input_ids) - 1
    with torch.no_grad():
        logits = model(ids).logits
    logprobs = torch.log_softmax(logits[0, :-1].float(), dim=-1)
    targets = ids[0, 1:]
    picked = logprobs.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    picked = picked[n_prefix:]                 # score only the program itself
    return float(-picked.sum().item()), int(picked.numel()), len(text)


def paired_bootstrap(deltas: list[float], rounds: int = BOOTSTRAP) -> tuple[float, float]:
    rng = random.Random(SEED)
    n = len(deltas)
    means = []
    for _ in range(rounds):
        means.append(sum(deltas[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return means[int(0.025 * rounds)], means[int(0.975 * rounds)]


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

    print("| model | lexicon | NLL/token | NLL/char | ΔNLL/token | ΔNLL/char | "
          "95% CI (Δ/char) | reading |")
    print("|---|---|---|---|---|---|---|---|")

    for repo in args.models:
        try:
            tok = AutoTokenizer.from_pretrained(repo)
            model = AutoModelForCausalLM.from_pretrained(
                repo, torch_dtype=torch.float32).to(device).eval()
        except Exception as exc:                              # pragma: no cover
            print(f"| `{repo}` | — | — | — | — | — | — | skipped: "
                  f"{type(exc).__name__} |")
            continue

        per_item: dict[str, list[tuple[float, int, int]]] = {}
        for name, programs in corpora.items():
            per_item[name] = [score_program(model, tok, p, args.prefix, device)
                              for p in programs]

        def summarise(name: str) -> tuple[float, float]:
            rows = per_item[name]
            return (sum(r[0] for r in rows) / sum(r[1] for r in rows),
                    sum(r[0] for r in rows) / sum(r[2] for r in rows))

        base_tok, base_chr = summarise("identity")
        for name in corpora:
            n_tok, n_chr = summarise(name)
            if name == "identity":
                print(f"| `{repo}` | `identity` (3DOM) | {n_tok:.4f} | {n_chr:.4f} "
                      f"| — | — | — | baseline |")
                continue
            deltas = [a[0] / a[2] - b[0] / b[2]
                      for a, b in zip(per_item[name], per_item["identity"])]
            lo, hi = paired_bootstrap(deltas)
            d_tok, d_chr = n_tok - base_tok, n_chr - base_chr
            # The pre-committed reading rule, applied mechanically.
            if d_chr <= 0.05 * base_chr and d_tok > 0.15 * base_tok:
                reading = "**fragmentation, not distance**"
            elif d_chr > 0.15 * base_chr:
                reading = "genuine prior distance"
            else:
                reading = "small / inconclusive"
            print(f"| `{repo}` | `{name}` | {n_tok:.4f} | {n_chr:.4f} | "
                  f"{d_tok:+.4f} | {d_chr:+.4f} | [{lo:+.4f}, {hi:+.4f}] | "
                  f"{reading} |")

        del model
        if device == "cuda":
            torch.cuda.empty_cache()

    print("\n**Reading rule** (pre-committed, applied mechanically above): a large "
          "Δ per token with a small Δ per character means the apparent alienness "
          "is mostly token fragmentation, not pretraining distance. Such a "
          "candidate must not be reported as more alien; it is more EXPENSIVE.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
