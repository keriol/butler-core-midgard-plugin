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
- neutral routing observability events.

Midgard does not own:

- a Butler's name;
- Butler-side Asgard implementation;
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

The intended user-facing meaning is equivalent to:

> This Butler is currently unavailable. It may be offline or incorrectly configured. If you need the Doctor: <documentation link>

The localized sentence does not belong in the reusable Midgard package.

## Georges observability

Midgard does not import Alfred or Georges.

Instead, Midgard exposes a neutral observer port and emits structured routing events:

```text
midgard.route.received
midgard.route.selected
midgard.route.completed
midgard.route.failed
```

A concrete Butler host may adapt this port to its observability system. In the current private Alfred proving runtime, the adapter will project these facts into Georges.

Georges records routing success/failure independently from any client error notification.

Observer failure must not change the routing result.
