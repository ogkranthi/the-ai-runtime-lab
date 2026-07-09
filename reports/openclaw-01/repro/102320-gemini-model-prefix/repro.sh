#!/usr/bin/env bash
# Two-variant repro. Run with VARIANT=prefixed, then VARIANT=control, each after
# setting the Gemini model id in the config and restarting the gateway.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
# shellcheck source=/dev/null
source "$ROOT/scripts/_common.sh"
EVIDENCE="$HERE/evidence"
mkdir -p "$EVIDENCE"
VARIANT="${VARIANT:-prefixed}"

if gateway_up; then
  export CAPTURE_DIR="$EVIDENCE" HERE WEBCHAT_URL VARIANT
  if python3 - <<'PY'
import json, os, sys
from lib.webchat import send_message, poll_reply, Blocked
from lib.evidence import load_captures
here, url, variant = os.environ["HERE"], os.environ["WEBCHAT_URL"], os.environ["VARIANT"]
prompt = open(os.path.join(here, "fixtures", "prompt.txt"), encoding="utf-8").read()
try:
    conv = send_message(url, "gemini-agent", prompt)
    reply = poll_reply(url, conv, timeout=90)
except Blocked as exc:
    print("blocked:", exc); sys.exit(3)
# A functionResponse request reaching Gemini means the capability check passed.
caps = [c for c in load_captures(os.path.join(here, "evidence")) if c.get("provider") == "gemini"]
saw_fn = any("functionResponse" in json.dumps(c.get("request", {}).get("body", "")) for c in caps)
capability_ok = saw_fn and not reply.get("error")
out = {"variant": variant, "capability_ok": bool(capability_ok),
       "gemini_request_seen": bool(saw_fn), "error": reply.get("error")}
with open(os.path.join(here, "evidence", f"{variant}-outcome.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2)
print("variant", variant, "capability_ok", capability_ok)
PY
  then
    python3 "$HERE/assert.py"
  else
    python3 "$HERE/assert.py" --block-reason "trigger did not complete; see gateway logs"
  fi
else
  python3 "$HERE/assert.py" --block-reason "gateway not reachable at $WEBCHAT_URL"
fi
