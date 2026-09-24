"""Audio decoding through the project's existing FFmpeg runtime boundary."""

from __future__ import annotations

from array import array
from pathlib import Path
import subprocess


class AudioDecodeError(RuntimeError):
    pass


def decode_audio_f32_mono(
    path: str | Path,
    *,
    sample_rate_hz: int,
    ffmpeg_bin: str = "ffmpeg",
) -> list[float]:
    """Decode arbitrary FFmpeg-supported media to mono float32 PCM."""

    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)

    command = [
        ffmpeg_bin,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(source),
        "-vn",
        "-ac",
        "1",
        "-ar",
        str(sample_rate_hz),
        "-f",
        "f32le",
        "pipe:1",
    ]
    proc = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise AudioDecodeError(
            f"ffmpeg failed for {source}: "
            + proc.stderr.decode("utf-8", errors="replace").strip()
        )
    if len(proc.stdout) % 4:
        raise AudioDecodeError(f"invalid f32le byte length for {source}")

    pcm = array("f")
    pcm.frombytes(proc.stdout)
    if not pcm:
        raise AudioDecodeError(f"decoded audio is empty: {source}")
    return pcm.tolist()
