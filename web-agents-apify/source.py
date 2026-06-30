"""Source layer for Field Lab 01.

Apify is the data plane. The agent runs Actors through this layer to pull public
pages about a company. Each page comes back as {url, text, fetched_at}, and the
model extracts evidence-bearing fields from that text downstream.

Two implementations:

- `ApifySource` runs real Actors. It needs APIFY_TOKEN.
- `MockSource` replays a baked fixture so the whole agent loop runs offline.

The Actors the agent can choose from:

  website_crawler   crawl the company domain for first-pass signals
  jobs_board        look for hiring pages, a common reason-to-reach-out signal

A page carries its `fetched_at` so the trust core can later judge freshness. A
field with no page behind it is a missing field, not a value.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List

# Actor catalog the agent plans over. Descriptions are handed to the planner.
ACTORS: Dict[str, str] = {
    "website_crawler": "crawl the company domain (home, about, team, blog) for first-pass signals",
    "jobs_board": "look for hiring pages, a common reason-to-reach-out signal",
}

HERE = os.path.dirname(os.path.abspath(__file__))
CRAWL_PAGES = os.path.join(HERE, "fixtures", "crawl_pages.json")


def _now() -> str:
    return datetime.now(timezone.utc).date().isoformat()


class ApifySource:
    """Runs real Apify Actors. One method per Actor in the catalog."""

    def __init__(self) -> None:
        token = os.environ.get("APIFY_TOKEN")
        if not token:
            raise SystemExit("Set APIFY_TOKEN first (see .env.example).")
        from apify_client import ApifyClient
        self.client = ApifyClient(token)

    def run(self, actor: str, company: str, domain: str) -> List[dict]:
        if actor == "website_crawler":
            return self._crawl([f"https://{domain}"], max_pages=6)
        if actor == "jobs_board":
            return self._crawl([f"https://{domain}/careers", f"https://{domain}/jobs"], max_pages=4)
        return []

    def _crawl(self, urls: List[str], max_pages: int) -> List[dict]:
        run = self.client.actor("apify/website-content-crawler").call(
            run_input={
                "startUrls": [{"url": u} for u in urls],
                "maxCrawlPages": max_pages,
            },
        )
        dataset_id = None
        if isinstance(run, dict):
            dataset_id = run.get("defaultDatasetId") or run.get("default_dataset_id")
        else:
            dataset_id = (
                getattr(run, "default_dataset_id", None)
                or getattr(run, "defaultDatasetId", None)
            )
            if not dataset_id and hasattr(run, "get"):
                dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            raise RuntimeError("Apify run did not include a default dataset id.")

        fetched = _now()
        pages = []
        for item in self.client.dataset(dataset_id).iterate_items():
            pages.append({
                "url": item.get("url", ""),
                "text": item.get("text", "") or "",
                "fetched_at": fetched,
            })
        return pages


class MockSource:
    """Replays the offline fixture so the agent loop runs with no token."""

    def __init__(self, path: str = CRAWL_PAGES) -> None:
        with open(path, "r", encoding="utf-8") as fh:
            self.data = json.load(fh)

    @property
    def as_of(self) -> str:
        return self.data["as_of"]

    def run(self, actor: str, company: str, domain: str) -> List[dict]:
        company_pages = self.data["companies"].get(company, {})
        return company_pages.get(actor, [])


if __name__ == "__main__":
    # Offline demo: show what one Actor returns for one company.
    src = MockSource()
    for page in src.run("website_crawler", "Forge Labs", "forgelabs.io"):
        print(page["url"], "->", page["text"][:80])
