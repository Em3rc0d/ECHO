# Model Selection Evidence — MK1

## Candidates mínimos

A. YAMNet embeddings + head.
B. PANNs/CNN14 feature/fine-tune.
C. compact custom CNN.

## Required record

Para cada candidate: source/checkpoint URL, license, checksum, preprocessing, params/artifact size, hardware, quality metrics, false alarms/hour, p95 latency, peak RAM/GPU, export/runtime issues.

## Decision rule

El ganador se marca `CERTIFIED` sólo después del benchmark común. Hasta entonces todos permanecen `CANDIDATE`.