"""Event publishers for local replay and MQTT delivery."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping


class JsonlEventPublisher:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def publish(self, event: Mapping[str, object]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(event), sort_keys=True) + "\n")


class MqttEventPublisher:
    """Synchronous QoS 1 event publisher.

    The topic is explicit input: ECHO does not invent a new topic convention at
    runtime. QoS 1 can duplicate delivery, so consumers must use event_id as the
    idempotency key.
    """

    def __init__(
        self,
        *,
        host: str,
        port: int,
        topic: str,
        client_id: str = "echo-mvp",
        username: str | None = None,
        password: str | None = None,
        keepalive: int = 60,
    ) -> None:
        try:
            import paho.mqtt.client as mqtt
        except ImportError as exc:
            raise RuntimeError(
                "MQTT publishing requires paho-mqtt; install the 'mvp' extra"
            ) from exc
        if not topic:
            raise ValueError("MQTT topic must be explicit")
        self.topic = topic
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
        )
        if username is not None:
            self._client.username_pw_set(username, password)
        self._client.connect(host, port, keepalive)
        self._client.loop_start()

    def publish(self, event: Mapping[str, object]) -> None:
        payload = json.dumps(dict(event), sort_keys=True, separators=(",", ":"))
        info = self._client.publish(self.topic, payload, qos=1, retain=False)
        info.wait_for_publish()
        if info.rc != 0:
            raise RuntimeError(f"MQTT publish failed with rc={info.rc}")

    def close(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()
