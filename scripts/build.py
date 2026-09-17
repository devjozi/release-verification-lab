#!/usr/bin/env python3
"""Build the inspectable release artifact and its checksum manifest."""

from __future__ import annotations

import hashlib
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
VERSION = "0.1.0"
ARTIFACT = DIST / f"release-verification-lab-{VERSION}.tar.gz"
INCLUDE = ["src", "tests", "scripts", "README.md", "ARCHITECTURE.md"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    DIST.mkdir(exist_ok=True)
    if ARTIFACT.exists():
        ARTIFACT.unlink()

    with tarfile.open(ARTIFACT, "w:gz") as archive:
        for relative in INCLUDE:
            archive.add(ROOT / relative, arcname=relative)

    digest = sha256(ARTIFACT)
    checksum = DIST / f"{ARTIFACT.name}.sha256"
    checksum.write_text(f"{digest}  {ARTIFACT.name}\n", encoding="utf-8")
    print(f"artifact={ARTIFACT.relative_to(ROOT)}")
    print(f"sha256={digest}")


if __name__ == "__main__":
    main()
