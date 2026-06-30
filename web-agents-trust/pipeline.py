"""The reliability layer, Field Lab 01 module 2.

Module 1 hands over a prospect list that looks done: every field sourced, every
field cited. This module decides which of it is actually safe to act on.

  1. trust    judge every claim against its evidence (trust.py). Catch stale,
               unsupported, conflicting, and wrong-entity values.
  2. policy   apply the fit rubric to what survived (policy.py). Fit, never truth.
  3. reveal   show the contrast: the list looked done, here is what holds.

It degrades, it does not pad. A short list you can stand behind beats a full list
with junk in it.

    python pipeline.py     # offline, deterministic, no keys
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List

import present
from models import Claim, Evidence, Verdict
from policy import FitResult, fits
from trust import judge

HERE = os.path.dirname(os.path.abspath(__file__))
PROSPECTS = os.path.join(HERE, "fixtures", "prospects.json")

FIELD_ORDER = ["location", "size", "product_type", "eng_leader_contact", "reason_to_reach_out"]
VCOLOR = {"accept": present.GREEN, "review": present.YELLOW, "reject": present.RED}


@dataclass
class Review:
    """One company after the reliability layer, with the trace kept for the report."""

    company: str
    domain: str
    accepted: Dict[str, str] = field(default_factory=dict)
    verdicts: List[Verdict] = field(default_factory=list)
    fit: FitResult = None
    safe: bool = False


def _claim(company: str, domain: str, raw: dict) -> Claim:
    return Claim(
        field=raw["field"],
        value=raw["value"],
        company=company,
        domain=domain,
        evidence=[Evidence(**e) for e in raw["evidence"]],
    )


def run(path: str = PROSPECTS) -> List[Review]:
    """Run trust then policy over the prospect list and return per-company reviews."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    as_of = data["as_of"]

    reviews: List[Review] = []
    for company in data["companies"]:
        name, domain = company["company"], company["domain"]
        review = Review(company=name, domain=domain)

        # Trust gate: only accepted values move on. Everything else is a named gap.
        for raw in company["claims"]:
            verdict = judge(_claim(name, domain, raw), as_of=as_of)
            review.verdicts.append(verdict)
            if verdict.decision == "accept":
                review.accepted[raw["field"]] = raw["value"]

        # Policy runs only on what trust accepted, and decides fit, never truth.
        review.fit = fits(name, review.accepted)
        review.safe = review.fit.fits
        reviews.append(review)

    return reviews


def show(reviews: List[Review]) -> None:
    """The reveal: which of the candidates that looked done are safe to act on."""
    safe = [r for r in reviews if r.safe]

    print("\n" + present.rule("TRUST REVIEW  ·  which candidates are safe to act on"))
    print()

    overview = []
    for r in reviews:
        verified = sum(1 for v in r.verdicts if v.decision == "accept")
        status = ("SAFE", present.GREEN) if r.safe else ("HELD", present.RED)
        if r.safe:
            why = "every field verified and fits"
        else:
            why = (r.fit.gaps[0] if r.fit.gaps else "see detail below")
        overview.append([r.company, f"{verified}/{len(r.verdicts)}", status, why])
    print(present.table(
        ["company", "verified", "status", "why"], overview, caps=[16, 9, 6, 44],
    ))
    print()

    # For the held companies, show exactly what the trust core dropped and why.
    for r in reviews:
        if r.safe:
            continue
        print(present.style(f"{r.company} held back", present.BOLD, present.RED))
        detail = []
        for v in r.verdicts:
            if v.decision != "accept":
                detail.append([
                    v.trace.get("field", "?"),
                    (v.decision, VCOLOR.get(v.decision, "")),
                    v.reason,
                ])
        for gap in r.fit.gaps:
            detail.append(["fit", ("gap", present.YELLOW), gap])
        print(present.table(["field", "verdict", "why"], detail, caps=[20, 8, 50]))
        print()

    headline = f"{len(safe)} of {len(reviews)} safe to act on  ·  each backed by accepted evidence"
    print(present.banner(headline, present.GREEN))
    print()


if __name__ == "__main__":
    show(run())
