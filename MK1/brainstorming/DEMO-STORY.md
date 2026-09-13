# Demo Story — MK1

## Escenario

Una fuente `CAM-01` emite audio continuo. ECHO decodifica y normaliza, crea ventanas solapadas, ejecuta el modelo y acumula evidencia temporal. Varias ventanas compatibles se consolidan en un único `CONFIRMED_EVENT`. El publisher lo envía por MQTT. Un subscriber independiente lo recibe y lo registra.

## Lo que debe observar el evaluador

1. La fuente está identificada y su salud es visible.
2. `RAW_INFERENCE` no se confunde con alarma.
3. Un evento acústico sostenido no produce spam de notificaciones.
4. Un sonido fuera de taxonomía puede ser rechazado/OTHER según policy.
5. Si se corta el stream, el source pasa a estado degradado y recupera conexión.
6. La evidencia de benchmark queda separada de la demo visual.

## Mensaje de producto

ECHO transforma audio ambiental en eventos acústicos estructurados mediante IA; cámaras/MQTT sólo conectan esa capacidad con el entorno.