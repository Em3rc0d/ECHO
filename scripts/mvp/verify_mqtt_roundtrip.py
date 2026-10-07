#!/usr/bin/env python3
"""Verify ECHO MQTT QoS1 roundtrip by canonical event-message payload.

event_id identifies one logical acoustic event across lifecycle transitions.
Therefore CONFIRMED and CLOSED intentionally share event_id and must not be
treated as duplicate MQTT deliveries. QoS 1 duplicates are exact repetitions
of the same canonical payload and are allowed.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import time


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            payload = json.loads(raw)
            if not isinstance(payload, dict) or not payload.get("event_id"):
                raise ValueError(f"{path}:{line_no}: invalid ECHO event")
            rows.append(payload)
    return rows


def canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def transition_key(payload: dict) -> str:
    lifecycle = str((payload.get("provenance") or {}).get("lifecycle") or "UNKNOWN")
    return f"{payload['event_id']}:{lifecycle}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sent", type=Path, required=True)
    parser.add_argument("--received", type=Path, required=True)
    parser.add_argument("--wait-seconds", type=float, default=10.0)
    args = parser.parse_args()

    sent = load_jsonl(args.sent)
    sent_counts = Counter(canonical(row) for row in sent)

    deadline = time.monotonic() + max(0.0, args.wait_seconds)
    received: list[dict] = []
    while True:
        if args.received.is_file():
            received = load_jsonl(args.received)
        received_counts = Counter(canonical(row) for row in received)
        if sent_counts and all(
            received_counts[payload] >= count
            for payload, count in sent_counts.items()
        ):
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(0.25)

    received_counts = Counter(canonical(row) for row in received)
    sent_ids = {str(row["event_id"]) for row in sent}
    received_ids = {str(row["event_id"]) for row in received}

    missing_event_ids = sorted(sent_ids - received_ids)

    missing_messages = []
    for payload, expected_count in sent_counts.items():
        actual_count = received_counts[payload]
        if actual_count < expected_count:
            decoded = json.loads(payload)
            missing_messages.append(
                {
                    "event_id": str(decoded["event_id"]),
                    "lifecycle": str(
                        (decoded.get("provenance") or {}).get("lifecycle") or "UNKNOWN"
                    ),
                    "expected_count": expected_count,
                    "received_count": actual_count,
                }
            )

    unexpected_messages = []
    for payload, actual_count in received_counts.items():
        if payload not in sent_counts:
            decoded = json.loads(payload)
            unexpected_messages.append(
                {
                    "event_id": str(decoded["event_id"]),
                    "lifecycle": str(
                        (decoded.get("provenance") or {}).get("lifecycle") or "UNKNOWN"
                    ),
                    "received_count": actual_count,
                }
            )

    exact_qos_duplicates = []
    for payload, expected_count in sent_counts.items():
        actual_count = received_counts[payload]
        if actual_count > expected_count:
            decoded = json.loads(payload)
            exact_qos_duplicates.append(
                {
                    "event_id": str(decoded["event_id"]),
                    "lifecycle": str(
                        (decoded.get("provenance") or {}).get("lifecycle") or "UNKNOWN"
                    ),
                    "extra_delivery_count": actual_count - expected_count,
                }
            )

    sent_transition_counts = Counter(transition_key(row) for row in sent)
    received_transition_counts = Counter(transition_key(row) for row in received)

    status = (
        "PASS"
        if sent_counts and not missing_messages and not unexpected_messages
        else "FAIL"
    )
    report = {
        "schema_version": "echo.mvp-mqtt-roundtrip.v2",
        "status": status,
        "sent_messages": len(sent),
        "sent_unique_event_ids": len(sent_ids),
        "received_messages": len(received),
        "received_unique_event_ids": len(received_ids),
        "missing_event_ids": missing_event_ids,
        "missing_messages": missing_messages,
        "unexpected_messages": unexpected_messages,
        "exact_qos_duplicate_deliveries": exact_qos_duplicates,
        "sent_transition_counts": dict(sorted(sent_transition_counts.items())),
        "received_transition_counts": dict(sorted(received_transition_counts.items())),
        "qos_semantics": (
            "AT_LEAST_ONCE; event_id identifies the logical event; lifecycle "
            "transitions sharing event_id are distinct messages"
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
