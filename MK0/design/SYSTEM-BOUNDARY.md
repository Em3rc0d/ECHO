# System Boundary — MK0

## Entrada

Una `AudioSource` representa una fuente lógica: cámara IP, NVR, archivo de replay o micrófono. La fuente debe estar identificada por `source_id`; credenciales y URI son configuración externa.

## Pipeline lógico candidato

```text
AudioSource
  -> Ingestion
  -> Decode / Resample / Channel normalization
  -> Windowing
  -> Model inference
  -> RAW_INFERENCE
  -> Temporal Event Engine
  -> CANDIDATE_EVENT
  -> CONFIRMED_EVENT
  -> Pub/Sub / persistence / API
  -> ALERT (si una política decide alertar)
```

## Separación esencial

- **RAW_INFERENCE:** salida de una ventana del modelo; nunca es una alarma.
- **CANDIDATE_EVENT:** evidencia temporal acumulada todavía reversible.
- **CONFIRMED_EVENT:** ocurrencia acústica consolidada según reglas versionadas.
- **ALERT:** proyección opcional de un evento confirmado hacia un consumidor.

## Invariantes de diseño

1. `source_id` acompaña toda observación.
2. timestamps distinguen tiempo de captura, inferencia y publicación.
3. modelo y Event Engine tienen versiones independientes.
4. los contratos no contienen secretos.
5. una caída de un source no debe bloquear los demás en arquitectura target.
6. la PoC de un source debe usar las mismas abstracciones que N sources.