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

import present
from models import Claim, Evidence
from trust import judge

HERE = os.path.dirname(os.path.abspath(__file__))
DIRTY_THIRTY = os.path.join(HERE, "fixtures", "dirty_thirty.json")

RECALL_BAR = 0.85
PRECISION_BAR = 0.80

VCOLOR = {"accept": present.GREEN, "review": present.YELLOW, "reject": present.RED}


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

    zero_unsupported = not unsupported_accepted
    all_have_reason = not missing_reason

    def ok_cell(ok: bool):
        return ("PASS", present.GREEN) if ok else ("FAIL", present.RED)

    print("\n" + present.rule("DIRTY THIRTY  ·  trust core eval"))
    print()
    _show_records(rows)
    print()

    score_rows = [
        ["bad-record recall", f"{recall:.0%}", ">= 85%", ok_cell(recall >= RECALL_BAR)],
        ["clean-record precision", f"{precision:.0%}", ">= 80%", ok_cell(precision >= PRECISION_BAR)],
        ["evidence coverage", f"{coverage:.0%}", "100%", ok_cell(coverage >= 1.0)],
        ["unsupported accepted", str(len(unsupported_accepted)), "0", ok_cell(zero_unsupported)],
        ["reason on every reject", "all" if all_have_reason else "missing", "all", ok_cell(all_have_reason)],
    ]
    print(present.table(["metric", "value", "bar", "result"], score_rows, caps=[24, 8, 8, 6]))
    print()

    passed = (
        recall >= RECALL_BAR
        and precision >= PRECISION_BAR
        and coverage >= 1.0
        and zero_unsupported
        and all_have_reason
    )
    headline = (
        f"{'PASS' if passed else 'FAIL'}  ·  caught {len(caught)}/{len(bad)} bad  "
        f"·  kept {len(clean_accepted)}/{len(accepted)} clean"
    )
    print(present.banner(headline, present.GREEN if passed else present.RED))
    print()
    return passed


def _show_records(rows: List[tuple]) -> None:
    table_rows = []
    for rec, v in rows:
        table_rows.append([
            rec["id"], rec["group"], rec["expect"],
            (v.decision, VCOLOR.get(v.decision, "")), v.reason,
        ])
    print(present.table(
        ["id", "group", "expect", "verdict", "reason"], table_rows,
        caps=[16, 12, 8, 8, 58],
    ))


if __name__ == "__main__":
    ok = run()
    raise SystemExit(0 if ok else 1)
