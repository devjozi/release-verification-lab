#!/usr/bin/env python3
"""Verify artifact integrity and a running release candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


EXPECTED_HEALTH = {"status": "ok", "service": "release-verification-lab"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_digest(artifact: Path) -> str:
    checksum = artifact.with_name(f"{artifact.name}.sha256")
    line = checksum.read_text(encoding="utf-8").strip()
    digest, filename = line.split(maxsplit=1)
    if filename != artifact.name:
        raise ValueError("checksum manifest names a different artifact")
    return digest


def fetch_health(base_url: str) -> dict[str, object]:
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/healthz",
        headers={"Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        if response.status != 200:
            raise RuntimeError(f"health check returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def verify_runtime(base_url: str, attempts: int = 10, delay_seconds: float = 0.5) -> None:
    """Retry briefly to absorb normal process-startup races, then fail closed."""
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            payload = fetch_health(base_url)
            if payload != EXPECTED_HEALTH:
                raise RuntimeError(f"unexpected health payload: {payload!r}")
            return
        except (OSError, ValueError, RuntimeError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(delay_seconds)

    raise RuntimeError(f"runtime health check did not pass after {attempts} attempts: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args()

    artifact = Path(args.artifact)
    actual = sha256(artifact)
    expected = expected_digest(artifact)
    if actual != expected:
        raise SystemExit("release verification failed: artifact checksum mismatch")

    try:
        verify_runtime(args.base_url)
    except (OSError, ValueError, RuntimeError, urllib.error.URLError) as exc:
        raise SystemExit(f"release verification failed: runtime check: {exc}") from exc

    print("release verification passed: artifact integrity + runtime behavior")


if __name__ == "__main__":
    main()
