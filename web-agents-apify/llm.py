"""Model layer for the module 1 agent.

The agent reasons in two places: it plans which Apify Actor to run next, and it
extracts rubric fields with evidence from crawled pages. Both go through a Model.

Two implementations:

- `LLMModel`  calls a real model. It picks Anthropic when ANTHROPIC_API_KEY is
  set, otherwise OpenRouter when OPENROUTER_API_KEY is set. Imports are lazy so
  the offline path never needs these packages installed.
- `MockModel` reads the page annotations baked into the offline fixture, so the
  whole agent loop runs and is verifiable with no key and no network.

Extraction returns evidence, never bare values. A value the model cannot ground
in a verbatim page snippet is dropped, not guessed. That is the contract the
trust core depends on.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List

from models import Evidence

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - keep offline path resilient
    load_dotenv = None

if load_dotenv:
    # Make live mode work from plain terminals by loading project .env values.
    load_dotenv()


def _strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        if t.endswith("```"):
            t = t[: -3]
        if t.startswith("json"):
            t = t[4:]
    return t.strip()


class Model:
    """Interface shared by the live and mock models."""

    def plan(self, company: str, domain: str, gaps: List[str],
             actors: Dict[str, str], tried: List[str]) -> dict:
        raise NotImplementedError

    def extract(self, company: str, pages: List[dict],
                fields: List[tuple]) -> List[dict]:
        raise NotImplementedError


class MockModel(Model):
    """Offline model. Plans a fixed sourcing order and reads page annotations.

    The fixture pages carry an `extractable` list, which stands in for what a real
    model would pull from the page text. The snippet still comes from the page, so
    the evidence the trust core sees is honest.
    """

    def plan(self, company, domain, gaps, actors, tried):
        if "website_crawler" not in tried:
            return {"actor": "website_crawler",
                    "rationale": "crawl the company site for first-pass signals"}
        if "reason_to_reach_out" in gaps and "jobs_board" not in tried:
            return {"actor": "jobs_board",
                    "rationale": "check hiring pages for a reason to reach out now"}
        return {"actor": "stop",
                "rationale": "no remaining source is likely to fill the open gaps"}

    def extract(self, company, pages, fields):
        wanted = {name for name, _ in fields}
        hits: List[dict] = []
        for page in pages:
            for ann in page.get("extractable", []):
                if ann["field"] not in wanted:
                    continue
                hits.append({
                    "field": ann["field"],
                    "value": ann["value"],
                    "evidence": Evidence(
                        source_url=page["url"],
                        snippet=ann["snippet"],
                        fetched_at=page["fetched_at"],
                        claimed_value=ann.get("claimed_value", ann["value"]),
                        entity=company,
                    ),
                })
        return hits


class LLMModel(Model):
    """Live model. Anthropic if its key is set, else OpenRouter."""

    def __init__(self) -> None:
        if os.environ.get("ANTHROPIC_API_KEY"):
            self.provider = "anthropic"
            self.model = os.environ.get("MODEL", "claude-sonnet-5")
        elif os.environ.get("OPENROUTER_API_KEY"):
            self.provider = "openrouter"
            self.model = os.environ.get("MODEL", "anthropic/claude-sonnet-5")
        else:
            raise SystemExit(
                "Set ANTHROPIC_API_KEY or OPENROUTER_API_KEY for live mode, "
                "or run the agent offline (see README)."
            )

    def _chat(self, system: str, user: str) -> str:
        if self.provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic()
            msg = client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return msg.content[0].text
        import requests
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def plan(self, company, domain, gaps, actors, tried):
        system = (
            "You plan one sourcing step for a B2B sales-research agent. "
            "Pick the single Actor most likely to fill an open gap, or stop. "
            "Reply with strict JSON: {\"actor\": <name or 'stop'>, \"rationale\": <str>}."
        )
        catalog = "\n".join(f"- {name}: {desc}" for name, desc in actors.items())
        user = (
            f"Company: {company} ({domain})\n"
            f"Open gaps: {', '.join(gaps) or 'none'}\n"
            f"Actors already tried: {', '.join(tried) or 'none'}\n"
            f"Available actors:\n{catalog}\n"
            "Choose the next actor, or 'stop' if nothing is likely to help."
        )
        try:
            return json.loads(_strip_fences(self._chat(system, user)))
        except Exception:
            return {"actor": "stop", "rationale": "planner returned unparseable output"}

    def extract(self, company, pages, fields):
        specs = "\n".join(f"- {name}: {desc}" for name, desc in fields)
        system = (
            "You extract structured fields from crawled web pages for a sales "
            "rubric. For each field you can support, return the value and the "
            "exact verbatim snippet from the page that backs it. Never invent a "
            "value. If a field is not supported by the pages, omit it. Reply with "
            "strict JSON: a list of objects with keys field, value, snippet, "
            "source_url, fetched_at."
        )
        payload = [
            {"url": p["url"], "fetched_at": p["fetched_at"], "text": p["text"]}
            for p in pages
        ]
        user = (
            f"Company: {company}\nFields to extract:\n{specs}\n\n"
            f"Pages (JSON):\n{json.dumps(payload)}"
        )
        try:
            rows = json.loads(_strip_fences(self._chat(system, user)))
        except Exception:
            return []

        hits: List[dict] = []
        for r in rows:
            snippet = r.get("snippet", "")
            source_url = r.get("source_url", "")
            # Ground the snippet: it must actually appear on the cited page.
            page = next((p for p in pages if p["url"] == source_url), None)
            if not page or not snippet or snippet not in page["text"]:
                continue
            hits.append({
                "field": r["field"],
                "value": r["value"],
                "evidence": Evidence(
                    source_url=source_url,
                    snippet=snippet,
                    fetched_at=r.get("fetched_at", page["fetched_at"]),
                    claimed_value=r["value"],
                    entity=company,
                ),
            })
        return hits
