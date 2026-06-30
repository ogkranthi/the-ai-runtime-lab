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

## Run it end to end (VS Code terminal)

The data plane runs with nothing but your keys. No agent, no scaffolding. Clone
it, add an Apify token, and `source.py` pulls public signals with evidence
attached to every field.

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

### 3. Add your token

    cp .env.example .env

Open `.env` in VS Code and paste your `APIFY_TOKEN`. Get one at
https://console.apify.com/account/integrations. The token stays in `.env` and
never goes in the code.

### 4. Confirm it runs

    python smoke.py

Expected output: `apify ok: SUCCEEDED`. If you do not see that, fix it now, not
at minute five of the build.

### 5. Run the source layer

    python source.py

This pulls the public signals the rubric scores for one company and prints a
record where every field carries its evidence: the source URL, the exact snippet
it came from, and a `fetched_at` timestamp.

## Environment variables

Two variables, and only the first is needed to run the data plane.

- `APIFY_TOKEN` runs the source layer. Required.
- `ANTHROPIC_API_KEY` is for the model steps you add at the workshop. Not needed
  to run the data plane.

Both live in `.env`, never in the code.

## What you build at the workshop

This folder is the source layer. At the workshop you build the rest, file by
file, run from this same VS Code terminal:

1. `rubric.md`   write down what "qualified" means before you build, so the
   target cannot drift to match whatever the agent produces.
2. `source.py`   already here: pull the signals the rubric scores and attach
   evidence to every field.
3. `trust.py`    the artifact: one source-agnostic function that decides whether
   a single claim is true and supported right now, and catches the four breaks
   (stale, unsupported, conflicting, extraction-drift).
4. `eval.py`     grade the trust core against the Dirty Thirty trap set on two
   numbers: bad-record recall and clean-record precision.
5. `policy.py`   the thin fit filter, applied only to claims the trust core
   already accepted. It decides fit, never truth.
6. Founder report and teardown: turn the live run into a qualified list with
   provenance in plain sight and one headline number, how many leads are safe to
   act on and on what basis.

## The one rule this folder follows

Every field the source layer returns carries its evidence: the source URL, the
exact snippet it came from, and a `fetched_at` timestamp. Plausible is not
verified. A field with no source is a missing field, not a value. That evidence
is exactly what the trust core checks next.
