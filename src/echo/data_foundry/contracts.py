"""Typed contracts used after dataset-specific metadata has been parsed.

The module intentionally has no audio/ML/framework dependency.  Foundry code can
therefore validate identity, rights, mapping and split invariants before any
neural model or decoder is installed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


TARGET_LABELS = (
    "GLASS_SHATTER",
    "SIREN",
    "FIRE_ALARM",
    "VEHICLE_HORN",
    "TIRE_SQUEAL",
)


class MappingStatus(str, Enum):
    EXACT = "EXACT"
    NARROWER = "NARROWER"
    BROADER = "BROADER"
    AMBIGUOUS = "AMBIGUOUS"
    NEGATIVE = "NEGATIVE"
    UNUSABLE = "UNUSABLE"
    MIXED = "MIXED"


class UseDecision(str, Enum):
    ALLOW_RELEASE_SAFE = "ALLOW_RELEASE_SAFE"
    ALLOW_RESEARCH_ONLY = "ALLOW_RESEARCH_ONLY"
    RESEARCH_ONLY = "RESEARCH_ONLY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    QUARANTINE = "QUARANTINE"
    DENY = "DENY"


class AdmissionStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    STAGED = "STAGED"
    ADMITTED_RELEASE_SAFE = "ADMITTED_RELEASE_SAFE"
    ADMITTED_RESEARCH_ONLY = "ADMITTED_RESEARCH_ONLY"
    ADMITTED_FIELD_HOLDOUT = "ADMITTED_FIELD_HOLDOUT"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class RawAssetCandidate:
    """Dataset-neutral metadata before Foundry admission.

    Adapters should preserve upstream semantics in ``original_labels`` and
    ``extra`` rather than guessing ECHO labels.
    """

    source_dataset: str
    source_release: str
    source_asset_id: str
    origin_uri: str | None = None
    local_relpath: str | None = None
    license_id: str = "UNKNOWN"
    original_labels: tuple[str, ...] = ()
    label_provenance: str | None = None
    recording_group_id: str | None = None
    uploader_or_source_id: str | None = None
    site_id: str | None = None
    device_id: str | None = None
    original_split: str | None = None
    duration_seconds: float | None = None
    sample_rate_hz: int | None = None
    channels: int | None = None
    field_holdout: bool = False
    extra: Mapping[str, Any] = field(default_factory=dict)

    @property
    def asset_id(self) -> str:
        return f"{self.source_dataset}:{self.source_asset_id}"


@dataclass(frozen=True)
class AssetRecord:
    """Canonical admitted/quarantined Foundry record."""

    asset_id: str
    source_dataset: str
    source_release: str
    source_asset_id: str
    sha256: str
    license_id: str
    use_decision: UseDecision
    original_labels: tuple[str, ...]
    echo_labels: tuple[str, ...]
    mapping_status: MappingStatus
    recording_group_id: str
    admission_status: AdmissionStatus
    reason_codes: tuple[str, ...] = ()
    origin_uri: str | None = None
    local_relpath: str | None = None
    byte_size: int | None = None
    duration_seconds: float | None = None
    sample_rate_hz: int | None = None
    channels: int | None = None
    label_provenance: str | None = None
    uploader_or_source_id: str | None = None
    site_id: str | None = None
    device_id: str | None = None
    original_split: str | None = None
    echo_split: str | None = None
    field_holdout: bool = False
    parent_asset_ids: tuple[str, ...] = ()
    extra: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = "echo.asset-record.v1"

    def __post_init__(self) -> None:
        unknown_targets = set(self.echo_labels) - set(TARGET_LABELS)
        if unknown_targets:
            raise ValueError(f"Unknown ECHO labels: {sorted(unknown_targets)}")
        if not self.recording_group_id:
            raise ValueError("recording_group_id must not be empty")
        if len(self.sha256) != 64 or any(c not in "0123456789abcdef" for c in self.sha256.lower()):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        if self.echo_split not in {None, "train", "validation", "test", "field_holdout"}:
            raise ValueError(f"unsupported echo_split: {self.echo_split}")
        if self.field_holdout and self.echo_split not in {None, "field_holdout"}:
            raise ValueError("field_holdout asset cannot be assigned to a development split")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "asset_id": self.asset_id,
            "source_dataset": self.source_dataset,
            "source_release": self.source_release,
            "source_asset_id": self.source_asset_id,
            "origin_uri": self.origin_uri,
            "local_relpath": self.local_relpath,
            "sha256": self.sha256,
            "byte_size": self.byte_size,
            "duration_seconds": self.duration_seconds,
            "sample_rate_hz": self.sample_rate_hz,
            "channels": self.channels,
            "license_id": self.license_id,
            "use_decision": self.use_decision.value,
            "original_labels": list(self.original_labels),
            "echo_labels": list(self.echo_labels),
            "mapping_status": self.mapping_status.value,
            "label_provenance": self.label_provenance,
            "recording_group_id": self.recording_group_id,
            "uploader_or_source_id": self.uploader_or_source_id,
            "site_id": self.site_id,
            "device_id": self.device_id,
            "original_split": self.original_split,
            "echo_split": self.echo_split,
            "field_holdout": self.field_holdout,
            "admission_status": self.admission_status.value,
            "reason_codes": list(self.reason_codes),
            "parent_asset_ids": list(self.parent_asset_ids),
            "extra": dict(self.extra),
        }


def normalize_labels(labels: Sequence[str]) -> tuple[str, ...]:
    """Deduplicate while preserving deterministic lexical order."""

    return tuple(sorted({str(label).strip() for label in labels if str(label).strip()}))
