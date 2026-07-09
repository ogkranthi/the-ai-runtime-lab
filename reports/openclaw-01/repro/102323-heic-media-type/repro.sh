#!/usr/bin/env bash
# One command: generate fixtures, send the triggering inputs, capture, assert.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
# shellcheck source=/dev/null
source "$ROOT/scripts/_common.sh"

EVIDENCE="$HERE/evidence"
mkdir -p "$EVIDENCE"

python3 "$HERE/fixtures/generate.py" || true

if gateway_up; then
  export CAPTURE_DIR="$EVIDENCE" HERE WEBCHAT_URL
  if python3 - <<'PY'
import base64, os, sys
from lib.webchat import send_message, poll_reply, Blocked

here, url = os.environ["HERE"], os.environ["WEBCHAT_URL"]

def attach(fn, mt):
    p = os.path.join(here, "fixtures", fn)
    if not os.path.exists(p):
        return None
    with open(p, "rb") as f:
        return {"filename": fn, "media_type": mt, "data_base64": base64.b64encode(f.read()).decode()}

try:
    for fn, mt in [("sample.heic", "image/heic"), ("sample.tiff", "image/tiff")]:
        a = attach(fn, mt)
        if not a:
            continue
        conv = send_message(url, "anthropic-agent", "Describe this image.", [a])
        poll_reply(url, conv, timeout=60)
        for agent in ("openai-agent", "gemini-agent"):  # control
            conv = send_message(url, agent, "Describe this image.", [a])
            poll_reply(url, conv, timeout=60)
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
