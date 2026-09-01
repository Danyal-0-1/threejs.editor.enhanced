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
    return {
        "tokens/program": prog_tokens / len(programs),
        "tokens/operation": op_tokens / max(len(ops), 1),
        "tokens/selector": sel_tokens / max(len(selectors), 1),
        "fertility (tok/char)": prog_tokens / chars,
        "fragmented %": 100.0 * prog_frag / prog_tokens,
    }


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

    print(f"# Fertility — 3dom-grammar/1.1.0")
    print(f"\nCorpus: the 62-item parallel positive corpus, one lexicon per column. "
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

    for repo in args.tokenizers:
        try:
            tok = AutoTokenizer.from_pretrained(repo, trust_remote_code=False)
        except Exception as exc:                              # pragma: no cover
            print(f"\n_Skipped `{repo}`: {type(exc).__name__}: {exc}_")
            continue
        rows = {n: tokenizer_row(tok, n) for n in names}
        emit_table(f"Tokenizer `{repo}`", list(next(iter(rows.values()))), rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
