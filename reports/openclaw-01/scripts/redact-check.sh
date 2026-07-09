#!/usr/bin/env bash
# Fail if any committed evidence file contains a key-shaped string. Run before
# committing. Scans evidence directories only, where captured payloads live.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Key-shaped patterns. Kept in sync with harness/lib/redact.py.
PATTERNS=(
  'sk-[A-Za-z0-9_-]{16,}'
  'AIza[0-9A-Za-z_-]{20,}'
  'Bearer[[:space:]]+[A-Za-z0-9._-]{16,}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  'AKIA[0-9A-Z]{16}'
)

# Files to scan: everything under any evidence/ directory.
mapfile -t FILES < <(find "$ROOT" -type f -path '*/evidence/*' \
  \( -name '*.json' -o -name '*.log' -o -name '*.txt' -o -name '*.md' \) 2>/dev/null)

if [ "${#FILES[@]}" -eq 0 ]; then
  echo "redact-check: no evidence files to scan (clean)."
  exit 0
fi

hits=0
for pat in "${PATTERNS[@]}"; do
  if grep -RInE "$pat" "${FILES[@]}" 2>/dev/null; then
    hits=1
  fi
done

if [ "$hits" -ne 0 ]; then
  echo ""
  echo "redact-check FAILED: key-shaped material found in evidence. Do not commit."
  echo "Remove the secret, re-run the repro, and check again."
  exit 1
fi

echo "redact-check passed: no key-shaped strings in ${#FILES[@]} evidence file(s)."
exit 0
