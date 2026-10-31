import { createHash, randomUUID } from "node:crypto";
import { db, transaction } from "./db.js";
import { parseEvent, originFor, descriptions } from "./contracts.js";
export class Rejected extends Error {}
export async function reject(topic: string, payload: Buffer, reason: string) {
  const hash = createHash("sha256").update(topic).update(payload).digest("hex");
  await db.query(
    `INSERT INTO rejected_messages(digest,topic,reason) VALUES($1,$2,$3)
 ON CONFLICT(digest) DO UPDATE SET count=rejected_messages.count+1,last_at=now()`,
    [hash, topic.slice(0, 256), reason.slice(0, 128)],
  );
}
export async function ingest(raw: unknown, diagnostic = false) {
  let e;
  try {
    e = parseEvent(raw);
  } catch (err) {
    throw new Rejected((err as Error).message);
  }
  const lifecycle = e.provenance.lifecycle,
    origin = originFor(e, diagnostic);
  return transaction(async (c) => {
    const source = await c.query(
      "SELECT site_id,enabled FROM sources WHERE source_id=$1",
      [e.source_id],
    );
    if (
      !source.rowCount ||
      source.rows[0].site_id !== e.site_id ||
      !source.rows[0].enabled
    )
      throw new Rejected("SOURCE_NOT_AUTHORIZED");
    await c.query(
      `INSERT INTO acoustic_events(event_id,source_id,site_id,event_type,stream_session_id,onset_utc,
  end_utc,lifecycle,origin,model_version,threshold_version,confidence) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
  ON CONFLICT DO NOTHING`,
      [
        e.event_id,
        e.source_id,
        e.site_id,
        e.event_type,
        e.stream_session_id,
        e.onset_utc,
        e.end_utc,
        lifecycle,
        origin,
        e.model_version,
        e.threshold_version,
        e.confidence,
      ],
    );
    const old = (
      await c.query(
        "SELECT * FROM acoustic_events WHERE event_id=$1 FOR UPDATE",
        [e.event_id],
      )
    ).rows[0];
    if (
      old.source_id !== e.source_id ||
      old.site_id !== e.site_id ||
      old.event_type !== e.event_type ||
      old.stream_session_id !== e.stream_session_id ||
      old.model_version !== e.model_version ||
      old.threshold_version !== e.threshold_version ||
      old.origin !== origin ||
      new Date(old.onset_utc).getTime() !== Date.parse(e.onset_utc)
    )
      throw new Rejected("EVENT_IDENTITY_CONFLICT");
    const receipt = await c.query(
      "INSERT INTO event_receipts(event_id,lifecycle,payload) VALUES($1,$2,$3) ON CONFLICT DO NOTHING RETURNING event_id",
      [e.event_id, lifecycle, e],
    );
    if (!receipt.rowCount) return false;
    if (lifecycle === "CLOSED")
      await c.query(
        `UPDATE acoustic_events SET lifecycle='CLOSED',end_utc=$2,confidence=$3 WHERE event_id=$1`,
        [e.event_id, e.end_utc, e.confidence],
      );
    if (origin === "ACCEPTED_OPERATIONAL" && lifecycle === "CONFIRMED") {
      const alertId = randomUUID();
      const alert = await c.query(
        "INSERT INTO operational_alerts(alert_id,event_id) VALUES($1,$2) ON CONFLICT DO NOTHING RETURNING alert_id",
        [alertId, e.event_id],
      );
      const age = Date.now() - Date.parse(e.onset_utc);
      if (
        alert.rowCount &&
        old.lifecycle !== "CLOSED" &&
        age >= 0 &&
        age < 120000
      ) {
        const subs = await c.query(
          `SELECT s.subscription_id FROM push_subscriptions s JOIN users u USING(user_id)
    JOIN user_sites us ON us.user_id=s.user_id WHERE s.enabled AND u.enabled AND us.site_id=$1`,
          [e.site_id],
        );
        const payload = {
          title: "ECHO · Actividad acústica",
          body: `${e.source_id} · ${descriptions[e.event_type]}. Revise esta fuente.`,
          url: `/events/${encodeURIComponent(e.event_id)}`,
          tag: `event:${e.event_id}`,
          site_id: e.site_id,
          lab: false,
        };
        for (const sub of subs.rows)
          await c.query(
            `INSERT INTO notification_deliveries(delivery_id,subscription_id,dedup_key,payload,expires_at)
    VALUES($1,$2,$3,$4,now()+interval '120 seconds') ON CONFLICT DO NOTHING`,
            [randomUUID(), sub.subscription_id, `event:${e.event_id}`, payload],
          );
      }
    }
    return true;
  });
}
