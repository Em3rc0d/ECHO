"""Config-driven metadata intake for ECHO Data Foundry."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .adapters import (
    parse_esc50_metadata,
    parse_fsd50k_ground_truth,
    parse_singapura,
    parse_sonyc_annotations,
    parse_urbansound8k_metadata,
)
from .contracts import RawAssetCandidate
from .hashing import canonical_json_sha256


def candidate_to_dict(candidate: RawAssetCandidate) -> dict[str, Any]:
    row = asdict(candidate)
    row["schema_version"] = "echo.raw-asset-candidate.v1"
    row["asset_id"] = candidate.asset_id
    row["original_labels"] = list(candidate.original_labels)
    return row


def candidate_from_dict(row: Mapping[str, Any]) -> RawAssetCandidate:
    return RawAssetCandidate(
        source_dataset=str(row.get("source_dataset") or ""),
        source_release=str(row.get("source_release") or ""),
        source_asset_id=str(row.get("source_asset_id") or ""),
        origin_uri=row.get("origin_uri"),
        local_relpath=row.get("local_relpath"),
        license_id=str(row.get("license_id") or "UNKNOWN"),
        original_labels=tuple(str(v) for v in row.get("original_labels", []) or []),
        label_provenance=row.get("label_provenance"),
        recording_group_id=row.get("recording_group_id"),
        uploader_or_source_id=row.get("uploader_or_source_id"),
        site_id=row.get("site_id"),
        device_id=row.get("device_id"),
        original_split=row.get("original_split"),
        duration_seconds=(float(row["duration_seconds"]) if row.get("duration_seconds") is not None else None),
        sample_rate_hz=(int(row["sample_rate_hz"]) if row.get("sample_rate_hz") is not None else None),
        channels=(int(row["channels"]) if row.get("channels") is not None else None),
        field_holdout=bool(row.get("field_holdout", False)),
        extra=dict(row.get("extra") or {}),
    )


def write_candidate_manifest(path: str | Path, candidates: Iterable[RawAssetCandidate]) -> str:
    rows = [candidate_to_dict(candidate) for candidate in candidates]
    rows.sort(key=lambda row: str(row["asset_id"]))
    text = "".join(json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n" for row in rows)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_candidate_manifest(path: str | Path) -> list[RawAssetCandidate]:
    result: list[RawAssetCandidate] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid candidate JSONL at line {line_number}") from exc
            result.append(candidate_from_dict(payload))
    return result


def load_intake_spec(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema_version") != "echo.intake-spec.v1":
        raise ValueError("unsupported intake spec schema")
    if payload.get("adapter") not in {"fsd50k", "sonyc", "singapura", "esc50", "urbansound8k"}:
        raise ValueError("unsupported intake adapter")
    if not isinstance(payload.get("parameters"), Mapping):
        raise ValueError("intake parameters must be an object")
    return payload


def run_intake_spec(spec: Mapping[str, Any]) -> list[RawAssetCandidate]:
    adapter = str(spec["adapter"])
    p = dict(spec.get("parameters") or {})
    if adapter == "fsd50k":
        return parse_fsd50k_ground_truth(
            p["csv_path"], partition=str(p["partition"]),
            vocabulary_csv=p.get("vocabulary_csv"), clip_info_json=p.get("clip_info_json"),
            audio_root=p.get("audio_root"),
        )
    if adapter == "sonyc":
        return parse_sonyc_annotations(p["csv_path"], audio_root=p.get("audio_root"))
    if adapter == "singapura":
        return parse_singapura(p["metadata_csv"], p["labels_dir"], audio_root=p.get("audio_root"))
    if adapter == "esc50":
        return parse_esc50_metadata(p["csv_path"], audio_root=p.get("audio_root"))
    if adapter == "urbansound8k":
        return parse_urbansound8k_metadata(p["csv_path"], audio_root=p.get("audio_root"))
    raise ValueError(f"unsupported adapter: {adapter}")


def intake_spec_digest(spec: Mapping[str, Any]) -> str:
    return canonical_json_sha256(dict(spec))
