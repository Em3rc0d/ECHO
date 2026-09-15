#!/usr/bin/env python3
"""Materialize evidence-only OpenGameArt GLASS candidates for MK1 closure.

This discovery step deliberately grants zero corpus credit. Canonical OpenGameArt
pages prove rights/provenance; direct files/archives are transport. Archive rows
whose names merely mention glass stay review-only until a separate semantic
admission change explicitly proves break/shatter intent.
"""

from __future__ import annotations

import hashlib
from html import unescape
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import time
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import zipfile

from echo.data_foundry.canonical_fingerprints import canonical_audio_fingerprint
from echo.data_foundry.probe import probe_audio

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/data_foundry/opengameart_glass_expansion.v1.json"
REPORT = ROOT / "MK1/mining-site/materialization/opengameart-glass-expansion-materialization.json"
OUTPUT_ROOT = Path(
    os.environ.get(
        "ECHO_OPENGAMEART_GLASS_EXPANSION_ROOT",
        ROOT / ".materialized-opengameart-glass-expansion",
    )
)
USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"
AUDIO_SUFFIXES = {".wav", ".ogg", ".mp3", ".flac", ".aiff", ".aif", ".m4a", ".aac"}
MAX_ARCHIVE_BYTES = 20_000_000
MAX_UNCOMPRESSED_BYTES = 120_000_000
MAX_ARCHIVE_MEMBERS = 1000


def fetch(url: str, *, attempts: int = 6) -> tuple[bytes, str | None, str]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
        try:
            with urlopen(request, timeout=120) as response:  # nosec B310 - governed public evidence URLs
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


def normalize_html_text(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", unescape(text)).strip().casefold()


def validate_config(config: Mapping[str, Any]) -> None:
    if config.get("schema_version") != "echo.opengameart-glass-expansion.v1":
        raise ValueError("unsupported OpenGameArt glass expansion schema")
    if config.get("target") != "GLASS_SHATTER":
        raise ValueError("OpenGameArt glass expansion target drift")
    if config.get("phase") != "EVIDENCE_DISCOVERY_ONLY":
        raise ValueError("OpenGameArt glass expansion must remain discovery-only")

    sources = config.get("sources")
    if not isinstance(sources, list) or len(sources) != 3:
        raise ValueError("OpenGameArt glass expansion requires exactly three governed sources")
    seen: set[str] = set()
    for source in sources:
        if not isinstance(source, Mapping):
            raise ValueError("source row must be an object")
        source_id = str(source.get("source_id") or "")
        if not source_id or source_id in seen:
            raise ValueError(f"missing or duplicate source_id: {source_id}")
        seen.add(source_id)
        if source.get("declared_license") != "CC0":
            raise ValueError(f"source must remain CC0: {source_id}")
        page = urlparse(str(source.get("canonical_source_page") or ""))
        if page.scheme != "https" or page.netloc.casefold() != "opengameart.org":
            raise ValueError(f"canonical source page must be HTTPS OpenGameArt: {source_id}")
        if not str(source.get("creator") or ""):
            raise ValueError(f"creator missing: {source_id}")
        family = str(source.get("underlying_source_family_candidate") or "")
        if not family.startswith("OPENGAMEART_"):
            raise ValueError(f"invalid source-family candidate: {source_id}")
        markers = source.get("page_markers")
        if not isinstance(markers, list) or not markers:
            raise ValueError(f"page markers missing: {source_id}")

        kind = source.get("kind")
        if kind == "direct_audio":
            media = urlparse(str(source.get("media_url") or ""))
            if media.scheme != "https" or media.netloc.casefold() != "opengameart.org":
                raise ValueError("direct audio must use HTTPS OpenGameArt transport")
            if source.get("semantic_candidate") != "glass_shatter":
                raise ValueError("Till Behrend direct row must remain explicit glass_shatter candidate")
            if not str(source.get("recording_family_candidate") or ""):
                raise ValueError("direct audio recording-family candidate missing")
        elif kind == "zip_glass_discovery":
            archive = urlparse(str(source.get("archive_url") or ""))
            if archive.scheme != "https" or archive.netloc.casefold() != "opengameart.org" or not archive.path.casefold().endswith(".zip"):
                raise ValueError(f"archive must be an HTTPS OpenGameArt ZIP: {source_id}")
            if int(source.get("minimum_glass_named_audio_entries") or 0) < 1:
                raise ValueError(f"glass-named discovery floor missing: {source_id}")
            governance = source.get("governance")
            if not isinstance(governance, Mapping):
                raise ValueError(f"archive governance missing: {source_id}")
            required_true = {
                "glass_named_files_are_review_candidates_only",
                "filename_glass_alone_does_not_prove_break_or_shatter",
                "recording_group_credit_forbidden_in_discovery",
            }
            if any(governance.get(key) is not True for key in required_true):
                raise ValueError(f"archive discovery stop-line weakened: {source_id}")
        else:
            raise ValueError(f"unsupported source kind: {kind}")


def page_evidence(source: Mapping[str, Any], page_bytes: bytes, resolved_url: str) -> dict[str, Any]:
    text = normalize_html_text(page_bytes.decode("utf-8", errors="replace"))
    missing = [marker for marker in source["page_markers"] if str(marker).casefold() not in text]
    if missing:
        raise ValueError(f"canonical page markers missing for {source['source_id']}: {missing}")
    return {
        "url": source["canonical_source_page"],
        "resolved_url": resolved_url,
        "page_sha256": hashlib.sha256(page_bytes).hexdigest(),
        "creator": source["creator"],
        "license_id": source["declared_license"],
        "markers_pass": True,
    }


def safe_glass_members(archive_bytes: bytes, minimum_count: int) -> tuple[list[zipfile.ZipInfo], int, int]:
    if len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise ValueError("OpenGameArt archive exceeds bounded compressed-size limit")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        infos = archive.infolist()
    if len(infos) > MAX_ARCHIVE_MEMBERS:
        raise ValueError("OpenGameArt archive member count exceeds bounded limit")

    selected: list[zipfile.ZipInfo] = []
    seen: set[str] = set()
    uncompressed = 0
    audio_count = 0
    for info in infos:
        name = info.filename.replace("\\", "/")
        path = PurePosixPath(name)
        if info.is_dir():
            continue
        if path.is_absolute() or ".." in path.parts or not path.name:
            raise ValueError(f"unsafe archive member path: {name}")
        if name in seen:
            raise ValueError(f"duplicate archive member path: {name}")
        seen.add(name)
        if info.flag_bits & 0x1:
            raise ValueError(f"encrypted archive member is not allowed: {name}")
        uncompressed += int(info.file_size)
        if uncompressed > MAX_UNCOMPRESSED_BYTES:
            raise ValueError("OpenGameArt archive exceeds bounded uncompressed-size limit")
        if path.suffix.casefold() in AUDIO_SUFFIXES:
            audio_count += 1
            if "glass" in name.casefold():
                selected.append(info)

    if len(selected) < minimum_count:
        raise ValueError(f"glass-named audio count {len(selected)} below governed floor {minimum_count}")
    return sorted(selected, key=lambda item: item.filename.casefold()), audio_count, uncompressed


def materialize_bytes(source: Mapping[str, Any], source_asset_id: str, media_bytes: bytes, suffix: str) -> dict[str, Any]:
    source_dir = OUTPUT_ROOT / str(source["source_id"])
    source_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(source_asset_id).name)
    path = source_dir / safe_name
    if not path.suffix and suffix:
        path = path.with_suffix(suffix)
    path.write_bytes(media_bytes)
    probe = probe_audio(path)
    if not probe.ok:
        raise RuntimeError(f"audio probe failed for {source_asset_id}: {probe.reason}")
    fingerprint = canonical_audio_fingerprint(path)
    return {
        "source_id": source["source_id"],
        "source_asset_id": source_asset_id,
        "underlying_source_family_candidate": source["underlying_source_family_candidate"],
        "license_id": "CC0",
        "media_sha256": hashlib.sha256(media_bytes).hexdigest(),
        "size_bytes": len(media_bytes),
        "audio_probe": probe.to_dict(),
        "canonical_fingerprint": fingerprint,
    }


def materialize_direct(source: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    media_bytes, content_type, resolved_url = fetch(str(source["media_url"]))
    parsed = urlparse(resolved_url)
    if parsed.scheme != "https" or parsed.netloc.casefold() != "opengameart.org":
        raise ValueError("direct OpenGameArt media resolved off governed host")
    row = materialize_bytes(source, str(source["expected_filename"]), media_bytes, Path(parsed.path).suffix.lower())
    row.update({
        "role": "positive_candidate",
        "target": "GLASS_SHATTER",
        "semantic_candidate": source["semantic_candidate"],
        "recording_family_candidate": source["recording_family_candidate"],
        "content_type": content_type,
        "transport_url": source["media_url"],
        "resolved_transport_url": resolved_url,
        "admission_status": "REAL_BYTES_MATERIALIZED_SEPARATE_ADMISSION_REQUIRED",
    })
    return [row], {
        "kind": "direct_audio",
        "media_sha256": row["media_sha256"],
        "resolved_transport_url": resolved_url,
        "source_credit": False,
    }


def materialize_archive(source: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    archive_bytes, content_type, resolved_url = fetch(str(source["archive_url"]))
    parsed = urlparse(resolved_url)
    if parsed.scheme != "https" or parsed.netloc.casefold() != "opengameart.org":
        raise ValueError("OpenGameArt archive resolved off governed host")
    minimum = int(source["minimum_glass_named_audio_entries"])
    selected, audio_count, uncompressed = safe_glass_members(archive_bytes, minimum)
    rows: list[dict[str, Any]] = []
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        for info in selected:
            member = info.filename.replace("\\", "/")
            row = materialize_bytes(source, member, archive.read(info), PurePosixPath(member).suffix.casefold())
            row.update({
                "role": "glass_named_review_candidate",
                "target": "GLASS_SHATTER",
                "semantic_candidate": "glass_named_filename_review_required",
                "recording_family_candidate": None,
                "archive_member_crc32": f"{info.CRC:08x}",
                "admission_status": "DISCOVERY_REVIEW_ONLY_NO_CORPUS_CREDIT",
            })
            rows.append(row)
    return rows, {
        "kind": "zip_glass_discovery",
        "archive_sha256": hashlib.sha256(archive_bytes).hexdigest(),
        "archive_size_bytes": len(archive_bytes),
        "archive_uncompressed_size_bytes": uncompressed,
        "archive_audio_entry_count": audio_count,
        "glass_named_audio_entry_count": len(rows),
        "content_type": content_type,
        "resolved_transport_url": resolved_url,
        "source_credit": False,
    }


def duplicate_groups(rows: list[Mapping[str, Any]], key_path: tuple[str, ...]) -> list[list[str]]:
    grouped: dict[str, list[str]] = {}
    for row in rows:
        value: Any = row
        for key in key_path:
            value = value.get(key) if isinstance(value, Mapping) else None
        if value:
            grouped.setdefault(str(value), []).append(f"{row['source_id']}:{row['source_asset_id']}")
    return sorted((sorted(values) for values in grouped.values() if len(values) > 1), key=lambda values: values[0])


def main() -> int:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    validate_config(config)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, Any]] = []
    sources_report: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for source in config["sources"]:
        source_id = str(source["source_id"])
        try:
            page_bytes, _, resolved_page = fetch(str(source["canonical_source_page"]))
            canonical = page_evidence(source, page_bytes, resolved_page)
            if source["kind"] == "direct_audio":
                rows, transport = materialize_direct(source)
            else:
                rows, transport = materialize_archive(source)
            all_rows.extend(rows)
            sources_report.append({
                "source_id": source_id,
                "source_family_candidate": source["underlying_source_family_candidate"],
                "canonical_source_evidence": canonical,
                "transport_evidence": transport,
                "materialized_count": len(rows),
                "fingerprinted_count": sum(
                    1
                    for row in rows
                    if isinstance(row.get("canonical_fingerprint"), Mapping)
                    and row["canonical_fingerprint"].get("vector_sha256")
                    and row["canonical_fingerprint"].get("canonical_pcm_sha256")
                ),
                "status": "PASS",
            })
        except Exception as exc:
            failures.append({"source_id": source_id, "error": f"{type(exc).__name__}:{exc}"})

    exact_media_duplicates = duplicate_groups(all_rows, ("media_sha256",))
    canonical_pcm_duplicates = duplicate_groups(all_rows, ("canonical_fingerprint", "canonical_pcm_sha256"))
    fingerprinted = sum(
        1
        for row in all_rows
        if isinstance(row.get("canonical_fingerprint"), Mapping)
        and row["canonical_fingerprint"].get("vector_sha256")
        and row["canonical_fingerprint"].get("canonical_pcm_sha256")
    )
    direct_count = sum(1 for row in all_rows if row["role"] == "positive_candidate")
    review_count = sum(1 for row in all_rows if row["role"] == "glass_named_review_candidate")
    status = "PASS" if not failures and len(sources_report) == len(config["sources"]) and fingerprinted == len(all_rows) else "PARTIAL"

    payload = {
        "schema_version": "echo.opengameart-glass-expansion-materialization.v1",
        "status": status,
        "target": "GLASS_SHATTER",
        "phase": "EVIDENCE_DISCOVERY_ONLY",
        "source_count": len(sources_report),
        "materialized_count": len(all_rows),
        "fingerprinted_count": fingerprinted,
        "explicit_positive_candidate_count": direct_count,
        "glass_named_review_candidate_count": review_count,
        "sources": sorted(sources_report, key=lambda row: row["source_id"]),
        "exact_media_sha256_duplicate_groups": exact_media_duplicates,
        "canonical_pcm_sha256_duplicate_groups": canonical_pcm_duplicates,
        "assets": sorted(all_rows, key=lambda row: (row["source_id"], str(row["source_asset_id"]).casefold())),
        "failures": failures,
        "certification_stop_line": (
            "PASS proves canonical CC0 page markers, real bytes, safe archive inspection, audio probes and canonical fingerprints only. "
            "Only the Till Behrend direct row is an explicit positive candidate. Generic glass-named archive rows remain semantic review-only. "
            "No row receives ledger/split/coverage/source-diversity credit until a separate reviewed admission change passes all downstream gates."
        ),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "materialized": len(all_rows),
        "fingerprinted": fingerprinted,
        "explicit_positive_candidates": direct_count,
        "glass_named_review_candidates": review_count,
        "exact_media_duplicate_groups": len(exact_media_duplicates),
        "canonical_pcm_duplicate_groups": len(canonical_pcm_duplicates),
        "failures": len(failures),
    }, sort_keys=True))
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
