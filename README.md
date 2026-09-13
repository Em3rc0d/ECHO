# ECHO

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

Esta frase es la **promesa inmutable del proyecto**. Cámaras IP, RTSP/ONVIF, Pub/Sub, dashboards, almacenamiento, alertas y cualquier otra integración son infraestructura de soporte; no redefinen el propósito central de ECHO.

## Estado

ECHO se encuentra en fase **research/design-first**. La implementación de producto está deliberadamente bloqueada hasta cerrar los gates de investigación, diseño, arquitectura, planificación y validación definidos en MK0/MK1.

## Método de evolución

Cada milestone mantiene exactamente la misma estructura interna:

```text
brainstorming -> design -> arch -> plan -> build -> test
```

Y además contiene dos áreas de evidencia:

```text
mining-site/
quarries/
```

- **MK0** — investigación exhaustiva, reducción de incertidumbre y evidencia trazable.
- **MK1** — primera versión conceptual/construible, acotada, limpia y con decisiones cerradas.
- **MK2** — producto funcional, robusto, multipunto, reproducible y certificable dentro del alcance definido.

`build/` existe en cada MK por consistencia, pero permanece **GATED / NOT_STARTED** hasta que los nodos anteriores estén cerrados.

## Arquitectura objetivo

```text
IP Camera / Microphone(s)
        |
        v
Source Registry + RTSP/ONVIF
        |
        v
Audio Ingestion (FFmpeg / optional relay)
        |
        v
Normalize -> per-source bounded buffer
        |
        v
Inference Engine
(YAMNet baseline + challengers)
        |
        v
RAW_INFERENCE
        |
        v
Temporal Event Engine
        |
        v
CANDIDATE_EVENT -> CONFIRMED_EVENT
        |
        +------> Event Store / API
        |
        +------> Pub/Sub (MQTT candidate)
                        |
                        v
                  ALERT / subscribers
```

La arquitectura nace **multi-source/multipunto**, aunque la primera PoC puede validar una sola cámara real.

## Principios

1. ECHO clasifica **eventos acústicos observables**; no infiere delitos ni situaciones sociales no demostrables por audio.
2. Ningún threshold, distancia, accuracy o SLO se presenta como hecho sin benchmark propio.
3. La evidencia, datasets, modelos, configuración y decisiones deben tener provenance y versionado.
4. Un cambio upstream invalida los certificados downstream que dependan de él.
5. No se suben credenciales ni datasets raw al repositorio.
6. El audio continuo no se retiene por defecto; privacidad y minimización son requisitos de diseño.

## Navegación

- [`PROJECT-CHARTER.md`](PROJECT-CHARTER.md) — promesa, alcance y reglas inmutables.
- [`MK0/`](MK0/) — investigación, minería y factibilidad.
- [`MK1/`](MK1/) — especificación de la primera build.
- [`MK2/`](MK2/) — especificación del producto robusto.
- [`governance/`](governance/) — gates, decisiones, riesgos y certificación encadenada.
- [`schemas/`](schemas/) — contratos preliminares y event envelope.
- [`research/`](research/) — matrices consolidadas de modelos, datasets y proyectos relacionados.

## Regla de build

> **No programar mientras existan decisiones importantes abiertas que cambien el diseño del sistema.**

La entrada a `MK1/build` requiere cumplir la Definition of Ready y cerrar todos los gates internos que no dependan de una cámara/credencial externa. Las dependencias humanas o físicas se marcan `EXTERNAL_GATE_OPEN`, nunca se inventan.
