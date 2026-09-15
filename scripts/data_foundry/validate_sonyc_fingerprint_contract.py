#!/usr/bin/env python3
"""Fail-closed validator for durable SONYC canonical fingerprint evidence.

SONYC materialization fingerprints are ``echo.canonical-audio-fingerprint.v1``
payloads. Their canonical digest fields are ``vector_sha256`` and
``canonical_pcm_sha256``; there is deliberately no generic ``digest`` field.

This validator protects the source-materialization -> durable-candidate contract
before evidence is committed. It also verifies that summary counts describe the
unique ledger-relevant acoustic assets rather than the number of semantic rows,
because a polyphonic asset may appear in both target and confuser candidate
files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from echo.data_foundry.canonical_fingerprints import (
    FINGERPRINT_ALGORITHM,
    FINGERPRINT_SCHEMA_VERSION,
)

SUMMARY_SCHEMA_VERSION = "echo.sonyc-full-materialization-summary.v2"
TARGET_FILE = "sonyc-v2.3-target-candidates.jsonl"
CONFUSER_FILE = "sonyc-v2.3-confuser-candidates.jsonl"
SUMMARY_FILE = "sonyc-v2.3-full-materialization-summary.json"


def _is_sha256(value: object) -> bool:
    text = str(value or "").lower()
    return len(text) == 64 and all(ch in "0123456789abcdef" for ch in text)


def validate_fingerprint(payload: object) -> list[str]:
    """Return contract violations for one canonical fingerprint payload."""

    if not isinstance(payload, Mapping):
        return ["canonical_fingerprint must be an object"]

    errors: list[str] = []
    if payload.get("schema_version") != FINGERPRINT_SCHEMA_VERSION:
        errors.append(
            f"fingerprint schema must be {FINGERPRINT_SCHEMA_VERSION}, got {payload.get('schema_version')!r}"
        )
    if payload.get("algorithm") != FINGERPRINT_ALGORITHM:
        errors.append(
            f"fingerprint algorithm must be {FINGERPRINT_ALGORITHM}, got {payload.get('algorithm')!r}"
        )

    canonical_pcm_sha256 = payload.get("canonical_pcm_sha256")
    vector_sha256 = payload.get("vector_sha256")
    if not _is_sha256(canonical_pcm_sha256):
        errors.append("canonical_pcm_sha256 must be a SHA-256 hex digest")
    if not _is_sha256(vector_sha256):
        errors.append("vector_sha256 must be a SHA-256 hex digest")

    bins = payload.get("bins")
    levels = payload.get("levels")
    vector = payload.get("vector")
    if not isinstance(bins, int) or isinstance(bins, bool) or bins <= 0:
        errors.append("bins must be a positive integer")
    if not isinstance(levels, int) or isinstance(levels, bool) or not 2 <= levels <= 255:
        errors.append("levels must be an integer in [2, 255]")
    if not isinstance(vector, list):
        errors.append("vector must be a list")
    elif isinstance(bins, int) and not isinstance(bins, bool) and len(vector) != bins:
        errors.append(f"vector length {len(vector)} does not match bins {bins}")
    if isinstance(vector, list) and isinstance(levels, int) and not isinstance(levels, bool):
        for index, value in enumerate(vector):
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= levels:
                errors.append(f"vector[{index}] must be an integer in [0, {levels}]")
                break
        if not errors or all(not item.startswith("vector[") for item in errors):
            if all(isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 255 for value in vector):
                actual = hashlib.sha256(bytes(vector)).hexdigest()
                if _is_sha256(vector_sha256) and actual != vector_sha256:
                    errors.append("vector_sha256 does not match vector bytes")

    decoded_sample_count = payload.get("decoded_sample_count")
    if (
        not isinstance(decoded_sample_count, int)
        or isinstance(decoded_sample_count, bool)
        or decoded_sample_count <= 0
    ):
        errors.append("decoded_sample_count must be a positive integer")

    decode = payload.get("canonical_decode")
    if not isinstance(decode, Mapping):
        errors.append("canonical_decode must be an object")
    else:
        if decode.get("channels") != 1:
            errors.append("canonical_decode.channels must be 1")
        sample_rate = decode.get("sample_rate_hz")
        if not isinstance(sample_rate, int) or isinstance(sample_rate, bool) or sample_rate <= 0:
            errors.append("canonical_decode.sample_rate_hz must be a positive integer")
        if decode.get("sample_format") != "s16le":
            errors.append("canonical_decode.sample_format must be 's16le'")

    return errors


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line:
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path.name}:{line_number}: row must be an object")
            rows.append(value)
    return rows


def validate_materialization(root: Path) -> dict[str, int]:
    """Validate SONYC v2 durable candidate fingerprint closure.

    Raises ``ValueError`` on the first fail-closed aggregate of violations.
    Returns compact counts when the contract is satisfied.
    """

    summary_path = root / SUMMARY_FILE
    target_path = root / TARGET_FILE
    confuser_path = root / CONFUSER_FILE
    for path in (summary_path, target_path, confuser_path):
        if not path.is_file():
            raise ValueError(f"required SONYC evidence missing: {path.name}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("schema_version") != SUMMARY_SCHEMA_VERSION:
        raise ValueError(
            f"expected {SUMMARY_SCHEMA_VERSION}, got {summary.get('schema_version')!r}"
        )
    if int(summary.get("fingerprint_failures") or 0) != 0:
        raise ValueError("SONYC summary reports fingerprint_failures > 0")

    rows_by_file = {
        TARGET_FILE: _load_jsonl(target_path),
        CONFUSER_FILE: _load_jsonl(confuser_path),
    }
    expected_counts = {
        TARGET_FILE: int(summary.get("target_candidate_count") or 0),
        CONFUSER_FILE: int(summary.get("confuser_candidate_count") or 0),
    }

    errors: list[str] = []
    unique_assets: dict[tuple[str, str, str], Mapping[str, Any]] = {}
    checked = 0

    for filename, rows in rows_by_file.items():
        if len(rows) != expected_counts[filename]:
            errors.append(
                f"{filename}: row count {len(rows)} != summary count {expected_counts[filename]}"
            )
        for line_number, row in enumerate(rows, 1):
            checked += 1
            source_dataset = str(row.get("source_dataset") or "")
            source_asset_id = str(row.get("source_asset_id") or "")
            media_sha256 = str(row.get("sha256") or "")
            if not source_dataset or not source_asset_id or not _is_sha256(media_sha256):
                errors.append(f"{filename}:{line_number}: invalid asset identity")
                continue

            fingerprint = row.get("canonical_fingerprint")
            fp_errors = validate_fingerprint(fingerprint)
            for message in fp_errors:
                errors.append(f"{filename}:{line_number}: {message}")
            if row.get("fingerprint_error") not in (None, ""):
                errors.append(f"{filename}:{line_number}: fingerprint_error must be empty")

            key = (source_dataset, source_asset_id, media_sha256)
            previous = unique_assets.get(key)
            if previous is not None and previous != fingerprint:
                errors.append(
                    f"{filename}:{line_number}: conflicting fingerprint for duplicate semantic row {source_asset_id}"
                )
            elif isinstance(fingerprint, Mapping):
                unique_assets[key] = fingerprint

    expected_unique = int(summary.get("fingerprinted_ledger_relevant_assets") or 0)
    if len(unique_assets) != expected_unique:
        errors.append(
            "unique fingerprinted ledger-relevant assets "
            f"{len(unique_assets)} != summary count {expected_unique}"
        )

    if errors:
        preview = errors[:12]
        suffix = "" if len(errors) <= len(preview) else f" (+{len(errors) - len(preview)} more)"
        raise ValueError("SONYC fingerprint contract failed: " + " | ".join(preview) + suffix)

    return {
        "candidate_rows_checked": checked,
        "unique_ledger_relevant_assets": len(unique_assets),
        "target_candidate_rows": len(rows_by_file[TARGET_FILE]),
        "confuser_candidate_rows": len(rows_by_file[CONFUSER_FILE]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--materialization-dir",
        default="MK1/mining-site/materialization",
        help="Directory containing SONYC durable evidence files",
    )
    args = parser.parse_args()
    try:
        report = validate_materialization(Path(args.materialization_dir))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps({"status": "PASS", **report}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
