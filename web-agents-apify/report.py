"""Founder-facing trust report for Field Lab 01, module 2.

Turns one agent run into something a founder can act on. For every company it
shows the provenance: what was checked, what was kept with its source, and what
was rejected and why. It ends with one headline number, how many of these are
safe to act on and on what basis.

This is the prod-ready face of the pipeline. The number is honest because the
trust core earned it against the Dirty Thirty, and every line traces to a source.
"""
from __future__ import annotations

from typing import List

from agent import CompanyResult, run


def render(results: List[CompanyResult]) -> str:
    qualified = [r for r in results if r.qualified]
    lines: List[str] = []
    lines.append("# Founder trust report, design-partner candidates")
    lines.append("")
    lines.append(
        f"**{len(qualified)} of {len(results)} companies are safe to act on.** "
        "Safe means every fit field traces to a source that currently supports it, "
        "the trust core accepted it, and it clears rubric v1. The rest are listed "
        "with the exact gap, not padded into the list."
    )
    lines.append("")

    if qualified:
        lines.append("## Qualified")
        lines.append("")
        for r in qualified:
            lines.append(f"### {r.company} ({r.domain})")
            if r.actions:
                lines.append(f"- sourced by: {'; '.join(r.actions)}")
            for v in r.verdicts:
                if v.decision == "accept":
                    f = v.trace["field"]
                    src = v.trace["sources"][0] if v.trace["sources"] else "no source"
                    lines.append(f"- **{f}**: {r.accepted.get(f)}  \n  source: {src}  \n  check: {v.reason}")
            lines.append("")

    degraded = [r for r in results if not r.qualified]
    if degraded:
        lines.append("## Held back, with the gap named")
        lines.append("")
        for r in degraded:
            lines.append(f"### {r.company} ({r.domain})")
            for v in r.verdicts:
                if v.decision != "accept":
                    lines.append(f"- dropped **{v.trace['field']}**: {v.reason}")
            for gap in r.fit.gaps:
                lines.append(f"- fit gap: {gap}")
            lines.append("")

    lines.append("---")
    lines.append(
        f"Headline: **{len(qualified)} of {len(results)} safe to act on**, "
        "each backed by a source the trust core accepted under rubric v1."
    )
    return "\n".join(lines)


if __name__ == "__main__":
    print(render(run()))
