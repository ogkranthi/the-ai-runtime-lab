# Data

`complaints.jsonl` is the frozen, participant-visible snapshot. One JSON object
per line. Make every decision only from this file.

## Record shape

```json
{
  "complaint_id": "7654321",
  "date_received": "2026-05-14",
  "state": "MA",
  "sources": [
    {
      "source_id": "7654321-narrative",
      "source_type": "consumer_narrative",
      "text": "I did not authorize this transaction... XXXX ... they still have not returned my money."
    }
  ]
}
```

The record intentionally excludes the CFPB product, sub-product, issue,
sub-issue, company response, timely response, and consumer disputed fields.
Those encode the answers. If the evidence is not in the narrative text, it does
not exist for this challenge.

## Redaction markers

`XXXX` marks content the CFPB removed before publication. Treat redacted content
as unknown. Do not guess what was behind a redaction.

## Placeholder status

The committed file is a PLACEHOLDER: 10 synthetic complaints, written by hand to
cover the routing teams and the risk edge cases so the repo runs end to end.
They are not real CFPB records. See `prep/snapshot_manifest.json`
(`"placeholder": true`).

To build the real 200-complaint snapshot, run `prep/prepare_dataset.py` against a
CFPB export. See `prep/README.md`.

## Quote normalization

The evaluator validates evidence quotes against the narrative after
normalization: lowercase, collapse whitespace runs to single spaces, strip
punctuation except the `XXXX` redaction marker. If a quote fails to validate,
check for smart quotes, trailing punctuation, or text that spans a redaction.
