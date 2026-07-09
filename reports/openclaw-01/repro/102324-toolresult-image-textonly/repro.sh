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
import os, sys
from lib.webchat import send_message, poll_reply, Blocked
here, url = os.environ["HERE"], os.environ["WEBCHAT_URL"]
prompt = open(os.path.join(here, "fixtures", "prompt.txt"), encoding="utf-8").read()
try:
    # Target agent must be set to a text-only model in the sandbox config.
    conv = send_message(url, "openai-agent", prompt)
    poll_reply(url, conv, timeout=90)
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
