#!/usr/bin/env python3
"""Merge governed Freesound CC0 gap evidence into the canonical MK1 ledger.

The CC0 materializer is an acquisition path, not a new acoustic source. Every
row is normalized to the already-certified source id
`echo-freesound-release-safe-v1`, whose underlying source family is FREESOUND.
This prevents FSD50K/Freesound wrapper double-counting while allowing current
rights, probes, hashes, fingerprints and explicitly reviewed semantics to enrich
the same canonical asset identity.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Mapping

from echo.data_foundry.contracts import TARGET_LABELS
from echo.data_foundry.ledger import (
    file_sha256,
    load_underlying_source_policy,
    summarize_ledger,
    validate_ledger,
)
from echo.data_foundry.source_policy import load_dataset_certification
from scripts.data_foundry.build_canonical_asset_ledger import (
    add_entry,
    make_entry,
    recompute_stage,
)

ROOT = Path(__file__).resolve().parents[2]
MATERIALIZATION = ROOT / "MK1/mining-site/materialization"
LEDGER = MATERIALIZATION / "canonical-release-safe-asset-ledger.jsonl"
SUMMARY = MATERIALIZATION / "canonical-release-safe-asset-ledger-summary.json"
REPORT = MATERIALIZATION / "freesound-cc0-gap-assets-report.json"
SUPPLEMENTAL = ROOT / "configs/data_foundry/freesound_cc0_supplemental.v1.json"
SOURCE_POLICY_PATH = ROOT / "configs/data_foundry/dataset_certification.v1.json"
FAMILY_POLICY_PATH = ROOT / "configs/data_foundry/underlying_source_families.v1.json"

CANONICAL_SOURCE_ID = "echo-freesound-release-safe-v1"
MATERIALIZED_STATUS = "CC0_REAL_PREVIEW_MATERIALIZED_REVIEW_REQUIRED"
EXACT_SEMANTICS = {
    "FIRE_ALARM": {"fire_alarm"},
    "TIRE_SQUEAL": {"tire_squeal"},
}


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
                raise ValueError(f"expected object at {path}:{line_number}")
            rows.append(row)
    return rows


def supplemental_index(payload: Mapping[str, Any]) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    targets = payload.get("targets")
    if not isinstance(targets, Mapping):
        return result
    for target, rows in targets.items():
        if str(target) not in TARGET_LABELS or not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            sound_id = int(row["sound_id"])
            if sound_id in result:
                raise ValueError(f"supplemental sound_id repeated: {sound_id}")
            result[sound_id] = {
                "target": str(target),
                "semantic": str(row.get("semantic") or ""),
                "recording_family": str(row.get("recording_family") or ""),
            }
    return result


def semantic_decision(
    *,
    sound_id: int,
    report_target: str,
    report_semantic: str,
    supplemental: Mapping[int, Mapping[str, Any]],
) -> tuple[str, bool, str, list[str]]:
    """Return semantic, exact-positive flag, recording family and blockers."""

    curated = supplemental.get(sound_id)
    semantic = str(report_semantic or "")
    family = ""
    blockers: list[str] = []
    if curated:
        curated_target = str(curated.get("target") or "")
        if curated_target != report_target:
            blockers.append("CURATED_TARGET_CONFLICT")
            return semantic, False, family, blockers
        else:
            semantic = str(curated.get("semantic") or semantic)
            family = str(curated.get("recording_family") or "")

    if "augmentation_only" in semantic:
        blockers.append("AUGMENTATION_ONLY_NO_REAL_SOURCE_CREDIT")
        return semantic, False, family, blockers
    if "license_text_conflict" in semantic:
        blockers.append("RIGHTS_TEXT_CONFLICT_REVIEW_REQUIRED")
        return semantic, False, family, blockers

    exact = semantic in EXACT_SEMANTICS.get(report_target, set())
    return semantic, exact, family, blockers


def attach_fingerprint(
    *,
    current: dict[str, Any],
    incoming: Mapping[str, Any] | None,
    source_policy: Mapping[str, Any],
) -> None:
    if not isinstance(incoming, Mapping) or not incoming.get("vector_sha256"):
        return
    existing = current.get("canonical_fingerprint")
    if isinstance(existing, Mapping) and dict(existing) != dict(incoming):
        blockers = set(str(v) for v in current.get("blocking_reasons") or [])
        blockers.add("IDENTITY_CONFLICT_CANONICAL_FINGERPRINT")
        current["blocking_reasons"] = sorted(blockers)
        recompute_stage(current, source_policy)
        return
    current["canonical_fingerprint"] = dict(incoming)


def main() -> int:
    for path in (LEDGER, SUMMARY, REPORT, SUPPLEMENTAL, SOURCE_POLICY_PATH, FAMILY_POLICY_PATH):
        if not path.is_file():
            raise SystemExit(f"required evidence missing: {path.relative_to(ROOT)}")

    report = read_json(REPORT)
    fp_enrichment = report.get("canonical_fingerprint_enrichment")
    if not isinstance(fp_enrichment, Mapping) or fp_enrichment.get("status") != "PASS":
        raise SystemExit("Freesound CC0 report is not fingerprint-complete; refuse ledger augmentation")

    source_policy = load_dataset_certification(SOURCE_POLICY_PATH)
    family_policy = load_underlying_source_policy(FAMILY_POLICY_PATH)
    supplemental = supplemental_index(read_json(SUPPLEMENTAL))

    rows = read_jsonl(LEDGER)
    entries = {str(row["ledger_asset_id"]): row for row in rows}
    if len(entries) != len(rows):
        raise SystemExit("canonical ledger contains duplicate ledger_asset_id before CC0 augmentation")

    stats = Counter()
    for row in report.get("assets") or []:
        stats[f"status:{row.get('status')}"] += 1
        if row.get("status") != MATERIALIZED_STATUS:
            continue
        target = str(row.get("target") or "")
        if target not in {"FIRE_ALARM", "TIRE_SQUEAL"}:
            stats["ignored_non_gap_target"] += 1
            continue
        sound_id = int(row["sound_id"])
        semantic, exact, family, semantic_blockers = semantic_decision(
            sound_id=sound_id,
            report_target=target,
            report_semantic=str(row.get("semantic") or ""),
            supplemental=supplemental,
        )
        group = f"freesound:{family}" if family else f"freesound:sound:{sound_id}"
        group_status = "CURATED_RECORDING_FAMILY" if family else "FALLBACK_CLIP_ID"
        semantic_status = "EXACT_CURATED_CC0_SEMANTIC" if exact else "REVIEW_REQUIRED"
        ledger_id = f"{CANONICAL_SOURCE_ID}:{sound_id}"
        existed = ledger_id in entries

        entry = make_entry(
            source_policy=source_policy,
            family_policy=family_policy,
            source_dataset=CANONICAL_SOURCE_ID,
            source_asset_id=str(sound_id),
            media_sha256=str(row.get("media_sha256") or ""),
            byte_size=int(row.get("size_bytes") or 0) or None,
            audio_probe=(row.get("audio_probe") if isinstance(row.get("audio_probe"), Mapping) else None),
            license_id=str(row.get("license_id") or "UNKNOWN"),
            candidate_targets=[target],
            echo_labels=([target] if exact else []),
            hard_negative_for=[],
            semantic_status_by_target={target: semantic_status},
            label_provenance=[
                str(row.get("page_url") or ""),
                str(SUPPLEMENTAL.relative_to(ROOT)),
                str(REPORT.relative_to(ROOT)),
            ],
            recording_group_id=group,
            grouping_status=group_status,
            origin_uri=str(row.get("resolved_page_url") or row.get("page_url") or "") or None,
            original_split=None,
            materialization_evidence=[str(REPORT.relative_to(ROOT))],
            blocking_reasons=semantic_blockers,
        )
        add_entry(entries, entry, source_policy)
        attach_fingerprint(
            current=entries[ledger_id],
            incoming=(row.get("canonical_fingerprint") if isinstance(row.get("canonical_fingerprint"), Mapping) else None),
            source_policy=source_policy,
        )
        stats["materialized_rows"] += 1
        stats["exact_positive_rows"] += int(exact)
        stats["review_rows"] += int(not exact)
        stats["merged_existing_rows"] += int(existed)
        stats[f"target:{target}:materialized"] += 1
        stats[f"target:{target}:exact"] += int(exact)

    final_rows = validate_ledger(entries.values())
    previous = read_json(SUMMARY)
    summary = summarize_ledger(final_rows)
    summary.update({
        key: value
        for key, value in previous.items()
        if key not in summary and key not in {"cc0_gap_augmentation"}
    })
    summary["cc0_gap_augmentation"] = {
        "status": "PASS",
        "canonical_source_id": CANONICAL_SOURCE_ID,
        "underlying_source_family": "FREESOUND",
        "report_sha256": file_sha256(REPORT),
        "supplemental_sha256": file_sha256(SUPPLEMENTAL),
        "fingerprint_enrichment": dict(fp_enrichment),
        "stats": dict(sorted(stats.items())),
        "source_diversity_stop_line": "CC0 gap acquisition is another Freesound path and never creates a second source-family credit versus FSD50K/direct Freesound.",
        "semantic_stop_line": "Only explicit fire_alarm/tire_squeal supplemental decisions become positives; all broader/composite candidates remain review-only.",
    }
    input_digests = dict(summary.get("input_digests") or {})
    input_digests["freesound_cc0_gap"] = {
        "path": str(REPORT.relative_to(ROOT)),
        "sha256": file_sha256(REPORT),
    }
    input_digests["freesound_cc0_supplemental"] = {
        "path": str(SUPPLEMENTAL.relative_to(ROOT)),
        "sha256": file_sha256(SUPPLEMENTAL),
    }
    summary["input_digests"] = dict(sorted(input_digests.items()))

    with LEDGER.open("w", encoding="utf-8") as handle:
        for row in final_rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "PASS",
        "entries": summary["entry_count"],
        "positive_counts": summary["positive_counts"],
        "fingerprints_missing": summary["canonical_fingerprint_missing_count"],
        "cc0_stats": summary["cc0_gap_augmentation"]["stats"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
