"""Compact summary of a held-out run's exported CSVs (read-only)."""
import csv
import os
import sys
from collections import defaultdict

RUN = sys.argv[1]
C = os.path.join(RUN, "csv")


def rd(name):
    p = os.path.join(C, f"{name}.csv")
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def short(m):
    return m.split("/")[-1].replace("Qwen2.5-Coder-", "QC-").replace("deepseek-coder-", "DS-").replace("Instruct", "I").replace("instruct", "I")


ORDER = ["Qwen/Qwen2.5-Coder-0.5B", "Qwen/Qwen2.5-Coder-0.5B-Instruct", "Qwen/Qwen2.5-Coder-1.5B",
         "Qwen/Qwen2.5-Coder-1.5B-Instruct", "Qwen/Qwen2.5-Coder-3B", "Qwen/Qwen2.5-Coder-3B-Instruct",
         "Qwen/Qwen2.5-Coder-7B", "Qwen/Qwen2.5-Coder-7B-Instruct", "Qwen/Qwen2.5-Coder-14B",
         "Qwen/Qwen2.5-Coder-14B-Instruct", "Qwen/Qwen2.5-Coder-32B", "Qwen/Qwen2.5-Coder-32B-Instruct",
         "Qwen/Qwen2.5-72B", "Qwen/Qwen2.5-72B-Instruct",
         "deepseek-ai/deepseek-coder-1.3b-base", "deepseek-ai/deepseek-coder-1.3b-instruct",
         "deepseek-ai/deepseek-coder-33b-base", "deepseek-ai/deepseek-coder-33b-instruct",
         "meta-llama/Llama-3.2-1B", "meta-llama/Llama-3.2-1B-Instruct", "bigcode/starcoder2-3b"]

# --- reversion (rule condition) per model x family, row-weighted over lexicons
re_rows = rd("rule_effect")
rev = defaultdict(lambda: [0, 0.0])
for r in re_rows:
    if r["record_type"] == "reversion":
        n = int(r["n_rows"])
        rev[(r["model"], r["family"])][0] += n
        rev[(r["model"], r["family"])][1] += n * f(r["reversion_rate"])
# --- rule effect: per model x family x control, mean over lexicons; CIs excluding zero
eff = defaultdict(list)
excl = defaultdict(lambda: [0, 0, 0])   # (pos-excluding, neg-excluding, total)
for r in re_rows:
    if r["record_type"] == "rule_effect" and r.get("stratum", "ALL") == "ALL":
        k = (r["model"], r["family"], r["control"])
        eff[k].append(f(r["mean_rule_effect"]))
        e = excl[(r["family"], r["control"])]
        e[2] += 1
        if r["ci_excludes_zero"] == "True":
            e[0 if f(r["mean_rule_effect"]) > 0 else 1] += 1
# --- KM
km = {}
shape = {}
for r in rd("kstar_survival"):
    if r["record_type"] == "km_summary":
        km[(r["model"], r["family"], r["population"])] = r
    elif r["record_type"] == "curve_shape":
        shape[(r["model"], r["family"])] = r

fams = sorted({k[1] for k in rev})
print("== Reversion rate with the rule table (rule condition), and extinction (KM median shots, initially-wrong sites)")
hdr = "model".ljust(22) + "".join(f"| {fam}: rev   KM-median [CI] cens  alreadyOK nonmono ".ljust(58) for fam in fams)
print(hdr)
for m in ORDER:
    line = short(m).ljust(22)
    for fam in fams:
        n, s = rev.get((m, fam), (0, 0))
        rr = s / n if n else float("nan")
        k = km.get((m, fam, "INITIALLY_WRONG"))
        sh = shape.get((m, fam), {})
        if k:
            med, lo, hi, cens = k["km_median"], k["ci_lo"], k["ci_hi"], f(k["censoring_rate"])
            kms = f"{f(med):.1f} [{f(lo):.1f},{f(hi):.1f}] {cens:.0%}" if f(med) is not None else f"{med} {cens:.0%}"
        else:
            kms = "n/a"
        line += f"| {rr:.3f}  {kms:24s} {f(sh.get('share_already_correct')) or 0:.2f}   {f(sh.get('share_nonmonotone')) or 0:.2f} ".ljust(58)
    print(line)

print("\n== Rule effect (rule - control), mean over lexicons, per model")
for fam in fams:
    for ctl in ("norule", "norule_lenmatched"):
        vals = [(short(m), sum(v) / len(v)) for m in ORDER for (mm, ff, cc), v in eff.items()
                if mm == m and ff == fam and cc == ctl and v]
        e = excl[(fam, ctl)]
        print(f"  {fam} vs {ctl}: " + ", ".join(f"{a} {b:+.2f}" for a, b in vals))
        print(f"     intervals excluding zero: {e[0]} positive, {e[1]} negative, of {e[2]} (model x lexicon)")

print("\n== H4: base-model risk predicts instruct reversion (held-out)")
for r in rd("h4_metrics_baselines_calibration"):
    if r.get("predictor") == "risk":
        print(f"  {short(r['pair'].split('|')[0]):14s} {r.get('family',''):4s} AUROC {f(r['auroc']):.3f}  AP {f(r['auprc']):.3f} "
              f"(prev {f(r['prevalence']):.3f})  ECE {f(r['ece']) if r.get('ece') else float('nan'):.3f}  n={r['n_rows']}")
for r in rd("h4_metrics_baselines_calibration"):
    if r.get("criterion"):
        d = f(r.get("delta"))
        print(f"  {short(r['pair'].split('|')[0]):14s} {r.get('family',''):4s} {r['criterion']:26s} {r['status']:12s}"
              + (f" delta {d:+.3f} [{f(r['ci_lo']):+.3f},{f(r['ci_hi']):+.3f}] Holm p {f(r['p_holm']):.4f}" if d is not None else f" {r.get('detail','')[:60]}"))

print("\n== Paraphrase sensitivity (reversion range across p0-p2)")
for r in rd("paraphrase"):
    if r["record_type"] == "range":
        print(f"  {short(r['model']):22s} {r['family']}: range {f(r['reversion_range']):.3f}")


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


print("\n== Arm B: free generation by the instruct models (mean over lexicons)")
print("   reach = the generated program contains the decision point; revert|reach = it wrote the OLD spelling there")
hb = [r for r in rd("arm_b_hurdle") if r.get("record_type") == "hurdle" and r.get("stratum") == "ALL"]
agg = defaultdict(lambda: defaultdict(list))
for r in hb:
    for k in ("p_reach", "p_revert_given_reach", "parse_valid_rate", "task_accuracy"):
        agg[(r["model"], r["family"])][k].append(f(r.get(k)))
if not hb:
    print("   NOT RUN")
for m in ORDER:
    for fam in fams:
        a = agg.get((m, fam))
        if a:
            print(f"  {short(m):22s} {fam}: reach {mean(a['p_reach']):.2f}   revert|reach {mean(a['p_revert_given_reach']):.2f}"
                  f"   parses {mean(a['parse_valid_rate']):.2f}   task correct {mean(a['task_accuracy']):.2f}")

print("\n== H5: respelling repairs (error reduction per changed symbol; mean over families and lexicons)")
h5 = [r for r in rd("h5_budget_outcomes") if r.get("record_type") == "arm"]
red = defaultdict(lambda: defaultdict(list))
deg = defaultdict(list)
for r in h5:
    red[r["model"]][r["arm"]].append(f(r.get("error_reduction_per_changed_symbol")))
    if r["arm"] == "targeted" and r.get("control_degradation") not in (None, ""):
        deg[r["model"]].append(f(r["control_degradation"]))
if not h5:
    print("   NOT RUN")
for m in ORDER:
    if m in red:
        a = red[m]
        print(f"  {short(m):22s} targeted {mean(a.get('targeted', [])):+.2f}   random {mean(a.get('random', [])):+.2f}"
              f"   global {mean(a.get('global', [])):+.2f}   control change (targeted) max {max(deg[m]) if deg[m] else float('nan'):+.3f}")
print("\nThe registered verdicts with intervals are in reports/HYPOTHESIS_RESULTS.md and reports/HELDOUT_RESULTS.md.")
