#!/usr/bin/env python3
"""Materialize Signature Sounds CC0 smashed-glass evidence for MK1.

The Signature Sounds page is the canonical provenance/rights authority.
MediaFire is transport only and never receives source-family credit. The first
run is intentionally evidence-discovery only: it records the exact ZIP hash,
archive members, per-WAV hashes, probes and canonical fingerprints so a later
review can pin the archive before any ledger admission is possible.
"""

from __future__ import annotations

import base64
import hashlib
from html import unescape
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import time
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
import zipfile

from echo.data_foundry.canonical_fingerprints import canonical_audio_fingerprint
from echo.data_foundry.probe import probe_audio

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/data_foundry/signature_sounds_glass_cc0.v1.json"
REPORT = ROOT / "MK1/mining-site/materialization/signature-sounds-glass-cc0-materialization.json"
OUTPUT_ROOT = Path(
    os.environ.get(
        "ECHO_SIGNATURE_SOUNDS_GLASS_ROOT",
        ROOT / ".materialized-signature-sounds-glass",
    )
)
USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/152.0.0.0 Safari/537.36"
)
MAX_ARCHIVE_BYTES = 25_000_000
MAX_UNCOMPRESSED_BYTES = 100_000_000
MAX_ARCHIVE_MEMBERS = 500


class _MediaFireDownloadButtonParser(HTMLParser):
    """Collect only values attached to MediaFire's public download button."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.values: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() != "a":
            return
        values = {str(key).casefold(): str(value or "") for key, value in attrs}
        is_download_button = (
            values.get("id", "").casefold() == "downloadbutton"
            or values.get("aria-label", "").casefold() == "download file"
        )
        if not is_download_button:
            return
        for attribute in ("href", "data-scrambled-url"):
            value = values.get(attribute, "").strip()
            if value:
                self.values.append((attribute, value))


def fetch(
    url: str,
    *,
    attempts: int = 6,
    user_agent: str = USER_AGENT,
    referer: str | None = None,
) -> tuple[bytes, str | None, str]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        headers = {"User-Agent": user_agent, "Accept": "*/*"}
        if referer:
            headers["Referer"] = referer
        request = Request(url, headers=headers)
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
    if config.get("schema_version") != "echo.signature-sounds-glass-cc0.v1":
        raise ValueError("unsupported Signature Sounds config schema")
    if config.get("source_id") != "echo-signature-sounds-glass-cc0-v1":
        raise ValueError("Signature Sounds source_id drift")
    if config.get("declared_license") != "CC0":
        raise ValueError("Signature Sounds acquisition must remain CC0")
    if config.get("target") != "GLASS_SHATTER":
        raise ValueError("Signature Sounds target drift")
    if config.get("underlying_source_family_candidate") != "SIGNATURE_SOUNDS":
        raise ValueError("Signature Sounds family drift")
    if not str(config.get("recording_family") or ""):
        raise ValueError("Signature Sounds conservative recording family missing")

    governance = config.get("governance")
    if not isinstance(governance, Mapping):
        raise ValueError("Signature Sounds governance missing")
    if int(governance.get("minimum_audio_entries") or 0) < 40:
        raise ValueError("Signature Sounds minimum audio entry floor weakened")
    if governance.get("all_audio_entries_share_one_recording_family_until_stronger_session_evidence_exists") is not True:
        raise ValueError("Signature Sounds conservative grouping stop-line weakened")
    if governance.get("corpus_admission_forbidden_until_archive_sha256_is_pinned") is not True:
        raise ValueError("Signature Sounds archive pin stop-line weakened")

    transport = config.get("acquisition_transport")
    if not isinstance(transport, Mapping):
        raise ValueError("Signature Sounds transport missing")
    if transport.get("source_credit") is not False:
        raise ValueError("MediaFire transport must not receive source credit")
    landing = str(transport.get("landing_page") or "")
    parsed = urlparse(landing)
    if parsed.scheme != "https" or parsed.netloc.casefold() != "www.mediafire.com":
        raise ValueError("Signature Sounds transport landing page must be the governed MediaFire HTTPS page")
    expected = transport.get("expected_archive_sha256")
    if expected is not None and not re.fullmatch(r"[0-9a-f]{64}", str(expected)):
        raise ValueError("expected_archive_sha256 must be null for discovery or an exact SHA-256")


def canonical_page_evidence_ok(page_text: str) -> tuple[bool, list[str]]:
    normalized = normalize_html_text(page_text)
    required = {
        "PACK_MARKER_MISSING": "smashed glass one-shots",
        "CC0_MARKER_MISSING": "cc0",
        "COUNT_MARKER_MISSING": "40+ smashed glass one-shots",
        "RECORDED_MARKER_MISSING": "recorded with high-quality equipment",
        "WAV_MARKER_MISSING": "high-quality wav format",
    }
    missing = [code for code, marker in required.items() if marker not in normalized]
    return not missing, missing


def _validate_mediafire_direct_zip_url(raw_url: str) -> str:
    candidate = unescape(raw_url).replace("\\/", "/").strip()
    if candidate.startswith("//"):
        candidate = "https:" + candidate
    parsed = urlparse(candidate)
    host = (parsed.hostname or "").casefold()
    if parsed.scheme.casefold() != "https":
        raise ValueError("MediaFire direct URL must use HTTPS")
    if not host.startswith("download") or not host.endswith(".mediafire.com"):
        raise ValueError("MediaFire direct URL host is outside the governed download CDN")
    if ".zip" not in unquote(parsed.path).casefold():
        raise ValueError("MediaFire direct URL is not the governed ZIP asset")
    return candidate


def _decode_scrambled_mediafire_url(value: str) -> str:
    cleaned = unescape(value).strip()
    padding = "=" * (-len(cleaned) % 4)
    try:
        decoded = base64.b64decode(cleaned + padding, validate=True).decode("utf-8")
    except Exception as exc:
        raise ValueError("invalid MediaFire scrambled download URL") from exc
    return decoded


def direct_mediafire_download_url(landing_html: str) -> str:
    """Resolve only MediaFire's own public direct-download button representations."""

    decoded = unescape(landing_html).replace("\\/", "/")
    parser = _MediaFireDownloadButtonParser()
    parser.feed(decoded)

    candidates: list[str] = []
    for attribute, value in parser.values:
        if attribute == "data-scrambled-url":
            try:
                candidates.append(_decode_scrambled_mediafire_url(value))
            except ValueError:
                continue
        else:
            candidates.append(value)

    # MediaFire has historically emitted a JS variable for the same public
    # download-button destination. It is still validated against the exact CDN.
    candidates.extend(
        match.group(1)
        for match in re.finditer(
            r"\bkNO\s*=\s*[\"'](https?://[^\"']+)[\"']",
            decoded,
            flags=re.IGNORECASE,
        )
    )

    # Final compatibility fallback: accept a literal direct CDN URL anywhere
    # in the public landing page, but never an arbitrary off-domain URL.
    candidates.extend(
        re.findall(
            r"https://download[^\"'<>\s]+\.mediafire\.com/[^\"'<>\s]+",
            decoded,
            flags=re.IGNORECASE,
        )
    )

    for candidate in candidates:
        try:
            return _validate_mediafire_direct_zip_url(candidate)
        except ValueError:
            continue
    raise ValueError("MediaFire public download button did not expose a governed direct ZIP URL")


def safe_audio_members(archive_bytes: bytes, minimum_count: int) -> tuple[list[zipfile.ZipInfo], list[str], int]:
    if len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise ValueError("Signature Sounds archive exceeds bounded acquisition limit")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        infos = archive.infolist()
    if len(infos) > MAX_ARCHIVE_MEMBERS:
        raise ValueError("Signature Sounds archive member count exceeds bounded limit")

    audio: list[zipfile.ZipInfo] = []
    ignored: list[str] = []
    seen: set[str] = set()
    uncompressed = 0
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
            raise ValueError("Signature Sounds archive exceeds bounded uncompressed limit")
        if path.suffix.casefold() == ".wav":
            audio.append(info)
        else:
            ignored.append(name)

    if len(audio) < minimum_count:
        raise ValueError(f"Signature Sounds audio count {len(audio)} below governed floor {minimum_count}")
    return sorted(audio, key=lambda info: info.filename.casefold()), sorted(ignored), uncompressed


def duplicate_groups(rows: list[Mapping[str, Any]], key: str) -> list[list[str]]:
    grouped: dict[str, list[str]] = {}
    for row in rows:
        value = str(row.get(key) or "")
        if value:
            grouped.setdefault(value, []).append(str(row["source_asset_id"]))
    return sorted((sorted(values) for values in grouped.values() if len(values) > 1), key=lambda values: values[0])


def materialize_archive(config: Mapping[str, Any], archive_bytes: bytes) -> tuple[list[dict[str, Any]], list[str], int, list[dict[str, str]]]:
    minimum_count = int(config["governance"]["minimum_audio_entries"])
    audio_members, ignored, uncompressed = safe_audio_members(archive_bytes, minimum_count)
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        for index, info in enumerate(audio_members, 1):
            source_asset_id = info.filename.replace("\\", "/")
            try:
                media_bytes = archive.read(info)
                path = OUTPUT_ROOT / f"{index:04d}-{Path(source_asset_id).name}"
                path.write_bytes(media_bytes)
                probe = probe_audio(path)
                if not probe.ok:
                    raise RuntimeError(f"audio probe failed: {probe.reason}")
                fingerprint = canonical_audio_fingerprint(path)
                rows.append({
                    "source_asset_id": source_asset_id,
                    "source_dataset_candidate": config["source_id"],
                    "underlying_source_family_candidate": config["underlying_source_family_candidate"],
                    "role": "positive_candidate",
                    "target": config["target"],
                    "semantic": config["positive_semantic"],
                    "recording_family": config["recording_family"],
                    "license_id": "CC0",
                    "media_sha256": hashlib.sha256(media_bytes).hexdigest(),
                    "size_bytes": len(media_bytes),
                    "archive_member_crc32": f"{info.CRC:08x}",
                    "audio_probe": probe.to_dict(),
                    "canonical_fingerprint": fingerprint,
                    "admission_status": "REAL_BYTES_MATERIALIZED_ARCHIVE_PIN_REQUIRED",
                })
            except Exception as exc:
                failures.append({
                    "source_asset_id": source_asset_id,
                    "error": f"{type(exc).__name__}:{exc}",
                })
    return rows, ignored, uncompressed, failures


def main() -> int:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    validate_config(config)

    source_page_bytes, _, resolved_source_page = fetch(str(config["canonical_source_page"]))
    source_page_text = source_page_bytes.decode("utf-8", errors="replace")
    source_ok, missing_markers = canonical_page_evidence_ok(source_page_text)
    if not source_ok:
        raise SystemExit(
            "Signature Sounds canonical rights/provenance evidence failed closed: "
            + ",".join(missing_markers)
        )

    landing_url = str(config["acquisition_transport"]["landing_page"])
    landing_bytes, _, resolved_landing = fetch(
        landing_url,
        user_agent=BROWSER_USER_AGENT,
        referer=str(config["canonical_source_page"]),
    )
    landing_text = landing_bytes.decode("utf-8", errors="replace")
    direct_url = direct_mediafire_download_url(landing_text)
    archive_bytes, content_type, resolved_archive = fetch(
        direct_url,
        user_agent=BROWSER_USER_AGENT,
        referer=resolved_landing,
    )
    resolved_direct = _validate_mediafire_direct_zip_url(resolved_archive)
    archive_sha256 = hashlib.sha256(archive_bytes).hexdigest()
    expected_sha256 = config["acquisition_transport"].get("expected_archive_sha256")
    if expected_sha256 is not None and archive_sha256 != str(expected_sha256):
        raise SystemExit("Signature Sounds archive SHA-256 drift from pinned manifest")

    rows, ignored, uncompressed, failures = materialize_archive(config, archive_bytes)
    fingerprinted = sum(
        1
        for row in rows
        if isinstance(row.get("canonical_fingerprint"), Mapping)
        and row["canonical_fingerprint"].get("vector_sha256")
        and row["canonical_fingerprint"].get("canonical_pcm_sha256")
    )
    exact_media_duplicates = duplicate_groups(rows, "media_sha256")
    pcm_rows = [
        {
            "source_asset_id": row["source_asset_id"],
            "canonical_pcm_sha256": (row.get("canonical_fingerprint") or {}).get("canonical_pcm_sha256"),
        }
        for row in rows
    ]
    canonical_pcm_duplicates = duplicate_groups(pcm_rows, "canonical_pcm_sha256")
    minimum_count = int(config["governance"]["minimum_audio_entries"])
    status = "PASS" if not failures and len(rows) >= minimum_count and fingerprinted == len(rows) else "PARTIAL"

    payload = {
        "schema_version": "echo.signature-sounds-glass-materialization.v1",
        "source_id": config["source_id"],
        "source_family_candidate": config["underlying_source_family_candidate"],
        "target": config["target"],
        "status": status,
        "canonical_source_evidence": {
            "url": config["canonical_source_page"],
            "resolved_url": resolved_source_page,
            "page_sha256": hashlib.sha256(source_page_bytes).hexdigest(),
            "license_id": config["declared_license"],
            "markers_pass": source_ok,
        },
        "transport_evidence": {
            "landing_page": landing_url,
            "resolved_landing_page": resolved_landing,
            "landing_page_sha256": hashlib.sha256(landing_bytes).hexdigest(),
            "resolved_archive_url": resolved_direct,
            "resolved_archive_host": urlparse(resolved_direct).netloc,
            "content_type": content_type,
            "source_credit": False,
        },
        "archive_evidence": {
            "archive_sha256": archive_sha256,
            "expected_archive_sha256": expected_sha256,
            "pin_status": "PINNED_MATCH" if expected_sha256 is not None else "DISCOVERED_UNPINNED",
            "size_bytes": len(archive_bytes),
            "uncompressed_size_bytes": uncompressed,
            "audio_entry_count": len(rows) + len(failures),
            "ignored_non_audio_entries": ignored,
        },
        "materialized_count": len(rows),
        "fingerprinted_count": fingerprinted,
        "positive_candidate_count": len(rows),
        "positive_candidate_group_count": 1 if rows else 0,
        "recording_family": config["recording_family"],
        "exact_media_sha256_duplicate_groups": exact_media_duplicates,
        "canonical_pcm_sha256_duplicate_groups": canonical_pcm_duplicates,
        "assets": sorted(rows, key=lambda row: str(row["source_asset_id"]).casefold()),
        "failures": failures,
        "certification_stop_line": (
            "PASS proves canonical CC0/source markers, public archive acquisition, per-WAV bytes/probe/fingerprint and conservative one-family grouping. "
            "DISCOVERED_UNPINNED evidence grants zero ledger/split/coverage credit. The exact archive SHA-256 must be pinned in the manifest before a separate admission change may run."
        ),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "archive_sha256": archive_sha256,
        "archive_pin_status": payload["archive_evidence"]["pin_status"],
        "materialized": len(rows),
        "fingerprinted": fingerprinted,
        "exact_media_duplicate_groups": len(exact_media_duplicates),
        "canonical_pcm_duplicate_groups": len(canonical_pcm_duplicates),
        "failures": len(failures),
    }, sort_keys=True))
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
