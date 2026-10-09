"""EXPLORATORY (not preregistered): KM median shots for initially-wrong sites, pooled over models,
by grammar family x mapping density (d25/d50/d75) and by family x stratum. Read-only."""
import csv, sys
from collections import defaultdict
rows = [r for r in csv.DictReader(open(sys.argv[1])) if r["record_type"] == "site" and r["status"] == "ok"
        and r["already_correct"] == "False"]

def km_median(items):            # items: (time, event)
    items = sorted(items)
    n, s, i = len(items), 1.0, 0
    while i < len(items):
        t = items[i][0]
        d = sum(1 for x in items[i:] if x[0] == t and x[1])
        c = sum(1 for x in items[i:] if x[0] == t)
        if d:
            s *= 1 - d / n
            if s <= 0.5:
                return t
        n -= c
        i += c
    return None

def summarise(key):
    g = defaultdict(list)
    for r in rows:
        ev = r["censored"] == "False" and r["k_star"] != ""
        t = float(r["k_star"]) if ev else float(r.get("top_rung") or 32)
        g[key(r)].append((t, ev))
    for k in sorted(g):
        it = g[k]
        med = km_median(it)
        cens = sum(1 for _t, e in it if not e) / len(it)
        print(f"  {' / '.join(k):22s} n={len(it):5d}  KM median {'>32' if med is None else f'{med:5.2f}'}  censored {cens:.0%}")

print("By grammar family x share of remapped symbols (lexicon d25/d50/d75):")
summarise(lambda r: (r["family"], r["lexicon"][:3]))
print("By grammar family x role (stratum):")
summarise(lambda r: (r["family"], r["stratum"]))
print("By grammar family x model kind:")
summarise(lambda r: (r["family"], "instruct" if "nstruct" in r["model"] else "base"))
