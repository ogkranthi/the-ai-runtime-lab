"""One-time prep: build data/complaints.jsonl from a CFPB export.

This script turns a raw CFPB Consumer Complaint Database export into the frozen,
participant-visible snapshot. It filters to bank-relevant complaints that have a
consumer narrative, takes a stratified sample, strips every label-leaking field,
and writes an auditable manifest.

It uses only the Python standard library. See data/prep/README.md for the export
URL and the exact command.

Usage:
    python data/prep/prepare_dataset.py --input cfpb_export.csv \
        --output data/complaints.jsonl --n 200 --seed 7
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
from datetime import date

# CFPB product values that we exclude. The raw database is dominated by
# credit-reporting complaints against the credit bureaus, which do not fit a
# regional-bank routing scenario.
EXCLUDE_IF_CONTAINS = ["credit reporting", "credit repair"]

# Map a raw CFPB Product string to a coarse group, used only for stratification
# so that no single product dominates the sample. Matching is case-insensitive
# substring matching, first hit wins.
PRODUCT_GROUPS = [
    ("checking or savings", "deposits"),
    ("bank account", "deposits"),
    ("credit card", "cards"),
    ("prepaid card", "cards"),
    ("mortgage", "mortgage"),
    ("student loan", "loans"),
    ("vehicle loan", "loans"),
    ("payday loan", "loans"),
    ("personal loan", "loans"),
    ("consumer loan", "loans"),
    ("money transfer", "payments"),
    ("money service", "payments"),
    ("virtual currency", "payments"),
    ("debt collection", "debt_collection"),
]

# Fields we keep. Everything else is dropped, especially the label-leaking
# CFPB fields (product, sub-product, issue, sub-issue, company response,
# timely response, consumer disputed).
NARRATIVE_COL = "Consumer complaint narrative"
ID_COL = "Complaint ID"
DATE_COL = "Date received"
STATE_COL = "State"
PRODUCT_COL = "Product"

MIN_CHARS = 300
MAX_CHARS = 3000
MAX_GROUP_SHARE = 0.30


def group_for(product: str):
    p = (product or "").lower()
    for needle, group in PRODUCT_GROUPS:
        if needle in p:
            return group
    return None


def excluded(product: str) -> bool:
    p = (product or "").lower()
    return any(needle in p for needle in EXCLUDE_IF_CONTAINS)


def read_rows(path: str):
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            yield row


def prepare(input_path: str, output_path: str, n: int, seed: int):
    rng = random.Random(seed)
    counts = {"raw": 0, "with_narrative": 0, "bank_relevant": 0, "sampled": 0}

    # Stage 1 and 2: filter to bank-relevant complaints that have a narrative.
    pool = []
    for row in read_rows(input_path):
        counts["raw"] += 1
        narrative = (row.get(NARRATIVE_COL) or "").strip()
        if not narrative:
            continue
        counts["with_narrative"] += 1
        product = row.get(PRODUCT_COL) or ""
        if excluded(product):
            continue
        group = group_for(product)
        if group is None:
            continue
        counts["bank_relevant"] += 1
        pool.append({
            "complaint_id": (row.get(ID_COL) or "").strip(),
            # CFPB exports may give a full ISO timestamp; keep the date only.
            "date_received": (row.get(DATE_COL) or "").strip().split("T")[0][:10],
            "state": (row.get(STATE_COL) or "").strip(),
            "narrative": narrative,
            "_group": group,
            "_len": len(narrative),
        })

    # Stage 3: stratified sample. Prefer narratives in the readable band, but keep
    # a spread by allowing some outside it. Cap any single group at 30 percent.
    by_group = {}
    for r in pool:
        by_group.setdefault(r["_group"], []).append(r)

    per_group_cap = max(1, int(n * MAX_GROUP_SHARE))
    for g in by_group:
        rng.shuffle(by_group[g])
        # Bring in-band narratives to the front, but do not drop the rest.
        by_group[g].sort(key=lambda r: 0 if MIN_CHARS <= r["_len"] <= MAX_CHARS else 1)

    # Round-robin across groups so the sample stays balanced.
    sample = []
    groups = sorted(by_group.keys())
    idx = {g: 0 for g in groups}
    taken = {g: 0 for g in groups}
    while len(sample) < n and any(idx[g] < len(by_group[g]) for g in groups):
        for g in groups:
            if len(sample) >= n:
                break
            if taken[g] >= per_group_cap:
                continue
            if idx[g] < len(by_group[g]):
                sample.append(by_group[g][idx[g]])
                idx[g] += 1
                taken[g] += 1
    counts["sampled"] = len(sample)

    # Stage 4 and 5: strip label-leaking fields, preserve the raw narrative text.
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as out:
        for r in sample:
            record = {
                "complaint_id": r["complaint_id"],
                "date_received": r["date_received"],
                "state": r["state"],
                "sources": [
                    {
                        "source_id": f"{r['complaint_id']}-narrative",
                        "source_type": "consumer_narrative",
                        "text": r["narrative"],
                    }
                ],
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Stage 6: write an auditable manifest.
    manifest = {
        "placeholder": False,
        "cfpb_export_input": os.path.basename(input_path),
        "prepared_on": date.today().isoformat(),
        "seed": seed,
        "target_n": n,
        "min_chars_preferred": MIN_CHARS,
        "max_chars_preferred": MAX_CHARS,
        "max_group_share": MAX_GROUP_SHARE,
        "excluded_if_product_contains": EXCLUDE_IF_CONTAINS,
        "row_counts": counts,
        "group_counts": {g: taken[g] for g in groups},
    }
    manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshot_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)

    print(f"Wrote {counts['sampled']} complaints to {output_path}")
    print(f"Wrote manifest to {manifest_path}")
    print(json.dumps(counts, indent=2))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build data/complaints.jsonl from a CFPB export.")
    ap.add_argument("--input", required=True, help="Path to a CFPB export CSV.")
    ap.add_argument("--output", default="data/complaints.jsonl")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args(argv)

    if not os.path.exists(args.input):
        print(f"Input not found: {args.input}", file=sys.stderr)
        print("See data/prep/README.md for the CFPB export URL and download command.", file=sys.stderr)
        return 2

    prepare(args.input, args.output, args.n, args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
