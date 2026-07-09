# Config-level mitigations

Mitigations validated during the reproduction work. These are things an operator
can do today, without an upstream code change, to reduce the blast radius of the
four issues. Each was checked in the same sandbox that produced the evidence. A
mitigation is a compensating control, not a fix; the underlying adapter behavior
still needs an upstream change.

## 102323, HEIC and TIFF media type

Constrain the accepted upload types on the WebChat channel to the set the target
provider supports, or add a pre-send conversion step to JPEG or PNG. Constraining
the channel is the smaller change and it fails closed: an unsupported upload is
rejected with a clear message before it reaches the provider, instead of a bare
400. Validate by re-running `repro/102323` and confirming the outgoing request no
longer carries the unsupported media_type.

## 102324, tool_result image to a text-only model

Pin each agent to a model that matches the tools it can call. If a tool can return
an image, do not point that agent at a text-only model. This removes the mismatch
that triggers the 400. It does not add the missing capability check, so an
operator who later repoints the agent reintroduces the issue.

## 102321, OpenAI refusal dropped

There is no clean config-only mitigation that restores the refusal text, because
the drop happens in the adapter's response mapping. The partial control is
operational: watch for empty assistant replies paired with a non-empty provider
refusal in the captured evidence, and treat an empty reply as a signal to inspect
rather than a benign non-answer. The real fix is upstream.

## 102320, Gemini provider-prefixed model id

Configure Gemini agents with the plain, unprefixed model id. The control run in
`repro/102320` shows the unprefixed id passes the multimodal path that the
prefixed id fails. This is a one-line config change and it fully avoids the issue
for the assessed version.
