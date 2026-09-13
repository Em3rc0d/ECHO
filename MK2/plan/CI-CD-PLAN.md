# CI/CD Plan — MK2

## Pull request gates

- formatting/lint/type checks;
- unit/contract tests;
- schema compatibility;
- dependency/license checks;
- no-secret scan;
- small deterministic model fixture tests.

## Main/release gates

- integration tests;
- benchmark regression against approved tolerances;
- artifact checksum/SBOM;
- container/package build;
- certification manifest generation;
- release candidate approval.

## Heavy tests

Load/soak/field benchmarks pueden ejecutarse en runner dedicado y adjuntar resultados por hash. Un CI green genérico no sustituye hardware certification.