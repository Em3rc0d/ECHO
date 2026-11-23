"""Exact-zero signal-quality regression: no model or acoustic assets needed."""

import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from echo.runtime.event_engine import TemporalEventEngine, ThresholdConfig
from echo.runtime.pipeline import EchoReplayPipeline
from echo.runtime.signal_quality import inspect_pcm_window


class SignalInspectionTests(unittest.TestCase):
    def test_exact_zero_and_signed_zero_never_reach_model(self):
        result = inspect_pcm_window([0.0, -0.0] * 8)
        self.assertEqual((result.state, result.reason), ("NO_SIGNAL", "EXACT_DIGITAL_ZERO"))
        self.assertFalse(result.analysis_allowed)

    def test_nonfinite_empty_and_malformed_fail_closed(self):
        for values, expected in [
            ([], "EMPTY_PCM"),
            ([0.0, math.nan], "NONFINITE_PCM"),
            ([1.0, math.inf], "NONFINITE_PCM"),
            ([float("-inf"), 1.0], "NONFINITE_PCM"),
            ([0.0, "bad"], "NONNUMERIC_PCM"),
        ]:
            with self.subTest(values=values):
                result = inspect_pcm_window(values)
                self.assertEqual(result.state, "INVALID_SIGNAL")
                self.assertEqual(result.reason, expected)

    def test_nonzero_near_silence_is_not_arbitrarily_rejected(self):
        result = inspect_pcm_window([0.0, 1.0 / 32768.0, 0.0])
        self.assertTrue(result.analysis_allowed)
        self.assertEqual(result.state, "UNASSESSED_NONZERO")
        self.assertIn("NOT_FIELD_CALIBRATED", result.reason)


class FakeScorer:
    sample_rate_hz = 2
    model_version = "test-only"
    def __init__(self):
        self.calls = 0

    def score(self, waveform):
        self.calls += 1
        return {"GLASS_SHATTER": 0.9}


class FakePublisher:
    def __init__(self):
        self.messages = []

    def publish(self, payload):
        self.messages.append(payload)


class PipelineBoundaryTests(unittest.TestCase):
    def run_pcm(self, pcm, *, enabled):
        scorer = FakeScorer()
        publisher = FakePublisher()
        engine = TemporalEventEngine(
            thresholds={"GLASS_SHATTER": ThresholdConfig(
                on_threshold=0.5, off_threshold=0.2,
                confirm_windows=2, release_windows=1,
            )},
            threshold_version="test",
        )
        pipeline = EchoReplayPipeline(
            scorer=scorer, event_engine=engine, publishers=[publisher],
            signal_quality_gate_enabled=enabled,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.wav"
            path.write_bytes(b"fixture-not-decoded")
            with patch("echo.runtime.pipeline.decode_audio_f32_mono", return_value=pcm):
                summary = pipeline.run_file(
                    path, source_id="test-cam", site_id="test-site",
                    window_seconds=1.0, hop_seconds=1.0,
                )
        return scorer, publisher, summary

    def test_external_exact_silence_suppresses_scoring_events(self):
        scorer, publisher, summary = self.run_pcm([0.0] * 12, enabled=True)
        self.assertEqual(scorer.calls, 0)
        self.assertEqual(publisher.messages, [])
        self.assertEqual(summary["window_count"], 6)
        self.assertEqual(summary["no_signal_window_count"], 6)
        self.assertEqual(summary["scored_window_count"], 0)
        self.assertEqual(summary["signal_quality_state"], "NO_SIGNAL")

    def test_signal_loss_breaks_temporal_candidate_accumulation(self):
        # One positive then silence then one positive: neither is confirmed.
        scorer, publisher, summary = self.run_pcm([0.5, 0.5, 0.0, 0.0, 0.5, 0.5], enabled=True)
        self.assertEqual(scorer.calls, 2)
        self.assertFalse(publisher.messages)
        self.assertEqual(summary["signal_quality_state"], "PARTIAL_SIGNAL")

    def test_invalid_pcm_is_rejected_without_inference(self):
        scorer, publisher, summary = self.run_pcm([0.3, 0.3, math.nan, 0.0], enabled=True)
        self.assertEqual(scorer.calls, 1)
        self.assertEqual(publisher.messages, [])
        self.assertEqual(summary["invalid_signal_window_count"], 1)

    def test_controlled_replay_remains_unchanged_until_explicit_gate(self):
        scorer, publisher, summary = self.run_pcm([0.0] * 6, enabled=False)
        self.assertEqual(scorer.calls, 3)
        self.assertEqual(
            [msg["provenance"]["lifecycle"] for msg in publisher.messages],
            ["CONFIRMED", "CLOSED"],
        )
        self.assertEqual(summary["signal_quality_state"], "NOT_APPLIED")


if __name__ == "__main__":
    unittest.main()
