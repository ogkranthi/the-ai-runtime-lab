#!/usr/bin/env bash
# Run every reproduction, then regenerate the status table in FINDINGS.md. The
# working-notes section below the table is hand-written and is never touched.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

for d in repro/*/; do
  if [ -f "${d}repro.sh" ]; then
    echo "== running ${d}"
    bash "${d}repro.sh" || echo "   (repro exited nonzero; outcome recorded in summary.json)"
  fi
done

echo "== regenerating FINDINGS table"
python3 - "$ROOT" <<'PY'
import json, os, sys

root = sys.argv[1]
begin = "<!-- BEGIN GENERATED TABLE -->"
end = "<!-- END GENERATED TABLE -->"

rows = []
for d in sorted(os.listdir(os.path.join(root, "repro"))):
    summary = os.path.join(root, "repro", d, "evidence", "summary.json")
    if not os.path.isfile(summary):
        rows.append((d, "no run", "-", "-"))
        continue
    with open(summary, encoding="utf-8") as fh:
        s = json.load(fh)
    link = f"[evidence](repro/{d}/evidence/)"
    rows.append((s.get("issue", d), s.get("reproduced", "?"),
                 s.get("model_target", "-"), link))

table = ["| Issue | Reproduced | Model | Evidence |",
         "|-------|------------|-------|----------|"]
for issue, repro, model, link in rows:
    table.append(f"| {issue} | {repro} | {model} | {link} |")
block = begin + "\n" + "\n".join(table) + "\n" + end

path = os.path.join(root, "FINDINGS.md")
with open(path, encoding="utf-8") as fh:
    text = fh.read()

if begin in text and end in text:
    pre = text[: text.index(begin)]
    post = text[text.index(end) + len(end):]
    text = pre + block + post
else:
    text = block + "\n\n" + text

with open(path, "w", encoding="utf-8") as fh:
    fh.write(text)
print("FINDINGS table updated with", len(rows), "rows")
PY
