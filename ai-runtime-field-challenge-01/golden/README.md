# Golden labels

`labels.jsonl` holds the scored labels. `eval_ids.txt` lists the complaint ids
the evaluator scores. Everything here is public by design.

This is not a hidden benchmark. The labels are visible so you can study them,
argue with them, and do honest failure analysis. The goal is evaluation
discipline, evidence grounding, and tradeoff thinking under a customer-shaped
constraint, not a leaderboard number.

The labels were assigned against the frozen rubric and reviewed by a single
owner. You can raise disagreements as GitHub issues, but labels will not change
mid-challenge.

## Current labels

The committed labels cover 40 complaints from the real 200-complaint CFPB
snapshot, drafted against the frozen rubric and reviewed by the owner. The risk
calls use the recall-first posture in `rubric.md`: when the record leaves a
substantive regulatory or harm allegation unresolved, the complaint is flagged,
and only already-resolved or clearly trivial complaints are left unflagged.

The distribution follows the spec below: at least 5 per team (`other` has 3), and
25 complaints with `risk_flag: true`.

## Label spec

- 40 labeled complaints, listed in `eval_ids.txt`.
- Routing distribution: at least 5 complaints per routing team (`other` may have
  2 to 3).
- Risk distribution: with the recall-first posture, expect roughly 22 to 28
  complaints with `risk_flag: true`.
- Seed edge cases on purpose: angry-but-routine, short-but-severe, multi-issue
  where the primary subject requires judgment, regulatory-sounding but
  already-resolved complaints, vague narratives, and heavily redacted narratives.
- Every label includes a `label_reason` and `evidence_sources` referencing the
  narrative `source_id`. The reason must be supportable from the narrative text
  alone.

## Label row shape

```json
{
  "complaint_id": "7654321",
  "routing_team": "fraud_disputes",
  "risk_flag": true,
  "label_reason": "Unauthorized transaction with repeated unresolved dispute attempts described in the narrative.",
  "evidence_sources": ["7654321-narrative"]
}
```

## Labeling guide

1. Read the whole narrative before deciding anything.
2. Route by primary subject matter, not by how upset the consumer sounds.
3. Decide risk from concrete harm signals in the text, not from tone. Reread the
   two calibration rules in `rubric.md` before every risk decision.
4. Write the `label_reason` as if you will defend it in a GitHub issue. If you
   cannot point to text that supports it, change the label.
5. When two routes seem plausible, pick the one the complaint is mostly about and
   note the alternative in the reason.
