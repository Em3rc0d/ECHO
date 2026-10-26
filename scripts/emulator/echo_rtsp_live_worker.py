#!/usr/bin/env python3
"""Docker-only RTSP live diagnostic inference (not a field acceptance policy).

FFmpeg decodes audio only, with a bounded PCM window buffer. Each source owns
its own TemporalEventEngine and session; audio is never saved to disk.
"""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
import subprocess
import threading
import time

import numpy as np

from demo.server import build_scorer, load_thresholds
from echo.runtime.event_engine import RawInference, TemporalEventEngine

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = ("negative", "glass_shatter", "siren", "vehicle_horn", "silence")


def now():
    return datetime.now(timezone.utc)


def emit(directory: Path, source_id: str, payload: dict):
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (source_id + ".json")
    temp = directory / (source_id + ".tmp")
    temp.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    os.replace(temp, target)


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


def audio_chunks(proc, chunk_size=32768):
    while True:
        raw = proc.stdout.read(chunk_size * 4)
        if not raw:
            break
        yield np.frombuffer(raw, dtype="<f4")


def consume_camera(row, args, scorer, scorer_lock, config, version, thresholds):
    source_id = row["source_id"]
    uri = row["rtsp_uri"]
    state = {"source_id": source_id, "site_id": row.get("site_id", "VMT-EMULATED"),
             "mode": "LAB_RTSP_DIAGNOSTIC_ONLY", "published_target_events": False,
             "rtsp_uri": uri, "state": "STARTING", "scores": {},
             "events": [], "windows": 0, "stream_generation": None}
    generation = 0
    while True:
        generation += 1
        session = f"rtsp:{source_id}:{generation}:{int(time.time()*1000)}"
        engine = TemporalEventEngine(thresholds=thresholds, threshold_version=version)
        state.update(state="CONNECTING", session=session, stream_generation=generation)
        emit(args.output_dir, source_id, state)
        proc = subprocess.Popen(
            ["ffmpeg", "-nostdin", "-loglevel", "error", "-rtsp_transport", "tcp",
             "-i", uri, "-map", "0:a:0", "-vn", "-ac", "1", "-ar",
             str(scorer.sample_rate_hz), "-f", "f32le", "-acodec", "pcm_f32le", "pipe:1"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0,
        )
        began = now()
        try:
            for offset, waveform in feed_pcm_chunks(
                audio_chunks(proc), sample_rate=scorer.sample_rate_hz,
                window_seconds=float(config["window_seconds"]),
                hop_seconds=float(config["hop_seconds"]),
            ):
                end = began + timedelta(seconds=(offset + len(waveform)) / scorer.sample_rate_hz)
                start = began + timedelta(seconds=offset / scorer.sample_rate_hz)
                rms = math.sqrt(float(np.mean(np.square(waveform, dtype=np.float64))))
                peak = float(np.max(np.abs(waveform)))
                with scorer_lock:
                    scores = scorer.score(waveform)
                candidates = [e.to_dict() for e in engine.ingest(RawInference(
                    source_id=source_id, site_id=state["site_id"], stream_session_id=session,
                    window_start_utc=start, window_end_utc=end, scores=scores,
                    model_version=scorer.model_version,
                ))]
                # Real peak envelope for the browser (64 bins over last 6s).
                envelope = [float(np.max(np.abs(part))) for part in
                            np.array_split(waveform, 64)]
                state.update(state="ONLINE", at=now().isoformat(),
                             waveform_envelope=envelope,
                             window_start_utc=start.isoformat(), window_end_utc=end.isoformat(),
                             windows=state["windows"] + 1,
                             scores=scores, rms=rms, peak=peak,
                             events=(state["events"] + candidates)[-20:])
                emit(args.output_dir, source_id, state)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
            state.update(state="RECONNECTING", at=now().isoformat(),
                         last_exit_code=proc.returncode)
            emit(args.output_dir, source_id, state)
            time.sleep(args.retry_seconds)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cameras", type=Path, default=ROOT / "config/emulator/vmt-cameras.json")
    parser.add_argument("--selection", type=Path, default=ROOT / "artifacts/mvp-benchmark/selection.json")
    parser.add_argument("--event-config", type=Path, default=ROOT / "artifacts/mvp-temporal/temporal-event-config.json")
    parser.add_argument("--panns-checkpoint", type=Path, default=ROOT / "artifacts/models/panns/Cnn14_mAP=0.431.pth")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/live-monitor")
    parser.add_argument("--retry-seconds", type=float, default=2.0)
    args = parser.parse_args()
    _, benchmark, _, scorer = build_scorer(args.selection, args.panns_checkpoint, "cpu")
    config, version, thresholds = load_thresholds(args.event_config)
    inventory = json.loads(args.cameras.read_text(encoding="utf-8"))
    rows = inventory["cameras"]
    lock = threading.Lock()
    print(json.dumps({"mode": "LAB_RTSP_DIAGNOSTIC_ONLY", "model": benchmark,
                      "sources": len(rows)}), flush=True)
    for camera in rows:
        row = dict(camera)
        row["rtsp_uri"] = "rtsp://rtsp-server:8554/vmt/cam-" + row["source_id"].split("-")[-1].lower()
        thread = threading.Thread(target=consume_camera,
              args=(row, args, scorer, lock, config, version, thresholds), daemon=True)
        thread.start()
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
