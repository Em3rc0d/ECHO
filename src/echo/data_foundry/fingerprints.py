"""Lightweight PCM-WAV near-duplicate fingerprinting for Foundry screening.

This is a screening signal, not a cryptographic identity. SHA-256 remains the
canonical asset identity. Unsupported/non-PCM WAV files simply return None and
can be fingerprinted later by an audio decoder stage.
"""

from __future__ import annotations

from array import array
import hashlib
from pathlib import Path
import sys
import wave


def wav_envelope_fingerprint(path: str | Path, *, bins: int = 128, levels: int = 31) -> str | None:
    if bins <= 0 or levels <= 1:
        raise ValueError("bins and levels must be positive")
    p = Path(path)
    if p.suffix.lower() != ".wav":
        return None
    try:
        with wave.open(str(p), "rb") as wav:
            channels = wav.getnchannels()
            width = wav.getsampwidth()
            frames = wav.getnframes()
            if channels <= 0 or width != 2 or frames <= 0:
                return None
            raw = wav.readframes(frames)
    except (wave.Error, EOFError, OSError):
        return None

    samples = array("h")
    samples.frombytes(raw)
    if sys.byteorder == "big":
        samples.byteswap()
    frame_count = len(samples) // channels
    if frame_count <= 0:
        return None

    # Downmix by arithmetic mean to keep fingerprint independent of channel count.
    mono: list[int] = []
    for frame_index in range(frame_count):
        base = frame_index * channels
        mono.append(sum(int(samples[base + c]) for c in range(channels)) // channels)

    step = max(1, len(mono) // bins)
    envelope: list[float] = []
    for start in range(0, len(mono), step):
        segment = mono[start : start + step]
        if not segment:
            continue
        envelope.append(sum(abs(v) for v in segment) / len(segment))
        if len(envelope) == bins:
            break
    while len(envelope) < bins:
        envelope.append(0.0)

    peak = max(envelope) or 1.0
    quantized = bytes(min(levels, max(0, round((value / peak) * levels))) for value in envelope[:bins])
    return hashlib.sha256(quantized).hexdigest()
