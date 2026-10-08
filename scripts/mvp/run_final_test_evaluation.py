#!/usr/bin/env python3
"""Run the frozen ECHO MVP temporal evaluation on the benchmark test split.

No parameter is selected or modified here. The script consumes the canonical
ECHO-MVP-001-TEMPORAL-CONTROLLED-v1 policy and evaluates it once on deterministic
long streams composed from the frozen test split.

Important boundary: positive test clips were previously exercised by a wiring
smoke, but test metrics were not used to select the model or temporal policy.
This is the first metric-bearing temporal test evaluation.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
import wave

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echo.modeling.audio import decode_audio_f32_mono
from echo.modeling.inference import EmbeddingHeadScorer
from echo.modeling.manifest import MVP_TARGETS, BenchmarkRow, load_benchmark_manifest
from echo.modeling.media_index import load_media_index
from echo.runtime.event_engine import RawInference, TemporalEventEngine, ThresholdConfig
from echo.runtime.replay import iter_replay_windows

TARGETS = tuple(MVP_TARGETS)
EPOCH = datetime(2000, 1, 1, tzinfo=timezone.utc)


def stable_key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def edge_fade(values, sample_rate_hz: int, seconds: float = 0.02):
    import numpy as np
    audio = np.asarray(values, dtype=np.float32).copy()
    count = min(int(round(sample_rate_hz * seconds)), audio.size // 2)
    if count <= 0:
        return audio
    ramp = np.linspace(0.0, 1.0, count, endpoint=True, dtype=np.float32)
    audio[:count] *= ramp
    audio[-count:] *= ramp[::-1]
    return audio


def write_wav(path: Path, values, sample_rate_hz: int) -> None:
    import numpy as np
    audio = np.asarray(values, dtype=np.float32)
    audio = np.clip(audio, -1.0, 1.0)
    pcm = (audio * 32767.0).round().astype("<i2", copy=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate_hz)
        handle.writeframes(pcm.tobytes())


class AudioPool:
    def __init__(self, *, media: dict[str, str], sample_rate_hz: int, max_positive_seconds: float):
        self.media = media
        self.sample_rate_hz = sample_rate_hz
        self.max_positive_samples = int(round(sample_rate_hz * max_positive_seconds))
        self.cache = {}

    def decoded(self, row: BenchmarkRow):
        if row.media_sha256 not in self.cache:
            self.cache[row.media_sha256] = edge_fade(
                decode_audio_f32_mono(
                    self.media[row.media_sha256],
                    sample_rate_hz=self.sample_rate_hz,
                ),
                self.sample_rate_hz,
            )
        return self.cache[row.media_sha256]

    def positive(self, row: BenchmarkRow):
        audio = self.decoded(row)
        if audio.size <= self.max_positive_samples:
            return audio.copy()
        start = (audio.size - self.max_positive_samples) // 2
        return audio[start:start + self.max_positive_samples].copy()


def build_streams(rows: list[BenchmarkRow], pool: AudioPool, output_dir: Path):
    import numpy as np

    positives = sorted(
        [row for row in rows if any(t in row.positive_labels for t in TARGETS)],
        key=lambda r: stable_key("test-positive:" + r.asset_id),
    )
    backgrounds = sorted(
        [
            row for row in rows
            if not row.positive_labels
            and all(row.supervision.get(t) == 0 for t in TARGETS)
        ],
        key=lambda r: stable_key("test-background:" + r.asset_id),
    )
    if not positives or not backgrounds:
        raise RuntimeError("test split lacks positives or pure backgrounds")

    truth = []
    mixed_chunks = []
    cursor = 0
    bg_cursor = 0

    def add_background(seconds: float):
        nonlocal cursor, bg_cursor
        remaining = int(round(seconds * pool.sample_rate_hz))
        while remaining > 0:
            row = backgrounds[bg_cursor % len(backgrounds)]
            bg_cursor += 1
            audio = pool.decoded(row)
            take = min(remaining, int(audio.size))
            mixed_chunks.append(audio[:take])
            cursor += take
            remaining -= take

    add_background(10.0)
    gaps = (4.0, 6.0, 3.0, 8.0, 5.0)
    for i, row in enumerate(positives):
        audio = pool.positive(row)
        start = cursor
        mixed_chunks.append(audio)
        cursor += int(audio.size)
        end = cursor
        truth.append({
            "asset_id": row.asset_id,
            "media_sha256": row.media_sha256,
            "labels": [t for t in row.positive_labels if t in TARGETS],
            "start_seconds": start / pool.sample_rate_hz,
            "end_seconds": end / pool.sample_rate_hz,
        })
        if i < len(positives) - 1:
            add_background(gaps[i % len(gaps)])
    add_background(10.0)

    mixed = np.concatenate(mixed_chunks).astype(np.float32, copy=False)
    mixed_path = output_dir / "test-mixed.wav"
    write_wav(mixed_path, mixed, pool.sample_rate_hz)

    negative_chunks = [pool.decoded(row) for row in backgrounds]
    negative = np.concatenate(negative_chunks).astype(np.float32, copy=False)
    negative_path = output_dir / "test-negative.wav"
    write_wav(negative_path, negative, pool.sample_rate_hz)

    return {
        "positive_rows": len(positives),
        "pure_background_rows": len(backgrounds),
        "mixed": {
            "path": str(mixed_path),
            "sha256": sha256_file(mixed_path),
            "duration_seconds": mixed.size / pool.sample_rate_hz,
            "ground_truth": truth,
        },
        "negative": {
            "path": str(negative_path),
            "sha256": sha256_file(negative_path),
            "duration_seconds": negative.size / pool.sample_rate_hz,
            "ground_truth": [],
        },
    }


def load_thresholds(config: dict):
    return {
        label: ThresholdConfig(
            on_threshold=float(config["labels"][label]["on_threshold"]),
            off_threshold=float(config["labels"][label]["off_threshold"]),
            confirm_windows=int(config["labels"][label]["confirm_windows"]),
            release_windows=int(config["labels"][label]["release_windows"]),
            cooldown_seconds=float(config["labels"][label]["cooldown_seconds"]),
        )
        for label in TARGETS
    }


def score_stream(*, path: Path, scorer, window_seconds: float, hop_seconds: float, output: Path):
    waveform = decode_audio_f32_mono(path, sample_rate_hz=scorer.sample_rate_hz)
    rows = []
    with output.open("w", encoding="utf-8") as handle:
        for window in iter_replay_windows(
            waveform,
            sample_rate_hz=scorer.sample_rate_hz,
            window_seconds=window_seconds,
            hop_seconds=hop_seconds,
            pad_final=True,
        ):
            row = {
                "window_index": window.index,
                "start_seconds": window.start_sample / scorer.sample_rate_hz,
                "end_seconds": window.end_sample / scorer.sample_rate_hz,
                "scores": scorer.score(window.waveform),
            }
            rows.append(row)
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            if len(rows) % 100 == 0:
                print(f"{path.name}: {len(rows)} windows", flush=True)
    return rows


def run_engine(*, scores: list[dict], thresholds, threshold_version: str, scenario_id: str, window_seconds: float):
    engine = TemporalEventEngine(thresholds=thresholds, threshold_version=threshold_version)
    events = {}
    last_end = 0.0
    for row in scores:
        start = float(row["start_seconds"])
        end = float(row["end_seconds"])
        last_end = max(last_end, end)
        inf = RawInference(
            source_id=scenario_id,
            site_id="ECHO-MVP-FINAL-TEST",
            stream_session_id=scenario_id,
            window_start_utc=EPOCH + timedelta(seconds=start),
            window_end_utc=EPOCH + timedelta(seconds=end),
            scores=row["scores"],
            model_version="ECHO-MVP-001-PANNS-CNN14-HEAD",
        )
        for event in engine.ingest(inf):
            rec = events.setdefault(event.event_id, {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "onset_seconds": (event.onset_utc - EPOCH).total_seconds(),
                "confirmed_at_seconds": None,
                "end_seconds": None,
            })
            if event.lifecycle == "CONFIRMED":
                rec["confirmed_at_seconds"] = end
            elif event.lifecycle == "CLOSED" and event.end_utc is not None:
                rec["end_seconds"] = (event.end_utc - EPOCH).total_seconds()
    for event in engine.close_session(
        source_id=scenario_id,
        site_id="ECHO-MVP-FINAL-TEST",
        stream_session_id=scenario_id,
        end_utc=EPOCH + timedelta(seconds=last_end),
        model_version="ECHO-MVP-001-PANNS-CNN14-HEAD",
    ):
        rec = events.setdefault(event.event_id, {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "onset_seconds": (event.onset_utc - EPOCH).total_seconds(),
            "confirmed_at_seconds": None,
            "end_seconds": None,
        })
        if event.end_utc is not None:
            rec["end_seconds"] = (event.end_utc - EPOCH).total_seconds()
    return list(events.values())


def evaluate(*, label: str, truth: list[dict], predictions: list[dict], duration_seconds: float, window_seconds: float):
    truths = [t for t in truth if label in t["labels"]]
    preds = [p for p in predictions if p["event_type"] == label and p["confirmed_at_seconds"] is not None]
    unmatched = set(range(len(truths)))
    matched = 0
    false = 0
    latencies = []
    for pred in sorted(preds, key=lambda p: p["confirmed_at_seconds"]):
        at = float(pred["confirmed_at_seconds"])
        candidates = [
            i for i in unmatched
            if float(truths[i]["start_seconds"]) <= at <= float(truths[i]["end_seconds"]) + window_seconds
        ]
        if not candidates:
            false += 1
            continue
        i = min(candidates, key=lambda j: abs(at - float(truths[j]["start_seconds"])))
        unmatched.remove(i)
        matched += 1
        latencies.append(at - float(truths[i]["start_seconds"]))

    precision = matched / len(preds) if preds else (1.0 if not truths else 0.0)
    recall = matched / len(truths) if truths else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    hours = duration_seconds / 3600.0
    return {
        "truth_events": len(truths),
        "predicted_events": len(preds),
        "matched_events": matched,
        "missed_events": len(unmatched),
        "false_alarm_events": false,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_alarms_per_hour": false / hours if hours else 0.0,
        "median_detection_latency_seconds": (
            sorted(latencies)[len(latencies)//2] if latencies else None
        ),
    }


def resolve_head(selection_path: Path, selection: dict) -> Path:
    raw = Path(str((selection.get("winner") or {}).get("checkpoint") or ""))
    name = Path(str(raw).replace("\\", "/")).name
    candidates = [raw, selection_path.resolve().parent / "panns" / name]
    if not raw.is_absolute():
        candidates.append((ROOT / raw).resolve())
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError("selected ECHO head checkpoint not found")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "MK1/mining-site/materialization/mvp-benchmark-manifest.jsonl")
    parser.add_argument("--media-index", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--temporal-config", type=Path, required=True)
    parser.add_argument("--panns-checkpoint", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/mvp-final-test")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    config = json.loads(args.temporal_config.read_text(encoding="utf-8"))
    if config.get("threshold_version") != "ECHO-MVP-001-TEMPORAL-CONTROLLED-v1":
        raise SystemExit("refusing non-frozen temporal config")
    if config.get("test_split_used") is not False:
        raise SystemExit("frozen policy provenance says test was used; refusing evaluation")

    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    if (selection.get("winner") or {}).get("benchmark") != "PANNS_CNN14_HEAD":
        raise SystemExit("unexpected selected model")
    head = resolve_head(args.selection, selection)
    if not args.panns_checkpoint.is_file():
        raise SystemExit(f"missing PANNs checkpoint: {args.panns_checkpoint}")

    rows = [row for row in load_benchmark_manifest(args.manifest) if row.split == "test"]
    media = load_media_index(args.media_index)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    scorer = EmbeddingHeadScorer(
        checkpoint=head,
        backbone="panns",
        device=args.device,
        panns_checkpoint=str(args.panns_checkpoint),
    )
    pool = AudioPool(media=media, sample_rate_hz=scorer.sample_rate_hz, max_positive_seconds=12.0)
    streams = build_streams(rows, pool, args.output_dir)

    window_seconds = float(config["window_seconds"])
    hop_seconds = float(config["hop_seconds"])
    thresholds = load_thresholds(config)

    mixed_scores = score_stream(
        path=Path(streams["mixed"]["path"]),
        scorer=scorer,
        window_seconds=window_seconds,
        hop_seconds=hop_seconds,
        output=args.output_dir / "test-mixed-scores.jsonl",
    )
    negative_scores = score_stream(
        path=Path(streams["negative"]["path"]),
        scorer=scorer,
        window_seconds=window_seconds,
        hop_seconds=hop_seconds,
        output=args.output_dir / "test-negative-scores.jsonl",
    )

    mixed_events = run_engine(
        scores=mixed_scores,
        thresholds=thresholds,
        threshold_version=config["threshold_version"],
        scenario_id="test-mixed",
        window_seconds=window_seconds,
    )
    negative_events = run_engine(
        scores=negative_scores,
        thresholds=thresholds,
        threshold_version=config["threshold_version"],
        scenario_id="test-negative",
        window_seconds=window_seconds,
    )

    labels = {}
    for label in TARGETS:
        mixed = evaluate(
            label=label,
            truth=streams["mixed"]["ground_truth"],
            predictions=mixed_events,
            duration_seconds=streams["mixed"]["duration_seconds"],
            window_seconds=window_seconds,
        )
        negative = evaluate(
            label=label,
            truth=[],
            predictions=negative_events,
            duration_seconds=streams["negative"]["duration_seconds"],
            window_seconds=window_seconds,
        )
        labels[label] = {
            "mixed_stream": mixed,
            "negative_stream": negative,
            "combined_false_alarm_events": mixed["false_alarm_events"] + negative["false_alarm_events"],
            "combined_false_alarms_per_hour": (
                (mixed["false_alarm_events"] + negative["false_alarm_events"]) /
                ((streams["mixed"]["duration_seconds"] + streams["negative"]["duration_seconds"]) / 3600.0)
            ),
        }

    macro_f1 = sum(labels[t]["mixed_stream"]["f1"] for t in TARGETS) / len(TARGETS)
    macro_recall = sum(labels[t]["mixed_stream"]["recall"] for t in TARGETS) / len(TARGETS)
    macro_precision = sum(labels[t]["mixed_stream"]["precision"] for t in TARGETS) / len(TARGETS)

    report = {
        "schema_version": "echo.mvp-final-temporal-test.v1",
        "profile_id": "ECHO-MVP-001",
        "status": "FINAL_FROZEN_TEST_COMPLETE",
        "temporal_policy": config["threshold_version"],
        "model_benchmark": "PANNS_CNN14_HEAD",
        "test_split_used_for_selection": False,
        "note_on_prior_test_exposure": (
            "Positive test clips were previously used for non-metric E2E wiring smoke. "
            "No test metric selected the model or temporal policy."
        ),
        "stream_summary": streams,
        "macro": {
            "precision": macro_precision,
            "recall": macro_recall,
            "f1": macro_f1,
        },
        "labels": labels,
        "boundary": (
            "Frozen benchmark test evaluation on deterministic synthetic long streams. "
            "This is not field validation and must not be generalized to deployment conditions."
        ),
    }
    report_path = args.output_dir / "final-test-report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "report": str(report_path),
        "macro": report["macro"],
        "labels": {
            t: {
                "precision": labels[t]["mixed_stream"]["precision"],
                "recall": labels[t]["mixed_stream"]["recall"],
                "f1": labels[t]["mixed_stream"]["f1"],
                "false_alarms_per_hour": labels[t]["combined_false_alarms_per_hour"],
                "missed_events": labels[t]["mixed_stream"]["missed_events"],
            } for t in TARGETS
        },
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
