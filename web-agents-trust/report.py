"""Founder-facing trust report, Field Lab 01 module 2.

Turns one reliability run into a Markdown artifact a founder can act on. For every
company it shows the provenance: what was kept with its source, and what was
dropped and why. It ends with one headline number, how many are safe to act on
and on what basis.

    python report.py            # prints Markdown to stdout
    python report.py > out.md   # save the artifact
"""
from __future__ import annotations

from typing import List

from pipeline import Review, run

FIELD_LABEL = {
    "location": "location",
    "size": "size",
    "product_type": "product",
    "eng_leader_contact": "engineering lead",
    "reason_to_reach_out": "reason to reach out",
}


def render(reviews: List[Review]) -> str:
    safe = [r for r in reviews if r.safe]
    lines: List[str] = []
    lines.append("# Founder trust report, design-partner candidates")
    lines.append("")
    lines.append(
        f"**{len(safe)} of {len(reviews)} candidates are safe to act on.** Safe means "
        "every fit field traces to a source the trust core accepted as true and "
        "supported right now, and the company clears the fit rubric. The rest are "
        "listed with the exact gap, not padded into the list."
    )
    lines.append("")

    if safe:
        lines.append("## Safe to act on")
        lines.append("")
        for r in safe:
            lines.append(f"### {r.company} ({r.domain})")
            for v in r.verdicts:
                if v.decision == "accept":
                    f = v.trace.get("field", "?")
                    src = v.trace.get("sources") or []
                    where = src[0] if src else "no source"
                    lines.append(f"- **{FIELD_LABEL.get(f, f)}**: {r.accepted.get(f)}  ")
                    lines.append(f"  source: {where}  ")
                    lines.append(f"  check: {v.reason}")
            lines.append("")

    held = [r for r in reviews if not r.safe]
    if held:
        lines.append("## Held back, with the gap named")
        lines.append("")
        for r in held:
            lines.append(f"### {r.company} ({r.domain})")
            for v in r.verdicts:
                if v.decision != "accept":
                    f = v.trace.get("field", "?")
                    lines.append(f"- dropped **{FIELD_LABEL.get(f, f)}**: {v.reason}")
            for gap in r.fit.gaps:
                lines.append(f"- fit gap: {gap}")
            lines.append("")

    lines.append("---")
    lines.append(
        f"Headline: **{len(safe)} of {len(reviews)} safe to act on**, each backed by "
        "a source the trust core accepted."
    )
    return "\n".join(lines)


if __name__ == "__main__":
    print(render(run()))
