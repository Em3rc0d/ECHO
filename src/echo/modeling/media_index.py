"""Portable resolver for ECHO MVP content-addressed media indexes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_media_index(path: str | Path) -> dict[str, str]:
    """Load a COMPLETE media index and resolve entries on the current machine.

    Older ECHO indexes stored absolute host paths. If such a path is unavailable
    (for example after mounting the corpus into Docker), resolution falls back
    to the content-addressed objects directory beside the index.
    """
    index_path = Path(path).resolve()
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    if payload.get("status") != "COMPLETE":
        raise ValueError(
            f"media index is not COMPLETE: missing={payload.get('missing_sha256_count')}"
        )

    raw = payload.get("by_sha256")
    if not isinstance(raw, dict):
        raise ValueError("media index missing by_sha256")

    object_dir = index_path.parent / "objects"
    resolved: dict[str, str] = {}

    for digest, stored in raw.items():
        digest = str(digest)
        if len(digest) != 64:
            raise ValueError(f"invalid media SHA-256 key: {digest!r}")

        stored_path = Path(str(stored))
        candidates: list[Path] = []

        if stored_path.is_file():
            candidates.append(stored_path)

        if not stored_path.is_absolute():
            relative = index_path.parent / stored_path
            if relative.is_file():
                candidates.append(relative)

        candidates.extend(
            candidate
            for candidate in sorted(object_dir.glob(f"{digest}.*"))
            if candidate.is_file()
        )

        unique: list[Path] = []
        seen: set[str] = set()
        for candidate in candidates:
            key = str(candidate.resolve())
            if key not in seen:
                unique.append(candidate.resolve())
                seen.add(key)

        valid = [candidate for candidate in unique if _sha256_file(candidate) == digest]
        if len(valid) != 1:
            raise ValueError(
                f"media {digest}: expected exactly one SHA-valid local object, "
                f"found {len(valid)}"
            )
        resolved[digest] = str(valid[0])

    return resolved
