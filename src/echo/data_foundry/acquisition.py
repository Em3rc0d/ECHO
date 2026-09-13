"""Publisher-bundle acquisition verification for ECHO Data Foundry.

This module deliberately verifies already acquired files; it does not silently
download multi-gigabyte datasets.  Acquisition is explicit so license/terms,
disk planning and source provenance stay visible to the operator.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


_CHUNK = 1024 * 1024


@dataclass(frozen=True)
class FileVerification:
    name: str
    required: bool
    present: bool
    checksum_expected: str | None
    checksum_actual: str | None
    checksum_ok: bool | None
    size_bytes: int | None

    @property
    def ok(self) -> bool:
        if not self.required:
            return True
        if not self.present:
            return False
        return self.checksum_ok is not False


def md5_file(path: str | Path) -> str:
    """Compute publisher-compatible MD5 for release-bundle verification only.

    ECHO does not use MD5 as the admitted asset identity; local audio identity
    is SHA-256 in the main Foundry pipeline.
    """

    digest = hashlib.md5(usedforsecurity=False)
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_acquisition_registry(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema_version") != "echo.acquisition-registry.v1":
        raise ValueError("unsupported acquisition registry schema")
    sources = payload.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("acquisition registry requires sources object")
    return payload


def files_for_stage(source: Mapping[str, Any], stage: str) -> list[Mapping[str, Any]]:
    if stage not in {"metadata", "full"}:
        raise ValueError("stage must be 'metadata' or 'full'")
    rows = []
    for entry in source.get("files", []):
        required_for = entry.get("required_for", [])
        if stage in required_for:
            rows.append(entry)
    return rows


def verify_source_release(
    *,
    registry: Mapping[str, Any],
    source_id: str,
    root: str | Path,
    stage: str,
) -> list[FileVerification]:
    sources = registry.get("sources", {})
    if source_id not in sources:
        raise KeyError(f"unknown acquisition source: {source_id}")
    source = sources[source_id]
    base = Path(root)
    required_entries = files_for_stage(source, stage)
    results: list[FileVerification] = []

    for entry in required_entries:
        name = str(entry["name"])
        path = base / name
        expected = str(entry.get("md5") or "").lower() or None
        if not path.is_file():
            results.append(
                FileVerification(
                    name=name,
                    required=True,
                    present=False,
                    checksum_expected=expected,
                    checksum_actual=None,
                    checksum_ok=None,
                    size_bytes=None,
                )
            )
            continue
        actual = md5_file(path) if expected else None
        results.append(
            FileVerification(
                name=name,
                required=True,
                present=True,
                checksum_expected=expected,
                checksum_actual=actual,
                checksum_ok=(actual == expected) if expected else None,
                size_bytes=path.stat().st_size,
            )
        )
    return results


def verification_summary(results: Iterable[FileVerification]) -> dict[str, Any]:
    rows = list(results)
    missing = [row.name for row in rows if row.required and not row.present]
    checksum_failed = [
        row.name for row in rows if row.required and row.present and row.checksum_ok is False
    ]
    return {
        "required_files": len(rows),
        "present_files": sum(1 for row in rows if row.present),
        "missing_files": missing,
        "checksum_failed": checksum_failed,
        "status": "PASS" if not missing and not checksum_failed else "FAIL",
    }
