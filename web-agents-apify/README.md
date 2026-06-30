# Apify data plane, Field Lab 01

Apify-specific code for The AI Runtime Field Lab 01, "A Reliability Layer for
Web-Grounded Agents." Apify is the data plane: the Actors and datasets that feed
the sourcing agent. Everything in this folder is the source layer only. The
trust core, the policy filter, and the eval are what you build at the workshop.

Lab page: https://lab.theairuntime.com/01/

## What is here

- `smoke.py`      a thirty-second check that your Apify token works
- `source.py`     the source layer: pull public signals and attach evidence
- `requirements.txt`
- `.env.example`  copy to `.env` and add your token

## Setup

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env   # then add your APIFY_TOKEN

## Run the smoke test

    python smoke.py

It should print `apify ok: SUCCEEDED`. If it does not, fix that before the
workshop, not at minute five of the build.

## The one rule this folder follows

Every field the source layer returns carries its evidence: the source URL, the
exact snippet it came from, and a `fetched_at` timestamp. Plausible is not
verified. A field with no source is a missing field, not a value. That evidence
is exactly what the trust core checks next.
