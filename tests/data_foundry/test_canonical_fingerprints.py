from __future__ import annotations

from array import array
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import wave

from echo.data_foundry.canonical_fingerprints import canonical_audio_fingerprint, fingerprint_distance


def write_wave(path: Path, *, frequency: float, modulation: float, sample_rate: int = 16000, stereo: bool = False, amplitude: float = 0.65) -> None:
    seconds = 2.0
    channels = 2 if stereo else 1
    values: list[int] = []
    for i in range(int(sample_rate * seconds)):
        t = i / float(sample_rate)
        envelope = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(2 * math.pi * modulation * t))
        value = int(32767 * amplitude * envelope * math.sin(2 * math.pi * frequency * t))
        if stereo:
            values.extend([value, int(value * 0.8)])
        else:
            values.append(value)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(array("h", values).tobytes())


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg required for canonical fingerprint fixtures")
class CanonicalFingerprintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        policy = json.loads(Path("configs/data_foundry/near_duplicate_policy.v1.json").read_text(encoding="utf-8"))
        cls.max_distance = float(policy["comparison"]["candidate_max_distance"])

    def test_transforms_stay_close_and_independent_audio_stays_far(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = root / "original.wav"
            write_wave(original, frequency=440.0, modulation=2.0)
            mp3 = root / "reencoded.mp3"
            gain = root / "gain.wav"
            stereo_resampled = root / "stereo-resampled.wav"
            independent = root / "independent.wav"
            write_wave(independent, frequency=880.0, modulation=3.7)
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(original), "-codec:a", "libmp3lame", "-b:a", "128k", str(mp3)], check=True)
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(original), "-af", "volume=0.35", str(gain)], check=True)
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(original), "-ar", "44100", "-ac", "2", str(stereo_resampled)], check=True)

            base = canonical_audio_fingerprint(original)
            self.assertLessEqual(fingerprint_distance(base, canonical_audio_fingerprint(mp3)), self.max_distance)
            self.assertLessEqual(fingerprint_distance(base, canonical_audio_fingerprint(gain)), self.max_distance)
            self.assertLessEqual(fingerprint_distance(base, canonical_audio_fingerprint(stereo_resampled)), self.max_distance)
            self.assertGreater(fingerprint_distance(base, canonical_audio_fingerprint(independent)), self.max_distance)

    def test_repeated_decode_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.wav"
            write_wave(path, frequency=523.25, modulation=1.5)
            first = canonical_audio_fingerprint(path)
            second = canonical_audio_fingerprint(path)
            self.assertEqual(first["canonical_pcm_sha256"], second["canonical_pcm_sha256"])
            self.assertEqual(first["vector_sha256"], second["vector_sha256"])
            self.assertEqual(first["vector"], second["vector"])


if __name__ == "__main__":
    unittest.main()
