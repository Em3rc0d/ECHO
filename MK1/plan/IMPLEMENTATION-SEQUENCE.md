# Implementation Sequence — MK1

**No ejecutar hasta DoR.**

1. contracts/domain types;
2. file replay adapter;
3. preprocessing + windowing;
4. model adapter baseline;
5. benchmark harness;
6. Event Engine;
7. schemas serialization;
8. MQTT publisher + test subscriber;
9. telemetry;
10. RTSP adapter;
11. E2E replay;
12. camera E2E si external gate está resuelto;
13. packaging/demo.

Cada paso sólo inicia con tests definidos. No construir dashboard antes de que el evento estructurado sea estable.