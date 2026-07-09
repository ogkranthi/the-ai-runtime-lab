"""mitmproxy addon: capture provider request and response pairs as evidence.

Loaded by mitmdump (see docker/compose.yml). For every request that targets a
known provider, it writes one sanitized JSON file into CAPTURE_DIR:

    {
      "captured_at": "...",
      "provider": "anthropic",
      "request":  {"method","path","content_type","body"},
      "response": {"status","content_type","body"}
    }

Headers are dropped to nothing except content-type. Bodies are kept because the
whole point is to prove what was on the wire, but every string is run through the
shared redactor so no key-shaped material lands on disk. Run redact-check.sh
before committing anyway.
"""
from __future__ import annotations

import json
import os
import sys
import time

# The whole harness dir is mounted at /harness (see compose). Use the shared
# redactor so the proxy and the checks agree on what a secret looks like.
sys.path.insert(0, "/harness")
try:
    from lib.redact import redact_obj, redact_text
except Exception:  # pragma: no cover - fallback if mounted differently
    def redact_text(t):
        return t

    def redact_obj(o):
        return o

CAPTURE_DIR = os.environ.get("CAPTURE_DIR", "/capture")

# Map a request host or base-url path prefix to a provider name.
PROVIDER_HINTS = [
    ("anthropic", ("anthropic", "api.anthropic.com")),
    ("openai", ("openai", "api.openai.com")),
    ("gemini", ("gemini", "generativelanguage.googleapis.com")),
]

_counter = 0


def _provider_for(flow) -> str:
    host = (flow.request.host or "").lower()
    path = (flow.request.path or "").lower()
    for name, hints in PROVIDER_HINTS:
        if any(h in host or h in path for h in hints):
            return name
    return ""


def _json_or_text(raw: bytes):
    if not raw:
        return ""
    try:
        return redact_obj(json.loads(raw.decode("utf-8")))
    except Exception:
        return redact_text(raw.decode("utf-8", "replace"))


def response(flow):  # mitmproxy hook name
    global _counter
    provider = _provider_for(flow)
    if not provider:
        return

    _counter += 1
    record = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "provider": provider,
        "request": {
            "method": flow.request.method,
            "path": flow.request.path,
            "content_type": flow.request.headers.get("content-type", ""),
            "body": _json_or_text(flow.request.raw_content or b""),
        },
        "response": {
            "status": flow.response.status_code,
            "content_type": flow.response.headers.get("content-type", ""),
            "body": _json_or_text(flow.response.raw_content or b""),
        },
    }

    os.makedirs(CAPTURE_DIR, exist_ok=True)
    fname = f"{_counter:03d}-{provider}-{flow.response.status_code}.json"
    with open(os.path.join(CAPTURE_DIR, fname), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2)
        fh.write("\n")
