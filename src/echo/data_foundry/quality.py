"""Metadata-quality and exact-duplicate checks for Foundry records."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping, Sequence

from .contracts import RawAssetCandidate


def candidate_quality_issues(candidate: RawAssetCandidate) -> tuple[str, ...]:
    issues: list[str] = []
    if not candidate.source_dataset.strip():
        issues.append("SOURCE_DATASET_MISSING")
    if not candidate.source_release.strip():
        issues.append("SOURCE_RELEASE_MISSING")
    if not candidate.source_asset_id.strip():
        issues.append("SOURCE_ASSET_ID_MISSING")
    if not candidate.recording_group_id:
        issues.append("GROUP_ID_MISSING")
    if candidate.duration_seconds is not None and candidate.duration_seconds <= 0:
        issues.append("DURATION_INVALID")
    if candidate.sample_rate_hz is not None and candidate.sample_rate_hz <= 0:
        issues.append("SAMPLE_RATE_INVALID")
    if candidate.channels is not None and candidate.channels <= 0:
        issues.append("CHANNEL_COUNT_INVALID")
    if candidate.field_holdout and candidate.original_split in {"train", "validation", "test"}:
        issues.append("FIELD_HOLDOUT_SOURCE_SPLIT_CONFLICT")
    return tuple(sorted(set(issues)))


def exact_duplicate_clusters(rows: Iterable[Mapping[str, object]]) -> dict[str, tuple[str, ...]]:
    by_hash: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        digest = str(row.get("sha256") or "")
        asset_id = str(row.get("asset_id") or "")
        if digest and asset_id:
            by_hash[digest].append(asset_id)
    return {
        digest: tuple(sorted(asset_ids))
        for digest, asset_ids in sorted(by_hash.items())
        if len(asset_ids) > 1
    }


def duplicate_label_conflicts(rows: Sequence[Mapping[str, object]]) -> dict[str, tuple[str, ...]]:
    labels_by_hash: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    assets_by_hash: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        digest = str(row.get("sha256") or "")
        if not digest:
            continue
        raw_labels = row.get("echo_labels") or []
        labels = tuple(sorted(str(value) for value in raw_labels))
        labels_by_hash[digest].add(labels)
        assets_by_hash[digest].append(str(row.get("asset_id") or ""))
    return {
        digest: tuple(sorted(asset for asset in assets_by_hash[digest] if asset))
        for digest, variants in labels_by_hash.items()
        if len(variants) > 1
    }
