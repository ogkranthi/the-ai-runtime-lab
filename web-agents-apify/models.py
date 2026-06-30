"""Shared data model for Field Lab 01.

Three layers share these types:

- The source layer (`source.py`) emits CandidateRecords whose fields each carry
  Evidence.
- The trust core (`trust.py`) judges a single Claim and its Evidence and returns
  a Verdict. It knows nothing about fit.
- The policy filter (`policy.py`) reads accepted values and decides fit.

Evidence is the spine. A value with no evidence is a missing field, not a value.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Evidence:
    """Where a single field's value came from. No evidence, no value.

    `claimed_value` is the value this particular source supports. Two sources
    with different `claimed_value` for the same field is a conflict. `entity` is
    the company the source is actually about, which is how extraction-drift gets
    caught: evidence about the wrong company does not back a claim.
    """

    source_url: str
    snippet: str
    fetched_at: str  # ISO 8601 date, YYYY-MM-DD
    claimed_value: Optional[str] = None
    entity: Optional[str] = None


@dataclass
class Field:
    """A scored field plus the single piece of evidence that backs it.

    `value` stays None until a source supports it.
    """

    value: Optional[str] = None
    evidence: Optional[Evidence] = None


@dataclass
class CandidateRecord:
    """One company, one record. Each field traces to a source or stays empty."""

    company: str
    domain: str
    location: Field = field(default_factory=Field)
    size: Field = field(default_factory=Field)
    product_type: Field = field(default_factory=Field)
    eng_leader_contact: Field = field(default_factory=Field)
    reason_to_reach_out: Field = field(default_factory=Field)


@dataclass
class Claim:
    """A single field's value about one company, plus every source for it.

    The trust core judges one Claim at a time. `evidence` is a list so the core
    can see source disagreement, not just a single citation.
    """

    field: str
    value: Optional[str]
    company: str
    domain: str = ""
    evidence: List[Evidence] = field(default_factory=list)


@dataclass
class Verdict:
    """The trust core's answer for one claim.

    `decision` is one of accept, reject, review. `reason` is always populated,
    including on accept, so every record can explain itself. `trace` is the
    observability record: what was checked and what was rejected and why.
    """

    decision: str  # "accept" | "reject" | "review"
    reason: str
    break_kind: Optional[str] = None  # stale | unsupported | conflicting | drift
    trace: dict = field(default_factory=dict)
