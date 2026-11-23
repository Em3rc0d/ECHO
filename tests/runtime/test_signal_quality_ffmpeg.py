"""Optional lab integration of real FFmpeg PCM decode with the pre-inference gate.

No PANNs model/checkpoint, camera access, MQTT, or real environment is exercised.
This test is reproducible in the Docker image supplying FFmpeg, but is not a
Docker runtime certificate by itself.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from echo.runtime.event_engine import TemporalEventEngine, ThresholdConfig
from echo.runtime.pipeline import EchoReplayPipeline


class HighFalsePositiveScorer:
    sample_rate_hz = 32000
    model_version = "test-high-glass-score"

    def __init__(self):
        self.calls = 0

    def score(self, waveform):
        self.calls += 1
        return {"GLASS_SHATTER": 0.5620440244674683}


class CollectingPublisher:
    def __init__(self):
        self.events = []

    def publish(self, event):
        self.events.append(event)


@unittest.skipUnless(shutil.which("ffmpeg"), "requires ffmpeg in test environment")
class FfmpegSignalQualityIntegrationTests(unittest.TestCase):
    def run_pipeline(self, path):
        scorer = HighFalsePositiveScorer()
        publisher = CollectingPublisher()
        engine = TemporalEventEngine(
            thresholds={"GLASS_SHATTER": ThresholdConfig(
                on_threshold=0.35, off_threshold=0.15,
                confirm_windows=3, release_windows=1,
            )},
            threshold_version="test-only",
        )
        pipeline = EchoReplayPipeline(
            scorer=scorer, event_engine=engine, publishers=[publisher],
            signal_quality_gate_enabled=True,
        )
        summary = pipeline.run_file(
            path, source_id="lab-source", site_id="lab-site",
            window_seconds=6.0, hop_seconds=1.0,
        )
        return scorer, publisher, summary

    def test_60s_exact_zero_is_not_inferred_or_published(self):
        with tempfile.TemporaryDirectory() as folder:
            wav = Path(folder) / "digital-zero.wav"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-f", "lavfi", "-i", "anullsrc=r=32000:cl=mono",
                "-t", "60", "-c:a", "pcm_s16le", "-y", str(wav),
            ], check=True, timeout=60)
            scorer, publisher, summary = self.run_pipeline(wav)
        self.assertEqual(summary["window_count"], 55)
        self.assertEqual(summary["signal_quality_state"], "NO_SIGNAL")
        self.assertEqual(summary["no_signal_window_count"], 55)
        self.assertEqual(summary["scored_window_count"], 0)
        self.assertEqual(summary["event_message_count"], 0)
        self.assertEqual(scorer.calls, 0)
        self.assertEqual(publisher.events, [])

    def test_nonzero_pcm_is_not_rejected_by_magic_amplitude_threshold(self):
        with tempfile.TemporaryDirectory() as folder:
            wav = Path(folder) / "sine.wav"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=32000",
                "-t", "7", "-c:a", "pcm_s16le", "-y", str(wav),
            ], check=True, timeout=60)
            scorer, publisher, summary = self.run_pipeline(wav)
        self.assertEqual(summary["window_count"], 2)
        self.assertEqual(summary["signal_quality_state"], "UNASSESSED_NONZERO")
        self.assertEqual(summary["scored_window_count"], 2)
        self.assertEqual(summary["no_signal_window_count"], 0)
        self.assertEqual(scorer.calls, 2)
        self.assertEqual(publisher.events, [])


if __name__ == "__main__":
    unittest.main()
