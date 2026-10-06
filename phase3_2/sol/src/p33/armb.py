"""armb.py — Arm B: unrestricted natural-language-to-DSL generation.

Arm A asks "which spelling do you prefer, given this exact prefix?". Arm B
asks "what do you actually write?". The two are not interchangeable: a model
can prefer the right spelling and never reach the site, or reach it and
revert. So Arm B reports, separately and never collapsed:

    parse validity            does the output parse at all?
    task accuracy             does it lower to the target canonical IR?
    P(O)  site reach          did the output reproduce the program up to a
                              decision site?
    P(Y|O) conditional        having reached it, did it emit the competitor?

The Experiment-02 error this guards against: `3/3` bare vs `15/20` scaffolded
reversions were read as "scaffolding increases reversion", when bare outputs
simply reached the site less often. Conditional reversion actually FELL.

OPERATIONAL DEFINITION OF "REACHED". The output, with insignificant layout
whitespace removed (outside quotes only -- inside a selector, whitespace is the
descendant combinator), starts with the site's own prefix normalised the same
way. Then the characters that follow decide the outcome: the correct
spelling, the competitor, or something else. This is strict -- a generation
that differs anywhere before the site has not reached THAT site -- and it is
exact, which is what makes P(Y|O) interpretable.

NATURAL-LANGUAGE REQUESTS are rendered deterministically from the IR in plain
English. They use natural verbs ("move", "scale"), which can themselves cue
the familiar spelling when a lexicon has remapped that verb. That is the
realistic condition, not a flaw, and it is recorded here so it is not
mistaken for one.
"""

from __future__ import annotations

import hashlib

import canonicalize as C
import transpiler as T

from phase3_2 import prompts, sites2 as S, templates as TM
from phase3_2.backends import BACKENDS

from p33 import config as CFG
from p33 import demos as D
from p33 import pipeline as PL
from p33 import registry

BUCKETS = ("LEX_FAIL", "PARSE_FAIL", "VALID_VACUOUS", "VALID_WRONG", "VALID_CORRECT")

# ---------------------------------------------------------------------------
# IR -> English
# ---------------------------------------------------------------------------

_TYPE_NOUN = {"mesh": "meshes", "group": "groups", "light": "lights", "camera": "cameras"}
_PSEUDO = {"selected": "the current selection", "lasso": "the lasso selection"}


def _matcher(m) -> str:
    if m.kind == "class":
        return f"objects of class '{m.name}'"
    if m.kind == "id":
        return f"the object with id '{m.name}'"
    if m.kind == "type":
        return _TYPE_NOUN.get(m.name, m.name)
    if m.kind == "pseudo":
        return _PSEUDO.get(m.name, m.name)
    if m.kind == "wildcard":
        return "every object"
    return f"{m.kind} '{m.name}'"


def describe_selector(sel) -> str:
    steps = list(sel.steps)
    parts = [" that are also ".join(_matcher(m) for m in st.matchers) for st in steps]
    text = parts[-1]
    for i in range(len(steps) - 1, 0, -1):
        rel = "directly inside" if steps[i].combinator == "child" else "anywhere inside"
        text = f"{text} {rel} {parts[i - 1]}"
    return text


def describe_op(op) -> str:
    s = describe_selector(op.selector)
    v = C.args_in_order(op.op, op.args)
    f = lambda x: C.format_number(x) if isinstance(x, (int, float)) else str(x)  # noqa: E731
    return {
        "recolor": lambda: f"change the colour of {s} to {f(v[0])}",
        "scale": lambda: f"scale {s} by {f(v[0])} along the {f(v[1])} axis",
        "move": lambda: f"move {s} by ({f(v[0])}, {f(v[1])}, {f(v[2])})",
        "rotate": lambda: f"rotate {s} by {f(v[1])} degrees around the {f(v[0])} axis",
        "delete": lambda: f"delete {s}",
        "spin": lambda: f"spin {s} {f(v[1])} turns around the {f(v[0])} axis over {f(v[2])} seconds",
        "duplicate": lambda: f"make a copy of {s} offset by ({f(v[0])}, {f(v[1])}, {f(v[2])})",
        "setMaterial": lambda: f"set the material of {s} to {f(v[0])}",
        "setOpacity": lambda: f"set the opacity of {s} to {f(v[0])}",
        "setVisible": lambda: f"make {s} {'visible' if str(v[0]) in ('1', 'true') else 'invisible'}",
        "wireframe": lambda: f"turn wireframe display {'on' if str(v[0]) in ('1', 'true') else 'off'} for {s}",
        "metalness": lambda: f"set the metalness of {s} to {f(v[0])}",
        "roughness": lambda: f"set the roughness of {s} to {f(v[0])}",
        "castShadow": lambda: f"make {s} {'cast' if str(v[0]) in ('1', 'true') else 'stop casting'} shadows",
        "receiveShadow": lambda: f"make {s} {'receive' if str(v[0]) in ('1', 'true') else 'stop receiving'} shadows",
    }[op.op]()


def describe_program(ir) -> str:
    ops = [describe_op(o) for o in ir.ops]
    if not ops:
        return "select nothing and change nothing"
    if len(ops) == 1:
        return ops[0][0].upper() + ops[0][1:] + "."
    joined = "; then ".join(ops)
    return "First, " + joined + "."


# ---------------------------------------------------------------------------
# prompt, extraction, evaluation
# ---------------------------------------------------------------------------

INSTRUCTION = ("\nWrite exactly one 3DOM program for the request, on one line, "
               "using the spellings in the table.\n")


def build_prompt(table: str, demos: D.DemoSet, demo_requests: list[str],
                 request: str) -> str:
    out = [table.rstrip(), INSTRUCTION, "\nEXAMPLES\n"]
    for req, prog in zip(demo_requests, demos.texts):
        out.append(f"Request: {req}\nProgram: {prog}\n\n")
    out.append(f"Request: {request}\nProgram:")
    return "".join(out)


def extract_program(raw: str) -> str:
    """First non-empty line, with code fences and a 'Program:' label removed."""
    for line in raw.replace("```", "\n").splitlines():
        t = line.strip()
        if t.lower().startswith("program:"):
            t = t[8:].strip()
        if t and not t.lower().startswith(("request:", "javascript", "js")):
            return t
    return ""


def normalize_layout(text: str) -> str:
    """Drop whitespace OUTSIDE quotes; keep it inside (selector combinators)."""
    out, q = [], None
    for ch in text:
        if q:
            out.append(ch)
            if ch == q:
                q = None
        elif ch in "'\"":
            q = ch
            out.append(ch)
        elif not ch.isspace():
            out.append(ch)
    return "".join(out)


def evaluate(text: str, backend, phi, target_hash: str) -> dict:
    if not text:
        return {"bucket": "LEX_FAIL", "detail": "empty output", "ir_hash": None, "n_ops": 0}
    try:
        n = backend.num_parses(text, phi)
        if n != 1:
            return {"bucket": "PARSE_FAIL", "detail": f"num_parses={n}", "ir_hash": None, "n_ops": 0}
        ir = backend.parse(text, phi)
    except T.LexError as exc:
        return {"bucket": "LEX_FAIL", "detail": str(exc)[:200], "ir_hash": None, "n_ops": 0}
    except Exception as exc:
        return {"bucket": "PARSE_FAIL", "detail": f"{type(exc).__name__}: {str(exc)[:160]}",
                "ir_hash": None, "n_ops": 0}
    h = C.content_hash(ir)
    if not ir.ops:
        return {"bucket": "VALID_VACUOUS", "detail": "zero operations (D5)", "ir_hash": h, "n_ops": 0}
    return {"bucket": "VALID_CORRECT" if h == target_hash else "VALID_WRONG",
            "detail": "", "ir_hash": h, "n_ops": len(ir.ops)}


def observe(text: str, site) -> dict:
    g, p = normalize_layout(text), normalize_layout(site.prefix)
    if not g.startswith(p):
        return {"site_id": site.site_id, "reached": False, "outcome": "not_reached",
                "emitted": None}
    rest = g[len(p):]
    for name, cand in sorted((("correct", site.correct), ("reverted", site.competitor)),
                             key=lambda kv: -len(kv[1])):
        if rest.startswith(normalize_layout(cand)):
            return {"site_id": site.site_id, "reached": True, "outcome": name,
                    "emitted": cand}
    return {"site_id": site.site_id, "reached": True, "outcome": "other",
            "emitted": rest[:12]}


def hurdle(obs: list[dict]) -> dict:
    n = len(obs)
    reached = [o for o in obs if o["reached"]]
    rev = [o for o in reached if o["outcome"] == "reverted"]
    return {"n_sites": n, "n_reached": len(reached), "n_reverted": len(rev),
            "p_reach": len(reached) / n if n else None,
            "p_revert_given_reach": len(rev) / len(reached) if reached else None,
            "product_reported_alongside": (len(rev) / n) if n else None}


# ---------------------------------------------------------------------------
# cells and scoring (registered with the shared crash-safe runner)
# ---------------------------------------------------------------------------

def _is_generator(model: str) -> bool:
    s = registry.REGISTRY.get(model)
    return s is None or s.kind == "instruct"


def armb_cells(cfg, plan, model, revision):
    temps_by = {}
    for (fam, lx), sites in plan.sites.items():
        temps_by[(fam, lx)] = sorted({s.template_id for s in sites})
    lim = int(cfg.armb.get("template_limit", 0))
    out = []
    for (fam, lx) in sorted(temps_by):
        tids = temps_by[(fam, lx)][:lim] if lim else temps_by[(fam, lx)]
        for ci, chunk in enumerate(PL.chunks(tids, cfg.chunk_size)):
            fields = {"experiment": "armb", "config_hash": cfg.config_hash(),
                      "model": model, "revision": revision, "family": fam,
                      "lexicon": lx, "condition": "generate", "chunk": ci,
                      "decoding_sha": CFG.sha256_json(_decoding(cfg)),
                      "template_ids_sha": CFG.sha256_json(chunk)}
            out.append(PL.Cell(PL.shards.cell_key(fields), fields, chunk, model,
                               fam, lx, "generate"))
    return out


def _decoding(cfg) -> dict:
    return {"do_sample": False, "num_beams": 1,
            "max_new_tokens": int(cfg.armb.get("max_new_tokens", 192)),
            "n_demos": int(cfg.armb.get("n_demos", 4))}


def score_armb_cell(cfg, cell, scorer, plan, _cache=None) -> list[dict]:
    temps = {t.template_id: t for t in TM.build_templates()}
    L = PL.phi(cell.lexicon)
    be = BACKENDS[cell.family]
    cc = plan.classes[f"{cell.family}/{cell.lexicon}/{cell.model}"]
    rendered = plan.rendered[(cell.family, cell.lexicon)]
    order = D.pool_order(list(rendered), cfg.seeds["demo_order"],
                         f"armb/{cell.family}/{cell.lexicon}")
    dec = _decoding(cfg)
    pb = prompts.bundle("rule", L)
    sites_by_t = {}
    for s in plan.sites[(cell.family, cell.lexicon)]:
        sites_by_t.setdefault(s.template_id, []).append(s)
    rows = []
    for tid in cell.sites:                       # Arm B units are templates
        PL.check_stop()
        t = temps[tid]
        target = rendered[tid]
        anchor = sites_by_t[tid][0]
        demos = D.for_site(anchor, {k: v for k, v in rendered.items() if k != tid},
                           order, dec["n_demos"])
        reqs = [describe_program(temps[d].ir) for d in demos.ids]
        request = describe_program(t.ir)
        prompt = build_prompt(pb.text, demos, reqs, request)
        raw = scorer.generate(prompt, max_new_tokens=dec["max_new_tokens"])
        prog = extract_program(raw)
        ev = evaluate(prog, be, L, C.content_hash(t.ir))
        obs = [observe(prog, s) for s in sites_by_t[tid]]
        rows.append({
            "schema_version": "p33/1", "row_key": f"{cell.key}|{tid}",
            "run_id": cfg.run_id, "stage": cfg.stage, "split": cc.label,
            "cell_key": cell.key, "model": cell.model,
            "model_revision": scorer.revision, "tokenizer_id": scorer.tokenizer_id,
            "family": cell.family, "lexicon": cell.lexicon, "template": tid,
            "condition": "generate", "nl_request": request, "prompt_sha": hashlib.sha256(prompt.encode()).hexdigest(),
            "table_prompt_sha": pb.sha, "demo_ids": list(demos.ids),
            "demo_set_sha": demos.sha, "decoding": dec,
            "decoding_sha": CFG.sha256_json(dec),
            "raw_output": raw, "extracted": prog, "target_program": target,
            "bucket": ev["bucket"], "detail": ev["detail"],
            "parse_valid": ev["bucket"] in ("VALID_VACUOUS", "VALID_WRONG", "VALID_CORRECT"),
            "task_correct": ev["bucket"] == "VALID_CORRECT",
            "ir_hash": ev["ir_hash"], "target_ir_hash": C.content_hash(t.ir),
            "n_ops": ev["n_ops"],
            "site_obs": [{**o, "terminal": s.terminal_id, "stratum": S.stratum(s)}
                         for o, s in zip(obs, sites_by_t[tid])],
            "status": "ok",
        })
    return rows


PL.register("armb", armb_cells, score_armb_cell, _is_generator)
