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
[runtime required]
      |
    Asgard
      |
active Butler runtime
```

Responses travel through the same chain in reverse.

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
- target Butler resolution;
- Asgard runtime lookup;
- concrete runtime lifecycle;
- domain intent parsing or business logic;
- provider-specific behavior;
- authentication, permission or confirmation policy.

## Target Butler metadata

A request may carry `target_butler_name`.

Midgard transports that value without resolving it. When a concrete active Butler runtime must be addressed, target resolution belongs to Asgard.

This distinction is deliberate: carrying routing metadata is a communication concern; deciding which concrete runtime instance it identifies is not.

## Core-facing seam

MID-001 uses an injected `CoreRequestHandler` protocol.

The protocol is intentionally small and runtime-neutral. It proves the communication contract without forcing Midgard to depend on Alfred, Wilfred, an HTTP transport, or a runtime loader.

A later integration slice can connect this seam to Butler Core using evidence from a real consumer rather than inventing a broader Core abstraction prematurely.
