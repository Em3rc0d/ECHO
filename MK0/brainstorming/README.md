# MK0 / Brainstorming

## Pregunta central

¿Cómo convertir audio ambiental continuo, potencialmente ruidoso y proveniente de cámaras/micrófonos heterogéneos, en eventos acústicos estructurados y útiles en tiempo casi real?

## Escenarios

1. **Archivo/replay controlado** — valida el core ML sin red ni cámara.
2. **Micrófono local** — valida streaming continuo.
3. **Cámara IP con audio** — valida RTSP/codec/latencia real.
4. **N fuentes simultáneas** — valida scheduling, backpressure y aislamiento.
5. **Subscriber externo** — valida Pub/Sub y contrato de evento.

## Eventos candidatos, no congelados

```text
ALARM_SIREN
HORN
GLASS_BREAK
IMPACT_CRASH
YELL_SCREAM
REVERSING_BEEPER
TIRE_SCREECH
BACKGROUND_NO_TARGET
UNKNOWN
```

La lista es candidata. Cada clase debe superar cuatro preguntas:

```text
¿es acústicamente observable?
¿hay data suficiente/obtenible?
¿se puede distinguir de confusores reales?
¿tiene valor dentro de la promesa de ECHO?
```

## Anti-scope

No incorporar por presión de demo:

- reconocimiento facial;
- detección de personas/objetos por video;
- ASR/transcripción;
- identificación de hablante;
- inferencia de crimen/situación;
- mapas/dispatch;
- blockchain;
- cloud obligatorio.

## Hipótesis de producto

- H-001: transfer learning sobre embeddings generales superará una CNN desde cero con poca data propia.
- H-002: el Event Engine temporal reducirá falsas alarmas frente a publicar ventanas crudas.
- H-003: el mayor error en campo vendrá de domain shift y hard negatives, no de la inferencia matemática en sí.
- H-004: una arquitectura multi-source no exige N cámaras físicas para validar contratos.
- H-005: 10–15 m puede ser rango nominal razonable para ciertos eventos fuertes, pero debe medirse.

Todas permanecen hipótesis hasta test.