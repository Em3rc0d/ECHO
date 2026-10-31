import test from "node:test";
import assert from "node:assert/strict";
import { parseEvent, originFor } from "../src/contracts.js";
export const fixture = (overrides: Record<string, unknown> = {}) => ({
  schema_version: "echo.event.v1",
  event_id: "contract-event",
  source_id: "TEST-CAMERA",
  site_id: "TEST-SITE",
  event_type: "SIREN",
  onset_utc: "2026-10-26T20:00:00Z",
  end_utc: null,
  confidence: { peak: 0.8, mean: 0.7 },
  model_version: "test-model",
  threshold_version: "test-policy",
  stream_session_id: "test-session",
  provenance: {
    event_engine: "echo.temporal-event-engine.v1",
    lifecycle: "CONFIRMED",
    evidence_windows: 1,
  },
  ...overrides,
});
test("current MQTT events never gain operational acceptance from a high score", () => {
  const event = parseEvent(fixture({ confidence: { peak: 1, mean: 1 } }));
  assert.equal(originFor(event), "CONTROLLED_OR_UNASSESSED");
  assert.equal(originFor(event, true), "LAB_DIAGNOSTIC");
});
test("an invented upstream acceptance profile cannot authorize delivery", () => {
  const event = parseEvent(
    fixture({
      provenance: {
        lifecycle: "CONFIRMED",
        operator_acceptance: { accepted: true, profile_id: "invented" },
      },
    }),
  );
  assert.equal(originFor(event), "CONTROLLED_OR_UNASSESSED");
});
test("reject unsupported classes and malformed lifecycle timing", () => {
  assert.throws(
    () => parseEvent(fixture({ event_type: "GUNSHOT" })),
    /UNSUPPORTED/,
  );
  assert.throws(
    () => parseEvent(fixture({ provenance: { lifecycle: "CLOSED" } })),
    /END_INVALID/,
  );
  assert.throws(
    () =>
      parseEvent(
        fixture({
          end_utc: "2026-10-26T19:00:00Z",
          provenance: { lifecycle: "CLOSED" },
        }),
      ),
    /END_INVALID/,
  );
  assert.throws(
    () => parseEvent(fixture({ confidence: { peak: 1.1, mean: 0.7 } })),
    /SCHEMA/,
  );
  assert.throws(
    () => parseEvent(fixture({ schema_version: "echo.event.v2" })),
    /SCHEMA/,
  );
});
