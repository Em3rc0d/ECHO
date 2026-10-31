import webpush from "web-push";
import { randomUUID } from "node:crypto";
import { db, transaction } from "./db.js";
import { config, secret } from "./config.js";
export const vapidPublic = secret("VAPID_PUBLIC_KEY", false);
const privateKey = secret("VAPID_PRIVATE_KEY", false);
export const pushReady = Boolean(vapidPublic && privateKey);
if (pushReady)
  webpush.setVapidDetails(
    process.env.VAPID_SUBJECT || "mailto:operator@example.invalid",
    vapidPublic,
    privateKey,
  );
const hosts = (
  process.env.PUSH_ALLOWED_HOSTS ||
  "fcm.googleapis.com,updates.push.services.mozilla.com,web.push.apple.com"
).split(",");
export function validEndpoint(value: string) {
  try {
    const u = new URL(value);
    return (
      u.protocol === "https:" &&
      !u.username &&
      !u.password &&
      (!u.port || u.port === "443") &&
      hosts.includes(u.hostname)
    );
  } catch {
    return false;
  }
}
export async function labPush(user: string, site: string) {
  const key = `lab:${user}:${randomUUID()}`;
  await transaction(async (c) => {
    const subs = await c.query(
      "SELECT subscription_id FROM push_subscriptions WHERE user_id=$1 AND enabled",
      [user],
    );
    const payload = {
      title: "ECHO · PRUEBA DE LABORATORIO",
      body: "Prueba de entrega. No representa un evento acústico aceptado.",
      url: "/?lab=push",
      tag: key,
      lab: true,
      site_id: site,
    };
    for (const sub of subs.rows)
      await c.query(
        `INSERT INTO notification_deliveries(delivery_id,subscription_id,dedup_key,payload,expires_at)
    VALUES($1,$2,$3,$4,now()+interval '120 seconds')`,
        [randomUUID(), sub.subscription_id, key, payload],
      );
    if (!subs.rowCount) throw new Error("NO_PUSH_SUBSCRIPTION");
  });
}
export async function deliverPush() {
  if (!pushReady) return;
  // One supervised process owns this worker. Recover abandoned leases after a crash.
  await db.query(`UPDATE notification_deliveries SET status='RETRY',next_attempt=now()
 WHERE status='SENDING' AND updated_at<now()-interval '60 seconds'`);
  const row = await transaction(async (c) => {
    await c.query(`UPDATE notification_deliveries SET status='EXPIRED',updated_at=now()
   WHERE status IN ('PENDING','RETRY') AND expires_at<=now()`);
    const r =
      await c.query(`SELECT d.*,s.subscription,s.user_id,s.enabled AS subscribed,u.enabled AS user_enabled,
   EXISTS(SELECT 1 FROM user_sites us WHERE us.user_id=s.user_id AND us.site_id=d.payload->>'site_id') AS authorized
   FROM notification_deliveries d JOIN push_subscriptions s USING(subscription_id) JOIN users u ON u.user_id=s.user_id
   WHERE d.status IN ('PENDING','RETRY') AND d.next_attempt<=now() AND d.expires_at>now()
   ORDER BY d.created_at LIMIT 1 FOR UPDATE OF d SKIP LOCKED`);
    if (!r.rowCount) return null;
    const item = r.rows[0];
    const recent = await c.query(
      `SELECT count(*)::int AS n FROM notification_deliveries d JOIN push_subscriptions s USING(subscription_id)
   WHERE s.user_id=$1 AND d.attempts>0 AND d.updated_at>now()-interval '1 minute'`,
      [item.user_id],
    );
    if (
      !item.subscribed ||
      !item.user_enabled ||
      !item.authorized ||
      (item.payload.lab && !config.lab)
    ) {
      await c.query(
        `UPDATE notification_deliveries SET status='SUPPRESSED',updated_at=now() WHERE delivery_id=$1`,
        [item.delivery_id],
      );
      return null;
    }
    if (recent.rows[0].n >= 5) {
      await c.query(
        `UPDATE notification_deliveries SET next_attempt=now()+interval '15 seconds' WHERE delivery_id=$1`,
        [item.delivery_id],
      );
      return null;
    }
    await c.query(
      `UPDATE notification_deliveries SET status='SENDING',attempts=attempts+1,updated_at=now() WHERE delivery_id=$1`,
      [item.delivery_id],
    );
    return item;
  });
  if (!row) return;
  try {
    if (!validEndpoint(row.subscription.endpoint))
      throw Object.assign(new Error("ENDPOINT_DENIED"), { statusCode: 400 });
    const result = await webpush.sendNotification(
      row.subscription,
      JSON.stringify(row.payload),
      {
        TTL: Math.max(
          1,
          Math.floor((new Date(row.expires_at).getTime() - Date.now()) / 1000),
        ),
        timeout: 10000,
        urgency: "normal",
      },
    );
    await db.query(
      `UPDATE notification_deliveries SET status='PROVIDER_ACCEPTED',provider_status=$2,updated_at=now() WHERE delivery_id=$1`,
      [row.delivery_id, result.statusCode],
    );
  } catch (err) {
    const status = Number((err as { statusCode?: number }).statusCode || 0);
    const expired = status === 404 || status === 410;
    const retry =
      (status === 0 || status === 429 || status >= 500) && row.attempts < 2;
    await transaction(async (c) => {
      if (expired)
        await c.query(
          "UPDATE push_subscriptions SET enabled=false WHERE subscription_id=$1",
          [row.subscription_id],
        );
      await c.query(
        `UPDATE notification_deliveries SET status=$2,provider_status=$3,last_error=$4,
    next_attempt=now()+interval '15 seconds',updated_at=now() WHERE delivery_id=$1`,
        [
          row.delivery_id,
          expired ? "EXPIRED" : retry ? "RETRY" : "FAILED",
          status,
          status ? "PROVIDER_REJECTED" : "NETWORK_ERROR",
        ],
      );
    });
  }
}
