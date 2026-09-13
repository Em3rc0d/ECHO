# Quarry — Thresholds

Los thresholds se calibran por clase, modelo y versión de datos.

Preguntas: ¿global o per-class? ¿enter/exit distintos? ¿qué objetivo se optimiza: F1, recall mínimo, false alarms/hour? ¿cómo cambia con domain shift?

Resultado esperado: tabla versionada de thresholds + calibration report + holdout verification. No ajustar después de mirar el test final.