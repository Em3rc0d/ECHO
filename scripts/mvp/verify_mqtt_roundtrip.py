#!/usr/bin/env python3
"""Verify ECHO MQTT QoS1 roundtrip by event_id and payload equality."""

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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sent", type=Path, required=True)
    parser.add_argument("--received", type=Path, required=True)
    parser.add_argument("--wait-seconds", type=float, default=10.0)
    args = parser.parse_args()

    sent = load_jsonl(args.sent)
    sent_ids = {str(row["event_id"]) for row in sent}

    deadline = time.monotonic() + max(0.0, args.wait_seconds)
    received: list[dict] = []
    while True:
        if args.received.is_file():
            received = load_jsonl(args.received)
        received_ids = {str(row["event_id"]) for row in received}
        if sent_ids and sent_ids.issubset(received_ids):
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(0.25)

    sent_by_id = {str(row["event_id"]): row for row in sent}
    received_by_id: dict[str, list[dict]] = {}
    for row in received:
        received_by_id.setdefault(str(row["event_id"]), []).append(row)

    missing = sorted(set(sent_by_id) - set(received_by_id))
    mismatched = sorted(
        event_id
        for event_id, expected in sent_by_id.items()
        if event_id in received_by_id
        and any(actual != expected for actual in received_by_id[event_id])
    )
    delivery_counts = Counter(str(row["event_id"]) for row in received)
    duplicates = {
        event_id: count
        for event_id, count in sorted(delivery_counts.items())
        if event_id in sent_by_id and count > 1
    }

    status = "PASS" if sent_by_id and not missing and not mismatched else "FAIL"
    report = {
        "schema_version": "echo.mvp-mqtt-roundtrip.v1",
        "status": status,
        "sent_messages": len(sent),
        "sent_unique_event_ids": len(sent_by_id),
        "received_messages": len(received),
        "received_unique_event_ids": len(received_by_id),
        "missing_event_ids": missing,
        "payload_mismatch_event_ids": mismatched,
        "duplicate_delivery_counts": duplicates,
        "qos_semantics": "AT_LEAST_ONCE_EVENT_ID_IS_IDEMPOTENCY_KEY",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
