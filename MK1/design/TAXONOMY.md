# MK1 Acoustic Taxonomy v1

**Estado:** `FROZEN_FOR_MK1`  
**Decision:** D-022  
**Certificate:** CERT-MK0-010

## Principio

Cada target describe una **firma acústica observable**. Nunca implica por sí sola un delito, accidente, intención humana o causa social.

## Targets MK1

| Label ECHO | Semántica | Mapping/evidence inicial | Confusores prioritarios |
|---|---|---|---|
| `GLASS_SHATTER` | sonido de vidrio/material vítreo fragmentándose | AudioSet `Glass`/`Shatter`; assets deben validarse para glass semantics | metal/ceramic impact, dishes, brittle plastic |
| `SIREN` | patrón acústico de sirena de advertencia | AudioSet `Siren`; SONYC siren | alarms, tonal music, machinery |
| `FIRE_ALARM` | señal acústica de alarma contra incendio/emergencia | AudioSet `Fire alarm`; comparable Frigate `fire_alarm` | smoke alarm, buzzer, reversing beep, siren |
| `VEHICLE_HORN` | bocina/claxon de vehículo | AudioSet `Vehicle horn`; SONYC car-horn; ESC-50 car horn | air horn, alarm, tonal machinery |
| `TIRE_SQUEAL` | chirrido/fricción de neumático sobre superficie | AudioSet `Tire squeal` | metal squeal, brakes, machinery |

## Estados no-target

### `BACKGROUND_NO_TARGET`

No es una gran clase semántica. En entrenamiento multi-label corresponde normalmente a un vector target sin clases activas y debe cubrir contexto real diverso.

### Hard negatives

Obligatorios por target. Pool inicial:

```text
speech / crowd / music
normal traffic / engines
wind / rain
metal impacts / ceramic impacts
beeps / buzzers / reversing beepers
door slam
construction machinery
radio/TV playback
```

### `UNKNOWN`

Estado del decision layer cuando no existe evidencia suficiente para targets conocidos. No se fuerza necesariamente como neurona entrenada.

## Deferred labels

| Label | Motivo de defer |
|---|---|
| `VEHICLE_COLLISION` | un `impact` no demuestra colisión vehicular; requiere corpus específico y definición acústica verificable |
| `STRONG_IMPACT` | útil, pero demasiado amplio para la primera taxonomía; necesita hard-negative engineering |
| `YELL_SCREAM` | viable, pero amplía sensibilidad de privacidad y dominio humano; queda MK2/extended |
| `REVERSING_BEEPER` | SONYC ofrece evidencia, pero no es core para el primer vertical |
| `CAR_ALARM` | disponible en AudioSet/SONYC; diferido para evitar solape temprano con `FIRE_ALARM`/`SIREN` |

## Multi-label contract

Las clases no son mutuamente excluyentes. El head debe permitir múltiples probabilidades simultáneas (p. ej. sigmoids por target).

```json
{
  "SIREN": 0.91,
  "VEHICLE_HORN": 0.14,
  "GLASS_SHATTER": 0.02
}
```

Thresholds numéricos quedan fuera de este documento: se calibran solo con validation data y se certifican después.