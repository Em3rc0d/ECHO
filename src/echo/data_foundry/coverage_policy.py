"""Fail-closed corpus coverage policy for ECHO Data Foundry."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .contracts import TARGET_LABELS


def load_coverage_policy(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema_version") != "echo.coverage-policy.v1":
        raise ValueError("unsupported coverage policy schema")
    profiles = payload.get("profiles")
    if not isinstance(profiles, Mapping) or not profiles:
        raise ValueError("coverage policy requires profiles")
    return payload


def _profile(policy: Mapping[str, Any], profile: str) -> Mapping[str, Any]:
    profiles = policy.get("profiles", {})
    row = profiles.get(profile) if isinstance(profiles, Mapping) else None
    if not isinstance(row, Mapping):
        raise ValueError(f"coverage policy has no profile {profile!r}")
    return row


def evaluate_coverage(
    rows: Iterable[Mapping[str, Any]],
    *,
    policy: Mapping[str, Any],
    profile: str,
) -> dict[str, Any]:
    """Evaluate real admitted rows against the versioned corpus-solidity floor.

    Field-holdout rows are intentionally excluded from development coverage so
    an untouched evaluation set can never be used to hide a training gap.
    """
    cfg = _profile(policy, profile)
    materialized = [dict(row) for row in rows]
    development = [
        row
        for row in materialized
        if not bool(row.get("field_holdout"))
        and row.get("echo_split") != "field_holdout"
    ]

    class_assets: Counter[str] = Counter()
    class_duration: Counter[str] = Counter()
    class_groups: dict[str, set[str]] = defaultdict(set)
    class_sources: dict[str, set[str]] = defaultdict(set)
    class_source_assets: dict[str, Counter[str]] = defaultdict(Counter)
    split_assets: dict[str, Counter[str]] = defaultdict(Counter)
    split_groups: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )

    negative_assets = 0
    negative_groups: set[str] = set()
    negative_sources: set[str] = set()

    for row in development:
        labels = tuple(str(v) for v in (row.get("echo_labels") or []))
        source = str(row.get("source_dataset") or "UNKNOWN")
        group = str(row.get("recording_group_id") or "")
        split = str(row.get("echo_split") or "")
        duration = float(row.get("duration_seconds") or 0.0)

        if not labels:
            negative_assets += 1
            if group:
                negative_groups.add(group)
            negative_sources.add(source)

        for label in labels:
            if label not in TARGET_LABELS:
                continue
            class_assets[label] += 1
            class_sources[label].add(source)
            class_source_assets[label][source] += 1
            if group:
                class_groups[label].add(group)
            if duration > 0:
                class_duration[label] += duration
            if split:
                split_assets[split][label] += 1
                if group:
                    split_groups[split][label].add(group)

    failures: list[dict[str, Any]] = []
    target_cfg = cfg.get("target_labels", {})
    for label in TARGET_LABELS:
        req = target_cfg.get(label, {})
        assets = class_assets[label]
        groups = len(class_groups[label])
        sources = len(class_sources[label])
        duration = float(class_duration[label])

        checks = (
            ("ASSETS", assets, int(req.get("min_assets", 1))),
            ("GROUPS", groups, int(req.get("min_independent_groups", 1))),
            ("SOURCES", sources, int(req.get("min_sources", 1))),
            (
                "DURATION_SECONDS",
                duration,
                float(req.get("min_clip_duration_seconds", 0.0)),
            ),
        )
        for metric, actual, minimum in checks:
            if actual < minimum:
                failures.append(
                    {
                        "code": f"{label}_{metric}_BELOW_MIN",
                        "label": label,
                        "metric": metric,
                        "actual": actual,
                        "required": minimum,
                    }
                )

        max_fraction = float(
            cfg.get("max_single_source_fraction_per_class", 1.0)
        )
        if assets > 0 and class_source_assets[label]:
            largest = max(class_source_assets[label].values())
            fraction = largest / assets
            if fraction > max_fraction:
                failures.append(
                    {
                        "code": f"{label}_SOURCE_CONCENTRATION_TOO_HIGH",
                        "label": label,
                        "metric": "MAX_SINGLE_SOURCE_FRACTION",
                        "actual": round(fraction, 6),
                        "required_max": max_fraction,
                    }
                )

    for split, req in (cfg.get("per_split") or {}).items():
        min_assets = int(req.get("min_assets_per_class", 0))
        min_groups = int(req.get("min_groups_per_class", 0))
        for label in TARGET_LABELS:
            assets = split_assets[str(split)][label]
            groups = len(split_groups[str(split)][label])
            if assets < min_assets:
                failures.append(
                    {
                        "code": f"{label}_{str(split).upper()}_ASSETS_BELOW_MIN",
                        "label": label,
                        "split": split,
                        "metric": "ASSETS",
                        "actual": assets,
                        "required": min_assets,
                    }
                )
            if groups < min_groups:
                failures.append(
                    {
                        "code": f"{label}_{str(split).upper()}_GROUPS_BELOW_MIN",
                        "label": label,
                        "split": split,
                        "metric": "GROUPS",
                        "actual": groups,
                        "required": min_groups,
                    }
                )

    background = cfg.get("background") or {}
    background_checks = (
        (
            "BACKGROUND_ASSETS_BELOW_MIN",
            negative_assets,
            int(background.get("min_assets", 0)),
        ),
        (
            "BACKGROUND_GROUPS_BELOW_MIN",
            len(negative_groups),
            int(background.get("min_independent_groups", 0)),
        ),
        (
            "BACKGROUND_SOURCES_BELOW_MIN",
            len(negative_sources),
            int(background.get("min_sources", 0)),
        ),
    )
    for code, actual, minimum in background_checks:
        if actual < minimum:
            failures.append({"code": code, "actual": actual, "required": minimum})

    class_summary = {}
    for label in TARGET_LABELS:
        assets = class_assets[label]
        source_counts = dict(sorted(class_source_assets[label].items()))
        class_summary[label] = {
            "asset_count": assets,
            "independent_group_count": len(class_groups[label]),
            "source_count": len(class_sources[label]),
            "sources": sorted(class_sources[label]),
            "source_asset_counts": source_counts,
            "max_single_source_fraction": (
                round(max(source_counts.values()) / assets, 6)
                if assets and source_counts
                else None
            ),
            "clip_duration_seconds": round(float(class_duration[label]), 6),
            "split_assets": {
                split: split_assets[split][label]
                for split in sorted((cfg.get("per_split") or {}).keys())
            },
            "split_groups": {
                split: len(split_groups[split][label])
                for split in sorted((cfg.get("per_split") or {}).keys())
            },
        }

    return {
        "schema_version": "echo.coverage-gate.v1",
        "policy_id": policy.get("policy_id"),
        "profile": profile,
        "status": "PASS" if not failures else "FAIL",
        "development_asset_count": len(development),
        "field_holdout_excluded_count": len(materialized) - len(development),
        "classes": class_summary,
        "background": {
            "asset_count": negative_assets,
            "independent_group_count": len(negative_groups),
            "source_count": len(negative_sources),
            "sources": sorted(negative_sources),
        },
        "failures": failures,
        "gap_codes": sorted({str(item["code"]) for item in failures}),
    }
