#!/usr/bin/env python3
"""Materialize deterministic WAV events from the certified-candidate s0500 audit.

This stage does not mutate the canonical ledger. It reconstructs the governed
BigSoundBank s0500 source, verifies source identity and every audited PCM slice,
writes deterministic mono 16 kHz PCM WAV segments, and records byte hashes,
probes and canonical fingerprints. Corpus credit is granted only by the separate
reviewed ledger augmentation.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
from urllib.request import Request, urlopen
import wave

from echo.data_foundry.canonical_fingerprints import canonical_audio_fingerprint
from echo.data_foundry.probe import probe_audio

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "MK1/mining-site/materialization/bigsoundbank-0500-segmentation-audit.json"
OUTPUT = ROOT / "MK1/mining-site/materialization/bigsoundbank-0500-segment-materialization.json"
SCRATCH = Path(os.environ.get("ECHO_BSB_0500_SEGMENT_ROOT", ROOT / ".materialized-bsb-0500-segments"))

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2


def fetch(url: str) -> tuple[bytes, str]:
    req = Request(url, headers={"User-Agent": "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"})
    with urlopen(req, timeout=90) as response:  # nosec B310 - governed public URL
        return response.read(), response.geturl()


def decode_pcm(source: Path) -> bytes:
    proc = subprocess.run(
        [
            "ffmpeg", "-nostdin", "-v", "error", "-i", str(source),
            "-map", "0:a:0", "-vn", "-sn", "-dn",
            "-ac", "1", "-ar", str(SAMPLE_RATE),
            "-f", "s16le", "-acodec", "pcm_s16le", "pipe:1",
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if not proc.stdout or len(proc.stdout) % 2:
        raise SystemExit("invalid canonical PCM decode for s0500")
    return proc.stdout


def render_wav(path: Path, pcm: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(CHANNELS)
        handle.setsampwidth(SAMPLE_WIDTH)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(pcm)


def main() -> int:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if audit.get("status") != "PASS_CANDIDATE":
        raise SystemExit("s0500 audit is not PASS_CANDIDATE")
    if audit.get("detected_event_count") != 17 or audit.get("unique_segment_pcm_hash_count") != 17:
        raise SystemExit("s0500 audit cardinality drift")
    if audit.get("recording_family") != "tire_500":
        raise SystemExit("s0500 recording family drift")

    source_bytes, resolved = fetch(str(audit["media_url"]))
    if hashlib.sha256(source_bytes).hexdigest() != audit.get("media_sha256"):
        raise SystemExit("s0500 source media SHA-256 drift")

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "source.mp3"
        source.write_bytes(source_bytes)
        pcm = decode_pcm(source)

    SCRATCH.mkdir(parents=True, exist_ok=True)
    rows = []
    for event in audit["events"]:
        index = int(event["event_index"])
        start = int(round(float(event["start_seconds"]) * SAMPLE_RATE))
        end = int(round(float(event["end_seconds"]) * SAMPLE_RATE))
        segment_pcm = pcm[start * 2:end * 2]
        pcm_sha = hashlib.sha256(segment_pcm).hexdigest()
        if pcm_sha != event["canonical_pcm_sha256"]:
            raise SystemExit(f"event {index:02d} PCM identity mismatch")
        if len(segment_pcm) // 2 != int(event["decoded_sample_count"]):
            raise SystemExit(f"event {index:02d} sample-count mismatch")

        wav_path = SCRATCH / f"bigsoundbank-0500-event-{index:02d}.wav"
        render_wav(wav_path, segment_pcm)
        wav_bytes = wav_path.read_bytes()
        probe = probe_audio(wav_path)
        if not probe.ok:
            raise SystemExit(f"event {index:02d} probe failed: {probe.reason}")
        fingerprint = canonical_audio_fingerprint(wav_path)
        if fingerprint["canonical_pcm_sha256"] != pcm_sha:
            raise SystemExit(f"event {index:02d} fingerprint PCM identity mismatch")

        rows.append({
            "segment_asset_id": f"bigsoundbank-500:event-{index:02d}",
            "event_index": index,
            "start_seconds": event["start_seconds"],
            "end_seconds": event["end_seconds"],
            "duration_seconds": event["duration_seconds"],
            "recording_family": "tire_500",
            "license_id": "CC0",
            "semantic": "tire_squeal",
            "rendered_format": {
                "container": "wav",
                "codec": "pcm_s16le",
                "sample_rate_hz": SAMPLE_RATE,
                "channels": CHANNELS,
                "sample_width_bytes": SAMPLE_WIDTH,
            },
            "media_sha256": hashlib.sha256(wav_bytes).hexdigest(),
            "size_bytes": len(wav_bytes),
            "audio_probe": probe.to_dict(),
            "canonical_fingerprint": fingerprint,
        })

    if len(rows) != 17 or len({row["media_sha256"] for row in rows}) != 17:
        raise SystemExit("rendered segment identity/cardinality failure")

    payload = {
        "schema_version": "echo.bigsoundbank-0500-segment-materialization.v1",
        "status": "PASS",
        "phase": "SEGMENT_MATERIALIZED_NO_CORPUS_CREDIT",
        "source_dataset": "echo-bigsoundbank-cc0-gap-v1",
        "parent_asset_key": "bigsoundbank-500",
        "parent_media_sha256": audit["media_sha256"],
        "resolved_parent_media_url": resolved,
        "canonical_page": audit["canonical_page"],
        "canonical_page_sha256": audit["canonical_page_sha256"],
        "target": "TIRE_SQUEAL",
        "recording_family": "tire_500",
        "segment_count": len(rows),
        "segments": rows,
        "audit_sha256": hashlib.sha256(AUDIT.read_bytes()).hexdigest(),
        "stop_lines": [
            "Materialization alone grants zero corpus credit.",
            "All 17 events inherit one BigSoundBank acoustic source family and one recording group: tire_500.",
            "Reviewed admission must remove the overlapping full s0500 asset before adding these events.",
            "Global exact/near dedup, protected split and coverage must rerun after admission.",
        ],
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "segments": len(rows),
        "unique_media_sha256": len({row["media_sha256"] for row in rows}),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
