"""Structural checks over captured provider bodies.

Small helpers the per-issue assert.py scripts share, so the walk logic lives in
one place.
"""
from __future__ import annotations

from typing import Any, Iterator, List

UNSUPPORTED_ANTHROPIC_MEDIA = {"image/heic", "image/heif", "image/tiff"}


def _walk(obj: Any) -> Iterator[Any]:
    yield obj
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def media_types(body: Any) -> List[str]:
    """Every media_type string found anywhere in a request body."""
    found = []
    for node in _walk(body):
        if isinstance(node, dict):
            mt = node.get("media_type") or node.get("mimeType") or node.get("mime_type")
            if isinstance(mt, str):
                found.append(mt)
    return found


def has_tool_result_image(body: Any) -> bool:
    """True if a tool_result block in the body carries an image block."""
    for node in _walk(body):
        if isinstance(node, dict) and node.get("type") == "tool_result":
            for inner in _walk(node.get("content")):
                if isinstance(inner, dict) and inner.get("type") == "image":
                    return True
    return False


def refusal_present(body: Any) -> bool:
    """True if an OpenAI-style refusal field is present and non-empty."""
    for node in _walk(body):
        if isinstance(node, dict):
            r = node.get("refusal")
            if isinstance(r, str) and r.strip():
                return True
    return False
