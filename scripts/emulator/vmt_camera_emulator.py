#!/usr/bin/env python3
"""VMT camera-edge emulator for ECHO.

The emulator publishes synthetic camera-like H.264/AAC RTSP streams through
MediaMTX and emits camera lifecycle/telemetry over MQTT. Audio scenarios are
resolved from ECHO's governed temporal fixtures (or generated digital silence).

It is intentionally an edge emulator, not an alternate ECHO classifier.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import signal
import subprocess
import threading
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = {"negative", "glass_shatter", "siren", "vehicle_horn", "silence"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug_topic(value: str) -> str:
    return value.replace("/", "_").replace("+", "_").replace("#", "_")


def resolve_fixture(fixtures_path: Path, scenario: str) -> Path | None:
    if scenario == "silence":
        return None
    payload = json.loads(fixtures_path.read_text(encoding="utf-8"))
    rows = payload.get("scenarios") or []
    preferred = [row for row in rows if row.get("partition") == "temporal_holdout"]
    if not preferred:
        preferred = [row for row in rows if row.get("partition") == "temporal_tune"]
    suffix = "negative" if scenario == "negative" else f"burst-{scenario}"
    row = next(
        (item for item in preferred if str(item.get("scenario_id") or "").endswith(suffix)),
        None,
    )
    if row is None:
        raise RuntimeError(f"no governed fixture found for scenario={scenario}")
    stored = Path(str(row.get("wav") or ""))
    candidates = [stored, fixtures_path.resolve().parent / "streams" / stored.name]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        f"fixture WAV not found for scenario={scenario}: "
        + ", ".join(str(candidate) for candidate in candidates)
    )


@dataclass(frozen=True)
class CameraSpec:
    source_id: str
    site_id: str
    rtsp_path: str
    scenario: str
    width: int = 640
    height: int = 360
    fps: int = 10


@dataclass
class CameraRuntime:
    spec: CameraSpec
    scenario: str
    desired_online: bool = True
    process: subprocess.Popen[bytes] | None = None
    stream_generation: int = 0
    state: str = "OFFLINE"
    started_monotonic: float = 0.0
    next_retry_monotonic: float = 0.0
    restart_count: int = 0
    last_exit_code: int | None = None


class VmtCameraEmulator:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        config = json.loads(args.config.read_text(encoding="utf-8"))
        self.site_id = str(config.get("site_id") or "VMT-EMULATED")
        specs: list[CameraSpec] = []
        for row in config.get("cameras") or []:
            scenario = str(row.get("scenario") or "negative")
            if scenario not in SCENARIOS:
                raise ValueError(f"unsupported scenario in config: {scenario}")
            source_id = str(row["source_id"])
            specs.append(
                CameraSpec(
                    source_id=source_id,
                    site_id=str(row.get("site_id") or self.site_id),
                    rtsp_path=str(row.get("rtsp_path") or source_id.lower()),
                    scenario=scenario,
                    width=int(row.get("width") or 640),
                    height=int(row.get("height") or 360),
                    fps=int(row.get("fps") or 10),
                )
            )
        if not specs:
            raise ValueError("camera emulator config must define at least one camera")
        self.cameras = {
            spec.source_id: CameraRuntime(spec=spec, scenario=spec.scenario)
            for spec in specs
        }
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.mqtt_connected = threading.Event()
        self._mqtt = self._make_mqtt_client()

    def _make_mqtt_client(self):
        try:
            import paho.mqtt.client as mqtt
        except ImportError as exc:
            raise RuntimeError("camera emulator requires paho-mqtt") from exc
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.args.mqtt_client_id,
        )
        client.will_set(
            "vmt/emulator/status",
            json.dumps({"state": "OFFLINE", "at": utc_now()}, separators=(",", ":")),
            qos=1,
            retain=True,
        )
        client.on_connect = self._on_connect
        client.on_message = self._on_message
        return client

    def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        del userdata, flags, properties
        if reason_code != 0:
            print(json.dumps({"kind": "mqtt_connect_failed", "reason": str(reason_code)}), flush=True)
            return
        self.mqtt_connected.set()
        client.subscribe("vmt/cameras/+/control", qos=1)
        self._publish_json(
            "vmt/emulator/status",
            {"state": "ONLINE", "at": utc_now(), "camera_count": len(self.cameras)},
            retain=True,
        )
        self._publish_inventory()

    def _on_message(self, client, userdata, message) -> None:
        del client, userdata
        try:
            payload = json.loads(message.payload.decode("utf-8"))
        except Exception as exc:
            print(json.dumps({"kind": "invalid_control", "topic": message.topic, "error": str(exc)}), flush=True)
            return
        parts = message.topic.split("/")
        if len(parts) != 4 or parts[:2] != ["vmt", "cameras"] or parts[3] != "control":
            return
        source_id = parts[2]
        self._apply_control(source_id, payload)

    def _apply_control(self, source_id: str, payload: dict[str, Any]) -> None:
        with self.lock:
            runtime = self.cameras.get(source_id)
            if runtime is None:
                return
            command = str(payload.get("command") or "")
            if command == "restart":
                self._stop_camera(runtime, state="RECONNECTING")
                runtime.desired_online = True
                runtime.next_retry_monotonic = 0.0
            elif command == "set_online":
                online = payload.get("online")
                if not isinstance(online, bool):
                    self._publish_status(
                        runtime,
                        extra={"control_error": "online must be a JSON boolean"},
                    )
                    return
                runtime.desired_online = online
                if not online:
                    self._stop_camera(runtime, state="OFFLINE")
                else:
                    runtime.next_retry_monotonic = 0.0
            elif command == "set_scenario":
                scenario = str(payload.get("scenario") or "")
                if scenario not in SCENARIOS:
                    self._publish_status(runtime, extra={"control_error": f"unsupported scenario: {scenario}"})
                    return
                runtime.scenario = scenario
                if runtime.desired_online:
                    self._stop_camera(runtime, state="RECONNECTING")
                    runtime.next_retry_monotonic = 0.0
                self._publish_inventory()
            else:
                self._publish_status(runtime, extra={"control_error": f"unsupported command: {command}"})

    def _publish_json(
        self,
        topic: str,
        payload: dict[str, Any],
        *,
        retain: bool = False,
        qos: int = 1,
    ) -> None:
        info = self._mqtt.publish(
            topic,
            json.dumps(payload, sort_keys=True, separators=(",", ":")),
            qos=qos,
            retain=retain,
        )
        if info.rc != 0:
            print(
                json.dumps(
                    {
                        "kind": "mqtt_publish_degraded",
                        "topic": topic,
                        "rc": int(info.rc),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )

    def _publish_inventory(self) -> None:
        rows = []
        with self.lock:
            for runtime in self.cameras.values():
                rows.append(
                    {
                        "source_id": runtime.spec.source_id,
                        "site_id": runtime.spec.site_id,
                        "source_type": "rtsp",
                        "rtsp_uri": self._advertised_rtsp_uri(runtime.spec),
                        "scenario": runtime.scenario,
                        "synthetic_video": True,
                    }
                )
        self._publish_json(
            "vmt/emulator/inventory",
            {"version": "ECHO-VMT-CAMERA-EMULATOR-v1", "at": utc_now(), "cameras": rows},
            retain=True,
        )

    def _publish_status(
        self,
        runtime: CameraRuntime,
        *,
        extra: dict[str, Any] | None = None,
    ) -> None:
        payload: dict[str, Any] = {
            "version": "ECHO-VMT-CAMERA-EMULATOR-v1",
            "source_id": runtime.spec.source_id,
            "site_id": runtime.spec.site_id,
            "source_type": "rtsp",
            "state": runtime.state,
            "stream_generation": runtime.stream_generation,
            "rtsp_uri": self._advertised_rtsp_uri(runtime.spec),
            "scenario": runtime.scenario,
            "at": utc_now(),
        }
        if runtime.last_exit_code is not None:
            payload["last_exit_code"] = runtime.last_exit_code
        if extra:
            payload.update(extra)
        topic = f"vmt/cameras/{slug_topic(runtime.spec.source_id)}/status"
        self._publish_json(topic, payload, retain=True)

    def _publish_telemetry(self, runtime: CameraRuntime) -> None:
        uptime = 0.0
        if runtime.process is not None and runtime.started_monotonic:
            uptime = max(0.0, time.monotonic() - runtime.started_monotonic)
        topic = f"vmt/cameras/{slug_topic(runtime.spec.source_id)}/telemetry"
        self._publish_json(
            topic,
            {
                "version": "ECHO-VMT-CAMERA-EMULATOR-v1",
                "source_id": runtime.spec.source_id,
                "site_id": runtime.spec.site_id,
                "state": runtime.state,
                "stream_generation": runtime.stream_generation,
                "scenario": runtime.scenario,
                "uptime_seconds": round(uptime, 3),
                "restart_count": runtime.restart_count,
                "media": {
                    "video_codec": "H264",
                    "width": runtime.spec.width,
                    "height": runtime.spec.height,
                    "fps": runtime.spec.fps,
                    "audio_codec": "AAC-LC",
                    "audio_sample_rate_hz": 44100,
                    "audio_channels": 1,
                },
                "at": utc_now(),
            },
            retain=False,
            qos=1,
        )

    def _advertised_rtsp_uri(self, spec: CameraSpec) -> str:
        return f"{self.args.advertised_rtsp_base.rstrip('/')}/{spec.rtsp_path.lstrip('/')}"

    def _publish_rtsp_uri(self, spec: CameraSpec) -> str:
        return f"{self.args.publish_rtsp_base.rstrip('/')}/{spec.rtsp_path.lstrip('/')}"

    def _ffmpeg_command(self, runtime: CameraRuntime) -> list[str]:
        spec = runtime.spec
        command = [
            self.args.ffmpeg_bin,
            "-hide_banner",
            "-loglevel",
            self.args.ffmpeg_loglevel,
            "-re",
            "-f",
            "lavfi",
            "-i",
            f"color=c=black:s={spec.width}x{spec.height}:r={spec.fps}",
        ]
        fixture = resolve_fixture(self.args.fixtures, runtime.scenario)
        if fixture is None:
            command.extend(["-re", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono"])
        else:
            command.extend(["-re", "-stream_loop", "-1", "-i", str(fixture)])
        command.extend(
            [
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-tune",
                "zerolatency",
                "-pix_fmt",
                "yuv420p",
                "-g",
                str(max(1, spec.fps * 2)),
                "-b:v",
                "350k",
                "-c:a",
                "aac",
                "-profile:a",
                "aac_low",
                "-ar",
                "44100",
                "-ac",
                "1",
                "-b:a",
                "96k",
                "-f",
                "rtsp",
                "-rtsp_transport",
                "tcp",
                self._publish_rtsp_uri(spec),
            ]
        )
        return command

    def _start_camera(self, runtime: CameraRuntime) -> None:
        runtime.stream_generation += 1
        runtime.state = "CONNECTING"
        runtime.last_exit_code = None
        self._publish_status(runtime)
        runtime.process = subprocess.Popen(self._ffmpeg_command(runtime))
        runtime.started_monotonic = time.monotonic()
        print(
            json.dumps(
                {
                    "kind": "camera_start",
                    "source_id": runtime.spec.source_id,
                    "generation": runtime.stream_generation,
                    "scenario": runtime.scenario,
                    "rtsp_uri": self._advertised_rtsp_uri(runtime.spec),
                },
                sort_keys=True,
            ),
            flush=True,
        )

    def _stop_camera(self, runtime: CameraRuntime, *, state: str) -> None:
        proc = runtime.process
        runtime.process = None
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        if proc is not None:
            runtime.last_exit_code = proc.returncode
        runtime.state = state
        self._publish_status(runtime)

    def _tick_camera(self, runtime: CameraRuntime, now: float) -> None:
        if not runtime.desired_online:
            if runtime.process is not None:
                self._stop_camera(runtime, state="OFFLINE")
            return
        if runtime.process is None:
            if now >= runtime.next_retry_monotonic:
                try:
                    self._start_camera(runtime)
                except Exception as exc:
                    runtime.state = "RECONNECTING"
                    runtime.restart_count += 1
                    runtime.next_retry_monotonic = now + self.args.reconnect_seconds
                    self._publish_status(runtime, extra={"error": str(exc)})
            return
        code = runtime.process.poll()
        if code is not None:
            runtime.last_exit_code = code
            runtime.process = None
            runtime.state = "RECONNECTING"
            runtime.restart_count += 1
            runtime.next_retry_monotonic = now + self.args.reconnect_seconds
            self._publish_status(runtime)
            return
        if (
            runtime.state == "CONNECTING"
            and now - runtime.started_monotonic >= self.args.online_after_seconds
        ):
            runtime.state = "ONLINE"
            self._publish_status(runtime)

    def run(self) -> int:
        self._mqtt.connect(self.args.mqtt_host, self.args.mqtt_port, 60)
        self._mqtt.loop_start()
        if not self.mqtt_connected.wait(timeout=10.0):
            print(
                json.dumps(
                    {
                        "kind": "mqtt_start_degraded",
                        "host": self.args.mqtt_host,
                        "port": self.args.mqtt_port,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        last_telemetry = 0.0
        try:
            while not self.stop_event.wait(0.5):
                now = time.monotonic()
                with self.lock:
                    for runtime in self.cameras.values():
                        self._tick_camera(runtime, now)
                    if now - last_telemetry >= self.args.telemetry_seconds:
                        for runtime in self.cameras.values():
                            self._publish_telemetry(runtime)
                        last_telemetry = now
        finally:
            with self.lock:
                for runtime in self.cameras.values():
                    runtime.desired_online = False
                    self._stop_camera(runtime, state="OFFLINE")
            self._publish_json(
                "vmt/emulator/status",
                {"state": "OFFLINE", "at": utc_now()},
                retain=True,
            )
            self._mqtt.loop_stop()
            self._mqtt.disconnect()
        return 0

    def request_stop(self, *_args) -> None:
        self.stop_event.set()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "config/emulator/vmt-cameras.json",
    )
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=ROOT / "artifacts/mvp-temporal/fixtures.json",
    )
    parser.add_argument("--publish-rtsp-base", default="rtsp://rtsp-server:8554")
    parser.add_argument("--advertised-rtsp-base", default="rtsp://127.0.0.1:8554")
    parser.add_argument("--mqtt-host", default="broker")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--mqtt-client-id", default="echo-vmt-camera-emulator")
    parser.add_argument("--telemetry-seconds", type=float, default=5.0)
    parser.add_argument("--reconnect-seconds", type=float, default=2.0)
    parser.add_argument("--online-after-seconds", type=float, default=1.0)
    parser.add_argument("--ffmpeg-bin", default="ffmpeg")
    parser.add_argument("--ffmpeg-loglevel", default="warning")
    args = parser.parse_args()
    if (
        args.telemetry_seconds <= 0
        or args.reconnect_seconds <= 0
        or args.online_after_seconds < 0
    ):
        parser.error(
            "telemetry/reconnect must be positive and online-after non-negative"
        )
    app = VmtCameraEmulator(args)
    signal.signal(signal.SIGTERM, app.request_stop)
    signal.signal(signal.SIGINT, app.request_stop)
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
