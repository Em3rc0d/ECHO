#!/usr/bin/env python3
"""Build the leakage-safe benchmark manifest for ECHO-MVP-001.

This builder consumes the canonical release-safe ledger and reproduces the same
recording-group split policy used by the corpus closure pipeline.

Supervision is intentionally partial:
- selected MVP labels are explicit positives;
- canonical background (no ECHO positive label) is negative for every MVP target;
- `hard_negative_for` supplies only explicit target-specific negatives;
- rows positive for excluded MVP labels are removed entirely and are never
  relabeled as background or negative evidence.

The script indexes governed media; it does not download audio.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from echo.data_foundry.splits import SplitRatios, assign_group

ROOT = Path(__file__).resolve().parents[2]
MATERIALIZATION = ROOT / "MK1/mining-site/materialization"

DEFAULT_CONFIG = ROOT / "configs/mvp/mk1.v1.json"
DEFAULT_LEDGER = MATERIALIZATION / "canonical-release-safe-asset-ledger.jsonl"
DEFAULT_COVERAGE = MATERIALIZATION / "coverage-gate.json"
DEFAULT_SPLIT_POLICY = ROOT / "configs/data_foundry/split_policy.v1.json"
DEFAULT_OUTPUT = MATERIALIZATION / "mvp-benchmark-manifest.jsonl"
DEFAULT_SUMMARY = MATERIALIZATION / "mvp-benchmark-manifest-summary.json"

VALID_SPLITS = {"train", "validation", "test"}
EXPECTED_CONFLICT_STRATEGY = "quarantine_entire_recording_group"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: expected JSON object")
            rows.append(row)
    return rows


def ready(row: Mapping[str, Any]) -> bool:
    return (
        row.get("rights_status") == "ALLOW_RELEASE_SAFE"
        and row.get("stage_status") == "READY_FOR_GLOBAL_DEDUP"
        and not (row.get("blocking_reasons") or [])
        and bool(row.get("media_sha256"))
        and int(row.get("byte_size") or 0) > 0
        and isinstance(row.get("audio_probe"), Mapping)
        and row.get("audio_probe", {}).get("ok") is True
        and bool(row.get("recording_group_id"))
    )


def split_assignments(
    rows: Iterable[Mapping[str, Any]], split_policy: Mapping[str, Any]
) -> tuple[dict[str, str], set[str]]:
    strategy = str(split_policy.get("protected_original_split_conflict_strategy") or "")
    if strategy != EXPECTED_CONFLICT_STRATEGY:
        raise ValueError(
            "MVP manifest requires the certified split-conflict strategy "
            f"{EXPECTED_CONFLICT_STRATEGY!r}, got {strategy!r}"
        )

    original_map = {
        str(key).lower(): str(value)
        for key, value in (split_policy.get("original_split_map") or {}).items()
    }
    ratios_cfg = split_policy.get("fallback_group_hash_ratios") or {}
    ratios = SplitRatios(
        train=float(ratios_cfg.get("train", 0.7)),
        validation=float(ratios_cfg.get("validation", 0.15)),
        test=float(ratios_cfg.get("test", 0.15)),
    )
    seed = str(split_policy.get("seed") or "")

    by_group: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        if ready(row):
            by_group[str(row["recording_group_id"])].append(row)

    assignments: dict[str, str] = {}
    quarantined: set[str] = set()
    for group, items in sorted(by_group.items()):
        if any(bool(item.get("field_holdout")) for item in items):
            assignments[group] = "field_holdout"
            continue

        originals = sorted(
            {
                original_map[str(item.get("original_split") or "").lower()]
                for item in items
                if str(item.get("original_split") or "").lower() in original_map
            }
        )
        if len(originals) > 1:
            assignments[group] = "quarantine"
            quarantined.add(group)
        elif originals:
            assignments[group] = originals[0]
        else:
            assignments[group] = assign_group(group, seed=seed, ratios=ratios)

    return assignments, quarantined


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--split-policy", type=Path, default=DEFAULT_SPLIT_POLICY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--require-aligned", action="store_true")
    args = parser.parse_args()

    config = load_json(args.config)
    coverage = load_json(args.coverage)
    split_policy = load_json(args.split_policy)
    rows = read_jsonl(args.ledger)

    profile_id = str(config.get("profile_id") or "")
    targets = tuple(str(v) for v in config.get("target_labels", []))
    excluded = set(str(v) for v in config.get("excluded_target_labels", []))
    target_set = set(targets)

    if not profile_id or not targets:
        raise SystemExit("MVP config requires profile_id and target_labels")
    if target_set & excluded:
        raise SystemExit("MVP selected and excluded targets overlap")

    assignments, quarantined_groups = split_assignments(rows, split_policy)

    manifest: list[dict[str, Any]] = []
    excluded_positive_rows = 0
    skipped_nonready_rows = 0
    skipped_nondevelopment_rows = 0
    positive_counts: dict[str, Counter[str]] = defaultdict(Counter)
    explicit_negative_counts: dict[str, Counter[str]] = defaultdict(Counter)
    background_counts: Counter[str] = Counter()

    for row in rows:
        if not ready(row):
            skipped_nonready_rows += 1
            continue

        group = str(row.get("recording_group_id") or "")
        split = assignments.get(group)
        if split not in VALID_SPLITS:
            skipped_nondevelopment_rows += 1
            continue

        labels = {str(v) for v in (row.get("echo_labels") or [])}
        if labels & excluded:
            excluded_positive_rows += 1
            continue

        selected_positive = labels & target_set
        confuses = {str(v) for v in (row.get("hard_negative_for") or [])} & target_set
        explicit_negative = confuses - selected_positive

        is_background = not labels
        if is_background:
            explicit_negative = set(targets)

        if not selected_positive and not explicit_negative:
            continue

        supervision: dict[str, int | None] = {}
        for target in targets:
            if target in selected_positive:
                supervision[target] = 1
                positive_counts[split][target] += 1
            elif target in explicit_negative:
                supervision[target] = 0
                explicit_negative_counts[split][target] += 1
            else:
                supervision[target] = None

        if is_background:
            background_counts[split] += 1

        probe = row.get("audio_probe") if isinstance(row.get("audio_probe"), Mapping) else {}
        manifest.append(
            {
                "schema_version": "echo.mvp-benchmark-row.v2",
                "profile_id": profile_id,
                "asset_id": row.get("ledger_asset_id"),
                "split": split,
                "source_dataset": row.get("source_dataset"),
                "underlying_source_family": row.get("underlying_source_family"),
                "source_asset_id": row.get("source_asset_id"),
                "recording_group_id": group,
                "media_sha256": row.get("media_sha256"),
                "duration_seconds": float(probe.get("duration_seconds") or 0.0),
                "sample_rate_hz": probe.get("sample_rate_hz"),
                "channels": probe.get("channels"),
                "origin_uri": row.get("origin_uri"),
                "materialization_evidence": list(row.get("materialization_evidence") or []),
                "positive_labels": sorted(selected_positive),
                "explicit_negative_labels": sorted(explicit_negative),
                "is_background": is_background,
                "supervision": supervision,
            }
        )

    manifest.sort(key=lambda row: (str(row["split"]), str(row.get("asset_id") or "")))

    alignment_gaps: list[str] = []
    coverage_classes = coverage.get("classes", {})
    for target in targets:
        class_row = coverage_classes.get(target, {})
        expected = class_row.get("split_assets", {})
        for split in sorted(VALID_SPLITS):
            actual = positive_counts[split][target]
            required = int(expected.get(split, 0) or 0)
            if actual != required:
                alignment_gaps.append(
                    f"{target}_{split.upper()}_POSITIVE_COUNT_{actual}_NE_{required}"
                )

    expected_development = int(coverage.get("development_asset_count", 0) or 0)
    actual_development = sum(
        1
        for row in rows
        if ready(row)
        and assignments.get(str(row.get("recording_group_id") or "")) in VALID_SPLITS
    )
    if actual_development != expected_development:
        alignment_gaps.append(
            f"DEVELOPMENT_ASSET_COUNT_{actual_development}_NE_{expected_development}"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in manifest:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    summary = {
        "schema_version": "echo.mvp-benchmark-manifest-summary.v2",
        "profile_id": profile_id,
        "status": "ALIGNED" if not alignment_gaps else "MISALIGNED",
        "target_labels": list(targets),
        "excluded_target_labels": sorted(excluded),
        "row_count": len(manifest),
        "excluded_positive_rows": excluded_positive_rows,
        "skipped_nonready_rows": skipped_nonready_rows,
        "skipped_nondevelopment_rows": skipped_nondevelopment_rows,
        "quarantined_recording_group_count": len(quarantined_groups),
        "positive_counts_by_split": {
            split: dict(sorted(positive_counts[split].items()))
            for split in sorted(VALID_SPLITS)
        },
        "explicit_negative_counts_by_split": {
            split: dict(sorted(explicit_negative_counts[split].items()))
            for split in sorted(VALID_SPLITS)
        },
        "background_counts_by_split": dict(sorted(background_counts.items())),
        "alignment_gap_codes": alignment_gaps,
        "supervision_contract": (
            "Selected positives=1; canonical background and hard_negative_for=0; "
            "unobserved target labels remain null/masked. Excluded-target positives are absent."
        ),
        "split_contract": {
            "policy_id": split_policy.get("policy_id"),
            "seed": split_policy.get("seed"),
            "protected_original_split_conflict_strategy": split_policy.get(
                "protected_original_split_conflict_strategy"
            ),
        },
    }
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "profile_id": profile_id,
                "status": summary["status"],
                "rows": len(manifest),
                "excluded_positive_rows": excluded_positive_rows,
                "alignment_gaps": len(alignment_gaps),
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )

    if args.require_aligned and alignment_gaps:
        for gap in alignment_gaps:
            print(" -", gap)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
