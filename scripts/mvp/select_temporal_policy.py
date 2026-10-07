#!/usr/bin/env python3
"""Select ECHO temporal Event Engine policy on controlled validation streams.

Parameter selection uses temporal_tune only. temporal_holdout is evaluated once
after selection and never participates in the choice. The benchmark test split
is not consulted.

This produces controlled-validation temporal calibration evidence, not a field
or production calibration claim.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
from statistics import median
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echo.modeling.manifest import MVP_TARGETS
from echo.runtime.event_engine import RawInference, TemporalEventEngine, ThresholdConfig

TARGETS = tuple(MVP_TARGETS)
EPOCH = datetime(2000, 1, 1, tzinfo=timezone.utc)


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError(f"{path}:{line_no}: expected object")
            rows.append(payload)
    return rows


def resolve_score_file(summary_path: Path, raw: str, scenario_id: str) -> Path:
    stored = Path(raw)
    candidates = [
        stored,
        summary_path.resolve().parent / "scores" / f"{scenario_id}.jsonl",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        f"{scenario_id}: score file not found in "
        + ", ".join(str(candidate) for candidate in candidates)
    )


def config_dict(cfg: ThresholdConfig) -> dict:
    return {
        "on_threshold": cfg.on_threshold,
        "off_threshold": cfg.off_threshold,
        "confirm_windows": cfg.confirm_windows,
        "release_windows": cfg.release_windows,
        "cooldown_seconds": cfg.cooldown_seconds,
    }


def simulate(
    *,
    label: str,
    cfg: ThresholdConfig,
    scenario: dict,
    score_rows: list[dict],
) -> list[dict]:
    engine = TemporalEventEngine(
        thresholds={label: cfg},
        threshold_version="ECHO-MVP-001-TEMPORAL-CANDIDATE",
    )
    events: dict[str, dict] = {}
    last_end = 0.0

    for row in score_rows:
        start_seconds = float(row["start_seconds"])
        end_seconds = float(row["end_seconds"])
        last_end = max(last_end, end_seconds)
        inference = RawInference(
            source_id=str(scenario["scenario_id"]),
            site_id="ECHO-MVP-TEMPORAL-CALIBRATION",
            stream_session_id=str(scenario["scenario_id"]),
            window_start_utc=EPOCH + timedelta(seconds=start_seconds),
            window_end_utc=EPOCH + timedelta(seconds=end_seconds),
            scores={label: float((row.get("scores") or {}).get(label, 0.0))},
            model_version="ECHO-MVP-001-CACHED-WINDOW-SCORES",
        )
        for event in engine.ingest(inference):
            record = events.setdefault(
                event.event_id,
                {
                    "event_id": event.event_id,
                    "label": label,
                    "onset_seconds": (
                        event.onset_utc.astimezone(timezone.utc) - EPOCH
                    ).total_seconds(),
                    "confirmed_at_seconds": None,
                    "end_seconds": None,
                },
            )
            if event.lifecycle == "CONFIRMED":
                record["confirmed_at_seconds"] = end_seconds
            if event.lifecycle == "CLOSED" and event.end_utc is not None:
                record["end_seconds"] = (
                    event.end_utc.astimezone(timezone.utc) - EPOCH
                ).total_seconds()

    for event in engine.close_session(
        source_id=str(scenario["scenario_id"]),
        site_id="ECHO-MVP-TEMPORAL-CALIBRATION",
        stream_session_id=str(scenario["scenario_id"]),
        end_utc=EPOCH + timedelta(seconds=last_end),
        model_version="ECHO-MVP-001-CACHED-WINDOW-SCORES",
    ):
        record = events.setdefault(
            event.event_id,
            {
                "event_id": event.event_id,
                "label": label,
                "onset_seconds": (
                    event.onset_utc.astimezone(timezone.utc) - EPOCH
                ).total_seconds(),
                "confirmed_at_seconds": None,
                "end_seconds": None,
            },
        )
        if event.end_utc is not None:
            record["end_seconds"] = (
                event.end_utc.astimezone(timezone.utc) - EPOCH
            ).total_seconds()

    return sorted(
        events.values(),
        key=lambda row: (
            math.inf
            if row["confirmed_at_seconds"] is None
            else row["confirmed_at_seconds"]
        ),
    )


def evaluate_partition(
    *,
    label: str,
    cfg: ThresholdConfig,
    partition: str,
    scenarios: list[dict],
    scores_by_scenario: dict[str, list[dict]],
    window_seconds: float,
) -> dict:
    truth_count = 0
    prediction_count = 0
    matched_count = 0
    false_alarm_count = 0
    detection_latencies = []
    closure_latencies = []
    total_duration_seconds = 0.0
    scenario_reports = []

    for scenario in scenarios:
        if scenario["partition"] != partition:
            continue
        scenario_id = str(scenario["scenario_id"])
        truths = [
            row
            for row in (scenario.get("ground_truth") or [])
            if label in (row.get("labels") or [])
        ]
        predictions = simulate(
            label=label,
            cfg=cfg,
            scenario=scenario,
            score_rows=scores_by_scenario[scenario_id],
        )
        total_duration_seconds += float(scenario["duration_seconds"])
        truth_count += len(truths)
        prediction_count += len(predictions)

        unmatched_truth = set(range(len(truths)))
        scenario_matches = []
        scenario_false = 0

        for prediction in predictions:
            confirmed_at = prediction.get("confirmed_at_seconds")
            if confirmed_at is None:
                scenario_false += 1
                continue
            candidates = [
                index
                for index in unmatched_truth
                if float(truths[index]["start_seconds"]) <= confirmed_at
                <= float(truths[index]["end_seconds"]) + window_seconds
            ]
            if not candidates:
                scenario_false += 1
                continue
            matched_index = min(
                candidates,
                key=lambda index: abs(
                    confirmed_at - float(truths[index]["start_seconds"])
                ),
            )
            unmatched_truth.remove(matched_index)
            truth = truths[matched_index]
            matched_count += 1
            latency = confirmed_at - float(truth["start_seconds"])
            detection_latencies.append(latency)
            if prediction.get("end_seconds") is not None:
                closure_latencies.append(
                    float(prediction["end_seconds"])
                    - float(truth["end_seconds"])
                )
            scenario_matches.append(
                {
                    "event_id": prediction["event_id"],
                    "asset_id": truth["asset_id"],
                    "detection_latency_seconds": latency,
                }
            )

        false_alarm_count += scenario_false
        scenario_reports.append(
            {
                "scenario_id": scenario_id,
                "truth_events": len(truths),
                "predicted_events": len(predictions),
                "matched_events": len(scenario_matches),
                "missed_events": len(unmatched_truth),
                "false_alarm_events": scenario_false,
                "matches": scenario_matches,
            }
        )

    precision = (
        matched_count / prediction_count if prediction_count else (1.0 if truth_count == 0 else 0.0)
    )
    recall = matched_count / truth_count if truth_count else 1.0
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall > 0
        else 0.0
    )
    hours = total_duration_seconds / 3600.0
    false_alarms_per_hour = false_alarm_count / hours if hours > 0 else 0.0

    return {
        "label": label,
        "partition": partition,
        "truth_events": truth_count,
        "predicted_events": prediction_count,
        "matched_events": matched_count,
        "missed_events": truth_count - matched_count,
        "false_alarm_events": false_alarm_count,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_alarms_per_hour": false_alarms_per_hour,
        "median_detection_latency_seconds": (
            median(detection_latencies) if detection_latencies else None
        ),
        "median_closure_latency_seconds": (
            median(closure_latencies) if closure_latencies else None
        ),
        "stream_hours": hours,
        "scenarios": scenario_reports,
    }


def candidate_grid(base_threshold: float):
    on_values = sorted(
        {
            round(min(0.95, max(0.05, base_threshold + delta)), 4)
            for delta in (-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15)
        }
    )
    for on_threshold in on_values:
        off_values = sorted(
            {
                round(min(on_threshold, max(0.05, on_threshold - delta)), 4)
                for delta in (0.0, 0.05, 0.10, 0.20)
            }
        )
        for off_threshold in off_values:
            for confirm_windows in (1, 2, 3):
                for release_windows in (1, 2, 3):
                    for cooldown_seconds in (0.0, 2.0, 5.0, 10.0):
                        yield ThresholdConfig(
                            on_threshold=on_threshold,
                            off_threshold=off_threshold,
                            confirm_windows=confirm_windows,
                            release_windows=release_windows,
                            cooldown_seconds=cooldown_seconds,
                        )


def selection_key(report: dict, cfg: ThresholdConfig, base_threshold: float):
    latency = report["median_detection_latency_seconds"]
    if latency is None:
        latency = math.inf
    return (
        float(report["f1"]),
        float(report["recall"]),
        -float(report["false_alarms_per_hour"]),
        -float(latency),
        -abs(cfg.on_threshold - base_threshold),
        -cfg.confirm_windows,
        -cfg.release_windows,
        -cfg.cooldown_seconds,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--score-summary", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "artifacts/mvp-temporal",
    )
    parser.add_argument("--top-candidates", type=int, default=10)
    args = parser.parse_args()

    fixtures = json.loads(args.fixtures.read_text(encoding="utf-8"))
    score_summary = json.loads(args.score_summary.read_text(encoding="utf-8"))
    selection = json.loads(args.selection.read_text(encoding="utf-8"))

    if fixtures.get("source_split") != "validation" or fixtures.get("test_split_used") is not False:
        raise SystemExit("temporal calibration must use validation only")
    if score_summary.get("status") != "COMPLETE":
        raise SystemExit("temporal score cache is incomplete")

    winner = selection.get("winner") or {}
    if winner.get("benchmark") != "PANNS_CNN14_HEAD":
        raise SystemExit("temporal calibration benchmark winner mismatch")
    base_thresholds = winner.get("validation_thresholds") or {}
    missing = [target for target in TARGETS if target not in base_thresholds]
    if missing:
        raise SystemExit(f"winner missing validation thresholds: {missing}")

    scenarios = fixtures.get("scenarios") or []
    score_meta = {
        str(row["scenario_id"]): row
        for row in (score_summary.get("scenarios") or [])
    }
    scores_by_scenario = {}
    for scenario in scenarios:
        scenario_id = str(scenario["scenario_id"])
        meta = score_meta.get(scenario_id)
        if not meta:
            raise SystemExit(f"score summary missing scenario {scenario_id}")
        path = resolve_score_file(
            args.score_summary,
            str(meta.get("score_file") or ""),
            scenario_id,
        )
        scores_by_scenario[scenario_id] = load_jsonl(path)

    window_seconds = float(score_summary["window_seconds"])
    selected = {}
    detail = {}
    warnings = []

    for label in TARGETS:
        base_threshold = float(base_thresholds[label])
        ranked = []
        for cfg in candidate_grid(base_threshold):
            tune_report = evaluate_partition(
                label=label,
                cfg=cfg,
                partition="temporal_tune",
                scenarios=scenarios,
                scores_by_scenario=scores_by_scenario,
                window_seconds=window_seconds,
            )
            ranked.append(
                (
                    selection_key(tune_report, cfg, base_threshold),
                    cfg,
                    tune_report,
                )
            )
        ranked.sort(key=lambda item: item[0], reverse=True)
        _key, best_cfg, best_tune = ranked[0]
        holdout_report = evaluate_partition(
            label=label,
            cfg=best_cfg,
            partition="temporal_holdout",
            scenarios=scenarios,
            scores_by_scenario=scores_by_scenario,
            window_seconds=window_seconds,
        )

        selected[label] = config_dict(best_cfg)
        detail[label] = {
            "base_validation_threshold": base_threshold,
            "selected_config": config_dict(best_cfg),
            "selection_rule": (
                "temporal_tune event F1; ties prefer recall, lower false alarms/hour, "
                "lower median detection latency, then parameters nearest the base "
                "validation threshold and lower temporal complexity"
            ),
            "tune": best_tune,
            "holdout": holdout_report,
            "top_tune_candidates": [
                {
                    "config": config_dict(cfg),
                    "f1": report["f1"],
                    "precision": report["precision"],
                    "recall": report["recall"],
                    "false_alarms_per_hour": report["false_alarms_per_hour"],
                    "median_detection_latency_seconds": report[
                        "median_detection_latency_seconds"
                    ],
                }
                for _rank_key, cfg, report in ranked[: args.top_candidates]
            ],
        }
        if holdout_report["recall"] == 0.0:
            warnings.append(f"ZERO_HOLDOUT_RECALL:{label}")
        if holdout_report["false_alarm_events"] > 0:
            warnings.append(
                f"HOLDOUT_FALSE_ALARMS:{label}:{holdout_report['false_alarm_events']}"
            )

    def macro(metric: str, partition_key: str) -> float:
        return sum(
            float(detail[label][partition_key][metric])
            for label in TARGETS
        ) / len(TARGETS)

    report = {
        "schema_version": "echo.mvp-temporal-calibration-report.v1",
        "profile_id": "ECHO-MVP-001",
        "status": "CONTROLLED_VALIDATION_CALIBRATION_COMPLETE",
        "model_benchmark": winner["benchmark"],
        "selection_partition": "temporal_tune",
        "evaluation_partition": "temporal_holdout",
        "test_split_used": False,
        "window_seconds": window_seconds,
        "hop_seconds": float(score_summary["hop_seconds"]),
        "macro": {
            "tune_f1": macro("f1", "tune"),
            "tune_recall": macro("recall", "tune"),
            "holdout_f1": macro("f1", "holdout"),
            "holdout_recall": macro("recall", "holdout"),
            "holdout_false_alarms_per_hour": macro(
                "false_alarms_per_hour",
                "holdout",
            ),
        },
        "labels": detail,
        "warnings": warnings,
        "boundary": (
            "Parameters selected on deterministic synthetic long streams composed "
            "from governed validation audio and evaluated on recording-group-disjoint "
            "temporal holdout. This is not field calibration and must not be described "
            "as production-ready temporal behavior."
        ),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.output_dir / "calibration-report.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    config = {
        "schema_version": "echo.event-threshold-config.v1",
        "threshold_version": "ECHO-MVP-001-TEMPORAL-CONTROLLED-v1",
        "status": "CONTROLLED_VALIDATION_CALIBRATED_NOT_FIELD_CALIBRATED",
        "profile_id": "ECHO-MVP-001",
        "model_benchmark": winner["benchmark"],
        "window_seconds": window_seconds,
        "hop_seconds": float(score_summary["hop_seconds"]),
        "selection_partition": "temporal_tune",
        "holdout_evaluated": True,
        "test_split_used": False,
        "labels": selected,
        "calibration_report": str(report_path),
        "warnings": warnings,
        "boundary": report["boundary"],
    }
    config_path = args.output_dir / "temporal-event-config.json"
    config_path.write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": report["status"],
                "config": str(config_path),
                "report": str(report_path),
                "macro": report["macro"],
                "warnings": warnings,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
