#!/usr/bin/env python3
"""Assert 102321: OpenAI returned a refusal but the delivered reply is empty."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "harness"))
from lib.evidence import load_captures, write_summary  # noqa: E402
from lib.checks import refusal_present  # noqa: E402

ISSUE = "102321"
TITLE = "OpenAI refusal dropped from the reply"
VERSION = os.environ.get("OPENCLAW_VERSION", "vX.Y.Z")
MODEL = os.environ.get("OPENAI_MODEL", "<openai model string>")


def delivered_reply(ev: str):
    path = os.path.join(ev, "webchat-reply.json")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block-reason", default="")
    args = ap.parse_args()
    ev = os.path.join(HERE, "evidence")

    openai = [c for c in load_captures(ev) if c.get("provider") == "openai"]
    reply = delivered_reply(ev)
    if not openai or reply is None:
        reason = args.block_reason or "missing OpenAI capture or delivered reply"
        write_summary(ev, issue=ISSUE, title=TITLE, openclaw_version=VERSION,
                      model_target=MODEL, reproduced="blocked",
                      observed="no captured OpenAI response with a delivered reply",
                      expected="response has a refusal while the delivered reply is empty",
                      reason=reason)
        print("blocked:", reason)
        return 2

    has_refusal = any(refusal_present(c.get("response", {}).get("body")) for c in openai)
    delivered_text = (reply.get("assistant_text") or "").strip()

    if has_refusal and not delivered_text:
        observed = "OpenAI response carried a refusal, but the delivered reply was empty"
        write_summary(ev, issue=ISSUE, title=TITLE, openclaw_version=VERSION,
                      model_target=MODEL, reproduced="true", observed=observed,
                      expected="the adapter should deliver the refusal text to the user")
        print("reproduced:", observed)
        return 0

    observed = f"refusal_present={has_refusal}, delivered_text_empty={not delivered_text}"
    write_summary(ev, issue=ISSUE, title=TITLE, openclaw_version=VERSION,
                  model_target=MODEL, reproduced="false", observed=observed,
                  expected="refusal present and delivered reply empty")
    print("not reproduced:", observed)
    return 1


if __name__ == "__main__":
    sys.exit(main())
