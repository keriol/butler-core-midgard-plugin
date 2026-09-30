# Midgard architecture

Midgard is the reusable cross-Butler communication channel between Bifröst and Butler Core.

## Canonical routing model

Every concrete Butler owns its own Asgard entity. Asgard is the authoritative source of that Butler's name.

Midgard observes the Asgard targets available to it and chooses the requested Butler universe.

```text
                       Asgard("Butler-A") -> Butler A
                      /
Bifröst -> Midgard --+-- Asgard("Butler-B") -> Butler B
                      \
                       Asgard("Butler-C") -> Butler C
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

## Routing failures

There is no implicit default Butler.

Stable failures include:

- missing target;
- unknown target;
- unavailable target;
- duplicate/ambiguous identity;
- downstream ingress failure;
- correlation mismatch;
- source-identity mismatch.

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

This preserves the rule:

```text
Midgard -> neutral routing event -> Alfred adapter -> Georges
```

Georges records the fact. Osvaldo remains responsible for deciding whether an eligible event becomes user-facing communication, and Hermes/Bifröst remain delivery mechanisms after policy approval.

Observer failure must not change the routing result.
