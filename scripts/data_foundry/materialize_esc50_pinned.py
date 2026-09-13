#!/usr/bin/env python3
"""Materialize a pinned ESC-50 research snapshot within ECHO-FREE-TIER-001."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import time
from urllib.request import Request, urlopen
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BOUNDARY = ROOT / "configs/data_foundry/free_tier_boundary.v1.json"
PINNED_COMMIT = "33c8ce9eb2cf0b1c2f8bcf322eb349b6be34dbb6"
ARCHIVE_URL = f"https://codeload.github.com/karolpiczak/ESC-50/zip/{PINNED_COMMIT}"
USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"
TARGET_MAP = {"siren": "SIREN", "car_horn": "VEHICLE_HORN"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, target: Path, attempts: int = 5) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_suffix(target.suffix + ".part")
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/zip,*/*;q=0.8"})
            with urlopen(request, timeout=180) as response, part.open("wb") as out:  # nosec B310 - pinned public GitHub archive
                shutil.copyfileobj(response, out, length=1024 * 1024)
                final_url = response.geturl()
            part.replace(target)
            return final_url
        except Exception as exc:
            last = exc
            part.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(min(20, 2 ** attempt))
    raise RuntimeError(f"download failed: {url}: {last}") from last


def wav_probe(path: Path) -> dict:
    try:
        with wave.open(str(path), "rb") as wav:
            rate = int(wav.getframerate())
            frames = int(wav.getnframes())
            channels = int(wav.getnchannels())
        return {
            "ok": True,
            "sample_rate_hz": rate,
            "channels": channels,
            "duration_seconds": frames / rate if rate else 0.0,
            "backend": "python-wave",
        }
    except Exception as exc:
        return {"ok": False, "reason": f"{type(exc).__name__}: {exc}", "backend": "python-wave"}


def dir_size(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) if path.exists() else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    limit = int(boundary["github_actions"]["project_max_working_set_bytes"])
    work = Path(args.work_root)
    out = Path(args.output_dir)
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    archive = work / "esc50-pinned.zip"
    final_url = download(ARCHIVE_URL, archive)
    archive_sha = sha256_file(archive)
    if dir_size(work) > limit:
        raise SystemExit("free-tier working-set boundary exceeded after ESC-50 download")

    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        meta_names = [name for name in names if name.endswith("/meta/esc50.csv")]
        if len(meta_names) != 1:
            raise SystemExit(f"expected one ESC-50 metadata CSV, found {len(meta_names)}")
        metadata_text = zf.read(meta_names[0]).decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(metadata_text)))
        selected = [row for row in rows if str(row.get("category")) in TARGET_MAP]
        if not selected:
            raise SystemExit("pinned ESC-50 snapshot contains no selected target rows")

        audio_by_name = {Path(name).name: name for name in names if "/audio/" in name and name.endswith(".wav")}
        extract_root = work / "selected"
        extract_root.mkdir(parents=True, exist_ok=True)
        candidates = []
        probe_failures = 0
        counts: dict[str, int] = {}
        folds: dict[str, dict[str, int]] = {}
        total_duration = 0.0

        for row in selected:
            filename = str(row["filename"])
            member = audio_by_name.get(filename)
            if member is None:
                raise SystemExit(f"metadata audio missing from archive: {filename}")
            target_path = extract_root / filename
            with zf.open(member) as src, target_path.open("wb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)
            probe = wav_probe(target_path)
            if not probe["ok"]:
                probe_failures += 1
            else:
                total_duration += float(probe["duration_seconds"])
            category = str(row["category"])
            echo_label = TARGET_MAP[category]
            counts[echo_label] = counts.get(echo_label, 0) + 1
            fold = str(row.get("fold") or "unknown")
            folds.setdefault(echo_label, {})[fold] = folds.setdefault(echo_label, {}).get(fold, 0) + 1
            candidates.append({
                "schema_version": "echo.esc50-materialized-candidate.v1",
                "source_dataset": "esc50",
                "source_release": PINNED_COMMIT,
                "source_asset_id": filename,
                "sha256": sha256_file(target_path),
                "byte_size": target_path.stat().st_size,
                "license_id": "CC-BY-NC",
                "profile": "research_extended",
                "label_provenance": "ESC-50 meta/esc50.csv pinned Git commit",
                "source_category": category,
                "echo_labels": [echo_label],
                "original_fold": int(row["fold"]),
                "src_file": int(row["src_file"]),
                "take": str(row["take"]),
                "recording_group_candidate": f"esc50:{row['src_file']}:{row['take']}",
                "audio_probe": probe,
            })

    if dir_size(work) > limit:
        raise SystemExit("free-tier working-set boundary exceeded during ESC-50 materialization")

    candidate_path = out / "esc50-pinned-target-candidates.jsonl"
    with candidate_path.open("w", encoding="utf-8") as handle:
        for row in sorted(candidates, key=lambda item: item["source_asset_id"]):
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")

    summary = {
        "schema_version": "echo.esc50-pinned-materialization.v1",
        "status": "PASS" if probe_failures == 0 else "PASS_WITH_REVIEW_FLAGS",
        "source_id": "esc50",
        "pinned_commit": PINNED_COMMIT,
        "archive_url": ARCHIVE_URL,
        "resolved_archive_url": final_url,
        "archive_sha256": archive_sha,
        "archive_size_bytes": archive.stat().st_size,
        "profile": "research_extended",
        "license_id": "CC-BY-NC",
        "selected_asset_count": len(candidates),
        "target_counts": dict(sorted(counts.items())),
        "target_fold_counts": {key: dict(sorted(value.items())) for key, value in sorted(folds.items())},
        "probe_failures": probe_failures,
        "total_selected_duration_seconds": round(total_duration, 6),
        "candidate_manifest_sha256": sha256_file(candidate_path),
        "working_set_final_bytes": dir_size(work),
        "working_set_limit_bytes": limit,
        "certification_boundary": "Pinned real ESC-50 target bytes materialized under the free-tier boundary. CC-BY-NC keeps this evidence research-only and it cannot satisfy release_safe source diversity.",
    }
    (out / "esc50-pinned-materialization-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
