#!/usr/bin/env python3
"""voyager_models.py — list the models of the ASU RC LLM API, and probe what each can measure.

    python3 tools/voyager_models.py list                      # the model list, as served today
    python3 tools/voyager_models.py probe                     # what each listed model supports
    python3 tools/voyager_models.py probe --models ID,ID      # only these models

The API is ASU Research Computing's OpenAI-compatible gateway, https://openai.rc.asu.edu/v1. It
serves the models on Research Computing hardware at no cost, and works from anywhere (laptop or
Sol) without the VPN. Keys are personal: create one in the Voyager portal,
https://voyager.rc.asu.edu (which needs the ASU network or the SSLVPN), under Keys -> AI LLM.
The setup is in ../VOYAGER.md.

THE KEY is read from $ASU_RC_API_KEY, or from the file named by $ASU_RC_API_KEY_FILE (default
~/.config/asu-rc/llm_api_key), which must be readable by you alone (chmod 600). It goes only into
the Authorization header. It is never printed, logged or written to any output.

OUTPUT goes to configs/voyager/ (or --out), named by date:

  models_<date>.json   the /v1/models answer, unchanged, with the date and the address
  models_<date>.md     one row per model: type, context window, capabilities
  probe_<date>.json    per model: each check's HTTP status and result
  probe_<date>.md      one row per model, and which part of the experiment it can serve

WHAT THE PROBE ASKS. It sends neutral prompts only ("The capital of France is"), never the
experiment's materials, so the models stay unseen. Each check is one tiny request:

  chat             /chat/completions answers                       -> Arm B (free generation)
  chat_logprobs    it returns top_logprobs for the tokens it writes -> first-token diagnostics
  completions      /completions answers (no chat template)
  prompt_logprobs  /completions returns the log-probabilities of the PROMPT's own tokens
                   (echo=true, or vLLM's prompt_logprobs)          -> Arm A (forced-prefix margins)

H4 also needs a base model with its instruct twin; the probe reports base models it can tell
from the model list, and the decision is made in the preregistration.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime
import json
import os
import stat
import sys
import time
import urllib.error
import urllib.request

CODE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get("ASU_RC_API_BASE", "https://openai.rc.asu.edu/v1").rstrip("/")
KEY_FILE = os.environ.get("ASU_RC_API_KEY_FILE",
                          os.path.join(os.path.expanduser("~"), ".config", "asu-rc", "llm_api_key"))
OUT = os.path.join(CODE, "configs", "voyager")
NOT_TEXT = ("embed", "image", "audio", "speech", "transcri", "video", "tts", "whisper", "rerank")
PROMPT = "The capital of France is"


class NoKey(RuntimeError):
    pass


def load_key() -> str:
    """The API key, from the environment or a private file. Never returned to any output."""
    key = os.environ.get("ASU_RC_API_KEY", "").strip()
    if key:
        return key
    if not os.path.isfile(KEY_FILE):
        raise NoKey(f"no key: set ASU_RC_API_KEY, or put it in {KEY_FILE} (chmod 600). "
                        f"Create one in the Voyager portal, https://voyager.rc.asu.edu (Keys -> AI LLM)")
    mode = os.stat(KEY_FILE).st_mode
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise NoKey(f"{KEY_FILE} can be read by others; run: chmod 600 {KEY_FILE}")
    key = open(KEY_FILE, encoding="utf-8").read().strip()
    if not key:
        raise NoKey(f"{KEY_FILE} is empty")
    return key


def request(key: str, method: str, path: str, body: dict | None = None, *, timeout: float = 360.0,
            tries: int = 4) -> tuple[int, dict | str]:
    """One API call with the gateway's retry advice: wait a minute on 429, back off on 502-504.
    Returns (HTTP status, parsed JSON or a short error text). The key is never part of the result."""
    data = None if body is None else json.dumps(body).encode("utf-8")
    delay = 5.0
    for attempt in range(tries):
        req = urllib.request.Request(BASE + path, data=data, method=method)
        req.add_header("Authorization", "Bearer " + key)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", "replace")[:300]
            if e.code == 429 and attempt + 1 < tries:
                time.sleep(60)
                continue
            if e.code in (502, 503, 504) and attempt + 1 < tries:
                time.sleep(delay)
                delay *= 2
                continue
            return e.code, text.replace(key, "<key>")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt + 1 < tries:
                time.sleep(delay)
                delay *= 2
                continue
            return 0, f"connection failed: {type(e).__name__}: {e}".replace(key, "<key>")
    return 0, "no answer"


# --------------------------------------------------------------------- list

def _flag(m: dict, *names) -> str:
    for n in names:
        if n in m:
            v = m[n]
            return "yes" if v is True else ("no" if v is False else str(v))
    return ""


def models_table(listing: dict) -> list[dict]:
    rows = []
    for m in sorted(listing.get("data", []), key=lambda m: str(m.get("id"))):
        rows.append({
            "id": str(m.get("id", "")),
            "type": _flag(m, "model_type", "type", "mode"),
            "context": _flag(m, "context_window", "max_input_tokens", "context_length"),
            "tools": _flag(m, "supports_function_calling"),
            "vision": _flag(m, "supports_vision"),
            "structured": _flag(m, "supports_response_schema"),
            "reasoning": _flag(m, "supports_reasoning", "reasoning", "reasoning_levels"),
            "deprecated": _flag(m, "deprecated", "deprecation_date", "deprecation"),
            "owner": _flag(m, "owned_by"),
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
    cols = ["id", "type", "context", "tools", "vision", "structured", "reasoning", "deprecated", "owner"]
    lines = [f"# ASU RC LLM API: the models served on {day}", "",
             f"From `GET {BASE}/models` ({len(rows)} models). The raw answer is in `models_{day}.json`.",
             "What each model can measure is in the probe table (`probe_<date>.md`).", ""]
    lines += md_table(rows, cols)
    open(os.path.join(a.out, f"models_{day}.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"{len(rows)} models -> {a.out}/models_{day}.md")
    return 0


# --------------------------------------------------------------------- probe

def _is_text(m: dict) -> bool:
    kind = " ".join(str(m.get(k, "")) for k in ("model_type", "type", "mode")).lower()
    return not any(t in kind or t in str(m.get("id", "")).lower() for t in NOT_TEXT)


def classify(results: dict) -> dict:
    """What a model can serve, from the four checks."""
    return {"arm_b": bool(results.get("chat", {}).get("ok")),
            "arm_a": bool(results.get("prompt_logprobs", {}).get("ok")),
            "first_token_logprobs": bool(results.get("chat_logprobs", {}).get("ok"))}


def check_chat(key, model, logprobs=False):
    body = {"model": model, "messages": [{"role": "user", "content": "Reply with one word: ready"}],
            "max_tokens": 32, "temperature": 0}
    if logprobs:
        body.update({"logprobs": True, "top_logprobs": 5})
    status, r = request(key, "POST", "/chat/completions", body)
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
        out["error"] = str(r)[:160]
    return out


def check_completions(key, model, echo=False):
    body = {"model": model, "prompt": PROMPT + (" Paris" if echo else ""), "max_tokens": 1,
            "temperature": 0, "logprobs": 1}
    if echo:
        body["echo"] = True
    status, r = request(key, "POST", "/completions", body)
    out = {"status": status, "ok": False}
    if status == 200 and isinstance(r, dict) and r.get("choices"):
        ch = r["choices"][0]
        if not echo:
            out["ok"] = "text" in ch
        else:
            tl = ((ch.get("logprobs") or {}).get("token_logprobs")) or []
            numeric = [x for x in tl if isinstance(x, (int, float))]
            out.update({"ok": len(numeric) >= 3, "scored_tokens": len(numeric), "via": "echo"})
    elif status != 200:
        out["error"] = str(r)[:160]
    if echo and not out["ok"]:                        # vLLM's own field, if echo is not supported
        body = {"model": model, "prompt": PROMPT + " Paris", "max_tokens": 1, "temperature": 0,
                "prompt_logprobs": 1}
        status, r = request(key, "POST", "/completions", body)
        if status == 200 and isinstance(r, dict) and r.get("choices"):
            pl = r["choices"][0].get("prompt_logprobs") or []
            if len([x for x in pl if x]) >= 3:
                out.update({"ok": True, "scored_tokens": len([x for x in pl if x]), "via": "prompt_logprobs",
                            "status": status})
    return out


def probe_model(key: str, model: str) -> dict:
    res = {"chat": check_chat(key, model), "chat_logprobs": check_chat(key, model, logprobs=True),
           "completions": check_completions(key, model),
           "prompt_logprobs": check_completions(key, model, echo=True)}
    res["serves"] = classify(res)
    return res


def cmd_probe(a) -> int:
    key = load_key()
    status, listing = request(key, "GET", "/models")
    if status != 200 or not isinstance(listing, dict):
        print(f"GET {BASE}/models failed: HTTP {status}: {listing}", file=sys.stderr)
        return 1
    byid = {str(m.get("id")): m for m in listing.get("data", [])}
    want = [m for m in a.models.split(",") if m] if a.models else sorted(byid)
    unknown = [m for m in want if m not in byid]
    if unknown:
        print(f"not served now: {unknown}", file=sys.stderr)
        return 1
    text = [m for m in want if _is_text(byid[m])]
    skipped = sorted(set(want) - set(text))
    print(f"probing {len(text)} text models with {a.workers} workers"
          + (f" (skipping {len(skipped)} non-text models)" if skipped else ""))
    results = {}
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(probe_model, key, m): m for m in text}
        for f in cf.as_completed(futs):
            m = futs[f]
            results[m] = f.result()
            s = results[m]["serves"]
            print(f"  {m:45s} Arm B {'yes' if s['arm_b'] else 'no ':3s}  Arm A {'yes' if s['arm_a'] else 'no'}")
    day = datetime.date.today().isoformat()
    os.makedirs(a.out, exist_ok=True)
    json.dump({"probed_on": day, "base_url": BASE, "prompt": PROMPT, "skipped_not_text": skipped,
               "results": dict(sorted(results.items()))},
              open(os.path.join(a.out, f"probe_{day}.json"), "w", encoding="utf-8"), indent=1)
    rows = []
    for m, r in sorted(results.items()):
        s = r["serves"]
        base_like = "base" in m.lower() and "instruct" not in m.lower()
        rows.append({"model": m, "chat": "yes" if r["chat"]["ok"] else f"no ({r['chat']['status']})",
                     "chat logprobs": f"top {r['chat_logprobs'].get('top_k', 0)}" if r["chat_logprobs"]["ok"] else "no",
                     "completions": "yes" if r["completions"]["ok"] else f"no ({r['completions']['status']})",
                     "prompt logprobs": f"yes ({r['prompt_logprobs'].get('via')})" if r["prompt_logprobs"]["ok"] else "no",
                     "Arm B": "yes" if s["arm_b"] else "no", "Arm A": "yes" if s["arm_a"] else "no",
                     "note": "looks like a base model" if base_like else ""})
    cols = ["model", "chat", "chat logprobs", "completions", "prompt logprobs", "Arm B", "Arm A", "note"]
    lines = [f"# ASU RC LLM API: what each model can measure ({day})", "",
             f"Probed with neutral prompts only (`{PROMPT}`), never the experiment's materials.",
             "Arm B needs `chat`; Arm A's forced-prefix margin needs `prompt logprobs`. The raw checks",
             f"are in `probe_{day}.json`." + (f" Skipped as non-text: {', '.join(skipped)}." if skipped else ""), ""]
    lines += md_table(rows, cols)
    n_a = sum(1 for r in rows if r["Arm A"] == "yes")
    n_b = sum(1 for r in rows if r["Arm B"] == "yes")
    lines += ["", f"**{n_b} of {len(rows)} can serve Arm B; {n_a} can serve Arm A.**"]
    open(os.path.join(a.out, f"probe_{day}.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"{n_b} models for Arm B, {n_a} for Arm A -> {a.out}/probe_{day}.md")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("list", help="save the model list")
    pl.add_argument("--out", default=OUT)
    pp = sub.add_parser("probe", help="check what each model supports")
    pp.add_argument("--out", default=OUT)
    pp.add_argument("--models", default="", help="comma-separated model ids (default: all text models)")
    pp.add_argument("--workers", type=int, default=4, help="parallel requests (the gateway advises 4-8)")
    a = ap.parse_args(argv)
    try:
        return cmd_list(a) if a.cmd == "list" else cmd_probe(a)
    except NoKey as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
