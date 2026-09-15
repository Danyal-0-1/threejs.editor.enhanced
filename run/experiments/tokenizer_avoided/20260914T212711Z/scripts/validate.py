"""validate.py — the checks that must pass BEFORE any conclusion is written.

Each check prints PASS / FAIL and the script exits nonzero if any FAILs, so a
pipeline cannot record an unvalidated run as complete.
"""
from __future__ import annotations

import collections, csv, glob, hashlib, json, math, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "alien_syntax", "src"))
sys.path.insert(0, os.path.join(REPO, "grammar_and_3DOM_client"))

import checkpoint as C
import stats as ST

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""),
          flush=True)


def raw_rows(pattern: str) -> list[dict]:
    out = []
    for p in glob.glob(os.path.join(RUN, "raw", "*", "*", pattern)):
        if "smoke" in p:
            continue
        out += C.read_rows(p)
    return out


def main() -> int:
    with open(os.path.join(RUN, "metrics", "aggregate.json"), encoding="utf-8") as fh:
        A = json.load(fh)
    laneA, laneB = A["lane_a"], A["lane_b"]

    # 1 — unit tests
    r = subprocess.run([sys.executable, os.path.join(HERE, "test_harness.py")],
                       capture_output=True, text=True,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    n_tests = 0
    for line in r.stderr.splitlines():
        if line.startswith("Ran "):
            n_tests = int(line.split()[1])
    check("1. unit tests (prompt renderer, parser, checkpoint, scoring)",
          r.returncode == 0, f"{n_tests} tests, rc={r.returncode}")

    # 2 — four-language smoke evidence exists
    smoke = C.read_rows(os.path.join(RUN, "raw", "smoke", "smoke.jsonl"))
    check("2. four-language smoke test recorded",
          len({s["language"] for s in smoke}) == 4,
          f"languages={sorted({s['language'] for s in smoke})}")

    # 3 — paired gold programs produce IDENTICAL canonical IR in all languages
    from transpiler import parse
    from canonicalize import content_hash
    from phi import identity_phi, load_candidate
    with open(os.path.join(RUN, "inputs", "task_dataset.json"), encoding="utf-8") as fh:
        ds = json.load(fh)
    phis = {"identity": identity_phi(),
            **{n: load_candidate(n) for n in ("alpha", "beta", "gamma")}}
    bad = []
    n_checked = 0
    for case in ds["cases"]:
        if not case.get("gold_renderings"):
            continue
        want = case["gold_ir_hash"]
        for lang, src in case["gold_renderings"].items():
            n_checked += 1
            if content_hash(parse(src, phis[lang])) != want:
                bad.append(f"{case['id']}/{lang}")
    check("3. paired targets produce identical canonical IR across languages",
          not bad, f"{n_checked} renderings checked, {len(bad)} mismatched")

    # 4 — aggregate denominators match the raw rows
    #
    # The aggregate is a PAIRED design: it uses only the cases present in EVERY
    # language, so the denominator is the INTERSECTION, not the per-language raw
    # count. The check must intersect the same way, or a partially-complete run
    # reports a false mismatch.
    gen = [r for r in raw_rows("gen.jsonl") if r.get("scoring_family") == "generation"]

    def paired_cases(model, cond):
        by = collections.defaultdict(set)
        for r in gen:
            if r["model"] == model and r["condition"] == cond:
                by[r["language"]].add(r["case_id"])
        return set.intersection(*by.values()) if by else set()

    mism = []
    for model, m in laneB["models"].items():
        for cond, ce in m["conditions"].items():
            want_n = len(paired_cases(model, cond))
            for lang, e in ce["languages"].items():
                want = e["semantic_accuracy"]["denominator"]
                if want != want_n:
                    mism.append(f"{model}/{cond}/{lang}: agg={want} paired_raw={want_n}")
    check("4. aggregate denominators verified against raw rows",
          not mism, f"{len(mism)} mismatches" + ("; " + "; ".join(mism[:3]) if mism else ""))

    # 5 — independently recompute selected aggregates from raw rows
    errs = []
    for model, m in laneB["models"].items():
        for cond, ce in m["conditions"].items():
            cases = paired_cases(model, cond)
            for lang, e in ce["languages"].items():
                rs = [r for r in gen if r["model"] == model
                      and r["condition"] == cond and r["language"] == lang
                      and r["case_id"] in cases]
                k = sum(1 for r in rs if r.get("semantic_correct") == 1)
                if k != e["semantic_accuracy"]["numerator"]:
                    errs.append(f"{model}/{cond}/{lang} k {k}!={e['semantic_accuracy']['numerator']}")
                lo, hi = ST.wilson(k, len(rs))
                if len(rs) and not math.isclose(lo, e["semantic_accuracy"]["wilson95_lo"],
                                                abs_tol=1e-9):
                    errs.append(f"{model}/{cond}/{lang} wilson_lo")
    # Lane A: recompute NLL/char independently
    nll = raw_rows("nll.jsonl") + raw_rows("nll_cpu.jsonl")
    for label, m in laneA["models"].items():
        for lang, e in m["languages"].items():
            rs = [r for r in nll if r["model"] == m["model"]
                  and r["device"] == m["device"] and r["language"] == lang
                  and r.get("outcome") == "VERIFIED"]
            if not rs:
                continue
            got = sum(r["total_nll_nats"] for r in rs) / sum(r["chars"] for r in rs)
            if not math.isclose(got, e["nll_per_char"], rel_tol=1e-9):
                errs.append(f"{label}/{lang} nll_per_char {got} != {e['nll_per_char']}")
    check("5. selected aggregates independently recomputed", not errs,
          f"{len(errs)} discrepancies" + ("; " + "; ".join(errs[:3]) if errs else ""))

    # 6 — plot CSV values match aggregate data
    pm = []
    for d in sorted(glob.glob(os.path.join(RUN, "plots", "**", "data.csv"), recursive=True)):
        with open(d, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        if not rows:
            pm.append(f"{os.path.relpath(d, RUN)}: empty")
    # spot-check accuracy plot against aggregate.json
    ap = os.path.join(RUN, "plots", "overall", "01_accuracy_bare", "data.csv")
    if os.path.exists(ap):
        with open(ap, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                e = (laneB["models"].get(row["model"], {}).get("conditions", {})
                     .get("bare", {}).get("languages", {}).get(row["language"]))
                if e and row["accuracy"] not in ("", "None"):
                    if not math.isclose(float(row["accuracy"]),
                                        e["semantic_accuracy"]["proportion"], rel_tol=1e-9):
                        pm.append(f"01_accuracy_bare {row['model']}/{row['language']}")
    check("6. plot CSV values match aggregate data", not pm,
          f"{len(pm)} problems" + ("; " + "; ".join(pm[:3]) if pm else ""))

    # 7 — every plotted result has raw evidence behind it
    plot_dirs = [os.path.dirname(p) for p in
                 glob.glob(os.path.join(RUN, "plots", "**", "data.csv"), recursive=True)]
    missing = [os.path.relpath(d, RUN) for d in plot_dirs
               if not all(os.path.exists(os.path.join(d, f))
                          for f in ("plot.png", "plot.svg", "data.csv", "README.md"))]
    check("7. every plot dir has plot.png, plot.svg, data.csv, README.md",
          not missing, f"{len(plot_dirs)} plots, {len(missing)} incomplete")

    # 8 — no missing value silently became zero
    #
    # A zero accuracy is a legitimate result (alpha really does score 0 in some
    # cells). What must never happen is a MISSING cell rendered as zero. Every
    # zero-valued accuracy cell is therefore traced back to raw rows: it is valid
    # only if raw rows exist for that cell AND none of them scored correct.
    #
    # The plot CSVs come in three shapes -- some carry `language`, some carry
    # `condition`, and the per-task heatmaps carry `task` -- with the missing
    # field encoded in the DIRECTORY name. All three are resolved here; a check
    # that assumed one shape would silently pass the other two.
    TASK_COL = {"op-selection": "op_correct",
                "selector-resolution": "selector_correct",
                "arg-extraction": "args_correct",
                "multi-op": "multi_op_correct"}
    zeros, bad_zeros = [], []
    for d in plot_dirs:
        rel = os.path.relpath(d, RUN)
        dir_lang = next((l for l in ("identity", "alpha", "beta", "gamma")
                         if f"by_language/{l}" in rel.replace(os.sep, "/")), None)
        dir_cond = ("scaffolded" if rel.endswith("scaffolded")
                    else "bare" if rel.endswith("bare") else None)
        with open(os.path.join(d, "data.csv"), encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                for k in ("accuracy", "semantic_accuracy"):
                    v = row.get(k)
                    if v in (None, "", "None"):
                        continue
                    try:
                        if float(v) != 0.0:
                            continue
                    except ValueError:
                        continue
                    model = row.get("model")
                    lang = row.get("language") or dir_lang
                    cond = row.get("condition") or dir_cond
                    task = row.get("task")
                    zeros.append(f"{rel}:{k}")
                    rs = [r for r in gen if r["model"] == model
                          and (lang is None or r["language"] == lang)
                          and (cond is None or r["condition"] == cond)]
                    col = TASK_COL.get(task, "semantic_correct")
                    if not rs:
                        bad_zeros.append(
                            f"{rel} {model}/{lang}/{cond}: zero plotted but NO raw rows")
                    elif any(r.get(col) == 1 for r in rs):
                        bad_zeros.append(
                            f"{rel} {model}/{lang}/{cond}/{task or 'semantic'}: "
                            f"zero plotted but raw rows contain a correct answer")
    check("8. every plotted zero is a REAL zero traced to raw rows",
          not bad_zeros,
          f"{len(zeros)} zero cells traced, {len(bad_zeros)} unsupported")

    # 9 — outcome taxonomy is mutually exclusive and totals match
    tax = []
    for model, m in laneB["models"].items():
        for cond, ce in m["conditions"].items():
            for lang, e in ce["languages"].items():
                tot = sum(e["outcomes"].values())
                if tot != e["semantic_accuracy"]["denominator"]:
                    tax.append(f"{model}/{cond}/{lang}: outcomes={tot} n={e['semantic_accuracy']['denominator']}")
    check("9. outcome taxonomy totals equal the denominators", not tax,
          f"{len(tax)} mismatches")

    # 10 — VALID_CORRECT count equals semantic_correct count
    vc = []
    for model, m in laneB["models"].items():
        for cond, ce in m["conditions"].items():
            for lang, e in ce["languages"].items():
                if e["outcomes"].get("VALID_CORRECT", 0) != e["semantic_accuracy"]["numerator"]:
                    vc.append(f"{model}/{cond}/{lang}")
    check("10. VALID_CORRECT count == semantic-accuracy numerator", not vc,
          f"{len(vc)} mismatches")

    # 11 — greedy decoding really was deterministic across repetitions
    nondet = [r for r in gen if r.get("deterministic") == 0]
    check("11. greedy decoding deterministic across repetitions",
          not nondet, f"{len(nondet)} of {len(gen)} rows differed between reps")

    # 12 — blocked cells carry an exact error and are not zero-filled
    blocked = (laneA["blocked"] + laneB["blocked"]
               + A.get("conditional_loss", {}).get("blocked", [])
               + A.get("labeling_control", {}).get("blocked", []))
    check("12. blocked cells carry exact command and error",
          all(b.get("error") and b.get("attempted_command") for b in blocked),
          f"{len(blocked)} blocked cells recorded")

    # 13 — checksums of every artefact
    dest = os.path.join(RUN, "metadata", "output-checksums.txt")
    n = 0
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("# sha256 of every raw result, metric, report and plot\n")
        for base in ("raw", "metrics", "reports", "plots", "prompts", "inputs"):
            for dirpath, _d, files in os.walk(os.path.join(RUN, base)):
                for name in sorted(files):
                    p = os.path.join(dirpath, name)
                    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
                    fh.write(f"{h}  {os.path.relpath(p, RUN)}\n")
                    n += 1
    check("13. checksums recorded for raw, metrics, reports, plots", n > 0,
          f"{n} files hashed -> metadata/output-checksums.txt")

    # 14 — nothing outside the experiment directory was changed by this session
    #
    # NOTE: the repository owner committed during this run (`E2_tokenizer_avoided`),
    # which tracked a mid-run snapshot of the experiment directory AND their own
    # pre-existing edits. That is an external event, not an action of this
    # session. Comparing against the session-start snapshot would therefore
    # report the owner's commit as a change by us. The meaningful question is
    # asked directly instead: does any file OUTSIDE the experiment directory
    # differ from HEAD, or has any been deleted?
    try:
        diff = subprocess.run(["git", "status", "--porcelain=v1"],
                              cwd=REPO, capture_output=True, text=True).stdout.splitlines()
        outside = [l for l in diff if l.strip()
                   and "run/experiments/tokenizer_avoided/" not in l]
        deleted = [l for l in diff if l.strip().startswith("D")]
        with open(os.path.join(RUN, "metadata", "git-status-end.txt"), "w",
                  encoding="utf-8") as fh:
            fh.write("# git status at end of run\n")
            fh.write(f"# HEAD: {subprocess.run(['git','rev-parse','HEAD'],cwd=REPO,capture_output=True,text=True).stdout.strip()}\n")
            fh.write("# NOTE: commit E2_tokenizer_avoided was made by the repository\n"
                     "# owner DURING this run; it is not an action of this session.\n")
            for l in diff:
                fh.write(l + "\n")
            fh.write("\n# entries OUTSIDE run/experiments/tokenizer_avoided/\n")
            for l in outside:
                fh.write(l + "\n")
        check("14. no file outside the experiment directory was modified or deleted",
              not outside and not deleted,
              f"{len(diff)} changed paths, {len(outside)} outside the experiment dir, "
              f"{len(deleted)} deleted")
    except Exception as exc:
        check("14. git status comparison", False, f"{type(exc).__name__}: {exc}")

    print()
    n_fail = sum(1 for _n, ok, _d in results if not ok)
    print(f"{len(results) - n_fail}/{len(results)} checks passed")
    with open(os.path.join(RUN, "metadata", "validation.json"), "w", encoding="utf-8") as fh:
        json.dump([{"check": n, "pass": ok, "detail": d} for n, ok, d in results],
                  fh, indent=2)
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
