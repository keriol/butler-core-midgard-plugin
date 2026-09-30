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
[runtime required]
      |
    Asgard
      |
active Butler runtime
```

Responses return through the same path in reverse.

The project is currently in private incubation and is being developed public-ready from the first commit.

## Scope

Midgard owns provider-neutral communication-channel contracts, correlation preservation, safe routing/session metadata transport, and structured channel errors.

Midgard does not own concrete Butler runtime resolution, domain behavior, provider logic, UI, STT/TTS, authentication policy, or runtime creation.

## Status

Early bootstrap. Active work is tracked in GitHub Issues.

## License

Apache License 2.0.
