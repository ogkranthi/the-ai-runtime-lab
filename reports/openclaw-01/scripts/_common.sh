# Sourced by every repro.sh. Loads .env and sets shared paths. Not executable on
# its own.

# ROOT must be set by the caller before sourcing.
: "${ROOT:?ROOT must be set before sourcing _common.sh}"

# Load throwaway keys and settings from .env if present.
if [ -f "$ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$ROOT/.env"
  set +a
fi

: "${WEBCHAT_URL:=http://localhost:8080}"
export WEBCHAT_URL
export PYTHONPATH="$ROOT/harness:${PYTHONPATH:-}"

# gateway_up: returns 0 if the local WebChat channel answers, 1 otherwise.
gateway_up() {
  python3 - "$WEBCHAT_URL" <<'PY'
import sys
sys.path.insert(0, __import__("os").environ["PYTHONPATH"].split(":")[0])
from lib.webchat import gateway_up
sys.exit(0 if gateway_up(sys.argv[1]) else 1)
PY
}
