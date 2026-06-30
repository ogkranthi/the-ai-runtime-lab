# web-agents-trust, Field Lab 01 module 2

Module 2 of The AI Runtime Field Lab 01, "A Reliability Layer for Web-Grounded
Agents." This is the part the lab is really about.

Module 1 (in `../web-agents-apify`) is the sourcing agent. It produces a prospect
list that looks done: every field sourced, every field cited. Module 2 decides
which of that list is actually safe to act on.

It is the reliability layer: a source-agnostic trust core, a thin fit filter on
top, and an eval that proves the trust core works against a planted trap set.
Everything here is pure Python, deterministic, and runs with no keys.

Lab page: https://lab.theairuntime.com/01/

## The reveal

Module 1 said four candidates looked done. Run module 2 and two of them fall:

    python pipeline.py

```
company      verified   status   why
Forge Labs   5/5        SAFE     every field verified and fits
Quantal      5/5        SAFE     every field verified and fits
Mega Corp    5/5        HELD     headcount 5000 outside 50 to 300
Helios CRM   3/5        HELD     no accepted headcount

2 of 4 safe to act on
```

Mega Corp is real but too big. Helios has two sources that disagree on its
headcount and a reason to reach out that no source actually backs. The trust core
catches both, and the list shrinks from "looks done" to "safe to act on."

## What is here

- `ARCHITECTURE.md`   the full technical walkthrough and learning guide
- `trust.py`     the trust core: judge one claim and its evidence, catch the four breaks
- `policy.py`    the fit filter, applied only to what the trust core accepted
- `pipeline.py`  wire trust and policy over the prospect list, then show the reveal
- `report.py`    the founder-facing trust report (Markdown)
- `eval.py`      grade the trust core against the Dirty Thirty trap set
- `models.py`    the data model: Evidence, Claim, Verdict
- `present.py`   terminal tables and banners, no dependencies
- `fixtures/prospects.json`     the module 1 output this layer runs over
- `fixtures/dirty_thirty.json`  thirty frozen claims, ten clean and twenty planted

## The four ways web data breaks

The trust core catches each one. See `trust.py` and `ARCHITECTURE.md` for how.

| break | what it means |
|-------|---------------|
| stale | true once, not anymore, and the source is cached |
| unsupported | the evidence is missing, walled, or does not back the claim |
| conflicting | two sources disagree on a field that matters |
| extraction-drift | the wrong field, or the wrong company, was grabbed |

## Run it

No setup beyond Python. No keys, no install.

    python pipeline.py     # the reveal: which candidates are safe to act on
    python eval.py         # grade the trust core against the Dirty Thirty
    python report.py       # the founder trust report, as Markdown

`python report.py > report.md` saves the founder artifact.

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
unsupported accepted claims, a reason on every rejection. Current result: PASS,
20 of 20 bad caught, 10 of 10 clean kept.

## The two layers, and why they stay apart

The trust core decides whether a claim is true and supported right now. The policy
filter decides whether a true claim fits the founder's profile. The core is
source-agnostic and reusable for any web-grounded agent. The fit logic sits on
top so it never contaminates the core. Mixing them is how the layer rots.
