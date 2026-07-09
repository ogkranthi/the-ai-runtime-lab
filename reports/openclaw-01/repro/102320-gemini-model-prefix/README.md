# 102320: Gemini provider-prefixed model id fails the multimodal capability check

Upstream issue: https://github.com/openclaw/openclaw/issues/102320 (placeholder link)

## User-visible symptom

A Gemini agent configured with a provider-prefixed model id (for example
`gemini/gemini-x.y`) works for plain chat but fails when a tool returns a
`functionResponse` with image or file data. The unprefixed id works on the same
path.

## Expected vs actual

- Expected: the capability check accepts the model whether or not the id carries a
  provider prefix.
- Actual: the multimodal capability check compares against the unprefixed id, so a
  prefixed id fails the check on the `functionResponse` path while plain chat,
  which does not run that check, still works.

## How to run

This repro has two variants. Run each after setting the Gemini `model` in
`docker/openclaw-config/config.yaml`:

```bash
# 1. set the Gemini model to a provider-prefixed id, restart the gateway, then:
VARIANT=prefixed bash repro.sh

# 2. set the Gemini model to the plain unprefixed id, restart the gateway, then:
VARIANT=control bash repro.sh
```

Each run writes `evidence/<variant>-outcome.json`. `assert.py` compares them.

Reproduced means: the prefixed variant fails the multimodal capability check while
the unprefixed control passes the same path.
