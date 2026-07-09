"""Minimal WebChat client: send a message, poll for the reply.

This talks to the local WebChat channel served by the compose network. The exact
HTTP shape depends on the pinned OpenClaw release; adjust the two endpoint paths
below if the pinned release differs, and note the change in VERSION.md.

If the gateway is unreachable, the caller should treat the run as blocked, not
failed. `gateway_up` exists so a repro can check first and record a clean blocked
outcome with a reason.
"""
from __future__ import annotations

import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


class Blocked(Exception):
    """Raised when the environment prevents the attempt (gateway down, etc.)."""


def gateway_up(webchat_url: str, timeout: float = 3.0) -> bool:
    try:
        req = urllib.request.Request(webchat_url.rstrip("/") + "/health", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 500
    except Exception:
        return False


def _post(url: str, payload: Dict[str, Any], timeout: float = 60.0) -> Dict[str, Any]:
    import json
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.URLError as exc:
        raise Blocked(f"WebChat unreachable at {url}: {exc}") from exc


def send_message(webchat_url: str, agent: str, text: str,
                 attachments: Optional[List[Dict[str, Any]]] = None) -> str:
    """Send one WebChat message to the named agent. Returns a conversation id."""
    base = webchat_url.rstrip("/")
    resp = _post(base + "/api/send", {
        "agent": agent,
        "text": text,
        "attachments": attachments or [],
    })
    conv = resp.get("conversation_id") or resp.get("conversation") or resp.get("id")
    if not conv:
        raise Blocked(f"WebChat send returned no conversation id: {resp}")
    return conv


def poll_reply(webchat_url: str, conversation_id: str, timeout: float = 60.0,
               interval: float = 2.0) -> Dict[str, Any]:
    """Poll for the assistant reply. Returns the reply object, possibly empty."""
    base = webchat_url.rstrip("/")
    deadline = time.time() + timeout
    last: Dict[str, Any] = {}
    while time.time() < deadline:
        import json
        req = urllib.request.Request(
            base + f"/api/conversation/{conversation_id}", method="GET")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                last = json.loads(resp.read().decode("utf-8") or "{}")
        except urllib.error.URLError as exc:
            raise Blocked(f"WebChat poll failed: {exc}") from exc
        if last.get("done") or last.get("assistant_text") is not None or last.get("error"):
            return last
        time.sleep(interval)
    return last
