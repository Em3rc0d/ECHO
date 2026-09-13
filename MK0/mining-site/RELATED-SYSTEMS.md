# Related Systems — MK0

**Status:** `CERTIFIED_LANDSCAPE / NON-COPYING_REFERENCE`

## Purpose

Study systems that solve adjacent parts of the pipeline so ECHO can reuse proven architectural patterns without falsely claiming novelty for commodity components or copying a whole product.

## Frigate

Open-source NVR oriented to camera processing. Relevant because documentation includes audio detection per camera and MQTT integration. Lessons: camera-scoped configuration/health, dedicated audio role, topic-based event exposure and practical FFmpeg/stream handling. Difference: ECHO's promise and engineering evidence center on acoustic event detection/classification, benchmark governance and a source-agnostic acoustic event layer rather than full NVR functionality.

## YAMNet real-time/community projects

Several public projects demonstrate microphone/stream -> YAMNet -> selected labels/notification. They validate the feasibility of continuous inference and transfer learning, but typically lack ECHO's data/license governance, model comparison, source abstraction, temporal event semantics or multi-source certification.

## Cry/baby-monitor style projects

Useful examples of IP-camera/RTSP audio extraction feeding YAMNet or similar models with notifications. Their narrow classes and domestic context do not directly establish ECHO robustness.

## Acoustic localization projects

Microphone-array systems combine SED with direction-of-arrival/localization. They are related but out of current scope because ECHO does not require array-based direction estimation to satisfy its promise.

## Commercial/vendor analytics

Some camera/NVR vendors provide audio anomaly/event detection. They demonstrate market relevance but may have closed data/models, device lock-in and opaque evaluation, so they are not the scientific baseline.

## Comparison dimensions

For every related system consider source protocols, model, labels, streaming, event aggregation, multi-source behavior, Pub/Sub/API, hardware footprint, license, maintenance and limitations.

## Engineering conclusion

The individual pieces—RTSP, audio classification, MQTT—are not novel. ECHO's own value is the certified acoustic pipeline, controllable taxonomy/data/model benchmark, multi-source event semantics and reproducible evidence within its fixed promise.

## Invalidation

Update when a directly comparable open project materially changes the state of the art or offers a component that invalidates an ECHO assumption.