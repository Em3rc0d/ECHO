# Gates de ECHO

**Status:** `NORMATIVE`

## 1. Regla global

Ningún gate pasa por intención, antigüedad del documento o cantidad de código. Cada transición requiere inputs válidos, criterios explícitos y evidencia. Los gates siguen el pipeline interno obligatorio:

```text
brainstorming -> design -> arch -> plan -> build -> test
```

## 2. Estados

`OPEN`: falta evidencia o decisión.  
`CANDIDATE`: propuesta razonable aún no certificada.  
`CERTIFIED`: criterios satisfechos y upstream válido.  
`INVALIDATED`: un input material cambió.  
`EXTERNAL_GATE_OPEN`: depende de factor externo.  
`READY_NOT_STARTED`: gate de entrada satisfecho, ejecución aún no iniciada.

## 3. Regla de dependencia

```text
input evidence
   -> artifact
      -> gate certificate
         -> downstream artifact
```

Si un input cambia, no se borra el certificado histórico; su versión activa pasa a invalidada y los dependientes deben reevaluarse.

## 4. MK0 -> MK1

Requiere: promise/boundary, source catalog, related-project matrix, model/dataset landscape, PoC/target architecture, preliminary contracts, taxonomy, data policy, benchmark protocol, risk register, privacy/security policy, license registry y external gates.

Resultado actual: `CERT-MK0-013 = CERTIFIED`.

## 5. MK1 build gate

Requiere MK0 válido, DoR, test plan, source/audio/event contracts, taxonomía congelada, benchmark A/B/C, dataset manifest policy, event lifecycle, MQTT contract y secrets/observability strategy.

Resultado actual para replay: `CERT-MK1-READY-001 = CERTIFIED`, `MK1/build = READY_NOT_STARTED`.

## 6. MK1 test/certification gate

Debe producir evidencia real de:

```text
dataset manifest + split audit
benchmark results
model selection
threshold calibration
streaming replay
false alarms/source-hour
misses + per-class metrics
latency/resources
Event Engine behavior
Pub/Sub idempotency
failure/reconnect behavior
security/privacy checks
error analysis
```

La rama de cámara real añade codec, RTSP jitter/reconnect, distance/SNR y field latency.

## 7. MK1 -> MK2

No basta con completar features. Deben estar congelados el modelo o reasoned deferral, operating envelope inicial, known failure modes, benchmark artifacts, schemas y migration path. MK2 recibe evidencia, no supuestos.

## 8. MK2 release gate

Requiere capacidad N certificada, load/soak, backpressure, resilience/chaos, observability, rollback, security, model governance, drift/regression, release reproducibility, SBOM/licensing y cierre de external gates necesarios para el deployment declarado.

## 9. Regla anti-auto-certification

Un documento que describe cómo debería funcionar una prueba no certifica que la prueba pasó. Protocolo y resultado son artefactos diferentes.

## 10. Invalidation examples

- cambiar taxonomy invalida mappings, heads, thresholds y model comparison;
- cambiar preprocessing invalida benchmark comparable;
- cambiar event schema puede invalidar consumers y replay evidence;
- cambiar broker semantics invalida delivery tests;
- cambiar camera hardware invalida field compatibility/capacity claims.