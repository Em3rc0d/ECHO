#!/usr/bin/env python3
"""Materialize public-domain Freesound previews for exact ECHO gap candidates.

Only live pages that explicitly state Creative Commons 0 are eligible. The
script downloads the public preview representation, never a login-gated
original. Every preview is hashed and technically probed. Semantic/grouping
review remains required before corpus admission.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import html
import json
import os
from pathlib import Path
import re
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from echo.data_foundry.probe import probe_audio

ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = ROOT / "MK1/mining-site/materialization/freesound-gap-discovery.json"
SUPPLEMENTAL = ROOT / "configs/data_foundry/freesound_cc0_supplemental.v1.json"
OUTPUT_ROOT = Path(os.environ.get("ECHO_FREESOUND_CC0_ROOT", ROOT / ".materialized-freesound-cc0"))
REPORT = ROOT / "MK1/mining-site/materialization/freesound-cc0-gap-assets-report.json"


def fetch(url: str, *, attempts: int = 5) -> tuple[bytes, str | None, str]:
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
            with urlopen(request, timeout=90) as response:  # nosec B310 - public evidence URLs only
                return response.read(), response.headers.get_content_type(), response.geturl()
        except HTTPError as exc:
            last_error = exc
            if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                raise
        except (URLError, TimeoutError) as exc:
            last_error = exc
        if attempt < attempts:
            time.sleep(min(12, 2 ** (attempt - 1)))
    raise RuntimeError(f"fetch failed after {attempts} attempts: {url}: {last_error}") from last_error


def is_cc0_page(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text).casefold()
    return (
        "creative commons 0" in normalized
        or "creativecommons.org/publicdomain/zero/1.0" in normalized
        or "cc0 1.0" in normalized
    )


def preview_urls(page_text: str, page_url: str) -> list[str]:
    decoded = html.unescape(page_text).replace("\\/", "/")
    patterns = [
        r"https://cdn\.freesound\.org/previews/[^\"'<> ]+?\.(?:mp3|ogg)",
        r"https://freesound\.org/data/previews/[^\"'<> ]+?\.(?:mp3|ogg)",
        r"//cdn\.freesound\.org/previews/[^\"'<> ]+?\.(?:mp3|ogg)",
        r"/data/previews/[^\"'<> ]+?\.(?:mp3|ogg)",
    ]
    found: list[str] = []
    for pattern in patterns:
        for raw in re.findall(pattern, decoded, flags=re.IGNORECASE):
            url = raw
            if url.startswith("//"):
                url = "https:" + url
            elif url.startswith("/"):
                url = urljoin(page_url, url)
            if url not in found:
                found.append(url)
    found.sort(key=lambda value: ("-hq." not in value, not value.endswith(".mp3"), value))
    return found


def page_title(text: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return re.sub(r"\s+", " ", html.unescape(match.group(1))).strip()


def candidate_map() -> dict[int, dict[str, Any]]:
    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    supplemental = json.loads(SUPPLEMENTAL.read_text(encoding="utf-8"))
    result: dict[int, dict[str, Any]] = {}
    for target, row in discovery["targets"].items():
        for sound_id in row["discovered_unique_asset_ids"]:
            result[int(sound_id)] = {
                "sound_id": int(sound_id),
                "target": target,
                "semantic": "exact_taxonomy_candidate_review_required",
                "recording_family": None,
                "origin": "FreesoundDataset_exact_category",
            }
    for target, rows in supplemental["targets"].items():
        for row in rows:
            sound_id = int(row["sound_id"])
            existing = result.setdefault(
                sound_id,
                {
                    "sound_id": sound_id,
                    "target": target,
                    "semantic": row["semantic"],
                    "recording_family": row["recording_family"],
                    "origin": "supplemental_public_search",
                },
            )
            existing["target"] = target
            existing["semantic"] = row["semantic"]
            existing["recording_family"] = row["recording_family"]
            if existing.get("origin") != "FreesoundDataset_exact_category":
                existing["origin"] = "supplemental_public_search"
    return result


def materialize_one(candidate: dict[str, Any]) -> dict[str, Any]:
    sound_id = int(candidate["sound_id"])
    target = str(candidate["target"])
    page_url = f"https://freesound.org/s/{sound_id}/"
    page_bytes, _, resolved_page = fetch(page_url)
    text = page_bytes.decode("utf-8", errors="replace")
    base = {
        **candidate,
        "source_dataset": "echo-freesound-cc0-gap-v1",
        "page_url": page_url,
        "resolved_page_url": resolved_page,
        "page_sha256": hashlib.sha256(page_bytes).hexdigest(),
        "page_title": page_title(text),
        "license_id": "CC0" if is_cc0_page(text) else "NOT_CC0",
    }
    if not is_cc0_page(text):
        return {**base, "status": "METADATA_ONLY_NON_CC0_OR_UNCONFIRMED"}

    previews = preview_urls(text, resolved_page)
    if not previews:
        return {**base, "status": "CC0_PAGE_NO_PUBLIC_PREVIEW_URL_FOUND"}

    last_error = None
    for media_url in previews:
        try:
            media_bytes, content_type, resolved_media = fetch(media_url)
            suffix = Path(resolved_media).suffix.lower()
            if suffix not in {".mp3", ".ogg"}:
                suffix = ".mp3" if content_type == "audio/mpeg" else ".ogg"
            path = OUTPUT_ROOT / target / f"freesound-{sound_id}{suffix}"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(media_bytes)
            probe = probe_audio(path)
            if not probe.ok:
                path.unlink(missing_ok=True)
                last_error = f"AUDIO_PROBE_FAILED:{probe.reason}"
                continue
            return {
                **base,
                "status": "CC0_REAL_PREVIEW_MATERIALIZED_REVIEW_REQUIRED",
                "media_url": media_url,
                "resolved_media_url": resolved_media,
                "content_type": content_type,
                "media_sha256": hashlib.sha256(media_bytes).hexdigest(),
                "size_bytes": len(media_bytes),
                "local_relpath": str(path.relative_to(OUTPUT_ROOT)),
                "audio_probe": probe.to_dict(),
                "grouping_status": "REVIEW_REQUIRED",
            }
        except Exception as exc:
            last_error = f"{type(exc).__name__}:{exc}"
    return {**base, "status": "CC0_PREVIEW_FETCH_OR_PROBE_FAILED", "error": last_error}


def main() -> int:
    candidates = candidate_map()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        future_map = {pool.submit(materialize_one, row): sound_id for sound_id, row in candidates.items()}
        for future in as_completed(future_map):
            sound_id = future_map[future]
            try:
                rows.append(future.result())
            except Exception as exc:
                rows.append({
                    **candidates[sound_id],
                    "source_dataset": "echo-freesound-cc0-gap-v1",
                    "status": "PAGE_FETCH_FAILED",
                    "error": f"{type(exc).__name__}:{exc}",
                })

    materialized = [row for row in rows if row["status"] == "CC0_REAL_PREVIEW_MATERIALIZED_REVIEW_REQUIRED"]
    by_target = {}
    for target in ("FIRE_ALARM", "TIRE_SQUEAL"):
        target_rows = [row for row in rows if row.get("target") == target]
        target_materialized = [row for row in materialized if row.get("target") == target]
        by_target[target] = {
            "candidate_count": len(target_rows),
            "cc0_materialized_count": len(target_materialized),
            "materialized_duration_seconds": round(sum(float((row.get("audio_probe") or {}).get("duration_seconds") or 0.0) for row in target_materialized), 6),
            "status_counts": {
                status: sum(1 for row in target_rows if row.get("status") == status)
                for status in sorted({str(row.get("status")) for row in target_rows})
            },
        }

    payload = {
        "schema_version": "echo.freesound-cc0-materialization-report.v1",
        "source_dataset": "echo-freesound-cc0-gap-v1",
        "candidate_count": len(rows),
        "materialized_count": len(materialized),
        "targets": by_target,
        "assets": sorted(rows, key=lambda row: (str(row.get("target")), int(row.get("sound_id", 0)))),
        "certification_note": "Only CC0 public previews are materialized. All assets remain review/group/dedup candidates and are not automatically admitted positives.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"candidates": len(rows), "materialized": len(materialized), "targets": by_target}, sort_keys=True))
    return 0 if materialized else 2


if __name__ == "__main__":
    raise SystemExit(main())
