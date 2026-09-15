#!/usr/bin/env python3
"""Materialize small public release-safe gap and confuser assets.

Raw media is written to a CI scratch/artifact directory, never committed to Git.
The repository receives hashes, probes, canonical fingerprints and license-page
evidence. Admission into a frozen corpus still requires governed semantics,
grouping, global deduplication and the corpus solidity gate.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from echo.data_foundry.canonical_fingerprints import canonical_audio_fingerprint
from echo.data_foundry.probe import probe_audio

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/data_foundry/gap_source_candidates.v1.json"
WIKIMEDIA_CONFUSERS = ROOT / "configs/data_foundry/wikimedia_confusers.v1.json"
BIGSOUNDBANK_CONFUSERS = ROOT / "configs/data_foundry/bigsoundbank_confusers.v1.json"
BIGSOUNDBANK_GLASS_EXPANSION = ROOT / "configs/data_foundry/bigsoundbank_glass_expansion.v1.json"
OUTPUT_ROOT = Path(os.environ.get("ECHO_GAP_ASSET_ROOT", ROOT / ".materialized-gap-assets"))
REPORT = ROOT / "MK1/mining-site/materialization/public-gap-assets-report.json"


def fetch(url: str, *, attempts: int = 6) -> tuple[bytes, str | None, str]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        request = Request(
            url,
            headers={
                "User-Agent": "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)",
                "Accept": "*/*",
            },
        )
        try:
            with urlopen(request, timeout=120) as response:  # nosec B310 - versioned public source evidence
                return response.read(), response.headers.get_content_type(), response.geturl()
        except HTTPError as exc:
            last_error = exc
            if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                raise
        except (URLError, TimeoutError) as exc:
            last_error = exc
        if attempt < attempts:
            time.sleep(min(20, 2 ** (attempt - 1)))
    raise RuntimeError(f"fetch failed after {attempts} attempts: {url}: {last_error}") from last_error


def extension_for(url: str, content_type: str | None) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac", ".aiff", ".aif"}:
        return suffix
    return mimetypes.guess_extension(content_type or "") or ".bin"


def license_marker_ok(source_id: str, expected_license: str, page_text: str) -> bool:
    lower = page_text.casefold()
    if source_id == "echo-bigsoundbank-cc0-gap-v1":
        return "cc0" in lower and ("public domain" in lower or "free and royalty-free" in lower)
    if expected_license.casefold() in {"public-domain", "public domain", "cc0"}:
        return "public domain" in lower or "cc0" in lower or "cc-zero" in lower
    if "cc-by-sa" in expected_license.casefold():
        return "share alike" in lower or "cc-by-sa" in lower or "attribution-share alike" in lower
    return False


def iter_assets(
    config: dict,
    wikimedia_confusers: dict,
    bigsoundbank_confusers: dict,
    bigsoundbank_glass_expansion: dict,
):
    for source_id in ("echo-bigsoundbank-cc0-gap-v1", "echo-wikimedia-fire-alarm-v1"):
        source = config["sources"][source_id]
        for target, rows in source["targets"].items():
            for row in rows:
                yield source_id, source, target, row

    source_id = str(wikimedia_confusers.get("source_dataset") or "")
    if source_id != "echo-wikimedia-fire-alarm-v1":
        raise ValueError(f"unsupported Wikimedia confuser source_dataset: {source_id}")
    source = config["sources"][source_id]
    for row in wikimedia_confusers.get("assets") or []:
        hard_negative_for = [str(value) for value in (row.get("hard_negative_for") or [])]
        if not hard_negative_for:
            raise ValueError(f"Wikimedia confuser missing hard_negative_for: {row.get('asset_key')}")
        yield source_id, source, hard_negative_for[0], row

    source_id = str(bigsoundbank_confusers.get("source_dataset") or "")
    if source_id != "echo-bigsoundbank-cc0-gap-v1":
        raise ValueError(f"unsupported BigSoundBank confuser source_dataset: {source_id}")
    source = config["sources"][source_id]
    for row in bigsoundbank_confusers.get("assets") or []:
        hard_negative_for = [str(value) for value in (row.get("hard_negative_for") or [])]
        if not hard_negative_for:
            raise ValueError(f"BigSoundBank confuser missing hard_negative_for: {row.get('asset_key')}")
        yield source_id, source, hard_negative_for[0], row

    source_id = str(bigsoundbank_glass_expansion.get("source_dataset") or "")
    target = str(bigsoundbank_glass_expansion.get("target") or "")
    if source_id != "echo-bigsoundbank-cc0-gap-v1":
        raise ValueError(f"unsupported BigSoundBank glass source_dataset: {source_id}")
    if target != "GLASS_SHATTER":
        raise ValueError(f"unsupported BigSoundBank glass target: {target}")
    source = config["sources"][source_id]
    for row in bigsoundbank_glass_expansion.get("assets") or []:
        if row.get("hard_negative_for"):
            raise ValueError(f"BigSoundBank glass positive cannot carry hard-negative role: {row.get('asset_key')}")
        if str(row.get("semantic") or "") != "glass_shatter":
            raise ValueError(f"BigSoundBank glass semantic drift: {row.get('asset_key')}")
        yield source_id, source, target, row


def main() -> int:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    wikimedia_confusers = json.loads(WIKIMEDIA_CONFUSERS.read_text(encoding="utf-8"))
    bigsoundbank_confusers = json.loads(BIGSOUNDBANK_CONFUSERS.read_text(encoding="utf-8"))
    bigsoundbank_glass_expansion = json.loads(BIGSOUNDBANK_GLASS_EXPANSION.read_text(encoding="utf-8"))
    if wikimedia_confusers.get("schema_version") != "echo.wikimedia-confusers.v1":
        raise SystemExit("unsupported Wikimedia confuser config schema")
    if bigsoundbank_confusers.get("schema_version") != "echo.bigsoundbank-confusers.v1":
        raise SystemExit("unsupported BigSoundBank confuser config schema")
    if bigsoundbank_glass_expansion.get("schema_version") != "echo.bigsoundbank-glass-expansion.v1":
        raise SystemExit("unsupported BigSoundBank glass expansion config schema")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    failures = []

    for source_id, source, target, row in iter_assets(
        config,
        wikimedia_confusers,
        bigsoundbank_confusers,
        bigsoundbank_glass_expansion,
    ):
        asset_key = str(row["asset_key"])
        page_url = str(row["url"])
        media_url = str(row["media_url"])
        expected_license = str(row.get("license") or ("CC0" if source_id == "echo-bigsoundbank-cc0-gap-v1" else "UNKNOWN"))
        hard_negative_for = sorted({str(value) for value in (row.get("hard_negative_for") or [])})
        try:
            page_bytes, _, resolved_page = fetch(page_url)
            page_text = page_bytes.decode("utf-8", errors="replace")
            if not license_marker_ok(source_id, expected_license, page_text):
                raise RuntimeError(f"license marker not confirmed for {asset_key}")

            media_bytes, content_type, resolved_media = fetch(media_url)
            suffix = extension_for(resolved_media, content_type)
            path = OUTPUT_ROOT / source_id / f"{asset_key}{suffix}"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(media_bytes)
            probe = probe_audio(path)
            if not probe.ok:
                raise RuntimeError(f"audio probe failed for {asset_key}: {probe.reason}")
            fingerprint = canonical_audio_fingerprint(path)

            rows.append({
                "asset_key": asset_key,
                "source_dataset": source_id,
                "target": target,
                "semantic": row.get("semantic"),
                "hard_negative_for": hard_negative_for,
                "recording_family": row.get("recording_family"),
                "license_id": expected_license,
                "page_url": page_url,
                "resolved_page_url": resolved_page,
                "page_sha256": hashlib.sha256(page_bytes).hexdigest(),
                "media_url": media_url,
                "resolved_media_url": resolved_media,
                "media_sha256": hashlib.sha256(media_bytes).hexdigest(),
                "size_bytes": len(media_bytes),
                "content_type": content_type,
                "local_relpath": str(path.relative_to(OUTPUT_ROOT)),
                "audio_probe": probe.to_dict(),
                "canonical_fingerprint": fingerprint,
                "admission_status": (
                    "CANDIDATE_REAL_BYTES_MATERIALIZED_GOVERNED_HARD_NEGATIVE"
                    if hard_negative_for
                    else "CANDIDATE_REAL_BYTES_MATERIALIZED_REVIEW_REQUIRED"
                ),
            })
        except Exception as exc:
            failures.append({
                "asset_key": asset_key,
                "source_dataset": source_id,
                "target": target,
                "hard_negative_for": hard_negative_for,
                "error": f"{type(exc).__name__}:{exc}",
            })

    payload = {
        "schema_version": "echo.public-gap-materialization-report.v2",
        "status": "PASS" if not failures else "PARTIAL",
        "materialized_count": len(rows),
        "fingerprinted_count": sum(1 for row in rows if row.get("canonical_fingerprint")),
        "failure_count": len(failures),
        "assets": sorted(rows, key=lambda value: (value["source_dataset"], value["target"], value["asset_key"])),
        "failures": failures,
        "certification_note": "Materialized bytes are candidates only. Explicit hard-negative roles remain governed by versioned config; exact BigSoundBank glass_shatter rows are governed positives only after canonical-ledger semantic admission; fingerprinting closes codec-normalized evidence capture, but grouping/global dedup/rights/coverage gates still control admission.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "materialized": len(rows), "fingerprinted": payload["fingerprinted_count"], "failures": len(failures)}, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
