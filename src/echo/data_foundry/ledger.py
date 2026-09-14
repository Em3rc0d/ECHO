"""Canonical durable evidence ledger for MK1 Corpus Foundry closure.

The ledger consolidates already-materialized source evidence without promoting
candidates to final corpus admission. It is a deterministic stop-line surface
between source-specific materializers and the global admission/dedup/split
pipeline.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from echo.data_foundry.contracts import TARGET_LABELS


LEDGER_ENTRY_SCHEMA = "echo.canonical-asset-ledger-entry.v1"
LEDGER_SUMMARY_SCHEMA = "echo.canonical-asset-ledger-summary.v1"
_ALLOWED_STAGE_STATUS = {"READY_FOR_GLOBAL_DEDUP", "REVIEW_REQUIRED", "BLOCKED"}
_ALLOWED_RIGHTS_STATUS = {"ALLOW_RELEASE_SAFE", "REVIEW_REQUIRED", "RESEARCH_ONLY", "DENY"}


def stable_json_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_underlying_source_policy(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != "echo.underlying-source-families.v1":
        raise ValueError("unsupported underlying-source-family policy schema")
    sources = payload.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("underlying-source-family policy requires sources")
    for source_id, row in sources.items():
        if not isinstance(row, Mapping) or not str(row.get("family") or "").strip():
            raise ValueError(f"underlying source family missing: {source_id}")
    return payload


def underlying_source_family(policy: Mapping[str, Any], source_dataset: str) -> str:
    sources = policy.get("sources")
    if not isinstance(sources, Mapping):
        raise ValueError("underlying source policy missing sources")
    row = sources.get(source_dataset)
    if not isinstance(row, Mapping):
        raise ValueError(f"unregistered underlying source family: {source_dataset}")
    family = str(row.get("family") or "").strip()
    if not family:
        raise ValueError(f"empty underlying source family: {source_dataset}")
    return family


def _is_sha256(value: object) -> bool:
    text = str(value or "").lower()
    return len(text) == 64 and all(ch in "0123456789abcdef" for ch in text)


def validate_ledger_entry(row: Mapping[str, Any]) -> None:
    if row.get("schema_version") != LEDGER_ENTRY_SCHEMA:
        raise ValueError("unsupported canonical ledger entry schema")
    required_text = (
        "ledger_asset_id",
        "source_dataset",
        "source_release",
        "source_asset_id",
        "underlying_source_family",
        "license_id",
        "rights_status",
        "recording_group_id",
        "grouping_status",
        "stage_status",
    )
    for key in required_text:
        if not str(row.get(key) or "").strip():
            raise ValueError(f"canonical ledger entry missing {key}")
    if not _is_sha256(row.get("media_sha256")):
        raise ValueError(f"invalid media_sha256 for {row.get('ledger_asset_id')}")
    raw_byte_size = row.get("byte_size")
    if raw_byte_size is not None and int(raw_byte_size) < 0:
        raise ValueError(f"negative byte_size for {row.get('ledger_asset_id')}")
    labels = {str(value) for value in (row.get("echo_labels") or [])}
    confuses = {str(value) for value in (row.get("hard_negative_for") or [])}
    unknown = (labels | confuses) - set(TARGET_LABELS)
    if unknown:
        raise ValueError(f"unknown ECHO target(s): {sorted(unknown)}")
    conflict = labels & confuses
    if conflict:
        raise ValueError(f"asset cannot be positive and hard negative for same target: {sorted(conflict)}")
    if row.get("rights_status") not in _ALLOWED_RIGHTS_STATUS:
        raise ValueError(f"unsupported rights_status: {row.get('rights_status')}")
    if row.get("stage_status") not in _ALLOWED_STAGE_STATUS:
        raise ValueError(f"unsupported stage_status: {row.get('stage_status')}")
    blockers = row.get("blocking_reasons")
    if not isinstance(blockers, list):
        raise ValueError("blocking_reasons must be a list")
    if row.get("stage_status") == "READY_FOR_GLOBAL_DEDUP" and blockers:
        raise ValueError("READY_FOR_GLOBAL_DEDUP cannot carry blocking reasons")
    probe = row.get("audio_probe")
    if row.get("stage_status") == "READY_FOR_GLOBAL_DEDUP":
        if int(row.get("byte_size") or 0) <= 0:
            raise ValueError("ready entry requires positive byte_size")
        if not isinstance(probe, Mapping) or probe.get("ok") is not True:
            raise ValueError("ready entry requires a valid asset-level audio probe")
        if float(probe.get("duration_seconds") or 0.0) <= 0:
            raise ValueError("ready entry requires positive duration")
        if int(probe.get("sample_rate_hz") or 0) <= 0 or int(probe.get("channels") or 0) <= 0:
            raise ValueError("ready entry requires sample rate and channels")
        if row.get("rights_status") != "ALLOW_RELEASE_SAFE":
            raise ValueError("ready entry must have release-safe rights")
        if not labels and not confuses:
            raise ValueError("ready entry must be an exact positive or explicit hard negative")


def validate_ledger(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    materialized = [dict(row) for row in rows]
    seen: dict[str, str] = {}
    for row in materialized:
        validate_ledger_entry(row)
        asset_id = str(row["ledger_asset_id"])
        digest = str(row["media_sha256"])
        previous = seen.get(asset_id)
        if previous is not None and previous != digest:
            raise ValueError(f"ledger asset identity collision with conflicting bytes: {asset_id}")
        if previous is not None:
            raise ValueError(f"duplicate ledger_asset_id: {asset_id}")
        seen[asset_id] = digest
    return sorted(materialized, key=lambda row: str(row["ledger_asset_id"]))


def ledger_digest(rows: Iterable[Mapping[str, Any]]) -> str:
    materialized = validate_ledger(rows)
    return stable_json_sha256(materialized)


def summarize_ledger(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    materialized = validate_ledger(rows)
    stage = Counter(str(row["stage_status"]) for row in materialized)
    source_counts = Counter(str(row["source_dataset"]) for row in materialized)
    family_counts = Counter(str(row["underlying_source_family"]) for row in materialized)
    blockers = Counter(
        str(code)
        for row in materialized
        for code in (row.get("blocking_reasons") or [])
    )
    positive = Counter()
    hard_negative = Counter()
    positive_families: dict[str, set[str]] = defaultdict(set)
    hard_negative_families: dict[str, set[str]] = defaultdict(set)
    sha_assets: dict[str, list[str]] = defaultdict(list)
    fingerprinted = 0
    for row in materialized:
        family = str(row["underlying_source_family"])
        for label in row.get("echo_labels") or []:
            positive[str(label)] += 1
            positive_families[str(label)].add(family)
        for label in row.get("hard_negative_for") or []:
            hard_negative[str(label)] += 1
            hard_negative_families[str(label)].add(family)
        sha_assets[str(row["media_sha256"])].append(str(row["ledger_asset_id"]))
        fp = row.get("canonical_fingerprint")
        if isinstance(fp, Mapping) and fp.get("vector_sha256"):
            fingerprinted += 1
    duplicate_groups = [
        {"sha256": digest, "asset_ids": sorted(asset_ids)}
        for digest, asset_ids in sha_assets.items()
        if len(asset_ids) > 1
    ]
    return {
        "schema_version": LEDGER_SUMMARY_SCHEMA,
        "entry_count": len(materialized),
        "ledger_sha256": stable_json_sha256(materialized),
        "stage_status_counts": dict(sorted(stage.items())),
        "source_asset_counts": dict(sorted(source_counts.items())),
        "underlying_source_family_counts": dict(sorted(family_counts.items())),
        "positive_counts": {label: positive[label] for label in TARGET_LABELS},
        "positive_underlying_source_family_counts": {
            label: len(positive_families[label]) for label in TARGET_LABELS
        },
        "hard_negative_counts": {label: hard_negative[label] for label in TARGET_LABELS},
        "hard_negative_underlying_source_family_counts": {
            label: len(hard_negative_families[label]) for label in TARGET_LABELS
        },
        "blocking_reason_counts": dict(sorted(blockers.items())),
        "canonical_fingerprint_count": fingerprinted,
        "canonical_fingerprint_missing_count": len(materialized) - fingerprinted,
        "exact_duplicate_sha256_group_count": len(duplicate_groups),
        "exact_duplicate_sha256_groups": sorted(duplicate_groups, key=lambda row: row["sha256"]),
    }
