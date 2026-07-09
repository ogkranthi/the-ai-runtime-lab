# Readiness rubric

Six dimensions. Each gets one rating: pass, gate, or fail. Pass means ready for
the use case as assessed. Gate means usable with a named compensating control.
Fail means not ready without upstream change. The scorecard in `scorecard.yaml`
records the rating and a one-line reason per dimension.

## Identity and permissions

How the system establishes who is acting and what they may do: channel
authentication, per-agent scoping, and the separation between a sandbox config and
a production one. Pass: identities are explicit and least-privilege, and a sandbox
cannot reach production channels or keys. Gate: workable isolation exists but
depends on operator discipline rather than enforced boundaries. Fail: a
misconfiguration can let one agent or channel act with another's authority.

## Data handling and retention

What the system sends to providers, what it logs, and how long it keeps it. Pass:
outbound payloads are minimal and predictable, logs redact secrets, and retention
is bounded and documented. Gate: handling is acceptable but retention or
redaction depends on manual steps. Fail: secrets or user content land in logs or
provider requests in ways the operator cannot see or control.

## Failure modes and blast radius

What happens when a provider rejects a request or returns something unexpected,
and how far that failure spreads. Pass: failures are contained to the turn, the
user gets a clear signal, and one bad input cannot stall the channel. Gate:
failures are contained but the user-facing signal is poor. Fail: a single
rejected request produces an empty or misleading reply, or takes down more than
the turn. The four reproductions in this folder all live in this dimension.

## Observability and debuggability

Whether an operator can see what happened and reconstruct why. Pass: requests,
responses, and errors are visible and correlatable without extra instrumentation.
Gate: the signal exists but requires assembling logs by hand. Fail: a failed turn
leaves no usable trace, so the operator cannot tell a dropped refusal from a
provider outage.

## Upgrade and release risk

How safe it is to move between versions: pinning, changelogs, and the chance that
an adapter change silently alters behavior. Pass: versions pin cleanly, changes
are documented, and adapter behavior is testable before rollout. Gate: upgrades
are workable but under-documented, so a re-test is required each time. Fail:
behavior shifts between releases without notice, so a working config can break on
upgrade.

## Operational maturity

The day-two posture: config ergonomics, defaults, the quality of the sandbox
story, and how the project handles reported issues. Pass: safe defaults, a real
sandbox path, and responsive issue handling. Gate: usable but with sharp edges
that an experienced operator can manage. Fail: defaults are unsafe or the project
does not engage with reliability reports.
