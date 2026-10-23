#!/usr/bin/env python3
"""voyager_models.py — list the models of the ASU RC LLM API, and probe what each can measure.

    python3 tools/voyager_models.py list                      # the model list, as served today
    python3 tools/voyager_models.py probe                     # what each text model supports
    python3 tools/voyager_models.py probe --models ID,ID      # only these models

The address and the key are handled in p4/runtime/asu_api.py, the one place for both (the key is
never printed, logged or written). The setup is in ../VOYAGER.md.

OUTPUT goes to configs/voyager/ (or --out), named by date:

  models_<date>.json   the /v1/models answer, unchanged, with the date and the address
  models_<date>.md     the text models (what each is, its served precision, its context), then the rest
  probe_<date>.json    per model: each check's HTTP status and result
  probe_<date>.md      per model: whether it can serve Arm A and Arm B the way Phase 3.3 measured them

WHAT THE PROBE ASKS. Neutral prompts only (a sentence about a river, and `def add(a, b):`), never
the experiment's materials, so the models stay unseen. Phase 3.3 scored RAW TEXT, with no chat
template and no special tokens (p4/scoring/margins.py), and Arm B generated from raw text. So the
checks that decide use /v1/completions:

  prompt_logprobs  the id of every prompt token and its log-probability, special tokens off
                   (prompt_logprobs=0, return_token_ids, add_special_tokens=false)    -> Arm A
  margins          three one-word contrasts at the end of the sentence, scored the way
                   margins.py does (from the first divergent token); the first one twice:
                     repeatable   the same request gives the same margin, bit for bit
                     resolution   the coarsest step 2^-j that every margin is a whole multiple
                                  of. 2^-3 means the logits are rounded (bf16), so a margin
                                  nearer zero than about 0.125 nats has an unreliable sign
  raw_generation   greedy text from `def add(a, b):`, twice: an answer, and the same one -> Arm B
  chat, chat_logprobs   the chat endpoint, and top_logprobs on generated tokens (diagnostics)

A model listed as a FAMILY routes each request to an instruct or a thinking member by reasoning
effort. It is probed as its members, named directly, because the routing default could change.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime
import json
import os
import re
import sys

CODE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, CODE)

from p4.runtime import asu_api as API  # noqa: E402
from p4.runtime.asu_api import NoKey, request  # noqa: E402,F401  (tests replace `request`)

BASE = API.BASE
KEY_FILE = API.KEY_FILE
OUT = os.path.join(CODE, "configs", "voyager")
NOT_TEXT = ("embed", "image", "audio", "speech", "transcri", "video", "tts", "whisper", "rerank")
HELPER_ONLY = ("not meant for direct use", "not a chat model")
SENTENCE = ("The river ran slowly past the old mill, and the children watched the water carry "
            "leaves toward the bridge. When the bell rang, everyone walked home along the")
PAIRS = ((" road", " river"), (" path", " bridge"), (" street", " water"))
CODE_PROMPT = "def add(a, b):\n"
TIMEOUT, TRIES = 60.0, 2            # per probe request: a deployment that hangs must not stall the probe


def load_key() -> str:
    return API.load_key(KEY_FILE)


def _err(r) -> str:
    """An error answer, cut to its first sentence: the gateway's messages can name its internals."""
    text = r if isinstance(r, str) else json.dumps(r)
    m = re.search(r'"message"\s*:\s*"([^"]*)', text)          # also in a cut-off JSON answer
    return (m.group(1) if m else text).split(". ")[0].strip()[:120]


# --------------------------------------------------------------------- list

def _short(text: str, n: int = 150) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[:n - 1].rstrip() + "…"


def _reasoning(m: dict) -> str:
    r = m.get("reasoning")
    if isinstance(r, dict):
        mode = r.get("mode", "")
        levels = r.get("levels") or {}
        if mode == "mapped" and levels.get("none") not in (None, "none"):
            return "always (none acts as low)"
        return {"mapped": "effort none-high", "unsupported": "no"}.get(mode, mode)
    fam = m.get("family")
    if isinstance(fam, dict) and fam.get("members"):
        return "by member"
    return ""


def members(m: dict) -> list[str]:
    fam = m.get("family")
    if isinstance(fam, dict) and isinstance(fam.get("members"), dict):
        return sorted(set(fam["members"].values()))
    return []


def models_table(listing: dict) -> list[dict]:
    rows = []
    for m in sorted(listing.get("data", []), key=lambda m: str(m.get("id"))):
        rows.append({
            "id": str(m.get("id", "")),
            "type": str(m.get("model_type") or m.get("type") or m.get("mode") or ""),
            "context": str(m.get("context_window") or m.get("max_input_tokens") or ""),
            "served as": str(m.get("quantization") or ""),
            "reasoning": _reasoning(m),
            "tools": "yes" if m.get("supports_function_calling") else ("no" if "supports_function_calling" in m else ""),
            "vision": "yes" if m.get("supports_vision") else ("no" if "supports_vision" in m else ""),
            "members": ", ".join(members(m)),
            "what it is": _short(m.get("description", "")),
        })
    return rows


def md_table(rows: list[dict], cols: list[str]) -> list[str]:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")).replace("|", "/") for c in cols) + " |")
    return out


def cmd_list(a) -> int:
    key = load_key()
    status, listing = request(key, "GET", "/models")
    if status != 200 or not isinstance(listing, dict):
        print(f"GET {BASE}/models failed: HTTP {status}: {listing}", file=sys.stderr)
        return 1
    day = datetime.date.today().isoformat()
    os.makedirs(a.out, exist_ok=True)
    snap = {"listed_on": day, "base_url": BASE, "response": listing}
    json.dump(snap, open(os.path.join(a.out, f"models_{day}.json"), "w", encoding="utf-8"), indent=1)
    rows = models_table(listing)
    text = [r for r in rows if r["type"] == "chat"]
    other = [r for r in rows if r["type"] != "chat"]
    lines = [f"# ASU RC LLM API: the models served on {day}", "",
             f"From `GET {BASE}/models`: {len(rows)} models, {len(text)} of them text (chat) models. "
             f"The raw answer, with every field, is in `models_{day}.json`. What each text model can "
             "measure for the experiment is in the probe table (`probe_<date>.md`).", "",
             "**served as** is the precision of the served weights. **members**: the id is a family that "
             "routes to these models by reasoning effort; they can also be named directly.", "",
             "## Text models", ""]
    lines += md_table(text, ["id", "served as", "context", "reasoning", "members", "what it is"])
    lines += ["", "## Other models (not text generation)", ""]
    lines += md_table(other, ["id", "type", "what it is"])
    open(os.path.join(a.out, f"models_{day}.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"{len(rows)} models ({len(text)} text) -> {a.out}/models_{day}.md")
    return 0


# --------------------------------------------------------------------- probe

def _is_text(m: dict) -> bool:
    kind = " ".join(str(m.get(k, "")) for k in ("model_type", "type", "mode")).lower()
    return not any(t in kind or t in str(m.get("id", "")).lower() for t in NOT_TEXT)


def probe_targets(listing: dict) -> tuple[list[tuple[str, str]], list[str]]:
    """[(model to probe, note)], [skipped with reason]. Families become their members."""
    targets, skipped, seen = [], [], set()
    for m in sorted(listing.get("data", []), key=lambda m: str(m.get("id"))):
        mid = str(m.get("id"))
        if not _is_text(m):
            skipped.append(f"{mid}: not a text model ({m.get('model_type') or m.get('type')})")
            continue
        desc = str(m.get("description", "")).lower()
        if any(h in desc for h in HELPER_ONLY):
            skipped.append(f"{mid}: {_short(m.get('description', ''), 90)}")
            continue
        mem = members(m)
        for name, note in ([(x, f"member of {mid}") for x in mem] if mem else [(mid, "")]):
            if name not in seen:
                seen.add(name)
                targets.append((name, note))
    return targets, skipped


def check_chat(key, model, logprobs=False):
    body = {"model": model, "messages": [{"role": "user", "content": "Reply with one word: ready"}],
            "max_tokens": 32, "temperature": 0}
    if logprobs:
        body.update({"logprobs": True, "top_logprobs": 5})
    status, r = request(key, "POST", "/chat/completions", body, timeout=TIMEOUT, tries=TRIES)
    out = {"status": status, "ok": False}
    if status == 200 and isinstance(r, dict) and r.get("choices"):
        ch = r["choices"][0]
        if not logprobs:
            out["ok"] = "message" in ch
            out["answered"] = bool((ch.get("message") or {}).get("content"))
        else:
            content = ((ch.get("logprobs") or {}).get("content")) or []
            k = len(content[0].get("top_logprobs") or []) if content else 0
            out.update({"ok": bool(content) and k > 0, "top_k": k})
    elif status != 200:
        out["error"] = _err(r)
    return out


def prompt_tokens(key, model, text, *, special=False):
    """(status, info): the served tokenisation of `text` and each token's log-probability."""
    body = {"model": model, "prompt": text, "max_tokens": 1, "temperature": 0, "prompt_logprobs": 0,
            "return_token_ids": True, "add_special_tokens": special}
    status, r = request(key, "POST", "/completions", body, timeout=TIMEOUT, tries=TRIES)
    if status != 200 or not isinstance(r, dict) or not r.get("choices"):
        return status, {"error": _err(r)}
    ch = r["choices"][0]
    ids, pl = ch.get("prompt_token_ids"), ch.get("prompt_logprobs")
    if not isinstance(ids, list) or not isinstance(pl, list) or len(pl) != len(ids) or not ids:
        return status, {"error": "no prompt token ids or log-probabilities in the answer"}
    lps = [None]
    for j in range(1, len(ids)):
        e = (pl[j] or {}).get(str(ids[j]))
        if not isinstance(e, dict) or not isinstance(e.get("logprob"), (int, float)):
            return status, {"error": f"position {j} has no log-probability for its own token"}
        lps.append(float(e["logprob"]))
    return status, {"ids": ids, "lps": lps, "served": r.get("model"),
                    "fingerprint": r.get("system_fingerprint")}


def check_prompt_logprobs(key, model):
    status, info = prompt_tokens(key, model, SENTENCE)
    out = {"status": status, "ok": "ids" in info}
    if "ids" in info:
        st2, on = prompt_tokens(key, model, SENTENCE, special=True)
        out.update({"n_tokens": len(info["ids"]), "served": info["served"],
                    "fingerprint": info["fingerprint"],
                    "special_tokens_added_by_default": (len(on["ids"]) - len(info["ids"])) if "ids" in on else None})
    else:
        out["error"] = info.get("error")
    return out


def _margin(key, model, c, q):
    sa, a = prompt_tokens(key, model, SENTENCE + c)
    sb, b = prompt_tokens(key, model, SENTENCE + q)
    if "ids" not in a or "ids" not in b:
        return {"ok": False, "error": a.get("error") or b.get("error")}
    k = 0
    for x, y in zip(a["ids"], b["ids"]):
        if x != y:
            break
        k += 1
    if k < 1 or k >= len(a["ids"]) or k >= len(b["ids"]):
        return {"ok": False, "error": f"degenerate pair (k={k})"}
    lc, lq = sum(a["lps"][k:]), sum(b["lps"][k:])
    return {"ok": True, "m": lc - lq, "k": k, "n_c": len(a["ids"]) - k, "n_q": len(b["ids"]) - k,
            "fingerprint": a["fingerprint"]}


def resolution(ms: list[float]) -> int | None:
    """The smallest j <= 10 such that every margin is a whole multiple of 2^-j, or None."""
    nz = [m for m in ms if m != 0.0]
    if not nz:
        return None
    for j in range(0, 11):
        step = 2.0 ** -j
        if all(abs(m - round(m / step) * step) < 1e-5 for m in nz):
            return j
    return None


def check_margins(key, model):
    got = [_margin(key, model, c, q) for c, q in PAIRS]
    if not all(g["ok"] for g in got):
        return {"ok": False, "error": next(g["error"] for g in got if not g["ok"])}
    again = _margin(key, model, *PAIRS[0])
    ms = [g["m"] for g in got]
    return {"ok": True, "margins": ms, "single_token": [g["n_c"] == 1 and g["n_q"] == 1 for g in got],
            "repeatable": again.get("ok", False) and again["m"] == ms[0],
            "resolution_log2": resolution(ms),
            "ties": sum(1 for m in ms if m == 0.0)}


def check_raw_generation(key, model):
    texts = []
    status = 0
    for _ in range(2):
        status, r = request(key, "POST", "/completions", {"model": model, "prompt": CODE_PROMPT,
                                                          "max_tokens": 24, "temperature": 0}, timeout=TIMEOUT, tries=TRIES)
        if status != 200 or not isinstance(r, dict) or not r.get("choices"):
            return {"status": status, "ok": False, "error": _err(r)}
        texts.append(r["choices"][0].get("text") or "")
    return {"status": status, "ok": any(t.strip() for t in texts), "deterministic": texts[0] == texts[1],
            "sample": texts[0][:80]}


def classify(results: dict) -> dict:
    """What a model can serve, from the checks."""
    mg = results.get("margins", {})
    return {"arm_a": bool(results.get("prompt_logprobs", {}).get("ok") and mg.get("ok")),
            "arm_b": bool(results.get("raw_generation", {}).get("ok")),
            "chat": bool(results.get("chat", {}).get("ok")),
            "first_token_logprobs": bool(results.get("chat_logprobs", {}).get("ok"))}


def probe_model(key: str, model: str) -> dict:
    res = {"prompt_logprobs": check_prompt_logprobs(key, model)}
    st = res["prompt_logprobs"]["status"]
    if st == 0 or st >= 500:                      # the deployment does not answer: stop here
        for k in ("margins", "raw_generation", "chat", "chat_logprobs"):
            res[k] = {"status": st, "ok": False, "error": "not tried: the model did not answer"}
        res["no_answer"] = res["prompt_logprobs"].get("error", "")
        res["serves"] = classify(res)
        return res
    res["margins"] = (check_margins(key, model) if res["prompt_logprobs"]["ok"]
                      else {"ok": False, "error": "no prompt log-probabilities"})
    res["raw_generation"] = check_raw_generation(key, model)
    res["chat"] = check_chat(key, model)
    res["chat_logprobs"] = check_chat(key, model, logprobs=True)
    res["serves"] = classify(res)
    return res


def _res_text(r: dict) -> str:
    mg = r.get("margins", {})
    if not mg.get("ok"):
        return ""
    j = mg.get("resolution_log2")
    return "finer than 2^-10" if j is None else f"2^-{j} ({2.0 ** -j:g} nats)"


def cmd_probe(a) -> int:
    key = load_key()
    status, listing = request(key, "GET", "/models")
    if status != 200 or not isinstance(listing, dict):
        print(f"GET {BASE}/models failed: HTTP {status}: {listing}", file=sys.stderr)
        return 1
    byid = {str(m.get("id")): m for m in listing.get("data", [])}
    parent = {x: k for k, m in byid.items() for x in members(m)}
    targets, skipped = probe_targets(listing)
    notes = dict(targets)
    if a.models:
        chosen, unknown = [], []
        for m in (x for x in a.models.split(",") if x):
            if m in byid and members(byid[m]):
                chosen += members(byid[m])
            elif m in byid or m in parent:
                chosen.append(m)
            else:
                unknown.append(m)
        if unknown:
            print(f"not served now: {unknown}", file=sys.stderr)
            return 1
        targets = [(m, notes.get(m, "")) for m in dict.fromkeys(chosen)]
        skipped = []
    print(f"probing {len(targets)} text models with {a.workers} workers"
          + (f" (skipping {len(skipped)})" if skipped else ""))
    results = {}
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(probe_model, key, m): m for m, _n in targets}
        for f in cf.as_completed(futs):
            m = futs[f]
            results[m] = f.result()
            s = results[m]["serves"]
            print(f"  {m:40s} Arm A {'yes' if s['arm_a'] else 'no ':3s}  Arm B {'yes' if s['arm_b'] else 'no'}"
                  + ("  (did not answer)" if results[m].get("no_answer") is not None else ""), flush=True)
    day = datetime.date.today().isoformat()
    os.makedirs(a.out, exist_ok=True)
    blob = {"probed_on": day, "base_url": BASE, "sentence": SENTENCE, "pairs": PAIRS,
            "code_prompt": CODE_PROMPT, "skipped": skipped, "notes": notes,
            "results": dict(sorted(results.items()))}
    json.dump(blob, open(os.path.join(a.out, f"probe_{day}.json"), "w", encoding="utf-8"), indent=1)
    n_a, n_b = write_probe_table(a.out, blob, byid)
    print(f"{n_a} models for Arm A, {n_b} for Arm B -> {a.out}/probe_{day}.md")
    return 0


def write_probe_table(out: str, blob: dict, byid: dict) -> tuple[int, int]:
    """probe_<date>.md, from the probe's JSON record and the model list."""
    day, results, notes, skipped = blob["probed_on"], blob["results"], blob["notes"], blob["skipped"]
    rows = []
    for m, r in sorted(results.items()):
        s, pl, mg, rg = r["serves"], r["prompt_logprobs"], r["margins"], r["raw_generation"]
        rows.append({
            "model": m, "served as": byid.get(m, {}).get("quantization", ""),
            "Arm A": "yes" if s["arm_a"] else f"no ({pl.get('status')})",
            "margin step": _res_text(r),
            "repeatable": ("yes" if mg.get("repeatable") else "NO") if mg.get("ok") else "",
            "Arm B": ("yes" if rg.get("deterministic") else "yes, not deterministic") if s["arm_b"] else f"no ({rg.get('status')})",
            "chat": "yes" if s["chat"] else f"no ({r['chat']['status']})",
            "chat logprobs": f"top {r['chat_logprobs'].get('top_k', 0)}" if s["first_token_logprobs"] else "no",
            "served id": f"{pl.get('served', '')} · {pl.get('fingerprint', '')}" if pl.get("ok") else "",
            "note": "; ".join(x for x in (notes.get(m, ""), "did not answer: " + _short(r["no_answer"], 70)
                                           if r.get("no_answer") is not None else "") if x),
        })
    cols = ["model", "served as", "Arm A", "margin step", "repeatable", "Arm B", "chat", "chat logprobs",
            "served id", "note"]
    n_a = sum(1 for r in results.values() if r["serves"]["arm_a"])
    n_b = sum(1 for r in results.values() if r["serves"]["arm_b"])
    lines = [f"# ASU RC LLM API: what each model can measure ({day})", "",
             "Probed with neutral prompts only, never the experiment's materials (the prompts are in "
             f"`probe_{day}.json`).", "",
             "- **Arm A** (margins from a forced prefix, as Phase 3.3 scored them): `/v1/completions` "
             "returns every prompt token's id and log-probability with special tokens off, and three "
             "test margins could be scored from the first divergent token.",
             "- **margin step**: every test margin was a whole multiple of this. A coarse step means the "
             "server rounds its logits (bf16), so margins nearer zero than the step have an unreliable "
             "sign; Phase 3.3 avoided this with an fp32 output head, which an API cannot offer.",
             "- **repeatable**: the same request gave the same margin, bit for bit.",
             "- **Arm B** (greedy generation from raw text): `/v1/completions` answered, and twice the same.",
             "- **served id**: the model the gateway actually ran, and its `system_fingerprint`. The "
             "pipeline pins this pair and refuses to mix answers from two of them.", ""]
    lines += md_table(rows, cols)
    lines += ["", f"**{n_a} of {len(rows)} can serve Arm A; {n_b} can serve Arm B.**"]
    if skipped:
        lines += ["", "Not probed: " + "; ".join(skipped) + "."]
    open(os.path.join(out, f"probe_{day}.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return n_a, n_b


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("list", help="save the model list")
    pl.add_argument("--out", default=OUT)
    pp = sub.add_parser("probe", help="check what each model supports")
    pp.add_argument("--out", default=OUT)
    pp.add_argument("--models", default="", help="comma-separated model ids (default: all text models)")
    pp.add_argument("--workers", type=int, default=4, help="models probed at once (the gateway advises 4-8 requests)")
    a = ap.parse_args(argv)
    try:
        return cmd_list(a) if a.cmd == "list" else cmd_probe(a)
    except NoKey as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
