"""Source layer for Field Lab 01.

Apify is the data plane. This module pulls the public signals the rubric scores
for one target company and returns a record where every field carries its
evidence. It does not judge truth or fit. The trust core decides whether a claim
is supported; the policy filter decides whether a true claim fits. Both are built
at the workshop, on top of what this returns.

Lab page: https://lab.theairuntime.com/01/
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from apify_client import ApifyClient


@dataclass
class Evidence:
    """Where a single field's value came from. No evidence, no value."""

    source_url: str
    snippet: str
    fetched_at: str  # ISO 8601 UTC


@dataclass
class Field:
    """A scored field plus the evidence that backs it.

    `value` stays None until a source supports it.
    """

    value: Optional[str] = None
    evidence: Optional[Evidence] = None


@dataclass
class CandidateRecord:
    """One company, one record. Each field traces to a source or stays empty."""

    company: str
    domain: str
    size: Field = field(default_factory=Field)
    product_type: Field = field(default_factory=Field)
    eng_leader_contact: Field = field(default_factory=Field)
    reason_to_reach_out: Field = field(default_factory=Field)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _client() -> ApifyClient:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise SystemExit("Set APIFY_TOKEN first (see .env.example).")
    return ApifyClient(token)


def fetch_company(company: str, domain: str) -> CandidateRecord:
    """Pull the public signals the rubric scores for one company.

    TODO (workshop): wire each field below to a real Apify Actor result and
    attach its Evidence. Leave a field empty when no source supports it. Do not
    guess. The smallest honest record beats a full record with invented values.
    """
    client = _client()

    # Example: crawl the company site for first-pass signals. Replace or add
    # Actors (job boards, public profiles, press) as the rubric needs.
    run = client.actor("apify/website-content-crawler").call(
        run_input={
            "startUrls": [{"url": f"https://{domain}"}],
            "maxCrawlPages": 5,
        },
    )
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    record = CandidateRecord(company=company, domain=domain)

    # Each extracted field MUST set value and evidence together, for example:
    #
    #   page = items[0]
    #   record.product_type = Field(
    #       value="developer tools",
    #       evidence=Evidence(
    #           source_url=page["url"],
    #           snippet=page["text"][:280],
    #           fetched_at=_now(),
    #       ),
    #   )
    #
    # Until you wire it, fields stay empty, which is the honest default.
    _ = items  # placeholder so a first run does something visible

    return record


if __name__ == "__main__":
    rec = fetch_company("Example Co", "example.com")
    print(rec)
