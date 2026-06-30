# web-agents-apify, Field Lab 01

The full reference build for The AI Runtime Field Lab 01, "A Reliability Layer
for Web-Grounded Agents." Apify is the data plane: the Actors and datasets that
feed the sourcing agent. On top of it sits the artifact the lab is really about,
a source-agnostic trust core that decides which web claims are safe to act on.

The whole pipeline runs end to end with no model key. The trust core is
deterministic, so the eval produces the same safe-to-act number every run.

Lab page: https://lab.theairuntime.com/01/

## The two modules

**Module 1, the use-case agent end to end.** The founder hands the agent a seed
list of target companies. For each one the agent runs a loop: plan which Apify
Actor to run, source public pages, extract each rubric field with a verbatim
evidence snippet, gate every claim through the trust core, and take another
sourcing action if a required field is still open. It produces a prospect list
where every field traces to a source.

**Module 2, evals and prod-ready.** Grade the trust core against the Dirty
Thirty trap set on two numbers, then turn a live run into a founder report with
the provenance in plain sight and one headline number.

## What is here

Module 1, the agent:

- `rubric.md`   the fit profile as explicit, checkable rules (rubric v1)
- `agent.py`    the agent loop: plan, source, extract, verify, iterate, qualify
- `llm.py`      the model layer: a live model (Anthropic or OpenRouter) or an offline mock
- `source.py`   the data plane: run Apify Actors, or replay the offline fixture
- `trust.py`    the trust core: judge one claim and its evidence, catch the four breaks
- `policy.py`   the fit filter, applied only to what the trust core accepted

Module 2, evals and report:

- `eval.py`     grade the trust core against the Dirty Thirty
- `report.py`   the founder-facing trust report
- `fixtures/dirty_thirty.json`   thirty frozen claims, ten clean and twenty planted
- `fixtures/crawl_pages.json`    an offline crawl fixture so the agent runs with no keys

Shared:

- `models.py`   the data model: Evidence, Claim, Verdict, and the record types
- `smoke.py`    a thirty-second check that your Apify token works
- `requirements.txt`, `.env.example`

## Setup (VS Code terminal)

These steps use the VS Code integrated terminal (open it with
`Terminal > New Terminal`). Every command is plain shell, so any terminal works
the same way.

### 1. Clone the repo and open it in VS Code

    git clone https://github.com/ogkranthi/the-ai-runtime-lab
    cd the-ai-runtime-lab/web-agents-apify

In VS Code: `File > Open Folder` and pick `the-ai-runtime-lab`, then open the
integrated terminal and `cd web-agents-apify`.

### 2. Create the environment and install

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt

On Windows, activate with `.venv\Scripts\activate` instead of the `source` line.

### 3. Add your token (only needed for live Apify)

    cp .env.example .env

Open `.env` in VS Code and paste your `APIFY_TOKEN`. Get one at
https://console.apify.com/account/integrations. The token stays in `.env` and
never goes in the code. The eval, the agent, and the report all run offline
without it.

## Run module 1, the agent end to end

    python agent.py

Runs the agent loop over the seed list using the offline mock model and crawl
fixture, so it needs no keys. For each company it prints the sourcing actions it
took, what the trust core dropped, and the fit gaps. Expected: `qualified 2/4
companies`. Watch Quantal take a second action (the jobs board) to fill its
reason-to-reach-out gap, and Helios get held back on a conflicting headcount.

Run it live against real Apify Actors and a real model:

    python smoke.py            # first confirm the token: apify ok: SUCCEEDED
    python agent.py --live     # needs APIFY_TOKEN and a model key

In live mode the model plans the Actors and extracts fields from the crawled
text; everything else is identical. The trust core stays deterministic, so the
verification step does not drift.

## Run module 2, evals and report

    python eval.py

Grades the trust core against the Dirty Thirty and prints a verdict per record
plus the scorecard. Expected: `RESULT: PASS`, caught 20/20 bad, kept 10/10
accepted clean.

    python report.py

Renders the founder trust report from an agent run: per-company provenance, what
was checked, what was rejected and why, ending with the headline number.

## The bar, the Dirty Thirty

Thirty frozen records with known answers, ten clean and twenty each planted with
one break. The guard is graded on two numbers, not one. An agent that rejects
everything gets perfect recall and fails on precision, so it fails.

| group        | count | verdict          |
|--------------|-------|------------------|
| clean        | 10    | accept           |
| stale        | 5     | review or reject |
| unsupported  | 5     | review or reject |
| conflicting  | 5     | review           |
| drift        | 5     | reject           |

Pass bar: bad-record recall at or above 85 percent, clean-record precision at or
above 80 percent, evidence coverage 100 percent on accepted records, zero
unsupported accepted claims, a reason on every rejection.

## Environment variables

Only the first is needed, and only for live Apify pulls. The pipeline otherwise
runs offline.

- `APIFY_TOKEN` runs the live Apify Actors.
- `ANTHROPIC_API_KEY` or `OPENROUTER_API_KEY` drives the live agent: the model
  plans Actors and extracts fields from crawled text. Pick one provider, you do
  not need both. Only `python agent.py --live` needs these; the trust core stays
  deterministic either way.

All of them live in `.env`, never in the code.

## The one rule this build follows

Every field the source layer returns carries its evidence: the source URL, the
exact snippet it came from, and a `fetched_at` timestamp. Plausible is not
verified. A field with no source is a missing field, not a value. The trust core
checks that evidence; the policy filter decides fit on top of it; the two never
mix. That separation is what keeps the layer from rotting.
