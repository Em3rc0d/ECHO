import { readFileSync } from "node:fs";
import { Ajv2020 } from "ajv/dist/2020.js";
import { createRequire } from "node:module";
import type { FormatsPlugin } from "ajv-formats";
import { config } from "./config.js";
const require = createRequire(import.meta.url);
const addFormats = require("ajv-formats") as FormatsPlugin;
const ajv = new Ajv2020({ strict: false, allErrors: true });
addFormats(ajv);
const schema = JSON.parse(
  readFileSync(process.env.EVENT_SCHEMA || "/app/event.schema.json", "utf8"),
);
const validate = ajv.compile(schema);
export type AcousticEvent = {
  schema_version: string;
  event_id: string;
  source_id: string;
  site_id: string;
  event_type: string;
  onset_utc: string;
  end_utc: string | null;
  confidence: { peak: number; mean: number };
  model_version: string;
  threshold_version: string;
  stream_session_id: string;
  provenance: { lifecycle: string; [key: string]: unknown };
};
export function parseEvent(raw: unknown): AcousticEvent {
  if (!validate(raw)) throw new Error("EVENT_SCHEMA_INVALID");
  const e = raw as AcousticEvent;
  if (
    !Number.isFinite(Date.parse(e.onset_utc)) ||
    (e.end_utc != null && !Number.isFinite(Date.parse(e.end_utc)))
  )
    throw new Error("TIMESTAMP_INVALID");
  if (e.confidence.mean > e.confidence.peak)
    throw new Error("CONFIDENCE_ORDER_INVALID");
  if (!["GLASS_SHATTER", "SIREN", "VEHICLE_HORN"].includes(e.event_type))
    throw new Error("UNSUPPORTED_ACTIVE_TARGET");
  if (!["CONFIRMED", "CLOSED"].includes(e.provenance?.lifecycle))
    throw new Error("LIFECYCLE_REQUIRED");
  if (
    e.provenance.lifecycle === "CLOSED" &&
    (!e.end_utc || Date.parse(e.end_utc) < Date.parse(e.onset_utc))
  )
    throw new Error("END_INVALID");
  if (e.provenance.lifecycle === "CONFIRMED" && e.end_utc != null)
    throw new Error("CONFIRMED_END_INVALID");
  if (
    [
      e.event_id,
      e.source_id,
      e.site_id,
      e.model_version,
      e.threshold_version,
      e.stream_session_id,
    ].some((s) => !s || s.length > 256)
  )
    throw new Error("IDENTITY_TOO_LONG");
  return e;
}
type Profile = {
  profile_id: string;
  site_id: string;
  source_id: string;
  model_version: string;
  threshold_version: string;
};
// Empty by default. Only a separately authorized upstream acceptance adapter may supply this evidence.
const routing = JSON.parse(readFileSync(config.routingPath, "utf8")) as {
  version: string;
  approved_upstream_profiles: Profile[];
};
export function originFor(e: AcousticEvent, diagnostic = false): string {
  if (diagnostic) return "LAB_DIAGNOSTIC";
  const a = e.provenance.operator_acceptance as
    | { accepted?: boolean; profile_id?: string }
    | undefined;
  if (
    a?.accepted === true &&
    routing.approved_upstream_profiles.some(
      (p) =>
        p.profile_id === a.profile_id &&
        p.site_id === e.site_id &&
        p.source_id === e.source_id &&
        p.model_version === e.model_version &&
        p.threshold_version === e.threshold_version,
    )
  )
    return "ACCEPTED_OPERATIONAL";
  return "CONTROLLED_OR_UNASSESSED";
}
export const descriptions: Record<string, string> = {
  GLASS_SHATTER: "Sonido compatible con rotura de vidrio",
  SIREN: "Actividad acústica tipo sirena",
  VEHICLE_HORN: "Sonido compatible con claxon",
};
