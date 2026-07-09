#!/usr/bin/env python3
"""Assert 102323: an Anthropic request carried an unsupported media_type and 400.

Writes evidence/summary.json. Exit 0 reproduced, 1 not reproduced, 2 blocked.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "harness"))
from lib.evidence import load_captures, write_summary  # noqa: E402
from lib.checks import media_types, UNSUPPORTED_ANTHROPIC_MEDIA  # noqa: E402

ISSUE = "102323"
TITLE = "HEIC and TIFF media type passed through to Anthropic"
VERSION = os.environ.get("OPENCLAW_VERSION", "vX.Y.Z")
MODEL = os.environ.get("ANTHROPIC_MODEL", "<anthropic model string>")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block-reason", default="")
    args = ap.parse_args()
    ev = os.path.join(HERE, "evidence")

    anthropic = [c for c in load_captures(ev) if c.get("provider") == "anthropic"]
    if not anthropic:
        reason = args.block_reason or "no Anthropic provider traffic captured"
        write_summary(ev, issue=ISSUE, title=TITLE, openclaw_version=VERSION,
                      model_target=MODEL, reproduced="blocked",
                      observed="no captured Anthropic request",
                      expected="Anthropic request with an unsupported media_type returns 400",
                      reason=reason)
        print("blocked:", reason)
        return 2

    for c in anthropic:
        bad = [m for m in media_types(c.get("request", {}).get("body"))
               if m in UNSUPPORTED_ANTHROPIC_MEDIA]
        if bad and c.get("response", {}).get("status") == 400:
            observed = f"Anthropic received media_type {bad[0]} and returned 400"
            write_summary(ev, issue=ISSUE, title=TITLE, openclaw_version=VERSION,
                          model_target=MODEL, reproduced="true", observed=observed,
                          expected="the adapter should convert or reject unsupported media before sending")
            print("reproduced:", observed)
            return 0

    observed = "Anthropic requests captured, but none carried an unsupported media_type returning 400"
    write_summary(ev, issue=ISSUE, title=TITLE, openclaw_version=VERSION,
                  model_target=MODEL, reproduced="false", observed=observed,
                  expected="unsupported media_type forwarded and 400 returned")
    print("not reproduced:", observed)
    return 1


if __name__ == "__main__":
    sys.exit(main())
