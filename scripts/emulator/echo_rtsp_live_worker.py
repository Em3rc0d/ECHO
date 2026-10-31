#!/usr/bin/env python3
"""Docker-only diagnostic RTSP inference with isolated source supervision.

No accepted target publication, audio recording, model or threshold changes.
Transport draining and status heartbeats continue independently of inference.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
import re
import signal
import sys
import threading
import time
from urllib.parse import urlsplit
from uuid import uuid4

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from echo.runtime.event_engine import RawInference, TemporalEventEngine
from scripts.emulator.rtsp_process import Backoff, InferenceCancelled, RtspSession, ScorerGate


def now():
    return datetime.now(timezone.utc)


def emit(directory: Path, source_id: str, payload: dict):
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (source_id + ".json")
    temp = directory / (source_id + ".tmp")
    temp.write_text(json.dumps(payload, sort_keys=True, allow_nan=False), encoding="utf-8")
    os.replace(temp, target)


class CameraStatus:
    def __init__(self, row, directory, worker_instance):
        self.directory = directory
        self.lock = threading.RLock()
        self.transport = None
        self.phase = "STARTING"
        self.phase_started = time.monotonic()
        self.values = {"source_id": row["source_id"], "site_id": row["site_id"],
                       "mode": "LAB_RTSP_DIAGNOSTIC_ONLY", "published_target_events": False,
                       "state": "STARTING", "at": None, "scores": {}, "waveform_envelope": [],
                       "events": [], "windows": 0, "stream_generation": 0,
                       "diagnostics": {"worker_instance_id": worker_instance, "session_windows": 0,
                                       "consecutive_failures": 0, "backoff_seconds": 0}}

    def update(self, **fields):
        with self.lock:
            self.values.update(fields)

    def diagnostics(self, **fields):
        with self.lock:
            self.values["diagnostics"].update(fields)

    def attach(self, transport):
        with self.lock:
            self.transport = transport

    def set_phase(self, phase):
        with self.lock:
            self.phase = phase
            self.phase_started = time.monotonic()

    def append_events(self, events):
        with self.lock:
            self.values["events"] = (self.values["events"] + events)[-20:]

    def publish(self):
        with self.lock:
            diagnostics = {**self.values["diagnostics"], "phase": self.phase,
                           "phase_seconds": round(time.monotonic() - self.phase_started, 3)}
            if self.transport is not None:
                diagnostics.update(self.transport.snapshot())
            payload = {**self.values, "updated_at": now().isoformat(), "diagnostics": diagnostics}
            emit(self.directory, self.values["source_id"], payload)

    def safe_publish(self):
        try:
            self.publish()
        except (OSError, ValueError) as exc:
            print(json.dumps({"kind": "snapshot_write_failed", "source_id": self.values["source_id"],
                              "error_type": type(exc).__name__}), flush=True)


def feed_pcm_chunks(chunks, *, sample_rate, window_seconds=6, hop_seconds=1):
    """Yield overlapping complete windows; no padding and no unbounded retention."""
    width = int(sample_rate * window_seconds)
    step = int(sample_rate * hop_seconds)
    if step <= 0 or width < step:
        raise ValueError("require 0 < hop <= window")
    samples = np.empty(0, dtype=np.float32)
    frame_position = 0
    for chunk in chunks:
        samples = np.concatenate((samples, chunk))
        while len(samples) >= width:
            yield frame_position, samples[:width].copy()
            samples = samples[step:]
            frame_position += step


def audio_chunks(transport, stop_event):
    for raw in transport.chunks(stop_event):
        yield np.frombuffer(raw, dtype="<f4")


def consume_camera(row, args, scorer, gate, config, version, thresholds, stop_event,
                   status, *, process_factory=RtspSession, startup_delay=0):
    source_id = row["source_id"]
    backoff = Backoff(args.retry_seconds, args.max_retry_seconds)
    generation = status.values["stream_generation"]
    if stop_event.wait(startup_delay):
        status.update(state="STOPPED")
        return
    while not stop_event.is_set():
        generation += 1
        session = f"rtsp:{source_id}:{generation}:{uuid4().hex}"
        engine = TemporalEventEngine(thresholds=thresholds, threshold_version=version)
        transport = process_factory(row["rtsp_uri"], scorer.sample_rate_hz,
                    queue_seconds=args.queue_seconds, idle_seconds=args.idle_seconds,
                    timeout_seconds=args.rtsp_timeout_seconds, threads=args.decoder_threads,
                    binary=args.ffmpeg_bin)
        status.attach(transport)
        status.set_phase("CONNECTING")
        status.update(state="CONNECTING", session=session, stream_generation=generation,
                      at=None, scores={}, waveform_envelope=[], rms=None, peak=None,
                      window_start_utc=None, window_end_utc=None)
        status.diagnostics(session_windows=0, backoff_seconds=0, next_retry_utc=None,
                           decoder_threads=args.decoder_threads, last_error_type=None,
                           model_wait_seconds=0, inference_seconds=0)
        status.safe_publish()
        windows, last_end, reason = 0, None, None
        try:
            transport.start()
            began = now()
            status.set_phase("BUFFERING")
            for offset, waveform in feed_pcm_chunks(audio_chunks(transport, stop_event),
                    sample_rate=scorer.sample_rate_hz, window_seconds=float(config["window_seconds"]),
                    hop_seconds=float(config["hop_seconds"])):
                if stop_event.is_set() or transport.done.is_set():
                    break
                end = began + timedelta(seconds=(offset + len(waveform)) / scorer.sample_rate_hz)
                start = began + timedelta(seconds=offset / scorer.sample_rate_hz)
                status.set_phase("WAITING_FOR_MODEL")
                with gate.slot(lambda: stop_event.is_set() or transport.done.is_set()) as waited:
                    status.diagnostics(model_wait_seconds=round(waited, 3))
                    status.set_phase("INFERENCE")
                    scoring_started = time.monotonic()
                    scores = scorer.score(waveform)
                    status.diagnostics(inference_seconds=round(time.monotonic() - scoring_started, 3))
                if stop_event.is_set() or transport.done.is_set():
                    break
                candidates = [e.to_dict() for e in engine.ingest(RawInference(
                    source_id=source_id, site_id=row["site_id"], stream_session_id=session,
                    window_start_utc=start, window_end_utc=end, scores=scores,
                    model_version=scorer.model_version))]
                status.append_events(candidates)
                windows += 1
                last_end = end
                status.set_phase("READING")
                status.diagnostics(session_windows=windows)
                status.update(state="ONLINE", at=now().isoformat(),
                              waveform_envelope=[float(np.max(np.abs(part))) for part in np.array_split(waveform, 64)],
                              window_start_utc=start.isoformat(), window_end_utc=end.isoformat(),
                              windows=status.values["windows"] + 1, scores=scores,
                              rms=math.sqrt(float(np.mean(np.square(waveform, dtype=np.float64)))),
                              peak=float(np.max(np.abs(waveform))))
                status.safe_publish()
        except InferenceCancelled:
            reason = "SHUTDOWN" if stop_event.is_set() else transport.reason or "INFERENCE_CANCELLED"
        except Exception as exc:
            reason = "SPAWN_ERROR" if transport.process is None else "SOURCE_PROCESSING_ERROR"
            status.diagnostics(last_error_type=type(exc).__name__)
            transport.stop(reason)
        finally:
            reason = reason or transport.reason or ("SHUTDOWN" if stop_event.is_set() else "RTSP_EOF")
            status.set_phase("REAPING")
            result = transport.close()
            while not result["cleanup_complete"]:
                status.update(state="REAPING")
                status.diagnostics(reconnect_reason="PROCESS_REAP_PENDING")
                status.safe_publish()
                if stop_event.wait(1):
                    return
                result = transport.close()
            code = transport.process.returncode if transport.process else None
            if reason == "RTSP_EOF" and code not in (None, 0, -15):
                reason = "FFMPEG_EXIT_NONZERO"
            try:
                status.append_events([e.to_dict() for e in engine.close_session(
                    source_id=source_id, site_id=row["site_id"], stream_session_id=session,
                    end_utc=last_end or now(), model_version=scorer.model_version)])
            except Exception as exc:
                status.diagnostics(event_close_error_type=type(exc).__name__)
            status.attach(None)
            status.diagnostics(**result, reconnect_reason=reason, last_exit_code=code,
                               last_session_duration_seconds=result["session_duration_seconds"],
                               last_session_windows=windows)
            status.update(last_exit_code=code, state="STOPPED" if stop_event.is_set() else "RECONNECTING",
                          scores={}, waveform_envelope=[], rms=None, peak=None)
            print(json.dumps({"kind": "rtsp_session_end", "source_id": source_id,
                              "generation": generation, "session": session, "reason": reason,
                              "exit_code": code, "session_windows": windows, **result},
                             sort_keys=True), flush=True)
        if stop_event.is_set():
            status.set_phase("STOPPED")
            status.safe_publish()
            return
        stable = windows >= 3 and result["session_duration_seconds"] >= args.reset_backoff_seconds
        delay = backoff.failed(stable=stable)
        status.set_phase("BACKOFF")
        status.diagnostics(backoff_seconds=delay, consecutive_failures=backoff.failures,
                           next_retry_utc=(now() + timedelta(seconds=delay)).isoformat())
        print(json.dumps({"kind": "rtsp_retry_scheduled", "source_id": source_id,
                          "generation": generation, "reason": reason, "backoff_seconds": delay,
                          "consecutive_failures": backoff.failures}), flush=True)
        status.safe_publish()
        if stop_event.wait(delay):
            status.update(state="STOPPED")
            status.set_phase("STOPPED")
            status.safe_publish()
            return


def supervise_camera(row, args, scorer, gate, config, version, thresholds, stop_event, status, **kwargs):
    """Recover unexpected coordinator exceptions without abandoning an old child."""
    failures = Backoff(args.retry_seconds, args.max_retry_seconds)
    while not stop_event.is_set():
        try:
            consume_camera(row, args, scorer, gate, config, version, thresholds, stop_event, status, **kwargs)
            return
        except Exception as exc:
            status.update(state="REAPING", scores={}, waveform_envelope=[])
            status.set_phase("REAPING")
            status.diagnostics(reconnect_reason="SOURCE_THREAD_EXCEPTION", last_error_type=type(exc).__name__)
            transport = status.transport
            if transport is not None:
                transport.stop("SOURCE_THREAD_EXCEPTION")
                while not stop_event.is_set():
                    try:
                        result = transport.close()
                        if result["cleanup_complete"]:
                            status.diagnostics(**result)
                            status.attach(None)
                            break
                    except Exception as cleanup_error:
                        status.diagnostics(last_error_type=type(cleanup_error).__name__)
                    status.safe_publish()
                    stop_event.wait(1)
                if status.transport is not None:
                    return
            delay = failures.failed()
            status.update(state="RECONNECTING")
            status.set_phase("BACKOFF")
            status.diagnostics(backoff_seconds=delay, consecutive_failures=failures.failures,
                               next_retry_utc=(now() + timedelta(seconds=delay)).isoformat())
            status.safe_publish()
            if stop_event.wait(delay):
                return


def camera_rows(inventory, rtsp_base):
    base = urlsplit(rtsp_base)
    if base.scheme not in {"rtsp", "rtsps"} or not base.hostname or base.query or base.fragment:
        raise ValueError("invalid RTSP base configuration")
    rows, seen = [], set()
    for camera in inventory["cameras"]:
        row = dict(camera)
        identifier, path = row["source_id"], row["rtsp_path"]
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", identifier) or identifier in seen:
            raise ValueError("invalid or duplicate source identity")
        if not re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*", path):
            raise ValueError("invalid configured RTSP path")
        seen.add(identifier)
        row["site_id"] = row.get("site_id", inventory.get("site_id", "VMT-EMULATED"))
        row["rtsp_uri"] = rtsp_base.rstrip("/") + "/" + path
        rows.append(row)
    if not rows:
        raise ValueError("at least one source is required")
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cameras", type=Path, default=ROOT / "config/emulator/vmt-cameras.json")
    parser.add_argument("--selection", type=Path, default=ROOT / "artifacts/mvp-benchmark/selection.json")
    parser.add_argument("--event-config", type=Path, default=ROOT / "artifacts/mvp-temporal/temporal-event-config.json")
    parser.add_argument("--panns-checkpoint", type=Path, default=ROOT / "artifacts/models/panns/Cnn14_mAP=0.431.pth")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/live-monitor")
    parser.add_argument("--rtsp-base", default=os.environ.get("ECHO_RTSP_BASE", "rtsp://rtsp-server:8554"))
    parser.add_argument("--retry-seconds", type=float, default=2.0)
    parser.add_argument("--max-retry-seconds", type=float, default=30.0)
    parser.add_argument("--reset-backoff-seconds", type=float, default=30.0)
    parser.add_argument("--queue-seconds", type=float, default=12.0)
    parser.add_argument("--idle-seconds", type=float, default=15.0)
    parser.add_argument("--rtsp-timeout-seconds", type=float, default=10.0)
    parser.add_argument("--startup-stagger-seconds", type=float, default=0.25)
    parser.add_argument("--decoder-threads", type=int, default=1)
    parser.add_argument("--ffmpeg-bin", default="ffmpeg")
    args = parser.parse_args()
    numbers = [args.retry_seconds, args.max_retry_seconds, args.reset_backoff_seconds,
               args.queue_seconds, args.idle_seconds, args.rtsp_timeout_seconds, args.startup_stagger_seconds]
    if not all(math.isfinite(n) for n in numbers) or not 0 < args.retry_seconds <= args.max_retry_seconds <= 300 or not (
        0 < args.queue_seconds <= 60 and args.idle_seconds > 0 and args.rtsp_timeout_seconds > 0
        and args.reset_backoff_seconds > 0 and args.startup_stagger_seconds >= 0 and 1 <= args.decoder_threads <= 4):
        parser.error("invalid bounded retry/queue/timeout/thread configuration")
    rows = camera_rows(json.loads(args.cameras.read_text(encoding="utf-8")), args.rtsp_base)
    from demo.server import build_scorer, load_thresholds
    _, benchmark, _, scorer = build_scorer(args.selection, args.panns_checkpoint, "cpu")
    config, version, thresholds = load_thresholds(args.event_config)
    gate, stop_event = ScorerGate(), threading.Event()
    worker_instance = uuid4().hex
    statuses = [CameraStatus(row, args.output_dir, worker_instance) for row in rows]
    threads = []
    signal.signal(signal.SIGTERM, lambda *_: stop_event.set())
    signal.signal(signal.SIGINT, lambda *_: stop_event.set())
    print(json.dumps({"mode": "LAB_RTSP_DIAGNOSTIC_ONLY", "model": benchmark,
                      "sources": len(rows), "worker_instance_id": worker_instance}), flush=True)
    for index, (row, status) in enumerate(zip(rows, statuses)):
        thread = threading.Thread(target=supervise_camera,
            args=(row, args, scorer, gate, config, version, thresholds, stop_event, status),
            kwargs={"startup_delay": index * args.startup_stagger_seconds},
            name="source-" + row["source_id"], daemon=True)
        threads.append(thread)
        thread.start()
    try:
        while not stop_event.wait(1):
            for status, thread in zip(statuses, threads):
                if not thread.is_alive():
                    status.update(state="WORKER_STOPPED")
                    status.diagnostics(reconnect_reason="SOURCE_THREAD_STOPPED")
                status.safe_publish()
    finally:
        stop_event.set()
        for status in statuses:
            if status.transport is not None:
                status.transport.stop("SHUTDOWN")
        deadline = time.monotonic() + 10
        for thread in threads:
            thread.join(timeout=max(0, deadline - time.monotonic()))
        for status, thread in zip(statuses, threads):
            if not thread.is_alive() and status.transport is None:
                status.update(state="STOPPED")
                status.set_phase("STOPPED")
            status.safe_publish()
    return 1 if any(t.is_alive() for t in threads) or any(s.transport and not s.transport.closed for s in statuses) else 0


if __name__ == "__main__":
    raise SystemExit(main())
