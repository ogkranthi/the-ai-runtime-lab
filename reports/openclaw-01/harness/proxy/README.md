# Capture proxy

`capture_addon.py` is a mitmproxy addon. It is the evidence mechanism for this
whole folder. It records what OpenClaw actually put on the wire to each provider,
so a claim like "the original media_type was forwarded to Anthropic" is shown, not
asserted.

## How it fits together

1. `docker/openclaw-config/config.yaml` points each provider `base_url` at the
   proxy, and the compose file also sets `HTTPS_PROXY` on the gateway. Either path
   sends outgoing provider traffic through mitmdump.
2. For every request that targets a known provider host or base-url prefix, the
   addon writes one sanitized JSON file into `CAPTURE_DIR` (the active repro's
   `evidence/` directory, set by `repro.sh`).
3. Each file holds the request (method, path, content-type, body) and the response
   (status, content-type, body). Headers are dropped except content-type, so no
   `Authorization` or `x-api-key` reaches disk. Bodies are kept, but every string
   is run through `harness/lib/redact.py`.

## What it deliberately does not do

- It does not keep request headers beyond content-type.
- It does not store secrets. If a body somehow contains a key-shaped string, the
  redactor replaces it, and `scripts/redact-check.sh` is the backstop before
  commit.
- It does not touch any non-provider traffic.
