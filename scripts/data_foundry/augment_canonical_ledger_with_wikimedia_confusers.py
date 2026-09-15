#!/usr/bin/env python3
"""Attach governed Wikimedia hard-negative roles to materialized public assets.

This stage does not create labels, source families, or media evidence. It promotes
only target-free rows whose versioned config role exactly matches the durable
public materialization report, after release-safe rights and technical evidence
have already been captured. Final dedup/group/split/coverage gates remain
mandatory.
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
MAT = ROOT / "MK1/mining-site/materialization"
LEDGER = MAT / "canonical-release-safe-asset-ledger.jsonl"
REPORT = MAT / "public-gap-assets-report.json"
CONFIG = ROOT / "configs/data_foundry/wikimedia_confusers.v1.json"
SOURCE_POLICY = ROOT / "configs/data_foundry/dataset_certification.v1.json"
SEMANTIC_STATUS = "EXPLICIT_CURATED_WIKIMEDIA_HARD_NEGATIVE"
ALLOWED_LICENSES = {"CC0", "CC0-1.0", "PUBLIC-DOMAIN", "PUBLIC DOMAIN"}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"expected object at {path}:{line_number}")
            rows.append(row)
    return rows


def governed_roles(
    config_row: Mapping[str, Any],
    report_row: Mapping[str, Any],
    ledger_row: Mapping[str, Any],
) -> list[str]:
    """Return roles only when config/report agree and no positive overlap exists."""

    configured = {
        str(value)
        for value in (config_row.get("hard_negative_for") or [])
        if str(value) in TARGET_LABELS
    }
    reported = {
        str(value)
        for value in (report_row.get("hard_negative_for") or [])
        if str(value) in TARGET_LABELS
    }
    if not configured:
        raise ValueError("Wikimedia confuser config has no governed target roles")
    if reported != configured:
        raise ValueError(
            f"Wikimedia confuser role mismatch: config={sorted(configured)} report={sorted(reported)}"
        )

    positives = {
        str(value)
        for value in (ledger_row.get("echo_labels") or [])
        if str(value) in TARGET_LABELS
    }
    conflict = configured & positives
    if conflict:
        raise ValueError(
            f"Wikimedia confuser cannot be hard negative for a positive target: {sorted(conflict)}"
        )
    return sorted(configured)


def main() -> int:
    for path in (LEDGER, REPORT, CONFIG, SOURCE_POLICY):
        if not path.is_file():
            raise SystemExit(f"required evidence missing: {path.relative_to(ROOT)}")

    config = read_json(CONFIG)
    if config.get("schema_version") != "echo.wikimedia-confusers.v1":
        raise SystemExit("unsupported Wikimedia confuser config schema")
    source_id = str(config.get("source_dataset") or "")
    if source_id != "echo-wikimedia-fire-alarm-v1":
        raise SystemExit(f"unexpected Wikimedia source_dataset: {source_id}")

    report = read_json(REPORT)
    report_by_key = {
        (str(row.get("source_dataset") or ""), str(row.get("asset_key") or "")): row
        for row in (report.get("assets") or [])
        if isinstance(row, Mapping)
    }

    rows = read_jsonl(LEDGER)
    by_id = {str(row["ledger_asset_id"]): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("canonical ledger contains duplicate ledger_asset_id")

    source_policy = load_dataset_certification(SOURCE_POLICY)
    attached_rows = 0
    attached_roles = 0

    for config_row in config.get("assets") or []:
        if not isinstance(config_row, Mapping):
            raise SystemExit("Wikimedia confuser config row must be an object")
        asset_key = str(config_row.get("asset_key") or "")
        if not asset_key:
            raise SystemExit("Wikimedia confuser config row missing asset_key")

        report_row = report_by_key.get((source_id, asset_key))
        if report_row is None:
            raise SystemExit(f"materialized Wikimedia confuser missing from public report: {asset_key}")
        if str(report_row.get("license_id") or "").upper() not in ALLOWED_LICENSES:
            raise SystemExit(f"Wikimedia confuser license is not release-safe: {asset_key}")
        if not str(report_row.get("media_sha256") or ""):
            raise SystemExit(f"Wikimedia confuser missing media SHA-256: {asset_key}")
        probe = report_row.get("audio_probe")
        if not isinstance(probe, Mapping) or probe.get("ok") is not True:
            raise SystemExit(f"Wikimedia confuser missing valid audio probe: {asset_key}")
        fingerprint = report_row.get("canonical_fingerprint")
        if not isinstance(fingerprint, Mapping) or not fingerprint.get("vector_sha256"):
            raise SystemExit(f"Wikimedia confuser missing canonical fingerprint: {asset_key}")

        ledger_id = f"{source_id}:{asset_key}"
        ledger_row = by_id.get(ledger_id)
        if ledger_row is None:
            raise SystemExit(f"Wikimedia confuser missing from canonical ledger: {ledger_id}")
        if str(ledger_row.get("media_sha256") or "") != str(report_row.get("media_sha256") or ""):
            raise SystemExit(f"Wikimedia confuser media identity mismatch: {ledger_id}")

        roles = governed_roles(config_row, report_row, ledger_row)
        ledger_row["hard_negative_for"] = sorted(
            set(ledger_row.get("hard_negative_for") or []) | set(roles)
        )
        ledger_row["candidate_targets"] = sorted(
            set(ledger_row.get("candidate_targets") or []) | set(roles)
        )
        semantic = dict(ledger_row.get("semantic_status_by_target") or {})
        for target in roles:
            previous = semantic.get(target)
            if previous not in {None, "REVIEW_REQUIRED", SEMANTIC_STATUS}:
                raise SystemExit(
                    f"Wikimedia confuser semantic conflict: {ledger_id} {target}: {previous}"
                )
            semantic[target] = SEMANTIC_STATUS
        ledger_row["semantic_status_by_target"] = dict(sorted(semantic.items()))
        ledger_row["label_provenance"] = sorted(
            set(ledger_row.get("label_provenance") or [])
            | {
                str(config_row.get("url") or ""),
                "configs/data_foundry/wikimedia_confusers.v1.json",
            }
        )
        recompute_stage(ledger_row, source_policy)
        if ledger_row.get("stage_status") != "READY_FOR_GLOBAL_DEDUP":
            raise SystemExit(
                f"governed Wikimedia confuser did not reach READY_FOR_GLOBAL_DEDUP: "
                f"{ledger_id} blockers={ledger_row.get('blocking_reasons')}"
            )
        attached_rows += 1
        attached_roles += len(roles)

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
                "source_dataset": source_id,
                "underlying_source_family_boundary": "WIKIMEDIA_COMMONS",
                "attached_rows": attached_rows,
                "attached_hard_negative_roles": attached_roles,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
