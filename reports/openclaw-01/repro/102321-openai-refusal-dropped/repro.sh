#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
# shellcheck source=/dev/null
source "$ROOT/scripts/_common.sh"
EVIDENCE="$HERE/evidence"
mkdir -p "$EVIDENCE"

if gateway_up; then
  export CAPTURE_DIR="$EVIDENCE" HERE WEBCHAT_URL
  if python3 - <<'PY'
import json, os, sys
from lib.webchat import send_message, poll_reply, Blocked
here, url = os.environ["HERE"], os.environ["WEBCHAT_URL"]
prompt = open(os.path.join(here, "fixtures", "prompt.txt"), encoding="utf-8").read()
try:
    conv = send_message(url, "openai-agent", prompt)
    reply = poll_reply(url, conv, timeout=90)
    # Record the user-visible reply so assert.py can compare it to the provider body.
    delivered = {"assistant_text": reply.get("assistant_text"), "error": reply.get("error")}
    with open(os.path.join(here, "evidence", "webchat-reply.json"), "w", encoding="utf-8") as fh:
        json.dump(delivered, fh, indent=2)
except Blocked as exc:
    print("blocked:", exc); sys.exit(3)
PY
  then
    sleep 2
    python3 "$HERE/assert.py"
  else
    python3 "$HERE/assert.py" --block-reason "trigger did not complete; see gateway logs"
  fi
else
  python3 "$HERE/assert.py" --block-reason "gateway not reachable at $WEBCHAT_URL"
fi
