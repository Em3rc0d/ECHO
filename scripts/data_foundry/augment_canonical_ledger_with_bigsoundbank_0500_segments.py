#!/usr/bin/env python3
"""Replace BigSoundBank s0500 parent credit with audited child event assets.

This is a reviewed corpus transformation, not source inflation:
- the overlapping parent positive is removed before children are added;
- all 17 children inherit one underlying source family and one recording group;
- source/group diversity therefore does not increase;
- every child must match the deterministic materialization report;
- global dedup, grouping, splits and coverage still run afterward.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from echo.data_foundry.ledger import (
    file_sha256,
    load_underlying_source_policy,
    summarize_ledger,
    validate_ledger,
)
from echo.data_foundry.source_policy import load_dataset_certification
from scripts.data_foundry.build_canonical_asset_ledger import make_entry, recompute_stage

ROOT = Path(__file__).resolve().parents[2]
MAT = ROOT / "MK1/mining-site/materialization"
LEDGER = MAT / "canonical-release-safe-asset-ledger.jsonl"
SUMMARY = MAT / "canonical-release-safe-asset-ledger-summary.json"
AUDIT = MAT / "bigsoundbank-0500-segmentation-audit.json"
REPORT = MAT / "bigsoundbank-0500-segment-materialization.json"
SOURCE_POLICY_PATH = ROOT / "configs/data_foundry/dataset_certification.v1.json"
FAMILY_POLICY_PATH = ROOT / "configs/data_foundry/underlying_source_families.v1.json"

SOURCE_ID = "echo-bigsoundbank-cc0-gap-v1"
PARENT_ASSET_ID = "bigsoundbank-500"
PARENT_LEDGER_ID = f"{SOURCE_ID}:{PARENT_ASSET_ID}"
TARGET = "TIRE_SQUEAL"
RECORDING_GROUP = f"{SOURCE_ID}:tire_500"
EXPECTED_SEGMENTS = 17


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError("ledger row must be object")
                rows.append(row)
    return rows


def main() -> int:
    for path in (LEDGER, SUMMARY, AUDIT, REPORT, SOURCE_POLICY_PATH, FAMILY_POLICY_PATH):
        if not path.is_file():
            raise SystemExit(f"missing required evidence: {path.relative_to(ROOT)}")

    audit = read_json(AUDIT)
    report = read_json(REPORT)
    if audit.get("status") != "PASS_CANDIDATE":
        raise SystemExit("s0500 segmentation audit is not PASS_CANDIDATE")
    if report.get("status") != "PASS" or report.get("phase") != "SEGMENT_MATERIALIZED_NO_CORPUS_CREDIT":
        raise SystemExit("s0500 segment materialization is not PASS")
    if report.get("segment_count") != EXPECTED_SEGMENTS:
        raise SystemExit("s0500 segment count drift")
    if report.get("parent_media_sha256") != audit.get("media_sha256"):
        raise SystemExit("s0500 parent media identity disagreement")
    if report.get("recording_family") != "tire_500":
        raise SystemExit("s0500 recording-family drift")

    audit_events = {int(row["event_index"]): row for row in audit.get("events") or []}
    segments = report.get("segments") or []
    if len(audit_events) != EXPECTED_SEGMENTS or len(segments) != EXPECTED_SEGMENTS:
        raise SystemExit("s0500 audit/materialization cardinality mismatch")

    source_policy = load_dataset_certification(SOURCE_POLICY_PATH)
    family_policy = load_underlying_source_policy(FAMILY_POLICY_PATH)
    rows = read_jsonl(LEDGER)
    entries = {str(row["ledger_asset_id"]): row for row in rows}
    if len(entries) != len(rows):
        raise SystemExit("duplicate ledger_asset_id before s0500 augmentation")

    parent = entries.get(PARENT_LEDGER_ID)
    if not isinstance(parent, Mapping):
        raise SystemExit("s0500 parent is missing from canonical ledger")
    if TARGET not in set(parent.get("echo_labels") or []):
        raise SystemExit("s0500 parent is not an admitted TIRE_SQUEAL positive")
    if str(parent.get("recording_group_id")) != RECORDING_GROUP:
        raise SystemExit("s0500 parent recording group drift")
    if str(parent.get("license_id")).upper() not in {"CC0", "CC0-1.0"}:
        raise SystemExit("s0500 parent rights drift")

    del entries[PARENT_LEDGER_ID]

    child_ids: list[str] = []
    for segment in segments:
        idx = int(segment["event_index"])
        audited = audit_events.get(idx)
        if not audited:
            raise SystemExit(f"missing audit event {idx}")
        fp = segment.get("canonical_fingerprint")
        if not isinstance(fp, Mapping):
            raise SystemExit(f"segment {idx} missing canonical fingerprint")
        if fp.get("canonical_pcm_sha256") != audited.get("canonical_pcm_sha256"):
            raise SystemExit(f"segment {idx} PCM identity mismatch vs audit")
        if int(fp.get("decoded_sample_count") or 0) != int(audited.get("decoded_sample_count") or 0):
            raise SystemExit(f"segment {idx} sample-count mismatch vs audit")
        if segment.get("semantic") != "tire_squeal":
            raise SystemExit(f"segment {idx} semantic drift")
        if segment.get("recording_family") != "tire_500":
            raise SystemExit(f"segment {idx} family drift")

        source_asset_id = str(segment["segment_asset_id"])
        ledger_id = f"{SOURCE_ID}:{source_asset_id}"
        if ledger_id in entries:
            raise SystemExit(f"segment ledger id already exists: {ledger_id}")

        row = make_entry(
            source_policy=source_policy,
            family_policy=family_policy,
            source_dataset=SOURCE_ID,
            source_asset_id=source_asset_id,
            media_sha256=str(segment["media_sha256"]),
            byte_size=int(segment["size_bytes"]),
            audio_probe=segment["audio_probe"],
            license_id="CC0",
            candidate_targets=[TARGET],
            echo_labels=[TARGET],
            hard_negative_for=[],
            semantic_status_by_target={TARGET: "EXACT_AUDITED_TEMPORAL_EVENT"},
            label_provenance=[
                str(audit.get("canonical_page") or ""),
                str(AUDIT.relative_to(ROOT)),
                str(REPORT.relative_to(ROOT)),
            ],
            recording_group_id=RECORDING_GROUP,
            grouping_status="AUDITED_PARENT_EVENT_SEGMENTS_ONE_GROUP",
            origin_uri=str(audit.get("canonical_page") or ""),
            original_split=None,
            materialization_evidence=[str(AUDIT.relative_to(ROOT)), str(REPORT.relative_to(ROOT))],
        )
        row["canonical_fingerprint"] = dict(fp)
        recompute_stage(row, source_policy)
        if row.get("stage_status") not in {"READY_FOR_GLOBAL_DEDUP", "REVIEW_REQUIRED"}:
            raise SystemExit(f"segment {idx} not eligible for global audit: {row.get('blocking_reasons')}")
        entries[ledger_id] = row
        child_ids.append(ledger_id)

    final_rows = validate_ledger(entries.values())
    previous = read_json(SUMMARY)
    summary = summarize_ledger(final_rows)
    summary.update({key: value for key, value in previous.items() if key not in summary and key != "bigsoundbank_0500_segmentation_augmentation"})
    summary["bigsoundbank_0500_segmentation_augmentation"] = {
        "status": "PASS",
        "source_id": SOURCE_ID,
        "target": TARGET,
        "parent_removed": PARENT_LEDGER_ID,
        "child_count": EXPECTED_SEGMENTS,
        "child_ledger_ids": sorted(child_ids),
        "recording_group_id": RECORDING_GROUP,
        "underlying_source_family": parent.get("underlying_source_family"),
        "audit_sha256": file_sha256(AUDIT),
        "segment_report_sha256": file_sha256(REPORT),
        "overlap_stop_line": "The full s0500 parent positive is removed before child-event credit is added.",
        "diversity_stop_line": "All 17 child events retain exactly one BigSoundBank source family and one recording group.",
    }
    digests = dict(summary.get("input_digests") or {})
    digests["bigsoundbank_0500_segmentation_audit"] = {"path": str(AUDIT.relative_to(ROOT)), "sha256": file_sha256(AUDIT)}
    digests["bigsoundbank_0500_segment_materialization"] = {"path": str(REPORT.relative_to(ROOT)), "sha256": file_sha256(REPORT)}
    summary["input_digests"] = dict(sorted(digests.items()))

    with LEDGER.open("w", encoding="utf-8") as handle:
        for row in final_rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "PASS",
        "parent_removed": PARENT_LEDGER_ID,
        "children_added": EXPECTED_SEGMENTS,
        "positive_counts": summary.get("positive_counts"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
