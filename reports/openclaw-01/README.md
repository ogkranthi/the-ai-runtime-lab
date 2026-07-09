# OpenClaw provider reliability, readiness Installment 01

This folder is the reproducibility base for readiness Installment 01, an
assessment of OpenClaw provider-adapter reliability. The prose report lives on
the site. This folder holds the evidence: anyone can clone it, bring their own
API keys, and re-run every reproduction that backs the published claims.

Published report: https://lab.theairuntime.com/readiness/openclaw-01 (placeholder, update on publish)

## What this assesses

OpenClaw is a multi-provider gateway. It accepts messages on a channel and
forwards them to a provider (Anthropic, OpenAI, Gemini, and others) through a
per-provider adapter. This installment looks at four adapter behaviors where the
gateway forwards a request the provider rejects, or drops content the provider
returned, so the user sees a failure with no useful signal.

The four reproductions:

| Issue | Short name | Provider |
|-------|------------|----------|
| 102323 | HEIC and TIFF media type passed through | Anthropic |
| 102324 | tool_result image block to a text-only model | provider-agnostic |
| 102321 | OpenAI refusal dropped from the reply | OpenAI |
| 102320 | Gemini provider-prefixed model id capability check | Gemini |

Each reproduction is self-contained under `repro/<issue>/` and produces a
`summary.json` you can audit.

## Quickstart

```bash
cp .env.example .env          # add throwaway keys, see SANDBOX.md for spend caps
docker compose -f docker/compose.yml up -d
bash scripts/run-all.sh       # runs every repro, regenerates the FINDINGS table
bash scripts/redact-check.sh  # fails if any evidence file contains a key-shaped string
```

Each repro also runs on its own:

```bash
bash repro/102323-heic-media-type/repro.sh
```

## The rules that keep this safe

- OpenClaw runs in Docker only, pinned to the release in `VERSION.md`, with a
  non-main sandbox config and a local WebChat channel. No real messaging
  platform (no Telegram, no Slack, no WhatsApp) is used anywhere in this folder.
- Keys are throwaway, kept in a gitignored `.env`, with hard spend caps.
- Every committed evidence file passes `scripts/redact-check.sh` first.
- If a reproduction surfaces an unreported security issue, it goes to OpenClaw's
  `SECURITY.md` privately and does not appear in this folder.

See `SANDBOX.md` for the full setup and safety rules.
