# 102321: OpenAI refusal dropped from the reply

Upstream issue: https://github.com/openclaw/openclaw/issues/102321 (placeholder link)

## User-visible symptom

The user sends a request the OpenAI model declines. Instead of a refusal message,
the user sees an empty reply with no explanation.

## Expected vs actual

- Expected: when the model returns a refusal, the user sees it, so they know the
  request was declined rather than lost.
- Actual: the chat-completions response carries a `refusal` field, but the adapter
  maps only the assistant `content` to the channel. A refusal has empty content,
  so the user gets an empty reply and the refusal text never reaches them.

## How to run

```bash
bash repro.sh
```

`repro.sh` sends the prompt in `fixtures/prompt.txt`, which is written to elicit a
model refusal. The capture proxy records the OpenAI response. The script also
saves the user-visible WebChat reply to `evidence/webchat-reply.json`. `assert.py`
checks that the captured response has a non-empty `refusal` while the delivered
reply is empty.

Reproduced means: the captured OpenAI response contains a `refusal`, and the
delivered assistant text in `webchat-reply.json` is empty.
