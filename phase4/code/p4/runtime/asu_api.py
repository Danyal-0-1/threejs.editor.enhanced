"""asu_api.py — the ASU RC LLM API ("Voyager"): its address, the key, and one request.

Shared by tools/voyager_models.py (the model list and the probe) and p4/scoring/api.py (the
scorer), so the key is handled in exactly one place.

THE API is ASU Research Computing's OpenAI-compatible gateway, https://openai.rc.asu.edu/v1, in
front of vLLM servers on Research Computing hardware. It works from anywhere (laptop, Sol login
node or compute node) without the VPN. The setup is in ../../VOYAGER.md.

THE KEY is personal (the Voyager portal, Keys -> AI LLM). It is read from $ASU_RC_API_KEY, or from
the file named by $ASU_RC_API_KEY_FILE (default ~/.config/asu-rc/llm_api_key), which must be
readable by its owner alone (chmod 600). It goes only into the Authorization header. It is never
printed, logged, written to a result, or left in an error message.

LIMITS (Research Computing's documentation, read 2026-10-22): a per-minute token budget answers
429 (wait one minute); the fair queue answers 503 after 5 minutes; 502-504 are retried with
backoff; 4-8 parallel requests per model is the advised starting point.
"""

from __future__ import annotations

import json
import os
import stat
import time
import urllib.error
import urllib.request

BASE = os.environ.get("ASU_RC_API_BASE", "https://openai.rc.asu.edu/v1").rstrip("/")
KEY_FILE = os.environ.get("ASU_RC_API_KEY_FILE",
                          os.path.join(os.path.expanduser("~"), ".config", "asu-rc", "llm_api_key"))


class NoKey(RuntimeError):
    pass


def load_key(path: str | None = None) -> str:
    """The API key, from the environment or a private file. Never returned to any output."""
    key = os.environ.get("ASU_RC_API_KEY", "").strip()
    if key:
        return key
    path = path or KEY_FILE
    if not os.path.isfile(path):
        raise NoKey(f"no key: set ASU_RC_API_KEY, or put it in {path} (chmod 600). "
                    f"Create one in the Voyager portal, https://voyager.rc.asu.edu (Keys -> AI LLM)")
    if os.stat(path).st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise NoKey(f"{path} can be read by others; run: chmod 600 {path}")
    key = open(path, encoding="utf-8").read().strip()
    if not key:
        raise NoKey(f"{path} is empty")
    return key


def request(key: str, method: str, path: str, body: dict | None = None, *, timeout: float = 360.0,
            tries: int = 4, base: str | None = None) -> tuple[int, dict | str]:
    """One API call with the gateway's retry advice: wait a minute on 429, back off on 502-504
    and on a dropped connection. Returns (HTTP status, parsed JSON or a short error text);
    status 0 means no answer. The key is never part of the result."""
    data = None if body is None else json.dumps(body).encode("utf-8")
    delay = 5.0
    for attempt in range(tries):
        req = urllib.request.Request((base or BASE) + path, data=data, method=method)
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
                delay = min(delay * 2, 120.0)
                continue
            return e.code, text.replace(key, "<key>")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt + 1 < tries:
                time.sleep(delay)
                delay = min(delay * 2, 120.0)
                continue
            return 0, f"connection failed: {type(e).__name__}: {e}".replace(key, "<key>")
    return 0, "no answer"
