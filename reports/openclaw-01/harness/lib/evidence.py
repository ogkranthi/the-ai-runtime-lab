"""Evidence helpers: load captured payloads and write summary.json.

Every repro writes the same summary.json shape so run-all.sh can build one table
from all four. `reproduced` is true, false, or blocked. Blocked is a legitimate
outcome and must carry a reason.
"""
from __future__ import annotations

import json
import os
from datetime import date
from typing import Any, Dict, List

VALID_REPRODUCED = {"true", "false", "blocked"}


def load_captures(evidence_dir: str) -> List[Dict[str, Any]]:
    """Load every sanitized capture JSON in an evidence dir, sorted by filename.

    Skips summary.json and anything under a raw/ subdir.
    """
    captures = []
    if not os.path.isdir(evidence_dir):
        return captures
    for name in sorted(os.listdir(evidence_dir)):
        if name == "summary.json" or not name.endswith(".json"):
            continue
        path = os.path.join(evidence_dir, name)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as fh:
            try:
                captures.append(json.load(fh))
            except json.JSONDecodeError:
                continue
    return captures


def provider_requests(captures: List[Dict[str, Any]], provider: str) -> List[Dict[str, Any]]:
    return [c for c in captures if c.get("provider") == provider]


def write_summary(evidence_dir: str, *, issue: str, title: str, openclaw_version: str,
                  model_target: str, reproduced: str, observed: str, expected: str,
                  reason: str = "", run_date: str = "") -> Dict[str, Any]:
    """Write summary.json and return it. reproduced must be true|false|blocked."""
    if reproduced not in VALID_REPRODUCED:
        raise ValueError(f"reproduced must be one of {VALID_REPRODUCED}, got {reproduced!r}")
    if reproduced == "blocked" and not reason:
        raise ValueError("a blocked outcome must include a reason")

    os.makedirs(evidence_dir, exist_ok=True)
    evidence_files = sorted(
        name for name in os.listdir(evidence_dir)
        if name.endswith(".json") and name != "summary.json"
    )
    summary = {
        "issue": issue,
        "title": title,
        "openclaw_version": openclaw_version,
        "model_target": model_target,
        "reproduced": reproduced,
        "observed": observed,
        "expected": expected,
        "evidence_files": evidence_files,
        "run_date": run_date or date.today().isoformat(),
    }
    if reason:
        summary["reason"] = reason
    with open(os.path.join(evidence_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return summary
