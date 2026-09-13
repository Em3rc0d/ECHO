"""Coverage and quarantine reports for ECHO Data Foundry."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping

from .contracts import TARGET_LABELS


def coverage_report(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    materialized = [dict(row) for row in rows]
    by_status: Counter[str] = Counter()
    by_source: Counter[str] = Counter()
    by_license: Counter[str] = Counter()
    by_split: Counter[str] = Counter()
    by_class_assets: Counter[str] = Counter()
    by_class_groups: dict[str, set[str]] = defaultdict(set)
    by_class_duration: Counter[str] = Counter()
    total_duration = 0.0

    for row in materialized:
        by_status[str(row.get("admission_status") or "UNKNOWN")] += 1
        by_source[str(row.get("source_dataset") or "UNKNOWN")] += 1
        by_license[str(row.get("license_id") or "UNKNOWN")] += 1
        if row.get("echo_split"):
            by_split[str(row["echo_split"])] += 1
        duration = float(row.get("duration_seconds") or 0.0)
        if duration > 0:
            total_duration += duration
        group = str(row.get("recording_group_id") or "")
        for label in row.get("echo_labels", []) or []:
            label = str(label)
            by_class_assets[label] += 1
            if group:
                by_class_groups[label].add(group)
            if duration > 0:
                by_class_duration[label] += duration

    classes = {}
    for label in TARGET_LABELS:
        classes[label] = {
            "asset_count": by_class_assets[label],
            "independent_group_count": len(by_class_groups[label]),
            "duration_seconds": round(by_class_duration[label], 6),
        }

    return {
        "schema_version": "echo.coverage-report.v1",
        "asset_count": len(materialized),
        "total_duration_seconds": round(total_duration, 6),
        "by_admission_status": dict(sorted(by_status.items())),
        "by_source": dict(sorted(by_source.items())),
        "by_license": dict(sorted(by_license.items())),
        "by_split": dict(sorted(by_split.items())),
        "classes": classes,
        "coverage_gaps": [label for label in TARGET_LABELS if by_class_assets[label] == 0],
    }


def quarantine_report(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    materialized = [dict(row) for row in rows]
    quarantined = []
    rejected = []
    reason_counts: Counter[str] = Counter()
    for row in materialized:
        status = str(row.get("admission_status") or "")
        if status not in {"QUARANTINED", "REJECTED"}:
            continue
        summary = {
            "asset_id": row.get("asset_id"),
            "source_dataset": row.get("source_dataset"),
            "license_id": row.get("license_id"),
            "original_labels": row.get("original_labels", []),
            "echo_labels": row.get("echo_labels", []),
            "reason_codes": row.get("reason_codes", []),
        }
        for reason in row.get("reason_codes", []) or []:
            reason_counts[str(reason)] += 1
        (quarantined if status == "QUARANTINED" else rejected).append(summary)
    return {
        "schema_version": "echo.quarantine-report.v1",
        "quarantined_count": len(quarantined),
        "rejected_count": len(rejected),
        "reason_counts": dict(sorted(reason_counts.items())),
        "quarantined": sorted(quarantined, key=lambda row: str(row.get("asset_id"))),
        "rejected": sorted(rejected, key=lambda row: str(row.get("asset_id"))),
    }
