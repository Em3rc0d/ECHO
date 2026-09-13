"""Technical audio probes used by the MK1 Data Foundry.

WAV is probed with the Python standard library. Other formats use ffprobe when
available. The probe is deterministic metadata evidence; decoding/normalizing
for model input remains the later audio-runtime responsibility.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess
import wave


@dataclass(frozen=True)
class AudioProbe:
    ok: bool
    backend: str
    duration_seconds: float | None = None
    sample_rate_hz: int | None = None
    channels: int | None = None
    codec_name: str | None = None
    reason: str | None = None

    def to_dict(self) -> dict[str, object | None]:
        return {
            "ok": self.ok,
            "backend": self.backend,
            "duration_seconds": self.duration_seconds,
            "sample_rate_hz": self.sample_rate_hz,
            "channels": self.channels,
            "codec_name": self.codec_name,
            "reason": self.reason,
        }


def _probe_wave(path: Path) -> AudioProbe:
    try:
        with wave.open(str(path), "rb") as wav:
            channels = wav.getnchannels()
            sample_rate = wav.getframerate()
            frames = wav.getnframes()
            width = wav.getsampwidth()
    except (wave.Error, EOFError, OSError) as exc:
        return AudioProbe(ok=False, backend="wave", reason=f"WAVE_PROBE_ERROR:{type(exc).__name__}")
    if channels <= 0 or sample_rate <= 0 or frames <= 0 or width <= 0:
        return AudioProbe(ok=False, backend="wave", reason="WAVE_INVALID_TECHNICAL_METADATA")
    return AudioProbe(
        ok=True,
        backend="wave",
        duration_seconds=frames / float(sample_rate),
        sample_rate_hz=sample_rate,
        channels=channels,
        codec_name=f"pcm_s{width * 8}le",
    )


def _probe_ffprobe(path: Path) -> AudioProbe:
    executable = shutil.which("ffprobe")
    if not executable:
        return AudioProbe(ok=False, backend="ffprobe", reason="FFPROBE_NOT_AVAILABLE")
    command = [
        executable,
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,sample_rate,channels,duration:format=duration",
        "-of", "json",
        str(path),
    ]
    try:
        proc = subprocess.run(command, check=False, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return AudioProbe(ok=False, backend="ffprobe", reason=f"FFPROBE_EXEC_ERROR:{type(exc).__name__}")
    if proc.returncode != 0:
        return AudioProbe(ok=False, backend="ffprobe", reason="FFPROBE_MEDIA_ERROR")
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return AudioProbe(ok=False, backend="ffprobe", reason="FFPROBE_JSON_ERROR")
    streams = payload.get("streams") or []
    if not streams:
        return AudioProbe(ok=False, backend="ffprobe", reason="NO_AUDIO_STREAM")
    stream = streams[0]
    try:
        rate = int(stream.get("sample_rate")) if stream.get("sample_rate") else None
        channels = int(stream.get("channels")) if stream.get("channels") else None
        raw_duration = stream.get("duration") or (payload.get("format") or {}).get("duration")
        duration = float(raw_duration) if raw_duration not in (None, "N/A", "") else None
    except (TypeError, ValueError):
        return AudioProbe(ok=False, backend="ffprobe", reason="FFPROBE_INVALID_METADATA")
    if not rate or rate <= 0 or not channels or channels <= 0:
        return AudioProbe(ok=False, backend="ffprobe", reason="AUDIO_TECHNICAL_METADATA_MISSING")
    if duration is not None and duration <= 0:
        return AudioProbe(ok=False, backend="ffprobe", reason="AUDIO_DURATION_INVALID")
    return AudioProbe(
        ok=True,
        backend="ffprobe",
        duration_seconds=duration,
        sample_rate_hz=rate,
        channels=channels,
        codec_name=(str(stream.get("codec_name")) if stream.get("codec_name") else None),
    )


def probe_audio(path: str | Path) -> AudioProbe:
    p = Path(path)
    if not p.is_file():
        return AudioProbe(ok=False, backend="none", reason="FILE_NOT_FOUND")
    if p.suffix.lower() == ".wav":
        wav_result = _probe_wave(p)
        if wav_result.ok:
            return wav_result
        # A WAV-labelled file may use a codec unsupported by stdlib wave.
        ff_result = _probe_ffprobe(p)
        return ff_result if ff_result.ok else AudioProbe(
            ok=False,
            backend="wave+ffprobe",
            reason=f"{wav_result.reason};{ff_result.reason}",
        )
    return _probe_ffprobe(p)
