"""Duplicate and leakage audits for ECHO Data Foundry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Any


@dataclass(frozen=True)
class DuplicateFinding:
    key_type: str
    key: str
    asset_ids: tuple[str, ...]
    splits: tuple[str, ...]
    groups: tuple[str, ...]

    @property
    def crosses_splits(self) -> bool:
        return len(set(self.splits)) > 1


def _group_findings(rows: Iterable[Mapping[str, Any]], *, key_getter, key_type: str) -> list[DuplicateFinding]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        key = key_getter(row)
        if not key:
            continue
        grouped.setdefault(str(key), []).append(row)
    result: list[DuplicateFinding] = []
    for key, items in grouped.items():
        if len(items) < 2:
            continue
        result.append(DuplicateFinding(
            key_type=key_type,
            key=key,
            asset_ids=tuple(sorted(str(item.get("asset_id") or "") for item in items)),
            splits=tuple(sorted({str(item.get("echo_split") or "") for item in items if item.get("echo_split")})),
            groups=tuple(sorted({str(item.get("recording_group_id") or "") for item in items if item.get("recording_group_id")})),
        ))
    return sorted(result, key=lambda item: (item.key_type, item.key))


def find_exact_duplicates(rows: Iterable[Mapping[str, Any]]) -> list[DuplicateFinding]:
    return _group_findings(rows, key_getter=lambda row: row.get("sha256"), key_type="sha256")


def find_near_duplicate_fingerprints(rows: Iterable[Mapping[str, Any]]) -> list[DuplicateFinding]:
    def fingerprint(row: Mapping[str, Any]) -> str | None:
        extra = row.get("extra")
        if isinstance(extra, Mapping):
            value = extra.get("near_duplicate_fingerprint")
            return str(value) if value else None
        return None
    return _group_findings(rows, key_getter=fingerprint, key_type="near_duplicate_fingerprint")


def audit_group_integrity(rows: Iterable[Mapping[str, Any]]) -> None:
    seen: dict[str, str] = {}
    for row in rows:
        group = str(row.get("recording_group_id") or "")
        split = str(row.get("echo_split") or "")
        if not group or not split:
            continue
        previous = seen.get(group)
        if previous is not None and previous != split:
            raise ValueError(f"recording group {group!r} crosses splits: {previous} vs {split}")
        seen[group] = split


def audit_duplicate_leakage(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    materialized = [dict(row) for row in rows]
    audit_group_integrity(materialized)
    exact = find_exact_duplicates(materialized)
    near = find_near_duplicate_fingerprints(materialized)
    cross = [item for item in exact + near if item.crosses_splits]
    if cross:
        details = "; ".join(f"{item.key_type}:{item.key}" for item in cross[:10])
        raise ValueError(f"duplicate leakage across splits: {details}")
    return {
        "exact_duplicate_groups": len(exact),
        "near_duplicate_groups": len(near),
        "cross_split_duplicate_groups": 0,
        "exact": [item.__dict__ for item in exact],
        "near": [item.__dict__ for item in near],
    }
