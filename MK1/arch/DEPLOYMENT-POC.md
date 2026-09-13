# Deployment PoC — MK1

```text
┌──────────────────────── Host MK1 ────────────────────────┐
│ ECHO process                                             │
│  source adapters -> inference -> event engine -> publish │
│             |                         |                  │
│          metrics                  event metadata         │
│                                                         │
│ Mosquitto broker (separate process/container)            │
│ Test subscriber                                          │
└─────────────────────────────────────────────────────────┘
              ^
              |
        LAN / RTSP
              |
          Camera/NVR
```

## Decisiones

- Una sola máquina minimiza variables en PoC.
- Broker se mantiene separado para probar contrato de red.
- Cámara puede reemplazarse por replay sin cambiar core.
- Docker es opcional hasta evaluar restricciones de acceso a audio/GPU; no es requisito conceptual.