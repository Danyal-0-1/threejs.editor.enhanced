"""h5.py — targeted, semantics-preserving repair of risky spellings.

H5 (preregistered, confirmatory): rewriting ONLY the predicted-high-risk roles
reduces error more PER CHANGED SYMBOL than random rewriting at the same budget,
and does not degrade low-risk / non-colliding sites by more than 0.02.

THREE ARMS, one lexicon at a time
    targeted   the `budget` remapped roles with the highest mean BASE-model
               risk (-M_seq, rule condition) -- the H4 predictor, no
               instruct outcome used to choose them
    random     `budget` remapped roles drawn uniformly, repeated over the
               deterministic seeds in `seeds.h5_random`
    global     every remapped role (the PA-Tool-style "rename everything")

WHAT A REPAIR DOES. A repaired role takes its spelling from the `beta`
lexicon, whose alphabet is disjoint from CSS. The familiar spelling then no
longer means anything at that role -- a silent SEMANTIC collision becomes a
loud LEXICAL one. I7 is respected: repairing T_CLASS_SIGIL also moves
T_CHAIN_OP to the same new spelling.

THE PROOF. Every accepted repair must preserve canonical IR over the COMPLETE
corpus -- the 62 Phase 1 programs plus the 80 templates, in BOTH grammar
families, with no sampling and no tolerance:

    hash(ir) == hash(parse(render(ir, L), L)) == hash(parse(render(ir, L'), L'))

A repair that fails is rejected before anything is scored.

OUTCOMES, both reported:
    reversion     M_seq < 0 at the site                     (preregistered wording)
    silent error  reversion AND the site is still SEMANTIC  (the harm that matters)
"""

from __future__ import annotations

import copy
import json
import os
import random
from collections import defaultdict

import canonicalize as C
import generate_corpus as G
import phi as P

from phase3_2 import prompts, sites2 as S, templates as TM
from phase3_2.backends import BACKENDS
from phase3_2.margins import build_prefix

from p33 import config as CFG
from p33 import pipeline as PL
from p33 import registry

REPAIR_SOURCE = "beta"
FOLLOWER = {"T_CLASS_SIGIL": "T_CHAIN_OP"}          # I7
_CONTEXT: dict = {}                                  # set by prepare()


def _blob(pid: str) -> dict:
    from phase3_2._vendor import CANDIDATES
    return json.load(open(os.path.join(CANDIDATES, f"phi_{pid}.json"), encoding="utf-8"))


def remapped_roles(L: P.PhiMap) -> list[str]:
    ident = P.identity_phi(L.table)
    return sorted(t.id for t in L.table.terminals if t.substitutable
                  and t.id not in FOLLOWER.values()
                  and L.spelling(t.id) != ident.spelling(t.id))


def repaired_phi(base_pid: str, roles: list[str], tag: str) -> P.PhiMap:
    src = P.load_candidate(REPAIR_SOURCE)
    blob = copy.deepcopy(_blob(base_pid))
    for tid in roles:
        blob["map"][tid]["to"] = src.spelling(tid)
        if tid in FOLLOWER:
            blob["map"][FOLLOWER[tid]]["to"] = src.spelling(tid)
    blob["phi_id"] = f"{base_pid}__{tag}"
    L2 = P.validate_phi(blob, P.load_terminals())       # V1-V8 or raise
    PL._PHI_CACHE[L2.phi_id] = L2
    return L2


def proof_corpus() -> list:
    ident = P.identity_phi()
    from phase3_2.backends import DOM
    irs = [DOM.parse(p, ident) for p in G.phase1_programs("positive", ident)]
    irs += [t.ir for t in TM.build_templates()]
    return irs


def ir_proof(L: P.PhiMap, L2: P.PhiMap) -> dict:
    """Exhaustive canonical-IR equality. No sampling, no tolerance."""
    corpus = proof_corpus()
    bad = []
    n = 0
    for fam, be in sorted(BACKENDS.items()):
        for i, ir in enumerate(corpus):
            n += 1
            h0 = C.content_hash(ir)
            try:
                h1 = C.content_hash(be.parse(be.render(ir, L), L))
                h2 = C.content_hash(be.parse(be.render(ir, L2), L2))
            except Exception as exc:
                bad.append(f"{fam}#{i}: {type(exc).__name__}")
                continue
            if not (h0 == h1 == h2):
                bad.append(f"{fam}#{i}: hash mismatch")
    return {"n_checked": n, "n_mismatch": len(bad), "examples": bad[:5],
            "passed": not bad, "families": sorted(BACKENDS)}


def define_arms(L: P.PhiMap, risk_by_role: dict[str, float], *, budget: int,
                seeds: list[int]) -> list[tuple[str, int, list[str]]]:
    cands = remapped_roles(L)
    b = min(budget, len(cands))
    ranked = sorted(cands, key=lambda t: (-risk_by_role.get(t, float("-inf")), t))
    arms = [("targeted", 0, sorted(ranked[:b]))]
    for sd in seeds:
        arms.append(("random", sd, sorted(random.Random(sd).sample(cands, b))))
    arms.append(("global", 0, sorted(cands)))
    return arms


def prepare(cfg, run_dir: str) -> dict:
    """Choose arms from BASE-model Arm A risk, prove every repair, record both.

    Idempotent: if `manifests/h5_arms.json` exists it is re-derived and must
    match exactly, so a resumed H5 run cannot silently change its arms.
    """
    merged = os.path.join(run_dir, "merged", "arm_a.jsonl")
    if not os.path.exists(merged):
        raise RuntimeError("H5 needs merged Arm A results in this run (base-model risk)")
    rows = [json.loads(l) for l in open(merged, encoding="utf-8") if l.strip()]
    risk = defaultdict(list)
    for r in rows:
        s = registry.REGISTRY.get(r["model"])
        if r["condition"] == "rule" and r["status"] == "ok" and (s is None or s.kind == "base"):
            risk[(r["family"], r["lexicon"], r["model"], r["terminal"])].append(-r["m_seq"])
    arms, proofs = {}, {}
    budget = int(cfg.h5.get("budget", 3))
    for fam in sorted(cfg.families):
        for lx in sorted(cfg.lexicons):
            L = PL.phi(lx)
            for inst in sorted(cfg.models):
                spec = registry.REGISTRY.get(inst)
                base = spec.pair if spec and spec.kind == "instruct" else inst
                rbr = {t: sum(v) / len(v) for (f, l, m, t), v in risk.items()
                       if f == fam and l == lx and m == base}
                for arm, sd, roles in define_arms(L, rbr, budget=budget,
                                                  seeds=list(cfg.seeds["h5_random"])):
                    tag = f"h5_{arm}_{sd}"
                    L2 = repaired_phi(lx, roles, tag)
                    if (lx, tag) not in proofs:
                        proofs[(lx, tag)] = ir_proof(L, L2)
                    if not proofs[(lx, tag)]["passed"]:
                        raise RuntimeError(f"repair {lx}/{tag} changes canonical IR: "
                                           f"{proofs[(lx, tag)]['examples']}")
                    arms.setdefault(f"{fam}/{lx}/{inst}", []).append(
                        {"arm": arm, "seed": sd, "roles": roles, "repaired_phi": L2.phi_id,
                         "n_changed": len(roles)})
    out = {"arms": arms, "proofs": {f"{k[0]}/{k[1]}": v for k, v in sorted(proofs.items())},
           "repair_source": REPAIR_SOURCE, "budget": budget}
    p = os.path.join(run_dir, "manifests", "h5_arms.json")
    if os.path.exists(p):
        if CFG.sha256_json(json.load(open(p))) != CFG.sha256_json(out):
            raise RuntimeError("h5_arms.json differs from the re-derived arms; "
                               "the Arm A data or code changed under this run")
    else:
        CFG.atomic_write_text(p, json.dumps(out, indent=1, sort_keys=True))
    _CONTEXT.clear()
    _CONTEXT.update(out)
    return out


def _is_instruct(model: str) -> bool:
    s = registry.REGISTRY.get(model)
    return s is None or s.kind == "instruct"


def h5_cells(cfg, plan, model, revision):
    if not _CONTEXT:
        raise RuntimeError("call h5.prepare(cfg, run_dir) before enumerating H5 cells")
    out = []
    for (fam, lx), sites in sorted(plan.sites.items()):
        for a in _CONTEXT["arms"].get(f"{fam}/{lx}/{model}", []):
            for ci, chunk in enumerate(PL.chunks(sites, cfg.chunk_size)):
                fields = {"experiment": "h5", "config_hash": cfg.config_hash(),
                          "model": model, "revision": revision, "family": fam,
                          "lexicon": lx, "condition": f"{a['arm']}_{a['seed']}",
                          "chunk": ci, "roles": a["roles"],
                          "site_ids_sha": CFG.sha256_json([s.site_id for s in chunk])}
                c = PL.Cell(PL.shards.cell_key(fields), fields, chunk, model, fam, lx,
                            f"{a['arm']}_{a['seed']}")
                c.fields["repaired_phi"] = a["repaired_phi"]
                out.append(c)
    return out


def score_h5_cell(cfg, cell, scorer, plan, _cache=None) -> list[dict]:
    L2 = PL.phi(cell.fields["repaired_phi"])
    be = BACKENDS[cell.family]
    roles = set(cell.fields["roles"])
    cc = plan.classes[f"{cell.family}/{cell.lexicon}/{cell.model}"]
    ident = P.identity_phi()
    temps = {t.template_id: t for t in TM.build_templates()}
    pb = prompts.bundle("rule", L2)
    rep_cache: dict = {}
    rows = []
    for s in cell.sites:
        PL.check_stop()
        if s.template_id not in rep_cache:
            text = be.render(temps[s.template_id].ir, L2)
            rep_cache[s.template_id] = {(x.terminal_id, x.occurrence): x for x in
                                        S.classify(text, L2, be, template_id=s.template_id,
                                                   identity=ident)}
        s2 = rep_cache[s.template_id].get((s.terminal_id, s.occurrence))
        row = {"schema_version": "p33/1", "run_id": cfg.run_id, "stage": cfg.stage,
               "split": cc.label, "cell_key": cell.key,
               "row_key": f"{cell.key}|{s.site_id}",
               "model": cell.model, "model_revision": scorer.revision,
               "tokenizer_id": scorer.tokenizer_id, "family": cell.family,
               "lexicon": cell.lexicon, "repaired_phi": L2.phi_id,
               "condition": cell.condition,
               "arm": cell.condition.rsplit("_", 1)[0],
               "seed": int(cell.condition.rsplit("_", 1)[1]),
               "roles_changed": sorted(roles), "n_changed": len(roles),
               "orig_site_id": s.site_id, "template": s.template_id,
               "terminal": s.terminal_id, "stratum": S.stratum(s),
               "repaired_role": s.terminal_id in roles, "prompt_sha": pb.sha}
        if s2 is None:
            row.update({"status": "excluded", "exclusion_reason": "site vanished after repair"})
        else:
            row.update({"collision_after": s2.collision.value,
                        "correct_after": s2.correct, "competitor_after": s2.competitor})
            if s2.collision.value == "none":
                row.update({"status": "excluded", "exclusion_reason": "no contrast after repair"})
            else:
                prompts.assert_prompt_matches(s2, L2, pb)
                PL._score_into(row, scorer, build_prefix(s2, rule=pb.text), s2)
                if row["status"] == "ok":
                    row["reverted_after"] = row["m_seq"] < 0
                    row["silent_error_after"] = row["reverted_after"] and \
                        s2.collision.value == "semantic"
        rows.append(row)
    return rows


PL.register("h5", h5_cells, score_h5_cell, _is_instruct)
