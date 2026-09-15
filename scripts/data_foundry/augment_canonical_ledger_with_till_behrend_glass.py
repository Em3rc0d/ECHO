#!/usr/bin/env python3
"""Admit the single explicit Till Behrend CC0 glass-break asset into MK1.

The wider OpenGameArt glass expansion report is discovery evidence. This stage
admits exactly one direct asset whose canonical page, author, license, semantic,
bytes, probe and fingerprint are explicit. Generic rubberduck glass-named rows
remain review-only and cannot enter through this path.
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
from scripts.data_foundry.build_canonical_asset_ledger import add_entry, make_entry, recompute_stage

ROOT = Path(__file__).resolve().parents[2]
MAT = ROOT / "MK1/mining-site/materialization"
LEDGER = MAT / "canonical-release-safe-asset-ledger.jsonl"
SUMMARY = MAT / "canonical-release-safe-asset-ledger-summary.json"
REPORT = MAT / "opengameart-glass-expansion-materialization.json"
MANIFEST = ROOT / "configs/data_foundry/opengameart_glass_expansion.v1.json"
SOURCE_POLICY_PATH = ROOT / "configs/data_foundry/dataset_certification.v1.json"
FAMILY_POLICY_PATH = ROOT / "configs/data_foundry/underlying_source_families.v1.json"

SOURCE_ID = "echo-opengameart-till-behrend-glass-v1"
SOURCE_FAMILY = "OPENGAMEART_TILL_BEHREND"
TARGET = "GLASS_SHATTER"
ASSET_ID = "glass_breaking.wav"
RECORDING_GROUP = "till-behrend:glass-breaking"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"expected object at {path}:{number}")
            rows.append(row)
    return rows


def governed_source(manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    if manifest.get("phase") != "EVIDENCE_DISCOVERY_ONLY" or manifest.get("target") != TARGET:
        raise ValueError("OpenGameArt glass manifest phase/target drift")
    matches = [row for row in (manifest.get("sources") or []) if isinstance(row, Mapping) and row.get("source_id") == SOURCE_ID]
    if len(matches) != 1:
        raise ValueError("Till Behrend governed source must appear exactly once")
    source = matches[0]
    if source.get("creator") != "Till Behrend":
        raise ValueError("Till Behrend creator drift")
    if source.get("declared_license") != "CC0":
        raise ValueError("Till Behrend source is no longer CC0")
    if source.get("underlying_source_family_candidate") != SOURCE_FAMILY:
        raise ValueError("Till Behrend source-family drift")
    if source.get("kind") != "direct_audio":
        raise ValueError("Till Behrend asset must remain direct_audio")
    if source.get("expected_filename") != ASSET_ID:
        raise ValueError("Till Behrend expected filename drift")
    if source.get("semantic_candidate") != "glass_shatter":
        raise ValueError("Till Behrend semantic drift")
    if source.get("recording_family_candidate") != RECORDING_GROUP:
        raise ValueError("Till Behrend recording-family drift")
    return source


def validated_asset(report: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, Any]:
    if report.get("status") != "PASS" or report.get("phase") != "EVIDENCE_DISCOVERY_ONLY":
        raise ValueError("OpenGameArt glass expansion durable report is not PASS discovery evidence")
    if list(report.get("failures") or []):
        raise ValueError("OpenGameArt glass expansion report contains failures")
    if int(report.get("explicit_positive_candidate_count") or -1) != 1:
        raise ValueError("OpenGameArt glass expansion explicit-positive count drift")

    source_reports = [row for row in (report.get("sources") or []) if isinstance(row, Mapping) and row.get("source_id") == SOURCE_ID]
    if len(source_reports) != 1:
        raise ValueError("Till Behrend source report must appear exactly once")
    source_report = source_reports[0]
    if source_report.get("status") != "PASS" or int(source_report.get("materialized_count") or -1) != 1:
        raise ValueError("Till Behrend materialization is not exactly one PASS row")
    evidence = source_report.get("canonical_source_evidence")
    if not isinstance(evidence, Mapping):
        raise ValueError("Till Behrend canonical source evidence missing")
    if evidence.get("markers_pass") is not True or evidence.get("creator") != "Till Behrend" or evidence.get("license_id") != "CC0":
        raise ValueError("Till Behrend canonical source evidence drift")
    if evidence.get("url") != source.get("canonical_source_page") or not evidence.get("page_sha256"):
        raise ValueError("Till Behrend canonical page identity incomplete")

    assets = [row for row in (report.get("assets") or []) if isinstance(row, Mapping)]
    exact = [row for row in assets if row.get("source_id") == SOURCE_ID]
    if len(exact) != 1:
        raise ValueError("Till Behrend asset must appear exactly once")
    row = dict(exact[0])
    if row.get("source_asset_id") != ASSET_ID:
        raise ValueError("Till Behrend asset id drift")
    if row.get("role") != "positive_candidate" or row.get("target") != TARGET or row.get("semantic_candidate") != "glass_shatter":
        raise ValueError("Till Behrend positive semantics drift")
    if row.get("recording_family_candidate") != RECORDING_GROUP:
        raise ValueError("Till Behrend grouping drift")
    if row.get("underlying_source_family_candidate") != SOURCE_FAMILY or row.get("license_id") != "CC0":
        raise ValueError("Till Behrend family/license drift")
    if row.get("admission_status") != "REAL_BYTES_MATERIALIZED_SEPARATE_ADMISSION_REQUIRED":
        raise ValueError("Till Behrend materialization state drift")
    if not row.get("media_sha256") or int(row.get("size_bytes") or 0) <= 0:
        raise ValueError("Till Behrend byte identity incomplete")
    probe = row.get("audio_probe")
    if not isinstance(probe, Mapping) or probe.get("ok") is not True or float(probe.get("duration_seconds") or 0) <= 0:
        raise ValueError("Till Behrend probe incomplete")
    fp = row.get("canonical_fingerprint")
    if not isinstance(fp, Mapping) or not fp.get("vector_sha256") or not fp.get("canonical_pcm_sha256"):
        raise ValueError("Till Behrend fingerprint incomplete")

    # Explicitly prove that archive review rows cannot enter this admission path.
    if any(other.get("source_id") != SOURCE_ID and other.get("role") == "positive_candidate" for other in assets):
        raise ValueError("unexpected non-Till explicit positive in discovery report")
    return row


def main() -> int:
    for path in (LEDGER, SUMMARY, REPORT, MANIFEST, SOURCE_POLICY_PATH, FAMILY_POLICY_PATH):
        if not path.is_file():
            raise SystemExit(f"required evidence missing: {path.relative_to(ROOT)}")

    source_policy = load_dataset_certification(SOURCE_POLICY_PATH)
    family_policy = load_underlying_source_policy(FAMILY_POLICY_PATH)
    manifest = read_json(MANIFEST)
    source = governed_source(manifest)
    report = read_json(REPORT)
    row = validated_asset(report, source)

    source_row = (source_policy.get("sources") or {}).get(SOURCE_ID)
    if not isinstance(source_row, Mapping) or (source_row.get("profiles") or {}).get("release_safe") != "ALLOW":
        raise SystemExit("Till Behrend source is not ALLOW for release_safe")
    family_row = (family_policy.get("sources") or {}).get(SOURCE_ID)
    if not isinstance(family_row, Mapping) or family_row.get("family") != SOURCE_FAMILY or family_row.get("diversity_credit") is not True:
        raise SystemExit("Till Behrend underlying source-family policy is not certified")

    existing_rows = read_jsonl(LEDGER)
    entries = {str(item["ledger_asset_id"]): item for item in existing_rows}
    if len(entries) != len(existing_rows):
        raise SystemExit("canonical ledger contains duplicate ledger_asset_id before Till augmentation")
    ledger_id = f"{SOURCE_ID}:{ASSET_ID}"
    if ledger_id in entries:
        raise SystemExit(f"Till Behrend asset already exists before deterministic augmentation: {ledger_id}")

    entry = make_entry(
        source_policy=source_policy,
        family_policy=family_policy,
        source_dataset=SOURCE_ID,
        source_asset_id=ASSET_ID,
        media_sha256=str(row["media_sha256"]),
        byte_size=int(row["size_bytes"]),
        audio_probe=row["audio_probe"],
        license_id="CC0",
        candidate_targets=[TARGET],
        echo_labels=[TARGET],
        hard_negative_for=[],
        semantic_status_by_target={TARGET: "EXACT_CURATED_CC0_SEMANTIC"},
        label_provenance=[
            str(source["canonical_source_page"]),
            str(MANIFEST.relative_to(ROOT)),
            str(REPORT.relative_to(ROOT)),
        ],
        recording_group_id="opengameart:till-behrend:glass-breaking",
        grouping_status="CURATED_RECORDING_FAMILY",
        origin_uri=str(source["canonical_source_page"]),
        original_split=None,
        materialization_evidence=[str(REPORT.relative_to(ROOT))],
        blocking_reasons=[],
    )
    entry["canonical_fingerprint"] = dict(row["canonical_fingerprint"])
    recompute_stage(entry, source_policy)
    add_entry(entries, entry, source_policy)

    final_rows = validate_ledger(entries.values())
    previous = read_json(SUMMARY)
    summary = summarize_ledger(final_rows)
    summary.update({
        key: value
        for key, value in previous.items()
        if key not in summary and key != "opengameart_till_behrend_glass_augmentation"
    })
    summary["opengameart_till_behrend_glass_augmentation"] = {
        "status": "PASS",
        "source_id": SOURCE_ID,
        "underlying_source_family": SOURCE_FAMILY,
        "asset_id": ASSET_ID,
        "recording_group_id": "opengameart:till-behrend:glass-breaking",
        "report_sha256": file_sha256(REPORT),
        "manifest_sha256": file_sha256(MANIFEST),
        "canonical_source_page_sha256": str(
            next(item for item in report["sources"] if item["source_id"] == SOURCE_ID)["canonical_source_evidence"]["page_sha256"]
        ),
        "source_diversity_stop_line": "Distinct author/origin receives one candidate underlying-family credit; OpenGameArt hosting itself is not the family identity.",
        "semantic_stop_line": "Exactly glass_breaking.wav is admitted. The eleven generic rubberduck glass-named discovery rows remain review-only and receive zero positive credit here.",
    }
    input_digests = dict(summary.get("input_digests") or {})
    input_digests["opengameart_glass_expansion_report"] = {
        "path": str(REPORT.relative_to(ROOT)),
        "sha256": file_sha256(REPORT),
    }
    input_digests["opengameart_glass_expansion_manifest"] = {
        "path": str(MANIFEST.relative_to(ROOT)),
        "sha256": file_sha256(MANIFEST),
    }
    summary["input_digests"] = dict(sorted(input_digests.items()))

    with LEDGER.open("w", encoding="utf-8") as handle:
        for item in final_rows:
            handle.write(json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "PASS",
        "entries": summary["entry_count"],
        "positive_counts": summary["positive_counts"],
        "fingerprints_missing": summary["canonical_fingerprint_missing_count"],
        "till_behrend": summary["opengameart_till_behrend_glass_augmentation"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
