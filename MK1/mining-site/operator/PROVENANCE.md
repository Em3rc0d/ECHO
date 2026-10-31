# Operator provenance

Date: 2026-10-26. Evidence classes are explicit.

* OFFICIAL: PROJECT-CHARTER.md, CERT-ECHO-000, canonical schemas, governance
  free-tier policy and the professor demo scope freeze.
* OBSERVED: PR #56 open/draft at inspection; branch head
  1ee59f1add866120387d3fc9a5f9a0abd4ec664a. Its body predates subsequent browser
  HLS/control code; the inspected source and updated RTSP runbook contain both.
* OBSERVED: existing worker emits bounded atomic JSON diagnostic snapshots with
  real scores/envelope, independent temporal engines and no accepted MQTT target
  publication. Emulator MQTT telemetry has a separate stream_generation.
* OBSERVED: repository workflows use explicit path filters or manual dispatch;
  this increment avoids all automatically validated paths.
* GENERATED: UI palette/tokens/layout, API adapter, SQL operations model,
  source-level acceptance bridge and runbooks. No new empirical claim follows.
* INFERRED: a selected HLS player plus bounded opt-in previews reduces unnecessary
  client streams. Actual device/network/CPU performance is NOT_MEASURED.

Primary implementation references consulted:

* https://github.com/mqttjs/MQTT.js — handleMessage backpressure and QoS handling;
  installed dependency source inspected for callback-before-PUBACK order.
* https://fastify.dev/docs/latest/Reference/Reply/ — SSE hijack lifecycle.
* https://github.com/fastify/fastify-cookie and
  https://github.com/fastify/fastify-static — Fastify plugin compatibility.
* https://github.com/web-push-libs/web-push — VAPID, TTL and provider status.
* https://mediamtx.org/docs/features/expose-the-server-in-a-subfolder — HTTP media
  proxy context; this implementation proxies selected HLS playlists/segments.

Package lockfiles capture exact resolved versions, hashes and license metadata.
No dependencies were used to execute model/runtime tests. npm install lifecycle
scripts were disabled during source preparation. React quality guidance was
applied to subscriptions, cleanup, effects, focus, labels and bounded players.
