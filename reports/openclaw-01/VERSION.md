# Pinned versions

Fill these in from the environment you assessed. The evidence is only
reproducible against a pinned version.

- OpenClaw release: `vX.Y.Z` (placeholder, set to the release you ran)
- OpenClaw commit hash: `<40-char sha>` (placeholder)
- Config snapshot date: `2026-07-03`
- Capture proxy: mitmproxy `X.Y` (placeholder, set to the version in the compose file)

## Provider model targets used in the reproductions

The exact model strings are set in `docker/openclaw-config/` and echoed into each
`summary.json` under `model_target`. Record the versions you used here as well,
so a re-run can match them.

- Anthropic: `<model string>`
- OpenAI: `<model string>`
- Gemini: `<model string>`

## How to update

When you re-run against a newer OpenClaw release, bump the release and commit
hash here, re-run `scripts/run-all.sh`, and note in `FINDINGS.md` any issue whose
`reproduced` value changed. A change from `true` to `false` with a fix commit
noted is a finding, not a regression in this work.
