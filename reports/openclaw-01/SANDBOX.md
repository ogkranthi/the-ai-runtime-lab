# Sandbox and safety rules

These rules are enforced by the setup in this folder. Read them before running
anything.

## Isolation

- OpenClaw runs in Docker only, through `docker/compose.yml`. Do not run it
  against your main install or a shared host.
- The pinned version is in `VERSION.md`. Do not float the version; a moving
  target makes the evidence unreproducible.
- The config in `docker/openclaw-config/` is a non-main sandbox config. It
  enables one channel, a local WebChat channel served inside the compose
  network. It does not enable any real messaging platform.

## No real messaging platforms

Nothing in this folder uses or requires Telegram, Slack, WhatsApp, or any other
real messaging account. The only channel is the local WebChat channel. If you
find yourself adding a platform token, stop; that is out of scope here.

## Keys and spend

- Provider keys live in `.env`, which is gitignored. Copy `.env.example` and
  fill it with throwaway keys, not your production keys.
- Set a hard spend cap on each key in the provider console before you run. The
  reproductions send small inputs, but a misconfigured loop should not be able to
  spend more than a dollar or two. `.env.example` documents a suggested cap per
  provider.

## Redaction before commit

- The capture proxy redacts obvious secrets as it writes, but you must still run
  `scripts/redact-check.sh` before committing any evidence.
- `redact-check.sh` fails if a committed evidence file contains a bearer token, an
  `sk-` shaped string, or other key-shaped material. A failing check means do not
  commit; find and remove the secret first.
- Raw gateway logs are gitignored. Only sanitized capture JSON and `summary.json`
  are committed.

## Security disclosure

If a reproduction surfaces a security issue that is not already public, it does
not go in this folder. Report it privately through OpenClaw's `SECURITY.md`
process. This folder documents provider-reliability behavior that is already
visible to a user, not undisclosed vulnerabilities.
