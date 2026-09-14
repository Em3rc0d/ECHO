"""Codec-independent local fingerprints for ECHO corpus leakage screening.

The fingerprint is a screening signal, not a cryptographic identity. Every
input is decoded by local FFmpeg into the same mono 16 kHz signed-16 PCM stream
before feature extraction so container/codec/sample-rate/channel differences do
not create blind spots. SHA-256 of the original bytes remains asset identity.
"""

from __future__ import annotations

from array import array
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Iterable, Mapping, Any


FINGERPRINT_SCHEMA_VERSION = "echo.canonical-audio-fingerprint.v1"
FINGERPRINT_ALGORITHM = "normalized-rms-envelope-v1"


def canonical_pcm16_bytes(
    path: str | Path,
    *,
    sample_rate_hz: int = 16_000,
    ffmpeg_bin: str = "ffmpeg",
    timeout_seconds: int = 90,
) -> bytes:
    """Decode the first audio stream to deterministic mono PCM16LE bytes."""

    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")
    executable = shutil.which(ffmpeg_bin)
    if not executable:
        raise RuntimeError(f"{ffmpeg_bin} not available")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(p)
    command = [
        executable,
        "-nostdin",
        "-v", "error",
        "-i", str(p),
        "-map", "0:a:0",
        "-vn",
        "-sn",
        "-dn",
        "-ac", "1",
        "-ar", str(sample_rate_hz),
        "-f", "s16le",
        "-acodec", "pcm_s16le",
        "pipe:1",
    ]
    try:
        proc = subprocess.run(
            command,
            check=False,
            capture_output=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"canonical decode failed: {type(exc).__name__}") from exc
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace")[-500:]
        raise RuntimeError(f"canonical decode failed with ffmpeg rc={proc.returncode}: {detail}")
    if not proc.stdout:
        raise RuntimeError("canonical decode produced no PCM bytes")
    if len(proc.stdout) % 2:
        raise RuntimeError("canonical decode produced odd PCM16 byte count")
    return proc.stdout


def rms_envelope_vector(
    pcm16le: bytes,
    *,
    bins: int = 128,
    levels: int = 255,
) -> tuple[int, ...]:
    """Return a normalized fixed-length RMS envelope quantized to byte levels."""

    if bins <= 0:
        raise ValueError("bins must be positive")
    if not 2 <= levels <= 255:
        raise ValueError("levels must be in [2, 255]")
    if not pcm16le or len(pcm16le) % 2:
        raise ValueError("pcm16le must contain complete samples")

    samples = array("h")
    samples.frombytes(pcm16le)
    if sys.byteorder == "big":
        samples.byteswap()
    count = len(samples)
    if count <= 0:
        raise ValueError("pcm16le contains no samples")

    envelope: list[float] = []
    for index in range(bins):
        start = (index * count) // bins
        end = ((index + 1) * count) // bins
        if end <= start:
            envelope.append(0.0)
            continue
        total = 0
        for sample in samples[start:end]:
            value = int(sample)
            total += value * value
        envelope.append((total / float(end - start)) ** 0.5)

    peak = max(envelope) or 1.0
    return tuple(
        min(levels, max(0, round((value / peak) * levels)))
        for value in envelope
    )


def canonical_audio_fingerprint(
    path: str | Path,
    *,
    bins: int = 128,
    levels: int = 255,
    sample_rate_hz: int = 16_000,
    ffmpeg_bin: str = "ffmpeg",
) -> dict[str, Any]:
    """Build deterministic canonical decode and screening fingerprint evidence."""

    pcm = canonical_pcm16_bytes(
        path,
        sample_rate_hz=sample_rate_hz,
        ffmpeg_bin=ffmpeg_bin,
    )
    vector = rms_envelope_vector(pcm, bins=bins, levels=levels)
    encoded = bytes(vector)
    return {
        "schema_version": FINGERPRINT_SCHEMA_VERSION,
        "algorithm": FINGERPRINT_ALGORITHM,
        "canonical_decode": {
            "channels": 1,
            "sample_rate_hz": sample_rate_hz,
            "sample_format": "s16le",
        },
        "bins": bins,
        "levels": levels,
        "decoded_sample_count": len(pcm) // 2,
        "canonical_pcm_sha256": hashlib.sha256(pcm).hexdigest(),
        "vector_sha256": hashlib.sha256(encoded).hexdigest(),
        "vector": list(vector),
    }


def normalized_vector_distance(
    left: Iterable[int],
    right: Iterable[int],
    *,
    levels: int = 255,
) -> float:
    """Mean absolute vector distance normalized to [0, 1]."""

    a = tuple(int(value) for value in left)
    b = tuple(int(value) for value in right)
    if not a or len(a) != len(b):
        raise ValueError("fingerprint vectors must be non-empty and equal length")
    if levels <= 0:
        raise ValueError("levels must be positive")
    return sum(abs(x - y) for x, y in zip(a, b)) / float(len(a) * levels)


def fingerprint_distance(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
) -> float:
    """Distance between two compatible canonical fingerprint payloads."""

    if left.get("algorithm") != FINGERPRINT_ALGORITHM or right.get("algorithm") != FINGERPRINT_ALGORITHM:
        raise ValueError("incompatible fingerprint algorithm")
    if left.get("bins") != right.get("bins") or left.get("levels") != right.get("levels"):
        raise ValueError("incompatible fingerprint dimensions")
    return normalized_vector_distance(
        left.get("vector") or (),
        right.get("vector") or (),
        levels=int(left.get("levels") or 255),
    )


def are_near_duplicates(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    *,
    max_distance: float,
) -> bool:
    if not 0 <= max_distance <= 1:
        raise ValueError("max_distance must be in [0, 1]")
    return fingerprint_distance(left, right) <= max_distance
