# External Gates

**Status:** `ACTIVE_REGISTER`

## 1. Definición

Un external gate es una condición que el repositorio no puede cerrar mediante documentación o búsqueda web porque depende de hardware, una persona, una red, credenciales, autorización o ambiente físico. Se registra explícitamente para evitar dos fallos: fingir que está resuelto o bloquear innecesariamente trabajo independiente.

## 2. Cámara y entorno de campo

| Gate | Estado | Evidencia para cierre | Bloquea |
|---|---|---|---|
| XG-01 modelo exacto | EXTERNAL_GATE_OPEN | marca/modelo/ficha o acceso | compatibility claim |
| XG-02 audio disponible | EXTERNAL_GATE_OPEN | audio stream verificado | camera audio ingest |
| XG-03 RTSP profile/URI | EXTERNAL_GATE_OPEN | conexión autorizada | real RTSP E2E |
| XG-04 ONVIF | EXTERNAL_GATE_OPEN | discovery/profile test | auto-discovery only |
| XG-05 codec/sample-rate/channels | EXTERNAL_GATE_OPEN | probe del stream | codec certification |
| XG-06 credentials | EXTERNAL_GATE_OPEN | secret provisioned fuera de Git | connection |
| XG-07 reachability | EXTERNAL_GATE_OPEN | LAN/VPN/firewall test | field integration |
| XG-08 concurrency limit | EXTERNAL_GATE_OPEN | controlled multi-client test/docs | fan-out design confirmation |
| XG-09 permission to capture | EXTERNAL_GATE_OPEN | authorization record | field dataset |
| XG-10 test location | EXTERNAL_GATE_OPEN | site + safe protocol | distance/SNR evidence |
| XG-11 safe event playback | EXTERNAL_GATE_OPEN | approved test events/procedure | some positive classes |
| XG-12 mic fallback | EXTERNAL_GATE_OPEN | approved USB/IP mic if needed | fallback ingest |

## 3. Privacy/compliance gate

Antes de captar audio real debe documentarse propósito de prueba, responsable, acceso, retention, almacenamiento y autorización/base aplicable. El repositorio no sustituye revisión institucional/jurídica cuando corresponda.

## 4. Información que se solicita a la profesora

```text
camera/NVR brand + model
whether audio exists
RTSP/ONVIF support
codec/sample rate if known
network access method
whether credentials can be issued for the project
whether controlled recordings/tests are authorized
physical location/range available
whether an external microphone fallback is allowed
```

Nunca se solicita publicar credenciales en issues o Markdown.

## 5. Evidencia de cierre

Cerrar un gate exige un artefacto verificable: probe output saneado, test log, foto/model identifier, config export sin secrets, autorización o measurement bundle. El cierre debe enlazarse en `CERTIFICATION-LEDGER.md`.

## 6. Dependency behavior

Un external gate puede bloquear una rama de claims sin bloquear toda la ingeniería. Por ejemplo, XG-03 bloquea real-camera ingestion, pero no impide validar source abstraction con replay.

## 7. Invalidation

Cambio de cámara, NVR, firmware, red, ubicación o política de autorización puede reabrir gates previamente cerrados.