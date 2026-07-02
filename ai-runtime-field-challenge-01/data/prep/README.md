# Dataset prep

`prepare_dataset.py` builds the frozen participant snapshot from a raw CFPB
export. It runs once. Participants do not run it; they use the committed
`data/complaints.jsonl`.

## Get the CFPB export

Download a CSV export from the CFPB Consumer Complaint Database:

https://www.consumerfinance.gov/data-research/consumer-complaints/

Use the "Download" option and export as CSV with consumer complaint narratives
included. The full export is large. You can filter by date range on the CFPB
site before downloading to keep it manageable.

## Run the prep

```bash
python data/prep/prepare_dataset.py --input cfpb_export.csv \
    --output data/complaints.jsonl --n 200 --seed 7
```

What it does:

1. Keeps only complaints that have a consumer narrative (opt-in narratives).
2. Excludes products whose name contains "credit reporting" or "credit repair",
   which otherwise dominate the database and do not fit a bank routing scenario.
3. Keeps bank-relevant products (deposits, cards, mortgage, loans, payments and
   money transfer, debt collection) and takes a stratified sample so no single
   product group exceeds 30 percent.
4. Strips every label-leaking CFPB field. The output keeps only complaint id,
   date received, state, and the narrative text.
5. Preserves the raw narrative, including XXXX redaction markers, typos, and
   all-caps passages.
6. Writes `snapshot_manifest.json` with the export date, filter criteria, and
   row counts at each step, so the snapshot is auditable.

## Placeholder note

The repo currently ships a placeholder `data/complaints.jsonl` (10 synthetic
complaints) so the agent and evaluator run end to end without the real export.
`snapshot_manifest.json` has `"placeholder": true`. Run the prep against a real
CFPB export to produce the 200-complaint snapshot, then hand-label 40 records
(see `golden/README.md`) before publishing.
