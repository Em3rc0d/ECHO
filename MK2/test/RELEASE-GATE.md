# MK2 Release Gate

**Estado:** `NOT_READY`

## Quality

- [ ] field holdout meets frozen ML SLOs
- [ ] false alarms/source-hour within SLO
- [ ] per-class recall within critical thresholds
- [ ] calibration reviewed

## Realtime/capacity

- [ ] latency p95/p99 within SLO
- [ ] certified source capacity established per hardware profile
- [ ] bounded queues verified
- [ ] no unbounded memory growth in soak

## Resilience

- [ ] source reconnect automatic
- [ ] broker failure policy passes
- [ ] storage failure policy passes
- [ ] duplicate delivery is idempotent
- [ ] model rollback passes

## Security/privacy

- [ ] no secrets in repository/images/logs
- [ ] retention policy enforced
- [ ] evidence clips, if enabled, have TTL/ACL/encryption policy
- [ ] no ASR/speaker identification introduced

## Reproducibility/provenance

- [ ] code/model/config/schema hashes recorded
- [ ] dataset manifest recorded
- [ ] test report hashed
- [ ] release attestation verifies
- [ ] ancestor certificates valid

Todos los checks deben pasar o tener waiver explícito y justificado. Un waiver no puede ocultar un requisito MUST de seguridad/integridad.