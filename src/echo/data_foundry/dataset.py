"""Validated benchmark-facing view of a frozen Foundry bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .hashing import canonical_json_sha256


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON object required: {path}")
    return payload


def _read_asset_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid asset manifest JSONL line {line_number}") from exc
            if not isinstance(row, dict) or not row.get("asset_id"):
                raise ValueError(f"invalid asset manifest row at line {line_number}")
            rows.append(row)
    return rows


def validate_frozen_bundle(bundle_dir: str | Path) -> dict[str, Any]:
    root = Path(bundle_dir)
    dataset_path = root / "dataset-manifest.json"
    asset_path = root / "asset-manifest.jsonl"
    split_path = root / "split-manifest.json"
    for path in (dataset_path, asset_path, split_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    dataset = _read_json(dataset_path)
    split = _read_json(split_path)
    rows = _read_asset_rows(asset_path)

    asset_digest = hashlib.sha256(asset_path.read_bytes()).hexdigest()
    if asset_digest != dataset.get("asset_manifest_sha256"):
        raise ValueError("asset-manifest digest does not match dataset manifest")
    split_digest = canonical_json_sha256(split)
    if split_digest != dataset.get("split_manifest_sha256"):
        raise ValueError("split-manifest digest does not match dataset manifest")
    if int(dataset.get("asset_count", -1)) != len(rows):
        raise ValueError("asset_count does not match asset manifest")

    assignments = split.get("assignments")
    if not isinstance(assignments, dict):
        raise ValueError("split manifest assignments must be an object")
    by_asset = {str(row["asset_id"]): row for row in rows}
    if set(assignments) != set(by_asset):
        raise ValueError("split assignments and asset manifest identities differ")
    for asset_id, assigned_split in assignments.items():
        row_split = by_asset[asset_id].get("echo_split")
        if row_split != assigned_split:
            raise ValueError(f"split mismatch for {asset_id}: {row_split!r} vs {assigned_split!r}")

    reports = dataset.get("reports") or {}
    known_gaps = list(dataset.get("known_gaps") or [])
    profile = dataset.get("profile")
    coverage_gate_digest = reports.get("coverage_gate_sha256")
    coverage_policy_digest = reports.get("coverage_policy_sha256")

    # release_safe is a cryptographically bound certification claim.  A legacy
    # or hand-built bundle is not allowed to obtain that status merely because
    # its asset/split hashes are internally consistent.
    if profile == "release_safe":
        if not dataset.get("source_certification_sha256"):
            raise ValueError("release_safe bundle lacks source certification identity")
        if not coverage_policy_digest:
            raise ValueError("release_safe bundle lacks coverage policy identity")
        if not coverage_gate_digest:
            raise ValueError("release_safe bundle lacks coverage gate identity")

    if coverage_gate_digest:
        gate_path = root / "coverage-gate.json"
        if not gate_path.is_file():
            raise FileNotFoundError(gate_path)
        gate = _read_json(gate_path)
        actual_gate_digest = canonical_json_sha256(gate)
        if actual_gate_digest != coverage_gate_digest:
            raise ValueError("coverage-gate digest does not match dataset manifest")
        if gate.get("profile") != profile:
            raise ValueError("coverage-gate profile does not match dataset manifest")
        if gate.get("status") != "PASS" or known_gaps:
            raise ValueError("frozen bundle has unresolved corpus coverage/diversity gaps")

    return {
        "manifest_id": dataset.get("manifest_id"),
        "profile": profile,
        "taxonomy_version": dataset.get("taxonomy_version"),
        "asset_count": len(rows),
        "asset_manifest_sha256": asset_digest,
        "split_manifest_sha256": split_digest,
        "source_certification_sha256": dataset.get("source_certification_sha256"),
        "coverage_policy_sha256": coverage_policy_digest,
        "coverage_gate_sha256": coverage_gate_digest,
        "known_gaps": known_gaps,
    }


def load_benchmark_split(bundle_dir: str | Path, split_name: str) -> list[dict[str, Any]]:
    if split_name not in {"train", "validation", "test", "field_holdout"}:
        raise ValueError("unsupported benchmark split")
    validate_frozen_bundle(bundle_dir)
    rows = _read_asset_rows(Path(bundle_dir) / "asset-manifest.jsonl")
    selected = [row for row in rows if row.get("echo_split") == split_name]
    selected.sort(key=lambda row: str(row["asset_id"]))
    return selected
