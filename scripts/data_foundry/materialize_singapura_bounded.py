#!/usr/bin/env python3
"""Materialize the useful SINGA:PURA v1.0a subset within ECHO-FREE-TIER-001.

All multipart publisher archives are verified, but only recordings carrying
ECHO exact targets or explicit hard-negative labels are extracted. The script
pre-computes the selected uncompressed footprint from 7z metadata and fails
before extraction if the 10 GiB project working-set ceiling would be exceeded.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import time
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "configs/data_foundry/acquisition_registry.v1.json"
BOUNDARY = ROOT / "configs/data_foundry/free_tier_boundary.v1.json"
SOURCE_ID = "singapura-v1.0a"
USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"

TARGET_CODES = {
    "3-1": "GLASS_SHATTER",
    "5-1": "VEHICLE_HORN",
    "5-3": "SIREN",
}
CONFUSER_CODES = {
    "5-2": ["SIREN", "FIRE_ALARM"],
    "5-4": ["SIREN", "FIRE_ALARM"],
    "12-1": ["TIRE_SQUEAL"],
    "0-1": ["TIRE_SQUEAL"],
    "3-0": ["GLASS_SHATTER"],
}


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def publisher_url(record_url: str, filename: str) -> str:
    parsed = urlparse(record_url)
    record_id = parsed.path.rstrip("/").split("/")[-1]
    if parsed.netloc != "zenodo.org" or not record_id.isdigit():
        raise ValueError(record_url)
    return f"https://zenodo.org/api/records/{record_id}/files/{quote(filename, safe='')}/content"


def download(url: str, target: Path, attempts: int = 7) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_suffix(target.suffix + ".part")
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/octet-stream,*/*;q=0.8"})
            with urlopen(req, timeout=180) as response, part.open("wb") as out:  # nosec B310 - pinned public publisher URL
                shutil.copyfileobj(response, out, length=1024 * 1024)
            part.replace(target)
            return
        except Exception as exc:
            last_error = exc
            part.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(min(30, 2 ** (attempt - 1)))
    raise RuntimeError(f"download failed: {url}: {last_error}") from last_error


def dir_size(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) if path.exists() else 0


def ffprobe(path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,sample_rate,channels,duration:format=duration",
        "-of", "json", str(path),
    ]
    try:
        payload = json.loads(subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT))
        stream = (payload.get("streams") or [{}])[0]
        duration = stream.get("duration") or (payload.get("format") or {}).get("duration")
        return {
            "ok": True,
            "codec_name": stream.get("codec_name"),
            "sample_rate_hz": int(stream["sample_rate"]) if stream.get("sample_rate") else None,
            "channels": int(stream["channels"]) if stream.get("channels") else None,
            "duration_seconds": float(duration) if duration is not None else None,
            "backend": "ffprobe",
        }
    except Exception as exc:
        return {"ok": False, "reason": f"{type(exc).__name__}: {exc}", "backend": "ffprobe"}


def parse_label_zip(path: Path) -> dict[str, dict]:
    selected: dict[str, dict] = {}
    with zipfile.ZipFile(path) as zf:
        for name in sorted(zf.namelist()):
            if not name.casefold().endswith(".csv"):
                continue
            with zf.open(name) as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
                rows = list(csv.DictReader(text))
            if not rows:
                continue
            filename = str(rows[0].get("filename") or (Path(name).stem + ".flac")).strip()
            codes = sorted({str(row.get("event_label") or "").strip() for row in rows})
            exact = sorted({TARGET_CODES[code] for code in codes if code in TARGET_CODES})
            confuses = sorted({target for code in codes for target in CONFUSER_CODES.get(code, [])})
            if exact or confuses:
                selected[filename] = {
                    "event_labels": codes,
                    "echo_labels": exact,
                    "confuses": confuses,
                    "annotation_row_count": len(rows),
                }
    return selected


def load_metadata(path: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            filename = str(row.get("filename") or "").strip()
            if filename:
                rows[filename] = row
    return rows


def list_archive_members(archive: Path) -> list[tuple[str, int]]:
    output = subprocess.check_output(["7z", "l", "-slt", str(archive)], text=True, stderr=subprocess.STDOUT)
    members: list[tuple[str, int]] = []
    current_path: str | None = None
    current_size: int | None = None
    for line in output.splitlines() + [""]:
        if line.startswith("Path = "):
            if current_path is not None and current_size is not None:
                members.append((current_path, current_size))
            current_path = line[7:]
            current_size = None
        elif line.startswith("Size = "):
            value = line[7:].strip()
            if value.isdigit():
                current_size = int(value)
        elif not line.strip() and current_path is not None and current_size is not None:
            members.append((current_path, current_size))
            current_path = None
            current_size = None
    return members


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    limit = int(boundary["github_actions"]["project_max_working_set_bytes"])
    source = registry["sources"][SOURCE_ID]
    entries = {row["name"]: row for row in source["files"]}

    work = Path(args.work_root)
    raw = work / "raw"
    extracted = work / "selected"
    out = Path(args.output_dir)
    raw.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    required = [
        "labelled_metadata_public.csv", "labels_public.zip",
        "labelled.z01", "labelled.z02", "labelled.z03", "labelled.z04", "labelled.zip",
    ]
    bundle_evidence = []
    for name in required:
        entry = entries[name]
        target = raw / name
        download(publisher_url(source["record_url"], name), target)
        actual = digest(target, "md5")
        expected = str(entry["md5"]).lower()
        if actual.lower() != expected:
            raise SystemExit(f"publisher checksum mismatch {name}: {actual} != {expected}")
        bundle_evidence.append({
            "name": name,
            "size_bytes": target.stat().st_size,
            "publisher_md5": expected,
            "actual_md5": actual,
            "sha256": digest(target, "sha256"),
            "status": "PASS",
        })
        if dir_size(work) > limit:
            raise SystemExit("free-tier working-set boundary exceeded during download")

    selected = parse_label_zip(raw / "labels_public.zip")
    metadata = load_metadata(raw / "labelled_metadata_public.csv")
    archive = raw / "labelled.zip"
    members = list_archive_members(archive)
    selected_members = [(path, size) for path, size in members if Path(path).name in selected]
    missing = sorted(set(selected) - {Path(path).name for path, _ in selected_members})
    if missing:
        raise SystemExit(f"selected labelled assets missing from multipart archive: {len(missing)}")

    selected_uncompressed = sum(size for _, size in selected_members)
    safety_margin = 512 * 1024 * 1024
    projected = dir_size(work) + selected_uncompressed + safety_margin
    if projected > limit:
        raise SystemExit(f"bounded extraction would exceed free-tier working-set ceiling: projected={projected} limit={limit}")

    list_file = work / "selected-paths.txt"
    list_file.write_text("\n".join(path for path, _ in selected_members) + "\n", encoding="utf-8")
    extracted.mkdir(parents=True, exist_ok=True)
    subprocess.run(["7z", "x", "-y", f"-o{extracted}", str(archive), f"@{list_file}"], check=True)
    if dir_size(work) > limit:
        raise SystemExit("free-tier working-set boundary exceeded after selective extraction")

    extracted_files = {p.name: p for p in extracted.rglob("*.flac")}
    candidates = []
    target_counts: dict[str, int] = {}
    hard_negative_counts: dict[str, int] = {}
    probe_failures = 0
    total_duration = 0.0
    for filename in sorted(selected):
        path = extracted_files.get(filename)
        if path is None:
            raise SystemExit(f"extraction missing selected asset: {filename}")
        labels = selected[filename]
        meta = metadata.get(filename, {})
        probe = ffprobe(path)
        if not probe["ok"]:
            probe_failures += 1
        elif probe.get("duration_seconds"):
            total_duration += float(probe["duration_seconds"])
        for label in labels["echo_labels"]:
            target_counts[label] = target_counts.get(label, 0) + 1
        for confused in labels["confuses"]:
            hard_negative_counts[confused] = hard_negative_counts.get(confused, 0) + 1
        candidates.append({
            "schema_version": "echo.singapura-materialized-candidate.v1",
            "source_dataset": SOURCE_ID,
            "source_release": "v1.0a",
            "source_asset_id": filename,
            "sha256": digest(path, "sha256"),
            "byte_size": path.stat().st_size,
            "license_id": "CC-BY-SA-4.0",
            "profile": "research_extended",
            "label_provenance": "SINGA:PURA labels_public.zip",
            "source_event_labels": labels["event_labels"],
            "echo_labels": labels["echo_labels"],
            "confuses": labels["confuses"],
            "annotation_row_count": labels["annotation_row_count"],
            "sensor_id": meta.get("sensor_id"),
            "recording_group_candidate": f"singapura:{meta.get('sensor_id') or 'unknown'}:{filename}",
            "audio_probe": probe,
        })

    candidate_path = out / "singapura-v1.0a-candidates.jsonl"
    with candidate_path.open("w", encoding="utf-8") as handle:
        for row in candidates:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")

    summary = {
        "schema_version": "echo.singapura-bounded-materialization.v1",
        "status": "PASS" if probe_failures == 0 else "PASS_WITH_REVIEW_FLAGS",
        "source_id": SOURCE_ID,
        "source_release": "v1.0a",
        "profile": "research_extended",
        "publisher_files_verified": len(bundle_evidence),
        "publisher_file_evidence": bundle_evidence,
        "selected_recording_count": len(candidates),
        "selected_uncompressed_bytes": selected_uncompressed,
        "total_selected_duration_seconds": round(total_duration, 6),
        "probe_failures": probe_failures,
        "target_counts": dict(sorted(target_counts.items())),
        "hard_negative_counts_by_target": dict(sorted(hard_negative_counts.items())),
        "candidate_manifest_sha256": digest(candidate_path, "sha256"),
        "working_set_final_bytes": dir_size(work),
        "working_set_limit_bytes": limit,
        "certification_boundary": "Real selected SINGA:PURA bytes verified and probed under ECHO-FREE-TIER-001. CC-BY-SA-4.0 keeps this evidence in research_extended unless release policy is separately cleared.",
    }
    summary_path = out / "singapura-v1.0a-materialization-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
