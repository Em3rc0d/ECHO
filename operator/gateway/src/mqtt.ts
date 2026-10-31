import mqtt from "mqtt";
import { config, secret } from "./config.js";
import { db } from "./db.js";
import { ingest, reject, Rejected } from "./ingest.js";
export const broker = mqtt.connect(config.mqtt, {
  clientId: "echo-operator-gateway-v1",
  clean: false,
  protocolVersion: 4,
  reconnectPeriod: 2000,
  connectTimeout: 10000,
  queueQoSZero: false,
  username: secret("MQTT_USERNAME", false) || undefined,
  password: secret("MQTT_PASSWORD", false) || undefined,
});
export const mqttHealth = {
  connected: false,
  last_message_at: null as string | null,
  rejected: 0,
};
broker.on("connect", () => {
  mqttHealth.connected = true;
  broker.subscribe(
    [config.topic, "vmt/cameras/+/status", "vmt/cameras/+/telemetry"],
    { qos: 1 },
  );
});
broker.on("close", () => {
  mqttHealth.connected = false;
});
broker.on("error", () => {
  mqttHealth.connected = false;
});
// MQTT.js invokes callback before QoS1 PUBACK. Do not use an async message listener.
broker.handleMessage = (packet, done) => {
  const processPacket = async () => {
    const payload = Buffer.isBuffer(packet.payload)
      ? packet.payload
      : Buffer.from(packet.payload);
    try {
      if (payload.length > 262144) throw new Rejected("PACKET_TOO_LARGE");
      let data;
      try {
        data = JSON.parse(payload.toString("utf8"));
      } catch {
        throw new Rejected("JSON_INVALID");
      }
      if (packet.topic === config.topic) await ingest(data);
      else {
        const match =
          /^vmt\/cameras\/([A-Za-z0-9_-]{1,80})\/(?:status|telemetry)$/.exec(
            packet.topic,
          );
        if (
          !match ||
          data.source_id !== match[1] ||
          data.version !== "ECHO-VMT-CAMERA-EMULATOR-v1" ||
          ![
            "ONLINE",
            "OFFLINE",
            "STARTING",
            "CONNECTING",
            "RECONNECTING",
            "STOPPING",
            "ERROR",
          ].includes(data.state) ||
          !Number.isFinite(Date.parse(data.at)) ||
          !Number.isSafeInteger(data.stream_generation)
        )
          throw new Rejected("TELEMETRY_INVALID");
        await db.query(
          `INSERT INTO source_health(source_id,state,emulator_generation,scenario,source_at)
     SELECT source_id,$2,$3,$4,$5 FROM sources WHERE source_id=$1 AND site_id=$6 AND emulated
     ON CONFLICT(source_id) DO UPDATE SET state=EXCLUDED.state,emulator_generation=EXCLUDED.emulator_generation,
     scenario=EXCLUDED.scenario,source_at=EXCLUDED.source_at,received_at=now()
     WHERE source_health.source_at IS NULL OR source_health.source_at<=EXCLUDED.source_at`,
          [
            data.source_id,
            data.state,
            data.stream_generation,
            String(data.scenario || "").slice(0, 80),
            data.at,
            data.site_id,
          ],
        );
      }
      mqttHealth.last_message_at = new Date().toISOString();
    } catch (err) {
      if (!(err instanceof Rejected)) throw err;
      mqttHealth.rejected++;
      await reject(packet.topic, payload, err.message);
    }
  };
  processPacket()
    .then(() => done())
    .catch(() => {
      // Do not acknowledge storage failures. Supervisor restarts and broker redelivers.
      broker.end(true);
      process.exitCode = 1;
      setTimeout(() => process.exit(1), 20);
    });
};
export async function control(source: string, payload: object) {
  if (!broker.connected) throw new Error("MQTT_UNAVAILABLE");
  await Promise.race([
    broker.publishAsync(
      `vmt/cameras/${source}/control`,
      JSON.stringify(payload),
      { qos: 1, retain: false },
    ),
    new Promise((_, reject) => {
      const t = setTimeout(
        () => reject(new Error("MQTT_PUBLISH_TIMEOUT")),
        5000,
      );
      t.unref();
    }),
  ]);
  return { accepted_by_broker: true, camera_acknowledged: false };
}
