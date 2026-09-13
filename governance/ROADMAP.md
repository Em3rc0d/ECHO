# ECHO Roadmap

**Status:** `EVIDENCE_DRIVEN`

## 1. Principio

ECHO no avanza por calendario ni por porcentaje subjetivo. Avanza cuando los nodos del grafo que alimentan la siguiente fase están cerrados o aislados como experimentos/gates externos.

## 2. Camino crítico actual

```text
MK0 CERTIFIED
     |
     +--> MK1 replay build READY
     |        |
     |        v
     |   dataset manifest + baseline pipeline
     |        |
     |        v
     |   A/B/C benchmark
     |        |
     |        v
     |   threshold + Event Engine calibration
     |        |
     |        v
     |   streaming E2E + MQTT + persistence
     |        |
     |        v
     |   error analysis + regression evidence
     |
     +--> EXT-CAMERA-001
              |
              v
         real-camera ingest + field tests

both evidence branches
        -> MK1 CERTIFIED
        -> MK2 design freeze from measurements
        -> MK2 hardening/build
        -> MK2 release certification
```

## 3. MK1 execution sequence

Primero se materializa el corpus/manifest y un replay determinista. Luego se implementan los tres benchmark arms de forma comparable. Solo después de obtener scores se congelan thresholds y Event Engine parameters. Después se conecta Pub/Sub/consumers y se mide el sistema completo. La cámara real se integra cuando el external gate esté disponible sin bloquear el core offline.

## 4. MK1 evidence deliverables

- admitted-asset manifest y license audit;
- split leakage report;
- baseline/challenger configs;
- model result bundles;
- calibration curves;
- long-stream false-positive analysis;
- model winner decision;
- replay E2E event logs;
- runtime profile;
- failure/reconnect evidence;
- camera/field evidence si está disponible;
- MK1 certificate.

## 5. MK2 trigger

MK2 no debe diseñar capacity numbers o SLO finales por anticipación. Los valores iniciales salen de MK1 y se convierten en targets medibles de scale, resilience y operations.

## 6. MK2 workstreams

Multi-source scheduling, capacity, backpressure, durable event delivery si los requisitos lo exigen, observability, model registry/release, security hardening, CI/CD, migration, rollback, drift monitoring, load/soak/chaos y release supply-chain certification.

## 7. External dependencies

La cámara/profesora, permisos de captura, site y hardware objetivo aparecen como gates explícitos. Si llegan tarde, el roadmap conserva trabajo replay/offline válido sin presentar claims falsos de campo.

## 8. Stop-the-line conditions

Detener avance y reabrir upstream si aparece leakage, licencia incompatible, taxonomía incoherente, un modelo no reproducible, un contrato insuficiente, pérdida de source identity, cola sin límite o un false-positive profile que haga inviable la estrategia actual.

## 9. Success definition

El roadmap termina en MK2 release cuando ECHO cumple la promesa dentro de un operating envelope documentado, con limitaciones conocidas y evidencia reproducible; no cuando “ya no queda nada por mejorar”.