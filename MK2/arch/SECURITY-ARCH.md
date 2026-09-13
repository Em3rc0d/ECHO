# Security Architecture — MK2

## Trust zones

- camera/NVR network;
- ECHO runtime;
- broker/message network;
- management/control plane;
- artifact/model registry.

## Controls target

- secret manager/env injection;
- least-privilege broker ACL;
- TLS cuando endpoints lo soporten;
- network segmentation;
- signed/checksummed release artifacts;
- dependency/SBOM scanning;
- non-root containers/processes cuando aplique;
- immutable config snapshots;
- audit logs de operaciones administrativas.

## Camera limitation

Cámaras legacy pueden ofrecer RTSP sin TLS. Mitigar con LAN/VLAN/segmentation; no afirmar confidencialidad del stream si el dispositivo no la soporta.