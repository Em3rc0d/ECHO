#!/usr/bin/env python3
"""Build the canonical MK1 release-safe evidence ledger from durable reports.

This script never promotes an entry to final corpus admission. It consolidates
source-specific evidence, records blockers explicitly, collapses wrapper-level
source identity into underlying acoustic source families, and emits a stable
ledger for the global dedup/group/split/coverage stages.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

from echo.data_foundry.contracts import TARGET_LABELS
from echo.data_foundry.ledger import (
    LEDGER_ENTRY_SCHEMA,
    file_sha256,
    load_underlying_source_policy,
    summarize_ledger,
    underlying_source_family,
    validate_ledger,
)
from echo.data_foundry.source_policy import load_dataset_certification, source_profile_state


ROOT = Path(__file__).resolve().parents[2]
MATERIALIZATION = ROOT / "MK1/mining-site/materialization"
SOURCE_POLICY_PATH = ROOT / "configs/data_foundry/dataset_certification.v1.json"
FAMILY_POLICY_PATH = ROOT / "configs/data_foundry/underlying_source_families.v1.json"
OUTPUT_LEDGER = MATERIALIZATION / "canonical-release-safe-asset-ledger.jsonl"
OUTPUT_SUMMARY = MATERIALIZATION / "canonical-release-safe-asset-ledger-summary.json"

INPUTS = {
    "sonyc_summary": MATERIALIZATION / "sonyc-v2.3-full-materialization-summary.json",
    "sonyc_targets": MATERIALIZATION / "sonyc-v2.3-target-candidates.jsonl",
    "sonyc_confusers": MATERIALIZATION / "sonyc-v2.3-confuser-candidates.jsonl",
    "freesound_release_safe": MATERIALIZATION / "freesound-release-safe-materialization.json",
    "public_gap": MATERIALIZATION / "public-gap-assets-report.json",
    "singapura_summary": MATERIALIZATION / "singapura-v1.0a-materialization-summary.json",
    "esc50_summary": MATERIALIZATION / "esc50-pinned-materialization-summary.json",
    "fsd50k_metadata": MATERIALIZATION / "fsd50k-metadata-inspection.json",
    "fsd50k_exact_candidates": MATERIALIZATION / "fsd50k-exact-freesound-candidates.json",
}

EXACT_FREESOUND_STATUSES = {"EXACT_FSD50K_GROUND_TRUTH", "EXACT_CURATED"}
EXACT_PUBLIC_SEMANTICS = {
    "GLASS_SHATTER": {"glass_shatter"},
    "SIREN": {"siren", "vehicle_siren"},
    "FIRE_ALARM": {"fire_alarm"},
    "VEHICLE_HORN": {"car_horn"},
    "TIRE_SQUEAL": {"tire_squeal"},
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    result = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"JSONL row must be an object: {path}:{line_number}")
            result.append(row)
    return result


def git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def release_for(source_policy: Mapping[str, Any], source_id: str) -> str:
    sources = source_policy.get("sources")
    row = sources.get(source_id) if isinstance(sources, Mapping) else None
    if not isinstance(row, Mapping):
        raise ValueError(f"source missing from dataset certification: {source_id}")
    release = str(row.get("release") or "").strip()
    if not release:
        raise ValueError(f"source certification release missing: {source_id}")
    return release


def classify_rights(license_id: str, source_state: str) -> tuple[str, list[str]]:
    value = str(license_id or "UNKNOWN").strip()
    upper = value.upper()
    blockers: list[str] = []
    if source_state != "ALLOW":
        blockers.append(f"SOURCE_PROFILE_{source_state}")
    if upper in {"CC0", "CC0-1.0", "PUBLIC-DOMAIN", "PUBLIC DOMAIN"}:
        rights = "ALLOW_RELEASE_SAFE"
    elif upper.startswith("CC-BY-") and "-NC" not in upper and "-SA" not in upper:
        rights = "ALLOW_RELEASE_SAFE"
    elif upper in {"CC-BY", "CC BY"}:
        rights = "ALLOW_RELEASE_SAFE"
    elif "NC" in upper or "SA" in upper:
        rights = "RESEARCH_ONLY"
        blockers.append("LICENSE_NOT_RELEASE_SAFE")
    else:
        rights = "REVIEW_REQUIRED"
        blockers.append("RIGHTS_UNCONFIRMED")
    if source_state != "ALLOW" and rights == "ALLOW_RELEASE_SAFE":
        rights = "REVIEW_REQUIRED"
    return rights, blockers


def recompute_stage(row: dict[str, Any], source_policy: Mapping[str, Any]) -> None:
    derived_codes = {
        "LICENSE_NOT_RELEASE_SAFE", "RIGHTS_UNCONFIRMED", "MISSING_MEDIA_SHA256",
        "MISSING_ASSET_LEVEL_BYTE_SIZE", "MISSING_ASSET_LEVEL_AUDIO_PROBE",
        "NON_POSITIVE_DURATION", "MISSING_SAMPLE_RATE", "MISSING_CHANNEL_COUNT",
        "MISSING_RECORDING_GROUP", "GROUPING_GLOBAL_AUDIT_REQUIRED",
        "NO_EXACT_SEMANTIC_ROLE", "FIELD_HOLDOUT_EXCLUDED_FROM_DEV",
    }
    blockers = {
        str(value)
        for value in row.get("blocking_reasons") or []
        if str(value) not in derived_codes and not str(value).startswith("SOURCE_PROFILE_")
    }
    source_id = str(row["source_dataset"])
    state = source_profile_state(source_policy, source_id=source_id, profile="release_safe")
    rights, rights_blockers = classify_rights(str(row.get("license_id") or "UNKNOWN"), state)
    row["rights_status"] = rights
    blockers.update(rights_blockers)

    if not row.get("media_sha256"):
        blockers.add("MISSING_MEDIA_SHA256")
    if int(row.get("byte_size") or 0) <= 0:
        blockers.add("MISSING_ASSET_LEVEL_BYTE_SIZE")
    probe = row.get("audio_probe")
    if not isinstance(probe, Mapping) or probe.get("ok") is not True:
        blockers.add("MISSING_ASSET_LEVEL_AUDIO_PROBE")
    else:
        if float(probe.get("duration_seconds") or 0.0) <= 0:
            blockers.add("NON_POSITIVE_DURATION")
        if int(probe.get("sample_rate_hz") or 0) <= 0:
            blockers.add("MISSING_SAMPLE_RATE")
        if int(probe.get("channels") or 0) <= 0:
            blockers.add("MISSING_CHANNEL_COUNT")
    if not str(row.get("recording_group_id") or "").strip():
        blockers.add("MISSING_RECORDING_GROUP")
    if str(row.get("grouping_status") or "").startswith("FALLBACK"):
        blockers.add("GROUPING_GLOBAL_AUDIT_REQUIRED")
    if not (row.get("echo_labels") or row.get("hard_negative_for")):
        blockers.add("NO_EXACT_SEMANTIC_ROLE")
    if row.get("field_holdout"):
        blockers.add("FIELD_HOLDOUT_EXCLUDED_FROM_DEV")

    fatal_prefixes = (
        "SOURCE_PROFILE_",
        "LICENSE_NOT_RELEASE_SAFE",
        "RIGHTS_UNCONFIRMED",
        "MISSING_MEDIA_SHA256",
        "MISSING_ASSET_LEVEL_BYTE_SIZE",
        "MISSING_ASSET_LEVEL_AUDIO_PROBE",
        "NON_POSITIVE_DURATION",
        "MISSING_SAMPLE_RATE",
        "MISSING_CHANNEL_COUNT",
        "MISSING_RECORDING_GROUP",
        "FIELD_HOLDOUT_EXCLUDED_FROM_DEV",
        "IDENTITY_CONFLICT",
    )
    sorted_blockers = sorted(blockers)
    row["blocking_reasons"] = sorted_blockers
    if any(code.startswith(fatal_prefixes) for code in sorted_blockers):
        row["stage_status"] = "BLOCKED"
    elif sorted_blockers:
        row["stage_status"] = "REVIEW_REQUIRED"
    else:
        row["stage_status"] = "READY_FOR_GLOBAL_DEDUP"


def make_entry(
    *,
    source_policy: Mapping[str, Any],
    family_policy: Mapping[str, Any],
    source_dataset: str,
    source_asset_id: str,
    media_sha256: str,
    byte_size: int | None,
    audio_probe: Mapping[str, Any] | None,
    license_id: str,
    candidate_targets: list[str],
    echo_labels: list[str],
    hard_negative_for: list[str],
    semantic_status_by_target: Mapping[str, str],
    label_provenance: list[str],
    recording_group_id: str,
    grouping_status: str,
    origin_uri: str | None,
    original_split: str | None,
    materialization_evidence: list[str],
    blocking_reasons: list[str] | None = None,
) -> dict[str, Any]:
    release = release_for(source_policy, source_dataset)
    family = underlying_source_family(family_policy, source_dataset)
    row = {
        "schema_version": LEDGER_ENTRY_SCHEMA,
        "ledger_asset_id": f"{source_dataset}:{source_asset_id}",
        "source_dataset": source_dataset,
        "source_release": release,
        "source_asset_id": source_asset_id,
        "underlying_source_family": family,
        "origin_uri": origin_uri,
        "media_sha256": media_sha256,
        "byte_size": byte_size,
        "audio_probe": dict(audio_probe) if isinstance(audio_probe, Mapping) else None,
        "license_id": license_id,
        "rights_status": "REVIEW_REQUIRED",
        "candidate_targets": sorted(set(candidate_targets) & set(TARGET_LABELS)),
        "echo_labels": sorted(set(echo_labels) & set(TARGET_LABELS)),
        "hard_negative_for": sorted(set(hard_negative_for) & set(TARGET_LABELS)),
        "semantic_status_by_target": dict(sorted((str(k), str(v)) for k, v in semantic_status_by_target.items() if str(k) in TARGET_LABELS)),
        "label_provenance": sorted({str(v) for v in label_provenance if str(v).strip()}),
        "recording_group_id": recording_group_id,
        "grouping_status": grouping_status,
        "original_split": original_split,
        "field_holdout": False,
        "canonical_fingerprint": None,
        "materialization_evidence": sorted(set(materialization_evidence)),
        "stage_status": "BLOCKED",
        "blocking_reasons": sorted(set(blocking_reasons or [])),
    }
    recompute_stage(row, source_policy)
    return row


def merge_entries(existing: dict[str, Any], incoming: dict[str, Any], source_policy: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    conflicts: list[str] = []
    immutable = (
        "source_dataset", "source_release", "source_asset_id",
        "underlying_source_family", "media_sha256", "license_id",
    )
    for key in immutable:
        if existing.get(key) != incoming.get(key):
            conflicts.append(f"IDENTITY_CONFLICT_{key.upper()}")
    existing_size = int(existing.get("byte_size") or 0)
    incoming_size = int(incoming.get("byte_size") or 0)
    if existing_size and incoming_size and existing_size != incoming_size:
        conflicts.append("IDENTITY_CONFLICT_BYTE_SIZE")
    merged["byte_size"] = existing.get("byte_size") or incoming.get("byte_size")
    if not isinstance(existing.get("audio_probe"), Mapping) and isinstance(incoming.get("audio_probe"), Mapping):
        merged["audio_probe"] = incoming["audio_probe"]
    elif isinstance(existing.get("audio_probe"), Mapping) and isinstance(incoming.get("audio_probe"), Mapping):
        if existing["audio_probe"] != incoming["audio_probe"]:
            conflicts.append("IDENTITY_CONFLICT_AUDIO_PROBE")

    for key in ("candidate_targets", "echo_labels", "hard_negative_for", "label_provenance", "materialization_evidence"):
        merged[key] = sorted(set(existing.get(key) or []) | set(incoming.get(key) or []))
    merged_semantic = dict(existing.get("semantic_status_by_target") or {})
    for target, status in (incoming.get("semantic_status_by_target") or {}).items():
        previous = merged_semantic.get(target)
        if previous and previous != status:
            merged_semantic[target] = f"CONFLICT:{previous}|{status}"
            conflicts.append(f"SEMANTIC_STATUS_CONFLICT_{target}")
        else:
            merged_semantic[target] = status
    merged["semantic_status_by_target"] = dict(sorted(merged_semantic.items()))

    if existing.get("recording_group_id") != incoming.get("recording_group_id"):
        ex_status = str(existing.get("grouping_status") or "")
        in_status = str(incoming.get("grouping_status") or "")
        if ex_status.startswith("FALLBACK") and not in_status.startswith("FALLBACK"):
            merged["recording_group_id"] = incoming.get("recording_group_id")
            merged["grouping_status"] = incoming.get("grouping_status")
        elif in_status.startswith("FALLBACK") and not ex_status.startswith("FALLBACK"):
            pass
        else:
            conflicts.append("IDENTITY_CONFLICT_RECORDING_GROUP")

    if existing.get("original_split") and incoming.get("original_split") and existing.get("original_split") != incoming.get("original_split"):
        conflicts.append("IDENTITY_CONFLICT_ORIGINAL_SPLIT")
    merged["original_split"] = existing.get("original_split") or incoming.get("original_split")
    merged["origin_uri"] = existing.get("origin_uri") or incoming.get("origin_uri")
    merged["blocking_reasons"] = sorted(set(existing.get("blocking_reasons") or []) | set(incoming.get("blocking_reasons") or []) | set(conflicts))
    recompute_stage(merged, source_policy)
    return merged


def add_entry(entries: dict[str, dict[str, Any]], row: dict[str, Any], source_policy: Mapping[str, Any]) -> None:
    key = str(row["ledger_asset_id"])
    if key in entries:
        entries[key] = merge_entries(entries[key], row, source_policy)
    else:
        entries[key] = row


def confuser_targets_for_asset(
    entries: Mapping[str, Mapping[str, Any]],
    *,
    source_dataset: str,
    source_asset_id: str,
    confuses: list[str],
) -> list[str]:
    """Return valid hard-negative roles after positive-label precedence.

    Polyphonic source clips may contain both an ECHO target and a known confuser.
    Such a clip remains a valid positive for the target, but cannot simultaneously
    be credited as a hard negative for that same target. We preserve the strict
    ledger validator and remove only the contradictory hard-negative role.
    """
    key = f"{source_dataset}:{source_asset_id}"
    existing_positive = set(entries.get(key, {}).get("echo_labels") or [])
    requested = {str(target) for target in confuses if str(target) in TARGET_LABELS}
    return sorted(requested - existing_positive)


def ingest_sonyc(entries: dict[str, dict[str, Any]], source_policy: Mapping[str, Any], family_policy: Mapping[str, Any]) -> dict[str, int]:
    stats = Counter()
    for row in read_jsonl(INPUTS["sonyc_targets"]):
        probe = row.get("audio_probe") if isinstance(row.get("audio_probe"), Mapping) else None
        entry = make_entry(
            source_policy=source_policy,
            family_policy=family_policy,
            source_dataset="sonyc-ust-v2",
            source_asset_id=str(row["source_asset_id"]),
            media_sha256=str(row["sha256"]),
            byte_size=int(row.get("byte_size") or 0) or None,
            audio_probe=probe,
            license_id=str(row.get("license_id") or "UNKNOWN"),
            candidate_targets=list(row.get("echo_labels") or []),
            echo_labels=list(row.get("echo_labels") or []),
            hard_negative_for=[],
            semantic_status_by_target={str(target): "EXACT_SOURCE_GROUND_TRUTH" for target in row.get("echo_labels") or []},
            label_provenance=[str(row.get("label_provenance") or "SONYC-UST v2.3")],
            recording_group_id=str(row.get("recording_group_candidate") or ""),
            grouping_status="SOURCE_TIME_SENSOR_GROUP",
            origin_uri=str(row.get("archive_member") or "") or None,
            original_split=str(row.get("split") or "") or None,
            materialization_evidence=[str(INPUTS["sonyc_targets"].relative_to(ROOT)), str(INPUTS["sonyc_summary"].relative_to(ROOT))],
        )
        add_entry(entries, entry, source_policy)
        stats["target_rows"] += 1

    for row in read_jsonl(INPUTS["sonyc_confusers"]):
        source_asset_id = str(row["source_asset_id"])
        requested_confuses = [str(value) for value in (row.get("confuses") or [])]
        confuses = confuser_targets_for_asset(
            entries,
            source_dataset="sonyc-ust-v2",
            source_asset_id=source_asset_id,
            confuses=requested_confuses,
        )
        stats["confuser_target_roles_requested"] += len(set(requested_confuses) & set(TARGET_LABELS))
        stats["confuser_target_roles_shadowed_by_positive"] += len(
            (set(requested_confuses) & set(TARGET_LABELS)) - set(confuses)
        )
        if not confuses:
            stats["confuser_rows_fully_shadowed_by_positive"] += 1
            continue
        entry = make_entry(
            source_policy=source_policy,
            family_policy=family_policy,
            source_dataset="sonyc-ust-v2",
            source_asset_id=source_asset_id,
            media_sha256=str(row["sha256"]),
            byte_size=None,
            audio_probe=None,
            license_id=str(row.get("license_id") or "UNKNOWN"),
            candidate_targets=confuses,
            echo_labels=[],
            hard_negative_for=confuses,
            semantic_status_by_target={str(target): "EXPLICIT_SOURCE_CONFUSER" for target in confuses},
            label_provenance=["SONYC-UST v2.3 source confuser annotations"],
            recording_group_id=str(row.get("recording_group_candidate") or ""),
            grouping_status="SOURCE_TIME_SENSOR_GROUP",
            origin_uri=str(row.get("archive_member") or "") or None,
            original_split=str(row.get("split") or "") or None,
            materialization_evidence=[str(INPUTS["sonyc_confusers"].relative_to(ROOT)), str(INPUTS["sonyc_summary"].relative_to(ROOT))],
        )
        add_entry(entries, entry, source_policy)
        stats["confuser_rows"] += 1
    return dict(stats)


def freesound_group(row: Mapping[str, Any]) -> tuple[str, str, list[str]]:
    families = sorted({str(value) for value in (row.get("recording_family_by_target") or {}).values() if str(value).strip()})
    if len(families) == 1:
        return f"freesound:{families[0]}", "CURATED_RECORDING_FAMILY", []
    if len(families) > 1:
        return f"freesound:sound:{row.get('sound_id')}", "FALLBACK_CONFLICTING_CURATED_FAMILIES", ["RECORDING_FAMILY_CONFLICT"]
    return f"freesound:sound:{row.get('sound_id')}", "FALLBACK_CLIP_ID", []


def ingest_freesound(entries: dict[str, dict[str, Any]], source_policy: Mapping[str, Any], family_policy: Mapping[str, Any]) -> dict[str, int]:
    payload = read_json(INPUTS["freesound_release_safe"])
    stats = Counter()
    for row in payload.get("assets") or []:
        status = str(row.get("status") or "")
        stats[f"status:{status}"] += 1
        if status != "RELEASE_SAFE_REAL_PREVIEW_MATERIALIZED":
            continue
        targets = [str(value) for value in (row.get("targets") or []) if str(value) in TARGET_LABELS]
        semantic = row.get("semantic_status_by_target") or {}
        exact = [target for target in targets if str(semantic.get(target) or "") in EXACT_FREESOUND_STATUSES]
        group, group_status, group_blockers = freesound_group(row)
        entry = make_entry(
            source_policy=source_policy,
            family_policy=family_policy,
            source_dataset="echo-freesound-release-safe-v1",
            source_asset_id=str(row["sound_id"]),
            media_sha256=str(row["media_sha256"]),
            byte_size=int(row.get("size_bytes") or 0) or None,
            audio_probe=(row.get("audio_probe") if isinstance(row.get("audio_probe"), Mapping) else None),
            license_id=str(row.get("license_id") or "UNKNOWN"),
            candidate_targets=targets,
            echo_labels=exact,
            hard_negative_for=[],
            semantic_status_by_target={target: str(semantic.get(target) or "UNKNOWN") for target in targets},
            label_provenance=[*(str(v) for v in (row.get("provenance") or [])), str(row.get("page_url") or "")],
            recording_group_id=group,
            grouping_status=group_status,
            origin_uri=str(row.get("resolved_page_url") or row.get("page_url") or "") or None,
            original_split=str(row.get("fsd50k_split") or "") or None,
            materialization_evidence=[str(INPUTS["freesound_release_safe"].relative_to(ROOT))],
            blocking_reasons=group_blockers,
        )
        add_entry(entries, entry, source_policy)
        stats["materialized_rows"] += 1
        stats["exact_semantic_rows"] += int(bool(exact))
    return dict(stats)


def ingest_public_gap(entries: dict[str, dict[str, Any]], source_policy: Mapping[str, Any], family_policy: Mapping[str, Any]) -> dict[str, int]:
    payload = read_json(INPUTS["public_gap"])
    stats = Counter()
    for row in payload.get("assets") or []:
        source_id = str(row.get("source_dataset") or "")
        if source_id not in {"echo-bigsoundbank-cc0-gap-v1", "echo-wikimedia-fire-alarm-v1"}:
            stats["unknown_source_rows"] += 1
            continue
        target = str(row.get("target") or "")
        semantic = str(row.get("semantic") or "")
        is_exact = target in TARGET_LABELS and semantic in EXACT_PUBLIC_SEMANTICS.get(target, set())
        blockers: list[str] = []
        semantic_status = "EXACT_CURATED_PAGE_SEMANTIC" if is_exact else "REVIEW_REQUIRED"
        if "augmentation_only" in semantic:
            semantic_status = "AUGMENTATION_ONLY"
            blockers.append("AUGMENTATION_ONLY_NO_REAL_SOURCE_CREDIT")
        group_raw = str(row.get("recording_family") or "").strip()
        group = f"{source_id}:{group_raw}" if group_raw else ""
        entry = make_entry(
            source_policy=source_policy,
            family_policy=family_policy,
            source_dataset=source_id,
            source_asset_id=str(row.get("asset_key") or ""),
            media_sha256=str(row.get("media_sha256") or ""),
            byte_size=int(row.get("size_bytes") or 0) or None,
            audio_probe=(row.get("audio_probe") if isinstance(row.get("audio_probe"), Mapping) else None),
            license_id=str(row.get("license_id") or "UNKNOWN"),
            candidate_targets=([target] if target in TARGET_LABELS else []),
            echo_labels=([target] if is_exact else []),
            hard_negative_for=[],
            semantic_status_by_target=({target: semantic_status} if target in TARGET_LABELS else {}),
            label_provenance=[str(row.get("page_url") or ""), "configs/data_foundry/gap_source_candidates.v1.json"],
            recording_group_id=group,
            grouping_status="CURATED_RECORDING_FAMILY" if group else "MISSING",
            origin_uri=str(row.get("resolved_page_url") or row.get("page_url") or "") or None,
            original_split=None,
            materialization_evidence=[str(INPUTS["public_gap"].relative_to(ROOT))],
            blocking_reasons=blockers,
        )
        add_entry(entries, entry, source_policy)
        stats[f"source:{source_id}"] += 1
        stats["exact_semantic_rows"] += int(is_exact)
    return dict(stats)


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in INPUTS.values() if not path.is_file()]
    if missing:
        raise SystemExit(f"required durable evidence missing: {missing}")

    source_policy = load_dataset_certification(SOURCE_POLICY_PATH)
    family_policy = load_underlying_source_policy(FAMILY_POLICY_PATH)
    entries: dict[str, dict[str, Any]] = {}
    source_input_stats = {
        "sonyc": ingest_sonyc(entries, source_policy, family_policy),
        "freesound": ingest_freesound(entries, source_policy, family_policy),
        "public_gap": ingest_public_gap(entries, source_policy, family_policy),
    }
    rows = validate_ledger(entries.values())
    summary = summarize_ledger(rows)
    summary.update({
        "status": "PASS_CONSOLIDATED_WITH_OPEN_GATES",
        "profile": "release_safe",
        "baseline_commit": git_head(),
        "global_invariant": "ECHO-FREE-TIER-001",
        "corpus_certificate": {"id": "CERT-MK1-DF-CORPUS-001", "status": "OPEN"},
        "input_digests": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": file_sha256(path)}
            for name, path in sorted(INPUTS.items())
        },
        "source_input_stats": source_input_stats,
        "profile_exclusions": {
            "singapura-v1.0a": "research_extended / CC-BY-SA-4.0; evidence retained but not counted in release_safe ledger",
            "esc50": "research_extended / CC-BY-NC; evidence retained but not counted in release_safe ledger",
            "fsd50k-1.0_wrapper": "metadata/label provenance only; current per-asset Freesound materialization is represented by echo-freesound-release-safe-v1 and shares underlying family FREESOUND"
        },
        "open_global_gates": [
            "canonical fingerprint coverage for all ledger assets",
            "cross-format near-duplicate global audit",
            "recording-family review for fallback Freesound groups",
            "asset-level technical evidence for standalone SONYC confuser rows",
            "dedicated second-source hard negatives where required",
            "group-aware split feasibility",
            "coverage/diversity gate",
            "freeze/bundle validation",
            "second clean freeze reproducibility"
        ],
        "certification_boundary": "Ledger consolidation is evidence plumbing, not corpus admission. READY_FOR_GLOBAL_DEDUP means the row may enter the global dedup/group audit; it does not mean ADMITTED_RELEASE_SAFE or CERTIFIED."
    })

    OUTPUT_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_LEDGER.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    OUTPUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": summary["status"],
        "entries": summary["entry_count"],
        "stage_status_counts": summary["stage_status_counts"],
        "positive_counts": summary["positive_counts"],
        "hard_negative_counts": summary["hard_negative_counts"],
        "fingerprints_missing": summary["canonical_fingerprint_missing_count"]
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
