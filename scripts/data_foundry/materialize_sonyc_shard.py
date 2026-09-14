#!/usr/bin/env python3
"""Materialize one SONYC-UST v2.3 audio shard inside the free-tier boundary.

The job downloads exactly one publisher shard plus annotations, verifies MD5,
extracts only that shard, probes/hash-inventories every WAV, derives conservative
exact target/confuser evidence from ground-truth rows when available, and
canonical-fingerprints only ledger-relevant target/confuser assets while the
real bytes still exist. Raw audio is discarded after compact evidence is emitted.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import time
import wave
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from echo.data_foundry.canonical_fingerprints import FINGERPRINT_ALGORITHM
from echo.data_foundry.canonical_fingerprints import canonical_audio_fingerprint

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "configs/data_foundry/acquisition_registry.v1.json"
BOUNDARY = ROOT / "configs/data_foundry/free_tier_boundary.v1.json"
SOURCE_ID = "sonyc-ust-v2"
USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"

TARGET_COLUMNS = {
    "VEHICLE_HORN": "car-horn",
    "SIREN": "siren",
}
CONFUSER_COLUMNS = {
    "car-alarm": ["SIREN", "FIRE_ALARM"],
    "reverse-beeper": ["SIREN", "FIRE_ALARM"],
    "machinery-impact": ["GLASS_SHATTER"],
    "non-machinery-impact": ["GLASS_SHATTER"],
}


def md5_file(path: Path) -> str:
    h = hashlib.md5()  # nosec B303 - publisher checksum compatibility only
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def publisher_url(record_url: str, filename: str) -> str:
    parsed = urlparse(record_url)
    record_id = parsed.path.rstrip("/").split("/")[-1]
    if parsed.netloc != "zenodo.org" or not record_id.isdigit():
        raise ValueError(f"unsupported publisher record: {record_url}")
    return f"https://zenodo.org/api/records/{record_id}/files/{quote(filename, safe='')}/content"


def download(url: str, target: Path, attempts: int = 7) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_suffix(target.suffix + ".part")
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/octet-stream,*/*;q=0.8"})
            with urlopen(request, timeout=180) as response, part.open("wb") as out:  # nosec B310 - pinned public publisher URL
                shutil.copyfileobj(response, out, length=1024 * 1024)
                final_url = response.geturl()
            part.replace(target)
            return final_url
        except Exception as exc:
            last_error = exc
            part.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(min(30, 2 ** (attempt - 1)))
    raise RuntimeError(f"download failed: {url}: {last_error}") from last_error


def verify_download(source: dict, entry: dict, target: Path) -> dict:
    final_url = download(publisher_url(source["record_url"], entry["name"]), target)
    actual = md5_file(target)
    expected = str(entry.get("md5") or "").lower()
    if expected and actual.lower() != expected:
        target.unlink(missing_ok=True)
        raise RuntimeError(f"publisher MD5 mismatch for {entry['name']}: {actual} != {expected}")
    return {
        "name": entry["name"],
        "size_bytes": target.stat().st_size,
        "publisher_md5": expected or None,
        "actual_md5": actual,
        "sha256": sha256_file(target),
        "final_url": final_url,
        "status": "PASS",
    }


def find_presence_column(headers: list[str], token: str) -> str | None:
    token = token.casefold()
    exact = [h for h in headers if h.casefold().endswith("_presence") and token in h.casefold()]
    if not exact:
        return None
    exact.sort(key=lambda value: (0 if value.casefold().startswith("5-") else 1, len(value), value))
    return exact[0]


def load_annotations(path: Path) -> tuple[dict[str, list[dict[str, str]]], dict[str, str | None], list[str]]:
    by_file: dict[str, list[dict[str, str]]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        if "audio_filename" not in headers:
            raise RuntimeError("SONYC annotations.csv missing audio_filename")
        for row in reader:
            name = str(row.get("audio_filename") or "").strip()
            if name:
                by_file.setdefault(name, []).append(row)
    columns: dict[str, str | None] = {}
    for target, token in TARGET_COLUMNS.items():
        columns[target] = find_presence_column(headers, token)
    for token in CONFUSER_COLUMNS:
        columns[f"CONFUSER:{token}"] = find_presence_column(headers, token)
    return by_file, columns, headers


def one(values: list[dict[str, str]], column: str | None) -> bool:
    if not column:
        return False
    return any(str(row.get(column, "")).strip() == "1" for row in values)


def group_candidate(row: dict[str, str] | None, filename: str) -> str:
    if not row:
        return f"sonyc-unknown:{filename}"
    parts = [
        str(row.get("sensor_id") or "unknown"),
        str(row.get("year") or "unknown"),
        str(row.get("week") or "unknown"),
        str(row.get("day") or "unknown"),
        str(row.get("hour") or "unknown"),
    ]
    return "sonyc:" + ":".join(parts)


def probe_wav(path: Path) -> dict:
    try:
        with wave.open(str(path), "rb") as wav:
            rate = int(wav.getframerate())
            frames = int(wav.getnframes())
            channels = int(wav.getnchannels())
            width = int(wav.getsampwidth())
        return {
            "ok": True,
            "sample_rate_hz": rate,
            "channels": channels,
            "sample_width_bytes": width,
            "frames": frames,
            "duration_seconds": (frames / rate if rate else 0.0),
            "backend": "python-wave",
        }
    except Exception as exc:
        return {"ok": False, "reason": f"{type(exc).__name__}: {exc}", "backend": "python-wave"}


def dir_size(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) if path.exists() else 0


def materialize(shard: int, work_root: Path, output_dir: Path) -> dict:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    source = registry["sources"][SOURCE_ID]
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    limit = int(boundary["github_actions"]["project_max_working_set_bytes"])

    filename = f"audio-{shard}.tar.gz"
    entries = {row["name"]: row for row in source["files"]}
    if filename not in entries:
        raise ValueError(f"unknown SONYC shard {shard}")

    raw = work_root / "raw"
    extracted = work_root / "extracted"
    annotations = raw / "annotations.csv"
    archive = raw / filename
    metadata_evidence = verify_download(source, entries["annotations.csv"], annotations)
    shard_evidence = verify_download(source, entries[filename], archive)

    if dir_size(work_root) > limit:
        raise RuntimeError("free-tier working-set boundary exceeded before extraction")

    extracted.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tf:
        tf.extractall(extracted, filter="data")

    if dir_size(work_root) > limit:
        raise RuntimeError("free-tier working-set boundary exceeded after extraction")

    annotations_by_file, presence_columns, annotation_headers = load_annotations(annotations)
    wavs = sorted(p for p in extracted.rglob("*") if p.is_file() and p.suffix.casefold() == ".wav")
    if not wavs:
        raise RuntimeError(f"{filename} extracted zero WAV files")

    output_dir.mkdir(parents=True, exist_ok=True)
    inventory_path = output_dir / f"sonyc-shard-{shard:02d}.jsonl.gz"
    asset_count = 0
    probe_failures = 0
    fingerprinted_assets = 0
    fingerprint_failures = 0
    unmatched_annotations = 0
    ground_truth_assets = 0
    target_counts = {key: 0 for key in TARGET_COLUMNS}
    confuser_counts = {key: 0 for key in CONFUSER_COLUMNS}
    split_counts: dict[str, int] = {}
    total_duration = 0.0

    with gzip.open(inventory_path, "wt", encoding="utf-8", compresslevel=9) as out:
        for wav_path in wavs:
            filename_only = wav_path.name
            rows = annotations_by_file.get(filename_only, [])
            authoritative = [row for row in rows if str(row.get("annotator_id") or "").strip() == "0"]
            chosen = authoritative[0] if authoritative else (rows[0] if rows else None)
            if not rows:
                unmatched_annotations += 1
            if authoritative:
                ground_truth_assets += 1

            echo_labels = [target for target in TARGET_COLUMNS if one(authoritative, presence_columns.get(target))]
            confuses: set[str] = set()
            source_confusers: list[str] = []
            for token, targets in CONFUSER_COLUMNS.items():
                if one(authoritative, presence_columns.get(f"CONFUSER:{token}")):
                    source_confusers.append(token)
                    confuses.update(targets)

            for label in echo_labels:
                target_counts[label] += 1
            for token in source_confusers:
                confuser_counts[token] += 1

            split = str((chosen or {}).get("split") or "unknown")
            split_counts[split] = split_counts.get(split, 0) + 1
            probe = probe_wav(wav_path)
            if not probe["ok"]:
                probe_failures += 1
            else:
                total_duration += float(probe["duration_seconds"])

            canonical_fingerprint = None
            fingerprint_error = None
            if (echo_labels or confuses) and probe.get("ok") is True:
                try:
                    canonical_fingerprint = canonical_audio_fingerprint(wav_path)
                    fingerprinted_assets += 1
                except Exception as exc:
                    fingerprint_failures += 1
                    fingerprint_error = f"{type(exc).__name__}: {exc}"

            crowd_votes: dict[str, dict[str, int]] = {}
            for target in TARGET_COLUMNS:
                col = presence_columns.get(target)
                known = [str(row.get(col, "")).strip() for row in rows] if col else []
                crowd_votes[target] = {
                    "positive": sum(value == "1" for value in known),
                    "negative": sum(value == "0" for value in known),
                    "unknown": sum(value not in {"0", "1"} for value in known),
                }

            rel = wav_path.relative_to(extracted).as_posix()
            record = {
                "schema_version": "echo.sonyc-materialized-asset.v2",
                "source_dataset": SOURCE_ID,
                "source_release": "2.3",
                "source_asset_id": filename_only,
                "archive": filename,
                "archive_member": rel,
                "sha256": sha256_file(wav_path),
                "byte_size": wav_path.stat().st_size,
                "license_id": "CC-BY-4.0",
                "label_provenance": "SONYC-UST-v2.3 annotations.csv",
                "annotation_row_count": len(rows),
                "ground_truth_row_count": len(authoritative),
                "annotation_status": "GROUND_TRUTH_AVAILABLE" if authoritative else ("CROWD_ONLY_REVIEW_REQUIRED" if rows else "ANNOTATION_MISSING"),
                "echo_labels_ground_truth": echo_labels,
                "source_confusers_ground_truth": source_confusers,
                "confuses_ground_truth": sorted(confuses),
                "crowd_votes": crowd_votes,
                "split": split,
                "sensor_id": (chosen or {}).get("sensor_id"),
                "recording_group_candidate": group_candidate(chosen, filename_only),
                "audio_probe": probe,
                "canonical_fingerprint": canonical_fingerprint,
                "fingerprint_error": fingerprint_error,
            }
            out.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
            asset_count += 1

    inventory_sha256 = sha256_file(inventory_path)
    summary = {
        "schema_version": "echo.sonyc-shard-materialization.v2",
        "status": "PASS" if probe_failures == 0 and fingerprint_failures == 0 and unmatched_annotations == 0 else "PASS_WITH_REVIEW_FLAGS",
        "source_id": SOURCE_ID,
        "source_release": "2.3",
        "shard_index": shard,
        "shard_file": filename,
        "metadata_evidence": metadata_evidence,
        "shard_evidence": shard_evidence,
        "annotation_columns": presence_columns,
        "annotation_header_count": len(annotation_headers),
        "asset_count": asset_count,
        "ground_truth_asset_count": ground_truth_assets,
        "unmatched_annotation_assets": unmatched_annotations,
        "probe_failures": probe_failures,
        "fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "fingerprinted_ledger_relevant_assets": fingerprinted_assets,
        "fingerprint_failures": fingerprint_failures,
        "total_duration_seconds": round(total_duration, 6),
        "target_ground_truth_counts": target_counts,
        "confuser_ground_truth_counts": confuser_counts,
        "split_counts": dict(sorted(split_counts.items())),
        "inventory_file": inventory_path.name,
        "inventory_sha256": inventory_sha256,
        "working_set_peak_guard_bytes": limit,
        "working_set_final_bytes": dir_size(work_root),
        "certification_note": "Real bytes verified/probed; ledger-relevant target/confuser assets were canonical-fingerprinted before raw bytes were discarded. Final corpus admission still requires global dedup/group/split/coverage gates.",
    }
    summary_path = output_dir / f"sonyc-shard-{shard:02d}.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    if args.shard < 0 or args.shard > 18:
        raise SystemExit("SONYC shard must be 0..18")
    summary = materialize(args.shard, Path(args.work_root), Path(args.output_dir))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
