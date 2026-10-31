# Operator open gates and limitations

All entries remain OPEN / NOT_EXECUTED unless independently evidenced later.

| Gate | Why it matters | Closure evidence |
|---|---|---|
| G01 Docker image/build/migration | New code has not been started | Exact SHA/image hashes and startup logs |
| G02 Broker reconnect/idempotency | QoS1 can duplicate and reorder | Receipt counts and interruption/replay evidence |
| G03 HLS/browser audio | Browser codec/autoplay/proxy behavior varies | Chrome/Android/iOS playback evidence |
| G04 Domain robustness #53 | Field confusers remain unresolved | Governed hard-negative/untouched holdout evidence |
| G05 Operational acceptance | Empty approved profile list is intentional | Independently approved upstream profile/adapter |
| G06 Push installation/delivery | Secure origin/browser/provider constraints | Real phone subscription, click and delivery records |
| G07 Site/RBAC/CSRF | UI controls are not an authorization boundary | API negative tests with distinct accounts/sites |
| G08 Recovery | A written backup procedure is not a restored DB | Isolated restore + row/hash/access verification |
| G09 Capacity/latency | Existing scorer serializes inference | Source-hours, CPU/RAM/backlog/disconnect measurements |
| G10 Visual/accessibility | Source polish is not visual QA | Screenshots at responsive sizes, Tab/zoom/reduced motion |
| G11 Supply chain | Lockfiles are not a vulnerability certification | Independent dependency/license audit |
| G12 Retention | Event/audit tables grow on disk | Reviewed retention/purge policy and backup expiry |
| G13 VPS/remote plane | Only optional colocated config is supplied | Authorized deployment and secure split-plane adapter |

Known limits: single gateway replica; polling read-only snapshots every second;
SSE every two seconds with up to 50 clients; full per-site snapshot on each tick;
history uses offset pagination, latest dashboard alerts capped at 100; registry
upsert edits name/enabled only for existing sources; new registry entries do not
configure the Acoustic Plane. No assignment/escalation workflow, remote camera
provisioning, learned OOD classifier or certified operational severity exists.

Web Push uses at-least-once outbox attempts and provider acceptance logs, not a
device-delivery receipt. Crash recovery can resend a browser tag. Secret files
and DB push subscription keys require host/backup access controls. Local broker
allows anonymous traffic only on its isolated non-exposed Docker network.

Worker risks remain visible: the supervision hotfix adds independent draining,
bounded queues/watchdog/backoff and FIFO scorer access, but real fairness,
latency and recovery are unmeasured. Stale inference is distinct from heartbeat;
an in-process scorer hang still requires container-level supervision.
Worker snapshots retain at most 20 transitions per source; a gateway outage
longer than that bounded history may lose diagnostic transitions. Accepted MQTT
delivery has its own durable broker/session path and finite queue budget.

No operating envelope, production readiness, zero false positives or 100-camera
capacity is claimed. MK2 remains gated. No certificate is issued or invalidated.

SSE frames are capped at 2 MiB and slow clients are disconnected; diagnostic
transition summaries in snapshots are bounded separately from persisted receipts.

PR #57 P1 review: the `redirect: error` transport and dropped `session` query
were corrected at source level using the pinned MediaMTX query fallback and a
single exact-resource cookie-check redirect. Scripted regression and RBAC cases
are written, NOT_EXECUTED. G03 remains OPEN until real master/child/fragment
playback, user-enabled audio and camera-switch recovery are demonstrated.
