from __future__ import annotations

import struct
import tempfile
import unittest
import wave
from pathlib import Path

from echo.data_foundry.probe import probe_audio


class AudioProbeTests(unittest.TestCase):
    def test_pcm_wave_probe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.wav"
            with wave.open(str(path), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(16000)
                wav.writeframes(b"".join(struct.pack("<h", 500 if i % 2 else -500) for i in range(1600)))
            result = probe_audio(path)
            self.assertTrue(result.ok)
            self.assertEqual(result.backend, "wave")
            self.assertEqual(result.sample_rate_hz, 16000)
            self.assertEqual(result.channels, 1)
            self.assertAlmostEqual(result.duration_seconds or 0.0, 0.1, places=6)

    def test_missing_file_fails(self) -> None:
        result = probe_audio("/definitely/not/present/echo.wav")
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "FILE_NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
