# Midgard architecture

Midgard is the reusable cross-Butler communication channel between Bifröst and Butler Core.

```text
external client
      |
    Bifröst
      |
    Midgard
      |
  Butler Core
      |
 concrete Butler runtime
      |
 Butler-owned ingress entity
 (for Alfred: Asgard)
```

Responses travel through the same communication path in reverse.

## Ownership

Midgard owns:

- provider-neutral request/response channel contracts;
- request correlation preservation;
- safe routing/session metadata transport;
- a Core-facing handler seam;
- structured channel failures.

Midgard does not own:

- client UI, STT or TTS;
- Bifröst transport/session implementation;
- Butler-side entities such as Asgard;
- concrete runtime lifecycle;
- domain intent parsing or business logic;
- provider-specific behavior;
- authentication, permission or confirmation policy.

## Asgard ownership

Asgard is **not** a Butler Core plugin and is not part of Midgard.

Asgard is a Butler-side plugin/entity. In the current private proving runtime, it is an entity of Alfred.

Midgard/Core may communicate toward a concrete Butler runtime through a Butler-owned ingress boundary, but ownership of that boundary remains with the Butler.

## Target Butler metadata

A request may carry `target_butler_name`.

MID-001 only transports that metadata. It deliberately does **not** define which component resolves a requested Butler name to a concrete runtime.

That routing responsibility must be specified separately. In particular, it must not be assigned to Alfred's Asgard entity merely because Asgard is the Butler-side ingress boundary.

## Core-facing seam

MID-001 uses an injected `CoreRequestHandler` protocol.

The protocol is intentionally small and runtime-neutral. It proves the communication contract without forcing Midgard to depend on Alfred, Wilfred, an HTTP transport, Asgard, or a runtime loader.

A later integration slice can connect this seam to Butler Core using evidence from a real consumer rather than inventing a broader Core abstraction prematurely.
