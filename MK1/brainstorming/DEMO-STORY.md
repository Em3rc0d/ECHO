# MK1 Demo Story

**Status:** `DESIGN_SCENARIO / NOT_TEST_EVIDENCE`

## Goal

Demonstrate the same path that is evaluated, without hand-picking a single positive clip and bypassing temporal/event logic.

## Scenario

A deterministic replay source identified as `SIM-CAM-01` feeds continuous audio containing background, confusers and one or more target occurrences. ECHO normalizes/windows audio, emits raw inference internally, consolidates a target through the Event Engine and publishes one confirmed event via MQTT. A subscriber displays/logs the versioned event envelope.

A second replay source can run concurrently to demonstrate source isolation. When real camera access exists, `CAM-01` replaces the replay adapter while the downstream path stays unchanged.

## What the audience sees

Source health; event type; confidence/calibrated score; source ID; timestamp; model/config/schema version; and a delivery log showing one physical occurrence is not spammed as multiple alerts.

## What the demo must not imply

One successful event does not prove field recall, false-alarm rate, distance, model superiority or camera fleet capacity. Those claims come from test reports.

## Failure injection

Optionally disconnect a replay/RTSP source or restart the broker to show explicit degraded/reconnect state without crashing the entire acoustic pipeline.

## Evidence link

The demo should use the same build/config/schema as the test bundle; otherwise it is presentation-only and cannot be cited as certification evidence.

## Invalidation

Update if event lifecycle or product contract changes.