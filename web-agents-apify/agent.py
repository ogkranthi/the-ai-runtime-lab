"""End-to-end sourcing agent for Field Lab 01, module 1.

The use case: a B2B SaaS founder hands the agent a seed list of target companies
and wants a weekly list of qualified design-partner candidates. The agent works
each company as an agent, not a fixed pipeline:

  1. plan     ask the model which Apify Actor to run next, given the open gaps
  2. source   run that Actor through the data plane to pull public pages
  3. extract  the model pulls each rubric field with a verbatim evidence snippet
  4. verify   the trust core judges every claim; only accepted values are kept
  5. iterate  if a required field is still open, take another sourcing action
  6. qualify  apply the fit rubric to what survived, and report

It degrades, it does not pad. It hands over the companies it can stand behind and
names the exact gap on the rest. Run offline by default (mock model and source,
no keys), or `--live` against real Apify and a real model.

    python agent.py            # offline, verifiable, no keys
    python agent.py --live     # real Apify Actors and a real model
"""
from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from llm import LLMModel, MockModel, Model
from models import Claim, Evidence, Verdict
from policy import FitResult, fits
from source import ACTORS, ApifySource, MockSource
from trust import judge

# The fields the rubric scores, each with a short spec the model extracts against.
FIELDS = [
    ("location", "the country the company is headquartered in"),
    ("size", "employee headcount, for example '120 employees'"),
    ("product_type", "what the product is, for example 'developer tools'"),
    ("eng_leader_contact", "an engineering leader's title and name"),
    ("reason_to_reach_out", "a recent, specific event worth reaching out about now"),
]
MAX_ACTIONS = 3  # sourcing actions per company before the agent gives up


@dataclass
class CompanyResult:
    """One company after the full agent loop, with the trace kept for the report."""

    company: str
    domain: str
    accepted: Dict[str, str] = field(default_factory=dict)
    verdicts: List[Verdict] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    fit: FitResult = None  # set after policy
    qualified: bool = False


def work_company(company: str, domain: str, model: Model, source, as_of: str) -> CompanyResult:
    """Run the agent loop for a single company until its gaps close or budget runs out."""
    evidence_by_field: Dict[str, List[Evidence]] = defaultdict(list)
    value_by_field: Dict[str, str] = {}
    verdict_by_field: Dict[str, Verdict] = {}
    actions: List[str] = []
    tried: List[str] = []

    def open_gaps() -> List[str]:
        return [
            name for name, _ in FIELDS
            if name not in verdict_by_field or verdict_by_field[name].decision != "accept"
        ]

    for _ in range(MAX_ACTIONS):
        gaps = open_gaps()
        if not gaps:
            break

        plan = model.plan(company, domain, gaps, ACTORS, tried)
        actor = plan.get("actor", "stop")
        if actor not in ACTORS or actor in tried:
            actions.append(f"stop: {plan.get('rationale', 'no further action')}")
            break
        tried.append(actor)

        pages = source.run(actor, company, domain)
        actions.append(f"ran {actor} ({len(pages)} pages): {plan.get('rationale', '')}".strip())

        # Extract evidence-bearing fields, then re-judge everything we now hold.
        for hit in model.extract(company, pages, FIELDS):
            f = hit["field"]
            evidence_by_field[f].append(hit["evidence"])
            value_by_field.setdefault(f, hit["value"])

        for f, evidence in evidence_by_field.items():
            claim = Claim(field=f, value=value_by_field[f], company=company,
                          domain=domain, evidence=evidence)
            verdict_by_field[f] = judge(claim, as_of=as_of)

    accepted = {
        f: value_by_field[f]
        for f, v in verdict_by_field.items() if v.decision == "accept"
    }
    fit = fits(company, accepted)
    return CompanyResult(
        company=company, domain=domain, accepted=accepted,
        verdicts=list(verdict_by_field.values()), actions=actions,
        fit=fit, qualified=fit.fits,
    )


# A weekly seed list: the founder's watchlist of target companies.
SEED_LIST = [
    ("Forge Labs", "forgelabs.io"),
    ("Quantal", "quantal.dev"),
    ("Mega Corp", "megacorp.com"),
    ("Helios CRM", "helios.app"),
]


def run(live: bool = False, seed_list=SEED_LIST) -> List[CompanyResult]:
    """Run the agent over the seed list. Offline by default, live with keys."""
    if live:
        model: Model = LLMModel()
        source = ApifySource()
        as_of = MockSource().as_of  # a real run would stamp today's date here
    else:
        model = MockModel()
        source = MockSource()
        as_of = source.as_of

    return [work_company(c, d, model, source, as_of) for c, d in seed_list]


def _summary(results: List[CompanyResult]) -> str:
    qualified = [r for r in results if r.qualified]
    lines = [f"qualified {len(qualified)}/{len(results)} companies", ""]
    for r in results:
        mark = "QUALIFIED" if r.qualified else "degraded "
        lines.append(f"{mark}  {r.company} ({r.domain})")
        for step in r.actions:
            lines.append(f"            step {step}")
        for v in r.verdicts:
            if v.decision != "accept":
                lines.append(f"            dropped {v.trace['field']}: {v.reason}")
        for gap in r.fit.gaps:
            lines.append(f"            gap {gap}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(_summary(run(live="--live" in sys.argv)))
