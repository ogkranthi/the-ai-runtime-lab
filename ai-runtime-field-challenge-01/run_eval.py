"""Deterministic evaluator for AI Runtime Field Challenge 01.

Scores a predictions file against the public golden labels. No LLM calls, no
network. Rerunning it verifies committed predictions against the labels; it does
not regenerate predictions.

Usage:
    python run_eval.py --predictions outputs/predictions.jsonl

Quote normalization (used to validate evidence): lowercase, collapse whitespace
runs to single spaces, and strip punctuation. The XXXX redaction marker is
alphanumeric, so it survives normalization unchanged. Both the quote and the
source text are normalized the same way before the substring check.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LABELS_PATH = os.path.join(HERE, "golden", "labels.jsonl")
EVAL_IDS_PATH = os.path.join(HERE, "golden", "eval_ids.txt")
COMPLAINTS_PATH = os.path.join(HERE, "data", "complaints.jsonl")
SCHEMA_PATH = os.path.join(HERE, "agent", "schemas", "prediction.schema.json")

ROUTING_TEAMS = [
    "account_access", "payments_transfers", "fraud_disputes",
    "credit_lending", "customer_service", "other",
]


def normalize(text: str) -> str:
    lowered = (text or "").lower()
    kept = [c if (c.isalnum() or c.isspace()) else " " for c in lowered]
    return " ".join("".join(kept).split())


def load_jsonl(path: str):
    rows = []
    with open(path, "r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                rows.append((line_no, json.loads(raw)))
            except json.JSONDecodeError as exc:
                fail(f"{os.path.basename(path)} line {line_no}: invalid JSON ({exc.msg})")
    return rows


def fail(message: str):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_row(record: dict, schema: dict, line_no: int):
    try:
        import jsonschema
        try:
            jsonschema.validate(record, schema)
            return
        except jsonschema.ValidationError as exc:
            fail(f"predictions line {line_no}: schema-invalid ({exc.message})")
    except ImportError:
        _manual_validate(record, line_no)


def _manual_validate(record: dict, line_no: int):
    for key in ["complaint_id", "routing_team", "risk_flag", "confidence", "ai_usage", "reason", "evidence"]:
        if key not in record:
            fail(f"predictions line {line_no}: missing field '{key}'")
    if record["routing_team"] not in ROUTING_TEAMS:
        fail(f"predictions line {line_no}: routing_team not in enum '{record['routing_team']}'")
    if not isinstance(record["risk_flag"], bool):
        fail(f"predictions line {line_no}: risk_flag must be boolean")
    if not isinstance(record.get("evidence"), list) or not record["evidence"]:
        fail(f"predictions line {line_no}: evidence must be a non-empty list")
    for item in record["evidence"]:
        if not all(k in item for k in ("criterion", "source_id", "quote")):
            fail(f"predictions line {line_no}: evidence item missing a required key")


def load_source_index():
    """Map complaint_id -> {source_id: normalized_text}."""
    index = {}
    for _, rec in load_jsonl(COMPLAINTS_PATH):
        by_source = {s["source_id"]: normalize(s["text"]) for s in rec.get("sources", [])}
        index[rec["complaint_id"]] = by_source
    return index


def count_valid_evidence(prediction: dict, source_index: dict):
    """Return (total_items, valid_items) for one prediction's evidence."""
    cid = prediction["complaint_id"]
    sources = source_index.get(cid, {})
    total = valid = 0
    for item in prediction.get("evidence", []):
        total += 1
        sid = item.get("source_id", "")
        quote = normalize(item.get("quote", ""))
        if sid in sources and quote and quote in sources[sid]:
            valid += 1
    return total, valid


def main(argv=None):
    ap = argparse.ArgumentParser(description="Deterministic evaluator for Challenge 01.")
    ap.add_argument("--predictions", required=True)
    args = ap.parse_args(argv)

    if not os.path.exists(args.predictions):
        fail(f"predictions file not found: {args.predictions}")

    schema = load_schema()
    source_index = load_source_index()

    labels = {rec["complaint_id"]: rec for _, rec in load_jsonl(LABELS_PATH)}
    with open(EVAL_IDS_PATH, "r", encoding="utf-8") as fh:
        eval_ids = [line.strip() for line in fh if line.strip()]

    predictions = {}
    for line_no, rec in load_jsonl(args.predictions):
        if "complaint_id" not in rec:
            fail(f"predictions line {line_no}: missing complaint_id")
        validate_row(rec, schema, line_no)
        predictions[rec["complaint_id"]] = rec

    scored = len(eval_ids)
    found = sum(1 for cid in eval_ids if cid in predictions)
    missing = scored - found

    routing_correct = 0
    per_team = {t: [0, 0] for t in ROUTING_TEAMS}  # team -> [correct, total]
    tp = fp = fn = tn = 0
    rows_with_evidence = 0
    total_items = valid_items = 0
    flagged_no_valid = 0

    for cid in eval_ids:
        gold = labels[cid]
        pred = predictions.get(cid)
        pred_route = pred["routing_team"] if pred else "other"
        pred_risk = bool(pred["risk_flag"]) if pred else False

        per_team[gold["routing_team"]][1] += 1
        if pred_route == gold["routing_team"]:
            routing_correct += 1
            per_team[gold["routing_team"]][0] += 1

        gold_risk = bool(gold["risk_flag"])
        if pred_risk and gold_risk:
            tp += 1
        elif pred_risk and not gold_risk:
            fp += 1
        elif (not pred_risk) and gold_risk:
            fn += 1
        else:
            tn += 1

        items = valid = 0
        if pred:
            if pred.get("evidence"):
                rows_with_evidence += 1
            items, valid = count_valid_evidence(pred, source_index)
        total_items += items
        valid_items += valid
        if pred_risk and valid == 0:
            flagged_no_valid += 1

    routing_accuracy = routing_correct / scored if scored else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    coverage = rows_with_evidence / scored if scored else 0.0
    valid_rate = valid_items / total_items if total_items else 0.0

    print("AI Runtime Field Challenge 01 Evaluation")
    print()
    print(f"Scored labels: {scored}")
    print(f"Predictions found: {found} ({missing} missing)")
    print()
    print("Routing")
    print(f"  Correct: {routing_correct} / {scored}")
    print(f"  Routing accuracy: {routing_accuracy:.2f}")
    print("  Per-team breakdown:")
    for t in ROUTING_TEAMS:
        c, total = per_team[t]
        if total:
            print(f"    {t}: {c}/{total}")
    print()
    print("Risk flag (positive class = risk_flag true)")
    print(f"  TP: {tp}  FP: {fp}  FN: {fn}  TN: {tn}")
    print(f"  High-risk recall: {recall:.2f}")
    print(f"  High-risk precision: {precision:.2f}")
    print()
    print("Evidence")
    print(f"  Rows with at least one evidence item: {rows_with_evidence} / {scored} (coverage {coverage:.2f})")
    print(f"  Valid evidence items: {valid_items} / {total_items} (valid evidence rate {valid_rate:.2f})")
    print(f"  Flagged rows with no valid evidence: {flagged_no_valid}")
    print()
    print("Primary metrics: high-risk recall, routing accuracy, valid evidence rate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
