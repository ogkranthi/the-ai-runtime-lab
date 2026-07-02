# Customer brief: Financial Complaint Triage

A regional bank receives hundreds of consumer complaints every week. The
operations team needs to route each complaint to the right internal team and
identify complaints that may carry regulatory, legal, or customer-harm risk.

Today routing is inconsistent. Some complaints go to the wrong team. Some
high-risk complaints get treated like routine service issues. Some complaints
sound severe because of tone, but the underlying issue is operationally routine.

The bank wants an AI triage agent that reads messy complaint narratives, routes
each complaint, flags risk, and cites the evidence behind every decision.

## Dataset

You work from a frozen snapshot derived from the CFPB Consumer Complaint
Database. Make every decision only from `data/complaints.jsonl`. If the evidence
is not in the cached record, it does not exist for this challenge. Narratives
contain CFPB redaction markers (XXXX). Treat redacted content as unknown.

## Task

For each complaint, predict two things: the routing team and the risk flag.
Support both with short verbatim quotes from the narrative. This is a fixed-list
triage of a frozen snapshot. There is no discovery step and no live data.

## Customer goal

Two failure modes matter.

1. A high-risk complaint is missed. This is the most serious failure, so
   high-risk recall is the primary metric.
2. A complaint is routed to the wrong team. This wastes operations time, so
   routing accuracy is the second metric.

Every routed or flagged decision must be grounded in the narrative, so valid
evidence rate is the third metric.

## What good looks like

The agent explains why. It cites exact narrative text. It separates angry tone
from actual regulatory risk. It admits uncertainty on vague complaints instead
of inventing detail.
