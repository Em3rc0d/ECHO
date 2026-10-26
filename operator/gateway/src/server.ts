import Fastify from "fastify";
import cookie from "@fastify/cookie";
import rateLimit from "@fastify/rate-limit";
import staticFiles from "@fastify/static";
import { randomBytes, randomUUID } from "node:crypto";
import { Readable } from "node:stream";
import { z, ZodError } from "zod";
import { config } from "./config.js";
import { db, transaction, audit } from "./db.js";
import {
  authenticate,
  digest,
  hashPassword,
  verifyPassword,
  operator,
  type User,
} from "./auth.js";
import { broker, mqttHealth, control } from "./mqtt.js";
import { live, refreshLive } from "./live.js";
import {
  deliverPush,
  labPush,
  pushReady,
  vapidPublic,
  validEndpoint,
} from "./push.js";

const app = Fastify({
  logger: {
    redact: [
      "req.headers.cookie",
      "req.headers.authorization",
      "password",
      "subscription",
    ],
  },
  bodyLimit: 16384,
  trustProxy: (_address: string, hop: number) => hop === 0,
});
await app.register(cookie);
await app.register(rateLimit, { max: 600, timeWindow: "1 minute" });
app.decorateRequest("user");
const id = z.string().regex(/^[A-Za-z0-9_-]{1,80}$/);
const eventId = z.string().min(1).max(256);
function forbidden() {
  return Object.assign(new Error("FORBIDDEN"), { statusCode: 403 });
}
function requireAdmin(user: User) {
  if (user.role !== "admin") throw forbidden();
}
async function sourceFor(user: User, source: string) {
  const r = await db.query(
    "SELECT * FROM sources WHERE source_id=$1 AND site_id=ANY($2::text[])",
    [source, user.sites],
  );
  if (!r.rowCount)
    throw Object.assign(new Error("SOURCE_NOT_FOUND"), { statusCode: 404 });
  return r.rows[0];
}
app.addHook("onRequest", async (req, reply) => {
  reply
    .header("X-Content-Type-Options", "nosniff")
    .header("Referrer-Policy", "same-origin")
    .header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    .header(
      "Content-Security-Policy",
      "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; media-src 'self' blob:; connect-src 'self'; worker-src 'self' blob:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
    );
  if (
    req.routeOptions.url?.startsWith("/api/") ||
    req.url.startsWith("/api/")
  ) {
    reply.header("Cache-Control", "no-store");
    if (
      !["GET", "HEAD", "OPTIONS"].includes(req.method) &&
      req.headers.origin !== config.origin
    )
      return reply.code(403).send({ error: "ORIGIN_DENIED" });
    if (req.routeOptions.url !== "/api/login") {
      const user = await authenticate(req);
      if (!user) return reply.code(401).send({ error: "SESSION_REQUIRED" });
      req.user = user;
    }
  }
});
app.setErrorHandler((error, req, reply) => {
  if (error instanceof ZodError)
    return reply.code(400).send({ error: "INPUT_INVALID" });
  const err = error as Error & { statusCode?: number };
  const status = err.statusCode || 500;
  if (status >= 500) req.log.error({ err: error }, "Request failed");
  reply
    .code(status)
    .send({ error: status >= 500 ? "SERVICE_ERROR" : err.message });
});
app.post(
  "/api/login",
  { config: { rateLimit: { max: 5, timeWindow: "1 minute" } } },
  async (req, reply) => {
    const b = z
      .object({
        username: z.string().min(1).max(80),
        password: z.string().min(1).max(256),
      })
      .parse(req.body);
    const row = (
      await db.query("SELECT * FROM users WHERE username=$1 AND enabled", [
        b.username,
      ])
    ).rows[0];
    // Constant-work dummy verification limits username enumeration by computation time.
    const hash =
      row?.password_hash ||
      "00000000000000000000000000000000:" + "00".repeat(64);
    const valid = verifyPassword(b.password, hash);
    if (!row || !valid) {
      await audit(null, "LOGIN_FAILED", null);
      return reply.code(401).send({ error: "INVALID_CREDENTIALS" });
    }
    const token = randomBytes(32).toString("hex");
    if (req.cookies.echo_session)
      await db.query("DELETE FROM sessions WHERE token_hash=$1", [
        digest(req.cookies.echo_session),
      ]);
    await db.query(
      `INSERT INTO sessions VALUES($1,$2,now()+interval '8 hours')`,
      [digest(token), row.user_id],
    );
    await audit(row.user_id, "LOGIN", row.user_id);
    reply.setCookie("echo_session", token, {
      path: "/",
      httpOnly: true,
      sameSite: "strict",
      secure: config.origin.startsWith("https:"),
      maxAge: 28800,
    });
    return { ok: true };
  },
);
app.post("/api/logout", async (req, reply) => {
  await db.query("DELETE FROM sessions WHERE token_hash=$1", [
    digest(req.cookies.echo_session!),
  ]);
  reply.clearCookie("echo_session", { path: "/" });
  return { ok: true };
});
app.get("/api/me", async (req) => ({
  user: req.user,
  lab_push_enabled: config.lab,
  push_ready: pushReady,
  vapid_public_key: vapidPublic,
}));
async function snapshot(user: User) {
  const sources = (
    await db.query(
      `SELECT s.*,h.state AS camera_state,h.emulator_generation,h.scenario,h.source_at,
 h.received_at FROM sources s LEFT JOIN source_health h USING(source_id) WHERE s.site_id=ANY($1::text[]) ORDER BY s.source_id`,
      [user.sites],
    )
  ).rows;
  const events = (
    await db.query(
      `SELECT * FROM acoustic_events WHERE site_id=ANY($1::text[]) ORDER BY onset_utc DESC,event_id LIMIT 50`,
      [user.sites],
    )
  ).rows;
  const alerts = (
    await db.query(
      `SELECT a.*,e.source_id,e.site_id,e.event_type,e.onset_utc,e.lifecycle,e.origin
 FROM operational_alerts a JOIN acoustic_events e USING(event_id) WHERE e.site_id=ANY($1::text[])
 ORDER BY CASE a.state WHEN 'NEW' THEN 0 WHEN 'ACKNOWLEDGED' THEN 1 ELSE 2 END,a.created_at DESC LIMIT 100`,
      [user.sites],
    )
  ).rows;
  const safe = sources.map((s) => {
    const worker = live.get(s.source_id);
    const stamp = new Date(s.source_at || 0).getTime();
    const age = Date.now() - stamp;
    const state = !s.enabled
      ? "DISABLED"
      : !s.source_at
        ? "UNKNOWN"
        : age > 20000 || age < -5000
          ? "STALE"
          : s.camera_state;
    const diagnostic = worker
      ? {
          ...worker,
          events: worker.events.slice(-10).map((raw) => {
            const e = raw as {
              event_id?: string;
              event_type?: string;
              provenance?: { lifecycle?: string };
            };
            return {
              event_id: e?.event_id,
              event_type: e?.event_type,
              provenance: { lifecycle: e?.provenance?.lifecycle },
            };
          }),
        }
      : null;
    return { ...s, camera_state: state, live: diagnostic };
  });
  const counts = (
    await db.query(
      `SELECT a.state,count(*)::int AS count FROM operational_alerts a
    JOIN acoustic_events e USING(event_id) WHERE e.site_id=ANY($1::text[]) GROUP BY a.state`,
      [user.sites],
    )
  ).rows;
  return {
    at: new Date().toISOString(),
    sources: safe,
    events,
    alerts,
    alert_totals: Object.fromEntries(counts.map((r) => [r.state, r.count])),
    mqtt: mqttHealth,
    boundary: "LAB / CONTROLLED · FIELD ROBUSTNESS GATE OPEN",
    capacity: "UNMEASURED",
  };
}
app.get("/api/snapshot", async (req) => snapshot(req.user));
let clientCount = 0;
app.get("/api/stream", async (req, reply) => {
  if (clientCount >= 50)
    return reply.code(503).send({ error: "STREAM_CAPACITY" });
  clientCount++;
  reply.hijack();
  reply.raw.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-store",
    Connection: "keep-alive",
    "X-Accel-Buffering": "no",
    "X-Content-Type-Options": "nosniff",
  });
  let busy = false,
    closed = false;
  const send = async () => {
    if (busy || closed) return;
    busy = true;
    try {
      const user = await authenticate(req);
      if (!user) {
        reply.raw.end();
        return;
      }
      if (reply.raw.writableLength > 262144) {
        reply.raw.end();
        return;
      }
      const payload = JSON.stringify(await snapshot(user));
      if (Buffer.byteLength(payload) > 2 * 1024 * 1024) {
        reply.raw.write(
          'event: capacity\ndata: {"error":"SNAPSHOT_CAPACITY"}\n\n',
        );
        reply.raw.end();
        return;
      }
      reply.raw.write(`event: snapshot\ndata: ${payload}\n\n`);
    } catch {
      reply.raw.end();
    } finally {
      busy = false;
    }
  };
  const timer = setInterval(() => void send(), 2000);
  reply.raw.on("close", () => {
    closed = true;
    clearInterval(timer);
    clientCount--;
  });
  await send();
});
app.get("/api/events", async (req) => {
  const q = z
    .object({
      source: z.string().max(80).optional(),
      type: z.enum(["GLASS_SHATTER", "SIREN", "VEHICLE_HORN"]).optional(),
      lifecycle: z.enum(["CONFIRMED", "CLOSED"]).optional(),
      origin: z
        .enum([
          "LAB_DIAGNOSTIC",
          "CONTROLLED_OR_UNASSESSED",
          "ACCEPTED_OPERATIONAL",
        ])
        .optional(),
      from: z.iso.datetime().optional(),
      to: z.iso.datetime().optional(),
      offset: z.coerce.number().int().min(0).max(100000).default(0),
    })
    .parse(req.query);
  return {
    events: (
      await db.query(
        `SELECT * FROM acoustic_events WHERE site_id=ANY($1::text[])
 AND ($2::text IS NULL OR source_id=$2) AND ($3::text IS NULL OR event_type=$3)
 AND ($4::text IS NULL OR lifecycle=$4) AND ($5::text IS NULL OR origin=$5)
 AND ($6::timestamptz IS NULL OR onset_utc>=$6) AND ($7::timestamptz IS NULL OR onset_utc<=$7)
 ORDER BY onset_utc DESC,event_id LIMIT 50 OFFSET $8`,
        [
          req.user.sites,
          q.source || null,
          q.type || null,
          q.lifecycle || null,
          q.origin || null,
          q.from || null,
          q.to || null,
          q.offset,
        ],
      )
    ).rows,
  };
});
app.get("/api/events/:event", async (req, reply) => {
  const event = eventId.parse((req.params as { event: string }).event);
  const row = (
    await db.query(
      "SELECT * FROM acoustic_events WHERE event_id=$1 AND site_id=ANY($2::text[])",
      [event, req.user.sites],
    )
  ).rows[0];
  if (!row) return reply.code(404).send({ error: "EVENT_NOT_FOUND" });
  const receipts = (
    await db.query(
      "SELECT lifecycle,payload,received_at FROM event_receipts WHERE event_id=$1 ORDER BY received_at",
      [event],
    )
  ).rows;
  const alert =
    (
      await db.query("SELECT * FROM operational_alerts WHERE event_id=$1", [
        event,
      ])
    ).rows[0] || null;
  const history = (
    await db.query(
      "SELECT action,detail,created_at FROM audit_logs WHERE entity_id=$1 ORDER BY created_at DESC LIMIT 50",
      [alert?.alert_id || event],
    )
  ).rows;
  return { event: row, receipts, alert, history };
});
app.post("/api/alerts/:alert/:action", async (req) => {
  if (!operator(req.user)) throw forbidden();
  const p = z
    .object({ alert: z.uuid(), action: z.enum(["acknowledge", "resolve"]) })
    .parse(req.params);
  return transaction(async (c) => {
    const a = (
      await c.query(
        `SELECT a.* FROM operational_alerts a JOIN acoustic_events e USING(event_id)
   WHERE a.alert_id=$1 AND e.site_id=ANY($2::text[]) FOR UPDATE OF a`,
        [p.alert, req.user.sites],
      )
    ).rows[0];
    if (!a)
      throw Object.assign(new Error("ALERT_NOT_FOUND"), { statusCode: 404 });
    if (p.action === "acknowledge" && a.state === "NEW")
      await c.query(
        `UPDATE operational_alerts SET state='ACKNOWLEDGED',acknowledged_by=$2,acknowledged_at=now() WHERE alert_id=$1`,
        [p.alert, req.user.user_id],
      );
    else if (p.action === "resolve" && a.state === "ACKNOWLEDGED")
      await c.query(
        `UPDATE operational_alerts SET state='RESOLVED',resolved_by=$2,resolved_at=now() WHERE alert_id=$1`,
        [p.alert, req.user.user_id],
      );
    else
      throw Object.assign(new Error("ALERT_STATE_CONFLICT"), {
        statusCode: 409,
      });
    await c.query(
      "INSERT INTO audit_logs(user_id,action,entity_id) VALUES($1,$2,$3)",
      [req.user.user_id, p.action.toUpperCase(), p.alert],
    );
    return { ok: true };
  });
});
app.post(
  "/api/sources/:source/control",
  { config: { rateLimit: { max: 20, timeWindow: "1 minute" } } },
  async (req) => {
    if (!operator(req.user)) throw forbidden();
    const source = id.parse((req.params as { source: string }).source);
    const row = await sourceFor(req.user, source);
    if (!row.emulated || !row.enabled) throw forbidden();
    const payload = z
      .discriminatedUnion("command", [
        z.object({ command: z.literal("restart") }).strict(),
        z
          .object({ command: z.literal("set_online"), online: z.boolean() })
          .strict(),
        z
          .object({
            command: z.literal("set_scenario"),
            scenario: z.enum([
              "negative",
              "glass_shatter",
              "siren",
              "vehicle_horn",
              "silence",
            ]),
          })
          .strict(),
      ])
      .parse(req.body);
    await audit(req.user.user_id, "CAMERA_CONTROL_REQUESTED", source, payload);
    const result = await control(source, payload);
    await audit(
      req.user.user_id,
      "CAMERA_CONTROL_BROKER_ACCEPTED",
      source,
      payload,
    );
    return result;
  },
);
app.get("/api/media/:source/*", async (req, reply) => {
  const p = req.params as { source: string; "*": string };
  const source = await sourceFor(req.user, id.parse(p.source));
  if (!source.enabled || !source.media_path)
    return reply.code(404).send({ error: "MEDIA_UNAVAILABLE" });
  const segment = p["*"];
  if (
    !/^[A-Za-z0-9_/-]+\.(m3u8|mp4|m4s|ts)$/.test(segment) ||
    segment.includes("..")
  )
    return reply.code(400).send({ error: "MEDIA_PATH_INVALID" });
  const target = new URL(`${config.media}/${source.media_path}/${segment}`);
  const q = new URL(req.url, config.origin).searchParams;
  for (const key of ["_HLS_msn", "_HLS_part", "_HLS_skip"])
    if (q.has(key)) target.searchParams.set(key, q.get(key)!.slice(0, 20));
  const response = await fetch(target, {
    signal: AbortSignal.timeout(20000),
    redirect: "error",
  });
  if (!response.ok || !response.body)
    return reply
      .code(response.status >= 400 ? response.status : 502)
      .send({ error: "MEDIA_UPSTREAM_UNAVAILABLE" });
  reply.header(
    "Content-Type",
    response.headers.get("content-type") || "application/octet-stream",
  );
  return reply.send(Readable.fromWeb(response.body as any));
});
app.get("/api/health", async (req) => ({
  at: new Date().toISOString(),
  database: (await db.query("SELECT 1")).rowCount === 1,
  mqtt: mqttHealth,
  live_sources: live.size,
  clients: clientCount,
}));
app.get("/api/push", async (req) => ({
  subscriptions: (
    await db.query(
      "SELECT subscription_id,enabled,created_at FROM push_subscriptions WHERE user_id=$1",
      [req.user.user_id],
    )
  ).rows,
  deliveries: (
    await db.query(
      `SELECT delivery_id,status,attempts,provider_status,created_at FROM notification_deliveries
 JOIN push_subscriptions USING(subscription_id) WHERE user_id=$1 ORDER BY created_at DESC LIMIT 30`,
      [req.user.user_id],
    )
  ).rows,
}));
app.post("/api/push/subscriptions", async (req) => {
  if (!pushReady)
    throw Object.assign(new Error("PUSH_NOT_CONFIGURED"), { statusCode: 503 });
  const b = z
    .object({
      endpoint: z.url().max(2048),
      expirationTime: z.number().nullable().optional(),
      keys: z
        .object({
          p256dh: z.string().regex(/^[A-Za-z0-9_-]{80,160}$/),
          auth: z.string().regex(/^[A-Za-z0-9_-]{16,64}$/),
        })
        .strict(),
    })
    .strict()
    .parse(req.body);
  if (!validEndpoint(b.endpoint))
    throw Object.assign(new Error("PUSH_PROVIDER_DENIED"), { statusCode: 400 });
  // Endpoint ownership cannot silently move between accounts.
  const result = await db.query(
    `INSERT INTO push_subscriptions VALUES($1,$2,$3,$4,true,now())
 ON CONFLICT(endpoint) DO UPDATE SET subscription=EXCLUDED.subscription,enabled=true
 WHERE push_subscriptions.user_id=EXCLUDED.user_id RETURNING subscription_id`,
    [randomUUID(), req.user.user_id, b.endpoint, b],
  );
  if (!result.rowCount)
    throw Object.assign(new Error("SUBSCRIPTION_OWNERSHIP_CONFLICT"), {
      statusCode: 409,
    });
  await audit(
    req.user.user_id,
    "PUSH_SUBSCRIBED",
    result.rows[0].subscription_id,
  );
  return { ok: true };
});
app.delete("/api/push/subscriptions", async (req) => {
  const b = z.object({ endpoint: z.string().max(2048) }).parse(req.body);
  await db.query(
    "UPDATE push_subscriptions SET enabled=false WHERE user_id=$1 AND endpoint=$2",
    [req.user.user_id, b.endpoint],
  );
  return { ok: true };
});
app.post(
  "/api/push/lab",
  { config: { rateLimit: { max: 2, timeWindow: "1 minute" } } },
  async (req) => {
    if (!config.lab || !operator(req.user) || !req.user.sites.length)
      throw forbidden();
    await labPush(req.user.user_id, req.user.sites[0]);
    await audit(req.user.user_id, "LAB_PUSH_REQUESTED", null);
    return { queued: true, lab: true };
  },
);
app.get("/api/admin/users", async (req) => {
  requireAdmin(req.user);
  return {
    users: (
      await db.query(
        `SELECT user_id,username,role,enabled,
 ARRAY(SELECT site_id FROM user_sites us WHERE us.user_id=u.user_id) AS sites FROM users u
 WHERE u.user_id=$1 OR (EXISTS(SELECT 1 FROM user_sites us WHERE us.user_id=u.user_id)
 AND NOT EXISTS(SELECT 1 FROM user_sites us WHERE us.user_id=u.user_id AND NOT(us.site_id=ANY($2::text[]))))
 ORDER BY username`,
        [req.user.user_id, req.user.sites],
      )
    ).rows,
  };
});
app.post("/api/admin/users", async (req) => {
  requireAdmin(req.user);
  const b = z
    .object({
      username: id,
      password: z.string().min(16).max(256),
      role: z.enum(["viewer", "operator", "admin"]),
      sites: z.array(id).max(100),
    })
    .parse(req.body);
  if (!b.sites.every((s) => req.user.sites.includes(s))) throw forbidden();
  const uid = randomUUID();
  await transaction(async (c) => {
    await c.query("INSERT INTO users VALUES($1,$2,$3,$4,true)", [
      uid,
      b.username,
      hashPassword(b.password),
      b.role,
    ]);
    for (const site of new Set(b.sites))
      await c.query("INSERT INTO user_sites VALUES($1,$2)", [uid, site]);
    await c.query(
      "INSERT INTO audit_logs(user_id,action,entity_id) VALUES($1,$2,$3)",
      [req.user.user_id, "USER_CREATED", uid],
    );
  });
  return { user_id: uid };
});
app.patch("/api/admin/users/:user", async (req) => {
  requireAdmin(req.user);
  const uid = z.uuid().parse((req.params as { user: string }).user);
  const b = z
    .object({
      enabled: z.boolean(),
      role: z.enum(["viewer", "operator", "admin"]),
      sites: z.array(id).max(100),
    })
    .parse(req.body);
  if (
    uid === req.user.user_id ||
    !b.sites.every((s) => req.user.sites.includes(s))
  )
    throw forbidden();
  await transaction(async (c) => {
    // Admins can only alter accounts whose existing memberships are within their own scope.
    const target = (
      await c.query("SELECT site_id FROM user_sites WHERE user_id=$1", [uid])
    ).rows;
    if (!target.every((s) => req.user.sites.includes(s.site_id)))
      throw forbidden();
    await c.query("UPDATE users SET enabled=$2,role=$3 WHERE user_id=$1", [
      uid,
      b.enabled,
      b.role,
    ]);
    await c.query("DELETE FROM user_sites WHERE user_id=$1", [uid]);
    for (const site of new Set(b.sites))
      await c.query("INSERT INTO user_sites VALUES($1,$2)", [uid, site]);
    await c.query("DELETE FROM sessions WHERE user_id=$1", [uid]);
    await c.query(
      "INSERT INTO audit_logs(user_id,action,entity_id,detail) VALUES($1,$2,$3,$4)",
      [req.user.user_id, "USER_UPDATED", uid, b],
    );
  });
  return { ok: true };
});
app.post("/api/admin/sources", async (req) => {
  requireAdmin(req.user);
  const b = z
    .object({
      source_id: id,
      site_id: id,
      name: z.string().min(1).max(100),
      kind: z.enum(["ip_camera", "microphone", "replay"]),
      enabled: z.boolean(),
      emulated: z.boolean().default(false),
      media_path: z
        .string()
        .regex(/^[A-Za-z0-9_-]+(?:\/[A-Za-z0-9_-]+)*$/)
        .max(128)
        .nullable()
        .default(null),
    })
    .strict()
    .parse(req.body);
  if (!req.user.sites.includes(b.site_id)) throw forbidden();
  const total = Number(
    (await db.query("SELECT count(*) FROM sources")).rows[0].count,
  );
  const existing = await db.query(
    "SELECT site_id FROM sources WHERE source_id=$1",
    [b.source_id],
  );
  if (existing.rowCount && existing.rows[0].site_id !== b.site_id)
    throw Object.assign(new Error("SOURCE_ID_CONFLICT"), { statusCode: 409 });
  if (total >= 1000 && !existing.rowCount)
    throw Object.assign(new Error("REGISTRY_LIMIT"), { statusCode: 409 });
  await db.query(
    `INSERT INTO sources(source_id,site_id,name,kind,enabled,emulated,media_path) VALUES($1,$2,$3,$4,$5,$6,$7)
 ON CONFLICT(source_id) DO UPDATE SET name=EXCLUDED.name,enabled=EXCLUDED.enabled
 WHERE sources.site_id=EXCLUDED.site_id`,
    [
      b.source_id,
      b.site_id,
      b.name,
      b.kind,
      b.enabled,
      b.emulated,
      b.media_path,
    ],
  );
  await audit(req.user.user_id, "SOURCE_UPSERT", b.source_id, {
    enabled: b.enabled,
  });
  return { ok: true, worker_configuration_required: true };
});
app.post("/api/admin/sites", async (req) => {
  requireAdmin(req.user);
  const b = z
    .object({ site_id: id, name: z.string().min(1).max(100) })
    .parse(req.body);
  await transaction(async (c) => {
    await c.query("INSERT INTO sites VALUES($1,$2)", [b.site_id, b.name]);
    await c.query("INSERT INTO user_sites VALUES($1,$2)", [
      req.user.user_id,
      b.site_id,
    ]);
  });
  await audit(req.user.user_id, "SITE_CREATED", b.site_id);
  return { ok: true };
});
await app.register(staticFiles, { root: config.webRoot, cacheControl: false });
app.setNotFoundHandler((req, reply) => {
  if (req.url.startsWith("/api/"))
    return reply.code(404).send({ error: "NOT_FOUND" });
  if (req.method === "GET" && !req.url.split("?")[0].includes("."))
    return reply.sendFile("index.html");
  return reply.code(404).send({ error: "NOT_FOUND" });
});
let stopping = false;
async function refreshLoop() {
  if (stopping) return;
  try {
    await refreshLive();
  } catch (err) {
    app.log.error({ err }, "Snapshot adapter unavailable");
  }
  if (!stopping) setTimeout(() => void refreshLoop(), 1000).unref();
}
async function pushLoop() {
  if (stopping) return;
  try {
    await deliverPush();
  } catch (err) {
    app.log.error({ err }, "Push delivery unavailable");
  }
  if (!stopping) setTimeout(() => void pushLoop(), 1000).unref();
}
const cleanup = setInterval(
  () =>
    void db
      .query("DELETE FROM sessions WHERE expires_at<now()")
      .catch(() => {}),
  60000,
);
await app.listen({ host: "0.0.0.0", port: 3000 });
void refreshLoop();
void pushLoop();
for (const signal of ["SIGTERM", "SIGINT"])
  process.on(signal, () => {
    stopping = true;
    clearInterval(cleanup);
    broker.end(true);
    void app.close().then(() => db.end());
    setTimeout(() => process.exit(0), 10000).unref();
  });
