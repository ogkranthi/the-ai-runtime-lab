"""The sourcing agent, Field Lab 01 module 1.

Give it a list of target companies. For each one it works like an agent, not a
script:

  1. plan     ask the model which Apify Actor to run next, given what is missing
  2. source   run that Actor through the data plane to pull public pages
  3. extract  the model pulls each rubric field with the exact snippet it came from
  4. iterate  if a field is still missing, take another sourcing action
  5. present  a prospect card per company, every field traced to a source

That is the whole of module 1: point it at the web, get back a clean, cited
prospect list. The list looks done.

Whether each value is actually true, fresh, and a real fit is the next question,
and that is the reliability layer you build in module 2.

    python agent.py            # offline, no keys, runs the full loop
    python agent.py --live     # real Apify Actors and a real model
"""
from __future__ import annotations

import sys
from typing import List

from llm import LLMModel, MockModel, Model
from models import Prospect, SourcedField
from source import ACTORS, ApifySource, MockSource

# The fields the customer frame asks for, each with a spec the model extracts to.
FIELDS = [
    ("location", "the country the company is headquartered in"),
    ("size", "employee headcount, for example '120 employees'"),
    ("product_type", "what the product is, for example 'developer tools'"),
    ("eng_leader_contact", "an engineering leader's title and name"),
    ("reason_to_reach_out", "a recent, specific event worth reaching out about now"),
]
LABELS = {
    "location": "location",
    "size": "size",
    "product_type": "product",
    "eng_leader_contact": "engineering lead",
    "reason_to_reach_out": "reason to reach out",
}
MAX_ACTIONS = 3  # sourcing actions per company before the agent moves on

# A weekly seed list: the founder's watchlist of target companies.
SEED_LIST = [
    ("Forge Labs", "forgelabs.io"),
    ("Quantal", "quantal.dev"),
    ("Mega Corp", "megacorp.com"),
    ("Helios CRM", "helios.app"),
]


def work_company(company: str, domain: str, model: Model, source, log=print) -> Prospect:
    """Run the agent loop for one company until its card is full or budget runs out."""
    prospect = Prospect(company=company, domain=domain)
    tried: List[str] = []

    log(f"\n  {company} ({domain})")
    for _ in range(MAX_ACTIONS):
        missing = [name for name, _ in FIELDS if name not in prospect.fields]
        if not missing:
            break

        plan = model.plan(company, domain, missing, ACTORS, tried)
        actor = plan.get("actor", "stop")
        rationale = plan.get("rationale", "")
        if actor not in ACTORS or actor in tried:
            prospect.actions.append(f"stop: {rationale}")
            log(f"    stop: {rationale}")
            break
        tried.append(actor)

        pages = source.run(actor, company, domain)
        for hit in model.extract(company, pages, FIELDS):
            prospect.fields.setdefault(
                hit["field"], SourcedField(value=hit["value"], evidence=hit["evidence"])
            )

        found = len(prospect.fields)
        prospect.actions.append(f"ran {actor}: {rationale}")
        log(f"    plan -> {actor}: {rationale}")
        log(f"    crawled {len(pages)} pages, sourced {found}/{len(FIELDS)} fields")

    return prospect


def run(live: bool = False, seed_list=SEED_LIST, log=print) -> List[Prospect]:
    """Source every company on the seed list. Offline by default, live with keys."""
    if live:
        model: Model = LLMModel()
        source = ApifySource()
    else:
        model = MockModel()
        source = MockSource()

    log(f"Sourcing {len(seed_list)} target companies for design-partner fit...")
    return [work_company(c, d, model, source, log=log) for c, d in seed_list]


def present(prospects: List[Prospect]) -> str:
    """The deliverable: a clean prospect list with a source on every field."""
    total_fields = sum(len(p.fields) for p in prospects)
    lines = [
        "",
        "=" * 60,
        "PROSPECT LIST",
        "=" * 60,
        f"{len(prospects)} candidates, {total_fields} fields, every one traced to a source.",
        "",
    ]
    for p in prospects:
        lines.append(f"{p.company}  ({p.domain})")
        for name, _ in FIELDS:
            label = LABELS[name]
            sf = p.fields.get(name)
            if sf:
                lines.append(f"  {label:<22}{sf.value}")
                lines.append(f"  {'':<22}via {sf.evidence.source_url}")
            else:
                lines.append(f"  {label:<22}(not found)")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    prospects = run(live="--live" in sys.argv)
    print(present(prospects))
