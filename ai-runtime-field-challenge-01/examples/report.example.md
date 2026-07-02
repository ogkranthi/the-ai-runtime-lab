# Field report: AI Runtime Field Challenge 01 (mini report example)

This is an example of a mini report: run the reference agent, change one thing,
report the score and one failure. It is short on purpose.

## 1. Links

- Predictions file: `outputs/predictions.jsonl`
- Fork: https://github.com/example/ai-runtime-field-challenge-01

## 2. AI usage

- Provider: anthropic
- Model: claude-sonnet-5

The one change: I added a line to the triage prompt telling the model that a calm
tone never lowers a risk assessment, and to check the narrative against the
concrete harm signals before deciding risk.

## 3. Result table

| Metric | Value |
|--------|-------|
| Routing accuracy | 0.90 |
| High-risk recall | 0.90 |
| High-risk precision | 0.69 |
| Risk counts (TP / FP / FN / TN) | 9 / 4 / 1 / 26 |
| Evidence coverage | 1.00 |
| Valid evidence rate | 0.93 |

## 4. What I changed and what happened

Adding the harm-signal check raised high-risk recall (fewer missed severe cases)
and lowered precision (more tone-driven false positives). For this customer,
recall is the primary metric, so the trade was worth it. I would tighten the
false positives next.

## 5. One failure

A complaint about a delayed transfer that used strong language ("this is
unacceptable") got flagged as high risk. The transfer had already completed. The
harm-signal check helped on missed severe cases but made the agent more eager to
flag on tone, which is the opposite failure.
