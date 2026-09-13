"""Admission orchestration for one local Foundry asset."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import AdmissionStatus, AssetRecord, MappingStatus, RawAssetCandidate, UseDecision
from .hashing import sha256_file
from .mapping import LabelMapper, MappingDecision
from .policies import classify_license
from .quality import candidate_quality_issues


def decide_admission(
    *,
    profile: str,
    use_decision: UseDecision,
    mapping: MappingDecision,
    quality_issues: Sequence[str],
    field_holdout: bool,
    manual_review_approved: bool = False,
) -> tuple[AdmissionStatus, tuple[str, ...]]:
    reasons = set(quality_issues)

    if use_decision is UseDecision.DENY:
        reasons.add("LICENSE_DENIED")
        return AdmissionStatus.REJECTED, tuple(sorted(reasons))
    if use_decision in {UseDecision.QUARANTINE, UseDecision.REVIEW_REQUIRED}:
        reasons.add("LICENSE_REVIEW_OR_UNKNOWN")
    if profile == "release_safe" and use_decision in {
        UseDecision.RESEARCH_ONLY,
        UseDecision.ALLOW_RESEARCH_ONLY,
    }:
        reasons.add("LICENSE_RESEARCH_ONLY_FOR_REQUESTED_PROFILE")

    if mapping.review_required and not manual_review_approved:
        reasons.add("LABEL_REVIEW_REQUIRED")
    if mapping.status in {MappingStatus.BROADER, MappingStatus.AMBIGUOUS} and mapping.echo_labels and not manual_review_approved:
        reasons.add("LABEL_MAPPING_AMBIGUOUS")

    blocking = {
        "SOURCE_DATASET_MISSING",
        "SOURCE_RELEASE_MISSING",
        "SOURCE_ASSET_ID_MISSING",
        "GROUP_ID_MISSING",
        "DURATION_INVALID",
        "SAMPLE_RATE_INVALID",
        "CHANNEL_COUNT_INVALID",
        "FIELD_HOLDOUT_SOURCE_SPLIT_CONFLICT",
        "AUDIO_PROBE_FAILED",
        "LICENSE_REVIEW_OR_UNKNOWN",
        "LICENSE_RESEARCH_ONLY_FOR_REQUESTED_PROFILE",
        "LABEL_REVIEW_REQUIRED",
        "LABEL_MAPPING_AMBIGUOUS",
    }
    if reasons & blocking:
        return AdmissionStatus.QUARANTINED, tuple(sorted(reasons))

    if field_holdout:
        return AdmissionStatus.ADMITTED_FIELD_HOLDOUT, tuple(sorted(reasons))
    if profile == "research_extended":
        return AdmissionStatus.ADMITTED_RESEARCH_ONLY, tuple(sorted(reasons))
    return AdmissionStatus.ADMITTED_RELEASE_SAFE, tuple(sorted(reasons))


def materialize_asset_record(
    candidate: RawAssetCandidate,
    *,
    mapper: LabelMapper,
    profile: str,
    local_path: str | Path | None = None,
    policy_decisions: Mapping[str, Mapping[str, Any]] | None = None,
    manual_review_approved: bool = False,
    manual_echo_labels: Sequence[str] | None = None,
    additional_quality_issues: Sequence[str] = (),
    additional_extra: Mapping[str, Any] | None = None,
) -> AssetRecord:
    path = Path(local_path or candidate.local_relpath or "")
    if not str(path) or not path.exists() or not path.is_file():
        raise FileNotFoundError(f"asset file not found: {path}")

    mapping = mapper.map_labels(candidate.source_dataset, candidate.original_labels)
    if manual_echo_labels is not None:
        mapping = MappingDecision(
            echo_labels=tuple(sorted(set(manual_echo_labels))),
            status=MappingStatus.EXACT if manual_review_approved else mapping.status,
            review_required=not manual_review_approved,
            matched_source_labels=mapping.matched_source_labels,
            unmapped_source_labels=mapping.unmapped_source_labels,
            uses=mapping.uses,
            confuses=mapping.confuses,
        )

    use_decision = classify_license(candidate.license_id, profile=profile, decisions=policy_decisions)
    quality_issues = tuple(sorted(set(candidate_quality_issues(candidate)) | set(additional_quality_issues)))
    status, reasons = decide_admission(
        profile=profile,
        use_decision=use_decision,
        mapping=mapping,
        quality_issues=quality_issues,
        field_holdout=candidate.field_holdout,
        manual_review_approved=manual_review_approved,
    )

    return AssetRecord(
        asset_id=candidate.asset_id,
        source_dataset=candidate.source_dataset,
        source_release=candidate.source_release,
        source_asset_id=candidate.source_asset_id,
        origin_uri=candidate.origin_uri,
        local_relpath=candidate.local_relpath,
        sha256=sha256_file(path),
        byte_size=path.stat().st_size,
        duration_seconds=candidate.duration_seconds,
        sample_rate_hz=candidate.sample_rate_hz,
        channels=candidate.channels,
        license_id=candidate.license_id,
        use_decision=use_decision,
        original_labels=candidate.original_labels,
        echo_labels=mapping.echo_labels,
        mapping_status=mapping.status,
        label_provenance=candidate.label_provenance,
        recording_group_id=candidate.recording_group_id or "",
        uploader_or_source_id=candidate.uploader_or_source_id,
        site_id=candidate.site_id,
        device_id=candidate.device_id,
        original_split=candidate.original_split,
        echo_split="field_holdout" if candidate.field_holdout else None,
        field_holdout=candidate.field_holdout,
        admission_status=status,
        reason_codes=reasons,
        extra={
            **dict(candidate.extra),
            "mapping_uses": mapping.uses,
            "confuses": mapping.confuses,
            **dict(additional_extra or {}),
        },
    )
