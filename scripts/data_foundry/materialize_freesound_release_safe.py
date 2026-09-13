#!/usr/bin/env python3
"""Materialize release-safe Freesound previews for exact ECHO candidates.

Eligible rights are deliberately narrow: CC0/public-domain or attribution-only
CC-BY. NC, Sampling+, ShareAlike and unknown terms fail closed. Candidate
semantics come from FSD50K exact ground truth, FreesoundDataset exact-category
evidence, or explicitly curated supplemental records. Real previews are hashed
and probed but remain pre-admission evidence until global Foundry gates pass.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import html
import json
import os
from pathlib import Path
import re
import threading
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from echo.data_foundry.probe import probe_audio

ROOT = Path(__file__).resolve().parents[1]
FSD = ROOT / "MK1/mining-site/materialization/fsd50k-exact-freesound-candidates.json"
DISCOVERY = ROOT / "MK1/mining-site/materialization/freesound-gap-discovery.json"
SUPPLEMENTAL = ROOT / "configs/data_foundry/freesound_cc0_supplemental.v1.json"
BOUNDARY = ROOT / "configs/data_foundry/free_tier_boundary.v1.json"
OUTPUT_ROOT = Path(os.environ.get("ECHO_FREESOUND_RELEASE_SAFE_ROOT", ROOT / ".materialized-freesound-release-safe"))
REPORT = ROOT / "MK1/mining-site/materialization/freesound-release-safe-materialization.json"
USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"
_LOCK = threading.Lock()
_WRITTEN_BYTES = 0


def fetch(url: str, attempts: int = 5) -> tuple[bytes, str | None, str]:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
        try:
            with urlopen(request, timeout=90) as response:  # nosec B310 - public evidence URLs
                return response.read(), response.headers.get_content_type(), response.geturl()
        except HTTPError as exc:
            last = exc
            if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                raise
        except (URLError, TimeoutError) as exc:
            last = exc
        if attempt < attempts:
            time.sleep(min(12, 2 ** (attempt - 1)))
    raise RuntimeError(f"fetch failed after {attempts} attempts: {url}: {last}") from last


def classify_license(text: str) -> str | None:
    normalized = html.unescape(text).replace("\\/", "/").casefold()
    # Reject restricted families before checking generic BY markers.
    if "creativecommons.org/licenses/by-nc" in normalized or "attribution noncommercial" in normalized:
        return None
    if "sampling+" in normalized or "sampling plus" in normalized:
        return None
    if "creativecommons.org/licenses/by-sa" in normalized or "attribution-share alike" in normalized:
        return None
    if "creativecommons.org/publicdomain/zero/1.0" in normalized or "creative commons 0" in normalized or "cc0 1.0" in normalized:
        return "CC0"
    match = re.search(r"creativecommons\.org/licenses/by/(\d+(?:\.\d+)?)", normalized)
    if match:
        version = match.group(1)
        return f"CC-BY-{version}"
    # Historical Freesound pages sometimes render only the license title.
    if "attribution license" in normalized and "noncommercial" not in normalized and "share alike" not in normalized:
        return "CC-BY"
    return None


def previews(page_text: str, page_url: str) -> list[str]:
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
    return re.sub(r"\s+", " ", html.unescape(match.group(1))).strip() if match else None


def merge_candidate(result: dict[int, dict[str, Any]], sound_id: int, *, target: str, provenance: str, semantic_status: str, semantic: str | None = None, recording_family: str | None = None, fsd_labels: list[str] | None = None, fsd_split: str | None = None) -> None:
    row = result.setdefault(sound_id, {
        "sound_id": sound_id,
        "targets": [],
        "provenance": [],
        "semantic_status_by_target": {},
        "semantic_by_target": {},
        "recording_family_by_target": {},
        "fsd50k_labels": fsd_labels or [],
        "fsd50k_split": fsd_split,
    })
    row["targets"] = sorted(set(row["targets"]) | {target})
    row["provenance"] = sorted(set(row["provenance"]) | {provenance})
    row["semantic_status_by_target"][target] = semantic_status
    if semantic:
        row["semantic_by_target"][target] = semantic
    if recording_family:
        row["recording_family_by_target"][target] = recording_family
    if fsd_labels:
        row["fsd50k_labels"] = sorted(set(row.get("fsd50k_labels") or []) | set(fsd_labels))
    if fsd_split:
        row["fsd50k_split"] = fsd_split


def candidate_map() -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    if FSD.is_file():
        payload = json.loads(FSD.read_text(encoding="utf-8"))
        for row in payload.get("candidates", []):
            sid = int(row["sound_id"])
            for target in row.get("targets", []):
                merge_candidate(
                    result, sid, target=str(target),
                    provenance="FSD50K_v1.0_exact_ground_truth",
                    semantic_status="EXACT_FSD50K_GROUND_TRUTH",
                    fsd_labels=list(row.get("fsd50k_labels") or []),
                    fsd_split=row.get("fsd50k_split"),
                )

    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    for target, cfg in discovery.get("targets", {}).items():
        for sid in cfg.get("discovered_unique_asset_ids", []):
            merge_candidate(
                result, int(sid), target=str(target),
                provenance="FreesoundDataset_exact_category",
                semantic_status="EXACT_CATEGORY_REVIEW_REQUIRED",
                semantic="exact_taxonomy_candidate_review_required",
            )

    supplemental = json.loads(SUPPLEMENTAL.read_text(encoding="utf-8"))
    for target, rows in supplemental.get("targets", {}).items():
        for row in rows:
            merge_candidate(
                result, int(row["sound_id"]), target=str(target),
                provenance="ECHO_curated_supplemental",
                semantic_status=("EXACT_CURATED" if str(row.get("semantic")) in {"fire_alarm", "tire_squeal"} else "REVIEW_REQUIRED"),
                semantic=row.get("semantic"), recording_family=row.get("recording_family"),
            )
    return result


def reserve_bytes(size: int, limit: int) -> None:
    global _WRITTEN_BYTES
    with _LOCK:
        if _WRITTEN_BYTES + size > limit:
            raise RuntimeError("free-tier Freesound scratch budget would be exceeded")
        _WRITTEN_BYTES += size


def materialize_one(candidate: dict[str, Any], limit: int) -> dict[str, Any]:
    sid = int(candidate["sound_id"])
    page_url = f"https://freesound.org/s/{sid}/"
    page_bytes, _, resolved_page = fetch(page_url)
    text = page_bytes.decode("utf-8", errors="replace")
    license_id = classify_license(text)
    base = {
        **candidate,
        "source_dataset": "echo-freesound-release-safe-v1",
        "page_url": page_url,
        "resolved_page_url": resolved_page,
        "page_sha256": hashlib.sha256(page_bytes).hexdigest(),
        "page_title": page_title(text),
        "license_id": license_id or "NOT_RELEASE_SAFE_OR_UNCONFIRMED",
    }
    if not license_id:
        return {**base, "status": "RIGHTS_NOT_RELEASE_SAFE_OR_UNCONFIRMED"}
    candidates = previews(text, resolved_page)
    if not candidates:
        return {**base, "status": "RELEASE_SAFE_PAGE_NO_PUBLIC_PREVIEW"}
    last_error = None
    for media_url in candidates:
        try:
            media, content_type, resolved_media = fetch(media_url)
            reserve_bytes(len(media), limit)
            suffix = Path(resolved_media).suffix.lower()
            if suffix not in {".mp3", ".ogg"}:
                suffix = ".mp3" if content_type == "audio/mpeg" else ".ogg"
            path = OUTPUT_ROOT / f"freesound-{sid}{suffix}"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(media)
            probe = probe_audio(path)
            if not probe.ok:
                path.unlink(missing_ok=True)
                last_error = f"AUDIO_PROBE_FAILED:{probe.reason}"
                continue
            return {
                **base,
                "status": "RELEASE_SAFE_REAL_PREVIEW_MATERIALIZED",
                "media_url": media_url,
                "resolved_media_url": resolved_media,
                "media_sha256": hashlib.sha256(media).hexdigest(),
                "size_bytes": len(media),
                "content_type": content_type,
                "local_relpath": path.name,
                "audio_probe": probe.to_dict(),
            }
        except Exception as exc:
            last_error = f"{type(exc).__name__}:{exc}"
    return {**base, "status": "RELEASE_SAFE_PREVIEW_FETCH_OR_PROBE_FAILED", "error": last_error}


def main() -> int:
    policy = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    limit = int(policy["github_actions"]["project_max_working_set_bytes"])
    candidates = candidate_map()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(materialize_one, row, limit): sid for sid, row in candidates.items()}
        for future in as_completed(futures):
            sid = futures[future]
            try:
                rows.append(future.result())
            except Exception as exc:
                rows.append({**candidates[sid], "sound_id": sid, "source_dataset": "echo-freesound-release-safe-v1", "status": "MATERIALIZATION_FAILED", "error": f"{type(exc).__name__}:{exc}"})

    materialized = [row for row in rows if row.get("status") == "RELEASE_SAFE_REAL_PREVIEW_MATERIALIZED"]
    target_summary = {}
    for target in ("GLASS_SHATTER", "SIREN", "FIRE_ALARM", "VEHICLE_HORN", "TIRE_SQUEAL"):
        all_target = [row for row in rows if target in (row.get("targets") or [])]
        target_media = [row for row in materialized if target in (row.get("targets") or [])]
        exact_fsd = [row for row in target_media if row.get("semantic_status_by_target", {}).get(target) == "EXACT_FSD50K_GROUND_TRUTH"]
        exact_curated = [row for row in target_media if row.get("semantic_status_by_target", {}).get(target) == "EXACT_CURATED"]
        target_summary[target] = {
            "candidate_count": len(all_target),
            "release_safe_real_preview_count": len(target_media),
            "exact_fsd50k_ground_truth_real_preview_count": len(exact_fsd),
            "exact_curated_real_preview_count": len(exact_curated),
            "materialized_duration_seconds": round(sum(float((row.get("audio_probe") or {}).get("duration_seconds") or 0.0) for row in target_media), 6),
            "license_counts": {license_id: sum(1 for row in target_media if row.get("license_id") == license_id) for license_id in sorted({str(row.get("license_id")) for row in target_media})},
        }

    payload = {
        "schema_version": "echo.freesound-release-safe-materialization.v1",
        "status": "PASS" if materialized else "FAIL_NO_RELEASE_SAFE_MEDIA",
        "candidate_count": len(rows),
        "materialized_count": len(materialized),
        "materialized_bytes": sum(int(row.get("size_bytes") or 0) for row in materialized),
        "working_set_limit_bytes": limit,
        "targets": target_summary,
        "assets": sorted(rows, key=lambda row: int(row.get("sound_id", 0))),
        "certification_boundary": "Current Freesound page rights and real public preview bytes were verified. Exact FSD50K ground-truth candidates have strong label provenance; category/supplemental candidates retain their explicit review status. Final admission, uploader/recording grouping, dedup, split and corpus coverage remain Foundry responsibilities.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "candidate_count": len(rows), "materialized_count": len(materialized), "targets": target_summary}, sort_keys=True))
    return 0 if materialized else 2


if __name__ == "__main__":
    raise SystemExit(main())
