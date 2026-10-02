# Butler Core Midgard Plugin

**The cross-Butler communication channel for the Butler ecosystem.**

Midgard sits between external/client bridges such as Bifröst and Butler Core.

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

Responses return through the same communication path in reverse.

**Asgard is not a Butler Core plugin.** It is a Butler-side ingress abstraction supplied by a concrete Butler runtime and remains outside this package.

Midgard 0.0.1 is the first Public Alpha checkpoint of the provider-neutral communication layer.

## Scope

Midgard owns provider-neutral communication-channel contracts, correlation preservation, safe routing/session metadata transport, and structured channel errors.

Midgard does not own concrete Butler runtime behavior, Butler-side entities such as Asgard, domain behavior, provider logic, UI, STT/TTS, authentication policy, or runtime creation.

## Status

Current Public Alpha: **0.0.1**.

The 0.0.1 line provides the live-proven Core-facing channel, explicit Butler-target routing boundary, Butler directory projection and client-manifest aggregation. A reusable standalone Asgard implementation is deliberately not part of this release. Active work is tracked in GitHub Issues.

## License

Apache License 2.0.
