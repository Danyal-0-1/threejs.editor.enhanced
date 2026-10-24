"""asu_api.py — the ASU RC LLM API ("Voyager"): its address, the key, and one request.

Shared by tools/voyager_models.py (the model list and the probe) and p4/scoring/api.py (the
scorer), so the key is handled in exactly one place.

THE API is ASU Research Computing's OpenAI-compatible gateway, https://openai.rc.asu.edu/v1, in
front of vLLM servers on Research Computing hardware. The setup is in ../../VOYAGER.md.

THE KEY is personal (the Voyager portal, Keys -> AI LLM). It is read from $ASU_RC_API_KEY, or from
the file named by $ASU_RC_API_KEY_FILE (default ~/.config/asu-rc/llm_api_key), which must be
readable by its owner alone (chmod 600). It goes only into the Authorization header. It is never
printed, logged, written to a result, or left in an error message.

LIMITS (Research Computing's documentation, read 2026-10-22): a per-minute token budget answers
429 (wait one minute); the fair queue answers 503 after 5 minutes; 502-504 are retried with
backoff; 4-8 parallel requests per model is the advised starting point.

CONNECTIONS (2026-10-23). Each thread keeps one open connection and reuses it. The first version
opened a new TLS connection per request; at 54 requests in flight from a laptop, connections
stalled in TCP retransmission for minutes. A request now gives up after `timeout` seconds and is
retried on a fresh connection, as are 500 and 502-504 answers and dropped connections. Each retry
is noted on stderr (never with the key), so a job's log shows what the gateway did.
"""

from __future__ import annotations

import http.client
import json
import os
import stat
import sys
import threading
import time
import urllib.parse

BASE = os.environ.get("ASU_RC_API_BASE", "https://openai.rc.asu.edu/v1").rstrip("/")
KEY_FILE = os.environ.get("ASU_RC_API_KEY_FILE",
                          os.path.join(os.path.expanduser("~"), ".config", "asu-rc", "llm_api_key"))
RETRIED = (500, 502, 503, 504)
_LOCAL = threading.local()


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


def _note(msg: str) -> None:
    print(f"[asu_api {time.strftime('%H:%M:%S')}] {msg}", file=sys.stderr, flush=True)


def _connection(base: str, timeout: float):
    """This thread's open connection to `base`, made on first use."""
    u = urllib.parse.urlsplit(base)
    conns = getattr(_LOCAL, "conns", None)
    if conns is None:
        conns = _LOCAL.conns = {}
    k = (u.scheme, u.netloc, timeout)
    if k not in conns:
        cls = http.client.HTTPSConnection if u.scheme == "https" else http.client.HTTPConnection
        conns[k] = cls(u.netloc, timeout=timeout)
    return conns[k], u.path.rstrip("/"), k


def _drop(k) -> None:
    conn = getattr(_LOCAL, "conns", {}).pop(k, None)
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass


def request(key: str, method: str, path: str, body: dict | None = None, *, timeout: float = 360.0,
            tries: int = 4, base: str | None = None) -> tuple[int, dict | str]:
    """One API call with the gateway's retry advice: wait a minute on 429; back off on 500,
    502-504, a timeout or a dropped connection. Returns (HTTP status, parsed JSON or a short
    error text); status 0 means no answer. The key is never part of the result."""
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Authorization": "Bearer " + key}
    if data is not None:
        headers["Content-Type"] = "application/json"
    delay = 5.0
    for attempt in range(tries):
        last = attempt + 1 == tries
        conn, prefix, k = _connection(base or BASE, timeout)
        try:
            conn.request(method, prefix + path, body=data, headers=headers)
            resp = conn.getresponse()
            raw = resp.read()
            status = resp.status
            if (resp.getheader("connection") or "").lower() == "close":
                _drop(k)
        except (OSError, http.client.HTTPException) as e:          # timeouts, resets, closed sockets
            _drop(k)
            if not last:
                _note(f"{path}: no answer ({type(e).__name__}); retry {attempt + 2}/{tries} in {delay:.0f} s")
                time.sleep(delay)
                delay = min(delay * 2, 120.0)
                continue
            return 0, f"connection failed: {type(e).__name__}: {e}".replace(key, "<key>")
        if status == 200:
            try:
                return 200, json.loads(raw.decode("utf-8"))
            except ValueError:
                return 0, "the answer was not JSON"
        text = raw.decode("utf-8", "replace")[:300].replace(key, "<key>")
        if status == 429 and not last:
            _note(f"{path}: 429 (token budget); retry {attempt + 2}/{tries} in 60 s")
            time.sleep(60)
            continue
        if status in RETRIED and not last:
            _note(f"{path}: HTTP {status}; retry {attempt + 2}/{tries} in {delay:.0f} s")
            time.sleep(delay)
            delay = min(delay * 2, 120.0)
            continue
        return status, text
    return 0, "no answer"
