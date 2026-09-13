"""End-to-end corpus materialization for ECHO MK1 Data Foundry."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .admission import materialize_asset_record
from .contracts import AdmissionStatus, AssetRecord, MappingStatus, RawAssetCandidate, UseDecision
from .dedup import audit_duplicate_leakage
from .fingerprints import wav_envelope_fingerprint
from .hashing import canonical_json_sha256
from .intake import read_candidate_manifest
from .manifest import build_dataset_manifest, write_asset_manifest, write_json
from .mapping import LabelMapper
from .policies import load_policy
from .probe import probe_audio
from .reports import coverage_report, quarantine_report
from .reviews import ReviewDecision, load_review_decisions, review_for
from .source_policy import assert_sources_allowed
from .splits import SplitRatios, assign_group


_ADMITTED = {
    AdmissionStatus.ADMITTED_RELEASE_SAFE,
    AdmissionStatus.ADMITTED_RESEARCH_ONLY,
    AdmissionStatus.ADMITTED_FIELD_HOLDOUT,
}


def _path_for_candidate(candidate: RawAssetCandidate, audio_root: str | Path | None) -> Path:
    rel = Path(candidate.local_relpath or "")
    if rel.is_absolute() or audio_root is None:
        return rel
    return Path(audio_root) / rel


def _enrich_candidate_from_probe(candidate: RawAssetCandidate, path: Path) -> tuple[RawAssetCandidate, tuple[str, ...], dict[str, Any]]:
    probe = probe_audio(path)
    issues: list[str] = []
    extra: dict[str, Any] = {"audio_probe": probe.to_dict()}
    if not probe.ok:
        issues.append("AUDIO_PROBE_FAILED")
        return candidate, tuple(issues), extra

    enriched = replace(
        candidate,
        duration_seconds=(candidate.duration_seconds if candidate.duration_seconds is not None else probe.duration_seconds),
        sample_rate_hz=(candidate.sample_rate_hz if candidate.sample_rate_hz is not None else probe.sample_rate_hz),
        channels=(candidate.channels if candidate.channels is not None else probe.channels),
    )
    mismatches: list[str] = []
    if candidate.sample_rate_hz is not None and probe.sample_rate_hz is not None and candidate.sample_rate_hz != probe.sample_rate_hz:
        mismatches.append("sample_rate_hz")
    if candidate.channels is not None and probe.channels is not None and candidate.channels != probe.channels:
        mismatches.append("channels")
    if mismatches:
        extra["source_probe_metadata_mismatch"] = mismatches

    fingerprint = wav_envelope_fingerprint(path)
    if fingerprint:
        extra["near_duplicate_fingerprint"] = fingerprint
        extra["near_duplicate_fingerprint_method"] = "pcm_wav_envelope_v1"
    return enriched, tuple(issues), extra


def admit_candidates(
    candidates: Sequence[RawAssetCandidate],
    *,
    profile: str,
    mapper: LabelMapper,
    license_decisions: Mapping[str, Mapping[str, Any]],
    audio_root: str | Path | None = None,
    reviews: Mapping[str, ReviewDecision] | None = None,
) -> list[AssetRecord]:
    records: list[AssetRecord] = []
    for original_candidate in candidates:
        path = _path_for_candidate(original_candidate, audio_root)
        candidate, probe_issues, probe_extra = _enrich_candidate_from_probe(original_candidate, path)
        review = review_for(candidate.asset_id, reviews)
        record = materialize_asset_record(
            candidate,
            mapper=mapper,
            profile=profile,
            local_path=path,
            policy_decisions=license_decisions,
            manual_review_approved=bool(review and review.approved),
            manual_echo_labels=(review.echo_labels if review and review.approved else None),
            additional_quality_issues=probe_issues,
            additional_extra=probe_extra,
        )
        if review is not None:
            extra = dict(record.extra)
            extra["manual_review"] = {
                "approved": review.approved,
                "reviewer": review.reviewer,
                "reviewed_at_utc": review.reviewed_at_utc,
                "rationale": review.rationale,
                "evidence_ref": review.evidence_ref,
            }
            if not review.approved:
                record = replace(
                    record,
                    admission_status=AdmissionStatus.QUARANTINED,
                    reason_codes=tuple(sorted(set(record.reason_codes) | {"MANUAL_REVIEW_REJECTED"})),
                    extra=extra,
                )
            else:
                record = replace(record, extra=extra)
        records.append(record)
    return records


def write_record_manifest(path: str | Path, records: Iterable[AssetRecord]) -> str:
    return write_asset_manifest(path, records)


def read_record_manifest(path: str | Path) -> list[AssetRecord]:
    records: list[AssetRecord] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid asset JSONL at line {line_number}") from exc
            records.append(AssetRecord(
                asset_id=str(row["asset_id"]),
                source_dataset=str(row["source_dataset"]),
                source_release=str(row["source_release"]),
                source_asset_id=str(row["source_asset_id"]),
                sha256=str(row["sha256"]),
                license_id=str(row["license_id"]),
                use_decision=UseDecision(str(row["use_decision"])),
                original_labels=tuple(str(v) for v in row.get("original_labels", [])),
                echo_labels=tuple(str(v) for v in row.get("echo_labels", [])),
                mapping_status=MappingStatus(str(row["mapping_status"])),
                recording_group_id=str(row["recording_group_id"]),
                admission_status=AdmissionStatus(str(row["admission_status"])),
                reason_codes=tuple(str(v) for v in row.get("reason_codes", [])),
                origin_uri=row.get("origin_uri"), local_relpath=row.get("local_relpath"),
                byte_size=row.get("byte_size"), duration_seconds=row.get("duration_seconds"),
                sample_rate_hz=row.get("sample_rate_hz"), channels=row.get("channels"),
                label_provenance=row.get("label_provenance"), uploader_or_source_id=row.get("uploader_or_source_id"),
                site_id=row.get("site_id"), device_id=row.get("device_id"), original_split=row.get("original_split"),
                echo_split=row.get("echo_split"), field_holdout=bool(row.get("field_holdout", False)),
                parent_asset_ids=tuple(str(v) for v in row.get("parent_asset_ids", [])), extra=dict(row.get("extra") or {}),
                schema_version=str(row.get("schema_version") or "echo.asset-record.v1"),
            ))
    return records


def load_split_policy(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema_version") != "echo.split-policy.v1":
        raise ValueError("unsupported split policy schema")
    ratios = payload.get("fallback_group_hash_ratios", {})
    SplitRatios(float(ratios["train"]), float(ratios["validation"]), float(ratios["test"]))
    return payload


def assign_record_splits(records: Sequence[AssetRecord], *, policy: Mapping[str, Any]) -> list[AssetRecord]:
    ratios_raw = policy["fallback_group_hash_ratios"]
    ratios = SplitRatios(float(ratios_raw["train"]), float(ratios_raw["validation"]), float(ratios_raw["test"]))
    seed = str(policy["seed"])
    preserve = bool(policy.get("preserve_recognized_original_splits", True))
    original_map = {str(k).casefold(): str(v) for k, v in (policy.get("original_split_map") or {}).items()}
    group_splits: dict[str, str] = {}
    result: list[AssetRecord] = []

    for record in records:
        if record.admission_status not in _ADMITTED:
            result.append(replace(record, echo_split=None))
            continue
        if record.field_holdout or record.admission_status is AdmissionStatus.ADMITTED_FIELD_HOLDOUT:
            split = "field_holdout"
        else:
            split = None
            if preserve and record.original_split:
                split = original_map.get(str(record.original_split).casefold())
            if split is None:
                split = assign_group(record.recording_group_id, seed=seed, ratios=ratios)
        previous = group_splits.get(record.recording_group_id)
        if previous is not None and previous != split:
            raise ValueError(f"group {record.recording_group_id!r} receives conflicting splits: {previous} vs {split}")
        group_splits[record.recording_group_id] = split
        result.append(replace(record, echo_split=split))
    return result


def freeze_corpus(
    *,
    records: Sequence[AssetRecord],
    output_dir: str | Path,
    manifest_id: str,
    profile: str,
    taxonomy_version: str,
    source_registry: Mapping[str, Any],
    license_policy: Mapping[str, Any],
    label_mapping: Mapping[str, Any],
    split_policy: Mapping[str, Any],
    source_certification: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    assigned = assign_record_splits(records, policy=split_policy)
    admitted = [record for record in assigned if record.admission_status in _ADMITTED]

    if source_certification is not None:
        assert_sources_allowed(
            (record.source_dataset for record in admitted),
            profile=profile,
            policy=source_certification,
        )

    rows = [record.to_dict() for record in admitted]
    dedup = audit_duplicate_leakage(rows)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    asset_hash = write_asset_manifest(out / "asset-manifest.jsonl", admitted)
    split_manifest = {
        "schema_version": "echo.split-manifest.v1",
        "seed": split_policy["seed"],
        "assignments": {record.asset_id: record.echo_split for record in sorted(admitted, key=lambda r: r.asset_id)},
    }
    split_hash = write_json(out / "split-manifest.json", split_manifest)
    coverage = coverage_report(rows)
    quarantine = quarantine_report(record.to_dict() for record in assigned)
    dedup_hash = write_json(out / "dedup-report.json", dedup)
    coverage_hash = write_json(out / "coverage-report.json", coverage)
    quarantine_hash = write_json(out / "quarantine-report.json", quarantine)

    known_gaps = coverage["coverage_gaps"]
    source_certification_hash = (
        canonical_json_sha256(dict(source_certification)) if source_certification is not None else None
    )
    manifest = build_dataset_manifest(
        manifest_id=manifest_id,
        profile=profile,
        taxonomy_version=taxonomy_version,
        records=rows,
        source_registry_sha256=canonical_json_sha256(dict(source_registry)),
        license_policy_sha256=canonical_json_sha256(dict(license_policy)),
        label_mapping_sha256=canonical_json_sha256(dict(label_mapping)),
        split_policy_sha256=canonical_json_sha256(dict(split_policy)),
        source_certification_sha256=source_certification_hash,
        split_manifest_sha256=split_hash,
        known_gaps=known_gaps,
        reports={
            "coverage_report_sha256": coverage_hash,
            "dedup_report_sha256": dedup_hash,
            "quarantine_report_sha256": quarantine_hash,
        },
    )
    dataset_manifest_hash = write_json(out / "dataset-manifest.json", manifest)
    return {
        "status": "PASS" if not known_gaps else "PASS_WITH_COVERAGE_GAPS",
        "admitted_assets": len(admitted),
        "asset_manifest_sha256": asset_hash,
        "split_manifest_sha256": split_hash,
        "dataset_manifest_sha256": dataset_manifest_hash,
        "source_certification_sha256": source_certification_hash,
        "coverage_gaps": known_gaps,
        "output_dir": str(out),
    }


def admit_from_files(
    *,
    candidate_manifest: str | Path,
    mapping_path: str | Path,
    license_policy_path: str | Path,
    profile: str,
    output_path: str | Path,
    audio_root: str | Path | None = None,
    reviews_path: str | Path | None = None,
) -> str:
    candidates = read_candidate_manifest(candidate_manifest)
    mapper = LabelMapper.from_json(mapping_path)
    license_payload = load_policy(license_policy_path)
    reviews = load_review_decisions(reviews_path) if reviews_path else None
    records = admit_candidates(
        candidates,
        profile=profile,
        mapper=mapper,
        license_decisions=license_payload["decisions"],
        audio_root=audio_root,
        reviews=reviews,
    )
    return write_record_manifest(output_path, records)
