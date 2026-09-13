# Data Foundry — Acquisition and Release Verification

**Status:** `IMPLEMENTED / EXTERNAL_MEDIA_REQUIRED_FOR_CORPUS_EXECUTION`

## Purpose

Acquisition is an explicit Foundry gate. ECHO does not treat a folder named after a dataset as evidence that the correct upstream release was obtained. Every selected release has a registry entry containing canonical record URL, expected publisher bundle names and published checksums where available.

## Trust model

```text
publisher record
   -> declared release file
   -> publisher checksum verification
   -> local extraction
   -> per-audio SHA-256
   -> asset provenance/admission
```

Publisher MD5 values are used only to verify that an acquired bundle matches the publisher's published artifact. They are **not** ECHO asset identities. Each admitted local asset receives SHA-256.

## Machine-readable registry

`configs/data_foundry/acquisition_registry.v1.json` covers the selected FSD50K, SONYC-UST and SINGA:PURA Zenodo releases with file-level published MD5 checksums. ESC-50 and UrbanSound8K are represented as explicit research-only/manual/pinned acquisitions because their distribution mechanism differs.

The registry is validated structurally by `schemas/data_foundry/acquisition-registry.schema.json` and exercised by unit tests.

## CLI

```bash
echo-data-foundry acquisition-plan fsd50k-1.0 --stage metadata
echo-data-foundry acquisition-plan sonyc-ust-v2 --stage full
echo-data-foundry verify-acquisition fsd50k-1.0 /data/landing/fsd50k --stage metadata
```

A verification FAIL lists missing files and checksum mismatches. Downstream intake must not continue for that release until the declared acquisition stage passes.

## Multipart releases

FSD50K and SINGA:PURA use multipart archives for audio. All parts belonging to a logical archive must be present and publisher-verified before extraction. The Foundry never hashes an incomplete multipart member as if it were an audio asset.

## Disk/network planning

Full source audio is intentionally not downloaded by CI. Public releases are multi-gigabyte and may have license/terms that require an explicit operator decision. CI tests the deterministic verifier against fixtures; a real acquisition run occurs on controlled project storage.

## Evidence produced

A real acquisition run retains:

- source ID and release;
- canonical record URL;
- publisher file names/checksums;
- verification timestamp;
- local landing path identity;
- PASS/FAIL result;
- extraction procedure/version;
- any manual-download authorization notes.

## Stop-the-line

Missing bundle, checksum mismatch, release ambiguity, unrecorded manual substitution, or a source whose terms no longer match the registry causes `DF-G1 = FAIL` until resolved.

## Invalidation

If an upstream record publishes a new release or file/checksum changes, update the registry under a new reviewed commit and re-run acquisition verification. Historical manifests retain the old release identity.
