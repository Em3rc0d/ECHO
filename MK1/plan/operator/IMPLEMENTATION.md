# Operator implementation and handoff plan

Status: CODE_IMPLEMENTED / RUNTIME_NOT_EXECUTED.

| Increment | Source deliverable | Validation state |
|---|---|---|
| Contract adapter | Unchanged canonical event schema + stricter lifecycle checks | Written tests, not run |
| Persistence | Transactional migration, receipts, occurrence, accounts, alerts, audit, outbox | Migration not run |
| Gateway | Durable MQTT handling, read-only diagnostics, REST/SSE, session/site roles | Static type analysis only |
| Presentation | Responsive dark PWA, selected HLS, real scores/envelope, source control, timeline | Browser/visual QA not run |
| Push | Permission/subscription flow, deep links, TTL/retries, provider results, separate LAB route | Mobile delivery not run |
| Operations | Local Docker/secret bootstrap, optional HTTPS config, backup/restore runbook | Docker/build/deploy not run |
| Handoff | Dedicated branch and draft review PR against PR #56 branch | No merge, no certification |

Dependencies: PR #56 supplies worker/emulator support. This increment does not
modify its Python files or frozen professor demo. Review dependency PR first;
then restack the Operator PR after the base is merged if appropriate.

No new workflow is introduced. Reviewed existing automatic workflow path filters:
data-foundry/schema/corpus paths and `.github/workflows/**` are excluded from
this change. Non-main branch push does not match main-only triggers. Draft PR
base is `feat/rtsp-live-monitor-mk1` so its diff excludes the earlier work.
CI skip markers supplement this inspection; they do not replace it.

Gate to release: every required case in test/operator/ACCEPTANCE.md must have
real execution evidence, including restore and the negative acceptance boundary.
The model/domain gate remains independent and cannot be closed by UI QA.
