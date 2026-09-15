#!/usr/bin/env python3
"""Merge governed OpenGameArt/rubberduck CC0 evidence into the MK1 ledger.

This stage is deliberately downstream of real-byte materialization. It grants
semantic roles only when the durable acquisition report and the versioned
manifest agree exactly, source-level policy allows release_safe use, and every
row carries a valid probe plus canonical fingerprint. Global grouping/dedup,
splits and coverage remain downstream gates.
"""

from __future__ import annotations

from collections import Counter
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
from scripts.data_foundry.build_canonical_asset_ledger import (
    add_entry,
    make_entry,
    recompute_stage,
)

ROOT = Path(__file__).resolve().parents[2]
MATERIALIZATION = ROOT / "MK1/mining-site/materialization"
LEDGER = MATERIALIZATION / "canonical-release-safe-asset-ledger.jsonl"
SUMMARY = MATERIALIZATION / "canonical-release-safe-asset-ledger-summary.json"
REPORT = MATERIALIZATION / "opengameart-rubberduck-cc0-materialization.json"
MANIFEST = ROOT / "configs/data_foundry/opengameart_rubberduck_cc0.v1.json"
SOURCE_POLICY_PATH = ROOT / "configs/data_foundry/dataset_certification.v1.json"
FAMILY_POLICY_PATH = ROOT / "configs/data_foundry/underlying_source_families.v1.json"

SOURCE_ID = "echo-opengameart-rubberduck-cc0-v1"
SOURCE_FAMILY = "OPENGAMEART_RUBBERDUCK"
TARGET = "GLASS_SHATTER"
POSITIVE_SEMANTIC = "glass_breaking_exact_candidate"
MATERIALIZED_STATUS = "REAL_BYTES_MATERIALIZED_REVIEW_REQUIRED"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"expected JSON object at {path}:{line_number}")
            rows.append(value)
    return rows


def manifest_index(payload: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    if payload.get("source_id") != SOURCE_ID:
        raise ValueError("OpenGameArt manifest source_id drift")
    if payload.get("underlying_source_family_candidate") != SOURCE_FAMILY:
        raise ValueError("OpenGameArt manifest source-family drift")
    if payload.get("declared_license") != "CC0":
        raise ValueError("OpenGameArt manifest is no longer CC0")

    transport = payload.get("acquisition_transport")
    if not isinstance(transport, Mapping):
        raise ValueError("OpenGameArt transport evidence missing")
    commit = str(transport.get("commit") or "")
    if len(commit) != 40:
        raise ValueError("OpenGameArt transport must remain commit-pinned")

    rows = payload.get("assets")
    if not isinstance(rows, list) or not rows:
        raise ValueError("OpenGameArt manifest assets missing")
    result: dict[str, dict[str, Any]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("OpenGameArt manifest row is not an object")
        asset_id = str(raw.get("path") or "")
        if not asset_id or asset_id in result:
            raise ValueError(f"OpenGameArt invalid/duplicate asset id: {asset_id}")
        role = str(raw.get("role") or "")
        family = str(raw.get("recording_family") or "")
        semantic = str(raw.get("semantic") or "")
        if not family:
            raise ValueError(f"OpenGameArt recording family missing: {asset_id}")
        if role == "positive_candidate":
            if raw.get("target") != TARGET or semantic != POSITIVE_SEMANTIC:
                raise ValueError(f"OpenGameArt positive semantic drift: {asset_id}")
        elif role == "hard_negative_candidate":
            if list(raw.get("confuses") or []) != [TARGET]:
                raise ValueError(f"OpenGameArt hard-negative mapping drift: {asset_id}")
        else:
            raise ValueError(f"OpenGameArt unsupported role: {role}")
        result[asset_id] = dict(raw)
    return result


def validate_report(
    report: Mapping[str, Any],
    manifest: Mapping[str, Any],
    governed: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if report.get("status") != "PASS":
        raise ValueError("OpenGameArt durable materialization is not PASS")
    if report.get("source_id") != SOURCE_ID:
        raise ValueError("OpenGameArt report source_id drift")
    if report.get("source_family_candidate") != SOURCE_FAMILY:
        raise ValueError("OpenGameArt report source-family drift")
    if list(report.get("failures") or []):
        raise ValueError("OpenGameArt durable materialization has failures")

    source_evidence = report.get("canonical_source_evidence")
    if not isinstance(source_evidence, Mapping):
        raise ValueError("OpenGameArt canonical source evidence missing")
    if source_evidence.get("markers_pass") is not True:
        raise ValueError("OpenGameArt source-page markers did not pass")
    if str(source_evidence.get("license_id") or "") != "CC0":
        raise ValueError("OpenGameArt source-page license is not CC0")
    if str(source_evidence.get("url") or "") != str(manifest.get("canonical_source_page") or ""):
        raise ValueError("OpenGameArt canonical source page drift")
    if not str(source_evidence.get("page_sha256") or ""):
        raise ValueError("OpenGameArt canonical source-page hash missing")

    transport = report.get("transport_evidence")
    manifest_transport = manifest.get("acquisition_transport")
    if not isinstance(transport, Mapping) or not isinstance(manifest_transport, Mapping):
        raise ValueError("OpenGameArt transport evidence missing")
    if transport.get("source_credit") is not False:
        raise ValueError("OpenGameArt mirror must never receive source credit")
    for key in ("repository", "commit", "directory"):
        if str(transport.get(key) or "") != str(manifest_transport.get(key) or ""):
            raise ValueError(f"OpenGameArt transport {key} drift")

    rows = report.get("assets")
    if not isinstance(rows, list):
        raise ValueError("OpenGameArt report assets missing")
    if int(report.get("materialized_count") or -1) != len(rows):
        raise ValueError("OpenGameArt materialized_count mismatch")
    if int(report.get("fingerprinted_count") or -1) != len(rows):
        raise ValueError("OpenGameArt fingerprinted_count mismatch")
    if {str(row.get("source_asset_id") or "") for row in rows if isinstance(row, Mapping)} != set(governed):
        raise ValueError("OpenGameArt report/manifest asset set mismatch")

    validated: list[dict[str, Any]] = []
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("OpenGameArt report row is not an object")
        asset_id = str(raw.get("source_asset_id") or "")
        expected = governed[asset_id]
        if raw.get("admission_status") != MATERIALIZED_STATUS:
            raise ValueError(f"OpenGameArt unexpected materialization status: {asset_id}")
        if raw.get("source_dataset_candidate") != SOURCE_ID:
            raise ValueError(f"OpenGameArt row source drift: {asset_id}")
        if raw.get("underlying_source_family_candidate") != SOURCE_FAMILY:
            raise ValueError(f"OpenGameArt row family drift: {asset_id}")
        if raw.get("license_id") != "CC0":
            raise ValueError(f"OpenGameArt row license drift: {asset_id}")
        for field in ("role", "semantic", "recording_family"):
            if str(raw.get(field) or "") != str(expected.get(field) or ""):
                raise ValueError(f"OpenGameArt row {field} drift: {asset_id}")
        if raw.get("role") == "positive_candidate":
            if raw.get("target") != TARGET or list(raw.get("confuses") or []):
                raise ValueError(f"OpenGameArt positive role conflict: {asset_id}")
        else:
            if list(raw.get("confuses") or []) != [TARGET]:
                raise ValueError(f"OpenGameArt hard-negative role conflict: {asset_id}")
        if str(raw.get("transport_commit") or "") != str(manifest_transport.get("commit") or ""):
            raise ValueError(f"OpenGameArt row transport commit drift: {asset_id}")
        if not str(raw.get("media_sha256") or "") or int(raw.get("size_bytes") or 0) <= 0:
            raise ValueError(f"OpenGameArt row byte identity incomplete: {asset_id}")
        probe = raw.get("audio_probe")
        if not isinstance(probe, Mapping) or probe.get("ok") is not True:
            raise ValueError(f"OpenGameArt row probe incomplete: {asset_id}")
        fingerprint = raw.get("canonical_fingerprint")
        if not isinstance(fingerprint, Mapping) or not fingerprint.get("vector_sha256") or not fingerprint.get("canonical_pcm_sha256"):
            raise ValueError(f"OpenGameArt row fingerprint incomplete: {asset_id}")
        validated.append(dict(raw))

    positives = [row for row in validated if row["role"] == "positive_candidate"]
    negatives = [row for row in validated if row["role"] == "hard_negative_candidate"]
    if len(positives) != 6 or {str(row["recording_family"]) for row in positives} != {"bfh1:glass_breaking"}:
        raise ValueError("OpenGameArt conservative positive grouping contract failed")
    if len(negatives) < 20 or len({str(row["recording_family"]) for row in negatives}) < 10:
        raise ValueError("OpenGameArt governed hard-negative floor unexpectedly regressed")
    return validated


def main() -> int:
    for path in (LEDGER, SUMMARY, REPORT, MANIFEST, SOURCE_POLICY_PATH, FAMILY_POLICY_PATH):
        if not path.is_file():
            raise SystemExit(f"required evidence missing: {path.relative_to(ROOT)}")

    source_policy = load_dataset_certification(SOURCE_POLICY_PATH)
    family_policy = load_underlying_source_policy(FAMILY_POLICY_PATH)
    manifest = read_json(MANIFEST)
    governed = manifest_index(manifest)
    report = read_json(REPORT)
    report_rows = validate_report(report, manifest, governed)

    source_row = (source_policy.get("sources") or {}).get(SOURCE_ID)
    if not isinstance(source_row, Mapping) or (source_row.get("profiles") or {}).get("release_safe") != "ALLOW":
        raise SystemExit("OpenGameArt source is not ALLOW for release_safe")
    family_row = (family_policy.get("sources") or {}).get(SOURCE_ID)
    if not isinstance(family_row, Mapping) or family_row.get("family") != SOURCE_FAMILY or family_row.get("diversity_credit") is not True:
        raise SystemExit("OpenGameArt underlying source-family policy is not certified")

    existing_rows = read_jsonl(LEDGER)
    entries = {str(row["ledger_asset_id"]): row for row in existing_rows}
    if len(entries) != len(existing_rows):
        raise SystemExit("canonical ledger contains duplicate ledger_asset_id before OpenGameArt augmentation")

    stats = Counter()
    for row in report_rows:
        asset_id = str(row["source_asset_id"])
        role = str(row["role"])
        is_positive = role == "positive_candidate"
        family = str(row["recording_family"])
        ledger_id = f"{SOURCE_ID}:{asset_id}"
        if ledger_id in entries:
            raise SystemExit(f"OpenGameArt asset already exists before deterministic augmentation: {ledger_id}")

        entry = make_entry(
            source_policy=source_policy,
            family_policy=family_policy,
            source_dataset=SOURCE_ID,
            source_asset_id=asset_id,
            media_sha256=str(row["media_sha256"]),
            byte_size=int(row["size_bytes"]),
            audio_probe=row["audio_probe"],
            license_id="CC0",
            candidate_targets=[TARGET],
            echo_labels=([TARGET] if is_positive else []),
            hard_negative_for=([] if is_positive else [TARGET]),
            semantic_status_by_target={
                TARGET: "EXACT_CURATED_CC0_SEMANTIC" if is_positive else "EXPLICIT_CURATED_CONFUSER"
            },
            label_provenance=[
                str(manifest["canonical_source_page"]),
                str(MANIFEST.relative_to(ROOT)),
                str(REPORT.relative_to(ROOT)),
            ],
            recording_group_id=f"opengameart:rubberduck:{family}",
            grouping_status="CURATED_RECORDING_FAMILY",
            origin_uri=str(manifest["canonical_source_page"]),
            original_split=None,
            materialization_evidence=[str(REPORT.relative_to(ROOT))],
            blocking_reasons=[],
        )
        entry["canonical_fingerprint"] = dict(row["canonical_fingerprint"])
        recompute_stage(entry, source_policy)
        add_entry(entries, entry, source_policy)
        stats["rows"] += 1
        stats["positive_rows"] += int(is_positive)
        stats["hard_negative_rows"] += int(not is_positive)
        stats[f"group:{family}"] += 1

    final_rows = validate_ledger(entries.values())
    previous = read_json(SUMMARY)
    summary = summarize_ledger(final_rows)
    summary.update({
        key: value
        for key, value in previous.items()
        if key not in summary and key != "opengameart_rubberduck_cc0_augmentation"
    })
    summary["opengameart_rubberduck_cc0_augmentation"] = {
        "status": "PASS",
        "source_id": SOURCE_ID,
        "underlying_source_family": SOURCE_FAMILY,
        "report_sha256": file_sha256(REPORT),
        "manifest_sha256": file_sha256(MANIFEST),
        "canonical_source_page_sha256": str(report["canonical_source_evidence"]["page_sha256"]),
        "stats": dict(sorted(stats.items())),
        "source_diversity_stop_line": "The OpenGameArt submission/creator is one acoustic-origin family. The pinned GitHub mirror is transport only and never receives independent credit.",
        "grouping_stop_line": "All six numbered glass-breaking variants remain one positive recording group unless stronger independent-session evidence is later proven.",
    }
    input_digests = dict(summary.get("input_digests") or {})
    input_digests["opengameart_rubberduck_cc0_report"] = {
        "path": str(REPORT.relative_to(ROOT)),
        "sha256": file_sha256(REPORT),
    }
    input_digests["opengameart_rubberduck_cc0_manifest"] = {
        "path": str(MANIFEST.relative_to(ROOT)),
        "sha256": file_sha256(MANIFEST),
    }
    summary["input_digests"] = dict(sorted(input_digests.items()))

    with LEDGER.open("w", encoding="utf-8") as handle:
        for row in final_rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "PASS",
        "entries": summary["entry_count"],
        "positive_counts": summary["positive_counts"],
        "hard_negative_counts": summary.get("hard_negative_counts"),
        "fingerprints_missing": summary["canonical_fingerprint_missing_count"],
        "opengameart_stats": summary["opengameart_rubberduck_cc0_augmentation"]["stats"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
