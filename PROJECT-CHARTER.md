# ECHO Project Charter

## Promesa inmutable

> **Sistema inteligente para la detección y clasificación de eventos acústicos en ambientes mediante inteligencia artificial.**

Esta formulación es ley de alcance. Ningún milestone puede modificarla sin declarar explícitamente que se trata de otro producto.

## Problema

Los ambientes vigilados generan audio continuo y no estructurado. En sistemas tradicionales, la detección depende de una persona escuchando, de la revisión posterior de grabaciones o de capacidades cerradas del fabricante. ECHO busca transformar ese flujo acústico en observaciones y eventos tipificados, temporizados, puntuados y distribuibles en tiempo casi real.

## Qué sí es ECHO

- detección de actividad/eventos acústicos;
- clasificación de eventos acústicos observables;
- inferencia casi en tiempo real;
- procesamiento de una o múltiples fuentes;
- conversión de inferencias en eventos acústicos temporales;
- publicación de eventos mediante contratos estructurados;
- evaluación reproducible de precisión, recall, falsas alarmas, latencia y robustez.

## Qué no es ECHO

- un NVR;
- un sistema de reconocimiento facial;
- un sistema de interpretación de delitos;
- un sistema de reconocimiento de identidad o transcripción de conversaciones;
- una plataforma de visión artificial general;
- una blockchain;
- un sistema que garantice causalidad a partir del audio.

Ejemplos de frontera semántica:

```text
✅ GLASS_BREAK
❌ ROBBERY_CONFIRMED

✅ IMPACT_CRASH
❌ TRAFFIC_ACCIDENT_CONFIRMED

✅ YELL_SCREAM
❌ PERSON_IN_DANGER

✅ ALARM_SIREN
❌ BUILDING_EMERGENCY_CONFIRMED
```

## Principios de ingeniería

1. **Evidence first.** Hechos, hipótesis y decisiones se distinguen explícitamente.
2. **Multi-source by design.** La PoC puede usar una fuente; el dominio nunca se diseña como single-camera.
3. **Contracts over coupling.** Cada etapa recibe y emite contratos versionados.
4. **Benchmarks before promises.** Distancia, thresholds, accuracy y SLO se obtienen por medición.
5. **Privacy by default.** El audio continuo no se conserva salvo política explícita.
6. **No build before closure.** Build se habilita solo cuando los nodos críticos previos están cerrados.
7. **Downstream invalidation.** Cambiar evidencia/decisiones upstream invalida certificados dependientes.

## Madurez

- **MK0:** estado del arte + evidencia + incertidumbres + decisiones candidatas.
- **MK1:** especificación acotada y primera vertical de producto.
- **MK2:** producto robusto, multipunto, reproducible y operable dentro del alcance certificado.

## Flujo interno obligatorio en cada MK

```text
brainstorming -> design -> arch -> plan -> build -> test
```

`mining-site/` y `quarries/` existen dentro de cada MK como áreas de evidencia y extracción; no sustituyen ninguna de las seis fases.