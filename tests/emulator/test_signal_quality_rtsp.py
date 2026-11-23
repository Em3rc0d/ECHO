"""Pre-inference signal validity across the diagnostic RTSP worker.

This uses fake PCM transport and a fake scorer. It requires numpy but no
camera, FFmpeg subprocess, network, checkpoint, credentials or MQTT. These
tests do not certify four-source runtime capacity.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest

import numpy as np

from echo.runtime.event_engine import ThresholdConfig
from scripts.emulator.echo_rtsp_live_worker import CameraStatus, consume_camera


class FakeGate:
    def __init__(self):
        self.slots = 0

    @contextmanager
    def slot(self, cancelled):
        self.slots += 1
        if cancelled():
            raise AssertionError("unexpected source cancellation")
        yield 0.0


class FakeScorer:
    sample_rate_hz = 4
    model_version = "fake-siren"

    def __init__(self):
        self.calls = 0

    def score(self, pcm):
        self.calls += 1
        if not np.all(np.isfinite(pcm)):
            raise AssertionError("invalid PCM reached scorer")
        return {"SIREN": 0.9}


class FakeTransport:
    """Exactly four complete 2 s windows; EOF stops the worker."""
    pcm_values = ((0.5,) * 8, (0.0,) * 8, (0.5,) * 8, (0.5,) * 8)

    def __init__(self, *_args, **_kwargs):
        self.process = None
        self.done = threading.Event()
        self.reason = None
        self.closed = False

    def start(self):
        self.process = SimpleNamespace(returncode=0)

    def chunks(self, stop):
        for chunk in self.pcm_values:
            yield np.asarray(chunk, dtype="<f4").tobytes()
        stop.set()

    def snapshot(self):
        return {
            "cleanup_complete": self.closed,
            "session_duration_seconds": 8.0,
            "process_reaped": self.closed,
            "stderr_tail": [],
        }

    def close(self):
        self.closed = True
        return self.snapshot()

    def stop(self, reason):
        self.reason = reason
        self.done.set()


class AllZeroTransport(FakeTransport):
    pcm_values = ((0.0,) * 8,)


class RtspSignalBoundaryTests(unittest.TestCase):
    def run_transport(self, transport_factory):
        stop = threading.Event()
        args = SimpleNamespace(
            retry_seconds=0.001, max_retry_seconds=0.002,
            queue_seconds=12, idle_seconds=15, rtsp_timeout_seconds=10,
            decoder_threads=1, ffmpeg_bin="ffmpeg",
            reset_backoff_seconds=30,
        )
        scorer = FakeScorer()
        gate = FakeGate()
        row = {
            "source_id": "CAM-SIGNAL",
            "site_id": "LAB",
            "rtsp_uri": "rtsp://localhost/not-contacted",
        }
        observations = []
        with tempfile.TemporaryDirectory() as temp:
            status = CameraStatus(row, Path(temp), "a" * 32)
            original_update = status.update

            def observe(**fields):
                if fields.get("signal_quality") == "NO_SIGNAL":
                    observations.append({
                        "at_before": status.values.get("at"),
                        "at_in_update": fields.get("at"),
                        "scores": fields.get("scores"),
                        "signal_quality": fields["signal_quality"],
                    })
                original_update(**fields)

            status.update = observe
            consume_camera(
                row, args, scorer, gate,
                {"window_seconds": 2, "hop_seconds": 2},
                "fake-test-policy",
                {"SIREN": ThresholdConfig(0.8, 0.4, 2, 1)},
                stop, status, process_factory=transport_factory,
            )
            snapshot = json.loads((Path(temp) / "CAM-SIGNAL.json").read_text())
        return scorer, gate, snapshot, observations

    def test_silence_never_acquires_scorer_and_preserves_no_inference(self):
        scorer, gate, saved, observations = self.run_transport(AllZeroTransport)
        self.assertEqual(scorer.calls, 0)
        self.assertEqual(gate.slots, 0)
        self.assertEqual(saved["windows"], 0)
        self.assertIsNone(saved["at"])
        self.assertEqual(saved["diagnostics"]["signal_quality_checked_windows"], 1)
        self.assertEqual(saved["diagnostics"]["signal_quality_rejected_windows"], 1)
        self.assertEqual(len(observations), 1)
        self.assertIsNone(observations[0]["at_in_update"])
        self.assertEqual(observations[0]["scores"], {})
        self.assertFalse(saved["published_target_events"])

    def test_valid_silence_valid_does_not_bridge_temporal_candidates(self):
        scorer, gate, saved, observations = self.run_transport(FakeTransport)
        self.assertEqual(scorer.calls, 3)
        self.assertEqual(gate.slots, 3)
        self.assertEqual(saved["windows"], 3)
        self.assertEqual(saved["diagnostics"]["signal_quality_checked_windows"], 4)
        self.assertEqual(saved["diagnostics"]["signal_quality_rejected_windows"], 1)
        self.assertEqual(len(observations), 1)
        self.assertIsNotNone(observations[0]["at_before"])
        self.assertIsNone(observations[0]["at_in_update"])
        self.assertEqual(observations[0]["scores"], {})
        events = saved["events"]
        self.assertEqual(
            [event["provenance"]["lifecycle"] for event in events],
            ["CONFIRMED", "CLOSED"],
        )
        self.assertEqual(events[0]["event_id"], events[1]["event_id"])
        self.assertFalse(saved["published_target_events"])


if __name__ == "__main__":
    unittest.main()
