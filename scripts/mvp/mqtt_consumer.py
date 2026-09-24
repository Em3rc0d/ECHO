#!/usr/bin/env python3
"""Minimal QoS 1 ECHO event smoke consumer with event_id dedup visibility."""

from __future__ import annotations

import argparse
import json
import os


REQUIRED = {
    "schema_version",
    "event_id",
    "source_id",
    "site_id",
    "event_type",
    "onset_utc",
    "confidence",
    "model_version",
    "threshold_version",
    "stream_session_id",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--client-id", default="echo-mvp-smoke-consumer")
    parser.add_argument("--username", default=None)
    parser.add_argument("--password-env", default=None)
    args = parser.parse_args()

    try:
        import paho.mqtt.client as mqtt
    except ImportError as exc:
        raise SystemExit("install ECHO with the 'mvp' extra") from exc

    seen: dict[str, int] = {}

    def on_connect(client, _userdata, _flags, reason_code, _properties):
        if reason_code != 0:
            raise RuntimeError(f"MQTT connect failed: {reason_code}")
        client.subscribe(args.topic, qos=1)
        print(json.dumps({"status": "subscribed", "topic": args.topic}), flush=True)

    def on_message(_client, _userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        missing = sorted(REQUIRED - set(payload))
        if missing:
            print(json.dumps({"status": "invalid", "missing": missing}), flush=True)
            return
        event_id = str(payload["event_id"])
        seen[event_id] = seen.get(event_id, 0) + 1
        print(
            json.dumps(
                {
                    "status": "event",
                    "event_id": event_id,
                    "delivery_count_seen": seen[event_id],
                    "lifecycle": (payload.get("provenance") or {}).get("lifecycle"),
                    "event_type": payload.get("event_type"),
                    "source_id": payload.get("source_id"),
                },
                sort_keys=True,
            ),
            flush=True,
        )

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=args.client_id,
    )
    if args.username is not None:
        password = os.environ.get(args.password_env) if args.password_env else None
        client.username_pw_set(args.username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.host, args.port, 60)
    client.loop_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
