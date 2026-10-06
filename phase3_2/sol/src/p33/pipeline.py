"""pipeline.py — plan, then score: Arm A and the primary/extinction experiment.

Order of operations inside every runner, and why:

  1. `splits.enforce_config`   BEFORE anything is enumerated -- a held-out cell
                               is refused before its sites are even listed.
  2. `shards.assert_compatible` -- a resume under a different config is refused.
  3. `build_plan`              -- deterministic, order-independent selection.
  4. per model: load ONCE, verify the loaded revision equals the pin, score
     every pending cell, write each cell atomically, release GPU memory.
  5. the job manifest is RUNNING from the first second and ends COMPLETE,
     PARTIAL (some cells failed, e.g. OOM) or INTERRUPTED (SIGTERM / SIGUSR1 /
     Slurm timeout). Finished cells are never lost; resume skips them.

Every row carries the cell's split label (DEVELOPMENT / HELDOUT / ...), its
model revision, tokenizer id, prompt hash and -- for the ladder -- the exact
demonstration ids, order and hash.
"""

from __future__ import annotations

import json
import os
import signal
from collections import Counter, defaultdict
from dataclasses import dataclass, field

import phi as P

from phase3_2 import prompts, sampling, sites2 as S, templates as TM
from phase3_2.backends import BACKENDS
from phase3_2.margins import ScoringError, build_prefix

from p33 import SCHEMA_VERSION
from p33 import config as CFG
from p33 import demos as D
from p33 import provenance, registry, shards, splits

# ---------------------------------------------------------------------------
# interruption
# ---------------------------------------------------------------------------


class Interrupted(Exception):
    pass


_STOP = {"flag": False, "signal": None}


def _handler(signum, _frame):
    _STOP["flag"] = True
    _STOP["signal"] = signum


def install_signal_handlers() -> None:
    """SIGTERM (scancel / preemption), SIGUSR1 (Slurm --signal before timeout),
    SIGINT. The handler only sets a flag; the loop stops between sites, so the
    cell in progress is abandoned (its temp file never becomes a shard)."""
    for s in (signal.SIGTERM, signal.SIGUSR1, signal.SIGINT):
        try:
            signal.signal(s, _handler)
        except (ValueError, OSError):
            pass


def check_stop() -> None:
    if _STOP["flag"]:
        raise Interrupted(f"signal {_STOP['signal']}")


def reset_stop() -> None:
    _STOP["flag"] = False
    _STOP["signal"] = None


# ---------------------------------------------------------------------------
# plan
# ---------------------------------------------------------------------------

_PHI_CACHE: dict[str, P.PhiMap] = {}


def phi(pid: str) -> P.PhiMap:
    if pid not in _PHI_CACHE:
        _PHI_CACHE[pid] = P.load_candidate(pid)
    return _PHI_CACHE[pid]


@dataclass
class Plan:
    sites: dict[tuple[str, str], list]           # (family, lexicon) -> sites
    expected: Counter                            # available per (fam, lex, stratum)
    dropped: list
    grid: list[dict]
    classes: dict[str, "splits.CellClass"]
    rendered: dict[tuple[str, str], dict[str, str]] = field(default_factory=dict)

    def all_sites(self) -> list:
        return [s for k in sorted(self.sites) for s in self.sites[k]]


def build_plan(cfg: "CFG.RunConfig", *, site_limit: int,
               run_dir: str | None = None) -> Plan:
    classes = splits.enforce_config(cfg, run_dir=run_dir)      # (1) refuse first
    ident = P.identity_phi()
    temps = TM.build_templates()
    pool, rendered = [], {}
    for fam in sorted(cfg.families):
        be = BACKENDS[fam]
        for lx in sorted(cfg.lexicons):
            L = phi(lx)
            rmap = {}
            for t in temps:
                text = be.render(t.ir, L)
                rmap[t.template_id] = text
                pool += [s for s in S.classify(text, L, be, template_id=t.template_id,
                                               identity=ident) if s.is_usable]
            rendered[(fam, lx)] = rmap
    kept, dropped = sampling.dedupe_within_cells(pool)
    expected = Counter(sampling.cell_key(s) for s in kept)
    n_cells = sum(1 for v in expected.values() if v)
    if site_limit and site_limit < n_cells:
        raise ValueError(f"site_limit {site_limit} cannot cover the {n_cells} "
                         f"materially available cells; raise it or use 0")
    chosen = sampling.balanced(kept, site_limit, dedupe=False)
    sampling.assert_balanced(chosen, families=cfg.families, expected=expected)
    by_cell: dict[tuple[str, str], list] = defaultdict(list)
    for s in sorted(chosen, key=sampling.canonical_key):
        by_cell[(sampling.family_of(s), s.phi_id)].append(s)
    grid = sampling.structural_grid(pool, families=cfg.families, lexicons=cfg.lexicons)
    return Plan(dict(by_cell), expected, dropped, grid, classes, rendered)


def chunks(seq: list, n: int) -> list[list]:
    return [seq[i:i + n] for i in range(0, len(seq), max(n, 1))]


def assigned_models(models: list[str], task: int | None, n_tasks: int | None) -> list[str]:
    if task is None:
        return list(models)
    n = n_tasks or len(models)
    return [m for i, m in enumerate(models) if i % n == task]


def revision_for(model: str, pins: dict) -> str:
    rev = pins.get(model, {}).get("revision")
    if not rev:
        raise RuntimeError(f"{model} is not pinned. Run `p33 prefetch` (or "
                           f"`prefetch --verify-only`) to write model_pins.json.")
    return rev


@dataclass
class Cell:
    key: str
    fields: dict
    sites: list
    model: str
    family: str
    lexicon: str
    condition: str


def _cells(cfg, plan, model, revision, experiment, kinds, site_source) -> list[Cell]:
    out = []
    for (fam, lx) in sorted(site_source):
        for kind in kinds:
            for ci, chunk in enumerate(chunks(site_source[(fam, lx)], cfg.chunk_size)):
                fields = {"experiment": experiment, "config_hash": cfg.config_hash(),
                          "model": model, "revision": revision, "family": fam,
                          "lexicon": lx, "condition": kind, "chunk": ci,
                          "site_ids_sha": CFG.sha256_json([s.site_id for s in chunk])}
                out.append(Cell(shards.cell_key(fields), fields, chunk, model,
                                fam, lx, kind))
    return out


def arm_a_cells(cfg, plan, model, revision) -> list[Cell]:
    return _cells(cfg, plan, model, revision, "arm_a",
                  list(cfg.arm_a["conditions"]), plan.sites)


def primary_site_source(cfg, plan_full: Plan) -> dict:
    """The primary experiment uses its own balanced subset (`primary.site_limit`)."""
    flat = plan_full.all_sites()
    lim = int(cfg.primary.get("site_limit", 0))
    exp = Counter(sampling.cell_key(s) for s in flat)
    if lim and lim < sum(1 for v in exp.values() if v):
        raise ValueError(f"primary.site_limit {lim} cannot cover {len(exp)} cells")
    chosen = sampling.balanced(flat, lim, dedupe=False)
    sampling.assert_balanced(chosen, families=sorted({sampling.family_of(s) for s in flat}),
                             expected=exp)
    by: dict = defaultdict(list)
    for s in sorted(chosen, key=sampling.canonical_key):
        by[(sampling.family_of(s), s.phi_id)].append(s)
    return dict(by)


def primary_cells(cfg, plan, model, revision) -> list[Cell]:
    kinds = ["ladder"] + list(cfg.primary.get("paraphrases", []))
    return _cells(cfg, plan, model, revision, "primary", kinds,
                  primary_site_source(cfg, plan))


# experiment registry: name -> (cells_fn(cfg, plan, model, rev), score_fn, model_filter)
EXPERIMENTS: dict[str, tuple] = {}


def register(name: str, cells_fn, score_fn, model_filter=None) -> None:
    EXPERIMENTS[name] = (cells_fn, score_fn, model_filter or (lambda m: True))


def models_for(cfg, experiment: str) -> list[str]:
    flt = EXPERIMENTS[experiment][2]
    return [m for m in cfg.models if flt(m)]


def expected_keys(cfg, plan, pins, experiment) -> list[str]:
    cells_fn = EXPERIMENTS[experiment][0]
    return sorted(c.key for m in models_for(cfg, experiment)
                  for c in cells_fn(cfg, plan, m, revision_for(m, pins)))


# ---------------------------------------------------------------------------
# rows
# ---------------------------------------------------------------------------

def _base_row(cfg, cell, site, scorer, cc, pb) -> dict:
    ms = registry.REGISTRY.get(cell.model)
    return {
        "schema_version": SCHEMA_VERSION, "run_id": cfg.run_id, "stage": cfg.stage,
        "split": cc.label, "split_kind": cc.kind, "cell_key": cell.key,
        "model": cell.model, "model_kind": ms.kind if ms else "fake",
        "model_family": ms.family if ms else "fake",
        "model_size_b": ms.size_b if ms else 0.0,
        "model_revision": scorer.revision, "tokenizer_id": scorer.tokenizer_id,
        "dtype": getattr(scorer, "dtype", cfg.dtype),
        "family": cell.family, "lexicon": site.phi_id,
        "template": site.template_id, "site_id": site.site_id,
        "terminal": site.terminal_id, "role": site.role, "stratum": S.stratum(site),
        "occurrence": site.occurrence, "char_offset": site.char_offset,
        "correct": site.correct, "competitor": site.competitor,
        "condition": cell.condition if pb is None else pb.condition,
        "prompt_sha": pb.sha if pb else None,
        "prompt_chars": len(pb.text) if pb else None,
    }


def _score_into(row: dict, scorer, prefix: str, site) -> dict:
    try:
        ps = scorer.score_pair_detailed(prefix, site.correct, site.competitor)
        row.update({"status": "ok", "exclusion_reason": None,
                    "m_seq": ps.m_seq, "logp_correct": ps.logp_correct,
                    "logp_competitor": ps.logp_competitor, "tie": ps.tie,
                    "k_common": ps.k_common, "merged": ps.merged,
                    "n_tok_correct": ps.n_tok_correct,
                    "n_tok_competitor": ps.n_tok_competitor,
                    "n_prefix_tokens": ps.n_prefix_tokens,
                    "first_div_correct": ps.first_div_correct_str,
                    "first_div_competitor": ps.first_div_competitor_str,
                    "fp32_head": ps.fp32_head})
    except ScoringError as exc:
        # NEVER a silent 0.0: the row exists, says why, and carries no margin
        row.update({"status": "excluded",
                    "exclusion_reason": f"{type(exc).__name__}: {exc}"[:300],
                    "m_seq": None, "logp_correct": None, "logp_competitor": None,
                    "tie": None, "k_common": None, "merged": None,
                    "n_tok_correct": None, "n_tok_competitor": None,
                    "n_prefix_tokens": None, "first_div_correct": None,
                    "first_div_competitor": None, "fp32_head": None})
    return row


def score_arm_a_cell(cfg, cell: Cell, scorer, plan: Plan, nll_cache: dict) -> list[dict]:
    rows = []
    cc = plan.classes[f"{cell.family}/{cell.lexicon}/{cell.model}"]
    counter = lambda t: len(scorer.ids(t))  # noqa: E731
    for site in cell.sites:
        check_stop()
        L = phi(site.phi_id)                                   # P33-006: per site
        pb = prompts.bundle(cell.condition, L, count_tokens=counter)
        prompts.assert_prompt_matches(site, L, pb)
        prefix = build_prefix(site, rule=pb.text)
        row = _base_row(cfg, cell, site, scorer, cc, pb)
        row["prompt_tokens"] = counter(pb.text)
        row["row_key"] = f"{cell.key}|{site.site_id}"
        _score_into(row, scorer, prefix, site)
        if cfg.arm_a.get("program_nll", True):
            if site.program not in nll_cache:
                nll_cache[site.program] = scorer.program_nll(site.program)
            nl = nll_cache[site.program]
            row.update({"program_nll": nl["nll"],
                        "program_nll_per_char": nl["nll_per_char"],
                        "program_n_tokens": nl["n_scored"] + 1})
        rows.append(row)
    return rows


def score_primary_cell(cfg, cell: Cell, scorer, plan: Plan, _cache=None) -> list[dict]:
    rows = []
    cc = plan.classes[f"{cell.family}/{cell.lexicon}/{cell.model}"]
    ladder = list(cfg.primary["ladder"])
    rendered = plan.rendered[(cell.family, cell.lexicon)]
    order = D.pool_order(list(rendered), cfg.seeds["demo_order"],
                         f"{cell.family}/{cell.lexicon}")
    order_sha = CFG.sha256_json(order)
    for site in cell.sites:
        check_stop()
        L = phi(site.phi_id)
        if cell.condition == "ladder":
            pb = prompts.bundle("rule", L)
            prompts.assert_prompt_matches(site, L, pb)
            demos = D.for_site(site, rendered, order, max(ladder))
            leaks = D.audit(site, demos, opening=D.common_opening(rendered))
            if leaks:
                raise AssertionError(f"demonstration leak for {site.site_id}: {leaks}")
            for k in ladder:
                ds = demos.first(k)
                prefix = build_prefix(site, rule=pb.text, shots=k, examples=list(ds.texts))
                row = _base_row(cfg, cell, site, scorer, cc, pb)
                row.update({"row_key": f"{cell.key}|{site.site_id}|ladder|{k:03d}",
                            "kind": "ladder", "rung": k, "demo_ids": list(ds.ids),
                            "demo_set_sha": ds.sha, "demo_order_sha": order_sha,
                            "demo_seed": cfg.seeds["demo_order"]})
                rows.append(_score_into(row, scorer, prefix, site))
        else:
            pb = prompts.bundle(cell.condition, L)
            prompts.assert_prompt_matches(site, L, pb)
            row = _base_row(cfg, cell, site, scorer, cc, pb)
            row.update({"row_key": f"{cell.key}|{site.site_id}|{cell.condition}",
                        "kind": "paraphrase", "rung": 0})
            rows.append(_score_into(row, scorer, build_prefix(site, rule=pb.text), site))
    return rows


# ---------------------------------------------------------------------------
# the runner
# ---------------------------------------------------------------------------

def write_plan_artifacts(run_dir: str, plan: Plan, experiment: str) -> None:
    """Site plan, exclusion audit and structural grid -- idempotent."""
    out = os.path.join(run_dir, "manifests", f"plan_{experiment}.json")
    blob = {"sites": [{"site_id": s.site_id, "family": sampling.family_of(s),
                       "lexicon": s.phi_id, "template": s.template_id,
                       "terminal": s.terminal_id, "stratum": S.stratum(s),
                       "prefix_len": len(s.prefix)} for s in plan.all_sites()],
            "dropped": [d.__dict__ for d in plan.dropped],
            "grid": plan.grid,
            "expected": {f"{f}/{l}/{st}": n for (f, l, st), n in sorted(plan.expected.items())},
            "classes": {k: v.__dict__ for k, v in sorted(plan.classes.items())}}
    text = json.dumps(blob, sort_keys=True, indent=1)
    if os.path.exists(out):
        if CFG.sha256_json(json.load(open(out))) != CFG.sha256_json(blob):
            raise RuntimeError(f"{out} differs from the recomputed plan: the "
                               f"materials changed under an existing run")
        return
    os.makedirs(os.path.dirname(out), exist_ok=True)
    CFG.atomic_write_text(out, text)


def run(cfg: "CFG.RunConfig", run_dir: str, experiment: str, *, scorer_factory,
        pins: dict, task: int | None = None, n_tasks: int | None = None) -> str:
    """Score every pending cell of `experiment` for this task's models."""
    if experiment not in EXPERIMENTS:
        raise ValueError(f"unknown experiment {experiment!r}; known {sorted(EXPERIMENTS)}")
    cfg.validate()
    install_signal_handlers()
    CFG.ensure_run_layout(run_dir)
    shards.assert_compatible(run_dir, cfg)
    plan = build_plan(cfg, site_limit=cfg.site_limit,
                      run_dir=run_dir if cfg.stage == "heldout" else None)
    write_plan_artifacts(run_dir, plan, experiment)
    store = shards.ShardStore(run_dir, experiment)
    store.clean_temp()
    man = provenance.JobManifest(run_dir, cfg, experiment=experiment)
    cells_fn, score_fn, _flt = EXPERIMENTS[experiment]
    status = "COMPLETE"
    applies = set(models_for(cfg, experiment))
    try:
        # task i -> model i of the FULL config list; an experiment that does not
        # apply to that model (Arm B / H5 on a base model) is a no-op for the task
        for model in assigned_models(cfg.models, task, n_tasks):
            if model not in applies:
                continue
            rev = revision_for(model, pins)
            cells = cells_fn(cfg, plan, model, rev)
            todo = []
            for c in cells:
                st = store.status(c.key)
                if st.state == "corrupt":
                    store.quarantine(c.key)
                if st.state != "done":
                    todo.append(c)
            if not todo:
                continue
            scorer = scorer_factory(model)
            if scorer.revision != rev:
                raise RuntimeError(f"{model}: loaded revision {scorer.revision} "
                                   f"!= pinned {rev}")
            man.add_model(model, {"revision": scorer.revision,
                                  "tokenizer_id": scorer.tokenizer_id,
                                  "snapshot_path": getattr(scorer, "snapshot_path", None),
                                  "n_cells": len(cells), "n_todo": len(todo)})
            nll_cache: dict = {}
            for c in todo:
                check_stop()
                try:
                    rows = score_fn(cfg, c, scorer, plan, nll_cache)
                    for r in rows:
                        if r.get("prompt_sha"):
                            man.add_prompt(f"{r['lexicon']}/{r.get('condition', c.condition)}",
                                           r["prompt_sha"])
                    store.write(c.key, c.fields, rows, job=provenance.job_identity())
                except Interrupted:
                    raise
                except Exception as exc:          # incl. CUDA OOM
                    store.record_failure(c.key, c.fields, exc,
                                         job=provenance.job_identity())
                    status = "PARTIAL"
                    try:
                        import torch
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                    except Exception:
                        pass
            scorer.release()
    except Interrupted as exc:
        man.finish("INTERRUPTED", note=str(exc))
        return "INTERRUPTED"
    except Exception as exc:
        man.finish("FAILED", note=f"{type(exc).__name__}: {exc}")
        raise
    man.finish(status)
    return status


def merge(cfg: "CFG.RunConfig", run_dir: str, experiment: str, *, pins: dict):
    plan = build_plan(cfg, site_limit=cfg.site_limit,
                      run_dir=run_dir if cfg.stage == "heldout" else None)
    store = shards.ShardStore(run_dir, experiment)
    res = store.merge(expected_keys(cfg, plan, pins, experiment))
    store.write_merged(res)
    return res


register("arm_a", arm_a_cells, score_arm_a_cell)
register("primary", primary_cells, score_primary_cell)
