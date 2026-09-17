# release-verification-lab

A small, reproducible release-engineering system that verifies build artifacts and deployed behavior instead of trusting green CI alone.

## What this first slice proves

- the application can be syntax-checked and unit-tested
- a deterministic release artifact can be built
- the artifact has a recorded SHA-256 digest
- a running service exposes a health endpoint
- the verification step checks both artifact integrity and live behavior
- GitHub Actions runs the same checks in CI

The repository is intentionally small. The engineering value is in the release contract and the verification boundary, not in application complexity.

## Local run

```bash
python -m compileall -q src tests scripts
python -m unittest discover -s tests -v
python scripts/build.py
python src/service.py --port 8080
```

In another terminal:

```bash
python scripts/verify_release.py --artifact dist/release-verification-lab-0.1.0.tar.gz --base-url http://127.0.0.1:8080
```

## Release contract

A release is not considered healthy because CI is green. For this lab, the minimum release contract is:

1. source passes syntax checks and tests
2. a deterministic archive is produced
3. the archive digest matches its recorded checksum
4. the running service returns the expected health response

The same contract is exercised by GitHub Actions.

## Status

Initial engineering slice. This is a standalone portfolio project inspired by general release-engineering patterns. It contains no JX configuration, credentials, client identifiers or private production data.

## Next increments

- add dependency/security scanning tied to the actual dependency graph
- add versioned release metadata and GitHub Releases
- add stronger deployment smoke checks and failure reporting
- add a documented rollback/recovery path
- compare release candidates against a known-good version
