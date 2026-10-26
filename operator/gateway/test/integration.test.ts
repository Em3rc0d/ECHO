// Written for an isolated Operator Docker stack. NOT EXECUTED by implementation agent.
import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { db } from "../src/db.js";
import { ingest } from "../src/ingest.js";
import { hashPassword } from "../src/auth.js";
import { config } from "../src/config.js";
const enabled = process.env.ECHO_OPERATOR_TEST_ALLOWED === "true";
test(
  "DB lifecycle idempotency, identity and API site authorization",
  { skip: !enabled },
  async () => {
    const suffix = randomUUID().slice(0, 8),
      site = "TEST-" + suffix,
      source = "TEST-CAM-" + suffix,
      user = randomUUID(),
      password = randomUUID();
    const ids = [randomUUID(), randomUUID()];
    const make = (event: string, lifecycle: string) => ({
      schema_version: "echo.event.v1",
      event_id: event,
      source_id: source,
      site_id: site,
      event_type: "SIREN",
      onset_utc: "2026-10-26T20:00:00Z",
      end_utc: lifecycle === "CLOSED" ? "2026-10-26T20:00:07Z" : null,
      confidence: { peak: 0.8, mean: 0.7 },
      model_version: "test-model",
      threshold_version: "test-policy",
      stream_session_id: "test-session",
      provenance: { lifecycle, evidence_windows: 1 },
    });
    let token = "";
    try {
      await db.query("INSERT INTO sites VALUES($1,$2)", [
        site,
        "Isolated integration fixture",
      ]);
      await db.query(
        `INSERT INTO sources(source_id,site_id,name,kind,emulated) VALUES($1,$2,$1,'ip_camera',true)`,
        [source, site],
      );
      assert.equal(await ingest(make(ids[0], "CONFIRMED")), true);
      assert.equal(await ingest(make(ids[0], "CONFIRMED")), false);
      assert.equal(await ingest(make(ids[0], "CLOSED")), true);
      assert.equal(await ingest(make(ids[0], "CLOSED")), false);
      await ingest(make(ids[1], "CLOSED"));
      await ingest(make(ids[1], "CONFIRMED"));
      const rows = (
        await db.query(
          "SELECT lifecycle,origin FROM acoustic_events WHERE event_id=ANY($1::text[])",
          [ids],
        )
      ).rows;
      assert.equal(rows.length, 2);
      assert.ok(
        rows.every(
          (r) =>
            r.lifecycle === "CLOSED" && r.origin === "CONTROLLED_OR_UNASSESSED",
        ),
      );
      assert.equal(
        (
          await db.query(
            "SELECT * FROM operational_alerts WHERE event_id=ANY($1::text[])",
            [ids],
          )
        ).rowCount,
        0,
      );
      await assert.rejects(
        () =>
          ingest({ ...make(ids[0], "CONFIRMED"), stream_session_id: "forged" }),
        /IDENTITY_CONFLICT/,
      );
      await assert.rejects(
        () => ingest({ ...make(randomUUID(), "CONFIRMED"), site_id: "FORGED" }),
        /SOURCE_NOT_AUTHORIZED/,
      );
      await db.query(`INSERT INTO users VALUES($1,$2,$3,'viewer',true)`, [
        user,
        "test_" + suffix,
        hashPassword(password),
      ]);
      // Viewer deliberately has no site membership; no source/event/media access.
      const base = process.env.TEST_API_BASE || "http://gateway:3000";
      const login = await fetch(base + "/api/login", {
        method: "POST",
        headers: { Origin: config.origin, "Content-Type": "application/json" },
        body: JSON.stringify({ username: "test_" + suffix, password }),
      });
      assert.equal(login.status, 200);
      token = login.headers.get("set-cookie")!.split(";")[0];
      const headers = {
        Origin: config.origin,
        Cookie: token,
        "Content-Type": "application/json",
      };
      assert.equal((await fetch(base + "/api/snapshot")).status, 401);
      const snap = (await (
        await fetch(base + "/api/snapshot", { headers })
      ).json()) as any;
      assert.deepEqual(snap.sources, []);
      assert.deepEqual(snap.events, []);
      assert.equal(
        (await fetch(`${base}/api/events/${ids[0]}`, { headers })).status,
        404,
      );
      assert.equal(
        (await fetch(`${base}/api/media/${source}/index.m3u8`, { headers }))
          .status,
        404,
      );
      assert.equal(
        (
          await fetch(`${base}/api/sources/${source}/control`, {
            method: "POST",
            headers,
            body: JSON.stringify({ command: "restart" }),
          })
        ).status,
        403,
      );
      assert.equal(
        (
          await fetch(base + "/api/logout", {
            method: "POST",
            headers: { Cookie: token, Origin: "https://untrusted.invalid" },
          })
        ).status,
        403,
      );
    } finally {
      await db.query("DELETE FROM audit_logs WHERE user_id=$1", [user]);
      await db.query("DELETE FROM users WHERE user_id=$1", [user]);
      await db.query(
        "DELETE FROM acoustic_events WHERE event_id=ANY($1::text[])",
        [ids],
      );
      await db.query("DELETE FROM sources WHERE source_id=$1", [source]);
      await db.query("DELETE FROM sites WHERE site_id=$1", [site]);
      await db.end();
    }
  },
);
