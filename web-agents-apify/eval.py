"""Eval harness for Field Lab 01, module 2.

Grades the trust core against the Dirty Thirty: thirty frozen claims, ten clean
and twenty each planted with one break. The guard is scored on two numbers, not
one. An agent that rejects everything gets perfect recall and fails on precision,
so it fails. Catching the bad while keeping the good is the whole skill.

Pass bar:
  bad-record recall      at or above 85 percent
  clean-record precision at or above 80 percent
  evidence coverage      100 percent on accepted records
  unsupported accepted   zero
  a reason on every rejection
"""
from __future__ import annotations

import json
import os
from typing import List

from models import Claim, Evidence
from trust import judge

HERE = os.path.dirname(os.path.abspath(__file__))
DIRTY_THIRTY = os.path.join(HERE, "fixtures", "dirty_thirty.json")

RECALL_BAR = 0.85
PRECISION_BAR = 0.80


def _load(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _claim(record: dict) -> Claim:
    c = record["claim"]
    evidence = [Evidence(**e) for e in record["evidence"]]
    return Claim(
        field=c["field"],
        value=c["value"],
        company=c["company"],
        domain=c.get("domain", ""),
        evidence=evidence,
    )


def run(path: str = DIRTY_THIRTY) -> bool:
    data = _load(path)
    as_of = data["as_of"]
    records = data["records"]

    rows = []
    for rec in records:
        verdict = judge(_claim(rec), as_of=as_of)
        rows.append((rec, verdict))

    # An accepted record is "kept". Anything else (reject or review) is "caught".
    accepted = [(r, v) for r, v in rows if v.decision == "accept"]
    bad = [(r, v) for r, v in rows if r["group"] != "clean"]
    caught = [(r, v) for r, v in bad if v.decision != "accept"]
    clean_accepted = [(r, v) for r, v in accepted if r["group"] == "clean"]

    recall = len(caught) / len(bad) if bad else 1.0
    precision = len(clean_accepted) / len(accepted) if accepted else 0.0

    # Coverage and unsupported-accepted both read the trace the trust core emitted.
    with_evidence = [(r, v) for r, v in accepted if r["evidence"]]
    coverage = len(with_evidence) / len(accepted) if accepted else 1.0
    unsupported_accepted = [
        (r, v) for r, v in accepted if v.break_kind == "unsupported"
    ]
    rejections = [(r, v) for r, v in rows if v.decision != "accept"]
    missing_reason = [(r, v) for r, v in rejections if not v.reason.strip()]

    _print_records(rows)
    print()

    bars = [
        ("bad-record recall", recall, recall >= RECALL_BAR, f">= {RECALL_BAR:.0%}"),
        ("clean-record precision", precision, precision >= PRECISION_BAR, f">= {PRECISION_BAR:.0%}"),
        ("evidence coverage", coverage, coverage >= 1.0, "100%"),
    ]
    print("metric                    value     bar       result")
    print("-" * 54)
    for name, value, ok, bar in bars:
        print(f"{name:<25} {value:>6.0%}   {bar:<8}  {'PASS' if ok else 'FAIL'}")
    zero_unsupported = not unsupported_accepted
    all_have_reason = not missing_reason
    print(f"{'unsupported accepted':<25} {len(unsupported_accepted):>6}   {'0':<8}  {'PASS' if zero_unsupported else 'FAIL'}")
    print(f"{'reason on every reject':<25} {'-':>6}   {'all':<8}  {'PASS' if all_have_reason else 'FAIL'}")

    passed = (
        recall >= RECALL_BAR
        and precision >= PRECISION_BAR
        and coverage >= 1.0
        and zero_unsupported
        and all_have_reason
    )
    print()
    print(f"caught {len(caught)}/{len(bad)} bad, kept {len(clean_accepted)}/{len(accepted)} accepted clean")
    print("RESULT:", "PASS" if passed else "FAIL")
    return passed


def _print_records(rows: List[tuple]) -> None:
    print(f"{'id':<16} {'group':<12} {'expect':<8} {'verdict':<8} reason")
    print("-" * 92)
    for rec, v in rows:
        flag = "" if v.decision == rec["expect"] else "  <-- off"
        print(f"{rec['id']:<16} {rec['group']:<12} {rec['expect']:<8} {v.decision:<8} {v.reason}{flag}")


if __name__ == "__main__":
    ok = run()
    raise SystemExit(0 if ok else 1)
