#!/usr/bin/env python3
"""Build a leakage-safe benchmark manifest for ECHO-MVP-001.

The manifest preserves partial supervision:
- selected ECHO labels are explicit positives;
- canonical background (no ECHO labels) is negative for every MVP target;
- `extra.confuses` creates only explicit target-specific negatives;
- excluded MVP targets are removed entirely and are never relabeled as background.

This script does not copy or download audio. It produces an index over the
already-governed canonical release-safe ledger.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
MATERIALIZATION = ROOT / "MK1/mining-site/materialization"

DEFAULT_CONFIG = ROOT / "configs/mvp/mk1.v1.json"
DEFAULT_LEDGER = MATERIALIZATION / "canonical-release-safe-asset-ledger.jsonl"
DEFAULT_COVERAGE = MATERIALIZATION / "coverage-gate.json"
DEFAULT_OUTPUT = MATERIALIZATION / "mvp-benchmark-manifest.jsonl"
DEFAULT_SUMMARY = MATERIALIZATION / "mvp-benchmark-manifest-summary.json"

VALID_SPLITS = {"train", "validation", "test"}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
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
            yield row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--require-aligned", action="store_true")
    args = parser.parse_args()

    config = load_json(args.config)
    coverage = load_json(args.coverage)

    profile_id = str(config.get("profile_id") or "")
    targets = tuple(str(v) for v in config.get("target_labels", []))
    excluded = set(str(v) for v in config.get("excluded_target_labels", []))
    target_set = set(targets)

    if not profile_id or not targets:
        raise SystemExit("MVP config requires profile_id and target_labels")
    if target_set & excluded:
        raise SystemExit("MVP selected and excluded targets overlap")

    manifest: list[dict[str, Any]] = []
    excluded_positive_rows = 0
    skipped_unsplit_rows = 0
    positive_counts: dict[str, Counter[str]] = defaultdict(Counter)
    explicit_negative_counts: dict[str, Counter[str]] = defaultdict(Counter)
    background_counts: Counter[str] = Counter()
    media_reference_missing = 0

    for row in read_jsonl(args.ledger):
        if bool(row.get("field_holdout")):
            continue

        split = str(row.get("echo_split") or "")
        if split not in VALID_SPLITS:
            skipped_unsplit_rows += 1
            continue

        labels = {str(v) for v in (row.get("echo_labels") or [])}
        if labels & excluded:
            excluded_positive_rows += 1
            continue

        selected_positive = labels & target_set
        extra = row.get("extra") if isinstance(row.get("extra"), dict) else {}
        confuses = {
            str(v) for v in (extra.get("confuses") or [])
        } & target_set
        explicit_negative = confuses - selected_positive

        is_background = not labels
        if is_background:
            explicit_negative = set(targets)

        if not selected_positive and not explicit_negative:
            continue

        local_relpath = row.get("local_relpath")
        origin_uri = row.get("origin_uri")
        if not local_relpath and not origin_uri:
            media_reference_missing += 1

        supervision = {}
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

        manifest.append(
            {
                "schema_version": "echo.mvp-benchmark-row.v1",
                "profile_id": profile_id,
                "asset_id": row.get("asset_id"),
                "split": split,
                "source_dataset": row.get("source_dataset"),
                "recording_group_id": row.get("recording_group_id"),
                "sha256": row.get("sha256"),
                "duration_seconds": row.get("duration_seconds"),
                "sample_rate_hz": row.get("sample_rate_hz"),
                "channels": row.get("channels"),
                "local_relpath": local_relpath,
                "origin_uri": origin_uri,
                "positive_labels": sorted(selected_positive),
                "explicit_negative_labels": sorted(explicit_negative),
                "is_background": is_background,
                "supervision": supervision,
            }
        )

    manifest.sort(
        key=lambda row: (str(row["split"]), str(row.get("asset_id") or ""))
    )

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

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in manifest:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    summary = {
        "schema_version": "echo.mvp-benchmark-manifest-summary.v1",
        "profile_id": profile_id,
        "status": "ALIGNED" if not alignment_gaps else "MISALIGNED",
        "target_labels": list(targets),
        "excluded_target_labels": sorted(excluded),
        "row_count": len(manifest),
        "excluded_positive_rows": excluded_positive_rows,
        "skipped_unsplit_rows": skipped_unsplit_rows,
        "media_reference_missing": media_reference_missing,
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
            "Selected positives=1; canonical background and explicit extra.confuses=0; "
            "unobserved target labels remain null/masked. Excluded-target positives are absent."
        ),
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
