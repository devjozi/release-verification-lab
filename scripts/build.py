#!/usr/bin/env python3
"""Build a byte-for-byte deterministic release artifact and checksum."""

from __future__ import annotations

import gzip
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


def add_deterministic(archive: tarfile.TarFile, path: Path, arcname: str) -> None:
    """Add a path with normalized archive metadata so repeated builds match."""
    if path.is_dir():
        info = archive.gettarinfo(str(path), arcname=arcname)
        info.mtime = 0
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        archive.addfile(info)
        for child in sorted(path.iterdir(), key=lambda item: item.name):
            add_deterministic(archive, child, f"{arcname}/{child.name}")
        return

    info = archive.gettarinfo(str(path), arcname=arcname)
    info.mtime = 0
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    with path.open("rb") as stream:
        archive.addfile(info, stream)


def main() -> None:
    DIST.mkdir(exist_ok=True)
    if ARTIFACT.exists():
        ARTIFACT.unlink()

    with ARTIFACT.open("wb") as output:
        with gzip.GzipFile(fileobj=output, mode="wb", compresslevel=9, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for relative in INCLUDE:
                    add_deterministic(archive, ROOT / relative, relative)

    digest = sha256(ARTIFACT)
    checksum = DIST / f"{ARTIFACT.name}.sha256"
    checksum.write_text(f"{digest}  {ARTIFACT.name}\n", encoding="utf-8")
    print(f"artifact={ARTIFACT.relative_to(ROOT)}")
    print(f"sha256={digest}")


if __name__ == "__main__":
    main()
