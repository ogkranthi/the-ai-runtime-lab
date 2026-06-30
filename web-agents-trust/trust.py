"""Trust core for Field Lab 01.

One source-agnostic function, `judge`, takes a single Claim and its Evidence and
returns a Verdict of accept, reject, or review with a reason. It catches the four
ways web data breaks:

  stale         true once, not anymore, and the source is cached
  unsupported   evidence missing, walled, or does not back the claim
  conflicting   two sources disagree on a field that matters
  drift         the wrong field or the wrong company was grabbed

It knows nothing about the fit profile. Whether a true claim is a good fit is the
policy filter's job. Keeping the two apart is what keeps the layer from rotting.

The verdict carries a trace: every field's sources, what was checked, and what was
rejected and why. That trace is the observability output for the founder report.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from models import Claim, Evidence, Verdict

# How long a field stays fresh, in days. Time-sensitive fields expire fast; a
# product category barely moves. A field not listed uses DEFAULT_FRESHNESS_DAYS.
FRESHNESS_DAYS = {
    "reason_to_reach_out": 90,
    "eng_leader_contact": 180,
    "size": 365,
    "product_type": 730,
}
DEFAULT_FRESHNESS_DAYS = 3650

# Shape rules: a field whose value fails this is a wrong-field grab (drift), not a
# weak source. A headcount that carries no number was never a headcount.
SHAPE_RULES = {
    "size": lambda v: any(ch.isdigit() for ch in v),
}


def _parse(d: str) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date()


def _supports(ev: Evidence, value: str) -> bool:
    """True when this one source actually backs `value`.

    A source backs a value when it is not walled (has a snippet), it claims the
    same value, and that value shows up in the snippet text. Plausible is not
    verified.
    """
    if not ev.snippet or not ev.snippet.strip():
        return False  # walled or empty: nothing to read
    if ev.claimed_value is not None and ev.claimed_value.strip() != value.strip():
        return False  # the source supports a different value
    return value.strip().lower() in ev.snippet.lower()


def judge(claim: Claim, as_of: str) -> Verdict:
    """Decide whether one claim is true and supported as of `as_of`.

    `as_of` is passed in, never read from the clock, so the same claim always
    gets the same verdict. That is what makes the eval reproducible.
    """
    field = claim.field
    company = claim.company
    value = claim.value
    checks: List[str] = []
    sources = [e.source_url for e in claim.evidence]

    def out(decision: str, reason: str, break_kind: Optional[str] = None) -> Verdict:
        return Verdict(
            decision=decision,
            reason=reason,
            break_kind=break_kind,
            trace={
                "field": field,
                "company": company,
                "value": value,
                "sources": sources,
                "checks": checks,
                "rejected": None if decision == "accept" else reason,
            },
        )

    # No value or no evidence at all. A field with no source is a missing field.
    checks.append("evidence-present")
    if not value or not claim.evidence:
        return out("reject", "unsupported: no evidence attached to the claim", "unsupported")

    # Shape: a value that cannot be this field was grabbed from the wrong place.
    checks.append("value-shape")
    shape_ok = SHAPE_RULES.get(field, lambda v: True)(value)
    if not shape_ok:
        return out(
            "reject",
            f"extraction-drift: '{value}' is the wrong shape for {field}",
            "drift",
        )

    # Support: at least one source has to actually back the value.
    checks.append("value-supported")
    supporting = [e for e in claim.evidence if _supports(e, value)]
    if not supporting:
        return out(
            "reject",
            "unsupported: evidence is missing, walled, or does not back the value",
            "unsupported",
        )

    # Drift: the value is backed, but only by sources about a different company.
    checks.append("entity-match")
    supporting_on_entity = [e for e in supporting if e.entity == company]
    if not supporting_on_entity:
        wrong = next((e.entity for e in supporting if e.entity), "another company")
        return out(
            "reject",
            f"extraction-drift: evidence is about {wrong}, not {company}",
            "drift",
        )

    # Conflict: on-entity sources disagree on the value that matters.
    checks.append("source-agreement")
    on_entity_values = {
        e.claimed_value for e in claim.evidence
        if e.entity == company and e.claimed_value
    }
    if len(on_entity_values) > 1:
        pair = " vs ".join(sorted(on_entity_values))
        return out("review", f"conflicting: sources disagree ({pair})", "conflicting")

    # Stale: the freshest supporting source is older than the field's window.
    checks.append("freshness")
    window = FRESHNESS_DAYS.get(field, DEFAULT_FRESHNESS_DAYS)
    newest = max(_parse(e.fetched_at) for e in supporting_on_entity)
    age = (_parse(as_of) - newest).days
    if age > window:
        return out(
            "review",
            f"stale: evidence is {age} days old, past the {window}-day window for {field}",
            "stale",
        )

    return out(
        "accept",
        f"supported by {supporting_on_entity[0].source_url}, entity matches, fresh ({age}d old)",
    )


if __name__ == "__main__":
    demo = Claim(
        field="size",
        value="120 employees",
        company="Forge Labs",
        domain="forgelabs.io",
        evidence=[
            Evidence(
                source_url="https://forgelabs.io/about",
                snippet="Forge Labs is a team of 120 employees building developer tooling.",
                fetched_at="2026-06-12",
                claimed_value="120 employees",
                entity="Forge Labs",
            )
        ],
    )
    print(judge(demo, as_of="2026-06-30"))
