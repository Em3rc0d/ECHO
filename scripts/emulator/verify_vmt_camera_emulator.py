#!/usr/bin/env python3
"""Verify the local VMT camera emulator over both RTSP and MQTT."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[2]


def load_sources(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("cameras") or []
    if not rows:
        raise ValueError("no cameras in emulator config")
    return rows


def wait_mqtt_statuses(
    host: str,
    port: int,
    expected: set[str],
    timeout: float,
) -> dict[str, dict]:
    try:
        import paho.mqtt.client as mqtt
    except ImportError as exc:
        raise RuntimeError("verification requires paho-mqtt") from exc

    found: dict[str, dict] = {}
    event = threading.Event()
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="echo-vmt-emulator-verify",
    )

    def on_connect(client, userdata, flags, reason_code, properties):
        del userdata, flags, properties
        if reason_code == 0:
            client.subscribe("vmt/cameras/+/status", qos=1)

    def on_message(client, userdata, message):
        del client, userdata
        try:
            payload = json.loads(message.payload.decode("utf-8"))
        except Exception:
            return
        source_id = str(payload.get("source_id") or "")
        if source_id in expected:
            found[source_id] = payload
            if expected.issubset(found) and all(
                found[item].get("state") == "ONLINE" for item in expected
            ):
                event.set()

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, port, 60)
    client.loop_start()
    try:
        event.wait(timeout)
    finally:
        client.loop_stop()
        client.disconnect()
    return found


def ffprobe_stream(url: str, ffprobe_bin: str, timeout: float) -> dict:
    deadline = time.monotonic() + timeout
    last_error = ""
    while time.monotonic() < deadline:
        try:
            proc = subprocess.run(
                [
                    ffprobe_bin,
                    "-v",
                    "error",
                    "-rtsp_transport",
                    "tcp",
                    "-show_streams",
                    "-of",
                    "json",
                    url,
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=max(2.0, min(8.0, timeout)),
            )
            if proc.returncode == 0:
                return json.loads(proc.stdout)
            last_error = proc.stderr.strip()
        except subprocess.TimeoutExpired:
            last_error = "ffprobe timeout"
        time.sleep(1.0)
    raise RuntimeError(f"ffprobe failed for {url}: {last_error}")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "config/emulator/vmt-cameras.json",
    )
    parser.add_argument("--rtsp-base", default="rtsp://rtsp-server:8554")
    parser.add_argument("--mqtt-host", default="broker")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--ffprobe-bin", default="ffprobe")
    args = parser.parse_args()

    rows = load_sources(args.config)
    expected = {str(row["source_id"]) for row in rows}
    statuses = wait_mqtt_statuses(
        args.mqtt_host,
        args.mqtt_port,
        expected,
        args.timeout,
    )

    results = []
    ok = True
    for row in rows:
        source_id = str(row["source_id"])
        path = str(row.get("rtsp_path") or source_id.lower())
        url = f"{args.rtsp_base.rstrip('/')}/{path.lstrip('/')}"
        probe = ffprobe_stream(url, args.ffprobe_bin, args.timeout)
        streams = probe.get("streams") or []
        videos = [stream for stream in streams if stream.get("codec_type") == "video"]
        audios = [stream for stream in streams if stream.get("codec_type") == "audio"]
        status = statuses.get(source_id)
        row_ok = bool(
            videos
            and audios
            and status
            and status.get("state") == "ONLINE"
        )
        ok = ok and row_ok
        results.append(
            {
                "source_id": source_id,
                "rtsp_uri": url,
                "mqtt_state": None if status is None else status.get("state"),
                "video_codec": None if not videos else videos[0].get("codec_name"),
                "audio_codec": None if not audios else audios[0].get("codec_name"),
                "audio_sample_rate": (
                    None if not audios else audios[0].get("sample_rate")
                ),
                "pass": row_ok,
            }
        )

    print(
        json.dumps(
            {"status": "PASS" if ok else "FAIL", "cameras": results},
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
