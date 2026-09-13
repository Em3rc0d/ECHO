# MK0 Build Gate

**Status:** `CLOSED_FOR_RESEARCH_ARTIFACTS`

## Purpose

Prevent MK0 from turning into unreviewed product implementation while still allowing reproducibility tooling.

## Preconditions

Problem boundary, research plan, architecture candidates and test/claim validation policy must exist. Any code/probe created in MK0 must answer a research question and be disposable or explicitly versioned.

## Permitted examples

- script to inspect metadata/license manifests;
- minimal RTSP/codec feasibility probe with no credentials committed;
- model-input sanity check;
- schema validation prototype;
- benchmark environment capture.

## Prohibited as certification evidence by itself

- one successful demo clip;
- hand-picked model prediction;
- manually observed camera connection without logs/config provenance;
- performance number without frozen data/config/hardware identity.

## Evidence required

Every research artifact names question, inputs, environment, command/config, output, interpretation and whether result is reproducible.

## Exit

MK0 build stage is complete when no additional tooling is required to validate the research claims feeding MK0 test/certification.

## Invalidation

A changed research question or input version invalidates the affected probe/result.