import { readFile, stat } from "node:fs/promises";
import { join } from "node:path";
import { config } from "./config.js";
import { db } from "./db.js";
import { ingest, Rejected } from "./ingest.js";
export type Live = {
  source_id: string;
  state: string;
  at?: string;
  session?: string;
  worker_generation?: number;
  scores: Record<string, number>;
  waveform_envelope: number[];
  windows?: number;
  rms?: number;
  peak?: number;
  window_start_utc?: string;
  window_end_utc?: string;
  estimated_lag_ms?: number | null;
  events: unknown[];
  mode: string;
  age_ms: number | null;
  stale: boolean;
};
export const live = new Map<string, Live>();
const processedDiagnostics = new Set<string>();
export async function refreshLive() {
  const rows = (await db.query("SELECT source_id FROM sources WHERE enabled"))
    .rows;
  for (const { source_id: id } of rows) {
    if (!/^[A-Za-z0-9_-]{1,80}$/.test(id)) continue;
    try {
      const path = join(config.liveDir, id + ".json");
      if ((await stat(path)).size > 256 * 1024)
        throw new Error("Snapshot oversized");
      const data = JSON.parse(await readFile(path, "utf8"));
      if (data.source_id !== id) throw new Error("Snapshot source mismatch");
      const stamp = Date.parse(data.at);
      const age = Number.isFinite(stamp)
        ? Math.max(0, Date.now() - stamp)
        : null;
      const stale = age === null || age > 15000 || stamp > Date.now() + 5000;
      const scores: Record<string, number> = {};
      for (const label of ["GLASS_SHATTER", "SIREN", "VEHICLE_HORN"]) {
        const value = data.scores?.[label];
        if (
          typeof value === "number" &&
          Number.isFinite(value) &&
          value >= 0 &&
          value <= 1
        )
          scores[label] = value;
      }
      const current: Live = {
        source_id: id,
        state: stale ? "STALE" : String(data.state || "UNKNOWN"),
        at: data.at,
        session: data.session,
        worker_generation: data.stream_generation,
        scores,
        waveform_envelope: Array.isArray(data.waveform_envelope)
          ? data.waveform_envelope
              .slice(0, 64)
              .map((x: unknown) =>
                typeof x === "number" && Number.isFinite(x)
                  ? Math.max(0, Math.min(1, x))
                  : 0,
              )
          : [],
        windows: data.windows,
        rms: data.rms,
        peak: data.peak,
        window_start_utc: data.window_start_utc,
        window_end_utc: data.window_end_utc,
        estimated_lag_ms: Number.isFinite(
          stamp - Date.parse(data.window_end_utc),
        )
          ? Math.max(0, stamp - Date.parse(data.window_end_utc))
          : null,
        events: Array.isArray(data.events) ? data.events.slice(-20) : [],
        mode: "LAB_RTSP_DIAGNOSTIC_ONLY",
        age_ms: age,
        stale,
      };
      live.set(id, current);
      for (const event of current.events) {
        const candidate = event as {
          event_id?: string;
          provenance?: { lifecycle?: string };
        };
        const key =
          typeof candidate?.event_id === "string" &&
          candidate.provenance?.lifecycle
            ? `${candidate.event_id}:${candidate.provenance.lifecycle}`
            : null;
        if (key && processedDiagnostics.has(key)) continue;
        try {
          await ingest(event, true);
          if (key) {
            if (processedDiagnostics.size >= 5000) processedDiagnostics.clear();
            processedDiagnostics.add(key);
          }
        } catch (err) {
          if (!(err instanceof Rejected)) throw err;
        }
      }
    } catch (err) {
      if ((err as NodeJS.ErrnoException).code === "ENOENT")
        live.set(id, {
          source_id: id,
          state: "NO_DATA",
          scores: {},
          waveform_envelope: [],
          events: [],
          mode: "LAB_RTSP_DIAGNOSTIC_ONLY",
          stale: true,
          age_ms: null,
        });
      else if (
        (err as Error).message.includes("Snapshot") ||
        err instanceof SyntaxError
      )
        live.delete(id);
      else throw err;
    }
  }
  for (const id of live.keys())
    if (!rows.some((r) => r.source_id === id)) live.delete(id);
}
