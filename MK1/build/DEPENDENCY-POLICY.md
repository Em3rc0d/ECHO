# Dependency Policy — MK1

Antes de agregar una dependencia:

- justificar función;
- fijar rango/version compatible;
- revisar licencia;
- evitar SDK pesado si una librería estándar basta;
- registrar transitive risk relevante;
- impedir que notebook-only dependencies entren al runtime.

Candidates esperados: Python, framework ML elegido, audio/numpy stack, paho-mqtt o equivalente, FFmpeg como runtime externo. La lista exacta se congela tras benchmark/model selection.