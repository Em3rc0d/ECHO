from __future__ import annotations

import struct
import tempfile
import unittest
import wave
from pathlib import Path

from echo.data_foundry.fingerprints import wav_envelope_fingerprint


class FingerprintTests(unittest.TestCase):
    def _write_wave(self, path: Path, samples: list[int]) -> None:
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))

    def test_gain_scaled_wave_has_same_envelope_fingerprint(self) -> None:
        samples = [1000 if i % 200 < 100 else -1000 for i in range(16000)]
        scaled = [2000 if value > 0 else -2000 for value in samples]
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.wav"
            b = Path(tmp) / "b.wav"
            self._write_wave(a, samples)
            self._write_wave(b, scaled)
            self.assertEqual(wav_envelope_fingerprint(a), wav_envelope_fingerprint(b))

    def test_non_wave_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.mp3"
            path.write_bytes(b"not audio")
            self.assertIsNone(wav_envelope_fingerprint(path))


if __name__ == "__main__":
    unittest.main()
