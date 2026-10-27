"""Regression definitions only: implementation agent must NOT execute this file.

All process tests use fake pipes/processes; no FFmpeg, sockets or model weights.
"""
from io import BytesIO
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from scripts.emulator.rtsp_process import (
    Backoff, CHUNK_BYTES, InferenceCancelled, RtspSession, ScorerGate,
    StderrTail, ffmpeg_command,
)


class FragmentPipe:
    def __init__(self, pieces):
        self.pieces = iter(pieces)

    def read(self, _size):
        return next(self.pieces, b"")


class TransportTests(unittest.TestCase):
    def test_stdout_and_stderr_are_drained_independently_without_real_processes(self):
        process = Mock(pid=123, stdout=BytesIO(struct.pack('<4f',1,2,3,4)),
                       stderr=BytesIO(b'decoder diagnostic\n'),poll=Mock(return_value=0),
                       wait=Mock(return_value=0))
        factory=Mock(return_value=process)
        session=RtspSession('rtsp://camera/path',32000,factory=factory)
        session.start()
        self.assertEqual(b''.join(session.chunks(threading.Event())),struct.pack('<4f',1,2,3,4))
        self.assertTrue(session.close()['cleanup_complete'])
        self.assertIn('decoder diagnostic',str(session.tail.snapshot()))
        self.assertEqual(factory.call_args.kwargs['stderr'],subprocess.PIPE)
        self.assertEqual(factory.call_args.kwargs['stdout'],subprocess.PIPE)
        self.assertFalse(any(t.is_alive() for t in session.threads))

    def test_backoff_is_bounded_and_does_not_reset_on_one_short_session(self):
        policy = Backoff()
        self.assertEqual([policy.failed() for _ in range(7)], [2, 4, 8, 16, 30, 30, 30])
        self.assertEqual(policy.failed(stable=True), 2)
        self.assertEqual(policy.failures, 1)

    def test_stderr_is_bounded_redacted_and_handles_split_credentials(self):
        tail = StderrTail("rtsp://alice:p%40ss@camera/path?token=topsecret")
        tail.feed(b"[rtsp @ 123] rtsp://alice:p%40")
        tail.feed(b"ss@camera/path?token=topsecret failed\nplain alice p@ss topsecret\n")
        tail.feed(b"p\x01@ss\n")
        first = str(tail.snapshot())
        for secret in ["alice", "p@ss", "p%40ss", "topsecret", "rtsp://"]:
            self.assertNotIn(secret, first)
        tail.feed(b"x" * 4096)
        tail.feed(b"password=not-for-display" * 200)
        tail.feed(b"\n")
        for i in range(100):
            tail.feed((f"error {i}\n").encode())
        tail.finish()
        snapshot = tail.snapshot()
        self.assertLessEqual(len(snapshot["stderr_tail"]), 16)
        self.assertTrue(snapshot["stderr_truncated"])
        self.assertTrue(all(len(line) <= 600 for line in snapshot["stderr_tail"]))

    def test_pcm_short_pipe_reads_are_reassembled_without_padding(self):
        raw = struct.pack("<8f", *range(8))
        session = RtspSession("rtsp://camera/path", 32000)
        session.process = SimpleNamespace(pid=1,poll=lambda:0,stdout=FragmentPipe([raw[:1], raw[1:4], raw[4:13], raw[13:]]))
        session._read_stdout()
        self.assertTrue(session.stdout_done.is_set())
        self.assertEqual(b"".join(session.chunks(threading.Event())), raw)
        self.assertIsNone(session.reason)
        self.assertEqual(session.snapshot()["transport_bytes"], len(raw))

    def test_truncated_pcm_and_overflow_end_the_session_explicitly(self):
        short = RtspSession("rtsp://camera/path", 32000)
        short.process = Mock(stdout=FragmentPipe([b"abc"]), poll=Mock(return_value=None))
        short._read_stdout()
        self.assertEqual(short.reason, "PCM_TRUNCATED")
        full = RtspSession("rtsp://camera/path", 1, queue_seconds=1)
        full.process = Mock(stdout=FragmentPipe([b"\0" * CHUNK_BYTES] * 3), poll=Mock(return_value=None))
        full._read_stdout()
        self.assertEqual(full.reason, "PCM_QUEUE_OVERFLOW")
        self.assertEqual(full.audio.qsize(), 1)
        full.process.terminate.assert_called()
        self.assertEqual(list(full.chunks(threading.Event())), [])

    def test_decode_command_requests_only_audio_and_caps_threads(self):
        command = ffmpeg_command("rtsp://camera/custom", 32000)
        self.assertEqual(command[command.index("-allowed_media_types") + 1], "audio")
        self.assertEqual(command[command.index("-timeout") + 1], "10000000")
        self.assertEqual(command[command.index("-rtsp_transport") + 1], "tcp")
        self.assertLess(command.index("-threads"), command.index("-i"))
        self.assertEqual(command[command.index("-threads") + 1], "1")
        self.assertEqual(command[-1], "pipe:1")

    def test_stall_watchdog_stops_one_process_without_waiting_for_inference(self):
        session = RtspSession("rtsp://camera/path", 32000, clock=lambda: 0)
        session.clock = lambda: 16
        session.process = Mock(poll=Mock(return_value=None))
        with patch.object(session.done, "wait", return_value=False):
            session._watch()
        self.assertEqual(session.reason, "RTSP_IDLE_TIMEOUT")
        session.process.terminate.assert_called_once()

    def test_terminate_timeout_escalates_to_kill_and_reaps_before_close(self):
        session = RtspSession("rtsp://camera/path", 32000)
        session.process = Mock(stdout=BytesIO(), stderr=BytesIO(), poll=Mock(return_value=None))
        session.process.wait.side_effect = [subprocess.TimeoutExpired("ffmpeg", 3), -9]
        result = session.close()
        session.process.kill.assert_called_once()
        self.assertTrue(result["forced_kill"])
        self.assertTrue(result["process_reaped"])
        self.assertTrue(result["cleanup_complete"])
        session.close()
        self.assertEqual(session.process.kill.call_count, 1)

    def test_unreaped_process_does_not_report_cleanup_complete(self):
        session = RtspSession("rtsp://camera/path", 32000)
        session.process = Mock(poll=Mock(return_value=None))
        session.process.wait.side_effect = subprocess.TimeoutExpired("ffmpeg", 2)
        self.assertFalse(session.close()["cleanup_complete"])
        self.assertFalse(session.reaped)

    def test_scorer_gate_cancellation_and_exception_release(self):
        gate = ScorerGate()
        with self.assertRaises(InferenceCancelled):
            with gate.slot(lambda: True):
                self.fail("cancelled source acquired scorer")
        with self.assertRaises(RuntimeError):
            with gate.slot(lambda: False):
                raise RuntimeError("fake scorer failure")
        with gate.slot(lambda: False):
            self.assertTrue(gate.busy)
        self.assertFalse(gate.busy)

    def test_fifo_gate_preserves_source_order_without_parallel_model_calls(self):
        gate, order = ScorerGate(), []
        def work(name):
            with gate.slot(lambda: False):
                order.append(name)
        with gate.slot(lambda: False):
            first = threading.Thread(target=work, args=("CAM-002",))
            first.start()
            with gate.condition:
                self.assertTrue(gate.condition.wait_for(lambda: len(gate.waiters) == 1, 1))
            second = threading.Thread(target=work, args=("CAM-003",))
            second.start()
            with gate.condition:
                self.assertTrue(gate.condition.wait_for(lambda: len(gate.waiters) == 2, 1))
        first.join(1)
        second.join(1)
        self.assertEqual(order, ["CAM-002", "CAM-003"])


class WorkerRecoveryTests(unittest.TestCase):
    def test_unexpected_coordinator_error_is_retried_instead_of_killing_source(self):
        from scripts.emulator.echo_rtsp_live_worker import CameraStatus, supervise_camera
        stop = threading.Event()
        row = {"source_id": "CAM-003", "site_id": "LAB"}
        args = SimpleNamespace(retry_seconds=0.001, max_retry_seconds=0.002)
        def recovered(*_args, **_kwargs):
            stop.set()
        with tempfile.TemporaryDirectory() as directory:
            status = CameraStatus(row, Path(directory), "a" * 32)
            with patch("scripts.emulator.echo_rtsp_live_worker.consume_camera") as consume:
                def calls(*pos, **kw):
                    if consume.call_count == 1:
                        raise RuntimeError("credential must not be logged")
                    recovered()
                consume.side_effect = calls
                supervise_camera(row, args, None, None, None, None, None, stop, status)
                self.assertEqual(consume.call_count, 2)
            saved = json.loads((Path(directory) / "CAM-003.json").read_text())
        self.assertEqual(saved["diagnostics"]["reconnect_reason"], "SOURCE_THREAD_EXCEPTION")
        self.assertNotIn("credential", json.dumps(saved))

    def test_source_recovers_after_exit_one_with_new_generation_and_fresh_engine(self):
        import numpy as np
        from echo.runtime.event_engine import ThresholdConfig
        from scripts.emulator.echo_rtsp_live_worker import CameraStatus, consume_camera
        stop = threading.Event()
        attempts, sessions = [], []

        class FakeTransport:
            def __init__(self, *_args, **_kwargs):
                self.index = len(attempts)
                attempts.append(self)
                self.process = None
                self.done = threading.Event()
                self.reason = None
                self.closed = False
            def start(self):
                self.process = SimpleNamespace(returncode=1 if self.index == 0 else 0)
            def chunks(self, _stop):
                if self.index:
                    yield np.ones(64 * 6, dtype="<f4").tobytes()
                    stop.set()
            def snapshot(self):
                return {"session_duration_seconds": 1, "process_reaped": True,
                        "cleanup_complete": self.closed, "stderr_tail": ["fake exit 1"] if not self.index else []}
            def close(self):
                self.closed = True
                return self.snapshot()
            def stop(self, reason):
                self.reason = reason
                self.done.set()

        args = SimpleNamespace(retry_seconds=0.001, max_retry_seconds=0.002,
            queue_seconds=12, idle_seconds=15, rtsp_timeout_seconds=10,
            decoder_threads=1, ffmpeg_bin="ffmpeg", reset_backoff_seconds=30)
        scorer = SimpleNamespace(sample_rate_hz=64, model_version="fake-model",
                                  score=lambda _wave: {"SIREN": 0.9})
        row = {"source_id": "CAM-003", "site_id": "LAB", "rtsp_uri": "rtsp://camera/siren"}
        with tempfile.TemporaryDirectory() as directory:
            status = CameraStatus(row, Path(directory), "a" * 32)
            original_update = status.update
            def track(**fields):
                if "session" in fields:
                    sessions.append(fields["session"])
                original_update(**fields)
            status.update = track
            consume_camera(row, args, scorer, ScorerGate(), {"window_seconds": 6, "hop_seconds": 1},
                "fake-policy", {"SIREN": ThresholdConfig(.8, .4, 1, 1)}, stop, status,
                process_factory=FakeTransport)
            saved = json.loads((Path(directory) / "CAM-003.json").read_text())
        self.assertEqual(len(attempts), 2)
        self.assertEqual(saved["stream_generation"], 2)
        self.assertEqual(saved["windows"], 1)
        self.assertNotEqual(sessions[0], sessions[1])
        self.assertEqual(saved["state"], "STOPPED")
        self.assertFalse(saved["published_target_events"])
        self.assertEqual([e["provenance"]["lifecycle"] for e in saved["events"]], ["CONFIRMED", "CLOSED"])
        self.assertTrue(all(e["stream_session_id"] == sessions[1] for e in saved["events"]))
        self.assertNotIn("rtsp_uri", saved)

    def test_configured_rtsp_path_and_site_are_not_derived_from_camera_number(self):
        from scripts.emulator.echo_rtsp_live_worker import camera_rows
        rows = camera_rows({"site_id": "LAB", "cameras": [{"source_id": "CAM-003", "rtsp_path": "custom/siren"}]}, "rtsp://camera:8554")
        self.assertEqual(rows[0]["rtsp_uri"], "rtsp://camera:8554/custom/siren")
        self.assertEqual(rows[0]["site_id"], "LAB")

    def test_heartbeat_never_refreshes_inference_time_and_sources_are_isolated(self):
        from scripts.emulator.echo_rtsp_live_worker import CameraStatus
        with tempfile.TemporaryDirectory() as directory:
            first = CameraStatus({"source_id": "CAM-001", "site_id": "LAB"}, Path(directory), "a" * 32)
            second = CameraStatus({"source_id": "CAM-003", "site_id": "LAB"}, Path(directory), "a" * 32)
            first.update(at="2026-10-26T10:00:00+00:00", windows=161)
            second.update(state="RECONNECTING")
            first.publish()
            second.publish()
            one = json.loads((Path(directory) / "CAM-001.json").read_text())
            three = json.loads((Path(directory) / "CAM-003.json").read_text())
        self.assertEqual(one["at"], "2026-10-26T10:00:00+00:00")
        self.assertIn("updated_at", one)
        self.assertIsNone(three["at"])
        self.assertEqual(three["windows"], 0)


if __name__ == "__main__":
    unittest.main()
