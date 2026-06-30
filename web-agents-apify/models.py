"""Data model for the module 1 sourcing agent.

Every sourced field carries its evidence: the source URL, the snippet it came
from, and when it was fetched. A field with no source is a missing field, not a
value. That is the only rule module 1 keeps.

Whether a sourced value is actually true, fresh, and a real fit is the job of the
reliability layer, and that is module 2.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Evidence:
    """Where a single field's value came from. No evidence, no value."""

    source_url: str
    snippet: str
    fetched_at: str  # ISO 8601 date, YYYY-MM-DD
    claimed_value: Optional[str] = None
    entity: Optional[str] = None


@dataclass
class SourcedField:
    """A value the agent found, plus the evidence that backs it."""

    value: str
    evidence: Evidence


@dataclass
class Prospect:
    """One company's prospect card: every field traces to a source, or is blank."""

    company: str
    domain: str
    fields: Dict[str, SourcedField] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
