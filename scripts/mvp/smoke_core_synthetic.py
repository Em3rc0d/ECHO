#!/usr/bin/env python3
"""Offline synthetic smoke for the ECHO MVP execution core.

This is an implementation regression only. It proves that the partial-label
training stack, compact CNN frontend, replay windows and Temporal Event Engine
execute coherently without requiring any acoustic corpus bytes.

It MUST NOT be reported as ECHO acoustic-model accuracy.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    import numpy as np
    import torch
except ImportError as exc:
    raise SystemExit("install ECHO with the 'mvp' extra") from exc

from echo.modeling.compact_cnn import build_compact_cnn
from echo.modeling.embedding_head import (
    HeadTrainingConfig,
    supervision_arrays,
    train_embedding_head,
)
from echo.modeling.manifest import BenchmarkRow, MVP_TARGETS
from echo.modeling.metrics import evaluate_binary, tune_threshold
from echo.runtime.event_engine import RawInference, TemporalEventEngine, ThresholdConfig
from echo.runtime.replay import iter_replay_windows


BASE = datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc)


def synthetic_rows(seed: int = 1337):
    rng = np.random.default_rng(seed)
    rows: list[BenchmarkRow] = []
    features: list[np.ndarray] = []
    fake_sha = "a" * 64

    for split, count in (("train", 90), ("validation", 36), ("test", 36)):
        for index in range(count):
            target_index = index % len(MVP_TARGETS)
            feature = rng.normal(0.0, 0.2, size=8).astype(np.float32)
            feature[target_index] += 2.5

            supervision = {target: None for target in MVP_TARGETS}
            positive = MVP_TARGETS[target_index]
            explicit_negative = MVP_TARGETS[(target_index + 1) % len(MVP_TARGETS)]
            supervision[positive] = 1
            supervision[explicit_negative] = 0

            rows.append(
                BenchmarkRow(
                    asset_id=f"synthetic:{split}:{index}",
                    split=split,
                    source_dataset="echo-synthetic-smoke",
                    recording_group_id=f"synthetic-group:{split}:{index}",
                    media_sha256=fake_sha,
                    duration_seconds=1.0,
                    positive_labels=(positive,),
                    explicit_negative_labels=(explicit_negative,),
                    supervision=supervision,
                )
            )
            features.append(feature)

    return rows, np.stack(features)


def inference(index: int, score: float, *, source: str = "cam-1", session: str = "s1"):
    start = BASE + timedelta(seconds=index)
    return RawInference(
        source_id=source,
        site_id="site-1",
        stream_session_id=session,
        window_start_utc=start,
        window_end_utc=start + timedelta(seconds=1),
        scores={"SIREN": score},
        model_version="synthetic-smoke",
    )


def main() -> int:
    binary = evaluate_binary([0.9, 0.8, 0.2, 0.1], [1, 0, 0, 1], threshold=0.5)
    if (binary.tp, binary.fp, binary.tn, binary.fn) != (1, 1, 1, 1):
        raise RuntimeError("binary metric regression")

    tuned = tune_threshold(
        [0.95, 0.8, 0.7, 0.2, 0.1],
        [1, 1, 0, 0, 0],
        candidates=[0.5, 0.75, 0.9],
    )
    if tuned.threshold != 0.75 or abs(tuned.f1 - 1.0) > 1e-12:
        raise RuntimeError("threshold-tuning regression")

    rows, features = synthetic_rows()
    _y, mask = supervision_arrays(rows)
    if int(mask.sum()) != len(rows) * 2:
        raise RuntimeError("partial-supervision mask regression")

    _model, report = train_embedding_head(
        features=features,
        rows=rows,
        input_dim=8,
        config=HeadTrainingConfig(
            epochs=35,
            batch_size=24,
            hidden_dim=16,
            dropout=0.0,
            patience=8,
            seed=1337,
        ),
        device="cpu",
    )
    if report["validation"]["macro_f1"] < 0.90:
        raise RuntimeError("synthetic validation regression")
    if report["test"]["macro_f1"] < 0.90:
        raise RuntimeError("synthetic test regression")

    cnn = build_compact_cnn(num_targets=len(MVP_TARGETS))
    logits = cnn(torch.randn(2, 16000))
    if tuple(logits.shape) != (2, len(MVP_TARGETS)):
        raise RuntimeError("compact CNN output-shape regression")
    if not bool(torch.isfinite(logits).all()):
        raise RuntimeError("compact CNN non-finite output")

    windows = list(
        iter_replay_windows(
            [1.0, 2.0, 3.0],
            sample_rate_hz=2,
            window_seconds=2.0,
            hop_seconds=1.0,
            pad_final=True,
        )
    )
    if len(windows) != 2 or windows[0].waveform != (1.0, 2.0, 3.0, 0.0):
        raise RuntimeError("replay final-padding regression")

    engine = TemporalEventEngine(
        thresholds={
            "SIREN": ThresholdConfig(
                on_threshold=0.8,
                off_threshold=0.4,
                confirm_windows=2,
                release_windows=2,
                cooldown_seconds=3.0,
            )
        },
        threshold_version="synthetic-smoke-v1",
    )

    if engine.ingest(inference(0, 0.9)):
        raise RuntimeError("event confirmed too early")
    opened = engine.ingest(inference(1, 0.9))
    if len(opened) != 1 or opened[0].lifecycle != "CONFIRMED":
        raise RuntimeError("event confirmation regression")

    closed = engine.close_session(
        source_id="cam-1",
        site_id="site-1",
        stream_session_id="s1",
        end_utc=BASE + timedelta(seconds=2),
        model_version="synthetic-smoke",
    )
    if (
        len(closed) != 1
        or closed[0].lifecycle != "CLOSED"
        or closed[0].event_id != opened[0].event_id
    ):
        raise RuntimeError("EOF event-close regression")

    isolation = TemporalEventEngine(
        thresholds={
            "SIREN": ThresholdConfig(
                on_threshold=0.8,
                off_threshold=0.4,
                confirm_windows=2,
                release_windows=2,
                cooldown_seconds=3.0,
            )
        },
        threshold_version="synthetic-smoke-v1",
    )
    isolation.ingest(inference(0, 0.9, source="a"))
    isolation.ingest(inference(0, 0.9, source="b"))
    event_a = isolation.ingest(inference(1, 0.9, source="a"))
    event_b = isolation.ingest(inference(1, 0.9, source="b"))
    if (
        len(event_a) != 1
        or len(event_b) != 1
        or event_a[0].event_id == event_b[0].event_id
    ):
        raise RuntimeError("source-isolation regression")

    result = {
        "schema_version": "echo.mvp-core-synthetic-smoke.v1",
        "status": "PASS",
        "scope": "IMPLEMENTATION_REGRESSION_ONLY_NOT_ACOUSTIC_PERFORMANCE",
        "torch_version": torch.__version__,
        "metrics": "PASS",
        "partial_supervision_masked_training": "PASS",
        "synthetic_validation_macro_f1": report["validation"]["macro_f1"],
        "synthetic_test_macro_f1": report["test"]["macro_f1"],
        "compact_cnn_forward": "PASS",
        "replay_final_padding": "PASS",
        "event_engine_eof_close": "PASS",
        "event_engine_source_isolation": "PASS",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
