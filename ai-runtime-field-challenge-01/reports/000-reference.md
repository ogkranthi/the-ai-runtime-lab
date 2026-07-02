# Field report: AI Runtime Field Challenge 01 (reference)

Status: reference against the real 200-complaint snapshot with the 40 golden
labels. The labels were drafted with model assistance and need a human review
pass before publication. No live model run was available at build time, so the
predictions scored here are a build-time stand-in that mirrors a realistic agent
run (mostly correct, with a few planted errors). Regenerate this by running
`agent/run_agent.py` with an API key and scoring the output with `run_eval.py`.
The evaluator numbers below are real output on the real 40 labels.

## 1. Links

- Predictions file: build-time stand-in over the 40 labeled complaints
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
| Routing accuracy | 0.93 (37 / 40) |
| High-risk recall | 0.86 (12 / 14) |
| High-risk precision | 0.92 (12 / 13) |
| Risk counts (TP / FP / FN / TN) | 12 / 1 / 2 / 25 |
| Evidence coverage | 1.00 (40 / 40) |
| Valid evidence rate | 0.97 (78 / 80) |
| Runtime | not applicable (build-time stand-in) |
| Estimated cost | not applicable (build-time stand-in) |

Per-team routing: account_access 6/7, payments_transfers 6/6, fraud_disputes
8/9, credit_lending 10/10, customer_service 5/5, other 2/3.

## 4. What I built

The reference agent in `agent/run_agent.py`. One LLM call per complaint, schema
validation with a retry and a schema-valid fallback. It exists to set the honesty
bar, not to top a score.

## 5. FDE decision log

| Decision | Alternative | Why | Tradeoff |
|----------|-------------|-----|----------|
| One combined LLM call per complaint | Separate calls for routing and risk | Simpler and cheaper for a reference | Blending the two decisions makes it easier for tone or product words to pull both the route and the risk the same wrong direction |
| Route by primary subject, risk separately | Route by severity | Matches the rubric tiebreak and keeps escalation in the risk flag | A severe complaint about a product still routes to that product team, which can feel counterintuitive |

## 6. Failure table

| Complaint ID | Expected (route / flag) | Predicted (route / flag) | Failure mode | What happened |
|--------------|-------------------------|--------------------------|--------------|---------------|
| 23138290 | account_access / true | customer_service / false | Route miss and missed high risk | A short complaint about a closed account with funds held three months, rent behind, and eviction with children read as a routine service runaround. Both the route and the risk were wrong. |
| 23168131 | account_access / true | account_access / false | Missed high risk | Funds withheld for about ten months across eight returned checks were treated as routine. The risk evidence quote also did not appear in the narrative, so it failed validation. |
| 23098880 | customer_service / false | customer_service / true | Tone read as risk | A frustrated accessibility complaint from a consumer with a disability was flagged as high risk. The narrative describes a service and communication gap, not financial harm or lending discrimination. |
| 23095960 | fraud_disputes / true | credit_lending / true | Route miss | An unresolved card fraud claim that also mentions account closures pulled the route toward credit_lending. The risk flag was correct. |
| 23132966 | other / false | customer_service / false | Over-routing a vague record | A mid-conversation transcript fragment was pushed into customer_service instead of other. The model preferred a specific team over admitting the record was too thin. |

## 7. Most interesting failure

23138290 is the one that matters. The narrative is short and plain: the bank
closed the account, has held the money for three months, the rent is behind, and
the consumer fears eviction with their children. The agent read the calm, short
text as a routine service complaint and got both decisions wrong, routing it to
customer_service and setting risk false. This is the calibration rule failing in
practice: a short narrative is not automatically low risk. The severity was in
the facts (funds withheld, eviction exposure), not in the tone, and the agent
keyed on tone. The paired failure is 23098880, where the agent overreacted to a
frustrated but operationally routine accessibility complaint. Together they show
the same root cause from both sides: risk keyed on affect instead of on concrete
harm.

## 8. What I would change in v2

Split the risk decision into its own step with an explicit checklist of concrete
harm signals (funds inaccessible, foreclosure or repossession, unresolved fraud,
discrimination, ignored dispute process). Add a rule that tone, whether calm or
angry, never moves the risk decision on its own. Reread short narratives once
against the harm checklist before finalizing, since the short-but-severe case is
where this agent is weakest.

## 9. Share block

```
I built an AI complaint-triage agent for AI Runtime Field Challenge 01.

High-risk recall: 0.86
Routing accuracy: 0.93

Most interesting failure: a short, calm complaint about a closed account with
funds held for three months and eviction looming was read as a routine service
issue, a missed high-risk case.
The lesson: risk has to key on concrete harm signals, not tone or length.

Repo: <link>
```
