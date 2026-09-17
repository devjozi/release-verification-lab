# Architecture

## Boundary

The system separates **build validity** from **release validity**.

```text
source
  |
  +--> syntax checks
  +--> unit tests
  |
  +--> deterministic build --> release archive --> SHA-256
                                           |
                                           +--> integrity verification

running service ---------------------------------> /healthz
                                                   |
                                                   +--> behavior verification

CI orchestrates the same checks and fails the run when any required gate fails.
```

## Components

### `src/service.py`
Minimal HTTP service used as the deployable workload. Its purpose is to provide a real running target for verification rather than pretending the build itself proves runtime health.

### `tests/`
Fast unit-level checks for the service contract.

### `scripts/build.py`
Creates a deterministic source archive and a SHA-256 sidecar file. The build step is intentionally boring and inspectable.

### `scripts/verify_release.py`
The release gate. It verifies the artifact checksum and then probes `/healthz` on a running instance.

### `.github/workflows/ci.yml`
Replays the release contract in a clean GitHub-hosted environment.

## Core invariants

1. **CI success is not deployment success.** CI must include a check against the output or running system that matters.
2. **Artifact identity is explicit.** The artifact being verified is identified by path and checksum rather than by an implicit workspace state.
3. **The runtime contract is observable.** Verification uses an externally visible HTTP response.
4. **Verification is fail-closed.** A checksum mismatch, non-200 response, malformed payload or wrong health state fails the gate.
5. **Portfolio claims stay bounded.** This repository demonstrates a release-verification pattern; it does not claim production adoption, uptime or customer outcomes.

## Failure boundaries

A green build can still fail after artifact creation or when the service starts. The important boundary is therefore:

`build passed` != `artifact verified` != `runtime verified`.

The lab is designed to make those states inspectable separately.
