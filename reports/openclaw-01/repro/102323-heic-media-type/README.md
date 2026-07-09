# 102323: HEIC and TIFF media type passed through to Anthropic

Upstream issue: https://github.com/openclaw/openclaw/issues/102323 (placeholder link)

## User-visible symptom

A user sends a normal photo through WebChat to an Anthropic-backed agent. If the
photo is a HEIC (common on iPhones) or a TIFF, the agent returns nothing useful.
The same photo works on OpenAI and Gemini agents.

## Expected vs actual

- Expected: the adapter converts an unsupported image type, or rejects it with a
  clear message before sending.
- Actual: the adapter forwards the original `media_type` to Anthropic. Anthropic
  supports a fixed set of image media types; HEIC and TIFF are not in it, so the
  provider returns 400 and the user gets an empty or error reply.

## How to run

```bash
bash repro.sh
```

`repro.sh` generates tiny HEIC and TIFF fixtures, sends each through WebChat to the
Anthropic agent, and sends the same fixtures to the OpenAI and Gemini agents as a
control. The capture proxy records every outgoing provider request. `assert.py`
then checks the captured Anthropic request for the unsupported `media_type` and a
400 response, and writes `evidence/summary.json`.

Reproduced means: a captured Anthropic request carries `image/heic` or
`image/tiff` and the response status is 400.
