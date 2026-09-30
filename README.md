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

**Asgard is not a Butler Core plugin.** It is a Butler-side plugin/entity. In the current private proving runtime, Asgard is an Alfred entity.

The project is currently in private incubation and is being developed public-ready from the first commit.

## Scope

Midgard owns provider-neutral communication-channel contracts, correlation preservation, safe routing/session metadata transport, and structured channel errors.

Midgard does not own concrete Butler runtime behavior, Butler-side entities such as Asgard, domain behavior, provider logic, UI, STT/TTS, authentication policy, or runtime creation.

## Status

Early bootstrap. Active work is tracked in GitHub Issues.

## License

Apache License 2.0.
