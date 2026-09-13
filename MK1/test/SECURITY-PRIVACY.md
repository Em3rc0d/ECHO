# Security & Privacy Tests — MK1

- logs no contienen RTSP/MQTT password;
- schema event no acepta URI con credenciales;
- invalid source config falla cerrado;
- publisher no permite topic arbitrario derivado de input no validado;
- artifacts/checkpoints se verifican por checksum;
- retention de audio está deshabilitada por defecto;
- cualquier modo de capture para dataset exige flag/config explícito y path dedicado;
- crash dump/logging no serializa PCM accidentalmente.

Estos tests no sustituyen pentest; son guardrails mínimos de PoC.