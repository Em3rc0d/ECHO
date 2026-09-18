#!/usr/bin/env python3
"""Audit temporal segmentation of BigSoundBank s0500 without granting corpus credit.

The canonical page states that s0500 contains 17 tire-screech events. This tool
materializes the governed CC0 media, decodes it to mono PCM, applies one frozen
energy segmentation rule, and emits evidence only. It MUST NOT mutate the
canonical ledger or coverage artifacts.

PASS_CANDIDATE requires:
- governed page/media identity,
- positive technical decode,
- exactly 17 separated active regions,
- every region >= minimum duration,
- unique PCM SHA-256 per region.

A PASS_CANDIDATE report still grants zero corpus credit. A reviewed admission
stage must later render canonical segment bytes/fingerprints and replace the
overlapping full-source asset rather than double-count it.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import statistics
import struct
import subprocess
import tempfile
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/data_foundry/gap_source_candidates.v1.json"
REPORT = ROOT / "MK1/mining-site/materialization/bigsoundbank-0500-segmentation-audit.json"

TARGET = "TIRE_SQUEAL"
ASSET_KEY = "bigsoundbank-500"
EXPECTED_EVENTS = 17
SAMPLE_RATE = 16000
FRAME_MS = 25
HOP_MS = 10
NOISE_PERCENTILE = 0.20
NOISE_MULTIPLIER = 3.5
MAX_RMS_FRACTION = 0.05
MERGE_GAP_SECONDS = 0.18
MIN_EVENT_SECONDS = 0.12
PAD_SECONDS = 0.08


def fetch(url: str) -> tuple[bytes, str]:
    req = Request(url, headers={"User-Agent": "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"})
    with urlopen(req, timeout=90) as response:  # nosec B310 - governed public evidence URLs only
        return response.read(), response.geturl()


def governed_row() -> dict:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    rows = payload["sources"]["echo-bigsoundbank-cc0-gap-v1"]["targets"][TARGET]
    exact = [row for row in rows if row.get("asset_key") == ASSET_KEY]
    if len(exact) != 1:
        raise SystemExit("governed s0500 row must exist exactly once")
    row = exact[0]
    if row.get("semantic") != "tire_squeal" or row.get("recording_family") != "tire_500":
        raise SystemExit("s0500 semantic/grouping governance drift")
    return row


def decode_pcm(mp3: Path) -> bytes:
    cmd = [
        "ffmpeg", "-v", "error", "-i", str(mp3),
        "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "s16le", "pipe:1",
    ]
    proc = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not proc.stdout:
        raise SystemExit("ffmpeg produced empty PCM")
    return proc.stdout


def rms_frames(samples: list[int]) -> list[float]:
    frame = max(1, SAMPLE_RATE * FRAME_MS // 1000)
    hop = max(1, SAMPLE_RATE * HOP_MS // 1000)
    values: list[float] = []
    for start in range(0, max(1, len(samples) - frame + 1), hop):
        chunk = samples[start:start + frame]
        if not chunk:
            break
        values.append(math.sqrt(sum(x * x for x in chunk) / len(chunk)))
    return values


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def regions_from_activity(active: list[bool]) -> list[tuple[float, float]]:
    raw: list[tuple[int, int]] = []
    start: int | None = None
    for idx, flag in enumerate(active + [False]):
        if flag and start is None:
            start = idx
        elif not flag and start is not None:
            raw.append((start, idx - 1))
            start = None

    merge_frames = max(0, round(MERGE_GAP_SECONDS * 1000 / HOP_MS))
    merged: list[tuple[int, int]] = []
    for current in raw:
        if merged and current[0] - merged[-1][1] - 1 <= merge_frames:
            merged[-1] = (merged[-1][0], current[1])
        else:
            merged.append(current)

    result: list[tuple[float, float]] = []
    total_duration = len(active) * HOP_MS / 1000
    for a, b in merged:
        start_s = max(0.0, a * HOP_MS / 1000 - PAD_SECONDS)
        end_s = min(total_duration, (b * HOP_MS + FRAME_MS) / 1000 + PAD_SECONDS)
        if end_s - start_s >= MIN_EVENT_SECONDS:
            result.append((round(start_s, 6), round(end_s, 6)))
    return result


def segment_pcm_sha(pcm: bytes, start_s: float, end_s: float) -> tuple[str, int]:
    start = max(0, int(start_s * SAMPLE_RATE)) * 2
    end = min(len(pcm), int(end_s * SAMPLE_RATE) * 2)
    segment = pcm[start:end]
    return hashlib.sha256(segment).hexdigest(), len(segment) // 2


def main() -> int:
    row = governed_row()
    page_bytes, resolved_page = fetch(row["url"])
    page_text = page_bytes.decode("utf-8", errors="replace").casefold()
    required_markers = ["tire squeal", "17 screeching tire", "cc0"]
    missing_markers = [marker for marker in required_markers if marker not in page_text]
    media_bytes, resolved_media = fetch(row["media_url"])

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "0500.mp3"
        path.write_bytes(media_bytes)
        pcm = decode_pcm(path)

    if len(pcm) % 2:
        raise SystemExit("decoded PCM byte length must be even")
    samples = list(struct.unpack("<" + "h" * (len(pcm) // 2), pcm))
    rms = rms_frames(samples)
    if not rms:
        raise SystemExit("no RMS frames decoded")

    noise = percentile(rms, NOISE_PERCENTILE)
    max_rms = max(rms)
    threshold = max(noise * NOISE_MULTIPLIER, max_rms * MAX_RMS_FRACTION)
    regions = regions_from_activity([value >= threshold for value in rms])

    event_rows = []
    for idx, (start_s, end_s) in enumerate(regions, 1):
        sha, sample_count = segment_pcm_sha(pcm, start_s, end_s)
        event_rows.append({
            "event_index": idx,
            "start_seconds": start_s,
            "end_seconds": end_s,
            "duration_seconds": round(end_s - start_s, 6),
            "canonical_pcm_sha256": sha,
            "decoded_sample_count": sample_count,
            "recording_family": "tire_500",
        })

    unique_hashes = len({row["canonical_pcm_sha256"] for row in event_rows})
    exact_count = len(event_rows) == EXPECTED_EVENTS
    separated_unique = unique_hashes == len(event_rows)
    markers_pass = not missing_markers
    status = "PASS_CANDIDATE" if markers_pass and exact_count and separated_unique else "REVIEW_REQUIRED"

    payload = {
        "schema_version": "echo.bigsoundbank-0500-segmentation-audit.v1",
        "status": status,
        "phase": "SEGMENTATION_EVIDENCE_ONLY_NO_CORPUS_CREDIT",
        "source_dataset": "echo-bigsoundbank-cc0-gap-v1",
        "asset_key": ASSET_KEY,
        "target": TARGET,
        "recording_family": "tire_500",
        "expected_event_count_from_page": EXPECTED_EVENTS,
        "detected_event_count": len(event_rows),
        "unique_segment_pcm_hash_count": unique_hashes,
        "canonical_page": row["url"],
        "resolved_page": resolved_page,
        "canonical_page_sha256": hashlib.sha256(page_bytes).hexdigest(),
        "page_markers_required": required_markers,
        "page_markers_missing": missing_markers,
        "media_url": row["media_url"],
        "resolved_media_url": resolved_media,
        "media_sha256": hashlib.sha256(media_bytes).hexdigest(),
        "media_size_bytes": len(media_bytes),
        "decode": {"sample_rate_hz": SAMPLE_RATE, "channels": 1, "sample_format": "s16le"},
        "segmentation_policy": {
            "frame_ms": FRAME_MS,
            "hop_ms": HOP_MS,
            "noise_percentile": NOISE_PERCENTILE,
            "noise_multiplier": NOISE_MULTIPLIER,
            "max_rms_fraction": MAX_RMS_FRACTION,
            "merge_gap_seconds": MERGE_GAP_SECONDS,
            "min_event_seconds": MIN_EVENT_SECONDS,
            "pad_seconds": PAD_SECONDS,
            "threshold_rms": round(threshold, 6),
            "noise_rms": round(noise, 6),
            "max_rms": round(max_rms, 6),
        },
        "events": event_rows,
        "stop_lines": [
            "This audit grants zero corpus, coverage, split, group or source-diversity credit.",
            "All derived events inherit one recording family: tire_500.",
            "A later admission must replace the overlapping full-source positive instead of double-counting it.",
            "Admission requires canonical rendered bytes, standard fingerprints, global dedup, split integrity and coverage rerun.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "detected": len(event_rows),
        "expected": EXPECTED_EVENTS,
        "unique": unique_hashes,
        "missing_markers": missing_markers,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
