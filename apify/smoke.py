"""Thirty-second check that your Apify token works before the workshop.

Runs a tiny one-page crawl through the Apify SDK and prints the run status.
Expected output: "apify ok: SUCCEEDED".
"""
import os

from apify_client import ApifyClient


def main() -> None:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise SystemExit("Set APIFY_TOKEN first (see .env.example).")

    client = ApifyClient(token)
    run = client.actor("apify/website-content-crawler").call(
        run_input={
            "startUrls": [{"url": "https://example.com"}],
            "maxCrawlPages": 1,
        },
    )
    print("apify ok:", run["status"])


if __name__ == "__main__":
    main()
