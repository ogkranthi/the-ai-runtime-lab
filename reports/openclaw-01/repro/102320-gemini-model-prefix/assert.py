#!/usr/bin/env python3
"""Assert 102320: prefixed id fails the multimodal capability check, control passes."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "harness"))
from lib.evidence import write_summary  # noqa: E402

ISSUE = "102320"
TITLE = "Gemini provider-prefixed model id fails the multimodal capability check"
VERSION = os.environ.get("OPENCLAW_VERSION", "vX.Y.Z")
MODEL = os.environ.get("GEMINI_MODEL", "<gemini model string>")


def load(ev: str, variant: str):
    path = os.path.join(ev, f"{variant}-outcome.json")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block-reason", default="")
    args = ap.parse_args()
    ev = os.path.join(HERE, "evidence")

    prefixed = load(ev, "prefixed")
    control = load(ev, "control")
    if prefixed is None or control is None:
        have = [v for v in ("prefixed", "control") if load(ev, v) is not None]
        reason = args.block_reason or (
            f"need both variants; have {have or 'none'}. Run VARIANT=prefixed and VARIANT=control.")
        write_summary(ev, issue=ISSUE, title=TITLE, openclaw_version=VERSION,
                      model_target=MODEL, reproduced="blocked",
                      observed=f"variants present: {have or 'none'}",
                      expected="prefixed capability_ok=false and control capability_ok=true",
                      reason=reason)
        print("blocked:", reason)
        return 2

    if prefixed.get("capability_ok") is False and control.get("capability_ok") is True:
        observed = "prefixed id failed the multimodal capability check while the unprefixed control passed"
        write_summary(ev, issue=ISSUE, title=TITLE, openclaw_version=VERSION,
                      model_target=MODEL, reproduced="true", observed=observed,
                      expected="the capability check should normalize the provider prefix")
        print("reproduced:", observed)
        return 0

    observed = f"prefixed capability_ok={prefixed.get('capability_ok')}, control capability_ok={control.get('capability_ok')}"
    write_summary(ev, issue=ISSUE, title=TITLE, openclaw_version=VERSION,
                  model_target=MODEL, reproduced="false", observed=observed,
                  expected="prefixed fails and control passes")
    print("not reproduced:", observed)
    return 1


if __name__ == "__main__":
    sys.exit(main())
