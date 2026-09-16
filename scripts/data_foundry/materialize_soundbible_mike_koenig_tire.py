#!/usr/bin/env python3
"""Materialize the Mike Koenig / SoundBible tire-squeal evidence candidate.

This is deliberately evidence-only. It verifies origin and transport pages,
fetches the OpenGameArt derivative archive, extracts exactly one audio asset,
and records hashes, probe data and a codec-independent fingerprint. It does
not register the source in the canonical corpus or grant coverage credit.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from echo.data_foundry.canonical_fingerprints import canonical_audio_fingerprint
from echo.data_foundry.probe import probe_audio


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/data_foundry/soundbible_mike_koenig_tire.v1.json"
REPORT = ROOT / "MK1/mining-site/materialization/soundbible-mike-koenig-tire-materialization.json"
OUTPUT_ROOT = Path(
    os.environ.get(
        "ECHO_SOUNDBIBLE_TIRE_ROOT",
        ROOT / ".materialized-soundbible-mike-koenig-tire",
    )
)
USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"


def fetch(url: str, attempts: int = 6) -> tuple[bytes, str | None, str]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
        try:
            with urlopen(request, timeout=120) as response:  # nosec B310 - pinned public evidence URL
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


def require_markers(*, page_name: str, body: str, markers: list[str]) -> None:
    haystack = body.casefold()
    missing = [marker for marker in markers if marker.casefold() not in haystack]
    if missing:
        raise RuntimeError(f"{page_name} missing required evidence markers: {missing}")


def main() -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    if cfg.get("schema_version") != "echo.soundbible-mike-koenig-tire.v1":
        raise SystemExit("unsupported Mike Koenig tire manifest schema")
    if cfg.get("phase") != "EVIDENCE_MATERIALIZATION_ONLY":
        raise SystemExit("manifest phase must remain evidence-only")
    if cfg.get("target") != "TIRE_SQUEAL":
        raise SystemExit("unexpected target")
    if cfg.get("underlying_source_family_candidate") != "SOUNDBIBLE_MIKE_KOENIG":
        raise SystemExit("underlying source-family candidate drift")

    origin = cfg["origin"]
    transport = cfg["transport"]
    asset_cfg = cfg["asset"]
    if origin.get("declared_license") != "CC-BY-3.0" or transport.get("declared_license") != "CC-BY-3.0":
        raise SystemExit("both origin and transport evidence must agree on CC-BY-3.0")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    extract_root = OUTPUT_ROOT / "extracted"
    extract_root.mkdir(parents=True, exist_ok=True)

    origin_bytes, _, resolved_origin = fetch(str(origin["canonical_page"]))
    origin_text = origin_bytes.decode("utf-8", errors="replace")
    require_markers(page_name="SoundBible origin", body=origin_text, markers=list(origin["page_markers"]))

    transport_bytes, _, resolved_transport = fetch(str(transport["page"]))
    transport_text = transport_bytes.decode("utf-8", errors="replace")
    require_markers(page_name="OpenGameArt transport", body=transport_text, markers=list(transport["page_markers"]))

    archive_bytes, archive_content_type, resolved_archive = fetch(str(transport["archive_url"]))
    archive_path = OUTPUT_ROOT / "carskid.7z"
    archive_path.write_bytes(archive_bytes)
    subprocess.run(
        ["7z", "x", str(archive_path), f"-o{extract_root}", "-y"],
        check=True,
        cwd=OUTPUT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    allowed = {str(value).casefold() for value in asset_cfg.get("allowed_extensions") or []}
    audio_files = sorted(
        path for path in extract_root.rglob("*")
        if path.is_file() and path.suffix.casefold() in allowed
    )
    expected_count = int(asset_cfg["expected_audio_file_count"])
    if len(audio_files) != expected_count:
        raise RuntimeError(f"expected {expected_count} extracted audio file(s), found {len(audio_files)}")

    audio_path = audio_files[0]
    probe = probe_audio(audio_path)
    if not probe.ok:
        raise RuntimeError(f"audio probe failed: {probe.reason}")
    fingerprint = canonical_audio_fingerprint(audio_path)
    media_bytes = audio_path.read_bytes()

    payload = {
        "schema_version": "echo.soundbible-mike-koenig-tire-materialization.v1",
        "status": "PASS",
        "phase": "EVIDENCE_MATERIALIZED_NO_CORPUS_CREDIT",
        "target": "TIRE_SQUEAL",
        "source_id_candidate": cfg["source_id_candidate"],
        "underlying_source_family_candidate": cfg["underlying_source_family_candidate"],
        "creator": cfg["creator"],
        "license_id": "CC-BY-3.0",
        "origin": {
            "canonical_page": origin["canonical_page"],
            "resolved_page": resolved_origin,
            "page_sha256": hashlib.sha256(origin_bytes).hexdigest(),
            "markers_verified": list(origin["page_markers"]),
        },
        "transport": {
            "page": transport["page"],
            "resolved_page": resolved_transport,
            "page_sha256": hashlib.sha256(transport_bytes).hexdigest(),
            "markers_verified": list(transport["page_markers"]),
            "archive_url": transport["archive_url"],
            "resolved_archive_url": resolved_archive,
            "archive_content_type": archive_content_type,
            "archive_sha256": hashlib.sha256(archive_bytes).hexdigest(),
            "archive_size_bytes": len(archive_bytes),
        },
        "asset": {
            "asset_key": asset_cfg["asset_key"],
            "archive_member": str(audio_path.relative_to(extract_root)),
            "semantic_candidate": asset_cfg["semantic_candidate"],
            "recording_family_candidate": asset_cfg["recording_family_candidate"],
            "media_sha256": hashlib.sha256(media_bytes).hexdigest(),
            "size_bytes": len(media_bytes),
            "audio_probe": probe.to_dict(),
            "canonical_fingerprint": fingerprint,
            "admission_status": "DISCOVERY_REAL_BYTES_MATERIALIZED_REVIEW_REQUIRED",
        },
        "stop_lines": list(cfg["stop_lines"]),
        "certification_note": "PASS proves public origin/rights/bytes/probe/fingerprint evidence only. A later reviewed source registration and ledger admission is required before any corpus or coverage credit.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "asset": payload["asset"]["asset_key"],
        "duration_seconds": payload["asset"]["audio_probe"]["duration_seconds"],
        "archive_bytes": payload["transport"]["archive_size_bytes"],
        "media_bytes": payload["asset"]["size_bytes"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
