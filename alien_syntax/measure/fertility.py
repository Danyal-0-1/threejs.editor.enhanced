"""fertility.py — tokenizer fertility of each candidate, measured not estimated.

    python3 measure/fertility.py --md                 # needs `transformers`
    python3 measure/fertility.py --structural --md    # no models required
    python3 measure/fertility.py --tokenizers Qwen/Qwen2.5-Coder-0.5B --md

WHY THIS IS THE BINDING CONSTRAINT
    A glyph like ◬ (U+25EC) is three UTF-8 bytes, absent from code pretraining,
    and fragments into byte-fallback pieces. Applied across fifteen verbs, every
    alien program becomes materially longer IN TOKENS than its 3DOM twin: more
    sampling steps, more chances to derail, tighter context under scaffolding.
    The resulting "familiarity gap" would then be partly a LENGTH effect — the
    single most likely reason this paper gets rejected. So fertility is measured
    per tokenizer, over the full parallel corpus, and it gates candidate
    selection (CONSTRAINT 1) rather than being reported as an afterthought.

transformers.AutoTokenizer, NOT tiktoken: tiktoken does not cover the
Qwen2.5-Coder family, which is the primary model line for this study.

DEFINITIONS (fixed here, before any number exists)
    tokens/program    mean over the parallel positive corpus
    tokens/operation  mean over every emitted operation_call fragment
    tokens/selector   mean over every emitted quoted selector
    fertility ratio   total tokens / total characters (higher = worse)
    fragmented %      share of token ids whose individual decode contains
                      U+FFFD — i.e. the id carries part of a character, not a
                      whole one. This is the byte-fallback signal for both
                      byte-level BPE (Qwen) and SentencePiece byte fallback.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIEN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ALIEN, "src"))

from canonicalize import args_in_order, format_number, quote_string  # noqa: E402
from phi import identity_phi, load_candidate  # noqa: E402
from transpiler import Emitter, parse  # noqa: E402
import generate_corpus as G  # noqa: E402

# Qwen2.5-Coder is the primary model line; the frontier tokenizer is a fifth,
# deliberately different, BPE for external validity. Any gated repo needs
# `huggingface-cli login`; override the whole list with --tokenizers.
DEFAULT_TOKENIZERS = (
    "Qwen/Qwen2.5-Coder-0.5B",
    "Qwen/Qwen2.5-Coder-1.5B",
    "Qwen/Qwen2.5-Coder-3B",
    "Qwen/Qwen2.5-Coder-7B",
    "deepseek-ai/DeepSeek-V3",          # frontier tokenizer
)
CANDIDATES = ("identity", "alpha", "beta", "gamma")


def corpus_for(name: str) -> tuple[list[str], list[str], list[str]]:
    """(programs, operation fragments, quoted selectors) for one lexicon."""
    phi = load_candidate(name)
    ident = identity_phi(phi.table)
    programs = (G.phase1_programs("positive", ident) if name in ("identity", "3dom")
                else G.generate(phi, write=False)["positive"])
    emitter = Emitter(phi)
    ops: list[str] = []
    selectors: list[str] = []
    for program in programs:
        ir = parse(program, phi)
        for op in ir.ops:
            selector = quote_string(emitter.emit(op.selector))
            selectors.append(selector)
            args = ",".join(
                format_number(v) if isinstance(v, (int, float))
                else quote_string(str(v))
                for v in args_in_order(op.op, op.args))
            ops.append(f"{emitter.chain}{emitter.verb_spelling[op.op]}({args})")
    return programs, ops, selectors


def structural_row(name: str) -> dict[str, float]:
    programs, ops, selectors = corpus_for(name)
    chars = sum(len(p) for p in programs)
    utf8 = sum(len(p.encode("utf-8")) for p in programs)
    multibyte = sum(1 for p in programs for c in p if len(c.encode("utf-8")) > 1)
    return {
        "chars/program": chars / len(programs),
        "utf8 bytes/program": utf8 / len(programs),
        "bytes/char": utf8 / chars,
        "multibyte chars/program": multibyte / len(programs),
        "chars/operation": sum(len(o) for o in ops) / max(len(ops), 1),
        "chars/selector": sum(len(s) for s in selectors) / max(len(selectors), 1),
    }


def tokenizer_row(tok, name: str) -> dict[str, float]:
    programs, ops, selectors = corpus_for(name)

    def count(texts: list[str]) -> tuple[int, int]:
        """(token count, fragmented-id count) over CORPUS TOTALS.

        add_special_tokens=False: BOS/EOS are a property of the harness, not of
        the lexicon, and adding a constant to every column would dilute the very
        ratio this measurement exists to compute.
        """
        total = frag = 0
        for text in texts:
            ids = tok(text, add_special_tokens=False).input_ids
            total += len(ids)
            frag += sum(1 for i in ids if "�" in tok.decode([i]))
        return total, frag

    prog_tokens, prog_frag = count(programs)
    op_tokens, _ = count(ops)
    sel_tokens, _ = count(selectors)
    chars = sum(len(p) for p in programs)
    utf8 = sum(len(p.encode("utf-8")) for p in programs)
    return {
        "tokens/program": prog_tokens / len(programs),
        "tokens/operation": op_tokens / max(len(ops), 1),
        "tokens/selector": sel_tokens / max(len(selectors), 1),
        # Two normalisations, because they disagree exactly where it matters.
        # A glyph lexicon is SHORTER in code points and LONGER in bytes, so a
        # code-point ratio flatters it and a byte ratio penalises it. Both are
        # reported; CONSTRAINT 1 is defined on tok/char (code points).
        "fertility (tok/char)": prog_tokens / chars,
        "fertility (tok/utf8-byte)": prog_tokens / utf8,
        "fragmented %": 100.0 * prog_frag / prog_tokens,
    }


def provenance(repo: str, tok) -> dict[str, object]:
    """Everything needed to reproduce a fertility number.

    A number without its tokenizer revision is not a measurement, it is an
    anecdote. An unresolvable revision is recorded as 'unresolved' rather than
    omitted, so the gap is visible.
    """
    info: dict[str, object] = {
        "repo": repo,
        "revision": "unresolved",
        "tokenizer_class": type(tok).__name__,
        "vocab_size": getattr(tok, "vocab_size", None),
        "is_fast": getattr(tok, "is_fast", None),
        "captured_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    try:
        import huggingface_hub
        info["revision"] = huggingface_hub.model_info(repo).sha or "unresolved"
        info["huggingface_hub"] = huggingface_hub.__version__
    except Exception as exc:                                   # offline / gated
        info["revision_error"] = f"{type(exc).__name__}: {exc}"[:120]
    try:
        import transformers
        info["transformers"] = transformers.__version__
    except Exception:                                          # pragma: no cover
        info["transformers"] = "absent"
    return info


def corpus_fingerprint(names: list[str]) -> dict[str, object]:
    """Which corpus produced these numbers, as a hash rather than a promise."""
    blob = {n: corpus_for(n)[0] for n in names}
    digest = hashlib.sha256(
        json.dumps(blob, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return {"programs_per_lexicon": {n: len(v) for n, v in blob.items()},
            "sha256": digest}


def emit_table(title: str, metrics: list[str], rows: dict[str, dict[str, float]],
               baseline: str = "identity") -> None:
    print(f"\n### {title}\n")
    print("| metric | " + " | ".join(f"`{c}`" for c in rows) + " | β÷3DOM | γ÷3DOM |")
    print("|---" * (len(rows) + 3) + "|")
    for metric in metrics:
        cells = [f"{rows[c][metric]:.3f}" for c in rows]
        base = rows[baseline][metric] if baseline in rows else 0.0
        def ratio(c: str) -> str:
            if c not in rows or not base:
                return "—"
            return f"{rows[c][metric] / base:.3f}"
        print(f"| {metric} | " + " | ".join(cells) + f" | {ratio('beta')} | "
              f"{ratio('gamma')} |")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("candidates", nargs="*", default=list(CANDIDATES))
    ap.add_argument("--tokenizers", nargs="*", default=list(DEFAULT_TOKENIZERS))
    ap.add_argument("--structural", action="store_true",
                    help="character/byte statistics only; no model downloads")
    ap.add_argument("--md", action="store_true", help="markdown output")
    args = ap.parse_args(argv[1:])
    names = args.candidates or list(CANDIDATES)

    print("# Fertility — 3dom-grammar/1.1.0")
    fingerprint = corpus_fingerprint(names)
    sizes = set(fingerprint["programs_per_lexicon"].values())     # type: ignore[union-attr]
    if len(sizes) != 1:
        print(f"\n**CORPORA ARE NOT PAIRED**: "
              f"{fingerprint['programs_per_lexicon']}. Every ratio below would "
              f"compare different programs; refusing to report.")
        return 4
    print(f"\nCorpus: the {sizes.pop()}-item parallel positive corpus, one lexicon "
          f"per column, sha256 `{str(fingerprint['sha256'])[:16]}`. "
          f"`identity` is 3DOM itself.")

    structural = {n: structural_row(n) for n in names}
    emit_table("Structural (no tokenizer required)",
               list(next(iter(structural.values()))), structural)

    if args.structural:
        print("\n_Tokenizer rows not run (`--structural`). CONSTRAINT 1 of the "
              "selection rule is defined on the FERTILITY RATIO, which needs a "
              "tokenizer; the table above is a proxy and is not a substitute._")
        return 0

    try:
        from transformers import AutoTokenizer
    except ImportError:
        print("\n**transformers is not installed.** Install it and re-run:\n")
        print("    pip install transformers\n")
        print("Falling back to `--structural`; the fertility ratio is NOT "
              "reported, and CONSTRAINT 1 therefore remains UNMEASURED.")
        return 2

    measured: list[dict[str, object]] = []
    skipped: list[str] = []
    for repo in args.tokenizers:
        try:
            tok = AutoTokenizer.from_pretrained(repo, trust_remote_code=False)
        except Exception as exc:                              # pragma: no cover
            skipped.append(f"{repo}: {type(exc).__name__}: {exc}")
            print(f"\n_Skipped `{repo}`: {type(exc).__name__}: {exc}_")
            continue
        rows = {n: tokenizer_row(tok, n) for n in names}
        emit_table(f"Tokenizer `{repo}`", list(next(iter(rows.values()))), rows)
        prov = provenance(repo, tok)
        measured.append({"tokenizer": prov, "rows": rows})
        print(f"\n_Tokenizer revision `{prov['revision']}`, "
              f"transformers `{prov['transformers']}`, "
              f"class `{prov['tokenizer_class']}`._")

    print("\n### Provenance\n")
    print("```json")
    print(json.dumps({"corpus": fingerprint, "tokenizers": measured},
                     indent=2, ensure_ascii=False))
    print("```")

    if skipped:
        print("\n**Skipped tokenizers:**\n")
        for line in skipped:
            print(f"- `{line}`")

    if not measured:
        print("\n**NO TOKENIZER WAS LOADED.** The fertility ratio is UNMEASURED "
              "and CONSTRAINT 1 remains PENDING. This is a FAILURE, not an empty "
              "result: exiting nonzero so a pipeline cannot record it as a "
              "completed phase.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
