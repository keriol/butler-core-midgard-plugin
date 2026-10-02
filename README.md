# Butler Core Midgard Plugin 🌉

**Provider-neutral communication and cross-Butler routing for the Butler ecosystem.**

Midgard sits between client bridges such as Bifröst and Butler Core. It owns
routing semantics and correlation preservation without owning any concrete
Butler runtime.

```text
external client
      |
    Bifröst
      |
    Midgard
      |
  Butler Core
```

For explicit concrete-Butler traffic:

```text
Bifröst
   |
Midgard
   |
Butler-owned Asgard
   |
concrete Butler
```

## Current release

**Public Alpha: 0.1.0 — Ignition**

Midgard 0.1.0 is the first network-capable release validated in
**IGNITION-001**, the coordinated Butler-to-Android baseline.

## Responsibilities

Midgard owns:

- provider-neutral communication-channel contracts;
- explicit Butler target routing;
- request correlation preservation;
- canonical source-Butler identity checks;
- visible Butler directory projection;
- node-manifest aggregation;
- structured routing/channel errors;
- provider-neutral tracing hooks.

Midgard does **not** own:

- concrete Butler behavior;
- Asgard implementations;
- client UI;
- STT/TTS;
- household policy;
- Home Assistant provider logic;
- authentication policy.

## Butler identity

Each concrete Butler owns its own ingress boundary and declares its own
canonical identity.

Midgard resolves explicit Butler targets against those declared identities. It
does not fabricate or silently substitute a Butler name.

A successful concrete-Butler response must preserve:

```text
request_id
source_butler_name
```

## Butler unavailable

Routing failures remain structured and provider-neutral.

A client may receive a neutral `butler_unavailable` notification descriptor,
but localized presentation remains a client responsibility.

## Development

Python 3.10 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
python -m build
```

## Public boundary

The package intentionally contains no:

- concrete Alfred/Wilfred implementation;
- household entity identifiers;
- private deployment configuration;
- provider credentials.

Public boundary tests enforce this separation.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

Active work and release evidence are tracked in GitHub Issues.

## Security

See [SECURITY.md](SECURITY.md).

## License

Apache License 2.0.
