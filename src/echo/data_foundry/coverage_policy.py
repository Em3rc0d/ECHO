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


def _duplicate_group_count(rows: list[dict[str, Any]], key_getter) -> int:
    counts: Counter[str] = Counter()
    for row in rows:
        key = key_getter(row)
        if key:
            counts[str(key)] += 1
    return sum(1 for count in counts.values() if count > 1)


def evaluate_coverage(
    rows: Iterable[Mapping[str, Any]],
    *,
    policy: Mapping[str, Any],
    profile: str,
) -> dict[str, Any]:
    """Evaluate admitted rows against the versioned corpus-solidity floor.

    The gate is intentionally conservative. Field-holdout rows are excluded
    from development coverage, explicit confuser mappings are required for
    hard-negative credit, and duplicate/technical-quality failures prevent a
    corpus from using repeated or unverified media to satisfy numeric floors.
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
    confuser_assets: Counter[str] = Counter()
    confuser_groups: dict[str, set[str]] = defaultdict(set)
    confuser_sources: dict[str, set[str]] = defaultdict(set)

    missing_probe: list[str] = []
    missing_duration: list[str] = []
    unknown_license: list[str] = []
    missing_label_provenance: list[str] = []

    for row in development:
        asset_id = str(row.get("asset_id") or "")
        labels = tuple(str(v) for v in (row.get("echo_labels") or []))
        source = str(row.get("source_dataset") or "UNKNOWN")
        group = str(row.get("recording_group_id") or "")
        split = str(row.get("echo_split") or "")
        duration = float(row.get("duration_seconds") or 0.0)
        license_id = str(row.get("license_id") or "UNKNOWN").strip().upper()
        label_provenance = str(row.get("label_provenance") or "").strip()
        extra = row.get("extra") if isinstance(row.get("extra"), Mapping) else {}
        probe = extra.get("audio_probe") if isinstance(extra, Mapping) else None

        if not isinstance(probe, Mapping) or probe.get("ok") is not True:
            missing_probe.append(asset_id)
        if duration <= 0:
            missing_duration.append(asset_id)
        if license_id in {"", "UNKNOWN", "NONE", "NULL"}:
            unknown_license.append(asset_id)
        if not label_provenance:
            missing_label_provenance.append(asset_id)

        if not labels:
            negative_assets += 1
            if group:
                negative_groups.add(group)
            negative_sources.add(source)
            confuses = extra.get("confuses", ()) if isinstance(extra, Mapping) else ()
            if isinstance(confuses, (list, tuple, set)):
                for target in {str(value) for value in confuses} & set(TARGET_LABELS):
                    confuser_assets[target] += 1
                    if group:
                        confuser_groups[target].add(group)
                    confuser_sources[target].add(source)

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
        ("BACKGROUND_ASSETS_BELOW_MIN", negative_assets, int(background.get("min_assets", 0))),
        ("BACKGROUND_GROUPS_BELOW_MIN", len(negative_groups), int(background.get("min_independent_groups", 0))),
        ("BACKGROUND_SOURCES_BELOW_MIN", len(negative_sources), int(background.get("min_sources", 0))),
    )
    for code, actual, minimum in background_checks:
        if actual < minimum:
            failures.append({"code": code, "actual": actual, "required": minimum})

    hard_negative_cfg = (cfg.get("hard_negatives") or {}).get("per_target", {})
    for label in TARGET_LABELS:
        req = hard_negative_cfg.get(label, {})
        checks = (
            ("HARD_NEGATIVE_ASSETS", confuser_assets[label], int(req.get("min_assets", 0))),
            ("HARD_NEGATIVE_GROUPS", len(confuser_groups[label]), int(req.get("min_independent_groups", 0))),
            ("HARD_NEGATIVE_SOURCES", len(confuser_sources[label]), int(req.get("min_sources", 0))),
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

    quality = cfg.get("asset_quality") or {}
    quality_checks = (
        ("ASSETS_WITHOUT_VALID_AUDIO_PROBE", len(missing_probe), 0, bool(quality.get("require_audio_probe_ok", False)), missing_probe),
        ("ASSETS_WITHOUT_POSITIVE_DURATION", len(missing_duration), 0, bool(quality.get("require_positive_duration", False)), missing_duration),
        ("ASSETS_WITH_UNKNOWN_LICENSE", len(unknown_license), 0, bool(quality.get("require_known_license", False)), unknown_license),
        ("ASSETS_WITHOUT_LABEL_PROVENANCE", len(missing_label_provenance), 0, bool(quality.get("require_label_provenance", False)), missing_label_provenance),
    )
    for code, actual, required, enabled, asset_ids in quality_checks:
        if enabled and actual > required:
            failures.append(
                {
                    "code": code,
                    "actual": actual,
                    "required": required,
                    "sample_asset_ids": asset_ids[:20],
                }
            )

    exact_duplicate_groups = _duplicate_group_count(
        development, key_getter=lambda row: row.get("sha256")
    )

    def _near(row: Mapping[str, Any]) -> str | None:
        extra = row.get("extra")
        if isinstance(extra, Mapping):
            value = extra.get("near_duplicate_fingerprint")
            return str(value) if value else None
        return None

    near_duplicate_groups = _duplicate_group_count(development, key_getter=_near)
    max_exact = int(quality.get("max_exact_duplicate_groups", exact_duplicate_groups))
    max_near = int(quality.get("max_near_duplicate_groups", near_duplicate_groups))
    if exact_duplicate_groups > max_exact:
        failures.append(
            {
                "code": "EXACT_DUPLICATE_GROUPS_ABOVE_MAX",
                "actual": exact_duplicate_groups,
                "required_max": max_exact,
            }
        )
    if near_duplicate_groups > max_near:
        failures.append(
            {
                "code": "NEAR_DUPLICATE_GROUPS_ABOVE_MAX",
                "actual": near_duplicate_groups,
                "required_max": max_near,
            }
        )

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
            "hard_negatives": {
                "asset_count": confuser_assets[label],
                "independent_group_count": len(confuser_groups[label]),
                "source_count": len(confuser_sources[label]),
                "sources": sorted(confuser_sources[label]),
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
        "asset_quality": {
            "assets_without_valid_audio_probe": len(missing_probe),
            "assets_without_positive_duration": len(missing_duration),
            "assets_with_unknown_license": len(unknown_license),
            "assets_without_label_provenance": len(missing_label_provenance),
            "exact_duplicate_groups": exact_duplicate_groups,
            "near_duplicate_groups": near_duplicate_groups,
        },
        "failures": failures,
        "gap_codes": sorted({str(item["code"]) for item in failures}),
    }
