// WRITTEN / NOT_EXECUTED: presentation boundary only; no model or network.
import test from "node:test";
import assert from "node:assert/strict";
import {
  snapshotFreshness,
  workerDiagnostics,
} from "../src/worker-diagnostics.js";

test("fresh heartbeat preserves reconnect state without making old scores fresh", () => {
  const now = Date.parse("2026-10-26T20:00:00Z");
  const result = snapshotFreshness(
    {
      state: "RECONNECTING",
      at: "2026-10-26T19:59:00Z",
      updated_at: "2026-10-26T19:59:59Z",
    },
    now,
  );
  assert.equal(result.state, "RECONNECTING");
  assert.equal(result.stale, true);
  assert.equal(result.age_ms, 60000);
  assert.equal(result.snapshot_age_ms, 1000);
  assert.equal(
    snapshotFreshness(
      { state: "CONNECTING", updated_at: "2026-10-26T20:00:00Z" },
      now,
    ).state,
    "CONNECTING",
  );
});
test("legacy snapshots, stale heartbeat and future timestamps remain conservative", () => {
  const now = Date.parse("2026-10-26T20:00:00Z");
  assert.equal(
    snapshotFreshness({ state: "ONLINE", at: "2026-10-26T20:00:00Z" }, now)
      .stale,
    false,
  );
  assert.equal(
    snapshotFreshness(
      {
        state: "ONLINE",
        at: "2026-10-26T20:00:00Z",
        updated_at: "2026-10-26T19:59:00Z",
      },
      now,
    ).state,
    "STALE",
  );
  assert.equal(
    snapshotFreshness({ state: "ONLINE", at: "2026-10-26T21:00:00Z" }, now)
      .stale,
    true,
  );
});
test("diagnostics discard raw URI/credentials, invalid numerics, controls and unbounded stderr", () => {
  const value = workerDiagnostics({
    last_exit_code: 1,
    phase: "BACKOFF",
    backoff_seconds: 30,
    session_windows: 0,
    transport_bytes: Infinity,
    model_wait_seconds: -1,
    rtsp_uri: "rtsp://user:secret@camera/path",
    stderr_tail: Array(100).fill(
      "failure rtsp://user:secret@camera/path token=secret\u001b[31m\n",
    ),
  });
  assert.equal(value.last_exit_code, 1);
  assert.equal(value.backoff_seconds, 30);
  assert.equal(value.session_windows, 0);
  assert.equal(value.transport_bytes, undefined);
  assert.equal(value.model_wait_seconds, undefined);
  assert.equal(value.stderr_tail.length, 16);
  assert.ok(value.stderr_tail.every((s) => s.length <= 600));
  assert.ok(!JSON.stringify(value).includes("rtsp://"));
  assert.ok(!JSON.stringify(value).includes("secret"));
  assert.ok(!("rtsp_uri" in value));
});
