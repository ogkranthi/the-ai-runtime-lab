# AI Runtime Field Challenge 01: Financial Complaint Triage

Build an AI agent that routes consumer finance complaints and flags regulatory
risk from messy public complaint narratives.

One-line promise: build a public FDE-style AI agent case study in one afternoon.

## The scenario

A regional bank gets hundreds of consumer complaints a week and routes them
inconsistently, so high-risk complaints sometimes get treated like routine
service tickets. You build an AI triage agent that reads a frozen snapshot of
real complaint narratives, routes each one to the right internal team, flags the
ones that carry regulatory or customer-harm risk, and cites the exact narrative
text behind every decision. This is a fixed-list triage of a frozen snapshot, not
live monitoring and not discovery.

## The labels are public by design

This is not a leaderboard and not a hidden benchmark. The 40 scored labels ship
in the repo. The point is evaluation discipline, evidence grounding, failure
analysis, and tradeoff thinking under a customer-shaped constraint. You are
building proof that you can reason about a production AI system, not chasing a
secret number.

## Who this is for

- AI engineers building portfolio proof of work.
- FDE and solutions engineering candidates.
- Builders learning production AI evaluation.

## What you will build

Read cached complaint narratives, route each complaint, flag risk, cite evidence,
run the deterministic evaluator, and write a field report.

## AI is required

AI must do the core reasoning: classification, risk flagging, and evidence
selection. Deterministic code is welcome for orchestration, schema validation,
quote checking, scoring, and reporting. Rules-only or manual-only submissions run
fine, but they are not eligible to be featured.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY=your_key_here

python agent/run_agent.py --input data/complaints.jsonl --output outputs/predictions.jsonl --limit 10
python run_eval.py --predictions outputs/predictions.jsonl
cp REPORT_TEMPLATE.md REPORT.md
```

The repo ships with a placeholder dataset (10 synthetic complaints) so it runs
end to end immediately. See `data/README.md` to build the real 200-complaint
snapshot from the CFPB export.

## Cost note

A full 200-complaint run is cheap. Assuming about 2,300 input tokens and about
250 output tokens per complaint (the prompt carries the brief and rubric each
call) and Anthropic Sonnet-class pricing of roughly 3 dollars per million input
tokens and 15 dollars per million output tokens, a full run lands around 2 to 4
dollars. Prices change, so confirm current rates for your model before you run.
Use `--limit` while you iterate to keep spend near zero.

## Determinism note

The evaluator is deterministic: no LLM calls, no network. It verifies committed
predictions against the labels. LLM generation is not perfectly deterministic
even at temperature 0, so regenerating predictions may shift a few decisions.
Verification means rerunning the evaluator against your committed predictions
file, not regenerating predictions.

## What you submit

A GitHub issue linking to your `REPORT.md` and your committed
`outputs/predictions.jsonl` in your fork. Anyone can rerun the evaluator against
your predictions.

## Two submission levels

- Mini report (30 to 60 minutes): run the reference agent, change one thing,
  report the score plus one failure.
- Full field report (2 to 4 hours): your own approach, full template.

## Rules

- Use any stack and any model provider.
- Do not modify the golden labels or `eval_ids.txt`.
- Public labels are allowed; this is not a hidden benchmark.
- Commit your predictions file. Submissions without it are incomplete.
- Submit a report, not just code.
- Honest failure analysis matters more than score.

A completed report means: `REPORT.md` filled in, `predictions.jsonl` committed,
and the evaluator rerunnable against it.

Challenge 02 ships after 5 completed reports on Challenge 01.
