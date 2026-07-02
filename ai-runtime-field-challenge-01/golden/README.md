# Golden labels

`labels.jsonl` holds the scored labels. `eval_ids.txt` lists the complaint ids
the evaluator scores. Everything here is public by design.

This is not a hidden benchmark. The labels are visible so you can study them,
argue with them, and do honest failure analysis. The goal is evaluation
discipline, evidence grounding, and tradeoff thinking under a customer-shaped
constraint, not a leaderboard number.

The labels were assigned by a single labeler against the frozen rubric. You can
raise disagreements as GitHub issues, but labels will not change mid-challenge.

## Placeholder status

The committed labels cover the 10 placeholder complaints in
`data/complaints.jsonl`, so the repo runs end to end today. When you build the
real 200-complaint snapshot (see `data/prep/README.md`), replace these with 40
hand labels following the spec below.

## Label spec for the real dataset

- 40 labeled complaints, listed in `eval_ids.txt`.
- Routing distribution: at least 5 complaints per routing team (`other` may have
  2 to 3).
- Risk distribution: 10 to 14 complaints with `risk_flag: true`.
- Seed edge cases on purpose: angry-but-routine, short-but-severe, multi-issue
  where the primary subject requires judgment, vague narratives, and heavily
  redacted narratives.
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
