#!/usr/bin/env python3
"""Inspect pinned FSD50K metadata/ground-truth bundles without full audio.

This does not claim corpus admission. It produces a deterministic compact view
of the release metadata so per-asset, free-tier acquisition can be designed
without materializing the >10 GiB multipart audio archives.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import time
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "configs/data_foundry/acquisition_registry.v1.json"
SOURCE_ID = "fsd50k-1.0"
USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"
TOKENS = ("siren", "horn", "shatter", "glass", "fire alarm", "fire_alarm", "tire", "tyre", "squeal")


def file_hash(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def publisher_url(record_url: str, filename: str) -> str:
    parsed = urlparse(record_url)
    record_id = parsed.path.rstrip("/").split("/")[-1]
    return f"https://zenodo.org/api/records/{record_id}/files/{quote(filename, safe='')}/content"


def download(url: str, target: Path, attempts: int = 5) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=180) as response, target.open("wb") as out:  # nosec B310 - pinned public publisher URL
                shutil.copyfileobj(response, out, length=1024 * 1024)
            return
        except Exception as exc:
            last = exc
            target.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(min(20, 2 ** attempt))
    raise RuntimeError(f"download failed: {url}: {last}") from last


def compact_csv_evidence(zf: zipfile.ZipFile, member: str) -> dict:
    raw = zf.read(member)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    reader = csv.DictReader(io.StringIO(text))
    headers = list(reader.fieldnames or [])
    rows = []
    matches = []
    unique_matching_values: set[str] = set()
    row_count = 0
    for row in reader:
        row_count += 1
        if len(rows) < 3:
            rows.append({key: row.get(key) for key in headers[:12]})
        joined = " | ".join(str(row.get(key) or "") for key in headers)
        if any(token in joined.casefold() for token in TOKENS):
            if len(matches) < 500:
                matches.append({key: row.get(key) for key in headers[:20]})
            for value in row.values():
                text_value = str(value or "").strip()
                if any(token in text_value.casefold() for token in TOKENS):
                    unique_matching_values.add(text_value)
    return {
        "member": member,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "row_count": row_count,
        "headers": headers,
        "sample_rows": rows,
        "target_keyword_match_count_capped": len(matches),
        "target_keyword_matching_values": sorted(unique_matching_values)[:500],
        "target_keyword_rows": matches,
    }


def inspect_zip(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        members = sorted(zf.namelist())
        csv_members = [name for name in members if name.casefold().endswith(".csv")]
        csv_evidence = [compact_csv_evidence(zf, name) for name in csv_members]
        return {
            "archive_name": path.name,
            "archive_sha256": file_hash(path, "sha256"),
            "member_count": len(members),
            "members": members,
            "csv_evidence": csv_evidence,
        }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    source = registry["sources"][SOURCE_ID]
    entries = {row["name"]: row for row in source["files"]}
    work = Path(args.work_root)
    work.mkdir(parents=True, exist_ok=True)
    bundle_rows = []
    archive_evidence = []
    for name in ("FSD50K.ground_truth.zip", "FSD50K.metadata.zip"):
        target = work / name
        download(publisher_url(source["record_url"], name), target)
        expected = str(entries[name]["md5"]).lower()
        actual = file_hash(target, "md5")
        if actual.lower() != expected:
            raise SystemExit(f"publisher MD5 mismatch {name}: {actual} != {expected}")
        bundle_rows.append({
            "name": name,
            "publisher_md5": expected,
            "actual_md5": actual,
            "sha256": file_hash(target, "sha256"),
            "size_bytes": target.stat().st_size,
            "status": "PASS",
        })
        archive_evidence.append(inspect_zip(target))
    payload = {
        "schema_version": "echo.fsd50k-metadata-inspection.v1",
        "status": "PASS",
        "source_id": SOURCE_ID,
        "source_release": "1.0",
        "publisher_bundles": bundle_rows,
        "archives": archive_evidence,
        "interpretation": "Metadata/ground-truth evidence only. Full FSD50K audio is not materialized because the multipart dev set exceeds ECHO-FREE-TIER-001. Any per-asset acquisition path must independently verify current rights/media and cannot inflate source diversity through duplicate upstream assets.",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "archives": len(archive_evidence), "output_bytes": output.stat().st_size}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
