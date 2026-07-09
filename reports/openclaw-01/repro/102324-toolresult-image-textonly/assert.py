#!/usr/bin/env python3
"""Assert 102324: a tool_result image block reached a provider and got 400."""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "harness"))
from lib.evidence import load_captures, write_summary  # noqa: E402
from lib.checks import has_tool_result_image  # noqa: E402

ISSUE = "102324"
TITLE = "tool_result image block sent to a text-only model"
VERSION = os.environ.get("OPENCLAW_VERSION", "vX.Y.Z")
MODEL = os.environ.get("TEXTONLY_MODEL", "<text-only model string>")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block-reason", default="")
    args = ap.parse_args()
    ev = os.path.join(HERE, "evidence")

    captures = [c for c in load_captures(ev) if c.get("provider")]
    if not captures:
        reason = args.block_reason or "no provider traffic captured"
        write_summary(ev, issue=ISSUE, title=TITLE, openclaw_version=VERSION,
                      model_target=MODEL, reproduced="blocked",
                      observed="no captured provider request",
                      expected="a tool_result image block reaches the provider and returns 400",
                      reason=reason)
        print("blocked:", reason)
        return 2

    for c in captures:
        if has_tool_result_image(c.get("request", {}).get("body")) and \
                c.get("response", {}).get("status") == 400:
            observed = "provider request carried a tool_result image block and returned 400"
            write_summary(ev, issue=ISSUE, title=TITLE, openclaw_version=VERSION,
                          model_target=MODEL, reproduced="true", observed=observed,
                          expected="the adapter should not send image blocks to a text-only model")
            print("reproduced:", observed)
            return 0

    observed = "provider requests captured, but none carried a tool_result image block returning 400"
    write_summary(ev, issue=ISSUE, title=TITLE, openclaw_version=VERSION,
                  model_target=MODEL, reproduced="false", observed=observed,
                  expected="tool_result image block forwarded and 400 returned")
    print("not reproduced:", observed)
    return 1


if __name__ == "__main__":
    sys.exit(main())
