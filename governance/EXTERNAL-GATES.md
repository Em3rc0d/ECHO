# External Gates

Estas condiciones no pueden cerrarse desde documentación o Internet; requieren profesora, hardware, red o autorización.

| Gate | Estado | Qué necesitamos |
|---|---|---|
| XG-01 Camera model | EXTERNAL_GATE_OPEN | marca/modelo exacto |
| XG-02 Audio capability | EXTERNAL_GATE_OPEN | confirmar micrófono/audio stream |
| XG-03 RTSP | EXTERNAL_GATE_OPEN | URL/perfil o confirmación de soporte |
| XG-04 ONVIF | EXTERNAL_GATE_OPEN | soporte/profile opcional |
| XG-05 Audio codec | EXTERNAL_GATE_OPEN | AAC/G.711/otro + sample rate |
| XG-06 Credentials | EXTERNAL_GATE_OPEN | acceso autorizado; nunca commit |
| XG-07 Network reachability | EXTERNAL_GATE_OPEN | misma red/VPN/NAT/firewall |
| XG-08 Stream concurrency limits | EXTERNAL_GATE_OPEN | conexiones toleradas por cámara/NVR |
| XG-09 Recording permission | EXTERNAL_GATE_OPEN | permiso para capturas de evaluación |
| XG-10 Field test location | EXTERNAL_GATE_OPEN | ambiente y distancias disponibles |
| XG-11 Event playback policy | EXTERNAL_GATE_OPEN | qué eventos pueden reproducirse de forma segura y autorizada |
| XG-12 External microphone fallback | EXTERNAL_GATE_OPEN | disponibilidad si cámara no sirve |

## Checklist para la profesora

Preguntar únicamente datos técnicos necesarios: modelo de cámara, si tiene micrófono, acceso RTSP/ONVIF, codec de audio, forma de acceso de red, autorización para usar el stream en pruebas y posibilidad de ejecutar ensayos controlados. No se requieren credenciales dentro del repositorio.