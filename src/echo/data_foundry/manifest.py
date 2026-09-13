"""Canonical manifest generation for ECHO Data Foundry evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .contracts import AssetRecord
from .hashing import canonical_json_bytes, canonical_json_sha256


def canonical_asset_rows(records: Iterable[AssetRecord | Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        if isinstance(record, AssetRecord):
            row = record.to_dict()
        else:
            row = dict(record)
        if not row.get("asset_id"):
            raise ValueError("asset row requires asset_id")
        rows.append(row)
    rows.sort(key=lambda item: str(item["asset_id"]))
    return rows


def asset_manifest_text(records: Iterable[AssetRecord | Mapping[str, Any]]) -> str:
    rows = canonical_asset_rows(records)
    # One canonical JSON object per line; stable sort makes digest input-order invariant.
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
        for row in rows
    )


def asset_manifest_sha256(records: Iterable[AssetRecord | Mapping[str, Any]]) -> str:
    return hashlib.sha256(asset_manifest_text(records).encode("utf-8")).hexdigest()


def write_asset_manifest(path: str | Path, records: Iterable[AssetRecord | Mapping[str, Any]]) -> str:
    text = asset_manifest_text(records)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_dataset_manifest(
    *,
    manifest_id: str,
    profile: str,
    taxonomy_version: str,
    records: Sequence[AssetRecord | Mapping[str, Any]],
    source_registry_sha256: str,
    license_policy_sha256: str,
    label_mapping_sha256: str,
    split_policy_sha256: str,
    split_manifest_sha256: str | None = None,
    known_gaps: Sequence[str] = (),
    reports: Mapping[str, str] | None = None,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    if profile not in {"release_safe", "research_extended", "field_holdout"}:
        raise ValueError(f"unsupported dataset profile: {profile}")
    rows = canonical_asset_rows(records)
    source_releases = sorted(
        {
            f"{row.get('source_dataset')}@{row.get('source_release')}"
            for row in rows
            if row.get("source_dataset") and row.get("source_release")
        }
    )
    timestamp = created_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest = {
        "schema_version": "echo.dataset-manifest.v1",
        "manifest_id": manifest_id,
        "created_at_utc": timestamp,
        "taxonomy_version": taxonomy_version,
        "profile": profile,
        "source_registry_sha256": source_registry_sha256,
        "license_policy_sha256": license_policy_sha256,
        "label_mapping_sha256": label_mapping_sha256,
        "split_policy_sha256": split_policy_sha256,
        "asset_manifest_sha256": asset_manifest_sha256(rows),
        "split_manifest_sha256": split_manifest_sha256,
        "asset_count": len(rows),
        "source_releases": source_releases,
        "known_gaps": sorted(set(known_gaps)),
        "reports": dict(sorted((reports or {}).items())),
    }
    return manifest


def dataset_manifest_digest(manifest: Mapping[str, Any]) -> str:
    """Digest a dataset manifest exactly as represented, including timestamp.

    The benchmark should primarily bind to the asset/split/policy hashes inside
    the record. This digest additionally identifies the complete manifest file.
    """

    return canonical_json_sha256(dict(manifest))


def write_json(path: str | Path, payload: Mapping[str, Any]) -> str:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    output.write_text(text, encoding="utf-8")
    return canonical_json_sha256(dict(payload))
