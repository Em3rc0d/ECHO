#!/usr/bin/env python3
"""Fail-fast preflight for the Docker professor demo.

This script validates only the runtime artifacts needed by demo/server.py.
It does not download models, mutate datasets, or claim scientific validity.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_JSON = {
    "selection": ROOT / "artifacts/mvp-benchmark/selection.json",
    "temporal_config": ROOT / "artifacts/mvp-temporal/temporal-event-config.json",
    "fixtures": ROOT / "artifacts/mvp-temporal/fixtures.json",
}
PANNS_CHECKPOINT = ROOT / "artifacts/models/panns/Cnn14_mAP=0.431.pth"

REQUIRED_SCENARIO_SUFFIXES = (
    "burst-glass_shatter",
    "burst-siren",
    "burst-vehicle_horn",
    "negative",
)


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def load_json(name: str, path: Path) -> dict:
    if not path.is_file():
        fail(f"missing {name}: {path.relative_to(ROOT)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    print(f"[PASS] {name}: {path.relative_to(ROOT)}")
    return payload


def resolve_selected_checkpoint(selection: dict, selection_path: Path) -> Path:
    winner = selection.get("winner") or {}
    benchmark = str(winner.get("benchmark") or "")
    raw = str(winner.get("checkpoint") or "")
    if not raw:
        fail("selection winner is missing checkpoint")
    if benchmark != "PANNS_CNN14_HEAD":
        fail(
            "demo runbook currently expects PANNS_CNN14_HEAD; "
            f"selection reports {benchmark!r}"
        )

    stored = Path(raw)
    filename = Path(raw.replace("\\", "/")).name
    candidates = [
        stored,
        (ROOT / stored).resolve() if not stored.is_absolute() else stored,
        selection_path.resolve().parent / "panns" / filename,
    ]
    for candidate in candidates:
        if candidate.is_file():
            print(
                "[PASS] selected ECHO head: "
                + str(candidate.resolve().relative_to(ROOT))
            )
            return candidate.resolve()
    fail(
        "selected ECHO head checkpoint missing; checked: "
        + ", ".join(str(path) for path in candidates)
    )
    raise AssertionError("unreachable")


def resolve_fixture_wav(fixtures_path: Path, scenario: dict) -> Path | None:
    raw = str(scenario.get("wav") or "")
    if not raw:
        return None
    stored = Path(raw)
    candidates = [
        stored,
        (ROOT / stored).resolve() if not stored.is_absolute() else stored,
        fixtures_path.resolve().parent / "streams" / stored.name,
    ]
    return next((path.resolve() for path in candidates if path.is_file()), None)


def main() -> int:
    print("ECHO professor-demo artifact preflight")
    print(f"root: {ROOT}")

    selection_path = REQUIRED_JSON["selection"]
    selection = load_json("selection", selection_path)
    temporal = load_json("temporal config", REQUIRED_JSON["temporal_config"])
    fixtures = load_json("fixtures", REQUIRED_JSON["fixtures"])

    resolve_selected_checkpoint(selection, selection_path)

    if not PANNS_CHECKPOINT.is_file():
        fail(
            "missing pinned PANNs Cnn14 checkpoint: "
            + str(PANNS_CHECKPOINT.relative_to(ROOT))
        )
    print(
        "[PASS] PANNs checkpoint: "
        + str(PANNS_CHECKPOINT.relative_to(ROOT))
    )

    status = str(temporal.get("status") or "")
    if status != "CONTROLLED_VALIDATION_CALIBRATED_NOT_FIELD_CALIBRATED":
        fail(
            "unexpected temporal config status: "
            f"{status!r}; expected controlled-validation v1 boundary"
        )
    labels = temporal.get("labels") or {}
    expected_labels = {"GLASS_SHATTER", "SIREN", "VEHICLE_HORN"}
    if set(labels) != expected_labels:
        fail(
            "temporal config labels mismatch: "
            f"{sorted(labels)} != {sorted(expected_labels)}"
        )
    print("[PASS] temporal config target set and field-calibration boundary")

    scenarios = fixtures.get("scenarios") or []
    preferred = [
        row for row in scenarios if row.get("partition") == "temporal_holdout"
    ]
    if not preferred:
        preferred = [
            row for row in scenarios if row.get("partition") == "temporal_tune"
        ]

    found = {}
    for suffix in REQUIRED_SCENARIO_SUFFIXES:
        row = next(
            (
                item
                for item in preferred
                if str(item.get("scenario_id") or "").endswith(suffix)
            ),
            None,
        )
        if row is None:
            fail(f"missing demo scenario ending in {suffix!r}")
        wav = resolve_fixture_wav(REQUIRED_JSON["fixtures"], row)
        if wav is None:
            fail(
                f"scenario {row.get('scenario_id')} exists but its WAV is missing"
            )
        found[suffix] = wav
        print(
            f"[PASS] scenario {suffix}: "
            + str(wav.relative_to(ROOT))
        )

    print()
    print("[READY] Runtime artifact set is sufficient to start the Docker demo.")
    print(
        "[BOUNDARY] This preflight checks presence/shape only. "
        "It does not certify field performance or production readiness."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
