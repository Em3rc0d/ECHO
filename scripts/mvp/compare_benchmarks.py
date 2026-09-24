#!/usr/bin/env python3
"""Select the provisional ECHO MVP model using validation evidence only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED = {
    "YAMNET_EMBEDDINGS_HEAD",
    "PANNS_CNN14_HEAD",
    "COMPACT_LOGMEL_CNN",
}


def load(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("profile_id") != "ECHO-MVP-001":
        raise ValueError(f"{path}: not an ECHO-MVP-001 result")
    if payload.get("benchmark") not in EXPECTED:
        raise ValueError(f"{path}: unexpected benchmark {payload.get('benchmark')!r}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path, nargs=3)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/mvp-benchmark/selection.json"),
    )
    args = parser.parse_args()

    rows = [load(path) for path in args.results]
    names = {str(row["benchmark"]) for row in rows}
    if names != EXPECTED:
        raise SystemExit(
            f"expected exactly {sorted(EXPECTED)}, got {sorted(names)}"
        )

    def selection_key(row):
        validation = row.get("validation") or {}
        return (
            float(validation.get("macro_f1", 0.0)),
            float(validation.get("macro_recall", 0.0)),
            -float(validation.get("macro_false_positive_rate", 1.0)),
        )

    winner = max(rows, key=selection_key)
    payload = {
        "schema_version": "echo.mvp-model-selection.v1",
        "profile_id": "ECHO-MVP-001",
        "status": "PROVISIONAL_MVP_WINNER",
        "selection_rule": (
            "Select by validation macro F1; ties prefer validation macro recall "
            "then lower validation false-positive rate. Test metrics are reported "
            "but never used to select the winner."
        ),
        "winner": {
            "benchmark": winner["benchmark"],
            "checkpoint": winner.get("checkpoint"),
            "validation": winner.get("validation"),
            "test": winner.get("test"),
            "validation_thresholds": winner.get("validation_thresholds"),
        },
        "candidates": [
            {
                "benchmark": row["benchmark"],
                "checkpoint": row.get("checkpoint"),
                "validation": row.get("validation"),
                "test": row.get("test"),
            }
            for row in sorted(rows, key=lambda row: str(row["benchmark"]))
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "winner": payload["winner"]["benchmark"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
