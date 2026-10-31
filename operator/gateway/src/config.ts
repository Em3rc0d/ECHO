import { readFileSync } from "node:fs";
export function secret(name: string, required = true): string {
  const path = process.env[name + "_FILE"];
  const value = path ? readFileSync(path, "utf8").trim() : process.env[name];
  if (required && !value) throw new Error(`Missing ${name} or ${name}_FILE`);
  return value || "";
}
export const config = {
  production: process.env.NODE_ENV === "production",
  origin: process.env.PUBLIC_ORIGIN || "http://localhost:8090",
  mqtt: process.env.MQTT_URL || "mqtt://broker:1883",
  liveDir: process.env.LIVE_DIR || "/live",
  media: process.env.MEDIA_ORIGIN || "http://rtsp-server:8888",
  lab:
    process.env.ENABLE_LAB_PUSH === "true" &&
    process.env.NODE_ENV !== "production",
  topic: process.env.MQTT_EVENT_TOPIC || "echo/events",
  webRoot: process.env.WEB_ROOT || "/app/public",
  routingPath: process.env.ROUTING_FILE || "/app/config.acceptance.json",
};
if (config.production && !config.origin.startsWith("https://"))
  throw new Error("Production requires HTTPS");
