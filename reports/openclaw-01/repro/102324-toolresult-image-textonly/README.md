# 102324: tool_result image block sent to a text-only model

Upstream issue: https://github.com/openclaw/openclaw/issues/102324 (placeholder link)

## User-visible symptom

An agent runs a tool that returns an image (for example a chart or a screenshot).
If the session targets a text-only model, the turn fails with a provider 400 and
the user gets no answer, even though the tool ran.

## Expected vs actual

- Expected: the adapter checks the model's capabilities before sending. A
  text-only model should get a text description or a clear local error, not an
  image block.
- Actual: the adapter forwards the `tool_result` with its image block to a
  text-only model, and the provider rejects the request with 400.

## How to run

Set the target agent to a text-only model in `docker/openclaw-config/config.yaml`
(a model without image input), then:

```bash
bash repro.sh
```

`repro.sh` sends the prompt in `fixtures/prompt.txt`, which drives a tool call
whose result includes an image. The capture proxy records the outgoing provider
request. `assert.py` checks that a captured request contains a `tool_result` with
an image block and that the response is 400.

Reproduced means: a captured provider request contains a `tool_result` image block
and the response status is 400.
