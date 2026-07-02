# Data terms and provenance

## Source

This dataset is derived from the CFPB Consumer Complaint Database, a public
database published by the United States Consumer Financial Protection Bureau.

Source reference: https://www.consumerfinance.gov/data-research/consumer-complaints/

Snapshot date: see `data/prep/snapshot_manifest.json` for the export date and the
row counts at each filtering step.

## How the narratives are published

Complaint narratives are consumer-submitted. The CFPB publishes a narrative only
when the consumer opts in to publication, and only after the CFPB takes steps to
remove personal information. Narratives in this snapshot may contain XXXX
redaction markers applied by the CFPB where information was removed.

This dataset is not public domain and does not carry zero legal surface. It is a
derived, filtered snapshot of consumer-submitted text published by a federal
agency under its own publication rules. Treat it accordingly.

## Permitted use

This snapshot is provided for educational, research, and challenge-participation
use.

- Do not attempt to re-identify any consumer.
- Do not augment this dataset with restricted, login-gated, paywalled, or
  platform-prohibited data in public forks.
- Keep the provenance note and the source reference when you redistribute a fork.

## Code license

The code in this repository is MIT licensed. See `LICENSE`. The license covers
the code, not the underlying complaint narratives, which remain subject to the
CFPB publication terms linked above.
