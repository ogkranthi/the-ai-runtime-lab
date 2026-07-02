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

    python agent.py                                       # offline, no keys, full loop
    python agent.py --live --the-ai-runtime               # live, real watchlist
    python agent.py --live --company "Acme" --domain acme.com  # live, one company

The offline watchlist is fictional. The --the-ai-runtime flag points a live run at
a set of real companies, and --company / --domain runs a single company inline.
"""
from __future__ import annotations

import sys
from typing import List

import present
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

# The offline demo watchlist. These companies are FICTIONAL: they exist only in
# the offline crawl fixture, so they resolve with `python agent.py` but not in a
# live run. For `--live`, use --the-ai-runtime to source real companies.
SEED_LIST = [
    ("Forge Labs", "forgelabs.io"),
    ("Quantal", "quantal.dev"),
    ("Mega Corp", "megacorp.com"),
    ("Helios CRM", "helios.app"),
]


# Real companies for a live run: the The AI Runtime watchlist. The
# --the-ai-runtime flag selects these, and a live run uses them by default, since
# the demo companies above are fictional and do not resolve on the web.
THE_AI_RUNTIME_SEEDS = [
    ("Sentry", "sentry.io"),
    ("PostHog", "posthog.com"),
    ("Supabase", "supabase.com"),
    ("Tailscale", "tailscale.com"),
]


def _short(text: str, n: int = 96) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


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
            log(f"    stop: {_short(rationale)}")
            break
        tried.append(actor)

        log(f"    plan -> {actor}: {_short(rationale)}")
        pages = source.run(actor, company, domain)
        for hit in model.extract(company, pages, FIELDS):
            prospect.fields.setdefault(
                hit["field"], SourcedField(value=hit["value"], evidence=hit["evidence"])
            )

        found = len(prospect.fields)
        prospect.actions.append(f"ran {actor}: {rationale}")
        log(f"    crawled {len(pages)} pages, sourced {found}/{len(FIELDS)} fields")

    return prospect


def run(live: bool = False, seed_list=None, log=print) -> List[Prospect]:
    """Source every company on the seed list. Offline by default, live with keys.

    Offline uses the fictional demo watchlist. Live defaults to the real The AI
    Runtime watchlist, since the demo companies do not resolve on the web.
    """
    if live:
        model: Model = LLMModel()
        source = ApifySource()
        if seed_list is None:
            seed_list = THE_AI_RUNTIME_SEEDS
    else:
        model = MockModel()
        source = MockSource()
        if seed_list is None:
            seed_list = SEED_LIST

    log(f"Sourcing {len(seed_list)} target companies for design-partner fit...")
    return [work_company(c, d, model, source, log=log) for c, d in seed_list]


def _short_url(url: str) -> str:
    return url.replace("https://", "").replace("http://", "")


def show(prospects: List[Prospect]) -> None:
    """The deliverable: a clean, boxed prospect list, a source on every field."""
    total = sum(len(p.fields) for p in prospects)
    possible = len(prospects) * len(FIELDS)

    print("\n" + present.rule("PROSPECT LIST  ·  design-partner candidates"))
    print()
    for p in prospects:
        found = len(p.fields)
        count = present.style(f"{found}/{len(FIELDS)}", present.GREEN if found == len(FIELDS) else present.YELLOW)
        title = present.style(f"{p.company}", present.BOLD, present.CYAN)
        print(f"{title}  {present.style(p.domain, present.DIM)}  {count}")
        rows = []
        for name, _ in FIELDS:
            sf = p.fields.get(name)
            if sf:
                rows.append([
                    LABELS[name],
                    (sf.value, present.GREEN),
                    (_short_url(sf.evidence.source_url), present.DIM),
                ])
            else:
                rows.append([LABELS[name], ("not found", present.DIM), ""])
        print(present.table(["field", "value", "source"], rows, caps=[20, 46, 40]))
        print()

    # An honest banner: celebrate a full sweep, flag a partial one, call out empty.
    if total == possible:
        print(present.banner(f"✓  all {possible} fields sourced and cited", present.GREEN))
    elif total > 0:
        print(present.banner(
            f"{total}/{possible} fields sourced and cited  ·  the rest had no public source",
            present.YELLOW,
        ))
    else:
        print(present.banner(
            "0 fields sourced  ·  check the domains are real and reachable",
            present.YELLOW,
        ))
    print()


def _arg_value(argv: List[str], flag: str):
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


def _seeds_from_argv(argv: List[str]):
    """Pick the seed list from the flags, or None to use run()'s default."""
    company = _arg_value(argv, "--company")
    if company:
        # One company inline. --domain is optional; fall back to the name.
        return [(company, _arg_value(argv, "--domain") or company)]
    if "--the-ai-runtime" in argv:
        return THE_AI_RUNTIME_SEEDS
    return None


if __name__ == "__main__":
    show(run(live="--live" in sys.argv, seed_list=_seeds_from_argv(sys.argv)))
