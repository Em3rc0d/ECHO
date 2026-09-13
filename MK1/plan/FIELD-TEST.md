# MK1 Field Test Protocol

**Estado:** `EXTERNAL_GATE_OPEN` hasta disponer de cámara/ambiente/autorización.

## Distancia

```text
5 m
10 m
15 m
20 m
25 m
```

## Registrar por trial

```text
source_id
device/mic
codec
distance
background condition
event label
start/end ground truth
model/event timestamps
confidence
SNR estimate if available
latency
result hit/miss/false alarm
```

## Condiciones

Comparar al menos background bajo/medio/alto cuando sea práctico. Mantener eventos y posiciones reproducibles.

## Seguridad

No generar físicamente eventos peligrosos para probar ECHO. Usar sonidos seguros/autorizados, playback controlado cuando sea válido o capturas pasivas de eventos reales autorizados.

## Salida

Curvas por clase/dispositivo:

```text
recall vs distance
confidence vs distance
recall vs SNR
latency vs network/device
false alarms/hour
```

Solo después se congela una promesa de rango.