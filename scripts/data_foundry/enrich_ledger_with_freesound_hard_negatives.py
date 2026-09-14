#!/usr/bin/env python3
"""Preserve governed Freesound/FSD50K hard-negative roles in the canonical ledger.

The Freesound materializer already carries hard-negative decisions produced by
MK1-HARD-NEGATIVE-MAPPING-001. The canonical ledger builder intentionally
rebuilds source rows from durable materialization evidence, but older builds
failed to copy those roles. This enrichment restores only roles already present
in the release-safe materialization report. It never invents labels, never
creates a new source family, and positive ECHO labels always take precedence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from echo.data_foundry.contracts import TARGET_LABELS
from echo.data_foundry.ledger import validate_ledger
from echo.data_foundry.source_policy import load_dataset_certification
from scripts.data_foundry.build_canonical_asset_ledger import recompute_stage

ROOT = Path(__file__).resolve().parents[2]
MATERIALIZATION = ROOT / "MK1/mining-site/materialization"
LEDGER = MATERIALIZATION / "canonical-release-safe-asset-ledger.jsonl"
FREESOUND = MATERIALIZATION / "freesound-release-safe-materialization.json"
SOURCE_POLICY = ROOT / "configs/data_foundry/dataset_certification.v1.json"
SOURCE_ID = "echo-freesound-release-safe-v1"
MATERIALIZED_STATUS = "RELEASE_SAFE_REAL_PREVIEW_MATERIALIZED"
SEMANTIC_STATUS = "EXPLICIT_FSD50K_HARD_NEGATIVE_MAPPING_001"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"expected JSON object at {path}:{line_number}")
            rows.append(row)
    return rows


def valid_hard_negative_roles(
    materialized_row: Mapping[str, Any],
    ledger_row: Mapping[str, Any],
) -> list[str]:
    """Return source-governed hard-negative roles after positive precedence."""

    requested = {
        str(value)
        for value in materialized_row.get("hard_negative_for") or []
        if str(value) in TARGET_LABELS
    }
    positives = {
        str(value)
        for value in ledger_row.get("echo_labels") or []
        if str(value) in TARGET_LABELS
    }
    return sorted(requested - positives)


def main() -> int:
    for path in (LEDGER, FREESOUND, SOURCE_POLICY):
        if not path.is_file():
            raise SystemExit(f"required evidence missing: {path.relative_to(ROOT)}")

    source_policy = load_dataset_certification(SOURCE_POLICY)
    rows = read_jsonl(LEDGER)
    by_id = {str(row["ledger_asset_id"]): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("canonical ledger contains duplicate ledger_asset_id")

    payload = read_json(FREESOUND)
    materialized_hn_rows = 0
    attached_roles = 0
    shadowed_by_positive = 0
    missing_ledger_rows: list[str] = []

    for source_row in payload.get("assets") or []:
        if not isinstance(source_row, Mapping):
            continue
        if str(source_row.get("status") or "") != MATERIALIZED_STATUS:
            continue
        requested = {
            str(value)
            for value in source_row.get("hard_negative_for") or []
            if str(value) in TARGET_LABELS
        }
        if not requested:
            continue
        materialized_hn_rows += 1
        ledger_id = f"{SOURCE_ID}:{source_row['sound_id']}"
        ledger_row = by_id.get(ledger_id)
        if ledger_row is None:
            missing_ledger_rows.append(ledger_id)
            continue

        roles = valid_hard_negative_roles(source_row, ledger_row)
        shadowed_by_positive += len(requested - set(roles))
        if not roles:
            continue

        ledger_row["hard_negative_for"] = sorted(
            set(ledger_row.get("hard_negative_for") or []) | set(roles)
        )
        ledger_row["candidate_targets"] = sorted(
            set(ledger_row.get("candidate_targets") or []) | set(roles)
        )
        semantic = dict(ledger_row.get("semantic_status_by_target") or {})
        for target in roles:
            previous = semantic.get(target)
            if previous and previous != SEMANTIC_STATUS:
                raise SystemExit(
                    f"semantic status conflict while attaching Freesound hard negative: "
                    f"{ledger_id} {target}: {previous} != {SEMANTIC_STATUS}"
                )
            semantic[target] = SEMANTIC_STATUS
        ledger_row["semantic_status_by_target"] = dict(sorted(semantic.items()))
        ledger_row["label_provenance"] = sorted(
            set(ledger_row.get("label_provenance") or [])
            | {"FSD50K_v1.0_hard_negative_mapping_001"}
        )
        recompute_stage(ledger_row, source_policy)
        attached_roles += len(roles)

    if missing_ledger_rows:
        raise SystemExit(
            "materialized Freesound hard-negative evidence missing from canonical ledger: "
            + ", ".join(sorted(missing_ledger_rows)[:20])
        )

    final_rows = validate_ledger(by_id.values())
    with LEDGER.open("w", encoding="utf-8") as handle:
        for row in final_rows:
            handle.write(
                json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                + "\n"
            )

    print(
        json.dumps(
            {
                "status": "PASS",
                "materialized_hard_negative_rows": materialized_hn_rows,
                "attached_hard_negative_roles": attached_roles,
                "shadowed_by_positive": shadowed_by_positive,
                "source_dataset": SOURCE_ID,
                "underlying_source_family_boundary": "FREESOUND",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
