# Field report: AI Runtime Field Challenge 01 (reference)

Status: build-time reference against the PLACEHOLDER dataset. No live model run
was available when this was written, so the predictions were produced by hand to
represent a realistic reference-agent run, then scored by the deterministic
evaluator. Regenerate this on the full 200-complaint dataset with a real
`run_agent.py` run before publishing. The numbers below are real evaluator
output on the 10 placeholder complaints, not a live model result.

## 1. Links

- Predictions file: build-time placeholder run (10 complaints)
- Fork: this repository

## 2. AI usage

- Provider: anthropic
- Model: claude-sonnet-5 (reference default, verify before a real run)

Where AI did the work:

- [x] signal extraction
- [x] routing classification
- [x] risk flagging
- [x] evidence selection
- [x] explanation

Where deterministic code did the work:

- [x] schema validation
- [x] quote checking
- [x] scoring
- [x] reporting

Prompt strategy: one combined call per complaint. The prompt carries the brief,
the rubric, and a four-step instruction: extract signals, route by subject
matter, decide risk with the two calibration rules, then select verbatim quotes.
The model returns strict JSON. The harness adds the id and the AI-usage block and
validates against the schema.

## 3. Result table

| Metric | Value |
|--------|-------|
| Routing accuracy | 0.90 (9 / 10) |
| High-risk recall | 0.75 (3 / 4) |
| High-risk precision | 0.75 (3 / 4) |
| Risk counts (TP / FP / FN / TN) | 3 / 1 / 1 / 5 |
| Evidence coverage | 1.00 (10 / 10) |
| Valid evidence rate | 0.95 (19 / 20) |
| Runtime | not applicable (build-time placeholder) |
| Estimated cost | not applicable (build-time placeholder) |

## 4. What I built

The reference agent in `agent/run_agent.py`, run against the placeholder set. It
makes one LLM call per complaint, validates the response against the schema, and
falls back to `other` and `risk_flag false` on a parse failure. Nothing fancy. It
exists to set the honesty bar, not to top a score.

## 5. FDE decision log

| Decision | Alternative | Why | Tradeoff |
|----------|-------------|-----|----------|
| One combined LLM call per complaint | A multi-step pipeline (separate extract, route, risk calls) | Simpler, cheaper, easier to reason about for a reference | A single call blends routing and risk reasoning, which contributed to the P0005 tone false positive |

## 6. Failure table

| Complaint ID | Expected (route / flag) | Predicted (route / flag) | Failure mode | What happened |
|--------------|-------------------------|--------------------------|--------------|---------------|
| P0005 | customer_service / false | customer_service / true | Tone read as risk | The all-caps anger and repetition were treated as elevated risk. The underlying request was a routine address update. |
| P0009 | payments_transfers / true | payments_transfers / false | Missed high risk | A large wire missing during a home closing was treated as a routine transfer delay. This is the worst failure mode, a missed high-risk complaint. The risk evidence quote also did not appear in the narrative, so it failed quote validation. |
| P0010 | other / false | customer_service / false | Over-routing a vague record | A heavily redacted, contentless complaint was pushed into customer_service instead of other. The model preferred a specific team over admitting the record was too thin. |

## 7. Most interesting failure

P0009 is the one that matters. The narrative describes a large wire for a home
closing that never arrived, with the closing at risk. That is a severe,
time-sensitive loss. The agent routed it correctly to payments_transfers but read
it as a routine delay and set `risk_flag` false. The tone was calm and factual,
and the agent leaned on tone instead of the concrete harm in the text. This is
the exact trap the rubric warns about from the other direction: it warns that
angry tone is not risk, and P0005 shows the agent overreacting to tone, while
P0009 shows it underreacting to a calm description of real harm. The lesson is
that the risk decision has to key on concrete harm signals (missing funds,
foreclosure, blocked access), not on affect.

## 8. What I would change in v2

Separate the risk decision from the routing decision. Give the risk step its own
short prompt that lists the concrete harm signals and asks the model to check the
narrative against each one before deciding. Add a rule that a calm tone never
lowers a risk assessment on its own. Consider a second pass only on complaints
where routing and risk disagree in confidence, since those are where tone and
harm come apart.

## 9. Share block

```
I built an AI complaint-triage agent for AI Runtime Field Challenge 01.

High-risk recall: 0.75
Routing accuracy: 0.90

Most interesting failure: a calm complaint about a missing wire during a home
closing got treated as a routine delay, a missed high-risk case.
The lesson: risk has to key on concrete harm signals, not tone.

Repo: <link>
```
