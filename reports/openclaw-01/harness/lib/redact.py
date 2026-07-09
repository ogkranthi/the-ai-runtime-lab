"""Redaction shared by the capture proxy and the evidence helpers.

One source of truth for what a secret looks like, so the proxy that writes
evidence and the checks that verify it agree.
"""
from __future__ import annotations

import re
from typing import Any

# Patterns for key-shaped material. Kept deliberately broad; a false positive
# costs nothing here, a missed secret costs a leak.
KEY_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),          # OpenAI and Anthropic style
    re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),          # Google api keys
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]{16,}", re.IGNORECASE),
    re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}"),    # chat token style, never expected here
    re.compile(r"AKIA[0-9A-Z]{16}"),                 # aws access key id
]

REDACTED = "REDACTED"

# Header names that must never appear in evidence at all.
SECRET_HEADERS = {"authorization", "x-api-key", "x-goog-api-key", "api-key", "cookie"}


def redact_text(text: str) -> str:
    for pattern in KEY_PATTERNS:
        text = pattern.sub(REDACTED, text)
    return text


def redact_obj(obj: Any) -> Any:
    """Recursively redact strings inside a JSON-like object."""
    if isinstance(obj, str):
        return redact_text(obj)
    if isinstance(obj, list):
        return [redact_obj(x) for x in obj]
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(k, str) and k.lower() in SECRET_HEADERS:
                out[k] = REDACTED
            else:
                out[k] = redact_obj(v)
        return out
    return obj
