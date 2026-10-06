"""fertility.py — token fertility for EVERY distinct tokenizer, not just one.

DEFECT P33-009. `run_arm_a.py` computed fertility with `args.models[0]` only,
then reported it as if it held for every model in the run. Fertility is a
property of a TOKENIZER, and the whole multi-family design exists because
tokenizers differ. Here every requested model's tokenizer is fingerprinted;
models sharing a tokenizer (e.g. a base/instruct pair) are grouped, and each
distinct tokenizer gets its own measurement.

PER (tokenizer, family, lexicon)
    tokens, chars, tok_per_char           over the 80 rendered templates
    rel_fertility_vs_identity             tok/char relative to 3DOM itself
    rel_token_count                       total tokens relative to identity
    fragmentation                         mean tokens per substitutable
                                          spelling, each tokenised in isolation
Candidate-level tokenisation -- merged flag, first divergent token, tokens
per candidate -- is recorded per site in the Arm A rows, where it belongs.

Tokenizers only: no model weights are loaded here, so this runs on CPU.
"""

from __future__ import annotations

import phi as P

from phase3_2 import templates as TM
from phase3_2.backends import BACKENDS


def load_tokenizer(model_id: str, pins: dict):
    """(tokenizer_id, count_fn) from the PINNED local snapshot, offline."""
    from transformers import AutoTokenizer
    from p33.scorers import resolve_snapshot, tokenizer_fingerprint
    pin = pins.get(model_id, {})
    path, _sha = resolve_snapshot(model_id, revision=pin.get("revision"),
                                  allow_patterns=pin.get("allow_patterns"))
    tok = AutoTokenizer.from_pretrained(path, local_files_only=True)
    return tokenizer_fingerprint(path), (lambda t: len(tok(t, add_special_tokens=False)["input_ids"]))


def rows_for_tokenizer(tokenizer_id: str, count, models: list[str],
                       families: list[str], lexicons: list[str]) -> list[dict]:
    temps = TM.build_templates()
    ident = P.identity_phi()
    out = []
    for fam in sorted(families):
        be = BACKENDS[fam]
        base_txt = [be.render(t.ir, ident) for t in temps]
        btok = sum(count(x) for x in base_txt)
        bchr = sum(len(x) for x in base_txt)
        for lx in ["identity"] + sorted(lexicons):
            L = ident if lx == "identity" else P.load_candidate(lx)
            txt = [be.render(t.ir, L) for t in temps]
            n = sum(count(x) for x in txt)
            c = sum(len(x) for x in txt)
            spellings = sorted({L.spelling(t.id) for t in L.table.terminals if t.substitutable})
            frag = sum(count(s) for s in spellings) / len(spellings)
            out.append({"tokenizer_id": tokenizer_id, "models": "|".join(sorted(models)),
                        "family": fam, "lexicon": lx, "tokens": n, "chars": c,
                        "tok_per_char": n / c,
                        "rel_fertility_vs_identity": (n / c) / (btok / bchr),
                        "rel_token_count": n / btok, "fragmentation": frag,
                        "n_templates": len(temps)})
    return out


def compute(models: list[str], families: list[str], lexicons: list[str], *,
            tokenizer_loader) -> list[dict]:
    """`tokenizer_loader(model) -> (tokenizer_id, count_fn)`; groups by id."""
    groups: dict[str, tuple] = {}
    for m in sorted(models):
        tid, cnt = tokenizer_loader(m)
        if tid in groups:
            groups[tid][1].append(m)
        else:
            groups[tid] = (cnt, [m])
    out = []
    for tid, (cnt, ms) in sorted(groups.items()):
        out += rows_for_tokenizer(tid, cnt, ms, families, lexicons)
    return out
