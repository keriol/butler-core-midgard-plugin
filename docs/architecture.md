# Midgard architecture

Midgard is the reusable cross-Butler communication channel between Bifröst and Butler Core.

## Canonical routing model

Every concrete Butler owns its own Asgard entity. Asgard is authoritative for the name/identity of that Butler.

Midgard asks the visible Asgard targets whether they belong to the requested Butler and routes to the unique positive answer.

```text
Midgard: "Who is Butler-B?"

Asgard("Butler-A") -> not me
Asgard("Butler-B") -> me
Asgard("Butler-C") -> not me

Midgard -> Asgard("Butler-B") -> Butler B
```

Butler Core remains provider-neutral. It owns neither Butler identity nor cross-Butler target selection.

## Identity ownership

Request-side routing metadata:

```text
target_butler_name
```

is carried into Midgard.

Response-side identity:

```text
source_butler_name
```

must be supplied by the selected Butler's Asgard.

Midgard verifies that the response identity matches the Asgard it selected. It never fabricates or silently substitutes a Butler identity.

## Midgard ownership

Midgard owns:

- provider-neutral request/response channel contracts;
- visibility of Butler-owned Asgard targets through a neutral port;
- deterministic cross-Butler selection;
- request correlation preservation;
- safe routing/session metadata transport;
- structured routing failures;
- semantic timing/meaning of its routing trace events.

Midgard does not own:

- a Butler's name;
- Butler-side Asgard implementation;
- Georges tracing contracts;
- trace storage/persistence;
- client UI, STT or TTS;
- Bifröst transport/session implementation;
- concrete runtime lifecycle;
- domain intent parsing or business logic;
- provider-specific behavior;
- authentication, permission or confirmation policy.

## Butler unavailable

If every visible Asgard answers "not me", Midgard returns `butler_not_found`.

If the matching Asgard is offline/unavailable, or the selected Butler fails to answer, Midgard returns the appropriate structured error.

These cases may carry the same semantic client-notification descriptor:

```text
kind = butler_unavailable
presentation = system_neutral
documentation_url = optional
```

Bifröst transports this descriptor and Interphone owns localized rendering.

This is synchronous request/response UX, not proactive Butler communication. No fallback Butler is selected and no unrelated Asgard is involved.

## Georges observability

Midgard emits routing observability through Butler Core's provider-neutral Georges tracing contract:

```text
Midgard
  |
  +-> TraceEvent("midgard.route.received")
  +-> TraceEvent("midgard.route.selected")
  +-> TraceEvent("midgard.route.completed")
  +-> TraceEvent("midgard.route.failed")
        |
        v
   injected Core Tracer
        |
        v
 concrete Butler sink
```

Midgard depends on the Core tracing API rather than maintaining a second observer/event abstraction.

Only safe routing metadata is traced. Request message bodies, credentials, endpoints and provider payloads are excluded.

Tracer failure must not change routing behavior.
