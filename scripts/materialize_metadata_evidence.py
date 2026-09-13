#!/usr/bin/env python3
"""Materialize publisher metadata + exact-gap discovery evidence in hosted CI.

This job intentionally does not download multi-GB audio. It produces immutable
publisher-checksum evidence and exact candidate identities so full-media
execution on persistent storage starts from a closed source graph.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ACQ = ROOT / "configs/data_foundry/acquisition_registry.v1.json"
GAPS = ROOT / "configs/data_foundry/gap_source_candidates.v1.json"
OUT = ROOT / "MK1/mining-site/materialization"


def get(url: str, *, attempts: int = 7) -> bytes:
    """Fetch public evidence with bounded retry for transient publisher errors."""
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
            print(f"fetch [{attempt}/{attempts}] {url}", flush=True)
            with urlopen(request, timeout=180) as response:  # nosec B310 - URLs are versioned public evidence
                return response.read()
        except HTTPError as exc:
            last_error = exc
            if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                raise
        except (URLError, TimeoutError) as exc:
            last_error = exc
        if attempt < attempts:
            time.sleep(min(30, 2 ** (attempt - 1)))
    raise RuntimeError(f"public evidence fetch failed after {attempts} attempts: {url}: {last_error}") from last_error


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()  # nosec B303 - publisher checksum compatibility


def materialize_metadata() -> dict:
    registry = json.loads(ACQ.read_text(encoding="utf-8"))
    files = []
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for source_id, source in registry["sources"].items():
            record_url = str(source.get("record_url") or "")
            if "zenodo.org/records/" not in record_url:
                continue
            for row in source.get("files", []):
                if "metadata" not in (row.get("required_for") or []):
                    continue
                name = str(row["name"])
                url = f"{record_url.rstrip('/')}/files/{name}?download=1"
                data = get(url)
                target = tmpdir / source_id / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                actual = md5_bytes(data)
                expected = str(row.get("md5") or "")
                ok = actual.casefold() == expected.casefold()
                if not ok:
                    raise RuntimeError(f"checksum mismatch {source_id}/{name}: {actual} != {expected}")
                files.append({
                    "source_id": source_id,
                    "name": name,
                    "url": url,
                    "size_bytes": len(data),
                    "md5_expected": expected,
                    "md5_actual": actual,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "status": "PASS",
                })
    return {
        "schema_version": "echo.metadata-materialization-evidence.v1",
        "status": "PASS",
        "files": files,
    }


def scrape_freesound_exact_candidates() -> dict:
    gaps = json.loads(GAPS.read_text(encoding="utf-8"))
    source = gaps["sources"]["echo-freesound-exact-gap-v1"]
    targets = {}
    for target, cfg in source["targets"].items():
        ids: set[int] = set()
        snapshots = []
        for page in range(1, int(cfg["pages"]) + 1):
            url = str(cfg["explorer_base"]) + f"?page={page}"
            data = get(url)
            text = data.decode("utf-8", errors="replace")
            page_ids = {int(v) for v in re.findall(r"freesound\.org/s/(\d+)", text)}
            ids.update(page_ids)
            snapshots.append({
                "page": page,
                "url": url,
                "sha256": hashlib.sha256(data).hexdigest(),
                "discovered_ids": sorted(page_ids),
            })
        targets[target] = {
            "expected_candidate_count": cfg["expected_candidate_count"],
            "expected_ground_truth_count": cfg["expected_ground_truth_count"],
            "discovered_unique_asset_ids": sorted(ids),
            "discovered_unique_count": len(ids),
            "page_snapshots": snapshots,
            "status": (
                "PASS_DISCOVERY" if len(ids) >= int(cfg["expected_candidate_count"])
                else "PARTIAL_DISCOVERY_REVIEW_REQUIRED"
            ),
        }
    return {
        "schema_version": "echo.gap-candidate-discovery-evidence.v1",
        "source_id": "echo-freesound-exact-gap-v1",
        "targets": targets,
        "admission_status": "NOT_ADMITTED_MEDIA_NOT_ACQUIRED",
    }


def verify_explicit_gap_pages() -> dict:
    gaps = json.loads(GAPS.read_text(encoding="utf-8"))
    source = gaps["sources"]["echo-bigsoundbank-cc0-gap-v1"]
    targets = {}
    for target, rows in source["targets"].items():
        evidence = []
        for row in rows:
            data = get(str(row["url"]))
            text = data.decode("utf-8", errors="replace")
            cc0 = "CC0" in text or "public domain" in text.lower()
            evidence.append({
                **row,
                "page_sha256": hashlib.sha256(data).hexdigest(),
                "cc0_marker_present": cc0,
                "status": "PASS_PAGE_EVIDENCE" if cc0 else "REVIEW_REQUIRED",
            })
        targets[target] = evidence
    return {
        "schema_version": "echo.gap-page-evidence.v1",
        "source_id": "echo-bigsoundbank-cc0-gap-v1",
        "targets": targets,
        "admission_status": "NOT_ADMITTED_MEDIA_NOT_ACQUIRED",
    }


def write_json(name: str, payload: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    write_json("publisher-metadata-materialization.json", materialize_metadata())
    write_json("freesound-gap-discovery.json", scrape_freesound_exact_candidates())
    write_json("bigsoundbank-gap-page-evidence.json", verify_explicit_gap_pages())
    print("metadata materialization evidence: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
