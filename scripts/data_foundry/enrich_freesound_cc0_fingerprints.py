#!/usr/bin/env python3
"""Attach codec-independent fingerprints while Freesound CC0 bytes still exist.

The materialization workflow keeps audio only in runner scratch. This stage runs
before scratch disappears and persists the canonical fingerprint inside the
compact evidence report. Missing local bytes or fingerprint failures are
fail-closed for rows that otherwise claim successful materialization.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from echo.data_foundry.canonical_fingerprints import canonical_audio_fingerprint

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "MK1/mining-site/materialization/freesound-cc0-gap-assets-report.json"
MEDIA_ROOT = Path(os.environ.get("ECHO_FREESOUND_CC0_ROOT", ROOT / ".materialized-freesound-cc0"))
MATERIALIZED = "CC0_REAL_PREVIEW_MATERIALIZED_REVIEW_REQUIRED"


def main() -> int:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("Freesound CC0 report must be a JSON object")

    materialized = 0
    fingerprinted = 0
    failures: list[str] = []
    for row in payload.get("assets") or []:
        if row.get("status") != MATERIALIZED:
            continue
        materialized += 1
        relpath = str(row.get("local_relpath") or "").strip()
        if not relpath:
            failures.append(f"sound {row.get('sound_id')}: missing local_relpath")
            continue
        path = MEDIA_ROOT / relpath
        if not path.is_file():
            failures.append(f"sound {row.get('sound_id')}: materialized bytes missing at {path}")
            continue
        try:
            fingerprint = canonical_audio_fingerprint(path)
        except Exception as exc:  # fail-closed evidence stage
            failures.append(f"sound {row.get('sound_id')}: {type(exc).__name__}:{exc}")
            continue
        row["canonical_fingerprint"] = fingerprint
        fingerprinted += 1

    payload["canonical_fingerprint_enrichment"] = {
        "schema_version": "echo.freesound-cc0-fingerprint-enrichment.v1",
        "status": "PASS" if not failures and fingerprinted == materialized else "FAIL",
        "materialized_count": materialized,
        "fingerprinted_count": fingerprinted,
        "failure_count": len(failures),
        "failures": failures,
        "algorithm": "normalized-rms-envelope-v1",
        "canonical_decode": {"channels": 1, "sample_rate_hz": 16000, "sample_format": "s16le"},
    }
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(payload["canonical_fingerprint_enrichment"], sort_keys=True))
    if failures or fingerprinted != materialized:
        raise SystemExit("Freesound CC0 canonical fingerprint enrichment failed closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
