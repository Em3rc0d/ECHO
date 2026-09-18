#!/usr/bin/env python3
"""Admit the certified Mike Koenig / SoundBible tire-squeal derivatives into MK1.

The durable materialization proves canonical origin, CC-BY-3.0 rights, archive
identity, real bytes, probes and fingerprints. All archive members are admitted
as exact TIRE_SQUEAL assets but remain one conservative recording group and one
underlying acoustic source family.
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
REPORT = MAT / "soundbible-mike-koenig-tire-materialization.json"
MANIFEST = ROOT / "configs/data_foundry/soundbible_mike_koenig_tire.v1.json"
SOURCE_POLICY_PATH = ROOT / "configs/data_foundry/dataset_certification.v1.json"
FAMILY_POLICY_PATH = ROOT / "configs/data_foundry/underlying_source_families.v1.json"

SOURCE_ID = "echo-soundbible-mike-koenig-tire-v1"
SOURCE_FAMILY = "SOUNDBIBLE_MIKE_KOENIG"
TARGET = "TIRE_SQUEAL"
LICENSE_ID = "CC-BY-3.0"
RECORDING_GROUP = "soundbible:mike-koenig:tires-squealing-1178"
CANONICAL_PAGE = "https://soundbible.com/1178-Tires-Squealing.html"


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


def validate_contract(manifest: Mapping[str, Any], report: Mapping[str, Any]) -> list[dict[str, Any]]:
    if manifest.get("target") != TARGET:
        raise ValueError("SoundBible target drift")
    if manifest.get("source_id_candidate") != SOURCE_ID:
        raise ValueError("SoundBible source id drift")
    if manifest.get("underlying_source_family_candidate") != SOURCE_FAMILY:
        raise ValueError("SoundBible source family drift")
    if (manifest.get("origin") or {}).get("declared_license") != LICENSE_ID:
        raise ValueError("SoundBible manifest license drift")
    if (manifest.get("origin") or {}).get("canonical_page") != CANONICAL_PAGE:
        raise ValueError("SoundBible canonical page drift")
    if (manifest.get("asset") or {}).get("recording_family_candidate") != RECORDING_GROUP:
        raise ValueError("SoundBible recording family drift")

    if report.get("status") != "PASS":
        raise ValueError("SoundBible durable report is not PASS")
    if report.get("phase") != "EVIDENCE_MATERIALIZED_NO_CORPUS_CREDIT":
        raise ValueError("SoundBible report phase drift")
    if report.get("source_id_candidate") != SOURCE_ID or report.get("target") != TARGET:
        raise ValueError("SoundBible report source/target drift")
    if report.get("license_id") != LICENSE_ID:
        raise ValueError("SoundBible report license drift")
    if (report.get("origin") or {}).get("canonical_page") != CANONICAL_PAGE:
        raise ValueError("SoundBible report canonical page drift")
    if int((report.get("transport") or {}).get("audio_member_count") or 0) != 3:
        raise ValueError("SoundBible archive member count drift")

    assets = [dict(row) for row in (report.get("assets") or []) if isinstance(row, Mapping)]
    if len(assets) != 3:
        raise ValueError("SoundBible report must contain exactly three governed audio members")

    keys: set[str] = set()
    for row in assets:
        key = str(row.get("asset_key") or "")
        if not key or key in keys:
            raise ValueError("SoundBible asset key missing/duplicate")
        keys.add(key)
        if row.get("semantic_candidate") != "tire_squeal":
            raise ValueError(f"SoundBible semantic drift: {key}")
        if row.get("recording_family_candidate") != RECORDING_GROUP:
            raise ValueError(f"SoundBible recording-family drift: {key}")
        if row.get("admission_status") != "DISCOVERY_REAL_BYTES_MATERIALIZED_REVIEW_REQUIRED":
            raise ValueError(f"SoundBible evidence state drift: {key}")
        if not row.get("media_sha256") or int(row.get("size_bytes") or 0) <= 0:
            raise ValueError(f"SoundBible byte identity incomplete: {key}")
        probe = row.get("audio_probe")
        if not isinstance(probe, Mapping) or probe.get("ok") is not True or float(probe.get("duration_seconds") or 0) <= 0:
            raise ValueError(f"SoundBible probe incomplete: {key}")
        fp = row.get("canonical_fingerprint")
        if not isinstance(fp, Mapping) or not fp.get("vector_sha256") or not fp.get("canonical_pcm_sha256"):
            raise ValueError(f"SoundBible fingerprint incomplete: {key}")
    return assets


def main() -> int:
    for path in (LEDGER, SUMMARY, REPORT, MANIFEST, SOURCE_POLICY_PATH, FAMILY_POLICY_PATH):
        if not path.is_file():
            raise SystemExit(f"required evidence missing: {path.relative_to(ROOT)}")

    source_policy = load_dataset_certification(SOURCE_POLICY_PATH)
    family_policy = load_underlying_source_policy(FAMILY_POLICY_PATH)
    manifest = read_json(MANIFEST)
    report = read_json(REPORT)
    assets = validate_contract(manifest, report)

    source_row = (source_policy.get("sources") or {}).get(SOURCE_ID)
    if not isinstance(source_row, Mapping) or (source_row.get("profiles") or {}).get("release_safe") != "ALLOW":
        raise SystemExit("SoundBible source is not ALLOW for release_safe")
    family_row = (family_policy.get("sources") or {}).get(SOURCE_ID)
    if not isinstance(family_row, Mapping) or family_row.get("family") != SOURCE_FAMILY or family_row.get("diversity_credit") is not True:
        raise SystemExit("SoundBible underlying source-family policy is not certified")

    existing_rows = read_jsonl(LEDGER)
    entries = {str(item["ledger_asset_id"]): item for item in existing_rows}
    if len(entries) != len(existing_rows):
        raise SystemExit("canonical ledger contains duplicate ledger_asset_id before SoundBible augmentation")

    for row in sorted(assets, key=lambda x: str(x["asset_key"])):
        asset_key = str(row["asset_key"])
        ledger_id = f"{SOURCE_ID}:{asset_key}"
        if ledger_id in entries:
            raise SystemExit(f"SoundBible asset already exists before deterministic augmentation: {ledger_id}")
        entry = make_entry(
            source_policy=source_policy,
            family_policy=family_policy,
            source_dataset=SOURCE_ID,
            source_asset_id=asset_key,
            media_sha256=str(row["media_sha256"]),
            byte_size=int(row["size_bytes"]),
            audio_probe=row["audio_probe"],
            license_id=LICENSE_ID,
            candidate_targets=[TARGET],
            echo_labels=[TARGET],
            hard_negative_for=[],
            semantic_status_by_target={TARGET: "EXACT_CURATED_CC_BY_3_SEMANTIC"},
            label_provenance=[
                CANONICAL_PAGE,
                str((manifest.get("transport") or {}).get("page") or ""),
                str(MANIFEST.relative_to(ROOT)),
                str(REPORT.relative_to(ROOT)),
            ],
            recording_group_id=RECORDING_GROUP,
            grouping_status="CURATED_RECORDING_FAMILY",
            origin_uri=CANONICAL_PAGE,
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
        if key not in summary and key != "soundbible_mike_koenig_tire_augmentation"
    })
    summary["soundbible_mike_koenig_tire_augmentation"] = {
        "status": "PASS",
        "source_id": SOURCE_ID,
        "underlying_source_family": SOURCE_FAMILY,
        "asset_count": len(assets),
        "recording_group_id": RECORDING_GROUP,
        "report_sha256": file_sha256(REPORT),
        "manifest_sha256": file_sha256(MANIFEST),
        "source_diversity_stop_line": "Three derivative members receive exactly one acoustic-origin family and one recording-group identity.",
        "license_stop_line": "CC-BY-3.0 attribution to Mike Koenig and exact version provenance must remain attached to all admitted rows.",
    }
    input_digests = dict(summary.get("input_digests") or {})
    input_digests["soundbible_mike_koenig_tire_report"] = {
        "path": str(REPORT.relative_to(ROOT)),
        "sha256": file_sha256(REPORT),
    }
    input_digests["soundbible_mike_koenig_tire_manifest"] = {
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
        "soundbible": summary["soundbible_mike_koenig_tire_augmentation"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
