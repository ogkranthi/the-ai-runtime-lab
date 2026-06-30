"""Policy filter for Field Lab 01, module 1.

The thin growth layer. It runs only on values the trust core already accepted and
applies the fit rules from rubric.md: US-based, 50 to 300 people, developer-facing,
an engineering-leader contact, a real reason to reach out now.

It decides fit, never truth. Whether a claim is supported is the trust core's job,
and this filter must never re-judge it. Mixing the two is how the layer rots.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

# Accepted field values for one company, keyed by field name. A field the trust
# core did not accept is simply absent here, and an absent field fails its rule.
AcceptedFields = Dict[str, str]

DEV_FACING_KEYWORDS = [
    "developer", "api", "sdk", "ci/cd", "platform",
    "infrastructure", "observability", "tooling", "tools",
]
LEADER_TITLES = [
    "vp engineering", "vp of engineering", "head of engineering",
    "cto", "director of engineering",
]


@dataclass
class FitResult:
    """Does this company fit, and if not, exactly which rules failed."""

    company: str
    fits: bool
    gaps: List[str] = field(default_factory=list)


def _headcount(value: str):
    digits = re.findall(r"\d[\d,]*", value)
    return int(digits[0].replace(",", "")) if digits else None


def fits(company: str, accepted: AcceptedFields) -> FitResult:
    """Apply rubric v1 to one company's accepted fields.

    A missing field is a failed rule, not a pass. We degrade, we do not pad.
    """
    gaps: List[str] = []

    location = accepted.get("location", "")
    if not re.search(r"united states|\bus\b|u\.s\.", location, re.IGNORECASE):
        gaps.append("not confirmed US-based" if location else "no accepted location")

    size = accepted.get("size", "")
    head = _headcount(size) if size else None
    if head is None:
        gaps.append("no accepted headcount")
    elif not (50 <= head <= 300):
        gaps.append(f"headcount {head} outside 50 to 300")

    product = accepted.get("product_type", "")
    if not product:
        gaps.append("no accepted product type")
    elif not any(k in product.lower() for k in DEV_FACING_KEYWORDS):
        gaps.append(f"product '{product}' is not developer-facing")

    contact = accepted.get("eng_leader_contact", "")
    if not contact:
        gaps.append("no accepted engineering-leader contact")
    elif not any(t in contact.lower() for t in LEADER_TITLES):
        gaps.append(f"contact '{contact}' is not an engineering leader")

    reason = accepted.get("reason_to_reach_out", "")
    if not reason:
        gaps.append("no accepted reason to reach out")

    return FitResult(company=company, fits=not gaps, gaps=gaps)


if __name__ == "__main__":
    demo = {
        "location": "United States",
        "size": "120 employees",
        "product_type": "developer tools",
        "eng_leader_contact": "VP Engineering, Dana Reed",
        "reason_to_reach_out": "shipped a public API beta in June 2026",
    }
    print(fits("Forge Labs", demo))
