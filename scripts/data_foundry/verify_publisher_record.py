#!/usr/bin/env python3
"""Verify a pinned Zenodo release against Zenodo's public Records API.

This certifies publisher-declared release identity and file inventory/checksums.
It does NOT certify downloaded bytes; full acquisition later verifies the same
checksums against local files and computes per-asset SHA-256.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Mapping
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from echo.data_foundry.acquisition import load_acquisition_registry
from echo.data_foundry.source_policy import load_dataset_certification


USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"


def _zenodo_record_id(record_url: str) -> str:
    parsed = urlparse(record_url)
    if parsed.netloc != "zenodo.org" or "/records/" not in parsed.path:
        raise ValueError(f"not a pinned Zenodo record URL: {record_url!r}")
    record_id = parsed.path.rstrip("/").split("/")[-1]
    if not record_id.isdigit():
        raise ValueError(f"invalid Zenodo record id: {record_url!r}")
    return record_id


def _fetch_json(url: str, retries: int = 5) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urlopen(req, timeout=30) as response:
                payload = json.load(response)
            if not isinstance(payload, dict):
                raise ValueError("publisher API response is not a JSON object")
            return payload
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2**attempt, 10))
    raise RuntimeError(f"publisher API request failed after {retries} attempts: {url}") from last_error


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _normalize_md5(value: object) -> str | None:
    raw = str(value or "").strip().lower()
    if raw.startswith("md5:"):
        raw = raw[4:]
    if len(raw) == 32 and all(c in "0123456789abcdef" for c in raw):
        return raw
    return None


def _release_matches(expected: str, actual: object) -> bool:
    exp = expected.strip().lower().removeprefix("v")
    act = str(actual or "").strip().lower().removeprefix("v")
    if not act:
        # Immutable Zenodo record ID still pins the release; missing optional
        # version metadata is reported but does not create a false mismatch.
        return True
    return exp == act


def verify_source(
    *,
    source_id: str,
    acquisition_registry_path: str,
    certification_path: str,
) -> dict[str, Any]:
    acquisition = load_acquisition_registry(acquisition_registry_path)
    certification = load_dataset_certification(certification_path)

    source = acquisition["sources"].get(source_id)
    cert = certification["sources"].get(source_id)
    if not isinstance(source, dict) or not isinstance(cert, dict):
        raise KeyError(f"source is not present in both registries: {source_id}")

    record_url = str(source.get("record_url") or "")
    record_id = _zenodo_record_id(record_url)
    api_url = f"https://zenodo.org/api/records/{record_id}"
    payload = _fetch_json(api_url)

    if str(payload.get("id")) != record_id:
        raise ValueError(f"publisher record id mismatch: expected {record_id}, got {payload.get('id')!r}")
    if payload.get("status") not in {None, "published"}:
        raise ValueError(f"publisher record is not published: {payload.get('status')!r}")

    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    expected_release = str(cert.get("release") or "")
    actual_release = metadata.get("version")
    if expected_release and not _release_matches(expected_release, actual_release):
        raise ValueError(
            f"publisher version mismatch for {source_id}: expected {expected_release!r}, got {actual_release!r}"
        )

    publisher_files = payload.get("files")
    if not isinstance(publisher_files, list):
        raise ValueError("publisher record does not expose a file inventory")
    by_key: dict[str, dict[str, Any]] = {}
    for item in publisher_files:
        if isinstance(item, dict) and item.get("key"):
            by_key[str(item["key"])] = item

    expected_files = source.get("files")
    if not isinstance(expected_files, list) or not expected_files:
        raise ValueError(f"no certified file inventory configured for {source_id}")

    verified: list[dict[str, Any]] = []
    expected_names: set[str] = set()
    for entry in expected_files:
        if not isinstance(entry, dict):
            raise ValueError(f"invalid acquisition registry entry for {source_id}")
        name = str(entry.get("name") or "")
        expected_md5 = _normalize_md5(entry.get("md5"))
        if not name or not expected_md5:
            raise ValueError(f"file entry lacks a valid name/md5: {source_id}:{name!r}")
        expected_names.add(name)
        publisher = by_key.get(name)
        if publisher is None:
            raise ValueError(f"publisher record is missing configured file: {source_id}/{name}")
        publisher_md5 = _normalize_md5(publisher.get("checksum"))
        if publisher_md5 != expected_md5:
            raise ValueError(
                f"publisher checksum drift for {source_id}/{name}: configured {expected_md5}, publisher {publisher_md5}"
            )
        links = publisher.get("links") if isinstance(publisher.get("links"), dict) else {}
        verified.append({
            "name": name,
            "md5": expected_md5,
            "size_bytes": publisher.get("size"),
            "content_url": links.get("self") or links.get("content"),
            "required_for": sorted(str(v) for v in entry.get("required_for", [])),
        })

    publisher_names = set(by_key)
    if publisher_names != expected_names:
        missing_in_registry = sorted(publisher_names - expected_names)
        missing_at_publisher = sorted(expected_names - publisher_names)
        raise ValueError(
            "strict publisher inventory mismatch for "
            f"{source_id}: unregistered_publisher_files={missing_in_registry}, "
            f"missing_publisher_files={missing_at_publisher}"
        )

    evidence_payload = {
        "schema_version": "echo.publisher-record-evidence.v1",
        "source_id": source_id,
        "record_id": record_id,
        "record_url": record_url,
        "api_url": api_url,
        "doi": payload.get("doi") or metadata.get("doi"),
        "title": metadata.get("title"),
        "expected_release": expected_release,
        "publisher_version": actual_release,
        "publisher_status": payload.get("status"),
        "publisher_created": payload.get("created"),
        "publisher_updated": payload.get("updated") or payload.get("modified"),
        "publisher_record_canonical_sha256": _canonical_sha256(payload),
        "configured_file_count": len(expected_names),
        "publisher_file_count": len(publisher_names),
        "files": sorted(verified, key=lambda row: row["name"]),
        "status": "PASS",
        "scope": "publisher_release_identity_and_inventory_checksums_not_downloaded_bytes",
    }
    return evidence_payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_id")
    parser.add_argument("--acquisition-registry", default="configs/data_foundry/acquisition_registry.v1.json")
    parser.add_argument("--certification", default="configs/data_foundry/dataset_certification.v1.json")
    parser.add_argument("--report")
    args = parser.parse_args()

    result = verify_source(
        source_id=args.source_id,
        acquisition_registry_path=args.acquisition_registry,
        certification_path=args.certification,
    )
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.report:
        output = Path(args.report)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
