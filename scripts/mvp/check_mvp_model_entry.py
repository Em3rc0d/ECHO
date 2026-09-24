#!/usr/bin/env python3
"""Fail-closed model-entry gate for the first ECHO MVP.

This gate does not weaken or replace the full `release_safe` corpus gate.
It authorizes model work only for the explicitly selected MVP classes when
their own coverage, splits, diversity, hard-negative, quality and structural
requirements already pass.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MATERIALIZATION = ROOT / "MK1/mining-site/materialization"

DEFAULT_CONFIG = ROOT / "configs/mvp/mk1.v1.json"
DEFAULT_COVERAGE = MATERIALIZATION / "coverage-gate.json"
DEFAULT_POLICY = ROOT / "configs/data_foundry/coverage_policy.v1.json"
DEFAULT_LEDGER = MATERIALIZATION / "canonical-release-safe-asset-ledger-summary.json"
DEFAULT_OUTPUT = MATERIALIZATION / "mvp-model-entry-readiness.json"

STRUCTURAL_EVIDENCE = {
    "global_dedup_audit": "global-dedup-audit.json",
    "recording_family_audit": "recording-family-audit.json",
    "split_integrity": "split-integrity.json",
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def artifact_pass(payload: dict[str, Any]) -> bool:
    status = str(payload.get("status", "")).upper()
    return status in {"PASS", "CERTIFIED", "IDENTICAL"} and payload.get("gap_codes") in (None, [])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--coverage-policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--ledger-summary", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    config = load_json(args.config)
    coverage = load_json(args.coverage)
    policy = load_json(args.coverage_policy)
    ledger = load_json(args.ledger_summary)

    profile_id = str(config.get("profile_id") or "")
    targets = [str(x) for x in config.get("target_labels", [])]
    excluded = [str(x) for x in config.get("excluded_target_labels", [])]

    gaps: list[str] = []

    if not profile_id:
        gaps.append("MVP_PROFILE_ID_MISSING")
    if not targets:
        gaps.append("MVP_TARGETS_EMPTY")
    if set(targets) & set(excluded):
        gaps.append("MVP_TARGET_EXCLUSION_OVERLAP")

    release_profile = policy.get("profiles", {}).get("release_safe", {})
    target_policy = release_profile.get("target_labels", {})
    hn_policy = release_profile.get("hard_negatives", {}).get("per_target", {})
    split_policy = release_profile.get("per_split", {})
    max_source_fraction = float(
        release_profile.get("max_single_source_fraction_per_class", 1.0)
    )

    for target in targets:
        if target not in target_policy:
            gaps.append(f"{target}_NOT_IN_RELEASE_SAFE_POLICY")

    structural: dict[str, Any] = {}
    for node, filename in STRUCTURAL_EVIDENCE.items():
        path = MATERIALIZATION / filename
        if not path.is_file():
            gaps.append(f"{node.upper()}_MISSING")
            structural[node] = {"status": "MISSING", "pass": False}
            continue
        payload = load_json(path)
        passed = artifact_pass(payload)
        structural[node] = {"status": payload.get("status"), "pass": passed}
        if not passed:
            gaps.append(f"{node.upper()}_NOT_PASS")

    blockers = ledger.get("blocking_reason_counts")
    if isinstance(blockers, dict):
        active_blockers = {
            str(k): int(v) for k, v in blockers.items() if int(v) > 0
        }
    else:
        active_blockers = {}
    if active_blockers:
        gaps.append("LEDGER_BLOCKERS_PRESENT")

    missing_fingerprints = int(
        ledger.get("canonical_fingerprint_missing_count", 0) or 0
    )
    if missing_fingerprints:
        gaps.append("CANONICAL_FINGERPRINT_COVERAGE_INCOMPLETE")

    asset_quality = coverage.get("asset_quality", {})
    quality_zero_fields = (
        "assets_with_unknown_license",
        "assets_without_label_provenance",
        "assets_without_positive_duration",
        "assets_without_valid_audio_probe",
        "exact_duplicate_groups",
        "near_duplicate_groups",
    )
    for field in quality_zero_fields:
        value = int(asset_quality.get(field, 0) or 0)
        if value != 0:
            gaps.append(f"ASSET_QUALITY_{field.upper()}_{value}")

    background = coverage.get("background", {})
    background_policy = release_profile.get("background", {})
    if int(background.get("asset_count", 0) or 0) < int(
        background_policy.get("min_assets", 0) or 0
    ):
        gaps.append("BACKGROUND_ASSETS_BELOW_MIN")
    if int(background.get("independent_group_count", 0) or 0) < int(
        background_policy.get("min_independent_groups", 0) or 0
    ):
        gaps.append("BACKGROUND_GROUPS_BELOW_MIN")
    if int(background.get("source_count", 0) or 0) < int(
        background_policy.get("min_sources", 0) or 0
    ):
        gaps.append("BACKGROUND_SOURCES_BELOW_MIN")

    classes = coverage.get("classes", {})
    target_readiness: dict[str, Any] = {}
    for target in targets:
        row = classes.get(target, {})
        req = target_policy.get(target, {})
        hn_req = hn_policy.get(target, {})
        target_gaps: list[str] = []

        checks = (
            (
                "ASSETS",
                int(row.get("asset_count", 0) or 0),
                int(req.get("min_assets", 0) or 0),
            ),
            (
                "GROUPS",
                int(row.get("independent_group_count", 0) or 0),
                int(req.get("min_independent_groups", 0) or 0),
            ),
            (
                "SOURCES",
                int(row.get("source_count", 0) or 0),
                int(req.get("min_sources", 0) or 0),
            ),
        )
        for metric, actual, required in checks:
            if actual < required:
                target_gaps.append(f"{target}_{metric}_{actual}_LT_{required}")

        duration = float(row.get("clip_duration_seconds", 0.0) or 0.0)
        min_duration = float(req.get("min_clip_duration_seconds", 0.0) or 0.0)
        if duration < min_duration:
            target_gaps.append(f"{target}_DURATION_{duration}_LT_{min_duration}")

        concentration = float(
            row.get("max_single_source_fraction", 1.0) or 0.0
        )
        if concentration > max_source_fraction:
            target_gaps.append(
                f"{target}_SOURCE_CONCENTRATION_{concentration}_GT_{max_source_fraction}"
            )

        split_assets = row.get("split_assets", {})
        split_groups = row.get("split_groups", {})
        for split_name, split_req in split_policy.items():
            assets = int(split_assets.get(split_name, 0) or 0)
            groups = int(split_groups.get(split_name, 0) or 0)
            min_assets = int(split_req.get("min_assets_per_class", 0) or 0)
            min_groups = int(split_req.get("min_groups_per_class", 0) or 0)
            if assets < min_assets:
                target_gaps.append(
                    f"{target}_{split_name.upper()}_ASSETS_{assets}_LT_{min_assets}"
                )
            if groups < min_groups:
                target_gaps.append(
                    f"{target}_{split_name.upper()}_GROUPS_{groups}_LT_{min_groups}"
                )

        hn = row.get("hard_negatives", {})
        hn_checks = (
            (
                "HARD_NEGATIVE_ASSETS",
                int(hn.get("asset_count", 0) or 0),
                int(hn_req.get("min_assets", 0) or 0),
            ),
            (
                "HARD_NEGATIVE_GROUPS",
                int(hn.get("independent_group_count", 0) or 0),
                int(hn_req.get("min_independent_groups", 0) or 0),
            ),
            (
                "HARD_NEGATIVE_SOURCES",
                int(hn.get("source_count", 0) or 0),
                int(hn_req.get("min_sources", 0) or 0),
            ),
        )
        for metric, actual, required in hn_checks:
            if actual < required:
                target_gaps.append(f"{target}_{metric}_{actual}_LT_{required}")

        gaps.extend(target_gaps)
        target_readiness[target] = {
            "status": "PASS" if not target_gaps else "FAIL",
            "asset_count": row.get("asset_count"),
            "independent_group_count": row.get("independent_group_count"),
            "source_count": row.get("source_count"),
            "clip_duration_seconds": row.get("clip_duration_seconds"),
            "max_single_source_fraction": row.get("max_single_source_fraction"),
            "split_assets": split_assets,
            "split_groups": split_groups,
            "hard_negatives": hn,
            "gap_codes": target_gaps,
        }

    gaps = sorted(dict.fromkeys(gaps))
    ready = not gaps

    result = {
        "schema_version": "echo.mvp-model-entry-readiness.v1",
        "profile_id": profile_id,
        "status": "READY" if ready else "BLOCKED",
        "mvp_modeling_allowed": ready,
        "source_profile": config.get("source_profile"),
        "target_labels": targets,
        "excluded_target_labels": excluded,
        "excluded_target_behavior": config.get("excluded_target_behavior"),
        "full_release_gate_unchanged": True,
        "full_release_coverage_status": coverage.get("status"),
        "full_release_gap_codes": coverage.get("gap_codes", []),
        "ledger_blocking_reason_counts": active_blockers,
        "canonical_fingerprint_missing_count": missing_fingerprints,
        "structural_evidence": structural,
        "asset_quality": asset_quality,
        "background": background,
        "target_readiness": target_readiness,
        "gap_codes": gaps,
        "next_authorized_stage": (
            "MVP_BENCHMARK_A_B_C" if ready else "MVP_DATA_CLOSURE"
        ),
    }

    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")

    if args.stdout:
        print(encoded, end="")
    else:
        print(profile_id, result["status"])
        print("mvp_modeling_allowed:", ready)
        print("targets:", ", ".join(targets))
        print("gap_codes:", len(gaps))
        for gap in gaps:
            print(" -", gap)

    if args.require_ready and not ready:
        print("MVP MODEL ENTRY GATE: BLOCKED")
        return 3
    if args.require_ready:
        print("MVP MODEL ENTRY GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
