#!/usr/bin/env python3
"""Merge ephemeral SONYC shard inventories into durable compact evidence."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

EXPECTED_SHARDS = set(range(19))
TARGETS = ("VEHICLE_HORN", "SIREN")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compact_technical_evidence(row: dict) -> dict:
    return {
        "byte_size": row["byte_size"],
        "audio_probe": row["audio_probe"],
        "canonical_fingerprint": row.get("canonical_fingerprint"),
        "fingerprint_error": row.get("fingerprint_error"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    input_root = Path(args.input_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summaries: dict[int, dict] = {}
    inventories: dict[int, Path] = {}
    for path in input_root.rglob("sonyc-shard-*.json"):
        payload = load_json(path)
        index = int(payload["shard_index"])
        summaries[index] = payload
    for path in input_root.rglob("sonyc-shard-*.jsonl.gz"):
        name = path.name.removeprefix("sonyc-shard-").removesuffix(".jsonl.gz")
        inventories[int(name)] = path

    missing_summaries = sorted(EXPECTED_SHARDS - set(summaries))
    missing_inventories = sorted(EXPECTED_SHARDS - set(inventories))
    if missing_summaries or missing_inventories:
        raise SystemExit(f"incomplete SONYC evidence: summaries={missing_summaries} inventories={missing_inventories}")

    total_assets = 0
    total_duration = 0.0
    probe_failures = 0
    fingerprinted_assets = 0
    fingerprint_failures = 0
    unmatched_annotations = 0
    target_counts = Counter()
    confuser_counts = Counter()
    split_counts = Counter()
    target_groups: dict[str, set[str]] = defaultdict(set)
    target_splits: dict[str, Counter[str]] = defaultdict(Counter)
    seen_sha: dict[str, str] = {}
    duplicate_sha: dict[str, list[str]] = defaultdict(list)
    selected_records: list[dict] = []
    confuser_records: list[dict] = []
    shard_rows: list[dict] = []

    for index in sorted(EXPECTED_SHARDS):
        summary = summaries[index]
        inv = inventories[index]
        if sha256_file(inv) != summary["inventory_sha256"]:
            raise SystemExit(f"inventory digest mismatch for shard {index}")
        if summary["shard_evidence"]["actual_md5"] != summary["shard_evidence"]["publisher_md5"]:
            raise SystemExit(f"publisher checksum mismatch recorded for shard {index}")

        shard_rows.append({
            "shard_index": index,
            "shard_file": summary["shard_file"],
            "publisher_md5": summary["shard_evidence"]["publisher_md5"],
            "archive_sha256": summary["shard_evidence"]["sha256"],
            "archive_size_bytes": summary["shard_evidence"]["size_bytes"],
            "asset_count": summary["asset_count"],
            "inventory_sha256": summary["inventory_sha256"],
            "fingerprinted_ledger_relevant_assets": int(summary.get("fingerprinted_ledger_relevant_assets") or 0),
            "fingerprint_failures": int(summary.get("fingerprint_failures") or 0),
            "status": summary["status"],
        })
        total_assets += int(summary["asset_count"])
        total_duration += float(summary["total_duration_seconds"])
        probe_failures += int(summary["probe_failures"])
        fingerprinted_assets += int(summary.get("fingerprinted_ledger_relevant_assets") or 0)
        fingerprint_failures += int(summary.get("fingerprint_failures") or 0)
        unmatched_annotations += int(summary["unmatched_annotation_assets"])
        target_counts.update(summary["target_ground_truth_counts"])
        confuser_counts.update(summary["confuser_ground_truth_counts"])
        split_counts.update(summary["split_counts"])

        with gzip.open(inv, "rt", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                sha = str(row["sha256"])
                asset = str(row["source_asset_id"])
                previous = seen_sha.get(sha)
                if previous and previous != asset:
                    duplicate_sha[sha].extend([previous, asset])
                else:
                    seen_sha[sha] = asset

                labels = list(row.get("echo_labels_ground_truth") or [])
                confuses = list(row.get("confuses_ground_truth") or [])
                technical = compact_technical_evidence(row)
                if labels:
                    compact = {
                        "source_dataset": row["source_dataset"],
                        "source_release": row["source_release"],
                        "source_asset_id": row["source_asset_id"],
                        "sha256": row["sha256"],
                        **technical,
                        "license_id": row["license_id"],
                        "label_provenance": row["label_provenance"],
                        "echo_labels": labels,
                        "split": row["split"],
                        "sensor_id": row.get("sensor_id"),
                        "recording_group_candidate": row["recording_group_candidate"],
                        "archive": row["archive"],
                        "archive_member": row["archive_member"],
                    }
                    selected_records.append(compact)
                    for label in labels:
                        target_groups[label].add(str(row["recording_group_candidate"]))
                        target_splits[label][str(row["split"])] += 1
                if confuses:
                    confuser_records.append({
                        "source_dataset": row["source_dataset"],
                        "source_release": row["source_release"],
                        "source_asset_id": row["source_asset_id"],
                        "sha256": row["sha256"],
                        **technical,
                        "license_id": row["license_id"],
                        "confuses": confuses,
                        "source_confusers": row.get("source_confusers_ground_truth", []),
                        "split": row["split"],
                        "recording_group_candidate": row["recording_group_candidate"],
                        "archive": row["archive"],
                        "archive_member": row["archive_member"],
                    })

    selected_records.sort(key=lambda row: (row["source_asset_id"], row["sha256"]))
    confuser_records.sort(key=lambda row: (row["source_asset_id"], row["sha256"]))

    target_path = output_dir / "sonyc-v2.3-target-candidates.jsonl"
    with target_path.open("w", encoding="utf-8") as handle:
        for row in selected_records:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")

    confuser_path = output_dir / "sonyc-v2.3-confuser-candidates.jsonl"
    with confuser_path.open("w", encoding="utf-8") as handle:
        for row in confuser_records:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")

    shard_digest_path = output_dir / "sonyc-v2.3-shard-digests.json"
    shard_digest_path.write_text(json.dumps({
        "schema_version": "echo.sonyc-shard-digests.v2",
        "source_id": "sonyc-ust-v2",
        "source_release": "2.3",
        "shards": shard_rows,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    status = "PASS" if not duplicate_sha and probe_failures == 0 and fingerprint_failures == 0 and unmatched_annotations == 0 else "PASS_WITH_REVIEW_FLAGS"
    summary = {
        "schema_version": "echo.sonyc-full-materialization-summary.v2",
        "status": status,
        "source_id": "sonyc-ust-v2",
        "source_release": "2.3",
        "shards_expected": 19,
        "shards_materialized": 19,
        "asset_count": total_assets,
        "total_duration_seconds": round(total_duration, 6),
        "probe_failures": probe_failures,
        "fingerprinted_ledger_relevant_assets": fingerprinted_assets,
        "fingerprint_failures": fingerprint_failures,
        "unmatched_annotation_assets": unmatched_annotations,
        "exact_duplicate_sha256_group_count": len(duplicate_sha),
        "exact_duplicate_examples": [
            {"sha256": sha, "assets": sorted(set(assets))[:10]}
            for sha, assets in sorted(duplicate_sha.items())[:20]
        ],
        "split_counts": dict(sorted(split_counts.items())),
        "target_ground_truth_counts": dict(sorted(target_counts.items())),
        "target_independent_group_candidates": {label: len(target_groups[label]) for label in TARGETS},
        "target_split_counts": {label: dict(sorted(target_splits[label].items())) for label in TARGETS},
        "confuser_ground_truth_counts": dict(sorted(confuser_counts.items())),
        "target_candidate_count": len(selected_records),
        "confuser_candidate_count": len(confuser_records),
        "target_candidates_sha256": sha256_file(target_path),
        "confuser_candidates_sha256": sha256_file(confuser_path),
        "shard_digests_sha256": sha256_file(shard_digest_path),
        "certification_boundary": "Real SONYC bytes were fully materialized shard-by-shard under ECHO-FREE-TIER-001. Ledger-relevant target/confuser records retain asset-level size, probe and canonical fingerprint evidence. Global source diversity, hard-negative, near-duplicate, split and coverage gates remain authoritative.",
    }
    summary_path = output_dir / "sonyc-v2.3-full-materialization-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())