"""Offline verification of pinned publisher evidence snapshots.

The snapshots are human-reviewed evidence captured from immutable official
publisher records. They let ordinary CI verify internal consistency without
making repository correctness depend on publisher uptime.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .acquisition import load_acquisition_registry
from .source_policy import load_dataset_certification


SNAPSHOT_SCHEMA = "echo.publisher-snapshot.v1"


def load_snapshot(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema_version") != SNAPSHOT_SCHEMA:
        raise ValueError(f"unsupported publisher snapshot schema: {path}")
    if not isinstance(payload.get("files"), list) or not payload["files"]:
        raise ValueError(f"publisher snapshot has no files: {path}")
    return payload


def _file_map(rows: object, *, source: str) -> dict[str, str]:
    if not isinstance(rows, list):
        raise ValueError(f"file inventory must be a list: {source}")
    result: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError(f"file inventory row must be an object: {source}")
        name = str(row.get("name") or "")
        digest = str(row.get("md5") or "").lower()
        if not name or len(digest) != 32 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError(f"invalid publisher file identity in {source}: {name!r}")
        if name in result:
            raise ValueError(f"duplicate publisher filename in {source}: {name}")
        result[name] = digest
    return result


def verify_snapshot(
    *,
    source_id: str,
    snapshot: Mapping[str, Any],
    acquisition_registry: Mapping[str, Any],
    certification_policy: Mapping[str, Any],
    source_registry: Mapping[str, Any],
) -> dict[str, Any]:
    if snapshot.get("source_id") != source_id:
        raise ValueError(f"snapshot source_id mismatch: {source_id}")

    acquisition_source = acquisition_registry.get("sources", {}).get(source_id)
    certification_source = certification_policy.get("sources", {}).get(source_id)
    registry_sources = source_registry.get("sources", [])
    registry_source = next(
        (row for row in registry_sources if isinstance(row, Mapping) and row.get("source_id") == source_id),
        None,
    )
    if not isinstance(acquisition_source, Mapping):
        raise ValueError(f"source missing from acquisition registry: {source_id}")
    if not isinstance(certification_source, Mapping):
        raise ValueError(f"source missing from certification policy: {source_id}")
    if not isinstance(registry_source, Mapping):
        raise ValueError(f"source missing from source registry: {source_id}")

    expected_url = str(acquisition_source.get("record_url") or "")
    if str(snapshot.get("record_url") or "") != expected_url:
        raise ValueError(f"publisher record URL drift for {source_id}")
    if str(registry_source.get("canonical_url") or "") != expected_url:
        raise ValueError(f"source registry URL drift for {source_id}")

    expected_release = str(certification_source.get("release") or "").lower().removeprefix("v")
    snapshot_release = str(snapshot.get("release") or "").lower().removeprefix("v")
    registry_release = str(registry_source.get("release") or "").lower().removeprefix("v")
    if snapshot_release != expected_release:
        raise ValueError(f"snapshot release drift for {source_id}: {snapshot_release} != {expected_release}")
    if registry_release != expected_release and source_id != "singapura-v1.0a":
        raise ValueError(f"source registry release drift for {source_id}: {registry_release} != {expected_release}")
    if source_id == "singapura-v1.0a" and "1.0a" not in registry_release:
        raise ValueError("SINGA:PURA source registry is not pinned to v1.0a")

    expected_license = str(registry_source.get("dataset_license") or "")
    snapshot_license = str(snapshot.get("dataset_license") or "")
    if expected_license != snapshot_license:
        raise ValueError(f"dataset license drift for {source_id}: {snapshot_license} != {expected_license}")

    snapshot_files = _file_map(snapshot.get("files"), source=f"snapshot:{source_id}")
    registry_files = _file_map(acquisition_source.get("files"), source=f"acquisition:{source_id}")
    if snapshot_files != registry_files:
        missing = sorted(set(snapshot_files) - set(registry_files))
        unexpected = sorted(set(registry_files) - set(snapshot_files))
        checksum_drift = sorted(
            name for name in set(snapshot_files) & set(registry_files)
            if snapshot_files[name] != registry_files[name]
        )
        raise ValueError(
            f"publisher inventory drift for {source_id}: "
            f"snapshot_only={missing}, registry_only={unexpected}, checksum_drift={checksum_drift}"
        )

    return {
        "schema_version": "echo.publisher-snapshot-verification.v1",
        "source_id": source_id,
        "record_id": str(snapshot.get("record_id") or ""),
        "record_url": expected_url,
        "release": snapshot.get("release"),
        "dataset_license": snapshot_license,
        "file_count": len(snapshot_files),
        "status": "PASS",
        "scope": "pinned_official_publisher_metadata_not_local_media_bytes",
    }


def verify_snapshot_from_files(
    *,
    source_id: str,
    snapshot_path: str | Path,
    acquisition_registry_path: str | Path = "configs/data_foundry/acquisition_registry.v1.json",
    certification_path: str | Path = "configs/data_foundry/dataset_certification.v1.json",
    source_registry_path: str | Path = "configs/data_foundry/source_registry.v1.json",
) -> dict[str, Any]:
    snapshot = load_snapshot(snapshot_path)
    acquisition = load_acquisition_registry(acquisition_registry_path)
    certification = load_dataset_certification(certification_path)
    with Path(source_registry_path).open("r", encoding="utf-8") as handle:
        source_registry = json.load(handle)
    return verify_snapshot(
        source_id=source_id,
        snapshot=snapshot,
        acquisition_registry=acquisition,
        certification_policy=certification,
        source_registry=source_registry,
    )
