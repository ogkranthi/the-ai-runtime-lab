"""End-to-end sourcing agent for Field Lab 01, module 1.

Wires the three layers into one run:

  source   pull public signals with evidence on every field (source.py, or the
           offline sample batch so this runs with no Apify token)
  trust    judge each claim and keep only what is true and supported (trust.py)
  policy   apply the fit rubric to the accepted values (policy.py)

The output is a prospect list where every kept field traces to a source, plus a
degrade list: the companies we cannot stand behind and exactly why. We hand over
what holds and name the gaps. A short honest list beats a full list with junk.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List

from models import Claim, Evidence, Verdict
from policy import FitResult, fits
from trust import judge

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE_BATCH = os.path.join(HERE, "fixtures", "sample_batch.json")


@dataclass
class CompanyResult:
    """One company after all three layers, with the trace kept for the report."""

    company: str
    domain: str
    accepted: Dict[str, str] = field(default_factory=dict)
    verdicts: List[Verdict] = field(default_factory=list)
    fit: FitResult = None  # set after policy
    qualified: bool = False


def _claim(company: str, domain: str, raw: dict) -> Claim:
    return Claim(
        field=raw["field"],
        value=raw["value"],
        company=company,
        domain=domain,
        evidence=[Evidence(**e) for e in raw["evidence"]],
    )


def run(batch_path: str = SAMPLE_BATCH) -> List[CompanyResult]:
    """Run source, trust, and policy over one batch and return per-company results."""
    with open(batch_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    as_of = data["as_of"]

    results: List[CompanyResult] = []
    for company in data["companies"]:
        name, domain = company["company"], company["domain"]
        res = CompanyResult(company=name, domain=domain)

        # Trust gate: only accepted values move on. Everything else is a named gap.
        for raw in company["claims"]:
            verdict = judge(_claim(name, domain, raw), as_of=as_of)
            res.verdicts.append(verdict)
            if verdict.decision == "accept":
                res.accepted[raw["field"]] = raw["value"]

        # Policy runs only on what trust accepted, and decides fit, never truth.
        res.fit = fits(name, res.accepted)
        res.qualified = res.fit.fits
        results.append(res)

    return results


def _summary(results: List[CompanyResult]) -> str:
    qualified = [r for r in results if r.qualified]
    lines = [f"qualified {len(qualified)}/{len(results)} companies", ""]
    for r in results:
        mark = "QUALIFIED" if r.qualified else "degraded "
        lines.append(f"{mark}  {r.company}")
        for v in r.verdicts:
            if v.decision != "accept":
                lines.append(f"            dropped {v.trace['field']}: {v.reason}")
        for gap in r.fit.gaps:
            lines.append(f"            gap {gap}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(_summary(run()))
